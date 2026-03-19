from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional


class ApiAuthorizationBase(BaseModel):
    """API授权基础模型"""
    vendor_name: str = Field(..., description="供应商名称")
    vendor_contact: str = Field(..., description="供应商负责人")
    contact_phone: str = Field(..., description="联系电话")
    authorized_ips: Optional[str] = Field(None, description="授权IP地址，逗号分隔")
    knowledge_base_ids: List[str] = Field(..., description="授权知识库ID列表")
    start_time: datetime = Field(..., description="授权开始时间")
    end_time: datetime = Field(..., description="授权结束时间")


class ApiAuthorizationCreate(ApiAuthorizationBase):
    """创建API授权模型"""
    pass


class ApiAuthorizationUpdate(BaseModel):
    """更新API授权模型"""
    vendor_name: Optional[str] = Field(None, description="供应商名称")
    vendor_contact: Optional[str] = Field(None, description="供应商负责人")
    contact_phone: Optional[str] = Field(None, description="联系电话")
    authorized_ips: Optional[str] = Field(None, description="授权IP地址，逗号分隔")
    knowledge_base_ids: Optional[List[str]] = Field(None, description="授权知识库ID列表")
    start_time: Optional[datetime] = Field(None, description="授权开始时间")
    end_time: Optional[datetime] = Field(None, description="授权结束时间")
    is_active: Optional[bool] = Field(None, description="是否激活")


class ApiAuthorizationResponse(BaseModel):
    """API授权响应模型"""
    id: str = Field(..., description="授权ID")
    vendor_name: str = Field(..., description="供应商名称")
    vendor_contact: str = Field(..., description="供应商负责人")
    contact_phone: str = Field(..., description="联系电话")
    authorized_ips: Optional[str] = Field(None, description="授权IP地址，逗号分隔")
    auth_code: str = Field(..., description="授权码")
    start_time: datetime = Field(..., description="授权开始时间")
    end_time: datetime = Field(..., description="授权结束时间")
    is_active: bool = Field(..., description="是否激活")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    knowledge_base_ids: List[str] = Field(default_factory=list, description="授权知识库ID列表")
    knowledge_base_names: List[str] = Field(default_factory=list, description="授权知识库名称列表")

    class Config:
        from_attributes = True
