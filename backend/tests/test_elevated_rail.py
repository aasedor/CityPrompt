import json
import pytest
from app.services.elevated_rail import VARIANT, validate_rail_overlap
from app.services.native_specialist_streets import validate_specialist_properties
from app.services.native_street_candidate_contract import native_street_runtime_capabilities
from app.services.road_network import network_snapshot


def rectangle(x0, y0, x1, y1):
    return [[x / 111320, y / 111320] for x, y in [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]]


def test_complete_corridor_is_protected_in_both_edit_directions():
    rail = rectangle(-13, 0, 13, 100)
    cross = rectangle(-50, 46, 50, 54)
    props = {"road_selected_variant_id": VARIANT}
    with pytest.raises(ValueError, match="crossings"):
        validate_rail_overlap(rail, props, [(cross, {})])
    with pytest.raises(ValueError, match="crossings"):
        validate_rail_overlap(cross, {}, [(rail, props)])
    validate_rail_overlap(rectangle(13, 0, 20, 100), {}, [(rail, props)])
    validate_rail_overlap(rectangle(-4, -40, 4, 0), {}, [(rail, props)])


def test_no_ordinary_road_graph_or_public_road_connection():
    props = dict(
        road_selected_variant_id=VARIANT,
        road_archetype_id="elevated_garden_rail",
        width=26,
        plan_centerline=[[0, 0], [0, 80 / 111320]],
        procedural_road=1,
    )
    assert not network_snapshot(json.dumps([dict(id="rail", properties=props)]))["edges"]
    validate_specialist_properties(props)
    with pytest.raises(ValueError, match="public road"):
        validate_specialist_properties({**props, "connect_to_public_road": True})


def test_exact_native_runtime_capability_is_available():
    item = next(c for c in native_street_runtime_capabilities() if c.selections[0].variant_id == VARIANT)
    selected = item.selections[0]
    assert selected.archetype_id == "elevated_garden_rail"
    assert selected.compatibility.nominal_row_width_m == 26
    assert selected.compatibility.min_length_m == 48
    assert selected.compatibility.max_length_m == 288
