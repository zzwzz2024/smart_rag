"""
API聊天接口
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger
from backend.app.database import get_db
from backend.app.services.api_authorization_service import ApiAuthorizationService
from backend.app.services.api_log_service import ApiLogService
from backend.app.models.response_model import Response
from backend.app.config import get_settings
from backend.app.schemas.api import ApiChatRequest
from backend.app.utils.api_utils import get_client_ip, calculate_response_time


router = APIRouter()
settings = get_settings()


@router.post("", response_model=Response)
async def api_chat(
    request: ApiChatRequest,
    auth_code: str,
    db: AsyncSession = Depends(get_db),
    fastapi_request: Request = None,
):
    """使用API授权码访问知识库"""
    import time
    start_time = time.time()
    status = 200
    error_message = None
    client_ip = get_client_ip(fastapi_request)  # 使用工具函数获取客户端IP
    
    try:
        # 验证授权
        authorization = await ApiAuthorizationService.validate_authorization(
            db, auth_code, client_ip
        )
        if not authorization:
            status = 401
            error_message = "授权无效或已过期"
            return Response(data={"success": False, "message": error_message})
        
        # 检查知识库是否在授权列表中
        from sqlalchemy import select, join
        from backend.app.models.knowledge_base import KnowledgeBase
        from backend.app.models.api_authorization import knowledge_base_authorization_association
        
        result = await db.execute(
            select(
                KnowledgeBase.id
            ).select_from(
                join(
                    knowledge_base_authorization_association,
                    KnowledgeBase,
                    knowledge_base_authorization_association.c.knowledge_base_id == KnowledgeBase.id
                )
            ).where(
                knowledge_base_authorization_association.c.authorization_id == authorization.id,
                KnowledgeBase.id == request.kb_id
            )
        )
        
        if not result.scalar_one_or_none():
            status = 403
            error_message = "知识库未授权"
            return Response(data={"success": False, "message": error_message})
        
        # 处理聊天请求
        from backend.app.core.rag_pipeline import RAGPipeline
        from backend.app.models.model import Model
        from sqlalchemy import select
        
        # 获取知识库信息
        kb_result = await db.execute(
            select(KnowledgeBase).where(KnowledgeBase.id == request.kb_id)
        )
        knowledge_base = kb_result.scalar_one()
        
        # 确定使用的模型
        model_id = request.model_id or knowledge_base.embedding_model_id
        if not model_id:
            # 如果没有指定模型，使用默认模型
            model_result = await db.execute(
                select(Model).where(Model.is_active == True).limit(1)
            )
            default_model = model_result.scalar_one_or_none()
            if not default_model:
                status = 500
                error_message = "无可用模型"
                return Response(data={"success": False, "message": error_message})
            model_id = default_model.id
        
        # 获取模型的完整信息
        model_result = await db.execute(
            select(Model).where(Model.id == model_id)
        )
        model = model_result.scalar_one()
        
        # 获取嵌入模型和重排序模型
        embedding_model = None
        if knowledge_base.embedding_model_id:
            embed_result = await db.execute(
                select(Model).where(Model.id == knowledge_base.embedding_model_id)
            )
            embedding_model = embed_result.scalar_one_or_none()
        
        rerank_model = None
        if knowledge_base.rerank_model_id:
            rerank_result = await db.execute(
                select(Model).where(Model.id == knowledge_base.rerank_model_id)
            )
            rerank_model = rerank_result.scalar_one_or_none()
        
        # 初始化RAG pipeline，使用知识库的模型信息
        pipeline = RAGPipeline(
            api_key=model.api_key,
            base_url=model.base_url,
            model_name=model.model,
            embedding_model=embedding_model,
            rerank_model=rerank_model
        )
        logger.info(f"pipeline初始化完成")
        # 执行查询
        response = await pipeline.run(
            query=request.query,
            kb_ids=[request.kb_id],
            model_id=model_id,
            model=model.model,
            api_key=model.api_key,
            base_url=model.base_url,
            retrieval_mode=knowledge_base.retrieval_mode,
            use_llm = False,
            db=db
        )
        
        return Response(data={
            "success": True,
            "answer": response.answer,
        })
    except Exception as e:
        logger.error(f"API聊天失败: {str(e)}")
        status = 500
        error_message = str(e)
        return Response(data={"success": False, "message": settings.DEFAULT_ERROR_MESSAGE})
    finally:
        # 记录日志
        try:
            response_time = calculate_response_time(start_time)  # 使用工具函数计算响应时间
            
            await ApiLogService.create_log(
                db=db,
                auth_code=auth_code,
                endpoint=settings.API_CHAT_ENDPOINT,
                method="POST",
                ip=client_ip,
                status=status,
                response_time=response_time,
                error_message=error_message
            )
        except Exception as log_error:
            logger.error(f"记录日志失败: {str(log_error)}")
