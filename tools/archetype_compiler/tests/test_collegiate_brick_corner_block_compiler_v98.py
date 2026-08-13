from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


TOOL_DIR = Path(__file__).resolve().parents[1]
if str(TOOL_DIR) not in sys.path: sys.path.insert(0, str(TOOL_DIR))
from build_collegiate_brick_corner_block_sticker_lego_v98 import build_geometry
from compile_collegiate_brick_corner_block_sticker_lego_v98 import (
    ASSETS, GEOMETRY_HASHES, REFERENCE_HASHES, SIZE_MATRIX, _build_profile, _carrier, _face_groups,
)
from glass_profiles import GLASS_PROFILES


def _carriers(size: str = "canonical") -> list[dict]:
    return [_carrier(mesh, group) for mesh in build_geometry(size)["meshes"] for group in _face_groups(mesh)]


def test_exact_locks_profiles_and_whole_module_contract() -> None:
    assert {size: build_geometry(size)["geometry_sha256"] for size in SIZE_MATRIX} == GEOMETRY_HASHES
    assert set(REFERENCE_HASHES) == set(build_geometry("canonical")["reference_evidence"])
    canonical, extended = build_geometry("canonical"), build_geometry("extended")
    assert extended["dimensions"]["width_m"] - canonical["dimensions"]["width_m"] == 7.0
    assert canonical["courtyard"]["width_m"] == 14.0 and extended["courtyard"]["width_m"] == 21.0
    assert not canonical["whole_modules"] and len(extended["whole_modules"]) == 10
    assert all(m.get("module_width_m") == 7.0 for m in extended["meshes"] if m["name"] in extended["whole_modules"])
    for size in SIZE_MATRIX:
        profile, package = _build_profile(size)
        assert package["status"] == "pass" and not package["failures"]
        assert profile["production_contract"]["clay_lock"]["geometry_sha256"] == GEOMETRY_HASHES[size]


def test_every_visible_face_owned_exactly_once_without_fallback() -> None:
    registered = set(ASSETS.values())
    for size in SIZE_MATRIX:
        geometry = build_geometry(size); carriers = _carriers(size)
        counts = {(m["name"], face): 0 for m in geometry["meshes"] for face in range(len(m["faces"]))}
        for carrier in carriers:
            assert carrier["source_image_path"] in registered
            assert carrier["final_surface_coverage"] is True
            assert "generic" not in carrier["finish_class"] and "fallback" not in carrier["finish_class"]
            for face in carrier["face_indices"]: counts[(carrier["surface_id"], face)] += 1
        assert counts and set(counts.values()) == {1}
        profile, _ = _build_profile(size)
        audit = profile["massing_graph"]["final_surface_audit"]
        assert audit["status"] == "pass" and audit["owned_once_count"] == audit["visible_face_count"] == len(counts)


def test_roles_are_disjoint_and_courtyard_corner_blades_complete() -> None:
    geometry = build_geometry("canonical"); carriers = _carriers(); by = {c["surface_id"]: c for c in carriers if len(c["face_indices"]) == len(next(m for m in geometry["meshes"] if m["name"] == c["surface_id"])["faces"])}
    roles = {c["floor_role"] for c in carriers}
    assert {"ground", "middle", "top", "entry", "blades", "corner_ground", "corner_middle", "corner_top",
            "courtyard_ground", "courtyard_middle", "courtyard_top", "crown", "roof", "roof_screen", "roof_equipment"} <= roles
    court = [m for m in geometry["meshes"] if m.get("courtyard") or str(m.get("side", "")).startswith("court_")]
    assert court and all(any(c["surface_id"] == m["name"] for c in carriers) for m in court)
    blades = [m for m in geometry["meshes"] if m.get("carrier_kind") == "entry_precast_blade"]
    assert len(blades) == 2 and all(by[m["name"]]["source_image_path"] == ASSETS["precast"] for m in blades)
    assert sum(m.get("carrier_kind") == "corner_crown" for m in geometry["meshes"]) == 1


def test_metric_brick_constant_across_sides_court_and_tiers() -> None:
    for size in SIZE_MATRIX:
        geometry = build_geometry(size); carriers = _carriers(size)
        brick_meshes = [m for m in geometry["meshes"] if m["material_domain"] == "warm_brick"]
        assert brick_meshes
        for mesh in brick_meshes:
            related = [c for c in carriers if c["surface_id"] == mesh["name"]]
            assert related and all(c["world_metric_uv_tile_m"] == 2.4 for c in related)
            assert all(c["source_image_path"] in {ASSETS["brick_front"], ASSETS["brick_return"], ASSETS["brick_court"]} for c in related)


def test_glass_cards_and_backings_are_separate_exact_atlas_cells() -> None:
    geometry = build_geometry("canonical"); carriers = _carriers(); by = {c["surface_id"]: c for c in carriers}
    glass = [m for m in geometry["meshes"] if m["material_domain"] == "recessed_glazing"]
    cards = [m for m in geometry["meshes"] if m["material_domain"] == "interior_card"]
    backs = [m for m in geometry["meshes"] if m["material_domain"] == "interior_backing"]
    assert len(glass) == len(cards) == len(backs) == 218
    for mesh in glass:
        c = by[mesh["name"]]
        assert c["material_role"] == "glass" and c["glass_profile"] in GLASS_PROFILES
        assert c["source_image_path"] in {ASSETS["glass_residential"], ASSETS["glass_corner"]}
        assert .25 <= c["surface_alpha_override"] <= .32
        assert .88 <= c["transmission_override"] <= .94
        assert .04 <= c["roughness_override"] <= .065
        assert "uv_u_min" not in c
    for mesh in cards + backs:
        c = by[mesh["name"]]
        assert c["source_image_path"] in {ASSETS["interior_residential"], ASSETS["interior_corner"], ASSETS["interior_lobby"]}
        assert c["uv_u_max"] - c["uv_u_min"] == .25 and c["uv_v_max"] - c["uv_v_min"] == .5
        if mesh["material_domain"] == "interior_backing": assert c["emission_strength_override"] == 0.0
        else: assert .060 <= c["emission_strength_override"] <= .095


def test_roof_plan_bounds_datums_and_semantic_separation() -> None:
    geometry = build_geometry("canonical"); carriers = _carriers()
    roof = [c for c in carriers if c["floor_role"] == "roof"]
    assert roof and all(c["axis"] == "plan" and len(c["plan_bounds"]) == 4 for c in roof)
    assert {c["source_image_path"] for c in roof} == {ASSETS["gravel"], ASSETS["membrane"]}
    membrane = [c for c in roof if c["source_image_path"] == ASSETS["membrane"]]
    assert len(membrane) == 6 and all(c["sticker_layer"] == "dark_inner_membrane" for c in membrane)
    by = {m["name"]: m for m in geometry["meshes"]}
    for carrier in roof:
        for face in carrier["face_indices"]:
            assert min(by[carrier["surface_id"]]["vertices"][i][2] for i in by[carrier["surface_id"]]["faces"][face]) >= 17.2
    returns = [c for c in carriers if c["sticker_layer"] == "roof_edge_flashing"]
    assert returns and all(c["floor_role"] == "crown" and c["source_image_path"] == ASSETS["flashing"] for c in returns)
    screen = [c for c in carriers if c["floor_role"] == "roof_screen"]
    assert screen and all(c["source_image_path"] == ASSETS["bronze_screen"] for c in screen)


def test_asset_provenance_is_hash_locked() -> None:
    provenance = json.loads((TOOL_DIR / "sticker_assets/collegiate_brick_corner_block_v98/provenance.json").read_text())
    assert len(provenance["assets"]) == 25
    for record in provenance["assets"].values():
        path = TOOL_DIR.parents[1] / record["path"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == record["sha256"]


def test_clay_v1_repairs_inherit_adjacent_semantic_finishes() -> None:
    geometry = build_geometry("canonical"); carriers = _carriers(); by = {c["surface_id"]: c for c in carriers}
    kinds: dict[str, list[dict]] = {}
    for mesh in geometry["meshes"]: kinds.setdefault(str(mesh.get("carrier_kind")), []).append(mesh)
    assert len(kinds["datum_slot_closure"]) == 32
    assert all(by[m["name"]]["source_image_path"] in {ASSETS["brick_front"], ASSETS["brick_return"], ASSETS["brick_court"]}
               for m in kinds["datum_slot_closure"])
    pale_kinds = ("mega_light_mullion", "mega_masonry_spandrel", "multi_storey_mega_frame",
                  "multi_storey_mega_frame_bridge", "entry_slot_bridge", "oriel_terminal_cheek",
                  "corner_lobby_pale_pier", "corner_lobby_pale_plinth")
    assert all(kinds[k] for k in pale_kinds)
    for kind in pale_kinds:
        assert all(by[m["name"]]["source_image_path"] in {ASSETS["precast"], ASSETS["base"]} for m in kinds[kind])
    cheeks = kinds["entry_recess_cheek"]
    assert len(cheeks) == 2
    assert {by[m["name"]]["source_image_path"] for m in cheeks} == {ASSETS["precast"], ASSETS["brick_return"]}
    mega_glass = [m for m in geometry["meshes"] if m.get("grouped_lights") == 3 and m["material_domain"] == "recessed_glazing"]
    assert len(mega_glass) == 45 and all(by[m["name"]]["source_image_path"] == ASSETS["glass_residential"] for m in mega_glass)


def test_clay_v2_wall_zones_junction_depth_and_entry_back_roof_are_owned() -> None:
    geometry = build_geometry("canonical"); carriers = _carriers(); by = {c["surface_id"]: c for c in carriers}
    kinds: dict[str, list[dict]] = {}
    for mesh in geometry["meshes"]: kinds.setdefault(str(mesh.get("carrier_kind")), []).append(mesh)
    assert len(kinds["aperture_sill_wall"]) == len(kinds["aperture_head_wall"]) == 185
    wall_zones = kinds["aperture_sill_wall"] + kinds["aperture_head_wall"]
    for mesh in wall_zones:
        expected = ASSETS["precast"] if mesh.get("level") == 0 else (ASSETS["brick_court"] if str(mesh.get("side", "")).startswith("court_") else ASSETS["brick_front"] if mesh.get("side") == "front" else ASSETS["brick_return"])
        assert by[mesh["name"]]["source_image_path"] == expected
    entry_back = [m for m in geometry["meshes"] if m.get("behind_shallow_entry")]
    assert entry_back and any(m["material_domain"] == "residential_slab" for m in entry_back)
    assert any(m["material_domain"] == "gravel_roof" for m in entry_back)
    for mesh in entry_back:
        sources = {c["source_image_path"] for c in carriers if c["surface_id"] == mesh["name"]}
        expected = ({ASSETS["base"]} if mesh["material_domain"] == "residential_slab" else
                    {ASSETS["membrane"], ASSETS["flashing"]} if mesh["material_domain"] == "dark_roof_membrane" else
                    {ASSETS["gravel"], ASSETS["flashing"]})
        assert sources == expected
    assert len(kinds["entry_slot_bridge"]) == 5 and len(kinds["oriel_terminal_cheek"]) == 2
    assert all(by[m["name"]]["source_image_path"] == ASSETS["precast"] for m in kinds["entry_slot_bridge"] + kinds["oriel_terminal_cheek"])
    assert len(kinds["pale_ground_pier"]) == 2 and all(by[m["name"]]["source_image_path"] == ASSETS["precast"] for m in kinds["pale_ground_pier"])
    mega = kinds["multi_storey_mega_frame"] + kinds["multi_storey_mega_frame_bridge"]
    assert mega and all(m.get("projection_depth_m") == .22 for m in mega)
    assert all(by[m["name"]]["source_image_path"] == ASSETS["precast"] for m in mega)


def test_signature_corner_binding_and_continuous_ground_datums_are_owned() -> None:
    geometry = build_geometry("canonical"); carriers = _carriers(); by = {c["surface_id"]: c for c in carriers}
    kinds: dict[str, list[dict]] = {}
    for mesh in geometry["meshes"]: kinds.setdefault(str(mesh.get("carrier_kind")), []).append(mesh)
    pale = ("stair_oriel_binding_cheek", "stair_oriel_binding_bridge", "continuous_corner_canopy")
    assert all(len(kinds[k]) == 1 for k in pale)
    assert all(by[kinds[k][0]["name"]]["source_image_path"] == ASSETS["precast"] for k in pale)
    assert len(kinds["continuous_corner_plinth"]) == 1
    assert by[kinds["continuous_corner_plinth"][0]["name"]]["source_image_path"] == ASSETS["base"]
    assert all(m.get("broad_corner_pavilion") for m in kinds["oriel_spandrel_band"] + kinds["oriel_soffit"] + kinds["oriel_cap"] + kinds["corner_crown"])
    assert all(by[m["name"]]["source_image_path"] == ASSETS["bronze_spandrel"] for m in kinds["oriel_spandrel_band"] + kinds["oriel_cap"] + kinds["corner_crown"])
    assert by[kinds["oriel_soffit"][0]["name"]]["source_image_path"] == ASSETS["precast"]
    broad_glass = [m for m in geometry["meshes"] if m.get("broad_corner_pavilion") and m["material_domain"] == "recessed_glazing"]
    assert len(broad_glass) == 24 and all(by[m["name"]]["source_image_path"] == ASSETS["glass_corner"] for m in broad_glass)


def test_explicit_terminal_caps_inherit_pale_adjacent_finish() -> None:
    for size in SIZE_MATRIX:
        geometry = build_geometry(size); carriers = _carriers(size)
        by_surface: dict[str, list[dict]] = {}
        for carrier in carriers: by_surface.setdefault(carrier["surface_id"], []).append(carrier)
        explicit = [m for m in geometry["meshes"] if m.get("outward_terminal_faces") and
                    m.get("terminal_source_map") in {"pale_precast", "court_coping"}]
        assert len([m for m in explicit if m.get("carrier_kind") == "court_coping_corner_cap"]) == 4
        assert explicit
        for mesh in explicit:
            assert mesh["material_domain"] == "precast"
            expected = ASSETS["coping"] if (mesh.get("terminal_source_map") == "court_coping" or
                                             mesh.get("carrier_kind") == "parapet_corner_cap") else ASSETS["precast"]
            assert {c["source_image_path"] for c in by_surface[mesh["name"]]} == {expected}
            assert all(c["source_image_path"] != ASSETS["joint"] for c in by_surface[mesh["name"]])


def test_floor_band_endpoint_and_oriel_junction_caps_are_pale_precast_only() -> None:
    forbidden = {
        ASSETS["joint"], ASSETS["interior_residential"],
        ASSETS["interior_corner"], ASSETS["interior_lobby"],
    }
    for size in SIZE_MATRIX:
        geometry = build_geometry(size); carriers = _carriers(size)
        by_surface: dict[str, list[dict]] = {}
        for carrier in carriers: by_surface.setdefault(carrier["surface_id"], []).append(carrier)
        caps = [m for m in geometry["meshes"] if m.get("carrier_kind") == "precast_datum_endpoint_cap"]
        assert len(caps) == 20
        assert {m.get("terminal") for m in caps} == {
            "mega0_left", "mega0_right", "mega1_left", "mega1_right", "oriel_junction",
        }
        assert all(m["material_domain"] == "precast" and m.get("outward_terminal_faces")
                   and m.get("terminal_source_map") == "pale_precast" for m in caps)
        for mesh in caps:
            assigned = {c["source_image_path"] for c in by_surface[mesh["name"]]}
            assert assigned == {ASSETS["precast"]}
            assert assigned.isdisjoint(forbidden)


def test_final_sill_closures_and_pale_datum_contract_never_use_dark_or_interior() -> None:
    forbidden = {
        ASSETS["joint"], ASSETS["interior_residential"], ASSETS["interior_corner"],
        ASSETS["interior_lobby"], ASSETS["membrane"], ASSETS["bronze_spandrel"],
    }
    expected_sills = {"canonical": 15, "extended": 20}
    for size in SIZE_MATRIX:
        geometry = build_geometry(size); carriers = _carriers(size)
        by_surface: dict[str, list[dict]] = {}
        for carrier in carriers: by_surface.setdefault(carrier["surface_id"], []).append(carrier)
        sills = [m for m in geometry["meshes"] if m.get("carrier_kind") == "mega_sill_slot_closure"]
        assert len(sills) == expected_sills[size]
        protected = [m for m in geometry["meshes"] if
                     m.get("explicit_underside_role") == "pale_precast_underside"]
        assert all(m["material_domain"] == "precast" for m in protected)
        assert all(m.get("terminal_source_map") == "pale_precast" and
                   m.get("explicit_underside_role") == "pale_precast_underside" for m in sills)
        corner_ends = [m for m in protected if m.get("datum_corner_endpoint")]
        assert len(corner_ends) == 4
        for mesh in protected:
            assigned = {c["source_image_path"] for c in by_surface[mesh["name"]]}
            assert assigned == {ASSETS["precast"]}
            assert assigned.isdisjoint(forbidden)


def test_v2_roof_and_metal_authority_are_explicit() -> None:
    carriers = _carriers()
    screen = [c for c in carriers if c["sticker_layer"] == "bronze_mechanical_screen"]
    hvac = [c for c in carriers if c["sticker_layer"] in {"aged_galvanized_hvac", "galvanized_roof_service"}]
    assert screen and all(c["metallic_override"] == .72 and c["world_metric_uv_tile_m"] == 1.0 for c in screen)
    assert hvac and all(c["metallic_override"] >= .78 for c in hvac)


def test_court_brick_parapet_bases_caps_and_pale_coping_are_disjoint() -> None:
    geometry = build_geometry("canonical"); carriers = _carriers(); by: dict[str, list[dict]] = {}
    for carrier in carriers: by.setdefault(carrier["surface_id"], []).append(carrier)
    brick = [m for m in geometry["meshes"] if m.get("carrier_kind") == "court_parapet_brick_base"]
    closures = [m for m in geometry["meshes"] if m.get("carrier_kind") == "court_continuous_corner_L"]
    pale = [m for m in geometry["meshes"] if m.get("terminal_source_map") == "court_coping"]
    assert len(brick) == 4 and len(closures) == 4 and len(pale) == 12
    assert all(m["material_domain"] == "warm_brick" for m in brick)
    assert all({c["source_image_path"] for c in by[m["name"]]} == {ASSETS["brick_court"]} for m in brick)
    assert all(m["material_domain"] == "warm_brick" and m.get("terminal_source_map") == "court_brick"
               and m.get("render_risk_closure") for m in closures)
    assert all({c["source_image_path"] for c in by[m["name"]]} == {ASSETS["brick_court"]} for m in closures)
    assert all(c["final_surface_coverage"] is True for m in closures for c in by[m["name"]])
    assert all({c["source_image_path"] for c in by[m["name"]]} == {ASSETS["coping"]} for m in pale)


def test_optical_v3_room_cues_stairs_and_bright_lobby_are_semantic() -> None:
    geometry = build_geometry("canonical"); carriers = _carriers(); by: dict[str, list[dict]] = {}
    for carrier in carriers: by.setdefault(carrier["surface_id"], []).append(carrier)
    rooms = [m for m in geometry["meshes"] if m["material_domain"] == "interior_architecture"]
    stairs = [m for m in geometry["meshes"] if m.get("carrier_kind") == "stair_landing"]
    lobby_pale = [m for m in geometry["meshes"] if m.get("carrier_kind") in
                  {"bright_lobby_floor", "bright_lobby_ceiling"}]
    lobby_back = [m for m in geometry["meshes"] if m["material_domain"] == "bright_interior_card"]
    assert len(rooms) == 872 and len(stairs) == 4 and len(lobby_pale) == 2 and len(lobby_back) == 1
    assert all({c["source_image_path"] for c in by[m["name"]]} == {ASSETS["precast"]}
               for m in rooms + stairs + lobby_pale)
    lobby_carrier = by[lobby_back[0]["name"]][0]
    assert lobby_carrier["source_image_path"] == ASSETS["interior_lobby"]
    assert lobby_carrier["emission_strength_override"] == .12
    assert lobby_carrier["uv_u_max"] - lobby_carrier["uv_u_min"] == .25


def test_optical_v3_oriel_has_highest_reflection_authority() -> None:
    carriers = _carriers()
    ordinary = [c for c in carriers if c["sticker_layer"] == "physical_residential_glass"]
    oriel = [c for c in carriers if c["sticker_layer"] == "physical_corner_glass"]
    assert ordinary and oriel
    assert all(c["glass_profile"] == "residential_low_e" and c["transmission_override"] == .94 for c in ordinary)
    assert all(c["glass_profile"] == "reflective_curtain_wall" and c["coat_weight_override"] == .30 for c in oriel)
    assert min(c["specular_ior_level_override"] for c in oriel) > max(c["specular_ior_level_override"] for c in ordinary)
