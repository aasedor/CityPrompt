"""
Generate 6 new building archetype images (4 variants each = 24 total)
using Gemini 3 Pro image generation.

Archetypes:
  1. waste_to_energy_plant
  2. senior_living_complex
  3. brewery_distillery
  4. solar_farm_agrivoltaics
  5. immersive_experience_venue
  6. modern_fire_station
"""

from __future__ import annotations

import base64
import io
import shutil
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
_BASE_OUT = _PROJECT_ROOT / "frontend" / "public" / "archetypes" / "buildings"

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
# All archetypes and their variant prompts
# ---------------------------------------------------------------------------

ARCHETYPES = [
    {
        "dir": "waste_to_energy_plant",
        "variants": [
            {
                "label": "Ski Slope WtE",
                "filename": "variant_0.png",
                "prompt": (
                    "Photorealistic 8K architectural rendering, aerial three-quarter angle view, golden hour warm light. "
                    "A monumental waste-to-energy plant with dramatically sloping rooftop forming a 400-meter artificial ski slope "
                    "covered in bright green synthetic turf with tiny figures skiing and hiking. Brushed-aluminum brick facade with "
                    "rhythmic gaps allowing warm interior light to glow through. 85-meter climbing wall with colored handholds on "
                    "longest vertical face. Rooftop bar terrace with string lights at summit. Waterfront industrial district with "
                    "cargo ships. Clean white steam from sculptural chimney. Wildflower meadows on flat roof sections."
                ),
            },
            {
                "label": "Hillside WtE",
                "filename": "variant_1.png",
                "prompt": (
                    "Photorealistic 8K architectural rendering, aerial three-quarter angle view, golden hour warm light. "
                    "A waste-to-energy plant disappearing into rolling green hills, entire roof covered in native grasses, "
                    "wildflowers, and walking paths merging with surrounding meadow. Only curved glass curtain walls visible "
                    "at entrance revealing industrial machinery. Single elegant tapered concrete chimney rising organically "
                    "from grassy mounds. Undulating green roof with sculpted berms and rainwater pools reflecting golden sky. "
                    "Solar panels on south-facing slopes. Visitors on meandering paths. Sheep grazing on adjacent hillsides. "
                    "Northern European pastoral landscape with distant wind turbines."
                ),
            },
            {
                "label": "Mosaic WtE",
                "filename": "variant_2.png",
                "prompt": (
                    "Photorealistic 8K architectural rendering, aerial three-quarter angle view, golden hour warm light. "
                    "A waste-to-energy facility with spectacular 100-meter sculptural chimney adorned with colorful mosaic "
                    "tiles in deep blue, gold, crimson, emerald in organic Hundertwasser patterns. Massive golden sphere atop "
                    "chimney. Playful asymmetric windows in white stucco walls with ceramic tile patches. Rooftop gardens with "
                    "small trees. European river setting with historic stone bridges. Wrought-iron railings with organic forms. "
                    "Whimsical art palace atmosphere. Pedestrians on riverbank promenade."
                ),
            },
            {
                "label": "Transparent WtE",
                "filename": "variant_3.png",
                "prompt": (
                    "Photorealistic 8K architectural rendering, aerial three-quarter angle view, golden hour warm light. "
                    "A cutting-edge waste-to-energy plant with large sections of floor-to-ceiling structural glass revealing "
                    "gleaming stainless steel furnaces and turbines within. Perforated Corten steel facade with thousands of "
                    "laser-cut circular openings glowing warm orange from interior lighting. Cantilevered glass-bottomed "
                    "observation bridge over main process hall. Adjacent CLT timber visitor center with skylights. Educational "
                    "garden paths with interpretive signage. Suburban setting with schools and parks nearby. Children on "
                    "observation deck."
                ),
            },
        ],
    },
    {
        "dir": "senior_living_complex",
        "variants": [
            {
                "label": "Garden Courtyard",
                "filename": "variant_0.png",
                "prompt": (
                    "Photorealistic 8K architectural rendering, aerial three-quarter angle view, golden hour warm light. "
                    "A senior living community of intimate 2-3 story buildings around interconnected garden courtyards. One "
                    "courtyard with central fountain and rose gardens, another with raised vegetable beds, a third with covered "
                    "pergola and outdoor dining. Warm brick facades with large windows, Juliet balconies, pitched copper roofs "
                    "with dormers. Covered colonnades with arched openings connecting buildings. Central community pavilion with "
                    "glass conservatory. Meandering brick pathways with benches and bird baths. Elderly residents tending "
                    "gardens. Leafy suburban neighborhood with mature oaks. Dappled golden light."
                ),
            },
            {
                "label": "Urban Tower",
                "filename": "variant_1.png",
                "prompt": (
                    "Photorealistic 8K architectural rendering, aerial three-quarter angle view, golden hour warm light. "
                    "A sleek 12-story senior living tower with sculptural curving form in warm champagne-toned metal panels "
                    "and floor-to-ceiling glass. Cantilevered balconies overflowing with trailing greenery and small trees "
                    "cascading down the building face. Rooftop wellness terrace with lap pool, yoga pavilion, meditation "
                    "garden with Japanese maples. Ground-level public plaza with cafe and water features. Separate wellness "
                    "center with curved timber-lattice facade connected by glass sky bridge. Residents exercising on rooftop. "
                    "Urban neighborhood with transit and park across street."
                ),
            },
            {
                "label": "Timber Cohousing",
                "filename": "variant_2.png",
                "prompt": (
                    "Photorealistic 8K architectural rendering, aerial three-quarter angle view, golden hour warm light. "
                    "A senior cohousing community built entirely of CLT in pale natural wood and dark shou sugi ban charred "
                    "timber. Cluster of 3-4 story timber buildings with steeply pitched roofs and deep overhanging eaves "
                    "connected by covered wooden walkways. Double-height communal windows with exposed timber beams. Central "
                    "courtyard with shared kitchen garden, outdoor wood-fired oven, communal dining pavilion, shallow reflecting "
                    "pool. Green sedum roofs blending with forested hillside. Ground-floor apartments with private timber-deck "
                    "patios. Elderly residents sharing meal under pavilion. Scandinavian coastal landscape with pine forest and "
                    "granite outcrops."
                ),
            },
            {
                "label": "Mediterranean Resort",
                "filename": "variant_3.png",
                "prompt": (
                    "Photorealistic 8K architectural rendering, aerial three-quarter angle view, golden hour warm light. "
                    "A luxurious senior living resort in Mediterranean revival style. White stucco walls, terracotta barrel-tile "
                    "roofs, wrought-iron balcony railings. Buildings 2-4 stories in U-shape around turquoise swimming pool with "
                    "fountain, palm trees, bougainvillea pergolas, covered outdoor dining terrace. Arched colonnades with stone "
                    "columns. Bell tower with clock. Mediterranean cypress, olive trees, lavender borders, citrus groves. Bocce "
                    "court and putting green. Residents lounging by pool and dining under pergola. Rolling hills, distant ocean "
                    "views, golden sunset."
                ),
            },
        ],
    },
    {
        "dir": "brewery_distillery",
        "variants": [
            {
                "label": "Highland Distillery",
                "filename": "variant_0.png",
                "prompt": (
                    "Photorealistic 8K architectural rendering, aerial three-quarter angle view, golden hour warm light. "
                    "A luxury whisky distillery concealed beneath an undulating green roof of thousands of interlocking timber "
                    "beams forming rolling grass, heather, and wildflower landscape merging with Scottish Highlands terrain. "
                    "Complex timber gridshell of pale Scandinavian spruce visible through large glass curtain walls. Gleaming "
                    "copper pot stills 6 meters tall reflecting warm amber light inside. Visitor arrival court with low stone "
                    "wall and gravel paths. Building stretches 120 meters. Sheep grazing on green roof. Stream along glass "
                    "wall base. Rolling emerald hills with stone walls and distant purple mountains."
                ),
            },
            {
                "label": "Canal Brewery",
                "filename": "variant_1.png",
                "prompt": (
                    "Photorealistic 8K architectural rendering, aerial three-quarter angle view, golden hour warm light. "
                    "A craft brewery in a converted 19th-century brick warehouse along a canal. Original red-brown brick "
                    "preserved with Corten steel, glass curtain walls, exposed steel framing. Two-story glass addition "
                    "extending over canal with taproom and glass floor. Tall arched windows revealing stainless steel "
                    "fermentation tanks. Rooftop beer garden with string lights, hop vine trellises, reclaimed timber "
                    "furniture. Preserved brick chimney wrapped in neon signage. Cobblestone courtyard with outdoor seating, "
                    "food trucks, live music stage. Revitalized industrial waterfront. Golden sunset reflecting in canal water."
                ),
            },
            {
                "label": "Crystal Brewhouse",
                "filename": "variant_2.png",
                "prompt": (
                    "Photorealistic 8K architectural rendering, aerial three-quarter angle view, golden hour warm light. "
                    "A state-of-the-art craft brewery with soaring glass-and-steel brewhouse pavilion, faceted crystalline "
                    "roof of triangulated steel beams and glass panels. Polished copper kettles and stainless tanks visible "
                    "through transparent enclosure. Long low production wing with standing-seam zinc roof. Cantilevered glass "
                    "taproom with panoramic views of hop fields and mountains. Reflecting pool mirroring crystalline structure. "
                    "Outdoor terraces at multiple levels. PV panels on south-facing roof. Board-formed concrete base walls. "
                    "Agricultural fields and distant mountains."
                ),
            },
            {
                "label": "Farmstead Brewery",
                "filename": "variant_3.png",
                "prompt": (
                    "Photorealistic 8K architectural rendering, aerial three-quarter angle view, golden hour warm light. "
                    "A farmstead brewery as agricultural compound of connected barn-like structures. Gambrel roofs in weathered "
                    "cedar shingles and vertical board-and-batten in natural gray. Main barn with massive sliding door revealing "
                    "copper brewing vessels. Stone-and-timber tasting room in renovated 1850s dairy barn with hand-hewn beams. "
                    "Hop bines climbing tall cedar poles in adjacent fields. Malting floor with conical-roofed kiln tower. "
                    "Farmhouse beer garden with reclaimed wood tables under apple trees strung with Edison bulbs. Grain silos "
                    "converted to fermentation vessels. Creek with stone bridge. Rolling farmland with split-rail fences."
                ),
            },
        ],
    },
    {
        "dir": "solar_farm_agrivoltaics",
        "variants": [
            {
                "label": "Desert Solar Farm",
                "filename": "variant_0.png",
                "prompt": (
                    "Photorealistic 8K architectural rendering, aerial three-quarter angle view, golden hour warm light. "
                    "A vast utility-scale solar farm on rolling desert terrain with thousands of single-axis tracking PV panels "
                    "in precise parallel rows tilted toward low golden sun. Dark blue-black crystalline silicon creating "
                    "mesmerizing geometric pattern to horizon. Central operations building with communications array. Electrical "
                    "substation with transformers and transmission lines. Desert sagebrush, rocky outcrops, distant mesa "
                    "formations in warm ochre. Panels casting long parallel shadows. Perimeter fence. Maintenance workers "
                    "inspecting panels. Golden sunset creating shimmering sea of warm reflections across thousands of panels."
                ),
            },
            {
                "label": "Agrivoltaic Farm",
                "filename": "variant_1.png",
                "prompt": (
                    "Photorealistic 8K architectural rendering, aerial three-quarter angle view, golden hour warm light. "
                    "An agrivoltaic farm with semi-transparent bifacial solar panels elevated 4-5 meters above actively farmed "
                    "cropland on slender white steel columns. Dappled light canopy over leafy vegetables, berry bushes, herb "
                    "gardens below. Motorized tilting brackets. Small tractor and farm workers harvesting into wooden crates. "
                    "Elegant minimal structure with cable-stayed cross-bracing. Timber-and-glass farm stand with green roof at "
                    "entrance. Drip irrigation and rainwater swales. Lush agricultural valley with patchwork fields, hedgerows, "
                    "distant village with church steeple."
                ),
            },
            {
                "label": "Floating Solar",
                "filename": "variant_2.png",
                "prompt": (
                    "Photorealistic 8K architectural rendering, aerial three-quarter angle view, golden hour warm light. "
                    "A floating solar farm of thousands of PV panels on white HDPE pontoon platforms in geometric island "
                    "formation on a calm reservoir. Rectangular blocks with maintenance walkway gratings between sections. "
                    "Mooring cables to shore anchors. Array covers 60% of water surface. Onshore inverter station in timber-clad "
                    "building. Floating maintenance dock with electric boat. Dark water contrasting with blue-black panels "
                    "catching golden reflections. Waterfowl in channels between panel blocks. Green hills with deciduous forest. "
                    "Small dam with spillway. Golden sky reflecting off water and tilted panel faces."
                ),
            },
            {
                "label": "CSP Tower",
                "filename": "variant_3.png",
                "prompt": (
                    "Photorealistic 8K architectural rendering, aerial three-quarter angle view, golden hour warm light. "
                    "A concentrated solar power plant in flat desert with a gleaming white concrete tower 200 meters tall, "
                    "receiver glowing intensely bright white-orange at top where thousands of reflected sunbeams converge. Over "
                    "10,000 billboard-sized heliostats in precise radial concentric rings extending nearly a kilometer. Mirrors "
                    "nearest tower tilted steeply, farther ones more gently. Hypnotic spiral pattern of silver mirrors and sand. "
                    "Molten salt storage tanks and turbine hall at base. Maintenance roads radiating like spokes. Flat desert to "
                    "distant mountain ranges in purple-blue haze. Thousands of mirrors creating sea of golden reflections."
                ),
            },
        ],
    },
    {
        "dir": "immersive_experience_venue",
        "variants": [
            {
                "label": "Industrial Portal",
                "filename": "variant_0.png",
                "prompt": (
                    "Photorealistic 8K architectural rendering, aerial three-quarter angle view, golden hour warm light. "
                    "A massive converted industrial warehouse as immersive art venue. Raw concrete-and-steel structure preserved "
                    "with sawtooth skylights. A giant iridescent sculptural portal bursting through the roof in faceted mirrored "
                    "panels and neon-lit geometric forms. Facade sections replaced with backlit translucent panels pulsing "
                    "magenta, cyan, violet. Monumental entry portal of surreal organic fiberglass archway -- swirling tentacles, "
                    "oversized mushrooms, crystalline formations. Painted asphalt murals and interactive light installations. "
                    "Food trucks and outdoor stage. Industrial district with elevated highway ramps. Lines of excited visitors. "
                    "Raw concrete catching golden light while iridescent sculpture shimmers rainbow."
                ),
            },
            {
                "label": "Geodesic Dome",
                "filename": "variant_1.png",
                "prompt": (
                    "Photorealistic 8K architectural rendering, aerial three-quarter angle view, golden hour warm light. "
                    "A purpose-built immersive venue featuring a massive 60-meter geodesic dome with ETFE cushion skin shifting "
                    "from transparent to opaque, currently glowing deep indigo and magenta. Low circular black concrete base "
                    "with continuous glass band revealing dark cavernous interior lit by projected light. Secondary smaller dome "
                    "connected via glass tunnel housing cafe. Sunken courtyard with black reflecting pool mirroring dome. Black "
                    "gravel ground plane, boulders, ornamental grasses. ETFE panels glowing warmly. Transparent triangles "
                    "revealing projected light inside. Waterfront site with calm ocean reflecting dome's glow."
                ),
            },
            {
                "label": "Mirror Droplet",
                "filename": "variant_2.png",
                "prompt": (
                    "Photorealistic 8K architectural rendering, aerial three-quarter angle view, golden hour warm light. "
                    "An immersive venue entirely clad in polished stainless steel mirror panels reflecting and distorting "
                    "surrounding cityscape in kaleidoscopic effect. Fluid amorphous form -- no flat surfaces or right angles "
                    "-- resembling a melted metallic droplet 40 meters tall, 80 meters long. Dark rectangular openings with "
                    "LED strip edges in warm amber. Sunken entry plaza with broad stairs. Polished black granite paving "
                    "extending reflective quality to ground. People photographing distorted reflections. Contemporary urban "
                    "district with glass towers. Golden hour transforms mirror facade into blazing golden sculpture reflecting "
                    "clouds and sunset in warped dreamlike distortions."
                ),
            },
            {
                "label": "Underground Venue",
                "filename": "variant_3.png",
                "prompt": (
                    "Photorealistic 8K architectural rendering, aerial three-quarter angle view, golden hour warm light. "
                    "An immersive venue built entirely underground, visible as dramatic circular skylights cut into a public "
                    "park, each emitting different colored light -- deep blue, violet, warm amber, emerald -- from galleries "
                    "below. Main entrance a sweeping concrete ramp spiraling down through 20-meter opening, board-formed walls "
                    "embedded with fiber-optic starfield points. Sculpted grass mounds over buried structure. Ventilation shafts "
                    "as bronze sculptural totems. Glass-floored viewing platforms to peer into swirling projections below. "
                    "Reflecting pool above main exhibition hall. Dense urban context with apartment buildings. Golden sunset "
                    "light on grass mounds while colored light from below creates otherworldly glow."
                ),
            },
        ],
    },
    {
        "dir": "modern_fire_station",
        "variants": [
            {
                "label": "Deconstructivist",
                "filename": "variant_0.png",
                "prompt": (
                    "Photorealistic 8K architectural rendering, aerial three-quarter angle view, golden hour warm light. "
                    "A fire station as bold deconstructivist sculpture in raw exposed concrete. Dramatically angled walls "
                    "leaning, tilting, slicing through space at sharp diagonals with no right angles. Long thin concrete planes "
                    "extending outward like frozen explosion shards. Three apparatus bays with red-painted steel frames between "
                    "angular concrete planes. Tall angular concrete hose-drying tower with narrow slit window. Board-formed "
                    "concrete with visible wood grain. Small windows punched at unexpected angles. Paved concrete apron with "
                    "dramatic geometric shadows. European institutional campus setting. Intense golden light-and-shadow "
                    "contrasts accentuating every angular plane."
                ),
            },
            {
                "label": "Mass Timber",
                "filename": "variant_1.png",
                "prompt": (
                    "Photorealistic 8K architectural rendering, aerial three-quarter angle view, golden hour warm light. "
                    "A modern fire station in CLT and mass timber with warm honey-toned wood visible as deep overhanging eaves, "
                    "exposed beam ends, timber-clad upper floors. Lower apparatus bay in board-formed concrete with three "
                    "glass-paneled overhead doors revealing red fire engines. Upper living quarters with floor-to-ceiling "
                    "windows. Extensive green roof garden with native grasses, sedum, wildflowers, small trees in naturalistic "
                    "meadow. Private ipe terraces extending into green roof. Shou sugi ban charred timber accent panels. "
                    "Training tower in charred timber. Solar panels on south-facing roof. Welcoming residential scale. "
                    "Suburban neighborhood with mature trees and community park."
                ),
            },
            {
                "label": "Cantilevered Modern",
                "filename": "variant_2.png",
                "prompt": (
                    "Photorealistic 8K architectural rendering, aerial three-quarter angle view, golden hour warm light. "
                    "A striking modern fire station with bold cantilevered second floor extending 10 meters beyond ground "
                    "level, clad in perforated anodized aluminum in deep red-bronze finish. Ground floor transparent -- "
                    "floor-to-ceiling glass revealing three gleaming red fire engines and polished concrete. Corner clock tower "
                    "in glass and steel rising 25 meters. Flat roofs, crisp edges. Public plaza with memorial wall, flagpole. "
                    "LED strip outlining cantilever edge. Mixed-use urban neighborhood with retail, apartments, transit stop. "
                    "Golden light reflecting off glass apparatus bay showcasing engines."
                ),
            },
            {
                "label": "Craftsman Neighborhood",
                "filename": "variant_3.png",
                "prompt": (
                    "Photorealistic 8K architectural rendering, aerial three-quarter angle view, golden hour warm light. "
                    "A fire station blending with residential neighborhood. Warm red-brown brick, painted wood trim, "
                    "standing-seam charcoal metal roof, covered front porch with timber columns. Apparatus bay set back with "
                    "wood-paneled overhead doors referencing barn aesthetics. Crew quarters above like a large craftsman home "
                    "with gabled dormers, divided-lite windows, flower boxes. Community room with stone fireplace facing "
                    "street. Memorial garden with bronze firefighter statue and flagstone paths. Traditional brick hose tower "
                    "with copper cupola. Kitchen garden and basketball court behind fence. Tree-lined residential street with "
                    "craftsman bungalows. Evening light making station glow like a welcoming home."
                ),
            },
        ],
    },
]

# ---------------------------------------------------------------------------
# Image generation helpers
# ---------------------------------------------------------------------------


def generate_image(prompt: str) -> bytes | None:
    """Call Gemini API and return PNG bytes."""
    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseModalities": ["TEXT", "IMAGE"],
            "temperature": 0.0,
        },
    }

    print(f"  -> Calling Gemini API ({len(prompt)} chars)...")
    resp = httpx.post(API_URL, json=body, timeout=120.0)

    if resp.status_code != 200:
        print(f"  X API error {resp.status_code}: {resp.text[:300]}")
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


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    total_generated = 0
    total_skipped = 0

    for arch in ARCHETYPES:
        out_dir = _BASE_OUT / arch["dir"]
        out_dir.mkdir(parents=True, exist_ok=True)

        print(f"\n{'='*60}")
        print(f"Archetype: {arch['dir']}")
        print(f"Output:    {out_dir}")
        print(f"{'='*60}")

        for i, variant in enumerate(arch["variants"]):
            filename = variant["filename"]
            filepath = out_dir / filename

            if filepath.exists():
                print(f"  [{i}] {variant['label']} -- already exists, skipping")
                total_skipped += 1
                continue

            print(f"  [{i}] Generating {variant['label']}...")
            img_bytes = generate_image(variant["prompt"])

            if img_bytes:
                cropped = resize_and_crop(img_bytes, CARD_WIDTH, CARD_HEIGHT)
                filepath.write_bytes(cropped)
                print(f"  OK Saved {filepath.name} ({len(cropped):,} bytes)")
                total_generated += 1
            else:
                print(f"  X Failed to generate {variant['label']}")

            # Rate limit -- 8 seconds between requests
            print("  .. Waiting 8s for rate limit...")
            time.sleep(8)

        # Copy variant_0 as hero.png
        v0 = out_dir / "variant_0.png"
        hero = out_dir / "hero.png"
        if v0.exists() and not hero.exists():
            shutil.copy2(v0, hero)
            print(f"  OK Copied variant_0.png -> hero.png")

    print(f"\n{'='*60}")
    print(f"Done! Generated: {total_generated}, Skipped: {total_skipped}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
