#!/usr/bin/env python3
"""
Generate 12 experimental speculative archetypes (4 buildings, 4 parks, 4 streets).

Each archetype is a 1000-year-future concept rooted in a specific pressure —
climate adaptation, bioengineered materials, post-scarcity energy, multispecies
urbanism, deep-time memory. Each archetype's 4 variants differ across climate /
philosophy / era / scale, each with a distinct story — not facade swaps.

Pipeline: for each archetype, generate hero + 4 variant PNGs via Gemini 3.1
Flash Image Preview (text-to-image), save to frontend/public/archetypes/, then
splice Tier-1 metadata into the appropriate catalog JSON via text-level edits.

Usage:
    python scripts/generate_experimental_archetypes.py --dry-run
    python scripts/generate_experimental_archetypes.py --limit=1   # test one
    python scripts/generate_experimental_archetypes.py             # all 12
"""

from __future__ import annotations

import base64
import json
import sys
import time
from pathlib import Path
from typing import Any

import httpx

# Reconfigure stdout for UTF-8 so non-ASCII labels don't crash Windows cp1252 console.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except AttributeError:
    pass

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parent.parent
PUBLIC = ROOT / "frontend" / "public" / "archetypes"
ENV_FILE = ROOT / "backend" / ".env"
CATALOGS = {
    "buildings": ROOT / "frontend" / "src" / "data" / "buildingArchetypes.json",
    "openspaces": ROOT / "frontend" / "src" / "data" / "openSpaceArchetypes.json",
    "streets": ROOT / "frontend" / "src" / "data" / "streetPathArchetypes.json",
}
MODEL = "gemini-3.1-flash-image-preview"


def load_gemini_key() -> str:
    if not ENV_FILE.exists():
        print(f"ERROR: .env missing at {ENV_FILE}")
        sys.exit(1)
    for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("GEMINI_API_KEY="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    print("ERROR: GEMINI_API_KEY not in backend/.env")
    sys.exit(1)


def gemini_url() -> str:
    key = load_gemini_key()
    return (
        f"https://generativelanguage.googleapis.com/v1beta/"
        f"models/{MODEL}:generateContent?key={key}"
    )


STYLE_SUFFIX = (
    " Photorealistic architectural concept rendering. Cinematic lighting. "
    "Sharp material detail. Not illustration, not cartoon, not stylised — "
    "documentary photography of a real place that just happens to be from "
    "a 1000-year future. 8K detail, professional architectural photography."
)


# ---------------------------------------------------------------------------
# The 12 experimental archetypes — each with 4 story-driven variants
# ---------------------------------------------------------------------------

ARCHETYPES: list[dict[str, Any]] = [
    # ═══════════════════════════════════════════════════════════════════════
    # BUILDINGS (4)
    # ═══════════════════════════════════════════════════════════════════════
    {
        "kind": "buildings",
        "slug": "experimental-grown-habitat-tree",
        "id": "experimental_grown_habitat_tree",
        "title": "Grown Habitat Tree",
        "subcategory": "Experimental",
        "development_type": "residential_multifamily",
        "aesthetic_category": "experimental_biogenic",
        "description": (
            "A family of living architectural towers grown from engineered "
            "mycelium, atmospheric-carbon fibre, and photosynthetic bioplastic. "
            "The building grows with its inhabitants — new branches added as "
            "a family expands, dormant limbs pruned as generations pass. Walls "
            "repair themselves; windows are crystallised sap membranes; the "
            "building itself sequesters carbon, produces oxygen, and feeds "
            "pollinators. The canonical post-extraction dwelling."
        ),
        "tags": ["experimental", "biogenic", "living-architecture", "post-extraction",
                 "multispecies", "mycelium", "carbon-negative"],
        "style_profile": {
            "materials": [
                "engineered mycelium structural members",
                "atmospheric-carbon bioplastic skin",
                "crystallised sap window membranes",
                "photosynthetic living outer layer",
                "self-healing bio-composite"
            ],
            "facadeRhythm": "Organic branching rhythm — apartments as pod-chambers nested along limbs",
            "roofForm": "Canopy crown with seasonally shifting pollinator flowers",
            "frontageType": "Buttressed root-plinth with communal entry hollows",
            "windowStyle": "Translucent sap membranes, organic aperture shapes",
            "massing": "Tree-like trunk + radiating branches + canopy, 80-300m tall",
            "heightTendency": "Mid-rise to tall (80-300m), tapering with age and species",
            "streetRelationship": "Root system extends beneath sidewalks, integrates with urban water table",
            "renderingMood": "Sacred, alive, warm — like standing beneath an ancient grove",
            "articulation": "Growth rings visible at scale; branches thicken over decades",
            "publicRealm": "Root-level communal hollows, canopy observation platforms"
        },
        "prompt_block": {
            "subject": "A living architectural tree — a multi-generational dwelling grown, not built",
            "details": [
                "Organic branching massing with apartment pod-chambers",
                "Living photosynthetic outer skin",
                "Crystallised sap window membranes",
                "Visible aerial or buttress roots at the base",
                "Canopy crown with seasonal pollinator flowers",
                "Scale: 80-300m, inhabitable at all heights"
            ]
        },
        "suggested_width_m": 40,
        "suggested_depth_m": 40,
        "min_floors": 10,
        "max_floors": 60,
        "hero_prompt": (
            "A family of four living architectural 'habitat trees' at varying heights clustered "
            "in a mixed-use neighbourhood of a 1000-year-future city at golden hour. Each tree is "
            "grown from engineered mycelium and photosynthetic bioplastic — organic branching "
            "trunks with apartment pod-chambers nested in the branches, crystallised sap window "
            "membranes glowing warm amber. Aerial roots descend at the bases. Low warm sun behind. "
            "Photorealistic, architectural concept photography, sharp material detail, atmospheric."
        ),
        "variants": [
            {
                "id": "grown_habitat_tropical_mangrove",
                "label": "Tropical Mangrove Tower",
                "story": (
                    "In equatorial coastal cities after sea level rise, families grow habitat "
                    "trees directly in the new shoreline. Aerial roots braid down into shallow "
                    "salt water; fig-like branches carry apartments; leaves are silvery-backed "
                    "for heat reflection. The building filters seawater and hosts a tidal "
                    "biome at its base."
                ),
                "color": "#2D5E3A",
                "min_floors": 15, "max_floors": 40,
                "suggested_floor_height": 3.6, "suggested_area_sqm": 2800,
                "prompt": (
                    "A 150-meter-tall living architectural tree rooted in shallow tidal mudflats "
                    "at the edge of a tropical coastal city at late-afternoon golden hour. Smooth "
                    "engineered bioplastic bark in deep jade green. Aerial buttress roots descend "
                    "30-40m from the trunk into shallow salt water, lit by warm low sun casting "
                    "long reflections. Fig-like horizontal branches carry organic pod-chamber "
                    "apartments glowing warm from within. Broad silver-backed leaves at the crown "
                    "shimmer. Mangrove root clusters at the waterline. Small boats moored nearby."
                ),
                "facade_primary": "engineered bioplastic bark in deep jade green",
                "facade_secondary": "aerial buttress roots descending into salt water",
                "facade_ground": "mangrove-rooted tidal mudflat plinth",
                "facade_palette": "deep jade bark, silver-backed leaves, warm amber windows",
                "roof_form": "broad silver-backed leaf canopy",
                "roof_material": "photosynthetic leaf membrane"
            },
            {
                "id": "grown_habitat_boreal_mycotecture",
                "label": "Boreal Mycotecture Spire",
                "story": (
                    "In cold climate cities, a mushroom-form strain that thickens its insulating "
                    "mycelium walls in winter (R-80 passive insulation) and photosynthesises in "
                    "the short intense summer. Windows are deep-set circular apertures. Dormant "
                    "winter mode rings visible as growth bands."
                ),
                "color": "#E8DEC2",
                "min_floors": 8, "max_floors": 25,
                "suggested_floor_height": 3.2, "suggested_area_sqm": 2200,
                "prompt": (
                    "A 120-meter-tall living architectural tower with a broad conical mushroom-"
                    "shaped massing in a boreal forest setting during early winter. Exterior is "
                    "thick cream-white mycelium skin with faint golden mottling and subtle "
                    "horizontal growth-ring bands. Windows are deep-set circular amber apertures. "
                    "Snow dusts the upper ridges. Dense pine forest and snow at the base. Soft "
                    "diffuse winter daylight. Atmospheric, sculptural, warm interior light glowing "
                    "through deep apertures."
                ),
                "facade_primary": "thick cream insulating mycelium skin",
                "facade_secondary": "horizontal growth-ring bands expressing annual cycles",
                "facade_ground": "mycelial root plinth anchored in frozen ground",
                "facade_palette": "cream mycelium, golden mottle, warm amber windows",
                "roof_form": "conical mushroom cap with spore-chimney vents",
                "roof_material": "thickened winter-mode mycelium cap"
            },
            {
                "id": "grown_habitat_desert_baobab",
                "label": "Desert Carbon-Sink Baobab",
                "story": (
                    "In rewilded deserts, a fat-trunked baobab-form where the swollen trunk "
                    "stores water and sequestered atmospheric carbon. Minimal openings to "
                    "reject heat. At dusk, the crown unfurls massive white night-blooming "
                    "flowers that feed moth-and-bat pollinator networks."
                ),
                "color": "#A8927A",
                "min_floors": 6, "max_floors": 20,
                "suggested_floor_height": 3.8, "suggested_area_sqm": 3200,
                "prompt": (
                    "A 90-meter-tall building shaped like a swollen baobab tree rooted in a red "
                    "desert at dusk. Bulbous grey-brown sculptural bioplastic bark facade. Small "
                    "circular window apertures glow warm orange. At the crown, a cluster of "
                    "massive white-petalled night-blooming flowers are half-open, catching the "
                    "last light. Deep purple-indigo twilight sky with first stars. Scattered "
                    "rewilded desert plants (succulents, desert grasses) at the base. Long cool "
                    "shadows. Sculptural, sacred, silent."
                ),
                "facade_primary": "swollen grey-brown carbon-sink bioplastic bark",
                "facade_secondary": "minimal deep-set circular apertures",
                "facade_ground": "root-flare bulge integrating with rewilded desert floor",
                "facade_palette": "grey-brown bark, orange window glow, white night-bloom petals",
                "roof_form": "flowering crown that opens at dusk for pollinators",
                "roof_material": "massive white-petalled bioengineered night-bloom flowers"
            },
            {
                "id": "grown_habitat_mass_timber_hybrid",
                "label": "Mass-Timber Hybrid Living Skin",
                "story": (
                    "The transitional species — engineered cross-laminated timber structural "
                    "frame with a dense living skin of mosses, ferns, and climbing vines grown "
                    "across every face. Still legibly a building from a distance, clearly alive "
                    "at touch. Common in temperate cities as first-generation biogenic retrofit."
                ),
                "color": "#5F7D3B",
                "min_floors": 5, "max_floors": 15,
                "suggested_floor_height": 3.4, "suggested_area_sqm": 1800,
                "prompt": (
                    "A 60-meter-tall rectangular contemporary building in a temperate European "
                    "city at midday. Exposed cross-laminated timber post-and-beam structure is "
                    "visible through a dense living skin of lush green mosses, ferns, and "
                    "climbing vines covering every face. Glass infill panels between timber "
                    "beams catch sky reflections. Small green-roof gardens on each floor. "
                    "Street trees below. Warm clean daylight with slight atmospheric haze. "
                    "Wet moss textures, crisp architectural photography."
                ),
                "facade_primary": "exposed cross-laminated timber post-and-beam structure",
                "facade_secondary": "dense living skin of mosses, ferns, and climbing vines",
                "facade_ground": "timber-framed ground-floor lobby with integrated rainwater swale",
                "facade_palette": "warm timber tones, lush green living skin, glass reflections",
                "roof_form": "stepped green-roof terraces on every floor",
                "roof_material": "intensive green-roof planting over timber deck"
            }
        ]
    },
    {
        "kind": "buildings",
        "slug": "experimental-memory-cathedral",
        "id": "experimental_memory_cathedral",
        "title": "Memory Cathedral",
        "subcategory": "Experimental",
        "development_type": "institutional",
        "aesthetic_category": "experimental_archival",
        "description": (
            "A monumental civic structure where every surface brick is a digital resonator "
            "holding a second of the site's history. Visitors touch the walls to summon "
            "holographic memories into being. A new skin layer accretes every century, "
            "making the building a literal stratified archive of its place. Part library, "
            "part reliquary, part clock."
        ),
        "tags": ["experimental", "deep-time", "memory", "archival", "civic", "monumental", "touch-interactive"],
        "style_profile": {
            "materials": ["quantum-dot memory bricks", "carved stone base", "graphene reinforcement lattice", "layered century-skins"],
            "facadeRhythm": "Tight brick grid at human scale, each brick ~5cm square",
            "roofForm": "Stepped crown with open sky-well for astronomical resonance",
            "frontageType": "Monumental civic entry with processional approach",
            "windowStyle": "Narrow vertical memory-slits glowing with archive activity",
            "massing": "Monolithic sculptural form with faceted or stepped geometry",
            "heightTendency": "Mid-rise monumental (30-80m)",
            "streetRelationship": "Setback plaza with processional approach and memory-touch waypoints",
            "renderingMood": "Reverent, ancient-future, softly humming with latent archive",
            "articulation": "Century-strata visible as horizontal banding; touch-wear patina at human height",
            "publicRealm": "Approach plaza + inner orans courtyard for communal memory rituals"
        },
        "prompt_block": {
            "subject": "A monumental civic memory archive — a building whose bricks each hold a second of the site's history",
            "details": [
                "Monolithic sculptural massing with century-strata horizontal banding",
                "Tight grid of small ~5cm quantum-dot memory bricks",
                "Narrow vertical memory-slit windows glowing with archive activity",
                "Open sky-well at the crown",
                "Monumental processional entry",
                "Inner open courtyard for communal memory rituals"
            ]
        },
        "suggested_width_m": 50,
        "suggested_depth_m": 50,
        "min_floors": 6,
        "max_floors": 20,
        "hero_prompt": (
            "A monumental civic Memory Cathedral at twilight — a 60-meter-tall sculptural "
            "building covered in tight grid of small glowing indigo-blue memory bricks, with "
            "horizontal century-strata banding and narrow vertical light slits. Tall processional "
            "entry. Set on a wide plaza with visitors approaching. Faintly glowing holographic "
            "wisps rise from where people touch the walls. Indigo twilight sky. Cinematic, "
            "reverent, ancient-future architecture."
        ),
        "variants": [
            {
                "id": "memory_cathedral_indigo_archive",
                "label": "Indigo Archive",
                "story": (
                    "Built over a former library district. Deep indigo quantum-dot bricks hum "
                    "faintly blue at night. Carved stone base expresses the library lineage "
                    "with incised text fragments in dead languages. The canonical civic memorial."
                ),
                "color": "#2A3A7A",
                "min_floors": 8, "max_floors": 14,
                "suggested_floor_height": 5.0, "suggested_area_sqm": 2200,
                "prompt": (
                    "A monumental 50-meter Memory Cathedral at dusk with a tight grid facade of "
                    "small glowing deep-indigo-blue quantum-dot memory bricks. Horizontal "
                    "century-strata banding visible. Narrow vertical light slits glow warm amber. "
                    "Carved sandstone base with incised text fragments in ancient scripts. "
                    "Monumental processional entry with tall double doors. A wide plaza with a "
                    "few visitors approaching, faint holographic memory-wisps rising where they "
                    "touch the walls. Twilight sky with first stars. Cinematic, reverent."
                ),
                "facade_primary": "deep indigo quantum-dot memory bricks in tight 5cm grid",
                "facade_secondary": "carved sandstone base with incised ancient-script text fragments",
                "facade_ground": "monumental processional double-door entry",
                "facade_palette": "deep indigo, warm amber light slits, pale sandstone base",
                "roof_form": "stepped crown with central open sky-well",
                "roof_material": "quantum-dot bricks at rooftop with integrated starlight resonators"
            },
            {
                "id": "memory_cathedral_sand_monolith",
                "label": "Sand-White Desert Monolith",
                "story": (
                    "The desert variant. Thin glass-silica skin catches harsh sun; memories "
                    "activate through solar pulses during the day and cool into quiet archive "
                    "at night. Ancient-feeling ziggurat step form — the first Memory Cathedral "
                    "form to have been built, and still the model."
                ),
                "color": "#E8DDC7",
                "min_floors": 6, "max_floors": 10,
                "suggested_floor_height": 5.2, "suggested_area_sqm": 3000,
                "prompt": (
                    "A monumental stepped ziggurat-form Memory Cathedral in a sun-bleached "
                    "desert landscape at noon. Pale sand-white facade of thin glass-silica "
                    "plates with slight iridescent sheen catching the harsh sun. Small windows "
                    "and slit apertures. Geometric terraced steps casting sharp shadows. The "
                    "surrounding desert floor is pale cracked clay. Harsh overhead sunlight. "
                    "Severe, ancient, timeless. Photorealistic architectural photography."
                ),
                "facade_primary": "thin pale iridescent glass-silica plates",
                "facade_secondary": "stepped ziggurat terraces with geometric shadow",
                "facade_ground": "cracked pale clay desert plinth",
                "facade_palette": "sand-white silica, iridescent sheen, pale clay",
                "roof_form": "flat stepped terraces crowned by an open sky altar",
                "roof_material": "thickened silica plates with solar-resonance embeds"
            },
            {
                "id": "memory_cathedral_obsidian_sanctum",
                "label": "Black Obsidian Sanctum",
                "story": (
                    "A smaller Memory Cathedral built at a meteorite impact site. Faceted "
                    "black obsidian-glass skin reflects the stars; memories of ancient impacts "
                    "surface. Small-scale sanctum, intensely interior. For grief and deep time."
                ),
                "color": "#0F0B1E",
                "min_floors": 4, "max_floors": 7,
                "suggested_floor_height": 4.8, "suggested_area_sqm": 1000,
                "prompt": (
                    "A small faceted monumental sanctum-building with black obsidian-glass "
                    "faceted facade reflecting a starry night sky. Tall narrow vertical form, "
                    "roughly 25 meters tall. Thin vertical light slots glow warm amber-orange. "
                    "Set on dark volcanic rock ground with scattered stones. Sacred, silent, "
                    "mysterious. Stars and milky way visible above. Cinematic night photography, "
                    "sharp faceted reflections, atmospheric."
                ),
                "facade_primary": "faceted polished obsidian-glass quantum-dot bricks",
                "facade_secondary": "thin vertical amber light slits",
                "facade_ground": "dark volcanic rock plinth with scattered meteorite fragments",
                "facade_palette": "deep black obsidian, starlight reflections, warm amber slits",
                "roof_form": "tapered point with a single open sky-well aligned to zenith",
                "roof_material": "obsidian faceted crown"
            },
            {
                "id": "memory_cathedral_verdigris",
                "label": "Verdigris Cathedral",
                "story": (
                    "The ancient-future variant — already 500 years old in our reference. "
                    "Oxidised copper-green skin over carved stone base. Ivy and moss creeping "
                    "up. The Memory Cathedral that has BECOME memory, its century-strata now "
                    "encrusted with its own patina."
                ),
                "color": "#5D8A6E",
                "min_floors": 5, "max_floors": 12,
                "suggested_floor_height": 5.0, "suggested_area_sqm": 2400,
                "prompt": (
                    "A weathered monumental 40-meter Memory Cathedral with oxidised copper-"
                    "green (verdigris) quantum-dot brick skin and a carved pale sandstone base. "
                    "Patches of moss and lichen creeping up the lower walls. Tall narrow "
                    "pointed memory-window slits glow warm from within at late-afternoon "
                    "golden hour. Ivy climbing the south facade. Set in a cobbled plaza with "
                    "old plane trees and worn stone benches. Rich aged textures, patina, "
                    "moss, warm golden light. Photorealistic, atmospheric, lived-in."
                ),
                "facade_primary": "oxidised copper-green verdigris memory bricks",
                "facade_secondary": "carved pale sandstone base with weathered ornament",
                "facade_ground": "cobbled plaza entry with worn stone benches",
                "facade_palette": "verdigris green, pale aged sandstone, moss, warm amber light",
                "roof_form": "copper-green stepped crown with open sky-well and weathervane resonators",
                "roof_material": "aged verdigris copper cladding over resonator substrate"
            }
        ]
    },
    {
        "kind": "buildings",
        "slug": "experimental-vertical-polynya",
        "id": "experimental_vertical_polynya",
        "title": "Vertical Polynya",
        "subcategory": "Experimental",
        "development_type": "residential_highrise",
        "aesthetic_category": "experimental_inverse",
        "description": (
            "An inverse arcology — a 1-2km tall slender vertical void carved through urban "
            "density, lined with vertical gardens, waterfalls, crop racks, and open-air civic "
            "nodes. People live on the inner walls looking inward across the void, not "
            "outward over the city. The architecture is the EMPTY SPACE; the void is "
            "simultaneously the lobby, the park, the climate cooler, and the view."
        ),
        "tags": ["experimental", "inverse-arcology", "void-architecture", "vertical-urbanism",
                 "climate-cooled", "multi-program"],
        "style_profile": {
            "materials": ["tensegrity cable-shell outer frame", "climbing plant curtains on inner walls",
                           "glass + bio-composite terrace projections", "water-cascade infrastructure"],
            "facadeRhythm": "Continuous inner cliff-like vertical expression punctuated by projecting terraces every 20-40m",
            "roofForm": "Open to sky — the void IS the atrium",
            "frontageType": "Outer ring of entry arcades opening to the void",
            "windowStyle": "Large operable glass walls facing inward across the void",
            "massing": "Slender hollow cylinder or tapered cone, 1-2km tall, 80-200m diameter void",
            "heightTendency": "Ultra-tall (800-2000m)",
            "streetRelationship": "Ground-floor plaza at the void base with water feature and microclimate",
            "renderingMood": "Sublime vertical scale, soft filtered light, falling water ambient sound",
            "articulation": "Inner void reads as a sublime architectural canyon",
            "publicRealm": "Void floor plaza, mid-height civic rings, cable-stayed sky bridges"
        },
        "prompt_block": {
            "subject": "A vertical architectural void carved through urban density — people live on its inner walls",
            "details": [
                "Slender hollow cylinder 1-2km tall with 80-200m diameter open interior",
                "Inner walls covered in vertical gardens, cascading waterfalls, projecting terraces",
                "Apartments face INWARD across the void, not outward",
                "Open to sky — no roof",
                "Mid-height civic nodes and cable-stayed sky bridges across the void",
                "Ground plaza at the base of the void"
            ]
        },
        "suggested_width_m": 200,
        "suggested_depth_m": 200,
        "min_floors": 60,
        "max_floors": 200,
        "hero_prompt": (
            "Looking up into an ultra-tall 1.5km architectural void cut through a dense future "
            "city at mid-morning. Cylindrical inner walls rise out of sight, lined with vertical "
            "gardens, small waterfalls cascading down, projecting glass-and-vine terraces every "
            "30 meters with tiny human figures. Open sky at the top. Filtered sunlight streaming "
            "down. Mist at the floor. Dramatic vertical perspective. Sublime scale. Photorealistic "
            "architectural concept photography, atmospheric, awe-inducing."
        ),
        "variants": [
            {
                "id": "vertical_polynya_equatorial",
                "label": "Equatorial Rainforest Void",
                "story": (
                    "In tropical megalopolis, the void becomes a vertical rainforest — "
                    "cascading vines, hummingbirds, epiphytes clinging to sheer walls, warm "
                    "humid air rising continuously. The void is both climate infrastructure "
                    "(draws heat up and out) and a multispecies biome."
                ),
                "color": "#1F6B3D",
                "min_floors": 120, "max_floors": 200,
                "suggested_floor_height": 4.0, "suggested_area_sqm": 8000,
                "prompt": (
                    "Looking up into a 2km vertical architectural void cut through a tropical "
                    "megalopolis at mid-morning. Sheer inner cylindrical walls covered in "
                    "cascading tropical vines, orchids, bromeliads, ferns. Small living terraces "
                    "projecting inward with tiny human figures. Hummingbirds in flight. Faint "
                    "mist and humid air. Filtered bright sunlight from above. Rich biological "
                    "detail, dramatic vertical perspective, photorealistic concept photography."
                ),
                "facade_primary": "inner cylindrical walls covered in cascading tropical vines",
                "facade_secondary": "projecting glass-and-timber terraces with orchids and bromeliads",
                "facade_ground": "misty ground-level plaza with tropical pool and ferns",
                "facade_palette": "deep forest green, warm timber terraces, bright tropical flowers",
                "roof_form": "open to sky — no ceiling; just the open aperture to the sun",
                "roof_material": "none — the void IS the roof"
            },
            {
                "id": "vertical_polynya_arctic_shaft",
                "label": "Arctic Aurora Shaft",
                "story": (
                    "In high-latitude cities, a pristine white ceramic-lined void channels "
                    "the aurora borealis downward through the city. Mid-height observation "
                    "platforms; heated lower levels release gentle steam. Long winter days "
                    "are spent looking UP into the sky, not forward."
                ),
                "color": "#B6D6E6",
                "min_floors": 80, "max_floors": 160,
                "suggested_floor_height": 4.2, "suggested_area_sqm": 6500,
                "prompt": (
                    "Looking up into a cylindrical vertical void cut through a dense arctic "
                    "city at night. Pristine white ceramic-plated inner walls reflecting "
                    "aurora borealis light — shimmering greens, magentas, pale purples flowing "
                    "down the walls. Gentle steam rising from heated lower levels. Snow dusting "
                    "the upper rim. Small warm-lit apartment windows inset into the walls. Thin "
                    "sky bridges crossing mid-height. Dramatic cold atmospheric lighting, "
                    "sublime scale."
                ),
                "facade_primary": "pristine white ceramic-plated inner cladding",
                "facade_secondary": "thin inset apartment windows glowing warm amber",
                "facade_ground": "heated basin plaza with hot springs, steam, and ice pools",
                "facade_palette": "white ceramic, aurora green-magenta reflections, warm amber apartment light",
                "roof_form": "open aperture to the night sky framing the aurora",
                "roof_material": "none — the sky is the ceiling"
            },
            {
                "id": "vertical_polynya_temperate_falls",
                "label": "Temperate Rain Forest Void",
                "story": (
                    "Pacific-Northwest-climate variant. Integrated waterfalls cascade down "
                    "the walls, generating hydroelectric power while irrigating fern-and-"
                    "moss wall gardens. Timber viewing platforms at every level. Cool mist "
                    "year-round."
                ),
                "color": "#3E6A52",
                "min_floors": 80, "max_floors": 140,
                "suggested_floor_height": 4.0, "suggested_area_sqm": 7000,
                "prompt": (
                    "Looking up into a 1.5km vertical architectural void in a Pacific-Northwest "
                    "city at soft overcast morning. Inner walls of mossy stone and engineered "
                    "dark timber, covered in cascading waterfalls and lush fern gardens. Warm "
                    "timber observation platforms projecting at every few levels. Soft cool "
                    "mist rising. Filtered grey daylight from above. Sound of flowing water "
                    "suggested. Lush, atmospheric, serene."
                ),
                "facade_primary": "mossy basalt-textured inner walls with cascading waterfalls",
                "facade_secondary": "fern and moss wall gardens irrigated by the falling water",
                "facade_ground": "basin-pool forest floor with ferns and timber boardwalks",
                "facade_palette": "deep moss green, dark timber, silver waterfalls, soft grey light",
                "roof_form": "open to the grey Pacific sky with hanging mist",
                "roof_material": "none"
            },
            {
                "id": "vertical_polynya_urban_retrofit",
                "label": "Urban Retrofit Polynya",
                "story": (
                    "Carved through existing late-20th-century office towers that were "
                    "preserved rather than demolished. The inner walls are a cross-section of "
                    "history — exposed concrete slabs, glass curtain-wall fragments, brick "
                    "infill, patched with new biogenic skin. A living archaeological artefact."
                ),
                "color": "#8A7E72",
                "min_floors": 60, "max_floors": 120,
                "suggested_floor_height": 3.8, "suggested_area_sqm": 5000,
                "prompt": (
                    "Looking up into a vertical architectural void cut like a core sample "
                    "through existing 20th-century office towers. The inner walls are a rich "
                    "cross-section of urban history — exposed concrete floor slabs, glass "
                    "curtain-wall fragments, brick infill, layered materials, patched here "
                    "and there with new green living terraces and climbing vines. "
                    "Heterogeneous materiality. Afternoon sun. Photorealistic architectural "
                    "documentary photography, atmospheric."
                ),
                "facade_primary": "heterogeneous cross-section of retained 20th-century building skins",
                "facade_secondary": "new living green-terrace patches retrofitted into the old",
                "facade_ground": "urban plaza floor with salvaged pavement patterns",
                "facade_palette": "exposed concrete, aged glass, brick, green patches, aged steel",
                "roof_form": "open sky with surviving upper tower fragments at the rim",
                "roof_material": "none"
            }
        ]
    },
    {
        "kind": "buildings",
        "slug": "experimental-nomadic-dacha",
        "id": "experimental_nomadic_dacha",
        "title": "Nomadic Dacha",
        "subcategory": "Experimental",
        "development_type": "residential_single_family",
        "aesthetic_category": "experimental_mobile",
        "description": (
            "A small autonomous dwelling (~12m x 12m) mounted on six robotic legs, walking "
            "slowly (~100m/day) along a migration route across rewilded continents. Solar-"
            "skinned, closed-loop water, prints its own spare parts from atmospheric feedstock. "
            "The occupant owns a ROUTE, not a plot. Architecture finally untethered from land."
        ),
        "tags": ["experimental", "nomadic", "walking-architecture", "post-property",
                 "autonomous", "migratory", "single-household"],
        "style_profile": {
            "materials": ["titanium + carbon-fibre leg structure", "climate-specific outer skin",
                           "photovoltaic roof canopy", "atmospheric-water-capture rails"],
            "facadeRhythm": "Single integrated skin continuous around all sides; legs visible as sculptural supports",
            "roofForm": "Broad solar canopy overhanging the body; collects rainwater",
            "frontageType": "Hinged entry ramp that lowers to the ground when stationary",
            "windowStyle": "Small porthole or slit apertures; context-reactive tinting",
            "massing": "Compact pavilion body (~12m × 12m × 4m) on 6 slender legs 3-8m tall",
            "heightTendency": "Low to mid (body 4-6m above ground depending on terrain)",
            "streetRelationship": "None — moves through landscape, not streets. Occasional 'resting plazas' at known waypoints",
            "renderingMood": "Quiet, graceful, slightly alien — like seeing a giraffe on the horizon",
            "articulation": "Leg joints exposed as hex mechanisms; body skin smooth and climate-adapted",
            "publicRealm": "Temporary ground-connection when stationary; gathering hearths at waypoint plazas"
        },
        "prompt_block": {
            "subject": "A small autonomous walking dwelling on 6 robotic legs, migrating across rewilded landscape",
            "details": [
                "Compact ~12m square pavilion body elevated on 6 legs",
                "Climate-specific outer skin (canvas, fur-pile, algal, etc.)",
                "Broad solar canopy roof overhanging the body",
                "Small porthole windows glowing with warm interior light",
                "Visible leg mechanisms — titanium + carbon-fibre",
                "Set in wild landscape, not a street"
            ]
        },
        "suggested_width_m": 12,
        "suggested_depth_m": 12,
        "min_floors": 1,
        "max_floors": 2,
        "hero_prompt": (
            "A small architectural walking dwelling on six slender robotic legs, standing "
            "in a wide rewilded savanna landscape at golden hour. The pavilion body is about "
            "12 meters square, clad in a beige climate-adaptive skin, topped with a broad "
            "overhanging dark photovoltaic canopy. Small porthole windows glow warm amber. "
            "Legs are 4 meters tall, articulated with visible hex mechanisms. A single thin "
            "stream of smoke from a hearth vent. Tall grasses and scattered acacia trees "
            "around. Sublime, graceful, alien-yet-domestic. Photorealistic architectural "
            "concept photography."
        ),
        "variants": [
            {
                "id": "nomadic_dacha_steppe_walker",
                "label": "Steppe Walker",
                "story": (
                    "Follows ancient Central Asian grassland migration routes — routes "
                    "re-established after the re-wilding. Beige canvas-tensile skin over "
                    "titanium frame. Low, wide-stance legs adapted to grassland terrain. "
                    "Yurt-inherited form."
                ),
                "color": "#C9B896",
                "min_floors": 1, "max_floors": 1,
                "suggested_floor_height": 3.2, "suggested_area_sqm": 140,
                "prompt": (
                    "A small architectural walking dwelling about 12 meters wide on six low "
                    "titanium robotic legs, standing in a wide Mongolian steppe at golden hour. "
                    "Beige canvas-tensile-skin over a lightweight titanium frame. Low, wide-"
                    "stance legs 3 meters tall. Dark photovoltaic panel canopy roof extending "
                    "out. A wild horse herd grazing 100 meters away. Tall golden grasses. Long "
                    "afternoon shadows. Sharp detail, atmospheric, serene."
                ),
                "facade_primary": "beige canvas-tensile climate skin stretched over titanium frame",
                "facade_secondary": "titanium hex-joint legs with carbon-fibre accents",
                "facade_ground": "temporary ground footprint — steppe grass beneath footpads",
                "facade_palette": "beige canvas, warm titanium, golden-grass surroundings",
                "roof_form": "broad overhanging dark photovoltaic canopy",
                "roof_material": "photovoltaic panels on carbon-fibre canopy frame"
            },
            {
                "id": "nomadic_dacha_rainforest_tracker",
                "label": "Rainforest Canopy Tracker",
                "story": (
                    "Follows seasonal fruiting cycles in a re-wilded Amazon basin. Deep green "
                    "algal bio-skin with faint bioluminescent moss patches that glow at night. "
                    "Tall slender legs for canopy-level travel between emergent trees."
                ),
                "color": "#1E4A32",
                "min_floors": 1, "max_floors": 2,
                "suggested_floor_height": 3.0, "suggested_area_sqm": 120,
                "prompt": (
                    "A small architectural walking dwelling on six tall slender robotic legs "
                    "(6-7 meters tall) standing at Amazon rainforest canopy level at dusk. "
                    "Deep green algal bio-skin with faint bioluminescent moss patches glowing "
                    "softly. Small arched windows with warm interior amber light. Tall trunks "
                    "of emergent kapok trees nearby. Mist in the air. Photorealistic, humid "
                    "atmospheric rainforest rendering, subtle bioluminescence, serene alien-"
                    "domestic mood."
                ),
                "facade_primary": "deep green algal bio-skin over carbon-fibre shell",
                "facade_secondary": "bioluminescent moss patches on the undersides",
                "facade_ground": "none — elevated at rainforest canopy level",
                "facade_palette": "deep forest green, faint bioluminescent cyan, warm amber windows",
                "roof_form": "small canopy with integrated rainwater funnel",
                "roof_material": "water-collecting bio-composite canopy"
            },
            {
                "id": "nomadic_dacha_arctic_ambler",
                "label": "Arctic Ambler",
                "story": (
                    "Tundra migration. Thick white fur-pile bio-composite insulation skin "
                    "(thickens in winter, thins in summer). Wide snowshoe-like feet. Slow "
                    "winter hibernation mode where the skin thickens dramatically and the "
                    "dwelling itself sleeps for months."
                ),
                "color": "#E8E8E8",
                "min_floors": 1, "max_floors": 1,
                "suggested_floor_height": 3.4, "suggested_area_sqm": 145,
                "prompt": (
                    "A small architectural walking dwelling on six robotic legs with wide "
                    "snowshoe-like footpads, crossing Arctic tundra in soft winter daylight. "
                    "Thick white fur-pile-textured bio-composite insulating outer skin, "
                    "slightly shaggy and warm-looking. Small deep-set circular portholes glow "
                    "warm amber-orange. Snow dusts the roof and canopy. A fresh trail of "
                    "snowshoe footprints trailing behind. Low pale winter sun casting long "
                    "blue shadows. Atmospheric, serene, crisp."
                ),
                "facade_primary": "thick white fur-pile bio-composite insulating skin",
                "facade_secondary": "titanium hex-joint legs with wide snowshoe footpads",
                "facade_ground": "wide padded feet imprinting the snow",
                "facade_palette": "white fur-pile, warm amber porthole light, blue-tinted snow shadows",
                "roof_form": "gentle dome canopy with rainwater/snowmelt channel",
                "roof_material": "insulated bio-composite dome"
            },
            {
                "id": "nomadic_dacha_desert_pilgrim",
                "label": "Desert Pilgrim",
                "story": (
                    "Oasis-to-oasis migration across rewilded North African and Arabian "
                    "deserts. Tall slender legs for sand-dune crossings. Broad overhanging "
                    "solar canopy extending well beyond the body for shade. Ochre adobe-"
                    "textured bio-composite skin."
                ),
                "color": "#C9956B",
                "min_floors": 1, "max_floors": 1,
                "suggested_floor_height": 3.2, "suggested_area_sqm": 130,
                "prompt": (
                    "A small architectural walking dwelling on six tall slender robotic legs "
                    "(5m tall) crossing golden desert dunes at sunset. Warm ochre adobe-"
                    "textured bio-composite exterior skin. Broad overhanging dark photovoltaic "
                    "canopy extending well beyond the footprint for shade. A small arched "
                    "doorway. Long shadow trails behind. Distant silhouette of a camel caravan. "
                    "Orange-pink sky, dust suspended in the air. Photorealistic, warm evening "
                    "light, atmospheric."
                ),
                "facade_primary": "warm ochre adobe-textured bio-composite skin",
                "facade_secondary": "titanium tall-stance legs with wide sand-pads",
                "facade_ground": "sand-pad footprints in dune crest",
                "facade_palette": "ochre adobe, warm sandy dunes, dark solar canopy, orange-pink sky",
                "roof_form": "very broad overhanging photovoltaic canopy for shade",
                "roof_material": "photovoltaic array with water-capture rails"
            }
        ]
    },

    # ═══════════════════════════════════════════════════════════════════════
    # OPENSPACES (4)
    # ═══════════════════════════════════════════════════════════════════════
    {
        "kind": "openspaces",
        "slug": "experimental-tidal-cathedral-park",
        "id": "experimental_tidal_cathedral_park",
        "title": "Tidal Cathedral Park",
        "subcategory": "Experimental",
        "aesthetic_category": "experimental",
        "space_type": "park",
        "description": (
            "A former drowned neighbourhood intentionally re-flooded twice daily by controlled "
            "tides. Submerged streets and piazzas emerge at low tide; stepped amphitheatres "
            "stand partially underwater; bioluminescent seagrass grows where there were once "
            "streets. An urban memorial that is also an active wetland and an inhabitable ruin "
            "— the city learning to love its own drowned form."
        ),
        "tags": ["experimental", "tidal", "climate-adaptation", "wetland", "ruin", "memorial"],
        "hero_prompt": (
            "A Tidal Cathedral Park at mid-tide — a former drowned neighbourhood with stone "
            "piazzas and stepped amphitheatres half-underwater in clear salt water, "
            "bioluminescent seagrass glowing faintly green in the submerged streets. Worn "
            "stone building fronts still standing, now colonised by algae and small coral. "
            "Visitors on boardwalks and small boats. Soft overcast sky. Photorealistic, "
            "atmospheric, serene and slightly melancholy."
        ),
        "suggested_width_m": 150,
        "suggested_depth_m": 150,
        "suggested_area_sqm": 22500,
        "variants": [
            {
                "id": "tidal_park_venetian_resurrection",
                "label": "Venetian Resurrection",
                "story": (
                    "Mediterranean canal-city lineage. Stepped stone piazzas emerge at low "
                    "tide; fragments of palazzi rise like small islands. Active fish and "
                    "mollusc nurseries in the flooded streets. The city that always knew "
                    "this was coming."
                ),
                "color": "#7A8B95",
                "prompt": (
                    "A Mediterranean canal-city at mid-tide — stepped stone piazzas and "
                    "palazzi fragments half-submerged in clear blue-green salt water. "
                    "Remnant stone balconies and arched windows still standing, colonised "
                    "by algae and small coral. Bioluminescent seagrass faintly visible in "
                    "submerged streets. Small electric boats weaving between the ruins. "
                    "Soft overcast afternoon. Serene, melancholy, beautiful."
                )
            },
            {
                "id": "tidal_park_bangladesh_delta",
                "label": "Bangladesh Delta Reshore",
                "story": (
                    "River delta typology. Stilted timber pavilions rise above the flooded "
                    "plain; floating markets assemble at high tide. Re-established fishing "
                    "villages atop the drowned older settlements. Adaptation as continuity."
                ),
                "color": "#8B6B4A",
                "prompt": (
                    "A Bangladeshi delta urban-park at high tide — stilted timber "
                    "pavilions rise above the flooded plain, connected by narrow wooden "
                    "bridges. A floating market of small brightly-painted boats gathered "
                    "between them. Mangroves in the background. Warm late-afternoon tropical "
                    "light. Vivid, vibrant, living adaptation."
                )
            },
            {
                "id": "tidal_park_manhattan_flood",
                "label": "Manhattan Flood Park",
                "story": (
                    "Post-flood Manhattan — subway tunnels are now coral-lined grottos; "
                    "avenue amphitheatres host low-tide gatherings. The street grid "
                    "preserved as a tidal pattern. Skyline still standing, feet wet."
                ),
                "color": "#6B6B78",
                "prompt": (
                    "A post-flood Manhattan park at low tide — Manhattan-scale streets "
                    "and subway-entry amphitheatres half-submerged in cloudy green salt "
                    "water. Still-standing mid-rise buildings at the edge, their lower "
                    "floors coral-encrusted. Visitors walking on exposed stone avenues. "
                    "Overcast sky. Elegaic, sublime. Photorealistic."
                )
            },
            {
                "id": "tidal_park_pacific_atoll",
                "label": "Pacific Atoll Coral Park",
                "story": (
                    "Engineered coral colonies grown over former Pacific-island settlements. "
                    "The coral is the architecture; the old paths are now reef channels. "
                    "Swimmers, snorkellers, and fish share the plaza-reefs."
                ),
                "color": "#E8A89A",
                "prompt": (
                    "A Pacific atoll coral-park at low tide — engineered coral colonies "
                    "grown over the foundations of a former small Pacific-island settlement. "
                    "Pink and orange coral structures replace walls; turquoise reef "
                    "channels replace streets. A few visitors snorkelling. Bright clear "
                    "tropical light, vivid colours. Photorealistic, vibrant."
                )
            }
        ]
    },
    {
        "kind": "openspaces",
        "slug": "experimental-echo-garden",
        "id": "experimental_echo_garden",
        "title": "Echo Garden",
        "subcategory": "Experimental",
        "aesthetic_category": "experimental",
        "space_type": "plaza",
        "description": (
            "A circular plaza where speech is captured, slowed, and played back across weeks "
            "via acoustic architecture — directional panels, silence wells, cross-fade zones. "
            "Your voice becomes tomorrow's context, and the garden itself is a slow-motion "
            "public discourse. A civic resource for a society that wants to listen more "
            "slowly than it speaks."
        ),
        "tags": ["experimental", "acoustic", "time-shifted", "civic", "contemplative", "discourse"],
        "hero_prompt": (
            "A circular open-air Echo Garden plaza at dusk — a shallow bowl of light "
            "sandstone paving with concentric sound-directing panels, a central silence "
            "well, and a few low benches. A few visitors scattered, some speaking into the "
            "panels, some listening. Soft warm lanterns at the rim. Clear sky with first "
            "stars. Photorealistic, contemplative, hushed atmospheric."
        ),
        "suggested_width_m": 80,
        "suggested_depth_m": 80,
        "suggested_area_sqm": 5000,
        "variants": [
            {
                "id": "echo_garden_zen_gravel",
                "label": "Zen Gravel Echo",
                "story": (
                    "Japanese-influenced — raked gravel around concentric timber acoustic "
                    "panels; a single stone silence well at the centre. Minimalist voice-"
                    "listening. Three benches for the three kinds of thought."
                ),
                "color": "#D6CCB6",
                "prompt": (
                    "A Zen-style minimalist Echo Garden — raked pale gravel circles around "
                    "dark timber acoustic panels arranged concentrically, with a single "
                    "stone well at the centre. Three low timber benches. Surrounded by a "
                    "few black pines. Soft morning light, deep shadows. Atmospheric, "
                    "serene, intentional."
                )
            },
            {
                "id": "echo_garden_islamic_courtyard",
                "label": "Islamic Courtyard Echo",
                "story": (
                    "Muqarnas-inspired acoustic niches in the rim walls; a central fountain "
                    "that cross-fades the previous week's voices into water-sound. Tiled in "
                    "deep blue and cream. Seating along the arcades."
                ),
                "color": "#2A4D8F",
                "prompt": (
                    "An Islamic courtyard Echo Garden — a square walled plaza with deep "
                    "blue and cream ceramic-tiled walls. Muqarnas-inspired geometric "
                    "acoustic niches recessed into the rim walls. Central octagonal fountain "
                    "with slow-flowing water. Palm trees at the corners. Arched arcade "
                    "seating. Late-afternoon warm light. Photorealistic, richly detailed."
                )
            },
            {
                "id": "echo_garden_celtic_stone",
                "label": "Celtic Standing Stone Echo",
                "story": (
                    "Megalithic precedent — standing stones arranged as primary acoustic "
                    "resonators, with engraved grooves directing sound. Moss and wildflowers "
                    "in the interstices. Pre-modern technology meets post-modern acoustics."
                ),
                "color": "#6B7560",
                "prompt": (
                    "A Celtic-standing-stone-inspired Echo Garden — a circle of 12 tall "
                    "weathered grey standing stones, 3-4 meters high, engraved with flowing "
                    "groove patterns. Moss and wildflowers in the interstices and at the "
                    "bases. A single low stone bench at the centre. Grey Atlantic sky and "
                    "wind-bent grass around. Atmospheric, ancient-future, mossy textures."
                )
            },
            {
                "id": "echo_garden_modernist_plaza",
                "label": "Modernist Parametric Plaza",
                "story": (
                    "Clean concrete + parametric sound panels — the contemporary "
                    "articulation. Brutalist-adjacent sculptural form, with warm inlaid "
                    "timber handholds at listening stations."
                ),
                "color": "#A8A6A1",
                "prompt": (
                    "A modernist parametric Echo Garden plaza — clean board-formed concrete "
                    "floor with a cluster of tall parametric acoustic panels arranged in "
                    "sculptural curves. Warm timber insets at listener handholds. A few "
                    "minimalist benches. Contemporary architectural lighting. Late-afternoon "
                    "soft sun. Brutalist-adjacent, sculptural, serene."
                )
            }
        ]
    },
    {
        "kind": "openspaces",
        "slug": "experimental-pollinator-cathedral",
        "id": "experimental_pollinator_cathedral",
        "title": "Pollinator Cathedral",
        "subcategory": "Experimental",
        "aesthetic_category": "experimental",
        "space_type": "park",
        "description": (
            "A 200-meter vertical wildflower supercluster engineered as monument-scale "
            "habitat for the last 3,000 native pollinator species. Humans access via cable-"
            "stayed catwalks between lantern-pods. Sacred and ecological in equal measure — "
            "part cathedral, part living Noah's ark for the insects that built agriculture."
        ),
        "tags": ["experimental", "multispecies", "pollinator", "vertical-habitat", "sacred", "ecological"],
        "hero_prompt": (
            "A 200-meter-tall Pollinator Cathedral — a vertical wildflower supercluster "
            "like a slender architectural tower but entirely alive, covered in millions "
            "of blooming wildflowers in pink, purple, yellow, and white. Thin cable-stayed "
            "catwalks with human figures crossing between small glass lantern-pods at "
            "various heights. Clouds of bees and butterflies in the air around the "
            "structure. Late-afternoon golden light. Photorealistic, sublime, "
            "cathedral-scale wildlife habitat."
        ),
        "suggested_width_m": 40,
        "suggested_depth_m": 40,
        "suggested_area_sqm": 1600,
        "variants": [
            {
                "id": "pollinator_tropical_orchid",
                "label": "Tropical Orchid Tower",
                "story": (
                    "Tropical orchid and hummingbird variant — pink, magenta, and violet "
                    "orchids cover the structure. Hummingbirds and nectar-moths abound. "
                    "Humid air. Golden-hour shafts of light."
                ),
                "color": "#C04A8A",
                "prompt": (
                    "A 180-meter Pollinator Cathedral in a tropical setting, covered in "
                    "cascading pink, magenta, and violet orchids. Hummingbirds in flight "
                    "around it. Humid air, soft shafts of golden-hour sunlight. Cable "
                    "catwalks visible faintly between lantern-pods. Lush, vibrant, sacred."
                )
            },
            {
                "id": "pollinator_prairie_sunflower",
                "label": "Prairie Sunflower Stack",
                "story": (
                    "Great-Plains heritage — golden yellow sunflowers and goldenrods cover "
                    "the tower. Monarch butterflies and native bees. Late-summer warmth."
                ),
                "color": "#D8A82A",
                "prompt": (
                    "A 180-meter Pollinator Cathedral in a prairie setting, entirely covered "
                    "in golden yellow sunflowers, goldenrod, and coneflowers. Monarch "
                    "butterflies and large native bees swarming around. Warm blue sky, low "
                    "late-summer sun casting long shadows across wild grassland at the base. "
                    "Vibrant, sun-drenched, sacred."
                )
            },
            {
                "id": "pollinator_alpine_wildflower",
                "label": "Alpine Wildflower Spire",
                "story": (
                    "High-elevation variant — alpine wildflowers (gentians, alpine asters, "
                    "edelweiss) and alpine moths. Thin clear cold air. Snow-capped peaks "
                    "behind. Silver-green palette."
                ),
                "color": "#6E8A8C",
                "prompt": (
                    "A 150-meter Pollinator Cathedral in a high-alpine setting, covered in "
                    "small silver-green alpine wildflowers — gentians, asters, edelweiss. "
                    "Snow-capped mountain peaks behind. Thin cold clear air, intense high-"
                    "altitude sun. Alpine moths and bees in the air. Crisp, sharp, serene."
                )
            },
            {
                "id": "pollinator_mediterranean_lavender",
                "label": "Mediterranean Lavender Obelisk",
                "story": (
                    "Dry-climate lavender, rosemary, and thyme variant. Silver-green and "
                    "purple foliage. Honeybees and wild solitary bees. Fragrant in the heat. "
                    "Olive trees at the base."
                ),
                "color": "#8A7EB8",
                "prompt": (
                    "A 160-meter Pollinator Cathedral in a Mediterranean setting, covered "
                    "in silver-purple lavender, rosemary, and thyme. Honeybees swarming. "
                    "Olive trees scattered at the base. Warm dry late-afternoon light, deep "
                    "shadows. Fragrant, dusty, sacred."
                )
            }
        ]
    },
    {
        "kind": "openspaces",
        "slug": "experimental-slow-park",
        "id": "experimental_slow_park",
        "title": "Slow Park",
        "subcategory": "Experimental",
        "aesthetic_category": "experimental",
        "space_type": "park",
        "description": (
            "A park where time deliberately runs at 1/10 speed for visitors — via deep "
            "meditative programming, acoustic isolation, and carefully curated attention "
            "fields. No clocks, phones, or photos. Entering requires a 30-minute transition. "
            "The civic library of slowness, meant for grief, deep thought, and major life "
            "decisions. A public resource as essential as clean water."
        ),
        "tags": ["experimental", "contemplative", "time", "meditation", "grief", "slow"],
        "hero_prompt": (
            "A Slow Park at soft dawn — a wide open contemplative space with a single "
            "ancient tree, a shallow reflecting pool, a stone bench, and absolute silence. "
            "Soft pink-grey pre-dawn light. A single still figure sitting on the bench. "
            "Mist clinging to the water. No clocks, no signage, nothing urgent. "
            "Photorealistic, deeply still, contemplative, held."
        ),
        "suggested_width_m": 100,
        "suggested_depth_m": 100,
        "suggested_area_sqm": 10000,
        "variants": [
            {
                "id": "slow_park_japanese_moss",
                "label": "Japanese Moss Garden",
                "story": (
                    "Moss carpets across soft undulating ground, a few thoughtful stones, "
                    "a single stone basin. The slowness of moss, felt as architecture."
                ),
                "color": "#6A8A5E",
                "prompt": (
                    "A Japanese moss-garden Slow Park — soft undulating moss-covered ground "
                    "with a few thoughtful stones, a single stone water basin dripping "
                    "slowly. Dappled filtered light through old pines. A single stone path "
                    "winding through. Soft, muted, slow."
                )
            },
            {
                "id": "slow_park_monastic_cloister",
                "label": "European Monastic Cloister",
                "story": (
                    "Walled stone herb garden, a central well, low clipped lavender, a "
                    "covered arcade walk. The monastic tradition as civic resource."
                ),
                "color": "#C9B896",
                "prompt": (
                    "A European monastic-cloister Slow Park — a walled pale stone herb "
                    "garden with a central well, low clipped lavender beds, a surrounding "
                    "arcade walk with worn stone columns. Late-afternoon golden light. Warm, "
                    "lived-in, sacred. Photorealistic, atmospheric."
                )
            },
            {
                "id": "slow_park_rainforest_cathedral",
                "label": "Rainforest Cathedral",
                "story": (
                    "Under giant canopy trees, filtered light, tree-ferns, a single "
                    "rain-pool. The pre-agricultural forest as contemplative chamber."
                ),
                "color": "#2E4D32",
                "prompt": (
                    "A rainforest-cathedral Slow Park — under the canopy of giant old-growth "
                    "trees, a misty green space with tall tree-ferns and a single still "
                    "rain-pool reflecting the canopy above. Soft shafts of green-filtered "
                    "light. Vast, silent, primeval."
                )
            },
            {
                "id": "slow_park_prairie_stillness",
                "label": "Prairie Stillness",
                "story": (
                    "Wide open prairie grasses under a vast sky, wind the only sound, a "
                    "single bench facing the horizon. Slowness of vast space."
                ),
                "color": "#B8AA82",
                "prompt": (
                    "A prairie-stillness Slow Park — wide open tall-grass prairie under a "
                    "vast pale sky. A single weathered timber bench facing the horizon. "
                    "Wind bending the grasses. Late-afternoon soft gold light. Vast, silent, "
                    "stilling."
                )
            }
        ]
    },

    # ═══════════════════════════════════════════════════════════════════════
    # STREETS (4)
    # ═══════════════════════════════════════════════════════════════════════
    {
        "kind": "streets",
        "slug": "experimental-ring-aqueduct",
        "id": "experimental_ring_aqueduct",
        "title": "Ring Aqueduct",
        "subcategory": "Experimental",
        "aesthetic_category": "experimental",
        "description": (
            "A canal-street hybrid — a 20m-wide ring channel circulating the city's "
            "stormwater and greywater in a slow civic loop, with pedestrian paths both "
            "sides and crossings every 100m. Water is simultaneously the infrastructure, "
            "the transportation medium (small electric boats), and the civic spine. "
            "Blue-green infrastructure at urban scale."
        ),
        "tags": ["experimental", "canal", "water-infrastructure", "transit", "blue-green"],
        "hero_prompt": (
            "A Ring Aqueduct street corridor at dusk — a 20-meter-wide slow-flowing canal "
            "ring with pale stone pedestrian walks on both sides, small electric boats "
            "drifting along, arched stone bridges every few hundred meters. Continuous "
            "row of elegant 4-6 storey buildings on both sides. Gas-lantern-style warm "
            "lights beginning to glow. Late twilight, water reflections. Photorealistic, "
            "atmospheric, timeless."
        ),
        "suggested_width_m": 40,
        "variants": [
            {
                "id": "ring_aqueduct_venetian",
                "label": "Venetian Canal Ring",
                "story": (
                    "Mediterranean canal-city lineage — pale stone palazzi on both sides, "
                    "arched bridges, a slower-flowing turquoise canal. The classical "
                    "reference model."
                ),
                "color": "#94A8B3",
                "prompt": (
                    "A Venetian-style Ring Aqueduct corridor at golden-hour — a 20-meter-wide "
                    "turquoise canal with pale stone palazzo fronts on both sides, narrow "
                    "stone pedestrian walks, an arched stone bridge mid-frame, small "
                    "wooden and electric boats drifting. Late-afternoon golden light, "
                    "warm reflections. Photorealistic, warm, timeless."
                )
            },
            {
                "id": "ring_aqueduct_scandinavian",
                "label": "Scandinavian Timber Ring",
                "story": (
                    "Fjord-inflected — dark timber and pale steel architecture, a colder "
                    "deeper canal, timber-decked walks, minimalist arched bridges."
                ),
                "color": "#3A4E5A",
                "prompt": (
                    "A Scandinavian-style Ring Aqueduct corridor at mid-morning overcast — "
                    "a dark deep canal with dark-stained timber and pale steel 5-storey "
                    "buildings on both sides, timber-decked pedestrian walks, a minimalist "
                    "steel arched bridge. Clean, restrained, atmospheric. Photorealistic."
                )
            },
            {
                "id": "ring_aqueduct_tropical_mangrove",
                "label": "Tropical Mangrove Ring",
                "story": (
                    "Tropical city variant — wooden stilted pavilions and market sheds, "
                    "palm trees, a warmer brown-green canal, fishing-village vibe."
                ),
                "color": "#4A7058",
                "prompt": (
                    "A tropical mangrove-lined Ring Aqueduct corridor — a brown-green "
                    "canal with stilted timber pavilions and small market sheds on both "
                    "sides, palm trees, a small wooden fishing boat. Warm late-afternoon "
                    "light. Vibrant, lively, humid."
                )
            },
            {
                "id": "ring_aqueduct_polished_modern",
                "label": "Polished Ultra-Modern Ring",
                "story": (
                    "Ultra-contemporary variant — white ceramic + polished stainless steel "
                    "architecture, clear filtered water, minimalist architectural restraint. "
                    "The near-future aesthetic."
                ),
                "color": "#E8EDF0",
                "prompt": (
                    "A polished ultra-modern Ring Aqueduct corridor at noon — clear "
                    "filtered water in a white ceramic and polished stainless steel canal, "
                    "minimalist 6-storey buildings with glass curtain walls on both sides, "
                    "a single slender steel arched bridge. Bright clean daylight. "
                    "Restrained, pristine."
                )
            }
        ]
    },
    {
        "kind": "streets",
        "slug": "experimental-braided-transit-mesh",
        "id": "experimental_braided_transit_mesh",
        "title": "Braided Transit Mesh",
        "subcategory": "Experimental",
        "aesthetic_category": "experimental",
        "description": (
            "No more distinction between 'street' and 'transit.' A multi-layered ribbon of "
            "intertwined lanes — walking, cycling, transit pods, cargo drones, tree canopy — "
            "BRAID around each other vertically on a hyperboloid structure with transparent "
            "decks. A DNA-helix street. Stratified, legible, and beautiful to watch."
        ),
        "tags": ["experimental", "multi-modal", "stratified", "transparent", "hyperboloid"],
        "hero_prompt": (
            "A Braided Transit Mesh street corridor at mid-morning — a dramatic stratified "
            "ribbon of intertwined lanes ascending and braiding around each other — a "
            "transparent walking deck, a cycle lane below, a transit-pod channel, a cargo-"
            "drone lane, all wrapped in living tree-canopy infill. Small human figures "
            "and pods visible at multiple levels. Soft morning light. Photorealistic, "
            "architectural sci-fi infrastructure."
        ),
        "suggested_width_m": 30,
        "variants": [
            {
                "id": "braided_transit_tokyo_vertical",
                "label": "Tokyo Vertical Braid",
                "story": (
                    "Dense urban Tokyo-inspired variant — signage-heavy, transparent decks, "
                    "cyberpunk warmth, cargo drones weaving. The dense-city exemplar."
                ),
                "color": "#2A3450",
                "prompt": (
                    "A Tokyo-style Braided Transit Mesh corridor at early evening — dense "
                    "stratified transit ribbon with transparent decks, warm signage glowing, "
                    "cargo drones weaving between levels, cycle lane, pedestrian walk, "
                    "transit pods. Neon and lantern reflections. Cyberpunk-warm, dense, "
                    "vibrant. Photorealistic."
                )
            },
            {
                "id": "braided_transit_alpine_pass",
                "label": "Alpine Pass Braid",
                "story": (
                    "Mountain-pass variant — the braid is integrated into a sheer cliff face, "
                    "with viewing decks looking out across valleys. Transit as landscape "
                    "experience."
                ),
                "color": "#8B9AA8",
                "prompt": (
                    "An alpine-pass Braided Transit Mesh corridor — stratified transit "
                    "ribbon cantilevered out from a sheer granite cliff face, with "
                    "transparent viewing decks looking across a mountain valley. Small "
                    "transit pods and cyclists visible. Bright alpine light, vast landscape. "
                    "Sublime, atmospheric."
                )
            },
            {
                "id": "braided_transit_amazon_canopy",
                "label": "Amazon Canopy Braid",
                "story": (
                    "Tropical rainforest variant — the braided structure is vine-covered and "
                    "integrated with canopy-level vegetation, forming a living transit spine "
                    "through the forest. Wildlife uses the lower lanes."
                ),
                "color": "#2D5E3A",
                "prompt": (
                    "An Amazon-canopy Braided Transit Mesh corridor — a stratified transit "
                    "ribbon suspended at rainforest canopy level, covered in vines and "
                    "epiphytes. Transparent walking deck, cycle lane, transit-pod channel. "
                    "Monkeys visible in the vegetation. Misty humid forest. Lush, vibrant, "
                    "alive."
                )
            },
            {
                "id": "braided_transit_desert_ribbon",
                "label": "Desert Sun-Shade Ribbon",
                "story": (
                    "Hot desert variant — the upper lane is a perforated sun-shade canopy "
                    "that cools the lower pedestrian walks. Solar-positive infrastructure."
                ),
                "color": "#D9B989",
                "prompt": (
                    "A desert-setting Braided Transit Mesh corridor at midday — stratified "
                    "transit ribbon with a perforated white sun-shade canopy above casting "
                    "dappled cool shadows on the lower pedestrian and cycle lanes. Warm "
                    "sandy dunes on both sides. Crisp sharp shadows. Bright, hot, sculptural."
                )
            }
        ]
    },
    {
        "kind": "streets",
        "slug": "experimental-whispering-path",
        "id": "experimental_whispering_path",
        "title": "Whispering Path",
        "subcategory": "Experimental",
        "aesthetic_category": "experimental",
        "description": (
            "A narrow (3m) pedestrian street lined with sound-directional vegetation and "
            "bone-conducting handrails. Different segments play the voices of people who "
            "walked here in the past (opt-in, anonymised, ephemeral). The street as "
            "palimpsest of footsteps — walking the path is walking through time."
        ),
        "tags": ["experimental", "acoustic", "pedestrian", "memory", "palimpsest"],
        "hero_prompt": (
            "A narrow 3-meter Whispering Path corridor at soft dusk — a pedestrian path "
            "lined with softly-rustling directional vegetation, a long polished timber "
            "handrail running along one side, small warm floor-lanterns embedded in the "
            "stone paving. A single walking figure ahead. Hushed, intimate, atmospheric. "
            "Photorealistic, contemplative."
        ),
        "suggested_width_m": 3,
        "variants": [
            {
                "id": "whispering_path_forest_moss",
                "label": "Forest Moss Path",
                "story": (
                    "Through a moss-covered old-growth forest — directional ferns, moss-"
                    "covered handrails, birdsong layer. The most sacred of the Whispering "
                    "Paths."
                ),
                "color": "#3E5F3E",
                "prompt": (
                    "A Whispering Path through a moss-covered old-growth forest at soft "
                    "morning light — narrow stone path winding between massive moss-covered "
                    "tree trunks, moss-covered timber handrails. Deep green ferns lining "
                    "the edges. Filtered green light. Atmospheric, sacred, hushed."
                )
            },
            {
                "id": "whispering_path_urban_plaza",
                "label": "Urban Plaza Whisper",
                "story": (
                    "Through a dense urban centre — narrow path between tall flowering "
                    "trees, with building facades close on both sides, quiet in a way the "
                    "surrounding city is not."
                ),
                "color": "#8B8E6E",
                "prompt": (
                    "An urban Whispering Path corridor at late-afternoon — narrow 3m path "
                    "between tall flowering cherry trees, with 5-storey building facades "
                    "close on both sides, a polished handrail running along one side, "
                    "small warm lights embedded at the base. A few pedestrians walking. "
                    "Intimate, hushed in the city. Photorealistic."
                )
            },
            {
                "id": "whispering_path_desert_dune",
                "label": "Desert Dune Whisper",
                "story": (
                    "Through sand dunes — the path is sand-cradled with large acoustic "
                    "shells embedded at intervals, the voices carried on the wind. The "
                    "path of pilgrimage."
                ),
                "color": "#D4B082",
                "prompt": (
                    "A desert Whispering Path — a narrow sand path winding between tall "
                    "golden dunes, with large polished acoustic shells embedded at intervals "
                    "along the path. Warm late-afternoon sun. Long shadow. A single walker. "
                    "Sculptural, atmospheric, pilgrimage-like."
                )
            },
            {
                "id": "whispering_path_arctic_tundra",
                "label": "Arctic Tundra Whisper",
                "story": (
                    "Across Arctic tundra — a raised timber boardwalk with icy brass handrail, "
                    "the voices made crisper by the cold air. Long polar twilight walks."
                ),
                "color": "#B6C6D4",
                "prompt": (
                    "An Arctic Whispering Path — a raised weathered timber boardwalk with a "
                    "polished brass handrail extending across Arctic tundra in the long polar "
                    "twilight. Frost on the handrail. Distant mountains. Pale pink-purple sky. "
                    "Crisp, cold, contemplative."
                )
            }
        ]
    },
    {
        "kind": "streets",
        "slug": "experimental-thermal-belt",
        "id": "experimental_thermal_belt",
        "title": "Thermal Belt",
        "subcategory": "Experimental",
        "aesthetic_category": "experimental",
        "description": (
            "A street whose surface temperature and pattern actively reconfigure — dark "
            "carbon-capture tarmac in winter, white solar-reflective crystalline surface "
            "in summer, softening where pedestrians gather, hardening for cargo. Smart-"
            "material urban infrastructure. The pavement as climate device."
        ),
        "tags": ["experimental", "responsive", "smart-material", "climate-adaptive", "pavement"],
        "hero_prompt": (
            "A Thermal Belt street corridor — the pavement surface shows a visible pattern "
            "of morphing regions: dark carbon-capture areas, white cool-reflective areas, "
            "soft textured pedestrian zones, all flowing into each other in a subtle "
            "gradient. Buildings of various styles on both sides. Mid-day sun. Photorealistic, "
            "technical-yet-elegant."
        ),
        "suggested_width_m": 20,
        "variants": [
            {
                "id": "thermal_belt_saharan_daylight",
                "label": "Saharan Daylight Belt",
                "story": (
                    "Hot-climate full-summer mode — white crystalline reflective surface "
                    "cooling the street, mirror-like in patches. For the hottest days."
                ),
                "color": "#EDE8DE",
                "prompt": (
                    "A Thermal Belt street in full summer Saharan setting — the street "
                    "surface is white crystalline with mirror-like reflective patches "
                    "casting scattered bright reflections. Sand-coloured 4-storey "
                    "buildings on both sides. Harsh overhead sunlight, crisp shadows. "
                    "Hot, sculptural."
                )
            },
            {
                "id": "thermal_belt_nordic_night",
                "label": "Nordic Night Belt",
                "story": (
                    "Cold-climate winter mode — dark radiant-heated surface glowing faintly "
                    "warm, patches of melted clear through the frost. Winter-long darkness."
                ),
                "color": "#2A2A3A",
                "prompt": (
                    "A Thermal Belt street in a Nordic winter night setting — the street "
                    "surface is dark with warm radiant-heating zones glowing faintly orange, "
                    "patches of melted stone clear through the surrounding frost. Snow on "
                    "the rooftops of dark timber buildings. Warm amber street lanterns. "
                    "Atmospheric, cosy-cold."
                )
            },
            {
                "id": "thermal_belt_tropical_humid",
                "label": "Tropical Humid Belt",
                "story": (
                    "Tropical variant — perforated blue-green surface that 'breathes,' "
                    "venting humid air and releasing cooling mist in the shade-zones."
                ),
                "color": "#4A7076",
                "prompt": (
                    "A Thermal Belt street in a tropical-humid city — the street surface "
                    "is perforated blue-green, 'breathing' with faint cooling mist rising "
                    "from shade-zones. Palm trees, tropical 4-storey buildings on both "
                    "sides. Warm late-afternoon light. Vibrant, humid."
                )
            },
            {
                "id": "thermal_belt_himalayan",
                "label": "Himalayan Permafrost Belt",
                "story": (
                    "High-altitude cold-adaptive variant — thick insulating white surface, "
                    "radiant-heated paths, snow around the edges."
                ),
                "color": "#D9E2E8",
                "prompt": (
                    "A Thermal Belt street in a Himalayan high-altitude setting — thick "
                    "insulating white pavement with radiant-heated clear paths, snow "
                    "banked on the edges. Stone buildings with prayer flags. Sharp alpine "
                    "light, distant peaks. Crisp, pristine, atmospheric."
                )
            }
        ]
    },
]


# ---------------------------------------------------------------------------
# Gemini image generation
# ---------------------------------------------------------------------------


def generate_image(prompt: str, retries: int = 2) -> bytes | None:
    """Generate a single image via Gemini 3.1 Flash Image Preview."""
    full_prompt = prompt + STYLE_SUFFIX
    payload = {
        "contents": [{"role": "user", "parts": [{"text": full_prompt}]}],
        "generationConfig": {
            "responseModalities": ["TEXT", "IMAGE"],
            "temperature": 0.7,  # higher for creative variation
        },
    }
    url = gemini_url()

    for attempt in range(retries + 1):
        try:
            resp = httpx.post(url, json=payload,
                              headers={"Content-Type": "application/json"}, timeout=180.0)
        except httpx.TimeoutException:
            print(f"    TIMEOUT (attempt {attempt + 1})")
            if attempt < retries:
                time.sleep(5)
                continue
            return None

        if resp.status_code == 429:
            print(f"    RATE LIMITED — waiting 30s (attempt {attempt + 1})")
            time.sleep(30)
            continue

        if resp.status_code != 200:
            print(f"    HTTP {resp.status_code}: {resp.text[:200]}")
            if attempt < retries:
                time.sleep(5)
                continue
            return None

        data = resp.json()
        for candidate in data.get("candidates", []):
            for part in candidate.get("content", {}).get("parts", []):
                inline = part.get("inlineData") or part.get("inline_data")
                if inline and inline.get("data"):
                    return base64.b64decode(inline["data"])

        print(f"    no image in response (attempt {attempt + 1})")
        if attempt < retries:
            time.sleep(5)
            continue

    return None


# ---------------------------------------------------------------------------
# Image generation per archetype
# ---------------------------------------------------------------------------


def generate_archetype_images(arch: dict) -> bool:
    """Generate hero + 4 variant PNGs for an archetype. Returns True if all succeeded."""
    folder = PUBLIC / arch["kind"] / arch["slug"]
    folder.mkdir(parents=True, exist_ok=True)

    # Hero
    hero_path = folder / "hero.png"
    if not hero_path.exists():
        print(f"  hero.png ...", end=" ", flush=True)
        img = generate_image(arch["hero_prompt"])
        if not img:
            print("FAILED")
            return False
        hero_path.write_bytes(img)
        print(f"OK ({len(img)//1024} KB)")
        time.sleep(2)
    else:
        print(f"  hero.png  (already exists, skip)")

    # Variants
    for i, v in enumerate(arch["variants"]):
        variant_path = folder / f"variant_{i}.png"
        if variant_path.exists():
            print(f"  variant_{i}.png ({v['label']!r})  (already exists, skip)")
            continue
        print(f"  variant_{i}.png ({v['label']!r}) ...", end=" ", flush=True)
        img = generate_image(v["prompt"])
        if not img:
            print("FAILED")
            return False
        variant_path.write_bytes(img)
        print(f"OK ({len(img)//1024} KB)")
        time.sleep(2)

    return True


# ---------------------------------------------------------------------------
# Catalog JSON entry builders
# ---------------------------------------------------------------------------


def build_building_entry(arch: dict) -> dict:
    return {
        "id": arch["id"],
        "title": arch["title"],
        "buildingSubcategory": arch["subcategory"],
        "developmentType": arch["development_type"],
        "aestheticCategory": arch["aesthetic_category"],
        "description": arch["description"],
        "generationTags": arch["tags"],
        "styleProfile": arch["style_profile"],
        "prompt": arch["prompt_block"],
        "suggestedWidth_m": arch["suggested_width_m"],
        "suggestedDepth_m": arch["suggested_depth_m"],
        "minFloors": arch["min_floors"],
        "maxFloors": arch["max_floors"],
        "thumbnailUrl": f"/archetypes/buildings/{arch['slug']}/hero.png",
        "variants": [
            {
                "id": v["id"],
                "label": v["label"],
                "description": v["story"],
                "thumbnailUrl": f"/archetypes/buildings/{arch['slug']}/variant_{i}.png",
                "color": v["color"],
                "minFloors": v["min_floors"],
                "maxFloors": v["max_floors"],
                "suggestedFloorHeight": v["suggested_floor_height"],
                "suggestedAreaSqm": v["suggested_area_sqm"],
                "facadeDetail": {
                    "primaryMaterial": v["facade_primary"],
                    "secondaryMaterial": v["facade_secondary"],
                    "groundFloor": v["facade_ground"],
                    "colorScheme": v["facade_palette"],
                },
                "roofDetail": {
                    "form": v["roof_form"],
                    "material": v["roof_material"],
                },
            }
            for i, v in enumerate(arch["variants"])
        ],
    }


def build_openspace_entry(arch: dict) -> dict:
    return {
        "id": arch["id"],
        "title": arch["title"],
        "spaceType": arch["space_type"],
        "aestheticCategory": arch["aesthetic_category"],
        "buildingSubcategory": arch["subcategory"],
        "description": arch["description"],
        "generationTags": arch["tags"],
        "suggestedWidth_m": arch["suggested_width_m"],
        "suggestedDepth_m": arch["suggested_depth_m"],
        "suggestedAreaSqm": arch["suggested_area_sqm"],
        "thumbnailUrl": f"/archetypes/openspaces/{arch['slug']}/hero.png",
        "shape": "rectangular",
        "variants": [
            {
                "id": v["id"],
                "label": v["label"],
                "description": v["story"],
                "thumbnailUrl": f"/archetypes/openspaces/{arch['slug']}/variant_{i}.png",
                "color": v["color"],
            }
            for i, v in enumerate(arch["variants"])
        ],
    }


def build_street_entry(arch: dict) -> dict:
    return {
        "id": arch["id"],
        "title": arch["title"],
        "aestheticCategory": arch["aesthetic_category"],
        "buildingSubcategory": arch["subcategory"],
        "description": arch["description"],
        "generationTags": arch["tags"],
        "typicalWidth_m": arch["suggested_width_m"],
        "laneCount": 2,
        "hasSidewalk": True,
        "shape": "linear",
        "thumbnailUrl": f"/archetypes/streets/{arch['slug']}/hero.png",
        "variants": [
            {
                "id": v["id"],
                "label": v["label"],
                "description": v["story"],
                "thumbnailUrl": f"/archetypes/streets/{arch['slug']}/variant_{i}.png",
                "color": v["color"],
            }
            for i, v in enumerate(arch["variants"])
        ],
    }


def archetype_already_in_catalog(catalog_path: Path, arch_id: str) -> bool:
    text = catalog_path.read_text(encoding="utf-8")
    return f'"id": "{arch_id}"' in text


def splice_into_catalog(catalog_path: Path, new_entry: dict) -> None:
    """Text-level splice — insert new_entry before the closing `]` of archetypes array.
    Skips if archetype ID already exists in the catalog (idempotent re-runs)."""
    if archetype_already_in_catalog(catalog_path, new_entry["id"]):
        return  # already present, don't double-insert

    text = catalog_path.read_text(encoding="utf-8")
    close = text.rfind("]")
    if close < 0:
        raise RuntimeError(f"No closing ] in {catalog_path}")

    # Walk back to last `}` before `]`
    insertion_point = close
    while insertion_point > 0 and text[insertion_point - 1] in " \t\r\n":
        insertion_point -= 1

    raw = json.dumps(new_entry, indent=4, ensure_ascii=False)
    # Re-indent to match the file's 8-space indent for archetype entries
    lines = raw.split("\n")
    indented = lines[0] + "\n" + "\n".join("    " + line for line in lines[1:])
    new_text = text[:insertion_point] + ",\n    " + indented + "\n  " + text[close:]

    # Validate by parsing
    parsed = json.loads(new_text)
    catalog_path.write_text(new_text, encoding="utf-8")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    limit = None
    dry_run = False
    for a in sys.argv[1:]:
        if a.startswith("--limit="):
            limit = int(a.split("=", 1)[1])
        elif a == "--dry-run":
            dry_run = True
        elif a in ("-h", "--help"):
            print(__doc__)
            sys.exit(0)

    targets = ARCHETYPES[:limit] if limit else ARCHETYPES
    print(f"Processing {len(targets)} archetype(s){' (DRY RUN)' if dry_run else ''}")
    print()

    if dry_run:
        for arch in targets:
            print(f"  [{arch['kind']}] {arch['id']}  ({arch['title']}, {len(arch['variants'])} variants)")
        return 0

    # Backup catalogs
    backups = {}
    for kind, path in CATALOGS.items():
        bak = path.with_suffix(path.suffix + ".bak-exp")
        bak.write_bytes(path.read_bytes())
        backups[kind] = bak
        print(f"Backup: {bak.name}")
    print()

    successes = 0
    for i, arch in enumerate(targets, 1):
        print(f"[{i}/{len(targets)}] {arch['id']}  ({arch['title']})")
        ok = generate_archetype_images(arch)
        if not ok:
            print(f"    IMAGES FAILED — skipping catalog splice for {arch['id']}")
            continue

        # Build + splice
        if arch["kind"] == "buildings":
            entry = build_building_entry(arch)
        elif arch["kind"] == "openspaces":
            entry = build_openspace_entry(arch)
        else:
            entry = build_street_entry(arch)

        try:
            already = archetype_already_in_catalog(CATALOGS[arch["kind"]], arch["id"])
            splice_into_catalog(CATALOGS[arch["kind"]], entry)
            tag = "already present in" if already else "spliced into"
            print(f"    [OK] {tag} {arch['kind']} catalog")
            successes += 1
        except Exception as e:
            print(f"    SPLICE FAILED: {e}")
            continue

    print()
    print(f"=== Done: {successes}/{len(targets)} archetypes completed ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
