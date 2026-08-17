#!/usr/bin/env python3
"""Fast, read-only preflight for the shared City Prompt model-library seed.

The audit reads only each GLB's JSON header. It does not decode textures or
vertex buffers, so it can check the entire multi-gigabyte seed quickly while
still proving the contracts that affect runtime seating and smooth shading:

* every catalogue URL resolves to a hydrated seed object;
* every GLB is structurally readable and self-contained;
* every rendered primitive has positions and normals;
* LEGO geometry has finite bounds and sits on the Y=0 ground datum; and
* stackable LEGO modules reach the declared datum used by the next module; and
* declared dimensions remain compatible with the authored geometry.

Performance risks such as excessive primitives, triangles, materials, or file
size are warnings. Broken references, missing normals, malformed GLBs, and
grounding-contract violations are errors.
"""
from __future__ import annotations

import argparse
import json
import math
import struct
import sys
from collections import defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import urlparse


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SEED_DIR = REPO_ROOT / "seed" / "model-library"
GLB_MAGIC = b"glTF"
JSON_CHUNK_TYPE = 0x4E4F534A
BOTTOM_TOLERANCE_M = 0.02
FOOTPRINT_TOLERANCE_M = 0.6
ROOF_OVERHANG_ALLOWANCE_M = 1.4
FRONT_PROTRUSION_ALLOWANCE_M = 3.0
HEIGHT_TOLERANCE_M = 1.2
MAX_EXTENT_M = 500.0
TRIANGLE_WARN_THRESHOLD = 80_000
MATERIAL_WARN_THRESHOLD = 14
PRIMITIVE_WARN_THRESHOLD = 128
SIZE_WARN_BYTES = 8 * 1024 * 1024


class AuditError(ValueError):
    """An actionable problem with a seed object or catalogue contract."""


@dataclass(frozen=True)
class Bounds:
    minimum: tuple[float, float, float]
    maximum: tuple[float, float, float]

    @property
    def extents(self) -> tuple[float, float, float]:
        return tuple(self.maximum[i] - self.minimum[i] for i in range(3))  # type: ignore[return-value]


@dataclass(frozen=True)
class GlbStats:
    path: str
    size_bytes: int
    bounds: Bounds
    primitives: int
    triangles: int
    materials: int
    images: int
    missing_normal_primitives: int


def _mat_mul(a: tuple[float, ...], b: tuple[float, ...]) -> tuple[float, ...]:
    """Multiply two glTF column-major 4x4 matrices."""
    return tuple(
        sum(a[k * 4 + row] * b[col * 4 + k] for k in range(4))
        for col in range(4)
        for row in range(4)
    )


def _node_matrix(node: dict[str, Any]) -> tuple[float, ...]:
    raw_matrix = node.get("matrix")
    if isinstance(raw_matrix, list) and len(raw_matrix) == 16:
        return tuple(float(value) for value in raw_matrix)

    tx, ty, tz = (float(value) for value in node.get("translation", [0, 0, 0]))
    sx, sy, sz = (float(value) for value in node.get("scale", [1, 1, 1]))
    x, y, z, w = (float(value) for value in node.get("rotation", [0, 0, 0, 1]))

    translation = (
        1.0, 0.0, 0.0, 0.0,
        0.0, 1.0, 0.0, 0.0,
        0.0, 0.0, 1.0, 0.0,
        tx, ty, tz, 1.0,
    )
    rotation = (
        1 - 2 * (y * y + z * z), 2 * (x * y + z * w), 2 * (x * z - y * w), 0.0,
        2 * (x * y - z * w), 1 - 2 * (x * x + z * z), 2 * (y * z + x * w), 0.0,
        2 * (x * z + y * w), 2 * (y * z - x * w), 1 - 2 * (x * x + y * y), 0.0,
        0.0, 0.0, 0.0, 1.0,
    )
    scale = (
        sx, 0.0, 0.0, 0.0,
        0.0, sy, 0.0, 0.0,
        0.0, 0.0, sz, 0.0,
        0.0, 0.0, 0.0, 1.0,
    )
    return _mat_mul(_mat_mul(translation, rotation), scale)


IDENTITY_MATRIX = (
    1.0, 0.0, 0.0, 0.0,
    0.0, 1.0, 0.0, 0.0,
    0.0, 0.0, 1.0, 0.0,
    0.0, 0.0, 0.0, 1.0,
)


def _transform_point(matrix: tuple[float, ...], point: tuple[float, float, float]) -> tuple[float, float, float]:
    x, y, z = point
    return (
        matrix[0] * x + matrix[4] * y + matrix[8] * z + matrix[12],
        matrix[1] * x + matrix[5] * y + matrix[9] * z + matrix[13],
        matrix[2] * x + matrix[6] * y + matrix[10] * z + matrix[14],
    )


def _transform_bounds(bounds: Bounds, matrix: tuple[float, ...]) -> Bounds:
    corners = [
        _transform_point(matrix, (x, y, z))
        for x in (bounds.minimum[0], bounds.maximum[0])
        for y in (bounds.minimum[1], bounds.maximum[1])
        for z in (bounds.minimum[2], bounds.maximum[2])
    ]
    return Bounds(
        tuple(min(point[i] for point in corners) for i in range(3)),  # type: ignore[arg-type]
        tuple(max(point[i] for point in corners) for i in range(3)),  # type: ignore[arg-type]
    )


def _merge_bounds(bounds: Iterable[Bounds]) -> Bounds:
    items = list(bounds)
    if not items:
        raise AuditError("GLB contains no scene-referenced mesh bounds")
    return Bounds(
        tuple(min(item.minimum[i] for item in items) for i in range(3)),  # type: ignore[arg-type]
        tuple(max(item.maximum[i] for item in items) for i in range(3)),  # type: ignore[arg-type]
    )


def _read_glb_json(path: Path) -> dict[str, Any]:
    size = path.stat().st_size
    if size < 200:
        raise AuditError("file is a Git LFS pointer or otherwise too small")
    with path.open("rb") as stream:
        header = stream.read(12)
        if len(header) != 12:
            raise AuditError("truncated GLB header")
        magic, version, declared_length = struct.unpack("<4sII", header)
        if magic != GLB_MAGIC:
            raise AuditError("invalid GLB magic")
        if version != 2:
            raise AuditError(f"unsupported GLB version {version}")
        if declared_length != size:
            raise AuditError(f"GLB length header says {declared_length} bytes; file has {size}")
        chunk_header = stream.read(8)
        if len(chunk_header) != 8:
            raise AuditError("missing GLB JSON chunk")
        chunk_length, chunk_type = struct.unpack("<II", chunk_header)
        if chunk_type != JSON_CHUNK_TYPE:
            raise AuditError("first GLB chunk is not JSON")
        raw_json = stream.read(chunk_length)
        if len(raw_json) != chunk_length:
            raise AuditError("truncated GLB JSON chunk")
    try:
        payload = json.loads(raw_json.decode("utf-8").rstrip(" \t\r\n\0"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise AuditError(f"invalid GLB JSON ({exc})") from exc
    if payload.get("asset", {}).get("version") != "2.0":
        raise AuditError("GLB JSON does not declare glTF 2.0")
    return payload


def _primitive_triangles(primitive: dict[str, Any], accessors: list[dict[str, Any]]) -> int:
    accessor_index = primitive.get("indices")
    if accessor_index is None:
        accessor_index = primitive.get("attributes", {}).get("POSITION")
    if not isinstance(accessor_index, int) or not 0 <= accessor_index < len(accessors):
        return 0
    count = int(accessors[accessor_index].get("count", 0))
    mode = int(primitive.get("mode", 4))
    if mode == 4:
        return count // 3
    if mode in (5, 6):
        return max(0, count - 2)
    return 0


def inspect_glb(path: Path, *, display_path: str | None = None) -> GlbStats:
    payload = _read_glb_json(path)
    accessors = payload.get("accessors") or []
    meshes = payload.get("meshes") or []
    nodes = payload.get("nodes") or []
    if not isinstance(accessors, list) or not isinstance(meshes, list) or not isinstance(nodes, list):
        raise AuditError("accessors, meshes, and nodes must be arrays")

    for collection_name in ("buffers", "images"):
        for item in payload.get(collection_name) or []:
            uri = item.get("uri")
            if isinstance(uri, str) and not uri.startswith("data:"):
                raise AuditError(f"GLB is not self-contained ({collection_name[:-1]} URI: {uri})")

    scene_index = payload.get("scene", 0)
    scenes = payload.get("scenes") or []
    if scenes and isinstance(scene_index, int) and 0 <= scene_index < len(scenes):
        roots = scenes[scene_index].get("nodes") or []
    else:
        children = {child for node in nodes for child in node.get("children", []) if isinstance(child, int)}
        roots = [index for index in range(len(nodes)) if index not in children]

    scene_bounds: list[Bounds] = []
    primitive_count = triangle_count = missing_normals = 0
    used_materials: set[int] = set()

    def visit(node_index: int, parent_matrix: tuple[float, ...], ancestors: frozenset[int]) -> None:
        nonlocal primitive_count, triangle_count, missing_normals
        if node_index in ancestors:
            raise AuditError(f"scene graph cycle at node {node_index}")
        if not 0 <= node_index < len(nodes):
            raise AuditError(f"scene references missing node {node_index}")
        node = nodes[node_index]
        world = _mat_mul(parent_matrix, _node_matrix(node))
        mesh_index = node.get("mesh")
        if mesh_index is not None:
            if not isinstance(mesh_index, int) or not 0 <= mesh_index < len(meshes):
                raise AuditError(f"node {node_index} references missing mesh {mesh_index}")
            for primitive in meshes[mesh_index].get("primitives") or []:
                primitive_count += 1
                attributes = primitive.get("attributes") or {}
                position_index = attributes.get("POSITION")
                if not isinstance(position_index, int) or not 0 <= position_index < len(accessors):
                    raise AuditError(f"mesh {mesh_index} primitive has no valid POSITION accessor")
                accessor = accessors[position_index]
                minimum = accessor.get("min")
                maximum = accessor.get("max")
                if not (
                    isinstance(minimum, list) and len(minimum) == 3
                    and isinstance(maximum, list) and len(maximum) == 3
                ):
                    raise AuditError(f"mesh {mesh_index} POSITION accessor lacks min/max bounds")
                local = Bounds(tuple(map(float, minimum)), tuple(map(float, maximum)))
                if not all(math.isfinite(value) for value in (*local.minimum, *local.maximum)):
                    raise AuditError(f"mesh {mesh_index} has non-finite bounds")
                scene_bounds.append(_transform_bounds(local, world))
                if "NORMAL" not in attributes:
                    missing_normals += 1
                material = primitive.get("material")
                if isinstance(material, int):
                    used_materials.add(material)
                triangle_count += _primitive_triangles(primitive, accessors)
        next_ancestors = ancestors | {node_index}
        for child in node.get("children") or []:
            if not isinstance(child, int):
                raise AuditError(f"node {node_index} has a non-integer child")
            visit(child, world, next_ancestors)

    for root in roots:
        if not isinstance(root, int):
            raise AuditError("scene has a non-integer root node")
        visit(root, IDENTITY_MATRIX, frozenset())

    bounds = _merge_bounds(scene_bounds)
    if any(extent <= 1e-6 for extent in bounds.extents):
        raise AuditError(f"degenerate GLB extents {bounds.extents}")
    if max(bounds.extents) > MAX_EXTENT_M:
        raise AuditError(f"absurd GLB extent {max(bounds.extents):.2f} m (limit {MAX_EXTENT_M} m)")

    return GlbStats(
        path=display_path or str(path),
        size_bytes=path.stat().st_size,
        bounds=bounds,
        primitives=primitive_count,
        triangles=triangle_count,
        materials=len(used_materials),
        images=len(payload.get("images") or []),
        missing_normal_primitives=missing_normals,
    )


def object_path_from_url(url: str, objects_dir: Path) -> Path:
    parts = [part for part in urlparse(url).path.split("/") if part]
    try:
        library_index = parts.index("library")
    except ValueError as exc:
        raise AuditError(f"URL has no /library/ object key: {url}") from exc
    relative = parts[library_index + 1 :]
    if not relative or any(part in (".", "..") for part in relative):
        raise AuditError(f"URL has an invalid library object key: {url}")
    return objects_dir.joinpath(*relative)


def _validate_lego_contract(stats: GlbStats, lego: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    contract = lego.get("coordinate_contract") or {}
    if contract.get("units") != "metres":
        errors.append("coordinate contract must declare metre units")
    if contract.get("origin") != "bottom centre":
        errors.append("coordinate contract must declare a bottom-centre origin")
    if stats.missing_normal_primitives:
        errors.append(f"{stats.missing_normal_primitives} primitive(s) have no NORMAL accessor")

    min_y = stats.bounds.minimum[1]
    if abs(min_y) > BOTTOM_TOLERANCE_M:
        errors.append(
            f"bottom sits at Y={min_y:.3f} m; expected +/-{BOTTOM_TOLERANCE_M:.2f} m"
        )

    width = float(lego.get("width_m") or 0)
    depth = float(lego.get("depth_m") or 0)
    height = float(lego.get("height_m") or 0)
    if min(width, depth, height) <= 0:
        errors.append("declared LEGO dimensions must all be positive")
    elif lego.get("role") not in ("roof", "assembled", "attachment"):
        # The planner positions the next level at this declared height. A
        # module whose geometry ends below that datum leaves the next level
        # visibly floating even though both assets individually start at Y=0.
        # Geometry above the datum is allowed: parapets, cornices, canopies,
        # and other facade details commonly cross the structural stack seam.
        top_y = stats.bounds.maximum[1]
        if top_y < height - BOTTOM_TOLERANCE_M:
            errors.append(
                f"top ends at Y={top_y:.3f} m, below the next-module datum "
                f"Y={height:.3f} m by more than {BOTTOM_TOLERANCE_M:.2f} m"
            )
    return errors


def _dimension_warnings(stats: GlbStats, lego: dict[str, Any]) -> list[str]:
    """Report fit-envelope drift without blocking a seed.

    Runtime base-lift and terrain seating depend on the vertical datum and are
    hard contracts. Width/depth/height drift is still important, but landmark
    appendages and legacy roof packages intentionally exceed their nominal fit
    envelopes, so those differences belong in the optimization backlog rather
    than making a clean clone impossible to seed.
    """
    warnings: list[str] = []
    extent_x, extent_y, extent_z = stats.bounds.extents
    role = str(lego.get("role") or "")
    allow_inset = bool(lego.get("allow_inset_footprint"))
    width = float(lego.get("width_m") or 0)
    depth = float(lego.get("depth_m") or 0)
    height = float(lego.get("height_m") or 0)
    if min(width, depth, height) <= 0:
        return warnings

    roof_allowance = ROOF_OVERHANG_ALLOWANCE_M if role in ("roof", "assembled") else 0.0
    width_tolerance = FOOTPRINT_TOLERANCE_M + roof_allowance
    if allow_inset:
        if extent_x > width + width_tolerance:
            warnings.append(f"X extent {extent_x:.2f} m exceeds inset envelope {width + width_tolerance:.2f} m")
    elif abs(extent_x - width) > width_tolerance:
        warnings.append(f"X extent {extent_x:.2f} m vs declared width {width:.2f} m")

    if allow_inset:
        if extent_z > depth + FRONT_PROTRUSION_ALLOWANCE_M + roof_allowance:
            warnings.append(f"Z extent {extent_z:.2f} m exceeds inset depth envelope")
    elif extent_z < depth - FOOTPRINT_TOLERANCE_M:
        warnings.append(f"Z extent {extent_z:.2f} m is smaller than declared depth {depth:.2f} m")
    elif extent_z > depth + FRONT_PROTRUSION_ALLOWANCE_M + roof_allowance:
        warnings.append(f"Z extent {extent_z:.2f} m exceeds declared depth allowances")

    if abs(extent_y - height) > HEIGHT_TOLERANCE_M:
        warnings.append(f"Y extent {extent_y:.2f} m vs declared height {height:.2f} m")
    if (
        role not in ("roof", "assembled", "attachment")
        and stats.bounds.maximum[1] > height + BOTTOM_TOLERANCE_M
    ):
        warnings.append(
            f"upper geometry extends {stats.bounds.maximum[1] - height:.3f} m "
            "above the next-module datum; visually verify the seam-crossing detail"
        )
    return warnings


def _performance_warnings(stats: GlbStats) -> list[str]:
    warnings: list[str] = []
    if stats.triangles > TRIANGLE_WARN_THRESHOLD:
        warnings.append(f"{stats.triangles:,} triangles exceeds the {TRIANGLE_WARN_THRESHOLD:,} warning budget")
    if stats.materials > MATERIAL_WARN_THRESHOLD:
        warnings.append(f"{stats.materials} materials exceeds the {MATERIAL_WARN_THRESHOLD} warning budget")
    if stats.primitives > PRIMITIVE_WARN_THRESHOLD:
        warnings.append(f"{stats.primitives} primitives may cause excessive draw calls")
    if stats.size_bytes > SIZE_WARN_BYTES:
        warnings.append(f"{stats.size_bytes / 1_048_576:.1f} MB exceeds the {SIZE_WARN_BYTES // 1_048_576} MB warning budget")
    return warnings


def audit_seed_library(seed_dir: Path = DEFAULT_SEED_DIR, *, limit: int | None = None) -> dict[str, Any]:
    rows_path = seed_dir / "model_library.json"
    objects_dir = seed_dir / "objects"
    try:
        payload = json.loads(rows_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"status": "fail", "errors": [f"model_library.json is unreadable: {exc}"], "warnings": [], "assets": []}

    rows = payload.get("rows")
    if not isinstance(rows, list):
        return {"status": "fail", "errors": ["model_library.json has no rows array"], "warnings": [], "assets": []}

    references: dict[Path, list[tuple[dict[str, Any], str]]] = defaultdict(list)
    top_errors: list[str] = []
    for row in rows:
        urls: list[tuple[str, str]] = []
        if isinstance(row.get("model_url"), str):
            urls.append(("model_url", row["model_url"]))
        for lod, url in (row.get("lod_urls") or {}).items():
            if isinstance(url, str):
                urls.append((f"lod_urls.{lod}", url))
        if isinstance(row.get("thumbnail_url"), str):
            urls.append(("thumbnail_url", row["thumbnail_url"]))
        for label, url in urls:
            try:
                references[object_path_from_url(url, objects_dir)].append((row, label))
            except AuditError as exc:
                top_errors.append(f"row {row.get('id')}: {exc}")

    referenced_glbs = {path for path in references if path.suffix.lower() == ".glb"}
    disk_glbs = set(objects_dir.rglob("*.glb")) if objects_dir.is_dir() else set()
    glb_paths = sorted(referenced_glbs | disk_glbs)
    if limit is not None:
        glb_paths = glb_paths[: max(0, limit)]

    for path in references:
        if path.suffix.lower() != ".glb" and not path.is_file():
            top_errors.append(f"referenced object is missing: {path.relative_to(seed_dir).as_posix()}")

    asset_reports: list[dict[str, Any]] = []
    all_errors = list(top_errors)
    all_warnings: list[str] = []
    for path in glb_paths:
        display_path = path.relative_to(seed_dir).as_posix()
        asset_errors: list[str] = []
        asset_warnings: list[str] = []
        if not path.is_file():
            asset_errors.append("referenced object is missing")
            stats = None
        else:
            try:
                stats = inspect_glb(path, display_path=display_path)
            except (AuditError, OSError, struct.error) as exc:
                stats = None
                asset_errors.append(str(exc))

        if stats is not None:
            asset_warnings.extend(_performance_warnings(stats))
            for row, _label in references[path]:
                lego = (row.get("metadata") or {}).get("lego")
                if isinstance(lego, dict):
                    asset_errors.extend(_validate_lego_contract(stats, lego))
                    asset_warnings.extend(_dimension_warnings(stats, lego))
            if stats.missing_normal_primitives and not any(
                "NORMAL accessor" in error for error in asset_errors
            ):
                asset_errors.append(f"{stats.missing_normal_primitives} primitive(s) have no NORMAL accessor")
            if path not in referenced_glbs:
                asset_warnings.append("seed GLB is not referenced by any catalogue row")

        row_ids = sorted({str(row.get("id")) for row, _label in references[path]})
        report: dict[str, Any] = {
            "path": display_path,
            "row_ids": row_ids,
            "status": "fail" if asset_errors else "pass",
            "errors": sorted(set(asset_errors)),
            "warnings": sorted(set(asset_warnings)),
        }
        if stats is not None:
            report["stats"] = asdict(stats)
        asset_reports.append(report)
        all_errors.extend(f"{display_path}: {error}" for error in report["errors"])
        all_warnings.extend(f"{display_path}: {warning}" for warning in report["warnings"])

    return {
        "status": "fail" if all_errors else "pass",
        "rows": len(rows),
        "referenced_objects": len(references),
        "audited_glbs": len(glb_paths),
        "errors": all_errors,
        "warnings": all_warnings,
        "assets": asset_reports,
    }


def print_summary(result: dict[str, Any], *, verbose: bool = False) -> None:
    print(
        "asset audit: "
        f"{result['status'].upper()}  "
        f"{result.get('audited_glbs', 0)} GLBs, "
        f"{len(result.get('errors', []))} errors, "
        f"{len(result.get('warnings', []))} warnings"
    )
    for error in result.get("errors", []):
        print(f"  ERROR   {error}")
    if verbose:
        for warning in result.get("warnings", []):
            print(f"  warning {warning}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed-dir", type=Path, default=DEFAULT_SEED_DIR)
    parser.add_argument("--limit", type=int, default=None, help="audit only the first N GLBs (pilot mode)")
    parser.add_argument("--json", action="store_true", help="emit the complete machine-readable report")
    parser.add_argument("--verbose", action="store_true", help="print performance warnings")
    args = parser.parse_args()

    result = audit_seed_library(args.seed_dir.resolve(), limit=args.limit)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print_summary(result, verbose=args.verbose)
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
