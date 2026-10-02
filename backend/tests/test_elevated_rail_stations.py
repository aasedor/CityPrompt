import json
import pytest

from app.services.elevated_rail import validate_rail_overlap
from app.services.native_specialist_streets import validate_specialist_properties
from app.services.native_street_candidate_contract import native_street_runtime_capabilities
from app.services.road_network import network_snapshot

VARIANTS={
    'skytrain_elevated_corridor_v0':'skytrain_elevated_corridor',
    'elevated_rail_transit_corridor_v0':'elevated_rail_transit_corridor',
}


def props(variant,stops=None):
    return dict(road_selected_variant_id=variant,road_archetype_id=VARIANTS[variant],width=26,
                plan_centerline=[[0,0],[0,160/111320]],road_native_stops=stops or [])


@pytest.mark.parametrize('variant',VARIANTS)
def test_station_lifecycle_and_complete_envelope_validation(variant):
    base=props(variant)
    for chosen in ([],[dict(id='a',stationM=40)],
                   [dict(id='a',stationM=100)],
                   [dict(id='a',stationM=40),dict(id='b',stationM=100)]):
        validate_specialist_properties({**base,'road_native_stops':chosen})
    for chosen in ([dict(id='a',stationM=23)],
                   [dict(id='a',stationM=137)],
                   [dict(id='a',stationM=40),dict(id='b',stationM=89)],
                   [dict(id='a',stationM=40),dict(id='a',stationM=100)],
                   [dict(id='a',stationM=float('nan'))]):
        with pytest.raises(ValueError):
            validate_specialist_properties({**base,'road_native_stops':chosen})
    with pytest.raises(ValueError,match='public road'):
        validate_specialist_properties({**base,'connect_to_public_road':True})


@pytest.mark.parametrize('variant',VARIANTS)
def test_station_rail_keeps_exact_native_identity_and_is_excluded_from_road_graph(variant):
    item=next(c for c in native_street_runtime_capabilities() if c.selections[0].variant_id==variant)
    assert item.selections[0].archetype_id==VARIANTS[variant]
    assert item.selections[0].compatibility.nominal_row_width_m==26
    assert not network_snapshot(json.dumps([dict(id='rail',properties={**props(variant),'procedural_road':1})]))['edges']
    rail=[[x/111320,y/111320] for x,y in [(-13,0),(13,0),(13,160),(-13,160)]]
    cross=[[x/111320,y/111320] for x,y in [(-30,75),(30,75),(30,85),(-30,85)]]
    with pytest.raises(ValueError,match='crossings'):
        validate_rail_overlap(cross,{},[(rail,props(variant))])
