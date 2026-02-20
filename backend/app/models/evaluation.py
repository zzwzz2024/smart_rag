import uuid
from datetime import datetime
from sqlalchemy import String, Text, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.database import Base


class Evaluation(Base):
    __tablename__ = "evaluations"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    query: Mapped[str] = mapped_column(Text, nullable=False)
    reference_answer: Mapped[str] = mapped_column(Text, nullable=False)
    rag_answer: Mapped[str] = mapped_column(Text, nullable=False)
    score: Mapped[float] = mapped_column(Float, nullable=False)
    kb_id: Mapped[str] = mapped_column(String, nullable=False)
    model_id: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )