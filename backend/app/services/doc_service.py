"""
文档上传 & 处理服务
"""
import os
import uuid
from typing import Optional
from loguru import logger
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.config import get_settings
from backend.app.models.document import Document, DocumentChunk
from backend.app.models.knowledge_base import KnowledgeBase
from backend.app.core.document_parser import DocumentParser
from backend.app.core.chunker import SmartChunker
from backend.app.core.vector_store import VectorStore

settings = get_settings()
parser = DocumentParser()
chunker = SmartChunker()

# 延迟初始化VectorStore，在process_document中根据知识库配置创建
vector_store_instances = {}


async def process_document(
    db: AsyncSession,
    doc_id: str,
):
    """
    文档处理全流程:
    1. 解析文档
    2. 智能分块
    3. 向量化 & 存入向量库
    4. 更新数据库状态
    """
    # 获取文档记录
    result = await db.execute(select(Document).where(Document.id == doc_id))
    doc = result.scalar_one_or_none()
    if not doc:
        logger.error(f"Document not found: {doc_id}")
        return

    try:
        # 更新状态
        doc.status = "processing"
        # 不要在这里提交事务，让调用者处理事务提交

        logger.info(f"Processing document: {doc.filename}")

        # Step 1: 解析
        parsed = parser.parse(doc.file_path)
        if not parsed.content.strip():
            raise ValueError("文档内容为空")

        # Step 2: 分块
        chunks = chunker.chunk_document(parsed, doc.id, doc.kb_id)
        if not chunks:
            raise ValueError("分块结果为空")

        # Step 3: 存入数据库
        db_chunks = []
        chunk_ids = []
        chunk_contents = []
        chunk_metadatas = []

        for chunk in chunks:
            db_chunk = DocumentChunk(
                id=chunk.id,
                doc_id=doc.id,
                kb_id=doc.kb_id,
                content=chunk.content,
                chunk_index=chunk.chunk_index,
                token_count=chunk.token_count,
                meta=chunk.metadata,
            )
            db_chunks.append(db_chunk)
            chunk_ids.append(chunk.id)
            chunk_contents.append(chunk.content)
            chunk_metadatas.append(chunk.metadata)

        db.add_all(db_chunks)

        # Step 4: 向量化 & 存入向量库
        # 获取知识库配置
        kb_result = await db.execute(
            select(KnowledgeBase).where(KnowledgeBase.id == doc.kb_id)
        )
        kb = kb_result.scalar_one_or_none()
        
        if not kb:
            raise ValueError(f"知识库不存在: {doc.kb_id}")
        
        # 获取模型配置
        embedding_model_id = kb.embedding_model_id
        embedding_model = None
        if embedding_model_id:
            from backend.app.models.model import Model
            model_result = await db.execute(
                select(Model).where(Model.id == embedding_model_id)
            )
            embedding_model = model_result.scalar_one_or_none()
        
        # 创建或获取VectorStore实例
        vector_store_key = f"{doc.kb_id}_{embedding_model_id or 'default'}"
        if vector_store_key not in vector_store_instances:
            vector_store_instances[vector_store_key] = VectorStore(embedding_model=embedding_model)
        
        current_vector_store = vector_store_instances[vector_store_key]
        
        # 向量化并存储
        await current_vector_store.add_chunks(
            kb_id=doc.kb_id,
            chunk_ids=chunk_ids,
            contents=chunk_contents,
            metadatas=chunk_metadatas,
        )

        # Step 5: 更新统计
        doc.status = "completed"
        doc.chunk_count = len(chunks)

        # 更新知识库统计
        kb_result = await db.execute(
            select(KnowledgeBase).where(KnowledgeBase.id == doc.kb_id)
        )
        kb = kb_result.scalar_one_or_none()
        if kb:
            # 重新计算
            count_result = await db.execute(
                select(Document).where(Document.kb_id == doc.kb_id)
            )
            all_docs = count_result.scalars().all()
            kb.doc_count = len(all_docs)
            kb.chunk_count = sum(d.chunk_count for d in all_docs)

        await db.commit()
        logger.info(
            f"Document '{doc.filename}' processed: {len(chunks)} chunks"
        )

    except Exception as e:
        logger.error(f"Document processing failed: {e}")
        # 不要在这里提交事务，让调用者处理事务回滚
        # 文档记录和分块记录会被自动回滚
        raise