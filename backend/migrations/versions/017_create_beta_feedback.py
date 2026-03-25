"""Create beta_feedback table for tester suggestions

Revision ID: 017_create_beta_feedback
Revises: 016_master_plan_2d
Create Date: 2026-03-24
"""

from typing import Sequence, Union

from alembic import op

revision: str = "017_create_beta_feedback"
down_revision: Union[str, None] = "016_master_plan_2d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE IF NOT EXISTS beta_feedback (
            id UUID DEFAULT gen_random_uuid() NOT NULL,
            author_id UUID NOT NULL,
            category VARCHAR(30) NOT NULL DEFAULT 'suggestion',
            text TEXT NOT NULL,
            page_url VARCHAR(500),
            status VARCHAR(20) NOT NULL DEFAULT 'open',
            admin_notes TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
            PRIMARY KEY (id),
            FOREIGN KEY(author_id) REFERENCES users (id) ON DELETE CASCADE
        )
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_beta_feedback_author_id
        ON beta_feedback (author_id)
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_beta_feedback_status
        ON beta_feedback (status)
    """)


def downgrade() -> None:
    op.drop_index("ix_beta_feedback_status", table_name="beta_feedback")
    op.drop_index("ix_beta_feedback_author_id", table_name="beta_feedback")
    op.drop_table("beta_feedback")
