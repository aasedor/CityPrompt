import pytest
from app.services.native_tram import VARIANT, validate_tram_properties, validate_tram_ground


def props(length=144, stops=None):
    return dict(
        road_selected_variant_id=VARIANT,
        road_archetype_id="light_rail_tram_avenue",
        width=22,
        plan_centerline=[[0, 0], [0, length / 111320]],
        road_native_stops=stops or [],
    )


def test_manual_stops_and_empty_route_station_inventory():
    validate_tram_properties(props())
    validate_tram_properties(props(stops=[dict(id="one", stationM=15), dict(id="two", stationM=129)]))
    validate_tram_ground(props(), dict(terrain_strategy="platform", community_3d_mask_existing_tiles=True))


@pytest.mark.parametrize(
    "stops",
    [
        [dict(id="one", stationM=14)],
        [dict(id="one", stationM=130)],
        [dict(id="one", stationM=40), dict(id="two", stationM=60)],
        [dict(id="one", stationM=40), dict(id="one", stationM=90)],
        [dict(id="one", stationM=True)],
        [dict(id="one", stationM=40, url="untrusted.glb")],
    ],
)
def test_invalid_stop_does_not_become_a_partial_platform(stops):
    with pytest.raises(ValueError):
        validate_tram_properties(props(stops=stops))


def test_bend_reversal_wrong_identity_and_unprepared_site():
    p = props()
    p["plan_centerline"].insert(1, [0.001, 0.0005])
    with pytest.raises(ValueError, match="straight"):
        validate_tram_properties(p)
    p = props()
    p["width"] = 24
    with pytest.raises(ValueError, match="22 m"):
        validate_tram_properties(p)
    with pytest.raises(ValueError, match="prepared"):
        validate_tram_ground(props(), {})


def test_old_street_instances_unchanged():
    validate_tram_properties({"road_selected_variant_id": "brt_bus_rapid_transit_corridor_v0"})
    validate_tram_ground({"road_selected_variant_id": "unrelated"}, None)
