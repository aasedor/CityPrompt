#!/usr/bin/env python3
"""Promote reviewed compiler families into the durable model-library seed.

The API manifest importer is useful for a running stack, but its rows and object
uploads are machine-local.  This tool creates the same deterministic storage
layout under ``seed/model-library`` so a reviewed family survives a clean clone.

Promotion fails closed unless the current validation and quality reports pass,
all declared GLBs are hydrated and under the API upload cap, and the locked-view
human approval is present.  The command is a dry run unless ``--apply`` is used.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


REPO = Path(__file__).resolve().parents[1]
BACKEND = REPO / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.services.lego_assembly import (  # noqa: E402
    lego_metadata_from_manifest,
    manifest_validation_errors,
)


DEFAULT_SEED_DIR = REPO / "seed" / "model-library"
DEFAULT_OWNER_ID = "651daf60-b797-4f95-b1e7-6364d6dc0665"
ID_NAMESPACE = uuid.UUID("231ae4fb-50a1-50e2-8201-f4ee165594fd")
MAX_UPLOAD_BYTES = 75 * 1024 * 1024
TAG_REUSE_KEY_LIMIT = 3
LFS_POINTER_PREFIX = b"version https://git-lfs.github.com/spec/"
REQUIRED_COLUMNS = {
    "id",
    "owner_id",
    "source_building_id",
    "source_project_id",
    "name",
    "description",
    "category",
    "tags",
    "model_url",
    "lod_urls",
    "thumbnail_url",
    "generation_prompt",
    "generation_engine",
    "architectural_style",
    "is_public",
    "use_count",
    "metadata",
    "created_at",
}


@dataclass(frozen=True)
class PreparedUnit:
    family: str
    role: str
    variant_key: str
    lod: int
    source: Path
    destination_name: str
    row: dict[str, Any]


@dataclass(frozen=True)
class PreparedFamily:
    family: str
    source_dir: Path
    preview_source: Path
    preview_name: str
    units: tuple[PreparedUnit, ...]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "family_dir",
        type=Path,
        nargs="+",
        help="compiled family folder(s) containing manifest and reports",
    )
    parser.add_argument("--seed-dir", type=Path, default=DEFAULT_SEED_DIR)
    parser.add_argument("--owner-id", default=DEFAULT_OWNER_ID)
    parser.add_argument(
        "--apply",
        action="store_true",
        help="copy objects and update model_library.json",
    )
    return parser.parse_args()


def load_json(path: Path, label: str) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"{label} is missing: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"{label} is invalid JSON: {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"{label} must be a JSON object: {path}")
    return payload


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_glb(path: Path) -> None:
    try:
        size = path.stat().st_size
        with path.open("rb") as stream:
            head = stream.read(max(4, len(LFS_POINTER_PREFIX)))
    except FileNotFoundError as exc:
        raise ValueError(f"declared GLB is missing: {path}") from exc
    if head.startswith(LFS_POINTER_PREFIX):
        raise ValueError(f"declared GLB is still a Git LFS pointer: {path}")
    if head[:4] != b"glTF":
        raise ValueError(f"declared GLB has no glTF binary header: {path}")
    if size > MAX_UPLOAD_BYTES:
        raise ValueError(
            f"declared GLB exceeds the {MAX_UPLOAD_BYTES // 1_048_576} MB API cap: "
            f"{path} ({size / 1_048_576:.1f} MB)"
        )


def synthesized_units(manifest: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    units = [
        (str(module.get("role") or "").strip().lower(), dict(module))
        for module in manifest["modules"]
    ]
    assembled = manifest.get("assembled") or {}
    if assembled.get("filename"):
        dimensions = manifest.get("dimensions") or {}
        units.append(
            (
                "assembled",
                {
                    "role": "assembled",
                    "filename": assembled["filename"],
                    "width_m": assembled.get("width_m", dimensions.get("width_m")),
                    "depth_m": assembled.get("depth_m", dimensions.get("depth_m")),
                    "height_m": assembled.get("height_m"),
                    "native_floors": assembled.get("floors"),
                    "floor_height_m": dimensions.get("floor_height_m"),
                    "repeatable_z": False,
                    "variant_key": "default",
                    "lod": 0,
                    "triangle_count": assembled.get("triangle_count"),
                    "material_count": assembled.get("material_count"),
                },
            )
        )
    return units


def current_memory_version() -> str:
    memory = load_json(
        REPO / "tools" / "archetype_compiler" / "high_quality_building_memory.json",
        "quality memory",
    )
    return str(memory.get("memory_version") or "")


def prepare_family(family_dir: Path, owner_id: str) -> PreparedFamily:
    family_dir = family_dir.resolve()
    manifests = sorted(family_dir.glob("*_manifest.json"))
    if len(manifests) != 1:
        raise ValueError(
            f"expected exactly one *_manifest.json in {family_dir}; found {len(manifests)}"
        )
    manifest_path = manifests[0]
    manifest = load_json(manifest_path, "manifest")
    errors = manifest_validation_errors(manifest)
    if errors:
        raise ValueError("manifest is not importable: " + "; ".join(errors))

    family = str(manifest["family"]).strip()
    if family_dir.name != family:
        raise ValueError(
            f"family folder name {family_dir.name!r} does not match manifest family {family!r}"
        )

    validation_path = family_dir / "validation_report.json"
    quality_path = family_dir / "quality_assessment.json"
    validation = load_json(validation_path, "validation report")
    quality = load_json(quality_path, "quality assessment")
    if validation.get("status") != "pass":
        raise ValueError(
            f"validation status for {family} is {validation.get('status')!r}; expected 'pass'"
        )
    if quality.get("memory_version") != current_memory_version():
        raise ValueError(
            f"quality assessment for {family} uses memory {quality.get('memory_version')!r}; "
            f"rerun against {current_memory_version()!r}"
        )
    if quality.get("status") != "pass" or quality.get("high_quality_ready") is not True:
        raise ValueError(f"quality assessment for {family} is not approved and ready")
    if quality.get("hard_failures") or quality.get("review_findings"):
        raise ValueError(f"quality assessment for {family} still contains findings")
    if validation_path.stat().st_mtime_ns < manifest_path.stat().st_mtime_ns:
        raise ValueError(
            f"validation report for {family} predates the manifest; rerun validation"
        )
    if quality_path.stat().st_mtime_ns < validation_path.stat().st_mtime_ns:
        raise ValueError(
            f"quality assessment for {family} predates validation; rerun assessment"
        )

    thumbnail_name = str(manifest.get("thumbnail") or f"{family}_preview.png")
    if Path(thumbnail_name).name != thumbnail_name:
        raise ValueError(
            f"thumbnail must be a filename inside the family folder: {thumbnail_name!r}"
        )
    preview = family_dir / thumbnail_name
    if not preview.is_file() or preview.stat().st_size < 200:
        raise ValueError(f"family preview is missing or not hydrated: {preview}")
    preview_hash = sha256(preview)
    thumbnail_url = f"/api/v1/files/library/lego/{owner_id}/{family}/preview.png?v={preview_hash[:12]}"

    label = str(manifest.get("archetype_label") or family)
    archetype_id = str(manifest["archetype_id"])
    generator = manifest.get("generator") or {}
    generation_prompt = (
        f"Procedural module generated by {generator.get('name') or 'archetype_compiler'} "
        f"v{generator.get('version') or 'unknown'} from archetype {archetype_id}"
    )
    style = manifest.get("aesthetic_category_id")
    architectural_style = str(style)[:50] if style else None
    reuse_keys = [
        str(value) for value in manifest.get("reuse_keys") or [] if str(value).strip()
    ]
    prepared: list[PreparedUnit] = []
    for role, module in synthesized_units(manifest):
        filename = str(module.get("filename") or "")
        if Path(filename).name != filename:
            raise ValueError(
                f"module filename must remain inside the family folder: {filename!r}"
            )
        source = family_dir / filename
        verify_glb(source)
        variant_key = str(module.get("variant_key") or "default")
        lod = max(0, int(module.get("lod") or 0))
        destination_name = f"{role}--{variant_key}--lod{lod}.glb"
        content_hash = sha256(source)
        model_url = (
            f"/api/v1/files/library/lego/{owner_id}/{family}/"
            f"{destination_name}?v={content_hash[:12]}"
        )
        lego = lego_metadata_from_manifest(
            manifest,
            module,
            role=role,
            validation_status="pass",
        )
        lego["content_hash"] = content_hash
        identity_label = role if variant_key == "default" else f"{role} / {variant_key}"
        stable_id = uuid.uuid5(
            ID_NAMESPACE, f"{owner_id}/{family}/{role}/{variant_key}/{lod}"
        )
        row = {
            "id": str(stable_id),
            "owner_id": owner_id,
            "source_building_id": None,
            "source_project_id": None,
            "name": f"{label} — {identity_label}"[:255],
            "description": None,
            "category": "lego_module",
            "tags": [family, role, variant_key, *reuse_keys[:TAG_REUSE_KEY_LIMIT]],
            "model_url": model_url,
            "lod_urls": None,
            "thumbnail_url": thumbnail_url,
            "generation_prompt": generation_prompt,
            "generation_engine": "compiler",
            "architectural_style": architectural_style,
            "is_public": False,
            "use_count": 0,
            "metadata": {"lego": lego},
            "created_at": manifest.get("created_at"),
        }
        prepared.append(
            PreparedUnit(
                family=family,
                role=role,
                variant_key=variant_key,
                lod=lod,
                source=source,
                destination_name=destination_name,
                row=row,
            )
        )
    return PreparedFamily(
        family=family,
        source_dir=family_dir,
        preview_source=preview,
        preview_name="preview.png",
        units=tuple(prepared),
    )


def row_identity(row: dict[str, Any]) -> tuple[str, str, str, int] | None:
    metadata = row.get("metadata")
    lego = metadata.get("lego") if isinstance(metadata, dict) else None
    if not isinstance(lego, dict):
        return None
    family = str(lego.get("family") or "")
    role = str(lego.get("role") or "")
    if not family or not role:
        return None
    return (
        family,
        role,
        str(lego.get("variant_key") or "default"),
        max(0, int(lego.get("lod") or 0)),
    )


def promote(
    family_dirs: Iterable[Path],
    *,
    seed_dir: Path = DEFAULT_SEED_DIR,
    owner_id: str = DEFAULT_OWNER_ID,
    apply: bool = False,
) -> dict[str, Any]:
    owner_id = str(uuid.UUID(owner_id))
    seed_dir = seed_dir.resolve()
    rows_path = seed_dir / "model_library.json"
    payload = load_json(rows_path, "model library seed")
    columns = payload.get("columns")
    rows = payload.get("rows")
    if not isinstance(columns, list) or not REQUIRED_COLUMNS <= set(columns):
        raise ValueError("model library seed columns do not match the required schema")
    if not isinstance(rows, list):
        raise ValueError("model library seed rows must be a list")

    prepared_families = [prepare_family(Path(path), owner_id) for path in family_dirs]
    family_names = [item.family for item in prepared_families]
    if len(family_names) != len(set(family_names)):
        raise ValueError("the same family was supplied more than once")

    result_rows = [dict(row) for row in rows]
    identity_index: dict[tuple[str, str, str, int], int] = {}
    id_index: dict[str, int] = {}
    for index, row in enumerate(result_rows):
        row_id = str(row.get("id") or "")
        if row_id:
            id_index[row_id] = index
        if str(row.get("owner_id")) == owner_id:
            identity = row_identity(row)
            if identity is not None:
                if identity in identity_index:
                    raise ValueError(
                        f"seed contains duplicate LEGO identity: {identity}"
                    )
                identity_index[identity] = index

    added = updated = 0
    object_writes: list[tuple[Path, Path]] = []
    for family in sorted(prepared_families, key=lambda value: value.family):
        family_destination = seed_dir / "objects" / "lego" / owner_id / family.family
        object_writes.append(
            (family.preview_source, family_destination / family.preview_name)
        )
        for unit in sorted(
            family.units,
            key=lambda value: (value.role, value.variant_key, value.lod),
        ):
            identity = (unit.family, unit.role, unit.variant_key, unit.lod)
            row = dict(unit.row)
            if identity in identity_index:
                index = identity_index[identity]
                row["id"] = result_rows[index]["id"]
                row["created_at"] = (
                    result_rows[index].get("created_at") or row["created_at"]
                )
                result_rows[index] = row
                updated += 1
            else:
                if row["id"] in id_index:
                    raise ValueError(
                        f"deterministic row id collides with an unrelated seed row: {row['id']}"
                    )
                identity_index[identity] = len(result_rows)
                id_index[row["id"]] = len(result_rows)
                result_rows.append(row)
                added += 1
            object_writes.append(
                (unit.source, family_destination / unit.destination_name)
            )

    objects_changed = 0
    if apply:
        for source, destination in object_writes:
            destination.parent.mkdir(parents=True, exist_ok=True)
            if destination.is_file() and sha256(destination) == sha256(source):
                continue
            shutil.copy2(source, destination)
            objects_changed += 1
        payload["rows"] = result_rows
        payload["count"] = len(result_rows)
        temporary = rows_path.with_suffix(rows_path.suffix + ".tmp")
        temporary.write_text(
            # Preserve the seed's established ASCII-escaped JSON style so a
            # small promotion does not rewrite every existing Unicode label.
            json.dumps(payload, indent=1, ensure_ascii=True) + "\n",
            encoding="utf-8",
        )
        os.replace(temporary, rows_path)

    return {
        "families": family_names,
        "rows_before": len(rows),
        "rows_after": len(result_rows),
        "rows_added": added,
        "rows_updated": updated,
        "objects_planned": len(object_writes),
        "objects_changed": objects_changed,
        "applied": apply,
    }


def main() -> int:
    args = parse_args()
    try:
        result = promote(
            args.family_dir,
            seed_dir=args.seed_dir,
            owner_id=args.owner_id,
            apply=args.apply,
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"promotion: BLOCKED ({exc})")
        return 1
    print(json.dumps(result, indent=2))
    if not args.apply:
        print("promotion: dry run only; pass --apply after review approval")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
