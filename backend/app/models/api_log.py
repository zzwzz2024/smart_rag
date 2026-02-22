import uuid
from datetime import datetime
from sqlalchemy import String, Text, Integer, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.database import Base


class ApiLog(Base):
    """API访问日志模型"""
    __tablename__ = "api_logs"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    
    # 授权信息
    auth_code: Mapped[str] = mapped_column(String(64), index=True)
    
    # 请求信息
    endpoint: Mapped[str] = mapped_column(String(255))
    method: Mapped[str] = mapped_column(String(10))
    ip: Mapped[str] = mapped_column(String(50))
    user_agent: Mapped[str] = mapped_column(Text, nullable=True)
    
    # 响应信息
    status: Mapped[int] = mapped_column(Integer)
    response_time: Mapped[float] = mapped_column(Integer)  # 响应时间（毫秒）
    error_message: Mapped[str] = mapped_column(Text, nullable=True)
    
    # 时间戳
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, index=True
    )
