from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_teacher
from app.api.routes.progress import build_progress_payload
from app.models.learner_state import LearnerState
from app.models.submission import Submission
from app.models.task import Task
from app.models.user import User
from app.schemas.progress import StudentProgressOut, StudentSummaryOut
from app.schemas.task import TaskCreateIn, TaskOut

router = APIRouter(prefix="/teacher", tags=["teacher"])


def serialize_task(task: Task) -> TaskOut:
    return TaskOut(
        id=task.id,
        title=task.title,
        body=task.body,
        difficulty=task.difficulty,
        topic=task.topic,
        answer_key=task.answer_key,
    )


@router.post("/tasks", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
def create_task(
    data: TaskCreateIn,
    db: Session = Depends(get_db),
    teacher: User = Depends(require_teacher),
):
    _ = teacher
    task = Task(
        title=data.title.strip(),
        body=data.body.strip(),
        difficulty=data.difficulty,
        topic=data.topic.strip(),
        answer_key=data.answer_key.strip() if data.answer_key else None,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return serialize_task(task)


@router.get("/tasks", response_model=list[TaskOut])
def list_tasks(db: Session = Depends(get_db), teacher: User = Depends(require_teacher)):
    _ = teacher
    tasks = db.query(Task).order_by(Task.difficulty.asc(), Task.id.asc()).all()
    return [serialize_task(task) for task in tasks]


@router.get("/students", response_model=list[StudentSummaryOut])
def list_students(db: Session = Depends(get_db), teacher: User = Depends(require_teacher)):
    _ = teacher
    students = db.query(User).filter(User.role == "student").order_by(User.id.asc()).all()
    result = []
    for student in students:
        state = db.query(LearnerState).filter(LearnerState.user_id == student.id).first()
        total_attempts = db.query(func.count(Submission.id)).filter(Submission.user_id == student.id).scalar() or 0
        result.append(
            StudentSummaryOut(
                id=student.id,
                email=student.email,
                full_name=student.full_name,
                role=student.role,
                skill_score=state.skill_score if state else 50,
                total_attempts=total_attempts,
            )
        )
    return result


@router.get("/students/{student_id}/progress", response_model=StudentProgressOut)
def student_progress_view(student_id: int, db: Session = Depends(get_db), teacher: User = Depends(require_teacher)):
    _ = teacher
    student = db.query(User).filter(User.id == student_id, User.role == "student").first()
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
    return build_progress_payload(db, student)
