"""
对话服务
"""
import uuid
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from backend.app.models.conversation import Conversation, Message
from backend.app.models.model import Model
from backend.app.core.rag_pipeline import RAGPipeline
from backend.app.schemas.chat import ChatRequest, ChatResponse, Citation

rag_pipeline = RAGPipeline()


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
            conversation = Conversation(
                id=request.conversation_id,
                user_id=user_id,
                kb_id=request.kb_ids[0] if request.kb_ids else None,
                title=request.query[:50],
            )
            db.add(conversation)
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
    if request.model_id:
        try:
            model_result = await db.execute(
                select(Model).where(Model.id == request.model_id, Model.is_active == True)
            )
            model = model_result.scalar_one_or_none()
            if model:
                model_name = model.model
        except Exception as e:
            logger.error(f"Failed to fetch model: {e}")

    # 调用 RAG Pipeline
    result = await rag_pipeline.run(
        query=request.query,
        kb_ids=request.kb_ids,
        conversation_history=history,
        model=model_name,
        model_id=request.model_id,
        temperature=request.temperature,
        top_k=request.top_k,
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