"""
效果评估 API
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database import get_db
from backend.app.models.user import User
from backend.app.models.knowledge_base import KnowledgeBase
from backend.app.models.evaluation import Evaluation
from backend.app.schemas.evaluation import EvalReport, EvalMetrics, EvalCreate, EvalResponse
from backend.app.utils.auth import get_current_user
from backend.app.core.evaluator import Evaluator
from backend.app.core.rag_pipeline import RAGPipeline

router = APIRouter()
evaluator = Evaluator()
pipeline = RAGPipeline()


@router.get("/report/{kb_id}", response_model=EvalReport)
async def get_eval_report(
    kb_id: str,
    period: int = 30,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """获取知识库评估报告"""
    result = await db.execute(
        select(KnowledgeBase).where(KnowledgeBase.id == kb_id)
    )
    kb = result.scalar_one_or_none()
    if not kb:
        return EvalReport(
            kb_id=kb_id, kb_name="未知", metrics=EvalMetrics(), period=f"{period}d"
        )

    report = await evaluator.generate_report(db, kb_id, kb.name, period)
    return report


@router.get("", response_model=list[EvalResponse])
async def get_evaluations(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """获取评估列表"""
    result = await db.execute(select(Evaluation).order_by(Evaluation.created_at.desc()))
    evaluations = result.scalars().all()
    return [EvalResponse.model_validate(eval) for eval in evaluations]


@router.post("", response_model=EvalResponse)
async def create_evaluation(
    eval_data: EvalCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """创建评估"""
    # 使用 RAG 生成回答
    rag_result = await pipeline.run(
        query=eval_data.query,
        kb_ids=eval_data.kb_ids,
    )
    
    # 简单的评分逻辑（可以根据需要改进）
    score = 0.0
    rag_answer = rag_result.answer
    if rag_answer:
        # 基于回答长度和是否包含关键词进行简单评分
        if len(rag_answer) > 50:
            score += 0.5
        if any(keyword in rag_answer.lower() for keyword in eval_data.reference_answer.lower().split()[:5]):
            score += 0.5
    
    # 创建评估记录
    evaluation = Evaluation(
        query=eval_data.query,
        reference_answer=eval_data.reference_answer,
        rag_answer=rag_answer,
        score=min(1.0, score)
    )
    
    db.add(evaluation)
    await db.commit()
    await db.refresh(evaluation)
    
    return EvalResponse.model_validate(evaluation)


@router.delete("/{eval_id}")
async def delete_evaluation(
    eval_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """删除评估"""
    result = await db.execute(select(Evaluation).where(Evaluation.id == eval_id))
    evaluation = result.scalar_one_or_none()
    
    if not evaluation:
        raise HTTPException(status_code=404, detail="评估不存在")
    
    await db.delete(evaluation)
    await db.commit()
    
    return {"message": "评估已删除"}
