from pydantic import BaseModel, Field


class SubmissionIn(BaseModel):
    task_id: int
    answer: str = Field(min_length=1)
    is_correct: bool | None = None


class SubmissionOut(BaseModel):
    submission_id: int
    new_skill_score: int
    delta: int
    is_correct: bool
    message: str

