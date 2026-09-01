"""Contract tests for real, non-stretching RLASM semantic LEGO frontage."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "backend"))

from app.services.lego_assembly import (  # noqa: E402
    AssemblyPlanningError,
    AssemblyRequest,
    ModuleDescriptor,
    lego_metadata_from_manifest,
    manifest_validation_errors,
    plan_vertical_assembly,
)


def semantic_module(
    semantic_role: str,
    width_m: float,
    *,
    variant_key: str | None = None,
) -> ModuleDescriptor:
    repeatable = semantic_role == "middle"
    variant = variant_key or semantic_role
    return ModuleDescriptor(
        id=f"historical-{variant}",
        name=f"Historical {variant}",
        model_url=f"/{variant}.glb",
        family="historical-brick-main-street-semantic-v4",
        role="attachment",
        width_m=width_m,
        depth_m=22.5,
        height_m=11.25,
        archetype_ids=("historical_brick_main_street", "historical_brick_victorian"),
        reuse_keys=("historical", "brick", "main-street"),
        min_floors=2,
        max_floors=2,
        native_floors=2,
        variant_key=variant,
        allow_inset_footprint=True,
        assembly_axis="x",
        semantic_role=semantic_role,
        repeatable_x=repeatable,
        required_once=not repeatable,
        min_repeats=2 if repeatable else None,
        max_repeats=20 if repeatable else None,
        native_repeat_count=2 if repeatable else None,
    )


@pytest.fixture
def kit() -> list[ModuleDescriptor]:
    return [
        semantic_module("left_end", 1.35),
        semantic_module("middle", 2.10, variant_key="middle_a"),
        semantic_module("middle", 2.10, variant_key="middle_b"),
        semantic_module("middle", 2.10, variant_key="middle_c"),
        semantic_module("entrance", 8.10),
        semantic_module("right_end", 1.35),
    ]


def plan(kit: list[ModuleDescriptor], width_m: float) -> dict:
    return plan_vertical_assembly(
        kit,
        AssemblyRequest(
            width_m,
            24.0,
            2,
            archetype_id="historical_brick_victorian",
            preferred_family="historical-brick-main-street-semantic-v4",
        ),
    )


@pytest.mark.parametrize(
    ("target_width", "expected_middle", "expected_occupied"),
    ((15.0, 2, 15.0), (19.2, 4, 19.2), (30.0, 8, 27.6)),
)
def test_width_growth_adds_whole_bays_without_scaling_fixed_identity(
    kit: list[ModuleDescriptor],
    target_width: float,
    expected_middle: int,
    expected_occupied: float,
) -> None:
    recipe = plan(kit, target_width)

    assert recipe["version"] == 4
    assert recipe["fit"]["assembly_mode"] == "semantic_bay_grid"
    assert recipe["fit"]["occupied_width_m"] == pytest.approx(expected_occupied)
    assert recipe["semantic_invariants"]["repeatable_middle_count"] == expected_middle
    assert recipe["semantic_invariants"]["fixed_anchor_counts"] == {
        "left_end": 1,
        "entrance": 1,
        "right_end": 1,
    }
    assert all(instance["scale"] == [1.0, 1.0, 1.0] for instance in recipe["instances"])
    assert sum(instance["semantic_role"] == "entrance" for instance in recipe["instances"]) == 1


def test_oversized_fractional_remainder_becomes_symmetric_site_margin(
    kit: list[ModuleDescriptor],
) -> None:
    recipe = plan(kit, 30.0)
    assert recipe["fit"]["site_margin_width_each_m"] == pytest.approx(1.2)
    entrance = next(instance for instance in recipe["instances"] if instance["semantic_role"] == "entrance")
    assert entrance["position"][0] == pytest.approx(0.0)


def test_narrow_or_wrong_height_target_never_enters_forced_fit(
    kit: list[ModuleDescriptor],
) -> None:
    for request in (
        AssemblyRequest(
            10.0,
            24.0,
            2,
            archetype_id="historical_brick_victorian",
            preferred_family="historical-brick-main-street-semantic-v4",
        ),
        AssemblyRequest(
            15.0,
            24.0,
            3,
            archetype_id="historical_brick_victorian",
            preferred_family="historical-brick-main-street-semantic-v4",
        ),
    ):
        with pytest.raises(AssemblyPlanningError):
            plan_vertical_assembly(kit, request, allow_forced_fit=True)


def test_manifest_v4_preserves_semantic_module_contract() -> None:
    modules = [
        {
            "role": "attachment",
            "variant_key": semantic_role,
            "filename": f"{semantic_role}.glb",
            "width_m": width,
            "depth_m": 22.5,
            "height_m": 11.25,
            "assembly_axis": "x",
            "semantic_role": semantic_role,
            "required_once": semantic_role != "middle",
            "repeatable_x": semantic_role == "middle",
            "native_repeat_count": 2 if semantic_role == "middle" else None,
        }
        for semantic_role, width in (
            ("left_end", 1.35),
            ("middle", 2.10),
            ("entrance", 8.10),
            ("right_end", 1.35),
        )
    ]
    manifest = {
        "manifest_schema": 4,
        "grammar_schema_version": 4,
        "family": "historical-brick-main-street-semantic-v4",
        "archetype_id": "historical_brick_main_street",
        "variant_id": "historical_brick_victorian",
        "reuse_keys": ["historical"],
        "dimensions": {"min_floors": 2, "max_floors": 2},
        "modules": modules,
    }

    assert manifest_validation_errors(manifest) == []
    metadata = lego_metadata_from_manifest(manifest, modules[1])
    assert metadata["enabled"] is True
    assert metadata["semantic_role"] == "middle"
    assert metadata["repeatable_x"] is True
    assert metadata["native_repeat_count"] == 2
