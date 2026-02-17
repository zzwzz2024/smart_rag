from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from enum import Enum
from backend.app.database import Base


class ModelType(str, Enum):
    EMBEDDING = "embedding"
    CHAT = "chat"
    RERANK = "rerank"


class ModelVendor(Base):
    __tablename__ = "model_vendors"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True, index=True)  # 厂商名称
    description = Column(Text, nullable=True)  # 厂商描述
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # 关系
    models = relationship("Model", back_populates="vendor_obj")


class Model(Base):
    __tablename__ = "models"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    model = Column(String, nullable=False, index=True)  # 模型标识
    type = Column(String, nullable=False, index=True)  # 使用String类型替代SQLEnum
    vendor_id = Column(String, ForeignKey("model_vendors.id"), nullable=True, index=True)  # 模型厂商外键
    api_key = Column(String, nullable=True)
    base_url = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False, index=True)  # 模型状态
    is_default = Column(Boolean, default=False, nullable=False, index=True)  # 是否为默认模型
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # 关系
    vendor_obj = relationship("ModelVendor", back_populates="models")
