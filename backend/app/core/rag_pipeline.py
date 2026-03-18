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
        system_prompt = """你是一个意图检测助手，负责判断用户的查询是需要检索知识库还是查询数据库。

        规则：
        1. 如果查询涉及项目和采购类信息查询（如项目名称、项目编号、项目负责人、项目状态等）或采购信息（如采购订单、采购物品、采购金额、供应商等），返回 'database'
        2. 如果查询涉及省份景点、历史典故及发生时间类信息（如景点、历史典故、历史典故发生时间、省会等信息），返回 'graph_database'
        3. 其他所有查询（如技术文档、产品信息、公司政策等）返回 'knowledge_base'

        只需要返回 'database'、'graph_database' 或 'knowledge_base'，不需要其他任何内容。
        """

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"用户查询：{query}"}
        ]

        try:
            # 获取或创建模型客户端
            client = self.generator._get_or_create_client(model_id, model, api_key, base_url)
            
            response = await client.chat.completions.create(
                model=model or "gpt-3.5-turbo",
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
        system_prompt = """你是一个SQL查询生成器，负责根据用户的自然语言查询和表结构生成PostgreSQL SQL查询语句。

        表结构：
        1. 项目表 (project_info)
            project_code IS '项目编码：唯一标识符，主键'
            project_name IS '项目名称'
            region IS '所属大区'
            city IS '所属城市'
            department IS '所属部门'
            construction_unit IS '建设单位'
            contract_amount IS '合同金额'
            payment_terms IS '付款条款'
            sales_manager IS '销售经理'
            product_manager IS '产品经理'
            tech_manager IS '技术负责人'
            ops_manager IS '运维负责人'
            planned_start IS '计划开始日期'
            actual_start IS '实际开始日期'
            planned_end IS '计划结束日期'
            actual_end IS '实际结束日期'
            delay_status IS '延期状态（如：正常、延期）'
            construction_cycle IS '建设周期'

        2. 采购表 (project_purchases)
            id IS '主键ID'
            project_code IS '关联项目编码：外键，关联 project_info 表'
            project_name IS '项目名称（冗余字段，便于查询展示）'
            purchase_item IS '采购物品/服务名称'
            quantity IS '采购数量'
            unit_price IS '单价'
            total_amount IS '总金额'
            supplier IS '供应商名称'
            purchase_officer IS '采购负责人'
            warranty_period IS '质保期'
            purchase_date IS '采购日期'
            status IS '项目状态'

        要求：
        1. 分析用户查询，理解其意图
        2. 根据表结构生成正确的SQL查询语句
        3. 确保SQL语句语法正确，避免SQL注入
        4. 只返回SQL语句，不需要其他任何内容
        5. 如果查询涉及多个表，使用适当的JOIN操作
        """

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"用户查询：{query}"}
        ]

        try:
            # 获取或创建模型客户端
            client = self.generator._get_or_create_client(model_id, model, api_key, base_url)
            
            response = await client.chat.completions.create(
                model=model or "gpt-3.5-turbo",
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
        system_prompt = """你是一个Cypher查询生成器，负责根据用户的自然语言查询生成Neo4j Cypher查询语句。

        图数据库结构：
        1. 节点类型：
           - Province: 省份节点，包含属性：name（省份名称）、code（简称）
           - City：省会城市 包含属性: name（省会名称）
           - ScenicSpot：景点名称  包含属性: name（景点名称）
           - HistoricalFigure: 事件/典故，包含属性：name（事件/典故）
           - Event：历史事件，包含属性：name（事件名称）
           - Year：发生年份，包含属性：years（事件年份）

        2. 关系类型：
           - CAPITAL: (p1)-[:CAPITAL]->(c1) 表示p1的省会是c1
           - HAS_SPOT: (c1)-[:HAS_SPOT]->(s1) 表示c1的景点是s1
           - RELATED_TO: (s1)-[:RELATED_TO]->(h1) 表示s1的历史典故是h1
           - INVOLVED_IN: (h1)-[:INVOLVED_IN {years: ['1919年', '1949年']}]->(e1) 表示h1历史典故的发生时间是e1
           

        要求：
        1. 分析用户查询，理解其意图
        2. 根据图数据库结构生成正确的Cypher查询语句,注意要使用模糊查询，比如用户输入北京，要能匹配到北京市的省和市，输入长沙会战，需要模糊匹配HistoricalFigure和Event两个字段。
        3. 只能用我给你的关系和节点字段生成SQL，并确保Cypher语句语法正确
        4. 只返回Cypher查询语句，不需要其他任何内容
        5. 如果查询涉及多个节点，使用适当的关系查询
        """

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"用户查询：{query}"}
        ]

        try:
            # 获取或创建模型客户端
            client = self.generator._get_or_create_client(model_id, model, api_key, base_url)
            
            response = await client.chat.completions.create(
                model=model or "gpt-3.5-turbo",
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
            raise

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
                return [
                    {"province": {"name": "江苏省", "capital": "南京"},
                     "stories": [{"name": "金陵十二钗", "time": "清代", "description": "《红楼梦》中的经典典故"}]}
                ]
            
            # 执行Cypher查询
            with self.neo4j_driver.session() as session:
                result = session.run(cypher)
                results = [record.data() for record in result]
            
            logger.info(f"[RAG] Cypher executed successfully, {len(results)} rows returned")
            return results
        except Exception as e:
            logger.error(f"Cypher execution failed: {e}")
            # 失败时返回模拟数据
            return [
                {"province": {"name": "江苏省", "capital": "南京"},
                 "stories": [{"name": "金陵十二钗", "time": "清代", "description": "《红楼梦》中的经典典故"}]}
            ]

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
            logger.info(f"[RAG] Starting - query='{query[:50]}...', kb_ids={kb_ids}")

            # ── 新增：意图检测 ──
            intent = await self._detect_query_intent(
                query=query,
                model=model,
                api_key=api_key,
                base_url=base_url,
                model_id=model_id
            )
            
            # 如果是数据库查询意图
            if intent == 'database' and pm_db:
                logger.info(f"[RAG] Database query intent detected")
                try:
                    # 生成SQL查询
                    sql = await self._generate_sql_query(
                        query=query,
                        model=model,
                        api_key=api_key,
                        base_url=base_url,
                        model_id=model_id
                    )
                    
                    # 执行SQL查询
                    results = await self._execute_sql_query(sql,pm_db)
                    
                    # 将查询结果传递给大模型进行总结
                    system_prompt = f"""你是一个专业的数据分析助手，负责根据数据库查询结果回答用户的问题。
                    请基于以下查询结果，用自然、友好的语言回答用户的问题：
                    查询结果：
                    {results}
                    作答规则：
                     - 仅基于用户提供的【参考信息】整理回答问题；
                    - 仔细阅读参考信息中的内容，确保能够理解并提取相关信息；
                    - 【关键】在回答前，先判断参考信息是否包含与问题直接相关的内容：
                      * 如果问题问的是 A，但参考信息只提到 B（即使 A 和 B 很相似），也属于"无相关内容"；
                      * 例如：问题问"歌王"，但参考信息只有"歌后"，属于无相关内容；
                      * 例如：问题问"张三的成绩"，但参考信息只有"李四的成绩"，属于无相关内容；
                    - 若参考信息中包含与问题直接相关的内容，必须基于这些内容生成回答；
                    - 若参考信息中无相关内容或只有相似内容，必须回复："根据提供的信息，未检索到相关内容"；
                    - 禁止编造、推测或使用外部知识（包括基于相似概念的推断）；
                    - 回答中不要包含任何参考信息的引用，不要显示推理过程，直接给出答案即可；
                    - 回答需简洁、准确、有条理；
                    """
                    
                    messages = [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": query}
                    ]
                    
                    # 获取或创建模型客户端
                    client = self.generator._get_or_create_client(model_id, model, api_key, base_url)
                    
                    response = await client.chat.completions.create(
                        model=model or "gpt-3.5-turbo",
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
                    pass
            # 如果是图数据库查询意图
            elif intent == 'graph_database':
                logger.info(f"[RAG] Graph database query intent detected")
                try:
                    # 生成Cypher查询
                    cypher = await self._generate_cypher_query(
                        query=query,
                        model=model,
                        api_key=api_key,
                        base_url=base_url,
                        model_id=model_id
                    )
                    
                    # 执行Cypher查询
                    results = await self._execute_cypher_query(cypher)
                    
                    # 将查询结果传递给大模型进行总结
                    system_prompt = f"""你是一个专业的数据分析助手，负责根据图数据库查询结果回答用户的问题。
                    请基于以下查询结果，用自然、友好的语言回答用户的问题：
                    查询结果：
                    {results}
                    作答规则：
                     - 仅基于用户提供的【参考信息】整理回答问题；
                    - 仔细阅读参考信息中的内容，确保能够理解并提取相关信息；
                    - 【关键】在回答前，先判断参考信息是否包含与问题直接相关的内容：
                      * 如果问题问的是 A，但参考信息只提到 B（即使 A 和 B 很相似），也属于"无相关内容"；
                      * 例如：问题问"歌王"，但参考信息只有"歌后"，属于无相关内容；
                      * 例如：问题问"张三的成绩"，但参考信息只有"李四的成绩"，属于无相关内容；
                    - 若参考信息中包含与问题直接相关的内容，必须基于这些内容生成回答；
                    - 若参考信息中无相关内容或只有相似内容，必须回复："根据提供的信息，未检索到相关内容"；
                    - 禁止编造、推测或使用外部知识（包括基于相似概念的推断）；
                    - 回答中不要包含任何参考信息的引用，不要显示推理过程，直接给出答案即可；
                    - 回答需简洁、准确、有条理；
                    """
                    
                    messages = [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": query}
                    ]
                    
                    # 获取或创建模型客户端
                    client = self.generator._get_or_create_client(model_id, model, api_key, base_url)
                    
                    response = await client.chat.completions.create(
                        model=model or "gpt-3.5-turbo",
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
                    pass

            # ── Stage 1: 查询改写 ──
            processed_query = query
            if settings.ENABLE_QUERY_REWRITE:
                logger.info(f"[RAG] Stage 1: Query Rewriting")
                processed_query, expanded_queries = await self._rewrite_query_with_llm(
                    query=query,
                    domain=domain,
                    model=model,
                    api_key=api_key,
                    model_id=model_id
                )
            else:
                expanded_queries = []

            # ── 新增：权限前置检查 ──
            authorized_doc_ids = None
            authorized_kb_ids = None
            if db and user:
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
                    # 2. 知识库所有者
                    # if kb.owner_id == user.id:
                    #     # 获取该知识库下所有文档
                    #     doc_result = await db.execute(
                    #         select(Document.id).where(
                    #             (Document.kb_id == kb.id) &
                    #             (Document.is_deleted == False)
                    #         )
                    #     )
                    #     for doc_id in doc_result.scalars().all():
                    #         authorized_doc_ids.add(doc_id)
                    # elif user.role_id:
                    #     # 3. 通过角色授权的知识库
                    #     kb_role_result = await db.execute(
                    #         select(KnowledgeBaseRole).where(
                    #             (KnowledgeBaseRole.kb_id == kb.id) &
                    #             (KnowledgeBaseRole.role_id == user.role_id) &
                    #             (KnowledgeBaseRole.is_deleted == False)
                    #         )
                    #     )
                    #     if kb_role_result.scalar_one_or_none():
                    #         # 有知识库权限，获取所有文档
                    #         doc_result = await db.execute(
                    #             select(Document.id).where(
                    #                 (Document.kb_id == kb.id) &
                    #                 (Document.is_deleted == False)
                    #             )
                    #         )
                    #         for doc_id in doc_result.scalars().all():
                    #             authorized_doc_ids.add(doc_id)
                    #     else:
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
                authorized_doc_ids = list(authorized_doc_ids) if authorized_doc_ids else None

            # ── Stage 2: 检索 ──
            logger.info(f"[RAG] Stage 2: Retrieval - query='{processed_query[:50]}', domain={domain}")
            retrieved = await self.retriever.retrieve(
                query=processed_query,
                kb_ids=list(authorized_kb_ids),
                top_k=settings.RETRIEVAL_TOP_K,
                mode=retrieval_mode,
                domain=domain,
                doc_ids=authorized_doc_ids,
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
                return GenerationResult(
                    answer="\n".join(results),
                    confidence=0.0,
                    citations=[],
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
        db: AsyncSession = None,
    ):
        """流式 RAG"""
        top_k = top_k or settings.RERANK_TOP_K

        # ── 新增：意图检测 ──
        intent = await self._detect_query_intent(
            query=query,
            model=model,
            api_key=api_key,
            base_url=None,
            model_id=model_id
        )
        
        # 如果是数据库查询意图
        if intent == 'database' and db:
            logger.info(f"[RAG Stream] Database query intent detected")
            try:
                # 生成SQL查询
                sql = await self._generate_sql_query(
                    query=query,
                    model=model,
                    api_key=api_key,
                    base_url=None,
                    model_id=model_id
                )
                
                # 执行SQL查询
                results = await self._execute_sql_query(sql)
                
                # 将查询结果传递给大模型进行流式总结
                system_prompt = f"""你是一个专业的数据分析助手，负责根据数据库查询结果回答用户的问题。

                请基于以下查询结果，用自然、友好的语言回答用户的问题：
                
                查询结果：
                {results}
                """
                
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query}
                ]
                
                # 获取或创建模型客户端
                client = self.generator._get_or_create_client(model_id, model, api_key, None)
                
                # 流式生成
                async for chunk in client.chat.completions.create(
                    model=model or "gpt-3.5-turbo",
                    messages=messages,
                    temperature=temperature or 0.7,
                    max_tokens=1000,
                    stream=True
                ):
                    if chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content
                return
            except Exception as e:
                logger.error(f"Database query failed: {e}")
                # 失败时回退到知识库查询
                pass
        # 如果是图数据库查询意图
        elif intent == 'graph_database':
            logger.info(f"[RAG Stream] Graph database query intent detected")
            try:
                # 生成Cypher查询
                cypher = await self._generate_cypher_query(
                    query=query,
                    model=model,
                    api_key=api_key,
                    base_url=None,
                    model_id=model_id
                )
                
                # 执行Cypher查询
                results = await self._execute_cypher_query(cypher)
                
                # 将查询结果传递给大模型进行流式总结
                system_prompt = f"""你是一个专业的数据分析助手，负责根据图数据库查询结果回答用户的问题。

                请基于以下查询结果，用自然、友好的语言回答用户的问题：
                
                查询结果：
                {results}
                """
                
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query}
                ]
                
                # 获取或创建模型客户端
                client = self.generator._get_or_create_client(model_id, model, api_key, None)
                
                # 流式生成
                async for chunk in client.chat.completions.create(
                    model=model or "gpt-3.5-turbo",
                    messages=messages,
                    temperature=temperature or 0.7,
                    max_tokens=1000,
                    stream=True
                ):
                    if chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content
                return
            except Exception as e:
                logger.error(f"Graph database query failed: {e}")
                # 失败时回退到知识库查询
                pass

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