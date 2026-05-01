"""Compose 6 new Waterfront Space archetype entries as JSON-valid text.

Run:  python scripts/_compose_new_waterfront.py
Output: scripts/_waterfront_snippet.json
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
              min_area, max_area, suggested_area, aspect_ratio, shape,
              space_type="park"):
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
        "aestheticCategory": "waterfront_spaces",
        "spaceType": space_type,
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
# 1) Marina / Yacht Harbor
# ---------------------------------------------------------------------------
marina = archetype(
    id="marina_yacht_harbor",
    slug="marina-yacht-harbor",
    title="Marina / Yacht Harbor",
    description="A protected small-craft harbour with floating docks, slip pontoons, breakwater, dockmaster building, and a public landside promenade ringing the harbour basin",
    tags=["waterfront", "marina", "yacht-harbor", "docks", "breakwater", "small-craft"],
    landscape_character=(
        "A protected small-craft marina seen from drone altitude. The site is a roughly "
        "rectangular or D-shaped basin of calm clear water sheltered by a stone-or-concrete "
        "breakwater on the seaward side. Inside the basin, a regular rhythm of floating "
        "timber-and-aluminium dock fingers extends from the landside quay perpendicular to "
        "the shore, creating numbered slip rows. Sailing yachts, motor cruisers, and small "
        "fishing boats are tied alongside the slips with masts visible as a forest of "
        "vertical pencils from above. A landside paved quay runs along the shore with the "
        "dockmaster's two-storey timber-clad building, fuel dock, and a small chandlery shop "
        "clustered at one end. A public promenade with benches, lamp posts, and small "
        "planters runs along the upper landside edge open to walking visitors. Pollard "
        "bollards punctuate the quay edge. From above the marina reads as a calm rectangular "
        "water basin with regular rectangular dock fingers and a striped pattern of moored "
        "boats, framed by a paved quay and a curving breakwater arm."
    ),
    paving="Concrete or stone-paver landside quay and promenade; timber-and-aluminium floating dock fingers",
    planting="Small landside planters with hardy salt-tolerant grasses and small accent palms or sycamores; minimal in-water planting",
    seating="Benches and small picnic tables along the public promenade, mooring bollards as informal seats",
    water="The harbour basin itself; small fuel-dock fountain or boat-cleanup hose station",
    openness="Strongly open to the seaward edge through the breakwater opening; landside enclosed by the harbour buildings and promenade",
    prompt_subject="Aerial view of a protected small-craft marina with floating dock fingers, moored boats, breakwater, and landside dockmaster building",
    prompt_details=[
        "Roughly rectangular or D-shaped basin of calm clear water",
        "Stone or concrete breakwater protecting the seaward side with one navigation entrance",
        "Regular rhythm of floating timber-and-aluminium dock fingers perpendicular to shore",
        "Sailing yachts and motor cruisers tied alongside slips with masts visible from above",
        "Two-storey landside dockmaster building, fuel dock, and chandlery clustered at one end",
        "Public promenade with benches and lamp posts along the landside edge",
    ],
    prompt_negative=[
        "No commercial fishing wharf with industrial trawlers",
        "No urban plaza dominating the landside",
        "No grass lawn dominating",
        "No text overlays",
    ],
    property_presets={
        "tree_density_level": "very_low",
        "tree_density": 0.05,
        "has_paths": True,
        "has_benches": True,
        "shade_strategy": "minimal_landside",
    },
    variants_data=[
        variant(
            "marina_yacht_harbor_v0", "Inland-Lake Recreational Marina", "#6B8A4A",
            "Inland-lake recreational marina, roughly 60 by 80 meters of small calm freshwater inlet with two parallel timber-floating-dock fingers each holding 8 small motorboat and sailboat slips. A modest single-storey timber-clad boathouse with a fuel pump sits at the head of the docks. A small gravel parking pad, a kayak rack, and a single concrete boat ramp at the far end. Surrounding context shows a forested freshwater-lake recreational shoreline with cabins.",
            3000, 8000, 5000, "marina-yacht-harbor"),
        variant(
            "marina_yacht_harbor_v1", "Working Fishing-Harbour", "#5C5C5C",
            "Working small-fishing-harbour, roughly 80 by 100 meters of stone-walled harbour basin with a continuous concrete quay around the inside edge. Wooden trawlers and small fishing boats tied alongside the quay with nets and crates visible on the decks. A small fish-market shed and ice plant occupy the landside. A short stone breakwater arm protects the entrance. Surrounding context shows a Mediterranean or Atlantic coastal-fishing-village setting with whitewashed or stone houses climbing the hillside behind.",
            5500, 12000, 8500, "marina-yacht-harbor"),
        variant(
            "marina_yacht_harbor_v2", "Pacific-Style Floating-Dock Marina", "#5B7065",
            "Pacific-Northwest-style floating-dock marina, roughly 120 by 140 meters of protected harbour basin with five long floating-dock fingers extending from a continuous landside boardwalk. 60-80 sailing yachts and motor cruisers in slips, plus a designated guest-dock for transient visitors. A two-storey timber-clad dockmaster building with cafe-and-marine-supply shop clusters near the entry. A small public-promenade-and-park edge runs along the shore. Surrounding context shows a Pacific-coast harbourside town.",
            14000, 25000, 20000, "marina-yacht-harbor"),
        variant(
            "marina_yacht_harbor_v3", "Mediterranean Superyacht Harbour", "#A0826D",
            "Mediterranean superyacht harbour, roughly 200 by 250 meters of large protected harbour basin with multiple long stone-and-concrete piers and floating dock fingers accommodating large motor yachts and superyachts (40-100m vessels). A long curving stone breakwater arm with a lighthouse marks the entrance. The landside features a wide stone-paver promenade lined with palms, paired with a continuous row of yacht-club, restaurant, and shopping pavilions. Surrounding context shows a Mediterranean Riviera coastal town with terraced pastel-coloured villas climbing the hillside.",
            35000, 80000, 55000, "marina-yacht-harbor"),
    ],
    render_overlay="Replace the colored zone with a photorealistic small-craft marina. Roughly rectangular or D-shaped basin of calm clear water. Stone or concrete breakwater protecting the seaward side. Regular floating dock fingers perpendicular to shore. Sailing yachts and motor cruisers tied alongside slips. Two-storey dockmaster building, fuel dock, and chandlery clustered at one end. Public promenade with benches. Surrounding coastal town. Keep surrounding satellite map context exactly as-is. Oblique aerial view, late-afternoon golden hour, sharp shadows, photorealistic, 8k.",
    render_roof="Replace the colored zone viewed from directly above with a marina. Calm rectangular water basin with regular rectangular dock fingers extending from shore. Striped pattern of moored boats. Paved quay border and curving breakwater arm. Dockmaster-building roof and small landside structures. Surrounding coastal town. Keep surrounding context exactly as-is.",
    render_negative="cartoon, illustration, sketch, low quality, blurry, text, watermark, unrealistic colors, industrial commercial fishing wharf with trawlers, urban plaza dominating landside",
    suggested_w=120, suggested_d=140, min_w=40, max_w=300, min_d=50, max_d=350,
    min_area=3000, max_area=80000, suggested_area=15000,
    aspect_ratio="1:1.15", shape="irregular",
)


# ---------------------------------------------------------------------------
# 2) Working Pier / Wharf Conversion
# ---------------------------------------------------------------------------
working_pier_conversion = archetype(
    id="working_pier_wharf_conversion",
    slug="working-pier-wharf-conversion",
    title="Working Pier / Wharf Conversion",
    description="A former industrial cargo or rail pier converted into a public landscape — preserving the heavy-timber piling structure and warehouse shed bones while overlaying lawn, sports, retail, or art programming",
    tags=["waterfront", "pier", "wharf", "conversion", "adaptive-reuse", "industrial"],
    landscape_character=(
        "A converted working pier or wharf seen from drone altitude. The site is a long "
        "rectangular timber-or-concrete pier extending out into a river or harbour from a "
        "shore edge, originally built for cargo handling or rail freight and now reprogrammed "
        "as a public landscape. The pier's heavy industrial bones are preserved — bollards, "
        "rail tracks set into the deck surface, sections of the original warehouse shed roof "
        "kept as covered pavilion shelters, cor-ten cleats and tie-downs as sculptural "
        "punctuation. The pier deck holds layered contemporary programs: lawn panels, "
        "playgrounds, sports courts, performance pads, kiosk-and-café pavilions, and "
        "perimeter timber-railed promenade walkways. Pioneer-tree planters in heavy timber "
        "boxes break up the deck. A continuous edge railing runs the perimeter. From above "
        "the pier reads as a long rectangular projection out from shore with a layered "
        "patchwork of programs visible across the deck and the original industrial bones "
        "(sheds, rails, pilings) as preserved infrastructure."
    ),
    paving="Original concrete or asphalt pier deck preserved; new timber, gravel, or grass overlay panels",
    planting="Pioneer-tree groves in heavy timber planters; salt-tolerant grass panels; climbing vines on preserved warehouse walls",
    seating="Benches and lounge seating distributed across program zones; original bollards as informal seats",
    water="Surrounding harbour or river water on three sides; possible water-play feature on the deck",
    openness="Long projection out into open water; programs enclosed by original industrial bones",
    prompt_subject="Aerial view of a converted working pier or wharf with preserved industrial bones and contemporary public-park programming on the deck",
    prompt_details=[
        "Long rectangular pier extending from shore into water on three sides",
        "Preserved industrial bones — bollards, deck-set rails, original warehouse shed sections",
        "Layered program zones — lawn panels, playgrounds, sports courts, kiosk-and-café pavilions",
        "Pioneer-tree planters in heavy timber boxes punctuating the deck",
        "Continuous timber-railed promenade walkway along the perimeter",
        "Surrounding city waterfront or working-river edge context",
    ],
    prompt_negative=[
        "No active cargo cranes or shipping containers on the pier",
        "No casual park lawn dominating without industrial preservation",
        "No urban plaza without water context",
        "No text overlays",
    ],
    property_presets={
        "tree_density_level": "low",
        "tree_density": 0.2,
        "has_paths": True,
        "has_benches": True,
        "shade_strategy": "preserved_warehouse_pavilions",
    },
    variants_data=[
        variant(
            "working_pier_wharf_conversion_v0", "Granville-Island Public Market Pier", "#8B6914",
            "Granville-Island-style public-market converted pier, roughly 70 by 100 meters of preserved industrial pier with original corrugated-metal warehouse sheds adapted as a public-market food hall and arts complex. Cobbled pavement around the buildings; small wharf-side benches; floating boat-tied-up restaurants alongside one edge. A small concrete plaza with a totem pole. Surrounding context shows a working-creek industrial-arts district with a downtown skyline beyond.",
            5000, 10000, 7500, "working-pier-wharf-conversion"),
        variant(
            "working_pier_wharf_conversion_v1", "Pier-39 Retail Tourist Boardwalk", "#B8860B",
            "Pier-39-style tourist retail boardwalk pier, roughly 80 by 120 meters of long timber-decked pier with a continuous double row of small wood-shingle retail kiosks lining a central pedestrian promenade. A small carousel and arcade pavilion at the seaward end. Sea-lion floating-dock viewing deck on one side. Marine-themed nautical-rope-and-buoy decoration. Surrounding context shows a tourist-waterfront-district with mid-rise hotels.",
            8000, 14000, 11000, "working-pier-wharf-conversion"),
        variant(
            "working_pier_wharf_conversion_v2", "Industrial Loading-Pier Adaptive", "#5C5C5C",
            "Industrial-loading-pier adaptive-overlay park, roughly 100 by 180 meters of preserved heavy-concrete cargo pier with cor-ten and weathered-timber programs overlaid: rusted-rail walking path running the spine, salt-meadow garden panels, a small skate-and-bike plaza, retained warehouse shed as covered pavilion, a few timber-shipping-crate climbing structures. Surrounding context shows a working-harbour industrial waterfront with active container terminals nearby.",
            18000, 30000, 24000, "working-pier-wharf-conversion"),
        variant(
            "working_pier_wharf_conversion_v3", "Brooklyn-Bridge-Park Pier", "#5B7065",
            "Brooklyn-Bridge-Park-style massive sports-and-lawn pier, roughly 150 by 250 meters of long projecting public-park pier on heavy-timber-and-steel pilings, with a layered program of large lawn panels, multiple basketball-and-soccer courts, a sand-volleyball pit, kiosk-and-café pavilions, perimeter promenade with benches, and pioneer-birch planters. Preserved trolley-track inset into the deck. Surrounding context shows a major US-city waterfront with an iconic suspension bridge and downtown skyline.",
            30000, 60000, 45000, "working-pier-wharf-conversion"),
    ],
    render_overlay="Replace the colored zone with a photorealistic converted working pier or wharf. Long rectangular pier extending from shore into water. Preserved industrial bones — bollards, deck-set rails, original warehouse shed sections. Layered program zones — lawn panels, playgrounds, sports courts, kiosk-and-café pavilions. Pioneer-tree planters in heavy timber boxes. Continuous timber-railed promenade. Surrounding city waterfront. Keep surrounding satellite map context exactly as-is. Oblique aerial view, late-afternoon golden hour, sharp shadows, photorealistic, 8k.",
    render_roof="Replace the colored zone viewed from directly above with a converted pier. Long rectangular projection out from shore into water on three sides. Layered patchwork of program shapes across the deck. Original industrial bones as preserved infrastructure. Surrounding city waterfront. Keep surrounding context exactly as-is.",
    render_negative="cartoon, illustration, sketch, low quality, blurry, text, watermark, unrealistic colors, active cargo cranes, shipping containers on the pier, urban plaza without water context",
    suggested_w=100, suggested_d=180, min_w=30, max_w=200, min_d=50, max_d=350,
    min_area=4000, max_area=60000, suggested_area=15000,
    aspect_ratio="1:1.8", shape="rectangular",
)


# ---------------------------------------------------------------------------
# 3) Floating Park / Pool
# ---------------------------------------------------------------------------
floating_park = archetype(
    id="floating_park_pool",
    slug="floating-park-pool",
    title="Floating Park / Pool",
    description="A landscape platform built directly over a river or harbour — an island park supported on pillars, a moored floating pontoon meadow, or a floating swim-pool basin",
    tags=["waterfront", "floating", "island", "pool", "pontoon", "iconic"],
    landscape_character=(
        "A floating park or pool seen from drone altitude. The site is a constructed landscape "
        "platform sitting on or over a body of water — either supported by sculpted concrete "
        "pillars rising from the harbour bed (Little-Island-style), moored as floating timber-"
        "and-foam pontoons (Copenhagen-harbour-bath style), or as a floating filtered-water "
        "swim basin (Plus-Pool style). The platform's edges are bounded by glass, steel, or "
        "timber railings. The deck supports landscaped meadow, walking paths, viewing "
        "decks, performance areas, or swim lanes depending on type. Connection to shore is "
        "made by one or two narrow gangway bridges. Floating boats may surround. Bridges "
        "rise above the water connecting back to the urban shore. From above the platform "
        "reads as a discrete shaped object floating in the water with its own internal "
        "geometry, connected to the shore by a thin gangway thread."
    ),
    paving="Timber decking, gravel, or stone-paver platform surface; deck-railing perimeter",
    planting="Meadow grass and small shrubs in shallow planters on the platform; flowering perennials at viewpoints",
    seating="Built-in deck benches, open viewing platforms, shaded lounge pavilions; pool-edge benches if applicable",
    water="Surrounded by harbour, river, or open-sea water on all sides",
    openness="Strongly enclosed by water on all sides with single shore-connection point",
    prompt_subject="Aerial view of a floating park or swim-pool platform sitting on or over a body of water connected to shore by a narrow gangway",
    prompt_details=[
        "Constructed landscape platform sitting on or over a body of water",
        "Edges bounded by glass, steel, or timber railings",
        "Platform deck supports meadow, walking paths, viewing decks, or swim lanes",
        "Connection to shore by one or two narrow gangway bridges",
        "Surrounding harbour, river, or open-sea water on all sides",
        "Surrounding city waterfront or harbour edge context",
    ],
    prompt_negative=[
        "No park sitting on dry land",
        "No conventional pier (must clearly read as floating or pillar-supported)",
        "No working ship",
        "No text overlays",
    ],
    property_presets={
        "tree_density_level": "low",
        "tree_density": 0.2,
        "has_paths": True,
        "has_benches": True,
        "shade_strategy": "shaded_lounge_pavilions",
    },
    variants_data=[
        variant(
            "floating_park_pool_v0", "Plus-Pool Style Swim Basin", "#5B7065",
            "Plus-Pool-style floating filtered-water swim basin, roughly 30 by 30 meters of cross-shaped (or +-shape) pool basin moored in a clean harbour, divided into four arms (sport lap, lounge, kids, leisure). Timber-clad perimeter walkway with low railings. A single gangway connection to a shore-side bathhouse. Surrounding context shows a contemporary urban waterfront with mid-rise lofts.",
            500, 1500, 1000, "floating-park-pool"),
        variant(
            "floating_park_pool_v1", "Copenhagen Harbour Bath", "#708090",
            "Copenhagen-Harbour-Bath-style floating swim platform, roughly 50 by 50 meters of timber-decked floating pontoon platform with multiple swim basins of different depths, a slide and diving tower at one end, and a shaded shower-and-changing pavilion. Deck-edge ladders into the harbour. Lifeguard station central. Surrounding context shows a Scandinavian urban waterfront with low-rise harbourside warehouses converted to apartments.",
            1500, 3000, 2200, "floating-park-pool"),
        variant(
            "floating_park_pool_v2", "Floating-Boardwalk Meadow Loop", "#3F6B3F",
            "Floating-boardwalk meadow-loop park, roughly 80 by 60 meters of moored timber-pontoon park with a winding meadow-grass-and-wildflower-planted top surface and a perimeter loop boardwalk. Several small open viewing decks. Pollinator-friendly wildflower planting in shallow soil. A narrow gangway to shore. Surrounding context shows a brackish harbour edge with reedbed-and-marsh wetlands and low-rise residential beyond.",
            3000, 5500, 4000, "floating-park-pool"),
        variant(
            "floating_park_pool_v3", "Little-Island Pillar-Meadow", "#5B7065",
            "Little-Island-style sculpted-pillar-supported elevated park, roughly 100 by 80 meters of organic-shaped landscape platform supported by 132 sculpted concrete tulip-shaped pillars rising from the harbour bed at varied heights. The platform's surface holds a layered landscape of small lawns, sloping flower meadows, mature specimen trees, winding pedestrian paths, and a small open-sided amphitheatre at one end. Two arched footbridge connections to shore. Surrounding context shows a major-US-city iconic urban harbour with skyline.",
            5500, 9000, 7500, "floating-park-pool"),
    ],
    render_overlay="Replace the colored zone with a photorealistic floating park or swim platform. Constructed landscape platform sitting on or over water. Edges bounded by railings. Platform deck supports meadow, walking paths, viewing decks, or swim lanes per the variant. Narrow gangway connection to shore. Surrounding water on all sides. Surrounding city waterfront. Keep surrounding satellite map context exactly as-is. Oblique aerial view, late-afternoon golden hour, sharp shadows, photorealistic, 8k.",
    render_roof="Replace the colored zone viewed from directly above with a floating park or pool. Discrete shaped platform floating in the water with its own internal geometry. Surrounding water visible all around. Thin gangway thread connecting to shore. Surrounding city waterfront. Keep surrounding context exactly as-is.",
    render_negative="cartoon, illustration, sketch, low quality, blurry, text, watermark, unrealistic colors, park on dry land, conventional pier, working ship",
    suggested_w=80, suggested_d=70, min_w=20, max_w=140, min_d=20, max_d=120,
    min_area=500, max_area=10000, suggested_area=3500,
    aspect_ratio="1.15:1", shape="irregular",
)


# ---------------------------------------------------------------------------
# 4) Lighthouse Point / Headland Park
# ---------------------------------------------------------------------------
lighthouse_point_park = archetype(
    id="lighthouse_point_park",
    slug="lighthouse-point-park",
    title="Lighthouse Point / Headland Park",
    description="A coastal headland or rocky point park anchored by a working lighthouse, with windswept grass-and-rock terrain, viewing platforms, an interpretive station, and dramatic sea vistas",
    tags=["waterfront", "lighthouse", "headland", "coastal", "rocky-point", "vista"],
    landscape_character=(
        "A coastal lighthouse-point park seen from drone altitude. The site is a rocky or "
        "grassy promontory projecting out into open ocean, with the working lighthouse — a "
        "tall painted (white-and-red, or all-white) cylindrical tower with a glass lantern "
        "room on top — standing on the highest point of the headland. The lighthouse keeper's "
        "stone-or-timber cottage and a small interpretive-museum building stand nearby. "
        "Walking paths of crushed gravel or boardwalk-on-rock follow the headland edges to "
        "viewing platforms and benches at the most dramatic vantage points. The terrain is "
        "windswept salt-meadow grass with patches of exposed bedrock, scattered low juniper "
        "or coastal heather, and occasional twisted-form coastal trees. A single access road "
        "or path leads from the mainland to a small visitor parking lot. From above the park "
        "reads as a green-and-grey rocky headland projecting into surrounding blue water, "
        "with the lighthouse tower casting a long shadow as the focal vertical accent."
    ),
    paving="Crushed-gravel paths and boardwalk-on-rock viewing platforms; small visitor parking lot",
    planting="Windswept salt-meadow grass, low juniper and coastal heather, scattered twisted-form coastal trees",
    seating="Stone benches at viewing platforms, paired benches along the headland paths",
    water="Surrounding open ocean on three sides; no internal water features",
    openness="Strongly open to ocean on three sides; lighthouse tower as dominant vertical anchor",
    prompt_subject="Aerial view of a coastal lighthouse-point park with a working lighthouse on a rocky headland projecting into open ocean",
    prompt_details=[
        "Rocky or grassy promontory projecting out into open ocean",
        "Tall painted cylindrical lighthouse tower with glass lantern room standing on the high point",
        "Lighthouse keeper's cottage and small interpretive building nearby",
        "Crushed-gravel walking paths or boardwalk leading to viewing platforms and benches",
        "Windswept salt-meadow grass with patches of exposed bedrock and low juniper",
        "Single access road and small visitor parking lot at the landward edge",
    ],
    prompt_negative=[
        "No urban harbour with boats and docks",
        "No commercial fishing wharf",
        "No urban plaza on the headland",
        "No text overlays",
    ],
    property_presets={
        "tree_density_level": "very_low",
        "tree_density": 0.05,
        "has_paths": True,
        "has_benches": True,
        "shade_strategy": "minimal_windswept",
    },
    variants_data=[
        variant(
            "lighthouse_point_park_v0", "Cape Rocky-Headland Light", "#5C5C5C",
            "Small Cape-style rocky-headland lighthouse point, roughly 80 by 100 meters of windswept rocky promontory with a small white-and-red painted timber-clad cylindrical lighthouse and adjacent two-storey timber keeper's cottage. Crushed-gravel path leads from a small parking lot to the lighthouse and continues along the headland edge to two stone-bench viewing platforms. Sparse juniper and salt-meadow grass cover the rock. Surrounding context shows an Atlantic-coast forested mainland with a single access road descending to the headland.",
            5000, 12000, 8000, "lighthouse-point-park"),
        variant(
            "lighthouse_point_park_v1", "Atlantic Dune Point Light Station", "#A8A06F",
            "Atlantic-dune-point lighthouse station, roughly 120 by 150 meters of low sandy dune-and-grass headland with a tall painted-stone-cylindrical lighthouse, an attached timber-and-shingle keeper's house complex, and a small interpretive-museum pavilion. Boardwalk paths through the dune grass to the lighthouse and to viewing decks at the headland tip. Surrounding context shows a Mid-Atlantic dune-and-marsh coastal landscape with the open ocean on three sides.",
            12000, 25000, 18000, "lighthouse-point-park"),
        variant(
            "lighthouse_point_park_v2", "Pacific Cliff Promontory Light", "#5B7065",
            "Pacific-Northwest cliff-promontory lighthouse point, roughly 180 by 200 meters of dramatic rocky cliff-edge promontory rising 30m above the surf below, with an iconic white-painted concrete-cylindrical lighthouse, attached fog-signal building, and Coast-Guard interpretive complex. Crushed-stone paths lead to multiple cliff-edge viewing platforms with safety railings. Wind-twisted Sitka spruce cling to sheltered hollows. Surrounding context shows a Pacific-coast headland with sweeping ocean horizons.",
            18000, 35000, 28000, "lighthouse-point-park"),
        variant(
            "lighthouse_point_park_v3", "Mediterranean Fortress Lighthouse", "#A0826D",
            "Mediterranean fortress-style lighthouse-and-esplanade point, roughly 200 by 180 meters of large rocky-coastal promontory with a tall stone-and-iron cylindrical lighthouse rising from the corner of an old stone fortress complex. A wide stone-paved esplanade with palms wraps the headland with iron-railed viewing balconies projecting over the cliff. A small chapel and museum complex within the fortress walls. Surrounding context shows a Mediterranean coastal town with terraced pastel-coloured villas approaching from the mainland.",
            28000, 50000, 38000, "lighthouse-point-park"),
    ],
    render_overlay="Replace the colored zone with a photorealistic coastal lighthouse-point park. Rocky or grassy promontory projecting into open ocean. Tall painted lighthouse tower as dominant vertical anchor. Keeper's cottage and small interpretive building nearby. Walking paths leading to viewing platforms and benches. Windswept salt-meadow grass with bedrock patches and low juniper. Single access road and small parking lot. Keep surrounding satellite map context exactly as-is. Oblique aerial view, dramatic raking afternoon light, sharp shadows, photorealistic, 8k.",
    render_roof="Replace the colored zone viewed from directly above with a coastal lighthouse-point park. Green-and-grey rocky headland projecting into surrounding blue water. Lighthouse-tower roof shape casting a long thin shadow. Keeper's cottage and interpretive building roof shapes. Path lines and viewing-platform shapes along the headland edges. Surrounding ocean on three sides. Keep surrounding context exactly as-is.",
    render_negative="cartoon, illustration, sketch, low quality, blurry, text, watermark, unrealistic colors, urban harbour, commercial fishing wharf, urban plaza on headland",
    suggested_w=180, suggested_d=180, min_w=50, max_w=320, min_d=50, max_d=300,
    min_area=5000, max_area=50000, suggested_area=20000,
    aspect_ratio="1:1", shape="irregular",
)


# ---------------------------------------------------------------------------
# 5) Tidal Marsh Boardwalk
# ---------------------------------------------------------------------------
tidal_marsh_boardwalk = archetype(
    id="tidal_marsh_boardwalk",
    slug="tidal-marsh-boardwalk",
    title="Tidal Marsh Boardwalk",
    description="An ecological tidal-edge park with elevated timber boardwalks and viewing platforms threading through salt marsh, mangrove, or estuary mudflat habitat",
    tags=["waterfront", "tidal-marsh", "boardwalk", "estuary", "ecological", "interpretive"],
    landscape_character=(
        "A tidal-marsh boardwalk park seen from drone altitude. The site is a stretch of "
        "intertidal habitat — salt marsh, cordgrass meadow, mangrove flat, or estuary mud — "
        "with a network of elevated timber-and-steel boardwalks raised about a meter above "
        "the marsh surface threading through the habitat. Boardwalk segments converge at "
        "polygonal viewing platforms with bench seating, interpretive signage, and bird-"
        "watching blinds. A small gravel-paved trailhead pavilion sits at the landward end "
        "with a parking lot and an interpretive-pavilion shelter. Channels of tidal water "
        "wind through the marsh in serpentine lines, exposed at low tide and submerged at "
        "high tide. Native marsh grasses (cordgrass, reed, phragmites depending on biome) "
        "form dense low cover. Occasional small navigable channel visible. From above the "
        "park reads as a green-and-brown marsh expanse threaded by a thin pale boardwalk "
        "network with polygonal platforms and bordered by a thin landside path-and-pavilion."
    ),
    paving="Elevated timber-and-steel boardwalk planks; small gravel landside trailhead and parking lot",
    planting="Native marsh vegetation — cordgrass, reed, phragmites, or mangrove — left ecological-uncultivated",
    seating="Polygonal viewing-platform benches; benches at the trailhead pavilion",
    water="The tidal marsh itself with serpentine tidal channels; no decorative water features",
    openness="Open horizontal marsh expanse with elevated boardwalk thread as the only built form",
    prompt_subject="Aerial view of a tidal marsh boardwalk park with elevated timber boardwalks threading through salt-marsh or mangrove habitat",
    prompt_details=[
        "Stretch of intertidal habitat — salt marsh, cordgrass, mangrove, or mudflat",
        "Network of elevated timber-and-steel boardwalks raised above the marsh",
        "Polygonal viewing platforms with bench seating and bird-blinds at intervals",
        "Small gravel-paved trailhead pavilion and parking lot at the landward end",
        "Tidal channels winding through the marsh in serpentine lines",
        "Native marsh vegetation forming dense low cover",
    ],
    prompt_negative=[
        "No urban plaza or paved hardscape inside the marsh",
        "No buildings on the marsh surface (only small platforms)",
        "No casual park lawn",
        "No text overlays",
    ],
    property_presets={
        "tree_density_level": "low",
        "tree_density": 0.15,
        "has_paths": True,
        "has_benches": True,
        "shade_strategy": "platform_shelters",
    },
    variants_data=[
        variant(
            "tidal_marsh_boardwalk_v0", "Cordgrass Salt-Marsh Boardwalk", "#7E9F5A",
            "Cordgrass salt-marsh boardwalk park, roughly 100 by 150 meters of east-coast Spartina cordgrass salt marsh with a single linear timber boardwalk threading from a small landside parking lot out to a single hexagonal viewing platform near the marsh-edge. Tidal creek winding past the platform. Small interpretive-signage pavilion at the trailhead. Surrounding context shows an Atlantic-coast estuary with low-rise residential set back behind the marsh boundary.",
            6000, 18000, 12000, "tidal-marsh-boardwalk"),
        variant(
            "tidal_marsh_boardwalk_v1", "Mangrove Tidal-Flat Walk", "#3F6B3F",
            "Mangrove tidal-flat boardwalk park, roughly 150 by 200 meters of subtropical mangrove forest with a Y-shaped boardwalk threading through dense mangrove canopy and across exposed mudflats. Two viewing platforms at the boardwalk junctions with bird-blind screens. Crab-burrowed mudflat clearings between mangrove clumps. A small open-air trailhead pavilion at the landward end. Surrounding context shows a tropical coastal estuary with low-rise resort development set back from the marsh.",
            18000, 35000, 25000, "tidal-marsh-boardwalk"),
        variant(
            "tidal_marsh_boardwalk_v2", "Reedbed Estuary Boardwalk", "#6B8A4A",
            "Reedbed estuary boardwalk park, roughly 200 by 250 meters of brackish reedbed-and-phragmites estuary with an extensive multi-leg boardwalk network connecting three viewing platforms at different points along the river-edge. A small bird-watching tower at the most remote platform. Tidal creek winding through the reeds. A trailhead pavilion with restrooms and an interpretive exhibit at the landward end. Surrounding context shows a temperate-Atlantic estuary with surrounding wet-meadow farmland.",
            35000, 60000, 45000, "tidal-marsh-boardwalk"),
        variant(
            "tidal_marsh_boardwalk_v3", "Bird-Blind Viewing Circuit", "#4A7C59",
            "Multi-platform bird-blind viewing-circuit marsh park, roughly 300 by 250 meters of large protected wetland-conservation area with a long looping boardwalk circuit connecting five separate timber-clad bird-blind viewing platforms at different vantage points across the marsh. A central wooden-tower observation deck rises above. Multiple species-specific interpretive panels. A larger interpretive-centre building at the trailhead with parking. Surrounding context shows a regional-park-quality wetland conservation reserve.",
            65000, 100000, 80000, "tidal-marsh-boardwalk"),
    ],
    render_overlay="Replace the colored zone with a photorealistic tidal marsh boardwalk park. Stretch of intertidal habitat — salt marsh, cordgrass, mangrove, or mudflat. Network of elevated timber-and-steel boardwalks raised above the marsh. Polygonal viewing platforms with bench seating and bird-blinds at intervals. Small gravel trailhead pavilion and parking lot. Tidal channels winding through the marsh. Native marsh vegetation forming dense low cover. Keep surrounding satellite map context exactly as-is. Oblique aerial view, soft late-afternoon light, photorealistic, 8k.",
    render_roof="Replace the colored zone viewed from directly above with a tidal marsh park. Green-and-brown marsh expanse threaded by a thin pale boardwalk network. Polygonal viewing-platform shapes. Tidal channels visible as winding serpentine lines through the marsh. Trailhead pavilion at the landward edge. Keep surrounding context exactly as-is.",
    render_negative="cartoon, illustration, sketch, low quality, blurry, text, watermark, unrealistic colors, urban plaza inside marsh, large buildings on marsh surface, casual park lawn",
    suggested_w=180, suggested_d=200, min_w=60, max_w=350, min_d=70, max_d=350,
    min_area=6000, max_area=100000, suggested_area=30000,
    aspect_ratio="1:1.1", shape="irregular",
)


# ---------------------------------------------------------------------------
# 6) Lake Edge Plaza
# ---------------------------------------------------------------------------
lake_edge_plaza = archetype(
    id="lake_edge_plaza",
    slug="lake-edge-plaza",
    title="Lake Edge Plaza",
    description="A hard-paved urban plaza meeting a flat lake edge — formal stone esplanade or terrace with a continuous lake-side parapet, lining the urban edge of a major lake or large reservoir",
    tags=["waterfront", "lakefront", "plaza", "esplanade", "hardscape", "urban-edge"],
    space_type="plaza",
    landscape_character=(
        "A lake-edge urban plaza seen from drone altitude. The site is a long, hard-paved "
        "esplanade or terrace running along the urban edge of a flat clear lake — typically "
        "10-30 meters wide and stretching several hundred meters along the shore. The plaza "
        "floor is formal stone or precast concrete pavers in a directional pattern parallel "
        "to the water edge. A continuous low parapet wall, balustrade, or perimeter stone "
        "bench runs along the water edge. Paired allées of mature plane trees, palms, or "
        "lindens line the landward side of the esplanade in regular planting tree-pits. "
        "Periodic stone-paved overlooks with bench seating project slightly into the water. "
        "Lamp posts, decorative bollards, small fountains, or sculpture punctuate the "
        "promenade. The landside opens onto a major arterial street or city blocks. From "
        "above the plaza reads as a long pale-coloured stone strip running the lake's edge "
        "with paired tree-allée bands, periodic overlook bumpouts, and the urban city block "
        "fabric visible on the landward side."
    ),
    paving="Formal stone or precast concrete pavers in a directional pattern parallel to the water edge",
    planting="Paired allées of mature trees in regular tree-pits along the landward side",
    seating="Continuous stone perimeter bench at the water edge, paired benches along the allées, overlook benches",
    water="The lake itself bordering the entire promenade edge",
    openness="Strongly open to the lake on one long side; landside enclosed by city block frontage",
    prompt_subject="Aerial view of a long lake-edge urban plaza esplanade with stone paving, parapet wall, paired tree allées, and overlook bumpouts",
    prompt_details=[
        "Long hard-paved esplanade running along the urban edge of a flat clear lake",
        "Formal stone or precast concrete pavers in a directional pattern parallel to the water",
        "Continuous low parapet wall or stone perimeter bench at the water edge",
        "Paired allées of mature trees in regular tree-pits along the landward side",
        "Periodic stone-paved overlook bumpouts projecting slightly into the water",
        "Surrounding city blocks or major arterial street on the landward side",
    ],
    prompt_negative=[
        "No grass lawn dominating the floor",
        "No suburban beach with sand",
        "No marina with boats and docks",
        "No text overlays",
    ],
    property_presets={
        "tree_density_level": "medium",
        "tree_density": 0.35,
        "has_paths": True,
        "has_benches": True,
        "shade_strategy": "paired_landside_allees",
    },
    variants_data=[
        variant(
            "lake_edge_plaza_v0", "Como-Style Stone Terrace", "#A0826D",
            "Como-style stone-terrace lake-edge plaza, roughly 25 by 80 meters of warm-stone-paver terrace stepping in two shallow tiers down to the lake edge. A continuous wrought-iron-railed balustrade along the water side. A single row of clipped plane trees in stone tree-pits along the landward side. Two small classical-style stone overlook bumpouts. Surrounding context shows a Northern-Italian lakefront town with pastel-coloured villas climbing the hillside behind.",
            1500, 4000, 2500, "lake-edge-plaza"),
        variant(
            "lake_edge_plaza_v1", "Geneva Quayside Esplanade", "#8B7355",
            "Geneva-style quayside esplanade, roughly 30 by 200 meters of pale grey-stone-paver promenade running along the urban-Geneva-style lake edge. A continuous low stone parapet wall along the water. Two paired rows of clipped horse-chestnut trees. Five wrought-iron-and-glass-canopy lakeside cafés along the landward side. A periodic small classical fountain on the axis. Surrounding context shows a 19th-century European limestone city with a major boulevard along the landside.",
            5000, 12000, 8500, "lake-edge-plaza"),
        variant(
            "lake_edge_plaza_v2", "Modern Timber Lakefront Deck", "#6B4423",
            "Modern timber-and-stone lakefront deck plaza, roughly 35 by 250 meters of contemporary mixed-stone-and-timber-deck waterfront promenade with a low cor-ten-steel railing along the water and a row of black-steel planters with ornamental grasses on the landside. Three large overlook bumpouts with integrated bench-and-lounger furniture. A small kiosk pavilion. Surrounding context shows a contemporary mixed-use lakefront district with mid-rise residential and office towers.",
            10000, 18000, 14000, "lake-edge-plaza"),
        variant(
            "lake_edge_plaza_v3", "Chicago-Lakefront Hard Plaza", "#708090",
            "Chicago-Lakefront-style massive hard plaza esplanade, roughly 50 by 500 meters of broad continuous Indiana-limestone esplanade with paired allées of plane trees, multiple monumental cast-iron Beaux-Arts lamp standards, periodic stone overlook bumpouts with bench seating, and a continuous stone perimeter rail at the lake edge. A grand civic museum complex visible at one end. Multiple grand stone staircases connect to the lake-level. Surrounding context shows a major US-city with a strong lakefront skyline of mid-and-high-rise towers.",
            22000, 60000, 40000, "lake-edge-plaza"),
    ],
    render_overlay="Replace the colored zone with a photorealistic lake-edge urban plaza esplanade. Long hard-paved promenade running along the urban edge of a flat clear lake. Formal stone or precast concrete pavers in a directional pattern parallel to the water. Continuous low parapet wall or stone perimeter bench at the water edge. Paired allées of mature trees in regular tree-pits on the landward side. Periodic stone-paved overlook bumpouts. Surrounding city blocks. Keep surrounding satellite map context exactly as-is. Oblique aerial view, late-afternoon golden hour, sharp shadows, photorealistic, 8k.",
    render_roof="Replace the colored zone viewed from directly above with a lake-edge plaza esplanade. Long pale-coloured stone strip running the lake's edge. Paired tree-allée bands along the landward side. Periodic overlook bumpout shapes projecting into the water. Urban city-block fabric on the landward side. Keep surrounding context exactly as-is.",
    render_negative="cartoon, illustration, sketch, low quality, blurry, text, watermark, unrealistic colors, grass lawn floor, suburban sandy beach, marina with docks",
    suggested_w=40, suggested_d=200, min_w=15, max_w=80, min_d=50, max_d=600,
    min_area=1500, max_area=60000, suggested_area=10000,
    aspect_ratio="1:5", shape="linear",
)


# ---------------------------------------------------------------------------
# Emit
# ---------------------------------------------------------------------------
all_archetypes = [marina, working_pier_conversion, floating_park,
                  lighthouse_point_park, tidal_marsh_boardwalk, lake_edge_plaza]


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

    out_path = Path(__file__).parent / "_waterfront_snippet.json"
    out_path.write_text(snippet, encoding="utf-8")
    print(f"OK: wrote {len(snippet)} chars to {out_path}")
    print(f"Validates as JSON array of {len(all_archetypes)} entries")
    return 0


if __name__ == "__main__":
    sys.exit(main())
