"""Prepare deterministic intrinsic Sticker assets for the tilt-up industrial V98 pilot.

Exact variant-0 images condition material palette only. Geometry owns tilt-up
panel joints, apertures, loading bays, frames, canopy, parapets and equipment.
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
OUT = Path(__file__).resolve().parent / "sticker_assets/industrial_tilt_up_concrete_v98"
REF = REPO / "frontend/public/archetypes/buildings/industrial_park_modernism"
STREET = REF / "variant_0.png"
OBLIQUE = REF / "variant_0_angle_60.jpg"
AERIAL = REF / "variant_0_angle_90.jpg"
SIZE = 1024
ATLAS_SIZE = (2048, 1024)
EXPECTED_REFERENCE_HASHES = {
    STREET: "de5e08df02bcda3c33c5a0d9eb5f13ac4c8f4d4c50a5ac89ef9d0df7826baab7",
    OBLIQUE: "0e2fd31a87d156a3e8a04f0fbaea93b1e0e69606e1c4ebbe8f1a52bb9923c65b",
    AERIAL: "d6abca22f264b4ba34c4d43af49eb0d311236f5dadebce2ed393220e1be3817e",
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


def _noise(base: tuple[int, int, int], seed: int, amplitude: int, scale: int = 84) -> Image.Image:
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


def _aggregate(target: Path, base: tuple[int, int, int], seed: int, *, weathered: bool = False,
               mirror: bool = False) -> None:
    """Seamless mineral field with no panel joint, aperture, form tie or cast shadow."""
    rng = random.Random(seed)
    fine = _noise(base, seed, 7 if weathered else 5, 112)
    broad = _noise(base, seed + 91, 12 if weathered else 8, 14).filter(ImageFilter.GaussianBlur(10))
    image = Image.blend(fine, broad, .40).convert("RGBA")
    grain = Image.new("RGBA", image.size, (0, 0, 0, 0)); draw = ImageDraw.Draw(grain)
    for _ in range(1800):
        x, y = rng.randrange(SIZE), rng.randrange(SIZE); r = rng.choice((1, 1, 1, 2, 2, 3))
        delta = rng.choice((-24, -15, -9, 9, 14, 20))
        colour = tuple(_clamp(c + delta) for c in base)
        draw.ellipse((x-r, y-r, x+r, y+r), fill=(*colour, rng.randrange(30, 90)))
    # Sparse casting/tie impressions add credible metric character without
    # drawing panel boundaries or a structural grid into the material.
    for _ in range(42):
        x, y = rng.randrange(18, SIZE-18), rng.randrange(18, SIZE-18)
        r = rng.choice((2, 3, 3, 4))
        draw.ellipse((x-r, y-r, x+r, y+r), fill=(67, 69, 66, 28), outline=(222, 219, 207, 16), width=1)
    if weathered:
        for _ in range(45):
            x, y = rng.randrange(SIZE), rng.randrange(SIZE); rx, ry = rng.randrange(15, 70), rng.randrange(10, 45)
            draw.ellipse((x-rx, y-ry, x+rx, y+ry), fill=(73, 72, 66, rng.randrange(3, 13)))
    result = Image.alpha_composite(image, grain.filter(ImageFilter.GaussianBlur(.45)))
    if mirror:
        result = result.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    _save(result, target)


def _paint(target: Path, base: tuple[int, int, int], seed: int, *, ribbed: bool = False) -> None:
    image = _noise(base, seed, 4, 96).convert("RGBA")
    if ribbed:
        relief = Image.new("RGBA", image.size, (0, 0, 0, 0)); draw = ImageDraw.Draw(relief)
        # Door-sheet micro-ribs only; opening, jamb and panel schedule remain geometry.
        for x in range(0, SIZE, 22):
            draw.line((x, 0, x, SIZE), fill=(18, 20, 20, 58), width=3)
            draw.line((x + 4, 0, x + 4, SIZE), fill=(244, 244, 238, 38), width=2)
        image = Image.alpha_composite(image, relief)
    _save(image, target)


def _sectional_door(target: Path, base: tuple[int, int, int], seed: int) -> None:
    """Neutral gray overhead-door sheet with metric horizontal sections.

    Geometry owns the door opening and frame. These regular shallow courses
    are intrinsic formed-sheet relief, shared by right and rear doors.
    """
    rng = random.Random(seed)
    image = _noise(base, seed, 5, 96).convert("RGBA")
    relief = Image.new("RGBA", image.size, (0, 0, 0, 0)); draw = ImageDraw.Draw(relief)
    course_px = 96  # bound to compiler's 4m metric tile => 0.375m sections
    for y in range(0, SIZE, course_px):
        draw.line((0, y, SIZE, y), fill=(28, 31, 31, 116), width=5)
        draw.line((0, y + 6, SIZE, y + 6), fill=(245, 245, 239, 76), width=3)
        draw.line((0, y + course_px - 4, SIZE, y + course_px - 4), fill=(54, 57, 57, 44), width=2)
    # Restrained vertical edge variation belongs to formed sheet, not a frame.
    for x in range(64, SIZE, 128):
        draw.line((x, 0, x, SIZE), fill=(245, 245, 239, 11), width=1)
    for _ in range(80):
        x, y = rng.randrange(SIZE), rng.randrange(SIZE)
        draw.ellipse((x, y, x + rng.randrange(1, 5), y + rng.randrange(1, 3)), fill=(72, 74, 72, 12))
    _save(Image.alpha_composite(image, relief), target)


def _metal(target: Path, base: tuple[int, int, int], seed: int, *, grille: bool = False) -> None:
    rng = random.Random(seed)
    image = _noise(base, seed, 6, 92).convert("RGBA")
    marks = Image.new("RGBA", image.size, (0, 0, 0, 0)); draw = ImageDraw.Draw(marks)
    for _ in range(500):
        x, y = rng.randrange(SIZE), rng.randrange(SIZE)
        draw.ellipse((x, y, x+rng.randrange(1, 6), y+rng.randrange(1, 4)), fill=(89, 77, 62, rng.randrange(2, 10)))
    if grille:
        for y in range(7, SIZE, 16):
            draw.line((0, y, SIZE, y), fill=(12, 14, 14, 32), width=3)
    _save(Image.alpha_composite(image, marks.filter(ImageFilter.GaussianBlur(.5))), target)


def _glass(target: Path, base: tuple[int, int, int], seed: int, *, rooflight: bool = False) -> None:
    # Neutral optical field only: no sky, horizon, reflections, aperture or mullions.
    field = _noise(base, seed, 3, 72).filter(ImageFilter.GaussianBlur(2.3))
    if not rooflight:
        # Low-frequency neutral optical variation prevents a dead black pane
        # without printing a sky, horizon or recognisable scene reflection.
        broad = _noise(_mix(base, (170, 186, 193), .30), seed + 404, 12, 10).filter(ImageFilter.GaussianBlur(18))
        field = Image.blend(field, broad, .22)
    veil = Image.new("RGB", field.size, (181, 195, 201) if not rooflight else (137, 155, 161))
    _save(Image.blend(field, veil, .62 if not rooflight else .42), target)


def _membrane(target: Path, base: tuple[int, int, int], seed: int, *, perimeter: bool = False) -> None:
    rng = random.Random(seed)
    image = _noise(base, seed, 6 if not perimeter else 10, 86).convert("RGBA")
    wear = Image.new("RGBA", image.size, (0, 0, 0, 0)); draw = ImageDraw.Draw(wear)
    for _ in range(700 if not perimeter else 1050):
        x, y = rng.randrange(SIZE), rng.randrange(SIZE); rx, ry = rng.randrange(3, 30), rng.randrange(2, 16)
        tone = rng.choice((80, 111, 145, 184))
        draw.ellipse((x-rx, y-ry, x+rx, y+ry), fill=(tone, tone, tone, rng.randrange(2, 9)))
    # Subtle material lap frequency only; no parapet shadow or hard drain marks.
    for y in range(112, SIZE, 160):
        draw.line((0, y, SIZE, y), fill=(73, 76, 75, 24 if not perimeter else 30), width=2)
        draw.line((0, y + 3, SIZE, y + 3), fill=(235, 234, 228, 13), width=1)
    for _ in range(22 if not perimeter else 36):
        x, y = rng.randrange(SIZE), rng.randrange(SIZE); r = rng.randrange(10, 34)
        draw.ellipse((x-r, y-r, x+r, y+r), outline=(90, 92, 89, 13), width=2)
    _save(Image.alpha_composite(image, wear.filter(ImageFilter.GaussianBlur(4.8))), target)


def _interior_atlas(target: Path, seed: int, *, upper: bool) -> None:
    rng = random.Random(seed); atlas = Image.new("RGB", ATLAS_SIZE)
    for index in range(8):
        card = Image.new("RGB", (512, 512), (32 + index % 3 * 2, 38 + index % 2 * 2, 41 + index % 4))
        draw = ImageDraw.Draw(card, "RGBA")
        draw.rectangle((0, 0, 512, 82), fill=(25, 28, 28, 255))
        for light in range(4):
            x = 55 + light * 130 + rng.randrange(-8, 9)
            draw.rounded_rectangle((x-19, 37, x+19, 43), radius=2, fill=(205, 196, 171, 28 if not upper else 22))
        if upper:
            for x in (42, 176, 310, 444):
                draw.rectangle((x, 286, min(x+83, 500), 299), fill=(82, 75, 67, 80))
                draw.rectangle((x+16, 230, min(x+64, 500), 281), fill=(30, 36, 37, 185))
            draw.rectangle((30, 128, 482, 190), fill=(121, 112, 95, 72))
        else:
            draw.rectangle((35, 100, 477, 205), fill=(102, 98, 88, 54))
            draw.rectangle((43, 330, 469, 360), fill=(82, 74, 65, 78))
            for x in (108, 254, 406):
                draw.rectangle((x-18, 385, x+18, 411), fill=(128, 111, 84, 42))
        veil = Image.new("RGB", card.size, (60, 65, 64) if not upper else (58, 68, 72))
        card = Image.blend(card.filter(ImageFilter.GaussianBlur(.8)), veil, .22)
        atlas.paste(card, ((index % 4) * 512, (index // 4) * 512))
    _save(atlas, target)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for path, expected in EXPECTED_REFERENCE_HASHES.items():
        if not path.is_file() or _hash(path) != expected:
            raise ValueError(f"exact reference missing or changed: {path}")

    crop_specs = {
        "warm_concrete": (STREET, (445, 213, 615, 390)),
        "cool_concrete": (STREET, (790, 245, 950, 460)),
        "plinth": (STREET, (520, 520, 680, 600)),
        "joinery": (STREET, (205, 342, 315, 455)),
        "glass": (STREET, (215, 350, 300, 435)),
        "canopy": (OBLIQUE, (245, 533, 455, 585)),
        "roof": (AERIAL, (315, 220, 930, 665)),
        "equipment": (OBLIQUE, (405, 240, 595, 400)),
        "door": (STREET, (835, 415, 955, 590)),
    }
    sampled = {key: _median(path, box) for key, (path, box) in crop_specs.items()}
    palette = {
        "warm": _mix(sampled["warm_concrete"], (181, 173, 151), .78),
        # The exact service view is shadowed; normalize toward light exposed
        # aggregate so side/rear panels never inherit photographic charcoal.
        "cool": _mix(sampled["cool_concrete"], (159, 163, 160), .96),
        "plinth": _mix(sampled["plinth"], (128, 130, 124), .80),
        "joinery": _mix(sampled["joinery"], (72, 76, 74), .94),
        "glass": _mix(sampled["glass"], (137, 157, 165), .96),
        "canopy": _mix(sampled["canopy"], (68, 71, 69), .90),
        "roof": _mix(sampled["roof"], (211, 211, 203), .86),
        "roof_perimeter": _mix(sampled["roof"], (164, 165, 159), .84),
        "galvanized": _mix(sampled["equipment"], (145, 149, 146), .86),
        "door": _mix(sampled["door"], (132, 136, 135), .94),
    }
    outputs = {
        "warm_buff_concrete_front": OUT / "warm_buff_concrete_front_intrinsic.png",
        "warm_buff_concrete_return": OUT / "warm_buff_concrete_return_intrinsic.png",
        "cool_gray_side_rear_concrete": OUT / "cool_gray_side_rear_concrete_intrinsic.png",
        "weathered_plinth_reveal_concrete": OUT / "weathered_plinth_reveal_concrete_intrinsic.png",
        "dark_joint_sealant": OUT / "dark_joint_sealant_intrinsic.png",
        "pale_coping_flashing": OUT / "pale_coping_flashing_intrinsic.png",
        "charcoal_bronze_aluminum": OUT / "charcoal_bronze_aluminum_intrinsic.png",
        "physical_neutral_glass": OUT / "physical_neutral_glass_intrinsic.png",
        "lobby_lower_office_interiors": OUT / "lobby_lower_office_interior_atlas.png",
        "upper_office_interiors": OUT / "upper_office_interior_atlas.png",
        "canopy_top": OUT / "dark_canopy_top_intrinsic.png",
        "canopy_fascia": OUT / "dark_canopy_fascia_intrinsic.png",
        "canopy_soffit_posts": OUT / "dark_canopy_soffit_posts_intrinsic.png",
        "ribbed_overhead_doors": OUT / "ribbed_overhead_doors_intrinsic.png",
        "dock_rubber_hardware": OUT / "dock_rubber_hardware_intrinsic.png",
        "galvanized_threshold": OUT / "galvanized_threshold_intrinsic.png",
        "personnel_doors": OUT / "personnel_doors_intrinsic.png",
        "safety_yellow_bollards": OUT / "safety_yellow_bollards_intrinsic.png",
        "off_white_tpo": OUT / "off_white_tpo_intrinsic.png",
        "roof_perimeter_patch": OUT / "roof_perimeter_patch_intrinsic.png",
        "rooflight_glass": OUT / "rooflight_glass_intrinsic.png",
        "rooflight_curb": OUT / "rooflight_curb_intrinsic.png",
        "aged_galvanized_hvac_duct_vents": OUT / "aged_galvanized_hvac_duct_vents_intrinsic.png",
        "service_grille": OUT / "service_grille_intrinsic.png",
        "blank_sign_plate": OUT / "blank_sign_plate_intrinsic.png",
        "openwork_shadow_backing": OUT / "openwork_shadow_backing_intrinsic.png",
    }
    _aggregate(outputs["warm_buff_concrete_front"], palette["warm"], 987000)
    _aggregate(outputs["warm_buff_concrete_return"], palette["warm"], 987000, mirror=True)
    _aggregate(outputs["cool_gray_side_rear_concrete"], palette["cool"], 987001)
    _aggregate(outputs["weathered_plinth_reveal_concrete"], palette["plinth"], 987002, weathered=True)
    _paint(outputs["dark_joint_sealant"], (42, 43, 40), 987003)
    _metal(outputs["pale_coping_flashing"], (181, 183, 178), 987004)
    _paint(outputs["charcoal_bronze_aluminum"], palette["joinery"], 987005)
    _glass(outputs["physical_neutral_glass"], palette["glass"], 987006)
    _interior_atlas(outputs["lobby_lower_office_interiors"], 987007, upper=False)
    _interior_atlas(outputs["upper_office_interiors"], 987008, upper=True)
    _paint(outputs["canopy_top"], palette["canopy"], 987009)
    _paint(outputs["canopy_fascia"], _mix(palette["canopy"], (53, 55, 54), .22), 987010)
    _paint(outputs["canopy_soffit_posts"], _mix(palette["canopy"], (79, 81, 78), .20), 987011)
    _sectional_door(outputs["ribbed_overhead_doors"], palette["door"], 987012)
    _paint(outputs["dock_rubber_hardware"], (39, 40, 38), 987013)
    _metal(outputs["galvanized_threshold"], (138, 142, 139), 987014)
    _paint(outputs["personnel_doors"], _mix(palette["door"], (91, 95, 93), .32), 987015)
    _paint(outputs["safety_yellow_bollards"], (205, 163, 38), 987016)
    _membrane(outputs["off_white_tpo"], palette["roof"], 987017)
    _membrane(outputs["roof_perimeter_patch"], palette["roof_perimeter"], 987018, perimeter=True)
    _glass(outputs["rooflight_glass"], _mix(palette["glass"], (111, 128, 133), .30), 987019, rooflight=True)
    _metal(outputs["rooflight_curb"], _mix(palette["galvanized"], (124, 129, 127), .24), 987020)
    _metal(outputs["aged_galvanized_hvac_duct_vents"], palette["galvanized"], 987021)
    _metal(outputs["service_grille"], (54, 58, 57), 987022, grille=True)
    _metal(outputs["blank_sign_plate"], (126, 128, 124), 987023)
    _paint(outputs["openwork_shadow_backing"], (62, 68, 69), 987024)

    atlas_roles = {"lobby_lower_office_interiors", "upper_office_interiors"}
    records = {}
    for role, path in outputs.items():
        with Image.open(path) as image:
            expected = ATLAS_SIZE if role in atlas_roles else (SIZE, SIZE)
            if image.mode != "RGB" or image.size != expected:
                raise ValueError(f"invalid {role}: {image.mode} {image.size}")
        records[role] = {
            "path": _repo(path), "sha256": _hash(path),
            "evidence_class": "constrained_completion" if role in atlas_roles else "exact_palette_conditioned_intrinsic",
            "contains_printed_panel_joints": False,
            "contains_printed_structural_grid": False,
            "contains_printed_apertures": False,
            "contains_printed_mullions": False,
            "contains_printed_reflections_or_horizon": False,
            "contains_baked_directional_lighting": False,
            "contains_text_or_logo": False,
        }
    provenance = {
        "schema": "siteforge.sticker-asset-provenance@1",
        "building": "industrial_park_modernism--industrial_tilt_up_concrete", "variant_index": 0,
        "identity_authority": "three_exact_variant_0_images",
        "exact_reference_sources": {p.name: {"path": _repo(p), "sha256": h, "evidence_class": "exact_reference"}
                                    for p, h in EXPECTED_REFERENCE_HASHES.items()},
        "palette_conditioning": {
            "rule": "bounds-asserted median probes blended toward intrinsic material priors; no source pixels pasted",
            "crops_px": {key: {"path": _repo(path), "box": list(box)} for key, (path, box) in crop_specs.items()},
            "sampled_rgb": {key: list(value) for key, value in sampled.items()},
            "prepared_palette_rgb": {key: list(value) for key, value in palette.items()},
        },
        "geometry_ownership": ["tilt-up panel joints and sealant grooves", "apertures", "loading recesses",
                               "window and door frames", "canopy geometry", "parapets, coping profiles and roof equipment"],
        "concrete_contract": "Intrinsic aggregate and low-frequency mineral variation only; no printed panel grid, joints, form ties, openings, text, shadows or lighting.",
        "glass_contract": "Neutral physical optical field only; no printed frame, aperture, reflection or horizon.",
        "interior_contract": "Separate deterministic neutral-veiled 4x2 lower/lobby and upper-office cards remain recessed and subordinate.",
        "roof_contract": "Off-white TPO and perimeter patch belong only to explicit upward roof faces; parapets, coping, curbs and equipment retain construction-role finishes.",
        "atlas_grid": [4, 2], "assets": records, "post_generation_nonuniform_scale_allowed": False,
    }
    _atomic_json(provenance, OUT / "provenance.json")
    print(json.dumps({"output": str(OUT), "prepared_assets": len(outputs)}, indent=2))


if __name__ == "__main__":
    main()
