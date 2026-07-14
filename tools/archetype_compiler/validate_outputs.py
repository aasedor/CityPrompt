"""Validate the GLB family produced by blender_generate.py against its grammar.

Checks (failures exit non-zero):
- required files exist and parse as GLB (podium, floor, roof, manifest; assembled if declared)
- non-empty geometry, finite bounds, no absurd extents
- footprint matches the grammar within tolerance (balconies/frames may protrude the front)
- bottom sits at 0 within 2 cm
- module heights and assembled stack height are consistent
- manifest carries the archetype id and reuse keys

Warnings (reported, not fatal): high triangle count, many materials, missing
optional setback, missing thumbnail.

GLB axis note: modules are exported with ``export_yup=True``; Blender Z (up)
becomes glTF Y, Blender -Y (front) becomes glTF +Z. Width stays X, the
building depth is the glTF Z extent, and heights are Y extents.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

try:
    import numpy as np
    import trimesh
except ImportError as exc:  # pragma: no cover
    raise SystemExit(
        "validate_outputs.py needs trimesh + numpy.\n"
        "Install with: python -m pip install -r tools/archetype_compiler/requirements.txt"
    ) from exc

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BOTTOM_TOLERANCE_M = 0.02
FOOTPRINT_TOLERANCE_M = 0.6          # frames sit slightly proud of walls
ROOF_OVERHANG_ALLOWANCE_M = 1.2      # gabled/mono-pitch eaves overhang every side
FRONT_PROTRUSION_ALLOWANCE_M = 3.0   # balconies + canopies overhang the front facade
HEIGHT_TOLERANCE_M = 1.2             # parapets/mech screens rise above nominal module height
MAX_EXTENT_M = 500.0
TRIANGLE_WARN_THRESHOLD = 80_000
MATERIAL_WARN_THRESHOLD = 14


def _load_scene(path: Path):
    scene = trimesh.load(str(path), force="scene")
    meshes = [g for g in scene.geometry.values() if isinstance(g, trimesh.Trimesh)]
    return scene, meshes


def _check_module(path: Path, expected: dict[str, Any], errors: list[str], warnings: list[str]) -> dict[str, Any]:
    label = path.name
    if not path.exists():
        errors.append(f"{label}: file missing")
        return {"file": label, "status": "missing"}
    if path.stat().st_size < 1_000:
        errors.append(f"{label}: file is suspiciously small ({path.stat().st_size} bytes)")

    try:
        scene, meshes = _load_scene(path)
    except Exception as exc:
        errors.append(f"{label}: failed to parse GLB ({exc})")
        return {"file": label, "status": "unparseable"}

    if not meshes:
        errors.append(f"{label}: GLB contains no mesh geometry")
        return {"file": label, "status": "empty"}

    bounds = scene.bounds  # [[minx,miny,minz],[maxx,maxy,maxz]] in glTF axes (Y up)
    if bounds is None or not np.isfinite(bounds).all():
        errors.append(f"{label}: NaN/inf bounds")
        return {"file": label, "status": "nan-bounds"}

    (min_x, min_y, min_z), (max_x, max_y, max_z) = bounds
    extent_x, extent_y, extent_z = max_x - min_x, max_y - min_y, max_z - min_z
    tri_count = int(sum(len(m.faces) for m in meshes))
    material_names = {str(getattr(m.visual, "material", None) and m.visual.material.name) for m in meshes}

    report = {
        "file": label,
        "status": "ok",
        "triangles": tri_count,
        "extent_m": {"width_x": round(float(extent_x), 3), "height_y": round(float(extent_y), 3), "depth_z": round(float(extent_z), 3)},
        "bottom_y": round(float(min_y), 4),
        "materials": sorted(material_names),
    }

    if max(extent_x, extent_y, extent_z) > MAX_EXTENT_M:
        errors.append(f"{label}: extent {max(extent_x, extent_y, extent_z):.1f} m is absurd (limit {MAX_EXTENT_M} m)")
    if abs(min_y) > BOTTOM_TOLERANCE_M:
        errors.append(f"{label}: bottom sits at Y={min_y:.3f} m; must be within ±{BOTTOM_TOLERANCE_M} m of 0 (origin at bottom centre)")

    width = expected.get("width_m")
    depth = expected.get("depth_m")
    height = expected.get("height_m")
    # Roof modules (and assembled stacks containing them) may carry eave overhangs
    role = expected.get("role") or ""
    width_tol = FOOTPRINT_TOLERANCE_M + (ROOF_OVERHANG_ALLOWANCE_M if role in ("roof", "assembled") else 0.0)
    if width and abs(extent_x - width) > width_tol:
        errors.append(f"{label}: X extent {extent_x:.2f} m vs grammar width {width} m (tol {width_tol} m)")
    if depth:
        if extent_z < depth - FOOTPRINT_TOLERANCE_M:
            errors.append(f"{label}: Z extent {extent_z:.2f} m smaller than grammar depth {depth} m")
        elif extent_z > depth + FRONT_PROTRUSION_ALLOWANCE_M + (ROOF_OVERHANG_ALLOWANCE_M if role in ("roof", "assembled") else 0.0):
            errors.append(
                f"{label}: Z extent {extent_z:.2f} m exceeds grammar depth {depth} m + allowances"
            )
    if height and abs(extent_y - height) > HEIGHT_TOLERANCE_M:
        errors.append(f"{label}: Y extent {extent_y:.2f} m vs nominal module height {height} m (tol {HEIGHT_TOLERANCE_M} m)")

    if tri_count > TRIANGLE_WARN_THRESHOLD:
        warnings.append(f"{label}: {tri_count} triangles (heavy; consider simplification)")
    if len(material_names) > MATERIAL_WARN_THRESHOLD:
        warnings.append(f"{label}: {len(material_names)} materials (many; consider consolidation)")

    if errors and any(e.startswith(label) for e in errors):
        report["status"] = "failed"
    return report


def validate_family(output_dir: Path, grammar_path: Path | None = None) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    manifests = sorted(output_dir.glob("*_manifest.json"))
    if not manifests:
        return {"status": "fail", "errors": [f"no *_manifest.json found in {output_dir}"], "warnings": [], "modules": []}
    manifest_path = manifests[0]
    if grammar_path and grammar_path.exists() and len(manifests) > 1:
        # Multiple families in one folder: validate the one this grammar produced
        family = json.loads(grammar_path.read_text(encoding="utf-8")).get("family_id")
        matching = [m for m in manifests if m.name.startswith(f"{family}_")]
        if matching:
            manifest_path = matching[0]
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"status": "fail", "errors": [f"manifest unreadable: {exc}"], "warnings": [], "modules": []}

    grammar = None
    if grammar_path and grammar_path.exists():
        grammar = json.loads(grammar_path.read_text(encoding="utf-8"))

    # manifest correctness
    for key in ("family", "archetype_id", "modules", "dimensions", "coordinate_contract"):
        if not manifest.get(key):
            errors.append(f"manifest: missing '{key}'")
    if not manifest.get("reuse_keys"):
        errors.append("manifest: reuse_keys is empty — archetype provenance was lost")
    if grammar:
        if manifest.get("archetype_id") != grammar["source"]["archetype_id"]:
            errors.append("manifest: archetype_id does not match grammar source")
        if manifest.get("reuse_keys") != grammar["source"]["reuse_keys"]:
            errors.append("manifest: reuse_keys do not match grammar source")

    roles_present = {m["role"] for m in manifest.get("modules", [])}
    for required in ("podium", "floor", "roof"):
        if required not in roles_present:
            errors.append(f"manifest: required module role '{required}' missing")
    if "setback" not in roles_present:
        warnings.append("no setback module (optional)")

    module_reports = []
    for module in manifest.get("modules", []):
        path = output_dir / module["filename"]
        module_reports.append(_check_module(path, module, errors, warnings))

    assembled = manifest.get("assembled")
    if assembled:
        path = output_dir / assembled["filename"]
        report = _check_module(
            path,
            {"role": "assembled",
             "width_m": manifest["dimensions"]["width_m"], "depth_m": manifest["dimensions"]["depth_m"],
             "height_m": assembled["height_m"]},
            errors, warnings,
        )
        report["role"] = "assembled"
        # stack height must equal podium + floors + (setback) + roof
        dims = manifest["dimensions"]
        floors = assembled["floors"]
        expected_height = (
            dims["podium_height_m"]
            + max(0, floors - 1 - (1 if assembled.get("uses_setback") else 0)) * dims["floor_height_m"]
            + (dims["setback_height_m"] if assembled.get("uses_setback") else 0.0)
            + dims["roof_height_m"]
        )
        if not math.isclose(assembled["height_m"], expected_height, abs_tol=0.05):
            errors.append(
                f"assembled: manifest height {assembled['height_m']} m != computed stack {expected_height:.2f} m"
            )
        module_reports.append(report)
    else:
        errors.append("manifest: no assembled preview recorded")

    thumbnail = manifest.get("thumbnail")
    if thumbnail and not (output_dir / thumbnail).exists():
        warnings.append(f"thumbnail '{thumbnail}' declared but missing")
    elif not thumbnail:
        warnings.append("no thumbnail rendered")

    status = "fail" if errors else "pass"
    return {
        "status": status,
        "family": manifest.get("family"),
        "archetype_id": manifest.get("archetype_id"),
        "reuse_keys": manifest.get("reuse_keys"),
        "manifest": manifest_path.name,
        "errors": errors,
        "warnings": warnings,
        "modules": module_reports,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate a generated archetype GLB family")
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--grammar", type=Path, default=None)
    parser.add_argument("--report", type=Path, default=None, help="where to write validation_report.json")
    args = parser.parse_args()

    result = validate_family(args.output_dir.resolve(), args.grammar.resolve() if args.grammar else None)
    report_path = args.report or (args.output_dir / "validation_report.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(result, indent=2), encoding="utf-8")

    print(f"validation: {result['status'].upper()}  ({report_path})")
    for error in result["errors"]:
        print(f"  ERROR   {error}")
    for warning in result["warnings"]:
        print(f"  warning {warning}")
    for module in result["modules"]:
        if module.get("status") == "ok":
            extent = module.get("extent_m", {})
            print(
                f"  ok      {module['file']}: {module.get('triangles', '?')} tris, "
                f"{extent.get('width_x')}x{extent.get('depth_z')}x{extent.get('height_y')} m"
            )
    sys.exit(0 if result["status"] == "pass" else 1)


if __name__ == "__main__":
    main()
