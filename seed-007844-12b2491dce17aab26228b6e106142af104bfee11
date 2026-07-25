"""
Backend archetype resolution for plan generation — the model-aware brain.

Line-for-line port of the frontend resolver (resolvePlanZoneArchetypes.ts
resolveBuilding + AESTHETIC_FAMILIES + stablePick) over the codegen'd dims
table (backend/app/data/archetype_plan_dims.json, regenerate with
scripts/export_archetype_plan_dims.py). Resolving here — BEFORE massing —
lets the generator carve parcels matching the 3D model's real footprint, and
emitting the resolved id on the zone keeps the frontend resolver (which
skips zones that already carry an archetype id) and the model cache in
agreement.

Parity contract: same (development_type, aesthetic, floors) inputs must pick
the same archetype id as the frontend. test_plan_archetypes.py pins this.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from app.services.plan_geometry.community_rules import FLOOR_HEIGHT_M

_DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "archetype_plan_dims.json"
_FAMILIES_PATH = Path(__file__).resolve().parents[2] / "data" / "archetype_families.json"

# Mirror of resolvePlanZoneArchetypes.ts AESTHETIC_FAMILIES — keep in sync.
AESTHETIC_FAMILIES: dict[str, list[str]] = {
    "european": ["parisian", "haussmann", "amsterdam", "mediterranean", "neoclassical", "classical"],
    "heritage": ["historical", "brownstone", "industrial_brick", "traditional_vernacular", "neoclassical", "romanesque"],
    "historic": ["historical", "brownstone", "traditional_vernacular", "neoclassical", "romanesque"],
    "modern": ["contemporary_urban", "contemporary_midrise", "modernist", "minimalist", "glass_tower_modern"],
    "contemporary": ["contemporary_urban", "contemporary_midrise", "japanese_contemporary", "modernist"],
    "nordic": ["scandinavian_nordic"],
    "scandinavian": ["scandinavian_nordic"],
    "green": ["eco_urban_green_architecture", "biophilic"],
    "sustainable": ["eco_urban_green_architecture", "biophilic"],
    "industrial": ["industrial_brick", "daylight_factory", "machine_aesthetic"],
}

# Absolute sanity clamps for parcel targets (metres).
MIN_TARGET_M = 8.0
MAX_TARGET_M = 90.0


def _norm(value: object) -> str:
    return re.sub(r"[\s\-]+", "_", str(value if value is not None else "").lower().strip())


@lru_cache(maxsize=1)
def load_dims_table() -> list[dict]:
    payload = json.loads(_DATA_PATH.read_text(encoding="utf-8"))
    entries = payload.get("archetypes") or []
    if not entries:
        raise RuntimeError(f"archetype dims table empty/missing: {_DATA_PATH}")
    return entries


@lru_cache(maxsize=1)
def dims_by_id() -> dict[str, dict]:
    return {e["id"]: e for e in load_dims_table()}


@lru_cache(maxsize=1)
def load_families() -> dict:
    """Coherence knowledge base (scripts/build_archetype_families.py).

    {"families": {name: {region, character, compatible, universal?, streets,
    parks}}, "archetypes": {archetype_id: family}}. Missing file degrades to
    empty (coherence checks become no-ops) — the draw never depends on it."""
    try:
        return json.loads(_FAMILIES_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"families": {}, "archetypes": {}}


def family_of(archetype_id: str | None) -> str | None:
    if not archetype_id:
        return None
    return load_families().get("archetypes", {}).get(archetype_id)


def compatible_families(family: str) -> frozenset[str]:
    """The family itself + its curated neighbors + every universal family."""
    data = load_families().get("families", {})
    spec = data.get(family) or {}
    allowed = {family, *spec.get("compatible", [])}
    allowed.update(name for name, s in data.items() if s.get("universal"))
    return frozenset(allowed)


def variants_of(archetype_id: str | None) -> tuple[str, ...]:
    if not archetype_id:
        return ()
    entry = dims_by_id().get(archetype_id) or {}
    return tuple(entry.get("variant_ids") or ())


def _stable_pick(candidates: list[dict]) -> dict | None:
    if not candidates:
        return None
    return sorted(candidates, key=lambda e: (0 if e.get("has_variants") else 1, e["id"]))[0]


def resolve_building_archetype(
    development_type: object, aesthetic: object, floors: object,
    prefer_family: str | None = None,
) -> dict | None:
    """Port of resolveBuilding (resolvePlanZoneArchetypes.ts:79-137).

    prefer_family narrows the final pool to the declared style family (and its
    compatible neighbors) when any member survives the type/aesthetic/floor
    filters — the coherence lever that stops _stable_pick's lexicographic
    tiebreak from mixing a Kyoto machiya into a Calgary district. Default None
    is byte-identical to the frontend resolver (parity pinned by
    test_plan_archetypes.py)."""
    table = load_dims_table()
    dev_type = _norm(development_type) or "mixed_use"
    aesthetic_n = _norm(aesthetic)
    try:
        floors_n = int(float(floors))  # type: ignore[arg-type]
    except (TypeError, ValueError):
        floors_n = 0
    if floors_n <= 0:
        floors_n = 4

    pool = [e for e in table if e["usable"] and _norm(e["development_type"]) == dev_type]
    if not pool:
        pool = [
            e
            for e in table
            if e["usable"]
            and (
                _norm(e["development_type"]).startswith(f"{dev_type}_")
                or dev_type.startswith(f"{_norm(e['development_type'])}_")
            )
        ]
    if not pool:
        pool = [e for e in table if e["usable"] and _norm(e["development_type"]) == "mixed_use"]
    if not pool:
        return None

    if aesthetic_n:
        def _cat(e: dict) -> str:
            return _norm(e["aesthetic_category"])

        direct = [e for e in pool if _cat(e) and (aesthetic_n in _cat(e) or _cat(e) in aesthetic_n)]
        if direct:
            pool = direct
        else:
            family_terms = [
                term
                for family, terms in AESTHETIC_FAMILIES.items()
                if family in aesthetic_n or aesthetic_n in family
                for term in terms
            ]
            if family_terms:
                familial = [
                    e
                    for e in pool
                    if _cat(e) and any(t in _cat(e) or _cat(e) in t for t in family_terms)
                ]
                if familial:
                    pool = familial

    def _min_f(e: dict) -> float:
        return e["min_floors"] if e["min_floors"] is not None else 1

    def _max_f(e: dict) -> float:
        return e["max_floors"] if e["max_floors"] is not None else 999

    in_range = [e for e in pool if _min_f(e) <= floors_n <= _max_f(e)]
    if in_range:
        pool = in_range
    else:
        def _distance(e: dict) -> float:
            return min(abs(_min_f(e) - floors_n), abs(_max_f(e) - floors_n))

        best = min(_distance(e) for e in pool)
        pool = [e for e in pool if _distance(e) == best]

    if prefer_family:
        allowed = compatible_families(prefer_family)
        in_family = [e for e in pool if family_of(e["id"]) in allowed]
        if in_family:
            # Exact family beats compatible neighbors when both survived.
            exact = [e for e in in_family if family_of(e["id"]) == prefer_family]
            pool = exact or in_family

    return _stable_pick(pool)


@dataclass(frozen=True)
class TargetFootprint:
    # width = FRONTAGE (along the street / bar axis), depth = perpendicular.
    # NOT normalized long/short: a rowhouse module is 8m wide x 12m deep and
    # must be cut every 8m along the bar — swapping would slice it sideways.
    width_m: float
    depth_m: float
    aspect: float  # width/depth as-is (may be < 1)
    source: str  # "measured" | "catalog"


@dataclass(frozen=True)
class MeasuredEntry:
    variant_id: str
    dimensions: dict


def build_measured_dims(rows: list) -> dict[str, MeasuredEntry]:
    """Index completed cache rows -> per-archetype measured dims.

    Prefers the variant_id=="default" row (the pre-warm key) so the emitted
    variant matches the cache key later; falls back to the lexicographically
    first variant. Rows without dimension metadata are skipped.
    """
    by_arch: dict[str, list] = {}
    for row in rows:
        dims = (getattr(row, "metadata_", None) or {}).get("dimensions")
        if not dims or not dims.get("long_per_height"):
            continue
        by_arch.setdefault(row.archetype_id, []).append(row)
    out: dict[str, MeasuredEntry] = {}
    for arch, arch_rows in by_arch.items():
        arch_rows.sort(key=lambda r: (0 if r.variant_id == "default" else 1, r.variant_id))
        chosen = arch_rows[0]
        out[arch] = MeasuredEntry(
            variant_id=chosen.variant_id,
            dimensions=(chosen.metadata_ or {})["dimensions"],
        )
    return out


def _clamp(value: float, lo: float | None, hi: float | None) -> float:
    if lo is not None:
        value = max(value, lo)
    if hi is not None:
        value = min(value, hi)
    return max(MIN_TARGET_M, min(MAX_TARGET_M, value))


def target_footprint(
    entry: dict, floors: int, measured: dict[str, MeasuredEntry] | None = None
) -> TargetFootprint | None:
    """Target parcel W×D for an archetype at a floor count.

    Measured cache dims win (converted to metres via the same height
    anchoring the globe placement uses: height = floors × FLOOR_HEIGHT_M),
    clamped to the catalog's min/max envelope; else catalog suggested W×D.
    """
    m = (measured or {}).get(entry["id"])
    if m:
        # GLB long side ~ frontage: archetype cards depict street-facing
        # rows/facades, so the model's long axis fronts the street.
        height_m = max(1.0, floors) * FLOOR_HEIGHT_M
        width = _clamp(height_m * m.dimensions["long_per_height"], entry.get("min_w_m"), entry.get("max_w_m"))
        depth = _clamp(height_m * m.dimensions["short_per_height"], entry.get("min_d_m"), entry.get("max_d_m"))
        return TargetFootprint(round(width, 2), round(depth, 2), round(width / depth, 3), "measured")

    sw, sd = entry.get("suggested_w_m"), entry.get("suggested_d_m")
    if sw and sd:
        # Catalog width/depth are already frontage x depth — keep as-is.
        width = _clamp(sw, entry.get("min_w_m"), entry.get("max_w_m"))
        depth = _clamp(sd, entry.get("min_d_m"), entry.get("max_d_m"))
        return TargetFootprint(round(width, 2), round(depth, 2), round(width / depth, 3), "catalog")

    return None
