"""
标签服务
"""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from loguru import logger

from backend.app.models.tag import Tag
from backend.app.schemas.tag import TagCreate, TagUpdate


async def create_tag(db: AsyncSession, tag_data: TagCreate) -> Tag:
    """创建标签"""
    try:
        tag = Tag(**tag_data.model_dump())
        db.add(tag)
        await db.commit()
        await db.refresh(tag)
        logger.info(f"Created tag: {tag.name}")
        return tag
    except Exception as e:
        logger.error(f"Failed to create tag: {e}")
        await db.rollback()
        raise


async def get_tags(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Tag]:
    """获取标签列表"""
    try:
        result = await db.execute(
            select(Tag).offset(skip).limit(limit)
        )
        tags = result.scalars().all()
        return tags
    except Exception as e:
        logger.error(f"Failed to get tags: {e}")
        raise


async def get_tag(db: AsyncSession, tag_id: str) -> Optional[Tag]:
    """获取标签详情"""
    try:
        result = await db.execute(
            select(Tag).where(Tag.id == tag_id)
        )
        tag = result.scalar_one_or_none()
        return tag
    except Exception as e:
        logger.error(f"Failed to get tag: {e}")
        raise


async def update_tag(db: AsyncSession, tag_id: str, tag_data: TagUpdate) -> Optional[Tag]:
    """更新标签"""
    try:
        result = await db.execute(
            select(Tag).where(Tag.id == tag_id)
        )
        tag = result.scalar_one_or_none()
        if not tag:
            return None
        
        update_data = tag_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(tag, field, value)
        
        await db.commit()
        await db.refresh(tag)
        logger.info(f"Updated tag: {tag.name}")
        return tag
    except Exception as e:
        logger.error(f"Failed to update tag: {e}")
        await db.rollback()
        raise


async def delete_tag(db: AsyncSession, tag_id: str) -> bool:
    """删除标签"""
    try:
        result = await db.execute(
            select(Tag).where(Tag.id == tag_id)
        )
        tag = result.scalar_one_or_none()
        if not tag:
            return False
        
        await db.delete(tag)
        await db.commit()
        logger.info(f"Deleted tag: {tag.name}")
        return True
    except Exception as e:
        logger.error(f"Failed to delete tag: {e}")
        await db.rollback()
        raise
