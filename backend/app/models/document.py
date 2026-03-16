import uuid
from datetime import datetime
from sqlalchemy import (
    String, Text, Integer, Float, DateTime, ForeignKey, JSON, Boolean,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.database import Base


class Document(Base):
    __tablename__ = "kb_documents"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    kb_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("kb_knowledge_bases.id")
    )
    filename: Mapped[str] = mapped_column(String(255))
    file_path: Mapped[str] = mapped_column(String(500))
    file_type: Mapped[str] = mapped_column(String(20))     # pdf, docx, md, txt ...
    file_size: Mapped[int] = mapped_column(Integer)         # bytes
    status: Mapped[str] = mapped_column(
        String(20), default="pending"
    )  # pending / processing / completed / failed
    chunk_count: Mapped[int] = mapped_column(Integer, default=0)
    meta: Mapped[dict] = mapped_column(JSON, nullable=True)
    error_msg: Mapped[str] = mapped_column(Text, nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )

    # 关系
    knowledge_base = relationship("KnowledgeBase", back_populates="documents")
    chunks = relationship(
        "DocumentChunk", back_populates="document", cascade="all, delete-orphan"
    )
    roles = relationship("Role", secondary="kb_document_roles", back_populates="documents")


class DocumentRole(Base):
    __tablename__ = "kb_document_roles"

    doc_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("kb_documents.id"), primary_key=True
    )
    role_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("sys_roles.id"), primary_key=True
    )
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )


class DocumentChunk(Base):
    __tablename__ = "kb_document_chunks"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    doc_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("kb_documents.id")
    )
    kb_id: Mapped[str] = mapped_column(String(36), index=True)
    content: Mapped[str] = mapped_column(Text)
    chunk_index: Mapped[int] = mapped_column(Integer)
    token_count: Mapped[int] = mapped_column(Integer, default=0)
    meta: Mapped[dict] = mapped_column(JSON, nullable=True)
    # meta 内容示例: {"page": 3, "header": "第三章 ...", "source": "xx.pdf"}
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )

    # 关系
    document = relationship("Document", back_populates="chunks")