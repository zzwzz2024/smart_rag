"""
LangGraph 工作流管理
使用 LangGraph 管理模型和编排流程
"""
from typing import List, Optional, Dict, Any, AsyncGenerator
from langgraph.graph import StateGraph, START, END
from langgraph.runtime import get_runtime
from pydantic import BaseModel, Field
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from backend.app.core.retriever import HybridRetriever, RetrievalResult
from backend.app.core.reranker import Reranker
from backend.app.core.generator import Generator, GenerationResult
from backend.app.config import get_settings

settings = get_settings()


class RAGState(BaseModel):
    """RAG工作流状态"""
    model_config = {
        "arbitrary_types_allowed": True
    }
    
    query: str
    processed_query: str = ""
    kb_ids: List[str]
    conversation_history: List[Dict[str, Any]] = Field(default_factory=list)
    model: Optional[str] = None
    model_id: Optional[str] = None
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    temperature: Optional[float] = None
    top_p: Optional[float] = 0.95
    top_k: Optional[int] = None
    retrieval_mode: str = "hybrid"
    domain: Optional[str] = None
    use_llm: bool = True
    db: Optional[AsyncSession] = None
    pm_db: Optional[AsyncSession] = None
    user: Optional[Any] = None
    retrieved_chunks: List[RetrievalResult] = Field(default_factory=list)
    reranked_chunks: List[RetrievalResult] = Field(default_factory=list)
    generation_result: Optional[GenerationResult] = None
    intent: Optional[str] = None
    error: Optional[str] = None
    workflow_steps: List[Dict[str, Any]] = Field(default_factory=list)
    current_state: str = "initial"


class LangGraphWorkflow:
    """基于LangGraph的RAG工作流"""

    def __init__(self, api_key=None, base_url=None, model_name=None, embedding_model=None, rerank_model=None,
                 db: AsyncSession = None, pm_db: AsyncSession = None, rerank_provider=None):
        self.retriever = HybridRetriever(embedding_model=embedding_model, db=db)
        self.reranker = Reranker(
            rerank_model=rerank_model,
            db=db,
            provider=rerank_provider
        )
        self.generator = Generator(api_key, base_url, model_name, db=db)
        self.db = db
        self.pm_db = pm_db
        self.graph = self._build_graph()
        self.runnable = None

    def _build_graph(self):
        """构建LangGraph工作流"""
        graph = StateGraph(RAGState)

        # 添加节点
        graph.add_node("process_query", self._process_query)
        graph.add_node("detect_intent", self._detect_intent)
        graph.add_node("handle_database_intent", self._handle_database_intent)
        graph.add_node("handle_graph_database_intent", self._handle_graph_database_intent)
        graph.add_node("retrieve", self._retrieve)
        graph.add_node("rerank", self._rerank)
        graph.add_node("generate", self._generate)

        # 添加边
        graph.add_edge(START, "process_query")
        graph.add_edge("process_query", "detect_intent")
        
        # 条件边
        def intent_router(state: RAGState):
            if state.intent == "database" and state.pm_db:
                return "handle_database_intent"
            elif state.intent == "graph_database":
                return "handle_graph_database_intent"
            else:
                return "retrieve"

        graph.add_conditional_edges(
            "detect_intent",
            intent_router,
            {
                "handle_database_intent": "handle_database_intent",
                "handle_graph_database_intent": "handle_graph_database_intent",
                "retrieve": "retrieve"
            }
        )

        graph.add_edge("handle_database_intent", END)
        graph.add_edge("handle_graph_database_intent", END)
        graph.add_edge("retrieve", "rerank")
        graph.add_edge("rerank", "generate")
        graph.add_edge("generate", END)

        return graph

    async def _process_query(self, state: RAGState) -> Dict[str, Any]:
        """处理查询"""
        try:
            from backend.app.utils.time_tool import replace_relative_time_in_query
            processed_query = replace_relative_time_in_query(state.query)
            logger.info(f"[LangGraph] Processed query: {processed_query}")
            
            # 记录步骤
            step = {
                "step": "process_query",
                "status": "completed",
                "input": state.query,
                "output": processed_query,
                "timestamp": datetime.now().isoformat()
            }
            workflow_steps = state.workflow_steps.copy()
            workflow_steps.append(step)
            
            return {
                "processed_query": processed_query,
                "workflow_steps": workflow_steps,
                "current_state": "process_query_completed"
            }
        except Exception as e:
            logger.error(f"Process query failed: {e}")
            
            # 记录错误步骤
            step = {
                "step": "process_query",
                "status": "failed",
                "input": state.query,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            workflow_steps = state.workflow_steps.copy()
            workflow_steps.append(step)
            
            return {
                "error": str(e),
                "workflow_steps": workflow_steps,
                "current_state": "process_query_failed"
            }

    async def _detect_intent(self, state: RAGState) -> Dict[str, Any]:
        """检测查询意图"""
        try:
            from backend.app.core.prompts import INTENT_DETECTION_PROMPT
            system_prompt = INTENT_DETECTION_PROMPT

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"用户查询：{state.processed_query}"}
            ]

            client = self.generator._get_or_create_client(state.model_id, state.model, state.api_key, state.base_url)
            response = await client.chat.completions.create(
                model=state.model or "",
                messages=messages,
                temperature=0.1,
                max_tokens=20
            )

            intent = response.choices[0].message.content.strip().lower()
            logger.info(f"[LangGraph] Detected intent: {intent}")

            # 确定最终意图
            final_intent = "knowledge_base"
            if intent == 'database':
                final_intent = "database"
            elif intent == 'graph_database':
                final_intent = "graph_database"
            
            # 记录步骤
            step = {
                "step": "detect_intent",
                "status": "completed",
                "input": state.processed_query,
                "output": final_intent,
                "timestamp": datetime.now().isoformat()
            }
            workflow_steps = state.workflow_steps.copy()
            workflow_steps.append(step)

            return {
                "intent": final_intent,
                "workflow_steps": workflow_steps,
                "current_state": "detect_intent_completed"
            }
        except Exception as e:
            logger.error(f"Intent detection failed: {e}")
            
            # 记录错误步骤
            step = {
                "step": "detect_intent",
                "status": "failed",
                "input": state.processed_query,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            workflow_steps = state.workflow_steps.copy()
            workflow_steps.append(step)
            
            return {
                "intent": "knowledge_base",
                "workflow_steps": workflow_steps,
                "current_state": "detect_intent_failed"
            }

    async def _handle_database_intent(self, state: RAGState) -> Dict[str, Any]:
        """处理数据库查询意图"""
        try:
            logger.info("[LangGraph] Handling database intent")
            
            # 记录步骤开始
            step = {
                "step": "handle_database_intent",
                "status": "in_progress",
                "input": state.processed_query,
                "timestamp": datetime.now().isoformat()
            }
            workflow_steps = state.workflow_steps.copy()
            workflow_steps.append(step)
            
            # 生成SQL查询
            from backend.app.core.prompts import SQL_GENERATION_PROMPT
            system_prompt = SQL_GENERATION_PROMPT

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"用户查询：{state.processed_query}"}
            ]

            client = self.generator._get_or_create_client(state.model_id, state.model, state.api_key, state.base_url)
            response = await client.chat.completions.create(
                model=state.model or "",
                messages=messages,
                temperature=0.1,
                max_tokens=500
            )

            sql = response.choices[0].message.content.strip()
            logger.info(f"[LangGraph] Generated SQL: {sql}")

            # 执行SQL查询
            from sqlalchemy import text
            result = await state.pm_db.execute(text(sql))
            rows = result.all()
            columns = result.keys()
            results = [dict(zip(columns, row)) for row in rows]
            logger.info(f"[LangGraph] SQL executed successfully, {len(results)} rows returned")

            # 生成回答
            from backend.app.core.prompts import DATABASE_ANALYSIS_PROMPT
            system_prompt = DATABASE_ANALYSIS_PROMPT.format(results=results)

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": state.processed_query}
            ]

            response = await client.chat.completions.create(
                model=state.model or "",
                messages=messages,
                temperature=state.temperature or 0.7,
                max_tokens=1000
            )

            answer = response.choices[0].message.content.strip()
            logger.info("[LangGraph] Database query completed successfully")

            # 构建结果
            generation_result = GenerationResult(
                answer=answer,
                confidence=0.9,
                citations=[],
                response_time=0.0,
                token_usage={}
            )

            # 更新步骤状态
            workflow_steps[-1].update({
                "status": "completed",
                "output": answer,
                "details": {
                    "sql": sql,
                    "result_count": len(results)
                },
                "timestamp_end": datetime.now().isoformat()
            })

            return {
                "generation_result": generation_result,
                "workflow_steps": workflow_steps,
                "current_state": "database_intent_completed"
            }
        except Exception as e:
            logger.error(f"Database intent handling failed: {e}")
            
            # 更新步骤状态为失败
            workflow_steps = state.workflow_steps.copy()
            if workflow_steps and workflow_steps[-1].get("step") == "handle_database_intent":
                workflow_steps[-1].update({
                    "status": "failed",
                    "error": str(e),
                    "timestamp_end": datetime.now().isoformat()
                })
            else:
                # 添加失败步骤
                step = {
                    "step": "handle_database_intent",
                    "status": "failed",
                    "input": state.processed_query,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
                workflow_steps.append(step)
            
            return {
                "error": str(e), 
                "intent": "knowledge_base",
                "workflow_steps": workflow_steps,
                "current_state": "database_intent_failed"
            }

    async def _handle_graph_database_intent(self, state: RAGState) -> Dict[str, Any]:
        """处理图数据库查询意图"""
        try:
            logger.info("[LangGraph] Handling graph database intent")
            
            # 记录步骤开始
            step = {
                "step": "handle_graph_database_intent",
                "status": "in_progress",
                "input": state.processed_query,
                "timestamp": datetime.now().isoformat()
            }
            workflow_steps = state.workflow_steps.copy()
            workflow_steps.append(step)
            
            # 生成Cypher查询
            from backend.app.core.prompts import CYPHER_GENERATION_PROMPT
            system_prompt = CYPHER_GENERATION_PROMPT

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"用户查询：{state.processed_query}"}
            ]

            client = self.generator._get_or_create_client(state.model_id, state.model, state.api_key, state.base_url)
            response = await client.chat.completions.create(
                model=state.model or "",
                messages=messages,
                temperature=0.1,
                max_tokens=500
            )

            cypher = response.choices[0].message.content.strip()
            logger.info(f"[LangGraph] Generated Cypher: {cypher}")

            # 执行Cypher查询
            try:
                from neo4j import GraphDatabase
                neo4j_driver = GraphDatabase.driver(
                    settings.NEO4J_URL,
                    auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
                )
                with neo4j_driver.session() as session:
                    result = session.run(cypher)
                    results = [record.data() for record in result]
                logger.info(f"[LangGraph] Cypher executed successfully, {len(results)} rows returned")
            except Exception as e:
                logger.warning(f"Neo4j execution failed: {e}")
                results = []

            # 生成回答
            from backend.app.core.prompts import GRAPH_DATABASE_ANALYSIS_PROMPT
            system_prompt = GRAPH_DATABASE_ANALYSIS_PROMPT.format(results=results)

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": state.processed_query}
            ]

            response = await client.chat.completions.create(
                model=state.model or "",
                messages=messages,
                temperature=state.temperature or 0.7,
                max_tokens=1000
            )

            answer = response.choices[0].message.content.strip()
            logger.info("[LangGraph] Graph database query completed successfully")

            # 构建结果
            generation_result = GenerationResult(
                answer=answer,
                confidence=0.9,
                citations=[],
                response_time=0.0,
                token_usage={}
            )

            # 更新步骤状态
            workflow_steps[-1].update({
                "status": "completed",
                "output": answer,
                "details": {
                    "cypher": cypher,
                    "result_count": len(results)
                },
                "timestamp_end": datetime.now().isoformat()
            })

            return {
                "generation_result": generation_result,
                "workflow_steps": workflow_steps,
                "current_state": "graph_database_intent_completed"
            }
        except Exception as e:
            logger.error(f"Graph database intent handling failed: {e}")
            
            # 更新步骤状态为失败
            workflow_steps = state.workflow_steps.copy()
            if workflow_steps and workflow_steps[-1].get("step") == "handle_graph_database_intent":
                workflow_steps[-1].update({
                    "status": "failed",
                    "error": str(e),
                    "timestamp_end": datetime.now().isoformat()
                })
            else:
                # 添加失败步骤
                step = {
                    "step": "handle_graph_database_intent",
                    "status": "failed",
                    "input": state.processed_query,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
                workflow_steps.append(step)
            
            return {
                "error": str(e), 
                "intent": "knowledge_base",
                "workflow_steps": workflow_steps,
                "current_state": "graph_database_intent_failed"
            }

    async def _retrieve(self, state: RAGState) -> Dict[str, Any]:
        """检索文档"""
        try:
            logger.info(f"[LangGraph] Retrieving documents for query: {state.processed_query}")
            
            # 记录步骤开始
            step = {
                "step": "retrieve",
                "status": "in_progress",
                "input": state.processed_query,
                "details": {
                    "kb_ids": state.kb_ids,
                    "retrieval_mode": state.retrieval_mode,
                    "domain": state.domain
                },
                "timestamp": datetime.now().isoformat()
            }
            workflow_steps = state.workflow_steps.copy()
            workflow_steps.append(step)
            
            # 检查权限
            authorized_doc_ids, authorized_kb_ids = await self._check_permissions(
                state.db, state.user, state.kb_ids
            )

            # 检索
            retrieved = await self.retriever.retrieve(
                query=state.processed_query,
                kb_ids=authorized_kb_ids or state.kb_ids,
                top_k=settings.RETRIEVAL_TOP_K,
                mode=state.retrieval_mode,
                domain=state.domain,
                doc_ids=authorized_doc_ids,
            )
            logger.info(f"[LangGraph] Retrieved {len(retrieved)} chunks")
            
            # 更新步骤状态
            workflow_steps[-1].update({
                "status": "completed",
                "output": f"Retrieved {len(retrieved)} chunks",
                "details": {
                    "kb_ids": state.kb_ids,
                    "retrieval_mode": state.retrieval_mode,
                    "domain": state.domain,
                    "retrieved_count": len(retrieved),
                    "authorized_doc_ids": authorized_doc_ids,
                    "authorized_kb_ids": authorized_kb_ids
                },
                "timestamp_end": datetime.now().isoformat()
            })
            
            return {
                "retrieved_chunks": retrieved,
                "workflow_steps": workflow_steps,
                "current_state": "retrieve_completed"
            }
        except Exception as e:
            logger.error(f"Retrieval failed: {e}")
            
            # 更新步骤状态为失败
            workflow_steps = state.workflow_steps.copy()
            if workflow_steps and workflow_steps[-1].get("step") == "retrieve":
                workflow_steps[-1].update({
                    "status": "failed",
                    "error": str(e),
                    "timestamp_end": datetime.now().isoformat()
                })
            else:
                # 添加失败步骤
                step = {
                    "step": "retrieve",
                    "status": "failed",
                    "input": state.processed_query,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
                workflow_steps.append(step)
            
            return {
                "error": str(e),
                "workflow_steps": workflow_steps,
                "current_state": "retrieve_failed"
            }

    async def _rerank(self, state: RAGState) -> Dict[str, Any]:
        """重排序"""
        try:
            logger.info(f"[LangGraph] Reranking {len(state.retrieved_chunks)} chunks")
            
            # 记录步骤开始
            step = {
                "step": "rerank",
                "status": "in_progress",
                "input": f"{len(state.retrieved_chunks)} chunks",
                "details": {
                    "original_count": len(state.retrieved_chunks),
                    "enable_rerank": settings.ENABLE_RERANK,
                    "top_k": state.top_k or settings.RERANK_TOP_K
                },
                "timestamp": datetime.now().isoformat()
            }
            workflow_steps = state.workflow_steps.copy()
            workflow_steps.append(step)
            
            if settings.ENABLE_RERANK:
                reranked = await self.reranker.rerank(
                    query=state.processed_query,
                    results=state.retrieved_chunks,
                    top_k=state.top_k or settings.RERANK_TOP_K,
                )
                
                # 过滤
                threshold = settings.SIMILARITY_THRESHOLD * 0.8
                filtered = [
                    r for r in reranked
                    if r.score >= threshold
                ]
                if not filtered:
                    logger.warning("[LangGraph] All results below threshold, using top result")
                    filtered = reranked[:3]
            else:
                logger.info("[LangGraph] Reranking disabled, using top results directly")
                filtered = state.retrieved_chunks[:state.top_k or settings.RERANK_TOP_K]
            
            logger.info(f"[LangGraph] After reranking: {len(filtered)} chunks")
            
            # 更新步骤状态
            workflow_steps[-1].update({
                "status": "completed",
                "output": f"{len(filtered)} chunks after reranking",
                "details": {
                    "original_count": len(state.retrieved_chunks),
                    "enable_rerank": settings.ENABLE_RERANK,
                    "top_k": state.top_k or settings.RERANK_TOP_K,
                    "final_count": len(filtered),
                    "threshold": settings.SIMILARITY_THRESHOLD * 0.8 if settings.ENABLE_RERANK else None
                },
                "timestamp_end": datetime.now().isoformat()
            })
            
            return {
                "reranked_chunks": filtered,
                "workflow_steps": workflow_steps,
                "current_state": "rerank_completed"
            }
        except Exception as e:
            logger.error(f"Reranking failed: {e}")
            
            # 更新步骤状态为失败
            workflow_steps = state.workflow_steps.copy()
            if workflow_steps and workflow_steps[-1].get("step") == "rerank":
                workflow_steps[-1].update({
                    "status": "failed",
                    "error": str(e),
                    "timestamp_end": datetime.now().isoformat()
                })
            else:
                # 添加失败步骤
                step = {
                    "step": "rerank",
                    "status": "failed",
                    "input": f"{len(state.retrieved_chunks)} chunks",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
                workflow_steps.append(step)
            
            return {
                "reranked_chunks": state.retrieved_chunks[:5],
                "workflow_steps": workflow_steps,
                "current_state": "rerank_failed"
            }

    async def _generate(self, state: RAGState) -> Dict[str, Any]:
        """生成回答"""
        try:
            logger.info("[LangGraph] Generating answer")
            
            # 记录步骤开始
            step = {
                "step": "generate",
                "status": "in_progress",
                "input": state.processed_query,
                "details": {
                    "reranked_chunks_count": len(state.reranked_chunks),
                    "model": state.model,
                    "model_id": state.model_id
                },
                "timestamp": datetime.now().isoformat()
            }
            workflow_steps = state.workflow_steps.copy()
            workflow_steps.append(step)
            
            if not state.reranked_chunks:
                logger.warning("[LangGraph] No chunks retrieved")
                result = await self.generator.generate(
                    query=state.processed_query,
                    retrieved_chunks=[],
                    conversation_history=state.conversation_history,
                    model=state.model,
                    model_id=state.model_id,
                    temperature=state.temperature,
                    top_p=state.top_p,
                    api_key=state.api_key,
                    base_url=state.base_url
                )
            else:
                result = await self.generator.generate(
                    query=state.processed_query,
                    retrieved_chunks=state.reranked_chunks,
                    conversation_history=state.conversation_history,
                    model=state.model,
                    model_id=state.model_id,
                    api_key=state.api_key,
                    base_url=state.base_url,
                    temperature=state.temperature,
                    top_p=state.top_p,
                )
            
            logger.info(
                f"[LangGraph] Generation completed - confidence={result.confidence}, "
                f"citations={len(result.citations)}"
            )
            
            # 更新步骤状态
            workflow_steps[-1].update({
                "status": "completed",
                "output": result.answer[:100] + "..." if len(result.answer) > 100 else result.answer,
                "details": {
                    "reranked_chunks_count": len(state.reranked_chunks),
                    "model": state.model,
                    "model_id": state.model_id,
                    "confidence": result.confidence,
                    "citations_count": len(result.citations),
                    "response_time": result.response_time,
                    "token_usage": result.token_usage
                },
                "timestamp_end": datetime.now().isoformat()
            })
            
            return {
                "generation_result": result,
                "workflow_steps": workflow_steps,
                "current_state": "generate_completed"
            }
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            
            # 更新步骤状态为失败
            workflow_steps = state.workflow_steps.copy()
            if workflow_steps and workflow_steps[-1].get("step") == "generate":
                workflow_steps[-1].update({
                    "status": "failed",
                    "error": str(e),
                    "timestamp_end": datetime.now().isoformat()
                })
            else:
                # 添加失败步骤
                step = {
                    "step": "generate",
                    "status": "failed",
                    "input": state.processed_query,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
                workflow_steps.append(step)
            
            return {
                "error": str(e),
                "workflow_steps": workflow_steps,
                "current_state": "generate_failed"
            }

    async def _check_permissions(self, db, user, kb_ids) -> tuple:
        """检查权限"""
        if not db or not user:
            return None, None

        logger.info("[LangGraph] Checking permissions")
        from backend.app.models.document import Document, DocumentRole
        from backend.app.models.knowledge_base import KnowledgeBase, KnowledgeBaseRole
        from sqlalchemy import select

        authorized_doc_ids = set()
        authorized_kb_ids = set()

        # 获取所有相关知识库
        kb_result = await db.execute(
            select(KnowledgeBase).where(
                (KnowledgeBase.id.in_(kb_ids)) &
                (KnowledgeBase.is_deleted == False)
            )
        )
        knowledge_bases = kb_result.scalars().all()

        for kb in knowledge_bases:
            # 检查知识库权限
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

            # 检查文档权限
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

        logger.info(f"[LangGraph] Authorized {len(authorized_doc_ids)} documents")
        return list(authorized_doc_ids) if authorized_doc_ids else None, list(authorized_kb_ids) if authorized_kb_ids else None

    async def run(self, **kwargs) -> Dict[str, Any]:
        """运行工作流"""
        try:
            # 初始化 runnable
            if self.runnable is None:
                self.runnable = self.graph.compile()
            
            # 构建初始状态
            initial_state = RAGState(**kwargs)
            
            # 运行工作流
            result = await self.runnable.ainvoke(initial_state)
            
            # 检查 result 是否为字典
            if isinstance(result, dict):
                # 构建返回结果，包含工作流步骤和当前状态
                response = {
                    "generation_result": result.get("generation_result"),
                    "workflow_steps": result.get("workflow_steps", []),
                    "current_state": result.get("current_state", "completed"),
                    "error": result.get("error")
                }
                
                # 返回结果
                if response["generation_result"]:
                    return response
                else:
                    raise Exception(response["error"] or "Workflow failed without error message")
            else:
                # 构建返回结果，包含工作流步骤和当前状态
                response = {
                    "generation_result": result.generation_result,
                    "workflow_steps": result.workflow_steps,
                    "current_state": result.current_state,
                    "error": result.error
                }
                
                # 返回结果
                if result.generation_result:
                    return response
                else:
                    raise Exception(result.error or "Workflow failed without error message")
        except Exception as e:
            logger.error(f"Workflow run failed: {e}")
            # 返回默认结果
            return {
                "generation_result": GenerationResult(
                    answer=f"处理请求时出错: {str(e)}",
                    confidence=0.0,
                    citations=[],
                    response_time=0.0,
                    token_usage={}
                ),
                "workflow_steps": [],
                "current_state": "error",
                "error": str(e)
            }

    async def run_stream(self, **kwargs) -> AsyncGenerator[str, None]:
        """流式运行工作流"""
        try:
            # 初始化 runnable
            if self.runnable is None:
                self.runnable = self.graph.compile()
            
            # 构建初始状态
            initial_state = RAGState(**kwargs)
            
            # 定义一个函数来流式处理工作流步骤
            async def process_workflow_steps():
                # 运行工作流获取结果
                result = await self.runnable.ainvoke(initial_state)
                
                # 检查 result 是否为字典
                if isinstance(result, dict):
                    # 发送工作流步骤信息
                    workflow_steps = result.get("workflow_steps", [])
                    # 只发送一次工作流步骤信息
                    import json
                    yield f"data: {json.dumps({'workflow_steps': workflow_steps}, ensure_ascii=False)}\n\n"
                    import asyncio
                    await asyncio.sleep(0.05)
                    
                    # 发送每个步骤的状态更新
                    for i, step in enumerate(workflow_steps):
                        import json
                        yield f"data: {json.dumps({'current_step': step['step'], 'step_index': i}, ensure_ascii=False)}\n\n"
                        import asyncio
                        await asyncio.sleep(0.1)  # 控制步骤更新速度
                    
                    # 流式输出
                    if result.get("generation_result"):
                        answer = result["generation_result"].answer
                        for char in answer:
                            import json
                            yield f"data: {json.dumps({'token': char}, ensure_ascii=False)}\n\n"
                            import asyncio
                            await asyncio.sleep(0.01)  # 控制输出速度
                    else:
                        error_message = f"处理请求时出错: {result.get('error') or '未知错误'}"
                        for char in error_message:
                            import json
                            yield f"data: {json.dumps({'token': char}, ensure_ascii=False)}\n\n"
                            import asyncio
                            await asyncio.sleep(0.01)
                else:
                    # 发送工作流步骤信息
                    workflow_steps = result.workflow_steps
                    # 只发送一次工作流步骤信息
                    import json
                    yield f"data: {json.dumps({'workflow_steps': workflow_steps}, ensure_ascii=False)}\n\n"
                    import asyncio
                    await asyncio.sleep(0.05)
                    
                    # 发送每个步骤的状态更新
                    for i, step in enumerate(workflow_steps):
                        import json
                        yield f"data: {json.dumps({'current_step': step['step'], 'step_index': i}, ensure_ascii=False)}\n\n"
                        import asyncio
                        await asyncio.sleep(0.1)  # 控制步骤更新速度
                    
                    # 流式输出
                    if result.generation_result:
                        answer = result.generation_result.answer
                        for char in answer:
                            import json
                            yield f"data: {json.dumps({'token': char}, ensure_ascii=False)}\n\n"
                            import asyncio
                            await asyncio.sleep(0.01)  # 控制输出速度
                    else:
                        error_message = f"处理请求时出错: {result.error or '未知错误'}"
                        for char in error_message:
                            import json
                            yield f"data: {json.dumps({'token': char}, ensure_ascii=False)}\n\n"
                            import asyncio
                            await asyncio.sleep(0.01)
            
            # 执行并返回结果
            async for chunk in process_workflow_steps():
                yield chunk
            
            # 发送结束标记
            yield "data: [DONE]\n\n"
        except Exception as e:
            logger.error(f"Workflow stream failed: {e}")
            error_message = f"处理请求时出错: {str(e)}"
            for char in error_message:
                import json
                yield f"data: {json.dumps({'token': char}, ensure_ascii=False)}\n\n"
                import asyncio
                await asyncio.sleep(0.01)
            yield "data: [DONE]\n\n"

    async def run_with_agent(self, **kwargs) -> Dict[str, Any]:
        """使用智能体执行工作流"""
        try:
            # 初始化 runnable
            if self.runnable is None:
                self.runnable = self.graph.compile()
            
            # 构建初始状态
            initial_state = RAGState(**kwargs)
            
            # 运行工作流
            result = await self.runnable.ainvoke(initial_state)
            
            # 检查 result 是否为字典
            if isinstance(result, dict):
                # 构建智能体结果
                agent_result = {
                    'agent': 'research_agent',
                    'result': {
                        'success': True,
                        'response': result.get('generation_result').answer if result.get('generation_result') else '处理失败',
                        'confidence': result.get('generation_result').confidence if result.get('generation_result') else 0.0
                    },
                    'workflow_steps': result.get('workflow_steps', []),
                    'current_state': result.get('current_state', 'completed')
                }
            else:
                # 构建智能体结果
                agent_result = {
                    'agent': 'research_agent',
                    'result': {
                        'success': True,
                        'response': result.generation_result.answer if result.generation_result else '处理失败',
                        'confidence': result.generation_result.confidence if result.generation_result else 0.0
                    },
                    'workflow_steps': result.workflow_steps,
                    'current_state': result.current_state
                }
            
            return agent_result
        except Exception as e:
            logger.error(f"Agent workflow failed: {e}")
            return {
                'agent': 'research_agent',
                'result': {
                    'success': False,
                    'error': str(e)
                },
                'workflow_steps': [],
                'current_state': 'error'
            }

    async def run_with_agent_stream(self, **kwargs) -> AsyncGenerator[str, None]:
        """使用智能体执行工作流（流式输出）"""
        try:
            # 初始化 runnable
            if self.runnable is None:
                self.runnable = self.graph.compile()

            # 构建初始状态
            initial_state = RAGState(**kwargs)

            # 定义一个函数来流式处理工作流步骤
            async def process_workflow_steps():
                # 运行工作流获取结果，使用 stream 模式
                # astream_events 返回的是每个节点的输出字典，如 {'node_name': output}
                workflow_steps = []
                final_answer = ""

                async for event in self.runnable.astream_events(initial_state, version="v2"):
                    import json

                    # 处理节点完成事件
                    if event['event'] == 'on_chain_end' or event['event'] == 'on_chain_start':
                        node_name = event.get('name', '')

                        # 如果是工作流步骤相关的节点，发送更新
                        if node_name in ['process_query', 'detect_intent', 'retrieve', 'rerank', 'generate']:
                            # 构建当前步骤信息
                            step_info = {
                                'step': node_name,
                                'status': 'in_progress' if event['event'] == 'on_chain_start' else 'completed',
                                'timestamp': event.get('start_time', event.get('end_time', ''))
                            }

                            yield f"data: {json.dumps({'current_step': step_info}, ensure_ascii=False)}\n\n"

                    # 如果有生成器的 token 输出
                    if event['event'] == 'on_chain_end':
                        chunks = event.get('data', {}).get('chunk', [])
                        for chunk in chunks:
                            if hasattr(chunk, 'content') and chunk.content:
                                # 流式返回 token
                                yield f"data: {json.dumps({'token': chunk.content}, ensure_ascii=False)}\n\n"
                                final_answer += chunk.content

                    # 收集工作流步骤
                    if event['event'] == 'on_chain_end' and node_name in ['process_query', 'detect_intent', 'retrieve',
                                                                          'rerank', 'generate']:
                        metadata = event.get('metadata', {})
                        step_info = {
                            'step': node_name,
                            'status': 'completed',
                            'timestamp': event.get('end_time', ''),
                            'input': metadata.get('checkpoint_ns', ''),
                            'output': str(event.get('data', {}).get('output', {}))[:100]  # 限制长度
                        }
                        workflow_steps.append(step_info)

                    if event.get('name', '') == 'generate' and event.get('event', "") == 'on_chain_end':
                        # 发送结束标记
                        final_answer = "查询结果是:x.........."

                # 发送完整的工作流步骤信息
                if workflow_steps:
                    import asyncio
                    await asyncio.sleep(0.05)  # 短暂延迟，确保前面的步骤更新已发送
                    yield f"data: {json.dumps({'workflow_steps': final_answer}, ensure_ascii=False)}\n\n"

            # 执行并返回结果
            async for chunk in process_workflow_steps():
                yield chunk

            yield "data: [DONE]\n\n"

        except Exception as e:
            logger.error(f"Agent workflow stream failed: {e}")
            error_message = f"处理请求时出错：{str(e)}"
            for char in error_message:
                import json
                yield f"data: {json.dumps({'token': char}, ensure_ascii=False)}\n\n"
                import asyncio
                await asyncio.sleep(0.01)
            yield "data: [DONE]\n\n"