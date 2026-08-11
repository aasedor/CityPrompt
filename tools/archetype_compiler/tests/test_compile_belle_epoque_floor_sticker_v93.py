from __future__ import annotations

import math

from compile_belle_epoque_floor_sticker_v93 import FLOOR_SURFACE_IDS, build_profile, build_profiles


def test_profiles_compile_for_both_bounded_floor_counts() -> None:
    payload, registry = build_profiles()
    assert set(payload["profiles"]) == {
        "grand-magasin-belle-epoque-floor-5", "grand-magasin-belle-epoque-floor-6",
        "grand-magasin-belle-epoque",
    }
    assert [entry["floors"] for entry in registry["entries"]] == [5, 6]


def test_compiler_replaces_full_height_elevation_carriers_with_floor_carriers() -> None:
    profile = build_profile(5)
    assemblies = profile["massing_graph"]["assemblies"]
    floor = [item for item in assemblies if item.get("sticker_layer") == "floor_band"]
    assert len(floor) == 45
    assert len([item for item in assemblies if item.get("sticker_layer") == "floor_coverage_seal"]) == 45
    assert not any(
        (str(item.get("surface_id")) in FLOOR_SURFACE_IDS or str(item.get("semantic_surface_id")) in FLOOR_SURFACE_IDS)
        and item.get("sticker_layer") not in {"floor_band", "floor_coverage_seal"}
        for item in assemblies
    )


def test_every_floor_carrier_targets_one_floor_addressable_mesh() -> None:
    profile = build_profile(6)
    graph = profile["massing_graph"]
    mesh_names = {mesh["name"] for mesh in graph["nodes"][0]["meshes"]}
    floor = [item for item in graph["assemblies"] if item.get("sticker_layer") == "floor_band"]
    assert len(floor) == 54
    assert len([item for item in graph["assemblies"] if item.get("sticker_layer") == "floor_coverage_seal"]) == 54
    assert all(len(item["target_ids"]) == 1 and item["target_ids"][0] in mesh_names for item in floor)


def test_roof_source_never_appears_on_floor_carrier() -> None:
    for floors in (5, 6):
        profile = build_profile(floors)
        floor = [item for item in profile["massing_graph"]["assemblies"] if item.get("sticker_layer") == "floor_band"]
        assert all(item["source_id"] != "roof" for item in floor)
        assert all(item["roof_material_allowed"] is False for item in floor)


def test_six_storey_profile_shifts_full_fixed_roof_group() -> None:
    five = build_profile(5)
    six = build_profile(6)
    assert math.isclose(six["massing_graph"]["height_m"] - five["massing_graph"]["height_m"], 4.1)
    assert six["production_contract"]["floor_sticker_method"]["sequence"].count("middle_repeat") == 2
    assert five["production_contract"]["floor_sticker_method"]["sequence"].count("middle_repeat") == 1
