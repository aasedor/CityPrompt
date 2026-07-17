"""Generate rectified, repeatable facade sheets for one compiled family.

The geometry generator remains responsible for massing, roofs, setbacks and
shadow-casting attachments.  This tool moves the small facade detail that is
expensive to model (window assemblies, reveals, masonry variation, shopfronts)
into a compact photographic elevation, following the same texture-atlas
strategy used by the Chicago and Kinnaird reference models.

Run after ``generate_family.py`` has produced ``grammar.json``::

    backend/.venv/Scripts/python.exe tools/archetype_compiler/generate_facade_sheets.py \
        --family build/worldclass-v7/rndsqr

The raw Gemini elevation is cached.  ``--reprocess`` re-runs the deterministic
band detection and texture processing without making another API call.
"""
from __future__ import annotations

import argparse
import io
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter

TOOL_DIR = Path(__file__).resolve().parent
REPO_ROOT = TOOL_DIR.parents[1]
sys.path.insert(0, str(TOOL_DIR))

from generate_textures import derive_roughness, flatten_lighting, load_api_key  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

MODEL_ID = "gemini-3.1-flash-image"
SHEET_BAYS = 4
ELEVATION_FLOORS = 3
PARAPET_M = 0.9
ALBEDO_WIDTH = 1024
ROUGHNESS_WIDTH = 512
EMISSIVE_WIDTH = 512
JPEG_QUALITY = 91
MAX_ATTEMPTS = 3

PROMPT_TEMPLATES = (
    "Architectural facade TEXTURE MAP for a professional real-time 3D model. "
    "Create a strict rectified orthographic front elevation; the flat wall surface "
    "fills 100 percent of the image. Bottom to top: one {podium_m:.1f} metre {ground}; "
    "exactly {floors} identical {floor_m:.1f} metre upper storeys; then a thin parapet. "
    "Exactly {bays} structural bays across, but preserve intentional asymmetry and signature bays. "
    "Architectural identity: {look}. NON-NEGOTIABLE identity cues: {identity}. "
    "Material zoning: {material_zones}. Do not genericize, regularize away, or substitute these cues. "
    "Physically believable construction, precise window frames, deep reveals, lintels, "
    "sills, material joints and subtle weathering. A few windows may show softly lit, "
    "unoccupied interiors. Flat even overcast capture light. The wall reaches every edge: "
    "no sky, no pavement, no perspective, no whole-building scene, no people, no signs, "
    "no legible text, no trees and no cars.",
    "Rectified edge-to-edge facade atlas for texturing a rectangular game building. "
    "Shift-lens straight-on elevation, zero perspective. At the bottom edge place one "
    "{podium_m:.1f} metre {ground}; above it exactly {floors} repeating {floor_m:.1f} "
    "metre floors; slim coping at the top. {bays} structural bays wide. Style and construction: "
    "{look}. Required building-specific identity: {identity}. Material zoning: {material_zones}. "
    "Retain distinctive feature bays and deliberate asymmetry. Photoreal architectural materials, accurate joinery, windows, shadowed reveals, "
    "sills and restrained age variation. Uniform diffuse overcast light. Texture surface "
    "only: no sky, no ground plane, no perspective, no massing setback, no people, no writing or scenery.",
    "Seamless architectural elevation texture, wall surface edge to edge, for a modular GLB. "
    "Exactly {bays} structural bays across. Vertical arrangement: {podium_m:.1f} metre {ground} "
    "at the bottom, then {floors} matching {floor_m:.1f} metre typical floors, then a narrow "
    "roofline band. Visual brief: {look}. Required unique composition: {identity}. "
    "Material zones: {material_zones}. Professional archviz realism, buildable details, "
    "fine window assemblies and natural material variation. Orthographic, evenly de-lit, "
    "no sky, no street, no perspective, no objects, no people and no text.",
)


def load_grammar(family_dir: Path) -> dict:
    path = family_dir / "grammar.json"
    if not path.exists():
        raise SystemExit(f"grammar.json not found in {family_dir}; generate the family first")
    return json.loads(path.read_text(encoding="utf-8"))


def facade_look_prose(grammar: dict) -> str:
    source = grammar.get("source") or {}
    materials = grammar.get("materials") or {}
    details = []
    for slot in ("primary", "secondary", "accent"):
        text = str((materials.get(slot) or {}).get("source_text") or "").strip().rstrip(".")
        if text and text.lower() not in {item.lower() for item in details}:
            details.append(text)
    identity = source.get("variant_label") or source.get("archetype_label") or grammar["family_id"]
    category = source.get("aesthetic_category_label") or source.get("aesthetic_category_id") or ""
    system = str((grammar.get("facade") or {}).get("system") or "").replace("_", " ")
    roof = str((grammar.get("roof") or {}).get("type") or "").replace("_", " ")
    sentence = f"{identity}; {category}; {system} facade; {roof} roof"
    if details:
        sentence += "; " + "; ".join(details)
    return sentence[:650]


def signature_prose(grammar: dict) -> tuple[str, str]:
    signature = grammar.get("architectural_signature") or {}
    identity = str(signature.get("identity") or "preserve the reference's distinctive composition and proportions")
    material_zones = str(signature.get("material_zones") or "faithful archetype-specific material hierarchy")
    return identity[:700], material_zones[:420]


def band_layout(grammar: dict) -> dict:
    dims = grammar["dimensions"]
    podium = float(dims["podium_height_m"])
    floor = float(dims["floor_height_m"])
    total = PARAPET_M + ELEVATION_FLOORS * floor + podium
    return {
        "podium_m": podium,
        "floor_m": floor,
        "parapet_f": PARAPET_M / total,
        "floor_f": floor / total,
        "podium_f": podium / total,
        "requested_span_m": SHEET_BAYS * float(grammar["facade"]["bay_width_m"]),
    }


def reference_image(grammar: dict) -> Image.Image | None:
    thumb = str((grammar.get("source") or {}).get("thumbnail_url") or "")
    candidate = REPO_ROOT / "frontend" / "public" / thumb.lstrip("/")
    if not thumb or not candidate.exists():
        return None
    image = Image.open(candidate).convert("RGB")
    image.thumbnail((1024, 1024))
    print(f"[facade_sheets] reference={candidate.relative_to(REPO_ROOT)}")
    return image


def generate_elevation(client, prompt: str, reference: Image.Image | None) -> Image.Image:
    from google.genai import types

    contents: list = []
    if reference is not None:
        contents.append(reference)
        prompt += (
            " The attached catalogue image is a HARD DESIGN REFERENCE, not loose inspiration. "
            "Match its silhouette logic, architectural language, bay proportions, material zones, "
            "opening rhythm, signature asymmetry and colour palette. Preserve the cues that make it "
            "recognizable while converting it into the rectified texture map specified above."
        )
    contents.append(prompt)
    response = client.models.generate_content(
        model=MODEL_ID,
        contents=contents,
        config=types.GenerateContentConfig(
            response_modalities=["TEXT", "IMAGE"],
            image_config=types.ImageConfig(aspect_ratio="9:16", image_size="2K"),
        ),
    )
    for candidate in response.candidates or []:
        for part in (candidate.content.parts if candidate.content else []) or []:
            inline = getattr(part, "inline_data", None)
            if inline and inline.data:
                return Image.open(io.BytesIO(inline.data)).convert("RGB")
    reasons = ", ".join(str(candidate.finish_reason) for candidate in (response.candidates or []))
    raise RuntimeError(f"Gemini returned no image ({reasons})")


def _row_variance_profile(image: Image.Image) -> np.ndarray:
    grey = np.asarray(image.convert("L"), dtype=np.float64)
    profile = grey.var(axis=1)
    width = max(3, image.height // 200)
    return np.convolve(profile, np.ones(width) / width, mode="same")


def detect_floor_band(
    elevation: Image.Image,
    fallback_top: float,
    fallback_bottom: float,
    expected_fraction: float,
) -> tuple[float, float, str]:
    height = elevation.height
    profile = _row_variance_profile(elevation)
    body = profile[int(0.07 * height): int(0.76 * height)]
    body = body - body.mean()
    if body.std() < 1e-6:
        return fallback_top, fallback_bottom, "fallback-flat"
    autocorrelation = np.correlate(body, body, mode="full")[body.size - 1:]
    low = max(8, int(0.5 * expected_fraction * height))
    high = min(body.size - 1, int(1.85 * expected_fraction * height))
    if high <= low + 4:
        return fallback_top, fallback_bottom, "fallback-range"
    lag = low + int(np.argmax(autocorrelation[low:high]))
    confidence = float(autocorrelation[lag] / (autocorrelation[0] + 1e-9))
    if confidence < 0.24:
        return fallback_top, fallback_bottom, f"fallback-confidence-{confidence:.2f}"
    midpoint = int(0.40 * height)
    start = max(0, midpoint - lag // 2)
    stop = min(height, midpoint + lag // 2)
    anchor = start + int(np.argmin(profile[start:stop]))
    top, bottom = anchor / height, (anchor + lag) / height
    if bottom > 0.88:
        top, bottom = top - lag / height, top
    return top, bottom, f"autocorrelation-{lag}px-{confidence:.2f}"


def detect_podium_band(
    elevation: Image.Image,
    lowest_floor_bottom: float,
    fallback_top: float,
) -> tuple[float, float, str]:
    height = elevation.height
    grey = np.asarray(elevation.convert("L"), dtype=np.float64)
    luminance = grey.mean(axis=1)
    median = float(np.median(luminance[int(0.15 * height): int(0.75 * height)]))
    bottom = height - 1
    for y in range(height - 1, int(0.80 * height), -1):
        if luminance[y] <= median * 1.35:
            bottom = y
            break
    top = max(int(lowest_floor_bottom * height), int(fallback_top * height))
    if bottom - top < height * 0.05:
        return fallback_top, 1.0, "fallback-thin"
    return top / height, bottom / height, f"pavement-cut-{bottom}px"


def slice_band(elevation: Image.Image, top: float, bottom: float) -> Image.Image:
    trim = 0.012 * (bottom - top)
    y0 = max(0, int(round((top + trim) * elevation.height)))
    y1 = min(elevation.height, int(round((bottom - trim) * elevation.height)))
    return elevation.crop((0, y0, elevation.width, max(y0 + 8, y1)))


def roll_accent_off_seam(band: Image.Image) -> Image.Image:
    array = np.asarray(band.convert("RGB"), dtype=np.int16)
    saturation = (array.max(axis=2) - array.min(axis=2)).mean(axis=0)
    kernel_width = max(8, band.width // 16)
    smooth = np.convolve(saturation, np.ones(kernel_width) / kernel_width, mode="same")
    peak = int(np.argmax(smooth))
    if smooth[peak] < smooth.mean() * 1.45:
        return band
    return Image.fromarray(np.roll(np.asarray(band), int(0.61 * band.width) - peak, axis=1))


def make_horizontally_tileable(image: Image.Image, feather: float = 0.07) -> Image.Image:
    array = np.asarray(image, dtype=np.float64)
    rolled = np.roll(array, image.width // 2, axis=1)
    index = np.arange(image.width)
    distance = np.minimum(index, image.width - 1 - index) / max(1.0, feather * image.width)
    weight = np.clip(distance, 0.0, 1.0)
    weight = (weight * weight * (3 - 2 * weight))[None, :, None]
    return Image.fromarray(np.clip(weight * array + (1 - weight) * rolled, 0, 255).astype(np.uint8))


def derive_emissive_mask(albedo: Image.Image) -> Image.Image:
    """Conservative warm-window mask; black everywhere except plausible lit glass."""
    rgb = np.asarray(albedo.convert("RGB"), dtype=np.float32) / 255.0
    maximum = rgb.max(axis=2)
    minimum = rgb.min(axis=2)
    warm = (rgb[:, :, 0] > rgb[:, :, 2] * 1.14) & (rgb[:, :, 1] > rgb[:, :, 2] * 1.04)
    saturated = (maximum - minimum) > 0.07
    midbright = (maximum > 0.34) & (maximum < 0.93)
    mask = (warm & saturated & midbright).astype(np.uint8) * 255
    result = Image.fromarray(mask, mode="L").filter(ImageFilter.MedianFilter(5)).filter(ImageFilter.GaussianBlur(1.1))
    return ImageEnhance.Contrast(result).enhance(1.35)


def process_band(name: str, band: Image.Image, out_dir: Path, roughness_anchor: float) -> dict:
    prepared = make_horizontally_tileable(flatten_lighting(roll_accent_off_seam(band)))
    target_height = max(64, round(ALBEDO_WIDTH * prepared.height / prepared.width))
    albedo = prepared.resize((ALBEDO_WIDTH, target_height), Image.Resampling.LANCZOS)
    roughness = derive_roughness(albedo, roughness_anchor).resize(
        (ROUGHNESS_WIDTH, max(32, round(ROUGHNESS_WIDTH * target_height / ALBEDO_WIDTH))),
        Image.Resampling.LANCZOS,
    )
    emissive = derive_emissive_mask(albedo).resize(
        (EMISSIVE_WIDTH, max(32, round(EMISSIVE_WIDTH * target_height / ALBEDO_WIDTH))),
        Image.Resampling.LANCZOS,
    )
    albedo_file = f"{name}_albedo.jpg"
    roughness_file = f"{name}_roughness.jpg"
    emissive_file = f"{name}_emissive.png"
    albedo.save(out_dir / albedo_file, quality=JPEG_QUALITY, subsampling=0)
    roughness.convert("L").save(out_dir / roughness_file, quality=88)
    emissive.save(out_dir / emissive_file, optimize=True)
    return {
        "albedo": albedo_file,
        "roughness": roughness_file,
        "emissive": emissive_file,
        "px": [albedo.width, albedo.height],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate facade sheets for one modular family")
    parser.add_argument("--family", required=True, type=Path, help="directory containing grammar.json")
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--api-key", default=None)
    parser.add_argument("--force", action="store_true", help="regenerate the cached raw elevation")
    parser.add_argument("--reprocess", action="store_true", help="reuse cached elevation; no API call")
    args = parser.parse_args()

    family_dir = args.family.resolve()
    grammar = load_grammar(family_dir)
    family = grammar["family_id"]
    out_dir = (args.out or TOOL_DIR / "facade_sheets" / family).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    raw_path = out_dir / "elevation_raw.jpg"
    layout = band_layout(grammar)
    look = facade_look_prose(grammar)
    identity, material_zones = signature_prose(grammar)
    prompt_used = "(cached raw)"
    print(f"[facade_sheets] family={family} look={look[:110]!r}")

    if args.reprocess:
        if not raw_path.exists():
            raise SystemExit(f"--reprocess requested but {raw_path} is missing")
        elevation = Image.open(raw_path).convert("RGB")
        prompt_used = "(reprocess)"
    elif raw_path.exists() and not args.force:
        elevation = Image.open(raw_path).convert("RGB")
        print(f"[facade_sheets] reusing {raw_path.name}; pass --force to regenerate")
    else:
        from google import genai

        client = genai.Client(api_key=load_api_key(args.api_key))
        reference = reference_image(grammar)
        elevation = None
        last_error: Exception | None = None
        retail = bool((grammar.get("massing") or {}).get("has_podium_retail"))
        ground = (
            "commercial ground floor with detailed glazed storefronts and a main entrance"
            if retail else
            "taller ground floor with a clearly detailed main entrance and larger windows"
        )
        for attempt in range(MAX_ATTEMPTS):
            prompt_used = PROMPT_TEMPLATES[attempt % len(PROMPT_TEMPLATES)].format(
                podium_m=layout["podium_m"],
                ground=ground,
                floors=ELEVATION_FLOORS,
                floor_m=layout["floor_m"],
                bays=SHEET_BAYS,
                look=look,
                identity=identity,
                material_zones=material_zones,
            )
            try:
                elevation = generate_elevation(client, prompt_used, reference)
                break
            except Exception as exc:
                last_error = exc
                print(f"[facade_sheets] attempt {attempt + 1} failed: {exc}")
                time.sleep(0.8)
        if elevation is None:
            raise SystemExit(f"all Gemini attempts failed: {last_error}")
        elevation.save(raw_path, quality=93, subsampling=0)
        print(f"[facade_sheets] saved {raw_path.name} {elevation.width}x{elevation.height}")

    first_floor_top = layout["parapet_f"] + layout["floor_f"]
    first_floor_bottom = first_floor_top + layout["floor_f"]
    requested_podium_top = layout["parapet_f"] + ELEVATION_FLOORS * layout["floor_f"]
    floor_top, floor_bottom, floor_method = detect_floor_band(
        elevation, first_floor_top, first_floor_bottom, layout["floor_f"]
    )
    period = floor_bottom - floor_top
    lowest_top = floor_top
    while lowest_top + 2 * period < 0.86:
        lowest_top += period
    podium_top, podium_bottom, podium_method = detect_podium_band(
        elevation, lowest_top + period, requested_podium_top
    )
    print(f"[facade_sheets] floor={floor_top:.3f}:{floor_bottom:.3f} ({floor_method})")
    print(f"[facade_sheets] podium={podium_top:.3f}:{podium_bottom:.3f} ({podium_method})")

    floor_band = slice_band(elevation, floor_top, floor_bottom)
    alt_top = floor_top - period
    if alt_top < layout["parapet_f"] * 0.72:
        alt_top = floor_top + period
    alt_bottom = min(podium_top, alt_top + period)
    if alt_bottom - alt_top < period * 0.72:
        alt_top, alt_bottom = floor_top, floor_bottom
    floor_alt_band = slice_band(elevation, alt_top, alt_bottom)
    crown_bottom = min(podium_top, max(floor_bottom, layout["parapet_f"] + layout["floor_f"] * 1.08))
    crown_band = slice_band(elevation, 0.0, crown_bottom)
    podium_band = slice_band(elevation, podium_top, podium_bottom)
    bands = {
        "floor": process_band("floor", floor_band, out_dir, 0.52),
        "floor_alt": process_band("floor_alt", floor_alt_band, out_dir, 0.52),
        "crown": process_band("crown", crown_band, out_dir, 0.50),
        "podium": process_band("podium", podium_band, out_dir, 0.40),
    }
    span_m = layout["floor_m"] * floor_band.width / max(1, floor_band.height)
    manifest = {
        "schema": "facade-sheet@3",
        "family": family,
        "archetype_id": (grammar.get("source") or {}).get("archetype_id"),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "model": MODEL_ID,
        "prompt": prompt_used,
        "style_reference": (grammar.get("source") or {}).get("thumbnail_url"),
        "architectural_signature": grammar.get("architectural_signature"),
        "span_m": round(span_m, 2),
        "requested_span_m": round(layout["requested_span_m"], 2),
        "sheet_bays": SHEET_BAYS,
        "bands": {
            "floor": {**bands["floor"], "height_m": layout["floor_m"]},
            "floor_alt": {**bands["floor_alt"], "height_m": layout["floor_m"]},
            "crown": {**bands["crown"], "height_m": layout["floor_m"]},
            "podium": {**bands["podium"], "height_m": layout["podium_m"]},
        },
        "detection": {
            "floor": floor_method,
            "floor_alt": [round(alt_top, 4), round(alt_bottom, 4)],
            "crown": [0.0, round(crown_bottom, 4)],
            "podium": podium_method,
        },
    }
    manifest_path = out_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"[facade_sheets] span={span_m:.2f}m; wrote {manifest_path}")
    print(str(out_dir))


if __name__ == "__main__":
    main()
