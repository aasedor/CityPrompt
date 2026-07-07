"""Policy synthesis — one Claude call over retrieved chunks, with hard guardrails.

Liability posture (per docs/MUNICIPAL_POLICY_SPATIAL_AI_RESEARCH_2026_06_25.md):
outputs are framed as trade-offs/considerations for INTERNAL DELIBERATION, never
verdicts. Guardrails are mechanical, not prompt-hopeful:
  1. citations are schema-required on every consideration;
  2. every citation quote is difflib-verified against the stored chunk text —
     a fabricated quote is stripped and the item's confidence halved;
  3. verdict language ("violates", "non-compliant", ...) is rewritten post-hoc;
  4. synthesis failure degrades the policy section, never the DNA build.
"""

from __future__ import annotations

import difflib
import json
import logging
import re
from typing import Any, Literal, Optional

import anthropic
from celery.exceptions import SoftTimeLimitExceeded
from pydantic import BaseModel, Field, ValidationError

from app.core.config import get_settings
from app.core.usage_logger import log_api_usage_sync
from app.services.policy_intelligence.retrieval import ScoredChunk

logger = logging.getLogger(__name__)

QUOTE_MATCH_THRESHOLD = 0.85

_BANNED_LANGUAGE = {
    r"\bviolat\w+\b": "may not align with",
    r"\bnon-?compliant\b": "potentially inconsistent",
    r"\billegal\b": "outside current provisions",
    r"\bprohibited\b": "not contemplated by the current wording",
    r"\bbreach\w*\b": "tension with",
}


class Citation(BaseModel):
    doc: str                      # document slug
    title: str = ""
    section: Optional[str] = None
    page: int
    quote: str = Field(..., min_length=10, max_length=400)
    verified: bool = False
    url: Optional[str] = None     # official document URL (enriched server-side, never model-provided)


class Consideration(BaseModel):
    topic: str
    framing: Literal["trade_off", "opportunity", "context"] = "trade_off"
    risk: Literal["low", "medium", "high"] = "medium"
    detail: str
    citations: list[Citation] = Field(default_factory=list)
    confidence: float = 0.7


class PolicyInsight(BaseModel):
    summaries: list[str] = Field(default_factory=list)
    conformance_considerations: list[Consideration] = Field(default_factory=list)
    opportunities: list[Consideration] = Field(default_factory=list)
    corpus_status: Literal["complete", "partial", "absent"] = "partial"
    documents_consulted: list[str] = Field(default_factory=list)
    confidence: float = 0.0
    disclaimer: str = (
        "For internal deliberation only — not a legal conformance determination. "
        "Considerations are framed as trade-offs; consult the responsible authority."
    )


SYSTEM_PROMPT = """You are a municipal policy analyst assisting city planners with INTERNAL deliberation.

You receive excerpts from a city's policy documents plus facts about a specific site. Record policy intelligence for that site using the record_policy_insight tool.

Hard rules:
- Every consideration and opportunity MUST cite at least one excerpt, quoting it VERBATIM (copy the exact words; do not paraphrase inside "quote").
- Only cite the provided excerpts. If the excerpts don't support a claim, leave it out.
- Frame everything as trade-offs, considerations, or opportunities for discussion. NEVER use verdict language: no "violates", "non-compliant", "illegal", "prohibited", "breach".
- Plans are often discretionary; where wording is aspirational, say so.
- 3-6 considerations and 2-4 opportunities maximum. Be concrete and site-specific."""

_CITATION_SCHEMA = {
    "type": "object",
    "properties": {
        "doc": {"type": "string", "description": "document slug exactly as given in the excerpt header"},
        "section": {"type": "string"},
        "page": {"type": "integer"},
        "quote": {"type": "string", "description": "verbatim words copied from the excerpt, 10-60 words"},
    },
    "required": ["doc", "page", "quote"],
}

_CONSIDERATION_SCHEMA = {
    "type": "object",
    "properties": {
        "topic": {"type": "string"},
        "framing": {"type": "string", "enum": ["trade_off", "opportunity", "context"]},
        "risk": {"type": "string", "enum": ["low", "medium", "high"]},
        "detail": {"type": "string"},
        "citations": {"type": "array", "items": _CITATION_SCHEMA},
    },
    "required": ["topic", "detail", "citations"],
}

INSIGHT_TOOL = {
    "name": "record_policy_insight",
    "description": "Record structured policy intelligence for the site.",
    "input_schema": {
        "type": "object",
        "properties": {
            "summaries": {
                "type": "array", "items": {"type": "string"},
                "description": "1-3 short paragraphs summarizing what applicable policies say about this kind of site",
            },
            "conformance_considerations": {"type": "array", "items": _CONSIDERATION_SCHEMA},
            "opportunities": {"type": "array", "items": _CONSIDERATION_SCHEMA},
        },
        "required": ["summaries", "conformance_considerations", "opportunities"],
    },
}


def _strip_json_fences(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    return text.strip()


def _extract_json_object(text: str) -> str:
    """First balanced {...} in the text (string-aware) — tolerates preambles/epilogues."""
    start = text.find("{")
    if start == -1:
        return text
    depth = 0
    in_string = False
    escaped = False
    for index in range(start, len(text)):
        char = text[index]
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[start:index + 1]
    return text[start:]


def _coerce_stringified_payload(payload: Any) -> dict[str, Any]:
    """Repair the known claude-sonnet-5 tool quirk: nested fields (or whole
    field payloads) arrive as JSON-encoded STRINGS instead of objects/arrays."""

    def decode(value: Any) -> Any:
        if isinstance(value, str):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return value

    payload = decode(payload)
    if not isinstance(payload, dict):
        raise TypeError(f"payload is {type(payload).__name__}, not an object")

    # A stringified field can wrap the whole payload object.
    for key in ("summaries", "conformance_considerations", "opportunities"):
        decoded = decode(payload.get(key))
        if isinstance(decoded, dict) and "conformance_considerations" in decoded:
            payload = {**decoded, **{k: v for k, v in payload.items() if k != key and v}}
            decoded = payload.get(key)
        payload[key] = decoded

    summaries = payload.get("summaries") or []
    payload["summaries"] = [str(s) for s in summaries if isinstance(s, (str, int, float))] \
        if isinstance(summaries, list) else [str(summaries)]

    for key in ("conformance_considerations", "opportunities"):
        items = payload.get(key) or []
        if not isinstance(items, list):
            items = [items]
        payload[key] = [item for item in (decode(i) for i in items) if isinstance(item, dict)]

    return payload


def _compact_site_facts(site_facts: dict[str, Any]) -> dict[str, Any]:
    """Prune site facts to prompt-safe size — NEVER blind-truncate JSON mid-string."""
    compact: dict[str, Any] = {}
    for key, value in site_facts.items():
        if value is None:
            continue
        if key == "districts" and isinstance(value, list):
            compact[key] = [
                {"code": d.get("code"), "major": d.get("major"), "area_pct_of_site": d.get("area_pct_of_site")}
                if isinstance(d, dict) else d
                for d in value[:8]
            ]
        elif key == "frontage_streets" and isinstance(value, list):
            compact[key] = [
                {"name": s.get("name"), "ctp_class": s.get("ctp_class")} if isinstance(s, dict) else s
                for s in value[:8]
            ]
        elif key == "applicable_plans" and isinstance(value, list):
            compact[key] = [p.get("name") if isinstance(p, dict) else p for p in value[:8]]
        else:
            compact[key] = value
    return compact


def _rewrite_banned_language(text: str) -> tuple[str, bool]:
    rewritten = text
    hit = False
    for pattern, replacement in _BANNED_LANGUAGE.items():
        new = re.sub(pattern, replacement, rewritten, flags=re.IGNORECASE)
        if new != rewritten:
            hit = True
            rewritten = new
    return rewritten, hit


def _verify_quote(quote: str, chunks_by_doc: dict[str, list[ScoredChunk]], doc: str) -> bool:
    """A quote is genuine if it fuzzy-matches a window of some chunk of that doc."""
    needle = " ".join(quote.split()).lower()
    if not needle:
        return False
    for chunk in chunks_by_doc.get(doc, []):
        haystack = " ".join(chunk.text.split()).lower()
        if needle in haystack:
            return True
        # sliding fuzzy match over windows about the quote's length
        window = max(len(needle), 40)
        step = max(20, window // 2)
        for start in range(0, max(1, len(haystack) - window + 1), step):
            ratio = difflib.SequenceMatcher(
                None, needle, haystack[start:start + window]
            ).ratio()
            if ratio >= QUOTE_MATCH_THRESHOLD:
                return True
    return False


def apply_guardrails(
    insight: PolicyInsight, chunks: list[ScoredChunk]
) -> tuple[PolicyInsight, list[dict[str, Any]]]:
    """Mechanical post-pass: quote verification + banned-language rewrite."""
    warnings: list[dict[str, Any]] = []
    chunks_by_doc: dict[str, list[ScoredChunk]] = {}
    for chunk in chunks:
        chunks_by_doc.setdefault(chunk.document_slug, []).append(chunk)

    scrubbed_summaries: list[str] = []
    for summary in insight.summaries:
        rewritten, hit = _rewrite_banned_language(summary)
        if hit:
            warnings.append({
                "code": "LIABILITY_LANGUAGE_FILTERED",
                "severity": "info",
                "message": "Verdict language rewritten in a policy summary.",
                "source_phase": "policy_intelligence",
            })
        scrubbed_summaries.append(rewritten)
    insight.summaries = scrubbed_summaries

    def scrub(items: list[Consideration], kind: str) -> list[Consideration]:
        kept: list[Consideration] = []
        for item in items:
            detail, hit = _rewrite_banned_language(item.detail)
            if hit:
                item.detail = detail
                warnings.append({
                    "code": "LIABILITY_LANGUAGE_FILTERED",
                    "severity": "info",
                    "message": f"Verdict language rewritten in {kind} '{item.topic}'.",
                    "source_phase": "policy_intelligence",
                })
            verified_citations = []
            for citation in item.citations:
                if _verify_quote(citation.quote, chunks_by_doc, citation.doc):
                    citation.verified = True
                    # Enrich with the official document URL from the corpus —
                    # the model never provides URLs, so links can't hallucinate.
                    doc_chunks = chunks_by_doc.get(citation.doc) or []
                    if doc_chunks:
                        citation.url = citation.url or doc_chunks[0].source_url
                        citation.title = citation.title or doc_chunks[0].document_title
                    verified_citations.append(citation)
                else:
                    item.confidence = round(item.confidence * 0.5, 2)
                    warnings.append({
                        "code": "CITATION_UNVERIFIED",
                        "severity": "warning",
                        "message": f"Dropped a quote in {kind} '{item.topic}' that does not match "
                                   f"the {citation.doc} corpus text.",
                        "source_phase": "policy_intelligence",
                    })
            item.citations = verified_citations
            if not item.citations:
                warnings.append({
                    "code": "UNCITED_POLICY_CLAIM",
                    "severity": "warning",
                    "message": f"{kind} '{item.topic}' kept as context only — no verifiable citation.",
                    "source_phase": "policy_intelligence",
                })
                item.framing = "context"
                item.confidence = round(min(item.confidence, 0.3), 2)
            kept.append(item)
        return kept

    insight.conformance_considerations = scrub(insight.conformance_considerations, "consideration")
    insight.opportunities = scrub(insight.opportunities, "opportunity")
    return insight, warnings


async def synthesize_policy_insight(
    *,
    site_facts: dict[str, Any],
    chunks: list[ScoredChunk],
    corpus_status: str,
    documents_consulted: list[str],
    model: str | None = None,
) -> tuple[PolicyInsight, list[dict[str, Any]]]:
    """One Claude call -> guardrailed PolicyInsight. Never raises; degrades."""
    settings = get_settings()
    model = model or settings.urban_dna_agent_model

    if not chunks:
        return (
            PolicyInsight(corpus_status="absent", confidence=0.0),
            [{
                "code": "POLICY_CORPUS_MISSING",
                "severity": "warning",
                "message": "No policy corpus available for this city — planning proceeds philosophy-only.",
                "source_phase": "policy_intelligence",
            }],
        )

    excerpts = []
    for chunk in chunks:
        header = f"[doc: {chunk.document_slug} | {chunk.document_title} | pages {chunk.page_start}-{chunk.page_end}"
        if chunk.section_label:
            header += f" | section: {chunk.section_label}"
        header += "]"
        excerpts.append(f"{header}\n{chunk.text}")

    user_message = (
        "SITE FACTS (from the city's open data):\n"
        + json.dumps(_compact_site_facts(site_facts), indent=1, default=str)
        + "\n\nPOLICY EXCERPTS:\n\n"
        + "\n\n---\n\n".join(excerpts)
    )

    client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
    try:
        return await _synthesize_with_client(
            client, model, user_message, corpus_status, documents_consulted, chunks,
        )
    finally:
        # Close inside the running loop: the Celery task wraps this in
        # asyncio.run(), and a GC-time aclose() after the loop is gone emits
        # "Event loop is closed" noise (observed in trial logs 2026-07-07).
        try:
            await client.close()
        except Exception:  # noqa: BLE001 — cleanup must never mask the result
            pass


async def _synthesize_with_client(
    client: "anthropic.AsyncAnthropic",
    model: str,
    user_message: str,
    corpus_status: str,
    documents_consulted: list[str],
    chunks: list[ScoredChunk],
) -> tuple[PolicyInsight, list[dict[str, Any]]]:
    insight = None
    last_error = "?"
    # Up to 2 samples: the model nondeterministically JSON-encodes nested tool
    # fields as strings (same quirk as the expert runner); a fresh sample
    # usually conforms, and _coerce_stringified_payload repairs most cases.
    for attempt in range(2):
        try:
            # Forced tool use = schema-validated JSON. claude-sonnet-5 rejects
            # assistant prefill, and its adaptive thinking can otherwise leak
            # reasoning prose into the text channel (observed in smoke runs).
            message = await client.messages.create(
                model=model,
                max_tokens=8000,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": user_message}],
                tools=[INSIGHT_TOOL],
                tool_choice={"type": "tool", "name": "record_policy_insight"},
            )
        except SoftTimeLimitExceeded:
            raise  # must reach the Celery task handler, or the snapshot hangs until SIGKILL
        except Exception as exc:  # noqa: BLE001 — degrade, never fail the DNA build
            logger.warning("Policy synthesis call failed: %s", exc)
            return (
                PolicyInsight(corpus_status="partial", documents_consulted=documents_consulted, confidence=0.0),
                [{
                    "code": "POLICY_SYNTHESIS_UNAVAILABLE",
                    "severity": "warning",
                    "message": f"Policy synthesis unavailable: {exc}",
                    "source_phase": "policy_intelligence",
                }],
            )

        try:
            log_api_usage_sync(
                provider="anthropic",
                operation="urban_dna_policy_synthesis",
                input_tokens=message.usage.input_tokens,
                output_tokens=message.usage.output_tokens,
            )
        except SoftTimeLimitExceeded:
            raise  # sync DB frame — must reach the task handler, or the snapshot strands
        except Exception as exc:  # noqa: BLE001
            logger.warning("Failed to log policy synthesis usage: %s", exc)

        raw_text = "".join(
            block.text for block in message.content if getattr(block, "type", None) == "text"
        )

        try:
            payload = next(
                (block.input for block in message.content if getattr(block, "type", None) == "tool_use"),
                None,
            )
            if payload is None:  # fallback: parse the text channel
                payload = json.loads(_extract_json_object(_strip_json_fences(raw_text)))
            payload = _coerce_stringified_payload(payload)
            insight = PolicyInsight(
                summaries=payload.get("summaries", []),
                conformance_considerations=payload.get("conformance_considerations", []),
                opportunities=payload.get("opportunities", []),
                corpus_status=corpus_status,
                documents_consulted=documents_consulted,
            )
            break
        except (json.JSONDecodeError, ValidationError, AttributeError, TypeError) as exc:
            last_error = f"stop_reason={getattr(message, 'stop_reason', '?')}: {exc}"
            logger.warning("Policy synthesis attempt %d unparseable: %s", attempt, last_error)

    if insight is None:
        return (
            PolicyInsight(corpus_status="partial", documents_consulted=documents_consulted, confidence=0.0),
            [{
                "code": "POLICY_SYNTHESIS_UNPARSEABLE",
                "severity": "warning",
                "message": f"Policy synthesis output could not be parsed after retry ({last_error[:160]}); "
                           "policy section degraded.",
                "source_phase": "policy_intelligence",
            }],
        )

    insight, warnings = apply_guardrails(insight, chunks)
    cited = [
        c for group in (insight.conformance_considerations, insight.opportunities)
        for c in group if c.citations
    ]
    total = len(insight.conformance_considerations) + len(insight.opportunities)
    insight.confidence = round(len(cited) / total, 2) if total else 0.3
    return insight, warnings
