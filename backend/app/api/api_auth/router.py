"""
API授权相关路由
"""
from fastapi import APIRouter
from backend.app.api.api_auth.endpoints import authorization, chat, docs, logs

router = APIRouter()

# 注册子路由
router.include_router(authorization.router, prefix="/auth", tags=["api_authorization"])
router.include_router(chat.router, prefix="/chat", tags=["api_chat"])
router.include_router(docs.router, prefix="/doc", tags=["api_docs"])
router.include_router(logs.router, prefix="/logs", tags=["api_logs"])
