import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Table, Column, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.database import Base

# 知识库与标签的多对多关联表
knowledge_base_tag_association = Table(
    'knowledge_base_tag_association',
    Base.metadata,
    Column('knowledge_base_id', String(36), ForeignKey('knowledge_bases.id'), primary_key=True),
    Column('tag_id', String(36), ForeignKey('tags.id'), primary_key=True)
)

class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    name: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    color: Mapped[str] = mapped_column(String(20), default="#4CAF50")
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
        secondary=knowledge_base_tag_association,
        back_populates="tags"
    )
