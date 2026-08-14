"""Prepare deterministic, illumination-neutral intrinsic materials for Building 9."""
from __future__ import annotations

import hashlib
import json
import math
import os
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[2]
TOOL_DIR = Path(__file__).resolve().parent
OUT = TOOL_DIR / "sticker_assets/brutalist_heroic_v98"
REFERENCES = {
    "frontend/public/archetypes/buildings/brutalist_institutional/variant_0.png": "955d4d45a2148325e2529d02139192c47080210d304bbc0ad856c50b9ef2abbc",
    "frontend/public/archetypes/buildings/brutalist_institutional/variant_0_angle_60.jpg": "ab69b3ddf450414c39d8fbb3c2e4886ec6748b0d02c6c2d751f000c2b456031b",
    "frontend/public/archetypes/buildings/brutalist_institutional/variant_0_angle_90.jpg": "427226ea95af68f6e54c0302896ca42dd8cb42167294f0396465cec801317bd5",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def clamp(value: float) -> int:
    return max(0, min(255, round(value)))


def atomic_save(image: Image.Image, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(f".{target.name}.tmp.png")
    image.convert("RGB").save(temporary, format="PNG", compress_level=9, optimize=False)
    os.replace(temporary, target)


def noise(base: tuple[int, int, int], seed: int, amplitude: int = 12) -> Image.Image:
    rng = random.Random(seed)
    low = Image.new("RGB", (64, 64))
    pixels = low.load()
    for y in range(64):
        for x in range(64):
            value = rng.randint(-amplitude, amplitude)
            pixels[x, y] = tuple(clamp(channel + value) for channel in base)
    return low.resize((1024, 1024), Image.Resampling.BICUBIC)


def anisotropic_noise(base: tuple[int, int, int], seed: int, amplitude: int) -> Image.Image:
    """Long vertical intrinsic variation without a printed board or panel schedule."""
    rng = random.Random(seed)
    low = Image.new("RGB", (1024, 12))
    pixels = low.load()
    harmonics = [(rng.randrange(3, 29), rng.random() * math.tau, rng.uniform(.12, .42)) for _ in range(8)]
    for y in range(12):
        drift = rng.uniform(-1.0, 1.0)
        for x in range(1024):
            value = sum(math.sin(math.tau * frequency * x / 1024 + phase) * weight
                        for frequency, phase, weight in harmonics)
            value = max(-amplitude, min(amplitude, round(amplitude * (value + drift * .12))))
            pixels[x, y] = tuple(clamp(channel + value) for channel in base)
    return low.resize((1024, 1024), Image.Resampling.BICUBIC).filter(ImageFilter.GaussianBlur(.45))


def seamless_pour_variation(base: tuple[int, int, int], seed: int, amplitude: int = 6) -> Image.Image:
    """Seamless, dephased broad variation without square interpolation cells."""
    rng = random.Random(seed)
    field = Image.new("L", (1024, 1024), 128)
    draw = ImageDraw.Draw(field, "L")
    # Ellipses cross tile boundaries and are repeated at wrapped offsets. Their
    # unequal axes prevent a checker cadence while preserving seamless edges.
    for _ in range(28):
        cx, cy = rng.randrange(1024), rng.randrange(1024)
        rx, ry = rng.randrange(120, 370), rng.randrange(45, 180)
        value = clamp(128 + rng.randint(-amplitude * 4, amplitude * 4))
        for ox in (-1024, 0, 1024):
            for oy in (-1024, 0, 1024):
                draw.ellipse((cx + ox - rx, cy + oy - ry, cx + ox + rx, cy + oy + ry), fill=value)
    field = field.filter(ImageFilter.GaussianBlur(72))
    pixels = field.load()
    image = Image.new("RGB", field.size)
    target = image.load()
    for y in range(1024):
        for x in range(1024):
            delta = (pixels[x, y] - 128) * .28
            target[x, y] = tuple(clamp(channel + delta) for channel in base)
    return image


def concrete(
    path: Path,
    base: tuple[int, int, int],
    seed: int,
    *,
    return_variant: bool = False,
    grain_alpha: float = .44,
    weathering_alpha: int = 12,
) -> None:
    # Broad pour variation and directional shutter-board grain replace the old
    # isotropic sand field. Geometry continues to own joints and openings.
    broad = seamless_pour_variation(base, seed, 6)
    grain = anisotropic_noise(base, seed + 17, 9)
    image = Image.blend(broad, grain, grain_alpha)
    draw = ImageDraw.Draw(image, "RGBA")
    rng = random.Random(seed + 90)
    for _ in range(46):
        x = rng.randrange(1024)
        width = rng.choice((1, 1, 2))
        shade = rng.choice(((54, 51, 46, 11), (238, 232, 218, 9)))
        y0 = rng.randrange(-180, 80)
        y1 = min(1024, y0 + rng.randrange(560, 1260))
        draw.line((x, y0, x + rng.choice((-2, -1, 0, 1, 2)), y1), fill=shade, width=width)
    # Sparse, soft construction weathering; deliberately non-grid and too
    # diffuse to become printed geometry.
    weather = Image.new("RGBA", image.size, (0, 0, 0, 0))
    weather_draw = ImageDraw.Draw(weather, "RGBA")
    for _ in range(10):
        x = rng.randrange(1024)
        y = rng.randrange(1024)
        weather_draw.ellipse((x - 30, y - 120, x + 30, y + 120), fill=(62, 58, 51, weathering_alpha))
    image = Image.alpha_composite(image.convert("RGBA"), weather.filter(ImageFilter.GaussianBlur(42))).convert("RGB")
    if return_variant:
        draw = ImageDraw.Draw(image, "RGBA")
        draw.rectangle((0, 0, 1024, 1024), fill=(61, 68, 72, 10))
    atomic_save(image, path)


def membrane(path: Path, base: tuple[int, int, int], seed: int, *, court: bool = False) -> None:
    image = noise(base, seed, 4).filter(ImageFilter.GaussianBlur(14))
    rng = random.Random(seed + 23)
    weather = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(weather, "RGBA")
    for _ in range(18 if court else 12):
        x, y = rng.randrange(1024), rng.randrange(1024)
        rx, ry = rng.randrange(35, 120), rng.randrange(22, 85)
        draw.ellipse((x - rx, y - ry, x + rx, y + ry), fill=(48, 53, 54, rng.randrange(7, 17)))
    weather = weather.filter(ImageFilter.GaussianBlur(34 if court else 48))
    atomic_save(Image.alpha_composite(image.convert("RGBA"), weather).convert("RGB"), path)


def metal(path: Path, base: tuple[int, int, int], seed: int, *, vertical: bool = False) -> None:
    image = noise(base, seed, 6)
    draw = ImageDraw.Draw(image, "RGBA")
    if vertical:
        for x in range(0, 1024, 48):
            draw.line((x, 0, x, 1024), fill=(235, 224, 203, 25), width=2)
            draw.line((x + 4, 0, x + 4, 1024), fill=(32, 29, 25, 28), width=2)
    atomic_save(image, path)


def glass(path: Path) -> None:
    image = Image.new("RGB", (1024, 1024), (96, 111, 117))
    draw = ImageDraw.Draw(image)
    for y in range(1024):
        amount = y / 1023
        color = (clamp(112 - 27 * amount), clamp(128 - 28 * amount), clamp(134 - 27 * amount))
        draw.line((0, y, 1024, y), fill=color)
    # Broad neutral optical variation; no horizon, mullion, or architecture.
    overlay = noise((101, 116, 122), 91, 5).filter(ImageFilter.GaussianBlur(34))
    atomic_save(Image.blend(image, overlay, .18), path)


def atlas(path: Path, seed: int, *, ground: bool) -> None:
    image = Image.new("RGB", (2048, 1024), (28, 31, 32))
    rng = random.Random(seed)
    for row in range(2):
        for col in range(4):
            x0, y0 = col * 512, row * 512
            base = (29 + rng.randrange(8), 32 + rng.randrange(8), 33 + rng.randrange(8))
            cell = noise(base, seed * 19 + row * 4 + col, 3).resize((512, 512), Image.Resampling.LANCZOS)
            glow = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
            glow_draw = ImageDraw.Draw(glow, "RGBA")
            # One broad, low-authority occupied wash per cell. Soft edges and
            # irregular centres avoid printed windows, bands, or horizons.
            cx = rng.randrange(150, 363)
            cy = rng.randrange(160, 353)
            rx = rng.randrange(100, 205)
            ry = rng.randrange(90, 190)
            warm = (82 + rng.randrange(14), 73 + rng.randrange(12), 59 + rng.randrange(10), 24 if ground else 17)
            glow_draw.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), fill=warm)
            cell = Image.alpha_composite(cell.convert("RGBA"), glow.filter(ImageFilter.GaussianBlur(74))).convert("RGB")
            image.paste(cell, (x0, y0))
    atomic_save(image, path)


def main() -> None:
    for relative, expected in REFERENCES.items():
        path = ROOT / relative
        if not path.is_file() or digest(path) != expected:
            raise ValueError(f"exact reference mismatch: {relative}")
    OUT.mkdir(parents=True, exist_ok=True)
    creators = {
        "boardformed_concrete_front_intrinsic.png": lambda p: concrete(p, (168, 160, 143), 10),
        "boardformed_concrete_return_intrinsic.png": lambda p: concrete(p, (153, 151, 141), 11, return_variant=True),
        "deep_concrete_reveal_intrinsic.png": lambda p: concrete(p, (116, 117, 113), 12, return_variant=True, grain_alpha=.20, weathering_alpha=7),
        "weathered_concrete_soffit_intrinsic.png": lambda p: concrete(p, (123, 124, 120), 13, return_variant=True, grain_alpha=.18, weathering_alpha=8),
        "pale_concrete_coping_intrinsic.png": lambda p: concrete(p, (182, 181, 174), 14, grain_alpha=.16, weathering_alpha=5),
        "dark_bronze_joinery_intrinsic.png": lambda p: metal(p, (56, 52, 45), 20, vertical=True),
        "physical_neutral_glass_intrinsic.png": glass,
        "ground_public_interior_atlas.png": lambda p: atlas(p, 31, ground=True),
        "upper_institutional_interior_atlas.png": lambda p: atlas(p, 32, ground=False),
        "roof_membrane_intrinsic.png": lambda p: membrane(p, (169, 173, 174), 40),
        "sunken_roof_court_intrinsic.png": lambda p: membrane(p, (91, 96, 98), 41, court=True),
        "roof_perimeter_flashing_intrinsic.png": lambda p: metal(p, (137, 138, 134), 42),
        "aged_service_metal_intrinsic.png": lambda p: metal(p, (118, 119, 114), 43, vertical=True),
    }
    for name, creator in creators.items():
        creator(OUT / name)
    assets = {}
    for path in sorted(OUT.glob("*.png")):
        with Image.open(path) as image:
            if image.mode != "RGB":
                raise ValueError(path)
            size = list(image.size)
        assets[path.name] = {
            "path": path.relative_to(ROOT).as_posix(),
            "sha256": digest(path),
            "mode": "RGB",
            "size": size,
            "semantic_exclusions": [
                "printed openings", "printed frames", "printed panel joints",
                "directional lighting", "reflection horizon", "text",
            ],
        }
    provenance = {
        "schema": "siteforge.intrinsic-sticker-assets@1",
        "family": "brutalist_heroic_v98",
        "reference_sha256": REFERENCES,
        "metric_concrete_tile_m": 2.0,
        "assets": assets,
    }
    temporary = OUT / ".provenance.tmp"
    temporary.write_text(json.dumps(provenance, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, OUT / "provenance.json")


if __name__ == "__main__":
    main()
