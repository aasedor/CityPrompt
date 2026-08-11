from __future__ import annotations

from build_belle_epoque_continuous_geometry_v94 import SURFACES, build_continuous_geometry
from compile_belle_epoque_continuous_sticker_v94 import build_profile


def test_continuous_geometry_has_one_cap_free_wall_per_elevation() -> None:
    geometry = build_continuous_geometry()
    assert geometry["audit"]["status"] == "pass"
    assert geometry["audit"]["continuous_wall_count"] == len(SURFACES) == 9
    assert geometry["audit"]["internal_floor_cap_count"] == 0
    assert not any(mesh["name"] == "wrapped_corner_canopy" for mesh in geometry["meshes"])


def test_every_continuous_wall_has_exact_floor_and_hero_face_owners() -> None:
    geometry = build_continuous_geometry()
    walls = [mesh for mesh in geometry["meshes"] if mesh.get("material_domain") == "vertical_occupied_floor"]
    for mesh in walls:
        assert set(mesh["floor_face_indices"]) == {"0", "1", "2", "3", "4"}
        assert set(mesh["hero_floor_face_indices"]) == {"0", "1", "2", "3", "4"}
        owned = [index for indices in mesh["floor_face_indices"].values() for index in indices]
        assert sorted(owned) == list(range(len(mesh["faces"])))


def test_profile_uses_continuous_floor_carriers_and_physical_signature_details() -> None:
    profile = build_profile()
    graph = profile["massing_graph"]
    floor = [item for item in graph["assemblies"] if item.get("sticker_layer") == "floor_band"]
    coverage = [item for item in graph["assemblies"] if item.get("sticker_layer") == "floor_coverage_seal"]
    kinds = {item["kind"] for item in graph["assemblies"]}
    assert len(floor) == len(coverage) == 45
    assert all(item.get("continuous_shell") and item.get("face_indices") for item in floor + coverage)
    assert {"recessed_portal_section", "curved_glass_canopy", "dome_rib_system"} <= kinds
    assert "shadow_line" not in {
        item["kind"] for item in graph["assemblies"] if str(item.get("id", "")).startswith("v94_")
    }
    assert graph["continuous_floor_sticker_contract"]["internal_floor_cap_count"] == 0


def test_legacy_opaque_canopy_carriers_do_not_survive() -> None:
    profile = build_profile()
    assemblies = profile["massing_graph"]["assemblies"]
    assert not any("wrapped_corner_canopy" in item.get("target_ids", []) for item in assemblies)
    assert not any(item.get("id") == "v92_skin_wrapped_canopy" for item in assemblies)


def test_entrance_uses_registered_corner_crop_behind_physical_frame() -> None:
    profile = build_profile()
    assemblies = profile["massing_graph"]["assemblies"]
    entrance = next(item for item in assemblies if item.get("id") == "v94_portal_glass_sticker")
    assert entrance["material_role"] == "glass"
    assert entrance["sticker_layer"] == "entrance_optical_overlay"
    assert entrance["uv_u_min"] > 0 and entrance["uv_u_max"] < 1
    assert entrance["uv_v_max"] < 0.5


def test_roof_edge_uses_directional_stickers_not_full_plan_wrap() -> None:
    assemblies = build_profile()["massing_graph"]["assemblies"]
    assert not any(item.get("id") == "v92_skin_perimeter_roof_edge_wrap" for item in assemblies)
    edge = [item for item in assemblies if item.get("sticker_layer") == "roof_edge_finish"]
    assert len(edge) == 4
    assert {item["axis"] for item in edge} == {"front", "right", "rear", "left"}
    assert {face for item in edge for face in item["face_indices"]} == set(range(4)) | set(range(8, 12)) | set(range(16, 20))


def test_corner_cupola_is_lower_and_tower_uses_only_upper_atlas() -> None:
    geometry = build_continuous_geometry()
    cupola = next(mesh for mesh in geometry["meshes"] if mesh["name"] == "corner_glass_cupola")
    assert max(vertex[2] for vertex in cupola["vertices"]) < 27.2
    assemblies = build_profile()["massing_graph"]["assemblies"]
    tower = next(item for item in assemblies if item.get("id") == "v92_skin_corner_tower")
    assert tower["uv_v_min"] >= 0.7
    assert tower["height_m"] < 5.0


def test_principal_join_has_registered_return_and_no_rail_cornices() -> None:
    geometry = build_continuous_geometry()
    names = {mesh["name"] for mesh in geometry["meshes"]}
    assert not any("main_cornice" in name or "crown_return" in name for name in names)
    assemblies = build_profile()["massing_graph"]["assemblies"]
    join = next(item for item in assemblies if item.get("sticker_layer") == "corner_join_finish")
    assert join["target_ids"] == ["facade_front_continuous_wall"]
    assert join["face_indices"] == [4, 8, 12, 16, 21, 27]
