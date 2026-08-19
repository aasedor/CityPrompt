"""Design Director — doctrine integrity, coherence rules, bounded authority.

All offline: no network, canned tool_use messages, patched Anthropic client.
Structural assertions only — never on LLM prose.

The point of this suite is that the DESIGN quality of a plan is now testable.
Every coherence rule is asserted twice: once that it fires on the defect it
exists for, and once that it stays silent on a plan that does not have it. A
rule that cannot stay quiet is a rule that trains users to ignore it.
"""

import re
from unittest.mock import AsyncMock, MagicMock

import pytest

import app.services.planning_agents.design_director as director_module
from app.services.plan_geometry.community_rules import FIRE_CLEAR_WIDTH_M
from app.services.plan_geometry.plan_evaluator import (
    BLOCK_EDGE_MAX_M,
    CANOPY_TARGET,
    INTERSECTION_TARGET_PER_KM2,
    PARK_ACCESS_RADIUS_M,
)
from app.services.plan_metrics import ASSUMPTIONS
from app.services.planning_agents.coherence import (
    apply_repairs,
    audit_and_repair,
    audit_coherence,
    resolve_values,
)
from app.services.planning_agents.design_director import (
    allowed_values,
    context_height_from_dna,
    run_design_review,
)
from app.services.planning_agents.design_doctrine import (
    DISCIPLINES,
    DOCTRINE_THRESHOLDS,
    PRINCIPLES,
    Principle,
    doctrine_prompt_block,
    get_principle,
    principles_for,
    threshold,
)
from app.services.planning_agents.registry import EXPERTS
from app.services.planning_agents.scenarios import SCENARIO_PRESETS
from app.services.planning_agents.schemas import (
    PARAMETER_VOCABULARY,
    MergedParameter,
    PhilosophyWeights,
    ScenarioDefinition,
)

# Principles whose test is genuinely a judgement, not a measurement. Listing
# them explicitly means a NEW principle cannot quietly ship an unmeasurable
# "TEST" line — it has to be added here on purpose.
_QUALITATIVE_PRINCIPLES = {
    "legibility.image",
    "legibility.serial_vision",
    "legibility.civic_hierarchy",
    "human.positive_space",
    "open_space.landscape_first",
    "climate.absorbent_ground",
    "mobility.parking_position",
    "context.phasing",
    "integrity.trade_off",
    "street.active_frontage",
    "climate.winter_city",
}

BALANCED = ScenarioDefinition(
    scenario_id="t",
    label="Test",
    philosophy=PhilosophyWeights(primary="balanced", intensity=0.5),
)


def _merged(values: dict, candidates: dict | None = None) -> dict[str, MergedParameter]:
    """Build a merged parameter set; ``candidates`` adds losing positions."""
    candidates = candidates or {}
    return {
        path: MergedParameter(
            parameter_path=path,
            value=value,
            rationale="because",
            contributors=["built_form_urban_design"],
            candidates=[{"agent_id": "built_form_urban_design", "value": value}]
            + [{"agent_id": "mobility", "value": alt} for alt in candidates.get(path, [])],
        )
        for path, value in values.items()
    }


# ---------------------------------------------------------------------------
# Doctrine integrity
# ---------------------------------------------------------------------------


def test_principle_ids_are_unique():
    ids = [p.principle_id for p in PRINCIPLES]
    assert len(ids) == len(set(ids))


def test_principles_reference_only_real_parameter_paths():
    """Doctrine may not invent a parameter the engine cannot read."""
    for principle in PRINCIPLES:
        for path in principle.parameter_paths:
            assert path in PARAMETER_VOCABULARY, f"{principle.principle_id} -> {path}"


def test_principles_reference_only_real_disciplines():
    for principle in PRINCIPLES:
        for discipline in principle.disciplines:
            assert discipline in DISCIPLINES, f"{principle.principle_id} -> {discipline}"


def test_every_expert_has_doctrine():
    """An expert with no principles would silently argue from nothing."""
    for spec in EXPERTS:
        assert principles_for(spec.agent_id), spec.agent_id
    assert principles_for("design_director")


# Any snake_case token in a measure line is a threshold reference: the prompt
# renderer resolves exactly these against DOCTRINE_THRESHOLDS.
_THRESHOLD_REF = re.compile(r"\b[a-z][a-z0-9]*(?:_[a-z0-9]+)+\b")


def _unknown_threshold_refs(principles) -> list[tuple[str, str]]:
    known = set(DOCTRINE_THRESHOLDS)
    return [
        (principle.principle_id, token)
        for principle in principles
        for token in _THRESHOLD_REF.findall(principle.measure)
        if token not in known
    ]


def test_measures_only_cite_defined_thresholds():
    """A TEST line naming a threshold that does not exist renders a principle
    with no number attached — the expert is told to measure something the
    prompt never defines."""
    assert _unknown_threshold_refs(PRINCIPLES) == []


def test_unknown_threshold_detector_is_not_vacuous():
    """Negative control: the check above must actually be able to fail."""
    bogus = Principle(
        principle_id="test.bogus",
        title="t",
        disciplines=("design_director",),
        statement="s",
        measure="Keep it under invented_threshold_m at all times.",
    )
    assert _unknown_threshold_refs([bogus]) == [("test.bogus", "invented_threshold_m")]


def test_every_measurable_principle_names_a_threshold():
    """A measure with no number in it is prose pretending to be a test."""
    for principle in PRINCIPLES:
        if not principle.measure:
            continue
        refs = _THRESHOLD_REF.findall(principle.measure)
        assert refs or principle.principle_id in _QUALITATIVE_PRINCIPLES, principle.principle_id


def test_thresholds_do_not_drift_from_the_evaluator():
    """Doctrine restates constants the drawn-plan evaluator measures. If the
    two disagree, the panel advises toward a target the evaluator will score
    as a failure."""
    assert threshold("fire_clear_width_m") == FIRE_CLEAR_WIDTH_M
    assert threshold("block_edge_max_m") == BLOCK_EDGE_MAX_M
    assert threshold("park_access_radius_m") == PARK_ACCESS_RADIUS_M
    assert threshold("canopy_target") == CANOPY_TARGET
    assert threshold("intersection_density_target_per_km2") == INTERSECTION_TARGET_PER_KM2


def test_thresholds_do_not_drift_from_the_metrics_engine():
    assert threshold("avg_unit_area_m2") == ASSUMPTIONS["avg_unit_area_m2"]["value"]
    assert threshold("residential_efficiency") == ASSUMPTIONS["residential_efficiency"]["value"]


def test_aligns_with_annotations_are_all_asserted():
    """Every threshold claiming an alignment must be covered by a drift test
    above — otherwise the annotation is decoration."""
    annotated = {key for key, spec in DOCTRINE_THRESHOLDS.items() if spec.get("aligns_with")}
    asserted = {
        "fire_clear_width_m",
        "block_edge_max_m",
        "park_access_radius_m",
        "canopy_target",
        "intersection_density_target_per_km2",
    }
    assert annotated == asserted


def test_doctrine_prompt_block_is_byte_stable():
    """The runner's prompt cache depends on identical bytes for identical
    inputs; a set-ordered render would silently cost cache hits."""
    first = doctrine_prompt_block("mobility", "transit_oriented", "new_urbanism")
    second = doctrine_prompt_block("mobility", "transit_oriented", "new_urbanism")
    assert first == second and first


def test_philosophy_relevant_principles_rank_first():
    ordered = principles_for("climate_public_realm", "climate_resilience")
    assert "climate_resilience" in ordered[0].philosophy_affinity


def test_get_principle_round_trips():
    assert get_principle("street.enclosure").title
    assert get_principle("no.such.principle") is None


def test_threshold_raises_on_typo():
    with pytest.raises(KeyError):
        threshold("enclosure_ratio_maximum")


# ---------------------------------------------------------------------------
# Coherence — each rule fires, and stays silent
# ---------------------------------------------------------------------------


def _rules(findings):
    return {f.rule_id for f in findings}


def test_coherent_plan_produces_no_findings():
    """The false-positive guard. A well-formed plan must be silent."""
    plan = {
        "buildings.floors": 4,
        "buildings.height_m": 14.1,
        "buildings.development_type": "mixed_use",
        "streets.row_width_m": 20.0,
        "landscape.tree_density": 0.6,
        "landscape.ground_texture": "permeable pavers and rain gardens",
        "buildings.unit_count": 400,
    }
    assert audit_coherence(plan, site_area_m2=20_000) == []


def test_empty_parameters_produce_no_findings():
    """A degraded panel yields few parameters; that is not a design defect."""
    assert audit_coherence({}) == []
    assert audit_coherence({"buildings.floors": 4}) == []


def test_fire_access_fires_below_the_clear_width():
    findings = audit_coherence({"streets.row_width_m": 4.0})
    finding = next(f for f in findings if f.rule_id == "fire_access")
    assert finding.severity == "error"
    assert finding.repair_value == FIRE_CLEAR_WIDTH_M
    assert finding.repair_mode == "at_least"
    assert "fire_access" not in _rules(audit_coherence({"streets.row_width_m": FIRE_CLEAR_WIDTH_M}))


def test_street_enclosure_catches_the_canyon_the_merge_creates():
    """The core defect: independent per-path merging pairs tall massing with a
    narrow right-of-way that no expert ever proposed together."""
    findings = audit_coherence({"buildings.height_m": 24.0, "streets.row_width_m": 8.0})
    finding = next(f for f in findings if f.rule_id == "street_enclosure")
    assert finding.repair_path == "streets.row_width_m"
    assert finding.repair_value == pytest.approx(24.0)  # widened to a 1:1 room


def test_street_enclosure_caps_height_when_widening_would_make_an_arterial():
    findings = audit_coherence({"buildings.height_m": 90.0, "streets.row_width_m": 20.0})
    finding = next(f for f in findings if f.rule_id == "street_enclosure")
    assert finding.repair_path == "buildings.height_m"
    assert finding.repair_mode == "at_most"
    assert finding.repair_value == pytest.approx(20.0 * threshold("enclosure_ratio_max"))


def test_street_enclosure_silent_in_the_comfort_band():
    assert "street_enclosure" not in _rules(audit_coherence({"buildings.height_m": 16.0, "streets.row_width_m": 20.0}))


def test_street_enclosure_derives_height_from_floors_when_absent():
    findings = audit_coherence({"buildings.floors": 8, "streets.row_width_m": 6.0})
    assert "street_enclosure" in _rules(findings)


def test_height_floors_consistency_fires_on_divergence():
    findings = audit_coherence({"buildings.floors": 4, "buildings.height_m": 30.0})
    finding = next(f for f in findings if f.rule_id == "height_floors_consistency")
    assert finding.repair_value == pytest.approx(12.8)  # 4 x 3.2


def test_height_floors_consistency_allows_the_mixed_use_ground_floor_premium():
    """A mixed-use block IS taller at the same storey count. Flagging that
    would push the panel toward unlettable ground floors."""
    assert "height_floors_consistency" not in _rules(
        audit_coherence({"buildings.floors": 4, "buildings.height_m": 14.1, "buildings.development_type": "mixed_use"})
    )


def test_canopy_deliverability_fires_when_the_row_cannot_hold_trees():
    findings = audit_coherence({"landscape.tree_density": 0.9, "streets.row_width_m": 11.0})
    finding = next(f for f in findings if f.rule_id == "canopy_deliverability")
    assert finding.repair_value == threshold("street_tree_min_row_m")
    assert "canopy_deliverability" not in _rules(
        audit_coherence({"landscape.tree_density": 0.9, "streets.row_width_m": 18.0})
    )


def test_yield_plausibility_fires_only_with_a_site_area():
    plan = {"buildings.unit_count": 9000, "buildings.floors": 4}
    assert "yield_plausibility" not in _rules(audit_coherence(plan))
    findings = audit_coherence(plan, site_area_m2=20_000)
    finding = next(f for f in findings if f.rule_id == "yield_plausibility")
    assert finding.severity == "error"
    assert finding.repair_value < 9000


def test_yield_plausibility_silent_inside_the_band():
    assert "yield_plausibility" not in _rules(
        audit_coherence({"buildings.unit_count": 450, "buildings.floors": 4}, site_area_m2=20_000)
    )


def test_context_transition_fires_and_then_answers_itself():
    plan = {"buildings.height_m": 30.0}
    finding = next(f for f in audit_coherence(plan, context_height_m=8.0) if f.rule_id == "context_transition")
    assert finding.repair_path == "site.design_brief"
    # Once the brief carries the step-down the condition is answered, so the
    # finding must not persist forever against an unchanged height.
    plan["site.design_brief"] = finding.repair_value
    assert "context_transition" not in _rules(audit_coherence(plan, context_height_m=8.0))


def test_philosophy_band_catches_a_scenario_contradicting_itself():
    findings = audit_coherence({"buildings.floors": 9}, philosophy=PhilosophyWeights(primary="missing_middle"))
    finding = next(f for f in findings if f.rule_id == "philosophy_band")
    assert finding.repair_value == threshold("missing_middle_max_floors")
    assert "philosophy_band" not in _rules(
        audit_coherence({"buildings.floors": 3}, philosophy=PhilosophyWeights(primary="missing_middle"))
    )


def test_mixed_use_ground_floor_fires_when_the_massing_leaves_no_room():
    findings = audit_coherence(
        {"buildings.development_type": "mixed_use", "buildings.floors": 4, "buildings.height_m": 12.8}
    )
    finding = next(f for f in findings if f.rule_id == "mixed_use_ground_floor")
    assert finding.repair_mode == "at_least"
    assert "mixed_use_ground_floor" not in _rules(
        audit_coherence(
            {"buildings.development_type": "residential", "buildings.floors": 4, "buildings.height_m": 12.8}
        )
    )


def test_paved_canopy_conflict_respects_a_permeable_ground_plane():
    hard = {"landscape.tree_density": 0.8, "landscape.ground_texture": "granite sett paving"}
    assert "paved_canopy_conflict" in _rules(audit_coherence(hard))
    soft = {"landscape.tree_density": 0.8, "landscape.ground_texture": "permeable pavers and rain gardens"}
    assert "paved_canopy_conflict" not in _rules(audit_coherence(soft))


def test_findings_are_ordered_most_severe_first():
    findings = audit_coherence(
        {"streets.row_width_m": 3.0, "buildings.floors": 7, "landscape.tree_density": 0.9},
    )
    severities = [f.severity for f in findings]
    rank = {"error": 2, "warning": 1, "info": 0}
    assert severities == sorted(severities, key=lambda s: -rank[s])


# ---------------------------------------------------------------------------
# Repair semantics
# ---------------------------------------------------------------------------


def test_at_least_repairs_take_the_binding_minimum():
    """Fire access and enclosure both raise the same right-of-way. Rule order
    must not decide which one wins — the binding constraint must."""
    plan = {"buildings.height_m": 24.0, "streets.row_width_m": 4.0, "landscape.tree_density": 0.9}
    repaired, applied = apply_repairs(plan, audit_coherence(plan))
    assert repaired["streets.row_width_m"] == pytest.approx(24.0)


def test_info_findings_are_not_auto_applied():
    plan = {"landscape.tree_density": 0.8, "landscape.ground_texture": "granite sett paving"}
    repaired, applied = apply_repairs(plan, audit_coherence(plan))
    assert repaired["landscape.ground_texture"] == "granite sett paving"
    assert applied == []


def test_repair_converges_and_leaves_no_repairable_defect():
    """A single pass is not enough: capping storeys invalidates a height that
    was consistent before the cap."""
    plan = {
        "buildings.floors": 9,
        "buildings.height_m": 28.8,
        "buildings.development_type": "mixed_use",
        "streets.row_width_m": 4.0,
        "landscape.tree_density": 0.9,
        "buildings.unit_count": 9000,
    }
    outcome = audit_and_repair(plan, philosophy=PhilosophyWeights(primary="missing_middle"), site_area_m2=20_000)
    assert outcome.converged
    assert outcome.passes > 1  # the second pass is what makes this correct
    repairable = [f for f in outcome.residual_findings if f.severity in ("warning", "error") and f.has_repair()]
    assert repairable == []
    assert outcome.values["streets.row_width_m"] >= FIRE_CLEAR_WIDTH_M


def test_resolve_values_accepts_merged_parameters_and_raw_values():
    merged = _merged({"buildings.floors": 5})
    assert resolve_values(merged)["buildings.floors"] == 5
    assert resolve_values({"buildings.floors": 5})["buildings.floors"] == 5
    assert resolve_values({"buildings.floors": {"value": 5}})["buildings.floors"] == 5


# ---------------------------------------------------------------------------
# Design Director — bounded authority
# ---------------------------------------------------------------------------


class _FakeUsage:
    input_tokens = 8000
    output_tokens = 700


def _patch_director(monkeypatch, payload=None, error: Exception | None = None):
    async def create(**kwargs):
        if error is not None:
            raise error
        block = MagicMock()
        block.type = "tool_use"
        block.input = payload
        message = MagicMock()
        message.content = [block]
        message.usage = _FakeUsage()
        return message

    client = MagicMock()
    client.messages.create = AsyncMock(side_effect=create)
    client.close = AsyncMock()
    monkeypatch.setattr(director_module.anthropic, "AsyncAnthropic", MagicMock(return_value=client))
    monkeypatch.setattr(director_module, "log_api_usage_sync", MagicMock())
    return client


def test_allowed_values_includes_losing_positions_and_repairs():
    merged = _merged({"buildings.floors": 6}, candidates={"buildings.floors": [4]})
    findings = audit_coherence({"buildings.floors": 6, "streets.row_width_m": 3.0})
    permitted = allowed_values("buildings.floors", merged, findings)
    assert 6 in permitted and 4 in permitted


@pytest.mark.anyio
async def test_director_cannot_invent_a_number(monkeypatch):
    """The bounded-authority contract: a value no expert proposed and the audit
    did not compute is discarded, and the discard is disclosed."""
    _patch_director(
        monkeypatch,
        payload={
            "charter": "A single planted spine.",
            "critique": [],
            "resolutions": [
                {
                    "rule_id": "design_judgement",
                    "parameter_path": "buildings.floors",
                    "value": 42,
                    "reason": "taller is better",
                }
            ],
        },
    )
    merged = _merged({"buildings.floors": 4})
    reviewed, review = await run_design_review(merged, BALANCED)
    assert reviewed["buildings.floors"].value == 4
    assert any(note.code.startswith("DIRECTOR_OUT_OF_BOUNDS") for note in review.notes)


@pytest.mark.anyio
async def test_director_may_reopen_a_merge_toward_a_position_an_expert_took(monkeypatch):
    """Reopening a merge the philosophy weighting decided is a legitimate
    design act — as long as the value came from the panel."""
    _patch_director(
        monkeypatch,
        payload={
            "charter": "Fabric steps down to the west.",
            "critique": [],
            "resolutions": [
                {
                    "rule_id": "design_judgement",
                    "parameter_path": "buildings.floors",
                    "value": 4,
                    "reason": "the transition to the west edge governs",
                }
            ],
        },
    )
    merged = _merged({"buildings.floors": 6}, candidates={"buildings.floors": [4]})
    reviewed, review = await run_design_review(merged, BALANCED)
    assert reviewed["buildings.floors"].value == 4
    assert "design_director" in reviewed["buildings.floors"].contributors
    # Provenance survives: the WHY panel still shows every original position.
    assert reviewed["buildings.floors"].candidates
    assert not any(note.code.startswith("DIRECTOR_OUT_OF_BOUNDS") for note in review.notes)


@pytest.mark.anyio
async def test_director_authors_narrative_paths_freely(monkeypatch):
    _patch_director(
        monkeypatch,
        payload={
            "charter": "One spine.",
            "critique": [],
            "resolutions": [
                {
                    "rule_id": "design_judgement",
                    "parameter_path": "site.design_brief",
                    "value": "A planted spine from the station to the creek.",
                    "reason": "organizing idea",
                }
            ],
        },
    )
    merged = _merged({"buildings.floors": 4})
    reviewed, review = await run_design_review(merged, BALANCED)
    assert reviewed["site.design_brief"].value.startswith("A planted spine")
    assert not any(note.code.startswith("DIRECTOR_OUT_OF_BOUNDS") for note in review.notes)


@pytest.mark.anyio
async def test_director_critique_must_cite_a_real_principle(monkeypatch):
    _patch_director(
        monkeypatch,
        payload={
            "charter": "c",
            "critique": [
                {"principle_id": "street.enclosure", "observation": "the street reads well"},
                {"principle_id": "invented.principle", "observation": "trust me"},
            ],
        },
    )
    reviewed, review = await run_design_review(_merged({"buildings.floors": 4}), BALANCED)
    assert [note.principle_id for note in review.critique] == ["street.enclosure"]
    assert review.critique[0].title  # resolved from the doctrine, not the model


@pytest.mark.anyio
async def test_director_failure_still_leaves_a_coherent_plan(monkeypatch):
    """Degradation contract: the review never fails a scenario run, and the
    deterministic repairs still land."""
    _patch_director(monkeypatch, error=RuntimeError("model unavailable"))
    merged = _merged({"buildings.height_m": 24.0, "streets.row_width_m": 3.0})
    reviewed, review = await run_design_review(merged, BALANCED)

    assert review.failed
    assert any(note.code == "DESIGN_DIRECTOR_UNAVAILABLE" for note in review.notes)
    assert review.charter  # deterministic fallback, not empty
    assert reviewed["streets.row_width_m"].value >= FIRE_CLEAR_WIDTH_M
    assert "coherence_audit" in reviewed["streets.row_width_m"].contributors
    assert review.usage["status"] == "error"


@pytest.mark.anyio
async def test_director_records_deterministic_resolutions(monkeypatch):
    _patch_director(monkeypatch, payload={"charter": "c", "critique": []})
    merged = _merged({"streets.row_width_m": 3.0})
    reviewed, review = await run_design_review(merged, BALANCED)
    fire = next(r for r in review.resolutions if r.rule_id == "fire_access")
    assert fire.decided_by == "deterministic"
    assert fire.from_value == 3.0
    assert fire.to_value == FIRE_CLEAR_WIDTH_M


@pytest.mark.anyio
async def test_clean_plan_needs_no_repair(monkeypatch):
    _patch_director(monkeypatch, payload={"charter": "c", "critique": []})
    merged = _merged({"buildings.floors": 4, "buildings.height_m": 12.8, "streets.row_width_m": 18.0})
    reviewed, review = await run_design_review(merged, BALANCED)
    assert review.findings == []
    assert review.resolutions == []
    assert {p: m.value for p, m in reviewed.items()} == {
        "buildings.floors": 4,
        "buildings.height_m": 12.8,
        "streets.row_width_m": 18.0,
    }


# ---------------------------------------------------------------------------
# DNA plumbing
# ---------------------------------------------------------------------------


def test_context_height_from_dna_reads_the_connector_field():
    dna = {"built_form": {"fields": {"context_avg_height_m": {"value": 7.4}}}}
    assert context_height_from_dna(dna) == 7.4


@pytest.mark.parametrize(
    "dna",
    [
        None,
        {},
        {"built_form": {}},
        {"built_form": {"fields": {}}},
        {"built_form": {"fields": {"context_avg_height_m": {"value": 0}}}},
    ],
)
def test_context_height_absent_disables_the_transition_rule(dna):
    """No context is not zero context — the rule must switch off, not fire."""
    assert context_height_from_dna(dna) is None


def test_every_scenario_preset_survives_the_audit_contract():
    """Each shipped preset must be able to run the audit without error."""
    for preset in SCENARIO_PRESETS.values():
        assert audit_coherence({"buildings.floors": 5}, philosophy=preset.philosophy) is not None


# ---------------------------------------------------------------------------
# Post-override reconciliation
# ---------------------------------------------------------------------------


@pytest.mark.anyio
async def test_arithmetic_is_reconciled_after_a_director_override(monkeypatch):
    """The director raising the storey count must not leave the height
    describing a different building — the geometry engine can only draw one."""
    _patch_director(
        monkeypatch,
        payload={
            "charter": "c",
            "critique": [],
            "resolutions": [
                {
                    "rule_id": "design_judgement",
                    "parameter_path": "buildings.floors",
                    "value": 6,
                    "reason": "the spine can carry six",
                }
            ],
        },
    )
    merged = _merged(
        {"buildings.floors": 4, "buildings.height_m": 12.8},
        candidates={"buildings.floors": [6]},
    )
    reviewed, review = await run_design_review(merged, BALANCED)

    assert reviewed["buildings.floors"].value == 6
    assert reviewed["buildings.height_m"].value == pytest.approx(6 * threshold("typical_storey_m"))
    assert "height_floors_consistency" not in _rules(review.residual_findings)


@pytest.mark.anyio
async def test_design_positions_are_reported_not_overwritten(monkeypatch):
    """A judgement rule the director overrode stays overridden — and stays
    visible as a residual finding rather than being silently re-applied."""
    _patch_director(
        monkeypatch,
        payload={
            "charter": "c",
            "critique": [],
            "resolutions": [
                {
                    "rule_id": "philosophy_band",
                    "parameter_path": "buildings.floors",
                    "value": 8,
                    "reason": "the corridor governs, not the label",
                }
            ],
        },
    )
    scenario = ScenarioDefinition(
        scenario_id="mm",
        label="MM",
        philosophy=PhilosophyWeights(primary="missing_middle", intensity=0.6),
    )
    merged = _merged({"buildings.floors": 5}, candidates={"buildings.floors": [8]})
    reviewed, review = await run_design_review(merged, scenario)

    assert reviewed["buildings.floors"].value == 8  # not clawed back to the 4-storey cap
    assert "philosophy_band" in _rules(review.residual_findings)  # but still disclosed


@pytest.mark.anyio
async def test_resolutions_report_the_net_move_once_per_parameter(monkeypatch):
    """Convergence can touch a path several times; the audit trail must show
    the net change, not one row per internal pass."""
    _patch_director(monkeypatch, payload={"charter": "c", "critique": []})
    merged = _merged(
        {
            "buildings.floors": 9,
            "buildings.height_m": 28.8,
            "streets.row_width_m": 3.0,
            "buildings.unit_count": 9000,
        }
    )
    reviewed, review = await run_design_review(
        merged,
        ScenarioDefinition(scenario_id="mm", label="MM", philosophy=PhilosophyWeights(primary="missing_middle")),
        site_area_m2=20_000,
    )
    deterministic = [r for r in review.resolutions if r.decided_by == "deterministic"]
    paths = [r.parameter_path for r in deterministic]
    assert len(paths) == len(set(paths)), paths
    row = next(r for r in deterministic if r.parameter_path == "streets.row_width_m")
    assert row.from_value == 3.0  # the original, not an intermediate pass value
