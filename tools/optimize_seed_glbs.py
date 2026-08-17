#!/usr/bin/env python3
"""Losslessly consolidate fragmented model-library GLBs.

Sticker Method exports may contain one material and primitive per authored
surface. The geometry and texture count can be reasonable while thousands of
draw calls make the model expensive in Three.js. This tool preserves geometry,
UVs, textures, the ground datum, and runtime material semantics while removing
surface-only provenance from delivery materials and joining compatible
primitives with glTF Transform.

The default target list is the bounded three-asset performance pilot. Without
``--apply`` optimized files are written under an ignored artifacts directory.
With ``--apply`` the source seed GLBs are replaced only after every acceptance
check and glTF validation passes. Catalogue hashes must then be synchronized.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import shutil
import struct
import subprocess
import sys
import tempfile
from dataclasses import asdict
from pathlib import Path
from typing import Any

try:
    from audit_seed_model_library import GlbStats, inspect_glb
except ModuleNotFoundError:  # Imported as tools.optimize_seed_glbs in tests.
    from tools.audit_seed_model_library import GlbStats, inspect_glb


REPO_ROOT = Path(__file__).resolve().parents[1]
GLTF_TRANSFORM_VERSION = "4.4.2"
JSON_CHUNK_TYPE = 0x4E4F534A
RUNTIME_MATERIAL_EXTRA_KEYS = frozenset(
    {
        "environment_intensity",
        "facade_sheet_role",
        "glazing_lod",
        "glazing_profile",
    }
)
DEFAULT_TARGETS = (
    Path(
        "seed/model-library/objects/lego/3c9deca4-522d-4b7b-ad11-d4f291678077/"
        "daylight-sawtooth-factory-v98-extended/assembled--default--lod0.glb"
    ),
    Path(
        "seed/model-library/objects/lego/3c9deca4-522d-4b7b-ad11-d4f291678077/"
        "daylight-sawtooth-v98-native-tiers/assembled--extended--lod0.glb"
    ),
    Path(
        "seed/model-library/objects/lego/3c9deca4-522d-4b7b-ad11-d4f291678077/"
        "old-montreal-textile-v98-native-tiers/assembled--extended--lod0.glb"
    ),
)


class OptimizationError(RuntimeError):
    """The candidate failed a lossless optimization acceptance check."""


def _runtime_material_semantic(name: str, extras: dict[str, Any]) -> str:
    lowered = name.lower()
    glazing_lod = str(extras.get("glazing_lod") or "").lower()
    if lowered.startswith("mat_sheet_"):
        return "MAT_Sheet"
    if "glazinginterior" in lowered or glazing_lod == "interior":
        return "MAT_GlazingInterior"
    if "glassoverlay" in lowered:
        return "MAT_GlassOverlay"
    if "glass" in lowered:
        return "MAT_Glass"
    if "interior_shadow" in lowered:
        return "MAT_InteriorShadow"
    if "interiorsolarshade" in lowered:
        return "MAT_InteriorSolarShade"
    return "MAT_Optimized"


def normalize_materials_payload(payload: dict[str, Any]) -> dict[str, int]:
    """Canonicalize delivery material names/extras in a parsed glTF payload.

    Visual properties and runtime-consumed extras remain part of the signature.
    Per-surface QA/provenance extras are intentionally removed from the runtime
    GLB; they already live in the compiler evidence and source manifests.
    """
    materials = payload.get("materials") or []
    names_before = {str(material.get("name") or "") for material in materials}
    signatures: set[str] = set()

    for material in materials:
        original_name = str(material.get("name") or "")
        source_extras = material.get("extras") or {}
        runtime_extras = {
            key: value
            for key, value in source_extras.items()
            if key in RUNTIME_MATERIAL_EXTRA_KEYS
        }
        if runtime_extras:
            material["extras"] = runtime_extras
        else:
            material.pop("extras", None)

        signature_payload = {
            key: value
            for key, value in material.items()
            if key != "name"
        }
        signature_json = json.dumps(
            signature_payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        )
        digest = hashlib.sha256(signature_json.encode("utf-8")).hexdigest()[:12]
        semantic = _runtime_material_semantic(original_name, runtime_extras)
        material["name"] = f"{semantic}_{digest}"
        signatures.add(f"{semantic}:{digest}")

    return {
        "materials": len(materials),
        "unique_names_before": len(names_before),
        "canonical_signatures": len(signatures),
    }


def _rewrite_glb_materials(source: Path, destination: Path) -> dict[str, int]:
    raw = source.read_bytes()
    if len(raw) < 20:
        raise OptimizationError(f"{source}: truncated GLB")
    magic, version, declared_length = struct.unpack_from("<4sII", raw, 0)
    if magic != b"glTF" or version != 2 or declared_length != len(raw):
        raise OptimizationError(f"{source}: invalid GLB header")

    chunks: list[tuple[int, bytes]] = []
    offset = 12
    found_json = False
    summary: dict[str, int] | None = None
    while offset < len(raw):
        if offset + 8 > len(raw):
            raise OptimizationError(f"{source}: truncated chunk header")
        chunk_length, chunk_type = struct.unpack_from("<II", raw, offset)
        offset += 8
        chunk = raw[offset : offset + chunk_length]
        if len(chunk) != chunk_length:
            raise OptimizationError(f"{source}: truncated chunk")
        offset += chunk_length
        if chunk_type == JSON_CHUNK_TYPE and not found_json:
            payload = json.loads(chunk.decode("utf-8").rstrip(" \t\r\n\0"))
            summary = normalize_materials_payload(payload)
            chunk = json.dumps(
                payload,
                separators=(",", ":"),
                ensure_ascii=False,
            ).encode("utf-8")
            chunk += b" " * ((4 - len(chunk) % 4) % 4)
            found_json = True
        chunks.append((chunk_type, chunk))

    if not found_json or summary is None:
        raise OptimizationError(f"{source}: GLB has no JSON chunk")

    total_length = 12 + sum(8 + len(chunk) for _kind, chunk in chunks)
    rebuilt = bytearray(struct.pack("<4sII", b"glTF", 2, total_length))
    for chunk_type, chunk in chunks:
        rebuilt.extend(struct.pack("<II", len(chunk), chunk_type))
        rebuilt.extend(chunk)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(rebuilt)
    return summary


def _npx_command() -> str:
    command = shutil.which("npx.cmd") or shutil.which("npx")
    if not command:
        raise OptimizationError("npx is required to run @gltf-transform/cli")
    return command


def _run_cli(*args: str) -> None:
    command = [
        _npx_command(),
        "--yes",
        f"@gltf-transform/cli@{GLTF_TRANSFORM_VERSION}",
        *args,
    ]
    completed = subprocess.run(
        command,
        cwd=REPO_ROOT,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        detail = (completed.stderr or completed.stdout).strip()
        raise OptimizationError(f"glTF Transform {' '.join(args[:1])} failed: {detail}")


def _bounds_close(before: GlbStats, after: GlbStats, tolerance: float = 1e-4) -> bool:
    values_before = (*before.bounds.minimum, *before.bounds.maximum)
    values_after = (*after.bounds.minimum, *after.bounds.maximum)
    return all(
        math.isclose(left, right, rel_tol=0, abs_tol=tolerance)
        for left, right in zip(values_before, values_after, strict=True)
    )


def _accept_candidate(before: GlbStats, after: GlbStats) -> None:
    if not _bounds_close(before, after):
        raise OptimizationError("candidate changed the model bounds")
    if before.triangles != after.triangles:
        raise OptimizationError(
            f"candidate changed triangle count {before.triangles} -> {after.triangles}"
        )
    if after.missing_normal_primitives:
        raise OptimizationError("candidate contains primitives without normals")
    if after.primitives >= before.primitives:
        raise OptimizationError("candidate did not reduce primitive count")
    if after.materials >= before.materials:
        raise OptimizationError("candidate did not reduce material count")


def optimize_one(source: Path, destination: Path) -> dict[str, Any]:
    source = source.resolve()
    destination = destination.resolve()
    if not source.is_file():
        raise OptimizationError(f"missing source GLB: {source}")

    source_hash_before = hashlib.sha256(source.read_bytes()).hexdigest()
    before = inspect_glb(source)
    with tempfile.TemporaryDirectory(prefix="cityprompt-glb-opt-") as temp_name:
        temp_dir = Path(temp_name)
        deduped = temp_dir / "01-deduped.glb"
        normalized = temp_dir / "02-normalized.glb"
        candidate = temp_dir / "03-candidate.glb"

        # First join canonicalizes duplicate texture objects and accessors. The
        # original per-surface extras still prevent material consolidation.
        _run_cli(
            "join",
            str(source),
            str(deduped),
            "--keepNamed",
            "false",
            "--keepMeshes",
            "false",
        )
        normalization = _rewrite_glb_materials(deduped, normalized)
        # With delivery-only extras and canonical semantic names, compatible
        # surfaces can finally share one material and primitive.
        _run_cli(
            "join",
            str(normalized),
            str(candidate),
            "--keepNamed",
            "false",
            "--keepMeshes",
            "false",
        )
        _run_cli("validate", str(candidate))

        after = inspect_glb(candidate)
        _accept_candidate(before, after)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(candidate, destination)

    return {
        "source": str(source),
        "destination": str(destination),
        "sha256_before": source_hash_before,
        "sha256_after": hashlib.sha256(destination.read_bytes()).hexdigest(),
        "normalization": normalization,
        "before": asdict(before),
        "after": asdict(after),
        "primitive_reduction_percent": round(
            (1 - after.primitives / before.primitives) * 100,
            2,
        ),
        "size_reduction_percent": round(
            (1 - after.size_bytes / before.size_bytes) * 100,
            2,
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "targets",
        nargs="*",
        type=Path,
        help="seed GLBs to optimize; defaults to the three-asset pilot",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=REPO_ROOT / "artifacts" / "model-library-optimization-pilot",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="replace each source only after the optimized candidate passes",
    )
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    targets = args.targets or list(DEFAULT_TARGETS)
    reports: list[dict[str, Any]] = []
    try:
        for target in targets:
            source = target if target.is_absolute() else REPO_ROOT / target
            if args.apply:
                destination = source
            else:
                objects_root = REPO_ROOT / "seed" / "model-library" / "objects"
                try:
                    relative_output = source.resolve().relative_to(objects_root)
                except ValueError:
                    relative_output = Path(source.name)
                destination = args.output_dir / relative_output
            report = optimize_one(source, destination)
            reports.append(report)
            if not args.json:
                before = report["before"]
                after = report["after"]
                print(source.relative_to(REPO_ROOT).as_posix())
                print(
                    f"  primitives {before['primitives']:,} -> {after['primitives']:,} "
                    f"({report['primitive_reduction_percent']:.2f}% fewer)"
                )
                print(
                    f"  materials  {before['materials']:,} -> {after['materials']:,}; "
                    f"size {before['size_bytes'] / 1_048_576:.2f} -> "
                    f"{after['size_bytes'] / 1_048_576:.2f} MB"
                )
    except (OptimizationError, OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps({"status": "pass", "assets": reports}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
