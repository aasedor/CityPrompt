"""Policy Intelligence Engine — chunker anchors, retrieval ranking, guardrails.

All deterministic and offline: fixture text, mocked Anthropic client.
Assertions are structural (never on LLM content).
"""

from unittest.mock import AsyncMock, MagicMock

import pytest

import app.services.policy_intelligence.synthesis as synthesis_module
from app.services.policy_intelligence.chunker import MAX_CHUNK_CHARS, chunk_pages
from app.services.policy_intelligence.retrieval import (
    ChunkRecord,
    ScoredChunk,
    build_query_terms,
    rank_chunks,
)
from app.services.policy_intelligence.synthesis import (
    Citation,
    Consideration,
    PolicyInsight,
    apply_guardrails,
    synthesize_policy_insight,
)

# ---------------------------------------------------------------------------
# Chunker
# ---------------------------------------------------------------------------

def test_chunker_page_anchors_and_sizes():
    pages = [
        "2.1 RESIDENTIAL DENSITY\n\n" + ("Density shall support transit viability. " * 40),
        ("Continued discussion of density bonusing provisions in established areas. " * 40),
        "5.3 TREE CANOPY\n\n" + ("Canopy targets apply to all new development. " * 30),
    ]
    chunks = chunk_pages(pages)
    assert chunks, "no chunks produced"
    for chunk in chunks:
        assert 1 <= chunk.page_start <= chunk.page_end <= 3
        assert len(chunk.text) <= MAX_CHUNK_CHARS + 200
        assert chunk.token_count > 0
    # heading detection carried into section labels
    assert any((c.section_label or "").startswith("2.1") for c in chunks)
    assert any((c.section_label or "").startswith("5.3") for c in chunks)
    # page ordering is monotonic
    starts = [c.page_start for c in chunks]
    assert starts == sorted(starts)


def test_chunker_handles_empty_and_blank_pages():
    assert chunk_pages([]) == []
    assert chunk_pages(["", "   ", "\n\n"]) == []
    chunks = chunk_pages(["", "Only page two has text.", ""])
    assert len(chunks) == 1
    assert chunks[0].page_start == 2
    # Regression (review finding): page_end must be the last CONTENT page,
    # not a trailing blank page — citations point at real text.
    assert chunks[0].page_end == 2


def test_summaries_are_scrubbed_for_verdict_language():
    """Regression (review finding): the liability filter skipped summaries."""
    insight = PolicyInsight(summaries=["The proposal violates the height limit and is non-compliant."])
    result, warnings = apply_guardrails(insight, [_scored_chunk()])
    text = result.summaries[0].lower()
    assert "violates" not in text and "non-compliant" not in text
    assert any(w["code"] == "LIABILITY_LANGUAGE_FILTERED" for w in warnings)


# ---------------------------------------------------------------------------
# Retrieval
# ---------------------------------------------------------------------------

def _record(i: int, text: str, slug: str = "mdp", section: str | None = None) -> ChunkRecord:
    return ChunkRecord(
        chunk_id=str(i), document_slug=slug, document_title=slug.upper(),
        section_label=section, page_start=i, page_end=i, text=text,
    )


def test_build_query_terms_includes_districts_and_topics():
    terms = build_query_terms(
        {"districts": [{"code": "CC-X"}, {"code": "R-CG"}], "lap_name": "Beltline: Part 1",
         "community_name": "BELTLINE"},
        topics=["density", "tree canopy"],
    )
    assert "cc-x" in terms
    assert "r-cg" in terms
    assert "beltline" in terms
    assert "density" in terms
    assert "canopy" in terms
    assert len(terms) == len(set(terms))  # deduped


def test_rank_chunks_prefers_relevant_and_respects_budget():
    records = [
        _record(1, "Residential density near transit stations should increase. " * 5),
        _record(2, "Storm sewer maintenance schedules for winter operations. " * 5),
        _record(3, "Density bonusing and height incentives in the Beltline. " * 5,
                section="Density provisions"),
    ]
    ranked = rank_chunks(records, ["density", "height", "beltline", "transit"], top_k=2)
    assert [c.chunk_id for c in ranked] == ["3", "1"]  # section boost wins
    assert all(c.score > 0 for c in ranked)

    tiny = rank_chunks(records, ["density"], top_k=5, max_total_chars=100)
    assert tiny == []  # nothing fits a 100-char budget


def test_rank_chunks_empty_inputs():
    assert rank_chunks([], ["density"]) == []
    assert rank_chunks([_record(1, "text")], []) == []


# ---------------------------------------------------------------------------
# Guardrails
# ---------------------------------------------------------------------------

CHUNK_TEXT = (
    "The Municipal Development Plan directs that residential density in "
    "transit station areas should support transit viability and provide a "
    "gradient of building heights stepping down to established streets."
)


def _scored_chunk() -> ScoredChunk:
    return ScoredChunk(
        chunk_id="c1", document_slug="mdp-lup009", document_title="MDP",
        section_label="2.2 Transit Areas", page_start=41, page_end=41,
        text=CHUNK_TEXT, score=3.0,
    )


def test_guardrails_keep_verified_quote():
    insight = PolicyInsight(conformance_considerations=[
        Consideration(
            topic="density", detail="Density supports the MDP direction.",
            citations=[Citation(doc="mdp-lup009", page=41,
                                quote="residential density in transit station areas should support transit viability")],
        )
    ])
    result, warnings = apply_guardrails(insight, [_scored_chunk()])
    consideration = result.conformance_considerations[0]
    assert consideration.citations and consideration.citations[0].verified
    assert not any(w["code"] == "CITATION_UNVERIFIED" for w in warnings)


def test_guardrails_strip_fabricated_quote_and_demote():
    insight = PolicyInsight(conformance_considerations=[
        Consideration(
            topic="parking", detail="Parking minimums are abolished citywide.",
            confidence=0.8,
            citations=[Citation(doc="mdp-lup009", page=99,
                                quote="all parking minimums are hereby abolished across the entire city")],
        )
    ])
    result, warnings = apply_guardrails(insight, [_scored_chunk()])
    consideration = result.conformance_considerations[0]
    assert consideration.citations == []            # fabricated quote stripped
    assert consideration.framing == "context"        # demoted without citations
    assert consideration.confidence <= 0.3
    codes = {w["code"] for w in warnings}
    assert "CITATION_UNVERIFIED" in codes
    assert "UNCITED_POLICY_CLAIM" in codes


def test_guardrails_rewrite_verdict_language():
    insight = PolicyInsight(conformance_considerations=[
        Consideration(
            topic="height", detail="The proposal violates the height limit and is non-compliant.",
            citations=[Citation(doc="mdp-lup009", page=41,
                                quote="a gradient of building heights stepping down to established streets")],
        )
    ])
    result, warnings = apply_guardrails(insight, [_scored_chunk()])
    detail = result.conformance_considerations[0].detail.lower()
    assert "violates" not in detail
    assert "non-compliant" not in detail
    assert any(w["code"] == "LIABILITY_LANGUAGE_FILTERED" for w in warnings)


# ---------------------------------------------------------------------------
# Synthesis (mocked Anthropic)
# ---------------------------------------------------------------------------

class _FakeUsage:
    input_tokens = 900
    output_tokens = 400


def _fake_message(text: str):
    block = MagicMock()
    block.type = "text"
    block.text = text
    message = MagicMock()
    message.content = [block]
    message.usage = _FakeUsage()
    return message


def _mock_anthropic(monkeypatch, text: str | None = None, error: Exception | None = None):
    create_mock = AsyncMock(return_value=_fake_message(text or "{}"))
    if error is not None:
        create_mock.side_effect = error
    client = MagicMock()
    client.messages.create = create_mock
    monkeypatch.setattr(synthesis_module.anthropic, "AsyncAnthropic", MagicMock(return_value=client))
    monkeypatch.setattr(synthesis_module, "log_api_usage_sync", MagicMock())
    return create_mock


@pytest.mark.anyio
async def test_synthesis_happy_path(monkeypatch):
    payload = """```json
{"summaries": ["The MDP directs density to transit areas."],
 "conformance_considerations": [
   {"topic": "density", "framing": "trade_off", "risk": "low",
    "detail": "Site density direction aligns with station-area policy.",
    "citations": [{"doc": "mdp-lup009", "page": 41,
                   "quote": "residential density in transit station areas should support transit viability"}]}],
 "opportunities": []}
```"""
    _mock_anthropic(monkeypatch, text=payload)
    insight, warnings = await synthesize_policy_insight(
        site_facts={"dominant_district": "CC-X"}, chunks=[_scored_chunk()],
        corpus_status="partial", documents_consulted=["mdp-lup009"],
    )
    assert insight.corpus_status == "partial"
    assert insight.conformance_considerations[0].citations[0].verified
    assert insight.confidence == 1.0  # all items cited
    assert "internal deliberation" in insight.disclaimer.lower()


@pytest.mark.anyio
async def test_synthesis_no_corpus_degrades(monkeypatch):
    create_mock = _mock_anthropic(monkeypatch)
    insight, warnings = await synthesize_policy_insight(
        site_facts={}, chunks=[], corpus_status="absent", documents_consulted=[],
    )
    assert insight.corpus_status == "absent"
    assert insight.confidence == 0.0
    assert any(w["code"] == "POLICY_CORPUS_MISSING" for w in warnings)
    create_mock.assert_not_called()  # no chunks -> no spend


@pytest.mark.anyio
async def test_synthesis_llm_failure_degrades(monkeypatch):
    _mock_anthropic(monkeypatch, error=RuntimeError("api down"))
    insight, warnings = await synthesize_policy_insight(
        site_facts={}, chunks=[_scored_chunk()],
        corpus_status="partial", documents_consulted=["mdp-lup009"],
    )
    assert insight.confidence == 0.0
    assert any(w["code"] == "POLICY_SYNTHESIS_UNAVAILABLE" for w in warnings)


@pytest.mark.anyio
async def test_synthesis_unparseable_output_degrades(monkeypatch):
    _mock_anthropic(monkeypatch, text="I think this site is great, here are my thoughts...")
    insight, warnings = await synthesize_policy_insight(
        site_facts={}, chunks=[_scored_chunk()],
        corpus_status="partial", documents_consulted=["mdp-lup009"],
    )
    assert insight.confidence == 0.0
    assert any(w["code"] == "POLICY_SYNTHESIS_UNPARSEABLE" for w in warnings)


# ---------------------------------------------------------------------------
# Builder integration: the policy phase merges into the policy section
# ---------------------------------------------------------------------------

@pytest.mark.anyio
async def test_builder_policy_phase_merges_and_degrades():
    from shapely.geometry import Polygon

    from app.services.city_connector.base import CityConnector
    from app.services.urban_dna.builder import build_dna

    class EmptyConnector(CityConnector):
        city_id = "emptyville"

    site = Polygon([(-114.075, 51.043), (-114.062, 51.043), (-114.062, 51.049), (-114.075, 51.049)])

    async def fake_synthesizer(dna):
        return (
            {"insight": {"summaries": ["s"], "corpus_status": "partial"}},
            [{"code": "POLICY_INSTRUMENT_SUNSETTING", "severity": "warning",
              "message": "x", "source_phase": "policy_intelligence"}],
            0.75,
        )

    dna = await build_dna(
        site_polygon=site, connector=EmptyConnector(), project_id="p", zone_id="z",
        policy_synthesizer=fake_synthesizer,
    )
    assert dna.policy.fields["insight"].value["summaries"] == ["s"]
    assert dna.policy.fields["insight"].confidence == 0.75
    assert dna.policy.meta.confidence == 0.75
    assert any(w.code == "POLICY_INSTRUMENT_SUNSETTING" for w in dna.policy.meta.warnings)

    async def raising_synthesizer(dna):
        raise RuntimeError("db exploded")

    dna2 = await build_dna(
        site_polygon=site, connector=EmptyConnector(), project_id="p", zone_id="z",
        policy_synthesizer=raising_synthesizer,
    )
    assert dna2.policy.meta.confidence == 0.0
    assert any(w.code == "POLICY_SYNTHESIS_UNAVAILABLE" for w in dna2.policy.meta.warnings)
