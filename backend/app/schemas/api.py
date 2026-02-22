"""
API相关的模型定义
"""
from pydantic import BaseModel
from typing import Optional


class ApiChatRequest(BaseModel):
    """API聊天请求模型"""
    query: str
    kb_id: str
    model_id: str = None


class ApiLogQuery(BaseModel):
    """API日志查询模型"""
    auth_code: str = None
    skip: int = 0
    limit: int = 20
    start_date: str = None
    end_date: str = None
    vendor: str = None


class ApiLogStatsQuery(BaseModel):
    """API日志统计查询模型"""
    auth_code: str = None
    days: int = 7
    start_date: str = None
    end_date: str = None
    vendor: str = None
