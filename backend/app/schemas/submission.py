from pydantic import BaseModel, Field


class SubmissionIn(BaseModel):
    task_id: int
    answer: str = Field(min_length=1)
    is_correct: bool | None = None
    time_spent_seconds: int | None = Field(default=None, ge=0)
    mode: str = Field(default="self_education", min_length=2, max_length=50)


class SubmissionOut(BaseModel):
    submission_id: int
    new_skill_score: int
    delta: int
    is_correct: bool
    message: str
    attempt_number: int = 1
    feedback: str | None = None
