"""Placement policy — which archetype family goes on which block, and where
the open space goes. Pure functions of geometry + parameters (no RNG), so
re-runs and the refinement loop stay deterministic.

The vocabulary emitted here mirrors the frontend catalog
(frontend/src/data/*.json via resolvePlanZoneArchetypes.ts):
- development_type values must be real catalog developmentType entries
  (resolver matches exact-then-prefix and silently falls back to mixed_use);
- floors targets must land inside the target family's minFloors..maxFloors;
- street `width` picks the resolver band (<10 yield, <15 narrow residential,
  <22 collector, >=22 main street);
- open-space AREA picks pocket (<1500 m2) vs neighborhood (>=1500 m2) park —
  and 900-2000 m2 is a catalog gap, so band-resolved greens must avoid it;
- a zone carrying a direct *_archetype_id skips the resolver entirely (used
  for ponds, greenways, plazas, arterials, laneways, roundabouts).

Render-cap note: Gemini accepts ~48 reference images (~3 per archetype) and
GPT keeps only the first 15 — each palette stays at <=5 building
(type, aesthetic, floors) triples so a whole plan resolves to ~13 distinct
archetypes.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field, replace
from typing import Any

from shapely import affinity
from shapely.geometry import Point, Polygon, box
from shapely.geometry.base import BaseGeometry
from shapely.validation import make_valid

from app.services.plan_geometry.archetypes import (
    TargetFootprint,
    dims_by_id,
    resolve_building_archetype,
    target_footprint,
    variants_of,
)
from app.services.plan_geometry.community_rules import FLOOR_HEIGHT_M, RuleProfile
from app.services.plan_geometry.parceling import (
    MIN_BLOCK_M2,
    TypologyDims,
    _long_axis_angle,
    decompose_holed,
)
from app.services.plan_geometry.street_graph import StreetNetwork
from app.services.site_engine import iter_polygons

# development_type values the palettes may emit — every one exists in
# buildingArchetypes.json, so the resolver never falls back to mixed_use.
CATALOG_DEV_TYPES = frozenset({
    "residential_single_family", "residential_duplex", "residential_multifamily",
    "residential_highrise", "mixed_use", "commercial_retail", "commercial_office",
    "institutional_education", "institutional_health",
})

# Footprint envelopes per typology — see TypologyDims docstring for the
# catalog archetypes each row mirrors.
TYPOLOGY_DIMS: dict[str, TypologyDims] = {
    "point_towers": TypologyDims(unit_w_m=30.0, unit_d_m=30.0, gap_m=24.0),
    "row_bars": TypologyDims(unit_w_m=0.0, unit_d_m=11.0, gap_m=16.0),
    "anchor_mass": TypologyDims(unit_w_m=60.0, unit_d_m=45.0, gap_m=0.0),
}

# Resolver open-space band edges (must match resolvePlanZoneArchetypes.ts).
POCKET_PARK_MIN_M2 = 200.0
POCKET_PARK_MAX_M2 = 900.0
NEIGHBORHOOD_PARK_MIN_M2 = 2000.0

POND_MIN_M2 = 300.0     # stormwater_retention_pond catalog range
POND_MAX_M2 = 9600.0
PLAZA_MIN_M2 = 1400.0   # formal_civic_plaza catalog range


@dataclass(frozen=True)
class BlockContext:
    index: int                     # original block index (names stay "Block {i+1}")
    area_m2: float
    dist_to_centroid_m: float
    dist_to_edge_m: float
    transect: float                # 0 = site edge, 1 = deepest core
    fronts_spine: bool
    touches_boundary: bool         # the block borders the site edge
    dist_to_green_m: float         # to the signature green; inf if none
    abuts_low_rise: bool
    ceiling_floors: float | None


@dataclass(frozen=True)
class BandSpec:
    development_type: str
    aesthetic: str
    floors_delta: float | None     # relative to rules.floors (refinement bumps propagate)
    floors_abs: float | None       # absolute target (edge/anchor bands)
    typology: str
    # Exact catalog archetype (Master Planner-named). None = resolve by
    # (development_type, aesthetic, floors) as always.
    archetype_id: str | None = None


@dataclass(frozen=True)
class BarOption:
    """One resolved per-bar character (within-block variety). Emitted on
    BlockPlan so the generator can rotate archetypes across the bars of a
    perimeter ring / row set instead of stamping one model N times."""
    development_type: str
    aesthetic: str
    archetype_id: str | None
    variant_id: str | None


# Per-bar variety keeps the parcel grid carved for the PRIMARY archetype, so
# an alternate only qualifies when its own frontage sits believably in that
# grid (globe contain-fit scaling absorbs the remainder). Kept generous — a
# rowhouse beside a mid-rise apartment is normal streetwall variety; too tight
# a band silently collapses the ring back to a monoculture.
BAR_WIDTH_COMPAT_LO = 0.35
BAR_WIDTH_COMPAT_HI = 2.4
# Variant rotation: how many of the primary archetype's OWN variants join the
# bar cycle (same scale/family by construction), and the total option cap —
# bounds the distinct render refs and 3D cache keys one plan can demand.
MAX_VARIANT_BARS = 3
MAX_BAR_OPTIONS = 5


@dataclass(frozen=True)
class Palette:
    bands: dict[str, BandSpec]     # keys: core | frontage | mid | edge | anchor
    spine_archetype_id: str | None = None  # direct road_archetype_id for the spine
    water_feature: bool = False    # water basin + greenway on the central green
    plaza: bool = False            # carve a civic plaza off the anchor block
    laneways: bool = False         # mid-block rear lanes on row_bars blocks
    # Cap EVERY band's floors at the DNA context average + 2 (not just core) —
    # the Economic scenario's "similar to surrounding development" mechanism.
    context_match: bool = False
    # Direct road_archetype_id stamped on LOCAL streets (e.g. woonerf/cycling
    # streets for the Environmental scenario). None = width-band resolution.
    local_archetype_id: str | None = None
    # Central water feature: which archetype the basin resolves to, and whether
    # it reads formal (pure ellipse — City Beautiful) or naturalized (organic
    # wobble — stormwater pond).
    water_archetype_id: str = "stormwater_retention_pond"
    formal_water: bool = False
    # Curvilinear street grid: long-axis rows bow toward the site's heart
    # (street_graph translated bow-curves; generator guard owns the fallback).
    # crescent_archetype_id tags bowed locals (sagitta-qualified) so they
    # resolve to a crescent street archetype; None = keep width-band/local id.
    curvilinear: bool = False
    crescent_archetype_id: str | None = None
    # ── Master Planner extensions ────────────────────────────────────────────
    # Declared style family (archetype_families.json): family-aware resolution
    # keeps every pick coherent. None = legacy resolution.
    style_family: str | None = None
    # Per-band character rotation: (development_type, aesthetic, archetype_id)
    # triples cycled across same-band blocks and across the bars within a
    # block (archetype_id None = resolve). Empty = preset single-character.
    alternates: dict[str, tuple[tuple[str, str, str | None], ...]] = field(default_factory=dict)
    # planting_structure per green kind (park/pocket/courtyard/greenway/plaza),
    # mirrored by the globe's parkScatter — see master_planner.spec vocabulary.
    landscape: dict[str, str] = field(default_factory=dict)
    # Direct green_space_archetype_id for the signature central green.
    central_archetype_id: str | None = None
    # Massing for the degenerate one-block site; None keeps the historic
    # perimeter courtyard.
    single_block_typology: str | None = None


@dataclass(frozen=True)
class BlockPlan:
    development_type: str
    aesthetic: str
    floors_target: float
    typology: str
    band: str
    # Model-aware fields: resolved BEFORE massing so parcels can be carved to
    # the 3D model's real footprint (None = legacy TYPOLOGY_DIMS behavior).
    archetype_id: str | None = None
    variant_id: str | None = None
    target: "TargetFootprint | None" = None
    # Width-compatible sibling characters for the block's OTHER bars (empty =
    # every bar carries the primary archetype, the historic behavior).
    bar_options: tuple[BarOption, ...] = ()


# Coherent character families per scenario; floors verified against the
# catalog minFloors/maxFloors of each family (e.g. highrise entries start at
# 4+, institutional_health at 2+).
PALETTES: dict[str, Palette] = {
    # ── Current master-plan philosophies ─────────────────────────────────────
    "economic": Palette(bands={
        "core": BandSpec("residential_multifamily", "contemporary_midrise", 1.0, None, "perimeter_block"),
        "frontage": BandSpec("mixed_use", "contemporary_urban", 0.0, None, "perimeter_block"),
        "mid": BandSpec("residential_multifamily", "contemporary", 0.0, None, "perimeter_block"),
        "edge": BandSpec("residential_single_family", "contemporary", None, 2.0, "row_bars"),
        "anchor": BandSpec("commercial_retail", "contemporary", None, 2.0, "anchor_mass"),
    }, context_match=True, curvilinear=True, crescent_archetype_id="london_crescent_road",
       landscape={"park": "active_recreation", "pocket": "garden_courtyard",
                  "courtyard": "garden_courtyard", "greenway": "formal_allee",
                  "plaza": "formal_allee"}),
    "city_policy": Palette(bands={
        "core": BandSpec("residential_multifamily", "contemporary_midrise", 1.0, None, "perimeter_block"),
        "frontage": BandSpec("mixed_use", "contemporary_midrise", 1.0, None, "perimeter_block"),
        "mid": BandSpec("residential_multifamily", "brownstone", 0.0, None, "row_bars"),
        "edge": BandSpec("residential_duplex", "brownstone_rowhouse", None, 3.0, "row_bars"),
        "anchor": BandSpec("institutional_health", "biophilic_contemporary_institutional", None, 4.0, "anchor_mass"),
    }, plaza=True, laneways=True, curvilinear=True, crescent_archetype_id="london_crescent_road",
       landscape={"park": "active_recreation", "pocket": "garden_courtyard",
                  "courtyard": "formal_quad", "greenway": "formal_allee",
                  "plaza": "formal_allee"}),
    "city_beautiful": Palette(bands={
        "core": BandSpec("mixed_use", "parisian", 2.0, None, "perimeter_block"),
        "frontage": BandSpec("mixed_use", "haussmann", 1.0, None, "perimeter_block"),
        "mid": BandSpec("residential_multifamily", "neoclassical", 0.0, None, "perimeter_block"),
        "edge": BandSpec("residential_duplex", "brownstone_rowhouse", None, 3.0, "row_bars"),
        "anchor": BandSpec("institutional_education", "classical", None, 4.0, "anchor_mass"),
    }, spine_archetype_id="haussmann_boulevard", water_feature=True, plaza=True,
       water_archetype_id="fountain_water_feature", formal_water=True,
       landscape={"park": "formal_allee", "pocket": "formal_quad",
                  "courtyard": "formal_quad", "greenway": "formal_allee",
                  "plaza": "formal_allee"}),
    "environmental": Palette(bands={
        "core": BandSpec("residential_multifamily", "eco_urban_green_architecture", 2.0, None, "perimeter_block"),
        "frontage": BandSpec("mixed_use", "scandinavian_nordic", 1.0, None, "perimeter_block"),
        "mid": BandSpec("residential_multifamily", "scandinavian_nordic", 0.0, None, "row_bars"),
        "edge": BandSpec("residential_duplex", "brownstone_rowhouse", None, 3.0, "row_bars"),
        "anchor": BandSpec("institutional_education", "biophilic", None, 3.0, "anchor_mass"),
        # curvilinear but NO crescent id: every local stays a woonerf, bowed or not.
    }, water_feature=True, laneways=True, local_archetype_id="woonerf_shared_street",
       curvilinear=True,
       landscape={"park": "naturalistic_grove", "pocket": "garden_courtyard",
                  "courtyard": "garden_courtyard", "greenway": "naturalistic_grove",
                  "plaza": "formal_allee"}),
    # ── Retired V1 preset ids (existing scenario rows redraw identically) ────
    "climate_first": Palette(bands={
        "core": BandSpec("residential_multifamily", "eco_urban_green_architecture", 2.0, None, "perimeter_block"),
        "frontage": BandSpec("mixed_use", "scandinavian_nordic", 1.0, None, "perimeter_block"),
        "mid": BandSpec("residential_multifamily", "scandinavian_nordic", 0.0, None, "row_bars"),
        "edge": BandSpec("residential_duplex", "brownstone_rowhouse", None, 3.0, "row_bars"),
        "anchor": BandSpec("institutional_education", "biophilic", None, 3.0, "anchor_mass"),
    }, spine_archetype_id=None, water_feature=True, plaza=False, laneways=True,
       landscape={"park": "naturalistic_grove", "pocket": "garden_courtyard",
                  "courtyard": "garden_courtyard", "greenway": "naturalistic_grove",
                  "plaza": "formal_allee"}),
    "as_of_right": Palette(bands={
        "core": BandSpec("residential_multifamily", "contemporary_urban", 3.0, None, "point_towers"),
        "frontage": BandSpec("mixed_use", "contemporary_urban", 1.0, None, "perimeter_block"),
        "mid": BandSpec("residential_multifamily", "contemporary_midrise", 0.0, None, "perimeter_block"),
        "edge": BandSpec("residential_single_family", "contemporary", None, 2.0, "row_bars"),
        "anchor": BandSpec("commercial_office", "modernist", None, 6.0, "anchor_mass"),
    }, spine_archetype_id="arterial_boulevard", water_feature=False, plaza=True, laneways=False,
       landscape={"park": "open_meadow", "pocket": "garden_courtyard",
                  "courtyard": "paved_plaza", "greenway": "formal_allee",
                  "plaza": "formal_allee"}),
    "lap_compliant": Palette(bands={
        "core": BandSpec("residential_multifamily", "contemporary_midrise", 1.0, None, "perimeter_block"),
        "frontage": BandSpec("mixed_use", "contemporary_midrise", 1.0, None, "perimeter_block"),
        "mid": BandSpec("residential_multifamily", "brownstone", 0.0, None, "row_bars"),
        "edge": BandSpec("residential_duplex", "brownstone_rowhouse", None, 3.0, "row_bars"),
        "anchor": BandSpec("institutional_health", "biophilic_contemporary_institutional", None, 4.0, "anchor_mass"),
    }, spine_archetype_id=None, water_feature=False, plaza=True, laneways=True,
       landscape={"park": "active_recreation", "pocket": "garden_courtyard",
                  "courtyard": "formal_quad", "greenway": "formal_allee",
                  "plaza": "formal_allee"}),
}
_DEFAULT_PALETTE = PALETTES["city_policy"]

# Custom scenarios carry an extracted philosophy primary — map it to the
# nearest preset palette so a "make it beautiful" brief draws beaux-arts
# fabric, not the default midrise mix.
_PHILOSOPHY_TO_PALETTE: dict[str, str] = {
    "developer_feasibility": "economic",
    "neighbourhood_context": "economic",
    "climate_resilience": "environmental",
    "landscape_urbanism": "environmental",
    "transit_oriented": "environmental",
    "city_beautiful": "city_beautiful",
    "garden_city": "city_beautiful",
}

_LOW_RISE_LU_PREFIXES = ("R-C", "R-1", "R-2", "R-G")
_LOW_RISE_CEILING_M = 12.0


def palette_for(scenario_id: str, palette_hint: str | None = None) -> Palette:
    direct = PALETTES.get(scenario_id)
    if direct is not None:
        return direct
    if palette_hint:
        mapped = _PHILOSOPHY_TO_PALETTE.get(palette_hint)
        if mapped:
            return PALETTES[mapped]
    return _DEFAULT_PALETTE


def resolve_layout_strategy(raw: Any) -> str:
    """Map the experts' free-text layout.strategy onto a known mode.

    This is the previously-dead wire from PARAMETER_VOCABULARY: absent or
    unrecognized values take the default transect mode.
    """
    text = str(raw or "").strip().lower()
    if not text:
        return "transect_green"
    if "grid" in text or "fine" in text:
        return "urban_grid"
    if "courtyard" in text or "central green" in text:
        return "courtyard_focus"
    return "transect_green"


def effective_palette(scenario_id: str, strategy: str, palette_hint: str | None = None) -> Palette:
    """Apply the layout strategy on top of the scenario palette."""
    palette = palette_for(scenario_id, palette_hint)
    if strategy == "transect_green":
        return palette
    # Both alternate strategies read as consistent perimeter fabric.
    bands = {
        key: replace(spec, typology="perimeter_block")
        for key, spec in palette.bands.items()
    }
    if strategy == "urban_grid":
        # A fine-grained-grid brief reads straight and rectilinear.
        return replace(palette, bands=bands, laneways=False, curvilinear=False)
    # courtyard_focus: solid central green, courtyards everywhere.
    return replace(palette, bands=bands, laneways=False, water_feature=False)


def site_hash(boundary_m: BaseGeometry) -> int:
    """Deterministic seed from the metric centroid (stable across runs —
    the local metric CRS choice is itself deterministic)."""
    centroid = boundary_m.centroid
    return (int(centroid.x * 100) * 73856093) ^ (int(centroid.y * 100) * 19349663)


def _dna_value(dna: dict[str, Any] | None, section: str, fieldname: str) -> Any:
    try:
        return (dna or {})[section]["fields"][fieldname]["value"]
    except (KeyError, TypeError):
        return None


def compute_block_contexts(
    *,
    blocks: list[tuple[int, BaseGeometry]],
    boundary_m: BaseGeometry,
    network: StreetNetwork,
    district_lookup: list[tuple[BaseGeometry, dict[str, Any]]],
    signature_green_m: BaseGeometry | None,
) -> list[BlockContext]:
    """Context signals per developable block. Tolerates locked-street networks
    (no segments): fronts_spine is simply False everywhere."""
    exterior = boundary_m.exterior
    centroid = boundary_m.centroid

    spine_band: BaseGeometry | None = None
    spine_segments = [s for s in network.segments if s.role == "spine"]
    if spine_segments:
        seg = spine_segments[0]
        spine_band = seg.line.buffer(seg.row_width_m / 2 + 1.0)

    low_rise_geoms: list[BaseGeometry] = []
    for geom, props in district_lookup:
        height = props.get("height_m")
        code = str(props.get("code") or "")
        if (height is not None and float(height) <= _LOW_RISE_CEILING_M) or \
                code.startswith(_LOW_RISE_LU_PREFIXES):
            low_rise_geoms.append(geom)

    edge_dists = {index: block.centroid.distance(exterior) for index, block in blocks}
    max_edge = max(edge_dists.values(), default=0.0)

    contexts: list[BlockContext] = []
    for index, block in blocks:
        block_centroid = block.centroid
        ceiling: float | None = None
        for geom, props in district_lookup:
            try:
                if geom.contains(block_centroid) and props.get("height_m"):
                    ceiling = float(props["height_m"]) / FLOOR_HEIGHT_M
                    break
            except Exception:  # noqa: BLE001 — municipal geometry
                continue
        touches_boundary = bool(block.distance(exterior) < 2.0)
        contexts.append(BlockContext(
            index=index,
            area_m2=float(block.area),
            dist_to_centroid_m=float(block_centroid.distance(centroid)),
            dist_to_edge_m=float(edge_dists[index]),
            transect=(edge_dists[index] / max_edge) if max_edge > 0 else 0.0,
            fronts_spine=bool(spine_band is not None and block.distance(spine_band) < 0.5),
            touches_boundary=touches_boundary,
            dist_to_green_m=(
                float(block.distance(signature_green_m))
                if signature_green_m is not None else math.inf
            ),
            abuts_low_rise=bool(
                touches_boundary
                and any(g.distance(block) < 30.0 for g in low_rise_geoms)
            ),
            ceiling_floors=ceiling,
        ))
    return contexts


def plan_blocks(
    *,
    contexts: list[BlockContext],
    palette: Palette,
    rules: RuleProfile,
    base_type: str | None,
    base_aesthetic: str | None,
    dna: dict[str, Any] | None = None,
    measured_dims: dict | None = None,
) -> dict[int, BlockPlan]:
    """Assign each block a band (anchor > edge > frontage > core > mid), then
    resolve the band's spec to concrete tags. Experts' development_type /
    aesthetic (when emitted) override the MID band only — the transect bands
    keep their strategic roles. Bands carrying alternates rotate their
    character across same-band blocks (deterministic: contexts arrive in
    block-index order), so a district reads as one fabric with several hands
    instead of one stamp."""
    plans: dict[int, BlockPlan] = {}
    if not contexts:
        return plans

    anchor_index: int | None = None
    if len(contexts) >= 5:
        with_green = [c for c in contexts if math.isfinite(c.dist_to_green_m)]
        if with_green:
            anchor_index = min(with_green, key=lambda c: (c.dist_to_green_m, c.index)).index

    context_avg_h = _dna_value(dna, "built_form", "context_avg_height_m")
    band_turns: dict[str, int] = {}

    for ctx in contexts:
        # anchor > frontage > edge > core > mid. Main-street character wins
        # over the boundary step-down (West District: the mixed-use spine
        # runs all the way out); every other block bordering the site edge
        # steps DOWN toward the existing neighbourhood; genuinely interior
        # blocks carry the height.
        if len(contexts) == 1:
            band = "mid"
        elif ctx.index == anchor_index:
            band = "anchor"
        elif ctx.fronts_spine and not ctx.abuts_low_rise:
            band = "frontage"
        elif ctx.abuts_low_rise or ctx.touches_boundary or ctx.transect < 0.35:
            band = "edge"
        elif ctx.transect > 0.70:
            band = "core"
        else:
            band = "mid"

        spec = palette.bands[band]
        development_type = spec.development_type
        aesthetic = spec.aesthetic
        arch_hint = spec.archetype_id
        if band == "mid" and (base_type or base_aesthetic):
            # Expert override changes the character — a pinned id no longer applies.
            arch_hint = None
            if base_type:
                development_type = base_type
            if base_aesthetic:
                aesthetic = base_aesthetic

        # Character rotation across same-band blocks. Options are
        # (development_type, aesthetic, archetype_id|None) triples.
        options: list[tuple[str, str, str | None]] = [(development_type, aesthetic, arch_hint)]
        for triple in palette.alternates.get(band, ()):
            if triple not in options:
                options.append(triple)
        # A LONE block is a microcosm of the transect: its ring bars should
        # rotate through the frontage/mid/edge characters (and their
        # alternates) so a single-block infill reads as several distinct
        # buildings, not one monoculture ring (the "24 identical buildings"
        # bug). The primary stays the mid character; the rest become bar
        # options below.
        if len(contexts) == 1:
            for bk in ("frontage", "edge", "core", "anchor"):
                other = palette.bands.get(bk)
                if other is None:
                    continue
                triple = (other.development_type, other.aesthetic, other.archetype_id)
                if triple not in options:
                    options.append(triple)
                for alt in palette.alternates.get(bk, ()):
                    if alt not in options:
                        options.append(alt)
        turn = band_turns.get(band, 0)
        band_turns[band] = turn + 1
        development_type, aesthetic, arch_hint = options[turn % len(options)]

        if spec.floors_abs is not None:
            floors = spec.floors_abs
        else:
            floors = max(1.0, rules.floors + (spec.floors_delta or 0.0))
        # Soft compatibility with the surrounding built form; the district
        # ceiling clamp still applies afterwards in the generator. Normally
        # only the core band is capped; a context_match palette (Economic —
        # "development similar to its surroundings") caps every band.
        cap_to_context = band == "core" or palette.context_match
        if cap_to_context and isinstance(context_avg_h, (int, float)) and context_avg_h > 0:
            floor_min = 1.0 if palette.context_match else 3.0
            floors = max(floor_min, min(floors, context_avg_h / FLOOR_HEIGHT_M + 2.0))
        if band == "core" and floors >= 8.0 and development_type == "residential_multifamily":
            development_type = "residential_highrise"

        if len(contexts) > 1:
            typology = spec.typology
        else:
            # One-block sites historically forced a perimeter courtyard —
            # the master planner may choose the massing instead.
            typology = palette.single_block_typology or "perimeter_block"

        # Resolve the concrete archetype NOW — before massing — so parcels
        # can be carved to the model's footprint and the zone can carry the
        # id downstream (render refs + model-cache hits + globe placement).
        # A planner-named archetype_id pins the entry; otherwise resolution is
        # family-aware so ties never mix style families.
        floors_int = max(1, int(round(float(floors))))

        def _resolve_entry(dev: str, aes: str, aid: str | None) -> dict | None:
            if aid:
                pinned = dims_by_id().get(aid)
                if pinned is not None and pinned.get("usable"):
                    return pinned
            return resolve_building_archetype(
                dev, aes, floors_int, prefer_family=palette.style_family,
            )

        entry = _resolve_entry(development_type, aesthetic, arch_hint)
        target = target_footprint(entry, floors_int, measured_dims) if entry else None
        measured_entry = (measured_dims or {}).get(entry["id"]) if entry else None

        # Per-bar options: the primary archetype's OWN VARIANTS come first
        # (same building, different sub-style — a real streetscape), then the
        # band's other characters when their frontage fits the carved grid.
        bar_options: list[BarOption] = []
        if entry is not None:
            primary_variant = measured_entry.variant_id if measured_entry else None
            for vid in variants_of(entry["id"]):
                if vid == primary_variant:
                    continue
                bar_options.append(BarOption(
                    development_type=development_type,
                    aesthetic=aesthetic,
                    archetype_id=entry["id"],
                    variant_id=vid,
                ))
                if len(bar_options) >= MAX_VARIANT_BARS:
                    break
        if entry is not None and len(options) > 1:
            seen_ids = {entry["id"]}
            for dev, aes, aid in options:
                if (dev, aes, aid) == (development_type, aesthetic, arch_hint):
                    continue
                alt = _resolve_entry(dev, aes, aid)
                if alt is None or alt["id"] in seen_ids:
                    continue
                alt_target = target_footprint(alt, floors_int, measured_dims)
                if target is not None and alt_target is not None:
                    ratio = alt_target.width_m / max(target.width_m, 0.1)
                    if not (BAR_WIDTH_COMPAT_LO <= ratio <= BAR_WIDTH_COMPAT_HI):
                        continue
                seen_ids.add(alt["id"])
                alt_measured = (measured_dims or {}).get(alt["id"])
                bar_options.append(BarOption(
                    development_type=dev,
                    aesthetic=aes,
                    archetype_id=alt["id"],
                    variant_id=alt_measured.variant_id if alt_measured else None,
                ))
                if len(bar_options) >= MAX_BAR_OPTIONS:
                    break

        plans[ctx.index] = BlockPlan(
            development_type=development_type,
            aesthetic=aesthetic,
            floors_target=round(float(floors), 1),
            typology=typology,
            band=band,
            archetype_id=entry["id"] if entry else None,
            variant_id=measured_entry.variant_id if measured_entry else None,
            target=target,
            bar_options=tuple(bar_options),
        )
    return plans


# --- open space -----------------------------------------------------------------


@dataclass(frozen=True)
class GreenSpec:
    geom_m: BaseGeometry
    kind: str                      # "central" | "pocket" | "plaza" | "pond" | "greenway"
    name_suffix: str
    archetype_id: str | None       # direct green_space_archetype_id, else area-band resolve


@dataclass(frozen=True)
class OpenSpacePlan:
    specs: list[GreenSpec] = field(default_factory=list)
    consumed_indices: frozenset[int] = frozenset()
    carved_blocks: dict[int, BaseGeometry] = field(default_factory=dict)
    central_geom_m: BaseGeometry | None = None
    open_area_m2: float = 0.0


def organic_basin(
    center: Point, rx: float, ry: float, angle_deg: float, seed: int,
    vertices: int = 64, formal: bool = False,
) -> Polygon:
    """Basin outline: an ellipse modulated by two sinusoidal harmonics whose
    phases derive from the site hash — pure function of geometry. `formal`
    zeroes the harmonics (a pure ellipse — City Beautiful reflecting basin
    instead of a naturalized pond edge)."""
    phi1 = 2 * math.pi * (seed % 360) / 360.0
    phi2 = 2 * math.pi * ((seed >> 8) % 360) / 360.0
    amp1, amp2 = (0.0, 0.0) if formal else (0.14, 0.06)
    points = []
    for k in range(vertices):
        t = 2 * math.pi * k / vertices
        wobble = 1.0 + amp1 * math.sin(3 * t + phi1) + amp2 * math.sin(7 * t + phi2)
        points.append((rx * math.cos(t) * wobble, ry * math.sin(t) * wobble))
    basin = Polygon(points)
    basin = affinity.rotate(basin, angle_deg, origin=(0, 0))
    return affinity.translate(basin, xoff=center.x, yoff=center.y)


def _pond_and_greenway(
    block: BaseGeometry, seed: int, formal: bool = False
) -> tuple[Polygon | None, BaseGeometry | None]:
    """Carve a water basin into the central block; the remainder becomes the
    greenway ring (decomposed hole-free by the caller)."""
    rect = block.minimum_rotated_rectangle
    coords = list(rect.exterior.coords)
    edges = [math.hypot(x2 - x1, y2 - y1) for (x1, y1), (x2, y2) in zip(coords[:-1], coords[1:])]
    long_e, short_e = max(edges), min(edges)
    rx, ry = 0.38 * long_e / 2, 0.38 * short_e / 2
    if rx < 8.0 or ry < 8.0:
        return None, None

    pond = organic_basin(block.centroid, rx, ry, _long_axis_angle(block), seed, formal=formal)
    pond = make_valid(pond.intersection(block.buffer(-2.0)))
    ponds = [p for p in iter_polygons(pond) if p.area >= 1.0]
    if not ponds:
        return None, None
    pond_poly = max(ponds, key=lambda p: p.area)

    cap = min(POND_MAX_M2, 0.5 * block.area)
    if pond_poly.area > cap:
        factor = math.sqrt(cap / pond_poly.area)
        pond_poly = affinity.scale(pond_poly, xfact=factor, yfact=factor, origin=pond_poly.centroid)
        pond_poly = make_valid(pond_poly.intersection(block.buffer(-2.0)))
        polys = list(iter_polygons(pond_poly))
        if not polys:
            return None, None
        pond_poly = max(polys, key=lambda p: p.area)
    if pond_poly.area < POND_MIN_M2:
        return None, None

    greenway = make_valid(block.difference(pond_poly))
    return pond_poly, (greenway if not greenway.is_empty else None)


def _carve_corner(
    block: BaseGeometry, target: BaseGeometry, size_w: float, size_d: float
) -> tuple[BaseGeometry | None, BaseGeometry | None]:
    """Cut a size_w x size_d square from the bbox corner of `block` nearest
    `target`. Returns (carved piece, remainder) or (None, None) when the cut
    would fragment the block or leave it unbuildable."""
    minx, miny, maxx, maxy = block.bounds
    corners = [(minx, miny), (maxx, miny), (maxx, maxy), (minx, maxy)]
    cx, cy = min(corners, key=lambda c: (Point(c).distance(target), c))
    square = box(
        cx if cx == minx else cx - size_w,
        cy if cy == miny else cy - size_d,
        cx if cx == maxx else cx + size_w,
        cy if cy == maxy else cy + size_d,
    )
    piece = make_valid(block.intersection(square))
    pieces = [p for p in iter_polygons(piece) if p.area >= 1.0]
    if len(pieces) != 1:
        return None, None
    remainder = make_valid(block.difference(square))
    remainder_polys = list(iter_polygons(remainder))
    if len(remainder_polys) != 1 or remainder_polys[0].area < MIN_BLOCK_M2:
        return None, None
    return pieces[0], remainder_polys[0]


def _carve_park_strip(
    block: BaseGeometry, target_area: float, toward: BaseGeometry
) -> tuple[BaseGeometry | None, BaseGeometry | None]:
    """Cut a full-width park strip of ~target_area from the end of `block`
    nearest `toward`, leaving a clean rectangular developable remainder.

    Consuming a WHOLE block as the signature green over-parks a few-block site
    (half of a 2-block site becomes park). Carving a right-sized strip keeps
    the rest of the block buildable and the park fronting a street. Returns
    (park, remainder) or (None, None) when no buildable remainder survives."""
    angle = _long_axis_angle(block)
    origin = block.centroid
    work = make_valid(affinity.rotate(block, -angle, origin=origin))
    minx, miny, maxx, maxy = work.bounds
    width, span = maxx - minx, maxy - miny
    if width < 24.0 or span < 45.0:
        return None, None
    depth = max(14.0, min(target_area / width, span - 32.0))
    if span - depth < 30.0:
        return None, None
    toward_pt = affinity.rotate(
        toward if isinstance(toward, Point) else toward.centroid, -angle, origin=origin
    )
    near_min = abs(toward_pt.y - miny) <= abs(maxy - toward_pt.y)
    strip = (box(minx - 1, miny, maxx + 1, miny + depth) if near_min
             else box(minx - 1, maxy - depth, maxx + 1, maxy + 1))
    park = make_valid(work.intersection(strip))
    remainder = make_valid(work.difference(strip))
    park_polys = [p for p in iter_polygons(park) if p.area >= 1.0]
    rem_polys = [p for p in iter_polygons(remainder) if p.area >= MIN_BLOCK_M2]
    if len(park_polys) != 1 or len(rem_polys) != 1:
        return None, None
    return (
        affinity.rotate(park_polys[0], angle, origin=origin),
        affinity.rotate(rem_polys[0], angle, origin=origin),
    )


def select_open_space(
    *,
    blocks: list[BaseGeometry],
    boundary_m: BaseGeometry,
    rules: RuleProfile,
    palette: Palette,
    network: StreetNetwork,
    seed: int,
) -> OpenSpacePlan:
    """One signature central green (pond + greenway when the palette says so),
    pocket parks placed far from it (that is where park access is weakest),
    and optionally a civic plaza carved off the future anchor block."""
    gross = float(boundary_m.area)
    open_target = rules.open_space_share * gross
    specs: list[GreenSpec] = []
    consumed: set[int] = set()
    carved: dict[int, BaseGeometry] = {}
    open_area = 0.0
    central: BaseGeometry | None = None

    if len(blocks) >= 2:
        by_proximity = sorted(
            range(len(blocks)),
            key=lambda i: (blocks[i].centroid.distance(boundary_m.centroid), i),
        )
        central_index = next(
            (i for i in by_proximity if blocks[i].area >= NEIGHBORHOOD_PARK_MIN_M2),
            by_proximity[0],
        )
        central_block = blocks[central_index]

        # Few-block sites: carve a right-sized park from the central block
        # instead of consuming the whole thing (which would over-park). Larger
        # sites (>4 blocks) keep the whole-block signature green — there the
        # land budget easily affords a dedicated park block.
        central = central_block
        if (
            len(blocks) <= 4
            and central_block.area > open_target * 1.6
            and central_block.area > NEIGHBORHOOD_PARK_MIN_M2 + MIN_BLOCK_M2
        ):
            park, remainder = _carve_park_strip(central_block, open_target, boundary_m.centroid)
            if park is not None:
                central = park
                carved[central_index] = remainder
        if central_index not in carved:
            consumed.add(central_index)
        open_area += float(central.area)

        pond = greenway = None
        if palette.water_feature and central.area >= 2400.0:
            pond, greenway = _pond_and_greenway(central, seed, formal=palette.formal_water)
        if pond is not None and greenway is not None:
            pond_name = "Reflecting Basin" if palette.formal_water else "Pond"
            specs.append(GreenSpec(pond, "pond", pond_name, palette.water_archetype_id))
            lobes = [
                p for p in iter_polygons(decompose_holed(greenway, central))
                if p.area >= 50.0
            ]
            for n, lobe in enumerate(lobes):
                specs.append(GreenSpec(
                    lobe, "greenway", f"Greenway {chr(65 + (n % 26))}", "linear_park_greenway",
                ))
        else:
            specs.append(GreenSpec(central, "central", "Park", palette.central_archetype_id))

        # Pocket parks: donors far from the central green first. A block whose
        # park was already carved (central) is excluded — otherwise it would be
        # re-carved from its ORIGINAL geometry and the two parks would overlap.
        pocket_count = 0
        donors = sorted(
            (i for i in range(len(blocks)) if i not in consumed and i not in carved),
            key=lambda i: (-blocks[i].centroid.distance(central.centroid), i),
        )
        for i in donors:
            if open_area >= open_target or pocket_count >= 4:
                break
            block = blocks[i]
            if MIN_BLOCK_M2 <= block.area <= POCKET_PARK_MAX_M2:
                consumed.add(i)
                open_area += float(block.area)
                pocket_count += 1
                specs.append(GreenSpec(block, "pocket", f"Pocket Park {pocket_count}", None))
                continue
            if block.area < 2 * MIN_BLOCK_M2 + 625.0:
                continue
            piece, remainder = _carve_corner(block, boundary_m.exterior, 25.0, 25.0)
            if piece is None or not (POCKET_PARK_MIN_M2 <= piece.area <= POCKET_PARK_MAX_M2):
                continue
            carved[i] = remainder
            open_area += float(piece.area)
            pocket_count += 1
            specs.append(GreenSpec(piece, "pocket", f"Pocket Park {pocket_count}", None))

        # Still short of the target: consume additional whole blocks nearest
        # the centroid (the pre-variety algorithm), skipping any block whose
        # area would land in the 900-2000 m² resolver gap.
        park_count = 1
        for i in by_proximity:
            if open_area >= open_target or len(consumed) >= max(1, len(blocks) - 1):
                break
            if i in consumed or i in carved:
                continue
            area = float(blocks[i].area)
            if POCKET_PARK_MAX_M2 < area < NEIGHBORHOOD_PARK_MIN_M2:
                continue
            if open_area + area <= open_target * 1.6:
                consumed.add(i)
                open_area += area
                park_count += 1
                specs.append(GreenSpec(blocks[i], "central", f"Park {park_count}", None))

        # Civic plaza off the (future) anchor block — the developable block
        # nearest the central green, same ordering plan_blocks uses.
        if palette.plaza and len(blocks) - len(consumed) >= 4:
            candidates = sorted(
                (i for i in range(len(blocks)) if i not in consumed),
                key=lambda i: (blocks[i].distance(central), i),
            )
            spine_segments = [s for s in network.segments if s.role == "spine"]
            plaza_target: BaseGeometry = (
                spine_segments[0].line if spine_segments else boundary_m.centroid
            )
            for i in candidates[:2]:
                base = carved.get(i, blocks[i])
                piece, remainder = _carve_corner(base, plaza_target, 42.0, 45.0)
                if piece is None or piece.area < PLAZA_MIN_M2:
                    continue
                carved[i] = remainder
                open_area += float(piece.area)
                specs.append(GreenSpec(piece, "plaza", "Civic Plaza", "formal_civic_plaza"))
                break

    return OpenSpacePlan(
        specs=specs,
        consumed_indices=frozenset(consumed),
        carved_blocks=carved,
        central_geom_m=central,
        open_area_m2=open_area,
    )


def carve_lane(block: BaseGeometry, lane_width_m: float) -> BaseGeometry | None:
    """Mid-block rear lane along the long axis. Returns the lane polygon, or
    None when the block is unsuitable (halves too small to build on)."""
    rect = block.minimum_rotated_rectangle
    coords = list(rect.exterior.coords)
    edges = [math.hypot(x2 - x1, y2 - y1) for (x1, y1), (x2, y2) in zip(coords[:-1], coords[1:])]
    if min(edges) < 55.0:
        return None

    angle = _long_axis_angle(block)
    origin = block.centroid
    work = affinity.rotate(block, -angle, origin=origin)
    minx, miny, maxx, maxy = work.bounds
    cy = (miny + maxy) / 2
    lane_work = box(minx - 1.0, cy - lane_width_m / 2, maxx + 1.0, cy + lane_width_m / 2)
    lane = make_valid(affinity.rotate(lane_work, angle, origin=origin).intersection(block))
    if lane.is_empty:
        return None

    halves = [p for p in iter_polygons(make_valid(block.difference(lane))) if p.area >= 1.0]
    if len(halves) < 2 or any(h.area < MIN_BLOCK_M2 for h in halves):
        return None
    return lane
