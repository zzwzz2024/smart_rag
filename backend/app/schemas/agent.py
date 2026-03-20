"""智能体相关的数据模型"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class FeedbackRequest(BaseModel):
    """反馈请求模型"""
    message_id: str = Field(..., description="消息ID")
    rating: int = Field(..., ge=0, le=1, description="反馈评分，0为负反馈，1为正反馈")
    comment: Optional[str] = Field(None, description="反馈评论")


class FeedbackResponse(BaseModel):
    """反馈响应模型"""
    id: str
    conversation_id: str
    query: str
    response: str
    feedback: int
    timestamp: datetime
    metadata: Optional[Dict[str, Any]]
