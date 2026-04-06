from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import get_settings


def build_engine(database_url: str):
    connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
    return create_engine(database_url, connect_args=connect_args, future=True)


def build_session_factory(engine):
    return sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


settings = get_settings()
engine = build_engine(settings.database_url)
SessionLocal = build_session_factory(engine)

