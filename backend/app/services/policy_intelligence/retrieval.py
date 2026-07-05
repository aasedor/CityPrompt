"""Lexical retrieval over policy chunks — pure Python, fully unit-testable.

BM25-flavoured term scoring over in-memory chunks. At corpus scale (single-city,
a handful of documents, low thousands of chunks) this is fast and needs no DB
features the mocked-DB test harness can't exercise. Swap point for pgvector.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from typing import Iterable

_WORD_RE = re.compile(r"[a-z0-9][a-z0-9\-]{1,}")

# High-signal planning terms get a scoring boost when matched.
_BOOST_TERMS = {
    "density", "height", "setback", "parking", "far", "floor", "storeys", "storey",
    "transit", "pedestrian", "cycling", "bikeway", "pathway", "canopy", "tree",
    "flood", "heritage", "affordable", "housing", "mixed-use", "frontage",
}


def tokenize(text: str) -> list[str]:
    return _WORD_RE.findall(text.lower())


@dataclass
class ScoredChunk:
    chunk_id: str
    document_slug: str
    document_title: str
    section_label: str | None
    page_start: int
    page_end: int
    text: str
    score: float


@dataclass
class ChunkRecord:
    """DB-agnostic view of a PolicyChunk joined with its document."""

    chunk_id: str
    document_slug: str
    document_title: str
    section_label: str | None
    page_start: int
    page_end: int
    text: str


def build_query_terms(site_facts: dict, topics: Iterable[str]) -> list[str]:
    """Query terms from DNA facts: district codes, plan names, community, topics."""
    terms: list[str] = []
    for topic in topics:
        terms.extend(tokenize(str(topic)))

    districts = site_facts.get("districts") or []
    for district in districts:
        code = (district.get("code") or "") if isinstance(district, dict) else str(district)
        if code:
            terms.append(code.lower())
            terms.extend(tokenize(code))
    for key in ("lap_name", "community_name", "dominant_district"):
        value = site_facts.get(key)
        if value:
            terms.extend(tokenize(str(value)))
    # de-dup, keep order
    seen: set[str] = set()
    out = []
    for term in terms:
        if term not in seen:
            seen.add(term)
            out.append(term)
    return out


def rank_chunks(
    records: list[ChunkRecord],
    query_terms: list[str],
    top_k: int = 12,
    max_total_chars: int = 24_000,
) -> list[ScoredChunk]:
    """TF-IDF-ish ranking with boosts; returns top_k within a char budget."""
    if not records or not query_terms:
        return []

    doc_freq: dict[str, int] = {}
    tokenized: list[set[str]] = []
    for record in records:
        tokens = set(tokenize(record.text))
        tokenized.append(tokens)
        for term in set(query_terms) & tokens:
            doc_freq[term] = doc_freq.get(term, 0) + 1

    n_docs = len(records)
    scored: list[ScoredChunk] = []
    for record, tokens in zip(records, tokenized):
        score = 0.0
        for term in query_terms:
            if term in tokens:
                idf = math.log(1 + n_docs / (1 + doc_freq.get(term, 0)))
                score += idf * (2.0 if term in _BOOST_TERMS else 1.0)
        if record.section_label:
            section_tokens = set(tokenize(record.section_label))
            if section_tokens & set(query_terms):
                score *= 1.3
        if score > 0:
            scored.append(
                ScoredChunk(
                    chunk_id=record.chunk_id,
                    document_slug=record.document_slug,
                    document_title=record.document_title,
                    section_label=record.section_label,
                    page_start=record.page_start,
                    page_end=record.page_end,
                    text=record.text,
                    score=round(score, 3),
                )
            )

    scored.sort(key=lambda c: c.score, reverse=True)
    selected: list[ScoredChunk] = []
    total_chars = 0
    for chunk in scored:
        if len(selected) >= top_k or total_chars + len(chunk.text) > max_total_chars:
            continue
        selected.append(chunk)
        total_chars += len(chunk.text)
    return selected
