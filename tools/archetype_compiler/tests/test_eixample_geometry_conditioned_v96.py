from __future__ import annotations

from build_eixample_conditioned_geometry_v96 import build_geometry
from compile_eixample_geometry_conditioned_v96 import FLOOR_ROLE, build_outputs


def test_locked_geometry_is_four_storeys_with_true_courtyard_and_portal() -> None:
    geometry = build_geometry()
    assert geometry["floor_count"] == 4
    assert geometry["open_courtyard"] is True
    names = {mesh["name"] for mesh in geometry["meshes"]}
    assert {f"outer_wall_{index}" for index in range(8)} <= names
    assert {f"court_wall_{index}" for index in range(8)} <= names
    assert {"terrace_roof_ring", "hero_portal_tunnel", "hero_portal_door"} <= names
    court_roof = next(mesh for mesh in geometry["meshes"] if mesh["name"] == "courtyard_floor")
    assert {vertex[2] for vertex in court_roof["vertices"]} == {14.5}
    hero = next(mesh for mesh in geometry["meshes"] if mesh["name"] == "outer_wall_1")
    assert len(hero["floor_face_indices"]["0"]) == 3
    assert all(hero["floor_face_indices"][str(floor)] for floor in range(4))


def test_every_locked_face_has_exactly_one_sticker_owner() -> None:
    payload, _registry, package, contract = build_outputs()
    profile = payload["profiles"]["eixample_apartment_block"]
    geometry_node = profile["massing_graph"]["nodes"][0]
    face_count = {mesh["name"]: len(mesh["faces"]) for mesh in geometry_node["meshes"]}
    owners = {name: [0] * count for name, count in face_count.items()}
    for assembly in profile["massing_graph"]["assemblies"]:
        if assembly.get("kind") != "carrier_skin":
            continue
        for target in assembly["target_ids"]:
            if target not in owners:
                continue
            selected = assembly.get("face_indices") or list(range(face_count[target]))
            for face in selected:
                owners[target][int(face)] += 1
    assert package["status"] == "pass"
    assert contract["status"] == "pass"
    assert package["carrier_count"] == 117
    assert all(value == 1 for values in owners.values() for value in values)


def test_floor_and_roof_domains_never_overlap() -> None:
    payload, _registry, _package, _contract = build_outputs()
    profile = payload["profiles"]["eixample_apartment_block"]
    assemblies = [item for item in profile["massing_graph"]["assemblies"] if item.get("kind") == "carrier_skin"]
    roles = {item["floor_role"] for item in assemblies}
    assert set(FLOOR_ROLE) | {"roof"} <= roles
    for item in assemblies:
        if item["floor_role"] == "roof":
            assert item["material_role"] == "roof"
            assert not any(str(target).startswith(("outer_wall_", "court_wall_")) for target in item["target_ids"])
        elif item["floor_role"] != "top_crown" or not any("parapet" in target for target in item["target_ids"]):
            assert item["material_role"] == "elevation"
            assert item.get("z_max_m", 4.0) <= 19.5


def test_semantic_registration_prevents_false_portals_and_roof_crown_overlap() -> None:
    payload, _registry, _package, _contract = build_outputs()
    profile = payload["profiles"]["eixample_apartment_block"]
    carriers = [item for item in profile["massing_graph"]["assemblies"] if item.get("kind") == "carrier_skin"]
    wall_carriers = [item for item in carriers if any(target.startswith(("outer_wall_", "court_wall_")) for target in item["target_ids"])]
    principal = [item for item in wall_carriers if "principal_elevation" in item["source_image_path"]]
    assert {item["target_ids"][0] for item in principal} == {"outer_wall_1"}
    assert max(item["uv_v_max"] for item in wall_carriers) == 0.8948
    for prefix in ("outer_parapet", "court_parapet"):
        for segment in range(8):
            target = f"{prefix}_{segment}"
            crown = next(item for item in carriers if item["id"] == f"v96_{target}_crown_sticker")
            roof_return = next(item for item in carriers if item["id"] == f"v96_{target}_roof_return_sticker")
            cap = next(item for item in carriers if item["id"] == f"v96_{target}_terracotta_cap_sticker")
            assert crown["face_indices"] == [0]
            assert (crown["uv_v_min"], crown["uv_v_max"], crown["floor_role"]) == (0.8948, 1.0, "top_crown")
            assert roof_return["face_indices"] == [1]
            assert roof_return["floor_role"] == "roof"
            assert cap["face_indices"] == [2]
            assert "terracotta_cap" in cap["source_image_path"]


def test_floor_specific_balcony_counts_and_repeatable_height() -> None:
    payload, _registry, _package, _contract = build_outputs()
    profile = payload["profiles"]["eixample_apartment_block"]
    balconies = [item for item in profile["massing_graph"]["assemblies"] if item.get("kind") == "balcony_array"]
    assert len(balconies) == 16
    assert {item["segments"] for item in balconies if item["levels_z"] == [4.72]} == {3}
    assert {item["segments"] for item in balconies if item["levels_z"] == [9.72, 14.72]} == {4}
    assert all(item["planter_enabled"] is False for item in balconies)
    assert all(item["rail_enabled"] is False for item in balconies)
    assert profile["massing_graph"]["reference_dimensions"]["repeatable_middle_height_m"] == 5.0


def test_profile_is_fixed_select_and_place_landmark() -> None:
    payload, registry, package, _contract = build_outputs()
    profile = payload["profiles"]["eixample_apartment_block"]
    production = profile["production_contract"]
    assert production["placement_model"] == "select_and_place_landmark"
    assert production["architect_score_target"] == 95
    assert production["floor_sticker_method"]["post_generation_nonuniform_scale_allowed"] is False
    assert profile["dimension_overrides"]["default_floors"] == 4
    assert registry["paid_facade_calls"] == 0
    assert package["locked_geometry_sha256"] == profile["massing_graph"]["carrier_space_contract"]["locked_geometry_sha256"]
    # The real catalogue variant must resolve to V96 during normal generation,
    # not silently fall back to the legacy rectangular Eixample profile.
    assert payload["profiles"]["eixample-apartment-block-classic"] == profile
    rooflights = [node for node in profile["massing_graph"]["nodes"] if "rooflight" in node["id"]]
    assert len(rooflights) == 4
    assert {node["material"] for node in rooflights} == {"rooflight_glass"}
