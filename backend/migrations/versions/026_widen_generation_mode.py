"""Widen archetype_model_cache.generation_mode to VARCHAR(20)

The new "multi_image" prewarm mode is 11 characters — one more than the
original VARCHAR(10) — and PostgreSQL raises StringDataRightTruncation on
over-length varchar input, which would fail every multi-image claim.

Revision ID: 026_widen_generation_mode
Revises: 025_create_archetype_model_cache
Create Date: 2026-07-11
"""

from typing import Sequence, Union

from alembic import op

revision: str = "026_widen_generation_mode"
down_revision: Union[str, None] = "025_create_archetype_model_cache"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TABLE archetype_model_cache ALTER COLUMN generation_mode TYPE VARCHAR(20)")


def downgrade() -> None:
    op.execute("ALTER TABLE archetype_model_cache ALTER COLUMN generation_mode TYPE VARCHAR(10)")
