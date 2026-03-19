from typing import List, Dict, Any
import httpx
from loguru import logger
from ..base_reranker import BaseReranker


class QwenReranker(BaseReranker):
    """Qwen rerank model implementation"""
    
    def __init__(self, api_key: str, model_name: str = "qwen-rerank", **kwargs):
        """Initialize Qwen reranker"""
        super().__init__(model_name)
        self.api_key = api_key
        self.model_name = model_name
        self.kwargs = kwargs
    
    async def rerank(
        self, 
        query: str, 
        documents: List[str], 
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """Rerank documents using Qwen"""
        try:
            # 调用Qwen Rerank API
            response_data = await self._call_qwen_rerank_api(query, documents)
            
            # 解析结果
            reranked_docs = []
            for result_item in response_data.get("results", []):
                index = result_item.get("index", 0)
                score = result_item.get("relevance_score", 0)
                reranked_docs.append({
                    "content": documents[index] if index < len(documents) else "",
                    "score": score,
                    "index": index
                })
            
            # Sort by score and return top_k
            reranked_docs.sort(key=lambda x: x["score"], reverse=True)
            return reranked_docs[:top_k]
        except Exception as e:
            logger.error(f"Qwen Rerank 失败：{e}")
            # 回退到模拟实现
            return self._fallback_rerank(query, documents, top_k)
    
    async def _call_qwen_rerank_api(self, query: str, documents: List[str]) -> dict:
        """调用 Qwen (DashScope) Rerank API"""
        # DashScope API 地址 - 正确的路径
        dashscope_api_url = "https://dashscope.aliyuncs.com/api/v1/services/rerank/text-rerank/text-rerank"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": self.model_name or "gte-rerank-v2",
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
    
    def _fallback_rerank(
        self, 
        query: str, 
        documents: List[str], 
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """回退到模拟实现"""
        logger.info("Qwen Rerank 失败，使用回退实现")
        reranked_docs = []
        for i, doc in enumerate(documents):
            # Simulate reranking score
            score = 1.0 / (i + 1)
            reranked_docs.append({
                "content": doc,
                "score": score,
                "index": i
            })
        
        # Sort by score and return top_k
        reranked_docs.sort(key=lambda x: x["score"], reverse=True)
        return reranked_docs[:top_k]
