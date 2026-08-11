from __future__ import annotations

import hashlib
from copy import deepcopy
from pathlib import Path

from belle_epoque_floor_sticker_v93 import audit_floor_plan, build_floor_plan, load_contract


SEGMENTED_SIX_HASH = "6" * 64
REPO = Path(__file__).resolve().parents[3]


def test_five_storey_plan_has_one_sticker_per_floor_per_elevation() -> None:
    plan = build_floor_plan(5)
    assert plan["audit"]["status"] == "pass"
    assert plan["sequence"] == ["ground", "middle_lower", "middle_repeat", "middle_upper", "top_crown"]
    assert plan["audit"]["floor_sticker_instance_count"] == 45
    assert plan["wall_top_z_m"] == 20.5
    assert plan["roof_instance"]["z_min_m"] == 20.5


def test_six_storey_inserts_exactly_one_repeatable_middle_and_shifts_fixed_upper_assemblies() -> None:
    five = build_floor_plan(5)
    six = build_floor_plan(6, segmented_geometry_sha256=SEGMENTED_SIX_HASH)
    assert six["audit"]["status"] == "pass"
    assert len(six["sequence"]) == len(five["sequence"]) + 1
    assert six["sequence"] == ["ground", "middle_lower", "middle_repeat", "middle_repeat", "middle_upper", "top_crown"]
    assert six["sequence"].count("middle_repeat") == five["sequence"].count("middle_repeat") + 1
    assert six["top_crown_translation_z_m"] == 4.1
    assert six["roof_translation_z_m"] == 4.1
    assert six["wall_top_z_m"] == 24.6


def test_six_storey_plan_is_blocked_without_separately_hashed_segmented_geometry() -> None:
    plan = build_floor_plan(6)
    assert plan["audit"]["status"] == "blocked"
    assert {failure["code"] for failure in plan["audit"]["failures"]} == {
        "six_storey_without_separately_hashed_segmented_geometry"
    }


def test_roof_source_and_material_can_never_own_a_vertical_floor_polygon() -> None:
    plan = build_floor_plan(5)
    assert plan["audit"]["roof_owned_vertical_wall_conflicts"] == []
    assert all(item["domain"] == "vertical_occupied_floor" for item in plan["floor_instances"])
    assert all(item["source_id"] != "roof" for item in plan["floor_instances"])
    assert all(item["roof_material_allowed"] is False for item in plan["floor_instances"])
    assert plan["roof_instance"]["domain"] == "roof_only"
    assert plan["roof_instance"]["vertical_wall_material_allowed"] is False


def test_each_floor_crop_is_explicit_and_within_its_source() -> None:
    plan = build_floor_plan(5)
    for item in plan["floor_instances"]:
        width, height = item["source_pixel_size"]
        x0, y0, x1, y1 = item["source_crop_xyxy"]
        assert (x0, x1) == (0, width)
        assert 0 <= y0 < y1 <= height
        assert item["uv_crop"] == [0.0, y0 / height, 1.0, y1 / height]


def test_floor_crops_are_bound_to_the_reviewed_exact_source_bytes() -> None:
    contract = load_contract()
    for source in contract["elevation_sources"].values():
        assert hashlib.sha256((REPO / source["path"]).read_bytes()).hexdigest() == source["sha256"]


def test_a_gap_overlap_or_roof_leak_is_a_hard_stop() -> None:
    contract = load_contract()
    plan = build_floor_plan(5, contract=contract)
    broken = deepcopy(plan)
    front_middle = next(
        item for item in broken["floor_instances"]
        if item["surface_id"] == "facade_front" and item["band_key"] == "middle_lower"
    )
    front_middle["z_min_m"] += 0.2
    broken["floor_instances"][2]["source_id"] = "roof"
    report = audit_floor_plan(broken, contract)
    codes = {failure["code"] for failure in report["failures"]}
    assert "gap_between_floor_bands" in codes
    assert "roof_source_on_vertical_wall_or_top_crown" in codes


def test_middle_repeat_uses_identical_source_crop_when_inserted() -> None:
    plan = build_floor_plan(6, segmented_geometry_sha256=SEGMENTED_SIX_HASH)
    for surface in load_contract()["surface_bindings"]:
        repeated = [item for item in plan["floor_instances"] if item["surface_id"] == surface and item["band_key"] == "middle_repeat"]
        assert len(repeated) == 2
        assert repeated[0]["source_crop_xyxy"] == repeated[1]["source_crop_xyxy"]
        assert repeated[0]["source_id"] == repeated[1]["source_id"]
