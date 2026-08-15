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
from typing import Any, Literal

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
from app.services.master_planner.lego_catalog import (
    LegoArchetypeCapability,
    LegoPlanningCatalog,
    select_lego_archetype,
)
from app.services.public_realm_lego import build_public_realm_capability_catalog
from app.services.public_realm_catalog import (
    resolve_public_realm_catalog_identity,
)
from app.services.plan_geometry.placement import BandSpec, Palette, palette_for

BAND_KEYS = ("core", "frontage", "mid", "edge", "anchor")
TYPOLOGIES = ("perimeter_block", "point_towers", "row_bars", "anchor_mass")
LAYOUT_STRATEGIES = ("transect_green", "urban_grid", "courtyard_focus")

MAX_FLOORS = 40.0
MAX_ALTERNATES = 3
BLOCK_TARGET_MIN_M = 60.0
BLOCK_TARGET_MAX_M = 180.0
NEIGHBORHOOD_DIVERSITY_MIN_AREA_M2 = 15_000.0
DISTRICT_DIVERSITY_MIN_AREA_M2 = 50_000.0
NEIGHBORHOOD_DIVERSITY_MIN_BLOCKS = 3
DISTRICT_DIVERSITY_MIN_BLOCKS = 8

# Direct road_archetype_id allowlists (streetPathArchetypes.json). The spine
# set keeps to >=22 m main-street characters; locals to 10-15 m residential
# characters — the width bands the resolver would otherwise pick from.
SPINE_STREET_IDS = frozenset(
    {
        "arterial_boulevard",
        "haussmann_boulevard",
        "main_street_complete",
        "downtown_thoroughfare",
        "neighborhood_main_street",
        "montreal_commercial_boulevard",
        "toronto_streetcar_street",
        "light_rail_tram_avenue",
        "scenic_parkway",
    }
)
LOCAL_STREET_IDS = frozenset(
    {
        "narrow_residential_street",
        "yield_street",
        "woonerf_shared_street",
        "toronto_victorian_residential_street",
        "montreal_plateau_residential_rue",
        "new_york_brownstone_side_street",
        "vancouver_cherry_blossom_street",
        "london_terrace_street",
        "green_alley",
        "toronto_laneway",
        "calgary_local",
    }
)
CRESCENT_STREET_IDS = frozenset({"london_crescent_road"})

WATER_ARCHETYPE_IDS = frozenset(
    {
        "fountain_water_feature",
        "stormwater_retention_pond",
        "pond_lake",
        "wetland_rain_garden",
        "canal_waterway",
    }
)
# Direct ids safe for the signature central green at any plausible area
# (openSpaceArchetypes.json) — None lets the frontend resolve by area band.
CENTRAL_PARK_IDS = frozenset(
    {
        "neighborhood_park",
        "community_park",
        "urban_forest",
        "botanical_garden",
        "japanese_garden",
        "london_garden_square",
        "parisian_jardin",
        "amsterdam_vondelpark",
        "market_square",
        "amphitheater_lawn",
    }
)

# LEGO-backed plans may express the whole trusted visual catalogue. The
# compiler decides whether each selected identity has an exact kit or uses the
# family-pending source-fitted fallback; validation must never re-home intent.
LEGO_SPINE_STREET_IDS = SPINE_STREET_IDS
LEGO_LOCAL_STREET_IDS = LOCAL_STREET_IDS
LEGO_CENTRAL_PARK_IDS = CENTRAL_PARK_IDS
LEGO_WATER_ARCHETYPE_IDS = frozenset({"stormwater_retention_pond"})

# One authoritative server catalog supplies both validation and recipe
# compilation. A family addition cannot become selectable in the planner
# without simultaneously existing in the strict compiler.
PUBLIC_REALM_VARIANTS_BY_ARCHETYPE: dict[str, tuple[str, ...]] = dict(
    build_public_realm_capability_catalog().variants_by_archetype
)

SPINE_PUBLIC_REALM_VARIANT_IDS = PUBLIC_REALM_VARIANTS_BY_ARCHETYPE["main_street_complete"]
LOCAL_PUBLIC_REALM_VARIANT_IDS = tuple(
    variant
    for archetype_id in sorted(LEGO_LOCAL_STREET_IDS)
    for variant in PUBLIC_REALM_VARIANTS_BY_ARCHETYPE.get(archetype_id, ())
)
CENTRAL_PARK_VARIANT_IDS = tuple(
    variant
    for archetype_id in sorted(LEGO_CENTRAL_PARK_IDS)
    for variant in PUBLIC_REALM_VARIANTS_BY_ARCHETYPE.get(archetype_id, ())
)
POCKET_PARK_VARIANT_IDS = PUBLIC_REALM_VARIANTS_BY_ARCHETYPE["urban_pocket_park"]
GREENWAY_VARIANT_IDS = PUBLIC_REALM_VARIANTS_BY_ARCHETYPE["linear_park_greenway"]

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
    # Exact executable child identity for fixed/variant-only LEGO families.
    variant_id: str | None = None


class BandPlan(BaseModel):
    development_type: str
    aesthetic: str = ""
    # No range constraint here: an out-of-range value from the LLM must be
    # REPAIRED by validate_spec (clamped), not fail the whole composition.
    floors: float = 4.0
    typology: str = "perimeter_block"
    # Exact catalog archetype (optional) — the planner may name the building.
    archetype_id: str | None = None
    # Exact executable child identity when the parent alias itself cannot plan.
    variant_id: str | None = None
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


class PublicRealmPlan(BaseModel):
    """Visible variants for the first executable park/street family cohort.

    Archetype IDs continue to carry planning intent. These identities select a
    bounded appearance/configuration within the compatible family and are
    validated again when the server compiles the metric public-realm recipe.
    """

    spine_street_variant_id: str | None = None
    local_street_variant_id: str | None = None
    central_park_variant_id: str | None = None
    pocket_park_variant_id: str | None = None
    courtyard_variant_id: str | None = None
    greenway_variant_id: str | None = None
    rationale: str = ""


class PlanDiversity(BaseModel):
    """Size-aware minimum character palette retained by deterministic planning.

    A compact infill site may truthfully be one architectural ensemble. Larger
    sites need several compatible hands and repeated public-realm roles need
    visible variation. These targets are derived from geometry, never authored
    by the LLM, and are capped by the executable catalog actually installed.
    """

    scale: Literal["compact", "neighborhood", "district"] = "compact"
    building_characters_per_band: int = Field(default=1, ge=1, le=4)
    park_characters: int = Field(default=1, ge=1, le=4)
    street_characters: int = Field(default=1, ge=1, le=4)
    max_repeat_share: float = Field(default=1.0, ge=0.25, le=1.0)


def diversity_plan_for_site(site_summary: dict[str, Any] | None) -> PlanDiversity:
    """Translate site area/block capacity into a deterministic variety floor."""

    summary = site_summary or {}
    area_m2 = max(0.0, float(summary.get("area_m2") or 0.0))
    try:
        estimated_blocks = max(0, int(summary.get("est_blocks") or 0))
    except (TypeError, ValueError):
        estimated_blocks = 0
    if area_m2 >= DISTRICT_DIVERSITY_MIN_AREA_M2 or estimated_blocks >= DISTRICT_DIVERSITY_MIN_BLOCKS:
        return PlanDiversity(
            scale="district",
            building_characters_per_band=3,
            park_characters=3,
            street_characters=3,
            max_repeat_share=0.5,
        )
    if area_m2 >= NEIGHBORHOOD_DIVERSITY_MIN_AREA_M2 or estimated_blocks >= NEIGHBORHOOD_DIVERSITY_MIN_BLOCKS:
        return PlanDiversity(
            scale="neighborhood",
            building_characters_per_band=2,
            park_characters=2,
            street_characters=2,
            max_repeat_share=0.7,
        )
    return PlanDiversity()


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
    public_realm: PublicRealmPlan = Field(default_factory=PublicRealmPlan)
    diversity: PlanDiversity = Field(default_factory=PlanDiversity)


@lru_cache(maxsize=1)
def known_development_types() -> frozenset[str]:
    return frozenset(_norm(e["development_type"]) for e in load_dims_table() if e["usable"])


def _note(code: str, message: str) -> dict[str, Any]:
    return {"code": code, "severity": "info", "message": message, "source_phase": "master_planner"}


def _public_realm_variant(
    value: str | None,
    *,
    archetype_id: str,
    kind: Literal["park", "street"],
    field_name: str,
    notes: list[dict[str, Any]],
) -> str | None:
    allowed = PUBLIC_REALM_VARIANTS_BY_ARCHETYPE.get(archetype_id, ())
    if value in allowed:
        return value
    if not allowed and value is None:
        return None
    if (
        not allowed
        and value is not None
        and resolve_public_realm_catalog_identity(
            kind,
            archetype_id,
            value,
        )
        is not None
    ):
        return value
    if value is not None:
        resolution = f"{allowed[0]} used" if allowed else "variant selection removed"
        notes.append(
            _note(
                "MASTER_PLAN_PUBLIC_REALM_VARIANT_REPAIRED",
                f"public_realm.{field_name} '{value}' is not compatible with " f"'{archetype_id}' - {resolution}.",
            )
        )
    return allowed[0] if allowed else None


def _validated_public_realm_plan(
    requested: PublicRealmPlan,
    *,
    spine_archetype_id: str | None,
    local_archetype_id: str | None,
    central_park_archetype_id: str | None,
    notes: list[dict[str, Any]],
) -> PublicRealmPlan:
    spine_id = spine_archetype_id if spine_archetype_id in SPINE_STREET_IDS else "main_street_complete"
    local_id = local_archetype_id if local_archetype_id in LOCAL_STREET_IDS else "narrow_residential_street"
    central_id = central_park_archetype_id if central_park_archetype_id in CENTRAL_PARK_IDS else "neighborhood_park"
    return PublicRealmPlan(
        spine_street_variant_id=_public_realm_variant(
            requested.spine_street_variant_id,
            archetype_id=spine_id,
            kind="street",
            field_name="spine_street_variant_id",
            notes=notes,
        ),
        local_street_variant_id=_public_realm_variant(
            requested.local_street_variant_id,
            archetype_id=local_id,
            kind="street",
            field_name="local_street_variant_id",
            notes=notes,
        ),
        central_park_variant_id=_public_realm_variant(
            requested.central_park_variant_id,
            archetype_id=central_id,
            kind="park",
            field_name="central_park_variant_id",
            notes=notes,
        ),
        pocket_park_variant_id=_public_realm_variant(
            requested.pocket_park_variant_id,
            archetype_id="urban_pocket_park",
            kind="park",
            field_name="pocket_park_variant_id",
            notes=notes,
        ),
        courtyard_variant_id=_public_realm_variant(
            requested.courtyard_variant_id,
            archetype_id="urban_pocket_park",
            kind="park",
            field_name="courtyard_variant_id",
            notes=notes,
        ),
        greenway_variant_id=_public_realm_variant(
            requested.greenway_variant_id,
            archetype_id="linear_park_greenway",
            kind="park",
            field_name="greenway_variant_id",
            notes=notes,
        ),
        rationale=str(requested.rationale or "")[:1000],
    )


def validate_spec(
    spec: MasterPlanSpec,
    scenario_id: str,
    palette_hint: str | None = None,
    lego_catalog: LegoPlanningCatalog | None = None,
) -> tuple[MasterPlanSpec, list[dict[str, Any]]]:
    """Repair a spec in place of rejecting it — a drawable plan with notes
    beats a failed scenario. Invalid band entries fall back to the scenario's
    preset palette band; invalid direct ids fall back to band resolution."""
    if lego_catalog is not None:
        return _validate_spec_with_lego(spec, scenario_id, palette_hint, lego_catalog)

    notes: list[dict[str, Any]] = []
    dev_types = known_development_types()
    catalog = dims_by_id()

    def _gate_id(aid: str | None, where: str) -> str | None:
        if aid is None:
            return None
        entry = catalog.get(aid)
        if entry is None or not entry.get("usable"):
            notes.append(
                _note(
                    "MASTER_PLAN_ID_DROPPED",
                    f"{where} archetype_id '{aid}' is not a usable catalog id — resolved by type/aesthetic instead.",
                )
            )
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
            notes.append(
                _note(
                    "MASTER_PLAN_BAND_REPAIRED",
                    f"Band '{key}' development_type '{band.development_type}' is not in the catalog — preset character kept.",
                )
            )
            continue
        repaired.floors = min(MAX_FLOORS, max(1.0, float(band.floors)))
        if repaired.typology not in TYPOLOGIES:
            notes.append(
                _note(
                    "MASTER_PLAN_TYPOLOGY_REPAIRED",
                    f"Band '{key}' typology '{band.typology}' unknown — perimeter_block used.",
                )
            )
            repaired.typology = "perimeter_block"
        kept_alts: list[BandAlternate] = []
        for alt in repaired.alternates[: MAX_ALTERNATES * 2]:
            alt_id = _gate_id(alt.archetype_id, f"Band '{key}' alternate")
            if alt_id:
                entry = catalog[alt_id]
                kept_alts.append(
                    BandAlternate(
                        development_type=_norm(entry["development_type"]),
                        aesthetic=_norm(entry["aesthetic_category"]),
                        archetype_id=alt_id,
                    )
                )
            elif _norm(alt.development_type) in dev_types:
                kept_alts.append(
                    BandAlternate(
                        development_type=_norm(alt.development_type),
                        aesthetic=_norm(alt.aesthetic),
                    )
                )
            else:
                notes.append(
                    _note(
                        "MASTER_PLAN_ALTERNATE_DROPPED",
                        f"Band '{key}' alternate '{alt.development_type}' is not in the catalog — dropped.",
                    )
                )
                continue
            if len(kept_alts) >= MAX_ALTERNATES:
                break
        repaired.alternates = kept_alts
        bands[key] = repaired

    # ── Coherence: one style family per district (the anti-mashup rule) ──────
    families_known = set(load_families().get("families", {}))
    family = spec.style_family if spec.style_family in families_known else None
    if spec.style_family and family is None:
        notes.append(
            _note(
                "MASTER_PLAN_FAMILY_UNKNOWN",
                f"style_family '{spec.style_family}' is not in the knowledge base — inferring from the palette.",
            )
        )

    def _resolved_family(dev: str, aes: str, floors: float, aid: str | None) -> str | None:
        if aid:
            return family_of(aid)
        entry = resolve_building_archetype(dev, aes, max(1, int(round(floors))), prefer_family=family)
        return family_of(entry["id"]) if entry else None

    if family is None and bands:
        votes = [
            f
            for f in (
                _resolved_family(b.development_type, b.aesthetic, b.floors, b.archetype_id) for b in bands.values()
            )
            if f
        ]
        if votes:
            family = sorted(set(votes), key=lambda f: (-votes.count(f), f))[0]
            notes.append(
                _note(
                    "MASTER_PLAN_FAMILY_INFERRED",
                    f"style_family inferred as '{family}' from the band palette.",
                )
            )

    if family:
        allowed = compatible_families(family)
        for key, band in bands.items():
            band_fam = _resolved_family(band.development_type, band.aesthetic, band.floors, band.archetype_id)
            if band_fam and band_fam not in allowed:
                notes.append(
                    _note(
                        "MASTER_PLAN_COHERENCE_REPAIRED",
                        f"Band '{key}' resolves to family '{band_fam}', incompatible with "
                        f"'{family}' — explicit id dropped; family-aware resolution applies.",
                    )
                )
                band.archetype_id = None
            kept: list[BandAlternate] = []
            for alt in band.alternates:
                alt_fam = _resolved_family(alt.development_type, alt.aesthetic, band.floors, alt.archetype_id)
                if alt_fam and alt_fam not in allowed:
                    notes.append(
                        _note(
                            "MASTER_PLAN_COHERENCE_REPAIRED",
                            f"Band '{key}' alternate '{alt.archetype_id or alt.development_type}' is "
                            f"family '{alt_fam}', incompatible with '{family}' — dropped.",
                        )
                    )
                    continue
                kept.append(alt)
            band.alternates = kept

    def _gate(value: str | None, allowed: frozenset[str], what: str) -> str | None:
        if value is None or value in allowed:
            return value
        notes.append(
            _note("MASTER_PLAN_ID_DROPPED", f"{what} '{value}' is not an allowed archetype id — band resolution kept.")
        )
        return None

    open_space = spec.open_space.model_copy(deep=True)
    if open_space.water_archetype_id not in WATER_ARCHETYPE_IDS:
        notes.append(
            _note(
                "MASTER_PLAN_ID_DROPPED",
                f"water_archetype_id '{open_space.water_archetype_id}' not allowed — stormwater_retention_pond used.",
            )
        )
        open_space.water_archetype_id = "stormwater_retention_pond"
    open_space.central_park_archetype_id = _gate(
        open_space.central_park_archetype_id,
        CENTRAL_PARK_IDS,
        "central_park_archetype_id",
    )

    landscape = spec.landscape.model_copy(deep=True)
    for attr, allowed, fallback in (
        ("park_structure", PARK_STRUCTURES, "naturalistic_grove"),
        ("pocket_structure", POCKET_STRUCTURES, "garden_courtyard"),
        ("courtyard_structure", COURTYARD_STRUCTURES, "garden_courtyard"),
        ("greenway_structure", LINEAR_STRUCTURES, "formal_allee"),
    ):
        if getattr(landscape, attr) not in allowed:
            notes.append(
                _note(
                    "MASTER_PLAN_LANDSCAPE_REPAIRED",
                    f"landscape.{attr} '{getattr(landscape, attr)}' unknown — {fallback} used.",
                )
            )
            setattr(landscape, attr, fallback)

    single_block = spec.single_block_typology
    if single_block is not None and single_block not in TYPOLOGIES:
        notes.append(
            _note(
                "MASTER_PLAN_TYPOLOGY_REPAIRED",
                f"single_block_typology '{single_block}' unknown — perimeter courtyard kept.",
            )
        )
        single_block = None

    strategy = spec.layout_strategy if spec.layout_strategy in LAYOUT_STRATEGIES else "transect_green"
    if strategy != spec.layout_strategy:
        notes.append(
            _note(
                "MASTER_PLAN_STRATEGY_REPAIRED",
                f"layout_strategy '{spec.layout_strategy}' unknown — transect_green used.",
            )
        )

    block_target = spec.block_target_m
    if block_target is not None:
        clamped = min(BLOCK_TARGET_MAX_M, max(BLOCK_TARGET_MIN_M, float(block_target)))
        if clamped != float(block_target):
            notes.append(
                _note("MASTER_PLAN_GRAIN_CLAMPED", f"block_target_m {block_target:g} clamped to {clamped:g} m.")
            )
        block_target = clamped

    spine_archetype_id = _gate(
        spec.spine_archetype_id,
        SPINE_STREET_IDS,
        "spine_archetype_id",
    )
    local_archetype_id = _gate(
        spec.local_archetype_id,
        LOCAL_STREET_IDS,
        "local_archetype_id",
    )
    crescent_archetype_id = _gate(
        spec.crescent_archetype_id,
        CRESCENT_STREET_IDS,
        "crescent_archetype_id",
    )
    # The broad/Classic contract carries no executable family promise. Keep
    # the optional block inert here; LEGO validation below owns defaults and
    # cross-family compatibility repairs.
    public_realm = spec.public_realm.model_copy(
        update={"rationale": str(spec.public_realm.rationale or "")[:1000]},
    )

    validated = MasterPlanSpec(
        design_narrative=str(spec.design_narrative or "")[:2000],
        style_family=family,
        layout_strategy=strategy,
        block_target_m=block_target,
        curvilinear=bool(spec.curvilinear),
        laneways=bool(spec.laneways),
        spine_archetype_id=spine_archetype_id,
        local_archetype_id=local_archetype_id,
        crescent_archetype_id=crescent_archetype_id,
        single_block_typology=single_block,
        bands=bands,
        open_space=open_space,
        landscape=landscape,
        public_realm=public_realm,
        diversity=spec.diversity,
    )
    return validated, notes


def _preset_band_plan(preset: Palette, key: str) -> BandPlan:
    band = preset.bands[key]
    floors = float(band.floors_abs) if band.floors_abs is not None else max(1.0, 4.0 + float(band.floors_delta or 0.0))
    return BandPlan(
        development_type=band.development_type,
        aesthetic=band.aesthetic,
        floors=floors,
        typology=band.typology,
        archetype_id=band.archetype_id,
        variant_id=band.variant_id,
    )


def _lego_capability_maps(
    lego_catalog: LegoPlanningCatalog,
) -> dict[str, LegoArchetypeCapability]:
    by_parent = {capability.parent_id: capability for capability in lego_catalog.capabilities}
    return by_parent


def _select_lego_character(
    *,
    development_type: str,
    aesthetic: str,
    floors: float,
    archetype_id: str | None,
    variant_id: str | None,
    lego_catalog: LegoPlanningCatalog,
) -> tuple[LegoArchetypeCapability, str | None, int]:
    """Resolve one requested character to an executable parent/variant/floor."""

    by_parent = _lego_capability_maps(lego_catalog)
    if not by_parent:
        raise ValueError("No executable LEGO building families are available for Master Planner.")

    requested_selectable = variant_id
    parent_id = archetype_id if archetype_id in by_parent else None
    if parent_id is None and archetype_id in lego_catalog.parent_by_selectable_id:
        parent_id = lego_catalog.parent_by_selectable_id[archetype_id]
        requested_selectable = archetype_id
    if parent_id is None and variant_id in lego_catalog.parent_by_selectable_id:
        parent_id = lego_catalog.parent_by_selectable_id[variant_id]

    if parent_id is None:
        resolved = resolve_building_archetype(
            development_type,
            aesthetic,
            floors,
            allowed_archetype_ids=lego_catalog.parent_ids,
            supported_floors_by_archetype=lego_catalog.supported_floors_by_parent,
        )
        parent_id = str(resolved["id"]) if resolved is not None else lego_catalog.parent_ids[0]

    capability = by_parent[parent_id]
    if requested_selectable not in capability.selectable_ids:
        requested_selectable = archetype_id if archetype_id in capability.selectable_ids else None
    selection = select_lego_archetype(
        lego_catalog,
        parent_id,
        floors,
        preferred_selectable_id=requested_selectable,
    )
    if selection is None:
        raise ValueError(f"LEGO archetype '{parent_id}' has no executable identity and floor pair.")
    return capability, selection.variant_id, selection.floors


def _fill_site_scaled_lego_alternates(
    bands: dict[str, BandPlan],
    *,
    diversity: PlanDiversity,
    lego_catalog: LegoPlanningCatalog,
    dimensions: dict[str, dict[str, Any]],
    notes: list[dict[str, Any]],
) -> None:
    """Guarantee a coherent alternate palette when a larger-site LLM omits it.

    Same-band rotation is the geometry engine's safe diversity mechanism: each
    block is carved to its own primary family's native footprint. We therefore
    add parents here, before placement, instead of forcing unlike authored 3D
    assets into an already-cut cell. Existing AI choices always lead; catalog
    additions merely fill the size-derived minimum when compatible inventory
    exists at the band's exact floor count.
    """

    requested_count = min(
        diversity.building_characters_per_band,
        MAX_ALTERNATES + 1,
        len(lego_catalog.capabilities),
    )
    if requested_count <= 1:
        return

    by_parent = {capability.parent_id: capability for capability in lego_catalog.capabilities}
    added = 0
    underfilled: list[str] = []
    for band_key in BAND_KEYS:
        band = bands.get(band_key)
        if band is None or band.archetype_id not in by_parent:
            continue
        # A neighborhood has one landmark anchor, not a rotating landmark row.
        target_count = min(requested_count, 2) if band_key == "anchor" else requested_count
        primary_capability = by_parent[band.archetype_id]
        primary_family = family_of(primary_capability.parent_id)
        allowed_families = compatible_families(primary_family) if primary_family else frozenset()
        existing_parents = {
            parent_id
            for parent_id in (
                band.archetype_id,
                *(alternate.archetype_id for alternate in band.alternates),
            )
            if parent_id
        }
        if len(existing_parents) >= target_count:
            continue

        primary_type = _norm(primary_capability.development_type)
        primary_aesthetic = _norm(primary_capability.aesthetic_category)
        candidates: list[tuple[tuple[int, int, int, str], LegoArchetypeCapability, str | None]] = []
        for capability in lego_catalog.capabilities:
            if capability.parent_id in existing_parents:
                continue
            selection = select_lego_archetype(
                lego_catalog,
                capability.parent_id,
                band.floors,
            )
            if selection is None or int(selection.floors) != int(round(band.floors)):
                continue
            candidate_family = family_of(capability.parent_id)
            candidate_type = _norm(capability.development_type)
            candidate_aesthetic = _norm(capability.aesthetic_category)
            same_type = candidate_type == primary_type
            related_aesthetic = bool(
                primary_aesthetic
                and candidate_aesthetic
                and (primary_aesthetic in candidate_aesthetic or candidate_aesthetic in primary_aesthetic)
            )
            if primary_family and candidate_family == primary_family:
                coherence_rank = 0
            elif primary_family and candidate_family in allowed_families:
                coherence_rank = 1
            elif same_type or related_aesthetic:
                coherence_rank = 2
            else:
                # Do not satisfy a numeric target by creating an architectural
                # mash-up. A smaller coherent executable palette is truthful.
                continue
            score = (
                coherence_rank,
                0 if same_type else 1,
                0 if related_aesthetic else 1,
                capability.parent_id,
            )
            candidates.append((score, capability, selection.variant_id))

        for _score, capability, variant_id in sorted(candidates, key=lambda item: item[0]):
            entry = dimensions.get(capability.parent_id)
            if entry is None:
                continue
            band.alternates.append(
                BandAlternate(
                    development_type=_norm(entry["development_type"]),
                    aesthetic=_norm(entry["aesthetic_category"]),
                    archetype_id=capability.parent_id,
                    variant_id=variant_id,
                )
            )
            existing_parents.add(capability.parent_id)
            added += 1
            if len(existing_parents) >= target_count or len(band.alternates) >= MAX_ALTERNATES:
                break
        if len(existing_parents) < target_count:
            underfilled.append(band_key)

    if added:
        notes.append(
            _note(
                "MASTER_PLAN_DIVERSITY_FILLED",
                f"The {diversity.scale} site diversity contract added {added} compatible "
                "LEGO building character"
                f"{'s' if added != 1 else ''} to under-specified bands.",
            )
        )
    if underfilled:
        notes.append(
            _note(
                "MASTER_PLAN_DIVERSITY_CATALOG_LIMITED",
                "The installed executable catalog cannot fully meet the "
                f"{diversity.scale} diversity target for: {', '.join(underfilled)}. "
                "The plan kept the smaller coherent palette instead of mixing incompatible families.",
            )
        )


def _validate_spec_with_lego(
    spec: MasterPlanSpec,
    scenario_id: str,
    palette_hint: str | None,
    lego_catalog: LegoPlanningCatalog,
) -> tuple[MasterPlanSpec, list[dict[str, Any]]]:
    """Validate common plan fields, then hard-bind every band to LEGO."""

    if not lego_catalog.capabilities:
        raise ValueError("No executable LEGO building families are available for Master Planner.")

    # Preserve the established validation contract for streets, landscape,
    # open space, strategy and grain. Building bands are rebuilt below. Known
    # public-realm identities are deliberately not constrained to the smaller
    # executable-kit registry: unbuilt selections compile as family-pending
    # source-fitted representations without losing the authored character.
    common, notes = validate_spec(spec, scenario_id, palette_hint)
    preset = palette_for(scenario_id, palette_hint)
    spine_archetype_id = common.spine_archetype_id or "main_street_complete"
    local_archetype_id = common.local_archetype_id or (
        preset.local_archetype_id if preset.local_archetype_id in LEGO_LOCAL_STREET_IDS else "narrow_residential_street"
    )

    open_space = common.open_space.model_copy(deep=True)
    if open_space.central_park_archetype_id is None:
        open_space.central_park_archetype_id = "neighborhood_park"

    public_realm = _validated_public_realm_plan(
        spec.public_realm,
        spine_archetype_id=spine_archetype_id,
        local_archetype_id=local_archetype_id,
        central_park_archetype_id=open_space.central_park_archetype_id,
        notes=notes,
    )
    dimensions = dims_by_id()
    repaired_bands: dict[str, BandPlan] = {}

    for key in BAND_KEYS:
        requested = spec.bands.get(key)
        if requested is None:
            requested = _preset_band_plan(preset, key)
            notes.append(
                _note(
                    "MASTER_PLAN_LEGO_BAND_FILLED",
                    f"Band '{key}' was missing — an imported LEGO family was selected deterministically.",
                )
            )

        requested_entry = dimensions.get(str(requested.archetype_id or ""))
        requested_variant = requested.variant_id
        if requested_entry is None and requested.archetype_id:
            requested_entry = next(
                (
                    candidate
                    for candidate in dimensions.values()
                    if requested.archetype_id in (candidate.get("variant_ids") or ())
                ),
                None,
            )
            if requested_entry is not None:
                requested_variant = requested.archetype_id
        requested_parent = str(requested_entry.get("id")) if requested_entry is not None else None
        requested_selectable = requested_variant or requested_parent
        capability = next(
            (candidate for candidate in lego_catalog.capabilities if candidate.parent_id == requested_parent),
            None,
        )
        is_known_family_pending = bool(
            requested_entry is not None
            and requested_entry.get("usable")
            and requested_parent
            and requested_selectable
            and (
                capability is None
                or requested_selectable not in capability.selectable_ids
                or lego_catalog.parent_by_selectable_id.get(requested_selectable) != requested_parent
            )
        )
        if is_known_family_pending:
            assert requested_entry is not None and requested_parent is not None
            valid_variants = tuple(requested_entry.get("variant_ids") or ())
            selected_pending_variant = requested_variant if requested_variant in valid_variants else None
            typology = requested.typology if requested.typology in TYPOLOGIES else preset.bands[key].typology
            repaired_bands[key] = BandPlan(
                development_type=_norm(requested_entry["development_type"]),
                aesthetic=_norm(requested_entry["aesthetic_category"]),
                floors=min(MAX_FLOORS, max(1.0, float(requested.floors))),
                typology=typology,
                archetype_id=requested_parent,
                variant_id=selected_pending_variant,
                alternates=[],
            )
            notes.append(
                _note(
                    "MASTER_PLAN_LEGO_FAMILY_PENDING",
                    f"Band '{key}' keeps catalogue archetype "
                    f"'{selected_pending_variant or requested_parent}' as planned massing "
                    "until its exact Sticker/LEGO family is imported.",
                )
            )
            continue

        capability, selected_variant, selected_floor = _select_lego_character(
            development_type=requested.development_type,
            aesthetic=requested.aesthetic,
            floors=requested.floors,
            archetype_id=requested.archetype_id,
            variant_id=requested.variant_id,
            lego_catalog=lego_catalog,
        )
        entry = dimensions[capability.parent_id]
        typology = requested.typology if requested.typology in TYPOLOGIES else preset.bands[key].typology
        if requested.archetype_id != capability.parent_id or requested.variant_id != selected_variant:
            notes.append(
                _note(
                    "MASTER_PLAN_LEGO_ARCHETYPE_REPAIRED",
                    f"Band '{key}' now uses imported LEGO archetype " f"'{selected_variant or capability.parent_id}'.",
                )
            )
        if float(requested.floors) != float(selected_floor):
            notes.append(
                _note(
                    "MASTER_PLAN_LEGO_FLOORS_SNAPPED",
                    f"Band '{key}' floors {requested.floors:g} snapped to the proven " f"LEGO height {selected_floor}.",
                )
            )

        alternates: list[BandAlternate] = []
        for alternate in requested.alternates[:MAX_ALTERNATES]:
            alt_capability, alt_variant, _ = _select_lego_character(
                development_type=alternate.development_type,
                aesthetic=alternate.aesthetic,
                floors=selected_floor,
                archetype_id=alternate.archetype_id,
                variant_id=alternate.variant_id,
                lego_catalog=lego_catalog,
            )
            alt_entry = dimensions[alt_capability.parent_id]
            candidate = BandAlternate(
                development_type=_norm(alt_entry["development_type"]),
                aesthetic=_norm(alt_entry["aesthetic_category"]),
                archetype_id=alt_capability.parent_id,
                variant_id=alt_variant,
            )
            if candidate not in alternates:
                alternates.append(candidate)

        repaired_bands[key] = BandPlan(
            development_type=_norm(entry["development_type"]),
            aesthetic=_norm(entry["aesthetic_category"]),
            floors=float(selected_floor),
            typology=typology,
            archetype_id=capability.parent_id,
            variant_id=selected_variant,
            alternates=alternates,
        )

    _fill_site_scaled_lego_alternates(
        repaired_bands,
        diversity=common.diversity,
        lego_catalog=lego_catalog,
        dimensions=dimensions,
        notes=notes,
    )

    family_votes = [family_of(band.archetype_id) for band in repaired_bands.values() if family_of(band.archetype_id)]
    style_family = (
        sorted(set(family_votes), key=lambda family: (-family_votes.count(family), family))[0] if family_votes else None
    )
    validated = common.model_copy(
        update={
            "bands": repaired_bands,
            "style_family": style_family,
            "spine_archetype_id": spine_archetype_id,
            "local_archetype_id": local_archetype_id,
            # The initial network-node kit supports ordinary graph intersections
            # and compact roundabouts, not a culturally styled crescent street.
            "crescent_archetype_id": None,
            "open_space": open_space,
            "public_realm": public_realm,
        }
    )
    return validated, notes


def lego_fallback_spec(
    scenario_id: str,
    lego_catalog: LegoPlanningCatalog,
    palette_hint: str | None = None,
    *,
    narrative: str = "The imported LEGO building library sets the district character.",
    site_summary: dict[str, Any] | None = None,
) -> MasterPlanSpec:
    """Create a complete zero-LLM plan constrained to executable families."""

    if not lego_catalog.capabilities:
        raise ValueError("No executable LEGO building families are available for Master Planner.")
    preset = palette_for(scenario_id, palette_hint)
    raw = MasterPlanSpec(
        design_narrative=narrative,
        style_family=preset.style_family,
        curvilinear=preset.curvilinear,
        laneways=preset.laneways,
        spine_archetype_id=preset.spine_archetype_id,
        local_archetype_id=preset.local_archetype_id,
        crescent_archetype_id=preset.crescent_archetype_id,
        single_block_typology=preset.single_block_typology,
        bands={key: _preset_band_plan(preset, key) for key in BAND_KEYS},
        open_space=OpenSpaceProgram(
            water_feature=preset.water_feature,
            formal_water=preset.formal_water,
            water_archetype_id=preset.water_archetype_id,
            plaza=preset.plaza,
            central_park_archetype_id=preset.central_archetype_id,
        ),
        landscape=LandscapePlan(
            park_structure=preset.landscape.get("park", "naturalistic_grove"),
            pocket_structure=preset.landscape.get("pocket", "garden_courtyard"),
            courtyard_structure=preset.landscape.get("courtyard", "garden_courtyard"),
            greenway_structure=preset.landscape.get("greenway", "formal_allee"),
        ),
        diversity=diversity_plan_for_site(site_summary),
    )
    validated, _ = validate_spec(
        raw,
        scenario_id,
        palette_hint,
        lego_catalog=lego_catalog,
    )
    return validated


def palette_from_spec(
    spec: MasterPlanSpec,
    scenario_id: str,
    palette_hint: str | None = None,
    lego_catalog: LegoPlanningCatalog | None = None,
) -> Palette:
    """MasterPlanSpec -> the Palette the placement policy executes.

    Bands the planner didn't (validly) author keep the preset's BandSpec —
    including its relative-floors behavior — so a partial spec degrades to
    the familiar scenario character instead of a surprise. Alternates stay
    raw (type, aesthetic) pairs: plan_blocks resolves them at the block's
    FINAL floor count (context caps can move it), the one place archetype
    resolution already lives.
    """
    if lego_catalog is not None:
        spec, _ = validate_spec(
            spec,
            scenario_id,
            palette_hint,
            lego_catalog=lego_catalog,
        )
    preset = palette_for(scenario_id, palette_hint)
    bands: dict[str, BandSpec] = {}
    alternates: dict[
        str,
        tuple[
            tuple[str, str, str | None] | tuple[str, str, str | None, str | None],
            ...,
        ],
    ] = {}
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
            variant_id=band.variant_id,
        )
        characters = tuple(
            dict.fromkeys(
                (
                    (
                        alt.development_type,
                        alt.aesthetic,
                        alt.archetype_id,
                        alt.variant_id,
                    )
                    if lego_catalog is not None
                    else (alt.development_type, alt.aesthetic, alt.archetype_id)
                )
                for alt in band.alternates
            )
        )
        if characters:
            alternates[key] = characters

    family_pending_archetype_ids = (
        frozenset(
            band.archetype_id
            for band in spec.bands.values()
            if band.archetype_id
            and (
                (band.variant_id or band.archetype_id) not in lego_catalog.parent_by_selectable_id
                or lego_catalog.parent_by_selectable_id.get(band.variant_id or band.archetype_id) != band.archetype_id
            )
        )
        if lego_catalog is not None
        else frozenset()
    )
    allowed_archetype_ids = (
        frozenset((*lego_catalog.parent_ids, *family_pending_archetype_ids)) if lego_catalog is not None else None
    )
    allowed_variant_ids_by_archetype = dict(lego_catalog.variants_by_parent) if lego_catalog is not None else {}
    supported_floors_by_selectable_id = (
        dict(lego_catalog.supported_floors_by_selectable_id) if lego_catalog is not None else {}
    )
    target_dimensions_by_selectable_id = (
        dict(lego_catalog.target_dimensions_by_selectable_id) if lego_catalog is not None else {}
    )
    public_realm_variants = (
        {
            key: value
            for key, value in {
                "spine": spec.public_realm.spine_street_variant_id,
                "local": spec.public_realm.local_street_variant_id,
                "central": spec.public_realm.central_park_variant_id,
                "pocket": spec.public_realm.pocket_park_variant_id,
                "courtyard": spec.public_realm.courtyard_variant_id,
                "greenway": spec.public_realm.greenway_variant_id,
                "plaza": "formal_civic_plaza_v0",
                "pond": "stormwater_retention_pond_v0",
                "path": "multi_use_trail_v1",
                "lane": "toronto_laneway_v0",
                "roundabout": "roundabout_v0",
            }.items()
            if value
        }
        if lego_catalog is not None
        else {}
    )
    public_realm_variant_cycles: dict[str, tuple[str, ...]] = {}
    if lego_catalog is not None:
        role_archetypes = {
            "spine": spec.spine_archetype_id,
            "local": spec.local_archetype_id,
            "central": spec.open_space.central_park_archetype_id,
            "pocket": "urban_pocket_park",
            "courtyard": "urban_pocket_park",
            "greenway": "linear_park_greenway",
        }
        for role, archetype_id in role_archetypes.items():
            selected = public_realm_variants.get(role)
            allowed = PUBLIC_REALM_VARIANTS_BY_ARCHETYPE.get(archetype_id or "", ())
            if not selected or selected not in allowed:
                continue
            target = spec.diversity.street_characters if role in {"spine", "local"} else spec.diversity.park_characters
            public_realm_variant_cycles[role] = tuple(list(dict.fromkeys((selected, *allowed)))[:target])

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
        public_realm_variants=public_realm_variants,
        public_realm_variant_cycles=public_realm_variant_cycles,
        central_archetype_id=spec.open_space.central_park_archetype_id,
        single_block_typology=spec.single_block_typology,
        allowed_archetype_ids=allowed_archetype_ids,
        allowed_variant_ids_by_archetype=allowed_variant_ids_by_archetype,
        supported_floors_by_selectable_id=supported_floors_by_selectable_id,
        target_dimensions_by_selectable_id=target_dimensions_by_selectable_id,
        family_pending_archetype_ids=family_pending_archetype_ids,
    )
