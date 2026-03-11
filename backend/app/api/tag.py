"""
标签API
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database import get_db
from backend.app.models.user import User
from backend.app.schemas.tag import TagCreate, TagResponse, TagUpdate
from backend.app.services.tag_service import create_tag, get_tags, get_tag, update_tag, delete_tag
from backend.app.utils.auth import get_current_user
from backend.app.models.response_model import Response

router = APIRouter()


@router.post("", response_model=Response)
async def create_tag_api(
    tag_data: TagCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """创建标签"""
    tag = await create_tag(db, tag_data)
    return Response(data=TagResponse.model_validate(tag))


@router.get("", response_model=Response)
async def get_tags_api(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """获取标签列表"""
    tags = await get_tags(db, skip, limit)
    return Response(data=[TagResponse.model_validate(tag) for tag in tags])


@router.get("/{tag_id}", response_model=Response)
async def get_tag_api(
    tag_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """获取标签详情"""
    tag = await get_tag(db, tag_id)
    if not tag:
        raise HTTPException(404, "标签不存在")
    return Response(data=TagResponse.model_validate(tag))


@router.put("/{tag_id}", response_model=Response)
async def update_tag_api(
    tag_id: str,
    tag_data: TagUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """更新标签"""
    tag = await update_tag(db, tag_id, tag_data)
    if not tag:
        raise HTTPException(404, "标签不存在")
    return Response(data=TagResponse.model_validate(tag))


@router.delete("/{tag_id}", response_model=Response)
async def delete_tag_api(
    tag_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """删除标签"""
    success = await delete_tag(db, tag_id)
    if not success:
        raise HTTPException(404, "标签不存在")
    return Response(data={"message": "标签删除成功"})
