"""Locked clay geometry for the Brick & Bronze Fins faculty-office V98 pilot.

The exact variant-0 street, oblique and roof views lock five occupied storeys,
a frontage-dominant 3:2 canonical block, a full-height recessed entry slot, a
single broad bronze front projection and a substantial screened rooftop plant court.
Only complete ordinary office bays may be inserted horizontally; depth and
the five-storey vertical stack are immutable.
"""
from __future__ import annotations

import hashlib
import json
import math
from typing import Any


ARCHETYPE_ID = "administrative_faculty_office_building"
VARIANT_ID = "admin_faculty_brick_bronze_fins"
ORDINARY_STACK_M = 3.75
ENTRY_SLOT_M = 5.0
PROJECTING_VOLUME_M = 10.0
SIDE_BAY_M = 5.0
DEPTH_M = 20.0
FLOOR_BANDS = (
    {"level": 0, "role": "tall_transparent_ground", "z_min_m": 0.0, "z_max_m": 4.2},
    {"level": 1, "role": "office", "z_min_m": 4.2, "z_max_m": 7.8},
    {"level": 2, "role": "office", "z_min_m": 7.8, "z_max_m": 11.4},
    {"level": 3, "role": "office", "z_min_m": 11.4, "z_max_m": 15.0},
    {"level": 4, "role": "office_top", "z_min_m": 15.0, "z_max_m": 18.6},
)
SIZE_MATRIX: dict[str, dict[str, float | int]] = {
    "canonical": {"width_m": 30.0, "depth_m": DEPTH_M, "ordinary_front_stacks": 4, "side_bays": 4, "floors": 5},
    # Two complete 3.75 m ordinary front stacks are inserted; slot/projection stay fixed.
    "extended": {"width_m": 37.5, "depth_m": DEPTH_M, "ordinary_front_stacks": 6, "side_bays": 4, "floors": 5},
}
REFERENCE_EVIDENCE = (
    "frontend/public/archetypes/buildings/administrative-faculty-office-building/variant_0.png",
    "frontend/public/archetypes/buildings/administrative-faculty-office-building/variant_0_angle_60.jpg",
    "frontend/public/archetypes/buildings/administrative-faculty-office-building/variant_0_angle_90.jpg",
)


def _hash(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _mesh(name: str, vertices: list[list[float]], faces: list[list[int]], owner: str,
          domain: str, *, face_roles: list[str] | None = None, **metadata: Any) -> dict[str, Any]:
    roles = face_roles or [domain] * len(faces)
    if len(roles) != len(faces):
        raise ValueError(f"{name!r}: face role count does not match face count")
    return {
        "name": name, "vertices": vertices, "faces": faces,
        "face_owners": [[owner] for _ in faces], "sticker_owner_id": owner,
        "material_domain": domain, "face_roles": roles, **metadata,
    }


def _box(name: str, bounds: tuple[float, float, float, float, float, float],
         owner: str, domain: str, **metadata: Any) -> dict[str, Any]:
    x0, x1, y0, y1, z0, z1 = bounds
    vertices = [[x0, y0, z0], [x1, y0, z0], [x1, y1, z0], [x0, y1, z0],
                [x0, y0, z1], [x1, y0, z1], [x1, y1, z1], [x0, y1, z1]]
    faces = [[0, 3, 2, 1], [4, 5, 6, 7], [0, 1, 5, 4],
             [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7]]
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
    vertices = [_point(orientation, u0, inset0, z0, width, depth), _point(orientation, u1, inset0, z0, width, depth),
                _point(orientation, u1, inset1, z0, width, depth), _point(orientation, u0, inset1, z0, width, depth),
                _point(orientation, u0, inset0, z1, width, depth), _point(orientation, u1, inset0, z1, width, depth),
                _point(orientation, u1, inset1, z1, width, depth), _point(orientation, u0, inset1, z1, width, depth)]
    faces = [[0, 3, 2, 1], [4, 5, 6, 7], [0, 1, 5, 4],
             [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7]]
    return _mesh(name, vertices, faces, owner, domain, **metadata)


def _aperture(side: str, bay: int, level: int, width: float, depth: float, *,
              plane_inset: float = 0.0, wall_depth: float = 0.48,
              wall_domain: str = "umber_brick", prefix_tag: str = "ordinary",
              module_width_m: float | None = None, module_u0: float | None = None) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    band = FLOOR_BANDS[level]
    extent = width if side in {"front", "rear"} else depth
    module_width = float(module_width_m or SIDE_BAY_M)
    bay0 = float(module_u0) if module_u0 is not None else -extent / 2 + bay * module_width
    bay1 = bay0 + module_width
    centre = (bay0 + bay1) / 2
    half = min((1.32 if level == 0 else 1.18), module_width * 0.34)
    u0, u1 = centre - half, centre + half
    z0 = float(band["z_min_m"]) + (0.20 if level == 0 else 0.48)
    z1 = float(band["z_max_m"]) - (0.25 if level == 0 else 0.42)
    prefix = f"{side}_{prefix_tag}_bay_{bay:02d}_level_{level}"
    owner = f"sticker_{prefix}_wall"
    meshes = [
        _oriented_box(f"{prefix}_pier_left", side, bay0, u0, float(band["z_min_m"]), float(band["z_max_m"]),
                      plane_inset, plane_inset + wall_depth, width, depth, owner, wall_domain,
                      side=side, bay=bay, level=level, carrier_kind="extruded_wall_bay"),
        _oriented_box(f"{prefix}_pier_right", side, u1, bay1, float(band["z_min_m"]), float(band["z_max_m"]),
                      plane_inset, plane_inset + wall_depth, width, depth, owner, wall_domain,
                      side=side, bay=bay, level=level, carrier_kind="extruded_wall_bay"),
        _oriented_box(f"{prefix}_sill", side, u0, u1, float(band["z_min_m"]), z0,
                      plane_inset, plane_inset + wall_depth, width, depth, owner, wall_domain,
                      side=side, bay=bay, level=level, carrier_kind="extruded_wall_bay"),
        _oriented_box(f"{prefix}_head", side, u0, u1, z1, float(band["z_max_m"]),
                      plane_inset, plane_inset + wall_depth, width, depth, owner, wall_domain,
                      side=side, bay=bay, level=level, carrier_kind="extruded_wall_bay"),
    ]
    glass_inset = plane_inset + wall_depth + 0.18
    returns: list[str] = []
    contour = [[u0, z0], [u1, z0], [u1, z1], [u0, z1]]
    for index, (a, b) in enumerate(zip(contour, contour[1:] + contour[:1])):
        name = f"{prefix}_return_{index}"
        returns.append(name)
        vertices = [_point(side, a[0], plane_inset, a[1], width, depth),
                    _point(side, b[0], plane_inset, b[1], width, depth),
                    _point(side, b[0], glass_inset, b[1], width, depth),
                    _point(side, a[0], glass_inset, a[1], width, depth)]
        meshes.append(_mesh(name, vertices, [[0, 1, 2, 3]], f"sticker_{prefix}_returns",
                            "opening_return", side=side, bay=bay, level=level,
                            carrier_kind="opening_return_tunnel"))
    glass_name = f"{prefix}_recessed_glass"
    meshes.append(_mesh(glass_name, [_point(side, u0, glass_inset, z0, width, depth),
                                    _point(side, u1, glass_inset, z0, width, depth),
                                    _point(side, u1, glass_inset, z1, width, depth),
                                    _point(side, u0, glass_inset, z1, width, depth)], [[0, 1, 2, 3]],
                        f"sticker_{prefix}_glass", "recessed_glazing", side=side, bay=bay, level=level,
                        carrier_kind="recessed_glass"))
    interior_inset = glass_inset + 0.34
    interior_name = f"{prefix}_interior_card"
    meshes.append(_mesh(interior_name, [_point(side, u0 + 0.06, interior_inset, z0 + 0.06, width, depth),
                                       _point(side, u1 - 0.06, interior_inset, z0 + 0.06, width, depth),
                                       _point(side, u1 - 0.06, interior_inset, z1 - 0.06, width, depth),
                                       _point(side, u0 + 0.06, interior_inset, z1 - 0.06, width, depth)], [[0, 1, 2, 3]],
                        f"sticker_{prefix}_interior_card", "interior_card",
                        face_roles=["interior_card"], side=side, bay=bay, level=level,
                        behind_glass_m=0.34, occupied=True, carrier_kind="recessed_interior_card"))
    mullions: list[str] = []
    for index, ratio in enumerate((1 / 3, 2 / 3)):
        u = u0 + (u1 - u0) * ratio
        name = f"{prefix}_vertical_mullion_{index}"
        mullions.append(name)
        meshes.append(_oriented_box(name, side, u - 0.035, u + 0.035, z0 + 0.04, z1 - 0.04,
                                    glass_inset - 0.045, glass_inset - 0.010, width, depth,
                                    f"sticker_{prefix}_mullions", "bronze_mullion", side=side,
                                    bay=bay, level=level, carrier_kind="physical_mullion"))
    z = z0 + (z1 - z0) * 0.52
    name = f"{prefix}_horizontal_mullion"
    mullions.append(name)
    meshes.append(_oriented_box(name, side, u0 + 0.04, u1 - 0.04, z - 0.035, z + 0.035,
                                glass_inset - 0.045, glass_inset - 0.010, width, depth,
                                f"sticker_{prefix}_mullions", "bronze_mullion", side=side,
                                bay=bay, level=level, carrier_kind="physical_mullion"))
    return meshes, {"aperture_id": prefix, "side": side, "bay": bay, "level": level,
                    "kind": "window", "shape": "rectangular", "contour_uz_m": contour,
                    "facade_plane_inset_m": plane_inset, "recess_depth_m": glass_inset - plane_inset,
                    "return_meshes": returns, "recessed_glass_mesh": glass_name,
                    "interior_card_mesh": interior_name,
                    "mullion_meshes": mullions, "flat_printed_void": False}


def _entry_loggia(width: float, depth: float, bay: int, bay0: float) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    bay1 = bay0 + ENTRY_SLOT_M
    u0, u1 = bay0 + 0.36, bay1 - 0.36
    z0, z1, inset = 4.28, 18.32, 1.80
    prefix = "fixed_front_vertical_entry_loggia"
    meshes = [
        _oriented_box(f"{prefix}_left_reveal", "front", bay0, u0, 0.0, 18.6, -0.12, inset,
                      width, depth, "sticker_entry_cream_reveals", "cream_masonry",
                      fixed_identity=True, carrier_kind="deep_loggia_reveal"),
        _oriented_box(f"{prefix}_right_reveal", "front", u1, bay1, 0.0, 18.6, -0.12, inset,
                      width, depth, "sticker_entry_cream_reveals", "cream_masonry",
                      fixed_identity=True, carrier_kind="deep_loggia_reveal"),
        _oriented_box(f"{prefix}_top_reveal", "front", u0, u1, z1, 18.6, -0.12, inset,
                      width, depth, "sticker_entry_cream_reveals", "cream_masonry",
                      fixed_identity=True, carrier_kind="deep_loggia_reveal"),
        _oriented_box(f"{prefix}_ground_soffit", "front", u0, u1, 4.10, z0, -0.12, inset,
                      width, depth, "sticker_entry_cream_reveals", "cream_masonry",
                      fixed_identity=True, carrier_kind="deep_loggia_reveal"),
    ]
    glass_name = f"{prefix}_recessed_curtain_glass"
    meshes.append(_oriented_box(glass_name, "front", u0, u1, z0, z1, inset, inset + 0.035,
                                width, depth, "sticker_entry_curtain_glass", "recessed_glazing",
                                fixed_identity=True, carrier_kind="recessed_glass"))
    entry_interior_cards: list[str] = []
    for band in FLOOR_BANDS[1:]:
        level = int(band["level"])
        card_z0 = max(z0 + 0.08, float(band["z_min_m"]) + 0.08)
        card_z1 = min(z1 - 0.08, float(band["z_max_m"]) - 0.08)
        name = f"{prefix}_interior_card_level_{level}"
        entry_interior_cards.append(name)
        meshes.append(_oriented_box(name, "front", u0 + 0.08, u1 - 0.08, card_z0, card_z1,
                                    inset + 0.38, inset + 0.405, width, depth,
                                    f"sticker_entry_interior_card_level_{level}", "interior_card",
                                    face_roles=["interior_card"] * 6, fixed_identity=True,
                                    side="front", bay=bay, level=level, behind_glass_m=0.345,
                                    occupied=True, carrier_kind="recessed_interior_card"))
    mullions: list[str] = []
    for index, u in enumerate((u0 + (u1 - u0) / 3, u0 + 2 * (u1 - u0) / 3)):
        name = f"{prefix}_vertical_mullion_{index}"
        mullions.append(name)
        meshes.append(_oriented_box(name, "front", u - 0.045, u + 0.045, z0, z1,
                                    inset - 0.055, inset - 0.01, width, depth,
                                    "sticker_entry_bronze_mullions", "bronze_mullion",
                                    fixed_identity=True, carrier_kind="physical_mullion"))
    for level, band in enumerate(FLOOR_BANDS[:-1], start=1):
        z = float(band["z_max_m"])
        name = f"{prefix}_floor_transom_{level}"
        mullions.append(name)
        meshes.append(_oriented_box(name, "front", u0, u1, z - 0.055, z + 0.055,
                                    inset - 0.055, inset - 0.01, width, depth,
                                    "sticker_entry_bronze_mullions", "bronze_mullion",
                                    fixed_identity=True, carrier_kind="physical_mullion"))
    # The exact grade entry is a cavernous lobby threshold: open at the facade,
    # with the physical double doors held at the back of the 1.8 m tunnel.
    tunnel_name = f"{prefix}_open_ground_lobby_tunnel"
    tunnel_contour = [[u0, 0.08], [u1, 0.08], [u1, 4.10], [u0, 4.10]]
    tunnel_returns: list[str] = []
    for index, (a, b) in enumerate(zip(tunnel_contour, tunnel_contour[1:] + tunnel_contour[:1])):
        name = f"{tunnel_name}_return_{index}"
        tunnel_returns.append(name)
        meshes.append(_mesh(name, [_point("front", a[0], -0.12, a[1], width, depth),
                                  _point("front", b[0], -0.12, b[1], width, depth),
                                  _point("front", b[0], inset, b[1], width, depth),
                                  _point("front", a[0], inset, a[1], width, depth)], [[0, 1, 2, 3]],
                            "sticker_entry_ground_tunnel_returns", "opening_return",
                            face_roles=["opening_return"], fixed_identity=True, side="front",
                            bay=bay, level=0, carrier_kind="open_lobby_tunnel_return"))
    door_names: list[str] = []
    centre = (u0 + u1) / 2
    for index, (a, b) in enumerate(((centre - 1.18, centre), (centre, centre + 1.18))):
        name = f"{prefix}_double_door_{index}"
        door_names.append(name)
        meshes.append(_oriented_box(name, "front", a, b, 0.10, 3.25, inset - 0.08, inset,
                                    width, depth, "sticker_entry_double_doors", "bronze_door",
                                    fixed_identity=True, carrier_kind="physical_entry_door"))
    return meshes, {"module_id": prefix, "bay": bay, "full_height_recess_m": inset,
                    "double_height_entry_zone_m": [0.0, 7.8], "curtain_glass_mesh": glass_name,
                    "interior_card_meshes": entry_interior_cards,
                    "mullion_meshes": mullions, "door_meshes": door_names,
                    "ground_lobby_open_at_facade": True, "ground_tunnel_depth_m": inset,
                    "ground_tunnel_return_meshes": tunnel_returns,
                    "flat_printed_void": False, "fixed_identity": True}


def _projecting_bronze_bay(width: float, depth: float, start_u: float, start_bay: int) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    meshes: list[dict[str, Any]] = []
    apertures: list[dict[str, Any]] = []
    plane = -0.90
    for module in range(3):
        bay = start_bay + module
        module_u0 = start_u + module * (PROJECTING_VOLUME_M / 3)
        for level in range(5):
            authored, aperture = _aperture("front", bay, level, width, depth, plane_inset=plane,
                                           wall_depth=0.42, wall_domain="bronze_and_brick_infill",
                                           prefix_tag="projecting_bronze", module_width_m=PROJECTING_VOLUME_M / 3,
                                           module_u0=module_u0)
            meshes.extend(authored)
            aperture["projection_m"] = abs(plane)
            aperture["fixed_identity"] = True
            apertures.append(aperture)
    x0 = start_u
    x1 = x0 + PROJECTING_VOLUME_M
    y0 = -depth / 2 + plane - 0.16
    y1 = -depth / 2 + plane + 0.18
    frame_owner = "sticker_fixed_projecting_bronze_frame"
    meshes.extend([
        _box("fixed_projecting_bronze_left_edge", (x0 - 0.18, x0 + 0.24, y0, y1, 0.42, 18.98),
             frame_owner, "bronze_frame", fixed_identity=True, carrier_kind="projection_edge"),
        _box("fixed_projecting_bronze_right_edge", (x1 - 0.24, x1 + 0.18, y0, y1, 0.42, 18.98),
             frame_owner, "bronze_frame", fixed_identity=True, carrier_kind="projection_edge"),
        _box("fixed_projecting_bronze_top_edge", (x0 - 0.18, x1 + 0.18, y0, y1, 18.55, 18.98),
             frame_owner, "bronze_frame", fixed_identity=True, carrier_kind="projection_edge"),
        _box("fixed_projecting_bronze_base_edge", (x0 - 0.18, x1 + 0.18, y0, y1, 0.38, 0.72),
             frame_owner, "bronze_frame", fixed_identity=True, carrier_kind="projection_edge"),
    ])
    meshes.append(_box("fixed_projecting_bronze_solid_return_cheek",
                       (x1 - 0.72, x1 + 0.10, -depth / 2 - 1.10, -depth / 2 + 0.58, 0.32, 18.92),
                       "sticker_projecting_bronze_solid_return_cheek", "bronze_frame",
                       fixed_identity=True, carrier_kind="solid_projection_return_cheek"))
    for index, band in enumerate(FLOOR_BANDS[:-1]):
        z = float(band["z_max_m"])
        meshes.append(_box(f"fixed_projecting_bronze_slab_band_{index}",
                           (x0, x1, y0 - 0.02, y1 + 0.02, z - 0.13, z + 0.13),
                           "sticker_projecting_bronze_slab_bands", "bronze_slab_band",
                           fixed_identity=True, carrier_kind="slab_band"))
    return meshes, apertures


def _slab_bands(width: float, depth: float) -> list[dict[str, Any]]:
    meshes: list[dict[str, Any]] = []
    for index, band in enumerate(FLOOR_BANDS[:-1]):
        z = float(band["z_max_m"])
        owner = f"sticker_continuous_slab_band_{index}"
        meshes.extend([
            _box(f"slab_band_{index}_left", (-width / 2 - 0.13, -width / 2 + 0.26, -depth / 2, depth / 2,
                                              z - 0.10, z + 0.10), owner, "masonry_slab_band", carrier_kind="slab_band"),
            _box(f"slab_band_{index}_right", (width / 2 - 0.26, width / 2 + 0.13, -depth / 2, depth / 2,
                                               z - 0.10, z + 0.10), owner, "masonry_slab_band", carrier_kind="slab_band"),
            _box(f"slab_band_{index}_rear", (-width / 2, width / 2, depth / 2 - 0.26, depth / 2 + 0.13,
                                              z - 0.10, z + 0.10), owner, "masonry_slab_band", carrier_kind="slab_band"),
        ])
    return meshes


def _roof(width: float, depth: float) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    meshes = [
        _box("fixed_gravel_roof", (-width / 2 + 0.42, width / 2 - 0.42, -depth / 2 + 0.42, depth / 2 - 0.42,
                                    18.64, 18.82), "sticker_roof_gravel", "gravel_roof",
             fixed_identity=True, carrier_kind="roof_deck"),
    ]
    for side, bounds in (
        ("front", (-width / 2 - 0.12, width / 2 + 0.12, -depth / 2 - 0.12, -depth / 2 + 0.42, 18.6, 19.55)),
        ("rear", (-width / 2 - 0.12, width / 2 + 0.12, depth / 2 - 0.42, depth / 2 + 0.12, 18.6, 19.55)),
        ("left", (-width / 2 - 0.12, -width / 2 + 0.42, -depth / 2, depth / 2, 18.6, 19.55)),
        ("right", (width / 2 - 0.42, width / 2 + 0.12, -depth / 2, depth / 2, 18.6, 19.55)),
    ):
        meshes.append(_box(f"fixed_roof_parapet_{side}", bounds, f"sticker_roof_parapet_{side}",
                           "brick_parapet", fixed_identity=True, carrier_kind="roof_parapet"))
    # Exact roof evidence: a substantial compound with orthogonal dividers,
    # producing six addressable plant zones inside one bounded outer court.
    x0, x1, y0, y1 = -7.5, 7.5, -5.0, 5.0
    screen_z0, screen_z1 = 18.82, 20.45
    screens = [
        ("west", (x0, x0 + 0.22, y0, y1)), ("east", (x1 - 0.22, x1, y0, y1)),
        ("south", (x0, x1, y0, y0 + 0.22)), ("north", (x0, x1, y1 - 0.22, y1)),
        ("divider_south", (x0, x1, y0 + (y1 - y0) / 3 - 0.11, y0 + (y1 - y0) / 3 + 0.11)),
        ("divider_north", (x0, x1, y0 + 2 * (y1 - y0) / 3 - 0.11, y0 + 2 * (y1 - y0) / 3 + 0.11)),
        ("divider_vertical", ((x0 + x1) / 2 - 0.11, (x0 + x1) / 2 + 0.11, y0, y1)),
    ]
    screen_names: list[str] = []
    louver_names: list[str] = []
    for label, (sx0, sx1, sy0, sy1) in screens:
        name = f"fixed_mechanical_screen_{label}"
        screen_names.append(name)
        meshes.append(_box(name, (sx0, sx1, sy0, sy1, screen_z0, screen_z1),
                           f"sticker_mechanical_screen_{label}", "bronze_screen",
                           fixed_identity=True, carrier_kind="louver_screen"))
        for index in range(8):
            z = screen_z0 + 0.12 + index * 0.18
            louver = f"{name}_louver_{index}"
            louver_names.append(louver)
            meshes.append(_box(louver, (sx0 - 0.035, sx1 + 0.035, sy0 - 0.035, sy1 + 0.035,
                                        z, z + 0.055), f"sticker_mechanical_louvers_{label}",
                               "bronze_louver", fixed_identity=True, carrier_kind="physical_louver_fin"))
    equipment: list[str] = []
    ducts: list[str] = []
    pipes: list[str] = []
    cell_w = (x1 - x0) / 2
    cell_d = (y1 - y0) / 3
    equipment_bounds: list[tuple[float, float, float, float, float, float]] = []
    for row in range(3):
        for col in range(2):
            cx = x0 + (col + 0.5) * cell_w
            cy = y0 + (row + 0.5) * cell_d
            unit_w = 2.35 + 0.35 * ((row + col) % 2)
            unit_d = 1.20 + 0.30 * ((2 * row + col) % 3)
            unit_h = 0.62 + 0.18 * ((row + 2 * col) % 3)
            lateral = (-0.55 if col == 0 else 0.55) + 0.18 * (row - 1)
            longitudinal = (-0.28, 0.32, -0.10)[row]
            cx += lateral
            cy += longitudinal
            equipment_bounds.append((cx - unit_w / 2, cx + unit_w / 2,
                                     cy - unit_d / 2, cy + unit_d / 2,
                                     18.82, 18.82 + unit_h))
    for index, bounds in enumerate(equipment_bounds):
        name = f"fixed_roof_equipment_{index}"
        equipment.append(name)
        meshes.append(_box(name, bounds, f"sticker_roof_equipment_{index}", "mechanical_equipment",
                           fixed_identity=True, carrier_kind="bounded_roof_equipment"))
    # Low service runs visually link the smaller units while keeping most of
    # every gravel-floored zone exposed. All remain below the screen crown.
    for index, (row, col) in enumerate(((0, 0), (1, 0), (2, 0), (0, 1), (1, 1), (2, 1))):
        bounds = equipment_bounds[index]
        unit_cx = (bounds[0] + bounds[1]) / 2
        unit_cy = (bounds[2] + bounds[3]) / 2
        divider_x = -0.11 if col == 0 else 0.11
        name = f"fixed_roof_low_duct_{index}"
        ducts.append(name)
        meshes.append(_box(name, (min(unit_cx, divider_x), max(unit_cx, divider_x),
                                  unit_cy - 0.16, unit_cy + 0.16, 18.88, 19.12),
                           f"sticker_roof_low_duct_{index}", "mechanical_duct",
                           fixed_identity=True, carrier_kind="bounded_low_mechanical_duct"))
    for index, (y, x_start, x_end) in enumerate(((-3.95, -5.8, -1.0),
                                                  (-0.55, 1.0, 5.8),
                                                  (3.75, -5.6, -1.0))):
        name = f"fixed_roof_low_pipe_{index}"
        pipes.append(name)
        meshes.append(_box(name, (x_start, x_end, y - 0.055, y + 0.055, 18.91, 19.04),
                           f"sticker_roof_low_pipe_{index}", "mechanical_pipe",
                           fixed_identity=True, carrier_kind="bounded_low_mechanical_pipe"))
    return meshes, {"court_parts": 6, "bounds_xy_m": [x0, x1, y0, y1],
                    "screen_meshes": screen_names, "physical_louver_meshes": louver_names,
                    "equipment_meshes": equipment, "low_duct_meshes": ducts,
                    "low_pipe_meshes": pipes, "equipment_bounded_by_court": True,
                    "gravel_clearance_preserved": True}


def build_geometry(size_id: str) -> dict[str, Any]:
    if size_id not in SIZE_MATRIX:
        raise KeyError(f"unsupported administrative faculty V98 size {size_id!r}")
    spec = SIZE_MATRIX[size_id]
    width, depth = float(spec["width_m"]), float(spec["depth_m"])
    ordinary_stacks, side_bays, floors = int(spec["ordinary_front_stacks"]), int(spec["side_bays"]), int(spec["floors"])
    expected_width = ordinary_stacks * ORDINARY_STACK_M + ENTRY_SLOT_M + PROJECTING_VOLUME_M
    if depth != DEPTH_M or floors != 5 or not math.isclose(width, expected_width) or side_bays != 4:
        raise ValueError("V98 locks five floors and 20 m depth; width changes by two complete 3.75 m ordinary stacks")
    meshes: list[dict[str, Any]] = []
    apertures: list[dict[str, Any]] = []
    entry_bay = ordinary_stacks
    projection_start = ordinary_stacks + 1
    front_u = -width / 2
    # Four exact narrow ordinary stacks canonically; two more only in extended.
    for bay in range(ordinary_stacks):
        for level in range(5):
            authored, aperture = _aperture("front", bay, level, width, depth,
                                           module_width_m=ORDINARY_STACK_M,
                                           module_u0=front_u + bay * ORDINARY_STACK_M)
            meshes.extend(authored); apertures.append(aperture)
    entry_u0 = front_u + ordinary_stacks * ORDINARY_STACK_M
    entry_meshes, entry = _entry_loggia(width, depth, entry_bay, entry_u0)
    meshes.extend(entry_meshes)
    projection_u0 = entry_u0 + ENTRY_SLOT_M
    projection_meshes, projection_apertures = _projecting_bronze_bay(width, depth, projection_u0, projection_start)
    meshes.extend(projection_meshes); apertures.extend(projection_apertures)
    rear_bays = int(round(width / SIDE_BAY_M))
    for side, count in (("rear", rear_bays), ("left", side_bays), ("right", side_bays)):
        for bay in range(count):
            for level in range(5):
                # The extended 37.5 m frontage is not divisible by the nominal
                # 5 m return/rear module. Distribute its eight constrained rear
                # bays evenly across the locked width; never let a rounded bay
                # count create a 40 m rear skin behind a 37.5 m building.
                if side == "rear":
                    rear_module = width / count
                    authored, aperture = _aperture(
                        side, bay, level, width, depth,
                        module_width_m=rear_module,
                        module_u0=-width / 2 + bay * rear_module,
                    )
                else:
                    authored, aperture = _aperture(side, bay, level, width, depth)
                meshes.extend(authored)
                aperture["completion_evidence"] = "exact_oblique" if side == "right" else "constrained"
                apertures.append(aperture)
    meshes.extend(_slab_bands(width, depth))
    roof_meshes, mechanical_court = _roof(width, depth)
    meshes.extend(roof_meshes)
    ownership = [{"owner_id": mesh["sticker_owner_id"], "mesh_name": mesh["name"],
                  "face_indices": list(range(len(mesh["faces"]))), "face_count": len(mesh["faces"]),
                  "fallback_material_forbidden": True} for mesh in meshes]
    checked_faces = sum(len(mesh["faces"]) for mesh in meshes)
    geometry: dict[str, Any] = {
        "schema": "administrative-faculty-office-sticker-lego-v98@1",
        "archetype_id": ARCHETYPE_ID, "variant_id": VARIANT_ID, "size_id": size_id,
        "reference_authority": "exact_three_view_images_lock_five_storeys_and_30x20_frontage_dominant_mass",
        "reference_evidence": list(REFERENCE_EVIDENCE),
        "dimensions": {"width_m": width, "depth_m": depth, "occupied_storeys": floors,
                       "wall_top_m": 18.6, "parapet_top_m": 19.55},
        "structural_grid": {"ordinary_front_stack_width_m": ORDINARY_STACK_M,
                            "ordinary_front_stacks": ordinary_stacks, "side_bays": side_bays,
                            "entry_slot_width_m": ENTRY_SLOT_M, "projecting_volume_width_m": PROJECTING_VOLUME_M,
                            "horizontal_growth_unit": "two_complete_ordinary_front_stacks",
                            "vertical_scaling": "forbidden", "depth_scaling": "forbidden"},
        "floor_bands": [dict(band) for band in FLOOR_BANDS],
        "fixed_modules": {"entry_loggias": 1, "entry_bay": entry_bay,
                          "projecting_bronze_bays": 1, "projecting_bronze_window_modules": 3,
                          "projection_start_bay": projection_start,
                          "mechanical_courts": 1, "mechanical_court_parts": 6,
                          "occupied_storeys": 5, "depth_m": DEPTH_M},
        "scalable_modules": {"unit": "pair_of_complete_3.75m_ordinary_office_stacks_left_of_fixed_entry",
                             "canonical_repeatable_stacks": ordinary_stacks,
                             "extended_repeatable_stacks": SIZE_MATRIX["extended"]["ordinary_front_stacks"]},
        "entry_loggia": entry, "mechanical_court": mechanical_court,
        "completion_policy": {"front": "exact", "right": "exact_oblique",
                              "left": "constrained_punched_window_completion",
                              "rear": "constrained_punched_window_completion_no_invented_entry"},
        "carrier_kinds": ["extruded_wall_bay", "opening_return_tunnel", "recessed_glass",
                          "recessed_interior_card",
                          "physical_mullion", "deep_loggia_reveal", "physical_entry_door",
                          "projection_edge", "slab_band", "roof_deck", "roof_parapet",
                          "louver_screen", "physical_louver_fin", "bounded_roof_equipment",
                          "bounded_low_mechanical_duct", "bounded_low_mechanical_pipe"],
        "geometry_hard_stops": [
            "occupied_storeys_must_equal_5", "canonical_footprint_must_equal_30x20",
            "depth_must_equal_20", "entry_loggia_count_must_equal_1",
            "entry_ground_must_remain_open_1.8m_deep_lobby_tunnel",
            "projecting_bronze_front_bays_must_equal_1", "projection_edges_must_remain_physical",
            "projecting_bronze_volume_must_equal_10m_and_three_window_modules",
            "all_windows_require_returns_recessed_glass_interior_cards_and_physical_mullions",
            "roof_must_remain_flat_gravel_behind_parapet", "mechanical_court_parts_must_equal_6",
            "mechanical_screens_require_physical_louvers", "roof_equipment_must_remain_bounded",
            "no_depth_or_vertical_scaling", "growth_requires_two_complete_3.75m_office_stacks",
            "no_invented_rear_entry", "every_visible_face_requires_exactly_one_sticker_owner",
        ],
        "apertures": apertures, "surface_ownership": ownership,
        "surface_audit": {"status": "pass", "checked_faces": checked_faces,
                          "failure_count": 0, "exactly_one_owner_per_face": True},
        "locked_mesh_bundle": {"kind": "locked_mesh_bundle", "mesh_names": [m["name"] for m in meshes],
                               "generic_primitive_assemblies": [],
                               "all_visible_faces_require_exactly_one_sticker_owner": True},
        "meshes": meshes,
    }
    geometry["geometry_sha256"] = _hash(geometry)
    return geometry


if __name__ == "__main__":
    print(json.dumps({size: build_geometry(size)["geometry_sha256"] for size in SIZE_MATRIX}, indent=2))
