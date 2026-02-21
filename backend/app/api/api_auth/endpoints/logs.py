"""
API日志管理接口
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger
from backend.app.database import get_db
from backend.app.models.user import User
from backend.app.services.api_log_service import ApiLogService
from backend.app.utils.auth import get_current_user
from backend.app.models.response_model import Response
from backend.app.config import get_settings
from backend.app.schemas.api import ApiLogQuery, ApiLogStatsQuery
from backend.app.utils.api_utils import format_response_time


router = APIRouter()
settings = get_settings()


# 重写模型以使用配置中的默认值
class ApiLogQueryWithDefaults(ApiLogQuery):
    """API日志查询模型（带默认值）"""
    limit: int = settings.DEFAULT_PAGE_SIZE  # 从配置中获取默认值


class ApiLogStatsQueryWithDefaults(ApiLogStatsQuery):
    """API日志统计查询模型（保持默认值）"""
    pass


@router.post("/list", response_model=Response)
async def get_api_logs(
    query: ApiLogQueryWithDefaults,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """获取API访问日志列表"""
    try:
        logs = await ApiLogService.get_logs(
            db, 
            skip=query.skip, 
            limit=min(query.limit, settings.MAX_PAGE_SIZE),  # 限制最大页面大小
            auth_code=query.auth_code,
            start_date=query.start_date,
            end_date=query.end_date,
            vendor=query.vendor
        )
        
        total = await ApiLogService.get_log_count(
            db, 
            auth_code=query.auth_code,
            start_date=query.start_date,
            end_date=query.end_date,
            vendor=query.vendor
        )
        
        # 构建响应数据
        log_data = []
        for log in logs:
            log_data.append({
                "id": log.id,
                "auth_code": log.auth_code,
                "endpoint": log.endpoint,
                "method": log.method,
                "ip": log.ip,
                "status": log.status,
                "response_time": log.response_time,
                "formatted_response_time": format_response_time(log.response_time),  # 格式化响应时间
                "error_message": log.error_message,
                "created_at": log.created_at
            })
        
        return Response(data={
            "logs": log_data,
            "total": total
        })
    except Exception as e:
        logger.error(f"获取日志失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取日志失败")


@router.post("/stats", response_model=Response)
async def get_api_log_stats(
    query: ApiLogStatsQueryWithDefaults,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """获取API访问统计数据"""
    try:
        stats = await ApiLogService.get_access_stats(
            db, 
            days=query.days,
            auth_code=query.auth_code,
            start_date=query.start_date,
            end_date=query.end_date,
            vendor=query.vendor
        )
        
        return Response(data={"stats": stats})
    except Exception as e:
        logger.error(f"获取日志统计失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取日志统计失败")


@router.post("/vendor-stats", response_model=Response)
async def get_api_log_vendor_stats(
    query: ApiLogStatsQueryWithDefaults,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """获取API访问厂商统计数据"""
    try:
        stats = await ApiLogService.get_vendor_stats(
            db, 
            days=query.days,
            start_date=query.start_date,
            end_date=query.end_date
        )
        
        return Response(data={"stats": stats})
    except Exception as e:
        logger.error(f"获取厂商统计失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取厂商统计失败")


@router.post("/endpoint-stats", response_model=Response)
async def get_api_log_endpoint_stats(
    query: ApiLogStatsQueryWithDefaults,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """获取API访问接口名统计数据"""
    try:
        stats = await ApiLogService.get_endpoint_stats(
            db, 
            days=query.days,
            start_date=query.start_date,
            end_date=query.end_date
        )
        
        return Response(data={"stats": stats})
    except Exception as e:
        logger.error(f"获取接口名统计失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取接口名统计失败")
