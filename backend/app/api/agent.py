"""智能体相关API"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import uuid

from backend.app.database import get_db
from backend.app.schemas.agent import FeedbackRequest, FeedbackResponse
from backend.app.models.agent import AgentFeedback
from backend.app.models.response_model import Response

router = APIRouter()

@router.post("/feedback", response_model=Response)
async def submit_feedback(
    feedback_data: FeedbackRequest,
    db: AsyncSession = Depends(get_db),
):
    """提交智能体反馈"""
    try:
        feedback = AgentFeedback(
            id=str(uuid.uuid4()),
            conversation_id=feedback_data.message_id,
            query="",
            response="",
            feedback=feedback_data.rating,
            metadata={"comment": feedback_data.comment}
        )
        db.add(feedback)
        await db.commit()
        await db.refresh(feedback)
        return Response(data={"message": "反馈提交成功"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"提交反馈失败: {str(e)}")


@router.get("/feedback", response_model=Response)
async def get_feedback(
    limit: int = 100,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    """获取反馈列表"""
    try:
        from sqlalchemy import select
        result = await db.execute(
            select(AgentFeedback).offset(offset).limit(limit).order_by(AgentFeedback.timestamp.desc())
        )
        feedbacks = result.scalars().all()
        return Response(data=[
            {
                "id": f.id,
                "conversation_id": f.conversation_id,
                "query": f.query,
                "response": f.response,
                "feedback": f.feedback,
                "timestamp": f.timestamp,
                "metadata": f.metadata
            }
            for f in feedbacks
        ])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取反馈失败: {str(e)}")
