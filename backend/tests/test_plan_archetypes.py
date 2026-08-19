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


# ---------------------------------------------------------------------------
# Catalogue breadth — seeded rotation and the derived development-type set
# ---------------------------------------------------------------------------


def _pool_for(dev_type: str, aesthetic: str, floors: int) -> set[str]:
    """Every archetype the resolver will return across a run of seeds."""
    return {
        entry["id"]
        for seed in range(40)
        if (entry := resolve_building_archetype(dev_type, aesthetic, floors, variety_seed=seed))
    }


def test_unseeded_resolution_is_unchanged_by_the_variety_feature():
    """The parity contract: no seed means the frontend's exact answer."""
    for dev_type in ("residential_single_family", "residential_multifamily", "mixed_use"):
        for floors in (2, 4, 8):
            assert resolve_building_archetype(dev_type, "contemporary", floors) == resolve_building_archetype(
                dev_type, "contemporary", floors, variety_seed=None
            )


def test_seeded_rotation_uses_more_than_one_archetype():
    """A 26-entry pool answering the same query must not collapse onto one
    building — that is what made a 224-entry catalogue render as ~9."""
    pool = _pool_for("residential_single_family", "contemporary", 3)
    assert len(pool) > 1


def test_seeded_rotation_is_deterministic():
    """Same site, same plan — the seed is derived from the site hash."""
    for seed in (0, 7, 12345):
        first = resolve_building_archetype("residential_multifamily", "contemporary", 5, variety_seed=seed)
        second = resolve_building_archetype("residential_multifamily", "contemporary", 5, variety_seed=seed)
        assert first == second


def test_rotation_stays_inside_compatible_style_families():
    """Variety must not put a machiya beside a Calgary walk-up."""
    from app.services.plan_geometry.archetypes import compatible_families, family_of

    primary = resolve_building_archetype("residential_single_family", "contemporary", 3)
    primary_family = family_of(primary["id"])
    if primary_family is None:
        pytest.skip("archetype_families.json unavailable; coherence guard is a no-op by design")
    allowed = compatible_families(primary_family)
    for archetype_id in _pool_for("residential_single_family", "contemporary", 3):
        assert family_of(archetype_id) in allowed, archetype_id


def test_catalog_dev_types_is_derived_from_the_table():
    """Hand-listing this set let it drift to 9 entries against a 26-type
    catalogue, capping how much of the library any plan could reach and
    contradicting the Master Planner, which validates against the table."""
    from app.services.plan_geometry.archetypes import load_dims_table
    from app.services.plan_geometry.placement import CATALOG_DEV_TYPES

    in_table = {e["development_type"] for e in load_dims_table() if e["usable"]}
    assert CATALOG_DEV_TYPES == in_table
    assert len(CATALOG_DEV_TYPES) > 20


def test_every_catalog_dev_type_actually_resolves():
    """The guarantee the hand-list was protecting: no emitted type may fall
    back to mixed_use."""
    from app.services.plan_geometry.placement import CATALOG_DEV_TYPES

    for dev_type in CATALOG_DEV_TYPES:
        entry = resolve_building_archetype(dev_type, "", 4)
        assert entry is not None, dev_type
        assert entry["development_type"] == dev_type, f"{dev_type} fell back to {entry['development_type']}"
