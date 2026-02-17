"""
SmartRAG Embedding 服务
支持: OpenAI API / 本地 Sentence-Transformers
"""
import numpy as np
from typing import List
from loguru import logger
from openai import OpenAI
from backend.app.config import get_settings
settings = get_settings()


class EmbeddingService:
    """向量化服务 - 单例模式"""

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self,api_key=None,base_url=None,model_name=None):
        if self._initialized:
            return
        self._initialized = False

        if settings.USE_LOCAL_EMBEDDING:
            self._init_local_model()
        else:
            self._init_openai_client(api_key,base_url,model_name)

    def _init_openai_client(self,api_key=None,base_url=None,model_name=None):
        """初始化 OpenAI Embedding 客户端"""
        # from openai import OpenAI
        logger.info(f"_init_openai_client")
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url,
            timeout = 120.0
        )
        self.model = settings.EMBEDDING_MODEL
        self.is_local = False
        logger.info(f"Embedding service initialized (OpenAI: {self.model})")

    def _init_local_model(self):
        """初始化本地 Embedding 模型"""
        from sentence_transformers import SentenceTransformer
        self.local_model = SentenceTransformer(settings.LOCAL_EMBEDDING_MODEL)
        self.is_local = True
        logger.info(
            f"Embedding service initialized (Local: {settings.LOCAL_EMBEDDING_MODEL})"
        )

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """批量生成向量"""
        if not texts:
            return []

        # 清洗空文本
        texts = [t if t.strip() else " " for t in texts]

        if self.is_local:
            return self._embed_local(texts)
        else:
            return self._embed_openai(texts)

    def embed_query(self, query: str) -> List[float]:
        """查询向量化"""
        result = self.embed_texts([query])
        return result[0] if result else []

    def _embed_openai(self, texts: List[str]) -> List[List[float]]:
        """使用 OpenAI API"""
        logger.info(f"_embed_openai开始")
        all_embeddings = []
        batch_size = 50

        for i in range(0, len(texts), batch_size):
            batch = texts[i: i + batch_size]
            response = self.client.embeddings.create(
                model=self.model,
                input=batch,
            )
            embeddings = [item.embedding for item in response.data]
            all_embeddings.extend(embeddings)

        logger.info(f"_embed_openai完成")
        return all_embeddings

    def _embed_local(self, texts: List[str]) -> List[List[float]]:
        """使用本地模型"""
        embeddings = self.local_model.encode(
            texts,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        return embeddings.tolist()