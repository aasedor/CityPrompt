"""Prepare deterministic intrinsic sticker assets for the V98 textile mill.

The rectified five-bay/three-floor elevation is an existing generated master.
This script never rewrites or non-uniformly rescales that master.  It prepares
the construction-return and roof/service materials needed to prevent exposed
clay in orbit views.  Exact variant imagery is used as evidence, not mistaken
for a literal rear elevation.
"""
from __future__ import annotations

import hashlib
import json
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageOps, ImageStat


REPO = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent / "sticker_assets/old_montreal_textile_v98"
REFERENCE_DIR = REPO / "frontend/public/archetypes/buildings/old-montreal-warehouse-loft"
MASTER = OUT / "five_bay_three_floor_intrinsic_v2.png"
WINDOW_ATLAS = OUT / "five_bay_three_floor_window_only_v1.png"
INTERIOR_ATLAS = OUT / "five_bay_three_floor_interior_only_v2.png"
INTERIOR_VARIANTS = OUT / "five_bay_three_floor_interior_only_v3.png"
FRONT_REFERENCE = REFERENCE_DIR / "variant_2.png"
OBLIQUE_REFERENCE = REFERENCE_DIR / "variant_2_angle_60.jpg"
AERIAL_REFERENCE = REFERENCE_DIR / "variant_2_angle_90.jpg"
SIZE = 1024


def _repo_path(path: Path) -> str:
    return path.relative_to(REPO).as_posix()


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _brick_construction(target: Path) -> None:
    """Atomic aged brick only: no baked mullions, windows, arches or belts."""
    rng = random.Random(9801)
    image = Image.new("RGB", (SIZE, SIZE), (119, 61, 43))
    draw = ImageDraw.Draw(image)
    course_h, brick_w = 28, 92
    for row, y in enumerate(range(-course_h, SIZE + course_h, course_h)):
        offset = -(brick_w // 2) if row % 2 else 0
        mortar = (152, 142, 128)
        draw.rectangle((0, y, SIZE, y + 3), fill=mortar)
        for x in range(offset, SIZE + brick_w, brick_w):
            jitter = rng.randint(-10, 9)
            brick = (_clamp(121 + jitter), _clamp(62 + jitter // 2), _clamp(43 + jitter // 3))
            draw.rectangle((x + 3, y + 4, x + brick_w - 2, y + course_h - 2), fill=brick)
            draw.line((x + 3, y + 5, x + brick_w - 3, y + 5), fill=(151, 82, 57), width=1)
            draw.rectangle((x, y, x + 3, y + course_h), fill=mortar)
    image.filter(ImageFilter.GaussianBlur(0.28)).save(target)


def _sample_colour(source: Path, box: tuple[int, int, int, int]) -> tuple[int, int, int]:
    with Image.open(source) as image:
        patch = image.convert("RGB").crop(box)
    mean = ImageStat.Stat(patch).mean
    return tuple(round(channel) for channel in mean)


def _clamp(value: int) -> int:
    return max(0, min(255, value))


def _stone_construction(target: Path) -> None:
    # Keep limestone materially distinct from both red brick and warm rooms.
    # This is a construction surface, not a crop containing baked openings.
    base = (158, 153, 143)
    rng = random.Random(9802)
    image = Image.new("RGB", (SIZE, SIZE), base)
    pixels = image.load()
    for y in range(SIZE):
        for x in range(SIZE):
            grain = rng.randint(-5, 5) + ((x * 11 + y * 7) % 5) - 2
            pixels[x, y] = tuple(_clamp(channel + grain) for channel in base)
    draw = ImageDraw.Draw(image)
    course = 168
    block = 256
    for row, y in enumerate(range(0, SIZE, course)):
        draw.line((0, y, SIZE, y), fill=tuple(_clamp(c - 24) for c in base), width=3)
        offset = block // 2 if row % 2 else 0
        for x in range(-offset, SIZE, block):
            draw.line(
                (x, y, x, min(SIZE, y + course)),
                fill=tuple(_clamp(c - 17) for c in base),
                width=2,
            )
    image.filter(ImageFilter.GaussianBlur(0.45)).save(target)


def _horizontal_cut_stone(target: Path) -> None:
    """Continuous cut-stone microtexture for belts, sills and cornices."""
    base = (139, 137, 132)
    rng = random.Random(9808)
    image = Image.new("RGB", (SIZE, SIZE), base)
    pixels = image.load()
    for y in range(SIZE):
        edge_tone = -round(5 * abs(y - SIZE / 2) / (SIZE / 2))
        for x in range(SIZE):
            grain = rng.randint(-7, 7) + edge_tone
            pixels[x, y] = tuple(_clamp(channel + grain) for channel in base)
    image.filter(ImageFilter.GaussianBlur(0.55)).save(target)


def _black_iron(target: Path) -> None:
    image = Image.new("RGB", (SIZE, SIZE), (29, 31, 30))
    draw = ImageDraw.Draw(image)
    for x in range(0, SIZE, 128):
        draw.rectangle((x, 0, min(SIZE, x + 126), SIZE), fill=(31, 33, 32))
        draw.line((x, 0, x, SIZE), fill=(13, 15, 15), width=3)
        draw.line((min(SIZE - 1, x + 125), 0, min(SIZE - 1, x + 125), SIZE), fill=(48, 49, 47), width=1)
        for y in range(48, SIZE, 192):
            draw.ellipse((x + 7, y, x + 13, y + 6), fill=(73, 72, 66))
    image.filter(ImageFilter.GaussianBlur(0.3)).save(target)


def _warm_interior_card(target: Path, role: str = "middle") -> None:
    base_by_role = {
        "ground": (96, 79, 61),
        "middle": (74, 62, 51),
        "top": (66, 58, 50),
    }
    base = base_by_role[role]
    image = Image.new("RGB", (SIZE, SIZE), base)
    pixels = image.load()
    for y in range(SIZE):
        height_tone = 22 - abs(y - 470) // 28
        for x in range(SIZE):
            bay_tone = ((x // 170) % 3) * 5
            pixels[x, y] = tuple(_clamp(channel + height_tone // 3 + bay_tone) for channel in base)
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 790, SIZE, SIZE), fill=(39, 36, 32))
    draw.line((0, 790, SIZE, 790), fill=(136, 108, 78), width=3)
    for x in range(90, SIZE, 230):
        draw.rectangle((x, 180, x + 70, 650), fill=(92, 77, 61))
    image.filter(ImageFilter.GaussianBlur(5.0)).save(target)


def _interior_variant_atlas(source: Path, target: Path) -> None:
    """Expand the generated 3x3 room source into five non-adjacent bay variants.

    Geometry owns all apertures and sash.  This deterministic operation only
    varies the recessed room evidence through source-cell choice, crop,
    mirroring and restrained exposure/colour shifts.
    """
    with Image.open(source) as loaded:
        base = loaded.convert("RGB")
    source_w, source_h = base.size
    cell_w, cell_h = source_w // 3, source_h // 3
    out_cell_w, out_cell_h = 300, 300
    atlas = Image.new("RGB", (out_cell_w * 5, out_cell_h * 3))
    source_cells = (0, 1, 2, 0, 1)
    flips = (False, True, False, True, False)
    brightness = (0.92, 1.04, 0.98, 1.08, 0.88)
    colour = (0.96, 1.04, 0.99, 1.02, 0.94)
    zoom = (1.04, 1.10, 1.06, 1.12, 1.08)
    for row in range(3):
        for column in range(5):
            source_column = (source_cells[column] + row) % 3
            crop = base.crop((source_column * cell_w, row * cell_h,
                              (source_column + 1) * cell_w, (row + 1) * cell_h))
            crop_size = round(min(cell_w, cell_h) / zoom[column])
            x_bias = (-0.10, 0.08, 0.0, -0.06, 0.11)[column]
            x0 = round((cell_w - crop_size) * (0.5 + x_bias))
            y0 = round((cell_h - crop_size) * (0.42 + 0.05 * ((column + row) % 3)))
            x0 = max(0, min(cell_w - crop_size, x0))
            y0 = max(0, min(cell_h - crop_size, y0))
            crop = crop.crop((x0, y0, x0 + crop_size, y0 + crop_size))
            if flips[column] ^ bool(row % 2):
                crop = ImageOps.mirror(crop)
            crop = ImageEnhance.Brightness(crop).enhance(brightness[column] * (1.06 if row == 2 else 1.0))
            crop = ImageEnhance.Color(crop).enhance(colour[column])
            crop = crop.resize((out_cell_w, out_cell_h), Image.Resampling.LANCZOS)
            atlas.paste(crop, (column * out_cell_w, row * out_cell_h))
    atlas.save(target)


def _neutral_window_glass(target: Path) -> None:
    """Subtle neutral variation only; reflection and transmission stay shader-driven."""
    image = Image.new("RGB", (SIZE, SIZE), (205, 213, 209))
    pixels = image.load()
    rng = random.Random(9809)
    for y in range(SIZE):
        tone = round(3 * (1.0 - y / max(SIZE - 1, 1)))
        for x in range(SIZE):
            grain = rng.choice((-1, 0, 0, 0, 1))
            pixels[x, y] = (205 + tone + grain, 213 + tone + grain, 209 + tone + grain)
    image.filter(ImageFilter.GaussianBlur(3.0)).save(target)


def _dark_gravel_roof(target: Path) -> None:
    rng = random.Random(9803)
    image = Image.new("RGB", (SIZE, SIZE), (65, 65, 61))
    draw = ImageDraw.Draw(image)
    for _ in range(26000):
        x = rng.randrange(SIZE)
        y = rng.randrange(SIZE)
        tone = rng.randrange(45, 94)
        radius = 1 if rng.random() < 0.83 else 2
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=(tone, tone, _clamp(tone - 3)))
    image.filter(ImageFilter.GaussianBlur(0.55)).save(target)


def _skylight_glass(target: Path) -> None:
    """Restrained aged monitor glass; modeled ribs own every visible bar."""
    rng = random.Random(9810)
    image = Image.new("RGB", (SIZE, SIZE), (89, 108, 111))
    pixels = image.load()
    for y in range(SIZE):
        gradient = round(9 * (1.0 - y / max(SIZE - 1, 1)))
        for x in range(SIZE):
            grime = rng.choice((-3, -2, -1, 0, 0, 0, 1, 2))
            pixels[x, y] = (89 + gradient + grime, 108 + gradient + grime, 111 + gradient + grime)
    image.filter(ImageFilter.GaussianBlur(5.0)).save(target)


def _dark_coping(target: Path) -> None:
    image = Image.new("RGB", (SIZE, SIZE), (42, 43, 41))
    draw = ImageDraw.Draw(image)
    panel = 256
    for x in range(0, SIZE, panel):
        draw.rectangle((x, 0, min(SIZE, x + panel - 3), SIZE), fill=(44 + (x // panel) % 2 * 3, 45, 43))
        draw.line((x, 0, x, SIZE), fill=(17, 19, 19), width=4)
        draw.line((x + 5, 0, x + 5, SIZE), fill=(62, 63, 59), width=2)
    draw.line((0, 58, SIZE, 58), fill=(74, 74, 68), width=3)
    draw.line((0, SIZE - 58, SIZE, SIZE - 58), fill=(20, 22, 22), width=4)
    image.filter(ImageFilter.GaussianBlur(0.35)).save(target)


def _skylight_glass_metal(target: Path) -> None:
    image = Image.new("RGB", (SIZE, SIZE), (73, 91, 96))
    draw = ImageDraw.Draw(image)
    panel_w = 128
    panel_h = 256
    for y in range(0, SIZE, panel_h):
        for x in range(0, SIZE, panel_w):
            phase = ((x // panel_w) + (y // panel_h)) % 3
            glass = (80 + phase * 5, 98 + phase * 6, 103 + phase * 7)
            draw.rectangle((x + 5, y + 5, x + panel_w - 5, y + panel_h - 5), fill=glass)
            draw.line((x + 15, y + 8, x + panel_w - 18, y + panel_h - 8), fill=(120, 137, 139), width=3)
        draw.line((0, y, SIZE, y), fill=(24, 29, 30), width=10)
    for x in range(0, SIZE, panel_w):
        draw.line((x, 0, x, SIZE), fill=(23, 28, 29), width=9)
    image.filter(ImageFilter.GaussianBlur(0.45)).save(target)


def _hvac_service_casing(target: Path) -> None:
    image = Image.new("RGB", (SIZE, SIZE), (156, 153, 140))
    draw = ImageDraw.Draw(image)
    panel_w = 256
    panel_h = 256
    for y in range(0, SIZE, panel_h):
        for x in range(0, SIZE, panel_w):
            phase = ((x // panel_w) + (y // panel_h)) % 2
            fill = (160 + phase * 4, 157 + phase * 4, 143 + phase * 3)
            draw.rectangle((x + 4, y + 4, x + panel_w - 4, y + panel_h - 4), fill=fill)
            draw.line((x + 22, y + 46, x + panel_w - 22, y + 46), fill=(98, 100, 94), width=3)
            for vent_y in range(y + 76, y + 196, 16):
                draw.line((x + 42, vent_y, x + panel_w - 42, vent_y), fill=(101, 103, 96), width=4)
            for px, py in ((x + 14, y + 14), (x + panel_w - 20, y + 14), (x + 14, y + panel_h - 20), (x + panel_w - 20, y + panel_h - 20)):
                draw.ellipse((px, py, px + 6, py + 6), fill=(70, 72, 69))
    image.filter(ImageFilter.GaussianBlur(0.3)).save(target)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    required = [MASTER, WINDOW_ATLAS, INTERIOR_ATLAS, FRONT_REFERENCE, OBLIQUE_REFERENCE, AERIAL_REFERENCE,
                OUT / "brick_return_intrinsic_v2.png", OUT / "pale_stone_construction_intrinsic_v2.png"]
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"missing V98 source assets: {missing}")

    with Image.open(MASTER) as image:
        if image.size != (1254, 1254):
            raise ValueError("V98 carrier-conditioned master must remain the original 1254x1254 square")
    with Image.open(WINDOW_ATLAS) as image:
        if image.size != (1254, 1254):
            raise ValueError("V98 window-only atlas must remain the generated 1254x1254 square")
    _interior_variant_atlas(INTERIOR_ATLAS, INTERIOR_VARIANTS)
    master_hash_before = _hash(MASTER)

    outputs = {
        "red_brick_construction_return": OUT / "brick_return_intrinsic.png",
        "pale_stone_belt_pier_soffit": OUT / "pale_stone_construction_intrinsic.png",
        "horizontal_cut_stone": OUT / "cut_stone_horizontal_intrinsic.png",
        "black_iron_frame_metal": OUT / "black_iron_metal_intrinsic.png",
        "warm_shallow_interior_card": OUT / "warm_interior_card_intrinsic.png",
        "ground_interior_card": OUT / "ground_interior_card_intrinsic.png",
        "middle_interior_card": OUT / "middle_interior_card_intrinsic.png",
        "top_interior_card": OUT / "top_interior_card_intrinsic.png",
        "neutral_physical_window_glass": OUT / "neutral_window_glass_intrinsic.png",
        "dark_gravel_membrane_roof": OUT / "dark_gravel_roof_intrinsic.png",
        "dark_coping": OUT / "dark_coping_intrinsic.png",
        "skylight_glass_metal": OUT / "skylight_glass_metal_intrinsic.png",
        "skylight_glass": OUT / "skylight_glass_intrinsic.png",
        "hvac_service_casing": OUT / "hvac_service_casing_intrinsic.png",
    }
    _brick_construction(outputs["red_brick_construction_return"])
    _stone_construction(outputs["pale_stone_belt_pier_soffit"])
    _horizontal_cut_stone(outputs["horizontal_cut_stone"])
    _black_iron(outputs["black_iron_frame_metal"])
    _warm_interior_card(outputs["warm_shallow_interior_card"], "middle")
    _warm_interior_card(outputs["ground_interior_card"], "ground")
    _warm_interior_card(outputs["middle_interior_card"], "middle")
    _warm_interior_card(outputs["top_interior_card"], "top")
    _neutral_window_glass(outputs["neutral_physical_window_glass"])
    _dark_gravel_roof(outputs["dark_gravel_membrane_roof"])
    _dark_coping(outputs["dark_coping"])
    _skylight_glass_metal(outputs["skylight_glass_metal"])
    _skylight_glass(outputs["skylight_glass"])
    _hvac_service_casing(outputs["hvac_service_casing"])

    if _hash(MASTER) != master_hash_before:
        raise RuntimeError("the generated master was modified")
    for path in outputs.values():
        with Image.open(path) as image:
            if image.size != (SIZE, SIZE) or image.mode != "RGB":
                raise ValueError(f"invalid prepared asset {path.name}: {image.size} {image.mode}")

    exact_sources = {
        "street_identity": FRONT_REFERENCE,
        "oblique_side_and_roof_evidence": OBLIQUE_REFERENCE,
        "aerial_roof_plan_evidence": AERIAL_REFERENCE,
    }
    asset_records = {
        "five_bay_three_floor_intrinsic_v2": {
            "path": _repo_path(MASTER),
            "evidence_class": "generated",
            "derivation": "generated after clay revision 3 locked; rectified intrinsic elevation conditioned jointly on exact variant_2 references and final canonical carrier",
            "sha256": master_hash_before,
        },
        "five_bay_three_floor_window_only_v1": {
            "path": _repo_path(WINDOW_ATLAS),
            "evidence_class": "generated",
            "derivation": "window-only atlas generated after locked geometry and atomic-surface audit; contains glazing, sash and interiors but no masonry or other carrier-owned architecture",
            "sha256": _hash(WINDOW_ATLAS),
        },
        "five_bay_three_floor_interior_only_v2": {
            "path": _repo_path(INTERIOR_ATLAS),
            "evidence_class": "generated",
            "derivation": "interior-only three-band occupied-loft atlas generated after locked geometry; contains no glass, frames, mullions, masonry or exterior silhouette",
            "sha256": _hash(INTERIOR_ATLAS),
        },
        "five_bay_three_floor_interior_only_v3": {
            "path": _repo_path(INTERIOR_VARIANTS),
            "evidence_class": "deterministic_variant_atlas",
            "derivation": "five bay variants per floor derived from the approved interior-only source using crop, mirror and restrained exposure/colour shifts; no exterior geometry or glass",
            "sha256": _hash(INTERIOR_VARIANTS),
        },
    }
    derivations = {
        "red_brick_construction_return": "deterministic atomic aged-brick construction surface; contains no baked windows, arches, belts or metal",
        "pale_stone_belt_pier_soffit": "deterministic procedural completion using stone colour sampled from generated master",
        "horizontal_cut_stone": "deterministic joint-free weathered cut-stone microtexture for narrow horizontal construction",
        "black_iron_frame_metal": "deterministic procedural completion of black iron frame/metal vocabulary visible in exact street and oblique references",
        "warm_shallow_interior_card": "deterministic procedural shallow-interior completion matching warm glazing evidence in exact street and oblique references",
        "ground_interior_card": "deterministic brighter ground-floor interior card, physically behind neutral glass",
        "middle_interior_card": "deterministic restrained middle-floor interior card, physically behind neutral glass",
        "top_interior_card": "deterministic dim top-floor interior card, physically behind neutral glass",
        "neutral_physical_window_glass": "neutral low-detail optical colour field with no baked mullions, windows, rooms or directional reflections",
        "dark_gravel_membrane_roof": "deterministic procedural completion matching exact aerial gravel/membrane roof evidence",
        "dark_coping": "deterministic procedural completion matching dark parapet coping visible in exact oblique and aerial references",
        "skylight_glass_metal": "deterministic procedural completion matching the two long metal-framed skylights in exact aerial evidence",
        "skylight_glass": "restrained aged gray-green monitor glazing without printed ribs, divisions or directional streaks",
        "hvac_service_casing": "deterministic procedural completion matching bounded rooftop service casing in exact oblique and aerial evidence",
    }
    for role, path in outputs.items():
        asset_records[role] = {
            "path": _repo_path(path),
            "evidence_class": "constrained_completion",
            "derivation": derivations[role],
            "sha256": _hash(path),
        }

    provenance = {
        "schema": "siteforge.sticker-asset-provenance@1",
        "building": "old-montreal-warehouse-loft--old-mtl-textile-mill",
        "variant_index": 2,
        "method": "V98 generated rectified master plus deterministic native-scale crops and reference-constrained procedural surface completions",
        "exact_reference_sources": {
            role: {
                "path": _repo_path(path),
                "evidence_class": "exact_reference",
                "sha256": _hash(path),
            }
            for role, path in exact_sources.items()
        },
        "rear_evidence": {
            "evidence_class": "constrained_completion",
            "statement": "Rear and hidden returns are constrained completion from exact oblique and aerial evidence; no exact rear elevation exists in the variant_2 triplet.",
        },
        "assets": asset_records,
        "master_source_grid": [5, 3],
        "master_dimensions_px": [1254, 1254],
        "post_generation_nonuniform_scale_allowed": False,
        "approval_space": "rendered_on_locked_geometry_with_front_side_rear_roof_soffit_and_service-carrier seam audit",
    }
    (OUT / "provenance.json").write_text(json.dumps(provenance, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(OUT), "prepared_assets": len(outputs), "master_unchanged": True}, indent=2))


if __name__ == "__main__":
    main()
