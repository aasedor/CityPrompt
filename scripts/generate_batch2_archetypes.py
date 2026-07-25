"""
Generate batch 2 archetype images: Industrial General, Heavy, Warehouse, Recreational.
Uses Gemini 3 Pro Image API.
"""

from __future__ import annotations
import base64, io, json, sys, time, argparse
from pathlib import Path
import httpx
from PIL import Image

_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SCRIPT_DIR.parent
_ENV_FILE = _PROJECT_ROOT / "backend" / ".env"
_PUBLIC_DIR = _PROJECT_ROOT / "frontend" / "public" / "archetypes"
_DATA_DIR = _PROJECT_ROOT / "frontend" / "src" / "data"
CARD_WIDTH, CARD_HEIGHT = 1024, 768

def _load_api_key():
    for line in _ENV_FILE.read_text().splitlines():
        if line.strip().startswith("GEMINI_API_KEY="):
            return line.strip().split("=", 1)[1].strip()
    sys.exit("ERROR: GEMINI_API_KEY not found")

API_KEY = _load_api_key()
MODEL = "gemini-3-pro-image-preview"
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={API_KEY}"

STYLE_ANCHOR = (
    "Style: photorealistic architectural visualization, high-end 3D rendering "
    "quality like a professional archviz studio. Warm golden-hour afternoon "
    "sunlight from the left at roughly 45 degrees, casting soft natural shadows. "
    "Slightly hazy atmospheric perspective in the background. Natural color "
    "grading with warm tones. Sharp detail on materials and textures. "
    "Photorealistic, 8K detail, architectural photography composition."
)
NO_PEOPLE = (
    "Absolutely no people, no human figures, no pedestrians, no silhouettes, "
    "no crowds anywhere in the scene. The scene is completely empty of humans."
)
BUILDING_FRAME = (
    "Photorealistic architectural visualization. "
    "Street-level perspective from across the street, approximately 25 meters away, "
    "at a 3/4 angle showing two facades. The full building is visible from ground "
    "to roofline with some sky above and street/sidewalk below. "
)

ALL_ARCHETYPES = {

# ============================================================
# INDUSTRIAL: GENERAL
# ============================================================
"functionalist_brick_industrial": {
    "id": "functionalist_brick_industrial",
    "title": "Functionalist Brick Industrial",
    "description": "Traditional brick industrial building with honest structural expression, utilitarian design, and robust load-bearing masonry construction",
    "developmentType": "industrial",
    "buildingSubcategory": "General Industrial",
    "aestheticCategory": "functionalist_brick",
    "minFloors": 2, "maxFloors": 6, "suggestedAreaSqm": 8000, "shadeId": "#8B4513",
    "facadeDetail": {
        "primaryMaterial": "dark red-brown engineering brick in English bond",
        "secondaryMaterial": "cast iron columns and beams visible through windows",
        "accentMaterial": "stone lintels, cast iron rainwater goods",
        "groundFloor": "large arched openings for goods and vehicle access",
        "upperFloors": "tall multi-pane steel-sash windows between brick piers",
        "cornice": "corbelled brick cornice with dentil course",
        "colorScheme": "dark red-brown brick, dark steel, stone accents"
    },
    "roofDetail": {"form": "low-pitched gable or flat with saw-tooth monitors", "material": "slate or corrugated iron", "features": "brick chimneys, ventilators, loading cranes", "aerialAppearance": "dark slate with brick chimneys and ventilator cowls"},
    "variants": [
        {"id": "brick_corbelled_utility", "label": "Corbelled Brick Utility",
         "description": "Utilitarian brick building with decorative corbelled brickwork courses, arched windows, and prominent chimney stacks for industrial processes.",
         "prompt": "Corbelled brick utility building. Multi-story dark red engineering brick industrial building with elaborate decorative corbelled brick courses creating shadow patterns at the roofline and between floors. Tall semi-circular arched windows with stone keystones and radiating brick voussoirs. Prominent octagonal brick chimney stack rising from the rear. Brick buttresses between window bays adding structural rhythm. Cast iron rainwater downpipes with ornate hopper heads. Loading doorways with timber doors and iron lifting beams above. Cobblestone yard in foreground. Inspired by Victorian-era waterworks, pumping stations, and gas works.",
         "facadeDetail": {"primaryMaterial": "dark red engineering brick with corbelled courses", "secondaryMaterial": "stone keystones, arched window heads", "groundFloor": "loading doorways with timber doors and iron lifting beams", "colorScheme": "dark red brick, grey stone, black ironwork"},
         "roofDetail": {"form": "low-pitched gable with corbelled brick eaves", "material": "slate with prominent chimney stack"}, "palette": {"primary": "#7B3B2A"}},
        {"id": "brick_multistory_mill", "label": "Multi-story Mill",
         "description": "Tall multi-story brick mill with cast iron frame, massive window areas, and slow-burning timber floor construction. The archetypal industrial revolution factory.",
         "prompt": "Multi-story brick mill building. Tall six-story dark red brick industrial building with an internal cast iron structural frame. Massive window areas: the facade is more glass than brick, with tall steel-sash multi-pane windows stacked between narrow brick piers from ground to roof. Segmental brick arches over each window tier. Stone plinth and stone band courses between floors. Engine house bay projecting at one end with an arched window. Loading lucam (hoisting bay) projecting from the top floor with a crane beam. Brick stair tower with arched windows. Inspired by Quarry Bank Mill and Saltaire mills.",
         "facadeDetail": {"primaryMaterial": "dark red brick with narrow piers between huge windows", "secondaryMaterial": "cast iron frame visible, stone band courses", "groundFloor": "arched entrance, loading bays", "colorScheme": "dark red brick, stone grey bands, vast glass areas"},
         "roofDetail": {"form": "low-pitched gable with stone coping", "material": "slate"}, "palette": {"primary": "#6B3A2A"}},
        {"id": "brick_courtyard_factory", "label": "Courtyard Factory",
         "description": "U-shaped or courtyard-plan brick factory with a central yard for goods handling, surrounded by workshop wings with large windows.",
         "prompt": "Courtyard factory complex. U-shaped red brick industrial complex organized around a central cobblestone goods yard. Main range facing the street is three stories with tall arched windows and a central clock tower gateway. Side wings are two stories with continuous steel-sash industrial glazing. Covered loading canopy of cast iron columns and corrugated iron roof along one side of the yard. Vehicle entrance arch through the main range with heavy timber gates. Brick boundary walls with cast iron railings. Each wing has its own brick chimney. Office wing distinguished by larger windows with stone surrounds. Inspired by British Victorian factories and Boulton & Watt's Soho Manufactory.",
         "facadeDetail": {"primaryMaterial": "red brick with arched windows and clock tower", "secondaryMaterial": "cast iron loading canopy, stone window surrounds on office wing", "groundFloor": "arched gateway entrance, loading bays with canopy", "colorScheme": "red brick, grey stone, dark iron, cobblestone yard"},
         "roofDetail": {"form": "gabled wings with central clock tower", "material": "slate with decorative ridge tiles"}, "palette": {"primary": "#8B4513"}},
        {"id": "brick_chimney_centric", "label": "Chimney-Centric",
         "description": "Industrial building dominated by a monumental brick chimney stack, typical of power stations, kilns, and heavy manufacturing where the chimney is the primary architectural feature.",
         "prompt": "Chimney-centric industrial building. Low brick industrial building dominated by a massive ornamental brick chimney stack rising to 40 meters. The chimney features decorative corbelled brick bands, an octagonal top section, and a flared cap. The associated building is a single-story engine house with very tall arched windows (to accommodate machinery inside) with stone surrounds and iron frames. Buttressed brick walls. Secondary smaller chimneys visible. Brick boundary wall with cast iron gates. Rail tracks running to loading doors. The chimney is the building's defining silhouette and architectural statement. Inspired by Victorian brewery chimneys, pottery kilns, and pumping station chimneys.",
         "facadeDetail": {"primaryMaterial": "red brick with monumental chimney stack", "secondaryMaterial": "tall arched engine-house windows with stone surrounds", "groundFloor": "large arched openings for machinery, rail access doors", "colorScheme": "red brick, stone arches, black iron, decorative chimney bands"},
         "roofDetail": {"form": "low gable on engine house, massive chimney dominates", "material": "slate on building, ornamental brick on chimney"}, "palette": {"primary": "#704214"}}
    ]
},

"structural_expressionism_industrial": {
    "id": "structural_expressionism_industrial",
    "title": "Structural Expressionism Industrial",
    "description": "Industrial building where the structural system is the primary architectural expression, celebrating engineering through exposed trusses, spans, and tension systems",
    "developmentType": "industrial",
    "buildingSubcategory": "General Industrial",
    "aestheticCategory": "structural_expressionism",
    "minFloors": 1, "maxFloors": 2, "suggestedAreaSqm": 6000, "shadeId": "#4682B4",
    "facadeDetail": {
        "primaryMaterial": "exposed steel structural frame with metal or glass cladding",
        "secondaryMaterial": "steel tension cables, exposed connections and nodes",
        "accentMaterial": "galvanized steel, aluminum secondary structure",
        "groundFloor": "open clear-span space visible through glazing",
        "upperFloors": "mezzanine level with exposed steel walkways",
        "cornice": "exposed steel truss profile forming the roofline",
        "colorScheme": "silver steel, glass, galvanized metal"
    },
    "roofDetail": {"form": "dramatic long-span truss or cable structure", "material": "standing-seam metal or ETFE", "features": "exposed trusses visible from exterior, cable stays", "aerialAppearance": "dramatic structural form with visible truss geometry"},
    "variants": [
        {"id": "industrial_bowstring_truss", "label": "Bow-string Truss",
         "description": "Industrial building with elegant curved bow-string trusses creating a distinctive arched roofline, combining structural efficiency with visual grace.",
         "prompt": "Bow-string truss industrial building. Wide-span single-story building with a row of elegant curved bow-string steel trusses forming an arched roof profile. The trusses are exposed on the exterior at the gable ends showing the curved top chord and straight bottom chord connected by vertical and diagonal web members. Full-height glass curtain walls at the gable ends revealing the truss structure inside. Side walls of corrugated metal with clerestory windows between truss bays. Each truss bay is expressed on the exterior as a subtle structural rhythm. Painted steel structure in industrial red-oxide primer. Concrete plinth base. Inspired by 19th-century railway goods sheds and industrial arcades.",
         "facadeDetail": {"primaryMaterial": "exposed curved bow-string steel trusses at gable ends", "secondaryMaterial": "glass curtain wall gables, corrugated metal side walls", "groundFloor": "glass gable end revealing truss structure, large sliding doors", "colorScheme": "red-oxide painted steel, silver corrugated metal, glass gable"},
         "roofDetail": {"form": "curved bow-string truss creating arched profile", "material": "standing-seam metal over curved trusses"}, "palette": {"primary": "#8B4513"}},
        {"id": "industrial_geodesic_span", "label": "Geodesic Span",
         "description": "Geodesic dome or space-frame industrial enclosure with triangulated structural geometry, lightweight efficiency, and futuristic form.",
         "prompt": "Geodesic span industrial building. Large dome-shaped industrial enclosure constructed from a triangulated geodesic steel space frame. The triangular steel tube frame is fully exposed on the exterior with panels of translucent polycarbonate and opaque insulated metal infilling the triangular bays in an irregular pattern. The structure creates a dramatic hemispherical or barrel-vaulted form. Ground-level rectangular entrance structure of concrete block connecting to the dome. Interior visible through translucent panels: a vast column-free industrial space. The geometric complexity of the triangulated frame creates striking shadow patterns. Inspired by Buckminster Fuller's geodesic domes and aircraft maintenance hangars.",
         "facadeDetail": {"primaryMaterial": "triangulated steel tube geodesic frame", "secondaryMaterial": "translucent polycarbonate and metal infill panels", "groundFloor": "concrete block entrance structure connecting to dome", "colorScheme": "silver steel frame, translucent white panels, opaque grey panels"},
         "roofDetail": {"form": "geodesic dome or barrel vault", "material": "steel frame with mixed polycarbonate and metal panels"}, "palette": {"primary": "#C0C0C0"}},
        {"id": "industrial_exposed_space_frame", "label": "Exposed Space Frame",
         "description": "Industrial building with a dramatic exposed space-frame roof structure -- a three-dimensional lattice of steel tubes creating a lightweight long-span roof.",
         "prompt": "Exposed space frame industrial building. Large industrial building roofed by a dramatic three-dimensional steel space frame -- a lattice of tubular steel members connected at spherical nodes creating a geometric grid extending far beyond the walls as a dramatic cantilevered canopy. The space frame is fully exposed with no ceiling, visible from outside through clerestory glazing. Supporting columns are minimal: thin steel pipe columns at wide intervals. Walls are lightweight: glass and insulated metal panels hung from the space frame. The roof appears to float. The geometric precision of the space frame grid is the primary architectural feature. Inspired by Konrad Wachsmann's space frame systems and exhibition halls.",
         "facadeDetail": {"primaryMaterial": "exposed tubular steel space frame with spherical nodes", "secondaryMaterial": "lightweight glass and metal panel walls", "groundFloor": "minimal columns, dramatic cantilevered canopy overhang", "colorScheme": "white-painted space frame, clear glass, light grey panels"},
         "roofDetail": {"form": "flat space-frame grid cantilevering beyond walls", "material": "steel space frame with metal deck above"}, "palette": {"primary": "#E0E0E0"}},
        {"id": "industrial_tension_structure", "label": "Tension-Structure",
         "description": "Cable-stayed or tension-structure industrial building using steel cables and masts to create dramatic suspended or tensioned roof forms.",
         "prompt": "Tension-structure industrial building. Dramatic industrial building with a cable-stayed roof system. A row of tall tapered steel masts (pylons) rise above the building, from which steel cable stays fan out to support the roof structure below. The cables create a dramatic harp-like pattern against the sky. The roof is a lightweight metal deck suspended from the cables, creating a column-free interior. Walls are full-height glass between the mast supports, revealing the vast interior space. Steel base structure with exposed concrete foundations at each mast. The masts and cables dominate the composition, creating a bridge-like industrial aesthetic. Inspired by cable-stayed bridges applied to building architecture, and Renzo Piano's industrial projects.",
         "facadeDetail": {"primaryMaterial": "tapered steel masts with fan-pattern cable stays", "secondaryMaterial": "full-height glass walls between mast supports", "groundFloor": "glass walls revealing column-free interior, steel base", "colorScheme": "white-painted steel masts, silver cables, clear glass"},
         "roofDetail": {"form": "cable-suspended lightweight metal deck", "material": "metal deck hung from steel cable stays"}, "palette": {"primary": "#B0C4DE"}}
    ]
},

"corrugated_vernacular_industrial": {
    "id": "corrugated_vernacular_industrial",
    "title": "Corrugated Vernacular Industrial",
    "description": "Simple utilitarian industrial building clad in corrugated metal, representing the most common and economical form of industrial architecture worldwide",
    "developmentType": "industrial",
    "buildingSubcategory": "General Industrial",
    "aestheticCategory": "corrugated_vernacular",
    "minFloors": 1, "maxFloors": 2, "suggestedAreaSqm": 3000, "shadeId": "#708090",
    "facadeDetail": {
        "primaryMaterial": "corrugated galvanized steel or aluminum cladding",
        "secondaryMaterial": "steel portal frame structure",
        "accentMaterial": "painted steel roller doors, concrete block base walls",
        "groundFloor": "large roller doors and personnel entries",
        "upperFloors": "continuous metal cladding with occasional windows",
        "cornice": "simple metal flashing at roof edge",
        "colorScheme": "galvanized silver, or painted industrial colors"
    },
    "roofDetail": {"form": "gable, barrel vault, or Quonset arch", "material": "corrugated metal matching walls", "features": "ridge ventilator, gutters, downspouts", "aerialAppearance": "corrugated metal roof, simple form"},
    "variants": [
        {"id": "industrial_quonset_hut", "label": "Quonset Hut",
         "description": "Semi-cylindrical corrugated steel Quonset hut with its distinctive half-barrel vault form, originally developed for WWII military use.",
         "prompt": "Quonset hut industrial building. Semi-cylindrical corrugated galvanized steel structure forming a perfect half-barrel vault from ground to ridge. The corrugated metal sheets follow the curve continuously from foundation to apex with no separate walls or roof -- the structure IS the enclosure. Flat corrugated steel end walls with a large sliding door and a personnel door with a small window. No windows in the curved walls. Simple concrete slab foundation with metal base channel. Ventilation louver at the ridge peak. Weathered galvanized finish with some rust staining. Gravel yard around the building. Simple, iconic, purely functional military-industrial form. Inspired by WWII Quonset huts and Nissen huts.",
         "facadeDetail": {"primaryMaterial": "corrugated galvanized steel in continuous half-barrel curve", "secondaryMaterial": "flat corrugated steel end walls", "groundFloor": "large sliding door and personnel door in flat end wall", "colorScheme": "weathered galvanized silver with rust staining"},
         "roofDetail": {"form": "semi-cylindrical barrel vault (no separate roof -- wall IS roof)", "material": "corrugated galvanized steel"}, "palette": {"primary": "#A0A0A0"}},
        {"id": "industrial_gabled_metal_shed", "label": "Gabled Metal Shed",
         "description": "Simple gable-roofed corrugated metal industrial shed on a steel portal frame -- the most common industrial building form worldwide.",
         "prompt": "Gabled metal shed industrial building. Simple rectangular industrial building with corrugated metal wall cladding and a corrugated metal gable roof on a steel portal frame. The walls are painted dark green or grey corrugated steel with horizontal profile. A row of translucent corrugated polycarbonate panels at high level provides daylight. Large painted steel roller shutter door on the gable end. Personnel door with a small porch canopy. Exposed steel gutters and downpipes. Concrete block plinth wall at the base to protect the metal cladding. Concrete apron at the entrance. Utilitarian and functional with no architectural pretension. Industrial estate context.",
         "facadeDetail": {"primaryMaterial": "painted corrugated steel cladding (dark green or grey)", "secondaryMaterial": "translucent polycarbonate light panels, concrete block plinth", "groundFloor": "large roller shutter door, personnel door with canopy", "colorScheme": "dark green or grey corrugated metal, concrete plinth, painted steel trim"},
         "roofDetail": {"form": "simple gable with ridge ventilator", "material": "corrugated metal matching walls"}, "palette": {"primary": "#556B2F"}},
        {"id": "industrial_monitor_roof_steel", "label": "Monitor Roof Steel",
         "description": "Steel-clad industrial building with a raised central monitor (clerestory) roof providing bilateral top-lighting to the work floor below.",
         "prompt": "Monitor-roof steel industrial building. Wide-span corrugated metal-clad building with a raised central monitor (clerestory) running the full building length. The monitor has continuous glazing on both sides providing even bilateral top-lighting. The monitor creates a distinctive raised central ridge visible in the roofline profile. Walls of vertical corrugated metal in silver-grey. Personnel doors and a large sliding track door at the gable end. Exposed steel gutter and downpipe system. The building form clearly expresses its function: maximum daylight without glare. Concrete slab floor visible through the entrance. Simple industrial context with chain-link fencing.",
         "facadeDetail": {"primaryMaterial": "vertical corrugated metal cladding in silver-grey", "secondaryMaterial": "continuous glazed monitor clerestory", "groundFloor": "large sliding track door, personnel entries", "colorScheme": "silver-grey corrugated metal, glazed monitor strip"},
         "roofDetail": {"form": "low-pitched gable with raised central monitor clerestory", "material": "corrugated metal with glazed monitor"}, "palette": {"primary": "#808080"}},
        {"id": "industrial_barrel_vault_metal", "label": "Barrel-Vaulted Metal",
         "description": "Barrel-vaulted corrugated metal industrial building with a gracefully curved roof creating a larger and more elegant form than a simple gable shed.",
         "prompt": "Barrel-vaulted metal industrial building. Industrial building with a graceful curved barrel-vault roof of corrugated metal supported on steel arched ribs visible at the gable ends. The continuous curve creates an elegant profile compared to a simple gable. Corrugated metal wall panels below the spring line of the vault. Large glazed gable end walls with the steel arched ribs exposed, framing a dramatic industrial interior space. Row of circular porthole windows along the side walls at the spring line. Large roller door at one end. The curved form gives the building a distinctive, almost aircraft-hangar character. Painted in two-tone: dark base walls, lighter curved roof. Inspired by aircraft hangars and train maintenance sheds.",
         "facadeDetail": {"primaryMaterial": "corrugated metal barrel-vault roof on steel arched ribs", "secondaryMaterial": "glazed gable end walls showing arched ribs, porthole windows", "groundFloor": "large roller door, glazed gable end", "colorScheme": "two-tone: dark grey walls, lighter silver curved roof, exposed steel ribs"},
         "roofDetail": {"form": "barrel vault (continuous curve) on steel arched ribs", "material": "corrugated metal over curved steel ribs"}, "palette": {"primary": "#696969"}}
    ]
},

# ============================================================
# INDUSTRIAL: HEAVY
# ============================================================
"machine_aesthetic_heavy_industrial": {
    "id": "machine_aesthetic_heavy_industrial",
    "title": "Machine Aesthetic Heavy Industrial",
    "description": "Heavy industrial facility where the process equipment IS the architecture -- blast furnaces, silos, pipelines, and open-frame structures creating a dramatic industrial landscape",
    "developmentType": "industrial",
    "buildingSubcategory": "Heavy Industrial",
    "aestheticCategory": "machine_aesthetic",
    "minFloors": 1, "maxFloors": 10, "suggestedAreaSqm": 20000, "shadeId": "#4A4A4A",
    "facadeDetail": {
        "primaryMaterial": "exposed steel process equipment and structural steel",
        "secondaryMaterial": "corrugated metal enclosures, concrete foundations",
        "accentMaterial": "pipes, ducts, conveyors, stairs, and platforms",
        "groundFloor": "open steel frame at ground level with equipment access",
        "upperFloors": "exposed process equipment, catwalks, and platforms",
        "cornice": "no traditional roofline -- equipment silhouette defines the profile",
        "colorScheme": "rust, dark steel, industrial grey, painted safety colors"
    },
    "roofDetail": {"form": "no conventional roof -- equipment determines profile", "material": "steel and metal enclosures", "features": "stacks, conveyors, cranes, platforms", "aerialAppearance": "complex industrial equipment landscape with stacks and conveyors"},
    "variants": [
        {"id": "heavy_blast_furnace", "label": "Blast Furnace Verticality",
         "description": "Towering blast furnace complex with dramatic vertical steel structures, hot blast stoves, gas cleaning equipment, and a spaghetti of pipes and conveyors.",
         "prompt": "Blast furnace heavy industrial complex. Towering vertical steel structure dominated by a massive cylindrical blast furnace rising 30 meters, surrounded by hot blast stoves (tall cylindrical steel vessels), gas cleaning equipment, and a complex network of large-diameter steel pipes running in every direction. Steel stairways and catwalks zigzagging up the furnace structure. Overhead conveyor belt carrying raw materials to the furnace top. Casting house at the base with a corrugated metal enclosure. Steam and haze rising from the top. The entire complex is a dense vertical forest of steel with no conventional architectural facade. Rust-brown patina on steel surfaces. Railroad tracks in the foreground. Inspired by Bethlehem Steel and Landschaftspark Duisburg-Nord.",
         "facadeDetail": {"primaryMaterial": "exposed structural steel with rust-brown patina", "secondaryMaterial": "large-diameter process pipes, cylindrical vessels", "groundFloor": "casting house, railroad tracks, open steel frame", "colorScheme": "rust-brown steel, dark grey equipment, industrial orange safety paint"},
         "roofDetail": {"form": "no roof -- vertical equipment profile", "material": "steel structures and equipment"}, "palette": {"primary": "#8B4513"}},
        {"id": "heavy_open_frame_process", "label": "Open-Frame Process",
         "description": "Open steel frame process plant with no enclosing walls -- all equipment, pipes, and vessels exposed to the elements on a multi-level steel framework.",
         "prompt": "Open-frame process plant. Multi-level industrial facility with no enclosing walls -- a pure open steel framework supporting chemical process equipment at various levels. Steel pipe racks running horizontally at multiple heights carrying hundreds of pipes in neat parallel rows. Distillation columns (tall cylindrical steel vessels) rising through the framework. Heat exchangers, pumps, and valve manifolds visible at every level. Steel grating walkways and platforms at each level with pipe railings. Vertical steel ladders connecting levels. The entire facility is a three-dimensional grid of steel with equipment threaded through it. Night lighting: sodium vapor lamps creating orange glow. Inspired by oil refineries and petrochemical plants.",
         "facadeDetail": {"primaryMaterial": "open structural steel framework with no walls", "secondaryMaterial": "parallel pipe racks, cylindrical process vessels", "groundFloor": "concrete pads with pumps and equipment at grade", "colorScheme": "silver and grey steel, stainless process equipment, safety-yellow railings"},
         "roofDetail": {"form": "no roof -- open framework with equipment at various heights", "material": "open steel frame"}, "palette": {"primary": "#708090"}},
        {"id": "heavy_silo_cluster", "label": "Silo Cluster",
         "description": "Cluster of massive cylindrical concrete or steel silos for grain, cement, or bulk material storage, creating a monumental industrial composition.",
         "prompt": "Silo cluster industrial facility. Group of massive cylindrical concrete silos clustered together -- six to eight silos of varying heights (tallest 40 meters) creating a monumental geometric composition of cylinders against the sky. Smooth poured concrete surfaces with visible pour-line rings. Steel conveyor bridge connecting the silo tops to a central elevator tower. Corrugated metal head-house at the top of the elevator tower. Loading spouts and vehicle bays at the base. Connecting catwalks between silos at various levels. The stark geometric purity of the concrete cylinders creates an almost sculptural composition. Dust and haze in the atmosphere. Railroad tracks alongside. Inspired by grain elevators that Le Corbusier admired as examples of functional beauty.",
         "facadeDetail": {"primaryMaterial": "smooth poured concrete cylinders with pour-line rings", "secondaryMaterial": "steel elevator tower, conveyor bridges between silos", "groundFloor": "loading bays, vehicle access beneath silos, railroad tracks", "colorScheme": "raw grey concrete cylinders, steel conveyor bridges, corrugated metal head-house"},
         "roofDetail": {"form": "conical or flat concrete silo tops with steel conveyors", "material": "concrete silo caps with steel equipment"}, "palette": {"primary": "#A0A0A0"}},
        {"id": "heavy_pipeline_network", "label": "Pipeline Network",
         "description": "Above-ground pipeline network facility where the architecture is defined by massive interconnected pipe systems, manifolds, and valve stations.",
         "prompt": "Pipeline network industrial facility. Above-ground industrial complex defined by massive steel pipes (1-3 meter diameter) running on elevated concrete pipe racks, splitting into manifolds, and connecting to storage tanks. The pipes are painted in a color-coded system: red for steam, blue for water, yellow for gas, green for product. Valve wheels and actuators at regular intervals. Insulated pipes wrapped in aluminum jacketing with weather-protective steel saddles. Concrete pipe supports marching across the landscape in regular rhythm. Control valve stations housed in small metal enclosures. The pipeline network creates an abstract linear composition across the industrial landscape. Low-angle view emphasizing the pipes receding into the distance. Inspired by pipeline terminals and industrial processing facilities.",
         "facadeDetail": {"primaryMaterial": "large-diameter color-coded steel pipes on concrete racks", "secondaryMaterial": "aluminum-jacketed insulated pipes, valve stations", "groundFloor": "concrete pipe supports, valve access platforms", "colorScheme": "color-coded pipes: red, blue, yellow, green on grey concrete supports"},
         "roofDetail": {"form": "no building -- above-ground pipeline network", "material": "steel pipes and concrete supports"}, "palette": {"primary": "#4682B4"}}
    ]
},

"brutalist_utility_heavy_industrial": {
    "id": "brutalist_utility_heavy_industrial",
    "title": "Brutalist Utility Heavy Industrial",
    "description": "Massive raw concrete heavy industrial structure with monumental scale, utilitarian function, and the severe aesthetic of poured concrete infrastructure",
    "developmentType": "industrial",
    "buildingSubcategory": "Heavy Industrial",
    "aestheticCategory": "brutalist_utility",
    "minFloors": 1, "maxFloors": 6, "suggestedAreaSqm": 15000, "shadeId": "#696969",
    "facadeDetail": {
        "primaryMaterial": "massive poured-in-place concrete walls and structures",
        "secondaryMaterial": "concrete buttresses, retaining walls",
        "accentMaterial": "steel access doors, ventilation grilles",
        "groundFloor": "heavy concrete base with minimal openings",
        "upperFloors": "solid concrete walls with few or no windows",
        "cornice": "raw concrete parapet or stepped profile",
        "colorScheme": "raw grey concrete with weathering and staining"
    },
    "roofDetail": {"form": "flat concrete slab or bunker-like profile", "material": "reinforced concrete", "features": "concrete parapets, ventilation towers", "aerialAppearance": "massive concrete surfaces with minimal features"},
    "variants": [
        {"id": "heavy_slip_formed", "label": "Slip-formed Concrete",
         "description": "Tall industrial structure built using continuous slip-forming -- the concrete was poured continuously upward creating a seamless monolithic form with visible horizontal pour marks.",
         "prompt": "Slip-formed concrete industrial tower. Tall monolithic concrete structure built by continuous slip-forming -- the concrete walls are seamless from base to top with subtle horizontal pour-speed marks creating a fine horizontal striation texture. The structure is a tall rectangular tower (cooling tower or process column enclosure) with absolutely no windows and minimal openings. Massive concrete buttresses at the base. A few small steel access doors with concrete surrounds. Ventilation openings near the top as simple rectangular slots. The sheer monolithic scale creates an overwhelming presence. Concrete surface shows weathering: dark water staining dripping from edges, lichen growth at base. Brutally austere and monumental. Inspired by nuclear power plant containment structures and industrial cooling towers.",
         "facadeDetail": {"primaryMaterial": "monolithic slip-formed concrete with horizontal pour marks", "secondaryMaterial": "concrete buttresses at base", "groundFloor": "massive concrete base with small steel access doors", "colorScheme": "raw grey concrete with dark water staining and weathering"},
         "roofDetail": {"form": "flat concrete cap or open top", "material": "reinforced concrete"}, "palette": {"primary": "#808080"}},
        {"id": "heavy_monolithic_bunker", "label": "Monolithic Bunker",
         "description": "Massive windowless concrete bunker structure for heavy industrial processes, ammunition storage, or infrastructure protection.",
         "prompt": "Monolithic concrete bunker. Massive windowless reinforced concrete structure with enormously thick walls (visible 1-meter thickness at the entrance reveals). Simple rectangular form partially buried into an earth berm on three sides. Single massive blast-proof steel door with heavy hinges and locking mechanisms. Concrete ventilation shafts rising from the roof like abstract sculptures. Raw board-formed concrete texture with deep formwork tie holes in a regular grid pattern. Earth and grass growing on the bermed sides. Security fencing surrounding. The building's impenetrability and mass are its defining characteristics. Inspired by WWII Atlantic Wall bunkers, cold war infrastructure, and Paul Virilio's bunker archaeology.",
         "facadeDetail": {"primaryMaterial": "enormously thick reinforced concrete walls with formwork texture", "secondaryMaterial": "earth berms on three sides, concrete ventilation shafts", "groundFloor": "single massive blast-proof steel door, thick concrete reveals", "colorScheme": "raw grey concrete, earth and grass berms, heavy steel door"},
         "roofDetail": {"form": "flat concrete slab with ventilation shafts, partially earth-covered", "material": "thick reinforced concrete with earth covering"}, "palette": {"primary": "#696969"}},
        {"id": "heavy_exposed_aggregate", "label": "Exposed Aggregate",
         "description": "Heavy industrial building with exposed aggregate concrete finish -- the surface treatment reveals the stone aggregate within the concrete, creating a rough, textured surface.",
         "prompt": "Exposed aggregate concrete industrial building. Heavy industrial processing building with walls of exposed aggregate concrete -- the surface has been washed or sand-blasted to reveal the rounded river stones and gravel within the concrete mix, creating a rough pebbly texture across the entire facade. The aggregate stones vary from dark grey to brown creating a natural mottled appearance. Recessed window bands of industrial steel-sash glazing. Smooth poured concrete structural frame expressed around the rough aggregate infill panels. Concrete loading dock platform at ground level. The textural contrast between smooth structural concrete and rough aggregate panels creates visual interest on an otherwise utilitarian form. Inspired by 1960s-70s municipal and industrial concrete architecture.",
         "facadeDetail": {"primaryMaterial": "exposed aggregate concrete panels with visible river stones", "secondaryMaterial": "smooth concrete structural frame, steel-sash windows", "groundFloor": "concrete loading dock platform, industrial doors", "colorScheme": "mottled grey-brown aggregate, smooth grey concrete frame"},
         "roofDetail": {"form": "flat with concrete parapet", "material": "concrete"}, "palette": {"primary": "#7A7A6B"}},
        {"id": "heavy_precast_heavy_form", "label": "Pre-cast Heavy Form",
         "description": "Heavy industrial building constructed from massive pre-cast concrete elements -- beams, columns, and wall panels assembled into a monumental structural system.",
         "prompt": "Pre-cast heavy form industrial building. Massive industrial structure assembled from enormous pre-cast concrete elements. Giant pre-cast concrete portal frames (inverted U-shapes) marching in regular rhythm along the building length, each frame clearly separated by a visible joint. Pre-cast concrete wall panels spanning between the portal frames with chamfered panel edges creating deep V-grooves at every joint. Panel lifting holes plugged but still visible. The sheer scale of each pre-cast element (10-meter tall portal frames, 3-meter wide wall panels) gives the building a monumental repetitive rhythm. Simple rectangular form with powerful structural expression. Inspired by Soviet-era heavy industrial prefab construction and Pier Luigi Nervi's pre-cast systems.",
         "facadeDetail": {"primaryMaterial": "massive pre-cast concrete portal frames and wall panels", "secondaryMaterial": "visible panel joints with chamfered V-groove edges", "groundFloor": "pre-cast concrete base with industrial steel doors between portals", "colorScheme": "uniform grey pre-cast concrete, visible joints and lifting holes"},
         "roofDetail": {"form": "pre-cast concrete double-T roof beams spanning between portals", "material": "pre-cast concrete roof elements"}, "palette": {"primary": "#909090"}}
    ]
},

"early_20c_megastructure_industrial": {
    "id": "early_20c_megastructure_industrial",
    "title": "Early 20th Century Megastructure",
    "description": "Massive early 20th century industrial building with heroic-scale steel and timber construction, designed by pioneering industrial architects like Albert Kahn",
    "developmentType": "industrial",
    "buildingSubcategory": "Heavy Industrial",
    "aestheticCategory": "early_20c_megastructure",
    "minFloors": 1, "maxFloors": 3, "suggestedAreaSqm": 25000, "shadeId": "#5C4033",
    "facadeDetail": {
        "primaryMaterial": "steel frame with brick curtain walls or concrete",
        "secondaryMaterial": "massive steel trusses, crane rails",
        "accentMaterial": "steel-sash industrial glazing, rail access doors",
        "groundFloor": "rail access at grade, overhead crane bays",
        "upperFloors": "massive open spans with exposed steel trusses",
        "cornice": "steel truss profile visible at roofline",
        "colorScheme": "dark brick, steel, industrial glass"
    },
    "roofDetail": {"form": "massive steel truss with monitor skylights", "material": "steel frame with metal or glass roofing", "features": "overhead crane rails, monitor skylights, ventilators", "aerialAppearance": "vast steel truss roof with monitor skylights"},
    "variants": [
        {"id": "heavy_albert_kahn_truss", "label": "Albert Kahn Steel-Truss",
         "description": "Massive Albert Kahn-designed steel-truss factory with vast clear-span bays, glass curtain walls, and pioneering reinforced concrete and steel construction.",
         "prompt": "Albert Kahn steel-truss factory. Enormous single-story industrial building with massive steel Warren trusses spanning 30+ meters creating vast column-free manufacturing bays. The side walls are almost entirely glass: floor-to-ceiling steel-sash industrial glazing between minimal brick piers. The glass walls make the interior fully visible: a vast, light-filled manufacturing space with overhead crane rails running on the steel trusses. Sawtooth monitor skylights supplement the wall glazing. Simple brick end walls with the steel truss profile expressed. Railroad sidings running into the building through large openings. The building achieves cathedral-like interior volumes through pure engineering. Inspired by Albert Kahn's Ford Rouge Plant and Chrysler Tank Arsenal.",
         "facadeDetail": {"primaryMaterial": "massive steel Warren trusses with glass curtain walls", "secondaryMaterial": "minimal brick piers, steel-sash industrial glazing", "groundFloor": "railroad-accessed openings, glass walls revealing interior", "colorScheme": "dark steel trusses, vast glass walls, minimal red brick"},
         "roofDetail": {"form": "massive steel truss with sawtooth monitors", "material": "steel trusses with metal and glass roofing"}, "palette": {"primary": "#4A4A4A"}},
        {"id": "heavy_craneway_hall", "label": "Crane-way Hall",
         "description": "Massive crane-way hall with overhead travelling cranes, stepped building profile following crane rail heights, and industrial-scale doors.",
         "prompt": "Crane-way hall heavy industrial building. Massive multi-bay industrial hall with a stepped roof profile -- each bay at a different height corresponding to different overhead crane capacities. The tallest bay (main assembly hall) has an overhead travelling crane with a massive steel bridge visible through the clerestory windows. Steel-framed walls with corrugated metal cladding and high-level clerestory glazing. Massive sliding steel doors (10+ meters tall) on the gable end for moving large equipment in and out. Steel crane rails running the full length of each bay. Steel access stairs and platforms on the exterior. The building's profile directly expresses the crane requirements within. Inspired by shipbuilding halls and heavy engineering works.",
         "facadeDetail": {"primaryMaterial": "corrugated metal cladding on steel frame", "secondaryMaterial": "clerestory glazing, massive sliding steel doors", "groundFloor": "massive doors for equipment, rail access, concrete apron", "colorScheme": "grey corrugated metal, dark steel frame, industrial glazing"},
         "roofDetail": {"form": "stepped multi-bay profile with clerestory glazing at steps", "material": "corrugated metal at different heights"}, "palette": {"primary": "#505050"}},
        {"id": "heavy_continuous_monitor", "label": "Continuous Monitor",
         "description": "Vast single-story factory with continuous raised monitor skylights running the entire length, providing even top-lighting to an enormous floor area.",
         "prompt": "Continuous monitor factory. Vast single-story industrial building stretching hundreds of meters with multiple parallel raised monitor skylights (clerestories) running the full length like the backbone of an enormous creature. The monitors are glazed on both sides providing perfectly even bilateral top-lighting to the factory floor below. Between the monitors, the roof slopes are clad in corrugated metal. Side walls are brick with horizontal bands of steel-sash pivot windows. The enormous repetitive rhythm of the parallel monitors creates a distinctive saw-tooth-like roofscape visible from the street. End wall shows the multiple monitor profile with brick gable infill. Inspired by massive WWI/WWII ordnance factories and Kahn-designed production plants.",
         "facadeDetail": {"primaryMaterial": "brick walls with steel-sash window bands", "secondaryMaterial": "multiple parallel glazed monitor roofs", "groundFloor": "brick walls with loading doors, rail access", "colorScheme": "red-brown brick, corrugated metal roof, glazed monitors"},
         "roofDetail": {"form": "multiple parallel raised monitors with bilateral glazing", "material": "corrugated metal between glazed monitors"}, "palette": {"primary": "#8B4513"}},
        {"id": "heavy_timber_foundry", "label": "Heavy Timber Foundry",
         "description": "Historic heavy timber foundry with massive timber truss roof structure, brick walls, and the atmospheric patina of a working metal foundry.",
         "prompt": "Heavy timber foundry. Historic industrial building with massive walls of dark soot-stained brick and an interior spanned by enormous heavy timber king-post trusses visible through high-level windows and the open gable end. The timber structure is blackened from decades of foundry heat and smoke. Tall arched openings at ground level for casting and material handling, some bricked up and modified over generations. A casting chimney (shorter and wider than a boiler chimney) rises from the building. Dirt floor visible through the entrance. The walls show repairs and modifications across different eras: original stone, Victorian brick additions, steel patches. Heavy timber doors on iron hinges. The building has accumulated industrial patina over a century of use. Inspired by 19th-century iron foundries and Ironbridge-era workshops.",
         "facadeDetail": {"primaryMaterial": "dark soot-stained brick with repairs across eras", "secondaryMaterial": "massive timber king-post trusses visible inside", "groundFloor": "tall arched openings, some modified, heavy timber doors", "colorScheme": "dark stained brick, blackened timber, cast iron, industrial patina"},
         "roofDetail": {"form": "gable with heavy timber trusses, casting chimney", "material": "slate over heavy timber trusses"}, "palette": {"primary": "#3D2B1F"}}
    ]
},

# ============================================================
# INDUSTRIAL: WAREHOUSE
# ============================================================
"romanesque_revival_warehouse": {
    "id": "romanesque_revival_warehouse",
    "title": "Romanesque Revival Warehouse",
    "description": "Grand Romanesque Revival warehouse with round-arched windows, rusticated stone, and the monumental masonry construction of late 19th-century commercial buildings",
    "developmentType": "industrial",
    "buildingSubcategory": "Warehouse",
    "aestheticCategory": "romanesque_revival_warehouse",
    "minFloors": 3, "maxFloors": 7, "suggestedAreaSqm": 8000, "shadeId": "#8B6914",
    "facadeDetail": {
        "primaryMaterial": "rock-faced rusticated stone or dark brick with stone trim",
        "secondaryMaterial": "round-arched windows with deep stone voussoirs",
        "accentMaterial": "carved stone capitals, iron cresting",
        "groundFloor": "round-arched loading bays with heavy stone voussoirs",
        "upperFloors": "grouped round-arched windows with colonettes between",
        "cornice": "corbelled brick or stone arcade cornice",
        "colorScheme": "dark reddish-brown stone or brick, grey stone arches"
    },
    "roofDetail": {"form": "flat or low-pitched behind decorative parapet", "material": "built-up roof behind masonry parapet", "features": "decorative parapet, corner towers on larger examples", "aerialAppearance": "flat with decorative masonry parapet and towers"},
    "variants": [
        {"id": "warehouse_arch_window_brick", "label": "Arch-Window Brick",
         "description": "Dark brick warehouse with rhythmic round-arched windows, rusticated stone base, and Richardsonian Romanesque influence.",
         "prompt": "Romanesque Revival brick warehouse. Massive dark red-brown brick building with rhythmic rows of round-arched windows -- each window topped with a deep semicircular arch of contrasting light stone voussoirs. Rusticated rough-cut brownstone base course. Windows grouped in pairs and triplets separated by slender stone colonettes with carved leaf capitals. Deep window reveals creating dramatic shadow. Corbelled brick cornice with small arched corbel table. Round-arched loading doors at ground level with heavy stone surrounds. The facade has tremendous visual weight and solidity. Inspired by H.H. Richardson's Marshall Field Warehouse and Romanesque Revival commercial buildings.",
         "facadeDetail": {"primaryMaterial": "dark red-brown brick with light stone arched voussoirs", "secondaryMaterial": "rusticated brownstone base, stone colonettes with carved capitals", "groundFloor": "round-arched loading doors with heavy stone surrounds", "colorScheme": "dark brick, light stone arches, brownstone base"},
         "roofDetail": {"form": "flat behind corbelled brick arcade parapet", "material": "built-up roof behind parapet"}, "palette": {"primary": "#6B3A2A"}},
        {"id": "warehouse_rusticated_stone", "label": "Rusticated Stone Base",
         "description": "Warehouse with a massive rusticated stone base of rough-cut rock-faced ashlar, transitioning to smoother brick upper floors.",
         "prompt": "Rusticated stone base warehouse. Multi-story warehouse with a dramatic two-story rusticated stone base of massive rough-cut rock-faced granite blocks with deeply recessed mortar joints. The stone blocks are enormous and deliberately rough-textured, creating deep shadow and visual weight. Above the stone base, the facade transitions to smoother red brick with round-arched windows. Stone string course marking the transition. Round-arched entrance in the stone base with a massive stone lintel and carved keystone. Upper brick floors have paired arched windows with thin stone colonettes. The heavy stone base gives the building an impregnable fortress-like character. Inspired by Richardson's Allegheny County Courthouse and Romanesque commercial architecture.",
         "facadeDetail": {"primaryMaterial": "massive rock-faced granite rusticated base, red brick above", "secondaryMaterial": "stone string courses, round-arched windows with stone trim", "groundFloor": "massive rock-faced stone with arched entrance, huge stone blocks", "colorScheme": "grey granite base, red brick upper, stone trim, deep shadow"},
         "roofDetail": {"form": "flat with stone and brick cornice", "material": "built-up roof"}, "palette": {"primary": "#808070"}},
        {"id": "warehouse_timber_loft", "label": "Timber-Framed Loft",
         "description": "Brick warehouse with exposed heavy timber internal structure visible through large windows, representing the classic loft conversion building type.",
         "prompt": "Timber-framed loft warehouse. Five-story red brick warehouse with the internal heavy timber post-and-beam structure clearly visible through very large multi-pane steel-sash windows. The timber columns, beams, and floor decks create a warm visible grid behind the glass. Segmental brick arches over each window. Cast iron columns on the ground floor replacing timber for fire resistance. Wide loading door on the upper floor with a timber crane beam projecting above (loading lucam). Fire escape stairs in cast iron on the side facade. Simple brick dentil cornice. The building represents the classic type now converted to loft apartments and creative offices. Inspired by SoHo and DUMBO loft buildings and Castlefield Manchester warehouses.",
         "facadeDetail": {"primaryMaterial": "red brick with large windows showing timber structure inside", "secondaryMaterial": "heavy timber post-and-beam visible through glass, cast iron ground floor", "groundFloor": "cast iron columns, large display windows, loading entrance", "colorScheme": "red brick, warm timber visible inside, dark steel windows, cast iron"},
         "roofDetail": {"form": "flat with brick parapet and loading lucam", "material": "built-up roof"}, "palette": {"primary": "#8B4513"}},
        {"id": "warehouse_polychrome_brick", "label": "Polychrome Brick",
         "description": "Romanesque warehouse with decorative polychrome brickwork patterns -- bands, diaper patterns, and contrasting brick colors creating ornamental facades.",
         "prompt": "Polychrome brick Romanesque warehouse. Grand multi-story brick warehouse with elaborate decorative polychrome brickwork -- horizontal bands of cream, red, and blue-black brick creating striped patterns across the facade. Diamond-shaped diaper patterns in contrasting brick colors within the spandrel panels. Round-arched windows with alternating red and cream brick voussoirs (polychrome arches). Carved stone capitals on brick colonettes between grouped windows. Corbelled brick cornice with an elaborate interlocking brick pattern. The polychrome decoration transforms a utilitarian warehouse into a richly ornamental commercial building. Inspired by High Victorian Gothic/Romanesque commercial architecture and Ruskinian color principles applied to industrial buildings.",
         "facadeDetail": {"primaryMaterial": "polychrome brickwork: red, cream, and blue-black bands and patterns", "secondaryMaterial": "round-arched windows with polychrome voussoirs, stone capitals", "groundFloor": "polychrome arched loading bays, decorative brick base", "colorScheme": "red, cream, blue-black brick in decorative bands and diamond patterns"},
         "roofDetail": {"form": "flat behind elaborate corbelled polychrome parapet", "material": "built-up roof behind decorative parapet"}, "palette": {"primary": "#A0522D"}}
    ]
},

"midcentury_distribution_warehouse": {
    "id": "midcentury_distribution_warehouse",
    "title": "Mid-Century Distribution Warehouse",
    "description": "Post-war distribution warehouse with efficient clear-span construction, minimal ornament, and functional design for goods handling and storage",
    "developmentType": "industrial",
    "buildingSubcategory": "Warehouse",
    "aestheticCategory": "midcentury_distribution",
    "minFloors": 1, "maxFloors": 2, "suggestedAreaSqm": 6000, "shadeId": "#A0A0A0",
    "facadeDetail": {
        "primaryMaterial": "concrete block, brick, or tilt-up concrete walls",
        "secondaryMaterial": "steel framing, minimal glazing",
        "accentMaterial": "painted steel overhead doors, concrete loading dock",
        "groundFloor": "truck-height loading dock with multiple overhead doors",
        "upperFloors": "minimal or no upper floors -- single clear-span volume",
        "cornice": "simple metal coping or concrete cap",
        "colorScheme": "neutral grey or buff masonry, painted steel trim"
    },
    "roofDetail": {"form": "flat, low-pitched gable, or bowstring truss", "material": "built-up roof or metal deck", "features": "roof-mounted HVAC units, skylights", "aerialAppearance": "flat grey or white membrane roof with HVAC units"},
    "variants": [
        {"id": "warehouse_flat_roof_masonry", "label": "Flat-Roof Masonry Box",
         "description": "Simple rectangular concrete block or brick warehouse with flat roof, truck dock, and minimal architectural treatment.",
         "prompt": "Flat-roof masonry box warehouse. Simple rectangular single-story warehouse of painted concrete masonry unit (CMU) block walls with a flat roof. Long truck-height loading dock running the full length with multiple painted steel overhead doors in alternating colors (white and grey). Concrete dock bumpers and levelers. Small office portion distinguished by a strip of aluminum-framed windows and a personnel entry with a flat metal canopy. Downspouts at regular intervals. The building is deliberately plain and functional with no architectural ornament. Asphalt truck court in front of the loading dock with painted dock-number markings. Chain-link fence with barbed wire at the property line. Typical 1950s-60s distribution warehouse.",
         "facadeDetail": {"primaryMaterial": "painted concrete masonry block (CMU) walls", "secondaryMaterial": "multiple painted steel overhead doors, aluminum office windows", "groundFloor": "raised loading dock with dock levelers, office entry with metal canopy", "colorScheme": "buff or grey painted CMU, white overhead doors, grey metal trim"},
         "roofDetail": {"form": "flat with metal coping", "material": "built-up roof with gravel"}, "palette": {"primary": "#B0B0A0"}},
        {"id": "warehouse_clear_span_steel", "label": "Clear-Span Steel",
         "description": "Steel-framed clear-span warehouse with rigid-frame construction, metal wall cladding, and maximum unobstructed interior floor area.",
         "prompt": "Clear-span steel warehouse. Large single-story warehouse with rigid steel portal frame construction providing a vast column-free interior. Metal wall cladding in horizontal profile (charcoal grey) with a high-level band of translucent fiberglass panels for daylight. Large truck-access roller doors on the front elevation. Office component built out from one end with glass storefront entrance. Steel rain gutters and downpipes. Roof ridge running the full length with a ventilation ridge cap. The building reads as a clean efficient metal-clad box with the steel structure expressed at the gable ends. Concrete slab floor visible through the open truck doors. Inspired by 1960s-70s steel distribution warehouses.",
         "facadeDetail": {"primaryMaterial": "horizontal corrugated metal cladding in charcoal grey", "secondaryMaterial": "translucent fiberglass daylight panels, glass office front", "groundFloor": "large truck roller doors, glass office entrance", "colorScheme": "charcoal grey metal walls, silver roof, translucent light panels"},
         "roofDetail": {"form": "low-pitched gable with ridge ventilator", "material": "metal deck with metal cladding"}, "palette": {"primary": "#505050"}},
        {"id": "warehouse_dock_high_concrete", "label": "Dock-High Concrete",
         "description": "Reinforced concrete dock-high warehouse designed specifically for truck logistics with multiple loading positions and a raised concrete dock.",
         "prompt": "Dock-high concrete warehouse. Robust single-story reinforced concrete warehouse built at truck-bed height (1.2 meters above grade) on a raised concrete platform. Tilt-up concrete wall panels with a light sandblasted finish. Continuous concrete loading dock spanning the full building width with painted steel dock bumpers, rubber dock seals, and hydraulic dock levelers at each position. Yellow-painted bollards protecting the dock edge. Recessed overhead coiling doors in painted steel. Small concrete-framed office entry with steps from grade to dock level. The raised concrete platform is the defining feature: the entire building sits elevated for efficient truck loading. Inspired by purpose-built logistics warehouses.",
         "facadeDetail": {"primaryMaterial": "tilt-up concrete panels on raised concrete platform", "secondaryMaterial": "continuous concrete loading dock, steel overhead doors", "groundFloor": "raised 1.2m concrete dock platform, dock levelers, bumpers", "colorScheme": "light grey concrete, painted steel doors, yellow bollards"},
         "roofDetail": {"form": "flat concrete deck with minimal parapet", "material": "concrete slab with membrane"}, "palette": {"primary": "#C0C0C0"}},
        {"id": "warehouse_glulam_arch", "label": "Glulam Arch",
         "description": "Warehouse with elegant glued-laminated timber (glulam) arched roof structure, combining the warmth of wood with the clear-span efficiency of an arch.",
         "prompt": "Glulam arch warehouse. Single-story warehouse with a distinctive curved roof created by elegant glued-laminated timber (glulam) three-pin arches. The warm honey-colored timber arches are visible at the gable end through a large glazed wall, creating a dramatic cathedral-like interior space. The arches spring from concrete pad foundations at grade, curving up and over to create both wall and roof structure. Corrugated metal cladding between the arches on the sides. The timber arches are the primary architectural feature: their warm wood color and graceful curves contrast with the utilitarian function. Loading access between arches at the side. Inspired by 1950s-60s timber arch warehouses and sports halls across Scandinavia and the Pacific Northwest.",
         "facadeDetail": {"primaryMaterial": "glued-laminated timber arches in warm honey color", "secondaryMaterial": "glazed gable end showing arches, corrugated metal side cladding", "groundFloor": "concrete base with loading openings between arch bases", "colorScheme": "warm honey timber arches, silver corrugated metal, glass gable end"},
         "roofDetail": {"form": "curved glulam three-pin arch (arch IS the roof)", "material": "corrugated metal over timber arches"}, "palette": {"primary": "#CD853F"}}
    ]
},

"modern_bigbox_warehouse": {
    "id": "modern_bigbox_warehouse",
    "title": "Modern Big-Box Logistics",
    "description": "Contemporary large-scale logistics and distribution center with massive footprint, insulated metal panel construction, and advanced freight handling systems",
    "developmentType": "industrial",
    "buildingSubcategory": "Warehouse",
    "aestheticCategory": "modern_bigbox",
    "minFloors": 1, "maxFloors": 3, "suggestedAreaSqm": 30000, "shadeId": "#606060",
    "facadeDetail": {
        "primaryMaterial": "insulated metal panel (IMP) or tilt-wall concrete",
        "secondaryMaterial": "glass office entrance, steel loading infrastructure",
        "accentMaterial": "corporate branding, LED-illuminated signage",
        "groundFloor": "multiple truck loading bays with dock seals",
        "upperFloors": "massive single-volume or mezzanine with conveyor systems",
        "cornice": "clean flat metal or concrete parapet",
        "colorScheme": "light grey or white panels, corporate accent colors"
    },
    "roofDetail": {"form": "flat with massive footprint, skylights", "material": "TPO or PVC membrane with solar panels", "features": "rooftop solar array, skylights, HVAC", "aerialAppearance": "vast white membrane roof with solar panel array"},
    "variants": [
        {"id": "warehouse_imp_box", "label": "Insulated Metal Panel Box",
         "description": "Contemporary IMP-clad logistics warehouse with clean lines, corporate branding, and automated loading systems.",
         "prompt": "Insulated metal panel logistics warehouse. Vast contemporary distribution center clad in clean white insulated metal panels (IMP) with flush joints creating a seamless appearance. Extremely long facade stretching over 200 meters. Multiple truck loading bays with blue dock seals along one side. Sleek glass-fronted office entrance at one end with corporate logo signage. LED-illuminated building number signs at each loading bay. Concrete truck court with painted lane markings. The sheer scale and length of the building is the dominant impression. Minimal landscaping: a few specimen trees at the office entrance. Solar panels visible on the roof edge. Inspired by Amazon, FedEx, and DHL distribution centers.",
         "facadeDetail": {"primaryMaterial": "white insulated metal panels with flush joints", "secondaryMaterial": "glass office entrance, dock seal bays", "groundFloor": "multiple loading bays with dock seals, glass office entry", "colorScheme": "white IMP panels, blue dock seals, corporate logo colors"},
         "roofDetail": {"form": "flat with massive footprint", "material": "white TPO membrane with solar panels"}, "palette": {"primary": "#E8E8E8"}},
        {"id": "warehouse_tilt_wall_mega", "label": "Tilt-Wall Mega-Center",
         "description": "Enormous tilt-wall concrete distribution mega-center with textured concrete panels, multiple loading courts, and campus-scale infrastructure.",
         "prompt": "Tilt-wall concrete mega distribution center. Enormous logistics facility constructed of textured tilt-wall concrete panels with a light sandblasted exposed-aggregate finish. The building footprint covers an entire city block. Multiple loading courts: truck docks on two sides with scores of overhead doors. Main truck entrance with a staffed security gatehouse and automated barrier. Office block integrated at one corner with curtain wall glazing and a corporate entrance canopy. Concrete panel joints sealed with dark sealant in a regular grid. Landscaped berm along the public road frontage screening the dock activities. Scale indicators: semi-trailers parked at docks appear tiny against the building mass. Inspired by major e-commerce fulfillment centers.",
         "facadeDetail": {"primaryMaterial": "textured tilt-wall concrete with exposed aggregate", "secondaryMaterial": "curtain wall office block, security gatehouse", "groundFloor": "scores of overhead doors on multiple loading courts", "colorScheme": "warm grey concrete, dark panel joints, corporate branding at office"},
         "roofDetail": {"form": "flat, vast footprint", "material": "TPO membrane"}, "palette": {"primary": "#A0A0A0"}},
        {"id": "warehouse_cross_dock", "label": "Cross-Dock Facility",
         "description": "Purpose-built cross-dock facility with truck bays on opposing sides for rapid goods transfer without long-term storage.",
         "prompt": "Cross-dock logistics facility. Narrow but extremely long warehouse designed specifically for cross-docking: truck loading bays on BOTH long sides of the building so goods are unloaded on one side and immediately loaded onto outbound trucks on the other. The building is only 50 meters deep but 300 meters long. Clean white insulated metal panel cladding. Continuous cantilevered steel canopy over the dock face on both sides protecting the loading operations. The interior is a long narrow conveyor sorting hall visible through translucent wall panels glowing from within at dusk. Minimal office presence -- just a small control room. The building's extreme proportions (very long, relatively narrow) are its defining characteristic. Inspired by FedEx and UPS sorting hub architecture.",
         "facadeDetail": {"primaryMaterial": "white insulated metal panels, extremely long facade", "secondaryMaterial": "cantilevered steel dock canopy on both sides", "groundFloor": "loading bays on both long sides, interior glow through translucent panels", "colorScheme": "white panels, grey steel canopy, interior glow at dusk"},
         "roofDetail": {"form": "flat, extremely long and narrow footprint", "material": "metal deck with membrane"}, "palette": {"primary": "#D0D0D0"}},
        {"id": "warehouse_multistory_urban", "label": "Multi-Story Urban",
         "description": "Multi-story urban logistics building designed for dense city locations with truck ramps, high ceilings, and vertical goods movement.",
         "prompt": "Multi-story urban logistics building. Four-story urban warehouse with a spiral truck access ramp visible on the exterior, allowing delivery trucks to drive up to each level. Precast concrete facade with horizontal strip windows at each level. Truck-height openings on each floor accessed from the ramp. The spiral ramp is architecturally expressed as a sculptural concrete helix wrapping around one end of the building. Ground-floor retail or showroom space with glass storefront facing the street. Loading dock at grade level with conventional dock doors. The multi-story format allows warehouse operations in dense urban areas where land is expensive. Green wall on the street-facing facade to soften the urban impact. Inspired by multi-story urban logistics buildings in Tokyo, Brooklyn, and London.",
         "facadeDetail": {"primaryMaterial": "precast concrete with horizontal strip windows", "secondaryMaterial": "sculptural spiral truck ramp, green wall on street face", "groundFloor": "retail/showroom with glass storefront, loading dock", "colorScheme": "light grey concrete, green wall, glass retail front"},
         "roofDetail": {"form": "flat with rooftop truck turnaround area", "material": "concrete deck"}, "palette": {"primary": "#909090"}}
    ]
},

# ============================================================
# RECREATIONAL
# ============================================================
"parkitecture_recreational": {
    "id": "parkitecture_recreational",
    "title": "Parkitecture",
    "description": "National Park Service Rustic style recreational building using natural materials, hand-crafted details, and designs that harmonize with the natural landscape",
    "developmentType": "recreational",
    "buildingSubcategory": "Recreational",
    "aestheticCategory": "parkitecture",
    "minFloors": 1, "maxFloors": 3, "suggestedAreaSqm": 2000, "shadeId": "#5C4033",
    "facadeDetail": {
        "primaryMaterial": "native stone and peeled log timber",
        "secondaryMaterial": "hand-split wood shingles, rough-hewn timbers",
        "accentMaterial": "wrought iron hardware, hand-forged hinges",
        "groundFloor": "stone base with massive timber entrance, covered porch",
        "upperFloors": "log construction or timber frame with stone chimneys",
        "cornice": "wide overhanging eaves with exposed log rafter tails",
        "colorScheme": "natural stone, warm timber, dark stained wood"
    },
    "roofDetail": {"form": "steeply pitched gable or hip with wide overhangs", "material": "hand-split wood shakes or dark slate", "features": "massive stone chimney, exposed log rafter tails", "aerialAppearance": "dark wood shake roof with massive stone chimney"},
    "variants": [
        {"id": "rec_adirondack_rustic", "label": "Adirondack Rustic",
         "description": "Adirondack Great Camp style with massive peeled-log construction, stone fireplaces, bark-covered exteriors, and wilderness lodge grandeur.",
         "prompt": "Adirondack Rustic recreational building. Grand lodge-style building constructed of massive peeled spruce and cedar logs with bark-covered accents. Enormous stone fireplace chimney of local fieldstone rising through the center. Wide covered front porch with massive log columns and log railings. Walls of horizontally stacked peeled logs with saddle-notch corners. Bark-covered decorative panels in the gable ends with twig-work patterns. Deep overhanging eaves with exposed log rafter tails. Multi-pane windows with divided lites and dark wood frames. Stone foundation and steps. Set among mature pine and birch trees. Inspired by Adirondack Great Camps like Camp Sagamore and Whiteface Lodge.",
         "facadeDetail": {"primaryMaterial": "massive peeled spruce and cedar logs, saddle-notch corners", "secondaryMaterial": "native fieldstone chimney and foundation, bark-covered panels", "groundFloor": "wide covered porch with log columns, stone steps", "colorScheme": "warm golden peeled log, grey fieldstone, bark-brown accents"},
         "roofDetail": {"form": "steeply pitched gable with deep overhangs", "material": "hand-split cedar shakes"}, "palette": {"primary": "#8B6914"}},
        {"id": "rec_log_cabin_vernacular", "label": "Log Cabin Vernacular",
         "description": "Traditional pioneer log cabin with dovetail corners, mud chinking, stone hearth, and the simple honest construction of frontier vernacular architecture.",
         "prompt": "Log cabin vernacular recreational building. Simple single-story log cabin of hand-hewn square-notched timbers with visible dovetail corner joints. White mortar chinking between the logs. Low-pitched gable roof of hand-split wood shakes with a simple stone chimney at one end. Small multi-pane windows with simple wood frames and shutters. Covered front porch spanning the full width with round log posts and a plank floor. Plank door with iron strap hinges. Wood pile stacked neatly beside the cabin. Stone foundation visible at the base. Rail fence surrounding a small cleared yard. Set at the edge of a meadow with forest behind. Authentically simple pioneer construction with no modern materials. Inspired by historic frontier cabins and living history museums.",
         "facadeDetail": {"primaryMaterial": "hand-hewn square logs with dovetail corners", "secondaryMaterial": "white mortar chinking, stone chimney", "groundFloor": "full-width covered plank porch, plank door with iron hinges", "colorScheme": "warm brown hewn logs, white chinking, grey stone, dark wood shakes"},
         "roofDetail": {"form": "low-pitched gable with stone chimney", "material": "hand-split wood shakes"}, "palette": {"primary": "#6B4226"}},
        {"id": "rec_shingle_style_pavilion", "label": "Shingle Style Pavilion",
         "description": "Shingle Style recreational pavilion with continuous wood shingle cladding flowing over walls and roof, creating an organic, textured mass.",
         "prompt": "Shingle Style recreational pavilion. Organic-looking building entirely wrapped in warm brown cedar shingles -- the shingles flow continuously over walls, turrets, gable ends, and roof without interruption, creating a unified textured surface. Round turret element at one corner with a conical shingled cap. Wide arched openings on the ground floor for covered gathering space. Eyebrow dormers (curved shingled dormers) in the roof. Continuous band of windows at the upper level recessed behind a shingled wall surface. Massive fieldstone base and chimney. The building seems to emerge from the landscape, its shingle skin like tree bark. Wide overhanging eaves. Inspired by McKim Mead & White's Casino at Narragansett and Shingle Style seaside resorts.",
         "facadeDetail": {"primaryMaterial": "continuous cedar shingle cladding over walls and roof", "secondaryMaterial": "fieldstone base and chimney, arched openings", "groundFloor": "wide arched openings for covered pavilion space, stone base", "colorScheme": "warm brown cedar shingles, grey fieldstone, dark green trim"},
         "roofDetail": {"form": "complex gambrel and gable with shingled turret and eyebrow dormers", "material": "cedar shingles continuous from walls"}, "palette": {"primary": "#8B7355"}},
        {"id": "rec_ccc_stone", "label": "CCC-Era Stone",
         "description": "Civilian Conservation Corps stone construction with massive hand-laid native stone walls, heavy timber details, and the robust craftsmanship of 1930s New Deal park construction.",
         "prompt": "CCC-era stone recreational building. Robust park building constructed of massive hand-laid native stone walls -- each stone carefully selected and fitted by Civilian Conservation Corps workers in the 1930s. The stone walls are thick (visible 18-inch depth at window reveals) with deeply recessed mortar joints. Heavy timber roof structure with exposed log purlins and peeled-log rafter tails extending beyond the stone walls. Wide covered porch with massive stone piers and heavy timber lintels. Multi-pane casement windows with stone sills and lintels. Massive stone chimney with a slightly battered (inward-sloping) profile. Stone retaining walls and steps integrated into the hillside. The craftsmanship is visible in the careful stone selection and fitting. Inspired by CCC-built park structures across US National and State Parks.",
         "facadeDetail": {"primaryMaterial": "massive hand-laid native stone with deep mortar joints", "secondaryMaterial": "heavy timber roof structure, peeled-log details", "groundFloor": "wide stone porch with massive piers, thick stone walls", "colorScheme": "varied native stone colors (grey, brown, tan), warm timber, dark stain"},
         "roofDetail": {"form": "medium-pitch gable with wide overhangs and exposed log purlins", "material": "dark slate or wood shakes"}, "palette": {"primary": "#7A7A6B"}}
    ]
},

}

# ---- Generation functions (same as batch 1) ----

def generate_image(prompt, retries=2):
    body = {"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"responseModalities": ["TEXT", "IMAGE"], "temperature": 0.0}}
    for attempt in range(retries + 1):
        try:
            print(f"  -> Calling Gemini Pro ({len(prompt)} chars)...")
            resp = httpx.post(API_URL, json=body, timeout=120.0)
            if resp.status_code == 429:
                wait = 30 * (attempt + 1)
                print(f"  Rate limited, waiting {wait}s...")
                time.sleep(wait)
                continue
            if resp.status_code != 200:
                print(f"  X API error {resp.status_code}: {resp.text[:300]}")
                if attempt < retries: time.sleep(10); continue
                return None
            data = resp.json()
            candidates = data.get("candidates", [])
            if not candidates: print("  X No candidates"); return None
            for part in candidates[0].get("content", {}).get("parts", []):
                if "inlineData" in part: return base64.b64decode(part["inlineData"]["data"])
            print("  X No image in response"); return None
        except Exception as e:
            print(f"  X Exception: {e}")
            if attempt < retries: time.sleep(10); continue
            return None
    return None

def resize_and_crop(img_bytes, w, h):
    img = Image.open(io.BytesIO(img_bytes))
    ratio = max(w / img.width, h / img.height)
    new_w, new_h = int(img.width * ratio), int(img.height * ratio)
    img = img.resize((new_w, new_h), Image.LANCZOS)
    left, top = (new_w - w) // 2, (new_h - h) // 2
    img = img.crop((left, top, left + w, top + h))
    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return buf.getvalue()

BUILDING_FRAME = (
    "Photorealistic architectural visualization. "
    "Street-level perspective from across the street, approximately 25 meters away, "
    "at a 3/4 angle showing two facades. The full building is visible from ground "
    "to roofline with some sky above and street/sidewalk below. "
)

def generate_archetype_images(arch_id, arch_data, skip_existing=True):
    out_dir = _PUBLIC_DIR / "buildings" / arch_id
    out_dir.mkdir(parents=True, exist_ok=True)
    variants = arch_data["variants"]
    print(f"\n{'='*60}\nArchetype: {arch_data['title']} ({arch_id})\nOutput: {out_dir}\nVariants: {len(variants)}\n{'='*60}")
    for i, variant in enumerate(variants):
        filename = f"variant_{i}.png"
        filepath = out_dir / filename
        if skip_existing and filepath.exists():
            print(f"  [{i}] {variant['label']} -- already exists, skipping"); continue
        prompt = BUILDING_FRAME + variant["prompt"] + " " + NO_PEOPLE + " " + STYLE_ANCHOR
        print(f"  [{i}] Generating {variant['label']}...")
        img_bytes = generate_image(prompt)
        if img_bytes:
            cropped = resize_and_crop(img_bytes, CARD_WIDTH, CARD_HEIGHT)
            filepath.write_bytes(cropped)
            print(f"  OK Saved {filepath.name} ({len(cropped):,} bytes)")
        else:
            print(f"  X Failed to generate {variant['label']}")
        if i < len(variants) - 1: print("  .. Waiting 5s..."); time.sleep(5)
    v0, hero = out_dir / "variant_0.png", out_dir / "hero.png"
    if v0.exists() and not hero.exists():
        hero.write_bytes(v0.read_bytes()); print(f"  OK Copied variant_0.png -> hero.png")

def update_archetypes_json(generated_archetypes):
    json_path = _DATA_DIR / "buildingArchetypes.json"
    data = json.loads(json_path.read_text(encoding="utf-8"))
    existing_ids = {a["id"] for a in data["archetypes"]}
    added = 0
    for arch_id, arch_data in generated_archetypes.items():
        if arch_id in existing_ids: print(f"  Skipping {arch_id} -- already in JSON"); continue
        entry = {
            "id": arch_id, "shadeId": arch_data.get("shadeId", "#888888"),
            "title": arch_data["title"], "aestheticCategory": arch_data.get("aestheticCategory", arch_id),
            "description": arch_data["description"], "buildingSubcategory": arch_data.get("buildingSubcategory", "General"),
            "generationTags": [arch_data.get("aestheticCategory", arch_id)],
            "palette": {"skyTop": "#8fa2b8", "skyBottom": "#c4b896", "ground": "#8a8a7a", "accent": arch_data.get("shadeId", "#888888")},
            "styleProfile": {"era": "", "influences": [], "keywords": []},
            "facadeDetail": arch_data.get("facadeDetail", {}), "roofDetail": arch_data.get("roofDetail", {}),
            "thumbnailUrl": f"/archetypes/buildings/{arch_id}/hero.png",
            "variants": [{"id": v["id"], "label": v["label"], "thumbnailUrl": f"/archetypes/buildings/{arch_id}/variant_{i}.png",
                          "description": v["description"], "facadeDetail": v.get("facadeDetail", {}), "roofDetail": v.get("roofDetail", {}),
                          "shadeId": None, "palette": v.get("palette", {"primary": "#888888"})} for i, v in enumerate(arch_data["variants"])],
            "minFloors": arch_data.get("minFloors", 2), "maxFloors": arch_data.get("maxFloors", 6),
            "suggestedAreaSqm": arch_data.get("suggestedAreaSqm", 5000), "developmentType": arch_data.get("developmentType", "institutional"),
        }
        data["archetypes"].append(entry); added += 1; print(f"  Added {arch_id}")
    if added > 0:
        json_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"\nUpdated JSON with {added} new archetypes")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--category", type=str)
    parser.add_argument("--no-skip", action="store_true")
    parser.add_argument("--json-only", action="store_true")
    args = parser.parse_args()
    skip = not args.no_skip
    targets = {args.category: ALL_ARCHETYPES[args.category]} if args.category else ALL_ARCHETYPES
    total = sum(len(a["variants"]) for a in targets.values())
    print(f"Batch 2: {len(targets)} archetypes, {total} images, est cost: ${total * 0.134:.2f}")
    if not args.json_only:
        for arch_id, arch_data in targets.items():
            generate_archetype_images(arch_id, arch_data, skip_existing=skip)
            time.sleep(3)
    print("\nUpdating JSON...")
    update_archetypes_json(targets)
    print(f"\nDONE! Batch 2 complete.")

if __name__ == "__main__":
    main()
