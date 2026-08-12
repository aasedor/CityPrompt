from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest


MODULE_PATH = Path(__file__).parents[1] / "build_daylight_sawtooth_sticker_lego_v98.py"
SPEC = importlib.util.spec_from_file_location("daylight_sawtooth_v98", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


@pytest.fixture(scope="module")
def canonical():
    return MODULE.build_geometry("canonical")


@pytest.fixture(scope="module")
def extended():
    return MODULE.build_geometry("extended")


def test_exact_refs_lock_one_storey_canonical(canonical):
    assert canonical["reference_authority"].startswith("exact_three_view_images")
    assert len(canonical["reference_evidence"]) == 3
    assert canonical["dimensions"] == {
        "width_m": 60.0, "depth_m": 40.0, "occupied_storeys": 1,
        "wall_top_m": 6.0, "tooth_valley_m": 6.35, "tooth_ridge_m": 11.2,
    }


def test_bounded_tier_expands_by_complete_tooth_cells(canonical, extended):
    assert canonical["structural_grid"]["tooth_count"] == 6
    assert extended["structural_grid"]["tooth_count"] == 8
    assert canonical["dimensions"]["depth_m"] == extended["dimensions"]["depth_m"] == 40.0
    assert extended["dimensions"]["width_m"] - canonical["dimensions"]["width_m"] == 20.0
    assert extended["structural_grid"]["front_bays"] - canonical["structural_grid"]["front_bays"] == 4
    assert extended["dimensions"]["occupied_storeys"] == 1


def test_all_teeth_are_same_handed_physical_northlights(canonical):
    cells = canonical["roof_cells"]
    assert len(cells) == 6
    assert {cell["northlight_orientation"] for cell in cells} == {"+X"}
    assert all(cell["same_handed"] for cell in cells)
    names = {mesh["name"]: mesh for mesh in canonical["meshes"]}
    for cell in cells:
        assert names[cell["opaque_mesh"]]["watertight"] is True
        glass = names[cell["northlight_mesh"]]
        assert glass["watertight"] is True
        assert glass["material_domain"] == "northlight_glass"
        assert glass["physical_glass"] is True
        # 25 longitudinal glazing bars plus 6 continuous crossbars.
        assert len(cell["northlight_frames"]) == 31
        assert all(names[name]["physical_frame"] for name in cell["northlight_frames"])


def test_roof_cells_are_individually_addressable(canonical):
    opaque = [m for m in canonical["meshes"] if m["material_domain"] == "opaque_roof"]
    glass = [m for m in canonical["meshes"] if m["material_domain"] == "northlight_glass"]
    assert len(opaque) == len(glass) == 6
    assert len({m["sticker_owner_id"] for m in opaque + glass}) == 12


def test_every_aperture_is_a_true_recess(canonical):
    names = {mesh["name"] for mesh in canonical["meshes"]}
    for aperture in canonical["apertures"]:
        assert aperture["flat_printed_void"] is False
        assert aperture["recess_depth_m"] > 0.4
        assert aperture["return_meshes"]
        assert set(aperture["return_meshes"]) <= names
        assert aperture["recessed_back_mesh"] in names


def test_singular_three_door_dock_has_complete_access_stack(canonical):
    dock = canonical["dock"]
    assert dock["dock_count"] == 1
    assert dock["rolling_door_count"] == 3
    assert dock["canopy_count"] == 1
    assert dock["stairs"] == 4
    assert dock["ramp_mesh"] == "fixed_loading_ramp"
    front_doors = [a for a in canonical["apertures"] if a["side"] == "front" and a["kind"] == "rolling_door"]
    assert [a["bay"] for a in front_doors] == [0, 1, 2]
    assert not [a for a in canonical["apertures"] if a["side"] != "front" and a["kind"] == "rolling_door"]


def test_detached_chimney_is_hollow_and_ring_capped(canonical):
    record = canonical["chimney"]
    assert record["detached"] and record["hollow"] and record["ring_capped"]
    assert record["inner_radius_m"] > 0
    assert record["outer_radius_m"] > record["inner_radius_m"]
    mesh = next(m for m in canonical["meshes"] if m["name"] == record["mesh"])
    assert {"chimney_exterior", "chimney_interior", "chimney_ring_cap", "chimney_bottom_ring"} == set(mesh["face_roles"])
    assert "chimney_top_cap" not in mesh["face_roles"]


def test_rear_and_left_are_constrained_without_invented_dock(canonical):
    assert canonical["completion_policy"]["rear"] == "constrained_no_extra_dock"
    for aperture in canonical["apertures"]:
        if aperture["side"] in {"rear", "left"}:
            assert aperture["completion_evidence"] == "constrained"
            assert aperture["kind"] == "window"


def test_every_face_has_exactly_one_sticker_owner(canonical, extended):
    for geometry in (canonical, extended):
        face_count = 0
        owner_count = 0
        for mesh in geometry["meshes"]:
            face_count += len(mesh["faces"])
            owner_count += len(mesh["face_owners"])
            assert len(mesh["faces"]) == len(mesh["face_owners"])
            assert all(len(owners) == 1 and owners[0] for owners in mesh["face_owners"])
        assert face_count == owner_count


def test_hard_stops_cover_identity_failures(canonical):
    stops = set(canonical["geometry_hard_stops"])
    assert {
        "occupied_storeys_must_equal_1", "canonical_tooth_count_must_equal_6",
        "all_teeth_must_share_handedness", "all_northlights_must_face_+X",
        "chimney_must_be_detached_hollow_and_ring_capped", "dock_count_must_equal_1",
        "rolling_door_count_must_equal_3", "no_depth_or_vertical_scaling",
        "no_partial_tooth_expansion", "no_invented_rear_dock",
        "every_visible_face_requires_exactly_one_sticker_owner",
    } <= stops


def test_hashes_are_deterministic(canonical, extended):
    assert MODULE.build_geometry("canonical")["geometry_sha256"] == canonical["geometry_sha256"]
    assert MODULE.build_geometry("extended")["geometry_sha256"] == extended["geometry_sha256"]
    assert canonical["geometry_sha256"] != extended["geometry_sha256"]


def test_unknown_size_is_rejected():
    with pytest.raises(KeyError):
        MODULE.build_geometry("rubber")
