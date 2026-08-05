"""Compile reference-driven neighborhood-park material skins without API calls.

This mirrors the deterministic half of the Parisian facade workflow:
hard archetype references -> one audited rectified orthographic atlas ->
derived normal/roughness/AO maps -> provenance manifest and QA sheet.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

TOOL_DIR = Path(__file__).resolve().parent
REPO_ROOT = TOOL_DIR.parents[1]
SCHEDULE_PATH = TOOL_DIR / "neighborhood_park_sources.json"
DEFAULT_PUBLIC_OUT = REPO_ROOT / "frontend/public/park-skins/neighborhood-park"
DEFAULT_ARTIFACT_OUT = REPO_ROOT / "artifacts/neighborhood-park-reference-skins-v2"
TEXTURE_SIZE = 1024
JPEG_QUALITY = 92


def gray(arr: np.ndarray) -> np.ndarray:
    return arr.astype(np.float64) @ np.array([0.299, 0.587, 0.114])


def flatten_lighting(image: Image.Image) -> Image.Image:
    arr = np.asarray(image.convert("RGB"), dtype=np.float64)
    luminance = Image.fromarray(gray(arr).astype(np.uint8))
    blur_radius = max(10, min(arr.shape[:2]) / 3)
    blurred = np.asarray(luminance.filter(ImageFilter.GaussianBlur(blur_radius)), dtype=np.float64)
    gain = blurred.mean() / np.clip(blurred, 24.0, None)
    return Image.fromarray(np.clip(arr * gain[..., None], 0, 255).astype(np.uint8))


def derive_normal(albedo: Image.Image, strength: float) -> Image.Image:
    height = gray(np.asarray(albedo.filter(ImageFilter.GaussianBlur(1.2)))) / 255.0
    padded = np.pad(height, 1, mode="wrap")
    gx = ((padded[:-2, 2:] + 2 * padded[1:-1, 2:] + padded[2:, 2:])
          - (padded[:-2, :-2] + 2 * padded[1:-1, :-2] + padded[2:, :-2])) / 8.0
    gy = ((padded[2:, :-2] + 2 * padded[2:, 1:-1] + padded[2:, 2:])
          - (padded[:-2, :-2] + 2 * padded[:-2, 1:-1] + padded[:-2, 2:])) / 8.0
    nx, ny, nz = -gx * strength, gy * strength, np.ones_like(gx)
    length = np.sqrt(nx * nx + ny * ny + nz * nz)
    rgb = np.stack((nx / length, ny / length, nz / length), axis=-1) * 0.5 + 0.5
    return Image.fromarray(np.clip(rgb * 255, 0, 255).astype(np.uint8))


def derive_roughness(albedo: Image.Image, base: float) -> Image.Image:
    g = gray(np.asarray(albedo)).astype(np.uint8)
    local = np.asarray(Image.fromarray(g).filter(ImageFilter.BoxBlur(8)), dtype=np.float64)
    contrast = np.abs(g.astype(np.float64) - local)
    lo, hi = np.percentile(contrast, (5, 95))
    normalized = np.clip((contrast - lo) / max(hi - lo, 1e-6), 0, 1)
    roughness = base + (0.5 - normalized) * 0.16
    return Image.fromarray(np.clip(roughness * 255, 26, 252).astype(np.uint8), mode="L")


def derive_ao(albedo: Image.Image) -> Image.Image:
    g = gray(np.asarray(albedo)).astype(np.uint8)
    local = np.asarray(Image.fromarray(g).filter(ImageFilter.GaussianBlur(10)), dtype=np.float64)
    relief = np.clip((local - g.astype(np.float64)) / 80.0, 0, 1)
    ao = 1.0 - relief * 0.36
    return Image.fromarray(np.clip(ao * 255, 0, 255).astype(np.uint8), mode="L")


def crop_pixels(image: Image.Image, box: list[float]) -> tuple[int, int, int, int]:
    width, height = image.size
    left, top, right, bottom = box
    return (
        max(0, min(width - 1, round(left * width))),
        max(0, min(height - 1, round(top * height))),
        max(1, min(width, round(right * width))),
        max(1, min(height, round(bottom * height))),
    )


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    names = ["arialbd.ttf" if bold else "arial.ttf", "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"]
    for name in names:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def rounded_image(image: Image.Image, size: tuple[int, int], radius: int = 14) -> Image.Image:
    fitted = image.copy()
    fitted.thumbnail(size, Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", size, "#e7e8e5")
    x, y = (size[0] - fitted.width) // 2, (size[1] - fitted.height) // 2
    canvas.paste(fitted, (x, y))
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, size[0] - 1, size[1] - 1), radius=radius, fill=255)
    result = Image.new("RGB", size, "white")
    result.paste(canvas, mask=mask)
    return result


def build_material_qa(schedule: dict, public_out: Path, artifact_out: Path) -> Path:
    cell_w, header_h, source_h, atlas_h, gap = 430, 130, 310, 300, 20
    width = cell_w * 4 + gap * 5
    height = header_h + source_h + atlas_h + gap * 4 + 70
    sheet = Image.new("RGB", (width, height), "#f4f2ed")
    draw = ImageDraw.Draw(sheet)
    draw.text((gap, 22), "NEIGHBORHOOD PARK — REFERENCE-DRIVEN MATERIAL PILOT", font=font(29, True), fill="#1d2a25")
    draw.text((gap, 64), "Existing archetype photo → audited park crop → rectified orthographic atlas → derived PBR", font=font(18), fill="#4d5b55")
    draw.text((gap, 94), "No generated colors and no image-generation API calls", font=font(16, True), fill="#7b5635")
    for column, (variant_id, variant) in enumerate(schedule["variants"].items()):
        x = gap + column * (cell_w + gap)
        source = Image.open(REPO_ROOT / variant["source"]).convert("RGB")
        sheet.paste(rounded_image(source, (cell_w, source_h)), (x, header_h))
        draw.rounded_rectangle((x, header_h + source_h - 45, x + cell_w, header_h + source_h), radius=12, fill="#17231fdc")
        draw.text((x + 16, header_h + source_h - 36), variant["label"], font=font(20, True), fill="white")
        sy = header_h + source_h + gap
        albedo = Image.open(public_out / variant_id / "albedo.jpg").convert("RGB")
        sheet.paste(rounded_image(albedo, (cell_w, atlas_h), radius=12), (x, sy))
        draw.rounded_rectangle((x + 12, sy + atlas_h - 40, x + 236, sy + atlas_h - 8), radius=9, fill="#17231fdc")
        draw.text((x + 24, sy + atlas_h - 34), "RECTIFIED PARK ATLAS", font=font(14, True), fill="white")
    draw.text((gap, height - 44), "Finite pilot: one fixed LEGO topology × four whole-image identity atlases; no repeating material fragments", font=font(15), fill="#59655f")
    artifact_out.mkdir(parents=True, exist_ok=True)
    output = artifact_out / "neighborhood-park-reference-materials.png"
    sheet.save(output, optimize=True)
    return output


def compile_textures(schedule: dict, public_out: Path, artifact_out: Path) -> dict:
    manifest = {
        "schemaVersion": 1,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "method": schedule["method"],
        "apiCalls": 0,
        "atlasSize": TEXTURE_SIZE,
        "variants": {},
    }
    crop_root = artifact_out / "atlas-crops"
    for variant_id, variant in schedule["variants"].items():
        source_path = REPO_ROOT / variant["source"]
        source = Image.open(source_path).convert("RGB")
        pixels = crop_pixels(source, variant["atlasCrop"])
        raw = source.crop(pixels)
        flattened = flatten_lighting(raw)
        albedo = flattened.resize((TEXTURE_SIZE, TEXTURE_SIZE), Image.Resampling.LANCZOS)
        normal = derive_normal(albedo, float(variant["atlasNormalStrength"]))
        roughness = derive_roughness(albedo, float(variant["atlasRoughness"]))
        ao = derive_ao(albedo)
        destination = public_out / variant_id
        destination.mkdir(parents=True, exist_ok=True)
        albedo.save(destination / "albedo.jpg", quality=JPEG_QUALITY, optimize=True)
        normal.save(destination / "normal.png", optimize=True)
        roughness.save(destination / "roughness.jpg", quality=90, optimize=True)
        ao.save(destination / "ao.jpg", quality=90, optimize=True)
        crop_root.mkdir(parents=True, exist_ok=True)
        raw.save(crop_root / f"{variant_id}.jpg", quality=JPEG_QUALITY)
        mean_rgb = np.asarray(albedo).reshape(-1, 3).mean(axis=0)
        variant_manifest = {
            "label": variant["label"],
            "source": variant["source"],
            "atlasCropNormalized": variant["atlasCrop"],
            "atlasCropPixels": pixels,
            "roughnessAnchor": variant["atlasRoughness"],
            "normalStrength": variant["atlasNormalStrength"],
            "meanRgb": [round(float(value), 1) for value in mean_rgb],
            "projection": "single non-repeating XY atlas across common park bounds",
            "files": {
                "albedo": f"{variant_id}/albedo.jpg",
                "normal": f"{variant_id}/normal.png",
                "roughness": f"{variant_id}/roughness.jpg",
                "ao": f"{variant_id}/ao.jpg"
            }
        }
        manifest["variants"][variant_id] = variant_manifest
    public_out.mkdir(parents=True, exist_ok=True)
    (public_out / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    artifact_out.mkdir(parents=True, exist_ok=True)
    (artifact_out / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--schedule", type=Path, default=SCHEDULE_PATH)
    parser.add_argument("--public-out", type=Path, default=DEFAULT_PUBLIC_OUT)
    parser.add_argument("--artifact-out", type=Path, default=DEFAULT_ARTIFACT_OUT)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    schedule = json.loads(args.schedule.read_text(encoding="utf-8"))
    if args.dry_run:
        print(f"method={schedule['method']} api_calls=0")
        for variant_id, variant in schedule["variants"].items():
            print(f"{variant_id}: {variant['source']} -> 1 rectified PBR park atlas")
        print(f"planned: {len(schedule['variants'])} whole-image atlases projected across one fixed LEGO topology")
        return
    compile_textures(schedule, args.public_out, args.artifact_out)
    qa = build_material_qa(schedule, args.public_out, args.artifact_out)
    print(f"wrote {args.public_out / 'manifest.json'}")
    print(f"wrote {qa}")


if __name__ == "__main__":
    main()
