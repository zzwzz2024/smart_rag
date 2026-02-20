"""
对话服务
"""
import uuid
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from backend.app.core.embedder import EmbeddingService
from backend.app.models.conversation import Conversation, Message
from backend.app.models.model import Model
from backend.app.core.rag_pipeline import RAGPipeline
from backend.app.schemas.chat import ChatRequest, ChatResponse, Citation

rag_pipeline = None

def get_rag_pipeline(api_key=None, base_url=None):
    """获取 RAGPipeline 实例，支持惰性初始化"""
    global rag_pipeline
    if rag_pipeline is None:
        rag_pipeline = RAGPipeline(api_key=api_key, base_url=base_url)
    return rag_pipeline

async def chat(
    db: AsyncSession,
    request: ChatRequest,
    user_id: str,
) -> ChatResponse:
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

    # 获取对话历史
    history = await _get_conversation_history(db, conversation.id)

    # 如果提供了 model_id，从数据库获取模型详情
    model_name = request.model
    api_key = ""
    base_url = ""
    embedding_model = None
    rerank_model = None
    chat_model = None
    
    if request.model_id:
        try:
            model_result = await db.execute(
                select(Model).where(Model.id == request.model_id, Model.is_active == True)
            )
            model = model_result.scalar_one_or_none()
            if model:
                model_name = model.model
                api_key = model.api_key
                base_url = model.base_url
                chat_model = model
        except Exception as e:
            logger.error(f"Failed to fetch model: {e}")
    
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

    # 替换原 L117-L127 块为：
    global rag_pipeline

    # 如果本次请求指定了自定义模型（embedding 或 rerank），则创建新 pipeline 实例
    if rag_pipeline is None and embedding_model is not None and rerank_model is not None:
        pipeline = RAGPipeline(
            api_key=api_key,
            base_url=base_url,
            embedding_model=embedding_model,
            rerank_model=rerank_model
        )
    else:
        # 复用全局已初始化的 rag_pipeline（由 api/chat.py 初始化）
        if rag_pipeline is None:
            raise RuntimeError("全局 rag_pipeline 未初始化，请检查 api/chat.py 初始化逻辑")
        pipeline = rag_pipeline

    # 调用 pipeline.run
    result = await pipeline.run(
        query=request.query,
        kb_ids=request.kb_ids,
        conversation_history=history,
        model=model_name,
        temperature=chat_model.temperature,
        top_k=chat_model.top_k,
        top_p=chat_model.top_p,
        api_key=api_key,
        base_url=base_url
    )

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
    )
    db.add(ai_message)
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

    return ChatResponse(
        message_id=ai_message.id,
        conversation_id=conversation.id,
        answer=result.answer,
        citations=citations,
        confidence=result.confidence,
        # suggested_questions=result.suggested_questions,
        token_usage=result.token_usage,
    )


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