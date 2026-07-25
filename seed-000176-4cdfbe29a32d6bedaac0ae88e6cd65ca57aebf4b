"""Create urban_dna_scenarios table (Planning Agents scenario runs)

Revision ID: 024_create_urban_dna_scenarios
Revises: 023_create_policy_corpus_tables
Create Date: 2026-07-05
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "024_create_urban_dna_scenarios"
down_revision: Union[str, None] = "023_create_policy_corpus_tables"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE IF NOT EXISTS urban_dna_scenarios (
            id UUID DEFAULT gen_random_uuid() NOT NULL,
            snapshot_id UUID NOT NULL,
            scenario_id VARCHAR(60) NOT NULL,
            label VARCHAR(120) NOT NULL,
            status VARCHAR(12) NOT NULL DEFAULT 'pending',
            payload JSONB,
            error TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
            PRIMARY KEY (id),
            FOREIGN KEY(snapshot_id) REFERENCES urban_dna_snapshots (id) ON DELETE CASCADE
        )
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_urban_dna_scenarios_snapshot_id
        ON urban_dna_scenarios (snapshot_id)
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS urban_dna_scenarios")
