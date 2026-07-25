"""
Generate batch 3 archetype images: Rec Centre, Sports Arena, Hotels, Transit Stations.
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
        if line.strip().startswith("GEMINI_API_KEY="): return line.strip().split("=", 1)[1].strip()
    sys.exit("ERROR: GEMINI_API_KEY not found")

API_KEY = _load_api_key()
MODEL = "gemini-3-pro-image-preview"
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={API_KEY}"

STYLE_ANCHOR = "Style: photorealistic architectural visualization, high-end 3D rendering quality like a professional archviz studio. Warm golden-hour afternoon sunlight from the left at roughly 45 degrees, casting soft natural shadows. Slightly hazy atmospheric perspective in the background. Natural color grading with warm tones. Sharp detail on materials and textures. Photorealistic, 8K detail, architectural photography composition."
NO_PEOPLE = "Absolutely no people, no human figures, no pedestrians, no silhouettes, no crowds anywhere in the scene. The scene is completely empty of humans."
BUILDING_FRAME = "Photorealistic architectural visualization. Street-level perspective from across the street, approximately 25 meters away, at a 3/4 angle showing two facades. The full building is visible from ground to roofline with some sky above and street/sidewalk below. "

ALL_ARCHETYPES = {

# ============================================================
# REC CENTRE
# ============================================================
"civic_modernism_rec_centre": {
    "id": "civic_modernism_rec_centre",
    "title": "Civic Modernism Rec Centre",
    "description": "Mid-century civic modernist recreation centre with clean lines, honest materials, and functional community-serving design",
    "developmentType": "recreational",
    "buildingSubcategory": "Rec Centre",
    "aestheticCategory": "civic_modernism_rec",
    "minFloors": 1, "maxFloors": 3, "suggestedAreaSqm": 4000, "shadeId": "#CD853F",
    "facadeDetail": {"primaryMaterial": "red brick or concrete with expressed structure", "secondaryMaterial": "clerestory glazing, timber or steel structural elements", "accentMaterial": "painted steel entrance canopy, signage", "groundFloor": "welcoming glazed entrance lobby with covered drop-off", "upperFloors": "gymnasium volume expressed as a taller windowless mass", "cornice": "clean flat roofline or exposed roof structure at edges", "colorScheme": "warm brick, exposed structure, glass entrance"},
    "roofDetail": {"form": "flat or distinctive structural roof form", "material": "built-up or metal", "features": "gymnasium volume visible, clerestory windows", "aerialAppearance": "flat with raised gymnasium volume"},
    "variants": [
        {"id": "rec_brick_glass_box", "label": "Brick-and-Glass Box",
         "description": "Clean mid-century brick and glass rec centre with expressed concrete frame, large glazed entrance, and honest material palette.",
         "prompt": "Brick-and-glass box recreation centre. Clean mid-century modern community building with warm red brick walls set within an expressed reinforced concrete structural frame -- the concrete columns and beams create a visible grid on the exterior. Large floor-to-ceiling glass entrance lobby with views into the lobby and pool area. Gymnasium wing expressed as a taller brick volume with no windows and a flat concrete fascia. Covered entrance canopy in painted white steel with the community centre name in mid-century sans-serif lettering. Landscaped entrance with a public plaza and bicycle racks. Low-pitched roof behind a clean brick parapet. The building radiates civic pride and functional modernism. Inspired by 1960s municipal recreation centres and community pools.",
         "facadeDetail": {"primaryMaterial": "warm red brick within expressed concrete frame", "secondaryMaterial": "large glass entrance lobby, concrete structural grid", "groundFloor": "glazed lobby entrance with white steel canopy, public plaza", "colorScheme": "red brick, white concrete frame, glass entrance, painted steel"},
         "roofDetail": {"form": "flat with raised gymnasium volume", "material": "built-up roof behind brick parapet"}, "palette": {"primary": "#8B4513"}},
        {"id": "rec_exposed_glulam", "label": "Exposed Glulam Beam",
         "description": "Recreation centre with dramatic exposed glulam timber beams creating the pool hall or gymnasium roof, celebrating timber engineering.",
         "prompt": "Exposed glulam beam recreation centre. Community centre with a dramatic double-height pool hall roofed by massive curved glued-laminated timber (glulam) beams in warm honey color, visible through a full-height glass curtain wall on the entrance side. The glulam beams arch gracefully over the swimming pool interior. Lower single-story wings in warm cedar timber cladding house changing rooms and offices. Timber rain-screen entrance facade with integrated signage. Stone base anchoring the building to the ground. Green sedum roof on the lower wings. The warm timber palette gives the building a welcoming community feel. Inspired by Scandinavian and Canadian timber recreation centres.",
         "facadeDetail": {"primaryMaterial": "curved glulam beams visible through glass, cedar timber cladding", "secondaryMaterial": "full-height glass pool hall wall, stone base", "groundFloor": "timber-clad entrance with glass revealing glulam pool hall", "colorScheme": "warm honey glulam, cedar cladding, stone base, green roof"},
         "roofDetail": {"form": "curved glulam arches over pool hall, flat green roof on wings", "material": "standing seam metal over glulam, sedum on wings"}, "palette": {"primary": "#CD853F"}},
        {"id": "rec_clerestory_modern", "label": "Clerestory Modern",
         "description": "Recreation centre with dramatic clerestory windows running the length of the gym/pool hall, flooding the interior with natural light.",
         "prompt": "Clerestory modern recreation centre. Contemporary community centre with a distinctive raised clerestory band of windows running the full length of the main hall -- the clerestory is a continuous strip of glazing between the lower wall plane and the overhanging roof, flooding the interior with diffused natural light. White rendered walls below the clerestory. The roof plane extends beyond the walls as a dramatic overhang, supported by angled steel columns. Lower entrance wing in dark brick with a recessed glass entry. The clerestory creates a signature horizontal light-band visible from the street, especially dramatic at dusk when the interior glows. Inspired by Alvar Aalto's community buildings and Jorn Utzon's sports halls.",
         "facadeDetail": {"primaryMaterial": "white rendered walls with continuous clerestory glazing band", "secondaryMaterial": "dark brick entrance wing, angled steel columns", "groundFloor": "recessed glass entrance in dark brick wing", "colorScheme": "white render below, glass clerestory band, overhanging roof plane"},
         "roofDetail": {"form": "flat overhanging roof with clerestory gap between roof and wall", "material": "standing seam metal with deep overhang"}, "palette": {"primary": "#E0E0E0"}},
        {"id": "rec_concrete_frame", "label": "Concrete Frame",
         "description": "Brutalist-influenced concrete frame rec centre with bold exposed concrete structure, deep window reveals, and monumental civic presence.",
         "prompt": "Concrete frame recreation centre. Bold community centre with a fully exposed board-formed reinforced concrete structural frame creating deep recessed bays filled with either glass or brick infill. The concrete frame is expressed on all elevations as a heavy grid of beams and columns with visible formwork texture. Deep concrete window reveals cast dramatic shadows. Main gymnasium volume rises as a monolithic concrete box above the lower wings. Concrete entrance canopy cantilevered from the main structure. Interior visible through glass panels: a vibrant community space with colored walls and activity zones. Concrete plinth base with integrated seating. Inspired by Denys Lasdun's civic buildings and Brazilian Brutalist community centres.",
         "facadeDetail": {"primaryMaterial": "exposed board-formed concrete frame with brick and glass infill", "secondaryMaterial": "deep concrete window reveals, cantilevered entrance canopy", "groundFloor": "concrete colonnade entrance with glass revealing community space", "colorScheme": "raw grey concrete, warm brick infill, colored interior visible"},
         "roofDetail": {"form": "flat concrete with raised gymnasium box", "material": "concrete slab with gravel"}, "palette": {"primary": "#808080"}}
    ]
},

"postmodern_rec_centre": {
    "id": "postmodern_rec_centre",
    "title": "Postmodern Community Rec Centre",
    "description": "Playful postmodern recreation centre with bold colors, geometric shapes, and contextual references creating a welcoming community presence",
    "developmentType": "recreational",
    "buildingSubcategory": "Rec Centre",
    "aestheticCategory": "postmodern_rec",
    "minFloors": 1, "maxFloors": 3, "suggestedAreaSqm": 3500, "shadeId": "#E06030",
    "facadeDetail": {"primaryMaterial": "colored stucco, metal panels, or brick in varied colors", "secondaryMaterial": "oversized geometric windows, colored steel canopies", "accentMaterial": "bright accent panels, playful signage", "groundFloor": "inviting entrance with bold color and oversized canopy", "upperFloors": "varied massing with different colors per volume", "cornice": "varied roofline with geometric accents", "colorScheme": "bold primary and secondary colors, playful palette"},
    "roofDetail": {"form": "varied heights with geometric accents", "material": "standing seam metal in accent colors", "features": "colored roof elements, geometric forms", "aerialAppearance": "colorful varied roof with geometric accents"},
    "variants": [
        {"id": "rec_color_blocked", "label": "Color-Blocked Facade",
         "description": "Bold color-blocked rec centre with each programmatic volume expressed in a different bright color, creating a vibrant community landmark.",
         "prompt": "Color-blocked facade recreation centre. Playful community centre where each programmatic volume is clad in a different bold color: the gymnasium is bright blue metal panels, the pool wing is warm orange stucco, the entrance lobby is bright yellow, and the office wing is deep green. Each colored volume intersects and overlaps at different heights, creating a dynamic collage-like composition. Oversized circular windows on the gymnasium. Triangular entrance canopy in red steel. Bold sans-serif signage in contrasting colors. The building is deliberately joyful and child-friendly, announcing itself as a community gathering place through pure color energy. Landscaped plaza with colored concrete paving. Inspired by MVRDV and Sauerbruch Hutton's colorful community buildings.",
         "facadeDetail": {"primaryMaterial": "colored metal panels and stucco: blue, orange, yellow, green", "secondaryMaterial": "oversized circular windows, red steel canopy", "groundFloor": "yellow entrance lobby with red triangular canopy, colored plaza", "colorScheme": "bright blue, orange, yellow, green, red accents"},
         "roofDetail": {"form": "varied heights with intersecting colored volumes", "material": "colored standing seam metal"}, "palette": {"primary": "#4169E1"}},
        {"id": "rec_neo_traditional", "label": "Neo-Traditional Vernacular",
         "description": "Neo-traditional rec centre using local vernacular materials and forms in a contemporary interpretation, fitting into a residential neighborhood context.",
         "prompt": "Neo-traditional vernacular recreation centre. Community centre designed to fit into a residential neighborhood using locally familiar materials in a contemporary composition. Warm red-brown brick matching the surrounding houses with pitched roof forms echoing the neighborhood gable rooflines. But the scale and proportions are clearly civic: wider spans, taller windows, and a prominent glazed entrance bay. Arts-and-crafts-influenced details: decorative brick patterns, deep window reveals, timber-framed entrance porch. Community garden visible at the side. Bicycle parking under a covered timber structure. The building says 'community centre' while respecting its domestic-scale surroundings. Inspired by contextual community architecture and RIBA award-winning neighbourhood centres.",
         "facadeDetail": {"primaryMaterial": "warm red-brown brick matching neighborhood context", "secondaryMaterial": "glazed entrance bay, decorative brick patterns", "groundFloor": "timber-framed entrance porch, accessible ramp, community noticeboard", "colorScheme": "warm brick matching neighbors, timber entrance, slate-grey roof"},
         "roofDetail": {"form": "pitched gables echoing residential context but at civic scale", "material": "slate or concrete tile matching neighborhood"}, "palette": {"primary": "#8B4513"}},
        {"id": "rec_deconstructivist_angle", "label": "Deconstructivist Angle",
         "description": "Angular deconstructivist rec centre with dramatically tilted walls, sharp angles, and fragmented forms creating an exciting, dynamic community building.",
         "prompt": "Deconstructivist angle recreation centre. Dramatically angular community centre with walls tilted at sharp angles from vertical, creating a dynamic sense of movement and energy. Zinc-clad angular volumes slicing through each other at impossible-seeming angles. A massive angular cantilevered entrance canopy juts out over the plaza like a ship's prow. Slashed window openings cut diagonally across the tilted facades. Interior visible through angular glass walls: a bright climbing wall and sports hall. The building's aggressive geometry announces excitement and physical activity -- the architecture itself feels athletic. Sharp knife-edge metal corners and angular steel columns. Inspired by Daniel Libeskind, Coop Himmelb(l)au, and Zaha Hadid's sports centres.",
         "facadeDetail": {"primaryMaterial": "zinc cladding on sharply angled volumes", "secondaryMaterial": "diagonal slashed window openings, angular glass walls", "groundFloor": "angular cantilevered entrance prow over plaza", "colorScheme": "dark zinc, silver metalwork, angular glass, bright interior visible"},
         "roofDetail": {"form": "angular tilted planes at colliding angles", "material": "zinc panels"}, "palette": {"primary": "#708090"}},
        {"id": "rec_playful_geometric", "label": "Playful Geometric",
         "description": "Playful geometric rec centre with oversized geometric shapes -- circles, triangles, hexagons -- as architectural elements creating a whimsical, inviting building.",
         "prompt": "Playful geometric recreation centre. Whimsical community centre composed of oversized geometric shapes: a large circular window (5-meter diameter) marks the entrance, triangular roof elements in bright colors project above the roofline, and hexagonal skylights dot the facade. Walls of smooth white stucco with geometric cutout patterns filled with colored glass -- red, yellow, blue, green -- creating a stained-glass effect when lit from within. Rounded corners on building volumes. A cylindrical stair tower with a spiral ramp. Entrance through a oversized triangular portal in bright red. Playful, welcoming, and child-friendly without being childish. The geometry is precise and sophisticated while feeling joyful. Inspired by Aldo van Eyck's playgrounds, Friedensreich Hundertwasser, and contemporary children's museums.",
         "facadeDetail": {"primaryMaterial": "smooth white stucco with geometric colored-glass cutouts", "secondaryMaterial": "oversized circular window, triangular roof elements", "groundFloor": "oversized triangular red entrance portal, cylindrical stair tower", "colorScheme": "white stucco, bright red/yellow/blue/green geometric accents"},
         "roofDetail": {"form": "varied with projecting triangular elements and hexagonal skylights", "material": "white membrane with colored geometric projections"}, "palette": {"primary": "#E06030"}}
    ]
},

"contemporary_sustainable_rec_centre": {
    "id": "contemporary_sustainable_rec_centre",
    "title": "Contemporary Sustainable Rec Centre",
    "description": "Net-zero or Passive House recreation centre showcasing advanced sustainable design with mass timber, solar integration, and biophilic principles",
    "developmentType": "recreational",
    "buildingSubcategory": "Rec Centre",
    "aestheticCategory": "sustainable_rec",
    "minFloors": 1, "maxFloors": 3, "suggestedAreaSqm": 4500, "shadeId": "#228B22",
    "facadeDetail": {"primaryMaterial": "mass timber structure with sustainable cladding", "secondaryMaterial": "high-performance triple-glazing, solar panels", "accentMaterial": "recycled materials, living wall elements", "groundFloor": "transparent lobby showing sustainable features", "upperFloors": "timber structure visible, solar integration", "cornice": "green roof edge or solar canopy", "colorScheme": "natural timber, green elements, solar blue-black"},
    "roofDetail": {"form": "green roof or solar canopy", "material": "extensive green roof with PV array", "features": "rooftop solar, rainwater collection, green roof", "aerialAppearance": "green roof with solar panel array"},
    "variants": [
        {"id": "rec_passive_house", "label": "Passive House Standard",
         "description": "Certified Passive House recreation centre with super-insulated envelope, MVHR, and minimal energy demand, visible through architectural expression.",
         "prompt": "Passive House standard recreation centre. Highly insulated community centre with extremely thick walls (visible 500mm wall depth at window reveals) expressing the super-insulation. Triple-glazed windows with insulated frames, each window precisely positioned for optimal solar gain -- south facade is mostly glass, north facade nearly windowless. Compact building form minimizing surface area. Mechanical ventilation heat recovery (MVHR) unit visible as a discreet rooftop element. Airtight construction expressed through smooth seamless rendered walls. Building energy dashboard displayed on a screen visible through the entrance lobby glass. High-performance entrance vestibule (airlock) with two sets of doors. Rooftop solar panels. The building's energy efficiency is its defining architectural feature. Inspired by Passivhaus-certified community buildings in Austria and Germany.",
         "facadeDetail": {"primaryMaterial": "smooth rendered super-insulated walls with 500mm reveals", "secondaryMaterial": "triple-glazed windows, mostly glass south face", "groundFloor": "entrance vestibule (airlock), energy dashboard visible", "colorScheme": "white rendered walls, dark window frames, solar panels, minimal"},
         "roofDetail": {"form": "compact flat with solar panels and MVHR unit", "material": "green roof with PV array"}, "palette": {"primary": "#E8E8E8"}},
        {"id": "rec_mass_timber_eco", "label": "Mass Timber Eco-Hub",
         "description": "Mass timber recreation centre celebrating carbon-sequestering construction with exposed CLT and glulam throughout.",
         "prompt": "Mass timber eco-hub recreation centre. Community centre built entirely of exposed cross-laminated timber (CLT) and glulam, showcasing carbon-sequestering construction. The warm honey-colored timber structure is fully visible on the exterior as a grid of massive timber columns and beams with CLT wall and roof panels. Charred timber (Shou Sugi Ban) rain-screen cladding on the lower portions for weather protection. Large timber-framed windows with deep reveals showing the CLT panel thickness. Covered timber colonnade entrance with massive round log columns. Green roof with native wildflower meadow planting. Rainwater collection visible as a copper-pipe system flowing to a bioswale. The building smells of fresh timber. Carbon calculator display at entrance showing sequestered CO2. Inspired by mass timber community buildings in British Columbia and Scandinavia.",
         "facadeDetail": {"primaryMaterial": "exposed CLT and glulam structure in honey color", "secondaryMaterial": "charred timber (Shou Sugi Ban) rain-screen at base", "groundFloor": "covered colonnade with round log columns, bioswale", "colorScheme": "warm honey timber, charred black base, green roof, copper rain pipes"},
         "roofDetail": {"form": "CLT roof panels with wildflower green roof", "material": "CLT structure with extensive green roof"}, "palette": {"primary": "#CD853F"}},
        {"id": "rec_biophilic_glass", "label": "Biophilic Glass",
         "description": "Biophilic glass recreation centre with maximum transparency, indoor trees, living walls, and the boundary between inside and outside dissolved.",
         "prompt": "Biophilic glass recreation centre. Ultra-transparent community centre with full-height glass walls on all sides blurring the boundary between indoor and outdoor. Mature trees growing inside the building visible through the glass, their canopies reaching toward the roof. Interior living walls of lush tropical plants covering structural columns. The roof is a lightweight ETFE cushion system allowing diffused natural light to flood the interior. Operable glass panels that slide open completely in good weather, opening the entire ground floor to the surrounding park. Internal pool area visible through glass with garden views. The building feels like a occupied greenhouse or winter garden. Minimal steel structure painted white disappearing against the glass. Inspired by Singapore's Gardens by the Bay and Junya Ishigami's KAIT Workshop.",
         "facadeDetail": {"primaryMaterial": "full-height glass walls with minimal white steel frame", "secondaryMaterial": "living walls on columns, mature indoor trees visible", "groundFloor": "operable glass panels opening entirely to park, indoor garden", "colorScheme": "transparent glass, white steel, green vegetation everywhere"},
         "roofDetail": {"form": "lightweight ETFE cushion canopy allowing diffused light", "material": "ETFE pillows on minimal steel frame"}, "palette": {"primary": "#90EE90"}},
        {"id": "rec_net_zero_solar", "label": "Net-Zero Solar Form",
         "description": "Net-zero energy recreation centre where the roof form is sculpted to maximize solar panel output, making renewable energy generation the architectural expression.",
         "prompt": "Net-zero solar form recreation centre. Community centre where the entire roof is a sculpted solar energy collector -- tilted at optimal solar angle (30-40 degrees), the south-facing roof is completely covered in building-integrated photovoltaic (BIPV) panels creating a dramatic dark blue-black angular plane visible from the street. The north-facing roof slopes gently to a green roof. The building's asymmetric profile is determined entirely by solar optimization. Walls of rammed earth below the solar roof, giving warmth and thermal mass. Vertical solar fins on the west facade doubling as sunshades. Energy production displays at the entrance. Battery storage containers visible at the rear, painted in corporate green. The building generates more energy than it consumes. Inspired by net-zero energy community centres and solar-optimized architecture.",
         "facadeDetail": {"primaryMaterial": "rammed earth walls with layered earth tones", "secondaryMaterial": "BIPV solar roof plane, vertical solar fins", "groundFloor": "rammed earth entrance with energy display, covered solar canopy", "colorScheme": "warm rammed earth, blue-black solar panels, green accents"},
         "roofDetail": {"form": "asymmetric: steep south solar roof, gentle north green roof", "material": "BIPV panels south face, green roof north face"}, "palette": {"primary": "#1B3A4B"}}
    ]
},

# ============================================================
# SPORTS ARENA
# ============================================================
"monumental_antiquity_arena": {
    "id": "monumental_antiquity_arena",
    "title": "Monumental Antiquity Arena",
    "description": "Classically-inspired sports arena drawing on the monumental forms of ancient amphitheaters, Roman arenas, and Beaux-Arts civic architecture",
    "developmentType": "recreational",
    "buildingSubcategory": "Sports Arena",
    "aestheticCategory": "monumental_arena",
    "minFloors": 2, "maxFloors": 6, "suggestedAreaSqm": 25000, "shadeId": "#C4A265",
    "facadeDetail": {"primaryMaterial": "limestone, marble, or precast concrete with classical references", "secondaryMaterial": "arched openings, columns or pilasters", "accentMaterial": "bronze doors, carved ornament", "groundFloor": "grand arched entrance portals with classical surrounds", "upperFloors": "tiered arcaded facade reflecting seating tiers within", "cornice": "heavy classical cornice or attic story", "colorScheme": "pale stone, classical proportions, monumental scale"},
    "roofDetail": {"form": "large-span roof or open-air with classical edge treatment", "material": "steel truss with metal cladding or open bowl", "features": "distinctive roof profile, classical balustrade at rim", "aerialAppearance": "oval or circular plan with tiered seating visible"},
    "variants": [
        {"id": "arena_roman_amphitheater", "label": "Roman Amphitheater Revival",
         "description": "Modern arena directly inspired by the Roman Colosseum with tiered arched facade, classical orders, and monumental civic grandeur.",
         "prompt": "Roman Amphitheater Revival sports arena. Massive oval sports arena with a tiered facade of repeating arched openings inspired directly by the Roman Colosseum. Three tiers of arches: Doric half-columns flanking the ground-floor arches, Ionic on the second tier, Corinthian on the third. Pale travertine limestone cladding (or convincing precast concrete substitute). Each arch reveals a vaulted concourse behind. Massive arched entrance portals at the cardinal points with bronze gates. An attic story above the arches with a simple cornice. The oval plan is clearly expressed in the curved facade. The building achieves monumental civic gravitas through its direct classical quotation. Inspired by the Colosseum and neo-classical sports venues like Harvard Stadium.",
         "facadeDetail": {"primaryMaterial": "pale travertine limestone with three tiers of arched openings", "secondaryMaterial": "Doric, Ionic, Corinthian half-columns at each tier", "groundFloor": "massive arched entrance portals with bronze gates", "colorScheme": "warm travertine limestone, bronze gates, deep arch shadows"},
         "roofDetail": {"form": "open bowl (no roof) with classical balustrade at rim", "material": "open-air with stone rim"}, "palette": {"primary": "#D4C5A9"}},
        {"id": "arena_neoclassical_stadium", "label": "Neo-Classical Stadium",
         "description": "Grand neoclassical stadium with a columned entrance facade, pediment, and the civic monumentality of a Greek temple applied to a modern sports venue.",
         "prompt": "Neo-Classical stadium arena. Grand sports venue with a monumental neoclassical entrance facade: a full-width portico of massive fluted Corinthian columns supporting a triangular pediment with carved relief depicting athletic competition. Behind the classical portico, the modern stadium bowl rises, clad in pale limestone with horizontal banding. The contrast between the ceremonial classical front and the functional curved stadium mass behind creates architectural drama. Wide stone steps leading up to the portico flanked by bronze athlete statues on pedestals. Side elevations show the curved seating bowl profile in simpler limestone arcades. Inspired by Olympic stadiums with classical aspirations and Beaux-Arts civic sports buildings.",
         "facadeDetail": {"primaryMaterial": "pale limestone with monumental Corinthian portico", "secondaryMaterial": "carved pediment relief, bronze athlete statues", "groundFloor": "wide stone steps up to columned portico, bronze gates", "colorScheme": "pale limestone, white marble columns, bronze sculpture accents"},
         "roofDetail": {"form": "stadium bowl visible behind classical portico", "material": "modern steel roof structure behind classical facade"}, "palette": {"primary": "#E8DCC8"}},
        {"id": "arena_art_deco_colosseum", "label": "Art Deco Colosseum",
         "description": "Art Deco sports arena combining the oval amphitheater form with bold Deco geometric ornament, zigzag patterns, and streamlined vertical emphasis.",
         "prompt": "Art Deco Colosseum sports arena. Massive oval arena with bold Art Deco geometric facade treatment. Tall vertical piers with stepped geometric capitals rising between narrow window slots creating a dramatic vertical rhythm around the entire oval circumference. Polychrome terra cotta ornament in gold, turquoise, and deep red: zigzag chevrons, stylized athlete figures, and sunburst medallions concentrated at the entrance portals. Main entrance marked by a dramatically stepped and set-back tower element with an illuminated crown. Chrome and nickel hardware on the bronze entrance doors with geometric patterns. The building combines the power of an ancient amphitheater with the optimistic machine-age energy of Art Deco. Inspired by 1930s-era stadiums and the Deco vocabulary of the Chrysler Building applied to sports architecture.",
         "facadeDetail": {"primaryMaterial": "buff stone or cast stone with vertical piers and Deco ornament", "secondaryMaterial": "polychrome terra cotta: gold, turquoise, red zigzag patterns", "groundFloor": "stepped tower entrance with bronze doors and Deco ornament", "colorScheme": "buff stone, gold/turquoise terra cotta, chrome, stepped tower"},
         "roofDetail": {"form": "oval bowl with stepped Art Deco rim treatment", "material": "steel structure with Deco-ornamented fascia"}, "palette": {"primary": "#C4A265"}},
        {"id": "arena_beaux_arts", "label": "Beaux-Arts Arena",
         "description": "Lavish Beaux-Arts sports arena with paired columns, sculptural groups, mansard roof elements, and the civic grandeur of a Paris opera house applied to sport.",
         "prompt": "Beaux-Arts sports arena. Opulent sports venue with a lavish French Beaux-Arts facade: paired Corinthian columns flanking every bay, elaborate carved stone cartouches and garland swags between floors, sculptural figure groups representing athletic virtues crowning the main entrance pediment. Rich cream limestone facade with deeper cream stone ornamental carving creating subtle color contrasts. Mansard roof elements with copper dormers above the main entrance pavilion. Grand double-height arched entrance windows with ornate stone surrounds. Balustrade parapet with stone urns. The building treats sport as high culture, giving an arena the architectural language of an opera house. Inspired by the Paris Opera (Palais Garnier) applied to a sports arena, and Grand Central Terminal's civic grandeur.",
         "facadeDetail": {"primaryMaterial": "cream limestone with elaborate carved ornament", "secondaryMaterial": "paired Corinthian columns, sculptural groups, garland swags", "groundFloor": "grand arched entrance with ornate stone surrounds, bronze doors", "colorScheme": "cream limestone, deeper carved ornament, copper mansard, bronze"},
         "roofDetail": {"form": "mansard with copper dormers at entrance, curved bowl behind", "material": "copper mansard at front, modern structure at rear"}, "palette": {"primary": "#E8DCC8"}}
    ]
},

"high_tech_arena": {
    "id": "high_tech_arena",
    "title": "High-Tech Structural Arena",
    "description": "Contemporary sports arena celebrating structural engineering with cable-net roofs, ETFE cushions, retractable elements, and exposed steel technology",
    "developmentType": "recreational",
    "buildingSubcategory": "Sports Arena",
    "aestheticCategory": "high_tech_arena",
    "minFloors": 2, "maxFloors": 5, "suggestedAreaSqm": 30000, "shadeId": "#4682B4",
    "facadeDetail": {"primaryMaterial": "glass, ETFE, or metal cladding on steel structure", "secondaryMaterial": "exposed steel cables, masts, and tension elements", "accentMaterial": "LED media screens, dynamic lighting", "groundFloor": "transparent concourse with visible interior", "upperFloors": "dramatic structural expression", "cornice": "distinctive roof edge profile", "colorScheme": "silver steel, translucent ETFE, dramatic lighting"},
    "roofDetail": {"form": "dramatic cable-net, retractable dome, or tensile structure", "material": "ETFE, cable-net, or retractable panels", "features": "dramatic structural roof as primary feature", "aerialAppearance": "iconic roof structure visible from above"},
    "variants": [
        {"id": "arena_cable_net_roof", "label": "Cable-Net Roof",
         "description": "Arena with an iconic cable-net tensile roof structure creating a lightweight saddle or dome form suspended from steel masts.",
         "prompt": "Cable-net roof sports arena. Dramatic sports venue with an iconic tensile cable-net roof structure: a network of steel cables forming a saddle-shaped (hyperbolic paraboloid) surface stretched between tall steel compression ring and masts. The cable-net supports lightweight ETFE cushion panels that glow from within at night. The perimeter of the bowl is an elegant curved concrete concourse with full-height glass revealing the interior seating bowl. Slender raking steel masts around the perimeter support the cable edges. The roof appears to float impossibly above the arena. LED strips along the cables create dynamic color patterns at night. Inspired by the Munich Olympic Stadium by Frei Otto, Allianz Arena, and modern cable-net arenas.",
         "facadeDetail": {"primaryMaterial": "curved glass concourse with cable-net roof above", "secondaryMaterial": "steel tension masts, ETFE cushion roof panels", "groundFloor": "transparent glass concourse showing interior, steel mast bases", "colorScheme": "silver cables, white ETFE glow, glass concourse, LED accents"},
         "roofDetail": {"form": "saddle-shaped cable-net tensile structure", "material": "steel cables with ETFE cushion infill"}, "palette": {"primary": "#C0C0C0"}},
        {"id": "arena_retractable_dome", "label": "Retractable Dome",
         "description": "Arena with a mechanized retractable roof that can open to the sky, featuring visible mechanical systems and kinetic architecture.",
         "prompt": "Retractable dome sports arena. Large sports arena with a dramatic retractable roof -- shown partially open with the massive steel and glass roof segments separated to reveal the sky above the playing field. The retractable mechanism is architecturally expressed: visible steel tracks, massive bogies, and mechanical actuators. Each roof segment is a curved steel-framed panel clad in metal and glass. The fixed perimeter of the arena is a sleek curved facade of silver perforated metal panels with a corporate media screen. When open, the interior seating bowl is visible from outside. The engineering of the moving roof IS the architectural spectacle. Inspired by Mercedes-Benz Stadium Atlanta's pinwheel roof, and SoFi Stadium's translucent canopy.",
         "facadeDetail": {"primaryMaterial": "perforated metal curved facade with media screen", "secondaryMaterial": "retractable steel and glass roof segments, visible mechanism", "groundFloor": "covered entrance concourse, steel track mechanism visible", "colorScheme": "silver perforated metal, dark steel mechanism, glass, LED screen"},
         "roofDetail": {"form": "retractable segmented dome shown partially open", "material": "steel-framed panels with metal and glass cladding"}, "palette": {"primary": "#708090"}},
        {"id": "arena_exposed_steel_truss", "label": "Exposed Steel Truss",
         "description": "Arena with a massive exposed steel truss roof spanning the entire bowl, celebrating structural engineering as the primary architectural expression.",
         "prompt": "Exposed steel truss arena. Sports arena where a single massive steel truss spans the entire 120-meter width of the bowl without intermediate supports -- the truss is the building's defining feature. The triangulated steel truss is fully exposed on the exterior, rising above the seating bowl as a dramatic geometric lattice against the sky. The truss members are painted in bright white, contrasting with the dark sky. Below the truss, the arena bowl is enclosed with a curved glass and metal panel facade. Diagonal steel bracing on the facade expresses the lateral forces from the roof. The scale of the truss creates an almost bridge-like quality. Inspired by structural expressionist arenas and Pier Luigi Nervi's sports halls.",
         "facadeDetail": {"primaryMaterial": "curved glass and metal panel facade below massive truss", "secondaryMaterial": "exposed white-painted steel truss above, diagonal bracing", "groundFloor": "glass entrance concourse beneath truss, steel columns", "colorScheme": "white steel truss, dark glass facade, structural connections visible"},
         "roofDetail": {"form": "massive single-span steel truss rising above bowl", "material": "steel truss with metal deck"}, "palette": {"primary": "#E0E0E0"}},
        {"id": "arena_etfe_pillow", "label": "ETFE Pillow Facade",
         "description": "Arena wrapped in an ETFE cushion skin that glows, changes color, and creates a dramatic translucent envelope around the entire building.",
         "prompt": "ETFE pillow facade sports arena. Futuristic sports arena entirely wrapped in a skin of inflated ETFE (ethylene tetrafluoroethylene) cushion panels. The ETFE pillows create a quilted, organic-looking translucent surface that glows from within with programmable LED lighting -- currently showing warm amber. The irregular hexagonal ETFE panels are held in a steel diagrid frame that wraps continuously around walls and roof with no distinction between the two. The underlying steel structure is visible as dark shadows behind the translucent ETFE skin. At ground level, the ETFE gives way to clear glass entrance portals. The building appears as a massive glowing jewel-like form at dusk. Inspired by the Allianz Arena Munich (Herzog & de Meuron) and the Beijing Water Cube.",
         "facadeDetail": {"primaryMaterial": "inflated ETFE cushion panels in steel diagrid frame", "secondaryMaterial": "programmable LED backlighting, steel diagrid structure", "groundFloor": "clear glass entrance portals beneath ETFE skin", "colorScheme": "translucent ETFE glow (amber/white), dark steel diagrid visible behind"},
         "roofDetail": {"form": "continuous ETFE skin wrapping walls and roof", "material": "ETFE cushions in steel diagrid (same as walls)"}, "palette": {"primary": "#FFB347"}}
    ]
},

"concrete_megastructure_arena": {
    "id": "concrete_megastructure_arena",
    "title": "Concrete Megastructure Arena",
    "description": "Monumental concrete sports arena with massive sculptural concrete forms, dramatic engineering, and the raw power of reinforced concrete at monumental scale",
    "developmentType": "recreational",
    "buildingSubcategory": "Sports Arena",
    "aestheticCategory": "concrete_megastructure_arena",
    "minFloors": 2, "maxFloors": 5, "suggestedAreaSqm": 35000, "shadeId": "#696969",
    "facadeDetail": {"primaryMaterial": "exposed reinforced concrete at monumental scale", "secondaryMaterial": "board-formed concrete with visible formwork", "accentMaterial": "minimal -- concrete is the expression", "groundFloor": "massive concrete structure at ground level", "upperFloors": "sculptural concrete forms expressing structural forces", "cornice": "dramatic concrete profile against the sky", "colorScheme": "raw concrete in all its tonal variation"},
    "roofDetail": {"form": "dramatic concrete shell, dome, or cantilever", "material": "reinforced concrete", "features": "sculptural concrete roof as primary feature", "aerialAppearance": "dramatic concrete form -- dome, bowl, or folded plate"},
    "variants": [
        {"id": "arena_sweeping_concrete_bowl", "label": "Sweeping Concrete Bowl",
         "description": "Arena with a sweeping continuous concrete bowl form where the seating structure IS the exterior facade, creating a dramatic curving concrete silhouette.",
         "prompt": "Sweeping concrete bowl sports arena. Monumental arena where the reinforced concrete seating bowl is directly expressed on the exterior as a sweeping curved concrete wall. The bowl's profile curves outward and upward from a narrow base, creating a dramatic convex concrete surface that seems to defy gravity. Board-formed concrete texture with visible formwork patterns. Ramp structures spiral up the exterior, connecting concourse levels. Continuous horizontal bands of deeply recessed slot windows between the seating tiers create dark shadow lines on the concrete surface. The building's form is a pure expression of the seating geometry within -- no applied cladding, no decoration. At the rim, the concrete edge creates a sharp silhouette against the sky. Inspired by Pier Luigi Nervi's Palazzetto dello Sport and Oscar Niemeyer's sports venues.",
         "facadeDetail": {"primaryMaterial": "sweeping curved board-formed concrete bowl exterior", "secondaryMaterial": "spiral concrete ramps, deeply recessed slot windows", "groundFloor": "concrete base where bowl meets ground, entrance beneath overhang", "colorScheme": "raw grey concrete with formwork texture, deep shadow slots"},
         "roofDetail": {"form": "concrete bowl rim as roofline, may be open-air or thin shell dome", "material": "reinforced concrete"}, "palette": {"primary": "#808080"}},
        {"id": "arena_flying_buttress_stadium", "label": "Flying Buttress Stadium",
         "description": "Stadium with massive concrete flying buttresses radiating from the bowl, expressing the structural forces of the cantilevered seating tiers.",
         "prompt": "Flying buttress sports stadium. Dramatic stadium with massive reinforced concrete flying buttresses radiating outward from the seating bowl at regular intervals around the circumference. Each buttress is a bold sculptural concrete element angled outward, supporting the cantilevered upper seating tiers and the roof structure. Between the buttresses, the concourse is fully glazed, revealing the concourse circulation and the excitement within. The buttresses cast dramatic angular shadows on the glass walls between them. From a distance, the radiating buttresses create a crown-like or flower-like silhouette. The structural logic is immediately legible: the buttresses push outward to resist the inward pull of the cantilevered tiers. Inspired by Brasilia's National Stadium, Pier Luigi Nervi's Flaminio Stadium, and Gothic cathedral structural principles.",
         "facadeDetail": {"primaryMaterial": "massive concrete flying buttresses radiating from bowl", "secondaryMaterial": "glass curtain walls between buttresses", "groundFloor": "entrance between buttress bases, glazed concourse", "colorScheme": "raw concrete buttresses, clear glass between, dramatic shadows"},
         "roofDetail": {"form": "cantilevered roof supported by the buttress system", "material": "concrete and steel cantilevered from buttresses"}, "palette": {"primary": "#909090"}},
        {"id": "arena_ribbed_concrete_dome", "label": "Ribbed Concrete Dome",
         "description": "Arena with a dramatic thin-shell ribbed concrete dome spanning the entire bowl, creating a soaring interior and iconic exterior profile.",
         "prompt": "Ribbed concrete dome sports arena. Arena covered by a magnificent thin-shell reinforced concrete dome with bold exposed concrete ribs radiating from the apex like the spokes of a wheel. The ribs are visible on both interior and exterior, creating a dramatic sunflower-like pattern on the dome surface. Between the ribs, the shell panels are thinner, with some replaced by triangular glazed panels allowing natural light to enter in dramatic shafts. The dome springs from a low circular concrete ring beam at the top of the seating bowl. From the street, the dome's profile dominates the skyline -- a perfect hemisphere in raw concrete. The engineering achievement of the clear-span dome IS the architecture. Inspired by Nervi's Palazzetto dello Sport, the Pantheon's dome principle, and Kenzo Tange's Olympic Gymnasium.",
         "facadeDetail": {"primaryMaterial": "thin-shell concrete dome with exposed radiating ribs", "secondaryMaterial": "triangular glazed panels between ribs, concrete ring beam", "groundFloor": "entrance beneath dome overhang, curved concrete base", "colorScheme": "raw concrete dome with rib shadows, glazed triangular panels"},
         "roofDetail": {"form": "ribbed concrete dome spanning entire bowl", "material": "thin-shell reinforced concrete with glazed infill panels"}, "palette": {"primary": "#A0A0A0"}},
        {"id": "arena_monolithic_pier", "label": "Monolithic Pier",
         "description": "Arena supported on massive monolithic concrete piers or columns, lifting the entire bowl above ground and creating a dramatic colonnade underneath.",
         "prompt": "Monolithic pier sports arena. Massive sports arena elevated entirely above ground on enormous monolithic concrete piers -- the entire seating bowl is lifted one full story above grade on tapering concrete columns, creating a dramatic covered colonnade underneath for pedestrian circulation and entrance. The concrete piers are Y-shaped or mushroom-headed, supporting the slab of the arena floor above. The bowl rises above the piers as a continuous concrete wall. The ground level beneath the elevated bowl is a vast shaded public plaza. The piers are raw board-formed concrete with visible formwork tie holes. Stairs and ramps ascend through the piers to the concourse level. The building appears to hover above the landscape on its massive supports. Inspired by Le Corbusier's pilotis concept applied at monumental scale, and Brasilia's institutional buildings.",
         "facadeDetail": {"primaryMaterial": "massive concrete Y-piers supporting elevated bowl", "secondaryMaterial": "concrete bowl wall above, covered plaza below", "groundFloor": "vast covered public plaza beneath elevated bowl, pier bases", "colorScheme": "raw concrete piers, concrete bowl, shaded plaza beneath"},
         "roofDetail": {"form": "concrete bowl rim, possible tensile roof canopy", "material": "reinforced concrete"}, "palette": {"primary": "#7A7A7A"}}
    ]
},

# ============================================================
# HOTELS
# ============================================================
"chateauesque_hotel": {
    "id": "chateauesque_hotel",
    "title": "Chateauesque / Grand Railway Hotel",
    "description": "Grand historic hotel in the Chateauesque style with turrets, steep copper roofs, ornate stone facades, and the romantic grandeur of French Renaissance castle architecture",
    "developmentType": "hospitality",
    "buildingSubcategory": "Hotels",
    "aestheticCategory": "chateauesque_hotel",
    "minFloors": 4, "maxFloors": 12, "suggestedAreaSqm": 15000, "shadeId": "#8B6914",
    "facadeDetail": {"primaryMaterial": "limestone or sandstone with ornate carved details", "secondaryMaterial": "copper steep roofs, turrets, dormers", "accentMaterial": "carved stone crests, iron balconettes, copper finials", "groundFloor": "grand porte-cochere entrance with carved stone surround", "upperFloors": "tall windows with stone surrounds, balconettes, turrets at corners", "cornice": "steep copper roof with dormers and turrets above ornate stone cornice", "colorScheme": "warm stone, green copper roofs, ornate carved details"},
    "roofDetail": {"form": "steep chateau roof with turrets, dormers, and copper", "material": "copper with verdigris patina", "features": "conical turret roofs, elaborate copper dormers, carved stone finials", "aerialAppearance": "dramatic green copper roofscape with turrets and dormers"},
    "variants": [
        {"id": "hotel_scottish_baronial", "label": "Scottish Baronial",
         "description": "Grand Scottish Baronial hotel with round towers, crow-stepped gables, bartizans, and the romantic castle imagery of the Scottish Highlands.",
         "prompt": "Scottish Baronial grand hotel. Romantic castle-like hotel in Scottish Baronial style with round corner towers topped with conical slate roofs (pepper-pot turrets), crow-stepped (corbie-stepped) gables creating a distinctive stepped silhouette, and bartizans (small projecting turrets) at upper corners. Walls of rough-cut Scottish granite in warm pink-grey tones. Small deeply recessed windows with stone mullions on the towers, larger windows on the main block. Grand entrance through a pointed arch in a square tower with crenellations. Baronial hall window: a massive pointed-arch window illuminating the main staircase. Hotel name carved in stone above the entrance. Surrounding highland landscape with manicured grounds. Inspired by Balmoral Castle, the Banff Springs Hotel, and Gleneagles.",
         "facadeDetail": {"primaryMaterial": "rough-cut pink-grey Scottish granite", "secondaryMaterial": "round towers with conical roofs, crow-stepped gables, bartizans", "groundFloor": "pointed-arch entrance in square tower with crenellations", "colorScheme": "pink-grey granite, dark slate turret caps, deep window recesses"},
         "roofDetail": {"form": "steep slate with conical tower caps and crow-stepped gables", "material": "dark slate, conical slate turret roofs"}, "palette": {"primary": "#9E8E7E"}},
        {"id": "hotel_french_renaissance", "label": "French Renaissance Revival",
         "description": "Opulent French Renaissance Revival hotel with mansard roofs, ornate dormers, carved pilasters, and the grandeur of a Loire Valley chateau.",
         "prompt": "French Renaissance Revival grand hotel. Opulent hotel inspired by Loire Valley chateaux with a dramatic steep mansard roof clad in patterned dark slate with elaborate copper-roofed dormers projecting from every bay. Walls of smooth pale cream limestone with richly carved details: pilasters with Composite capitals between every window bay, carved stone cartouches and garland swags above windows, carved stone balustrades at every level. Corner pavilion towers with taller mansard roofs and copper finials. Grand porte-cochere entrance with carved caryatid figures supporting the canopy. Tall arched windows on the piano nobile (first floor) with French doors opening to stone balconies. The richness of ornamental carving creates deep shadow and visual complexity. Inspired by Chateau de Chambord, the Banff Springs Hotel entrance, and the Frontenac.",
         "facadeDetail": {"primaryMaterial": "smooth cream limestone with elaborate carved ornament", "secondaryMaterial": "mansard roof with patterned slate and copper dormers", "groundFloor": "grand porte-cochere with carved caryatids, arched entrance", "colorScheme": "cream limestone, dark patterned slate mansard, copper dormers and finials"},
         "roofDetail": {"form": "steep mansard with elaborate copper dormers and corner pavilion towers", "material": "patterned dark slate with copper dormers and finials"}, "palette": {"primary": "#E8DCC8"}},
        {"id": "hotel_gothic_revival_grand", "label": "Gothic Revival Grand",
         "description": "Grand Gothic Revival hotel with pointed arches, pinnacles, tracery windows, and medieval-inspired grandeur creating a fairytale silhouette.",
         "prompt": "Gothic Revival grand hotel. Towering hotel with an elaborate Gothic Revival facade: clusters of slender pinnacles and spires rising from every corner and roofline creating a fairytale silhouette against the sky. Pointed-arch windows with stone tracery (trefoils and quatrefoils) throughout. A massive pointed-arch porte-cochere entrance with elaborate carved stone hood molding and a heraldic crest above. Flying buttresses on the chapel-like wing. Walls of warm buff limestone with carved Gothic ornament concentrated at the entrance and skyline. Tall multi-story bay windows with Gothic tracery. The building combines the verticality of a Gothic cathedral with the horizontal extent of a grand hotel. Oriel windows projecting from upper floors. Inspired by St Pancras Renaissance Hotel London and the Parliament Buildings Ottawa.",
         "facadeDetail": {"primaryMaterial": "warm buff limestone with Gothic carved ornament", "secondaryMaterial": "pointed-arch windows with tracery, pinnacles and spires", "groundFloor": "massive pointed-arch porte-cochere with heraldic carving", "colorScheme": "warm buff limestone, dark slate roofs, pinnacles silhouetted against sky"},
         "roofDetail": {"form": "steep pitched with forest of pinnacles and spires", "material": "dark slate with stone pinnacles and copper finials"}, "palette": {"primary": "#C4A87C"}},
        {"id": "hotel_alpine_chateau", "label": "Alpine Chateau",
         "description": "Alpine chateau hotel with deep overhanging eaves, timber balconies, stone and timber construction, and the warm hospitality aesthetic of Swiss and Austrian mountain lodges.",
         "prompt": "Alpine chateau grand hotel. Warm and inviting mountain hotel combining a heavy stone base with elaborate timber upper floors in traditional Alpine chateau style. Ground and first floors of massive rough-cut stone (local granite or limestone). Upper floors of dark stained timber frame with white-plastered infill panels and carved timber balconies wrapping every guest room. Deeply overhanging gable roof with exposed ornately carved timber brackets and rafter tails. Heavy timber shutters on every window with carved heart or edelweiss motifs. Main entrance through a stone arch with a carved timber canopy. Steeply pitched roof with multiple dormers and a central tower. Flower boxes overflowing with red geraniums on every balcony. Mountain backdrop suggested. Inspired by the Badrutt's Palace St. Moritz, Chateau Lake Louise, and traditional Engadin architecture.",
         "facadeDetail": {"primaryMaterial": "rough-cut stone base, dark timber frame upper floors", "secondaryMaterial": "carved timber balconies, white plaster infill, carved shutters", "groundFloor": "massive stone arch entrance with timber canopy", "colorScheme": "grey stone, dark stained timber, white plaster, red geranium accents"},
         "roofDetail": {"form": "steeply pitched gable with deep eaves and carved timber brackets", "material": "dark slate or wood shingle with ornate timber details"}, "palette": {"primary": "#5C4033"}}
    ]
},

"resort_modernism_hotel": {
    "id": "resort_modernism_hotel",
    "title": "Resort Modernism Hotel",
    "description": "Mid-century and contemporary resort hotel with regional modernist design, climate-responsive architecture, and vacation destination aesthetics",
    "developmentType": "hospitality",
    "buildingSubcategory": "Hotels",
    "aestheticCategory": "resort_modernism",
    "minFloors": 1, "maxFloors": 6, "suggestedAreaSqm": 8000, "shadeId": "#20B2AA",
    "facadeDetail": {"primaryMaterial": "regional materials adapted to climate", "secondaryMaterial": "extensive glazing, outdoor living spaces", "accentMaterial": "tropical plantings, water features", "groundFloor": "open-air lobby connecting to pool and landscape", "upperFloors": "guest room balconies with climate-responsive design", "cornice": "varies by regional style", "colorScheme": "climate-appropriate palette"},
    "roofDetail": {"form": "varies by regional style", "material": "regional roofing materials", "features": "varies by climate", "aerialAppearance": "varies by regional style with pool and landscape visible"},
    "variants": [
        {"id": "hotel_balinese_villa", "label": "Balinese Villa",
         "description": "Tropical Balinese villa resort with thatched alang-alang roofs, open-air pavilions, reflecting pools, and the spiritual serenity of traditional Balinese architecture.",
         "prompt": "Balinese villa resort hotel. Serene tropical hotel complex of interconnected open-air pavilions with steeply pitched thatched alang-alang (grass) roofs supported by carved stone columns. No glass walls -- the spaces are open to the tropical garden with flowing white curtains that billow in the breeze. Central infinity pool with a carved stone temple-gate (split gate / candi bentar) entrance feature. Rough-cut volcanic stone walls and floors. Carved stone water features and lotus ponds. Frangipani trees and tropical planting throughout. Teak wood furniture visible in the open pavilions. Stone pathway of irregular stepping stones crossing a shallow reflecting pool. Traditional Balinese stone carved guardian statues flanking the entrance. Inspired by Aman Resorts Bali and traditional Balinese compound architecture.",
         "facadeDetail": {"primaryMaterial": "carved volcanic stone columns and walls", "secondaryMaterial": "thatched alang-alang grass roofs, open-air pavilions", "groundFloor": "open pavilions with flowing curtains, stone split-gate entrance", "colorScheme": "grey volcanic stone, golden thatch, tropical green, teak wood"},
         "roofDetail": {"form": "steeply pitched traditional Balinese thatch", "material": "alang-alang grass thatch"}, "palette": {"primary": "#8B7355"}},
        {"id": "hotel_miami_art_deco", "label": "Miami Beach Art Deco",
         "description": "Iconic Miami Beach Art Deco hotel with pastel colors, nautical motifs, neon signage, and the glamorous streamlined aesthetic of 1930s Ocean Drive.",
         "prompt": "Miami Beach Art Deco hotel. Iconic three-story Ocean Drive hotel in classic Miami Art Deco style. Smooth white stucco facade with pastel accents: mint-green horizontal speed lines (racing stripes), coral-pink geometric window surrounds, and a lavender accent band at the parapet. Streamlined rounded corners on the building mass. Central vertical tower element with the hotel name in classic neon script lettering (currently unlit, daytime). Porthole windows, ship-rail chrome balcony railings, and nautical motifs in the stucco decoration. Continuous horizontal eyebrow shade ledges over the windows. Flat roof with an Art Deco parapet featuring stepped geometric ornament. Sidewalk cafe with striped awning at street level. Palm trees flanking the entrance. Terrazzo entrance steps. Inspired by the Colony Hotel, Carlyle Hotel, and Breakwater Hotel on Ocean Drive.",
         "facadeDetail": {"primaryMaterial": "smooth white stucco with pastel geometric accents", "secondaryMaterial": "neon hotel signage, nautical chrome details, porthole windows", "groundFloor": "sidewalk cafe with striped awning, terrazzo entrance steps", "colorScheme": "white stucco, mint-green, coral-pink, lavender accents, chrome"},
         "roofDetail": {"form": "flat with stepped Art Deco parapet and tower element", "material": "white stucco parapet"}, "palette": {"primary": "#98D4BB"}},
        {"id": "hotel_brutalist_resort", "label": "Brutalist Resort",
         "description": "Bold Brutalist resort hotel with raw concrete, dramatic cantilevers, and the uncompromising material honesty of concrete applied to tropical leisure.",
         "prompt": "Brutalist resort hotel. Dramatic resort hotel in raw board-formed concrete with bold geometric forms set against a tropical landscape. Massive concrete cantilevers project guest room balconies outward over a pool deck below. The concrete is left raw and unfinished with visible wood-grain formwork texture, contrasting dramatically with the lush tropical vegetation growing up and around the concrete forms. Deep concrete brise-soleil sunshading on the west facade creates geometric shadow patterns. Open concrete colonnade at ground level connecting to an infinity pool. Concrete spiral staircase visible on the exterior. The brutal honesty of the concrete is softened by cascading tropical vines and bougainvillea growing from planter boxes integrated into the concrete. Inspired by brutalist resort hotels in Cancun, Hayman Island, and Paulo Mendes da Rocha's concrete houses.",
         "facadeDetail": {"primaryMaterial": "raw board-formed concrete with wood-grain texture", "secondaryMaterial": "concrete brise-soleil, cantilevered balconies", "groundFloor": "open concrete colonnade connecting to pool, tropical plants", "colorScheme": "raw grey concrete, lush green tropical vegetation, blue pool"},
         "roofDetail": {"form": "flat concrete with cantilevered upper levels", "material": "exposed concrete slab"}, "palette": {"primary": "#808080"}},
        {"id": "hotel_eco_lodge", "label": "Eco-Lodge Vernacular",
         "description": "Sustainable eco-lodge hotel using local vernacular materials, passive design strategies, and minimal environmental impact.",
         "prompt": "Eco-lodge vernacular hotel. Low-impact sustainable lodge hotel using locally sourced natural materials and passive design. Buildings of rammed earth walls with visible horizontal earth-layer stratification in warm ochre and sienna tones. Thatched or living roof (sedum and wildflowers) merging with the landscape. Deep covered verandas with local timber posts and beams providing shade and rain protection. Operable timber louver screens for natural ventilation and privacy. Rainwater collection visible as timber gutters flowing to stone cisterns. Solar water heating panels discreetly integrated on south-facing roof slopes. Composting garden visible. Natural stone pathways between buildings. The architecture is almost camouflaged in its landscape, emerging gently from the terrain. Inspired by &Beyond and Singita safari lodges, and contemporary rammed earth eco-resorts.",
         "facadeDetail": {"primaryMaterial": "rammed earth walls with visible stratification layers", "secondaryMaterial": "local timber post-and-beam verandas, timber louver screens", "groundFloor": "deep covered veranda with timber columns, stone pathways", "colorScheme": "warm earth tones (ochre, sienna, umber), natural timber, green roof"},
         "roofDetail": {"form": "low-pitched with living roof or thatch merging with landscape", "material": "living sedum/wildflower roof or natural thatch"}, "palette": {"primary": "#C4A87C"}}
    ]
},

"corporate_tower_hotel": {
    "id": "corporate_tower_hotel",
    "title": "Corporate Tower Hotel",
    "description": "Modern high-rise hotel tower with glass curtain walls, atrium lobbies, and the sleek commercial aesthetic of international business hospitality",
    "developmentType": "hospitality",
    "buildingSubcategory": "Hotels",
    "aestheticCategory": "corporate_tower_hotel",
    "minFloors": 10, "maxFloors": 50, "suggestedAreaSqm": 20000, "shadeId": "#4682B4",
    "facadeDetail": {"primaryMaterial": "glass curtain wall or metal and glass cladding", "secondaryMaterial": "aluminum mullion system, stone or metal base", "accentMaterial": "porte-cochere, branded signage, night lighting", "groundFloor": "grand lobby entrance with porte-cochere", "upperFloors": "repetitive guest room window grid, possible atrium void", "cornice": "clean top or distinctive crown", "colorScheme": "glass, metal, stone base, branded accent colors"},
    "roofDetail": {"form": "flat or distinctive crown/cap", "material": "mechanical penthouse with architectural screen", "features": "rooftop bar or pool on some variants", "aerialAppearance": "flat top or distinctive cap with mechanical equipment"},
    "variants": [
        {"id": "hotel_glass_curtain_wall", "label": "Glass Curtain Wall",
         "description": "Sleek all-glass curtain wall hotel tower reflecting the sky and surrounding city, with a minimal frameless aesthetic.",
         "prompt": "Glass curtain wall hotel tower. Sleek modern high-rise hotel tower with a fully glazed curtain wall facade reflecting the sky, clouds, and surrounding buildings. The glass is a high-performance tinted blue-green with minimal visible aluminum mullions creating a seamless reflective surface. The tower tapers slightly toward the top. A dramatic cantilevered glass and steel porte-cochere marks the hotel entrance at ground level with valet parking beneath. Polished stone lobby interior visible through the glass ground floor. The hotel brand logo is subtly embedded in the glass at the top. At dusk, the interior guest room lights create a warm grid pattern behind the reflective glass. Revolving door entrance with brass trim. Inspired by international luxury hotel chains: Ritz-Carlton, Four Seasons, and Park Hyatt tower designs.",
         "facadeDetail": {"primaryMaterial": "high-performance blue-green tinted glass curtain wall", "secondaryMaterial": "minimal aluminum mullions, stone lobby visible at ground", "groundFloor": "cantilevered glass porte-cochere, polished stone lobby", "colorScheme": "blue-green reflective glass, brass entrance details, warm interior glow"},
         "roofDetail": {"form": "clean flat top with subtle crown lighting", "material": "flat with mechanical penthouse screen"}, "palette": {"primary": "#4682B4"}},
        {"id": "hotel_portman_atrium", "label": "John Portman Atrium Style",
         "description": "Hotel with a soaring interior atrium void running the full height of the building, with glass elevators and interior balcony corridors -- the signature of John Portman's revolutionary hotel design.",
         "prompt": "John Portman atrium hotel. Hotel tower with a spectacular full-height interior atrium visible through a massive glass wall on the facade. The atrium is a soaring void running the entire height of the building (20+ stories) with interior balcony corridors (galleries) running around all four sides at every floor, planted with trailing vines and greenery. Glass capsule elevators rise through the atrium void, visible from outside. The atrium floor features a water feature and lush tropical planting. From the exterior, the glass wall reveals the entire dramatic interior atrium and its capsule elevators. The remaining three sides are conventional hotel room facades in precast concrete with regular window grids. The atrium side is the architectural spectacle. Inspired by John Portman's Hyatt Regency Atlanta (1967), Marriott Marquis, and Renaissance Center.",
         "facadeDetail": {"primaryMaterial": "full-height glass wall revealing interior atrium", "secondaryMaterial": "precast concrete on other facades, glass capsule elevators", "groundFloor": "glass atrium wall showing tropical lobby, grand entrance", "colorScheme": "glass atrium wall, warm precast concrete, green interior planting"},
         "roofDetail": {"form": "flat with glass atrium skylight", "material": "glass atrium roof, concrete on solid portions"}, "palette": {"primary": "#C0C0C0"}},
        {"id": "hotel_minimalist_slab", "label": "Minimalist Slab",
         "description": "Ultra-minimal hotel slab with a restrained material palette, precise detailing, and the quiet luxury of architectural minimalism.",
         "prompt": "Minimalist slab hotel. Refined rectangular slab hotel tower with a rigorously minimal aesthetic. Facade of pale matte precast concrete panels with hairline joints and flush frameless windows -- the glass sits perfectly flush with the concrete surface creating a seamless plane. No projections, no balconies, no applied ornament. The building is a perfect rectangular prism with razor-sharp edges. Ground floor set back behind ultra-thin steel columns with full-height frameless glass. Discreet hotel entrance marked only by a thin brass strip and a recessed door. The building achieves luxury through material precision and restraint rather than excess. At night, the warm guest room lighting creates a lantern-like glow through the flush windows. Inspired by David Chipperfield, John Pawson, and Tadao Ando's approach to hotel design.",
         "facadeDetail": {"primaryMaterial": "pale matte precast concrete with hairline joints", "secondaryMaterial": "frameless flush-mounted windows, ultra-thin steel columns", "groundFloor": "set back glass lobby behind thin columns, discreet brass entrance", "colorScheme": "pale matte concrete, frameless glass, brass entrance, warm glow"},
         "roofDetail": {"form": "razor-flat top with invisible parapet", "material": "hidden membrane"}, "palette": {"primary": "#E0DDD5"}},
        {"id": "hotel_postmodern_skyscraper", "label": "Postmodern Skyscraper",
         "description": "Postmodern hotel skyscraper with a distinctive top (broken pediment, pyramid, or crown), contextual references, and the colorful eclecticism of 1980s corporate architecture.",
         "prompt": "Postmodern skyscraper hotel. Bold postmodern hotel tower with a highly distinctive top: a massive broken pediment or stepped pyramid crown in contrasting material (pink granite against grey glass) creating an instantly recognizable skyline profile. The tower body combines reflective glass with horizontal bands of polished granite in two contrasting colors (grey and warm pink or red). Monumental entrance portico with oversized classical columns supporting an abstract pediment -- classical elements used at exaggerated scale. The ground floor features a dramatic double-height lobby visible through a grand arch. Corner setbacks and notches break up the box form. Decorative metalwork in gold anodized aluminum. The building is confident, colorful, and deliberately memorable. Inspired by Michael Graves' Portland Building, Philip Johnson's AT&T Building (now 550 Madison), and postmodern Marriott and Westin towers of the 1980s.",
         "facadeDetail": {"primaryMaterial": "reflective glass with horizontal polished granite bands", "secondaryMaterial": "distinctive crown in pink granite, oversized classical entrance", "groundFloor": "monumental entrance arch with oversized columns, double-height lobby", "colorScheme": "grey glass, pink and grey granite bands, gold aluminum accents"},
         "roofDetail": {"form": "distinctive crown: broken pediment or stepped pyramid in pink granite", "material": "granite-clad crown with glass accents"}, "palette": {"primary": "#BC8F8F"}}
    ]
},

# ============================================================
# TRANSIT STATIONS
# ============================================================
"historic_grand_station": {
    "id": "historic_grand_station",
    "title": "Historic Grand Station",
    "description": "Monumental historic railway terminal combining grand civic architecture with the engineering spectacle of iron and glass train sheds",
    "developmentType": "institutional",
    "buildingSubcategory": "Transit Station",
    "aestheticCategory": "historic_grand_station",
    "minFloors": 2, "maxFloors": 5, "suggestedAreaSqm": 15000, "shadeId": "#8B7355",
    "facadeDetail": {"primaryMaterial": "stone or brick monumental facade", "secondaryMaterial": "iron and glass train shed behind", "accentMaterial": "clock tower, carved ornament", "groundFloor": "grand arched entrance portals", "upperFloors": "hotel or office space above concourse", "cornice": "ornate classical cornice or train shed profile visible", "colorScheme": "warm stone, iron structure, glass"},
    "roofDetail": {"form": "iron and glass arched train shed", "material": "iron/steel and glass", "features": "arched train shed spanning tracks, clock tower", "aerialAppearance": "arched glass train shed behind stone head building"},
    "variants": [
        {"id": "station_beaux_arts", "label": "Beaux-Arts Terminal",
         "description": "Grand Beaux-Arts railway terminal with monumental classical facade, vaulted concourse, and the civic grandeur of early 20th-century rail travel.",
         "prompt": "Beaux-Arts railway terminal. Grand monumental railway station with a lavish Beaux-Arts facade of pale granite with paired Corinthian columns flanking three massive arched entrance portals. Elaborate carved stone sculpture groups above the arches depicting Transportation and Progress. An ornate clock centered in the facade. Behind the stone head building, the iron and glass arched train shed roof is visible, spanning over the platforms. Grand double-height arched windows flood the main concourse with light. Stone balustrade parapet with stone eagles or urns. Bronze entrance doors with geometric patterns. The building treats railway travel as a grand civic ceremony. Inspired by Grand Central Terminal New York, Union Station Washington DC, and Pennsylvania Station.",
         "facadeDetail": {"primaryMaterial": "pale granite with paired Corinthian columns", "secondaryMaterial": "massive arched entrance portals, carved sculpture groups", "groundFloor": "three grand arched entrances with bronze doors, stone steps", "colorScheme": "pale granite, carved stone, bronze doors, train shed iron behind"},
         "roofDetail": {"form": "stone head building with iron/glass train shed behind", "material": "granite on head building, iron and glass arch over tracks"}, "palette": {"primary": "#D4C5A9"}},
        {"id": "station_victorian_iron_glass", "label": "Victorian Iron & Glass",
         "description": "Victorian railway station with an enormous wrought-iron and glass arched train shed creating a cathedral of engineering behind a more modest brick head building.",
         "prompt": "Victorian iron and glass railway station. Railway station dominated by an enormous single-span wrought-iron arched train shed -- a soaring crescent-shaped arch of iron ribs and glass panels spanning 70+ meters over the tracks. The iron structure is painted in Victorian engineering colors: deep red oxide or dark green. The train shed dwarfs the brick head building in front, which is a more modest Victorian Gothic or Italianate structure with arched windows and a clock tower. The contrast between the ornate but small brick facade and the vast engineered iron shed behind creates the drama. Inside the shed, wrought-iron columns with ornate cast-iron capitals support the mezzanine. Ornate iron cresting along the ridge. Inspired by St Pancras Station by Barlow, Paddington Station by Brunel, and York Station.",
         "facadeDetail": {"primaryMaterial": "massive wrought-iron train shed arch visible above brick head building", "secondaryMaterial": "Victorian brick head building with clock tower", "groundFloor": "brick arched entrance beneath iron shed, clock tower", "colorScheme": "deep red/green painted iron, red brick, glass train shed"},
         "roofDetail": {"form": "massive single-span iron arch train shed", "material": "wrought-iron ribs with glass panel infill"}, "palette": {"primary": "#8B4513"}},
        {"id": "station_art_deco_terminal", "label": "Art Deco Terminal",
         "description": "Streamlined Art Deco railway or bus terminal with geometric ornament, stepped massing, and the optimistic machine-age aesthetic of 1930s transport architecture.",
         "prompt": "Art Deco railway terminal. Streamlined 1930s transport terminal with a bold symmetrical Art Deco facade. Central stepped tower with an illuminated clock and geometric sunburst ornament in polychrome terra cotta (gold and turquoise). Smooth buff limestone walls with incised geometric speed lines suggesting movement and modernity. Large arched entrance with geometric bronze doors featuring stylized locomotive motifs. Horizontal ribbon windows with chrome frames. Streamlined curved corners. Interior concourse visible through the arch: a grand space with geometric ceiling patterns and period lighting fixtures. Terrazzo floor with geometric compass rose pattern. The building embodies the romance and optimism of the golden age of rail travel. Inspired by Cincinnati Union Terminal, Buffalo Central Terminal, and Helsinki Central Station.",
         "facadeDetail": {"primaryMaterial": "smooth buff limestone with Art Deco geometric ornament", "secondaryMaterial": "polychrome terra cotta (gold, turquoise) on tower, chrome frames", "groundFloor": "large arched entrance with geometric bronze doors, terrazzo floor", "colorScheme": "buff limestone, gold/turquoise terra cotta, chrome, bronze"},
         "roofDetail": {"form": "stepped tower with illuminated geometric crown", "material": "limestone with terra cotta ornament"}, "palette": {"primary": "#C4A265"}},
        {"id": "station_neo_romanesque", "label": "Neo-Romanesque Station",
         "description": "Richardsonian Romanesque railway station with massive round-arched entrance, rusticated stone, and the powerful civic presence of H.H. Richardson's designs.",
         "prompt": "Neo-Romanesque railway station. Powerful railway station in Richardsonian Romanesque style with a massive round-arched entrance portal of enormous rusticated brownstone voussoirs. Walls of rock-faced granite in warm grey-pink tones with deep mortar joints. Round-arched windows grouped in triplets with stone colonettes between. Square clock tower with a pyramidal slate roof rising from one end. Deeply recessed entrance arch creating a dark dramatic threshold. Stone corbel table cornice. The building conveys civic power through sheer mass and weight of stone. Waiting room wing with large round-arched windows letting light into the double-height interior. The massive rusticated stone gives the building an almost geological permanence. Inspired by H.H. Richardson's stations (especially Albany and New London), and Romanesque civic architecture.",
         "facadeDetail": {"primaryMaterial": "rock-faced granite with massive rusticated arches", "secondaryMaterial": "brownstone voussoirs, stone colonettes, clock tower", "groundFloor": "massive round-arched entrance of rusticated stone", "colorScheme": "warm grey-pink granite, brownstone arches, dark slate tower roof"},
         "roofDetail": {"form": "hipped with square clock tower and pyramidal cap", "material": "dark slate"}, "palette": {"primary": "#9E8E7E"}}
    ]
},

"contemporary_transit_hub": {
    "id": "contemporary_transit_hub",
    "title": "Contemporary Transit Hub",
    "description": "Iconic contemporary transit station with dramatic structural forms, advanced materials, and the station as a landmark civic gateway",
    "developmentType": "institutional",
    "buildingSubcategory": "Transit Station",
    "aestheticCategory": "contemporary_transit",
    "minFloors": 1, "maxFloors": 4, "suggestedAreaSqm": 10000, "shadeId": "#E0E0E0",
    "facadeDetail": {"primaryMaterial": "glass, steel, ETFE, or white concrete", "secondaryMaterial": "dramatic structural elements as architecture", "accentMaterial": "integrated wayfinding, dynamic lighting", "groundFloor": "transparent concourse connecting modes of transport", "upperFloors": "dramatic roof structure above open concourse", "cornice": "distinctive structural roof profile", "colorScheme": "white, glass, steel, dramatic form"},
    "roofDetail": {"form": "iconic sculptural roof structure", "material": "steel and glass or ETFE", "features": "dramatic roof as primary architectural feature", "aerialAppearance": "iconic roof form visible as urban landmark"},
    "variants": [
        {"id": "transit_calatrava_organic", "label": "Santiago Calatrava Organic",
         "description": "Organic skeletal transit hub with bone-like white steel ribs, soaring wing-like canopy, and biomorphic structural forms. Inspired by Calatrava's stations.",
         "prompt": "Calatrava-style organic transit hub. Dramatic transit station with a soaring white steel skeletal structure resembling the ribcage of a vast creature or the spread wings of a bird. Tapered white steel ribs arch up and over the concourse, meeting at a central spine ridge. Between the ribs, triangular glass panels fill the spaces creating a luminous canopy. The steel ribs are not straight -- they curve and taper organically like bones, with visible pin connections at each joint. The entire structure appears to be alive, about to take flight. Below the soaring canopy, the concourse floor is a clean white marble expanse. The white steel structure against a blue sky creates an instantly iconic landmark. Inspired by Santiago Calatrava's Oculus at WTC New York, Lyon-Saint Exupery station, and Liege-Guillemins.",
         "facadeDetail": {"primaryMaterial": "tapered white steel skeletal ribs with glass infill", "secondaryMaterial": "white marble concourse floor, pin-joint connections", "groundFloor": "open glazed concourse beneath soaring skeletal canopy", "colorScheme": "pure white steel ribs, clear glass, white marble, blue sky"},
         "roofDetail": {"form": "soaring wing-like skeletal canopy of white steel ribs", "material": "white steel ribs with triangular glass panels"}, "palette": {"primary": "#F5F5F5"}},
        {"id": "transit_high_tech_glass", "label": "High-Tech Glass Canopy",
         "description": "High-tech transit station with a vast glass canopy supported by minimal tree-like steel columns, creating a light-filled covered concourse.",
         "prompt": "High-tech glass canopy transit hub. Major transit station covered by a vast undulating glass canopy supported by slender tree-like (dendriform) steel columns that branch outward at the top to support the glass panels above. The glass roof appears to float on minimal supports, flooding the concourse with natural light. Stainless steel spider fittings connect the glass panels. The canopy edge is a clean frameless glass line. Below, the concourse is a clean open space with polished concrete floors and integrated wayfinding signage. Escalators and stairs descend to platform levels below. The transparency and lightness of the structure makes the station feel outdoor while being fully sheltered. Inspired by Norman Foster's Canary Wharf station, Stansted Airport, and Stuttgart train station.",
         "facadeDetail": {"primaryMaterial": "vast glass canopy on tree-like steel columns", "secondaryMaterial": "stainless steel spider fittings, polished concrete floor", "groundFloor": "open concourse beneath floating glass roof, escalators down", "colorScheme": "clear glass, silver steel columns, polished concrete, minimal"},
         "roofDetail": {"form": "undulating glass canopy on dendriform columns", "material": "glass panels with stainless steel fittings"}, "palette": {"primary": "#E8E8E8"}},
        {"id": "transit_parametric_timber", "label": "Parametric Timber Shell",
         "description": "Transit station with a parametrically-designed curved timber shell roof creating a warm, organic interior space from digitally-fabricated timber elements.",
         "prompt": "Parametric timber shell transit station. Transit hub covered by a dramatic parametrically-designed curved timber shell -- a flowing organic double-curved surface constructed from hundreds of unique CNC-cut timber ribs and laths creating a warm wooden lattice canopy. The timber shell is open at the sides, rising from ground level and arching over the platforms. Natural light filters through the gaps in the timber lattice creating dappled shadow patterns on the platforms below (like being under a forest canopy). The warm honey-colored timber contrasts with the steel rail infrastructure below. Timber elements are connected with visible steel node plates. The shell form is computationally optimized for structural efficiency -- thicker at the supports, thinner at mid-span. Inspired by Shigeru Ban's timber structures, Zaha Hadid's parametric designs, and the Metropol Parasol.",
         "facadeDetail": {"primaryMaterial": "CNC-cut timber ribs and laths forming parametric shell", "secondaryMaterial": "steel node plate connections, open sides", "groundFloor": "open platform level beneath flowing timber canopy", "colorScheme": "warm honey timber lattice, steel connections, dappled light"},
         "roofDetail": {"form": "flowing double-curved parametric timber shell", "material": "timber lattice shell with gaps for light"}, "palette": {"primary": "#CD853F"}},
        {"id": "transit_minimalist_concrete", "label": "Minimalist Concrete Platform",
         "description": "Ultra-minimal concrete transit station reduced to pure geometric essentials -- a thin concrete canopy, clean platforms, and nothing more.",
         "prompt": "Minimalist concrete platform transit station. Ultra-reduced transit station consisting of a single impossibly thin reinforced concrete canopy slab hovering above the platform on minimal Y-shaped concrete columns. The canopy is a clean rectangular plane with razor-sharp edges, casting a precise geometric shadow on the platform below. No walls, no enclosure, no ornament -- just the pure geometric relationship between the horizontal canopy plane and the ground plane. The concrete surfaces are smooth white with invisible joints. Integrated bench seating is a simple cantilevered concrete shelf extending from the column bases. Wayfinding is minimal sans-serif text incised directly into the concrete. The station achieves its impact through radical reduction and material precision. Inspired by Paulo Mendes da Rocha's bus stops, Tadao Ando's minimalism, and Eduardo Souto de Moura's stations.",
         "facadeDetail": {"primaryMaterial": "thin white concrete canopy on Y-columns", "secondaryMaterial": "cantilevered concrete bench seats, incised text wayfinding", "groundFloor": "open platform beneath floating concrete plane", "colorScheme": "pure white concrete, sharp shadows, minimal"},
         "roofDetail": {"form": "single thin concrete canopy plane", "material": "white reinforced concrete"}, "palette": {"primary": "#F0F0F0"}}
    ]
},

"urban_light_rail_stop": {
    "id": "urban_light_rail_stop",
    "title": "Urban Light Rail Stop",
    "description": "Street-level light rail, tram, or BRT stop shelter with weather protection, passenger information, and integration into the urban streetscape",
    "developmentType": "institutional",
    "buildingSubcategory": "Transit Station",
    "aestheticCategory": "light_rail_stop",
    "minFloors": 1, "maxFloors": 1, "suggestedAreaSqm": 200, "shadeId": "#4682B4",
    "facadeDetail": {"primaryMaterial": "steel and glass or tensile fabric shelter", "secondaryMaterial": "platform surface, passenger information displays", "accentMaterial": "transit system branding, lighting", "groundFloor": "open shelter on raised platform", "upperFloors": "n/a -- single level", "cornice": "canopy edge", "colorScheme": "transit system brand colors, glass, steel"},
    "roofDetail": {"form": "shelter canopy", "material": "glass, metal, ETFE, or fabric", "features": "integrated lighting, real-time displays", "aerialAppearance": "linear shelter on platform"},
    "variants": [
        {"id": "stop_steel_glass_shelter", "label": "Steel & Glass Shelter",
         "description": "Contemporary steel and glass transit shelter with a curved glass canopy, LED real-time displays, and clean modern wayfinding.",
         "prompt": "Steel and glass light rail stop. Contemporary transit stop shelter with a curved laminated glass canopy supported by slender stainless steel columns. The glass canopy provides rain protection while maintaining visual transparency to the surrounding street. Integrated LED real-time arrival displays showing the next tram arrival. Heated glass windscreens at each end. Low concrete platform with tactile paving strips at the platform edge. Ticket validator machine in transit brand colors. Bench seating integrated into the steel structure. Night lighting strips recessed into the canopy edge creating a gentle downward glow. Transit system map displayed in a backlit panel. The shelter is elegant and unobtrusive, serving the street rather than dominating it. Inspired by European tram stop designs in Zurich, Vienna, and Barcelona.",
         "facadeDetail": {"primaryMaterial": "curved laminated glass canopy on stainless steel columns", "secondaryMaterial": "heated glass windscreens, LED displays", "groundFloor": "concrete platform with tactile paving, ticket validators", "colorScheme": "clear glass, stainless steel, transit brand colors on validators"},
         "roofDetail": {"form": "curved glass canopy", "material": "laminated glass with LED edge lighting"}, "palette": {"primary": "#C0C0C0"}},
        {"id": "stop_tensile_fabric", "label": "Tensile Fabric Canopy Stop",
         "description": "Dramatic tensile fabric canopy transit stop with swooping PTFE membrane stretched between steel masts, creating a lightweight sculptural shelter.",
         "prompt": "Tensile fabric canopy light rail stop. Dramatic transit shelter with a swooping white PTFE (Teflon-coated fiberglass) tensile fabric canopy stretched between two tall tapered steel masts. The fabric membrane creates a dynamic curved surface -- higher at the masts and dipping in the center, shedding rainwater to the sides. Steel tension cables at the fabric edges maintain the hyperbolic form. The white fabric glows translucently in daylight and is dramatically uplift from below at night. Below the canopy, a clean concrete platform with integrated stainless steel bench seating and real-time display poles. The tensile structure gives the stop a distinctive landmark quality visible from a distance. Inspired by tensile fabric transit shelters and Frei Otto's membrane structures.",
         "facadeDetail": {"primaryMaterial": "white PTFE tensile fabric membrane on steel masts", "secondaryMaterial": "steel tension cables, tapered steel mast columns", "groundFloor": "concrete platform with stainless steel benches, display poles", "colorScheme": "white fabric, silver steel masts and cables, concrete platform"},
         "roofDetail": {"form": "swooping tensile fabric canopy between two masts", "material": "PTFE membrane with steel cable edges"}, "palette": {"primary": "#F5F5F5"}},
        {"id": "stop_green_roof_tram", "label": "Green Roof Tram Stop",
         "description": "Sustainable tram stop with a living green roof shelter, integrated planting, and the stop as a pocket of urban greenery.",
         "prompt": "Green roof tram stop. Sustainable transit shelter with a living sedum green roof growing on top of the canopy structure, creating a pocket of urban greenery at the stop. The shelter frame is weathering steel (Corten) that has developed a rich rust-brown patina complementing the green roof plants. Wildflowers and sedums spill slightly over the canopy edges. Rainwater from the green roof is collected and flows to a small bioswale rain garden at one end of the platform. Timber bench seating. A real-time display integrated into a vertical timber post. The green roof is visible from passing vehicles and upper-floor windows, contributing to the urban green infrastructure network. Bee-friendly planting attracts pollinators. Inspired by Utrecht's green bus stops and biophilic urban transit design.",
         "facadeDetail": {"primaryMaterial": "living sedum green roof on Corten steel shelter frame", "secondaryMaterial": "timber bench seating, bioswale rain garden", "groundFloor": "concrete platform with timber benches, bioswale at end", "colorScheme": "green sedum roof, rust-brown Corten, warm timber, wildflowers"},
         "roofDetail": {"form": "flat green roof canopy with sedum and wildflowers", "material": "living green roof on steel structure"}, "palette": {"primary": "#6B8E23"}},
        {"id": "stop_brutalist_concrete", "label": "Brutalist Concrete Stop",
         "description": "Bold brutalist concrete transit shelter with a dramatic cantilevered concrete canopy, raw formwork texture, and monumental presence for a simple stop.",
         "prompt": "Brutalist concrete transit stop. Bold transit shelter consisting of a single massive board-formed concrete canopy dramatically cantilevered from a thick concrete wall at one end. The cantilever extends 8 meters without visible supports, creating a striking engineering statement. The concrete surfaces show raw wood-grain formwork texture and deliberate formwork tie holes in a regular grid. The supporting concrete wall doubles as a windscreen and contains an integrated recessed display panel and a concrete bench shelf cantilevered from its inner face. The underside of the canopy has exposed concrete waffle-slab structure creating a geometric coffered pattern. Dramatic shadow cast by the deep cantilever. Brutally simple: just concrete, gravity, and engineering. Inspired by Oscar Niemeyer's bus stations and Paulo Mendes da Rocha's concrete structures.",
         "facadeDetail": {"primaryMaterial": "board-formed concrete cantilever from concrete wall", "secondaryMaterial": "waffle-slab soffit, integrated concrete bench", "groundFloor": "concrete platform beneath dramatic cantilever", "colorScheme": "raw grey concrete with formwork texture, deep shadow"},
         "roofDetail": {"form": "dramatically cantilevered concrete canopy from wall", "material": "reinforced concrete with waffle-slab soffit"}, "palette": {"primary": "#808080"}}
    ]
},

}

# ---- Generation + JSON functions ----
def generate_image(prompt, retries=2):
    body = {"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"responseModalities": ["TEXT", "IMAGE"], "temperature": 0.0}}
    for attempt in range(retries + 1):
        try:
            print(f"  -> Calling Gemini Pro ({len(prompt)} chars)...")
            resp = httpx.post(API_URL, json=body, timeout=120.0)
            if resp.status_code == 429: wait = 30*(attempt+1); print(f"  Rate limited, waiting {wait}s..."); time.sleep(wait); continue
            if resp.status_code != 200: print(f"  X API error {resp.status_code}: {resp.text[:300]}"); (time.sleep(10) if attempt < retries else None); continue
            data = resp.json(); candidates = data.get("candidates", [])
            if not candidates: print("  X No candidates"); return None
            for part in candidates[0].get("content", {}).get("parts", []):
                if "inlineData" in part: return base64.b64decode(part["inlineData"]["data"])
            print("  X No image"); return None
        except Exception as e: print(f"  X Exception: {e}"); (time.sleep(10) if attempt < retries else None); continue
    return None

def resize_and_crop(img_bytes, w, h):
    img = Image.open(io.BytesIO(img_bytes)); ratio = max(w/img.width, h/img.height)
    new_w, new_h = int(img.width*ratio), int(img.height*ratio)
    img = img.resize((new_w, new_h), Image.LANCZOS)
    left, top = (new_w-w)//2, (new_h-h)//2
    img = img.crop((left, top, left+w, top+h))
    buf = io.BytesIO(); img.save(buf, format="PNG", optimize=True); return buf.getvalue()

def generate_archetype_images(arch_id, arch_data, skip_existing=True):
    out_dir = _PUBLIC_DIR / "buildings" / arch_id; out_dir.mkdir(parents=True, exist_ok=True)
    variants = arch_data["variants"]
    print(f"\n{'='*60}\nArchetype: {arch_data['title']} ({arch_id})\n{'='*60}")
    for i, variant in enumerate(variants):
        filepath = out_dir / f"variant_{i}.png"
        if skip_existing and filepath.exists(): print(f"  [{i}] {variant['label']} -- exists, skip"); continue
        prompt = BUILDING_FRAME + variant["prompt"] + " " + NO_PEOPLE + " " + STYLE_ANCHOR
        print(f"  [{i}] Generating {variant['label']}...")
        img_bytes = generate_image(prompt)
        if img_bytes:
            cropped = resize_and_crop(img_bytes, CARD_WIDTH, CARD_HEIGHT)
            filepath.write_bytes(cropped); print(f"  OK {filepath.name} ({len(cropped):,}b)")
        else: print(f"  X Failed {variant['label']}")
        if i < len(variants)-1: print("  .. Wait 5s..."); time.sleep(5)
    v0, hero = out_dir/"variant_0.png", out_dir/"hero.png"
    if v0.exists() and not hero.exists(): hero.write_bytes(v0.read_bytes()); print("  OK hero.png")

def update_archetypes_json(archetypes):
    json_path = _DATA_DIR / "buildingArchetypes.json"
    data = json.loads(json_path.read_text(encoding="utf-8"))
    existing = {a["id"] for a in data["archetypes"]}; added = 0
    for aid, ad in archetypes.items():
        if aid in existing: print(f"  Skip {aid}"); continue
        entry = {"id": aid, "shadeId": ad.get("shadeId","#888"), "title": ad["title"],
                 "aestheticCategory": ad.get("aestheticCategory",aid), "description": ad["description"],
                 "buildingSubcategory": ad.get("buildingSubcategory","General"),
                 "generationTags": [ad.get("aestheticCategory",aid)],
                 "palette": {"skyTop":"#8fa2b8","skyBottom":"#c4b896","ground":"#8a8a7a","accent":ad.get("shadeId","#888")},
                 "styleProfile": {"era":"","influences":[],"keywords":[]},
                 "facadeDetail": ad.get("facadeDetail",{}), "roofDetail": ad.get("roofDetail",{}),
                 "thumbnailUrl": f"/archetypes/buildings/{aid}/hero.png",
                 "variants": [{"id":v["id"],"label":v["label"],"thumbnailUrl":f"/archetypes/buildings/{aid}/variant_{i}.png",
                               "description":v["description"],"facadeDetail":v.get("facadeDetail",{}),"roofDetail":v.get("roofDetail",{}),
                               "shadeId":None,"palette":v.get("palette",{"primary":"#888"})} for i,v in enumerate(ad["variants"])],
                 "minFloors": ad.get("minFloors",2), "maxFloors": ad.get("maxFloors",6),
                 "suggestedAreaSqm": ad.get("suggestedAreaSqm",5000), "developmentType": ad.get("developmentType","institutional")}
        data["archetypes"].append(entry); added += 1; print(f"  Added {aid}")
    if added: json_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"); print(f"\n+{added} archetypes to JSON")

def main():
    parser = argparse.ArgumentParser(); parser.add_argument("--category"); parser.add_argument("--no-skip", action="store_true"); parser.add_argument("--json-only", action="store_true")
    args = parser.parse_args(); skip = not args.no_skip
    targets = {args.category: ALL_ARCHETYPES[args.category]} if args.category else ALL_ARCHETYPES
    total = sum(len(a["variants"]) for a in targets.values())
    print(f"Batch 3: {len(targets)} archetypes, {total} images, est ${total*0.134:.2f}")
    if not args.json_only:
        for aid, ad in targets.items(): generate_archetype_images(aid, ad, skip); time.sleep(3)
    print("\nUpdating JSON..."); update_archetypes_json(targets); print("DONE!")

if __name__ == "__main__": main()
