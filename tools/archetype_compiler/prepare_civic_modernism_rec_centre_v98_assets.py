"""Prepare deterministic intrinsic assets for the reference-locked rec-centre V98 pilot.

The three exact variant-0 references are palette evidence only.  Their lighting,
reflections, openings and structural grid are deliberately excluded: geometry
owns the concrete frame, apertures, joinery profiles and every roof silhouette.
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
OUT = Path(__file__).resolve().parent / "sticker_assets/civic_modernism_rec_centre_v98"
REF = REPO / "frontend/public/archetypes/buildings/civic_modernism_rec_centre"
STREET = REF / "variant_0.png"
OBLIQUE = REF / "variant_0_angle_60.jpg"
AERIAL = REF / "variant_0_angle_90.jpg"
SIZE = 1024
ATLAS_SIZE = (2048, 1024)
EXPECTED_REFERENCE_HASHES = {
    STREET: "9183129653aa668116a66add2613d1241b6ebbe342895565001d6a675d90ed37",
    OBLIQUE: "cc5c6668c724051a7eca406064ab9d70d0cf4dc79f5e0dc9d742b4e7b049340a",
    AERIAL: "8e221717803e0c92eb731d7a448687e6dd17cd32fc43d0724d9361b600ad2889",
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


def _noise(base: tuple[int, int, int], seed: int, amplitude: int, scale: int = 80) -> Image.Image:
    rng = random.Random(seed)
    small = Image.new("RGB", (scale, scale))
    pixels = []
    for _ in range(scale * scale):
        delta = rng.uniform(-amplitude, amplitude)
        pixels.append(tuple(_clamp(channel + delta) for channel in base))
    small.putdata(pixels)
    return small.resize((SIZE, SIZE), Image.Resampling.BICUBIC)


def _save(image: Image.Image, target: Path) -> None:
    temporary = target.with_name(f".{target.stem}.{os.getpid()}.tmp.png")
    image.convert("RGB").save(temporary, format="PNG", optimize=True)
    for attempt in range(12):
        try:
            temporary.replace(target)
            return
        except PermissionError:
            if attempt == 11:
                temporary.unlink(missing_ok=True)
                raise
            time.sleep(.10 * (attempt + 1))


def _atomic_json(data: dict, target: Path) -> None:
    temporary = target.with_name(f".{target.name}.{os.getpid()}.tmp")
    temporary.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    temporary.replace(target)


def _brick(target: Path, base: tuple[int, int, int], seed: int, *, mirrored: bool = False) -> None:
    rng = random.Random(seed)
    mortar = _mix(base, (178, 170, 155), .64)
    image = Image.new("RGB", (SIZE, SIZE), mortar)
    draw = ImageDraw.Draw(image)
    # Reference-compatible small modular running bond; no openings or frame lines.
    course, unit, joint = 28, 88, 3
    for row, y in enumerate(range(-course, SIZE + course, course)):
        offset = -unit // 2 if row % 2 else 0
        for x in range(offset - unit, SIZE + unit, unit):
            delta = rng.randint(-10, 10)
            colour = (_clamp(base[0] + delta), _clamp(base[1] + delta * .65), _clamp(base[2] + delta * .52))
            draw.rectangle((x + joint, y + joint, x + unit - joint, y + course - joint), fill=colour)
            for _ in range(2):
                px, py = rng.randint(x + 7, x + unit - 7), rng.randint(y + 6, y + course - 6)
                draw.ellipse((px, py, px + rng.randint(2, 6), py + rng.randint(1, 3)), fill=_mix(colour, (83, 55, 42), .15))
    if mirrored:
        image = image.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    _save(image.filter(ImageFilter.GaussianBlur(.15)), target)


def _mineral(target: Path, base: tuple[int, int, int], seed: int, *, stronger: bool = False) -> None:
    rng = random.Random(seed)
    fine = _noise(base, seed, 5 if not stronger else 8, 96)
    coarse = _noise(base, seed + 701, 10 if not stronger else 15, 12).filter(ImageFilter.GaussianBlur(8))
    image = Image.blend(fine, coarse, .48).convert("RGBA")
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0)); draw = ImageDraw.Draw(overlay)
    for _ in range(650 if not stronger else 900):
        x, y = rng.randrange(SIZE), rng.randrange(SIZE); r = rng.randrange(1, 7)
        tone = rng.choice((86, 118, 164, 202))
        draw.ellipse((x-r, y-r, x+r, y+r), fill=(tone, tone, tone, rng.randrange(2, 9)))
    _save(Image.alpha_composite(image, overlay.filter(ImageFilter.GaussianBlur(1.1))), target)


def _membrane(target: Path, base: tuple[int, int, int], seed: int, *, patched: bool = False) -> None:
    rng = random.Random(seed)
    image = _noise(base, seed, 7 if not patched else 12, 80).convert("RGBA")
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0)); draw = ImageDraw.Draw(overlay)
    for _ in range(680 if not patched else 980):
        x, y = rng.randrange(SIZE), rng.randrange(SIZE); rx, ry = rng.randrange(3, 30), rng.randrange(2, 18)
        tone = rng.choice((72, 104, 132, 174))
        draw.ellipse((x-rx, y-ry, x+rx, y+ry), fill=(tone, tone, tone, rng.randrange(2, 10)))
    # Subtle intrinsic lap seams and drain-adjacent wear.  All runs are
    # direction-neutral and low-contrast: no parapet or sunlight shadow.
    for y in range(96, SIZE, 128):
        draw.line((0, y, SIZE, y), fill=(70, 73, 72, 14 if not patched else 20), width=2)
        draw.line((0, y + 3, SIZE, y + 3), fill=(229, 228, 221, 9), width=1)
    for _ in range(18 if not patched else 30):
        x, y = rng.randrange(SIZE), rng.randrange(SIZE); r = rng.randrange(12, 36)
        draw.ellipse((x-r, y-r, x+r, y+r), outline=(76, 79, 78, 12), width=3)
    _save(Image.alpha_composite(image, overlay.filter(ImageFilter.GaussianBlur(5.0))), target)


def _paint(target: Path, base: tuple[int, int, int], seed: int, *, ribbed: bool = False) -> None:
    image = _noise(base, seed, 4, 96).convert("RGBA")
    if ribbed:
        overlay = Image.new("RGBA", image.size, (0, 0, 0, 0)); draw = ImageDraw.Draw(overlay)
        # Construction-scale shallow sheet ribs, not facade structure or lighting.
        for x in range(0, SIZE, 28):
            draw.line((x, 0, x, SIZE), fill=(65, 69, 70, 42), width=2)
            draw.line((x + 3, 0, x + 3, SIZE), fill=(245, 245, 240, 30), width=1)
        image = Image.alpha_composite(image, overlay)
    _save(image, target)


def _glass(target: Path, base: tuple[int, int, int], seed: int, *, skylight: bool = False) -> None:
    # Neutral optical field only: no mullions, apertures, scene reflection or horizon.
    image = _noise(base, seed, 3, 72).filter(ImageFilter.GaussianBlur(2.4))
    veil = Image.new("RGB", image.size, (211, 215, 211) if not skylight else (128, 143, 148))
    _save(Image.blend(image, veil, .78 if not skylight else .38), target)


def _metal(target: Path, base: tuple[int, int, int], seed: int, *, grille: bool = False) -> None:
    rng = random.Random(seed); image = _noise(base, seed, 7, 90).convert("RGBA")
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0)); draw = ImageDraw.Draw(overlay)
    for _ in range(520):
        x, y = rng.randrange(SIZE), rng.randrange(SIZE)
        draw.ellipse((x, y, x+rng.randrange(1, 7), y+rng.randrange(1, 4)), fill=(87, 75, 63, rng.randrange(2, 9)))
    if grille:
        # This is intrinsic perforation/finish, never an aperture or facade opening.
        for y in range(6, SIZE, 16):
            draw.line((0, y, SIZE, y), fill=(20, 23, 23, 30), width=3)
    _save(Image.alpha_composite(image, overlay.filter(ImageFilter.GaussianBlur(.5))), target)


def _interior_atlas(target: Path, seed: int, *, pool: bool) -> None:
    rng = random.Random(seed); atlas = Image.new("RGB", ATLAS_SIZE)
    for index in range(8):
        card = Image.new("RGB", (512, 512), (70 + index % 3 * 3, 76 + index % 2 * 3, 77 + index % 4))
        draw = ImageDraw.Draw(card, "RGBA")
        draw.rectangle((0, 0, 512, 68), fill=(27, 30, 31, 255))
        for light in range(4):
            x = 56 + light * 132 + rng.randrange(-8, 9)
            draw.ellipse((x-12, 33, x+12, 42), fill=(184, 174, 143, 56))
        if pool:
            # Recessed room-card evidence, intentionally soft and subordinate.
            draw.rectangle((0, 326, 512, 512), fill=(60, 139, 158, 230))
            draw.rectangle((0, 292, 512, 332), fill=(194, 185, 158, 175))
            draw.rectangle((0, 72, 512, 170), fill=(157, 164, 158, 78))
            for y in range(349, 500, 31):
                draw.line((0, y, 512, y+rng.randrange(-3, 4)), fill=(184, 219, 220, 70), width=2)
            for x in (86, 252, 416):
                draw.rectangle((x, 145, x+18, 327), fill=(82, 82, 76, 75))
        else:
            for x in (45, 205, 365):
                y = 302 + rng.randrange(-18, 19)
                draw.rectangle((x, y, x+102, y+11), fill=(93, 81, 68, 100))
                draw.rectangle((x+31, y-48, x+74, y-7), fill=(29, 34, 35, 180))
            draw.rectangle((34, 125, 478, 236), fill=(161, 126, 86, 120))
            for x in (104, 258, 408):
                draw.ellipse((x-28, 374, x+28, 410), fill=(188, 137, 78, 105))
        veil = Image.new("RGB", card.size, (72, 85, 88) if pool else (108, 86, 63))
        card = Image.blend(card.filter(ImageFilter.GaussianBlur(.65)), veil, .14)
        atlas.paste(card, ((index % 4) * 512, (index // 4) * 512))
    _save(atlas, target)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for path, expected in EXPECTED_REFERENCE_HASHES.items():
        if not path.is_file() or _hash(path) != expected:
            raise ValueError(f"exact reference missing or changed: {path}")

    crop_specs = {
        "brick": (STREET, (675, 235, 800, 375)),
        "concrete": (STREET, (250, 170, 310, 405)),
        "joinery": (STREET, (450, 435, 565, 545)),
        "glass": (STREET, (310, 325, 420, 500)),
        "canopy": (STREET, (585, 430, 745, 470)),
        "roof": (AERIAL, (625, 195, 980, 515)),
        "equipment": (AERIAL, (410, 205, 590, 360)),
    }
    sampled = {key: _median(path, box) for key, (path, box) in crop_specs.items()}
    palette = {
        "brick": _mix(sampled["brick"], (166, 103, 80), .82),
        # The street crop carries strong sunset warmth; retain only a small
        # reference contribution so the intrinsic frame stays neutral in City
        # Prompt lighting instead of baking the photograph's ochre cast.
        "concrete": _mix(sampled["concrete"], (159, 163, 161), .96),
        "roof_low": _mix(sampled["roof"], (184, 181, 172), .78),
        "roof_high": _mix(sampled["roof"], (173, 171, 164), .72),
        "roof_patch": _mix(sampled["roof"], (140, 139, 134), .78),
        "canopy": _mix(sampled["canopy"], (207, 207, 199), .80),
        "joinery": _mix(sampled["joinery"], (59, 63, 61), .88),
        "glass": _mix(sampled["glass"], (132, 147, 150), .90),
        "entry": (129, 104, 76), "threshold": (151, 150, 144),
        "galvanized": _mix(sampled["equipment"], (139, 144, 142), .86),
    }
    outputs = {
        "warm_brick_front": OUT / "warm_brick_front_intrinsic.png",
        "warm_brick_return": OUT / "warm_brick_return_intrinsic.png",
        "warm_brick_parapet": OUT / "warm_brick_parapet_intrinsic.png",
        "cool_weathered_pale_concrete": OUT / "cool_weathered_pale_concrete_intrinsic.png",
        "pale_concrete_coping": OUT / "pale_concrete_coping_intrinsic.png",
        "low_roof_membrane": OUT / "low_roof_membrane_intrinsic.png",
        "high_roof_membrane": OUT / "high_roof_membrane_intrinsic.png",
        "roof_perimeter_patch": OUT / "roof_perimeter_patch_intrinsic.png",
        "ribbed_canopy_top": OUT / "ribbed_canopy_top_intrinsic.png",
        "smooth_canopy_fascia_soffit_posts": OUT / "smooth_canopy_fascia_soffit_posts_intrinsic.png",
        "dark_aluminum_joinery": OUT / "dark_aluminum_joinery_intrinsic.png",
        "physical_clear_glass": OUT / "physical_clear_glass_intrinsic.png",
        "pool_hall_interiors": OUT / "pool_hall_interior_atlas.png",
        "community_lobby_interiors": OUT / "community_lobby_interior_atlas.png",
        "warm_entry_door_finish": OUT / "warm_entry_door_finish_intrinsic.png",
        "entry_threshold": OUT / "entry_threshold_intrinsic.png",
        "aged_galvanized_hvac_service": OUT / "aged_galvanized_hvac_service_intrinsic.png",
        "dark_service_grille": OUT / "dark_service_grille_intrinsic.png",
        "skylight_glass": OUT / "skylight_glass_intrinsic.png",
        "skylight_curb": OUT / "skylight_curb_intrinsic.png",
    }
    _brick(outputs["warm_brick_front"], palette["brick"], 985000)
    _brick(outputs["warm_brick_return"], palette["brick"], 985000, mirrored=True)
    _brick(outputs["warm_brick_parapet"], _mix(palette["brick"], (145, 82, 62), .10), 985002)
    _mineral(outputs["cool_weathered_pale_concrete"], palette["concrete"], 985003)
    _mineral(outputs["pale_concrete_coping"], _mix(palette["concrete"], (163, 163, 159), .20), 985004, stronger=True)
    _membrane(outputs["low_roof_membrane"], palette["roof_low"], 985005)
    _membrane(outputs["high_roof_membrane"], palette["roof_high"], 985006)
    _membrane(outputs["roof_perimeter_patch"], palette["roof_patch"], 985007, patched=True)
    _paint(outputs["ribbed_canopy_top"], palette["canopy"], 985008, ribbed=True)
    _paint(outputs["smooth_canopy_fascia_soffit_posts"], palette["canopy"], 985009)
    _paint(outputs["dark_aluminum_joinery"], palette["joinery"], 985010)
    _glass(outputs["physical_clear_glass"], palette["glass"], 985011)
    _interior_atlas(outputs["pool_hall_interiors"], 985012, pool=True)
    _interior_atlas(outputs["community_lobby_interiors"], 985013, pool=False)
    _paint(outputs["warm_entry_door_finish"], palette["entry"], 985014)
    _mineral(outputs["entry_threshold"], palette["threshold"], 985015, stronger=True)
    _metal(outputs["aged_galvanized_hvac_service"], palette["galvanized"], 985016)
    _metal(outputs["dark_service_grille"], (48, 52, 51), 985017, grille=True)
    _glass(outputs["skylight_glass"], _mix(palette["glass"], (110, 131, 138), .25), 985018, skylight=True)
    _metal(outputs["skylight_curb"], _mix(palette["galvanized"], (118, 124, 123), .22), 985019)

    records = {}
    atlas_roles = {"pool_hall_interiors", "community_lobby_interiors"}
    for role, path in outputs.items():
        with Image.open(path) as image:
            expected = ATLAS_SIZE if role in atlas_roles else (SIZE, SIZE)
            if image.mode != "RGB" or image.size != expected:
                raise ValueError(f"invalid {role}: {image.mode} {image.size}")
        records[role] = {
            "path": _repo(path), "sha256": _hash(path),
            "evidence_class": "exact_palette_conditioned_intrinsic" if role not in atlas_roles else "constrained_completion",
            "contains_printed_structural_grid": False, "contains_printed_mullions": False,
            "contains_printed_reflections_or_horizon": False, "contains_baked_directional_lighting": False,
            "contains_printed_apertures": False,
        }
    provenance = {
        "schema": "siteforge.sticker-asset-provenance@1",
        "building": "civic_modernism_rec_centre--rec_brick_glass_box", "variant_index": 0,
        "identity_authority": "three_exact_variant_0_images",
        "exact_reference_sources": {path.name: {"path": _repo(path), "sha256": digest, "evidence_class": "exact_reference"}
                                    for path, digest in EXPECTED_REFERENCE_HASHES.items()},
        "palette_conditioning": {
            "rule": "bounds-asserted median probes blended toward material priors; no source pixels pasted",
            "crops_px": {key: {"path": _repo(path), "box": list(box)} for key, (path, box) in crop_specs.items()},
            "sampled_rgb": {key: list(value) for key, value in sampled.items()},
            "prepared_palette_rgb": {key: list(value) for key, value in palette.items()},
        },
        "geometry_ownership": ["concrete structural grid", "apertures", "mullions and transoms", "door rails and frames",
                               "canopy and roof silhouettes", "parapets, rooflights and mechanical equipment"],
        "glass_contract": "Intrinsic neutral optical field only; no printed mullions, apertures, scene reflections or hard horizon.",
        "interior_contract": "Separate deterministic neutral-veiled 4x2 pool-hall and community-lobby cards sit behind physical glass and never own facade geometry.",
        "roof_contract": "Low deck, high deck and perimeter patch are disjoint upward-face assets; parapets, coping, curbs and equipment use construction-role finishes.",
        "atlas_grid": [4, 2], "assets": records, "post_generation_nonuniform_scale_allowed": False,
    }
    _atomic_json(provenance, OUT / "provenance.json")
    print(json.dumps({"output": str(OUT), "prepared_assets": len(outputs)}, indent=2))


if __name__ == "__main__":
    main()
