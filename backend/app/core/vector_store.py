"""
SmartRAG 向量存储 (ChromaDB)
支持: 按知识库隔离的 Collection 管理
"""
import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import List, Optional, Dict
from dataclasses import dataclass
from loguru import logger

from backend.app.config import get_settings
from backend.app.core.embedder import EmbeddingService

settings = get_settings()


@dataclass
class SearchResult:
    """检索结果"""
    chunk_id: str
    content: str
    score: float
    metadata: dict


class VectorStore:
    """向量存储服务"""

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self,api_key=None,base_url=None,model_name=None, embedding_model=None):
        if self._initialized:
            return
        self._initialized = False
        logger.info(f"VectorStore初始化url:{base_url}, model:{model_name}, embedding_model:{embedding_model}")
        # if api_key is None or base_url is None or model_name is None and embedding_model is None:
        #     logger.error("VectorStore初始化失败, api_key, base_url, model_name, embedding_model 模型参数为空")
        #     logger.info("无需初始化VectorStore")
        # else:
        self.client = chromadb.PersistentClient(
            path=settings.CHROMA_PERSIST_DIR,
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        self.embedder = EmbeddingService(embedding_model=embedding_model)
        logger.info("VectorStore initialized (ChromaDB)")

    def _get_collection(self, kb_id: str):
        """获取或创建 Collection"""
        collection_name = f"kb_{kb_id.replace('-', '_')}"
        return self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def add_chunks(
        self,
        kb_id: str,
        chunk_ids: List[str],
        contents: List[str],
        metadatas: List[dict],
    ):
        """批量添加向量"""
        if not contents:
            return

        collection = self._get_collection(kb_id)

        # 批量 Embedding
        embeddings = self.embedder.embed_texts(contents)

        # 写入 ChromaDB
        batch_size = 500
        for i in range(0, len(contents), batch_size):
            end = min(i + batch_size, len(contents))
            collection.add(
                ids=chunk_ids[i:end],
                embeddings=embeddings[i:end],
                documents=contents[i:end],
                metadatas=metadatas[i:end],
            )

        logger.info(
            f"Added {len(contents)} chunks to collection kb_{kb_id}"
        )

    async def search(
        self,
        kb_id: str,
        query: str,
        top_k: int = 20,
    ) -> List[SearchResult]:
        """向量检索"""
        collection = self._get_collection(kb_id)

        if collection.count() == 0:
            return []
        logger.info(f"query_embedding开始")
        query_embedding = await self.embedder.embed_query(query)
        logger.info(f"query_embedding完成")

        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=min(top_k, collection.count()),
            include=["documents", "metadatas", "distances"],
        )

        search_results = []
        if results and results["ids"] and results["ids"][0]:
            for i, chunk_id in enumerate(results["ids"][0]):
                # ChromaDB 返回 distance, 转成 similarity score
                distance = results["distances"][0][i]
                score = 1 - distance  # cosine distance → similarity

                search_results.append(SearchResult(
                    chunk_id=chunk_id,
                    content=results["documents"][0][i],
                    score=score,
                    metadata=results["metadatas"][0][i] if results["metadatas"] else {},
                ))
                # return SearchResult(items=raw_items)

        return search_results

    def delete_by_doc(self, kb_id: str, doc_id: str):
        """删除某个文档的所有向量"""
        collection = self._get_collection(kb_id)
        try:
            collection.delete(where={"doc_id": doc_id})
            logger.info(f"Deleted vectors for doc {doc_id}")
        except Exception as e:
            logger.error(f"Failed to delete vectors: {e}")

    def delete_collection(self, kb_id: str):
        """删除整个知识库的 Collection"""
        collection_name = f"kb_{kb_id.replace('-', '_')}"
        try:
            self.client.delete_collection(collection_name)
            logger.info(f"Deleted collection {collection_name}")
        except Exception as e:
            logger.warning(f"Collection not found: {e}")

    def get_collection_stats(self, kb_id: str) -> dict:
        """获取 Collection 统计信息"""
        collection = self._get_collection(kb_id)
        return {
            "count": collection.count(),
            "name": collection.name,
        }