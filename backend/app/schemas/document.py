from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class DocumentResponse(BaseModel):
    id: str = Field(..., description="文档ID")
    kb_id: str = Field(..., description="知识库ID")
    filename: str = Field(..., description="文件名")
    file_type: str = Field(..., description="文件类型")
    file_size: int = Field(..., description="文件大小（字节）")
    status: str = Field(..., description="处理状态")
    chunk_count: int = Field(..., description="分块数量")
    error_msg: Optional[str] = Field(None, description="错误信息，可选")
    created_at: datetime = Field(..., description="创建时间")

    class Config:
        from_attributes = True


class ChunkResponse(BaseModel):
    id: str = Field(..., description="文本块ID")
    content: str = Field(..., description="文本内容")
    chunk_index: int = Field(..., description="块索引")
    token_count: int = Field(..., description="token数量")
    meta: Optional[dict] = Field(None, description="元数据，可选")

    class Config:
        from_attributes = True


class DocumentPermissionResponse(BaseModel):
    role_id: str = Field(..., description="角色ID")
    role_name: str = Field(..., description="角色名称")
    role_code: str = Field(..., description="角色代码")

    class Config:
        from_attributes = True
