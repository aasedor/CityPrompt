#!/usr/bin/env python3
"""
Generate 12 utopic speculative archetypes (4 buildings, 4 parks, 4 streets).

Where experimental archetypes respond to pressure (climate, extraction, deep-
time), utopic archetypes answer a different question: *what happens when
constraints dissolve and we design for flourishing?* Maximum biophilia,
Alexandrian pattern language, Keltner awe research, circadian science,
prospect-refuge theory, and the primal places human DNA was tuned to love.

Pipeline identical to generate_experimental_archetypes.py: generate hero +
4 variant PNGs via Gemini 3.1 Flash Image Preview, splice Tier-1 metadata
into the appropriate catalog JSON via text-level edits (idempotent on re-run).

Usage:
    python scripts/generate_utopic_archetypes.py --dry-run
    python scripts/generate_utopic_archetypes.py --limit=1
    python scripts/generate_utopic_archetypes.py
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
    return (
        f"https://generativelanguage.googleapis.com/v1beta/"
        f"models/{MODEL}:generateContent?key={load_gemini_key()}"
    )


STYLE_SUFFIX = (
    " Photorealistic architectural concept rendering. Cinematic lighting. "
    "Sharp material detail. Not illustration, not cartoon, not stylised — "
    "documentary photography of a real place in a 1000-year utopic future "
    "where humanity has solved its problems and designs purely for beauty, "
    "awe, and human flourishing. 8K detail, professional architectural "
    "photography, biophilic, serene."
)


# ---------------------------------------------------------------------------
# The 12 utopic archetypes
# ---------------------------------------------------------------------------

ARCHETYPES: list[dict[str, Any]] = [
    # ═══════════════════════════════════════════════════════════════════════
    # BUILDINGS (4)
    # ═══════════════════════════════════════════════════════════════════════
    {
        "kind": "buildings",
        "slug": "utopic-sunpath-pavilion",
        "id": "utopic_sunpath_pavilion",
        "title": "Sunpath Pavilion",
        "subcategory": "Utopic",
        "development_type": "residential_single_family",
        "aesthetic_category": "utopic_biophilic",
        "description": (
            "A family dwelling designed around the annual path of the sun. Each "
            "room has its sun hour; rotating living walls and adjustable screens "
            "follow the light through the seasons, so a family's daily rhythm is "
            "aligned with circadian science and the ancient human instinct to "
            "worship the sun. The house is a slow clock you live in — a gift to "
            "the nervous system that modern buildings have long forgotten how to "
            "give."
        ),
        "tags": ["utopic", "biophilic", "circadian", "solar", "contemplative", "single-family"],
        "style_profile": {
            "materials": ["natural timber", "pale stone", "operable shoji-like screens", "copper-roofed verandas", "lime-washed plaster"],
            "facadeRhythm": "Stepped screens and verandas oriented to the solar arc, opening and closing through the day",
            "roofForm": "Low overhanging roof calibrated to admit winter sun and block summer sun",
            "frontageType": "East-facing dawn entry + west-facing sunset veranda",
            "windowStyle": "Floor-to-ceiling operable screens; tall east windows for morning; low west windows for sunset",
            "massing": "Low-slung 1-2 storey pavilion, long in the east-west axis to maximise solar frontage",
            "heightTendency": "Low (1-2 storeys, typically 8m max)",
            "streetRelationship": "Private garden wall on street; solar frontage to the south",
            "renderingMood": "Serene, sun-drenched, reverent, timeless",
            "articulation": "Horizontal shadow lines trace the hour; the building reads as a slow sundial",
            "publicRealm": "Private south garden; shared east-west pedestrian paths between neighbouring pavilions"
        },
        "prompt_block": {
            "subject": "A family dwelling designed around the annual solar path",
            "details": [
                "Low 1-2 storey pavilion with long east-west axis",
                "Operable screens and verandas tracking the sun",
                "Materials: natural timber, pale stone, copper, lime-wash",
                "South-facing garden with fruit trees",
                "Stepped shadow lines calibrated to the hour"
            ]
        },
        "suggested_width_m": 20,
        "suggested_depth_m": 12,
        "min_floors": 1,
        "max_floors": 2,
        "hero_prompt": (
            "A Sunpath Pavilion family dwelling at golden hour — a low 1-2 storey "
            "home with a long east-west axis, operable timber screens on the "
            "south facade partially open to catch low afternoon sun. Pale "
            "natural stone base, warm timber upper walls, copper-edged low roof. "
            "A deep south-facing veranda with a family having tea. A garden of "
            "fruit trees and wildflowers in front. Long horizontal shadow lines "
            "trace the hour across the facade. Sun-drenched, serene, timeless."
        ),
        "variants": [
            {
                "id": "sunpath_japanese_shoji",
                "label": "Japanese Shoji Sun Pavilion",
                "story": (
                    "Japan. Traditional shoji screens enlarged to architectural "
                    "scale, tracking the sun on engineered silent runners. "
                    "Cypress timber, white paper, tatami. Family tea ceremony "
                    "aligns with the golden hour."
                ),
                "color": "#D6CFBE",
                "min_floors": 1, "max_floors": 2,
                "suggested_floor_height": 3.0, "suggested_area_sqm": 180,
                "prompt": (
                    "A Japanese Sunpath Pavilion family home at golden hour in a "
                    "mossy garden setting. Cypress timber post-and-beam frame "
                    "with large sliding shoji paper screens partially open on "
                    "the south facade, letting warm sun through as soft glowing "
                    "rectangles. Low-sloped cedar-shingle roof with deep "
                    "overhang. Engawa veranda with tatami. Stone basin. Pine "
                    "tree and maple in the garden. Serene, warm, contemplative."
                ),
                "facade_primary": "cypress timber post-and-beam frame",
                "facade_secondary": "large sliding shoji paper screens",
                "facade_ground": "stone plinth with engawa timber veranda",
                "facade_palette": "pale cypress, warm paper, dark cedar roof, mossy stone",
                "roof_form": "low-sloped cedar-shingle roof with deep overhang",
                "roof_material": "hand-split cedar shingles with copper gutters"
            },
            {
                "id": "sunpath_mediterranean_courtyard",
                "label": "Mediterranean Courtyard Sun House",
                "story": (
                    "Mediterranean coast. Whitewashed limestone walls enclose "
                    "a central courtyard; canvas awnings track the midday sun. "
                    "Fig tree shade, lemon tree scent, cicada soundscape. "
                    "Shuttered windows regulate the dialogue with heat."
                ),
                "color": "#F0ECE0",
                "min_floors": 1, "max_floors": 2,
                "suggested_floor_height": 3.3, "suggested_area_sqm": 220,
                "prompt": (
                    "A Mediterranean Sunpath courtyard home in late afternoon. "
                    "Whitewashed limestone walls enclosing a central courtyard "
                    "with a large fig tree providing dappled shade. Canvas "
                    "awnings (blue-striped) overhead on tracking runners. "
                    "Terracotta tile roof. Wooden shuttered windows partially "
                    "open. Lemon trees in clay pots. Stone paving with pattern. "
                    "Cicada-soundscape atmosphere. Warm golden sun."
                ),
                "facade_primary": "lime-washed limestone walls",
                "facade_secondary": "wooden shuttered windows with aged-green paint",
                "facade_ground": "stone-paved entry with low planters",
                "facade_palette": "whitewashed lime, weathered green shutters, terracotta tiles",
                "roof_form": "low-pitch terracotta tile roof with courtyard skylight",
                "roof_material": "hand-thrown terracotta roof tiles"
            },
            {
                "id": "sunpath_scandinavian_pine",
                "label": "Scandinavian Pine Sun Home",
                "story": (
                    "Northern Europe. Timber-framed house with oversized "
                    "southern windows to capture scarce winter sun; natural "
                    "wool-and-pine interior that glows amber in the long dusk. "
                    "Birch forest setting. Sauna wing at the back."
                ),
                "color": "#B89562",
                "min_floors": 1, "max_floors": 2,
                "suggested_floor_height": 3.1, "suggested_area_sqm": 200,
                "prompt": (
                    "A Scandinavian Sunpath pine home at low-angle winter sun, "
                    "set in a birch forest. Timber-framed with oversized "
                    "floor-to-ceiling south windows glowing warm amber with "
                    "interior firelight. Dark-stained pine cladding, pale "
                    "stone base. Snow on the ground. Smoke rising from a "
                    "chimney. A wood-burning sauna wing visible at the back. "
                    "Long blue-tinted shadows. Crisp, golden, cosy."
                ),
                "facade_primary": "dark-stained vertical pine cladding",
                "facade_secondary": "oversized floor-to-ceiling south-facing glass",
                "facade_ground": "pale granite base and weathered timber porch",
                "facade_palette": "dark pine, amber interior glow, pale granite, birch white",
                "roof_form": "low gabled roof with deep overhang and chimney",
                "roof_material": "standing-seam zinc roof with copper details"
            },
            {
                "id": "sunpath_himalayan_stone",
                "label": "Himalayan Stone-Roof Sun Dwelling",
                "story": (
                    "High Himalaya. Stacked-stone walls retain solar heat "
                    "overnight; earth-planted roof terraces catch the "
                    "mountain sun. Stone hearth central. Prayer flags at "
                    "ridge. Mountain views every direction."
                ),
                "color": "#8A7558",
                "min_floors": 1, "max_floors": 2,
                "suggested_floor_height": 2.8, "suggested_area_sqm": 160,
                "prompt": (
                    "A Himalayan Sunpath stone dwelling at clear high-altitude "
                    "golden hour. Stacked-stone walls in warm brown granite. "
                    "Earth-and-grass planted roof terraces catching the sun. "
                    "Small timber-framed windows with warm interior light. "
                    "Prayer flags on the ridge. Snow-capped peaks in the "
                    "distance. Clean crisp thin air. Deep shadows. Sacred, "
                    "weighty, peaceful."
                ),
                "facade_primary": "warm stacked-stone masonry (brown granite)",
                "facade_secondary": "small timber-framed windows with deep reveals",
                "facade_ground": "compacted earth forecourt with prayer flags",
                "facade_palette": "warm brown granite, timber, green earth-roof, prayer-flag colours",
                "roof_form": "flat earth-planted roof terraces with ridge flag-lines",
                "roof_material": "green-roof soil + wildflower meadow"
            }
        ]
    },
    {
        "kind": "buildings",
        "slug": "utopic-hearth-atrium",
        "id": "utopic_hearth_atrium",
        "title": "Hearth Atrium",
        "subcategory": "Utopic",
        "development_type": "residential_single_family",
        "aesthetic_category": "utopic_biophilic",
        "description": (
            "A family dwelling built around a great central hearth — the "
            "~200,000-year-old cognitive anchor our species grew up around — "
            "with a crystal-glass oculus opening directly to the sky above. "
            "Daily life revolves around fire and sky: cooking, story-telling, "
            "mourning, stargazing, all in one room. Ancient ritual preserved "
            "with modern care. The house IS the hearth."
        ),
        "tags": ["utopic", "biophilic", "hearth", "ancient", "ritual", "sky-oculus", "single-family"],
        "style_profile": {
            "materials": ["handmade brick or stone", "carved timber beams", "lime-plaster walls", "crystal-glass oculus", "woven textiles"],
            "facadeRhythm": "Inward-focused — the primary architecture is the central atrium, not the facade",
            "roofForm": "Cone or pyramid with central circular oculus to the sky",
            "frontageType": "Modest entry threshold into a dramatic central hearth-atrium",
            "windowStyle": "Small hand-cut windows at human height; the oculus is the primary light source",
            "massing": "Compact square or circular plan, 1-2 storey ring wrapping the hearth",
            "heightTendency": "Low (1-2 storeys, with 8-12m ceiling over the hearth)",
            "streetRelationship": "Understated exterior; the magic is inside",
            "renderingMood": "Warm, ancient, sacred — a cave with a hole to heaven",
            "articulation": "Facade quiet; interior atrium soars",
            "publicRealm": "Cluster of homes share an outdoor common fire-pit between their private hearths"
        },
        "prompt_block": {
            "subject": "A family dwelling built around a great central hearth and sky oculus",
            "details": [
                "Compact square or circular plan wrapping a central atrium",
                "Central hearth (open fire or ember brazier)",
                "Crystal-glass oculus directly above, opening to the sky",
                "Ring of rooms around the hearth",
                "Warm handmade materials (brick, timber, plaster)"
            ]
        },
        "suggested_width_m": 18,
        "suggested_depth_m": 18,
        "min_floors": 1,
        "max_floors": 2,
        "hero_prompt": (
            "Interior of a Hearth Atrium family dwelling at blue hour. A low "
            "family gathering around a great central fire-hearth on a polished "
            "stone floor. Above them, a crystal-glass oculus opens to a "
            "darkening blue sky with first stars. Ring of rooms around the "
            "hearth with small warm-lit doorways. Warm handmade brick walls, "
            "carved timber beams rising to the oculus. Smoke drifts upward "
            "through the oculus. Sacred, warm, ancient, awe-inducing."
        ),
        "variants": [
            {
                "id": "hearth_atrium_nordic_longhouse",
                "label": "Nordic Longhouse Hearth",
                "story": (
                    "Nordic tradition. Timber-framed longhouse with a large "
                    "iron brazier at centre; reindeer-skin floor around the "
                    "hearth; carved wood beams rise to a peaked oculus framed "
                    "with runes. Smoke rises through snow."
                ),
                "color": "#6B4A2E",
                "min_floors": 1, "max_floors": 2,
                "suggested_floor_height": 4.5, "suggested_area_sqm": 280,
                "prompt": (
                    "Interior of a Nordic longhouse Hearth Atrium at blue "
                    "winter dusk. Large wrought-iron brazier at centre with "
                    "orange flames. Timber-planked floor with reindeer skins. "
                    "Dark carved timber beams rise to a peaked oculus with "
                    "engraved runes at the rim, opening to indigo twilight sky "
                    "outside. Snow visible falling through the oculus. Long "
                    "dining table beside the hearth. Warm, sacred, ancient."
                ),
                "facade_primary": "dark horizontal timber cladding",
                "facade_secondary": "carved wooden runic-engraved frames",
                "facade_ground": "peat-block and stone plinth",
                "facade_palette": "dark timber, iron, amber fire, reindeer brown",
                "roof_form": "tall peaked gable with central rune-framed oculus",
                "roof_material": "hand-split cedar shingles"
            },
            {
                "id": "hearth_atrium_persian_courtyard",
                "label": "Persian Courtyard Hearth",
                "story": (
                    "Persian tradition. Tile-lined square atrium with columned "
                    "arcade around; central brazier of wrought bronze; "
                    "calligraphy bands above the doors; pool of water mirrors "
                    "the oculus above. The hearth where poetry lived."
                ),
                "color": "#2A4D8F",
                "min_floors": 1, "max_floors": 2,
                "suggested_floor_height": 5.0, "suggested_area_sqm": 260,
                "prompt": (
                    "Interior of a Persian courtyard Hearth Atrium at dusk. "
                    "Square atrium with deep blue and cream ceramic-tiled "
                    "columned arcade around a central bronze brazier with warm "
                    "flames. Calligraphic Quranic bands above the doorways. A "
                    "shallow still reflecting pool beside the brazier mirrors "
                    "the ornate muqarnas dome oculus above. Soft warm lanterns "
                    "in the arcade niches. Rich, contemplative, luminous."
                ),
                "facade_primary": "deep blue and cream ceramic-tiled facade panels",
                "facade_secondary": "carved stone columned arcade",
                "facade_ground": "inlaid stone courtyard with water channels",
                "facade_palette": "deep lapis blue, cream, gold calligraphy, warm bronze",
                "roof_form": "muqarnas dome with central oculus",
                "roof_material": "polychrome tiled muqarnas vaulting"
            },
            {
                "id": "hearth_atrium_pueblo_adobe",
                "label": "Pueblo Adobe Hearth",
                "story": (
                    "Pueblo / Ancestral Puebloan tradition. Adobe walls with "
                    "rounded corners; kiva-style sunken hearth at centre; "
                    "rough-hewn timber ladder through the oculus to the roof "
                    "terrace. High desert setting. Earth-and-sky cosmology."
                ),
                "color": "#B8815A",
                "min_floors": 1, "max_floors": 1,
                "suggested_floor_height": 3.8, "suggested_area_sqm": 180,
                "prompt": (
                    "Interior of a Pueblo adobe Hearth Atrium at early morning "
                    "high-desert light. Warm ochre-adobe walls with rounded "
                    "corners and small hand-cut windows. Kiva-style sunken "
                    "stone fire-pit at the centre with glowing embers. Rough-"
                    "hewn wooden ladder rising through a circular roof oculus "
                    "to a roof terrace, bright desert sky visible above. "
                    "Hand-woven rugs on a packed-earth floor. Warm, sacred, "
                    "elemental."
                ),
                "facade_primary": "warm ochre adobe plaster walls",
                "facade_secondary": "rough-hewn timber lintels and vigas",
                "facade_ground": "packed-earth plinth with low adobe bench",
                "facade_palette": "warm ochre, timber brown, amber fire, desert sky blue",
                "roof_form": "flat earth-packed roof with circular oculus and ladder",
                "roof_material": "earth-packed timber-beam roof with rooftop terrace"
            },
            {
                "id": "hearth_atrium_japanese_irori",
                "label": "Japanese Irori Hearth",
                "story": (
                    "Japanese irori tradition. Timber-framed open room with a "
                    "square sunken hearth at centre, pot on a kettle-hook "
                    "overhead. Shoji and tatami around. Engawa opening to a "
                    "moss garden. Oculus above frames the moon."
                ),
                "color": "#D6CFBE",
                "min_floors": 1, "max_floors": 2,
                "suggested_floor_height": 3.6, "suggested_area_sqm": 200,
                "prompt": (
                    "Interior of a Japanese irori Hearth Atrium at evening. "
                    "Timber-framed open room with tatami matting. Square "
                    "sunken irori fire-pit at centre with glowing charcoal "
                    "embers and a black iron kettle on a bamboo kettle-hook "
                    "descending from the ceiling. Shoji paper screens around "
                    "the walls partially open to a moss garden. Circular "
                    "oculus above frames a full moon in a twilight sky. "
                    "Serene, spare, sacred."
                ),
                "facade_primary": "cypress timber post-and-beam frame",
                "facade_secondary": "large sliding shoji paper screens",
                "facade_ground": "engawa veranda on stone plinth",
                "facade_palette": "pale cypress, warm paper, amber charcoal, deep moss green",
                "roof_form": "low pitched cedar-shingle roof with circular oculus",
                "roof_material": "hand-split cedar shingles"
            }
        ]
    },
    {
        "kind": "buildings",
        "slug": "utopic-intergenerational-commons",
        "id": "utopic_intergenerational_commons",
        "title": "Intergenerational Commons",
        "subcategory": "Utopic",
        "development_type": "residential_multifamily",
        "aesthetic_category": "utopic_biophilic",
        "description": (
            "A mid-rise residence where each floor holds a single extended "
            "family of 10-30 people — the social unit humans actually evolved "
            "for. A central open vertical stair pierces every floor so every "
            "generation is visible to the others. Shared library, shared kitchen "
            "nodes, shared children's play floor. The architecture finally "
            "honours the extended family the way our bodies expect."
        ),
        "tags": ["utopic", "intergenerational", "extended-family", "commons", "vertical-community"],
        "style_profile": {
            "materials": ["mass timber (CLT)", "warm stone base", "ceramic tile interiors", "woven rope balustrades", "abundant plantlife"],
            "facadeRhythm": "Vertical family bays with distinct expression per family; courtyards project outward",
            "roofForm": "Stepped green roof terraces with shared gardens and a central skylight over the vertical stair",
            "frontageType": "Generous ground-floor common room opening onto a shared courtyard",
            "windowStyle": "Floor-to-ceiling operable glass onto each family's veranda; small deep windows to the interior",
            "massing": "Rectangular or circular 10-20 storey block around a central vertical atrium",
            "heightTendency": "Mid-rise (10-20 storeys)",
            "streetRelationship": "Ground-floor commons opens directly to the street; above, private family terraces",
            "renderingMood": "Warm, social, layered, alive with all ages",
            "articulation": "Each family floor visibly distinct via varied screen colors, planting, textiles",
            "publicRealm": "Ground commons + rooftop garden + every floor's central open stair landing"
        },
        "prompt_block": {
            "subject": "Mid-rise multi-family residence — one extended family per floor with a central vertical open stair",
            "details": [
                "10-20 storey rectangular or circular block",
                "Central open vertical stair visible through every floor",
                "Each floor is a single extended family of 10-30 people",
                "Shared ground-floor commons, rooftop garden",
                "Ring of family rooms and verandas around the central atrium",
                "Warm timber + stone + plant palette"
            ]
        },
        "suggested_width_m": 40,
        "suggested_depth_m": 40,
        "min_floors": 10,
        "max_floors": 20,
        "hero_prompt": (
            "Cross-section perspective of a 15-storey Intergenerational Commons "
            "residence at golden hour. Warm mass-timber post-and-beam structure "
            "with a central open vertical atrium stair visible through every "
            "floor — each level is a distinct extended family's home with "
            "different textiles, plants, coloured screens. Children on one "
            "landing, grandparents on another, young adults elsewhere. "
            "Stepped green-roof terraces at the crown. Sun streaming through a "
            "central skylight. Warm, layered, alive."
        ),
        "variants": [
            {
                "id": "commons_mediterranean_familia",
                "label": "Mediterranean Familia Tower",
                "story": (
                    "Southern European variant — pastel-washed stucco facades, "
                    "wrought-iron balconies, grape vines climbing the central "
                    "courtyard, lemon trees on each family terrace. The "
                    "matriarchal abuela apartment on floor 1."
                ),
                "color": "#E8C098",
                "min_floors": 10, "max_floors": 16,
                "suggested_floor_height": 3.6, "suggested_area_sqm": 1600,
                "prompt": (
                    "A Mediterranean Familia Intergenerational Commons — a 12-"
                    "storey pastel-washed stucco tower with wrought-iron "
                    "balconies on every floor, grape vines and jasmine climbing "
                    "a central open courtyard, lemon trees on family terraces. "
                    "Warm evening light, strings of lights in the courtyard, "
                    "families visible at multiple levels. A grandmother on a "
                    "ground-floor porch. Strings of drying laundry on upper "
                    "balconies. Warm, social, lived-in, golden hour."
                ),
                "facade_primary": "pastel-washed lime stucco (pale apricot, terracotta, cream)",
                "facade_secondary": "wrought-iron balcony railings with grape vines",
                "facade_ground": "stone-paved street entrance with public fountain",
                "facade_palette": "warm pastel stuccos, dark iron, green vines, terracotta roof",
                "roof_form": "stepped green roof with rooftop olive grove and dining pergola",
                "roof_material": "clay tile with rooftop dining pavilion"
            },
            {
                "id": "commons_chinese_tulou",
                "label": "Chinese Tulou-Inspired Round Commons",
                "story": (
                    "Inspired by Fujian tulou — round earthen-walled communal "
                    "fortress reimagined as modern multi-generational housing. "
                    "Thick rammed-earth outer wall, timber-framed inner "
                    "galleries around a vast central courtyard with a pond "
                    "and cooking pavilion."
                ),
                "color": "#C9A076",
                "min_floors": 4, "max_floors": 6,
                "suggested_floor_height": 3.8, "suggested_area_sqm": 3200,
                "prompt": (
                    "A Chinese Tulou-inspired round Intergenerational Commons — "
                    "a 5-storey round building in rammed-earth ochre outer "
                    "wall with timber-framed inner gallery balconies around a "
                    "vast central courtyard. Central pond with stepping stones "
                    "and a small cooking pavilion with smoke rising. "
                    "Multi-generational families visible on every gallery. "
                    "Late-afternoon golden light filtering into the courtyard. "
                    "Sacred, communal, ancient-future."
                ),
                "facade_primary": "thick rammed-earth ochre outer walls",
                "facade_secondary": "timber-framed inner gallery balconies",
                "facade_ground": "stone-paved courtyard with pond and cooking pavilion",
                "facade_palette": "warm ochre earth, honey timber, pond-water blue, terracotta",
                "roof_form": "double-pitched tiled roof ring encircling the courtyard",
                "roof_material": "hand-thrown clay tile"
            },
            {
                "id": "commons_scandinavian_timber",
                "label": "Scandinavian Timber Commons",
                "story": (
                    "Northern European variant — exposed cross-laminated timber "
                    "throughout, shared communal sauna levels every 4 floors, "
                    "snow-melted rooftop hot tubs, birch-forested ground floor "
                    "commons with fireplace."
                ),
                "color": "#A77842",
                "min_floors": 10, "max_floors": 15,
                "suggested_floor_height": 3.4, "suggested_area_sqm": 1500,
                "prompt": (
                    "A Scandinavian timber Intergenerational Commons — a 12-"
                    "storey exposed cross-laminated timber tower with glass "
                    "curtain walls showing the warm timber structure. Birch "
                    "trees at the ground floor commons. Shared sauna pavilion "
                    "every 4 floors visible as glowing warm rectangles. "
                    "Rooftop hot tubs with steam rising in winter evening. "
                    "Crisp, warm, nordic, serene."
                ),
                "facade_primary": "exposed cross-laminated timber post-and-beam",
                "facade_secondary": "floor-to-ceiling glass curtain wall infill",
                "facade_ground": "birch-tree-lined stone commons entrance",
                "facade_palette": "honey timber, clear glass, birch white, amber interior light",
                "roof_form": "flat stepped green roof with hot tub terraces",
                "roof_material": "green roof with timber sauna + hot tub pavilion"
            },
            {
                "id": "commons_tropical_veranda",
                "label": "Tropical Veranda Commons",
                "story": (
                    "Tropical variant — deep overhanging roofs, indoor-outdoor "
                    "floors, every family has a full veranda with hammocks and "
                    "mosquito-nets at night. Woven rattan ceilings. Banana "
                    "trees and frangipani in the courtyard."
                ),
                "color": "#4A7A5E",
                "min_floors": 8, "max_floors": 14,
                "suggested_floor_height": 3.8, "suggested_area_sqm": 1700,
                "prompt": (
                    "A tropical Veranda Intergenerational Commons — a 10-storey "
                    "building with deep overhanging thatched-timber roofs on "
                    "every floor, extensive open verandas with hammocks and "
                    "woven rattan ceilings. Banana trees and frangipani in a "
                    "central open courtyard with a clear pool. Lush, warm, "
                    "humid. Late-afternoon golden light through palm shadows. "
                    "Families visible on every veranda. Alive, vibrant."
                ),
                "facade_primary": "deep overhanging timber verandas on every floor",
                "facade_secondary": "woven rattan ceiling soffits and bamboo shades",
                "facade_ground": "courtyard pool with banana trees and frangipani",
                "facade_palette": "honey timber, woven rattan, green banana leaves, frangipani white",
                "roof_form": "stepped overhanging tropical pitched roofs",
                "roof_material": "fibre-based thatched panels over timber structure"
            }
        ]
    },
    {
        "kind": "buildings",
        "slug": "utopic-contemplation-spire",
        "id": "utopic_contemplation_spire",
        "title": "Contemplation Spire",
        "subcategory": "Utopic",
        "development_type": "institutional",
        "aesthetic_category": "utopic_civic",
        "description": (
            "A public civic spire of 30 chambers, each tuned to a specific "
            "mental state — grief, creative work, rest, forgiveness, memory, "
            "anticipation, awe, decision-making, reconciliation. Citizens visit "
            "the chamber their day needs; each chamber's light, acoustics, "
            "scent, temperature, and materiality are precisely calibrated to "
            "that state. The most important civic building after the library."
        ),
        "tags": ["utopic", "civic", "contemplative", "awe", "tower", "mental-health"],
        "style_profile": {
            "materials": ["carved pale stone", "mass timber", "crystal-glass", "water features", "bioplastic translucent panels"],
            "facadeRhythm": "Each chamber expressed externally as a distinct facade quadrant",
            "roofForm": "Slender tapering spire with an observatory oculus at the crown",
            "frontageType": "Monumental civic entry with reflection pool and cypress allée",
            "windowStyle": "Chamber-specific — no two windows alike; some narrow, some vast, some coloured",
            "massing": "Slender 30-storey tapered spire, 25x25m at base, 10x10m at crown",
            "heightTendency": "Tall (100-150m)",
            "streetRelationship": "Monumental civic approach with reflection pool and processional allée",
            "renderingMood": "Reverent, varied (each chamber a different mood), contemplative",
            "articulation": "Each chamber's external expression a distinct architectural gesture",
            "publicRealm": "Ground-level cypress allée + reflection pool; rooftop observatory open to all"
        },
        "prompt_block": {
            "subject": "A slender civic tower of 30 chambers each tuned to a specific mental state",
            "details": [
                "Slender tapered 30-storey spire, 100-150m tall",
                "Each chamber expressed as a distinct facade gesture",
                "Monumental entry with reflection pool and cypress allée",
                "Rooftop observatory oculus",
                "Materials: carved pale stone, mass timber, crystal-glass, water"
            ]
        },
        "suggested_width_m": 25,
        "suggested_depth_m": 25,
        "min_floors": 25,
        "max_floors": 40,
        "hero_prompt": (
            "A slender 130-meter tapered civic Contemplation Spire at dusk. "
            "Each of its 30 storeys visibly distinct — narrow slit windows on "
            "one level, a projecting quiet balcony on another, a fully glazed "
            "chamber elsewhere, a carved-stone sanctum at another. Crystal "
            "glass crown at the top with an astronomical oculus. Long cypress "
            "allée leading to a monumental entry with a still reflecting pool. "
            "Soft twilight, each chamber glowing warm with different colours "
            "(amber, blue, cream, rose). Reverent, sublime, varied."
        ),
        "variants": [
            {
                "id": "contemplation_monastic_stone",
                "label": "Monastic Stone Spire",
                "story": (
                    "Romanesque-inspired. Carved honey-stone with small "
                    "Norman-arched windows and a weathered steep stone roof "
                    "on the crown. Feels ancient even new. The grief and "
                    "reconciliation chambers are at the base with candlelit "
                    "stone; the awe chamber is at the apex."
                ),
                "color": "#D4B37A",
                "min_floors": 20, "max_floors": 30,
                "suggested_floor_height": 4.0, "suggested_area_sqm": 500,
                "prompt": (
                    "A Romanesque-inspired monastic Contemplation Spire at "
                    "soft dawn — slender tapered 25-storey carved honey-"
                    "coloured stone tower with small Norman-arched windows "
                    "and decorative carved stone bands marking each chamber. "
                    "Steep dark weathered-stone conical roof at the crown "
                    "with a tiny cross finial replaced by a crystal oculus. "
                    "Surrounding cypress allée with stone monastery walls. "
                    "Hushed, ancient, sacred."
                ),
                "facade_primary": "carved honey-coloured Romanesque stone",
                "facade_secondary": "small Norman-arched windows with carved surrounds",
                "facade_ground": "cloistered stone cypress-allée approach",
                "facade_palette": "honey stone, weathered dark roof, cypress green, cream cloister",
                "roof_form": "tall conical weathered-stone roof with crystal-oculus finial",
                "roof_material": "weathered dark sandstone slate"
            },
            {
                "id": "contemplation_zen_minimalist",
                "label": "Zen Minimalist Spire",
                "story": (
                    "Japanese Zen-inspired. Pale smooth concrete with honey-"
                    "toned timber screens. Shallow reflecting pool at base. "
                    "Water features cascading silently between chambers. "
                    "Rest and creative-work chambers."
                ),
                "color": "#E8E4DC",
                "min_floors": 20, "max_floors": 30,
                "suggested_floor_height": 4.2, "suggested_area_sqm": 480,
                "prompt": (
                    "A Zen-minimalist Contemplation Spire at morning overcast "
                    "— slender tapered 25-storey pale smooth-concrete tower "
                    "with honey-toned timber screen accents at each chamber, "
                    "occasional cascading water features trickling down "
                    "between levels. Shallow still reflecting pool at the "
                    "base with a single stone path across. Spare pine tree. "
                    "Restrained, serene, luminous."
                ),
                "facade_primary": "pale smooth board-formed concrete",
                "facade_secondary": "honey-toned timber screens on select chambers",
                "facade_ground": "shallow still reflecting pool with stone path",
                "facade_palette": "pale cream concrete, honey timber, water, single pine green",
                "roof_form": "flat crystal-glass observatory at crown",
                "roof_material": "crystal-glass oculus over observatory chamber"
            },
            {
                "id": "contemplation_sufi_geometric",
                "label": "Sufi Geometric Spire",
                "story": (
                    "Sufi-inspired. Intricate geometric tile patterns across "
                    "every chamber, calligraphy bands above doors, light "
                    "filtered through mashrabiya wooden screens throws "
                    "shifting patterns on interior floors. Memory and "
                    "anticipation chambers."
                ),
                "color": "#4A88A8",
                "min_floors": 20, "max_floors": 30,
                "suggested_floor_height": 4.0, "suggested_area_sqm": 500,
                "prompt": (
                    "A Sufi-inspired geometric Contemplation Spire at late-"
                    "afternoon light — slender tapered 25-storey tower clad "
                    "in intricate deep-blue and cream geometric ceramic tiles "
                    "with calligraphic Arabic bands above the doorways at "
                    "each chamber level. Mashrabiya carved-wood screen "
                    "windows casting shifting geometric shadows. Central "
                    "courtyard with a tiled fountain at the base. "
                    "Luminous, sacred, rich, contemplative."
                ),
                "facade_primary": "intricate deep-blue and cream geometric ceramic tile",
                "facade_secondary": "mashrabiya carved-wood screen windows",
                "facade_ground": "tiled courtyard with octagonal fountain",
                "facade_palette": "lapis blue, cream, gold calligraphy, warm timber, terracotta",
                "roof_form": "tiled geometric dome with calligraphy band",
                "roof_material": "polychrome tiled dome over astronomical chamber"
            },
            {
                "id": "contemplation_indigenous_wheel",
                "label": "Indigenous Medicine Wheel Spire",
                "story": (
                    "Inspired by North American Indigenous medicine-wheel "
                    "cosmology — four primary chambers at cardinal directions "
                    "(each a different element: earth, fire, water, air), "
                    "surrounded by 26 more. Weathered timber with stone, "
                    "natural textures, prayer-flag colours."
                ),
                "color": "#8A6244",
                "min_floors": 20, "max_floors": 30,
                "suggested_floor_height": 3.8, "suggested_area_sqm": 450,
                "prompt": (
                    "An Indigenous medicine-wheel-inspired Contemplation Spire "
                    "at golden hour on a prairie ridge. Slender 25-storey "
                    "tower with four primary facade sections at cardinal "
                    "directions, each in a distinct earthy palette (ochre, "
                    "red, white, black). Weathered timber framing with stone "
                    "infill panels. Prayer-flag colours at the crown. Ground "
                    "surrounded by tall prairie grasses. Eagle in the sky. "
                    "Sacred, rooted, four-directional."
                ),
                "facade_primary": "weathered timber framing with stone infill panels",
                "facade_secondary": "four cardinal-direction colour bands (ochre, red, white, black)",
                "facade_ground": "stone-circle prairie plinth with medicine-wheel pattern",
                "facade_palette": "weathered timber, stone greys, ochre, red, white, black, prairie gold",
                "roof_form": "four-peaked crown with prayer-flag lines",
                "roof_material": "weathered timber shingle with ceremonial flag-lines"
            }
        ]
    },

    # ═══════════════════════════════════════════════════════════════════════
    # OPENSPACES (4)
    # ═══════════════════════════════════════════════════════════════════════
    {
        "kind": "openspaces",
        "slug": "utopic-savanna-garden",
        "id": "utopic_savanna_garden",
        "title": "Savanna Garden",
        "subcategory": "Utopic",
        "aesthetic_category": "utopic",
        "space_type": "park",
        "description": (
            "The evolutionary-optimal park — open meadow with scattered large "
            "shade trees, a watering hole, and a distant ridge on the horizon. "
            "Prospect-refuge theory perfected. Every human visual system was "
            "tuned by a million years of preferring exactly this landscape; the "
            "park is what our DNA expects to see. Reading, resting, "
            "picnicking, thinking — all deeply calibrated by this ancient "
            "ground."
        ),
        "tags": ["utopic", "biophilic", "savanna", "prospect-refuge", "evolutionary-optimal"],
        "hero_prompt": (
            "A Savanna Garden park at golden hour — wide open tall-grass meadow "
            "with a scattering of large spreading shade trees, a shallow "
            "watering hole at the centre with stepping stones, and a distant "
            "low ridge on the horizon. A few figures reading under the trees, "
            "a family by the water. Warm late-afternoon light, long shadows. "
            "Sublime, timeless, deeply restorative. Photorealistic biophilic "
            "architectural photography."
        ),
        "suggested_width_m": 150,
        "suggested_depth_m": 120,
        "suggested_area_sqm": 18000,
        "variants": [
            {
                "id": "savanna_african_acacia",
                "label": "African Acacia Savanna",
                "story": "Central African ancestral variant — acacia trees, tall golden grasses, gazelle herd visible, distant kopje rock-hill.",
                "color": "#C0A466",
                "prompt": (
                    "An African acacia Savanna Garden park at golden hour — "
                    "spreading acacia trees with flat-topped canopies, tall "
                    "golden ochre grasses, a shallow watering hole with "
                    "zebra and gazelle visible in the distance, a rocky "
                    "kopje on the horizon. Warm late-afternoon sun, long "
                    "shadows. Deeply primal, sublime."
                )
            },
            {
                "id": "savanna_oak_meadow",
                "label": "English Oak Meadow",
                "story": "Northern European variant — spreading oaks over wildflower meadow, grazing deer, stone folly.",
                "color": "#7A8B52",
                "prompt": (
                    "An English Oak Meadow Savanna Garden in late-afternoon "
                    "early-summer light — spreading ancient oak trees over a "
                    "wildflower meadow (buttercups, ox-eye daisies, red "
                    "clover), a small reflecting pond, grazing fallow deer, "
                    "a distant stone folly on a low ridge. Warm hazy light, "
                    "long grass shadows. Timeless, pastoral."
                )
            },
            {
                "id": "savanna_prairie_cottonwood",
                "label": "Prairie Cottonwood Garden",
                "story": "North American prairie variant — cottonwood trees clustered near a slow creek, tallgrass prairie, bison herd in distance.",
                "color": "#C8B06A",
                "prompt": (
                    "A North American prairie Cottonwood Savanna Garden at "
                    "golden hour — tall cottonwood trees clustered near a "
                    "slow shallow creek, wide tallgrass prairie of big "
                    "bluestem and goldenrod, a small herd of bison in the "
                    "distance, a low ridge on the horizon. Warm autumn sun, "
                    "vast sky. Primal, American."
                )
            },
            {
                "id": "savanna_mediterranean_olive",
                "label": "Mediterranean Olive Savanna",
                "story": "Mediterranean variant — ancient olive trees, wildflower meadow, stone outcrops, distant hilltop village.",
                "color": "#9AA87E",
                "prompt": (
                    "A Mediterranean olive Savanna Garden at late-afternoon "
                    "golden hour — ancient gnarled olive trees with "
                    "silver-green leaves scattered across a wildflower "
                    "meadow (red poppies, purple thyme), rough limestone "
                    "outcrops, a distant hilltop village visible on the "
                    "horizon. Warm dry light, long shadows. Timeless, "
                    "mythic."
                )
            }
        ]
    },
    {
        "kind": "openspaces",
        "slug": "utopic-aquarium-gardens",
        "id": "utopic_aquarium_gardens",
        "title": "Aquarium Gardens",
        "subcategory": "Utopic",
        "aesthetic_category": "utopic",
        "space_type": "park",
        "description": (
            "An inhabitable aquatic-biome park you walk through via clear glass "
            "atria, with fish flocking overhead and coral or kelp framing you. "
            "Multisensory awe-machine combining water's parasympathetic calm, "
            "the blue-shift of mammalian cortisol, and the sheer sublime of "
            "an alien biosphere you can enter. Free to the public."
        ),
        "tags": ["utopic", "biophilic", "aquatic", "multisensory", "awe", "immersive"],
        "hero_prompt": (
            "Interior of an Aquarium Gardens park — a wide glass-walled "
            "promenade under a great clear curved aquarium dome at mid-day. "
            "Schools of silvery and colourful fish flock overhead; a giant "
            "sea turtle drifts by; coral structures frame the far wall. "
            "Visitors strolling, children with hands pressed to the glass. "
            "Soft aquatic light filtering down in rippling beams. Sublime, "
            "blue, immersive. Photorealistic."
        ),
        "suggested_width_m": 80,
        "suggested_depth_m": 80,
        "suggested_area_sqm": 6400,
        "variants": [
            {
                "id": "aquarium_coral_reef",
                "label": "Coral Reef Garden",
                "story": "Tropical coral reef variant — colourful reef fish, parrotfish, sea turtles, bright coral structures.",
                "color": "#E88A6A",
                "prompt": (
                    "A Coral Reef Aquarium Garden park — wide glass-walled "
                    "promenade under a giant clear aquarium dome filled with "
                    "schools of bright tropical fish (parrotfish, clownfish, "
                    "tangs), sea turtles, vibrant coral structures in pink, "
                    "orange, and white. Ripply blue-green light filtering "
                    "down. Visitors in wonder. Vivid, warm, awe."
                )
            },
            {
                "id": "aquarium_kelp_forest",
                "label": "Kelp Forest Garden",
                "story": "Pacific cold-water variant — towering giant kelp, sea lions, orange garibaldi fish, dappled green-gold light.",
                "color": "#3E6B52",
                "prompt": (
                    "A Kelp Forest Aquarium Garden park — wide glass-walled "
                    "promenade beside a towering underwater kelp forest, "
                    "massive green-gold kelp fronds swaying, sea lions "
                    "playing, bright orange garibaldi fish, dappled green-"
                    "gold light filtering through the kelp canopy from "
                    "above. Cool, lush, serene."
                )
            },
            {
                "id": "aquarium_river_garden",
                "label": "Freshwater River Garden",
                "story": "Temperate river variant — trout, sturgeon, pike, willows overhead above the glass, freshwater clarity.",
                "color": "#6A96A0",
                "prompt": (
                    "A Freshwater River Aquarium Garden park — a glass-"
                    "walled promenade beside and under a wide flowing "
                    "freshwater river habitat with trout, pike, and large "
                    "sturgeon drifting past. Willow branches overhead "
                    "above the glass. Ripples and reflections of tree "
                    "shadows on the river bottom. Clear cool light."
                )
            },
            {
                "id": "aquarium_arctic_ice",
                "label": "Arctic Ice Aquarium",
                "story": "Polar variant — beluga whales, narwhals, ice caves, pale blue-white light, cold clear water.",
                "color": "#B6D6E0",
                "prompt": (
                    "An Arctic Ice Aquarium Gardens park — a glass-walled "
                    "promenade passing through clear pale-blue icy water "
                    "with beluga whales and narwhals drifting by, ice-"
                    "cave-like blue-white structures framing the space. "
                    "Pale cool light from above. Awe-inspiring, serene, "
                    "cold-bright."
                )
            }
        ]
    },
    {
        "kind": "openspaces",
        "slug": "utopic-stone-garden-of-time",
        "id": "utopic_stone_garden_of_time",
        "title": "Stone Garden of Time",
        "subcategory": "Utopic",
        "aesthetic_category": "utopic",
        "space_type": "park",
        "description": (
            "A megalithic landscape of massive standing stones precisely aligned "
            "to celestial cycles — solstices, planetary conjunctions, specific "
            "stars' annual transits. Walking the stones is walking deep time. "
            "A civic astronomical instrument you live inside, combining the "
            "ancient resonance of standing-stone ritual with modern "
            "astronomical precision."
        ),
        "tags": ["utopic", "megalithic", "astronomical", "sacred", "deep-time", "ceremonial"],
        "hero_prompt": (
            "A Stone Garden of Time at sunrise during an equinox — a ring of "
            "massive weathered granite standing stones, each 5-8 meters tall, "
            "arranged precisely so the rising sun frames between the eastern "
            "stones. Wild grasses and wildflowers between the stones. A single "
            "figure standing at the ring's centre. Pink-gold dawn light. "
            "Sacred, ancient-future, awe-inducing. Photorealistic."
        ),
        "suggested_width_m": 120,
        "suggested_depth_m": 120,
        "suggested_area_sqm": 14400,
        "variants": [
            {
                "id": "stone_time_solstice_circle",
                "label": "Solstice Stone Circle",
                "story": "Stonehenge-inspired solstice circle — trilithons aligned to summer and winter sunrises.",
                "color": "#8A8278",
                "prompt": (
                    "A Solstice Stone Circle at midsummer sunrise — massive "
                    "weathered grey trilithon standing stones in a circle, "
                    "the rising sun precisely framed between two eastern "
                    "trilithons. Mist hanging low. Wild meadow grass "
                    "between the stones. A small gathering of still "
                    "figures at the centre. Pink-gold dawn, sacred, timeless."
                )
            },
            {
                "id": "stone_time_lunar_standing",
                "label": "Lunar Standing Stones",
                "story": "Bronze-Age-inspired lunar cycle marker — tall slender stones tracking monthly phases.",
                "color": "#A8A29A",
                "prompt": (
                    "A Lunar Standing Stones garden at full-moon rise — tall "
                    "slender weathered grey standing stones of varying "
                    "heights (3-8m) arranged to track lunar phases, the "
                    "full moon precisely framed between two tall stones on "
                    "the eastern horizon. Evening twilight sky. Moss and "
                    "wildflowers at the base. Sacred, mysterious."
                )
            },
            {
                "id": "stone_time_planetary_inca",
                "label": "Planetary Alignment Garden",
                "story": "Incan-precision stonework — finely joined polygonal stones marking planetary conjunctions.",
                "color": "#7A6B58",
                "prompt": (
                    "An Incan-inspired Planetary Alignment Stone Garden "
                    "at golden-hour — precisely fitted polygonal grey "
                    "stones in terraced walls with carved astronomical "
                    "sight-lines, small notches framing where Venus "
                    "rises. High-altitude clear air, distant mountains. "
                    "Wild alpine grasses. Sacred, precise, sublime."
                )
            },
            {
                "id": "stone_time_southern_star",
                "label": "Southern Star Chart Garden",
                "story": "Southern-hemisphere star-pattern stones — positions of stones mirror constellations overhead.",
                "color": "#6A5E4A",
                "prompt": (
                    "A Southern Star Chart Stone Garden at night — scattered "
                    "dark standing stones whose positions mirror the "
                    "Southern Cross and nearby constellations on the ground. "
                    "Clear dark sky with the actual Milky Way blazing "
                    "overhead. Wild grasses and scattered eucalyptus. "
                    "Dramatic, sacred, cosmic."
                )
            }
        ]
    },
    {
        "kind": "openspaces",
        "slug": "utopic-night-bloom-garden",
        "id": "utopic_night_bloom_garden",
        "title": "Night Bloom Garden",
        "subcategory": "Utopic",
        "aesthetic_category": "utopic",
        "space_type": "park",
        "description": (
            "A park experienced primarily at night. Bioluminescent plants, "
            "moon-path pavements, star-observation platforms, night-blooming "
            "flowers releasing fragrance only after dusk. The sacred night "
            "that modern cities obliterated — reclaimed with modern "
            "atmospheric care (dark-sky preserves, minimal light pollution) "
            "and ancient reverence."
        ),
        "tags": ["utopic", "nocturnal", "bioluminescent", "dark-sky", "sacred-night"],
        "hero_prompt": (
            "A Night Bloom Garden park at blue hour — a winding stone path "
            "glowing faintly from bioluminescent moss edges, tall night-"
            "blooming white moonflowers, bioluminescent pale-blue fern "
            "glades, a small reflecting pool mirroring the first stars. A "
            "single figure sitting on a stone bench. Deep indigo sky. "
            "Faint soft glow throughout, no harsh lights. Sacred, still, "
            "magical. Photorealistic night photography."
        ),
        "suggested_width_m": 100,
        "suggested_depth_m": 100,
        "suggested_area_sqm": 10000,
        "variants": [
            {
                "id": "night_full_moon_lotus",
                "label": "Full Moon Lotus Garden",
                "story": "Tropical lily-pond variant — waterlily pools, night-blooming lotus, tropical fireflies.",
                "color": "#C8D4E8",
                "prompt": (
                    "A tropical Full Moon Lotus Night Bloom Garden — "
                    "terraced waterlily pools filled with open white night-"
                    "blooming lotus flowers, tall papyrus, fireflies "
                    "drifting above the water. Full moon casting silver "
                    "reflections on the pools. Warm humid night. Magical, "
                    "serene, luminous."
                )
            },
            {
                "id": "night_milky_way_meadow",
                "label": "New Moon Milky Way Meadow",
                "story": "Dark-sky preserve — wildflower meadow under a blazing Milky Way, bioluminescent fungi in shadows.",
                "color": "#2A2E4A",
                "prompt": (
                    "A New Moon Milky Way Meadow Night Bloom Garden — wide "
                    "wildflower meadow at the edge of a small forest under "
                    "a brilliant blazing Milky Way directly overhead. "
                    "Small faint-glowing clusters of bioluminescent fungi "
                    "at the forest edge. A single figure lying back on the "
                    "grass. Dark-sky preserve, no light pollution. Awe, "
                    "cosmic."
                )
            },
            {
                "id": "night_fern_cathedral",
                "label": "Blue Hour Fern Cathedral",
                "story": "Temperate fern gully variant — cool blue bioluminescent mosses, tall tree ferns, small waterfalls.",
                "color": "#3A5E6A",
                "prompt": (
                    "A temperate Blue Hour Fern Cathedral Night Bloom "
                    "Garden — gully lined with tall tree-ferns glowing "
                    "pale-blue from bioluminescent mosses at their bases, "
                    "small waterfalls cascading over moss-covered rocks, "
                    "a narrow timber boardwalk winding through. Deep blue "
                    "twilight above through the fern canopy. Cool, lush, "
                    "sacred."
                )
            },
            {
                "id": "night_desert_cactus",
                "label": "Desert Night Cactus Garden",
                "story": "Arid variant — tall columnar cacti with rare night-blooming white flowers, clear desert sky.",
                "color": "#4A5062",
                "prompt": (
                    "A Desert Night Cactus Bloom Garden — tall columnar "
                    "saguaro-like cacti bearing rare white night-blooming "
                    "flowers at their crowns, a winding sand path, a "
                    "blazing Milky Way overhead in a cloudless desert sky. "
                    "Pale sand glowing faintly in starlight. Crisp, "
                    "cosmic, sacred."
                )
            }
        ]
    },

    # ═══════════════════════════════════════════════════════════════════════
    # STREETS (4)
    # ═══════════════════════════════════════════════════════════════════════
    {
        "kind": "streets",
        "slug": "utopic-heart-main",
        "id": "utopic_heart_main",
        "title": "Heart Main",
        "subcategory": "Utopic",
        "aesthetic_category": "utopic",
        "description": (
            "The archetypal beloved main street distilled. 18m wide, continuous "
            "human-scaled shopfronts, outdoor cafés, fountains, musicians, "
            "benches, trees, scented plantings. Jane Jacobs + Rome + Kyoto + "
            "the Djemaa El Fna, perfected. The street you remember from the "
            "town you loved — the one every visitor secretly wishes their own "
            "city had."
        ),
        "tags": ["utopic", "main-street", "pedestrian", "beloved", "community"],
        "hero_prompt": (
            "A Heart Main beloved main street at late-afternoon golden hour "
            "— 18m wide pedestrian street lined with continuous warm shopfronts "
            "at ground level, outdoor café seating, a small central fountain, "
            "a busker, plane trees, stone benches, scented lavender planters. "
            "Warm stone paving, varied 3-4 storey buildings above. People "
            "strolling, sitting, talking. Warm, alive, loved. Photorealistic."
        ),
        "suggested_width_m": 18,
        "variants": [
            {
                "id": "heart_main_italian_piazza",
                "label": "Italian Piazza Main",
                "story": "Italian hilltown tradition — warm sandstone, stone fountain, cypress, passeggiata flowers.",
                "color": "#D8A074",
                "prompt": (
                    "An Italian hilltown Heart Main street at golden hour — "
                    "18m wide warm-sandstone-paved pedestrian street lined "
                    "with 3-storey ochre-and-umber stucco buildings, wrought-"
                    "iron balconies with geraniums, a central baroque stone "
                    "fountain, outdoor café tables, strolling families, a "
                    "solitary accordion player. Warm, romantic, ancient-alive."
                )
            },
            {
                "id": "heart_main_japanese_shotengai",
                "label": "Japanese Shōtengai Main",
                "story": "Traditional Japanese covered arcade — paper lanterns, wood shopfronts, seasonal banners.",
                "color": "#C94545",
                "prompt": (
                    "A Japanese shōtengai Heart Main street at evening — a "
                    "covered pedestrian arcade with a translucent glass-"
                    "roofed canopy, lined with traditional wooden shopfronts "
                    "(ramen, tea, wagashi sweets), red paper lanterns "
                    "glowing warm above, seasonal cherry-blossom banners. "
                    "Strolling visitors in yukata. Warm, festive, timeless."
                )
            },
            {
                "id": "heart_main_moroccan_medina",
                "label": "Moroccan Medina Main",
                "story": "Narrow souk variant — woven reed shade canopies, textile shops, spice stalls, fountain niches.",
                "color": "#A8520A",
                "prompt": (
                    "A Moroccan medina Heart Main street at warm afternoon — "
                    "a 10m wide cobbled street shaded by woven reed mats "
                    "overhead casting dappled shadows, lined with small "
                    "open-front shops (textiles, ceramics, spices in conical "
                    "piles, leather goods), tiled fountain niches, mint tea "
                    "stalls. Warm rich light, scents of spice and orange "
                    "blossom. Rich, alive, ancient."
                )
            },
            {
                "id": "heart_main_new_england",
                "label": "New England Main",
                "story": "White-clapboard + red-brick tradition — autumn maples, bandstand, village green.",
                "color": "#C97554",
                "prompt": (
                    "A New England Heart Main street in autumn mid-afternoon "
                    "— 18m wide street lined with historic white-clapboard "
                    "and red-brick 3-storey buildings with hand-painted "
                    "shop signs, brilliant red and orange sugar-maple "
                    "trees along both sides, a small village-green "
                    "bandstand visible, strolling families. Warm autumn "
                    "light. Nostalgic, beloved, all-American."
                )
            }
        ]
    },
    {
        "kind": "streets",
        "slug": "utopic-plane-tree-allee",
        "id": "utopic_plane_tree_allee",
        "title": "Plane-Tree Allée",
        "subcategory": "Utopic",
        "aesthetic_category": "utopic",
        "description": (
            "A ceremonial boulevard defined by double rows of 40m tall tree "
            "canopies, formal paving, fountains at regular intervals, "
            "monumental endpoints at both ends. Used for weddings, funerals, "
            "festivals, and the daily passeggiata. Monumental and walkable "
            "simultaneously — civic grandeur at human scale."
        ),
        "tags": ["utopic", "ceremonial", "boulevard", "allée", "tree-lined"],
        "hero_prompt": (
            "A grand Plane-Tree Allée ceremonial boulevard at late-afternoon "
            "golden hour — straight stone-paved avenue defined by double "
            "rows of 40-meter-tall mature plane trees arching overhead to "
            "form a living tunnel, sunlight dappled down through the leaves. "
            "Small bronze-basin fountains at regular intervals. Distant "
            "monumental arch at the end of the allée. Strolling couples, "
            "a wedding procession. Sacred, grand, loved."
        ),
        "suggested_width_m": 30,
        "variants": [
            {
                "id": "allee_parisian_plane",
                "label": "Parisian Plane-Tree Allée",
                "story": "Classic Parisian Haussmann allée — crushed-stone paths, plane trees, stone fountain basins.",
                "color": "#7A8E52",
                "prompt": (
                    "A Parisian Plane-Tree Allée at golden hour — wide "
                    "crushed-stone path flanked by 40-meter mature plane "
                    "trees, stone fountain basins, Haussmann-style "
                    "limestone buildings visible through the leaves. "
                    "Couples strolling. Warm light filtering through "
                    "the canopy. Classic, romantic."
                )
            },
            {
                "id": "allee_cherry_blossom",
                "label": "Cherry Blossom Allée",
                "story": "Japanese spring cherry-blossom ceremonial walk — sakura canopy overhead, petals falling.",
                "color": "#F2C2D4",
                "prompt": (
                    "A Japanese Cherry Blossom Allée in full spring bloom "
                    "— wide stone-paved path flanked by double rows of "
                    "mature cherry trees in peak bloom forming a pink "
                    "canopy overhead, petals falling gently. Small "
                    "timber shrine at one end. Strolling visitors in "
                    "kimono. Magical, ephemeral, sacred."
                )
            },
            {
                "id": "allee_live_oak_moss",
                "label": "Live Oak Mossy Allée",
                "story": "Louisiana live-oak + Spanish-moss tradition — ancient oaks with hanging moss forming a deep green tunnel.",
                "color": "#586A44",
                "prompt": (
                    "A Louisiana Live Oak Mossy Allée at humid golden-hour "
                    "— wide stone-paved path flanked by massive ancient "
                    "live-oak trees draped heavily with Spanish moss "
                    "forming a deep green living tunnel. Distant "
                    "antebellum pavilion at the end. Atmospheric, "
                    "mysterious, southern."
                )
            },
            {
                "id": "allee_ginkgo_golden",
                "label": "Ginkgo Golden Allée",
                "story": "Autumn ginkgo allée — brilliant golden-yellow fan-leaves overhead and fallen carpet below.",
                "color": "#E8C040",
                "prompt": (
                    "A Ginkgo Golden Allée in peak autumn — wide stone-"
                    "paved path flanked by double rows of mature ginkgo "
                    "trees in full autumn gold, brilliant yellow fan-"
                    "leaves forming a luminous canopy overhead and a "
                    "thick golden carpet below. Soft autumn light. "
                    "Magical, luminous, transient."
                )
            }
        ]
    },
    {
        "kind": "streets",
        "slug": "utopic-stream-promenade",
        "id": "utopic_stream_promenade",
        "title": "Stream Promenade",
        "subcategory": "Utopic",
        "aesthetic_category": "utopic",
        "description": (
            "A walking street flanking a shallow freshwater stream, with "
            "stepping stones and narrow stone footbridges at intervals, willows "
            "overhead, fish visible in the clear water, and wading ledges where "
            "children and adults can dip feet. Water sound everywhere. Deep "
            "evolutionary comfort — the street our ancestors chose to camp "
            "along."
        ),
        "tags": ["utopic", "water", "biophilic", "pedestrian", "ancient"],
        "hero_prompt": (
            "A Stream Promenade walking street at late-afternoon — a shallow "
            "clear freshwater stream flowing gently alongside a stone-paved "
            "pedestrian path, willow trees overhanging the water, small stone "
            "stepping-stone crossings. Children wading, adults reading on low "
            "stone benches by the water. Fish visible below. Soft dappled "
            "light through the willows. Warm, timeless, deeply restorative."
        ),
        "suggested_width_m": 15,
        "variants": [
            {
                "id": "stream_alpine_brook",
                "label": "Alpine Brook Promenade",
                "story": "Mountain brook variant — crystal cold glacial stream, larch and pine, rough stone paving.",
                "color": "#6A8896",
                "prompt": (
                    "An Alpine Brook Stream Promenade — a clear cold "
                    "glacial mountain stream tumbling over smooth stones "
                    "alongside a rough stone-paved walking path, flanked "
                    "by larch and pine trees, mountain meadow wildflowers. "
                    "Snow-capped peaks in the distance. Crisp alpine air. "
                    "Serene, restorative."
                )
            },
            {
                "id": "stream_japanese_canal",
                "label": "Japanese Canal Promenade",
                "story": "Japanese canal variant — koi-filled stone-lined canal, stone lanterns, cherry trees overhead.",
                "color": "#A86A8A",
                "prompt": (
                    "A Japanese Canal Stream Promenade — a stone-lined "
                    "shallow canal filled with large orange-and-white "
                    "koi fish alongside a timber-and-stone walking path, "
                    "cherry trees overhead, stone lanterns lit warm at "
                    "intervals. Traditional wooden-shop facades. Soft "
                    "evening light. Serene, beloved."
                )
            },
            {
                "id": "stream_mediterranean_irrigation",
                "label": "Mediterranean Irrigation Canal",
                "story": "Persian/Mediterranean irrigation variant — clear stone-channel water, citrus trees, tiled paving.",
                "color": "#C8A858",
                "prompt": (
                    "A Mediterranean Irrigation Canal Stream Promenade — "
                    "a stone-channel of clear flowing water alongside a "
                    "tiled walking path, flanked by lemon and orange "
                    "trees in fruit, trailing jasmine. Warm golden light. "
                    "Tile-fountain niches. Fragrant, warm, ancient."
                )
            },
            {
                "id": "stream_english_chalk",
                "label": "English Chalk Stream",
                "story": "Chalk-stream variant — crystal clear shallow water, watercress, trout, overhanging willow.",
                "color": "#8AA670",
                "prompt": (
                    "An English Chalk Stream Promenade — a crystal-clear "
                    "shallow chalk stream flowing gently alongside a "
                    "grassy walking path, watercress growing at the "
                    "edges, brown trout visible in the clear water, "
                    "weeping willow overhanging. Soft English summer "
                    "afternoon light. Pastoral, timeless."
                )
            }
        ]
    },
    {
        "kind": "streets",
        "slug": "utopic-starlight-processional",
        "id": "utopic_starlight_processional",
        "title": "Starlight Processional",
        "subcategory": "Utopic",
        "aesthetic_category": "utopic",
        "description": (
            "A night-specific street experience — bioluminescent pavement "
            "seams guiding the way, moon-angled lanterns that don't wash out "
            "the sky, canopy gaps precisely placed to reveal specific star "
            "patterns overhead. Walking the street becomes stargazing. The "
            "sacred night reclaimed for everyday civic life."
        ),
        "tags": ["utopic", "nocturnal", "stargazing", "sacred-night", "dark-sky"],
        "hero_prompt": (
            "A Starlight Processional walking street at deep twilight — a "
            "paved pedestrian path with faint bioluminescent seams marking "
            "the way, soft warm moon-angled lanterns casting gentle pools of "
            "light on the ground but not washing out the sky, strategic gaps "
            "in the tree canopy overhead revealing brilliant star patterns "
            "and the Milky Way. A few strolling figures looking up. Sacred, "
            "quiet, cosmic. Photorealistic night photography."
        ),
        "suggested_width_m": 12,
        "variants": [
            {
                "id": "starlight_northern_aurora",
                "label": "Northern Aurora Processional",
                "story": "High-latitude variant — aurora borealis visible, birch forest, snow underfoot.",
                "color": "#5EB080",
                "prompt": (
                    "A Northern Aurora Starlight Processional — stone-"
                    "paved pedestrian path through a birch forest at "
                    "night, soft warm lanterns casting small warm pools, "
                    "brilliant green-and-magenta aurora borealis "
                    "shimmering above. Snow on the ground. A few figures "
                    "walking, looking up. Sacred, cosmic."
                )
            },
            {
                "id": "starlight_mediterranean_cypress",
                "label": "Mediterranean Cypress Starwalk",
                "story": "Mediterranean variant — dark cypress silhouettes, warm Mediterranean air, visible constellations.",
                "color": "#2A4A5A",
                "prompt": (
                    "A Mediterranean Cypress Starlight Processional — a "
                    "stone-paved path flanked by tall dark cypress tree "
                    "silhouettes, warm amber lanterns at intervals "
                    "lighting low pools on the ground but not the sky. "
                    "Brilliant clear Mediterranean night sky with Orion "
                    "and the Pleiades visible directly above the path. "
                    "Warm night air, scent of rosemary."
                )
            },
            {
                "id": "starlight_desert_milky_way",
                "label": "Desert Milky Way Path",
                "story": "Open desert variant — pale sand path, Milky Way arching overhead, minimal lighting.",
                "color": "#0F1E3A",
                "prompt": (
                    "A Desert Milky Way Starlight Processional — pale "
                    "sand path winding gently through desert dunes, "
                    "small soft warm LED markers along the path edge, "
                    "the brilliant Milky Way arching directly overhead "
                    "in a pristine dark-sky-preserve sky. A single "
                    "figure walking. Cosmic, sacred."
                )
            },
            {
                "id": "starlight_tropical_palm",
                "label": "Tropical Constellation Palm Walk",
                "story": "Tropical variant — palm tree silhouettes, warm humid night, southern hemisphere constellations.",
                "color": "#1A3040",
                "prompt": (
                    "A Tropical Palm Starlight Processional — stone-"
                    "paved path through a grove of tall palm silhouettes "
                    "at night, warm amber lanterns casting low pools of "
                    "light. Southern Cross and southern Milky Way "
                    "visible through gaps in the palm canopy. Warm "
                    "humid tropical night. Magical, sacred."
                )
            }
        ]
    },
]


# ---------------------------------------------------------------------------
# Image generation (identical pipeline to experimental script)
# ---------------------------------------------------------------------------


def generate_image(prompt: str, retries: int = 2) -> bytes | None:
    full_prompt = prompt + STYLE_SUFFIX
    payload = {
        "contents": [{"role": "user", "parts": [{"text": full_prompt}]}],
        "generationConfig": {
            "responseModalities": ["TEXT", "IMAGE"],
            "temperature": 0.7,
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


def generate_archetype_images(arch: dict) -> bool:
    folder = PUBLIC / arch["kind"] / arch["slug"]
    folder.mkdir(parents=True, exist_ok=True)

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
# Catalog entry builders (identical schema to experimental script)
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
    return f'"id": "{arch_id}"' in catalog_path.read_text(encoding="utf-8")


def splice_into_catalog(catalog_path: Path, new_entry: dict) -> None:
    if archetype_already_in_catalog(catalog_path, new_entry["id"]):
        return

    text = catalog_path.read_text(encoding="utf-8")
    close = text.rfind("]")
    if close < 0:
        raise RuntimeError(f"No closing ] in {catalog_path}")
    insertion_point = close
    while insertion_point > 0 and text[insertion_point - 1] in " \t\r\n":
        insertion_point -= 1

    raw = json.dumps(new_entry, indent=4, ensure_ascii=False)
    lines = raw.split("\n")
    indented = lines[0] + "\n" + "\n".join("    " + line for line in lines[1:])
    new_text = text[:insertion_point] + ",\n    " + indented + "\n  " + text[close:]

    json.loads(new_text)  # validate
    catalog_path.write_text(new_text, encoding="utf-8")


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
    print(f"Processing {len(targets)} utopic archetype(s){' (DRY RUN)' if dry_run else ''}")
    print()

    if dry_run:
        for arch in targets:
            print(f"  [{arch['kind']}] {arch['id']}  ({arch['title']}, {len(arch['variants'])} variants)")
        return 0

    successes = 0
    for i, arch in enumerate(targets, 1):
        print(f"[{i}/{len(targets)}] {arch['id']}  ({arch['title']})")
        ok = generate_archetype_images(arch)
        if not ok:
            print(f"    IMAGES FAILED — skipping catalog splice for {arch['id']}")
            continue

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
    print(f"=== Done: {successes}/{len(targets)} utopic archetypes completed ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
