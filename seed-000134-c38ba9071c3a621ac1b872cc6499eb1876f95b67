"""Policy corpus ingestion: PDF/HTML -> MinIO -> page-anchored chunks -> Postgres.

Page extraction uses PyMuPDF directly (per-page text) rather than the Documents
pipeline's single-blob extraction — citations need page anchors. HTML documents
(e.g. Edmonton's Bylaw 20001 zone pages) are flattened to text with table rows
preserved as "cell | cell" lines and ingest as single-page documents.
Idempotent per (city, slug, version): re-ingesting replaces the document and
its chunks.
"""

from __future__ import annotations

import logging
from datetime import datetime
from html.parser import HTMLParser

import fitz  # PyMuPDF
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.services.policy_intelligence.chunker import chunk_pages

logger = logging.getLogger(__name__)


def extract_page_texts(pdf_bytes: bytes) -> list[str]:
    with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
        return [page.get_text("text") for page in doc]


class _TextExtractor(HTMLParser):
    """HTML -> plain text; table rows become 'cell | cell' lines.

    Regulation values on zoningbylaw.edmonton.ca live in tables (Subsection |
    Regulation | Value) — flattening a row to one line keeps the number next to
    the rule name, which is what BM25 retrieval and quote verification need.
    """

    _SKIP = {"script", "style", "head", "noscript", "nav", "footer", "template", "svg"}
    _BLOCK = {"p", "div", "li", "h1", "h2", "h3", "h4", "h5", "h6", "section",
              "article", "table", "ul", "ol", "br"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._lines: list[str] = []
        self._current: list[str] = []
        self._skip_depth = 0
        self._cells: list[str] | None = None  # open <tr> collects cell texts

    def _flush(self) -> None:
        text = "".join(self._current).strip()
        if text:
            self._lines.append(text)
        self._current = []

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag in self._SKIP:
            self._skip_depth += 1
            return
        if tag == "tr":
            self._flush()
            self._cells = []
        elif tag in ("td", "th") and self._cells is not None:
            self._flush()
        elif tag in self._BLOCK:
            self._flush()

    def handle_endtag(self, tag: str) -> None:
        if tag in self._SKIP:
            self._skip_depth = max(0, self._skip_depth - 1)
            return
        if tag in ("td", "th") and self._cells is not None:
            cell = "".join(self._current).strip()
            self._current = []
            self._cells.append(cell)
        elif tag == "tr" and self._cells is not None:
            row = " | ".join(cell for cell in self._cells if cell)
            if row:
                self._lines.append(row)
            self._cells = None
        elif tag in self._BLOCK:
            self._flush()

    def handle_data(self, data: str) -> None:
        if self._skip_depth == 0 and data:
            self._current.append(data)

    def text(self) -> str:
        self._flush()
        return "\n".join(self._lines)


def html_to_text(html: str) -> str:
    extractor = _TextExtractor()
    extractor.feed(html)
    return extractor.text()


def ingest_policy_html(
    session: Session,
    *,
    city: str,
    slug: str,
    title: str,
    source_url: str,
    html: str,
    instrument_type: str = "zoning_rule",
    version: str = "v1",
):
    """Store + chunk one HTML policy page (single-page document)."""
    from app.models.models import PolicyChunk, PolicyDocument
    from app.tasks.processing import _upload_to_storage

    settings = get_settings()

    text = html_to_text(html)
    chunks = chunk_pages([text])
    if not chunks:
        raise ValueError(f"{slug}: no extractable text in HTML")

    storage_key = f"{settings.policy_corpus_bucket_prefix}/{city}/{slug}/{version}.html"
    try:
        storage_url = _upload_to_storage(storage_key, html.encode("utf-8"), "text/html")
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
        version=version,
        status="active",
        page_count=1,
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
    logger.info("Ingested %s/%s v%s (html): %d chunks", city, slug, version, len(chunks))
    return document


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
