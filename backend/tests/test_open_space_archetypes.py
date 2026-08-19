"""Open-space archetype resolution — bands, tiers, coherence, and no drift.

The engine used to name 2 archetypes out of a 130-entry catalogue, from a
hardcoded threshold that sat inside neither band it selected. These tests pin
the replacement: resolution against the catalogue's own area bands, a canonical
tier ladder that always answers, and rotation that widens the palette without
putting a velodrome in a courtyard.
"""

import json
from pathlib import Path

import pytest

from app.services.plan_geometry.open_space_archetypes import (
    CANONICAL_PARK_LADDER,
    NOT_AT_GRADE_IDS,
    SCALE_FIT_FACTOR,
    contains_area,
    ladder_bounds,
    load_open_space_dims,
    open_space_dims_by_id,
    resolve_open_space_archetype,
)

_FRONTEND_CATALOGUE = Path(__file__).resolve().parents[2] / "frontend" / "src" / "data" / "openSpaceArchetypes.json"


def _resolve(area: float, **kwargs) -> str:
    entry = resolve_open_space_archetype(area, **kwargs)
    assert entry is not None
    return entry["id"]


# ---------------------------------------------------------------------------
# Table integrity
# ---------------------------------------------------------------------------


def test_table_loads_and_is_populated():
    table = load_open_space_dims()
    assert len(table) > 100
    assert all(entry.get("id") for entry in table)


def test_every_canonical_ladder_entry_exists():
    table = open_space_dims_by_id()
    for archetype_id in CANONICAL_PARK_LADDER:
        assert archetype_id in table, archetype_id


def test_ladder_is_ordered_and_covers_a_real_range():
    bounds = ladder_bounds("park")
    assert [row[0] for row in bounds] == list(CANONICAL_PARK_LADDER)
    assert bounds[0][1] < bounds[-1][1]


def test_codegen_table_has_not_drifted_from_the_frontend_catalogue():
    """The backend table is committed codegen. If the frontend catalogue moves
    and the export is not re-run, the two resolvers silently disagree — which
    is exactly the failure this whole module replaced."""
    if not _FRONTEND_CATALOGUE.exists():
        pytest.skip("frontend catalogue not present in this checkout")
    payload = json.loads(_FRONTEND_CATALOGUE.read_text(encoding="utf-8"))
    source = payload.get("archetypes") if isinstance(payload, dict) else payload
    source_bands = {entry["id"]: (entry.get("minAreaSqm"), entry.get("maxAreaSqm")) for entry in source or []}
    for entry in load_open_space_dims():
        assert entry["id"] in source_bands, f"{entry['id']} no longer in the catalogue — re-run the export"
        low, high = source_bands[entry["id"]]
        assert entry["min_area_sqm"] == low
        assert entry["max_area_sqm"] == high


# ---------------------------------------------------------------------------
# Tier selection
# ---------------------------------------------------------------------------


def test_smallest_containing_tier_wins():
    """Bands overlap: a 3 ha green is admitted by both neighbourhood and
    community. It is not a community park merely because it qualifies."""
    assert contains_area("neighborhood_park", 32_000)
    assert contains_area("community_park", 32_000)
    assert _resolve(32_000) == "neighborhood_park"


def test_tiers_step_up_with_area():
    picks = [_resolve(area) for area in (400, 2_500, 60_000, 200_000)]
    assert picks == ["urban_pocket_park", "neighborhood_park", "community_park", "regional_park"]


def test_area_in_a_band_gap_still_resolves_to_the_nearest_tier():
    """905 m2 falls between the pocket ceiling (900) and the neighbourhood
    floor (2,000). The old code stamped it pocket park via a threshold that
    disagreed with both bands; the answer is right, the reasoning was not."""
    assert not contains_area("urban_pocket_park", 905)
    assert not contains_area("neighborhood_park", 905)
    assert _resolve(905) == "urban_pocket_park"


def test_plaza_ladder_is_separate_from_parks():
    assert _resolve(600, space_type="plaza") != _resolve(600, space_type="park")


# ---------------------------------------------------------------------------
# Authored ids
# ---------------------------------------------------------------------------


def test_authored_id_wins_when_its_band_admits_the_area():
    assert _resolve(5_000, prefer_id="japanese_garden") == "japanese_garden"


def test_authored_id_is_ignored_when_its_band_cannot_hold_the_area():
    """Honouring it anyway would stamp an archetype the renderer must stretch
    far outside the geometry the entry describes."""
    assert not contains_area("urban_pocket_park", 250_000)
    assert _resolve(250_000, prefer_id="urban_pocket_park") != "urban_pocket_park"


# ---------------------------------------------------------------------------
# Rotation: breadth without incoherence
# ---------------------------------------------------------------------------


def test_rotation_widens_the_palette():
    picks = {_resolve(6_000, structure="active_recreation", variety_seed=seed) for seed in range(20)}
    assert len(picks) > 1


def test_rotation_is_deterministic():
    for seed in (0, 5, 991):
        assert _resolve(6_000, variety_seed=seed) == _resolve(6_000, variety_seed=seed)


def test_unseeded_resolution_is_the_canonical_tier():
    """No seed must stay predictable — the ladder, never a specialty entry."""
    for area in (400, 2_500, 60_000):
        assert _resolve(area) in CANONICAL_PARK_LADDER


def test_rotation_respects_scale_fit():
    """An entry's band is permissive enough to admit a velodrome into a
    courtyard. The catalogue's suggested area is what it is really drawn for."""
    table = open_space_dims_by_id()
    area = 3_000.0
    for seed in range(30):
        entry = table[_resolve(area, structure="active_recreation", variety_seed=seed)]
        suggested = entry.get("suggested_area_sqm")
        if not suggested:
            continue
        assert 1 / SCALE_FIT_FACTOR <= area / suggested <= SCALE_FIT_FACTOR, entry["id"]


def test_rotation_never_selects_a_non_at_grade_archetype():
    """A rooftop garden is planted, not at grade — it cannot be a park carved
    out of a block."""
    assert "rooftop_garden" in NOT_AT_GRADE_IDS
    picks = {_resolve(1_500, variety_seed=seed) for seed in range(40)}
    assert not (picks & NOT_AT_GRADE_IDS)


def test_derived_band_constants_match_the_catalogue():
    from app.services.plan_geometry.placement import (
        NEIGHBORHOOD_PARK_MIN_M2,
        POCKET_PARK_MAX_M2,
        POCKET_PARK_MIN_M2,
    )

    table = open_space_dims_by_id()
    assert POCKET_PARK_MIN_M2 == table["urban_pocket_park"]["min_area_sqm"]
    assert POCKET_PARK_MAX_M2 == table["urban_pocket_park"]["max_area_sqm"]
    assert NEIGHBORHOOD_PARK_MIN_M2 == table["neighborhood_park"]["min_area_sqm"]
