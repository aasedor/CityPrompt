"""Design Doctrine — the canon the panel reasons from, as data.

Why this exists: the expert prompts used to carry one-line philosophy
fragments, so every expert argued from whatever it remembered about urbanism.
That produces fluent but generic plans. A world-class designer argues from a
named, citable body of principle with numbers attached — and can say WHICH
principle a move serves and what it costs.

Two halves, deliberately separated:

- ``DOCTRINE_THRESHOLDS`` — every number the doctrine asserts, in ONE place.
  ``coherence.py`` computes against these; the prompt text renders from these.
  A threshold is never restated as a literal anywhere else in this package, so
  tuning the canon cannot drift the audit away from the prompt.
- ``PRINCIPLES`` — the qualitative canon, each entry carrying its measurable
  test, its real attribution, the disciplines that own it, and the
  PARAMETER_VOCABULARY paths it bears on.

Invariant kept from the panel architecture: doctrine ADVISES. Nothing here
draws geometry, and no principle may reference a parameter path outside
``PARAMETER_VOCABULARY`` (enforced by test).

Thresholds marked "aligns with" mirror a constant the drawn-plan evaluator
(``plan_geometry/plan_evaluator.py``) already measures. They are restated here
rather than imported because this package must stay free of shapely/geometry
imports; the alignment is asserted by test, not by convention.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

# ---------------------------------------------------------------------------
# Thresholds — the doctrine's numbers. Single source of truth.
# ---------------------------------------------------------------------------

DOCTRINE_THRESHOLDS: dict[str, dict[str, Any]] = {
    # --- Massing arithmetic -------------------------------------------------
    "typical_storey_m": {
        "value": 3.2,
        "unit": "m",
        "note": "floor-to-floor for residential/office storeys above grade",
    },
    "ground_floor_premium_m": {
        "value": 1.3,
        "unit": "m",
        "note": "extra ground-floor height where the ground plane is commercial or mixed use",
    },
    "commercial_ground_floor_min_m": {
        "value": 4.5,
        "unit": "m",
        "note": "floor-to-floor below which a ground floor cannot let a real retail/commercial tenant",
        "source": "ULI/retail fit-out practice; Gehl active-frontage criteria",
    },
    # --- The street as a room ----------------------------------------------
    "enclosure_ratio_min": {
        "value": 0.17,
        "unit": "height:width",
        "note": "1:6 — below this the street stops reading as an enclosed space and becomes a gap",
        "source": "Alexander, A Pattern Language; Allan Jacobs, Great Streets",
    },
    "enclosure_ratio_comfort_low": {
        "value": 0.33,
        "unit": "height:width",
        "note": "1:3 — lower bound of the comfortable, well-defined street room",
        "source": "Allan Jacobs, Great Streets (1993)",
    },
    "enclosure_ratio_comfort_high": {
        "value": 1.0,
        "unit": "height:width",
        "note": "1:1 — upper bound of comfortable enclosure for a general street",
        "source": "Allan Jacobs, Great Streets (1993)",
    },
    "enclosure_ratio_max": {
        "value": 2.0,
        "unit": "height:width",
        "note": "2:1 — beyond this the street is a canyon: sky view, daylight and winter sun collapse",
        "source": "Gehl, Cities for People; winter-city solar access practice",
    },
    # --- Block and grain ----------------------------------------------------
    "block_edge_max_m": {
        "value": 150.0,
        "unit": "m",
        "note": "maximum block face before the walking network loses permeability",
        "source": "Jane Jacobs, short-block principle; Calgary Complete Streets intersection spacing",
        "aligns_with": "plan_evaluator.BLOCK_EDGE_MAX_M",
    },
    "block_edge_min_m": {
        "value": 60.0,
        "unit": "m",
        "note": "below this, street area and intersection count overwhelm developable land",
    },
    "intersection_density_target_per_km2": {
        "value": 40.0,
        "unit": "intersections/km2",
        "note": "walkable-grid benchmark for connectivity",
        "aligns_with": "plan_evaluator.INTERSECTION_TARGET_PER_KM2",
    },
    "coverage_max_perimeter_block": {
        "value": 0.65,
        "unit": "ratio",
        "note": "footprint coverage of net block area above which courtyards and light wells fail",
    },
    "frontage_rhythm_max_m": {
        "value": 30.0,
        "unit": "m",
        "note": "maximum uninterrupted facade length before the ground plane reads as a blank wall",
        "source": "Gehl, Cities for People — units per 100m of frontage",
    },
    # --- Open space and climate --------------------------------------------
    "park_access_radius_m": {
        "value": 400.0,
        "unit": "m",
        "note": "walking distance within which every dwelling should reach usable open space",
        "aligns_with": "plan_evaluator.PARK_ACCESS_RADIUS_M",
    },
    "open_space_share_min": {
        "value": 0.10,
        "unit": "ratio",
        "note": "minimum public open-space share of gross site area",
    },
    "canopy_target": {
        "value": 0.16,
        "unit": "ratio",
        "note": "canopy cover target",
        "source": "Calgary Urban Forest Strategy — 16% by 2060",
        "aligns_with": "plan_evaluator.CANOPY_TARGET",
    },
    "street_tree_min_row_m": {
        "value": 15.0,
        "unit": "m",
        "note": (
            "right-of-way below which a boulevard cannot carry continuous street trees "
            "alongside sidewalks and a travel lane — high canopy targets become undeliverable"
        ),
    },
    "structural_soil_min_row_m": {
        "value": 20.0,
        "unit": "m",
        "note": "right-of-way that comfortably carries large-species trees with real soil volume",
    },
    # --- Mobility -----------------------------------------------------------
    "fire_clear_width_m": {
        "value": 6.0,
        "unit": "m",
        "note": "unobstructed width required for emergency apparatus access — life safety, never traded",
        "source": "fire access route standard",
        "aligns_with": "community_rules.FIRE_CLEAR_WIDTH_M",
    },
    "row_min_two_way_m": {
        "value": 11.0,
        "unit": "m",
        "note": "narrowest credible two-way local street with a sidewalk on at least one side",
    },
    "row_max_local_m": {
        "value": 30.0,
        "unit": "m",
        "note": "above this a local street is a traffic corridor, not a neighbourhood street",
    },
    "tod_core_radius_m": {
        "value": 400.0,
        "unit": "m",
        "note": "5-minute walk — the transit-oriented intensity core",
        "source": "Calthorpe, The Next American Metropolis (1993)",
    },
    "tod_edge_radius_m": {
        "value": 800.0,
        "unit": "m",
        "note": "10-minute walk — outer limit of transit-supportive density",
    },
    # --- Format and intensity bands ----------------------------------------
    "missing_middle_max_floors": {
        "value": 4.0,
        "unit": "storeys",
        "note": "upper bound of the missing-middle band; above it the format is mid-rise, not gentle density",
        "source": "Alexander, A Pattern Language #21 Four-Storey Limit; Parolek, Missing Middle Housing",
    },
    "walkup_max_floors": {
        "value": 6.0,
        "unit": "storeys",
        "note": "above this an elevator and concrete/steel frame are required — a step change in cost",
    },
    "context_step_ratio": {
        "value": 2.0,
        "unit": "ratio",
        "note": (
            "maximum proposed height as a multiple of prevailing context height before a "
            "transition/step-down is required at the sensitive edge"
        ),
    },
    # --- Yield plausibility -------------------------------------------------
    "avg_unit_area_m2": {
        "value": 75.0,
        "unit": "m2",
        "note": "blended average unit size — mirrors plan_metrics.ASSUMPTIONS",
    },
    "residential_efficiency": {
        "value": 0.82,
        "unit": "ratio",
        "note": "net sellable area per gross floor area — mirrors plan_metrics.ASSUMPTIONS",
    },
    "yield_plausibility_band": {
        "value": 2.0,
        "unit": "ratio",
        "note": (
            "a stated unit count more than this multiple away (either direction) from the count "
            "implied by floors x coverage x site area is not a design position, it is an error"
        ),
    },
}


def threshold(key: str) -> float:
    """The doctrine's number for ``key``. Raises on an unknown key by design —
    a typo must fail loudly rather than silently disable an audit rule."""
    return float(DOCTRINE_THRESHOLDS[key]["value"])


# ---------------------------------------------------------------------------
# Principles — the qualitative canon
# ---------------------------------------------------------------------------

# Disciplines map onto registry agent_ids, plus "design_director" for the
# synthesis voice that owns whole-plan composition.
DISCIPLINES = (
    "land_use_zoning",
    "mobility",
    "built_form_urban_design",
    "climate_public_realm",
    "design_director",
)


@dataclass(frozen=True)
class Principle:
    principle_id: str
    title: str
    disciplines: tuple[str, ...]
    statement: str  # imperative — what to do
    measure: str = ""  # how it is tested; "" when genuinely qualitative
    source: str = ""  # real attribution, shown to users in the design review
    philosophy_affinity: tuple[str, ...] = ()  # philosophies that amplify it
    parameter_paths: tuple[str, ...] = field(default_factory=tuple)


PRINCIPLES: tuple[Principle, ...] = (
    # --- Structure & legibility --------------------------------------------
    Principle(
        principle_id="legibility.image",
        title="Build a legible image",
        disciplines=("built_form_urban_design", "design_director"),
        statement=(
            "Give the plan the five elements a person navigates by: continuous paths, readable "
            "edges, districts with their own character, nodes where movement concentrates, and "
            "landmarks that can be seen from the paths. A plan a stranger cannot describe from "
            "memory has failed before it is built."
        ),
        measure="Every district reachable by a path that terminates on a node or landmark.",
        source="Kevin Lynch, The Image of the City (1960)",
        philosophy_affinity=("city_beautiful", "new_urbanism", "garden_city"),
        parameter_paths=("layout.strategy", "site.design_brief"),
    ),
    Principle(
        principle_id="legibility.serial_vision",
        title="Compose the walk, not the drawing",
        disciplines=("built_form_urban_design", "design_director"),
        statement=(
            "The plan is experienced as a sequence of unfolding views, never as the aerial it is "
            "drawn as. Bend or terminate streets so something is revealed; reserve the terminated "
            "vista for the building worth arriving at."
        ),
        measure="At least one terminated vista per district; primary axes end on a landmark, not a gap.",
        source="Gordon Cullen, Townscape (1961)",
        philosophy_affinity=("city_beautiful", "new_urbanism"),
        parameter_paths=("layout.strategy", "site.design_brief"),
    ),
    Principle(
        principle_id="legibility.civic_hierarchy",
        title="Let the civic building be the exception",
        disciplines=("built_form_urban_design", "land_use_zoning", "design_director"),
        statement=(
            "Ordinary fabric should be consistent and quiet; the civic, cultural or shared building "
            "earns the height, the material and the position that everything else concedes. Where "
            "everything is special, nothing reads as important."
        ),
        measure="One clearly dominant civic/shared anchor; fabric character otherwise consistent.",
        source="Camillo Sitte, City Planning According to Artistic Principles (1889); Leon Krier",
        philosophy_affinity=("city_beautiful", "garden_city"),
        parameter_paths=("buildings.development_aesthetic", "layout.strategy", "site.design_brief"),
    ),
    # --- Block & grain ------------------------------------------------------
    Principle(
        principle_id="grain.short_blocks",
        title="Keep blocks short and the network connected",
        disciplines=("mobility", "built_form_urban_design", "design_director"),
        statement=(
            "Short blocks multiply the routes between any two points, spread footfall across more "
            "frontages, and make walking competitive with driving. Long blocks and cul-de-sacs "
            "concentrate traffic onto a few collectors and strand the interior."
        ),
        measure=(
            "Block faces between block_edge_min_m and block_edge_max_m; intersection density at or "
            "above intersection_density_target_per_km2."
        ),
        source="Jane Jacobs, The Death and Life of Great American Cities (1961); Hillier, Space Syntax",
        philosophy_affinity=("new_urbanism", "fifteen_minute", "transit_oriented"),
        parameter_paths=("layout.strategy", "streets.row_width_m", "site.design_brief"),
    ),
    Principle(
        principle_id="grain.fine_parcels",
        title="Prefer many small parcels to few large ones",
        disciplines=("land_use_zoning", "built_form_urban_design"),
        statement=(
            "Fine grain lets different builders, budgets and eras contribute, which is what "
            "produces variety and resilience. One parcel developed by one hand at one moment "
            "produces a project, not a piece of city."
        ),
        measure="Uninterrupted facade runs at or below frontage_rhythm_max_m.",
        source="Jane Jacobs (1961); Krier, The Architecture of Community",
        philosophy_affinity=("new_urbanism", "missing_middle", "neighbourhood_context"),
        parameter_paths=("buildings.development_type", "buildings.development_aesthetic", "layout.strategy"),
    ),
    Principle(
        principle_id="grain.perimeter_block",
        title="Hold the block edge, protect the block interior",
        disciplines=("built_form_urban_design", "design_director"),
        statement=(
            "Build to the street edge and keep the soft, private, planted world inside the block. "
            "This one move produces the street wall, the defensible courtyard, and the screened "
            "location for parking and servicing at the same time."
        ),
        measure="Coverage at or below coverage_max_perimeter_block; parking and loading off the street frontage.",
        source="Alexander, A Pattern Language #106 Positive Outdoor Space; European perimeter-block practice",
        philosophy_affinity=("new_urbanism", "city_beautiful", "developer_feasibility"),
        parameter_paths=("layout.strategy", "buildings.development_type", "site.design_brief"),
    ),
    # --- The street as a room ----------------------------------------------
    Principle(
        principle_id="street.enclosure",
        title="Proportion the street as a room",
        disciplines=("built_form_urban_design", "mobility", "design_director"),
        statement=(
            "Building height and right-of-way width are one decision, never two. Too little height "
            "for the width and the street dissolves; too much and it becomes a canyon that loses "
            "sun. Change one and you must re-decide the other."
        ),
        measure=(
            "Height:width between enclosure_ratio_comfort_low and enclosure_ratio_comfort_high; "
            "never below enclosure_ratio_min or above enclosure_ratio_max."
        ),
        source="Allan Jacobs, Great Streets (1993); Alexander, A Pattern Language",
        philosophy_affinity=("new_urbanism", "city_beautiful", "neighbourhood_context"),
        parameter_paths=("buildings.floors", "buildings.height_m", "streets.row_width_m"),
    ),
    Principle(
        principle_id="street.active_frontage",
        title="Put eyes and doors on the street",
        disciplines=("land_use_zoning", "built_form_urban_design"),
        statement=(
            "Habitable rooms, entrances and windows must face the public realm. Safety after dark "
            "comes from ordinary occupied buildings overlooking the street, not from lighting "
            "levels or surveillance added later."
        ),
        measure="Ground floors habitable or commercial on all primary frontages; blank walls under frontage_rhythm_max_m.",
        source="Jane Jacobs (1961); Newman, Defensible Space (1972); CPTED",
        philosophy_affinity=("new_urbanism", "fifteen_minute", "transit_oriented"),
        parameter_paths=("buildings.development_type", "buildings.development_aesthetic", "site.design_brief"),
    ),
    Principle(
        principle_id="street.ground_floor_height",
        title="Give the ground floor room to change use",
        disciplines=("land_use_zoning", "built_form_urban_design"),
        statement=(
            "A generous ground floor can be a shop, a workshop, a clinic or a home over the "
            "building's life. A short one can only ever be what it was built as."
        ),
        measure="Commercial and mixed-use ground floors at or above commercial_ground_floor_min_m.",
        source="ULI retail practice; Gehl, Cities for People (2010)",
        philosophy_affinity=("fifteen_minute", "transit_oriented", "developer_feasibility"),
        parameter_paths=("buildings.height_m", "buildings.floors", "buildings.development_type"),
    ),
    # --- Human scale --------------------------------------------------------
    Principle(
        principle_id="human.walking_speed",
        title="Detail the plan for 5 km/h",
        disciplines=("built_form_urban_design", "climate_public_realm", "design_director"),
        statement=(
            "The first two storeys and the ground plane carry almost all of the experience of a "
            "place. Spend the material, the articulation and the planting budget there; the upper "
            "storeys can be quiet."
        ),
        measure="Doorway/unit rhythm and planting resolved at the frontage_rhythm_max_m interval.",
        source="Jan Gehl, Life Between Buildings (1971) and Cities for People (2010)",
        philosophy_affinity=("new_urbanism", "fifteen_minute", "tactical_urbanism"),
        parameter_paths=("buildings.development_aesthetic", "landscape.ground_texture", "site.design_brief"),
    ),
    Principle(
        principle_id="human.positive_space",
        title="Shape outdoor space, do not leave it over",
        disciplines=("climate_public_realm", "built_form_urban_design", "design_director"),
        statement=(
            "Open space must be a shaped, enclosed, sittable place with a clear edge and a reason "
            "to be there. Residual grass between buildings is not open space, and counting it as "
            "such is the most common way a plan overstates its own generosity."
        ),
        measure="Each open space bounded by building or street on the majority of its perimeter.",
        source="Alexander, A Pattern Language #106; Whyte, The Social Life of Small Urban Spaces (1980)",
        philosophy_affinity=("garden_city", "landscape_urbanism", "city_beautiful"),
        parameter_paths=("layout.strategy", "landscape.ground_texture", "site.design_brief"),
    ),
    # --- Open space network -------------------------------------------------
    Principle(
        principle_id="open_space.access",
        title="Everyone within a short walk of real open space",
        disciplines=("climate_public_realm", "land_use_zoning"),
        statement=(
            "Open space is a network with a hierarchy — doorstep greens, neighbourhood parks, the "
            "district park — not a single quantity to be met. Distance to the nearest usable space "
            "matters more than total hectares."
        ),
        measure="Every dwelling within park_access_radius_m of usable open space; share at or above open_space_share_min.",
        source="Calgary MDP open-space direction; Howard, Garden Cities of To-morrow (1902)",
        philosophy_affinity=("garden_city", "landscape_urbanism", "climate_resilience", "fifteen_minute"),
        parameter_paths=("layout.strategy", "landscape.tree_density", "site.design_brief"),
    ),
    Principle(
        principle_id="open_space.landscape_first",
        title="Read the land before drawing the roads",
        disciplines=("climate_public_realm", "design_director"),
        statement=(
            "Drainage, slope, existing trees and water set the plan's structure. A layout that "
            "fights the site's hydrology pays for it permanently in infrastructure and flood risk."
        ),
        measure="Low ground and drainage corridors held as open space rather than built on.",
        source="Ian McHarg, Design with Nature (1969)",
        philosophy_affinity=("landscape_urbanism", "climate_resilience", "garden_city"),
        parameter_paths=("layout.strategy", "landscape.ground_texture", "site.design_brief"),
    ),
    # --- Climate ------------------------------------------------------------
    Principle(
        principle_id="climate.canopy",
        title="Treat canopy as infrastructure",
        disciplines=("climate_public_realm",),
        statement=(
            "Shade continuity along walking routes is what makes a street usable in heat, and "
            "canopy is the cheapest cooling a plan can buy. But canopy is delivered by soil volume "
            "in the right-of-way — if the street is too narrow, the target is fiction."
        ),
        measure=(
            "Canopy at or above canopy_target, with rights-of-way at or above street_tree_min_row_m "
            "wherever a high planting intensity is claimed."
        ),
        source="Calgary Urban Forest Strategy (16% by 2060)",
        philosophy_affinity=("climate_resilience", "landscape_urbanism", "garden_city"),
        parameter_paths=("landscape.tree_density", "streets.row_width_m", "landscape.ground_texture"),
    ),
    Principle(
        principle_id="climate.winter_city",
        title="Design for the cold half of the year",
        disciplines=("climate_public_realm", "built_form_urban_design", "design_director"),
        statement=(
            "At this latitude the sun is low and the wind is the real enemy of public life. Keep "
            "winter sun on the south-facing public spaces and the primary walking routes, and "
            "break the prevailing wind with built form rather than asking planting to do it."
        ),
        measure="Primary public spaces hold midwinter midday sun; enclosure at or below enclosure_ratio_max on solar streets.",
        source="Norman Pressman, Northern Cityscape; winter-city design practice",
        philosophy_affinity=("climate_resilience", "garden_city"),
        parameter_paths=("layout.strategy", "buildings.floors", "site.design_brief"),
    ),
    Principle(
        principle_id="climate.absorbent_ground",
        title="Drain on the surface, visibly",
        disciplines=("climate_public_realm",),
        statement=(
            "Green stormwater infrastructure should be the amenity and the drainage at once — "
            "swales, rain gardens and permeable surfaces in the public realm rather than pipes "
            "under it. Piped-only drainage spends the same money and buys nothing else."
        ),
        measure="Permeable/planted treatment on the ground plane where open space and streets meet.",
        source="Calgary stormwater direction; low-impact development practice",
        philosophy_affinity=("climate_resilience", "landscape_urbanism"),
        parameter_paths=("landscape.ground_texture", "landscape.tree_density"),
    ),
    # --- Mobility -----------------------------------------------------------
    Principle(
        principle_id="mobility.transect",
        title="Grade intensity along a transect",
        disciplines=("land_use_zoning", "mobility", "design_director"),
        statement=(
            "Intensity should fall off legibly from the busiest node to the quietest edge. An "
            "abrupt jump between bands is what neighbours experience as an imposition and what "
            "makes an approval contested."
        ),
        measure=(
            "Highest intensity within tod_core_radius_m of the transit node, transitional to "
            "tod_edge_radius_m; height steps at sensitive edges within context_step_ratio."
        ),
        source="Duany/Plater-Zyberk, SmartCode transect; Calthorpe (1993)",
        philosophy_affinity=("transit_oriented", "new_urbanism", "neighbourhood_context"),
        parameter_paths=("buildings.floors", "buildings.height_m", "buildings.development_type", "layout.strategy"),
    ),
    Principle(
        principle_id="mobility.life_safety",
        title="Emergency access is not a trade-off",
        disciplines=("mobility",),
        statement=(
            "Every building must be reachable by emergency apparatus. Narrow, intimate streets are "
            "a legitimate and often excellent design position right up to this line and never past it."
        ),
        measure="All routes at or above fire_clear_width_m clear width.",
        source="fire access route standard",
        philosophy_affinity=(),
        parameter_paths=("streets.row_width_m",),
    ),
    Principle(
        principle_id="mobility.parking_position",
        title="Park behind, not in front",
        disciplines=("mobility", "built_form_urban_design"),
        statement=(
            "Where parking sits decides what the street becomes. Behind or beneath the building "
            "the street stays a street; in front of it the street becomes a parking lot with a "
            "road through it. Quantity is a policy question; position is a design one."
        ),
        measure="No surface parking between the building face and the primary street frontage.",
        source="Shoup, The High Cost of Free Parking (2005); new-urbanist practice",
        philosophy_affinity=("transit_oriented", "new_urbanism", "fifteen_minute"),
        parameter_paths=("layout.strategy", "site.design_brief"),
    ),
    Principle(
        principle_id="mobility.daily_needs",
        title="Put daily needs inside the walk",
        disciplines=("land_use_zoning", "mobility"),
        statement=(
            "A neighbourhood becomes walkable when there is somewhere worth walking to. Non-"
            "residential floorspace concentrated at the node and at corners does more for walking "
            "than any amount of sidewalk width."
        ),
        measure="Mixed use at the node and at primary corners; daily needs within tod_core_radius_m.",
        source="Moreno, 15-minute city; Calthorpe pedestrian pocket",
        philosophy_affinity=("fifteen_minute", "transit_oriented", "new_urbanism"),
        parameter_paths=("buildings.development_type", "layout.strategy", "site.design_brief"),
    ),
    # --- Context & transition ----------------------------------------------
    Principle(
        principle_id="context.transition",
        title="Transition before you contrast",
        disciplines=("land_use_zoning", "built_form_urban_design", "design_director"),
        statement=(
            "Where the proposal meets established lower-scale fabric, step the height down and "
            "match the setback rhythm. The transition is what converts an objection into an "
            "accepted edge, and it costs less yield than a refusal does."
        ),
        measure="Proposed height at a sensitive edge within context_step_ratio of prevailing context height.",
        source="Calgary MDP transition policy; contextual infill practice",
        philosophy_affinity=("neighbourhood_context", "missing_middle", "developer_feasibility"),
        parameter_paths=("buildings.floors", "buildings.height_m", "layout.strategy"),
    ),
    Principle(
        principle_id="context.format_fit",
        title="Choose a format the market and the crew can actually build",
        disciplines=("land_use_zoning", "design_director"),
        statement=(
            "Storey count is a construction-type decision before it is a design one: wood-frame "
            "walk-up, wood over podium, and concrete tower are three different businesses. A plan "
            "that lands just past a threshold pays the full step change for one extra floor."
        ),
        measure=(
            "Intensity sits inside a coherent construction band — missing_middle_max_floors, "
            "walkup_max_floors, or explicitly above with the cost step acknowledged."
        ),
        source="Parolek, Missing Middle Housing; construction-type cost practice",
        philosophy_affinity=("developer_feasibility", "missing_middle", "neighbourhood_context"),
        parameter_paths=("buildings.floors", "buildings.height_m", "buildings.unit_count"),
    ),
    Principle(
        principle_id="context.phasing",
        title="Make the first phase good on its own",
        disciplines=("land_use_zoning", "design_director"),
        statement=(
            "A master plan is delivered over a decade in pieces by different parties. Each phase "
            "must be a complete, decent place on the day it opens, not a fragment that only makes "
            "sense once the whole is finished — because the whole often is not."
        ),
        measure="First phase delivers its own frontage, open space and access.",
        source="incremental urbanism practice; Krier, urban quarter",
        philosophy_affinity=("developer_feasibility", "tactical_urbanism"),
        parameter_paths=("layout.strategy", "site.design_brief"),
    ),
    # --- Honesty ------------------------------------------------------------
    Principle(
        principle_id="integrity.arithmetic",
        title="Numbers must survive multiplication",
        disciplines=("land_use_zoning", "design_director"),
        statement=(
            "Unit count, storeys, coverage and site area are one system. A yield that the massing "
            "cannot physically hold is not an ambitious position — it is an error, and it "
            "discredits every defensible number beside it."
        ),
        measure="Stated unit count within yield_plausibility_band of the count implied by the massing.",
        source="development pro-forma practice",
        philosophy_affinity=("developer_feasibility",),
        parameter_paths=("buildings.unit_count", "buildings.floors", "buildings.height_m"),
    ),
    Principle(
        principle_id="integrity.trade_off",
        title="Name the cost of every position",
        disciplines=DISCIPLINES,
        statement=(
            "Every real design move gives something up. State what this plan sacrifices and for "
            "what — a recommendation presented as pure gain is either trivial or dishonest, and "
            "decision-makers can only choose between disclosed trade-offs."
        ),
        measure="Each contested parameter carries the losing position and the reason it lost.",
        source="planning practice; the panel's own trade-off contract",
        philosophy_affinity=(),
        parameter_paths=("site.design_brief",),
    ),
)


# ---------------------------------------------------------------------------
# Selection & rendering
# ---------------------------------------------------------------------------


def principles_for(
    discipline: str,
    philosophy_primary: str = "",
    philosophy_secondary: str = "",
    limit: int = 0,
) -> tuple[Principle, ...]:
    """Principles this discipline owns, philosophy-relevant ones first.

    Ordering is deterministic (affinity rank, then principle_id) so the prompt
    block stays byte-stable for a given discipline/philosophy pair — the
    runner's prompt cache depends on that.
    """
    owned = [p for p in PRINCIPLES if discipline in p.disciplines]

    def rank(principle: Principle) -> tuple[int, str]:
        if philosophy_primary and philosophy_primary in principle.philosophy_affinity:
            return (0, principle.principle_id)
        if philosophy_secondary and philosophy_secondary in principle.philosophy_affinity:
            return (1, principle.principle_id)
        # Universal principles (no affinity list) are canon for everyone and
        # outrank principles tuned to a philosophy this scenario is not running.
        if not principle.philosophy_affinity:
            return (2, principle.principle_id)
        return (3, principle.principle_id)

    ordered = sorted(owned, key=rank)
    return tuple(ordered[:limit] if limit else ordered)


def _threshold_line(key: str) -> str:
    spec = DOCTRINE_THRESHOLDS[key]
    unit = f" {spec['unit']}" if spec.get("unit") else ""
    return f"- {key} = {spec['value']}{unit}: {spec['note']}"


def doctrine_prompt_block(
    discipline: str,
    philosophy_primary: str = "",
    philosophy_secondary: str = "",
    limit: int = 8,
) -> str:
    """Render the canon for one expert's prompt.

    Only the thresholds actually named by the selected principles are listed,
    so an expert is never handed numbers it has no principle to apply.
    """
    selected = principles_for(discipline, philosophy_primary, philosophy_secondary, limit=limit)
    if not selected:
        return ""

    lines = [
        "DESIGN DOCTRINE — the canon you argue from. Cite the principle_id when a "
        "recommendation serves one, and say which principle you are trading away when they conflict.",
    ]
    for principle in selected:
        lines.append(f"\n[{principle.principle_id}] {principle.title}")
        lines.append(f"  {principle.statement}")
        if principle.measure:
            lines.append(f"  TEST: {principle.measure}")
        if principle.source:
            lines.append(f"  SOURCE: {principle.source}")

    named = sorted({key for principle in selected for key in DOCTRINE_THRESHOLDS if key in principle.measure})
    if named:
        lines.append("\nDOCTRINE THRESHOLDS (use these exact numbers; do not invent competing ones):")
        lines.extend(_threshold_line(key) for key in named)
    return "\n".join(lines)


def get_principle(principle_id: str) -> Principle | None:
    return next((p for p in PRINCIPLES if p.principle_id == principle_id), None)
