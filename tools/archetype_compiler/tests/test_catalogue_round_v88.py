"""V88 quality-first ten-building checkpoint contracts."""
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_v88_is_two_finite_five_building_batches():
    batches = [load("catalogue_round_v88_batch_a.json"), load("catalogue_round_v88_batch_b.json")]
    assert [len(batch["entries"]) for batch in batches] == [5, 5]
    assert all(batch["pipeline_version"] == "v88" for batch in batches)
    assert all(batch["paid_facade_calls"] == 0 for batch in batches)


def test_all_v88_profiles_require_complete_architect_workflow():
    profiles = load("architectural_signature_profiles.d/catalogue_round_v88.json")["profiles"]
    assert len(profiles) == 10
    for profile in profiles.values():
        production = profile["production_contract"]
        workflow = production["stage_workflow"]
        assert production["quality_contract_version"] == 4
        assert len(workflow["required_stages"]) == 10
        assert all(stage["approval_required"] for stage in workflow["required_stages"].values())
        assert workflow["architect_release_score"] >= 85
        assert workflow["hard_stops_block_release"] is True


def test_weak_v87_shapes_are_reauthored_not_retextured():
    profiles = load("architectural_signature_profiles.d/catalogue_round_v88.json")["profiles"]
    terracotta = profiles["glass_office_terracotta_fins"]["massing_graph"]
    catalan = profiles["med_arcade_catalan_modernista"]["massing_graph"]
    greystone = profiles["classic_brownstone_grey_stone"]["massing_graph"]
    assert any(node["id"] == "terracotta_middle_terrace" for node in terracotta["nodes"])
    assert not any(node["material"] == "glass" and node["kind"] == "box" for node in terracotta["nodes"])
    assert any(node["id"] == "catalan_rear_body" and node["kind"] == "box" for node in catalan["nodes"])
    assert any(item["id"] == "catalan_front_image_lock" for item in catalan["assemblies"])
    greystone_bays = [item for item in greystone["assemblies"] if item["id"].startswith("greystone_true_bay_")]
    assert len(greystone_bays) == 2
    assert all(item["columns"] == 3 and item["rows"] == 2 for item in greystone_bays)
    assert terracotta["reference_dimensions"] == {"width_m": 32.0, "depth_m": 22.0, "floors": 4}
    assert not any(item["kind"] == "frame_grid" for item in terracotta["assemblies"])
    terracotta_profile = profiles["glass_office_terracotta_fins"]
    assert terracotta_profile["dimension_overrides"]["default_floors"] == 4


def test_corbusian_roof_room_is_restrained_and_recessed():
    profile = load("architectural_signature_profiles.d/catalogue_round_v88.json")["profiles"]["modernist_civic_white_corbusian"]
    graph = profile["massing_graph"]
    penthouse = next(node for node in graph["nodes"] if node["id"] == "penthouse_block")
    assert penthouse["size"][0] <= 12.0
    assert any(item["id"] == "penthouse_true_ribbon" for item in graph["assemblies"])
    assert not any(item["id"] == "skin_penthouse_front" for item in graph["assemblies"])


def test_skin_driven_catalan_has_registered_local_depth():
    profile = load("architectural_signature_profiles.d/catalogue_round_v88.json")["profiles"]["med_arcade_catalan_modernista"]
    graph = profile["massing_graph"]
    ids = {item["id"] for item in graph["assemblies"]}
    assert {
        "catalan_front_image_lock",
        "catalan_piano_nobile_gallery",
        "catalan_left_oriel_stack",
        "catalan_right_oriel_stack",
    }.issubset(ids)
    front = next(item for item in graph["assemblies"] if item["id"] == "catalan_front_image_lock")
    assert front["kind"] == "facade_skin"
    assert all(not node["id"].endswith("_volume") for node in graph["nodes"])
    assert not any(item["kind"] == "curved_balcony_array" for item in graph["assemblies"])
    assert profile["production_contract"]["stage_workflow"]["representation"] == "registered_sticker_landmark"
    assert sum(node["id"].endswith("_stone_soffit") for node in graph["nodes"]) == 7


def test_catalan_sticker_method_is_a_fixed_select_and_place_landmark():
    profile = load("architectural_signature_profiles.d/catalogue_round_v88.json")["profiles"]["med_arcade_catalan_modernista"]
    graph = profile["massing_graph"]
    placement = profile["production_contract"]["placement_contract"]
    assert graph["reference_dimensions"] == {"width_m": 14.0, "depth_m": 31.0, "floors": 6}
    assert placement["method"] == "sticker_method"
    assert placement["mode"] == "fixed_landmark"
    assert placement["ui_interaction"] == "select_and_place"
    assert placement["polygon_fit"] is False
    assert placement["non_uniform_scale"] == "forbidden"
    assert placement["floor_count_change"] == "forbidden"
    assert any(item["id"] == "catalan_left_return" and item.get("source_image_path") for item in graph["assemblies"])
    assert any(node["id"] == "catalan_entry_opening_block" and node["kind"] == "opening_block" for node in graph["nodes"])
    assert any(node["id"] == "catalan_main_roof" and node["kind"] == "undulating_roof_shell" for node in graph["nodes"])
    entrance_skin = next(item for item in graph["assemblies"] if item["id"] == "catalan_front_image_lock")
    assert entrance_skin["opening_clearances"][0]["shape"] == "round_arch"
    assert entrance_skin["opening_clearances"][0]["spring_z_m"] == 1.95
    entrance_block = next(node for node in graph["nodes"] if node["id"] == "catalan_entry_opening_block")
    assert entrance_block["back_frame_material"] == "signature_metal"
    assert not any(item["id"] == "catalan_rear_gallery_balconies" for item in graph["assemblies"])
    assert not any(item["id"].endswith("_physical_windows") for item in graph["assemblies"])


def test_moorish_sticker_landmark_has_registered_deep_front_and_return_arcades():
    profile = load("architectural_signature_profiles.d/catalogue_round_v88.json")["profiles"]["med_arcade_moorish"]
    graph = profile["massing_graph"]
    placement = profile["production_contract"]["placement_contract"]
    assert graph["reference_dimensions"] == {"width_m": 20.0, "depth_m": 15.0, "floors": 2}
    assert placement["method"] == "sticker_method"
    assert placement["mode"] == "fixed_landmark"
    assert placement["polygon_fit"] is False
    front = next(node for node in graph["nodes"] if node["id"] == "moorish_front_deep_arcade")
    side = next(node for node in graph["nodes"] if node["id"] == "moorish_right_deep_arcade")
    assert front["kind"] == side["kind"] == "opening_block"
    assert front["axis"] == "front" and len(front["opening_centres_m"]) == 3
    assert side["axis"] == "right" and len(side["opening_centres_m"]) == 2
    assert front["size"][1] >= 6.0 and side["size"][0] >= 3.0
    front_skin = next(item for item in graph["assemblies"] if item["id"] == "moorish_front_arcade_sticker")
    side_skin = next(item for item in graph["assemblies"] if item["id"] == "moorish_right_arcade_sticker")
    assert len(front_skin["opening_clearances"]) == 3
    assert len(side_skin["opening_clearances"]) == 2
    assert all(item["shape"] == "horseshoe_arch" for item in front_skin["opening_clearances"] + side_skin["opening_clearances"])
    assert any(item["id"] == "moorish_geometric_roof_parapet" and item["kind"] == "lattice_parapet" for item in graph["assemblies"])
    assert profile["production_contract"]["stage_workflow"]["representation"] == "registered_sticker_landmark"


def test_catalan_stickers_share_one_exact_facade_registration_frame():
    profile = load("architectural_signature_profiles.d/catalogue_round_v88.json")["profiles"]["med_arcade_catalan_modernista"]
    graph = profile["massing_graph"]
    registered = [
        item for item in graph["assemblies"]
        if item.get("registration_group") == "catalan_front_elevation"
    ]
    assert len(registered) >= 9
    for item in registered:
        cx, _cy, cz = item["centre"]
        span, height = item["span_m"], item["height_m"]
        assert abs(item.get("uv_u_min", 0.0) - ((cx - span / 2 + 7.0) / 14.0)) < 1e-9
        assert abs(item.get("uv_u_max", 1.0) - ((cx + span / 2 + 7.0) / 14.0)) < 1e-9
        assert abs(item.get("uv_v_min", 0.0) - ((cz - height / 2) / 17.0 * 0.79)) < 1e-9
        assert abs(item.get("uv_v_max", 1.0) - ((cz + height / 2) / 17.0 * 0.79)) < 1e-9

    registration = profile["production_contract"]["image_lock"]["surface_registration"]
    assert registration["anchor_types"] == ["window_centres", "column_centres", "floor_datums"]
    base = [item for item in registered if item["mask_semantics"] == "continuous_registration_base"]
    assert len(base) == 1 and "alpha_mask_path" not in base[0]
    assert all(
        item.get("alpha_mask_path", "").endswith(".png")
        for item in registered if item["mask_semantics"] == "alpha_isolated_projected_feature"
    )
