#!/usr/bin/env python3
"""
Generate 12 Festival / Ephemeral archetypes (4 buildings, 4 parks, 4 streets).

Architecture designed to be temporary but beautiful — matsuri shrines, Diwali
pandals, carnival bandstands, Holi plazas, Burning Man playa camps,
processional avenues. The moments a culture stops normal life to make
something gorgeous together. Every archetype draws on a real festival tradition.

Identical pipeline to generate_experimental_archetypes.py / generate_utopic_archetypes.py.
"""

from __future__ import annotations

import base64
import json
import sys
import time
from pathlib import Path
from typing import Any

import httpx

# Reconfigure stdout for UTF-8 so Japanese/Sanskrit/Latvian labels (ō, ā, ņ, é, etc.)
# don't crash Windows cp1252 console printing.
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
    " Photorealistic festival photography. Cinematic lighting. Sharp detail. "
    "Vibrant, alive, communal. Not illustration — documentary photography of "
    "a real festival in full swing. 8K detail, professional photography."
)


ARCHETYPES: list[dict[str, Any]] = [
    # ═══════════════ BUILDINGS (4) ═══════════════
    {
        "kind": "buildings",
        "slug": "festival-matsuri-mikoshi-pavilion",
        "id": "festival_matsuri_mikoshi_pavilion",
        "title": "Matsuri Mikoshi Pavilion",
        "subcategory": "Festival",
        "development_type": "institutional",
        "aesthetic_category": "festival_ephemeral",
        "description": (
            "A Japanese festival portable shrine pavilion — a carved and "
            "gilded wooden mikoshi or elevated dance platform paraded through "
            "the streets during matsuri, then stored at the community shrine "
            "until next year. Built of wood, paper, and lacquer; ornamented "
            "with bells, silks, and fresh flowers. The spirit resides in it "
            "for three days. Community hands-lifted, drum-accompanied, "
            "ecstatically paraded."
        ),
        "tags": ["festival", "ephemeral", "matsuri", "japanese", "ritual", "portable"],
        "style_profile": {
            "materials": ["carved lacquered wood", "gold-leaf ornament", "paper lanterns", "silk banners", "bronze bells"],
            "facadeRhythm": "Tiered ornamented pagoda-like layers",
            "roofForm": "Elaborate multi-tiered curved roof with golden finial",
            "frontageType": "Carried on wooden poles by 30-50 community members",
            "windowStyle": "Small shrine-openings with silk-hung interior",
            "massing": "Compact ornate rectangular shrine body raised on carrying poles",
            "heightTendency": "Small (3-6m tall on carrying poles)",
            "streetRelationship": "Paraded THROUGH streets; stationed at shrines between",
            "renderingMood": "Ecstatic, sacred, communal, loud with drums",
            "articulation": "Dense ornament — bells, tassels, carved panels, gold-leaf",
            "publicRealm": "Street-center activation; entire community around"
        },
        "prompt_block": {
            "subject": "A Japanese festival portable shrine pavilion being paraded through a street",
            "details": [
                "Carved lacquered wood with gold-leaf ornament",
                "Multi-tiered curved roof with golden finial",
                "Carried by 30-50 community members on wooden poles",
                "Bells, silks, paper lanterns ornament",
                "Community crowd around, drums, chanting"
            ]
        },
        "suggested_width_m": 4,
        "suggested_depth_m": 4,
        "min_floors": 1,
        "max_floors": 2,
        "hero_prompt": (
            "A Matsuri Mikoshi Pavilion being paraded through a Japanese "
            "festival street at warm evening — ornate carved lacquered wooden "
            "portable shrine with gold-leaf ornament, multi-tiered curved "
            "roof, golden phoenix finial, hung with silks and paper lanterns. "
            "Carried on long wooden poles by 40 community members in happi "
            "coats and hachimaki headbands, chanting in rhythm. Drums visible. "
            "Dense festive crowd around, paper lanterns overhead. Warm amber "
            "festival light. Ecstatic, sacred, communal."
        ),
        "variants": [
            {
                "id": "matsuri_gion_yamaboko",
                "label": "Gion Yamaboko Float",
                "story": "Kyoto's towering Gion Matsuri wheeled float — 25m tall with roof-top pine, tapestries, a ritual child rider.",
                "color": "#C8401E", "min_floors": 5, "max_floors": 8,
                "suggested_floor_height": 3.0, "suggested_area_sqm": 40,
                "prompt": (
                    "A Gion Matsuri Yamaboko festival float in a Kyoto street at dusk "
                    "— towering 25-meter wheeled wooden float with a tall pine tree at "
                    "the top, hung with ancient Persian and Chinese tapestries on every "
                    "face, gold ornaments, a ritual child rider in costume visible at "
                    "the top. Dozens of men in white costumes pulling with thick ropes. "
                    "Kyoto traditional machiya buildings on both sides. Paper lanterns. "
                    "Warm evening, festive crowd, drums. Sacred, ancient."
                ),
                "facade_primary": "towering timber float frame with Persian tapestries",
                "facade_secondary": "carved gold and lacquered ornament bands",
                "facade_ground": "massive wooden wheels drawn by community ropes",
                "facade_palette": "ancient tapestry reds, gold, lacquered black, pine green",
                "roof_form": "tall pine tree rising from the float's peak",
                "roof_material": "living pine tree lashed to the roof armature"
            },
            {
                "id": "matsuri_kanda_mikoshi",
                "label": "Kanda Mikoshi Shrine",
                "story": "Tokyo Kanda Matsuri portable shrine — black-lacquered, gold-ornamented, phoenix-topped, carried at shoulder.",
                "color": "#1A1A2A", "min_floors": 1, "max_floors": 1,
                "suggested_floor_height": 3.5, "suggested_area_sqm": 25,
                "prompt": (
                    "A Kanda Matsuri mikoshi portable shrine being carried at shoulder "
                    "height through a Tokyo neighbourhood festival — black-lacquered "
                    "wooden shrine body, intricate gold-leaf ornament, carved dragons, "
                    "golden phoenix finial on the multi-tiered roof, silk tassels. "
                    "Carried by 40 men in white happi coats and hachimaki. Dense "
                    "crowd. Paper lanterns strung overhead. Warm festive evening. "
                    "Ecstatic, communal."
                ),
                "facade_primary": "black-lacquered carved wood shrine body",
                "facade_secondary": "gold-leaf dragon and cloud ornament",
                "facade_ground": "carrying poles resting on shoulders of the community",
                "facade_palette": "lacquer black, gold leaf, crimson silks",
                "roof_form": "multi-tiered curved roof with golden phoenix finial",
                "roof_material": "gold-leaf over carved cedar"
            },
            {
                "id": "matsuri_sanja_portable",
                "label": "Sanja Asakusa Shrine",
                "story": "Asakusa's Sanja Matsuri mikoshi — rougher-hewn, tattoo-men bearers, traditional Edo character.",
                "color": "#8A3028", "min_floors": 1, "max_floors": 1,
                "suggested_floor_height": 3.2, "suggested_area_sqm": 20,
                "prompt": (
                    "A Sanja Matsuri mikoshi being carried in Asakusa Tokyo — weathered "
                    "lacquered wood portable shrine with hand-carved ornament, carried "
                    "by traditional Edo-style carriers in white fundoshi and tattoos "
                    "visible. Dense crowd around Sensō-ji temple grounds visible in "
                    "background. Deep crimson silks. Golden phoenix finial. Warm "
                    "afternoon light, traditional Edo atmosphere."
                ),
                "facade_primary": "weathered hand-carved lacquered wood",
                "facade_secondary": "crimson silk tassels and gold ornament",
                "facade_ground": "carrying poles on shoulders of traditional carriers",
                "facade_palette": "deep crimson, aged lacquer, warm gold, Asakusa red",
                "roof_form": "traditional tiered roof with phoenix finial",
                "roof_material": "aged gold leaf over cedar"
            },
            {
                "id": "matsuri_awa_odori_pavilion",
                "label": "Awa Odori Dance Pavilion",
                "story": "Shikoku's Awa Odori raised dance pavilion — open timber platform, paper lanterns, for ecstatic parade dancing.",
                "color": "#D87A30", "min_floors": 1, "max_floors": 2,
                "suggested_floor_height": 3.8, "suggested_area_sqm": 50,
                "prompt": (
                    "An Awa Odori dance pavilion at a Shikoku summer festival night — "
                    "raised timber platform 2m above the street, open on all sides, "
                    "with rows of warm paper lanterns hanging from the roof frame. "
                    "Dancers in yukata with conical amigasa hats performing the Awa "
                    "Odori dance on the platform and the street below. Musicians "
                    "with shamisen and taiko drums. Crowd. Warm summer night, "
                    "communal joy."
                ),
                "facade_primary": "open timber post-and-beam raised platform",
                "facade_secondary": "hanging warm paper lantern strings",
                "facade_ground": "stepped timber stair up from the street",
                "facade_palette": "warm timber, glowing paper orange, festival indigo yukata",
                "roof_form": "tent-like timber roof frame with lantern strings",
                "roof_material": "timber frame with paper lantern infill"
            }
        ]
    },
    {
        "kind": "buildings",
        "slug": "festival-diwali-pandal",
        "id": "festival_diwali_pandal",
        "title": "Diwali Pandal Pavilion",
        "subcategory": "Festival",
        "development_type": "institutional",
        "aesthetic_category": "festival_ephemeral",
        "description": (
            "An elaborate temporary festival pavilion built for Diwali or "
            "Durga Puja — bamboo-framed, cloth-clad, oil-lamp-arrayed, with "
            "thousands of marigold strings and rangoli floor patterns. Built "
            "over two weeks, adored for five days, then dismantled. A "
            "neighbourhood tradition of collective artistry."
        ),
        "tags": ["festival", "ephemeral", "diwali", "indian", "pandal", "oil-lamps"],
        "style_profile": {
            "materials": ["bamboo framing", "painted cloth panels", "clay diya oil lamps", "marigold garland strings", "rangoli powder floor"],
            "facadeRhythm": "Repetitive lamp-lined arches and tiered ornament",
            "roofForm": "Peaked or domed with finial; covered in lamps",
            "frontageType": "Grand ceremonial archway entry with oil-lamp rows",
            "windowStyle": "Open arcades — no glazing, covered for 5 days",
            "massing": "Large ornate pavilion 15-25m tall, 20-40m square footprint",
            "heightTendency": "Mid-rise (15-25m)",
            "streetRelationship": "Occupies a neighbourhood plaza; festival spills into surrounding streets",
            "renderingMood": "Warm with thousands of flames, crowds, music, incense",
            "articulation": "Dense ornament — marigolds, lamps, painted cloth, sculptural goddess",
            "publicRealm": "Surrounding plaza hosts food stalls, music, dance"
        },
        "prompt_block": {
            "subject": "An elaborate Diwali/Durga Puja temporary pavilion at night",
            "details": [
                "Bamboo-framed pavilion 15-25m tall",
                "Thousands of oil lamps (diyas) outlining every edge",
                "Marigold garland curtains",
                "Painted cloth panels in deep reds and golds",
                "Rangoli floor patterns",
                "Dense crowd with families in festival dress"
            ]
        },
        "suggested_width_m": 25,
        "suggested_depth_m": 25,
        "min_floors": 3,
        "max_floors": 6,
        "hero_prompt": (
            "An elaborate Diwali pandal pavilion at night — bamboo-framed "
            "20-meter-tall pavilion with thousands of small clay oil-lamp "
            "diyas outlining every arch and edge, strung with marigold "
            "garland curtains, painted cloth panels in deep reds and golds, "
            "rangoli powder patterns on the ground at the entrance. Dense "
            "crowd of families in festival dress. Warm flames everywhere. "
            "Incense smoke rising. Ecstatic, sacred, luminous."
        ),
        "variants": [
            {
                "id": "diwali_kolkata_durga",
                "label": "Kolkata Durga Puja Pandal",
                "story": "Kolkata's elaborate goddess-sheltering pandal — sculpted Durga image at the heart, bamboo architecture + painted cloth.",
                "color": "#C42E2E", "min_floors": 4, "max_floors": 6,
                "suggested_floor_height": 5.0, "suggested_area_sqm": 600,
                "prompt": (
                    "A Kolkata Durga Puja pandal at festival night — massive bamboo-"
                    "framed cathedral-like pavilion with a sculpted Durga goddess image "
                    "at the heart (10-armed, riding a lion), painted cloth panels in "
                    "deep reds and golds, thousands of oil lamps and chandeliers, "
                    "marigold garlands everywhere. Dense crowd of devotees. Incense "
                    "smoke. Warm, sacred, overwhelming."
                ),
                "facade_primary": "bamboo-framed painted cloth cathedral structure",
                "facade_secondary": "gold-trimmed red fabric drapery panels",
                "facade_ground": "rangoli-patterned entry with hundreds of diyas",
                "facade_palette": "deep Durga-red, gold, marigold orange, warm lamp amber",
                "roof_form": "tiered shikhara-style peak with central finial",
                "roof_material": "painted cloth over bamboo armature"
            },
            {
                "id": "diwali_jaipur_lamps",
                "label": "Jaipur Pink City Pavilion",
                "story": "Rajasthan Jaipur-style pandal — pink-sandstone-imitating painted cloth, thousands of diyas, peacock motifs.",
                "color": "#D4818A", "min_floors": 3, "max_floors": 5,
                "suggested_floor_height": 4.8, "suggested_area_sqm": 500,
                "prompt": (
                    "A Jaipur-style Diwali pandal at night — pavilion painted to "
                    "resemble the Pink City's sandstone with jharokha balconies and "
                    "peacock motifs, thousands of oil lamp diyas outlining every "
                    "edge, marigold garlands. Rajasthani folk dancers in colourful "
                    "skirts. Warm festival night, joyous crowd."
                ),
                "facade_primary": "pink-sandstone-painted bamboo-framed panels",
                "facade_secondary": "peacock and jharokha motifs",
                "facade_ground": "rangoli patterns with diyas",
                "facade_palette": "Jaipur pink, saffron, gold, peacock blue-green",
                "roof_form": "chhatri-style domed pavilions with finials",
                "roof_material": "painted cloth domes over bamboo"
            },
            {
                "id": "diwali_banaras_ghat",
                "label": "Banaras Ghat Pavilion",
                "story": "Riverfront Varanasi Diwali pandal — spanning the stone ghats, river-lamps floating, Ganges reflected.",
                "color": "#B8941A", "min_floors": 2, "max_floors": 4,
                "suggested_floor_height": 5.2, "suggested_area_sqm": 700,
                "prompt": (
                    "A Banaras ghat Diwali pandal at night along the Ganges — "
                    "bamboo pavilion built on the ancient stone ghat steps, thousands "
                    "of oil lamps on the steps, hundreds of floating lamps drifting "
                    "on the river, sadhus and families. Ancient ghat architecture "
                    "behind, warm river-reflected light, incense. Sacred, ancient, "
                    "luminous."
                ),
                "facade_primary": "bamboo-framed structure on ancient stone ghat steps",
                "facade_secondary": "saffron and gold fabric drapery",
                "facade_ground": "stone ghat steps lined with thousands of diyas",
                "facade_palette": "saffron, gold, river-reflection silver, ghat-stone grey",
                "roof_form": "open pavilion roof with golden finial",
                "roof_material": "painted cloth over bamboo frame"
            },
            {
                "id": "diwali_kerala_coconut",
                "label": "Kerala Coconut-Leaf Pavilion",
                "story": "South Indian Kerala-style pandal — woven coconut leaves, bronze oil-lamp chains, banana-stem pillars.",
                "color": "#7A8240", "min_floors": 2, "max_floors": 3,
                "suggested_floor_height": 4.5, "suggested_area_sqm": 400,
                "prompt": (
                    "A Kerala-style Diwali pandal at night — pavilion built of woven "
                    "coconut palm leaves, banana-stem pillars wrapped in red cloth, "
                    "bronze oil-lamp chains hanging from the roof, flower carpets on "
                    "the ground. Dancers in mundu and kerala sari. Tropical humid "
                    "night, warm glow, sacred."
                ),
                "facade_primary": "woven coconut palm leaf panels on bamboo frame",
                "facade_secondary": "banana-stem pillars wrapped in red cloth",
                "facade_ground": "flower-carpet pookalam floor pattern",
                "facade_palette": "palm-frond green, banana-stem white, red cloth, bronze lamps",
                "roof_form": "thatched palm-leaf roof with woven finial",
                "roof_material": "woven coconut palm leaf thatch"
            }
        ]
    },
    {
        "kind": "buildings",
        "slug": "festival-carnival-bandstand",
        "id": "festival_carnival_bandstand",
        "title": "Carnival Bandstand Pavilion",
        "subcategory": "Festival",
        "development_type": "institutional",
        "aesthetic_category": "festival_ephemeral",
        "description": (
            "A raised dance-and-music platform built for Carnival — ornate "
            "fabric canopies, feather decorations, sequin-studded facades, "
            "amplifier towers, costumed dancers on deck. Built three weeks "
            "before Ash Wednesday, torn down the day after. The stage where "
            "the year's ecstatic public ritual happens."
        ),
        "tags": ["festival", "ephemeral", "carnival", "bandstand", "music", "dance"],
        "style_profile": {
            "materials": ["scaffolding steel frame", "fabric canopies", "feather and sequin decoration", "amplifier towers", "painted plywood facade"],
            "facadeRhythm": "Tiered ornate stage front with amplifier towers flanking",
            "roofForm": "Large ornate canopy, sometimes with feather crown",
            "frontageType": "Open performance stage at 2m elevation above street",
            "windowStyle": "Fully open performance facade; dancers on display",
            "massing": "Wide rectangular raised platform, 3-6m tall stage + canopy",
            "heightTendency": "Low to mid (5-10m with canopy)",
            "streetRelationship": "Faces a parade route; crowd on bleachers opposite",
            "renderingMood": "Ecstatic, loud, colourful, percussive",
            "articulation": "Dense ornament — feathers, sequins, fabric drapes",
            "publicRealm": "Parade route in front; backstage zone behind"
        },
        "prompt_block": {
            "subject": "A raised Carnival bandstand pavilion in mid-parade",
            "details": [
                "Raised 3m stage platform",
                "Ornate fabric canopy overhead",
                "Amplifier tower columns on either side",
                "Costumed dancers on stage (feathers, sequins)",
                "Dense parade crowd in front",
                "Drums and brass instruments visible"
            ]
        },
        "suggested_width_m": 20,
        "suggested_depth_m": 10,
        "min_floors": 1,
        "max_floors": 2,
        "hero_prompt": (
            "A Carnival bandstand pavilion at the height of a parade — raised "
            "3m stage with ornate fabric canopy overhead, flanked by tall "
            "amplifier columns, deck crowded with costumed dancers in "
            "feathers and sequins, drummers and brass band in the back. "
            "Dense parade crowd in front on both sides. Vibrant, ecstatic, "
            "warm evening light, confetti in the air. Photorealistic, loud, "
            "communal."
        ),
        "variants": [
            {
                "id": "carnival_rio_samba",
                "label": "Rio Samba Pavilion",
                "story": "Rio samba-school pavilion — giant feather-costumed dancers, percussion corps, samba rhythms, tropical green-gold.",
                "color": "#F2C040", "min_floors": 1, "max_floors": 2,
                "suggested_floor_height": 4.0, "suggested_area_sqm": 180,
                "prompt": (
                    "A Rio Carnival samba-school pavilion at parade peak — raised "
                    "stage with tropical green-and-gold canopy, dozens of samba dancers "
                    "in giant feather headdresses and sequinned costumes, a full "
                    "percussion battery of 60 drummers at the back. Sambódromo "
                    "bleachers full of spectators. Confetti, warm Rio evening. "
                    "Ecstatic, loud, colorful."
                ),
                "facade_primary": "tropical green and gold sequinned facade",
                "facade_secondary": "feather-crown ornament along the canopy edge",
                "facade_ground": "scaffolding steel frame with cable drops",
                "facade_palette": "samba green, gold, rainbow sequins, feather multicolor",
                "roof_form": "massive feathered canopy with peacock-tail finial",
                "roof_material": "ornate fabric with feather-crown edge"
            },
            {
                "id": "carnival_venice_baroque",
                "label": "Venice Carnevale Baroque Stage",
                "story": "Venetian Carnevale masked-ball stage — baroque gilt architecture, commedia dell'arte characters, gondola backdrop.",
                "color": "#8A4A62", "min_floors": 1, "max_floors": 2,
                "suggested_floor_height": 4.5, "suggested_area_sqm": 140,
                "prompt": (
                    "A Venetian Carnevale baroque stage on Piazza San Marco — raised "
                    "stage with ornate gilt-painted baroque facade, red velvet draping, "
                    "masked dancers in commedia dell'arte costumes, chandeliers, "
                    "Campanile visible in background, sunset over the lagoon. "
                    "Elegant, mysterious, theatrical."
                ),
                "facade_primary": "gilt-painted baroque proscenium facade",
                "facade_secondary": "red velvet drapery and chandeliers",
                "facade_ground": "painted-cloth stair with carved balustrade",
                "facade_palette": "gilt gold, Venetian red, cream, Venetian-lagoon green-blue",
                "roof_form": "baroque pediment with sculpted cherubs and masks",
                "roof_material": "gilt-painted timber pediment with fabric canopy"
            },
            {
                "id": "carnival_nola_mardi_gras",
                "label": "New Orleans Mardi Gras Bandstand",
                "story": "NOLA Mardi Gras raised float-stage — brass-band musicians, purple-green-gold krewe colours, jazz rhythms.",
                "color": "#7A3ABA", "min_floors": 1, "max_floors": 2,
                "suggested_floor_height": 4.0, "suggested_area_sqm": 150,
                "prompt": (
                    "A New Orleans Mardi Gras bandstand at Bourbon Street parade — "
                    "raised stage in purple, green, and gold krewe colours, brass "
                    "band in full swing, masked dancers throwing beads to the crowd, "
                    "French Quarter wrought-iron balcony buildings behind. Warm "
                    "evening, party atmosphere, jazz."
                ),
                "facade_primary": "purple and green painted plywood stage facade",
                "facade_secondary": "gold fleur-de-lis ornament and bead curtains",
                "facade_ground": "french quarter cobbled street at stage base",
                "facade_palette": "Mardi Gras purple, green, gold, beads and feathers",
                "roof_form": "large fleur-de-lis-topped canopy",
                "roof_material": "painted canvas canopy with fleur-de-lis finial"
            },
            {
                "id": "carnival_trinidad_soca",
                "label": "Trinidad Soca Steel Pan Pavilion",
                "story": "Trinidad soca/steel-pan stage — steel drum orchestra, feathered mas costumes, Caribbean sunset palette.",
                "color": "#E0744A", "min_floors": 1, "max_floors": 2,
                "suggested_floor_height": 4.0, "suggested_area_sqm": 160,
                "prompt": (
                    "A Trinidad Carnival soca stage with a steel-pan orchestra — "
                    "raised stage with vibrant Caribbean sunset palette, steel pan "
                    "drummers at the back, mas dancers in elaborate feather-and-"
                    "sequin costumes, tropical palm silhouettes. Warm Caribbean "
                    "evening, vibrant, soca music."
                ),
                "facade_primary": "sunset-palette painted fabric stage facade",
                "facade_secondary": "feather and sequin ornamentation",
                "facade_ground": "scaffolding steel with steel-pan drum cluster",
                "facade_palette": "Caribbean sunset orange, turquoise, magenta, gold",
                "roof_form": "fan-shaped feather canopy",
                "roof_material": "feather-and-sequin-trimmed fabric fan"
            }
        ]
    },
    {
        "kind": "buildings",
        "slug": "festival-redentore-bridge-house",
        "id": "festival_redentore_bridge_house",
        "title": "Redentore Bridge-House",
        "subcategory": "Festival",
        "development_type": "institutional",
        "aesthetic_category": "festival_ephemeral",
        "description": (
            "The Venetian tradition of building temporary pontoon bridges "
            "across the Grand Canal or Giudecca Canal for festival pilgrimage "
            "(Redentore, Madonna della Salute, Festa di San Marco). Pavilion "
            "structures on the bridges — candlelit, flag-hung, lined with "
            "votive offerings. Built with boats lashed together, crossed by "
            "thousands, dismantled within days."
        ),
        "tags": ["festival", "ephemeral", "venice", "bridge", "waterborne", "votive"],
        "style_profile": {
            "materials": ["boat-pontoon substructure", "timber decking", "fabric banners", "votive candles", "strung paper lanterns"],
            "facadeRhythm": "Linear procession of flag-hung bays along the bridge",
            "roofForm": "Open-air flag-festooned or simple fabric canopy",
            "frontageType": "Pedestrian-only span between two waterfront plazas",
            "windowStyle": "Open — pilgrims walking in the open air",
            "massing": "Long linear span 200-400m, 3-5m wide",
            "heightTendency": "Low (at water level + 2-3m above)",
            "streetRelationship": "Connects two stone waterfront plazas across a canal",
            "renderingMood": "Sacred, candlelit, slow procession, water-reflected",
            "articulation": "Flag and candle-line rhythm along the span",
            "publicRealm": "Embarking and disembarking plazas activated with music and food stalls"
        },
        "prompt_block": {
            "subject": "A Venetian temporary festival pontoon bridge at night",
            "details": [
                "Linear timber-decked bridge on boat pontoons across a canal",
                "Strung with flags, candles, paper lanterns",
                "Pilgrims walking in procession",
                "Venetian palazzi on both sides",
                "Water reflections, gondolas"
            ]
        },
        "suggested_width_m": 5,
        "suggested_depth_m": 300,
        "min_floors": 1,
        "max_floors": 1,
        "hero_prompt": (
            "A Venetian Redentore festival pontoon bridge at night — long "
            "linear timber-decked bridge on lashed boat pontoons spanning "
            "the Giudecca Canal, hung with strings of paper lanterns and "
            "flags, thousands of candles lining the edges. Pilgrims walking "
            "in slow procession. Church of the Redentore glowing at the "
            "far end. Venetian palazzi on both sides. Water reflections, "
            "gondolas nearby. Sacred, candlelit, magical."
        ),
        "variants": [
            {
                "id": "redentore_classical",
                "label": "Classical Redentore Boat Bridge",
                "story": "The traditional July Redentore bridge — 300m pontoon span to the Redentore church, candles along the edges.",
                "color": "#C9A064", "min_floors": 1, "max_floors": 1,
                "suggested_floor_height": 3.0, "suggested_area_sqm": 1500,
                "prompt": (
                    "The classical Redentore pontoon bridge at festival night — long "
                    "300m timber-decked bridge on lashed gondolas and barges spanning "
                    "the Giudecca Canal, thousands of candles lining both edges, "
                    "Church of the Redentore glowing white at the far end. Pilgrims "
                    "walking. Warm Venetian summer night, water reflections."
                ),
                "facade_primary": "timber-decked span on gondola/barge pontoons",
                "facade_secondary": "thousands of votive candles along both edges",
                "facade_ground": "stone embarkation plaza with paving patterns",
                "facade_palette": "warm timber, candle amber, Venetian lagoon dark blue",
                "roof_form": "open air — no roof; flag-lines strung overhead",
                "roof_material": "painted cloth flag-strings (no solid roof)"
            },
            {
                "id": "redentore_candlelit_floating_pavilion",
                "label": "Candlelit Floating Pavilion",
                "story": "A mid-bridge floating pavilion — octagonal gazebo on pontoons, altar + choir + canopy of candles.",
                "color": "#DAA44A", "min_floors": 1, "max_floors": 2,
                "suggested_floor_height": 4.0, "suggested_area_sqm": 80,
                "prompt": (
                    "A mid-bridge floating candlelit pavilion at a Venetian festival "
                    "night — octagonal timber gazebo built on lashed pontoons in the "
                    "middle of a pontoon bridge, a small altar inside, a choir "
                    "singing, canopy of thousands of hanging candles, surrounded by "
                    "pilgrims passing. Warm amber, sacred."
                ),
                "facade_primary": "octagonal timber gazebo on lashed pontoons",
                "facade_secondary": "hanging curtain of thousands of candles",
                "facade_ground": "pontoon platform at water level with candle rings",
                "facade_palette": "warm timber, thousand-candle amber, lagoon-water dark",
                "roof_form": "tent-like timber frame with candle-canopy",
                "roof_material": "timber frame with hanging candle-curtain roof"
            },
            {
                "id": "redentore_silk_canopy_regatta",
                "label": "Silk-Canopy Regatta Pavilion",
                "story": "Regatta Storica floating pavilion — silk-canopied judging stand, flags of medieval Venetian republics.",
                "color": "#B82A45", "min_floors": 1, "max_floors": 2,
                "suggested_floor_height": 4.2, "suggested_area_sqm": 100,
                "prompt": (
                    "A Regatta Storica silk-canopy floating pavilion on the Grand "
                    "Canal — ornate timber judging stand on a barge, draped with red "
                    "and gold silk canopy, hung with medieval Venetian republic "
                    "flags, judges in period costume. Parade of historic boats "
                    "passing. Warm afternoon, festive, historic."
                ),
                "facade_primary": "ornate timber judging stand on barge",
                "facade_secondary": "red and gold silk canopy",
                "facade_ground": "polished barge deck with Venetian rugs",
                "facade_palette": "Venetian red, gold, cream, lagoon green",
                "roof_form": "silk-canopied tent with crown finial",
                "roof_material": "red-and-gold silk canopy"
            },
            {
                "id": "redentore_regatta_gondola_stand",
                "label": "Regatta Gondola Review Stand",
                "story": "Raised gondola-review stand at the Regatta Storica finish — timber tiered stand for spectators, canopy.",
                "color": "#9A7A3E", "min_floors": 1, "max_floors": 3,
                "suggested_floor_height": 3.5, "suggested_area_sqm": 120,
                "prompt": (
                    "A Regatta Gondola Review Stand — raised timber tiered spectator "
                    "stand at the finish of the historic gondola regatta, flag-hung, "
                    "draped canopy, spectators in period costume, gondoliers rowing "
                    "past in bright-painted racing gondolas. Grand Canal palazzi "
                    "behind. Warm historic atmosphere."
                ),
                "facade_primary": "tiered timber spectator stand",
                "facade_secondary": "flag-lines of medieval Venetian banners",
                "facade_ground": "stone quay integration with embankment",
                "facade_palette": "warm timber, flag multicolor, lagoon green, sun-amber",
                "roof_form": "fabric canopy with gold-tassel edges",
                "roof_material": "striped red-and-gold canvas canopy"
            }
        ]
    },

    # ═══════════════ OPENSPACES (4) ═══════════════
    {
        "kind": "openspaces",
        "slug": "festival-matsuri-night-plaza",
        "id": "festival_matsuri_night_plaza",
        "title": "Matsuri Night Market Plaza",
        "subcategory": "Festival",
        "aesthetic_category": "festival_ephemeral",
        "space_type": "plaza",
        "description": (
            "A neighbourhood plaza transformed for summer matsuri nights — "
            "rows of yatai food stalls, hundreds of paper lanterns overhead, "
            "a taiko drum stage, goldfish-scooping games for children, yukata-"
            "clad families. Built in a day, stored in boxes for a year. The "
            "intimate festival scale."
        ),
        "tags": ["festival", "ephemeral", "matsuri", "night-market", "japanese", "plaza"],
        "hero_prompt": (
            "A Japanese matsuri night market plaza at summer evening — dense "
            "rows of yatai wooden food stalls with warm amber lamps, hundreds "
            "of red and white paper lanterns strung overhead, families in "
            "colourful yukata robes strolling, children with goldfish-scoop "
            "games, a small raised taiko drum stage at the plaza centre. "
            "Warm summer night, steam rising from food stalls, paper-lantern "
            "shadows. Joyful, intimate, communal."
        ),
        "suggested_width_m": 40,
        "suggested_depth_m": 40,
        "suggested_area_sqm": 1600,
        "variants": [
            {
                "id": "matsuri_tanabata_star",
                "label": "Tanabata Star Festival Plaza",
                "story": "July star festival — bamboo poles hung with coloured paper wishes and streamers, indigo summer night.",
                "color": "#1A4A8A",
                "prompt": (
                    "A Tanabata star festival plaza at summer evening — tall bamboo "
                    "poles hung with hundreds of coloured paper streamers (fukinagashi) "
                    "and wish-papers (tanzaku) in the wind, paper lantern rows, yatai "
                    "food stalls, families in yukata. Deep indigo sky with first stars. "
                    "Magical, nostalgic."
                )
            },
            {
                "id": "matsuri_obon_ancestor",
                "label": "Obon Ancestor Festival",
                "story": "August ancestor festival — floating candle lanterns on a small pond, Bon dance circle, family reunion.",
                "color": "#D8843C",
                "prompt": (
                    "An Obon ancestor festival plaza at summer night — a central "
                    "circular Bon dance platform (yagura) with taiko drummers on top, "
                    "dancers in yukata circling around, hundreds of floating paper "
                    "candle-lanterns on a small pond reflecting warm light, families "
                    "watching. Sacred, warm, ancestral."
                )
            },
            {
                "id": "matsuri_natsumatsuri_summer",
                "label": "Summer Matsuri Plaza",
                "story": "General summer matsuri — goldfish scoops, cotton candy, shooting games, neighbourhood parade.",
                "color": "#E8504A",
                "prompt": (
                    "A classic Japanese summer matsuri night plaza — dense rows of "
                    "yatai food stalls serving takoyaki and yakisoba, goldfish-scoop "
                    "games, shooting-gallery games, warm paper lanterns, children "
                    "in yukata eating shaved ice. Warm summer night, steam, joyous "
                    "crowd. Nostalgic, alive."
                )
            },
            {
                "id": "matsuri_tsukimi_moon",
                "label": "Tsukimi Moon-Viewing Plaza",
                "story": "September moon festival — silver-pampas susuki grass, moon-viewing platforms, rice dumplings, full moon.",
                "color": "#B8B0A0",
                "prompt": (
                    "A Tsukimi moon-viewing plaza — small raised timber viewing "
                    "platforms with tatami mats arranged on a stone plaza, bundles of "
                    "silver-white susuki pampas grass, small altars with rice dumplings "
                    "and chestnuts, families sipping tea, a giant full moon in the "
                    "sky above. Serene, autumnal, contemplative."
                )
            }
        ]
    },
    {
        "kind": "openspaces",
        "slug": "festival-holi-paint-plaza",
        "id": "festival_holi_paint_plaza",
        "title": "Holi Paint Plaza",
        "subcategory": "Festival",
        "aesthetic_category": "festival_ephemeral",
        "space_type": "plaza",
        "description": (
            "A plaza designed for the Indian Holi festival — wide open "
            "paving for the ecstatic throwing of coloured powders, central "
            "fountain or water-pool for rinsing, perimeter drains for colour "
            "runoff, shaded stalls of powder colours (gulal). A surface "
            "designed to bloom with colour for one day a year."
        ),
        "tags": ["festival", "ephemeral", "holi", "indian", "colour", "spring"],
        "hero_prompt": (
            "A Holi paint plaza at peak festival mid-morning — a wide open "
            "stone plaza covered in clouds of vibrant coloured powders "
            "(pink, yellow, green, blue) thrown and suspended in the air, "
            "dancers drenched in rainbow colour, a central fountain with "
            "coloured water, stalls of pyramids of powder. Crowd of people "
            "of all ages covered head-to-toe in colour, smiling. Ecstatic, "
            "vibrant, joyful."
        ),
        "suggested_width_m": 50,
        "suggested_depth_m": 50,
        "suggested_area_sqm": 2500,
        "variants": [
            {
                "id": "holi_mathura_krishna",
                "label": "Mathura Krishna Birthplace Plaza",
                "story": "The mythic Mathura Holi — sacred birthplace of Krishna, most exuberant celebration.",
                "color": "#E84A9E",
                "prompt": (
                    "A Mathura Holi paint plaza at peak mid-morning — ancient stone "
                    "plaza near a Krishna temple, clouds of vibrant pink, yellow, "
                    "and green powder in the air, dancers covered head to toe, "
                    "musicians with dhol drums, Hindu temple spires visible behind. "
                    "Ecstatic, devotional, overwhelming colour."
                )
            },
            {
                "id": "holi_banaras_ghat",
                "label": "Banaras Ghat Holi",
                "story": "Varanasi ghats Holi — colour-powder thrown into the Ganges, ancient stone steps.",
                "color": "#C4702A",
                "prompt": (
                    "A Holi paint plaza on the Banaras ghats at morning — ancient stone "
                    "ghat steps down to the Ganges, clouds of saffron and crimson "
                    "powders in the air, pilgrims covered in colour, sadhus with faces "
                    "painted, some jumping into the river. Sacred river, ancient, "
                    "luminous."
                )
            },
            {
                "id": "holi_rural_punjab",
                "label": "Rural Punjab Village Holi",
                "story": "Village courtyard Holi — mustard field backdrop, folk dhol drummers, wheat harvest celebration.",
                "color": "#D8B828",
                "prompt": (
                    "A rural Punjab village Holi plaza — a clay-packed village "
                    "courtyard at morning, yellow mustard fields visible beyond, "
                    "clouds of coloured powder, villagers in traditional dress "
                    "covered in pinks and yellows, dhol drummers, children running. "
                    "Warm spring light, joyous."
                )
            },
            {
                "id": "holi_diaspora_global",
                "label": "Global Diaspora Holi",
                "story": "Modern international Holi — global celebration in urban park, Bollywood music, diverse crowd.",
                "color": "#8A4AC8",
                "prompt": (
                    "A contemporary global-diaspora Holi celebration in an urban park "
                    "plaza — diverse international crowd of all backgrounds covered in "
                    "rainbow powder, Bollywood music, big speakers, water-spray "
                    "archways. Modern city backdrop. Joyful, inclusive, vibrant."
                )
            }
        ]
    },
    {
        "kind": "openspaces",
        "slug": "festival-burning-man-camp",
        "id": "festival_burning_man_camp",
        "title": "Burning Man Playa Camp",
        "subcategory": "Festival",
        "aesthetic_category": "festival_ephemeral",
        "space_type": "plaza",
        "description": (
            "A desert temporary commune plaza for week-long festival — "
            "sculptural art installations, geodesic dome shelters, shade "
            "sails, communal kitchens, fire-sculpture at the centre, "
            "costumed participants. Built from scratch on alkali flats in "
            "one week, leaves no trace in the next."
        ),
        "tags": ["festival", "ephemeral", "burning-man", "desert", "commune", "radical"],
        "hero_prompt": (
            "A Burning Man playa camp at dusk — open alkali-flat desert "
            "with clusters of geodesic domes, hexayurts, shade sails on "
            "lightweight poles, a tall sculptural wooden structure being "
            "prepared for burning, art cars passing, costumed participants. "
            "Dusty pale light, Milky Way beginning above, warm camp fires. "
            "Creative, radical, magical."
        ),
        "suggested_width_m": 200,
        "suggested_depth_m": 200,
        "suggested_area_sqm": 40000,
        "variants": [
            {
                "id": "burning_art_camp",
                "label": "Monumental Art Camp",
                "story": "Sculpture-focused camp — giant wooden and steel art installations, interactive pieces, around a central temple.",
                "color": "#C9A065",
                "prompt": (
                    "A Burning Man art camp at dusk — tall monumental wooden "
                    "sculpture installations (10-20m tall figures, spires, geometric "
                    "forms), scattered on the open playa, art-car vehicles driving "
                    "between them, small geodesic living domes at the edges. Dust in "
                    "the air, golden hour light. Creative, monumental."
                )
            },
            {
                "id": "burning_sound_camp",
                "label": "Sound Stage Camp",
                "story": "Music-focused camp — giant speaker arrays, DJ booth platform, laser lights, dance crowd.",
                "color": "#3A3A8A",
                "prompt": (
                    "A Burning Man sound stage camp at night — massive speaker-array "
                    "stacks on a raised stage, DJ booth platform with laser lights "
                    "cutting through dust, hundreds of dancers in costume and neon, "
                    "open desert plain around. Vibrant, loud, magical."
                )
            },
            {
                "id": "burning_healing_camp",
                "label": "Healing Sanctuary Camp",
                "story": "Tranquil healing camp — yoga domes, tea pavilion, hammocks, quiet sacred-geometry garden.",
                "color": "#E8D8C0",
                "prompt": (
                    "A Burning Man healing sanctuary camp at morning — cluster of "
                    "pale fabric yoga domes, a tea pavilion with Persian rugs, "
                    "hammocks strung between poles, a sacred-geometry sand garden. "
                    "Serene, dusty pale light, tranquil."
                )
            },
            {
                "id": "burning_fire_conclave",
                "label": "Fire Conclave Temple",
                "story": "The temple burn — giant wooden temple structure, fire dancers, crowd circling for the final ritual.",
                "color": "#F2502A",
                "prompt": (
                    "A Burning Man fire conclave temple at night — giant wooden "
                    "temple structure (15m tall) at the centre with open archways, "
                    "ring of fire dancers with fire poi spinning flame, concentric "
                    "crowd watching silently. Deep desert night, stars above, "
                    "sacred, fiery, awe-inducing."
                )
            }
        ]
    },
    {
        "kind": "openspaces",
        "slug": "festival-midsummer-bonfire",
        "id": "festival_midsummer_bonfire",
        "title": "Midsummer Bonfire Garden",
        "subcategory": "Festival",
        "aesthetic_category": "festival_ephemeral",
        "space_type": "park",
        "description": (
            "A Nordic / Celtic / Slavic midsummer festival park — a central "
            "towering bonfire, maypole or flower-wreath-pole, long community "
            "dining tables, flower-crowned participants, folk musicians. The "
            "longest-day celebration lit by the latest-setting sun."
        ),
        "tags": ["festival", "ephemeral", "midsummer", "bonfire", "solstice", "nordic", "celtic"],
        "hero_prompt": (
            "A Nordic midsummer bonfire garden at white night — a central "
            "towering 5m bonfire sending sparks into a pale summer sky, a tall "
            "flower-decorated maypole in the middle of a meadow, long timber "
            "community dining tables covered in white cloths and wildflowers, "
            "participants wearing flower crowns. Pale Nordic white night, "
            "magical, communal."
        ),
        "suggested_width_m": 80,
        "suggested_depth_m": 80,
        "suggested_area_sqm": 6400,
        "variants": [
            {
                "id": "midsummer_scandinavian",
                "label": "Scandinavian Midsommar",
                "story": "Swedish/Finnish midsommar — maypole dance, flower crowns, lake-side, white-night celebration.",
                "color": "#9AD67A",
                "prompt": (
                    "A Scandinavian Midsommar festival garden — a tall flower-"
                    "decorated maypole (midsommarstång) in the centre of a green "
                    "meadow, families and children in folk dress dancing around it, "
                    "long dining tables with herring and aquavit, birch leaves "
                    "everywhere, a still lake in the background. Pale white-night "
                    "light, magical."
                )
            },
            {
                "id": "midsummer_baltic_janis",
                "label": "Baltic Jāņi Fire",
                "story": "Latvian/Lithuanian Jāņi — oak-leaf crowns, cheese-and-beer, towering bonfire, herbal medicine gathering.",
                "color": "#E8A04A",
                "prompt": (
                    "A Baltic Jāņi midsummer festival — a towering 6-meter bonfire "
                    "of pine logs in a meadow at twilight, participants in oak-leaf "
                    "crowns and flower wreaths, long wooden tables with traditional "
                    "cheese and beer, folk singers. Forest edge visible. Warm, "
                    "pagan, communal."
                )
            },
            {
                "id": "midsummer_slavic_kupala",
                "label": "Slavic Kupala Night",
                "story": "Ukrainian/Polish Kupala — flower-crown floating ritual on a river, leaping over fires, wild herbs.",
                "color": "#C8A0D6",
                "prompt": (
                    "A Slavic Kupala Night midsummer festival — young women in "
                    "traditional embroidered dress floating flower wreaths with small "
                    "candles on a gentle river at dusk, a towering bonfire on the "
                    "bank, participants leaping over it, folk singers. Romantic, "
                    "ritualistic, magical."
                )
            },
            {
                "id": "midsummer_basque_san_juan",
                "label": "Basque San Juan Night",
                "story": "Basque San Juan — coastal bonfire on a beach, leaping over fires at midnight, families swimming.",
                "color": "#D65A3A",
                "prompt": (
                    "A Basque San Juan midsummer festival on a beach at night — "
                    "a towering bonfire on the sand, families leaping over small "
                    "fires for luck, drumming, children running, ocean in the "
                    "background. Warm Mediterranean summer night, communal."
                )
            }
        ]
    },

    # ═══════════════ STREETS (4) ═══════════════
    {
        "kind": "streets",
        "slug": "festival-procession-way",
        "id": "festival_procession_way",
        "title": "Semana Santa Procession Way",
        "subcategory": "Festival",
        "aesthetic_category": "festival_ephemeral",
        "description": (
            "A ceremonial street activated during religious festival weeks — "
            "flower-carpeted paving, tall banners, candle-lined edges, "
            "balcony curtains, incense-smoke clouds, processional float "
            "(paso) borne by costaleros. Built for one week a year, "
            "transformed back to everyday life in a night."
        ),
        "tags": ["festival", "ephemeral", "procession", "catholic", "holy-week", "paso"],
        "hero_prompt": (
            "A Semana Santa procession street at night — narrow cobbled "
            "street in an old Spanish city, flower-petal carpet patterns on "
            "the stones, thousands of candles lining both edges, massive "
            "carved-and-gilded processional float (paso) being carried by "
            "costaleros, incense smoke, hooded nazareno processioners with "
            "candles, balcony viewers. Warm candle-amber light, sacred, "
            "solemn."
        ),
        "suggested_width_m": 8,
        "variants": [
            {
                "id": "procession_sevilla",
                "label": "Sevilla Semana Santa",
                "story": "Seville Holy Week — ornate gilt pasos, hooded processioners, baroque Andalucian streets.",
                "color": "#D2B048",
                "prompt": (
                    "A Sevilla Semana Santa procession at night — a massive ornate "
                    "gilt Baroque paso of the Virgin Mary carried by unseen costaleros "
                    "swaying gently down a narrow Andalucian cobbled street, dozens "
                    "of white-hooded nazareno processioners with candles, balcony "
                    "viewers in dark dress, warm candlelight, incense. Sacred, "
                    "dramatic, haunting."
                )
            },
            {
                "id": "procession_guatemala_alfombra",
                "label": "Guatemala Alfombra Procession",
                "story": "Guatemalan Semana Santa — intricate dyed-sawdust carpets (alfombras) on the street, colonial buildings.",
                "color": "#E8743A",
                "prompt": (
                    "A Guatemalan Semana Santa alfombra procession in Antigua — "
                    "ornate dyed-sawdust carpet patterns (alfombra) covering the "
                    "entire cobbled colonial street in elaborate colourful designs, "
                    "a processional Christ float being carried over them, colourful "
                    "Antigua pastel colonial buildings, priests in purple. Warm "
                    "morning light."
                )
            },
            {
                "id": "procession_philippines",
                "label": "Philippines Penitensya",
                "story": "Filipino Holy Week — carabao-pulled karozas, elaborate floral floats, tropical heat.",
                "color": "#B8CD5A",
                "prompt": (
                    "A Filipino Holy Week procession — massive elaborate floral "
                    "karozas (Christ floats) pulled by water buffalo (carabao) "
                    "through a tropical town street, bright tropical flowers "
                    "covering the floats, barefoot penitents, palm-thatched "
                    "houses. Warm tropical afternoon."
                )
            },
            {
                "id": "procession_oaxaca_velas",
                "label": "Oaxaca Velas Candlelit",
                "story": "Oaxacan Mexican Velas — candlelit procession with folk musicians, marigolds, colonial stone.",
                "color": "#C85060",
                "prompt": (
                    "An Oaxacan Velas candlelit procession at night — narrow stone "
                    "street in colonial Oaxaca, thousands of small clay candle "
                    "holders lining the edges, procession of folk musicians with "
                    "guitars and violins, women in traditional Oaxacan dress "
                    "carrying marigold bouquets, church in the background. Warm "
                    "festive night."
                )
            }
        ]
    },
    {
        "kind": "streets",
        "slug": "festival-night-market-lane",
        "id": "festival_night_market_lane",
        "title": "Night Market Festival Lane",
        "subcategory": "Festival",
        "aesthetic_category": "festival_ephemeral",
        "description": (
            "A street transformed into a linear night market for festival "
            "nights — rows of food stalls, strung lanterns, cooking smoke, "
            "dense crowds of eaters. Built at dusk, dismantled before dawn, "
            "every night of the festival. The urban ritual of street-food "
            "communion."
        ),
        "tags": ["festival", "ephemeral", "night-market", "food", "street-food", "asian"],
        "hero_prompt": (
            "A dense night-market festival lane at evening — narrow urban "
            "street transformed with rows of food stalls on both sides, "
            "hundreds of warm paper lanterns strung overhead, dense happy "
            "crowd of eaters, cooking steam and smoke rising, warm amber "
            "light reflecting off wet pavement. Vibrant, alive, hungry."
        ),
        "suggested_width_m": 6,
        "variants": [
            {
                "id": "night_market_taipei_shilin",
                "label": "Taipei Shilin Night Market",
                "story": "Taiwan's most famous night market — xiaolongbao, stinky tofu, bubble tea, red lanterns.",
                "color": "#D83848",
                "prompt": (
                    "A Taipei Shilin night market lane at festival evening — narrow "
                    "pedestrian lane crammed with food stalls serving stinky tofu, "
                    "bubble tea, xiaolongbao, oyster omelette, red paper lanterns "
                    "strung overhead, dense crowd of eaters, steam and smoke. Warm "
                    "humid Taiwan evening, vibrant."
                )
            },
            {
                "id": "night_market_bangkok_boat",
                "label": "Bangkok Khlong Boat Market",
                "story": "Thai floating boat night market — boats moored along a canal selling food, lanterns, tropical night.",
                "color": "#E09A3A",
                "prompt": (
                    "A Bangkok khlong canal boat night market at festival night — "
                    "dozens of wooden food boats moored along a small canal, warm "
                    "lamps, cooking steam, diners sitting at canal-edge tables, "
                    "lantern reflections on the water. Tropical humid night, "
                    "magical."
                )
            },
            {
                "id": "night_market_jemaa_fnaa",
                "label": "Marrakech Jemaa El-Fnaa",
                "story": "Marrakech's famous square at night — food stalls, snake charmers, storytellers, orange-lamp haze.",
                "color": "#C06828",
                "prompt": (
                    "Marrakech's Jemaa El-Fnaa square at festival night — dozens of "
                    "food stalls with orange lamps, smoke from grilling meats, snake "
                    "charmers with flutes, storytellers drawing circles of listeners, "
                    "Koutoubia minaret silhouette behind. Orange-hazed magical "
                    "North African night."
                )
            },
            {
                "id": "night_market_osaka_dotonbori",
                "label": "Osaka Dotonbori Lane",
                "story": "Japan's iconic neon-lit food lane — takoyaki, okonomiyaki, giant signage, canal reflections.",
                "color": "#3A5088",
                "prompt": (
                    "An Osaka Dotonbori night market lane — narrow canal-side street "
                    "packed with dense neon signs (giant crab, running man), takoyaki "
                    "and okonomiyaki stalls, dense crowd, canal reflections below. "
                    "Vibrant, loud, iconic Japanese nightlife."
                )
            }
        ]
    },
    {
        "kind": "streets",
        "slug": "festival-chariot-procession",
        "id": "festival_chariot_procession",
        "title": "Ritual Chariot Procession Avenue",
        "subcategory": "Festival",
        "aesthetic_category": "festival_ephemeral",
        "description": (
            "A wide avenue activated for ritual chariot or sacred-vehicle "
            "processions — Jagannath Rathyatra, Perahera, Cham, Yamaboko "
            "Junko. Towering sacred wheeled structures drawn by thousands "
            "of devotees, the street itself becoming the altar. Built into "
            "the city plan to accommodate these annual ritual passages."
        ),
        "tags": ["festival", "ephemeral", "procession", "chariot", "ritual", "ratha"],
        "hero_prompt": (
            "A ritual chariot procession avenue at peak day — wide stone "
            "street with a towering 15-meter sacred wooden chariot being "
            "pulled by thousands of devotees with long ropes, ornate "
            "ornament, flags, priests on the chariot, dense devotional "
            "crowd lining both sides. Warm festival afternoon, sacred."
        ),
        "suggested_width_m": 30,
        "variants": [
            {
                "id": "chariot_jagannath_puri",
                "label": "Jagannath Rathyatra Puri",
                "story": "India's ancient chariot festival — three towering wooden chariots to Jagannath temple, millions of devotees.",
                "color": "#D82828",
                "prompt": (
                    "A Jagannath Rathyatra chariot procession at Puri — a towering "
                    "15-meter wooden chariot with red-and-yellow painted ornament, "
                    "umbrella-topped, being pulled by thousands of devotees with "
                    "thick ropes along a wide stone avenue toward a Hindu temple "
                    "complex. Dense devotional crowd. Warm Indian afternoon, sacred."
                )
            },
            {
                "id": "chariot_sinhala_perahera",
                "label": "Sinhala Esala Perahera",
                "story": "Kandy's tooth-relic procession — caparisoned elephants, fire-twirlers, drummers, Sri Lankan Buddhist.",
                "color": "#F2B03C",
                "prompt": (
                    "A Sinhala Esala Perahera procession in Kandy Sri Lanka — "
                    "majestic elephants in elaborate gold-and-red caparisons, fire-"
                    "twirlers, Kandyan drummers in red and white, carrying a sacred "
                    "relic casket, dense crowd, temple in background. Warm tropical "
                    "night, sacred, spectacular."
                )
            },
            {
                "id": "chariot_tibetan_cham",
                "label": "Tibetan Cham Dance Procession",
                "story": "Tibetan Buddhist monastic dance-procession — masked lamas, long horns, red monastic robes, mountains.",
                "color": "#883A50",
                "prompt": (
                    "A Tibetan Cham dance procession at a mountain monastery — masked "
                    "lamas in elaborate brocade costumes with skull masks, long "
                    "Tibetan dungchen horns, red-robed monks, dance movements, snow-"
                    "capped Himalayan peaks behind. Sacred, ceremonial, ancient."
                )
            },
            {
                "id": "chariot_yamaboko_junko",
                "label": "Kyoto Yamaboko Junko",
                "story": "Gion Matsuri's grand procession — 32 tall float-chariots pulled through Kyoto's ancient streets.",
                "color": "#C8702E",
                "prompt": (
                    "A Kyoto Yamaboko Junko procession — a 25-meter tall wheeled "
                    "festival float hung with Persian tapestries, pulled by dozens "
                    "of men in white costumes through a Kyoto street lined with "
                    "ancient machiya townhouses, golden afternoon light, musicians "
                    "on the float. Sacred, historic, majestic."
                )
            }
        ]
    },
    {
        "kind": "streets",
        "slug": "festival-carnival-parade-avenue",
        "id": "festival_carnival_parade_avenue",
        "title": "Carnival Parade Avenue",
        "subcategory": "Festival",
        "aesthetic_category": "festival_ephemeral",
        "description": (
            "A wide urban avenue designed to host Carnival parade — permanent "
            "bleacher seating, amplifier towers, float-route width, dancers' "
            "changing tents. Activated once a year for peak public ritual, "
            "dormant otherwise. The civic stage for a city's ecstatic "
            "self-performance."
        ),
        "tags": ["festival", "ephemeral", "carnival", "parade", "samba", "public-ritual"],
        "hero_prompt": (
            "A Carnival parade avenue at peak night — wide urban street with "
            "bleacher stands full of spectators on both sides, a massive "
            "ornate samba-school float passing with giant feathered figures, "
            "dancers in sequinned costumes in the front, percussion battery "
            "at the rear, confetti and streamers raining down, warm stadium "
            "lighting. Ecstatic, loud, vibrant."
        ),
        "suggested_width_m": 35,
        "variants": [
            {
                "id": "carnival_rio_sambodromo",
                "label": "Rio Sambódromo",
                "story": "Rio's iconic parade corridor — concrete bleachers, samba-school floats, million-strong spectators.",
                "color": "#F2C040",
                "prompt": (
                    "Rio's Sambódromo parade avenue at Carnival night — wide concrete "
                    "avenue with tall bleachers packed with tens of thousands of "
                    "spectators on both sides, a massive tropical-themed samba "
                    "school float with 15-meter feather-headdressed dancer figures, "
                    "60 percussionists, confetti. Ecstatic, iconic."
                )
            },
            {
                "id": "carnival_salvador_blocos",
                "label": "Salvador Blocos Parade",
                "story": "Bahia Salvador's block-party Carnival — trio elétrico sound-trucks, dense dancing street crowd, Afro-Bahian.",
                "color": "#7A3A9A",
                "prompt": (
                    "A Salvador Bahia Carnival blocos parade street — giant trio "
                    "elétrico sound-truck with speakers and live musicians on top, "
                    "dense dancing crowd following it through the street, colonial "
                    "Pelourinho architecture on both sides. Warm tropical evening, "
                    "vibrant."
                )
            },
            {
                "id": "carnival_trinidad_mas",
                "label": "Trinidad Mas Band Parade",
                "story": "Trinidad's mas-band parade — elaborate Caribbean feather-costumes, steel-pan orchestras, limbo.",
                "color": "#E85AA4",
                "prompt": (
                    "A Trinidad Carnival mas-band parade — thousands of masqueraders "
                    "in elaborate feather-and-sequin costumes in a wide Port of Spain "
                    "street, steel-pan orchestra on a float, warm Caribbean sun, "
                    "dense crowd. Vibrant, tropical, joyful."
                )
            },
            {
                "id": "carnival_oruro_diablada",
                "label": "Oruro Diablada Parade",
                "story": "Bolivian Andean Carnival — elaborate devil and angel masked dancers, high-altitude ritual, folk.",
                "color": "#C82A2A",
                "prompt": (
                    "An Oruro Bolivia Diablada Carnival parade — elaborate devil-"
                    "masked dancers in red and gold costumes with horns, angel "
                    "dancers in white, folk musicians with panpipes and drums, high-"
                    "altitude Andean town, UNESCO heritage. Sacred-festive, "
                    "colourful."
                )
            }
        ]
    },
]


# ---------------------------------------------------------------------------
# Shared pipeline (identical to experimental/utopic scripts)
# ---------------------------------------------------------------------------


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
        "laneCount": 2, "hasSidewalk": True, "shape": "linear",
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
    print(f"Processing {len(targets)} Festival archetype(s){' (DRY RUN)' if dry_run else ''}\n")
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
    print(f"\n=== Done: {successes}/{len(targets)} Festival archetypes completed ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
