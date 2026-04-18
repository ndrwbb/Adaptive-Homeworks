from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Topic(Base):
    __tablename__ = "topics"

    topic_id: Mapped[str] = mapped_column(String(100), primary_key=True)
    topic_name: Mapped[str] = mapped_column(String(150), nullable=False)
    subject_id: Mapped[str] = mapped_column(String(50), nullable=False, server_default="math")
    subject_name: Mapped[str] = mapped_column(String(100), nullable=False, server_default="Математика")
