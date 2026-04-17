"""Endpoint for legacy per-user self-education statistics."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.services.adaptive_db import legacy_stats_for_user

router = APIRouter(prefix="/stats", tags=["stats"])


class UserStatsOut(BaseModel):
    user_id: str
    total_answers: int
    correct_answers: int
    accuracy: float
    current_difficulty: int
    weak_topics: list[str]

@router.get("/{user_id}", response_model=UserStatsOut)
def user_stats(user_id: str, db: Session = Depends(get_db)):
    """Return aggregated legacy self-education statistics for *user_id*."""
    return UserStatsOut(**legacy_stats_for_user(db, user_id))
