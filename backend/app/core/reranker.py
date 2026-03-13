"""
SmartRAG 重排序器
支持: LLM-based Reranking / Cross-Encoder (本地)
"""
"""
SmartRAG 重排序器
支持：Qwen Rerank API / LLM-based Reranking
"""
from typing import List, Optional
import httpx
from openai import AsyncOpenAI
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.core.retriever import RetrievalResult
from backend.app.config import get_settings
from backend.app.models.model import Model

settings = get_settings()


class Reranker:
    """重排序器"""

    def __init__(self, api_key=None, base_url=None, model_name=None, rerank_model=None, db: AsyncSession = None):
        self.rerank_config = None

        # 如果提供了 rerank_model，使用它的配置
        if rerank_model:
            self.rerank_config = rerank_model
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

        # 初始化 OpenAI client 用于 LLM-based rerank
        if self.rerank_config and self.rerank_config.api_key:
            self.client = AsyncOpenAI(
                api_key=self.rerank_config.api_key,
                base_url=self.rerank_config.base_url,
                timeout=120.0
            )
            self.model_name = self.rerank_config.model
        else:
            self.client = None
            self.model_name = None

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
            reranked = await self._cross_encoder_rerank(query, results, top_k)
            return reranked
        except Exception as e:
            logger.error(f"Cross-Encoder rerank 失败：{e}")
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
            documents = [r.content for r in results[:15]]

            # 调用 Qwen Rerank API
            response_data = await self._call_qwen_rerank_api(query, documents)

            # 解析结果
            scores = []
            for result_item in response_data.get("results", []):
                index = result_item.get("index", 0)
                score = result_item.get("relevance_score", 0)
                scores.append((index, score))

            # 按原始索引顺序排列分数
            ordered_scores = [0] * len(documents)
            for idx, score in scores:
                if idx < len(ordered_scores):
                    ordered_scores[idx] = score

            logger.info(f"Qwen Rerank 完成，前 5 个分数：{ordered_scores[:5]}")

            # 合并分数
            scored_results = []
            for i, result in enumerate(results[:15]):
                if i < len(ordered_scores):
                    rerank_score = float(ordered_scores[i])
                else:
                    rerank_score = result.score

                combined = 0.3 * result.score + 0.7 * rerank_score
                result.score = combined
                scored_results.append(result)

            scored_results.sort(key=lambda x: x.score, reverse=True)
            return scored_results[:top_k]

        except httpx.HTTPStatusError as e:
            logger.error(f"Qwen Rerank API HTTP 错误：{e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Qwen Rerank 失败：{e}")
            raise

    async def _call_qwen_rerank_api(self, query: str, documents: List[str]) -> dict:
        """调用 Qwen (DashScope) Rerank API"""
        # DashScope API 地址 - 正确的路径
        dashscope_api_url = "https://dashscope.aliyuncs.com/api/v1/services/rerank/text-rerank/text-rerank"

        headers = {
            "Authorization": f"Bearer {self.rerank_config.api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": self.rerank_config.model or "gte-rerank-v2",
            "input": {
                "query": query,
                "documents": documents
            },
            "parameters": {
                "return_documents": True,
                "top_n": len(documents)
            }
        }

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(dashscope_api_url, json=data, headers=headers)
            response.raise_for_status()
            return response.json()

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

        prompt = f"""请评估以下文档与用户查询的相关性。
            对每个文档给出 0-10 的相关性分数（10=完全相关, 0=完全无关）。
            
            用户查询: {query}
            
            候选文档:
            {docs_text}
            
            请严格按以下 JSON 格式输出（仅输出 JSON，无其他内容）:
            {{"scores": [score1, score2, ...]}}"""

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