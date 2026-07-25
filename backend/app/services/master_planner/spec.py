"""MasterPlanSpec — the contract between the Master Planner LLM and the engine.

Everything here is pure and deterministic: pydantic models for what the agent
may express, allowlists for every direct-archetype reference (a hallucinated
id would silently skip the frontend resolver and render nothing), validation
that repairs an imperfect spec toward the scenario's preset palette instead of
failing the draw, and the conversion to a placement.Palette the geometry
engine already understands.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from pydantic import BaseModel, Field

from app.services.plan_geometry.archetypes import (
    _norm,
    compatible_families,
    dims_by_id,
    family_of,
    load_dims_table,
    load_families,
    resolve_building_archetype,
)
from app.services.plan_geometry.placement import BandSpec, Palette, palette_for

BAND_KEYS = ("core", "frontage", "mid", "edge", "anchor")
TYPOLOGIES = ("perimeter_block", "point_towers", "row_bars", "anchor_mass")
LAYOUT_STRATEGIES = ("transect_green", "urban_grid", "courtyard_focus")

MAX_FLOORS = 40.0
MAX_ALTERNATES = 3
BLOCK_TARGET_MIN_M = 60.0
BLOCK_TARGET_MAX_M = 180.0

# Direct road_archetype_id allowlists (streetPathArchetypes.json). The spine
# set keeps to >=22 m main-street characters; locals to 10-15 m residential
# characters — the width bands the resolver would otherwise pick from.
SPINE_STREET_IDS = frozenset({
    "arterial_boulevard", "haussmann_boulevard", "main_street_complete",
    "downtown_thoroughfare", "neighborhood_main_street",
    "montreal_commercial_boulevard", "toronto_streetcar_street",
    "light_rail_tram_avenue", "scenic_parkway",
})
LOCAL_STREET_IDS = frozenset({
    "narrow_residential_street", "yield_street", "woonerf_shared_street",
    "toronto_victorian_residential_street", "montreal_plateau_residential_rue",
    "new_york_brownstone_side_street", "vancouver_cherry_blossom_street",
    "london_terrace_street", "green_alley",
})
CRESCENT_STREET_IDS = frozenset({"london_crescent_road"})

WATER_ARCHETYPE_IDS = frozenset({
    "fountain_water_feature", "stormwater_retention_pond", "pond_lake",
    "wetland_rain_garden", "canal_waterway",
})
# Direct ids safe for the signature central green at any plausible area
# (openSpaceArchetypes.json) — None lets the frontend resolve by area band.
CENTRAL_PARK_IDS = frozenset({
    "neighborhood_park", "community_park", "urban_forest", "botanical_garden",
    "japanese_garden", "london_garden_square", "parisian_jardin",
    "amsterdam_vondelpark", "market_square", "amphitheater_lawn",
})

# Planting-structure vocabulary — mirrored by the globe's parkScatter
# (frontend/src/components/viewer/globe/parkScatter.ts). Keep in sync.
PARK_STRUCTURES = ("formal_allee", "naturalistic_grove", "open_meadow", "active_recreation")
COURTYARD_STRUCTURES = ("formal_quad", "garden_courtyard", "paved_plaza")
LINEAR_STRUCTURES = ("formal_allee", "naturalistic_grove", "buffer_edge")
POCKET_STRUCTURES = PARK_STRUCTURES + COURTYARD_STRUCTURES

class BandAlternate(BaseModel):
    development_type: str
    aesthetic: str = ""
    # Exact catalog archetype (optional). Validated against the dims table.
    archetype_id: str | None = None


class BandPlan(BaseModel):
    development_type: str
    aesthetic: str = ""
    # No range constraint here: an out-of-range value from the LLM must be
    # REPAIRED by validate_spec (clamped), not fail the whole composition.
    floors: float = 4.0
    typology: str = "perimeter_block"
    # Exact catalog archetype (optional) — the planner may name the building.
    archetype_id: str | None = None
    alternates: list[BandAlternate] = Field(default_factory=list)


class OpenSpaceProgram(BaseModel):
    water_feature: bool = False
    formal_water: bool = False
    water_archetype_id: str = "stormwater_retention_pond"
    plaza: bool = False
    central_park_archetype_id: str | None = None


class LandscapePlan(BaseModel):
    park_structure: str = "naturalistic_grove"
    pocket_structure: str = "garden_courtyard"
    courtyard_structure: str = "garden_courtyard"
    greenway_structure: str = "formal_allee"
    rationale: str = ""


class MasterPlanSpec(BaseModel):
    design_narrative: str = ""
    # Declared palette family (archetype_families.json). All band characters
    # must belong to this family or a compatible one — the anti-mashup rule.
    style_family: str | None = None
    layout_strategy: str = "transect_green"
    # Urban grain: the preferred block edge in metres. Drives internal street
    # spacing; the engine still guarantees no block edge exceeds ~1.15x this.
    # ~70-100 m = fine walkable inner-city grain, ~110-140 m = generous/grand.
    # None keeps the scenario default. Clamped in validation.
    block_target_m: float | None = None
    curvilinear: bool = False
    laneways: bool = False
    spine_archetype_id: str | None = None
    local_archetype_id: str | None = None
    crescent_archetype_id: str | None = None
    # Typology for the degenerate one-block site (no street grid fits). None
    # keeps the historic perimeter courtyard.
    single_block_typology: str | None = None
    bands: dict[str, BandPlan] = Field(default_factory=dict)
    open_space: OpenSpaceProgram = Field(default_factory=OpenSpaceProgram)
    landscape: LandscapePlan = Field(default_factory=LandscapePlan)


@lru_cache(maxsize=1)
def known_development_types() -> frozenset[str]:
    return frozenset(_norm(e["development_type"]) for e in load_dims_table() if e["usable"])


def _note(code: str, message: str) -> dict[str, Any]:
    return {"code": code, "severity": "info", "message": message,
            "source_phase": "master_planner"}


def validate_spec(
    spec: MasterPlanSpec, scenario_id: str, palette_hint: str | None = None
) -> tuple[MasterPlanSpec, list[dict[str, Any]]]:
    """Repair a spec in place of rejecting it — a drawable plan with notes
    beats a failed scenario. Invalid band entries fall back to the scenario's
    preset palette band; invalid direct ids fall back to band resolution."""
    notes: list[dict[str, Any]] = []
    dev_types = known_development_types()
    catalog = dims_by_id()

    def _gate_id(aid: str | None, where: str) -> str | None:
        if aid is None:
            return None
        entry = catalog.get(aid)
        if entry is None or not entry.get("usable"):
            notes.append(_note(
                "MASTER_PLAN_ID_DROPPED",
                f"{where} archetype_id '{aid}' is not a usable catalog id — resolved by type/aesthetic instead.",
            ))
            return None
        return aid

    bands: dict[str, BandPlan] = {}
    for key in BAND_KEYS:
        band = spec.bands.get(key)
        if band is None:
            notes.append(_note("MASTER_PLAN_BAND_DEFAULTED", f"Band '{key}' missing — preset character kept."))
            continue
        repaired = band.model_copy(deep=True)
        repaired.archetype_id = _gate_id(band.archetype_id, f"Band '{key}'")
        if repaired.archetype_id:
            # An explicit archetype pins its own type/aesthetic — the planner
            # named the building; the band fields must agree with the catalog.
            entry = catalog[repaired.archetype_id]
            repaired.development_type = _norm(entry["development_type"])
            repaired.aesthetic = _norm(entry["aesthetic_category"])
        elif _norm(band.development_type) in dev_types:
            repaired.development_type = _norm(band.development_type)
            repaired.aesthetic = _norm(band.aesthetic)
        else:
            notes.append(_note(
                "MASTER_PLAN_BAND_REPAIRED",
                f"Band '{key}' development_type '{band.development_type}' is not in the catalog — preset character kept.",
            ))
            continue
        repaired.floors = min(MAX_FLOORS, max(1.0, float(band.floors)))
        if repaired.typology not in TYPOLOGIES:
            notes.append(_note(
                "MASTER_PLAN_TYPOLOGY_REPAIRED",
                f"Band '{key}' typology '{band.typology}' unknown — perimeter_block used.",
            ))
            repaired.typology = "perimeter_block"
        kept_alts: list[BandAlternate] = []
        for alt in repaired.alternates[: MAX_ALTERNATES * 2]:
            alt_id = _gate_id(alt.archetype_id, f"Band '{key}' alternate")
            if alt_id:
                entry = catalog[alt_id]
                kept_alts.append(BandAlternate(
                    development_type=_norm(entry["development_type"]),
                    aesthetic=_norm(entry["aesthetic_category"]),
                    archetype_id=alt_id,
                ))
            elif _norm(alt.development_type) in dev_types:
                kept_alts.append(BandAlternate(
                    development_type=_norm(alt.development_type), aesthetic=_norm(alt.aesthetic),
                ))
            else:
                notes.append(_note(
                    "MASTER_PLAN_ALTERNATE_DROPPED",
                    f"Band '{key}' alternate '{alt.development_type}' is not in the catalog — dropped.",
                ))
                continue
            if len(kept_alts) >= MAX_ALTERNATES:
                break
        repaired.alternates = kept_alts
        bands[key] = repaired

    # ── Coherence: one style family per district (the anti-mashup rule) ──────
    families_known = set(load_families().get("families", {}))
    family = spec.style_family if spec.style_family in families_known else None
    if spec.style_family and family is None:
        notes.append(_note(
            "MASTER_PLAN_FAMILY_UNKNOWN",
            f"style_family '{spec.style_family}' is not in the knowledge base — inferring from the palette.",
        ))

    def _resolved_family(dev: str, aes: str, floors: float, aid: str | None) -> str | None:
        if aid:
            return family_of(aid)
        entry = resolve_building_archetype(dev, aes, max(1, int(round(floors))),
                                           prefer_family=family)
        return family_of(entry["id"]) if entry else None

    if family is None and bands:
        votes = [f for f in (
            _resolved_family(b.development_type, b.aesthetic, b.floors, b.archetype_id)
            for b in bands.values()
        ) if f]
        if votes:
            family = sorted(set(votes), key=lambda f: (-votes.count(f), f))[0]
            notes.append(_note(
                "MASTER_PLAN_FAMILY_INFERRED",
                f"style_family inferred as '{family}' from the band palette.",
            ))

    if family:
        allowed = compatible_families(family)
        for key, band in bands.items():
            band_fam = _resolved_family(band.development_type, band.aesthetic,
                                        band.floors, band.archetype_id)
            if band_fam and band_fam not in allowed:
                notes.append(_note(
                    "MASTER_PLAN_COHERENCE_REPAIRED",
                    f"Band '{key}' resolves to family '{band_fam}', incompatible with "
                    f"'{family}' — explicit id dropped; family-aware resolution applies.",
                ))
                band.archetype_id = None
            kept: list[BandAlternate] = []
            for alt in band.alternates:
                alt_fam = _resolved_family(alt.development_type, alt.aesthetic,
                                           band.floors, alt.archetype_id)
                if alt_fam and alt_fam not in allowed:
                    notes.append(_note(
                        "MASTER_PLAN_COHERENCE_REPAIRED",
                        f"Band '{key}' alternate '{alt.archetype_id or alt.development_type}' is "
                        f"family '{alt_fam}', incompatible with '{family}' — dropped.",
                    ))
                    continue
                kept.append(alt)
            band.alternates = kept

    def _gate(value: str | None, allowed: frozenset[str], what: str) -> str | None:
        if value is None or value in allowed:
            return value
        notes.append(_note("MASTER_PLAN_ID_DROPPED", f"{what} '{value}' is not an allowed archetype id — band resolution kept."))
        return None

    open_space = spec.open_space.model_copy(deep=True)
    if open_space.water_archetype_id not in WATER_ARCHETYPE_IDS:
        notes.append(_note(
            "MASTER_PLAN_ID_DROPPED",
            f"water_archetype_id '{open_space.water_archetype_id}' not allowed — stormwater_retention_pond used.",
        ))
        open_space.water_archetype_id = "stormwater_retention_pond"
    open_space.central_park_archetype_id = _gate(
        open_space.central_park_archetype_id, CENTRAL_PARK_IDS, "central_park_archetype_id",
    )

    landscape = spec.landscape.model_copy(deep=True)
    for attr, allowed, fallback in (
        ("park_structure", PARK_STRUCTURES, "naturalistic_grove"),
        ("pocket_structure", POCKET_STRUCTURES, "garden_courtyard"),
        ("courtyard_structure", COURTYARD_STRUCTURES, "garden_courtyard"),
        ("greenway_structure", LINEAR_STRUCTURES, "formal_allee"),
    ):
        if getattr(landscape, attr) not in allowed:
            notes.append(_note(
                "MASTER_PLAN_LANDSCAPE_REPAIRED",
                f"landscape.{attr} '{getattr(landscape, attr)}' unknown — {fallback} used.",
            ))
            setattr(landscape, attr, fallback)

    single_block = spec.single_block_typology
    if single_block is not None and single_block not in TYPOLOGIES:
        notes.append(_note(
            "MASTER_PLAN_TYPOLOGY_REPAIRED",
            f"single_block_typology '{single_block}' unknown — perimeter courtyard kept.",
        ))
        single_block = None

    strategy = spec.layout_strategy if spec.layout_strategy in LAYOUT_STRATEGIES else "transect_green"
    if strategy != spec.layout_strategy:
        notes.append(_note("MASTER_PLAN_STRATEGY_REPAIRED",
                           f"layout_strategy '{spec.layout_strategy}' unknown — transect_green used."))

    block_target = spec.block_target_m
    if block_target is not None:
        clamped = min(BLOCK_TARGET_MAX_M, max(BLOCK_TARGET_MIN_M, float(block_target)))
        if clamped != float(block_target):
            notes.append(_note("MASTER_PLAN_GRAIN_CLAMPED",
                               f"block_target_m {block_target:g} clamped to {clamped:g} m."))
        block_target = clamped

    validated = MasterPlanSpec(
        design_narrative=str(spec.design_narrative or "")[:2000],
        style_family=family,
        layout_strategy=strategy,
        block_target_m=block_target,
        curvilinear=bool(spec.curvilinear),
        laneways=bool(spec.laneways),
        spine_archetype_id=_gate(spec.spine_archetype_id, SPINE_STREET_IDS, "spine_archetype_id"),
        local_archetype_id=_gate(spec.local_archetype_id, LOCAL_STREET_IDS, "local_archetype_id"),
        crescent_archetype_id=_gate(spec.crescent_archetype_id, CRESCENT_STREET_IDS, "crescent_archetype_id"),
        single_block_typology=single_block,
        bands=bands,
        open_space=open_space,
        landscape=landscape,
    )
    return validated, notes


def palette_from_spec(
    spec: MasterPlanSpec,
    scenario_id: str,
    palette_hint: str | None = None,
) -> Palette:
    """MasterPlanSpec -> the Palette the placement policy executes.

    Bands the planner didn't (validly) author keep the preset's BandSpec —
    including its relative-floors behavior — so a partial spec degrades to
    the familiar scenario character instead of a surprise. Alternates stay
    raw (type, aesthetic) pairs: plan_blocks resolves them at the block's
    FINAL floor count (context caps can move it), the one place archetype
    resolution already lives.
    """
    preset = palette_for(scenario_id, palette_hint)
    bands: dict[str, BandSpec] = {}
    alternates: dict[str, tuple[tuple[str, str, str | None], ...]] = {}
    for key in BAND_KEYS:
        band = spec.bands.get(key)
        if band is None:
            bands[key] = preset.bands[key]
            continue
        bands[key] = BandSpec(
            development_type=band.development_type,
            aesthetic=band.aesthetic,
            floors_delta=None,
            floors_abs=float(band.floors),
            typology=band.typology,
            archetype_id=band.archetype_id,
        )
        triples = tuple(dict.fromkeys(
            (alt.development_type, alt.aesthetic, alt.archetype_id)
            for alt in band.alternates
        ))
        if triples:
            alternates[key] = triples

    return Palette(
        bands=bands,
        style_family=spec.style_family,
        spine_archetype_id=spec.spine_archetype_id,
        water_feature=spec.open_space.water_feature,
        plaza=spec.open_space.plaza,
        laneways=spec.laneways,
        context_match=preset.context_match,
        local_archetype_id=spec.local_archetype_id,
        water_archetype_id=spec.open_space.water_archetype_id,
        formal_water=spec.open_space.formal_water,
        curvilinear=spec.curvilinear,
        crescent_archetype_id=spec.crescent_archetype_id,
        alternates=alternates,
        landscape={
            "park": spec.landscape.park_structure,
            "pocket": spec.landscape.pocket_structure,
            "courtyard": spec.landscape.courtyard_structure,
            "greenway": spec.landscape.greenway_structure,
            "plaza": "formal_allee",
        },
        central_archetype_id=spec.open_space.central_park_archetype_id,
        single_block_typology=spec.single_block_typology,
    )
