"""Protect the actual stairs, end supports and deck from street collisions."""

import math
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock
import uuid

import pytest
from geoalchemy2.shape import from_shape
from shapely.geometry import Polygon

from app.api.v1.site_zones import _validate_elevated_rail_neighbours


BRIDGE = "timber_covered_bridge_route_v1"


def strip(x0, y0, x1, y1):
    return [[x / 111320, y / 111320] for x, y in [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]]


def bridge():
    return strip(-3, 0, 3, 80), {
        "road_selected_variant_id": BRIDGE,
        "road_archetype_id": "urban_pedestrian_footbridge",
        "width": 6,
        "lane_count": 0,
        "plan_centerline": [[0, 0], [0, 80 / 111320]],
    }


def crossing(station, *, kind="road"):
    if kind == "bridge":
        properties = {
            **bridge()[1],
            "plan_centerline": [[-40 / 111320, station / 111320], [40 / 111320, station / 111320]],
        }
        width = 6
    elif kind == "path":
        width = 1.8
        properties = {
            "road_selected_variant_id": "concrete_neighbourhood_walk_v1",
            "road_archetype_id": "campus_pedestrian_spine",
            "width": width,
            "lane_count": 0,
            "plan_centerline": [[-40 / 111320, station / 111320], [40 / 111320, station / 111320]],
        }
    elif kind == "landmark":
        width = 36
        properties = {"road_selected_variant_id": "landmark_signature_bridge_v2", "lane_count": 0}
    else:
        width = 16
        properties = {"road_archetype_id": "calgary_local", "width": width, "lane_count": 2}
    return strip(-40, station - width / 2, 40, station + width / 2), properties


def saved_zone(source, zone_type="road"):
    coordinates, properties = source
    return SimpleNamespace(
        id=uuid.uuid4(),
        zone_type=zone_type,
        geometry=from_shape(Polygon(coordinates), srid=4326),
        properties=properties,
    )


async def check_neighbours(candidate, other, *, candidate_type="road", neighbour_type="road"):
    result = MagicMock()
    result.scalars.return_value.all.return_value = [saved_zone(other, neighbour_type)]
    database = AsyncMock()
    database.execute.return_value = result
    await _validate_elevated_rail_neighbours(
        database, uuid.uuid4(), candidate[0], candidate[1], zone_type=candidate_type
    )


@pytest.mark.parametrize("reverse", [False, True])
@pytest.mark.parametrize(
    "other",
    [
        crossing(40, kind="bridge"),
        crossing(3),
        crossing(40),
        crossing(40, kind="landmark"),
        crossing(14.5, kind="path"),
        crossing(15.6, kind="path"),
    ],
)
async def test_saved_bridge_rejects_full_structure_collisions_in_both_edit_directions(other, reverse):
    candidate, neighbour = (other, bridge()) if reverse else (bridge(), other)
    with pytest.raises(ValueError, match="bridge"):
        await check_neighbours(candidate, neighbour)


@pytest.mark.parametrize("reverse", [False, True])
@pytest.mark.parametrize(
    "other",
    [crossing(40, kind="path"), crossing(15.7, kind="path"), (strip(-8, -20, 8, 0), {}), (strip(3, 0, 8, 80), {})],
)
async def test_saved_bridge_retains_ground_endpoint_touches_and_clear_path_underpasses(other, reverse):
    candidate, neighbour = (other, bridge()) if reverse else (bridge(), other)
    await check_neighbours(candidate, neighbour)


def transform(source, *, reverse=False):
    coordinates, properties = source
    lng, lat = -114.04, 51.04
    sx = 111320 * math.cos(math.radians(lat))
    angle = math.pi / 5

    def rotate(point):
        x, y = point[0] * 111320, point[1] * 111320
        return [
            lng + (x * math.cos(angle) - y * math.sin(angle)) / sx,
            lat + (x * math.sin(angle) + y * math.cos(angle)) / 111320,
        ]

    transformed = dict(properties)
    if "plan_centerline" in properties:
        transformed["plan_centerline"] = [rotate(point) for point in properties["plan_centerline"]]
        if reverse:
            transformed["plan_centerline"].reverse()
    return [rotate(point) for point in coordinates], transformed


@pytest.mark.parametrize("reverse", [False, True])
async def test_oblique_reversed_bridge_uses_its_full_width_end_reservations(reverse):
    source = transform(bridge(), reverse=reverse)
    with pytest.raises(ValueError, match="bridge"):
        await check_neighbours(source, transform(crossing(14.5, kind="path")))
    await check_neighbours(source, transform(crossing(40, kind="path")))


@pytest.mark.parametrize("candidate_type", ["road", "street", "path"])
async def test_path_zone_types_cannot_bypass_the_bridge_support_guard(candidate_type):
    with pytest.raises(ValueError, match="bridge"):
        await check_neighbours(crossing(3, kind="path"), bridge(), candidate_type=candidate_type)
    await check_neighbours(crossing(40, kind="path"), bridge(), candidate_type=candidate_type)


@pytest.mark.parametrize(
    "changes",
    [
        {"road_selected_variant_id": "calgary_local_v0"},
        {"lane_count": False},
        {"width": 2},
        {"road_archetype_id": "calgary_local"},
    ],
)
async def test_only_exact_native_surface_paths_receive_the_underpass_exception(changes):
    coordinates, properties = crossing(40, kind="path")
    with pytest.raises(ValueError):
        await check_neighbours((coordinates, {**properties, **changes}), bridge())


async def test_bridge_clearance_rejects_non_array_route_metadata_without_server_error():
    coordinates, properties = bridge()
    with pytest.raises(ValueError):
        await check_neighbours(
            (coordinates, {**properties, "plan_centerline": "[[0,0],[0,0.00071865]]"}), crossing(40, kind="path")
        )


async def test_stale_bridge_polygon_cannot_hide_a_collision_behind_its_previous_route():
    stale = strip(-3, 100, 3, 180), bridge()[1]
    with pytest.raises(ValueError, match="bridge"):
        await check_neighbours(stale, crossing(140))
    with pytest.raises(ValueError, match="bridge"):
        await check_neighbours(crossing(140), stale)


async def test_neighbour_query_uses_only_the_persisted_road_enum():
    from sqlalchemy import Enum
    from sqlalchemy.dialects import postgresql
    from app.models.models import SiteZone

    enum = SiteZone.__table__.c.zone_type.type
    strict_enum = Enum(*enum.enums, name=enum.name, validate_strings=True)
    validate_bound_enum = strict_enum.bind_processor(postgresql.dialect())
    selected_types = set()
    project_id = uuid.uuid4()
    result = MagicMock()
    result.scalars.return_value.all.return_value = []

    async def execute(statement):
        compiled = statement.compile(dialect=postgresql.dialect())
        assert project_id in compiled.params.values()
        for parameter in compiled.binds.values():
            if getattr(parameter.type, "name", None) != "zone_type":
                continue
            values = parameter.value if parameter.expanding else [parameter.value]
            selected_types.update(validate_bound_enum(value) for value in values)
        return result

    database = SimpleNamespace(execute=execute)
    coordinates, properties = bridge()
    await _validate_elevated_rail_neighbours(database, project_id, coordinates, properties)
    assert selected_types == {"road"}
