from pydantic import BaseModel, Field


class TaskOut(BaseModel):
    id: int
    title: str
    body: str
    difficulty: int
    topic: str
    answer_key: str | None = None
    solution: str | None = None
    grade: int | None = None
    task_type: str = "open_answer"
    is_archived: bool = False


class TaskPracticeOut(BaseModel):
    id: int
    title: str
    body: str
    difficulty: int
    topic: str
    grade: int | None = None
    task_type: str = "open_answer"


class TaskCreateIn(BaseModel):
    title: str = Field(min_length=3, max_length=255)
    body: str = Field(min_length=3)
    difficulty: int = Field(ge=1, le=3)
    topic: str = Field(default="general", min_length=2, max_length=100)
    answer_key: str | None = Field(default=None, max_length=255)
    solution: str | None = None
    grade: int | None = Field(default=None, ge=1, le=12)
    task_type: str = Field(default="open_answer", min_length=2, max_length=50)


class TaskUpdateIn(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=255)
    body: str | None = Field(default=None, min_length=3)
    difficulty: int | None = Field(default=None, ge=1, le=3)
    topic: str | None = Field(default=None, min_length=2, max_length=100)
    answer_key: str | None = Field(default=None, max_length=255)
    solution: str | None = None
    grade: int | None = Field(default=None, ge=1, le=12)
    task_type: str | None = Field(default=None, min_length=2, max_length=50)
    is_archived: bool | None = None
