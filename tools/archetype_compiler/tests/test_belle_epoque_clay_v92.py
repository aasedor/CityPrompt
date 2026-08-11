import json
import math
from pathlib import Path

from build_belle_epoque_clay_v92 import (
    SCHEMA,
    audit,
    audit_visible_face_materials,
    build_geometry,
    build_lock,
    entrance_clear_fraction,
    evidence_contract,
    final_surface_classification,
    final_surface_coverage_audit,
    mesh_bad_edges,
    roof_topology_audit,
    sha256,
    storey_band_contract,
    storey_band_contract_audit,
    surface_contract,
)


def test_clay_lock_is_artifact_derived_and_sticker_agent_compatible(tmp_path: Path):
    lock = build_lock(tmp_path)
    report = json.loads((tmp_path / "belle_epoque_clay_v92_gate_report.json").read_text())
    assert lock["schema"] == SCHEMA
    assert lock["building_id"] == "grand-magasin-belle-epoque"
    assert lock["status"] == "approved"
    assert report["status"] == "pass"
    assert all(gate["passed"] for gate in report["gates"])
    assert len(lock["geometry_sha256"]) == 64
    assert lock["carrier_mode"] == "native_surface_material"
    assert lock["separate_sticker_face_boxes"] == "forbidden"
    assert (tmp_path / "belle_epoque_clay_v92.obj").exists()


def test_crown_and_every_authored_component_are_closed_manifold():
    geometry = build_geometry()
    assert all(mesh_bad_edges(mesh) == 0 for mesh in geometry["meshes"])
    crown = next(mesh for mesh in geometry["meshes"] if mesh["name"] == "watertight_perimeter_court_crown")
    assert len(crown["faces"]) == 24


def test_roof_ring_faces_are_non_crossing_and_wound_outward():
    geometry = build_geometry()
    crown = next(mesh for mesh in geometry["meshes"] if mesh["name"] == "watertight_perimeter_court_crown")
    topology = roof_topology_audit(crown)
    assert topology["crossing_top_faces"] == 0
    assert topology["face_winding_errors"] == 0


def test_court_is_open_and_no_roof_face_spans_lightwell():
    geometry = build_geometry()
    crown = next(mesh for mesh in geometry["meshes"] if mesh["name"] == "watertight_perimeter_court_crown")
    assert geometry["roof"]["court_is_open"] is True
    assert geometry["roof"]["court_cap_allowed"] is False
    assert geometry["roof"]["court_opening_bounds_m"] == [-9.0, 9.0, -7.5, 7.5]
    assert roof_topology_audit(crown)["court_cap_face_count"] == 0


def test_dormer_rhythm_is_3_3_2_2_and_every_dormer_is_manifold():
    geometry = build_geometry()
    dormers = [mesh for mesh in geometry["meshes"] if mesh["name"].startswith("dormer_")]
    counts = {side: sum(mesh["name"].startswith(f"dormer_{side}_") for mesh in dormers) for side in ("front", "rear", "left", "right")}
    assert counts == {"front": 3, "rear": 3, "left": 2, "right": 2}
    assert len(dormers) == geometry["roof"]["dormer_count"] == 10
    assert all(mesh_bad_edges(mesh) == 0 for mesh in dormers)


def test_roof_only_pass_freezes_landmark_dimensions():
    geometry = build_geometry()
    assert geometry["domes"][0] == {"id": "central_glass_dome", "centre": [0.0, 0.0], "diameter_m": 11.8, "curb_diameter_m": 12.4, "rise_m": 4.0, "drum_base_z_m": 24.45, "roof_seat_z_m": 24.8, "dome_base_z_m": 25.75, "top_z_m": 31.0}
    assert geometry["domes"][1] == {"id": "corner_glass_cupola", "centre": [-14.5, -13.5], "diameter_m": 6.4, "rise_m": 3.3, "tower_radius_m": 3.15, "tower_base_z_m": 18.4, "tower_top_z_m": 24.0, "drum_base_z_m": 23.85, "roof_seat_z_m": 24.0, "dome_base_z_m": 25.05, "top_z_m": 29.45, "street_anchor_priority": 1}
    entrance = geometry["entrance"]
    assert {key: entrance[key] for key in ("width_m", "depth_m", "canopy_depth_m")} == {"width_m": 5.4, "depth_m": 4.2, "canopy_depth_m": 4.0}


def test_every_authored_face_has_exactly_one_final_surface_classification():
    geometry = build_geometry()
    surfaces, _adjacency, _required = surface_contract()
    classification = final_surface_classification(geometry)
    coverage = final_surface_coverage_audit(geometry, classification, {surface["surface_id"] for surface in surfaces})
    assert coverage["passed"] is True
    assert coverage["authored_face_count"] == coverage["classified_face_count"] == 1680
    assert coverage["unclassified_face_count"] == 0
    assert coverage["duplicate_face_count"] == 0
    assert coverage["fallback_exception_count"] == 0


def test_final_surface_contract_covers_known_visible_fallback_sources():
    entries = final_surface_classification(build_geometry())["entries"]
    by_mesh: dict[str, list[dict]] = {}
    for entry in entries:
        by_mesh.setdefault(entry["mesh_name"], []).append(entry)
    assert by_mesh["corner_entrance_jamb_left"][0]["finish_class"] == "entrance_stone_return_finish"
    assert by_mesh["wrapped_corner_canopy"][0]["finish_class"] == "canopy_metal_top_edge_and_soffit_finish"
    assert by_mesh["front_main_cornice"][0]["finish_class"] == "cornice_metal_wrap_finish"
    assert {entry["finish_class"] for entry in by_mesh["dormer_front_0"]} == {"elevation_sticker", "roof_sticker_wrap"}
    assert by_mesh["central_dome_drum"][0]["finish_class"] == "roof_metal_wrap_finish"
    assert by_mesh["corner_cupola_drum"][0]["finish_class"] == "roof_metal_wrap_finish"
    assert by_mesh["right_wall"][0]["finish_class"] == "elevation_sticker_with_sampled_returns"
    assert all(entry["fallback_material_forbidden"] for entry in entries)


def test_visible_face_material_audit_blocks_one_fallback_polygon():
    classification = final_surface_classification(build_geometry())
    assignments: dict[str, dict[int, str]] = {}
    for entry in classification["entries"]:
        mesh = assignments.setdefault(entry["mesh_name"], {})
        for start, end in entry["face_ranges_inclusive"]:
            for face in range(start, end + 1):
                mesh[face] = "MAT_FinalFinish_v92_verified"
    assert audit_visible_face_materials(classification, assignments)["status"] == "pass"
    assignments["wrapped_corner_canopy"][1] = "MAT_Roof"
    failed = audit_visible_face_materials(classification, assignments)
    assert failed["status"] == "fail"
    assert failed["failure_count"] == 1
    assert failed["failures"][0] == {"mesh_name": "wrapped_corner_canopy", "face_index": 1, "material": "MAT_Roof", "finish_class": "canopy_metal_top_edge_and_soffit_finish"}


def test_surface_classification_does_not_change_approved_geometry_hash():
    assert sha256(build_geometry()) == "4a0c2c6514d0a546d3a3154b6766d40797c88b8b3ffb7ce4e1523831be73b815"


def test_six_storey_contract_adds_exactly_one_repeatable_middle_band():
    contract = storey_band_contract()
    five = contract["variants"]["five_storey"]
    six = contract["variants"]["six_storey"]
    assert len(five["repeatable_middle"]) == 3
    assert len(six["repeatable_middle"]) == 4
    assert five["ground"] == six["ground"]
    assert five["top_crown"]["template_id"] == six["top_crown"]["template_id"] == "top_crown_v92"
    assert five["roof"]["template_id"] == six["roof"]["template_id"] == "roof_v92"
    assert math.isclose(six["top_crown"]["z_min_m"] - five["top_crown"]["z_min_m"], 4.1)
    assert math.isclose(six["roof"]["z_min_m"] - five["roof"]["z_min_m"], 4.1)
    assert six["roof"]["translation_z_m"] == 4.1
    assert contract["insertion_z_range_m"] == [12.3, 16.4]


def test_six_storey_monolithic_scaling_is_blocked_until_segmented_geometry_exists():
    contract = storey_band_contract()
    six = contract["variants"]["six_storey"]
    assert six["geometry_status"] == "requires_separately_hashed_segmented_floor_addressable_bundle"
    assert six["monolithic_wall_scaling"] == "forbidden"
    assert contract["six_storey_generation_guard"] == "hard_stop_until_segmented_floor_addressable_geometry_is_present"


def test_roof_finish_never_owns_vertical_occupied_floor_carriers():
    classification = final_surface_classification(build_geometry())
    report = storey_band_contract_audit(storey_band_contract(), classification)
    assert report["passed"] is True
    assert report["roof_owned_vertical_face_conflicts"] == []


def test_single_wrapped_corner_entrance_is_deep_and_unobstructed():
    geometry = build_geometry()
    entrance = geometry["entrance"]
    clear_fraction, rays = entrance_clear_fraction(entrance)
    assert entrance["axis"] == "front_left_corner_wrapped"
    assert "centres_m" not in entrance
    assert entrance["carrier_surface_id"] == "corner_pavilion"
    assert entrance["depth_m"] >= 4.0
    assert len(rays) == 9
    assert clear_fraction >= 0.95
    mesh_names = {mesh["name"] for mesh in geometry["meshes"]}
    assert "wrapped_corner_canopy" in mesh_names
    assert any(name.startswith("corner_pavilion_facet_") for name in mesh_names)
    assert not any("front_arch" in name for name in mesh_names)


def test_evidence_conflict_gives_aerial_and_oblique_topology_authority():
    evidence = evidence_contract()
    conflict = evidence["evidence_conflicts"][0]
    assert conflict["id"] == "principal_entrance_topology"
    assert conflict["adjudication"] == "oblique_massing_and_roof_plan_control_topology"
    assert "entrance_plan_location" in conflict["street_identity_excluded_scope"]
    assert conflict["status"] == "resolved"


def test_domes_have_real_drums_seated_into_one_crown():
    geometry = build_geometry()
    assert geometry["roof"]["field_count"] == 8
    assert geometry["roof"]["mansard_field_count"] == 4
    assert geometry["roof"]["terrace_field_count"] == 4
    assert geometry["roof"]["central_dome_count"] == 1
    assert geometry["roof"]["corner_cupola_count"] == 1
    assert all(dome["roof_seat_z_m"] - dome["drum_base_z_m"] + 1e-6 >= 0.15 for dome in geometry["domes"])
    assert geometry["domes"][0]["rise_m"] / geometry["domes"][0]["diameter_m"] <= 0.45
    assert geometry["domes"][1]["rise_m"] / geometry["domes"][1]["diameter_m"] <= 0.55
    mesh_names = {mesh["name"] for mesh in geometry["meshes"]}
    assert {"central_dome_curb", "central_dome_cap", "central_dome_finial", "corner_cupola_cap", "corner_cupola_finial"}.issubset(mesh_names)


def test_mansard_seats_on_walls_and_has_real_setback_break():
    geometry = build_geometry()
    assert geometry["roof"]["outer_bottom_z_m"] == geometry["dimensions"]["wall_height_m"]
    assert geometry["roof"]["inner_eave_z_m"] - geometry["roof"]["outer_eave_z_m"] >= 3.0
    assert geometry["upper_setback"]["height_m"] >= 1.5
    assert geometry["upper_setback"]["inset_m"] >= 0.5
    mesh_names = {mesh["name"] for mesh in geometry["meshes"]}
    assert "front_main_cornice" in mesh_names
    assert "corner_pavilion_mid_cornice" in mesh_names


def test_final_roof_has_steep_mansard_then_flat_terrace_and_visible_court():
    roof = build_geometry()["roof"]
    mansard_slope = (roof["mansard_break_z_m"] - roof["outer_eave_z_m"]) / 3.5
    terrace_slope = (roof["inner_eave_z_m"] - roof["mansard_break_z_m"]) / 5.5
    assert mansard_slope / terrace_slope >= 3.0
    assert terrace_slope <= 0.25
    assert roof["section"] == "steep_outer_zinc_mansard_plus_shallow_inner_terrace_and_raised_court_curb"


def test_central_dome_fits_inside_court_with_circulation_margin():
    geometry = build_geometry()
    dome = geometry["domes"][0]
    assert dome["diameter_m"] <= 12.0
    assert dome["rise_m"] <= 4.2
    assert (15.0 - dome["curb_diameter_m"]) / 2 >= 1.0
    assert dome["top_z_m"] == geometry["dimensions"]["visible_height_m"]


def test_corner_cupola_has_concentric_vertical_tower_and_closed_returns():
    geometry = build_geometry()
    cupola = geometry["domes"][1]
    assert cupola["tower_top_z_m"] - cupola["tower_base_z_m"] >= 5.0
    assert cupola["tower_radius_m"] / (cupola["diameter_m"] / 2) >= 0.95
    assert 3.3 - cupola["tower_radius_m"] <= 0.25
    mesh_names = {mesh["name"] for mesh in geometry["meshes"]}
    assert {"corner_upper_tower", "corner_tower_crown", "corner_upper_front_return", "corner_upper_left_return"}.issubset(mesh_names)


def test_corner_pavilion_and_canopy_are_broad_enough_to_turn_both_streets():
    geometry = build_geometry()
    entrance = geometry["entrance"]
    assert math.pi * 7.0 / 2.0 >= 10.0
    assert entrance["width_m"] >= 5.0
    assert entrance["canopy_depth_m"] >= 3.5
    assert geometry["footprint_polygon_m"][0] == [-11.0, -17.0]


def test_every_exposed_carrier_has_mapping_boundary_and_non_bare_adjacency():
    surfaces, adjacency, _required = surface_contract()
    roles = {surface["role"] for surface in surfaces}
    assert {"front", "right", "rear", "left", "front_left_corner", "central_dome", "corner_cupola", "dormer_front_geometry", "dormer_rear_geometry", "dormer_left_geometry", "dormer_right_geometry"}.issubset(roles)
    corner = next(surface for surface in surfaces if surface["role"] == "front_left_corner")
    assert corner["mapping"] == "cylindrical"
    assert all(surface["exposed"] and surface["mapping"] in {"planar", "radial", "cylindrical"} and len(surface["boundary_m"]) >= 4 for surface in surfaces)
    assert all(item["mode"] in {"covered_joint", "hard_material_joint", "continuous_wrap", "feathered_lap"} for item in adjacency)
    assert all(item["mode"] != "bare_butt" for item in adjacency)


def test_gate_fails_when_geometry_is_regressed_not_when_status_text_changes():
    geometry = build_geometry()
    geometry["dimensions"]["depth_m"] = 20.0
    surfaces, adjacency, required = surface_contract()
    report = audit(geometry, evidence_contract(), surfaces, adjacency, required)
    gate = next(item for item in report["gates"] if item["id"] == "outer_plan_proportion")
    assert gate["passed"] is False
    assert report["status"] == "fail"


def test_fixed_landmark_forbids_shape_mutation(tmp_path: Path):
    placement = build_lock(tmp_path)["placement"]
    assert placement["mode"] == "fixed_select_and_place"
    assert placement["polygon_fit"] is False
    assert placement["uniform_scale"] == "forbidden"
    assert placement["non_uniform_scale"] == "forbidden"


def test_geometry_hash_changes_for_a_single_vertex_edit():
    geometry = build_geometry()
    before = sha256(geometry)
    geometry["meshes"][0]["vertices"][0][0] += 0.001
    assert sha256(geometry) != before
