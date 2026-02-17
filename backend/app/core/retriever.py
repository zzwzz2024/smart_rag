"""
SmartRAG 混合检索引擎
- 向量语义检索
- BM25 关键词检索
- RRF (Reciprocal Rank Fusion) 融合排序
"""
import re
from typing import List, Dict, Optional
from dataclasses import dataclass
from loguru import logger

from rank_bm25 import BM25Okapi
import jieba

from backend.app.core.vector_store import VectorStore, SearchResult
from backend.app.config import get_settings

settings = get_settings()

@dataclass
class RetrievalResult:
    """检索结果 (含融合分数)"""
    chunk_id: str
    content: str
    score: float
    vector_score: float
    bm25_score: float
    metadata: dict


class HybridRetriever:
    """混合检索器"""

    def __init__(self,api_key=None,base_url=None,model_name=None):
        self.vector_store = VectorStore(api_key,base_url,model_name)

    async def retrieve(
        self,
        query: str,
        kb_ids: List[str],
        top_k: int = 10,
        mode: str = "hybrid",     # vector / keyword / hybrid
        vector_weight: float = 0.7,
        keyword_weight: float = 0.3,
    ) -> List[RetrievalResult]:
        """
        主检索入口
        1. 查询预处理
        2. 多路召回
        3. RRF 融合
        """
        logger.info(
            f"Retrieving: query='{query[:50]}...', kb_ids={kb_ids}, mode={mode}"
        )

        # Step 1: 查询预处理
        processed_query = self._preprocess_query(query)

        all_results = []

        for kb_id in kb_ids:
            if mode == "vector":
                results = self._vector_search(processed_query, kb_id, top_k)
            elif mode == "keyword":
                results = self._keyword_search(processed_query, kb_id, top_k)
            else:
                results = self._hybrid_search(
                    processed_query, kb_id, top_k, vector_weight, keyword_weight
                )
            all_results.extend(results)

        # 按分数排序
        all_results.sort(key=lambda x: x.score, reverse=True)

        # 去重
        seen = set()
        unique_results = []
        for r in all_results:
            if r.chunk_id not in seen:
                seen.add(r.chunk_id)
                unique_results.append(r)

        return unique_results[:top_k]

    def _preprocess_query(self, query: str) -> str:
        """查询预处理"""
        query = query.strip()
        query = re.sub(r'\s+', ' ', query)
        return query

    def _vector_search(
        self, query: str, kb_id: str, top_k: int
    ) -> List[RetrievalResult]:
        """向量语义检索"""
        logger.info("_vector_search开始")
        results = self.vector_store.search(kb_id, query, top_k=top_k)
        logger.info("_vector_search完成")
        return [
            RetrievalResult(
                chunk_id=r.chunk_id,
                content=r.content,
                score=r.score,
                vector_score=r.score,
                bm25_score=0.0,
                metadata=r.metadata,
            )
            for r in results
        ]


    def _keyword_search(
        self, query: str, kb_id: str, top_k: int
    ) -> List[RetrievalResult]:
        """BM25 关键词检索"""
        # 从向量库获取所有文档 (生产环境应该用 ES)
        collection = self.vector_store._get_collection(kb_id)
        if collection.count() == 0:
            return []

        all_docs = collection.get(include=["documents", "metadatas"])
        if not all_docs["documents"]:
            return []

        # 中文分词
        tokenized_corpus = [
            list(jieba.cut(doc)) for doc in all_docs["documents"]
        ]
        tokenized_query = list(jieba.cut(query))

        # BM25
        bm25 = BM25Okapi(tokenized_corpus)
        scores = bm25.get_scores(tokenized_query)

        # 排序取 TopK
        scored_docs = list(zip(
            all_docs["ids"],
            all_docs["documents"],
            scores.tolist(),
            all_docs["metadatas"] or [{}] * len(all_docs["ids"]),
        ))
        scored_docs.sort(key=lambda x: x[2], reverse=True)

        max_score = max(scores) if max(scores) > 0 else 1.0

        results = []
        for doc_id, content, score, meta in scored_docs[:top_k]:
            normalized_score = score / max_score
            results.append(RetrievalResult(
                chunk_id=doc_id,
                content=content,
                score=normalized_score,
                vector_score=0.0,
                bm25_score=normalized_score,
                metadata=meta or {},
            ))

        return results

    def _hybrid_search(
        self,
        query: str,
        kb_id: str,
        top_k: int,
        vector_weight: float,
        keyword_weight: float,
    ) -> List[RetrievalResult]:
        """混合检索 + RRF 融合"""
        # 两路召回
        vector_results = self._vector_search(query, kb_id, top_k)
        logger.info("vector_results向量检索完成")
        keyword_results = self._keyword_search(query, kb_id, top_k)
        logger.info("keywords检索完成")
        logger.info("两路召回向量检索完成")
        # RRF 融合
        return self._rrf_fusion(
            vector_results,
            keyword_results,
            vector_weight,
            keyword_weight,
            k=60,
        )

    def _rrf_fusion(
        self,
        vector_results: List[RetrievalResult],
        keyword_results: List[RetrievalResult],
        vector_weight: float,
        keyword_weight: float,
        k: int = 60,
    ) -> List[RetrievalResult]:
        """
        Reciprocal Rank Fusion
        score = w1 * 1/(k + rank_vector) + w2 * 1/(k + rank_bm25)
        """
        rrf_scores: Dict[str, dict] = {}

        # 向量检索贡献
        for rank, result in enumerate(vector_results):
            cid = result.chunk_id
            if cid not in rrf_scores:
                rrf_scores[cid] = {
                    "result": result,
                    "rrf_score": 0.0,
                    "vector_score": result.vector_score,
                    "bm25_score": 0.0,
                }
            rrf_scores[cid]["rrf_score"] += vector_weight / (k + rank + 1)
            rrf_scores[cid]["vector_score"] = result.vector_score

        # BM25 贡献
        for rank, result in enumerate(keyword_results):
            cid = result.chunk_id
            if cid not in rrf_scores:
                rrf_scores[cid] = {
                    "result": result,
                    "rrf_score": 0.0,
                    "vector_score": 0.0,
                    "bm25_score": result.bm25_score,
                }
            rrf_scores[cid]["rrf_score"] += keyword_weight / (k + rank + 1)
            rrf_scores[cid]["bm25_score"] = result.bm25_score

        # 按 RRF 分数排序
        sorted_results = sorted(
            rrf_scores.values(),
            key=lambda x: x["rrf_score"],
            reverse=True,
        )
        logger.info("两路召回完成")
        return [
            RetrievalResult(
                chunk_id=item["result"].chunk_id,
                content=item["result"].content,
                score=item["rrf_score"],
                vector_score=item["vector_score"],
                bm25_score=item["bm25_score"],
                metadata=item["result"].metadata,
            )
            for item in sorted_results
        ]