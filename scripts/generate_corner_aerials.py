#!/usr/bin/env python3
"""
Generate multi-angle AERIAL reference images (60° steep-oblique + 90° nadir)
for archetype variants. Used as reference images by the globe render pipeline
(see useGlobeAIRender.ts:collectArchetypeImages).

Two generation modes:

  1. PILOT (default): the hand-curated 3-zone Calgary set
     — vertical_farm, grand-magasin, disc-golf-course — variant 3 only.

  2. CATALOG: walk the buildingArchetypes.json catalog and generate for every
     variant of every building archetype. Subject descriptions are composed
     automatically from each variant's JSON metadata.
         python scripts/generate_corner_aerials.py --catalog=buildings --angle=60
         python scripts/generate_corner_aerials.py --catalog=buildings --angle=90

  For 90° generation, if the corresponding 60° aerial already exists on disk,
  it is sent as a SECOND reference image alongside the street-level variant —
  the 60° gives the model roof-pattern info the street-level can't show.

Methodology & tuning knobs: see `memory/project_aerial_ref_generation.md`.

CLI flags:
  --catalog=buildings|openspaces  generate for an entire JSON catalog
  --angle=60|90                   which angle to generate (default 60)
  --only=<substring>              filter by archetype title substring
  --limit=N                       only run the first N matching jobs
  --skip-existing                 skip jobs whose output file already exists (default ON)
  --no-skip-existing              overwrite existing output files
  --dry-run                       print planned jobs without hitting the API
"""

from __future__ import annotations

import base64
import json
import sys
import time
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
from typing import Any

import httpx

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SCRIPT_DIR.parent
_ENV_FILE = _PROJECT_ROOT / "backend" / ".env"
_PUBLIC_DIR = _PROJECT_ROOT / "frontend" / "public" / "archetypes"


def _load_api_key() -> str:
    if not _ENV_FILE.exists():
        print(f"ERROR: .env file not found at {_ENV_FILE}")
        sys.exit(1)
    for line in _ENV_FILE.read_text().splitlines():
        line = line.strip()
        if line.startswith("GEMINI_API_KEY="):
            return line.split("=", 1)[1].strip()
    print("ERROR: GEMINI_API_KEY not found in .env file")
    sys.exit(1)


API_KEY = _load_api_key()
MODEL = "gemini-3.1-flash-image-preview"
API_URL = (
    f"https://generativelanguage.googleapis.com/v1beta/"
    f"models/{MODEL}:generateContent?key={API_KEY}"
)

# ---------------------------------------------------------------------------
# Shared prompt fragments
# ---------------------------------------------------------------------------

CAMERA_BLOCKS = {
    # 60° = steep-oblique. Building = corner 3/4 showing roof + upper facades.
    # Open space = ground-plane depth with foreshortening.
    (60, "building"): (
        "CAMERA: Drone photograph from a STEEP-OBLIQUE aerial angle. "
        "Camera is approximately 80 METERS above ground level, tilted about "
        "60 DEGREES DOWN from horizontal (i.e. ~30 degrees off from straight-down "
        "nadir). Rooftop and upper facades are both clearly visible — this is the "
        "classic steep-drone survey angle where you can read the building's plan "
        "AND its upper facade material in one frame. Frame the subject from a "
        "CORNER perspective so two adjacent facades are both visible (not a "
        "head-on elevation). 50mm equivalent lens, f/5.6, ISO 100."
    ),
    (60, "open_space"): (
        "CAMERA: Drone photograph from a STEEP-OBLIQUE aerial angle. "
        "Camera is approximately 80 METERS above ground level, tilted about "
        "60 DEGREES DOWN from horizontal. The subject is a GROUND-LEVEL OPEN "
        "SPACE — there is NO BUILDING at this site, NO facades, NO rooftops, "
        "NO enclosed structures. Show the full site layout from above with "
        "clear ground-plane depth — playing surfaces, paths, fixtures, "
        "landscape features, and any small site furniture must all be readable "
        "at this scale. Foreshortening reveals site depth. 50mm equivalent "
        "lens, f/5.6, ISO 100. "
        "DOMINANT SUBJECT: the open-space site and its characteristic features "
        "(playing surfaces, baskets, tee pads, court lines, pavilions, etc.) "
        "MUST FILL the majority of the frame and be unmistakably the primary "
        "content. Do NOT render the subject as a small patch inside a larger "
        "generic lawn or park — the reference is a FOCUSED facility, and the "
        "output must read as a FOCUSED facility too. Crop tight enough that "
        "the site's identity is immediately obvious from this image alone."
    ),
    # 90° = true nadir (straight-down). Building = ROOFTOP plan view only,
    # no facades, no horizon, no sky. Open space = ground-plane layout flat.
    (90, "building"): (
        "CAMERA: Drone photograph from TRUE NADIR — camera pointing STRAIGHT "
        "DOWN at the ground. Camera is approximately 150 METERS above ground "
        "level. The view shows the building's ROOFTOP from directly above — "
        "roof form, dormers, skylights, chimneys, mechanical equipment, "
        "rooflines, parapets, and roof material pattern. NO horizon, NO sky, "
        "NO facades visible — this is a pure top-down plan view like a "
        "satellite image or Google Earth overhead. 35mm equivalent lens "
        "at this altitude for minimal distortion. The building's full "
        "rooftop footprint must fit within the frame."
    ),
    (90, "open_space"): (
        "CAMERA: Drone photograph from TRUE NADIR — camera pointing STRAIGHT "
        "DOWN at the ground. Camera is approximately 150 METERS above ground "
        "level. The view shows the open-space site from directly above — "
        "FLAT ground-plane layout with no perspective, no foreshortening, "
        "no horizon, no sky visible. Like a satellite image or overhead "
        "diagram. Playing surfaces, paths, court lines, tee pads, baskets, "
        "paved areas, landscape, and site fixtures are all visible in "
        "plan. 35mm equivalent lens. "
        "DOMINANT SUBJECT: the characteristic site features MUST FILL the "
        "majority of the frame — do NOT show the site as a small patch "
        "inside a larger generic field. Crop tight to the FOCUSED facility."
    ),
    # Streets = linear corridors. Different camera logic than point-site
    # open spaces: show 60-100m of corridor length, both edges visible.
    (60, "street"): (
        "CAMERA: Drone photograph from a STEEP-OBLIQUE aerial angle. "
        "Camera is approximately 60 METERS above ground level, tilted about "
        "60 DEGREES DOWN from horizontal, positioned so the street corridor "
        "runs DIAGONALLY across the frame (not straight down the middle). "
        "The subject is a LINEAR STREET/PATHWAY CORRIDOR — the full width "
        "of the street (curb-to-curb plus sidewalks or setbacks) is visible "
        "across the frame, AND approximately 60–100 meters of corridor "
        "LENGTH is shown. Building facades, walls, fences, or tree rows "
        "lining BOTH sides (or the appropriate sides for the archetype) "
        "are clearly visible and give the corridor its urban/suburban/"
        "rural context. 35mm equivalent lens, f/5.6, ISO 100."
    ),
    (90, "street"): (
        "CAMERA: Drone photograph from TRUE NADIR — camera pointing STRAIGHT "
        "DOWN at the ground. Camera is approximately 120 METERS above ground "
        "level. The view shows a LINEAR STREET/PATHWAY CORRIDOR from "
        "directly above — roadway surface with lane markings, crosswalks, "
        "parking stripes; sidewalks and curbs; street trees visible as "
        "round canopies; parked cars visible as rectangles along the curb; "
        "footprints of buildings/edges lining BOTH sides clearly visible. "
        "The corridor runs across the frame (diagonally or along one axis). "
        "NO horizon, NO sky, NO facades — pure top-down plan view like "
        "Google Earth. 24mm equivalent lens for wide plan coverage."
    ),
}

FRAMING_BLOCK_BUILDING = (
    "FRAMING: The subject is DOMINANT and CENTERED — it fills the majority of "
    "the frame and is unambiguously the primary content. Appropriate urban or "
    "rural context may surround it per the archetype's typical setting: a "
    "rowhouse/terrace MUST appear embedded in its row of attached neighbors "
    "(continuous streetwall extending to both sides); a main-street commercial "
    "building MUST sit within a continuous row of other shopfronts; a tower "
    "MUST rise above surrounding mid-rise fabric; a detached residence sits on "
    "its own plot with garden; an industrial building sits in an active "
    "industrial zone with yards and warehousing nearby; a civic monument may "
    "sit in its plaza or campus. Supporting context should READ as context — "
    "the primary subject must remain clearly the protagonist, never upstaged "
    "or cropped by neighbors."
)

FRAMING_BLOCK_OPEN_SPACE = (
    "FRAMING: The site is DOMINANT and CENTERED in the frame — its "
    "characteristic features (playing surfaces, paving, planting, water, "
    "fixtures) fill the majority of the image and the site's identity is "
    "unmistakable from this frame alone. Appropriate context appears at the "
    "edges per the site's typical setting: an urban park sits among "
    "surrounding residential or commercial streets; a civic plaza fronts "
    "institutional or cultural buildings on 1-3 sides; a sports/recreation "
    "facility is a FOCUSED site with its court lines, nets, equipment, and "
    "markings filling the frame (do NOT render a sports facility as a tiny "
    "patch inside a huge generic lawn); a waterfront space shows the water "
    "edge and adjacent urban strip; an ecological/stormwater feature sits "
    "within its hosting urban infrastructure; a landscape park fills the "
    "frame with meadow/woodland/paths with city edges only at the boundary. "
    "The site must read unambiguously as THIS SPECIFIC site type — never as "
    "a generic empty field or undifferentiated plaza."
)

FRAMING_BLOCK_STREET = (
    "FRAMING: A LINEAR STREET/PATHWAY CORRIDOR runs through the frame as "
    "the dominant subject — diagonally or along one axis, with 60–100 "
    "meters of length visible. The full width of the corridor (roadway + "
    "sidewalks + any setback planting) is clearly visible, and the BOTH "
    "sides of the street are lined with appropriate edge conditions per "
    "the archetype: a residential street has homes and front yards on both "
    "sides; a grand boulevard has formal building facades and tree rows; "
    "an alley/laneway has the backs of buildings with dumpsters and "
    "utilities; a pedestrian promenade has mixed-use shopfronts with "
    "outdoor seating; a waterfront path has water on one side and urban "
    "fabric on the other; a highway has embankments or sparse suburban "
    "edges; a transit corridor has stations, platforms, or track "
    "infrastructure. The street's CHARACTER — lane markings, parked cars, "
    "street trees, lighting, paving, bike lanes, and edge buildings — "
    "must be unmistakable from this frame alone. The corridor must NOT be "
    "rendered as a point-like site or a generic road in empty countryside."
)

STYLE_BLOCK = (
    "STYLE: Photorealistic drone photography. Sharp detail on materials and "
    "textures. Warm golden-hour afternoon sunlight casting crisp directional "
    "shadows that reveal facade depth. Natural color grading matching the "
    "reference image's palette. 8K detail."
)

NO_PEOPLE_BLOCK = (
    "CONSTRAINTS: No visible people, no pedestrians, no crowds, no human "
    "figures. Keep parked/moving vehicles minimal — a few quiet street cars "
    "at distance are acceptable if they match the archetype's urban setting, "
    "but no foreground traffic. The subject's materials, colors, and "
    "character must NEVER be changed from the reference."
)

FIDELITY_BLOCK_BUILDING = (
    "MATCH THE REFERENCE: The attached reference image shows the canonical "
    "street-level appearance of this archetype. Preserve EXACTLY the same "
    "materials, colors, proportions, ornamentation, roof type, and overall "
    "architectural character OF THE SUBJECT. The camera position has moved "
    "to an aerial angle, and appropriate urban/rural context should be added "
    "per the FRAMING instructions — but the subject's own material palette "
    "and architectural details must match the reference. Do not invent new "
    "architectural elements on the subject. Do not add modern glass curtain "
    "walls, minimalism, or fantasy elements unless they are clearly in the "
    "reference. Surrounding context buildings should be plausible but should "
    "not upstage or visually duplicate the subject."
)

FIDELITY_BLOCK_OPEN_SPACE = (
    "MATCH THE REFERENCE: The attached reference image is the canonical "
    "appearance of this archetype at ground level. Preserve EXACTLY the same "
    "ground surface materials, fixtures, colors, landscape elements, and "
    "overall character. The ONLY thing that should change is the camera "
    "position — it is now 80 meters in the air looking down at the site, "
    "instead of at eye level. Do not invent new structures or fixtures not "
    "present in the reference. The reference is a GROUND-LEVEL OPEN SPACE "
    "and the output must also be the same ground-level open space — not a "
    "building, not a structure, not a roof. The characteristic features "
    "of the site (as shown in the reference) must DOMINATE the output — "
    "the image must unambiguously read as THIS specific type of open "
    "space, not as a generic park or empty field."
)

FIDELITY_BLOCK_STREET = (
    "MATCH THE REFERENCE: The attached reference image shows the canonical "
    "street-level appearance of this street/pathway archetype. Preserve "
    "EXACTLY the same roadway/pathway surface material, lane configuration, "
    "sidewalk style, street tree species and spacing, lighting fixtures, "
    "paving patterns, and character of the buildings or edge conditions "
    "lining the corridor. The camera position has moved to an aerial angle, "
    "but the street's identity, dimensions, and material palette must match "
    "the reference. Do not invent new lane configurations, unfamiliar "
    "surface materials, or edge conditions not suggested by the reference. "
    "The result must read unambiguously as THIS specific street type — "
    "never as a generic road in featureless terrain."
)

# ---------------------------------------------------------------------------
# JSON catalog paths (for --catalog=... mode)
# ---------------------------------------------------------------------------

_CATALOG_PATHS = {
    "buildings": _PROJECT_ROOT / "frontend" / "src" / "data" / "buildingArchetypes.json",
    "openspaces": _PROJECT_ROOT / "frontend" / "src" / "data" / "openSpaceArchetypes.json",
    "streets": _PROJECT_ROOT / "frontend" / "src" / "data" / "streetPathArchetypes.json",
}

_CATALOG_ZONE_TYPE = {
    "buildings": "building",
    "openspaces": "open_space",
    "streets": "street",  # linear corridor — distinct from point-site open space
}


# Hand-curated pilot outputs that should NEVER be overwritten by catalog-mode
# runs even with --no-skip-existing. These were generated from pilot ARCHETYPES
# with tuned prose and are the quality baseline we're chasing.
PRESERVE_PATHS: set[Path] = {
    # Buildings pilots (hand-curated in ARCHETYPES list)
    _PUBLIC_DIR / "buildings" / "vertical_farm" / "variant_3_angle_60.jpg",
    _PUBLIC_DIR / "buildings" / "vertical_farm" / "variant_3_angle_90.jpg",
    _PUBLIC_DIR / "buildings" / "grand-magasin" / "variant_3_angle_60.jpg",
    _PUBLIC_DIR / "buildings" / "grand-magasin" / "variant_3_angle_90.jpg",
    _PUBLIC_DIR / "buildings" / "civic_monumental_institution" / "variant_0_angle_60.jpg",
    _PUBLIC_DIR / "buildings" / "civic_monumental_institution" / "variant_0_angle_90.jpg",
    # Open-space pilots (April 2026 original 5-angle set — keep the 60/90 we match)
    _PUBLIC_DIR / "openspaces" / "beach-volleyball-courts" / "variant_3_angle_60.jpg",
    _PUBLIC_DIR / "openspaces" / "beach-volleyball-courts" / "variant_3_angle_90.jpg",
    _PUBLIC_DIR / "openspaces" / "disc-golf-course" / "variant_3_angle_60.jpg",
    _PUBLIC_DIR / "openspaces" / "disc-golf-course" / "variant_3_angle_90.jpg",
    _PUBLIC_DIR / "openspaces" / "tennis-court-cluster" / "variant_3_angle_60.jpg",
    _PUBLIC_DIR / "openspaces" / "tennis-court-cluster" / "variant_3_angle_90.jpg",
    # Streets pilots (pedestrian-promenade from original 5-angle set)
    _PUBLIC_DIR / "streets" / "pedestrian-promenade" / "variant_0_angle_60.jpg",
    _PUBLIC_DIR / "streets" / "pedestrian-promenade" / "variant_0_angle_90.jpg",
}


# ---------------------------------------------------------------------------
# Subject composer — builds a natural-language description of a variant from
# the archetype metadata. Used in --catalog mode where hand-crafting 672+
# subject paragraphs isn't tractable.
# ---------------------------------------------------------------------------


_FAMILY_KEYWORDS: list[tuple[str, list[str]]] = [
    # Order matters — most specific first. Each entry: (family_name, keyword_list).
    ("attached_row", [
        "rowhouse", "row house", "row housing", "terrace", "brownstone",
        "streetwall", "street wall", "hydrostone", "tenement", "mews",
        "crescent", "eixample", "london townhouse", "working-class housing",
    ]),
    ("courtyard_block", ["courtyard housing", "almshouse", "courtyard family housing"]),
    ("tower_highrise", [
        "high-rise", "high rise", "point tower", "apartment tower",
        "office tower", "tower /", "tower+", "tower +",
        "skyscraper", "+15",
    ]),
    ("office_commercial", [
        "office / institutional", "office /", "office-",
        "office building", "commercial high-rise", "office tower /",
        "innovation district", "innovation campus",
    ]),
    ("transit_infra", [
        "transit", "metro station", "lrt station", "ferry terminal",
        "platform", "aviation", "transit station", "transit shelter",
        "fire station",
    ]),
    ("industrial", [
        "warehouse", "factory", "industrial", "brewery", "distillery",
        "data center", "workshop", "maritime", "waterfront warehouse",
        "waste-to-energy", "solar", "ev infrastructure", "heavy industrial",
        "light industrial", "general industrial", "converted industrial",
    ]),
    ("landmark_civic", [
        "civic", "institutional", "educational", "public library",
        "concert hall", "department store", "grand retail", "government",
        "cultural", "health care", "immersive experience", "market hall",
        "sports arena", "sports / arena", "residential pavilion",
    ]),
    ("mainstreet_commercial", [
        "main street", "shophouse", "heritage commercial", "food hall",
        "corner commercial", "corner retail", "bodega", "brasserie",
        "cafe / pub", "cafe / brasserie", "heritage main street",
        "canal house / early commercial", "covered passage", "arcade",
    ]),
    ("detached_residential", [
        "detached", "mansion", "bungalow", "lodge", "chalet",
        "georgian house", "canal house / historic", "medieval",
        "renaissance townhouse", "laneway", "lanehouse", "narrow-lot",
        "victorian detached", "victorian heritage", "duplex", "triplex",
        "single-family", "vancouver vernacular", "urban lanehouse",
        "infill residential",
    ]),
    ("mixed_use_midrise", [
        "mixed use", "mixed-use", "mid-rise", "mid-high rise", "boulevard",
        "tod mixed use", "tod residential", "walk-up", "contemporary townhouse",
        "contemporary mid-rise", "low density residential", "resort mixed use",
        "eco mixed use", "lodge mixed use", "hospitality", "hotel", "hotels",
        "high-density residential", "senior living", "assisted living",
        "social housing", "luxury apartment", "apartment building",
        "pre-war apartment",
    ]),
    ("recreation", [
        "rec centre", "recreation", "recreational", "vertical recreation",
        "sports / arena",
    ]),
    ("agricultural", ["indoor agriculture"]),
]


_FAMILY_CONTEXT: dict[str, str] = {
    "attached_row": (
        "It is ONE unit within a continuous row of attached units sharing "
        "party walls. The row extends to both the LEFT and RIGHT of the "
        "subject with similar (but visually distinguishable) neighboring "
        "units forming an unbroken streetwall — do NOT render this as a "
        "detached standalone building."
    ),
    "courtyard_block": (
        "It is a multi-unit residential block arranged around a shared "
        "interior courtyard, with the courtyard wing wrapping the site. "
        "Neighboring residential blocks of similar scale are visible on the "
        "surrounding streets."
    ),
    "tower_highrise": (
        "It is a prominent vertical structure rising well above surrounding "
        "mid-rise urban fabric — other tall buildings are visible nearby in "
        "a dense downtown context, but this tower is the dominant subject."
    ),
    "office_commercial": (
        "It is a working office or commercial building set within an urban "
        "business district — other commercial buildings, plazas, or "
        "streetfront activity appear in the adjacent context, with pedestrian "
        "or transit links visible nearby."
    ),
    "transit_infra": (
        "It is clearly a piece of public transit infrastructure — canopies, "
        "platforms, trackwork or roadway, and wayfinding signage are visible "
        "and read as infrastructural, not domestic or commercial."
    ),
    "industrial": (
        "It is an active working industrial building in an industrial zone, "
        "with truck/rail access, loading docks or yards, and adjacent "
        "warehousing visible nearby — NOT a gentrified loft conversion."
    ),
    "landmark_civic": (
        "It is a dominant institutional or civic structure, fronting a "
        "public boulevard, square, or institutional campus. Formal "
        "landscaping, plaza paving, or supporting context buildings of "
        "similar scale frame the site."
    ),
    "mainstreet_commercial": (
        "It stands in a continuous row of similar street-facing commercial "
        "buildings along an urban main street — neighboring shopfronts, "
        "awnings, and signage line the sidewalk to either side, forming a "
        "traditional urban commercial strip."
    ),
    "mixed_use_midrise": (
        "It is a mid-rise building set within a dense urban street wall of "
        "similar mixed-use structures — ground-floor retail frontage, "
        "upper-floor residences, and neighboring mid-rise blocks are visible."
    ),
    "detached_residential": (
        "It is a standalone detached residence on its own plot, with a modest "
        "garden, driveway, and setback from the street. Other detached homes "
        "on their own plots are visible along the residential street."
    ),
    "recreation": (
        "It is a working recreational or community facility, set within its "
        "typical urban or park context — associated outdoor activity areas, "
        "pathways, or landscaping are visible."
    ),
    "agricultural": (
        "It is a working agricultural/indoor-farming facility — glasshouses, "
        "growing infrastructure, or service yards are integral to the site."
    ),
}


_FAMILY_NEGATIVE: dict[str, str] = {
    "attached_row": (
        "Working urban attached-row frontage within a continuous streetwall, "
        "NOT a detached suburban cottage and NOT an isolated institutional "
        "building."
    ),
    "courtyard_block": (
        "Multi-unit courtyard residential block, NOT a single-family "
        "detached home and NOT an isolated high-rise tower."
    ),
    "tower_highrise": (
        "Dominant high-rise structure, NOT a low-rise suburban building "
        "and NOT a single-family home."
    ),
    "office_commercial": (
        "Contemporary urban office or commercial building, NOT a detached "
        "residence and NOT a suburban strip mall."
    ),
    "transit_infra": (
        "Public transit infrastructure, NOT a generic civic hall and NOT "
        "a shopping mall."
    ),
    "industrial": (
        "Working industrial/warehouse building, NOT a gentrified loft "
        "conversion and NOT a residential condo."
    ),
    "landmark_civic": (
        "Monumental institutional or civic landmark, NOT a generic office "
        "tower and NOT a suburban house."
    ),
    "mainstreet_commercial": (
        "Traditional urban street-front commercial building within a "
        "continuous row of shopfronts, NOT a modern glass office tower "
        "and NOT a suburban strip mall."
    ),
    "mixed_use_midrise": (
        "Mid-rise urban mixed-use building, NOT a high-rise tower and NOT "
        "a detached house."
    ),
    "detached_residential": (
        "Standalone detached residence on its own plot, NOT a row of "
        "attached townhouses and NOT a commercial or institutional block."
    ),
    "recreation": (
        "Working recreational or community facility, NOT a generic office "
        "building and NOT an industrial warehouse."
    ),
    "agricultural": (
        "Working agricultural building, NOT a generic office or residential "
        "tower."
    ),
}


def _detect_building_family(arch: dict[str, Any], variant: dict[str, Any]) -> str:
    """Return a family bucket for an archetype+variant pair.

    Two-stage detection: match against (subcategory + archetype title/id) FIRST,
    then fall back to variant label + id only if nothing matched. Rationale:
    variant labels describe stylistic treatment ("Industrial Loft Style" on a
    main-street archetype) and must NOT override the archetype's fundamental
    typology — otherwise a main-street building gets classified as industrial
    and renders with loading docks instead of shopfronts.
    """
    subcat = (arch.get("buildingSubcategory") or "").lower()
    title = (arch.get("title") or "").lower()
    aid = (arch.get("id") or "").lower()
    primary_hay = f"{subcat} || {title} || {aid}"

    for family, keywords in _FAMILY_KEYWORDS:
        for kw in keywords:
            if kw in primary_hay:
                return family

    # Fallback: include variant label/id for archetypes whose subcategory is
    # generic or "custom" but whose variant label reveals the type.
    vlabel = (variant.get("label") or "").lower()
    vid = (variant.get("id") or "").lower()
    full_hay = f"{primary_hay} || {vlabel} || {vid}"

    for family, keywords in _FAMILY_KEYWORDS:
        for kw in keywords:
            if kw in full_hay:
                return family

    return "generic"


def _articled(noun: str) -> str:
    """Return 'a <noun>' or 'an <noun>' based on leading vowel sound."""
    if not noun:
        return noun
    first = noun.strip()[0].lower()
    return f"an {noun}" if first in "aeiou" else f"a {noun}"


def compose_building_subject(arch: dict[str, Any], variant: dict[str, Any]) -> str:
    """Compose a 6-element evocative subject paragraph for a building variant.

    The 6 elements, in order:
      1. Opening (variant-label + archetype-title + subcategory).
      2. Description prose (variant or archetype).
      3. Materials + roof sentence (flowing, not JSON-list).
      4. Archetype-family context — rowhouse-in-row / tower-above-fabric / etc.
      5. Dimensions + floor count in natural prose.
      6. Negative clarifier — what the subject MUST NOT be rendered as.

    Element 4 and 6 are the critical additions over the old metadata-list
    composer. Without them, typologies that need neighbors (rowhouses,
    streetwalls, mainstreet commercial, towers-in-context) render as
    isolated standalone buildings. See feedback_aerial_subject_text_richness.md.
    """
    arch_title = (arch.get("title") or arch.get("id") or "").strip()
    variant_label = (variant.get("label") or "").strip()
    subcat = (arch.get("buildingSubcategory") or "").strip()

    family = _detect_building_family(arch, variant)
    parts: list[str] = []

    # --- Element 1: Opening ---
    if variant_label and arch_title and variant_label.lower() != arch_title.lower():
        opener = f"{_articled(variant_label)} variant of the {arch_title} archetype"
        if subcat:
            parts.append(f"{opener[0].upper()}{opener[1:]} — {_articled(subcat.lower())} typology.")
        else:
            parts.append(f"{opener[0].upper()}{opener[1:]}.")
    elif variant_label:
        w = _articled(variant_label)
        parts.append(f"{w[0].upper()}{w[1:]} building.")
    elif arch_title:
        w = _articled(arch_title)
        parts.append(f"{w[0].upper()}{w[1:]} building.")

    # --- Element 2: Description prose ---
    desc = (variant.get("description") or "").strip()
    if not desc:
        desc = (arch.get("description") or "").strip()
    if desc:
        if not desc.endswith((".", "!", "?")):
            desc += "."
        parts.append(desc)

    # --- Element 3: Materials + roof (flowing prose, NOT a list) ---
    facade = variant.get("facadeDetail") or arch.get("facadeDetail") or {}
    roof = variant.get("roofDetail") or arch.get("roofDetail") or {}
    mat_sentences: list[str] = []

    primary = (facade.get("primaryMaterial") or "").strip()
    secondary = (facade.get("secondaryMaterial") or "").strip()
    accent = (facade.get("accentMaterial") or "").strip()
    ground = (facade.get("groundFloor") or "").strip()
    palette = (facade.get("colorScheme") or "").strip()

    facade_pieces: list[str] = []
    if primary:
        facade_pieces.append(f"The facade is {primary}")
    if secondary:
        if facade_pieces:
            facade_pieces.append(f", complemented by {secondary}")
        else:
            facade_pieces.append(f"The facade features {secondary}")
    if accent:
        if facade_pieces:
            facade_pieces.append(f", with accents of {accent}")
        else:
            facade_pieces.append(f"Accents of {accent}")
    if facade_pieces:
        mat_sentences.append("".join(facade_pieces).rstrip(".") + ".")

    if ground:
        mat_sentences.append(f"At the ground floor: {ground}.")

    roof_form = (roof.get("form") or "").strip()
    roof_mat = (roof.get("material") or "").strip()
    roof_aerial = (roof.get("aerialAppearance") or "").strip()
    roof_feat = (roof.get("features") or "").strip()

    roof_pieces: list[str] = []
    if roof_form and roof_mat:
        roof_pieces.append(f"The roof is {roof_form} in {roof_mat}")
    elif roof_form:
        roof_pieces.append(f"The roof is {roof_form}")
    elif roof_mat:
        roof_pieces.append(f"Roof material: {roof_mat}")
    if roof_aerial:
        roof_pieces.append(f" — from above, {roof_aerial}")
    elif roof_feat:
        roof_pieces.append(f" — {roof_feat}")
    if roof_pieces:
        mat_sentences.append("".join(roof_pieces).rstrip(".") + ".")

    if palette:
        mat_sentences.append(f"Overall palette: {palette}.")

    if mat_sentences:
        parts.append(" ".join(mat_sentences))

    # --- Element 4: Archetype-family context ---
    ctx = _FAMILY_CONTEXT.get(family)
    if ctx:
        parts.append(ctx)

    # --- Element 5: Dimensions + floors ---
    width = arch.get("suggestedWidth_m")
    depth = arch.get("suggestedDepth_m")
    min_f = arch.get("minFloors")
    max_f = arch.get("maxFloors")

    dim_bits: list[str] = []
    if width and depth:
        dim_bits.append(f"approximately {width}m wide by {depth}m deep")
    if min_f and max_f:
        if min_f == max_f:
            dim_bits.append(f"{min_f} storeys tall")
        elif min_f < max_f:
            dim_bits.append(f"{min_f}–{max_f} storeys tall")
    if dim_bits:
        parts.append("Dimensions: " + ", ".join(dim_bits) + ".")

    # --- Element 6: Negative clarifier ---
    neg = _FAMILY_NEGATIVE.get(family)
    if neg:
        parts.append(neg)

    return " ".join(p for p in parts if p).strip()


_OS_FAMILY_MAP: dict[str, str] = {
    # Direct from aestheticCategory to our family bucket.
    "sports_recreation": "sports_facility",
    "neighborhood_public_realm": "urban_park",
    "ecological_resilience": "ecological_stormwater",
    "specialty_gardens": "specialty_garden",
    "water_features": "water_feature",
    "social_event_spaces": "social_event",
    "civic_plazas": "civic_plaza",
    "waterfront_spaces": "waterfront",
    "parking_areas": "parking_landscape",
    "landscape_parks": "landscape_park",
    # Regional/cultural categories mapped by character.
    "london_georgian": "civic_plaza",
    "newyork_urban": "urban_park",
    "vancouver_waterfront": "waterfront",
    "parisian_civic": "civic_plaza",
    "parisian_garden": "specialty_garden",
    "parisian_formal_garden": "specialty_garden",
    "amsterdam_landscape": "landscape_park",
    "amsterdam_courtyard": "urban_park",
    "amsterdam_civic": "civic_plaza",
    "barcelona_courtyard": "urban_park",
    "barcelona_civic": "civic_plaza",
    "barcelona_urban": "urban_park",
    "montreal_landscape": "landscape_park",
    "montreal_civic": "civic_plaza",
    "toronto_landscape": "landscape_park",
    "toronto_civic": "civic_plaza",
    "calgary_river": "waterfront",
    "calgary_civic": "civic_plaza",
    "halifax_victorian": "urban_park",
    "halifax_natural": "landscape_park",
    "custom": "generic",
}


_OS_FAMILY_CONTEXT: dict[str, str] = {
    "sports_facility": (
        "This is a FOCUSED sports/recreation facility — its playing surfaces, "
        "court lines, nets, goals, equipment, and fixtures FILL the majority "
        "of the frame. The facility's identity (tennis court / basketball "
        "court / football pitch / disc golf / etc.) must be unmistakable "
        "from this image alone. Only thin edges of perimeter fencing, "
        "neighboring trees, or adjacent streets should be visible at the "
        "frame edges — do NOT render this as a small facility inside a huge "
        "generic lawn."
    ),
    "urban_park": (
        "This park sits within an urban neighborhood — adjacent low-to-mid-rise "
        "buildings, residential streets, and neighboring lots are visible at "
        "the frame edges, giving the park a readable urban context."
    ),
    "ecological_stormwater": (
        "This is an engineered ecological/stormwater landscape (bioswale, "
        "rain garden, constructed wetland, green infrastructure) integrated "
        "with urban infrastructure — adjacent streets, sidewalks, buildings, "
        "or hardscape appear at the edges, while the ecological planting, "
        "water, and grading DOMINATE the frame."
    ),
    "specialty_garden": (
        "This is a specialty or themed garden — its signature planting, "
        "geometry, and features (rose beds, sensory plantings, geometric "
        "parterre, etc.) DOMINATE the frame. Surrounding park or urban "
        "context is visible only at the edges."
    ),
    "water_feature": (
        "This landscape has a prominent water feature (fountain, reflecting "
        "pool, water plaza, cascading water) as its identity. The water and "
        "its immediate surrounds DOMINATE the frame; surrounding civic or "
        "park context appears only at the edges."
    ),
    "social_event": (
        "This is an event/gathering space (event lawn, amphitheater, "
        "performance pavilion) — its event-ready surface, seating, and "
        "performance focal point DOMINATE the frame. Adjacent park or urban "
        "fabric appears only at the edges."
    ),
    "civic_plaza": (
        "This is a formal civic plaza fronting institutional or cultural "
        "buildings — the plaza's hardscape paving, monuments, and any "
        "fountains or installations DOMINATE the frame. Civic buildings, "
        "monuments, or cultural landmarks appear on 1-3 edges."
    ),
    "waterfront": (
        "This is a waterfront public space — the water edge, pier, "
        "promenade, quay, or boardwalk DOMINATES the frame. The water body "
        "is clearly visible on one side; an adjacent urban strip or park "
        "appears on the other."
    ),
    "parking_landscape": (
        "This is a parking-area landscape — the paved surface with marked "
        "stalls, shade trees, drainage swales, and any canopy structures "
        "DOMINATES the frame. Adjacent commercial, industrial, or retail "
        "context appears at the edges."
    ),
    "landscape_park": (
        "This is a large naturalistic landscape park — meadow, woodland, "
        "water features, and meandering paths fill the frame. City or "
        "suburban edges appear only as thin strips at the frame boundary."
    ),
    "generic": "",
}


_OS_FAMILY_NEGATIVE: dict[str, str] = {
    "sports_facility": (
        "A FOCUSED sports/recreation facility with characteristic markings "
        "and equipment filling the frame — NOT a generic park and NOT an "
        "empty grass lawn."
    ),
    "urban_park": (
        "A neighborhood-scale urban park with residential/commercial "
        "surroundings — NOT a generic empty green field and NOT a civic "
        "plaza."
    ),
    "ecological_stormwater": (
        "An engineered ecological/stormwater landscape — NOT a generic "
        "naturalistic park and NOT a building or enclosed structure."
    ),
    "specialty_garden": (
        "A themed or specialty garden with signature planting dominant — "
        "NOT a generic lawn and NOT an empty plaza."
    ),
    "water_feature": (
        "A landscape with a prominent water feature — NOT a generic plaza "
        "without water and NOT a generic park."
    ),
    "social_event": (
        "An event/gathering space with event infrastructure — NOT a sports "
        "facility and NOT a parking lot."
    ),
    "civic_plaza": (
        "A formal civic plaza with hardscape paving dominant — NOT a grass "
        "park and NOT an empty asphalt lot."
    ),
    "waterfront": (
        "A waterfront public space with the water edge dominant — NOT a "
        "park set back from the water and NOT a generic plaza."
    ),
    "parking_landscape": (
        "A parking-area landscape — NOT a generic park and NOT an empty "
        "plaza."
    ),
    "landscape_park": (
        "A large naturalistic landscape park — NOT a manicured formal "
        "garden and NOT a sports facility."
    ),
    "generic": "",
}


def _detect_open_space_family(arch: dict[str, Any], variant: dict[str, Any]) -> str:
    """Return a family bucket for an open-space archetype+variant pair."""
    aesth = (arch.get("aestheticCategory") or "").strip()
    if aesth in _OS_FAMILY_MAP:
        return _OS_FAMILY_MAP[aesth]
    # Fallback to spaceType
    st = (arch.get("spaceType") or "").strip().lower()
    if st == "plaza":
        return "civic_plaza"
    if st == "park":
        return "urban_park"
    return "generic"


def compose_open_space_subject(arch: dict[str, Any], variant: dict[str, Any]) -> str:
    """Compose a 6-element evocative subject paragraph for an open-space variant.

    Same structural approach as compose_building_subject: opening, description,
    features, family context, dimensions, negative clarifier. Leverages the
    rich prose already in styleProfile.landscapeCharacter and prompt.details
    fields of the open-space catalog — these are already evocative and only
    need light wrapping.
    """
    arch_title = (arch.get("title") or arch.get("id") or "").strip()
    variant_label = (variant.get("label") or "").strip()
    aesth_raw = (arch.get("aestheticCategory") or "").strip()
    aesth = aesth_raw.replace("_", " ") if aesth_raw else ""

    family = _detect_open_space_family(arch, variant)
    parts: list[str] = []

    # --- Element 1: Opening ---
    if variant_label and arch_title and variant_label.lower() != arch_title.lower():
        opener = f"{_articled(variant_label)} variant of the {arch_title} archetype"
        if aesth:
            parts.append(f"{opener[0].upper()}{opener[1:]} — {_articled(aesth)} typology.")
        else:
            parts.append(f"{opener[0].upper()}{opener[1:]}.")
    elif variant_label:
        w = _articled(variant_label)
        parts.append(f"{w[0].upper()}{w[1:]}.")
    elif arch_title:
        w = _articled(arch_title)
        parts.append(f"{w[0].upper()}{w[1:]}.")

    # --- Element 2: Description prose ---
    # Prefer variant.description (specific to the variant), then layer in
    # the archetype's rich landscapeCharacter prose if available.
    var_desc = (variant.get("description") or "").strip()
    if var_desc:
        parts.append(var_desc if var_desc.endswith((".", "!", "?")) else var_desc + ".")

    style_profile = arch.get("styleProfile") or {}
    landscape_char = (style_profile.get("landscapeCharacter") or "").strip()
    if landscape_char:
        parts.append(
            landscape_char if landscape_char.endswith((".", "!", "?")) else landscape_char + "."
        )
    else:
        arch_desc = (arch.get("description") or "").strip()
        if arch_desc and arch_desc != var_desc:
            parts.append(arch_desc if arch_desc.endswith((".", "!", "?")) else arch_desc + ".")

    # --- Element 3: Specific feature details ---
    prompt_obj = arch.get("prompt") or {}
    details = prompt_obj.get("details") or []
    if isinstance(details, list) and details:
        cleaned = [str(d).strip().rstrip(".") for d in details if str(d).strip()]
        if cleaned:
            parts.append("Key features: " + "; ".join(cleaned[:6]) + ".")

    # --- Element 4: Family context ---
    ctx = _OS_FAMILY_CONTEXT.get(family)
    if ctx:
        parts.append(ctx)

    # --- Element 5: Dimensions ---
    width = arch.get("suggestedWidth_m")
    depth = arch.get("suggestedDepth_m")
    area = arch.get("suggestedAreaSqm")
    dim_bits: list[str] = []
    if width and depth:
        dim_bits.append(f"approximately {width}m wide by {depth}m deep")
    if area:
        dim_bits.append(f"about {area} m² in area")
    if dim_bits:
        parts.append("Dimensions: " + ", ".join(dim_bits) + ".")

    # --- Element 6: Ground-level clarifier + family-specific negative ---
    parts.append(
        "This is a GROUND-LEVEL OPEN SPACE — no building, no enclosed "
        "structures; the subject is the ground plane, planting, and site "
        "fixtures themselves."
    )
    neg = _OS_FAMILY_NEGATIVE.get(family)
    if neg:
        parts.append(neg)

    return " ".join(p for p in parts if p).strip()


# ---------------------------------------------------------------------------
# Street composer — linear corridor archetypes need their own family taxonomy
# and prose style (corridor character + edge conditions + lane configuration).
# ---------------------------------------------------------------------------


_STREET_FAMILY_KEYWORDS: list[tuple[str, list[str]]] = [
    # Order matters; most specific first.
    ("highway_freeway", ["highway", "freeway", "expressway", "grade-separated"]),
    ("european_canal_street", [
        "gracht", "amsterdam-gracht", "canal street", "canal-street",
        "canal waterway", "canal-waterway",
    ]),
    ("waterfront_path", [
        "waterfront", "boardwalk", "river pathway", "bow river",
        "quayside", "harbourfront",
    ]),
    ("service_alley", [
        "alley", "laneway", "service lane", "steeg", "back-alley",
        "back alley", "commercial alley", "green alley", "back lane",
        "back-lane",
    ]),
    ("transit_corridor", [
        "brt", "bus rapid transit", "elevated rail", "elevated-rail",
        "lrt", "tram", "metro surface", "transit corridor",
    ]),
    ("cycling_corridor", [
        "cycle bridge", "dedicated cycle", "protected cycle", "cycle track",
        "cycling-only", "bike-only",
    ]),
    ("pedestrian_promenade", [
        "promenade", "pedestrian", "passatge", "passeig", "covered passage",
        "campus pedestrian", "campus-pedestrian", "passage",
    ]),
    ("grand_boulevard", [
        "haussmann", "boulevard", "eixample", "grand avenue", "allee",
        "parkway", "scenic parkway", "landmark bridge",
        "signature bridge", "vehicular bridge",
    ]),
    ("arterial_collector", [
        "arterial", "collector", "downtown thoroughfare", "thoroughfare",
        "commercial street", "main street", "main-street", "straat",
        "roundabout", "traffic circle",
    ]),
    ("residential_street", [
        "residential street", "residential", "cul-de-sac", "neighborhood",
        "halifax steep", "narrow residential", "infill",
        "crescent road", "crescent street", "terrace street",
        "brownstone side", "cherry blossom", "parisian rue", "parisian-rue",
        "soho cobblestone", "cobblestone street", "yield street",
    ]),
]


_STREET_FAMILY_CONTEXT: dict[str, str] = {
    "highway_freeway": (
        "This is a limited-access HIGHWAY or freeway — multiple wide lanes "
        "in each direction, painted lane lines, possibly a median or "
        "barrier, and shoulder lanes. Edges are embankments, sound walls, "
        "service roads, or sparse commercial/suburban context at setback — "
        "no residential houses directly fronting."
    ),
    "european_canal_street": (
        "This is a European canal street — a narrow roadway runs alongside "
        "a water canal with bridges at intervals. Historic terrace-house "
        "facades line the land side; the canal forms the other edge; trees "
        "and moored boats give it distinctive character."
    ),
    "waterfront_path": (
        "This is a waterfront pathway/promenade — a linear public path runs "
        "along a body of water (river, harbour, lake). Water is on one "
        "side, urban or park context on the other. Railings, benches, and "
        "paving define the path."
    ),
    "service_alley": (
        "This is a narrow service alley or laneway — typically 3-6m wide, "
        "bordered on both sides by the backs of buildings (rear facades, "
        "service doors, dumpsters, fire escapes, utility meters, garage "
        "doors). Pavement is typically unadorned asphalt or cobble."
    ),
    "transit_corridor": (
        "This is a transit-priority corridor — dedicated bus lanes, LRT/tram "
        "tracks, or elevated rail infrastructure dominates the corridor. "
        "Platforms, stations, shelters, or track structures are visible; "
        "surrounding urban context appears at the edges."
    ),
    "cycling_corridor": (
        "This is a cycling-priority corridor — dedicated cycle lanes or a "
        "separated cycle track dominates the path. Painted bike markings, "
        "bollards or planters separating from any motor traffic, and "
        "minimal parking. Surrounding context appears at the edges."
    ),
    "pedestrian_promenade": (
        "This is a pedestrian-priority street/promenade — NO through-traffic "
        "cars; decorative paving (setts, bricks, stone), street furniture "
        "(benches, bollards), outdoor cafe seating, and mixed-use shopfronts "
        "on both sides. People are walking/cycling in the main channel."
    ),
    "grand_boulevard": (
        "This is a GRAND urban boulevard — wide multi-lane roadway, formal "
        "tree rows on median and edges, continuous grand architectural "
        "facades on both sides, wide sidewalks. Reads unambiguously as a "
        "ceremonial avenue, NOT a suburban street."
    ),
    "arterial_collector": (
        "This is an urban arterial or collector street — moderate multi-lane "
        "roadway, painted lane lines, sidewalks, street trees, and "
        "commercial or mixed-use building frontages on both sides with "
        "storefronts or driveways."
    ),
    "residential_street": (
        "This is a residential street within a neighborhood — narrow to "
        "moderate roadway, parallel parking, sidewalks, mature street "
        "trees, and single-family or attached residential frontages on "
        "both sides (front yards, driveways, porches)."
    ),
    "generic_street": (
        "This is an urban street corridor — lane markings, sidewalks, and "
        "building or landscape edges on both sides."
    ),
}


_STREET_FAMILY_NEGATIVE: dict[str, str] = {
    "highway_freeway": (
        "Limited-access highway/freeway — NOT an urban residential street "
        "and NOT a pedestrian promenade."
    ),
    "european_canal_street": (
        "Historic European canal street with water and terrace houses — NOT "
        "a generic residential street and NOT a highway."
    ),
    "waterfront_path": (
        "Waterfront pathway with water on one side — NOT an interior street "
        "and NOT a park."
    ),
    "service_alley": (
        "Narrow service alley with backs of buildings — NOT a main street "
        "and NOT a grand boulevard."
    ),
    "transit_corridor": (
        "Transit-priority corridor with dedicated track/lane infrastructure "
        "— NOT a general-traffic road."
    ),
    "cycling_corridor": (
        "Cycling-priority path/lane — NOT a general auto arterial and NOT "
        "a sidewalk."
    ),
    "pedestrian_promenade": (
        "Pedestrian-priority promenade — NOT an auto-oriented street and "
        "NOT a highway."
    ),
    "grand_boulevard": (
        "Grand ceremonial boulevard — NOT a narrow residential street and "
        "NOT a suburban arterial."
    ),
    "arterial_collector": (
        "Urban arterial/collector street — NOT a quiet residential lane "
        "and NOT a highway."
    ),
    "residential_street": (
        "Residential neighborhood street — NOT a commercial arterial and "
        "NOT a grand boulevard."
    ),
    "generic_street": "An urban street corridor.",
}


def _detect_street_family(arch: dict[str, Any], variant: dict[str, Any]) -> str:
    """Return a family bucket for a street archetype+variant pair.

    Two-stage: match against subcategory/title/id first; variant label as
    fallback. Similar philosophy to _detect_building_family — keeps "Victorian
    Lamppost" as a residential street not a highway just because the variant
    label contains some industrial-sounding word.
    """
    title = (arch.get("title") or "").lower()
    aid = (arch.get("id") or "").lower()
    aesth = (arch.get("aestheticCategory") or "").lower()
    primary_hay = f"{title} || {aid} || {aesth}"

    for family, keywords in _STREET_FAMILY_KEYWORDS:
        for kw in keywords:
            if kw in primary_hay:
                return family

    vlabel = (variant.get("label") or "").lower()
    vid = (variant.get("id") or "").lower()
    full_hay = f"{primary_hay} || {vlabel} || {vid}"
    for family, keywords in _STREET_FAMILY_KEYWORDS:
        for kw in keywords:
            if kw in full_hay:
                return family

    # Fall back on aestheticCategory
    if aesth == "pedestrian_oriented":
        return "pedestrian_promenade"
    if aesth == "transit_oriented":
        return "transit_corridor"
    if aesth == "cycling_oriented":
        return "cycling_corridor"
    return "generic_street"


def compose_street_subject(arch: dict[str, Any], variant: dict[str, Any]) -> str:
    """Compose a 6-element subject paragraph for a street/pathway variant."""
    arch_title = (arch.get("title") or arch.get("id") or "").strip()
    variant_label = (variant.get("label") or "").strip()
    aesth_raw = (arch.get("aestheticCategory") or "").strip()
    aesth = aesth_raw.replace("_", " ") if aesth_raw else ""

    family = _detect_street_family(arch, variant)
    parts: list[str] = []

    # E1: Opening
    if variant_label and arch_title and variant_label.lower() != arch_title.lower():
        opener = f"{_articled(variant_label)} variant of the {arch_title} archetype"
        if aesth:
            parts.append(f"{opener[0].upper()}{opener[1:]} — {_articled(aesth)} street.")
        else:
            parts.append(f"{opener[0].upper()}{opener[1:]}.")
    elif variant_label:
        w = _articled(variant_label)
        parts.append(f"{w[0].upper()}{w[1:]} street.")
    elif arch_title:
        w = _articled(arch_title)
        parts.append(f"{w[0].upper()}{w[1:]}.")

    # E2: Description prose (variant-specific + archetype corridor character)
    var_desc = (variant.get("description") or "").strip()
    if var_desc:
        parts.append(var_desc if var_desc.endswith((".", "!", "?")) else var_desc + ".")

    style = arch.get("styleProfile") or {}
    corridor_char = (style.get("corridorCharacter") or "").strip()
    if corridor_char:
        parts.append(
            corridor_char if corridor_char.endswith((".", "!", "?")) else corridor_char + "."
        )
    else:
        arch_desc = (arch.get("description") or "").strip()
        if arch_desc and arch_desc != var_desc:
            parts.append(arch_desc if arch_desc.endswith((".", "!", "?")) else arch_desc + ".")

    # E3: Feature details from prompt.details
    prompt_obj = arch.get("prompt") or {}
    details = prompt_obj.get("details") or []
    if isinstance(details, list) and details:
        cleaned = [str(d).strip().rstrip(".") for d in details if str(d).strip()]
        if cleaned:
            parts.append("Key features: " + "; ".join(cleaned[:6]) + ".")

    # E4: Family context
    ctx = _STREET_FAMILY_CONTEXT.get(family)
    if ctx:
        parts.append(ctx)

    # E5: Dimensions (use typicalWidth_m + laneCount + sidewalk flag)
    width = arch.get("typicalWidth_m") or arch.get("suggestedWidth_m")
    lanes = arch.get("laneCount")
    has_side = arch.get("hasSidewalk")
    has_median = arch.get("hasMedian")
    has_bike = arch.get("hasBikeLane")
    dim_bits: list[str] = []
    if width:
        dim_bits.append(f"approximately {width}m wide curb-to-curb")
    if lanes:
        dim_bits.append(f"{lanes} lane(s)")
    if has_median:
        dim_bits.append("with a center median")
    if has_bike:
        dim_bits.append("with a dedicated bike lane")
    if has_side:
        dim_bits.append("sidewalks on both sides")
    if dim_bits:
        parts.append("Corridor dimensions: " + ", ".join(dim_bits) + ".")

    # E6: Linear-corridor clarifier + family-specific negative
    parts.append(
        "This is a LINEAR STREET/PATHWAY CORRIDOR — a ribbon of public "
        "right-of-way with edge conditions on both sides; the output must "
        "show the full corridor running through the frame as the "
        "unmistakable dominant subject."
    )
    neg = _STREET_FAMILY_NEGATIVE.get(family)
    if neg:
        parts.append(neg)

    return " ".join(p for p in parts if p).strip()


def load_catalog_jobs(catalog: str, angle: int) -> list[dict[str, Any]]:
    """Walk a JSON catalog and emit one job per (archetype, variant) pair.

    Each job dict: {name, zone_type, subject, ref_path, out_path}.

    Variants without a `thumbnailUrl`, or whose underlying PNG file doesn't
    exist on disk, are skipped (with a log note — helpful for spotting
    incomplete catalog data).
    """
    catalog_path = _CATALOG_PATHS.get(catalog)
    if not catalog_path or not catalog_path.exists():
        print(f"ERROR: catalog '{catalog}' not found at {catalog_path}")
        return []

    zone_type = _CATALOG_ZONE_TYPE[catalog]
    if zone_type == "street":
        composer = compose_street_subject
    elif zone_type == "building":
        composer = compose_building_subject
    else:
        composer = compose_open_space_subject

    with catalog_path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    archetypes = data.get("archetypes", data if isinstance(data, list) else [])
    if not isinstance(archetypes, list):
        archetypes = []

    jobs: list[dict[str, Any]] = []
    missing = 0
    for arch in archetypes:
        variants = arch.get("variants") or []
        for v in variants:
            thumbnail = v.get("thumbnailUrl")
            if not thumbnail:
                continue
            rel = thumbnail.lstrip("/")
            if not rel.startswith("archetypes/"):
                continue
            ref_path = _PROJECT_ROOT / "frontend" / "public" / rel
            if not ref_path.exists():
                missing += 1
                continue

            stem = ref_path.stem  # e.g. "variant_0", "variant_3"
            out_path = ref_path.parent / f"{stem}_angle_{angle}.jpg"

            subject = composer(arch, v)
            arch_title = arch.get("title") or arch.get("id") or "?"
            variant_label = v.get("label") or v.get("id") or "?"

            jobs.append({
                "name": f"{arch_title} — {variant_label}",
                "arch_id": arch.get("id") or "",
                "zone_type": zone_type,
                "subject": subject,
                "ref_path": ref_path,
                "out_path": out_path,
            })

    if missing:
        print(f"NOTE: {missing} variants skipped — thumbnail PNG not found on disk")
    return jobs


def build_pilot_jobs(angle: int) -> list[dict[str, Any]]:
    """Flatten the hand-curated ARCHETYPES list to the same job shape as
    load_catalog_jobs. This is what runs when --catalog is not specified."""
    jobs: list[dict[str, Any]] = []
    for arch in ARCHETYPES:
        arch_dir: Path = arch["dir"]
        subject: str = arch["subject"]
        zone_type: str = arch.get("type", "building")
        for v in arch["variants"]:
            ref_path = arch_dir / f"variant_{v}.png"
            out_path = arch_dir / f"variant_{v}_angle_{angle}.jpg"
            jobs.append({
                "name": arch["name"],
                "zone_type": zone_type,
                "subject": subject,
                "ref_path": ref_path,
                "out_path": out_path,
            })
    return jobs


# ---------------------------------------------------------------------------
# Hand-curated pilot archetypes (the 3 Calgary-site zones — used when
# --catalog is not specified). Kept as-is for targeted regeneration.
# ---------------------------------------------------------------------------

ARCHETYPES = [
    {
        "name": "Vertical Farm / Indoor Agriculture",
        "type": "building",
        "dir": _PUBLIC_DIR / "buildings" / "vertical_farm",
        "variants": [3],
        "subject": (
            "A compact vertical farm / indoor agriculture building. "
            "Glass-and-steel exoskeleton frame exposing stacked horticultural "
            "levels visible through the transparent walls. Hydroponic growing "
            "racks with rows of lettuce, herbs, and leafy greens on each level, "
            "glowing warm-green and violet from LED grow lights. White powder-"
            "coated steel structural columns and diagonal bracing. Flat or "
            "slightly pitched roof with mechanical equipment (HVAC, rainwater "
            "collection). Approximately 25m wide x 25m deep, 4-6 storeys tall. "
            "Working agricultural-industrial building, not a generic office tower."
        ),
    },
    {
        "name": "Grand Magasin — Belle Epoque Parisian Department Store",
        "type": "building",
        "dir": _PUBLIC_DIR / "buildings" / "grand-magasin",
        "variants": [3],
        "subject": (
            "A Parisian Belle Epoque grand magasin (grand department store) in "
            "the Beaux-Arts tradition. Monumental 5-8 storey retail palace. "
            "Ashlar CREAM LIMESTONE facade with rusticated ground floor and "
            "smooth-cut upper stories. Grand-order Corinthian pilasters spanning "
            "floors 2-4. Tall arched windows with carved stone surrounds. "
            "Gilded bronze balconies on principal floor. Massive projecting "
            "stone cornice with modillions and balustrade parapet with "
            "statuary. Central GREEN-PATINA COPPER GLASS DOME (Neo-Byzantine "
            "or Art Nouveau) rising above zinc mansard roofing with ornamental "
            "iron cresting. Continuous plate-glass display windows at street "
            "level with multiple grand arched entrances and bronze revolving "
            "doors under iron-and-glass entrance canopies. Approximately 50m "
            "wide x 35m deep. Like Galeries Lafayette or Le Bon Marche."
        ),
    },
    {
        "name": "Disc Golf Course",
        "type": "open_space",
        "dir": _PUBLIC_DIR / "openspaces" / "disc-golf-course",
        "variants": [3],
        "subject": (
            "A compact urban disc golf course open space. Manicured grass "
            "fairways with mowed path patterns between tee pads and baskets. "
            "Yellow powder-coated steel chain baskets (Mach X / DISCatcher "
            "style) with visible chain assemblies and target flags. Small "
            "concrete or rubber tee pads at each hole start. Landscape-timber "
            "framing at tee boxes. Mature scattered deciduous trees forming "
            "natural obstacles and shade canopy. Wood-chip or gravel paths "
            "connecting holes. Wayfinding signs at each tee. Park benches at "
            "a few tee pads. Approximately 60m wide x 40m deep showing "
            "roughly a 3-hole cluster. Working sport facility, not a generic "
            "park."
        ),
    },
]

# ---------------------------------------------------------------------------
# Generation
# ---------------------------------------------------------------------------


def generate_image(
    prompt: str,
    reference_paths: list[Path],
    zone_type: str,
    angle: int,
    retries: int = 2,
) -> bytes | None:
    """Generate an aerial reference image.

    reference_paths: one or more images to feed Gemini. Typically:
      - angle 60 : [street_level_variant.png]
      - angle 90 : [street_level_variant.png, variant_N_angle_60.jpg]
        (the 60° oblique tells the model what the roof looks like, which
        the street-level image can't show — critical for accurate nadir.)
    """
    for p in reference_paths:
        if not p.exists():
            print(f"  ERROR: reference image not found at {p}")
            return None

    # Intro differs by (angle, zone_type) and by number of references.
    subject_kind = "open space" if zone_type == "open_space" else "building/subject"
    if angle == 90:
        camera_summary = (
            "the camera is now 150 meters in the air pointing STRAIGHT DOWN "
            "(true nadir) showing only the rooftop / ground-plane layout"
        )
    else:
        if zone_type == "open_space":
            camera_summary = (
                "the camera is now 80 meters in the air, tilted 60 degrees "
                "down from horizontal"
            )
        else:
            camera_summary = (
                "the camera is now 80 meters in the air, tilted 60 degrees "
                "down from horizontal, viewing the subject from a corner so "
                "both rooftop and upper facades are visible"
            )

    if len(reference_paths) == 1:
        intro_text = (
            f"The following reference image is the canonical view of the "
            f"{subject_kind}. Use it to understand the EXACT materials, "
            f"colors, proportions, and character of this archetype. You are "
            f"about to generate a NEW drone view of the SAME EXACT subject — "
            f"same materials, same character — but {camera_summary}. Do not "
            f"invent new elements. Do not change the palette."
        )
    else:
        intro_text = (
            f"The following {len(reference_paths)} reference images together "
            f"show the canonical appearance of this {subject_kind}. The first "
            f"is the street-level / ground-level view (materials and "
            f"character). The second is an oblique aerial view (rooftop and "
            f"massing from above). Use BOTH to triangulate the exact "
            f"appearance of the subject. You are about to generate a NEW "
            f"drone view of the SAME EXACT subject — same materials, same "
            f"character — but {camera_summary}. The rooftop you render at "
            f"nadir must match the rooftop visible in the second reference "
            f"image (oblique aerial). Do not invent new elements. Do not "
            f"change the palette."
        )

    parts: list[dict] = [{"text": intro_text}]
    for p in reference_paths:
        mime = "image/jpeg" if p.suffix.lower() in {".jpg", ".jpeg"} else "image/png"
        parts.append({
            "inlineData": {
                "mimeType": mime,
                "data": base64.b64encode(p.read_bytes()).decode("ascii"),
            }
        })
    parts.append({"text": prompt})

    payload = {
        "contents": [{"role": "user", "parts": parts}],
        "generationConfig": {
            "responseModalities": ["TEXT", "IMAGE"],
            # Lower temperature = tighter adherence to the reference + metadata.
            # Past drift issues came from temperature too high.
            "temperature": 0.35,
        },
    }

    for attempt in range(retries + 1):
        try:
            resp = httpx.post(
                API_URL,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=180.0,
            )
        except httpx.TimeoutException:
            print(f"  TIMEOUT (attempt {attempt + 1})")
            if attempt < retries:
                time.sleep(5)
                continue
            return None
        except httpx.RequestError as exc:
            print(f"  NETWORK ERROR: {exc}")
            if attempt < retries:
                time.sleep(5)
                continue
            return None

        if resp.status_code == 429:
            print(f"  RATE LIMITED — waiting 30s (attempt {attempt + 1})")
            time.sleep(30)
            continue

        if resp.status_code != 200:
            print(f"  HTTP {resp.status_code}: {resp.text[:300]}")
            if attempt < retries:
                time.sleep(5)
                continue
            return None

        try:
            data = resp.json()
        except Exception:
            print(f"  invalid JSON: {resp.text[:300]}")
            return None

        for candidate in data.get("candidates", []):
            for part in candidate.get("content", {}).get("parts", []):
                inline = part.get("inlineData") or part.get("inline_data")
                if inline and inline.get("data"):
                    return base64.b64decode(inline["data"])

        print(f"  no image in response (attempt {attempt + 1})")
        if attempt < retries:
            time.sleep(5)
            continue

    return None


def build_prompt(subject: str, zone_type: str, angle: int) -> str:
    camera = CAMERA_BLOCKS.get((angle, zone_type))
    if camera is None:
        raise ValueError(f"No camera block defined for angle={angle} zone_type={zone_type}")
    if zone_type == "street":
        framing = FRAMING_BLOCK_STREET
        fidelity = FIDELITY_BLOCK_STREET
    elif zone_type == "open_space":
        framing = FRAMING_BLOCK_OPEN_SPACE
        fidelity = FIDELITY_BLOCK_OPEN_SPACE
    else:
        framing = FRAMING_BLOCK_BUILDING
        fidelity = FIDELITY_BLOCK_BUILDING
    return "\n\n".join([
        f"SUBJECT: {subject}",
        camera,
        framing,
        STYLE_BLOCK,
        fidelity,
        NO_PEOPLE_BLOCK,
    ])


def main() -> int:
    # CLI args
    only_filter: str | None = None
    ids_file: Path | None = None
    catalog: str | None = None
    angle = 60
    limit: int | None = None
    skip_existing = True
    dry_run = False

    for arg in sys.argv[1:]:
        if arg.startswith("--only="):
            only_filter = arg.split("=", 1)[1].lower()
        elif arg.startswith("--ids-file="):
            ids_file = Path(arg.split("=", 1)[1])
        elif arg.startswith("--angle="):
            angle = int(arg.split("=", 1)[1])
        elif arg.startswith("--catalog="):
            catalog = arg.split("=", 1)[1]
        elif arg.startswith("--limit="):
            limit = int(arg.split("=", 1)[1])
        elif arg == "--skip-existing":
            skip_existing = True
        elif arg == "--no-skip-existing":
            skip_existing = False
        elif arg == "--dry-run":
            dry_run = True
        elif arg in ("--help", "-h"):
            print(__doc__)
            return 0
        else:
            print(f"ERROR: unknown flag {arg!r}")
            return 1

    if angle not in {60, 90}:
        print(f"ERROR: --angle must be 60 or 90 (got {angle})")
        return 1
    if catalog and catalog not in _CATALOG_PATHS:
        print(f"ERROR: --catalog must be one of {list(_CATALOG_PATHS.keys())} (got {catalog!r})")
        return 1

    # Load jobs from JSON catalog OR from hand-curated pilot list
    if catalog:
        print(f"Loading jobs from catalog: {catalog}")
        jobs = load_catalog_jobs(catalog, angle)
    else:
        jobs = build_pilot_jobs(angle)

    # Apply filters
    if only_filter:
        jobs = [j for j in jobs if only_filter in j["name"].lower()]
    if ids_file:
        if not ids_file.exists():
            print(f"ERROR: --ids-file not found: {ids_file}")
            return 1
        allowed_ids = {line.strip() for line in ids_file.read_text(encoding="utf-8").splitlines() if line.strip()}
        before = len(jobs)
        jobs = [j for j in jobs if j.get("arch_id") in allowed_ids]
        print(f"Filter --ids-file: kept {len(jobs)}/{before} jobs matching {len(allowed_ids)} archetype IDs")
    before_preserve = len(jobs)
    jobs = [j for j in jobs if j["out_path"].resolve() not in {p.resolve() for p in PRESERVE_PATHS}]
    preserved = before_preserve - len(jobs)
    if preserved:
        print(f"Preserving {preserved} pilot output(s) — will not regenerate "
              f"(see PRESERVE_PATHS in script)")
    if skip_existing:
        before = len(jobs)
        jobs = [j for j in jobs if not j["out_path"].exists()]
        skipped = before - len(jobs)
        if skipped:
            print(f"Skipping {skipped} job(s) whose output already exists "
                  f"(pass --no-skip-existing to overwrite)")
    if limit is not None:
        jobs = jobs[:limit]

    if not jobs:
        print("No jobs to run.")
        return 0

    # Header
    print(f"Ready: {len(jobs)} job(s) at ANGLE={angle}°")
    if only_filter:
        print(f"  Filter: --only={only_filter!r}")
    if limit is not None:
        print(f"  Limit: {limit}")
    print(f"  Model: {MODEL}  Temperature: 0.35")
    print(f"  Skip-existing: {skip_existing}")
    print()

    # Dry run — just print each job's composed subject + paths, no API calls
    if dry_run:
        print("DRY RUN — no API calls will be made.\n")
        for i, job in enumerate(jobs, 1):
            print(f"--- [{i}/{len(jobs)}] {job['name']}  [{job['zone_type']}]")
            print(f"    ref: {job['ref_path'].relative_to(_PROJECT_ROOT)}")
            print(f"    out: {job['out_path'].relative_to(_PROJECT_ROOT)}")
            subj = job["subject"]
            snippet = subj[:260] + ("…" if len(subj) > 260 else "")
            print(f"    subject ({len(subj)} chars): {snippet}")
            print()
        return 0

    # Run
    successes = 0
    failures: list[str] = []
    start = time.time()

    for i, job in enumerate(jobs, 1):
        name = job["name"]
        zone_type = job["zone_type"]
        ref_path: Path = job["ref_path"]
        out_path: Path = job["out_path"]

        # Build reference list: street-level PNG always first. For 90°,
        # also attach the existing 60° JPG if it exists (dual-ref).
        refs: list[Path] = [ref_path]
        if angle == 90:
            sibling_60 = out_path.parent / f"{ref_path.stem}_angle_60.jpg"
            if sibling_60.exists():
                refs.append(sibling_60)

        refs_str = " + ".join(r.name for r in refs)
        elapsed = time.time() - start
        rate = i / elapsed if elapsed > 0 else 0
        eta_min = (len(jobs) - i) / rate / 60 if rate > 0 else 0
        print(f"[{i}/{len(jobs)}] {name}  [{zone_type}]  refs=[{refs_str}] "
              f"-> {out_path.name}  (ETA {eta_min:.0f}m)")

        prompt = build_prompt(job["subject"], zone_type, angle)
        img_bytes = generate_image(prompt, refs, zone_type, angle)

        if img_bytes is None:
            print(f"    FAILED")
            failures.append(name)
            continue

        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_bytes(img_bytes)
        size_kb = len(img_bytes) / 1024
        print(f"    OK ({size_kb:.0f} KB)")
        successes += 1
        # Pace to avoid tripping rate limits
        time.sleep(2)

    total_elapsed = (time.time() - start) / 60
    print(f"\n=== Done: {successes}/{len(jobs)} succeeded  (took {total_elapsed:.1f} min)")
    if failures:
        print(f"    Failed ({len(failures)}): {', '.join(failures[:10])}"
              f"{'…' if len(failures) > 10 else ''}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
