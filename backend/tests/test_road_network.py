"""Metric topology and surface regressions for the interactive road engine."""

from dataclasses import replace
import json
import math

import pytest
from shapely.geometry import shape
from shapely.ops import unary_union

from app.services.road_network import Road, build_network, network_snapshot
from app.services.road_source import prepare_road_update


def road(id, points, width=10, **kwargs):
    return Road(id, tuple(map(tuple, points)), width, **kwargs)


MAIN = road("main", [(-80, 0), (80, 0)])


def assert_surfaces(network):
    junctions = [shape(j["generatedGeometry"]) for j in network["intersections"]]
    surfaces = [shape(e["geometry"]) for e in network["edges"]]
    assert all(p.is_valid for p in junctions + surfaces)
    for j in junctions:
        assert j.area > 0
        assert all(j.intersection(s).area < 1e-6 for s in surfaces)
    assert all(a.intersection(b).area < 1e-6 for i, a in enumerate(junctions) for b in junctions[i + 1 :])
    envelopes = unary_union([shape(e["envelope"]) for e in network["edges"]])
    assert envelopes.difference(unary_union(junctions + surfaces)).area < 1e-5


@pytest.mark.parametrize(
    "points,width,kind,count",
    [
        ([(0, -80), (0, 80)], 10, "four_way", 4),
        ([(0, 0), (0, 80)], 10, "t_intersection", 3),
        ([(0, 0), (0, 80)], 6, "t_intersection", 3),
        ([(0, 0), (60, 80)], 10, "t_intersection", 3),
        ([(-60, -80), (60, 80)], 10, "four_way", 4),
        ([(0, 1), (0, 80)], 10, "t_intersection", 3),
        ([(0, 0), (10, 20), (30, 50), (20, 80)], 10, "t_intersection", 3),
    ],
)
def test_crossings(points, width, kind, count):
    network = build_network((MAIN, road("branch", points, width)))
    assert len(network["intersections"]) == 1
    assert len(network["edges"]) == count
    junction = network["intersections"][0]
    node = next(n for n in network["nodes"] if n["id"] == junction["nodeId"])
    assert node["nodeType"] == kind
    assert len(node["connectedEdgeIds"]) == count
    assert {e["parentRoadId"] for e in network["edges"]} == {"main", "branch"}
    assert junction["approaches"] == sorted(junction["approaches"], key=lambda a: a["angle"])
    assert_surfaces(network)


def test_endpoint_to_endpoint_and_tolerance():
    a = road("a", [(-50, 0), (0, 0)])
    b = road("b", [(1, 0), (50, 0)])
    network = build_network((a, b))
    assert len(network["nodes"]) == 3
    assert any(n["nodeType"] == "continuation" for n in network["nodes"])
    assert len(build_network((a, b), 0.5)["nodes"]) == 4


def test_curved_crossing():
    a = road("a", [(-80, -10), (-30, 5), (20, 0), (80, 15)])
    b = road("b", [(-10, -80), (0, -20), (10, 20), (-5, 80)])
    network = build_network((a, b))
    assert len(network["edges"]) == 4
    assert_surfaces(network)


def test_width_and_radius_regenerate_with_stable_ids():
    branch = road("branch", [(0, -80), (0, 80)])
    before = build_network((MAIN, branch))
    after = build_network((replace(MAIN, width=22), branch))
    assert before["intersections"][0]["id"] == after["intersections"][0]["id"]
    assert before["intersections"][0]["generatedGeometry"] != after["intersections"][0]["generatedGeometry"]
    sharp = build_network((replace(MAIN, corner_radius=0), replace(branch, corner_radius=0)))
    assert (
        shape(before["intersections"][0]["generatedGeometry"]).area
        > shape(sharp["intersections"][0]["generatedGeometry"]).area
    )
    assert_surfaces(after)


def test_alignment_and_leg_deletion():
    north = road("north", [(0, 0), (0, 80)])
    south = road("south", [(0, -80), (0, 0)])
    assert any(n["nodeType"] == "four_way" for n in build_network((MAIN, north, south))["nodes"])
    assert any(n["nodeType"] == "t_intersection" for n in build_network((MAIN, north))["nodes"])
    network = build_network((MAIN,))
    assert all(n["nodeType"] == "dead_end" for n in network["nodes"])
    moved = build_network((MAIN, replace(north, centerline=((20, 0), (20, 80)))))
    assert any(n["location"] == [20, 0] and n["nodeType"] == "t_intersection" for n in moved["nodes"])


@pytest.mark.parametrize("spacing", [4, 12, 25])
def test_close_junctions(spacing):
    network = build_network((MAIN, road("a", [(0, -60), (0, 60)]), road("b", [(spacing, -60), (spacing, 60)])))
    assert len(network["intersections"]) == 2
    assert_surfaces(network)


def test_grade_separation_and_determinism():
    branch = road("branch", [(0, -80), (0, 80)], level="bridge:1")
    network = build_network((MAIN, branch))
    assert not network["intersections"]
    assert len(network["nodes"]) == 4
    assert network == build_network((branch, MAIN))


def test_multi_leg_and_acute():
    roads = tuple(
        road(str(i), [(0, 0), (80 * math.cos(a), 80 * math.sin(a))]) for i, a in enumerate([0, 0.2, 1.5, 3.2, 4.6])
    )
    network = build_network(roads, 0)
    assert any(n["nodeType"] == "multi_leg" for n in network["nodes"])
    assert_surfaces(network)


def test_source_move_width_and_snapshot():
    props = dict(procedural_road=1, plan_centerline=[[-114, 51], [-113.999, 51]], width=10)
    initial = prepare_road_update({"properties": props})
    moved = [[x, y + 0.001] for x, y in initial["coordinates"]]
    updated = prepare_road_update({"coordinates": moved}, initial["properties"])
    assert updated["properties"]["plan_centerline"][0][1] == pytest.approx(51.001)
    wide = prepare_road_update({"properties": {"width": 20}}, updated["properties"])
    assert wide["coordinates"] != updated["coordinates"]
    snapshot = network_snapshot(json.dumps([{"id": "a", "properties": wide["properties"]}]))
    assert len(snapshot["edges"]) == 1
    json.dumps(snapshot, allow_nan=False)
    assert snapshot["features"]["features"][0]["geometry"]["coordinates"][1] == pytest.approx(51.001)


def test_legacy_and_invalid_inputs():
    assert prepare_road_update({"properties": {"width": 20}}, {"width": 10}) == {"properties": {"width": 20}}
    assert not network_snapshot('[{"id":"legacy","properties":{}}]')["edges"]
    with pytest.raises(ValueError):
        build_network((replace(MAIN, width=float("nan")),))
    with pytest.raises(ValueError):
        prepare_road_update({"properties": {"procedural_road": 1}})
