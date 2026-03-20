"""智能体相关模型"""
from sqlalchemy import Column, String, Text, DateTime, Integer, JSON
from sqlalchemy.sql import func
from backend.app.database import Base


class AgentFeedback(Base):
    """智能体反馈表"""
    __tablename__ = "agent_feedback"
    
    id = Column(String, primary_key=True, index=True)
    conversation_id = Column(String, nullable=False, index=True)
    query = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    feedback = Column(Integer, nullable=False)  # 1-5分
    timestamp = Column(DateTime, default=func.now())
    extra_data = Column(JSON, nullable=True)
