"""
SmartRAG Embedding 服务
支持: OpenAI API / 本地 Sentence-Transformers
"""
import numpy as np
from typing import List
from loguru import logger
from openai import AsyncOpenAI
import httpx
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

    def __init__(self,api_key=None,base_url=None,model_name=None, embedding_model=None):
        if self._initialized:
            return
        self._initialized = False

        # 检查是否有有效的API密钥
        has_valid_api_key = False
        if embedding_model and embedding_model.api_key:
            has_valid_api_key = True
        elif api_key:
            has_valid_api_key = True

        # 如果没有有效的API密钥，使用本地模型
        if settings.USE_LOCAL_EMBEDDING or not has_valid_api_key:
            self._init_local_model()
        else:
            # 如果提供了embedding_model，使用它的配置
            if embedding_model:
                self._init_openai_client(embedding_model.api_key, embedding_model.base_url, embedding_model.model)
            else:
                self._init_openai_client(api_key,base_url,model_name)

    def _init_openai_client(self,api_key=None,base_url=None,model_name=None):
        """初始化 OpenAI Embedding 客户端"""
        # from openai import AsyncOpenAI
        logger.info(f"_init_openai_client")
        # 创建自定义的httpx AsyncClient，避免传递proxies参数
        http_client = httpx.AsyncClient(
            timeout=httpx.Timeout(120.0),
            follow_redirects=True
        )
        # 只传递必要的参数
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url,
            http_client=http_client
        )
        self.model = model_name
        self.is_local = False
        logger.info(f"Embedding service initialized (AsyncOpenAI: {self.model})")

    def _init_local_model(self):
        """初始化本地 Embedding 模型"""
        from sentence_transformers import SentenceTransformer
        self.local_model = ""#SentenceTransformer(settings.LOCAL_EMBEDDING_MODEL)
        self.is_local = True
        logger.info(
            f"Embedding service initialized (Local: {settings.LOCAL_EMBEDDING_MODEL})"
        )

    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """批量生成向量"""
        if not texts:
            return []

        # 清洗空文本
        texts = [t if t.strip() else " " for t in texts]

        if self.is_local:
            return self._embed_local(texts)
        else:
            return await self._embed_openai(texts)

    async def embed_query(self, query: str) -> List[float]:
        """查询向量化"""
        result = await self.embed_texts([query])
        return result[0] if result else []

    async def _embed_openai(self, texts: List[str]) -> List[List[float]]:
        """使用 OpenAI API"""
        logger.info(f"_embed_openai开始")
        all_embeddings = []
        batch_size = 25  # API 限制批量大小不能超过 25
        max_length = 2048  # API 限制输入长度不能超过 2048 个 token

        for i in range(0, len(texts), batch_size):
            batch = texts[i: i + batch_size]
            # 限制每个文本的长度
            batch = [text[:max_length] for text in batch]
            response = await self.client.embeddings.create(
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