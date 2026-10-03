from pathlib import Path
from types import SimpleNamespace
import sys

import pytest

from app.services.lego_assembly import (
    AssemblyPlanningError,
    AssemblyRequest,
    descriptor_from_library_entry,
    plan_vertical_assembly,
)


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from scripts.house_flex_pilot import load_program  # noqa: E402


def program_families():
    _, rows = load_program(ROOT)
    grouped = {}
    for row in rows:
        descriptor = descriptor_from_library_entry(
            SimpleNamespace(
                id=row["id"],
                name=row["name"],
                model_url=row["model_url"],
                metadata_=row["metadata"],
                is_public=True,
            )
        )
        assert descriptor is not None
        grouped.setdefault(row["variantId"], []).append(descriptor)
    return grouped


@pytest.mark.parametrize(
    "variant",
    [
        "bungalow_postwar_ranch",
        "toronto_foursquare_red_brick",
        "clapboard_north_end",
    ],
)
@pytest.mark.parametrize("storeys", [1, 2])
@pytest.mark.parametrize("scale", [0.85, 1.0, 1.15])
def test_house_pilot_selects_a_complete_assembly_with_uniform_xy_scale(variant, storeys, scale):
    family = program_families()[variant]
    assembly = next(module for module in family if module.native_floors == storeys)

    plan = plan_vertical_assembly(
        family,
        AssemblyRequest(
            assembly.width_m * scale,
            assembly.depth_m * scale,
            storeys,
            archetype_id=variant,
        ),
    )

    assert [instance["role"] for instance in plan["instances"]] == ["assembled"]
    assert plan["instances"][0]["asset_id"] == assembly.id
    assert plan["instances"][0]["scale"] == [scale, scale, 1.0]
    assert plan["assembled_height_m"] == pytest.approx(assembly.height_m)
    assert plan["fit"]["delivery_format"] in {"architectural_clay", "architectural_clay_module_v1"}


@pytest.mark.parametrize(
    "variant",
    [
        "bungalow_postwar_ranch",
        "toronto_foursquare_red_brick",
        "clapboard_north_end",
    ],
)
def test_house_pilot_rejects_storeys_outside_the_finite_program(variant):
    family = program_families()[variant]
    with pytest.raises(AssemblyPlanningError):
        plan_vertical_assembly(
            family,
            AssemblyRequest(family[0].width_m, family[0].depth_m, 3, archetype_id=variant),
        )


def test_house_pilot_does_not_cross_bind_sibling_variants():
    families = program_families()
    with pytest.raises(AssemblyPlanningError):
        plan_vertical_assembly(
            families["bungalow_postwar_ranch"],
            AssemblyRequest(10.898324, 16.05, 1, archetype_id="toronto_foursquare_red_brick"),
        )
