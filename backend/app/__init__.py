"""SmartRAG 应用初始化"""
import os
from loguru import logger
from .config import get_settings

# 获取配置
settings = get_settings()

# 配置日志文件
log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), settings.LOG_DIR)
os.makedirs(log_dir, exist_ok=True)

# 添加文件输出
logger.add(
    os.path.join(log_dir, "app_{time:YYYY-MM-DD}.log"),
    rotation="1 day",  # 每天轮换
    compression="zip",  # 压缩旧日志
    level="INFO",  # 日志级别
    backtrace=True,  # 包含堆栈回溯
    diagnose=True  # 包含诊断信息
)

# 配置控制台输出（可选，loguru默认会输出到控制台）
logger.add(
    lambda msg: print(msg, end=""),
    level="INFO"
)

__version__ = "1.0.0"
