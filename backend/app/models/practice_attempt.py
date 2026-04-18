from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class PracticeAttempt(Base):
    __tablename__ = "practice_attempts"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    external_user_key: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id"), index=True)
    topic: Mapped[str] = mapped_column(ForeignKey("topics.topic_id"), index=True)
    answer: Mapped[str] = mapped_column(Text)
    expected_answer: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_correct: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    mode: Mapped[str] = mapped_column(String(50), default="self_education", index=True)
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
