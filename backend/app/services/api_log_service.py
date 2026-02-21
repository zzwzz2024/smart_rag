from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.sql import label
from datetime import datetime, timedelta

from backend.app.models.api_log import ApiLog


class ApiLogService:
    """API日志服务"""
    
    @staticmethod
    async def create_log(
        db: AsyncSession,
        auth_code: str,
        endpoint: str,
        method: str,
        ip: str,
        status: int,
        response_time: float,
        user_agent: Optional[str] = None,
        error_message: Optional[str] = None
    ) -> ApiLog:
        """创建API访问日志"""
        log = ApiLog(
            auth_code=auth_code,
            endpoint=endpoint,
            method=method,
            ip=ip,
            status=status,
            response_time=int(response_time * 1000),  # 转换为毫秒
            user_agent=user_agent,
            error_message=error_message
        )
        db.add(log)
        await db.commit()
        await db.refresh(log)
        return log
    
    @staticmethod
    async def get_logs(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        auth_code: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        vendor: Optional[str] = None
    ) -> List[ApiLog]:
        """获取日志列表"""
        from sqlalchemy import and_, or_
        from backend.app.models.api_authorization import ApiAuthorization
        
        # 基础查询
        if vendor:
            # 如果指定了厂商，需要关联查询
            query = select(ApiLog).join(
                ApiAuthorization,
                ApiLog.auth_code == ApiAuthorization.auth_code
            ).where(
                ApiAuthorization.vendor_name == vendor
            )
        else:
            query = select(ApiLog)
        
        # 添加其他查询条件
        if auth_code:
            query = query.where(ApiLog.auth_code == auth_code)
        
        if start_date:
            # 将字符串转换为datetime对象
            from datetime import datetime
            start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
            query = query.where(ApiLog.created_at >= start_datetime)
        
        if end_date:
            # 结束日期需要包含当天的所有时间
            from datetime import datetime, timedelta
            end_datetime = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1) - timedelta(seconds=1)
            query = query.where(ApiLog.created_at <= end_datetime)
        
        result = await db.execute(
            query.order_by(ApiLog.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    @staticmethod
    async def get_log_count(
        db: AsyncSession,
        auth_code: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        vendor: Optional[str] = None
    ) -> int:
        """获取日志总数"""
        from sqlalchemy import func
        from backend.app.models.api_authorization import ApiAuthorization
        
        # 基础查询
        if vendor:
            # 如果指定了厂商，需要关联查询
            query = select(func.count(ApiLog.id)).join(
                ApiAuthorization,
                ApiLog.auth_code == ApiAuthorization.auth_code
            ).where(
                ApiAuthorization.vendor_name == vendor
            )
        else:
            query = select(func.count(ApiLog.id))
        
        # 添加其他查询条件
        if auth_code:
            query = query.where(ApiLog.auth_code == auth_code)
        
        if start_date:
            # 将字符串转换为datetime对象
            from datetime import datetime
            start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
            query = query.where(ApiLog.created_at >= start_datetime)
        
        if end_date:
            # 结束日期需要包含当天的所有时间
            from datetime import datetime, timedelta
            end_datetime = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1) - timedelta(seconds=1)
            query = query.where(ApiLog.created_at <= end_datetime)
        
        result = await db.execute(query)
        return result.scalar() or 0
    
    @staticmethod
    async def get_access_stats(
        db: AsyncSession,
        days: int = 7,
        auth_code: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        vendor: Optional[str] = None
    ) -> List[dict]:
        """获取访问统计数据"""
        from sqlalchemy import func
        from sqlalchemy.sql import label
        from backend.app.models.api_authorization import ApiAuthorization
        
        # 确定开始日期
        if start_date:
            from datetime import datetime
            start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
        else:
            from datetime import datetime, timedelta
            start_datetime = datetime.utcnow() - timedelta(days=days)
        
        # 基础查询
        if vendor:
            # 如果指定了厂商，需要关联查询
            query = select(
                label('date', func.date(ApiLog.created_at)),
                label('count', func.count(ApiLog.id))
            ).join(
                ApiAuthorization,
                ApiLog.auth_code == ApiAuthorization.auth_code
            ).where(
                and_(
                    ApiLog.created_at >= start_datetime,
                    ApiAuthorization.vendor_name == vendor
                )
            )
        else:
            query = select(
                label('date', func.date(ApiLog.created_at)),
                label('count', func.count(ApiLog.id))
            ).where(
                ApiLog.created_at >= start_datetime
            )
        
        # 添加其他查询条件
        if auth_code:
            query = query.where(ApiLog.auth_code == auth_code)
        
        if end_date:
            # 结束日期需要包含当天的所有时间
            from datetime import datetime, timedelta
            end_datetime = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1) - timedelta(seconds=1)
            query = query.where(ApiLog.created_at <= end_datetime)
        
        result = await db.execute(
            query.group_by(func.date(ApiLog.created_at))
            .order_by(func.date(ApiLog.created_at))
        )
        
        stats = []
        for date, count in result.all():
            stats.append({
                'date': date.strftime('%Y-%m-%d'),
                'count': count
            })
        
        return stats
    
    @staticmethod
    async def get_vendor_stats(
        db: AsyncSession,
        days: int = 7,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[dict]:
        """获取按厂商统计的访问数据"""
        from sqlalchemy import func
        from sqlalchemy.sql import label
        from backend.app.models.api_authorization import ApiAuthorization
        
        # 确定开始日期
        if start_date:
            from datetime import datetime
            start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
        else:
            from datetime import datetime, timedelta
            start_datetime = datetime.utcnow() - timedelta(days=days)
        
        # 构建查询
        query = select(
            label('vendor', ApiAuthorization.vendor_name),
            label('count', func.count(ApiLog.id))
        ).join(
            ApiAuthorization,
            ApiLog.auth_code == ApiAuthorization.auth_code
        ).where(
            ApiLog.created_at >= start_datetime
        )
        
        if end_date:
            # 结束日期需要包含当天的所有时间
            from datetime import datetime, timedelta
            end_datetime = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1) - timedelta(seconds=1)
            query = query.where(ApiLog.created_at <= end_datetime)
        
        result = await db.execute(
            query.group_by(ApiAuthorization.vendor_name)
            .order_by(func.count(ApiLog.id).desc())
        )
        
        stats = []
        for vendor, count in result.all():
            stats.append({
                'vendor': vendor,
                'count': count
            })
        
        return stats
    
    @staticmethod
    async def get_endpoint_stats(
        db: AsyncSession,
        days: int = 7,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[dict]:
        """获取按接口名统计的访问数据"""
        from sqlalchemy import func
        from sqlalchemy.sql import label
        
        # 确定开始日期
        if start_date:
            from datetime import datetime
            start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
        else:
            from datetime import datetime, timedelta
            start_datetime = datetime.utcnow() - timedelta(days=days)
        
        # 构建查询
        query = select(
            label('endpoint', ApiLog.endpoint),
            label('count', func.count(ApiLog.id))
        ).where(
            ApiLog.created_at >= start_datetime
        )
        
        if end_date:
            # 结束日期需要包含当天的所有时间
            from datetime import datetime, timedelta
            end_datetime = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1) - timedelta(seconds=1)
            query = query.where(ApiLog.created_at <= end_datetime)
        
        result = await db.execute(
            query.group_by(ApiLog.endpoint)
            .order_by(func.count(ApiLog.id).desc())
        )
        
        stats = []
        for endpoint, count in result.all():
            stats.append({
                'endpoint': endpoint,
                'count': count
            })
        
        return stats
