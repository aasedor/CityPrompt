"""Create dataset_cache and urban_dna_snapshots tables (Urban Intelligence DNA)

Revision ID: 022_create_urban_dna_tables
Revises: 021_add_previous_snapshot
Create Date: 2026-07-05
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "022_create_urban_dna_tables"
down_revision: Union[str, None] = "021_add_previous_snapshot"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE IF NOT EXISTS dataset_cache (
            id UUID DEFAULT gen_random_uuid() NOT NULL,
            dataset_id VARCHAR(120) NOT NULL,
            dataset_version VARCHAR(40) NOT NULL DEFAULT 'v1',
            bbox_hash VARCHAR(40) NOT NULL,
            features JSONB,
            feature_count INTEGER NOT NULL DEFAULT 0,
            source_status VARCHAR(20) NOT NULL DEFAULT 'ok',
            fetched_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
            expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
            PRIMARY KEY (id)
        )
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_dataset_cache_lookup
        ON dataset_cache (dataset_id, dataset_version, bbox_hash)
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_dataset_cache_expires_at
        ON dataset_cache (expires_at)
    """)

    op.execute("""
        CREATE TABLE IF NOT EXISTS urban_dna_snapshots (
            id UUID DEFAULT gen_random_uuid() NOT NULL,
            project_id UUID NOT NULL,
            zone_id UUID NOT NULL,
            city_id VARCHAR(40) NOT NULL DEFAULT 'osm',
            dna_schema_version VARCHAR(20) NOT NULL,
            dna JSONB,
            overall_confidence NUMERIC(4, 2),
            status VARCHAR(12) NOT NULL DEFAULT 'pending',
            error TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
            PRIMARY KEY (id),
            FOREIGN KEY(project_id) REFERENCES projects (id) ON DELETE CASCADE,
            FOREIGN KEY(zone_id) REFERENCES site_zones (id) ON DELETE CASCADE
        )
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_urban_dna_snapshots_project_id
        ON urban_dna_snapshots (project_id)
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_urban_dna_snapshots_zone_id_created_at
        ON urban_dna_snapshots (zone_id, created_at)
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS urban_dna_snapshots")
    op.execute("DROP TABLE IF EXISTS dataset_cache")
