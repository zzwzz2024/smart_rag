"""
SmartRAG 全局配置
"""
from typing import Optional
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """应用配置 - 支持 .env 文件与环境变量"""

    # ---- 应用 ----
    APP_NAME: str = "SmartRAG"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    SECRET_KEY: str = "smartrag-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7天

    # ---- 数据库 ----
    DATABASE_URL: str = "postgresql+asyncpg://postgres:P%40ssw0rd@localhost:5432/rag"
    REDIS_URL: str = "redis://localhost:6379/0"

    # ---- 文件存储 ----
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE_MB: int = 100

    # ---- LLM ----
    OPENAI_PROVIDER: str = "openai"
    OPENAI_API_KEY: str = "sk-f7758e4555e045fdb02d12579fee29b5"
    OPENAI_BASE_URL: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    LLM_MODEL: str = "qwen3-max"
    EMBEDDING_MODEL: str = "text-embedding-v1"
    EMBEDDING_DIMENSION: int = 1536
    LLM_TEMPERATURE: float = 0.1
    LLM_MAX_TOKENS: int = 4096

    # ---- 检索 ----
    CHUNK_SIZE: int = 512
    CHUNK_OVERLAP: int = 64
    RETRIEVAL_TOP_K: int = 20          # 粗检索数
    RERANK_TOP_K: int = 5              # 精排后保留数
    SIMILARITY_THRESHOLD: float = 0.3  # 最低相关性阈值

    # ---- ChromaDB ----
    CHROMA_PERSIST_DIR: str = "chroma_data"

    # ---- 本地 Embedding (可选) ----
    USE_LOCAL_EMBEDDING: bool = False
    LOCAL_EMBEDDING_MODEL: str = f"F:\model-file\pretrained\bge-base-zh-v1.5"

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()