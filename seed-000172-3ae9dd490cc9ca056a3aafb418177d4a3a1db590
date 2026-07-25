"""Create zone_history table for design version control

Revision ID: 020_create_zone_history
Revises: 019_create_render_audit_logs
Create Date: 2026-04-06
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "020_create_zone_history"
down_revision: Union[str, None] = "019_create_render_audit_logs"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create action enum
    op.execute(sa.text(
        "CREATE TYPE zone_history_action AS ENUM ('create', 'update', 'delete')"
    ))

    op.execute(sa.text("""
        CREATE TABLE IF NOT EXISTS zone_history (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            zone_id UUID NOT NULL,
            project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
            action zone_history_action NOT NULL,
            snapshot JSONB NOT NULL,
            user_id UUID REFERENCES users(id) ON DELETE SET NULL,
            user_email VARCHAR(255),
            description VARCHAR(500),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
        );
        CREATE INDEX IF NOT EXISTS ix_zone_history_zone_id ON zone_history(zone_id);
        CREATE INDEX IF NOT EXISTS ix_zone_history_project_id ON zone_history(project_id);
        CREATE INDEX IF NOT EXISTS ix_zone_history_created_at ON zone_history(created_at DESC);
    """))


def downgrade() -> None:
    op.execute(sa.text("DROP TABLE IF EXISTS zone_history"))
    op.execute(sa.text("DROP TYPE IF EXISTS zone_history_action"))
