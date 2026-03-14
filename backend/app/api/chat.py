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
import backend.app.services.chat_service as chat_service

router = APIRouter()


from backend.app.models.response_model import Response

@router.post("", response_model=Response)
async def chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """发送聊天消息"""

    # 实现意图识别和知识库匹配
    from backend.app.services.intent_service import IntentService
    intent_service = IntentService(db, user.id)
    matched_kb_ids = await intent_service.match_knowledge_bases(request.query)
    
    # 如果匹配到知识库，使用匹配结果；否则使用请求中的知识库（如果有）
    if matched_kb_ids:
        request.kb_ids = matched_kb_ids

    response = await chat_service.chat(db, request, user.id)
    return Response(data=response)


@router.post("/stream")
async def chat_stream(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """流式聊天"""
    try:
        async def event_generator():
            async for token in chat_service.chat_stream(db, request, user.id):
                yield f"data: {json.dumps({'token': token}, ensure_ascii=False)}\n\n"
            yield "data: [DONE]\n\n"

        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
        )
    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        raise HTTPException(500, f"流式聊天失败：{str(e)}")


@router.get("/conversations", response_model=Response)
async def list_conversations(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """获取对话列表"""
    result = await db.execute(
        select(Conversation)
        .where(Conversation.user_id == user.id, Conversation.is_deleted == False)
        .order_by(Conversation.updated_at.desc())
        .limit(50)
    )
    conversations = result.scalars().all()
    return Response(data=[ConversationResponse.model_validate(c) for c in conversations])


@router.get("/conversations/{conv_id}/messages", response_model=Response)
async def get_messages(
    conv_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """获取对话消息"""
    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conv_id, Message.is_deleted == False)
        .order_by(Message.created_at)
    )
    messages = result.scalars().all()
    return Response(data=[MessageResponse.model_validate(m) for m in messages])


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


@router.delete("/conversations/{conv_id}", response_model=Response)
async def delete_conversation(
    conv_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """删除对话"""
    result = await db.execute(
        select(Conversation).where(Conversation.id == conv_id, Conversation.is_deleted == False)
    )
    conv = result.scalar_one_or_none()
    if not conv or conv.user_id != user.id:
        raise HTTPException(404, "对话不存在")
    # 伪删除：将is_deleted字段设置为True
    conv.is_deleted = True
    await db.commit()
    return Response(data={"message": "已删除"})


@router.put("/conversations/{conv_id}/title", response_model=Response)
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
    return Response(data={"message": "标题已更新", "title": conv.title})


@router.put("/conversations/{conv_id}/pinned", response_model=Response)
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
    return Response(data={"message": "置顶状态已更新", "pinned": conv.pinned})


@router.post("/initialize-model", response_model=Response)
async def initialize_model(
    model_data: dict,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """初始化模型"""
    model_id = model_data.get("model_id")
    if not model_id:
        raise HTTPException(400, "模型ID不能为空")
    
    # 获取知识库和模型参数
    kb_id = model_data.get("kb_id")
    embedding_model_id = model_data.get("embedding_model_id")
    rerank_model_id = model_data.get("rerank_model_id")

    try:
        # 调用service层的初始化方法
        model = chat_service.initialize_rag_pipeline(
            model_id=model_id,
            kb_id=kb_id,
            embedding_model_id=embedding_model_id,
            rerank_model_id=rerank_model_id,
            db=db
        )
        return Response(data={"message": f"模型 {model.name} 配置验证成功", "model_id": model_id, "model": model.model})
    except ValueError as e:
        raise HTTPException(404, str(e))
    except Exception as e:
        raise HTTPException(500, f"初始化模型失败：{str(e)}")