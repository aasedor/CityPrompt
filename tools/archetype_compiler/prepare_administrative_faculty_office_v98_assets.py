"""Prepare intrinsic Sticker Method assets for the V98 faculty office pilot.

The three exact variant-0 views condition colour and material character only.
No reference pixels are pasted into an output: openings, mullions, fins, panel
joints, coping profiles, screens and mechanical silhouettes belong to geometry.
"""
from __future__ import annotations

import hashlib
import json
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageStat


REPO = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent / "sticker_assets/administrative_faculty_office_v98"
REFERENCE_DIR = REPO / "frontend/public/archetypes/buildings/administrative-faculty-office-building"
STREET = REFERENCE_DIR / "variant_0.png"
OBLIQUE = REFERENCE_DIR / "variant_0_angle_60.jpg"
AERIAL = REFERENCE_DIR / "variant_0_angle_90.jpg"
SIZE = 1024
OFFICE_INTERIOR_MASTER = OUT / "source_office_interior_master.png"
OFFICE_INTERIOR_MASTER_SHA256 = "7e6f7d4215333aab8b6be2eb0e989a1fa2670b270c457ececf4420a031e0c353"


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _repo_path(path: Path) -> str:
    return path.relative_to(REPO).as_posix()


def _clamp(value: float) -> int:
    return max(0, min(255, round(value)))


def _mix(a: tuple[int, int, int], b: tuple[int, int, int], amount: float) -> tuple[int, int, int]:
    return tuple(_clamp(x * (1.0 - amount) + y * amount) for x, y in zip(a, b))


def _assert_crop(path: Path, box: tuple[int, int, int, int]) -> tuple[int, int, int, int]:
    """Reject empty or padded PIL crops before any reference sampling."""
    with Image.open(path) as image:
        width, height = image.size
    left, top, right, bottom = box
    if not (0 <= left < right <= width and 0 <= top < bottom <= height):
        raise ValueError(f"out-of-bounds crop {box} for {path.name} ({width}x{height})")
    return box


def _median(path: Path, box: tuple[int, int, int, int]) -> tuple[int, int, int]:
    checked = _assert_crop(path, box)
    with Image.open(path) as image:
        patch = image.convert("RGB").crop(checked)
    return tuple(round(value) for value in ImageStat.Stat(patch).median)


def _save(image: Image.Image, target: Path) -> None:
    # Blender can render while an asset refinement pass is running.  Never let
    # it observe a partially-written PNG (which Blender displays as magenta).
    # Encode beside the destination, verify the complete image, then publish it
    # with one atomic replace on the same filesystem.
    temporary = target.with_name(f".{target.stem}.writing{target.suffix}")
    image.convert("RGB").save(temporary, format="PNG", optimize=True)
    with Image.open(temporary) as check:
        check.verify()
    temporary.replace(target)


def _intrinsic_noise(base: tuple[int, int, int], seed: int, amplitude: int = 8) -> Image.Image:
    rng = random.Random(seed)
    image = Image.new("RGB", (SIZE, SIZE), base)
    pixels = image.load()
    coarse = [[rng.uniform(-1.0, 1.0) for _ in range(65)] for _ in range(65)]
    for y in range(SIZE):
        gy = y * 64 / (SIZE - 1)
        iy, fy = min(63, int(gy)), gy % 1
        for x in range(SIZE):
            gx = x * 64 / (SIZE - 1)
            ix, fx = min(63, int(gx)), gx % 1
            top = coarse[iy][ix] * (1 - fx) + coarse[iy][ix + 1] * fx
            bottom = coarse[iy + 1][ix] * (1 - fx) + coarse[iy + 1][ix + 1] * fx
            value = (top * (1 - fy) + bottom * fy) * amplitude + rng.uniform(-1.4, 1.4)
            pixels[x, y] = tuple(_clamp(channel + value) for channel in base)
    return image


def _brick(target: Path, base: tuple[int, int, int], seed: int, *, front: bool) -> None:
    rng = random.Random(seed)
    mortar = _mix(base, (151, 145, 132), 0.58)
    image = Image.new("RGB", (SIZE, SIZE), mortar)
    draw = ImageDraw.Draw(image, "RGBA")
    course = 42
    joint = 5
    unit = 116
    for row, y in enumerate(range(-course, SIZE + course, course)):
        offset = -(unit // 2) if row % 2 else 0
        for x in range(offset - unit, SIZE + unit, unit):
            variation = rng.randint(-22, 18)
            warm = rng.randint(-7, 12)
            brick = (
                _clamp(base[0] + variation + warm),
                _clamp(base[1] + variation // 2 + warm // 3),
                _clamp(base[2] + variation // 3),
            )
            draw.rounded_rectangle(
                (x + joint, y + joint, x + unit - joint, y + course - joint),
                radius=2,
                fill=brick,
            )
            for _ in range(7):
                px = rng.randint(x + joint + 3, x + unit - joint - 3)
                py = rng.randint(y + joint + 2, y + course - joint - 2)
                draw.ellipse((px, py, px + rng.randint(2, 9), py + rng.randint(1, 3)), fill=(60, 42, 31, rng.randint(8, 24)))
    # Returns are marginally quieter, but never directionally shaded.
    haze = Image.new("RGBA", image.size, (55, 45, 37, 0 if front else 7))
    image = Image.alpha_composite(image.convert("RGBA"), haze)
    _save(image.filter(ImageFilter.GaussianBlur(0.18)), target)


def _bronze(target: Path, base: tuple[int, int, int], seed: int, role: str) -> None:
    rng = random.Random(seed)
    image = _intrinsic_noise(base, seed, amplitude=9).convert("RGBA")
    broad = Image.new("RGBA", image.size, (0, 0, 0, 0))
    broad_draw = ImageDraw.Draw(broad)
    # Broad, softly blended ochre/russet/patina clouds produce aged bronze
    # character without encoding panel boundaries or a lighting direction.
    patina = ((150, 100, 58), (112, 70, 50), (69, 101, 92), (48, 72, 70), (50, 53, 53))
    weights = (0, 0, 1, 1, 2, 2, 3, 4)
    for _ in range(620):
        x, y = rng.randrange(SIZE), rng.randrange(SIZE)
        rx, ry = rng.randrange(14, 70), rng.randrange(10, 54)
        colour = patina[rng.choice(weights)]
        broad_draw.ellipse((x - rx, y - ry, x + rx, y + ry), fill=colour + (rng.randrange(12, 30),))
    image = Image.alpha_composite(image, broad.filter(ImageFilter.GaussianBlur(12.0)))

    detail = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(detail)
    for _ in range(1350):
        x, y = rng.randrange(SIZE), rng.randrange(SIZE)
        radius = rng.randrange(1, 7)
        colour = patina[rng.choice(weights)]
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=colour + (rng.randrange(5, 18),))
    if role in {"fin", "screen"}:
        # Fine extrusion grain only; the physical fin/screen spacing is geometry.
        for x in range(0, SIZE, 9 if role == "fin" else 6):
            draw.line((x, 0, x, SIZE), fill=(217, 169, 102, 10), width=1)
    if role == "coping":
        for y in range(0, SIZE, 12):
            draw.line((0, y, SIZE, y), fill=(63, 39, 29, 8), width=1)
    image = Image.alpha_composite(image, detail.filter(ImageFilter.GaussianBlur(1.4)))
    _save(image, target)


def _graphite(target: Path, base: tuple[int, int, int], seed: int) -> None:
    image = _intrinsic_noise(base, seed, amplitude=4).convert("RGBA")
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    rng = random.Random(seed)
    for _ in range(330):
        x, y = rng.randrange(SIZE), rng.randrange(SIZE)
        draw.line((x, y, min(SIZE - 1, x + rng.randrange(4, 35)), y), fill=(205, 197, 178, rng.randrange(2, 7)))
    _save(Image.alpha_composite(image, overlay).filter(ImageFilter.GaussianBlur(0.25)), target)


def _glass(target: Path, base: tuple[int, int, int], seed: int, *, fritted: bool) -> None:
    """Intrinsic glazing with no horizon, reflection stripe, frame or mullion."""
    rng = random.Random(seed)
    image = _intrinsic_noise(base, seed, amplitude=3).convert("RGBA")
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    for _ in range(260):
        x, y = rng.randrange(SIZE), rng.randrange(SIZE)
        radius = rng.randrange(2, 12)
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=(202, 210, 202, rng.randrange(2, 5)))
    if fritted:
        # Screen-printed frit is material evidence; its carrier outline is not.
        for y in range(9, SIZE, 18):
            for x in range(9, SIZE, 18):
                jitter = rng.choice((-1, 0, 0, 0, 1))
                draw.ellipse((x - 2 + jitter, y - 2, x + 2 + jitter, y + 2), fill=(222, 220, 205, 48))
    _save(Image.alpha_composite(image, overlay).filter(ImageFilter.GaussianBlur(0.32)), target)


def _stone(target: Path, base: tuple[int, int, int], seed: int, *, plinth: bool) -> None:
    rng = random.Random(seed)
    image = _intrinsic_noise(base, seed, amplitude=7).convert("RGBA")
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    for _ in range(700):
        x, y = rng.randrange(SIZE), rng.randrange(SIZE)
        value = rng.choice((54, 76, 128, 172))
        alpha = rng.randrange(3, 14)
        draw.ellipse((x, y, x + rng.randrange(1, 5), y + rng.randrange(1, 4)), fill=(value, value, value, alpha))
    # Plinth joints and reveal boundaries remain physical geometry.
    _save(Image.alpha_composite(image, overlay).filter(ImageFilter.GaussianBlur(0.28)), target)


def _gravel(target: Path, base: tuple[int, int, int], seed: int) -> None:
    rng = random.Random(seed)
    image = Image.new("RGB", (SIZE, SIZE), base)
    draw = ImageDraw.Draw(image, "RGBA")
    for _ in range(30000):
        x, y = rng.randrange(SIZE), rng.randrange(SIZE)
        radius = rng.choice((1, 1, 2, 2, 3, 4))
        value = rng.randint(-40, 42)
        color = tuple(_clamp(channel + value) for channel in base)
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=color + (rng.randrange(90, 210),))
    _save(image.filter(ImageFilter.GaussianBlur(0.16)), target)


def _mechanical_metal(target: Path, base: tuple[int, int, int], seed: int, role: str) -> None:
    rng = random.Random(seed)
    image = _intrinsic_noise(base, seed, amplitude=6).convert("RGBA")
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    spacing = {"casing": 14, "duct": 24, "pipe": 10}[role]
    horizontal = role == "duct"
    for n in range(0, SIZE, spacing):
        coords = (0, n, SIZE, n) if horizontal else (n, 0, n, SIZE)
        draw.line(coords, fill=(235, 237, 228, 12), width=1)
    for _ in range(420):
        x, y = rng.randrange(SIZE), rng.randrange(SIZE)
        draw.ellipse((x, y, x + rng.randrange(1, 7), y + rng.randrange(1, 4)), fill=(91, 78, 64, rng.randrange(3, 13)))
    _save(Image.alpha_composite(image, overlay).filter(ImageFilter.GaussianBlur(0.25)), target)


def _office_atlas(target: Path, seed: int) -> None:
    """Create eight interior-only cards; no window boundary or exterior frame."""
    rng = random.Random(seed)
    card_w, card_h = 512, 512
    atlas = Image.new("RGB", (card_w * 4, card_h * 2))
    themes = [
        ((50, 47, 42), (183, 147, 98)),
        ((43, 48, 49), (154, 176, 170)),
        ((52, 44, 39), (190, 129, 80)),
        ((42, 44, 47), (167, 160, 136)),
        ((49, 45, 40), (184, 164, 116)),
        ((38, 46, 48), (136, 171, 168)),
        ((48, 41, 39), (187, 137, 100)),
        ((41, 43, 46), (163, 172, 164)),
    ]
    for index, (dark, warm) in enumerate(themes):
        card = Image.new("RGB", (card_w, card_h), dark)
        draw = ImageDraw.Draw(card, "RGBA")
        # Recess cue: ceiling/floor tones and occupied furniture, not an aperture.
        draw.rectangle((0, 0, card_w, 92), fill=_mix(dark, (25, 24, 23), 0.35) + (255,))
        draw.rectangle((0, 390, card_w, card_h), fill=_mix(dark, (88, 76, 61), 0.34) + (255,))
        for lamp in range(4):
            cx = 66 + lamp * 127 + rng.randrange(-10, 11)
            draw.ellipse((cx - 13, 38, cx + 13, 47), fill=warm + (180,))
            draw.ellipse((cx - 30, 45, cx + 30, 70), fill=warm + (18,))
        for desk in range(3):
            x = 45 + desk * 165 + rng.randrange(-12, 13)
            y = 290 + rng.randrange(-24, 25)
            draw.rectangle((x, y, x + 112, y + 15), fill=(111, 87, 63, 235))
            draw.rectangle((x + 8, y + 15, x + 15, 376), fill=(46, 42, 38, 230))
            draw.rectangle((x + 95, y + 15, x + 102, 376), fill=(46, 42, 38, 230))
            draw.rectangle((x + 38, y - 59, x + 87, y - 8), fill=(24, 28, 29, 245))
            draw.rectangle((x + 43, y - 54, x + 82, y - 14), fill=_mix(warm, (74, 91, 96), 0.55) + (215,))
        for shelf in range(2):
            x = 98 + shelf * 265 + rng.randrange(-15, 16)
            draw.rectangle((x, 123, x + 70, 265), fill=(34, 33, 31, 220))
            for y in range(140, 260, 29):
                draw.line((x + 5, y, x + 65, y), fill=(135, 108, 75, 150), width=3)
        atlas.paste(card.filter(ImageFilter.GaussianBlur(0.35)), ((index % 4) * card_w, (index // 4) * card_h))
    _save(atlas, target)


def _registered_office_atlas(target: Path) -> None:
    """Normalize the approved 2:1, 4x2 interior-only master without changing its grid."""
    if not OFFICE_INTERIOR_MASTER.is_file():
        raise FileNotFoundError(f"missing approved office interior master: {OFFICE_INTERIOR_MASTER}")
    actual_hash = _hash(OFFICE_INTERIOR_MASTER)
    if actual_hash != OFFICE_INTERIOR_MASTER_SHA256:
        raise ValueError(f"office interior master hash changed: {actual_hash}")
    with Image.open(OFFICE_INTERIOR_MASTER) as source:
        if source.mode != "RGB" or source.width * 1 != source.height * 2:
            raise ValueError(f"office interior master must be exact 2:1 RGB, got {source.size} {source.mode}")
        atlas = source.resize((2048, 1024), Image.Resampling.LANCZOS).convert("RGB")
    # The source cells are intentionally different rooms, but exterior glass
    # should remain the visual authority. A neutral veil suppresses photographic
    # contrast and saturation without inventing reflections or aperture edges.
    atlas = Image.blend(atlas, Image.new("RGB", atlas.size, (73, 71, 67)), 0.18)
    atlas = Image.blend(atlas, atlas.convert("L").convert("RGB"), 0.14)
    _save(atlas, target)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    references = [STREET, OBLIQUE, AERIAL]
    missing = [str(path) for path in references if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"missing exact administrative-faculty references: {missing}")

    # These crops are palette probes only. Assertions guarantee PIL never pads
    # an invalid crop with black pixels and silently corrupts the palette.
    crop_specs = {
        "brick_street": (STREET, (680, 185, 742, 308)),
        "brick_oblique": (OBLIQUE, (910, 395, 990, 570)),
        "bronze_street": (STREET, (609, 96, 658, 235)),
        "graphite_street": (STREET, (500, 186, 522, 394)),
        "glass_street": (STREET, (538, 188, 588, 340)),
        "entry_stone": (STREET, (323, 215, 382, 468)),
        "roof_gravel": (AERIAL, (389, 389, 485, 572)),
        "mechanical": (AERIAL, (604, 298, 683, 346)),
    }
    sampled = {name: _median(path, box) for name, (path, box) in crop_specs.items()}
    palette = {
        "cream_brick": _mix(sampled["brick_street"], (163, 128, 91), 0.58),
        # The photographic palette probe is shadow-heavy. Condition toward the
        # sun-warmed tan/umber masonry visible in the exact street/oblique refs.
        "umber_brick": _mix(sampled["brick_oblique"], (158, 120, 82), 0.72),
        # Keep the bronze warm, but cooler/darker than stained timber; broad
        # patina variation is added in _bronze without baking panel geometry.
        "bronze": _mix(sampled["bronze_street"], (105, 77, 58), 0.76),
        "graphite": _mix(sampled["graphite_street"], (35, 36, 35), 0.78),
        "clear_glass": _mix(sampled["glass_street"], (166, 177, 177), 0.68),
        "fritted_glass": _mix(sampled["glass_street"], (184, 186, 178), 0.62),
        # Exact street evidence shows a pale warm mineral reveal, distinctly
        # lighter than both masonry fields and free of directional shading.
        "entry_stone": _mix(sampled["entry_stone"], (194, 185, 168), 0.84),
        "roof_gravel": _mix(sampled["roof_gravel"], (119, 119, 113), 0.68),
        "mechanical": _mix(sampled["mechanical"], (144, 148, 143), 0.66),
    }

    outputs = {
        "cream_brick_front": OUT / "cream_brick_front_intrinsic.png",
        "cream_brick_return": OUT / "cream_brick_return_intrinsic.png",
        "umber_brick_front": OUT / "umber_brick_front_intrinsic.png",
        "umber_brick_return": OUT / "umber_brick_return_intrinsic.png",
        "weathered_bronze_panel": OUT / "weathered_bronze_panel_intrinsic.png",
        "weathered_bronze_fin": OUT / "weathered_bronze_fin_intrinsic.png",
        "weathered_bronze_coping": OUT / "weathered_bronze_coping_intrinsic.png",
        "weathered_bronze_screen": OUT / "weathered_bronze_screen_intrinsic.png",
        "dark_graphite_frame": OUT / "dark_graphite_frame_intrinsic.png",
        "clear_office_glass": OUT / "clear_office_glass_intrinsic.png",
        "fritted_entry_glass": OUT / "fritted_entry_glass_intrinsic.png",
        "occupied_office_interior_cards": OUT / "occupied_office_interior_atlas.png",
        "entry_concrete_reveal": OUT / "entry_concrete_reveal_intrinsic.png",
        "cast_stone_plinth": OUT / "cast_stone_plinth_intrinsic.png",
        "roof_gravel": OUT / "roof_gravel_intrinsic.png",
        "mechanical_casing": OUT / "mechanical_casing_intrinsic.png",
        "mechanical_duct": OUT / "mechanical_duct_intrinsic.png",
        "mechanical_pipe": OUT / "mechanical_pipe_intrinsic.png",
    }

    _brick(outputs["cream_brick_front"], palette["cream_brick"], 980300, front=True)
    _brick(outputs["cream_brick_return"], _mix(palette["cream_brick"], (139, 111, 82), 0.10), 980301, front=False)
    _brick(outputs["umber_brick_front"], palette["umber_brick"], 980302, front=True)
    _brick(outputs["umber_brick_return"], _mix(palette["umber_brick"], (125, 99, 76), 0.06), 980303, front=False)
    _bronze(outputs["weathered_bronze_panel"], palette["bronze"], 980304, "panel")
    _bronze(outputs["weathered_bronze_fin"], _mix(palette["bronze"], (81, 61, 47), 0.18), 980305, "fin")
    _bronze(outputs["weathered_bronze_coping"], _mix(palette["bronze"], (88, 68, 54), 0.12), 980306, "coping")
    _bronze(outputs["weathered_bronze_screen"], _mix(palette["bronze"], (95, 64, 45), 0.10), 980307, "screen")
    _graphite(outputs["dark_graphite_frame"], palette["graphite"], 980308)
    _glass(outputs["clear_office_glass"], palette["clear_glass"], 980309, fritted=False)
    _glass(outputs["fritted_entry_glass"], palette["fritted_glass"], 980310, fritted=True)
    _registered_office_atlas(outputs["occupied_office_interior_cards"])
    _stone(outputs["entry_concrete_reveal"], palette["entry_stone"], 980312, plinth=False)
    _stone(outputs["cast_stone_plinth"], _mix(palette["entry_stone"], (112, 107, 99), 0.20), 980313, plinth=True)
    _gravel(outputs["roof_gravel"], palette["roof_gravel"], 980314)
    _mechanical_metal(outputs["mechanical_casing"], palette["mechanical"], 980315, "casing")
    _mechanical_metal(outputs["mechanical_duct"], _mix(palette["mechanical"], (169, 171, 165), 0.22), 980316, "duct")
    _mechanical_metal(outputs["mechanical_pipe"], _mix(palette["mechanical"], (181, 183, 177), 0.26), 980317, "pipe")

    records: dict[str, dict[str, object]] = {}
    for role, path in outputs.items():
        with Image.open(path) as image:
            expected = (2048, 1024) if role == "occupied_office_interior_cards" else (SIZE, SIZE)
            if image.size != expected or image.mode != "RGB":
                raise ValueError(f"invalid prepared asset {path.name}: {image.size} {image.mode}")
        records[role] = {
            "path": _repo_path(path),
            "evidence_class": "constrained_completion",
            "generation": "deterministic_code_native_exact_palette_conditioned",
            "contains_printed_modeled_geometry": False,
            "contains_baked_directional_lighting": False,
            "sha256": _hash(path),
        }
    records["occupied_office_interior_cards"]["generation"] = "registered_image_generated_interior_only_master"
    records["occupied_office_interior_cards"]["source_master"] = {
        "path": _repo_path(OFFICE_INTERIOR_MASTER),
        "sha256": _hash(OFFICE_INTERIOR_MASTER),
        "grid": [4, 2],
        "source_dimensions_px": [1774, 887],
        "normalization": "whole-image Lanczos resize to 2048x1024; no crop, seam, or geometric reinterpretation",
    }

    provenance = {
        "schema": "siteforge.sticker-asset-provenance@1",
        "building": "administrative-faculty-office-building--admin-faculty-brick-bronze-fins",
        "variant_index": 0,
        "method": "exact-reference palette conditioning, deterministic intrinsic material synthesis, and one registered interior-only image-generated atlas",
        "reference_authority": "exact variant-0 images override generic parent and rollout metadata",
        "exact_reference_sources": {
            "street_identity": {"path": _repo_path(STREET), "sha256": _hash(STREET), "evidence_class": "exact_reference"},
            "oblique_roof_and_returns": {"path": _repo_path(OBLIQUE), "sha256": _hash(OBLIQUE), "evidence_class": "exact_reference"},
            "aerial_roof_plan": {"path": _repo_path(AERIAL), "sha256": _hash(AERIAL), "evidence_class": "exact_reference"},
        },
        "palette_conditioning": {
            "rule": "fixed, bounds-asserted median probes blended toward bounded material priors; no source pixels pasted",
            "crops_px": {
                name: {"path": _repo_path(path), "box": list(box)} for name, (path, box) in crop_specs.items()
            },
            "sampled_rgb": {key: list(value) for key, value in sampled.items()},
            "prepared_palette_rgb": {key: list(value) for key, value in palette.items()},
        },
        "beauty_correction": {
            "version": "v98.3",
            "entry_reveal": "pale warm mineral concrete/stone, reference-conditioned and intrinsically mottled without directional shading",
            "bronze": "warm bronze base with softly alpha-composited ochre, russet and restrained green-aged patina at broad and fine scales",
            "geometry_exclusions": ["panel boundaries", "fin spacing", "screen spacing", "coping profiles"],
            "registered_office_atlas_preserved": True,
            "optical_balance": "registered office cells neutral-veiled and partially desaturated so physical glazing remains dominant",
        },
        "metadata_admission": {
            "accepted": ["material role names: brick, bronze metal, graphite frames, glass, stone entry, flat gravel roof, mechanical screens"],
            "rejected_or_narrowed": [
                "generic 2-3-storey cream masonry base conflicts with the exact image's full-height warm tan/umber brick fields",
                "double-height corner entrance is narrowed to the tall recessed portal visible on the street view",
            ],
        },
        "geometry_ownership": [
            "all apertures and reveal depth",
            "window and curtain-wall mullions",
            "projecting bronze frame, fins, panel joints and coping profiles",
            "parapets, rooftop screens, ducts, pipes and equipment silhouettes",
            "fritted-glass carrier boundary and entry tunnel section",
        ],
        "glass_contract": "Intrinsic optical fields contain no printed mullions, frame outlines, hard horizons or scene reflections; frit dots are material evidence only.",
        "interior_contract": "The 4x2 office atlas contains shallow occupied office evidence only and no exterior aperture boundaries.",
        "visible_surface_coverage": sorted(records),
        "assets": records,
        "office_atlas_grid": [4, 2],
        "post_generation_nonuniform_scale_allowed": False,
        "image_generation_record": {
            "used": True,
            "purpose": "photoreal shallow occupied-interior evidence behind physical glass",
            "layout": "continuous 4-column x 2-row atlas, eight distinct faculty-office interiors, no separator bars",
            "exclusions": ["windows", "mullions", "exterior walls", "hard horizons", "text", "people", "logos", "exterior sun shadows", "isolation borders"],
            "source_master_sha256": OFFICE_INTERIOR_MASTER_SHA256,
        },
        "approval_space": "locked-carrier multi-view renders with all-face material audit; these intrinsic assets alone do not approve architectural fidelity",
    }
    (OUT / "provenance.json").write_text(json.dumps(provenance, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(OUT), "prepared_assets": len(outputs)}, indent=2))


if __name__ == "__main__":
    main()
