"""Build the locked four-storey Eixample carrier for Sticker Method V96.

The reference, rather than the legacy six-storey metadata, controls the visible
storey count and proportions.  The carrier is a broad Cerdà octagon with an
open light court, one real recessed entrance void, and disjoint floor/roof
surface ownership.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any


OUTER = ((-11.0, -23.0), (11.0, -23.0), (23.0, -11.0), (23.0, 11.0),
         (11.0, 23.0), (-11.0, 23.0), (-23.0, 11.0), (-23.0, -11.0))
# Clockwise: the visible normal points into the courtyard.
INNER = ((-5.5, -11.0), (-11.0, -5.5), (-11.0, 5.5), (-5.5, 11.0),
         (5.5, 11.0), (11.0, 5.5), (11.0, -5.5), (5.5, -11.0))
FLOOR_Z = (0.0, 4.5, 9.5, 14.5, 19.5)
HERO_SEGMENT = 1


def _sha256(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()
    return hashlib.sha256(raw).hexdigest()


def _quad_mesh(name: str, quads: list[list[list[float]]], domain: str,
               floor_faces: dict[str, list[int]] | None = None) -> dict[str, Any]:
    vertices: list[list[float]] = []
    faces: list[list[int]] = []
    for quad in quads:
        offset = len(vertices)
        vertices.extend(quad)
        faces.append([offset, offset + 1, offset + 2, offset + 3])
    result: dict[str, Any] = {
        "name": name, "vertices": vertices, "faces": faces,
        "material_domain": domain,
    }
    if floor_faces is not None:
        result["floor_face_indices"] = floor_faces
    return result


def _point(a: tuple[float, float], b: tuple[float, float], distance: float) -> tuple[float, float]:
    length = ((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2) ** 0.5
    return a[0] + (b[0] - a[0]) * distance / length, a[1] + (b[1] - a[1]) * distance / length


def _wall(segment: int, a: tuple[float, float], b: tuple[float, float], prefix: str) -> dict[str, Any]:
    quads: list[list[list[float]]] = []
    floor_faces = {str(index): [] for index in range(4)}
    for floor, (z0, z1) in enumerate(zip(FLOOR_Z, FLOOR_Z[1:])):
        if prefix == "outer" and segment == HERO_SEGMENT and floor == 0:
            length = ((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2) ** 0.5
            left, right = _point(a, b, length / 2 - 1.7), _point(a, b, length / 2 + 1.7)
            pieces = (
                [[a[0], a[1], z0], [left[0], left[1], z0], [left[0], left[1], z1], [a[0], a[1], z1]],
                [[right[0], right[1], z0], [b[0], b[1], z0], [b[0], b[1], z1], [right[0], right[1], z1]],
                [[left[0], left[1], 4.0], [right[0], right[1], 4.0], [right[0], right[1], z1], [left[0], left[1], z1]],
            )
        else:
            pieces = ([[a[0], a[1], z0], [b[0], b[1], z0],
                       [b[0], b[1], z1], [a[0], a[1], z1]],)
        for quad in pieces:
            floor_faces[str(floor)].append(len(quads))
            quads.append(quad)
    mesh = _quad_mesh(f"{prefix}_wall_{segment}", quads, "vertical_occupied_floor", floor_faces)
    mesh["semantic_surface_id"] = f"{prefix}_elevation_{segment}"
    return mesh


def _roof_ring() -> dict[str, Any]:
    quads = []
    for index in range(8):
        nxt = (index + 1) % 8
        oa, ob = OUTER[index], OUTER[nxt]
        # INNER is clockwise; pair the corresponding opposite-order edge.
        ia, ib = INNER[(7 - index) % 8], INNER[(-index) % 8]
        quads.append([[oa[0], oa[1], 19.5], [ob[0], ob[1], 19.5],
                      [ia[0], ia[1], 19.5], [ib[0], ib[1], 19.5]])
    return _quad_mesh("terrace_roof_ring", quads, "roof_only")


def _parapet_segment(name: str, a: tuple[float, float], b: tuple[float, float],
                     inward: bool) -> dict[str, Any]:
    dx, dy = b[0] - a[0], b[1] - a[1]
    length = (dx * dx + dy * dy) ** 0.5
    # right normal for outer loop; reverse for the inner court loop.
    nx, ny = dy / length, -dx / length
    if inward:
        nx, ny = -nx, -ny
    t = 0.28
    a2, b2 = (a[0] - nx * t, a[1] - ny * t), (b[0] - nx * t, b[1] - ny * t)
    z0, z1 = 19.5, 20.8
    quads = [
        [[a[0], a[1], z0], [b[0], b[1], z0], [b[0], b[1], z1], [a[0], a[1], z1]],
        [[b2[0], b2[1], z0], [a2[0], a2[1], z0], [a2[0], a2[1], z1], [b2[0], b2[1], z1]],
        [[a[0], a[1], z1], [b[0], b[1], z1], [b2[0], b2[1], z1], [a2[0], a2[1], z1]],
    ]
    return _quad_mesh(name, quads, "roof_only")


def _entrance_tunnel() -> list[dict[str, Any]]:
    a, b = OUTER[HERO_SEGMENT], OUTER[(HERO_SEGMENT + 1) % 8]
    length = ((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2) ** 0.5
    left, right = _point(a, b, length / 2 - 1.7), _point(a, b, length / 2 + 1.7)
    # inward is left of the CCW outer tangent
    tx, ty = (b[0] - a[0]) / length, (b[1] - a[1]) / length
    ix, iy = -ty, tx
    depth = 1.45
    li, ri = (left[0] + ix * depth, left[1] + iy * depth), (right[0] + ix * depth, right[1] + iy * depth)
    reveals = _quad_mesh("hero_portal_tunnel", [
        [[left[0], left[1], 0.0], [li[0], li[1], 0.0], [li[0], li[1], 4.0], [left[0], left[1], 4.0]],
        [[ri[0], ri[1], 0.0], [right[0], right[1], 0.0], [right[0], right[1], 4.0], [ri[0], ri[1], 4.0]],
        [[left[0], left[1], 4.0], [right[0], right[1], 4.0], [ri[0], ri[1], 4.0], [li[0], li[1], 4.0]],
        [[left[0], left[1], 0.015], [li[0], li[1], 0.015], [ri[0], ri[1], 0.015], [right[0], right[1], 0.015]],
    ], "entrance_return")
    door = _quad_mesh("hero_portal_door", [[
        [li[0], li[1], 0.08], [ri[0], ri[1], 0.08],
        [ri[0], ri[1], 3.82], [li[0], li[1], 3.82],
    ]], "entrance_door")
    return [reveals, door]


def _roof_access() -> dict[str, Any]:
    # Sit on the occupied roof ring, never over the open light court.
    x0, x1, y0, y1, z0, z1 = 12.5, 17.5, -2.25, 2.25, 19.5, 21.45
    v = [[x0, y0, z0], [x1, y0, z0], [x1, y1, z0], [x0, y1, z0],
         [x0, y0, z1], [x1, y0, z1], [x1, y1, z1], [x0, y1, z1]]
    f = [[0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7], [4, 5, 6, 7]]
    return {"name": "roof_access_house", "vertices": v, "faces": f, "material_domain": "roof_only"}


def _courtyard_floor() -> dict[str, Any]:
    # The Cerdà light court is open to the sky, but the visible surface is the
    # lower court roof rather than a black, ground-level void.  Holding it one
    # storey below the main terrace preserves the courtyard volume while
    # giving aerial and roof-audit views an architecturally legible terminus.
    vertices = [[x, y, 14.5] for x, y in reversed(INNER)]
    return {"name": "courtyard_floor", "vertices": vertices,
            "faces": [list(range(len(vertices)))], "material_domain": "courtyard_ground"}


def build_geometry() -> dict[str, Any]:
    meshes: list[dict[str, Any]] = []
    for index in range(8):
        meshes.append(_wall(index, OUTER[index], OUTER[(index + 1) % 8], "outer"))
        meshes.append(_wall(index, INNER[index], INNER[(index + 1) % 8], "court"))
        meshes.append(_parapet_segment(f"outer_parapet_{index}", OUTER[index], OUTER[(index + 1) % 8], False))
        meshes.append(_parapet_segment(f"court_parapet_{index}", INNER[index], INNER[(index + 1) % 8], True))
    meshes.extend([_roof_ring(), *_entrance_tunnel(), _roof_access(), _courtyard_floor()])
    geometry = {
        "schema": "eixample-geometry-conditioned-v96@1",
        "building_id": "eixample-apartment-block-classic",
        "floor_count": 4, "floor_datums_m": list(FLOOR_Z),
        "wall_top_z_m": 19.5, "open_courtyard": True, "meshes": meshes,
    }
    geometry["geometry_sha256"] = _sha256(geometry)
    return geometry


if __name__ == "__main__":
    built = build_geometry()
    print(json.dumps({"geometry_sha256": built["geometry_sha256"], "mesh_count": len(built["meshes"])}, indent=2))
