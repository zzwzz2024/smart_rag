"""
API相关的模型定义
"""
from pydantic import BaseModel, Field
from typing import Optional


class ApiChatRequest(BaseModel):
    """API聊天请求模型"""
    query: str = Field(..., description="聊天查询内容")
    kb_id: str = Field(..., description="知识库ID")
    model_id: Optional[str] = Field(None, description="模型ID，可选")


class ApiLogQuery(BaseModel):
    """API日志查询模型"""
    auth_code: Optional[str] = Field(None, description="授权码，可选")
    skip: int = Field(0, description="跳过记录数")
    limit: int = Field(20, description="返回记录数")
    start_date: Optional[str] = Field(None, description="开始日期，可选")
    end_date: Optional[str] = Field(None, description="结束日期，可选")
    vendor: Optional[str] = Field(None, description="厂商，可选")


class ApiLogStatsQuery(BaseModel):
    """API日志统计查询模型"""
    auth_code: Optional[str] = Field(None, description="授权码，可选")
    days: int = Field(7, description="统计天数")
    start_date: Optional[str] = Field(None, description="开始日期，可选")
    end_date: Optional[str] = Field(None, description="结束日期，可选")
    vendor: Optional[str] = Field(None, description="厂商，可选")
