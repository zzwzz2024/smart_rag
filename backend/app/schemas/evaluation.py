from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class EvalMetrics(BaseModel):
    """评估指标"""
    total_queries: int = Field(0, description="总查询数")
    avg_confidence: float = Field(0.0, description="平均置信度")
    hallucination_rate: float = Field(0.0, description="幻觉率")
    citation_rate: float = Field(0.0, description="引用率")
    positive_feedback_rate: float = Field(0.0, description="正面反馈率")
    avg_response_time: float = Field(0.0, description="平均响应时间")


class EvalDetail(BaseModel):
    query: str = Field(..., description="查询内容")
    answer: str = Field(..., description="回答内容")
    confidence: float = Field(..., description="置信度")
    has_citation: bool = Field(..., description="是否有引用")
    feedback_rating: Optional[int] = Field(None, description="反馈评分，可选")
    response_time: float = Field(..., description="响应时间")


class EvalReport(BaseModel):
    kb_id: str = Field(..., description="知识库ID")
    kb_name: str = Field(..., description="知识库名称")
    metrics: EvalMetrics = Field(..., description="评估指标")
    bad_cases: List[EvalDetail] = Field(default_factory=list, description="不良案例")
    period: str = Field(..., description="评估周期（\"7d\" / \"30d\"）")


class EvalCreate(BaseModel):
    """创建评估请求"""
    query: str = Field(..., description="查询内容")
    reference_answer: str = Field(..., description="参考回答")
    kb_ids: List[str] = Field(default_factory=list, description="知识库ID列表")
    model_id: str = Field(..., description="模型ID")


class EvalResponse(BaseModel):
    """评估响应"""
    id: int = Field(..., description="评估ID")
    query: str = Field(..., description="查询内容")
    reference_answer: str = Field(..., description="参考回答")
    rag_answer: str = Field(..., description="RAG回答")
    score: float = Field(..., description="评分")
    kb_id: str = Field(..., description="知识库ID")
    model_id: str = Field(..., description="模型ID")
    created_at: datetime = Field(..., description="创建时间")

    class Config:
        from_attributes = True
