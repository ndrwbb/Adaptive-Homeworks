from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_student, require_teacher
from app.services.answer_checker import check_answer
from app.models.homework import Homework
from app.models.homework_assignment import HomeworkAssignment
from app.models.homework_item import HomeworkItem
from app.models.homework_submission import HomeworkSubmission
from app.models.user import User
from app.schemas.homework import (
    HomeworkCreateIn,
    HomeworkDetailOut,
    HomeworkItemOut,
    HomeworkSubmissionIn,
    HomeworkSubmissionOut,
    HomeworkSummaryOut,
    TeacherHomeworkOut,
)

router = APIRouter(tags=["homeworks"])


def serialize_item(item: HomeworkItem) -> HomeworkItemOut:
    return HomeworkItemOut(
        id=item.id,
        title=item.title,
        prompt=item.prompt,
        item_type=item.item_type,
        difficulty=item.difficulty,
        max_points=item.max_points,
        answer_key=item.answer_key,
    )




def compute_assignment_status(
    homework: Homework,
    items: list[HomeworkItem],
    submissions: list[HomeworkSubmission],
    assignment: HomeworkAssignment,
) -> tuple[str, int | None]:
    now = datetime.now(timezone.utc)
    item_ids = {item.id for item in items}
    relevant = [submission for submission in submissions if submission.item_id in item_ids]
    by_item = {submission.item_id: submission for submission in relevant}
    manual_pending = any(
        item.item_type == "manual" and by_item.get(item.id) and by_item[item.id].review_status != "reviewed"
        for item in items
    )
    score = sum(submission.awarded_points for submission in relevant)
    completed_items = len(by_item)

    if homework.deadline.replace(tzinfo=timezone.utc) < now and completed_items == 0:
        return "closed", None
    if manual_pending:
        return "on_review", score
    if completed_items == 0:
        return "not_started", None
    if completed_items < len(items):
        return "in_progress", score
    return "checked", score


def build_homework_summary(
    homework: Homework,
    teacher: User,
    assignment: HomeworkAssignment,
    items: list[HomeworkItem],
    submissions: list[HomeworkSubmission],
) -> HomeworkSummaryOut:
    status, score = compute_assignment_status(homework, items, submissions, assignment)
    progress_label = f"{len(submissions)}/{len(items)} items completed"
    return HomeworkSummaryOut(
        assignment_id=assignment.id,
        homework_id=homework.id,
        title=homework.title,
        subject=homework.subject,
        teacher_name=teacher.full_name,
        deadline=homework.deadline.isoformat(),
        progress_label=progress_label,
        status=status,
        final_score=score,
        max_score=homework.max_score,
    )


@router.get("/homeworks/my", response_model=list[HomeworkSummaryOut])
def my_homeworks(db: Session = Depends(get_db), user: User = Depends(require_student)):
    assignments = (
        db.query(HomeworkAssignment)
        .filter(HomeworkAssignment.student_id == user.id)
        .order_by(HomeworkAssignment.id.asc())
        .all()
    )
    result = []
    for assignment in assignments:
        homework = db.query(Homework).filter(Homework.id == assignment.homework_id).first()
        teacher = db.query(User).filter(User.id == homework.teacher_id).first()
        items = db.query(HomeworkItem).filter(HomeworkItem.homework_id == homework.id).order_by(HomeworkItem.id.asc()).all()
        submissions = (
            db.query(HomeworkSubmission)
            .filter(HomeworkSubmission.assignment_id == assignment.id)
            .order_by(HomeworkSubmission.id.asc())
            .all()
        )
        result.append(build_homework_summary(homework, teacher, assignment, items, submissions))
    return result


@router.get("/homeworks/my/{assignment_id}", response_model=HomeworkDetailOut)
def my_homework_detail(assignment_id: int, db: Session = Depends(get_db), user: User = Depends(require_student)):
    assignment = (
        db.query(HomeworkAssignment)
        .filter(HomeworkAssignment.id == assignment_id, HomeworkAssignment.student_id == user.id)
        .first()
    )
    if not assignment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Homework assignment not found")

    homework = db.query(Homework).filter(Homework.id == assignment.homework_id).first()
    teacher = db.query(User).filter(User.id == homework.teacher_id).first()
    items = db.query(HomeworkItem).filter(HomeworkItem.homework_id == homework.id).order_by(HomeworkItem.id.asc()).all()
    submissions = (
        db.query(HomeworkSubmission)
        .filter(HomeworkSubmission.assignment_id == assignment.id)
        .order_by(HomeworkSubmission.id.asc())
        .all()
    )
    status_name, score = compute_assignment_status(homework, items, submissions, assignment)
    return HomeworkDetailOut(
        assignment_id=assignment.id,
        homework_id=homework.id,
        title=homework.title,
        subject=homework.subject,
        description=homework.description,
        teacher_name=teacher.full_name,
        deadline=homework.deadline.isoformat(),
        status=status_name,
        final_score=score,
        max_score=homework.max_score,
        requires_manual_review=homework.requires_manual_review,
        items=[serialize_item(item) for item in items],
    )


@router.post("/homeworks/my/{assignment_id}/submit-item", response_model=HomeworkSubmissionOut)
def submit_homework_item(
    assignment_id: int,
    data: HomeworkSubmissionIn,
    db: Session = Depends(get_db),
    user: User = Depends(require_student),
):
    assignment = (
        db.query(HomeworkAssignment)
        .filter(HomeworkAssignment.id == assignment_id, HomeworkAssignment.student_id == user.id)
        .first()
    )
    if not assignment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Homework assignment not found")

    item = (
        db.query(HomeworkItem)
        .filter(HomeworkItem.id == data.item_id, HomeworkItem.homework_id == assignment.homework_id)
        .first()
    )
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Homework item not found")

    existing = (
        db.query(HomeworkSubmission)
        .filter(HomeworkSubmission.assignment_id == assignment.id, HomeworkSubmission.item_id == item.id)
        .first()
    )
    if item.item_type == "test":
        is_correct = check_answer(data.answer, item.answer_key or "")
        awarded_points = item.max_points if is_correct else 0
        review_status = "reviewed"
    else:
        is_correct = None
        awarded_points = 0
        review_status = "pending"

    if existing:
        existing.answer = data.answer.strip()
        existing.is_correct = is_correct
        existing.awarded_points = awarded_points
        existing.review_status = review_status
        submission = existing
    else:
        submission = HomeworkSubmission(
            assignment_id=assignment.id,
            item_id=item.id,
            answer=data.answer.strip(),
            is_correct=is_correct,
            awarded_points=awarded_points,
            review_status=review_status,
        )
        db.add(submission)

    items = db.query(HomeworkItem).filter(HomeworkItem.homework_id == assignment.homework_id).all()
    db.flush()
    submissions = db.query(HomeworkSubmission).filter(HomeworkSubmission.assignment_id == assignment.id).all()
    homework = db.query(Homework).filter(Homework.id == assignment.homework_id).first()
    status_name, score = compute_assignment_status(homework, items, submissions, assignment)
    assignment.status = status_name
    assignment.final_score = score
    db.commit()
    db.refresh(submission)
    return HomeworkSubmissionOut(
        submission_id=submission.id,
        review_status=submission.review_status,
        is_correct=submission.is_correct,
        awarded_points=submission.awarded_points,
        status=status_name,
    )


@router.get("/teacher/homeworks", response_model=list[TeacherHomeworkOut])
def teacher_homeworks(db: Session = Depends(get_db), teacher: User = Depends(require_teacher)):
    homeworks = db.query(Homework).filter(Homework.teacher_id == teacher.id).order_by(Homework.id.asc()).all()
    result = []
    for homework in homeworks:
        items = db.query(HomeworkItem).filter(HomeworkItem.homework_id == homework.id).order_by(HomeworkItem.id.asc()).all()
        assignment_count = db.query(HomeworkAssignment).filter(HomeworkAssignment.homework_id == homework.id).count()
        result.append(
            TeacherHomeworkOut(
                homework_id=homework.id,
                title=homework.title,
                subject=homework.subject,
                deadline=homework.deadline.isoformat(),
                assignment_count=assignment_count,
                requires_manual_review=homework.requires_manual_review,
                max_score=homework.max_score,
                items=[serialize_item(item) for item in items],
            )
        )
    return result


@router.post("/teacher/homeworks", response_model=TeacherHomeworkOut, status_code=status.HTTP_201_CREATED)
def create_homework(data: HomeworkCreateIn, db: Session = Depends(get_db), teacher: User = Depends(require_teacher)):
    max_score = sum(item.max_points for item in data.items)
    requires_manual_review = any(item.item_type == "manual" for item in data.items)
    homework = Homework(
        title=data.title.strip(),
        subject=data.subject.strip(),
        description=data.description.strip(),
        teacher_id=teacher.id,
        deadline=data.deadline,
        max_score=max_score,
        requires_manual_review=requires_manual_review,
    )
    db.add(homework)
    db.flush()

    created_items = []
    for item_data in data.items:
        item = HomeworkItem(
            homework_id=homework.id,
            title=item_data.title.strip(),
            prompt=item_data.prompt.strip(),
            item_type=item_data.item_type,
            difficulty=item_data.difficulty,
            max_points=item_data.max_points,
            answer_key=item_data.answer_key.strip() if item_data.answer_key else None,
        )
        db.add(item)
        db.flush()
        created_items.append(item)

    for student_id in data.assignee_ids:
        assignment = HomeworkAssignment(
            homework_id=homework.id,
            student_id=student_id,
            status="not_started",
        )
        db.add(assignment)

    db.commit()
    assignment_count = db.query(HomeworkAssignment).filter(HomeworkAssignment.homework_id == homework.id).count()
    return TeacherHomeworkOut(
        homework_id=homework.id,
        title=homework.title,
        subject=homework.subject,
        deadline=homework.deadline.isoformat(),
        assignment_count=assignment_count,
        requires_manual_review=homework.requires_manual_review,
        max_score=homework.max_score,
        items=[serialize_item(item) for item in created_items],
    )
