"""
SmartRAG 全流程编排器
Query → Retrieval → Rerank → Generation → Output
"""
import json
from typing import List, Optional, Tuple, Dict, Any, AsyncGenerator
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.core.retriever import HybridRetriever, RetrievalResult
from backend.app.core.reranker import Reranker
from backend.app.core.generator import Generator, GenerationResult
from backend.app.config import get_settings
from sqlalchemy import select, text

settings = get_settings()

class RAGPipeline:
    """RAG 全流程编排"""

    def __init__(self, api_key=None, base_url=None, model_name=None, embedding_model=None, rerank_model=None,
                 db: AsyncSession = None,pm_db: AsyncSession = None, rerank_provider=None):
        self.retriever = HybridRetriever(embedding_model=embedding_model)
        self.reranker = Reranker(
            rerank_model=rerank_model,
            db = db,
            provider=rerank_provider
        )  # 传递所有参数
        self.generator = Generator(api_key, base_url, model_name)
        self.db = db
        self.pm_db = pm_db
        
        # 初始化Neo4j驱动
        try:
            from neo4j import GraphDatabase
            from backend.app.config import get_settings
            
            settings = get_settings()
            self.neo4j_driver = GraphDatabase.driver(
                settings.NEO4J_URL,
                auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
            )
            # 测试连接
            with self.neo4j_driver.session() as session:
                session.run("MATCH (n) RETURN count(n) LIMIT 1")
            logger.info("Neo4j connection established successfully")
        except Exception as e:
            logger.warning(f"Failed to initialize Neo4j driver: {e}")
            logger.warning("Using mock data for graph database queries")
            self.neo4j_driver = None

    async def _detect_query_intent(
        self,
        query: str,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model_id: Optional[str] = None,
    ) -> str:
        """
        检测用户查询意图
        返回：'knowledge_base'、'database' 或 'graph_database'
        """
        from backend.app.core.prompts import INTENT_DETECTION_PROMPT
        system_prompt = INTENT_DETECTION_PROMPT

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"用户查询：{query}"}
        ]

        try:
            # 获取或创建模型客户端
            client = self.generator._get_or_create_client(model_id, model, api_key, base_url)
            
            response = await client.chat.completions.create(
                model=model or "",
                messages=messages,
                temperature=0.1,
                max_tokens=20
            )

            intent = response.choices[0].message.content.strip().lower()
            logger.info(f"[RAG] Detected intent: {intent}")
            
            if intent == 'database':
                return 'database'
            elif intent == 'graph_database':
                return 'graph_database'
            else:
                return 'knowledge_base'
        except Exception as e:
            logger.error(f"Intent detection failed: {e}")
            # 失败时默认返回知识库查询
            return 'knowledge_base'

    async def _generate_sql_query(
        self,
        query: str,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model_id: Optional[str] = None,
    ) -> str:
        """
        根据用户查询和表结构生成SQL查询语句
        """
        from backend.app.core.prompts import SQL_GENERATION_PROMPT
        system_prompt = SQL_GENERATION_PROMPT

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"用户查询：{query}"}
        ]

        try:
            # 获取或创建模型客户端
            client = self.generator._get_or_create_client(model_id, model, api_key, base_url)
            
            response = await client.chat.completions.create(
                model=model or "",
                messages=messages,
                temperature=0.1,
                max_tokens=500
            )

            sql = response.choices[0].message.content.strip()
            logger.info(f"[RAG] Generated SQL: {sql}")
            
            return sql
        except Exception as e:
            logger.error(f"SQL generation failed: {e}")
            raise

    async def _generate_cypher_query(
        self,
        query: str,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model_id: Optional[str] = None,
    ) -> str:
        """
        根据用户查询生成Neo4j Cypher查询语句
        """
        from backend.app.core.prompts import CYPHER_GENERATION_PROMPT
        system_prompt = CYPHER_GENERATION_PROMPT

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"用户查询：{query}"}
        ]

        try:
            # 获取或创建模型客户端
            client = self.generator._get_or_create_client(model_id, model, api_key, base_url)
            
            response = await client.chat.completions.create(
                model=model or "",
                messages=messages,
                temperature=0.1,
                max_tokens=500
            )

            cypher = response.choices[0].message.content.strip()
            logger.info(f"[RAG] Generated Cypher: {cypher}")
            
            return cypher
        except Exception as e:
            logger.error(f"Cypher generation failed: {e}")
            raise

    async def _execute_sql_query(
        self,
        sql: str,
        pm_db: AsyncSession = None,
    ) -> List[dict]:
        """
        执行SQL查询并返回结果
        """
        try:
            logger.info(f"[RAG] Executing SQL: {sql}")
            result = await pm_db.execute(text(sql))
            rows = result.all()
            
            # 转换结果为字典列表
            columns = result.keys()
            results = [dict(zip(columns, row)) for row in rows]
            
            logger.info(f"[RAG] SQL executed successfully, {len(results)} rows returned")
            return results
        except Exception as e:
            logger.error(f"SQL execution failed: {e}")
            # 不要重新抛出异常，而是返回空列表
            return []

    async def _execute_cypher_query(
        self,
        cypher: str,
    ) -> List[dict]:
        """
        执行Cypher查询并返回结果
        """
        try:
            logger.info(f"[RAG] Executing Cypher: {cypher}")
            
            # 检查Neo4j驱动是否初始化
            if not self.neo4j_driver:
                logger.warning("Neo4j driver not initialized, using mock data")
                # 返回模拟数据
                return []
            
            # 执行Cypher查询
            with self.neo4j_driver.session() as session:
                result = session.run(cypher)
                results = [record.data() for record in result]
            
            logger.info(f"[RAG] Cypher executed successfully, {len(results)} rows returned")
            return results
        except Exception as e:
            logger.error(f"Cypher execution failed: {e}")
            # 失败时返回模拟数据
            return []

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
        from backend.app.core.prompts import QUERY_REWRITING_PROMPT
        system_prompt = QUERY_REWRITING_PROMPT.format(domain=domain if domain else "通用")

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"原始查询：{query}"}
        ]

        try:
            # 获取或创建模型客户端
            client = self.generator._get_or_create_client(model_id, model, api_key, base_url)
            
            response = await client.chat.completions.create(
                model=model or "",
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


    async def _process_relative_time(self, query: str) -> str:
        """处理查询中的相对时间"""
        from backend.app.utils.time_tool import replace_relative_time_in_query
        processed_query = replace_relative_time_in_query(query)
        logger.info(f"[RAG] Starting - original query='{query[:50]}...', processed query='{processed_query[:50]}...'")
        return processed_query

    async def _handle_database_intent(self, processed_query: str, model: str, api_key: str, base_url: str, model_id: str, temperature: float, pm_db) -> Optional[GenerationResult]:
        """处理数据库查询意图"""
        logger.info(f"[RAG] Database query intent detected")
        try:
            # 生成SQL查询
            sql = await self._generate_sql_query(
                query=processed_query,
                model=model,
                api_key=api_key,
                base_url=base_url,
                model_id=model_id
            )
            
            # 执行SQL查询
            results = await self._execute_sql_query(sql, pm_db)
            
            # 将查询结果传递给大模型进行总结
            from backend.app.core.prompts import DATABASE_ANALYSIS_PROMPT
            system_prompt = DATABASE_ANALYSIS_PROMPT.format(results=results)
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": processed_query}
            ]
            
            # 获取或创建模型客户端
            client = self.generator._get_or_create_client(model_id, model, api_key, base_url)
            
            response = await client.chat.completions.create(
                model=model or "",
                messages=messages,
                temperature=temperature or 0.7,
                max_tokens=1000
            )
            
            answer = response.choices[0].message.content.strip()
            logger.info(f"[RAG] Database query completed successfully")
            
            # 构建返回结果
            from backend.app.core.generator import GenerationResult
            return GenerationResult(
                answer=answer,
                confidence=0.9,
                citations=[],
                response_time=0.0,
                token_usage={}
            )
        except Exception as e:
            logger.error(f"Database query failed: {e}")
            # 失败时回退到知识库查询
            return None

    async def _handle_graph_database_intent(self, processed_query: str, model: str, api_key: str, base_url: str, model_id: str, temperature: float) -> Optional[GenerationResult]:
        """处理图数据库查询意图"""
        logger.info(f"[RAG] Graph database query intent detected")
        try:
            # 生成Cypher查询
            cypher = await self._generate_cypher_query(
                query=processed_query,
                model=model,
                api_key=api_key,
                base_url=base_url,
                model_id=model_id
            )
            
            # 执行Cypher查询
            results = await self._execute_cypher_query(cypher)
            
            # 将查询结果传递给大模型进行总结
            from backend.app.core.prompts import GRAPH_DATABASE_ANALYSIS_PROMPT
            system_prompt = GRAPH_DATABASE_ANALYSIS_PROMPT.format(results=results)
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": processed_query}
            ]
            
            # 获取或创建模型客户端
            client = self.generator._get_or_create_client(model_id, model, api_key, base_url)
            
            response = await client.chat.completions.create(
                model=model or "",
                messages=messages,
                temperature=temperature or 0.7,
                max_tokens=1000
            )
            
            answer = response.choices[0].message.content.strip()
            logger.info(f"[RAG] Graph database query completed successfully")
            
            # 构建返回结果
            from backend.app.core.generator import GenerationResult
            return GenerationResult(
                answer=answer,
                confidence=0.9,
                citations=[],
                response_time=0.0,
                token_usage={}
            )
        except Exception as e:
            logger.error(f"Graph database query failed: {e}")
            # 失败时回退到知识库查询
            return None

    async def _check_permissions(self, db, user, kb_ids) -> Tuple[Optional[List[str]], Optional[List[str]]]:
        """检查权限"""
        if not db or not user:
            return None, None

        logger.info("[RAG] Pre-filtering authorized documents")
        from backend.app.models.document import Document, DocumentRole
        from backend.app.models.knowledge_base import KnowledgeBase, KnowledgeBaseRole

        authorized_doc_ids = set()
        authorized_kb_ids = set()

        # 1. 获取所有相关知识库
        kb_result = await db.execute(
            select(KnowledgeBase).where(
                (KnowledgeBase.id.in_(kb_ids)) &
                (KnowledgeBase.is_deleted == False)
            )
        )
        knowledge_bases = kb_result.scalars().all()

        for kb in knowledge_bases:
            # 4. 单独的文档权限
            has_kb_permission = False
            kb_role_result = await db.execute(
                select(KnowledgeBaseRole).where(
                    (KnowledgeBaseRole.kb_id == kb.id) &
                    (KnowledgeBaseRole.role_id == user.role_id) &
                    (KnowledgeBaseRole.is_deleted == False)
                )
            )
            if kb_role_result.scalar_one_or_none():
                has_kb_permission = True
                authorized_kb_ids.add(kb.id)

            if not has_kb_permission:
                continue

            doc_role_result = await db.execute(
                select(DocumentRole.doc_id).where(
                    (DocumentRole.role_id == user.role_id) &
                    (DocumentRole.is_deleted == False)
                )
            )
            for doc_id in doc_role_result.scalars().all():
                # 验证文档是否在目标知识库中
                doc_check = await db.execute(
                    select(Document.kb_id).where(
                        (Document.id == doc_id) &
                        (Document.is_deleted == False)
                    )
                )
                doc_kb_id = doc_check.scalar_one_or_none()
                if doc_kb_id == kb.id and has_kb_permission:
                    authorized_doc_ids.add(doc_id)

        logger.info(f"[RAG] Authorized {len(authorized_doc_ids)} documents")
        return list(authorized_doc_ids) if authorized_doc_ids else None, list(authorized_kb_ids) if authorized_kb_ids else None

    async def _retrieve_and_rerank(self, processed_query: str, kb_ids: List[str], authorized_doc_ids: List[str], authorized_kb_ids: List[str], top_k: int, retrieval_mode: str, domain: str) -> List[RetrievalResult]:
        """检索和重排序"""
        # ── Stage 2: 检索 ──
        logger.info(f"[RAG] Stage 2: Retrieval - query='{processed_query[:50]}', domain={domain}")
        retrieved = await self.retriever.retrieve(
            query=processed_query,
            kb_ids=authorized_kb_ids or kb_ids,
            top_k=settings.RETRIEVAL_TOP_K,
            mode=retrieval_mode,
            domain=domain,
            doc_ids=authorized_doc_ids,
        )
        logger.info(f"[RAG] Retrieved {len(retrieved)} chunks")

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
                filtered = reranked[:3]
        else:
            logger.info("[RAG] Reranking disabled, using top results directly")
            filtered = retrieved[:top_k]

        logger.info(f"[RAG] After filtering: {len(filtered)} chunks")
        return filtered

    async def _generate_result(self, processed_query: str, filtered: List[RetrievalResult], conversation_history: List[dict], model: str, model_id: str, api_key: str, base_url: str, temperature: float, top_p: float) -> GenerationResult:
        """生成结果"""
        # ── Stage 4: 生成 ──
        logger.info("[RAG] Stage 4: Generation")
        result = await self.generator.generate(
            query=processed_query,
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

    async def _generate_non_llm_result(self, filtered: List[RetrievalResult], db) -> GenerationResult:
        """生成非LLM结果"""
        results = []
        for result in filtered:
            content = result.content.replace("\n", "")
            filename = "unknown"
            if db and result.chunk_id:
                try:
                    from backend.app.models.document import DocumentChunk, Document
                    # 从 chunk 获取 doc_id
                    chunk_result = await db.execute(
                        select(DocumentChunk.doc_id).where(DocumentChunk.id == result.chunk_id)
                    )
                    doc_id = chunk_result.scalar_one_or_none()
                    if doc_id:
                        # 从 document 表获取 filename
                        doc_result = await db.execute(
                            select(Document.filename).where(Document.id == doc_id)
                        )
                        filename = doc_result.scalar_one_or_none() or "unknown"
                except Exception as e:
                    logger.error(f"获取文件名失败：{str(e)}")
            else:
                filename = result.metadata.get("filename", "unknown")
            result_dict = {
                "filename": filename,
                "content": content,
                "score": result.score,
            }
            results.append(json.dumps(result_dict, ensure_ascii=False, indent=None))
        from backend.app.core.generator import GenerationResult
        return GenerationResult(
            answer="\n".join(results),
            confidence=0.0,
            citations=[],
            response_time=0.0,
            token_usage={}
        )

    async def run(
                self,
                query: str,
                kb_ids: List[str],
                conversation_history: List[dict] = None,
                model: Optional[str] = None,
                model_id: Optional[str] = None,
                api_key: Optional[str] = None,
                base_url: Optional[str] = None,
                temperature: Optional[float] = None,
                top_p: Optional[float] = 0.95,
                top_k: Optional[int] = None,
                retrieval_mode: str = "hybrid",
                domain: str = None,
                use_llm: bool = True,
                db=None,
                pm_db=None,
                user=None,
        ):
            """RAG 流程"""
            # 处理查询中的相对时间
            processed_query = await self._process_relative_time(query)

            # ── 新增：意图检测 ──
            intent = await self._detect_query_intent(
                query=processed_query,
                model=model,
                api_key=api_key,
                base_url=base_url,
                model_id=model_id
            )
            
            # 如果是数据库查询意图
            if intent == 'database' and pm_db:
                result = await self._handle_database_intent(
                    processed_query, model, api_key, base_url, model_id, temperature, pm_db
                )
                if result:
                    return result
            # 如果是图数据库查询意图
            elif intent == 'graph_database':
                result = await self._handle_graph_database_intent(
                    processed_query, model, api_key, base_url, model_id, temperature
                )
                if result:
                    return result

            # ── Stage 1: 查询改写 ──
            # 保留之前处理过的查询
            if settings.ENABLE_QUERY_REWRITE:
                logger.info(f"[RAG] Stage 1: Query Rewriting")
                processed_query, expanded_queries = await self._rewrite_query_with_llm(
                    query=processed_query,
                    domain=domain,
                    model=model,
                    api_key=api_key,
                    model_id=model_id
                )
            else:
                expanded_queries = []

            # ── 新增：权限前置检查 ──
            authorized_doc_ids, authorized_kb_ids = await self._check_permissions(db, user, kb_ids)

            # ── 检索和重排序 ──
            filtered = await self._retrieve_and_rerank(
                processed_query, kb_ids, authorized_doc_ids, authorized_kb_ids, top_k, retrieval_mode, domain
            )

            if not filtered:
                logger.warning("[RAG] No chunks retrieved")
                return await self.generator.generate(
                    query=processed_query,
                    retrieved_chunks=[],
                    conversation_history=conversation_history,
                    model=model,
                    model_id=model_id,
                    temperature=temperature,
                    top_p=top_p,
                    api_key=api_key,
                    base_url=base_url
                )

            # ── 生成结果 ──
            if use_llm:
                return await self._generate_result(
                    processed_query, filtered, conversation_history, model, model_id, api_key, base_url, temperature, top_p
                )
            else:
                return await self._generate_non_llm_result(filtered, db)

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
            user=None,  # 新增用户参数，用于权限检查
            db: AsyncSession = None,
            pm_db=None,
    ):
        """流式 RAG"""
        top_k = top_k or settings.RERANK_TOP_K

        # 处理查询中的相对时间
        processed_query = await self._process_relative_time_stream(query, kb_ids)

        # ── 新增：意图检测 ──
        intent = await self._detect_query_intent(
            query=processed_query,
            model=model,
            api_key=api_key,
            base_url=None,
            model_id=model_id
        )

        # 如果是数据库查询意图
        if intent == 'database' and pm_db:
            # 尝试处理数据库查询
            try:
                # 检查是否有生成的内容
                has_content = False
                async for token in self._handle_database_intent_stream(
                        processed_query, model, api_key, model_id, temperature, pm_db
                ):
                    yield token
                    has_content = True
                # 如果有内容生成，说明处理成功，直接返回
                if has_content:
                    return
            except Exception as e:
                logger.error(f"Database intent handling failed: {e}")
                # 失败时回退到知识库查询
        # 如果是图数据库查询意图
        elif intent == 'graph_database':
            # 尝试处理图数据库查询
            try:
                # 检查是否有生成的内容
                has_content = False
                async for token in self._handle_graph_database_intent_stream(
                        processed_query, model, api_key, model_id, temperature
                ):
                    yield token
                    has_content = True
                # 如果有内容生成，说明处理成功，直接返回
                if has_content:
                    return
            except Exception as e:
                logger.error(f"Graph database intent handling failed: {e}")
                # 失败时回退到知识库查询

        # ── 查询改写扩写 ──
        # 保留之前处理过的查询
        if settings.ENABLE_QUERY_REWRITE:
            logger.info(f"[RAG Stream] Query Rewriting - original query='{query[:50]}'")
            # 使用大模型进行查询改写和扩写
            processed_query, expanded_queries = await self._rewrite_query_with_llm(
                query=processed_query,
                domain=domain,
                model=model,
                api_key=api_key,
                model_id=model_id
            )
            logger.info(f"[RAG Stream] Processed query: {processed_query}")
        else:
            logger.info(f"[RAG Stream] Query rewriting disabled")

        # 检索和重排序
        filtered = await self._retrieve_and_rerank_stream(
            processed_query, kb_ids, top_k, retrieval_mode, domain, db, user
        )

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

    async def _process_relative_time_stream(self, query: str, kb_ids: List[str]) -> str:
        """处理查询中的相对时间（流式）"""
        from backend.app.utils.time_tool import replace_relative_time_in_query
        processed_query = replace_relative_time_in_query(query)
        logger.info(f"[RAG Stream] Starting - original query='{query[:50]}...', processed query='{processed_query[:50]}...', kb_ids={kb_ids}")
        return processed_query

    async def _handle_database_intent_stream(self, processed_query: str, model: str, api_key: str, model_id: str, temperature: float, db):
        """处理数据库查询意图（流式）"""
        logger.info(f"[RAG Stream] Database query intent detected")
        try:
            # 生成SQL查询
            sql = await self._generate_sql_query(
                query=processed_query,
                model=model,
                api_key=api_key,
                base_url=None,
                model_id=model_id
            )
            
            # 执行SQL查询
            results = await self._execute_sql_query(sql, db)
            
            # 将查询结果传递给大模型进行流式总结
            from backend.app.core.prompts import DATABASE_ANALYSIS_PROMPT
            system_prompt = DATABASE_ANALYSIS_PROMPT.format(results=results)
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": processed_query}
            ]
            
            # 获取或创建模型客户端
            client = self.generator._get_or_create_client(model_id, model, api_key, None)
            
            # 流式生成
            async for chunk in client.chat.completions.create(
                model=model or "",
                messages=messages,
                temperature=temperature or 0.7,
                max_tokens=1000,
                stream=True
            ):
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
            # 成功完成，不需要返回值
        except Exception as e:
            logger.error(f"Database query failed: {e}")
            # 失败时回退到知识库查询
            # 不返回任何值，让调用者知道生成器已结束

    async def _handle_graph_database_intent_stream(self, processed_query: str, model: str, api_key: str, model_id: str, temperature: float):
        """处理图数据库查询意图（流式）"""
        logger.info(f"[RAG Stream] Graph database query intent detected")
        try:
            # 生成Cypher查询
            cypher = await self._generate_cypher_query(
                query=processed_query,
                model=model,
                api_key=api_key,
                base_url=None,
                model_id=model_id
            )
            
            # 执行Cypher查询
            results = await self._execute_cypher_query(cypher)
            
            # 将查询结果传递给大模型进行流式总结
            from backend.app.core.prompts import GRAPH_DATABASE_ANALYSIS_PROMPT
            system_prompt = GRAPH_DATABASE_ANALYSIS_PROMPT.format(results=results)
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": processed_query}
            ]
            
            # 获取或创建模型客户端
            client = self.generator._get_or_create_client(model_id, model, api_key, None)
            
            # 流式生成
            async for chunk in client.chat.completions.create(
                model=model or "",
                messages=messages,
                temperature=temperature or 0.7,
                max_tokens=1000,
                stream=True
            ):
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
            # 成功完成，不需要返回值
        except Exception as e:
            logger.error(f"Graph database query failed: {e}")
            # 失败时回退到知识库查询
            # 不返回任何值，让调用者知道生成器已结束

    async def _check_permissions_stream(self, db, user, retrieved):
        """检查权限（流式）"""
        if not db or not user:
            return retrieved

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
        
        logger.info(f"[RAG Stream] After permission check: {len(authorized_chunks)} chunks")
        return authorized_chunks

    async def _retrieve_and_rerank_stream(self, processed_query: str, kb_ids: List[str], top_k: int, retrieval_mode: str, domain: str, db, user):
        """检索和重排序（流式）"""
        # 检索
        retrieved = await self.retriever.retrieve(
            query=processed_query, kb_ids=kb_ids,
            top_k=settings.RETRIEVAL_TOP_K, mode=retrieval_mode,
            domain=domain,  # 传递领域参数
        )

        # 权限检查
        retrieved = await self._check_permissions_stream(db, user, retrieved)

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

        return filtered

    async def run_with_agent(
        self,
        query: str,
        kb_ids: List[str],
        agent_name: str = "research_agent",
        context: Dict[str, Any] = None,
        model: Optional[str] = None,
        model_id: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """使用智能体执行RAG流程
        
        Args:
            query: 用户查询
            kb_ids: 知识库ID列表
            agent_name: 智能体名称
            context: 上下文信息
            model: 模型名称
            model_id: 模型ID
            api_key: API密钥
            base_url: API基础URL
            
        Returns:
            智能体执行结果
        """
        from backend.app.core.agents.research_agent import ResearchAgent
        from backend.app.core.agents.coordinator import AgentCoordinator
        
        # 构建上下文
        context = context or {}
        context.update({
            'kb_ids': kb_ids,
            'model': model,
            'model_id': model_id,
            'api_key': api_key,
            'base_url': base_url
        })
        
        # 初始化智能体
        from backend.app.core.agents.database_agent import DatabaseAgent
        from backend.app.core.agents.graph_agent import GraphAgent
        from backend.app.core.agents.time_agent import TimeAgent
        
        agents = {
            'research_agent': ResearchAgent(self),
            'database_agent': DatabaseAgent(self),
            'graph_agent': GraphAgent(self),
            'time_agent': TimeAgent(self)
        }
        
        # 初始化协调器
        coordinator = AgentCoordinator(agents)
        
        # 执行任务
        result = await coordinator.coordinate(query, context)
        return result

    async def run_with_agent_stream(
        self,
        query: str,
        kb_ids: List[str],
        agent_name: str = "research_agent",
        context: Dict[str, Any] = None,
        model: Optional[str] = None,
        model_id: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
    ) -> AsyncGenerator[str, None]:
        """使用智能体执行RAG流程（流式输出）
        
        Args:
            query: 用户查询
            kb_ids: 知识库ID列表
            agent_name: 智能体名称
            context: 上下文信息
            model: 模型名称
            model_id: 模型ID
            api_key: API密钥
            base_url: API基础URL
            
        Yields:
            流式输出的文本片段
        """
        from backend.app.core.agents.research_agent import ResearchAgent
        from backend.app.core.agents.coordinator import AgentCoordinator
        from backend.app.core.agents.database_agent import DatabaseAgent
        from backend.app.core.agents.graph_agent import GraphAgent
        from backend.app.core.agents.time_agent import TimeAgent
        
        # 构建上下文
        context = context or {}
        context.update({
            'kb_ids': kb_ids,
            'model': model,
            'model_id': model_id,
            'api_key': api_key,
            'base_url': base_url
        })
        
        # 初始化智能体
        agents = {
            'research_agent': ResearchAgent(self),
            'database_agent': DatabaseAgent(self),
            'graph_agent': GraphAgent(self),
            'time_agent': TimeAgent(self)
        }
        
        # 初始化协调器
        coordinator = AgentCoordinator(agents)
        
        # 执行任务获取结果
        agent_result = await coordinator.coordinate(query, context)
        
        # 流式生成响应
        if agent_result.get('result', {}).get('success'):
            answer = agent_result['result'].get('response', '智能体执行失败')
            
            # 逐字流式输出
            for char in answer:
                yield char
                import asyncio
                await asyncio.sleep(0.01)  # 控制输出速度
        else:
            error_message = f"智能体执行失败: {agent_result.get('result', {}).get('error', '未知错误')}"
            for char in error_message:
                yield char
                import asyncio
                await asyncio.sleep(0.01)