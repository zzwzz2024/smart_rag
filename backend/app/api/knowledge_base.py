"""
知识库管理 API
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.models.response_model import Response
from backend.app.database import get_db
from backend.app.models.user import User
from backend.app.models.knowledge_base import KnowledgeBase
from backend.app.models.model import Model
from backend.app.models.tag import Tag
from backend.app.models.domain import Domain
from backend.app.schemas.knowledge_base import KBCreate, KBUpdate, KBResponse
from backend.app.utils.auth import get_current_user
from backend.app.core.vector_store import VectorStore

router = APIRouter()
vector_store = VectorStore()


async def validate_model_active(db: AsyncSession, model_name: str, model_type: str) -> Optional[Model]:
    """
    验证模型是否存在且处于激活状态
    
    Args:
        db: 数据库会话
        model_name: 模型名称
        model_type: 模型类型
    
    Returns:
        Optional[Model]: 模型对象，如果模型名称为空则返回None
    
    Raises:
        HTTPException: 如果模型不存在或未激活
    """
    if not model_name:
        return None  # 空模型名称视为有效
    
    result = await db.execute(
        select(Model).where(
            Model.model == model_name,
            Model.type == model_type,
            Model.is_active == True
        )
    )
    model = result.scalar_one_or_none()
    
    if not model:
        raise HTTPException(
            status_code=400,
            detail=f"{model_type}模型 '{model_name}' 不存在或未激活"
        )
    
    return model


@router.post("/knowledge-base", response_model=Response)
async def create_kb(
    data: dict,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """创建知识库"""
    # 验证embedding模型是否有效
    embedding_model_id = data.get('embedding_model_id')
    embedding_model = None
    if embedding_model_id:
        result = await db.execute(
            select(Model).where(
                Model.id == embedding_model_id,
                Model.type == "embedding",
                Model.is_active == True
            )
        )
        embedding_model = result.scalar_one_or_none()
        if not embedding_model:
            raise HTTPException(
                status_code=400,
                detail=f"embedding模型ID '{embedding_model_id}' 不存在或未激活"
            )
    
    # 验证rerank模型是否有效
    rerank_model_id = data.get('rerank_model_id')
    rerank_model = None
    if rerank_model_id:
        result = await db.execute(
            select(Model).where(
                Model.id == rerank_model_id,
                Model.type == "rerank",
                Model.is_active == True
            )
        )
        rerank_model = result.scalar_one_or_none()
        if not rerank_model:
            raise HTTPException(
                status_code=400,
                detail=f"rerank模型ID '{rerank_model_id}' 不存在或未激活"
            )
    
    kb = KnowledgeBase(
        name=data.get('name'),
        description=data.get('description'),
        avatar=data.get('avatar') or "📚",
        embedding_model=embedding_model.model if embedding_model else "text-embedding-3-small",
        embedding_model_id=embedding_model_id,
        rerank_model=rerank_model.model if rerank_model else "",
        rerank_model_id=rerank_model_id,
        chunk_size=data.get('chunk_size') or 512,
        chunk_overlap=data.get('chunk_overlap') or 64,
        chunk_method=data.get('chunk_method') or "smart",
        retrieval_mode=data.get('retrieval_mode') or "hybrid",
        owner_id=user.id,
    )
    
    # 处理标签关联
    tag_ids = data.get('tag_ids', [])
    if tag_ids:
        tag_result = await db.execute(
            select(Tag).where(Tag.id.in_(tag_ids))
        )
        tags = tag_result.scalars().all()
        kb.tags = tags
    
    # 处理领域关联
    domain_ids = data.get('domain_ids', [])
    if domain_ids:
        domain_result = await db.execute(
            select(Domain).where(Domain.id.in_(domain_ids))
        )
        domains = domain_result.scalars().all()
        kb.domains = domains
    
    db.add(kb)
    await db.commit()
    
    # 重新查询知识库，预加载标签和领域关系
    result = await db.execute(
        select(KnowledgeBase)
        .options(
            selectinload(KnowledgeBase.tags),
            selectinload(KnowledgeBase.domains)
        )
        .where(KnowledgeBase.id == kb.id)
    )
    kb = result.scalar_one()
    
    # 构建响应数据，包括标签和领域信息
    kb_dict = {
        'id': kb.id,
        'name': kb.name,
        'description': kb.description,
        'avatar': kb.avatar,
        'embedding_model': kb.embedding_model,
        'embedding_model_id': kb.embedding_model_id,
        'rerank_model': kb.rerank_model,
        'rerank_model_id': kb.rerank_model_id,
        'chunk_size': kb.chunk_size,
        'chunk_overlap': kb.chunk_overlap,
        'chunk_method': kb.chunk_method,
        'retrieval_mode': kb.retrieval_mode,
        'doc_count': kb.doc_count,
        'chunk_count': kb.chunk_count,
        'owner_id': kb.owner_id,
        'created_at': kb.created_at,
        'updated_at': kb.updated_at,
        'tags': [{'id': tag.id, 'name': tag.name, 'color': tag.color, 'is_active': tag.is_active} for tag in kb.tags],
        'domains': [{'id': domain.id, 'name': domain.name, 'description': domain.description, 'is_active': domain.is_active} for domain in kb.domains]
    }
    
    return Response(data=kb_dict)


@router.get("/knowledge-base", response_model=Response)
async def list_kbs(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """获取知识库列表"""
    result = await db.execute(
        select(KnowledgeBase)
        .options(
            selectinload(KnowledgeBase.tags),
            selectinload(KnowledgeBase.domains)
        )
        .where(KnowledgeBase.owner_id == user.id, KnowledgeBase.is_deleted == False)
        .order_by(KnowledgeBase.updated_at.desc())
    )
    kbs = result.scalars().all()
    
    # 构建响应数据，包括标签和领域信息
    kb_list = []
    for kb in kbs:
        kb_dict = {
            'id': kb.id,
            'name': kb.name,
            'description': kb.description,
            'avatar': kb.avatar,
            'embedding_model': kb.embedding_model,
            'embedding_model_id': kb.embedding_model_id,
            'rerank_model': kb.rerank_model,
            'rerank_model_id': kb.rerank_model_id,
            'chunk_size': kb.chunk_size,
            'chunk_overlap': kb.chunk_overlap,
            'chunk_method': kb.chunk_method,
            'retrieval_mode': kb.retrieval_mode,
            'doc_count': kb.doc_count,
            'chunk_count': kb.chunk_count,
            'owner_id': kb.owner_id,
            'created_at': kb.created_at,
            'updated_at': kb.updated_at,
            'tags': [{'id': tag.id, 'name': tag.name, 'color': tag.color, 'is_active': tag.is_active} for tag in kb.tags],
            'domains': [{'id': domain.id, 'name': domain.name, 'description': domain.description, 'is_active': domain.is_active} for domain in kb.domains]
        }
        kb_list.append(kb_dict)
    
    return Response(data=kb_list)


@router.get("/knowledge-base/{kb_id}", response_model=Response)
async def get_kb(
    kb_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """获取知识库详情"""
    result = await db.execute(
        select(KnowledgeBase)
        .options(
            selectinload(KnowledgeBase.tags),
            selectinload(KnowledgeBase.domains)
        )
        .where(KnowledgeBase.id == kb_id, KnowledgeBase.is_deleted == False)
    )
    kb = result.scalar_one_or_none()
    if not kb or kb.owner_id != user.id:
        raise HTTPException(404, "知识库不存在")
    
    # 构建响应数据，包括标签和领域信息
    kb_dict = {
        'id': kb.id,
        'name': kb.name,
        'description': kb.description,
        'avatar': kb.avatar,
        'embedding_model': kb.embedding_model,
        'embedding_model_id': kb.embedding_model_id,
        'rerank_model': kb.rerank_model,
        'rerank_model_id': kb.rerank_model_id,
        'chunk_size': kb.chunk_size,
        'chunk_overlap': kb.chunk_overlap,
        'chunk_method': kb.chunk_method,
        'retrieval_mode': kb.retrieval_mode,
        'doc_count': kb.doc_count,
        'chunk_count': kb.chunk_count,
        'owner_id': kb.owner_id,
        'created_at': kb.created_at,
        'updated_at': kb.updated_at,
        'tags': [{'id': tag.id, 'name': tag.name, 'color': tag.color, 'is_active': tag.is_active} for tag in kb.tags],
        'domains': [{'id': domain.id, 'name': domain.name, 'description': domain.description, 'is_active': domain.is_active} for domain in kb.domains]
    }
    
    return Response(data=kb_dict)


@router.put("/knowledge-base/{kb_id}", response_model=Response)
async def update_kb(
    kb_id: str,
    data: dict,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """更新知识库"""
    result = await db.execute(
        select(KnowledgeBase)
        .options(
            selectinload(KnowledgeBase.tags),
            selectinload(KnowledgeBase.domains)
        )
        .where(KnowledgeBase.id == kb_id, KnowledgeBase.is_deleted == False)
    )
    kb = result.scalar_one_or_none()
    if not kb or kb.owner_id != user.id:
        raise HTTPException(404, "知识库不存在")

    # 验证embedding模型是否有效（如果提供了新值）
    if data.get('embedding_model_id') is not None:
        embedding_model_id = data.get('embedding_model_id')
        if embedding_model_id:
            result = await db.execute(
                select(Model).where(
                    Model.id == embedding_model_id,
                    Model.type == "embedding",
                    Model.is_active == True
                )
            )
            embedding_model = result.scalar_one_or_none()
            if not embedding_model:
                raise HTTPException(
                    status_code=400,
                    detail=f"embedding模型ID '{embedding_model_id}' 不存在或未激活"
                )
            data['embedding_model'] = embedding_model.model

    # 验证rerank模型是否有效（如果提供了新值）
    if data.get('rerank_model_id') is not None:
        rerank_model_id = data.get('rerank_model_id')
        if rerank_model_id:
            result = await db.execute(
                select(Model).where(
                    Model.id == rerank_model_id,
                    Model.type == "rerank",
                    Model.is_active == True
                )
            )
            rerank_model = result.scalar_one_or_none()
            if not rerank_model:
                raise HTTPException(
                    status_code=400,
                    detail=f"rerank模型ID '{rerank_model_id}' 不存在或未激活"
                )
            data['rerank_model'] = rerank_model.model

    # 处理标签和领域关联
    tag_ids = data.pop('tag_ids', None)
    domain_ids = data.pop('domain_ids', None)
    
    # 更新其他字段
    for field, value in data.items():
        if value is not None:
            setattr(kb, field, value)
    
    # 更新标签关联
    if tag_ids is not None:
        if tag_ids:
            tag_result = await db.execute(
                select(Tag).where(Tag.id.in_(tag_ids))
            )
            tags = tag_result.scalars().all()
            kb.tags = tags
        else:
            kb.tags = []
    
    # 更新领域关联
    if domain_ids is not None:
        if domain_ids:
            domain_result = await db.execute(
                select(Domain).where(Domain.id.in_(domain_ids))
            )
            domains = domain_result.scalars().all()
            kb.domains = domains
        else:
            kb.domains = []

    await db.commit()
    await db.refresh(kb)
    
    # 构建响应数据，包括标签和领域信息
    kb_dict = {
        'id': kb.id,
        'name': kb.name,
        'description': kb.description,
        'avatar': kb.avatar,
        'embedding_model': kb.embedding_model,
        'embedding_model_id': kb.embedding_model_id,
        'rerank_model': kb.rerank_model,
        'rerank_model_id': kb.rerank_model_id,
        'chunk_size': kb.chunk_size,
        'chunk_overlap': kb.chunk_overlap,
        'chunk_method': kb.chunk_method,
        'retrieval_mode': kb.retrieval_mode,
        'doc_count': kb.doc_count,
        'chunk_count': kb.chunk_count,
        'owner_id': kb.owner_id,
        'created_at': kb.created_at,
        'updated_at': kb.updated_at,
        'tags': [{'id': tag.id, 'name': tag.name, 'color': tag.color, 'is_active': tag.is_active} for tag in kb.tags],
        'domains': [{'id': domain.id, 'name': domain.name, 'description': domain.description, 'is_active': domain.is_active} for domain in kb.domains]
    }
    
    return Response(data=kb_dict)


@router.delete("/knowledge-base/{kb_id}", response_model=Response)
async def delete_kb(
    kb_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """删除知识库"""
    result = await db.execute(
        select(KnowledgeBase).where(KnowledgeBase.id == kb_id, KnowledgeBase.is_deleted == False)
    )
    kb = result.scalar_one_or_none()
    if not kb or kb.owner_id != user.id:
        raise HTTPException(404, "知识库不存在")

    # 删除向量库
    vector_store.delete_collection(kb_id)
    # 伪删除：将is_deleted字段设置为True
    kb.is_deleted = True
    await db.commit()
    return Response(data={"message": "已删除"})