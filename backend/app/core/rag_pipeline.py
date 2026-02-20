"""
SmartRAG 全流程编排器
Query → Retrieval → Rerank → Generation → Output
"""
import json
from typing import List, Optional
from loguru import logger

from backend.app.core.retriever import HybridRetriever, RetrievalResult
from backend.app.core.reranker import Reranker
from backend.app.core.generator import Generator, GenerationResult
from backend.app.config import get_settings
from backend.app.models.document import DocumentChunk, Document
from sqlalchemy import select

settings = get_settings()

class RAGPipeline:
    """RAG 全流程编排"""

    def __init__(self,api_key=None,base_url=None,model_name=None, embedding_model=None, rerank_model=None):
        self.retriever = HybridRetriever(embedding_model=embedding_model)
        self.reranker = Reranker(rerank_model=rerank_model)
        self.generator = Generator(api_key,base_url,model_name)

    async def run(
        self,
        query: str,
        kb_ids: List[str],
        conversation_history: List[dict] = None,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url:Optional[str] = None,
        model_id: Optional[str] = None,
        temperature: Optional[float] = None,
        top_k: Optional[float] = None,
        top_p: Optional[float] = None,
        retrieval_mode: str = "hybrid",
        use_llm: bool = True,
        db = None,
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
                model_id=model_id,
                temperature=temperature,
                top_p=top_p,
                api_key=api_key,
                base_url=base_url
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
        if use_llm:
            # ── Stage 4: 生成 ──
            logger.info("[RAG] Stage 4: Generation")
            result = await self.generator.generate(
                query=query,
                retrieved_chunks=filtered,
                conversation_history=conversation_history,
                model=model,
                model_id=model_id,
                api_key=api_key,
                base_url=base_url,
                temperature=temperature,
                top_p=top_p,
            )

            logger.info(
                f"[RAG] Done - confidence={result.confidence}, "
                f"citations={len(result.citations)}, "
                f"time={result.response_time:.2f}s"
            )

            return result
        else:
            results = []
            for result in filtered:
                content = result.content.replace("\n", "")
                filename = "unknown"
                if db and result.chunk_id:
                    try:
                        # 从chunk表获取doc_id
                        chunk_result = await db.execute(
                            select(DocumentChunk.doc_id).where(DocumentChunk.id == result.chunk_id)
                        )
                        doc_id = chunk_result.scalar_one_or_none()
                        if doc_id:
                            # 从document表获取filename
                            doc_result = await db.execute(
                                select(Document.filename).where(Document.id == doc_id)
                            )
                            filename = doc_result.scalar_one_or_none() or "unknown"
                    except Exception as e:
                        logger.error(f"获取文件名失败: {str(e)}")
                else:
                    # 如果没有数据库连接，回退到从metadata获取
                    filename = result.metadata.get("filename", "unknown")
                result_dict = {
                    "filename": filename,
                    "content": content,
                    "score": result.score,
                }
                results.append(json.dumps(result_dict, ensure_ascii=False, indent=None))
            return GenerationResult(
                answer="\n".join(results),
                confidence=0.0,
                citations=[],  # 保持原字段
                response_time=0.0,
                token_usage={}
            )


    async def run_stream(
        self,
        query: str,
        kb_ids: List[str],
        conversation_history: List[dict] = None,
        model: Optional[str] = None,
        model_id: Optional[str] = None,
        api_key: Optional[str] = None,
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
            model_id=model_id,
            api_key=api_key,
            temperature=temperature,
        ):
            yield token