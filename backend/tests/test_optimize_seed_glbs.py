from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.optimize_seed_glbs import normalize_materials_payload  # noqa: E402


def _material(name: str, *, extras: dict | None = None) -> dict:
    material = {
        "name": name,
        "doubleSided": True,
        "pbrMetallicRoughness": {
            "baseColorTexture": {"index": 2},
            "metallicFactor": 0,
            "roughnessFactor": 0.72,
        },
    }
    if extras:
        material["extras"] = extras
    return material


def test_normalize_materials_removes_surface_provenance_and_merges_names():
    payload = {
        "materials": [
            _material(
                "MAT_RegisteredCarrier_wall_left",
                extras={
                    "glazing_lod": "far",
                    "sticker_surface_id": "wall_left",
                    "massing_skin_u_min": -4,
                },
            ),
            _material(
                "MAT_RegisteredCarrier_wall_right",
                extras={
                    "glazing_lod": "far",
                    "sticker_surface_id": "wall_right",
                    "massing_skin_u_min": 0,
                },
            ),
        ]
    }

    summary = normalize_materials_payload(payload)

    assert summary["canonical_signatures"] == 1
    assert payload["materials"][0]["name"] == payload["materials"][1]["name"]
    assert payload["materials"][0]["extras"] == {"glazing_lod": "far"}
    assert payload["materials"][1]["extras"] == {"glazing_lod": "far"}


def test_normalize_materials_keeps_glass_runtime_semantics_separate():
    payload = {
        "materials": [
            _material("MAT_RegisteredCarrier_wall"),
            _material("MAT_Glass_industrial_sash"),
        ]
    }

    summary = normalize_materials_payload(payload)

    assert summary["canonical_signatures"] == 2
    assert payload["materials"][0]["name"].startswith("MAT_Optimized_")
    assert payload["materials"][1]["name"].startswith("MAT_Glass_")
