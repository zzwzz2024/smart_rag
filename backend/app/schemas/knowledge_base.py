from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class KBCreate(BaseModel):
    name: str
    description: Optional[str] = None
    avatar: Optional[str] = "📚"
    embedding_model: Optional[str] = "text-embedding-3-small"
    chunk_size: Optional[int] = 512
    chunk_overlap: Optional[int] = 64
    retrieval_mode: Optional[str] = "hybrid"


class KBUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    avatar: Optional[str] = None
    retrieval_mode: Optional[str] = None


class KBResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    avatar: str
    embedding_model: str
    chunk_size: int
    chunk_overlap: int
    retrieval_mode: str
    doc_count: int
    chunk_count: int
    owner_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True