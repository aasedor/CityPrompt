"""Create model_library table for reusable 3D model storage

Revision ID: 015_create_model_library
Revises: 014_create_api_usage_logs
Create Date: 2026-03-07
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "015_create_model_library"
down_revision: Union[str, None] = "014_create_api_usage_logs"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE IF NOT EXISTS model_library (
            id UUID DEFAULT gen_random_uuid() NOT NULL,
            owner_id UUID NOT NULL,
            source_building_id UUID,
            source_project_id UUID,
            name VARCHAR(255) NOT NULL,
            description TEXT,
            category VARCHAR(50) NOT NULL DEFAULT 'other',
            tags JSONB DEFAULT '[]'::jsonb,
            model_url VARCHAR(500) NOT NULL,
            lod_urls JSONB,
            thumbnail_url VARCHAR(500),
            generation_prompt TEXT,
            generation_engine VARCHAR(20),
            architectural_style VARCHAR(50),
            is_public BOOLEAN DEFAULT false,
            use_count INTEGER DEFAULT 0,
            metadata JSONB,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
            PRIMARY KEY (id),
            FOREIGN KEY(owner_id) REFERENCES users (id) ON DELETE CASCADE,
            FOREIGN KEY(source_building_id) REFERENCES buildings (id) ON DELETE SET NULL,
            FOREIGN KEY(source_project_id) REFERENCES projects (id) ON DELETE SET NULL
        )
    """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_model_library_owner_id
        ON model_library (owner_id)
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_model_library_category
        ON model_library (category)
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_model_library_is_public
        ON model_library (is_public)
    """)


def downgrade() -> None:
    op.drop_index("ix_model_library_is_public", table_name="model_library")
    op.drop_index("ix_model_library_category", table_name="model_library")
    op.drop_index("ix_model_library_owner_id", table_name="model_library")
    op.drop_table("model_library")
