"""
SmartRAG 全流程编排器
Query → Retrieval → Rerank → Generation → Output
"""
from typing import List, Optional
from loguru import logger

from backend.app.core.retriever import HybridRetriever, RetrievalResult
from backend.app.core.reranker import Reranker
from backend.app.core.generator import Generator, GenerationResult
from backend.app.config import get_settings

settings = get_settings()


class RAGPipeline:
    """RAG 全流程编排"""

    def __init__(self):
        self.retriever = HybridRetriever()
        self.reranker = Reranker()
        self.generator = Generator()

    async def run(
        self,
        query: str,
        kb_ids: List[str],
        conversation_history: List[dict] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        top_k: Optional[int] = None,
        retrieval_mode: str = "hybrid",
    ) -> GenerationResult:
        """
        执行完整 RAG 流程

        Stage 1: 检索 (Retrieval)
        Stage 2: 重排序 (Reranking)
        Stage 3: 过滤 (Filtering)
        Stage 4: 生成 (Generation)
        """
        top_k = top_k or settings.RERANK_TOP_K

        # ── Stage 1: 混合检索 ──
        logger.info(f"[RAG] Stage 1: Retrieval - query='{query[:50]}'")
        retrieved = await self.retriever.retrieve(
            query=query,
            kb_ids=kb_ids,
            top_k=settings.RETRIEVAL_TOP_K,
            mode=retrieval_mode,
        )
        logger.info(f"[RAG] Retrieved {len(retrieved)} chunks")

        if not retrieved:
            logger.warning("[RAG] No chunks retrieved")
            return await self.generator.generate(
                query=query,
                retrieved_chunks=[],
                conversation_history=conversation_history,
                model=model,
                temperature=temperature,
            )

        # ── Stage 2: 重排序 ──
        logger.info(f"[RAG] Stage 2: Reranking top {top_k}")
        reranked = await self.reranker.rerank(
            query=query,
            results=retrieved,
            top_k=top_k,
        )

        # ── Stage 3: 相关性过滤 ──
        filtered = [
            r for r in reranked
            if r.score >= settings.SIMILARITY_THRESHOLD
        ]
        if not filtered:
            logger.warning("[RAG] All results below threshold, using top result")
            filtered = reranked[:1]

        logger.info(f"[RAG] After filtering: {len(filtered)} chunks")

        # ── Stage 4: 生成 ──
        logger.info("[RAG] Stage 4: Generation")
        result = await self.generator.generate(
            query=query,
            retrieved_chunks=filtered,
            conversation_history=conversation_history,
            model=model,
            temperature=temperature,
        )

        logger.info(
            f"[RAG] Done - confidence={result.confidence}, "
            f"citations={len(result.citations)}, "
            f"time={result.response_time:.2f}s"
        )

        return result

    async def run_stream(
        self,
        query: str,
        kb_ids: List[str],
        conversation_history: List[dict] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        top_k: Optional[int] = None,
        retrieval_mode: str = "hybrid",
    ):
        """流式 RAG"""
        top_k = top_k or settings.RERANK_TOP_K

        # 检索 + 重排序
        retrieved = await self.retriever.retrieve(
            query=query, kb_ids=kb_ids,
            top_k=settings.RETRIEVAL_TOP_K, mode=retrieval_mode,
        )

        reranked = await self.reranker.rerank(
            query=query, results=retrieved, top_k=top_k,
        ) if retrieved else []

        filtered = [
            r for r in reranked if r.score >= settings.SIMILARITY_THRESHOLD
        ] or reranked[:1]

        # 流式生成
        async for token in self.generator.generate_stream(
            query=query,
            retrieved_chunks=filtered,
            conversation_history=conversation_history,
            model=model,
            temperature=temperature,
        ):
            yield token