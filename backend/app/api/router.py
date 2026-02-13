"""
API 路由注册
"""
from fastapi import APIRouter
from backend.app.api import auth, knowledge_base, document, chat, evaluation

api_router = APIRouter(prefix="/api")

api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(knowledge_base.router, prefix="/kb", tags=["知识库"])
api_router.include_router(document.router, prefix="/document", tags=["文档"])
api_router.include_router(chat.router, prefix="/chat", tags=["对话"])
api_router.include_router(evaluation.router, prefix="/eval", tags=["评估"])