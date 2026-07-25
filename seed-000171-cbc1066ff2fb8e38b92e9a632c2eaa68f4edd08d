"""Create render_audit_logs table for QA render history

Revision ID: 019_create_render_audit_logs
Revises: 018_add_render_credits
Create Date: 2026-03-26
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "019_create_render_audit_logs"
down_revision: Union[str, None] = "018_add_render_credits"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(sa.text("""
        CREATE TABLE IF NOT EXISTS render_audit_logs (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            user_email VARCHAR(255) NOT NULL,
            project_id UUID,
            model VARCHAR(100) NOT NULL,
            tokens_spent INTEGER DEFAULT 0,
            input_image_key VARCHAR(500),
            output_image_key VARCHAR(500),
            prompt_preview TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
        );
        CREATE INDEX IF NOT EXISTS ix_render_audit_logs_user_id ON render_audit_logs(user_id);
        CREATE INDEX IF NOT EXISTS ix_render_audit_logs_created_at ON render_audit_logs(created_at DESC);
    """))


def downgrade() -> None:
    op.execute(sa.text("DROP TABLE IF EXISTS render_audit_logs"))
