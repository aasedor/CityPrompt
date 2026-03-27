"""
Generate 44 archetype images (11 archetypes x 4 variants) for streets and parks.
Uses Gemini 3 Pro Image API.
"""
from __future__ import annotations
import base64, json, sys, time, shutil
from pathlib import Path
import httpx

_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SCRIPT_DIR.parent
_ENV_FILE = _PROJECT_ROOT / "backend" / ".env"
_PUBLIC_DIR = _PROJECT_ROOT / "frontend" / "public" / "archetypes"

def _load_api_key():
    for line in _ENV_FILE.read_text().splitlines():
        if line.strip().startswith("GEMINI_API_KEY="):
            return line.strip().split("=", 1)[1].strip()
    sys.exit("ERROR: GEMINI_API_KEY not found")

API_KEY = _load_api_key()
MODEL = "gemini-3-pro-image-preview"
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={API_KEY}"

# ─────────────────────────────────────────────
# STREETS (go in frontend/public/archetypes/streets/{kebab-case}/)
# ─────────────────────────────────────────────
STREET_ARCHETYPES = {
    "downtown-thoroughfare": [
        "Aerial photograph at 3/4 angle looking down a wide 6-lane downtown street in a major American city, golden hour warm light. Dark asphalt with white lane markings. Concrete sidewalks with Honey Locust trees in metal grates. 8-12 story brick and limestone buildings with ground-floor retail, canvas awnings. Parallel parked cars. Red city bus at transit shelter. Photorealistic, 8K.",
        "Aerial photograph at 3/4 angle of a grand European boulevard with tram tracks in grass median, double row of Platanus trees, wide granite sidewalks with cafe terraces under cream parasols. 6-8 story Haussmann buildings with limestone facades and mansard roofs. Modern low-floor tram. Photorealistic, 8K.",
        "Aerial photograph at 3/4 angle of a dense Asian downtown thoroughfare like Shibuya. 6-lane road with BRT station platform. 15-30 story glass towers with illuminated signage in Asian characters. Narrow packed sidewalks, covered arcade canopies, elevated pedestrian bridge. Dense overhead utility lines. Photorealistic, 8K.",
        "Aerial photograph at 3/4 angle of a contemporary complete street. Two travel lanes with planted median rain gardens. Protected bidirectional cycle track. Wide sidewalks with bioretention planters and Red Maple trees. 4-8 story contemporary mixed-use buildings with wood-panel accents. Parklet in converted parking bay. Photorealistic, 8K.",
    ],
    "pedestrian-only-street": [
        "Aerial photograph at 3/4 angle of a historic European pedestrian shopping street like Stroget Copenhagen. Full-width gray granite sett paving in fan patterns. 3-5 story painted plaster and brick facades. Wooden benches, cast-iron globe lamps, flower planters with red geraniums. Small fountain focal point. Golden hour. Photorealistic, 8K.",
        "Aerial photograph at 3/4 angle of a Mediterranean pedestrian promenade. Wide cream limestone paving with terracotta brick bands. Double row of Plane trees. Cafe terraces with white parasols. 3-5 story ochre and white stucco buildings with green shutters and bougainvillea. Central linear water feature. Golden hour. Photorealistic, 8K.",
        "Aerial photograph at 3/4 angle of an Asian night market pedestrian street at dusk. Narrow 10m street with concrete paving. 2-4 story shophouses. Market stalls with red, blue, green canvas canopies. Overhead string lights and red paper lanterns. Steam from food stalls. Dense signage in Asian characters. Photorealistic, 8K.",
        "Aerial photograph at 3/4 angle of a contemporary redesigned pedestrian street. Large light gray concrete pavers with stainless steel drainage. Corten steel planters with ornamental grasses and multi-stem Birch trees. Contemporary timber-slat benches. Mix of restored brick warehouses and new glass buildings. Abstract Corten sculpture. Golden hour. Photorealistic, 8K.",
    ],
    "green-alley": [
        "Aerial photograph at 3/4 angle of a Chicago-style green alley. Light cream permeable concrete pavers in herringbone pattern. Wood fences along both sides. Mature trees overhanging from backyards. LED cobra-head lights on poles. Recycled aggregate at edges. Single parked car. Golden hour. Photorealistic, 8K.",
        "Aerial photograph at 3/4 angle of a residential alley with continuous bioswale. Right two-thirds permeable asphalt, left third a bioswale with Carex sedges, Soft Rush, Blue Flag Iris. River cobble at inlets, limestone check dams. Adjacent 2-story houses. Mature shade trees. Golden hour. Photorealistic, 8K.",
        "Aerial photograph at 3/4 angle of an alley with alternating rain garden cells on both sides. Central permeable concrete pavers. Staggered rain gardens with Purple Coneflower, Black-Eyed Susan, Little Bluestem in purple, yellow, gold. Wood privacy fences. Mature Bur Oak trees. Golden hour. Photorealistic, 8K.",
        "Aerial photograph at 3/4 angle of a heavily planted native alley like a garden path. Decomposed granite pathway winding through dense Big Bluestem, Switchgrass, Wild Bergamot, Goldenrod. Flagstone stepping stones to garages. Rain barrels, birdhouses. Cedar post-and-rail fences. Wild, biodiverse. Golden hour. Photorealistic, 8K.",
    ],
    "commercial-alley-laneway": [
        "Aerial photograph at 3/4 angle of a narrow Melbourne-style laneway. 4-5 story brick warehouses with walls covered in colorful street art murals and graffiti. Bluestone flagstone paving. Tiny cafe fronts with reclaimed timber counters. Edison-bulb string lights overhead. Fire escapes and exposed pipes. Golden hour. Photorealistic, 8K.",
        "Aerial photograph at 3/4 angle of a Tokyo yokocho drinking alley at blue hour. Ultra-narrow 2.5m passage between timber and corrugated metal buildings. Noren curtains at bar entrances. Paper lanterns in red and white. Tangled overhead wires. Counter seating visible through doors. Steam from yakitori grill. Worn concrete paving with puddles. Photorealistic, 8K.",
        "Aerial photograph at 3/4 angle looking through a glass barrel-vault roof of a 19th-century European shopping passage. Iron-and-glass ceiling with geometric shadows. Polished cream and black marble floor in checkerboard. Ornate shop fronts with gilded lettering. Brass pendant lights. Wrought-iron gallery railings. Potted palms. Golden hour. Photorealistic, 8K.",
        "Aerial photograph at 3/4 angle of a Brooklyn-style activated alley between brick loft buildings. Asphalt painted with bold geometric mural in teal, coral, yellow. Pop-up vendor stalls with canvas awnings. Reclaimed wood picnic tables. Edison-bulb string lights overhead. Polished Airstream food truck. Large botanical mural on brick wall. Golden hour. Photorealistic, 8K.",
    ],
    "yield-street": [
        "Aerial photograph at 3/4 angle of a narrow Dutch woonerf residential street. Continuous red-brown clay brick pavers in herringbone, no curbs. Black bollards and planters with Hydrangeas defining the driving lane. 3-story brick rowhouses with stepped gables. Potted plants and bicycles at facades. Linden trees. Golden hour. Photorealistic, 8K.",
        "Aerial photograph at 3/4 angle of a narrow historic New England street like Beacon Hill. Worn red-brown brick paving with granite curbing. 3-4 story Federal-style brick rowhouses with black shutters, white trim. Brick sidewalks. Black gas-lamp street lights. Mature Elm trees creating arching canopy. Window boxes with geraniums. Slight uphill grade. Golden hour. Photorealistic, 8K.",
        "Aerial photograph at 3/4 angle of an extremely narrow Japanese residential alley. 3m-wide gray asphalt with white edge lines, no sidewalks. 2-story traditional houses with dark ceramic tile roofs, timber siding. Potted plants along building bases. Utility poles with overhead wires. Bicycles in racks. Mirror at corner. Immaculately clean. Golden hour. Photorealistic, 8K.",
        "Aerial photograph at 3/4 angle of a Scandinavian shared-space street. Light gray granite block pavers. Corten steel planters with ornamental grasses and Silver Birch trees creating chicanes. Timber bollards. 2-3 story contemporary houses with vertical timber cladding and green roofs. Cargo bikes near entries. Stainless steel drainage channels. Golden hour. Photorealistic, 8K.",
    ],
    "neighborhood-main-street": [
        "Aerial photograph at 3/4 angle of a small-town American main street. Two-lane road with diagonal parking. 2-3 story red and cream brick commercial buildings with pressed-metal cornices, canvas awnings, carved wood blade signs. Wide concrete sidewalks with brick accents. Black lamp posts with hanging flower baskets. Zelkova trees. Golden hour. Photorealistic, 8K.",
        "Aerial photograph at 3/4 angle of an English Victorian market town high street. Narrow two-lane road with parked cars. 2-3 story buildings in honey Cotswold stone, red brick, and painted stucco with Victorian sash windows and bay windows. York stone sidewalks. Victorian cast-iron lamp posts. Red pillar box. Ornate clock tower. Golden hour. Photorealistic, 8K.",
        "Aerial photograph at 3/4 angle of a Mediterranean village commercial street. Narrow 6m roadway paved in worn sandstone blocks. 2-3 story stucco buildings in white, ochre, terracotta with barrel-tile roofs, wooden shutters, wrought-iron balconies with bougainvillea. Arched doorways, canvas awnings. Potted lemon trees. Church bell tower above roofline. Golden hour. Photorealistic, 8K.",
        "Aerial photograph at 3/4 angle of a contemporary neighborhood main street. Two lanes with protected bike lane and raised planters. Wide sidewalks with rain garden tree trenches. 3-4 story contemporary mixed-use with NanaWall storefronts, cedar cladding, metal accents. Modern black steel street furniture. Wayfinding signage totem. Golden hour. Photorealistic, 8K.",
    ],
}

# ─────────────────────────────────────────────
# PARKS (go in frontend/public/archetypes/openspaces/{kebab-case}/)
# ─────────────────────────────────────────────
PARK_ARCHETYPES = {
    "linear-park-greenway": [
        "Aerial photograph at 3/4 angle of a rail trail linear park. 12-foot asphalt path along former rail corridor. Preserved steel tracks embedded in path. Wildflower meadow banks with Black-Eyed Susan, Purple Coneflower, Goldenrod. Railroad-tie benches. Steel truss rail bridge. Corten steel interpretive signs. Cyclists and joggers. Golden hour. Photorealistic, 8K.",
        "Aerial photograph at 3/4 angle of a riverfront greenway. Light concrete path parallel to a flowing river. Timber-and-steel overlook platforms cantilevered over the bank with cable railings. Weeping Willows and River Birch riparian buffer. Lawn terraces. Kayak launch ramp. Cable-stayed pedestrian bridge. Golden hour reflections on water. Photorealistic, 8K.",
        "Aerial photograph at 3/4 angle of a daylighted urban creek restoration park. Small meandering creek with gravel riffles and boulder weirs. Ipe timber boardwalk over wetland with Cattails and Blue Flag Iris. Crushed limestone path under Sycamores and Red Maples. Rain garden bioretention at stormwater outfalls. Ecology interpretive signs. Golden hour. Photorealistic, 8K.",
        "Aerial photograph at 3/4 angle of an elevated linear park on a repurposed rail viaduct like the High Line. Weathered Corten steel viaduct 8m above street. Concrete plank paving with ornamental grasses and perennials emerging through gaps. Built-in concrete bench seating. Cantilevered viewing platform. Preserved rail tracks. City buildings flanking both sides. Golden hour. Photorealistic, 8K.",
    ],
    "nature-preserve": [
        "Aerial photograph at 3/4 angle of a wetland nature preserve. Narrow ipe timber boardwalk elevated 1m above marsh water, winding through Cattails and Common Reed in amber-gold. Octagonal observation platform with Corten interpretive panel. Wood duck nesting boxes. Great Blue Heron in shallows. Bald Cypress trees at edges. Crushed shell path to visitor center. Golden hour. Photorealistic, 8K.",
        "Aerial photograph at 3/4 angle of a tallgrass prairie reserve. Mown trail through shoulder-height Big Bluestem and Indian Grass in gold and bronze. Scattered wildflowers — Compass Plant, Prairie Blazing Star. Timber observation platform. Burn management mosaic visible. Corten steel trail post. Distant Bur Oak savanna. Big expansive sky. Golden hour. Photorealistic, 8K.",
        "Aerial photograph at 3/4 angle of a coastal dune conservation area. Narrow timber boardwalk with rope railings through white sand dunes with Beach Grass and Seaside Goldenrod. Timber sand fencing. Rope-post barriers around Piping Plover nesting zone. Elevated observation platform overlooking sandy beach and ocean. Wind-sculpted dune forms. Coastal shrubs. Golden hour. Photorealistic, 8K.",
        "Aerial photograph at 3/4 angle of a trail through old-growth forest. Narrow crushed-stone path between massive 1-2m diameter tree trunks with deep furrowed bark. Fallen moss-covered logs with sword ferns. Ipe boardwalk over wet area. Nurse log with young trees growing from it. Dappled golden light through dense canopy 30-40m above. Cathedral-like atmosphere. Photorealistic, 8K.",
    ],
    "rooftop-garden": [
        "Aerial photograph at 3/4 angle of a lush intensive rooftop garden atop a 6-story building. Deep planting beds with Japanese Maple, multi-stem Birch, Hydrangeas, Lavender borders. Cedar pergola with Wisteria. Small reflecting pool with black granite edge. Ipe deck lounge area with teak furniture. Mown lawn panel. Glass railing with city views beyond. Golden hour. Photorealistic, 8K.",
        "Aerial photograph at 3/4 angle of an extensive sedum green roof on a commercial building. Continuous patchwork carpet of Sedum species — silver-green, deep red, yellow-green, blue-gray. Modular tray edges visible. Aluminum gravel strip border around drains. Narrow concrete maintenance path. Screened HVAC equipment. Building parapet with metal coping. Adjacent urban rooftops below. Golden hour. Photorealistic, 8K.",
        "Aerial photograph at 3/4 angle of a rooftop urban farm on an industrial building. Grid of galvanized steel raised beds with vegetable rows — lettuces, kale, tomatoes on stakes, eggplant, herb rows. White hooped row covers over some beds. Black drip irrigation tubing. Small timber greenhouse. Cedar composting bins. Strawberry crates. City skyline beyond. Golden hour. Photorealistic, 8K.",
        "Aerial photograph at 3/4 angle of a rooftop social space and bar at blue hour. Charcoal porcelain tile paving. Concrete-and-wood bench seating around rectangular gas fire table. Bar structure with reclaimed wood top and pendant lights. Edison-bulb string lights overhead. Corten planters with tall grasses and Olive trees. Wicker lounge furniture with white cushions. Glass railing with panoramic city skyline. Photorealistic, 8K.",
    ],
    "riverfront-park-beach": [
        "Aerial photograph at 3/4 angle of an urban river beach. Golden sand beach area along a wide river. Stepped light gray concrete terraces. Red and white striped parasols and deck chairs on sand. Beach volleyball court. Timber lifeguard station. Rope-and-buoy swimming zone. Timber deck promenade with cafe kiosks above. Plane trees. People swimming and sunbathing. Golden hour reflections. Photorealistic, 8K.",
        "Aerial photograph at 3/4 angle of a lake swimming beach in a park. Crescent-shaped golden sand beach with turquoise shallow water. Ipe swimming dock extending into lake. Floating swim platform. Cedar-shingled bathhouse. Yellow lifeguard chair. Green picnic area with White Oak trees. Colorful kayaks on timber rack. Native shoreline plantings. Families on sand. Golden hour. Photorealistic, 8K.",
        "Aerial photograph at 3/4 angle of a waterfront adventure park on a former industrial pier. Heavy timber pier with kayak launch, colorful boats. Climbing wall on retained brick facade. Adventure playground with timber-rope structures. Splash pad with colorful surface. Gabion retaining walls. Corten railings. Native meadow plantings. Young families playing. River and city skyline beyond. Golden hour. Photorealistic, 8K.",
        "Aerial photograph at 3/4 angle of a naturalized riverfront park. Gently sloping bio-engineered bank with coir log stabilization and willow plantings. Wet meadow of sedges, Blue Flag Iris, Joe-Pye Weed. Crushed gravel path under Sycamores and Cottonwoods. Timber observation platform over quiet backwater with water lilies. Log seating. Turtle on rock. Serene ecological atmosphere. Golden hour. Photorealistic, 8K.",
    ],
    "street-plaza-parklet": [
        "Aerial photograph at 3/4 angle of a NYC-style street plaza. Former roadway painted with bold geometric pattern in bright yellow, white, gray. Dozens of yellow bistro chairs and tables scattered informally. Black planter boxes with geraniums and Serviceberry trees. Granite bollards at vehicle entry. 4-6 story commercial buildings adjacent. People eating lunch. Golden hour. Photorealistic, 8K.",
        "Aerial photograph at 3/4 angle of a San Francisco parklet in two parking spaces. Douglas fir timber deck at sidewalk grade with horizontal timber slat railing. Potted Rosemary, Lavender, Olive trees in terracotta pots on traffic side. Cafe tables and bistro chairs. Built-in corner bench. Chalkboard menu. Adjacent brick cafe storefront. Parked cars beyond. Golden hour. Photorealistic, 8K.",
        "Aerial photograph at 3/4 angle of a tactical urbanism community plaza. Spray-painted asphalt with community mural in blue, coral, green. Painted jersey barriers. Mismatched donated Adirondack chairs in bright colors. Tire planters and pallet furniture. String lights on wood poles. Hand-painted signs. Children playing, neighbors chatting. Scrappy, joyful atmosphere. Golden hour. Photorealistic, 8K.",
        "Aerial photograph at 3/4 angle of a refined European pocket plaza. Gray granite pavers at sidewalk grade. Corten steel planters with Amelanchier trees and Hakonechloa grass. Granite bubbler fountain with polished stone sphere. Dark gray cast-aluminum city benches. Cafe terrace with marble-top tables and bistro chairs under green awning. Retractable bollards. 4-story limestone buildings. Golden hour. Photorealistic, 8K.",
    ],
}

RATE_LIMIT_DELAY = 6  # seconds between requests


def generate_image(prompt: str, client: httpx.Client) -> bytes | None:
    """Call Gemini API and return PNG bytes, or None on failure."""
    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseModalities": ["TEXT", "IMAGE"],
            "temperature": 0.0,
        },
    }
    for attempt in range(3):
        try:
            resp = client.post(API_URL, json=body, timeout=120)
            if resp.status_code == 429:
                wait = 30 * (attempt + 1)
                print(f"  Rate limited, waiting {wait}s...")
                time.sleep(wait)
                continue
            resp.raise_for_status()
            data = resp.json()
            for part in data["candidates"][0]["content"]["parts"]:
                if "inlineData" in part:
                    return base64.b64decode(part["inlineData"]["data"])
            print("  WARNING: No image in response")
            return None
        except Exception as e:
            print(f"  ERROR attempt {attempt+1}: {e}")
            if attempt < 2:
                time.sleep(10)
    return None


def process_archetypes(archetypes: dict, base_dir: Path):
    """Generate images for a set of archetypes."""
    client = httpx.Client()
    total = sum(len(v) for v in archetypes.values())
    done = 0

    for kebab_name, prompts in archetypes.items():
        out_dir = base_dir / kebab_name
        out_dir.mkdir(parents=True, exist_ok=True)

        for vi, prompt in enumerate(prompts):
            variant_file = out_dir / f"variant_{vi}.png"
            if variant_file.exists():
                print(f"  SKIP (exists): {variant_file.relative_to(_PROJECT_ROOT)}")
                done += 1
                continue

            done += 1
            print(f"  [{done}/{total}] Generating {kebab_name} variant_{vi} ...")
            img_bytes = generate_image(prompt, client)
            if img_bytes:
                variant_file.write_bytes(img_bytes)
                print(f"    Saved {variant_file.relative_to(_PROJECT_ROOT)} ({len(img_bytes)} bytes)")
            else:
                print(f"    FAILED to generate {variant_file}")

            time.sleep(RATE_LIMIT_DELAY)

        # Copy variant_0 as hero
        v0 = out_dir / "variant_0.png"
        hero = out_dir / "hero.png"
        if v0.exists() and not hero.exists():
            shutil.copy2(v0, hero)
            print(f"  Copied hero.png from variant_0.png for {kebab_name}")

    client.close()


def main():
    streets_dir = _PUBLIC_DIR / "streets"
    parks_dir = _PUBLIC_DIR / "openspaces"

    print("=" * 60)
    print("GENERATING STREET ARCHETYPES (6 x 4 = 24 images)")
    print("=" * 60)
    process_archetypes(STREET_ARCHETYPES, streets_dir)

    print()
    print("=" * 60)
    print("GENERATING PARK ARCHETYPES (5 x 4 = 20 images)")
    print("=" * 60)
    process_archetypes(PARK_ARCHETYPES, parks_dir)

    # Copy hero for any that were skipped
    for name in list(STREET_ARCHETYPES) + list(PARK_ARCHETYPES):
        if name in STREET_ARCHETYPES:
            d = streets_dir / name
        else:
            d = parks_dir / name
        v0 = d / "variant_0.png"
        hero = d / "hero.png"
        if v0.exists() and not hero.exists():
            shutil.copy2(v0, hero)
            print(f"  Copied hero.png for {name}")

    print("\nDone! Generated all images.")


if __name__ == "__main__":
    main()
