"""Detached blocks keep native house geometry, gaps and true polygon containment."""

from dataclasses import replace
from types import SimpleNamespace

import pytest
from geoalchemy2.shape import from_shape
from shapely.affinity import rotate, translate
from shapely.geometry import Polygon, box

from app.api.v1.lego_assembly import _strict_locked_building_plan
from app.services.lego_assembly import (
    AssemblyPlanningError,
    AssemblyRequest,
    DETACHED_ARCHETYPE_IDS,
    ModuleDescriptor,
    detached_plot_local_coordinates,
    plan_vertical_assembly,
)
from app.services.plan_geometry.archetypes import load_dims_table


def modules(archetype="detached_contemporary_infill"):
    return [
        ModuleDescriptor(
            id=role,
            name=role,
            model_url=f"/families/local-fixture/{role}.glb",
            family=archetype.replace("_", "-"),
            role=role,
            width_m=10,
            depth_m=12,
            height_m=height,
            archetype_ids=(archetype,),
            reuse_keys=(),
            min_floors=1,
            max_floors=3,
            repeatable_z=role == "floor",
        )
        for role, height in (("podium", 3), ("floor", 3), ("roof", 2))
    ]


def request(plot, *, width=200, depth=80, profile="rectangle"):
    return AssemblyRequest(
        target_width_m=width,
        target_depth_m=depth,
        target_floors=2,
        archetype_id="detached_contemporary_infill",
        footprint_profile=profile,
        footprint_local_m=tuple(plot.exterior.coords),
    )


def dwelling_footprints(plan):
    return [
        translate(
            rotate(
                box(-s["length_m"] / 2, -s["thickness_m"] / 2, s["length_m"] / 2, s["thickness_m"] / 2),
                s["rotation_degrees"],
                origin=(0, 0),
            ),
            s["centre_x_m"],
            s["centre_y_m"],
        )
        for s in plan["footprint_segments"]
    ]


@pytest.mark.parametrize(
    "plot",
    [
        box(-100, -20, 100, 20),
        box(-20, -100, 20, 100),
        rotate(box(-100, -20, 100, 20), 27, origin=(0, 0)),
        Polygon([(-100, -60), (100, -60), (100, -20), (-30, -20), (-30, 60), (-100, 60)]),
    ],
)
def test_wide_long_rotated_concave_housing_plots_keep_many_native_houses(plot):
    req = request(plot)
    plan = plan_vertical_assembly(modules(), req)
    assert plan == plan_vertical_assembly(modules(), req)
    assert plan["fit"]["dwelling_count"] > 8
    assert plan["fit"]["placement_mode"] == "detached_lots"
    assert all(instance["scale"] == [1, 1, 1] for instance in plan["instances"])
    assert plan["assembled_height_m"] == 8
    footprints = dwelling_footprints(plan)
    assert all(plot.buffer(1e-6).covers(footprint) for footprint in footprints)
    for i, house in enumerate(footprints):
        for other in footprints[i + 1 :]:
            assert house.distance(other) >= 3 - 1e-6
    assert len({item["segment_id"] for item in plan["instances"]}) == len(footprints)
    assert len(plan["instances"]) == len(footprints) * 3


def test_native_house_parcel_remains_one_house_without_stretch():
    plan = plan_vertical_assembly(modules(), request(box(-5, -6, 5, 6), width=10, depth=12))
    assert plan["fit"]["dwelling_count"] == 1
    assert all(instance["scale"] == [1, 1, 1] for instance in plan["instances"])
    assert plan["fit"]["setback_compliance"] == "not_assessed"


def test_block_long_strip_at_native_house_depth_still_repeats_with_gaps():
    plan = plan_vertical_assembly(modules(), request(box(-100, -6, 100, 6), width=200, depth=12))
    assert plan["fit"]["dwelling_count"] > 8
    footprints = dwelling_footprints(plan)
    assert all(box(-100, -6, 100, 6).buffer(1e-6).covers(house) for house in footprints)
    assert all(instance["scale"] == [1, 1, 1] for instance in plan["instances"])


@pytest.mark.parametrize("forced", [False, True])
def test_too_small_detached_plot_fails_even_in_forced_mode(forced):
    with pytest.raises(AssemblyPlanningError, match="No native-size"):
        plan_vertical_assembly(modules(), request(box(-2, -2, 2, 2)), allow_forced_fit=forced)


def test_detached_floor_range_cannot_make_a_tower():
    with pytest.raises(AssemblyPlanningError, match="cannot be stretched into towers"):
        plan_vertical_assembly(modules(), replace(request(box(-100, -40, 100, 40)), target_floors=30))


def test_detached_family_catalogue_set_excludes_attached_and_landmark_types():
    by_id = {entry["id"]: entry for entry in load_dims_table()}
    assert all(by_id[key]["development_type"] == "residential_single_family" for key in DETACHED_ARCHETYPE_IDS)
    assert "amsterdam_bell_gable_house" not in DETACHED_ARCHETYPE_IDS
    assert "farnsworth_house_glass_pavilion" not in DETACHED_ARCHETYPE_IDS
    assert "glass_tower_modern" not in DETACHED_ARCHETYPE_IDS


def test_shaped_detached_request_requires_actual_ring_and_rejects_invalid_geometry():
    with pytest.raises(AssemblyPlanningError, match="actual polygon"):
        plan_vertical_assembly(
            modules(), replace(request(box(-100, -40, 100, 40)), footprint_local_m=None, footprint_profile="l_shape")
        )
    with pytest.raises(AssemblyPlanningError, match="non-self-intersecting"):
        plan_vertical_assembly(
            modules(), replace(request(box(-100, -40, 100, 40)), footprint_local_m=((0, 0), (20, 20), (0, 20), (20, 0)))
        )


def test_grid_work_and_dwelling_count_are_bounded():
    with pytest.raises(AssemblyPlanningError, match="maximum 256"):
        plan_vertical_assembly(modules(), request(box(-1000, -1000, 1000, 1000)))


def test_exact_variant_uses_only_its_own_or_declared_parent_family():
    plan = plan_vertical_assembly(
        modules(), replace(request(box(-100, -40, 100, 40)), archetype_id="detached_infill_glass_box")
    )
    assert plan["archetype_id"] == "detached_infill_glass_box"
    assert plan["family"] == "detached-contemporary-infill"


def test_other_archetypes_retain_existing_vertical_assembly():
    tower_modules = [replace(m, max_floors=50) for m in modules("glass_tower_modern")]
    plan = plan_vertical_assembly(
        tower_modules,
        AssemblyRequest(target_width_m=10, target_depth_m=12, target_floors=30, archetype_id="glass_tower_modern"),
    )
    assert plan["target"]["floors"] == 30
    assert plan["fit"].get("placement_mode") is None
    assert len(plan["instances"]) == 31


def test_native_plot_frame_matches_globe_y_reflection_and_zone_certification():
    import math

    metres_per_lng = 111_320 * math.cos(math.radians(51))
    geo_ring = [
        (-114 + x / metres_per_lng, 51 + y / 111_320) for x, y in [(-100, -40), (100, -40), (100, 40), (-100, 40)]
    ]
    ring = detached_plot_local_coordinates(geo_ring, 200, 80)
    assert ring == ((-100, 40), (100, 40), (100, -40), (-100, -40))
    zone = SimpleNamespace(geometry=from_shape(Polygon(geo_ring), srid=4326))
    expected = plan_vertical_assembly(
        modules(),
        AssemblyRequest(
            target_width_m=200,
            target_depth_m=80,
            target_floors=2,
            archetype_id="detached_contemporary_infill",
            allow_setback=False,
            footprint_local_m=ring,
        ),
    )
    actual = _strict_locked_building_plan(
        modules(), "detached_contemporary_infill", (200, 80, 2, "rectangle", None), {}, zone=zone
    )
    assert actual == expected
