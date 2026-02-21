import secrets
import string
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import List, Optional
from loguru import logger

from backend.app.models.api_authorization import ApiAuthorization, knowledge_base_authorization_association
from backend.app.models.knowledge_base import KnowledgeBase
from backend.app.schemas.api_authorization import ApiAuthorizationCreate, ApiAuthorizationUpdate
from backend.app.utils.api_utils import make_timezone_aware, make_timezone_naive, check_time_in_range, validate_time_range


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
        try:
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
            start_time = make_timezone_naive(authorization_data.start_time)
            end_time = make_timezone_naive(authorization_data.end_time)
            
            # 验证时间范围
            start_time, end_time = validate_time_range(start_time, end_time)
            
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
            logger.info(f"Created authorization for vendor {authorization_data.vendor_name} with ID {authorization.id}")
            return authorization
        except Exception as e:
            logger.error(f"Failed to create authorization: {str(e)}")
            raise
    
    @staticmethod
    async def get_authorizations(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100
    ) -> List[ApiAuthorization]:
        """获取授权列表"""
        try:
            result = await db.execute(
                select(ApiAuthorization).offset(skip).limit(limit)
            )
            authorizations = result.scalars().all()
            logger.info(f"Retrieved {len(authorizations)} authorizations with skip={skip}, limit={limit}")
            return authorizations
        except Exception as e:
            logger.error(f"Failed to get authorizations: {str(e)}")
            raise
    
    @staticmethod
    async def get_authorization_by_id(
        db: AsyncSession,
        authorization_id: str
    ) -> Optional[ApiAuthorization]:
        """根据ID获取授权"""
        try:
            result = await db.execute(
                select(ApiAuthorization).where(ApiAuthorization.id == authorization_id)
            )
            authorization = result.scalar_one_or_none()
            if authorization:
                logger.info(f"Retrieved authorization by ID {authorization_id} for vendor {authorization.vendor_name}")
            else:
                logger.info(f"Authorization not found for ID {authorization_id}")
            return authorization
        except Exception as e:
            logger.error(f"Failed to get authorization by ID {authorization_id}: {str(e)}")
            raise
    
    @staticmethod
    async def get_authorization_by_code(
        db: AsyncSession,
        auth_code: str
    ) -> Optional[ApiAuthorization]:
        """根据授权码获取授权"""
        try:
            result = await db.execute(
                select(ApiAuthorization).where(ApiAuthorization.auth_code == auth_code)
            )
            authorization = result.scalar_one_or_none()
            if authorization:
                logger.info(f"Retrieved authorization by code for vendor {authorization.vendor_name}")
            else:
                logger.info(f"Authorization not found for code {auth_code}")
            return authorization
        except Exception as e:
            logger.error(f"Failed to get authorization by code {auth_code}: {str(e)}")
            raise
    
    @staticmethod
    async def update_authorization(
        db: AsyncSession,
        authorization_id: str,
        authorization_update: ApiAuthorizationUpdate
    ) -> Optional[ApiAuthorization]:
        """更新API授权"""
        try:
            authorization = await ApiAuthorizationService.get_authorization_by_id(db, authorization_id)
            if not authorization:
                logger.info(f"Authorization not found for ID {authorization_id}")
                return None
            
            # 更新基本信息
            update_data = authorization_update.model_dump(exclude_unset=True)
            knowledge_base_ids = update_data.pop('knowledge_base_ids', None)
            
            # 处理时区问题
            if 'start_time' in update_data:
                update_data['start_time'] = make_timezone_naive(update_data['start_time'])
            if 'end_time' in update_data:
                update_data['end_time'] = make_timezone_naive(update_data['end_time'])
            
            # 验证时间范围
            if 'start_time' in update_data and 'end_time' in update_data:
                update_data['start_time'], update_data['end_time'] = validate_time_range(
                    update_data['start_time'], update_data['end_time']
                )
            
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
            logger.info(f"Updated authorization for vendor {authorization.vendor_name} with ID {authorization_id}")
            return authorization
        except Exception as e:
            logger.error(f"Failed to update authorization {authorization_id}: {str(e)}")
            raise
    
    @staticmethod
    async def delete_authorization(
        db: AsyncSession,
        authorization_id: str
    ) -> bool:
        """删除API授权"""
        try:
            result = await db.execute(
                delete(ApiAuthorization).where(ApiAuthorization.id == authorization_id)
            )
            await db.commit()
            success = result.rowcount > 0
            if success:
                logger.info(f"Deleted authorization with ID {authorization_id}")
            else:
                logger.info(f"Authorization not found for deletion: {authorization_id}")
            return success
        except Exception as e:
            logger.error(f"Failed to delete authorization {authorization_id}: {str(e)}")
            raise
    
    @staticmethod
    async def validate_authorization(
        db: AsyncSession,
        auth_code: str,
        ip_address: Optional[str] = None
    ) -> Optional[ApiAuthorization]:
        """验证授权是否有效"""
        try:
            authorization = await ApiAuthorizationService.get_authorization_by_code(db, auth_code)
            if not authorization:
                logger.info(f"Authorization not found for code {auth_code}")
                return None
            
            # 检查是否激活
            if not authorization.is_active:
                logger.info(f"Authorization {auth_code} is inactive")
                return None
            
            # 检查是否在有效期内
            now = datetime.now(timezone.utc)
            
            # 使用工具函数检查时间是否在有效期内
            if not check_time_in_range(now, authorization.start_time, authorization.end_time):
                logger.info(f"Authorization {auth_code} is expired or not yet active")
                return None
            
            # 检查IP地址是否授权
            if ip_address and authorization.authorized_ips:
                authorized_ips = [ip.strip() for ip in authorization.authorized_ips.split(',')]
                if ip_address not in authorized_ips:
                    logger.info(f"IP address {ip_address} not authorized for authorization {auth_code}")
                    return None
            
            logger.info(f"Authorization {auth_code} is valid for vendor {authorization.vendor_name}")
            return authorization
        except Exception as e:
            logger.error(f"Failed to validate authorization {auth_code}: {str(e)}")
            raise
