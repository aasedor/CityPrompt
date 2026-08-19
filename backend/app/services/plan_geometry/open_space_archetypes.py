"""Open-space archetype resolution — catalogue-driven, by real area band.

Why this exists: park choice was a two-way threshold (``area < 1500 ?
urban_pocket_park : neighborhood_park``) against a catalogue of 130 open-space
archetypes, so 128 of them were unreachable by the drawing engine. The two
thresholds had also drifted from the catalogue's own bands — a 1,200 m² park
resolved to ``urban_pocket_park`` whose band stops at 900 m², and a 1,600 m²
park to ``neighborhood_park`` whose band starts at 2,000 m².

The catalogue already carries ``minAreaSqm``/``maxAreaSqm`` per entry, so the
right answer is to resolve by band containment against the table rather than
to maintain constants beside it. 46 park archetypes contain 1,200 m² — the
"resolver gap" the generator was steering around only ever existed in the
four-entry canonical ladder, never in the catalogue.

Coherence, mirroring the building resolver: the unseeded answer is stable and
predictable (canonical ladder first, then lexicographic), and a ``variety_seed``
rotates only within the aesthetic family of that unseeded pick — so a district
gets ten kinds of neighbourhood green, never a Japanese garden beside a skate
park beside a cemetery.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

_DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "open_space_plan_dims.json"

# The generic ladder. These are the entries a plan should reach for when
# nothing more specific is asked, smallest band first; everything else in the
# catalogue is reachable by rotation within an aesthetic family, or by a
# palette naming it outright.
CANONICAL_PARK_LADDER = (
    "urban_pocket_park",
    "neighborhood_park",
    "community_park",
    "regional_park",
)
CANONICAL_PLAZA_LADDER = (
    "courtyard_plaza",
    "formal_civic_plaza",
)

# Palette landscape structures -> the aesthetic families that express them.
# This is what connects the Master Planner's authored planting intent to real
# catalogue breadth instead of leaving it as a render-prompt string.
STRUCTURE_FAMILIES: dict[str, tuple[str, ...]] = {
    "active_recreation": ("sports_recreation", "neighborhood_public_realm"),
    "naturalistic_grove": ("landscape_parks", "ecological_resilience"),
    "open_meadow": ("landscape_parks", "neighborhood_public_realm"),
    "formal_allee": ("specialty_gardens", "landscape_parks"),
    "garden_courtyard": ("specialty_gardens", "neighborhood_public_realm"),
}


@lru_cache(maxsize=1)
def load_open_space_dims() -> list[dict]:
    payload = json.loads(_DATA_PATH.read_text(encoding="utf-8"))
    entries = payload.get("archetypes") or []
    if not entries:
        raise RuntimeError(f"open-space dims table empty/missing: {_DATA_PATH}")
    return entries


@lru_cache(maxsize=1)
def open_space_dims_by_id() -> dict[str, dict]:
    return {entry["id"]: entry for entry in load_open_space_dims()}


def _band(entry: dict) -> tuple[float, float]:
    low = entry.get("min_area_sqm")
    high = entry.get("max_area_sqm")
    return (float(low) if low else 0.0, float(high) if high else float("inf"))


def _band_distance(entry: dict, area_m2: float) -> float:
    low, high = _band(entry)
    if low <= area_m2 <= high:
        return 0.0
    return low - area_m2 if area_m2 < low else area_m2 - high


def contains_area(archetype_id: str, area_m2: float) -> bool:
    """Whether the catalogue entry's own band admits this area."""
    entry = open_space_dims_by_id().get(archetype_id)
    if entry is None:
        return False
    low, high = _band(entry)
    return low <= area_m2 <= high


def ladder_bounds(space_type: str = "park") -> list[tuple[str, float, float]]:
    """The canonical ladder with its catalogue bands, smallest first.

    Derived, never restated — the generator's tier targets come from here so a
    catalogue edit cannot silently desynchronise the sizes a plan carves from
    the sizes the resolver can name.
    """
    ladder = CANONICAL_PARK_LADDER if space_type == "park" else CANONICAL_PLAZA_LADDER
    table = open_space_dims_by_id()
    bounds = []
    for archetype_id in ladder:
        entry = table.get(archetype_id)
        if entry is None:
            continue
        low, high = _band(entry)
        bounds.append((archetype_id, low, high))
    return sorted(bounds, key=lambda row: row[1])


def _stable_pick(candidates: list[dict], variety_seed: int | None = None) -> dict | None:
    if not candidates:
        return None
    ordered = sorted(candidates, key=lambda e: (0 if e.get("has_variants") else 1, e["id"]))
    if variety_seed is None:
        return ordered[0]
    return ordered[variety_seed % len(ordered)]


def resolve_open_space_archetype(
    area_m2: float,
    space_type: str = "park",
    *,
    structure: str | None = None,
    prefer_id: str | None = None,
    variety_seed: int | None = None,
) -> dict | None:
    """Pick an open-space archetype whose catalogue band admits ``area_m2``.

    ``prefer_id`` (a palette- or planner-named archetype) wins whenever its own
    band admits the area. Otherwise the canonical ladder is preferred, so the
    default answer stays the familiar one; ``variety_seed`` then rotates within
    the aesthetic family of that default.
    """
    table = [
        e
        for e in load_open_space_dims()
        if e.get("usable") and e.get("space_type") == space_type and e["id"] not in NOT_AT_GRADE_IDS
    ]
    if not table:
        return None

    if prefer_id:
        pinned = open_space_dims_by_id().get(prefer_id)
        if pinned is not None and pinned.get("usable") and _band_distance(pinned, area_m2) == 0.0:
            return pinned

    # The canonical ladder is the DEFAULT and always answers, by nearest band
    # rather than by containment. The bands leave real gaps (pocket stops at
    # 900 m2, neighbourhood starts at 2,000), and a 905 m2 green is obviously
    # still a pocket park — dropping the ladder there would hand the default
    # to whichever specialty entry happened to sort first, which is how a
    # generic courtyard green ends up stamped a memorial garden.
    # Smallest tier that admits the area, then nearest tier if none does.
    # Bands overlap (neighbourhood 2,000-32,000 and community 8,000-100,000
    # both admit a 3 ha green), and the smaller tier is the right name: a park
    # is not a community park merely because it is big enough to qualify.
    by_id = {e["id"]: e for e in table}
    tiers = [by_id[archetype_id] for archetype_id, _, _ in ladder_bounds(space_type) if archetype_id in by_id]
    primary = next((entry for entry in tiers if _band_distance(entry, area_m2) == 0.0), None)
    if primary is None and tiers:
        best_tier = min(_band_distance(entry, area_m2) for entry in tiers)
        primary = _stable_pick([entry for entry in tiers if _band_distance(entry, area_m2) == best_tier])

    # Breadth comes from rotation, over entries whose OWN band admits the area.
    in_band = [e for e in table if _band_distance(e, area_m2) == 0.0]
    if not in_band:
        best = min(_band_distance(e, area_m2) for e in table)
        in_band = [e for e in table if _band_distance(e, area_m2) == best]

    if primary is None:
        primary = _stable_pick(in_band)
    if primary is None:
        return None
    if variety_seed is None:
        return primary

    families = STRUCTURE_FAMILIES.get(structure or "", ()) or (primary.get("aesthetic_category", ""),)
    coherent = [
        entry for entry in in_band if entry.get("aesthetic_category") in families and _fits_by_scale(entry, area_m2)
    ]
    return _stable_pick(coherent or [primary], variety_seed=variety_seed)


# An entry's band is permissive — a velodrome and a lawn can both "admit"
# 3,000 m2. The catalogue's suggested area is what the archetype is actually
# drawn for, so rotation additionally requires the green to be within this
# factor of it. Without it, variety puts an equestrian centre in a 6 ha
# inner-city plan: technically in band, obviously wrong.
SCALE_FIT_FACTOR = 2.5

# Catalogue entries that are not at-grade public open space, so a master plan
# must never select one for a park polygon carved out of a block. The catalogue
# marks them spaceType=park because they are planted, not because they sit on
# the ground. Named explicitly rather than pattern-matched: this is a short,
# reviewable list, and a silent regex would quietly drop legitimate entries as
# the catalogue grows.
NOT_AT_GRADE_IDS = frozenset({"rooftop_garden"})


def _fits_by_scale(entry: dict, area_m2: float) -> bool:
    suggested = entry.get("suggested_area_sqm")
    if not suggested or suggested <= 0 or area_m2 <= 0:
        return True
    return 1 / SCALE_FIT_FACTOR <= area_m2 / float(suggested) <= SCALE_FIT_FACTOR
