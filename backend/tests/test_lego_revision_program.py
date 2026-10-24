from dataclasses import replace
from types import SimpleNamespace

import pytest

from app.services.lego_assembly import (
    AssemblyPlanningError, AssemblyRequest, ModuleDescriptor, descriptor_from_library_entry, plan_vertical_assembly,
)


def house(storeys, revision, *, program="house-flex-v1", family="house-family", variant="bungalow_postwar_ranch"):
    return ModuleDescriptor(
        id=revision, name=revision, model_url=f"/{revision}.glb", family=family,
        role="assembled", width_m=10, depth_m=14, height_m=6.36 if storeys == 1 else 9.29,
        archetype_ids=(variant,), reuse_keys=(), native_floors=storeys,
        min_floors=storeys, max_floors=storeys, source_variant_id=variant,
        generation_archetype_id=variant, model_revision=revision,
        delivery_format="architectural_clay" if storeys == 1 else "architectural_clay_module_v1",
        placement_contract={"mode": "authored_storey_program", "storey_program_id": program},
    )


def request(**kwargs):
    return AssemblyRequest(target_width_m=10, target_depth_m=14, target_floors=2,
                           archetype_id="bungalow_postwar_ranch", model_revision="native-v1", **kwargs)


def test_pinned_native_revision_can_select_its_complete_authored_storey_assembly():
    plan = plan_vertical_assembly([house(1, "native-v1"), house(2, "two-storey-v1")], request(), allow_forced_fit=False)
    assert plan["instances"][0]["asset_id"] == "two-storey-v1"
    assert plan["assembled_height_m"] == pytest.approx(9.29)
    assert plan["instances"][0]["scale"][2] == 1


@pytest.mark.parametrize("changed", [
    {"family": "different-family"}, {"program": "different-program"},
    {"variant": "different-variant"},
])
def test_revision_program_does_not_admit_unrelated_assemblies(changed):
    with pytest.raises(AssemblyPlanningError):
        plan_vertical_assembly([house(1, "native-v1"), house(2, "other-v1", **changed)], request(), allow_forced_fit=False)


def test_fixed_revision_does_not_opt_into_an_assembly_programme():
    fixed = replace(house(1, "native-v1"), placement_contract=None)
    with pytest.raises(AssemblyPlanningError):
        plan_vertical_assembly([fixed, house(2, "two-storey-v1")], request(), allow_forced_fit=False)


def test_unknown_saved_revision_never_inherits_an_installed_programme():
    with pytest.raises(AssemblyPlanningError, match="not installed"):
        plan_vertical_assembly([house(1, "other-native-v1"), house(2, "two-storey-v1")], request(), allow_forced_fit=False)


def test_native_storeys_keep_the_exact_saved_revision_with_a_same_programme_replacement_installed():
    plan = plan_vertical_assembly([house(1, "new-native-v2"), house(1, "native-v1")],
                                  replace(request(), target_floors=1), allow_forced_fit=False)
    assert plan["instances"][0]["asset_id"] == "native-v1"


def test_content_hash_saved_revision_resolves_only_its_exact_native_programme_source():
    source = house(1, "native-v1")
    digest = "a" * 64
    bound = descriptor_from_library_entry(SimpleNamespace(id=source.id, name=source.name, model_url=source.model_url,
        metadata_={"rlasm": {"method_version": "6.1", "delivery_format": "architectural_clay", "runtime_enabled": True,
            "continuous_resize_allowed": False, "variant_id": source.source_variant_id, "candidate": source.model_revision,
            "model_sha256": digest}, "lego": {"enabled": True, "family": source.family, "role": "assembled",
            "width_m": 10, "depth_m": 14, "height_m": 6.36, "native_floors": 1, "min_floors": 1, "max_floors": 1,
            "repeatable_z": False, "source_variant_id": source.source_variant_id, "generation_archetype_id": source.source_variant_id,
            "archetype_ids": list(source.archetype_ids), "placement_contract": source.placement_contract}}))
    assert bound is not None
    plan = plan_vertical_assembly([bound, house(2, "two-storey-v1")], replace(request(), model_revision=digest), allow_forced_fit=False)
    assert plan["instances"][0]["asset_id"] == "two-storey-v1"
    with pytest.raises(AssemblyPlanningError, match="not installed"):
        plan_vertical_assembly([bound, house(2, "two-storey-v1")], replace(request(), model_revision="b" * 64), allow_forced_fit=False)
