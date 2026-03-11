from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class DomainBase(BaseModel):
    """领域基础模型"""
    name: str = Field(..., min_length=1, max_length=50, description="领域名称")
    description: Optional[str] = Field(None, max_length=200, description="领域描述")
    is_active: Optional[bool] = Field(True, description="是否启用")


class DomainCreate(DomainBase):
    """创建领域模型"""
    pass


class DomainUpdate(BaseModel):
    """更新领域模型"""
    name: Optional[str] = Field(None, min_length=1, max_length=50, description="领域名称")
    description: Optional[str] = Field(None, max_length=200, description="领域描述")
    is_active: Optional[bool] = Field(None, description="是否启用")


class DomainResponse(DomainBase):
    """领域响应模型"""
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
