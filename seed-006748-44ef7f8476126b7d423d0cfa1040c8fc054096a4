"""
Generate 4 design variants for every building archetype and their card images.

For each archetype, creates 4 material/design variants with:
  - Unique label, description, color palette
  - facadeDetail and roofDetail metadata
  - renderPrompt for aerial/polygon rendering
  - Card image generated via Gemini API

Usage:
    python scripts/generate_variants.py [--skip-existing] [--json-only]
"""

from __future__ import annotations

import base64
import io
import json
import os
import re
import sys
import time
from pathlib import Path

import httpx
from PIL import Image

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SCRIPT_DIR.parent
_ENV_FILE = _PROJECT_ROOT / "backend" / ".env"
_DATA_DIR = _PROJECT_ROOT / "frontend" / "src" / "data"
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
MODEL = "gemini-2.5-flash-image"
API_URL = (
    f"https://generativelanguage.googleapis.com/v1beta/"
    f"models/{MODEL}:generateContent?key={API_KEY}"
)

CARD_WIDTH = 1024
CARD_HEIGHT = 768

# ---------------------------------------------------------------------------
# Variant definitions per archetype
# Each entry: archetype_id -> list of 4 variant dicts
# ---------------------------------------------------------------------------

VARIANT_DEFINITIONS: dict[str, list[dict]] = {
    "brownstone_rowhouse_frontage": [
        {
            "id": "brownstone_rowhouse_red_sandstone",
            "label": "Red Brick & Sandstone",
            "color": "#8B4513",
            "description": "Classic red-brown brick facade with carved sandstone lintels, brownstone stoop with iron railings, and decorative cornice.",
            "facadeDetail": {"primaryMaterial": "red-brown brick", "secondaryMaterial": "carved sandstone lintels and sills", "groundFloor": "brownstone stoop with ornate iron railings", "colorScheme": "warm red-brown and tan"},
            "roofDetail": {"form": "flat with decorative pressed-metal cornice", "material": "membrane with stone parapet"},
        },
        {
            "id": "brownstone_rowhouse_limestone",
            "label": "Limestone & Wrought Iron",
            "color": "#C4B896",
            "description": "Pale limestone facade with ornamental wrought-iron balconettes, arched windows with keystones, and rusticated ground floor.",
            "facadeDetail": {"primaryMaterial": "cut limestone blocks", "secondaryMaterial": "wrought-iron balconettes and window guards", "groundFloor": "rusticated stone with arched entry", "colorScheme": "pale cream and charcoal iron"},
            "roofDetail": {"form": "mansard with dormer windows", "material": "slate tiles with copper flashing"},
        },
        {
            "id": "brownstone_rowhouse_painted_brick",
            "label": "Painted Brick & Timber",
            "color": "#6B8E6B",
            "description": "Painted brick in sage green with exposed timber window frames, planters on sills, and a painted wood entry door.",
            "facadeDetail": {"primaryMaterial": "painted brick in sage green", "secondaryMaterial": "exposed timber window frames and sills", "groundFloor": "painted wood paneled entry with brass hardware", "colorScheme": "sage green, cream trim, warm timber"},
            "roofDetail": {"form": "pitched with painted timber fascia", "material": "clay tiles in terracotta"},
        },
        {
            "id": "brownstone_rowhouse_dark_copper",
            "label": "Dark Brick & Copper",
            "color": "#2F4F4F",
            "description": "Dark charcoal brick with copper bay windows that have developed a green patina, copper downspouts, and a slate-trimmed entry.",
            "facadeDetail": {"primaryMaterial": "dark charcoal engineering brick", "secondaryMaterial": "patinated copper bay windows and trim", "groundFloor": "slate-framed entry with copper canopy", "colorScheme": "charcoal, verdigris copper, slate grey"},
            "roofDetail": {"form": "flat with copper-capped parapet", "material": "standing seam copper"},
        },
    ],
    "classic_brownstone_streetwall": [
        {
            "id": "classic_brownstone_traditional",
            "label": "Traditional Brownstone",
            "color": "#8B6F47",
            "description": "Traditional brownstone streetwall with continuous stoops, ornate cornices, and uniform window rhythm in warm brown tones.",
            "facadeDetail": {"primaryMaterial": "brownstone cladding", "secondaryMaterial": "cast iron window heads and cornices", "groundFloor": "high stoop entry with carved newel posts", "colorScheme": "warm brown and cream"},
            "roofDetail": {"form": "flat with elaborate pressed-tin cornice", "material": "membrane with stone coping"},
        },
        {
            "id": "classic_brownstone_federal",
            "label": "Federal Red Brick",
            "color": "#A0522D",
            "description": "Federal-style red brick streetwall with white marble trim, fan-light transoms over entries, and symmetrical sash windows.",
            "facadeDetail": {"primaryMaterial": "Flemish bond red brick", "secondaryMaterial": "white marble lintels and sills", "groundFloor": "recessed entry with fan-light transom", "colorScheme": "red brick, white marble, black shutters"},
            "roofDetail": {"form": "low-slope gable behind parapet", "material": "standing seam metal"},
        },
        {
            "id": "classic_brownstone_grey_stone",
            "label": "Greystone & Iron",
            "color": "#808080",
            "description": "Grey limestone streetwall with geometric art deco iron grilles, faceted bay windows, and a continuous cantilevered stone balcony.",
            "facadeDetail": {"primaryMaterial": "grey limestone ashlar", "secondaryMaterial": "art deco iron grilles and panels", "groundFloor": "recessed entry with geometric transom", "colorScheme": "cool grey, black iron, gold accents"},
            "roofDetail": {"form": "flat with stepped stone parapet", "material": "membrane with stone coping"},
        },
        {
            "id": "classic_brownstone_modern_infill",
            "label": "Contemporary Infill",
            "color": "#4682B4",
            "description": "Modern infill within a traditional streetwall — glass and steel facade with bronze-anodized frames respecting the cornice line and setback.",
            "facadeDetail": {"primaryMaterial": "floor-to-ceiling glass panels", "secondaryMaterial": "bronze-anodized aluminum mullions", "groundFloor": "transparent glass storefront with slim steel columns", "colorScheme": "glass, bronze, warm grey"},
            "roofDetail": {"form": "flat green roof with glass penthouse setback", "material": "vegetated extensive green roof"},
        },
    ],
    "historical_brick_main_street": [
        {
            "id": "historical_brick_victorian",
            "label": "Victorian Polychrome",
            "color": "#8B0000",
            "description": "Polychrome Victorian brick with decorative banding in cream and red, arched windows with keystones, and ornate pressed-metal shopfronts.",
            "facadeDetail": {"primaryMaterial": "polychrome red and cream brick", "secondaryMaterial": "carved stone window surrounds and keystones", "groundFloor": "pressed-metal shopfront with recessed entry", "colorScheme": "red brick, cream bands, forest green shopfront"},
            "roofDetail": {"form": "parapet with decorative brick corbelling", "material": "concealed flat roof behind parapet"},
        },
        {
            "id": "historical_brick_industrial",
            "label": "Industrial Loft Style",
            "color": "#696969",
            "description": "Raw industrial brick with large multi-pane factory windows, exposed steel lintels, and cast-iron pilasters at ground level.",
            "facadeDetail": {"primaryMaterial": "raw industrial red brick", "secondaryMaterial": "exposed steel lintels and tie plates", "groundFloor": "cast-iron pilasters with large display windows", "colorScheme": "raw brick, aged steel, black iron"},
            "roofDetail": {"form": "saw-tooth industrial roof profile", "material": "corrugated metal with clerestory glazing"},
        },
        {
            "id": "historical_brick_arts_crafts",
            "label": "Arts & Crafts Heritage",
            "color": "#DAA520",
            "description": "Arts and Crafts brick with half-timbered gable accents, leaded glass windows, and hand-crafted tile insets above the entry.",
            "facadeDetail": {"primaryMaterial": "textured clinker brick", "secondaryMaterial": "half-timber and stucco gable panels", "groundFloor": "arched brick entry with handmade tile surround", "colorScheme": "golden brick, dark timber, forest green"},
            "roofDetail": {"form": "steep gable with decorative bargeboards", "material": "hand-cut clay tiles"},
        },
        {
            "id": "historical_brick_colonial_revival",
            "label": "Colonial Revival",
            "color": "#B22222",
            "description": "Colonial Revival brick with white pilasters, a pedimented entry, symmetrical sash windows with shutters, and a dentil cornice.",
            "facadeDetail": {"primaryMaterial": "running bond red brick", "secondaryMaterial": "white-painted wood pilasters and cornices", "groundFloor": "pedimented entry with side lights", "colorScheme": "red brick, white trim, hunter green shutters"},
            "roofDetail": {"form": "hip roof with cupola", "material": "wood shingles"},
        },
    ],
    "victorian_heritage_avenue": [
        {
            "id": "victorian_heritage_queen_anne",
            "label": "Queen Anne Painted Lady",
            "color": "#9B59B6",
            "description": "Exuberant Queen Anne Victorian with a corner turret, multi-colored painted wood siding, decorative shingle patterns, and a wraparound porch.",
            "facadeDetail": {"primaryMaterial": "painted wood clapboard and fish-scale shingles", "secondaryMaterial": "turned wood spindles and gingerbread trim", "groundFloor": "wraparound porch with turned columns", "colorScheme": "three-tone: plum body, cream trim, teal accents"},
            "roofDetail": {"form": "complex hip-and-gable with corner turret", "material": "slate tiles in mixed colors"},
        },
        {
            "id": "victorian_heritage_italianate",
            "label": "Italianate Townhouse",
            "color": "#D4A574",
            "description": "Italianate Victorian with tall arched windows, heavy bracketed cornice, rusticated stone base, and a belvedere tower.",
            "facadeDetail": {"primaryMaterial": "smooth stucco over brick", "secondaryMaterial": "heavy paired wooden brackets under cornice", "groundFloor": "rusticated stone base with tall entry doors", "colorScheme": "warm ochre, cream trim, dark green shutters"},
            "roofDetail": {"form": "low hip with deep bracketed eaves and belvedere", "material": "standing seam metal"},
        },
        {
            "id": "victorian_heritage_gothic_revival",
            "label": "Gothic Revival",
            "color": "#4A4A4A",
            "description": "Gothic Revival with pointed arch windows, steep gables with decorative bargeboards, buttressed walls, and a rose window accent.",
            "facadeDetail": {"primaryMaterial": "dark stone and brick in pointed arch motifs", "secondaryMaterial": "carved stone tracery and finials", "groundFloor": "pointed arch entry with carved tympanum", "colorScheme": "dark grey stone, cream tracery, deep red doors"},
            "roofDetail": {"form": "steep cross gable with decorated ridge tiles", "material": "dark slate with terracotta ridge tiles"},
        },
        {
            "id": "victorian_heritage_second_empire",
            "label": "Second Empire Mansard",
            "color": "#5D478B",
            "description": "Second Empire Victorian with a prominent mansard roof featuring dormer windows, iron cresting, paired columns at the entry, and quoined corners.",
            "facadeDetail": {"primaryMaterial": "dressed stone with quoined corners", "secondaryMaterial": "paired Corinthian columns at entry portico", "groundFloor": "stone portico with double entry doors", "colorScheme": "warm grey stone, slate blue mansard, gold accents"},
            "roofDetail": {"form": "mansard with round-headed dormers and iron cresting", "material": "patterned slate in two tones"},
        },
    ],
    "contemporary_townhouse_courtyard": [
        {
            "id": "contemporary_townhouse_timber_screen",
            "label": "Timber Screen & Garden",
            "color": "#8B7355",
            "description": "Contemporary townhouse with vertical timber screen facade filtering light into courtyard gardens, green roof terraces, and natural stone base.",
            "facadeDetail": {"primaryMaterial": "vertical hardwood timber screens", "secondaryMaterial": "brushed concrete walls behind screens", "groundFloor": "natural stone base with recessed glazed entry", "colorScheme": "warm timber, concrete grey, garden green"},
            "roofDetail": {"form": "flat with accessible green roof terrace", "material": "intensive green roof with timber deck"},
        },
        {
            "id": "contemporary_townhouse_white_minimal",
            "label": "White Minimal & Glass",
            "color": "#E8E8E8",
            "description": "Crisp white-rendered townhouse with frameless corner glazing, cantilevered upper floors, and minimal black-framed windows.",
            "facadeDetail": {"primaryMaterial": "smooth white render", "secondaryMaterial": "frameless structural glass corners", "groundFloor": "flush glass entry with hidden frame", "colorScheme": "pure white, clear glass, matte black frames"},
            "roofDetail": {"form": "flat with hidden parapet and recessed skylights", "material": "white membrane with integrated PV panels"},
        },
        {
            "id": "contemporary_townhouse_brick_courtyard",
            "label": "Brick & Courtyard Walls",
            "color": "#CD853F",
            "description": "Warm brick courtyard townhouse with perforated brick screen walls, internal courtyard gardens visible through openings, and copper rainwater goods.",
            "facadeDetail": {"primaryMaterial": "handmade buff brick", "secondaryMaterial": "perforated brick screen walls creating dappled light", "groundFloor": "brick archway revealing courtyard garden", "colorScheme": "warm buff brick, copper, courtyard greenery"},
            "roofDetail": {"form": "asymmetric pitched roof with clerestory", "material": "zinc standing seam"},
        },
        {
            "id": "contemporary_townhouse_corten_garden",
            "label": "Cor-Ten & Living Wall",
            "color": "#8B4726",
            "description": "Weathering steel (Cor-Ten) clad townhouse with integrated living green wall panels, steel mesh balustrades, and polished concrete base.",
            "facadeDetail": {"primaryMaterial": "weathering Cor-Ten steel panels", "secondaryMaterial": "living green wall panels between windows", "groundFloor": "polished concrete with wide steel-framed entry", "colorScheme": "rust orange, living green, concrete grey"},
            "roofDetail": {"form": "butterfly roof directing rainwater to garden", "material": "Cor-Ten steel panels"},
        },
    ],
    "detached_contemporary_infill": [
        {
            "id": "detached_infill_glass_box",
            "label": "Glass Pavilion",
            "color": "#87CEEB",
            "description": "Transparent glass pavilion house with exposed steel structure, minimal solid walls, and landscape flowing through the interior.",
            "facadeDetail": {"primaryMaterial": "floor-to-ceiling structural glass", "secondaryMaterial": "exposed painted steel I-beam frame", "groundFloor": "glass walls with steel frame at grade", "colorScheme": "transparent glass, white steel, landscape green"},
            "roofDetail": {"form": "flat floating plane with deep overhang", "material": "white-painted steel deck with hidden membrane"},
        },
        {
            "id": "detached_infill_dark_zinc",
            "label": "Dark Zinc & Cedar",
            "color": "#36454F",
            "description": "Dark zinc-clad contemporary box with warm cedar soffits and reveals, punctuated by precisely placed windows of varying sizes.",
            "facadeDetail": {"primaryMaterial": "pre-patinated dark zinc panels", "secondaryMaterial": "western red cedar soffits and window reveals", "groundFloor": "cedar-clad ground floor with concealed garage", "colorScheme": "charcoal zinc, warm cedar, anthracite frames"},
            "roofDetail": {"form": "flat with concealed drainage", "material": "zinc standing seam continuing from walls"},
        },
        {
            "id": "detached_infill_white_render",
            "label": "White Render & Cantilever",
            "color": "#F5F5DC",
            "description": "Bold white-rendered volume with dramatic cantilever over glass ground floor, ribbon windows, and a sculptural folded roof.",
            "facadeDetail": {"primaryMaterial": "smooth white cement render", "secondaryMaterial": "continuous ribbon windows with slim aluminum frames", "groundFloor": "fully glazed recessed ground floor", "colorScheme": "brilliant white, clear glass, brushed aluminum"},
            "roofDetail": {"form": "folded plane with dramatic overhang", "material": "white-rendered concrete with hidden gutters"},
        },
        {
            "id": "detached_infill_rammed_earth",
            "label": "Rammed Earth & Timber",
            "color": "#A0522D",
            "description": "Rammed earth walls with visible stratification, heavy timber post-and-beam structure, and deep shaded verandahs.",
            "facadeDetail": {"primaryMaterial": "rammed earth with visible color layers", "secondaryMaterial": "heavy glulam timber beams and posts", "groundFloor": "rammed earth base with timber-framed openings", "colorScheme": "earth tones - ochre, sienna, raw timber"},
            "roofDetail": {"form": "mono-pitch with deep eaves for solar shading", "material": "exposed timber rafters with metal deck"},
        },
    ],
    "courtyard_family_housing": [
        {
            "id": "courtyard_family_mediterranean",
            "label": "Mediterranean Courtyard",
            "color": "#DEB887",
            "description": "Mediterranean-style family courtyard housing with terracotta walls, arched colonnades, a central fountain courtyard, and clay tile roofs.",
            "facadeDetail": {"primaryMaterial": "warm-toned stucco in terracotta", "secondaryMaterial": "stone arched colonnade around courtyard", "groundFloor": "arched entry portal to central fountain courtyard", "colorScheme": "terracotta, cream stone arches, dark green shutters"},
            "roofDetail": {"form": "low-pitched hip with wide eaves", "material": "barrel clay tiles in mixed terracotta tones"},
        },
        {
            "id": "courtyard_family_scandinavian",
            "label": "Nordic Timber Courtyard",
            "color": "#2E8B57",
            "description": "Scandinavian family housing around a shared timber-decked courtyard, with dark-stained timber cladding, large windows, and integrated planters.",
            "facadeDetail": {"primaryMaterial": "dark-stained vertical timber boarding", "secondaryMaterial": "light birch plywood window surrounds", "groundFloor": "timber deck extending into shared courtyard", "colorScheme": "charcoal timber, birch ply, courtyard greenery"},
            "roofDetail": {"form": "mono-pitch with sedum green roof", "material": "extensive green roof with timber fascia"},
        },
        {
            "id": "courtyard_family_brick_modern",
            "label": "Modern Brick Mews",
            "color": "#B8860B",
            "description": "Contemporary brick mews housing around a paved courtyard, with soldier-course brick detailing, Juliet balconies, and integrated bike storage.",
            "facadeDetail": {"primaryMaterial": "buff brick with soldier-course bands", "secondaryMaterial": "powder-coated steel Juliet balconies", "groundFloor": "brick-arched carriage entry to courtyard", "colorScheme": "golden buff brick, black steel, grey paving"},
            "roofDetail": {"form": "pitched with hidden valley gutter", "material": "dark grey concrete tiles"},
        },
        {
            "id": "courtyard_family_tropical",
            "label": "Tropical Breezeway",
            "color": "#228B22",
            "description": "Tropical family courtyard with open breezeways, louvered timber screens, lush interior garden courtyard, and deep shaded balconies.",
            "facadeDetail": {"primaryMaterial": "white render with horizontal louvered timber screens", "secondaryMaterial": "hardwood breezeway screens and balustrades", "groundFloor": "open breezeway passage to tropical garden courtyard", "colorScheme": "white walls, warm timber louvers, tropical green"},
            "roofDetail": {"form": "steep pitch for tropical rainfall", "material": "corrugated metal with wide overhangs"},
        },
    ],
    "modern_glass_office_institutional": [
        {
            "id": "glass_office_blue_curtainwall",
            "label": "Blue Glass Curtain Wall",
            "color": "#4169E1",
            "description": "Sleek blue-tinted glass curtain wall office with mullionless corners, stainless steel spandrel panels, and a double-height glass lobby.",
            "facadeDetail": {"primaryMaterial": "blue-tinted low-E glass curtain wall", "secondaryMaterial": "brushed stainless steel spandrel panels", "groundFloor": "double-height glass lobby with revolving doors", "colorScheme": "blue glass, silver steel, white marble lobby"},
            "roofDetail": {"form": "flat with rooftop mechanical penthouse", "material": "membrane with aluminum coping"},
        },
        {
            "id": "glass_office_terracotta_fins",
            "label": "Glass & Terracotta Fins",
            "color": "#CC7722",
            "description": "Glass office with vertical terracotta brise-soleil fins creating rhythm and solar shading, planted balcony terraces at setbacks.",
            "facadeDetail": {"primaryMaterial": "clear glass with terracotta ceramic fins", "secondaryMaterial": "planted balcony terraces at setback floors", "groundFloor": "open colonnade with retail at grade", "colorScheme": "clear glass, warm terracotta fins, green terraces"},
            "roofDetail": {"form": "stepped terraces with green roof", "material": "intensive green roof with terracotta planters"},
        },
        {
            "id": "glass_office_dark_frame",
            "label": "Dark Frame & Clear Glass",
            "color": "#1C1C1C",
            "description": "Minimalist glass office with bold dark structural frame expressed on exterior, clear glass revealing floor plates, and integrated LED edge lighting.",
            "facadeDetail": {"primaryMaterial": "ultra-clear low-iron glass", "secondaryMaterial": "exposed dark steel structural frame", "groundFloor": "transparent glass base with expressed steel columns", "colorScheme": "clear glass, matte black steel, warm interior glow"},
            "roofDetail": {"form": "flat with expressed steel crown frame", "material": "glass and steel crown structure"},
        },
        {
            "id": "glass_office_timber_hybrid",
            "label": "Mass Timber & Glass Hybrid",
            "color": "#A0785A",
            "description": "Mass timber and glass hybrid office with exposed CLT floor plates visible through glass, glulam columns, and biophilic interior gardens.",
            "facadeDetail": {"primaryMaterial": "structural glass revealing mass timber structure", "secondaryMaterial": "exposed glulam columns and CLT floor edges", "groundFloor": "timber-framed lobby with indoor trees", "colorScheme": "clear glass, honey-toned timber, interior greenery"},
            "roofDetail": {"form": "sawtooth with north-facing clerestory", "material": "timber deck with standing seam metal"},
        },
    ],
    "modernist_civic_block": [
        {
            "id": "modernist_civic_concrete_brutalist",
            "label": "Board-Formed Concrete",
            "color": "#778899",
            "description": "Heroic board-formed concrete civic block with deep reveals, cantilevered volumes, expressed structure, and monumental scale.",
            "facadeDetail": {"primaryMaterial": "board-formed exposed concrete", "secondaryMaterial": "deep concrete reveals and shadow lines", "groundFloor": "pilotis lifting main volume above ground plane", "colorScheme": "raw concrete, deep shadows, minimal"},
            "roofDetail": {"form": "flat cantilevered slab with expressed edge beam", "material": "exposed concrete with integrated drainage"},
        },
        {
            "id": "modernist_civic_white_corbusian",
            "label": "White Corbusian Modernism",
            "color": "#FFFFF0",
            "description": "Crisp white-rendered modernist block on pilotis with ribbon windows, roof garden, and free plan visible through transparent ground floor.",
            "facadeDetail": {"primaryMaterial": "smooth white cement render", "secondaryMaterial": "continuous horizontal ribbon windows", "groundFloor": "pilotis with free-standing columns in open ground floor", "colorScheme": "pure white, strip glazing, primary color accents"},
            "roofDetail": {"form": "flat roof garden with parapet", "material": "accessible roof garden with pergola"},
        },
        {
            "id": "modernist_civic_precast_panel",
            "label": "Precast Panel System",
            "color": "#A9A9A9",
            "description": "Systematic precast concrete panel civic building with repetitive window grid, expressed joints, and bold entrance canopy.",
            "facadeDetail": {"primaryMaterial": "bush-hammered precast concrete panels", "secondaryMaterial": "exposed panel joints with neoprene gaskets", "groundFloor": "bold cantilevered concrete entrance canopy", "colorScheme": "light grey precast, dark gaskets, recessed glazing"},
            "roofDetail": {"form": "flat with precast parapet panels", "material": "membrane with precast concrete coping"},
        },
        {
            "id": "modernist_civic_glass_volume",
            "label": "Transparent Glass Volume",
            "color": "#B0E0E6",
            "description": "Fully glazed modernist civic block — a transparent volume revealing public functions inside, with minimal steel structure and night-time civic glow.",
            "facadeDetail": {"primaryMaterial": "full-height structural glass walls", "secondaryMaterial": "slender steel cruciform columns", "groundFloor": "continuous glass at grade — no visual barrier to public", "colorScheme": "transparent glass, silver steel, warm interior light"},
            "roofDetail": {"form": "flat glass roof with steel structure", "material": "structural glass with steel space frame"},
        },
    ],
    "mid_century_modern_pavilion_block": [
        {
            "id": "mid_century_pavilion_glass_steel",
            "label": "Glass & Steel Pavilion",
            "color": "#2F4F4F",
            "description": "Mies-inspired glass and steel pavilion with expressed I-beam structure, floor-to-ceiling glass, travertine podium, and floating roof plane.",
            "facadeDetail": {"primaryMaterial": "floor-to-ceiling glass in black steel frames", "secondaryMaterial": "exposed wide-flange steel columns", "groundFloor": "travertine podium base with glass walls", "colorScheme": "clear glass, black steel, cream travertine"},
            "roofDetail": {"form": "flat floating plane with concealed edge", "material": "steel deck with white painted soffit"},
        },
        {
            "id": "mid_century_pavilion_wood_stone",
            "label": "Wood & Stone Organic",
            "color": "#8B7355",
            "description": "Wright-inspired organic mid-century with cantilevered stone terraces, horizontal board-and-batten wood siding, and integration with landscape.",
            "facadeDetail": {"primaryMaterial": "horizontal board-and-batten redwood siding", "secondaryMaterial": "cantilevered flagstone terraces", "groundFloor": "stone base anchoring into hillside", "colorScheme": "natural redwood, desert sandstone, landscape integration"},
            "roofDetail": {"form": "dramatic cantilever with deep eaves", "material": "copper with wide overhang"},
        },
        {
            "id": "mid_century_pavilion_white_concrete",
            "label": "White Concrete & Brise-Soleil",
            "color": "#DCDCDC",
            "description": "White concrete mid-century pavilion with egg-crate brise-soleil sun screens, elevated on slender columns, and a floating butterfly roof.",
            "facadeDetail": {"primaryMaterial": "white-painted concrete frame", "secondaryMaterial": "egg-crate concrete brise-soleil panels", "groundFloor": "open ground floor on slender round columns", "colorScheme": "white concrete, deep shadow patterns, tropical green"},
            "roofDetail": {"form": "inverted butterfly roof", "material": "white concrete shell"},
        },
        {
            "id": "mid_century_pavilion_brick_minimal",
            "label": "Brick & Glass Minimal",
            "color": "#CD853F",
            "description": "Minimal brick and glass mid-century with precise Roman brick courses, frameless glass corners, flat roof with wide fascia, and carport integration.",
            "facadeDetail": {"primaryMaterial": "Roman-format buff brick in running bond", "secondaryMaterial": "frameless glass corner windows", "groundFloor": "brick plinth with integrated planter walls", "colorScheme": "golden brick, clear glass, white fascia"},
            "roofDetail": {"form": "flat with wide painted fascia board", "material": "built-up tar and gravel with wide overhang"},
        },
    ],
}

# Import V2 definitions for the 34 archetypes that had generic templates
from variant_definitions_v2 import VARIANT_DEFINITIONS_V2
VARIANT_DEFINITIONS.update(VARIANT_DEFINITIONS_V2)

# For archetypes not in the manual definitions, generate sensible defaults
def _generate_default_variants(arch: dict) -> list[dict]:
    """Generate 4 generic design variants based on the archetype's existing metadata."""
    arch_id = arch["id"]
    title = arch.get("title", arch_id)
    base_facade = arch.get("facadeDetail", {})
    base_roof = arch.get("roofDetail", {})
    desc = arch.get("description", "")

    templates = [
        {
            "suffix": "timber_glass",
            "label": "Timber & Glass",
            "color": "#A67C52",
            "mat_primary": "cross-laminated timber (CLT) panels",
            "mat_secondary": "floor-to-ceiling structural glass",
            "ground": "timber-framed glazed entry with planted forecourt",
            "colors": "warm honey timber, clear glass, green accents",
            "roof_form": "flat with accessible green roof terrace",
            "roof_mat": "extensive sedum green roof",
            "desc_addon": "Warm mass timber construction with biophilic design, timber-framed glass facades, and green roof terrace.",
        },
        {
            "suffix": "white_metal",
            "label": "White Render & Metal",
            "color": "#4A7FA5",
            "mat_primary": "smooth white cement render",
            "mat_secondary": "anthracite powder-coated aluminum panels",
            "ground": "recessed glass entry with slim metal canopy",
            "colors": "brilliant white, dark grey metal, clear glass",
            "roof_form": "flat with expressed metal parapet edge",
            "roof_mat": "white membrane with metal coping",
            "desc_addon": "Crisp white-rendered volumes with contrasting dark metal panel accents, clean lines, and precision detailing.",
        },
        {
            "suffix": "brick_bronze",
            "label": "Brick & Bronze",
            "color": "#8B4513",
            "mat_primary": "dark handmade brick in stretcher bond",
            "mat_secondary": "bronze-anodized aluminum window frames and spandrels",
            "ground": "brick arched entry with bronze-framed glazing",
            "colors": "dark brick, warm bronze, deep reveals",
            "roof_form": "flat with brick parapet and bronze capping",
            "roof_mat": "membrane with bronze-capped brick parapet",
            "desc_addon": "Rich dark brick facade with warm bronze metalwork, deep window reveals, and traditional craft detailing.",
        },
        {
            "suffix": "concrete_corten",
            "label": "Concrete & Cor-Ten",
            "color": "#5B7065",
            "mat_primary": "board-formed exposed concrete",
            "mat_secondary": "weathering steel (Cor-Ten) panels and screens",
            "ground": "concrete plinth with Cor-Ten steel entry canopy",
            "colors": "raw concrete, rust-orange Cor-Ten, dark frames",
            "roof_form": "flat with Cor-Ten steel parapet screen",
            "roof_mat": "concrete slab with Cor-Ten edge panels",
            "desc_addon": "Raw industrial aesthetic with board-formed concrete and weathering steel panels, developing a natural patina over time.",
        },
    ]

    variants = []
    for t in templates:
        vid = f"{arch_id}_variant_{t['suffix']}"
        variants.append({
            "id": vid,
            "label": t["label"],
            "color": t["color"],
            "description": f"{title} in {t['label']} style. {t['desc_addon']}",
            "facadeDetail": {
                "primaryMaterial": t["mat_primary"],
                "secondaryMaterial": t["mat_secondary"],
                "groundFloor": t["ground"],
                "colorScheme": t["colors"],
            },
            "roofDetail": {
                "form": t["roof_form"],
                "material": t["roof_mat"],
            },
        })

    return variants


# ---------------------------------------------------------------------------
# Image generation
# ---------------------------------------------------------------------------

STYLE_ANCHOR = (
    "Style: photorealistic architectural visualization, high-end 3D rendering "
    "quality like a professional archviz studio. Warm golden-hour afternoon "
    "sunlight from the left at roughly 45 degrees, casting soft natural shadows. "
    "Slightly hazy atmospheric perspective in the background. Natural color "
    "grading with warm tones. Sharp detail on materials and textures — visible "
    "brick courses, glass reflections, concrete grain, metal patina. "
    "Photorealistic, 8K detail, architectural photography composition."
)

NO_PEOPLE = (
    "Absolutely no people, no human figures, no pedestrians, no silhouettes, "
    "no crowds anywhere in the scene. The scene is completely empty of humans."
)


def build_variant_prompt(arch_title: str, variant: dict) -> str:
    """Build a card image prompt for a building variant."""
    facade = variant.get("facadeDetail", {})
    roof = variant.get("roofDetail", {})

    desc = f"{arch_title} — {variant['label']} variant. {variant.get('description', '')}"
    if facade.get("primaryMaterial"):
        desc += f" Primary facade material: {facade['primaryMaterial']}."
    if facade.get("secondaryMaterial"):
        desc += f" Secondary material: {facade['secondaryMaterial']}."
    if facade.get("groundFloor"):
        desc += f" Ground floor: {facade['groundFloor']}."
    if facade.get("colorScheme"):
        desc += f" Color scheme: {facade['colorScheme']}."
    if roof.get("form"):
        desc += f" Roof: {roof['form']}."
    if roof.get("material"):
        desc += f" Roof material: {roof['material']}."

    desc += (
        " Surrounding context shows a typical urban street with mature "
        "trees and neighboring buildings of similar scale."
    )

    prompt = (
        "Photorealistic architectural visualization. "
        "Street-level perspective from across the street, approximately 25 meters away, "
        "at a 3/4 angle showing two facades. The full building is visible from ground "
        "to roofline with some sky above and street/sidewalk below. "
        f"{desc} "
        f"{NO_PEOPLE} {STYLE_ANCHOR}"
    )
    return prompt


def generate_image(prompt: str, retries: int = 5) -> bytes | None:
    """Call Gemini API to generate an image."""
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseModalities": ["TEXT", "IMAGE"],
            "temperature": 1.0,
        },
    }

    for attempt in range(retries):
        try:
            resp = httpx.post(API_URL, json=payload, timeout=120.0)
            if resp.status_code == 429:
                wait = 30 * (attempt + 1)
                print(f"  RATE LIMITED - waiting {wait}s (attempt {attempt + 1})")
                time.sleep(wait)
                continue
            resp.raise_for_status()
            data = resp.json()

            for candidate in data.get("candidates", []):
                for part in candidate.get("content", {}).get("parts", []):
                    if "inlineData" in part:
                        return base64.b64decode(part["inlineData"]["data"])

            print(f"  WARNING: No image in response (attempt {attempt + 1})")
            time.sleep(5)

        except Exception as e:
            print(f"  ERROR: {e} (attempt {attempt + 1})")
            time.sleep(10)

    return None


def save_image(image_bytes: bytes, output_path: Path) -> None:
    """Resize and save image."""
    img = Image.open(io.BytesIO(image_bytes))
    img = img.resize((CARD_WIDTH, CARD_HEIGHT), Image.LANCZOS)
    img.save(str(output_path), "PNG", optimize=True)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-existing", action="store_true")
    parser.add_argument("--json-only", action="store_true", help="Only update JSON, don't generate images")
    parser.add_argument("--force", action="store_true", help="Force-replace variants even if they exist (uses VARIANT_DEFINITIONS)")
    args = parser.parse_args()

    # Load building archetypes
    json_path = _DATA_DIR / "buildingArchetypes.json"
    data = json.loads(json_path.read_text(encoding="utf-8"))
    archetypes = data["archetypes"]

    updated_count = 0
    image_tasks = []

    for arch in archetypes:
        arch_id = arch["id"]

        # Check if this archetype has a proper definition in VARIANT_DEFINITIONS
        has_proper_def = arch_id in VARIANT_DEFINITIONS

        # If --force and we have a proper definition, always replace
        # Otherwise skip if already has variants
        if arch.get("variants") and len(arch["variants"]) >= 4:
            if not (args.force and has_proper_def):
                print(f"SKIP (has variants): {arch.get('title', arch_id)}")
                for vi, v in enumerate(arch["variants"]):
                    out_dir = _PUBLIC_DIR / "buildings" / arch_id
                    img_path = out_dir / f"variant_{vi}.png"
                    if not img_path.exists() or not args.skip_existing:
                        image_tasks.append({
                            "arch_title": arch.get("title", arch_id),
                            "variant": v,
                            "output_dir": out_dir,
                            "filename": f"variant_{vi}.png",
                            "thumb_url": f"/archetypes/buildings/{arch_id}/variant_{vi}.png",
                            "variant_index": vi,
                            "arch_id": arch_id,
                        })
                continue
            else:
                print(f"FORCE-REPLACING: {arch.get('title', arch_id)} (has proper V2 definitions)")

        # Get or generate variants
        if has_proper_def:
            variants = VARIANT_DEFINITIONS[arch_id]
        else:
            variants = _generate_default_variants(arch)

        # Add variants to archetype
        arch["variants"] = []
        for vi, v in enumerate(variants):
            thumb_url = f"/archetypes/buildings/{arch_id}/variant_{vi}.png"
            arch_variant = {
                "id": v["id"],
                "label": v["label"],
                "thumbnailUrl": thumb_url,
                "description": v.get("description", ""),
                "facadeDetail": v.get("facadeDetail", {}),
                "roofDetail": v.get("roofDetail", {}),
                "shadeId": v.get("shadeId"),
                "palette": {"primary": v.get("color", "#888888")},
            }
            arch["variants"].append(arch_variant)

            out_dir = _PUBLIC_DIR / "buildings" / arch_id
            img_path = out_dir / f"variant_{vi}.png"
            if not args.skip_existing or not img_path.exists():
                image_tasks.append({
                    "arch_title": arch.get("title", arch_id),
                    "variant": v,
                    "output_dir": out_dir,
                    "filename": f"variant_{vi}.png",
                    "thumb_url": thumb_url,
                    "variant_index": vi,
                    "arch_id": arch_id,
                })

        updated_count += 1
        print(f"ADDED variants: {arch.get('title', arch_id)} ({len(variants)} variants)")

    # Save updated JSON
    json_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nUpdated {updated_count} archetypes with variants in {json_path.name}")
    print(f"Image generation tasks: {len(image_tasks)}")

    if args.json_only:
        print("--json-only: skipping image generation")
        return

    # Generate images
    generated = 0
    failed = 0
    skipped = 0

    for i, task in enumerate(image_tasks):
        out_dir = task["output_dir"]
        img_path = out_dir / task["filename"]

        if args.skip_existing and img_path.exists():
            skipped += 1
            continue

        print(f"\n[{i+1}/{len(image_tasks)}] Generating: {task['arch_title']} - {task['variant']['label']}")
        prompt = build_variant_prompt(task["arch_title"], task["variant"])
        print(f"  Prompt length: {len(prompt)} chars")
        print(f"  Calling Gemini API...")

        image_bytes = generate_image(prompt)
        if image_bytes:
            out_dir.mkdir(parents=True, exist_ok=True)
            save_image(image_bytes, img_path)
            size_kb = img_path.stat().st_size / 1024
            print(f"  Saved: {img_path} ({size_kb:.1f} KB)")
            generated += 1
        else:
            print(f"  FAILED - skipping {task['variant']['label']}")
            failed += 1

        # Small delay between requests
        time.sleep(2)

    print(f"\n{'='*60}")
    print(f"Done! {generated} generated, {failed} failed, {skipped} skipped")


if __name__ == "__main__":
    main()
