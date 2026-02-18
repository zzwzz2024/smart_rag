"""
SmartRAG 内容生成器
支持: LLM-based 生成 & 结构化输出解析
"""
import time
from typing import List, Optional, Dict, AsyncGenerator
from dataclasses import dataclass
from openai import OpenAI
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
        self.default_client = OpenAI(
            api_key=api_key,
            base_url=base_url,
            timeout=120.0
        )
        print(f"Generator函数初始化完成")

    def _get_or_create_client(self, model_id: Optional[str] = None, model: Optional[str] = None, api_key: Optional[str] = None, base_url: Optional[str] = None) -> OpenAI:
        """
        获取或创建对应模型的客户端
        """
        # 使用model_id作为客户端的键
        client_key = model_id or model or "default"
        
        if client_key not in self.clients:
            # 只使用传递的api_key，不再使用默认api_key
            if not api_key:
                raise ValueError("API key is required for model client creation")
            # 只使用传递的base_url
            if not base_url:
                raise ValueError("Base URL is required for model client creation")
            # 这里可以根据model_id从数据库获取模型配置
            # 例如，获取模型的base_url等
            self.clients[client_key] = OpenAI(
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
    - 仅基于用户提供的【参考信息】回答问题；
    - 若参考信息中无相关内容，必须回复：“根据提供的信息，未检索到相关内容”；
    - 禁止编造、推测或使用外部知识；
    - 引用时请注明“参考信息 X”；
    - 回答需简洁、准确、有条理。"""

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
    ) -> GenerationResult:
        """
        生成答案
        """
        start_time = time.time()

        if not model:
            raise ValueError("Model is required for generation")
        temperature = temperature or settings.LLM_TEMPERATURE

        # 构造上下文
        context = self._build_context(retrieved_chunks)

        # 构造消息历史
        messages = self._build_messages(query, context, conversation_history or [])

        try:
            # 获取或创建对应模型的客户端
            client = self._get_or_create_client(model_id, model, api_key, base_url)
            
            response = client.chat.completions.create(
                model=model,
                messages= self._build_messages(query, context, conversation_history or []),
                temperature=temperature,
                max_tokens=settings.LLM_MAX_TOKENS,
            )

            answer = response.choices[0].message.content
            response_time = time.time() - start_time

            # 计算置信度 (基于检索结果的数量和质量)
            confidence = self._calculate_confidence(retrieved_chunks)

            # 构建引用
            citations = self._build_citations(retrieved_chunks)

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
        for chunk in retrieved_chunks:
            context_parts.append(f"参考信息 {chunk.chunk_id}:\n{chunk.content}\n---")

        return "\n".join(context_parts)

    def _calculate_confidence(self, retrieved_chunks: List[RetrievalResult]) -> float:
        """计算置信度"""
        if not retrieved_chunks:
            return 0.3  # 无参考信息的置信度较低

        # 基于检索结果的数量和平均分数计算置信度
        avg_score = sum(r.score for r in retrieved_chunks) / len(retrieved_chunks)
        count_factor = min(len(retrieved_chunks) / 5.0, 1.0)  # 最多5个结果为满分

        confidence = (avg_score * 0.7 + count_factor * 0.3)
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
            
            stream = client.chat.completions.create(
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
