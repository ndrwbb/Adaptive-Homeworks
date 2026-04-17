from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_teacher
from app.api.routes.progress import build_progress_payload
from app.models.homework_assignment import HomeworkAssignment
from app.models.homework_item import HomeworkItem
from app.models.homework_submission import HomeworkSubmission
from app.models.learner_state import LearnerState
from app.models.submission import Submission
from app.models.task import Task
from app.models.user import User
from app.schemas.homework import (
    ManualReviewIn,
    ManualReviewOut,
    PendingSubmissionOut,
)
from app.schemas.progress import StudentProgressOut, StudentSummaryOut
from app.schemas.task import TaskCreateIn, TaskOut, TaskUpdateIn

router = APIRouter(prefix="/teacher", tags=["teacher"])


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
        solution=data.solution.strip() if data.solution else None,
        grade=data.grade,
        task_type=data.task_type.strip(),
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return serialize_task(task)


@router.get("/tasks", response_model=list[TaskOut])
def list_tasks(
    topic: str | None = None,
    difficulty: int | None = None,
    include_archived: bool = False,
    db: Session = Depends(get_db),
    teacher: User = Depends(require_teacher),
):
    _ = teacher
    query = db.query(Task)
    if topic:
        query = query.filter(Task.topic == topic)
    if difficulty is not None:
        query = query.filter(Task.difficulty == difficulty)
    if not include_archived:
        query = query.filter(Task.is_archived.is_(False))
    tasks = query.order_by(Task.difficulty.asc(), Task.id.asc()).all()
    return [serialize_task(task) for task in tasks]


@router.patch("/tasks/{task_id}", response_model=TaskOut)
def update_task(
    task_id: int,
    data: TaskUpdateIn,
    db: Session = Depends(get_db),
    teacher: User = Depends(require_teacher),
):
    _ = teacher
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    values = data.model_dump(exclude_unset=True)
    for field in ("title", "body", "topic", "answer_key", "solution", "task_type"):
        if field in values and values[field] is not None:
            values[field] = values[field].strip()
    for field, value in values.items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)
    return serialize_task(task)


@router.delete("/tasks/{task_id}", response_model=TaskOut)
def archive_task(task_id: int, db: Session = Depends(get_db), teacher: User = Depends(require_teacher)):
    _ = teacher
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    task.is_archived = True
    db.commit()
    db.refresh(task)
    return serialize_task(task)


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


@router.get("/homeworks/{homework_id}/pending-reviews", response_model=list[PendingSubmissionOut])
def pending_reviews(
    homework_id: int,
    db: Session = Depends(get_db),
    teacher: User = Depends(require_teacher),
):
    """Список manual-ответов, ожидающих проверки учителем."""
    from app.models.homework import Homework

    homework = db.query(Homework).filter(Homework.id == homework_id, Homework.teacher_id == teacher.id).first()
    if not homework:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Homework not found")

    rows = (
        db.query(HomeworkSubmission, HomeworkItem, HomeworkAssignment, User)
        .join(HomeworkItem, HomeworkItem.id == HomeworkSubmission.item_id)
        .join(HomeworkAssignment, HomeworkAssignment.id == HomeworkSubmission.assignment_id)
        .join(User, User.id == HomeworkAssignment.student_id)
        .filter(
            HomeworkItem.homework_id == homework_id,
            HomeworkItem.item_type == "manual",
            HomeworkSubmission.review_status == "pending",
        )
        .all()
    )

    return [
        PendingSubmissionOut(
            submission_id=submission.id,
            assignment_id=assignment.id,
            student_name=student.full_name,
            item_title=item.title,
            item_prompt=item.prompt,
            answer=submission.answer,
            max_points=item.max_points,
            review_status=submission.review_status,
        )
        for submission, item, assignment, student in rows
    ]


@router.post("/submissions/{submission_id}/review", response_model=ManualReviewOut)
def review_submission(
    submission_id: int,
    data: ManualReviewIn,
    db: Session = Depends(get_db),
    teacher: User = Depends(require_teacher),
):
    """Выставить баллы за manual-задание и закрыть ревью."""
    from app.api.routes.homeworks import compute_assignment_status
    from app.models.homework import Homework

    submission = db.query(HomeworkSubmission).filter(HomeworkSubmission.id == submission_id).first()
    if not submission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found")

    item = db.query(HomeworkItem).filter(HomeworkItem.id == submission.item_id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Homework item not found")
    homework = db.query(Homework).filter(Homework.id == item.homework_id).first()
    if not homework:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Homework not found")

    # Убеждаемся, что это домашка этого учителя
    if homework.teacher_id != teacher.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your homework")

    if item.item_type != "manual":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only manual items can be reviewed")

    if data.awarded_points > item.max_points:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"awarded_points cannot exceed max_points ({item.max_points})",
        )

    submission.awarded_points = data.awarded_points
    submission.review_status = "reviewed"
    submission.is_correct = data.awarded_points > 0
    submission.review_comment = data.comment.strip() if data.comment else None

    # Пересчитываем статус и итоговый балл задания
    assignment = db.query(HomeworkAssignment).filter(HomeworkAssignment.id == submission.assignment_id).first()
    db.flush()
    items = db.query(HomeworkItem).filter(HomeworkItem.homework_id == homework.id).all()
    submissions = db.query(HomeworkSubmission).filter(HomeworkSubmission.assignment_id == assignment.id).all()
    new_status, new_score = compute_assignment_status(homework, items, submissions, assignment)
    assignment.status = new_status
    assignment.final_score = new_score

    db.commit()
    db.refresh(submission)

    return ManualReviewOut(
        submission_id=submission.id,
        awarded_points=submission.awarded_points,
        review_status=submission.review_status,
        assignment_status=new_status,
        assignment_final_score=new_score,
    )
