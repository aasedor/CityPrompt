"""Tests for reviewed learned-evidence to architectural-graph compilation."""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path

import pytest


TOOL_DIR = Path(__file__).resolve().parents[1]


def fixtures():
    profiles = json.loads((TOOL_DIR / "architectural_evidence_profiles.json").read_text(encoding="utf-8"))
    profile = profiles["profiles"]["scottish_baronial_v76"]
    memory = json.loads((TOOL_DIR / "high_quality_building_memory.json").read_text(encoding="utf-8"))
    grammar = {
        "source": {"archetype_id": profile["archetype_id"], "variant_id": profile["variant_id"]},
        "dimensions": {"width_m": 55.0, "depth_m": 36.0},
        "massing_graph": {
            "profile": profile["base_graph"],
            "reference_dimensions": {"width_m": 55.0, "depth_m": 36.0},
            "nodes": [
                {"id": "baronial_left_wing", "location": [-21.0, 0.0, 10.25], "size": [8.0, 20.0, 20.5]},
                {"id": "baronial_right_wing", "location": [21.0, 0.0, 10.25], "size": [8.0, 20.0, 20.5]},
                {"id": "baronial_left_roof", "location": [-21.0, 0.0, 20.5], "size": [8.0, 20.0, 5.4]},
                {"id": "baronial_right_roof", "location": [21.0, 0.0, 20.5], "size": [8.0, 20.0, 5.4]},
            ],
            "voids": [{"id": "baronial_open_quadrangle", "location": [0.0, 1.0, 12.0], "size": [39.0, 20.0, 24.0]}],
            "assemblies": [
                {"id": "baronial_court_rear_skin", "axis": "front", "centre": [0.0, 9.0, 10.25], "span_m": 38.7},
                {"id": "baronial_court_left_skin", "axis": "left", "centre": [-19.5, 0.0, 10.25], "span_m": 19.7},
                {"id": "baronial_court_right_skin", "axis": "right", "centre": [19.5, 0.0, 10.25], "span_m": 19.7},
                {"id": "baronial_crow_gables", "axis": "front", "base_centre": [0.0, -17.0, 20.0]},
                {"id": "baronial_corner_turrets", "centres": [[-25.0, -16.0], [25.0, 16.0]]},
                {"id": "baronial_gate_bartizan", "centre": [0.0, -18.0, 4.0]},
                {"id": "baronial_gate_portal", "centre": [0.0, -18.0, 4.0], "recess_plane_y": -17.4},
            ],
        },
    }
    evidence = {
        "schema": "archetype-geometry-evidence@1",
        "id": "test-evidence",
        "scope": "one_archetype_bounded_pilot",
        "status": "review",
        "street_geometry": {"valid_coverage": 0.93, "cross_model_disagreement": {"median_ratio": 0.034}},
        "roof_geometry": {"confidence": {"median": 1.12}},
        "uncertainty": {"hidden_sides": "high"},
    }
    return grammar, evidence, profile, memory


def test_reviewed_profile_applies_traceable_graph_patch_and_dimensions():
    from architectural_evidence import compile_interpretation

    grammar, evidence, profile, memory = fixtures()
    interpretation, patched = compile_interpretation(grammar, evidence, profile, memory)
    assert interpretation["decision"] == "apply_reviewed_constraints"
    assert interpretation["policy"]["learned_mesh_delivery"] == "prohibited"
    assert patched["dimensions"]["depth_m"] == 48.0
    assert patched["massing_graph"]["profile"] == profile["output_graph"]
    assert next(void for void in patched["massing_graph"]["voids"] if void["id"] == "baronial_open_quadrangle")["size"] == [29.0, 24.0, 24.0]


def test_plan_scale_moves_gate_recess_plane_with_the_deepened_envelope():
    from architectural_evidence import compile_interpretation

    grammar, evidence, profile, memory = fixtures()
    _interpretation, patched = compile_interpretation(grammar, evidence, profile, memory)
    portal = next(item for item in patched["massing_graph"]["assemblies"] if item["id"] == "baronial_gate_portal")
    assert portal["recess_plane_y"] == pytest.approx(-23.2, abs=1e-5)


def test_untraceable_operation_is_rejected():
    from architectural_evidence import compile_interpretation

    grammar, evidence, profile, memory = fixtures()
    broken = deepcopy(profile)
    broken["operations"][0].pop("evidence")
    with pytest.raises(ValueError, match="lacks traceable evidence"):
        compile_interpretation(grammar, evidence, broken, memory)


def test_low_confidence_withholds_the_patch():
    from architectural_evidence import compile_interpretation

    grammar, evidence, profile, memory = fixtures()
    evidence["roof_geometry"]["confidence"]["median"] = 0.8
    interpretation, patched = compile_interpretation(grammar, evidence, profile, memory)
    assert interpretation["decision"] == "withhold_patch"
    assert patched["dimensions"]["depth_m"] == 36.0
