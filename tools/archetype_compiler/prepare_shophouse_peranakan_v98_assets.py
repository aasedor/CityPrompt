"""Prepare deterministic intrinsic Sticker Method assets for the Peranakan shophouse.

The three exact variant-0 images condition palette and material character only.
They are not pasted into an asset: perspective, sunlight, apertures, pilasters,
arches, rails and roof silhouettes remain geometry ownership.
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
OUT = Path(__file__).resolve().parent / "sticker_assets/shophouse_peranakan_v98"
REF = REPO / "frontend/public/archetypes/buildings/shophouse_southeast_asian"
STREET = REF / "variant_0.png"
OBLIQUE = REF / "variant_0_angle_60.jpg"
AERIAL = REF / "variant_0_angle_90.jpg"
SIZE = 1024
ATLAS_SIZE = (2048, 1024)
EXPECTED_REFERENCE_HASHES = {
    STREET: "c388ea502ac3e7cca481063560fd74f17d06bdf354d48ea821d9a71a8bf17a47",
    OBLIQUE: "2751220f0b7511eee91ab94aa0b58cce6e6f4f4734167a4ee87480e610109d03",
    AERIAL: "df32530009a81081a8012e856b1d013f0f05ef3c00a7a4168395c1134c38c5ce",
}
PASTELS = {
    "turquoise": (83, 181, 179), "coral": (213, 126, 116),
    "ochre": (226, 178, 72), "mint": (132, 204, 155),
    "lavender": (182, 157, 204), "cream": (220, 207, 169),
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


def _noise(base: tuple[int, int, int], seed: int, amplitude: int, scale: int = 88) -> Image.Image:
    rng = random.Random(seed)
    small = Image.new("RGB", (scale, scale))
    small.putdata([tuple(_clamp(c + rng.uniform(-amplitude, amplitude)) for c in base)
                   for _ in range(scale * scale)])
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
            time.sleep(.1 * (attempt + 1))


def _atomic_json(data: dict, target: Path) -> None:
    temporary = target.with_name(f".{target.name}.{os.getpid()}.tmp")
    temporary.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    temporary.replace(target)


def _plaster(target: Path, base: tuple[int, int, int], seed: int, *, subdued: float = 0) -> None:
    # Chalky aged limewash: muted chroma, mineral roughness and broad clouding,
    # but no photograph-derived shadow, aperture or architectural boundary.
    colour = _mix(_mix(base, (204, 199, 183), .20), (184, 178, 163), subdued)
    fine = _noise(colour, seed, 4, 104)
    broad = _noise(colour, seed + 1, 14, 11).filter(ImageFilter.GaussianBlur(13))
    image = Image.blend(fine, broad, .38).convert("RGBA")
    rng = random.Random(seed + 2)
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0)); draw = ImageDraw.Draw(overlay)
    # Sparse mineral freckles only. Dense uniform speckle read as procedural
    # noise on the v4 facade and obscured the broader limewash ageing.
    for _ in range(105):
        x, y = rng.randrange(SIZE), rng.randrange(SIZE); r = rng.randrange(2, 9)
        draw.ellipse((x-r, y-r, x+r, y+r), fill=(95, 91, 81, rng.randrange(2, 8)))
    _save(Image.alpha_composite(image, overlay.filter(ImageFilter.GaussianBlur(1.4))), target)


def _paint(target: Path, base: tuple[int, int, int], seed: int, *, fine_relief: bool = False) -> None:
    image = _noise(base, seed, 4, 96).convert("RGBA")
    if fine_relief:
        # Abstract low-relief mineral flecks only; no architectural silhouette.
        rng = random.Random(seed); overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        for _ in range(2100):
            x, y = rng.randrange(SIZE), rng.randrange(SIZE); rx, ry = rng.randrange(2, 13), rng.randrange(1, 6)
            tone = rng.choice(((255, 249, 225), (177, 141, 108), (107, 149, 130), (196, 112, 92)))
            draw.ellipse((x-rx, y-ry, x+rx, y+ry), fill=(*tone, rng.randrange(24, 58)))
        image = Image.alpha_composite(image, overlay.filter(ImageFilter.GaussianBlur(.8)))
    _save(image, target)


def _ornament(target: Path, base: tuple[int, int, int], seed: int) -> None:
    """Dense intrinsic botanical relief; physical meshes still own silhouette."""
    rng = random.Random(seed)
    image = _noise(base, seed, 3, 96).convert("RGBA")
    relief = Image.new("RGBA", image.size, (0, 0, 0, 0)); draw = ImageDraw.Draw(relief)
    dark = _mix(base, (118, 91, 68), .42); light = _mix(base, (250, 238, 204), .46)
    # Continuous 128 px modules: mirrored vines, flower bosses, leaf lobes and
    # pendant drops. They are material relief only—no openings, rails or frames.
    module = 128
    for row, y0 in enumerate(range(-module, SIZE + module, module)):
        for col, x0 in enumerate(range(-module, SIZE + module, module)):
            phase = (row * 5 + col * 3 + seed) % 7
            cy = y0 + module // 2
            points = []
            for step in range(9):
                x = x0 + step * module / 8
                y = cy + (18 if step % 2 else -18) * (1 if phase % 2 else -1)
                points.append((x, y))
            draw.line(points, fill=(*dark, 170), width=9, joint="curve")
            draw.line([(x, y-3) for x, y in points], fill=(*light, 155), width=4, joint="curve")
            for step in (1, 3, 5, 7):
                x, y = points[step]
                rr = 15 + (phase + step) % 5
                draw.ellipse((x-rr, y-rr, x+rr, y+rr), fill=(*dark, 155))
                draw.ellipse((x-rr+5, y-rr+3, x+rr-5, y+rr-7), fill=(*light, 148))
            # Capital-like fan and pendant character inside the repeating field.
            cx = x0 + module // 2
            for dx in (-22, -11, 0, 11, 22):
                draw.ellipse((cx+dx-8, y0+10, cx+dx+8, y0+42), fill=(*light, 145))
            draw.polygon(((cx-15, y0+82), (cx+15, y0+82), (cx, y0+121)), fill=(*dark, 165))
            draw.ellipse((cx-7, y0+105, cx+7, y0+121), fill=(*light, 155))
    _save(Image.alpha_composite(image, relief.filter(ImageFilter.GaussianBlur(.45))), target)


def _tile(target: Path, seed: int, *, walkway: bool) -> None:
    rng = random.Random(seed)
    grout = (187, 179, 158); image = Image.new("RGB", (SIZE, SIZE), grout); draw = ImageDraw.Draw(image)
    # One ceramic motif occupies a credible 0.22–0.25 m module once the
    # compiler maps the square field at the declared metric repeat.
    # Slightly larger motifs than v2 so individual ceramics survive city-view
    # filtering; grout and the whole square panel remain isotropic.
    cell = 160 if walkway else 152
    palette = ((47, 135, 133), (218, 157, 79), (186, 83, 65), (228, 214, 166), (64, 91, 105))
    for row, y in enumerate(range(0, SIZE, cell)):
        for col, x in enumerate(range(0, SIZE, cell)):
            base = palette[(row * 3 + col * 5 + seed) % len(palette)]
            base = _mix(base, (204, 190, 158), .12 + rng.random() * .08)
            draw.rectangle((x+3, y+3, x+cell-3, y+cell-3), fill=base)
            # Flat ceramic motif, deliberately not an aperture or structural grid.
            inset = 13 if walkway else 17
            accent = palette[(row + col + 2) % len(palette)]
            draw.polygon(((x+cell//2, y+inset), (x+cell-inset, y+cell//2),
                          (x+cell//2, y+cell-inset), (x+inset, y+cell//2)), fill=accent)
            draw.ellipse((x+cell//2-5, y+cell//2-5, x+cell//2+5, y+cell//2+5), fill=(232, 219, 177))
    _save(image.filter(ImageFilter.GaussianBlur(.12)), target)


def _ceramic_panel(target: Path, family: int, seed: int) -> None:
    """Whole-unit Peranakan panel family, intrinsic and geometry-free."""
    rng = random.Random(seed)
    grout = (190, 181, 157); image = Image.new("RGB", (SIZE, SIZE), grout); draw = ImageDraw.Draw(image)
    palette = ((37, 124, 126), (215, 151, 69), (179, 73, 59), (230, 215, 167), (58, 83, 99))
    # Four large panels per metric repeat. Geometry owns dado edges/joints; the
    # image owns only ceramic colour and flat floral/scroll ornament.
    cell = 256
    for row, y in enumerate(range(0, SIZE, cell)):
        for col, x in enumerate(range(0, SIZE, cell)):
            base = _mix(palette[(family + row * 2 + col * 3) % len(palette)], (208, 194, 161), .12)
            accent = palette[(family * 2 + row + col + 1) % len(palette)]
            pale = (235, 220, 175)
            draw.rectangle((x+5, y+5, x+cell-5, y+cell-5), fill=base)
            cx, cy = x + cell//2, y + cell//2
            mode = family % 6
            if mode == 0:  # eight-petal rosette
                for angle in range(0, 360, 45):
                    import math
                    dx, dy = math.cos(math.radians(angle))*54, math.sin(math.radians(angle))*54
                    draw.ellipse((cx+dx-27, cy+dy-13, cx+dx+27, cy+dy+13), fill=accent)
                draw.ellipse((cx-25, cy-25, cx+25, cy+25), fill=pale)
            elif mode == 1:  # mirrored S scrolls
                draw.arc((x+30,y+40,x+150,y+210), 250, 100, fill=accent, width=22)
                draw.arc((x+106,y+40,x+226,y+210), 80, 290, fill=accent, width=22)
                draw.ellipse((cx-18,cy-18,cx+18,cy+18),fill=pale)
            elif mode == 2:  # lotus fan
                for dx in (-66,-33,0,33,66):
                    draw.ellipse((cx+dx-25,cy-73,cx+dx+25,cy+35),fill=accent)
                draw.polygon(((x+35,cy+44),(x+cell-35,cy+44),(cx,y+cell-34)),fill=pale)
            elif mode == 3:  # vine quatrefoil
                draw.line((x+24,cy,x+cell-24,cy),fill=accent,width=18)
                for dx in (-72,0,72):
                    for ox,oy in ((-24,0),(24,0),(0,-24),(0,24)):
                        draw.ellipse((cx+dx+ox-19,cy+oy-13,cx+dx+ox+19,cy+oy+13),fill=pale)
            elif mode == 4:  # peony medallion and corner leaves
                draw.ellipse((cx-72,cy-72,cx+72,cy+72),fill=accent)
                for r in (52,31,13): draw.ellipse((cx-r,cy-r,cx+r,cy+r),outline=pale,width=12)
                for ox,oy in ((25,25),(cell-25,25),(25,cell-25),(cell-25,cell-25)):
                    draw.ellipse((x+ox-19,y+oy-9,x+ox+19,y+oy+9),fill=pale)
            else:  # paired foliate scroll and pendant
                draw.arc((x+25,y+35,cx+22,y+185),210,70,fill=accent,width=20)
                draw.arc((cx-22,y+35,x+cell-25,y+185),110,330,fill=accent,width=20)
                draw.polygon(((cx-28,cy+20),(cx+28,cy+20),(cx,cy+94)),fill=pale)
            # Small deterministic glaze variation, not lighting.
            for _ in range(5):
                px=x+rng.randrange(18,cell-18); py=y+rng.randrange(18,cell-18)
                draw.ellipse((px-3,py-3,px+3,py+3),fill=_mix(base,pale,.35))
    _save(image.filter(ImageFilter.GaussianBlur(.10)), target)


def _wood(target: Path, base: tuple[int, int, int], seed: int) -> None:
    rng = random.Random(seed); image = _noise(base, seed, 8, 96).convert("RGBA")
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0)); draw = ImageDraw.Draw(overlay)
    for _ in range(150):
        y = rng.randrange(SIZE); wobble = rng.randrange(-4, 5)
        draw.line((0, y, SIZE, y+wobble), fill=(55, 32, 20, rng.randrange(5, 16)), width=1)
    _save(Image.alpha_composite(image, overlay.filter(ImageFilter.GaussianBlur(.5))), target)


def _glass(target: Path, seed: int) -> None:
    # Neutral optical intrinsic: no scene reflection, horizon, frame or opening.
    field = _noise((205, 214, 211), seed, 3, 72).filter(ImageFilter.GaussianBlur(2.2))
    _save(Image.blend(field, Image.new("RGB", field.size, (230, 229, 221)), .68), target)


def _roof_tile(target: Path, seed: int, *, cap: bool = False) -> None:
    rng = random.Random(seed); base = (159, 72, 48); image = Image.new("RGB", (SIZE, SIZE), (92, 49, 38)); draw = ImageDraw.Draw(image)
    # At compiler repeat 1.0 m, 5 courses/repeat produce 0.20 m pitch.
    course = 205 if not cap else 256; unit = 128 if not cap else 170
    for row, y in enumerate(range(-course, SIZE + course, course)):
        offset = unit // 2 if row % 2 else 0
        for x in range(-unit + offset, SIZE + unit, unit):
            c = _mix(base, (201, 104, 66), .05 + rng.random() * .23)
            # Alternating convex barrel and recessed pan channels. Symmetric
            # centre/edge values encode height rather than a lighting direction.
            barrel = ((x // unit) + row) % 2 == 0
            field = (_mix(c, (224, 132, 82), .20) if barrel
                     else _mix(c, (83, 45, 36), .08))
            draw.rounded_rectangle((x+3, y+5, x+unit-3, y+course+24), radius=unit//2,
                                   fill=field,
                                   outline=_mix(c, (74, 38, 31), .46), width=5)
            bands = 9
            for band in range(bands):
                inset = band * max(1, unit // (bands * 2))
                t = band / (bands - 1)
                height = 1.0 - abs(t * 2.0 - 1.0)
                tone = _mix(_mix(c, (72, 38, 31), .24), (232, 138, 86), height * (.34 if barrel else .12))
                draw.line((x+inset+5, y+22, x+inset+5, y+course+8), fill=tone, width=3)
                draw.line((x+unit-inset-5, y+22, x+unit-inset-5, y+course+8), fill=tone, width=3)
            draw.arc((x+8, y+course-unit//2, x+unit-8, y+course+unit//2), 0, 180,
                     fill=_mix(c, (238, 151, 94), .42 if barrel else .24), width=5)
        # Material lap/recess, not illumination: a neutral intrinsic groove
        # shared across the entire course so it survives city-distance filtering.
        draw.rectangle((0, y+1, SIZE, y+13), fill=(82, 42, 34))
        draw.line((0, y+14, SIZE, y+14), fill=(190, 100, 65), width=3)
    _save(image.filter(ImageFilter.GaussianBlur(.10)), target)


def _metal(target: Path, base: tuple[int, int, int], seed: int) -> None:
    _save(_noise(base, seed, 6, 96).filter(ImageFilter.GaussianBlur(.45)), target)


def _interior(target: Path, seed: int, *, shop: bool) -> None:
    rng = random.Random(seed); atlas = Image.new("RGB", ATLAS_SIZE)
    for index in range(8):
        card = Image.new("RGB", (512, 512), (62, 55, 46) if shop else (68, 61, 52)); draw = ImageDraw.Draw(card, "RGBA")
        draw.rectangle((0, 0, 512, 82), fill=(30, 28, 25, 255))
        for x in (75, 195, 320, 440):
            draw.ellipse((x-13, 40, x+13, 50), fill=(224, 174, 101, 65 + index * 2))
        if shop:
            for shelf in range(3):
                y = 180 + shelf * 85 + rng.randrange(-6, 7)
                draw.rectangle((35, y, 477, y+13), fill=(125, 91, 59, 130))
                for item in range(8):
                    x = 48 + item * 54 + rng.randrange(-5, 6)
                    colour = ((178, 91, 65), (74, 130, 112), (190, 151, 70))[item % 3]
                    draw.rectangle((x, y-35-rng.randrange(0, 14), x+21, y-2), fill=(*colour, 115))
        else:
            draw.rectangle((34, 136, 478, 260), fill=(120, 91, 67, 90))
            for x in (105, 255, 405):
                draw.rectangle((x-35, 325, x+35, 370), fill=(73, 51, 39, 150))
                draw.ellipse((x-26, 292, x+26, 338), fill=(153, 105, 65, 90))
        veil = Image.new("RGB", card.size, (87, 72, 57) if shop else (92, 80, 67))
        atlas.paste(Image.blend(card.filter(ImageFilter.GaussianBlur(.7)), veil, .16), ((index % 4)*512, (index//4)*512))
    _save(atlas, target)


def _contact_sheet(outputs: dict[str, Path]) -> None:
    roles = sorted(outputs); thumb = 160; label = 28; cols = 6
    rows = (len(roles) + cols - 1) // cols
    sheet = Image.new("RGB", (cols*thumb, rows*(thumb+label)), (235, 233, 226)); draw = ImageDraw.Draw(sheet)
    for index, role in enumerate(roles):
        with Image.open(outputs[role]) as source:
            preview = source.convert("RGB").resize((thumb, thumb), Image.Resampling.LANCZOS)
        x, y = (index % cols)*thumb, (index//cols)*(thumb+label)
        sheet.paste(preview, (x, y)); draw.text((x+4, y+thumb+4), role[:24], fill=(30, 30, 30))
    _save(sheet, OUT / "contact_sheet.png")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for path, digest in EXPECTED_REFERENCE_HASHES.items():
        if not path.is_file() or _hash(path) != digest:
            raise ValueError(f"exact reference missing or changed: {path}")

    crops = {
        "turquoise": (STREET, (405, 370, 560, 585)), "coral": (STREET, (880, 420, 1015, 610)),
        "ochre": (STREET, (1110, 355, 1250, 570)), "mint": (STREET, (1570, 360, 1750, 580)),
        "lavender": (STREET, (2250, 340, 2430, 575)), "cream": (OBLIQUE, (1190, 435, 1340, 620)),
        "trim": (STREET, (1320, 315, 1450, 380)), "timber": (STREET, (1250, 470, 1380, 670)),
        "roof": (AERIAL, (400, 120, 980, 420)), "iron": (STREET, (1440, 560, 1610, 720)),
    }
    sampled = {key: _median(path, box) for key, (path, box) in crops.items()}
    palette = {name: _mix(sampled[name], prior, .83) for name, prior in PASTELS.items()}
    palette.update({
        "trim": _mix(sampled["trim"], (225, 216, 185), .86),
        "timber": _mix(sampled["timber"], (79, 47, 31), .88),
        "roof": _mix(sampled["roof"], (185, 83, 48), .91),
        "iron": _mix(sampled["iron"], (53, 52, 46), .92),
    })
    outputs: dict[str, Path] = {}
    for index, name in enumerate(PASTELS):
        for suffix in ("front", "return", "rear"):
            role = f"plaster_{name}_{suffix}"
            outputs[role] = OUT / f"{role}_intrinsic.png"
            _plaster(outputs[role], palette[name], 986000 + index*10 + (0 if suffix == "front" else 1 if suffix == "return" else 2),
                     subdued=0 if suffix == "front" else .12 if suffix == "return" else .25)
    fixed = {
        "pale_trim_relief": "pale_trim_relief_intrinsic.png", "fine_ornament": "fine_ornament_intrinsic.png",
        "ceramic_dado": "peranakan_ceramic_dado_intrinsic.png", "walkway_tile": "five_foot_way_tile_intrinsic.png",
        "carved_dark_timber": "carved_dark_timber_intrinsic.png", "physical_clear_glass": "physical_clear_glass_intrinsic.png",
        "ground_shop_interiors": "ground_shop_interior_atlas.png", "upper_residential_interiors": "upper_residential_interior_atlas.png",
        "terracotta_roof_field": "terracotta_roof_field_intrinsic.png", "terracotta_ridge_cap": "terracotta_ridge_cap_intrinsic.png",
        "party_wall_plaster": "party_wall_plaster_intrinsic.png", "party_wall_coping": "party_wall_coping_intrinsic.png",
        "roof_flashing": "roof_flashing_intrinsic.png", "painted_fretwork_fascia": "painted_fretwork_fascia_intrinsic.png",
        "wrought_iron": "wrought_iron_intrinsic.png", "gutter_downpipe": "gutter_downpipe_intrinsic.png",
        "balcony_plaster": "balcony_plaster_intrinsic.png", "arcade_soffit_reveal": "arcade_soffit_reveal_intrinsic.png",
        "rear_service_finish": "rear_service_finish_intrinsic.png", "threshold_hardware": "threshold_hardware_intrinsic.png",
    }
    outputs.update({role: OUT / filename for role, filename in fixed.items()})
    for family in range(6):
        role = f"ceramic_dado_family_{family}"
        outputs[role] = OUT / f"peranakan_ceramic_dado_family_{family}_intrinsic.png"
    _paint(outputs["pale_trim_relief"], palette["trim"], 986100, fine_relief=True)
    _ornament(outputs["fine_ornament"], _mix(palette["trim"], (205, 179, 143), .18), 986101)
    _tile(outputs["ceramic_dado"], 986102, walkway=False); _tile(outputs["walkway_tile"], 986103, walkway=True)
    for family in range(6):
        _ceramic_panel(outputs[f"ceramic_dado_family_{family}"], family, 986220 + family)
    _wood(outputs["carved_dark_timber"], palette["timber"], 986104); _glass(outputs["physical_clear_glass"], 986105)
    _interior(outputs["ground_shop_interiors"], 986106, shop=True); _interior(outputs["upper_residential_interiors"], 986107, shop=False)
    _roof_tile(outputs["terracotta_roof_field"], 986108); _roof_tile(outputs["terracotta_ridge_cap"], 986109, cap=True)
    _plaster(outputs["party_wall_plaster"], (190, 157, 144), 986110, subdued=.18)
    _paint(outputs["party_wall_coping"], (173, 128, 111), 986111); _metal(outputs["roof_flashing"], (124, 116, 101), 986112)
    _paint(outputs["painted_fretwork_fascia"], _mix(palette["turquoise"], (78, 121, 107), .35), 986113)
    _metal(outputs["wrought_iron"], palette["iron"], 986114); _metal(outputs["gutter_downpipe"], (91, 93, 84), 986115)
    _plaster(outputs["balcony_plaster"], palette["coral"], 986116, subdued=.08)
    _plaster(outputs["arcade_soffit_reveal"], _mix(palette["trim"], (205, 196, 176), .28), 986117, subdued=.12)
    _plaster(outputs["rear_service_finish"], (184, 178, 163), 986118, subdued=.20)
    _metal(outputs["threshold_hardware"], (112, 101, 83), 986119)
    _contact_sheet(outputs)

    atlas_roles = {"ground_shop_interiors", "upper_residential_interiors"}
    records = {}
    for role, path in outputs.items():
        with Image.open(path) as image:
            expected = ATLAS_SIZE if role in atlas_roles else (SIZE, SIZE)
            if image.mode != "RGB" or image.size != expected:
                raise ValueError(f"invalid {role}: {image.mode} {image.size}")
        records[role] = {
            "path": _repo(path), "sha256": _hash(path),
            "evidence_class": "constrained_completion" if role in atlas_roles else "exact_palette_conditioned_intrinsic",
            "contains_printed_openings": False, "contains_printed_pilasters_or_arches": False,
            "contains_printed_rails_or_mullions": False, "contains_baked_directional_lighting": False,
            "contains_printed_reflection_horizon": False,
        }
    contact = OUT / "contact_sheet.png"
    provenance = {
        "schema": "siteforge.sticker-asset-provenance@1",
        "building": "shophouse_southeast_asian--shophouse_peranakan", "variant_index": 0,
        "identity_authority": "three_exact_variant_0_images",
        "exact_reference_sources": {p.name: {"path": _repo(p), "sha256": d, "evidence_class": "exact_reference"}
                                    for p, d in EXPECTED_REFERENCE_HASHES.items()},
        "palette_conditioning": {
            "rule": "bounds-asserted median probes blended strongly toward intrinsic material priors; no source pixels pasted",
            "crops_px": {k: {"path": _repo(p), "box": list(box)} for k, (p, box) in crops.items()},
            "sampled_rgb": {k: list(v) for k, v in sampled.items()}, "prepared_palette_rgb": {k: list(v) for k, v in palette.items()},
        },
        "geometry_ownership": ["openings and arches", "pilasters and capitals", "major plaster relief projection",
                               "balconies and rail silhouettes", "five-foot-way cavern", "roof slopes, dormers and party walls"],
        "tile_contract": "Six deterministic whole-unit ceramic dado families and the walkway asset own flat floral/scroll ceramic pattern only at constant 1m metric scale; geometry owns joints, corners, floor and wall section.",
        "ceramic_panel_families": [f"ceramic_dado_family_{i}" for i in range(6)],
        "glass_contract": "Neutral physical optical field only; no printed mullions, scene reflection, horizon or opening boundary.",
        "interior_contract": "Separate deterministic 4x2 ground-shop and upper-residential cards remain behind physical panes and inside apertures.",
        "roof_contract": "Terracotta field and ridge/cap are disjoint from party-wall plaster, coping, flashing, gutters and dormer geometry.",
        "atlas_grid": [4, 2], "assets": records,
        "contact_sheet": {"path": _repo(contact), "sha256": _hash(contact), "diagnostic_only": True},
        "post_generation_nonuniform_scale_allowed": False,
    }
    _atomic_json(provenance, OUT / "provenance.json")
    print(json.dumps({"output": str(OUT), "prepared_assets": len(outputs), "contact_sheet": str(contact)}, indent=2))


if __name__ == "__main__":
    main()
