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
import re
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
from app.services.plan_geometry.open_space_archetypes import ladder_bounds as open_space_ladder_bounds
from app.services.plan_geometry.parceling import (
    MIN_BLOCK_M2,
    TypologyDims,
    _long_axis_angle,
    decompose_holed,
)
from app.services.plan_geometry.street_graph import StreetNetwork
from app.services.site_engine import iter_polygons


def _catalog_dev_types() -> frozenset[str]:
    """development_type values a palette may emit.

    DERIVED from the dims table rather than hand-listed. The hand-listed
    version had drifted to 9 entries against a catalogue carrying 26, which
    put a hard ceiling on how much of the library a plan could ever use and
    contradicted the Master Planner — spec.validate_spec already accepts any
    type in the table, so a planner naming `institutional` or `hotel` produced
    a plan that the placement tests then rejected.

    The guarantee the hand-list was protecting is preserved and strengthened:
    every emitted type resolves in the catalogue, so the resolver never falls
    back to mixed_use. Deriving it also means importing new archetype families
    widens the palettes automatically instead of silently stranding them.
    """
    from app.services.plan_geometry.archetypes import load_dims_table

    return frozenset(_norm_dev_type(entry["development_type"]) for entry in load_dims_table() if entry.get("usable"))


def _norm_dev_type(value: object) -> str:
    return re.sub(r"[\s\-]+", "_", str(value or "").lower().strip())


CATALOG_DEV_TYPES = _catalog_dev_types()

# Footprint envelopes per typology — see TypologyDims docstring for the
# catalog archetypes each row mirrors.
TYPOLOGY_DIMS: dict[str, TypologyDims] = {
    "point_towers": TypologyDims(unit_w_m=30.0, unit_d_m=30.0, gap_m=24.0),
    "row_bars": TypologyDims(unit_w_m=0.0, unit_d_m=11.0, gap_m=16.0),
    "anchor_mass": TypologyDims(unit_w_m=60.0, unit_d_m=45.0, gap_m=0.0),
}


# Open-space band edges, DERIVED from the catalogue's own ladder rather than
# restated here — the hand-written copies had drifted from the entries they
# were mirroring, and from the frontend resolver, in different directions.
def _park_band(archetype_id: str, index: int, default: float) -> float:
    for candidate_id, low, high in open_space_ladder_bounds("park"):
        if candidate_id == archetype_id:
            return (low, high)[index]
    return default


POCKET_PARK_MIN_M2 = _park_band("urban_pocket_park", 0, 200.0)
POCKET_PARK_MAX_M2 = _park_band("urban_pocket_park", 1, 900.0)
NEIGHBORHOOD_PARK_MIN_M2 = _park_band("neighborhood_park", 0, 2000.0)

POND_MIN_M2 = 300.0  # stormwater_retention_pond catalog range
POND_MAX_M2 = 9600.0
PLAZA_MIN_M2 = 1400.0  # formal_civic_plaza catalog range


@dataclass(frozen=True)
class BlockContext:
    index: int  # original block index (names stay "Block {i+1}")
    area_m2: float
    dist_to_centroid_m: float
    dist_to_edge_m: float
    transect: float  # 0 = site edge, 1 = deepest core
    fronts_spine: bool
    touches_boundary: bool  # the block borders the site edge
    dist_to_green_m: float  # to the signature green; inf if none
    abuts_low_rise: bool
    ceiling_floors: float | None


@dataclass(frozen=True)
class BandSpec:
    development_type: str
    aesthetic: str
    floors_delta: float | None  # relative to rules.floors (refinement bumps propagate)
    floors_abs: float | None  # absolute target (edge/anchor bands)
    typology: str
    # Exact catalog archetype (Master Planner-named). None = resolve by
    # (development_type, aesthetic, floors) as always.
    archetype_id: str | None = None
    # Exact executable LEGO variant when the parent alias cannot assemble on
    # its own (notably fixed, assembled-only landmark families).
    variant_id: str | None = None


@dataclass(frozen=True)
class ProgramSlot:
    """One piece of non-residential community program.

    A neighbourhood is not only fabric: it has a shop, a school, a clinic, a
    rec centre. Without them a plan cannot satisfy the doctrine's
    ``mobility.daily_needs`` (somewhere worth walking to) or
    ``legibility.civic_hierarchy`` (one building that earns being the
    exception), and the whole institutional half of the catalogue is
    unreachable.

    ``min_dwellings`` is the catchment that earns the program — a corner shop
    needs a few hundred residents, a school a few thousand. Slots are declared
    largest-catchment first and the plan takes the biggest it qualifies for.
    """

    development_type: str
    aesthetic: str
    floors: float
    typology: str
    min_dwellings: float
    label: str
    # Exact catalogue building. Pinned because a development_type alone is far
    # too coarse for program: institutional_education spans a lecture hall to a
    # parking structure, so an unpinned "school" slot resolved to
    # university_academic_complex in a 700-home neighbourhood.
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
# Runtime LEGO recipes have a stricter 0.80-1.20 production envelope than
# legacy contain-fit models. Keep two percentage points of headroom because
# the browser remeasures WGS84 coordinates after a different local projection;
# a nominal 0.800 fit can otherwise arrive as 0.793 and be rebound.
RUNTIME_BAR_SCALE_MIN = 0.82
RUNTIME_BAR_SCALE_MAX = 1.18
# Uniformly resizing a complete authored building is visually safe; stretching
# one facade axis relative to the other distorts windows, bays, and texture
# atlases. Keep alternate-axis distortion below 6% while retaining useful
# near-native size variety.
RUNTIME_BAR_MAX_AXIS_RATIO = 1.06
# Variant rotation: how many of the primary archetype's OWN variants join the
# bar cycle (same scale/family by construction), and the total option cap —
# bounds the distinct render refs and 3D cache keys one plan can demand.
MAX_VARIANT_BARS = 3
MAX_BAR_OPTIONS = 5


def _character_tuple(
    value: tuple[str, str, str | None] | tuple[str, str, str | None, str | None],
) -> tuple[str, str, str | None, str | None]:
    """Normalize legacy three-field alternates to the LEGO-aware contract."""

    if len(value) == 3:
        development_type, aesthetic, archetype_id = value
        return development_type, aesthetic, archetype_id, None
    return value


def runtime_lego_rectangle_fit(
    cell_width_m: float,
    cell_depth_m: float,
    candidate_width_m: float,
    candidate_depth_m: float,
) -> bool:
    """Whether an authored rectangle fits a cell directly or quarter-turned."""

    if (
        min(
            cell_width_m,
            cell_depth_m,
            candidate_width_m,
            candidate_depth_m,
        )
        <= 0
    ):
        return False
    orientations = (
        (
            cell_width_m / candidate_width_m,
            cell_depth_m / candidate_depth_m,
        ),
        (
            cell_depth_m / candidate_width_m,
            cell_width_m / candidate_depth_m,
        ),
    )
    return any(
        RUNTIME_BAR_SCALE_MIN <= scale_x <= RUNTIME_BAR_SCALE_MAX
        and RUNTIME_BAR_SCALE_MIN <= scale_y <= RUNTIME_BAR_SCALE_MAX
        and max(scale_x, scale_y) / min(scale_x, scale_y) <= RUNTIME_BAR_MAX_AXIS_RATIO
        for scale_x, scale_y in orientations
    )


@dataclass(frozen=True)
class Palette:
    bands: dict[str, BandSpec]  # keys: core | frontage | mid | edge | anchor
    spine_archetype_id: str | None = None  # direct road_archetype_id for the spine
    water_feature: bool = False  # water basin + greenway on the central green
    plaza: bool = False  # carve a civic plaza off the anchor block
    laneways: bool = False  # mid-block rear lanes on row_bars blocks
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
    # Roundabouts are specialized junction archetypes, never generic nodes.
    # Keep them opt-in so ordinary master plans use conventional right-angle
    # T- and cross-intersections.
    automatic_roundabouts: bool = False
    # ── Master Planner extensions ────────────────────────────────────────────
    # Declared style family (archetype_families.json): family-aware resolution
    # keeps every pick coherent. None = legacy resolution.
    style_family: str | None = None
    # Per-band character rotation: (development_type, aesthetic,
    # archetype_id, variant_id) tuples cycled across same-band blocks and bars.
    alternates: dict[str, tuple[tuple[str, str, str | None, str | None], ...]] = field(default_factory=dict)
    # planting_structure per green kind (park/pocket/courtyard/greenway/plaza),
    # mirrored by the globe's parkScatter — see master_planner.spec vocabulary.
    landscape: dict[str, str] = field(default_factory=dict)
    # Executable Public Realm LEGO appearance identities selected by the
    # Master Planner. Geometry stays owned by the park/street compilers; these
    # keys choose only a compatible, visible material/planting/furnishing
    # variant for each generated role.
    public_realm_variants: dict[str, str] = field(default_factory=dict)
    # Size-aware cycles for repeated roles. The AI-selected identity remains
    # first; larger neighborhoods rotate only variants proven compatible with
    # that same archetype family and metric section/program.
    public_realm_variant_cycles: dict[str, tuple[str, ...]] = field(default_factory=dict)
    # Direct green_space_archetype_id for the signature central green.
    central_archetype_id: str | None = None
    # Massing for the degenerate one-block site; None keeps the historic
    # perimeter courtyard.
    single_block_typology: str | None = None
    # Non-residential community program, largest catchment first. The anchor
    # block takes the biggest slot the plan's dwelling estimate earns; further
    # slots land on spine-fronting blocks (daily needs belong at the node).
    program: tuple[ProgramSlot, ...] = ()
    # Runtime-proven LEGO inventory. ``None`` preserves legacy/manual palette
    # behavior; a populated map makes every selection and floor snap stay
    # inside imported, executable families.
    allowed_archetype_ids: frozenset[str] | None = None
    allowed_variant_ids_by_archetype: dict[str, tuple[str, ...]] = field(default_factory=dict)
    supported_floors_by_selectable_id: dict[str, tuple[int, ...]] = field(default_factory=dict)
    target_dimensions_by_selectable_id: dict[str, tuple[float, float]] = field(default_factory=dict)
    # Trusted catalogue identities whose exact Sticker/LEGO family is not in
    # the current runtime inventory. They remain pinned to authored geometry
    # and floors, then the binder certifies them as planned massing.
    family_pending_archetype_ids: frozenset[str] = frozenset()


def selected_target_footprint(
    entry: dict | None,
    floors: int,
    measured_dims: dict | None,
    palette: Palette,
    selectable_id: str | None,
) -> TargetFootprint | None:
    """Return the exact runtime LEGO target after parent/variant selection."""

    if entry is None:
        return None
    dimensions = (
        palette.target_dimensions_by_selectable_id.get(selectable_id or "")
        if palette.allowed_archetype_ids is not None
        else None
    )
    if dimensions:
        width_m, depth_m = dimensions
        width_m = max(1.0, float(width_m))
        depth_m = max(1.0, float(depth_m))
        return TargetFootprint(
            round(width_m, 2),
            round(depth_m, 2),
            round(width_m / depth_m, 3),
            "runtime_lego",
        )
    return target_footprint(entry, floors, measured_dims)


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
    "economic": Palette(
        program=(
            ProgramSlot(
                "recreational_centre",
                "contemporary",
                2.0,
                "anchor_mass",
                900.0,
                "Recreation Centre",
                "community_recreation_centre",
            ),
            ProgramSlot(
                "commercial_retail",
                "contemporary",
                2.0,
                "anchor_mass",
                150.0,
                "Corner Retail",
                "new_york_corner_bodega",
            ),
        ),
        bands={
            "core": BandSpec("residential_multifamily", "contemporary_midrise", 1.0, None, "perimeter_block"),
            "frontage": BandSpec("mixed_use", "contemporary_urban", 0.0, None, "perimeter_block"),
            "mid": BandSpec("residential_multifamily", "contemporary", 0.0, None, "perimeter_block"),
            "edge": BandSpec("residential_single_family", "contemporary", None, 2.0, "row_bars"),
            "anchor": BandSpec("commercial_retail", "contemporary", None, 2.0, "anchor_mass"),
        },
        context_match=True,
        curvilinear=True,
        crescent_archetype_id="london_crescent_road",
        landscape={
            "park": "active_recreation",
            "pocket": "garden_courtyard",
            "courtyard": "garden_courtyard",
            "greenway": "formal_allee",
            "plaza": "formal_allee",
        },
    ),
    "city_policy": Palette(
        program=(
            ProgramSlot(
                "recreational_centre",
                "contemporary_urban",
                2.0,
                "anchor_mass",
                900.0,
                "Recreation Centre",
                "community_recreation_centre",
            ),
            ProgramSlot(
                "institutional_health",
                "contemporary_urban",
                3.0,
                "anchor_mass",
                500.0,
                "Community Clinic",
                "functionalist_healthcare",
            ),
            ProgramSlot(
                "commercial_retail",
                "contemporary_urban",
                2.0,
                "anchor_mass",
                150.0,
                "Corner Retail",
                "new_york_corner_bodega",
            ),
        ),
        bands={
            "core": BandSpec("residential_multifamily", "contemporary_midrise", 1.0, None, "perimeter_block"),
            "frontage": BandSpec("mixed_use", "contemporary_midrise", 1.0, None, "perimeter_block"),
            "mid": BandSpec("residential_multifamily", "brownstone", 0.0, None, "row_bars"),
            "edge": BandSpec("residential_duplex", "brownstone_rowhouse", None, 3.0, "row_bars"),
            "anchor": BandSpec(
                "institutional_health", "biophilic_contemporary_institutional", None, 4.0, "anchor_mass"
            ),
        },
        plaza=True,
        laneways=True,
        curvilinear=True,
        crescent_archetype_id="london_crescent_road",
        landscape={
            "park": "active_recreation",
            "pocket": "garden_courtyard",
            "courtyard": "formal_quad",
            "greenway": "formal_allee",
            "plaza": "formal_allee",
        },
    ),
    "city_beautiful": Palette(
        program=(
            ProgramSlot(
                "institutional_education",
                "classical",
                4.0,
                "anchor_mass",
                900.0,
                "School",
                "collegiate_gothic",
            ),
            ProgramSlot(
                "institutional",
                "classical",
                3.0,
                "anchor_mass",
                250.0,
                "Civic Hall",
                "civic_classical_building",
            ),
        ),
        bands={
            "core": BandSpec("mixed_use", "parisian", 2.0, None, "perimeter_block"),
            "frontage": BandSpec("mixed_use", "haussmann", 1.0, None, "perimeter_block"),
            "mid": BandSpec("residential_multifamily", "neoclassical", 0.0, None, "perimeter_block"),
            "edge": BandSpec("residential_duplex", "brownstone_rowhouse", None, 3.0, "row_bars"),
            "anchor": BandSpec("institutional_education", "classical", None, 4.0, "anchor_mass"),
        },
        spine_archetype_id="haussmann_boulevard",
        water_feature=True,
        plaza=True,
        water_archetype_id="fountain_water_feature",
        formal_water=True,
        landscape={
            "park": "formal_allee",
            "pocket": "formal_quad",
            "courtyard": "formal_quad",
            "greenway": "formal_allee",
            "plaza": "formal_allee",
        },
    ),
    "environmental": Palette(
        program=(
            ProgramSlot(
                "recreational_centre",
                "biophilic",
                2.0,
                "anchor_mass",
                900.0,
                "Recreation Centre",
                "community_recreation_centre",
            ),
            ProgramSlot(
                "institutional_health",
                "biophilic",
                3.0,
                "anchor_mass",
                500.0,
                "Community Clinic",
                "biophilic_healthcare",
            ),
            ProgramSlot(
                "commercial_retail",
                "biophilic",
                2.0,
                "anchor_mass",
                150.0,
                "Corner Retail",
                "new_york_corner_bodega",
            ),
        ),
        bands={
            "core": BandSpec("residential_multifamily", "eco_urban_green_architecture", 2.0, None, "perimeter_block"),
            "frontage": BandSpec("mixed_use", "scandinavian_nordic", 1.0, None, "perimeter_block"),
            "mid": BandSpec("residential_multifamily", "scandinavian_nordic", 0.0, None, "row_bars"),
            "edge": BandSpec("residential_duplex", "brownstone_rowhouse", None, 3.0, "row_bars"),
            "anchor": BandSpec("institutional_education", "biophilic", None, 3.0, "anchor_mass"),
            # curvilinear but NO crescent id: every local stays a woonerf, bowed or not.
        },
        water_feature=True,
        laneways=True,
        local_archetype_id="woonerf_shared_street",
        curvilinear=True,
        landscape={
            "park": "naturalistic_grove",
            "pocket": "garden_courtyard",
            "courtyard": "garden_courtyard",
            "greenway": "naturalistic_grove",
            "plaza": "formal_allee",
        },
    ),
    # ── Retired V1 preset ids (existing scenario rows redraw identically) ────
    "climate_first": Palette(
        bands={
            "core": BandSpec("residential_multifamily", "eco_urban_green_architecture", 2.0, None, "perimeter_block"),
            "frontage": BandSpec("mixed_use", "scandinavian_nordic", 1.0, None, "perimeter_block"),
            "mid": BandSpec("residential_multifamily", "scandinavian_nordic", 0.0, None, "row_bars"),
            "edge": BandSpec("residential_duplex", "brownstone_rowhouse", None, 3.0, "row_bars"),
            "anchor": BandSpec("institutional_education", "biophilic", None, 3.0, "anchor_mass"),
        },
        spine_archetype_id=None,
        water_feature=True,
        # Preserve legacy redraws created when Climate First explicitly
        # included a central traffic-calming roundabout.
        automatic_roundabouts=True,
        plaza=False,
        laneways=True,
        landscape={
            "park": "naturalistic_grove",
            "pocket": "garden_courtyard",
            "courtyard": "garden_courtyard",
            "greenway": "naturalistic_grove",
            "plaza": "formal_allee",
        },
    ),
    "as_of_right": Palette(
        bands={
            "core": BandSpec("residential_multifamily", "contemporary_urban", 3.0, None, "point_towers"),
            "frontage": BandSpec("mixed_use", "contemporary_urban", 1.0, None, "perimeter_block"),
            "mid": BandSpec("residential_multifamily", "contemporary_midrise", 0.0, None, "perimeter_block"),
            "edge": BandSpec("residential_single_family", "contemporary", None, 2.0, "row_bars"),
            "anchor": BandSpec("commercial_office", "modernist", None, 6.0, "anchor_mass"),
        },
        spine_archetype_id="arterial_boulevard",
        water_feature=False,
        plaza=True,
        laneways=False,
        landscape={
            "park": "open_meadow",
            "pocket": "garden_courtyard",
            "courtyard": "paved_plaza",
            "greenway": "formal_allee",
            "plaza": "formal_allee",
        },
    ),
    "lap_compliant": Palette(
        bands={
            "core": BandSpec("residential_multifamily", "contemporary_midrise", 1.0, None, "perimeter_block"),
            "frontage": BandSpec("mixed_use", "contemporary_midrise", 1.0, None, "perimeter_block"),
            "mid": BandSpec("residential_multifamily", "brownstone", 0.0, None, "row_bars"),
            "edge": BandSpec("residential_duplex", "brownstone_rowhouse", None, 3.0, "row_bars"),
            "anchor": BandSpec(
                "institutional_health", "biophilic_contemporary_institutional", None, 4.0, "anchor_mass"
            ),
        },
        spine_archetype_id=None,
        water_feature=False,
        plaza=True,
        laneways=True,
        landscape={
            "park": "active_recreation",
            "pocket": "garden_courtyard",
            "courtyard": "formal_quad",
            "greenway": "formal_allee",
            "plaza": "formal_allee",
        },
    ),
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
    bands = {key: replace(spec, typology="perimeter_block") for key, spec in palette.bands.items()}
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


# A plan can afford at most a couple of program buildings before it runs out
# of render references (see the reference-budget cap in test_plan_placement).
# Program therefore REPLACES fabric on the blocks it takes rather than being
# added on top of it, and the anchor block — which already carried a
# non-residential character — is the first slot rather than an extra one.
MAX_PROGRAM_SLOTS = 2


def estimate_dwellings(contexts: list[BlockContext], rules: RuleProfile) -> float:
    """Rough dwelling catchment for the plan, on plan_metrics' assumptions.

    Deliberately the same arithmetic the metrics engine reports, so the scale
    that earns a school is the scale the plan says it has.
    """
    from app.services.plan_metrics import ASSUMPTIONS

    developable = sum(ctx.area_m2 for ctx in contexts)
    efficiency = float(ASSUMPTIONS["residential_efficiency"]["value"])
    unit_area = float(ASSUMPTIONS["avg_unit_area_m2"]["value"])
    if unit_area <= 0:
        return 0.0
    return developable * rules.coverage_ratio * max(1.0, rules.floors) * efficiency / unit_area


def assign_program(
    contexts: list[BlockContext],
    palette: Palette,
    rules: RuleProfile,
    anchor_index: int | None,
) -> dict[int, ProgramSlot]:
    """Which blocks carry community program, by the catchment they serve.

    The anchor takes the largest slot the plan earns — a few hundred homes
    justify a corner shop, a few thousand a school. Any further slot goes to a
    spine-fronting block, because daily needs belong at the node where people
    already walk, not tucked into the quietest corner of the site.
    """
    if not palette.program or anchor_index is None:
        return {}
    dwellings = estimate_dwellings(contexts, rules)
    qualifying = [slot for slot in palette.program if dwellings >= slot.min_dwellings]
    if not qualifying:
        return {}

    assignments: dict[int, ProgramSlot] = {anchor_index: qualifying[0]}
    for slot in qualifying[1:MAX_PROGRAM_SLOTS]:
        candidate = next(
            (ctx.index for ctx in contexts if ctx.fronts_spine and ctx.index not in assignments),
            None,
        )
        if candidate is None:
            break
        assignments[candidate] = slot
    return assignments


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
        if (height is not None and float(height) <= _LOW_RISE_CEILING_M) or code.startswith(_LOW_RISE_LU_PREFIXES):
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
        contexts.append(
            BlockContext(
                index=index,
                area_m2=float(block.area),
                dist_to_centroid_m=float(block_centroid.distance(centroid)),
                dist_to_edge_m=float(edge_dists[index]),
                transect=(edge_dists[index] / max_edge) if max_edge > 0 else 0.0,
                fronts_spine=bool(spine_band is not None and block.distance(spine_band) < 0.5),
                touches_boundary=touches_boundary,
                dist_to_green_m=(
                    float(block.distance(signature_green_m)) if signature_green_m is not None else math.inf
                ),
                abuts_low_rise=bool(touches_boundary and any(g.distance(block) < 30.0 for g in low_rise_geoms)),
                ceiling_floors=ceiling,
            )
        )
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
    variety_seed: int | None = None,
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

    program_by_block = assign_program(contexts, palette, rules, anchor_index)

    context_avg_h = _dna_value(dna, "built_form", "context_avg_height_m")
    band_turns: dict[str, int] = {}
    supported_floors_by_parent = (
        {
            parent_id: tuple(
                sorted(
                    {
                        floor
                        for selectable_id in (
                            parent_id,
                            *palette.allowed_variant_ids_by_archetype.get(parent_id, ()),
                        )
                        for floor in palette.supported_floors_by_selectable_id.get(selectable_id, ())
                    }
                )
            )
            for parent_id in palette.allowed_archetype_ids
        }
        if palette.allowed_archetype_ids is not None
        else None
    )

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
        program_slot = program_by_block.get(ctx.index)
        if program_slot is not None:
            # Program replaces the band's character on this block outright:
            # the school IS the building here, not a housing block wearing a
            # school's development_type.
            spec = BandSpec(
                development_type=program_slot.development_type,
                aesthetic=program_slot.aesthetic,
                floors_delta=None,
                floors_abs=program_slot.floors,
                typology=program_slot.typology,
                archetype_id=program_slot.archetype_id,
            )
        development_type = spec.development_type
        aesthetic = spec.aesthetic
        arch_hint = spec.archetype_id
        variant_hint = spec.variant_id
        if program_slot is None and band == "mid" and (base_type or base_aesthetic):
            # Expert override changes the character — a pinned id no longer applies.
            arch_hint = None
            variant_hint = None
            if base_type:
                development_type = base_type
            if base_aesthetic:
                aesthetic = base_aesthetic

        # Character rotation across same-band blocks. Options carry the
        # catalog parent plus an exact executable variant when required.
        options: list[tuple[str, str, str | None, str | None]] = [
            (development_type, aesthetic, arch_hint, variant_hint)
        ]
        # A program block is that program. Rotating it through the band's
        # alternates would turn the school back into an apartment block.
        for raw_character in () if program_slot is not None else palette.alternates.get(band, ()):
            character = _character_tuple(raw_character)
            if character not in options:
                options.append(character)
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
                character = (
                    other.development_type,
                    other.aesthetic,
                    other.archetype_id,
                    other.variant_id,
                )
                if character not in options:
                    options.append(character)
                for raw_alt in palette.alternates.get(bk, ()):
                    alt = _character_tuple(raw_alt)
                    if alt not in options:
                        options.append(alt)
        turn = band_turns.get(band, 0)
        band_turns[band] = turn + 1
        development_type, aesthetic, arch_hint, variant_hint = options[turn % len(options)]

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

        # Same band, different block => a different entry from the SAME
        # coherent pool. Without this every block that resolves to one tie
        # group stamps the identical archetype, which is what collapsed a
        # 224-entry catalogue onto ~26 buildings. Seeded from the site hash
        # and the block index, so a given site always redraws identically.
        block_seed = None if variety_seed is None else (variety_seed + ctx.index * 31 + turn) % 1_000_003

        def _resolve_entry(dev: str, aes: str, aid: str | None) -> dict | None:
            if aid and (palette.allowed_archetype_ids is None or aid in palette.allowed_archetype_ids):
                pinned = dims_by_id().get(aid)
                if pinned is not None and pinned.get("usable"):
                    return pinned
            return resolve_building_archetype(
                dev,
                aes,
                floors_int,
                prefer_family=palette.style_family,
                allowed_archetype_ids=palette.allowed_archetype_ids,
                supported_floors_by_archetype=supported_floors_by_parent,
                variety_seed=block_seed,
            )

        entry = _resolve_entry(development_type, aesthetic, arch_hint)
        selected_variant_id: str | None = None
        if entry is not None and palette.allowed_archetype_ids is not None:
            if entry["id"] in palette.family_pending_archetype_ids:
                selected_variant_id = variant_hint
            else:
                selection_ids = (
                    entry["id"],
                    *palette.allowed_variant_ids_by_archetype.get(entry["id"], ()),
                )
                preferred = variant_hint or entry["id"]
                candidates = [
                    (
                        abs(supported_floor - floors_int),
                        0 if selectable_id == preferred else 1,
                        selectable_id,
                        supported_floor,
                    )
                    for selectable_id in selection_ids
                    for supported_floor in palette.supported_floors_by_selectable_id.get(selectable_id, ())
                ]
                if not candidates:
                    entry = None
                else:
                    _, _, selectable_id, floors_int = min(candidates)
                    floors = float(floors_int)
                    selected_variant_id = selectable_id if selectable_id != entry["id"] else None
        target = selected_target_footprint(
            entry,
            floors_int,
            measured_dims,
            palette,
            selected_variant_id or (entry["id"] if entry else None),
        )
        measured_entry = (measured_dims or {}).get(entry["id"]) if entry else None

        # Per-bar options: the primary archetype's OWN VARIANTS come first
        # (same building, different sub-style — a real streetscape), then the
        # band's other characters when their frontage fits the carved grid.
        bar_options: list[BarOption] = []
        if entry is not None:
            primary_variant = selected_variant_id or (measured_entry.variant_id if measured_entry else None)
            available_variants = (
                variants_of(entry["id"])
                if entry["id"] in palette.family_pending_archetype_ids
                else (
                    palette.allowed_variant_ids_by_archetype.get(entry["id"], ())
                    if palette.allowed_archetype_ids is not None
                    else variants_of(entry["id"])
                )
            )
            for vid in available_variants:
                if vid == primary_variant:
                    continue
                if (
                    palette.allowed_archetype_ids is not None
                    and entry["id"] not in palette.family_pending_archetype_ids
                    and floors_int not in palette.supported_floors_by_selectable_id.get(vid, ())
                ):
                    continue
                if (
                    palette.allowed_archetype_ids is not None
                    and entry["id"] not in palette.family_pending_archetype_ids
                ):
                    variant_dimensions = palette.target_dimensions_by_selectable_id.get(vid)
                    if (
                        target is None
                        or variant_dimensions is None
                        or not runtime_lego_rectangle_fit(
                            target.width_m,
                            target.depth_m,
                            variant_dimensions[0],
                            variant_dimensions[1],
                        )
                    ):
                        continue
                bar_options.append(
                    BarOption(
                        development_type=development_type,
                        aesthetic=aesthetic,
                        archetype_id=entry["id"],
                        variant_id=vid,
                    )
                )
                if len(bar_options) >= MAX_VARIANT_BARS:
                    break
        if entry is not None and len(options) > 1:
            seen_ids = {entry["id"]}
            for dev, aes, aid, option_variant_id in options:
                if (dev, aes, aid, option_variant_id) == (
                    development_type,
                    aesthetic,
                    arch_hint,
                    variant_hint,
                ):
                    continue
                alt = _resolve_entry(dev, aes, aid)
                if alt is None or alt["id"] in seen_ids:
                    continue
                alt_variant_id = option_variant_id
                if palette.allowed_archetype_ids is not None:
                    selection_ids = tuple(
                        dict.fromkeys(
                            (
                                alt_variant_id,
                                alt["id"],
                                *palette.allowed_variant_ids_by_archetype.get(alt["id"], ()),
                            )
                        )
                    )
                    alt_selectable_id = next(
                        (
                            selectable_id
                            for selectable_id in selection_ids
                            if selectable_id
                            and floors_int in palette.supported_floors_by_selectable_id.get(selectable_id, ())
                            and (dimensions := palette.target_dimensions_by_selectable_id.get(selectable_id))
                            is not None
                            and target is not None
                            and runtime_lego_rectangle_fit(
                                target.width_m,
                                target.depth_m,
                                dimensions[0],
                                dimensions[1],
                            )
                        ),
                        None,
                    )
                    if alt_selectable_id is None:
                        continue
                    alt_variant_id = alt_selectable_id if alt_selectable_id != alt["id"] else None
                alt_target = selected_target_footprint(
                    alt,
                    floors_int,
                    measured_dims,
                    palette,
                    alt_variant_id or alt["id"],
                )
                if target is not None and alt_target is not None:
                    ratio = alt_target.width_m / max(target.width_m, 0.1)
                    if not (BAR_WIDTH_COMPAT_LO <= ratio <= BAR_WIDTH_COMPAT_HI):
                        continue
                seen_ids.add(alt["id"])
                alt_measured = (measured_dims or {}).get(alt["id"])
                bar_options.append(
                    BarOption(
                        development_type=dev,
                        aesthetic=aes,
                        archetype_id=alt["id"],
                        variant_id=alt_variant_id or (alt_measured.variant_id if alt_measured else None),
                    )
                )
                if len(bar_options) >= MAX_BAR_OPTIONS:
                    break

        plans[ctx.index] = BlockPlan(
            development_type=development_type,
            aesthetic=aesthetic,
            floors_target=round(float(floors), 1),
            typology=typology,
            band=band,
            archetype_id=entry["id"] if entry else None,
            variant_id=selected_variant_id or (measured_entry.variant_id if measured_entry else None),
            target=target,
            bar_options=tuple(bar_options),
        )
    return plans


# --- open space -----------------------------------------------------------------


@dataclass(frozen=True)
class GreenSpec:
    geom_m: BaseGeometry
    kind: str  # "central" | "pocket" | "plaza" | "pond" | "greenway"
    name_suffix: str
    archetype_id: str | None  # direct green_space_archetype_id, else area-band resolve


@dataclass(frozen=True)
class OpenSpacePlan:
    specs: list[GreenSpec] = field(default_factory=list)
    consumed_indices: frozenset[int] = frozenset()
    carved_blocks: dict[int, BaseGeometry] = field(default_factory=dict)
    central_geom_m: BaseGeometry | None = None
    open_area_m2: float = 0.0


def organic_basin(
    center: Point,
    rx: float,
    ry: float,
    angle_deg: float,
    seed: int,
    vertices: int = 64,
    formal: bool = False,
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
    block: BaseGeometry,
    target_area: float,
    toward: BaseGeometry,
    *,
    min_short_span: float = 24.0,
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
    if min_short_span > 24.0 and min(width, span) < min_short_span:
        return None, None
    depth = max(14.0, min(target_area / width, span - 32.0))
    if span - depth < 30.0:
        return None, None
    toward_pt = affinity.rotate(toward if isinstance(toward, Point) else toward.centroid, -angle, origin=origin)
    near_min = abs(toward_pt.y - miny) <= abs(maxy - toward_pt.y)
    strip = box(minx - 1, miny, maxx + 1, miny + depth) if near_min else box(minx - 1, maxy - depth, maxx + 1, maxy + 1)
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


def _split_park_with_gap(
    park: BaseGeometry,
    *,
    gap_m: float = 4.0,
) -> tuple[Polygon, Polygon] | None:
    """Divide a reserved green into two real parks separated by a path band."""

    angle = _long_axis_angle(park)
    origin = park.centroid
    work = make_valid(affinity.rotate(park, -angle, origin=origin))
    minx, miny, maxx, maxy = work.bounds
    if maxx - minx < 32.0 + gap_m:
        return None
    split_x = (minx + maxx) / 2.0
    gap = box(split_x - gap_m / 2.0, miny - 1.0, split_x + gap_m / 2.0, maxy + 1.0)
    pieces = [piece for piece in iter_polygons(make_valid(work.difference(gap))) if piece.area >= POCKET_PARK_MIN_M2]
    if len(pieces) != 2:
        return None
    rotated = [affinity.rotate(piece, angle, origin=origin) for piece in pieces]
    return rotated[0], rotated[1]


def select_open_space(
    *,
    blocks: list[BaseGeometry],
    boundary_m: BaseGeometry,
    rules: RuleProfile,
    palette: Palette,
    network: StreetNetwork,
    seed: int,
    target_count: int | None = None,
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

    # A compact infill/TOD parcel can be too small for even one internal
    # street, but that must not erase an explicitly requested park. Carve a
    # full-frontage green from one end of the sole block and leave a clean,
    # buildable remainder. The previous len(blocks) >= 2 gate produced 0 m2
    # open space for exactly this common station-area condition.
    target_count = max(1, min(8, int(target_count))) if target_count is not None else None

    if len(blocks) == 1:
        central_block = blocks[0]
        park, remainder = _carve_park_strip(
            central_block,
            max(open_target, min(central_block.area * 0.18, 1400.0)),
            boundary_m.centroid,
            # A lone narrow block has no neighbouring parcel to absorb the
            # lost depth. Requiring a wider cross-span prevents the park strip
            # from forcing perimeter or row-bar ends into unusable slivers.
            min_short_span=24.0 if target_count else 70.0,
        )
        if park is not None and remainder is not None:
            central = park
            carved[0] = remainder
            open_area = float(park.area)
            specs.append(GreenSpec(park, "central", "Park", palette.central_archetype_id))
            # An explicit multi-park brief on a compact station parcel must
            # produce separately measurable polygons, not reinterpret a
            # courtyard or leftover sliver as the second park. Carve bounded
            # pocket parks from the remaining developable block with a real
            # buildable remainder after every cut.
            explicit_pockets = max(0, (target_count or 1) - 1)
            current_remainder = remainder
            for pocket_index in range(explicit_pockets):
                piece, next_remainder = _carve_corner(
                    current_remainder,
                    boundary_m.exterior,
                    20.0,
                    20.0,
                )
                if piece is None or next_remainder is None:
                    break
                specs.append(
                    GreenSpec(
                        piece,
                        "pocket",
                        f"Pocket Park {pocket_index + 1}",
                        "urban_pocket_park",
                    )
                )
                open_area += float(piece.area)
                current_remainder = next_remainder
                carved[0] = current_remainder

            # Irregular site corners can make a 20 m corner cut unsafe even
            # though the already-reserved frontage green is ample. In that
            # case partition the reserved green with a 4 m path band. The two
            # outputs remain separately measurable and the gap cannot overlap
            # either park or any building.
            public_parks = [spec for spec in specs if spec.kind in {"central", "pocket"}]
            if target_count == 2 and len(public_parks) == 1:
                split_parks = _split_park_with_gap(park)
                if split_parks is not None:
                    park_a, park_b = split_parks
                    specs[0] = GreenSpec(park_a, "central", "Park", palette.central_archetype_id)
                    specs.append(GreenSpec(park_b, "pocket", "Pocket Park 1", "urban_pocket_park"))
                    open_area = float(park_a.area + park_b.area)
                    central = park_a

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
            lobes = [p for p in iter_polygons(decompose_holed(greenway, central)) if p.area >= 50.0]
            for n, lobe in enumerate(lobes):
                specs.append(
                    GreenSpec(
                        lobe,
                        "greenway",
                        f"Greenway {chr(65 + (n % 26))}",
                        "linear_park_greenway",
                    )
                )
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
            public_park_count = sum(spec.kind in {"central", "pocket"} for spec in specs)
            if (
                open_area >= open_target and (target_count is None or public_park_count >= target_count)
            ) or pocket_count >= 4:
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
            public_park_count = sum(spec.kind in {"central", "pocket"} for spec in specs)
            if (
                (open_area >= open_target and (target_count is None or public_park_count >= target_count))
                or (target_count is not None and public_park_count >= target_count)
                or len(consumed) >= max(1, len(blocks) - 1)
            ):
                break
            if i in consumed or i in carved:
                continue
            area = float(blocks[i].area)
            # The 900-2,000 m2 "resolver gap" this used to skip existed only in
            # the four-entry canonical ladder; the catalogue has 46 park
            # archetypes covering 1,200 m2 and open_space_archetypes resolves
            # against their real bands. Skipping these blocks now only loses
            # perfectly good neighbourhood greens.
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
            plaza_target: BaseGeometry = spine_segments[0].line if spine_segments else boundary_m.centroid
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
