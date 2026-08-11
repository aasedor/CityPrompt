"""Create floor-addressable five- and six-storey Grand Magasin geometry.

The five-storey bundle is a topology-only segmentation of the approved V92
shape.  The six-storey bundle inserts one 4.1 m middle storey and translates
the fixed top/crown and complete roof landmark group without stretching them.
"""
from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from belle_epoque_floor_sticker_v93 import build_floor_plan
from build_belle_epoque_clay_v92 import build_geometry


REPO = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = REPO / "artifacts/belle-epoque-floor-sticker-v93"

SURFACE_SOURCE_MESHES = {
    "facade_front": ["front_wall", "upper_front_setback"],
    "facade_right": ["right_wall", "upper_right_setback"],
    "facade_rear": ["rear_wall", "upper_rear_setback"],
    "facade_left": ["left_wall", "upper_left_setback"],
    "corner_pavilion": [
        "corner_pavilion_facet_0", "corner_pavilion_facet_1", "corner_pavilion_facet_2",
        "corner_pavilion_facet_3", "corner_upper_front_return", "corner_upper_left_return",
    ],
    "court_front": ["court_front_wall"],
    "court_right": ["court_right_wall"],
    "court_rear": ["court_rear_wall"],
    "court_left": ["court_left_wall"],
}

TOP_CROWN_DETAIL_MESHES = {
    "corner_pavilion_mid_cornice", "corner_pavilion_crown_cornice",
    "front_main_cornice", "right_main_cornice", "rear_main_cornice", "left_main_cornice",
    "front_crown_return", "right_crown_return", "rear_crown_return", "left_crown_return",
}

ROOF_LANDMARK_EXACT = {
    "watertight_perimeter_court_crown", "central_dome_curb", "central_dome_drum",
    "central_glass_dome", "central_dome_cap", "central_dome_finial", "corner_upper_tower",
    "corner_tower_crown", "corner_cupola_drum", "corner_glass_cupola", "corner_cupola_cap",
    "corner_cupola_finial",
}


def _sha256(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _is_prism(mesh: dict[str, Any]) -> bool:
    vertices = mesh["vertices"]
    if len(vertices) % 2:
        return False
    half = len(vertices) // 2
    if half < 3:
        return False
    return all(
        abs(float(vertices[index][0]) - float(vertices[index + half][0])) < 1e-8
        and abs(float(vertices[index][1]) - float(vertices[index + half][1])) < 1e-8
        for index in range(half)
    )


def _prism_slice(mesh: dict[str, Any], z_min: float, z_max: float) -> dict[str, Any] | None:
    if not _is_prism(mesh):
        raise ValueError(f"floor source mesh {mesh['name']} is not a vertical prism")
    source_min = min(float(vertex[2]) for vertex in mesh["vertices"])
    source_max = max(float(vertex[2]) for vertex in mesh["vertices"])
    lower, upper = max(source_min, z_min), min(source_max, z_max)
    if upper - lower <= 1e-8:
        return None
    half = len(mesh["vertices"]) // 2
    footprint = [[float(x), float(y)] for x, y, _z in mesh["vertices"][:half]]
    vertices = [[x, y, lower] for x, y in footprint] + [[x, y, upper] for x, y in footprint]
    return {"name": mesh["name"], "vertices": vertices, "faces": deepcopy(mesh["faces"])}


def _merge_meshes(name: str, pieces: list[dict[str, Any]], **metadata: Any) -> dict[str, Any]:
    vertices: list[list[float]] = []
    faces: list[list[int]] = []
    for piece in pieces:
        offset = len(vertices)
        vertices.extend(deepcopy(piece["vertices"]))
        faces.extend([[offset + int(index) for index in face] for face in piece["faces"]])
    return {"name": name, "vertices": vertices, "faces": faces, **metadata}


def _translate(mesh: dict[str, Any], dz: float) -> dict[str, Any]:
    moved = deepcopy(mesh)
    moved["vertices"] = [[float(x), float(y), round(float(z) + dz, 6)] for x, y, z in mesh["vertices"]]
    return moved


def _extend_floor_source(mesh: dict[str, Any], floor_count: int) -> dict[str, Any]:
    if floor_count == 5:
        return deepcopy(mesh)
    if floor_count != 6:
        raise ValueError("only five- and six-storey pilot geometry is supported")
    moved = deepcopy(mesh)
    # Upper-setback pieces are fixed top/crown content and translate intact.
    if mesh["name"].startswith("upper_") or mesh["name"].startswith("corner_upper_"):
        return _translate(mesh, 4.1)
    # Main wall/court/corner prisms grow only at their upper endpoint.  They are
    # immediately split into fixed-height floor pieces below, so no output face
    # is a stretched full-height sticker carrier.
    old_top = max(float(vertex[2]) for vertex in mesh["vertices"])
    moved["vertices"] = [
        [float(x), float(y), round(float(z) + 4.1, 6) if abs(float(z) - old_top) < 1e-8 else float(z)]
        for x, y, z in mesh["vertices"]
    ]
    return moved


def _is_roof_landmark(name: str) -> bool:
    return name in ROOF_LANDMARK_EXACT or name.startswith("dormer_")


def build_segmented_geometry(floor_count: int) -> dict[str, Any]:
    base = build_geometry()
    source_by_name = {str(mesh["name"]): mesh for mesh in base["meshes"]}
    consumed = {name for names in SURFACE_SOURCE_MESHES.values() for name in names}
    plan_hash_placeholder = "segmented-v93-pending" if floor_count == 6 else None
    plan = build_floor_plan(floor_count, segmented_geometry_sha256=plan_hash_placeholder)
    meshes: list[dict[str, Any]] = []

    instances_by_surface: dict[str, list[dict[str, Any]]] = {}
    for item in plan["floor_instances"]:
        instances_by_surface.setdefault(str(item["surface_id"]), []).append(item)

    for surface_id, source_names in SURFACE_SOURCE_MESHES.items():
        expanded = [_extend_floor_source(source_by_name[name], floor_count) for name in source_names]
        for item in sorted(instances_by_surface[surface_id], key=lambda value: value["floor_index"]):
            pieces = [
                piece for piece in (
                    _prism_slice(mesh, float(item["z_min_m"]), float(item["z_max_m"])) for mesh in expanded
                ) if piece is not None
            ]
            if not pieces:
                raise RuntimeError(f"no geometry for {item['id']}")
            meshes.append(_merge_meshes(
                str(item["id"]), pieces,
                semantic_surface_id=surface_id,
                floor_index=int(item["floor_index"]),
                floor_band=str(item["band_key"]),
                material_domain="vertical_occupied_floor",
            ))

    shift = 4.1 if floor_count == 6 else 0.0
    for mesh in base["meshes"]:
        name = str(mesh["name"])
        if name in consumed:
            continue
        output = _translate(mesh, shift) if shift and (name in TOP_CROWN_DETAIL_MESHES or _is_roof_landmark(name)) else deepcopy(mesh)
        output["material_domain"] = "roof_only" if _is_roof_landmark(name) else (
            "top_crown_detail" if name in TOP_CROWN_DETAIL_MESHES else "fixed_detail"
        )
        meshes.append(output)

    geometry = {
        "schema": "belle-epoque-segmented-floor-geometry@1",
        "building_id": "grand-magasin-belle-epoque",
        "floor_count": floor_count,
        "unit_floor_height_m": 4.1,
        "wall_top_z_m": round(4.1 * floor_count, 6),
        "source_v92_geometry_sha256": "4a0c2c6514d0a546d3a3154b6766d40797c88b8b3ffb7ce4e1523831be73b815",
        "top_crown_translation_z_m": shift,
        "roof_translation_z_m": shift,
        "sequence": plan["sequence"],
        "meshes": meshes,
    }
    geometry["geometry_sha256"] = _sha256({key: value for key, value in geometry.items() if key != "geometry_sha256"})
    geometry["audit"] = audit_segmented_geometry(geometry, base)
    return geometry


def _bounds(meshes: list[dict[str, Any]]) -> list[float]:
    vertices = [vertex for mesh in meshes for vertex in mesh["vertices"]]
    xs, ys, zs = zip(*vertices)
    return [min(xs), min(ys), min(zs), max(xs), max(ys), max(zs)]


def audit_segmented_geometry(geometry: dict[str, Any], base: dict[str, Any] | None = None) -> dict[str, Any]:
    base = base or build_geometry()
    floors = int(geometry["floor_count"])
    meshes = geometry["meshes"]
    failures: list[dict[str, Any]] = []
    expected_floor_meshes = len(SURFACE_SOURCE_MESHES) * floors
    floor_meshes = [mesh for mesh in meshes if mesh.get("material_domain") == "vertical_occupied_floor"]
    if len(floor_meshes) != expected_floor_meshes:
        failures.append({"code": "floor_addressable_mesh_count", "actual": len(floor_meshes), "expected": expected_floor_meshes})
    too_tall = []
    for mesh in floor_meshes:
        zs = [float(vertex[2]) for vertex in mesh["vertices"]]
        if max(zs) - min(zs) > 4.1 + 1e-6:
            too_tall.append(mesh["name"])
    if too_tall:
        failures.append({"code": "full_height_wall_polygon_after_floor_segmentation", "meshes": too_tall})
    roof_conflicts = [mesh["name"] for mesh in floor_meshes if mesh.get("material_domain") == "roof_only"]
    if roof_conflicts:
        failures.append({"code": "roof_owned_vertical_wall_or_top_crown", "meshes": roof_conflicts})

    original_bounds = _bounds(base["meshes"])
    output_bounds = _bounds(meshes)
    if floors == 5 and any(abs(a - b) > 1e-6 for a, b in zip(original_bounds, output_bounds)):
        failures.append({"code": "five_storey_silhouette_bounds_changed", "source": original_bounds, "segmented": output_bounds})
    if floors == 6:
        if geometry["top_crown_translation_z_m"] != 4.1 or geometry["roof_translation_z_m"] != 4.1:
            failures.append({"code": "six_storey_upper_shift_not_one_module"})
        if abs(output_bounds[5] - original_bounds[5] - 4.1) > 1e-6:
            failures.append({"code": "six_storey_height_delta_mismatch", "source": original_bounds[5], "segmented": output_bounds[5]})

    return {
        "status": "pass" if not failures else "fail",
        "floor_addressable_mesh_count": len(floor_meshes),
        "roof_owned_vertical_wall_conflicts": roof_conflicts,
        "source_bounds_m": original_bounds,
        "segmented_bounds_m": output_bounds,
        "failures": failures,
    }


def write_geometry(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    output.mkdir(parents=True, exist_ok=True)
    payload = {"schema": "belle-epoque-floor-geometry-pilot@1", "variants": {}}
    for floors in (5, 6):
        geometry = build_segmented_geometry(floors)
        payload["variants"][f"{floors}_storey"] = geometry
        (output / f"belle_epoque_{floors}_storey_geometry.json").write_text(json.dumps(geometry, indent=2) + "\n", encoding="utf-8")
    return payload


if __name__ == "__main__":
    built = write_geometry()
    print(json.dumps({key: {"geometry_sha256": value["geometry_sha256"], "audit": value["audit"]["status"]} for key, value in built["variants"].items()}, indent=2))
