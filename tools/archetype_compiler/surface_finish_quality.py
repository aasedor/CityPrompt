"""Audit baked PBR story materials and Blender-to-GLB render parity."""
from __future__ import annotations

import argparse
import json
import struct
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image


def glb_json(path: Path) -> dict[str, Any]:
    with path.open("rb") as stream:
        magic, version, _length = struct.unpack("<4sII", stream.read(12))
        if magic != b"glTF" or version != 2:
            raise ValueError(f"{path} is not a glTF 2 GLB")
        chunk_length, chunk_type = struct.unpack("<II", stream.read(8))
        if chunk_type != 0x4E4F534A:
            raise ValueError(f"{path} does not start with a JSON chunk")
        return json.loads(stream.read(chunk_length))


def resolved_material_specs(grammar: dict[str, Any]) -> dict[str, dict[str, Any]]:
    materials = dict(grammar.get("materials") or {})
    overrides = (
        (grammar.get("architectural_signature") or {}).get("signature_material_overrides") or {}
    )
    materials.update(overrides)
    return materials


def render_parity(source_path: Path, roundtrip_path: Path) -> dict[str, Any]:
    source = np.asarray(Image.open(source_path).convert("RGB"), dtype=np.float32) / 255.0
    roundtrip = np.asarray(
        Image.open(roundtrip_path).convert("RGB").resize(
            (source.shape[1], source.shape[0]), Image.Resampling.LANCZOS
        ),
        dtype=np.float32,
    ) / 255.0
    delta = np.abs(source - roundtrip)
    return {
        "mean_absolute_error": round(float(delta.mean()), 5),
        "p95_absolute_error": round(float(np.percentile(delta, 95)), 5),
        "similarity": round(1.0 - float(delta.mean()), 5),
        "passed": float(delta.mean()) <= 0.14,
    }


def assess(
    grammar: dict[str, Any],
    story_manifest: dict[str, Any],
    glb: dict[str, Any],
    *,
    source_render: Path | None = None,
    roundtrip_render: Path | None = None,
) -> dict[str, Any]:
    production = (grammar.get("architectural_signature") or {}).get("production_contract") or {}
    finish = production.get("surface_finish") or {}
    required_ids = [str(value) for value in finish.get("required_baked_materials") or []]
    specs = resolved_material_specs(grammar)
    story_by_key = {
        str(item.get("texture_key")): item for item in story_manifest.get("materials") or []
    }
    glb_by_key = {
        str((material.get("extras") or {}).get("texture_key")): material
        for material in glb.get("materials") or []
        if (material.get("extras") or {}).get("texture_key")
    }
    checks: list[dict[str, Any]] = []
    for material_id in required_ids:
        spec = specs.get(material_id) or {}
        key = str(spec.get("texture_key") or "")
        story = story_by_key.get(key) or {}
        exported = glb_by_key.get(key) or {}
        statistics = story.get("statistics") or {}
        pbr = exported.get("pbrMetallicRoughness") or {}
        channels_present = bool(
            pbr.get("baseColorTexture")
            and pbr.get("metallicRoughnessTexture")
            and exported.get("normalTexture")
        )
        variation_present = (
            float(statistics.get("albedo_std", 0.0)) >= 4.0
            and float(statistics.get("roughness_std", 0.0)) >= 2.0
            and float(statistics.get("normal_xy_std", 0.0)) >= 1.0
        )
        checks.extend([
            {
                "id": f"story_manifest:{material_id}",
                "passed": bool(story) and story.get("baked_pbr") is True,
                "detail": f"{material_id} resolves to {key!r}",
            },
            {
                "id": f"surface_variation:{material_id}",
                "passed": variation_present,
                "detail": statistics,
            },
            {
                "id": f"glb_pbr_channels:{material_id}",
                "passed": channels_present,
                "detail": f"exported material {exported.get('name')!r}",
            },
        ])
    parity = None
    if source_render and roundtrip_render:
        parity = render_parity(source_render, roundtrip_render)
        checks.append({
            "id": "neutral_glb_roundtrip_parity",
            "passed": parity["passed"],
            "detail": parity,
        })
    else:
        checks.append({
            "id": "neutral_glb_roundtrip_parity",
            "passed": False,
            "detail": "source and GLB neutral renders are both required",
        })
    failures = [item for item in checks if not item["passed"]]
    return {
        "schema": "surface-finish-quality@1",
        "status": "fail" if failures else "pass",
        "required_materials": required_ids,
        "render_parity": parity,
        "failures": failures,
        "checks": checks,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--grammar", type=Path, required=True)
    parser.add_argument("--story-manifest", type=Path, required=True)
    parser.add_argument("--glb", type=Path, required=True)
    parser.add_argument("--source-render", type=Path, required=True)
    parser.add_argument("--roundtrip-render", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = assess(
        json.loads(args.grammar.read_text(encoding="utf-8")),
        json.loads(args.story_manifest.read_text(encoding="utf-8")),
        glb_json(args.glb),
        source_render=args.source_render,
        roundtrip_render=args.roundtrip_render,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"{report['status'].upper()} {args.output}")
    raise SystemExit(0 if report["status"] == "pass" else 1)


if __name__ == "__main__":
    main()
