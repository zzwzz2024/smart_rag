"""
领域服务
"""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from loguru import logger

from backend.app.models.domain import Domain
from backend.app.schemas.domain import DomainCreate, DomainUpdate


async def create_domain(db: AsyncSession, domain_data: DomainCreate) -> Domain:
    """创建领域"""
    try:
        domain = Domain(**domain_data.model_dump())
        db.add(domain)
        await db.commit()
        await db.refresh(domain)
        logger.info(f"Created domain: {domain.name}")
        return domain
    except Exception as e:
        logger.error(f"Failed to create domain: {e}")
        await db.rollback()
        raise


async def get_domains(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Domain]:
    """获取领域列表"""
    try:
        result = await db.execute(
            select(Domain).where(Domain.is_deleted == False).order_by(Domain.created_at.desc()).offset(skip).limit(limit)
        )
        domains = result.scalars().all()
        return domains
    except Exception as e:
        logger.error(f"Failed to get domains: {e}")
        raise


async def get_domain(db: AsyncSession, domain_id: str) -> Optional[Domain]:
    """获取领域详情"""
    try:
        result = await db.execute(
            select(Domain).where(Domain.id == domain_id, Domain.is_deleted == False)
        )
        domain = result.scalar_one_or_none()
        return domain
    except Exception as e:
        logger.error(f"Failed to get domain: {e}")
        raise


async def update_domain(db: AsyncSession, domain_id: str, domain_data: DomainUpdate) -> Optional[Domain]:
    """更新领域"""
    try:
        result = await db.execute(
            select(Domain).where(Domain.id == domain_id, Domain.is_deleted == False)
        )
        domain = result.scalar_one_or_none()
        if not domain:
            return None
        
        update_data = domain_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(domain, field, value)
        
        await db.commit()
        await db.refresh(domain)
        logger.info(f"Updated domain: {domain.name}")
        return domain
    except Exception as e:
        logger.error(f"Failed to update domain: {e}")
        await db.rollback()
        raise


async def delete_domain(db: AsyncSession, domain_id: str) -> bool:
    """删除领域"""
    try:
        result = await db.execute(
            select(Domain).where(Domain.id == domain_id, Domain.is_deleted == False)
        )
        domain = result.scalar_one_or_none()
        if not domain:
            return False
        
        # 伪删除：将is_deleted字段设置为True
        domain.is_deleted = True
        await db.commit()
        logger.info(f"Deleted domain: {domain.name}")
        return True
    except Exception as e:
        logger.error(f"Failed to delete domain: {e}")
        await db.rollback()
        raise
