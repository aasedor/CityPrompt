from __future__ import annotations

import sys
from pathlib import Path


TOOL_DIR = Path(__file__).resolve().parents[1]
if str(TOOL_DIR) not in sys.path:
    sys.path.insert(0, str(TOOL_DIR))

from build_halifax_waterfront_warehouse_sticker_lego_v98 import SIZE_MATRIX, build_geometry
from compile_halifax_waterfront_warehouse_sticker_lego_v98 import ASSETS, REFERENCE_HASHES, _build_profile, _carrier


def _carriers(size_id: str):
    return [_carrier(mesh, list(range(len(mesh["faces"])))) for mesh in build_geometry(size_id)["meshes"]]


def test_exact_image_override_and_bounded_whole_bay_tiers_are_explicit() -> None:
    assert SIZE_MATRIX["canonical"] == {
        "width_m": 20.0, "depth_m": 15.0, "ordinary_front_bays": 6,
        "side_bays": 5, "storeys": 2,
    }
    assert SIZE_MATRIX["extended"] == {
        "width_m": 25.0, "depth_m": 15.0, "ordinary_front_bays": 8,
        "side_bays": 5, "storeys": 2,
    }
    profile, package = _build_profile("canonical")
    graph = profile["massing_graph"]
    assert package["status"] == "pass" and not package["failures"]
    assert graph["exact_image_override"]["required"] is True
    assert graph["exact_image_override"]["reference_sha256"] == REFERENCE_HASHES
    assert profile["production_contract"]["identity_mode"] == "massing_graph"
    assert profile["production_contract"]["identity_authority"] == "exact_image_locked_semantic_stack"
    assert profile["production_contract"]["lego_scalability"]["whole_modules_only"] is True


def test_every_visible_face_has_exactly_one_final_carrier() -> None:
    for size_id in SIZE_MATRIX:
        geometry = build_geometry(size_id)
        profile, package = _build_profile(size_id)
        carriers = profile["massing_graph"]["assemblies"]
        expected = {(mesh["name"], index) for mesh in geometry["meshes"] for index in range(len(mesh["faces"]))}
        actual = [(carrier["surface_id"], index) for carrier in carriers for index in carrier["face_indices"]]
        assert set(actual) == expected
        assert len(actual) == len(set(actual))
        assert all(carrier["final_surface_coverage"] for carrier in carriers)
        assert profile["massing_graph"]["surface_audit"]["status"] == "pass"
        assert package["carrier_count"] == len(geometry["meshes"])


def test_floor_roles_are_disjoint_and_roof_begins_above_occupied_top() -> None:
    profile, _package = _build_profile("canonical")
    graph = profile["massing_graph"]
    carriers = graph["assemblies"]
    assert graph["floor_sticker_contract"]["roles"] == ["ground", "top", "fixed_crown", "roof"]
    assert graph["floor_sticker_contract"]["roof_starts_at_z_m"] == 9.7
    assert {carrier["floor_role"] for carrier in carriers} == {"ground", "top", "fixed_crown", "roof"}
    by_surface = {}
    for carrier in carriers:
        by_surface.setdefault(carrier["surface_id"], set()).add(carrier["floor_role"])
    assert all(len(roles) == 1 for roles in by_surface.values())
    assert all(carrier["floor_role"] == "roof" for carrier in carriers if carrier["sticker_layer"] in {
        "weathered_flat_membrane_roof", "warm_brick_roof_parapet", "patinated_roof_coping",
        "chimney_brick", "chimney_coping", "aged_galvanized_roof_service",
    })
    assert all(carrier["floor_role"] == "fixed_crown" for carrier in carriers if carrier["sticker_layer"] == "patinated_cornice")
    assert all(carrier["floor_role"] == "fixed_crown" for carrier in carriers if carrier["sticker_layer"] == "patinated_stepped_coping")


def test_material_domains_map_to_role_correct_registered_assets() -> None:
    carriers = _carriers("canonical")
    assert all(carrier["source_image_path"] == ASSETS["plinth"] for carrier in carriers
               if carrier["sticker_layer"] == "weathered_stone_plinth")
    assert all(carrier["source_image_path"] == ASSETS["joinery"] for carrier in carriers
               if carrier["sticker_layer"] == "physical_dark_green_joinery")
    assert all(carrier["source_image_path"] == ASSETS["cornice"] for carrier in carriers
               if carrier["sticker_layer"] in {"patinated_cornice", "patinated_stepped_coping", "patinated_roof_coping", "patinated_roof_coping_corner"})
    assert all(carrier["source_image_path"] == ASSETS["chimney_brick"] for carrier in carriers
               if carrier["sticker_layer"] == "chimney_brick")
    assert all(carrier["source_image_path"] == ASSETS["chimney_coping"] for carrier in carriers
               if carrier["sticker_layer"] == "chimney_coping")
    assert not any(carrier["sticker_layer"].startswith("generic") for carrier in carriers)


def test_front_and_return_brick_share_metric_scale_and_phase() -> None:
    carriers = [carrier for carrier in _carriers("canonical") if carrier["sticker_layer"] == "warm_brick_masonry"]
    front = [carrier for carrier in carriers if carrier["source_image_path"] == ASSETS["brick_front"]]
    returns = [carrier for carrier in carriers if carrier["source_image_path"] == ASSETS["brick_return"]]
    assert front and returns
    metric = lambda item: (item["world_metric_uv_tile_m"], item["world_metric_uv_u_offset"], item["world_metric_uv_v_offset"])
    assert {metric(carrier) for carrier in front + returns} == {(1.20, 0.0, 0.0)}


def test_stone_keeps_one_metric_scale_across_piers_belts_arches_and_returns() -> None:
    stone_layers = {
        "pale_stone_rustication", "deep_pale_stone_reveal", "pale_stone_trim",
        "weathered_stone_plinth", "chimney_coping",
    }
    stone = [item for item in _carriers("canonical") if item["sticker_layer"] in stone_layers]
    assert stone
    metric = lambda item: (
        item["world_metric_uv_tile_m"], item["world_metric_uv_u_offset"],
        item["world_metric_uv_v_offset"], item["roughness_override"],
    )
    assert {metric(item) for item in stone} == {(1.65, 0.0, 0.0, .74)}


def test_ground_and_upper_glass_are_physical_and_do_not_print_frames() -> None:
    carriers = _carriers("canonical")
    ground = [item for item in carriers if item["sticker_layer"] == "physical_clear_storefront_glass"]
    upper = [item for item in carriers if item["sticker_layer"] == "physical_clear_upper_glass"]
    ground_frames = [item for item in carriers if item["sticker_layer"] == "physical_dark_green_ground_joinery"]
    upper_frames = [item for item in carriers if item["sticker_layer"] == "physical_dark_green_upper_joinery"]
    frames = ground_frames + upper_frames
    assert len(ground) == len(upper) == 24 and len(ground_frames) == 217 and len(upper_frames) == 72
    assert all(item["source_image_path"] == ASSETS["storefront_glass"] and item["material_role"] == "glass" for item in ground)
    assert all(item["source_image_path"] == ASSETS["upper_glass"] and item["material_role"] == "glass" for item in upper)
    assert all(item["transparency_mode"] == "BLENDED" and item["transmission_override"] > .75
               and item["roughness_override"] < .16 for item in ground + upper)
    assert all(item["glass_profile"] == "reflective_curtain_wall" for item in ground + upper)
    assert all(item["surface_alpha_override"] >= .68 and item["specular_ior_level_override"] >= .68
               and item["coat_weight_override"] >= .52 and item["emission_strength_override"] == .002
               for item in ground + upper)
    assert all(item["source_image_path"] == ASSETS["joinery"] and item["material_role"] == "elevation" for item in frames)
    assert {item["source_image_path"] for item in ground}.isdisjoint({item["source_image_path"] for item in frames})


def test_corrected_crown_arch_storefront_and_two_chimneys_have_semantic_stickers() -> None:
    carriers = _carriers("canonical")
    by_surface = {item["surface_id"]: item for item in carriers}
    assert by_surface["front_stepped_parapet_brick_infill"]["sticker_layer"] == "warm_brick_masonry"
    assert by_surface["front_stepped_parapet_left_stone_upright"]["sticker_layer"] == "pale_stone_trim"
    assert by_surface["front_stepped_parapet_layered_coping_1"]["sticker_layer"] == "patinated_stepped_coping"
    assert by_surface["front_upper_arch_00_outer_archivolt_00"]["sticker_layer"] == "pale_stone_trim"
    assert by_surface["front_upper_arch_00_left_impost_block"]["sticker_layer"] == "pale_stone_trim"
    assert by_surface["front_upper_arch_00_keystone_crest"]["sticker_layer"] == "pale_stone_trim"
    assert by_surface["front_ground_entrance_03_left_door_leaf"]["sticker_layer"] == "physical_dark_green_ground_joinery"
    assert by_surface["front_ground_storefront_00_stall_riser"]["sticker_layer"] == "physical_dark_green_ground_joinery"
    assert {by_surface[f"rear_brick_chimney_{index}_shaft"]["sticker_layer"] for index in range(2)} == {"chimney_brick"}
    assert {by_surface[f"rear_brick_chimney_{index}_independent_cap"]["sticker_layer"] for index in range(2)} == {"chimney_coping"}


def test_ground_and_upper_interiors_use_separate_deterministic_4_by_2_atlases() -> None:
    first = _carriers("canonical")
    second = _carriers("canonical")
    for layer, asset in (("ground_retail_interior_card", ASSETS["ground_interior"]),
                         ("upper_commercial_interior_card", ASSETS["upper_interior"])):
        selected = [item for item in first if item["sticker_layer"] == layer]
        repeated = [item for item in second if item["sticker_layer"] == layer]
        assert len(selected) == 24
        assert all(item["source_image_path"] == asset for item in selected)
        assert {item["atlas_cell_index"] for item in selected} == set(range(8))
        assert all(item["uv_u_max"] - item["uv_u_min"] == .25 for item in selected)
        assert all(item["uv_v_max"] - item["uv_v_min"] == .5 for item in selected)
        expected_emission = .008 if layer == "ground_retail_interior_card" else .006
        assert all(item["emission_strength_override"] == expected_emission for item in selected)
        assert [(item["surface_id"], item["atlas_cell_index"]) for item in selected] == [
            (item["surface_id"], item["atlas_cell_index"]) for item in repeated
        ]


def test_roof_deck_perimeter_chimney_and_services_never_share_the_roof_texture() -> None:
    carriers = _carriers("canonical")
    roof = [item for item in carriers if item["source_image_path"] == ASSETS["roof"]]
    assert len(roof) == 1
    assert roof[0]["surface_id"] == "flat_membrane_roof"
    expected = {
        "patinated_roof_coping": ASSETS["cornice"],
        "patinated_roof_coping_corner": ASSETS["cornice"],
        "chimney_brick": ASSETS["chimney_brick"],
        "chimney_coping": ASSETS["chimney_coping"],
        "aged_galvanized_roof_service": ASSETS["service_metal"],
    }
    for layer, asset in expected.items():
        selected = [item for item in carriers if item["sticker_layer"] == layer]
        assert selected and all(item["source_image_path"] == asset for item in selected)
        assert all(item["source_image_path"] != ASSETS["roof"] for item in selected)
    parapets = [item for item in carriers if item["sticker_layer"] == "warm_brick_roof_parapet"]
    assert len(parapets) == 4
    assert {item["source_image_path"] for item in parapets} == {ASSETS["brick_front"], ASSETS["brick_return"]}
    assert next(item for item in parapets if item["surface_id"] == "front_roof_parapet")["source_image_path"] == ASSETS["brick_front"]
    assert all(item["source_image_path"] == ASSETS["brick_return"] for item in parapets
               if item["surface_id"] != "front_roof_parapet")


def test_all_vertical_roof_parapets_are_warm_brick_and_membrane_is_deck_only() -> None:
    carriers = _carriers("canonical")
    parapets = [item for item in carriers if "roof_parapet" in item["surface_id"]]
    assert len(parapets) == 4
    assert all(item["sticker_layer"] == "warm_brick_roof_parapet" for item in parapets)
    assert all(item["source_image_path"] in {ASSETS["brick_front"], ASSETS["brick_return"]} for item in parapets)
    assert not any(item["source_image_path"] == ASSETS["roof_perimeter"] for item in carriers)


def test_both_chimneys_share_registered_shaft_and_cap_assets() -> None:
    by_surface = {item["surface_id"]: item for item in _carriers("canonical")}
    shafts = [by_surface[f"rear_brick_chimney_{index}_shaft"] for index in range(2)]
    caps = [by_surface[f"rear_brick_chimney_{index}_independent_cap"] for index in range(2)]
    assert {item["source_image_path"] for item in shafts} == {ASSETS["chimney_brick"]}
    assert {item["source_image_path"] for item in caps} == {ASSETS["chimney_coping"]}


def test_new_explicit_coping_corner_domain_routes_to_patina() -> None:
    mesh = {"name": "front_left_explicit_coping_corner", "material_domain": "patinated_coping_corner",
            "vertices": [[0, 0, 9.7], [1, 0, 9.7], [1, 1, 9.7], [0, 1, 9.7],
                         [0, 0, 10], [1, 0, 10], [1, 1, 10], [0, 1, 10]],
            "faces": [[0, 1, 2, 3]], "face_roles": ["patinated_coping_corner"]}
    carrier = _carrier(mesh, [0])
    assert carrier["source_image_path"] == ASSETS["cornice"]
    assert carrier["sticker_layer"] == "patinated_roof_coping_corner"
