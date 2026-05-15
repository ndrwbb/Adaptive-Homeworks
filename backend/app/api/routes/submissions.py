from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_student
from app.models.learner_state import LearnerState
from app.models.submission import Submission
from app.models.task import Task
from app.models.user import User
from app.schemas.submission import SubmissionIn, SubmissionOut
from app.services.answer_checker import check_answer

router = APIRouter(prefix="/submissions", tags=["submissions"])


def normalize_answer(answer: str) -> str:
    return " ".join(answer.strip().lower().split())


@router.post("", response_model=SubmissionOut)
def submit(data: SubmissionIn, db: Session = Depends(get_db), user: User = Depends(require_student)):
    task = db.query(Task).filter(Task.id == data.task_id).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    answer = data.answer.strip()
    if task.answer_key:
        is_correct = check_answer(answer, task.answer_key)
    elif data.is_correct is not None:
        is_correct = data.is_correct
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="is_correct is required when answer_key is missing",
        )

    state = db.query(LearnerState).filter(LearnerState.user_id == user.id).first()
    if not state:
        state = LearnerState(user_id=user.id, skill_score=50)
        db.add(state)
        db.flush()

    delta = 5 * task.difficulty if is_correct else -5 * task.difficulty
    state.skill_score = max(0, min(100, state.skill_score + delta))

    submission = Submission(
        user_id=user.id,
        task_id=task.id,
        answer=answer,
        is_correct=is_correct,
        score_delta=delta,
    )
    db.add(submission)
    db.commit()
    db.refresh(submission)

    message = "Correct answer. Skill score updated." if is_correct else "Answer recorded. Try a simpler task next."
    return SubmissionOut(
        submission_id=submission.id,
        new_skill_score=state.skill_score,
        delta=delta,
        is_correct=is_correct,
        message=message,
    )

