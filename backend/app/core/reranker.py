"""
SmartRAG 重排序器
支持: LLM-based Reranking / Cross-Encoder (本地)
"""
from typing import List
from openai import OpenAI
from loguru import logger
from backend.app.core.retriever import RetrievalResult
from backend.app.config import get_settings

settings = get_settings()


class Reranker:
    """重排序器"""

    def __init__(self,api_key=None,base_url=None,model_name=None):
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url,
            timeout = 120.0
        )

    async def rerank(
        self,
        query: str,
        results: List[RetrievalResult],
        top_k: int = 5,
    ) -> List[RetrievalResult]:
        """
        使用 LLM 对检索结果进行相关性重排序
        生产环境建议使用专用 Cross-Encoder 模型 (bce-reranker / bge-reranker)
        """
        if len(results) <= top_k:
            return results

        if len(results) <= 3:
            return results

        try:
            reranked = await self._llm_rerank(query, results, top_k)
            return reranked
        except Exception as e:
            logger.error(f"Reranking failed, falling back to original order: {e}")
            return results[:top_k]

    async def _llm_rerank(
        self,
        query: str,
        results: List[RetrievalResult],
        top_k: int,
    ) -> List[RetrievalResult]:
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

        response = self.client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
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
            scored_results.backend.append(result)

        scored_results.sort(key=lambda x: x.score, reverse=True)
        return scored_results[:top_k]