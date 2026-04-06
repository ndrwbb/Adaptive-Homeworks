from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class HomeworkSubmission(Base):
    __tablename__ = "homework_submissions"

    id: Mapped[int] = mapped_column(primary_key=True)
    assignment_id: Mapped[int] = mapped_column(ForeignKey("homework_assignments.id"), index=True)
    item_id: Mapped[int] = mapped_column(ForeignKey("homework_items.id"), index=True)
    answer: Mapped[str] = mapped_column(Text)
    is_correct: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    awarded_points: Mapped[int] = mapped_column(Integer, default=0)
    review_status: Mapped[str] = mapped_column(String(50), default="pending")
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

