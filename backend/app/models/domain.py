import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Table, Column, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.database import Base

# 知识库与领域的多对多关联表
knowledge_base_domain_association = Table(
    'knowledge_base_domain_association',
    Base.metadata,
    Column('knowledge_base_id', String(36), ForeignKey('knowledge_bases.id'), primary_key=True),
    Column('domain_id', String(36), ForeignKey('domains.id'), primary_key=True)
)

class Domain(Base):
    __tablename__ = "domains"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    name: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    description: Mapped[str] = mapped_column(String(200), nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # 关系
    knowledge_bases = relationship(
        "KnowledgeBase",
        secondary=knowledge_base_domain_association,
        back_populates="domains"
    )
