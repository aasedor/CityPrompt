from types import SimpleNamespace

import pytest

from app.services.lego_assembly import (
    AssemblyPlanningError,
    AssemblyRequest,
    descriptor_from_library_entry,
    plan_vertical_assembly,
)


def entry(asset_id: str, name: str, role: str, *, height: float, width: float = 24, depth: float = 18):
    return SimpleNamespace(
        id=asset_id,
        name=name,
        model_url=f"https://example.test/{asset_id}.glb",
        metadata_={
            "lego": {
                "enabled": True,
                "role": role,
                "family": "nordic-midrise",
                "width_m": width,
                "depth_m": depth,
                "height_m": height,
                "repeatable_z": role == "floor",
                "archetype_ids": ["nordic-midrise"],
                "reuse_keys": ["nordic", "mixed-use"],
                "min_floors": 3,
                "max_floors": 12,
            }
        },
    )


def test_descriptor_ignores_unconfigured_library_items():
    raw = SimpleNamespace(id="x", name="X", model_url="x.glb", metadata_={})
    assert descriptor_from_library_entry(raw) is None


def test_vertical_plan_reuses_archetype_metadata_and_stacks_modules():
    modules = [
        descriptor_from_library_entry(entry("podium", "Retail podium", "podium", height=4.5)),
        descriptor_from_library_entry(entry("floor", "Residential floor", "floor", height=3.2)),
        descriptor_from_library_entry(entry("setback", "Setback floor", "setback", height=3.2)),
        descriptor_from_library_entry(entry("roof", "Green roof", "roof", height=1.0)),
    ]

    plan = plan_vertical_assembly(
        [module for module in modules if module],
        AssemblyRequest(
            target_width_m=24,
            target_depth_m=18,
            target_floors=6,
            archetype_id="nordic-midrise",
            reuse_keys=("nordic", "mixed-use"),
        ),
    )

    assert plan["family"] == "nordic-midrise"
    assert [item["role"] for item in plan["instances"]] == [
        "podium",
        "floor",
        "floor",
        "floor",
        "floor",
        "setback",
        "roof",
    ]
    assert plan["instances"][0]["position"] == [0.0, 0.0, 0.0]
    assert plan["assembled_height_m"] == pytest.approx(21.5)
    assert plan["archetype_id"] == "nordic-midrise"
    assert plan["reuse_keys"] == ["nordic", "mixed-use"]


def test_rejects_destructive_footprint_scaling():
    modules = [
        descriptor_from_library_entry(entry("podium", "Podium", "podium", height=4.5)),
        descriptor_from_library_entry(entry("floor", "Floor", "floor", height=3.2)),
        descriptor_from_library_entry(entry("roof", "Roof", "roof", height=1.0)),
    ]

    with pytest.raises(AssemblyPlanningError):
        plan_vertical_assembly(
            [module for module in modules if module],
            AssemblyRequest(target_width_m=40, target_depth_m=18, target_floors=5),
        )
