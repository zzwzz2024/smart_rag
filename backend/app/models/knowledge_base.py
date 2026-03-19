import uuid
from datetime import datetime
from sqlalchemy import String, Text, Integer, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.database import Base
from backend.app.models.tag import knowledge_base_tag_association
from backend.app.models.domain import knowledge_base_domain_association


class KnowledgeBase(Base):
    __tablename__ = "kb_knowledge_bases"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    name: Mapped[str] = mapped_column(String(100), index=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    avatar: Mapped[str] = mapped_column(String(10), default="📚")

    # 配置
    embedding_model: Mapped[str] = mapped_column(
        String(100), default="text-embedding-3-small"
    )
    embedding_model_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("m_models.id"), nullable=True
    )
    rerank_model: Mapped[str] = mapped_column(
        String(100), default="", nullable=True
    )
    rerank_model_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("m_models.id"), nullable=True
    )
    chunk_size: Mapped[int] = mapped_column(Integer, default=512)
    chunk_overlap: Mapped[int] = mapped_column(Integer, default=64)
    chunk_method: Mapped[str] = mapped_column(
        String(50), default="smart"
    )  # smart / line / paragraph
    retrieval_mode: Mapped[str] = mapped_column(
        String(20), default="hybrid"
    )  # vector / keyword / hybrid

    # 统计
    doc_count: Mapped[int] = mapped_column(Integer, default=0)
    chunk_count: Mapped[int] = mapped_column(Integer, default=0)

    # 所属
    owner_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("sys_users.id")
    )
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # 关系
    owner = relationship("User", back_populates="knowledge_bases")
    documents = relationship(
        "Document", back_populates="knowledge_base", cascade="all, delete-orphan"
    )
    tags = relationship(
        "Tag",
        secondary=knowledge_base_tag_association,
        back_populates="knowledge_bases"
    )
    domains = relationship(
        "Domain",
        secondary=knowledge_base_domain_association,
        back_populates="knowledge_bases"
    )
    roles = relationship("Role", secondary="kb_knowledge_base_roles", back_populates="knowledge_bases")


class KnowledgeBaseRole(Base):
    __tablename__ = "kb_knowledge_base_roles"

    kb_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("kb_knowledge_bases.id"), primary_key=True
    )
    role_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("sys_roles.id"), primary_key=True
    )
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )