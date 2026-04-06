from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_student
from app.models.learner_state import LearnerState
from app.models.task import Task
from app.models.user import User
from app.schemas.task import TaskOut

router = APIRouter(prefix="/tasks", tags=["tasks"])


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
