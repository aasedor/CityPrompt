"""Street context — the plan must meet the real streets around it.

Three defects reproduced before these tests existed, all of which read to a
planner as "the roads are nonsensical and ignore what is there":

1. Anchor search was a hard cliff at 32 m. A centreline 31 m outside the parcel
   gave four gateways; 33 m gave none, and the plan drew an internal grid
   connected to nothing.
2. That total failure was SILENT — CONTEXT_ENTRIES_UNSERVED only fires when
   anchors exist but cannot be served.
3. Vehicle gateways were capped at a flat four regardless of site size.
"""

import math

from shapely.geometry import LineString, Polygon, mapping

from app.services.plan_geometry.community_rules import resolve_rules
from app.services.plan_geometry.generator import generate_plan_geometry
from app.services.plan_geometry.street_graph import (
    ROAD_ENTRY_LIMIT_MAX,
    ROAD_ENTRY_LIMIT_MIN,
    ROAD_FRONTAGE_BANDS_M,
    ROAD_FRONTAGE_PROXIMITY_M,
    generate_street_network,
    road_entry_anchors,
    road_entry_limit,
)

LAT, LON = 51.0450, -114.0700
M_LAT = 111_320.0
M_LON = M_LAT * math.cos(math.radians(LAT))
W, H = 400.0, 300.0

PARAMS = {"buildings.floors": {"value": 4}, "streets.row_width_m": {"value": 18.0}}


def _wgs(x: float, y: float) -> tuple[float, float]:
    return (LON + x / M_LON, LAT + y / M_LAT)


def _site_wgs() -> Polygon:
    return Polygon([_wgs(0, 0), _wgs(W, 0), _wgs(W, H), _wgs(0, H)])


def _site_metric() -> Polygon:
    return Polygon([(0, 0), (W, 0), (W, H), (0, H)])


def _ring_roads_metric(offset_m: float) -> list[LineString]:
    """A street on each of the four sides, ``offset_m`` outside the parcel."""
    return [
        LineString([(-60, -offset_m), (W + 60, -offset_m)]),
        LineString([(-60, H + offset_m), (W + 60, H + offset_m)]),
        LineString([(-offset_m, -60), (-offset_m, H + 60)]),
        LineString([(W + offset_m, -60), (W + offset_m, H + 60)]),
    ]


def _as_features(lines: list[LineString]) -> list[dict]:
    return [
        {
            "geometry": mapping(LineString([_wgs(x, y) for x, y in line.coords])),
            "properties": {"name": "Context Ave", "type": "Residential"},
        }
        for line in lines
    ]


def _plan(road_features: list[dict]):
    return generate_plan_geometry(
        site_polygon_wgs84=_site_wgs(),
        scenario_id="city_policy",
        scenario_label="street context",
        parameters=PARAMS,
        road_features=road_features,
        path_features=[],
        district_features=[],
    )


def _codes(result) -> set[str]:
    return {note.get("code") for note in result.notes}


def _context_connections(result) -> int:
    return sum(1 for zone in result.zones if zone["properties"].get("context_connection"))


# ---------------------------------------------------------------------------
# The proximity cliff
# ---------------------------------------------------------------------------


def test_anchors_survive_a_setback_beyond_the_preferred_band():
    """A parcel boundary routinely sits well back from the centreline — a wide
    arterial ROW, a boulevard median, a survey line behind the curb."""
    site = _site_metric()
    for offset in (5, 25, 31, 33, 40, 60, 100):
        anchors, band = road_entry_anchors(_ring_roads_metric(offset), site)
        assert anchors, f"no gateways at a {offset} m setback"
        assert band is not None


def test_widening_is_reported_not_hidden():
    """Anchoring further out changes the plan's edge condition, so it is
    disclosed rather than silently absorbed."""
    site = _site_metric()
    _, near_band = road_entry_anchors(_ring_roads_metric(15), site)
    _, far_band = road_entry_anchors(_ring_roads_metric(50), site)
    assert near_band == ROAD_FRONTAGE_PROXIMITY_M
    assert far_band is not None and far_band > ROAD_FRONTAGE_PROXIMITY_M

    result = _plan(_as_features(_ring_roads_metric(50)))
    assert "ROAD_CONTEXT_BAND_WIDENED" in _codes(result)


def test_a_setback_site_actually_connects():
    """The regression that started this: four real streets around the site and
    zero connections to any of them."""
    result = _plan(_as_features(_ring_roads_metric(40)))
    assert _context_connections(result) > 0
    assert "CONTEXT_CONNECTIONS_APPLIED" in _codes(result)


# ---------------------------------------------------------------------------
# Silent failure
# ---------------------------------------------------------------------------


def test_missing_road_context_is_warned_about():
    result = _plan([])
    assert "NO_ROAD_CONTEXT" in _codes(result)
    assert _context_connections(result) == 0


def test_unreachable_road_context_is_warned_about():
    """Roads exist but every one is far outside even the widest band."""
    far = [LineString([(-4000, -3000), (4000, -3000)])]
    result = _plan(_as_features(far))
    assert "ROAD_CONTEXT_UNREACHABLE" in _codes(result)


def test_a_well_connected_plan_raises_none_of_those_warnings():
    """The false-positive guard: normal context must stay quiet."""
    result = _plan(_as_features(_ring_roads_metric(12)))
    assert not ({"NO_ROAD_CONTEXT", "ROAD_CONTEXT_UNREACHABLE", "ROAD_CONTEXT_BAND_WIDENED"} & _codes(result))


# ---------------------------------------------------------------------------
# Gateway count
# ---------------------------------------------------------------------------


def test_gateway_count_scales_with_site_perimeter():
    small = Polygon([(0, 0), (80, 0), (80, 60), (0, 60)])
    large = Polygon([(0, 0), (1200, 0), (1200, 900), (0, 900)])
    assert road_entry_limit(small) == ROAD_ENTRY_LIMIT_MIN
    assert road_entry_limit(large) == ROAD_ENTRY_LIMIT_MAX
    assert ROAD_ENTRY_LIMIT_MIN <= road_entry_limit(_site_metric()) <= ROAD_ENTRY_LIMIT_MAX


def test_a_district_uses_more_than_four_gateways():
    """Ten real streets around a district previously produced four connections
    and ignored the rest."""
    site = Polygon([(0, 0), (900, 0), (900, 700), (0, 700)])
    roads = []
    for i in range(1, 5):
        roads.append(LineString([(-60, i * 140), (960, i * 140)]))
        roads.append(LineString([(i * 180, -60), (i * 180, 760)]))
    anchors, _ = road_entry_anchors(roads, site)
    assert len(anchors) > ROAD_ENTRY_LIMIT_MIN


# ---------------------------------------------------------------------------
# Orientation
# ---------------------------------------------------------------------------


def test_inconclusive_orientation_is_reported():
    """Falling back to the site rectangle is correct for mixed context; doing
    it silently makes the plan look like it ignored the neighbourhood."""
    rules, _ = resolve_rules("city_policy", PARAMS)
    scattered = [
        LineString([(-500, -200), (500, 260)]),
        LineString([(-460, 400), (520, -120)]),
        LineString([(-300, -300), (-280, 700)]),
    ]
    network = generate_street_network(_site_metric(), rules, [], context_road_lines=scattered)
    codes = {note.get("code") for note in network.notes}
    assert "CONTEXT_GRID_ORIENTATION_INCONCLUSIVE" in codes
    assert network.grid_orientation_source == "site_boundary_context_inconclusive"


def test_coherent_context_still_rotates_the_grid():
    rules, _ = resolve_rules("city_policy", PARAMS)
    angle = math.radians(30.0)
    rotated = []
    for i in range(-4, 5):
        for x1, y1, x2, y2 in (
            (-900, i * 130, 900, i * 130),
            (i * 130, -900, i * 130, 900),
        ):
            rotated.append(
                LineString(
                    [
                        (
                            x1 * math.cos(angle) - y1 * math.sin(angle) + W / 2,
                            x1 * math.sin(angle) + y1 * math.cos(angle) + H / 2,
                        ),
                        (
                            x2 * math.cos(angle) - y2 * math.sin(angle) + W / 2,
                            x2 * math.sin(angle) + y2 * math.cos(angle) + H / 2,
                        ),
                    ]
                )
            )
    network = generate_street_network(_site_metric(), rules, [], context_road_lines=rotated)
    assert network.grid_orientation_source == "surrounding_street_grid"
    assert abs(network.grid_angle_deg) > 2.0


def test_bands_are_ordered_widest_last():
    assert list(ROAD_FRONTAGE_BANDS_M) == sorted(ROAD_FRONTAGE_BANDS_M)
    assert ROAD_FRONTAGE_BANDS_M[0] == ROAD_FRONTAGE_PROXIMITY_M
