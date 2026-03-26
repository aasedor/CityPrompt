"""
Generate ALL new archetype card images using Gemini 3 Pro Image API.

Categories:
- Institutional: General (3 archetypes x 4 variants = 12 images)
- Institutional: Health Care (3 x 4 = 12)
- Industrial: Light (3 x 4 = 12)
- Industrial: General (3 x 4 = 12)
- Industrial: Heavy (3 x 4 = 12)
- Industrial: Warehouse (3 x 4 = 12)
- Recreational (3 x 4 = 12)
- Rec Centre (3 x 4 = 12)
- Sports Arena (3 x 4 = 12)
- Hotels (3 x 4 = 12)
- Transit Stations (3 x 4 = 12)
Total: 33 archetypes, 132 images (+ 12 transit = 144)

Usage:
    python scripts/generate_all_archetypes.py
    python scripts/generate_all_archetypes.py --category institutional_general
    python scripts/generate_all_archetypes.py --skip-existing
"""

from __future__ import annotations

import argparse
import base64
import io
import json
import sys
import time
from pathlib import Path

import httpx
from PIL import Image

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SCRIPT_DIR.parent
_ENV_FILE = _PROJECT_ROOT / "backend" / ".env"
_PUBLIC_DIR = _PROJECT_ROOT / "frontend" / "public" / "archetypes"
_DATA_DIR = _PROJECT_ROOT / "frontend" / "src" / "data"

CARD_WIDTH = 1024
CARD_HEIGHT = 768


def _load_api_key() -> str:
    for line in _ENV_FILE.read_text().splitlines():
        line = line.strip()
        if line.startswith("GEMINI_API_KEY="):
            return line.split("=", 1)[1].strip()
    print("ERROR: GEMINI_API_KEY not found")
    sys.exit(1)


API_KEY = _load_api_key()
MODEL = "gemini-3-pro-image-preview"
API_URL = (
    f"https://generativelanguage.googleapis.com/v1beta/"
    f"models/{MODEL}:generateContent?key={API_KEY}"
)

# ---------------------------------------------------------------------------
# Style constants
# ---------------------------------------------------------------------------

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

# ---------------------------------------------------------------------------
# ALL ARCHETYPE DEFINITIONS
# ---------------------------------------------------------------------------

ALL_ARCHETYPES = {

# ============================================================
# INSTITUTIONAL: GENERAL
# ============================================================
"neoclassical_institutional": {
    "id": "neoclassical_institutional",
    "title": "Neoclassical Institutional",
    "description": "Grand neoclassical institutional building with classical columns, pediments, and symmetrical facades inspired by Greek and Roman architecture",
    "developmentType": "institutional",
    "buildingSubcategory": "General Institutional",
    "aestheticCategory": "neoclassical",
    "minFloors": 2,
    "maxFloors": 5,
    "suggestedAreaSqm": 8000,
    "shadeId": "#D4C5A9",
    "facadeDetail": {
        "primaryMaterial": "pale limestone or marble ashlar with precise joints",
        "secondaryMaterial": "fluted Corinthian or Ionic columns, carved pediments",
        "accentMaterial": "bronze doors, carved stone balustrades, decorative frieze",
        "groundFloor": "rusticated stone base with grand entrance portico and wide stone steps",
        "upperFloors": "tall arched windows with keystones, pilasters between bays, ornate cornice",
        "cornice": "deep projecting entablature with dentil molding and carved modillions",
        "colorScheme": "pale cream limestone, white marble columns, bronze metalwork"
    },
    "roofDetail": {
        "form": "low-pitched hipped roof behind stone balustrade parapet, central dome or cupola",
        "material": "copper roofing with verdigris patina, or slate",
        "features": "dome with lantern, stone urns along parapet, pediment sculptures",
        "aerialAppearance": "green copper dome surrounded by pale stone parapets and balustrades"
    },
    "variants": [
        {
            "id": "neoclassical_beaux_arts",
            "label": "Beaux-Arts",
            "description": "Lavish French-influenced Beaux-Arts with paired columns, sculptural groups, mansard roof elements, and rich ornamentation. Inspired by the Paris Opera and New York Public Library.",
            "prompt": "Grand Beaux-Arts institutional building. Lavish French neoclassical facade of pale cream limestone with paired Corinthian columns flanking tall arched windows. Elaborate sculptural groups above the main entrance pediment. Deep projecting cornice with carved modillions and dentils. Rusticated ground floor with round-arched openings. Mansard roof elements with copper dormers. Bronze lanterns flanking the entrance stairs. Rich cartouche carvings between floors. Balustrade parapet with stone urns. Inspired by the New York Public Library and Paris Opera.",
            "facadeDetail": {"primaryMaterial": "pale cream limestone ashlar", "secondaryMaterial": "paired Corinthian columns, sculptural pediment groups", "groundFloor": "rusticated base with round-arched entrance, bronze doors, flanking lanterns", "colorScheme": "cream limestone, white marble sculpture, copper and bronze accents"},
            "roofDetail": {"form": "mansard with copper dormers behind stone balustrade", "material": "slate mansard with copper details"},
            "palette": {"primary": "#E8DCC8"}
        },
        {
            "id": "neoclassical_palladian",
            "label": "Palladian",
            "description": "Restrained Palladian symmetry with a central portico, Venetian windows (Palladian motif), and strict mathematical proportions. Inspired by Andrea Palladio's villas and Chiswick House.",
            "prompt": "Palladian institutional building. Perfectly symmetrical facade of warm cream stone with a projecting central portico of four Ionic columns supporting a triangular pediment. Venetian windows (Palladian motif: arched center light flanked by shorter rectangular side lights) on the piano nobile. Rusticated ground floor. Strict mathematical proportions with harmonious window spacing. Simple refined moldings and minimal sculptural ornament. Flat roof behind a plain stone parapet with corner quoins. Inspired by Chiswick House and Palladio's Villa Rotonda.",
            "facadeDetail": {"primaryMaterial": "warm cream ashlar stone with precise joints", "secondaryMaterial": "Ionic column portico, Venetian/Palladian windows", "groundFloor": "rusticated stone base with central arched entrance", "colorScheme": "warm cream stone throughout, minimal color contrast"},
            "roofDetail": {"form": "low-pitched hipped roof behind plain parapet", "material": "lead or slate"},
            "palette": {"primary": "#D4C5A9"}
        },
        {
            "id": "neoclassical_greek_revival",
            "label": "Greek Revival",
            "description": "Bold Greek Revival with a full-width temple-front portico of Doric columns, triglyph-metope frieze, and stark white painted surfaces. Inspired by the Parthenon and US Capitol.",
            "prompt": "Greek Revival institutional building. Bold temple-front facade with a full-width portico of massive fluted Doric columns supporting a deep entablature with triglyph-and-metope frieze. Stark white painted stone or stucco over brick. Low triangular pediment with no sculpture (clean geometric purity). Tall narrow windows with simple stone lintels and no arches. Heavy rectangular proportions emphasizing horizontal strength. Flat roof behind a plain parapet. No ornament beyond the classical orders. Inspired by the Second Bank of the United States and British Museum.",
            "facadeDetail": {"primaryMaterial": "white painted stone or stucco over brick", "secondaryMaterial": "massive fluted Doric columns, triglyph-metope frieze", "groundFloor": "full-width columned portico with stone steps spanning entire facade", "colorScheme": "stark white throughout with dark window voids"},
            "roofDetail": {"form": "low-pitched gable behind portico pediment", "material": "lead or dark membrane"},
            "palette": {"primary": "#F5F0E8"}
        },
        {
            "id": "neoclassical_federal",
            "label": "Federal Style",
            "description": "Refined American Federal style with delicate fan-light transoms, sidelights, elliptical windows, and restrained Georgian proportions. Inspired by Charles Bulfinch and the White House.",
            "prompt": "Federal style institutional building. Refined red brick facade with white painted wood or stone trim. Symmetrical five-bay composition with a central entrance featuring an elegant semi-elliptical fan-light transom and sidelights. Tall double-hung sash windows with white shutters and thin stone lintels with keystones. Delicate roofline balustrade. Shallow projecting central pavilion with a Palladian window above the entrance. Low hipped roof with prominent chimneys. Elliptical oculus windows in the gable ends. Restrained elegant proportions. Inspired by the White House and Massachusetts State House.",
            "facadeDetail": {"primaryMaterial": "warm red brick in Flemish bond", "secondaryMaterial": "white painted stone or wood trim, fan-light transom", "groundFloor": "central entrance with semi-elliptical fanlight, sidelights, white pilasters", "colorScheme": "warm red brick, white trim, dark green shutters, grey slate roof"},
            "roofDetail": {"form": "low hipped roof with rooftop balustrade and chimneys", "material": "dark grey slate"},
            "palette": {"primary": "#8B4513"}
        }
    ]
},

"brutalist_institutional": {
    "id": "brutalist_institutional",
    "title": "Brutalist Institutional",
    "description": "Monumental raw concrete institutional building with bold geometric massing, exposed structural elements, and uncompromising material honesty",
    "developmentType": "institutional",
    "buildingSubcategory": "General Institutional",
    "aestheticCategory": "brutalism",
    "minFloors": 2,
    "maxFloors": 8,
    "suggestedAreaSqm": 10000,
    "shadeId": "#808080",
    "facadeDetail": {
        "primaryMaterial": "board-formed raw reinforced concrete with visible formwork grain",
        "secondaryMaterial": "exposed concrete structural beams and columns",
        "accentMaterial": "deeply recessed windows, raw steel handrails",
        "groundFloor": "heavy concrete pilotis or monolithic concrete base with deeply recessed entrance",
        "upperFloors": "repetitive concrete window bays with deep reveals casting dramatic shadows",
        "cornice": "flat concrete parapet or dramatically cantilevered upper floors",
        "colorScheme": "raw grey concrete throughout, dark window voids, weathered staining"
    },
    "roofDetail": {
        "form": "flat concrete roof with mechanical penthouses and exposed services",
        "material": "poured concrete slab",
        "features": "rooftop mechanical equipment, concrete parapets, drainage scuppers",
        "aerialAppearance": "flat grey concrete with mechanical penthouses and exposed ductwork"
    },
    "variants": [
        {
            "id": "brutalist_heroic",
            "label": "Heroic Brutalism",
            "description": "Monumental heroic Brutalism with massive cantilevered volumes, dramatic overhangs, and sculptural concrete forms. Inspired by the Barbican and National Theatre London.",
            "prompt": "Heroic Brutalist institutional building. Monumental raw board-formed concrete with massive cantilevered upper volumes projecting dramatically over a recessed glass ground floor. Visible wood-grain formwork texture in the concrete. Deep geometric window recesses casting heavy shadows. Sculptural concrete stair towers and service cores expressed on the exterior. Massive concrete pilotis supporting hovering upper floors. Dramatic interplay of solid concrete masses and deep shadow voids. Weathered concrete with rain staining adding patina. Inspired by the Barbican Estate and National Theatre London.",
            "facadeDetail": {"primaryMaterial": "raw board-formed concrete with wood-grain texture", "secondaryMaterial": "massive cantilevered volumes, exposed stair towers", "groundFloor": "recessed glass beneath heavy concrete cantilever, concrete pilotis", "colorScheme": "raw grey concrete, dark shadow voids, weathered staining"},
            "roofDetail": {"form": "flat with dramatically stepped roofline and mechanical penthouses", "material": "poured concrete"},
            "palette": {"primary": "#808080"}
        },
        {
            "id": "brutalist_concrete_expressionism",
            "label": "Concrete Expressionism",
            "description": "Sculptural concrete expressionism with curved and folded concrete forms, shell structures, and organic geometry. Inspired by Saarinen and Niemeyer.",
            "prompt": "Concrete Expressionist institutional building. Sweeping curved poured concrete forms creating dramatic sculptural volumes. Thin-shell concrete roof structure with hyperbolic paraboloid or folded-plate geometry. Smooth white-painted concrete surfaces contrasting with raw exposed concrete structural ribs. Continuous ribbon windows following the building's curves. Freeform organic silhouette against the sky. Cantilevered concrete canopies with impossibly thin edges. Reflecting pool in the foreground. Inspired by TWA Terminal by Saarinen and Brasilia Cathedral by Niemeyer.",
            "facadeDetail": {"primaryMaterial": "smooth white-painted poured concrete", "secondaryMaterial": "exposed concrete structural ribs and thin-shell roof", "groundFloor": "sweeping curved glass walls beneath concrete shell", "colorScheme": "white concrete, dark glass, raw concrete ribs"},
            "roofDetail": {"form": "dramatic thin-shell or folded-plate sculptural roof", "material": "white-painted reinforced concrete"},
            "palette": {"primary": "#C0C0C0"}
        },
        {
            "id": "brutalist_new_brutalism",
            "label": "New Brutalism",
            "description": "Rigorous New Brutalism with exposed services, honest material expression, and Smithsons-inspired anti-aesthetic. Inspired by Robin Hood Gardens and Hunstanton School.",
            "prompt": "New Brutalist institutional building. Rigorously honest facade expressing every structural and mechanical system on the exterior. Raw concrete frame with infill panels of exposed brick. Visible steel I-beams and connections left unpainted. Exposed drainage pipes, electrical conduits, and ventilation ducts running along the exterior. Prefabricated concrete panels with visible lifting holes. Steel-framed windows with no decorative trim. Industrial steel staircase attached to the exterior. Deliberately anti-aesthetic with no applied decoration. Inspired by Hunstanton School by the Smithsons and Robin Hood Gardens.",
            "facadeDetail": {"primaryMaterial": "raw concrete frame with exposed brick infill panels", "secondaryMaterial": "visible steel structure, exposed mechanical services", "groundFloor": "open concrete frame with glass and brick infill, visible steel columns", "colorScheme": "raw concrete grey, red brick, unpainted steel, exposed copper pipes"},
            "roofDetail": {"form": "flat with exposed rooftop mechanical equipment and steel railings", "material": "concrete slab with visible waterproofing"},
            "palette": {"primary": "#696969"}
        },
        {
            "id": "brutalist_eco_brutalism",
            "label": "Eco-Brutalism",
            "description": "Contemporary Eco-Brutalism merging raw concrete with lush vegetation, green walls, and sustainable design. Inspired by Bosco Verticale and WOHA Architects.",
            "prompt": "Eco-Brutalist institutional building. Raw board-formed concrete structure with lush tropical vegetation growing from every horizontal surface and planter box. Deep concrete balconies overflowing with trailing vines, ferns, and small trees. Green living walls covering portions of the concrete facade. Exposed concrete structural grid with integrated planter troughs at every floor. Rainwater collection channels visible in the concrete. Large openings with no glass allowing natural ventilation through planted terraces. The building appears to be a concrete ruin being reclaimed by nature. Inspired by WOHA Architects and Bosco Verticale concept applied to raw concrete.",
            "facadeDetail": {"primaryMaterial": "raw board-formed concrete with integrated planters", "secondaryMaterial": "living green walls, trailing vines, planted balconies", "groundFloor": "open concrete colonnade with tropical planting beds", "colorScheme": "raw grey concrete with lush green vegetation, earth tones"},
            "roofDetail": {"form": "flat green roof with rooftop garden and concrete pergolas", "material": "concrete with extensive planting"},
            "palette": {"primary": "#4A7C59"}
        }
    ]
},

"contemporary_civic": {
    "id": "contemporary_civic",
    "title": "Contemporary Civic",
    "description": "Bold contemporary civic architecture with innovative forms, advanced materials, and striking geometric compositions",
    "developmentType": "institutional",
    "buildingSubcategory": "General Institutional",
    "aestheticCategory": "contemporary_civic",
    "minFloors": 2,
    "maxFloors": 6,
    "suggestedAreaSqm": 6000,
    "shadeId": "#4A90D9",
    "facadeDetail": {
        "primaryMaterial": "glass curtain wall with high-performance glazing",
        "secondaryMaterial": "perforated metal cladding panels, composite materials",
        "accentMaterial": "anodized aluminum, weathering steel (Corten), timber accents",
        "groundFloor": "fully glazed transparent lobby with cantilevered canopy",
        "upperFloors": "dynamic facade composition with varied panel sizes and orientations",
        "cornice": "sharp clean roofline with integrated solar shading",
        "colorScheme": "silver and glass with accent materials providing warmth"
    },
    "roofDetail": {
        "form": "dynamic asymmetric roofline or dramatic cantilever",
        "material": "standing seam metal or EPDM membrane",
        "features": "rooftop photovoltaic arrays, green roof sections",
        "aerialAppearance": "varied geometric roof planes with solar panels and green sections"
    },
    "variants": [
        {
            "id": "civic_stripped_classicism",
            "label": "Stripped Classicism",
            "description": "Modernized classical forms with simplified columns, abstract pediments, and monumental proportions but no ornament. Inspired by Paul Cret and 1930s civic buildings.",
            "prompt": "Stripped Classical civic building. Monumental symmetrical facade of smooth pale limestone with massively scaled simplified square columns (no fluting, no capitals) flanking a tall recessed entrance. Abstract geometric interpretation of a classical pediment as a flat stone panel above the entrance. Deeply incised horizontal bands of windows with minimal stone mullions. Heavy stone base with no rustication. Severe geometric proportions with no applied ornament whatsoever. Monumental bronze doors with geometric Art Deco patterns. Clean flat stone surfaces with razor-sharp edges. Inspired by Paul Cret's Federal Reserve Board Building and Mussolini-era rationalist architecture.",
            "facadeDetail": {"primaryMaterial": "smooth pale limestone with razor-sharp edges", "secondaryMaterial": "simplified square columns without capitals or fluting", "groundFloor": "deeply recessed entrance with monumental bronze doors", "colorScheme": "pale limestone, bronze doors, minimal dark window voids"},
            "roofDetail": {"form": "flat with heavy stone parapet and abstract cornice", "material": "hidden behind stone parapet"},
            "palette": {"primary": "#D4C5A9"}
        },
        {
            "id": "civic_high_tech",
            "label": "High-Tech Civic",
            "description": "High-Tech architecture with exposed structural steel, glass, tensioned cables, and celebration of engineering. Inspired by Renzo Piano, Richard Rogers, and Norman Foster.",
            "prompt": "High-Tech civic building. Exposed painted steel structural frame in bright primary colors (blue, red, yellow) with all structural connections, bolts, and nodes visible and celebrated. Full-height glass curtain walls suspended from external steel tension rods. Exposed cross-bracing in stainless steel cables. External escalators and circulation tubes in transparent glass. Visible color-coded mechanical services: blue for air, green for water, yellow for electrical. Tension-rod canopy over the entrance with spider fittings. Inspired by Centre Pompidou by Rogers and Piano, and Lloyd's of London.",
            "facadeDetail": {"primaryMaterial": "exposed painted steel frame in primary colors", "secondaryMaterial": "full-height glass curtain wall, stainless steel tension cables", "groundFloor": "transparent glass with visible steel structure, external escalators", "colorScheme": "bright blue steel frame, red circulation elements, silver cables, clear glass"},
            "roofDetail": {"form": "exposed steel truss roof structure visible from outside", "material": "steel trusses with glass or metal infill"},
            "palette": {"primary": "#0066CC"}
        },
        {
            "id": "civic_deconstructivism",
            "label": "Deconstructivism",
            "description": "Fragmented deconstructivist forms with colliding angles, tilted walls, and deliberately unstable geometry. Inspired by Gehry, Libeskind, and Hadid.",
            "prompt": "Deconstructivist civic building. Dramatically fragmented facade with sharp angular collisions of tilted metal-clad volumes piercing through each other at impossible angles. Walls that lean outward at alarming angles. Jagged slashed window openings cut at aggressive diagonals across the facade. Clashing materials: brushed titanium panels meeting raw weathering steel (Corten) meeting black zinc. No right angles anywhere. A fractured, exploded composition that appears structurally unstable but is precisely engineered. Knife-edge cantilevers and sharp pointed volumes. Inspired by Libeskind's Jewish Museum Berlin and Gehry's Guggenheim Bilbao.",
            "facadeDetail": {"primaryMaterial": "titanium or zinc cladding panels at sharp angles", "secondaryMaterial": "weathering steel (Corten), slashed window openings", "groundFloor": "angular glass entrance cut into tilted metal volume", "colorScheme": "silver titanium, rusty Corten, black zinc, fractured glass"},
            "roofDetail": {"form": "fragmented angular planes at colliding angles", "material": "titanium or zinc panels"},
            "palette": {"primary": "#708090"}
        },
        {
            "id": "civic_parametric",
            "label": "Parametric Form",
            "description": "Flowing parametric architecture with algorithmically generated curved surfaces, ETFE cladding, and organic computational geometry. Inspired by Zaha Hadid and MAD Architects.",
            "prompt": "Parametric civic building. Flowing organic form with continuously curved double-curved surfaces generated by computational algorithms. Seamless white fiber-reinforced polymer cladding with no visible joints following the building's complex topology. Irregularly shaped window openings that morph and flow across the surface like perforations in a continuous skin. No straight lines or flat surfaces anywhere. The building appears to flow and undulate like a frozen liquid. Entrance formed by the surface folding inward to create a covered threshold. Ground plane merges seamlessly with the building skin. Inspired by Zaha Hadid's Heydar Aliyev Center and MAD Architects' Harbin Opera House.",
            "facadeDetail": {"primaryMaterial": "seamless white fiber-reinforced polymer or GRC panels", "secondaryMaterial": "flowing irregular window openings in the continuous skin", "groundFloor": "surface folds inward creating a covered entrance threshold", "colorScheme": "pure white exterior, dark glass openings, seamless curves"},
            "roofDetail": {"form": "continuous curved surface merging with walls (no distinction)", "material": "same white cladding as walls"},
            "palette": {"primary": "#F0F0F0"}
        }
    ]
},

# ============================================================
# INSTITUTIONAL: HEALTH CARE
# ============================================================
"art_deco_healthcare": {
    "id": "art_deco_healthcare",
    "title": "Art Deco Healthcare",
    "description": "Streamlined Art Deco hospital building with geometric ornamentation, stepped massing, and optimistic machine-age aesthetics",
    "developmentType": "institutional",
    "buildingSubcategory": "Health Care",
    "aestheticCategory": "art_deco_healthcare",
    "minFloors": 3,
    "maxFloors": 12,
    "suggestedAreaSqm": 15000,
    "shadeId": "#C4A265",
    "facadeDetail": {
        "primaryMaterial": "smooth pale limestone or cast stone with geometric incised patterns",
        "secondaryMaterial": "polished granite base, aluminum or bronze spandrel panels",
        "accentMaterial": "geometric terra cotta ornament, chrome or nickel trim",
        "groundFloor": "polished granite entrance surround with geometric chrome canopy",
        "upperFloors": "vertical piers with geometric capitals, ribbon windows with metal spandrels",
        "cornice": "stepped crown with geometric zigzag or sunburst motifs",
        "colorScheme": "pale limestone, polished dark granite, chrome accents, terra cotta ornament"
    },
    "roofDetail": {
        "form": "stepped pyramidal crown or tower with geometric finial",
        "material": "copper or terra cotta tile",
        "features": "illuminated tower crown, geometric ventilation grilles",
        "aerialAppearance": "stepped setback tower with geometric crown and copper roofing"
    },
    "variants": [
        {
            "id": "healthcare_pwa_moderne",
            "label": "PWA Moderne",
            "description": "Depression-era PWA Moderne hospital with simplified classical massing, flat limestone surfaces, and restrained geometric ornament from New Deal public works programs.",
            "prompt": "PWA Moderne hospital building. Symmetrical stepped-back massing in smooth buff limestone with simplified Art Deco geometric ornament concentrated around the entrance and parapet. Flat pilasters without capitals flanking the entrance. Incised geometric patterns in the stone: chevrons, stylized eagles, and wheat sheaves referencing New Deal civic optimism. Aluminum-framed casement windows in horizontal bands. Restrained decoration: flat geometric bas-relief panels above the entrance depicting healthcare and science themes. Clean flat surfaces with minimal shadow. Low-relief geometric frieze at the roofline. Inspired by 1930s WPA-funded hospitals and municipal buildings.",
            "facadeDetail": {"primaryMaterial": "smooth buff limestone with incised geometric ornament", "secondaryMaterial": "flat pilasters, aluminum window frames", "groundFloor": "simplified classical entrance with geometric bas-relief panels", "colorScheme": "buff limestone, aluminum frames, geometric stone ornament"},
            "roofDetail": {"form": "flat with stepped parapet and geometric frieze", "material": "built-up roof behind limestone parapet"},
            "palette": {"primary": "#D4C5A9"}
        },
        {
            "id": "healthcare_zigzag_deco",
            "label": "Zigzag Deco",
            "description": "Exuberant Zigzag Art Deco hospital with bold polychrome terra cotta ornament, sunburst motifs, and dramatic vertical emphasis.",
            "prompt": "Zigzag Art Deco hospital tower. Dramatic vertical emphasis with bold setbacks stepping upward to an illuminated crown. Rich polychrome terra cotta ornament in gold, turquoise, and deep red featuring zigzag chevron patterns, sunburst motifs, and stylized floral designs. Vertical piers rising uninterrupted to the crown with geometric terra cotta capitals. Recessed spandrel panels in contrasting dark metal between floors. Elaborate entrance surround with geometric bronze doors and polychrome terra cotta arch featuring caduceus medical symbols. Chrome and nickel hardware throughout. Inspired by the Chrysler Building's ornamental vocabulary applied to a healthcare facility.",
            "facadeDetail": {"primaryMaterial": "pale limestone with polychrome terra cotta ornament", "secondaryMaterial": "gold, turquoise, and red terra cotta zigzag patterns", "groundFloor": "elaborate geometric entrance with bronze doors and polychrome arch", "colorScheme": "pale stone, gold and turquoise terra cotta, chrome accents, dark spandrels"},
            "roofDetail": {"form": "stepped setback crown with illuminated geometric finial", "material": "polychrome terra cotta and copper"},
            "palette": {"primary": "#C4A265"}
        },
        {
            "id": "healthcare_tropical_deco",
            "label": "Tropical Deco",
            "description": "Tropical Art Deco hospital with nautical motifs, pastel stucco, porthole windows, and streamlined horizontal emphasis. Inspired by Miami Beach Art Deco.",
            "prompt": "Tropical Art Deco hospital building. Streamlined horizontal facade of smooth white stucco with pastel mint-green and coral-pink accents. Nautical motifs: porthole windows, ship-rail balcony railings in chrome, streamlined curved corners. Horizontal speed lines (racing stripes) incised into the stucco. Flat roof with a streamlined tower element featuring glass block windows and a flagpole. Continuous horizontal eyebrow shading ledges above windows casting crisp shadow lines. Rounded corners on the building mass. Tropical landscaping with palm trees and bougainvillea. Neon signage integrated into the facade. Inspired by Miami Beach's Art Deco Historic District hospitals.",
            "facadeDetail": {"primaryMaterial": "smooth white stucco with streamlined curves", "secondaryMaterial": "pastel mint-green and coral accent bands, chrome railings", "groundFloor": "streamlined entrance with glass block sidelights and chrome canopy", "colorScheme": "white stucco, mint green, coral pink, chrome accents"},
            "roofDetail": {"form": "flat with streamlined tower and flagpole", "material": "white stucco parapet with horizontal speed lines"},
            "palette": {"primary": "#98D4BB"}
        },
        {
            "id": "healthcare_stripped_moderne",
            "label": "Stripped Moderne",
            "description": "Sleek Stripped Moderne hospital with smooth surfaces, rounded corners, glass block, and minimal ornament. The most modernist of the Deco variants.",
            "prompt": "Stripped Moderne hospital building. Extremely clean smooth white or pale grey rendered surfaces with absolutely no applied ornament. Rounded streamlined corners on the building mass. Horizontal ribbon windows wrapping continuously around corners. Glass block stairwell towers glowing from within. Flat roof with minimal parapet. Cantilevered entrance canopy with clean thin edge. Recessed entrance with chrome-framed glass doors. Continuous horizontal banding created by shadow lines from slight floor-plate projections. Inspired by the most minimal late-1930s hospital designs where Art Deco was stripped to pure geometric form.",
            "facadeDetail": {"primaryMaterial": "smooth white or pale grey render/stucco", "secondaryMaterial": "glass block stairwell towers, chrome window frames", "groundFloor": "recessed entrance with thin cantilevered concrete canopy", "colorScheme": "white or pale grey surfaces, chrome frames, glass block glow"},
            "roofDetail": {"form": "flat with minimal clean parapet", "material": "white rendered parapet"},
            "palette": {"primary": "#E8E8E8"}
        }
    ]
},

"functionalist_healthcare": {
    "id": "functionalist_healthcare",
    "title": "Functionalist Healthcare",
    "description": "Clean modernist hospital building with rational planning, honest material expression, and form following medical function",
    "developmentType": "institutional",
    "buildingSubcategory": "Health Care",
    "aestheticCategory": "functionalist_healthcare",
    "minFloors": 3,
    "maxFloors": 10,
    "suggestedAreaSqm": 20000,
    "shadeId": "#B0C4DE",
    "facadeDetail": {
        "primaryMaterial": "white rendered concrete or smooth precast panels",
        "secondaryMaterial": "aluminum curtain wall framing, glass",
        "accentMaterial": "colored accent panels, stainless steel trim",
        "groundFloor": "fully glazed lobby with covered ambulance drop-off",
        "upperFloors": "regular grid of windows expressing the ward layout, balconies for patient rooms",
        "cornice": "clean flat roofline with minimal parapet",
        "colorScheme": "white walls, silver aluminum frames, accent color panels"
    },
    "roofDetail": {
        "form": "flat roof with helipad and mechanical penthouse",
        "material": "membrane with equipment screens",
        "features": "helipad, cooling towers, rooftop garden areas",
        "aerialAppearance": "flat white roof with helipad marking and mechanical equipment"
    },
    "variants": [
        {
            "id": "healthcare_bauhaus",
            "label": "Bauhaus",
            "description": "Pure Bauhaus hospital with white cubic volumes, flat roofs, ribbon windows, and primary color accents. Inspired by the Bauhaus school and Paimio Sanatorium.",
            "prompt": "Bauhaus-style hospital building. Pure white cubic volumes intersecting at right angles with flat roofs and no ornament. Continuous horizontal ribbon windows with thin steel frames wrapping around corners. Cantilevered concrete balconies with tubular steel railings for patient sun-terraces. Pilotis raising the ground floor. Primary color accents: a bright red entrance canopy, yellow door, blue signage panel. Asymmetrical composition of interlocking white boxes. Glass curtain wall staircase tower. Inspired by Alvar Aalto's Paimio Sanatorium and the Bauhaus Dessau building.",
            "facadeDetail": {"primaryMaterial": "smooth white rendered concrete", "secondaryMaterial": "steel-framed ribbon windows, tubular steel railings", "groundFloor": "pilotis with recessed glass ground floor, red entrance canopy", "colorScheme": "white volumes, primary color accents (red, yellow, blue), steel grey frames"},
            "roofDetail": {"form": "flat roofs at varied heights on interlocking volumes", "material": "white rendered parapet"},
            "palette": {"primary": "#FFFFFF"}
        },
        {
            "id": "healthcare_minimalist_modern",
            "label": "Minimalist Modern",
            "description": "Ultra-minimal modern hospital with seamless white surfaces, frameless flush glazing, and pure geometric abstraction. Inspired by SANAA and Alberto Campo Baeza.",
            "prompt": "Minimalist modern hospital. Ethereally pure white building with seamless smooth surfaces and absolutely no visible joints, frames, or details. Floor-to-ceiling frameless glass panels set perfectly flush with the white wall surface. Extremely thin floor plates creating hovering horizontal planes. Deep recessed reveals where glass meets wall. No visible structure. The building reads as a stack of impossibly thin white planes separated by continuous glass bands. Subtle shadow lines are the only ornament. Pure geometric abstraction. Inspired by SANAA's New Museum and Alberto Campo Baeza's hospitals.",
            "facadeDetail": {"primaryMaterial": "seamless white rendered surfaces with invisible joints", "secondaryMaterial": "frameless flush-mounted glass panels", "groundFloor": "fully transparent glass ground floor with ultra-thin columns", "colorScheme": "pure white surfaces, clear glass, subtle shadow lines only"},
            "roofDetail": {"form": "razor-thin flat roof edge, minimal parapet", "material": "white membrane behind minimal edge"},
            "palette": {"primary": "#FAFAFA"}
        },
        {
            "id": "healthcare_clinical_modernism",
            "label": "Clinical Modernism",
            "description": "Rational clinical modernist hospital with expressed structural grid, solar shading brise-soleil, and efficient ward planning. Inspired by Le Corbusier's hospital designs.",
            "prompt": "Clinical Modernist hospital. Rational exposed concrete structural grid defining a clear bay system. Deep horizontal concrete brise-soleil sunshades projecting from each floor creating dramatic shadow patterns. Recessed glass walls behind the sunshade grid. Expressed floor plates with visible concrete edge beams. Covered ground-floor colonnade for ambulance access. Color-coded departments visible through the glass: blue surgical wing, green recovery ward. Rooftop helipad. Functional, rational, no-nonsense expression of hospital program. Inspired by Le Corbusier's Venice Hospital project and Oscar Niemeyer's hospital designs.",
            "facadeDetail": {"primaryMaterial": "exposed concrete structural frame with deep brise-soleil", "secondaryMaterial": "recessed glass curtain wall behind sunshades", "groundFloor": "open concrete colonnade with covered ambulance drop-off", "colorScheme": "raw concrete frame, glass walls, color-coded interior departments visible"},
            "roofDetail": {"form": "flat with helipad and concrete sunshade canopy", "material": "concrete with helipad markings"},
            "palette": {"primary": "#C0C0C0"}
        },
        {
            "id": "healthcare_rationalism",
            "label": "Rationalism",
            "description": "Italian Rationalist hospital with pure geometric forms, marble cladding, and monumental arcaded ground floors. Inspired by Giuseppe Terragni and Adalberto Libera.",
            "prompt": "Rationalist hospital building. Severe pure geometric composition of interlocking rectangular marble-clad volumes. Ground floor as a deep monumental arcade of square openings with no columns (just square voids cut into the mass). Smooth white Carrara marble cladding with precise thin joints. Square windows in a strict mathematical grid. No ornament, no moldings, no projections. The building is a pure abstract geometric composition of solid and void. One accent volume in polished dark green serpentine marble. Inspired by Giuseppe Terragni's Casa del Fascio and Adalberto Libera's Palazzo dei Congressi.",
            "facadeDetail": {"primaryMaterial": "white Carrara marble cladding with precise thin joints", "secondaryMaterial": "dark green serpentine marble accent volume", "groundFloor": "monumental arcade of square openings cut into the marble mass", "colorScheme": "white marble, dark green accent, minimal dark window voids"},
            "roofDetail": {"form": "flat, clean-edged, hidden behind marble parapet", "material": "hidden membrane"},
            "palette": {"primary": "#F0EDE8"}
        }
    ]
},

"biophilic_healthcare": {
    "id": "biophilic_healthcare",
    "title": "Biophilic Modern Healthcare",
    "description": "Nature-integrated healing environment with living walls, natural materials, courtyards, and evidence-based biophilic design principles",
    "developmentType": "institutional",
    "buildingSubcategory": "Health Care",
    "aestheticCategory": "biophilic_healthcare",
    "minFloors": 2,
    "maxFloors": 6,
    "suggestedAreaSqm": 12000,
    "shadeId": "#6B8E23",
    "facadeDetail": {
        "primaryMaterial": "natural timber cladding or stone with living green walls",
        "secondaryMaterial": "floor-to-ceiling glass bringing nature views into patient rooms",
        "accentMaterial": "copper accents with green patina, natural stone garden walls",
        "groundFloor": "open colonnade connecting interior to landscaped healing gardens",
        "upperFloors": "patient room balconies with timber screens and planter boxes",
        "cornice": "green roof edge with visible plantings overhanging",
        "colorScheme": "warm timber, green vegetation, natural stone, copper patina"
    },
    "roofDetail": {
        "form": "extensive green roof with rooftop healing garden",
        "material": "intensive green roof with trees, paths, and seating",
        "features": "rooftop garden paths, patient seating areas, rainwater collection",
        "aerialAppearance": "lush green rooftop garden with winding paths and patient seating areas"
    },
    "variants": [
        {
            "id": "healthcare_eco_tech",
            "label": "Eco-Tech",
            "description": "High-tech sustainable hospital with solar facades, automated shading, rainwater harvesting, and visible green technology systems.",
            "prompt": "Eco-Tech hospital building. Advanced sustainable facade with building-integrated photovoltaic glass panels creating a shimmering blue-black solar skin. Automated external motorized louver sunshading system responding to sun position. Visible rainwater harvesting channels and green infrastructure. Living green wall covering 30% of the facade with integrated irrigation. Wind turbines visible on the rooftop. Triple-glazed high-performance curtain wall. Exposed timber glulam structure visible through the glass. BREEAM Outstanding rating visible on entrance signage. Inspired by Singapore's Khoo Teck Puat Hospital and Freiburg's sustainable healthcare campus.",
            "facadeDetail": {"primaryMaterial": "photovoltaic glass panels and high-performance glazing", "secondaryMaterial": "motorized aluminum louver sunshading, living green walls", "groundFloor": "transparent lobby with visible timber structure, rainwater feature", "colorScheme": "blue-black solar glass, silver louvers, green living walls, warm timber"},
            "roofDetail": {"form": "green roof with photovoltaic canopy and wind turbines", "material": "intensive green roof with solar panel pergola"},
            "palette": {"primary": "#2E5090"}
        },
        {
            "id": "healthcare_courtyard_model",
            "label": "Courtyard Model",
            "description": "Healing courtyard hospital with patient rooms opening onto landscaped internal gardens, water features, and natural ventilation.",
            "prompt": "Courtyard hospital building. Low-rise warm stone and timber building organized around a series of landscaped healing courtyard gardens. Every patient room has floor-to-ceiling glass doors opening onto a private garden terrace. Natural warm sandstone walls with horizontal timber screen balconies. Internal courtyards visible through the building with mature trees, water features, and meditation gardens. Covered colonnades of timber columns connecting wings around the gardens. Climbing plants on timber trellises. Natural cross-ventilation through operable timber louvers. Inspired by Maggie's Centres and traditional Islamic hospital courtyard planning.",
            "facadeDetail": {"primaryMaterial": "warm sandstone walls with natural timber screens", "secondaryMaterial": "floor-to-ceiling glass opening to garden terraces, timber colonnades", "groundFloor": "covered timber colonnade with views through to courtyard gardens", "colorScheme": "warm sandstone, natural timber, green gardens, water features"},
            "roofDetail": {"form": "low-pitched green roof with overhanging timber eaves", "material": "sedum green roof with timber fascia"},
            "palette": {"primary": "#C4A87C"}
        },
        {
            "id": "healthcare_organic_architecture",
            "label": "Organic Architecture",
            "description": "Flowing organic hospital with curved forms inspired by nature, natural materials, and spaces designed around patient wellbeing.",
            "prompt": "Organic architecture hospital. Flowing curved building form inspired by natural shapes -- the facade undulates like a gentle wave or leaf edge. Warm natural timber cladding following the curves with vertical grain. Irregularly shaped windows like organic cell formations grouped in clusters. Curved green roof flowing seamlessly from the landscape up and over the building. Natural stone base anchoring the building to the earth. Interior visible through glass showing timber-lined patient rooms with garden views. The building appears to grow from the landscape rather than being placed upon it. Inspired by Frank Lloyd Wright's organic principles and Renzo Piano's Tjibaou Cultural Center.",
            "facadeDetail": {"primaryMaterial": "warm natural timber cladding following curved forms", "secondaryMaterial": "natural stone base, organic-shaped window clusters", "groundFloor": "flowing glass ground floor merging interior with landscape", "colorScheme": "warm timber, natural stone, green roof, organic forms"},
            "roofDetail": {"form": "curved green roof flowing from landscape up over the building", "material": "intensive green roof with native plantings"},
            "palette": {"primary": "#8B7355"}
        },
        {
            "id": "healthcare_mass_timber",
            "label": "Mass Timber Modern",
            "description": "Contemporary mass timber hospital showcasing exposed cross-laminated timber structure, biophilic wood interiors, and carbon-negative construction.",
            "prompt": "Mass timber hospital building. Contemporary building with fully exposed cross-laminated timber (CLT) structure visible on the exterior. Warm honey-colored glulam beams and CLT wall panels creating a distinctive wood-grid facade. Deep timber-framed balconies with timber privacy screens for patient rooms. Large expanses of glass between timber structural bays revealing the warm wood interior. Timber rain-screen cladding in varied widths creating visual texture. Charred timber (Shou Sugi Ban) accent panels at the ground floor. The building radiates warmth and calm through the visible natural wood grain. Inspired by Brock Commons at UBC and recent Scandinavian mass timber hospitals.",
            "facadeDetail": {"primaryMaterial": "exposed CLT and glulam timber structure, honey-colored", "secondaryMaterial": "timber rain-screen cladding, charred timber accents", "groundFloor": "charred timber (Shou Sugi Ban) base with glass lobby showing timber interior", "colorScheme": "warm honey timber, charred black accents, clear glass, green landscaping"},
            "roofDetail": {"form": "flat with exposed timber structure at roof edge, rooftop garden", "material": "green roof with exposed timber fascia"},
            "palette": {"primary": "#CD853F"}
        }
    ]
},

# ============================================================
# INDUSTRIAL: LIGHT
# ============================================================
"daylight_factory": {
    "id": "daylight_factory",
    "title": "Daylight Factory",
    "description": "Historic daylight factory with specialized roof forms designed to maximize natural light for manufacturing, featuring sawtooth roofs, monitor roofs, and large industrial windows",
    "developmentType": "industrial",
    "buildingSubcategory": "Light Industrial",
    "aestheticCategory": "daylight_factory",
    "minFloors": 1,
    "maxFloors": 3,
    "suggestedAreaSqm": 5000,
    "shadeId": "#8B6914",
    "facadeDetail": {
        "primaryMaterial": "load-bearing red brick with exposed structural frame",
        "secondaryMaterial": "large steel-sash industrial windows, cast iron columns",
        "accentMaterial": "stone lintels and sills, painted steel loading doors",
        "groundFloor": "large openings for goods access, brick piers between windows",
        "upperFloors": "continuous bands of steel-framed multi-pane windows maximizing daylight",
        "cornice": "brick corbel course or simple stone cap",
        "colorScheme": "red-brown brick, dark steel window frames, stone accents"
    },
    "roofDetail": {
        "form": "sawtooth or monitor roof with north-facing glazing",
        "material": "slate or corrugated metal with glass monitor windows",
        "features": "sawtooth profile visible from street, roof ventilators",
        "aerialAppearance": "distinctive sawtooth or monitor roof profile with glass panels"
    },
    "variants": [
        {
            "id": "factory_sawtooth_roof",
            "label": "Sawtooth Roof",
            "description": "Classic sawtooth-roofed factory with repeating asymmetric roof peaks, north-facing glazing for even daylight, and red brick construction.",
            "prompt": "Sawtooth-roofed daylight factory. Long single-story red brick industrial building with a distinctive repeating sawtooth roof profile visible from the street. Each sawtooth has a steep glazed north-facing slope (filled with multi-pane steel-framed glass) and a shorter opaque south-facing slope (slate-covered). The roof creates a dramatic zigzag silhouette against the sky. Tall steel-sash multi-pane windows along the brick walls. Loading dock with painted steel rolling doors. Brick chimney stack. Simple brick corbel cornice. Surrounding industrial context with rail siding. Inspired by New England textile mills and Albert Kahn's early factories.",
            "facadeDetail": {"primaryMaterial": "red brick with simple corbel courses", "secondaryMaterial": "steel-sash multi-pane industrial windows", "groundFloor": "loading docks with painted steel rolling doors, brick piers", "colorScheme": "red-brown brick, dark steel frames, slate and glass roof"},
            "roofDetail": {"form": "repeating sawtooth profile with north-facing glass", "material": "slate on opaque slopes, steel-framed glass on glazed slopes"},
            "palette": {"primary": "#8B4513"}
        },
        {
            "id": "factory_concrete_daylight",
            "label": "Concrete Frame Daylight",
            "description": "Reinforced concrete-framed daylight factory with mushroom columns, glass curtain walls between structural bays, and flat slab construction.",
            "prompt": "Concrete-framed daylight factory. Multi-story reinforced concrete industrial building with a clearly expressed concrete structural frame -- mushroom-headed columns visible through full-height glass curtain walls between structural bays. Flat concrete slab floors with exposed edges. Concrete spandrel panels between floors. The facade is predominantly glass: steel-framed multi-pane industrial glazing filling entire structural bays. Rooftop concrete monitors (raised clerestory sections) providing additional top-lighting. Concrete loading ramp at ground level. Raw concrete finish with formwork marks. Inspired by Albert Kahn's Packard Plant and early 20th-century concrete industrial buildings.",
            "facadeDetail": {"primaryMaterial": "raw reinforced concrete frame with mushroom columns", "secondaryMaterial": "full-height steel-framed industrial glazing between bays", "groundFloor": "concrete loading ramp, exposed concrete columns", "colorScheme": "raw grey concrete, dark steel window frames, glass"},
            "roofDetail": {"form": "flat slab with concrete monitor clerestories", "material": "concrete slab with glass monitors"},
            "palette": {"primary": "#A9A9A9"}
        },
        {
            "id": "factory_brick_timber_mill",
            "label": "Brick & Timber Mill",
            "description": "Traditional brick and heavy timber mill building with massive timber post-and-beam structure, slow-burning construction, and tall multi-pane windows.",
            "prompt": "Brick and timber mill building. Heavy masonry industrial building of dark red-brown brick with massive internal heavy timber post-and-beam structure visible through the tall windows. Very tall multi-pane steel-sash windows organized in vertical stacks between brick piers -- the windows are taller than they are wide, filling most of the wall area. Segmental brick arches over each window group. Stone foundation and sills. Loading crane bracket projecting from upper floor. Heavy timber floor beams visible at the window heads. Brick stair tower with arched windows. Brick chimney. Inspired by 19th-century New England textile mills and Lowell National Historical Park.",
            "facadeDetail": {"primaryMaterial": "dark red-brown brick with segmental arches over windows", "secondaryMaterial": "heavy timber structure visible through windows, stone sills", "groundFloor": "loading doors and tall windows with stone lintels", "colorScheme": "dark red-brown brick, warm timber interior visible, stone grey accents"},
            "roofDetail": {"form": "low-pitched gable with brick end walls", "material": "slate or wood shingle"},
            "palette": {"primary": "#6B3A2A"}
        },
        {
            "id": "factory_steel_sash_monitor",
            "label": "Steel-Sash Monitor",
            "description": "Steel-framed factory with raised monitor roof (clerestory) running the length of the building, providing bilateral top-lighting to the factory floor.",
            "prompt": "Steel-framed monitor-roof factory. Wide-span single-story industrial building with a raised central monitor (clerestory) running the full length of the building. The monitor has continuous steel-framed glazing on both sides providing even bilateral top-lighting. Exposed steel truss structure visible through the monitor glazing. Walls of corrugated metal cladding on a steel frame with bands of steel-sash pivot windows at work-bench height. Large sliding steel doors for vehicle access. Painted steel structure in industrial grey-green. Ventilation louvers in the monitor roof. Surrounding context: industrial yard with concrete aprons. Inspired by mid-century American light industrial buildings.",
            "facadeDetail": {"primaryMaterial": "corrugated metal cladding on steel frame", "secondaryMaterial": "steel-sash pivot windows in horizontal bands", "groundFloor": "large sliding steel doors, concrete loading apron", "colorScheme": "grey-green painted steel, silver corrugated metal, industrial glass"},
            "roofDetail": {"form": "gable with raised central monitor clerestory", "material": "corrugated metal with steel-framed glass monitor"},
            "palette": {"primary": "#6B7B6B"}
        }
    ]
},

"industrial_park_modernism": {
    "id": "industrial_park_modernism",
    "title": "Industrial Park Modernism",
    "description": "Contemporary light industrial building in a suburban business park setting with clean modern materials and efficient flexible floor plans",
    "developmentType": "industrial",
    "buildingSubcategory": "Light Industrial",
    "aestheticCategory": "industrial_park",
    "minFloors": 1,
    "maxFloors": 3,
    "suggestedAreaSqm": 4000,
    "shadeId": "#708090",
    "facadeDetail": {
        "primaryMaterial": "tilt-up concrete or metal panel cladding",
        "secondaryMaterial": "aluminum-framed storefront glazing at office entrance",
        "accentMaterial": "painted steel canopies, corporate signage",
        "groundFloor": "glazed office entrance with loading docks at rear",
        "upperFloors": "minimal fenestration, metal panels or precast concrete",
        "cornice": "clean flat parapet with metal coping",
        "colorScheme": "neutral grey panels, accent color at entrance, corporate branding"
    },
    "roofDetail": {
        "form": "flat or very low slope with screened mechanical equipment",
        "material": "TPO or EPDM membrane",
        "features": "screened rooftop units, skylights in warehouse portion",
        "aerialAppearance": "flat white or grey membrane roof with mechanical screens"
    },
    "variants": [
        {
            "id": "industrial_tilt_up_concrete",
            "label": "Tilt-up Concrete",
            "description": "Tilt-up concrete panel industrial building with textured concrete walls, minimal windows, and efficient box form.",
            "prompt": "Tilt-up concrete industrial building. Simple rectangular box form with textured concrete tilt-up wall panels -- each panel shows visible form-tie holes and sandblasted exposed-aggregate finish. Minimal fenestration: a strip of aluminum-framed windows at the office portion only. Large overhead coiling doors for loading. Painted steel entrance canopy with corporate signage. Concrete panel joints sealed with dark sealant creating a subtle grid pattern. Flat roof behind a concrete parapet with metal coping. Landscaped parking lot frontage with young trees. Typical suburban business park setting. Clean, efficient, no-nonsense industrial architecture.",
            "facadeDetail": {"primaryMaterial": "textured tilt-up concrete panels with exposed aggregate", "secondaryMaterial": "aluminum-framed office windows, steel entrance canopy", "groundFloor": "office entrance with storefront glazing, warehouse with overhead doors", "colorScheme": "warm grey concrete, dark sealant joints, painted steel accents"},
            "roofDetail": {"form": "flat with concrete parapet and metal coping", "material": "TPO membrane"},
            "palette": {"primary": "#A0A0A0"}
        },
        {
            "id": "industrial_pemb",
            "label": "Pre-Engineered Metal",
            "description": "Pre-engineered metal building (PEMB) with standing-seam metal walls and roof, clear-span rigid frame, and functional efficiency.",
            "prompt": "Pre-engineered metal building. Clear-span rigid-frame steel structure clad entirely in standing-seam metal panels in two-tone color scheme: dark charcoal walls with lighter silver roof panels. Steel ridge cap and gutter trim in accent color. Personnel door with small canopy. Large drive-through overhead doors. Translucent fiberglass roof panels providing natural daylight without windows. Ventilation ridge cap running the full length. Concrete slab floor visible at door openings. Downspouts and gutters in matching metal. Simple functional form with no architectural pretension. Gravel yard with concrete apron at doors. Typical industrial park setting.",
            "facadeDetail": {"primaryMaterial": "standing-seam metal wall panels in charcoal", "secondaryMaterial": "lighter metal roof panels, translucent fiberglass skylights", "groundFloor": "large overhead doors, personnel entry with small metal canopy", "colorScheme": "charcoal metal walls, silver roof, colored trim accents"},
            "roofDetail": {"form": "low-pitched gable with ridge ventilator", "material": "standing-seam metal with translucent panels"},
            "palette": {"primary": "#505050"}
        },
        {
            "id": "industrial_high_tech_flex",
            "label": "High-Tech Flex",
            "description": "High-tech flex industrial building with exposed steel structure, glass office front, and adaptable warehouse/lab space.",
            "prompt": "High-tech flex industrial building. Exposed painted steel structural frame visible on the exterior in bright white. Full-height glass curtain wall at the office/showroom portion with visible steel cross-bracing. Insulated metal panel cladding on the warehouse portion in clean silver. Transition from transparent office to opaque warehouse clearly expressed. Steel tension-rod entrance canopy. Loading dock screened by perforated metal panels. Rooftop mechanical equipment screened behind matching metal panels. Clean high-tech aesthetic suggesting R&D or tech manufacturing. Landscaped frontage with modern planters. Inspired by high-tech business parks in Silicon Valley and Cambridge Science Park.",
            "facadeDetail": {"primaryMaterial": "exposed white-painted steel frame with glass and metal panels", "secondaryMaterial": "insulated metal panels, perforated metal screens", "groundFloor": "glass office front transitioning to metal-clad warehouse", "colorScheme": "white steel frame, silver metal panels, clear glass, minimal accents"},
            "roofDetail": {"form": "flat with screened mechanical equipment", "material": "standing-seam metal"},
            "palette": {"primary": "#E0E0E0"}
        },
        {
            "id": "industrial_glass_front_tech",
            "label": "Glass-Front Tech",
            "description": "Sleek glass-front tech/R&D building with corporate lobby, clean modern materials, and campus-like landscaping.",
            "prompt": "Glass-front tech industrial building. Sleek modern facade with a dramatic two-story glass curtain wall office lobby facing the street, transitioning to a clean white metal-panel warehouse/lab wing behind. The glass front features a bold cantilevered aluminum sunshade brow above. Interior visible through the glass: polished concrete floors, exposed ductwork, tech-startup aesthetic. Corporate logo subtly embedded in the glass entrance. Warehouse wing with flush metal panels and concealed loading at the rear. Extensive modern landscaping: ornamental grasses, specimen trees, LED-lit pathways. Employee outdoor terrace visible. Inspired by Apple Park supplier buildings and modern biotech campuses.",
            "facadeDetail": {"primaryMaterial": "full-height glass curtain wall at office, white metal panels at warehouse", "secondaryMaterial": "cantilevered aluminum sunshade brow, frameless glass entrance", "groundFloor": "dramatic glass lobby with polished concrete floors visible", "colorScheme": "clear glass, white metal panels, silver aluminum, modern landscaping"},
            "roofDetail": {"form": "flat with clean edge, solar panel array on warehouse roof", "material": "TPO membrane with rooftop solar"},
            "palette": {"primary": "#F5F5F5"}
        }
    ]
},

"art_deco_industrial": {
    "id": "art_deco_industrial",
    "title": "Art Deco Industrial",
    "description": "Art Deco-influenced industrial building combining utilitarian function with decorative geometric ornament, popular in 1920s-1940s utility and manufacturing buildings",
    "developmentType": "industrial",
    "buildingSubcategory": "Light Industrial",
    "aestheticCategory": "art_deco_industrial",
    "minFloors": 1,
    "maxFloors": 4,
    "suggestedAreaSqm": 4000,
    "shadeId": "#B8860B",
    "facadeDetail": {
        "primaryMaterial": "buff brick or cast stone with geometric ornament",
        "secondaryMaterial": "steel-sash industrial windows, terra cotta accents",
        "accentMaterial": "geometric terra cotta panels, chrome or aluminum trim",
        "groundFloor": "brick entrance surround with stepped geometric lintel",
        "upperFloors": "large industrial windows between brick piers with geometric spandrels",
        "cornice": "stepped parapet with geometric ornament",
        "colorScheme": "buff brick, terra cotta ornament, chrome accents"
    },
    "roofDetail": {
        "form": "stepped parapet with Art Deco geometric crown",
        "material": "built-up roof behind ornamental parapet",
        "features": "geometric parapet silhouette, decorative ventilator housings",
        "aerialAppearance": "flat roof with stepped Art Deco parapet profile"
    },
    "variants": [
        {
            "id": "industrial_wpa_rustic",
            "label": "WPA Rustic",
            "description": "Depression-era WPA rustic industrial building with native stone construction, hand-crafted details, and simplified Deco geometric ornament built by Civilian Conservation Corps workers.",
            "prompt": "WPA Rustic industrial building. Sturdy utilitarian building constructed of rough-cut native fieldstone with massive stone lintels over openings. Simplified Art Deco geometric ornament carved into stone panels above the entrance: stylized gear wheels, wheat sheaves, and worker figures in bas-relief. Heavy timber roof trusses visible through large multi-pane windows. Massive stone chimney. Stone walls with visible mortar joints and varied stone colors (grey, brown, tan). Steel-sash industrial windows in groups. Low-pitched roof with wide overhanging eaves supported by timber brackets. Native stone retaining walls and steps. Inspired by 1930s CCC and WPA-built utility buildings in national parks and rural communities.",
            "facadeDetail": {"primaryMaterial": "rough-cut native fieldstone with varied colors", "secondaryMaterial": "heavy timber trusses visible inside, stone carved bas-relief panels", "groundFloor": "massive stone entrance with carved geometric panels, timber doors", "colorScheme": "natural grey-brown stone, warm timber, steel windows"},
            "roofDetail": {"form": "low-pitched gable with wide timber-bracketed eaves", "material": "slate or wood shingle"},
            "palette": {"primary": "#8B7D6B"}
        },
        {
            "id": "industrial_streamline_plant",
            "label": "Streamline Plant",
            "description": "Streamline Moderne industrial plant with curved corners, glass block stair towers, horizontal speed lines, and machine-age optimism.",
            "prompt": "Streamline Moderne industrial plant. Sleek aerodynamic industrial building with dramatically curved corners and smooth white or cream rendered surfaces. Continuous horizontal speed lines (raised horizontal bands) wrapping around the building. Glass block stair tower at the corner glowing from within. Horizontal ribbon windows with thin steel frames following the curves. Streamlined entrance with a curved concrete canopy and chrome-framed glass doors. Flat roof with a streamlined parapet. The building looks like it's moving even standing still -- pure machine-age optimism. Chrome lettering for company name. Painted steel pipe railings. Inspired by streamlined 1930s factories and Art Deco industrial buildings.",
            "facadeDetail": {"primaryMaterial": "smooth white or cream rendered concrete with curved corners", "secondaryMaterial": "glass block tower, horizontal ribbon windows", "groundFloor": "streamlined curved entrance with chrome-framed glass and concrete canopy", "colorScheme": "white or cream render, chrome accents, glass block glow"},
            "roofDetail": {"form": "flat with streamlined curved parapet", "material": "white rendered parapet"},
            "palette": {"primary": "#F5F0E0"}
        },
        {
            "id": "industrial_zigzag_utility",
            "label": "Zigzag Utility",
            "description": "Zigzag Art Deco utility building (power station or pumping station) with bold geometric ornament, stepped massing, and polychrome terra cotta accents.",
            "prompt": "Zigzag Art Deco utility building. Bold buff brick industrial facade with rich polychrome terra cotta geometric ornament. Stepped parapet creating a dramatic zigzag crown silhouette with chevron and sunburst motifs in gold and turquoise terra cotta. Tall vertical window bays between brick piers rising the full height. Decorative terra cotta spandrel panels between floors with geometric industrial motifs: gears, lightning bolts, stylized machinery. Elaborate entrance surround in carved stone with geometric bronze doors. Brick buttress piers at corners adding structural drama. The building celebrates industrial power through Art Deco ornamental language. Inspired by Battersea Power Station's decorative elements and 1920s utility architecture.",
            "facadeDetail": {"primaryMaterial": "buff brick with polychrome terra cotta ornament", "secondaryMaterial": "gold and turquoise terra cotta panels with geometric motifs", "groundFloor": "elaborate carved stone entrance with geometric bronze doors", "colorScheme": "buff brick, gold and turquoise terra cotta, bronze accents"},
            "roofDetail": {"form": "stepped zigzag parapet with terra cotta crown", "material": "built-up roof behind ornamental parapet"},
            "palette": {"primary": "#D4A76A"}
        },
        {
            "id": "industrial_stripped_classicism_utility",
            "label": "Stripped Classicism Utility",
            "description": "Stripped Classical industrial building combining monumental simplified classical forms with utilitarian function -- heavy stone base, simplified pilasters, and severe geometric proportions.",
            "prompt": "Stripped Classical utility building. Monumental industrial building of smooth pale limestone with severely simplified classical elements. Massive simplified square pilasters (no capitals, no fluting) marching across the facade between tall steel-sash window bays. Heavy rusticated stone base. Simple flat entablature with no moldings -- just a plain stone band at the roofline. Deeply recessed entrance with oversized bronze doors featuring geometric low-relief panels. The classical language is reduced to pure geometry: rectangles, squares, and proportion. Tall industrial windows with minimal stone mullions between the pilasters. Severe, monumental, and powerful. Inspired by stripped classical power stations and water treatment plants of the 1930s-1940s.",
            "facadeDetail": {"primaryMaterial": "smooth pale limestone with simplified square pilasters", "secondaryMaterial": "tall steel-sash windows between pilasters, bronze doors", "groundFloor": "heavy rusticated stone base with monumental bronze entrance", "colorScheme": "pale limestone, dark bronze doors, dark window voids, stone grey"},
            "roofDetail": {"form": "flat with heavy stone parapet and simple entablature", "material": "hidden behind stone parapet"},
            "palette": {"primary": "#C4B896"}
        }
    ]
},

}  # end ALL_ARCHETYPES


# ---------------------------------------------------------------------------
# Image generation
# ---------------------------------------------------------------------------

def generate_image(prompt: str, retries: int = 2) -> bytes | None:
    """Call Gemini Pro API and return PNG bytes."""
    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseModalities": ["TEXT", "IMAGE"],
            "temperature": 0.0,
        },
    }

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
                if attempt < retries:
                    time.sleep(10)
                    continue
                return None

            data = resp.json()
            candidates = data.get("candidates", [])
            if not candidates:
                print("  X No candidates in response")
                return None

            for part in candidates[0].get("content", {}).get("parts", []):
                if "inlineData" in part:
                    b64 = part["inlineData"]["data"]
                    return base64.b64decode(b64)

            print("  X No image in response")
            return None

        except Exception as e:
            print(f"  X Exception: {e}")
            if attempt < retries:
                time.sleep(10)
                continue
            return None

    return None


def resize_and_crop(img_bytes: bytes, w: int, h: int) -> bytes:
    """Resize image to target dimensions, center-cropping if needed."""
    img = Image.open(io.BytesIO(img_bytes))
    ratio = max(w / img.width, h / img.height)
    new_w = int(img.width * ratio)
    new_h = int(img.height * ratio)
    img = img.resize((new_w, new_h), Image.LANCZOS)
    left = (new_w - w) // 2
    top = (new_h - h) // 2
    img = img.crop((left, top, left + w, top + h))
    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return buf.getvalue()


def generate_archetype_images(arch_id: str, arch_data: dict, skip_existing: bool = True):
    """Generate all variant images for a single archetype."""
    out_dir = _PUBLIC_DIR / "buildings" / arch_id
    out_dir.mkdir(parents=True, exist_ok=True)

    variants = arch_data["variants"]
    print(f"\n{'='*60}")
    print(f"Archetype: {arch_data['title']} ({arch_id})")
    print(f"Output: {out_dir}")
    print(f"Variants: {len(variants)}")
    print(f"{'='*60}")

    for i, variant in enumerate(variants):
        filename = f"variant_{i}.png"
        filepath = out_dir / filename

        if skip_existing and filepath.exists():
            print(f"  [{i}] {variant['label']} -- already exists, skipping")
            continue

        prompt = (
            BUILDING_FRAME +
            variant["prompt"] + " " +
            NO_PEOPLE + " " + STYLE_ANCHOR
        )

        print(f"  [{i}] Generating {variant['label']}...")
        img_bytes = generate_image(prompt)

        if img_bytes:
            cropped = resize_and_crop(img_bytes, CARD_WIDTH, CARD_HEIGHT)
            filepath.write_bytes(cropped)
            print(f"  OK Saved {filepath.name} ({len(cropped):,} bytes)")
        else:
            print(f"  X Failed to generate {variant['label']}")

        # Rate limit between images
        if i < len(variants) - 1:
            print("  .. Waiting 5s for rate limit...")
            time.sleep(5)

    # Copy variant_0 as hero.png if needed
    v0 = out_dir / "variant_0.png"
    hero = out_dir / "hero.png"
    if v0.exists() and not hero.exists():
        hero.write_bytes(v0.read_bytes())
        print(f"  OK Copied variant_0.png -> hero.png")


def update_archetypes_json(generated_archetypes: dict):
    """Add generated archetypes to buildingArchetypes.json."""
    json_path = _DATA_DIR / "buildingArchetypes.json"
    data = json.loads(json_path.read_text(encoding="utf-8"))

    existing_ids = {a["id"] for a in data["archetypes"]}

    added = 0
    for arch_id, arch_data in generated_archetypes.items():
        if arch_id in existing_ids:
            print(f"  Skipping {arch_id} -- already in JSON")
            continue

        # Build the JSON entry
        entry = {
            "id": arch_id,
            "shadeId": arch_data.get("shadeId", "#888888"),
            "title": arch_data["title"],
            "aestheticCategory": arch_data.get("aestheticCategory", arch_id),
            "description": arch_data["description"],
            "buildingSubcategory": arch_data.get("buildingSubcategory", "General"),
            "generationTags": [arch_data.get("aestheticCategory", arch_id), arch_data.get("buildingSubcategory", "").lower().replace(" ", "_")],
            "palette": {"skyTop": "#8fa2b8", "skyBottom": "#c4b896", "ground": "#8a8a7a", "accent": arch_data.get("shadeId", "#888888")},
            "styleProfile": {"era": "", "influences": [], "keywords": []},
            "facadeDetail": arch_data.get("facadeDetail", {}),
            "roofDetail": arch_data.get("roofDetail", {}),
            "thumbnailUrl": f"/archetypes/buildings/{arch_id}/hero.png",
            "variants": [],
            "minFloors": arch_data.get("minFloors", 2),
            "maxFloors": arch_data.get("maxFloors", 6),
            "suggestedAreaSqm": arch_data.get("suggestedAreaSqm", 5000),
            "developmentType": arch_data.get("developmentType", "institutional"),
        }

        # Add variant entries
        for i, v in enumerate(arch_data["variants"]):
            entry["variants"].append({
                "id": v["id"],
                "label": v["label"],
                "thumbnailUrl": f"/archetypes/buildings/{arch_id}/variant_{i}.png",
                "description": v["description"],
                "facadeDetail": v.get("facadeDetail", {}),
                "roofDetail": v.get("roofDetail", {}),
                "shadeId": None,
                "palette": v.get("palette", {"primary": "#888888"}),
            })

        data["archetypes"].append(entry)
        added += 1
        print(f"  Added {arch_id} to JSON")

    if added > 0:
        json_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"\nUpdated {json_path} with {added} new archetypes")
    else:
        print("\nNo new archetypes to add to JSON")


def main():
    parser = argparse.ArgumentParser(description="Generate archetype card images")
    parser.add_argument("--category", type=str, help="Only generate specific category (e.g., 'neoclassical_institutional')")
    parser.add_argument("--skip-existing", action="store_true", default=True, help="Skip images that already exist")
    parser.add_argument("--no-skip", action="store_true", help="Regenerate all images even if they exist")
    parser.add_argument("--json-only", action="store_true", help="Only update JSON, don't generate images")
    args = parser.parse_args()

    skip = not args.no_skip

    if args.category:
        if args.category not in ALL_ARCHETYPES:
            print(f"Unknown category: {args.category}")
            print(f"Available: {', '.join(ALL_ARCHETYPES.keys())}")
            sys.exit(1)
        targets = {args.category: ALL_ARCHETYPES[args.category]}
    else:
        targets = ALL_ARCHETYPES

    total_images = sum(len(a["variants"]) for a in targets.values())
    print(f"Generating {len(targets)} archetypes, {total_images} images total")
    print(f"Model: {MODEL}")
    print(f"Skip existing: {skip}")
    print(f"Estimated cost: ${total_images * 0.134:.2f}")
    print()

    if not args.json_only:
        for arch_id, arch_data in targets.items():
            generate_archetype_images(arch_id, arch_data, skip_existing=skip)
            # Brief pause between archetypes
            time.sleep(3)

    # Update JSON
    print("\n" + "="*60)
    print("Updating buildingArchetypes.json...")
    print("="*60)
    update_archetypes_json(targets)

    print("\n" + "="*60)
    print("DONE!")
    print(f"Generated images for {len(targets)} archetypes")
    print("="*60)


if __name__ == "__main__":
    main()
