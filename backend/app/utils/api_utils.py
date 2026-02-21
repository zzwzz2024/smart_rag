"""
API相关的工具函数
"""
import os
import time
from datetime import datetime, timezone
from typing import Optional, Tuple
from loguru import logger
from backend.app.config import get_settings

settings = get_settings()


def get_project_root() -> str:
    """
    获取项目根目录
    
    Returns:
        str: 项目根目录路径
    """
    try:
        # 从当前文件路径向上遍历，找到项目根目录
        current_dir = os.path.dirname(__file__)
        project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
        return project_root
    except Exception as e:
        logger.error(f"获取项目根目录失败: {str(e)}")
        # 返回当前目录作为 fallback
        return os.getcwd()


def get_template_path(template_name: str) -> str:
    """
    获取模板文件路径
    
    Args:
        template_name: 模板文件名
    
    Returns:
        str: 模板文件完整路径
    """
    project_root = get_project_root()
    return os.path.join(project_root, template_name)


def generate_api_doc_filename(vendor_name: str) -> str:
    """
    生成API文档文件名
    
    Args:
        vendor_name: 厂商名称
    
    Returns:
        str: 生成的文件名
    """
    today = datetime.now().strftime("%Y-%m-%d")
    return f"{settings.API_DOC_FILENAME_PREFIX}-{vendor_name}-{today}.md"


def get_client_ip(request) -> str:
    """
    获取客户端IP地址
    
    Args:
        request: FastAPI请求对象
    
    Returns:
        str: 客户端IP地址
    """
    if request and request.client:
        return request.client.host
    return settings.DEFAULT_CLIENT_IP


def calculate_response_time(start_time: float) -> float:
    """
    计算响应时间（毫秒）
    
    Args:
        start_time: 请求开始时间
    
    Returns:
        float: 响应时间（毫秒）
    """
    return (time.time() - start_time) * 1000


def format_response_time(response_time_ms: float) -> str:
    """
    格式化响应时间
    
    Args:
        response_time_ms: 响应时间（毫秒）
    
    Returns:
        str: 格式化后的响应时间
    """
    if response_time_ms < 1000:
        return f"{response_time_ms:.2f}ms"
    elif response_time_ms < 60000:
        seconds = response_time_ms / 1000
        return f"{seconds:.2f}s"
    elif response_time_ms < 3600000:
        minutes = response_time_ms / 60000
        seconds = (response_time_ms % 60000) / 1000
        return f"{minutes:.0f}m {seconds:.2f}s"
    else:
        hours = response_time_ms / 3600000
        minutes = (response_time_ms % 3600000) / 60000
        return f"{hours:.0f}h {minutes:.0f}m"


def make_timezone_aware(dt: datetime) -> datetime:
    """
    将时区-naive的datetime转换为时区-aware的datetime
    
    Args:
        dt: 时区-naive的datetime对象
    
    Returns:
        datetime: 时区-aware的datetime对象
    """
    if dt and dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


def make_timezone_naive(dt: datetime) -> datetime:
    """
    将时区-aware的datetime转换为时区-naive的datetime
    
    Args:
        dt: 时区-aware的datetime对象
    
    Returns:
        datetime: 时区-naive的datetime对象
    """
    if dt and dt.tzinfo is not None:
        return dt.replace(tzinfo=None)
    return dt


def validate_time_range(start_time: Optional[datetime], end_time: Optional[datetime]) -> Tuple[Optional[datetime], Optional[datetime]]:
    """
    验证时间范围
    
    Args:
        start_time: 开始时间
        end_time: 结束时间
    
    Returns:
        Tuple[Optional[datetime], Optional[datetime]]: 验证后的开始时间和结束时间
    """
    # 转换为时区-naive
    start_time = make_timezone_naive(start_time)
    end_time = make_timezone_naive(end_time)
    
    # 验证时间范围
    if start_time and end_time and start_time > end_time:
        logger.warning("开始时间大于结束时间，将交换时间")
        start_time, end_time = end_time, start_time
    
    return start_time, end_time


def check_time_in_range(dt: datetime, start_time: datetime, end_time: datetime) -> bool:
    """
    检查时间是否在指定范围内
    
    Args:
        dt: 要检查的时间
        start_time: 开始时间
        end_time: 结束时间
    
    Returns:
        bool: 是否在范围内
    """
    # 确保所有时间都是时区-aware的
    dt = make_timezone_aware(dt)
    start_time = make_timezone_aware(start_time)
    end_time = make_timezone_aware(end_time)
    
    return start_time <= dt <= end_time
