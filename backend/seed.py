from datetime import datetime

from app.models.homework import Homework
from app.models.homework_assignment import HomeworkAssignment
from app.models.homework_item import HomeworkItem
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.fake_tasks import FAKE_TASKS
from app.models.learner_state import LearnerState
from app.models.task import Task
from app.models.user import User

DEMO_PASSWORD = "demo123"

DEMO_USERS = [
    {"email": "student@example.com", "full_name": "Alex Student", "role": "student"},
    {"email": "teacher@example.com", "full_name": "Maria Teacher", "role": "teacher"},
]

DEMO_TASKS = [
    {
        "id": task["id"],
        "title": f"{task['topic'].replace('_', ' ').title()} #{task['id']}",
        "body": task["question"],
        "difficulty": min(task["difficulty"], 3),
        "topic": task["topic"],
        "answer_key": task["answer"],
        "solution": task["solution"],
        "grade": task["grade"],
        "task_type": task["task_type"],
    }
    for task in FAKE_TASKS
]

DEMO_TASKS.extend(
    [
        {
            "title": "Essay reflection",
            "body": "Explain in 2-3 sentences why regular practice improves learning outcomes.",
            "difficulty": 2,
            "topic": "reflection",
            "answer_key": None,
            "solution": None,
            "grade": 7,
            "task_type": "manual",
        },
        {
            "title": "Quadratic roots",
            "body": "Find both roots of x^2 - 5x + 6 = 0.",
            "difficulty": 3,
            "topic": "algebra",
            "answer_key": "2, 3",
            "solution": "x^2 - 5x + 6 = (x - 2)(x - 3), so x = 2 or x = 3.",
            "grade": 8,
            "task_type": "open_answer",
        },
    ]
)


def seed_demo_data(db: Session):
    user_ids = {}
    for user_data in DEMO_USERS:
        user = db.query(User).filter(User.email == user_data["email"]).first()
        if not user:
            user = User(
                email=user_data["email"],
                full_name=user_data["full_name"],
                role=user_data["role"],
                password_hash=hash_password(DEMO_PASSWORD),
            )
            db.add(user)
            db.flush()

            if user.role == "student":
                db.add(LearnerState(user_id=user.id, skill_score=50))
        user_ids[user.email] = user.id

    if db.query(Task).count() == 0:
        db.add_all(Task(**task_data) for task_data in DEMO_TASKS)
        db.flush()

    if db.query(Homework).count() == 0:
        homework = Homework(
            title="Foundations Homework",
            subject="Mathematics",
            description="Complete one test item and one short explanation item.",
            teacher_id=user_ids["teacher@example.com"],
            deadline=datetime.fromisoformat("2099-03-05T18:00:00"),
            max_score=10,
            requires_manual_review=True,
        )
        db.add(homework)
        db.flush()

        db.add_all(
            [
                HomeworkItem(
                    homework_id=homework.id,
                    title="Solve an equation",
                    prompt="Solve x + 5 = 12",
                    item_type="test",
                    difficulty=1,
                    max_points=5,
                    answer_key="7",
                ),
                HomeworkItem(
                    homework_id=homework.id,
                    title="Explain your steps",
                    prompt="Explain how you isolated the variable.",
                    item_type="manual",
                    difficulty=1,
                    max_points=5,
                    answer_key=None,
                ),
            ]
        )
        db.flush()
        db.add(
            HomeworkAssignment(
                homework_id=homework.id,
                student_id=user_ids["student@example.com"],
                status="not_started",
            )
        )

    db.commit()


def run():
    from app.db.base import Base
    from app.db.session import SessionLocal, engine

    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed_demo_data(db)
    print("Seed done.")


if __name__ == "__main__":
    run()
