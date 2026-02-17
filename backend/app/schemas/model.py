from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from backend.app.models.model import ModelType


class ModelBase(BaseModel):
    name: str = Field(..., description="模型名称")
    model: str = Field(..., description="模型标识")
    type: ModelType = Field(..., description="模型类型")
    vendor_id: Optional[str] = Field(None, description="模型厂商ID", alias="vendorId")
    api_key: Optional[str] = Field(None, description="API密钥", alias="apiKey")
    base_url: Optional[str] = Field(None, description="基础URL", alias="baseUrl")
    description: Optional[str] = Field(None, description="模型描述")
    is_active: bool = Field(True, description="模型状态", alias="isActive")
    is_default: bool = Field(False, description="是否为默认模型", alias="isDefault")

    class Config:
        populate_by_name = True


class ModelCreate(ModelBase):
    pass


class ModelUpdate(BaseModel):
    name: Optional[str] = Field(None, description="模型名称")
    model: Optional[str] = Field(None, description="模型标识")
    vendor_id: Optional[str] = Field(None, description="模型厂商ID", alias="vendorId")
    api_key: Optional[str] = Field(None, description="API密钥", alias="apiKey")
    base_url: Optional[str] = Field(None, description="基础URL", alias="baseUrl")
    description: Optional[str] = Field(None, description="模型描述")
    is_active: Optional[bool] = Field(None, description="模型状态", alias="isActive")
    is_default: Optional[bool] = Field(None, description="是否为默认模型", alias="isDefault")

    class Config:
        populate_by_name = True


class ModelResponse(ModelBase):
    id: str = Field(..., description="模型ID")
    vendor_name: Optional[str] = Field(None, description="模型厂商名称", alias="vendorName")
    created_at: datetime = Field(..., description="创建时间", alias="createdAt")
    updated_at: datetime = Field(..., description="更新时间", alias="updatedAt")

    class Config:
        from_attributes = True
        populate_by_name = True


# 模型厂商相关schema
class ModelVendorBase(BaseModel):
    name: str = Field(..., description="厂商名称")
    description: Optional[str] = Field(None, description="厂商描述")


class ModelVendorCreate(ModelVendorBase):
    id: str = Field(..., description="厂商ID")


class ModelVendorUpdate(BaseModel):
    name: Optional[str] = Field(None, description="厂商名称")
    description: Optional[str] = Field(None, description="厂商描述")


class ModelVendorResponse(ModelVendorBase):
    id: str = Field(..., description="厂商ID")
    created_at: datetime = Field(..., description="创建时间", alias="createdAt")
    updated_at: datetime = Field(..., description="更新时间", alias="updatedAt")

    class Config:
        from_attributes = True
        populate_by_name = True


class ModelVendorListResponse(BaseModel):
    total: int = Field(..., description="总厂商数")
    items: list[ModelVendorResponse] = Field(..., description="厂商列表")


class ModelListResponse(BaseModel):
    total: int = Field(..., description="总模型数")
    items: list[ModelResponse] = Field(..., description="模型列表")
