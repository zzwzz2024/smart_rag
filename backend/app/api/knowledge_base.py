"""
知识库管理 API
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.models.response_model import Response
from backend.app.database import get_db
from backend.app.models.user import User
from backend.app.models.knowledge_base import KnowledgeBase
from backend.app.schemas.knowledge_base import KBCreate, KBUpdate, KBResponse
from backend.app.utils.auth import get_current_user
from backend.app.core.vector_store import VectorStore

router = APIRouter()
vector_store = VectorStore()


@router.post("/knowledge-base", response_model=Response)
async def create_kb(
    data: KBCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """创建知识库"""
    kb = KnowledgeBase(
        name=data.name,
        description=data.description,
        avatar=data.avatar,
        embedding_model=data.embedding_model,
        chunk_size=data.chunk_size,
        chunk_overlap=data.chunk_overlap,
        retrieval_mode=data.retrieval_mode,
        owner_id=user.id,
    )
    db.add(kb)
    await db.flush()
    # return KBResponse.model_validate(kb)
    return Response(
        data=KBResponse.model_validate(kb)
    )


@router.get("/knowledge-base", response_model=Response)
async def list_kbs(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """获取知识库列表"""
    result = await db.execute(
        select(KnowledgeBase)
        .where(KnowledgeBase.owner_id == user.id)
        .order_by(KnowledgeBase.updated_at.desc())
    )
    kbs = result.scalars().all()
    # return [KBResponse.model_validate(kb) for kb in kbs]
    return Response(
        data=[KBResponse.model_validate(kb) for kb in kbs]
    )


@router.get("/knowledge-base/{kb_id}", response_model=KBResponse)
async def get_kb(
    kb_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """获取知识库详情"""
    result = await db.execute(
        select(KnowledgeBase).where(KnowledgeBase.id == kb_id)
    )
    kb = result.scalar_one_or_none()
    if not kb or kb.owner_id != user.id:
        raise HTTPException(404, "知识库不存在")
    return KBResponse.model_validate(kb)


@router.put("/knowledge-base/{kb_id}", response_model=KBResponse)
async def update_kb(
    kb_id: str,
    data: KBUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """更新知识库"""
    result = await db.execute(
        select(KnowledgeBase).where(KnowledgeBase.id == kb_id)
    )
    kb = result.scalar_one_or_none()
    if not kb or kb.owner_id != user.id:
        raise HTTPException(404, "知识库不存在")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(kb, field, value)

    await db.flush()
    return KBResponse.model_validate(kb)


@router.delete("/knowledge-base/{kb_id}")
async def delete_kb(
    kb_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """删除知识库"""
    result = await db.execute(
        select(KnowledgeBase).where(KnowledgeBase.id == kb_id)
    )
    kb = result.scalar_one_or_none()
    if not kb or kb.owner_id != user.id:
        raise HTTPException(404, "知识库不存在")

    # 删除向量库
    vector_store.delete_collection(kb_id)
    # 级联删除（ORM 配置了 cascade）
    await db.delete(kb)
    return {"message": "已删除"}