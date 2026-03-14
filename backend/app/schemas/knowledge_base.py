from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


class KBCreate(BaseModel):
    name: str = Field(..., description="知识库名称")
    description: Optional[str] = Field(None, description="知识库描述")
    avatar: Optional[str] = Field("📚", description="知识库头像")
    embedding_model: Optional[str] = Field("text-embedding-3-small", description="嵌入模型")
    embedding_model_id: Optional[str] = Field(None, description="嵌入模型ID")
    rerank_model: Optional[str] = Field("", description="重排序模型")
    rerank_model_id: Optional[str] = Field(None, description="重排序模型ID")
    chunk_size: Optional[int] = Field(512, description="分块大小")
    chunk_overlap: Optional[int] = Field(64, description="分块重叠大小")
    chunk_method: Optional[str] = Field("smart", description="分块方法")
    retrieval_mode: Optional[str] = Field("hybrid", description="检索模式")
    tag_ids: Optional[List[str]] = Field(default_factory=list, description="标签ID列表")
    domain_ids: Optional[List[str]] = Field(default_factory=list, description="领域ID列表")


class KBUpdate(BaseModel):
    name: Optional[str] = Field(None, description="知识库名称")
    description: Optional[str] = Field(None, description="知识库描述")
    avatar: Optional[str] = Field(None, description="知识库头像")
    embedding_model: Optional[str] = Field(None, description="嵌入模型")
    embedding_model_id: Optional[str] = Field(None, description="嵌入模型ID")
    rerank_model: Optional[str] = Field(None, description="重排序模型")
    rerank_model_id: Optional[str] = Field(None, description="重排序模型ID")
    chunk_size: Optional[int] = Field(None, description="分块大小")
    chunk_overlap: Optional[int] = Field(None, description="分块重叠大小")
    chunk_method: Optional[str] = Field(None, description="分块方法")
    retrieval_mode: Optional[str] = Field(None, description="检索模式")
    tag_ids: Optional[List[str]] = Field(None, description="标签ID列表")
    domain_ids: Optional[List[str]] = Field(None, description="领域ID列表")


class KBResponse(BaseModel):
    id: str = Field(..., description="知识库ID")
    name: str = Field(..., description="知识库名称")
    description: Optional[str] = Field(None, description="知识库描述")
    avatar: str = Field(..., description="知识库头像")
    embedding_model: str = Field(..., description="嵌入模型")
    embedding_model_id: Optional[str] = Field(None, description="嵌入模型ID")
    rerank_model: Optional[str] = Field(None, description="重排序模型")
    rerank_model_id: Optional[str] = Field(None, description="重排序模型ID")
    chunk_size: int = Field(..., description="分块大小")
    chunk_overlap: int = Field(..., description="分块重叠大小")
    chunk_method: str = Field(..., description="分块方法")
    retrieval_mode: str = Field(..., description="检索模式")
    doc_count: int = Field(..., description="文档数量")
    chunk_count: int = Field(..., description="分块数量")
    owner_id: str = Field(..., description="所有者ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    tags: List[dict] = Field(default_factory=list, description="标签列表")
    domains: List[dict] = Field(default_factory=list, description="领域列表")

    class Config:
        from_attributes = True