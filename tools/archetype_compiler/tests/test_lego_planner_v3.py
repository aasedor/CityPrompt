"""Pure contract tests for facade-variant-aware LEGO planning.

These live with the compiler tests so they run without the database/FastAPI
dependency stack; the planner service itself deliberately has no framework
imports.
"""
from __future__ import annotations

import sys
from dataclasses import replace
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "backend"))

from app.services.lego_assembly import (  # noqa: E402
    AssemblyRequest,
    ModuleDescriptor,
    find_family_module_entry,
    manifest_validation_errors,
    plan_vertical_assembly,
)


def module(
    role: str,
    height: float,
    variant_key: str = "default",
    repeatable: bool = False,
    lod: int = 0,
) -> ModuleDescriptor:
    return ModuleDescriptor(
        id=f"{role}-{variant_key}-lod{lod}",
        name=f"{role} {variant_key}",
        model_url=f"/{role}-{variant_key}.glb",
        family="v3-family",
        role=role,
        width_m=22.0,
        depth_m=20.0,
        height_m=height,
        archetype_ids=("contemporary_midrise",),
        reuse_keys=("contemporary",),
        min_floors=3,
        max_floors=10,
        repeatable_z=repeatable,
        variant_key=variant_key,
        lod=lod,
    )


def test_planner_alternates_floor_variants_then_places_upper_and_crown():
    modules = [
        module("podium", 4.5),
        module("floor", 3.4, "typical_a", True),
        module("floor", 3.4, "typical_a", True, lod=1),
        module("floor", 3.4, "typical_b", True),
        module("setback", 3.4, "upper"),
        module("crown", 3.4, "crown"),
        module("roof", 1.2),
    ]
    plan = plan_vertical_assembly(
        modules,
        AssemblyRequest(22.0, 20.0, 8, archetype_id="contemporary_midrise"),
    )
    assert plan["version"] == 2
    assert [item["role"] for item in plan["instances"]] == [
        "podium", "floor", "floor", "floor", "floor", "floor", "setback", "crown", "roof",
    ]
    assert [item["variant_key"] for item in plan["instances"][1:6]] == [
        "typical_a", "typical_b", "typical_a", "typical_b", "typical_a",
    ]
    assert plan["instances"][-2]["variant_key"] == "crown"
    assert all(item["lod"] == 0 for item in plan["instances"])


def test_planner_prefers_first_newest_family_when_quality_scores_tie():
    base = [
        module("podium", 4.5),
        module("floor", 3.4, "typical_a", True),
        module("roof", 1.2),
    ]
    newest = [replace(item, id=f"new-{item.id}", family="family-v5-audited") for item in base]
    older = [replace(item, id=f"old-{item.id}", family="family-v4") for item in base]

    plan = plan_vertical_assembly(
        newest + older,
        AssemblyRequest(22.0, 20.0, 5, archetype_id="contemporary_midrise"),
    )

    assert plan["family"] == "family-v5-audited"


def test_manifest_v3_accepts_distinct_floor_identities_and_rejects_duplicates():
    manifest = {
        "manifest_schema": 3,
        "family": "v3-family",
        "archetype_id": "contemporary_midrise",
        "reuse_keys": ["contemporary"],
        "modules": [
            {"role": "floor", "variant_key": "typical_a", "lod": 0, "filename": "a.glb"},
            {"role": "floor", "variant_key": "typical_b", "lod": 0, "filename": "b.glb"},
        ],
    }
    assert manifest_validation_errors(manifest) == []
    manifest["modules"].append(
        {"role": "floor", "variant_key": "typical_a", "lod": 0, "filename": "duplicate.glb"}
    )
    assert any("duplicates module identity" in error for error in manifest_validation_errors(manifest))


def test_dedupe_identity_includes_variant_and_lod():
    class Entry:
        metadata_ = {"lego": {"family": "v3-family", "role": "floor", "variant_key": "typical_b", "lod": 0}}

    entry = Entry()
    assert find_family_module_entry([entry], "v3-family", "floor", "typical_b", 0) is entry
    assert find_family_module_entry([entry], "v3-family", "floor", "typical_a", 0) is None
