import math
from types import SimpleNamespace

import pytest
from geoalchemy2.shape import from_shape
from shapely.geometry import Polygon, box

from app.api.v1.lego_assembly import _locked_building_target, _strict_locked_building_plan
from app.services.lego_assembly import (
    AssemblyPlanningError,
    descriptor_from_library_entry,
    detached_plot_local_coordinates,
)
from app.services.residual_landscape import community_3d_source_hash
from tests.test_clay_runtime import clay_entry, plan
from tests.test_detached_assembly import dwelling_footprints


def test_explicit_home_plot_repeats_whole_exact_houses_with_gaps():
    actual = plan(native_home_plot=True, target_width_m=60, target_depth_m=30)
    shapes = dwelling_footprints(actual)
    assert len(shapes) > 1
    assert all(box(-30, -15, 30, 15).covers(shape) for shape in shapes)
    assert all(a.distance(b) >= 3 - 1e-6 for i, a in enumerate(shapes) for b in shapes[i + 1 :])
    assert all(item["scale"] == [1, 1, 1] and item["native_dimensions_m"] == [10, 8, 7] for item in actual["instances"])
    assert all(item["asset_id"] == "clay" for item in actual["instances"])
    assert actual["fit"]["dwelling_count"] == len(shapes)


def test_foursquare_home_plot_repeats_exact_variant_without_stretching():
    actual = plan(
        clay_entry("toronto_edwardian_foursquare", "toronto_foursquare_red_brick"),
        archetype_id="toronto_foursquare_red_brick",
        native_home_plot=True,
        target_width_m=30,
        target_depth_m=22,
    )
    shapes = dwelling_footprints(actual)
    assert len(shapes) == 2
    assert all(box(-15, -11, 15, 11).covers(shape) for shape in shapes)
    assert shapes[0].distance(shapes[1]) >= 3 - 1e-6
    assert all(item["scale"] == [1, 1, 1] and item["asset_id"] == "clay" for item in actual["instances"])


def test_home_plot_is_opt_in_and_never_repeats_landmarks_or_invents_variant():
    assert len(plan(target_width_m=60, target_depth_m=30)["instances"]) == 1
    with pytest.raises(AssemblyPlanningError):
        plan(native_home_plot=True, archetype_id="calgary_modern_infill_house")
    with pytest.raises(AssemblyPlanningError, match="Only detached-home"):
        plan(
            clay_entry("amsterdam_brown_cafe", "brown_cafe_corner"),
            native_home_plot=True,
            archetype_id="brown_cafe_corner",
        )
    with pytest.raises(AssemblyPlanningError):
        plan(native_home_plot=True, target_floors=3)


def test_server_replay_uses_persisted_home_plot_setting():
    geometry = box(-114.001, 51.001, -114.0002, 51.0013)
    props = {"development_selected_variant_id": "infill_flat_roof_minimal", "floors": 2, "native_home_plot": True}
    zone = SimpleNamespace(geometry=from_shape(geometry, srid=4326), properties=props)
    actual = _strict_locked_building_plan(
        [descriptor_from_library_entry(clay_entry())],
        "infill_flat_roof_minimal",
        (56, 33, 2, "rectangle", None),
        props,
        zone=zone,
    )
    assert actual["fit"]["dwelling_count"] > 1
    assert community_3d_source_hash("building", geometry, props) != community_3d_source_hash(
        "building", geometry, {**props, "native_home_plot": False}
    )
    assert community_3d_source_hash(
        "building", geometry, {**props, "native_home_plot": False}
    ) == community_3d_source_hash("building", geometry, {k: v for k, v in props.items() if k != "native_home_plot"})


@pytest.mark.parametrize("width", [12, 16, 36])
@pytest.mark.parametrize("degrees", [0, 15, 90, 135, 180, 270])
def test_home_frontage_survives_resize_rotation_and_server_replay(width, degrees):
    angle = math.radians(degrees)
    ring = [
        (
            -114 + (x * math.cos(angle) - y * math.sin(angle)) / (111320 * math.cos(math.radians(51))),
            51 + (x * math.sin(angle) + y * math.cos(angle)) / 111320,
        )
        for x, y in [(-width / 2, -8), (width / 2, -8), (width / 2, 8), (-width / 2, 8)]
    ]
    zone = SimpleNamespace(
        geometry=from_shape(Polygon(ring), srid=4326), properties={"native_home_plot": True, "floors": 2}
    )
    assert _locked_building_target(zone)[:3] == (width, 16, 2)
    local = detached_plot_local_coordinates(ring, width, 16, preserve_authored_axes=True)
    assert local[0] == pytest.approx((-width / 2, 8), abs=1e-5)
    assert local[1] == pytest.approx((width / 2, 8), abs=1e-5)


@pytest.mark.parametrize('degrees', [25, 115, 205, 295])
def test_fixed_landmark_axes_survive_server_replay_without_repeating_homes(degrees):
    angle=math.radians(degrees)
    ring=[(-114+(x*math.cos(angle)-y*math.sin(angle))/(111320*math.cos(math.radians(51))),
           51+(x*math.sin(angle)+y*math.cos(angle))/111320) for x,y in [(-7,-10),(7,-10),(7,10),(-7,10)]]
    props={'native_plot_axes':True,'floors':2,'development_selected_variant_id':'brown_cafe_corner'}
    zone=SimpleNamespace(geometry=from_shape(Polygon(ring),srid=4326),properties=props)
    target=_locked_building_target(zone)
    assert target[:3] == (14,20,2)
    result=_strict_locked_building_plan([descriptor_from_library_entry(clay_entry('amsterdam_brown_cafe','brown_cafe_corner'))],
                                      'brown_cafe_corner',target,props,zone=zone)
    assert len(result['instances']) == 1
    assert result['instances'][0]['scale'] == [1,1,1]
    # The fixture is wider than deep, so its local fit turns 90 degrees. That
    # local fit must stay identical while the authored world heading changes.
    assert result['instances'][0]['rotation_degrees'] == 90


def test_half_turn_of_identical_native_plot_invalidates_source_hash():
    ring=[(-114,51),(-113.9998,51),(-113.9998,51.0003),(-114,51.0003)]
    original=Polygon(ring);flipped=Polygon(ring[2:]+ring[:2])
    assert original.equals(flipped)
    for flag in ('native_home_plot','native_plot_axes'):
        props={flag:True,'floors':2}
        assert community_3d_source_hash('building',original,props) != community_3d_source_hash('building',flipped,props)
    assert community_3d_source_hash('building',original,{}) == community_3d_source_hash('building',flipped,{})
