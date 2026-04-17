from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_student
from app.models.submission import Submission
from app.models.task import Task
from app.models.user import User
from app.schemas.submission import SubmissionIn, SubmissionOut
from app.services.adaptive_db import (
    get_or_create_global_state,
    get_or_create_topic_state,
    next_attempt_number,
    record_practice_attempt,
    update_global_state,
    update_topic_state,
)
from app.services.answer_checker import check_answer

router = APIRouter(prefix="/submissions", tags=["submissions"])


def normalize_answer(answer: str) -> str:
    return " ".join(answer.strip().lower().split())


@router.post("", response_model=SubmissionOut)
def submit(data: SubmissionIn, db: Session = Depends(get_db), user: User = Depends(require_student)):
    task = db.query(Task).filter(Task.id == data.task_id, Task.is_archived.is_(False)).first()
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

    state = get_or_create_global_state(db, user.id)
    topic_state = get_or_create_topic_state(db, task.topic, user_id=user.id)
    delta = update_global_state(state, task, is_correct)
    update_topic_state(topic_state, task, is_correct)
    attempt_number = next_attempt_number(db, user.id, task.id)
    feedback = "Correct answer. Skill score updated." if is_correct else "Answer recorded. Try a simpler task next."

    submission = Submission(
        user_id=user.id,
        task_id=task.id,
        answer=answer,
        expected_answer=task.answer_key,
        is_correct=is_correct,
        score_delta=delta,
        attempt_number=attempt_number,
        time_spent_seconds=data.time_spent_seconds,
        feedback=feedback,
        mode=data.mode,
    )
    db.add(submission)
    record_practice_attempt(db, task, answer, is_correct, user_id=user.id, mode=data.mode)
    db.commit()
    db.refresh(submission)

    return SubmissionOut(
        submission_id=submission.id,
        new_skill_score=state.skill_score,
        delta=delta,
        is_correct=is_correct,
        message=feedback,
        attempt_number=attempt_number,
        feedback=feedback,
    )
