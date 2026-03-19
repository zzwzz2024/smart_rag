from typing import List, Dict, Any


class BaseReranker:
    """Base reranker class"""
    
    def __init__(self, model_name: str):
        """Initialize reranker"""
        self.model_name = model_name
    
    async def rerank(
        self, 
        query: str, 
        documents: List[str], 
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """Rerank documents"""
        raise NotImplementedError("Subclass must implement rerank method")
