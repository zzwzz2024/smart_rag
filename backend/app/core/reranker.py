"""
SmartRAG 重排序器
支持：Qwen Rerank API / LLM-based Reranking / 多厂商支持
"""
from typing import List, Optional, Dict, Any
import httpx
from openai import AsyncOpenAI
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.core.retriever import RetrievalResult
from backend.app.config import get_settings
from backend.app.models.model import Model
from backend.app.core.base_reranker import BaseReranker
from backend.app.core.rerank_models import QwenReranker, ZhipuReranker, DeepSeekReranker, GPTReranker

settings = get_settings()


def get_reranker_by_provider(provider: str, api_key: str, model_name: str, **kwargs) -> BaseReranker:
    """Get reranker by provider"""
    provider_map = {
        "qwen": QwenReranker,
        "zhipu": ZhipuReranker,
        "deepseek": DeepSeekReranker,
        "gpt": GPTReranker,
        "openai": GPTReranker
    }
    
    provider_lower = provider.lower()
    reranker_class = provider_map.get(provider_lower)
    
    if not reranker_class:
        raise ValueError(f"Unsupported rerank provider: {provider}")
    
    return reranker_class(api_key=api_key, model_name=model_name, **kwargs)


class Reranker:
    """重排序器"""

    def _infer_provider(self, model_name: str) -> str:
        """从模型名称中推断provider"""
        model_name_lower = model_name.lower()
        if "qwen" in model_name_lower:
            return "qwen"
        elif "zhipu" in model_name_lower or "glm" in model_name_lower:
            return "zhipu"
        elif "deepseek" in model_name_lower:
            return "deepseek"
        elif "gpt" in model_name_lower or "openai" in model_name_lower:
            return "gpt"
        return None

    def __init__(self, api_key=None, base_url=None, model_name=None, rerank_model=None, db: AsyncSession = None, provider=None):
        self.rerank_config = None
        self.provider = provider
        self.api_key = api_key or settings.DEFAULT_API_KEY

        # 如果提供了 rerank_model，使用它的配置
        if rerank_model:
            self.rerank_config = rerank_model
            # 从模型配置中提取provider信息
            if not self.provider:
                self.provider = self._infer_provider(rerank_model.model)
        elif db is not None:
            result = db.execute(
                select(Model).where(
                    Model.type == "rerank",
                    Model.is_active == True
                ).limit(1)
            )
            rerank_model_from_db = result.scalar_one_or_none()

            if rerank_model_from_db:
                logger.info(f"从数据库加载 rerank 模型：{rerank_model_from_db.name}")
                self.rerank_config = rerank_model_from_db
                # 从模型配置中提取provider信息
                if not self.provider:
                    self.provider = self._infer_provider(rerank_model_from_db.model)

        # 初始化 OpenAI client 用于 LLM-based rerank
        if self.rerank_config and self.rerank_config.api_key:
            self.client = AsyncOpenAI(
                api_key=self.rerank_config.api_key,
                base_url=self.rerank_config.base_url or settings.DEFAULT_BASE_URL,
                timeout=120.0
            )
            self.model_name = self.rerank_config.model
        elif self.api_key:
            self.client = AsyncOpenAI(
                api_key=self.api_key,
                base_url=base_url or settings.DEFAULT_BASE_URL,
                timeout=120.0
            )
            self.model_name = model_name or settings.DEFAULT_RERANK_MODEL
        else:
            self.client = None
            self.model_name = model_name or settings.DEFAULT_RERANK_MODEL

        # 初始化厂商特定的reranker
        self.provider_reranker = None
        if (self.rerank_config and self.rerank_config.api_key) or self.api_key:
            if not self.provider:
                # 从模型名称推断provider
                model_to_use = self.rerank_config.model if self.rerank_config else self.model_name
                self.provider = self._infer_provider(model_to_use)
            
            if self.provider:
                try:
                    api_key_to_use = self.rerank_config.api_key if self.rerank_config else self.api_key
                    model_to_use = self.rerank_config.model if self.rerank_config else self.model_name
                    self.provider_reranker = get_reranker_by_provider(
                        provider=self.provider,
                        api_key=api_key_to_use,
                        model_name=model_to_use
                    )
                    logger.info(f"初始化 {self.provider} rerank 模型：{model_to_use}")
                except Exception as e:
                    logger.error(f"初始化厂商rerank模型失败：{e}")
                    self.provider_reranker = None

    async def rerank(
            self,
            query: str,
            results: List[RetrievalResult],
            top_k: int = 5,
    ) -> List[RetrievalResult]:
        """
        使用 Cross-Encoder 模型进行 rerank
        """
        if len(results) <= 1:
            return results

        if len(results) <= 3:
            return results

        try:
            # 优先使用厂商特定的reranker
            if self.provider_reranker:
                logger.info(f"使用 {self.provider} rerank 模型")
                reranked = await self._provider_rerank(query, results, top_k)
                return reranked
            else:
                # 回退到原来的Qwen rerank
                reranked = await self._cross_encoder_rerank(query, results, top_k)
                return reranked
        except Exception as e:
            logger.error(f"厂商rerank失败：{e}")
            try:
                logger.info("降级到 LLM-based rerank")
                return await self._llm_rerank(query, results, top_k)
            except Exception as llm_e:
                logger.error(f"LLM-based rerank 也失败：{llm_e}")
                logger.warning("所有 rerank 方法都失败，返回原始结果")
                return results[:top_k]

    async def _cross_encoder_rerank(
            self,
            query: str,
            results: List[RetrievalResult],
            top_k: int,
    ) -> List[RetrievalResult]:
        """使用 Qwen Rerank API 进行 rerank"""
        if not self.rerank_config:
            raise ValueError("未配置 rerank 模型")

        try:
            # 创建Qwen reranker实例
            qwen_reranker = QwenReranker(
                api_key=self.rerank_config.api_key,
                model_name=self.rerank_config.model
            )

            documents = [r.content for r in results[:15]]
            reranked_docs = await qwen_reranker.rerank(query, documents, top_k=len(documents))

            # 构建分数映射
            score_map = {}
            for doc in reranked_docs:
                score_map[doc.get("index")] = doc.get("score", 0)

            logger.info(f"Qwen Rerank 完成，前 5 个分数：{list(score_map.values())[:5]}")

            # 合并分数
            scored_results = []
            for i, result in enumerate(results[:15]):
                rerank_score = score_map.get(i, result.score)
                combined = 0.3 * result.score + 0.7 * rerank_score
                result.score = combined
                scored_results.append(result)

            scored_results.sort(key=lambda x: x.score, reverse=True)
            return scored_results[:top_k]

        except Exception as e:
            logger.error(f"Qwen Rerank 失败：{e}")
            raise

    async def _provider_rerank(
            self,
            query: str,
            results: List[RetrievalResult],
            top_k: int,
    ) -> List[RetrievalResult]:
        """使用厂商特定的rerank模型进行重排序"""
        if not self.provider_reranker:
            raise ValueError("未初始化厂商rerank模型")

        try:
            documents = [r.content for r in results[:15]]

            # 调用厂商特定的rerank模型
            reranked_docs = await self.provider_reranker.rerank(query, documents, top_k=len(documents))

            # 构建分数映射
            score_map = {}
            for doc in reranked_docs:
                score_map[doc.get("index")] = doc.get("score", 0)

            logger.info(f"{self.provider} Rerank 完成，前 5 个分数：{list(score_map.values())[:5]}")

            # 合并分数
            scored_results = []
            for i, result in enumerate(results[:15]):
                rerank_score = score_map.get(i, result.score)
                combined = 0.3 * result.score + 0.7 * rerank_score
                result.score = combined
                scored_results.append(result)

            scored_results.sort(key=lambda x: x.score, reverse=True)
            return scored_results[:top_k]

        except Exception as e:
            logger.error(f"厂商rerank失败：{e}")
            raise

    async def _llm_rerank(
            self,
            query: str,
            results: List[RetrievalResult],
            top_k: int,
    ) -> List[RetrievalResult]:
        """LLM-based 重排序（降级方案）"""
        if not self.client:
            logger.warning("未初始化 LLM client，返回原始结果")
            return results[:top_k]
        """LLM-based 重排序"""

        # 构造评分 prompt
        docs_text = ""
        for i, r in enumerate(results[:15]):  # 最多评估15个
            docs_text += f"\n[文档{i + 1}]: {r.content[:300]}\n"

        from backend.app.core.prompts import RERANKER_PROMPT
        prompt = RERANKER_PROMPT.format(query=query, doc=docs_text)

        # 使用 chat API（不需要 documents 参数）
        response = await self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],  # ← 只需要 messages
            temperature=0,
            max_tokens=200,
        )

        # 解析分数
        import json
        try:
            content = response.choices[0].message.content.strip()
            # 提取 JSON
            if "```" in content:
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
            scores_data = json.loads(content)
            scores = scores_data.get("scores", [])
        except (json.JSONDecodeError, KeyError):
            logger.warning("Failed to parse reranker scores")
            return results[:top_k]

        # 合并分数并重排
        scored_results = []
        for i, result in enumerate(results[:15]):
            if i < len(scores):
                rerank_score = float(scores[i]) / 10.0
            else:
                rerank_score = result.score
            # 综合初始分数和重排分数
            combined = 0.3 * result.score + 0.7 * rerank_score
            result.score = combined
            scored_results.append(result)

        scored_results.sort(key=lambda x: x.score, reverse=True)
        return scored_results[:top_k]
