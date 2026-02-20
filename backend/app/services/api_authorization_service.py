import secrets
import string
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import List, Optional

from backend.app.models.api_authorization import ApiAuthorization, knowledge_base_authorization_association
from backend.app.models.knowledge_base import KnowledgeBase
from backend.app.schemas.api_authorization import ApiAuthorizationCreate, ApiAuthorizationUpdate


def generate_auth_code(length: int = 32) -> str:
    """生成授权码"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


class ApiAuthorizationService:
    """API授权服务"""
    
    @staticmethod
    async def create_authorization(
        db: AsyncSession,
        authorization_data: ApiAuthorizationCreate
    ) -> ApiAuthorization:
        """创建API授权"""
        # 生成唯一授权码
        auth_code = generate_auth_code()
        
        # 检查授权码是否已存在
        while True:
            existing = await db.execute(
                select(ApiAuthorization).where(ApiAuthorization.auth_code == auth_code)
            )
            if not existing.scalar_one_or_none():
                break
            auth_code = generate_auth_code()
        
        # 转换时区感知的datetime为时区-naive
        start_time = authorization_data.start_time
        end_time = authorization_data.end_time
        
        if start_time and hasattr(start_time, 'replace'):
            start_time = start_time.replace(tzinfo=None)
        if end_time and hasattr(end_time, 'replace'):
            end_time = end_time.replace(tzinfo=None)
        
        # 创建授权记录
        authorization = ApiAuthorization(
            vendor_name=authorization_data.vendor_name,
            vendor_contact=authorization_data.vendor_contact,
            contact_phone=authorization_data.contact_phone,
            authorized_ips=authorization_data.authorized_ips,
            auth_code=auth_code,
            start_time=start_time,
            end_time=end_time
        )
        
        # 添加授权的知识库
        if authorization_data.knowledge_base_ids:
            knowledge_bases = await db.execute(
                select(KnowledgeBase).where(
                    KnowledgeBase.id.in_(authorization_data.knowledge_base_ids)
                )
            )
            authorization.knowledge_bases = knowledge_bases.scalars().all()
        
        db.add(authorization)
        await db.commit()
        await db.refresh(authorization)
        return authorization
    
    @staticmethod
    async def get_authorizations(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100
    ) -> List[ApiAuthorization]:
        """获取授权列表"""
        result = await db.execute(
            select(ApiAuthorization).offset(skip).limit(limit)
        )
        return result.scalars().all()
    
    @staticmethod
    async def get_authorization_by_id(
        db: AsyncSession,
        authorization_id: str
    ) -> Optional[ApiAuthorization]:
        """根据ID获取授权"""
        result = await db.execute(
            select(ApiAuthorization).where(ApiAuthorization.id == authorization_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_authorization_by_code(
        db: AsyncSession,
        auth_code: str
    ) -> Optional[ApiAuthorization]:
        """根据授权码获取授权"""
        result = await db.execute(
            select(ApiAuthorization).where(ApiAuthorization.auth_code == auth_code)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def update_authorization(
        db: AsyncSession,
        authorization_id: str,
        authorization_update: ApiAuthorizationUpdate
    ) -> Optional[ApiAuthorization]:
        """更新API授权"""
        authorization = await ApiAuthorizationService.get_authorization_by_id(db, authorization_id)
        if not authorization:
            return None
        
        # 更新基本信息
        update_data = authorization_update.model_dump(exclude_unset=True)
        knowledge_base_ids = update_data.pop('knowledge_base_ids', None)
        
        # 处理时区问题
        if 'start_time' in update_data and update_data['start_time'] and hasattr(update_data['start_time'], 'replace'):
            update_data['start_time'] = update_data['start_time'].replace(tzinfo=None)
        if 'end_time' in update_data and update_data['end_time'] and hasattr(update_data['end_time'], 'replace'):
            update_data['end_time'] = update_data['end_time'].replace(tzinfo=None)
        
        for field, value in update_data.items():
            setattr(authorization, field, value)
        
        # 更新授权的知识库
        if knowledge_base_ids is not None:
            # 删除现有的关联
            await db.execute(
                delete(knowledge_base_authorization_association).where(
                    knowledge_base_authorization_association.c.authorization_id == authorization.id
                )
            )
            
            # 添加新的关联
            for knowledge_base_id in knowledge_base_ids:
                await db.execute(
                    knowledge_base_authorization_association.insert().values(
                        authorization_id=authorization.id,
                        knowledge_base_id=knowledge_base_id
                    )
                )
        
        await db.commit()
        await db.refresh(authorization)
        return authorization
    
    @staticmethod
    async def delete_authorization(
        db: AsyncSession,
        authorization_id: str
    ) -> bool:
        """删除API授权"""
        result = await db.execute(
            delete(ApiAuthorization).where(ApiAuthorization.id == authorization_id)
        )
        await db.commit()
        return result.rowcount > 0
    
    @staticmethod
    async def validate_authorization(
        db: AsyncSession,
        auth_code: str,
        ip_address: Optional[str] = None
    ) -> Optional[ApiAuthorization]:
        """验证授权是否有效"""
        authorization = await ApiAuthorizationService.get_authorization_by_code(db, auth_code)
        if not authorization:
            return None
        
        # 检查是否激活
        if not authorization.is_active:
            return None
        
        # 检查是否在有效期内
        now = datetime.now(timezone.utc)
        # 确保比较的时间都是有时区的
        if authorization.start_time.tzinfo is None:
            start_time = authorization.start_time.replace(tzinfo=timezone.utc)
        else:
            start_time = authorization.start_time
        
        if authorization.end_time.tzinfo is None:
            end_time = authorization.end_time.replace(tzinfo=timezone.utc)
        else:
            end_time = authorization.end_time
        
        if now < start_time or now > end_time:
            return None
        
        # 检查IP地址是否授权
        if ip_address and authorization.authorized_ips:
            authorized_ips = [ip.strip() for ip in authorization.authorized_ips.split(',')]
            if ip_address not in authorized_ips:
                return None
        
        return authorization
