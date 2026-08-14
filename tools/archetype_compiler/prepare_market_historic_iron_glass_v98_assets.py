"""Prepare deterministic intrinsic Sticker Method assets for Building 10."""
from __future__ import annotations

import hashlib
import json
import math
import os
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent / "sticker_assets/market_historic_iron_glass_v98"
REFERENCES = {
    "frontend/public/archetypes/buildings/food_hall_market_hall/variant_0.png": {
        "sha256": "0f04fa934c3b2883f82b3a27ba6883639aff8ab57a065e6b11fbe9c1afe13659",
        "size": [2752, 1536],
        "conditioning_crop_bounds_px": [0, 0, 2752, 1536],
    },
    "frontend/public/archetypes/buildings/food_hall_market_hall/variant_0_angle_60.jpg": {
        "sha256": "e504ab5a6c2af9141b0445d560a77d560d96b5e826949fec9be380f4d58d4c6a",
        "size": [1376, 768],
        "conditioning_crop_bounds_px": [0, 0, 1376, 768],
    },
    "frontend/public/archetypes/buildings/food_hall_market_hall/variant_0_angle_90.jpg": {
        "sha256": "af24f5150a12d417f07ae2fd5eab1c0037b984266b70ebb763fd60880dfa6be0",
        "size": [1376, 768],
        "conditioning_crop_bounds_px": [0, 0, 1376, 768],
    },
}
EXCLUSIONS = [
    "printed structural grids",
    "printed openings",
    "printed frames or mullions",
    "printed ironwork silhouettes",
    "printed roof ribs or seams",
    "directional lighting",
    "cast shadows",
    "reflection horizon",
    "text or signage",
]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def clamp(value: float) -> int:
    return max(0, min(255, round(value)))


def atomic_save(image: Image.Image, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(f".{target.name}.tmp.png")
    image.convert("RGB").save(temporary, format="PNG", compress_level=9, optimize=False)
    os.replace(temporary, target)


def soft_noise(base: tuple[int, int, int], seed: int, amplitude: int = 8, size: int = 1024) -> Image.Image:
    rng = random.Random(seed)
    low = Image.new("RGB", (64, 64))
    pixels = low.load()
    for y in range(64):
        for x in range(64):
            delta = rng.randint(-amplitude, amplitude)
            pixels[x, y] = tuple(clamp(channel + delta) for channel in base)
    return low.resize((size, size), Image.Resampling.BICUBIC).filter(ImageFilter.GaussianBlur(1.2))


def brick(path: Path, base: tuple[int, int, int], seed: int) -> None:
    image = soft_noise(base, seed, 8)
    draw = ImageDraw.Draw(image, "RGBA")
    rng = random.Random(seed + 91)
    course = 32
    for row, y in enumerate(range(0, 1025, course)):
        draw.line((0, y, 1024, y), fill=(211, 199, 176, 126), width=2)
        phase = 0 if row % 2 == 0 else 48
        for x in range(phase, 1025, 96):
            draw.line((x, y, x, min(1024, y + course)), fill=(204, 191, 169, 100), width=2)
    # Fine intrinsic fired-clay variation, never an opening or lighting cue.
    for _ in range(180):
        x, y = rng.randrange(1024), rng.randrange(1024)
        color = rng.choice(((75, 45, 31), (196, 116, 76), (109, 65, 42)))
        draw.ellipse((x - 6, y - 2, x + 6, y + 2), fill=(*color, rng.randrange(5, 17)))
    atomic_save(image, path)


def stone(path: Path, base: tuple[int, int, int], seed: int, weathered: bool = False) -> None:
    image = soft_noise(base, seed, 7 if weathered else 5)
    if weathered:
        rng = random.Random(seed + 31)
        wash = Image.new("RGBA", image.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(wash, "RGBA")
        for _ in range(22):
            x, y = rng.randrange(1024), rng.randrange(1024)
            rx, ry = rng.randrange(35, 150), rng.randrange(18, 90)
            draw.ellipse((x - rx, y - ry, x + rx, y + ry), fill=(74, 71, 62, rng.randrange(4, 13)))
        image = Image.alpha_composite(image.convert("RGBA"), wash.filter(ImageFilter.GaussianBlur(42))).convert("RGB")
    atomic_save(image, path)


def metal(path: Path, base: tuple[int, int, int], seed: int, patina: tuple[int, int, int] | None = None) -> None:
    image = soft_noise(base, seed, 5)
    rng = random.Random(seed + 13)
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay, "RGBA")
    for _ in range(70):
        x, y = rng.randrange(1024), rng.randrange(1024)
        length = rng.randrange(10, 80)
        color = (220, 215, 192, rng.randrange(3, 11))
        draw.line((x, y, min(1024, x + length), y + rng.choice((-1, 0, 1))), fill=color, width=1)
    if patina:
        for _ in range(28):
            x, y = rng.randrange(1024), rng.randrange(1024)
            radius = rng.randrange(12, 70)
            draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=(*patina, rng.randrange(3, 12)))
    atomic_save(Image.alpha_composite(image.convert("RGBA"), overlay.filter(ImageFilter.GaussianBlur(.35))).convert("RGB"), path)


def slate(path: Path) -> None:
    image = soft_noise((72, 77, 77), 90, 10)
    rng = random.Random(9090)
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay, "RGBA")
    # Fine mineral cleavage and lichen flecks only; the physical roof panels
    # remain responsible for courses, laps and edges.
    for _ in range(260):
        x, y = rng.randrange(1024), rng.randrange(1024)
        length = rng.randrange(5, 26)
        draw.line((x, y, min(1023, x + length), y + rng.choice((-1, 0, 1))),
                  fill=rng.choice(((30, 37, 39, 32), (137, 138, 118, 24), (82, 105, 94, 27))), width=1)
    atomic_save(Image.alpha_composite(image.convert("RGBA"), overlay).convert("RGB"), path)


def zinc(path: Path) -> None:
    image = soft_noise((158, 165, 162), 91, 7)
    rng = random.Random(9191)
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay, "RGBA")
    # Directional rolling grain and dispersed oxidation distinguish zinc from
    # slate without printing standing seams or geometry into the skin.
    for _ in range(150):
        x, y = rng.randrange(1024), rng.randrange(1024)
        length = rng.randrange(18, 100)
        draw.line((x, y, x + rng.choice((-1, 0, 1)), min(1023, y + length)),
                  fill=(222, 229, 224, rng.randrange(8, 19)), width=1)
    for _ in range(34):
        x, y = rng.randrange(1024), rng.randrange(1024)
        radius = rng.randrange(16, 78)
        draw.ellipse((x - radius, y - radius, x + radius, y + radius),
                     fill=(87, 130, 116, rng.randrange(7, 17)))
    atomic_save(Image.alpha_composite(image.convert("RGBA"), overlay.filter(ImageFilter.GaussianBlur(.5))).convert("RGB"), path)


def wood(path: Path) -> None:
    image = soft_noise((139, 91, 52), 51, 7)
    draw = ImageDraw.Draw(image, "RGBA")
    for x in range(0, 1024, 19):
        offset = round(3 * math.sin(x * .071))
        draw.line((x, 0, x + offset, 1024), fill=(77, 43, 25, 28), width=1)
    atomic_save(image, path)


def blank_signboard(path: Path) -> None:
    atomic_save(soft_noise((38, 42, 39), 61, 2), path)


def herringbone(path: Path) -> None:
    image = soft_noise((141, 83, 57), 62, 5)
    draw = ImageDraw.Draw(image, "RGBA")
    mortar = (201, 178, 150, 88)
    # Interlocking chevrons and staggered short joints create the visual bond
    # of narrow herringbone pavers without a cross-hatched structural grid.
    for y in range(-64, 1088, 64):
        offset = 32 if (y // 64) % 2 else 0
        for x in range(-96 + offset, 1088, 64):
            draw.line((x, y, x + 32, y + 32, x + 64, y), fill=mortar, width=2)
            draw.line((x + 16, y + 16, x + 1, y + 31), fill=mortar, width=2)
            draw.line((x + 48, y + 16, x + 63, y + 31), fill=mortar, width=2)
    atomic_save(image, path)


def glass(path: Path, base: tuple[int, int, int], seed: int, curved: bool = False) -> None:
    image = soft_noise(base, seed, 4)
    optical = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(optical, "RGBA")
    # Broad, low-authority waviness only; no horizon, rib, pane boundary or reflection.
    for index in range(9 if curved else 6):
        y = 70 + index * (106 if curved else 155)
        points = [(x, y + round(9 * math.sin(x / 145 + index * .73))) for x in range(0, 1025, 32)]
        draw.line(points, fill=(210, 226, 218, 8 if curved else 5), width=9)
    atomic_save(Image.alpha_composite(image.convert("RGBA"), optical.filter(ImageFilter.GaussianBlur(22))).convert("RGB"), path)


def atlas(path: Path, seed: int, ground: bool) -> None:
    result = Image.new("RGB", (2048, 1024), (122, 92, 66) if ground else (94, 82, 65))
    rng = random.Random(seed)
    for row in range(2):
        for col in range(4):
            index = row * 4 + col
            base = ((117 + rng.randrange(14), 87 + rng.randrange(12), 62 + rng.randrange(10)) if ground
                    else (90 + rng.randrange(11), 78 + rng.randrange(10), 62 + rng.randrange(8)))
            cell = soft_noise(base, seed * 37 + index, 2, 512)
            cues = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
            draw = ImageDraw.Draw(cues, "RGBA")
            # Soft market occupancy cues: counters/tables/people, never window frames or signs.
            for _ in range(5 if ground else 4):
                cx, cy = rng.randrange(70, 442), rng.randrange(90, 430)
                rx, ry = rng.randrange(18, 62), rng.randrange(22, 76)
                warm = ((215, 151, 82, rng.randrange(19, 35)) if ground
                        else (184, 132, 83, rng.randrange(14, 27)))
                draw.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), fill=warm)
            for _ in range(5 if ground else 4):
                cx, cy = rng.randrange(100, 412), rng.randrange(110, 400)
                draw.ellipse((cx - 10, cy - 20, cx + 10, cy + 20), fill=(45, 39, 34, 31))
            cell = Image.alpha_composite(cell.convert("RGBA"), cues.filter(ImageFilter.GaussianBlur(13))).convert("RGB")
            result.paste(cell, (col * 512, row * 512))
    atomic_save(result, path)


def main() -> None:
    for relative, record in REFERENCES.items():
        source = ROOT / relative
        if not source.is_file() or digest(source) != record["sha256"]:
            raise ValueError(f"exact reference mismatch: {relative}")
        with Image.open(source) as image:
            if list(image.size) != record["size"]:
                raise ValueError(f"reference dimension mismatch: {relative}")
        x0, y0, x1, y1 = record["conditioning_crop_bounds_px"]
        if not (0 <= x0 < x1 <= record["size"][0] and 0 <= y0 < y1 <= record["size"][1]):
            raise ValueError(f"out-of-bounds conditioning crop: {relative}")
    creators = {
        "warm_brick_front_intrinsic.png": lambda p: brick(p, (150, 83, 57), 10),
        "warm_brick_return_intrinsic.png": lambda p: brick(p, (144, 79, 55), 11),
        "warm_brick_rear_intrinsic.png": lambda p: brick(p, (137, 75, 53), 12),
        "pale_ashlar_intrinsic.png": lambda p: stone(p, (198, 190, 172), 20),
        "weathered_stone_plinth_intrinsic.png": lambda p: stone(p, (169, 162, 146), 21, True),
        "heritage_green_cast_iron_intrinsic.png": lambda p: metal(p, (58, 92, 75), 30, (91, 128, 108)),
        "dark_ornate_rail_intrinsic.png": lambda p: metal(p, (42, 69, 57), 31, (76, 108, 89)),
        "aged_hardware_intrinsic.png": lambda p: metal(p, (67, 68, 62), 32),
        "heritage_green_gutter_intrinsic.png": lambda p: metal(p, (45, 72, 61), 33, (65, 96, 79)),
        "warm_oak_stall_intrinsic.png": wood,
        "pale_counter_stone_intrinsic.png": lambda p: stone(p, (210, 205, 192), 52),
        "blank_dark_signboard_intrinsic.png": blank_signboard,
        "herringbone_market_paver_intrinsic.png": herringbone,
        "physical_vertical_low_iron_glass_intrinsic.png": lambda p: glass(p, (105, 128, 122), 70),
        "physical_curved_roof_glass_intrinsic.png": lambda p: glass(p, (157, 171, 163), 71, True),
        "ridge_lantern_glass_intrinsic.png": lambda p: glass(p, (139, 158, 151), 72),
        "rooflight_glass_intrinsic.png": lambda p: glass(p, (130, 149, 145), 73),
        "ground_market_interior_atlas.png": lambda p: atlas(p, 80, True),
        "gallery_market_interior_atlas.png": lambda p: atlas(p, 81, False),
        "dark_cavern_backing_intrinsic.png": lambda p: atomic_save(soft_noise((34, 32, 28), 82, 2), p),
        "weathered_slate_intrinsic.png": slate,
        "aged_zinc_roof_intrinsic.png": zinc,
        "flashing_coping_intrinsic.png": lambda p: metal(p, (158, 162, 158), 92, (126, 148, 139)),
        "aged_service_metal_intrinsic.png": lambda p: metal(p, (111, 114, 110), 93),
        "warm_copper_lamp_intrinsic.png": lambda p: metal(p, (151, 90, 53), 94, (91, 124, 91)),
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
            "semantic_exclusions": EXCLUSIONS,
        }
    provenance = {
        "schema": "siteforge.intrinsic-sticker-assets@1",
        "family": "market_historic_iron_glass_v98",
        "identity_authority": "three_exact_variant_0_images",
        "reference_evidence": REFERENCES,
        "canonical_dimensions_m": {"length": 60.0, "width": 45.0},
        "registered_asset_groups": {
            "brick": ["warm_brick_front_intrinsic.png", "warm_brick_return_intrinsic.png", "warm_brick_rear_intrinsic.png"],
            "physical_glass": ["physical_vertical_low_iron_glass_intrinsic.png", "physical_curved_roof_glass_intrinsic.png", "ridge_lantern_glass_intrinsic.png", "rooflight_glass_intrinsic.png"],
            "interior_atlases": ["ground_market_interior_atlas.png", "gallery_market_interior_atlas.png"],
        },
        "metric_contract": {"brick_course_m": 0.075, "paver_module_m": 0.24, "continuous_resize_allowed": False},
        "atlas_contract": {"columns": 4, "rows": 2, "cell_px": [512, 512], "printed_frames_allowed": False},
        "assets": assets,
    }
    temporary = OUT / ".provenance.tmp"
    temporary.write_text(json.dumps(provenance, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, OUT / "provenance.json")


if __name__ == "__main__":
    main()
