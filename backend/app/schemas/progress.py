from pydantic import BaseModel


class RecentSubmissionOut(BaseModel):
    submission_id: int
    task_title: str
    topic: str
    is_correct: bool
    score_delta: int
    submitted_at: str


class StudentProgressOut(BaseModel):
    user_id: int
    full_name: str
    skill_score: int
    total_attempts: int
    correct_attempts: int
    accuracy: float
    recent_submissions: list[RecentSubmissionOut]


class StudentSummaryOut(BaseModel):
    id: int
    email: str
    full_name: str
    role: str
    skill_score: int
    total_attempts: int

