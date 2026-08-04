"""Add preview_url and preview_status to buildings, create render_previews table

Revision ID: 008_add_render_previews
Revises: 007_add_architectural_style
Create Date: 2026-02-25
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision: str = "008_add_render_previews"
down_revision: Union[str, None] = "007_add_architectural_style"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _column_exists(table: str, column: str) -> bool:
    conn = op.get_bind()
    result = conn.execute(
        sa.text(
            "SELECT EXISTS (SELECT 1 FROM information_schema.columns "
            "WHERE table_name = :table AND column_name = :column)"
        ),
        {"table": table, "column": column},
    )
    return result.scalar()


def _table_exists(table: str) -> bool:
    conn = op.get_bind()
    result = conn.execute(
        sa.text("SELECT EXISTS (SELECT 1 FROM information_schema.tables " "WHERE table_name = :table)"),
        {"table": table},
    )
    return result.scalar()


def upgrade() -> None:
    if not _column_exists("buildings", "preview_url"):
        op.add_column("buildings", sa.Column("preview_url", sa.String(500), nullable=True))
    if not _column_exists("buildings", "preview_status"):
        op.add_column("buildings", sa.Column("preview_status", sa.String(20), nullable=True, server_default="idle"))

    if not _table_exists("render_previews"):
        op.create_table(
            "render_previews",
            sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
            sa.Column(
                "building_id",
                UUID(as_uuid=True),
                sa.ForeignKey("buildings.id", ondelete="CASCADE"),
                nullable=False,
                index=True,
            ),
            sa.Column("image_url", sa.String(500), nullable=False),
            sa.Column("prompt", sa.Text(), nullable=True),
            sa.Column("style", sa.String(50), nullable=True),
            sa.Column("source_type", sa.String(20), nullable=False, server_default="text"),
            sa.Column("source_image_url", sa.String(500), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        )


def downgrade() -> None:
    if _table_exists("render_previews"):
        op.drop_table("render_previews")
    if _column_exists("buildings", "preview_status"):
        op.drop_column("buildings", "preview_status")
    if _column_exists("buildings", "preview_url"):
        op.drop_column("buildings", "preview_url")
