"""
Endpoint for per-user statistics (MVP, in-memory data).
"""

from collections import Counter

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.services.adaptive import USER_ANSWERS, get_user_state

router = APIRouter(prefix="/stats", tags=["stats"])


class UserStatsOut(BaseModel):
    user_id: str
    total_answers: int
    correct_answers: int
    accuracy: float
    current_difficulty: int
    weak_topics: list[str]


def _compute_weak_topics(user_id: str) -> list[str]:
    """Return topics where the user has the most errors.

    Only topics with at least 1 wrong answer are considered.
    Returns up to 3 weakest topics sorted by error count descending.
    """
    errors: Counter[str] = Counter()
    for rec in USER_ANSWERS:
        if rec["user_id"] == user_id and not rec["was_correct"]:
            errors[rec["topic"]] += 1

    if not errors:
        return []

    # Return up to 3 topics, ordered by error count (most errors first).
    return [topic for topic, _ in errors.most_common(3)]


@router.get("/{user_id}", response_model=UserStatsOut)
def user_stats(user_id: str):
    """Return aggregated statistics for *user_id*."""
    state = get_user_state(user_id)
    user_records = [r for r in USER_ANSWERS if r["user_id"] == user_id]

    total = len(user_records)
    correct = sum(1 for r in user_records if r["was_correct"])
    accuracy = round(correct / total, 2) if total else 0.0

    return UserStatsOut(
        user_id=user_id,
        total_answers=total,
        correct_answers=correct,
        accuracy=accuracy,
        current_difficulty=state["current_difficulty"],
        weak_topics=_compute_weak_topics(user_id),
    )
