"""
API授权相关工具函数
"""
from typing import Dict, List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, join
from loguru import logger

from backend.app.models.api_authorization import ApiAuthorization, knowledge_base_authorization_association
from backend.app.models.knowledge_base import KnowledgeBase
from backend.app.schemas.api_authorization import ApiAuthorizationResponse


async def get_knowledge_bases_by_authorization_id(
    db: AsyncSession, authorization_id: str
) -> Tuple[List[str], List[str]]:
    """
    根据授权ID获取知识库信息
    
    Args:
        db: 数据库会话
        authorization_id: 授权ID
    
    Returns:
        Tuple[List[str], List[str]]: (知识库ID列表, 知识库名称列表)
    """
    try:
        result = await db.execute(
            select(
                KnowledgeBase.id,
                KnowledgeBase.name
            ).select_from(
                join(
                    knowledge_base_authorization_association,
                    KnowledgeBase,
                    knowledge_base_authorization_association.c.knowledge_base_id == KnowledgeBase.id
                )
            ).where(
                knowledge_base_authorization_association.c.authorization_id == authorization_id
            )
        )
        
        knowledge_base_ids = []
        knowledge_base_names = []
        for kb_id, kb_name in result.all():
            knowledge_base_ids.append(kb_id)
            knowledge_base_names.append(kb_name)
        
        return knowledge_base_ids, knowledge_base_names
    except Exception as e:
        logger.error(f"获取知识库信息失败: {str(e)}")
        return [], []


async def get_knowledge_bases_map_by_authorization_ids(
    db: AsyncSession, authorization_ids: List[str]
) -> Dict[str, Dict[str, List[str]]]:
    """
    批量获取多个授权的知识库信息
    
    Args:
        db: 数据库会话
        authorization_ids: 授权ID列表
    
    Returns:
        Dict[str, Dict[str, List[str]]]: 授权ID到知识库信息的映射
    """
    try:
        knowledge_base_map = {}
        
        if not authorization_ids:
            return knowledge_base_map
        
        result = await db.execute(
            select(
                knowledge_base_authorization_association.c.authorization_id,
                KnowledgeBase.id,
                KnowledgeBase.name
            ).select_from(
                join(
                    knowledge_base_authorization_association,
                    KnowledgeBase,
                    knowledge_base_authorization_association.c.knowledge_base_id == KnowledgeBase.id
                )
            ).where(
                knowledge_base_authorization_association.c.authorization_id.in_(authorization_ids)
            )
        )
        
        # 构建映射
        for auth_id, kb_id, kb_name in result.all():
            if auth_id not in knowledge_base_map:
                knowledge_base_map[auth_id] = {"ids": [], "names": []}
            knowledge_base_map[auth_id]["ids"].append(kb_id)
            knowledge_base_map[auth_id]["names"].append(kb_name)
        
        return knowledge_base_map
    except Exception as e:
        logger.error(f"批量获取知识库信息失败: {str(e)}")
        return {}


async def get_knowledge_bases_by_ids(
    db: AsyncSession, knowledge_base_ids: List[str]
) -> Tuple[List[str], List[str]]:
    """
    根据知识库ID列表获取知识库信息
    
    Args:
        db: 数据库会话
        knowledge_base_ids: 知识库ID列表
    
    Returns:
        Tuple[List[str], List[str]]: (知识库ID列表, 知识库名称列表)
    """
    try:
        knowledge_base_ids_list = []
        knowledge_base_names_list = []
        
        if not knowledge_base_ids:
            return knowledge_base_ids_list, knowledge_base_names_list
        
        result = await db.execute(
            select(KnowledgeBase).where(
                KnowledgeBase.id.in_(knowledge_base_ids)
            )
        )
        
        knowledge_bases = result.scalars().all()
        knowledge_base_ids_list = [kb.id for kb in knowledge_bases]
        knowledge_base_names_list = [kb.name for kb in knowledge_bases]
        
        return knowledge_base_ids_list, knowledge_base_names_list
    except Exception as e:
        logger.error(f"根据ID列表获取知识库信息失败: {str(e)}")
        return [], []


def build_authorization_response(
    authorization: ApiAuthorization,
    knowledge_base_ids: List[str],
    knowledge_base_names: List[str]
) -> ApiAuthorizationResponse:
    """
    构建授权响应数据
    
    Args:
        authorization: 授权对象
        knowledge_base_ids: 知识库ID列表
        knowledge_base_names: 知识库名称列表
    
    Returns:
        ApiAuthorizationResponse: 授权响应数据
    """
    return ApiAuthorizationResponse(
        id=authorization.id,
        vendor_name=authorization.vendor_name,
        vendor_contact=authorization.vendor_contact,
        contact_phone=authorization.contact_phone,
        authorized_ips=authorization.authorized_ips,
        auth_code=authorization.auth_code,
        start_time=authorization.start_time,
        end_time=authorization.end_time,
        is_active=authorization.is_active,
        created_at=authorization.created_at,
        updated_at=authorization.updated_at,
        knowledge_base_ids=knowledge_base_ids,
        knowledge_base_names=knowledge_base_names
    )


def build_knowledge_bases_info(
    knowledge_base_ids: List[str],
    knowledge_base_names: List[str]
) -> List[Dict[str, str]]:
    """
    构建知识库信息列表
    
    Args:
        knowledge_base_ids: 知识库ID列表
        knowledge_base_names: 知识库名称列表
    
    Returns:
        List[Dict[str, str]]: 知识库信息列表
    """
    knowledge_bases = []
    for kb_id, kb_name in zip(knowledge_base_ids, knowledge_base_names):
        knowledge_bases.append({"id": kb_id, "name": kb_name})
    return knowledge_bases
