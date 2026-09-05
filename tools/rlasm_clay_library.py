"""Deterministic loader for the canonical RLASM architectural-clay seed.

The manifest is deliberately small: one fixed assembled GLB per exact
catalogue variant.  Editable authoring files and review media remain in the
external artifact packages referenced by the manifest.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
from pathlib import Path, PurePosixPath
import re
import struct
from typing import Any, Iterable
import uuid


REPO_ROOT = Path(__file__).resolve().parents[1]
CLAY_ROOT = REPO_ROOT / "seed" / "model-library" / "rlasm-architectural-clay"
LIBRARY_PATH = CLAY_ROOT / "library.json"
SEED_OWNER_ID = "651daf60-b797-4f95-b1e7-6364d6dc0665"
SCHEMA = "cityprompt.rlasm-architectural-clay-library@1"
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
REQUIRED_SOURCE_ROLES = {"front", "oblique", "top"}


@dataclass(frozen=True)
class ClaySeedObject:
    source: Path
    storage_key: str


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _array_count(document: dict[str, Any], key: str) -> int:
    value = document.get(key)
    return len(value) if isinstance(value, list) else 0


def _glb_counts(path: Path) -> dict[str, int]:
    with path.open("rb") as handle:
        header = handle.read(20)
        if len(header) != 20:
            raise ValueError(f"GLB header is incomplete: {path}")
        magic, version, declared_length, json_length, json_type = struct.unpack(
            "<4sIIII", header
        )
        if magic != b"glTF" or version != 2 or declared_length != path.stat().st_size:
            raise ValueError(f"Invalid GLB container: {path}")
        if json_type != 0x4E4F534A:
            raise ValueError(f"GLB has no leading JSON chunk: {path}")
        document = json.loads(handle.read(json_length).decode("utf-8").rstrip(" \x00"))
    return {
        "meshes": _array_count(document, "meshes"),
        "materials": _array_count(document, "materials"),
        "textures": _array_count(document, "textures"),
        "images": _array_count(document, "images"),
    }


def _safe_relative_model_path(value: Any) -> PurePosixPath:
    path = PurePosixPath(str(value or ""))
    if path.is_absolute() or ".." in path.parts or path.suffix.lower() != ".glb":
        raise ValueError(f"Unsafe clay model path: {value!r}")
    if len(path.parts) != 2 or path.parts[0] != "models":
        raise ValueError(f"Clay model must live directly under models/: {value!r}")
    return path


def _validate_hash(value: Any, label: str) -> str:
    digest = str(value or "").lower()
    if not SHA256_RE.fullmatch(digest):
        raise ValueError(f"Invalid SHA-256 for {label}")
    return digest


def _validate_payload(payload: dict[str, Any], *, clay_root: Path = CLAY_ROOT, repo_root: Path = REPO_ROOT) -> None:
    if payload.get("schema") != SCHEMA:
        raise ValueError(f"Unsupported clay library schema: {payload.get('schema')!r}")
    if payload.get("method") != "RLASM" or payload.get("method_version") != "6.1":
        raise ValueError("The clay library must use canonical RLASM v6.1")
    if payload.get("delivery_format") != "architectural_clay":
        raise ValueError("The clay library delivery format is not architectural_clay")

    runtime = payload.get("runtime_policy") or {}
    required_runtime_values = {
        "building_detail_mode": "rlasm_architectural_clay_only",
        "unsupported_archetype_fallback": "planned_massing",
        "reference_images_drive_user_selection": True,
        "reference_images_drive_render_conditioning": True,
        "clay_previews_may_replace_catalogue_references": False,
        "continuous_resize_allowed": False,
        "terrain_fit_verified": False,
        "scaling_verified": False,
    }
    for key, expected in required_runtime_values.items():
        if runtime.get(key) != expected:
            raise ValueError(f"Invalid runtime policy {key}: {runtime.get(key)!r}")

    activation = payload.get("activation") or {}
    if activation.get("authorized_by") != "human_user":
        raise ValueError("Architectural-clay runtime promotion requires human activation")
    if activation.get("keeper_approval_implied") is not False:
        raise ValueError("Clay activation must not imply keeper approval")

    entries = payload.get("entries")
    if not isinstance(entries, list) or not entries:
        raise ValueError("The clay library has no runtime entries")

    unique_fields = {
        "candidate": set(),
        "family": set(),
        "archetype_variant": set(),
        "model_path": set(),
    }
    for entry in entries:
        candidate = str(entry.get("candidate") or "")
        family = str(entry.get("family") or "")
        identity = (str(entry.get("archetype_id") or ""), str(entry.get("variant_id") or ""))
        model = entry.get("model") or {}
        model_relative = _safe_relative_model_path(model.get("path"))
        values = {
            "candidate": candidate,
            "family": family,
            "archetype_variant": identity,
            "model_path": model_relative.as_posix(),
        }
        if not candidate or not family or not all(identity):
            raise ValueError(f"Incomplete exact identity for {candidate or model_relative}")
        for key, value in values.items():
            if value in unique_fields[key]:
                raise ValueError(f"Duplicate {key}: {value!r}")
            unique_fields[key].add(value)
        if entry.get("runtime_enabled") is not True:
            raise ValueError(f"Disabled entry belongs outside the runtime list: {candidate}")

        floors = entry.get("native_floors")
        dimensions = entry.get("design_dimensions_m") or {}
        if not isinstance(floors, int) or floors < 1:
            raise ValueError(f"Invalid native floor count for {candidate}")
        if any(not math.isfinite(float(dimensions.get(axis) or 0)) or float(dimensions.get(axis) or 0) <= 0
               for axis in ("width", "depth", "height")):
            raise ValueError(f"Invalid design dimensions for {candidate}")

        model_path = clay_root.joinpath(*model_relative.parts)
        if not model_path.is_file():
            raise FileNotFoundError(model_path)
        if model_path.stat().st_size != int(model.get("bytes") or -1):
            raise ValueError(f"Model byte count mismatch for {candidate}")
        if _sha256(model_path) != _validate_hash(model.get("sha256"), candidate):
            raise ValueError(f"Model hash mismatch for {candidate}")
        counts = _glb_counts(model_path)
        expected_counts = {
            "meshes": int(model.get("mesh_count") or 0),
            "materials": int(model.get("material_count") or 0),
            "textures": int(model.get("texture_count") or 0),
            "images": int(model.get("image_count") or 0),
        }
        if counts != expected_counts:
            raise ValueError(f"GLB inventory mismatch for {candidate}: {counts} != {expected_counts}")
        if counts["textures"] or counts["images"]:
            raise ValueError(f"Architectural-clay GLB embeds media: {candidate}")

        # Validate against the delivered scene, including node transforms and
        # every projection. Design measurements are not its placement bounds.
        import trimesh

        scene = trimesh.load(model_path, force="scene", process=False)
        if scene.bounds is None:
            raise ValueError(f"Architectural-clay GLB has no metric geometry: {candidate}")
        measured = dict(zip(("width", "height", "depth"), scene.extents))
        native = model.get("native_dimensions_m") or {}
        for axis, value in measured.items():
            declared = float(native.get(axis) or 0)
            if not math.isfinite(declared) or declared <= 0 or not math.isclose(declared, float(value), abs_tol=1e-4, rel_tol=1e-6):
                raise ValueError(f"Native {axis} does not match delivered GLB bounds for {candidate}")

        references = entry.get("references")
        if not isinstance(references, list):
            raise ValueError(f"Missing references for {candidate}")
        if {str(item.get("role") or "") for item in references} != REQUIRED_SOURCE_ROLES:
            raise ValueError(f"Reference roles are not exactly front/oblique/top for {candidate}")
        for reference in references:
            repo_path = PurePosixPath(str(reference.get("repo_path") or ""))
            if (
                repo_path.is_absolute()
                or ".." in repo_path.parts
                or repo_path.parts[:4]
                != ("frontend", "public", "archetypes", "buildings")
            ):
                raise ValueError(f"Non-authoritative source path for {candidate}: {repo_path}")
            source = repo_root.joinpath(*repo_path.parts)
            if not source.is_file():
                raise FileNotFoundError(source)
            if source.stat().st_size != int(reference.get("bytes") or -1):
                raise ValueError(f"Reference byte count mismatch: {source}")
            expected_hash = _validate_hash(reference.get("sha256"), str(source))
            if _sha256(source) != expected_hash:
                raise ValueError(f"Reference hash mismatch: {source}")

        review = entry.get("review") or {}
        if "PASS" not in str(review.get("status") or "").upper():
            raise ValueError(f"Independent review is not passing for {candidate}")
        if review.get("unresolved_p0") != 0 or review.get("unresolved_p1") != 0:
            raise ValueError(f"Independent review has blockers for {candidate}")
        _validate_hash(review.get("sha256"), f"{candidate} review")

    for archived in payload.get("review_only_archive") or []:
        if archived.get("runtime_enabled") is not False:
            raise ValueError("Scoped-only review archive cannot be runtime enabled")


def load_library(path: Path | None = None, *, repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    manifest = path or LIBRARY_PATH
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    _validate_payload(payload, clay_root=manifest.parent, repo_root=repo_root)
    return payload


def clay_seed_objects(payload: dict[str, Any], *, clay_root: Path = CLAY_ROOT) -> Iterable[ClaySeedObject]:
    for entry in payload["entries"]:
        model_relative = _safe_relative_model_path(entry["model"]["path"])
        source = clay_root.joinpath(*model_relative.parts)
        yield ClaySeedObject(
            source=source,
            storage_key=f"library/rlasm-architectural-clay/{model_relative.name}",
        )


def _thumbnail_url(entry: dict[str, Any]) -> str:
    front = next(reference for reference in entry["references"] if reference["role"] == "front")
    repo_path = str(front["repo_path"])
    prefix = "frontend/public"
    if not repo_path.startswith(prefix):
        raise ValueError(f"Unexpected front-reference path: {repo_path}")
    return repo_path[len(prefix) :]


def clay_seed_rows(payload: dict[str, Any]) -> Iterable[dict[str, Any]]:
    created_at = payload.get("updated_at") or payload["created_at"]
    for entry in payload["entries"]:
        model_name = PurePosixPath(entry["model"]["path"]).name
        model_url = f"/api/v1/files/library/rlasm-architectural-clay/{model_name}"
        dimensions = entry["model"]["native_dimensions_m"]
        floors = int(entry["native_floors"])
        candidate = entry["candidate"]
        variant_id = entry["variant_id"]
        archetype_id = entry["archetype_id"]
        yield {
            "id": str(
                uuid.uuid5(
                    uuid.NAMESPACE_URL,
                    f"https://cityprompt.ai/model-library/rlasm-clay/{candidate}",
                )
            ),
            "owner_id": SEED_OWNER_ID,
            "source_building_id": None,
            "source_project_id": None,
            "name": f"{entry['archetype_label']} — {entry['variant_label']} — RLASM Clay",
            "description": (
                f"Exact-variant, fixed-native-scale RLASM v6.1 architectural-clay "
                f"delivery for {entry['archetype_label']} / {entry['variant_label']}."
            ),
            "category": "building",
            "tags": ["rlasm", "architectural-clay", archetype_id, variant_id],
            "model_url": model_url,
            "lod_urls": {"0": model_url},
            "thumbnail_url": _thumbnail_url(entry),
            "generation_prompt": (
                f"Exact catalogue variant {variant_id}; preserve its reviewed native "
                "architectural-clay composition without sibling substitution or resizing."
            ),
            "generation_engine": "rlasm",
            "architectural_style": entry["variant_label"],
            "is_public": True,
            "use_count": 0,
            "metadata": {
                "rlasm": {
                    "method": "RLASM",
                    "method_version": "6.1",
                    "delivery_format": "architectural_clay",
                    "runtime_enabled": True,
                    "source_locked": True,
                    "candidate": candidate,
                    "archetype_id": archetype_id,
                    "variant_id": variant_id,
                    "model_sha256": entry["model"]["sha256"],
                    "review_status": entry["review"]["status"],
                    "review_sha256": entry["review"]["sha256"],
                    "continuous_resize_allowed": False,
                    "terrain_fit_verified": False,
                    "scaling_verified": False,
                    "keeper_approved": False,
                    "native_dimensions_m": dict(dimensions),
                    "design_dimensions_m": dict(entry["design_dimensions_m"]),
                },
                "lego": {
                    "enabled": True,
                    "family": entry["family"],
                    "role": "assembled",
                    "width_m": float(dimensions["width"]),
                    "depth_m": float(dimensions["depth"]),
                    "height_m": float(dimensions["height"]),
                    "archetype_ids": [archetype_id, variant_id],
                    "reuse_keys": [variant_id],
                    "min_floors": floors,
                    "max_floors": floors,
                    "repeatable_z": False,
                    "variant_key": variant_id,
                    "lod": 0,
                    "allowed_levels": [floors],
                    "native_floors": floors,
                    "source_variant_id": variant_id,
                    "generation_archetype_id": variant_id,
                    "footprint_compatibility": {
                        "placementMode": "select_and_place",
                        "polygonFit": False,
                        "continuous_resize_allowed": False,
                    },
                    "placement_contract": {
                        "mode": "fixed_landmark",
                        "continuous_resize_allowed": False,
                    },
                    "allow_inset_footprint": True,
                },
            },
            "created_at": created_at,
        }
