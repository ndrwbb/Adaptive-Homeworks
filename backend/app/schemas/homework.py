from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class HomeworkItemCreateIn(BaseModel):
    title: str = Field(min_length=2, max_length=255)
    prompt: str = Field(min_length=2)
    item_type: Literal["test", "manual"]
    difficulty: int = Field(ge=1, le=3)
    max_points: int = Field(ge=1)
    answer_key: str | None = None


class HomeworkCreateIn(BaseModel):
    title: str = Field(min_length=3, max_length=255)
    subject: str = Field(min_length=2, max_length=120)
    description: str = Field(min_length=3)
    deadline: datetime
    assignee_ids: list[int] = Field(min_length=1)
    items: list[HomeworkItemCreateIn] = Field(min_length=1)


class HomeworkItemOut(BaseModel):
    id: int
    title: str
    prompt: str
    item_type: str
    difficulty: int
    max_points: int
    answer_key: str | None = None


class HomeworkSummaryOut(BaseModel):
    assignment_id: int
    homework_id: int
    title: str
    subject: str
    teacher_name: str
    deadline: str
    progress_label: str
    status: str
    final_score: int | None = None
    max_score: int


class HomeworkDetailOut(BaseModel):
    assignment_id: int
    homework_id: int
    title: str
    subject: str
    description: str
    teacher_name: str
    deadline: str
    status: str
    final_score: int | None = None
    max_score: int
    requires_manual_review: bool
    items: list[HomeworkItemOut]


class HomeworkSubmissionIn(BaseModel):
    item_id: int
    answer: str = Field(min_length=1)


class HomeworkSubmissionOut(BaseModel):
    submission_id: int
    review_status: str
    is_correct: bool | None = None
    awarded_points: int
    status: str


class TeacherHomeworkOut(BaseModel):
    homework_id: int
    title: str
    subject: str
    deadline: str
    assignment_count: int
    requires_manual_review: bool
    max_score: int
    items: list[HomeworkItemOut]

