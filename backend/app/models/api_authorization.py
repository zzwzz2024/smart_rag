import uuid
from datetime import datetime
from sqlalchemy import String, Text, Integer, DateTime, ForeignKey, Table, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.database import Base

# 知识库授权多对多关联表
from sqlalchemy import Column

knowledge_base_authorization_association = Table(
    'knowledge_base_authorization_association',
    Base.metadata,
    Column('authorization_id', String(36), ForeignKey('api_authorizations.id'), primary_key=True),
    Column('knowledge_base_id', String(36), ForeignKey('knowledge_bases.id'), primary_key=True)
)


class ApiAuthorization(Base):
    """接口授权模型"""
    __tablename__ = "api_authorizations"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    
    # 供应商信息
    vendor_name: Mapped[str] = mapped_column(String(100), index=True)
    vendor_contact: Mapped[str] = mapped_column(String(100))
    contact_phone: Mapped[str] = mapped_column(String(20))
    
    # 授权信息
    authorized_ips: Mapped[str] = mapped_column(Text, nullable=True)  # 逗号分隔的IP地址列表
    auth_code: Mapped[str] = mapped_column(String(64), unique=True, index=True)  # 生成的授权码
    
    # 有效期
    start_time: Mapped[datetime] = mapped_column(DateTime)
    end_time: Mapped[datetime] = mapped_column(DateTime)
    
    # 状态
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # 时间戳
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # 关系
    knowledge_bases = relationship(
        "KnowledgeBase",
        secondary=knowledge_base_authorization_association,
        backref="api_authorizations"
    )
