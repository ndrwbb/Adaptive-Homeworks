from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class LearnerState(Base):
    __tablename__ = "learner_states"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    skill_score: Mapped[int] = mapped_column(Integer, default=50)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

