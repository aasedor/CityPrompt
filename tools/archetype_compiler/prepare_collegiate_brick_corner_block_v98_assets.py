"""Prepare deterministic intrinsic Sticker assets for the B8 collegiate brick block.

Exact variant-0 views condition colour and material character only. Geometry owns
openings, floor bands, pilasters, frames, parapets, roof edges and equipment.
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
OUT = Path(__file__).resolve().parent / "sticker_assets/collegiate_brick_corner_block_v98"
REF = REPO / "frontend/public/archetypes/buildings/graduate-family-housing"
STREET = REF / "variant_0.png"
OBLIQUE = REF / "variant_0_angle_60.jpg"
AERIAL = REF / "variant_0_angle_90.jpg"
SIZE = 1024
ATLAS_SIZE = (2048, 1024)
EXPECTED_REFERENCE_HASHES = {
    STREET: "975880325493f35fdae5367aeeccd5648ebe38f57baf5d7b7aa2ce024c17f747",
    OBLIQUE: "3af8854ea010429a2d4cc1c87862b04eb91a93294767467d393b80a41598c4df",
    AERIAL: "21e0c4e9ab7fd36fac73258b6294f492ca4af6424dd0b85c753f8604ef3f2dc5",
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
        return tuple(round(v) for v in ImageStat.Stat(
            image.convert("RGB").crop(assert_crop(path, box))).median)


def _noise(base: tuple[int, int, int], seed: int, amplitude: int, scale: int = 80) -> Image.Image:
    rng = random.Random(seed)
    image = Image.new("RGB", (scale, scale))
    image.putdata([tuple(_clamp(c + rng.uniform(-amplitude, amplitude)) for c in base)
                   for _ in range(scale * scale)])
    return image.resize((SIZE, SIZE), Image.Resampling.BICUBIC)


def _save(image: Image.Image, target: Path) -> None:
    temporary = target.with_name(f".{target.stem}.{os.getpid()}.tmp.png")
    image.convert("RGB").save(temporary, format="PNG", optimize=True)
    for attempt in range(12):
        try:
            os.replace(temporary, target)
            return
        except PermissionError:
            if attempt == 11:
                temporary.unlink(missing_ok=True)
                raise
            time.sleep(.10 * (attempt + 1))


def _atomic_json(data: dict, target: Path) -> None:
    temporary = target.with_name(f".{target.name}.{os.getpid()}.tmp")
    temporary.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, target)


def _brick(target: Path, base: tuple[int, int, int], seed: int, *, mirror: bool = False,
           subdued: bool = False) -> None:
    """Metric running-bond material only; no aperture, band or pilaster imagery."""
    rng = random.Random(seed)
    mortar = _mix(base, (178, 169, 150), .44 if subdued else .35)
    image = Image.new("RGB", (SIZE, SIZE), mortar)
    draw = ImageDraw.Draw(image)
    # A 28 px course at the compiler's 2.4 m tile is 65.6 mm.  The first
    # package used 75 mm courses and read too coarse at street distance.
    course = 28
    brick_w = 88
    for row, y in enumerate(range(-course, SIZE + course, course)):
        offset = -(brick_w // 2) if row % 2 else 0
        for x in range(offset - brick_w, SIZE + brick_w, brick_w):
            delta = rng.randint(-12 if subdued else -15, 11 if subdued else 14)
            colour = tuple(_clamp(c + delta + rng.randint(-2, 2)) for c in base)
            draw.rectangle((x + 2, y + 2, x + brick_w - 2, y + course - 3), fill=colour)
            # Fine fired-clay variation, not lighting.
            for _ in range(3):
                px, py = rng.randint(x + 6, x + brick_w - 6), rng.randint(y + 5, y + course - 6)
                draw.ellipse((px, py, px + rng.randint(1, 4), py + 1), fill=_mix(colour, (92, 67, 48), .14))
    result = image.filter(ImageFilter.GaussianBlur(.28))
    if mirror:
        result = result.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    _save(result, target)


def _mineral(target: Path, base: tuple[int, int, int], seed: int, *, weathered: bool = False) -> None:
    rng = random.Random(seed)
    fine = _noise(base, seed, 5 if not weathered else 8, 100)
    broad = _noise(base, seed + 51, 8 if not weathered else 13, 13).filter(ImageFilter.GaussianBlur(14))
    image = Image.blend(fine, broad, .38).convert("RGBA")
    grain = Image.new("RGBA", image.size, (0, 0, 0, 0)); draw = ImageDraw.Draw(grain)
    for _ in range(1300):
        x, y = rng.randrange(SIZE), rng.randrange(SIZE); r = rng.choice((1, 1, 2, 2, 3))
        d = rng.choice((-17, -10, 9, 14))
        draw.ellipse((x-r, y-r, x+r, y+r), fill=(*( _clamp(c+d) for c in base), rng.randrange(20, 65)))
    if weathered:
        for _ in range(38):
            x, y = rng.randrange(SIZE), rng.randrange(SIZE); rx, ry = rng.randrange(18, 80), rng.randrange(9, 38)
            draw.ellipse((x-rx, y-ry, x+rx, y+ry), fill=(78, 73, 65, rng.randrange(3, 12)))
    _save(Image.alpha_composite(image, grain.filter(ImageFilter.GaussianBlur(.7))), target)


def _metal(target: Path, base: tuple[int, int, int], seed: int, *, weathered: bool = False) -> None:
    rng = random.Random(seed)
    image = _noise(base, seed, 5 if not weathered else 8, 92).convert("RGBA")
    marks = Image.new("RGBA", image.size, (0, 0, 0, 0)); draw = ImageDraw.Draw(marks)
    for _ in range(550 if weathered else 250):
        x, y = rng.randrange(SIZE), rng.randrange(SIZE)
        tone = (77, 69, 57, rng.randrange(2, 10)) if weathered else (212, 197, 166, rng.randrange(2, 7))
        draw.ellipse((x, y, x+rng.randrange(1, 7), y+rng.randrange(1, 4)), fill=tone)
    _save(Image.alpha_composite(image, marks.filter(ImageFilter.GaussianBlur(.55))), target)


def _ribbed_bronze(target: Path, base: tuple[int, int, int], seed: int) -> None:
    """Fine intrinsic rolled-metal ribs, not a structural screen silhouette."""
    rng = random.Random(seed)
    image = _noise(base, seed, 5, 96).convert("RGBA")
    ribs = Image.new("RGBA", image.size, (0, 0, 0, 0)); draw = ImageDraw.Draw(ribs)
    for x in range(0, SIZE, 18):
        draw.rectangle((x, 0, x + 5, SIZE), fill=(35, 28, 23, 48))
        draw.line((x + 6, 0, x + 6, SIZE), fill=(218, 178, 125, 38), width=2)
    for _ in range(380):
        x, y = rng.randrange(SIZE), rng.randrange(SIZE)
        draw.ellipse((x, y, x + rng.randrange(1, 5), y + rng.randrange(1, 3)),
                     fill=(84, 101, 82, rng.randrange(4, 15)))
    _save(Image.alpha_composite(image, ribs.filter(ImageFilter.GaussianBlur(.32))), target)


def _galvanized(target: Path, base: tuple[int, int, int], seed: int, *, darker: bool = False) -> None:
    """Neutral metallic flake variation without a baked light direction."""
    rng = random.Random(seed)
    image = _noise(base, seed, 8 if darker else 10, 80).convert("RGBA")
    marks = Image.new("RGBA", image.size, (0, 0, 0, 0)); draw = ImageDraw.Draw(marks)
    for _ in range(1300):
        x, y = rng.randrange(SIZE), rng.randrange(SIZE)
        radius = rng.choice((1, 1, 2, 3, 5))
        delta = rng.choice((-25, -14, 11, 19))
        colour = tuple(_clamp(c + delta) for c in base)
        draw.ellipse((x-radius, y-radius, x+radius*2, y+radius), fill=(*colour, rng.randrange(18, 58)))
    _save(Image.alpha_composite(image, marks.filter(ImageFilter.GaussianBlur(.45))), target)


def _glass(target: Path, base: tuple[int, int, int], seed: int, *, corner: bool = False) -> None:
    # Physical optical field: broad neutral variance only, never a printed reflection scene.
    field = _noise(base, seed, 3, 72).filter(ImageFilter.GaussianBlur(2.2))
    broad = _noise(_mix(base, (183, 192, 194), .34), seed + 88, 13 if corner else 8, 10)
    # Neutral warm-grey ordinary pane; cooler, more variable oriel pane.  This
    # remains an intrinsic optical field and contains no printed sky horizon.
    veil = Image.new("RGB", field.size, (174, 185, 188) if corner else (187, 191, 188))
    _save(Image.blend(Image.blend(field, broad.filter(ImageFilter.GaussianBlur(18)), .29 if corner else .20),
                      veil, .46), target)


def _gravel(target: Path, base: tuple[int, int, int], seed: int) -> None:
    # Generate a deterministic half-size periodic cell and tile it. This makes
    # separately projected roof carriers meet without a light/dark image edge.
    rng = random.Random(seed); cell_size = SIZE // 2
    base_cell = _noise(base, seed, 7, 96).resize((cell_size, cell_size), Image.Resampling.LANCZOS).convert("RGBA")
    stones = Image.new("RGBA", (cell_size, cell_size), (0, 0, 0, 0)); draw = ImageDraw.Draw(stones)
    for _ in range(2400):
        x, y = rng.randrange(cell_size), rng.randrange(cell_size); r = rng.choice((1, 1, 2, 2, 3, 4))
        d = rng.randint(-30, 27); c = tuple(_clamp(v+d) for v in base)
        for ox in (-cell_size, 0, cell_size):
            for oy in (-cell_size, 0, cell_size):
                draw.ellipse((x-r+ox, y-r+oy, x+r*2+ox, y+r+oy), fill=(*c, rng.randrange(85, 190)))
    cell = Image.alpha_composite(base_cell, stones.filter(ImageFilter.GaussianBlur(.25))).convert("RGB")
    image = Image.new("RGB", (SIZE, SIZE))
    for x in (0, cell_size):
        for y in (0, cell_size): image.paste(cell, (x, y))
    _save(image, target)


def _membrane(target: Path, base: tuple[int, int, int], seed: int, *, path: bool = False) -> None:
    rng = random.Random(seed); image = _noise(base, seed, 6, 88).convert("RGBA")
    wear = Image.new("RGBA", image.size, (0, 0, 0, 0)); draw = ImageDraw.Draw(wear)
    for _ in range(500):
        x, y = rng.randrange(SIZE), rng.randrange(SIZE); rx, ry = rng.randrange(3, 25), rng.randrange(2, 12)
        draw.ellipse((x-rx, y-ry, x+rx, y+ry), fill=(145, 144, 139, rng.randrange(2, 9)))
    # No straight printed seam: the roof build owns membrane joints and paths.
    _save(Image.alpha_composite(image, wear.filter(ImageFilter.GaussianBlur(3.5))), target)


def _interior_atlas(target: Path, seed: int, role: str) -> None:
    rng = random.Random(seed); atlas = Image.new("RGB", ATLAS_SIZE)
    for index in range(8):
        if role == "residential": base = (82 + index % 3 * 5, 70 + index % 2 * 4, 56)
        elif role == "corner": base = (65, 72 + index % 3 * 4, 73 + index % 2 * 4)
        else: base = (94, 79, 57 + index % 3 * 4)
        card = Image.new("RGB", (512, 512), base); draw = ImageDraw.Draw(card, "RGBA")
        draw.rectangle((0, 0, 512, 72), fill=(26, 27, 25, 255))
        for light in range(4):
            x = 54 + light * 130 + rng.randrange(-9, 10)
            draw.rounded_rectangle((x-20, 34, x+20, 41), radius=2, fill=(238, 212, 162, 58 + index % 3 * 5))
        if role == "residential":
            draw.rectangle((35, 255, 180, 340), fill=(72, 60, 49, 120)); draw.rectangle((300, 180, 450, 320), fill=(55, 61, 59, 130))
        elif role == "corner":
            draw.rectangle((40, 160, 472, 225), fill=(86, 92, 85, 74)); draw.rectangle((90, 330, 422, 356), fill=(65, 57, 48, 86))
        else:
            draw.rectangle((35, 120, 477, 210), fill=(108, 92, 70, 72)); draw.rectangle((75, 350, 437, 378), fill=(71, 64, 54, 92))
            # Abstract landing/desk depth, subordinate and never aligned to a
            # facade frame or aperture edge.
            draw.rectangle((55, 255 + (index % 2) * 22, 457, 278 + (index % 2) * 22),
                           fill=(181, 142, 91, 42))
        card = Image.blend(card.filter(ImageFilter.GaussianBlur(.9)), Image.new("RGB", card.size, (82, 77, 68)), .08)
        atlas.paste(card, ((index % 4) * 512, (index // 4) * 512))
    _save(atlas, target)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for path, expected in EXPECTED_REFERENCE_HASHES.items():
        if not path.is_file() or _hash(path) != expected:
            raise ValueError(f"exact reference missing or changed: {path}")
    crop_specs = {
        "brick": (STREET, (420, 112, 520, 255)),
        "precast": (STREET, (645, 248, 690, 474)),
        "base": (STREET, (514, 535, 670, 650)),
        "bronze": (STREET, (532, 162, 633, 455)),
        "residential_glass": (STREET, (350, 285, 390, 386)),
        "corner_glass": (STREET, (558, 178, 615, 419)),
        "gravel": (OBLIQUE, (713, 200, 997, 360)),
        "membrane": (AERIAL, (455, 370, 740, 710)),
        "screen": (OBLIQUE, (470, 190, 735, 310)),
        "equipment": (AERIAL, (420, 205, 850, 360)),
    }
    sampled = {key: _median(path, box) for key, (path, box) in crop_specs.items()}
    palette = {
        "brick": _mix(sampled["brick"], (181, 143, 99), .82),
        "courtyard_brick": _mix(sampled["brick"], (157, 122, 88), .75),
        "precast": _mix(sampled["precast"], (190, 184, 169), .90),
        "base": _mix(sampled["base"], (158, 155, 146), .86),
        "bronze": _mix(sampled["bronze"], (92, 70, 51), .88),
        "residential_glass": _mix(sampled["residential_glass"], (168, 181, 184), .96),
        "corner_glass": _mix(sampled["corner_glass"], (157, 174, 179), .96),
        "gravel": _mix(sampled["gravel"], (165, 158, 145), .92),
        "membrane": _mix(sampled["membrane"], (67, 70, 70), .91),
        "screen": _mix(sampled["screen"], (94, 77, 61), .87),
        "galvanized": _mix(sampled["equipment"], (145, 147, 142), .92),
    }
    outputs = {
        "warm_tan_brick_front": OUT / "warm_tan_brick_front_intrinsic.png",
        "warm_tan_brick_return": OUT / "warm_tan_brick_return_intrinsic.png",
        "subdued_courtyard_brick": OUT / "subdued_courtyard_brick_intrinsic.png",
        "pale_precast": OUT / "pale_precast_intrinsic.png",
        "weathered_base_plinth_reveal": OUT / "weathered_base_plinth_reveal_intrinsic.png",
        "pale_coping_cornice": OUT / "pale_coping_cornice_intrinsic.png",
        "dark_joint_sealant": OUT / "dark_joint_sealant_intrinsic.png",
        "bronze_oriel_frames": OUT / "bronze_oriel_frames_intrinsic.png",
        "bronze_spandrel_casing": OUT / "bronze_spandrel_casing_intrinsic.png",
        "bronze_mechanical_screen": OUT / "bronze_mechanical_screen_intrinsic.png",
        "physical_residential_glass": OUT / "physical_residential_glass_intrinsic.png",
        "physical_corner_glass": OUT / "physical_corner_glass_intrinsic.png",
        "residential_interiors": OUT / "residential_interior_atlas.png",
        "corner_interiors": OUT / "corner_interior_atlas.png",
        "ground_lobby_interiors": OUT / "ground_lobby_interior_atlas.png",
        "gravel_ballast_roof": OUT / "gravel_ballast_roof_intrinsic.png",
        "dark_inner_membrane": OUT / "dark_inner_membrane_intrinsic.png",
        "membrane_service_path": OUT / "membrane_service_path_intrinsic.png",
        "roof_perimeter_flashing": OUT / "roof_perimeter_flashing_intrinsic.png",
        "aged_galvanized_hvac": OUT / "aged_galvanized_hvac_intrinsic.png",
        "galvanized_duct_rails_vents": OUT / "galvanized_duct_rails_vents_intrinsic.png",
        "rooflight_glass": OUT / "rooflight_glass_intrinsic.png",
        "rooflight_curb": OUT / "rooflight_curb_intrinsic.png",
        "threshold": OUT / "threshold_intrinsic.png",
        "door_hardware": OUT / "door_hardware_intrinsic.png",
    }
    _brick(outputs["warm_tan_brick_front"], palette["brick"], 988000)
    _brick(outputs["warm_tan_brick_return"], palette["brick"], 988000, mirror=True)
    _brick(outputs["subdued_courtyard_brick"], palette["courtyard_brick"], 988001, subdued=True)
    _mineral(outputs["pale_precast"], palette["precast"], 988002)
    _mineral(outputs["weathered_base_plinth_reveal"], palette["base"], 988003, weathered=True)
    _mineral(outputs["pale_coping_cornice"], _mix(palette["precast"], (190, 190, 182), .30), 988004)
    _metal(outputs["dark_joint_sealant"], (42, 41, 37), 988005)
    _metal(outputs["bronze_oriel_frames"], palette["bronze"], 988006)
    _metal(outputs["bronze_spandrel_casing"], _mix(palette["bronze"], (113, 82, 57), .25), 988007, weathered=True)
    _ribbed_bronze(outputs["bronze_mechanical_screen"], palette["screen"], 988008)
    _glass(outputs["physical_residential_glass"], palette["residential_glass"], 988009)
    _glass(outputs["physical_corner_glass"], palette["corner_glass"], 988010, corner=True)
    _interior_atlas(outputs["residential_interiors"], 988011, "residential")
    _interior_atlas(outputs["corner_interiors"], 988012, "corner")
    _interior_atlas(outputs["ground_lobby_interiors"], 988013, "lobby")
    _gravel(outputs["gravel_ballast_roof"], palette["gravel"], 988014)
    _membrane(outputs["dark_inner_membrane"], palette["membrane"], 988015)
    _membrane(outputs["membrane_service_path"], _mix(palette["membrane"], (113, 112, 106), .42), 988016, path=True)
    _metal(outputs["roof_perimeter_flashing"], _mix(palette["precast"], (152, 154, 150), .45), 988017)
    _galvanized(outputs["aged_galvanized_hvac"], palette["galvanized"], 988018, darker=True)
    _galvanized(outputs["galvanized_duct_rails_vents"], _mix(palette["galvanized"], (168, 171, 168), .32), 988019)
    _glass(outputs["rooflight_glass"], _mix(palette["corner_glass"], (118, 132, 134), .30), 988020, corner=True)
    _metal(outputs["rooflight_curb"], _mix(palette["galvanized"], (125, 128, 125), .28), 988021)
    _metal(outputs["threshold"], _mix(palette["galvanized"], (123, 126, 123), .33), 988022)
    _metal(outputs["door_hardware"], (54, 52, 47), 988023)

    atlas_roles = {"residential_interiors", "corner_interiors", "ground_lobby_interiors"}
    records = {}
    for role, path in outputs.items():
        with Image.open(path) as image:
            expected = ATLAS_SIZE if role in atlas_roles else (SIZE, SIZE)
            if image.mode != "RGB" or image.size != expected:
                raise ValueError(f"invalid {role}: {image.mode} {image.size}")
        records[role] = {
            "path": _repo(path), "sha256": _hash(path),
            "evidence_class": "constrained_completion" if role in atlas_roles else "exact_palette_conditioned_intrinsic",
            "contains_printed_openings": False,
            "contains_printed_frames_or_mullions": False,
            "contains_printed_bands_or_pilasters": False,
            "contains_printed_reflection_or_horizon": False,
            "contains_baked_directional_lighting": False,
            "contains_text_or_logo": False,
        }
    provenance = {
        "schema": "siteforge.sticker-asset-provenance@1",
        "building": "graduate_family_housing--collegiate_brick_corner_block", "variant_index": 0,
        "identity_authority": "three_exact_variant_0_images",
        "exact_reference_sources": {p.name: {"path": _repo(p), "sha256": h, "evidence_class": "exact_reference"}
                                    for p, h in EXPECTED_REFERENCE_HASHES.items()},
        "palette_conditioning": {
            "rule": "bounds-asserted median probes blended toward intrinsic material priors; no source pixels pasted",
            "crops_px": {k: {"path": _repo(p), "box": list(box)} for k, (p, box) in crop_specs.items()},
            "sampled_rgb": {k: list(v) for k, v in sampled.items()},
            "prepared_palette_rgb": {k: list(v) for k, v in palette.items()},
        },
        "geometry_ownership": ["openings and reveals", "precast bands and pilasters", "oriel projection and frames",
                               "parapets and coping profiles", "mechanical screen profiles and roof equipment"],
        "brick_contract": "Fine 65.6mm-course metric running-bond fired-clay field only; no printed opening, floor band, pilaster, shadow or lighting.",
        "glass_contract": "Separate neutral residential and corner optical fields; no printed frame, mullion, aperture, scene reflection or horizon.",
        "interior_contract": "Separate deterministic neutral-veiled 4x2 residential, corner and lobby cards remain recessed and subordinate.",
        "roof_contract": "Seamless light gravel, dark inner membrane and service path belong only to explicit upward roof fields; no printed membrane seam; verticals, curbs, coping and equipment retain construction-role finishes.",
        "atlas_grid": [4, 2], "assets": records, "post_generation_nonuniform_scale_allowed": False,
    }
    _atomic_json(provenance, OUT / "provenance.json")
    print(json.dumps({"output": str(OUT), "prepared_assets": len(outputs)}, indent=2))


if __name__ == "__main__":
    main()
