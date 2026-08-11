from __future__ import annotations

import math

from belle_epoque_floor_sticker_v93 import build_floor_plan
from build_belle_epoque_floor_geometry_v93 import SURFACE_SOURCE_MESHES, build_segmented_geometry


def test_five_storey_segmentation_preserves_v92_shape_bounds() -> None:
    geometry = build_segmented_geometry(5)
    assert geometry["audit"]["status"] == "pass"
    assert geometry["audit"]["source_bounds_m"] == geometry["audit"]["segmented_bounds_m"]
    assert geometry["audit"]["floor_addressable_mesh_count"] == len(SURFACE_SOURCE_MESHES) * 5
    assert geometry["audit"]["roof_owned_vertical_wall_conflicts"] == []


def test_six_storey_has_own_hash_and_one_module_height_increase() -> None:
    five = build_segmented_geometry(5)
    six = build_segmented_geometry(6)
    assert six["audit"]["status"] == "pass"
    assert six["geometry_sha256"] != five["geometry_sha256"]
    assert math.isclose(six["audit"]["segmented_bounds_m"][5] - five["audit"]["segmented_bounds_m"][5], 4.1)
    assert six["audit"]["floor_addressable_mesh_count"] == len(SURFACE_SOURCE_MESHES) * 6


def test_floor_plan_targets_resolve_to_segmented_geometry_names() -> None:
    for floor_count in (5, 6):
        geometry = build_segmented_geometry(floor_count)
        plan = build_floor_plan(floor_count, segmented_geometry_sha256=geometry["geometry_sha256"])
        names = {mesh["name"] for mesh in geometry["meshes"]}
        assert all(set(item["target_ids"]).issubset(names) for item in plan["floor_instances"])


def test_six_storey_fixed_ground_and_entrance_are_not_translated() -> None:
    five = build_segmented_geometry(5)
    six = build_segmented_geometry(6)
    five_meshes = {mesh["name"]: mesh for mesh in five["meshes"]}
    six_meshes = {mesh["name"]: mesh for mesh in six["meshes"]}
    for name in ("corner_entrance_jamb_left", "corner_entrance_jamb_right", "wrapped_corner_canopy"):
        assert six_meshes[name]["vertices"] == five_meshes[name]["vertices"]


def test_six_storey_complete_roof_landmark_group_moves_exactly_one_module() -> None:
    five = build_segmented_geometry(5)
    six = build_segmented_geometry(6)
    five_meshes = {mesh["name"]: mesh for mesh in five["meshes"]}
    six_meshes = {mesh["name"]: mesh for mesh in six["meshes"]}
    roof_names = [name for name, mesh in five_meshes.items() if mesh.get("material_domain") == "roof_only"]
    assert roof_names
    for name in roof_names:
        assert all(abs(float(b[2]) - float(a[2]) - 4.1) < 1e-6 for a, b in zip(five_meshes[name]["vertices"], six_meshes[name]["vertices"]))
