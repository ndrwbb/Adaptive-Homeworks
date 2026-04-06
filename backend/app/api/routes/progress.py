from sqlalchemy import func
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_db, get_current_user, require_student, require_teacher
from app.models.learner_state import LearnerState
from app.models.submission import Submission
from app.models.task import Task
from app.models.user import User
from app.schemas.progress import RecentSubmissionOut, StudentProgressOut

router = APIRouter(prefix="/progress", tags=["progress"])


def build_progress_payload(db: Session, user: User) -> StudentProgressOut:
    state = db.query(LearnerState).filter(LearnerState.user_id == user.id).first()
    skill_score = state.skill_score if state else 50

    total_attempts = db.query(func.count(Submission.id)).filter(Submission.user_id == user.id).scalar() or 0
    correct_attempts = (
        db.query(func.count(Submission.id))
        .filter(Submission.user_id == user.id, Submission.is_correct.is_(True))
        .scalar()
        or 0
    )
    accuracy = round((correct_attempts / total_attempts) * 100, 2) if total_attempts else 0.0

    recent_rows = (
        db.query(Submission, Task)
        .join(Task, Task.id == Submission.task_id)
        .filter(Submission.user_id == user.id)
        .order_by(Submission.submitted_at.desc(), Submission.id.desc())
        .limit(5)
        .all()
    )
    recent_submissions = [
        RecentSubmissionOut(
            submission_id=submission.id,
            task_title=task.title,
            topic=task.topic,
            is_correct=submission.is_correct,
            score_delta=submission.score_delta,
            submitted_at=submission.submitted_at.isoformat(),
        )
        for submission, task in recent_rows
    ]

    return StudentProgressOut(
        user_id=user.id,
        full_name=user.full_name,
        skill_score=skill_score,
        total_attempts=total_attempts,
        correct_attempts=correct_attempts,
        accuracy=accuracy,
        recent_submissions=recent_submissions,
    )


@router.get("/me", response_model=StudentProgressOut)
def my_progress(db: Session = Depends(get_db), user: User = Depends(require_student)):
    return build_progress_payload(db, user)


@router.get("/me/history", response_model=list[RecentSubmissionOut])
def my_history(db: Session = Depends(get_db), user: User = Depends(require_student)):
    return build_progress_payload(db, user).recent_submissions


@router.get("/student/{student_id}", response_model=StudentProgressOut)
def student_progress(student_id: int, db: Session = Depends(get_db), teacher: User = Depends(require_teacher)):
    _ = teacher
    student = db.query(User).filter(User.id == student_id, User.role == "student").first()
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
    return build_progress_payload(db, student)

