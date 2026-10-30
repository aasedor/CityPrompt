import pytest
from shapely.geometry import Polygon
from app.services.native_brt import validate_brt_properties, validate_brt_ground, VARIANT
from app.services.residual_landscape import community_3d_source_hash


def props(stops=None, length=100):
    return dict(
        road_selected_variant_id=VARIANT,
        road_archetype_id="brt_bus_rapid_transit_corridor",
        plan_centerline=[[0, 0], [0, length / 111320]],
        width=40,
        road_native_stops=stops or [],
    )


def test_manual_stops_and_empty_corridor():
    validate_brt_properties(props())
    validate_brt_properties(props([dict(id="one", stationM=32)]))
    validate_brt_properties(props([dict(id="one", stationM=32), dict(id="two", stationM=140)], 200))


def test_prepared_site_and_trusted_metric_identity():
    validate_brt_ground(props(), dict(community_3d_mask_existing_tiles=True))
    for boundary in (None, {}, dict(terrain_strategy="landscape", community_3d_mask_existing_tiles=True)):
        with pytest.raises(ValueError, match="prepared"):
            validate_brt_ground(props(), boundary)
    with pytest.raises(ValueError, match="40 m"):
        validate_brt_properties({**props(), "width": 12})


@pytest.mark.parametrize(
    "stops",
    [
        [dict(id="end", stationM=20)],
        [dict(id="end", stationM=70)],
        [dict(id="one", stationM=32), dict(id="two", stationM=60)],
        [dict(id="one", stationM=True)],
        [dict(id="one", stationM=float("nan"))],
        [dict(id="one", stationM=32, url="untrusted.glb")],
        [dict(id="one", stationM=32), dict(id="one", stationM=140)],
    ],
)
def test_rejects_invalid_stop_edits(stops):
    with pytest.raises(ValueError):
        validate_brt_properties(props(stops))


def test_straight_only_and_preserved_fixture():
    candidate = props()
    candidate["plan_centerline"].insert(1, [10 / 111320, 50 / 111320])
    with pytest.raises(ValueError, match="straight"):
        validate_brt_properties(candidate)
    validate_brt_properties(dict(road_selected_variant_id=VARIANT, validation_fixed_fixture=True))


def test_stop_move_changes_scene_source_hash():
    coordinates = Polygon([[-0.0002, 0], [0.0002, 0], [0.0002, 0.001], [-0.0002, 0.001]])
    before = community_3d_source_hash("road", coordinates, props([dict(id="one", stationM=32)]))
    after = community_3d_source_hash("road", coordinates, props([dict(id="one", stationM=45)]))
    assert before != after
