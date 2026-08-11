from copy import deepcopy
from pathlib import Path

import pytest

from belle_epoque_sticker_v92 import (
    ContractError,
    DEFAULT_SPEC,
    build_registration,
    load_document,
    sha256_bytes,
    canonical_bytes,
    validate_sources,
)
from build_belle_epoque_clay_v92 import build_lock


def _spec_for(clay):
    spec = deepcopy(load_document(DEFAULT_SPEC))
    # Unit tests exercise the registration contract against the deterministic
    # clay produced in this checkout. The published accepted hash remains a
    # separate release lock and is updated only after architect approval.
    spec["accepted_clay_geometry_sha256"] = clay["geometry_sha256"]
    return spec


def _approved(tmp_path: Path):
    clay = build_lock(tmp_path)
    spec = _spec_for(clay)
    lock_path = tmp_path / "clay_lock.json"
    registration = build_registration(clay, spec, lock_path=lock_path)
    return clay, spec, lock_path, registration


def test_approved_lock_compiles_all_thirty_eight_native_carrier_skins(tmp_path: Path):
    clay, _spec, _lock_path, registration = _approved(tmp_path)
    assert registration["status"] == "registration_ready_pending_atlas_and_glb"
    assert registration["clay_lock"]["geometry_sha256"] == clay["geometry_sha256"]
    assert registration["surface_coverage"]["exposed_surface_count"] == 38
    assert registration["surface_coverage"]["registered_surface_count"] == 38
    assert registration["surface_coverage"]["unowned_exposed_surfaces"] == []
    assert registration["surface_coverage"]["unassigned_visible_polygons"] == []
    assert registration["surface_coverage"]["generic_fallbacks"] == []
    assert registration["surface_coverage"]["broad_flat_colour_surfaces"] == []
    assert registration["surface_coverage"]["status"] == "mandatory_complete"
    assert all(item["kind"] == "carrier_skin" for item in registration["assemblies"])
    assert all(item["carrier_mode"] == "native_surface_material" for item in registration["assemblies"])
    assert all(item["material_binding"]["apply_to_existing_carrier"] is True for item in registration["assemblies"])
    assert all(item["material_binding"]["create_geometry"] is False for item in registration["assemblies"])
    assert all(item["material_binding"]["carrier_offset_m"] == 0.0 for item in registration["assemblies"])
    assert all(item["finish_class"] for item in registration["assemblies"])
    assert all(item["visible_face_coverage"]["scope"] == "all_visible_polygons" for item in registration["assemblies"])
    assert all(item["visible_face_coverage"]["generic_fallback_allowed"] is False for item in registration["assemblies"])
    assert all(item["visible_face_coverage"]["broad_flat_colour_allowed"] is False for item in registration["assemblies"])


def test_every_surface_has_explicit_numeric_anchors_and_crop_transform(tmp_path: Path):
    _clay, _spec, _lock_path, registration = _approved(tmp_path)
    for assembly in registration["assemblies"]:
        assert len(assembly["registration_anchors"]) >= 4
        for anchor in assembly["registration_anchors"]:
            assert len(anchor["object_space_m"]) == 3
            assert len(anchor["surface_uv"]) == 2
            assert len(anchor["source_uv"]) == 2
            assert all(isinstance(value, (int, float)) for value in anchor["object_space_m"])
            assert all(isinstance(value, (int, float)) for value in anchor["surface_uv"])
            assert all(isinstance(value, (int, float)) for value in anchor["source_uv"])
        assert len(assembly["source_crop_xyxy"]) == 4
        assert len(assembly["source_to_canonical_h"]) == 3
        assert all(len(row) == 3 for row in assembly["source_to_canonical_h"])


def test_domes_are_radial_drums_and_wrapped_entrance_are_cylindrical(tmp_path: Path):
    _clay, _spec, _lock_path, registration = _approved(tmp_path)
    by_role = {item["surface_role"]: item for item in registration["assemblies"]}
    assert by_role["central_dome"]["mapping"] == "radial_dome"
    assert by_role["corner_cupola"]["mapping"] == "radial_dome"
    assert by_role["central_dome_drum"]["mapping"] == "cylindrical_arc_length"
    assert by_role["corner_cupola_drum"]["mapping"] == "cylindrical_arc_length"
    assert by_role["front_left_corner"]["mapping"] == "cylindrical_arc_length"
    assert by_role["projecting_corner_cornices"]["mapping"] == "cylindrical_arc_length"
    assert by_role["wrapped_corner_canopy"]["mapping"] == "cylindrical_arc_length"
    assert by_role["central_dome_curb"]["mapping"] == "cylindrical_arc_length"
    assert by_role["central_dome_cap_finial"]["mapping"] == "cylindrical_arc_length"
    assert by_role["corner_cupola_cap_finial"]["mapping"] == "cylindrical_arc_length"
    assert by_role["upper_front_setback"]["mapping"] == "planar_anchored"
    assert by_role["dormer_front_geometry"]["mapping"] == "planar_anchored"
    assert by_role["dormer_rear_geometry"]["mapping"] == "planar_anchored"
    assert by_role["dormer_left_geometry"]["mapping"] == "planar_anchored"
    assert by_role["dormer_right_geometry"]["mapping"] == "planar_anchored"
    assert by_role["central_dome"]["mapping_parameters"]["v_mode"] == "meridional_arc_fraction"
    central_centre = next(anchor["object_space_m"][:2] for anchor in _clay["anchors"] if anchor["anchor_id"] == "central_dome_centre")
    cupola_centre = next(anchor["object_space_m"][:2] for anchor in _clay["anchors"] if anchor["anchor_id"] == "corner_cupola_centre")
    assert by_role["central_dome"]["mapping_parameters"]["centre_xy_m"] == pytest.approx(central_centre)
    assert by_role["corner_cupola"]["mapping_parameters"]["centre_xy_m"] == pytest.approx(cupola_centre)
    assert by_role["corner_cupola_drum"]["mapping_parameters"]["centre_xy_m"] == pytest.approx(cupola_centre)
    assert by_role["corner_upper_tower"]["mapping_parameters"]["centre_xy_m"] == pytest.approx(cupola_centre)
    assert by_role["corner_tower_crown"]["mapping_parameters"]["centre_xy_m"] == pytest.approx(cupola_centre)
    assert by_role["front_left_corner"]["mapping_parameters"]["centre_xy_m"] == pytest.approx([-11.0, -10.0], abs=1e-3)
    assert by_role["projecting_corner_cornices"]["mapping_parameters"]["centre_xy_m"] == pytest.approx([-11.0, -10.0], abs=1e-3)
    assert by_role["wrapped_corner_canopy"]["mapping_parameters"]["centre_xy_m"] == pytest.approx([-11.0, -10.0], abs=1e-3)


def test_every_clay_adjacency_emits_reciprocal_geometry_owned_seams(tmp_path: Path):
    clay, _spec, _lock_path, registration = _approved(tmp_path)
    seams = registration["reciprocal_seams"]
    assert len(seams) == len(clay["adjacency"]) * 2
    for seam in seams:
        reciprocal = [
            item for item in seams
            if item["seam_id"] == seam["seam_id"]
            and item["from_surface"] == seam["to_surface"]
            and item["to_surface"] == seam["from_surface"]
            and item["from_edge"] == seam["to_edge"]
            and item["to_edge"] == seam["from_edge"]
        ]
        assert len(reciprocal) == 1
        assert seam["owner_type"] == "geometry_cover"
        assert seam["owner_id"]
        assert seam["sticker_overlap_m"] == 0.0


def test_entrance_geometry_and_sticker_share_one_wrapped_contour_hash(tmp_path: Path):
    clay, _spec, _lock_path, registration = _approved(tmp_path)
    clearance = registration["entrance_clearance"]
    expected_hash = sha256_bytes(canonical_bytes(clay["entrance"]["contour_uv"]))
    assert clearance["topology"] == "single_wrapped_recessed_front_left_corner"
    assert clearance["carrier_surface_id"] == "corner_pavilion"
    assert clearance["geometry_contour_sha256"] == expected_hash
    assert clearance["sticker_contour_sha256"] == expected_hash
    assert len(clearance["contour_uv"]) == 1


@pytest.mark.parametrize("mutation", ["unapproved", "wrong_hash", "straight_entrance", "v91_box"])
def test_missing_unlocked_straight_front_or_v91_box_clay_is_rejected(tmp_path: Path, mutation: str):
    clay = build_lock(tmp_path)
    spec = _spec_for(clay)
    lock_path = tmp_path / "clay_lock.json"
    invalid = deepcopy(clay)
    if mutation == "unapproved":
        invalid["status"] = "review"
    elif mutation == "wrong_hash":
        invalid["geometry_sha256"] = "0" * 64
    elif mutation == "straight_entrance":
        invalid["entrance"]["topology"] = "three_straight_front_arches"
    else:
        invalid["surfaces"][0]["kind"] = "facade_skin"
        invalid["surfaces"][0]["carrier_thickness_m"] = 0.045
    with pytest.raises(ContractError):
        build_registration(invalid, spec, lock_path=lock_path)


def test_duplicate_feature_ownership_and_contour_drift_are_rejected(tmp_path: Path):
    clay = build_lock(tmp_path)
    spec = _spec_for(clay)
    lock_path = tmp_path / "clay_lock.json"
    duplicate = deepcopy(clay)
    duplicate["feature_ownership"]["sticker"].append(duplicate["feature_ownership"]["geometry"][0])
    with pytest.raises(ContractError, match="duplicates"):
        build_registration(duplicate, spec, lock_path=lock_path)
    drift = deepcopy(clay)
    drift["entrance"]["contour_uv"][0][0][0] += 0.01
    with pytest.raises(ContractError, match="contour hash"):
        build_registration(drift, spec, lock_path=lock_path)


def test_all_accepted_sources_are_hash_locked_with_explicit_crop_transforms():
    spec = load_document(DEFAULT_SPEC)
    sources = validate_sources(spec)
    assert len(sources) == 15
    assert all(source["verified_sha256"] == source["sha256"] for source in sources.values())
    assert all(len(source["source_crop_xyxy"]) == 4 for source in sources.values())
    assert all(len(source["source_to_canonical_h"]) == 3 for source in sources.values())


def test_every_visible_role_has_texture_class_and_no_generic_fallback(tmp_path: Path):
    clay, spec, _lock_path, registration = _approved(tmp_path)
    contract = spec["visible_face_coverage_contract"]
    assert contract["unmatched_polygon_action"] == "hard_stop"
    assert {"blue", "grey", "gray", "clay", "default"}.issubset(
        set(contract["generic_fallback_materials_forbidden"])
    )
    assert set(contract["finish_class_for_role"]) == {surface["role"] for surface in clay["surfaces"]}
    for assembly in registration["assemblies"]:
        finish = contract["finish_classes"][assembly["finish_class"]]
        assert finish["all_visible_faces"] is True
        assert finish["fallback_allowed"] is False
        assert finish["broad_flat_colour_allowed"] is False
        assert assembly["source_sha256"]


def test_entrance_canopy_roof_cornice_and_dormer_returns_have_deliberate_skins(tmp_path: Path):
    _clay, _spec, _lock_path, registration = _approved(tmp_path)
    supplements = {item["id"]: item for item in registration["supplemental_visible_bindings"]}
    assert set(supplements) == {
        "entrance_jamb_left_skin", "entrance_jamb_right_skin", "entrance_tunnel_soffit_skin",
        "entrance_tunnel_side_return_skin", "entrance_back_glass_skin",
        "entrance_interior_backplate_skin", "canopy_underside_skin",
    }
    assert supplements["entrance_back_glass_skin"]["finish_class"] == "entrance_dark_glass_pbr"
    assert supplements["entrance_interior_backplate_skin"]["finish_class"] == "entrance_occupied_interior_pbr"
    assert supplements["entrance_tunnel_soffit_skin"]["finish_class"] == "entrance_limestone_return_pbr"
    assert supplements["canopy_underside_skin"]["finish_class"] == "iron_glass_canopy_pbr"
    assert all(item["generic_fallback_allowed"] is False for item in supplements.values())
    by_role = {item["surface_role"]: item for item in registration["assemblies"]}
    for role in (
        "projecting_perimeter_cornice", "projecting_corner_cornices",
        "roof_mansard_front", "roof_terrace_front", "dormer_front_geometry",
        "central_dome_drum", "corner_cupola_drum",
    ):
        assert by_role[role]["visible_face_coverage"]["scope"] == "all_visible_polygons"


def test_delivery_rejects_glb_over_eight_megabytes(tmp_path: Path):
    clay = build_lock(tmp_path)
    spec = _spec_for(clay)
    lock_path = tmp_path / "clay_lock.json"
    oversized = tmp_path / "oversized.glb"
    with oversized.open("wb") as handle:
        handle.seek(spec["atlas_budget"]["assembled_glb_bytes_max"])
        handle.write(b"x")
    with pytest.raises(ContractError, match="V92 limit"):
        build_registration(clay, spec, lock_path=lock_path, assembled_glb=oversized)
