from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class DocumentResponse(BaseModel):
    id: str
    kb_id: str
    filename: str
    file_type: str
    file_size: int
    status: str
    chunk_count: int
    error_msg: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class ChunkResponse(BaseModel):
    id: str
    content: str
    chunk_index: int
    token_count: int
    meta: Optional[dict]

    class Config:
        from_attributes = True