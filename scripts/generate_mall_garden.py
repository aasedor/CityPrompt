#!/usr/bin/env python3
"""Generate archetype images for Mall Redevelopment and Community Garden Enhanced
using Gemini 3 Pro image generation API."""

import base64
import os
import shutil
import time

import httpx

# --- Config ---
ENV_PATH = os.path.join(os.path.dirname(__file__), "..", "backend", ".env")
BASE_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend", "public", "archetypes")
MODEL = "gemini-3-pro-image-preview"
ENDPOINT = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"
DELAY = 8  # seconds between requests


def load_api_key() -> str:
    with open(ENV_PATH) as f:
        for line in f:
            if line.startswith("GEMINI_API_KEY="):
                return line.strip().split("=", 1)[1]
    raise RuntimeError("GEMINI_API_KEY not found in backend/.env")


PROMPTS = {
    "buildings/mall_redevelopment": [
        # variant_0 — New Town Center
        "Photorealistic aerial 3/4 angle view of a walkable mixed-use town center built on a former suburban mall site, golden hour warm light, 8K resolution. A 22-block orthogonal street grid with 3-5 story buildings pulled to the street edge. Buildings have varied facades of red brick, cream-painted clapboard, and natural stone bases with large glass storefronts at street level. Tree-lined boulevards with honey locust and red maple canopy, diagonal on-street parking. Central town square with buff sandstone pavers, a circular fountain, cafe seating under market umbrellas. Pocket parks with green lawns between blocks. Wrapped parking garages with rooftop solar panels. Pedestrians on wide sidewalks. Surrounding suburban context visible at edges. Warm golden hour shadows casting long across the streets.",
        # variant_1 — Open-Air Retrofit
        "Photorealistic aerial 3/4 angle view of a retrofitted suburban shopping mall with sections of roof removed to create open-air pedestrian paseos, golden hour lighting, 8K resolution. The original mall footprint is a large rectangular mass with two parallel linear cuts revealing tree-lined walkways inside the former building. Exposed concrete frame painted warm white with matte black steel trusses visible. Former anchor stores re-clad with charcoal perforated aluminum panels, cedar wood-slat rain screens, and floor-to-ceiling curtain wall glass. Living green walls of ferns and jasmine on cut-edge walls. Crape myrtle trees growing in corten steel planters within the paseos. White fabric shade sails stretched between walls above. Polished concrete ground plane with corten steel drainage channels. Rooftop green roofs with sedum and solar canopies. Surrounding area has 4-6 story apartment buildings replacing former parking lots. A public event lawn with string lights at the main entrance.",
        # variant_2 — Community Campus
        "Photorealistic aerial 3/4 angle view of a former suburban shopping mall converted into a community campus with healthcare clinic, community college, library, and recreation center, golden hour lighting, 8K resolution. Large single-footprint building with warm off-white and light gray stucco walls, terracotta-colored fiber cement accent bands at entries. Angled steel entry canopies with translucent polycarbonate roofing at each institutional entrance. A new glass-enclosed atrium lobby projecting from the main facade with visible interior greenery. Half the former parking lot replaced by a 2-acre community park with a mowed walking loop trail through native grass meadow, clusters of mature oak and elm shade trees, a bioswale rain garden with river stone and native grasses, and a timber-and-rope playground. Decomposed granite walking paths with steel edging. A parking garage wrapped in light-gray precast with trailing ivy in vertical planting pockets. Rooftop skylights visible. Warm golden hour light, families using the park.",
        # variant_3 — Green Grid Eco-District
        "Photorealistic aerial 3/4 angle view of an eco-district built on a former suburban mall site, golden hour warm lighting, 8K resolution. A sinuous daylighted creek corridor with naturalized banks of native willows, sedges, and river stone runs diagonally through the site, 60-80 feet wide, with timber-and-steel pedestrian bridges with cable railings. Clusters of 3-4 story mass-timber buildings with honey-blonde CLT facades, charcoal-gray metal panel accents, deep window reveals, extensive silvery-green sedum green roofs with integrated solar pergolas. A 1.5-acre urban farm with organized dark-soil raised crop rows, white translucent hoop houses, and a small timber-frame farm stand with copper standing-seam roof. A heavy-timber market pavilion with zinc butterfly roof near a terraced grass amphitheater with stone retaining walls. Decomposed granite and permeable buff paver paths throughout. A mobility hub with covered bike parking and bus shelter. Almost no asphalt parking visible. People crossing bridges and browsing the farm stand.",
    ],
    "openspaces/community-garden-enhanced": [
        # variant_0 — Classic Allotment
        "Photorealistic aerial 3/4 angle view of a European-style allotment garden colony, golden hour warm lighting, 8K resolution. A patchwork of 30 individual rectangular garden plots separated by clipped 1.25-meter-tall privet hedgerows and connected by warm honey-toned packed gravel paths in a regular grid. Each plot has a small pitched-roof painted timber garden shed in varied colors -- soft blue, moss green, barn red, creamy yellow -- with white window trim, some with small covered porches. Plots contain diverse plantings: vegetable rows with cabbages and tomatoes on stakes, runner beans on bamboo wigwams, cutting flower beds with dahlias and sunflowers, berry bushes, small fruit trees, and small manicured lawn patches with garden chairs. A communal area at the entrance with an open-sided timber pavilion with hipped roof and picnic tables, shared tool storage shed, and composting station. A small communal orchard with mature apple and pear trees in one corner. Rain barrels and cold frames visible in some plots. Perimeter fence with climbing roses. Warm golden light casting long shadows across the patchwork.",
        # variant_1 — Urban Permaculture Farm
        "Photorealistic aerial 3/4 angle view of an urban permaculture farm and food forest community garden, golden hour warm lighting, 8K resolution. Clearly zonated layout: a dense seven-layer food forest zone with tall apple, pear, and plum tree canopy over hazelnut and elderberry understory and strawberry ground cover, appearing as a lush varied-texture green mass. Adjacent organized market garden with parallel cedar raised beds weathered silver-gray, 4 feet wide, filled with dark rich soil and rows of lettuces, kale, herbs, and root vegetables, straw mulch between rows. Two white translucent polyethylene hoop houses on galvanized steel frames. A small barn-red painted timber tool shed. An open-front timber farm stand with corrugated metal lean-to roof displaying wooden crates. Warm brown wood chip mulch paths through the food forest, buff decomposed granite paths through the market garden. An outdoor classroom with log-round seating in a semicircle around a demonstration bed. A three-bin timber composting station. A dark green rainwater cistern near the greenhouse. Community members tending beds.",
        # variant_2 — Healing Garden
        "Photorealistic aerial 3/4 angle view of a therapeutic healing garden adjacent to a hospital building, golden hour warm lighting, 8K resolution. A flowing organic figure-eight loop path 5-6 feet wide of warm buff-toned resin-bound gravel with dark stone edge bands, connecting raised sensory planting beds 30-36 inches high built of smooth buff-colored natural stone with rounded coping edges. Beds filled with lavender, rosemary, thyme, lamb's ear, and ornamental grasses in purples, silvers, and soft greens. A central water feature with a gray granite stone basin and gentle recirculating flow surrounded by ferns and Japanese iris. Heavy Douglas fir timber pergolas with climbing wisteria and jasmine providing shade. Circular meditation alcoves paved in blue-gray slate with single teak benches screened by tall miscanthus grasses. Japanese maple trees with red foliage and white-blossoming serviceberry trees for shade. Brushed stainless steel handrails with timber top rail along key path sections. A small lean-to greenhouse at one end. A covered walkway connecting to an adjacent modern hospital building. A person in a wheelchair on the path.",
        # variant_3 — Intercultural Social Garden
        "Photorealistic aerial 3/4 angle view of an intercultural community garden with communal cooking area and diverse cultural planting zones, golden hour warm lighting, 8K resolution. A central gathering lawn of mowed green turf surrounded by garden areas. A heavy timber post-and-beam cooking pavilion open three sides with corrugated metal roof, whitewashed domed masonry bread oven with brick chimney, stainless steel prep counters, and long communal timber dining tables. Culturally themed planting quadrants: a Mediterranean zone with olive and fig trees, grape arbor on timber trellis, terra-cotta raised beds of rosemary and sage. An Asian zone with bamboo-edged low beds of bok choy, lemongrass, and taro. An African-Caribbean zone with mounded beds of okra and callaloo with recycled timber edging. A Latin American milpa zone with corn, beans, and squash. A children's nature play area with timber balance beams, log stepping stones, and willow tunnel. A raised timber stage platform with string light poles. Bright mosaic tile art panels in blues, yellows, and oranges on the pavilion walls. Brightly painted Adirondack chairs in turquoise, yellow, and coral red on the lawn. Community members cooking and gardening.",
    ],
}


def generate_image(client: httpx.Client, api_key: str, prompt: str) -> bytes:
    """Call Gemini API and return raw PNG bytes."""
    resp = client.post(
        ENDPOINT,
        params={"key": api_key},
        json={
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "responseModalities": ["TEXT", "IMAGE"],
                "temperature": 0.0,
            },
        },
        timeout=120,
    )
    resp.raise_for_status()
    data = resp.json()

    # Find the part with inlineData
    for candidate in data.get("candidates", []):
        for part in candidate.get("content", {}).get("parts", []):
            if "inlineData" in part:
                b64 = part["inlineData"]["data"]
                return base64.b64decode(b64)

    raise RuntimeError(f"No image in response: {data}")


def main():
    api_key = load_api_key()
    client = httpx.Client()
    total = sum(len(v) for v in PROMPTS.values())
    done = 0

    for subdir, prompts in PROMPTS.items():
        out_dir = os.path.join(BASE_DIR, subdir)
        os.makedirs(out_dir, exist_ok=True)

        for i, prompt in enumerate(prompts):
            fname = f"variant_{i}.png"
            fpath = os.path.join(out_dir, fname)
            done += 1
            print(f"[{done}/{total}] Generating {subdir}/{fname} ...")

            img_bytes = generate_image(client, api_key, prompt)
            with open(fpath, "wb") as f:
                f.write(img_bytes)
            print(f"  -> Saved {len(img_bytes)} bytes")

            # Copy variant_0 as hero.png
            if i == 0:
                hero_path = os.path.join(out_dir, "hero.png")
                shutil.copy2(fpath, hero_path)
                print(f"  -> Copied to hero.png")

            # Delay between requests (skip after last)
            if done < total:
                print(f"  Waiting {DELAY}s ...")
                time.sleep(DELAY)

    client.close()
    print("\nDone! All images generated.")


if __name__ == "__main__":
    main()
