"""Add one canonical active site boundary per project.

Revision ID: 027_add_active_site_boundary
Revises: 026_widen_generation_mode
Create Date: 2026-08-03
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "027_add_active_site_boundary"
down_revision: Union[str, None] = "026_widen_generation_mode"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "site_zones",
        sa.Column(
            "is_active_boundary",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )
    # Preserve every legacy boundary, but nominate the most recently updated
    # one as authoritative. Older duplicates remain visible and recoverable.
    op.execute(
        """
        WITH ranked_boundaries AS (
            SELECT id,
                   ROW_NUMBER() OVER (
                       PARTITION BY project_id
                       ORDER BY updated_at DESC NULLS LAST,
                                created_at DESC NULLS LAST,
                                id DESC
                   ) AS boundary_rank
            FROM site_zones
            WHERE zone_type = 'site_boundary'
        )
        UPDATE site_zones AS zone
        SET is_active_boundary = (ranked.boundary_rank = 1)
        FROM ranked_boundaries AS ranked
        WHERE zone.id = ranked.id
        """
    )
    op.create_index(
        "uq_site_zones_active_boundary_per_project",
        "site_zones",
        ["project_id"],
        unique=True,
        postgresql_where=sa.text(
            "zone_type = 'site_boundary' AND is_active_boundary = true"
        ),
    )


def downgrade() -> None:
    op.drop_index(
        "uq_site_zones_active_boundary_per_project",
        table_name="site_zones",
    )
    op.drop_column("site_zones", "is_active_boundary")
