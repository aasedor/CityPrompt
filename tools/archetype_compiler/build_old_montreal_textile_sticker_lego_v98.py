"""Locked three-storey geometry for the Old Montreal textile-mill V98 pilot.

The exact variant_2 street, oblique and roof images are authoritative.  They
show three occupied storeys, so the archetype's generic 4--6 floor metadata is
explicitly rejected.  Capacity changes only by inserting complete 5 m facade
bays: canonical is 5x4 bays and extended is 7x4 bays.
"""
from __future__ import annotations

import hashlib
import json
import math
from typing import Any


ARCHETYPE_ID = "old_montreal_warehouse_loft"
VARIANT_ID = "old_mtl_textile_mill"
BAY_M = 5.0
DEPTH_M = 20.0
FLOOR_BANDS = (
    {"role": "ground", "z_min_m": 0.0, "z_max_m": 4.2, "repeatable": False},
    {"role": "middle", "z_min_m": 4.2, "z_max_m": 9.0, "repeatable": False},
    {"role": "top", "z_min_m": 9.0, "z_max_m": 12.9, "repeatable": False},
)
SIZE_MATRIX: dict[str, dict[str, float | int]] = {
    "canonical": {"width_m": 25.0, "depth_m": DEPTH_M, "front_bays": 5, "side_bays": 4, "floors": 3},
    "extended": {"width_m": 35.0, "depth_m": DEPTH_M, "front_bays": 7, "side_bays": 4, "floors": 3},
}
REFERENCE_EVIDENCE = (
    "frontend/public/archetypes/buildings/old-montreal-warehouse-loft/variant_2.png",
    "frontend/public/archetypes/buildings/old-montreal-warehouse-loft/variant_2_angle_60.jpg",
    "frontend/public/archetypes/buildings/old-montreal-warehouse-loft/variant_2_angle_90.jpg",
)


def _hash(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()
    return hashlib.sha256(payload).hexdigest()


def _mesh(name: str, vertices: list[list[float]], faces: list[list[int]], owner: str,
          domain: str, *, face_roles: list[str] | None = None, **metadata: Any) -> dict[str, Any]:
    resolved_face_roles = face_roles or [domain] * len(faces)
    if len(resolved_face_roles) != len(faces):
        raise ValueError(f"locked mesh {name!r} has {len(faces)} faces but {len(resolved_face_roles)} roles")
    return {
        "name": name,
        "vertices": vertices,
        "faces": faces,
        # A list per face makes duplicate/missing ownership mechanically visible.
        "face_owners": [[owner] for _face in faces],
        "sticker_owner_id": owner,
        "material_domain": domain,
        "face_roles": resolved_face_roles,
        **metadata,
    }


def _quad(name: str, vertices: list[list[float]], owner: str, domain: str,
          **metadata: Any) -> dict[str, Any]:
    return _mesh(name, vertices, [[0, 1, 2, 3]], owner, domain, **metadata)


def _box(name: str, bounds: tuple[float, float, float, float, float, float],
         owner: str, domain: str, **metadata: Any) -> dict[str, Any]:
    x0, x1, y0, y1, z0, z1 = bounds
    vertices = [
        [x0, y0, z0], [x1, y0, z0], [x1, y1, z0], [x0, y1, z0],
        [x0, y0, z1], [x1, y0, z1], [x1, y1, z1], [x0, y1, z1],
    ]
    faces = [[0, 3, 2, 1], [4, 5, 6, 7], [0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7]]
    return _mesh(name, vertices, faces, owner, domain, **metadata)


def _cylinder(name: str, centre: tuple[float, float], radius: float, z0: float, z1: float,
              owner: str, domain: str, segments: int = 16, **metadata: Any) -> dict[str, Any]:
    cx, cy = centre
    vertices = [[cx + radius * math.cos(2 * math.pi * index / segments), cy + radius * math.sin(2 * math.pi * index / segments), z]
                for z in (z0, z1) for index in range(segments)]
    vertices.extend([[cx, cy, z0], [cx, cy, z1]])
    faces: list[list[int]] = []
    for index in range(segments):
        nxt = (index + 1) % segments
        faces.extend([[index, nxt, segments + nxt, segments + index], [2 * segments, nxt, index], [2 * segments + 1, segments + index, segments + nxt]])
    return _mesh(name, vertices, faces, owner, domain, **metadata)


def _point(side: str, u: float, inset: float, z: float, width: float, depth: float) -> list[float]:
    if side == "front":
        return [u, -depth / 2 + inset, z]
    if side == "rear":
        return [-u, depth / 2 - inset, z]
    if side == "left":
        return [-width / 2 + inset, -u, z]
    if side == "right":
        return [width / 2 - inset, u, z]
    raise KeyError(side)


def _oriented_box(name: str, orientation: str, u0: float, u1: float, z0: float, z1: float,
                  inset0: float, inset1: float, width: float, depth: float,
                  owner: str, domain: str, **metadata: Any) -> dict[str, Any]:
    vertices = [
        _point(orientation, u0, inset0, z0, width, depth), _point(orientation, u1, inset0, z0, width, depth),
        _point(orientation, u1, inset1, z0, width, depth), _point(orientation, u0, inset1, z0, width, depth),
        _point(orientation, u0, inset0, z1, width, depth), _point(orientation, u1, inset0, z1, width, depth),
        _point(orientation, u1, inset1, z1, width, depth), _point(orientation, u0, inset1, z1, width, depth),
    ]
    faces = [[0, 3, 2, 1], [4, 5, 6, 7], [0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7]]
    return _mesh(name, vertices, faces, owner, domain, **metadata)


def _opening_contour(kind: str, centre_u: float, band: dict[str, Any], width_scale: float = 1.0) -> list[list[float]]:
    z0, z1 = float(band["z_min_m"]), float(band["z_max_m"])
    if kind == "door":
        half = 0.90 * width_scale
        return [[centre_u - half, z0 + 0.06], [centre_u + half, z0 + 0.06],
                [centre_u + half, z0 + 3.72], [centre_u - half, z0 + 3.72]]
    if band["role"] == "ground":
        half = 1.36 * width_scale
        return [[centre_u - half, z0 + 0.18], [centre_u + half, z0 + 0.18],
                [centre_u + half, z1 - 0.16], [centre_u - half, z1 - 0.16]]
    if band["role"] == "top":
        half = 1.22 * width_scale
        return [[centre_u - half, z0 + 0.58], [centre_u + half, z0 + 0.58],
                [centre_u + half, z1 - 0.52], [centre_u - half, z1 - 0.52]]
    # The middle-floor arch is true topology: the wall stops at this contour,
    # with curved masonry above, physical returns and glass 0.34 m behind it.
    half = 1.52 * width_scale
    bottom = z0 + 0.60
    spring = z1 - 0.94
    rise = 0.62
    contour = [[centre_u - half, bottom], [centre_u + half, bottom], [centre_u + half, spring]]
    contour.extend([
        [centre_u + half * math.cos(math.pi * step / 12), spring + rise * math.sin(math.pi * step / 12)]
        for step in range(1, 13)
    ])
    return contour


def _line_intersections(contour: list[list[float]], axis: int, value: float) -> list[float]:
    """Intersect a UZ aperture polygon with a vertical or horizontal line."""
    other = 1 - axis
    hits: list[float] = []
    for start, end in zip(contour, contour[1:] + contour[:1]):
        a, b = start[axis], end[axis]
        if math.isclose(a, b):
            if math.isclose(value, a):
                hits.extend((start[other], end[other]))
            continue
        if min(a, b) - 1e-9 <= value <= max(a, b) + 1e-9:
            ratio = (value - a) / (b - a)
            hits.append(start[other] + ratio * (end[other] - start[other]))
    return sorted(set(round(hit, 10) for hit in hits))


def _window_surface_assembly(prefix: str, side: str, contour: list[list[float]],
                             glass_inset: float, width: float, depth: float,
                             role: str) -> tuple[list[dict[str, Any]], str, list[str]]:
    """Add an interior card and contour-clipped near-black steel sash."""
    meshes: list[dict[str, Any]] = []
    centre_u = (min(point[0] for point in contour) + max(point[0] for point in contour)) / 2
    centre_z = sum(point[1] for point in contour) / len(contour)
    interior_inset = glass_inset + 0.28
    interior_name = f"{prefix}_window_interior_card"
    vertices = [_point(side, centre_u, interior_inset, centre_z, width, depth)] + [
        _point(side, point[0], interior_inset, point[1], width, depth) for point in contour
    ]
    faces = [[0, index + 1, (index + 1) % len(contour) + 1] for index in range(len(contour))]
    meshes.append(_mesh(interior_name, vertices, faces, f"sticker_{prefix}_interior_card", "interior_card",
                        side=side, band_role=role, behind_glass_m=0.28, warm_occupied=True))

    u0, u1 = min(point[0] for point in contour), max(point[0] for point in contour)
    z0, z1 = min(point[1] for point in contour), max(point[1] for point in contour)
    vertical_count = 3 if role == "ground" else 2
    horizontal_count = 2 if role in {"ground", "middle"} else 1
    sash_inset = glass_inset - 0.035
    half = 0.035
    mullions: list[str] = []

    for index in range(1, vertical_count + 1):
        u = u0 + (u1 - u0) * index / (vertical_count + 1)
        left_hits = _line_intersections(contour, 0, u - half)
        right_hits = _line_intersections(contour, 0, u + half)
        if len(left_hits) < 2 or len(right_hits) < 2:
            continue
        low = max(left_hits[0], right_hits[0]) + 0.06
        high = min(left_hits[-1], right_hits[-1]) - 0.06
        if high <= low:
            continue
        name = f"{prefix}_window_mullion_vertical_{index:02d}"
        mullions.append(name)
        meshes.append(_quad(name, [
            _point(side, u - half, sash_inset, low, width, depth),
            _point(side, u + half, sash_inset, low, width, depth),
            _point(side, u + half, sash_inset, high, width, depth),
            _point(side, u - half, sash_inset, high, width, depth),
        ], f"sticker_{prefix}_near_black_steel_sash", "window_mullion",
            face_roles=["near_black_steel_sash"], side=side, band_role=role,
            in_front_of_glass_m=0.035, contour_confined=True))

    for index in range(1, horizontal_count + 1):
        z = z0 + (z1 - z0) * index / (horizontal_count + 1)
        bottom_hits = _line_intersections(contour, 1, z - half)
        top_hits = _line_intersections(contour, 1, z + half)
        if len(bottom_hits) < 2 or len(top_hits) < 2:
            continue
        left = max(bottom_hits[0], top_hits[0]) + 0.06
        right = min(bottom_hits[-1], top_hits[-1]) - 0.06
        if right <= left:
            continue
        name = f"{prefix}_window_mullion_horizontal_{index:02d}"
        mullions.append(name)
        meshes.append(_quad(name, [
            _point(side, left, sash_inset, z - half, width, depth),
            _point(side, right, sash_inset, z - half, width, depth),
            _point(side, right, sash_inset, z + half, width, depth),
            _point(side, left, sash_inset, z + half, width, depth),
        ], f"sticker_{prefix}_near_black_steel_sash", "window_mullion",
            face_roles=["near_black_steel_sash"], side=side, band_role=role,
            in_front_of_glass_m=0.035, contour_confined=True))
    return meshes, interior_name, mullions


def _aperture_bay(side: str, bay: int, bay_count: int, band_index: int,
                  width: float, depth: float, kind: str = "window",
                  opening_profile: str = "ordinary") -> tuple[list[dict[str, Any]], dict[str, Any]]:
    band = FLOOR_BANDS[band_index]
    extent = width if side in {"front", "rear"} else depth
    bay_u0 = -extent / 2 + bay * BAY_M
    bay_u1 = bay_u0 + BAY_M
    centre = (bay_u0 + bay_u1) / 2
    width_scale = 1.0
    if opening_profile == "landmark_corner_storefront" and band["role"] == "ground":
        width_scale = 1.62
    elif opening_profile in {"right_terminal_narrow", "rear_terminal_narrow", "left_terminal_narrow"}:
        width_scale = 0.72
    contour = _opening_contour(kind, centre, band, width_scale)
    opening_u0 = min(point[0] for point in contour)
    opening_u1 = max(point[0] for point in contour)
    opening_z0 = min(point[1] for point in contour)
    opening_z1 = max(point[1] for point in contour)
    role = str(band["role"])
    prefix = f"{side}_bay_{bay:02d}_{role}"
    wall_owner = f"sticker_{prefix}_masonry"
    return_owner = f"sticker_{prefix}_{kind}_returns"
    glass_owner = f"sticker_{prefix}_{kind}_inset"
    apron_by_role = {
        "ground": (0.10, 0.10, 0.10, -0.12, 0.18),
        "middle": (0.20, 0.16, 0.16, -0.20, 0.24),
        "top": (0.12, 0.12, 0.12, -0.14, 0.20),
    }
    apron_drop, apron_rise, apron_overhang, apron_inset0, apron_inset1 = apron_by_role[role]
    meshes = [
        _oriented_box(f"{prefix}_pier_left", side, bay_u0, opening_u0, float(band["z_min_m"]), float(band["z_max_m"]), 0.0, 0.62, width, depth, wall_owner, "occupied_wall", side=side, bay=bay, band_role=role),
        _oriented_box(f"{prefix}_pier_right", side, opening_u1, bay_u1, float(band["z_min_m"]), float(band["z_max_m"]), 0.0, 0.62, width, depth, wall_owner, "occupied_wall", side=side, bay=bay, band_role=role),
        _oriented_box(f"{prefix}_sill_spandrel", side, opening_u0, opening_u1, float(band["z_min_m"]), opening_z0, 0.0, 0.62, width, depth, wall_owner, "occupied_wall", side=side, bay=bay, band_role=role),
        _oriented_box(f"{prefix}_projecting_sill_apron", side, opening_u0 - apron_overhang, opening_u1 + apron_overhang,
                      max(float(band["z_min_m"]), opening_z0 - apron_drop), opening_z0 + apron_rise,
                      apron_inset0, apron_inset1, width, depth, f"sticker_{prefix}_stone_sill_apron", "stone_spandrel",
                      side=side, bay=bay, band_role=role, substantial_apron=role == "middle",
                      apron_profile="deep_framed_middle" if role == "middle" else "slender_cut_stone_sill"),
    ]
    if role != "middle":
        meshes.append(_oriented_box(f"{prefix}_head_spandrel", side, opening_u0, opening_u1, opening_z1, float(band["z_max_m"]), 0.0, 0.62, width, depth, wall_owner, "occupied_wall", side=side, bay=bay, band_role=role))
    else:
        # Each trapezoid fills only the masonry above one curved arch segment.
        arch = contour[2:]
        for index, (start, end) in enumerate(zip(arch, arch[1:])):
            meshes.append(_quad(f"{prefix}_arch_spandrel_{index:02d}", [
                _point(side, start[0], 0.0, start[1], width, depth),
                _point(side, end[0], 0.0, end[1], width, depth),
                _point(side, end[0], 0.0, float(band["z_max_m"]), width, depth),
                _point(side, start[0], 0.0, float(band["z_max_m"]), width, depth),
            ], wall_owner, "occupied_wall", side=side, bay=bay, band_role=role, arch_masonry=True))
        # Projecting stone surround follows the shallow arch; vertical legs and
        # a deeper spandrel frame create the shadow hierarchy seen in the refs.
        meshes.extend([
            _oriented_box(f"{prefix}_surround_left", side, opening_u0 - 0.16, opening_u0 + 0.06, opening_z0 - 0.04, contour[2][1], -0.14, 0.16, width, depth, f"sticker_{prefix}_middle_surround", "stone_surround", side=side, bay=bay, band_role=role),
            _oriented_box(f"{prefix}_surround_right", side, opening_u1 - 0.06, opening_u1 + 0.16, opening_z0 - 0.04, contour[2][1], -0.14, 0.16, width, depth, f"sticker_{prefix}_middle_surround", "stone_surround", side=side, bay=bay, band_role=role),
        ])
        panel_u0, panel_u1 = opening_u0 + 0.22, opening_u1 - 0.22
        panel_z0, panel_z1 = float(band["z_min_m"]) + 0.18, opening_z0 - 0.18
        if panel_z1 > panel_z0:
            frame = 0.12
            meshes.extend([
                _oriented_box(f"{prefix}_deep_spandrel_frame", side, panel_u0, panel_u1, panel_z0, panel_z1,
                              0.08, 0.20, width, depth, f"sticker_{prefix}_middle_spandrel_panel",
                              "stone_spandrel", side=side, bay=bay, band_role=role, recessed_panel=True),
                _oriented_box(f"{prefix}_deep_spandrel_frame_left", side, panel_u0 - frame, panel_u0, panel_z0 - frame, panel_z1 + frame,
                              -0.08, 0.08, width, depth, f"sticker_{prefix}_middle_spandrel_frame",
                              "stone_spandrel", side=side, bay=bay, band_role=role),
                _oriented_box(f"{prefix}_deep_spandrel_frame_right", side, panel_u1, panel_u1 + frame, panel_z0 - frame, panel_z1 + frame,
                              -0.08, 0.08, width, depth, f"sticker_{prefix}_middle_spandrel_frame",
                              "stone_spandrel", side=side, bay=bay, band_role=role),
                _oriented_box(f"{prefix}_deep_spandrel_frame_bottom", side, panel_u0, panel_u1, panel_z0 - frame, panel_z0,
                              -0.08, 0.08, width, depth, f"sticker_{prefix}_middle_spandrel_frame",
                              "stone_spandrel", side=side, bay=bay, band_role=role),
                _oriented_box(f"{prefix}_deep_spandrel_frame_top", side, panel_u0, panel_u1, panel_z1, panel_z1 + frame,
                              -0.08, 0.08, width, depth, f"sticker_{prefix}_middle_spandrel_frame",
                              "stone_spandrel", side=side, bay=bay, band_role=role),
            ])
        arch_points = contour[2:] + [contour[0]]
        spring = contour[2][1]
        half = max(abs(point[0] - centre) for point in arch_points)
        rise = max(point[1] for point in arch_points) - spring
        for index, (start, end) in enumerate(zip(arch_points, arch_points[1:])):
            outer_start = [centre + (start[0] - centre) * (half + 0.20) / half,
                           spring + (start[1] - spring) * (rise + 0.20) / rise]
            outer_end = [centre + (end[0] - centre) * (half + 0.20) / half,
                         spring + (end[1] - spring) * (rise + 0.20) / rise]
            vertices = [
                _point(side, start[0], -0.16, start[1], width, depth),
                _point(side, end[0], -0.16, end[1], width, depth),
                _point(side, outer_end[0], -0.16, outer_end[1], width, depth),
                _point(side, outer_start[0], -0.16, outer_start[1], width, depth),
                _point(side, start[0], 0.16, start[1], width, depth),
                _point(side, end[0], 0.16, end[1], width, depth),
                _point(side, outer_end[0], 0.16, outer_end[1], width, depth),
                _point(side, outer_start[0], 0.16, outer_start[1], width, depth),
            ]
            meshes.append(_mesh(f"{prefix}_surround_arch_{index:02d}", vertices,
                [[0, 1, 2, 3], [4, 7, 6, 5], [0, 4, 5, 1], [1, 5, 6, 2], [2, 6, 7, 3], [3, 7, 4, 0]],
                f"sticker_{prefix}_middle_arch_surround", "stone_surround",
                side=side, bay=bay, band_role=role, projecting_curved_head=True))

    inset = 1.25 if kind == "door" else 0.56
    return_names: list[str] = []
    for index, (start, end) in enumerate(zip(contour, contour[1:] + contour[:1])):
        name = f"{prefix}_{kind}_return_{index:02d}"
        return_names.append(name)
        meshes.append(_quad(name, [
            _point(side, start[0], 0.0, start[1], width, depth),
            _point(side, end[0], 0.0, end[1], width, depth),
            _point(side, end[0], inset, end[1], width, depth),
            _point(side, start[0], inset, start[1], width, depth),
        ], return_owner, "opening_return", side=side, bay=bay, band_role=role, aperture_kind=kind))
    centre_z = sum(point[1] for point in contour) / len(contour)
    pane_vertices = [_point(side, centre, inset, centre_z, width, depth)] + [
        _point(side, point[0], inset, point[1], width, depth) for point in contour
    ]
    pane_faces = [[0, index + 1, (index + 1) % len(contour) + 1] for index in range(len(contour))]
    pane_name = f"{prefix}_{kind}_recessed_back"
    meshes.append(_mesh(pane_name, pane_vertices, pane_faces, glass_owner,
                        "recessed_door" if kind == "door" else "recessed_glazing",
                        side=side, bay=bay, band_role=role, aperture_kind=kind))
    interior_name: str | None = None
    mullion_names: list[str] = []
    if kind == "window":
        assembly, interior_name, mullion_names = _window_surface_assembly(
            prefix, side, contour, inset, width, depth, role,
        )
        meshes.extend(assembly)
    aperture = {
        "aperture_id": f"{prefix}_{kind}", "side": side, "bay": bay,
        "band_role": role, "kind": kind, "shape": "segmental_arch" if role == "middle" else "rectangular",
        "facade_plane_inset_m": 0.0, "recess_depth_m": inset,
        "contour_uz_m": contour, "return_meshes": return_names,
        "recessed_back_mesh": pane_name, "flat_printed_void": False, "opening_profile": opening_profile,
        "physical_glass_mesh": pane_name if kind == "window" else None,
        "interior_card_mesh": interior_name,
        "window_mullion_meshes": mullion_names,
        "door_tunnel_retained": kind == "door",
    }
    return meshes, aperture


def _belt_meshes(width: float, depth: float) -> list[dict[str, Any]]:
    meshes: list[dict[str, Any]] = []
    for label, z0, z1, projection in (
        ("stone_base", 0.00, 0.48, 0.18),
        ("ground_belt", 4.02, 4.38, 0.24),
        ("middle_belt", 8.78, 9.16, 0.26),
        ("cornice", 12.52, 13.22, 0.42),
        ("coping", 13.70, 14.02, 0.48),
    ):
        owner = f"sticker_continuous_stone_{label}"
        meshes.extend([
            _box(f"{label}_front", (-width / 2 - projection, width / 2 + projection, -depth / 2 - projection, -depth / 2 + 0.36, z0, z1), owner, "stone_belt", fixed_identity=True),
            _box(f"{label}_rear", (-width / 2 - projection, width / 2 + projection, depth / 2 - 0.36, depth / 2 + projection, z0, z1), owner, "stone_belt", fixed_identity=True),
            _box(f"{label}_left", (-width / 2 - projection, -width / 2 + 0.36, -depth / 2, depth / 2, z0, z1), owner, "stone_belt", fixed_identity=True),
            _box(f"{label}_right", (width / 2 - 0.36, width / 2 + projection, -depth / 2, depth / 2, z0, z1), owner, "stone_belt", fixed_identity=True),
        ])
    return meshes


def _corner_piers(width: float, depth: float) -> list[dict[str, Any]]:
    meshes: list[dict[str, Any]] = []
    for x_label, x0, x1 in (("left", -width / 2 - 0.06, -width / 2 + 0.78), ("right", width / 2 - 0.78, width / 2 + 0.06)):
        for y_label, y0, y1 in (("front", -depth / 2 - 0.06, -depth / 2 + 0.78), ("rear", depth / 2 - 0.78, depth / 2 + 0.06)):
            meshes.append(_box(f"fixed_corner_pier_{y_label}_{x_label}", (x0, x1, y0, y1, 0.0, 13.22), f"sticker_corner_pier_{y_label}_{x_label}", "masonry_pier", fixed_identity=True))
    return meshes


def _principal_corner_terrace(width: float, depth: float) -> list[dict[str, Any]]:
    """Project the pale-stone street corner and wrap its black top guardrail."""
    x = width / 2
    y = -depth / 2
    owner = "sticker_principal_corner_narrow_stone_pier"
    meshes = [
        _box("fixed_principal_corner_narrow_pier", (x - 0.62, x + 0.54, y - 0.54, y + 0.62, 0.0, 8.82), owner, "principal_corner_stone", fixed_identity=True, projection_m=0.54, pier_width_m=1.16),
        _box("fixed_principal_corner_capital", (x - 0.82, x + 0.68, y - 0.68, y + 0.82, 8.72, 9.10), "sticker_principal_corner_capital", "principal_corner_stone", fixed_identity=True, projection_m=0.68),
        _box("fixed_principal_corner_upper_brick_return", (x - 0.52, x + 0.42, y - 0.42, y + 0.52, 9.20, 13.22), "sticker_principal_corner_upper_brick_return", "masonry_pier", fixed_identity=True, upper_return=True),
    ]
    meshes.append(_box("fixed_principal_corner_corbel", (x - 0.92, x + 0.78, y - 0.78, y + 0.92, 8.58, 8.86), "sticker_principal_corner_corbel", "principal_corner_stone", fixed_identity=True, projection_m=0.78))
    meshes.extend([
        _box("fixed_top_terrace_front_slab", (x - 10.2, x + 0.82, y - 0.92, y + 0.16, 8.76, 9.12), "sticker_top_terrace_front_slab", "terrace_stone", fixed_identity=True, terrace_datum="top_of_middle"),
        _box("fixed_top_terrace_right_slab", (x - 0.16, x + 0.92, y - 0.82, y + 7.7, 8.76, 9.12), "sticker_top_terrace_right_slab", "terrace_stone", fixed_identity=True, terrace_datum="top_of_middle"),
    ])
    for side, start, count in (("front", x - 9.7, 9), ("right", y - 0.5, 7)):
        for index in range(count):
            if side == "front":
                x0 = start + index * 1.25
                bounds = (x0, x0 + 0.06, y - 0.98, y - 0.88, 9.10, 10.12)
            else:
                y0 = start + index * 1.25
                bounds = (x + 0.88, x + 0.98, y0, y0 + 0.06, 9.10, 10.12)
            meshes.append(_box(f"fixed_top_terrace_{side}_rail_post_{index:02d}", bounds, f"sticker_black_guardrail_{side}", "terrace_guardrail", fixed_identity=True))
    meshes.extend([
        _box("fixed_top_terrace_front_rail", (x - 9.7, x + 0.80, y - 1.00, y - 0.86, 10.00, 10.14), "sticker_black_guardrail_front", "terrace_guardrail", fixed_identity=True, rail_on_outer_slab_edge=True),
        _box("fixed_top_terrace_right_rail", (x + 0.86, x + 1.00, y - 0.5, y + 7.7, 10.00, 10.14), "sticker_black_guardrail_right", "terrace_guardrail", fixed_identity=True, rail_on_outer_slab_edge=True),
    ])
    return meshes


def _fixed_far_end_entrance_canopy(width: float, depth: float) -> list[dict[str, Any]]:
    """Protect the source's remote entrance while the principal corner stays glazed."""
    x0, x1 = -width / 2 + 0.45, -width / 2 + 4.55
    y0, y1 = -depth / 2 - 1.05, -depth / 2 + 0.32
    z0, z1 = 3.55, 3.84
    meshes = [
        _box("fixed_far_end_entrance_canopy", (x0, x1, y0, y1, z0, z1), "sticker_far_end_entrance_canopy_all_surfaces", "entrance_canopy", fixed_identity=True),
    ]
    for index, x in enumerate((x0 + 0.28, x1 - 0.28)):
        meshes.append(_box(f"fixed_far_end_canopy_support_{index}", (x - 0.08, x + 0.08, y0 + 0.20, y0 + 0.36, 0.0, z0), f"sticker_far_end_canopy_support_{index}", "entrance_support", fixed_identity=True))
    return meshes


def _roof_monitor(name: str, x0: float, x1: float, y0: float, y1: float, z0: float,
                  bay_segments: int) -> list[dict[str, Any]]:
    mid_y = (y0 + y1) / 2
    curb_top = z0 + 0.62
    ridge_z = z0 + 2.18
    owner = f"sticker_{name}"
    meshes: list[dict[str, Any]] = [
        _box(f"{name}_curb", (x0, x1, y0, y1, z0, curb_top), f"{owner}_metal_curb", "roof_monitor_metal", fixed_identity=True, curb_height_m=0.62),
        _quad(f"{name}_front_glass_plane", [[x0, y0, curb_top], [x1, y0, curb_top], [x1, mid_y, ridge_z], [x0, mid_y, ridge_z]], f"{owner}_front_glass", "roof_monitor_glass", face_roles=["skylight_glass"], fixed_identity=True, continuous_slope=True, pitch_rise_m=1.56),
        _quad(f"{name}_rear_glass_plane", [[x1, y1, curb_top], [x0, y1, curb_top], [x0, mid_y, ridge_z], [x1, mid_y, ridge_z]], f"{owner}_rear_glass", "roof_monitor_glass", face_roles=["skylight_glass"], fixed_identity=True, continuous_slope=True, pitch_rise_m=1.56),
        _box(f"{name}_ridge", (x0 - 0.08, x1 + 0.08, mid_y - 0.07, mid_y + 0.07, ridge_z - 0.07, ridge_z + 0.09), f"{owner}_metal_ridge", "roof_monitor_metal", fixed_identity=True),
    ]
    # Hipped glazed triangular ends close the monitor without boxy end caps.
    meshes.extend([
        _mesh(f"{name}_left_hip_end", [[x0, y0, curb_top], [x0, y1, curb_top], [x0, mid_y, ridge_z]], [[0, 1, 2]], f"{owner}_left_hip_glass", "roof_monitor_glass", face_roles=["skylight_glass"], fixed_identity=True),
        _mesh(f"{name}_right_hip_end", [[x1, y1, curb_top], [x1, y0, curb_top], [x1, mid_y, ridge_z]], [[0, 1, 2]], f"{owner}_right_hip_glass", "roof_monitor_glass", face_roles=["skylight_glass"], fixed_identity=True),
    ])
    for index in range(bay_segments + 1):
        x = x0 + (x1 - x0) * index / bay_segments
        rib_half = 0.025
        meshes.extend([
            _mesh(f"{name}_front_rib_{index:02d}", [[x-rib_half,y0,curb_top+0.015],[x+rib_half,y0,curb_top+0.015],[x+rib_half,mid_y,ridge_z+0.015],[x-rib_half,mid_y,ridge_z+0.015]], [[0,1,2,3]], f"{owner}_metal_ribs", "roof_monitor_metal", face_roles=["slope_following_fine_rib"], fixed_identity=True, rib_width_m=0.05, slope_offset_m=0.015),
            _mesh(f"{name}_rear_rib_{index:02d}", [[x-rib_half,mid_y,ridge_z+0.015],[x+rib_half,mid_y,ridge_z+0.015],[x+rib_half,y1,curb_top+0.015],[x-rib_half,y1,curb_top+0.015]], [[0,1,2,3]], f"{owner}_metal_ribs", "roof_monitor_metal", face_roles=["slope_following_fine_rib"], fixed_identity=True, rib_width_m=0.05, slope_offset_m=0.015),
        ])
    return meshes


def _rear_right_service_step(width: float, depth: float) -> list[dict[str, Any]]:
    """Attach the source-constrained rear-right service mass and roof step."""
    x0, x1 = width / 2 - 5.0, width / 2
    y0, y1 = depth / 2 - 0.9, depth / 2 + 1.65
    meshes = [
        _box("fixed_rear_right_service_volume", (x0, x1, y0, y1, 0.0, 7.6), "sticker_rear_right_service_volume_all_surfaces", "service_volume_wall", fixed_identity=True, footprint_step=True, projection_depth_m=1.65),
        _box("fixed_rear_right_service_cornice", (x0 - 0.16, x1 + 0.16, y0 - 0.16, y1 + 0.16, 7.42, 7.78), "sticker_rear_right_service_cornice", "service_volume_cornice", fixed_identity=True),
        _box("fixed_rear_right_service_roof", (x0 - 0.08, x1 + 0.08, y0 - 0.08, y1 + 0.08, 7.74, 7.88), "sticker_rear_right_service_roof", "subordinate_roof", fixed_identity=True, roof_outline_step=True),
        _box("fixed_rear_right_service_parapet", (x0 - 0.12, x1 + 0.12, y1 - 0.24, y1 + 0.12, 7.70, 8.24), "sticker_rear_right_service_parapet", "subordinate_roof", fixed_identity=True),
    ]
    for level, z in enumerate((1.3, 4.7)):
        for panel in range(3):
            px0 = x0 + 0.45 + panel * 1.35
            meshes.append(_box(f"fixed_rear_right_service_panel_{level}_{panel}", (px0, px0 + 0.90, y1 + 0.01, y1 + 0.10, z, z + 1.45), f"sticker_service_panel_{level}_{panel}", "service_panel_recess", fixed_identity=True))
    return meshes


def _pyramidal_skylight(width: float, roof_z: float) -> list[dict[str, Any]]:
    x0, x1 = -width / 2 + 1.7, -width / 2 + 3.6
    y0, y1 = 5.8, 7.6
    apex = [(x0 + x1) / 2, (y0 + y1) / 2, roof_z + 1.05]
    base_z = roof_z + 0.30
    return [
        _box("fixed_small_pyramidal_skylight_curb", (x0, x1, y0, y1, roof_z, base_z), "sticker_small_pyramidal_skylight_metal", "roof_monitor_metal", fixed_identity=True),
        _mesh("fixed_small_pyramidal_skylight_glass", [[x0, y0, base_z], [x1, y0, base_z], [x1, y1, base_z], [x0, y1, base_z], apex], [[0, 1, 4], [1, 2, 4], [2, 3, 4], [3, 0, 4]], "sticker_small_pyramidal_skylight_glass", "roof_monitor_glass", face_roles=["skylight_glass"] * 4, fixed_identity=True),
    ]


def _roof(width: float, depth: float, front_bays: int) -> list[dict[str, Any]]:
    roof_z = 13.22
    meshes = [
        _box("fixed_flat_roof_deck", (-width / 2, width / 2, -depth / 2, depth / 2, 13.16, roof_z), "sticker_flat_gravel_roof", "main_roof", fixed_identity=True),
        _box("fixed_parapet_front", (-width / 2 - 0.18, width / 2 + 0.18, -depth / 2 - 0.18, -depth / 2 + 0.32, 13.12, 13.92), "sticker_parapet_front_all_surfaces", "roof_parapet", fixed_identity=True),
        _box("fixed_parapet_rear", (-width / 2 - 0.18, width / 2 + 0.18, depth / 2 - 0.32, depth / 2 + 0.18, 13.12, 13.92), "sticker_parapet_rear_all_surfaces", "roof_parapet", fixed_identity=True),
        _box("fixed_parapet_left", (-width / 2 - 0.18, -width / 2 + 0.32, -depth / 2, depth / 2, 13.12, 13.92), "sticker_parapet_left_all_surfaces", "roof_parapet", fixed_identity=True),
        _box("fixed_parapet_right", (width / 2 - 0.32, width / 2 + 0.18, -depth / 2, depth / 2, 13.12, 13.92), "sticker_parapet_right_all_surfaces", "roof_parapet", fixed_identity=True),
    ]
    front_x0, front_x1 = -width / 2 + 3.8, width / 2 - 7.0
    rear_x0, rear_x1 = -width / 2 + 6.2, width / 2 - 2.8
    meshes.extend(_roof_monitor("fixed_long_monitor_front", front_x0, front_x1, -4.8, -2.1, roof_z, max(3, front_bays - 2)))
    meshes.extend(_roof_monitor("fixed_long_monitor_rear", rear_x0, rear_x1, 0.7, 3.7, roof_z, max(4, front_bays - 1)))
    meshes.extend(_pyramidal_skylight(width, roof_z))
    # Asymmetric rear-right service cluster: a curb/mass, multiple housings and vents.
    meshes.extend([
        _box("fixed_service_curb_mass", (width / 2 - 8.2, width / 2 - 0.8, 4.5, 8.7, roof_z, roof_z + 0.42), "sticker_service_curb_mass", "roof_service", fixed_identity=True),
        _box("fixed_hvac_unit_0", (width / 2 - 7.4, width / 2 - 4.8, 5.0, 7.5, roof_z + 0.42, roof_z + 1.75), "sticker_hvac_unit_0_all_surfaces", "roof_service", fixed_identity=True),
        _box("fixed_hvac_unit_1", (width / 2 - 4.4, width / 2 - 2.1, 5.3, 7.2, roof_z + 0.42, roof_z + 1.48), "sticker_hvac_unit_1_all_surfaces", "roof_service", fixed_identity=True),
        _box("fixed_service_plenum", (width / 2 - 3.2, width / 2 - 1.3, 7.3, 8.4, roof_z + 0.42, roof_z + 1.10), "sticker_service_plenum", "roof_service", fixed_identity=True),
        _cylinder("fixed_service_vent_0", (width / 2 - 7.3, 8.0), 0.22, roof_z + 0.42, roof_z + 1.65, "sticker_service_vent_0", "roof_service", fixed_identity=True),
        _cylinder("fixed_service_vent_1", (width / 2 - 6.5, 8.0), 0.18, roof_z + 0.42, roof_z + 1.42, "sticker_service_vent_1", "roof_service", fixed_identity=True),
        _cylinder("fixed_service_pipe_0", (width / 2 - 1.7, 4.9), 0.12, roof_z + 0.42, roof_z + 1.95, "sticker_service_pipe_0", "roof_service", fixed_identity=True),
    ])
    return meshes


def build_geometry(size_id: str) -> dict[str, Any]:
    if size_id not in SIZE_MATRIX:
        raise KeyError(f"unsupported Old Montreal textile-mill V98 size {size_id!r}")
    spec = SIZE_MATRIX[size_id]
    width, depth = float(spec["width_m"]), float(spec["depth_m"])
    front_bays, side_bays = int(spec["front_bays"]), int(spec["side_bays"])
    if width != front_bays * BAY_M or depth != side_bays * BAY_M:
        raise ValueError("V98 permits only complete 5 m horizontal structural bays")
    meshes: list[dict[str, Any]] = []
    apertures: list[dict[str, Any]] = []
    for side, count in (("front", front_bays), ("rear", front_bays), ("left", side_bays), ("right", side_bays)):
        for bay in range(count):
            for band_index, band in enumerate(FLOOR_BANDS):
                kind = "window"
                # The principal front-right corner is fully glazed. One fixed
                # deep public entrance sits at the remote front end; secondary
                # service doors differ on rear and left elevations.
                if band_index == 0 and ((side == "front" and bay == 0) or (side == "rear" and bay == count - 2) or (side == "left" and bay == count - 1)):
                    kind = "door"
                opening_profile = "ordinary"
                if side == "front" and bay == count - 1:
                    opening_profile = "landmark_corner_storefront" if band_index == 0 else "ordinary"
                elif side == "right" and bay == 0:
                    opening_profile = "landmark_corner_storefront" if band_index == 0 else "ordinary"
                elif side == "right" and bay == count - 1:
                    opening_profile = "right_terminal_narrow"
                elif side == "rear" and bay in {0, count - 1}:
                    opening_profile = "rear_terminal_narrow"
                elif side == "left" and bay in {0, count - 1}:
                    opening_profile = "left_terminal_narrow"
                authored, aperture = _aperture_bay(side, bay, count, band_index, width, depth, kind, opening_profile)
                meshes.extend(authored)
                aperture["bay_role"] = "fixed_left_end" if bay == 0 else "fixed_right_end" if bay == count - 1 else "repeatable_middle"
                apertures.append(aperture)
    meshes.extend(_belt_meshes(width, depth))
    meshes.extend(_corner_piers(width, depth))
    meshes.extend(_principal_corner_terrace(width, depth))
    meshes.extend(_fixed_far_end_entrance_canopy(width, depth))
    meshes.extend(_rear_right_service_step(width, depth))
    meshes.extend(_roof(width, depth, front_bays))
    ownership = [{
        "owner_id": mesh["sticker_owner_id"], "mesh_name": mesh["name"],
        "face_indices": list(range(len(mesh["faces"]))), "face_count": len(mesh["faces"]),
        "fallback_material_forbidden": True,
    } for mesh in meshes]
    geometry: dict[str, Any] = {
        "schema": "old-montreal-textile-sticker-lego-v98@1",
        "archetype_id": ARCHETYPE_ID,
        "variant_id": VARIANT_ID,
        "size_id": size_id,
        "reference_authority": "exact_three_view_images_override_conflicting_4_to_6_floor_metadata",
        "reference_evidence": list(REFERENCE_EVIDENCE),
        "dimensions": {"width_m": width, "depth_m": depth, "occupied_storeys": 3, "wall_top_m": 12.9, "parapet_top_m": 13.92},
        "structural_grid": {"bay_width_m": BAY_M, "front_bays": front_bays, "side_bays": side_bays, "horizontal_whole_bay_expansion_only": True, "vertical_scaling": "forbidden"},
        "floor_bands": [dict(band) for band in FLOOR_BANDS],
        "fixed_modules": {"ground_band": 1, "middle_band": 1, "top_band": 1, "corner_piers": 4, "principal_corner_stack": 1, "wraparound_top_terrace": 1, "long_roof_monitors": 2, "pyramidal_skylights": 1, "service_clusters": 1, "rear_right_service_volumes": 1, "hvac_units": 2, "far_end_entrances": 1},
        "elevation_end_conditions": {"front": "far_left_public_entrance_and_glazed_principal_right_corner", "right": "glazed_principal_corner_no_ground_door", "rear": "offset_service_door_near_far_end", "left": "far_rear_service_door"},
        "repeatable_middle_front_bays": front_bays - 2,
        "apertures": apertures,
        "surface_ownership": ownership,
        "locked_mesh_bundle": {"kind": "locked_mesh_bundle", "mesh_names": [mesh["name"] for mesh in meshes], "generic_primitive_assemblies": [], "all_visible_faces_require_exactly_one_sticker_owner": True},
        "meshes": meshes,
    }
    geometry["geometry_sha256"] = _hash(geometry)
    return geometry


if __name__ == "__main__":
    print(json.dumps({size: build_geometry(size)["geometry_sha256"] for size in SIZE_MATRIX}, indent=2))
