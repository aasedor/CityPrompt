from __future__ import annotations

from collections import Counter
import math

from build_old_montreal_textile_sticker_lego_v98 import BAY_M, FLOOR_BANDS, SIZE_MATRIX, build_geometry


def test_exact_images_lock_three_storeys_and_two_bounded_widths() -> None:
    assert set(SIZE_MATRIX) == {"canonical", "extended"}
    canonical = build_geometry("canonical")
    extended = build_geometry("extended")
    assert canonical["dimensions"] == {"width_m": 25.0, "depth_m": 20.0, "occupied_storeys": 3, "wall_top_m": 12.9, "parapet_top_m": 13.92}
    assert extended["dimensions"]["width_m"] == 35.0
    assert extended["dimensions"]["depth_m"] == 20.0
    assert extended["dimensions"]["occupied_storeys"] == 3
    assert canonical["reference_authority"] == "exact_three_view_images_override_conflicting_4_to_6_floor_metadata"
    assert [band["role"] for band in canonical["floor_bands"]] == ["ground", "middle", "top"]
    assert canonical["floor_bands"] == [dict(band) for band in FLOOR_BANDS]


def test_expansion_is_exactly_two_whole_horizontal_bays() -> None:
    canonical = build_geometry("canonical")
    extended = build_geometry("extended")
    assert canonical["structural_grid"]["bay_width_m"] == extended["structural_grid"]["bay_width_m"] == BAY_M
    assert canonical["structural_grid"]["front_bays"] == 5
    assert extended["structural_grid"]["front_bays"] == 7
    assert canonical["structural_grid"]["side_bays"] == extended["structural_grid"]["side_bays"] == 4
    assert extended["dimensions"]["width_m"] - canonical["dimensions"]["width_m"] == 2 * BAY_M
    assert extended["repeatable_middle_front_bays"] - canonical["repeatable_middle_front_bays"] == 2
    assert canonical["structural_grid"]["horizontal_whole_bay_expansion_only"] is True
    assert canonical["structural_grid"]["vertical_scaling"] == "forbidden"


def test_front_side_and_rear_have_true_recessed_openings() -> None:
    for size_id in SIZE_MATRIX:
        geometry = build_geometry(size_id)
        by_side = Counter(item["side"] for item in geometry["apertures"])
        assert by_side == {
            "front": geometry["structural_grid"]["front_bays"] * 3,
            "rear": geometry["structural_grid"]["front_bays"] * 3,
            "left": 4 * 3,
            "right": 4 * 3,
        }
        assert {item["side"] for item in geometry["apertures"] if item["kind"] == "door"} == {"front", "left", "rear"}
        assert all(item["flat_printed_void"] is False and item["recess_depth_m"] >= 0.34 for item in geometry["apertures"])
        assert all(item["return_meshes"] and item["recessed_back_mesh"] for item in geometry["apertures"])
        assert all(item["shape"] == "segmental_arch" for item in geometry["apertures"] if item["band_role"] == "middle")
        names = {mesh["name"] for mesh in geometry["meshes"]}
        assert all(item["recessed_back_mesh"] in names and set(item["return_meshes"]) <= names for item in geometry["apertures"])


def test_locked_architecture_includes_piers_belts_flat_roof_and_bounded_services() -> None:
    for size_id in SIZE_MATRIX:
        geometry = build_geometry(size_id)
        names = {mesh["name"] for mesh in geometry["meshes"]}
        assert len([name for name in names if name.startswith("fixed_corner_pier_")]) == 4
        for role in ("stone_base", "ground_belt", "middle_belt", "cornice", "coping"):
            assert {f"{role}_{side}" for side in ("front", "rear", "left", "right")} <= names
        assert {"fixed_flat_roof_deck", "fixed_parapet_front", "fixed_parapet_rear", "fixed_parapet_left", "fixed_parapet_right"} <= names
        assert {"fixed_long_monitor_front_curb", "fixed_long_monitor_rear_curb", "fixed_small_pyramidal_skylight_glass", "fixed_hvac_unit_0", "fixed_hvac_unit_1"} <= names
        assert geometry["fixed_modules"] == {"ground_band": 1, "middle_band": 1, "top_band": 1, "corner_piers": 4, "principal_corner_stack": 1, "wraparound_top_terrace": 1, "long_roof_monitors": 2, "pyramidal_skylights": 1, "service_clusters": 1, "rear_right_service_volumes": 1, "hvac_units": 2, "far_end_entrances": 1}
        assert len([name for name in names if name.startswith("fixed_hvac_unit_")]) == 2


def test_each_visible_locked_face_has_exactly_one_sticker_owner() -> None:
    for size_id in SIZE_MATRIX:
        geometry = build_geometry(size_id)
        bundle = geometry["locked_mesh_bundle"]
        assert bundle["kind"] == "locked_mesh_bundle"
        assert bundle["generic_primitive_assemblies"] == []
        assert bundle["mesh_names"] == [mesh["name"] for mesh in geometry["meshes"]]
        assert len(bundle["mesh_names"]) == len(set(bundle["mesh_names"]))
        schedule = {item["mesh_name"]: item for item in geometry["surface_ownership"]}
        assert set(schedule) == set(bundle["mesh_names"])
        for mesh in geometry["meshes"]:
            assert len(mesh["face_owners"]) == len(mesh["faces"])
            assert len(mesh["face_roles"]) == len(mesh["faces"])
            assert all(len(owners) == 1 and owners[0] == mesh["sticker_owner_id"] for owners in mesh["face_owners"])
            assert schedule[mesh["name"]]["face_indices"] == list(range(len(mesh["faces"])))
            assert schedule[mesh["name"]]["fallback_material_forbidden"] is True


def test_skylight_faces_separate_metal_and_physical_glass_roles() -> None:
    for size_id in SIZE_MATRIX:
        geometry = build_geometry(size_id)
        glass = [mesh for mesh in geometry["meshes"] if mesh["material_domain"] == "roof_monitor_glass"]
        metal = [mesh for mesh in geometry["meshes"] if mesh["material_domain"] == "roof_monitor_metal"]
        assert len(glass) == 9  # four surfaces per long monitor plus pyramid
        assert len(metal) >= 10
        assert all(set(mesh["face_roles"]) == {"skylight_glass"} for mesh in glass)
        names = {mesh["name"] for mesh in geometry["meshes"]}
        for monitor in ("fixed_long_monitor_front", "fixed_long_monitor_rear"):
            assert {f"{monitor}_curb", f"{monitor}_ridge", f"{monitor}_front_glass_plane", f"{monitor}_rear_glass_plane", f"{monitor}_left_hip_end", f"{monitor}_right_hip_end"} <= names
            assert len([name for name in names if name.startswith(f"{monitor}_front_rib_")]) >= 4


def test_roof_owners_never_own_occupied_vertical_faces() -> None:
    for size_id in SIZE_MATRIX:
        geometry = build_geometry(size_id)
        for mesh in geometry["meshes"]:
            if mesh["material_domain"] == "occupied_wall":
                assert not mesh["sticker_owner_id"].startswith("sticker_roof")
                assert mesh["band_role"] in {"ground", "middle", "top"}
            if mesh["material_domain"] in {"main_roof", "roof_parapet", "roof_monitor_glass", "roof_monitor_metal", "roof_access", "roof_service"}:
                assert all(vertex[2] >= 13.12 for vertex in mesh["vertices"])


def test_architect_blockers_are_explicit_identity_geometry() -> None:
    for size_id in SIZE_MATRIX:
        geometry = build_geometry(size_id)
        names = {mesh["name"] for mesh in geometry["meshes"]}
        assert {"fixed_principal_corner_narrow_pier", "fixed_principal_corner_capital", "fixed_principal_corner_corbel", "fixed_principal_corner_upper_brick_return", "fixed_top_terrace_front_slab", "fixed_top_terrace_right_slab", "fixed_top_terrace_front_rail", "fixed_top_terrace_right_rail"} <= names
        assert {"fixed_service_curb_mass", "fixed_service_plenum", "fixed_service_vent_0", "fixed_service_vent_1", "fixed_service_pipe_0"} <= names
        assert {"fixed_far_end_entrance_canopy", "fixed_far_end_canopy_support_0", "fixed_far_end_canopy_support_1"} <= names
        assert geometry["elevation_end_conditions"] == {"front": "far_left_public_entrance_and_glazed_principal_right_corner", "right": "glazed_principal_corner_no_ground_door", "rear": "offset_service_door_near_far_end", "left": "far_rear_service_door"}
        assert not any(item["kind"] == "door" and item["side"] == "right" and item["bay"] == 0 for item in geometry["apertures"])
        middle = [item for item in geometry["apertures"] if item["band_role"] == "middle"]
        assert all(max(point[1] for point in item["contour_uz_m"]) - item["contour_uz_m"][2][1] <= 0.63 for item in middle)
        assert all(item["recess_depth_m"] == 0.56 for item in middle)


def test_revision_two_corner_projection_and_terrace_location_are_measurable() -> None:
    for size_id in SIZE_MATRIX:
        geometry = build_geometry(size_id)
        meshes = {mesh["name"]: mesh for mesh in geometry["meshes"]}
        width = geometry["dimensions"]["width_m"]
        depth = geometry["dimensions"]["depth_m"]
        stack_front = meshes["fixed_principal_corner_narrow_pier"]
        stack_right = stack_front
        generic_corner = meshes["fixed_corner_pier_front_right"]
        assert min(vertex[1] for vertex in stack_front["vertices"]) <= -depth / 2 - 0.5
        assert max(vertex[0] for vertex in stack_right["vertices"]) >= width / 2 + 0.5
        assert min(vertex[1] for vertex in stack_front["vertices"]) < min(vertex[1] for vertex in generic_corner["vertices"]) - 0.4
        assert max(vertex[2] for vertex in stack_front["vertices"]) >= 8.8
        capital = meshes["fixed_principal_corner_capital"]
        assert max(vertex[0] for vertex in capital["vertices"]) >= width / 2 + 0.65
        front_slab = meshes["fixed_top_terrace_front_slab"]
        right_slab = meshes["fixed_top_terrace_right_slab"]
        assert min(vertex[2] for vertex in front_slab["vertices"]) < 9.0 < max(vertex[2] for vertex in front_slab["vertices"])
        assert min(vertex[0] for vertex in front_slab["vertices"]) <= width / 2 - 10.0
        assert max(vertex[1] for vertex in right_slab["vertices"]) >= -depth / 2 + 7.5
        assert meshes["fixed_top_terrace_front_rail"]["rail_on_outer_slab_edge"] is True
        assert meshes["fixed_top_terrace_right_rail"]["rail_on_outer_slab_edge"] is True


def test_revision_two_monitors_have_high_pitch_continuous_glazing_and_hipped_ends() -> None:
    for size_id in SIZE_MATRIX:
        geometry = build_geometry(size_id)
        meshes = {mesh["name"]: mesh for mesh in geometry["meshes"]}
        for monitor in ("fixed_long_monitor_front", "fixed_long_monitor_rear"):
            curb = meshes[f"{monitor}_curb"]
            front = meshes[f"{monitor}_front_glass_plane"]
            rear = meshes[f"{monitor}_rear_glass_plane"]
            assert curb["curb_height_m"] >= 0.6
            assert front["continuous_slope"] is rear["continuous_slope"] is True
            assert front["pitch_rise_m"] >= 1.5
            assert len(front["faces"]) == len(rear["faces"]) == 1
            assert meshes[f"{monitor}_left_hip_end"]["material_domain"] == "roof_monitor_glass"
            assert meshes[f"{monitor}_right_hip_end"]["material_domain"] == "roof_monitor_glass"
            assert len([name for name in meshes if name.startswith(f"{monitor}_front_rib_")]) >= 4


def test_revision_two_rear_right_service_step_changes_footprint_and_roof_outline() -> None:
    for size_id in SIZE_MATRIX:
        geometry = build_geometry(size_id)
        meshes = {mesh["name"]: mesh for mesh in geometry["meshes"]}
        depth = geometry["dimensions"]["depth_m"]
        volume = meshes["fixed_rear_right_service_volume"]
        roof = meshes["fixed_rear_right_service_roof"]
        assert max(vertex[1] for vertex in volume["vertices"]) >= depth / 2 + 1.6
        assert max(vertex[2] for vertex in volume["vertices"]) >= 7.5
        assert roof["roof_outline_step"] is True
        assert all(len(owners) == 1 for mesh in (volume, roof) for owners in mesh["face_owners"])


def test_revision_two_elevations_have_different_terminal_and_landmark_openings() -> None:
    for size_id in SIZE_MATRIX:
        geometry = build_geometry(size_id)
        front_bays = geometry["structural_grid"]["front_bays"]
        landmark_front = next(item for item in geometry["apertures"] if item["side"] == "front" and item["bay"] == front_bays - 1 and item["band_role"] == "ground")
        landmark_right = next(item for item in geometry["apertures"] if item["side"] == "right" and item["bay"] == 0 and item["band_role"] == "ground")
        right_terminal = next(item for item in geometry["apertures"] if item["side"] == "right" and item["bay"] == 3 and item["band_role"] == "ground")
        front_entry = next(item for item in geometry["apertures"] if item["side"] == "front" and item["bay"] == 0 and item["band_role"] == "ground")
        def contour_width(item):
            return max(point[0] for point in item["contour_uz_m"]) - min(point[0] for point in item["contour_uz_m"])
        assert landmark_front["opening_profile"] == landmark_right["opening_profile"] == "landmark_corner_storefront"
        assert contour_width(landmark_front) > 4.0
        assert contour_width(landmark_right) > contour_width(right_terminal) * 2
        assert front_entry["kind"] == "door" and front_entry["opening_profile"] == "ordinary"
        assert right_terminal["opening_profile"] == "right_terminal_narrow"


def test_revision_two_middle_arches_have_projecting_surrounds_and_deep_aprons() -> None:
    for size_id in SIZE_MATRIX:
        geometry = build_geometry(size_id)
        middle_count = sum(item["band_role"] == "middle" for item in geometry["apertures"])
        names = {mesh["name"] for mesh in geometry["meshes"]}
        assert len([name for name in names if name.endswith("_surround_left")]) == middle_count
        assert len([name for name in names if name.endswith("_surround_right")]) == middle_count
        assert len([name for name in names if name.endswith("_deep_spandrel_frame")]) == middle_count
        aprons = [mesh for mesh in geometry["meshes"] if mesh["name"].endswith("_projecting_sill_apron") and mesh.get("band_role") == "middle"]
        assert len(aprons) == middle_count
        assert all(min(vertex[0] for vertex in apron["vertices"]) < max(vertex[0] for vertex in apron["vertices"]) for apron in aprons)


def test_revision_four_aprons_are_role_specific_and_arch_heads_are_physical() -> None:
    for size_id in SIZE_MATRIX:
        geometry = build_geometry(size_id)
        middle_count = sum(item["band_role"] == "middle" for item in geometry["apertures"])
        aprons = [mesh for mesh in geometry["meshes"] if mesh["name"].endswith("_projecting_sill_apron")]
        assert {mesh["apron_profile"] for mesh in aprons} == {"deep_framed_middle", "slender_cut_stone_sill"}
        assert all(
            max(vertex[2] for vertex in mesh["vertices"]) - min(vertex[2] for vertex in mesh["vertices"]) <= 0.68
            for mesh in aprons
        )
        curved = [mesh for mesh in geometry["meshes"] if "_surround_arch_" in mesh["name"]]
        assert len(curved) == middle_count * 13
        assert all(mesh["projecting_curved_head"] is True and mesh["material_domain"] == "stone_surround" for mesh in curved)


def test_revision_three_corner_is_narrow_with_capital_and_upper_brick_return() -> None:
    for size_id in SIZE_MATRIX:
        geometry = build_geometry(size_id)
        meshes = {mesh["name"]: mesh for mesh in geometry["meshes"]}
        width = geometry["dimensions"]["width_m"]
        depth = geometry["dimensions"]["depth_m"]
        pier = meshes["fixed_principal_corner_narrow_pier"]
        capital = meshes["fixed_principal_corner_capital"]
        corbel = meshes["fixed_principal_corner_corbel"]
        upper = meshes["fixed_principal_corner_upper_brick_return"]
        assert pier["pier_width_m"] <= 1.2
        assert max(v[0] for v in pier["vertices"]) - min(v[0] for v in pier["vertices"]) <= 1.2
        assert max(v[1] for v in pier["vertices"]) - min(v[1] for v in pier["vertices"]) <= 1.2
        assert 1.4 <= max(v[0] for v in capital["vertices"]) - min(v[0] for v in capital["vertices"]) <= 1.6
        assert min(v[2] for v in capital["vertices"]) <= 8.72 and max(v[2] for v in capital["vertices"]) >= 9.10
        assert min(v[2] for v in corbel["vertices"]) >= 8.5
        assert min(v[2] for v in upper["vertices"]) >= 9.2 and max(v[2] for v in upper["vertices"]) >= 13.2
        assert min(v[1] for v in pier["vertices"]) <= -depth / 2 - 0.5
        assert max(v[0] for v in pier["vertices"]) >= width / 2 + 0.5


def test_revision_three_monitor_ribs_follow_slope_without_transverse_fins() -> None:
    for size_id in SIZE_MATRIX:
        geometry = build_geometry(size_id)
        meshes = {mesh["name"]: mesh for mesh in geometry["meshes"]}
        for monitor in ("fixed_long_monitor_front", "fixed_long_monitor_rear"):
            for side in ("front", "rear"):
                ribs = [mesh for name, mesh in meshes.items() if name.startswith(f"{monitor}_{side}_rib_")]
                assert len(ribs) >= 4
                for rib in ribs:
                    assert len(rib["faces"]) == 1
                    assert rib["rib_width_m"] <= 0.05
                    assert rib["slope_offset_m"] <= 0.02
                    assert rib["face_roles"] == ["slope_following_fine_rib"]
                    assert len({round(v[0], 3) for v in rib["vertices"]}) == 2


def test_revision_three_service_step_is_shallow_low_and_articulated() -> None:
    for size_id in SIZE_MATRIX:
        geometry = build_geometry(size_id)
        meshes = {mesh["name"]: mesh for mesh in geometry["meshes"]}
        depth = geometry["dimensions"]["depth_m"]
        volume = meshes["fixed_rear_right_service_volume"]
        assert volume["projection_depth_m"] <= 1.7
        assert max(v[1] for v in volume["vertices"]) <= depth / 2 + 1.7
        assert max(v[2] for v in volume["vertices"]) <= 7.7
        panels = [mesh for name, mesh in meshes.items() if name.startswith("fixed_rear_right_service_panel_")]
        assert len(panels) == 6
        assert all(mesh["material_domain"] == "service_panel_recess" for mesh in panels)


def test_every_window_has_physical_glass_interior_card_and_steel_mullions() -> None:
    for size_id in SIZE_MATRIX:
        geometry = build_geometry(size_id)
        meshes = {mesh["name"]: mesh for mesh in geometry["meshes"]}
        windows = [item for item in geometry["apertures"] if item["kind"] == "window"]
        assert windows
        for window in windows:
            assert window["physical_glass_mesh"] == window["recessed_back_mesh"]
            assert meshes[window["physical_glass_mesh"]]["material_domain"] == "recessed_glazing"
            assert meshes[window["interior_card_mesh"]]["material_domain"] == "interior_card"
            assert 0.22 <= meshes[window["interior_card_mesh"]]["behind_glass_m"] <= 0.35
            assert len(window["window_mullion_meshes"]) >= 3
            for name in window["window_mullion_meshes"]:
                mullion = meshes[name]
                assert mullion["material_domain"] == "window_mullion"
                assert mullion["face_roles"] == ["near_black_steel_sash"]
                assert mullion["contour_confined"] is True
                assert mullion["in_front_of_glass_m"] > 0
                assert all(len(owners) == 1 for owners in mullion["face_owners"])


def test_rectangular_windows_have_proportionate_vertical_and_horizontal_sashes() -> None:
    for size_id in SIZE_MATRIX:
        geometry = build_geometry(size_id)
        for window in (item for item in geometry["apertures"] if item["kind"] == "window" and item["shape"] == "rectangular"):
            verticals = [name for name in window["window_mullion_meshes"] if "_vertical_" in name]
            horizontals = [name for name in window["window_mullion_meshes"] if "_horizontal_" in name]
            assert len(verticals) == (3 if window["band_role"] == "ground" else 2)
            assert len(horizontals) == (2 if window["band_role"] == "ground" else 1)


def test_segmental_window_sashes_are_confined_inside_arch_contour() -> None:
    for size_id in SIZE_MATRIX:
        geometry = build_geometry(size_id)
        meshes = {mesh["name"]: mesh for mesh in geometry["meshes"]}
        for window in (item for item in geometry["apertures"] if item["kind"] == "window" and item["shape"] == "segmental_arch"):
            contour = window["contour_uz_m"]
            u0, u1 = min(p[0] for p in contour), max(p[0] for p in contour)
            z0, z1 = min(p[1] for p in contour), max(p[1] for p in contour)
            for name in window["window_mullion_meshes"]:
                mesh = meshes[name]
                # Convert world vertices back to the side's aperture UZ plane.
                for vertex in mesh["vertices"]:
                    if window["side"] in {"front", "rear"}:
                        u, z = (vertex[0] if window["side"] == "front" else -vertex[0]), vertex[2]
                    else:
                        u, z = (vertex[1] if window["side"] == "right" else -vertex[1]), vertex[2]
                    assert u0 <= u <= u1 and z0 <= z <= z1


def test_doors_keep_recessed_tunnel_and_receive_no_window_assembly() -> None:
    for size_id in SIZE_MATRIX:
        geometry = build_geometry(size_id)
        meshes = {mesh["name"]: mesh for mesh in geometry["meshes"]}
        for door in (item for item in geometry["apertures"] if item["kind"] == "door"):
            assert door["door_tunnel_retained"] is True
            assert door["physical_glass_mesh"] is None
            assert door["interior_card_mesh"] is None
            assert door["window_mullion_meshes"] == []
            assert door["recess_depth_m"] == 1.25
            assert meshes[door["recessed_back_mesh"]]["material_domain"] == "recessed_door"
            assert door["return_meshes"]


def test_fixed_end_modules_keep_local_geometry_across_widths() -> None:
    canonical = build_geometry("canonical")
    extended = build_geometry("extended")
    for side in ("front", "rear"):
        for band_role in ("ground", "middle", "top"):
            for bay_role in ("fixed_left_end", "fixed_right_end"):
                first = next(item for item in canonical["apertures"] if item["side"] == side and item["band_role"] == band_role and item["bay_role"] == bay_role)
                second = next(item for item in extended["apertures"] if item["side"] == side and item["band_role"] == band_role and item["bay_role"] == bay_role)
                assert first["kind"] == second["kind"]
                assert first["shape"] == second["shape"]
                assert first["recess_depth_m"] == second["recess_depth_m"]
                first_width = max(point[0] for point in first["contour_uz_m"]) - min(point[0] for point in first["contour_uz_m"])
                second_width = max(point[0] for point in second["contour_uz_m"]) - min(point[0] for point in second["contour_uz_m"])
                assert math.isclose(first_width, second_width)


def test_geometry_hashes_are_deterministic_and_size_specific() -> None:
    canonical = build_geometry("canonical")
    extended = build_geometry("extended")
    assert build_geometry("canonical")["geometry_sha256"] == canonical["geometry_sha256"]
    assert build_geometry("extended")["geometry_sha256"] == extended["geometry_sha256"]
    assert canonical["geometry_sha256"] != extended["geometry_sha256"]
    assert len(canonical["geometry_sha256"]) == 64
