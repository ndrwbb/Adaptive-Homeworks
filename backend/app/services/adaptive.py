"""
In-memory adaptive difficulty service for the MVP.

Stores user state and answer history in module-level dicts/lists.
Replace with database-backed storage once the schema is finalised.
"""

from __future__ import annotations

from app.fake_tasks import get_all_tasks

# ── In-memory stores ───────────────────────────────────────────
USER_STATE: dict[str, dict] = {}
USER_ANSWERS: list[dict] = []


def _default_state(user_id: str) -> dict:
    return {
        "user_id": user_id,
        "current_difficulty": 1,
    }


# ── Public API ─────────────────────────────────────────────────

def get_user_state(user_id: str) -> dict:
    """Return the current adaptive state for *user_id*, creating it if needed."""
    if user_id not in USER_STATE:
        USER_STATE[user_id] = _default_state(user_id)
    return USER_STATE[user_id]


def update_user_state(user_id: str, topic: str, was_correct: bool) -> dict:
    """Adjust difficulty after an answer and return the updated state.

    Rules:
      • correct  → difficulty += 1  (max 5)
      • wrong    → difficulty -= 1  (min 1)
    """
    state = get_user_state(user_id)
    if was_correct:
        state["current_difficulty"] = min(state["current_difficulty"] + 1, 5)
    else:
        state["current_difficulty"] = max(state["current_difficulty"] - 1, 1)
    return state


def record_answer(user_id: str, task_id: int, topic: str, was_correct: bool) -> None:
    """Append an answer record to the global history list."""
    USER_ANSWERS.append(
        {
            "user_id": user_id,
            "task_id": task_id,
            "topic": topic,
            "was_correct": was_correct,
        }
    )


def get_next_task_for_user(user_id: str, topic: str | None = None) -> dict | None:
    """Pick the next task whose difficulty is closest to the user's current level.

    If *topic* is given, only tasks of that topic are considered.
    Returns the task dict **without** the ``answer`` field, or ``None``
    if no matching task exists.
    """
    state = get_user_state(user_id)
    target = state["current_difficulty"]
    tasks = get_all_tasks()

    if topic:
        tasks = [t for t in tasks if t["topic"] == topic]

    if not tasks:
        return None

    # Pick the task with the smallest |difficulty - target|; break ties by id.
    best = min(tasks, key=lambda t: (abs(t["difficulty"] - target), t["id"]))

    # Never expose the correct answer before the user submits.
    safe = {k: v for k, v in best.items() if k != "answer"}
    return safe
