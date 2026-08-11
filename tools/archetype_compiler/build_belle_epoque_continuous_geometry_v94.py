"""Build the V94 continuous-shell five-storey Belle Epoque geometry.

V93 proved floor addressability by making every floor a separate closed prism.
Those internal caps created hairline render seams.  V94 welds the five bands
back into one topology per elevation, removes only the internal horizontal
caps, and records exact per-floor face ownership for the Sticker Agent.
"""
from __future__ import annotations

import hashlib
import json
import math
from copy import deepcopy
from typing import Any

from build_belle_epoque_floor_geometry_v93 import build_segmented_geometry


SURFACES = (
    "facade_front", "facade_right", "facade_rear", "facade_left", "corner_pavilion",
    "court_front", "court_right", "court_rear", "court_left",
)
INTERNAL_FLOOR_DATUMS = (4.1, 8.2, 12.3, 16.4)
CUPOLA_BASE_Z = 18.4
CUPOLA_VERTICAL_SCALE = 0.83
PLANAR_NORMALS = {
    "facade_front": (0.0, -1.0), "facade_right": (1.0, 0.0),
    "facade_rear": (0.0, 1.0), "facade_left": (-1.0, 0.0),
    "court_front": (0.0, 1.0), "court_right": (-1.0, 0.0),
    "court_rear": (0.0, -1.0), "court_left": (1.0, 0.0),
}
OBSOLETE_RAIL_CORNICES = {
    "corner_pavilion_mid_cornice", "corner_pavilion_crown_cornice",
    "front_main_cornice", "right_main_cornice", "rear_main_cornice", "left_main_cornice",
    "front_crown_return", "right_crown_return", "rear_crown_return", "left_crown_return",
}


def _sha256(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _normal(vertices: list[list[float]], face: list[int]) -> tuple[float, float, float]:
    a, b, c = (vertices[index] for index in face[:3])
    ab = (b[0] - a[0], b[1] - a[1], b[2] - a[2])
    ac = (c[0] - a[0], c[1] - a[1], c[2] - a[2])
    value = (
        ab[1] * ac[2] - ab[2] * ac[1],
        ab[2] * ac[0] - ab[0] * ac[2],
        ab[0] * ac[1] - ab[1] * ac[0],
    )
    length = math.sqrt(sum(component * component for component in value)) or 1.0
    return tuple(component / length for component in value)


def _is_internal_cap(vertices: list[list[float]], face: list[int]) -> bool:
    zs = [float(vertices[index][2]) for index in face]
    return max(zs) - min(zs) < 1e-7 and any(abs(zs[0] - datum) < 1e-6 for datum in INTERNAL_FLOOR_DATUMS)


def _continuous_surface(surface: str, pieces: list[dict[str, Any]]) -> dict[str, Any]:
    raw_vertices: list[list[float]] = []
    raw_faces: list[list[int]] = []
    for piece in sorted(pieces, key=lambda item: int(item["floor_index"])):
        offset = len(raw_vertices)
        raw_vertices.extend(deepcopy(piece["vertices"]))
        raw_faces.extend([
            [offset + int(index) for index in face]
            for face in piece["faces"] if not _is_internal_cap(piece["vertices"], face)
        ])

    vertices: list[list[float]] = []
    vertex_map: dict[tuple[float, float, float], int] = {}
    remap: dict[int, int] = {}
    for index, vertex in enumerate(raw_vertices):
        key = tuple(round(float(value), 6) for value in vertex)
        if key not in vertex_map:
            vertex_map[key] = len(vertices)
            vertices.append(list(key))
        remap[index] = vertex_map[key]
    faces: list[list[int]] = []
    seen: set[tuple[int, ...]] = set()
    for face in raw_faces:
        welded = [remap[index] for index in face]
        if len(set(welded)) < 3:
            continue
        canonical = tuple(sorted(welded))
        if canonical in seen:
            continue
        seen.add(canonical)
        faces.append(welded)

    floor_faces = {str(index): [] for index in range(5)}
    hero_faces = {str(index): [] for index in range(5)}
    for face_index, face in enumerate(faces):
        centre = [sum(vertices[index][axis] for index in face) / len(face) for axis in range(3)]
        floor_index = max(0, min(4, int(min(centre[2], 20.5 - 1e-7) // 4.1)))
        floor_faces[str(floor_index)].append(face_index)
        nx, ny, nz = _normal(vertices, face)
        if abs(nz) > 0.28:
            continue
        if surface == "corner_pavilion":
            rx, ry = centre[0] + 11.0, centre[1] + 10.0
            length = math.hypot(rx, ry) or 1.0
            outward = nx * rx / length + ny * ry / length
        else:
            dx, dy = PLANAR_NORMALS[surface]
            outward = nx * dx + ny * dy
        if outward >= 0.72:
            hero_faces[str(floor_index)].append(face_index)

    return {
        "name": f"{surface}_continuous_wall",
        "vertices": vertices,
        "faces": faces,
        "semantic_surface_id": surface,
        "material_domain": "vertical_occupied_floor",
        "floor_face_indices": floor_faces,
        "hero_floor_face_indices": hero_faces,
    }


def _shrink_cornice(mesh: dict[str, Any]) -> dict[str, Any]:
    output = deepcopy(mesh)
    name = str(output["name"])
    if "mid_cornice" in name or "main_cornice" in name:
        scale = 0.42
    elif "crown_cornice" in name or "crown_return" in name:
        scale = 0.54
    else:
        return output
    zs = [float(vertex[2]) for vertex in output["vertices"]]
    centre = (min(zs) + max(zs)) / 2
    output["vertices"] = [
        [float(x), float(y), round(centre + (float(z) - centre) * scale, 6)]
        for x, y, z in output["vertices"]
    ]
    # Cornices terminate at the wall/corner join and project only enough to
    # cast a shadow. The V92 clay bands overran the ends and read as rails.
    plan_bounds = {
        "front_main_cornice": (-11.0, 18.0, -17.18, -16.82),
        "right_main_cornice": (17.82, 18.18, -17.0, 17.0),
        "rear_main_cornice": (-18.0, 18.0, 16.82, 17.18),
        "left_main_cornice": (-18.18, -17.82, -10.0, 17.0),
        "front_crown_return": (-11.0, 18.0, -16.55, -16.15),
        "right_crown_return": (17.62, 18.02, -16.35, 16.35),
        "rear_crown_return": (-17.35, 17.35, 16.15, 16.55),
        "left_crown_return": (-18.02, -17.62, -9.5, 16.35),
    }
    if name in plan_bounds:
        x0, x1, y0, y1 = plan_bounds[name]
        output["vertices"] = [
            [min(max(float(x), x0), x1), min(max(float(y), y0), y1), float(z)]
            for x, y, z in output["vertices"]
        ]
    elif name.startswith("corner_pavilion_") and name.endswith("_cornice"):
        cx, cy = -11.0, -10.0
        refined = []
        for x, y, z in output["vertices"]:
            dx, dy = float(x) - cx, float(y) - cy
            radius = math.hypot(dx, dy) or 1.0
            compact_radius = 7.05 + (radius - 7.05) * 0.38
            refined.append([cx + dx / radius * compact_radius, cy + dy / radius * compact_radius, float(z)])
        output["vertices"] = refined
    output["v94_architectural_cornice"] = True
    return output


def _compress_corner_cupola(mesh: dict[str, Any]) -> dict[str, Any]:
    output = deepcopy(mesh)
    if str(output["name"]) not in {
        "corner_upper_tower", "corner_tower_crown", "corner_cupola_drum",
        "corner_glass_cupola", "corner_cupola_cap", "corner_cupola_finial",
    }:
        return output
    output["vertices"] = [
        [float(x), float(y), round(CUPOLA_BASE_Z + (float(z) - CUPOLA_BASE_Z) * CUPOLA_VERTICAL_SCALE, 6)]
        for x, y, z in output["vertices"]
    ]
    output["v94_cupola_vertical_scale"] = CUPOLA_VERTICAL_SCALE
    return output


def build_continuous_geometry() -> dict[str, Any]:
    segmented = build_segmented_geometry(5)
    floor_meshes = [mesh for mesh in segmented["meshes"] if mesh.get("material_domain") == "vertical_occupied_floor"]
    output: list[dict[str, Any]] = []
    for surface in SURFACES:
        pieces = [mesh for mesh in floor_meshes if mesh.get("semantic_surface_id") == surface]
        if len(pieces) != 5:
            raise RuntimeError(f"continuous surface {surface} expected five floor pieces, found {len(pieces)}")
        output.append(_continuous_surface(surface, pieces))
    for mesh in segmented["meshes"]:
        if mesh.get("material_domain") == "vertical_occupied_floor":
            continue
        if mesh["name"] == "wrapped_corner_canopy":
            continue
        if mesh["name"] in OBSOLETE_RAIL_CORNICES:
            continue
        output.append(_compress_corner_cupola(_shrink_cornice(mesh)))

    geometry = {
        "schema": "belle-epoque-continuous-floor-geometry@1",
        "building_id": "grand-magasin-belle-epoque",
        "floor_count": 5,
        "unit_floor_height_m": 4.1,
        "wall_top_z_m": 20.5,
        "source_v93_geometry_sha256": segmented["geometry_sha256"],
        "meshes": output,
    }
    geometry["geometry_sha256"] = _sha256({key: value for key, value in geometry.items() if key != "geometry_sha256"})
    geometry["audit"] = audit_continuous_geometry(geometry)
    return geometry


def audit_continuous_geometry(geometry: dict[str, Any]) -> dict[str, Any]:
    failures: list[dict[str, Any]] = []
    walls = [mesh for mesh in geometry["meshes"] if mesh.get("material_domain") == "vertical_occupied_floor"]
    if len(walls) != len(SURFACES):
        failures.append({"code": "continuous_wall_count", "actual": len(walls), "expected": len(SURFACES)})
    for mesh in walls:
        if any(_is_internal_cap(mesh["vertices"], face) for face in mesh["faces"]):
            failures.append({"code": "internal_floor_cap_survives", "mesh": mesh["name"]})
        for floor in range(5):
            if not mesh["floor_face_indices"].get(str(floor)):
                failures.append({"code": "missing_floor_face_owner", "mesh": mesh["name"], "floor": floor})
            if not mesh["hero_floor_face_indices"].get(str(floor)):
                failures.append({"code": "missing_hero_floor_face", "mesh": mesh["name"], "floor": floor})
    if any(mesh["name"] == "wrapped_corner_canopy" for mesh in geometry["meshes"]):
        failures.append({"code": "legacy_opaque_canopy_survives"})
    return {
        "status": "pass" if not failures else "fail",
        "continuous_wall_count": len(walls),
        "internal_floor_cap_count": sum(
            1 for mesh in walls for face in mesh["faces"] if _is_internal_cap(mesh["vertices"], face)
        ),
        "failures": failures,
    }


if __name__ == "__main__":
    built = build_continuous_geometry()
    print(json.dumps({"geometry_sha256": built["geometry_sha256"], "audit": built["audit"]}, indent=2))
