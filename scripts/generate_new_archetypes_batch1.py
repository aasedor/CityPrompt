"""
Generate 28 archetype images (7 archetypes x 4 variants) using Gemini 3 Pro,
then update buildingArchetypes.json with the 7 new archetypes.
"""

import base64
import json
import shutil
import time
from pathlib import Path

import httpx

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_ENV_FILE = _PROJECT_ROOT / "backend" / ".env"
_ARCHETYPES_DIR = _PROJECT_ROOT / "frontend" / "public" / "archetypes" / "buildings"
_JSON_FILE = _PROJECT_ROOT / "frontend" / "src" / "data" / "buildingArchetypes.json"

MODEL = "gemini-3-pro-image-preview"
ENDPOINT = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"
WAIT_SECONDS = 8


def load_api_key() -> str:
    for line in _ENV_FILE.read_text().splitlines():
        if line.startswith("GEMINI_API_KEY="):
            return line.split("=", 1)[1].strip()
    raise RuntimeError("GEMINI_API_KEY not found in backend/.env")


ARCHETYPES = [
    {
        "dir": "concert_hall_modern",
        "prompts": [
            "Photorealistic 8K architectural rendering, aerial three-quarter angle view, golden hour warm light. A sculptural organic concert hall with flowing white aluminum-clad shell forms that undulate like windswept snow dunes. The building emerges from a wetland park with reflective ponds. Smooth matte white panels curve into a publicly accessible rooftop promenade. Crystalline glass curtain wall with diagrid steel reveals warmly lit lobby with Manchurian ash timber glowing amber. Ornamental grasses, birch trees, wooden boardwalks. Pedestrians on curved rooftop paths. Soft pink and gold sky reflecting in water.",
            "Photorealistic 8K architectural rendering, aerial three-quarter angle view, golden hour warm light. A monumental concert hall rising from a historic red-brown brick warehouse base, topped with a spectacular undulating glass crown. Thousands of curved glass panels with chrome-dot frit creating iridescent reflections. Biomorphic elliptical window openings. Sequin-textured metallic roof with tent-like peaks. Waterfront promenade with boats. Public observation plaza between old brick and new glass. 26 stories tall. Warm amber light glowing from within.",
            "Photorealistic 8K architectural rendering, aerial three-quarter angle view, golden hour warm light. A sweeping concert hall with two opposing continuous curved planes in weathered bronze-tone metal panels. Gently sloping landscaped public rooftop terrace with native grasses and wildflowers. Cherry wood acoustic panels visible through dramatic oculus opening. Waterfront site with mountains and ocean panorama. Public plaza with cafe terracing. Pedestrians ascending the rooftop walk.",
            "Photorealistic 8K architectural rendering, aerial three-quarter angle view, golden hour warm light. A bold deconstructivist concert hall with billowing stainless steel sail-like forms catching golden sunlight in metallic flashes. Massive curved steel panels twist and fold. Warm Douglas fir wood visible through tall glass curtain walls. Terraced garden surrounds the base. Civic plaza with fountains and public art. Downtown high-rise towers behind. Steel surfaces shift from warm gold to cool silver.",
        ],
    },
    {
        "dir": "vertiport_evtol",
        "prompts": [
            "Photorealistic 8K architectural rendering, aerial three-quarter angle view, golden hour warm light. A sleek rooftop vertiport atop a 40-story glass office tower. Circular TLOF landing pad with illuminated cyan blue guidance lines. Lightweight ETFE membrane canopy over a compact passenger lounge with curved glass walls. A quad-tilt-rotor eVTOL aircraft approaching. Warm timber interiors visible through glass. Landscaped green edges. City skyline to horizon. Wind indicators on minimalist steel masts.",
            "Photorealistic 8K architectural rendering, aerial three-quarter angle view, golden hour warm light. A purpose-built ground-level vertiport with a sweeping crescent-shaped building wrapping two circular landing pads. Dramatic overhanging aluminum roof canopy extending 8m beyond glass facade. Warm stone flooring and timber-slatted ceiling inside. Two eVTOL aircraft on charging pads. Integrated metro stop with covered pedestrian bridge. Native landscaping. Suburban context.",
            "Photorealistic 8K architectural rendering, aerial three-quarter angle view, golden hour warm light. A futuristic vertiport with a grove of tree-like steel and timber columns supporting overlapping ETFE cushion canopy panels. Three hexagonal landing pads and central glass-pod passenger pavilion with curved timber ribs. Integrated solar cells give ETFE a blue-green shimmer. Living green walls on columns. eVTOL lifting off over decorative water feature. Waterfront park setting with city towers behind.",
            "Photorealistic 8K architectural rendering, aerial three-quarter angle view, golden hour warm light. A multi-modal transit hub with vertiport on elevated deck above rail station and bus terminal. Bold undulating Corten steel perforated roof spanning entire complex. Two TLOF pads with LED guidance on upper level. Glass-enclosed escalators. Light rail train at platform below. Polished terrazzo floors and digital wayfinding totems. Corten rust-orange patina glowing in golden light. Green roof sections with sedum.",
        ],
    },
    {
        "dir": "shophouse_southeast_asian",
        "prompts": [
            "Photorealistic 8K architectural rendering, aerial three-quarter angle view, golden hour warm light. A row of five lavishly decorated Peranakan shophouses in vibrant pastels -- turquoise, coral pink, saffron yellow, mint green, lavender. Elaborate plasterwork with phoenix and peony motifs. Peranakan ceramic tiles in cobalt blue, emerald, gold. French louvered shutters. Five-foot-way arcade with mosaic tile flooring. Pintu pagar half-doors in dark carved timber. Terracotta Chinese pantile roofs. Tropical plants on balconies. Narrow street with pedestrians and trishaw.",
            "Photorealistic 8K architectural rendering, aerial three-quarter angle view, golden hour warm light. Six traditional Southern Chinese-style shophouses with restrained facades in cream, warm ochre, pale terracotta. Timber-framed windows with dark hardwood shutters. Carved air vents with Chinese fretwork. Five-foot-way arcade with plain masonry columns. Clay tile roofs. Chinese signage in gold and red on wooden boards. Open-front shops displaying wares. Laundry on bamboo poles. Bicycle against wall. Rain trees providing dappled shade.",
            "Photorealistic 8K architectural rendering, aerial three-quarter angle view, golden hour warm light. Four heritage shophouses renovated into boutique hotel and design studios. Original ornate Peranakan facades in dusty rose and sage green preserved. Rear portions rebuilt with blackened steel frames, floor-to-ceiling glass, board-formed concrete. Rooftop plunge pool and tropical garden set back from street facade. Modern pendant lighting through ground-floor glass. Restored encaustic cement tiles in five-foot-way. Courtyard with ferns, water feature, frangipani tree.",
            "Photorealistic 8K architectural rendering, aerial three-quarter angle view, golden hour warm light. A contemporary mixed-use building reinterpreting shophouse typology. Three stories with narrow-and-deep proportions and five-foot-way arcade. Terracotta baguette louvers and perforated brass screens with abstracted Peranakan patterns. Each unit in different glazed terracotta -- deep indigo, warm amber, celadon green, dusty coral. Open-fronted artisan food stalls. Deep recessed balconies with trailing plants. Central linear atrium with living wall of tropical ferns. Tropical urban street with angsana trees.",
        ],
    },
    {
        "dir": "food_hall_market_hall",
        "prompts": [
            "Photorealistic 8K architectural rendering, aerial three-quarter angle view, golden hour warm light. A restored 19th-century market hall with exposed wrought-iron framework painted heritage green, supporting a soaring barrel-vaulted glass roof. Cast-iron Corinthian columns. Clerestory windows with decorative tracery. Timber-and-brass food stalls with hand-painted signage, hanging copper pendants, marble countertops. Herringbone brick flooring. Mezzanine gallery with wrought-iron railings. People dining at communal wooden tables. Red brick exterior with stone quoins on cobblestone square.",
            "Photorealistic 8K architectural rendering, aerial three-quarter angle view, golden hour warm light. A bold contemporary market hall with monumental arch in natural grey limestone. Open ends with massive cable-net glass facades. Inside the arch, a spectacular digital artwork of oversized fruits and flowers in hyper-saturated colors on the ceiling. Apartments in the arch with windows facing outward. 100 food stalls with sleek white counters and terrazzo. Communal timber tables. Public plaza with water features and young trees.",
            "Photorealistic 8K architectural rendering, aerial three-quarter angle view, golden hour warm light. A former rail warehouse transformed into a food hall. Sawtooth roof with north-facing clerestory glass. Exposed steel trusses painted matte black with warm timber insertions. Brick walls with preserved ghost lettering. Food stalls in reclaimed shipping containers and raw steel frames. Central area with vintage furniture, potted olive trees, festoon string lights. Loading dock doors open to beer garden with picnic tables. Rail tracks in polished concrete floor.",
            "Photorealistic 8K architectural rendering, aerial three-quarter angle view, golden hour warm light. An elegant open-air market pavilion with sweeping undulating timber-and-steel canopy resembling rolling green hills. Glulam timber beams in flowing organic form, covered with living green roof of sedum and wildflowers with skylights. Open on all sides, slender tapered steel columns. Radial vendor stalls with canvas awnings around central fountain. Families shopping. Park with mature trees and community garden adjacent.",
        ],
    },
    {
        "dir": "ev_charging_hub",
        "prompts": [
            "Photorealistic 8K architectural rendering, aerial three-quarter angle view, golden hour warm light. An elegant EV charging station with sweeping cantilevered bifacial solar panel canopy on slender angled white steel columns. 12 charging bays in gentle curve with flush LED guidance strips in soft blue. Semi-transparent blue-black photovoltaic surfaces creating dappled shadows. Central battery storage in sculptural Corten steel enclosure. Minimalist aluminum charging pedestals. Permeable pavers with rain gardens. Covered waiting shelter with curved glass and timber bench. Highway rest area with distant hills.",
            "Photorealistic 8K architectural rendering, aerial three-quarter angle view, golden hour warm light. A neighborhood mobility hub with dramatic butterfly zinc roof with integrated thin-film solar. Cafe wing with floor-to-ceiling glass and exposed timber beams, terrace under plane trees. Other wing sheltering 8 EV bays and e-bike docking. Living green wall on one side. Warm timber cladding contrasting with cool zinc. Small playground. Residential neighborhood with tree-lined streets.",
            "Photorealistic 8K architectural rendering, aerial three-quarter angle view, golden hour warm light. A reimagined highway rest stop as a grove of 12 tree-like CLT timber structures branching into ETFE membrane and solar canopies. Each tree-canopy shelters two fast-charging bays. Native wildflowers and grasses between columns. Central lounge pavilion with curved glass, coffee bar. Children's natural timber playground. Electric cables retracting from tree columns. Open countryside with green fields and distant wind turbines.",
            "Photorealistic 8K architectural rendering, aerial three-quarter angle view, golden hour warm light. An urban charging garden on a former gas station site. Six charging posts around a central garden with raised recycled-brick planters, ornamental grasses, flowering perennials, fruit trees. Triangular steel frames with terracotta and cream canvas shade sails. Kinetic wind sculpture in brushed stainless steel. Permeable grass pavers. Bicycle repair station. Free library box. Dense urban neighborhood with four-story brick apartments. Neighbors chatting on bench while cars charge.",
        ],
    },
    {
        "dir": "hyperscale_data_center",
        "prompts": [
            "Photorealistic 8K architectural rendering, aerial three-quarter angle view, golden hour warm light. A hyperscale data center campus with four identical low-rise buildings in pinwheel pattern around central landscaped courtyard with prairie meadow, walking trails, and curved timber gathering pavilion. Light grey precast concrete panels with dark bronze aluminum ventilation louvers. Sedum green roofs and rooftop solar arrays. Central cooling towers screened by perforated Corten panels. Bioswale rain gardens. Security gatehouse. Restored native grassland with mature oaks.",
            "Photorealistic 8K architectural rendering, aerial three-quarter angle view, golden hour warm light. An 8-story urban data center blending into a city block. Facade of alternating vertical fins in charcoal grey and warm bronze glazed terracotta evoking a microchip circuit board pattern. Ground-floor retail arcade with cafe, co-working, and digital art gallery. Rooftop terrace with intensive landscaping. No visible signage indicating data center function. Street-level pedestrians, street trees, transit stops. Contextual urban architecture.",
            "Photorealistic 8K architectural rendering, aerial three-quarter angle view, golden hour warm light. A sustainable data center on a Nordic fjord shore, converted from a former paper mill. Original massive brick and concrete structure preserved with new CLT timber additions in warm honey color. Large exposed steel pipes in RAL signal blue carrying seawater cooling. District heating exchange building exporting waste heat. Visitor education center in glass-and-timber pavilion. Rocky shoreline with birch and pine. Snow-capped mountains reflected in calm fjord. Living green walls of mosses and ferns.",
            "Photorealistic 8K architectural rendering, aerial three-quarter angle view, golden hour warm light. A next-generation modular data center in a dynamic circular ring formation 200m diameter, three stories. Open courtyard with reflective pool and sculptural landscape. Prefabricated pods in alternating silver and dark graphite corrugated aluminum. Color-coded piping (blue water, green coolant). Continuous clerestory glass band. Rooftop air-cooled heat exchangers with aerodynamic cowlings. Cable-mesh green walls with climbing jasmine. Flat arid landscape with photovoltaic arrays extending to horizon.",
        ],
    },
    {
        "dir": "vertical_farm",
        "prompts": [
            "Photorealistic 8K architectural rendering, aerial three-quarter angle view, golden hour warm light. A 30-story vertical farm tower with fully glazed facade in slender white steel diagrid. Each floor visible as a lush horizontal layer of hydroponic trays -- leafy greens, herbs, strawberries in gradient from pale seedlings to deep emerald. Robotic arms on ceiling rails. South-facing panels angled outward 15 degrees creating faceted profile. Ground floor farmers market and restaurant. Rooftop observation deck with beehives. Adjacent community garden plots. Mist catching golden light inside. Building glows green and gold at sunset.",
            "Photorealistic 8K architectural rendering, aerial three-quarter angle view, golden hour warm light. A six-story indoor vertical farm with opaque matte charcoal fiber-cement rainscreen. Narrow horizontal slot windows emitting distinctive pink-purple LED grow-light glow at dusk. Clean rectangular form with rounded corners. Rooftop solar panels and stainless steel rainwater cisterns. Double-height ground floor with glass frontage: retail farm shop, juice bar, viewing window into growing floors showing vertical towers bathed in magenta LED. Delivery trucks at dock. Pollinator gardens at perimeter.",
            "Photorealistic 8K architectural rendering, aerial three-quarter angle view, golden hour warm light. A 50-story mixed-use farmscraper with CLT timber structure showing honey-colored wood beams at floor edges. Dynamic rotating glass louver facade optimizing sunlight for crops. Every fifth floor a full greenhouse level. Terraced south-facing platforms with outdoor greenhouse pods. Food court and public market on first three floors. Rooftop restaurant with panoramic views and productive garden. Warm timber contrasting with crystalline glass farming bands. Dense Asian megacity skyline.",
            "Photorealistic 8K architectural rendering, aerial three-quarter angle view, golden hour warm light. Sprawling rooftop greenhouse complex atop a converted four-story red brick warehouse. Three interconnected peaked glass-and-aluminum ridge-and-furrow greenhouses. Hydroponic NFT channels and vertical towers with tomatoes, peppers, herbs under supplemental LED. Automated climate vents releasing warm humid air. PV canopy over rooftop courtyard. Galvanized rainwater tanks at corners feeding irrigation. Freight elevator shaft with living-wall facade. Ground-floor farm shop. Urban neighborhood with rowhouses. Glass greenhouses glow amber-green at sunset.",
        ],
    },
]


def generate_image(client: httpx.Client, api_key: str, prompt: str) -> bytes:
    """Call Gemini API and return raw PNG bytes."""
    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseModalities": ["TEXT", "IMAGE"],
            "temperature": 0.0,
        },
    }
    resp = client.post(
        ENDPOINT,
        params={"key": api_key},
        json=body,
        timeout=120.0,
    )
    resp.raise_for_status()
    data = resp.json()

    # Find the part with inlineData
    for candidate in data.get("candidates", []):
        for part in candidate.get("content", {}).get("parts", []):
            if "inlineData" in part:
                b64 = part["inlineData"]["data"]
                return base64.b64decode(b64)

    raise RuntimeError(f"No image data in response: {json.dumps(data)[:500]}")


def main():
    api_key = load_api_key()
    total = sum(len(a["prompts"]) for a in ARCHETYPES)
    done = 0

    client = httpx.Client()
    try:
        for arch in ARCHETYPES:
            dir_path = _ARCHETYPES_DIR / arch["dir"]
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"\n=== {arch['dir']} ===")

            for vi, prompt in enumerate(arch["prompts"]):
                variant_file = dir_path / f"variant_{vi}.png"
                if variant_file.exists():
                    print(f"  variant_{vi}.png already exists, skipping")
                    done += 1
                    continue

                print(f"  Generating variant_{vi}.png ... ", end="", flush=True)
                try:
                    img_bytes = generate_image(client, api_key, prompt)
                    variant_file.write_bytes(img_bytes)
                    print(f"OK ({len(img_bytes)} bytes)")
                except Exception as e:
                    print(f"FAILED: {e}")
                    done += 1
                    if done < total:
                        time.sleep(WAIT_SECONDS)
                    continue

                done += 1
                if done < total:
                    print(f"  Waiting {WAIT_SECONDS}s ... ({done}/{total})")
                    time.sleep(WAIT_SECONDS)

            # Copy variant_0 as hero
            v0 = dir_path / "variant_0.png"
            hero = dir_path / "hero.png"
            if v0.exists() and not hero.exists():
                shutil.copy2(v0, hero)
                print(f"  Copied variant_0.png -> hero.png")
            elif v0.exists():
                shutil.copy2(v0, hero)
                print(f"  Updated hero.png from variant_0.png")

    finally:
        client.close()

    print(f"\nDone! Generated {done}/{total} images.")


if __name__ == "__main__":
    main()
