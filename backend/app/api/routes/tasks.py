from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_student
from app.models.task import Task
from app.models.user import User
from app.schemas.task import TaskOut, TaskPracticeOut
from app.services.adaptive_db import (
    get_or_create_topic_state,
    pick_next_task,
    record_practice_attempt,
    skill_for_difficulty,
)
from app.services.answer_checker import check_answer

router = APIRouter(prefix="/tasks", tags=["tasks"])


def serialize_task(task: Task) -> TaskOut:
    return TaskOut(
        id=task.id,
        title=task.title,
        body=task.body,
        difficulty=task.difficulty,
        topic=task.topic,
        answer_key=task.answer_key,
        solution=task.solution,
        grade=task.grade,
        task_type=task.task_type,
        is_archived=task.is_archived,
    )


def serialize_practice_task(task: Task) -> TaskPracticeOut:
    return TaskPracticeOut(
        id=task.id,
        title=task.title,
        body=task.body,
        difficulty=task.difficulty,
        topic=task.topic,
        grade=task.grade,
        task_type=task.task_type,
    )


@router.get("/recommendation", response_model=TaskPracticeOut)
def recommendation(
    topic: str | None = Query(default=None),
    difficulty: int | None = Query(default=None, ge=1, le=3),
    db: Session = Depends(get_db),
    user: User = Depends(require_student),
):
    task = pick_next_task(db, topic=topic, difficulty=difficulty, user_id=user.id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No tasks found")

    return serialize_practice_task(task)


# ── Pydantic models for the new MVP endpoints ──────────────────

class AnswerIn(BaseModel):
    user_id: str = "demo_user"
    answer: str


class AnswerResult(BaseModel):
    task_id: int
    is_correct: bool
    correct_answer: str
    solution: str | None = None
    next_difficulty: int


# ── Helpers ─────────────────────────────────────────────────────

def _task_to_legacy_payload(task: Task, include_answer: bool = False) -> dict:
    payload = {
        "id": task.id,
        "topic": task.topic,
        "difficulty": task.difficulty,
        "grade": task.grade,
        "task_type": task.task_type,
        "question": task.body,
        "options": None,
        "title": task.title,
        "body": task.body,
    }
    if include_answer:
        payload["answer"] = task.answer_key
        payload["solution"] = task.solution
    return payload


# ── Backwards-compatible self-education endpoints ──────────────

@router.get("/next")
def next_task(
    user_id: str = Query(default="demo_user"),
    topic: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    """Return the next adaptive task for legacy clients, backed by the database."""
    task = pick_next_task(db, topic=topic, external_user_key=user_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No tasks matching the criteria",
        )
    return _task_to_legacy_payload(task)


@router.get("/all")
def list_tasks(db: Session = Depends(get_db)):
    """Return all active tasks without answers for legacy clients."""
    tasks = db.query(Task).filter(Task.is_archived.is_(False)).order_by(Task.id.asc()).all()
    return [_task_to_legacy_payload(task) for task in tasks]


@router.get("/{task_id}")
def get_single_task(task_id: int, db: Session = Depends(get_db)):
    """Return a single active task without the answer for legacy clients."""
    task = db.query(Task).filter(Task.id == task_id, Task.is_archived.is_(False)).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    return _task_to_legacy_payload(task)


@router.post("/{task_id}/answer", response_model=AnswerResult)
def submit_answer(task_id: int, body: AnswerIn, db: Session = Depends(get_db)):
    """Check a legacy self-education answer, persist attempt/state, and return result."""
    task = db.query(Task).filter(Task.id == task_id, Task.is_archived.is_(False)).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    if not task.answer_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task has no answer key",
        )

    is_correct = check_answer(body.answer, task.answer_key)
    state = get_or_create_topic_state(db, task.topic, external_user_key=body.user_id)
    state.attempts_count += 1
    if is_correct:
        state.correct_count += 1
        state.current_difficulty = min(state.current_difficulty + 1, 3)
    else:
        state.current_difficulty = max(state.current_difficulty - 1, 1)
    state.skill_score = skill_for_difficulty(state.current_difficulty)
    record_practice_attempt(
        db,
        task,
        body.answer.strip(),
        is_correct,
        external_user_key=body.user_id,
        mode="legacy_self_education",
    )
    db.commit()

    return AnswerResult(
        task_id=task_id,
        is_correct=is_correct,
        correct_answer=task.answer_key,
        solution=task.solution,
        next_difficulty=state.current_difficulty,
    )
