"""Create policy_documents and policy_chunks tables (Policy Intelligence Engine)

Revision ID: 023_create_policy_corpus_tables
Revises: 022_create_urban_dna_tables
Create Date: 2026-07-05
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "023_create_policy_corpus_tables"
down_revision: Union[str, None] = "022_create_urban_dna_tables"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE IF NOT EXISTS policy_documents (
            id UUID DEFAULT gen_random_uuid() NOT NULL,
            city VARCHAR(40) NOT NULL,
            slug VARCHAR(120) NOT NULL,
            title VARCHAR(255) NOT NULL,
            instrument_type VARCHAR(30) NOT NULL DEFAULT 'policy',
            source_url VARCHAR(600) NOT NULL,
            storage_url VARCHAR(600),
            effective_date TIMESTAMP WITH TIME ZONE,
            repealed_date TIMESTAMP WITH TIME ZONE,
            version VARCHAR(40) NOT NULL DEFAULT 'v1',
            status VARCHAR(20) NOT NULL DEFAULT 'active',
            page_count INTEGER,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
            PRIMARY KEY (id)
        )
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_policy_documents_city ON policy_documents (city)
    """)
    op.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS ix_policy_documents_city_slug_version
        ON policy_documents (city, slug, version)
    """)

    op.execute("""
        CREATE TABLE IF NOT EXISTS policy_chunks (
            id UUID DEFAULT gen_random_uuid() NOT NULL,
            policy_document_id UUID NOT NULL,
            section_label VARCHAR(255),
            page_start INTEGER NOT NULL,
            page_end INTEGER NOT NULL,
            text TEXT NOT NULL,
            token_count INTEGER NOT NULL DEFAULT 0,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
            PRIMARY KEY (id),
            FOREIGN KEY(policy_document_id) REFERENCES policy_documents (id) ON DELETE CASCADE
        )
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_policy_chunks_document_id
        ON policy_chunks (policy_document_id)
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS policy_chunks")
    op.execute("DROP TABLE IF EXISTS policy_documents")
