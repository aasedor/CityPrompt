"""Plan Evaluator + refinement loop — the P3 gate: a rigged bad plan must
measurably improve across iterations, every revision must carry its reason,
and locked layers must constrain what the loop may change."""

import math

from shapely.geometry import Polygon

from app.services.plan_geometry.plan_evaluator import (
    EvaluationReport,
    ScoreItem,
    evaluate_plan,
    revise_rules,
)
from app.services.plan_geometry.refinement import run_refinement_loop

LAT, LON = 51.0405, -114.0850
M_LAT = 111_320.0
M_LON = M_LAT * math.cos(math.radians(LAT))


def _offset(lon_m, lat_m):
    return (LON + lon_m / M_LON, LAT + lat_m / M_LAT)


def _site(width_m=500.0, depth_m=340.0) -> Polygon:
    return Polygon([_offset(0, 0), _offset(width_m, 0), _offset(width_m, depth_m), _offset(0, depth_m)])


DNA_STUB = {"land_use": {"fields": {"districts": {"value": [], "confidence": 0.0}}}, "site": {"fields": {}}}


def _report(**scores) -> EvaluationReport:
    report = EvaluationReport()
    for key, score in scores.items():
        report.add(ScoreItem(key=key, score=score))
    return report.finalize()


# ---------------------------------------------------------------------------
# Revision rules
# ---------------------------------------------------------------------------

def test_low_yield_bumps_floors_with_reason():
    base = {"floors": 4.0, "open_space_share": 0.1, "block_target_m": 180.0}
    overrides, revisions = revise_rules(_report(yield_vs_target=0.5), {}, base, [])
    assert overrides["floors"] == 5.0
    assert any(r["parameter"] == "floors" and "yield_vs_target" in r["reason"] for r in revisions)


def test_floor_bump_is_bounded():
    # base_rules follows the overrides between iterations (the generator applies
    # them), so the cap must hold via the explicit bump counter — feed the loop
    # its own output 4 times and require exactly 3 bumps.
    overrides: dict[str, float] = {}
    bumps = 0
    for iteration in range(4):
        base = {"floors": overrides.get("floors", 4.0), "open_space_share": 0.1,
                "block_target_m": 180.0}
        overrides, revisions = revise_rules(_report(yield_vs_target=0.5), overrides, base, [])
        bumps += sum(1 for r in revisions if r["parameter"] == "floors")
    assert bumps == 3
    assert overrides["floors"] == 7.0  # 4.0 + 3 bounded storeys


def test_streets_lock_blocks_grid_revisions():
    base = {"floors": 4.0, "open_space_share": 0.1, "block_target_m": 200.0}
    _, unlocked = revise_rules(_report(intersection_density=0.2), {}, base, [])
    assert any(r["parameter"] == "block_target_m" for r in unlocked)
    _, locked = revise_rules(_report(intersection_density=0.2), {}, base, ["streets"])
    assert not any(r["parameter"] == "block_target_m" for r in locked)


def test_no_revisions_when_everything_is_good():
    base = {"floors": 6.0, "open_space_share": 0.12, "block_target_m": 150.0}
    _, revisions = revise_rules(
        _report(yield_vs_target=1.0, open_space=1.0, park_access=1.0,
                intersection_density=0.9, block_scale=1.0),
        {}, base, [],
    )
    assert revisions == []


# ---------------------------------------------------------------------------
# Evaluator on real drawn geometry
# ---------------------------------------------------------------------------

def test_evaluator_scores_a_real_plan():
    from app.services.plan_geometry.generator import generate_plan_geometry

    result = generate_plan_geometry(
        site_polygon_wgs84=_site(), scenario_id="lap_compliant", scenario_label="LAP",
        parameters={"streets.row_width_m": {"value": 16.0}, "buildings.floors": {"value": 6}},
        road_features=[], district_features=[],
    )
    report = evaluate_plan(result, {"landscape.tree_density": {"value": 0.7}}, units_estimate=2000)
    assert 0.0 < report.overall <= 1.0
    assert report.scores["fire_access"].score == 1.0
    assert "park_access" in report.scores
    assert "detail" in report.scores["canopy_proxy"].model_dump()
    assert all(0.0 <= s.score <= 1.0 for s in report.scores.values())


# ---------------------------------------------------------------------------
# The P3 gate: a rigged bad plan measurably improves across iterations
# ---------------------------------------------------------------------------

def test_rigged_bad_plan_improves_across_iterations():
    # Rig: 2 storeys against a 3,000-unit target, starved open space, coarse grid.
    parameters = {
        "streets.row_width_m": {"value": 16.0},
        "buildings.floors": {"value": 2},
        "buildings.unit_count": {"value": 3000},
        "buildings.development_type": {"value": "mixed_use"},
        "landscape.tree_density": {"value": 0.3},
    }
    result, metrics, iterations = run_refinement_loop(
        site_polygon_wgs84=_site(),
        scenario_id="as_of_right",           # coarse 200 m grid, 10% open space
        scenario_label="Rigged",
        parameters=parameters,
        dna=DNA_STUB,
        road_features=[], district_features=[],
    )
    assert len(iterations) >= 2, "the loop should have found revisions to try"
    first, last = iterations[0], iterations[-1]
    assert last["overall_score"] > first["overall_score"], (
        f"no improvement: {first['overall_score']} -> {last['overall_score']}"
    )
    # Every non-final iteration recorded WHY the next one differs.
    for step in iterations[:-1]:
        assert step["revisions"], "intermediate iteration without recorded revisions"
        assert all(r.get("reason") for r in step["revisions"])
    # The revisions actually took effect on the drawn plan.
    assert last["overrides_in_effect"].get("floors", 2) > 2 or \
           last["overrides_in_effect"].get("open_space_share", 0) > 0.1
    # Final metrics are geometry-mode and internally consistent.
    assert metrics.mode == "geometry"
    gi = result.geometry_inputs
    assert abs(gi["row_area_m2"] + gi["open_space_area_m2"] + gi["net_block_area_m2"]
               - gi["site_area_m2"]) / gi["site_area_m2"] < 0.06


def test_locked_streets_survive_the_loop():
    from shapely.ops import unary_union

    from app.services.plan_geometry.generator import generate_plan_geometry

    parameters = {
        "streets.row_width_m": {"value": 16.0},
        "buildings.floors": {"value": 2},
        "buildings.unit_count": {"value": 3000},
    }
    seed = generate_plan_geometry(
        site_polygon_wgs84=_site(), scenario_id="as_of_right", scenario_label="Seed",
        parameters=parameters, road_features=[], district_features=[],
    )
    locked = unary_union([Polygon(z["coordinates"]) for z in seed.zones if z["zone_type"] == "road"])

    result, _, iterations = run_refinement_loop(
        site_polygon_wgs84=_site(), scenario_id="as_of_right", scenario_label="Locked",
        parameters=parameters, dna=DNA_STUB,
        road_features=[], district_features=[],
        locked_street_area_wgs84=locked, locks=["streets"],
    )
    # The loop iterated, but never touched the grid — and never judged the
    # locked network's intersection density (no countable centerlines).
    for step in iterations:
        assert not any(r["parameter"] == "block_target_m" for r in step["revisions"])
        assert "intersection_density" not in step["scores"]
    street_area = sum(Polygon(z["coordinates"]).area for z in result.zones if z["zone_type"] == "road")
    assert abs(street_area - locked.area) / locked.area < 0.02
