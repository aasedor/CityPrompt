#!/usr/bin/env python3
"""
Generate 12 Mythic Folk archetypes (4 buildings, 4 parks, 4 streets).

Architecture drawing on global folk / mythic resonance — oracle pavilions,
scholar-hermit keeps, moon-gate dwellings, ancestor shrines, faerie rings,
sacred groves, spirit ponds, oracle caves, pilgrim ways, ghost streets,
cunning-woman paths, crossroads shrines. Real typologies that carry the
numinous. Not fantasy kitsch — every archetype draws from a genuine folk
tradition.

Identical pipeline to generate_experimental_archetypes.py etc.
"""

from __future__ import annotations

import base64
import json
import sys
import time
from pathlib import Path
from typing import Any

import httpx

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
    for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("GEMINI_API_KEY="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    sys.exit("ERROR: GEMINI_API_KEY not found")


def gemini_url() -> str:
    return (
        f"https://generativelanguage.googleapis.com/v1beta/"
        f"models/{MODEL}:generateContent?key={load_gemini_key()}"
    )


STYLE_SUFFIX = (
    " Photorealistic documentary photography of a real folk tradition. "
    "Not fantasy illustration, not cartoon. Atmospheric, sacred, numinous. "
    "Cinematic lighting, soft natural atmospherics (mist, dawn, dusk, candlelight). "
    "8K detail, professional ethnographic photography."
)


ARCHETYPES: list[dict[str, Any]] = [
    # ═══════════════ BUILDINGS (4) ═══════════════
    {
        "kind": "buildings",
        "slug": "mythic-oracle-pavilion",
        "id": "mythic_oracle_pavilion",
        "title": "Oracle Pavilion",
        "subcategory": "Mythic",
        "development_type": "institutional",
        "aesthetic_category": "mythic_folk",
        "description": (
            "A small sacred structure built for divination and prophecy across "
            "world folk traditions — Delphic pavilion, Shinto oracle house, "
            "Vedic yajna-kund, West African babalawo consulting hut. The "
            "architecture of asking the unseen for an answer."
        ),
        "tags": ["mythic", "oracle", "sacred", "divination", "folk", "small-scale"],
        "style_profile": {
            "materials": ["carved stone", "aged timber", "woven thatch", "bronze/brass ritual objects", "smoke-stained interior"],
            "facadeRhythm": "Minimal, sculptural, oriented toward cardinal or celestial directions",
            "roofForm": "Peaked or domed with a single ritual opening/finial",
            "frontageType": "Small processional entry with threshold stones",
            "windowStyle": "Narrow slits or single oculus; interior kept dim",
            "massing": "Small (4-8m footprint), single-room, iconic silhouette",
            "heightTendency": "Low (3-6m)",
            "streetRelationship": "Isolated on a sacred ground; approach path from settlement",
            "renderingMood": "Hushed, sacred, liminal, smoke-filled",
            "articulation": "Ritual markers — threshold stones, offering ledges, sacred symbols",
            "publicRealm": "Small ritual precinct around; rest of community keeps distance"
        },
        "prompt_block": {
            "subject": "A small sacred oracle pavilion from a world folk tradition",
            "details": [
                "Small 4-8m footprint, iconic silhouette",
                "Sacred orientation to cardinal direction or sunrise",
                "Minimal but symbolically dense ornament",
                "Threshold markers (stones, ropes, posts)",
                "Offering ledges or altars at or near the entry",
                "Hushed, hazy, sacred atmosphere"
            ]
        },
        "suggested_width_m": 6,
        "suggested_depth_m": 6,
        "min_floors": 1,
        "max_floors": 1,
        "hero_prompt": (
            "A small sacred oracle pavilion at dawn on a sacred ground — a "
            "hushed small-scale structure of aged timber and carved stone, "
            "threshold stones and offering ledges at the entry, a thin "
            "stream of incense smoke rising from within. Pale mist clings "
            "to the ground. A single priestess figure approaching. Sacred, "
            "liminal, timeless."
        ),
        "variants": [
            {
                "id": "oracle_delphi_greek",
                "label": "Delphic Oracle Pavilion",
                "story": "Ancient Greek oracle pavilion at Delphi — carved limestone, laurel-wreathed, a tripod over the chasm, vapors rising.",
                "color": "#C8B896", "min_floors": 1, "max_floors": 1,
                "suggested_floor_height": 4.5, "suggested_area_sqm": 50,
                "prompt": (
                    "A Delphic oracle pavilion at dawn — ancient Greek carved "
                    "limestone tholos with a conical tile roof, laurel wreaths "
                    "at the entry, a bronze tripod inside over a small natural "
                    "rock chasm with faint vapors rising, a priestess (Pythia) "
                    "seated in meditation. Mount Parnassus in the background. "
                    "Pale dawn mist, sacred, ancient."
                ),
                "facade_primary": "carved honey-limestone ashlar",
                "facade_secondary": "fluted Ionic column threshold",
                "facade_ground": "stepped stone plinth with laurel garlands",
                "facade_palette": "honey limestone, deep laurel green, bronze tripod, dawn rose",
                "roof_form": "conical tiled roof with open central oculus",
                "roof_material": "terracotta tiles with bronze finial"
            },
            {
                "id": "oracle_ise_shinto",
                "label": "Ise Shinto Oracle House",
                "story": "Japanese Shinto oracle pavilion — unpainted cypress, thatched roof, shimenawa rope, mirror altar, rebuilt every 20 years.",
                "color": "#CEB882", "min_floors": 1, "max_floors": 1,
                "suggested_floor_height": 4.0, "suggested_area_sqm": 40,
                "prompt": (
                    "A Shinto oracle shrine at dawn — Japanese cypress-wood "
                    "pavilion with unpainted golden-toned timber, thick thatched "
                    "miscanthus-grass roof, thick shimenawa rice-straw rope hung "
                    "across the entrance with white paper shide, a small bronze "
                    "mirror altar visible inside. Cryptomeria forest around. "
                    "Mist, sacred."
                ),
                "facade_primary": "unpainted cypress timber post-and-beam",
                "facade_secondary": "thick shimenawa rope with white paper shide",
                "facade_ground": "raked white gravel plinth with stone threshold",
                "facade_palette": "golden cypress, white rope, dark green cryptomeria",
                "roof_form": "thatched miscanthus-grass roof with chigi crossed finials",
                "roof_material": "thick bundled miscanthus grass thatch"
            },
            {
                "id": "oracle_vedic_yajna",
                "label": "Vedic Yajna Fire Altar",
                "story": "Vedic fire-altar pavilion — brick yajna-kund, sacred fire, Vedic priest pouring ghee, chanted mantras.",
                "color": "#B8601A", "min_floors": 1, "max_floors": 1,
                "suggested_floor_height": 4.0, "suggested_area_sqm": 60,
                "prompt": (
                    "A Vedic yajna fire-altar pavilion at dusk — open-sided "
                    "timber-framed canopy over a central square brick fire-"
                    "altar pit (yajna-kund), a Vedic priest in white dhoti "
                    "pouring ghee onto a leaping sacred fire, smoke rising, "
                    "sanskrit mantras implied. Indian temple setting. Warm "
                    "sacred firelight."
                ),
                "facade_primary": "open timber post-and-beam canopy",
                "facade_secondary": "central square brick yajna-kund fire pit",
                "facade_ground": "stepped stone platform with ritual offerings",
                "facade_palette": "warm brick, sacred fire-orange, timber honey, white cotton",
                "roof_form": "pyramidal thatched canopy with central smoke vent",
                "roof_material": "thatched canopy over timber frame"
            },
            {
                "id": "oracle_yoruba_babalawo",
                "label": "Yoruba Babalawo Consulting Hut",
                "story": "Yoruba diviner's small consulting hut — mud-plastered walls, painted deity figures, palm-nut divination tray.",
                "color": "#8A5228", "min_floors": 1, "max_floors": 1,
                "suggested_floor_height": 3.2, "suggested_area_sqm": 20,
                "prompt": (
                    "A Yoruba babalawo diviner's consulting hut at dusk — small "
                    "mud-plastered walls painted with ochre and white ancestor "
                    "and deity figures, a thatched palm roof, a seated diviner "
                    "inside with a carved wooden opon-Ifa divination tray and "
                    "sacred palm nuts. Small offerings of kola nuts at the door. "
                    "Warm West African evening, sacred."
                ),
                "facade_primary": "ochre mud-plastered walls with painted deity figures",
                "facade_secondary": "thatched palm-leaf roof with bamboo ridge",
                "facade_ground": "packed earth threshold with offering stones",
                "facade_palette": "ochre, white, terracotta, warm palm thatch",
                "roof_form": "conical palm-thatch roof",
                "roof_material": "woven palm-leaf thatch"
            }
        ]
    },
    {
        "kind": "buildings",
        "slug": "mythic-bardic-keep",
        "id": "mythic_bardic_keep",
        "title": "Bardic Keep / Scholar's Tower",
        "subcategory": "Mythic",
        "development_type": "institutional",
        "aesthetic_category": "mythic_folk",
        "description": (
            "The hermit scholar's or bard's keep — a solitary tower or "
            "roundhouse where knowledge-keepers live. Dense with books, "
            "scrolls, instruments, astronomical tools, brewing potions or "
            "quipu knots. Folk-cultural cousin to the wizard-archetype. "
            "Isolated by choice."
        ),
        "tags": ["mythic", "scholar", "bard", "hermit", "tower", "knowledge-keeper"],
        "style_profile": {
            "materials": ["stacked stone", "aged timber beams", "parchment and ink", "leather-bound books", "bronze instruments"],
            "facadeRhythm": "Vertical narrow windows, thick walls, single winding stair visible externally",
            "roofForm": "Steep conical or pitched roof with observation platform or cupola",
            "frontageType": "Heavy wooden door at the base, lock and inscribed threshold",
            "windowStyle": "Narrow arrow-slit or arched windows, few in number",
            "massing": "Slender tall 3-5 storey tower, 8-12m square, 15-25m tall",
            "heightTendency": "Mid (15-25m)",
            "streetRelationship": "Isolated on a hill, ridge, or edge of settlement",
            "renderingMood": "Reclusive, weathered, full of accumulated knowledge, candle-lit",
            "articulation": "Weathered stone, moss, ivy; interior visibly dense with scrolls/books through windows",
            "publicRealm": "Modest garden at the base; footpath from distant village"
        },
        "prompt_block": {
            "subject": "A solitary scholar's tower or bard's keep on a hill at dusk",
            "details": [
                "Slender 3-5 storey tower, 15-25m tall",
                "Narrow arched or slit windows with warm candle-light glow",
                "Weathered stone with moss or ivy",
                "Single heavy wooden door at the base",
                "Steep conical or pitched roof with observation cupola",
                "Isolated on a hill or ridge"
            ]
        },
        "suggested_width_m": 10,
        "suggested_depth_m": 10,
        "min_floors": 3,
        "max_floors": 6,
        "hero_prompt": (
            "A Bardic Keep scholar's tower on a quiet hilltop at dusk — "
            "slender 4-storey weathered stone tower with narrow arched "
            "windows glowing warm amber from candles inside, mossy stone "
            "base, a heavy wooden door at the ground. Conical slate roof "
            "with a small observation cupola. A single figure visible in "
            "the uppermost window with a telescope. Purple-indigo twilight, "
            "first stars appearing. Silent, ancient, full of secrets."
        ),
        "variants": [
            {
                "id": "bardic_tuscan_astronomer",
                "label": "Tuscan Astronomer's Tower",
                "story": "Renaissance Italian hermit astronomer's stone tower in the Tuscan countryside — telescope, astrolabes, vineyard below.",
                "color": "#B8956A", "min_floors": 3, "max_floors": 5,
                "suggested_floor_height": 4.2, "suggested_area_sqm": 80,
                "prompt": (
                    "A Tuscan Renaissance astronomer's stone tower at dusk — "
                    "slender 4-storey rough-hewn warm-beige limestone tower "
                    "with narrow arched windows, set on a cypress-lined Tuscan "
                    "hilltop, vineyard terraces descending below. A telescope "
                    "visible through the top window. Warm amber candlelight "
                    "from within. Purple evening sky, Renaissance scholarly."
                ),
                "facade_primary": "rough-hewn warm-beige limestone ashlar",
                "facade_secondary": "narrow arched windows with stone reveals",
                "facade_ground": "heavy oak door with iron hinges on stone threshold",
                "facade_palette": "warm beige limestone, moss green, cypress dark, amber window glow",
                "roof_form": "low conical terracotta-tile roof with observation platform",
                "roof_material": "terracotta tiles with brass astrolabe finial"
            },
            {
                "id": "bardic_celtic_roundhouse",
                "label": "Celtic Bardic Roundhouse",
                "story": "Iron Age Celtic bard's roundhouse — drystone walls, thatched conical roof, carved spiral triskeles, harp inside.",
                "color": "#7A6B48", "min_floors": 1, "max_floors": 2,
                "suggested_floor_height": 4.0, "suggested_area_sqm": 100,
                "prompt": (
                    "A Celtic bardic roundhouse at twilight on a misty heath — "
                    "circular drystone-walled structure, thatched conical roof "
                    "with smoke-hole, carved triple-spiral triskele symbols on "
                    "the stones, warm amber firelight through the small "
                    "entrance revealing a harp inside, mossy hillside. Pale "
                    "green-grey mist, sacred, ancient."
                ),
                "facade_primary": "drystone rough-fitted circular walls",
                "facade_secondary": "carved spiral triskele stones at the entry",
                "facade_ground": "threshold stones with moss and heather",
                "facade_palette": "weathered grey stone, moss green, heather purple, amber firelight",
                "roof_form": "conical thatched roof with central smoke-hole",
                "roof_material": "thick heather-and-reed thatch"
            },
            {
                "id": "bardic_silk_road_madrasah",
                "label": "Silk Road Madrasah-Tower",
                "story": "Central Asian madrasah-tower — brick minaret with ornate turquoise tile, calligraphy, stacked manuscripts.",
                "color": "#3A7A9A", "min_floors": 4, "max_floors": 6,
                "suggested_floor_height": 4.5, "suggested_area_sqm": 90,
                "prompt": (
                    "A Silk Road madrasah-tower at dusk — slender 5-storey "
                    "brick minaret with intricate turquoise and deep-blue "
                    "geometric tilework, calligraphic Quranic bands, small "
                    "arched balconies at each level. Central Asian desert "
                    "oasis setting, palm trees and a small caravanserai at "
                    "the base. Warm amber window glow. Dusty sacred evening."
                ),
                "facade_primary": "fired-brick masonry with turquoise geometric tilework",
                "facade_secondary": "calligraphic Quranic bands and deep-blue tile accents",
                "facade_ground": "arched stone portal with scholar's threshold inscription",
                "facade_palette": "warm brick, turquoise tile, lapis blue, gold calligraphy, amber",
                "roof_form": "tapered minaret crown with small cupola and crescent",
                "roof_material": "glazed tile cupola with ornamental crescent"
            },
            {
                "id": "bardic_andean_quipu",
                "label": "Andean Quipu-Keeper's House",
                "story": "Inca-precision stone house for a quipucamayoc — fitted polygonal stones, woven knot-records, high-altitude altiplano.",
                "color": "#6A5A46", "min_floors": 1, "max_floors": 2,
                "suggested_floor_height": 3.2, "suggested_area_sqm": 70,
                "prompt": (
                    "An Andean quipu-keeper's stone house at dawn on the "
                    "altiplano — precisely fitted polygonal Inca stonework, "
                    "small thatched roof, a doorway revealing hundreds of "
                    "hanging coloured and knotted quipu cords inside. A "
                    "quipucamayoc in traditional dress working at the "
                    "entrance. Distant snow peaks, thin clear air."
                ),
                "facade_primary": "precisely fitted polygonal Inca stone masonry",
                "facade_secondary": "thatched ichu-grass roof",
                "facade_ground": "stone-paved threshold with offering bundles",
                "facade_palette": "weathered grey polygonal stone, warm thatch, distant snow white",
                "roof_form": "low thatched gabled roof",
                "roof_material": "ichu-grass thatch"
            }
        ]
    },
    {
        "kind": "buildings",
        "slug": "mythic-moon-gate-dwelling",
        "id": "mythic_moon_gate_dwelling",
        "title": "Moon-Gate Dwelling",
        "subcategory": "Mythic",
        "development_type": "residential_single_family",
        "aesthetic_category": "mythic_folk",
        "description": (
            "A dwelling whose primary architectural gesture is a perfectly "
            "circular 'moon-gate' entrance opening into an inner garden. "
            "Walking through the moon-gate is the daily crossing from "
            "public to private, mundane to sacred. Asian folk tradition: "
            "Chinese scholars' gardens, Korean hanok, Japanese teahouse "
            "tsukimi gardens."
        ),
        "tags": ["mythic", "moon-gate", "asian", "garden", "threshold", "contemplative"],
        "style_profile": {
            "materials": ["whitewashed lime or grey brick", "aged timber", "glazed clay tile", "polished stone paving", "moss and bamboo"],
            "facadeRhythm": "Dominant circular moon-gate in a long street wall; rest is quiet solid wall",
            "roofForm": "Low tile roof with upturned eaves over the moon-gate only",
            "frontageType": "Unbroken garden wall with a single circular opening",
            "windowStyle": "None on the street facade; all windows face inward to the garden",
            "massing": "Walled compound 15-25m square; main dwelling 1-2 storey inside",
            "heightTendency": "Low (1-2 storeys visible over the wall)",
            "streetRelationship": "Blank wall with a single dramatic circular opening",
            "renderingMood": "Contemplative, threshold-aware, inner-world-revealing",
            "articulation": "Moon-gate is THE articulation; walls are quiet",
            "publicRealm": "Narrow quiet lane outside; inner garden glimpsed through the gate"
        },
        "prompt_block": {
            "subject": "A dwelling's exterior wall dominated by a perfectly circular moon-gate",
            "details": [
                "Long quiet whitewashed or grey-brick wall",
                "Single perfect circular moon-gate 2.5-3m diameter",
                "Small roof with upturned eaves over the gate",
                "Garden visible through the gate (bamboo, stone, pond)",
                "Stepping stones leading into the garden",
                "Quiet narrow lane outside"
            ]
        },
        "suggested_width_m": 20,
        "suggested_depth_m": 15,
        "min_floors": 1,
        "max_floors": 2,
        "hero_prompt": (
            "A Moon-Gate Dwelling exterior wall at late-afternoon golden "
            "hour — a long quiet whitewashed wall with a single perfect "
            "circular moon-gate opening framed in dark grey stone, a small "
            "tile roof with upturned eaves above the gate. Through the gate "
            "visible: a garden with bamboo, a stepping-stone path, a still "
            "reflecting pool. A narrow stone lane in the foreground with "
            "moss. Warm golden light, quiet, sacred threshold."
        ),
        "variants": [
            {
                "id": "moongate_chinese_scholar",
                "label": "Chinese Scholar's Garden",
                "story": "Suzhou-style scholar's garden — whitewashed wall, dark-tiled moon-gate, inside a pond with rocks, pavilions, penjing.",
                "color": "#E8E4DA", "min_floors": 1, "max_floors": 2,
                "suggested_floor_height": 3.8, "suggested_area_sqm": 300,
                "prompt": (
                    "A Chinese Suzhou-style scholar's garden moon-gate at late "
                    "afternoon — long whitewashed exterior wall with a perfect "
                    "circular moon-gate edged in dark grey stone. Through the "
                    "gate visible: a scholar's garden with a still pond, "
                    "weathered scholar-stones, a small tile-roofed pavilion, "
                    "bamboo, a dwarf pine penjing. Stepping-stone path. "
                    "Golden hour, deeply contemplative."
                ),
                "facade_primary": "whitewashed lime-plaster wall",
                "facade_secondary": "dark grey stone moon-gate frame with carved lintel",
                "facade_ground": "stone-paved lane with mossy edges",
                "facade_palette": "whitewashed wall, dark grey stone, bamboo green, pond slate-blue",
                "roof_form": "tile roof with upturned eaves over the gate",
                "roof_material": "dark grey clay tile roofing"
            },
            {
                "id": "moongate_korean_hanok",
                "label": "Korean Hanok Moon-Gate",
                "story": "Korean hanok variant — earthen-brick wall, curved tile roof, inside an ondol-heated hanok with paper screens.",
                "color": "#D8C4A6", "min_floors": 1, "max_floors": 1,
                "suggested_floor_height": 3.4, "suggested_area_sqm": 280,
                "prompt": (
                    "A Korean hanok moon-gate at dusk — earthen-yellow brick "
                    "wall with a perfect circular moon-gate framed in dark "
                    "stone, curved tile roof with strongly upturned eaves "
                    "above. Through the gate visible: a traditional hanok "
                    "with white hanji paper shoji screens glowing warm amber, "
                    "a wooden veranda, stepping stones, pine tree. Warm "
                    "evening."
                ),
                "facade_primary": "earthen-yellow brick wall",
                "facade_secondary": "dark grey stone moon-gate frame",
                "facade_ground": "stone-paved lane with pine needles",
                "facade_palette": "earthen yellow, dark grey stone, warm hanji amber, pine green",
                "roof_form": "curved tile roof with upturned eaves",
                "roof_material": "grey clay tile with ridge ornament"
            },
            {
                "id": "moongate_japanese_tsukimi",
                "label": "Japanese Tsukimi Teahouse",
                "story": "Japanese moon-viewing teahouse variant — bamboo wall, small stone moon-gate, inside a moss garden with a tea pavilion.",
                "color": "#A2A876", "min_floors": 1, "max_floors": 1,
                "suggested_floor_height": 3.0, "suggested_area_sqm": 150,
                "prompt": (
                    "A Japanese tsukimi moon-viewing teahouse moon-gate at "
                    "dusk — low bamboo-and-plaster wall with a small stone "
                    "moon-gate. Through it visible: a moss garden with "
                    "stepping-stones, a small thatched teahouse with shoji "
                    "screens glowing warm, a full moon rising above. Serene, "
                    "contemplative."
                ),
                "facade_primary": "bamboo-and-plaster wall",
                "facade_secondary": "rough-hewn stone moon-gate frame",
                "facade_ground": "mossy stone-paved threshold",
                "facade_palette": "bamboo yellow-green, rough stone, deep moss, warm shoji amber, moon silver",
                "roof_form": "thatched teahouse roof visible inside",
                "roof_material": "miscanthus-grass thatch"
            },
            {
                "id": "moongate_zen_monastic",
                "label": "Zen Monastic Cell Moon-Gate",
                "story": "Austere Zen monastic variant — stark grey wall, small moon-gate, inside a single monk's raked-gravel garden.",
                "color": "#B8B8B8", "min_floors": 1, "max_floors": 1,
                "suggested_floor_height": 3.2, "suggested_area_sqm": 120,
                "prompt": (
                    "A Zen monastic cell moon-gate at dawn — stark grey stone "
                    "wall with a small perfect circular moon-gate. Through it "
                    "visible: a raked gravel garden with three thoughtful "
                    "stones, a single small austere timber monastic cell, a "
                    "pine. Pre-dawn pale light. Absolute serenity."
                ),
                "facade_primary": "stark grey stone or rendered wall",
                "facade_secondary": "plain smooth moon-gate frame",
                "facade_ground": "stone-paved minimal threshold",
                "facade_palette": "cool grey, pale gravel, dark pine green, dawn rose",
                "roof_form": "low shingled roof (monastic cell visible inside)",
                "roof_material": "weathered cedar shingle"
            }
        ]
    },
    {
        "kind": "buildings",
        "slug": "mythic-ancestor-shrine-house",
        "id": "mythic_ancestor_shrine_house",
        "title": "Ancestor Shrine House",
        "subcategory": "Mythic",
        "development_type": "residential_single_family",
        "aesthetic_category": "mythic_folk",
        "description": (
            "A family home with an integrated ancestor shrine — not a "
            "separate chapel, but a room, wall, or altar where the "
            "ancestors dwell and are daily consulted. Across Chinese, "
            "Yoruba, Māori, Balinese folk traditions. The house IS the "
            "family; the ancestors ARE the family."
        ),
        "tags": ["mythic", "ancestor", "shrine", "family-home", "sacred", "lineage"],
        "style_profile": {
            "materials": ["carved timber", "lacquered surfaces", "painted walls", "brass or bronze altar objects", "incense"],
            "facadeRhythm": "Dwelling facade expresses the family's lineage externally",
            "roofForm": "Tiered or layered, often with ancestor-totem finial",
            "frontageType": "Ceremonial entry with threshold markings",
            "windowStyle": "Varies by tradition; shrine area often has its own special window",
            "massing": "Family compound or single house, 1-3 storeys",
            "heightTendency": "Low to mid (1-3 storeys)",
            "streetRelationship": "Street presence formal; ancestors announce the family to the neighbourhood",
            "renderingMood": "Lineage-rooted, incense-hazed, warm, honoured",
            "articulation": "Carved ancestor images, lineage markings, offering niches",
            "publicRealm": "Threshold / front court for ceremonial receptions"
        },
        "prompt_block": {
            "subject": "A family home with integrated ancestor shrine from a world folk tradition",
            "details": [
                "Family dwelling 1-3 storey",
                "Ancestor shrine or altar as prominent architectural feature",
                "Traditional culturally-specific ornament",
                "Offering niches, incense, lineage markers",
                "Threshold with culturally-specific markings",
                "Family activity visible"
            ]
        },
        "suggested_width_m": 20,
        "suggested_depth_m": 25,
        "min_floors": 1,
        "max_floors": 3,
        "hero_prompt": (
            "A Chinese ancestral spirit-tablet family hall at evening — "
            "traditional courtyard home with deep red lacquered doors and "
            "gilded carved wooden panels, a central family hall visible "
            "through open doors containing an ornate ancestor altar with "
            "dozens of gilded wooden spirit tablets, lit candles, offerings "
            "of fruit and incense bowls smoking. Family figures in "
            "traditional dress visible. Warm evening, sacred."
        ),
        "variants": [
            {
                "id": "ancestor_chinese_tablet",
                "label": "Chinese Spirit-Tablet Hall",
                "story": "Traditional Chinese siheyuan family courtyard with central ancestral hall — spirit tablets, offerings, incense.",
                "color": "#B82A2A", "min_floors": 1, "max_floors": 2,
                "suggested_floor_height": 4.0, "suggested_area_sqm": 400,
                "prompt": (
                    "A Chinese siheyuan family courtyard home at dusk — "
                    "traditional Beijing-style courtyard with red lacquered "
                    "doors and gilded wood panels, a central ancestral hall "
                    "visible through open doors, an ornate altar with dozens "
                    "of gilded wooden spirit tablets, candles, incense, "
                    "offerings. Curved grey tile roof with ridge ornament. "
                    "Family in traditional dress. Warm sacred evening."
                ),
                "facade_primary": "deep red lacquered timber doors and wall panels",
                "facade_secondary": "gilded carved wooden ornamental panels",
                "facade_ground": "stone-paved courtyard with offering altar",
                "facade_palette": "lacquer red, gold leaf, dark grey roof tile, warm candle amber",
                "roof_form": "curved grey tile roof with ridge dragon ornament",
                "roof_material": "dark grey clay tile with glazed ridge figures"
            },
            {
                "id": "ancestor_yoruba_egungun",
                "label": "Yoruba Egungun Shrine Home",
                "story": "Yoruba compound with egungun ancestor shrine — mud-walled with painted ancestor figures, carved masks resting.",
                "color": "#B05828", "min_floors": 1, "max_floors": 1,
                "suggested_floor_height": 3.2, "suggested_area_sqm": 220,
                "prompt": (
                    "A Yoruba family compound with egungun ancestor shrine at "
                    "dusk — mud-plastered walls painted with stylised ancestor "
                    "figures in white and ochre, a thatched palm roof, a "
                    "central ritual space with carved wooden ancestor masks "
                    "resting on earthen shelves, beaded offerings, a small "
                    "fire. Warm West African evening, sacred."
                ),
                "facade_primary": "ochre mud-plastered walls painted with ancestor figures",
                "facade_secondary": "carved wooden ancestor mask niches",
                "facade_ground": "packed-earth threshold with offering bowls",
                "facade_palette": "ochre, white painted figures, warm thatch, deep shadows",
                "roof_form": "conical thatched palm-leaf roof",
                "roof_material": "woven palm-leaf thatch over timber rafters"
            },
            {
                "id": "ancestor_maori_wharenui",
                "label": "Māori Wharenui Meeting House",
                "story": "Māori carved meeting house — totemic ancestor figure carved into the gable, paua-shell eyes, communal dwelling.",
                "color": "#5A3020", "min_floors": 1, "max_floors": 1,
                "suggested_floor_height": 4.5, "suggested_area_sqm": 250,
                "prompt": (
                    "A Māori carved wharenui meeting house at evening — "
                    "traditional long wooden house with a towering carved "
                    "ancestor figure on the gable, paua-shell inlaid eyes "
                    "glinting, elaborate carved rafter ends and porch "
                    "posts, dark red ochre paint with black and white "
                    "patterns. Communal ground in front. Warm evening, "
                    "sacred, ancestral."
                ),
                "facade_primary": "carved timber gable with towering ancestor figure",
                "facade_secondary": "paua-shell inlaid eyes and red-ochre painted panels",
                "facade_ground": "ceremonial carved threshold posts",
                "facade_palette": "deep red ochre, black, white, warm paua iridescence, dark timber",
                "roof_form": "long gabled roof with carved ridge-beam and gable figures",
                "roof_material": "traditional thatched or contemporary shingle roof"
            },
            {
                "id": "ancestor_balinese_pura",
                "label": "Balinese Pura Keluarga",
                "story": "Balinese family temple compound — tiered meru shrines, carved stone gates, daily offerings.",
                "color": "#8A6A38", "min_floors": 1, "max_floors": 1,
                "suggested_floor_height": 4.0, "suggested_area_sqm": 200,
                "prompt": (
                    "A Balinese Pura Keluarga family temple at dawn — "
                    "traditional compound with a split candi bentar gate of "
                    "carved volcanic grey stone, multiple tiered meru shrine "
                    "towers with thatched roofs in the inner courtyard, "
                    "frangipani trees, small canang sari offerings on every "
                    "threshold. Pale tropical dawn light, sacred."
                ),
                "facade_primary": "carved volcanic grey stone temple walls and gates",
                "facade_secondary": "tiered meru shrines with thatched roofs",
                "facade_ground": "stone-paved threshold with canang sari offerings",
                "facade_palette": "volcanic grey stone, warm thatch, frangipani white-yellow, offering-leaf green",
                "roof_form": "tiered meru with 3-11 stacked thatched tiers",
                "roof_material": "black ijuk (sugar-palm fibre) thatch"
            }
        ]
    },

    # ═══════════════ OPENSPACES (4) ═══════════════
    {
        "kind": "openspaces",
        "slug": "mythic-faerie-ring-meadow",
        "id": "mythic_faerie_ring_meadow",
        "title": "Faerie Ring Meadow",
        "subcategory": "Mythic",
        "aesthetic_category": "mythic_folk",
        "space_type": "park",
        "description": (
            "A wildflower meadow with a naturally formed or ritually "
            "maintained ring of stones, mushrooms, or trees at its heart. "
            "Across European folk traditions, such rings are thresholds to "
            "the otherworld. A place of quiet awe, ritual offerings, and "
            "the feeling of being watched kindly."
        ),
        "tags": ["mythic", "faerie-ring", "meadow", "threshold", "otherworld", "folk-european"],
        "hero_prompt": (
            "A Faerie Ring Meadow at dawn mist — a wide wildflower meadow "
            "with a perfect natural ring of small mushrooms or standing "
            "stones at its centre, an ancient lichen-covered tree beside it, "
            "mist clinging to the grass. Soft pale pink-grey dawn light. "
            "Small offerings of flowers at the ring's edge. Sacred, liminal, "
            "threshold to otherworld."
        ),
        "suggested_width_m": 80,
        "suggested_depth_m": 80,
        "suggested_area_sqm": 6400,
        "variants": [
            {
                "id": "faerie_celtic_mushroom",
                "label": "Celtic Mushroom Ring",
                "story": "Irish/Scottish faerie ring — perfect circle of red-capped fly agaric mushrooms in a mossy clearing, misty dawn.",
                "color": "#B24A38",
                "prompt": (
                    "A Celtic faerie mushroom ring at misty dawn — a perfect "
                    "natural circle of red-and-white spotted fly agaric "
                    "mushrooms on a mossy forest-clearing floor, surrounded by "
                    "emerald ferns and ancient mossy stones. Pale ethereal "
                    "dawn mist drifting through. Magical, liminal, threshold-"
                    "feeling."
                )
            },
            {
                "id": "faerie_scandinavian_stone",
                "label": "Scandinavian Stone Ring",
                "story": "Nordic folk stone ring — ring of weathered lichen-covered standing stones in a heather meadow, white sky.",
                "color": "#A0A0A0",
                "prompt": (
                    "A Nordic faerie stone ring meadow at soft overcast noon — "
                    "a ring of nine weathered grey standing stones with "
                    "orange-and-green lichen, set in a heather-and-birch-"
                    "grass meadow. A single juniper bush. Pale Scandinavian "
                    "light, silent, ancient, sacred."
                )
            },
            {
                "id": "faerie_slavic_birch",
                "label": "Slavic Birch-Circle Ring",
                "story": "Slavic folk ring — circle of young white birch trees with red ribbons tied to branches, offering stones.",
                "color": "#E8E4D0",
                "prompt": (
                    "A Slavic faerie birch-circle meadow at golden hour — a "
                    "ring of 12 young white birch trees with their black-"
                    "marked bark, red and white folk ribbons tied to the "
                    "branches, a flat offering stone at the centre with "
                    "bread and an apple. Tall grasses around. Magical, "
                    "folk-ritual."
                )
            },
            {
                "id": "faerie_basque_oak",
                "label": "Basque Oak-Ring",
                "story": "Basque folk oak ring — ancient oak trees forming a ring around a flat stone altar, mountain mist.",
                "color": "#6A7A4A",
                "prompt": (
                    "A Basque oak-ring meadow in mountain mist — seven "
                    "ancient moss-covered oak trees forming a ring, their "
                    "canopies touching overhead, a flat rough-hewn granite "
                    "altar stone at the centre with small offerings. Mist, "
                    "ferns, Pyrenees slopes visible. Sacred, ancient, "
                    "pre-Christian."
                )
            }
        ]
    },
    {
        "kind": "openspaces",
        "slug": "mythic-sacred-grove",
        "id": "mythic_sacred_grove",
        "title": "Sacred Grove",
        "subcategory": "Mythic",
        "aesthetic_category": "mythic_folk",
        "space_type": "park",
        "description": (
            "An ancient forest grove considered sacred — Greek groves of the "
            "muses, Druid oak groves, Shinto forest shrines, Baltic sacred "
            "oaks. Walking the paths is a ritual act. The grove is older "
            "than the settlement; the settlement grew up around it."
        ),
        "tags": ["mythic", "grove", "sacred", "forest", "ritual", "ancient-tree"],
        "hero_prompt": (
            "A Sacred Grove at dawn mist — ancient tall-canopied trees "
            "with moss-covered trunks forming a dappled green chamber, a "
            "narrow stone-paved path winding through, small stone offerings "
            "at the base of one great tree, pale dawn shafts of light "
            "filtering through the canopy. Sacred, hushed, ancient."
        ),
        "suggested_width_m": 100,
        "suggested_depth_m": 100,
        "suggested_area_sqm": 10000,
        "variants": [
            {
                "id": "grove_greek_asphodel",
                "label": "Greek Asphodel Grove",
                "story": "Greek mythic grove — cypress and pine, asphodel wildflowers, ancient weathered stelae, Apollo's grove.",
                "color": "#6A8A5E",
                "prompt": (
                    "A Greek sacred grove at morning — tall cypress and "
                    "Aleppo pine trees, a meadow of pale asphodel and poppies, "
                    "ancient weathered marble stelae with Greek inscriptions, "
                    "a small altar-stone at the centre. Golden Mediterranean "
                    "morning light, sacred, classical, ancient."
                )
            },
            {
                "id": "grove_druid_oak",
                "label": "Druid Oak Grove",
                "story": "Druidic oak grove — giant ancient oaks, hanging mistletoe, Celtic altar-stone, mossy floor.",
                "color": "#4A6A3A",
                "prompt": (
                    "A Druid oak grove at atmospheric dawn mist — giant "
                    "ancient moss-covered oak trees with hanging mistletoe, "
                    "a ritual stone altar with a bronze sickle at the centre, "
                    "a robed druid figure approaching, mossy forest floor "
                    "with bluebells. Green misty light, sacred, ancient, "
                    "Celtic."
                )
            },
            {
                "id": "grove_shinto_forest",
                "label": "Shinto Forest Shrine",
                "story": "Japanese Shinto sacred grove — towering cryptomeria, vermilion torii gate, moss-covered stone steps.",
                "color": "#C92A2A",
                "prompt": (
                    "A Shinto sacred grove at soft dawn — towering Japanese "
                    "cryptomeria trees, a vermilion-red torii gate standing "
                    "at the entrance to a moss-covered stone step path, a "
                    "small wooden shrine visible deeper in the forest with "
                    "a shimenawa rope. Misty, sacred, hushed."
                )
            },
            {
                "id": "grove_baltic_oak",
                "label": "Baltic Sacred Oak",
                "story": "Baltic sacred oak — single monumental ancient oak, amber and honey offerings at base, pre-Christian.",
                "color": "#8A6A42",
                "prompt": (
                    "A Baltic sacred oak tree at golden hour — a single "
                    "monumental ancient oak tree, 20 meters tall with a "
                    "massive gnarled trunk, set in a meadow clearing. "
                    "Small wooden bowls of amber and honey at the base as "
                    "offerings, red wool ribbons tied to low branches. "
                    "Warm golden light, sacred, pagan-ancient."
                )
            }
        ]
    },
    {
        "kind": "openspaces",
        "slug": "mythic-dragon-spirit-pond",
        "id": "mythic_dragon_spirit_pond",
        "title": "Dragon-Spirit Pond",
        "subcategory": "Mythic",
        "aesthetic_category": "mythic_folk",
        "space_type": "park",
        "description": (
            "A body of water associated with folkloric dragons, serpents, "
            "nagas, or water-spirits. Chinese dragon pools, Welsh afanc "
            "lakes, Indian naga tanks, Japanese water-kami ponds. A place "
            "of small offerings and careful respect."
        ),
        "tags": ["mythic", "water", "dragon", "naga", "spirit", "offering"],
        "hero_prompt": (
            "A Dragon-Spirit Pond at dusk mist — a still dark pond "
            "surrounded by ancient stones and willows, a carved dragon "
            "spout at the water's edge releasing a trickle, mist rising "
            "from the water's surface, a small wooden offering platform "
            "with incense bowls. Deep green-blue water, sacred, mysterious."
        ),
        "suggested_width_m": 60,
        "suggested_depth_m": 60,
        "suggested_area_sqm": 3600,
        "variants": [
            {
                "id": "dragon_pond_chinese",
                "label": "Chinese Dragon Pool",
                "story": "Chinese imperial dragon pool — carved stone dragon spout, koi, zigzag bridge, pagoda pavilion.",
                "color": "#C8A03A",
                "prompt": (
                    "A Chinese imperial Dragon Pool at golden hour — a "
                    "circular stone-edged pond with a carved stone dragon "
                    "spout releasing a stream of water, large orange and "
                    "white koi visible in the clear water, a zigzag red "
                    "wooden bridge, a small pagoda-roofed pavilion beside "
                    "the pond, ginkgo trees. Sacred, classical Chinese."
                )
            },
            {
                "id": "dragon_pond_welsh_afanc",
                "label": "Welsh Afanc Lake",
                "story": "Welsh folkloric afanc lake — dark mountain tarn, mist, single solitary rune-stone at the water's edge.",
                "color": "#3E4A56",
                "prompt": (
                    "A Welsh folkloric afanc lake at misty dawn — a dark "
                    "still mountain tarn surrounded by rocky slopes, a "
                    "single solitary weathered stone with faint carved runes "
                    "at the water's edge, a small rowan tree nearby, rolling "
                    "mist. Atmospheric, mysterious, mythic, Welsh."
                )
            },
            {
                "id": "dragon_pond_indian_naga",
                "label": "Indian Naga Tank",
                "story": "South Indian stepped naga tank — carved stone serpent guardians at the corners, lotus blooms, ancient steps.",
                "color": "#9A6A3A",
                "prompt": (
                    "A South Indian naga temple tank at morning — square "
                    "stepped stone tank descending to still green-blue water, "
                    "carved stone naga serpent guardians rising at the four "
                    "corners, pink lotus blooms floating on the water, a "
                    "small granite stepped shrine. Warm morning light, "
                    "sacred, ancient Indian."
                )
            },
            {
                "id": "dragon_pond_japanese_kami",
                "label": "Japanese Water-Kami Pond",
                "story": "Japanese Shinto water-kami pond — small vermilion torii standing in the water, koi, shrine pavilion.",
                "color": "#E2382A",
                "prompt": (
                    "A Japanese Shinto water-kami pond at dusk — a small "
                    "vermilion-red torii gate standing directly in the "
                    "still green-gold pond water, koi fish visible below, "
                    "a small wooden shrine pavilion on the bank, hanging "
                    "paper shide streamers. Deep evergreen forest around. "
                    "Sacred, magical."
                )
            }
        ]
    },
    {
        "kind": "openspaces",
        "slug": "mythic-oracle-cave",
        "id": "mythic_oracle_cave",
        "title": "Oracle Cave / Spirit Hollow",
        "subcategory": "Mythic",
        "aesthetic_category": "mythic_folk",
        "space_type": "park",
        "description": (
            "A natural hollow, cave, or ritual passage-mound used for "
            "prophecy or spirit-contact. Delphi's chasm, West African "
            "ancestor caves, Celtic sidhe mounds, Andean chullpa tomb-caves. "
            "A place where the living cross into dialogue with the unseen."
        ),
        "tags": ["mythic", "cave", "oracle", "threshold", "ancestor", "liminal"],
        "hero_prompt": (
            "An Oracle Cave entrance at dawn mist — a dark natural stone "
            "cave opening in a mossy cliff face, ritual offerings of "
            "flowers and small clay bowls at the threshold, a narrow "
            "stone path approaching, ancient weathered symbols carved in "
            "the rock nearby. Pale dawn light, mysterious, sacred."
        ),
        "suggested_width_m": 40,
        "suggested_depth_m": 30,
        "suggested_area_sqm": 1200,
        "variants": [
            {
                "id": "oracle_cave_delphi",
                "label": "Delphi Chasm",
                "story": "Ancient Greek Delphi oracle chasm — narrow mountain cleft with laurel trees, marble omphalos stone, rising vapors.",
                "color": "#B8AA8A",
                "prompt": (
                    "The Delphi oracle chasm at dawn — narrow limestone "
                    "mountain cleft with laurel trees, a carved marble "
                    "omphalos stone at the threshold, faint pale vapors "
                    "rising from the cleft, ancient Greek columns on the "
                    "hillside above, Mount Parnassus. Sacred classical."
                )
            },
            {
                "id": "oracle_cave_yoruba_ancestor",
                "label": "Yoruba Ancestor Cave",
                "story": "West African ancestor cave — painted stylized figures at the entrance, sacred objects, offerings, dusty light.",
                "color": "#B06A30",
                "prompt": (
                    "A West African ancestor cave at dusk — rough stone "
                    "cave entrance painted with white and ochre stylized "
                    "ancestor figures, carved wooden mask-objects and "
                    "beaded offerings on stone shelves at the threshold, "
                    "a small pot of palm oil. Warm dusty African evening, "
                    "sacred."
                )
            },
            {
                "id": "oracle_cave_celtic_sidhe",
                "label": "Celtic Sidhe Mound",
                "story": "Irish neolithic passage-mound sidhe — grass-covered earthen mound with stone passage entry, Celtic spirals.",
                "color": "#4A6A3A",
                "prompt": (
                    "A Celtic sidhe passage-mound at dawn mist — grass-"
                    "covered earthen burial mound with a stone passage "
                    "entrance, ancient carved spiral triskele symbols on "
                    "the entrance stone, offerings of hazelnuts and milk, "
                    "mist drifting across the green Irish countryside. "
                    "Sacred, threshold."
                )
            },
            {
                "id": "oracle_cave_andean_chullpa",
                "label": "Andean Chullpa Tomb-Cave",
                "story": "Andean chullpa ancestor tomb — stone burial tower cut into cliff face, mummified ancestors, altiplano setting.",
                "color": "#8A6A52",
                "prompt": (
                    "An Andean chullpa ancestor tomb on an altiplano cliff — "
                    "a weathered stone burial tower partly carved into a "
                    "cliff face, small dark entrance visible, high-altitude "
                    "altiplano grassland around with distant snow peaks, "
                    "offerings of coca leaves on a stone. Pale thin alpine "
                    "air, ancient ancestral."
                )
            }
        ]
    },

    # ═══════════════ STREETS (4) ═══════════════
    {
        "kind": "streets",
        "slug": "mythic-pilgrims-way",
        "id": "mythic_pilgrims_way",
        "title": "Pilgrim's Way",
        "subcategory": "Mythic",
        "aesthetic_category": "mythic_folk",
        "description": (
            "An ancient walking pilgrimage route with way-shrines every "
            "kilometer — Camino de Santiago, Tibetan kora, Shikoku henro, "
            "Sufi tariqah. The path IS the practice. Wayfarers walk for "
            "months, sleeping in way-inns, marking their passage."
        ),
        "tags": ["mythic", "pilgrim", "walking", "sacred", "wayfinding", "ancient"],
        "hero_prompt": (
            "An ancient Pilgrim's Way path winding across a landscape at "
            "morning — narrow packed-earth path with stone way-shrines "
            "every hundred meters, a single hooded pilgrim walking with "
            "a staff, mossy stone markers, distant small village. Warm "
            "pilgrim-amber morning light, sacred, ancient, contemplative."
        ),
        "suggested_width_m": 3,
        "variants": [
            {
                "id": "pilgrim_camino_santiago",
                "label": "Camino de Santiago",
                "story": "Spanish pilgrim route to Santiago — stone paths, scallop-shell waymarkers, Romanesque wayside chapels.",
                "color": "#C8A868",
                "prompt": (
                    "A Camino de Santiago pilgrim path at golden hour — "
                    "packed-earth path across a Spanish meseta, stone "
                    "waymarker pillars with bronze scallop-shell inscribed, "
                    "a small Romanesque stone wayside chapel, a pilgrim "
                    "with staff and scallop-shell badge walking. Warm "
                    "golden Iberian light."
                )
            },
            {
                "id": "pilgrim_tibetan_kora",
                "label": "Tibetan Kora Prayer Path",
                "story": "Tibetan Buddhist kora path — mountain trail with prayer wheels, prayer flags, maroon-robed pilgrims.",
                "color": "#C44A3A",
                "prompt": (
                    "A Tibetan Buddhist kora pilgrim path — rough mountain "
                    "trail circling a sacred site, lined with large copper "
                    "prayer-wheel cylinders, colourful prayer flags strung "
                    "across, a maroon-robed Tibetan pilgrim making prostrations, "
                    "snow peaks beyond. Thin high-altitude light, sacred."
                )
            },
            {
                "id": "pilgrim_shikoku_henro",
                "label": "Shikoku 88-Temple Henro",
                "story": "Japanese Shikoku pilgrimage — white-clad pilgrims, bamboo staves, forest path, red torii gates.",
                "color": "#E8E4D0",
                "prompt": (
                    "A Shikoku henro pilgrim path at morning — narrow forest "
                    "path through Japanese cedar forest, a white-clad henro "
                    "pilgrim with conical sedge hat and bamboo staff walking, "
                    "a small vermilion torii shrine gate ahead, stone Buddha "
                    "statues (o-jizo-sama) at the path's edge. Dappled "
                    "morning light."
                )
            },
            {
                "id": "pilgrim_sufi_tariqah",
                "label": "Sufi Tariqah Dervish Path",
                "story": "Sufi pilgrim path — desert dust road to a saint's tomb, whirling dervishes in white, minaret in distance.",
                "color": "#D8A454",
                "prompt": (
                    "A Sufi Tariqah pilgrim path at golden hour — dusty "
                    "path through a desert landscape, a distant white-domed "
                    "saint's tomb (dargah) with minaret, three dervishes in "
                    "white robes and tall felt hats walking in procession. "
                    "Warm sacred Middle Eastern light, mystic."
                )
            }
        ]
    },
    {
        "kind": "streets",
        "slug": "mythic-ghost-street",
        "id": "mythic_ghost_street",
        "title": "Ghost Street / Spirit Lane",
        "subcategory": "Mythic",
        "aesthetic_category": "mythic_folk",
        "description": (
            "A narrow street with folkloric ghost or spirit associations — "
            "Edo yurei alleys, medieval plague alleys with shrine niches, "
            "Día de Muertos ofrenda streets, Slavic threshold-lanes for "
            "the domovoi. Places where the dead walk too."
        ),
        "tags": ["mythic", "ghost", "spirit", "alley", "liminal", "nocturnal"],
        "hero_prompt": (
            "A narrow mythic Ghost Street at atmospheric night mist — "
            "paper lanterns glowing pale along dark stone walls, a small "
            "shrine niche with offerings set into the wall, faint mist "
            "drifting, shadows of the past almost visible. Liminal, "
            "haunting, sacred."
        ),
        "suggested_width_m": 3,
        "variants": [
            {
                "id": "ghost_edo_yurei",
                "label": "Edo Yurei Alley",
                "story": "Edo Japan narrow stone alley — paper lanterns, rising mist, faint white figure glimpsed at the end.",
                "color": "#5A5A6E",
                "prompt": (
                    "An Edo Japan ghost alley at midnight mist — narrow "
                    "stone-paved lane between dark wooden machiya walls, "
                    "rows of pale paper chochin lanterns glowing dim, "
                    "thick rising mist, a faint white-clad figure barely "
                    "glimpsed at the far end. Atmospheric, haunting, "
                    "folkloric."
                )
            },
            {
                "id": "ghost_medieval_plague",
                "label": "Medieval Plague Alley",
                "story": "Medieval European plague-memorial alley — shrine niche with Virgin Mary statue, candles, cobblestone lane.",
                "color": "#6A5A4A",
                "prompt": (
                    "A medieval European plague-memorial alley at dusk — "
                    "narrow cobblestone lane between tall old stone walls, "
                    "a small wall-niche shrine with a weathered Virgin Mary "
                    "statue lit by candles, offerings of wildflowers. "
                    "Silent, ancient, haunting memorial."
                )
            },
            {
                "id": "ghost_dia_de_muertos",
                "label": "Día de Muertos Ofrenda Street",
                "story": "Mexican Oaxacan street for Day of the Dead — orange marigold arch, candlelit ofrenda altar, sugar skulls.",
                "color": "#E88A20",
                "prompt": (
                    "A Mexican Día de Muertos ofrenda street at twilight — "
                    "colonial Oaxacan street with a tall marigold-flower "
                    "archway, a colourful candlelit ofrenda altar with "
                    "photographs of the dead, sugar skulls, pan de muerto, "
                    "cempasúchil petals on the cobbles. Warm, sacred, "
                    "celebratory-sad."
                )
            },
            {
                "id": "ghost_slavic_domovoi",
                "label": "Slavic Threshold Domovoi Lane",
                "story": "Slavic whitewashed village lane — traditional houses with protective hex signs, domovoi offerings at thresholds.",
                "color": "#E4E0D0",
                "prompt": (
                    "A Slavic folk village lane at dusk — traditional "
                    "whitewashed houses with thatched roofs, carved wooden "
                    "shutters painted with protective hex-sign geometric "
                    "patterns, small bread-and-salt offerings on every "
                    "threshold for the household domovoi spirit. Warm "
                    "evening, folk-atmospheric."
                )
            }
        ]
    },
    {
        "kind": "streets",
        "slug": "mythic-cunning-woman-path",
        "id": "mythic_cunning_woman_path",
        "title": "Cunning-Woman Path",
        "subcategory": "Mythic",
        "aesthetic_category": "mythic_folk",
        "description": (
            "A path through the wild edge of a settlement, winding past "
            "herb-drying racks, crossroads shrines, and a small cottage "
            "or hut where the healer lives. European cunning-woman, "
            "Amazonian curandera, Nordic völva, African sangoma. The "
            "path to unofficial medicine and old knowledge."
        ),
        "tags": ["mythic", "healer", "wild-edge", "herb", "folk-medicine", "cunning-woman"],
        "hero_prompt": (
            "A Cunning-Woman Path at late afternoon — a narrow earth path "
            "winding through a tangle of wild herbs and flowers, wooden "
            "herb-drying racks hanging with bundles of dried plants, "
            "a small stone cottage at the end with smoke rising from a "
            "chimney, warm amber light from the window. Warm evening, "
            "folkloric, hidden-but-welcoming."
        ),
        "suggested_width_m": 2,
        "variants": [
            {
                "id": "cunning_european",
                "label": "European Cunning-Woman Path",
                "story": "English/German folk healer's path — hedgerow path, herbs hanging, small stone cottage with thatched roof.",
                "color": "#6A8240",
                "prompt": (
                    "An English cunning-woman path at golden hour — narrow "
                    "grass path through a hedgerow of hawthorn and wild "
                    "roses, wooden drying racks hanging with bundles of "
                    "dried lavender and sage, a small stone cottage with "
                    "thatched roof and smoke rising from the chimney. "
                    "Warm rural evening."
                )
            },
            {
                "id": "cunning_amazonian_curandera",
                "label": "Amazonian Curandera Path",
                "story": "Amazonian healer path through rainforest — medicinal vines hanging, small palm-thatched hut, carved gourd bowls.",
                "color": "#3E5E32",
                "prompt": (
                    "An Amazonian curandera healer path through rainforest "
                    "at humid afternoon — narrow earth path between dense "
                    "medicinal vines and ferns, carved gourd bowls hanging "
                    "from branches, a small palm-thatched hut with woven "
                    "baskets. Filtered green-gold jungle light, mystical, "
                    "humid."
                )
            },
            {
                "id": "cunning_nordic_volva",
                "label": "Nordic Völva Path",
                "story": "Nordic seeress path — stone path through birch and pine, rune-stones, small wooden cabin, pelts drying.",
                "color": "#8A9A8A",
                "prompt": (
                    "A Nordic völva seeress path at twilight — narrow stone "
                    "path through young birch and pine forest, weathered "
                    "rune-carved stones at intervals, a small wooden Nordic "
                    "cabin with reindeer pelts drying outside, warm interior "
                    "light. Cool Nordic evening, folkloric."
                )
            },
            {
                "id": "cunning_african_sangoma",
                "label": "African Sangoma Path",
                "story": "Southern African sangoma healer path — arid veld path, beaded offering strings, small thatched rondavel.",
                "color": "#C88A50",
                "prompt": (
                    "A southern African sangoma path at warm dusk — "
                    "narrow earth path across arid veld grassland, strings "
                    "of coloured beaded offerings tied to a small acacia "
                    "tree, a circular thatched rondavel hut, bones and "
                    "shells laid out for divination. Warm African evening, "
                    "sacred."
                )
            }
        ]
    },
    {
        "kind": "streets",
        "slug": "mythic-crossroads-shrine-path",
        "id": "mythic_crossroads_shrine_path",
        "title": "Crossroads Shrine Path",
        "subcategory": "Mythic",
        "aesthetic_category": "mythic_folk",
        "description": (
            "A rural road marked by shrines or deity-stones at every "
            "crossroads. Japanese dosojin, Indian crossroads deities, "
            "Haitian Elegua stones, Western European herm statues. "
            "Crossroads are liminal; the folk tradition protects them."
        ),
        "tags": ["mythic", "crossroads", "shrine", "folk", "threshold", "liminal"],
        "hero_prompt": (
            "A rural Crossroads Shrine Path at dawn — a dirt road meeting "
            "another at a gentle crossing, a weathered stone shrine with "
            "offerings of rice, flowers, and small coins at the intersection, "
            "ancient trees marking the corners. Soft dawn mist, sacred, "
            "folk-ritual."
        ),
        "suggested_width_m": 4,
        "variants": [
            {
                "id": "crossroads_japanese_dosojin",
                "label": "Japanese Dosojin Crossroads",
                "story": "Rural Japanese crossroads — pair of carved stone dosojin deity figures, rice offerings, cedar trees.",
                "color": "#8A8A7A",
                "prompt": (
                    "A rural Japanese dosojin crossroads at dawn — narrow "
                    "earth road meeting another, a pair of small weathered "
                    "stone dosojin deity figures (male and female) at the "
                    "intersection with offerings of rice and sake, tall "
                    "Japanese cedar trees at the corners. Misty morning, "
                    "sacred."
                )
            },
            {
                "id": "crossroads_indian_dhalsuvan",
                "label": "Indian Village Crossroads Deity",
                "story": "Indian rural crossroads deity — brightly painted stone figure, marigold garlands, oil offerings, banyan tree.",
                "color": "#F2B03C",
                "prompt": (
                    "An Indian rural crossroads deity shrine at dusk — "
                    "a brightly painted weathered stone village-deity "
                    "figure at the intersection of two dirt roads, orange "
                    "marigold garlands, oil-lamp offerings, a massive "
                    "ancient banyan tree overhead. Warm Indian evening, "
                    "sacred."
                )
            },
            {
                "id": "crossroads_haitian_elegua",
                "label": "Haitian Elegua Crossroads",
                "story": "Haitian Yoruba-diaspora crossroads — cement-and-shell Elegua head stone, offerings of cigars and rum.",
                "color": "#B83428",
                "prompt": (
                    "A Haitian Vodou Elegua crossroads at dusk — rural dirt "
                    "crossroads with a small concrete-and-seashell Elegua "
                    "head-stone at the centre, offerings of cigars, rum, "
                    "and a bowl of coins, red cloth tied around the stone. "
                    "Tropical warm evening, syncretic, sacred."
                )
            },
            {
                "id": "crossroads_european_hermes",
                "label": "European Herm Crossroads",
                "story": "Ancient Greek/European crossroads — a carved stone herm pillar with a bust, stone pile at the base.",
                "color": "#B8AA8A",
                "prompt": (
                    "An ancient European herm crossroads at golden hour — "
                    "a square weathered stone herm pillar at a rural "
                    "intersection, carved with a classical bust face at "
                    "the top, a small pile of traveler's offering-stones "
                    "at the base, olive trees at the corners. Warm "
                    "Mediterranean evening, classical, ancient."
                )
            }
        ]
    },
]


def generate_image(prompt: str, retries: int = 2) -> bytes | None:
    full_prompt = prompt + STYLE_SUFFIX
    payload = {
        "contents": [{"role": "user", "parts": [{"text": full_prompt}]}],
        "generationConfig": {"responseModalities": ["TEXT", "IMAGE"], "temperature": 0.7},
    }
    url = gemini_url()
    for attempt in range(retries + 1):
        try:
            resp = httpx.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=180.0)
        except httpx.TimeoutException:
            if attempt < retries: time.sleep(5); continue
            return None
        if resp.status_code == 429:
            print(f"    RATE LIMITED -- waiting 30s (attempt {attempt + 1})")
            time.sleep(30); continue
        if resp.status_code != 200:
            print(f"    HTTP {resp.status_code}: {resp.text[:200]}")
            if attempt < retries: time.sleep(5); continue
            return None
        data = resp.json()
        for candidate in data.get("candidates", []):
            for part in candidate.get("content", {}).get("parts", []):
                inline = part.get("inlineData") or part.get("inline_data")
                if inline and inline.get("data"):
                    return base64.b64decode(inline["data"])
        if attempt < retries: time.sleep(5); continue
    return None


def generate_archetype_images(arch: dict) -> bool:
    folder = PUBLIC / arch["kind"] / arch["slug"]
    folder.mkdir(parents=True, exist_ok=True)
    hero_path = folder / "hero.png"
    if not hero_path.exists():
        print(f"  hero.png ...", end=" ", flush=True)
        img = generate_image(arch["hero_prompt"])
        if not img: print("FAILED"); return False
        hero_path.write_bytes(img); print(f"OK ({len(img)//1024} KB)")
        time.sleep(2)
    else: print(f"  hero.png  (skip)")
    for i, v in enumerate(arch["variants"]):
        variant_path = folder / f"variant_{i}.png"
        if variant_path.exists():
            print(f"  variant_{i}.png ({v['label']!r})  (skip)"); continue
        print(f"  variant_{i}.png ({v['label']!r}) ...", end=" ", flush=True)
        img = generate_image(v["prompt"])
        if not img: print("FAILED"); return False
        variant_path.write_bytes(img); print(f"OK ({len(img)//1024} KB)")
        time.sleep(2)
    return True


def build_building_entry(arch: dict) -> dict:
    return {
        "id": arch["id"], "title": arch["title"],
        "buildingSubcategory": arch["subcategory"], "developmentType": arch["development_type"],
        "aestheticCategory": arch["aesthetic_category"],
        "description": arch["description"], "generationTags": arch["tags"],
        "styleProfile": arch["style_profile"], "prompt": arch["prompt_block"],
        "suggestedWidth_m": arch["suggested_width_m"], "suggestedDepth_m": arch["suggested_depth_m"],
        "minFloors": arch["min_floors"], "maxFloors": arch["max_floors"],
        "thumbnailUrl": f"/archetypes/buildings/{arch['slug']}/hero.png",
        "variants": [{
            "id": v["id"], "label": v["label"], "description": v["story"],
            "thumbnailUrl": f"/archetypes/buildings/{arch['slug']}/variant_{i}.png",
            "color": v["color"], "minFloors": v["min_floors"], "maxFloors": v["max_floors"],
            "suggestedFloorHeight": v["suggested_floor_height"], "suggestedAreaSqm": v["suggested_area_sqm"],
            "facadeDetail": {"primaryMaterial": v["facade_primary"], "secondaryMaterial": v["facade_secondary"],
                             "groundFloor": v["facade_ground"], "colorScheme": v["facade_palette"]},
            "roofDetail": {"form": v["roof_form"], "material": v["roof_material"]},
        } for i, v in enumerate(arch["variants"])]
    }


def build_openspace_entry(arch: dict) -> dict:
    return {
        "id": arch["id"], "title": arch["title"], "spaceType": arch["space_type"],
        "aestheticCategory": arch["aesthetic_category"], "buildingSubcategory": arch["subcategory"],
        "description": arch["description"], "generationTags": arch["tags"],
        "suggestedWidth_m": arch["suggested_width_m"], "suggestedDepth_m": arch["suggested_depth_m"],
        "suggestedAreaSqm": arch["suggested_area_sqm"],
        "thumbnailUrl": f"/archetypes/openspaces/{arch['slug']}/hero.png",
        "shape": "rectangular",
        "variants": [{"id": v["id"], "label": v["label"], "description": v["story"],
                      "thumbnailUrl": f"/archetypes/openspaces/{arch['slug']}/variant_{i}.png",
                      "color": v["color"]} for i, v in enumerate(arch["variants"])]
    }


def build_street_entry(arch: dict) -> dict:
    return {
        "id": arch["id"], "title": arch["title"], "aestheticCategory": arch["aesthetic_category"],
        "buildingSubcategory": arch["subcategory"], "description": arch["description"],
        "generationTags": arch["tags"], "typicalWidth_m": arch["suggested_width_m"],
        "laneCount": 1, "hasSidewalk": False, "shape": "linear",
        "thumbnailUrl": f"/archetypes/streets/{arch['slug']}/hero.png",
        "variants": [{"id": v["id"], "label": v["label"], "description": v["story"],
                      "thumbnailUrl": f"/archetypes/streets/{arch['slug']}/variant_{i}.png",
                      "color": v["color"]} for i, v in enumerate(arch["variants"])]
    }


def archetype_already_in_catalog(catalog_path: Path, arch_id: str) -> bool:
    return f'"id": "{arch_id}"' in catalog_path.read_text(encoding="utf-8")


def splice_into_catalog(catalog_path: Path, new_entry: dict) -> None:
    if archetype_already_in_catalog(catalog_path, new_entry["id"]): return
    text = catalog_path.read_text(encoding="utf-8")
    close = text.rfind("]")
    if close < 0: raise RuntimeError(f"No closing ] in {catalog_path}")
    ip = close
    while ip > 0 and text[ip - 1] in " \t\r\n": ip -= 1
    raw = json.dumps(new_entry, indent=4, ensure_ascii=False)
    lines = raw.split("\n")
    indented = lines[0] + "\n" + "\n".join("    " + line for line in lines[1:])
    new_text = text[:ip] + ",\n    " + indented + "\n  " + text[close:]
    json.loads(new_text)
    catalog_path.write_text(new_text, encoding="utf-8")


def main():
    limit, dry_run = None, False
    for a in sys.argv[1:]:
        if a.startswith("--limit="): limit = int(a.split("=", 1)[1])
        elif a == "--dry-run": dry_run = True
        elif a in ("-h", "--help"): print(__doc__); sys.exit(0)
    targets = ARCHETYPES[:limit] if limit else ARCHETYPES
    print(f"Processing {len(targets)} Mythic archetype(s){' (DRY RUN)' if dry_run else ''}\n")
    if dry_run:
        for arch in targets:
            print(f"  [{arch['kind']}] {arch['id']}  ({arch['title']})")
        return 0
    successes = 0
    for i, arch in enumerate(targets, 1):
        print(f"[{i}/{len(targets)}] {arch['id']}  ({arch['title']})")
        if not generate_archetype_images(arch):
            print(f"    IMAGES FAILED"); continue
        entry = (build_building_entry if arch["kind"] == "buildings"
                 else build_openspace_entry if arch["kind"] == "openspaces"
                 else build_street_entry)(arch)
        try:
            already = archetype_already_in_catalog(CATALOGS[arch["kind"]], arch["id"])
            splice_into_catalog(CATALOGS[arch["kind"]], entry)
            print(f"    [OK] {'already present in' if already else 'spliced into'} {arch['kind']} catalog")
            successes += 1
        except Exception as e:
            print(f"    SPLICE FAILED: {e}")
    print(f"\n=== Done: {successes}/{len(targets)} Mythic archetypes completed ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
