"""Compose 5 new Civic Plaza archetype entries as JSON-valid text.

Writes the entries to scripts/_civic_plazas_snippet.json so we can splice
them as raw text into openSpaceArchetypes.json (per CLAUDE.md NEVER
json.dump rule applied to openSpaceArchetypes.json — we generate the
snippet here as a STAND-ALONE JSON, not by parse-modify-dumping the
catalog).

Run:  python scripts/_compose_new_civic_plazas.py
Output: scripts/_civic_plazas_snippet.json (text snippet to splice)
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def variant(vid, label, color, description, min_area, max_area, suggested_area, slug):
    return {
        "id": vid,
        "label": label,
        "color": color,
        "description": description,
        "thumbnailUrl": f"/archetypes/openspaces/{slug}/variant_{vid.split('_v')[-1]}.png",
        "minAreaSqm": min_area,
        "maxAreaSqm": max_area,
        "suggestedAreaSqm": suggested_area,
    }


def archetype(*, id, slug, title, description, tags, landscape_character,
              paving, planting, seating, water, openness, prompt_subject,
              prompt_details, prompt_negative, property_presets,
              variants_data, render_overlay, render_roof, render_negative,
              suggested_w, suggested_d, min_w, max_w, min_d, max_d,
              min_area, max_area, suggested_area, aspect_ratio, shape):
    return {
        "id": id,
        "suggestedWidth_m": suggested_w,
        "suggestedDepth_m": suggested_d,
        "minWidth_m": min_w,
        "maxWidth_m": max_w,
        "minDepth_m": min_d,
        "maxDepth_m": max_d,
        "minAreaSqm": min_area,
        "maxAreaSqm": max_area,
        "aspectRatio": aspect_ratio,
        "shape": shape,
        "title": title,
        "aestheticCategory": "civic_plazas",
        "spaceType": "plaza",
        "description": description,
        "generationTags": tags,
        "styleProfile": {
            "landscapeCharacter": landscape_character,
            "pavingType": paving,
            "plantingType": planting,
            "seatingRealm": seating,
            "waterFeatures": water,
            "opennessEnclosure": openness,
        },
        "prompt": {
            "subject": prompt_subject,
            "details": prompt_details,
            "negative": prompt_negative,
        },
        "propertyPresets": property_presets,
        "suggestedAreaSqm": suggested_area,
        "thumbnailUrl": f"/archetypes/openspaces/{slug}/variant_0.png",
        "variants": variants_data,
        "renderPrompt": {
            "mapOverlay": render_overlay,
            "roofView": render_roof,
            "negative": render_negative,
        },
        "districtKit": None,
    }


# ---------------------------------------------------------------------------
# 1) City Hall / Government Plaza
# ---------------------------------------------------------------------------
city_hall = archetype(
    id="city_hall_government_plaza",
    slug="city-hall-government-plaza",
    title="City Hall / Government Plaza",
    description="A formal civic plaza fronting a city hall, courthouse, or government building, used for ceremonies, public assembly, and everyday political life",
    tags=["plaza", "civic", "government", "city-hall", "ceremonial"],
    landscape_character=(
        "A civic plaza fronting a government or city hall building seen from drone altitude. "
        "The plaza is a strong rectangular hardscape footprint anchored on its long edge by "
        "the steps and entry of a public institutional building. The pavement is a dignified "
        "pattern of large stone or precast concrete pavers in a regular grid, with a clear "
        "axial path running from the street edge up to the building entrance. A central focal "
        "element — flagpole cluster, monument, fountain, or a flat ceremonial speakers' area — "
        "sits midway along the axis. Formal symmetric tree planting (paired clipped allées, "
        "sentinel trees, or geometric tree blocks) flanks both sides of the axial path. Low "
        "stone or granite curbs separate the plaza from the surrounding street. From above, "
        "the plaza reads as a strict rectangular hardscape with a clear central axis and "
        "mirror-symmetric planting and seating along its long sides."
    ),
    paving="Large stone or precast concrete pavers in a regular ceremonial grid pattern",
    planting="Formal symmetric tree planting — paired allées, sentinel trees, or geometric tree blocks",
    seating="Stone benches at the perimeter, low planter walls, occasional stepped seating near the focal element",
    water="Optional axial fountain or reflecting pool aligned with the building entrance",
    openness="Strongly open hardscape framed by the institutional building on one side and city streets on the others",
    prompt_subject="Aerial view of a formal civic plaza fronting a government or city hall building",
    prompt_details=[
        "Strong rectangular hardscape with regular paver grid pattern visible",
        "Axial path running from street edge to the building entrance",
        "Central focal element — flagpole cluster, monument, or fountain — on the axis",
        "Symmetric tree planting flanking both sides of the axis",
        "Low stone curb edges separating plaza from streets",
        "Surrounding institutional and downtown buildings forming the civic context",
    ],
    prompt_negative=[
        "No chaotic asymmetric planting",
        "No suburban lawn surface dominating the plaza",
        "No parking lot inside the plaza",
        "No text overlays",
    ],
    property_presets={
        "tree_density_level": "low",
        "tree_density": 0.2,
        "has_paths": True,
        "has_benches": True,
        "shade_strategy": "axial_allees",
    },
    variants_data=[
        variant(
            "city_hall_government_plaza_v0", "Compact Civic Forecourt", "#5B7065",
            "Smaller-scale contemporary civic plaza, roughly 50 by 50 meters of pale granite paver hardscape stepping up to a contemporary glass-and-stone municipal building. A pair of flagpoles flanks a low bronze plaque on the central axis; a clipped row of pleached lindens lines each side of the axis. A single broad granite step runs across the building face. Paired stone benches with cast-iron lighting bollards punctuate the perimeter. Surrounding context shows a downtown commercial street with mid-rise buildings.",
            1500, 3500, 2500, "city-hall-government-plaza"),
        variant(
            "city_hall_government_plaza_v1", "Historic European Senate Square", "#8B7355",
            "Historic European-style government square, roughly 80 by 75 meters of cobblestone paving in a radiating fan pattern. A neoclassical cathedral or government building anchors one long edge with a columned portico and dome rising above the rooftop line. A single bronze equestrian or imperial monument sits at the geometric center on a tall stone pedestal. Cobblestones radiate outward in concentric rings around the monument. Stone bollards mark the perimeter. Surrounding context shows older 4-6 storey neoclassical institutional buildings facing onto the square.",
            4000, 9000, 6000, "city-hall-government-plaza"),
        variant(
            "city_hall_government_plaza_v2", "Mid-Century Modernist Civic Plaza", "#708090",
            "Mid-century modernist civic plaza, roughly 100 by 100 meters anchored by a sculptural arched concrete proscenium. A large rectangular reflecting pool with low stone coping fills the central area, doubling as a winter skating rink. Sweeping concrete walkways curve around the pool. A pair of curved tower-form government buildings rises behind the proscenium. Stepped concrete plinths and angular planting beds with clipped boxwood frame the entry. Surrounding context shows a 1960s downtown core with massing slabs and brutalist neighbours.",
            7000, 12000, 10000, "city-hall-government-plaza"),
        variant(
            "city_hall_government_plaza_v3", "Brutalist Civic Forecourt", "#5C5C5C",
            "Brutalist civic forecourt, roughly 150 by 100 meters of vast brick-and-concrete hardscape sloping gently up to the inverted-pyramid mass of a heavy concrete city hall. The brick paving runs in long parallel bands with periodic stone bands marking ceremonial axes. Several broad stepped tiers — concrete benches doubling as low retaining walls — break up the slope. A small grove of mature honey-locust trees clusters off-axis as the only soft element. Flagpoles cluster at the building face. Surrounding context shows a 1960s government district with concrete office slabs.",
            10000, 15000, 13000, "city-hall-government-plaza"),
    ],
    render_overlay="Replace the colored zone with a photorealistic civic plaza fronting a city hall or government building. Rectangular hardscape with a regular paver grid. Axial path running from street to building entrance. Central focal element — flagpole, monument, or fountain — on the axis. Symmetric tree planting flanking the axis. Low stone curb edges. Surrounding institutional buildings reading as civic context. Keep surrounding satellite map context exactly as-is. Oblique aerial view, midday sun, sharp shadows, photorealistic, 8k.",
    render_roof="Replace the colored zone viewed from directly above with a hard-paved civic plaza. Regular paver grid pattern. Strong central axis with focal element at midpoint. Symmetric tree canopy circles flanking the axis. Building footprint visible at one edge. Keep surrounding context exactly as-is.",
    render_negative="cartoon, illustration, sketch, low quality, blurry, text, watermark, unrealistic colors, suburban lawn, irregular asymmetric planting, parking lots inside the plaza",
    suggested_w=70, suggested_d=80, min_w=30, max_w=160, min_d=30, max_d=200,
    min_area=1500, max_area=15000, suggested_area=5000,
    aspect_ratio="1:1.15", shape="rectangular",
)


# ---------------------------------------------------------------------------
# 2) Sunken Plaza
# ---------------------------------------------------------------------------
sunken_plaza = archetype(
    id="sunken_plaza",
    slug="sunken-plaza",
    title="Sunken Plaza",
    description="A below-grade urban plaza set into the city fabric, with steps or ramps descending from the surrounding street level into a programmable lower court ringed by retail, café terraces, or transit access",
    tags=["plaza", "sunken", "below-grade", "urban", "ceremonial"],
    landscape_character=(
        "A sunken urban plaza seen from drone altitude. The plaza is set roughly one storey "
        "below the surrounding street grade, accessed by a continuous run of broad shallow "
        "steps wrapping two or three sides like an amphitheatre, plus an accessible ramp on "
        "the fourth side. The lower-court floor is a single hardscape — granite slabs, "
        "polished concrete, or stone tiles — with a strong geometric pattern visible from "
        "above. The court is ringed at its lower level by café terraces, small retail "
        "frontages, or arched transit-station entrances tucked under the surrounding "
        "buildings. A central focal element — fountain pool, sculpture, or seasonal feature "
        "(skating rink in winter, shallow water mirror in summer) — anchors the plaza floor. "
        "Planters with trees soften the upper rim. From above, the plaza reads as a clean "
        "rectangular pit framed by stepped seating tiers with an active programmable floor."
    ),
    paving="Granite slabs, polished concrete, or stone tile in a strong geometric floor pattern",
    planting="Tree planters along the upper rim and at lower-court corners; minimal ground-level planting",
    seating="Continuous stepped tiers wrapping the upper edge, café-terrace seating along the lower frontages",
    water="Central seasonal feature — fountain pool, skating rink, or reflecting water mirror",
    openness="Below-grade enclosure on three or four sides with strong vertical containment by surrounding buildings",
    prompt_subject="Aerial view of a sunken urban plaza set below street grade with stepped seating tiers wrapping the edge",
    prompt_details=[
        "Lower-court floor as a single hardscape rectangle with strong geometric paving pattern",
        "Continuous stepped seating tiers wrapping two or three sides of the plaza",
        "Café terraces, small retail, or transit-station entrances ringing the lower level",
        "Central focal element — fountain, sculpture, or seasonal feature — on the plaza floor",
        "Tree planters along the upper rim softening the edge",
        "Surrounding mid- or high-rise buildings forming a strong vertical enclosure",
    ],
    prompt_negative=[
        "No flat at-grade plaza — must clearly read as below street level",
        "No suburban lawn surface",
        "No parking inside the plaza",
        "No text overlays",
    ],
    property_presets={
        "tree_density_level": "low",
        "tree_density": 0.15,
        "has_paths": True,
        "has_benches": True,
        "shade_strategy": "rim_planters",
    },
    variants_data=[
        variant(
            "sunken_plaza_v0", "Intimate Courtyard Bowl", "#8B7355",
            "Small intimate sunken courtyard, roughly 25 by 30 meters of stone-tiled lower-court floor accessed by three sides of broad shallow steps. A simple central fountain pool with a low bronze sculpture sits at the focal point. Two cafés with retractable awnings open onto the lower floor at one edge; a clipped boxwood hedge runs along the rim. Surrounding context shows a continuous mid-rise European mixed-use block with limestone facades.",
            600, 1500, 800, "sunken-plaza"),
        variant(
            "sunken_plaza_v1", "Rockefeller-style Café & Rink Terrace", "#B8860B",
            "Iconic Rockefeller-style sunken plaza, roughly 50 by 30 meters of polished granite floor doubling as a winter ice rink and summer café terrace. A large gilded mythological statue dominates one short edge of the lower court. Café terraces with awning-shaded tables ring the long sides at the lower level. A continuous run of broad granite steps wraps the upper rim, dotted with planters of seasonal flowers. A tall holiday tree sits behind the statue in winter context. Surrounding context shows tall art-deco-era commercial towers.",
            1500, 3500, 2500, "sunken-plaza"),
        variant(
            "sunken_plaza_v2", "Corporate Atrium Tier", "#708090",
            "Modernist corporate sunken plaza, roughly 70 by 60 meters of poured concrete tiers stepping down through three levels to a central paved court. A geometric abstract sculpture anchors the center; concrete planters with grasses and small trees punctuate each tier. Glass curtain-wall office tower lobbies open onto the lower court. Pedestrian skybridges cross above. Surrounding context shows a 1980s corporate downtown with reflective-glass towers.",
            3500, 5500, 4500, "sunken-plaza"),
        variant(
            "sunken_plaza_v3", "Asian Transit-Integrated Sunken Plaza", "#5B7065",
            "Large Asian-style transit-integrated sunken plaza, roughly 80 by 75 meters of patterned terrazzo floor accessed by escalators and broad stair tiers from the surrounding street. The lower court is partially covered by a translucent steel-and-glass canopy. Subway and rail station entrances ring the lower level alongside a continuous arc of small retail frontages. Digital displays and lantern columns punctuate the floor. Manicured tree planters with bonsai-style shaping anchor the corners. Surrounding context shows a dense Asian megacity downtown with mixed-use towers.",
            5000, 6000, 5500, "sunken-plaza"),
    ],
    render_overlay="Replace the colored zone with a photorealistic sunken plaza set below street grade. Lower-court hardscape floor with strong geometric paving pattern. Continuous stepped seating tiers wrapping two or three sides. Café terraces, retail, or transit entrances at the lower level. Central focal element — fountain, sculpture, or seasonal feature. Tree planters along the upper rim. Surrounding mid- and high-rise buildings forming vertical enclosure. Keep surrounding satellite map context exactly as-is. Oblique aerial view, late-afternoon sun, sharp shadows, photorealistic, 8k.",
    render_roof="Replace the colored zone viewed from directly above with a sunken hardscape rectangle clearly stepped down from street grade. Stepped seating tiers visible as concentric ring shadows around the lower court. Geometric paving pattern on the lower floor. Central focal element shadow. Tree planter shapes along the rim. Keep surrounding context exactly as-is.",
    render_negative="cartoon, illustration, sketch, low quality, blurry, text, watermark, unrealistic colors, flat at-grade plaza, suburban lawn, parking lots",
    suggested_w=50, suggested_d=45, min_w=20, max_w=100, min_d=20, max_d=90,
    min_area=600, max_area=6000, suggested_area=2000,
    aspect_ratio="1.1:1", shape="rectangular",
)


# ---------------------------------------------------------------------------
# 3) Cathedral / Religious Forecourt
# ---------------------------------------------------------------------------
cathedral_forecourt = archetype(
    id="cathedral_religious_forecourt",
    slug="cathedral-religious-forecourt",
    title="Cathedral / Religious Forecourt",
    description="A formal hardscape forecourt or sacred plaza fronting a cathedral, mosque, basilica, or temple, used for processions, gathering, and ceremonial approach",
    tags=["plaza", "religious", "cathedral", "mosque", "temple", "forecourt", "sacred"],
    landscape_character=(
        "A religious forecourt fronting a cathedral, basilica, mosque, or temple seen from "
        "drone altitude. The forecourt is a strong open hardscape footprint — paved in stone, "
        "marble, cobblestone, or patterned tile — anchored at one edge by the soaring mass "
        "of the religious building with its characteristic dome, towers, columned portico, or "
        "minarets rising above. A clear processional axis runs from a street or gate edge "
        "straight to the building's main portal, often marked by a central monument, fountain, "
        "or ablution feature. The paving carries a strong geometric pattern (radiating cobble "
        "fan, marble inlay, tile pattern) that reads dramatically from above. Stone benches, "
        "low bollards, or stone columns punctuate the edges. From above, the forecourt is a "
        "strict ceremonial expanse with the religious building's dome or tower casting a "
        "distinctive shadow across the patterned hardscape."
    ),
    paving="Stone, marble, cobblestone, or patterned ceramic tile in a strong geometric design",
    planting="Restrained ceremonial planting — clipped sentinel trees, single olive or palm specimens, or no planting at all",
    seating="Stone perimeter benches, low stone walls, occasional shaded arcades along edges",
    water="Optional central ablution fountain or reflecting basin on the processional axis",
    openness="Open ceremonial hardscape framed dramatically by the religious building's mass on one side",
    prompt_subject="Aerial view of a formal religious forecourt fronting a cathedral, mosque, basilica, or temple",
    prompt_details=[
        "Strong open hardscape footprint paved in stone, marble, cobblestone, or patterned tile",
        "Religious building with dome, towers, portico, or minarets anchoring one edge",
        "Clear processional axis running from street/gate edge to the main portal",
        "Central monument, fountain, ablution feature, or column marking the axis",
        "Geometric paving pattern visible from above — radiating cobbles, marble inlay, or tile",
        "Restrained ceremonial planting only — clipped sentinels or none",
    ],
    prompt_negative=[
        "No casual park lawn surface",
        "No playground equipment",
        "No commercial signage",
        "No parking inside the forecourt",
        "No text overlays",
    ],
    property_presets={
        "tree_density_level": "very_low",
        "tree_density": 0.05,
        "has_paths": True,
        "has_benches": True,
        "shade_strategy": "perimeter_arcade",
    },
    variants_data=[
        variant(
            "cathedral_religious_forecourt_v0", "Asian Temple Plaza", "#6B4423",
            "Small intimate Asian temple plaza, roughly 30 by 50 meters of raked grey gravel and stone-flagged path leading to the timber-and-tile main hall of a Buddhist or Shinto temple. Stone lanterns line the central path; a small single-storey gate (torii or sanmon) marks the entry from the street. A small water-purification pavilion (chōzuya) sits to one side. Single mature pine and a small maple anchor the corners. Surrounding context shows a dense low-rise traditional Asian neighbourhood with timber-frame and tile-roof buildings.",
            1000, 2500, 1500, "cathedral-religious-forecourt"),
        variant(
            "cathedral_religious_forecourt_v1", "French Gothic Cathedral Parvis", "#8B7355",
            "French Gothic cathedral parvis, roughly 60 by 65 meters of pale stone-paver hardscape stretching out before the soaring twin-towered Gothic west front of a great cathedral. The pavers are arranged in a regular fan pattern. A bronze equestrian statue or processional cross sits on a stone pedestal at the center of the axis. Stone bollards on chains mark the perimeter. A single sentinel cedar of Lebanon stands off-axis. Surrounding context shows a medieval cathedral close — older stone canon's houses, episcopal palace, and narrow approach lanes.",
            3000, 5500, 4500, "cathedral-religious-forecourt"),
        variant(
            "cathedral_religious_forecourt_v2", "Italian Renaissance Basilica Square", "#A0826D",
            "Grand Italian Renaissance basilica square, roughly 110 by 100 meters of warm travertine paving in a radiating geometric pattern centred on a tall granite obelisk or column. The basilica with its great dome and columned portico anchors one long edge; covered arcades wrap the other three sides at the lower level with smaller institutional buildings rising above. Two matching baroque fountains flank the obelisk on the axis. Surrounding context shows a Renaissance city centre with Italian streets converging on the square.",
            8000, 14000, 11000, "cathedral-religious-forecourt"),
        variant(
            "cathedral_religious_forecourt_v3", "Islamic Mosque Courtyard", "#5B7065",
            "Vast Islamic mosque courtyard, roughly 150 by 150 meters of polished marble pavement in a strong eight-pointed star tile pattern. The grand domed mosque with six slender minarets rising at the corners anchors the qibla side; an arcaded riwaq with pointed arches wraps the other three sides providing shade. A large central ablution fountain with a small pavilion marks the geometric centre on the qibla axis. Geometric tile patterns intensify near the fountain. Surrounding context shows an Ottoman or Mughal capital with mixed historic urban fabric.",
            18000, 25000, 22000, "cathedral-religious-forecourt"),
    ],
    render_overlay="Replace the colored zone with a photorealistic religious forecourt fronting a cathedral, mosque, basilica, or temple. Strong open hardscape paved in stone, marble, cobblestone, or patterned tile. The religious building with its dome, towers, portico, or minarets anchoring one edge. Processional axis from the street edge to the main portal. Central monument, fountain, or ablution feature on the axis. Geometric paving pattern. Restrained ceremonial planting. Keep surrounding satellite map context exactly as-is. Oblique aerial view, sharp shadows, photorealistic, 8k.",
    render_roof="Replace the colored zone viewed from directly above with a hard-paved religious forecourt. Strong geometric paving pattern. Religious building footprint with characteristic dome shadow at one edge. Central focal element shadow on the axis. Perimeter arcade or bollard line. Keep surrounding context exactly as-is.",
    render_negative="cartoon, illustration, sketch, low quality, blurry, text, watermark, unrealistic colors, casual park lawn, playground equipment, commercial signage",
    suggested_w=80, suggested_d=80, min_w=25, max_w=180, min_d=25, max_d=180,
    min_area=1000, max_area=25000, suggested_area=4000,
    aspect_ratio="1:1", shape="rectangular",
)


# ---------------------------------------------------------------------------
# 4) Cultural Institution Forecourt
# ---------------------------------------------------------------------------
cultural_forecourt = archetype(
    id="cultural_institution_forecourt",
    slug="cultural-institution-forecourt",
    title="Cultural Institution Forecourt",
    description="An approach plaza fronting a museum, library, concert hall, or sports arena — designed to manage arrival flow, queue, and ceremonial approach to the building entrance",
    tags=["plaza", "cultural", "museum", "library", "concert-hall", "arena", "forecourt"],
    landscape_character=(
        "A cultural institution forecourt seen from drone altitude. The plaza is anchored on "
        "one edge by the dominant facade of a museum, library, concert hall, or sports arena "
        "— with a grand staircase, columned portico, ramped entry, or expansive concourse "
        "leading to the building. The plaza floor is paved in dignified stone, travertine, or "
        "polished concrete with a strong directional pattern guiding pedestrians toward the "
        "entry. A central feature — fountain pool, sculpture pad, or planted island — sits "
        "between the street and the building. The forecourt is wider than deep, allowing "
        "queue space and arrival photography. Stone benches, lighting columns, and ticket-"
        "kiosk pavilions punctuate the perimeter. Mature specimen trees may flank the entry "
        "or stand as sentinels at the corners. From above, the forecourt reads as an open "
        "rectangular landing with a strong axis of approach to the institutional building."
    ),
    paving="Travertine, granite, or polished concrete in a strong directional pattern guiding to the entry",
    planting="Specimen trees or paired allées flanking the entry; planted islands as occasional accents",
    seating="Stone perimeter benches, low planter walls, lounging steps near the entry",
    water="Optional central reflecting pool or fountain pad on the approach axis",
    openness="Open arrival hardscape framed by the institution's facade on one side and city streets on the others",
    prompt_subject="Aerial view of a cultural institution forecourt fronting a museum, library, concert hall, or sports arena",
    prompt_details=[
        "Strong rectangular hardscape with directional paving pattern guiding to the entry",
        "Dominant institutional facade — staircase, portico, ramped entry, or concourse — at one edge",
        "Central feature — fountain pool, sculpture pad, or planted island — between street and building",
        "Specimen trees or paired allées flanking the entry",
        "Stone benches and lighting columns at the perimeter",
        "Surrounding cultural-district urban fabric forming the context",
    ],
    prompt_negative=[
        "No casual park lawn dominating the plaza",
        "No playground equipment",
        "No parking inside the plaza",
        "No text overlays",
    ],
    property_presets={
        "tree_density_level": "low",
        "tree_density": 0.18,
        "has_paths": True,
        "has_benches": True,
        "shade_strategy": "entry_allees",
    },
    variants_data=[
        variant(
            "cultural_institution_forecourt_v0", "Modern Museum Plaza", "#5C5C5C",
            "Contemporary modern museum plaza, roughly 40 by 50 meters of textured polished concrete with a long ramped industrial-conversion entry leading into the brick mass of an industrial-building-turned-art-museum. A single oversized abstract steel sculpture anchors one edge of the plaza. A linear lawn strip with single river-birch specimens runs along the building face. Surrounding context shows an industrial-warehouse art district with adapted brick buildings.",
            1000, 3000, 2000, "cultural-institution-forecourt"),
        variant(
            "cultural_institution_forecourt_v1", "Beaux-Arts Library Steps", "#8B7355",
            "Grand Beaux-Arts library forecourt, roughly 60 by 70 meters of pale Indiana-limestone paver hardscape fronting the broad stepped grand staircase of a 1900s-era central library. Two large bronze lions flank the staircase on stone pedestals. A pair of bronze flagpoles stand at the curb. Mature plane trees in stone tree-pits punctuate the perimeter. Stone benches with cast-iron lighting columns line the sidewalk edge. Surrounding context shows a Beaux-Arts civic district with limestone government and cultural buildings.",
            3000, 5000, 4000, "cultural-institution-forecourt"),
        variant(
            "cultural_institution_forecourt_v2", "Concert Hall Forecourt", "#A0826D",
            "Travertine concert hall forecourt, roughly 90 by 80 meters of warm cream travertine paving in a regular grid pattern. A square central reflecting fountain pad with twin water jets sits on the axis between the curb and the concert hall's columned travertine facade. A continuous arcaded colonnade wraps three sides at the lower level. Plane-tree allées in long planter beds flank the approach. Surrounding context shows a Lincoln-Center-style cultural campus with multiple performing-arts buildings.",
            6000, 9000, 7500, "cultural-institution-forecourt"),
        variant(
            "cultural_institution_forecourt_v3", "Stadium Arena Concourse", "#708090",
            "Massive stadium arena concourse forecourt, roughly 150 by 100 meters of broad pale concrete paver concourse leading to the main entry portals of a large modern arena or stadium. A central oversized sculpture or statue of a sporting figure marks the approach axis. Decorative fan-zone graphics appear in the paving pattern. Lines of high-mast lighting columns edge the perimeter. Multiple ticket-kiosk pavilions stand at the curb edge. Surrounding context shows a sports-and-entertainment district with hotels, parking structures, and feeder streets.",
            10000, 15000, 13000, "cultural-institution-forecourt"),
    ],
    render_overlay="Replace the colored zone with a photorealistic cultural institution forecourt — museum, library, concert hall, or sports arena. Rectangular hardscape with directional paving pattern guiding to the entry. Dominant institutional facade — staircase, portico, ramped entry, or concourse — at one edge. Central feature — fountain pool, sculpture pad, or planted island — on the axis. Specimen trees or paired allées flanking the entry. Stone benches and lighting columns at the perimeter. Keep surrounding satellite map context exactly as-is. Oblique aerial view, late-afternoon sun, sharp shadows, photorealistic, 8k.",
    render_roof="Replace the colored zone viewed from directly above with a hard-paved cultural-institution forecourt. Directional paving pattern guiding to the entry. Building footprint with grand staircase or columned portico shadow at one edge. Central feature shadow on the axis. Tree canopy circles flanking the entry. Keep surrounding context exactly as-is.",
    render_negative="cartoon, illustration, sketch, low quality, blurry, text, watermark, unrealistic colors, casual park lawn, playground equipment, parking lots",
    suggested_w=70, suggested_d=70, min_w=25, max_w=160, min_d=25, max_d=120,
    min_area=1000, max_area=15000, suggested_area=3500,
    aspect_ratio="1:1", shape="rectangular",
)


# ---------------------------------------------------------------------------
# 5) Stepped / Terraced Plaza
# ---------------------------------------------------------------------------
stepped_plaza = archetype(
    id="stepped_terraced_plaza",
    slug="stepped-terraced-plaza",
    title="Stepped / Terraced Plaza",
    description="A topographic plaza built on a slope using broad stepped tiers — half plaza, half public stair — that cascade between two grade levels and double as informal seating",
    tags=["plaza", "stepped", "terraced", "topographic", "stair", "amphitheatre"],
    landscape_character=(
        "A stepped or terraced plaza seen from drone altitude. The plaza occupies a slope or "
        "grade change between an upper street and a lower street/water/court, descending in a "
        "series of broad shallow stone or concrete tiers. Each tier doubles as a gathering "
        "platform and as informal seating where people sit on the rises between levels. A "
        "central paved walking ramp or stair-aisle cuts straight through the tiers connecting "
        "top to bottom. Side balustrades or low parapet walls frame the descent. Planted "
        "pockets — clipped boxwood, palms, olive trees, or seasonal flowers — punctuate "
        "selected tiers. From above, the plaza reads as a layered topographic stripe of "
        "parallel tier shadows cascading down the grade with a clear central axis."
    ),
    paving="Stone, travertine, or precast concrete tiers with stepped risers between levels",
    planting="Punctuating planted pockets — clipped boxwood, olive, palm, or seasonal flowers — on selected tiers",
    seating="The tier risers themselves serve as informal seating; some tiers have stone bench inserts",
    water="Optional cascading water feature or fountain rill running down the central axis",
    openness="Open topographic cascade framed by parapet walls or balustrades on the long sides",
    prompt_subject="Aerial view of a stepped or terraced plaza descending between two grade levels in a series of broad stone tiers",
    prompt_details=[
        "Cascading parallel stepped tiers reading as a layered topographic stripe from above",
        "Central walking ramp or stair-aisle cutting through the tiers from top to bottom",
        "Side balustrades or low parapet walls framing the descent",
        "Planted pockets — clipped boxwood, palms, olive trees, or seasonal flowers — on selected tiers",
        "Optional cascading water rill or fountain on the axis",
        "Surrounding urban fabric at both upper and lower grade levels",
    ],
    prompt_negative=[
        "No flat single-level plaza",
        "No suburban lawn slope",
        "No parking inside the plaza",
        "No text overlays",
    ],
    property_presets={
        "tree_density_level": "low",
        "tree_density": 0.15,
        "has_paths": True,
        "has_benches": True,
        "shade_strategy": "tier_planters",
    },
    variants_data=[
        variant(
            "stepped_terraced_plaza_v0", "Aegean Whitewashed Village Steps", "#E8E0D0",
            "Small Aegean whitewashed village stepped plaza, roughly 20 by 30 meters of traditional Greek-island whitewashed stone tiers descending between two narrow village streets. Tier risers are painted brilliant white with cobalt-blue door insets at café fronts; the tier treads are warm flagstone. Pots of red geraniums punctuate every second tier. A pair of flowering bougainvillea vines drapes over a low parapet on one side. Surrounding context shows a tightly packed Cycladic village with whitewashed cubic houses.",
            500, 1000, 700, "stepped-terraced-plaza"),
        variant(
            "stepped_terraced_plaza_v1", "Spanish Steps Travertine Cascade", "#D4B89A",
            "Roman-classical Spanish-Steps-style travertine cascade, roughly 35 by 50 meters of broad shallow travertine tiers descending between an upper church-square level and a lower street fountain. Two graceful curved balustrades flank the descent; a central cascading run of broader steps forms the main axis. Stone urns and seasonal flowers (azaleas in spring) sit on selected upper tiers. A large baroque fountain marks the lower terminus. Surrounding context shows a Roman historic centre with ochre and cream-coloured 17th-c facades.",
            1500, 2500, 2000, "stepped-terraced-plaza"),
        variant(
            "stepped_terraced_plaza_v2", "Federation Square Contemporary Shard", "#5C5C5C",
            "Contemporary angular shard-pattern stepped plaza, roughly 60 by 65 meters of fragmented multi-coloured tile tiers descending between a transit terminus and a riverfront edge. The tier geometry is intentionally non-orthogonal — angular stair shards, asymmetric ramps, and triangular planted pockets create a contemporary sculptural ground. Cor-ten steel parapets line the edges. Surrounding context shows a contemporary cultural district with angular cantilevered museums and digital screens.",
            3000, 5500, 4500, "stepped-terraced-plaza"),
        variant(
            "stepped_terraced_plaza_v3", "Robson Square Modern Multi-Level", "#5B7065",
            "Robson-Square-style modernist multi-level terraced plaza, roughly 90 by 100 meters of broad poured-concrete tiers descending across two full storeys between an upper civic-court level and a lower courthouse podium. A central waterfall cascade runs down the full axis splashing through three large catchment basins on the lower tiers. Heavy planter beds with mature Japanese maples and dwarf conifers flank the descent. A sweeping accessible ramp wraps one side. Surrounding context shows a modernist 1970s downtown civic core with concrete-and-glass government buildings.",
            6500, 8000, 7500, "stepped-terraced-plaza"),
    ],
    render_overlay="Replace the colored zone with a photorealistic stepped or terraced plaza descending between two grade levels. Cascading parallel stepped stone or concrete tiers. Central walking ramp or stair-aisle cutting through the tiers. Side balustrades or parapet walls. Planted pockets on selected tiers. Optional cascading water feature on the axis. Surrounding urban context at both grade levels. Keep surrounding satellite map context exactly as-is. Oblique aerial view, late-afternoon sun, sharp shadows, photorealistic, 8k.",
    render_roof="Replace the colored zone viewed from directly above with a layered topographic plaza. Parallel tier shadows cascading down the grade. Central axis line running top to bottom. Planter pocket shapes on selected tiers. Surrounding street and building footprints at both upper and lower grade levels. Keep surrounding context exactly as-is.",
    render_negative="cartoon, illustration, sketch, low quality, blurry, text, watermark, unrealistic colors, flat single-level plaza, suburban grass slope, parking lots",
    suggested_w=50, suggested_d=55, min_w=15, max_w=120, min_d=15, max_d=110,
    min_area=500, max_area=8000, suggested_area=2000,
    aspect_ratio="1:1.1", shape="rectangular",
)


# ---------------------------------------------------------------------------
# Emit
# ---------------------------------------------------------------------------
all_archetypes = [city_hall, sunken_plaza, cathedral_forecourt,
                  cultural_forecourt, stepped_plaza]


def emit_snippet(archetypes: list[dict]) -> str:
    """Emit a JSON-text snippet ready to be spliced into an array.

    Each archetype rendered with 6-space first-level indent (matching the
    rich entries in openSpaceArchetypes.json), prefixed by 4 spaces for
    the opening '{' and suffixed by ',\\n' so it can sit in the array.
    """
    out_lines: list[str] = []
    for arch in archetypes:
        text = json.dumps(arch, indent=2, ensure_ascii=False)
        # json.dumps gives 2-space indent. We want 6-space inner / 4-space outer
        # to match the catalog. Add 4 spaces to every line, then bump the inner
        # by 2 more (so the entry's '{' sits at 4 spaces, fields at 6).
        prefixed = "\n".join("    " + line for line in text.splitlines())
        out_lines.append(prefixed + ",")
    return "\n".join(out_lines)


def main() -> int:
    snippet = emit_snippet(all_archetypes)

    # Validate by parsing as a JSON array (wrap in [..])
    try:
        json.loads("[" + snippet.rstrip(",") + "]")
    except json.JSONDecodeError as e:
        print(f"ERROR: emitted snippet is not valid JSON: {e}")
        return 1

    out_path = Path(__file__).parent / "_civic_plazas_snippet.json"
    out_path.write_text(snippet, encoding="utf-8")
    print(f"OK: wrote {len(snippet)} chars to {out_path}")
    print(f"Validates as JSON array of {len(all_archetypes)} entries")
    return 0


if __name__ == "__main__":
    sys.exit(main())
