"""模型工具函数"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.models.model import Model
from loguru import logger


async def get_default_model(db: AsyncSession, model_type: str) -> Model:
    """
    从数据库获取指定类型的默认模型
    
    Args:
        db: 数据库会话
        model_type: 模型类型，如 'embedding', 'chat', 'rerank'
    
    Returns:
        Model: 默认模型对象，如果没有找到则返回 None
    """
    try:
        result = await db.execute(
            select(Model).where(
                Model.type == model_type,
                Model.is_default == True,
                Model.is_active == True
            ).limit(1)
        )
        model = result.scalar_one_or_none()
        
        if model:
            logger.info(f"从数据库获取默认 {model_type} 模型：{model.name}")
        else:
            # 如果没有默认模型，尝试获取任何激活的模型
            result = await db.execute(
                select(Model).where(
                    Model.type == model_type,
                    Model.is_active == True
                ).limit(1)
            )
            model = result.scalar_one_or_none()
            if model:
                logger.info(f"从数据库获取激活的 {model_type} 模型：{model.name}")
            else:
                logger.warning(f"数据库中没有找到激活的 {model_type} 模型")
        
        return model
    except Exception as e:
        logger.error(f"获取默认模型失败：{e}")
        return None
