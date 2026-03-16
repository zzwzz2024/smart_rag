"""
SmartRAG 全流程编排器
Query → Retrieval → Rerank → Generation → Output
"""
import json
from typing import List, Optional, Tuple
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.core.retriever import HybridRetriever, RetrievalResult
from backend.app.core.reranker import Reranker
from backend.app.core.generator import Generator, GenerationResult
from backend.app.config import get_settings
from backend.app.models.document import DocumentChunk, Document
from sqlalchemy import select

settings = get_settings()

class RAGPipeline:
    """RAG 全流程编排"""

    def __init__(self, api_key=None, base_url=None, model_name=None, embedding_model=None, rerank_model=None,db: AsyncSession = None, rerank_provider=None):
        self.retriever = HybridRetriever(embedding_model=embedding_model)
        self.reranker = Reranker(
            rerank_model=rerank_model,
            db = db,
            provider=rerank_provider
        )  # 传递所有参数
        self.generator = Generator(api_key, base_url, model_name)

    async def _rewrite_query_with_llm(
        self,
        query: str,
        domain: str = None,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model_id: Optional[str] = None,
    ) -> Tuple[str, List[str]]:
        """
        使用大模型进行查询改写和扩写
        返回：(优化后的主查询，扩展查询列表)
        """
        system_prompt = f"""你是一个专业的查询改写助手，负责将用户的原始查询改写成更适合检索的形式，并生成相关的扩展查询。

        任务要求：
        1. 分析用户的原始查询，理解其意图
        2. 生成一个优化后的主查询，使其更清晰、更具体，更适合检索
        3. 生成3-5个相关的扩展查询，涵盖不同的表述方式、同义词、相关概念等
        4. 扩展查询应该与原始查询意图相关，但使用不同的词汇和表达方式
        5. 如果有领域信息，请结合领域知识进行改写和扩展
        6. 输出格式必须严格按照以下JSON格式：
        {{
            "optimized_query": "优化后的主查询",
            "expanded_queries": ["扩展查询1", "扩展查询2", "扩展查询3", ...]
        }}

        当前领域：{domain or "通用"}
        """

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"原始查询：{query}"}
        ]

        try:
            # 获取或创建模型客户端
            client = self.generator._get_or_create_client(model_id, model, api_key, base_url)
            
            response = await client.chat.completions.create(
                model=model or "gpt-3.5-turbo",
                messages=messages,
                temperature=0.7,
                max_tokens=500,
                response_format={"type": "json_object"}
            )

            import json
            result = json.loads(response.choices[0].message.content)
            optimized_query = result.get("optimized_query", query)
            expanded_queries = result.get("expanded_queries", [])
            
            logger.info(f"[RAG] LLM optimized query: {optimized_query}")
            logger.info(f"[RAG] LLM expanded queries: {expanded_queries}")
            
            return optimized_query, expanded_queries
        except Exception as e:
            logger.error(f"LLM query rewriting failed: {e}")
            # 失败时回退到原始查询
            return query, []

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
        domain: str = None,  # 新增领域参数
        user = None,  # 新增用户参数，用于权限检查
    ) -> GenerationResult:
        """
        执行完整 RAG 流程

        Stage 1: 查询改写扩写 (Query Rewriting)
        Stage 2: 检索 (Retrieval)
        Stage 3: 重排序 (Reranking)
        Stage 4: 过滤 (Filtering)
        Stage 5: 生成 (Generation)
        """
        top_k = top_k or settings.RERANK_TOP_K

        # ── Stage 1: 查询改写扩写 ──
        processed_query = query
        if settings.ENABLE_QUERY_REWRITE:
            logger.info(f"[RAG] Stage 1: Query Rewriting - original query='{query[:50]}'")
            # 使用大模型进行查询改写和扩写
            processed_query, expanded_queries = await self._rewrite_query_with_llm(
                query=query,
                domain=domain,
                model=model,
                api_key=api_key,
                base_url=base_url,
                model_id=model_id
            )
            logger.info(f"[RAG] Processed query: {processed_query}")
            if expanded_queries:
                logger.info(f"[RAG] Expanded queries: {expanded_queries[:3]}")
        else:
            logger.info(f"[RAG] Query rewriting disabled")

        # ── Stage 2: 混合检索 ──
        logger.info(f"[RAG] Stage 2: Retrieval - query='{processed_query[:50]}', domain={domain}")
        retrieved = await self.retriever.retrieve(
            query=processed_query,
            kb_ids=kb_ids,
            top_k=settings.RETRIEVAL_TOP_K,
            mode=retrieval_mode,
            domain=domain,  # 传递领域参数
        )
        logger.info(f"[RAG] Retrieved {len(retrieved)} chunks")

        # ── 权限检查 ──
        if db and user:
            logger.info("[RAG] Checking document permissions")
            from backend.app.models.document import Document, DocumentChunk
            from backend.app.models.knowledge_base import KnowledgeBase
            from sqlalchemy import select, exists
            
            # 过滤出用户有权限的chunks
            authorized_chunks = []
            
            for chunk in retrieved:
                try:
                    # 获取chunk对应的文档ID
                    chunk_result = await db.execute(
                        select(DocumentChunk.doc_id).where(DocumentChunk.id == chunk.chunk_id)
                    )
                    doc_id = chunk_result.scalar_one_or_none()
                    
                    if doc_id:
                        # 获取文档信息
                        doc_result = await db.execute(
                            select(Document).where(Document.id == doc_id, Document.is_deleted == False)
                        )
                        doc = doc_result.scalar_one_or_none()
                        
                        if doc:
                            # 获取知识库信息
                            kb_result = await db.execute(
                                select(KnowledgeBase).where(KnowledgeBase.id == doc.kb_id, KnowledgeBase.is_deleted == False)
                            )
                            kb = kb_result.scalar_one_or_none()
                            
                            if kb:
                                # 检查权限
                                if kb.owner_id == user.id:
                                    # 用户是知识库所有者，有权限
                                    authorized_chunks.append(chunk)
                                else:
                                    # 检查用户角色是否有权限
                                    if user.role_id:
                                        from backend.app.models.document import DocumentRole
                                        role_result = await db.execute(
                                            select(DocumentRole).where(
                                                DocumentRole.doc_id == doc_id,
                                                DocumentRole.role_id == user.role_id,
                                                DocumentRole.is_deleted == False
                                            )
                                        )
                                        if role_result.scalar_one_or_none():
                                            # 用户角色有权限
                                            authorized_chunks.append(chunk)
                except Exception as e:
                    logger.error(f"Permission check failed for chunk {chunk.chunk_id}: {e}")
            
            retrieved = authorized_chunks
            logger.info(f"[RAG] After permission check: {len(retrieved)} chunks")

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

        # ── Stage 3: 重排序 ──
        filtered = retrieved
        if settings.ENABLE_RERANK:
            logger.info(f"[RAG] Stage 3: Reranking top {top_k}")
            reranked = await self.reranker.rerank(
                query=processed_query,
                results=retrieved,
                top_k=top_k,
            )

            # ── Stage 4: 相关性过滤 ──
            # 降低阈值以提高召回率
            threshold = settings.SIMILARITY_THRESHOLD * 0.8
            filtered = [
                r for r in reranked
                if r.score >= threshold
            ]
            if not filtered:
                logger.warning("[RAG] All results below threshold, using top result")
                filtered = reranked[:3]  # 使用前3个结果
        else:
            logger.info("[RAG] Reranking disabled, using top results directly")
            # 直接使用检索结果的前top_k个
            filtered = retrieved[:top_k]

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
        domain: str = None,  # 新增领域参数
        user = None,  # 新增用户参数，用于权限检查
    ):
        """流式 RAG"""
        top_k = top_k or settings.RERANK_TOP_K

        # ── 查询改写扩写 ──
        processed_query = query
        if settings.ENABLE_QUERY_REWRITE:
            logger.info(f"[RAG Stream] Query Rewriting - original query='{query[:50]}'")
            # 使用大模型进行查询改写和扩写
            processed_query, expanded_queries = await self._rewrite_query_with_llm(
                query=query,
                domain=domain,
                model=model,
                api_key=api_key,
                model_id=model_id
            )
            logger.info(f"[RAG Stream] Processed query: {processed_query}")
        else:
            logger.info(f"[RAG Stream] Query rewriting disabled")

        # 检索
        retrieved = await self.retriever.retrieve(
            query=processed_query, kb_ids=kb_ids,
            top_k=settings.RETRIEVAL_TOP_K, mode=retrieval_mode,
            domain=domain,  # 传递领域参数
        )

        # ── 权限检查 ──
        if db and user:
            logger.info("[RAG Stream] Checking document permissions")
            from backend.app.models.document import Document, DocumentChunk
            from backend.app.models.knowledge_base import KnowledgeBase
            from sqlalchemy import select
            
            # 过滤出用户有权限的chunks
            authorized_chunks = []
            
            for chunk in retrieved:
                try:
                    # 获取chunk对应的文档ID
                    chunk_result = await db.execute(
                        select(DocumentChunk.doc_id).where(DocumentChunk.id == chunk.chunk_id)
                    )
                    doc_id = chunk_result.scalar_one_or_none()
                    
                    if doc_id:
                        # 获取文档信息
                        doc_result = await db.execute(
                            select(Document).where(Document.id == doc_id, Document.is_deleted == False)
                        )
                        doc = doc_result.scalar_one_or_none()
                        
                        if doc:
                            # 获取知识库信息
                            kb_result = await db.execute(
                                select(KnowledgeBase).where(KnowledgeBase.id == doc.kb_id, KnowledgeBase.is_deleted == False)
                            )
                            kb = kb_result.scalar_one_or_none()
                            
                            if kb:
                                # 检查权限
                                if kb.owner_id == user.id:
                                    # 用户是知识库所有者，有权限
                                    authorized_chunks.append(chunk)
                                else:
                                    # 检查用户角色是否有权限
                                    if user.role_id:
                                        from backend.app.models.document import DocumentRole
                                        role_result = await db.execute(
                                            select(DocumentRole).where(
                                                DocumentRole.doc_id == doc_id,
                                                DocumentRole.role_id == user.role_id,
                                                DocumentRole.is_deleted == False
                                            )
                                        )
                                        if role_result.scalar_one_or_none():
                                            # 用户角色有权限
                                            authorized_chunks.append(chunk)
                except Exception as e:
                    logger.error(f"Permission check failed for chunk {chunk.chunk_id}: {e}")
            
            retrieved = authorized_chunks
            logger.info(f"[RAG Stream] After permission check: {len(retrieved)} chunks")

        # 重排序
        filtered = retrieved
        if settings.ENABLE_RERANK:
            logger.info(f"[RAG Stream] Reranking top {top_k}")
            reranked = await self.reranker.rerank(
                query=processed_query, results=retrieved, top_k=top_k,
            ) if retrieved else []

            filtered = [
                r for r in reranked if r.score >= settings.SIMILARITY_THRESHOLD
            ] or reranked[:1]
        else:
            logger.info("[RAG Stream] Reranking disabled, using top results directly")
            # 直接使用检索结果的前top_k个
            filtered = retrieved[:top_k] if retrieved else []

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