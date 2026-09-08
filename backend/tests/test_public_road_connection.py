import pytest
from shapely.geometry import LineString, box
from app.services.public_road_connection import public_road_connection_fits


def fixture(end=110, enabled=True):
    line = [[10 / 111320, 50 / 111320], [end / 111320, 50 / 111320]]
    return {"connect_to_public_road": enabled, "width": 20, "plan_centerline": line}, LineString(line).buffer(
        10 / 111320, cap_style=2
    )


def test_public_connection_keeps_parcel_and_cross_section():
    props, polygon = fixture()
    assert public_road_connection_fits("road", props, polygon, box(0, 0, 100 / 111320, 100 / 111320))


@pytest.mark.parametrize("change", ["disabled", "building", "far", "two_ends", "too_wide", "reentry"])
def test_public_connection_does_not_bypass_other_site_constraints(change):
    props, polygon = fixture(140 if change == "far" else 110, change != "disabled")
    if change == "two_ends":
        props["plan_centerline"][0] = [-10 / 111320, 50 / 111320]
    if change == "too_wide":
        polygon = polygon.buffer(5 / 111320)
    if change == "reentry":
        props["plan_centerline"] = [
            [10 / 111320, 50 / 111320],
            [110 / 111320, 50 / 111320],
            [20 / 111320, 50 / 111320],
            [110 / 111320, 50 / 111320],
        ]
    assert not public_road_connection_fits(
        "building" if change == "building" else "road", props, polygon, box(0, 0, 100 / 111320, 100 / 111320)
    )
