"""A/B pilot: top-down orthographic park GROUND texture from GPT Image 2 vs Gemini.

Renders the pilot park zone (Water Centre 'Local Area Plan Aligned - Park',
bf5bc13d) polygon as a to-scale diagram, then asks both models for a nadir
orthophoto of the park's ground plane WITHOUT trees (trees come from the 3D
park kit). Output textures get draped onto the green_space fill mesh, so the
diagram is drawn at TRUE aspect, letterboxed in a square canvas, and a sidecar
JSON records the UV sub-rect of the zone bbox for the drape code.

  python scripts/_pilot_park_ortho_ab.py            # diagram + both renders
  python scripts/_pilot_park_ortho_ab.py --diagram-only
"""
from __future__ import annotations
import argparse, base64, json, math, os, sys
from pathlib import Path

import httpx
from PIL import Image, ImageDraw

_SD = Path(__file__).resolve().parent
sys.path.insert(0, str(_SD))
from generate_card_images import API_URL  # type: ignore  (Gemini generateContent URL+key)

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = _SD.parent
OUT = ROOT / "artifacts" / "park-ortho-pilot"
OUT.mkdir(parents=True, exist_ok=True)
ZONE = OUT / "zone.geojson"

CANVAS = 1024
FIT = 0.86  # park occupies 86% of the canvas' limiting dimension
METERS_PER_DEG_LAT = 111_320.0


def openai_key() -> str | None:
    if os.environ.get("OPENAI_API_KEY"):
        return os.environ["OPENAI_API_KEY"]
    for env in (ROOT / ".env", ROOT / "backend" / ".env"):
        if env.exists():
            for ln in env.read_text(encoding="utf-8").splitlines():
                if ln.strip().startswith("OPENAI_API_KEY="):
                    return ln.split("=", 1)[1].strip()
    return None


def build_diagram() -> tuple[Path, dict]:
    ring = json.loads(ZONE.read_text())["coordinates"][0]
    lngs = [p[0] for p in ring]
    lats = [p[1] for p in ring]
    w, s, e, n = min(lngs), min(lats), max(lngs), max(lats)
    lat0 = (s + n) / 2
    m_per_deg_lon = METERS_PER_DEG_LAT * math.cos(math.radians(lat0))
    width_m = (e - w) * m_per_deg_lon
    height_m = (n - s) * METERS_PER_DEG_LAT

    px_per_m = CANVAS * FIT / max(width_m, height_m)
    park_w_px = width_m * px_per_m
    park_h_px = height_m * px_per_m
    x0 = (CANVAS - park_w_px) / 2
    y0 = (CANVAS - park_h_px) / 2

    def to_px(lng: float, lat: float) -> tuple[float, float]:
        x = x0 + (lng - w) * m_per_deg_lon * px_per_m
        y = y0 + (n - lat) * METERS_PER_DEG_LAT * px_per_m  # north up -> canvas y down
        return x, y

    img = Image.new("RGB", (CANVAS, CANVAS), "white")
    d = ImageDraw.Draw(img)
    d.polygon([to_px(lng, lat) for lng, lat in ring], fill="#a5c88a", outline="#333333", width=4)
    diagram = OUT / "diagram.png"
    img.save(diagram)

    sidecar = {
        "zone_id": "bf5bc13d-8a01-4d7e-ab1b-c994fe085499",
        "bbox": {"west": w, "south": s, "east": e, "north": n},
        "size_m": {"width": round(width_m, 1), "height": round(height_m, 1)},
        # UV sub-rect of the zone bbox inside the texture (v=0 at image BOTTOM,
        # matching three.js texture convention)
        "uv_rect": {
            "u0": x0 / CANVAS,
            "v0": (CANVAS - (y0 + park_h_px)) / CANVAS,
            "u1": (x0 + park_w_px) / CANVAS,
            "v1": (CANVAS - y0) / CANVAS,
        },
    }
    (OUT / "texture_meta.json").write_text(json.dumps(sidecar, indent=2))
    print(f"diagram: park {width_m:.0f}x{height_m:.0f} m -> {park_w_px:.0f}x{park_h_px:.0f} px in {CANVAS}^2")
    return diagram, sidecar


def prompt_for(size_m: dict) -> str:
    return (
        "The attached image is a to-scale site-plan DIAGRAM of a neighborhood park in Calgary, Canada. "
        f"The green polygon is the park parcel, about {size_m['width']:.0f} m wide (east-west) by "
        f"{size_m['height']:.0f} m tall (north-south); north is up. "
        "Render this as a photorealistic straight-down TOP-DOWN AERIAL (nadir) orthophoto of the park's "
        "GROUND PLANE in summer, in the style of high-resolution Google Earth imagery: mowed lawn with "
        "natural tone variation and mowing stripes, smooth curving concrete walking paths linking the "
        "corners, a small circular central plaza with seating, low planting beds with shrubs and "
        "perennials, a sandy playground pad near one edge, and a gravel fitness loop. This is an OPEN "
        "TREELESS lawn park - all planting is low groundcover and shrubs seen from directly above; tree "
        "canopies are added later in 3D. Fill the parcel polygon with the park design and continue plain "
        "mowed grass beyond the outline to the image edges. CRITICAL: camera pointing exactly straight "
        "down with zero perspective, flat even midday light with no long shadows, no tree canopies, no "
        "buildings, no vehicles, no people, no text, labels or watermarks."
    )


def gpt_render(diagram: Path, prompt: str, out: Path, key: str) -> str:
    # gpt-image-2 rejects input_fidelity (locked-to-high internally) — omit it.
    data = {"model": "gpt-image-2", "prompt": prompt, "n": "1", "size": "1024x1024",
            "quality": "high", "output_format": "png"}
    for attempt in range(3):
        try:
            files = {"image": (diagram.name, diagram.read_bytes(), "image/png")}
            with httpx.Client(timeout=420.0) as c:
                r = c.post("https://api.openai.com/v1/images/edits", data=data, files=files,
                           headers={"Authorization": f"Bearer {key}"})
            if r.status_code != 200:
                return f"GPT: HTTP {r.status_code} {r.text[:160]}"
            b64 = r.json().get("data", [{}])[0].get("b64_json")
            if not b64:
                return "GPT: no image"
            out.write_bytes(base64.b64decode(b64))
            return f"GPT: OK ({out.stat().st_size // 1024} KB)"
        except Exception as exc:
            if attempt == 2:
                return f"GPT: ERR {type(exc).__name__}: {str(exc)[:120]}"
    return "GPT: failed"


def gemini_render(diagram: Path, prompt: str, out: Path, temp: float = 0.45) -> str:
    img_b64 = base64.b64encode(diagram.read_bytes()).decode()
    payload = {"contents": [{"role": "user", "parts": [
        {"inlineData": {"mimeType": "image/png", "data": img_b64}}, {"text": prompt}]}],
        "generationConfig": {"responseModalities": ["TEXT", "IMAGE"], "temperature": temp,
                             "imageConfig": {"aspectRatio": "1:1"}}}
    for attempt in range(3):
        try:
            with httpx.Client(timeout=240.0) as c:
                r = c.post(API_URL, json=payload, headers={"Content-Type": "application/json"})
            if r.status_code != 200:
                return f"GEM: HTTP {r.status_code} {r.text[:160]}"
            for part in r.json().get("candidates", [{}])[0].get("content", {}).get("parts", []):
                if part.get("inlineData", {}).get("mimeType", "").startswith("image/"):
                    out.write_bytes(base64.b64decode(part["inlineData"]["data"]))
                    return f"GEM: OK ({out.stat().st_size // 1024} KB)"
            return "GEM: no image"
        except Exception as exc:
            if attempt == 2:
                return f"GEM: ERR {type(exc).__name__}: {str(exc)[:120]}"
    return "GEM: failed"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--diagram-only", action="store_true")
    args = ap.parse_args()

    diagram, sidecar = build_diagram()
    if args.diagram_only:
        return
    prompt = prompt_for(sidecar["size_m"])

    key = openai_key()
    if not key:
        print("GPT: SKIPPED (no OPENAI_API_KEY)")
    else:
        print(gpt_render(diagram, prompt, OUT / "park_ortho_gpt.png", key))
    print(gemini_render(diagram, prompt, OUT / "park_ortho_gemini.png"))


if __name__ == "__main__":
    main()
