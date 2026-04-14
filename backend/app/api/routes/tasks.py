from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_student
from app.fake_tasks import get_all_tasks, get_task_by_id
from app.models.learner_state import LearnerState
from app.models.task import Task
from app.models.user import User
from app.schemas.task import TaskOut
from app.services.adaptive import (
    get_next_task_for_user,
    get_user_state,
    record_answer,
    update_user_state,
)
from app.services.answer_checker import check_answer

router = APIRouter(prefix="/tasks", tags=["tasks"])


# ── Existing DB-backed helpers ──────────────────────────────────

def pick_difficulty(skill_score: int) -> int:
    if skill_score < 40:
        return 1
    if skill_score < 70:
        return 2
    return 3


def serialize_task(task: Task) -> TaskOut:
    return TaskOut(
        id=task.id,
        title=task.title,
        body=task.body,
        difficulty=task.difficulty,
        topic=task.topic,
        answer_key=task.answer_key,
    )


@router.get("/recommendation", response_model=TaskOut)
def recommendation(
    topic: str | None = Query(default=None),
    difficulty: int | None = Query(default=None, ge=1, le=3),
    db: Session = Depends(get_db),
    user: User = Depends(require_student),
):
    state = db.query(LearnerState).filter(LearnerState.user_id == user.id).first()
    skill = state.skill_score if state else 50
    resolved_difficulty = difficulty if difficulty is not None else pick_difficulty(skill)

    query = db.query(Task).filter(Task.difficulty == resolved_difficulty)
    if topic:
        query = query.filter(Task.topic == topic)
    task = query.order_by(Task.id.asc()).first()
    if not task:
        fallback_query = db.query(Task)
        if topic:
            fallback_query = fallback_query.filter(Task.topic == topic)
        task = fallback_query.order_by(Task.difficulty.asc(), Task.id.asc()).first()

    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No tasks found")

    return serialize_task(task)


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

def _safe_task(task: dict) -> dict:
    """Return a copy of *task* without the ``answer`` and ``solution`` fields."""
    return {k: v for k, v in task.items() if k not in ("answer", "solution")}


# ── New fake-data endpoints ─────────────────────────────────────

@router.get("/next")
def next_task(
    user_id: str = Query(default="demo_user"),
    topic: str | None = Query(default=None),
):
    """Return the next adaptive task for *user_id* (fake-data layer)."""
    task = get_next_task_for_user(user_id, topic)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No tasks matching the criteria",
        )
    # get_next_task_for_user already strips `answer`, but also strip `solution`
    return _safe_task(task)


@router.get("/all")
def list_tasks():
    """Return **all** fake tasks without ``answer`` or ``solution``."""
    return [_safe_task(t) for t in get_all_tasks()]


@router.get("/{task_id}")
def get_single_task(task_id: int):
    """Return a single fake task without ``answer`` or ``solution``."""
    task = get_task_by_id(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    return _safe_task(task)


@router.post("/{task_id}/answer", response_model=AnswerResult)
def submit_answer(task_id: int, body: AnswerIn):
    """Check user's answer, update adaptive state, return result."""
    task = get_task_by_id(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    is_correct = check_answer(body.answer, task["answer"])
    record_answer(body.user_id, task_id, task["topic"], is_correct)
    state = update_user_state(body.user_id, task["topic"], is_correct)

    return AnswerResult(
        task_id=task_id,
        is_correct=is_correct,
        correct_answer=task["answer"],
        solution=task.get("solution"),
        next_difficulty=state["current_difficulty"],
    )
