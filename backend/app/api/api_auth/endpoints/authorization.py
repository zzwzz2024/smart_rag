"""
API授权管理接口
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger
from backend.app.database import get_db
from backend.app.models.user import User
from backend.app.schemas.api_authorization import (
    ApiAuthorizationCreate,
    ApiAuthorizationUpdate,
    ApiAuthorizationResponse
)
from backend.app.services.api_authorization_service import ApiAuthorizationService
from backend.app.utils.auth import get_current_user
from backend.app.utils.api_authorization_utils import (
    get_knowledge_bases_by_ids,
    get_knowledge_bases_map_by_authorization_ids,
    get_knowledge_bases_by_authorization_id,
    build_authorization_response,
    build_knowledge_bases_info
)
from backend.app.models.response_model import Response


router = APIRouter()


@router.post("/create", response_model=Response)
async def create_authorization(
    authorization_data: ApiAuthorizationCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """创建API授权"""
    try:
        authorization = await ApiAuthorizationService.create_authorization(
            db, authorization_data
        )
        
        # 单独查询知识库信息，避免延迟加载
        knowledge_base_ids, knowledge_base_names = await get_knowledge_bases_by_ids(
            db, authorization_data.knowledge_base_ids
        )
        
        # 构建响应数据
        response_data = build_authorization_response(
            authorization, knowledge_base_ids, knowledge_base_names
        )
        
        return Response(data=response_data)
    except Exception as e:
        logger.error(f"创建授权失败: {str(e)}")
        raise HTTPException(status_code=400, detail="创建授权失败，请检查输入信息")


@router.get("/list", response_model=Response)
async def get_authorizations(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """获取授权列表"""
    try:
        authorizations = await ApiAuthorizationService.get_authorizations(
            db, skip=skip, limit=limit
        )
        
        # 批量查询所有授权的知识库关联
        authorization_ids = [auth.id for auth in authorizations]
        knowledge_base_map = await get_knowledge_bases_map_by_authorization_ids(
            db, authorization_ids
        )
        
        # 构建响应数据
        response_data = []
        for authorization in authorizations:
            kb_info = knowledge_base_map.get(authorization.id, {"ids": [], "names": []})
            response_data.append(build_authorization_response(
                authorization, kb_info["ids"], kb_info["names"]
            ))
        
        return Response(data=response_data)
    except Exception as e:
        logger.error(f"获取授权列表失败: {str(e)}")
        raise HTTPException(status_code=400, detail="获取授权列表失败")


@router.get("/{authorization_id}", response_model=Response)
async def get_authorization(
    authorization_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """获取授权详情"""
    try:
        authorization = await ApiAuthorizationService.get_authorization_by_id(
            db, authorization_id
        )
        if not authorization:
            raise HTTPException(status_code=404, detail="授权不存在")
        
        # 单独查询知识库信息
        knowledge_base_ids, knowledge_base_names = await get_knowledge_bases_by_authorization_id(
            db, authorization_id
        )
        
        # 构建响应数据
        response_data = build_authorization_response(
            authorization, knowledge_base_ids, knowledge_base_names
        )
        
        return Response(data=response_data)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取授权详情失败: {str(e)}")
        raise HTTPException(status_code=400, detail="获取授权详情失败")


@router.put("/{authorization_id}", response_model=Response)
async def update_authorization(
    authorization_id: str,
    authorization_update: ApiAuthorizationUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """更新API授权"""
    try:
        authorization = await ApiAuthorizationService.update_authorization(
            db, authorization_id, authorization_update
        )
        if not authorization:
            raise HTTPException(status_code=404, detail="授权不存在")
        
        # 单独查询知识库信息
        knowledge_base_ids, knowledge_base_names = await get_knowledge_bases_by_authorization_id(
            db, authorization_id
        )
        
        # 构建响应数据
        response_data = build_authorization_response(
            authorization, knowledge_base_ids, knowledge_base_names
        )
        
        return Response(data=response_data)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新授权失败: {str(e)}")
        raise HTTPException(status_code=400, detail="更新授权失败，请检查输入信息")


@router.delete("/{authorization_id}", response_model=Response)
async def delete_authorization(
    authorization_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """删除API授权"""
    try:
        success = await ApiAuthorizationService.delete_authorization(
            db, authorization_id
        )
        if not success:
            raise HTTPException(status_code=404, detail="授权不存在")
        
        return Response(data={"message": "授权已删除"})
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除授权失败: {str(e)}")
        raise HTTPException(status_code=400, detail="删除授权失败")


@router.get("/validate/{auth_code}", response_model=Response)
async def validate_authorization(
    auth_code: str,
    ip: str = None,
    db: AsyncSession = Depends(get_db),
):
    """验证授权是否有效"""
    try:
        authorization = await ApiAuthorizationService.validate_authorization(
            db, auth_code, ip
        )
        if not authorization:
            return Response(data={"valid": False, "message": "授权无效或已过期"})
        
        # 单独查询知识库信息
        knowledge_base_ids, knowledge_base_names = await get_knowledge_bases_by_authorization_id(
            db, authorization.id
        )
        
        knowledge_bases = build_knowledge_bases_info(
            knowledge_base_ids, knowledge_base_names
        )
        
        return Response(data={
            "valid": True,
            "message": "授权有效",
            "authorization": {
                "vendor_name": authorization.vendor_name,
                "knowledge_bases": knowledge_bases,
                "expires_at": authorization.end_time
            }
        })
    except Exception as e:
        logger.error(f"验证授权失败: {str(e)}")
        return Response(data={"valid": False, "message": "验证失败"})
