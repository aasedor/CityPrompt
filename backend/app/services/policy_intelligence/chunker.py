"""Page-anchored chunking for policy PDFs.

Every chunk carries {page_start, page_end, section_label?} so citations are
mechanical — the synthesis layer never has to infer where a quote came from.
Heading detection is best-effort over plain page text (the corpus includes
OCR'd documents with no font metadata; don't rely on structure).
"""

from __future__ import annotations

import re
from dataclasses import dataclass

# ~4 chars/token heuristic; chunks target 300-700 tokens
MIN_CHUNK_CHARS = 1200
MAX_CHUNK_CHARS = 2800

_HEADING_RE = re.compile(
    r"^(?:\d+(?:\.\d+)*\s+)?[A-Z][A-Za-z0-9 ,'&/\-()]{4,80}$"
)


@dataclass
class Chunk:
    text: str
    page_start: int  # 1-based
    page_end: int
    section_label: str | None
    token_count: int


def _detect_heading(paragraph: str) -> str | None:
    """A short, title-cased/numbered first line reads as a section heading."""
    first_line = paragraph.strip().splitlines()[0].strip()
    if len(first_line) > 80 or len(first_line) < 5:
        return None
    letters = [c for c in first_line if c.isalpha()]
    if not letters:
        return None
    upper_ratio = sum(1 for c in letters if c.isupper()) / len(letters)
    if _HEADING_RE.match(first_line) and (upper_ratio > 0.6 or first_line[0].isdigit()):
        return first_line
    return None


def chunk_pages(page_texts: list[str]) -> list[Chunk]:
    """Merge/split per-page text into 300-700 token chunks with page anchors."""
    chunks: list[Chunk] = []
    buffer = ""
    buffer_start_page: int | None = None
    current_section: str | None = None

    def flush(end_page: int) -> None:
        nonlocal buffer, buffer_start_page
        text = buffer.strip()
        if text and buffer_start_page is not None:
            chunks.append(
                Chunk(
                    text=text,
                    page_start=buffer_start_page,
                    page_end=end_page,
                    section_label=current_section,
                    token_count=max(1, len(text) // 4),
                )
            )
        buffer = ""
        buffer_start_page = None

    for page_num, raw in enumerate(page_texts, start=1):
        page_text = (raw or "").strip()
        if not page_text:
            continue

        paragraphs = [p for p in re.split(r"\n\s*\n", page_text) if p.strip()]
        for paragraph in paragraphs:
            heading = _detect_heading(paragraph)
            if heading and len(buffer) >= MIN_CHUNK_CHARS:
                flush(page_num)
            if heading:
                current_section = heading

            if buffer_start_page is None:
                buffer_start_page = page_num
            buffer += ("\n\n" if buffer else "") + paragraph.strip()

            while len(buffer) > MAX_CHUNK_CHARS:
                split_at = buffer.rfind("\n\n", MIN_CHUNK_CHARS, MAX_CHUNK_CHARS)
                if split_at == -1:
                    split_at = buffer.rfind(". ", MIN_CHUNK_CHARS, MAX_CHUNK_CHARS)
                    split_at = split_at + 1 if split_at != -1 else MAX_CHUNK_CHARS
                head, buffer_rest = buffer[:split_at].strip(), buffer[split_at:].strip()
                chunks.append(
                    Chunk(
                        text=head,
                        page_start=buffer_start_page,
                        page_end=page_num,
                        section_label=current_section,
                        token_count=max(1, len(head) // 4),
                    )
                )
                buffer = buffer_rest
                buffer_start_page = page_num

    flush(len(page_texts))
    return chunks
