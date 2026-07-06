"""Yield & Metrics Engine — every number verified against hand calculation.

The Beltline case is computed BY HAND in comments; the acceptance bar from the
mission prompt is ±10% vs hand math (here we assert exact arithmetic since the
same constants drive both — the ±10% bar applies to the live smoke).
"""

import pytest

from app.services.plan_metrics import (
    ASSUMPTIONS,
    coerce_floors,
    compute_metrics,
    reconcile_ceilings,
)

# Beltline test site: 164,000 m² gross (16.4 ha), dominant CC-X, floors=6.
SITE_AREA = 164_000.0

BELTLINE_DNA = {
    "land_use": {
        "fields": {
            "districts": {
                "value": [
                    {"code": "CC-X", "area_pct_of_site": 41.07, "far": None, "height_m": None},
                    {"code": "DC", "area_pct_of_site": 24.36, "far": None, "height_m": None},
                    {"code": "CC-MH", "area_pct_of_site": 20.72, "far": None, "height_m": 80.0},
                ],
                "confidence": 1.0,
            },
            "lap_building_scale": {"value": None, "confidence": 0.0},
        },
    },
    "site": {"fields": {}},
}

PARAMS = {
    "buildings.floors": {"value": 6, "rationale": "r"},
    "buildings.development_type": {"value": "mixed_use"},
}


def test_beltline_parameter_mode_hand_verified():
    report = compute_metrics(
        scenario_id="as_of_right",
        dna=BELTLINE_DNA,
        parameters=PARAMS,
        geometry_inputs={"site_area_m2": SITE_AREA},
    )
    assert report.mode == "parameter"  # site_area alone must NOT flip to geometry mode
    m = report.metrics

    # HAND MATH:
    # net       = 164,000 x (1 - 0.22 - 0.10)          = 111,520
    # footprint = 111,520 x 0.50                        = 55,760
    # GFA       = 55,760 x 6                            = 334,560
    # FAR       = 334,560 / 164,000                     = 2.04
    # res GFA   = 334,560 x (1 - 0.15)                  = 284,376
    # units     = 284,376 x 0.82 / 75                   = 3,109.2
    # pop       = 3,109.2 x 1.7                         = 5,285.7
    # parking   = 3,109.2 x 0.50                        = 1,554.6
    assert m["net_developable_m2"].value == pytest.approx(111_520, rel=0.001)
    assert m["building_footprint_m2"].value == pytest.approx(55_760, rel=0.001)
    assert m["gfa_m2"].value == pytest.approx(334_560, rel=0.001)
    assert m["far_achieved"].value == pytest.approx(2.04, abs=0.01)
    assert m["units"].value == pytest.approx(3_109, rel=0.001)
    assert m["population"].value == pytest.approx(5_286, rel=0.001)
    assert m["parking_stalls"].value == pytest.approx(1_555, rel=0.001)

    # Derivations carry the actual numbers — no naked values.
    assert "111,520" in m["net_developable_m2"].derivation
    assert "334,560" in m["gfa_m2"].derivation
    assert "0.82" in m["units"].derivation
    # Assumptions are disclosed per metric and collected on the report.
    assert "avg_unit_area_m2" in m["units"].assumptions
    assert "persons_per_unit" in report.assumptions_used


def test_climate_scenario_uses_reduced_parking_ratio():
    report = compute_metrics(
        scenario_id="climate_first", dna=BELTLINE_DNA, parameters=PARAMS,
        geometry_inputs={"site_area_m2": SITE_AREA},
    )
    units = report.metrics["units"].value
    assert report.metrics["parking_stalls"].value == pytest.approx(units * 0.25, rel=0.001)
    assert "parking_ratio_climate" in report.metrics["parking_stalls"].assumptions


def test_geometry_mode_supersedes_parameter_assumptions():
    report = compute_metrics(
        scenario_id="as_of_right", dna=BELTLINE_DNA, parameters=PARAMS,
        geometry_inputs={
            "site_area_m2": SITE_AREA,
            "row_area_m2": 30_000.0,
            "open_space_area_m2": 20_000.0,
            "net_block_area_m2": 114_000.0,
            "building_footprint_m2": 50_000.0,
        },
    )
    assert report.mode == "geometry"
    m = report.metrics
    assert m["net_developable_m2"].value == pytest.approx(114_000)
    assert m["net_developable_m2"].assumptions == []          # no land-share assumptions
    assert m["gfa_m2"].value == pytest.approx(300_000)        # 50,000 x 6
    assert "drawn" in m["building_footprint_m2"].derivation


def test_prose_floors_ranges_take_the_midpoint():
    floors, how = coerce_floors("6-16 storeys, stepped", 3.2)
    assert floors == 11.0
    assert "midpoint" in how
    floors, _ = coerce_floors(8, 3.2)
    assert floors == 8.0
    floors, how = coerce_floors(None, 3.2)
    assert floors is None


def test_ceiling_reconciliation_uses_lap_fallback_and_flags_exceedance():
    districts = [
        {"code": "CC-MH", "area_pct_of_site": 20.0, "far": None, "height_m": 80.0},
        {"code": "M-CG", "area_pct_of_site": 50.0, "far": None, "height_m": None},
    ]
    rec, warnings = reconcile_ceilings(districts, "low", proposed_floors=11.0, floor_height_m=3.2)

    cc_mh = next(r for r in rec if r["district"] == "CC-MH")
    assert cc_mh["ceiling_floors"] == 25.0            # 80 / 3.2
    assert cc_mh["status"] == "within"

    m_cg = next(r for r in rec if r["district"] == "M-CG")
    assert m_cg["ceiling_floors"] == 6.0              # LAP 'low' fallback
    assert "LAP building-scale" in m_cg["source"]     # says so explicitly
    assert m_cg["status"] == "exceeds"                # 11 > 6
    assert any("M-CG" in w and "relaxation" in w for w in warnings)


def test_unknown_ceiling_is_reported_not_guessed():
    rec, warnings = reconcile_ceilings(
        [{"code": "DC", "area_pct_of_site": 24.0, "far": None, "height_m": None}],
        None, proposed_floors=6.0, floor_height_m=3.2,
    )
    assert rec[0]["status"] == "unknown"
    assert any("not assessable" in w for w in warnings)


def test_missing_site_area_degrades_with_warning():
    report = compute_metrics(scenario_id="x", dna=BELTLINE_DNA, parameters=PARAMS)
    assert report.metrics == {}
    assert any("site area unavailable" in w for w in report.warnings)
