"""
SmartRAG 效果评估引擎
"""
from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from backend.app.models.conversation import Message, Feedback
from backend.app.schemas.evaluation import EvalMetrics, EvalReport, EvalDetail


class Evaluator:
    """效果评估器"""

    async def generate_report(
        self,
        db: AsyncSession,
        kb_id: str,
        kb_name: str,
        period_days: int = 30,
    ) -> EvalReport:
        """生成评估报告"""
        since = datetime.utcnow() - timedelta(days=period_days)

        # 查询该知识库相关的消息
        stmt = (
            select(Message)
            .where(
                and_(
                    Message.role == "assistant",
                    Message.created_at >= since,
                )
            )
        )
        result = await db.execute(stmt)
        messages = result.scalars().all()

        if not messages:
            return EvalReport(
                kb_id=kb_id,
                kb_name=kb_name,
                metrics=EvalMetrics(),
                period=f"{period_days}d",
            )

        # 计算指标
        total = len(messages)
        confidences = [m.confidence for m in messages if m.confidence is not None]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0

        cited = sum(
            1 for m in messages
            if m.citations and len(m.citations) > 0
        )
        citation_rate = cited / total if total else 0

        # 低置信度 ≈ 可能幻觉
        hallucination_count = sum(
            1 for c in confidences if c < 0.4
        )
        hallucination_rate = hallucination_count / len(confidences) if confidences else 0

        # 反馈统计
        msg_ids = [m.id for m in messages]
        fb_stmt = select(Feedback).where(Feedback.message_id.in_(msg_ids))
        fb_result = await db.execute(fb_stmt)
        feedbacks = fb_result.scalars().all()

        positive = sum(1 for f in feedbacks if f.rating >= 3)
        positive_rate = positive / len(feedbacks) if feedbacks else 0

        # 响应时间
        response_times = [
            m.token_usage.get("response_time", 0)
            for m in messages
            if m.token_usage
        ]
        avg_response_time = (
            sum(response_times) / len(response_times) if response_times else 0
        )

        # Bad cases
        bad_cases = []
        for m in messages:
            if m.confidence is not None and m.confidence < 0.5:
                fb = next(
                    (f for f in feedbacks if f.message_id == m.id), None
                )
                bad_cases.append(EvalDetail(
                    query="",  # 需要关联 user message
                    answer=m.content[:200],
                    confidence=m.confidence,
                    has_citation=bool(m.citations),
                    feedback_rating=fb.rating if fb else None,
                    response_time=m.token_usage.get("response_time", 0) if m.token_usage else 0,
                ))

        metrics = EvalMetrics(
            total_queries=total,
            avg_confidence=round(avg_confidence, 4),
            hallucination_rate=round(hallucination_rate, 4),
            citation_rate=round(citation_rate, 4),
            positive_feedback_rate=round(positive_rate, 4),
            avg_response_time=round(avg_response_time, 2),
        )

        return EvalReport(
            kb_id=kb_id,
            kb_name=kb_name,
            metrics=metrics,
            bad_cases=bad_cases[:20],
            period=f"{period_days}d",
        )