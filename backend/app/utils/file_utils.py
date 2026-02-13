import os
import uuid
import shutil
from pathlib import Path
from typing import Optional, Set
from mimetypes import guess_type

from backend.app.config import get_settings

settings = get_settings()

ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.txt', '.md', '.pptx', '.xlsx', '.csv', '.html'}
ALLOWED_MIME_TYPES = {
    'application/pdf',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'text/plain',
    'text/markdown',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'text/csv',
    'text/html'
}


def validate_file_type(filename: str) -> bool:
    """验证文件扩展名是否允许"""
    _, ext = os.path.splitext(filename.lower())
    return ext in ALLOWED_EXTENSIONS


def validate_file_mime_type(filepath: str) -> bool:
    """验证文件MIME类型是否允许"""
    mime_type, _ = guess_type(filepath)
    if mime_type:
        return mime_type in ALLOWED_MIME_TYPES
    return False


def validate_file_size(filepath: str, max_size_mb: Optional[int] = None) -> bool:
    """验证文件大小是否超过限制"""
    if max_size_mb is None:
        max_size_mb = settings.MAX_FILE_SIZE_MB

    file_size_bytes = os.path.getsize(filepath)
    max_size_bytes = max_size_mb * 1024 * 1024  # MB to bytes
    return file_size_bytes <= max_size_bytes


def generate_unique_filename(original_filename: str) -> str:
    """生成唯一文件名保持原始扩展名"""
    name, ext = os.path.splitext(original_filename)
    unique_id = str(uuid.uuid4())
    return f"{unique_id}{ext}"


def get_upload_path(kb_id: str, filename: str) -> str:
    """获取上传文件的完整路径"""
    upload_dir = os.path.join(settings.UPLOAD_DIR, kb_id)
    os.makedirs(upload_dir, exist_ok=True)
    return os.path.join(upload_dir, filename)


def ensure_directory_exists(path: str):
    """确保目录存在，如果不存在则创建"""
    Path(path).parent.mkdir(parents=True, exist_ok=True)


def safe_remove_file(filepath: str) -> bool:
    """安全删除文件，忽略错误"""
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
        return False
    except OSError:
        return False


def safe_remove_directory(dir_path: str) -> bool:
    """安全删除目录及其内容，忽略错误"""
    try:
        if os.path.exists(dir_path):
            shutil.rmtree(dir_path)
            return True
        return False
    except OSError:
        return False


def get_file_size_mb(filepath: str) -> float:
    """获取文件大小（MB）"""
    size_bytes = os.path.getsize(filepath)
    return size_bytes / (1024 * 1024)


def get_file_extension(filename: str) -> str:
    """获取文件扩展名（带点号）"""
    return os.path.splitext(filename)[1].lower()


def cleanup_temp_files(temp_dir: str, keep_recent: int = 0):
    """清理临时文件，保留最近的几个"""
    if not os.path.exists(temp_dir):
        return

    files = []
    for item in os.listdir(temp_dir):
        item_path = os.path.join(temp_dir, item)
        if os.path.isfile(item_path):
            files.append((item_path, os.path.getmtime(item_path)))

    # 按修改时间排序
    files.sort(key=lambda x: x[1], reverse=True)

    # 删除旧文件，保留最新的keep_recent个
    for filepath, _ in files[keep_recent:]:
        try:
            os.remove(filepath)
        except OSError:
            pass  # 忽略删除错误


def copy_file_safe(src: str, dst: str) -> bool:
    """安全复制文件"""
    try:
        ensure_directory_exists(dst)
        shutil.copy2(src, dst)
        return True
    except (OSError, IOError):
        return False


def get_file_info(filepath: str) -> dict:
    """获取文件信息"""
    if not os.path.exists(filepath):
        return {}

    stat = os.stat(filepath)
    mime_type, _ = guess_type(filepath)

    return {
        "size": stat.st_size,
        "size_mb": stat.st_size / (1024 * 1024),
        "modified": stat.st_mtime,
        "created": stat.st_ctime,
        "mime_type": mime_type,
        "extension": get_file_extension(filepath),
        "basename": os.path.basename(filepath)
    }

