from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, Text, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    body: Mapped[str] = mapped_column(Text)
    difficulty: Mapped[int] = mapped_column(Integer, index=True)
    topic: Mapped[str] = mapped_column(ForeignKey("topics.topic_id"), default="general", index=True)
    subject_id: Mapped[str] = mapped_column(String(50), nullable=False, server_default="math")
    subject_name: Mapped[str] = mapped_column(String(100), nullable=False, server_default="Математика")
    answer_key: Mapped[str | None] = mapped_column(String(255), nullable=True)
    solution: Mapped[str | None] = mapped_column(Text, nullable=True)
    grade: Mapped[int | None] = mapped_column(Integer, nullable=True)
    task_type: Mapped[str] = mapped_column(String(50), default="open_answer", index=True)
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
