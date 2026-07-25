"""
Add 6 new street archetypes and 5 new park archetypes to their respective JSON files.
"""
import json
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_DATA_DIR = _PROJECT_ROOT / "frontend" / "src" / "data"

STREET_FILE = _DATA_DIR / "streetPathArchetypes.json"
PARK_FILE = _DATA_DIR / "openSpaceArchetypes.json"

NEW_STREETS = [
    {
        "id": "downtown_thoroughfare",
        "title": "Downtown Thoroughfare",
        "aestheticCategory": "auto_oriented",
        "description": "A wide 6-lane downtown street with transit service, lined by mid-rise commercial buildings with ground-floor retail, street trees in grates, and active sidewalks",
        "transportModes": ["walking", "transit", "automobile"],
        "volume": "high",
        "generationTags": ["downtown", "thoroughfare", "urban", "transit", "streets-pathways"],
        "styleProfile": {
            "corridorCharacter": "A wide downtown thoroughfare viewed from 3/4 aerial angle. Six travel lanes of dark asphalt with white lane markings. Concrete sidewalks with street trees in metal grates. 8-12 story commercial buildings with ground-floor retail and canvas awnings line both sides.",
            "movementHierarchy": "High-volume multi-modal — automobile, transit, walking",
            "surfaceType": "Dark asphalt with white lane markings, concrete sidewalks",
            "plantingCharacter": "Honey Locust trees in metal grates at regular intervals",
            "edgeConditions": "Ground-floor retail, canvas awnings, parallel parked cars",
            "publicRealm": "Active urban commercial corridor with transit service"
        },
        "prompt": {
            "subject": "Aerial view of a wide 6-lane downtown street with transit and commercial buildings",
            "details": [
                "Six lanes of dark asphalt with white lane markings",
                "Concrete sidewalks with street trees in metal grates",
                "8-12 story brick and limestone commercial buildings",
                "Ground-floor retail with canvas awnings",
                "Transit bus at shelter, parallel parked cars"
            ],
            "negative": ["No text overlays", "No unrealistic elements"]
        },
        "propertyPresets": {
            "mobility_profile": "auto_dominant",
            "transport_modes": ["walking", "transit", "automobile"],
            "width": 30,
            "lane_count": 6,
            "volume": "high",
            "road_surface": "asphalt",
            "sidewalks": "both",
            "has_sidewalks": True,
            "priority_pedestrian": 3,
            "priority_cycling": 4,
            "priority_transit": 2,
            "priority_auto": 1
        },
        "thumbnailUrl": "/archetypes/streets/downtown-thoroughfare/hero.png",
        "variants": [
            {"id": "downtown_thoroughfare_v0", "label": "American Downtown", "color": "#2C3E50", "description": "Downtown Thoroughfare in classic American city style. 6-lane road with parallel parking, transit shelters, brick and limestone buildings with ground-floor retail.", "thumbnailUrl": "/archetypes/streets/downtown-thoroughfare/variant_0.png"},
            {"id": "downtown_thoroughfare_v1", "label": "European Boulevard", "color": "#1A5276", "description": "Downtown Thoroughfare as grand European boulevard. Tram tracks in grass median, Haussmann buildings, cafe terraces under parasols.", "thumbnailUrl": "/archetypes/streets/downtown-thoroughfare/variant_1.png"},
            {"id": "downtown_thoroughfare_v2", "label": "Asian Urban", "color": "#6C3483", "description": "Downtown Thoroughfare in dense Asian city context. BRT station, glass towers with illuminated signage, elevated pedestrian bridge.", "thumbnailUrl": "/archetypes/streets/downtown-thoroughfare/variant_2.png"},
            {"id": "downtown_thoroughfare_v3", "label": "Complete Street", "color": "#1E8449", "description": "Downtown Thoroughfare as contemporary complete street. Planted median rain gardens, protected cycle track, bioretention planters, mixed-use buildings.", "thumbnailUrl": "/archetypes/streets/downtown-thoroughfare/variant_3.png"},
        ]
    },
    {
        "id": "pedestrian_only_street",
        "title": "Pedestrian-Only Street",
        "aestheticCategory": "pedestrian_oriented",
        "description": "A fully car-free pedestrian street with high-quality paving, street furniture, planting, and active ground-floor frontages for shopping and dining",
        "transportModes": ["walking"],
        "volume": "high",
        "generationTags": ["pedestrian", "car-free", "shopping", "promenade", "streets-pathways"],
        "styleProfile": {
            "corridorCharacter": "A fully pedestrian street viewed from 3/4 aerial angle. Full-width quality stone or concrete paving with no vehicle lanes. Ground-floor retail and cafe frontages with outdoor seating. Street furniture, planters, and public art. Lively human activity.",
            "movementHierarchy": "Pedestrian-only — no vehicle access",
            "surfaceType": "Granite sett paving, limestone, or high-quality concrete pavers",
            "plantingCharacter": "Street trees in planters, flower beds, seasonal planting",
            "edgeConditions": "Active ground-floor retail, cafe terraces, awnings",
            "publicRealm": "Premier pedestrian shopping and socializing environment"
        },
        "prompt": {
            "subject": "Aerial view of a pedestrian-only shopping street with quality paving and active frontages",
            "details": [
                "Full-width quality stone or concrete paving, no vehicle lanes",
                "Ground-floor retail and cafes with outdoor terraces",
                "Street furniture — benches, lamps, planters",
                "Trees and seasonal planting",
                "Fountain or public art focal point"
            ],
            "negative": ["No vehicles", "No road markings", "No text overlays"]
        },
        "propertyPresets": {
            "mobility_profile": "pedestrian",
            "transport_modes": ["walking"],
            "width": 15,
            "lane_count": 0,
            "volume": "high",
            "road_surface": "stone_paving",
            "sidewalks": "none",
            "has_sidewalks": False,
            "priority_pedestrian": 1,
            "priority_cycling": 3,
            "priority_transit": 4,
            "priority_auto": 4
        },
        "thumbnailUrl": "/archetypes/streets/pedestrian-only-street/hero.png",
        "variants": [
            {"id": "pedestrian_only_street_v0", "label": "Nordic Shopping Street", "color": "#5D6D7E", "description": "Pedestrian-Only Street in historic European style. Gray granite sett paving, painted facades, cast-iron lamps, flower planters, fountain focal point.", "thumbnailUrl": "/archetypes/streets/pedestrian-only-street/variant_0.png"},
            {"id": "pedestrian_only_street_v1", "label": "Mediterranean Promenade", "color": "#D4A017", "description": "Pedestrian-Only Street as Mediterranean promenade. Cream limestone paving, Plane trees, cafe terraces, ochre stucco buildings with bougainvillea.", "thumbnailUrl": "/archetypes/streets/pedestrian-only-street/variant_1.png"},
            {"id": "pedestrian_only_street_v2", "label": "Asian Night Market", "color": "#C0392B", "description": "Pedestrian-Only Street as Asian night market. Market stalls with colorful canopies, string lights and paper lanterns, dense signage, steam from food stalls.", "thumbnailUrl": "/archetypes/streets/pedestrian-only-street/variant_2.png"},
            {"id": "pedestrian_only_street_v3", "label": "Contemporary Redesign", "color": "#7D8B69", "description": "Pedestrian-Only Street with contemporary redesign. Concrete pavers, Corten planters with grasses, timber-slat benches, restored warehouses and new glass buildings.", "thumbnailUrl": "/archetypes/streets/pedestrian-only-street/variant_3.png"},
        ]
    },
    {
        "id": "green_alley",
        "title": "Green Alley",
        "aestheticCategory": "pedestrian_oriented",
        "description": "A residential alley retrofitted with permeable paving, bioswales, rain gardens, and native plantings for stormwater management and ecological habitat",
        "transportModes": ["walking", "automobile"],
        "volume": "very_low",
        "generationTags": ["alley", "green-infrastructure", "stormwater", "residential", "streets-pathways"],
        "styleProfile": {
            "corridorCharacter": "A residential green alley viewed from 3/4 aerial angle. Permeable paving replaces traditional asphalt. Bioswales and rain gardens line the edges. Native plantings and mature backyard trees overhang the alley.",
            "movementHierarchy": "Very low-speed shared access — walking and occasional automobile",
            "surfaceType": "Permeable concrete pavers or permeable asphalt",
            "plantingCharacter": "Bioswales with native sedges, rain gardens with wildflowers, overhanging backyard trees",
            "edgeConditions": "Wood privacy fences, rain barrels, garage entrances",
            "publicRealm": "Green infrastructure corridor in residential neighborhood"
        },
        "prompt": {
            "subject": "Aerial view of a green alley with permeable paving and bioswales",
            "details": [
                "Permeable concrete pavers or permeable asphalt surface",
                "Bioswales and rain gardens along edges",
                "Native wildflowers and sedges in stormwater features",
                "Mature trees overhanging from adjacent yards",
                "Wood privacy fences, residential character"
            ],
            "negative": ["No commercial signage", "No text overlays"]
        },
        "propertyPresets": {
            "mobility_profile": "balanced",
            "transport_modes": ["walking", "automobile"],
            "width": 5,
            "lane_count": 1,
            "volume": "very_low",
            "road_surface": "permeable_paving",
            "sidewalks": "none",
            "has_sidewalks": False,
            "priority_pedestrian": 1,
            "priority_cycling": 2,
            "priority_transit": 4,
            "priority_auto": 3
        },
        "thumbnailUrl": "/archetypes/streets/green-alley/hero.png",
        "variants": [
            {"id": "green_alley_v0", "label": "Chicago Permeable", "color": "#A3B86C", "description": "Green Alley in Chicago-style permeable paving. Cream herringbone pavers, wood fences, overhanging mature trees, LED lighting.", "thumbnailUrl": "/archetypes/streets/green-alley/variant_0.png"},
            {"id": "green_alley_v1", "label": "Bioswale Corridor", "color": "#3B7A57", "description": "Green Alley with continuous bioswale. Permeable asphalt with bioswale of sedges and iris, river cobble inlets, limestone check dams.", "thumbnailUrl": "/archetypes/streets/green-alley/variant_1.png"},
            {"id": "green_alley_v2", "label": "Rain Garden Cells", "color": "#DAA520", "description": "Green Alley with alternating rain garden cells. Central pavers flanked by rain gardens with Coneflower, Black-Eyed Susan, Little Bluestem.", "thumbnailUrl": "/archetypes/streets/green-alley/variant_2.png"},
            {"id": "green_alley_v3", "label": "Native Garden Path", "color": "#556B2F", "description": "Green Alley as heavily planted native garden path. Decomposed granite winding through Big Bluestem, Switchgrass, Wild Bergamot.", "thumbnailUrl": "/archetypes/streets/green-alley/variant_3.png"},
        ]
    },
    {
        "id": "commercial_alley_laneway",
        "title": "Commercial Alley / Laneway",
        "aestheticCategory": "pedestrian_oriented",
        "description": "A narrow commercial laneway activated with cafes, street art, pop-up vendors, or specialty retail in a compressed urban setting",
        "transportModes": ["walking"],
        "volume": "medium",
        "generationTags": ["alley", "laneway", "commercial", "cafe", "street-art", "streets-pathways"],
        "styleProfile": {
            "corridorCharacter": "A narrow commercial laneway viewed from 3/4 aerial angle. Tall brick or stone walls create an intimate passage. Ground-floor cafes and bars with tiny frontages. Overhead string lights. Street art and murals.",
            "movementHierarchy": "Pedestrian-only narrow passage",
            "surfaceType": "Bluestone flagstone, cobblestone, or worn concrete",
            "plantingCharacter": "Minimal — potted plants, window boxes, vine-covered walls",
            "edgeConditions": "Cafe counters, bar entrances, street art murals, fire escapes",
            "publicRealm": "Intimate activated urban passage with discovery character"
        },
        "prompt": {
            "subject": "Aerial view of a narrow commercial laneway with cafes and street art",
            "details": [
                "Narrow passage between tall brick or stone buildings",
                "Tiny cafe and bar frontages at ground level",
                "Overhead string lights and atmospheric lighting",
                "Street art murals on walls",
                "Quality stone or flagstone paving"
            ],
            "negative": ["No vehicles", "No text overlays"]
        },
        "propertyPresets": {
            "mobility_profile": "pedestrian",
            "transport_modes": ["walking"],
            "width": 4,
            "lane_count": 0,
            "volume": "medium",
            "road_surface": "stone_paving",
            "sidewalks": "none",
            "has_sidewalks": False,
            "priority_pedestrian": 1,
            "priority_cycling": 4,
            "priority_transit": 4,
            "priority_auto": 4
        },
        "thumbnailUrl": "/archetypes/streets/commercial-alley-laneway/hero.png",
        "variants": [
            {"id": "commercial_alley_laneway_v0", "label": "Melbourne Laneway", "color": "#B03A2E", "description": "Commercial Alley as Melbourne-style laneway. Brick warehouses with street art murals, bluestone paving, tiny cafe fronts, Edison-bulb string lights.", "thumbnailUrl": "/archetypes/streets/commercial-alley-laneway/variant_0.png"},
            {"id": "commercial_alley_laneway_v1", "label": "Tokyo Yokocho", "color": "#E74C3C", "description": "Commercial Alley as Tokyo yokocho drinking alley. Ultra-narrow passage with noren curtains, paper lanterns, counter seating, yakitori steam.", "thumbnailUrl": "/archetypes/streets/commercial-alley-laneway/variant_1.png"},
            {"id": "commercial_alley_laneway_v2", "label": "European Arcade", "color": "#D4AC0D", "description": "Commercial Alley as 19th-century European shopping passage. Glass barrel-vault roof, marble floor, ornate gilded shop fronts, brass lights.", "thumbnailUrl": "/archetypes/streets/commercial-alley-laneway/variant_2.png"},
            {"id": "commercial_alley_laneway_v3", "label": "Brooklyn Activated", "color": "#2980B9", "description": "Commercial Alley as Brooklyn-style activated alley. Painted asphalt mural, pop-up vendors, food truck, reclaimed wood tables, botanical mural.", "thumbnailUrl": "/archetypes/streets/commercial-alley-laneway/variant_3.png"},
        ]
    },
    {
        "id": "yield_street",
        "title": "Yield Street",
        "aestheticCategory": "auto_oriented",
        "description": "A narrow shared-surface street where vehicles must yield to oncoming traffic and pedestrians, with no curbs and integrated traffic-calming elements",
        "transportModes": ["walking", "cycling", "automobile"],
        "volume": "low",
        "generationTags": ["yield", "shared-space", "woonerf", "narrow", "residential", "streets-pathways"],
        "styleProfile": {
            "corridorCharacter": "A narrow yield street viewed from 3/4 aerial angle. Continuous surface paving with no curbs — vehicles share the space with pedestrians. Bollards and planters define the driving lane. Buildings front directly onto the street.",
            "movementHierarchy": "Low-speed shared space — pedestrians, cycling, automobile yielding",
            "surfaceType": "Clay brick pavers, cobblestone, or granite blocks — continuous surface, no curbs",
            "plantingCharacter": "Street trees creating canopy, planters as traffic calming",
            "edgeConditions": "Building facades directly abutting street, potted plants, bicycles",
            "publicRealm": "Intimate shared-use residential or historic street"
        },
        "prompt": {
            "subject": "Aerial view of a narrow yield street with shared surface and no curbs",
            "details": [
                "Continuous brick or stone paving with no curbs",
                "Bollards and planters defining driving lane",
                "Narrow enough that vehicles must yield to oncoming traffic",
                "Buildings fronting directly onto the street",
                "Bicycles, potted plants, street trees"
            ],
            "negative": ["No lane markings", "No traffic signals", "No text overlays"]
        },
        "propertyPresets": {
            "mobility_profile": "balanced",
            "transport_modes": ["walking", "cycling", "automobile"],
            "width": 6,
            "lane_count": 1,
            "volume": "low",
            "road_surface": "brick_paving",
            "sidewalks": "none",
            "has_sidewalks": False,
            "priority_pedestrian": 1,
            "priority_cycling": 2,
            "priority_transit": 4,
            "priority_auto": 3
        },
        "thumbnailUrl": "/archetypes/streets/yield-street/hero.png",
        "variants": [
            {"id": "yield_street_v0", "label": "Dutch Woonerf", "color": "#A04000", "description": "Yield Street as Dutch woonerf. Red-brown clay brick herringbone pavers, bollards and Hydrangea planters, brick rowhouses with stepped gables.", "thumbnailUrl": "/archetypes/streets/yield-street/variant_0.png"},
            {"id": "yield_street_v1", "label": "New England Historic", "color": "#6E2C00", "description": "Yield Street as historic New England street. Worn brick paving, Federal-style rowhouses, gas-lamp lights, mature Elm canopy.", "thumbnailUrl": "/archetypes/streets/yield-street/variant_1.png"},
            {"id": "yield_street_v2", "label": "Japanese Residential", "color": "#707B7C", "description": "Yield Street as narrow Japanese residential alley. 3m gray asphalt, traditional houses with tile roofs, potted plants, utility poles, immaculately clean.", "thumbnailUrl": "/archetypes/streets/yield-street/variant_2.png"},
            {"id": "yield_street_v3", "label": "Scandinavian Shared", "color": "#839192", "description": "Yield Street as Scandinavian shared-space. Gray granite pavers, Corten planters with grasses and Birch chicanes, timber-clad houses with green roofs.", "thumbnailUrl": "/archetypes/streets/yield-street/variant_3.png"},
        ]
    },
    {
        "id": "neighborhood_main_street",
        "title": "Neighborhood Main Street",
        "aestheticCategory": "pedestrian_oriented",
        "description": "A traditional neighborhood commercial street with two travel lanes, on-street parking, wide sidewalks, and 2-3 story mixed-use buildings with active retail",
        "transportModes": ["walking", "cycling", "automobile"],
        "volume": "medium",
        "generationTags": ["main-street", "neighborhood", "commercial", "retail", "streets-pathways"],
        "styleProfile": {
            "corridorCharacter": "A neighborhood main street viewed from 3/4 aerial angle. Two travel lanes with on-street parking — diagonal or parallel. Wide sidewalks with street trees and pedestrian amenities. 2-3 story mixed-use buildings with ground-floor retail.",
            "movementHierarchy": "Medium-speed local commercial — walking, cycling, automobile",
            "surfaceType": "Asphalt roadway, concrete or brick sidewalks",
            "plantingCharacter": "Street trees in tree wells or planting strips, flower baskets on lamp posts",
            "edgeConditions": "Ground-floor retail with awnings and blade signs, wide sidewalks, on-street parking",
            "publicRealm": "Active neighborhood commercial and social corridor"
        },
        "prompt": {
            "subject": "Aerial view of a neighborhood main street with shops and on-street parking",
            "details": [
                "Two-lane road with diagonal or parallel parking",
                "2-3 story mixed-use commercial buildings",
                "Ground-floor retail with awnings and signage",
                "Wide sidewalks with street trees and lamp posts",
                "Flower baskets, benches, pedestrian amenities"
            ],
            "negative": ["No text overlays", "No unrealistic elements"]
        },
        "propertyPresets": {
            "mobility_profile": "balanced",
            "transport_modes": ["walking", "cycling", "automobile"],
            "width": 16,
            "lane_count": 2,
            "volume": "medium",
            "road_surface": "asphalt",
            "sidewalks": "both",
            "has_sidewalks": True,
            "priority_pedestrian": 1,
            "priority_cycling": 3,
            "priority_transit": 3,
            "priority_auto": 2
        },
        "thumbnailUrl": "/archetypes/streets/neighborhood-main-street/hero.png",
        "variants": [
            {"id": "neighborhood_main_street_v0", "label": "Small-Town American", "color": "#922B21", "description": "Neighborhood Main Street in small-town American style. Red and cream brick buildings, pressed-metal cornices, canvas awnings, diagonal parking, flower basket lamp posts.", "thumbnailUrl": "/archetypes/streets/neighborhood-main-street/variant_0.png"},
            {"id": "neighborhood_main_street_v1", "label": "English High Street", "color": "#7B7D3E", "description": "Neighborhood Main Street as English Victorian high street. Cotswold stone and brick buildings, sash windows, York stone sidewalks, cast-iron lamp posts, red pillar box.", "thumbnailUrl": "/archetypes/streets/neighborhood-main-street/variant_1.png"},
            {"id": "neighborhood_main_street_v2", "label": "Mediterranean Village", "color": "#CA6F1E", "description": "Neighborhood Main Street as Mediterranean village street. White and ochre stucco with barrel-tile roofs, wrought-iron balconies, bougainvillea, sandstone paving.", "thumbnailUrl": "/archetypes/streets/neighborhood-main-street/variant_2.png"},
            {"id": "neighborhood_main_street_v3", "label": "Contemporary Urban", "color": "#2471A3", "description": "Neighborhood Main Street with contemporary design. Protected bike lane, rain garden tree trenches, mixed-use with NanaWall storefronts, modern steel furniture.", "thumbnailUrl": "/archetypes/streets/neighborhood-main-street/variant_3.png"},
        ]
    },
]

NEW_PARKS = [
    {
        "id": "linear_park_greenway",
        "title": "Linear Park / Greenway",
        "aestheticCategory": "ecological_resilience",
        "spaceType": "park",
        "description": "A narrow linear park following a former rail corridor, creek, or utility easement, with multi-use trails, native plantings, and ecological restoration",
        "generationTags": ["linear-park", "greenway", "trail", "ecological", "corridor"],
        "styleProfile": {
            "landscapeCharacter": "A linear park or greenway viewed from 3/4 aerial angle. A paved multi-use trail follows a narrow corridor — a former rail line, creek, or utility easement. Native wildflower meadows and riparian plantings flank the path. Bridges, overlooks, and interpretive signage.",
            "pavingType": "Asphalt or crushed limestone multi-use trail",
            "plantingType": "Native wildflower meadows, riparian buffer plantings, shade trees",
            "seatingRealm": "Railroad-tie benches, timber overlook platforms",
            "waterFeatures": "Creek, river, or stormwater features",
            "opennessEnclosure": "Linear corridor framed by vegetation and adjacent development"
        },
        "prompt": {
            "subject": "Aerial view of a linear park greenway along a former rail or creek corridor",
            "details": [
                "Multi-use asphalt or gravel trail along narrow corridor",
                "Native wildflower meadows flanking the trail",
                "Shade trees and riparian plantings",
                "Bridges, overlooks, and interpretive signage",
                "Cyclists, joggers, and walkers on path"
            ],
            "negative": ["No vehicles", "No text overlays"]
        },
        "propertyPresets": {
            "tree_density_level": "medium",
            "tree_density": 0.4,
            "has_paths": True,
            "has_benches": True,
            "shade_strategy": "riparian_canopy"
        },
        "thumbnailUrl": "/archetypes/openspaces/linear-park-greenway/hero.png",
        "variants": [
            {"id": "linear_park_greenway_v0", "label": "Rail Trail", "color": "#8B4513", "description": "Linear Park as rail trail. Asphalt path along former rail corridor, preserved tracks, wildflower meadow banks, railroad-tie benches, steel truss bridge.", "thumbnailUrl": "/archetypes/openspaces/linear-park-greenway/variant_0.png"},
            {"id": "linear_park_greenway_v1", "label": "Riverfront Greenway", "color": "#1B4F72", "description": "Linear Park as riverfront greenway. Concrete path along river, cantilevered overlook platforms, Weeping Willows, lawn terraces, kayak launch.", "thumbnailUrl": "/archetypes/openspaces/linear-park-greenway/variant_1.png"},
            {"id": "linear_park_greenway_v2", "label": "Daylighted Creek", "color": "#196F3D", "description": "Linear Park as daylighted creek restoration. Meandering creek with riffles and weirs, boardwalk over wetland, rain garden bioretention.", "thumbnailUrl": "/archetypes/openspaces/linear-park-greenway/variant_2.png"},
            {"id": "linear_park_greenway_v3", "label": "Elevated Viaduct", "color": "#6E2C00", "description": "Linear Park as elevated park on repurposed rail viaduct. Corten steel viaduct, concrete plank paving with grasses, preserved rail tracks, cantilevered viewing platform.", "thumbnailUrl": "/archetypes/openspaces/linear-park-greenway/variant_3.png"},
        ]
    },
    {
        "id": "nature_preserve",
        "title": "Nature Preserve",
        "aestheticCategory": "ecological_resilience",
        "spaceType": "park",
        "description": "A protected natural area with minimal development — boardwalks, observation platforms, and interpretive signage through wetland, prairie, dune, or forest ecosystems",
        "generationTags": ["nature", "preserve", "wetland", "prairie", "ecological", "conservation"],
        "styleProfile": {
            "landscapeCharacter": "A nature preserve viewed from 3/4 aerial angle. Undisturbed natural ecosystem with minimal built intervention. Narrow boardwalks and trails thread through wetland, prairie, dunes, or forest. Observation platforms and interpretive panels.",
            "pavingType": "Timber boardwalk, crushed stone trail, or mown path",
            "plantingType": "Native ecosystem — wetland marsh, tallgrass prairie, coastal dune, or old-growth forest",
            "seatingRealm": "Observation platforms, minimal benches at trailheads",
            "waterFeatures": "Natural — marsh water, creek, or ocean",
            "opennessEnclosure": "Open natural landscape with horizon views or enclosed forest canopy"
        },
        "prompt": {
            "subject": "Aerial view of a nature preserve with boardwalk and native ecosystems",
            "details": [
                "Undisturbed natural ecosystem — wetland, prairie, dunes, or forest",
                "Narrow timber boardwalk or crushed-stone trail",
                "Observation platform with interpretive panels",
                "Native wildlife and plantings",
                "Minimal built intervention"
            ],
            "negative": ["No vehicles", "No commercial development", "No text overlays"]
        },
        "propertyPresets": {
            "tree_density_level": "varies",
            "tree_density": 0.6,
            "has_paths": True,
            "has_benches": False,
            "shade_strategy": "natural_canopy"
        },
        "thumbnailUrl": "/archetypes/openspaces/nature-preserve/hero.png",
        "variants": [
            {"id": "nature_preserve_v0", "label": "Wetland Boardwalk", "color": "#1A5276", "description": "Nature Preserve as wetland with timber boardwalk through Cattails and Reed, observation platform, Bald Cypress, Great Blue Heron.", "thumbnailUrl": "/archetypes/openspaces/nature-preserve/variant_0.png"},
            {"id": "nature_preserve_v1", "label": "Tallgrass Prairie", "color": "#B7950B", "description": "Nature Preserve as tallgrass prairie reserve. Mown trail through Big Bluestem and Indian Grass, wildflowers, timber observation platform, Bur Oak savanna.", "thumbnailUrl": "/archetypes/openspaces/nature-preserve/variant_1.png"},
            {"id": "nature_preserve_v2", "label": "Coastal Dune", "color": "#D4AC0D", "description": "Nature Preserve as coastal dune conservation. Timber boardwalk through sand dunes with Beach Grass, sand fencing, Piping Plover nesting zone, ocean views.", "thumbnailUrl": "/archetypes/openspaces/nature-preserve/variant_2.png"},
            {"id": "nature_preserve_v3", "label": "Old-Growth Forest", "color": "#1B4F72", "description": "Nature Preserve as old-growth forest trail. Massive tree trunks, moss-covered logs, sword ferns, boardwalk over wet area, cathedral-like dappled light.", "thumbnailUrl": "/archetypes/openspaces/nature-preserve/variant_3.png"},
        ]
    },
    {
        "id": "rooftop_garden",
        "title": "Rooftop Garden",
        "aestheticCategory": "neighborhood_public_realm",
        "spaceType": "park",
        "description": "A rooftop open space atop a building — ranging from intensive gardens with trees and lawns to extensive green roofs, urban farms, or social terraces",
        "generationTags": ["rooftop", "garden", "green-roof", "urban-farm", "terrace"],
        "styleProfile": {
            "landscapeCharacter": "A rooftop garden or green roof viewed from 3/4 aerial angle atop a multi-story building. Planted beds, seating areas, and amenities set against a city skyline backdrop. Glass railings at building edge.",
            "pavingType": "Ipe deck, porcelain tile, or concrete pavers",
            "plantingType": "Intensive planting beds with trees and shrubs, or extensive sedum carpet",
            "seatingRealm": "Lounge furniture, built-in benches, dining areas",
            "waterFeatures": "Reflecting pool or fountain",
            "opennessEnclosure": "Open sky exposure with city views, glass railings at edges"
        },
        "prompt": {
            "subject": "Aerial view of a rooftop garden atop a multi-story building",
            "details": [
                "Planted beds with trees, shrubs, or sedum on rooftop",
                "Deck or paving with seating areas",
                "Glass railings with city views beyond",
                "Pergola or shade structure",
                "Green contrast against urban context"
            ],
            "negative": ["No text overlays"]
        },
        "propertyPresets": {
            "tree_density_level": "low",
            "tree_density": 0.2,
            "has_paths": True,
            "has_benches": True,
            "shade_strategy": "pergola_structure"
        },
        "thumbnailUrl": "/archetypes/openspaces/rooftop-garden/hero.png",
        "variants": [
            {"id": "rooftop_garden_v0", "label": "Intensive Garden", "color": "#27AE60", "description": "Rooftop Garden as lush intensive garden. Japanese Maple, Birch, Hydrangeas, cedar pergola with Wisteria, reflecting pool, ipe deck lounge, lawn panel.", "thumbnailUrl": "/archetypes/openspaces/rooftop-garden/variant_0.png"},
            {"id": "rooftop_garden_v1", "label": "Sedum Green Roof", "color": "#82E0AA", "description": "Rooftop Garden as extensive sedum green roof. Patchwork carpet of silver-green, red, yellow-green Sedum, modular trays, maintenance path, screened HVAC.", "thumbnailUrl": "/archetypes/openspaces/rooftop-garden/variant_1.png"},
            {"id": "rooftop_garden_v2", "label": "Urban Farm", "color": "#7D6608", "description": "Rooftop Garden as urban farm. Galvanized raised beds with vegetables, row covers, drip irrigation, timber greenhouse, composting bins, city skyline.", "thumbnailUrl": "/archetypes/openspaces/rooftop-garden/variant_2.png"},
            {"id": "rooftop_garden_v3", "label": "Social Terrace", "color": "#4A235A", "description": "Rooftop Garden as social space and bar at blue hour. Porcelain paving, fire table, bar structure, Edison-bulb lights, Corten planters, wicker lounge, panoramic skyline.", "thumbnailUrl": "/archetypes/openspaces/rooftop-garden/variant_3.png"},
        ]
    },
    {
        "id": "riverfront_park_beach",
        "title": "Riverfront Park / Beach",
        "aestheticCategory": "waterfront_spaces",
        "spaceType": "park",
        "description": "A waterfront park with beach, swimming, and recreation along a river or lake — combining sand, water access, promenades, and naturalized shoreline",
        "generationTags": ["waterfront", "beach", "river", "lake", "swimming", "recreation"],
        "styleProfile": {
            "landscapeCharacter": "A riverfront or lakefront park with beach viewed from 3/4 aerial angle. Sand beach area along water with stepped terraces, promenades, and recreation facilities. Trees and native plantings at the upland edge.",
            "pavingType": "Timber deck promenade, concrete terraces, sand beach",
            "plantingType": "Plane trees along promenade, native shoreline plantings, riparian buffer",
            "seatingRealm": "Deck chairs, parasols, picnic areas, timber platforms",
            "waterFeatures": "River, lake, or swimming zone with buoys",
            "opennessEnclosure": "Open water views with tree-framed upland edge"
        },
        "prompt": {
            "subject": "Aerial view of a riverfront park with beach and swimming area",
            "details": [
                "Sand beach along river or lake",
                "Stepped concrete terraces or timber promenade above",
                "Parasols, deck chairs, beach volleyball",
                "Trees and native plantings at upland edge",
                "People swimming, sunbathing, kayaking"
            ],
            "negative": ["No text overlays"]
        },
        "propertyPresets": {
            "tree_density_level": "low",
            "tree_density": 0.3,
            "has_paths": True,
            "has_benches": True,
            "shade_strategy": "canopy_trees"
        },
        "thumbnailUrl": "/archetypes/openspaces/riverfront-park-beach/hero.png",
        "variants": [
            {"id": "riverfront_park_beach_v0", "label": "Urban River Beach", "color": "#E67E22", "description": "Riverfront Park as urban river beach. Golden sand, concrete terraces, striped parasols, beach volleyball, timber promenade with cafe kiosks.", "thumbnailUrl": "/archetypes/openspaces/riverfront-park-beach/variant_0.png"},
            {"id": "riverfront_park_beach_v1", "label": "Lake Swimming Beach", "color": "#2E86C1", "description": "Riverfront Park as lake swimming beach. Crescent sand beach, turquoise water, swimming dock, cedar bathhouse, kayaks on rack.", "thumbnailUrl": "/archetypes/openspaces/riverfront-park-beach/variant_1.png"},
            {"id": "riverfront_park_beach_v2", "label": "Adventure Pier", "color": "#C0392B", "description": "Riverfront Park as waterfront adventure park on former industrial pier. Kayak launch, climbing wall, adventure playground, splash pad, gabion walls.", "thumbnailUrl": "/archetypes/openspaces/riverfront-park-beach/variant_2.png"},
            {"id": "riverfront_park_beach_v3", "label": "Naturalized Riverfront", "color": "#1E8449", "description": "Riverfront Park as naturalized ecological riverfront. Bio-engineered bank, wet meadow with sedges and Iris, Sycamores, observation platform, water lilies.", "thumbnailUrl": "/archetypes/openspaces/riverfront-park-beach/variant_3.png"},
        ]
    },
    {
        "id": "street_plaza_parklet",
        "title": "Street Plaza / Parklet",
        "aestheticCategory": "civic_plazas",
        "spaceType": "park",
        "description": "A small public space created by reclaiming street or parking space — from painted plazas with bistro furniture to timber parklets extending the sidewalk",
        "generationTags": ["plaza", "parklet", "tactical-urbanism", "street-reclamation", "public-space"],
        "styleProfile": {
            "landscapeCharacter": "A street plaza or parklet viewed from 3/4 aerial angle. Former roadway or parking spaces converted to public gathering space with seating, planters, and surface treatment. Adjacent buildings and street context visible.",
            "pavingType": "Painted asphalt, timber deck, or granite pavers",
            "plantingType": "Planters with small trees, potted plants, container gardens",
            "seatingRealm": "Bistro tables and chairs, benches, Adirondack chairs",
            "waterFeatures": "Small fountain or bubbler if formal design",
            "opennessEnclosure": "Open to street with bollards or planters defining edge"
        },
        "prompt": {
            "subject": "Aerial view of a street plaza or parklet reclaimed from roadway",
            "details": [
                "Former roadway or parking spaces converted to public space",
                "Bistro tables, chairs, and seating",
                "Planters with small trees and container gardens",
                "Bollards or barriers defining the space",
                "Adjacent building frontages and street context"
            ],
            "negative": ["No text overlays"]
        },
        "propertyPresets": {
            "tree_density_level": "low",
            "tree_density": 0.2,
            "has_paths": False,
            "has_benches": True,
            "shade_strategy": "parasols_canopies"
        },
        "thumbnailUrl": "/archetypes/openspaces/street-plaza-parklet/hero.png",
        "variants": [
            {"id": "street_plaza_parklet_v0", "label": "NYC Street Plaza", "color": "#F1C40F", "description": "Street Plaza as NYC-style painted plaza. Bold yellow geometric paint pattern, yellow bistro chairs, black planter boxes, granite bollards.", "thumbnailUrl": "/archetypes/openspaces/street-plaza-parklet/variant_0.png"},
            {"id": "street_plaza_parklet_v1", "label": "SF Parklet", "color": "#AF601A", "description": "Street Plaza as San Francisco timber parklet. Douglas fir deck, timber slat railing, terracotta pots with herbs, cafe tables, chalkboard menu.", "thumbnailUrl": "/archetypes/openspaces/street-plaza-parklet/variant_1.png"},
            {"id": "street_plaza_parklet_v2", "label": "Tactical Urbanism", "color": "#E74C3C", "description": "Street Plaza as tactical urbanism community plaza. Spray-painted mural, painted jersey barriers, colorful Adirondack chairs, tire planters, string lights.", "thumbnailUrl": "/archetypes/openspaces/street-plaza-parklet/variant_2.png"},
            {"id": "street_plaza_parklet_v3", "label": "European Pocket Plaza", "color": "#5B6F6F", "description": "Street Plaza as refined European pocket plaza. Gray granite pavers, Corten planters with Amelanchier, bubbler fountain, cast-aluminum benches, cafe terrace.", "thumbnailUrl": "/archetypes/openspaces/street-plaza-parklet/variant_3.png"},
        ]
    },
]


def main():
    # Update streets JSON
    with open(STREET_FILE, "r", encoding="utf-8") as f:
        streets_data = json.load(f)

    existing_ids = {a["id"] for a in streets_data["archetypes"]}
    added_streets = 0
    for arch in NEW_STREETS:
        if arch["id"] not in existing_ids:
            streets_data["archetypes"].append(arch)
            added_streets += 1
            print(f"  Added street: {arch['id']}")
        else:
            print(f"  SKIP (exists): {arch['id']}")

    with open(STREET_FILE, "w", encoding="utf-8") as f:
        json.dump(streets_data, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"Updated {STREET_FILE.name}: added {added_streets} archetypes\n")

    # Update parks JSON
    with open(PARK_FILE, "r", encoding="utf-8") as f:
        parks_data = json.load(f)

    existing_ids = {a["id"] for a in parks_data["archetypes"]}
    added_parks = 0
    for arch in NEW_PARKS:
        if arch["id"] not in existing_ids:
            parks_data["archetypes"].append(arch)
            added_parks += 1
            print(f"  Added park: {arch['id']}")
        else:
            print(f"  SKIP (exists): {arch['id']}")

    with open(PARK_FILE, "w", encoding="utf-8") as f:
        json.dump(parks_data, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"Updated {PARK_FILE.name}: added {added_parks} archetypes")


if __name__ == "__main__":
    main()
