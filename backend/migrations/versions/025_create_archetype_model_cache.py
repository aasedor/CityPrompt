"""Create archetype_model_cache table (generate-once GLB cache per archetype+variant+engine)

Revision ID: 025_create_archetype_model_cache
Revises: 024_create_urban_dna_scenarios
Create Date: 2026-07-10
"""

from typing import Sequence, Union

from alembic import op

revision: str = "025_create_archetype_model_cache"
down_revision: Union[str, None] = "024_create_urban_dna_scenarios"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # The UNIQUE constraint doubles as the concurrency-control primitive:
    # workers claim a key via INSERT ... ON CONFLICT DO NOTHING.
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS archetype_model_cache (
            id UUID DEFAULT gen_random_uuid() NOT NULL,
            archetype_id VARCHAR(120) NOT NULL,
            variant_id VARCHAR(120) NOT NULL DEFAULT 'default',
            engine VARCHAR(20) NOT NULL,
            status VARCHAR(16) NOT NULL DEFAULT 'generating',
            model_key VARCHAR(500),
            lod_keys JSONB,
            thumbnail_key VARCHAR(500),
            source_task_id VARCHAR(100),
            source_building_id UUID REFERENCES buildings (id) ON DELETE SET NULL,
            generation_mode VARCHAR(10) DEFAULT 'text',
            generation_prompt TEXT,
            size_bytes INTEGER,
            use_count INTEGER DEFAULT 0,
            error TEXT,
            metadata JSONB,
            claimed_at TIMESTAMP WITH TIME ZONE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
            PRIMARY KEY (id),
            UNIQUE (archetype_id, variant_id, engine)
        )
    """
    )
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_archetype_model_cache_status
        ON archetype_model_cache (status)
    """
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS archetype_model_cache")
