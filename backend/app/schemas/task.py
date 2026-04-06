from pydantic import BaseModel, Field


class TaskOut(BaseModel):
    id: int
    title: str
    body: str
    difficulty: int
    topic: str
    answer_key: str | None = None


class TaskCreateIn(BaseModel):
    title: str = Field(min_length=3, max_length=255)
    body: str = Field(min_length=3)
    difficulty: int = Field(ge=1, le=3)
    topic: str = Field(default="general", min_length=2, max_length=100)
    answer_key: str | None = Field(default=None, max_length=255)

