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

    def __init__(self):
        self.client = OpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL,
        )

    async def generate(
        self,
        query: str,
        retrieved_chunks: List[RetrievalResult],
        conversation_history: List[dict] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
    ) -> GenerationResult:
        """
        生成答案
        """
        start_time = time.time()

        model = model or settings.LLM_MODEL
        temperature = temperature or settings.LLM_TEMPERATURE

        # 构造上下文
        context = self._build_context(retrieved_chunks)

        # 构造消息历史
        messages = self._build_messages(query, context, conversation_history or [])

        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
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

    def _build_messages(
        self,
        query: str,
        context: str,
        conversation_history: List[dict]
    ) -> List[dict]:
        """构建消息历史"""
        system_prompt = f"""你是一个智能问答助手，基于提供的参考信息回答用户问题。
        - 如果参考信息中包含相关内容，请基于参考信息回答
        - 如果参考信息不足以回答，请说明信息不足
        - 引用参考信息中的内容时，请标注来源
        - 保持回答准确、简洁、有条理
        """

        messages = [{"role": "system", "content": system_prompt}]

        # 添加历史对话（限制长度避免超出上下文窗口）
        if conversation_history:
            # 只保留最近的几轮对话
            recent_history = conversation_history[-4:]  # 最多保留4轮对话
            messages.extend(recent_history)

        # 添加当前查询和上下文
        if context:
            user_content = f"参考信息:\n{context}\n\n问题: {query}"
        else:
            user_content = f"问题: {query}"

        messages.append({"role": "user", "content": user_content})

        return messages

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
            stream = self.client.chat.completions.create(
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
