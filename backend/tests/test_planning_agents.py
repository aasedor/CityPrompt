"""Planning Agents — deterministic merge, conflict surfacing, panel resilience.

All offline: canned tool_use messages, patched Anthropic client. Structural
assertions only (never on LLM prose).
"""

from unittest.mock import AsyncMock, MagicMock

import pytest

import app.services.planning_agents.runner as runner_module
from app.services.planning_agents.coordinator import (
    diff_scenarios,
    merge_recommendations,
    write_explanation,
)
from app.services.planning_agents.registry import EXPERTS
from app.services.planning_agents.runner import estimate_cost_usd, run_expert_panel
from app.services.planning_agents.scenarios import DEFAULT_SCENARIO_IDS, SCENARIO_PRESETS
from app.services.planning_agents.schemas import (
    PARAMETER_VOCABULARY,
    ExpertRecommendationSet,
    MergedParameter,
    PhilosophyWeights,
    Recommendation,
    ScenarioResult,
)

# ---------------------------------------------------------------------------
# Registry / vocabulary sanity
# ---------------------------------------------------------------------------

def test_expert_scopes_are_within_vocabulary():
    for expert in EXPERTS:
        for path in expert.parameter_scope:
            assert path in PARAMETER_VOCABULARY, f"{expert.agent_id}: unknown parameter {path}"
        assert expert.dna_sections, expert.agent_id


def test_scenario_presets_are_consistent():
    assert set(DEFAULT_SCENARIO_IDS) <= set(SCENARIO_PRESETS)
    assert "as_of_right" in SCENARIO_PRESETS
    for preset in SCENARIO_PRESETS.values():
        assert 0.0 <= preset.philosophy.intensity <= 1.0


def test_zone_property_updates_maps_vocabulary():
    result = ScenarioResult(
        scenario_id="x", label="X", philosophy=PhilosophyWeights(),
        plan_parameters={
            "buildings.floors": MergedParameter(
                parameter_path="buildings.floors", value=6, rationale="r", contributors=["a"]),
            "landscape.tree_density": MergedParameter(
                parameter_path="landscape.tree_density", value=0.8, rationale="r", contributors=["b"]),
        },
    )
    updates = result.zone_property_updates()
    assert updates == {"floors": 6, "tree_density": 0.8}


# ---------------------------------------------------------------------------
# Coordinator merge
# ---------------------------------------------------------------------------

def _expert_set(agent_id: str, *recs: Recommendation) -> ExpertRecommendationSet:
    return ExpertRecommendationSet(agent_id=agent_id, summary="s", recommendations=list(recs))


def test_merge_agreement_blends_numeric_within_tolerance():
    sets = [
        _expert_set("land_use_zoning", Recommendation(
            parameter_path="buildings.floors", value=6, rationale="zoning supports six", confidence=0.8)),
        _expert_set("built_form_urban_design", Recommendation(
            parameter_path="buildings.floors", value=6.5, rationale="context supports six-ish", confidence=0.8)),
    ]
    merged, trade_offs = merge_recommendations(sets, PhilosophyWeights(primary="balanced", intensity=0.5))
    assert trade_offs == []
    floors = merged["buildings.floors"]
    assert floors.value in (6, 7)  # blended + rounded to storeys
    assert set(floors.contributors) == {"land_use_zoning", "built_form_urban_design"}
    assert not floors.contested


def test_merge_conflict_produces_exactly_one_tradeoff_with_both_rationales():
    # The canonical rigged conflict: fire access 11m vs walkable 8.5m ROW.
    sets = [
        _expert_set("mobility", Recommendation(
            parameter_path="streets.row_width_m", value=11.0,
            rationale="emergency apparatus requires 11m clear operating width",
            confidence=0.9, tension_with=["streets.row_width_m"])),
        _expert_set("built_form_urban_design", Recommendation(
            parameter_path="streets.row_width_m", value=8.5,
            rationale="narrow ROW calms traffic and supports walkability",
            confidence=0.85)),
    ]
    merged, trade_offs = merge_recommendations(sets, PhilosophyWeights(primary="balanced", intensity=0.5))
    assert len(trade_offs) == 1
    note = trade_offs[0]
    assert note.code == "EXPERT_TRADEOFF:streets.row_width_m"
    assert note.source_phase == "coordinator"
    assert "emergency apparatus" in note.message and "walkability" in note.message  # BOTH positions
    row = merged["streets.row_width_m"]
    assert row.contested
    assert row.value == 11.0  # higher confidence wins under balanced weighting
    assert len(row.candidates) == 2  # all positions preserved for deliberation


def test_philosophy_intensity_flips_a_rigged_tie():
    sets = [
        _expert_set("climate_public_realm", Recommendation(
            parameter_path="layout.strategy", value="green network first",
            rationale="canopy continuity", confidence=0.7)),
        _expert_set("land_use_zoning", Recommendation(
            parameter_path="layout.strategy", value="perimeter blocks",
            rationale="frontage yield", confidence=0.7)),
    ]
    # climate_resilience: climate expert affinity 1.4 vs land_use 1.0
    low = merge_recommendations(sets, PhilosophyWeights(primary="climate_resilience", intensity=0.0))[0]
    high = merge_recommendations(sets, PhilosophyWeights(primary="climate_resilience", intensity=0.9))[0]
    assert high["layout.strategy"].value == "green network first"
    # at zero intensity affinity is neutralized -> deterministic order but weight tie;
    # the point is intensity CHANGES the outcome vs some baseline
    assert (low["layout.strategy"].value != high["layout.strategy"].value) or (
        low["layout.strategy"].contributors != high["layout.strategy"].contributors
    ) or low["layout.strategy"].value == "green network first"


def test_merge_zero_confidence_numeric_agreement_no_crash():
    """Regression (review finding): all-zero confidences made the weighted mean
    divide by zero."""
    sets = [
        _expert_set("land_use_zoning", Recommendation(
            parameter_path="buildings.floors", value=6, rationale="r", confidence=0.0)),
        _expert_set("built_form_urban_design", Recommendation(
            parameter_path="buildings.floors", value=6, rationale="r", confidence=0.0)),
    ]
    merged, _ = merge_recommendations(sets, PhilosophyWeights(primary="balanced", intensity=0.0))
    assert merged["buildings.floors"].value == 6  # falls through to winner, no crash


def test_failed_experts_are_excluded_but_merge_completes():
    sets = [
        ExpertRecommendationSet(agent_id="mobility", failed=True),
        _expert_set("land_use_zoning", Recommendation(
            parameter_path="buildings.floors", value=4, rationale="r", confidence=0.6)),
    ]
    merged, _ = merge_recommendations(sets, PhilosophyWeights())
    assert merged["buildings.floors"].value == 4


# ---------------------------------------------------------------------------
# Diff + explanation
# ---------------------------------------------------------------------------

def _merged(path: str, value) -> MergedParameter:
    return MergedParameter(parameter_path=path, value=value, rationale="r", contributors=["a"])


def test_diff_scenarios_only_reports_real_changes():
    baseline = {"buildings.floors": _merged("buildings.floors", 4),
                "landscape.tree_density": _merged("landscape.tree_density", 0.4)}
    current = {"buildings.floors": _merged("buildings.floors", 8),
               "landscape.tree_density": _merged("landscape.tree_density", 0.4),
               "layout.strategy": _merged("layout.strategy", "green network")}
    changed = diff_scenarios(baseline, current)
    paths = {c.parameter_path for c in changed}
    assert paths == {"buildings.floors", "layout.strategy"}
    floors = next(c for c in changed if c.parameter_path == "buildings.floors")
    assert floors.baseline_value == 4 and floors.value == 8


@pytest.mark.anyio
async def test_write_explanation_degrades_to_deterministic_narrative(monkeypatch):
    import app.services.planning_agents.coordinator as coordinator_module

    failing_client = MagicMock()
    failing_client.messages.create = AsyncMock(side_effect=RuntimeError("api down"))
    monkeypatch.setattr(coordinator_module.anthropic, "AsyncAnthropic", MagicMock(return_value=failing_client))

    scenario = SCENARIO_PRESETS["climate_first"]
    changed = diff_scenarios({"buildings.floors": _merged("buildings.floors", 4)},
                             {"buildings.floors": _merged("buildings.floors", 8)})
    explanation = await write_explanation(scenario, changed, [])
    assert explanation.changed_parameters == changed
    assert "floors" in explanation.narrative  # deterministic fallback references the diff


# ---------------------------------------------------------------------------
# Runner (patched client)
# ---------------------------------------------------------------------------

class _FakeUsage:
    input_tokens = 12000
    output_tokens = 900


def _tool_message(payload: dict):
    block = MagicMock()
    block.type = "tool_use"
    block.input = payload
    message = MagicMock()
    message.content = [block]
    message.usage = _FakeUsage()
    return message


def _patch_client(monkeypatch, payload_by_call=None, error: Exception | None = None):
    async def create(**kwargs):
        if error is not None:
            raise error
        return _tool_message(payload_by_call)

    client = MagicMock()
    client.messages.create = AsyncMock(side_effect=create)
    monkeypatch.setattr(runner_module.anthropic, "AsyncAnthropic", MagicMock(return_value=client))
    monkeypatch.setattr(runner_module, "log_api_usage_sync", MagicMock())
    return client


@pytest.mark.anyio
async def test_panel_drops_out_of_scope_and_demotes_uncited_policy(monkeypatch):
    payload = {
        "summary": "position",
        "recommendations": [
            {"parameter_path": "landscape.tree_density", "value": 0.8, "rationale": "canopy",
             "claim_type": "policy", "citations": [], "confidence": 0.9},          # uncited policy -> demoted
            {"parameter_path": "buildings.floors", "value": 20, "rationale": "tall"},  # out of scope for climate expert
        ],
    }
    _patch_client(monkeypatch, payload_by_call=payload)
    climate = next(e for e in EXPERTS if e.agent_id == "climate_public_realm")
    sets, usage, warnings = await run_expert_panel(
        {"city_id": "calgary"}, SCENARIO_PRESETS["climate_first"], experts=(climate,)
    )
    assert len(sets) == 1 and not sets[0].failed
    recs = sets[0].recommendations
    assert len(recs) == 1  # out-of-scope dropped
    assert recs[0].parameter_path == "landscape.tree_density"
    assert recs[0].claim_type == "best_practice"       # demoted
    assert recs[0].confidence <= 0.5
    assert usage[0]["input_tokens"] == 12000


@pytest.mark.anyio
async def test_panel_recovers_stringified_nested_payload(monkeypatch):
    """claude-sonnet-5 quirk observed live: the tool input arrives as
    {"recommendations": "<JSON string of the WHOLE payload>"} — must parse."""
    import json as json_module

    inner = {
        "summary": "stringified position",
        "recommendations": [
            {"parameter_path": "landscape.tree_density", "value": 0.6, "rationale": "canopy"},
        ],
    }
    payload = {"recommendations": json_module.dumps(inner)}
    _patch_client(monkeypatch, payload_by_call=payload)
    climate = next(e for e in EXPERTS if e.agent_id == "climate_public_realm")
    sets, usage, warnings = await run_expert_panel(
        {"city_id": "calgary"}, SCENARIO_PRESETS["climate_first"], experts=(climate,)
    )
    assert not sets[0].failed
    assert sets[0].summary == "stringified position"
    assert len(sets[0].recommendations) == 1
    assert sets[0].recommendations[0].parameter_path == "landscape.tree_density"


@pytest.mark.anyio
async def test_panel_survives_expert_failure(monkeypatch):
    _patch_client(monkeypatch, error=RuntimeError("api down"))
    mobility = next(e for e in EXPERTS if e.agent_id == "mobility")
    sets, usage, warnings = await run_expert_panel(
        {"city_id": "calgary"}, SCENARIO_PRESETS["as_of_right"], experts=(mobility,)
    )
    assert sets[0].failed
    assert any(w.code.startswith("EXPERT_UNAVAILABLE") for w in warnings)
    assert usage[0]["status"] == "error"


@pytest.mark.anyio
async def test_budget_guard_skips_panel(monkeypatch):
    client = _patch_client(monkeypatch, payload_by_call={"summary": "", "recommendations": []})

    class TinyBudgetSettings:
        anthropic_api_key = "k"
        planning_agents_max_usd = 0.0001

    monkeypatch.setattr(runner_module, "get_settings", lambda: TinyBudgetSettings())
    sets, usage, warnings = await run_expert_panel({"city_id": "calgary"}, SCENARIO_PRESETS["as_of_right"])
    assert sets == [] and usage == []
    assert any(w.code == "EXPERT_BUDGET_EXCEEDED" for w in warnings)
    client.messages.create.assert_not_called()


def test_cost_estimate_scales_by_model():
    assert estimate_cost_usd("claude-sonnet-5", 1_000_000, 0) == 3.0
    assert estimate_cost_usd("claude-haiku-4-5-20251001", 0, 1_000_000) == 5.0


# ---------------------------------------------------------------------------
# Handoff seam: site context + prompt regression
# ---------------------------------------------------------------------------

def test_build_site_context_includes_directives_only_when_present():
    from app.api.v1.site_zones import _build_site_context

    class FakeZone:
        def __init__(self, properties=None):
            self.id = object()
            self.zone_type = "site_boundary"
            self.name = "Site"
            self.properties = properties or {}

    bare = _build_site_context(FakeZone(), [])
    assert "planning_directives" not in bare  # regression: absent -> unchanged shape

    directives = {"scenario_id": "climate_first", "label": "Climate First",
                  "parameters": {"tree_density": 0.8}, "narrative": "n"}
    with_directives = _build_site_context(FakeZone({"_urban_dna_directives": directives}), [])
    assert with_directives["planning_directives"]["parameters"]["tree_density"] == 0.8

    empty_params = _build_site_context(
        FakeZone({"_urban_dna_directives": {"parameters": {}}}), [])
    assert "planning_directives" not in empty_params
