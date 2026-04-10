#!/usr/bin/env python3
"""
Create Canadian District Kit archetypes for City Prompt.

Generates building, street, and park archetype entries for 5 Canadian city kits:
Montreal, Vancouver, Toronto, Calgary, Halifax.

Includes transit-specific archetypes (Metro, SkyTrain, Streetcar, CTrain, Ferry).

Usage:
    python scripts/create_canadian_kits.py --dry-run
    python scripts/create_canadian_kits.py
"""

import json
import sys
from pathlib import Path

DRY_RUN = "--dry-run" in sys.argv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
BUILDING_FILE = PROJECT_ROOT / "frontend/src/data/buildingArchetypes.json"
STREET_FILE = PROJECT_ROOT / "frontend/src/data/streetPathArchetypes.json"
PARK_FILE = PROJECT_ROOT / "frontend/src/data/openSpaceArchetypes.json"

BASE_NEGATIVE = "cartoon, illustration, sketch, low quality, blurry, text, watermark, neon, unrealistic colors"

# Import helpers from create_district_kits
sys.path.insert(0, str(Path(__file__).resolve().parent))
from create_district_kits import make_building, make_variants, make_street, make_park


# ═══════════════════════════════════════════════════
# MONTREAL KIT (7 buildings + 3 streets + 2 parks)
# ═══════════════════════════════════════════════════

MONTREAL_BUILDINGS = [
    make_building(
        "montreal_triplex", "Montreal Plateau Triplex", "montreal_plateau",
        "Iconic Montreal triplex with exterior spiral staircase, grey limestone facade, wrought-iron railings, and flat roof",
        "#8B8682", 3, 3, 180, "residential_triplex",
        ["montreal", "triplex", "plateau", "exterior_staircase", "limestone", "spiral"],
        "rough-cut grey limestone (local quarry stone), sometimes clay brick", "wrought-iron exterior staircase with ornamental railings, fleur-de-lis or heart motifs", "bright painted doors (red, blue, green, yellow), tin roofing",
        "ground-floor unit at grade or half-sunk, separate entrance, small iron-fenced yard", "second and third floor accessed via exterior spiral or L-shaped wrought-iron staircase projecting over sidewalk, each unit with own entrance and small balcony landing", "flat roof with low parapet, tin or asphalt", "grey limestone body, black wrought iron, bright painted doors and window trim, silver-grey tin roof",
        "flat with low parapet", "tin (tole) or asphalt", "chimney stacks, clotheslines strung between buildings", "flat grey rooftops in continuous rows, rear balconies and clotheslines visible",
        ["rough-cut grey limestone", "wrought-iron staircase railings", "tin roofing", "painted wood doors and trim"],
        "Replace the colored building block with a photorealistic Montreal Plateau triplex. Keep the exact same building footprint and height. Grey limestone facade with exterior wrought-iron spiral staircase projecting over the sidewalk. Ornamental railings with fleur-de-lis motifs. Bright painted doors (red or blue). Flat tin roof. Three units stacked, each with own entrance. 3 storey. Maintain the surrounding satellite map context exactly as-is. Oblique aerial view, sunny day, sharp shadows, photorealistic, 8k",
        "Replace the colored block viewed from above with a flat tin roof. Rear balconies with clotheslines visible. Keep surrounding context exactly as-is.",
        f"{BASE_NEGATIVE}, modern glass, suburban",
        make_variants("montreal_triplex", [
            ("spiral_classic", "Classic Spiral Staircase", "Iconic spiral wrought-iron staircase, grey limestone, red door"),
            ("brick_straight", "Brick with Straight Stair", "Clay brick facade, straight L-shaped staircase, wider lot"),
            ("colorful_doors", "Colorful Doors", "Multiple bright painted doors visible, each unit a different color"),
            ("winter_scene", "Winter Character", "Snow-covered stairs and railings, icicles, warm interior glow"),
        ]),
    ),
    make_building(
        "montreal_duplex", "Montreal Duplex", "montreal_plateau",
        "Two-unit Montreal duplex with single exterior staircase, grey limestone or brick, small front yard with iron fence",
        "#8B8682", 2, 2, 150, "residential_duplex",
        ["montreal", "duplex", "plateau", "exterior_staircase", "limestone"],
        "grey limestone or clay brick, party wall construction", "wrought-iron exterior staircase to upper unit", "iron fence at front yard, painted wood trim",
        "ground-floor unit at grade with separate entrance, small front yard behind low iron fence", "upper unit accessed via exterior wrought-iron staircase, balcony landing at entrance", "flat roof with low parapet", "grey stone or brick, black iron, painted trim, slightly wider than triplex",
        "flat with low parapet", "tin or asphalt", "chimney, rear balcony", "flat roof, slightly wider footprint than triplex",
        ["grey limestone or clay brick", "wrought-iron staircase", "tin roofing", "iron fence"],
        "Replace the colored building block with a photorealistic Montreal duplex. Keep the exact same building footprint and height. Grey limestone or brick facade with exterior wrought-iron staircase to upper unit. Small front yard with iron fence. Flat tin roof. 2 storey. Maintain the surrounding satellite map context exactly as-is. Oblique aerial view, sunny day, sharp shadows, photorealistic, 8k",
        "Replace the colored block viewed from above with a flat tin roof. Rear balcony visible. Keep surrounding context exactly as-is.",
        f"{BASE_NEGATIVE}, modern glass, suburban",
        make_variants("montreal_duplex", [
            ("stone_classic", "Grey Stone Classic", "Classic grey limestone, simple iron stair, small front yard"),
            ("brick_ornate", "Ornate Brick", "Decorative brickwork, more elaborate iron railings"),
            ("corner_lot", "Corner Lot", "Wider exposure, windows on two sides, corner entrance"),
            ("garden_front", "Garden Front", "Lush front garden behind iron fence, flowering vines on stair"),
        ]),
    ),
    make_building(
        "montreal_limestone_commercial", "Old Montreal Limestone Commercial", "montreal_old",
        "Grey limestone heritage building in Old Montreal with Second Empire mansard roof, stone window surrounds, and heavy facade",
        "#6B6B6B", 3, 5, 350, "commercial_heritage",
        ["montreal", "old_montreal", "limestone", "second_empire", "mansard", "heritage"],
        "rough-cut grey limestone from local quarries, heavy masonry", "stone window surrounds with carved lintels, stone quoins at corners", "Second Empire mansard roof with dormers (on civic buildings), slate or tin",
        "stone-framed entrance, heavy timber doors, commercial ground floor with tall windows", "tall narrow windows with stone lintels, thick limestone walls, austere and heavy character", "Second Empire mansard roof with dormer windows, or flat roof with stone cornice", "grey limestone throughout, dark slate mansard, heavy austere character",
        "Second Empire mansard with slate, or flat with stone parapet", "dark slate on mansard", "dormer windows in mansard, chimney stacks, copper flashings with green patina", "dark slate mansard visible from above, or flat grey limestone parapet",
        ["rough-cut grey limestone", "dark slate roofing", "heavy stone lintels", "copper flashings"],
        "Replace the colored building block with a photorealistic Old Montreal grey limestone commercial building. Keep the exact same building footprint and height. Heavy grey limestone facade with stone window surrounds and quoins. Second Empire mansard roof with dormers and dark slate. Cobblestone street visible at base. 3-5 storey. Maintain the surrounding satellite map context exactly as-is. Oblique aerial view, sunny day, sharp shadows, photorealistic, 8k",
        "Replace the colored block viewed from above with a dark slate mansard roof with dormer windows. Heavy grey stone parapet. Keep surrounding context exactly as-is.",
        f"{BASE_NEGATIVE}, modern glass, suburban, stucco",
        make_variants("montreal_limestone_commercial", [
            ("bonsecours", "Bonsecours Market Style", "Grand neoclassical with dome, longest public market building"),
            ("warehouse", "Converted Warehouse", "Heavy limestone walls, large industrial windows, now loft condos"),
            ("second_empire", "Full Second Empire", "Elaborate mansard with ornate dormers, turrets at corners"),
            ("austere_commercial", "Austere Commercial", "Flat-roofed, minimal ornament, warehouse-like simplicity"),
        ]),
    ),
    make_building(
        "montreal_depanneur", "Montreal Depanneur", "montreal_plateau",
        "Corner convenience store (depanneur) with painted signage, recessed corner entrance, and residential units above",
        "#8B8682", 2, 3, 120, "commercial_retail",
        ["montreal", "depanneur", "corner_store", "plateau", "signage"],
        "same grey limestone or brick as surrounding residential fabric", "painted or neon signage projecting from facade", "recessed corner entrance or angled corner door, awning over storefront",
        "ground-floor retail with large display windows facing both streets, recessed corner entrance, projecting painted signage, awning", "residential units above accessed by separate exterior staircase (same as triplex)", "flat roof, same as surrounding residential", "grey stone or brick matching neighbourhood, colorful painted signage, lit interior",
        "flat with low parapet", "tin or asphalt", "same as surrounding residential", "flat roof, reads as part of the residential triplex fabric with commercial ground floor",
        ["grey limestone or brick", "painted signage", "plate-glass shopfront", "tin roofing"],
        "Replace the colored building block with a photorealistic Montreal depanneur (corner store). Keep the exact same building footprint and height. Corner building with ground-floor convenience store, large windows, painted signage, awning. Residential units above with exterior staircase. Grey limestone or brick matching Plateau neighbourhood. 2-3 storey. Maintain the surrounding satellite map context exactly as-is. Oblique aerial view, sunny day, sharp shadows, photorealistic, 8k",
        "Replace the colored block viewed from above with a flat roof matching surrounding triplexes. Keep surrounding context exactly as-is.",
        f"{BASE_NEGATIVE}, modern glass, suburban, chain store",
        make_variants("montreal_depanneur", [
            ("classic_plateau", "Classic Plateau Corner", "Grey stone, hand-painted sign, red awning, well-worn character"),
            ("neon_sign", "Vintage Neon", "Retro neon signage, 1960s character, lit at night"),
            ("mile_end", "Mile End Style", "Brick building, more eclectic signage, hipster neighbourhood"),
            ("winter_warm", "Winter Evening", "Warm interior glow, snow outside, inviting corner presence"),
        ]),
    ),
    make_building(
        "montreal_warehouse_loft", "Old Montreal Warehouse Loft", "montreal_old",
        "Converted grey limestone or brick warehouse with heavy timber interior, loading doors, and loft condominiums",
        "#6B6B6B", 4, 6, 400, "residential_loft",
        ["montreal", "old_montreal", "warehouse", "loft", "converted", "timber"],
        "grey limestone or red brick, heavy masonry walls", "large industrial multi-pane windows, cast-iron storefront elements", "loading doors on upper floors, heavy timber beams visible inside, cast-iron columns",
        "ground-floor storefronts with cast-iron columns, restaurants or galleries", "large industrial windows (multi-pane steel sash), loading doors converted to windows on upper floors, heavy masonry walls", "flat roof with stone or brick parapet", "grey limestone or red brick, black iron, large windows revealing timber and brick interiors",
        "flat with parapet", "membrane or tar", "mechanical equipment, rooftop terraces on conversions", "flat roof, large rectangular footprint, loading dock area visible",
        ["grey limestone or red brick", "heavy timber beams", "cast-iron columns", "steel-sash industrial windows"],
        "Replace the colored building block with a photorealistic Old Montreal converted warehouse loft. Keep the exact same building footprint and height. Heavy grey limestone or brick walls with large industrial multi-pane windows. Cast-iron storefront at ground level. Loading doors converted to windows on upper floors. Heavy timber interior visible. 4-6 storey. Maintain the surrounding satellite map context exactly as-is. Oblique aerial view, sunny day, sharp shadows, photorealistic, 8k",
        "Replace the colored block viewed from above with a flat roof. Large rectangular warehouse footprint. Keep surrounding context exactly as-is.",
        f"{BASE_NEGATIVE}, modern glass curtain wall, suburban",
        make_variants("montreal_warehouse_loft", [
            ("limestone_grand", "Grey Limestone Grand", "Massive grey stone walls, arched windows, former import warehouse"),
            ("brick_industrial", "Red Brick Industrial", "Red brick with stone lintels, simpler character, former factory"),
            ("gallery_ground", "Gallery Ground Floor", "Art gallery at street level, contemporary art visible through large windows"),
            ("penthouse_addition", "Modern Penthouse", "Glass and steel penthouse addition on heritage base, rooftop terrace"),
        ]),
    ),
    make_building(
        "montreal_mile_end_triplex", "Mile End Cultural Triplex", "montreal_mile_end",
        "Mile End neighbourhood triplex with buff brick, Portuguese ceramic tiles on facade, and cultural markers",
        "#C4A882", 3, 3, 180, "residential_triplex",
        ["montreal", "mile_end", "triplex", "portuguese", "cultural", "brick"],
        "clay brick, often buff or yellow rather than the Plateau's grey stone", "Portuguese-influenced ceramic tile panels depicting Catholic saints", "wrought-iron exterior staircase, same form as Plateau but with cultural overlays",
        "ground-floor unit, sometimes with small garden featuring Portuguese ceramic decoration", "buff brick facade with ceramic tile panels, exterior staircase, well-maintained character", "flat roof with low parapet", "buff or yellow brick, colorful ceramic tiles, iron railings, maintained gardens",
        "flat with low parapet", "tin or asphalt", "same as standard triplex", "flat roof, reads as triplex with distinctive brick colour",
        ["buff or yellow clay brick", "Portuguese ceramic tiles", "wrought-iron staircase", "tin roofing"],
        "Replace the colored building block with a photorealistic Mile End cultural triplex. Keep the exact same building footprint and height. Buff or yellow brick facade with Portuguese ceramic tile panels on facade. Exterior wrought-iron staircase. Well-maintained front garden. 3 storey. Maintain the surrounding satellite map context exactly as-is. Oblique aerial view, sunny day, sharp shadows, photorealistic, 8k",
        "Replace the colored block viewed from above with a flat tin roof. Well-maintained rear garden visible. Keep surrounding context exactly as-is.",
        f"{BASE_NEGATIVE}, modern glass, grey limestone",
        make_variants("montreal_mile_end_triplex", [
            ("portuguese", "Portuguese Ceramic", "Prominent ceramic saint tile panel on facade, well-tended garden"),
            ("jewish_heritage", "Jewish Heritage", "Subtle cultural markers, converted duplex synagogue next door"),
            ("artist_studio", "Artist Studio", "Creative signage, studio windows, Mile End bohemian character"),
            ("cafe_ground", "Ground Floor Cafe", "Independent cafe at ground level, neighbourhood gathering spot"),
        ]),
    ),
    make_building(
        "montreal_second_empire", "Montreal Second Empire Civic", "montreal_civic",
        "Grey limestone civic building with Second Empire mansard roof, copper patina, turrets, and classical ornament",
        "#6B6B6B", 4, 5, 500, "institutional_civic",
        ["montreal", "second_empire", "civic", "mansard", "turrets", "copper"],
        "grey limestone facade, dressed smooth ashlar", "stone balustrades, turrets at corners, classical columns and pilasters", "copper or slate mansard roof with green patina, ornate dormers",
        "monumental stone entrance with classical columns, wide steps, inscribed pediment", "classical pilasters and entablatures, tall arched windows, stone balconies", "elaborate Second Empire mansard with turrets, dormers, and copper or slate cladding", "grey limestone, copper-green patina on roof, classical stone ornament",
        "Second Empire mansard with turrets and dormers", "copper with green patina, or dark slate", "turrets at corners, ornate dormers, clock tower on some examples, copper finials", "dramatic mansard roofline with turrets and dormers, copper-green patina visible",
        ["grey limestone ashlar", "copper roofing with green patina", "dark slate", "classical stone ornament"],
        "Replace the colored building block with a photorealistic Montreal Second Empire civic building. Keep the exact same building footprint and height. Grey limestone with classical columns and pilasters. Elaborate mansard roof with turrets, dormers, and copper cladding showing green patina. Monumental stone entrance. 4-5 storey. Maintain the surrounding satellite map context exactly as-is. Oblique aerial view, sunny day, sharp shadows, photorealistic, 8k",
        "Replace the colored block viewed from above with a dramatic mansard roof with copper-green patina, turrets at corners, and ornate dormers. Keep surrounding context exactly as-is.",
        f"{BASE_NEGATIVE}, modern glass, suburban, residential",
        make_variants("montreal_second_empire", [
            ("city_hall", "City Hall Style", "Full Second Empire grandeur, clock tower, stone balconies"),
            ("courthouse", "Courthouse", "More austere classical, Doric columns, blind Justice statue"),
            ("museum", "Museum/Gallery", "Converted to cultural use, exhibition banners on facade"),
            ("church", "Institutional Church", "Ecclesiastical variant, rose window, bell tower instead of civic tower"),
        ]),
    ),
]

MONTREAL_STREETS = [
    make_street(
        "montreal_ruelle", "Montreal Ruelle Verte", "montreal_alley",
        "Montreal green back alley with community gardens, murals, vines, depaved sections, and rear triplex balconies",
        "Narrow back alley (ruelle) running behind Plateau triplex blocks. Originally for deliveries, now 'ruelles vertes' with community gardens, climbing vines on fences, children's play areas, murals, and depaved permeable sections. Bordered by rear fences, sheds, and the backs of triplexes with rear balconies and clotheslines.",
        "Partially depaved with permeable pavers, gravel, or exposed earth. Some asphalt remaining.",
        "Climbing vines on fences, small community garden plots, potted plants, some small trees",
        "Rear of triplex buildings with back balconies, clotheslines, garage structures, and fences",
        "Community garden plots, murals on walls, children's chalk drawings, bicycle parking, compost bins",
        ["montreal", "ruelle", "alley", "green", "community_garden", "mural"],
        "Replace the colored zone with a photorealistic Montreal ruelle verte (green back alley). Narrow alley behind triplexes, community gardens, vines on fences, murals on walls, depaved sections, rear balconies with clotheslines. Maintain satellite context. Oblique aerial view, photorealistic, 8k",
        BASE_NEGATIVE,
        {"width": 4},
    ),
    make_street(
        "montreal_plateau_rue", "Montreal Plateau Residential Rue", "montreal_residential",
        "Plateau residential street with continuous triplex facades, exterior staircases projecting over sidewalks, and bright painted doors",
        "Continuous wall of triplex facades with exterior wrought-iron staircases projecting over the sidewalk. Street trees (silver maples). Bright painted doors in red, blue, green. No front yards — buildings at property line. Parked cars on both sides. Overhead: clotheslines between buildings. The staircases create a rhythmic, sculptural streetwall unique to Montreal.",
        "Asphalt with concrete sidewalks, some cobblestone sections at older crossings",
        "Silver maple street trees at intervals",
        "Continuous triplex facades at property line, exterior staircases projecting over sidewalk, bright painted doors",
        "Wrought-iron staircases as dominant streetwall element, painted doors, clotheslines overhead, fire escapes on side walls",
        ["montreal", "plateau", "rue", "triplex", "staircase", "residential"],
        "Replace the colored zone with a photorealistic Montreal Plateau residential street. Continuous grey limestone triplexes with exterior wrought-iron staircases projecting over sidewalks. Bright painted doors. Street trees. Clotheslines. No front yards. Maintain satellite context. Oblique aerial view, photorealistic, 8k",
        BASE_NEGATIVE,
        {"width": 14},
    ),
    make_street(
        "montreal_boulevard", "Montreal Commercial Boulevard", "montreal_commercial",
        "Montreal commercial boulevard with cafe terrasses, neon signage, and mixed-height buildings along Saint-Laurent or Saint-Denis",
        "Commercial boulevard with ground-floor shops, cafes, and restaurants with sidewalk terrasses. Wider setbacks than residential streets. Neon and painted signage. Mix of 2-4 storey buildings. Cultural corridor feel. Street trees in tree wells. Bike lanes.",
        "Asphalt with wide concrete sidewalks, bike lane markings",
        "Street trees at intervals, seasonal planters on terrasses",
        "Mixed-height commercial buildings (2-4 storey), cafe terrasses, neon and painted signage, cultural venue marquees",
        "Sidewalk cafe terrasses with bistro chairs, neon signs, cultural venue marquees, BIXI bike share stations",
        ["montreal", "boulevard", "commercial", "saint_laurent", "terrasse", "neon"],
        "Replace the colored zone with a photorealistic Montreal commercial boulevard (like Saint-Laurent or Saint-Denis). Cafe terrasses, neon signage, mixed 2-4 storey buildings, cultural venues, bike lanes. Maintain satellite context. Oblique aerial view, photorealistic, 8k",
        BASE_NEGATIVE,
        {"width": 22},
    ),
]

MONTREAL_PARKS = [
    make_park(
        "montreal_mount_royal", "Mount Royal Park", "montreal_landscape", "park",
        "Olmsted-designed naturalistic park on Mount Royal with wooded hillside, Beaver Lake, and stone lookout with city views",
        "Frederick Law Olmsted-designed (1876) naturalistic park on Mount Royal. Wooded hillside with winding carriage paths. Beaver Lake (man-made). Stone lookout (Belvedere) with panoramic city views. The illuminated cross at summit. Granite and limestone retaining walls. Deciduous forest (predominantly maple). Gravel paths. The mountain rises 233m above the city.",
        "Gravel paths and winding carriage roads",
        "Dense deciduous forest, predominantly sugar maple, creating spectacular autumn colour",
        "Stone lookout (Belvedere), wooden benches along paths, Beaver Lake shoreline seating",
        "Beaver Lake, natural springs",
        ["montreal", "mount_royal", "olmsted", "mountain", "lookout", "forest"],
        "Replace the colored zone with a photorealistic Mount Royal Park. Wooded mountainside with winding gravel paths, stone lookout with city panorama, Beaver Lake, dense maple forest, granite retaining walls. Maintain satellite context. Oblique aerial view, photorealistic, 8k",
        BASE_NEGATIVE,
    ),
    make_park(
        "montreal_square", "Montreal Neighbourhood Square", "montreal_civic", "park",
        "Small formal Montreal square with central fountain, iron fence, benches, and mature trees, surrounded by triplexes",
        "Small formal square at a street intersection. Central fountain or monument. Low stone or iron perimeter fence. Benches. Mature deciduous trees. Sometimes a small playground. Surrounded on all sides by triplex facades. Scale is intimate — typically 0.5-1 acre. Provides breathing room in the dense triplex fabric.",
        "Gravel paths in simple geometric layout, stone edging",
        "Mature deciduous trees (maple, elm), seasonal flower beds",
        "Cast-iron or wooden benches, low iron perimeter fence",
        "Central fountain or small monument",
        ["montreal", "square", "fountain", "neighbourhood", "intimate"],
        "Replace the colored zone with a photorealistic Montreal neighbourhood square. Small formal garden with fountain, iron fence, benches, mature trees. Surrounded by triplex facades. Intimate scale. Maintain satellite context. Oblique aerial view, photorealistic, 8k",
        BASE_NEGATIVE,
    ),
]


# ═══════════════════════════════════════════════════
# VANCOUVER KIT (7 buildings + 3 streets + 2 parks)
# ═══════════════════════════════════════════════════

VANCOUVER_BUILDINGS = [
    make_building(
        "vancouver_special", "Vancouver Special", "vancouver_special",
        "Iconic post-war Vancouver house with flat roof, full-width front balcony, stucco facade, and guardian lion statues",
        "#C4A882", 2, 2, 220, "residential_house",
        ["vancouver", "vancouver_special", "flat_roof", "balcony", "stucco", "1970s"],
        "stucco upper facade, brick or stone veneer lower facade", "aluminum balcony railing across full front width", "vestigial coach lamps at upper corners, guardian lion statues at front gate",
        "ground-level front door (no steps), lower floor often converted to suite, brick or stone veneer", "full-width balcony at main floor level with aluminum railing, large living room windows with coach lamps at upper corners", "very shallow-pitched front gable, appearing nearly flat", "white or cream stucco, brick lower level, aluminum railings, wide lot coverage",
        "very shallow front gable, nearly flat", "tar and gravel", "minimal — nearly flat roof with very shallow pitch", "boxy rectangular form spanning nearly full lot width, flat appearance from above",
        ["stucco", "brick veneer", "aluminum railings", "tar and gravel roof"],
        "Replace the colored building block with a photorealistic Vancouver Special house. Keep the exact same building footprint and height. Boxy rectangular form with stucco upper facade and brick veneer lower level. Full-width front balcony with aluminum railing. Very shallow front gable roof. Wide lot coverage. Guardian lion statues at front gate. 2 storey. Maintain the surrounding satellite map context exactly as-is. Oblique aerial view, sunny day, sharp shadows, photorealistic, 8k",
        "Replace the colored block viewed from above with a nearly flat roof spanning most of the lot width. Boxy rectangular footprint. Keep surrounding context exactly as-is.",
        f"{BASE_NEGATIVE}, modern glass tower, heritage Victorian",
        make_variants("vancouver_special", [
            ("classic_white", "Classic White Stucco", "Standard white stucco, brick lower, aluminum railings, coach lamps"),
            ("renovated", "Renovated Modern", "Updated materials, new windows, landscaped, guardian lions removed"),
            ("garden_suite", "With Garden Suite", "Lower level converted to separate suite, separate entrance visible"),
            ("east_van", "East Van Character", "Slightly weathered, mature garden, established neighbourhood feel"),
        ]),
    ),
    make_building(
        "vancouver_laneway", "Vancouver Laneway House", "vancouver_laneway",
        "Small contemporary detached dwelling in rear yard facing the back lane, max 550 sq ft average",
        "#8B7355", 1, 2, 55, "residential_laneway",
        ["vancouver", "laneway_house", "contemporary", "small", "infill", "lane"],
        "wood frame, varies — cedar siding, fiber cement panels, stucco, metal cladding", "contemporary materials, large windows for natural light", "rooftop deck or at-grade patio, side-yard pedestrian path",
        "entrance facing the lane, one parking space, often with garage or carport integrated", "contemporary design, large windows, varied cladding, compact and efficient, often contrasts with older main house", "flat or shallow-pitched, sometimes with rooftop deck", "varied contemporary materials — natural cedar, white stucco, dark metal cladding",
        "flat or shallow-pitched, sometimes rooftop deck", "membrane with deck overlay or green roof", "rooftop deck railing, compact mechanical equipment", "small rectangular footprint in rear of lot, clearly distinct from main house ahead",
        ["cedar siding or fiber cement", "contemporary metal cladding", "large windows", "membrane or green roof"],
        "Replace the colored building block with a photorealistic Vancouver laneway house. Keep the exact same building footprint and height. Small contemporary dwelling facing a back lane. Cedar or modern cladding, large windows, compact form. Rooftop deck. In rear yard behind a main house. 1.5 storey. Maintain the surrounding satellite map context exactly as-is. Oblique aerial view, sunny day, sharp shadows, photorealistic, 8k",
        "Replace the colored block viewed from above with a small flat-roofed structure with rooftop deck in the rear portion of a residential lot. Keep surrounding context exactly as-is.",
        f"{BASE_NEGATIVE}, large building, commercial, heritage",
        make_variants("vancouver_laneway", [
            ("cedar_modern", "Cedar Modern", "Natural cedar siding, clean lines, floor-to-ceiling glass"),
            ("dark_metal", "Dark Metal Clad", "Charcoal metal cladding, minimalist, industrial-contemporary"),
            ("green_roof", "Green Roof", "Living roof with sedum, integrated into garden landscape"),
            ("garage_combo", "Garage Combo", "Combined parking and living, garage door at ground, suite above"),
        ]),
    ),
    make_building(
        "vancouver_gastown", "Gastown Heritage Commercial", "vancouver_gastown",
        "Victorian Italianate red brick building in Gastown with sandstone trim, cast-iron storefronts, and flat roof",
        "#8B4513", 2, 6, 300, "commercial_heritage",
        ["vancouver", "gastown", "heritage", "brick", "victorian", "cast_iron"],
        "red brick with contrasting green sandstone trim", "cast-iron columns at ground-floor storefronts", "decorative brick corbelling, strong cornice lines, flat roofs",
        "cast-iron column storefronts with large display windows, recessed entries", "brick facades with sandstone trim accents, decorative window surrounds, corbelled cornices", "flat roof with decorative parapet, strong cornice line", "warm red brick, green sandstone trim, black cast-iron columns",
        "flat with decorative parapet", "tar or membrane", "skylights, mechanical equipment, occasional rooftop addition", "flat roofs at varying heights creating picturesque roofline along the street",
        ["red brick", "green sandstone trim", "cast-iron columns", "decorative corbelling"],
        "Replace the colored building block with a photorealistic Gastown heritage commercial building. Keep the exact same building footprint and height. Red brick with green sandstone trim. Cast-iron columns at storefront. Decorative corbelling and strong cornice. Victorian Italianate character. 2-6 storey. Maintain the surrounding satellite map context exactly as-is. Oblique aerial view, sunny day, sharp shadows, photorealistic, 8k",
        "Replace the colored block viewed from above with a flat roof at varying heights. Red brick parapet visible. Keep surrounding context exactly as-is.",
        f"{BASE_NEGATIVE}, modern glass, stucco, suburban",
        make_variants("vancouver_gastown", [
            ("steam_clock", "Steam Clock Area", "Near the iconic steam clock, cobblestone street, cast-iron lampposts"),
            ("warehouse", "Converted Warehouse", "Wider bay structure, former wholesale, now lofts and restaurants"),
            ("corner_hotel", "Corner Hotel", "Former saloon/hotel on corner, prominent entrance, upper-floor galleries"),
            ("narrow_lot", "Narrow Lot", "Tall and narrow, single bay, intensely vertical character"),
        ]),
    ),
    make_building(
        "vancouver_craftsman", "Vancouver Craftsman Bungalow", "vancouver_craftsman",
        "Arts and Crafts bungalow with cedar shingle siding, clinker brick porch piers, deep eaves, and exposed rafters",
        "#8B6914", 1, 2, 140, "residential_house",
        ["vancouver", "craftsman", "bungalow", "cedar", "arts_crafts", "kitsilano"],
        "wood frame, cedar shingle or clapboard siding", "clinker brick or stone porch piers with tapered columns", "exposed rafter ends and decorative brackets under deep eaves, mock trusses in gable",
        "integral front porch with tapered columns on brick/stone piers, wide steps", "cedar shingle or clapboard walls, small attic window in gable, asymmetrical design", "front-gabled with low pitch and deep overhanging eaves", "earthy colours — greens, browns, natural wood stains, clinker brick warm tones",
        "front-gabled, low pitch, deep eaves", "composition shingle", "exposed rafter ends visible at eaves, clinker brick chimney", "front-gabled roof with deep overhangs, relatively low profile",
        ["cedar shingle or clapboard", "clinker brick porch piers", "composition shingle roof", "exposed rafter ends"],
        "Replace the colored building block with a photorealistic Vancouver Craftsman bungalow. Keep the exact same building footprint and height. Cedar shingle siding, front porch with clinker brick piers and tapered columns. Front-gabled roof with deep overhanging eaves and exposed rafter ends. Earthy colour palette. 1.5 storey. Maintain the surrounding satellite map context exactly as-is. Oblique aerial view, sunny day, sharp shadows, photorealistic, 8k",
        "Replace the colored block viewed from above with a front-gabled roof with deep overhangs. Low profile. Keep surrounding context exactly as-is.",
        f"{BASE_NEGATIVE}, modern glass, flat roof, urban tower",
        make_variants("vancouver_craftsman", [
            ("kitsilano", "Kitsilano Classic", "Well-maintained, mature garden, typical 5th/6th Avenue character"),
            ("painted_lady", "Painted Lady", "Colourful painted trim, flower boxes, cottage character"),
            ("original", "Original Character", "Less renovated, original windows, aged cedar, heritage charm"),
            ("garden_lush", "Lush Garden", "Overgrown west coast garden, ferns, moss on roof, rainforest character"),
        ]),
    ),
    make_building(
        "vancouver_tower_podium", "Vancouverism Tower-Podium", "vancouver_modern",
        "Slender glass point tower on street-activating podium with retail at grade — the defining Vancouver typology",
        "#4A90D9", 30, 40, 600, "residential_condo",
        ["vancouver", "vancouverism", "tower", "podium", "glass", "condo"],
        "glass curtain wall (tower), clear or lightly tinted", "concrete and masonry podium with ground-floor retail glazing", "slender tower floor plate (~605 sqm), 24.4m minimum tower separation",
        "street-activating podium with retail storefronts, townhouse-style units at grade, landscaped forecourt", "slender glass tower rising from wider podium, balconies on most floors, view corridors preserved through tower placement", "flat tower roof with mechanical penthouse, podium may have green roof or terrace", "clear glass reflecting sky and mountains, concrete podium in neutral tones",
        "flat with mechanical penthouse", "membrane with mechanical equipment", "mechanical penthouse, crane during construction, window-washing equipment", "slender tower footprint on wider podium base, separated from adjacent towers by 24.4m+",
        ["glass curtain wall", "concrete podium", "retail glazing at grade", "balcony railings"],
        "Replace the colored building block with a photorealistic Vancouverism tower-and-podium condo. Keep the exact same building footprint and height. Slender glass tower rising from a 4-7 storey podium with retail at grade and townhouses. Clear glass reflecting mountains and sky. 30-40 storey tower. Maintain the surrounding satellite map context exactly as-is. Oblique aerial view, sunny day, sharp shadows, photorealistic, 8k",
        "Replace the colored block viewed from above with a slender tower top and wider podium base. Keep surrounding context exactly as-is.",
        f"{BASE_NEGATIVE}, heritage, brick, low-rise suburban",
        make_variants("vancouver_tower_podium", [
            ("coal_harbour", "Coal Harbour", "Waterfront location, marina views, premium glass, sculptural form"),
            ("yaletown", "Yaletown", "Converted warehouse podium, heritage brick base, modern tower above"),
            ("metrotown", "Suburban Town Centre", "Transit-oriented, multiple towers on shared podium, bus exchange"),
            ("cambie_corridor", "Cambie Corridor", "Mid-scale (20-25 storey), along Canada Line, neighbourhood retail"),
        ]),
    ),
    make_building(
        "vancouver_skytrain_station", "SkyTrain Elevated Station", "vancouver_transit",
        "Automated SkyTrain station on elevated concrete guideway with glass-walled enclosure and mountain backdrop",
        "#4A90D9", 2, 3, 400, "transit_station",
        ["vancouver", "skytrain", "station", "elevated", "guideway", "transit"],
        "precast/prestressed concrete guideway beams (trapezoidal cross-section)", "glass and steel station enclosure, high transparency", "elevated concrete columns at regular intervals, driverless trains visible",
        "ground-level entrance with elevators, escalators, bus exchange area, fare gates", "glass-walled elevated station platform, concrete guideway extending in both directions, driverless trains", "steel and glass roof canopy over platform", "light grey concrete guideway, transparent glass station walls, steel structure",
        "steel and glass canopy", "glass panels in steel frame", "guideway extending from station in both directions", "elevated concrete ribbon with glass-enclosed station, guideway visible running through neighbourhood",
        ["precast concrete guideway", "glass curtain wall station", "steel canopy structure", "concrete columns"],
        "Replace the colored building block with a photorealistic Vancouver SkyTrain elevated station. Keep the exact same building footprint. Glass-walled station on elevated concrete guideway. Concrete columns supporting the guideway. Driverless train visible. Bus exchange at ground level. Mountain backdrop. Maintain the surrounding satellite map context exactly as-is. Oblique aerial view, sunny day, sharp shadows, photorealistic, 8k",
        "Replace the colored block viewed from above with an elevated concrete guideway with glass-enclosed station platform. Guideway extending in both directions. Keep surrounding context exactly as-is.",
        f"{BASE_NEGATIVE}, heritage, residential, low-rise",
        make_variants("vancouver_skytrain_station", [
            ("expo_line", "Expo Line", "Original 1985 design, simpler structure, guideway through suburbs"),
            ("canada_line", "Canada Line", "Modern underground/elevated hybrid, sleeker design"),
            ("commercial_broadway", "Major Interchange", "Large station with multiple platforms, bus exchange, dense surroundings"),
            ("suburban_terminus", "Suburban Terminus", "End-of-line station with park-and-ride, surrounded by lower density"),
        ]),
    ),
    make_building(
        "vancouver_west_end_tower", "West End Mid-Century Tower", "vancouver_midcentury",
        "1960s modernist apartment tower with ceramic tile facade, Juliet balconies, and breeze block screens",
        "#607D8B", 8, 20, 350, "residential_apartment",
        ["vancouver", "west_end", "midcentury", "tower", "ceramic", "modernist"],
        "reinforced concrete, pre-cast concrete panels, ceramic tile facades", "narrow Juliet-style balconies, breeze block screens on some facades", "flat roof, minimal ornamentation, modernist clean lines",
        "simple entrance lobby, sometimes with mid-century canopy, landscaped grounds", "ceramic tile or precast concrete facades, narrow Juliet balconies, some breeze block screens, flat roof", "flat roof, clean modernist top", "warm ceramic tile tones or cool concrete grey, set among mature trees",
        "flat", "membrane", "minimal mechanical equipment, clean modernist profile", "flat-roofed rectangular tower set back from street in landscaped grounds",
        ["ceramic tile facade", "precast concrete panels", "breeze block screens", "reinforced concrete"],
        "Replace the colored building block with a photorealistic West End mid-century apartment tower. Keep the exact same building footprint and height. 1960s modernist concrete with ceramic tile facade. Narrow Juliet balconies. Clean lines. Set in landscaped grounds with mature trees. 8-20 storey. Maintain the surrounding satellite map context exactly as-is. Oblique aerial view, sunny day, sharp shadows, photorealistic, 8k",
        "Replace the colored block viewed from above with a flat-roofed rectangular tower in landscaped grounds. Keep surrounding context exactly as-is.",
        f"{BASE_NEGATIVE}, heritage, ornate, glass curtain wall",
        make_variants("vancouver_west_end_tower", [
            ("beach_avenue", "Beach Avenue", "Ocean-facing, balconies with water views, 1960s California modern"),
            ("ceramic_tile", "Ceramic Tile Facade", "Distinctive warm ceramic tile treatment, mid-century character"),
            ("breeze_block", "Breeze Block Screen", "Decorative concrete block screens on facade, tropical modernist feel"),
            ("garden_tower", "Garden Tower", "Surrounded by lush West End tree canopy, almost hidden in greenery"),
        ]),
    ),
]

VANCOUVER_STREETS = [
    make_street(
        "vancouver_back_lane", "Vancouver Back Lane", "vancouver_lane",
        "Vancouver back lane with laneway houses, garages, power poles, and shared surface — no sidewalks",
        "Utilitarian lane behind single-family lots. Garbage/recycling pickup. Garage doors and parking pads. Now increasingly populated with laneway houses — small contemporary structures facing the lane. Mix of old garages and new architecture. No sidewalks; shared surface. Power poles and overhead wires.",
        "Asphalt or gravel, no curbs, no sidewalks, shared surface",
        "Minimal — some trees in adjacent yards overhang the lane",
        "Mix of garage structures, fence backs, and new laneway houses",
        "Power poles with overhead wires, garbage/recycling bins, parking pads, occasional laneway house entrance",
        ["vancouver", "lane", "laneway_house", "utilitarian", "back_lane"],
        "Replace the colored zone with a photorealistic Vancouver back lane. Utilitarian lane with mix of old garages and new contemporary laneway houses. Power poles, overhead wires, garbage bins, parking pads. No sidewalks. Maintain satellite context. Oblique aerial view, photorealistic, 8k",
        BASE_NEGATIVE,
        {"width": 6},
    ),
    make_street(
        "vancouver_residential_street", "Vancouver Cherry Blossom Street", "vancouver_residential",
        "Vancouver residential street with cherry trees, Craftsman bungalows or Vancouver Specials, grassy verge, and mountain views",
        "Boulevard-style residential street with grassy verge and street trees — often cherry trees famous for spring blossoms. Craftsman bungalows or Vancouver Specials set back with front gardens. Low hedges. Mountain and ocean views on north-south streets. Quiet, leafy, West Coast suburban character.",
        "Asphalt with concrete sidewalks separated by grassy boulevard strip",
        "Cherry trees (spectacular spring blossoms), or mature deciduous trees creating canopy",
        "Craftsman bungalows or Vancouver Specials set back with front gardens, low hedges",
        "Grassy boulevard between sidewalk and road, low front hedges, mountain views at cross streets",
        ["vancouver", "residential", "cherry_trees", "craftsman", "mountain_views"],
        "Replace the colored zone with a photorealistic Vancouver residential street. Cherry trees in bloom (or mature deciduous trees), grassy boulevard, Craftsman bungalows set back with gardens, mountain views. Leafy West Coast character. Maintain satellite context. Oblique aerial view, photorealistic, 8k",
        BASE_NEGATIVE,
        {"width": 16},
    ),
    make_street(
        "vancouver_skytrain_corridor", "SkyTrain Elevated Corridor", "vancouver_transit",
        "Elevated SkyTrain concrete guideway running through a neighbourhood, concrete columns, driverless trains overhead",
        "Elevated concrete guideway running above street level through suburban neighbourhoods. Concrete columns at regular intervals supporting the trapezoidal guideway beam. Driverless trains visible passing overhead. Street below continues with normal traffic. The guideway is a dominant visual element — like a highway for rail.",
        "Standard asphalt street below, concrete guideway overhead at ~2-3 storey height",
        "Street trees where space allows between columns",
        "Normal residential or commercial buildings on both sides, guideway running overhead between them",
        "Concrete guideway columns, station visible in distance, overhead power collection rail",
        ["vancouver", "skytrain", "guideway", "elevated", "corridor", "transit"],
        "Replace the colored zone with a photorealistic SkyTrain elevated corridor. Concrete guideway running above street level on concrete columns. Driverless train visible. Normal street and buildings below. Mountain backdrop. Maintain satellite context. Oblique aerial view, photorealistic, 8k",
        BASE_NEGATIVE,
        {"width": 20},
    ),
]

VANCOUVER_PARKS = [
    make_park(
        "vancouver_seawall", "Vancouver Seawall Promenade", "vancouver_waterfront", "park",
        "Continuous waterfront seawall path with ocean on one side, forest or city on the other, and mountain views across the inlet",
        "Continuous paved waterfront promenade. Ocean and harbour on one side, forest (Stanley Park) or urban development on the other. Mountain views across Burrard Inlet and English Bay. Separated cycling and walking lanes. Benches at viewpoints. Public art. Drift logs on adjacent beaches.",
        "Paved concrete path, separated walking and cycling lanes",
        "Adjacent forest (Stanley Park sections) or urban landscaping, drift logs on beaches",
        "Benches at viewpoints, low cable or concrete railing at water's edge",
        "Ocean water at path's edge, tidal shoreline, harbour activity",
        ["vancouver", "seawall", "waterfront", "promenade", "mountain_views", "ocean"],
        "Replace the colored zone with a photorealistic Vancouver seawall promenade. Continuous waterfront path with ocean on one side and forest or city on the other. Mountain views across the water. Separated walk/bike lanes. Public art. Maintain satellite context. Oblique aerial view, photorealistic, 8k",
        BASE_NEGATIVE,
    ),
    make_park(
        "vancouver_beach_park", "Vancouver Beach Park", "vancouver_waterfront", "park",
        "West Coast beach park with sandy beach, drift logs, grassy slope, outdoor pool, and mountain/ocean views",
        "Sandy beach with drift log barriers. Grassy slope behind beach. Concrete seawall path along edge. Mountain and ocean views. Outdoor pool (Kits Pool style). Volleyball courts. West Coast casual atmosphere — logs, sand, grass, water, mountains.",
        "Concrete seawall path, sand beach, grassy slope",
        "Beach grasses, mature deciduous trees on slope, drift logs as natural barriers",
        "Drift logs as informal seating, concrete benches along seawall, lifeguard station",
        "Ocean water, tidal zone, sometimes outdoor swimming pool",
        ["vancouver", "beach", "drift_logs", "ocean", "mountain_views", "kits_beach"],
        "Replace the colored zone with a photorealistic Vancouver beach park. Sandy beach with drift logs, grassy slope, seawall path, mountain views across the water. Outdoor pool. West Coast casual character. Maintain satellite context. Oblique aerial view, photorealistic, 8k",
        BASE_NEGATIVE,
    ),
]


# ═══════════════════════════════════════════════════
# TORONTO KIT (7 buildings + 3 streets + 2 parks)
# ═══════════════════════════════════════════════════

TORONTO_BUILDINGS = [
    make_building(
        "toronto_bay_and_gable", "Toronto Bay-and-Gable House", "toronto_victorian",
        "Toronto's signature Victorian house with large bay window covering half the facade, steep decorative gable, red brick, and stained glass",
        "#B03A2E", 2, 3, 150, "residential_townhouse",
        ["toronto", "bay_and_gable", "victorian", "red_brick", "stained_glass", "cabbagetown"],
        "red or white (buff) brick facade (often brick front only, clapboard sides to save cost)", "polychromatic brickwork around windows and gables, carved gable boards (gingerbread bargeboards)", "stained glass transoms over front door, Italianate brackets",
        "small front yard with low iron fence, tiled entrance path, front porch or recessed entry with stained glass fanlight", "large bay window covering more than half the front facade, steep decorative gable above bay, polychromatic brickwork, 10-11 ft ceiling heights", "steep gable with decorative carved bargeboards (gingerbread), slate or shingle roof", "warm red brick (Don Valley brick), cream stone lintels, stained glass colours, dark painted timber porch",
        "steep gable with decorative ridge", "slate or asphalt shingle", "ornate chimney pots in groups, decorative ridge tiles, finial at gable peak", "row of steep gables with bay window projections visible, continuous red brick streetwall",
        ["red Don Valley brick", "carved wooden bargeboards", "stained glass transoms", "slate roofing"],
        "Replace the colored building block with a photorealistic Toronto bay-and-gable house. Keep the exact same building footprint and height. Red brick with large bay window covering half the facade. Steep decorative gable with carved bargeboards above. Polychromatic brickwork. Stained glass fanlight over front door. Small front yard with iron fence. 2.5-3 storey. Maintain the surrounding satellite map context exactly as-is. Oblique aerial view, sunny day, sharp shadows, photorealistic, 8k",
        "Replace the colored block viewed from above with a steep gabled roof with ornate chimney pots. Bay window projection visible. Keep surrounding context exactly as-is.",
        f"{BASE_NEGATIVE}, modern glass, stucco, suburban, flat roof",
        make_variants("toronto_bay_and_gable", [
            ("cabbagetown", "Cabbagetown Classic", "Red brick, ornate gable, stained glass, quintessential Toronto Victorian"),
            ("parkdale", "Parkdale Grand", "Larger scale, more ornate, sometimes turret at corner, semi-detached"),
            ("buff_brick", "Buff Brick", "White/buff brick variant, subtler polychrome, Annex fringe area"),
            ("painted", "Painted Brick", "Entire facade painted white, gentrified look, maintaining bay-and-gable form"),
        ]),
    ),
    make_building(
        "toronto_annex_mansion", "Toronto Annex Mansion", "toronto_annex",
        "Grand Romanesque Revival mansion with sandstone, turrets, round arches, and wide front porch in the Annex neighbourhood",
        "#C4A35A", 2, 3, 300, "residential_luxury",
        ["toronto", "annex", "mansion", "romanesque", "sandstone", "turret"],
        "sandstone (the defining Annex material, unlike brick elsewhere)", "deeply carved stone ornament, Romanesque round arches, heavy stone columns", "turrets, round towers, domes, wide front porches with stone columns",
        "wide front porch with heavy stone columns, stone steps, carved arch entrance", "sandstone walls with deep-set windows, round arches, carved stone ornament, turrets and round towers at corners", "steeply pitched roof with multiple gables, dormers, and turrets", "warm sandstone, dark slate roof, heavy stone character",
        "steeply pitched with turrets and multiple gables", "dark slate", "turrets, dormers, ornate chimneys, multiple roof planes", "complex roofline with turrets and gables, sandstone walls visible",
        ["sandstone", "carved stone ornament", "dark slate roofing", "heavy stone columns"],
        "Replace the colored building block with a photorealistic Toronto Annex mansion. Keep the exact same building footprint and height. Sandstone with Romanesque Revival arches, turrets, round towers. Wide front porch with heavy stone columns. Deeply carved stone ornament. Steeply pitched slate roof. 2.5-3 storey. Maintain the surrounding satellite map context exactly as-is. Oblique aerial view, sunny day, sharp shadows, photorealistic, 8k",
        "Replace the colored block viewed from above with a complex roof with turrets and multiple gables. Dark slate. Keep surrounding context exactly as-is.",
        f"{BASE_NEGATIVE}, modern glass, flat roof, stucco",
        make_variants("toronto_annex_mansion", [
            ("corner_turret", "Corner Turret", "Prominent round turret at corner, conical slate cap, grandest form"),
            ("romanesque", "Full Romanesque", "Heavy round arches throughout, deeply carved, fortress-like"),
            ("queen_anne", "Queen Anne Hybrid", "Mix of Romanesque and Queen Anne, more decorative, varied textures"),
            ("converted", "Converted to Apartments", "Divided into units, multiple doorbells, slightly less maintained"),
        ]),
    ),
    make_building(
        "toronto_rowhouse", "Toronto Brick Rowhouse", "toronto_victorian",
        "Continuous row of red brick attached houses with bay windows, front porches with turned columns, and shared cornice",
        "#B03A2E", 2, 3, 130, "residential_townhouse",
        ["toronto", "rowhouse", "brick", "bay_window", "porch", "victorian"],
        "red brick (dominant), sometimes buff brick", "stone lintels and sills, decorative brickwork cornice", "turned wood porch columns, bay windows (angled or rectangular)",
        "small front yard with low iron or wood fence, front porch with turned wood columns, tiled entrance path", "bay windows on first and/or second floor, decorative brick cornice, sash windows with stone lintels", "shared cornice line along the row, gable or flat roof", "red brick, cream stone lintels, dark painted wood porch, iron fence",
        "gable or flat behind shared cornice", "slate or asphalt shingle", "chimney pots in groups along party walls, shared cornice line", "continuous roofline with shared cornices, bay window projections",
        ["red brick", "stone lintels and sills", "turned wood porch columns", "decorative brick cornice"],
        "Replace the colored building block with a photorealistic Toronto brick rowhouse. Keep the exact same building footprint and height. Continuous row of attached red brick houses with bay windows, front porches with turned wood columns, stone lintels. Shared cornice line. Small front yards with iron fences. 2-3 storey. Maintain the surrounding satellite map context exactly as-is. Oblique aerial view, sunny day, sharp shadows, photorealistic, 8k",
        "Replace the colored block viewed from above with continuous roofline with shared cornices. Party wall chimney pots. Keep surrounding context exactly as-is.",
        f"{BASE_NEGATIVE}, modern glass, detached, suburban",
        make_variants("toronto_rowhouse", [
            ("leslieville", "Leslieville", "Tight row, smaller scale, east-end working-class character"),
            ("trinity_bellwoods", "Trinity-Bellwoods", "Slightly grander, wider lots, Victorian ornament"),
            ("bay_window", "Prominent Bay", "Large projecting bay windows dominating the facade"),
            ("painted_porch", "Painted Porch", "Brightly painted porch columns and trim, gentrified character"),
        ]),
    ),
    make_building(
        "toronto_junction_industrial", "Toronto Junction Converted Industrial", "toronto_junction",
        "Converted factory or warehouse in the Junction/Dundas West with sawtooth roof, painted brick, and loading dock patios",
        "#795548", 2, 4, 350, "commercial_creative",
        ["toronto", "junction", "industrial", "converted", "sawtooth", "brick"],
        "red or brown brick, sometimes painted white or black", "large industrial windows (multi-pane steel sash)", "sawtooth roofline from factory skylights, loading docks converted to patios, ghost signs",
        "loading dock converted to restaurant patio, or former factory entrance repurposed as gallery entrance", "large industrial multi-pane steel sash windows, painted brick (white, black, or natural), exposed structure visible inside", "sawtooth roof with north-facing skylights, or flat industrial roof", "red/brown brick (natural or painted), black steel windows, industrial character",
        "sawtooth with skylights, or flat", "membrane or built-up tar", "sawtooth skylights, ventilation stacks, ghost painted signage on walls", "sawtooth roof profile visible, or flat roof, large rectangular industrial footprint",
        ["red or brown brick", "steel-sash industrial windows", "sawtooth skylights", "heavy timber interior"],
        "Replace the colored building block with a photorealistic Toronto Junction converted industrial building. Keep the exact same building footprint and height. Red or brown brick (some painted) with large steel-sash industrial windows. Sawtooth roofline from factory skylights. Loading dock converted to patio. Ghost signs on brick walls. 2-4 storey. Maintain the surrounding satellite map context exactly as-is. Oblique aerial view, sunny day, sharp shadows, photorealistic, 8k",
        "Replace the colored block viewed from above with a sawtooth roof with north-facing skylights. Large rectangular footprint. Keep surrounding context exactly as-is.",
        f"{BASE_NEGATIVE}, residential, suburban, ornate classical",
        make_variants("toronto_junction_industrial", [
            ("brewery", "Brewery Conversion", "Former brewery, smokestack preserved, now restaurant/event space"),
            ("white_painted", "White Painted Loft", "Entire brick facade painted white, gallery/studio character"),
            ("ghost_sign", "Ghost Sign Building", "Faded painted advertising visible on brick wall, heritage character"),
            ("restaurant_patio", "Restaurant Patio", "Loading dock transformed into vibrant patio with string lights"),
        ]),
    ),
    make_building(
        "toronto_edwardian", "Toronto Edwardian Foursquare", "toronto_edwardian",
        "Boxy Edwardian house with deep front porch, simpler ornament than Victorian, hipped roof, and wider lot",
        "#A0522D", 2, 3, 180, "residential_house",
        ["toronto", "edwardian", "foursquare", "porch", "hipped_roof", "1900s"],
        "smooth brick (cleaner than Victorian polychrome), sometimes stucco or timber accents on gables", "simpler stone sills, minimal decorative brickwork compared to Victorian", "deep front porch with simpler square columns, hipped roof",
        "deep front porch spanning full width, simpler square columns (not turned), wider steps", "boxy, broader proportions than Victorian bay-and-gable, hipped roof, larger windows, less ornament", "hipped or gable roof, less steep than Victorian", "smooth red or buff brick, cream trim, stained wood porch columns",
        "hipped or shallow gable", "asphalt shingle or slate", "dormers in hipped roof, central chimney, simpler profile", "broader, boxier footprint than Victorian, hipped roof",
        ["smooth brick", "simple stone sills", "square porch columns", "asphalt shingle"],
        "Replace the colored building block with a photorealistic Toronto Edwardian foursquare. Keep the exact same building footprint and height. Boxy proportions with smooth brick. Deep front porch with square columns. Hipped roof. Wider and more restrained than Victorian neighbours. 2-2.5 storey. Maintain the surrounding satellite map context exactly as-is. Oblique aerial view, sunny day, sharp shadows, photorealistic, 8k",
        "Replace the colored block viewed from above with a hipped roof with dormers. Broader footprint. Keep surrounding context exactly as-is.",
        f"{BASE_NEGATIVE}, modern glass, ornate Victorian, tower",
        make_variants("toronto_edwardian", [
            ("classic_red", "Classic Red Brick", "Standard red brick foursquare, deep porch, clean lines"),
            ("buff_brick", "Buff Brick", "Cream/buff brick, slightly grander proportions"),
            ("stucco_gable", "Stucco Gable", "Stucco accents in gable end, Arts & Crafts influence"),
            ("corner_lot", "Corner Lot", "Larger corner lot version, wrap-around porch, extra windows"),
        ]),
    ),
    make_building(
        "toronto_streetcar_stop", "Toronto Streetcar Platform Stop", "toronto_transit",
        "Raised modular streetcar platform with glass shelter, TTC red branding, and cycling throughway",
        "#D32F2F", 1, 1, 100, "transit_stop",
        ["toronto", "streetcar", "ttc", "platform", "transit", "king_street"],
        "modular composite raised platform materials", "glass and steel enclosed shelter with TTC red branding", "raised platform at curb level for level boarding, integrated cycling throughway",
        "raised modular platform in former travel lane, glass shelter with TTC signage", "platform creates transit-priority island between streetcar tracks and cycling lane", "glass and steel canopy", "TTC red branding, glass shelter, grey platform surface",
        "glass and steel canopy over shelter", "glass panels", "TTC signage, digital arrival display", "narrow raised platform in street, glass shelter visible",
        ["modular composite platform", "glass shelter walls", "steel canopy", "TTC red branding"],
        "Replace the colored building block with a photorealistic Toronto TTC streetcar platform stop. Keep the exact same footprint. Raised modular platform with glass shelter in TTC red branding. Streetcar tracks adjacent. Cycling throughway integrated. Red-and-white Flexity streetcar approaching. Maintain the surrounding satellite map context exactly as-is. Oblique aerial view, sunny day, sharp shadows, photorealistic, 8k",
        "Replace the colored block viewed from above with a narrow raised platform in the roadway with glass canopy. Streetcar tracks visible. Keep surrounding context exactly as-is.",
        f"{BASE_NEGATIVE}, suburban, highway, parking lot",
        make_variants("toronto_streetcar_stop", [
            ("king_street", "King Street Priority", "Transit-priority corridor, expanded pedestrian areas, patios in former car lanes"),
            ("queen_street", "Queen Street", "Mixed traffic, heritage buildings backdrop, busier character"),
            ("spadina", "Spadina Dedicated", "Centre-of-road dedicated right-of-way, wider platform"),
            ("heritage", "Heritage Shelter", "Older TTC shelter design, simpler form, classic character"),
        ]),
    ),
    make_building(
        "toronto_condo_tower", "Toronto Condo Podium Tower", "toronto_modern",
        "Modern glass condo tower with heritage facade retention at podium base, large floor plates, Toronto skyline character",
        "#607D8B", 30, 70, 700, "residential_condo",
        ["toronto", "condo", "tower", "podium", "glass", "heritage_retention"],
        "glass curtain wall, reflective blue-tinted (more reflective than Vancouver's clearer glass)", "precast concrete panels, metal cladding on podium", "heritage facade retention (front wall of demolished building kept as podium base), large floor plates",
        "podium with ground-floor retail, sometimes incorporating retained heritage facade", "glass tower with larger floor plates than Vancouver, more varied forms, blue-tinted reflective glass", "flat tower roof with mechanical penthouse", "reflective blue glass, concrete podium, heritage brick at base if retained",
        "flat with mechanical penthouse", "membrane", "mechanical penthouse, crane during construction", "large tower footprint, podium below, possibly retained heritage facade visible at base",
        ["reflective glass curtain wall", "precast concrete", "heritage brick (retained facade)", "metal cladding"],
        "Replace the colored building block with a photorealistic Toronto condo podium tower. Keep the exact same building footprint and height. Glass tower with blue-tinted reflective curtain wall on podium with ground-floor retail. Heritage facade retention at podium base if applicable. 30-70 storey. Maintain the surrounding satellite map context exactly as-is. Oblique aerial view, sunny day, sharp shadows, photorealistic, 8k",
        "Replace the colored block viewed from above with a large glass tower top. Heritage facade or podium visible at base. Keep surrounding context exactly as-is.",
        f"{BASE_NEGATIVE}, low-rise, heritage, Victorian, suburban",
        make_variants("toronto_condo_tower", [
            ("king_west", "King West", "Clustered towers, entertainment district, heritage retention at base"),
            ("yonge_eglinton", "Yonge & Eglinton", "Midtown tower cluster, transit-oriented at subway station"),
            ("waterfront", "Waterfront", "Lake Ontario views, wider podium, public realm at water's edge"),
            ("heritage_retained", "Heritage Retention", "Prominent retained Victorian facade as podium, tower rising behind"),
        ]),
    ),
]

TORONTO_STREETS = [
    make_street(
        "toronto_streetcar_street", "Toronto Streetcar Street", "toronto_transit",
        "Toronto streetcar corridor with embedded tracks, overhead catenary, heritage and condo buildings, and TTC Flexity cars",
        "Streetcar tracks embedded in road surface. Overhead catenary wires on poles. Mix of heritage 2-3 storey commercial buildings and new condo podiums. Wide sidewalks with retail frontage. Street trees in grated tree wells. Red-and-white TTC Flexity streetcars running in mixed traffic. King, Queen, Dundas, or College character.",
        "Asphalt with embedded steel streetcar tracks, concrete sidewalks",
        "Street trees (maple, honeylocust) in iron grates at regular intervals",
        "Mix of heritage Victorian commercial (2-3 storey brick) and modern condo podiums, retail at grade",
        "Streetcar overhead catenary wires and support poles, TTC shelters, bike ring parking, fire hydrants",
        ["toronto", "streetcar", "ttc", "tracks", "catenary", "queen_king"],
        "Replace the colored zone with a photorealistic Toronto streetcar street. Embedded tracks, overhead catenary wires, red-white TTC Flexity streetcar, mix of heritage brick and condo podium buildings, wide sidewalks, retail frontage. Maintain satellite context. Oblique aerial view, photorealistic, 8k",
        BASE_NEGATIVE,
        {"width": 23},
    ),
    make_street(
        "toronto_residential_street", "Toronto Victorian Residential Street", "toronto_residential",
        "Tree-canopied Toronto residential side street lined with bay-and-gable and rowhouse red brick facades",
        "Tree-canopied residential street with continuous red brick bay-and-gable or rowhouse facades. Small front yards with low fences. On-street parking. Mature maples and oaks creating tunnel-like canopy. Quiet, pedestrian-dominated. The 'old Toronto' feel. Tiled front paths to porches.",
        "Asphalt with concrete sidewalks, concrete curbs",
        "Mature maples and oaks creating dense canopy tunnel over the street",
        "Continuous bay-and-gable or rowhouse facades in red brick, small front yards with low iron or wood fences",
        "Low iron fences, tiled front paths, turned-column porches, parked cars, fire hydrants, blue recycling bins",
        ["toronto", "residential", "victorian", "red_brick", "tree_canopy", "bay_and_gable"],
        "Replace the colored zone with a photorealistic Toronto Victorian residential street. Tree canopy tunnel, continuous red brick bay-and-gable facades, small front yards, iron fences, tiled paths. Quiet character. Maintain satellite context. Oblique aerial view, photorealistic, 8k",
        BASE_NEGATIVE,
        {"width": 13},
    ),
    make_street(
        "toronto_laneway", "Toronto Laneway", "toronto_lane",
        "Toronto back laneway with gravel or cracked asphalt, garage backs, fences, emerging laneway suites, raw urban character",
        "Narrow back lane running behind Victorian or Edwardian houses. Gravel or cracked asphalt. Garage backs, fences, garbage bins. Some emerging laneway suites (smaller program than Vancouver). More raw and gritty than Montreal's ruelles or Vancouver's lanes. Utility poles. Uneven surfaces.",
        "Gravel or cracked asphalt, no curbs, uneven surfaces",
        "Weeds growing through cracks, some overhanging trees from adjacent yards",
        "Garage backs, wooden fences, occasional new laneway suite, exposed brick party walls of adjacent houses",
        "Garbage bins, recycling, utility poles, gravel surface, raw urban character",
        ["toronto", "laneway", "alley", "raw", "garage", "urban"],
        "Replace the colored zone with a photorealistic Toronto laneway. Narrow back lane with gravel or cracked asphalt, garage backs, wooden fences, utility poles. Raw urban character. Some emerging laneway suites. Maintain satellite context. Oblique aerial view, photorealistic, 8k",
        BASE_NEGATIVE,
        {"width": 4.5},
    ),
]

TORONTO_PARKS = [
    make_park(
        "toronto_ravine", "Toronto Ravine Park", "toronto_landscape", "park",
        "Deep glacial ravine cutting through the urban grid, dense deciduous forest, unpaved trails, wooden bridges, 20-30m below street",
        "Deep glacial valley (20-30m below street level) cutting through the regular urban grid. Dense deciduous forest (maple, oak, beech). Unpaved trails. Wooden footbridges over creeks. The ravines disrupt the street grid, creating dead-ends and curving roads at their edges. Descending from the city grid into wilderness.",
        "Unpaved earth and wood-chip trails, wooden boardwalks over wet sections",
        "Dense deciduous forest: sugar maple, red oak, American beech, white pine. Understory of ferns and wildflowers.",
        "Wooden benches at viewpoints, simple trail markers, wooden footbridges",
        "Creeks and streams at ravine bottom, some with exposed bedrock, seasonal flooding",
        ["toronto", "ravine", "forest", "glacial", "trails", "creek"],
        "Replace the colored zone with a photorealistic Toronto ravine park. Deep forested valley cutting below the urban grid. Dense deciduous forest, unpaved trails, wooden footbridge over creek. 20-30m below surrounding streets. Maintain satellite context. Oblique aerial view, photorealistic, 8k",
        BASE_NEGATIVE,
    ),
    make_park(
        "toronto_urban_square", "Toronto Urban Square", "toronto_civic", "plaza",
        "Hard-surfaced Toronto civic plaza with ice rink in winter, public art, reflecting pool, surrounded by towers",
        "Hard-surfaced civic plaza. Ice rink in winter, reflecting pool in summer. Public art installations. Programmed event space. Surrounded by towers. More corporate/civic than intimate. Nathan Phillips Square character — curved City Hall, reflecting pool/rink.",
        "Stone or concrete paving, reflecting pool/ice rink surface",
        "Minimal — some trees at edges, seasonal planters",
        "Public art, event stage, cafe kiosk, ice rink changing rooms in winter",
        "Reflecting pool (becomes ice rink in winter)",
        ["toronto", "urban_square", "civic", "ice_rink", "public_art", "nathan_phillips"],
        "Replace the colored zone with a photorealistic Toronto urban square. Hard-paved civic plaza with reflecting pool, public art, event space. Surrounded by towers. Maintain satellite context. Oblique aerial view, photorealistic, 8k",
        BASE_NEGATIVE,
    ),
]


# ═══════════════════════════════════════════════════
# CALGARY KIT (8 buildings + 3 streets + 2 parks)
# ═══════════════════════════════════════════════════

CALGARY_BUILDINGS = [
    make_building(
        "calgary_sandstone", "Calgary Sandstone Heritage", "calgary_sandstone",
        "Paskapoo sandstone civic or commercial building with Romanesque arches, rough-hewn walls, built after the 1886 fire",
        "#C4A35A", 2, 4, 350, "commercial_heritage",
        ["calgary", "sandstone", "paskapoo", "romanesque", "heritage", "1886"],
        "Paskapoo sandstone (buff/golden, from local Paleocene formation quarries), rough-hewn or dressed finish", "heavy stone voussoirs and keystones over semi-circular Romanesque arches", "deeply recessed entries, heavy stone verandas and balconies, checkerwork rock-face finish",
        "grand entrance through heavy semi-circular Romanesque arch with large voussoirs, deeply recessed, heavy stone steps", "rough-hewn sandstone walls, bands of recessed windows with Romanesque arches, heavy and fortress-like character", "flat or low-pitched with stone or brick parapet, sometimes tower element", "warm buff-to-golden Paskapoo sandstone, heavy and monumental character",
        "flat or low-pitched behind parapet", "built-up or membrane", "possible clock tower (City Hall), stone parapet, minimal visible equipment", "flat roof behind sandstone parapet, sometimes with tower element",
        ["Paskapoo sandstone (buff/golden)", "heavy stone voussoirs", "rough-hewn finish", "Romanesque arches"],
        "Replace the colored building block with a photorealistic Calgary Paskapoo sandstone heritage building. Keep the exact same building footprint and height. Warm buff-golden sandstone with Richardsonian Romanesque semi-circular arches. Rough-hewn stone walls with heavy voussoirs. Deeply recessed entrance. Built after 1886 fire. 2-4 storey. Maintain the surrounding satellite map context exactly as-is. Oblique aerial view, sunny day, sharp shadows, photorealistic, 8k",
        "Replace the colored block viewed from above with a flat roof behind sandstone parapet. Keep surrounding context exactly as-is.",
        f"{BASE_NEGATIVE}, modern glass, grey concrete, suburban",
        make_variants("calgary_sandstone", [
            ("city_hall", "City Hall Style", "Clock tower, most ornate, 15,500 individual stone pieces, Romanesque Revival"),
            ("knox_church", "Knox Church Style", "Late Gothic Revival sandstone, 1,200-seat church, massive organ"),
            ("commercial_block", "Stephen Avenue Commercial", "2-3 storey commercial, checkerwork rock-face, simpler ornament"),
            ("palliser_hotel", "Palliser Hotel Style", "Beaux-Arts sandstone, grand hotel, prairie grain elevator proportions"),
        ]),
    ),
    make_building(
        "calgary_inglewood", "Inglewood Heritage Brick Commercial", "calgary_inglewood",
        "Red brick Edwardian commercial building on 9th Avenue SE with flat parapet, large display windows, and sandstone trim",
        "#8B4513", 2, 3, 250, "commercial_heritage",
        ["calgary", "inglewood", "brick", "edwardian", "heritage", "9th_avenue"],
        "red or brown brick with sandstone trim accents", "decorative brick parapet, large ground-floor display windows, transom windows", "stone lintels and sills, recessed entries, heritage character",
        "large plate-glass display windows, recessed entrance, transom windows above", "red or brown brick facade with decorative parapet, sandstone trim, simple but well-proportioned windows", "flat roof with decorative brick or stone parapet", "warm red-brown brick, cream sandstone trim, heritage character weathered to warm patina",
        "flat with decorative parapet", "built-up tar or membrane", "simple parapet, minimal visible equipment", "flat roof, reads as part of a continuous main street commercial row",
        ["red-brown brick", "sandstone trim", "decorative brick parapet", "large display windows"],
        "Replace the colored building block with a photorealistic Inglewood heritage brick commercial building. Keep the exact same building footprint and height. Red-brown brick with sandstone trim on Calgary's oldest main street (9th Avenue SE). Decorative brick parapet. Large display windows. Edwardian commercial character weathered to warm patina. 2-3 storey. Maintain the surrounding satellite map context exactly as-is. Oblique aerial view, sunny day, sharp shadows, photorealistic, 8k",
        "Replace the colored block viewed from above with a flat roof behind decorative brick parapet. Part of continuous main street row. Keep surrounding context exactly as-is.",
        f"{BASE_NEGATIVE}, modern glass, suburban, sandstone",
        make_variants("calgary_inglewood", [
            ("burn_block", "Burn Block Style", "Romanesque-influenced, grand central arch, polychrome brickwork"),
            ("brewery", "Brewery Heritage", "Former Calgary Brewing building, smokestack, industrial heritage"),
            ("restored", "Beautifully Restored", "Facade restoration, heritage colours, modern retail inside"),
            ("mixed_era", "Mixed Era Block", "Heritage and contemporary infill side by side, Inglewood character"),
        ]),
    ),
    make_building(
        "calgary_plus15_tower", "Calgary Plus-15 Connected Tower", "calgary_downtown",
        "Downtown glass office tower connected by enclosed elevated Plus-15 pedestrian bridges at 4.5m above street level",
        "#607D8B", 15, 50, 600, "commercial_office",
        ["calgary", "plus15", "downtown", "glass", "tower", "skywalk"],
        "glass curtain wall, steel structure", "enclosed glass pedestrian bridges at +15 feet connecting to adjacent buildings", "each bridge architecturally matched to its connecting buildings",
        "ground-floor lobby with Plus-15 connection visible at second floor, street-level retail (often less active due to Plus-15 drawing traffic upward)", "glass curtain wall office tower, Plus-15 bridges connecting at second-floor level, visible from street as glass-enclosed bridges spanning between buildings", "flat roof with mechanical penthouse", "glass and steel, Plus-15 bridges in matching materials",
        "flat with mechanical penthouse", "membrane", "mechanical penthouse, window-washing equipment", "glass tower top, Plus-15 bridges visible connecting to adjacent towers",
        ["glass curtain wall", "steel structure", "enclosed glass Plus-15 bridges", "concrete piers"],
        "Replace the colored building block with a photorealistic Calgary Plus-15 connected downtown office tower. Keep the exact same building footprint and height. Glass curtain wall tower with enclosed glass pedestrian bridges (Plus-15) connecting to adjacent buildings at 4.5m above street level. Rocky Mountain backdrop visible. 15-50 storey. Maintain the surrounding satellite map context exactly as-is. Oblique aerial view, sunny day, sharp shadows, photorealistic, 8k",
        "Replace the colored block viewed from above with a glass tower top with Plus-15 bridges connecting to adjacent buildings. Keep surrounding context exactly as-is.",
        f"{BASE_NEGATIVE}, heritage, low-rise, suburban, residential",
        make_variants("calgary_plus15_tower", [
            ("the_bow", "The Bow (Foster+Partners)", "Crescent-shaped, 236m, facing Rocky Mountains, Calgary's tallest"),
            ("telus_sky", "TELUS Sky (BIG)", "Twisting form, Northern Lights LED art facade, LEED Platinum"),
            ("standard_office", "Standard Office Tower", "Typical 1980s office tower, rectangular, glass and steel, Plus-15 connected"),
            ("multiple_bridges", "Multiple Bridge Connections", "Corner tower with Plus-15 bridges in multiple directions"),
        ]),
    ),
    make_building(
        "calgary_beltline_midrise", "Calgary Beltline Mid-Rise", "calgary_beltline",
        "Contemporary mixed-use mid-rise along 17th Avenue with ground-floor retail and urban residential above",
        "#795548", 6, 12, 400, "mixed_use",
        ["calgary", "beltline", "midrise", "mixed_use", "17th_avenue", "contemporary"],
        "brick, precast panels, metal cladding, glass — contemporary material palette", "ground-floor retail glazing, residential balconies above", "flat roof, contextual design referencing heritage materiality",
        "ground-floor retail storefronts along 17th Avenue, residential entrance with lobby", "contemporary mixed-use facade with brick, metal panel, and glass, residential balconies, varied massing", "flat roof with potential rooftop amenity", "contemporary mix of warm brick, metal panels, and glass, urban character",
        "flat, possibly with rooftop amenity deck", "membrane with deck or green roof", "rooftop amenity space, mechanical equipment screened", "flat roof, mid-rise scale fitting into Beltline fabric",
        ["contemporary brick", "metal cladding panels", "glass curtain wall", "precast concrete"],
        "Replace the colored building block with a photorealistic Calgary Beltline mid-rise mixed-use building. Keep the exact same building footprint and height. Contemporary materials (brick, metal panel, glass) with ground-floor retail along 17th Avenue and residential above with balconies. 6-12 storey. Maintain the surrounding satellite map context exactly as-is. Oblique aerial view, sunny day, sharp shadows, photorealistic, 8k",
        "Replace the colored block viewed from above with a flat roof, mid-rise scale. Keep surrounding context exactly as-is.",
        f"{BASE_NEGATIVE}, heritage sandstone, suburban, low-rise bungalow",
        make_variants("calgary_beltline_midrise", [
            ("17th_avenue", "17th Avenue Red Mile", "Active retail frontage, restaurant patios, 17th Avenue character"),
            ("mission_district", "Mission District", "Slightly more residential feel, tree-lined, Mission neighbourhood"),
            ("brick_contemporary", "Brick Contemporary", "Warm brick cladding referencing heritage, modern form"),
            ("tower_emerging", "Emerging Tower", "Taller (12+ storey) condo or rental, Beltline densification"),
        ]),
    ),
    make_building(
        "calgary_bungalow", "Calgary Inner-City Bungalow", "calgary_residential",
        "Post-war prairie bungalow on a wide 50x120 foot lot with low-pitched roof, wide eaves, and stucco or brick veneer",
        "#A0785A", 1, 1, 120, "residential_house",
        ["calgary", "bungalow", "prairie", "postwar", "1950s", "wide_lot"],
        "wood frame, stucco or brick veneer exterior", "wide projecting eaves, low-pitched roof", "attached or detached single-car garage, front lawn, wide lot coverage",
        "front entrance with small covered porch, driveway to attached or detached garage", "low-slung horizontal emphasis responding to prairie landscape, wide eaves, long bands of windows, stucco or brick veneer", "low-pitched hip or gable roof with wide projecting eaves", "cream or tan stucco, or red/brown brick veneer, wide lot frontage is distinctively Calgary",
        "low-pitched hip or gable with wide eaves", "asphalt shingle", "low chimney, wide eaves visible, very low profile", "wide rectangular footprint covering much of 50-foot lot, low profile, prairie horizontal",
        ["stucco or brick veneer", "asphalt shingle roofing", "wood frame", "wide eaves"],
        "Replace the colored building block with a photorealistic Calgary inner-city bungalow. Keep the exact same building footprint and height. Low-slung post-war bungalow with stucco or brick veneer on a wide 50x120 foot lot. Low-pitched roof with wide projecting eaves. Front lawn. Attached garage. Prairie horizontal emphasis. Single storey. Maintain the surrounding satellite map context exactly as-is. Oblique aerial view, sunny day, sharp shadows, photorealistic, 8k",
        "Replace the colored block viewed from above with a wide low-pitched roof covering most of the lot. Very low profile, prairie horizontal. Keep surrounding context exactly as-is.",
        f"{BASE_NEGATIVE}, modern tower, multi-storey, ornate, urban",
        make_variants("calgary_bungalow", [
            ("altadore", "Altadore Classic", "Well-maintained, mature landscaping, desirable inner-city neighbourhood"),
            ("capitol_hill", "Capitol Hill", "Original character, slightly smaller, established trees"),
            ("infill_next_door", "Next to Modern Infill", "Original bungalow beside a new skinny infill, Calgary's contrast"),
            ("basement_suite", "With Basement Suite", "Separate basement entrance visible, converted to rental suite"),
        ]),
    ),
    make_building(
        "calgary_modern_infill", "Calgary Modern Infill House", "calgary_infill",
        "Contemporary narrow infill house on a split 25-foot lot with Hardie board, metal cladding, and flat or low-slope roof",
        "#607D8B", 2, 3, 130, "residential_house",
        ["calgary", "infill", "modern", "skinny", "hardie_board", "lot_split"],
        "fiber cement (Hardie board HZ10 for Calgary freeze-thaw), metal cladding", "large windows, contemporary clean lines", "flat or low-slope roof, significantly taller than neighbouring bungalows",
        "front entrance with modern canopy, narrow driveway, contemporary landscaping", "clean contemporary lines, Hardie board and metal cladding, large windows, narrow proportions on 25-foot lot", "flat or very low-slope roof", "grey or charcoal Hardie board, black or dark metal accents, large clear windows",
        "flat or very low-slope", "membrane", "minimal visible equipment, clean contemporary profile", "narrow rectangular footprint on half of former bungalow lot, flat roof, taller than neighbours",
        ["fiber cement (Hardie board)", "metal cladding", "large windows", "membrane roof"],
        "Replace the colored building block with a photorealistic Calgary modern infill house. Keep the exact same building footprint and height. Contemporary narrow house on a split 25-foot lot. Hardie board and metal cladding, large windows, flat roof. Significantly taller than neighbouring bungalows. 2-3 storey. Maintain the surrounding satellite map context exactly as-is. Oblique aerial view, sunny day, sharp shadows, photorealistic, 8k",
        "Replace the colored block viewed from above with a flat-roofed narrow house on half a former bungalow lot. Taller than neighbours. Keep surrounding context exactly as-is.",
        f"{BASE_NEGATIVE}, heritage, ornate, brick Victorian, bungalow",
        make_variants("calgary_modern_infill", [
            ("charcoal_hardie", "Charcoal Hardie Board", "Dark grey fiber cement, black metal accents, minimalist"),
            ("wood_accent", "Wood Accent", "Cedar or wood-look cladding accent panels, warmer feel"),
            ("duplex_infill", "Side-by-Side Duplex", "Two narrow units on one lot, mirrored design"),
            ("fourplex_rcg", "R-CG Fourplex", "Four units on one lot under new R-CG zoning, contextual height"),
        ]),
    ),
    make_building(
        "calgary_ctrain_station", "Calgary CTrain Station", "calgary_transit",
        "At-grade CTrain light rail station on 7th Avenue transit mall with platform canopy and synchronized signal lights",
        "#D32F2F", 1, 1, 200, "transit_station",
        ["calgary", "ctrain", "lrt", "station", "7th_avenue", "transit_mall"],
        "thin-shell concrete canopy structures on single slender columns (UHPFRC at Shawnessy)", "glass-walled heated shelters for Calgary's extreme winters", "staggered single-platform design (one direction per block, alternating)",
        "platform at street level in centre of 7th Avenue transit mall, accessible from sidewalk", "thin-shell concrete canopy or glass-walled heated shelter on platform, CTrain tracks in centre of street", "canopy or shelter roof over platform", "light grey concrete, glass shelters, CTrain red/blue branding, Plus-15 bridges crossing overhead",
        "thin concrete shell canopy or glass shelter", "concrete shell or glass panels", "CTrain signage, digital displays, emergency phones", "narrow platform in centre of 7th Avenue, canopy visible, tracks running along street",
        ["UHPFRC thin-shell concrete", "glass shelter walls", "steel columns", "platform pavers"],
        "Replace the colored building block with a photorealistic Calgary CTrain station on 7th Avenue transit mall. Keep the exact same footprint. At-grade platform with thin-shell concrete canopy in centre of street. No private vehicle traffic. Office tower canyon on both sides. Plus-15 bridges crossing overhead. CTrain visible. Maintain the surrounding satellite map context exactly as-is. Oblique aerial view, sunny day, sharp shadows, photorealistic, 8k",
        "Replace the colored block viewed from above with a thin canopy structure on a platform in the centre of 7th Avenue. CTrain tracks running along the street. Keep surrounding context exactly as-is.",
        f"{BASE_NEGATIVE}, suburban, parking lot, residential",
        make_variants("calgary_ctrain_station", [
            ("downtown_7th", "Downtown 7th Avenue", "Office tower canyon, Plus-15 overhead, synchronized signals"),
            ("shawnessy", "Shawnessy UHPFRC", "Thin-shell concrete canopy, single columns, suburban terminus"),
            ("saddletowne", "Saddletowne NE", "Centre-loading island platform, park-and-ride, northeast terminus"),
            ("city_hall", "City Hall Station", "Only station serving both directions, adjacent to sandstone City Hall"),
        ]),
    ),
    make_building(
        "calgary_central_library", "Calgary New Central Library", "calgary_landmark",
        "Snohetta-designed library with Chinook-arch cedar entrance, textured glass facade, built over an active CTrain line",
        "#8B6914", 4, 5, 2000, "institutional_cultural",
        ["calgary", "library", "snohetta", "chinook_arch", "cedar", "landmark"],
        "textured glass-and-metal facade panels, western red cedar entrance arch", "Chinook-arch-inspired entry form in western red cedar", "built literally over an active CTrain line, TIME Magazine 100 Greatest Places 2019",
        "dramatic western red cedar arch entrance inspired by the Chinook weather arch, wide public steps", "textured glass-and-metal facade creating diamond/hexagonal patterns, cedar-lined interior visible through glass", "complex angular roof forms", "warm cedar entrance against cool glass facade, textured patterns catching prairie light",
        "complex angular forms", "metal panels and glass", "angular roofline, public terrace, CTrain tracks passing below building", "complex angular roof, CTrain tracks visible passing underneath the building",
        ["western red cedar", "textured glass panels", "metal facade panels", "steel structure over CTrain"],
        "Replace the colored building block with a photorealistic building inspired by Calgary's New Central Library (Snohetta). Keep the exact same building footprint and height. Dramatic western red cedar arch entrance. Textured glass-and-metal facade with diamond patterns. Built over transit tracks. 4-5 storey. Maintain the surrounding satellite map context exactly as-is. Oblique aerial view, sunny day, sharp shadows, photorealistic, 8k",
        "Replace the colored block viewed from above with a complex angular roof. Transit tracks visible passing underneath. Keep surrounding context exactly as-is.",
        f"{BASE_NEGATIVE}, generic, suburban, residential, box",
        make_variants("calgary_central_library", [
            ("chinook_entry", "Chinook Arch Entry", "Emphasis on the dramatic cedar arch entrance, prairie sky above"),
            ("glass_texture", "Textured Glass Detail", "Close view showing the diamond/hexagonal glass pattern"),
            ("ctrain_below", "CTrain Passing Below", "View showing the building straddling the active CTrain line"),
            ("evening_glow", "Evening Illumination", "Interior warm glow through glass facade at dusk, prairie sky"),
        ]),
    ),
]

CALGARY_STREETS = [
    make_street(
        "calgary_stephen_avenue", "Stephen Avenue Pedestrian Mall", "calgary_heritage",
        "National Historic Site pedestrian mall with sandstone heritage buildings, Plus-15 bridges overhead, patios, and granite pavers",
        "Pedestrian-only historic street (8th Avenue SW). 30+ sandstone-era buildings from 1880-1930 on both sides. Granite pavers. Street trees. Patios and cafe seating. Plus-15 bridges crossing overhead connecting office towers. Public art. Heritage and modern coexisting — sandstone facades at ground level with glass towers above and behind.",
        "Granite pavers (new 2025-2026 renovation), stone curbs",
        "18 new trees with advanced soil cell technology for stormwater management",
        "Heritage sandstone buildings (1880-1930) at ground level, modern glass towers above/behind, Plus-15 bridges crossing overhead",
        "Patios, cafe seating, public art, heritage interpretive panels, Plus-15 bridge shadows on pavement",
        ["calgary", "stephen_avenue", "pedestrian", "sandstone", "heritage", "plus15"],
        "Replace the colored zone with a photorealistic Stephen Avenue pedestrian mall. Sandstone heritage buildings on both sides, granite pavers, Plus-15 bridges crossing overhead, patios, street trees. National Historic Site. Maintain satellite context. Oblique aerial view, photorealistic, 8k",
        BASE_NEGATIVE,
        {"width": 19},
    ),
    make_street(
        "calgary_bow_pathway", "Bow River Pathway", "calgary_pathway",
        "Multi-use pathway along the Bow River with prairie grasses, cottonwood trees, mountain views, and Peace Bridge",
        "Paved multi-use pathway along the Bow River. Native prairie grasses and cottonwood trees along edges. Views of downtown skyline with Rocky Mountain backdrop on clear days. Peace Bridge (Santiago Calatrava, red tubular steel helical truss) crossing the river. Separated pedestrian and cycling lanes. Year-round use (cleared of snow).",
        "Paved asphalt pathway (3-4m wide), separated walking and cycling lanes",
        "Native prairie grasses, cottonwood trees along riverbanks, willows near water edge",
        "Bow River on one side, urban fabric on the other, downtown skyline visible",
        "Benches at viewpoints, trail maps, washrooms, Peace Bridge as landmark crossing, mountain views",
        ["calgary", "bow_river", "pathway", "peace_bridge", "prairie", "mountain_views"],
        "Replace the colored zone with a photorealistic Bow River Pathway. Paved multi-use path along the river with prairie grasses and cottonwood trees. Downtown skyline and Rocky Mountain backdrop. Peace Bridge (red tubular steel) crossing. Maintain satellite context. Oblique aerial view, photorealistic, 8k",
        BASE_NEGATIVE,
        {"width": 8},
    ),
    make_street(
        "calgary_inglewood_street", "Inglewood Main Street", "calgary_heritage",
        "Heritage brick main street (9th Avenue SE) with restored facades, angle parking, local shops, and small-town-in-the-city character",
        "Calgary's oldest main street lined with heritage brick commercial buildings (1900-1920s). Wide sidewalks. Angle parking. Local shops, galleries, cafes. Restored Edwardian facades. Former brewery buildings nearby. Feels like a small prairie town despite proximity to downtown. Warm brick and sandstone patina.",
        "Asphalt with angle parking bays, wide concrete sidewalks",
        "Street trees in tree wells, seasonal planters at storefronts",
        "Continuous 2-3 storey heritage brick commercial facades, restored Edwardian character, local shops and galleries",
        "Angle parking, wide sidewalks, restored heritage signage, seasonal planters, local business character",
        ["calgary", "inglewood", "9th_avenue", "heritage", "brick", "main_street"],
        "Replace the colored zone with a photorealistic Inglewood main street (9th Avenue SE). Heritage brick storefronts with restored facades, angle parking, wide sidewalks, local shops and galleries. Small-town character. Maintain satellite context. Oblique aerial view, photorealistic, 8k",
        BASE_NEGATIVE,
        {"width": 19},
    ),
]

CALGARY_PARKS = [
    make_park(
        "calgary_princes_island", "Prince's Island Park", "calgary_river", "park",
        "River island park in the Bow River with walking paths, cottonwood trees, public art, event lawns, and mountain views",
        "20-hectare island in the Bow River immediately north of downtown. Large manicured grass lawns, ponds with fountains, flower gardens, art sculptures, outdoor stage, children's playground. Network of trails lined with cottonwood trees. Eastern end is designated wetland marsh (Chevron Learning Pathway). Connected to downtown by three bridges. Integrated into Bow River Pathway system. Mountain views on clear days.",
        "Paved and gravel walking paths, wooden boardwalks in wetland area",
        "Cottonwood trees (defining Calgary landscape element), flower gardens, native prairie grasses in wetland",
        "Benches along paths, outdoor stage for events, children's playground, food stands",
        "Ponds with fountains, lagoon (former lumber channel), constructed wetland at east end",
        ["calgary", "princes_island", "river", "island", "cottonwood", "events"],
        "Replace the colored zone with a photorealistic Prince's Island Park. River island with walking paths, cottonwood trees, grass lawns, ponds with fountains, public art. Downtown skyline and mountain backdrop. Maintain satellite context. Oblique aerial view, photorealistic, 8k",
        BASE_NEGATIVE,
    ),
    make_park(
        "calgary_prairie_plaza", "Calgary Prairie Urban Plaza", "calgary_civic", "plaza",
        "Open civic plaza with big prairie sky, reflecting pool, wind-swept character, seasonal markets, and mountain views",
        "Hard-surfaced civic plaza. Big sky overhead — Calgary's high elevation (1,045m) and prairie location create enormous open skies. Reflecting pool or water feature. Open and sometimes wind-swept. Designed for community gatherings and seasonal markets. Mountain views on clear days. The openness and sky are the defining features.",
        "Stone or concrete paving, open expanses",
        "Minimal — some trees at edges, native prairie grass in planters",
        "Seasonal market stalls, event stage, warming huts in winter, benches",
        "Reflecting pool, sometimes ice features in winter",
        ["calgary", "plaza", "prairie", "big_sky", "mountain_views", "open"],
        "Replace the colored zone with a photorealistic Calgary prairie urban plaza. Open civic space with big sky, reflecting pool, mountain views on horizon. Wind-swept, expansive character. Seasonal market potential. Maintain satellite context. Oblique aerial view, photorealistic, 8k",
        BASE_NEGATIVE,
    ),
]


# ═══════════════════════════════════════════════════
# HALIFAX KIT (6 buildings + 2 streets + 2 parks)
# ═══════════════════════════════════════════════════

HALIFAX_BUILDINGS = [
    make_building(
        "halifax_hydrostone", "Hydrostone Neighbourhood House", "halifax_hydrostone",
        "Arts and Crafts Tudor Revival house built with hydrostone blocks after the 1917 Halifax Explosion",
        "#A0785A", 2, 2, 120, "residential_house",
        ["halifax", "hydrostone", "tudor", "arts_crafts", "explosion", "1917"],
        "hydrostone blocks (concrete blocks with crushed granite finish), half-timbering on upper floor", "wood trim, stucco or rendered panels between timbers", "gabled dormers, hipped gable roof, fireproof construction",
        "simple entrance with covered porch, walkway from sidewalk", "half-timbering on second storey with stucco or rendered infill panels. Hydrostone blocks on first storey. Gabled dormers. Garden City layout.", "hipped gable roof with dormers", "light stone-like hydrostone blocks, dark timber half-timbering, cream stucco panels",
        "hipped gable with dormers", "asphalt shingle", "dormers, simple chimney", "small house in Garden City pattern, organized along boulevarded streets",
        ["hydrostone blocks (granite-faced concrete)", "timber half-timbering", "stucco infill panels", "asphalt shingle"],
        "Replace the colored building block with a photorealistic Halifax Hydrostone neighbourhood house. Keep the exact same building footprint and height. Hydrostone blocks on first storey, Tudor half-timbering on second with stucco panels. Gabled dormers. Garden City layout. Built after 1917 Halifax Explosion. 2 storey. Maintain the surrounding satellite map context exactly as-is. Oblique aerial view, sunny day, sharp shadows, photorealistic, 8k",
        "Replace the colored block viewed from above with a hipped gable roof with dormers. Small house in Garden City street pattern. Keep surrounding context exactly as-is.",
        f"{BASE_NEGATIVE}, modern glass, urban tower, concrete",
        make_variants("halifax_hydrostone", [
            ("classic_tudor", "Classic Tudor Style", "Strong half-timber pattern, cream stucco, well-maintained garden"),
            ("corner_house", "Corner House", "Slightly larger, more windows, facing two boulevarded streets"),
            ("restored", "Beautifully Restored", "Heritage-accurate restoration, National Historic Site character"),
            ("commercial_ground", "Commercial Ground Floor", "Hydrostone Market area, shop at ground level, residence above"),
        ]),
    ),
    make_building(
        "halifax_waterfront_warehouse", "Halifax Waterfront Warehouse", "halifax_maritime",
        "Heavy granite and ironstone maritime warehouse from 1800-1875, now restored as shops and restaurants",
        "#6B6B6B", 2, 3, 300, "commercial_heritage",
        ["halifax", "waterfront", "warehouse", "granite", "maritime", "privateers"],
        "granite and ironstone, heavy masonry, unadorned and functional", "heavy timber interior structure", "thick stone walls, small windows (security and structural), loading doors",
        "stone entrance, former loading dock area, now retail or restaurant at ground level", "heavy stone walls with small windows, loading doors, functional character without ornament", "flat or low-pitched roof", "grey granite, dark ironstone, heavy and austere maritime character",
        "flat or low-pitched", "slate or membrane", "simple parapet, minimal equipment", "heavy rectangular footprint along the waterfront wharf",
        ["granite", "ironstone", "heavy timber", "slate"],
        "Replace the colored building block with a photorealistic Halifax waterfront warehouse. Keep the exact same building footprint and height. Heavy granite and ironstone walls with small windows. Former maritime warehouse, now restored as shops and restaurants. No ornament — mass and durability. 2-3 storey. Maintain the surrounding satellite map context exactly as-is. Oblique aerial view, sunny day, sharp shadows, photorealistic, 8k",
        "Replace the colored block viewed from above with a flat or low-pitched roof. Heavy rectangular stone building along the waterfront. Keep surrounding context exactly as-is.",
        f"{BASE_NEGATIVE}, modern glass, suburban, bright colours",
        make_variants("halifax_waterfront_warehouse", [
            ("historic_properties", "Historic Properties", "Victorian-Italianate restored facades, Privateers' Wharf character"),
            ("shipping_warehouse", "Shipping Warehouse", "Larger scale, heavier construction, former import/export"),
            ("restaurant_conversion", "Restaurant Conversion", "Warm interior visible, patio on former loading dock"),
            ("chandlery", "Maritime Chandlery", "Smaller scale, maritime supplies, rope and anchor visible"),
        ]),
    ),
    make_building(
        "halifax_clapboard_row", "Halifax Painted Clapboard Row", "halifax_residential",
        "Brightly painted wooden clapboard rowhouse on Halifax's steep harbour-facing slopes",
        "#F4D03F", 2, 3, 120, "residential_townhouse",
        ["halifax", "clapboard", "painted", "bright", "harbour", "wooden"],
        "wood frame, painted wood clapboard siding in bold colours (yellows, blues, reds, greens)", "wood trim, decorative window surrounds", "double-hung sash windows, gable or hipped roof, front stoops",
        "front stoop with simple railing, narrow lot, directly on sidewalk or with tiny front yard", "painted clapboard in bold saturated colour (yellow, blue, red, green), white-painted window trim, sash windows", "gable or hipped roof with shingles", "bold painted clapboard colour, white trim, contrasting door colour",
        "gable or hipped", "asphalt shingle or metal roofing", "simple chimney, dormers on some", "colourful row of painted rooftops stepping up the hillside, harbour visible below",
        ["painted wood clapboard", "white wood trim", "asphalt shingle or metal roof", "wood sash windows"],
        "Replace the colored building block with a photorealistic Halifax painted clapboard rowhouse. Keep the exact same building footprint and height. Brightly painted wood clapboard (yellow, blue, red, or green) with white trim. Sash windows. Gable roof. On a steep hillside facing the harbour. 2-3 storey. Maintain the surrounding satellite map context exactly as-is. Oblique aerial view, sunny day, sharp shadows, photorealistic, 8k",
        "Replace the colored block viewed from above with a simple gabled roof. Colourful painted clapboard visible on facade, stepping up the hillside. Keep surrounding context exactly as-is.",
        f"{BASE_NEGATIVE}, modern glass, concrete, flat terrain",
        make_variants("halifax_clapboard_row", [
            ("sunny_yellow", "Sunny Yellow", "Bright yellow clapboard, white trim, blue door, classic Maritime"),
            ("ocean_blue", "Ocean Blue", "Deep blue clapboard, white trim, red door, harbour-facing"),
            ("heritage_red", "Heritage Red", "Dark red clapboard, cream trim, Georgian proportions"),
            ("row_of_colours", "Rainbow Row", "Adjacent houses in different bright colours creating a colourful street"),
        ]),
    ),
    make_building(
        "halifax_georgian", "Halifax Georgian Colonial", "halifax_colonial",
        "White clapboard or stone Georgian colonial building with symmetrical facade, Palladian proportions, and multi-pane sash windows",
        "#F5F0E1", 2, 3, 200, "institutional_heritage",
        ["halifax", "georgian", "colonial", "palladian", "clapboard", "symmetrical"],
        "wood clapboard (painted white or cream), or stone (granite)", "classical pilasters or columns at entrance, stone trim", "symmetrical facade with central door, multi-pane sash windows (6-over-6 or 12-over-12)",
        "central entrance with classical surround, pediment or fanlight, symmetrical steps", "strictly symmetrical multi-pane sash windows, classical pilasters, clapboard or stone walls", "low-pitched hip or gable roof with dormers", "white or cream painted clapboard, or grey granite, classical proportions",
        "low-pitched hip or gable with dormers", "slate or shingle", "dormers, central chimney or paired end chimneys", "symmetrical rectangular footprint, classical proportions",
        ["white painted clapboard or granite", "classical wood or stone columns", "multi-pane sash windows", "slate roofing"],
        "Replace the colored building block with a photorealistic Halifax Georgian colonial building. Keep the exact same building footprint and height. White clapboard or grey granite with symmetrical Palladian facade. Central entrance with classical surround. Multi-pane sash windows. Low-pitched roof with dormers. 2-3 storey. Maintain the surrounding satellite map context exactly as-is. Oblique aerial view, sunny day, sharp shadows, photorealistic, 8k",
        "Replace the colored block viewed from above with a symmetrical low-pitched roof with dormers. Classical proportions. Keep surrounding context exactly as-is.",
        f"{BASE_NEGATIVE}, modern glass, bright paint, Victorian ornament",
        make_variants("halifax_georgian", [
            ("government_house", "Government House", "Grand gubernatorial residence, Adam-influenced, formal gardens"),
            ("church", "Georgian Church", "St. Paul's style, Palladian, oldest surviving building in Halifax"),
            ("town_clock", "Town Clock Tower", "Three-tiered octagonal tower on white clapboard base, city landmark"),
            ("officers_quarters", "Military Officers' Quarters", "Citadel Hill area, more austere, military precision"),
        ]),
    ),
    make_building(
        "halifax_commercial", "Halifax Maritime Commercial", "halifax_commercial",
        "Victorian commercial building on Barrington Street with stone or brick, cast-iron storefront, and decorative cornice",
        "#6B6B6B", 2, 4, 250, "commercial_heritage",
        ["halifax", "barrington", "commercial", "victorian", "cast_iron", "maritime"],
        "stone (granite, ironstone) or brick, heavy masonry", "cast-iron storefronts at ground level, decorative cornices", "flat or low-pitched roofs with parapets, some Second Empire mansard roofs",
        "cast-iron column storefront with large display windows, recessed entry", "stone or brick facade, decorative window surrounds, cornice with brackets", "flat with decorative parapet, or Second Empire mansard", "grey stone or red brick, black cast-iron, heritage character",
        "flat with parapet, or mansard", "slate on mansard, membrane on flat", "decorative parapet or mansard dormers", "flat or mansard roof, part of commercial streetwall",
        ["granite or brick", "cast-iron storefront columns", "decorative stone cornice", "slate on mansard"],
        "Replace the colored building block with a photorealistic Halifax maritime commercial building. Keep the exact same building footprint and height. Stone or brick with cast-iron storefront columns at ground level. Decorative cornice. Victorian commercial character on Barrington Street. 2-4 storey. Maintain the surrounding satellite map context exactly as-is. Oblique aerial view, sunny day, sharp shadows, photorealistic, 8k",
        "Replace the colored block viewed from above with a flat or mansard roof. Part of a commercial streetwall. Keep surrounding context exactly as-is.",
        f"{BASE_NEGATIVE}, modern glass, suburban, bright clapboard",
        make_variants("halifax_commercial", [
            ("barrington_street", "Barrington Street", "Halifax's historic commercial spine, mix of stone and brick"),
            ("second_empire", "Second Empire Mansard", "Ornate mansard roof with dormers, grander civic presence"),
            ("adapted", "Adapted Over Centuries", "Georgian bones with Victorian facade, layers of history"),
            ("waterfront_retail", "Waterfront Retail", "Adjacent to boardwalk, tourist-oriented, maritime gift shops"),
        ]),
    ),
    make_building(
        "halifax_ferry_terminal", "Halifax Ferry Terminal", "halifax_transit",
        "Waterfront ferry terminal integrated into the Halifax Boardwalk, connecting to Dartmouth across the harbour",
        "#4A90D9", 1, 2, 200, "transit_station",
        ["halifax", "ferry", "terminal", "waterfront", "boardwalk", "harbour"],
        "renovated terminal building, modern acoustic ceiling, tourism kiosk", "floating dock/gangway extending into Halifax Harbour", "integrated into the Halifax Boardwalk promenade",
        "terminal entrance from boardwalk, ticket area, waiting shelter, views across harbour to Dartmouth", "compact terminal building with waiting area, connected to floating pier by gangway", "modern canopy over waiting area", "maritime character, glass for harbour views, integrated into boardwalk",
        "modern canopy", "metal or glass panels", "ferry signage, harbour views through glass", "compact terminal on waterfront, floating pier extending into harbour",
        ["renovated terminal building", "floating dock/gangway", "glass harbour viewing", "boardwalk integration"],
        "Replace the colored building block with a photorealistic Halifax ferry terminal. Keep the exact same footprint. Compact waterfront terminal integrated into the Halifax Boardwalk. Floating pier extending into harbour. Adjacent to Historic Properties heritage warehouses. Harbour views to Dartmouth. Maintain the surrounding satellite map context exactly as-is. Oblique aerial view, sunny day, sharp shadows, photorealistic, 8k",
        "Replace the colored block viewed from above with a compact terminal building with floating pier extending into the harbour. Part of the boardwalk promenade. Keep surrounding context exactly as-is.",
        f"{BASE_NEGATIVE}, suburban, highway, parking lot, inland",
        make_variants("halifax_ferry_terminal", [
            ("historic_properties", "Adjacent to Historic Properties", "Heritage warehouse backdrop, Victorian-Italianate facades"),
            ("dartmouth_side", "Dartmouth Terminal", "Alderney Landing side, smaller scale, community waterfront"),
            ("evening", "Evening Crossing", "Warm terminal glow, harbour lights, Dartmouth skyline reflection"),
            ("future_electric", "Future Electric Ferry", "Net-zero terminal, electric catamaran visible, modern sustainable"),
        ]),
    ),
]

HALIFAX_STREETS = [
    make_street(
        "halifax_boardwalk", "Halifax Waterfront Boardwalk", "halifax_waterfront",
        "Canada's longest downtown boardwalk — 4km wooden promenade along Halifax Harbour with warehouses and harbour views",
        "Continuous 4km wooden/composite boardwalk along Halifax Harbour. Heavy timber deck sections. Heritage warehouse buildings (Historic Properties) on one side, harbour on the other. Cable railings. Public art ('The Wave' sculpture). Orange hammocks at Salter section. Ferry terminal. Transitions through multiple character areas. Maritime warehouses and modern buildings alternate.",
        "Heavy timber or composite deck boardwalk, cable railings at harbour edge",
        "Wind-resistant coastal plantings, some trees in protected locations",
        "Heritage warehouse buildings (Victorian-Italianate stone facades) on landward side, open harbour on water side",
        "Orange hammocks (iconic photo spot), public art, interpretive panels, cable railings, maritime heritage elements",
        ["halifax", "boardwalk", "waterfront", "harbour", "timber", "hammocks"],
        "Replace the colored zone with a photorealistic Halifax waterfront boardwalk. Heavy timber deck along harbour, heritage warehouse buildings on one side, harbour views to Dartmouth on the other. Orange hammocks, public art. Canada's longest downtown boardwalk. Maintain satellite context. Oblique aerial view, photorealistic, 8k",
        BASE_NEGATIVE,
        {"width": 5},
    ),
    make_street(
        "halifax_steep_street", "Halifax Steep Residential Street", "halifax_residential",
        "Steep residential street climbing from harbour to Citadel Hill with painted clapboard houses stepping up the slope",
        "Street climbing steeply from the waterfront toward Citadel Hill. Wooden clapboard houses in bright colours stepping up the slope. Stepped sidewalks in some locations. Views of the harbour between buildings. Stone retaining walls. Iron handrails. The steepness creates layered, visual density — rooftops cascade below.",
        "Asphalt with concrete or stone sidewalks, sometimes stepped, stone curbs",
        "Mature deciduous trees where slope allows, gardens in front yards",
        "Painted clapboard houses stepping up the hillside, stone retaining walls between lots",
        "Stone retaining walls, iron handrails on steep sections, harbour views between buildings at cross streets",
        ["halifax", "steep", "hillside", "clapboard", "harbour_views", "citadel"],
        "Replace the colored zone with a photorealistic Halifax steep residential street. Climbing from harbour toward Citadel Hill. Brightly painted clapboard houses stepping up the slope. Stone retaining walls. Harbour views between buildings. Maintain satellite context. Oblique aerial view, photorealistic, 8k",
        BASE_NEGATIVE,
        {"width": 13},
    ),
]

HALIFAX_PARKS = [
    make_park(
        "halifax_public_gardens", "Halifax Public Gardens", "halifax_victorian", "park",
        "One of the finest surviving Victorian gardens in North America with bandstand, carpet beds, serpentine paths, and wrought-iron gates",
        "16-acre National Historic Site. Founded 1836. Gardenesque landscape by Richard Power. Axially symmetrical plan. Serpentine paths. Geometric carpet beds (densely planted dwarf plants in contrasting colours). Bandstand (1887, Queen Victoria's Golden Jubilee). Three fountains. Two stone bridges. Three ponds. Wrought-iron gates. Mature deciduous trees. Commemorative statuary. Enclosed by iron fence — bounded, curated space.",
        "Serpentine gravel and stone paths in formal layout",
        "Geometric carpet beds with contrasting plants, mature deciduous trees, tropical display beds (Victorian tradition)",
        "Wrought-iron benches, bandstand (1887), commemorative statuary, stone bridges over ponds",
        "Three fountains, three ponds with stone bridges, formal water features",
        ["halifax", "public_gardens", "victorian", "bandstand", "carpet_beds", "national_historic"],
        "Replace the colored zone with a photorealistic Halifax Public Gardens. Victorian formal garden with geometric carpet beds, bandstand, serpentine paths, fountains, ponds with stone bridges, wrought-iron gates, mature trees. National Historic Site. Maintain satellite context. Oblique aerial view, photorealistic, 8k",
        BASE_NEGATIVE,
    ),
    make_park(
        "halifax_coastal_park", "Halifax Coastal Forest Park", "halifax_natural", "park",
        "Coastal forest park meeting the Atlantic Ocean with hiking trails, ruined fortifications, rocky shoreline, and salt-wind shaped trees",
        "Coastal forest park at the tip of the Halifax peninsula. Mixed forest meeting the Atlantic Ocean. Hiking trails through woods. Ruined stone fortifications (18th-century batteries and towers). Rocky shoreline. Salt spray and wind shape the vegetation. Wilder and more exposed character than urban parks. Regenerating forest (much lost to Hurricane Juan in 2003).",
        "Unpaved hiking trails through forest, some gravel paths",
        "Mixed coastal forest: spruce, birch, maple. Salt-wind shaped trees. Regenerating understory.",
        "Simple trail markers, wooden benches at viewpoints, interpretive panels at fortification ruins",
        "Atlantic Ocean at shoreline, tidal pools on rocky coast",
        ["halifax", "coastal", "forest", "fortifications", "atlantic", "point_pleasant"],
        "Replace the colored zone with a photorealistic Halifax coastal forest park. Forest meeting the Atlantic Ocean. Hiking trails. Ruined stone fortifications. Rocky shoreline. Salt-wind shaped trees. Wild, exposed character. Maintain satellite context. Oblique aerial view, photorealistic, 8k",
        BASE_NEGATIVE,
    ),
]


# ═══════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════

ALL_BUILDINGS = (MONTREAL_BUILDINGS + VANCOUVER_BUILDINGS + TORONTO_BUILDINGS +
                 CALGARY_BUILDINGS + HALIFAX_BUILDINGS)
ALL_STREETS = (MONTREAL_STREETS + VANCOUVER_STREETS + TORONTO_STREETS +
               CALGARY_STREETS + HALIFAX_STREETS)
ALL_PARKS = (MONTREAL_PARKS + VANCOUVER_PARKS + TORONTO_PARKS +
             CALGARY_PARKS + HALIFAX_PARKS)


def main():
    print(f"{'DRY RUN' if DRY_RUN else 'LIVE RUN'} — create_canadian_kits.py")
    print(f"{'=' * 50}")
    print(f"Buildings to add: {len(ALL_BUILDINGS)}")
    print(f"Streets to add:   {len(ALL_STREETS)}")
    print(f"Parks to add:     {len(ALL_PARKS)}")
    print(f"Total:            {len(ALL_BUILDINGS) + len(ALL_STREETS) + len(ALL_PARKS)}")
    print()

    # Buildings
    with open(BUILDING_FILE, encoding="utf-8") as f:
        bdata = json.load(f)
    existing_ids = {a["id"] for a in bdata["archetypes"]}
    new_buildings = [b for b in ALL_BUILDINGS if b["id"] not in existing_ids]
    skipped = len(ALL_BUILDINGS) - len(new_buildings)
    print(f"Buildings: {len(new_buildings)} new, {skipped} skipped (already exist)")
    if DRY_RUN:
        for b in new_buildings:
            print(f"  + {b['id']} — {b['title']}")
    else:
        bdata["archetypes"].extend(new_buildings)
        with open(BUILDING_FILE, "w", encoding="utf-8") as f:
            json.dump(bdata, f, indent=2, ensure_ascii=False)
            f.write("\n")
        print(f"  Written to {BUILDING_FILE}")

    # Streets
    with open(STREET_FILE, encoding="utf-8") as f:
        sdata = json.load(f)
    street_list = sdata.get("archetypes", sdata.get("streetTypes", []))
    existing_ids = {a["id"] for a in street_list}
    new_streets = [s for s in ALL_STREETS if s["id"] not in existing_ids]
    skipped = len(ALL_STREETS) - len(new_streets)
    print(f"Streets:   {len(new_streets)} new, {skipped} skipped")
    if DRY_RUN:
        for s in new_streets:
            print(f"  + {s['id']} — {s['title']}")
    else:
        street_list.extend(new_streets)
        if "archetypes" in sdata:
            sdata["archetypes"] = street_list
        else:
            sdata["streetTypes"] = street_list
        with open(STREET_FILE, "w", encoding="utf-8") as f:
            json.dump(sdata, f, indent=2, ensure_ascii=False)
            f.write("\n")
        print(f"  Written to {STREET_FILE}")

    # Parks
    with open(PARK_FILE, encoding="utf-8") as f:
        pdata = json.load(f)
    park_list = pdata.get("archetypes", pdata.get("openSpaceTypes", []))
    existing_ids = {a["id"] for a in park_list}
    new_parks = [p for p in ALL_PARKS if p["id"] not in existing_ids]
    skipped = len(ALL_PARKS) - len(new_parks)
    print(f"Parks:     {len(new_parks)} new, {skipped} skipped")
    if DRY_RUN:
        for p in new_parks:
            print(f"  + {p['id']} — {p['title']}")
    else:
        park_list.extend(new_parks)
        if "archetypes" in pdata:
            pdata["archetypes"] = park_list
        else:
            pdata["openSpaceTypes"] = park_list
        with open(PARK_FILE, "w", encoding="utf-8") as f:
            json.dump(pdata, f, indent=2, ensure_ascii=False)
            f.write("\n")
        print(f"  Written to {PARK_FILE}")

    print(f"\n{'=' * 50}")

    # Summary by city
    cities = {
        "Montreal": (MONTREAL_BUILDINGS, MONTREAL_STREETS, MONTREAL_PARKS),
        "Vancouver": (VANCOUVER_BUILDINGS, VANCOUVER_STREETS, VANCOUVER_PARKS),
        "Toronto": (TORONTO_BUILDINGS, TORONTO_STREETS, TORONTO_PARKS),
        "Calgary": (CALGARY_BUILDINGS, CALGARY_STREETS, CALGARY_PARKS),
        "Halifax": (HALIFAX_BUILDINGS, HALIFAX_STREETS, HALIFAX_PARKS),
    }
    print("\nPer-city breakdown:")
    for city, (b, s, p) in cities.items():
        print(f"  {city}: {len(b)} buildings, {len(s)} streets, {len(p)} parks = {len(b)+len(s)+len(p)} total")

    print("\nDone!")


if __name__ == "__main__":
    main()
