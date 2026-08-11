"""Compile and validate V92 carrier-native stickers for the Belle Epoque pilot.

The tool is deliberately fail closed.  It does not create a facade card or
modify clay geometry.  Instead it verifies an architect-approved immutable
``clay_lock.json`` and emits registration instructions for ``carrier_skin``
assemblies that bind the accepted V91 pixels directly to named clay carriers.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import struct
import sys
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[2]
DEFAULT_SPEC = Path(__file__).with_name("belle_epoque_sticker_v92_contract.json")
HEX64 = set("0123456789abcdef")


class ContractError(ValueError):
    """A release-blocking clay or sticker registration error."""


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def resolve_path(raw: str | Path, *, relative_to: Path) -> Path:
    path = Path(raw)
    if path.is_absolute():
        return path
    local = relative_to / path
    return local if local.exists() else REPO / path


def png_size(path: Path) -> tuple[int, int]:
    with path.open("rb") as handle:
        header = handle.read(24)
    if len(header) != 24 or header[:8] != b"\x89PNG\r\n\x1a\n" or header[12:16] != b"IHDR":
        raise ContractError(f"sticker source is not a valid PNG: {path}")
    return struct.unpack(">II", header[16:24])


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and math.isfinite(float(value))


def _numeric_vector(value: Any, length: int, label: str) -> list[float]:
    if not isinstance(value, list) or len(value) != length or not all(_is_number(item) for item in value):
        raise ContractError(f"{label} must contain {length} finite numeric values")
    return [float(item) for item in value]


def load_document(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError(f"cannot read JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ContractError(f"JSON root must be an object: {path}")
    return value


def validate_sources(spec: dict[str, Any]) -> dict[str, dict[str, Any]]:
    verified: dict[str, dict[str, Any]] = {}
    sources = spec.get("source_policy", {}).get("sources", {})
    if not isinstance(sources, dict) or not sources:
        raise ContractError("sticker contract has no accepted sources")
    for source_id, source in sources.items():
        path = resolve_path(source.get("path", ""), relative_to=REPO)
        if not path.is_file():
            raise ContractError(f"accepted sticker is missing: {path}")
        actual_hash = sha256_file(path)
        if actual_hash != source.get("sha256"):
            raise ContractError(f"accepted sticker hash mismatch for {source_id}: {actual_hash}")
        dimensions = list(png_size(path))
        if dimensions != source.get("pixel_size"):
            raise ContractError(f"accepted sticker dimensions changed for {source_id}: {dimensions}")
        crop = source.get("source_crop_xyxy")
        _numeric_vector(crop, 4, f"{source_id}.source_crop_xyxy")
        transform = source.get("source_to_canonical_h")
        if not isinstance(transform, list) or len(transform) != 3:
            raise ContractError(f"{source_id} requires an explicit 3x3 crop transform")
        for row in transform:
            _numeric_vector(row, 3, f"{source_id}.source_to_canonical_h")
        verified[source_id] = {
            **source,
            "path": path.relative_to(REPO).as_posix(),
            "verified_sha256": actual_hash,
        }
    return verified


def validate_clay_lock(clay: dict[str, Any], spec: dict[str, Any], *, lock_path: Path) -> None:
    if clay.get("schema") != "belle-epoque-clay-lock@1":
        raise ContractError("missing or incompatible belle-epoque-clay-lock@1 evidence")
    if clay.get("building_id") != spec.get("building_id"):
        raise ContractError("clay lock belongs to a different building")
    if clay.get("status") != "approved":
        raise ContractError("clay evidence is not approved")
    if clay.get("coordinate_frame") != "x_right_y_rear_z_up_metres":
        raise ContractError("clay lock uses an unsupported coordinate frame")
    geometry_hash = str(clay.get("geometry_sha256", ""))
    if len(geometry_hash) != 64 or any(char not in HEX64 for char in geometry_hash):
        raise ContractError("clay geometry_sha256 is missing or malformed")
    accepted_hash = str(spec.get("accepted_clay_geometry_sha256", ""))
    if geometry_hash != accepted_hash:
        raise ContractError(
            f"clay geometry hash mismatch: expected architect-approved {accepted_hash}, got {geometry_hash}"
        )
    if clay.get("carrier_mode") != "native_surface_material":
        raise ContractError("stickers require native surface material carriers")
    if clay.get("separate_sticker_face_boxes") != "forbidden":
        raise ContractError("V91-style separate full-face sticker boxes are forbidden")

    immutable = clay.get("immutable", {})
    for key in ("geometry", "object_transforms", "cameras", "void_contours", "roof_topology"):
        if immutable.get(key) is not True:
            raise ContractError(f"clay lock must make {key} immutable")

    gate_path = resolve_path(clay.get("gate_report", ""), relative_to=lock_path.parent)
    gates = load_document(gate_path) if gate_path.is_file() else None
    if gates is None or gates.get("status") != "pass":
        raise ContractError("clay gate report is missing or not passing")
    failed_gates = [gate.get("id", "unnamed") for gate in gates.get("gates", []) if gate.get("passed") is not True]
    if failed_gates:
        raise ContractError(f"clay gate report contains failures: {', '.join(failed_gates)}")

    entrance = clay.get("entrance", {})
    if entrance.get("topology") != spec.get("required_entrance_topology"):
        raise ContractError("straight-front or multi-bay entrance topology is forbidden")
    if entrance.get("carrier_surface_id") != "corner_pavilion":
        raise ContractError("principal entrance must be registered on the wrapped corner carrier")
    if float(entrance.get("depth_m", 0.0)) < 4.0 or float(entrance.get("clear_ray_fraction", 0.0)) < 0.95:
        raise ContractError("wrapped entrance does not provide a clear deep tunnel")
    contours = entrance.get("contour_uv")
    if not isinstance(contours, list) or len(contours) != 1:
        raise ContractError("V92 entrance requires exactly one wrapped-corner contour loop")
    contour_hash = sha256_bytes(canonical_bytes(contours))
    if contour_hash != entrance.get("contour_sha256"):
        raise ContractError("entrance contour hash does not match its canonical UV loops")

    ownership = clay.get("feature_ownership", {})
    geometry_features = set(ownership.get("geometry", []))
    sticker_features = set(ownership.get("sticker", []))
    if not ownership.get("duplicate_ownership_forbidden") or geometry_features & sticker_features:
        raise ContractError("feature ownership duplicates geometry and sticker responsibilities")

    budgets = clay.get("budgets", {})
    if int(budgets.get("final_glb_max_bytes", 0)) > int(spec["atlas_budget"]["assembled_glb_bytes_max"]):
        raise ContractError("clay delivery budget exceeds the sticker contract GLB limit")
    if float(budgets.get("native_carrier_offset_max_m", 1.0)) > 0.003:
        raise ContractError("native carrier offset exceeds the 3 mm limit")


def validate_surfaces(clay: dict[str, Any], spec: dict[str, Any]) -> dict[str, dict[str, Any]]:
    surfaces = clay.get("surfaces")
    if not isinstance(surfaces, list) or not surfaces:
        raise ContractError("clay lock has no exposed native carriers")
    by_id: dict[str, dict[str, Any]] = {}
    roles: set[str] = set()
    for surface in surfaces:
        surface_id = str(surface.get("surface_id", ""))
        role = str(surface.get("role", ""))
        if not surface_id or surface_id in by_id:
            raise ContractError(f"duplicate or missing surface_id: {surface_id!r}")
        if surface.get("exposed") is not True:
            raise ContractError(f"registered carrier is not marked exposed: {surface_id}")
        if not surface.get("carrier_mesh"):
            raise ContractError(f"surface has no native carrier mesh: {surface_id}")
        if surface.get("kind") in {"box", "facade_skin", "sticker_box"}:
            raise ContractError(f"V91-style sticker carrier found: {surface_id}")
        thickness = float(surface.get("carrier_thickness_m", 0.0))
        if thickness > float(spec["registration_thresholds"]["full_face_carrier_thickness_m_max"]):
            raise ContractError(f"separate thick sticker carrier found: {surface_id} ({thickness} m)")
        boundary = surface.get("boundary_m")
        if not isinstance(boundary, list) or len(boundary) < 4:
            raise ContractError(f"surface boundary is incomplete: {surface_id}")
        for index, point in enumerate(boundary):
            _numeric_vector(point, 3, f"{surface_id}.boundary_m[{index}]")
        expected_instruction = spec.get("mapping_for_role", {}).get(role)
        if expected_instruction is None:
            raise ContractError(f"exposed surface has no sticker owner: {surface_id} ({role})")
        expected_clay_mapping = {
            "planar_anchored": "planar",
            "roof_plan_shared": "planar",
            "radial_dome": "radial",
            "cylindrical_arc_length": "cylindrical",
        }[expected_instruction]
        if surface.get("mapping") != expected_clay_mapping:
            raise ContractError(
                f"{surface_id} requires {expected_clay_mapping} clay mapping, got {surface.get('mapping')}"
            )
        by_id[surface_id] = surface
        roles.add(role)
    missing_roles = sorted(set(spec.get("required_surface_roles", [])) - roles)
    if missing_roles:
        raise ContractError(f"clay lock is missing required exposed roles: {', '.join(missing_roles)}")
    return by_id


def reciprocal_seams(clay: dict[str, Any], surfaces: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str, str]] = set()
    touched: set[str] = set()
    for index, seam in enumerate(clay.get("adjacency", [])):
        a, b = seam.get("a", {}), seam.get("b", {})
        a_id, b_id = str(a.get("surface_id", "")), str(b.get("surface_id", ""))
        a_edge, b_edge = str(a.get("edge_id", "")), str(b.get("edge_id", ""))
        if a_id not in surfaces or b_id not in surfaces or not a_edge or not b_edge:
            raise ContractError(f"adjacency {index} references an unknown surface or edge")
        key = (a_id, a_edge, b_id, b_edge)
        inverse = (b_id, b_edge, a_id, a_edge)
        if key in seen or inverse in seen:
            raise ContractError(f"duplicate adjacency for {a_id}:{a_edge} and {b_id}:{b_edge}")
        if seam.get("mode") not in {"covered_joint", "hard_material_joint", "continuous_wrap"} or not seam.get("cover_object"):
            raise ContractError(f"bare or ownerless sticker seam: {a_id}:{a_edge} -> {b_id}:{b_edge}")
        seen.add(key)
        touched.update((a_id, b_id))
        seam_id = f"seam_{index:02d}_{a_id}_{b_id}"
        common = {
            "seam_id": seam_id,
            "owner_type": "geometry_cover",
            "owner_id": seam["cover_object"],
            "mode": seam["mode"],
            "sticker_overlap_m": 0.0,
            "uv_gutter_px": 16,
        }
        output.extend((
            {**common, "from_surface": a_id, "from_edge": a_edge, "to_surface": b_id, "to_edge": b_edge},
            {**common, "from_surface": b_id, "from_edge": b_edge, "to_surface": a_id, "to_edge": a_edge},
        ))
    missing = sorted(set(surfaces) - touched)
    if missing:
        raise ContractError(f"exposed surfaces have no reciprocal seam registration: {', '.join(missing)}")
    return output


def _surface_bounds(surface: dict[str, Any]) -> tuple[float, float, float, float, float, float]:
    points = surface["boundary_m"]
    xs, ys, zs = zip(*points)
    return min(xs), max(xs), min(ys), max(ys), min(zs), max(zs)


def _planar_anchors(surface: dict[str, Any], wall_height: float) -> list[dict[str, Any]]:
    boundary = surface["boundary_m"]
    anchors: list[dict[str, Any]] = []
    corner_uv = ([0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0])
    for index, point in enumerate(boundary[:4]):
        uv = list(corner_uv[index])
        anchors.append({
            "anchor_id": f"boundary_{index}", "kind": "boundary_corner",
            "object_space_m": point, "surface_uv": uv, "source_uv": uv,
        })
    z_min, z_max = _surface_bounds(surface)[4:]
    if z_max - z_min >= wall_height * 0.8:
        for floor in range(1, 5):
            v = (floor * wall_height / 5.0 - z_min) / max(z_max - z_min, 1e-9)
            if 0.0 < v < 1.0:
                anchors.append({
                    "anchor_id": f"floor_datum_{floor}", "kind": "floor_datum",
                    "object_space_m": [
                        sum(point[0] for point in boundary[:4]) / 4,
                        sum(point[1] for point in boundary[:4]) / 4,
                        floor * wall_height / 5.0,
                    ],
                    "surface_uv": [0.5, v], "source_uv": [0.5, v],
                })
    return anchors


def _roof_plan_anchors(surface: dict[str, Any], plan_bounds: list[float]) -> list[dict[str, Any]]:
    x0, x1, y0, y1 = plan_bounds
    anchors = []
    for index, point in enumerate(surface["boundary_m"]):
        uv = [(point[0] - x0) / (x1 - x0), (point[1] - y0) / (y1 - y0)]
        anchors.append({
            "anchor_id": f"plan_boundary_{index}", "kind": "roof_plan_point",
            "object_space_m": point, "surface_uv": uv, "source_uv": uv,
        })
    return anchors


def _named_anchor_xy(clay: dict[str, Any], anchor_id: str) -> list[float]:
    matches = [anchor for anchor in clay.get("anchors", []) if anchor.get("anchor_id") == anchor_id]
    if len(matches) != 1:
        raise ContractError(f"clay lock requires exactly one {anchor_id!r} curved-mapping anchor")
    point = _numeric_vector(matches[0].get("object_space_m"), 3, f"anchors.{anchor_id}.object_space_m")
    return point[:2]


def _front_left_curve_centre_from_boundary(surface: dict[str, Any]) -> list[float]:
    """Recover the southwest pavilion centre from its locked arc envelope.

    The facade, canopy and two cornice profiles use different inner/outer
    radii, so a circumcircle fit is not stable across their compact boundary
    schedules.  Their common centre is the northeast corner of the southwest
    quadrant envelope: maximum X and maximum Y in the authored plan points.
    """
    unique: list[tuple[float, float]] = []
    for raw_point in surface["boundary_m"]:
        point = (float(raw_point[0]), float(raw_point[1]))
        if not any(math.dist(point, existing) <= 1e-6 for existing in unique):
            unique.append(point)
    if len(unique) < 3:
        raise ContractError(f"cannot derive cylindrical centre from clay boundary: {surface.get('surface_id', 'unknown')}")
    return [max(point[0] for point in unique), max(point[1] for point in unique)]


def _curved_anchors(surface: dict[str, Any], clay: dict[str, Any], mapping: str) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    role = surface["role"]
    boundary = surface["boundary_m"]
    if role.startswith("central_"):
        centre = _named_anchor_xy(clay, "central_dome_centre")
    elif role.startswith(("corner_cupola", "corner_upper_tower", "corner_tower_crown")):
        centre = _named_anchor_xy(clay, "corner_cupola_centre")
    else:
        # Pavilion, corner cornices and canopy share the rounded footprint
        # centre.  The entrance-axis anchor is on the outer opening and is not
        # a valid UV origin; derive the centre from the locked arc itself.
        centre = _front_left_curve_centre_from_boundary(surface)
    z_min, z_max = _surface_bounds(surface)[4:]
    mapping_parameters = {
        "centre_xy_m": centre,
        "theta_zero_axis_xy": [1.0, 0.0],
        "theta_direction": "counter_clockwise",
        "seam_angle_deg": 180.0,
        "v_mode": "meridional_arc_fraction" if mapping == "radial_dome" else "height_fraction",
    }
    anchors = []
    for index, point in enumerate(boundary):
        dx, dy = point[0] - centre[0], point[1] - centre[1]
        theta = math.atan2(dy, dx)
        u = (theta / (2 * math.pi)) % 1.0
        v = (point[2] - z_min) / max(z_max - z_min, 1e-9)
        anchors.append({
            "anchor_id": f"curved_{index}",
            "kind": "dome_anchor" if mapping == "radial_dome" else "arc_anchor",
            "object_space_m": point, "surface_uv": [u, v], "source_uv": [u, v],
        })
    if len(anchors) < 4:
        raise ContractError(f"curved carrier has fewer than four numeric anchors: {surface['surface_id']}")
    return anchors, mapping_parameters


def build_registration(
    clay: dict[str, Any], spec: dict[str, Any], *, lock_path: Path, assembled_glb: Path | None = None
) -> dict[str, Any]:
    validate_clay_lock(clay, spec, lock_path=lock_path)
    sources = validate_sources(spec)
    surfaces = validate_surfaces(clay, spec)
    seams = reciprocal_seams(clay, surfaces)
    dimensions = clay["dimensions"]
    wall_height = float(dimensions["wall_height_m"])
    all_points = [point for surface in surfaces.values() for point in surface["boundary_m"]]
    plan_bounds = [
        min(point[0] for point in all_points), max(point[0] for point in all_points),
        min(point[1] for point in all_points), max(point[1] for point in all_points),
    ]
    assemblies = []
    for surface_id, surface in surfaces.items():
        role = surface["role"]
        mapping = spec["mapping_for_role"][role]
        if mapping == "planar_anchored":
            anchors = _planar_anchors(surface, wall_height)
            parameters = {"solver": "least_squares_homography", "preserve_aspect": True}
        elif mapping == "roof_plan_shared":
            anchors = _roof_plan_anchors(surface, plan_bounds)
            parameters = {"shared_plan_bounds_m": plan_bounds, "projector": "global_xy"}
        else:
            anchors, parameters = _curved_anchors(surface, clay, mapping)
        if len(anchors) < int(spec["registration_thresholds"]["minimum_planar_anchor_count"]):
            raise ContractError(f"surface has too few explicit numeric anchors: {surface_id}")
        source_id = spec["source_for_role"][role]
        assemblies.append({
            "id": f"sticker_{surface_id}",
            "kind": "carrier_skin",
            "carrier_mode": "native_surface_material",
            "carrier_surface_id": surface_id,
            "carrier_mesh": surface["carrier_mesh"],
            "surface_role": role,
            "mapping": mapping,
            "mapping_parameters": parameters,
            "registration_anchors": anchors,
            "source_id": source_id,
            "source_path": sources[source_id]["path"],
            "source_sha256": sources[source_id]["verified_sha256"],
            "source_crop_xyxy": sources[source_id]["source_crop_xyxy"],
            "source_to_canonical_h": sources[source_id]["source_to_canonical_h"],
            "material_binding": {
                "albedo": "registered_sticker_atlas",
                "normal": "construction_role_metric_pbr",
                "roughness": "construction_role_metric_pbr",
                "apply_to_existing_carrier": True,
                "create_geometry": False,
                "carrier_offset_m": 0.0,
            },
        })

    contour_hash = clay["entrance"]["contour_sha256"]
    glb_bytes = assembled_glb.stat().st_size if assembled_glb is not None else None
    max_glb = int(spec["atlas_budget"]["assembled_glb_bytes_max"])
    if glb_bytes is not None and glb_bytes > max_glb:
        raise ContractError(f"assembled GLB is {glb_bytes} bytes; V92 limit is {max_glb}")
    lock_hash = sha256_file(lock_path)
    return {
        "schema": "belle-epoque-sticker-registration@1",
        "building_id": spec["building_id"],
        "pipeline": spec["pipeline"],
        "status": "delivery_pass" if glb_bytes is not None else "registration_ready_pending_atlas_and_glb",
        "clay_lock": {
            "path": lock_path.relative_to(REPO).as_posix() if lock_path.is_relative_to(REPO) else str(lock_path),
            "file_sha256": lock_hash,
            "geometry_sha256": clay["geometry_sha256"],
            "immutable_geometry_required": True,
        },
        "entrance_clearance": {
            "carrier_surface_id": clay["entrance"]["carrier_surface_id"],
            "topology": clay["entrance"]["topology"],
            "contour_sha256": contour_hash,
            "geometry_contour_sha256": contour_hash,
            "sticker_contour_sha256": contour_hash,
            "contour_uv": clay["entrance"]["contour_uv"],
            "operation": "clip carrier albedo and UV coverage by the identical contour; geometry owns jambs, soffit and 4.2 m tunnel",
        },
        "feature_ownership": clay["feature_ownership"],
        "surface_coverage": {
            "exposed_surface_count": len(surfaces),
            "registered_surface_count": len(assemblies),
            "unowned_exposed_surfaces": [],
        },
        "assemblies": assemblies,
        "reciprocal_seams": seams,
        "atlas_plan": {
            **spec["atlas_budget"],
            "opaque_atlas_count": 1,
            "alpha_glass_atlas_count_max": 1,
            "packing": "pack after registration; 16 px dilated gutters; preserve alpha losslessly",
            "material_slots": ["opaque_sticker_pbr", "glass_sticker_pbr", "roof_sticker_pbr"],
        },
        "delivery_measurements": {
            "assembled_glb_bytes": glb_bytes,
            "assembled_glb_bytes_max": max_glb,
            "within_glb_budget": None if glb_bytes is None else True,
        },
        "hard_stops": spec["hard_stops"],
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--clay-lock", type=Path, required=True)
    parser.add_argument("--contract", type=Path, default=DEFAULT_SPEC)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--assembled-glb", type=Path)
    parser.add_argument("--check", action="store_true", help="validate without writing registration JSON")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        lock_path = args.clay_lock.resolve()
        clay = load_document(lock_path)
        spec = load_document(args.contract.resolve())
        glb = args.assembled_glb.resolve() if args.assembled_glb else None
        registration = build_registration(clay, spec, lock_path=lock_path, assembled_glb=glb)
        if not args.check:
            if args.output is None:
                raise ContractError("--output is required unless --check is used")
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(registration, indent=2) + "\n", encoding="utf-8")
        print(
            f"[belle-epoque-sticker-v92] {registration['status']}: "
            f"{registration['surface_coverage']['registered_surface_count']} native carriers, "
            f"{len(registration['reciprocal_seams']) // 2} owned seams"
        )
        return 0
    except ContractError as exc:
        print(f"[belle-epoque-sticker-v92] HARD STOP: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
