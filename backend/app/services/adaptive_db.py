from collections import Counter

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.learner_state import LearnerState
from app.models.learner_topic_state import LearnerTopicState
from app.models.practice_attempt import PracticeAttempt
from app.models.submission import Submission
from app.models.task import Task


def clamp_score(value: int) -> int:
    return max(0, min(100, value))


def difficulty_for_score(skill_score: int) -> int:
    if skill_score < 40:
        return 1
    if skill_score < 70:
        return 2
    return 3


def skill_for_difficulty(difficulty: int) -> int:
    if difficulty <= 1:
        return 30
    if difficulty == 2:
        return 55
    return 80


def get_or_create_global_state(db: Session, user_id: int) -> LearnerState:
    state = db.query(LearnerState).filter(LearnerState.user_id == user_id).first()
    if not state:
        state = LearnerState(user_id=user_id, skill_score=50)
        db.add(state)
        db.flush()
    return state


def get_or_create_topic_state(
    db: Session,
    topic: str,
    user_id: int | None = None,
    external_user_key: str | None = None,
) -> LearnerTopicState:
    query = db.query(LearnerTopicState).filter(LearnerTopicState.topic == topic)
    if user_id is not None:
        query = query.filter(LearnerTopicState.user_id == user_id)
    else:
        query = query.filter(LearnerTopicState.external_user_key == external_user_key)

    state = query.first()
    if state:
        return state

    is_legacy_external = user_id is None
    state = LearnerTopicState(
        user_id=user_id,
        external_user_key=external_user_key,
        topic=topic,
        skill_score=30 if is_legacy_external else 50,
        current_difficulty=1 if is_legacy_external else 2,
    )
    db.add(state)
    db.flush()
    return state


def update_topic_state(state: LearnerTopicState, task: Task, is_correct: bool) -> int:
    delta = 5 * task.difficulty if is_correct else -5 * task.difficulty
    state.skill_score = clamp_score(state.skill_score + delta)
    state.current_difficulty = difficulty_for_score(state.skill_score)
    state.attempts_count += 1
    if is_correct:
        state.correct_count += 1
    return delta


def update_global_state(state: LearnerState, task: Task, is_correct: bool) -> int:
    delta = 5 * task.difficulty if is_correct else -5 * task.difficulty
    state.skill_score = clamp_score(state.skill_score + delta)
    return delta


def next_task_query(db: Session, topic: str | None = None, include_archived: bool = False):
    query = db.query(Task)
    if not include_archived:
        query = query.filter(Task.is_archived.is_(False))
    if topic:
        query = query.filter(Task.topic == topic)
    return query


def pick_next_task(
    db: Session,
    topic: str | None = None,
    difficulty: int | None = None,
    user_id: int | None = None,
    external_user_key: str | None = None,
) -> Task | None:
    resolved_topic = topic
    target_difficulty = difficulty

    if resolved_topic and target_difficulty is None:
        state = get_or_create_topic_state(db, resolved_topic, user_id=user_id, external_user_key=external_user_key)
        target_difficulty = state.current_difficulty

    if target_difficulty is None:
        target_difficulty = 2
        if user_id is not None:
            state = db.query(LearnerState).filter(LearnerState.user_id == user_id).first()
            target_difficulty = difficulty_for_score(state.skill_score if state else 50)

    query = next_task_query(db, resolved_topic).filter(Task.difficulty == target_difficulty)
    task = query.order_by(Task.id.asc()).first()
    if task:
        return task

    fallback_query = next_task_query(db, resolved_topic)
    return fallback_query.order_by(func.abs(Task.difficulty - target_difficulty), Task.id.asc()).first()


def next_attempt_number(db: Session, user_id: int, task_id: int) -> int:
    previous = (
        db.query(func.count(Submission.id))
        .filter(Submission.user_id == user_id, Submission.task_id == task_id)
        .scalar()
        or 0
    )
    return previous + 1


def record_practice_attempt(
    db: Session,
    task: Task,
    answer: str,
    is_correct: bool,
    user_id: int | None = None,
    external_user_key: str | None = None,
    mode: str = "self_education",
) -> PracticeAttempt:
    attempt = PracticeAttempt(
        user_id=user_id,
        external_user_key=external_user_key,
        task_id=task.id,
        topic=task.topic,
        answer=answer,
        expected_answer=task.answer_key,
        is_correct=is_correct,
        mode=mode,
    )
    db.add(attempt)
    return attempt


def legacy_stats_for_user(db: Session, user_key: str) -> dict:
    records = db.query(PracticeAttempt).filter(PracticeAttempt.external_user_key == user_key).all()
    total = len(records)
    correct = sum(1 for record in records if record.is_correct)
    weak_counter: Counter[str] = Counter(record.topic for record in records if not record.is_correct)

    state = (
        db.query(LearnerTopicState)
        .filter(LearnerTopicState.external_user_key == user_key)
        .order_by(LearnerTopicState.updated_at.desc())
        .first()
    )

    return {
        "user_id": user_key,
        "total_answers": total,
        "correct_answers": correct,
        "accuracy": round(correct / total, 2) if total else 0.0,
        "current_difficulty": state.current_difficulty if state else 1,
        "weak_topics": [topic for topic, _ in weak_counter.most_common(3)],
    }
