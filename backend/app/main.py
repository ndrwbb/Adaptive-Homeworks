from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import auth, homeworks, progress, submissions, tasks, teacher
from app.core.config import get_settings
from app.db.base import Base
from app.db.session import SessionLocal, engine
from seed import seed_demo_data


def create_app(session_factory=None, engine=None):
    settings = get_settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        Base.metadata.create_all(bind=app.state.engine)
        with app.state.session_factory() as db:
            seed_demo_data(db)
        yield

    app = FastAPI(
        title="Adaptive Homework API",
        description="Backend for adaptive homework assignment and student progress tracking.",
        version="0.6.0",
        lifespan=lifespan,
    )

    app.state.session_factory = session_factory or SessionLocal
    app.state.engine = engine or globals()["engine"]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/")
    def root():
        return {
            "message": "Adaptive Homework API",
            "docs": "/docs",
            "demo_accounts": {
                "student": "student@example.com / demo123",
                "teacher": "teacher@example.com / demo123",
            },
        }

    @app.get("/health")
    def health():
        return {"status": "ok"}

    app.include_router(auth.router)
    app.include_router(tasks.router)
    app.include_router(submissions.router)
    app.include_router(progress.router)
    app.include_router(homeworks.router)
    app.include_router(teacher.router)

    return app


app = create_app()
