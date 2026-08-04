"""Create master_plan_2d_options table

Revision ID: 016_master_plan_2d
Revises: 015_create_model_library
Create Date: 2026-03-10
"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "016_master_plan_2d"
down_revision: Union[str, None] = "015_create_model_library"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS master_plan_2d_options (
            id UUID DEFAULT gen_random_uuid() NOT NULL,
            project_id UUID NOT NULL,
            label VARCHAR(120) NOT NULL,
            style_preset VARCHAR(80) NOT NULL,
            variant_index INTEGER NOT NULL DEFAULT 0,
            preview_url TEXT NOT NULL,
            plan_svg TEXT NOT NULL,
            metadata JSONB,
            is_selected BOOLEAN NOT NULL DEFAULT false,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
            PRIMARY KEY (id),
            FOREIGN KEY(project_id) REFERENCES projects (id) ON DELETE CASCADE
        )
    """
    )

    op.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_master_plan_2d_options_project_id
        ON master_plan_2d_options (project_id)
    """
    )
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_master_plan_2d_options_project_variant
        ON master_plan_2d_options (project_id, variant_index)
    """
    )


def downgrade() -> None:
    op.drop_index("ix_master_plan_2d_options_project_variant", table_name="master_plan_2d_options")
    op.drop_index("ix_master_plan_2d_options_project_id", table_name="master_plan_2d_options")
    op.drop_table("master_plan_2d_options")
