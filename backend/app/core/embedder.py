"""
SmartRAG Embedding 服务
支持: OpenAI API / 本地 Sentence-Transformers
"""
from typing import List
from loguru import logger
from openai import AsyncOpenAI
import httpx
from backend.app.config import get_settings
settings = get_settings()


class EmbeddingService:

    def __init__(self,api_key=None,base_url=None,model_name=None, embedding_model=None, db=None):
        # 优先从数据库获取默认模型
        if db:
            import asyncio
            from backend.app.utils.model_utils import get_default_model
            try:
                default_model = asyncio.run(get_default_model(db, "embedding"))
                if default_model and default_model.api_key:
                    logger.info(f"使用数据库中的默认 embedding 模型：{default_model.name}")
                    self._init_openai_client(default_model.api_key, default_model.base_url, default_model.model)
                    # 确保至少有一个可用的嵌入模型
                    if not self.is_local and not hasattr(self, 'client'):
                        # 尝试使用本地模型作为最后的备用方案
                        self._init_local_model()
                    return
            except Exception as e:
                logger.error(f"从数据库获取默认模型失败：{e}")

        # 检查是否有有效的API密钥
        has_valid_api_key = False
        if embedding_model and embedding_model.api_key:
            has_valid_api_key = True
            logger.info(f"使用提供的 embedding 模型：{embedding_model.name}，API Key: {embedding_model.api_key[:5]}...")
        elif api_key:
            has_valid_api_key = True
            logger.info(f"使用提供的 API Key: {api_key[:5]}...")
        elif settings.DEFAULT_API_KEY:
            has_valid_api_key = True
            logger.info(f"使用默认 API Key: {settings.DEFAULT_API_KEY[:5]}...")

        # 如果没有有效的API密钥，使用本地模型
        if settings.USE_LOCAL_EMBEDDING or not has_valid_api_key:
            logger.info("没有有效的API密钥，尝试使用本地模型")
            self._init_local_model()
        else:
            # 如果提供了embedding_model，使用它的配置
            if embedding_model:
                logger.info(f"初始化 OpenAI 客户端使用模型：{embedding_model.model}，Base URL: {embedding_model.base_url}")
                self._init_openai_client(embedding_model.api_key, embedding_model.base_url, embedding_model.model)
            else:
                # 使用默认配置
                logger.info(f"初始化 OpenAI 客户端使用默认配置：模型={model_name or settings.DEFAULT_EMBEDDING_MODEL}，Base URL={base_url or settings.DEFAULT_BASE_URL}")
                self._init_openai_client(api_key or settings.DEFAULT_API_KEY, base_url or settings.DEFAULT_BASE_URL, model_name or settings.DEFAULT_EMBEDDING_MODEL)
        
        # 确保至少有一个可用的嵌入模型
        if not self.is_local and not hasattr(self, 'client'):
            # 尝试使用本地模型作为最后的备用方案
            self._init_local_model()

    def _init_openai_client(self,api_key=None,base_url=None,model_name=None):
        """初始化 OpenAI Embedding 客户端"""
        # from openai import AsyncOpenAI
        logger.info(f"_init_openai_client: api_key={api_key[:5]}..." if api_key else "_init_openai_client: api_key=None")
        
        # 检查API密钥是否为空
        if not api_key:
            logger.error("API key is required for OpenAI client initialization")
            self.client = None
            self.model = None
            self.is_local = False
            return
        
        # 检查base_url是否为空
        if not base_url:
            logger.error("Base URL is required for OpenAI client initialization")
            self.client = None
            self.model = None
            self.is_local = False
            return
        
        # 检查model_name是否为空
        if not model_name:
            logger.error("Model name is required for OpenAI client initialization")
            self.client = None
            self.model = None
            self.is_local = False
            return
        
        try:
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
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            self.client = None
            self.model = None
            self.is_local = False

    def _init_local_model(self):
        """初始化本地 Embedding 模型"""
        from sentence_transformers import SentenceTransformer
        logger.info(f"尝试初始化本地模型：{settings.LOCAL_EMBEDDING_MODEL}")
        try:
            self.local_model = SentenceTransformer(settings.LOCAL_EMBEDDING_MODEL)
            self.is_local = True
            self.client = None
            logger.info(
                f"Embedding service initialized (Local: {settings.LOCAL_EMBEDDING_MODEL})"
            )
        except Exception as e:
            logger.error(f"Failed to initialize local embedding model: {e}")
            # 初始化失败时，设置为未初始化状态
            self.is_local = False
            self.client = None
            self.local_model = None
            logger.warning("No valid embedding model available. Please provide an API key or ensure local model is properly configured.")

    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """批量生成向量"""
        if not texts:
            return []

        # 清洗空文本
        texts = [t if t.strip() else " " for t in texts]

        if self.is_local and hasattr(self, 'local_model') and self.local_model:
            return self._embed_local(texts)
        elif not self.is_local and hasattr(self, 'client') and self.client:
            return await self._embed_openai(texts)
        else:
            logger.error("No valid embedding model available. Please provide an API key or ensure local model is properly configured.")
            # 生成随机向量作为最后的备用方案
            import random
            embedding_dim = settings.EMBEDDING_DIMENSION
            return [[random.random() for _ in range(embedding_dim)] for _ in texts]

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