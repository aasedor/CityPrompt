"""Geometry-conditioned Sticker Method registration packages.

The package fingerprints the exact carrier used by every image-locked surface.
It is deliberately renderer-independent: Blender consumes the same geometry
and mapping declarations, while tests can reject a sticker that was authored
for a different mesh or transformed after approval.
"""
from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA = "siteforge.sticker-carrier-space@1"


def _sha256(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def mapping_method(spec: dict[str, Any]) -> str:
    axis = str(spec.get("axis", "front"))
    return {
        "front": "rectified_elevation",
        "rear": "rectified_elevation",
        "left": "rectified_elevation",
        "right": "rectified_elevation",
        "angle": "rectified_oblique_plane",
        "cylindrical_segment": "conformal_cylindrical_segment",
        "dome_radial": "radial_gore",
        "plan": "plan_orthographic",
        "box_projected": "directional_per_face_box_projection",
    }.get(axis, f"unsupported:{axis}")


def _target_meshes(targets: list[str], geometry: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        mesh for mesh in geometry.get("meshes", [])
        if any(str(mesh.get("name")) == target or str(mesh.get("name", "")).startswith(f"{target}_") for target in targets)
    ]


def _producer_for(target: str, assemblies: list[dict[str, Any]]) -> dict[str, Any] | None:
    candidates = [item for item in assemblies if target == str(item.get("id")) or target.startswith(f"{item.get('id')}_")]
    return max(candidates, key=lambda item: len(str(item.get("id", ""))), default=None)


def _mesh_carrier(mesh: dict[str, Any], face_indices: list[int]) -> dict[str, Any]:
    faces = mesh.get("faces") or []
    selected = face_indices or list(range(len(faces)))
    if not selected or min(selected) < 0 or max(selected) >= len(faces):
        raise ValueError(f"carrier selects invalid faces on {mesh.get('name')!r}: {selected}")
    used = sorted({int(vertex) for face_index in selected for vertex in faces[face_index]})
    payload = {
        "mesh": str(mesh["name"]),
        "vertices": [mesh["vertices"][index] for index in used],
        "faces": [faces[index] for index in selected],
        "selected_face_indices": selected,
    }
    return {
        "kind": "locked_mesh_faces",
        "target": str(mesh["name"]),
        "selected_face_count": len(selected),
        "fingerprint_sha256": _sha256(payload),
    }


def condition_profile(
    profile: dict[str, Any], geometry: dict[str, Any], *, score_target: int = 95,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Attach exact-carrier fingerprints and return the reviewable package."""

    conditioned = deepcopy(profile)
    graph = conditioned["massing_graph"]
    assemblies = graph.get("assemblies") or []
    geometry_sha = str(geometry["geometry_sha256"])
    records: list[dict[str, Any]] = []
    failures: list[dict[str, str]] = []

    for assembly in assemblies:
        if assembly.get("kind") != "carrier_skin":
            continue
        carrier_id = str(assembly.get("id", ""))
        targets = [str(value) for value in assembly.get("target_ids") or []]
        source = Path(str(assembly.get("source_image_path", "")))
        source = source if source.is_absolute() else REPO_ROOT / source
        method = mapping_method(assembly)
        carriers: list[dict[str, Any]] = []
        for mesh in _target_meshes(targets, geometry):
            carriers.append(_mesh_carrier(mesh, [int(value) for value in assembly.get("face_indices") or []]))
        if not carriers:
            for target in targets:
                producer = _producer_for(target, assemblies)
                if producer is not None:
                    carriers.append({
                        "kind": "locked_parametric_assembly",
                        "target": target,
                        "producer_id": str(producer["id"]),
                        "fingerprint_sha256": _sha256(producer),
                    })
        if not targets or not carriers:
            failures.append({"carrier": carrier_id, "reason": "unresolved_final_carrier"})
        if not source.is_file():
            failures.append({"carrier": carrier_id, "reason": f"missing_source:{source}"})
        if method.startswith("unsupported:"):
            failures.append({"carrier": carrier_id, "reason": method})

        record = {
            "carrier_id": carrier_id,
            "surface_id": str(assembly.get("surface_id", "")),
            "sticker_layer": str(assembly.get("sticker_layer", "")),
            "mapping_method": method,
            "mapping_axis": str(assembly.get("axis", "front")),
            "locked_geometry_sha256": geometry_sha,
            "carrier_targets": carriers,
            "source_image_path": str(assembly.get("source_image_path", "")),
            "source_image_sha256": _file_sha256(source) if source.is_file() else None,
            "source_uv_bounds": [
                float(assembly.get("uv_u_min", 0.0)), float(assembly.get("uv_v_min", 0.0)),
                float(assembly.get("uv_u_max", 1.0)), float(assembly.get("uv_v_max", 1.0)),
            ],
            "floor_role": str(assembly.get("floor_role", "")),
            "approval_space": "rendered_on_locked_carrier",
            "post_generation_crop_allowed": False,
            "post_generation_nonuniform_scale_allowed": False,
        }
        record["registration_sha256"] = _sha256(record)
        assembly["carrier_space"] = {
            "schema": SCHEMA,
            "locked_geometry_sha256": geometry_sha,
            "mapping_method": method,
            "registration_sha256": record["registration_sha256"],
            "approval_space": "rendered_on_locked_carrier",
            "post_generation_crop_allowed": False,
            "post_generation_nonuniform_scale_allowed": False,
        }
        records.append(record)

    package = {
        "schema": SCHEMA,
        "status": "pass" if not failures else "fail",
        "locked_geometry_sha256": geometry_sha,
        "carrier_count": len(records),
        "score_target": int(score_target),
        "approval_space": "rendered_on_locked_carrier",
        "required_conditioning_maps": [
            "uv_chart", "position", "normal", "depth", "visibility", "curvature",
            "ambient_occlusion", "floor_id", "construction_role", "opening_mask",
            "glass_mask", "uv_distortion",
        ],
        "hard_stops": [
            "carrier_geometry_hash_mismatch", "unresolved_final_carrier",
            "post_generation_crop", "post_generation_nonuniform_scale",
            "source_directional_light_baked_as_surface_albedo",
            "architect_score_below_95",
        ],
        "failures": failures,
        "carriers": records,
    }
    package["package_sha256"] = _sha256({key: value for key, value in package.items() if key != "package_sha256"})
    graph["carrier_space_contract"] = {
        "required": True,
        "schema": SCHEMA,
        "locked_geometry_sha256": geometry_sha,
        "package_sha256": package["package_sha256"],
        "carrier_count": len(records),
        "approval_space": "rendered_on_locked_carrier",
        "architect_score_target": int(score_target),
    }
    return conditioned, package
