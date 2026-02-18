"""
对话 API
"""
import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.rag_pipeline import RAGPipeline
from backend.app.models.model import Model
from backend.app.database import get_db
from backend.app.models.user import User
from backend.app.models.conversation import Conversation, Message, Feedback
from backend.app.schemas.chat import (
    ChatRequest, ChatResponse, ConversationResponse,
    MessageResponse, FeedbackRequest,
)
from backend.app.utils.auth import get_current_user
import backend.app.services.chat_service as chat_service

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
    
    if not request.model_id:
        raise HTTPException(400, "请选择一个模型，如果没有可用模型，请前往模型设置页面配置")

    response = await chat_service.chat(db, request, user.id)
    return response


@router.post("/stream")
async def chat_stream(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """流式聊天"""
    if not request.kb_ids:
        raise HTTPException(400, "请选择至少一个知识库")
    
    if not request.model_id:
        raise HTTPException(400, "请选择一个模型，如果没有可用模型，请前往模型设置页面配置")

    from backend.app.core.rag_pipeline import RAGPipeline
    pipeline = RAGPipeline()

    async def event_generator():
        async for token in pipeline.run_stream(
            query=request.query,
            kb_ids=request.kb_ids,
            model_id=request.model_id,
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


@router.put("/conversations/{conv_id}/title")
async def update_conversation_title(
    conv_id: str,
    title: dict,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """更新对话标题"""
    result = await db.execute(
        select(Conversation).where(Conversation.id == conv_id)
    )
    conv = result.scalar_one_or_none()
    if not conv or conv.user_id != user.id:
        raise HTTPException(404, "对话不存在")
    
    conv.title = title.get("title", conv.title)
    await db.commit()
    return {"message": "标题已更新", "title": conv.title}


@router.put("/conversations/{conv_id}/pinned")
async def toggle_conversation_pinned(
    conv_id: str,
    pinned: dict,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """切换对话置顶状态"""
    result = await db.execute(
        select(Conversation).where(Conversation.id == conv_id)
    )
    conv = result.scalar_one_or_none()
    if not conv or conv.user_id != user.id:
        raise HTTPException(404, "对话不存在")
    
    conv.pinned = pinned.get("pinned", False)
    await db.commit()
    return {"message": "置顶状态已更新", "pinned": conv.pinned}


@router.post("/initialize-model")
async def initialize_model(
    model_data: dict,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """初始化模型"""
    model_id = model_data.get("model_id")
    if not model_id:
        raise HTTPException(400, "模型ID不能为空")
    
    # 从数据库获取模型详情
    result = await db.execute(
        select(Model).where(Model.id == model_id, Model.is_active == True)
    )
    model = result.scalar_one_or_none()
    if not model:
        raise HTTPException(404, "模型不存在或未激活")

    # 获取知识库和模型参数
    kb_id = model_data.get("kb_id")
    embedding_model_id = model_data.get("embedding_model_id")
    rerank_model_id = model_data.get("rerank_model_id")

    # 初始化模型变量
    embedding_model = None
    rerank_model = None

    # 如果提供了embedding_model_id，从数据库获取embedding模型详情
    if embedding_model_id:
        embedding_result = await db.execute(
            select(Model).where(Model.id == embedding_model_id, Model.is_active == True)
        )
        embedding_model = embedding_result.scalar_one_or_none()

    # 如果提供了rerank_model_id，从数据库获取rerank模型详情
    if rerank_model_id:
        rerank_result = await db.execute(
            select(Model).where(Model.id == rerank_model_id, Model.is_active == True)
        )
        rerank_model = rerank_result.scalar_one_or_none()

    # 初始化RAG pipeline，传递模型详情
    chat_service.rag_pipeline = RAGPipeline(
        api_key=model.api_key,
        base_url=model.base_url,
        embedding_model=embedding_model,
        rerank_model=rerank_model
    )

    return {"message": f"模型 {model.name} 配置验证成功", "model_id": model_id, "model": model.model}