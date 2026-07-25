"""Backend archetype resolver — parity with resolvePlanZoneArchetypes.ts.

The pinned ids below are GROUND TRUTH captured from the frontend resolver
(vitest probe, 2026-07-11). If a catalog change breaks one of these, re-probe
the frontend with the same inputs and update BOTH sides deliberately — the
whole model-aware-plan design rests on backend and frontend agreeing.
"""

from types import SimpleNamespace

import pytest

from app.services.plan_geometry.archetypes import (
    MAX_TARGET_M,
    MIN_TARGET_M,
    MeasuredEntry,
    build_measured_dims,
    load_dims_table,
    resolve_building_archetype,
    target_footprint,
)

# (development_type, aesthetic, floors) -> frontend-resolved archetype id
FRONTEND_PARITY = [
    (("residential_multifamily", "contemporary_urban", 6), "contemporary_midrise"),
    (("mixed_use", "", 6), "alpine_mixed_use_lodge"),
    (("commercial_office", "modern", 20), "calgary_plus_15_connected_tower"),
    (("residential", "", 5), "adaptive_reuse_warehouse_lofts"),  # prefix fallback
    (("unknown_type_zzz", "", 3), "alpine_mixed_use_lodge"),  # mixed_use fallback
    (("residential_multifamily", "european", 4), "amsterdam_cornice_house"),  # family tier
    (("residential_multifamily", "contemporary_urban", 40), "contemporary_midrise"),  # nearest range
]


@pytest.mark.parametrize("inputs,expected", FRONTEND_PARITY)
def test_parity_with_frontend_resolver(inputs, expected):
    dev_type, aesthetic, floors = inputs
    entry = resolve_building_archetype(dev_type, aesthetic, floors)
    assert entry is not None
    assert entry["id"] == expected


def test_resolution_is_deterministic():
    picks = {resolve_building_archetype("mixed_use", "modern", 5)["id"] for _ in range(10)}
    assert len(picks) == 1


def test_table_loads_and_is_populated():
    table = load_dims_table()
    assert len(table) > 200
    assert all("id" in e and "usable" in e for e in table[:5])


def _entry(**overrides):
    base = {
        "id": "test_arch",
        "suggested_w_m": 25.0,
        "suggested_d_m": 18.0,
        "min_w_m": 15.0,
        "max_w_m": 40.0,
        "min_d_m": 12.0,
        "max_d_m": 25.0,
    }
    base.update(overrides)
    return base


def _measured(long_per_height, short_per_height, variant="default"):
    return {
        "test_arch": MeasuredEntry(
            variant_id=variant,
            dimensions={
                "long_per_height": long_per_height,
                "short_per_height": short_per_height,
                "aspect": long_per_height / short_per_height,
            },
        )
    }


def test_target_measured_beats_catalog_and_scales_with_floors():
    # 6 floors x 3.2 = 19.2m; long 0.7101/h -> 13.6m but clamped to min_w 15
    t6 = target_footprint(_entry(), 6, _measured(0.7101, 0.5796))
    assert t6.source == "measured"
    assert t6.width_m == 15.0  # clamped up to catalog min
    # 10 floors x 3.2 = 32m; long -> 22.7m, inside envelope
    t10 = target_footprint(_entry(), 10, _measured(0.7101, 0.5796))
    assert t10.width_m == pytest.approx(22.72, abs=0.1)
    assert t10.depth_m == pytest.approx(18.55, abs=0.1)
    assert t10.width_m >= t10.depth_m


def test_target_catalog_fallback_when_unmeasured():
    t = target_footprint(_entry(), 6, {})
    assert t.source == "catalog"
    assert (t.width_m, t.depth_m) == (25.0, 18.0)


def test_target_none_when_no_dims_anywhere():
    entry = _entry(suggested_w_m=None, suggested_d_m=None)
    assert target_footprint(entry, 6, {}) is None


def test_target_absolute_clamps():
    # Absurd measured ratios stay within the absolute envelope even without
    # catalog min/max.
    entry = _entry(min_w_m=None, max_w_m=None, min_d_m=None, max_d_m=None)
    tall = target_footprint(entry, 60, _measured(3.0, 2.0))
    assert tall.width_m <= MAX_TARGET_M
    tiny = target_footprint(entry, 1, _measured(0.05, 0.04))
    assert tiny.depth_m >= MIN_TARGET_M


def test_build_measured_dims_prefers_default_variant():
    rows = [
        SimpleNamespace(
            archetype_id="a",
            variant_id="variant_1",
            metadata_={"dimensions": {"long_per_height": 1.0, "short_per_height": 0.5}},
        ),
        SimpleNamespace(
            archetype_id="a",
            variant_id="default",
            metadata_={"dimensions": {"long_per_height": 0.6, "short_per_height": 0.4}},
        ),
        SimpleNamespace(archetype_id="b", variant_id="default", metadata_=None),  # no dims -> skipped
    ]
    measured = build_measured_dims(rows)
    assert set(measured) == {"a"}
    assert measured["a"].variant_id == "default"
    assert measured["a"].dimensions["long_per_height"] == 0.6
