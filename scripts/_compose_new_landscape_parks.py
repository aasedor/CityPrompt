"""Compose 8 new Landscape Parks archetype entries as JSON-valid text.

Run:  python scripts/_compose_new_landscape_parks.py
Output: scripts/_landscape_parks_snippet.json
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
        "aestheticCategory": "landscape_parks",
        "spaceType": "park",
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
# 1) Picturesque / Olmsted Park
# ---------------------------------------------------------------------------
picturesque_park = archetype(
    id="picturesque_olmsted_park",
    slug="picturesque-olmsted-park",
    title="Picturesque / Olmsted Park",
    description="A large naturalistic landscape park in the Picturesque or Olmsted tradition — rolling lawns, serpentine paths, naturalistic ponds, woodland fringes, and carefully composed long vistas",
    tags=["park", "landscape-park", "picturesque", "olmsted", "naturalistic"],
    landscape_character=(
        "A Picturesque-tradition landscape park seen from drone altitude. The composition is "
        "the canonical Olmsted recipe: broad sweeping meadows of mowed lawn open to long "
        "vistas, framed by deep belts of mixed deciduous woodland on the perimeter. A "
        "serpentine carriage drive curves through the park as the dominant circulation, "
        "doubled by softer pedestrian paths that deviate into the meadows and woodland. A "
        "naturalistic pond or lake with curving organic shoreline sits at one of the major "
        "vista terminations, often with a stone bridge or rustic timber bridge crossing a "
        "narrow neck. Clusters of mature specimen trees — oak, beech, elm, sycamore — punctuate "
        "the meadows as accent groups rather than rigid allées. A few stone shelters or "
        "rustic timber pavilions appear where paths converge. From above the park reads as "
        "alternating bands of pale-green mowed lawn, dark-green woodland, and reflective "
        "water, with curving path lines as the connective tissue."
    ),
    paving="Crushed-stone or compacted-dust serpentine carriage drives and softer pedestrian paths",
    planting="Picturesque mixed deciduous woodland belts with sweeping mowed lawn meadows and clustered specimen trees",
    seating="Rustic timber benches at vista points, occasional stone shelters or pavilions at path convergences",
    water="Naturalistic pond or lake with curving organic shoreline and rustic stone or timber bridges",
    openness="Strong contrast of open lawn meadows and enclosed woodland belts, framing carefully composed long vistas",
    prompt_subject="Aerial view of a large Picturesque-style landscape park with rolling lawns, serpentine paths, woodland belts, and a naturalistic lake",
    prompt_details=[
        "Broad sweeping mowed lawn meadows opening to long vistas",
        "Deep mixed deciduous woodland belts framing the perimeter",
        "Serpentine carriage drive curving through the park as dominant circulation",
        "Naturalistic pond or lake with organic curving shoreline",
        "Clustered specimen trees punctuating the meadows as accent groups, not rigid allées",
        "Surrounding city or suburban edge visible only at the boundary",
    ],
    prompt_negative=[
        "No formal geometric parterres or rigid axial planting",
        "No urban hardscape plazas inside the park",
        "No sports courts or playing fields filling the meadows",
        "No text overlays",
    ],
    property_presets={
        "tree_density_level": "high",
        "tree_density": 0.55,
        "has_paths": True,
        "has_benches": True,
        "shade_strategy": "perimeter_woodland_belts",
    },
    variants_data=[
        variant(
            "picturesque_olmsted_park_v0", "Hampstead Heath Wild Fringe", "#6B8A4A",
            "Hampstead-Heath-style wild fringe park, roughly 200 by 150 meters of unmowed wildflower meadow grading into oak-and-hawthorn copses with informal worn earthen footpaths winding through. Rough-mowed grass bands break up the meadow; ancient pollarded oaks anchor the central rise. A small naturalistic pond sits in a low corner with reedbed margins. Rustic split-rail fencing marks the perimeter. Surrounding context shows a leafy outer-suburban edge with detached Victorian-Edwardian villas.",
            5000, 30000, 18000, "picturesque-olmsted-park"),
        variant(
            "picturesque_olmsted_park_v1", "Mount Royal Hillside Lookout", "#4A7C59",
            "Mount-Royal-style hillside lookout park, roughly 300 by 200 meters of mature mixed-deciduous woodland blanketing a steep hillside with a single broad lookout terrace at the summit overlooking a city below. A serpentine carriage drive zigzags up the hill from a lower park entrance to the summit terrace. A stone-built lookout chalet or pavilion sits at the summit. Stone retaining walls support the upper terrace. Surrounding context shows a North American mid-rise neighbourhood at the foot of the hill.",
            20000, 60000, 40000, "picturesque-olmsted-park"),
        variant(
            "picturesque_olmsted_park_v2", "Prospect Park Woodland & Meadow", "#3F6B3F",
            "Prospect-Park-style large naturalistic park, roughly 400 by 350 meters mixing the canonical Olmstedian elements — a long sloping Long Meadow of mowed lawn at one end, the Ravine woodland with rustic timber footbridges over a stream in the middle, and the Lullwater lake with its naturalistic curving shoreline at the other. A serpentine carriage drive loops the perimeter; pedestrian paths radiate inward. Rustic stone arch bridges cross at narrow points. Surrounding context shows a dense urban Brownstone neighbourhood with a strong perimeter park edge.",
            50000, 90000, 75000, "picturesque-olmsted-park"),
        variant(
            "picturesque_olmsted_park_v3", "Central Park Multi-Landscape", "#2E5A2E",
            "Massive Central-Park-style flagship urban park, roughly 500 by 400 meters orchestrating multiple Picturesque landscape rooms in sequence: a Sheep Meadow open lawn, the Ramble dense woodland, the Lake with its rustic Bow Bridge, a Bethesda-Terrace-style formal stone overlook fronting the lake, and a Mall of paired American elms running south of the terrace. A continuous serpentine carriage drive forms the perimeter circulation. Surrounding context shows a high-density flagship Manhattan-like urban edge with continuous mid-rise streetwall on all four sides.",
            90000, 200000, 150000, "picturesque-olmsted-park"),
    ],
    render_overlay="Replace the colored zone with a photorealistic Picturesque-tradition landscape park. Sweeping mowed lawn meadows, deep mixed deciduous woodland belts, serpentine carriage drive curving through the park, naturalistic pond or lake with organic shoreline, clustered specimen trees punctuating the meadows. Surrounding city edge visible only at the boundary. Keep surrounding satellite map context exactly as-is. Oblique aerial view, late-afternoon golden hour, sharp shadows, photorealistic, 8k.",
    render_roof="Replace the colored zone viewed from directly above with a Picturesque landscape park. Alternating bands of pale-green mowed lawn meadow and dark-green woodland canopy. Curving serpentine path lines as connective tissue. Naturalistic water body with organic curving shoreline. Clustered specimen-tree canopy circles in the meadows. Keep surrounding context exactly as-is.",
    render_negative="cartoon, illustration, sketch, low quality, blurry, text, watermark, unrealistic colors, formal geometric parterres, urban plazas inside the park, sports courts dominating meadows",
    suggested_w=400, suggested_d=350, min_w=80, max_w=600, min_d=80, max_d=600,
    min_area=5000, max_area=200000, suggested_area=70000,
    aspect_ratio="1.15:1", shape="irregular",
)


# ---------------------------------------------------------------------------
# 2) Reclaimed Industrial Park
# ---------------------------------------------------------------------------
reclaimed_industrial_park = archetype(
    id="reclaimed_industrial_park",
    slug="reclaimed-industrial-park",
    title="Reclaimed Industrial Park",
    description="A landscape park created on a former industrial site — gasworks, steel mill, sugar refinery, colliery, or quarry — preserving heavy industrial relics as sculptural features set within ecological planting and recreational programming",
    tags=["park", "industrial", "post-industrial", "reclaimed", "adaptive-reuse", "landscape"],
    landscape_character=(
        "A reclaimed industrial landscape park seen from drone altitude. The site retains "
        "preserved monumental industrial relics — gasometer drums, steel mill blast furnaces, "
        "ore bunkers, sugar refinery silos, mine headframes, or massive concrete foundations — "
        "as the dominant compositional anchors, painted, weathered, or left in raw cor-ten "
        "patina. The ground plane around the relics is a layered patchwork: mowed lawn, "
        "naturalised meadow, rusted-rail walking paths, retained concrete pads now used as "
        "skate plazas or plant rooms, and pioneer-tree groves emerging from gravel and slag. "
        "Bridges of repurposed industrial steel cross former service trenches. Cor-ten steel "
        "wayfinding markers and retained machinery (cranes, ladders, conveyors) punctuate the "
        "ground as art. From above the park reads as monumental dark-grey industrial massings "
        "set within a green-and-brown palette of meadow, lawn, gravel, and pioneer tree "
        "clusters, with rust-colored linear paths threading between."
    ),
    paving="Mix of preserved concrete pads, rusted-rail walking paths, gravel plazas, and crushed-slag aggregate trails",
    planting="Pioneer-species tree groves (birch, willow, sumac), naturalised meadow, mowed lawn pockets, climbing vines on industrial relics",
    seating="Industrial-relic benches (repurposed I-beams), cor-ten steel furniture, retained machinery as climbing/seating sculpture",
    water="Adaptive water features — flooded former settling ponds, reclaimed cooling-water basins, reflecting pools at relic bases",
    openness="Strong vertical drama from preserved industrial massings rising above a horizontal landscape patchwork",
    prompt_subject="Aerial view of a reclaimed industrial landscape park preserving monumental industrial relics within ecological planting",
    prompt_details=[
        "Preserved monumental industrial relics — gasometers, blast furnaces, silos, mine headframes — as dominant features",
        "Layered ground plane mixing lawn, meadow, gravel plazas, and concrete pads",
        "Rusted-rail or cor-ten walking paths threading between the industrial relics",
        "Pioneer-tree groves (birch, willow, sumac) emerging from gravel and slag substrate",
        "Retained machinery (cranes, conveyors, ladders) as ground-level sculpture",
        "Surrounding former-industrial neighbourhood urban context",
    ],
    prompt_negative=[
        "No suburban manicured lawn dominating the entire site",
        "No formal geometric parterres",
        "No demolition rubble (relics must be preserved/curated, not demolished)",
        "No text overlays",
    ],
    property_presets={
        "tree_density_level": "medium",
        "tree_density": 0.4,
        "has_paths": True,
        "has_benches": True,
        "shade_strategy": "pioneer_groves_and_relics",
    },
    variants_data=[
        variant(
            "reclaimed_industrial_park_v0", "Domino Sugar Refinery Wharf", "#8B6914",
            "Domino-Park-style sugar refinery waterfront park, roughly 100 by 50 meters of linear riverside park preserving four massive cor-ten orange-brown sugar refinery cranes as a row of monumental sculptural relics fronting the waterfront. The ground is patterned with reclaimed timber and concrete strips, native grass beds, and a long elevated boardwalk paralleling the river. A water-play area sits among preserved industrial scrap as climbing sculpture. Surrounding context shows a Brooklyn-style brick-warehouse converted-loft district with a working-river edge.",
            5000, 12000, 8000, "reclaimed-industrial-park"),
        variant(
            "reclaimed_industrial_park_v1", "Gas Works Park", "#5C5C5C",
            "Gas-Works-Park-Seattle-style preserved-gasometer landscape park, roughly 150 by 150 meters of rolling reclaimed lawn rising up to the silhouette of preserved blue-and-rust gasometer drums and tower. A high earthen kite-flying mound dominates the centre. Walking paths loop around the lawn and approach the painted gasometer drums for self-tour. Pioneer birches edge the perimeter. A small picnic plaza occupies a former concrete pad. Surrounding context shows a Pacific-Northwest urban-residential lakefront edge.",
            12000, 30000, 22000, "reclaimed-industrial-park"),
        variant(
            "reclaimed_industrial_park_v2", "Zollverein Colliery Headframe", "#4A4A4A",
            "Zollverein-Coal-Mine-style colliery park, roughly 250 by 200 meters of post-industrial parkland orchestrated around a preserved black-steel mine pithead headframe rising 50m as the dominant landmark. Former coal-conveyor structures form a long elevated walkway across the site. Brick coke-oven complex preserved as a courtyard. Naturalised meadow and birch groves fill the spaces between relics. Cor-ten signage. Surrounding context shows a German Ruhr-region edge mixing former-industrial fabric and contemporary cultural quarter.",
            30000, 50000, 40000, "reclaimed-industrial-park"),
        variant(
            "reclaimed_industrial_park_v3", "Landschaftspark Duisburg-Nord", "#3F3F3F",
            "Landschaftspark-Duisburg-Nord-style massive steel-mill landscape park, roughly 400 by 350 meters of monumental preserved blast-furnace-and-ore-bunker complex turned recreational landscape. Climbers visible scaling preserved blast-furnace stairs. Former cooling pond converted to a swim/dive basin in a steel-walled chamber. Ore-bunker walls form a climbing-and-bouldering plaza. Catwalks aloft connect preserved structures. Pioneer-birch-and-meadow ground plane fills the spaces. Surrounding context shows a German industrial city with active steelworks at the perimeter.",
            70000, 200000, 130000, "reclaimed-industrial-park"),
    ],
    render_overlay="Replace the colored zone with a photorealistic reclaimed industrial landscape park. Preserved monumental industrial relics (gasometers, blast furnaces, silos, headframes, refinery cranes) as dominant features. Layered ground plane mixing lawn, meadow, gravel plazas, and concrete pads. Rusted-rail or cor-ten walking paths between the relics. Pioneer-tree groves emerging from gravel substrate. Retained machinery as ground-level sculpture. Surrounding former-industrial neighbourhood. Keep surrounding satellite map context exactly as-is. Oblique aerial view, dramatic late-afternoon raking light, sharp shadows, photorealistic, 8k.",
    render_roof="Replace the colored zone viewed from directly above with a reclaimed industrial park. Monumental dark-grey industrial relic footprints. Patchwork ground of lawn, meadow, gravel, and concrete pads. Linear cor-ten path threading between relics. Pioneer-tree canopy clusters. Keep surrounding context exactly as-is.",
    render_negative="cartoon, illustration, sketch, low quality, blurry, text, watermark, unrealistic colors, manicured suburban lawn, formal parterres, demolished rubble, generic green park",
    suggested_w=300, suggested_d=250, min_w=60, max_w=600, min_d=60, max_d=600,
    min_area=5000, max_area=200000, suggested_area=50000,
    aspect_ratio="1.2:1", shape="irregular",
)


# ---------------------------------------------------------------------------
# 3) Quarry / Sunken Garden Park
# ---------------------------------------------------------------------------
quarry_garden_park = archetype(
    id="quarry_sunken_garden_park",
    slug="quarry-sunken-garden-park",
    title="Quarry / Sunken Garden Park",
    description="A landscape park set inside a former quarry or excavated bowl, with terraced stone walls, cascading paths, and lush planting that takes advantage of the sheltered microclimate",
    tags=["park", "quarry", "sunken-garden", "bowl", "terraced", "topographic"],
    landscape_character=(
        "A former-quarry landscape park seen from drone altitude. The site is a dramatic "
        "rectangular or irregular bowl excavated 5-25 meters below the surrounding ground "
        "level, with rough vertical or stepped stone walls (limestone, sandstone, or basalt) "
        "forming the perimeter cliff face. A switchback stair path or accessible ramp descends "
        "from the rim to the floor of the bowl. The bowl floor holds the most lavish planting "
        "in the catalog: a formal central lawn or pond, deep ornamental flower beds layered "
        "with seasonal colour, mature specimen trees thriving in the sheltered microclimate. "
        "Cascading water features run down the cliff wall on one side, splashing through "
        "stepped basins. Climbing vines drape the cliff face. A small pavilion or tea-house "
        "may sit at the floor level. From above the park reads as a vivid colourful "
        "garden-floor inset within a frame of grey rough cliff face, with the surrounding "
        "ground level visible at the rim above."
    ),
    paving="Stone-dust paths on the bowl floor with stone stair switchbacks descending the cliff face",
    planting="Lush sheltered-microclimate planting — deep ornamental flower beds, mature specimen trees, climbing vines on cliff faces",
    seating="Stone benches set into rock-cliff alcoves, paired wrought-iron benches around the central lawn or pond",
    water="Cascading water feature splashing down the cliff face into stepped basins; central pond or lily pool",
    openness="Strong vertical enclosure by cliff walls on three or four sides; top-down view dominant",
    prompt_subject="Aerial view of a former quarry transformed into a sunken garden park with cliff walls and lush bowl-floor planting",
    prompt_details=[
        "Dramatic rectangular or irregular bowl excavated 5-25m below surrounding ground",
        "Rough stone cliff walls (limestone, sandstone, basalt) forming the perimeter",
        "Switchback stair path or accessible ramp descending from rim to floor",
        "Lavish flower-bed and specimen-tree planting on the bowl floor",
        "Cascading water feature down the cliff wall into stepped basins",
        "Central lawn, pond, or lily pool as the focal element",
    ],
    prompt_negative=[
        "No flat at-grade park (must clearly read as below-grade bowl)",
        "No active quarrying machinery or rubble",
        "No urban plaza hardscape dominating",
        "No text overlays",
    ],
    property_presets={
        "tree_density_level": "medium",
        "tree_density": 0.45,
        "has_paths": True,
        "has_benches": True,
        "shade_strategy": "cliff_microclimate",
    },
    variants_data=[
        variant(
            "quarry_sunken_garden_park_v0", "Vigeland Sunken Sculpture Bowl", "#8B7355",
            "Vigeland-style intimate sunken sculpture bowl, roughly 50 by 60 meters of grass-lined oval bowl excavated 6m below surrounding parkland. Stone-flagged paths spiral down from rim to floor in a single graceful curve. The grass floor is dotted with figurative bronze-and-stone sculptures. Mature beech trees ring the bowl perimeter at the upper rim. A simple arched stone bridge crosses a narrow stream at the lower entry. Surrounding context shows a Scandinavian-style park.",
            3000, 8000, 5000, "quarry-sunken-garden-park"),
        variant(
            "quarry_sunken_garden_park_v1", "Calgary Quarry Park Lake", "#5B7065",
            "Calgary-Quarry-Park-style naturalised quarry-pond park, roughly 150 by 120 meters of irregular reclaimed limestone-quarry pit now flooded as a clear-water lake ringed by stepped stone-block beach edges. A soft sand swim beach occupies one shallow corner. Walking paths follow the upper rim with occasional stair descents to lake-edge platforms. Naturalised aspen-and-fir woodland edges the rim. Surrounding context shows a Prairie-Canadian masterplanned suburban edge.",
            10000, 25000, 18000, "quarry-sunken-garden-park"),
        variant(
            "quarry_sunken_garden_park_v2", "Limestone Tier Cascade Garden", "#A0826D",
            "Tiered limestone quarry garden, roughly 200 by 150 meters with three distinct vertical tiers descending 18m from the rim. Each tier holds different planting — formal parterre on the upper, ornamental shrubbery on the middle, lily-pool with reflecting water on the lowest. A stone cascade-and-rill splashes down the cliff face on one side, audible from across the bowl. Stone-pillared pergolas frame views from upper-tier vantages. Surrounding context shows a Mediterranean coastal hilltown.",
            18000, 30000, 25000, "quarry-sunken-garden-park"),
        variant(
            "quarry_sunken_garden_park_v3", "Butchart Showpiece Sunken Garden", "#B85B6D",
            "Butchart-Gardens-style flagship showpiece sunken garden, roughly 250 by 200 meters of vast former limestone quarry now lavishly planted with concentric ornamental flower beds, manicured lawn panels, and specimen trees set into the grand quarry bowl. A central lily-pad pond with a small island of dwarf conifers anchors the floor. A cascading rock-garden water feature descends the back cliff face. Mature climbing vines drape the cliff walls. Looping stone-flagged paths lead visitors through colour-themed garden rooms. Surrounding context shows a Pacific-Northwest tourist-garden estate setting.",
            25000, 40000, 32000, "quarry-sunken-garden-park"),
    ],
    render_overlay="Replace the colored zone with a photorealistic former-quarry sunken garden park. Dramatic bowl 5-25m below surrounding ground level. Rough stone cliff walls forming the perimeter. Switchback stair or ramp descending from rim to floor. Lavish flower-bed and specimen-tree planting on the bowl floor. Cascading water feature down the cliff wall. Central lawn, pond, or lily pool. Surrounding parkland or hilltown context. Keep surrounding satellite map context exactly as-is. Oblique aerial view, sharp shadows, photorealistic, 8k.",
    render_roof="Replace the colored zone viewed from directly above with a sunken quarry garden. Vivid colourful garden-floor inset within a grey rough cliff-face frame. Cascading water-feature shape on the cliff face. Switchback path descending from rim to floor. Surrounding ground level visible at the upper rim. Keep surrounding context exactly as-is.",
    render_negative="cartoon, illustration, sketch, low quality, blurry, text, watermark, unrealistic colors, flat at-grade park, active quarry machinery, urban plaza hardscape",
    suggested_w=180, suggested_d=160, min_w=40, max_w=320, min_d=40, max_d=300,
    min_area=3000, max_area=40000, suggested_area=20000,
    aspect_ratio="1.1:1", shape="irregular",
)


# ---------------------------------------------------------------------------
# 4) Hilltop Topographic Park
# ---------------------------------------------------------------------------
hilltop_park = archetype(
    id="hilltop_topographic_park",
    slug="hilltop-topographic-park",
    title="Hilltop Topographic Park",
    description="A landscape park draped over a steep urban or suburban hill — switchback paths, viewpoint terraces, retaining walls, and dramatic vistas across the city below",
    tags=["park", "hilltop", "topographic", "viewpoint", "switchback", "terraced"],
    landscape_character=(
        "A hilltop landscape park seen from drone altitude. The site occupies a prominent "
        "steep hill or rocky outcrop rising 20-80 meters above the surrounding city, with the "
        "park's dominant form being its topography itself. Switchback walking paths zigzag "
        "from a lower park entrance up the hillside through a series of terraces. Stone or "
        "concrete retaining walls hold each terrace level, often planted with cascading vines "
        "or rockery shrubs. A summit terrace at the top is the main destination — a broad "
        "stone-paved belvedere with a low parapet wall offering a dramatic vista of the city "
        "below. A small pavilion, viewpoint marker, or sculpture anchors the summit. The "
        "hillsides are clothed in mixed woodland or naturalised meadow. Lower-elevation "
        "amenities (small picnic lawn, playground, café pavilion) cluster near the entrance. "
        "From above the park reads as a layered topographic stripe with the summit terrace "
        "as a distinctive flat focal cap, switchback paths visible as zigzag lines, and "
        "concentric retaining-wall edges descending the slope."
    ),
    paving="Stone-paved summit belvedere with crushed-stone or asphalt switchback paths descending the hill",
    planting="Mixed woodland or naturalised meadow on hillsides, cascading vines and rockery on retaining walls, sentinel trees at the summit",
    seating="Stone benches at viewpoint terraces, paired benches along switchback paths, a summit pavilion or viewing platform",
    water="Optional summit reflecting basin or low-flow rill cascading down a stepped hillside element",
    openness="Strong topographic enclosure by hillside form; summit opens to expansive distant vistas",
    prompt_subject="Aerial view of a hilltop landscape park with switchback paths ascending a steep slope to a summit viewpoint terrace",
    prompt_details=[
        "Steep hill rising 20-80m above the surrounding city as the dominant form",
        "Switchback walking paths zigzagging up the hillside through terraced levels",
        "Stone or concrete retaining walls between terraces with cascading vine planting",
        "Summit belvedere terrace with stone paving and parapet wall offering distant vistas",
        "Mixed woodland or naturalised meadow clothing the hillsides",
        "Surrounding city below the hill with rooftops visible from the summit",
    ],
    prompt_negative=[
        "No flat-ground park — must clearly read as a hill rising above surroundings",
        "No suburban lawn slope without retaining structure",
        "No urban plaza dominating the summit",
        "No text overlays",
    ],
    property_presets={
        "tree_density_level": "high",
        "tree_density": 0.55,
        "has_paths": True,
        "has_benches": True,
        "shade_strategy": "woodland_hillsides",
    },
    variants_data=[
        variant(
            "hilltop_topographic_park_v0", "Mediterranean Cypress Hill", "#6B8A4A",
            "Mediterranean cypress-and-stone hilltop park, roughly 80 by 90 meters draped over a small rocky coastal hill rising 25m above a Mediterranean village. Slender Italian cypresses line the switchback paths in pairs. Whitewashed stone retaining walls hold three terrace levels. The summit terrace is a circular cobbled platform with a single bronze sculpture of a maritime saint. A small whitewashed chapel sits at one terrace. Surrounding context shows a coastal Mediterranean village with whitewashed cubic houses descending to a harbour.",
            5000, 12000, 8000, "hilltop-topographic-park"),
        variant(
            "hilltop_topographic_park_v1", "Telegraph Hill Switchback", "#5B7065",
            "Telegraph-Hill-style steep urban switchback park, roughly 100 by 130 meters draped over a steep San-Francisco-like urban hill rising 35m. Asphalt-paved switchback paths zigzag up between dense Monterey-pine and eucalyptus plantings. Wooden public stairs cut straight up between switchbacks for ambitious walkers. The summit terrace is an octagonal stone-paved belvedere with a tower (Coit-Tower-like). Surrounding context shows a steep North-American hillside neighbourhood with terraced houses descending toward a downtown skyline.",
            12000, 20000, 16000, "hilltop-topographic-park"),
        variant(
            "hilltop_topographic_park_v2", "Buttes-Chaumont Rocky Belvedere", "#3F6B3F",
            "Buttes-Chaumont-style romantic rocky outcrop park, roughly 200 by 180 meters of dramatic Picturesque hilltop park rising 50m around a single tall rocky pinnacle topped by a Greek-temple folly. A cast-iron suspension footbridge crosses an artificial chasm to reach the summit. A grotto-and-stalactite ravine winds beneath. Sweeping mowed lawns and mature plane trees fill the lower slopes. A naturalistic lake with rocky shoreline laps at one foot. Surrounding context shows a Parisian working-class neighbourhood with Haussmannian streetwall.",
            25000, 40000, 33000, "hilltop-topographic-park"),
        variant(
            "hilltop_topographic_park_v3", "Pacific Terraced Viewpoint", "#2E5A2E",
            "Pacific-Northwest terraced-viewpoint regional park, roughly 250 by 220 meters draped across a forested mountain ridge rising 80m above a coastal city. Multiple concrete-and-rough-cedar viewpoint platforms cantilever out at different elevations along a long switchback trail of crushed gravel. Each platform has interpretive signage and stone benches. Mature Douglas fir and western red cedar clothe the slopes. The summit platform offers a panoramic glass-railed vista. Surrounding context shows a Pacific-Coast city with skyline visible from the summit.",
            45000, 70000, 58000, "hilltop-topographic-park"),
    ],
    render_overlay="Replace the colored zone with a photorealistic hilltop topographic park. Steep hill rising clearly above surroundings. Switchback walking paths zigzagging up the hillside. Stone or concrete retaining walls between terrace levels. Summit belvedere terrace with stone paving and parapet wall. Mixed woodland or meadow clothing the hillsides. Summit pavilion, sculpture, or tower as focal element. Surrounding city visible below. Keep surrounding satellite map context exactly as-is. Oblique aerial view, dramatic raking afternoon light, sharp shadows, photorealistic, 8k.",
    render_roof="Replace the colored zone viewed from directly above with a hilltop park. Layered topographic stripe with summit terrace as flat focal cap. Switchback paths visible as zigzag lines. Concentric retaining-wall edges descending the slope. Mixed canopy on the hillsides. Surrounding city rooftops at the lower edges. Keep surrounding context exactly as-is.",
    render_negative="cartoon, illustration, sketch, low quality, blurry, text, watermark, unrealistic colors, flat-ground park, urban plaza dominating summit, suburban lawn slope without structure",
    suggested_w=180, suggested_d=180, min_w=50, max_w=300, min_d=50, max_d=300,
    min_area=5000, max_area=70000, suggested_area=25000,
    aspect_ratio="1:1", shape="irregular",
)


# ---------------------------------------------------------------------------
# 5) Estate Picnic Grove
# ---------------------------------------------------------------------------
estate_picnic_grove = archetype(
    id="estate_picnic_grove",
    slug="estate-picnic-grove",
    title="Estate Picnic Grove",
    description="A traditional family-day-out park: open turf with widely-spaced shade trees, scattered picnic tables, charcoal grills, and small pavilions for shelter — the classic public picnic landscape",
    tags=["park", "picnic", "grove", "family", "shade-grove", "lawn"],
    landscape_character=(
        "An estate picnic grove park seen from drone altitude. The site is an open mowed-lawn "
        "expanse studded with widely-spaced mature shade trees forming a generous canopy "
        "above. Picnic tables and charcoal grills are scattered evenly across the lawn — "
        "small clusters of timber tables under each shade tree's canopy, with a grill "
        "pedestal at each cluster. A network of soft compacted-gravel paths winds through "
        "the grove, connecting the picnic clusters to perimeter parking and to occasional "
        "small open-sided timber-and-shingle picnic shelters or pavilions for rainy-day "
        "shelter. A flat open turf area in the centre serves as a casual play lawn — frisbee, "
        "kickball, kite-flying — without sports markings. From above the park reads as a "
        "regular pattern of dark-green tree canopy circles dotting a pale-green lawn, with "
        "small dark rectangles of picnic tables under each canopy and the occasional larger "
        "pavilion roof."
    ),
    paving="Compacted-gravel walking paths and small gravel parking pads at perimeter; lawn under tree canopy",
    planting="Widely-spaced mature shade trees (oak, maple, sycamore, elm) forming generous canopy above mowed lawn",
    seating="Timber picnic tables clustered under each tree canopy with charcoal grill pedestals",
    water="Optional drinking-fountain pillar; no decorative water features",
    openness="Open lawn with regular tree-canopy enclosure overhead, framed by perimeter woodland or fields",
    prompt_subject="Aerial view of an estate picnic grove park with widely-spaced shade trees and scattered picnic-table clusters",
    prompt_details=[
        "Open mowed-lawn expanse studded with widely-spaced mature shade trees",
        "Picnic tables and charcoal grills clustered under each tree canopy",
        "Compacted-gravel walking paths winding through the grove",
        "Small open-sided timber-and-shingle picnic shelters at occasional points",
        "A flat open central turf area for casual play (no sports markings)",
        "Surrounding rural or suburban edge with woodland or fields",
    ],
    prompt_negative=[
        "No formal sports field markings or bleachers",
        "No urban plaza hardscape",
        "No mature woodland canopy completely shading the entire lawn",
        "No text overlays",
    ],
    property_presets={
        "tree_density_level": "medium",
        "tree_density": 0.4,
        "has_paths": True,
        "has_benches": True,
        "shade_strategy": "scattered_canopy_grove",
    },
    variants_data=[
        variant(
            "estate_picnic_grove_v0", "Pine-Shaded Creekside Picnic", "#4A7C59",
            "Pine-shaded creekside picnic grove, roughly 70 by 80 meters of needle-carpet ground beneath a canopy of mature ponderosa pines and white pines. Picnic tables clustered in three groups under the largest pines, each with a steel charcoal grill. A small clear creek loops through the back edge of the grove with a stone-flag stepping-path crossing. A simple log-frame restroom shelter sits at the entry. Surrounding context shows a coniferous foothill landscape with a campground access road.",
            5000, 12000, 8000, "estate-picnic-grove"),
        variant(
            "estate_picnic_grove_v1", "Wide-Spaced Oak Shade Grove", "#6B8A4A",
            "Wide-spaced mature-oak picnic grove, roughly 120 by 100 meters of mowed lawn with twelve mature white-oak specimen trees evenly spaced as the dominant grove structure. Each oak has a cluster of two picnic tables and a charcoal grill in its dappled shade. A central open turf circle for casual play. Crushed-stone walking loop circles the lawn. A small open-sided timber-and-shingle picnic shelter sits to one side. Surrounding context shows a temperate-deciduous regional-park edge with mixed woodland.",
            10000, 25000, 18000, "estate-picnic-grove"),
        variant(
            "estate_picnic_grove_v2", "Open Meadow & Trestle Pavilion", "#8FA86F",
            "Open-meadow picnic grove with shelter pavilions, roughly 200 by 150 meters of broad mowed-lawn meadow with isolated specimen-shade-tree clusters at the corners and along one edge. A long open-sided timber-and-shingle pavilion with picnic-table seating runs along the upwind edge. Smaller scattered timber picnic tables sit in the shade clusters. A horseshoe-pit and a small play lawn anchor the off-axis corner. Surrounding context shows a rolling rural-recreational-park landscape.",
            25000, 50000, 38000, "estate-picnic-grove"),
        variant(
            "estate_picnic_grove_v3", "Regional-Park Picnic Plain", "#7E9F5A",
            "Massive regional-park picnic plain, roughly 350 by 250 meters of vast mowed-lawn expanse with scattered shade-tree clusters and multiple timber-and-shingle picnic-shelter pavilions distributed evenly across the site. Long compacted-gravel walking loops connect the shelters. Charcoal-grill pedestals appear at every cluster. A small playground occupies one corner. A perimeter forest belt frames the meadow. Surrounding context shows a rural regional-park access road and parking lots at the edges.",
            55000, 90000, 75000, "estate-picnic-grove"),
    ],
    render_overlay="Replace the colored zone with a photorealistic estate picnic grove park. Open mowed-lawn expanse studded with widely-spaced mature shade trees. Picnic tables and charcoal grills clustered under each tree canopy. Compacted-gravel walking paths through the grove. Open-sided timber-and-shingle picnic shelters at occasional points. Flat open central turf area for casual play. Surrounding rural or suburban edge. Keep surrounding satellite map context exactly as-is. Oblique aerial view, late-afternoon golden hour, photorealistic, 8k.",
    render_roof="Replace the colored zone viewed from directly above with an estate picnic grove. Regular pattern of dark-green tree canopy circles dotting pale-green lawn. Small dark picnic-table rectangles under each canopy. Pavilion roof shapes at occasional points. Compacted-gravel path lines winding through. Surrounding fields or woodland at the boundary. Keep surrounding context exactly as-is.",
    render_negative="cartoon, illustration, sketch, low quality, blurry, text, watermark, unrealistic colors, sports field markings, urban plaza hardscape, fully closed forest canopy",
    suggested_w=200, suggested_d=180, min_w=60, max_w=400, min_d=60, max_d=350,
    min_area=5000, max_area=90000, suggested_area=30000,
    aspect_ratio="1.1:1", shape="irregular",
)


# ---------------------------------------------------------------------------
# 6) Reservoir / Watershed Park
# ---------------------------------------------------------------------------
reservoir_park = archetype(
    id="reservoir_watershed_park",
    slug="reservoir-watershed-park",
    title="Reservoir / Watershed Park",
    description="A landscape park anchored on a drinking-water reservoir or impoundment lake, with a perimeter trail loop, small dam structure, and recreation amenities arranged around the shoreline",
    tags=["park", "reservoir", "watershed", "lake", "perimeter-trail", "dam"],
    landscape_character=(
        "A reservoir landscape park seen from drone altitude. The site is dominated by a "
        "large body of impounded water — clear, calm, and reflective — with a strong "
        "concrete-or-earthen dam structure visible at one end where the impoundment retains "
        "the water. A continuous perimeter walking-and-cycling trail loops the entire "
        "shoreline, paved with crushed gravel or asphalt. The shoreline alternates between "
        "naturalised vegetated edges (cattails, willows, native grasses), exposed rock or "
        "stone-armoured banks for shoreline erosion control, and a few formal landing decks "
        "or fishing platforms. A small parking lot and trailhead pavilion sits near the dam. "
        "On a far edge, a forested upland hillside rises gently, providing watershed cover. "
        "From above the park reads as a clear water surface ringed by a continuous trail "
        "thread, with the dam structure, trailhead pavilion, and forest-clad upland visible "
        "as the principal architectural elements."
    ),
    paving="Crushed-gravel or asphalt perimeter trail; small gravel parking lot at the trailhead",
    planting="Mix of naturalised shoreline vegetation (cattails, willows, native grasses), upland watershed forest, mowed lawn near the trailhead",
    seating="Stone or timber benches at viewpoints around the trail, fishing-platform timber decks",
    water="The dominant impounded reservoir lake itself; small dam-spillway feature at one end",
    openness="Strong open vista across the open water; perimeter forest enclosure of varying density",
    prompt_subject="Aerial view of a reservoir landscape park with a perimeter trail loop around a clear impoundment lake and a dam at one end",
    prompt_details=[
        "Large clear reservoir lake as the dominant feature",
        "Continuous perimeter walking-and-cycling trail looping the shoreline",
        "Concrete or earthen dam structure at one end of the lake",
        "Naturalised shoreline vegetation alternating with rock-armoured banks and timber landing decks",
        "Forested watershed upland hillside on the far edge",
        "Small parking lot and trailhead pavilion near the dam",
    ],
    prompt_negative=[
        "No urban plaza hardscape inside the park",
        "No marina with motor boats inside the reservoir",
        "No buildings on the water surface",
        "No text overlays",
    ],
    property_presets={
        "tree_density_level": "high",
        "tree_density": 0.5,
        "has_paths": True,
        "has_benches": True,
        "shade_strategy": "perimeter_forest",
    },
    variants_data=[
        variant(
            "reservoir_watershed_park_v0", "Concrete-Edge Utility Reservoir", "#708090",
            "Smaller utility-style reservoir with concrete-edge perimeter, roughly 100 by 120 meters of clear rectangular impoundment lake bounded by smooth concrete retaining walls. A continuous concrete-paved walkway with chain-link railings circles the perimeter. A small concrete spillway feature with a security access stair sits at one end. The far end shows a small treatment-plant pumphouse. Sparse landscaping — mowed grass strip with a single row of poplar trees — softens the edge. Surrounding context shows a suburban-utility setting with a service road.",
            8000, 20000, 14000, "reservoir-watershed-park"),
        variant(
            "reservoir_watershed_park_v1", "Stone-Banked Urban Reservoir", "#5B7065",
            "Stone-banked urban reservoir park, roughly 200 by 180 meters of clear roughly-rectangular impoundment lake bounded by Victorian-era stone retaining walls, with a perimeter cinder running track of pure horse-runners atop the embankment. A small classical stone gatehouse pumping station sits at one corner. Mature plane trees in single-file line the trail. A small wrought-iron-fenced overlook gazebo sits at the dam end. Surrounding context shows a Manhattan-style urban park edge (Central Park reservoir feel).",
            22000, 60000, 40000, "reservoir-watershed-park"),
        variant(
            "reservoir_watershed_park_v2", "Forested Upland Reservoir", "#3F6B3F",
            "Forested-upland regional reservoir, roughly 350 by 280 meters of irregular natural-shoreline impoundment lake set among mature mixed-hardwood forest. A small concrete dam with a stair-spillway sits at the south end with a stone gatehouse. A crushed-stone perimeter trail follows the entire shoreline weaving in and out of the woodland edge. Two small timber boat-launch ramps for non-motorised craft. A trailhead pavilion sits at a parking lot near the dam. Surrounding context shows a forested protected watershed in a temperate-deciduous setting.",
            65000, 150000, 100000, "reservoir-watershed-park"),
        variant(
            "reservoir_watershed_park_v3", "Earthen-Dam Recreation Reservoir", "#2E5A2E",
            "Massive earthen-dam recreation reservoir, roughly 600 by 400 meters of large irregular impoundment lake retained by a long earthen embankment dam visible as a green sloped wall at one end. A wide perimeter cycling-and-walking loop circles the entire shoreline with multiple parking lots, several picnic-grove access points, and three timber fishing piers spaced around the lake. Sandy swim-beach area at one corner. Forested upland watershed on the far shore. Surrounding context shows a recreational-reservoir suburban-edge setting with multiple access roads.",
            150000, 500000, 280000, "reservoir-watershed-park"),
    ],
    render_overlay="Replace the colored zone with a photorealistic reservoir landscape park. Large clear impoundment lake as the dominant feature. Continuous perimeter trail looping the shoreline. Concrete or earthen dam structure at one end. Naturalised shoreline vegetation alternating with rock-armoured banks and timber landing decks. Forested watershed upland hillside on the far edge. Small parking lot and trailhead pavilion near the dam. Keep surrounding satellite map context exactly as-is. Oblique aerial view, calm light, clear sky, photorealistic, 8k.",
    render_roof="Replace the colored zone viewed from directly above with a reservoir park. Clear water surface ringed by a continuous trail thread. Dam structure at one end visible as a long band shape. Trailhead pavilion roof. Forest-clad upland edge on the far side. Surrounding context at the boundary. Keep surrounding context exactly as-is.",
    render_negative="cartoon, illustration, sketch, low quality, blurry, text, watermark, unrealistic colors, urban plaza hardscape, marina with motor boats, buildings on water surface",
    suggested_w=400, suggested_d=300, min_w=80, max_w=900, min_d=80, max_d=700,
    min_area=8000, max_area=500000, suggested_area=80000,
    aspect_ratio="1.3:1", shape="irregular",
)


# ---------------------------------------------------------------------------
# 7) Greenbelt Buffer Park
# ---------------------------------------------------------------------------
greenbelt_buffer_park = archetype(
    id="greenbelt_buffer_park",
    slug="greenbelt-buffer-park",
    title="Greenbelt Buffer Park",
    description="A wide linear green corridor at the edge of a city or between districts — protective open space, recreational greenway, and ecological buffer rolled together",
    tags=["park", "greenbelt", "buffer", "linear", "edge", "regional-greenway"],
    landscape_character=(
        "A greenbelt buffer park seen from drone altitude. The site is a wide linear corridor "
        "of protected open space — typically 100-300 meters wide and several hundred meters "
        "to several kilometres long — running along a city edge, riverside, or district "
        "boundary. The dominant landscape is a layered mosaic of mowed-lawn meadow, "
        "naturalised meadow, mixed deciduous-and-coniferous woodland, and occasional active-"
        "recreation nodes (small playgrounds, sports clusters, picnic groves) distributed "
        "along the length. A continuous central spine path — paved or compacted gravel — "
        "runs the full length, with branch paths leading to nodes and to perimeter access "
        "points. A few timber-and-shingle pavilions and trailhead kiosks appear at major "
        "access points. From above the park reads as a long green stripe across the broader "
        "landscape, with a clear central path-spine threading its length and node-cluster "
        "features punctuating the otherwise-naturalistic ground."
    ),
    paving="Continuous central spine path (paved or compacted gravel) with branch paths to nodes",
    planting="Layered mosaic of mowed lawn, naturalised meadow, mixed woodland, and node-specific planting",
    seating="Trailhead pavilions with benches, paired benches at nodes, occasional standalone benches along the spine",
    water="Optional small natural creek or riparian band running along one edge of the corridor",
    openness="Long linear corridor with alternating open and enclosed sections per the planting mosaic",
    prompt_subject="Aerial view of a wide linear greenbelt buffer park running along a city edge or between districts",
    prompt_details=[
        "Wide linear corridor 100-300m wide running across the broader landscape",
        "Layered mosaic of mowed lawn, naturalised meadow, mixed woodland, and node clusters",
        "Continuous central spine path (paved or gravel) running the full length",
        "Branch paths leading to recreational nodes and perimeter access",
        "Trailhead pavilions and kiosks at major access points",
        "Surrounding city edge or district boundary at the long sides",
    ],
    prompt_negative=[
        "No urban plaza hardscape dominating",
        "No continuous formal parterres",
        "No major arterial road inside the corridor",
        "No text overlays",
    ],
    property_presets={
        "tree_density_level": "medium",
        "tree_density": 0.45,
        "has_paths": True,
        "has_benches": True,
        "shade_strategy": "alternating_open_woodland",
    },
    variants_data=[
        variant(
            "greenbelt_buffer_park_v0", "Suburban Wide-Lawn Greenbelt", "#8FA86F",
            "Suburban wide-lawn greenbelt, roughly 120m wide by 200m long stretch of mowed-lawn meadow with scattered specimen-tree clusters and a single curving asphalt walking-cycling path running its length. Two small playgrounds and a picnic-shelter pavilion punctuate the corridor. Perimeter sidewalks border on each long side with single-family suburban housing visible beyond. Surrounding context shows a North-American suburban subdivision.",
            12000, 30000, 22000, "greenbelt-buffer-park"),
        variant(
            "greenbelt_buffer_park_v1", "Forested Commuter Rail-Trail Buffer", "#3F6B3F",
            "Forested commuter rail-trail greenbelt, roughly 150m wide by 300m long corridor of mature mixed-conifer-and-deciduous woodland with a paved bike-pedestrian rail-trail on a former rail bed running its length. A few benches and trailhead pavilions punctuate the trail. Smaller branch paths lead to perimeter access. Surrounding context shows a temperate-region urban edge with light commercial frontage on one side and residential on the other.",
            30000, 70000, 50000, "greenbelt-buffer-park"),
        variant(
            "greenbelt_buffer_park_v2", "Agricultural-Edge Hedgerow Buffer", "#7E9F5A",
            "Agricultural-edge hedgerow greenbelt, roughly 180m wide by 400m long corridor of meadow alternating with hedgerow blocks and small woodlots, separating a city-edge from the rural farmland beyond. A network of crushed-stone footpaths threads through. Stone walls and old farm-style timber gates mark the perimeter. A small heritage-farm interpretation pavilion sits at one corner. Surrounding context shows working agricultural fields on one side and a low-density city edge on the other.",
            60000, 120000, 90000, "greenbelt-buffer-park"),
        variant(
            "greenbelt_buffer_park_v3", "Active-Recreation Greenbelt Spine", "#6B8A4A",
            "Massive active-recreation greenbelt spine, roughly 250m wide by 800m long protected corridor of mixed mowed-lawn open space with multiple sports nodes — soccer fields, baseball diamonds, basketball courts, a large playground — clustered at intervals along a continuous paved central spine path. Multiple trailhead pavilions and parking lots at major intersections. Naturalised woodland buffers between the active nodes. Surrounding context shows a metropolitan suburban edge with an arterial road bordering one long side.",
            150000, 300000, 220000, "greenbelt-buffer-park"),
    ],
    render_overlay="Replace the colored zone with a photorealistic greenbelt buffer park. Wide linear corridor of layered green mosaic. Continuous central spine path. Branch paths to recreational nodes. Trailhead pavilions at access points. Node clusters (playgrounds, sports, picnic groves) distributed along length. Surrounding city edge or district boundary at the long sides. Keep surrounding satellite map context exactly as-is. Oblique aerial view, sharp shadows, photorealistic, 8k.",
    render_roof="Replace the colored zone viewed from directly above with a greenbelt buffer park. Long green linear stripe across the broader landscape. Central spine path threading its length. Node-cluster features punctuating the otherwise-naturalistic ground. Surrounding context at the long sides. Keep surrounding context exactly as-is.",
    render_negative="cartoon, illustration, sketch, low quality, blurry, text, watermark, unrealistic colors, urban plaza hardscape, formal parterres, major arterial inside the corridor",
    suggested_w=180, suggested_d=600, min_w=80, max_w=400, min_d=150, max_d=1500,
    min_area=12000, max_area=300000, suggested_area=80000,
    aspect_ratio="1:3.3", shape="linear",
)


# ---------------------------------------------------------------------------
# 8) Foothill Trail Park
# ---------------------------------------------------------------------------
foothill_trail_park = archetype(
    id="foothill_trail_park",
    slug="foothill-trail-park",
    title="Foothill Trail Park",
    description="A wilder ridge-trail landscape park at the foothills of mountains or rolling hills — narrow walking trails, viewpoint outcrops, sparse rustic infrastructure, and a regional-conservation feel distinct from manicured urban parks",
    tags=["park", "foothill", "trail", "ridge-trail", "regional", "wilderness", "conservation"],
    landscape_character=(
        "A foothill ridge-trail park seen from drone altitude. The site occupies wilder "
        "terrain at the toe of mountains or rolling foothills — typically irregular "
        "boundaries following a ridgeline, watershed, or conservation parcel. The dominant "
        "landscape is biome-specific natural cover (montane forest, sage-scrub, eucalyptus, "
        "alpine meadow, heathland) with rocky outcrops or grassland breaks. A network of "
        "narrow earthen walking-and-cycling trails follows ridgelines and contours, marked "
        "by occasional cor-ten signposts and small log-or-stone benches at viewpoint outcrops. "
        "Trailheads at lower elevation have small gravel parking lots, simple log-frame "
        "kiosks, and pit-toilet shelters — minimal infrastructure compared to urban parks. "
        "The character is regional-conservation rather than manicured-recreation. From above "
        "the park reads as a swath of natural biome cover threaded by narrow trail lines "
        "with rocky outcrop or meadow breaks visible as paler patches."
    ),
    paving="Narrow earthen or fine-gravel trails contouring the terrain; small gravel trailhead parking lots",
    planting="Biome-specific natural cover — montane forest, sage-scrub, eucalyptus, alpine meadow, or heathland — left mostly unmanaged",
    seating="Log-or-stone benches at viewpoint outcrops, simple log-frame trailhead kiosks",
    water="Natural seasonal streams crossing the trails; no decorative water features",
    openness="Wild-natural-feeling enclosure varying with biome; trails open to long ridge vistas",
    prompt_subject="Aerial view of a foothill ridge-trail conservation park with narrow trails contouring the natural biome cover",
    prompt_details=[
        "Wilder terrain at the toe of mountains or rolling hills, irregular conservation boundary",
        "Biome-specific natural cover dominating the ground plane",
        "Narrow earthen walking trails following ridgelines and contours",
        "Cor-ten signposts and log-or-stone benches at viewpoint outcrops",
        "Small gravel trailhead parking lots and log-frame kiosks at access",
        "Surrounding rural-conservation or low-density edge",
    ],
    prompt_negative=[
        "No manicured urban-park lawn dominating",
        "No urban plaza hardscape",
        "No suburban subdivision inside the park",
        "No text overlays",
    ],
    property_presets={
        "tree_density_level": "variable",
        "tree_density": 0.45,
        "has_paths": True,
        "has_benches": False,
        "shade_strategy": "biome_natural",
    },
    variants_data=[
        variant(
            "foothill_trail_park_v0", "California Sage-Scrub Ridge", "#A8A06F",
            "California-style sage-scrub ridge trail park, roughly 200 by 250 meters of arid coastal-California foothill terrain dominated by silver-grey-green California sage and chamise scrub broken by occasional rocky outcrops. Narrow earthen ridge-line trail with switchbacks descends to a small log-frame trailhead kiosk. Sparse coast-live-oak clusters in the canyon bottoms. A small wood-railed viewpoint platform at a ridge spur. Surrounding context shows a California-foothill edge with dry grassland transitioning to suburban hillside neighbourhoods.",
            30000, 80000, 50000, "foothill-trail-park"),
        variant(
            "foothill_trail_park_v1", "Australian Eucalyptus Ridge", "#7E9F5A",
            "Australian eucalyptus ridge trail park, roughly 250 by 300 meters of rolling foothill terrain dominated by tall mature eucalyptus forest with smooth pale trunks and sparse blue-grey canopy. Reddish-earth narrow trails contour the slopes. Occasional grassy paddock breaks and rocky outcrops with kookaburra-friendly pavilion-style timber-and-corrugated-iron viewpoint shelters. Bushland kangaroo-trail evidence. Surrounding context shows an Australian rural-edge transitioning to a regional country town.",
            60000, 150000, 100000, "foothill-trail-park"),
        variant(
            "foothill_trail_park_v2", "UK Heathland Moor Trail", "#8B7355",
            "UK heathland-moor trail park, roughly 350 by 280 meters of open windswept heath dominated by purple heather and gorse with rough peaty trail tracks contouring across rolling moorland. A few isolated stunted hawthorns. Stone cairn waymarkers at trail junctions. A small drystone-walled livestock fold/refuge. Distant tor outcrops. Surrounding context shows an Atlantic-British upland-edge with stone-walled fields transitioning to a small heritage moor village.",
            120000, 300000, 200000, "foothill-trail-park"),
        variant(
            "foothill_trail_park_v3", "Alpine Larch Ridge Trail", "#3F6B3F",
            "Alpine-larch high-country ridge trail park, roughly 500 by 400 meters of subalpine montane terrain dominated by alpine larch forest with golden-yellow autumn needles, alpine meadow clearings, and rocky scree slopes. A long ridge trail traverses three named viewpoint summits. Small log-frame backcountry shelters at trail junctions. Tarns (small lakes) reflecting the surrounding peaks. Surrounding context shows an alpine national-park boundary transitioning to a high-elevation valley with a single mountain road.",
            300000, 800000, 500000, "foothill-trail-park"),
    ],
    render_overlay="Replace the colored zone with a photorealistic foothill ridge-trail conservation park. Wilder terrain at the toe of mountains or rolling foothills with biome-specific natural cover. Narrow earthen walking trails following ridgelines and contours. Cor-ten signposts and log benches at viewpoint outcrops. Small gravel trailhead parking lots and log-frame kiosks at access. Surrounding rural-conservation or low-density edge. Keep surrounding satellite map context exactly as-is. Oblique aerial view, dramatic raking light, sharp shadows, photorealistic, 8k.",
    render_roof="Replace the colored zone viewed from directly above with a foothill conservation park. Swath of biome-specific natural cover. Narrow trail lines threading the terrain. Rocky outcrop or meadow breaks visible as paler patches. Small trailhead parking and kiosk shapes at access. Surrounding rural edge. Keep surrounding context exactly as-is.",
    render_negative="cartoon, illustration, sketch, low quality, blurry, text, watermark, unrealistic colors, manicured urban-park lawn, urban plaza hardscape, suburban subdivision",
    suggested_w=400, suggested_d=400, min_w=100, max_w=900, min_d=100, max_d=900,
    min_area=30000, max_area=800000, suggested_area=200000,
    aspect_ratio="1:1", shape="irregular",
)


# ---------------------------------------------------------------------------
# Emit
# ---------------------------------------------------------------------------
all_archetypes = [picturesque_park, reclaimed_industrial_park, quarry_garden_park,
                  hilltop_park, estate_picnic_grove, reservoir_park,
                  greenbelt_buffer_park, foothill_trail_park]


def emit_snippet(archetypes: list[dict]) -> str:
    out_lines: list[str] = []
    for arch in archetypes:
        text = json.dumps(arch, indent=2, ensure_ascii=False)
        prefixed = "\n".join("    " + line for line in text.splitlines())
        out_lines.append(prefixed + ",")
    return "\n".join(out_lines)


def main() -> int:
    snippet = emit_snippet(all_archetypes)
    try:
        json.loads("[" + snippet.rstrip(",") + "]")
    except json.JSONDecodeError as e:
        print(f"ERROR: emitted snippet is not valid JSON: {e}")
        return 1

    out_path = Path(__file__).parent / "_landscape_parks_snippet.json"
    out_path.write_text(snippet, encoding="utf-8")
    print(f"OK: wrote {len(snippet)} chars to {out_path}")
    print(f"Validates as JSON array of {len(all_archetypes)} entries")
    return 0


if __name__ == "__main__":
    sys.exit(main())
