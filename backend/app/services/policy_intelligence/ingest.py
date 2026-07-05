"""Policy corpus ingestion: PDF bytes -> MinIO -> page-anchored chunks -> Postgres.

Page extraction uses PyMuPDF directly (per-page text) rather than the Documents
pipeline's single-blob extraction — citations need page anchors. Idempotent per
(city, slug, version): re-ingesting replaces the document and its chunks.
"""

from __future__ import annotations

import logging
from datetime import datetime

import fitz  # PyMuPDF
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.services.policy_intelligence.chunker import chunk_pages

logger = logging.getLogger(__name__)


def extract_page_texts(pdf_bytes: bytes) -> list[str]:
    with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
        return [page.get_text("text") for page in doc]


def ingest_policy_pdf(
    session: Session,
    *,
    city: str,
    slug: str,
    title: str,
    source_url: str,
    pdf_bytes: bytes,
    instrument_type: str = "policy",
    effective_date: datetime | None = None,
    repealed_date: datetime | None = None,
    version: str = "v1",
):
    """Store + chunk one policy PDF. Returns the PolicyDocument row."""
    from app.models.models import PolicyChunk, PolicyDocument
    from app.tasks.processing import _upload_to_storage

    settings = get_settings()

    page_texts = extract_page_texts(pdf_bytes)
    chunks = chunk_pages(page_texts)
    if not chunks:
        raise ValueError(f"{slug}: no extractable text (scanned PDF without OCR?)")

    storage_key = f"{settings.policy_corpus_bucket_prefix}/{city}/{slug}/{version}.pdf"
    try:
        storage_url = _upload_to_storage(storage_key, pdf_bytes, "application/pdf")
    except Exception as exc:  # noqa: BLE001 — storage is nice-to-have; chunks are the product
        logger.warning("MinIO upload failed for %s (%s); continuing without storage_url", slug, exc)
        storage_url = None

    existing = (
        session.query(PolicyDocument)
        .filter_by(city=city, slug=slug, version=version)
        .first()
    )
    if existing is not None:
        session.delete(existing)  # cascades to chunks
        session.flush()

    document = PolicyDocument(
        city=city,
        slug=slug,
        title=title,
        instrument_type=instrument_type,
        source_url=source_url,
        storage_url=storage_url,
        effective_date=effective_date,
        repealed_date=repealed_date,
        version=version,
        status="active",
        page_count=len(page_texts),
    )
    session.add(document)
    session.flush()

    for chunk in chunks:
        session.add(
            PolicyChunk(
                policy_document_id=document.id,
                section_label=chunk.section_label,
                page_start=chunk.page_start,
                page_end=chunk.page_end,
                text=chunk.text,
                token_count=chunk.token_count,
            )
        )
    session.commit()
    logger.info("Ingested %s/%s v%s: %d pages -> %d chunks", city, slug, version, len(page_texts), len(chunks))
    return document
