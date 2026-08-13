"""Prepare deterministic intrinsic assets for the image-locked Halifax V98 pilot.

Path A is authoritative: the exact variant-0 images describe a two-storey
Italianate brick commercial block with a flat membrane roof. Catalogue prose
about ironstone, loading doors, a gable roof and a hoist beam is rejected.
"""
from __future__ import annotations

import hashlib
import json
import os
import random
import time
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageStat


REPO = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent / "sticker_assets/halifax_waterfront_warehouse_v98"
REF = REPO / "frontend/public/archetypes/buildings/halifax-waterfront-warehouse"
STREET, OBLIQUE, AERIAL = (REF / "variant_0.png", REF / "variant_0_angle_60.jpg", REF / "variant_0_angle_90.jpg")
SIZE = 1024
EXPECTED_REFERENCE_HASHES = {
    STREET: "ad42ba20d97281337b2a501af57cee64418b3df0486b3fa6c881cd317ef4784c",
    OBLIQUE: "9b2a732476ea85a955d4047463bf7ea34dfed211e8e0f69fdd5b6b9c1ee49efb",
    AERIAL: "721b8ef5aff6c9e45b9f1bd0beb6df81219675471aece32fc4826f219a1bcdf3",
}


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _repo(path: Path) -> str:
    return path.relative_to(REPO).as_posix()


def _clamp(value: float) -> int:
    return max(0, min(255, round(value)))


def _mix(a: tuple[int, int, int], b: tuple[int, int, int], amount: float) -> tuple[int, int, int]:
    return tuple(_clamp(x * (1 - amount) + y * amount) for x, y in zip(a, b))


def assert_crop(path: Path, box: tuple[int, int, int, int]) -> tuple[int, int, int, int]:
    with Image.open(path) as image:
        width, height = image.size
    left, top, right, bottom = box
    if not (0 <= left < right <= width and 0 <= top < bottom <= height):
        raise ValueError(f"out-of-bounds crop {box} for {path.name} ({width}x{height})")
    return box


def _median(path: Path, box: tuple[int, int, int, int]) -> tuple[int, int, int]:
    with Image.open(path) as image:
        crop = image.convert("RGB").crop(assert_crop(path, box))
    return tuple(round(value) for value in ImageStat.Stat(crop).median)


def _noise(base: tuple[int, int, int], seed: int, amplitude: int = 12, scale: int = 96) -> Image.Image:
    rng = random.Random(seed)
    small = Image.new("RGB", (scale, scale))
    small.putdata([tuple(_clamp(c + rng.uniform(-amplitude, amplitude)) for c in base) for _ in range(scale * scale)])
    return small.resize((SIZE, SIZE), Image.Resampling.BICUBIC)


def _luma_noise(base: tuple[int, int, int], seed: int, amplitude: int, scale: int) -> Image.Image:
    """Neutral correlated variation that cannot create RGB/iridescent bands."""
    rng = random.Random(seed)
    small = Image.new("RGB", (scale, scale))
    pixels = []
    for _ in range(scale * scale):
        delta = rng.uniform(-amplitude, amplitude)
        pixels.append(tuple(_clamp(channel + delta) for channel in base))
    small.putdata(pixels)
    return small.resize((SIZE, SIZE), Image.Resampling.BICUBIC)


def _save(image: Image.Image, target: Path) -> None:
    # Assets can be consumed by Blender or pytest while a preparation pass is
    # running. Publish atomically so readers see a complete old or new PNG.
    temporary = target.with_name(f".{target.stem}.{os.getpid()}.tmp.png")
    image.convert("RGB").save(temporary, format="PNG", optimize=True)
    for attempt in range(12):
        try:
            temporary.replace(target)
            break
        except PermissionError:
            if attempt == 11:
                temporary.unlink(missing_ok=True)
                raise
            time.sleep(.10 * (attempt + 1))


def _brick(target: Path, base: tuple[int, int, int], seed: int, *, mirrored: bool = False) -> None:
    rng = random.Random(seed)
    mortar = _mix(base, (174, 164, 146), .58)
    image = Image.new("RGB", (SIZE, SIZE), mortar)
    draw = ImageDraw.Draw(image)
    # A slightly smaller, calmer running bond preserves masonry scale without
    # turning the facade into orange visual noise at street-view distance.
    course, unit, joint = 34, 96, 4
    for row, y in enumerate(range(-course, SIZE + course, course)):
        offset = -unit // 2 if row % 2 else 0
        for x in range(offset - unit, SIZE + unit, unit):
            delta, red = rng.randint(-12, 12), rng.randint(-3, 5)
            colour = (_clamp(base[0] + delta + red), _clamp(base[1] + delta * .62), _clamp(base[2] + delta * .48))
            draw.rounded_rectangle((x + joint, y + joint, x + unit - joint, y + course - joint), radius=2, fill=colour)
            for _ in range(2):
                px, py = rng.randint(x + 8, x + unit - 8), rng.randint(y + 7, y + course - 7)
                draw.ellipse((px, py, px + rng.randint(2, 8), py + rng.randint(1, 3)), fill=_mix(colour, (75, 54, 40), rng.uniform(.08, .22)))
    if mirrored:
        image = image.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    _save(image.filter(ImageFilter.GaussianBlur(.18)), target)


def _mineral(target: Path, base: tuple[int, int, int], seed: int, *, plinth: bool) -> None:
    rng = random.Random(seed)
    fine = _luma_noise(base, seed, 9 if plinth else 5, 96)
    coarse = _luma_noise(base, seed + 701, 15 if plinth else 11, 12).filter(ImageFilter.GaussianBlur(7))
    image = Image.blend(fine, coarse, .38 if plinth else .48).convert("RGBA")
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0)); draw = ImageDraw.Draw(overlay)
    for _ in range(950 if plinth else 620):
        x, y = rng.randrange(SIZE), rng.randrange(SIZE); r = rng.randrange(1, 9)
        tone = rng.choice((82, 112, 158, 196))
        draw.ellipse((x-r, y-r, x+r, y+r), fill=(tone, tone, tone, rng.randrange(2, 10)))
    _save(Image.alpha_composite(image, overlay.filter(ImageFilter.GaussianBlur(1.1))), target)


def _painted_joinery(target: Path, base: tuple[int, int, int], seed: int, *, hardware: bool = False) -> None:
    rng = random.Random(seed); image = _noise(base, seed, 5).convert("RGBA")
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0)); draw = ImageDraw.Draw(overlay)
    for _ in range(620):
        x, y = rng.randrange(SIZE), rng.randrange(SIZE)
        draw.line((x, y, min(SIZE, x + rng.randrange(3, 34)), y), fill=(191, 172, 130, rng.randrange(2, 9)), width=1)
    if hardware:
        for _ in range(260):
            x, y = rng.randrange(SIZE), rng.randrange(SIZE)
            draw.ellipse((x, y, x + rng.randrange(1, 5), y + rng.randrange(1, 4)), fill=(113, 78, 45, rng.randrange(3, 12)))
    _save(Image.alpha_composite(image, overlay).filter(ImageFilter.GaussianBlur(.25)), target)


def _patina(target: Path, base: tuple[int, int, int], seed: int) -> None:
    rng = random.Random(seed); image = _noise(base, seed, 8).convert("RGBA")
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0)); draw = ImageDraw.Draw(overlay)
    colours = ((84, 121, 117), (107, 139, 132), (126, 119, 94), (73, 104, 105))
    for _ in range(620):
        x, y = rng.randrange(SIZE), rng.randrange(SIZE); rx, ry = rng.randrange(8, 50), rng.randrange(7, 38)
        draw.ellipse((x-rx, y-ry, x+rx, y+ry), fill=rng.choice(colours) + (rng.randrange(4, 14),))
    _save(Image.alpha_composite(image, overlay.filter(ImageFilter.GaussianBlur(8))), target)


def _glass(target: Path, base: tuple[int, int, int], seed: int, *, storefront: bool) -> None:
    # Low-contrast optical field only: no horizon, mullion, frame or reflection stripe.
    image = _noise(base, seed, 3 if storefront else 4, 72).filter(ImageFilter.GaussianBlur(2.2))
    veil = Image.new("RGB", image.size, (151, 158, 158) if storefront else (140, 150, 153))
    _save(Image.blend(image, veil, .26), target)


def _membrane(target: Path, base: tuple[int, int, int], seed: int, *, perimeter: bool) -> None:
    rng = random.Random(seed); image = _noise(base, seed, 14 if not perimeter else 9).convert("RGBA")
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0)); draw = ImageDraw.Draw(overlay)
    for _ in range(900):
        x, y = rng.randrange(SIZE), rng.randrange(SIZE); r = rng.randrange(2, 22)
        draw.ellipse((x-r, y-r, x+r, y+r), fill=(61, 54, 49, rng.randrange(2, 11)))
    _save(Image.alpha_composite(image, overlay.filter(ImageFilter.GaussianBlur(4.5))), target)


def _metal(target: Path, base: tuple[int, int, int], seed: int) -> None:
    rng = random.Random(seed); image = _noise(base, seed, 8).convert("RGBA")
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0)); draw = ImageDraw.Draw(overlay)
    for _ in range(480):
        x, y = rng.randrange(SIZE), rng.randrange(SIZE)
        draw.ellipse((x, y, x + rng.randrange(1, 9), y + rng.randrange(1, 5)), fill=(95, 79, 61, rng.randrange(3, 12)))
    _save(Image.alpha_composite(image, overlay.filter(ImageFilter.GaussianBlur(.7))), target)


def _interior_atlas(target: Path, seed: int, *, retail: bool) -> None:
    rng = random.Random(seed); atlas = Image.new("RGB", (2048, 1024))
    for index in range(8):
        dark = (45 + index % 3 * 3, 48 + index % 2 * 3, 49 + index % 4)
        card = Image.new("RGB", (512, 512), dark); draw = ImageDraw.Draw(card, "RGBA")
        draw.rectangle((0, 0, 512, 72), fill=(29, 31, 31, 255))
        for light in range(4):
            cx = 62 + light * 130 + rng.randrange(-9, 10)
            draw.ellipse((cx-11, 36, cx+11, 44), fill=(157, 151, 132, 70))
        if retail:
            for shelf in range(3):
                x = 34 + shelf * 165 + rng.randrange(-8, 9)
                draw.rectangle((x, 150, x+125, 355), fill=(47, 43, 38, 225))
                for y in range(174, 350, 38):
                    draw.line((x+6, y, x+119, y), fill=(92, 91, 83, 80), width=3)
                    for item in range(5):
                        px=x+12+item*22+rng.randrange(-2,3); tone=82+rng.randrange(-10,14); draw.rectangle((px,y-18,px+10,y-2),fill=(tone,tone-2,tone-5,58))
        else:
            for desk in range(3):
                x=38+desk*165+rng.randrange(-10,11); y=286+rng.randrange(-18,19)
                draw.rectangle((x,y,x+112,y+12),fill=(78,77,72,125)); draw.rectangle((x+37,y-54,x+84,y-8),fill=(25,29,30,190))
                draw.rectangle((x+42,y-49,x+79,y-14),fill=(68,76,77,110))
            for x in (90,350): draw.rectangle((x,140,x+68,260),fill=(38,36,33,215))
        # Neutral veil prevents an interior card from reading as a pasted photograph.
        veil = Image.new("RGB", card.size, (49, 52, 52) if retail else (47, 51, 52))
        card = Image.blend(card.filter(ImageFilter.GaussianBlur(.65)), veil, .38)
        atlas.paste(card, ((index % 4) * 512, (index // 4) * 512))
    _save(atlas, target)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for path, expected in EXPECTED_REFERENCE_HASHES.items():
        if not path.is_file() or _hash(path) != expected:
            raise ValueError(f"exact reference missing or changed: {path}")
    crop_specs = {
        "brick": (STREET, (455, 185, 530, 285)), "stone": (STREET, (562, 195, 612, 510)),
        "joinery": (STREET, (405, 430, 505, 620)), "glass": (STREET, (455, 310, 520, 490)),
        "patina": (OBLIQUE, (730, 165, 1030, 300)), "roof": (AERIAL, (260, 250, 950, 690)),
    }
    sampled = {key: _median(path, box) for key, (path, box) in crop_specs.items()}
    palette = {
        "brick": _mix(sampled["brick"], (151, 102, 84), .74), "stone": _mix(sampled["stone"], (154, 155, 153), .90),
        "plinth": _mix(sampled["stone"], (145, 137, 123), .72), "green": _mix(sampled["joinery"], (35, 55, 47), .84),
        "patina": _mix(sampled["patina"], (108, 137, 134), .86), "glass": _mix(sampled["glass"], (134, 146, 149), .88),
        "roof": _mix(sampled["roof"], (91, 79, 70), .72), "roof_edge": _mix(sampled["roof"], (54, 53, 51), .83),
    }
    outputs = {
        "warm_brick_front": OUT / "warm_brick_front_intrinsic.png", "warm_brick_return": OUT / "warm_brick_return_intrinsic.png",
        "pale_warm_stone": OUT / "pale_warm_stone_intrinsic.png", "weathered_stone_plinth": OUT / "weathered_stone_plinth_intrinsic.png",
        "dark_green_joinery": OUT / "dark_green_joinery_intrinsic.png", "patinated_cornice_metal": OUT / "patinated_green_grey_cornice_intrinsic.png",
        "clear_upper_glass": OUT / "clear_upper_glass_intrinsic.png", "clear_storefront_glass": OUT / "clear_storefront_glass_intrinsic.png",
        "ground_retail_interiors": OUT / "ground_retail_interior_atlas.png", "upper_commercial_interiors": OUT / "upper_commercial_interior_atlas.png",
        "weathered_flat_membrane": OUT / "weathered_flat_membrane_intrinsic.png", "dark_perimeter_membrane": OUT / "dark_perimeter_membrane_intrinsic.png",
        "chimney_brick": OUT / "chimney_brick_intrinsic.png", "chimney_coping": OUT / "chimney_coping_intrinsic.png",
        "aged_galvanized_service_metal": OUT / "aged_galvanized_service_metal_intrinsic.png", "threshold_hardware": OUT / "threshold_hardware_intrinsic.png",
    }
    _brick(outputs["warm_brick_front"], palette["brick"], 980400); _brick(outputs["warm_brick_return"], palette["brick"], 980400, mirrored=True)
    _mineral(outputs["pale_warm_stone"], palette["stone"], 980402, plinth=False); _mineral(outputs["weathered_stone_plinth"], palette["plinth"], 980403, plinth=True)
    _painted_joinery(outputs["dark_green_joinery"], palette["green"], 980404); _patina(outputs["patinated_cornice_metal"], palette["patina"], 980405)
    _glass(outputs["clear_upper_glass"], palette["glass"], 980406, storefront=False); _glass(outputs["clear_storefront_glass"], _mix(palette["glass"], (111, 120, 115), .18), 980407, storefront=True)
    _interior_atlas(outputs["ground_retail_interiors"], 980408, retail=True); _interior_atlas(outputs["upper_commercial_interiors"], 980409, retail=False)
    _membrane(outputs["weathered_flat_membrane"], palette["roof"], 980410, perimeter=False); _membrane(outputs["dark_perimeter_membrane"], palette["roof_edge"], 980411, perimeter=True)
    _brick(outputs["chimney_brick"], _mix(palette["brick"], (135, 86, 59), .22), 980412); _mineral(outputs["chimney_coping"], _mix(palette["stone"], (130, 127, 116), .28), 980413, plinth=True)
    _metal(outputs["aged_galvanized_service_metal"], (142, 145, 139), 980414); _painted_joinery(outputs["threshold_hardware"], (44, 47, 43), 980415, hardware=True)
    records = {}
    for role, path in outputs.items():
        with Image.open(path) as image:
            expected = (2048, 1024) if role in {"ground_retail_interiors", "upper_commercial_interiors"} else (SIZE, SIZE)
            if image.mode != "RGB" or image.size != expected: raise ValueError(f"invalid {role}: {image.mode} {image.size}")
        records[role] = {"path": _repo(path), "sha256": _hash(path), "evidence_class": "constrained_completion",
                         "generation": "deterministic_code_native_exact_palette_conditioned",
                         "contains_printed_modeled_geometry": False, "contains_baked_directional_lighting": False}
    provenance = {
        "schema": "siteforge.sticker-asset-provenance@1", "building": "halifax-waterfront-warehouse--warehouse-privateers-wharf",
        "variant_index": 0, "identity_override": {"path": "A", "authority": "exact_image_locked_two_storey_italianate",
            "rejected_metadata": ["three-and-a-half-storey ironstone warehouse", "gable slate roof", "loading doors", "hoist beam"]},
        "exact_reference_sources": {path.name: {"path": _repo(path), "sha256": expected, "evidence_class": "exact_reference"} for path, expected in EXPECTED_REFERENCE_HASHES.items()},
        "palette_conditioning": {"rule": "fixed bounds-asserted median probes blended toward material priors; no source pixels pasted",
            "crops_px": {key: {"path": _repo(path), "box": list(box)} for key, (path, box) in crop_specs.items()},
            "sampled_rgb": {key: list(value) for key, value in sampled.items()}, "prepared_palette_rgb": {key: list(value) for key, value in palette.items()}},
        "geometry_ownership": ["openings and arch contours", "rustication and quoins", "mullions and sash", "cornice profiles and dentils", "roof/parapet/chimney/service silhouettes"],
        "glass_contract": "No printed mullions, frames, hard horizons, scene reflections or aperture boundaries.",
        "interior_contract": "Separate dark, desaturated, neutral-veiled ground retail and upper commercial 4x2 atlases contain subordinate interior evidence only; no tan stripes or printed facade geometry.",
        "assets": records, "atlas_grid": [4, 2], "post_generation_nonuniform_scale_allowed": False,
        "approval_space": "locked-carrier multi-view renders with all-face semantic audit",
    }
    (OUT / "provenance.json").write_text(json.dumps(provenance, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(OUT), "prepared_assets": len(outputs)}, indent=2))


if __name__ == "__main__":
    main()
