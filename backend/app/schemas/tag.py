from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class TagBase(BaseModel):
    """标签基础模型"""
    name: str = Field(..., min_length=1, max_length=50, description="标签名称")
    color: Optional[str] = Field("#4CAF50", description="标签颜色")
    is_active: Optional[bool] = Field(True, description="是否启用")


class TagCreate(TagBase):
    """创建标签模型"""
    pass


class TagUpdate(BaseModel):
    """更新标签模型"""
    name: Optional[str] = Field(None, min_length=1, max_length=50, description="标签名称")
    color: Optional[str] = Field(None, description="标签颜色")
    is_active: Optional[bool] = Field(None, description="是否启用")


class TagResponse(TagBase):
    """标签响应模型"""
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
