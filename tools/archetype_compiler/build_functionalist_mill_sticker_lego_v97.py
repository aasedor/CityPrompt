"""Locked, bay-addressable carriers for the V97 Sticker Method LEGO pilot."""
from __future__ import annotations

import hashlib
import json
from typing import Any


BAY_M = 5.0
FLOOR_H_M = 5.0
ENTRANCE_WING_BAYS = 1
ENTRANCE_RECESS_M = 2.0
SIZE_MATRIX: dict[str, dict[str, float | int]] = {
    "small": {"width_m": 35.0, "depth_m": 30.0, "floors": 4},
    "canonical": {"width_m": 50.0, "depth_m": 40.0, "floors": 5},
    "large": {"width_m": 65.0, "depth_m": 50.0, "floors": 6},
}


def _sha256(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()
    return hashlib.sha256(raw).hexdigest()


def _mesh(name: str, vertices: list[list[float]], faces: list[list[int]], domain: str,
          **metadata: Any) -> dict[str, Any]:
    return {"name": name, "vertices": vertices, "faces": faces,
            "material_domain": domain, **metadata}


def _quad(name: str, vertices: list[list[float]], domain: str, **metadata: Any) -> dict[str, Any]:
    return _mesh(name, vertices, [[0, 1, 2, 3]], domain, **metadata)


def _quads(name: str, quads: list[list[list[float]]], domain: str,
           **metadata: Any) -> dict[str, Any]:
    vertices: list[list[float]] = []
    faces: list[list[int]] = []
    for quad in quads:
        offset = len(vertices)
        vertices.extend(quad)
        faces.append([offset, offset + 1, offset + 2, offset + 3])
    return _mesh(name, vertices, faces, domain, **metadata)


def _box(name: str, bounds: tuple[float, float, float, float, float, float],
         domain: str, *, bottom: bool = True, **metadata: Any) -> dict[str, Any]:
    x0, x1, y0, y1, z0, z1 = bounds
    v = [[x0, y0, z0], [x1, y0, z0], [x1, y1, z0], [x0, y1, z0],
         [x0, y0, z1], [x1, y0, z1], [x1, y1, z1], [x0, y1, z1]]
    f = [[0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7], [4, 5, 6, 7]]
    if bottom:
        f.append([3, 2, 1, 0])
    return _mesh(name, v, f, domain, **metadata)


def _wall_bay(axis: str, bay: int, floor: int, width: float, depth: float,
              floors: int) -> dict[str, Any]:
    z0, z1 = floor * FLOOR_H_M, (floor + 1) * FLOOR_H_M
    if axis in {"front", "rear"}:
        x0 = -width / 2 + bay * BAY_M
        x1 = x0 + BAY_M
        y = (-depth / 2 + ENTRANCE_RECESS_M
             if axis == "front" and bay < ENTRANCE_WING_BAYS
             else -depth / 2 if axis == "front" else depth / 2)
        vertices = ([[x0, y, z0], [x1, y, z0], [x1, y, z1], [x0, y, z1]]
                    if axis == "front" else
                    [[x1, y, z0], [x0, y, z0], [x0, y, z1], [x1, y, z1]])
    else:
        y0 = -depth / 2 + bay * BAY_M
        y1 = y0 + BAY_M
        x = -width / 2 if axis == "left" else width / 2
        vertices = ([[x, y1, z0], [x, y0, z0], [x, y0, z1], [x, y1, z1]]
                    if axis == "left" else
                    [[x, y0, z0], [x, y1, z0], [x, y1, z1], [x, y0, z1]])
    role = "ground" if floor == 0 else "top_cornice" if floor == floors - 1 else "middle_repeat"
    if axis == "front" and bay == 0 and floor == 0:
        cx, half, opening_top = (x0 + x1) / 2, 1.0, 3.85
        return _quads(f"{axis}_bay_{bay:02d}_floor_{floor:02d}", [
            [[x0, y, z0], [cx - half, y, z0], [cx - half, y, z1], [x0, y, z1]],
            [[cx + half, y, z0], [x1, y, z0], [x1, y, z1], [cx + half, y, z1]],
            [[cx - half, y, opening_top], [cx + half, y, opening_top],
             [cx + half, y, z1], [cx - half, y, z1]],
        ], "vertical_occupied_floor", axis=axis, bay=bay, floor=floor,
                      floor_role=role, portal_aperture=True)
    return _quad(f"{axis}_bay_{bay:02d}_floor_{floor:02d}", vertices,
                 "vertical_occupied_floor", axis=axis, bay=bay, floor=floor, floor_role=role)


def _portal_geometry(width: float, depth: float) -> list[dict[str, Any]]:
    # The single entrance always occupies the first 5 m front bay.  Its wall
    # sticker remains on the clay face; these inset surfaces make the doorway
    # read as a tunnel rather than a dark printed rectangle.
    cx = -width / 2 + BAY_M / 2
    y0 = -depth / 2 + ENTRANCE_RECESS_M
    y1 = y0 + 1.25
    half, top = 1.0, 3.85
    tunnel = _quads("fixed_entrance_tunnel", [
        [[cx - half, y0, 0.02], [cx - half, y1, 0.02],
         [cx - half, y1, top], [cx - half, y0, top]],
        [[cx + half, y1, 0.02], [cx + half, y0, 0.02],
         [cx + half, y0, top], [cx + half, y1, top]],
        [[cx - half, y0, top], [cx - half, y1, top],
         [cx + half, y1, top], [cx + half, y0, top]],
    ], "entrance_return", fixed_identity=True)
    door = _quad("fixed_entrance_door", [
        [cx - half, y1, 0.08], [cx + half, y1, 0.08],
        [cx + half, y1, top - 0.08], [cx - half, y1, top - 0.08],
    ], "entrance_door", fixed_identity=True)
    threshold = _quad("fixed_entrance_threshold", [
        [cx - half, y0, 0.025], [cx - half, y1, 0.025],
        [cx + half, y1, 0.025], [cx + half, y0, 0.025],
    ], "entrance_return", fixed_identity=True)
    return [tunnel, door, threshold]


def _entrance_wing_returns(width: float, depth: float, floors: int) -> list[dict[str, Any]]:
    """Close the 10 m recessed stair/entrance wing at the main façade step."""
    x = -width / 2 + ENTRANCE_WING_BAYS * BAY_M
    y0, y1 = -depth / 2, -depth / 2 + ENTRANCE_RECESS_M
    result: list[dict[str, Any]] = []
    for floor in range(floors):
        z0, z1 = floor * FLOOR_H_M, (floor + 1) * FLOOR_H_M
        role = "ground" if floor == 0 else "top_cornice" if floor == floors - 1 else "middle_repeat"
        result.append(_quad(f"fixed_entrance_wing_return_floor_{floor:02d}", [
            [x, y0, z0], [x, y1, z0], [x, y1, z1], [x, y0, z1],
        ], "vertical_occupied_floor", axis="wing_return", bay=0, floor=floor,
                            floor_role=role, fixed_identity=True))
    return result


def _entrance_wing_eave_closure(width: float, depth: float, wall_top: float) -> list[dict[str, Any]]:
    x0, x1 = -width / 2, -width / 2 + ENTRANCE_WING_BAYS * BAY_M
    y0, y1 = -depth / 2, -depth / 2 + ENTRANCE_RECESS_M
    return [
        _quad("fixed_entrance_wing_soffit", [
            [x0, y0, wall_top - 0.04], [x0, y1, wall_top - 0.04],
            [x1, y1, wall_top - 0.04], [x1, y0, wall_top - 0.04],
        ], "roof_only", roof_role="fixed_entrance_soffit", fixed_identity=True),
        _quad("fixed_entrance_wing_fascia", [
            [x0, y0, wall_top - 0.04], [x1, y0, wall_top - 0.04],
            [x1, y0, wall_top + 0.24], [x0, y0, wall_top + 0.24],
        ], "roof_only", roof_role="fixed_entrance_fascia", fixed_identity=True),
    ]


def _rear_annex(width: float, depth: float) -> list[dict[str, Any]]:
    """A fixed two-storey rear service wing, visible in the oblique/aerial refs."""
    x0, x1 = width / 2 - 20.0, width / 2
    y0, y1 = depth / 2, depth / 2 + 10.0
    result: list[dict[str, Any]] = []
    for floor in range(2):
        z0, z1 = floor * FLOOR_H_M, (floor + 1) * FLOOR_H_M
        role = "ground" if floor == 0 else "top_cornice"
        for bay in range(4):
            bx0, bx1 = x0 + bay * BAY_M, x0 + (bay + 1) * BAY_M
            result.append(_quad(f"annex_rear_bay_{bay:02d}_floor_{floor:02d}", [
                [bx1, y1, z0], [bx0, y1, z0], [bx0, y1, z1], [bx1, y1, z1],
            ], "vertical_occupied_floor", axis="rear", bay=bay, floor=floor,
                                floor_role=role, fixed_identity=True))
        for side, x in (("left", x0), ("right", x1)):
            for bay in range(2):
                by0, by1 = y0 + bay * BAY_M, y0 + (bay + 1) * BAY_M
                vertices = ([[x, by1, z0], [x, by0, z0], [x, by0, z1], [x, by1, z1]]
                            if side == "left" else
                            [[x, by0, z0], [x, by1, z0], [x, by1, z1], [x, by0, z1]])
                result.append(_quad(f"annex_{side}_bay_{bay:02d}_floor_{floor:02d}", vertices,
                                    "vertical_occupied_floor", axis=side, bay=bay, floor=floor,
                                    floor_role=role, fixed_identity=True))
    result.append(_quad("fixed_rear_annex_roof", [
        [x0, y0, 10.05], [x1, y0, 10.05], [x1, y1, 10.05], [x0, y1, 10.05],
    ], "roof_only", roof_role="fixed_annex"))
    return result


def _roof(width: float, depth: float, wall_top: float) -> list[dict[str, Any]]:
    rise = depth * 0.18
    ridge_z = wall_top + rise
    ridge_left, ridge_right = -width / 2 + BAY_M, width / 2 - BAY_M
    meshes: list[dict[str, Any]] = []
    strip_count = int(round((width - 2 * BAY_M) / BAY_M))
    for index in range(strip_count):
        x0, x1 = ridge_left + index * BAY_M, ridge_left + (index + 1) * BAY_M
        meshes.append(_quad(f"roof_front_strip_{index:02d}", [
            [x0, -depth / 2, wall_top], [x1, -depth / 2, wall_top],
            [x1, 0.0, ridge_z], [x0, 0.0, ridge_z],
        ], "roof_only", roof_role="repeat_strip", roof_side="front", strip=index))
        meshes.append(_quad(f"roof_rear_strip_{index:02d}", [
            [x1, depth / 2, wall_top], [x0, depth / 2, wall_top],
            [x0, 0.0, ridge_z], [x1, 0.0, ridge_z],
        ], "roof_only", roof_role="repeat_strip", roof_side="rear", strip=index))
    meshes.append(_mesh("roof_left_hip", [
        [-width / 2, -depth / 2, wall_top], [-width / 2, depth / 2, wall_top],
        [ridge_left, -depth / 2, wall_top], [ridge_left, depth / 2, wall_top],
        [ridge_left, 0.0, ridge_z],
    ], [[0, 1, 4], [0, 4, 2], [1, 3, 4]], "roof_only", roof_role="fixed_hip"))
    meshes.append(_mesh("roof_right_hip", [
        [width / 2, depth / 2, wall_top], [width / 2, -depth / 2, wall_top],
        [ridge_right, depth / 2, wall_top], [ridge_right, -depth / 2, wall_top],
        [ridge_right, 0.0, ridge_z],
    ], [[0, 1, 4], [0, 4, 2], [1, 3, 4]], "roof_only", roof_role="fixed_hip"))
    # Three brick chimney stacks remain fixed in number at every capacity.
    for index, ratio in enumerate((0.30, 0.52, 0.70)):
        x = -width / 2 + width * ratio
        meshes.append(_box(f"fixed_chimney_{index}",
                           (x - 0.45, x + 0.45, -0.45, 0.45, ridge_z - 0.35, ridge_z + 1.65),
                           "roof_access", fixed_identity=True))
    dormer_x0, dormer_x1 = width / 2 - 15.0, width / 2 - 10.0
    dormer_y0, dormer_y1 = -depth * 0.18, -depth * 0.06
    dormer_base = wall_top + rise * 0.68
    meshes.append(_box("fixed_roof_service_dormer_body",
                       (dormer_x0, dormer_x1, dormer_y0, dormer_y1,
                        dormer_base, dormer_base + 1.7),
                       "roof_access", fixed_identity=True))
    cap_x0, cap_x1 = dormer_x0 - 0.2, dormer_x1 + 0.2
    cap_y0, cap_y1 = dormer_y0 - 0.2, dormer_y1 + 0.2
    cap_mid = (cap_y0 + cap_y1) / 2
    cap_eave, cap_ridge = dormer_base + 1.65, dormer_base + 2.55
    meshes.append(_mesh("fixed_roof_service_dormer_cap", [
        [cap_x0, cap_y0, cap_eave], [cap_x1, cap_y0, cap_eave],
        [cap_x1, cap_y1, cap_eave], [cap_x0, cap_y1, cap_eave],
        [cap_x0, cap_mid, cap_ridge], [cap_x1, cap_mid, cap_ridge],
    ], [[0, 1, 5, 4], [4, 5, 2, 3], [0, 4, 3], [1, 2, 5]],
                         "roof_only", roof_role="fixed_dormer_cap", fixed_identity=True))
    return meshes


def build_geometry(size_id: str) -> dict[str, Any]:
    if size_id not in SIZE_MATRIX:
        raise KeyError(f"unsupported V97 size {size_id!r}")
    spec = SIZE_MATRIX[size_id]
    width, depth, floors = float(spec["width_m"]), float(spec["depth_m"]), int(spec["floors"])
    if width % BAY_M or depth % BAY_M:
        raise ValueError("V97 dimensions must be whole 5 m bay multiples")
    front_bays, side_bays = int(width / BAY_M), int(depth / BAY_M)
    meshes: list[dict[str, Any]] = []
    for axis, count in (("front", front_bays), ("rear", front_bays),
                        ("left", side_bays), ("right", side_bays)):
        for bay in range(count):
            for floor in range(floors):
                meshes.append(_wall_bay(axis, bay, floor, width, depth, floors))
    meshes.extend(_portal_geometry(width, depth))
    meshes.extend(_entrance_wing_returns(width, depth, floors))
    meshes.extend(_entrance_wing_eave_closure(width, depth, floors * FLOOR_H_M))
    meshes.extend(_rear_annex(width, depth))
    meshes.extend(_roof(width, depth, floors * FLOOR_H_M))
    geometry = {
        "schema": "functional-mill-sticker-lego-v97@1",
        "building_id": "functionalist-brick-industrial--brick-multistory-mill",
        "size_id": size_id, "width_m": width, "depth_m": depth,
        "floor_count": floors, "floor_height_m": FLOOR_H_M,
        "floor_datums_m": [index * FLOOR_H_M for index in range(floors + 1)],
        "bay_module_m": BAY_M, "front_bay_count": front_bays,
        "side_bay_count": side_bays,
        "fixed_modules": {"entrance_bays": ENTRANCE_WING_BAYS, "far_end_bays": 1, "chimneys": 3},
        "repeat_middle_bays": front_bays - 3,
        "meshes": meshes,
    }
    geometry["geometry_sha256"] = _sha256(geometry)
    return geometry


if __name__ == "__main__":
    print(json.dumps({key: build_geometry(key)["geometry_sha256"] for key in SIZE_MATRIX}, indent=2))
