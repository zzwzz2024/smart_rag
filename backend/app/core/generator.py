"""
SmartRAG 内容生成器
支持: LLM-based 生成 & 结构化输出解析
"""
import time
from typing import List, Optional, Dict, AsyncGenerator
from dataclasses import dataclass
from openai import AsyncOpenAI
from loguru import logger

from backend.app.core.retriever import RetrievalResult
from backend.app.config import get_settings

settings = get_settings()

@dataclass
class GenerationResult:
    """生成结果"""
    answer: str
    confidence: float
    citations: List[Dict]  # [{"chunk_id": "...", "content": "...", "score": 0.x}]
    response_time: float
    token_usage: Dict[str, int]  # {"prompt": x, "completion": y, "total": z, "response_time": sec}


class Generator:
    """内容生成器"""

    def __init__(self,api_key=None,base_url=None,model_name=None):
        self.clients = {}  # 存储不同模型的客户端
        print(f"Generator函数初始化")
        # 只有当api_key和base_url都不为None时，才创建默认客户端
        if api_key and base_url:
            self.default_client = AsyncOpenAI(
                api_key=api_key,
                base_url=base_url,
                timeout=120.0
            )
        else:
            self.default_client = None
        print(f"Generator函数初始化完成")

    def _get_or_create_client(self, model_id: Optional[str] = None,
                              model: Optional[str] = None, api_key: Optional[str] = None,
                              base_url: Optional[str] = None) -> AsyncOpenAI:
        """
        获取或创建对应模型的客户端
        """
        # 使用model_id作为客户端的键
        client_key = model_id or model or "default"
        
        if client_key not in self.clients:
            # 如果没有传递api_key和base_url，使用默认客户端
            if not api_key or not base_url:
                if self.default_client:
                    return self.default_client
                else:
                    raise ValueError("API key and base URL are required for model client creation")
            
            # 这里可以根据model_id从数据库获取模型配置
            # 例如，获取模型的base_url等
            self.clients[client_key] = AsyncOpenAI(
                api_key=api_key,
                base_url=base_url,
            )
            logger.info(f"Created new client for model: {client_key}")
        
        logger.info(f"Using client for model: {client_key}")
        return self.clients[client_key]

    def _build_messages(
                self,
                query: str,
                context: str,
                conversation_history: List[dict]
        ) -> List[dict]:
            """构建消息历史"""
            system_prompt = """你是一个严谨的智能问答助手，请严格遵循：
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
            - 如果问你是谁，文档中没有相关内容，必须回复："我是你的智能检索助手"；
            - 对于包含时间、奖项等结构化信息的问题，回答格式要求：
              1. 首先给出总结性回答，使用加粗格式（**内容**），例如："**周杰伦共拿过 6 次新人奖**"；
              2. 然后分点列出具体信息，每个点前面有编号，时间信息使用加粗格式（**时间**），例如："1. **2001 年**：第一届全球华语歌曲排行榜\"最佳新人奖\""；
              3. 最后给出补充说明，使用加粗格式强调重要信息，例如："其中，**明确获奖的新人奖项共 6 项**（第 2 项仅为提名，不计入获奖次数）"；
              4. 严格按照上述格式输出，确保与示例格式完全一致。
            """

            messages = [{"role": "system", "content": system_prompt}]

            # 添加历史对话（限制长度）
            if conversation_history:
                messages.extend(conversation_history[-4:])

            # 将 context 和 query 合并到 user 消息中
            user_content = (
                f"【参考信息】\n{context}\n\n"
                f"【问题】\n{query}"
            )
            messages.append({"role": "user", "content": user_content})

            return messages

    def _build_relevance_check_messages(self, query: str, context: str) -> List[dict]:
            """构建相关性检查消息"""
            system_prompt = """你是一个严格的相关性判断助手。你的任务是判断【参考信息】是否包含与【问题】直接相关的内容。

            判断规则：
            1. 如果问题问的是具体的人/事/物 A，但参考信息只提到 B（即使 A 和 B 很相似），也属于"无相关内容"
            2. 不要做任何推断，只做字面匹配
            3. 如果参考信息中没有直接提到问题中的关键词，回答 "无相关内容"
            4. 如果参考信息中直接提到了问题中的关键词，回答 "有相关内容"
        
            输出格式：
            - 只输出 "有相关内容" 或 "无相关内容"，不要输出任何其他内容
            """

            messages = [{"role": "system", "content": system_prompt}]

            user_content = (
                f"【参考信息】\n{context}\n\n"
                f"【问题】\n{query}\n\n"
                f"请判断："
            )
            messages.append({"role": "user", "content": user_content})

            return messages

    async def generate(
                self,
                query: str,
                retrieved_chunks: List[RetrievalResult],
                conversation_history: List[dict] = None,
                model: Optional[str] = None,
                model_id: Optional[str] = None,
                api_key: Optional[str] = None,
                base_url: Optional[str] = None,
                temperature: Optional[float] = None,
                top_p: Optional[float] = 0.95,
        ) -> GenerationResult:
            """
            生成答案
            """
            start_time = time.time()

            if not model:
                # 如果没有提供模型，使用默认模型
                model = "gpt-3.5-turbo"
            temperature = temperature or 0.7

            # 构造上下文
            context = self._build_context(retrieved_chunks)

            # 构造消息历史
            # messages = self._build_messages(query, context, conversation_history or [])

            try:
                # 获取或创建对应模型的客户端
                client = self._get_or_create_client(model_id, model, api_key, base_url)

                # 第一步：先让模型判断是否有相关内容
                relevance_check_messages = self._build_relevance_check_messages(query, context)
                relevance_response = await client.chat.completions.create(
                    model=model,
                    messages=relevance_check_messages,
                    temperature=0.1,  # 降低温度，让判断更严格
                    max_tokens=50,
                )

                relevance_result = relevance_response.choices[0].message.content.strip().lower()
                # 构建引用（无论是否有相关内容，都返回检索到的 chunks）
                citations = self._build_citations(retrieved_chunks)

                # 如果判断为无相关内容，返回提示但保留引用信息
                if "no" in relevance_result or "无" in relevance_result:
                    response_time = time.time() - start_time
                    return GenerationResult(
                        answer="根据提供的信息，未检索到相关内容",
                        confidence=0.3,
                        citations=citations,
                        response_time=response_time,
                        token_usage={"response_time": round(response_time, 2)},
                    )

                # 第二步：有相关内容，生成答案
                response = await client.chat.completions.create(
                    model=model,
                    messages=self._build_messages(query, context, conversation_history or []),
                    temperature=temperature,
                    top_p=top_p,
                    max_tokens=1000,
                )

                answer = response.choices[0].message.content
                response_time = time.time() - start_time
                logger.info(f"大模型汇总回答Answer: {answer}")

                # 计算置信度 (基于检索结果的数量和质量)
                confidence = self._calculate_confidence(retrieved_chunks)

                # 构建引用
                # citations = self._build_citations(retrieved_chunks)

                token_usage = {
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                    "total": response.usage.total_tokens if response.usage else 0,
                    "response_time": round(response_time, 2),
                }

                return GenerationResult(
                    answer=answer,
                    confidence=confidence,
                    citations=citations,
                    response_time=response_time,
                    token_usage=token_usage,
                )
            except Exception as e:
                logger.error(f"Generation failed: {e}")
                response_time = time.time() - start_time
                return GenerationResult(
                    answer="抱歉，生成答案时出现错误，请稍后再试。",
                    confidence=0.0,
                    citations=[],
                    response_time=response_time,
                    token_usage={"response_time": round(response_time, 2)},
                )

    def _build_context(self, retrieved_chunks: List[RetrievalResult]) -> str:
        """构建上下文"""
        if not retrieved_chunks:
            return ""

        context_parts = []
        for i, chunk in enumerate(retrieved_chunks):
            # 使用知识库名称而不是 ID
            kb_name = chunk.metadata.get("kb_name", "知识库")
            # 确保知识库名称是字符串
            if not isinstance(kb_name, str):
                kb_name = "知识库"
            # 构建详细的参考信息，包含文件名和知识库名称
            filename = chunk.metadata.get("filename", "未知文件")
            context_parts.append(f"参考信息 {kb_name}（{filename}）:\n{chunk.content}\n---")

        return "\n".join(context_parts)

    def _calculate_confidence(self, retrieved_chunks: List[RetrievalResult]) -> float:
        """计算置信度"""
        if not retrieved_chunks:
            return 0.3  # 无参考信息的置信度较低

        # 获取向量分数和BM25分数
        vector_scores = [r.vector_score for r in retrieved_chunks if r.vector_score > 0]
        bm25_scores = [r.bm25_score for r in retrieved_chunks if r.bm25_score > 0]
        
        # 计算平均分数
        if vector_scores and bm25_scores:
            avg_vector_score = sum(vector_scores) / len(vector_scores)
            avg_bm25_score = sum(bm25_scores) / len(bm25_scores)
            # 综合向量和BM25分数
            avg_score = (avg_vector_score * 0.6 + avg_bm25_score * 0.4)
        elif vector_scores:
            avg_score = sum(vector_scores) / len(vector_scores)
        elif bm25_scores:
            avg_score = sum(bm25_scores) / len(bm25_scores)
        else:
            # 使用RRF分数作为兜底
            avg_score = sum(r.score for r in retrieved_chunks) / len(retrieved_chunks)

        # 计算数量因子
        count_factor = min(len(retrieved_chunks) / 3.0, 1.0)  # 最多3个结果为满分，提高权重
        
        # 调整权重，提高分数的影响
        confidence = (avg_score * 0.8 + count_factor * 0.2)
        
        # 对高相关结果给予额外提升
        if avg_score > 0.7:
            confidence = min(confidence * 1.1, 1.0)
        elif avg_score > 0.5:
            confidence = min(confidence * 1.05, 1.0)

        return min(confidence, 1.0)

    def _build_citations(self, retrieved_chunks: List[RetrievalResult]) -> List[Dict]:
        """构建引用"""
        citations = []
        for chunk in retrieved_chunks:
            citations.append({
                "chunk_id": chunk.chunk_id,
                "content": chunk.content[:200],  # 截取前200字符
                "score": round(chunk.score, 3),
            })
        return citations

    async def generate_stream(
        self,
        query: str,
        retrieved_chunks: List[RetrievalResult],
        conversation_history: List[dict] = None,
        model: Optional[str] = None,
        model_id: Optional[str] = None,
        api_key: Optional[str] = None,
        temperature: Optional[float] = None,
    ) -> AsyncGenerator[str, None]:
        """
        流式生成答案
        """
        model = model or settings.LLM_MODEL
        temperature = temperature or settings.LLM_TEMPERATURE

        # 构造上下文
        context = self._build_context(retrieved_chunks)

        # 构造消息
        messages = self._build_messages(query, context, conversation_history or [])

        try:
            # 获取或创建对应模型的客户端
            client = self._get_or_create_client(model_id, model, api_key)
            
            stream = await client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=settings.LLM_MAX_TOKENS,
                stream=True,
            )

            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            logger.error(f"Stream generation failed: {e}")
            yield "抱歉，生成答案时出现错误。"
