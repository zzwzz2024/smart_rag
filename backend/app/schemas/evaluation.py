from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class EvalMetrics(BaseModel):
    """评估指标"""
    total_queries: int = 0
    avg_confidence: float = 0.0
    hallucination_rate: float = 0.0
    citation_rate: float = 0.0
    positive_feedback_rate: float = 0.0
    avg_response_time: float = 0.0


class EvalDetail(BaseModel):
    query: str
    answer: str
    confidence: float
    has_citation: bool
    feedback_rating: Optional[int]
    response_time: float


class EvalReport(BaseModel):
    kb_id: str
    kb_name: str
    metrics: EvalMetrics
    bad_cases: List[EvalDetail] = []
    period: str  # "7d" / "30d"


class EvalCreate(BaseModel):
    """创建评估请求"""
    query: str
    reference_answer: str
    kb_ids: List[str] = []
    model_id: str


class EvalResponse(BaseModel):
    """评估响应"""
    id: int
    query: str
    reference_answer: str
    rag_answer: str
    score: float
    kb_id: str
    model_id: str
    created_at: datetime

    class Config:
        from_attributes = True