from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class LearnerTopicState(Base):
    __tablename__ = "learner_topic_states"
    __table_args__ = (
        UniqueConstraint("user_id", "topic", name="uq_learner_topic_state_user_topic"),
        UniqueConstraint("external_user_key", "topic", name="uq_learner_topic_state_external_topic"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    external_user_key: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)
    topic: Mapped[str] = mapped_column(String(100), index=True)
    skill_score: Mapped[int] = mapped_column(Integer, default=50)
    current_difficulty: Mapped[int] = mapped_column(Integer, default=1)
    attempts_count: Mapped[int] = mapped_column(Integer, default=0)
    correct_count: Mapped[int] = mapped_column(Integer, default=0)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
