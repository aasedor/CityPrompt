"""Add previous_snapshot column to zone_history

Revision ID: 021_add_previous_snapshot
Revises: 020_create_zone_history
Create Date: 2026-04-06
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "021_add_previous_snapshot"
down_revision: Union[str, None] = "020_create_zone_history"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(sa.text(
        "ALTER TABLE zone_history ADD COLUMN IF NOT EXISTS previous_snapshot JSONB"
    ))


def downgrade() -> None:
    op.execute(sa.text(
        "ALTER TABLE zone_history DROP COLUMN IF EXISTS previous_snapshot"
    ))
