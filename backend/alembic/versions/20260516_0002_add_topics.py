"""add topics

Revision ID: 20260516_0002
Revises: 20260516_0001
Create Date: 2026-05-16 23:40:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20260516_0002'
down_revision: Union[str, None] = '20260516_0001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create topics table
    op.create_table('topics',
        sa.Column('topic_id', sa.String(length=100), nullable=False),
        sa.Column('topic_name', sa.String(length=150), nullable=False),
        sa.Column('subject_id', sa.String(length=50), server_default='math', nullable=False),
        sa.Column('subject_name', sa.String(length=100), server_default='Математика', nullable=False),
        sa.PrimaryKeyConstraint('topic_id')
    )

    # 2. Update tasks table
    op.add_column('tasks', sa.Column('subject_id', sa.String(length=50), server_default='math', nullable=False))
    op.add_column('tasks', sa.Column('subject_name', sa.String(length=100), server_default='Математика', nullable=False))
    op.create_foreign_key('fk_tasks_topic_topics', 'tasks', 'topics', ['topic'], ['topic_id'])

    # 3. Update learner_topic_states table
    op.create_foreign_key('fk_learner_topic_states_topic_topics', 'learner_topic_states', 'topics', ['topic'], ['topic_id'])

    # 4. Update practice_attempts table
    op.create_foreign_key('fk_practice_attempts_topic_topics', 'practice_attempts', 'topics', ['topic'], ['topic_id'])


def downgrade() -> None:
    op.drop_constraint('fk_practice_attempts_topic_topics', 'practice_attempts', type_='foreignkey')
    op.drop_constraint('fk_learner_topic_states_topic_topics', 'learner_topic_states', type_='foreignkey')
    
    op.drop_constraint('fk_tasks_topic_topics', 'tasks', type_='foreignkey')
    op.drop_column('tasks', 'subject_name')
    op.drop_column('tasks', 'subject_id')
    
    op.drop_table('topics')
