"""Prepare deterministic Sticker Method assets for the V98 daylight factory.

Exact variant-0 imagery conditions the bounded material palette.  Generated
wall masters contain material evidence only: no windows, arches, piers,
cornices, roof teeth, sash bars, canopy outlines or chimney silhouettes.
Those features remain the exclusive responsibility of locked geometry.
"""
from __future__ import annotations

import hashlib
import json
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageStat


REPO = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent / "sticker_assets/daylight_sawtooth_v98"
REFERENCE_DIR = REPO / "frontend/public/archetypes/buildings/daylight_factory"
STREET = REFERENCE_DIR / "variant_0.png"
OBLIQUE = REFERENCE_DIR / "variant_0_angle_60.jpg"
AERIAL = REFERENCE_DIR / "variant_0_angle_90.jpg"
SIZE = 1024
MATERIAL_MASTER = OUT / "source_material_atlas.png"
INTERIOR_MASTER = OUT / "source_workshop_interior_master.png"
OPTICAL_MASTER = OUT / "source_optical_roof_atlas_v2.png"
LOCAL_MATERIAL_MASTER = Path(
    r"C:\Users\andre\.codex\generated_images\019fdd1b-296d-7e01-835e-83f66b73045d\exec-6cc67f7e-acad-42a4-9e0c-47f95eb55f52.png"
)
LOCAL_INTERIOR_MASTER = Path(
    r"C:\Users\andre\.codex\generated_images\019fdd1b-296d-7e01-835e-83f66b73045d\exec-fd0596f1-b5ec-49c8-9701-84cfecaab009.png"
)
LOCAL_OPTICAL_MASTER = Path(
    r"C:\Users\andre\.codex\generated_images\019fdd1b-296d-7e01-835e-83f66b73045d\exec-285b0232-7839-443e-82f8-c4d4912b3222.png"
)
MATERIAL_MASTER_SHA256 = "4edc3aed58f596e195e67d23dad8d170e050b75171bb5da8bf91b6163293dd2e"
INTERIOR_MASTER_SHA256 = "65b7060483f9844ce022c9936e7d5474f5b5a6a80b72b72753dc950650d872d0"
OPTICAL_MASTER_SHA256 = "0249f16fa38b26160fffb5a79c7b37be9bc94855fd8b599612c457961445efa1"


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _repo_path(path: Path) -> str:
    return path.relative_to(REPO).as_posix()


def _clamp(value: float) -> int:
    return max(0, min(255, round(value)))


def _median(path: Path, box: tuple[int, int, int, int]) -> tuple[int, int, int]:
    with Image.open(path) as image:
        patch = image.convert("RGB").crop(box)
    return tuple(round(value) for value in ImageStat.Stat(patch).median)


def _mix(a: tuple[int, int, int], b: tuple[int, int, int], amount: float) -> tuple[int, int, int]:
    return tuple(_clamp(left * (1.0 - amount) + right * amount) for left, right in zip(a, b))


def _save(image: Image.Image, target: Path) -> None:
    image.convert("RGB").save(target, optimize=True)


def _ensure_source_master(target: Path, local_source: Path, expected_sha256: str) -> None:
    """Materialize an approved source master once, then make reruns portable."""
    if not target.is_file():
        if not local_source.is_file():
            raise FileNotFoundError(
                f"missing approved master {target.name}; expected it in the asset folder "
                f"or at original generation path {local_source}"
            )
        target.write_bytes(local_source.read_bytes())
    actual = _hash(target)
    if actual != expected_sha256:
        raise ValueError(f"approved master hash mismatch for {target}: {actual}")


def _crop_master(
    source: Path,
    target: Path,
    box: tuple[int, int, int, int],
    *,
    size: tuple[int, int] = (SIZE, SIZE),
    flip_x: bool = False,
) -> None:
    """Extract a bounded intrinsic surface; geometry remains outside the crop."""
    with Image.open(source) as image:
        crop = image.convert("RGB").crop(box)
    if flip_x:
        crop = crop.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    _save(crop.resize(size, Image.Resampling.LANCZOS), target)


def _crop_workshop_atlas(source: Path, target: Path) -> list[list[int]]:
    """Repack eight equal interior-only bays into a deterministic 4-by-2 atlas."""
    with Image.open(source) as image:
        master = image.convert("RGB")
    atlas = Image.new("RGB", (2048, 1024))
    boxes: list[list[int]] = []
    for index in range(8):
        left = round(index * master.width / 8)
        right = round((index + 1) * master.width / 8)
        # Remove only the outermost master edge; there are no separator bars.
        box = (left + (2 if index == 0 else 0), 2, right - (2 if index == 7 else 0), master.height - 2)
        boxes.append(list(box))
        card = master.crop(box).resize((512, 512), Image.Resampling.LANCZOS)
        atlas.paste(card, ((index % 4) * 512, (index // 4) * 512))
    _save(atlas, target)
    return boxes


def _brick_field(target: Path, base: tuple[int, int, int], seed: int, *, chimney: bool = False) -> None:
    """Write a seamless-looking material field, never a facade drawing."""
    rng = random.Random(seed)
    mortar = _mix(base, (151, 137, 119), 0.52 if chimney else 0.45)
    image = Image.new("RGB", (SIZE, SIZE), mortar)
    draw = ImageDraw.Draw(image)
    course = 34 if chimney else 42
    nominal = 92 if chimney else 116
    joint = 3
    for row, y in enumerate(range(-course, SIZE + course, course)):
        offset = nominal // 2 if row % 2 else 0
        x = -nominal - offset
        while x < SIZE:
            width = nominal + rng.randint(-7, 7)
            tone = rng.randint(-20, 18)
            soot = -rng.randint(0, 12) if chimney else 0
            colour = tuple(_clamp(channel + tone + soot) for channel in base)
            draw.rectangle((x + joint, y + joint, x + width - joint, y + course - joint), fill=colour)
            if rng.random() < 0.28:
                chip_y = y + rng.randint(7, max(8, course - 8))
                draw.line((x + 8, chip_y, x + width - 12, chip_y + rng.choice((-1, 0, 1))),
                          fill=tuple(_clamp(c - 16) for c in colour), width=1)
            x += width
    # Broad low-contrast age variation; never directional cast shadows.
    haze = Image.new("RGBA", image.size, (0, 0, 0, 0))
    haze_draw = ImageDraw.Draw(haze)
    for _ in range(18):
        x, y = rng.randrange(SIZE), rng.randrange(SIZE)
        radius = rng.randrange(45, 150)
        if chimney:
            colour = (28, 25, 22, rng.randrange(6, 18))
        else:
            colour = rng.choice(((210, 205, 189, 7), (42, 39, 34, 8), (119, 101, 82, 8)))
        haze_draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=colour)
    haze = haze.filter(ImageFilter.GaussianBlur(42))
    image = Image.alpha_composite(image.convert("RGBA"), haze).convert("RGB")
    _save(image.filter(ImageFilter.GaussianBlur(0.18)), target)


def _weathered_concrete(target: Path, base: tuple[int, int, int], seed: int, *, top: bool) -> None:
    rng = random.Random(seed)
    image = Image.new("RGB", (SIZE, SIZE), base)
    draw = ImageDraw.Draw(image, "RGBA")
    for _ in range(24000):
        x, y = rng.randrange(SIZE), rng.randrange(SIZE)
        delta = rng.randint(-18, 18)
        colour = tuple(_clamp(c + delta) for c in base) + (rng.randint(25, 75),)
        radius = 1 if rng.random() < 0.92 else 2
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=colour)
    for _ in range(18):
        x = rng.randrange(SIZE)
        width = rng.randrange(6, 24)
        if top:
            y = rng.randrange(SIZE)
            draw.ellipse((x - 80, y - 18, x + 80, y + 18), fill=(55, 51, 44, rng.randrange(4, 13)))
        else:
            draw.rectangle((x, 0, x + width, SIZE), fill=(68, 62, 52, rng.randrange(3, 10)))
    _save(image.filter(ImageFilter.GaussianBlur(0.42)), target)


def _cut_stone(target: Path, base: tuple[int, int, int], seed: int) -> None:
    rng = random.Random(seed)
    image = Image.new("RGB", (SIZE, SIZE), base)
    draw = ImageDraw.Draw(image, "RGBA")
    for y in range(SIZE):
        tone = 7 * ((y % 121) / 120.0 - 0.5)
        draw.line((0, y, SIZE, y), fill=tuple(_clamp(c + tone) for c in base) + (75,), width=1)
    for _ in range(2200):
        x, y = rng.randrange(SIZE), rng.randrange(SIZE)
        tone = rng.choice((-13, -8, 7, 11))
        draw.point((x, y), fill=tuple(_clamp(c + tone) for c in base) + (90,))
    for _ in range(8):
        y = rng.randrange(SIZE)
        draw.line((0, y, SIZE, y + rng.randint(-2, 2)), fill=(65, 59, 50, 13), width=rng.randrange(2, 8))
    _save(image.filter(ImageFilter.GaussianBlur(0.35)), target)


def _roof_field(target: Path, base: tuple[int, int, int], seed: int) -> None:
    rng = random.Random(seed)
    image = Image.new("RGB", (SIZE, SIZE), base)
    draw = ImageDraw.Draw(image, "RGBA")
    course = 54
    for row, y in enumerate(range(0, SIZE, course)):
        tone = rng.randint(-8, 7)
        fill = tuple(_clamp(c + tone) for c in base) + (110,)
        draw.rectangle((0, y, SIZE, min(SIZE, y + course - 2)), fill=fill)
        draw.line((0, y, SIZE, y), fill=(20, 22, 22, 90), width=2)
        offset = 64 if row % 2 else 0
        for x in range(-offset, SIZE, 128):
            draw.line((x, y, x, min(SIZE, y + course)), fill=(25, 27, 27, 45), width=2)
    for _ in range(1800):
        x, y = rng.randrange(SIZE), rng.randrange(SIZE)
        draw.point((x, y), fill=(190, 184, 168, rng.randrange(4, 16)))
    _save(image.filter(ImageFilter.GaussianBlur(0.32)), target)


def _glass_field(target: Path, base: tuple[int, int, int], seed: int, *, northlight: bool) -> None:
    rng = random.Random(seed)
    image = Image.new("RGB", (SIZE, SIZE), base)
    draw = ImageDraw.Draw(image, "RGBA")
    for y in range(SIZE):
        if northlight:
            delta = -11 + 20 * (1.0 - y / (SIZE - 1))
        else:
            delta = 8 * (1.0 - abs(y / (SIZE - 1) - 0.46) * 2)
        draw.line((0, y, SIZE, y), fill=tuple(_clamp(c + delta) for c in base) + (92,), width=1)
    # Glass-only weathering: no printed grid, frame, aperture, horizon or
    # reflection stripe. Use small isotropic patches so repeating a pane does
    # not create conspicuous vertical or horizontal bands.
    for _ in range(96 if northlight else 52):
        x, y = rng.randrange(SIZE), rng.randrange(SIZE)
        radius_x = rng.randrange(3, 22)
        radius_y = rng.randrange(3, 22)
        alpha = rng.randrange(3, 12)
        draw.ellipse((x - radius_x, y - radius_y, x + radius_x, y + radius_y),
                     fill=(211, 205, 188, alpha))
    if northlight:
        for _ in range(120):
            x, y = rng.randrange(SIZE), rng.randrange(SIZE // 3, SIZE)
            radius = rng.randrange(3, 14)
            draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=(83, 75, 59, rng.randrange(5, 18)))
    _save(image.filter(ImageFilter.GaussianBlur(1.15 if northlight else 1.8)), target)


def _black_steel(target: Path, seed: int) -> None:
    rng = random.Random(seed)
    image = Image.new("RGB", (SIZE, SIZE), (29, 31, 31))
    draw = ImageDraw.Draw(image, "RGBA")
    for x in range(SIZE):
        tone = 5 * ((x % 83) / 82.0 - 0.5)
        draw.line((x, 0, x, SIZE), fill=(90, 92, 88, _clamp(14 + tone)), width=1)
    for _ in range(640):
        x, y = rng.randrange(SIZE), rng.randrange(SIZE)
        length = rng.randrange(2, 20)
        draw.line((x, y, min(SIZE, x + length), y), fill=(153, 115, 78, rng.randrange(3, 13)), width=1)
    _save(image.filter(ImageFilter.GaussianBlur(0.25)), target)


def _rolling_door(target: Path, base: tuple[int, int, int], seed: int) -> None:
    rng = random.Random(seed)
    image = Image.new("RGB", (SIZE, SIZE), base)
    draw = ImageDraw.Draw(image, "RGBA")
    slat = 42
    for y in range(0, SIZE, slat):
        draw.rectangle((0, y, SIZE, min(SIZE, y + slat - 3)), fill=tuple(_clamp(c + rng.randint(-4, 4)) for c in base) + (255,))
        draw.line((0, y, SIZE, y), fill=(35, 38, 36, 105), width=3)
        draw.line((0, y + 5, SIZE, y + 5), fill=(224, 221, 200, 28), width=2)
    for x in range(0, SIZE, 256):
        draw.rectangle((x, 0, x + 4, SIZE), fill=(37, 41, 39, 55))
    _save(image.filter(ImageFilter.GaussianBlur(0.28)), target)


def _canopy_surface(target: Path, seed: int, role: str) -> None:
    rng = random.Random(seed)
    palette = {
        "top": (54, 56, 54),
        "fascia": (37, 39, 39),
        "soffit": (72, 69, 62),
    }
    image = Image.new("RGB", (SIZE, SIZE), palette[role])
    draw = ImageDraw.Draw(image, "RGBA")
    if role == "top":
        for _ in range(9000):
            x, y = rng.randrange(SIZE), rng.randrange(SIZE)
            tone = rng.randrange(35, 80)
            draw.point((x, y), fill=(tone, tone, _clamp(tone - 3), rng.randrange(15, 48)))
    elif role == "fascia":
        for x in range(0, SIZE, 256):
            draw.line((x, 0, x, SIZE), fill=(12, 14, 14, 90), width=3)
    else:
        for x in range(0, SIZE, 128):
            draw.line((x, 0, x, SIZE), fill=(41, 39, 36, 60), width=2)
        for _ in range(25):
            x = rng.randrange(SIZE)
            draw.rectangle((x, 0, x + rng.randrange(4, 15), SIZE), fill=(92, 55, 34, rng.randrange(3, 12)))
    _save(image.filter(ImageFilter.GaussianBlur(0.45)), target)


def _workshop_atlas(target: Path, seed: int) -> None:
    """Create eight frame-free, opening-free shallow workshop cards."""
    rng = random.Random(seed)
    columns, rows = 4, 2
    cell_w, cell_h = 512, 512
    atlas = Image.new("RGB", (columns * cell_w, rows * cell_h), (52, 43, 34))
    for index in range(columns * rows):
        cell = Image.new("RGB", (cell_w, cell_h), (48 + index % 3 * 3, 41, 34))
        draw = ImageDraw.Draw(cell, "RGBA")
        # Ceiling and floor depth planes; no aperture edge or window frame.
        draw.rectangle((0, 0, cell_w, 176), fill=(66, 56, 45, 255))
        draw.rectangle((0, 390, cell_w, cell_h), fill=(38, 33, 29, 255))
        vanish_x = cell_w // 2 + rng.randint(-65, 65)
        for x in range(-80, cell_w + 80, 92):
            draw.line((x, 0, vanish_x, 245), fill=(105, 88, 66, 74), width=4)
        for y in (58, 119, 174):
            draw.line((0, y, cell_w, y + rng.randint(-4, 4)), fill=(124, 99, 70, 48), width=4)
        # Interior columns and machinery silhouettes are illusion only.
        for x in range(55 + index % 2 * 28, cell_w, 145):
            width = 17 + rng.randint(-3, 5)
            draw.rectangle((x, 118, x + width, 424), fill=(74, 64, 53, 210))
            draw.rectangle((x - 8, 408, x + width + 8, 429), fill=(42, 37, 32, 220))
        for _ in range(3 + index % 3):
            x = rng.randint(25, cell_w - 120)
            y = rng.randint(282, 405)
            w = rng.randint(55, 125)
            h = rng.randint(30, 92)
            draw.rectangle((x, y - h, x + w, y), fill=(37, 39, 37, 210))
            draw.line((x + 8, y - h + 9, x + w - 8, y - h + 9), fill=(128, 98, 64, 78), width=3)
        for _ in range(2 + index % 2):
            x = rng.randint(55, cell_w - 55)
            y = rng.randint(75, 245)
            radius = rng.randint(15, 32)
            draw.ellipse((x - radius, y - radius // 2, x + radius, y + radius // 2), fill=(255, 205, 139, 46 + index * 2))
            draw.line((x, y + radius // 2, x, y + 70), fill=(77, 66, 52, 90), width=2)
        cell = cell.filter(ImageFilter.GaussianBlur(1.25))
        atlas.paste(cell, ((index % columns) * cell_w, (index // columns) * cell_h))
    _save(atlas, target)


def _coping(target: Path, seed: int) -> None:
    rng = random.Random(seed)
    image = Image.new("RGB", (SIZE, SIZE), (43, 43, 40))
    draw = ImageDraw.Draw(image, "RGBA")
    for x in range(SIZE):
        tone = 8 * ((x % 137) / 136.0 - 0.5)
        draw.line((x, 0, x, SIZE), fill=(96, 93, 84, _clamp(12 + tone)), width=1)
    for _ in range(320):
        x, y = rng.randrange(SIZE), rng.randrange(SIZE)
        draw.line((x, y, min(SIZE, x + rng.randrange(2, 24)), y), fill=(163, 122, 76, rng.randrange(3, 14)), width=1)
    _save(image.filter(ImageFilter.GaussianBlur(0.3)), target)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    _ensure_source_master(MATERIAL_MASTER, LOCAL_MATERIAL_MASTER, MATERIAL_MASTER_SHA256)
    _ensure_source_master(INTERIOR_MASTER, LOCAL_INTERIOR_MASTER, INTERIOR_MASTER_SHA256)
    _ensure_source_master(OPTICAL_MASTER, LOCAL_OPTICAL_MASTER, OPTICAL_MASTER_SHA256)
    sources = [STREET, OBLIQUE, AERIAL]
    missing = [str(path) for path in sources if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"missing daylight-factory exact references: {missing}")

    # Fixed evidence crops condition hue/value only. No reference pixels are
    # pasted into masters, so scene objects and modeled geometry cannot leak.
    palette = {
        "brick": _mix(_median(STREET, (650, 285, 770, 650)), (137, 60, 37), 0.48),
        "stone": _mix(_median(STREET, (650, 606, 760, 673)), (137, 130, 116), 0.64),
        "concrete": _mix(_median(OBLIQUE, (78, 500, 265, 635)), (127, 121, 108), 0.52),
        "roof": _mix(_median(OBLIQUE, (530, 120, 780, 230)), (57, 61, 60), 0.62),
        "wall_glass": _mix(_median(STREET, (815, 315, 895, 565)), (96, 103, 101), 0.58),
        "northlight_glass": _mix(_median(AERIAL, (405, 222, 810, 500)), (84, 96, 97), 0.58),
        "rolling_door": _mix(_median(STREET, (120, 470, 220, 620)), (107, 120, 108), 0.72),
    }
    outputs = {
        "ordinary_red_brick_field": OUT / "red_brick_wall_intrinsic.png",
        "brick_construction_return": OUT / "red_brick_return_intrinsic.png",
        "pale_stone_sill_cap": OUT / "pale_stone_sill_cap_intrinsic.png",
        "dock_concrete_vertical": OUT / "weathered_dock_concrete_vertical_intrinsic.png",
        "dock_concrete_top": OUT / "weathered_dock_concrete_top_intrinsic.png",
        "opaque_tooth_roof": OUT / "dark_slate_metal_roof_intrinsic.png",
        "wall_window_glass": OUT / "neutral_industrial_glass_intrinsic.png",
        "northlight_glass": OUT / "northlight_glass_intrinsic.png",
        "steel_sash_and_flashing": OUT / "black_steel_intrinsic.png",
        "rolling_door_metal": OUT / "rolling_door_intrinsic.png",
        "occupied_workshop_interior_cards": OUT / "occupied_workshop_interior_atlas.png",
        "canopy_top": OUT / "canopy_top_intrinsic.png",
        "canopy_fascia": OUT / "canopy_fascia_intrinsic.png",
        "canopy_soffit": OUT / "canopy_soffit_intrinsic.png",
        "chimney_brick_wrap": OUT / "chimney_brick_intrinsic.png",
        "chimney_coping": OUT / "chimney_coping_intrinsic.png",
    }
    # The approved 3x2 material master is 1536x1024, with 512px cells and
    # narrow separator bars at x=511/1023 and y=511. Insets exclude them.
    material_boxes = {
        "ordinary_red_brick_field": (4, 4, 507, 507),
        "opaque_tooth_roof": (517, 4, 1019, 507),
        "dock_concrete_vertical": (1029, 4, 1532, 507),
        "rolling_door_metal": (4, 517, 507, 1020),
        # One uninterrupted smoky pane, deliberately inside the generated
        # atlas panel lines. Geometry, never this sticker, owns sash bars.
        "wall_window_glass": (650, 620, 755, 700),
        "steel_sash_and_flashing": (1029, 517, 1532, 1020),
    }
    for role, box in material_boxes.items():
        _crop_master(MATERIAL_MASTER, outputs[role], box)
    # The approved optical master is a 3:1 horizontal atlas (currently
    # 2172 x 724), not the 2048 x 1024 material-atlas layout. Derive the
    # thirds from the source so an out-of-bounds crop can never introduce
    # black PIL padding into a sticker.
    with Image.open(OPTICAL_MASTER) as optical_master:
        optical_width, optical_height = optical_master.size
    optical_third = optical_width // 3
    optical_boxes = {
        "opaque_tooth_roof": (2 * optical_third, 0, optical_width, optical_height),
    }
    for role, box in optical_boxes.items():
        _crop_master(OPTICAL_MASTER, outputs[role], box)
    # Optical glass must be continuous and geometry-agnostic. Use the exact
    # references only to condition hue/value; deterministic weathering avoids
    # baking a shared horizon or hard reflection band into every pane.
    _glass_field(outputs["wall_window_glass"], palette["wall_glass"], 980208, northlight=False)
    _glass_field(outputs["northlight_glass"], palette["northlight_glass"], 980209, northlight=True)
    # Returns deliberately reuse the same intrinsic field mirrored, preserving
    # the material identity without cloning conspicuous marks around a corner.
    _crop_master(MATERIAL_MASTER, outputs["brick_construction_return"], material_boxes["ordinary_red_brick_field"], flip_x=True)
    _cut_stone(outputs["pale_stone_sill_cap"], palette["stone"], 980202)
    _weathered_concrete(outputs["dock_concrete_top"], _mix(palette["concrete"], (104, 100, 91), 0.22), 980204, top=True)
    workshop_crop_boxes = _crop_workshop_atlas(INTERIOR_MASTER, outputs["occupied_workshop_interior_cards"])
    _canopy_surface(outputs["canopy_top"], 980211, "top")
    _canopy_surface(outputs["canopy_fascia"], 980212, "fascia")
    _canopy_surface(outputs["canopy_soffit"], 980213, "soffit")
    _brick_field(outputs["chimney_brick_wrap"], _mix(palette["brick"], (105, 61, 44), 0.24), 980214, chimney=True)
    _coping(outputs["chimney_coping"], 980215)

    for role, path in outputs.items():
        with Image.open(path) as image:
            expected = (2048, 1024) if role == "occupied_workshop_interior_cards" else (SIZE, SIZE)
            if image.size != expected or image.mode != "RGB":
                raise ValueError(f"invalid prepared asset {path.name}: {image.size} {image.mode}")

    records = {}
    for role, path in outputs.items():
        if role in {"wall_window_glass", "northlight_glass"}:
            generation = "deterministic_reference_palette_conditioned_intrinsic_glass"
            source = "exact_reference_palette_statistics"
            crop = None
        elif role in optical_boxes:
            generation = "deterministic_crop_from_approved_optical_roof_master_v2"
            source = _repo_path(OPTICAL_MASTER)
            crop = optical_boxes[role]
        elif role in material_boxes or role == "brick_construction_return":
            generation = "deterministic_crop_from_approved_material_master"
            source = _repo_path(MATERIAL_MASTER)
            crop = material_boxes["ordinary_red_brick_field"] if role == "brick_construction_return" else material_boxes[role]
        elif role == "occupied_workshop_interior_cards":
            generation = "deterministic_repack_from_approved_interior_master"
            source = _repo_path(INTERIOR_MASTER)
            crop = workshop_crop_boxes
        else:
            generation = "deterministic_code_native"
            source = None
            crop = None
        records[role] = {
            "path": _repo_path(path),
            "evidence_class": "constrained_completion",
            "generation": generation,
            "contains_printed_modeled_geometry": False,
            "sha256": _hash(path),
        }
        if source is not None:
            records[role]["source_master"] = source
            records[role]["source_crop_px"] = crop
        if role == "brick_construction_return":
            records[role]["transform"] = "horizontal_mirror"
    provenance = {
        "schema": "siteforge.sticker-asset-provenance@1",
        "building": "daylight-factory--factory-sawtooth-roof",
        "variant_index": 0,
        "method": "exact-reference-conditioned approved-master crops plus deterministic intrinsic completion; no facade or roof-feature overlays",
        "exact_reference_sources": {
            "street_identity": {"path": _repo_path(STREET), "evidence_class": "exact_reference", "sha256": _hash(STREET)},
            "oblique_wall_roof_canopy": {"path": _repo_path(OBLIQUE), "evidence_class": "exact_reference", "sha256": _hash(OBLIQUE)},
            "aerial_six_tooth_roof_plan": {"path": _repo_path(AERIAL), "evidence_class": "exact_reference", "sha256": _hash(AERIAL)},
        },
        "palette_conditioning": {
            "method": "fixed median reference crops blended toward bounded architectural material priors",
            "values_rgb": {key: list(value) for key, value in palette.items()},
        },
        "approved_generation_sources": {
            "material_atlas": {
                "path": _repo_path(MATERIAL_MASTER),
                "sha256": _hash(MATERIAL_MASTER),
                "layout": "3 columns x 2 rows: brick, dark roof, concrete / rolling door, smoky glass, black steel",
                "crop_policy": "fixed cell crops inset from separator bars; no windows, openings, or facade geometry",
            },
            "workshop_interior_master": {
                "path": _repo_path(INTERIOR_MASTER),
                "sha256": _hash(INTERIOR_MASTER),
                "layout": "continuous 8-cell interior-only concept master",
                "crop_policy": "eight deterministic equal-width crops repacked to a 4 x 2 atlas; outer edge inset only",
            },
            "optical_roof_master_v2": {
                "path": _repo_path(OPTICAL_MASTER),
                "sha256": _hash(OPTICAL_MASTER),
                "layout": "3 columns: wall glass, northlight glass, continuous dark roof",
                "crop_policy": "fixed intrinsic cell crops; no printed frames, mullions or architecture",
            },
        },
        "topology_authority": {
            "occupied_floors": 1,
            "sawtooth_units": 6,
            "statement": "Exact images override conflicting two-floor rollout metadata; clerestories are rooflight volume.",
        },
        "rear_evidence": {
            "evidence_class": "constrained_completion",
            "statement": "No exact rear elevation exists; rear and hidden returns may repeat only the ordinary material grammar constrained by the oblique and aerial references.",
        },
        "geometry_ownership": "Locked geometry exclusively owns openings, arches, piers, sash bars, sills, canopy edges, roof teeth, northlight frames and chimney silhouette.",
        "assets": records,
        "workshop_atlas_grid": [4, 2],
        "post_generation_nonuniform_scale_allowed": False,
        "approval_space": "rendered_on_locked_atomic_carriers_with_wall_roof_canopy_chimney_and_underface seam audit",
    }
    (OUT / "provenance.json").write_text(json.dumps(provenance, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(OUT), "prepared_assets": len(outputs)}, indent=2))


if __name__ == "__main__":
    main()
