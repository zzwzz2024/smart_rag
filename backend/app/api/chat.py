"""
对话 API
"""
import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database import get_db
from backend.app.models.user import User
from backend.app.models.conversation import Conversation, Message, Feedback
from backend.app.schemas.chat import (
    ChatRequest, ChatResponse, ConversationResponse,
    MessageResponse, FeedbackRequest,
)
from backend.app.utils.auth import get_current_user
from backend.app.services.chat_service import chat as chat_service

router = APIRouter()


@router.post("", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """发送聊天消息"""
    if not request.kb_ids:
        raise HTTPException(400, "请选择至少一个知识库")

    response = await chat_service(db, request, user.id)
    return response


@router.post("/stream")
async def chat_stream(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """流式聊天"""
    from backend.app.core.rag_pipeline import RAGPipeline
    pipeline = RAGPipeline()

    async def event_generator():
        async for token in pipeline.run_stream(
            query=request.query,
            kb_ids=request.kb_ids,
        ):
            yield f"data: {json.dumps({'token': token}, ensure_ascii=False)}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
    )


@router.get("/conversations", response_model=List[ConversationResponse])
async def list_conversations(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """获取对话列表"""
    result = await db.execute(
        select(Conversation)
        .where(Conversation.user_id == user.id)
        .order_by(Conversation.updated_at.desc())
        .limit(50)
    )
    conversations = result.scalars().all()
    return [ConversationResponse.model_validate(c) for c in conversations]


@router.get("/conversations/{conv_id}/messages", response_model=List[MessageResponse])
async def get_messages(
    conv_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """获取对话消息"""
    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conv_id)
        .order_by(Message.created_at)
    )
    messages = result.scalars().all()
    return [MessageResponse.model_validate(m) for m in messages]


@router.post("/feedback")
async def submit_feedback(
    data: FeedbackRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """提交反馈"""
    feedback = Feedback(
        message_id=data.message_id,
        rating=data.rating,
        comment=data.comment,
    )
    db.add(feedback)
    return {"message": "反馈已提交"}


@router.delete("/conversations/{conv_id}")
async def delete_conversation(
    conv_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """删除对话"""
    result = await db.execute(
        select(Conversation).where(Conversation.id == conv_id)
    )
    conv = result.scalar_one_or_none()
    if not conv or conv.user_id != user.id:
        raise HTTPException(404, "对话不存在")
    await db.delete(conv)
    return {"message": "已删除"}