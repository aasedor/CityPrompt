from types import SimpleNamespace

import pytest

from app.services.lego_assembly import (
    AssemblyPlanningError,
    AssemblyRequest,
    ModuleDescriptor,
    RLASM_ARCHITECTURAL_CLAY_FORMAT,
    RLASM_ARCHITECTURAL_CLAY_MODULE_FORMAT,
    descriptor_from_library_entry,
    plan_vertical_assembly,
    select_runtime_architecture_entries,
)


FAMILY = "vancouver-balcony-podium-tower"
VARIANT = "vancouverism_classic"


def module(role: str, width: float, depth: float, height: float, occupied_storeys: int) -> ModuleDescriptor:
    return ModuleDescriptor(
        id=role,
        name=role,
        model_url=f"/{role}.glb",
        family=FAMILY,
        role=role,
        width_m=width,
        depth_m=depth,
        height_m=height,
        archetype_ids=("vancouverism_tower_podium", VARIANT),
        reuse_keys=(VARIANT,),
        min_floors=16,
        max_floors=40,
        repeatable_z=role == "floor",
        variant_key=VARIANT,
        occupied_storeys=occupied_storeys,
        source_variant_id=VARIANT,
        generation_archetype_id=VARIANT,
        allow_inset_footprint=True,
        delivery_format=RLASM_ARCHITECTURAL_CLAY_MODULE_FORMAT,
    )


def family() -> list[ModuleDescriptor]:
    return [
        ModuleDescriptor(
            id="native",
            name="native",
            model_url="/native.glb",
            family=FAMILY,
            role="assembled",
            width_m=48.055,
            depth_m=40.055,
            height_m=58.8,
            archetype_ids=("vancouverism_tower_podium", VARIANT),
            reuse_keys=(VARIANT,),
            min_floors=16,
            max_floors=16,
            native_floors=16,
            source_variant_id=VARIANT,
            generation_archetype_id=VARIANT,
            delivery_format=RLASM_ARCHITECTURAL_CLAY_FORMAT,
        ),
        module("podium", 48.055, 40.055, 13.0, 3),
        module("floor", 34.731369, 28.3525, 3.2, 1),
        module("roof", 35.752499, 29.055, 4.2, 0),
    ]


@pytest.mark.parametrize(("storeys", "height", "floor_modules"), [(25, 87.6, 22), (40, 135.6, 37)])
def test_authored_vancouver_program_repeats_complete_floors(storeys, height, floor_modules):
    plan = plan_vertical_assembly(
        family(),
        AssemblyRequest(52, 44, storeys, archetype_id=VARIANT),
    )
    roles = [instance["role"] for instance in plan["instances"]]
    assert roles.count("podium") == 1
    assert roles.count("floor") == floor_modules
    assert roles.count("roof") == 1
    assert plan["assembled_height_m"] == height
    assert plan["fit"]["delivery_format"] == RLASM_ARCHITECTURAL_CLAY_MODULE_FORMAT
    assert all(instance["scale"][2] == 1 for instance in plan["instances"])


def test_native_vancouver_remains_the_unchanged_reviewed_assembly():
    plan = plan_vertical_assembly(
        family(),
        AssemblyRequest(52, 44, 16, archetype_id=VARIANT),
    )
    assert [instance["role"] for instance in plan["instances"]] == ["assembled"]
    assert plan["assembled_height_m"] == 58.8


def test_maximum_footprint_does_not_change_the_40_storey_height():
    plan = plan_vertical_assembly(
        family(),
        AssemblyRequest(57.5, 47.5, 40, archetype_id=VARIANT),
    )
    assert plan["assembled_height_m"] == 135.6
    assert all(instance["scale"][2] == 1 for instance in plan["instances"])
    assert plan["fit"]["scale_x"] == plan["fit"]["scale_y"]


def test_storeys_outside_the_reviewed_program_are_rejected():
    with pytest.raises(AssemblyPlanningError, match="fixed at its native size and floor count"):
        plan_vertical_assembly(
            family(),
            AssemblyRequest(52, 44, 41, archetype_id=VARIANT),
        )


def test_module_metadata_retains_authored_floor_credit():
    entry = SimpleNamespace(
        id="podium",
        name="podium",
        model_url="/podium.glb",
        metadata_={
            "rlasm": {
                "delivery_format": RLASM_ARCHITECTURAL_CLAY_MODULE_FORMAT,
                "method_version": "6.1",
                "runtime_enabled": True,
                "continuous_resize_allowed": False,
                "variant_id": VARIANT,
            },
            "lego": {
                "enabled": True,
                "family": FAMILY,
                "role": "podium",
                "width_m": 48.055,
                "depth_m": 40.055,
                "height_m": 13,
                "source_variant_id": VARIANT,
                "generation_archetype_id": VARIANT,
                "occupied_storeys": 3,
            },
        },
    )
    descriptor = descriptor_from_library_entry(entry)
    assert descriptor is not None
    assert descriptor.occupied_storeys == 3
    assert descriptor.delivery_format == RLASM_ARCHITECTURAL_CLAY_MODULE_FORMAT


def test_installed_clay_tier_keeps_valid_authored_modules_available():
    exact = SimpleNamespace(
        id="native",
        name="native",
        model_url="/native.glb",
        is_public=True,
        metadata_={
            "rlasm": {
                "delivery_format": RLASM_ARCHITECTURAL_CLAY_FORMAT,
                "method_version": "6.1",
                "runtime_enabled": True,
                "continuous_resize_allowed": False,
                "variant_id": VARIANT,
            },
            "lego": {
                "enabled": True,
                "family": FAMILY,
                "role": "assembled",
                "width_m": 48.055,
                "depth_m": 40.055,
                "height_m": 58.8,
                "native_floors": 16,
                "min_floors": 16,
                "max_floors": 16,
                "repeatable_z": False,
                "source_variant_id": VARIANT,
                "generation_archetype_id": VARIANT,
            },
        },
    )
    authored_floor = SimpleNamespace(
        id="floor",
        name="floor",
        model_url="/floor.glb",
        is_public=True,
        metadata_={
            "rlasm": {
                "delivery_format": RLASM_ARCHITECTURAL_CLAY_MODULE_FORMAT,
                "method_version": "6.1",
                "runtime_enabled": True,
                "continuous_resize_allowed": False,
                "variant_id": VARIANT,
            },
            "lego": {
                "enabled": True,
                "family": FAMILY,
                "role": "floor",
                "width_m": 34.731369,
                "depth_m": 28.3525,
                "height_m": 3.2,
                "repeatable_z": True,
                "source_variant_id": VARIANT,
                "generation_archetype_id": VARIANT,
            },
        },
    )

    selected = select_runtime_architecture_entries([exact, authored_floor])

    assert selected.clay_installed is True
    assert [entry.id for entry in selected] == ["native", "floor"]
