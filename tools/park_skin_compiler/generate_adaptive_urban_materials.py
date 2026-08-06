"""Generate a stationary Urban Contemporary park material kit locally.

The checked-in archetype image calibrates colour statistics and material grain.
No source photograph is projected onto a parcel and no API is called.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

try:
    from .compile_neighborhood_park_skins import (
        REPO_ROOT,
        crop_pixels,
        derive_ao,
        derive_normal,
        derive_roughness,
        flatten_lighting,
    )
except ImportError:  # direct script execution
    from compile_neighborhood_park_skins import (
        REPO_ROOT,
        crop_pixels,
        derive_ao,
        derive_normal,
        derive_roughness,
        flatten_lighting,
    )

TOOL_DIR = Path(__file__).resolve().parent
SCHEDULE_PATH = TOOL_DIR / "adaptive_urban_material_sources.json"
DEFAULT_OUT = REPO_ROOT / "artifacts/neighborhood-park-adaptive-urban-v1/materials"
SIZE = 512
ROLES = ("paver", "lawn", "asphalt", "planting", "safety", "timber")


def multiscale_noise(size: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    white = rng.normal(0, 1, (size, size))
    spectrum = np.fft.fft2(white)
    frequency = np.fft.fftfreq(size)
    fx, fy = np.meshgrid(frequency, frequency)
    radius = np.sqrt(fx * fx + fy * fy)
    falloff = 1.0 / np.maximum(radius, 1.0 / size) ** 1.15
    falloff[0, 0] = 0.0
    result = np.fft.ifft2(spectrum * falloff).real
    return (result - result.mean()) / max(result.std(), 1e-6)


def reference_statistics(crop: Image.Image, role: str) -> tuple[np.ndarray, np.ndarray]:
    pixels = np.asarray(flatten_lighting(crop), dtype=np.float64).reshape(-1, 3)
    luminance = pixels @ np.array([0.299, 0.587, 0.114])
    maximum = pixels.max(axis=1)
    minimum = pixels.min(axis=1)
    saturation = (maximum - minimum) / np.maximum(maximum, 1.0)
    red, green, blue = pixels[:, 0], pixels[:, 1], pixels[:, 2]
    role_filters = {
        "paver": (saturation < 0.22) & (luminance > 75) & (luminance < 215),
        "lawn": (green > red * 1.06) & (green > blue * 1.10) & (red > blue * 1.12),
        "asphalt": (saturation < 0.34) & (luminance < 105),
        "planting": (green > red * 1.02) & (green > blue * 1.05) & (red > blue * 1.08) & (luminance < 190),
        "safety": (red > green * 1.04) & (green > blue * 1.10) & (luminance > 85),
        "timber": (red > green * 1.04) & (green > blue * 1.04) & (luminance > 55) & (luminance < 205),
    }
    keep = role_filters[role]
    keep &= (luminance >= np.percentile(luminance, 5)) & (luminance <= np.percentile(luminance, 95))
    if keep.sum() < 128:
        keep = (luminance >= np.percentile(luminance, 12)) & (luminance <= np.percentile(luminance, 88))
    trimmed = pixels[keep]
    mean = trimmed.mean(axis=0)
    covariance = np.cov(trimmed, rowvar=False)
    covariance += np.eye(3) * 0.1
    return mean, covariance


def stationary_base(crop: Image.Image, role: str, seed: int) -> Image.Image:
    mean, covariance = reference_statistics(crop, role)
    transform = np.linalg.cholesky(covariance * 0.34)
    noise = np.stack([multiscale_noise(SIZE, seed + index * 97) for index in range(3)], axis=-1)
    rgb = mean + noise @ transform.T
    return Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8), mode="RGB")


def paver_pattern(base: Image.Image, seed: int) -> Image.Image:
    rng = np.random.default_rng(seed)
    result = base.filter(ImageFilter.GaussianBlur(2.2))
    draw = ImageDraw.Draw(result, "RGBA")
    course_h, unit_w, joint = 32, 64, 3
    for row, y in enumerate(range(-course_h, SIZE + course_h, course_h)):
        offset = -(unit_w // 2) if row % 2 else 0
        for x in range(offset, SIZE + unit_w, unit_w):
            shade = int(rng.normal(0, 7))
            fill = (130 + shade, 134 + shade, 132 + shade, 46)
            draw.rectangle((x + joint, y + joint, x + unit_w - joint, y + course_h - joint), fill=fill)
        draw.line((0, y, SIZE, y), fill=(62, 69, 67, 105), width=joint)
    for x in range(0, SIZE + unit_w, unit_w):
        draw.line((x, 0, x, SIZE), fill=(70, 75, 74, 50), width=1)
    return result


def lawn_pattern(base: Image.Image) -> Image.Image:
    arr = np.asarray(base, dtype=np.float64)
    x = np.arange(SIZE)[None, :]
    stripe = np.sin(x * 2 * np.pi / 64.0) * 5.0 + np.sin(x * 2 * np.pi / 128.0) * 3.0
    arr[..., 1] += stripe
    arr[..., 0] += stripe * 0.35
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))


def asphalt_pattern(base: Image.Image, seed: int) -> Image.Image:
    arr = np.asarray(base.filter(ImageFilter.GaussianBlur(3)), dtype=np.float64)
    fine = multiscale_noise(SIZE, seed + 300)
    arr += fine[..., None] * np.array([2.5, 2.8, 3.0])
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))


def planting_pattern(base: Image.Image, seed: int) -> Image.Image:
    rng = np.random.default_rng(seed)
    result = base.filter(ImageFilter.GaussianBlur(0.8))
    draw = ImageDraw.Draw(result, "RGBA")
    flower_colours = ((224, 194, 92, 160), (229, 221, 190, 150), (156, 105, 66, 120))
    for _ in range(460):
        x, y = int(rng.integers(0, SIZE)), int(rng.integers(0, SIZE))
        radius = int(rng.integers(1, 5))
        colour = flower_colours[int(rng.integers(0, len(flower_colours)))]
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=colour)
    return result


def safety_pattern(base: Image.Image, seed: int) -> Image.Image:
    rng = np.random.default_rng(seed)
    result = base.filter(ImageFilter.GaussianBlur(2.0))
    draw = ImageDraw.Draw(result, "RGBA")
    for _ in range(1300):
        x, y = int(rng.integers(0, SIZE)), int(rng.integers(0, SIZE))
        shade = int(rng.integers(-15, 16))
        draw.point((x, y), fill=(118 + shade, 93 + shade, 61 + shade, 90))
    return result


def timber_pattern(base: Image.Image, seed: int) -> Image.Image:
    rng = np.random.default_rng(seed)
    result = base.filter(ImageFilter.GaussianBlur(1.2))
    draw = ImageDraw.Draw(result, "RGBA")
    for x in range(0, SIZE, 32):
        draw.rectangle((x, 0, x + 2, SIZE), fill=(45, 30, 20, 130))
        draw.line((x + 5, 0, x + 5, SIZE), fill=(224, 190, 145, 28), width=1)
    for _ in range(22):
        x, y = int(rng.integers(0, SIZE)), int(rng.integers(0, SIZE))
        draw.ellipse((x - 5, y - 2, x + 5, y + 2), outline=(55, 34, 18, 75), width=1)
    return result


def synthesize(role: str, crop: Image.Image, seed: int) -> Image.Image:
    base = stationary_base(crop, role, seed)
    if role == "paver":
        return paver_pattern(base, seed)
    if role == "lawn":
        return lawn_pattern(base)
    if role == "asphalt":
        return asphalt_pattern(base, seed)
    if role == "planting":
        return planting_pattern(base, seed)
    if role == "safety":
        return safety_pattern(base, seed)
    if role == "timber":
        return timber_pattern(base, seed)
    raise ValueError(role)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--schedule", type=Path, default=SCHEDULE_PATH)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    schedule = json.loads(args.schedule.read_text(encoding="utf-8"))
    source_path = REPO_ROOT / schedule["source"]
    if args.dry_run:
        print(f"source={source_path}")
        print(f"method={schedule['method']} api_calls=0 materials={len(schedule['materials'])}")
        return
    source = Image.open(source_path).convert("RGB")
    manifest = {
        "schemaVersion": 1,
        "skin": schedule["skin"],
        "source": schedule["source"],
        "method": schedule["method"],
        "apiCalls": 0,
        "sourcePixelsProjected": False,
        "materials": {},
    }
    for index, role in enumerate(ROLES):
        spec = schedule["materials"][role]
        pixels = crop_pixels(source, spec["crop"])
        crop = source.crop(pixels)
        albedo = synthesize(role, crop, 3011 + index * 503)
        normal = derive_normal(albedo, float(spec["normalStrength"]))
        roughness = derive_roughness(albedo, float(spec["roughness"]))
        ao = derive_ao(albedo)
        role_dir = args.out / role
        role_dir.mkdir(parents=True, exist_ok=True)
        crop.save(role_dir / "source_crop.jpg", quality=92)
        albedo.save(role_dir / "albedo.jpg", quality=92, optimize=True)
        normal.save(role_dir / "normal.png", optimize=True)
        roughness.save(role_dir / "roughness.jpg", quality=90, optimize=True)
        ao.save(role_dir / "ao.jpg", quality=90, optimize=True)
        manifest["materials"][role] = {
            "cropNormalized": spec["crop"],
            "cropPixels": pixels,
            "metresPerTile": spec["metresPerTile"],
            "files": {
                "sourceCrop": f"{role}/source_crop.jpg",
                **{name: f"{role}/{name}.{'png' if name == 'normal' else 'jpg'}" for name in ("albedo", "normal", "roughness", "ao")},
            },
        }
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"wrote {args.out / 'manifest.json'}")


if __name__ == "__main__":
    main()
