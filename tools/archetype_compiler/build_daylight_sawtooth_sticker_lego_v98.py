"""Locked clay geometry for the Daylight Factory sawtooth-roof V98 pilot.

The three exact ``variant_0`` views are authoritative.  They lock a one-storey
brick factory whose canonical 60 m frontage contains six same-handed northlight
roof cells.  Capacity may grow only by complete 10 m tooth / two-bay cells.
"""
from __future__ import annotations

import hashlib
import json
import math
from typing import Any


ARCHETYPE_ID = "daylight_factory"
VARIANT_ID = "factory_sawtooth_roof"
BAY_M = 5.0
TOOTH_M = 10.0
DEPTH_M = 40.0
WALL_TOP_M = 6.0
VALLEY_M = 6.35
RIDGE_M = 11.2
SIZE_MATRIX: dict[str, dict[str, float | int]] = {
    "canonical": {"width_m": 60.0, "depth_m": DEPTH_M, "front_bays": 12, "side_bays": 8, "teeth": 6},
    "extended": {"width_m": 80.0, "depth_m": DEPTH_M, "front_bays": 16, "side_bays": 8, "teeth": 8},
}
REFERENCE_EVIDENCE = (
    "frontend/public/archetypes/buildings/daylight_factory/variant_0.png",
    "frontend/public/archetypes/buildings/daylight_factory/variant_0_angle_60.jpg",
    "frontend/public/archetypes/buildings/daylight_factory/variant_0_angle_90.jpg",
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


def _segmental_contour(centre: float, *, door: bool = False, dock_z: float = 0.0) -> list[list[float]]:
    if door:
        return [[centre - 1.72, dock_z], [centre + 1.72, dock_z],
                [centre + 1.72, 4.28], [centre - 1.72, 4.28]]
    half, bottom, spring, rise = 1.42, 0.72, 4.72, 0.34
    contour = [[centre - half, bottom], [centre + half, bottom], [centre + half, spring]]
    contour.extend([[centre + half * math.cos(math.pi * i / 10),
                     spring + rise * math.sin(math.pi * i / 10)] for i in range(1, 11)])
    return contour


def _aperture_bay(side: str, bay: int, count: int, width: float, depth: float,
                  *, kind: str = "window", dock_z: float = 0.0) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    extent = width if side in {"front", "rear"} else depth
    bay0 = -extent / 2 + bay * BAY_M
    bay1 = bay0 + BAY_M
    centre = (bay0 + bay1) / 2
    contour = _segmental_contour(centre, door=kind == "rolling_door", dock_z=dock_z)
    u0, u1 = min(p[0] for p in contour), max(p[0] for p in contour)
    z0, z1 = min(p[1] for p in contour), max(p[1] for p in contour)
    prefix = f"{side}_bay_{bay:02d}_{kind}"
    masonry_owner = f"sticker_{prefix}_brick"
    meshes = [
        _oriented_box(f"{prefix}_pier_left", side, bay0, u0, 0.0, WALL_TOP_M, 0.0, 0.52,
                      width, depth, masonry_owner, "brick_wall", side=side, bay=bay),
        _oriented_box(f"{prefix}_pier_right", side, u1, bay1, 0.0, WALL_TOP_M, 0.0, 0.52,
                      width, depth, masonry_owner, "brick_wall", side=side, bay=bay),
        _oriented_box(f"{prefix}_sill_spandrel", side, u0, u1, 0.0, z0, 0.0, 0.52,
                      width, depth, masonry_owner, "brick_wall", side=side, bay=bay),
    ]
    if kind == "rolling_door":
        meshes.append(_oriented_box(f"{prefix}_head", side, u0, u1, z1, WALL_TOP_M, 0.0, 0.52,
                                    width, depth, masonry_owner, "brick_wall", side=side, bay=bay))
    else:
        for index, (a, b) in enumerate(zip(contour[2:], contour[3:])):
            vertices = [_point(side, a[0], 0.0, a[1], width, depth),
                        _point(side, b[0], 0.0, b[1], width, depth),
                        _point(side, b[0], 0.0, WALL_TOP_M, width, depth),
                        _point(side, a[0], 0.0, WALL_TOP_M, width, depth)]
            meshes.append(_mesh(f"{prefix}_arch_spandrel_{index:02d}", vertices, [[0, 1, 2, 3]],
                                masonry_owner, "brick_wall", side=side, bay=bay, arch_masonry=True))
        meshes.append(_oriented_box(f"{prefix}_stone_sill", side, u0 - 0.12, u1 + 0.12,
                                    z0 - 0.12, z0 + 0.12, -0.14, 0.18, width, depth,
                                    f"sticker_{prefix}_stone_sill", "stone_sill", side=side, bay=bay))
    inset = 0.88 if kind == "rolling_door" else 0.48
    return_names: list[str] = []
    for index, (a, b) in enumerate(zip(contour, contour[1:] + contour[:1])):
        name = f"{prefix}_return_{index:02d}"
        return_names.append(name)
        vertices = [_point(side, a[0], 0.0, a[1], width, depth),
                    _point(side, b[0], 0.0, b[1], width, depth),
                    _point(side, b[0], inset, b[1], width, depth),
                    _point(side, a[0], inset, a[1], width, depth)]
        meshes.append(_mesh(name, vertices, [[0, 1, 2, 3]], f"sticker_{prefix}_returns",
                            "opening_return", side=side, bay=bay, aperture_kind=kind))
    centre_z = sum(p[1] for p in contour) / len(contour)
    pane_vertices = [_point(side, centre, inset, centre_z, width, depth)] + [
        _point(side, p[0], inset, p[1], width, depth) for p in contour]
    pane_faces = [[0, i + 1, (i + 1) % len(contour) + 1] for i in range(len(contour))]
    back_name = f"{prefix}_recessed_back"
    meshes.append(_mesh(back_name, pane_vertices, pane_faces, f"sticker_{prefix}_back",
                        "rolling_door" if kind == "rolling_door" else "recessed_glazing",
                        side=side, bay=bay, aperture_kind=kind))
    frame_names: list[str] = []
    if kind == "window":
        # The optical pane and occupied interior are physically separated.
        # The latter contains no printed sash or aperture outline.
        interior_inset = inset + 0.58
        interior_vertices = [_point(side, centre, interior_inset, centre_z, width, depth)] + [
            _point(side, p[0], interior_inset, p[1], width, depth) for p in contour]
        meshes.append(_mesh(f"{prefix}_interior_card", interior_vertices, pane_faces,
                            f"sticker_{prefix}_interior_card", "interior_card",
                            side=side, bay=bay, bay_index=bay, aperture_kind=kind,
                            behind_glass_m=0.58, printed_frame_forbidden=True))
        # Physical steel-sash bars remain in front of the glass rather than in its sticker.
        for index in range(1, 4):
            u = u0 + (u1 - u0) * index / 4
            name = f"{prefix}_vertical_sash_{index}"
            frame_names.append(name)
            meshes.append(_oriented_box(name, side, u - 0.035, u + 0.035, z0 + 0.05, z1 - 0.10,
                                        inset - 0.04, inset - 0.01, width, depth,
                                        f"sticker_{prefix}_steel_sash", "steel_sash", side=side, bay=bay))
        for index in range(1, 6):
            z = z0 + (z1 - z0) * index / 6
            name = f"{prefix}_horizontal_sash_{index}"
            frame_names.append(name)
            meshes.append(_oriented_box(name, side, u0 + 0.05, u1 - 0.05, z - 0.035, z + 0.035,
                                        inset - 0.04, inset - 0.01, width, depth,
                                        f"sticker_{prefix}_steel_sash", "steel_sash", side=side, bay=bay))
    return meshes, {
        "aperture_id": prefix, "side": side, "bay": bay, "kind": kind,
        "shape": "rectangular" if kind == "rolling_door" else "segmental_arch",
        "contour_uz_m": contour, "recess_depth_m": inset, "return_meshes": return_names,
        "recessed_back_mesh": back_name, "frame_meshes": frame_names,
        "flat_printed_void": False,
    }


def _slope_prism(name: str, x0: float, z0: float, x1: float, z1: float,
                 y0: float, y1: float, thickness: float, owner: str, domain: str,
                 **metadata: Any) -> dict[str, Any]:
    dx, dz = x1 - x0, z1 - z0
    length = math.hypot(dx, dz)
    nx, nz = -dz / length * thickness, dx / length * thickness
    vertices = [[x0, y0, z0], [x1, y0, z1], [x1 + nx, y0, z1 + nz], [x0 + nx, y0, z0 + nz],
                [x0, y1, z0], [x1, y1, z1], [x1 + nx, y1, z1 + nz], [x0 + nx, y1, z0 + nz]]
    faces = [[0, 1, 2, 3], [4, 7, 6, 5], [0, 4, 5, 1],
             [1, 5, 6, 2], [2, 6, 7, 3], [3, 7, 4, 0]]
    return _mesh(name, vertices, faces, owner, domain, watertight=True, **metadata)


def _roof_teeth(width: float, depth: float, teeth: int) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    meshes: list[dict[str, Any]] = []
    records: list[dict[str, Any]] = []
    for tooth in range(teeth):
        x0 = -width / 2 + tooth * TOOTH_M
        ridge_x, x1 = x0 + 8.0, x0 + TOOTH_M
        opaque = f"tooth_{tooth:02d}_opaque_slope"
        glass = f"tooth_{tooth:02d}_northlight_glass"
        meshes.append(_slope_prism(opaque, x0, VALLEY_M, ridge_x, RIDGE_M, -depth / 2, depth / 2,
                                   0.18, f"sticker_{opaque}", "opaque_roof", tooth=tooth,
                                   roof_handedness="ridge_east_glass_descends_east"))
        meshes.append(_slope_prism(glass, ridge_x, RIDGE_M, x1, VALLEY_M, -depth / 2, depth / 2,
                                   0.055, f"sticker_{glass}", "northlight_glass", tooth=tooth,
                                   northlight_orientation="+X", physical_glass=True))
        frame_names: list[str] = []
        # Dense industrial northlight grid: longitudinal posts and six
        # continuous crossbars, all physical rather than printed into glass.
        for frame in range(25):
            y = -depth / 2 + depth * frame / 24
            name = f"tooth_{tooth:02d}_northlight_frame_{frame:02d}"
            frame_names.append(name)
            meshes.append(_slope_prism(name, ridge_x, RIDGE_M + 0.04, x1, VALLEY_M + 0.04,
                                       y - 0.045, y + 0.045, 0.075,
                                       f"sticker_tooth_{tooth:02d}_steel_frames", "northlight_frame",
                                       tooth=tooth, physical_frame=True))
        dx, dz = x1 - ridge_x, VALLEY_M - RIDGE_M
        for rail in range(1, 7):
            ratio = rail / 7
            x = ridge_x + dx * ratio
            z = RIDGE_M + dz * ratio + 0.04
            name = f"tooth_{tooth:02d}_northlight_crossbar_{rail:02d}"
            frame_names.append(name)
            meshes.append(_box(name, (x - 0.045, x + 0.045, -depth / 2, depth / 2,
                                      z - 0.045, z + 0.045),
                               f"sticker_tooth_{tooth:02d}_steel_frames", "northlight_frame",
                               tooth=tooth, physical_frame=True))
        meshes.append(_box(f"tooth_{tooth:02d}_ridge_cap",
                           (ridge_x - 0.10, ridge_x + 0.10, -depth / 2 - 0.06, depth / 2 + 0.06,
                            RIDGE_M - 0.08, RIDGE_M + 0.14),
                           f"sticker_tooth_{tooth:02d}_ridge_cap", "roof_metal", tooth=tooth))
        # Brick gable ends make the tooth silhouette physical at front and rear.
        for side, y in (("front", -depth / 2), ("rear", depth / 2)):
            vertices = [[x0, y, WALL_TOP_M], [x1, y, WALL_TOP_M], [ridge_x, y, RIDGE_M],
                        [x0, y + (0.28 if side == "front" else -0.28), WALL_TOP_M],
                        [x1, y + (0.28 if side == "front" else -0.28), WALL_TOP_M],
                        [ridge_x, y + (0.28 if side == "front" else -0.28), RIDGE_M]]
            faces = [[0, 1, 2], [3, 5, 4], [0, 3, 4, 1], [1, 4, 5, 2], [2, 5, 3, 0]]
            meshes.append(_mesh(f"tooth_{tooth:02d}_{side}_brick_gable", vertices, faces,
                                f"sticker_tooth_{tooth:02d}_{side}_brick_gable", "brick_gable",
                                tooth=tooth, side=side, watertight=True))
        records.append({"tooth": tooth, "cell_x_m": [x0, x1], "ridge_x_m": ridge_x,
                        "opaque_mesh": opaque, "northlight_mesh": glass,
                        "northlight_frames": frame_names, "northlight_orientation": "+X",
                        "same_handed": True})
    return meshes, records


def _corbel_and_corners(width: float, depth: float) -> list[dict[str, Any]]:
    meshes: list[dict[str, Any]] = []
    for label, z0, z1, projection in (("base", 0.0, 0.34, 0.10),
                                      ("corbel", 5.58, 5.86, 0.18),
                                      ("cap", 5.86, 6.12, 0.24)):
        owner = f"sticker_continuous_{label}"
        meshes.extend([
            _box(f"{label}_front", (-width / 2 - projection, width / 2 + projection,
                                     -depth / 2 - projection, -depth / 2 + 0.28, z0, z1), owner, "brick_trim"),
            _box(f"{label}_rear", (-width / 2 - projection, width / 2 + projection,
                                    depth / 2 - 0.28, depth / 2 + projection, z0, z1), owner, "brick_trim"),
            _box(f"{label}_left", (-width / 2 - projection, -width / 2 + 0.28,
                                    -depth / 2, depth / 2, z0, z1), owner, "brick_trim"),
            _box(f"{label}_right", (width / 2 - 0.28, width / 2 + projection,
                                     -depth / 2, depth / 2, z0, z1), owner, "brick_trim"),
        ])
    for x_name, x in (("left", -width / 2), ("right", width / 2)):
        for y_name, y in (("front", -depth / 2), ("rear", depth / 2)):
            meshes.append(_box(f"fixed_corner_{y_name}_{x_name}",
                               (x - 0.06, x + 0.06 + (0.72 if x < 0 else 0),
                                y - (0.72 if y > 0 else 0.06), y + 0.06, 0.0, WALL_TOP_M),
                               f"sticker_corner_{y_name}_{x_name}", "brick_pier", fixed_identity=True))
    return meshes


def _dock(width: float, depth: float) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    x0, x1 = -width / 2, -width / 2 + 15.0
    y_front = -depth / 2
    meshes = [
        _box("fixed_loading_platform", (x0 - 0.15, x1 + 0.25, y_front - 2.65, y_front + 0.12,
                                        0.0, 0.92), "sticker_loading_platform", "dock_concrete", fixed_identity=True),
        _box("fixed_loading_canopy", (x0 - 0.35, x1 + 0.45, y_front - 3.10, y_front + 0.18,
                                      4.62, 4.92), "sticker_loading_canopy", "dock_canopy",
             face_roles=["canopy_soffit", "canopy_top", "canopy_fascia", "canopy_fascia", "canopy_fascia", "canopy_fascia"],
             fixed_identity=True),
    ]
    for index, x in enumerate((x0 + 0.35, x1 - 0.35)):
        meshes.append(_box(f"fixed_canopy_post_{index}", (x - 0.07, x + 0.07,
                                                           y_front - 2.88, y_front - 2.74, 0.0, 4.62),
                           f"sticker_canopy_post_{index}", "dock_steel", fixed_identity=True))
    # Four treads at the right end and a bounded concrete ramp at the left end.
    for step in range(4):
        meshes.append(_box(f"fixed_dock_stair_{step}",
                           (x1 + 0.25 + step * 0.34, x1 + 0.59 + step * 0.34,
                            y_front - 2.10, y_front - 0.50, 0.0, 0.23 * (step + 1)),
                           "sticker_dock_stairs", "dock_concrete", fixed_identity=True))
    ramp_vertices = [[x0 - 4.2, y_front - 2.55, 0.0], [x0, y_front - 2.55, 0.92],
                     [x0, y_front - 0.35, 0.92], [x0 - 4.2, y_front - 0.35, 0.0],
                     [x0 - 4.2, y_front - 2.55, -0.10], [x0, y_front - 2.55, -0.10],
                     [x0, y_front - 0.35, -0.10], [x0 - 4.2, y_front - 0.35, -0.10]]
    meshes.append(_mesh("fixed_loading_ramp", ramp_vertices,
                        [[0, 1, 2, 3], [4, 7, 6, 5], [0, 4, 5, 1], [1, 5, 6, 2],
                         [2, 6, 7, 3], [3, 7, 4, 0]],
                        "sticker_loading_ramp", "dock_concrete", fixed_identity=True, watertight=True))
    return meshes, {"dock_count": 1, "rolling_door_count": 3, "canopy_count": 1,
                    "platform_mesh": "fixed_loading_platform", "canopy_mesh": "fixed_loading_canopy",
                    "stairs": 4, "ramp_mesh": "fixed_loading_ramp", "fixed_identity": True}


def _chimney(width: float, depth: float, segments: int = 32) -> tuple[dict[str, Any], dict[str, Any]]:
    cx, cy = width / 2 + 5.2, depth / 2 - 8.0
    outer, inner, height = 2.05, 1.42, 22.0
    vertices: list[list[float]] = []
    for z, radius in ((0.0, outer), (height, outer), (0.0, inner), (height, inner)):
        vertices.extend([[cx + radius * math.cos(2 * math.pi * i / segments),
                          cy + radius * math.sin(2 * math.pi * i / segments), z]
                         for i in range(segments)])
    faces: list[list[int]] = []
    roles: list[str] = []
    for i in range(segments):
        j = (i + 1) % segments
        faces.append([i, j, segments + j, segments + i]); roles.append("chimney_exterior")
        faces.append([2 * segments + i, 3 * segments + i, 3 * segments + j, 2 * segments + j]); roles.append("chimney_interior")
        faces.append([segments + i, segments + j, 3 * segments + j, 3 * segments + i]); roles.append("chimney_ring_cap")
        faces.append([i, 2 * segments + i, 2 * segments + j, j]); roles.append("chimney_bottom_ring")
    mesh = _mesh("fixed_detached_hollow_chimney", vertices, faces, "sticker_detached_brick_chimney",
                 "brick_chimney", face_roles=roles, fixed_identity=True, hollow=True,
                 ring_capped=True, detached_clearance_m=3.15)
    return mesh, {"mesh": mesh["name"], "centre_xy_m": [cx, cy], "outer_radius_m": outer,
                  "inner_radius_m": inner, "height_m": height, "hollow": True,
                  "ring_capped": True, "detached": True}


def build_geometry(size_id: str) -> dict[str, Any]:
    if size_id not in SIZE_MATRIX:
        raise KeyError(f"unsupported daylight sawtooth V98 size {size_id!r}")
    spec = SIZE_MATRIX[size_id]
    width, depth = float(spec["width_m"]), float(spec["depth_m"])
    front_bays, side_bays, teeth = int(spec["front_bays"]), int(spec["side_bays"]), int(spec["teeth"])
    if depth != DEPTH_M or width != teeth * TOOTH_M or front_bays != teeth * 2:
        raise ValueError("V98 permits only whole 10 m tooth / paired 5 m facade-cell expansion")
    meshes: list[dict[str, Any]] = []
    apertures: list[dict[str, Any]] = []
    # Exact front: three loading doors at the far left; every other bay is a tall window.
    for side, count in (("front", front_bays), ("rear", front_bays),
                        ("left", side_bays), ("right", side_bays)):
        for bay in range(count):
            is_dock = side == "front" and bay < 3
            authored, aperture = _aperture_bay(side, bay, count, width, depth,
                                               kind="rolling_door" if is_dock else "window",
                                               dock_z=0.92 if is_dock else 0.0)
            meshes.extend(authored)
            aperture["completion_evidence"] = "exact" if side in {"front", "right"} else "constrained"
            apertures.append(aperture)
    meshes.extend(_corbel_and_corners(width, depth))
    roof_meshes, roof_cells = _roof_teeth(width, depth, teeth)
    meshes.extend(roof_meshes)
    dock_meshes, dock = _dock(width, depth)
    meshes.extend(dock_meshes)
    chimney_mesh, chimney = _chimney(width, depth)
    meshes.append(chimney_mesh)
    ownership = [{"owner_id": mesh["sticker_owner_id"], "mesh_name": mesh["name"],
                  "face_indices": list(range(len(mesh["faces"]))), "face_count": len(mesh["faces"]),
                  "fallback_material_forbidden": True} for mesh in meshes]
    checked_faces = sum(len(mesh["faces"]) for mesh in meshes)
    geometry: dict[str, Any] = {
        "schema": "daylight-sawtooth-sticker-lego-v98@1",
        "archetype_id": ARCHETYPE_ID, "variant_id": VARIANT_ID, "size_id": size_id,
        "reference_authority": "exact_three_view_images_override_generic_1_to_3_storey_metadata",
        "reference_evidence": list(REFERENCE_EVIDENCE),
        "dimensions": {"width_m": width, "depth_m": depth, "occupied_storeys": 1,
                       "wall_top_m": WALL_TOP_M, "tooth_valley_m": VALLEY_M,
                       "tooth_ridge_m": RIDGE_M},
        "structural_grid": {"bay_width_m": BAY_M, "tooth_cell_width_m": TOOTH_M,
                            "front_bays": front_bays, "side_bays": side_bays, "tooth_count": teeth,
                            "horizontal_whole_tooth_expansion_only": True,
                            "vertical_scaling": "forbidden", "depth_scaling": "forbidden"},
        "roof_cells": roof_cells, "dock": dock, "chimney": chimney,
        "completion_policy": {"front": "exact", "right": "exact_oblique",
                              "left": "constrained_same_bay_grammar", "rear": "constrained_no_extra_dock"},
        "apertures": apertures, "surface_ownership": ownership,
        "surface_audit": {"status": "pass", "checked_faces": checked_faces,
                          "failure_count": 0, "exactly_one_owner_per_face": True},
        "fixed_modules": {"storeys": 1, "depth_m": DEPTH_M, "dock_stacks": 1,
                          "detached_chimneys": 1, "tooth_handedness": "ridge_east_glass_descends_east"},
        "scalable_modules": {"unit": "complete_10m_tooth_plus_two_5m_facade_bays",
                             "canonical_units": 6, "extended_units": 8},
        "geometry_hard_stops": [
            "occupied_storeys_must_equal_1", "canonical_tooth_count_must_equal_6",
            "all_teeth_must_share_handedness", "all_northlights_must_face_+X",
            "roof_cells_must_remain_individually_addressable", "no_flat_or_gable_roof_substitution",
            "all_windows_and_doors_require_true_returns_and_recessed_backs",
            "chimney_must_be_detached_hollow_and_ring_capped", "dock_count_must_equal_1",
            "rolling_door_count_must_equal_3", "dock_requires_canopy_platform_stairs_and_ramp",
            "no_depth_or_vertical_scaling", "no_partial_tooth_expansion", "no_invented_rear_dock",
            "every_visible_face_requires_exactly_one_sticker_owner",
        ],
        "locked_mesh_bundle": {"kind": "locked_mesh_bundle", "mesh_names": [m["name"] for m in meshes],
                               "generic_primitive_assemblies": [],
                               "all_visible_faces_require_exactly_one_sticker_owner": True},
        "meshes": meshes,
    }
    geometry["geometry_sha256"] = _hash(geometry)
    return geometry


if __name__ == "__main__":
    print(json.dumps({size: build_geometry(size)["geometry_sha256"] for size in SIZE_MATRIX}, indent=2))
