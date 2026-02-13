from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class ChatRequest(BaseModel):
    """用户聊天请求"""
    query: str
    conversation_id: Optional[str] = None
    kb_ids: List[str] = []                    # 搜索哪些知识库
    model: Optional[str] = None
    temperature: Optional[float] = None
    top_k: Optional[int] = None
    stream: bool = False


class Citation(BaseModel):
    """引用来源"""
    chunk_id: str
    doc_id: str
    filename: str
    content: str
    score: float
    page: Optional[int] = None
    highlight: Optional[str] = None


class ChatResponse(BaseModel):
    """聊天响应"""
    message_id: str
    conversation_id: str
    answer: str
    citations: List[Citation] = []
    confidence: float = 0.0
    suggested_questions: List[str] = []
    token_usage: Optional[dict] = None


class ConversationResponse(BaseModel):
    id: str
    title: str
    kb_id: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    id: str
    role: str
    content: str
    citations: Optional[dict]
    confidence: Optional[float]
    created_at: datetime

    class Config:
        from_attributes = True


class FeedbackRequest(BaseModel):
    message_id: str
    rating: int        # 1, 2, 3
    comment: Optional[str] = None