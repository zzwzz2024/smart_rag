from pydantic import BaseModel, field_validator, Field
from datetime import datetime
from typing import Optional, List


class ChatRequest(BaseModel):
    """用户聊天请求"""
    query: str = Field(..., description="聊天查询内容")
    conversation_id: Optional[str] = Field(None, description="对话ID，可选")
    kb_ids: List[str] = Field(default_factory=list, description="搜索哪些知识库")
    model: Optional[str] = Field(None, description="模型名称，可选")
    model_id: Optional[str] = Field(None, description="模型ID，可选")
    temperature: Optional[float] = Field(None, description="温度参数，可选")
    top_k: Optional[int] = Field(None, description="搜索结果数量，可选")
    stream: bool = Field(False, description="是否流式响应")
    context_round: Optional[int] = Field(None, description="上下文轮数，可选")


class Citation(BaseModel):
    """引用来源"""
    chunk_id: str = Field(..., description="文本块ID")
    doc_id: str = Field(..., description="文档ID")
    filename: str = Field(..., description="文件名")
    content: str = Field(..., description="引用内容")
    score: float = Field(..., description="相关度分数")
    page: Optional[int] = Field(None, description="页码，可选")
    highlight: Optional[str] = Field(None, description="高亮内容，可选")


class ChatResponse(BaseModel):
    """聊天响应"""
    message_id: str = Field(..., description="消息ID")
    conversation_id: str = Field(..., description="对话ID")
    answer: str = Field(..., description="回答内容")
    citations: List[Citation] = Field(default_factory=list, description="引用来源列表")
    confidence: float = Field(0.0, description="置信度")
    suggested_questions: List[str] = Field(default_factory=list, description="建议问题列表")
    token_usage: Optional[dict] = Field(None, description="token使用情况，可选")


class ConversationResponse(BaseModel):
    id: str = Field(..., description="对话ID")
    title: str = Field(..., description="对话标题")
    kb_id: Optional[str] = Field(None, description="知识库ID，可选")
    pinned: bool = Field(False, description="是否置顶")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    id: str = Field(..., description="消息ID")
    role: str = Field(..., description="角色（user/assistant）")
    content: str = Field(..., description="消息内容")
    citations: Optional[List[dict]] = Field(None, description="引用来源，可选")
    confidence: Optional[float] = Field(None, description="置信度，可选")
    created_at: datetime = Field(..., description="创建时间")

    class Config:
        from_attributes = True
    
    @field_validator('citations', mode='before')
    @classmethod
    def parse_citations(cls, v):
        if isinstance(v, str):
            import json
            try:
                return json.loads(v)
            except:
                return None
        return v


class FeedbackRequest(BaseModel):
    message_id: str = Field(..., description="消息ID")
    rating: int = Field(..., description="评分（1-3）")
    comment: Optional[str] = Field(None, description="评论，可选")
