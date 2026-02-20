"""
API授权管理接口
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from loguru import logger
from backend.app.database import get_db
from backend.app.models.user import User
from backend.app.models.api_authorization import (
    ApiAuthorization,
    knowledge_base_authorization_association
)
from backend.app.schemas.api_authorization import (
    ApiAuthorizationCreate,
    ApiAuthorizationUpdate,
    ApiAuthorizationResponse
)
from backend.app.services.api_authorization_service import ApiAuthorizationService
from backend.app.utils.auth import get_current_user
from backend.app.models.response_model import Response


router = APIRouter()


@router.post("", response_model=Response)
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
        knowledge_base_ids = []
        knowledge_base_names = []
        if authorization_data.knowledge_base_ids:
            from sqlalchemy import select
            from backend.app.models.knowledge_base import KnowledgeBase
            
            result = await db.execute(
                select(KnowledgeBase).where(
                    KnowledgeBase.id.in_(authorization_data.knowledge_base_ids)
                )
            )
            knowledge_bases = result.scalars().all()
            knowledge_base_ids = [kb.id for kb in knowledge_bases]
            knowledge_base_names = [kb.name for kb in knowledge_bases]
        
        # 构建响应数据
        response_data = ApiAuthorizationResponse(
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
        
        return Response(data=response_data)
    except Exception as e:
        print(f"创建授权失败: {str(e)}")  # 打印详细错误以便调试
        raise HTTPException(status_code=400, detail="创建授权失败，请检查输入信息")


@router.get("", response_model=Response)
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
        
        # 单独查询所有授权的知识库关联
        from sqlalchemy import select, join
        from backend.app.models.knowledge_base import KnowledgeBase
        
        # 获取所有授权ID
        authorization_ids = [auth.id for auth in authorizations]
        
        # 批量查询知识库关联
        knowledge_base_map = {}
        if authorization_ids:
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
        
        # 构建响应数据
        response_data = []
        for authorization in authorizations:
            kb_info = knowledge_base_map.get(authorization.id, {"ids": [], "names": []})
            response_data.append(ApiAuthorizationResponse(
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
                knowledge_base_ids=kb_info["ids"],
                knowledge_base_names=kb_info["names"]
            ))
        
        return Response(data=response_data)
    except Exception as e:
        print(f"获取授权列表失败: {str(e)}")
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
        from sqlalchemy import select, join
        from backend.app.models.knowledge_base import KnowledgeBase
        
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
        
        # 构建响应数据
        response_data = ApiAuthorizationResponse(
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
        
        return Response(data=response_data)
    except HTTPException:
        raise
    except Exception as e:
        print(f"获取授权详情失败: {str(e)}")
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
        from sqlalchemy import select, join
        from backend.app.models.knowledge_base import KnowledgeBase
        
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
        
        # 构建响应数据
        response_data = ApiAuthorizationResponse(
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
        
        return Response(data=response_data)
    except HTTPException:
        raise
    except Exception as e:
        print(f"更新授权失败: {str(e)}")
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
        print(f"删除授权失败: {str(e)}")
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
        from sqlalchemy import select, join
        from backend.app.models.knowledge_base import KnowledgeBase
        
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
                knowledge_base_authorization_association.c.authorization_id == authorization.id
            )
        )
        
        knowledge_bases = []
        for kb_id, kb_name in result.all():
            knowledge_bases.append({"id": kb_id, "name": kb_name})
        
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
        print(f"验证授权失败: {str(e)}")
        return Response(data={"valid": False, "message": "验证失败"})


from pydantic import BaseModel
from typing import List

class ApiChatRequest(BaseModel):
    """API聊天请求模型"""
    query: str
    kb_id: str
    model_id: str = None


@router.post("/chat", response_model=Response)
async def api_chat(
    request: ApiChatRequest,
    auth_code: str,
    db: AsyncSession = Depends(get_db),
):
    """使用API授权码访问知识库"""
    try:
        # 验证授权
        from fastapi import Request
        
        # 获取客户端IP（这里简化处理，实际部署时应从请求头获取）
        client_ip = '127.0.0.1'  # 临时值，实际应从请求对象获取
        
        authorization = await ApiAuthorizationService.validate_authorization(
            db, auth_code, client_ip
        )
        if not authorization:
            return Response(data={"success": False, "message": "授权无效或已过期"})
        
        # 检查知识库是否在授权列表中
        from sqlalchemy import select, join
        from backend.app.models.knowledge_base import KnowledgeBase
        
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
            return Response(data={"success": False, "message": "知识库未授权"})
        
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
                return Response(data={"success": False, "message": "无可用模型"})
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
        print(f"API聊天失败: {str(e)}")
        return Response(data={"success": False, "message": "请求失败，请稍后重试"})
