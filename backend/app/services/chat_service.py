"""
对话服务
"""
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from loguru import logger
from backend.app.models.conversation import Conversation, Message, ChatLog
from backend.app.models.model import Model
from backend.app.core.langgraph_workflow import LangGraphWorkflow
from backend.app.schemas.chat import ChatRequest, ChatResponse, Citation

rag_pipeline = None

def get_rag_pipeline(api_key=None, base_url=None):
    """获取 LangGraphWorkflow 实例，支持惰性初始化"""
    global rag_pipeline
    if rag_pipeline is None:
        rag_pipeline = LangGraphWorkflow(api_key=api_key, base_url=base_url)
    return rag_pipeline


def initialize_rag_pipeline(model_id, kb_id=None, embedding_model_id=None, rerank_model_id=None, db=None):
    """初始化RAG pipeline"""
    global rag_pipeline
    
    # 从数据库获取模型详情
    result = db.execute(
        select(Model).where(Model.id == model_id, Model.is_active == True)
    )
    model = result.scalar_one_or_none()
    if not model:
        raise ValueError("模型不存在或未激活")

    # 初始化模型变量
    embedding_model = None
    rerank_model = None

    # 如果提供了embedding_model_id，从数据库获取embedding模型详情
    if embedding_model_id:
        embedding_result = db.execute(
            select(Model).where(Model.id == embedding_model_id, Model.is_active == True)
        )
        embedding_model = embedding_result.scalar_one_or_none()

    # 如果提供了rerank_model_id，从数据库获取rerank模型详情
    if rerank_model_id:
        rerank_result = db.execute(
            select(Model).where(Model.id == rerank_model_id, Model.is_active == True)
        )
        rerank_model = rerank_result.scalar_one_or_none()

    # 初始化LangGraph工作流，传递模型详情
    # 不传递provider参数，让Rerank类自己从模型名称中推断
    rag_pipeline = LangGraphWorkflow(
        api_key=model.api_key,
        base_url=model.base_url,
        embedding_model=embedding_model,
        rerank_model=rerank_model,
        db=db
    )
    
    return model

async def _get_conversation_history(
    db: AsyncSession,
    conversation_id: str,
    limit: int = 10,
) -> List[dict]:
    """获取对话历史"""
    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .limit(limit)
    )
    messages = result.scalars().all()
    messages.reverse()

    return [
        {"role": m.role, "content": m.content}
        for m in messages
    ]


# 导入模型
from backend.app.models.knowledge_base import KnowledgeBase
from backend.app.models.domain import Domain

async def _get_domain_from_kb(
    db: AsyncSession,
    kb_ids: List[str]
) -> Optional[str]:
    """从知识库获取领域信息"""
    if not kb_ids:
        return None
    
    try:
        # 获取第一个知识库的详情
        kb_result = await db.execute(
            select(KnowledgeBase).options(
                selectinload(KnowledgeBase.domains)
            ).where(KnowledgeBase.id == kb_ids[0])
        )
        kb = kb_result.scalar_one_or_none()
        
        if kb and kb.domains:
            # 使用第一个领域作为主要领域
            domain = kb.domains[0].name
            logger.info(f"知识库 {kb.name} 关联领域: {domain}")
            return domain
    except Exception as e:
        logger.error(f"获取领域信息失败: {e}")
    
    return None


async def chat(
        db: AsyncSession,
        pm_db: AsyncSession,
        request: ChatRequest,
        user_id: str,
) -> ChatResponse:
    # 获取用户信息
    from backend.app.models.user import User
    user_result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = user_result.scalar_one_or_none()
    """处理用户聊天请求"""
    # 获取或创建对话
    if request.conversation_id:
        result = await db.execute(
            select(Conversation).where(Conversation.id == request.conversation_id)
        )
        conversation = result.scalar_one_or_none()
        if not conversation:
            # 为新对话生成新的UUID，不使用前端的临时ID
            conversation = Conversation(
                user_id=user_id,
                kb_id=request.kb_ids[0] if request.kb_ids else None,
                title=request.query[:50],
            )
            db.add(conversation)
            await db.flush()
    else:
        conversation = Conversation(
            user_id=user_id,
            kb_id=request.kb_ids[0] if request.kb_ids else None,
            title=request.query[:50],
        )
        db.add(conversation)
        await db.flush()

    # 保存用户消息
    user_message = Message(
        conversation_id=conversation.id,
        role="user",
        content=request.query,
    )
    db.add(user_message)

    # 获取对话历史，使用context_round参数控制历史长度
    limit = request.context_round * 2 if request.context_round else 10  # 每个轮次包含用户和助手的消息，所以乘以2
    history = await _get_conversation_history(db, conversation.id, limit)

    # 如果提供了 model_id，从数据库获取模型详情
    embedding_model = None
    rerank_model = None

    result = await db.execute(
        select(Model).where(Model.type == "chat", Model.is_active == True).limit(1)
    )
    chat_model = result.scalar_one_or_none()
    api_key = chat_model.api_key
    base_url = chat_model.base_url
    model_name = chat_model.name

    # 如果提供了知识库ID，从数据库获取知识库关联的模型详情
    if request.kb_ids:
        try:
            from backend.app.models.knowledge_base import KnowledgeBase

            # 获取第一个知识库的详情
            kb_result = await db.execute(
                select(KnowledgeBase).where(KnowledgeBase.id == request.kb_ids[0])
            )
            kb = kb_result.scalar_one_or_none()

            if kb:
                # 获取embedding模型详情
                if kb.embedding_model_id:
                    embedding_model_result = await db.execute(
                        select(Model).where(Model.id == kb.embedding_model_id, Model.is_active == True)
                    )
                    embedding_model = embedding_model_result.scalar_one_or_none()

                # 获取rerank模型详情
                if kb.rerank_model_id:
                    rerank_model_result = await db.execute(
                        select(Model).where(Model.id == kb.rerank_model_id, Model.is_active == True)
                    )
                    rerank_model = rerank_model_result.scalar_one_or_none()

                logger.info(
                    f"Knowledge base {kb.name} associated with embedding model: {embedding_model.name if embedding_model else 'None'}, rerank model: {rerank_model.name if rerank_model else 'None'}")
        except Exception as e:
            logger.error(f"Failed to fetch knowledge base models: {e}")

    # 如果本次请求指定了自定义模型（embedding 或 rerank），则创建新 workflow 实例
    if embedding_model is not None and rerank_model is not None:
        pipeline = LangGraphWorkflow(
            api_key=api_key,
            base_url=base_url,
            embedding_model=embedding_model,
            rerank_model=rerank_model,
            db=db
        )
    else:
        # 复用全局已初始化的 rag_pipeline（由 api/chat.py 初始化）
        if rag_pipeline is None:
            # 如果全局 rag_pipeline 未初始化，创建一个默认的
            pipeline = LangGraphWorkflow(
                api_key=api_key,
                base_url=base_url
            )
        else:
            pipeline = rag_pipeline

    # 获取领域信息
    domain = await _get_domain_from_kb(db, request.kb_ids)

    # 调用 pipeline.run
    result = await pipeline.run(
        query=request.query,
        kb_ids=request.kb_ids,
        conversation_history=history,
        model=model_name,
        temperature=chat_model.temperature if chat_model else 0.7,
        top_k=chat_model.top_k if chat_model else 4,
        top_p=chat_model.top_p if chat_model else 0.95,
        api_key=api_key,
        base_url=base_url,
        db=db,
        pm_db=pm_db,
        domain=domain,  # 传递领域参数
        user=user  # 传递用户参数，用于权限检查
    )

    # 处理返回结果
    if isinstance(result, dict) and "generation_result" in result:
        # 新格式：包含工作流步骤和当前状态
        workflow_steps = result.get("workflow_steps", [])
        current_state = result.get("current_state", "completed")
        result = result["generation_result"]
    else:
        # 旧格式：直接返回生成结果
        workflow_steps = []
        current_state = "completed"

    # 保存 AI 回复
    ai_message = Message(
        conversation_id=conversation.id,
        role="assistant",
        content=result.answer,
        citations=result.citations,
        confidence=result.confidence,
        token_usage={
            **result.token_usage,
            "response_time": result.response_time,
        },
        retrieval_info={
            "workflow_steps": workflow_steps,
            "current_state": current_state
        },
    )
    db.add(ai_message)

    # 创建聊天日志记录
    chat_log = ChatLog(
        user_id=user_id,
        conversation_id=conversation.id,
        message_id=ai_message.id,
        query=request.query,
        answer=result.answer,
        model_used=model_name,
        knowledge_bases=request.kb_ids,
        response_time=result.response_time,
    )
    db.add(chat_log)

    await db.commit()

    # 构建响应
    citations = [
        Citation(
            chunk_id=c.get("chunk_id", ""),
            doc_id=c.get("doc_id", ""),
            filename=c.get("filename", ""),
            content=c.get("content", ""),
            score=c.get("score", 0),
            page=c.get("page"),
        )
        for c in result.citations
    ]

    # 检查是否需要返回表格数据
    table_data = None
    if result.answer and '|' in result.answer and '---' in result.answer:
        # 简单的表格检测逻辑
        lines = result.answer.split('\n')
        headers = []
        rows = []
        in_table = False
        for line in lines:
            line = line.strip()
            if line.startswith('|') and '---' not in line:
                if not in_table:
                    in_table = True
                # 解析表格行
                cells = [cell.strip() for cell in line.strip('|').split('|')]
                if headers:
                    rows.append(cells)
                else:
                    headers = cells
            elif '---' in line and in_table:
                # 表格分隔线，跳过
                continue
            elif in_table and not line:
                # 表格结束
                break
        if headers and rows:
            from backend.app.schemas.chat import TableData
            table_data = TableData(headers=headers, rows=rows)

    return ChatResponse(
        message_id=ai_message.id,
        conversation_id=conversation.id,
        answer=result.answer,
        citations=citations,
        confidence=result.confidence,
        # suggested_questions=result.suggested_questions,
        token_usage={
            **result.token_usage,
            "response_time": result.response_time,
        },
        retrieval_info={
            "workflow_steps": workflow_steps,
            "current_state": current_state
        },
        table_data=table_data
    )

async def chat_stream(
    db: AsyncSession,
    request: ChatRequest,
    user_id: str,
):
    """处理流式聊天请求"""
    if not request.kb_ids:
        raise ValueError("请选择至少一个知识库")
    
    # 获取用户信息
    from backend.app.models.user import User
    user_result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = user_result.scalar_one_or_none()
    
    # 获取或创建对话
    if request.conversation_id:
        result = await db.execute(
            select(Conversation).where(Conversation.id == request.conversation_id)
        )
        conversation = result.scalar_one_or_none()
        if not conversation:
            # 为新对话生成新的 UUID，不使用前端的临时 ID
            conversation = Conversation(
                user_id=user_id,
                kb_id=request.kb_ids[0] if request.kb_ids else None,
                title=request.query[:50],
            )
            db.add(conversation)
            await db.flush()
    else:
        conversation = Conversation(
            user_id=user_id,
            kb_id=request.kb_ids[0] if request.kb_ids else None,
            title=request.query[:50],
        )
        db.add(conversation)
        await db.flush()
    
    # 自动获取默认的聊天模型
    result = await db.execute(
        select(Model).where(Model.type == "chat", Model.is_active == True).limit(1)
    )
    chat_model = result.scalar_one_or_none()
    
    if not chat_model:
        raise ValueError("请先前往模型管理设置默认聊天模型")
    
    # 设置默认模型 ID
    request.model_id = chat_model.id

    # 获取或创建 RAG pipeline
    pipeline = get_rag_pipeline(
        api_key=chat_model.api_key,
        base_url=chat_model.base_url
    )

    # 获取领域信息
    domain = await _get_domain_from_kb(db, request.kb_ids)
    
    # 保存用户消息
    user_message = Message(
        conversation_id=conversation.id,
        role="user",
        content=request.query,
    )
    db.add(user_message)
    
    # 收集完整的回复内容
    full_content = ""
    workflow_steps = []
    
    # 执行流式聊天
    async for token in pipeline.run_stream(
        query=request.query,
        kb_ids=request.kb_ids,
        model_id=request.model_id,
        domain=domain,
        user=user,  # 传递用户参数，用于权限检查
        db=db  # 传递数据库会话，用于权限检查
    ):
        # 收集 token
        full_content += token
        yield token
        
        # 尝试解析 workflow_steps（如果有）
        import json
        try:
            if token.startswith('data: '):
                data = json.loads(token[6:])
                if 'workflow_steps' in data:
                    workflow_steps = data['workflow_steps']
        except:
            pass
    
    # 保存 AI 回复
    ai_message = Message(
        conversation_id=conversation.id,
        role="assistant",
        content=full_content,
        citations=[],
        confidence=0.9,
        token_usage={},
        retrieval_info={
            "workflow_steps": workflow_steps,
            "current_state": "completed"
        },
    )
    db.add(ai_message)
    
    # 创建聊天日志记录
    chat_log = ChatLog(
        user_id=user_id,
        conversation_id=conversation.id,
        message_id=ai_message.id,
        query=request.query,
        answer=full_content,
        model_used=chat_model.name,
        knowledge_bases=request.kb_ids,
        response_time=0,  # 流式响应，暂时设为 0
    )
    db.add(chat_log)
    
    await db.commit()
    
    # 返回消息 ID
    yield f"data: {json.dumps({'message_id': ai_message.id, 'conversation_id': conversation.id}, ensure_ascii=False)}\n\n"


async def agent_chat(
    db: AsyncSession,
    request: ChatRequest,
    user_id: str,
) -> ChatResponse:
    """处理智能体聊天请求"""
    # 获取用户信息
    from backend.app.models.user import User
    user_result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = user_result.scalar_one_or_none()
    
    # 获取或创建对话
    if request.conversation_id:
        result = await db.execute(
            select(Conversation).where(Conversation.id == request.conversation_id)
        )
        conversation = result.scalar_one_or_none()
        if not conversation:
            # 为新对话生成新的UUID，不使用前端的临时ID
            conversation = Conversation(
                user_id=user_id,
                kb_id=request.kb_ids[0] if request.kb_ids else None,
                title=request.query[:50],
            )
            db.add(conversation)
            await db.flush()
    else:
        conversation = Conversation(
            user_id=user_id,
            kb_id=request.kb_ids[0] if request.kb_ids else None,
            title=request.query[:50],
        )
        db.add(conversation)
        await db.flush()

    # 保存用户消息
    user_message = Message(
        conversation_id=conversation.id,
        role="user",
        content=request.query,
    )
    db.add(user_message)

    # 获取对话历史，使用context_round参数控制历史长度
    limit = request.context_round * 2 if request.context_round else 10  # 每个轮次包含用户和助手的消息，所以乘以2
    history = await _get_conversation_history(db, conversation.id, limit)

    # 如果提供了 model_id，从数据库获取模型详情
    embedding_model = None
    rerank_model = None

    result = await db.execute(
        select(Model).where(Model.type == "chat", Model.is_active == True).limit(1)
    )
    chat_model = result.scalar_one_or_none()
    api_key = chat_model.api_key
    base_url = chat_model.base_url
    model_name = chat_model.name
    
    # 如果提供了知识库ID，从数据库获取知识库关联的模型详情
    if request.kb_ids:
        try:
            from backend.app.models.knowledge_base import KnowledgeBase
            
            # 获取第一个知识库的详情
            kb_result = await db.execute(
                select(KnowledgeBase).where(KnowledgeBase.id == request.kb_ids[0])
            )
            kb = kb_result.scalar_one_or_none()
            
            if kb:
                # 获取embedding模型详情
                if kb.embedding_model_id:
                    embedding_model_result = await db.execute(
                        select(Model).where(Model.id == kb.embedding_model_id, Model.is_active == True)
                    )
                    embedding_model = embedding_model_result.scalar_one_or_none()
                
                # 获取rerank模型详情
                if kb.rerank_model_id:
                    rerank_model_result = await db.execute(
                        select(Model).where(Model.id == kb.rerank_model_id, Model.is_active == True)
                    )
                    rerank_model = rerank_model_result.scalar_one_or_none()
                
                logger.info(f"Knowledge base {kb.name} associated with embedding model: {embedding_model.name if embedding_model else 'None'}, rerank model: {rerank_model.name if rerank_model else 'None'}")
        except Exception as e:
            logger.error(f"Failed to fetch knowledge base models: {e}")

    # 如果本次请求指定了自定义模型（embedding 或 rerank），则创建新 workflow 实例
    if embedding_model is not None and rerank_model is not None:
        pipeline = LangGraphWorkflow(
            api_key=api_key,
            base_url=base_url,
            embedding_model=embedding_model,
            rerank_model=rerank_model,
            db = db
        )
    else:
        # 复用全局已初始化的 rag_pipeline（由 api/chat.py 初始化）
        if rag_pipeline is None:
            # 如果全局 rag_pipeline 未初始化，创建一个默认的
            pipeline = LangGraphWorkflow(
                api_key=api_key,
                base_url=base_url
            )
        else:
            pipeline = rag_pipeline

    # 获取领域信息
    domain = await _get_domain_from_kb(db, request.kb_ids)

    # 构建上下文
    context = {
        'conversation_history': history,
        'domain': domain,
        'user': user
    }

    # 调用智能体执行
    agent_result = await pipeline.run_with_agent(
        query=request.query,
        kb_ids=request.kb_ids,
        context=context,
        model=model_name,
        # temperature=chat_model.temperature if chat_model else 0.7,
        api_key=api_key,
        base_url=base_url
    )

    # 提取智能体执行结果
    if agent_result.get('result', {}).get('success'):
        answer = agent_result['result'].get('response', '智能体执行失败')
        confidence = agent_result['result'].get('confidence', 0.0)
    else:
        answer = f"智能体执行失败: {agent_result.get('result', {}).get('error', '未知错误')}"
        confidence = 0.0

    # 提取工作流步骤和当前状态
    workflow_steps = agent_result.get('workflow_steps', [])
    current_state = agent_result.get('current_state', 'completed')

    # 保存 AI 回复
    ai_message = Message(
        conversation_id=conversation.id,
        role="assistant",
        content=answer,
        confidence=confidence,
        token_usage={
            "workflow_steps": agent_result.get('workflow_steps', []),
            "current_state": agent_result.get('current_state', 'completed')
        },
    )
    db.add(ai_message)
    
    # 创建聊天日志记录
    chat_log = ChatLog(
        user_id=user_id,
        conversation_id=conversation.id,
        message_id=ai_message.id,
        query=request.query,
        answer=answer,
        model_used=model_name,
        knowledge_bases=request.kb_ids,
        agent_used=agent_result.get('agent', 'research_agent'),
    )
    db.add(chat_log)
    
    await db.commit()

    # 检查是否需要返回表格数据
    table_data = None
    if answer and '|' in answer and '---' in answer:
        # 简单的表格检测逻辑
        lines = answer.split('\n')
        headers = []
        rows = []
        in_table = False
        for line in lines:
            line = line.strip()
            if line.startswith('|') and '---' not in line:
                if not in_table:
                    in_table = True
                # 解析表格行
                cells = [cell.strip() for cell in line.strip('|').split('|')]
                if headers:
                    rows.append(cells)
                else:
                    headers = cells
            elif '---' in line and in_table:
                # 表格分隔线，跳过
                continue
            elif in_table and not line:
                # 表格结束
                break
        if headers and rows:
            from backend.app.schemas.chat import TableData
            table_data = TableData(headers=headers, rows=rows)

    return ChatResponse(
        message_id=ai_message.id,
        conversation_id=conversation.id,
        answer=answer,
        citations=[],
        confidence=confidence,
        suggested_questions=[],
        token_usage={
            "workflow_steps": agent_result.get('workflow_steps', []),
            "current_state": agent_result.get('current_state', 'completed')
        },
        table_data=table_data
    )


async def agent_chat_stream(
    db: AsyncSession,
    request: ChatRequest,
    user_id: str,
):
    """处理智能体流式聊天请求"""
    # 获取用户信息
    from backend.app.models.user import User
    user_result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = user_result.scalar_one_or_none()
    
    # 获取或创建对话
    if request.conversation_id:
        result = await db.execute(
            select(Conversation).where(Conversation.id == request.conversation_id)
        )
        conversation = result.scalar_one_or_none()
        if not conversation:
            # 为新对话生成新的 UUID，不使用前端的临时 ID
            conversation = Conversation(
                user_id=user_id,
                kb_id=request.kb_ids[0] if request.kb_ids else None,
                title=request.query[:50],
            )
            db.add(conversation)
            await db.flush()
    else:
        conversation = Conversation(
            user_id=user_id,
            kb_id=request.kb_ids[0] if request.kb_ids else None,
            title=request.query[:50],
        )
        db.add(conversation)
        await db.flush()
    
    # 自动获取默认的聊天模型
    result = await db.execute(
        select(Model).where(Model.type == "chat", Model.is_active == True).limit(1)
    )
    chat_model = result.scalar_one_or_none()
    
    if not chat_model:
        raise ValueError("请先前往模型管理设置默认聊天模型")
    
    # 获取或创建 RAG pipeline
    pipeline = get_rag_pipeline(
        api_key=chat_model.api_key,
        base_url=chat_model.base_url
    )

    # 获取领域信息
    domain = await _get_domain_from_kb(db, request.kb_ids)

    # 构建上下文
    context = {
        'domain': domain,
        'user': user
    }
    
    # 保存用户消息
    user_message = Message(
        conversation_id=conversation.id,
        role="user",
        content=request.query,
    )
    db.add(user_message)
    
    # 收集完整的回复内容和工作流步骤
    full_content = ""
    workflow_steps = []
    current_state = "running"
    
    # 执行智能体流式聊天
    async for token in pipeline.run_with_agent_stream(
        query=request.query,
        kb_ids=request.kb_ids,
        context=context,
        model=chat_model.name,
        api_key=chat_model.api_key,
        base_url=chat_model.base_url
    ):
        # 收集 token（只提取纯文本内容）
        import json
        try:
            # 尝试解析 token，如果是 JSON 格式，提取内部的 token 字段
            if token.startswith('data: '):
                data = json.loads(token[6:])
                # 如果是工作流步骤信息，不添加到 full_content
                if 'workflow_steps' in data or 'current_step' in data or 'message_id' in data:
                    pass  # 不添加到 full_content
                elif 'token' in data:
                    # 如果是 token 数据，检查是否是嵌套的 JSON
                    inner_token = data['token']
                    if isinstance(inner_token, str) and inner_token.startswith('data: '):
                        try:
                            inner_data = json.loads(inner_token[6:])
                            # 过滤掉 [DONE] 标记
                            if inner_data.get('token') == '[DONE]' or (isinstance(inner_data.get('token'), str) and '[DONE]' in inner_data.get('token', '')):
                                pass  # 不添加 [DONE]
                            elif 'token' in inner_data:
                                full_content += inner_data['token']
                        except:
                            # 不是 JSON，直接添加（但要过滤 [DONE]）
                            if '[DONE]' not in inner_token:
                                full_content += inner_token
                    else:
                        # 过滤掉 [DONE]
                        if '[DONE]' not in inner_token:
                            full_content += inner_token
            else:
                # 普通 token，直接添加（过滤 [DONE]）
                if '[DONE]' not in token:
                    full_content += token
        except:
            # 解析失败，直接添加原始 token（过滤 [DONE]）
            if '[DONE]' not in token:
                full_content += token
        
        yield token
        
        # 尝试解析 workflow_steps（如果有）
        try:
            if token.startswith('data: '):
                data = json.loads(token[6:])
                if 'workflow_steps' in data:
                    workflow_steps = data['workflow_steps']
                if 'current_state' in data:
                    current_state = data['current_state']
        except:
            pass
    
    # 保存 AI 回复
    ai_message = Message(
        conversation_id=conversation.id,
        role="assistant",
        content=full_content,
        citations=[],
        confidence=0.9,
        token_usage={
            "workflow_steps": workflow_steps,
            "current_state": current_state
        },
    )
    db.add(ai_message)
    
    # 创建聊天日志记录
    chat_log = ChatLog(
        user_id=user_id,
        conversation_id=conversation.id,
        message_id=ai_message.id,
        query=request.query,
        answer=full_content,
        model_used=chat_model.name,
        knowledge_bases=request.kb_ids,
        agent_used="research_agent",  # 默认智能体
        response_time=0,  # 流式响应，暂时设为 0
    )
    db.add(chat_log)
    
    await db.commit()
    
    # 返回消息 ID
    yield f"data: {json.dumps({'message_id': ai_message.id, 'conversation_id': conversation.id}, ensure_ascii=False)}\n\n"