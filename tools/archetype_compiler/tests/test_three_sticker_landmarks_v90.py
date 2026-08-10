from collections import Counter
import json
from pathlib import Path

from compile_three_sticker_landmarks_v90 import (
    TARGETS,
    amsterdam_draft,
    customize,
    paris_draft,
    registry,
    toronto_draft,
)
from compile_catalogue_round_v87 import build_profile


def _profile(target, draft):
    parent, variant, index, _family, width, depth, floors = target
    profile, _recipes = build_profile(parent, variant, index, width, depth, floors, draft)
    profile.pop("extends", None)
    customize(variant, profile)
    return profile


def test_batch_is_finite_and_uses_exact_variants():
    payload = registry()
    assert len(payload["entries"]) == 3
    assert payload["paid_facade_calls"] == 0
    assert {item["variant_id"] for item in payload["entries"]} == {
        "neck_gable_merchant",
        "parisian-corner-with-dome-zinc-mansard",
        "toronto_bay_gable_yellow_brick",
    }


def test_every_pilot_is_fixed_select_and_place_with_continuous_stickers():
    for target, draft in zip(TARGETS, (amsterdam_draft(), paris_draft(), toronto_draft())):
        profile = _profile(target, draft)
        production = profile["production_contract"]
        placement = production["placement_contract"]
        assert placement["mode"] == "fixed_landmark"
        assert placement["ui_interaction"] == "select_and_place"
        assert placement["polygon_fit"] is False
        assert placement["non_uniform_scale"] == "forbidden"
        assert production["sticker_method"]["duplicate_feature_ownership_forbidden"] is True
        skins = [item for item in profile["massing_graph"]["assemblies"] if item["kind"] == "facade_skin"]
        assert skins
        assert all("storey" not in item["id"] for item in skins)
        assert not any(item["kind"] == "punched_opening_schedule" for item in profile["massing_graph"]["assemblies"])


def test_paris_uses_a_true_dome_and_toronto_uses_projecting_bay():
    paris = _profile(TARGETS[1], paris_draft())
    node_counts = Counter(item["kind"] for item in paris["massing_graph"]["nodes"])
    assert node_counts["dome_roof"] == 1
    dome = next(item for item in paris["massing_graph"]["nodes"] if item["kind"] == "dome_roof")
    assert dome["rib_count"] >= 10
    drum = next(item for item in paris["massing_graph"]["nodes"] if item["id"] == "paris_dome_drum")
    assert drum["kind"] == "cylinder"
    assert dome["location"][2] <= drum["location"][2] + drum["height_m"] / 2

    toronto = _profile(TARGETS[2], toronto_draft())
    bay = next(item for item in toronto["massing_graph"]["nodes"] if item["id"] == "toronto_bay_mass")
    assert bay["size"][1] >= 1.0
    assert any(item["id"] == "toronto_bay_sticker" for item in toronto["massing_graph"]["assemblies"])
    roof = next(item for item in toronto["massing_graph"]["nodes"] if item["id"] == "toronto_main_roof")
    assert roof["ridge_axis"] == "x"
    assert not any(item["id"] == "toronto_porch_shadow" for item in toronto["massing_graph"]["nodes"])


def test_amsterdam_front_sheet_is_cropped_once_not_split_by_floor():
    profile = _profile(TARGETS[0], amsterdam_draft())
    front = next(item for item in profile["massing_graph"]["assemblies"] if item["id"] == "amsterdam_front_sticker")
    assert front["uv_u_min"] == 0.20
    assert front["uv_u_max"] == 0.80
    assert front["height_m"] == 11.6


def test_pipeline_memory_gates_stickers_behind_complete_massing_and_exact_glass_masks():
    memory_path = Path(__file__).parents[1] / "high_quality_building_memory.json"
    memory = json.loads(memory_path.read_text(encoding="utf-8"))
    principles = {item["id"]: item["rule"] for item in memory["non_negotiable_principles"]}

    assert "continuous_sticker_glazing_requires_exact_mask_registration" in principles
    assert "opening-accurate semantic glass mask" in principles[
        "continuous_sticker_glazing_requires_exact_mask_registration"
    ]
    assert "sticker_generation_follows_complete_silhouette_approval" in principles
    massing_rule = principles["sticker_generation_follows_complete_silhouette_approval"]
    assert "all-elevation occupancy map" in massing_rule
    assert "pre-render hard stops" in massing_rule
