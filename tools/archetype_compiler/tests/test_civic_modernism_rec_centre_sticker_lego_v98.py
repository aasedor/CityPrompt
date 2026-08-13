from __future__ import annotations

import sys
from pathlib import Path

TOOL_DIR=Path(__file__).resolve().parents[1]
if str(TOOL_DIR) not in sys.path: sys.path.insert(0,str(TOOL_DIR))

from build_civic_modernism_rec_centre_sticker_lego_v98 import SIZE_MATRIX,build_geometry
from compile_civic_modernism_rec_centre_sticker_lego_v98 import ASSETS,REFERENCE_HASHES,_build_profile,_carrier,_face_groups


def _carriers(size="canonical"):
    return [_carrier(mesh,group) for mesh in build_geometry(size)["meshes"] for group in _face_groups(mesh)]


def test_exact_refs_tiers_and_geometry_hashes_are_bound():
    assert set(REFERENCE_HASHES)==set(build_geometry("canonical")["reference_evidence"])
    for size in SIZE_MATRIX:
        profile,package=_build_profile(size);graph=profile["massing_graph"]
        assert package["status"]=="pass" and not package["failures"]
        assert graph["exact_image_override"]["reference_sha256"]==REFERENCE_HASHES
        assert profile["production_contract"]["clay_lock"]["geometry_sha256"]==build_geometry(size)["geometry_sha256"]
        assert len(profile["production_contract"]["fixed_identity"]) >= 3
        assert profile["production_contract"]["repeatable_capacity"] == ["complete 6.25m blind gymnasium bays only"]
        assert profile["massing_graph"]["recipe_contract"] == {
            "footprint_projection_allowance_m": 1.2,
            "projection_owner": "fixed_entrance_canopy",
            "occupied_footprint_excludes_projection": True,
        }


def test_every_visible_face_has_one_and_only_one_carrier():
    for size in SIZE_MATRIX:
        geometry=build_geometry(size);profile,_=_build_profile(size);carriers=profile["massing_graph"]["assemblies"]
        expected={(m["name"],i) for m in geometry["meshes"] for i in range(len(m["faces"]))}
        actual=[(c["surface_id"],i) for c in carriers for i in c["face_indices"]]
        assert set(actual)==expected and len(actual)==len(set(actual))
        assert profile["massing_graph"]["surface_audit"]["status"]=="pass"
        assert all(c["final_surface_coverage"] and not c["sticker_layer"].startswith("generic") for c in carriers)


def test_semantic_floor_roles_are_complete_disjoint_and_correct():
    profile,_=_build_profile("canonical");carriers=profile["massing_graph"]["assemblies"]
    expected={"fixed_public_ground","fixed_double_height_hall","fixed_tall_hall","fixed_crown","low_roof","high_roof","roof_equipment"}
    assert set(profile["massing_graph"]["floor_sticker_contract"]["roles"])==expected
    assert {c["floor_role"] for c in carriers}==expected
    by_surface={}
    for c in carriers: by_surface.setdefault(c["surface_id"],set()).add(c["floor_role"])
    assert all(len(roles)==1 for roles in by_surface.values())
    assert all(c["floor_role"]=="fixed_double_height_hall" for c in carriers if "pool_glass" in c["surface_id"])
    assert all(c["floor_role"]=="fixed_public_ground" for c in carriers if "front_entrance" in c["surface_id"] or c["surface_id"].startswith("fixed_entrance_canopy"))


def test_brick_has_constant_metric_uv_across_sides_tiers_and_mechanical_well():
    all_brick=[]
    for size in SIZE_MATRIX: all_brick += [c for c in _carriers(size) if c["sticker_layer"] in {"warm_brick","mechanical_well_brick"}]
    assert {c["world_metric_uv_tile_m"] for c in all_brick}=={1.10}
    assert {(c["world_metric_uv_u_offset"],c["world_metric_uv_v_offset"]) for c in all_brick}=={(0.0,0.0)}
    assert {c["source_image_path"] for c in all_brick} <= {ASSETS["brick_front"],ASSETS["brick_return"],ASSETS["brick_parapet"]}


def test_glass_is_physical_and_pool_lobby_cards_are_separate_deterministic_atlases():
    first=_carriers();second=_carriers()
    glass=[c for c in first if c["material_role"]=="glass" and c["sticker_layer"]=="physical_clear_glass"]
    assert glass and all(c["source_image_path"]==ASSETS["glass"] and c["surface_alpha_override"]==.30 and c["transmission_override"]==.91 and c["roughness_override"]==.055 for c in glass)
    assert all(c["specular_ior_level_override"]==.54 and c["coat_weight_override"]==.30 and c["emission_strength_override"]==0.0 for c in glass)
    for layer,asset in (("pool_hall_interior_card",ASSETS["pool_interior"]),("community_lobby_interior_card",ASSETS["lobby_interior"])):
        selected=[c for c in first if c["sticker_layer"]==layer];repeated=[c for c in second if c["sticker_layer"]==layer]
        assert selected and all(c["source_image_path"]==asset and c["uv_u_max"]-c["uv_u_min"]==.25 and c["uv_v_max"]-c["uv_v_min"]==.5 for c in selected)
        assert [(c["surface_id"],c["atlas_cell_index"]) for c in selected]==[(c["surface_id"],c["atlas_cell_index"]) for c in repeated]
        assert {c["source_image_path"] for c in selected}.isdisjoint({c["source_image_path"] for c in glass})
        assert {c["emission_strength_override"] for c in selected}==({.085} if layer.startswith("community") else {.075})


def test_canopy_rooflights_ladder_and_mechanical_well_have_role_correct_assets():
    by_surface={c["surface_id"]:[] for c in _carriers()}
    for c in _carriers(): by_surface[c["surface_id"]].append(c)
    assert next(c for c in by_surface["fixed_entrance_canopy_top"] if c["face_indices"]==[1])["source_image_path"]==ASSETS["canopy_ribbed"]
    assert next(c for c in by_surface["fixed_entrance_canopy_top"] if c["face_indices"]!=[1])["source_image_path"]==ASSETS["canopy_smooth"]
    assert all(c["source_image_path"]==ASSETS["skylight_glass"] for name,cs in by_surface.items() if "rooflight" in name and "glass" in name for c in cs)
    assert all(c["source_image_path"]==ASSETS["skylight_curb"] for name,cs in by_surface.items() if "rooflight" in name and "curb" in name for c in cs)
    assert all(c["source_image_path"]==ASSETS["service"] for name,cs in by_surface.items() if name.startswith("gym_access_ladder") or name.startswith("mechanical_equipment") for c in cs)
    assert all(c["source_image_path"]==ASSETS["brick_parapet"] for name,cs in by_surface.items() if name.startswith("mechanical_well_") for c in cs)


def test_corrected_junction_and_glazed_entry_have_semantic_assets():
    by_surface={c["surface_id"]:c for c in _carriers()}
    for name in ("pool_gym_front_junction_pier","pool_gym_front_junction_beam","pool_gym_rear_junction_pier","pool_gym_rear_junction_beam"):
        assert by_surface[name]["source_image_path"]==ASSETS["concrete"] and by_surface[name]["floor_role"]=="fixed_crown"
    assert by_surface["exposed_inner_gym_stepped_brick_wall"]["source_image_path"]==ASSETS["brick_parapet"]
    assert by_surface["exposed_inner_gym_wall_pale_coping"]["source_image_path"]==ASSETS["concrete"]
    for door in range(2):
        assert by_surface[f"front_entrance_04_glazed_door_{door}_recessed_glass"]["source_image_path"]==ASSETS["glass"]
        assert by_surface[f"front_entrance_04_glazed_door_{door}_lobby_card"]["source_image_path"]==ASSETS["lobby_interior"]
        assert by_surface[f"front_entrance_04_glazed_door_{door}_left_stile"]["source_image_path"]==ASSETS["aluminum"]


def test_roof_upward_faces_use_low_high_assets_and_edges_use_patch():
    by_surface={}
    for c in _carriers(): by_surface.setdefault(c["surface_id"],[]).append(c)
    for surface,asset in (("low_wing_membrane_roof",ASSETS["low_roof"]),("high_gym_membrane_roof",ASSETS["high_roof"])):
        top=next(c for c in by_surface[surface] if c["face_indices"]==[1]);edges=next(c for c in by_surface[surface] if c["face_indices"]!=[1])
        assert top["source_image_path"]==asset and edges["source_image_path"]==ASSETS["coping"]
        assert top["floor_role"] in {"low_roof","high_roof"} and edges["floor_role"]==top["floor_role"]
    roof_assets={ASSETS["low_roof"],ASSETS["high_roof"],ASSETS["roof_patch"]}
    assert not any(c["source_image_path"] in roof_assets for c in _carriers() if c["floor_role"] not in {"low_roof","high_roof"})
    assert not any(c["source_image_path"] in roof_assets for c in _carriers() if c["face_indices"] != [1])


def test_all_explicit_terminal_caps_use_adjacent_finish_and_never_dark_assets():
    geometry=build_geometry("canonical");carriers=_carriers();by_surface={c["surface_id"]:c for c in carriers}
    concrete_caps=[m for m in geometry["meshes"] if m.get("carrier_kind")=="closed_parapet_corner_cap"]
    brick_caps=[m for m in geometry["meshes"] if m.get("carrier_kind")=="closed_mechanical_well_corner_cap"]
    assert len(concrete_caps)==len(brick_caps)==4
    assert all(by_surface[m["name"]]["source_image_path"]==ASSETS["coping"] for m in concrete_caps)
    assert all(by_surface[m["name"]]["source_image_path"]==ASSETS["brick_parapet"] for m in brick_caps)
    terminal_names={m["name"] for m in concrete_caps+brick_caps}
    forbidden={ASSETS["service"],ASSETS["grille"],ASSETS["aluminum"]}
    assert not any(c["source_image_path"] in forbidden for c in carriers if c["surface_id"] in terminal_names)


def test_split_concrete_grid_reveal_and_junction_parts_stay_pale():
    geometry=build_geometry("canonical");carriers=_carriers();by_surface={}
    for c in carriers: by_surface.setdefault(c["surface_id"],[]).append(c)
    kinds={"deep_opening_reveal","exposed_concrete_grid_pier","exposed_concrete_grid_beam",
           "localized_massing_junction_pier","localized_massing_junction_beam"}
    selected=[m for m in geometry["meshes"] if m.get("carrier_kind") in kinds]
    assert selected and all(m["material_domain"]=="pale_exposed_concrete" for m in selected)
    assert all(c["source_image_path"]==ASSETS["concrete"] for m in selected for c in by_surface[m["name"]])


def test_final_named_terminals_inherit_adjacent_semantic_finish():
    geometry=build_geometry("canonical");carriers=_carriers();by_surface={c["surface_id"]:c for c in carriers}
    concrete_kinds={"curtain_wall_exterior_terminal_cap","junction_beam_outward_terminal_cap"}
    coping_kinds={"roof_junction_endpoint_cap","roof_step_terminal_cap"}
    brick_kinds={"closed_roof_step_wedge"}
    concrete=[m for m in geometry["meshes"] if m.get("carrier_kind") in concrete_kinds]
    coping=[m for m in geometry["meshes"] if m.get("carrier_kind") in coping_kinds]
    brick=[m for m in geometry["meshes"] if m.get("carrier_kind") in brick_kinds]
    assert len(concrete)==10 and len(coping)==5 and len(brick)==1
    assert all(by_surface[m["name"]]["source_image_path"]==ASSETS["concrete"] for m in concrete)
    assert all(by_surface[m["name"]]["source_image_path"]==ASSETS["coping"] for m in coping)
    assert all(by_surface[m["name"]]["source_image_path"]==ASSETS["brick_parapet"] for m in brick)
    terminals={m["name"] for m in concrete+coping+brick}
    forbidden={ASSETS["service"],ASSETS["grille"],ASSETS["aluminum"]}
    assert not any(c["source_image_path"] in forbidden for c in carriers if c["surface_id"] in terminals)
