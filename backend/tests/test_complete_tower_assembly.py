"""Exercise the exact private-row contract emitted by the landmark installer."""

import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.landmark_tower_storeys import private_binding, SOURCES
from app.services.lego_assembly import (
    descriptor_from_library_entry,
    plan_vertical_assembly,
    AssemblyRequest,
    AssemblyPlanningError,
)


@pytest.mark.parametrize(
    "family,count,width,depth,height",
    [
        ("gilded", 25, 32.779998779296875, 29.31721782684326, 95.8),
        ("gilded", 35, 32.779998779296875, 29.31721782684326, 129.8),
        ("twisted", 20, 43.4902229309082, 44.02571678161621, 79.7),
        ("twisted", 30, 43.4902229309082, 44.0266170501709, 113.7),
    ],
)
def test_installer_complete_assemblies_are_native_locked_and_cannot_shrink(family, count, width, depth, height):
    spec = SOURCES[family]
    contract = dict(
        source_variant_id=spec["variant_id"],
        occupied_storeys=count,
        sha256="a" * 64,
        id=spec["variant_id"] + "-authored-heights-v001",
        candidate="derived-v1",
        native_dimensions_m=dict(width=width, depth=depth, height=height),
        path="/not-read.glb",
        bytes=1,
    )
    row = private_binding(contract)
    module = descriptor_from_library_entry(
        SimpleNamespace(id=row["id"], name=row["name"], model_url=row["model_url"], metadata_=row["metadata"])
    )
    request = AssemblyRequest(width, depth, count, archetype_id=spec["variant_id"], model_revision="derived-v1")
    plan = plan_vertical_assembly([module], request, allow_forced_fit=False)
    assert plan["fit"]["native_scale_locked"] is True
    assert plan["instances"][0]["scale"] == [1, 1, 1]
    assert len(plan["instances"]) == 1
    with pytest.raises(AssemblyPlanningError):
        plan_vertical_assembly(
            [module],
            AssemblyRequest(
                width * 0.9, depth * 0.9, count, archetype_id=spec["variant_id"], model_revision="derived-v1"
            ),
            allow_forced_fit=False,
        )
