"""
领域API
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database import get_db
from backend.app.models.user import User
from backend.app.schemas.domain import DomainCreate, DomainResponse, DomainUpdate
from backend.app.services.domain_service import create_domain, get_domains, get_domain, update_domain, delete_domain
from backend.app.utils.auth import get_current_user
from backend.app.models.response_model import Response

router = APIRouter()


@router.post("", response_model=Response)
async def create_domain_api(
    domain_data: DomainCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """创建领域"""
    domain = await create_domain(db, domain_data)
    return Response(data=DomainResponse.model_validate(domain))


@router.get("", response_model=Response)
async def get_domains_api(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """获取领域列表"""
    domains = await get_domains(db, skip, limit)
    return Response(data=[DomainResponse.model_validate(domain) for domain in domains])


@router.get("/{domain_id}", response_model=Response)
async def get_domain_api(
    domain_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """获取领域详情"""
    domain = await get_domain(db, domain_id)
    if not domain:
        raise HTTPException(404, "领域不存在")
    return Response(data=DomainResponse.model_validate(domain))


@router.put("/{domain_id}", response_model=Response)
async def update_domain_api(
    domain_id: str,
    domain_data: DomainUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """更新领域"""
    domain = await update_domain(db, domain_id, domain_data)
    if not domain:
        raise HTTPException(404, "领域不存在")
    return Response(data=DomainResponse.model_validate(domain))


@router.delete("/{domain_id}", response_model=Response)
async def delete_domain_api(
    domain_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """删除领域"""
    success = await delete_domain(db, domain_id)
    if not success:
        raise HTTPException(404, "领域不存在")
    return Response(data={"message": "领域删除成功"})
