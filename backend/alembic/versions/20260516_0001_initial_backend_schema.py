"""initial backend schema

Revision ID: 20260516_0001
Revises:
Create Date: 2026-05-16
"""

from alembic import op
import sqlalchemy as sa

revision = "20260516_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=50), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_role"), "users", ["role"], unique=False)

    op.create_table(
        "tasks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("difficulty", sa.Integer(), nullable=False),
        sa.Column("topic", sa.String(length=100), nullable=False),
        sa.Column("answer_key", sa.String(length=255), nullable=True),
        sa.Column("solution", sa.Text(), nullable=True),
        sa.Column("grade", sa.Integer(), nullable=True),
        sa.Column("task_type", sa.String(length=50), nullable=False),
        sa.Column("is_archived", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_tasks_difficulty"), "tasks", ["difficulty"], unique=False)
    op.create_index(op.f("ix_tasks_is_archived"), "tasks", ["is_archived"], unique=False)
    op.create_index(op.f("ix_tasks_task_type"), "tasks", ["task_type"], unique=False)
    op.create_index(op.f("ix_tasks_topic"), "tasks", ["topic"], unique=False)

    op.create_table(
        "homeworks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("subject", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("teacher_id", sa.Integer(), nullable=False),
        sa.Column("deadline", sa.DateTime(timezone=True), nullable=False),
        sa.Column("max_score", sa.Integer(), nullable=False),
        sa.Column("requires_manual_review", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["teacher_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_homeworks_deadline"), "homeworks", ["deadline"], unique=False)
    op.create_index(op.f("ix_homeworks_subject"), "homeworks", ["subject"], unique=False)
    op.create_index(op.f("ix_homeworks_teacher_id"), "homeworks", ["teacher_id"], unique=False)
    op.create_index(op.f("ix_homeworks_title"), "homeworks", ["title"], unique=False)

    op.create_table(
        "learner_states",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("skill_score", sa.Integer(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("user_id"),
    )

    op.create_table(
        "learner_topic_states",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("external_user_key", sa.String(length=120), nullable=True),
        sa.Column("topic", sa.String(length=100), nullable=False),
        sa.Column("skill_score", sa.Integer(), nullable=False),
        sa.Column("current_difficulty", sa.Integer(), nullable=False),
        sa.Column("attempts_count", sa.Integer(), nullable=False),
        sa.Column("correct_count", sa.Integer(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("external_user_key", "topic", name="uq_learner_topic_state_external_topic"),
        sa.UniqueConstraint("user_id", "topic", name="uq_learner_topic_state_user_topic"),
    )
    op.create_index(op.f("ix_learner_topic_states_external_user_key"), "learner_topic_states", ["external_user_key"], unique=False)
    op.create_index(op.f("ix_learner_topic_states_topic"), "learner_topic_states", ["topic"], unique=False)
    op.create_index(op.f("ix_learner_topic_states_user_id"), "learner_topic_states", ["user_id"], unique=False)

    op.create_table(
        "homework_assignments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("homework_id", sa.Integer(), nullable=False),
        sa.Column("student_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("final_score", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["homework_id"], ["homeworks.id"]),
        sa.ForeignKeyConstraint(["student_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_homework_assignments_homework_id"), "homework_assignments", ["homework_id"], unique=False)
    op.create_index(op.f("ix_homework_assignments_status"), "homework_assignments", ["status"], unique=False)
    op.create_index(op.f("ix_homework_assignments_student_id"), "homework_assignments", ["student_id"], unique=False)

    op.create_table(
        "homework_items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("homework_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("prompt", sa.Text(), nullable=False),
        sa.Column("item_type", sa.String(length=50), nullable=False),
        sa.Column("difficulty", sa.Integer(), nullable=False),
        sa.Column("max_points", sa.Integer(), nullable=False),
        sa.Column("answer_key", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["homework_id"], ["homeworks.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_homework_items_homework_id"), "homework_items", ["homework_id"], unique=False)
    op.create_index(op.f("ix_homework_items_item_type"), "homework_items", ["item_type"], unique=False)

    op.create_table(
        "submissions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("task_id", sa.Integer(), nullable=False),
        sa.Column("answer", sa.Text(), nullable=False),
        sa.Column("expected_answer", sa.String(length=255), nullable=True),
        sa.Column("is_correct", sa.Boolean(), nullable=False),
        sa.Column("score_delta", sa.Integer(), nullable=False),
        sa.Column("attempt_number", sa.Integer(), nullable=False),
        sa.Column("time_spent_seconds", sa.Integer(), nullable=True),
        sa.Column("feedback", sa.Text(), nullable=True),
        sa.Column("mode", sa.String(length=50), nullable=False),
        sa.Column("submitted_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["task_id"], ["tasks.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_submissions_mode"), "submissions", ["mode"], unique=False)
    op.create_index(op.f("ix_submissions_task_id"), "submissions", ["task_id"], unique=False)
    op.create_index(op.f("ix_submissions_user_id"), "submissions", ["user_id"], unique=False)

    op.create_table(
        "practice_attempts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("external_user_key", sa.String(length=120), nullable=True),
        sa.Column("task_id", sa.Integer(), nullable=False),
        sa.Column("topic", sa.String(length=100), nullable=False),
        sa.Column("answer", sa.Text(), nullable=False),
        sa.Column("expected_answer", sa.String(length=255), nullable=True),
        sa.Column("is_correct", sa.Boolean(), nullable=False),
        sa.Column("mode", sa.String(length=50), nullable=False),
        sa.Column("submitted_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["task_id"], ["tasks.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_practice_attempts_external_user_key"), "practice_attempts", ["external_user_key"], unique=False)
    op.create_index(op.f("ix_practice_attempts_is_correct"), "practice_attempts", ["is_correct"], unique=False)
    op.create_index(op.f("ix_practice_attempts_mode"), "practice_attempts", ["mode"], unique=False)
    op.create_index(op.f("ix_practice_attempts_task_id"), "practice_attempts", ["task_id"], unique=False)
    op.create_index(op.f("ix_practice_attempts_topic"), "practice_attempts", ["topic"], unique=False)
    op.create_index(op.f("ix_practice_attempts_user_id"), "practice_attempts", ["user_id"], unique=False)

    op.create_table(
        "homework_submissions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("assignment_id", sa.Integer(), nullable=False),
        sa.Column("item_id", sa.Integer(), nullable=False),
        sa.Column("answer", sa.Text(), nullable=False),
        sa.Column("expected_answer", sa.String(length=255), nullable=True),
        sa.Column("is_correct", sa.Boolean(), nullable=True),
        sa.Column("awarded_points", sa.Integer(), nullable=False),
        sa.Column("review_status", sa.String(length=50), nullable=False),
        sa.Column("review_comment", sa.Text(), nullable=True),
        sa.Column("submitted_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["assignment_id"], ["homework_assignments.id"]),
        sa.ForeignKeyConstraint(["item_id"], ["homework_items.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_homework_submissions_assignment_id"), "homework_submissions", ["assignment_id"], unique=False)
    op.create_index(op.f("ix_homework_submissions_item_id"), "homework_submissions", ["item_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_homework_submissions_item_id"), table_name="homework_submissions")
    op.drop_index(op.f("ix_homework_submissions_assignment_id"), table_name="homework_submissions")
    op.drop_table("homework_submissions")
    op.drop_index(op.f("ix_practice_attempts_user_id"), table_name="practice_attempts")
    op.drop_index(op.f("ix_practice_attempts_topic"), table_name="practice_attempts")
    op.drop_index(op.f("ix_practice_attempts_task_id"), table_name="practice_attempts")
    op.drop_index(op.f("ix_practice_attempts_mode"), table_name="practice_attempts")
    op.drop_index(op.f("ix_practice_attempts_is_correct"), table_name="practice_attempts")
    op.drop_index(op.f("ix_practice_attempts_external_user_key"), table_name="practice_attempts")
    op.drop_table("practice_attempts")
    op.drop_index(op.f("ix_submissions_user_id"), table_name="submissions")
    op.drop_index(op.f("ix_submissions_task_id"), table_name="submissions")
    op.drop_index(op.f("ix_submissions_mode"), table_name="submissions")
    op.drop_table("submissions")
    op.drop_index(op.f("ix_homework_items_item_type"), table_name="homework_items")
    op.drop_index(op.f("ix_homework_items_homework_id"), table_name="homework_items")
    op.drop_table("homework_items")
    op.drop_index(op.f("ix_homework_assignments_student_id"), table_name="homework_assignments")
    op.drop_index(op.f("ix_homework_assignments_status"), table_name="homework_assignments")
    op.drop_index(op.f("ix_homework_assignments_homework_id"), table_name="homework_assignments")
    op.drop_table("homework_assignments")
    op.drop_index(op.f("ix_learner_topic_states_user_id"), table_name="learner_topic_states")
    op.drop_index(op.f("ix_learner_topic_states_topic"), table_name="learner_topic_states")
    op.drop_index(op.f("ix_learner_topic_states_external_user_key"), table_name="learner_topic_states")
    op.drop_table("learner_topic_states")
    op.drop_table("learner_states")
    op.drop_index(op.f("ix_homeworks_title"), table_name="homeworks")
    op.drop_index(op.f("ix_homeworks_teacher_id"), table_name="homeworks")
    op.drop_index(op.f("ix_homeworks_subject"), table_name="homeworks")
    op.drop_index(op.f("ix_homeworks_deadline"), table_name="homeworks")
    op.drop_table("homeworks")
    op.drop_index(op.f("ix_tasks_topic"), table_name="tasks")
    op.drop_index(op.f("ix_tasks_task_type"), table_name="tasks")
    op.drop_index(op.f("ix_tasks_is_archived"), table_name="tasks")
    op.drop_index(op.f("ix_tasks_difficulty"), table_name="tasks")
    op.drop_table("tasks")
    op.drop_index(op.f("ix_users_role"), table_name="users")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
