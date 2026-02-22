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
    UPLOAD_DIR: str = "E:\\ai_code\\github workplace\\zzwzz_rag\\backend\\uploads"
    MAX_FILE_SIZE_MB: int = 100

    # ---- ChromaDB ----
    CHROMA_PERSIST_DIR: str = "E:\\ai_code\\github workplace\\zzwzz_rag\\backend\\chroma_data"

    # ---- LLM ----
    EMBEDDING_DIMENSION: int = 1536
    LLM_TEMPERATURE: float = 0.1
    LLM_MAX_TOKENS: int = 4096

    # ---- 检索 ----
    CHUNK_SIZE: int = 512
    CHUNK_OVERLAP: int = 64
    RETRIEVAL_TOP_K: int = 30          # 粗检索数
    RERANK_TOP_K: int = 10             # 精排后保留数
    SIMILARITY_THRESHOLD: float = 0.2  # 最低相关性阈值

    # ---- 本地 Embedding (可选) ----
    USE_LOCAL_EMBEDDING: bool = False
    LOCAL_EMBEDDING_MODEL: str = f"F:\\model-file\\pretrained\\bge-base-zh-v1.5"

    # ---- API 配置 ----
    API_DOC_TEMPLATE_PATH: str = "API接口模版v1.0.0.md"
    DEFAULT_CLIENT_IP: str = "127.0.0.1"
    API_CHAT_ENDPOINT: str = "/api-auth/chat"
    API_DOC_FILENAME_PREFIX: str = "之之接口说明文档"

    # ---- 日志配置 ----
    LOG_DIR: str = "logs"

    # ---- 响应配置 ----
    DEFAULT_ERROR_MESSAGE: str = "请求失败，请稍后重试"
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()