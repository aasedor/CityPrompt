"""A source bridge's valid span may be shorter than its occupied width."""

import copy
import math
import uuid

import pytest
from fastapi import HTTPException
from geoalchemy2.shape import from_shape
from shapely.geometry import Polygon

from app.api.v1.lego_assembly import _public_realm_recipe_for_zone
from app.models.models import SiteZone
from app.services.native_modular_bridge import MODULAR_BRIDGE_IDENTITIES, modular_bridge_profile
from app.services.native_source_bridge import SOURCE_BRIDGE_LANES
from app.services.plan_geometry.generator import validate_street_plan_centerline_wgs84


def source(length=None, angle=0, variant="weathering_steel_v_footbridge_route_v1"):
    profile = modular_bridge_profile(variant)
    length = length or profile["program"]["minLengthM"] + 0.001
    width = profile["widthM"]
    sx = 111320 * math.cos(math.radians(51))

    def point(along, across=0):
        return [
            -114 + (along * math.cos(angle) - across * math.sin(angle)) / sx,
            51 + (along * math.sin(angle) + across * math.cos(angle)) / 111320,
        ]

    polygon = Polygon([point(0, -width / 2), point(length, -width / 2), point(length, width / 2), point(0, width / 2)])
    props = {
        "road_selected_variant_id": variant,
        "road_archetype_id": profile["sourceArchetypeId"],
        "width": width,
        "lane_count": SOURCE_BRIDGE_LANES.get(variant, 0),
        "plan_centerline": [point(0), point(length)],
        "plan_route_controls": [point(0), point(length)],
    }
    return polygon, props


@pytest.mark.parametrize("angle", [0, 0.7, math.pi / 2, math.pi])
def test_native_bridge_compiler_preserves_a_valid_shorter_than_width_authored_span(angle):
    polygon, props = source(angle=angle)
    before = copy.deepcopy(props)
    zone = SiteZone(id=uuid.uuid4(), zone_type="road", geometry=from_shape(polygon, srid=4326), properties=props)
    recipe = _public_realm_recipe_for_zone(zone, "street")
    assert recipe["variant_id"] == props["road_selected_variant_id"]
    assert recipe["target"]["row_width_m"] == 52
    assert recipe["target"]["length_m"] == pytest.approx(48.987, abs=0.002)
    assert zone.properties == before


@pytest.mark.parametrize("damage", ["shift", "width", "length", "bend", "missing", "nonfinite"])
def test_native_bridge_centerline_dispatch_rejects_stale_or_forged_geometry(damage):
    polygon, props = source()
    if damage == "shift":
        props["plan_centerline"] = [[x + 0.0001, y] for x, y in props["plan_centerline"]]
    elif damage == "width":
        props["width"] = 51
    elif damage == "length":
        props["plan_centerline"][1][0] += 0.001
    elif damage == "bend":
        props["plan_centerline"].insert(1, [-114.0001, 51.0001])
    elif damage == "missing":
        props.pop("plan_centerline")
    else:
        props["plan_centerline"][0][0] = math.nan
    assert not validate_street_plan_centerline_wgs84(polygon, props.get("plan_centerline"), properties=props)
    zone = SiteZone(id=uuid.uuid4(), zone_type="road", geometry=from_shape(polygon, srid=4326), properties=props)
    with pytest.raises(HTTPException) as exc:
        _public_realm_recipe_for_zone(zone, "street")
    assert exc.value.status_code == 422
    assert "public_realm_lego" not in zone.properties


@pytest.mark.parametrize("variant", list(MODULAR_BRIDGE_IDENTITIES))
@pytest.mark.parametrize("bound", ["minLengthM", "maxLengthM"])
@pytest.mark.parametrize("angle", [0, 0.7, math.pi / 2, math.pi])
def test_bridge_minimum_and_maximum_spans_compile_in_the_authored_metric_frame(variant, bound, angle):
    program = modular_bridge_profile(variant)["program"]
    length = program[bound] + (0.001 if bound == "minLengthM" else -0.001)
    polygon, props = source(length=length, angle=angle, variant=variant)
    zone = SiteZone(id=uuid.uuid4(), zone_type="road", geometry=from_shape(polygon, srid=4326), properties=props)
    recipe = _public_realm_recipe_for_zone(zone, "street")
    assert recipe["variant_id"] == variant
    assert recipe["target"]["length_m"] == pytest.approx(length, abs=0.001)
    assert zone.properties["plan_centerline"] == props["plan_centerline"]
