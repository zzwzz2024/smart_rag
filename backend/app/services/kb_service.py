"""
知识库管理服务
"""
from typing import Optional
from loguru import logger
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.knowledge_base import KnowledgeBase
from backend.app.models.document import Document
from backend.app.core.vector_store import VectorStore


class KnowledgeBaseService:
    """知识库服务类"""

    def __init__(self):
        self.vector_store = VectorStore()

    async def update_kb_statistics(
            self,
            db: AsyncSession,
            kb_id: str
    ) -> Optional[KnowledgeBase]:
        """
        更新知识库统计信息
        包括文档数量和分块数量
        """
        # 获取知识库
        kb_result = await db.execute(
            select(KnowledgeBase).where(KnowledgeBase.id == kb_id)
        )
        kb = kb_result.scalar_one_or_none()
        if not kb:
            return None

        # 计算文档数量和分块数量
        doc_result = await db.execute(
            select(Document)
            .where(Document.kb_id == kb_id)
        )
        documents = doc_result.scalars().all()

        kb.doc_count = len(documents)
        kb.chunk_count = sum(d.chunk_count for d in documents if d.chunk_count)

        # 更新向量库统计
        vector_stats = self.vector_store.get_collection_stats(kb_id)
        if vector_stats:
            # 同步向量库中的实际数量
            kb.chunk_count = vector_stats['count']

        await db.flush()
        return kb

    async def delete_kb_and_vectors(
            self,
            db: AsyncSession,
            kb_id: str
    ) -> bool:
        """
        删除知识库及其所有向量数据
        """
        try:
            # 删除向量库
            self.vector_store.delete_collection(kb_id)

            # 删除知识库记录（通过级联删除文档）
            kb_result = await db.execute(
                select(KnowledgeBase).where(KnowledgeBase.id == kb_id)
            )
            kb = kb_result.scalar_one_or_none()
            if kb:
                await db.delete(kb)
                await db.flush()

            logger.info(f"Knowledge base {kb_id} and its vectors deleted successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to delete knowledge base {kb_id}: {str(e)}")
            return False

    async def update_kb_config(
            self,
            db: AsyncSession,
            kb_id: str,
            **config_updates
    ) -> Optional[KnowledgeBase]:
        """
        更新知识库配置
        """
        result = await db.execute(
            update(KnowledgeBase)
            .where(KnowledgeBase.id == kb_id)
            .values(**config_updates)
            .returning(KnowledgeBase)
        )
        kb = result.scalar_one_or_none()
        if kb:
            await db.flush()
        return kb

    async def get_kb_by_id(
            self,
            db: AsyncSession,
            kb_id: str
    ) -> Optional[KnowledgeBase]:
        """
        根据ID获取知识库
        """
        result = await db.execute(
            select(KnowledgeBase).where(KnowledgeBase.id == kb_id)
        )
        return result.scalar_one_or_none()

    async def get_kb_with_stats(
            self,
            db: AsyncSession,
            kb_id: str
    ) -> Optional[dict]:
        """
        获取知识库及其统计信息
        """
        kb = await self.get_kb_by_id(db, kb_id)
        if not kb:
            return None

        # 获取向量库统计
        vector_stats = self.vector_store.get_collection_stats(kb_id)

        return {
            "id": kb.id,
            "name": kb.name,
            "description": kb.description,
            "avatar": kb.avatar,
            "doc_count": kb.doc_count,
            "chunk_count": kb.chunk_count,
            "vector_count": vector_stats.get('count', 0) if vector_stats else 0,
            "embedding_model": kb.embedding_model,
            "embedding_model_id": kb.embedding_model_id,
            "rerank_model": kb.rerank_model,
            "rerank_model_id": kb.rerank_model_id,
            "chunk_size": kb.chunk_size,
            "chunk_overlap": kb.chunk_overlap,
            "retrieval_mode": kb.retrieval_mode,
            "owner_id": kb.owner_id,
            "created_at": kb.created_at,
            "updated_at": kb.updated_at
        }

    async def reindex_kb(
            self,
            db: AsyncSession,
            kb_id: str
    ) -> bool:
        """
        重新索引整个知识库
        删除现有向量并重新添加所有文档的向量
        """
        try:
            # 先删除现有向量
            self.vector_store.delete_collection(kb_id)

            # 获取知识库中的所有文档
            doc_result = await db.execute(
                select(Document)
                .where(Document.kb_id == kb_id)
                .where(Document.status == "completed")
            )
            documents = doc_result.scalars().all()

            # 重新处理每个文档
            for doc in documents:
                # 这里可以调用文档处理服务重新处理文档
                # 但由于我们可能没有访问doc_service，我们可以直接重新索引
                from backend.app.services.doc_service import process_document
                await process_document(db, doc.id)

            logger.info(f"Reindexed knowledge base {kb_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to reindex knowledge base {kb_id}: {str(e)}")
            return False

    async def validate_kb_access(
            self,
            db: AsyncSession,
            kb_id: str,
            user_id: str
    ) -> bool:
        """
        验证用户是否有访问知识库的权限
        """
        result = await db.execute(
            select(KnowledgeBase)
            .where(KnowledgeBase.id == kb_id)
            .where(KnowledgeBase.owner_id == user_id)
        )
        return result.scalar_one_or_none() is not None


# 创建全局实例
kb_service = KnowledgeBaseService()