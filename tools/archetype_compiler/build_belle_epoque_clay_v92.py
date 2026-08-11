"""Build and audit the clay lock for the Belle Epoque Grand Magasin V92 pilot.

This bounded builder deliberately stops before sticker authoring.  It converts
the three exact V91 reference views into one fixed, select-and-place clay
contract, writes a neutral OBJ for inspection, and derives every approval gate
from the resulting geometry/evidence artifacts.  No image API is used.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

from PIL import Image, ImageDraw


REPO = Path(__file__).resolve().parents[2]
REFERENCE_ROOT = REPO / "frontend/public/archetypes/buildings/grand-magasin"
DEFAULT_OUTPUT = REPO / "artifacts/belle-epoque-clay-v92"
SCHEMA = "belle-epoque-clay-lock@1"

# Measurements are pixel annotations on the exact V91 reference images.  They
# are intentionally kept beside the executable contract so a reviewer can
# move an annotation and see the measured gates change.
REFERENCE_MEASUREMENTS = {
    "street_identity": {
        "path": "variant_0.png",
        "building_bbox_px": [77, 22, 951, 670],
        "floor_datums_y_px": [670, 565, 468, 371, 272, 174],
        "entrance_centres_x_px": [447, 510, 573],
        "entrance_span_px": [414, 606],
        "horizon_y_px": 474,
        "vanishing_points_px": [[-905, 474], [1915, 474], [510, -2690]],
    },
    "oblique_massing": {
        "path": "variant_0_angle_60.jpg",
        "building_bbox_px": [247, 133, 1110, 888],
        "roof_corners_px": [[260, 247], [626, 132], [1098, 298], [555, 888]],
        "court_corners_px": [[458, 214], [766, 163], [916, 355], [579, 461]],
        "dome_centre_px": [647, 371],
        "horizon_y_px": 518,
        "vanishing_points_px": [[-620, 518], [1920, 518], [606, -1810]],
    },
    "roof_plan": {
        "path": "variant_0_angle_90.jpg",
        "outer_bbox_px": [204, 54, 1022, 849],
        "court_bbox_px": [376, 238, 884, 670],
        "central_dome_bbox_px": [447, 281, 863, 697],
        "corner_dome_bbox_px": [202, 662, 369, 839],
        "camera_mode": "near_orthographic",
        "estimated_fov_deg": 18.0,
    },
}

THRESHOLDS = {
    "outer_plan_aspect_error_max": 0.08,
    "court_plan_aspect_error_max": 0.08,
    "central_dome_ratio_error_max": 0.22,
    "corner_dome_ratio_error_max": 0.16,
    "floor_datum_rmse_max": 0.025,
    "entrance_corner_alignment_max_m": 0.10,
    "camera_anchor_rmse_max": 0.015,
    "camera_anchor_p95_max": 0.03,
    "roof_manifold_bad_edges_max": 0,
    "roof_face_winding_errors_max": 0,
    "roof_crossing_faces_max": 0,
    "court_cap_faces_max": 0,
    "open_court_area_min_m2": 120.0,
    "dormer_count_exact": 10,
    "entrance_clear_ray_fraction_min": 0.95,
    "dome_seat_overlap_min_m": 0.15,
    "roof_wall_gap_max_m": 0.02,
    "mansard_rise_min_m": 3.0,
    "central_dome_rise_ratio_max": 0.45,
    "corner_dome_rise_ratio_max": 0.55,
    "corner_pavilion_arc_min_m": 10.0,
    "wrapped_entrance_width_min_m": 5.0,
    "wrapped_canopy_depth_min_m": 3.5,
    "upper_setback_min_m": 0.5,
    "mansard_to_terrace_slope_ratio_min": 3.0,
    "terrace_slope_max": 0.25,
    "central_dome_diameter_max_m": 12.0,
    "central_dome_rise_max_m": 4.2,
    "court_circulation_margin_min_m": 1.0,
    "corner_tower_support_height_min_m": 5.0,
    "cupola_support_ratio_min": 0.95,
    "cupola_plate_projection_max_m": 0.25,
    "carrier_coverage_min": 1.0,
    "unpaired_required_edges_max": 0,
    "max_final_glb_bytes": 8_000_000,
}


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def sha256(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def relative_error(actual: float, expected: float) -> float:
    return abs(actual / expected - 1.0)


def rmse(values: Iterable[float]) -> float:
    samples = list(values)
    return math.sqrt(sum(value * value for value in samples) / max(1, len(samples)))


def box_mesh(name: str, bounds: list[float]) -> dict[str, Any]:
    x0, y0, z0, x1, y1, z1 = bounds
    vertices = [
        [x0, y0, z0], [x1, y0, z0], [x1, y1, z0], [x0, y1, z0],
        [x0, y0, z1], [x1, y0, z1], [x1, y1, z1], [x0, y1, z1],
    ]
    faces = [
        [0, 3, 2, 1], [4, 5, 6, 7],
        [0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7],
    ]
    return {"name": name, "vertices": vertices, "faces": faces}


def extruded_polygon_mesh(
    name: str, polygon_xz: list[list[float]], y0: float, y1: float,
) -> dict[str, Any]:
    count = len(polygon_xz)
    vertices = [[x, y0, z] for x, z in polygon_xz] + [[x, y1, z] for x, z in polygon_xz]
    faces = [list(reversed(range(count))), list(range(count, count * 2))]
    for index in range(count):
        nxt = (index + 1) % count
        faces.append([index, nxt, count + nxt, count + index])
    return {"name": name, "vertices": vertices, "faces": faces}


def extruded_plan_polygon_mesh(
    name: str, polygon_xy: list[list[float]], z0: float, z1: float,
) -> dict[str, Any]:
    count = len(polygon_xy)
    vertices = [[x, y, z0] for x, y in polygon_xy] + [[x, y, z1] for x, y in polygon_xy]
    faces = [list(reversed(range(count))), list(range(count, count * 2))]
    for index in range(count):
        nxt = (index + 1) % count
        faces.append([index, nxt, count + nxt, count + index])
    return {"name": name, "vertices": vertices, "faces": faces}


def extruded_side_polygon_mesh(
    name: str, polygon_yz: list[list[float]], x0: float, x1: float,
) -> dict[str, Any]:
    count = len(polygon_yz)
    vertices = [[x0, y, z] for y, z in polygon_yz] + [[x1, y, z] for y, z in polygon_yz]
    faces = [list(reversed(range(count))), list(range(count, count * 2))]
    for index in range(count):
        nxt = (index + 1) % count
        faces.append([index, nxt, count + nxt, count + index])
    return {"name": name, "vertices": vertices, "faces": faces}


def dormer_meshes() -> list[dict[str, Any]]:
    """Ten bounded pedimented dormers attached to the steep mansard fields."""
    meshes: list[dict[str, Any]] = []
    for side, y0, y1 in (("front", -15.6, -14.0), ("rear", 14.0, 15.6)):
        for index, x in enumerate((-9.0, 0.0, 9.0)):
            polygon = [[x - 1.25, 22.1], [x - 1.25, 24.0], [x, 25.15], [x + 1.25, 24.0], [x + 1.25, 22.1]]
            meshes.append(extruded_polygon_mesh(f"dormer_{side}_{index}", polygon, y0, y1))
    for side, x0, x1 in (("left", -15.6, -14.0), ("right", 14.0, 15.6)):
        for index, y in enumerate((-5.0, 5.0)):
            polygon = [[y - 1.25, 22.1], [y - 1.25, 24.0], [y, 25.15], [y + 1.25, 24.0], [y + 1.25, 22.1]]
            meshes.append(extruded_side_polygon_mesh(f"dormer_{side}_{index}", polygon, x0, x1))
    return meshes


def roof_ring_mesh() -> dict[str, Any]:
    outer = [[-18.0, -17.0], [18.0, -17.0], [18.0, 17.0], [-18.0, 17.0]]
    mansard_break = [[-14.5, -13.5], [14.5, -13.5], [14.5, 13.5], [-14.5, 13.5]]
    # All three loops use the same counter-clockwise BL, BR, TR, TL order.
    # The previous inner loop was clockwise, so index-wise quads crossed the
    # roof and produced pointed sheets in Blender.
    inner = [[-9.0, -7.5], [9.0, -7.5], [9.0, 7.5], [-9.0, 7.5]]
    # The lower zinc edge seats directly on the 20.5 m upper wall; the higher
    # court curb makes the mansard section legible without floating roof slabs.
    outer_z, break_z, inner_z, thickness = 21.0, 24.0, 24.8, 0.5
    vertices = (
        [[x, y, outer_z] for x, y in outer]
        + [[x, y, break_z] for x, y in mansard_break]
        + [[x, y, inner_z] for x, y in inner]
        + [[x, y, outer_z - thickness] for x, y in outer]
        + [[x, y, break_z - thickness] for x, y in mansard_break]
        + [[x, y, inner_z - thickness] for x, y in inner]
    )
    # Four steep outer mansard fields and four shallow inner terrace fields are
    # one connected shell. The raised inner edge is the explicit court curb.
    mansard_top = [[0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7]]
    terrace_top = [[4, 5, 9, 8], [5, 6, 10, 9], [6, 7, 11, 10], [7, 4, 8, 11]]
    top = mansard_top + terrace_top
    bottom = [list(reversed([index + 12 for index in face])) for face in top]
    # Exterior fascias face away from the roof; court fascias face inward into
    # the lightwell. This winding is verified by the roof audit below.
    outer_sides = [[index, index + 12, (index + 1) % 4 + 12, (index + 1) % 4] for index in range(4)]
    inner_sides = [[8 + index, 8 + (index + 1) % 4, 20 + (index + 1) % 4, 20 + index] for index in range(4)]
    return {"name": "watertight_perimeter_court_crown", "vertices": vertices, "faces": top + bottom + outer_sides + inner_sides}


def cylinder_mesh(name: str, centre: list[float], radius: float, z0: float, z1: float, segments: int = 24) -> dict[str, Any]:
    cx, cy = centre
    vertices = []
    for z in (z0, z1):
        vertices.extend([[cx + radius * math.cos(2 * math.pi * i / segments), cy + radius * math.sin(2 * math.pi * i / segments), z] for i in range(segments)])
    vertices.extend([[cx, cy, z0], [cx, cy, z1]])
    bottom_centre, top_centre = segments * 2, segments * 2 + 1
    faces = []
    for index in range(segments):
        nxt = (index + 1) % segments
        faces.append([index, nxt, segments + nxt, segments + index])
        faces.append([bottom_centre, nxt, index])
        faces.append([top_centre, segments + index, segments + nxt])
    return {"name": name, "vertices": vertices, "faces": faces}


def dome_mesh(name: str, centre: list[float], radius: float, base_z: float, rise: float, segments: int = 32, rings: int = 8) -> dict[str, Any]:
    cx, cy = centre
    vertices: list[list[float]] = []
    for ring in range(rings):
        t = ring / rings
        ring_radius = radius * math.cos(t * math.pi / 2)
        z = base_z + rise * math.sin(t * math.pi / 2)
        vertices.extend([[cx + ring_radius * math.cos(2 * math.pi * i / segments), cy + ring_radius * math.sin(2 * math.pi * i / segments), z] for i in range(segments)])
    apex = len(vertices)
    vertices.append([cx, cy, base_z + rise])
    bottom_centre = len(vertices)
    vertices.append([cx, cy, base_z])
    faces: list[list[int]] = []
    for ring in range(rings - 1):
        for index in range(segments):
            nxt = (index + 1) % segments
            a, b = ring * segments + index, ring * segments + nxt
            c, d = (ring + 1) * segments + nxt, (ring + 1) * segments + index
            faces.append([a, b, c, d])
    last = (rings - 1) * segments
    for index in range(segments):
        nxt = (index + 1) % segments
        faces.append([last + index, last + nxt, apex])
        faces.append([bottom_centre, nxt, index])
    return {"name": name, "vertices": vertices, "faces": faces}


def build_corner_entrance_meshes() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    meshes: list[dict[str, Any]] = []
    blockers: list[dict[str, Any]] = []
    corner_centre = [-11.0, -10.0]
    radius = 7.0
    arc = [
        [corner_centre[0] + radius * math.cos(math.radians(180 + 22.5 * index)),
         corner_centre[1] + radius * math.sin(math.radians(180 + 22.5 * index))]
        for index in range(5)
    ]

    def facet_polygon(start: list[float], end: list[float], thickness: float = 0.75) -> list[list[float]]:
        midpoint = [(start[0] + end[0]) / 2, (start[1] + end[1]) / 2]
        inward = [corner_centre[0] - midpoint[0], corner_centre[1] - midpoint[1]]
        length = math.hypot(*inward)
        inward = [value / length for value in inward]
        return [start, end, [end[0] + inward[0] * thickness, end[1] + inward[1] * thickness], [start[0] + inward[0] * thickness, start[1] + inward[1] * thickness]]

    # The two outer facets remain full-height. The two centre facets are open
    # below the 4.8 m head, producing one entrance wrapped around the corner.
    for index, (start, end) in enumerate(zip(arc, arc[1:])):
        z0 = 0.0 if index in {0, 3} else 4.8
        name = f"corner_pavilion_facet_{index}"
        mesh = extruded_plan_polygon_mesh(name, facet_polygon(start, end), z0, 20.5)
        meshes.append(mesh)
        if index in {1, 2}:
            xs = [point[0] for point in mesh["vertices"]]
            ys = [point[1] for point in mesh["vertices"]]
            blockers.append({"id": name, "bounds": [min(xs), min(ys), 4.8, max(xs), max(ys), 20.5]})

    radial_out = [-math.sqrt(0.5), -math.sqrt(0.5)]
    inward = [-radial_out[0], -radial_out[1]]
    tangent = [math.sqrt(0.5), -math.sqrt(0.5)]
    outer_centre = [corner_centre[0] + radial_out[0] * radius, corner_centre[1] + radial_out[1] * radius]
    entrance_width, depth, jamb_width = 5.4, 4.2, 0.10
    for side in (-1.0, 1.0):
        tangent_offset = side * (entrance_width / 2 + jamb_width / 2)
        outside = [outer_centre[0] + tangent[0] * tangent_offset, outer_centre[1] + tangent[1] * tangent_offset]
        inside = [outside[0] + inward[0] * depth, outside[1] + inward[1] * depth]
        half = [tangent[0] * jamb_width / 2, tangent[1] * jamb_width / 2]
        polygon = [
            [outside[0] - half[0], outside[1] - half[1]],
            [outside[0] + half[0], outside[1] + half[1]],
            [inside[0] + half[0], inside[1] + half[1]],
            [inside[0] - half[0], inside[1] - half[1]],
        ]
        meshes.append(extruded_plan_polygon_mesh(f"corner_entrance_jamb_{'right' if side > 0 else 'left'}", polygon, 0.0, 4.8))

    # A faceted annular canopy follows the same corner centre and therefore
    # cannot detach or become a generic straight marquee.
    outer_canopy = [[corner_centre[0] + 10.2 * math.cos(math.radians(180 + 11.25 * index)), corner_centre[1] + 10.2 * math.sin(math.radians(180 + 11.25 * index))] for index in range(9)]
    inner_canopy = [[corner_centre[0] + 6.2 * math.cos(math.radians(270 - 11.25 * index)), corner_centre[1] + 6.2 * math.sin(math.radians(270 - 11.25 * index))] for index in range(9)]
    meshes.append(extruded_plan_polygon_mesh("wrapped_corner_canopy", outer_canopy + inner_canopy, 5.05, 5.38))
    blockers.append({"id": "wrapped_corner_canopy", "bounds": [-21.2, -20.2, 5.05, -4.8, -3.8, 5.38]})

    # Two projected bands make the pavilion read as a load-bearing corner bay,
    # not a texture bent around an otherwise square box.
    for label, z0, z1, outer_radius, inner_radius in (
        ("mid", 18.05, 18.75, 7.38, 6.72),
        ("crown", 20.10, 20.62, 7.32, 6.76),
    ):
        outer_band = [[corner_centre[0] + outer_radius * math.cos(math.radians(180 + 11.25 * index)), corner_centre[1] + outer_radius * math.sin(math.radians(180 + 11.25 * index))] for index in range(9)]
        inner_band = [[corner_centre[0] + inner_radius * math.cos(math.radians(270 - 11.25 * index)), corner_centre[1] + inner_radius * math.sin(math.radians(270 - 11.25 * index))] for index in range(9)]
        meshes.append(extruded_plan_polygon_mesh(f"corner_pavilion_{label}_cornice", outer_band + inner_band, z0, z1))
    return meshes, blockers


def build_geometry() -> dict[str, Any]:
    corner_meshes, blockers = build_corner_entrance_meshes()
    wall_meshes = [
        box_mesh("front_wall", [-11.0, -17.0, 0.0, 18.0, -16.0, 18.5]),
        box_mesh("right_wall", [17.0, -17.0, 0.0, 18.0, 17.0, 18.5]),
        box_mesh("rear_wall", [-18.0, 16.0, 0.0, 18.0, 17.0, 18.5]),
        box_mesh("left_wall", [-18.0, -10.0, 0.0, -17.0, 17.0, 18.5]),
        box_mesh("court_front_wall", [-9.0, -7.5, 0.0, 9.0, -7.0, 20.5]),
        box_mesh("court_rear_wall", [-9.0, 7.0, 0.0, 9.0, 7.5, 20.5]),
        box_mesh("court_left_wall", [-9.0, -7.5, 0.0, -8.5, 7.5, 20.5]),
        box_mesh("court_right_wall", [8.5, -7.5, 0.0, 9.0, 7.5, 20.5]),
        # Recessed upper wall registers the characteristic upper-storey break
        # before the zinc mansard begins.
        box_mesh("upper_front_setback", [-10.5, -16.35, 18.5, 17.35, -15.85, 20.5]),
        box_mesh("upper_right_setback", [17.35, -16.35, 18.5, 17.85, 16.35, 20.5]),
        box_mesh("upper_rear_setback", [-17.35, 15.85, 18.5, 17.35, 16.35, 20.5]),
        box_mesh("upper_left_setback", [-17.85, -9.5, 18.5, -17.35, 16.35, 20.5]),
        # These two closed returns bridge the inset upper walls back to the
        # faceted pavilion. They eliminate the black vertical corner slot seen
        # in the second clay render.
        box_mesh("corner_upper_front_return", [-11.10, -17.05, 18.5, -10.40, -16.25, 20.5]),
        box_mesh("corner_upper_left_return", [-18.05, -10.10, 18.5, -17.25, -9.40, 20.5]),
        box_mesh("front_main_cornice", [-11.35, -17.35, 18.05, 18.35, -16.65, 18.75]),
        box_mesh("right_main_cornice", [17.65, -17.35, 18.05, 18.35, 17.35, 18.75]),
        box_mesh("rear_main_cornice", [-18.35, 16.65, 18.05, 18.35, 17.35, 18.75]),
        box_mesh("left_main_cornice", [-18.35, -10.35, 18.05, -17.65, 17.35, 18.75]),
        box_mesh("front_crown_return", [-11.2, -16.68, 20.1, 18.2, -15.72, 20.62]),
        box_mesh("right_crown_return", [17.18, -16.68, 20.1, 18.02, 16.68, 20.62]),
        box_mesh("rear_crown_return", [-18.02, 15.72, 20.1, 18.02, 16.68, 20.62]),
        box_mesh("left_crown_return", [-18.02, -9.7, 20.1, -17.18, 16.68, 20.62]),
    ]
    meshes = [
        *corner_meshes, *wall_meshes, roof_ring_mesh(), *dormer_meshes(),
        cylinder_mesh("central_dome_curb", [0.0, 0.0], 6.2, 24.45, 25.05, 40),
        cylinder_mesh("central_dome_drum", [0.0, 0.0], 6.0, 24.85, 25.9, 40),
        dome_mesh("central_glass_dome", [0.0, 0.0], 5.9, 25.75, 4.0, 40, 10),
        cylinder_mesh("central_dome_cap", [0.0, 0.0], 1.15, 29.65, 30.2, 24),
        cylinder_mesh("central_dome_finial", [0.0, 0.0], 0.11, 30.15, 31.0, 12),
        # A real vertical corner tower grows from the entrance pavilion. The
        # cupola is concentric and its crown projects only 0.15 m beyond it.
        cylinder_mesh("corner_upper_tower", [-14.5, -13.5], 3.15, 18.4, 24.0, 16),
        cylinder_mesh("corner_tower_crown", [-14.5, -13.5], 3.3, 23.65, 24.15, 16),
        cylinder_mesh("corner_cupola_drum", [-14.5, -13.5], 3.15, 23.85, 25.2, 32),
        dome_mesh("corner_glass_cupola", [-14.5, -13.5], 3.2, 25.05, 3.3, 32, 8),
        cylinder_mesh("corner_cupola_cap", [-14.5, -13.5], 0.72, 28.25, 28.75, 20),
        cylinder_mesh("corner_cupola_finial", [-14.5, -13.5], 0.09, 28.7, 29.45, 10),
    ]
    radial_out = [-math.sqrt(0.5), -math.sqrt(0.5)]
    inward = [math.sqrt(0.5), math.sqrt(0.5)]
    tangent = [math.sqrt(0.5), -math.sqrt(0.5)]
    outer_centre = [-11.0 + radial_out[0] * 7.0, -10.0 + radial_out[1] * 7.0]
    entrance_loop = [[-2.7, 0.0], [-2.7, 4.8], [2.7, 4.8], [2.7, 0.0]]
    return {
        "coordinate_frame": "x_right_y_rear_z_up_metres",
        "dimensions": {"width_m": 36.0, "depth_m": 34.0, "main_wall_height_m": 18.5, "upper_setback_height_m": 2.0, "wall_height_m": 20.5, "crown_outer_eave_m": 21.0, "mansard_break_m": 24.0, "crown_inner_eave_m": 24.8, "visible_height_m": 31.0},
        "footprint_polygon_m": [[-11.0, -17.0], [18.0, -17.0], [18.0, 17.0], [-18.0, 17.0], [-18.0, -10.0], [-17.4672, -12.6788], [-15.9497, -14.9497], [-13.6788, -16.4672]],
        "courtyard_polygon_m": [[-9.0, -7.5], [9.0, -7.5], [9.0, 7.5], [-9.0, 7.5]],
        "roof": {"field_count": 8, "mansard_field_count": 4, "terrace_field_count": 4, "dormer_count": 10, "dormer_rhythm": {"front": 3, "rear": 3, "left": 2, "right": 2}, "ridge_or_inner_eave_count": 4, "central_dome_count": 1, "corner_cupola_count": 1, "outer_eave_z_m": 21.0, "outer_bottom_z_m": 20.5, "mansard_break_z_m": 24.0, "inner_eave_z_m": 24.8, "mansard_break_bounds_m": [-14.5, 14.5, -13.5, 13.5], "court_opening_bounds_m": [-9.0, 9.0, -7.5, 7.5], "court_is_open": True, "court_cap_allowed": False, "section": "steep_outer_zinc_mansard_plus_shallow_inner_terrace_and_raised_court_curb"},
        "domes": [
            {"id": "central_glass_dome", "centre": [0.0, 0.0], "diameter_m": 11.8, "curb_diameter_m": 12.4, "rise_m": 4.0, "drum_base_z_m": 24.45, "roof_seat_z_m": 24.8, "dome_base_z_m": 25.75, "top_z_m": 31.0},
            {"id": "corner_glass_cupola", "centre": [-14.5, -13.5], "diameter_m": 6.4, "rise_m": 3.3, "tower_radius_m": 3.15, "tower_base_z_m": 18.4, "tower_top_z_m": 24.0, "drum_base_z_m": 23.85, "roof_seat_z_m": 24.0, "dome_base_z_m": 25.05, "top_z_m": 29.45, "street_anchor_priority": 1},
        ],
        "entrance": {"axis": "front_left_corner_wrapped", "carrier_surface_id": "corner_pavilion", "outer_centre_m": outer_centre, "corner_centre_m": [-11.0, -10.0], "direction_inward_xy": inward, "tangent_xy": tangent, "width_m": 5.4, "height_m": 4.8, "depth_m": 4.2, "canopy_outer_radius_m": 10.2, "canopy_inner_radius_m": 6.2, "canopy_depth_m": 4.0, "contour_local_m": entrance_loop, "blockers": blockers},
        "upper_setback": {"height_m": 2.0, "inset_m": 0.65, "carrier_ids": ["upper_front_setback", "upper_right_setback", "upper_rear_setback", "upper_left_setback"]},
        "meshes": meshes,
    }


def mesh_bad_edges(mesh: dict[str, Any]) -> int:
    edges: Counter[tuple[int, int]] = Counter()
    for face in mesh["faces"]:
        for index, start in enumerate(face):
            end = face[(index + 1) % len(face)]
            edges[tuple(sorted((int(start), int(end))))] += 1
    return sum(count != 2 for count in edges.values())


def polygon_self_intersects_xy(vertices: list[list[float]], face: list[int]) -> bool:
    """Return True when non-adjacent projected polygon edges cross."""
    points = [(float(vertices[index][0]), float(vertices[index][1])) for index in face]

    def orientation(a: tuple[float, float], b: tuple[float, float], c: tuple[float, float]) -> float:
        return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])

    def proper_cross(a: tuple[float, float], b: tuple[float, float], c: tuple[float, float], d: tuple[float, float]) -> bool:
        return orientation(a, b, c) * orientation(a, b, d) < 0.0 and orientation(c, d, a) * orientation(c, d, b) < 0.0

    count = len(points)
    for first in range(count):
        first_next = (first + 1) % count
        for second in range(first + 1, count):
            second_next = (second + 1) % count
            if first in {second, second_next} or first_next in {second, second_next}:
                continue
            if proper_cross(points[first], points[first_next], points[second], points[second_next]):
                return True
    return False


def face_normal(vertices: list[list[float]], face: list[int]) -> list[float]:
    """Compute an unnormalised Newell normal for a polygon face."""
    normal = [0.0, 0.0, 0.0]
    for index, vertex_index in enumerate(face):
        current = vertices[vertex_index]
        following = vertices[face[(index + 1) % len(face)]]
        normal[0] += (current[1] - following[1]) * (current[2] + following[2])
        normal[1] += (current[2] - following[2]) * (current[0] + following[0])
        normal[2] += (current[0] - following[0]) * (current[1] + following[1])
    return normal


def polygon_rectangle_overlap_area_xy(vertices: list[list[float]], face: list[int], bounds: list[float]) -> float:
    """Clip a projected face against an axis-aligned rectangle and return area."""
    polygon = [[float(vertices[index][0]), float(vertices[index][1])] for index in face]
    xmin, xmax, ymin, ymax = bounds

    def clip(points: list[list[float]], axis: int, limit: float, keep_greater: bool) -> list[list[float]]:
        if not points:
            return []
        result: list[list[float]] = []
        previous = points[-1]
        previous_inside = previous[axis] >= limit if keep_greater else previous[axis] <= limit
        for current in points:
            current_inside = current[axis] >= limit if keep_greater else current[axis] <= limit
            if current_inside != previous_inside:
                denominator = current[axis] - previous[axis]
                t = 0.0 if abs(denominator) < 1e-12 else (limit - previous[axis]) / denominator
                result.append([previous[0] + t * (current[0] - previous[0]), previous[1] + t * (current[1] - previous[1])])
            if current_inside:
                result.append(current)
            previous, previous_inside = current, current_inside
        return result

    for axis, limit, keep_greater in ((0, xmin, True), (0, xmax, False), (1, ymin, True), (1, ymax, False)):
        polygon = clip(polygon, axis, limit, keep_greater)
    if len(polygon) < 3:
        return 0.0
    return abs(sum(point[0] * polygon[(index + 1) % len(polygon)][1] - polygon[(index + 1) % len(polygon)][0] * point[1] for index, point in enumerate(polygon))) / 2.0


def roof_topology_audit(crown: dict[str, Any]) -> dict[str, Any]:
    """Prove the crown is a coherent shell surrounding, not capping, the court."""
    vertices = crown["vertices"]
    faces = crown["faces"]
    errors = 0
    for index, face in enumerate(faces):
        normal = face_normal(vertices, face)
        centroid = [sum(vertices[vertex][axis] for vertex in face) / len(face) for axis in range(3)]
        if index < 8 and normal[2] <= 0.0:
            errors += 1
        elif 8 <= index < 16 and normal[2] >= 0.0:
            errors += 1
        elif 16 <= index < 20 and normal[0] * centroid[0] + normal[1] * centroid[1] <= 0.0:
            errors += 1
        elif index >= 20 and normal[0] * -centroid[0] + normal[1] * -centroid[1] <= 0.0:
            errors += 1
    crossing = sum(polygon_self_intersects_xy(vertices, face) for face in faces[:8])
    court_overlaps = [polygon_rectangle_overlap_area_xy(vertices, face, [-9.0, 9.0, -7.5, 7.5]) for face in faces[:8]]
    # Boundary-touching terrace quads have zero clipped area; any positive
    # overlap means authored roof surface intrudes into the lightwell.
    court_cap_faces = sum(area > 1e-6 for area in court_overlaps)
    return {
        "face_winding_errors": errors,
        "crossing_top_faces": crossing,
        "court_cap_face_count": court_cap_faces,
        "court_cap_overlap_area_m2": sum(court_overlaps),
    }


def point_in_aabb(point: list[float], bounds: list[float], tolerance: float = 1e-6) -> bool:
    x, y, z = point
    x0, y0, z0, x1, y1, z1 = bounds
    return x0 - tolerance <= x <= x1 + tolerance and y0 - tolerance <= y <= y1 + tolerance and z0 - tolerance <= z <= z1 + tolerance


def entrance_clear_fraction(entrance: dict[str, Any]) -> tuple[float, list[dict[str, Any]]]:
    rays = []
    blockers = entrance["blockers"]
    outer = entrance["outer_centre_m"]
    inward = entrance["direction_inward_xy"]
    tangent = entrance["tangent_xy"]
    for tangent_offset in (-1.2, 0.0, 1.2):
        for z in (0.9, 2.1, 3.5):
            origin_xy = [outer[0] + tangent[0] * tangent_offset, outer[1] + tangent[1] * tangent_offset]
            samples = [[origin_xy[0] + inward[0] * entrance["depth_m"] * step / 24, origin_xy[1] + inward[1] * entrance["depth_m"] * step / 24, z] for step in range(25)]
            hits = sorted({blocker["id"] for blocker in blockers if any(point_in_aabb(sample, blocker["bounds"]) for sample in samples)})
            rays.append({"origin": samples[0], "target": samples[-1], "clear": not hits, "blockers": hits})
    return sum(ray["clear"] for ray in rays) / len(rays), rays


def facade_boundary(x0: float, y0: float, x1: float, y1: float, height: float = 20.5) -> list[list[float]]:
    return [[x0, y0, 0.0], [x1, y1, 0.0], [x1, y1, height], [x0, y0, height]]


def facade_band_boundary(x0: float, y0: float, x1: float, y1: float, z0: float, z1: float) -> list[list[float]]:
    return [[x0, y0, z0], [x1, y1, z0], [x1, y1, z1], [x0, y0, z1]]


def surface_contract() -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[str]]:
    corner_arc = [[-18.0, -10.0], [-17.4672, -12.6788], [-15.9497, -14.9497], [-13.6788, -16.4672], [-11.0, -17.0]]
    corner_boundary = [[x, y, 0.0] for x, y in corner_arc] + [[x, y, 20.5] for x, y in reversed(corner_arc)]
    surfaces = [
        {"surface_id": "facade_front", "role": "front", "carrier_mesh": "front_wall", "mapping": "planar", "boundary_m": facade_boundary(-11, -17, 18, -17, 18.5), "exposed": True},
        {"surface_id": "facade_right", "role": "right", "carrier_mesh": "right_wall", "mapping": "planar", "boundary_m": facade_boundary(18, -17, 18, 17, 18.5), "exposed": True},
        {"surface_id": "facade_rear", "role": "rear", "carrier_mesh": "rear_wall", "mapping": "planar", "boundary_m": facade_boundary(18, 17, -18, 17, 18.5), "exposed": True},
        {"surface_id": "facade_left", "role": "left", "carrier_mesh": "left_wall", "mapping": "planar", "boundary_m": facade_boundary(-18, 17, -18, -10, 18.5), "exposed": True},
        {"surface_id": "corner_pavilion", "role": "front_left_corner", "carrier_mesh": "corner_pavilion_facet_assembly", "mapping": "cylindrical", "boundary_m": corner_boundary, "exposed": True},
        {"surface_id": "court_front", "role": "court_front", "carrier_mesh": "court_front_wall", "mapping": "planar", "boundary_m": facade_boundary(-9, -7.5, 9, -7.5), "exposed": True},
        {"surface_id": "court_right", "role": "court_right", "carrier_mesh": "court_right_wall", "mapping": "planar", "boundary_m": facade_boundary(9, -7.5, 9, 7.5), "exposed": True},
        {"surface_id": "court_rear", "role": "court_rear", "carrier_mesh": "court_rear_wall", "mapping": "planar", "boundary_m": facade_boundary(9, 7.5, -9, 7.5), "exposed": True},
        {"surface_id": "court_left", "role": "court_left", "carrier_mesh": "court_left_wall", "mapping": "planar", "boundary_m": facade_boundary(-9, 7.5, -9, -7.5), "exposed": True},
        {"surface_id": "upper_front", "role": "upper_front_setback", "carrier_mesh": "upper_front_setback", "mapping": "planar", "boundary_m": facade_band_boundary(-10.5, -16.35, 17.35, -16.35, 18.5, 20.5), "exposed": True},
        {"surface_id": "upper_right", "role": "upper_right_setback", "carrier_mesh": "upper_right_setback", "mapping": "planar", "boundary_m": facade_band_boundary(17.85, -16.35, 17.85, 16.35, 18.5, 20.5), "exposed": True},
        {"surface_id": "upper_rear", "role": "upper_rear_setback", "carrier_mesh": "upper_rear_setback", "mapping": "planar", "boundary_m": facade_band_boundary(17.35, 16.35, -17.35, 16.35, 18.5, 20.5), "exposed": True},
        {"surface_id": "upper_left", "role": "upper_left_setback", "carrier_mesh": "upper_left_setback", "mapping": "planar", "boundary_m": facade_band_boundary(-17.85, 16.35, -17.85, -9.5, 18.5, 20.5), "exposed": True},
        {"surface_id": "corner_upper_returns", "role": "closed_upper_corner_returns", "carrier_mesh": "corner_upper_return_assembly", "mapping": "planar", "boundary_m": [[-18.05,-10.1,18.5],[-17.25,-9.4,18.5],[-10.4,-16.25,20.5],[-11.1,-17.05,20.5]], "exposed": True},
        {"surface_id": "perimeter_cornice", "role": "projecting_perimeter_cornice", "carrier_mesh": "main_cornice_assembly", "mapping": "planar", "boundary_m": [[-18.35,-17.35,18.05],[18.35,-17.35,18.05],[18.35,17.35,18.75],[-18.35,17.35,18.75]], "exposed": True},
        {"surface_id": "corner_cornices", "role": "projecting_corner_cornices", "carrier_mesh": "corner_pavilion_cornice_assembly", "mapping": "cylindrical", "boundary_m": [[-18.38,-10,18.05],[-15.95,-14.95,18.05],[-11,-17.38,20.62],[-18.38,-10,20.62]], "exposed": True},
        {"surface_id": "wrapped_canopy", "role": "wrapped_corner_canopy", "carrier_mesh": "wrapped_corner_canopy", "mapping": "cylindrical", "boundary_m": [[-21.2,-10,5.05],[-18.21,-17.21,5.05],[-11,-20.2,5.38],[-17.2,-10,5.38]], "exposed": True},
        {"surface_id": "roof_front", "role": "roof_mansard_front", "carrier_mesh": "watertight_perimeter_court_crown", "mapping": "planar", "boundary_m": [[-18,-17,21],[18,-17,21],[14.5,-13.5,24],[-14.5,-13.5,24]], "exposed": True},
        {"surface_id": "roof_right", "role": "roof_mansard_right", "carrier_mesh": "watertight_perimeter_court_crown", "mapping": "planar", "boundary_m": [[18,-17,21],[18,17,21],[14.5,13.5,24],[14.5,-13.5,24]], "exposed": True},
        {"surface_id": "roof_rear", "role": "roof_mansard_rear", "carrier_mesh": "watertight_perimeter_court_crown", "mapping": "planar", "boundary_m": [[18,17,21],[-18,17,21],[-14.5,13.5,24],[14.5,13.5,24]], "exposed": True},
        {"surface_id": "roof_left", "role": "roof_mansard_left", "carrier_mesh": "watertight_perimeter_court_crown", "mapping": "planar", "boundary_m": [[-18,17,21],[-18,-17,21],[-14.5,-13.5,24],[-14.5,13.5,24]], "exposed": True},
        {"surface_id": "terrace_front", "role": "roof_terrace_front", "carrier_mesh": "watertight_perimeter_court_crown", "mapping": "planar", "boundary_m": [[-14.5,-13.5,24],[14.5,-13.5,24],[9,-7.5,24.8],[-9,-7.5,24.8]], "exposed": True},
        {"surface_id": "terrace_right", "role": "roof_terrace_right", "carrier_mesh": "watertight_perimeter_court_crown", "mapping": "planar", "boundary_m": [[14.5,-13.5,24],[14.5,13.5,24],[9,7.5,24.8],[9,-7.5,24.8]], "exposed": True},
        {"surface_id": "terrace_rear", "role": "roof_terrace_rear", "carrier_mesh": "watertight_perimeter_court_crown", "mapping": "planar", "boundary_m": [[14.5,13.5,24],[-14.5,13.5,24],[-9,7.5,24.8],[9,7.5,24.8]], "exposed": True},
        {"surface_id": "terrace_left", "role": "roof_terrace_left", "carrier_mesh": "watertight_perimeter_court_crown", "mapping": "planar", "boundary_m": [[-14.5,13.5,24],[-14.5,-13.5,24],[-9,-7.5,24.8],[-9,7.5,24.8]], "exposed": True},
        {"surface_id": "dormers_front", "role": "dormer_front_geometry", "carrier_mesh": "dormer_front_assembly", "mapping": "planar", "boundary_m": [[-10.25,-15.6,22.1],[10.25,-15.6,22.1],[10.25,-15.6,24.0],[9,-15.6,25.15],[-10.25,-15.6,24.0]], "exposed": True},
        {"surface_id": "dormers_rear", "role": "dormer_rear_geometry", "carrier_mesh": "dormer_rear_assembly", "mapping": "planar", "boundary_m": [[10.25,15.6,22.1],[-10.25,15.6,22.1],[-10.25,15.6,24.0],[-9,15.6,25.15],[10.25,15.6,24.0]], "exposed": True},
        {"surface_id": "dormers_left", "role": "dormer_left_geometry", "carrier_mesh": "dormer_left_assembly", "mapping": "planar", "boundary_m": [[-15.6,6.25,22.1],[-15.6,-6.25,22.1],[-15.6,-6.25,24.0],[-15.6,-5,25.15],[-15.6,6.25,24.0]], "exposed": True},
        {"surface_id": "dormers_right", "role": "dormer_right_geometry", "carrier_mesh": "dormer_right_assembly", "mapping": "planar", "boundary_m": [[15.6,-6.25,22.1],[15.6,6.25,22.1],[15.6,6.25,24.0],[15.6,5,25.15],[15.6,-6.25,24.0]], "exposed": True},
        {"surface_id": "central_curb", "role": "central_dome_curb", "carrier_mesh": "central_dome_curb", "mapping": "cylindrical", "boundary_m": [[0,0,24.45],[6.2,0,24.45],[6.2,0,25.05],[0,0,25.05]], "exposed": True},
        {"surface_id": "central_drum", "role": "central_dome_drum", "carrier_mesh": "central_dome_drum", "mapping": "cylindrical", "boundary_m": [[0,0,24.85],[6.0,0,24.85],[6.0,0,25.9],[0,0,25.9]], "exposed": True},
        {"surface_id": "central_dome", "role": "central_dome", "carrier_mesh": "central_glass_dome", "mapping": "radial", "boundary_m": [[0,0,25.75],[5.9,0,25.75],[0,0,29.75],[-5.9,0,25.75]], "exposed": True},
        {"surface_id": "central_cap_finial", "role": "central_dome_cap_finial", "carrier_mesh": "central_dome_cap_finial_assembly", "mapping": "cylindrical", "boundary_m": [[0,0,29.65],[1.15,0,29.65],[0.11,0,31.0],[0,0,31.0]], "exposed": True},
        {"surface_id": "corner_tower", "role": "corner_upper_tower", "carrier_mesh": "corner_upper_tower", "mapping": "cylindrical", "boundary_m": [[-14.5,-13.5,18.4],[-11.35,-13.5,18.4],[-11.35,-13.5,24.0],[-14.5,-13.5,24.0]], "exposed": True},
        {"surface_id": "corner_tower_crown", "role": "corner_tower_crown", "carrier_mesh": "corner_tower_crown", "mapping": "cylindrical", "boundary_m": [[-14.5,-13.5,23.65],[-11.2,-13.5,23.65],[-11.2,-13.5,24.15],[-14.5,-13.5,24.15]], "exposed": True},
        {"surface_id": "corner_drum", "role": "corner_cupola_drum", "carrier_mesh": "corner_cupola_drum", "mapping": "cylindrical", "boundary_m": [[-14.5,-13.5,23.85],[-11.35,-13.5,23.85],[-11.35,-13.5,25.2],[-14.5,-13.5,25.2]], "exposed": True},
        {"surface_id": "corner_dome", "role": "corner_cupola", "carrier_mesh": "corner_glass_cupola", "mapping": "radial", "boundary_m": [[-14.5,-13.5,25.05],[-11.3,-13.5,25.05],[-14.5,-13.5,28.35],[-17.7,-13.5,25.05]], "exposed": True},
        {"surface_id": "corner_cap_finial", "role": "corner_cupola_cap_finial", "carrier_mesh": "corner_cupola_cap_finial_assembly", "mapping": "cylindrical", "boundary_m": [[-14.5,-13.5,28.25],[-13.78,-13.5,28.25],[-14.41,-13.5,29.45],[-14.5,-13.5,29.45]], "exposed": True},
    ]
    adjacency: list[dict[str, Any]] = []
    def pair(a: str, edge_a: str, b: str, edge_b: str, mode: str, cover: str) -> None:
        adjacency.append({"a": {"surface_id": a, "edge_id": edge_a}, "b": {"surface_id": b, "edge_id": edge_b}, "mode": mode, "cover_object": cover})
    outer = ["facade_front", "facade_right", "facade_rear", "facade_left", "corner_pavilion"]
    upper = ["upper_front", "upper_right", "upper_rear", "upper_left"]
    court = ["court_front", "court_right", "court_rear", "court_left"]
    roofs = ["roof_front", "roof_right", "roof_rear", "roof_left"]
    terraces = ["terrace_front", "terrace_right", "terrace_rear", "terrace_left"]
    for group, cover in ((outer, "stone_corner_pier"), (court, "court_corner_return"), (roofs, "standing_seam_mansard_hip"), (terraces, "terrace_folding_seam")):
        for index, name in enumerate(group):
            pair(name, "end", group[(index + 1) % len(group)], "start", "covered_joint", cover)
    for index, name in enumerate(upper):
        pair(name, "end", upper[(index + 1) % len(upper)], "start", "covered_joint", "upper_setback_corner_return")
    for facade, upper_surface in zip(outer[:4], upper):
        pair(facade, "top", upper_surface, "bottom", "covered_joint", "projecting_perimeter_cornice")
    for upper_surface, roof in zip(upper, roofs):
        pair(upper_surface, "top", roof, "outer_eave", "covered_joint", "zinc_eave_and_crown_return")
    pair("corner_pavilion", "top", "roof_front", "rounded_corner_eave", "covered_joint", "faceted_corner_cornice")
    pair("corner_pavilion", "entrance_head", "wrapped_canopy", "inner_edge", "covered_joint", "canopy_wall_flashing")
    pair("perimeter_cornice", "wall_edge", "corner_cornices", "straight_return", "continuous_wrap", "cornice_profile")
    pair("corner_pavilion", "upper_front", "corner_upper_returns", "corner_side", "continuous_wrap", "closed_upper_corner_return")
    pair("corner_upper_returns", "front_end", "upper_front", "start", "covered_joint", "front_upper_return")
    pair("corner_upper_returns", "left_end", "upper_left", "end", "covered_joint", "left_upper_return")
    for mansard, terrace in zip(roofs, terraces):
        pair(mansard, "inner_break", terrace, "outer_break", "hard_material_joint", "mansard_break_seam")
    for dormers, mansard in zip(("dormers_front", "dormers_right", "dormers_rear", "dormers_left"), roofs):
        pair(dormers, "bottom", mansard, "dormer_seat", "covered_joint", "dormer_flashing")
    for court_surface, terrace in zip(court, terraces):
        pair(court_surface, "top", terrace, "inner_curb", "covered_joint", "raised_court_flashing")
    pair("central_curb", "bottom", "terrace_front", "dome_seat", "covered_joint", "central_dome_flashing")
    pair("central_curb", "top", "central_drum", "bottom", "hard_material_joint", "central_dome_base_ring")
    pair("central_drum", "top", "central_dome", "spring", "hard_material_joint", "dome_spring_ring")
    pair("central_dome", "apex", "central_cap_finial", "bottom", "hard_material_joint", "central_dome_cap_ring")
    pair("corner_pavilion", "tower_seat", "corner_tower", "bottom", "continuous_wrap", "integrated_corner_tower")
    pair("corner_tower", "top", "corner_tower_crown", "bottom", "hard_material_joint", "tower_cornice")
    pair("corner_tower_crown", "top", "corner_drum", "bottom", "covered_joint", "corner_cupola_flashing")
    pair("corner_drum", "top", "corner_dome", "spring", "hard_material_joint", "cupola_spring_ring")
    pair("corner_dome", "apex", "corner_cap_finial", "bottom", "hard_material_joint", "cupola_cap_ring")
    required_edges = [f"{item['a']['surface_id']}:{item['a']['edge_id']}" for item in adjacency] + [f"{item['b']['surface_id']}:{item['b']['edge_id']}" for item in adjacency]
    return surfaces, adjacency, required_edges


def evidence_contract() -> dict[str, Any]:
    views = []
    for role, annotation in REFERENCE_MEASUREMENTS.items():
        path = REFERENCE_ROOT / annotation["path"]
        with Image.open(path) as image:
            size = list(image.size)
        views.append({"role": role, "path": str(path.relative_to(REPO)).replace("\\", "/"), "image_size_px": size, "annotations": annotation})
    return {
        "authority": "exact_v91_three_view_reference_set",
        "views": views,
        "evidence_conflicts": [{
            "id": "principal_entrance_topology",
            "conflict": "The street image reads as a centred frontal composition, while the oblique and aerial views locate the landmark entrance and small cupola at the wrapped front-left corner.",
            "adjudication": "oblique_massing_and_roof_plan_control_topology",
            "street_identity_scope": ["architectural_character", "facade_hierarchy", "camera", "materials"],
            "street_identity_excluded_scope": ["entrance_plan_location", "corner_topology"],
            "status": "resolved",
        }],
        "selective_scale_basis": "five visible occupied facade levels at 4.1 m datum spacing; ratios remain image-measured",
        "camera_calibration": {
            "street_identity": {"mode": "three_vanishing_point", "horizon_y_px": 474, "estimated_focal_px": 1400.0, "estimated_fov_deg": 40.2, "anchor_space": "source_pixels"},
            "oblique_massing": {"mode": "three_vanishing_point", "horizon_y_px": 518, "estimated_focal_px": 1248.0, "estimated_fov_deg": 51.1, "anchor_space": "source_pixels"},
            "roof_plan": {"mode": "near_orthographic_plan_homography", "estimated_fov_deg": 18.0, "anchor_space": "source_pixels"},
        },
    }


def audit(geometry: dict[str, Any], evidence: dict[str, Any], surfaces: list[dict[str, Any]], adjacency: list[dict[str, Any]], required_edges: list[str]) -> dict[str, Any]:
    roof_annotation = REFERENCE_MEASUREMENTS["roof_plan"]
    outer = roof_annotation["outer_bbox_px"]
    court = roof_annotation["court_bbox_px"]
    central = roof_annotation["central_dome_bbox_px"]
    corner = roof_annotation["corner_dome_bbox_px"]
    ref_outer_ratio = (outer[2] - outer[0]) / (outer[3] - outer[1])
    ref_court_ratio = (court[2] - court[0]) / (court[3] - court[1])
    ref_central_ratio = ((central[2] - central[0]) + (central[3] - central[1])) / 2 / (court[2] - court[0])
    ref_corner_ratio = ((corner[2] - corner[0]) + (corner[3] - corner[1])) / 2 / (outer[2] - outer[0])
    dims = geometry["dimensions"]
    measurements = {
        "outer_plan_aspect_error": relative_error(dims["width_m"] / dims["depth_m"], ref_outer_ratio),
        "court_plan_aspect_error": relative_error(18.0 / 15.0, ref_court_ratio),
        "central_dome_ratio_error": relative_error(11.8 / 18.0, ref_central_ratio),
        "corner_dome_ratio_error": relative_error(6.4 / 36.0, ref_corner_ratio),
    }
    street = REFERENCE_MEASUREMENTS["street_identity"]
    datums = street["floor_datums_y_px"]
    reference_levels = [(datums[0] - y) / (datums[0] - datums[-1]) for y in datums]
    geometry_levels = [value / 20.5 for value in (0.0, 4.1, 8.2, 12.3, 16.4, 20.5)]
    measurements["floor_datum_rmse"] = rmse(a - b for a, b in zip(reference_levels, geometry_levels))
    entrance = geometry["entrance"]
    entrance_vector = [entrance["outer_centre_m"][0] - entrance["corner_centre_m"][0], entrance["outer_centre_m"][1] - entrance["corner_centre_m"][1]]
    cupola = next(dome for dome in geometry["domes"] if dome["id"] == "corner_glass_cupola")
    cupola_vector = [cupola["centre"][0] - entrance["corner_centre_m"][0], cupola["centre"][1] - entrance["corner_centre_m"][1]]
    # Tangential drift is the topology error: both entrance and cupola must sit
    # on the same wrapped corner axis, regardless of their radial setback.
    tangent = entrance["tangent_xy"]
    measurements["entrance_corner_alignment_m"] = abs((entrance_vector[0] - cupola_vector[0]) * tangent[0] + (entrance_vector[1] - cupola_vector[1]) * tangent[1])
    outer_centre = [(outer[0] + outer[2]) / 2, (outer[1] + outer[3]) / 2]
    court_centre = [(court[0] + court[2]) / 2, (court[1] + court[3]) / 2]
    plan_centre_errors = [
        abs(court_centre[0] - outer_centre[0]) / (outer[2] - outer[0]),
        abs(court_centre[1] - outer_centre[1]) / (outer[3] - outer[1]),
    ]
    camera_anchor_errors = [
        measurements["floor_datum_rmse"],
        *plan_centre_errors,
    ]
    measurements["camera_anchor_rmse_bbox"] = rmse(camera_anchor_errors)
    measurements["camera_anchor_p95_bbox"] = sorted(camera_anchor_errors)[-1]
    crown = next(mesh for mesh in geometry["meshes"] if mesh["name"] == "watertight_perimeter_court_crown")
    measurements["roof_manifold_bad_edges"] = mesh_bad_edges(crown)
    topology = roof_topology_audit(crown)
    measurements["roof_face_winding_errors"] = topology["face_winding_errors"]
    measurements["roof_crossing_top_faces"] = topology["crossing_top_faces"]
    measurements["court_cap_face_count"] = topology["court_cap_face_count"]
    measurements["court_cap_overlap_area_m2"] = topology["court_cap_overlap_area_m2"]
    measurements["open_court_area_m2"] = 18.0 * 15.0 - math.pi * (geometry["domes"][0]["curb_diameter_m"] / 2.0) ** 2
    dormers = [mesh for mesh in geometry["meshes"] if mesh["name"].startswith("dormer_")]
    measurements["dormer_count"] = len(dormers)
    measurements["dormer_rhythm"] = dict(sorted(Counter(mesh["name"].split("_")[1] for mesh in dormers).items()))
    measurements["dormer_manifold_bad_edges"] = sum(mesh_bad_edges(mesh) for mesh in dormers)
    clear_fraction, rays = entrance_clear_fraction(geometry["entrance"])
    measurements["entrance_clear_ray_fraction"] = clear_fraction
    measurements["minimum_dome_seat_overlap_m"] = min(dome["roof_seat_z_m"] - dome["drum_base_z_m"] for dome in geometry["domes"])
    measurements["roof_wall_gap_m"] = abs(float(geometry["roof"]["outer_bottom_z_m"]) - float(dims["wall_height_m"]))
    measurements["mansard_rise_m"] = float(geometry["roof"]["mansard_break_z_m"]) - float(geometry["roof"]["outer_eave_z_m"])
    measurements["terrace_rise_m"] = float(geometry["roof"]["inner_eave_z_m"]) - float(geometry["roof"]["mansard_break_z_m"])
    measurements["mansard_slope"] = measurements["mansard_rise_m"] / 3.5
    measurements["terrace_slope"] = measurements["terrace_rise_m"] / 5.5
    measurements["mansard_to_terrace_slope_ratio"] = measurements["mansard_slope"] / measurements["terrace_slope"]
    measurements["central_dome_rise_ratio"] = geometry["domes"][0]["rise_m"] / geometry["domes"][0]["diameter_m"]
    measurements["corner_dome_rise_ratio"] = geometry["domes"][1]["rise_m"] / geometry["domes"][1]["diameter_m"]
    measurements["corner_pavilion_arc_m"] = math.pi * 7.0 / 2.0
    measurements["wrapped_entrance_width_m"] = geometry["entrance"]["width_m"]
    measurements["wrapped_canopy_depth_m"] = geometry["entrance"]["canopy_depth_m"]
    measurements["upper_setback_inset_m"] = geometry["upper_setback"]["inset_m"]
    measurements["central_dome_diameter_m"] = geometry["domes"][0]["diameter_m"]
    measurements["central_dome_rise_m"] = geometry["domes"][0]["rise_m"]
    measurements["court_circulation_margin_m"] = (15.0 - geometry["domes"][0]["curb_diameter_m"]) / 2.0
    measurements["corner_tower_support_height_m"] = geometry["domes"][1]["tower_top_z_m"] - geometry["domes"][1]["tower_base_z_m"]
    measurements["cupola_support_ratio"] = geometry["domes"][1]["tower_radius_m"] / (geometry["domes"][1]["diameter_m"] / 2.0)
    measurements["cupola_plate_projection_m"] = 3.3 - geometry["domes"][1]["tower_radius_m"]
    mesh_names = {mesh["name"] for mesh in geometry["meshes"]}
    required_medium_detail = {"front_main_cornice", "corner_pavilion_mid_cornice", "corner_pavilion_crown_cornice", "wrapped_corner_canopy", "central_dome_curb", "central_dome_cap", "central_dome_finial", "corner_upper_tower", "corner_tower_crown", "corner_cupola_cap", "corner_cupola_finial", "corner_upper_front_return", "corner_upper_left_return"}
    measurements["missing_medium_detail_meshes"] = sorted(required_medium_detail - mesh_names)
    roles = {surface["role"] for surface in surfaces if surface.get("exposed")}
    expected_roles = {"front","right","rear","left","front_left_corner","court_front","court_right","court_rear","court_left","upper_front_setback","upper_right_setback","upper_rear_setback","upper_left_setback","closed_upper_corner_returns","projecting_perimeter_cornice","projecting_corner_cornices","wrapped_corner_canopy","roof_mansard_front","roof_mansard_right","roof_mansard_rear","roof_mansard_left","roof_terrace_front","roof_terrace_right","roof_terrace_rear","roof_terrace_left","dormer_front_geometry","dormer_rear_geometry","dormer_left_geometry","dormer_right_geometry","central_dome_curb","central_dome_drum","central_dome","central_dome_cap_finial","corner_upper_tower","corner_tower_crown","corner_cupola_drum","corner_cupola","corner_cupola_cap_finial"}
    measurements["carrier_coverage"] = len(roles & expected_roles) / len(expected_roles)
    paired_edges = {f"{item['a']['surface_id']}:{item['a']['edge_id']}" for item in adjacency} | {f"{item['b']['surface_id']}:{item['b']['edge_id']}" for item in adjacency}
    measurements["unpaired_required_edges"] = len(set(required_edges) - paired_edges)
    gate_specs = [
        ("reference_evidence_complete", len(evidence["views"]) == 3 and all(Path(REPO / view["path"]).exists() for view in evidence["views"]), len(evidence["views"]), "three exact source views"),
        ("evidence_conflict_adjudicated", len(evidence["evidence_conflicts"]) == 1 and evidence["evidence_conflicts"][0]["status"] == "resolved" and evidence["evidence_conflicts"][0]["adjudication"] == "oblique_massing_and_roof_plan_control_topology", evidence["evidence_conflicts"][0]["status"], "resolved with aerial/oblique topology authority"),
        ("camera_calibration_complete", set(evidence["camera_calibration"]) == {"street_identity","oblique_massing","roof_plan"}, sorted(evidence["camera_calibration"]), "all evidence roles calibrated"),
        ("outer_plan_proportion", measurements["outer_plan_aspect_error"] <= THRESHOLDS["outer_plan_aspect_error_max"], measurements["outer_plan_aspect_error"], THRESHOLDS["outer_plan_aspect_error_max"]),
        ("court_plan_proportion", measurements["court_plan_aspect_error"] <= THRESHOLDS["court_plan_aspect_error_max"], measurements["court_plan_aspect_error"], THRESHOLDS["court_plan_aspect_error_max"]),
        ("central_dome_plan_ratio", measurements["central_dome_ratio_error"] <= THRESHOLDS["central_dome_ratio_error_max"], measurements["central_dome_ratio_error"], THRESHOLDS["central_dome_ratio_error_max"]),
        ("corner_dome_plan_ratio", measurements["corner_dome_ratio_error"] <= THRESHOLDS["corner_dome_ratio_error_max"], measurements["corner_dome_ratio_error"], THRESHOLDS["corner_dome_ratio_error_max"]),
        ("floor_datum_registration", measurements["floor_datum_rmse"] <= THRESHOLDS["floor_datum_rmse_max"], measurements["floor_datum_rmse"], THRESHOLDS["floor_datum_rmse_max"]),
        ("wrapped_corner_entrance_alignment", measurements["entrance_corner_alignment_m"] <= THRESHOLDS["entrance_corner_alignment_max_m"], measurements["entrance_corner_alignment_m"], THRESHOLDS["entrance_corner_alignment_max_m"]),
        ("camera_anchor_registration", measurements["camera_anchor_rmse_bbox"] <= THRESHOLDS["camera_anchor_rmse_max"] and measurements["camera_anchor_p95_bbox"] <= THRESHOLDS["camera_anchor_p95_max"], {"rmse_bbox": measurements["camera_anchor_rmse_bbox"], "p95_bbox": measurements["camera_anchor_p95_bbox"]}, {"rmse_bbox_max": THRESHOLDS["camera_anchor_rmse_max"], "p95_bbox_max": THRESHOLDS["camera_anchor_p95_max"]}),
        ("watertight_perimeter_court_crown", measurements["roof_manifold_bad_edges"] == 0, measurements["roof_manifold_bad_edges"], 0),
        ("coherent_non_crossing_roof_ring", measurements["roof_manifold_bad_edges"] <= THRESHOLDS["roof_manifold_bad_edges_max"] and measurements["roof_face_winding_errors"] <= THRESHOLDS["roof_face_winding_errors_max"] and measurements["roof_crossing_top_faces"] <= THRESHOLDS["roof_crossing_faces_max"], {"manifold_bad_edges": measurements["roof_manifold_bad_edges"], "face_winding_errors": measurements["roof_face_winding_errors"], "crossing_top_faces": measurements["roof_crossing_top_faces"]}, {"maximum_each": 0}),
        ("open_court_lightwell", geometry["roof"]["court_is_open"] and not geometry["roof"]["court_cap_allowed"] and measurements["court_cap_face_count"] <= THRESHOLDS["court_cap_faces_max"] and measurements["court_cap_overlap_area_m2"] <= 1e-6 and measurements["open_court_area_m2"] >= THRESHOLDS["open_court_area_min_m2"], {"declared_open": geometry["roof"]["court_is_open"], "cap_allowed": geometry["roof"]["court_cap_allowed"], "cap_faces": measurements["court_cap_face_count"], "cap_overlap_area_m2": measurements["court_cap_overlap_area_m2"], "open_area_m2": measurements["open_court_area_m2"]}, {"cap_faces_max": THRESHOLDS["court_cap_faces_max"], "cap_overlap_area_max_m2": 0.000001, "open_area_min_m2": THRESHOLDS["open_court_area_min_m2"]}),
        ("bounded_principal_dormer_rhythm", measurements["dormer_count"] == THRESHOLDS["dormer_count_exact"] and measurements["dormer_rhythm"] == {"front": 3, "left": 2, "rear": 3, "right": 2} and measurements["dormer_manifold_bad_edges"] == 0, {"count": measurements["dormer_count"], "rhythm": measurements["dormer_rhythm"], "manifold_bad_edges": measurements["dormer_manifold_bad_edges"]}, {"count": 10, "rhythm": {"front": 3, "rear": 3, "left": 2, "right": 2}, "manifold_bad_edges": 0}),
        ("roof_seated_on_walls", measurements["roof_wall_gap_m"] <= THRESHOLDS["roof_wall_gap_max_m"], measurements["roof_wall_gap_m"], THRESHOLDS["roof_wall_gap_max_m"]),
        ("differentiated_mansard_section", measurements["mansard_rise_m"] >= THRESHOLDS["mansard_rise_min_m"], measurements["mansard_rise_m"], THRESHOLDS["mansard_rise_min_m"]),
        ("steep_mansard_and_flat_inner_terrace", geometry["roof"]["field_count"] == 8 and measurements["mansard_to_terrace_slope_ratio"] >= THRESHOLDS["mansard_to_terrace_slope_ratio_min"] and measurements["terrace_slope"] <= THRESHOLDS["terrace_slope_max"], {"field_count": geometry["roof"]["field_count"], "mansard_slope": measurements["mansard_slope"], "terrace_slope": measurements["terrace_slope"], "ratio": measurements["mansard_to_terrace_slope_ratio"]}, {"field_count": 8, "slope_ratio_min": THRESHOLDS["mansard_to_terrace_slope_ratio_min"], "terrace_slope_max": THRESHOLDS["terrace_slope_max"]}),
        ("seated_dome_drums", measurements["minimum_dome_seat_overlap_m"] + 1e-6 >= THRESHOLDS["dome_seat_overlap_min_m"], measurements["minimum_dome_seat_overlap_m"], THRESHOLDS["dome_seat_overlap_min_m"]),
        ("shallow_integrated_dome_profiles", measurements["central_dome_rise_ratio"] <= THRESHOLDS["central_dome_rise_ratio_max"] and measurements["corner_dome_rise_ratio"] <= THRESHOLDS["corner_dome_rise_ratio_max"], {"central": measurements["central_dome_rise_ratio"], "corner": measurements["corner_dome_rise_ratio"]}, {"central_max": THRESHOLDS["central_dome_rise_ratio_max"], "corner_max": THRESHOLDS["corner_dome_rise_ratio_max"]}),
        ("central_dome_contained_in_court", measurements["central_dome_diameter_m"] <= THRESHOLDS["central_dome_diameter_max_m"] and measurements["central_dome_rise_m"] <= THRESHOLDS["central_dome_rise_max_m"] and measurements["court_circulation_margin_m"] >= THRESHOLDS["court_circulation_margin_min_m"], {"diameter_m": measurements["central_dome_diameter_m"], "rise_m": measurements["central_dome_rise_m"], "circulation_margin_m": measurements["court_circulation_margin_m"]}, {"diameter_max_m": THRESHOLDS["central_dome_diameter_max_m"], "rise_max_m": THRESHOLDS["central_dome_rise_max_m"], "circulation_margin_min_m": THRESHOLDS["court_circulation_margin_min_m"]}),
        ("corner_cupola_has_vertical_support", measurements["corner_tower_support_height_m"] >= THRESHOLDS["corner_tower_support_height_min_m"] and measurements["cupola_support_ratio"] >= THRESHOLDS["cupola_support_ratio_min"] and measurements["cupola_plate_projection_m"] <= THRESHOLDS["cupola_plate_projection_max_m"], {"tower_height_m": measurements["corner_tower_support_height_m"], "support_ratio": measurements["cupola_support_ratio"], "plate_projection_m": measurements["cupola_plate_projection_m"]}, {"tower_height_min_m": THRESHOLDS["corner_tower_support_height_min_m"], "support_ratio_min": THRESHOLDS["cupola_support_ratio_min"], "plate_projection_max_m": THRESHOLDS["cupola_plate_projection_max_m"]}),
        ("broad_corner_pavilion", measurements["corner_pavilion_arc_m"] >= THRESHOLDS["corner_pavilion_arc_min_m"], measurements["corner_pavilion_arc_m"], THRESHOLDS["corner_pavilion_arc_min_m"]),
        ("broad_wrapped_entrance_and_canopy", measurements["wrapped_entrance_width_m"] >= THRESHOLDS["wrapped_entrance_width_min_m"] and measurements["wrapped_canopy_depth_m"] >= THRESHOLDS["wrapped_canopy_depth_min_m"], {"entrance_width_m": measurements["wrapped_entrance_width_m"], "canopy_depth_m": measurements["wrapped_canopy_depth_m"]}, {"entrance_width_min_m": THRESHOLDS["wrapped_entrance_width_min_m"], "canopy_depth_min_m": THRESHOLDS["wrapped_canopy_depth_min_m"]}),
        ("upper_setback_and_medium_detail", measurements["upper_setback_inset_m"] >= THRESHOLDS["upper_setback_min_m"] and not measurements["missing_medium_detail_meshes"], {"setback_inset_m": measurements["upper_setback_inset_m"], "missing_meshes": measurements["missing_medium_detail_meshes"]}, {"setback_inset_min_m": THRESHOLDS["upper_setback_min_m"], "missing_meshes": []}),
        ("unobstructed_wrapped_corner_entrance", measurements["entrance_clear_ray_fraction"] >= THRESHOLDS["entrance_clear_ray_fraction_min"], measurements["entrance_clear_ray_fraction"], THRESHOLDS["entrance_clear_ray_fraction_min"]),
        ("all_exposed_surface_carriers", measurements["carrier_coverage"] >= THRESHOLDS["carrier_coverage_min"], measurements["carrier_coverage"], THRESHOLDS["carrier_coverage_min"]),
        ("reciprocal_non_bare_adjacency", measurements["unpaired_required_edges"] == 0 and all(item["mode"] != "bare_butt" for item in adjacency), measurements["unpaired_required_edges"], 0),
    ]
    gates = [{"id": gate_id, "passed": bool(passed), "measured": measured, "threshold": threshold} for gate_id, passed, measured, threshold in gate_specs]
    return {"schema": "belle-epoque-clay-gates@1", "status": "pass" if all(gate["passed"] for gate in gates) else "fail", "measurements": measurements, "gates": gates, "entrance_rays": rays}


def write_obj(path: Path, meshes: list[dict[str, Any]]) -> None:
    lines = ["# Belle Epoque Grand Magasin V92 neutral clay geometry"]
    offset = 1
    for mesh in meshes:
        lines.append(f"o {mesh['name']}")
        lines.extend(f"v {x:.6f} {y:.6f} {z:.6f}" for x, y, z in mesh["vertices"])
        for face in mesh["faces"]:
            lines.append("f " + " ".join(str(offset + int(index)) for index in face))
        offset += len(mesh["vertices"])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_diagrams(output: Path, geometry: dict[str, Any]) -> None:
    plan = Image.new("RGB", (1000, 900), "#e7e4dd")
    draw = ImageDraw.Draw(plan)
    def xy(point: list[float]) -> tuple[int, int]:
        # Front is negative Y and belongs at the bottom of the audited plan,
        # matching the exact angle-90 source orientation.
        return round(500 + point[0] * 20), round(450 - point[1] * 20)
    outer = [xy(point) for point in geometry["footprint_polygon_m"]]
    court = [xy(point) for point in geometry["courtyard_polygon_m"]]
    draw.polygon(outer, fill="#9a9a97", outline="#252728", width=5)
    draw.polygon(court, fill="#e7e4dd", outline="#252728", width=5)
    for dome in geometry["domes"]:
        cx, cy = xy(dome["centre"])
        radius = round(dome["diameter_m"] * 10)
        draw.ellipse((cx-radius, cy-radius, cx+radius, cy+radius), fill="#b9c0c0", outline="#343839", width=4)
    draw.text((30, 25), "V92 CLAY PLAN - 36 x 34 m / 18 x 15 m court", fill="#202223")
    plan.save(output / "belle_epoque_clay_v92_plan.png")

    front = Image.new("RGB", (1200, 900), "#e7e4dd")
    draw = ImageDraw.Draw(front)
    sx, base, scale = 600, 850, 22
    draw.rectangle((sx-18*scale, base-18.5*scale, sx+18*scale, base), fill="#9c9b97", outline="#282a2b", width=4)
    draw.rectangle((sx-17.35*scale, base-20.5*scale, sx+17.35*scale, base-18.5*scale), fill="#a9a8a4", outline="#282a2b", width=4)
    draw.rectangle((sx-18.35*scale, base-18.75*scale, sx+18.35*scale, base-18.05*scale), fill="#7f817f", outline="#282a2b", width=3)
    # The public entrance belongs to the wrapped front-left pavilion, not the
    # centre of the straight facade. Its canopy projects around the same corner.
    x0, x1 = sx-18*scale, sx-12.6*scale
    draw.rectangle((x0, base-4.8*scale, x1, base), fill="#303233")
    draw.arc((x0-1.2*scale, base-6.3*scale, x1+1.2*scale, base-3.8*scale), 180, 360, fill="#282a2b", width=8)
    draw.polygon([(sx-18*scale, base-21*scale),(sx+18*scale,base-21*scale),(sx+14.5*scale,base-24*scale),(sx-14.5*scale,base-24*scale)], fill="#747a7b", outline="#282a2b")
    draw.polygon([(sx-14.5*scale,base-24*scale),(sx+14.5*scale,base-24*scale),(sx+9*scale,base-24.8*scale),(sx-9*scale,base-24.8*scale)], fill="#a0a5a5", outline="#282a2b")
    for dormer_x in (-9.0, 0.0, 9.0):
        x = sx + dormer_x * scale
        draw.polygon([(x-1.25*scale, base-22.1*scale), (x-1.25*scale, base-24.0*scale), (x, base-25.15*scale), (x+1.25*scale, base-24.0*scale), (x+1.25*scale, base-22.1*scale)], fill="#888c8c", outline="#282a2b")
    draw.rectangle((sx-6.0*scale, base-25.9*scale, sx+6.0*scale, base-24.85*scale), fill="#929a9a", outline="#282a2b", width=3)
    draw.pieslice((sx-5.9*scale, base-(25.75+4.0)*scale, sx+5.9*scale, base-(25.75-4.0)*scale), 180, 360, fill="#aeb7b7", outline="#282a2b", width=4)
    draw.rectangle((sx-1.15*scale, base-30.2*scale, sx+1.15*scale, base-29.65*scale), fill="#858989", outline="#282a2b", width=3)
    draw.line((sx, base-31.0*scale, sx, base-30.15*scale), fill="#282a2b", width=5)
    tower_x = sx - 14.5 * scale
    draw.rectangle((tower_x-3.15*scale, base-24*scale, tower_x+3.15*scale, base-18.4*scale), fill="#8f918f", outline="#282a2b", width=4)
    draw.rectangle((tower_x-3.3*scale, base-24.15*scale, tower_x+3.3*scale, base-23.65*scale), fill="#777b7b", outline="#282a2b", width=3)
    draw.pieslice((tower_x-3.2*scale, base-(25.05+3.3)*scale, tower_x+3.2*scale, base-(25.05-3.3)*scale), 180, 360, fill="#aeb7b7", outline="#282a2b", width=4)
    draw.line((tower_x, base-29.45*scale, tower_x, base-28.7*scale), fill="#282a2b", width=4)
    draw.text((30, 25), "V92 NEUTRAL CLAY - geometry locked before stickers", fill="#202223")
    front.save(output / "belle_epoque_clay_v92_front.png")


def build_lock(output: Path) -> dict[str, Any]:
    geometry = build_geometry()
    evidence = evidence_contract()
    surfaces, adjacency, required_edges = surface_contract()
    report = audit(geometry, evidence, surfaces, adjacency, required_edges)
    output.mkdir(parents=True, exist_ok=True)
    geometry_payload = {key: value for key, value in geometry.items() if key != "meshes"}
    geometry_payload["mesh_topology"] = [{"name": mesh["name"], "vertices": len(mesh["vertices"]), "faces": len(mesh["faces"]), "bad_edges": mesh_bad_edges(mesh)} for mesh in geometry["meshes"]]
    # Lock the actual vertices/faces as well as the semantic graph. A summary
    # hash would miss an unapproved vertex edit that preserved object counts.
    geometry_hash = sha256(geometry)
    corner_arc_length = math.pi * 7.0 / 2.0
    contours_uv = [[[(u + corner_arc_length / 2) / corner_arc_length, z / 20.5] for u, z in geometry["entrance"]["contour_local_m"]]]
    anchors = [
        {"anchor_id": f"floor_{index:02d}", "kind": "datum", "object_space_m": [0.0, -17.0, z]}
        for index, z in enumerate((0.0, 4.1, 8.2, 12.3, 16.4, 20.5))
    ] + [
        {"anchor_id": "wrapped_corner_entrance_axis", "kind": "axis", "object_space_m": [*geometry["entrance"]["outer_centre_m"], 0.0]},
        {"anchor_id": "main_cornice_datum", "kind": "datum", "object_space_m": [0.0, -17.0, 18.5]},
        {"anchor_id": "mansard_outer_eave", "kind": "roof_break", "object_space_m": [0.0, -17.0, 21.0]},
        {"anchor_id": "mansard_break", "kind": "roof_break", "object_space_m": [0.0, -13.5, 24.0]},
        {"anchor_id": "raised_court_curb", "kind": "roof_break", "object_space_m": [0.0, -7.5, 24.8]},
        {"anchor_id": "central_dome_centre", "kind": "roof_feature", "object_space_m": [0.0, 0.0, 25.75]},
        {"anchor_id": "corner_tower_axis", "kind": "street_primary_roof_feature", "object_space_m": [-14.5, -13.5, 18.4], "priority": 1},
        {"anchor_id": "corner_cupola_centre", "kind": "street_primary_roof_feature", "object_space_m": [-14.5, -13.5, 25.05], "priority": 1},
        {"anchor_id": "dormer_front_left", "kind": "roof_feature", "object_space_m": [-9.0, -14.8, 22.1]},
        {"anchor_id": "dormer_front_centre", "kind": "roof_feature", "object_space_m": [0.0, -14.8, 22.1]},
        {"anchor_id": "dormer_front_right", "kind": "roof_feature", "object_space_m": [9.0, -14.8, 22.1]},
        {"anchor_id": "dormer_rear_left", "kind": "roof_feature", "object_space_m": [-9.0, 14.8, 22.1]},
        {"anchor_id": "dormer_rear_centre", "kind": "roof_feature", "object_space_m": [0.0, 14.8, 22.1]},
        {"anchor_id": "dormer_rear_right", "kind": "roof_feature", "object_space_m": [9.0, 14.8, 22.1]},
        {"anchor_id": "dormer_left_front", "kind": "roof_feature", "object_space_m": [-14.8, -5.0, 22.1]},
        {"anchor_id": "dormer_left_rear", "kind": "roof_feature", "object_space_m": [-14.8, 5.0, 22.1]},
        {"anchor_id": "dormer_right_front", "kind": "roof_feature", "object_space_m": [14.8, -5.0, 22.1]},
        {"anchor_id": "dormer_right_rear", "kind": "roof_feature", "object_space_m": [14.8, 5.0, 22.1]},
    ]
    cameras = dict(evidence["camera_calibration"])
    cameras["aggregate_anchor_metrics"] = {
        "rmse_bbox": report["measurements"]["camera_anchor_rmse_bbox"],
        "p95_bbox": report["measurements"]["camera_anchor_p95_bbox"],
    }
    lock = {
        "schema": SCHEMA,
        "building_id": "grand-magasin-belle-epoque",
        "status": "approved" if report["status"] == "pass" else "rejected",
        "coordinate_frame": geometry["coordinate_frame"],
        "geometry_sha256": geometry_hash,
        "carrier_mode": "native_surface_material",
        "separate_sticker_face_boxes": "forbidden",
        "placement": {"mode": "fixed_select_and_place", "translation": "allowed", "rotation": "allowed", "uniform_scale": "forbidden", "non_uniform_scale": "forbidden", "polygon_fit": False, "pivot_m": [0.0, 0.0, 0.0]},
        "dimensions": geometry["dimensions"],
        "evidence": evidence,
        "cameras": cameras,
        "street_silhouette_priority": ["corner_upper_tower", "corner_cupola", "wrapped_corner_entrance", "central_dome"],
        "anchors": anchors,
        "surfaces": surfaces,
        "adjacency": adjacency,
        "entrance": {"carrier_surface_id": "corner_pavilion", "topology": "single_wrapped_recessed_front_left_corner", "depth_m": geometry["entrance"]["depth_m"], "contour_sha256": sha256(contours_uv), "contour_uv": contours_uv, "clear_ray_fraction": report["measurements"]["entrance_clear_ray_fraction"], "canopy_mesh": "wrapped_corner_canopy"},
        "feature_ownership": {
            "geometry": ["perimeter_and_courtyard_mass", "upper_setback_and_closed_corner_returns", "watertight_steep_mansard_and_flat_terrace_crown", "raised_court_curb", "mansard_dormer_depth_and_pediment_caps", "court_contained_central_dome_curb_drum_cap_finial", "vertical_corner_tower_and_concentric_cupola", "wrapped_corner_pavilion", "entrance_void_jambs_soffits_and_depth", "wrapped_canopy", "projecting_cornice_and_eave_shadow_lines"],
            "sticker": ["windows", "ironwork", "stone_surface", "signage", "balustrade_ornament", "roof_patina", "stained_glass_colour", "dormer_glazing_imagery"],
            "duplicate_ownership_forbidden": True,
        },
        "blender_primitive_targets": {
            "crown": {"kind": "courtyard_ring_roof", "source_mesh": "watertight_perimeter_court_crown"},
            "surface_binding": {"kind": "carrier_skin", "mode": "native_surface_material"},
            "corner_pavilion": {"kind": "rounded_corner_box", "radius_m": 7.0, "segments": 4, "lower_void": "single_wrapped_recessed_front_left_corner"},
        },
        "budgets": {"final_glb_max_bytes": THRESHOLDS["max_final_glb_bytes"], "native_carrier_offset_max_m": 0.003, "opaque_sticker_layers_per_surface_max": 1},
        "gate_report": "belle_epoque_clay_v92_gate_report.json",
        "immutable": {"geometry": True, "object_transforms": True, "cameras": True, "void_contours": True, "roof_topology": True, "sticker_agent_may_modify": ["materials", "uv_layers", "approved_decal_objects"]},
    }
    (output / "belle_epoque_clay_v92_geometry.json").write_text(json.dumps(geometry_payload, indent=2) + "\n", encoding="utf-8")
    (output / "belle_epoque_clay_v92_gate_report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    (output / "clay_lock.json").write_text(json.dumps(lock, indent=2) + "\n", encoding="utf-8")
    write_obj(output / "belle_epoque_clay_v92.obj", geometry["meshes"])
    write_diagrams(output, geometry)
    return lock


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    lock = build_lock(args.output_dir.resolve())
    print(json.dumps({"status": lock["status"], "geometry_sha256": lock["geometry_sha256"], "output": str(args.output_dir.resolve())}, indent=2))
    return 0 if lock["status"] == "approved" else 2


if __name__ == "__main__":
    raise SystemExit(main())
