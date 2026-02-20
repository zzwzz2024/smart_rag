"""
API 路由注册
"""
from fastapi import APIRouter
from backend.app.api import auth, knowledge_base, document, chat, evaluation, model, system, api_authorization

api_router = APIRouter(prefix="/api")

api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(knowledge_base.router, prefix="/kb", tags=["知识库"])
api_router.include_router(document.router, prefix="/document", tags=["文档"])
api_router.include_router(chat.router, prefix="/chat", tags=["对话"])
api_router.include_router(evaluation.router, prefix="/eval", tags=["知识库评估"])
api_router.include_router(model.router, prefix="/model", tags=["模型管理"])
api_router.include_router(api_authorization.router, prefix="/api-auth", tags=["API授权"])
api_router.include_router(system.router, tags=["系统设置"])