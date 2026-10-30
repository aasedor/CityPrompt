"""Small pathways must compile without weakening existing street contracts."""

import copy
import json
from pathlib import Path
import pytest
from types import SimpleNamespace
from shapely import affinity
from shapely.geometry import LineString, Point, Polygon
from shapely.ops import unary_union
from app.services.site_engine import WGS84_CRS, build_transformer, project_geometry
from app.services.native_street_candidate_contract import build_native_street_candidate_catalog
from app.services.public_realm_lego import (
    PublicRealmPlanRequest,
    StreetSegmentTarget,
    plan_public_realm_recipe,
    public_realm_recipe_identity,
    PublicRealmPlanningError,
    plan_public_realm_zone_recipe,
)

DATA = Path(__file__).resolve().parents[1] / "app/data/nativeStreetPilots.json"
PATHS = [
    row
    for row in json.loads(DATA.read_text(encoding="utf-8"))
    if row.get("program", {}).get("adapter") == "narrow-pathway-v1" and not row["id"].startswith("standalone_")
]
ALL_PATHS = [
    row
    for row in json.loads(DATA.read_text(encoding="utf-8"))
    if row.get("program", {}).get("adapter") == "narrow-pathway-v1"
]


def path_source(row, points):
    """Match the editor's filled exterior and keep the full source route."""
    line = LineString(points)
    radius = row["widthM"] / 2
    corridor = unary_union(
        [LineString([a, b]).buffer(radius, cap_style=2) for a, b in zip(points, points[1:])]
        + [Point(point).buffer(radius, quad_segs=6) for point in points[1:-1]]
    )
    geometry = Polygon(corridor.exterior)
    to_world = build_transformer("EPSG:32611", WGS84_CRS)
    offset = affinity.translate
    geometry_wgs = project_geometry(offset(geometry, xoff=705000, yoff=5658000), to_world)
    world_line = project_geometry(offset(line, xoff=705000, yoff=5658000), to_world)
    coordinates = [list(point) for point in world_line.coords]
    props = {
        "road_archetype_id": row["sourceArchetypeId"],
        "road_selected_variant_id": row["id"],
        "width": row["widthM"],
        "lane_count": 0,
        "plan_centerline": coordinates,
        "plan_route_controls": copy.deepcopy(coordinates),
    }
    return geometry_wgs, props, line.length


@pytest.mark.parametrize("row", ALL_PATHS, ids=lambda row: row["id"])
@pytest.mark.parametrize(
    "points",
    [
        [(0, 0), (20, 0), (1, 1), (20, 2)],
        [(0, 0), (20, 0), (0, 0), (0, 20)],
        [(0, 0), (70, 0), (70, 70), (0, 70), (0, 0)],
        [(0, 0), (20, 20), (0, 20), (20, 0)],
        [(0, 0), (0.3, 0), (10, 0)],
        [(0, 0), (10, 0), (10, 0.3)],
    ],
)
def test_geometry_backed_path_recipe_preserves_route_length_and_compile_source(row, points):
    from app.api.v1.lego_assembly import _public_realm_recipe_for_zone

    geometry, props, length = path_source(row, points)
    before = copy.deepcopy(props)
    recipe = plan_public_realm_zone_recipe("road", geometry, props, strict=True)
    assert recipe is not None
    assert recipe.target.row_width_m == row["widthM"]
    assert recipe.target.length_m == pytest.approx(length, abs=0.02)
    zone = SimpleNamespace(id="path", zone_type="road", properties=props, geometry=geometry.wkt)
    compiled = _public_realm_recipe_for_zone(zone, "street")
    assert compiled is not None
    assert zone.properties == before
    assert compiled["target"]["length_m"] == pytest.approx(length, abs=0.02)


@pytest.mark.parametrize("row", PATHS, ids=lambda row: row["id"])
def test_pathway_recipe_roundtrip_and_width_lock(row):
    for length in [2, 35, 300, 2000]:
        recipe = plan_public_realm_recipe(
            PublicRealmPlanRequest(
                archetype_id=row["sourceArchetypeId"],
                variant_id=row["id"],
                target=StreetSegmentTarget(row_width_m=row["widthM"], length_m=length),
            )
        )
        assert public_realm_recipe_identity(recipe) is not None
        assert recipe.variant_id == row["id"]
        assert recipe.target.row_width_m == row["widthM"]
        assert f"program:{row['programSha256']}" in recipe.component_set_ids
    for width, length in [(5, 35), (row["widthM"], 1), (row["widthM"], 2001)]:
        with pytest.raises(PublicRealmPlanningError):
            plan_public_realm_recipe(
                PublicRealmPlanRequest(
                    archetype_id=row["sourceArchetypeId"],
                    variant_id=row["id"],
                    target=StreetSegmentTarget(row_width_m=width, length_m=length),
                )
            )


@pytest.mark.parametrize("mutation", ["unknown_id", "wrong_width", "missing_module", "changed_program"])
def test_surface_only_exception_is_finite_and_hash_locked(tmp_path, mutation):
    rows = json.loads(DATA.read_text(encoding="utf-8"))
    row = copy.deepcopy(PATHS[0])
    if mutation == "unknown_id":
        row["id"] = "invented_path_v1"
    elif mutation == "wrong_width":
        row["widthM"] = 1.2
    elif mutation == "changed_program":
        row["program"]["baseLiftM"] = 3
    else:
        row = copy.deepcopy(rows[0])
        row["modules"] = {}
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps([row]), encoding="utf-8")
    with pytest.raises(ValueError):
        build_native_street_candidate_catalog(manifest)


def test_five_exact_pathway_choices():
    assert len(PATHS) == 5
    assert sorted(p["widthM"] for p in PATHS) == [1.5, 1.8, 2, 2, 3]


@pytest.mark.parametrize("variant", [None, [], {}, "invented_path_v1", "road_diet_complete_street_v1"])
def test_pathway_attestation_does_not_exempt_other_or_malformed_designs(variant):
    from app.services.surface_path import surface_path_width

    assert surface_path_width({"road_selected_variant_id": variant}) is None


@pytest.mark.parametrize(
    "mutation",
    ["wrong_width", "motor_lanes", "wrong_archetype", "missing_route", "nonfinite", "unrelated_route", "too_long"],
)
def test_pathway_attestation_rejects_untrusted_geometry_without_rewriting_source(mutation):
    from app.api.v1.lego_assembly import _public_realm_recipe_for_zone
    from fastapi import HTTPException

    geometry, props, _ = path_source(PATHS[0], [(0, 0), (20, 0), (1, 1), (20, 2)])
    if mutation == "wrong_width":
        props["width"] *= 3
    elif mutation == "motor_lanes":
        props["lane_count"] = 1
    elif mutation == "wrong_archetype":
        props["road_archetype_id"] = "unrelated_street"
    elif mutation == "missing_route":
        props.pop("plan_centerline")
    elif mutation == "nonfinite":
        props["plan_centerline"][0][0] = float("inf")
    elif mutation == "unrelated_route":
        props["plan_centerline"] = [[x + 0.001, y] for x, y in props["plan_centerline"]]
    else:
        geometry, props, _ = path_source(PATHS[0], [(0, 0), (2001, 0)])
    before = copy.deepcopy(props)
    zone = SimpleNamespace(id="invalid-path", zone_type="road", properties=props, geometry=geometry.wkt)
    with pytest.raises(HTTPException) as error:
        _public_realm_recipe_for_zone(zone, "street")
    assert error.value.status_code == 422
    assert error.value.detail["code"] == "invalid_pathway_source"
    assert zone.properties == before
