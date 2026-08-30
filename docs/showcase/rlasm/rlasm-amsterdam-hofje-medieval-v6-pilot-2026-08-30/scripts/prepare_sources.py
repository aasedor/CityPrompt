from __future__ import annotations

import hashlib
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
CATALOGUE = ROOT / "references" / "catalogue"
MATERIALS = ROOT / "references" / "materials"
IDENTITY = ROOT / "references" / "identity"

SOURCES = {
    "front": (CATALOGUE / "variant_0.png", "99728a7d685f0427a20b5b1946be1589c5308a847e027113d330bd904ac6f925"),
    "front_corner_60": (CATALOGUE / "variant_0_angle_60.jpg", "b4311cde0a2e955989ff5956157442b83df465a3a5aaee6333fce60e6cdec75a"),
    "true_top": (CATALOGUE / "variant_0_angle_90.jpg", "79228135938f59c2632c4b1ff6d545c8592d516937667ef387ff5d1b6e69f482"),
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    names = [
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
    ]
    for name in names:
        if Path(name).exists():
            return ImageFont.truetype(name, size)
    return ImageFont.load_default()


def cover(img: Image.Image, size: tuple[int, int]) -> Image.Image:
    scale = max(size[0] / img.width, size[1] / img.height)
    resized = img.resize((round(img.width * scale), round(img.height * scale)), Image.Resampling.LANCZOS)
    x = (resized.width - size[0]) // 2
    y = (resized.height - size[1]) // 2
    return resized.crop((x, y, x + size[0], y + size[1]))


def locked_board() -> None:
    canvas = Image.new("RGB", (1920, 1280), (232, 229, 220))
    draw = ImageDraw.Draw(canvas)
    draw.text((70, 42), "RLASM v6.1 LOCKED SOURCE BOARD", fill=(28, 30, 29), font=font(54, True))
    draw.text((72, 108), "Amsterdam Hofje / hofje_medieval / variant 0 — exact catalogue pixels", fill=(62, 66, 61), font=font(30))
    roles = [
        ("FRONT", SOURCES["front"][0], (70, 190, 900, 790)),
        ("60° / PLAN+MASSING", SOURCES["front_corner_60"][0], (960, 190, 1850, 790)),
        ("TRUE TOP / ROOF GRAPH", SOURCES["true_top"][0], (455, 835, 1465, 1190)),
    ]
    for role, path, box in roles:
        x0, y0, x1, y1 = box
        panel = cover(Image.open(path).convert("RGB"), (x1 - x0, y1 - y0))
        canvas.paste(panel, (x0, y0))
        draw.rectangle(box, outline=(45, 48, 43), width=4)
        draw.rectangle((x0, y0, x0 + 330, y0 + 50), fill=(26, 29, 27))
        draw.text((x0 + 14, y0 + 9), role, fill=(246, 244, 236), font=font(24, True))
    draw.text((70, 1215), "SHA-256 locked • no sibling mixing • pixels override conflicting catalogue prose", fill=(54, 58, 52), font=font(25, True))
    canvas.save(ROOT / "references" / "locked-source-board.png", quality=95)


def rectify_facade() -> tuple[Image.Image, dict]:
    src_path = SOURCES["front_corner_60"][0]
    bgr = cv2.imread(str(src_path), cv2.IMREAD_COLOR)
    # Courtyard-facing north wing; points follow the exposed brick carrier edges,
    # not the surrounding perspective context.
    src = np.float32([[278, 300], [785, 330], [784, 616], [272, 603]])
    dst = np.float32([[0, 0], [1599, 0], [1599, 799], [0, 799]])
    matrix = cv2.getPerspectiveTransform(src, dst)
    rect = cv2.warpPerspective(bgr, matrix, (1600, 800), flags=cv2.INTER_CUBIC)
    rgb = cv2.cvtColor(rect, cv2.COLOR_BGR2RGB)
    out = Image.fromarray(rgb)
    out.save(IDENTITY / "rectified-courtyard-facade-reference.png")
    return out, {
        "source": str(src_path.relative_to(ROOT)),
        "source_quad_px": src.astype(int).tolist(),
        "output_size_px": [1600, 800],
        "operation": "four-point projective rectification of the courtyard-facing north elevation",
        "mounted": False,
        "reason": "registration/measurement authority only; physical openings and carriers own the facade"
    }


def mirror_tile(patch: Image.Image, size: int = 1024, contrast: float = 1.0, saturation: float = 1.0) -> Image.Image:
    patch = patch.convert("RGB")
    patch = ImageEnhance.Contrast(patch).enhance(contrast)
    patch = ImageEnhance.Color(patch).enhance(saturation)
    quad = Image.new("RGB", (patch.width * 2, patch.height * 2))
    quad.paste(patch, (0, 0))
    quad.paste(patch.transpose(Image.Transpose.FLIP_LEFT_RIGHT), (patch.width, 0))
    quad.paste(patch.transpose(Image.Transpose.FLIP_TOP_BOTTOM), (0, patch.height))
    quad.paste(patch.transpose(Image.Transpose.ROTATE_180), (patch.width, patch.height))
    tiled = Image.new("RGB", (size, size))
    for y in range(0, size, quad.height):
        for x in range(0, size, quad.width):
            tiled.paste(quad, (x, y))
    return tiled


def tonal_sheet(source: Image.Image, crop: tuple[int, int, int, int], name: str, *, size: int = 1024, contrast: float = 1.0, saturation: float = 1.0, blur: float = 0.0) -> dict:
    patch = source.crop(crop)
    if blur:
        patch = patch.filter(ImageFilter.GaussianBlur(blur))
    sheet = mirror_tile(patch, size=size, contrast=contrast, saturation=saturation)
    path = MATERIALS / name
    sheet.save(path)
    return {
        "path": str(path.relative_to(ROOT)),
        "source": "references/catalogue/variant_0.png",
        "crop_px": list(crop),
        "operation": "exact-source crop, mirror-seam conditioning, restrained contrast/saturation normalization",
        "sha256": sha256(path)
    }


def sampled_swatch(source: Image.Image, crop: tuple[int, int, int, int], name: str, *, size: int = 1024, contrast: float = 1.0, saturation: float = 1.0, selector: str = "all") -> dict:
    """Build a projection-clean role swatch from the exact crop's pixel distribution.

    This deliberately removes photographed objects and perspective while retaining
    the locked source's mean, covariance, patina, and fine stochastic variation.
    It is used only for small trim/optical roles whose morphology is carried by
    geometry; brick and pantile retain literal source morphology below.
    """
    patch = np.asarray(source.crop(crop).convert("RGB"), dtype=np.float32)
    pixels = patch.reshape(-1, 3)
    r, g, b = pixels[:, 0], pixels[:, 1], pixels[:, 2]
    mean = pixels.mean(axis=1)
    chroma = pixels.max(axis=1) - pixels.min(axis=1)
    selectors = {
        "stone": (chroma < 62) & (mean > 115),
        "neutral": (chroma < 42) & (mean > 55) & (mean < 215),
        "dark_neutral": (chroma < 48) & (mean > 24) & (mean < 105),
        "green": (g > r * 1.02) & (g > b * 1.05) & (mean > 32) & (mean < 150),
        "glass": (chroma < 70) & (mean > 72) & (mean < 205),
        "flower": (r > g * 1.14) & (r > b * 1.18) & (mean > 55) & (mean < 205),
        "warm_plaster": (r > g * 1.025) & (g > b * 1.025) & (chroma < 82) & (mean > 72) & (mean < 188),
    }
    if selector in selectors and np.any(selectors[selector]):
        pixels = pixels[selectors[selector]]
    lo = np.percentile(pixels, 15, axis=0)
    hi = np.percentile(pixels, 85, axis=0)
    keep = np.all((pixels >= lo) & (pixels <= hi), axis=1)
    pixels = pixels[keep] if np.any(keep) else pixels
    rng = np.random.default_rng(61029)
    picks = pixels[rng.integers(0, len(pixels), size * size)].reshape(size, size, 3)
    # Low-amplitude spatial correlation preserves patina without reconstructing
    # photographed windows, gates, plants, or full architectural fragments.
    swatch = Image.fromarray(np.clip(picks, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2))
    swatch = ImageEnhance.Contrast(swatch).enhance(contrast)
    swatch = ImageEnhance.Color(swatch).enhance(saturation)
    path = MATERIALS / name
    swatch.save(path)
    return {
        "path": str(path.relative_to(ROOT)),
        "source": "references/catalogue/variant_0.png",
        "crop_px": list(crop),
        "operation": "exact-source robust pixel-distribution swatch; photographed objects and perspective removed; deterministic seed 61029",
        "sha256": sha256(path)
    }


def warm_source_pixels(source: Image.Image, crop: tuple[int, int, int, int], *, dark: bool = False) -> np.ndarray:
    arr = np.asarray(source.crop(crop).convert("RGB"), dtype=np.float32).reshape(-1, 3)
    r, g, b = arr[:, 0], arr[:, 1], arr[:, 2]
    value = arr.mean(axis=1)
    if dark:
        mask = (r > g * 1.08) & (r > b * 1.18) & (g > b * 0.94) & (value > 38) & (value < 145)
    else:
        mask = (r > g * 1.11) & (r > b * 1.25) & (g > b * 1.05) & (value > 55) & (value < 185)
    picked = arr[mask]
    if len(picked) < 128:
        picked = arr
    lo = np.percentile(picked, 10, axis=0)
    hi = np.percentile(picked, 90, axis=0)
    picked = picked[np.all((picked >= lo) & (picked <= hi), axis=1)]
    # Keep the family authority coherent across sun and shade; retain source
    # variation but pull extreme sampled pixels toward the exact-source median.
    median = np.median(picked, axis=0)
    picked = median + (picked - median) * (0.34 if dark else 0.28)
    return picked.astype(np.uint8)


def source_specific_brick_sheet(source: Image.Image, path: Path) -> None:
    """Observed hofje stretcher bond: ~210 x 55 mm brick, ~10 mm pale joint."""
    rng = np.random.default_rng(61031)
    pixels = warm_source_pixels(source, (600, 120, 900, 590), dark=False)
    # Locked references are dark red-brown masonry; normalize the sun-biased
    # sample population back toward the facade's robust shadow/sun midpoint.
    canvas = Image.new("RGB", (1024, 1024), (126, 101, 82))
    draw = ImageDraw.Draw(canvas)
    # v014 retains the photographed bond scale while restoring the locked warmth.
    # At the audited 2.4 m sheet width this resolves close to the source's
    # 210 x 55 mm units instead of the oversized v006 reading.
    course_h = 22
    brick_w = 76
    joint = 2
    for row, y in enumerate(range(-course_h, 1024 + course_h, course_h)):
        offset = -brick_w // 2 if row % 2 else 0
        for x in range(offset - brick_w, 1024 + brick_w, brick_w):
            sample = pixels[rng.integers(0, len(pixels))].astype(np.int16)
            sample = np.clip(sample + rng.integers(-8, 9, 3), 0, 255).astype(np.uint8)
            sample = np.clip(sample.astype(np.float32) * np.array([0.96, 0.88, 0.82]), 0, 255).astype(np.uint8)
            box = (x + joint, y + joint, x + brick_w - joint, y + course_h - joint)
            draw.rounded_rectangle(box, radius=2, fill=tuple(int(v) for v in sample))
            # Source-observed fired variation and worn arrises, never a second material family.
            if rng.random() < 0.55:
                shade = tuple(int(max(0, v - rng.integers(3, 13))) for v in sample)
                draw.line((box[0] + 3, box[3] - 2, box[2] - 3, box[3] - 2), fill=shade, width=1)
            if rng.random() < 0.18:
                hi = tuple(int(min(255, v + rng.integers(5, 16))) for v in sample)
                draw.line((box[0] + 5, box[1] + 2, box[2] - 5, box[1] + 2), fill=hi, width=1)
    # Add only micro-scale variation sampled from the same locked carrier.
    arr = np.asarray(canvas, dtype=np.int16)
    noise = rng.normal(0, 2.2, arr.shape[:2])[..., None]
    arr = np.clip(arr + noise, 0, 255).astype(np.uint8)
    Image.fromarray(arr).save(path)


def source_specific_pantile_sheet(source: Image.Image, path: Path) -> None:
    """Observed weathered Dutch pantiles: overlapping warm-dark S-profile rows."""
    rng = np.random.default_rng(61037)
    pixels = warm_source_pixels(source, (310, 45, 890, 315), dark=True)
    roof_gain = np.array([1.16, 0.91, 0.70])
    median = np.median(pixels, axis=0)
    target = np.clip(np.percentile(pixels, 42, axis=0) * roof_gain, 0, 255)
    base = tuple(int(v) for v in target)
    size = 2048
    canvas = Image.new("RGB", (size, size), base)
    draw = ImageDraw.Draw(canvas)
    # The locked roofs read as a coherent orange-red field whose S-rolls carry
    # the variation. Keep per-tile colour drift subordinate so the sheet cannot
    # become a pink rectangular patch grid at whole-roof scale.
    y = -46
    row = 0
    while y < size + 48:
        row_h = int(rng.integers(38, 44))
        nominal_w = int(rng.integers(44, 52))
        phase = int(rng.integers(-nominal_w, nominal_w))
        if row % 2:
            phase -= nominal_w // 2
        row_tint = rng.integers(-3, 4, 3) + np.array([rng.integers(-1, 3), 0, rng.integers(-2, 2)])
        x = phase - nominal_w
        while x < size + nominal_w:
            tile_w = int(np.clip(nominal_w + rng.integers(-3, 4), 41, 55))
            sample = pixels[rng.integers(0, len(pixels))].astype(np.float32)
            sample = target + (sample * roof_gain - target) * 0.10 + row_tint + rng.integers(-2, 3, 3)
            sample = np.clip(sample, 0, 255).astype(np.uint8)
            c = tuple(int(v) for v in sample)
            dark_c = tuple(int(max(0, v - rng.integers(14, 20))) for v in sample)
            light_c = tuple(int(min(255, v + rng.integers(7, 13))) for v in sample)
            draw.rounded_rectangle((x, y, x + tile_w + 1, y + row_h + 4), radius=6, fill=c)
            wave = max(9, int(tile_w * 0.25))
            draw.rounded_rectangle((x + 1, y + 2, x + 2 + wave, y + row_h + 1), radius=wave // 2, fill=dark_c)
            draw.arc((x + int(tile_w * 0.29), y + 1, x + int(tile_w * 0.78), y + row_h + 5), 72, 285, fill=light_c, width=3)
            draw.arc((x + 1, y + row_h - 15, x + tile_w, y + row_h + 8), 180, 360, fill=dark_c, width=2)
            if rng.random() < 0.07:
                patina = tuple(int(np.clip(v + d, 0, 255)) for v, d in zip(c, (-7, 2, 0)))
                draw.line((x + tile_w * 0.34, y + 8, x + tile_w * 0.42, y + row_h - 6), fill=patina, width=2)
            x += tile_w
        lap = tuple(int(max(0, v - int(rng.integers(9, 14)))) for v in base)
        draw.line((0, y + row_h - 1, size, y + row_h - 1), fill=lap, width=2)
        y += row_h
        row += 1
    arr = np.asarray(canvas, dtype=np.int16)
    coarse = rng.normal(0, 1, (128, 128))
    coarse = np.asarray(Image.fromarray(np.uint8(np.clip(coarse * 28 + 128, 0, 255))).resize((size, size), Image.Resampling.BICUBIC), dtype=np.float32)
    coarse = (coarse - 128.0)[..., None] * np.array([0.10, 0.07, 0.05])
    noise = rng.normal(0, 1.4, arr.shape[:2])[..., None]
    Image.fromarray(np.clip(arr + coarse + noise, 0, 255).astype(np.uint8)).save(path)


def source_specific_gravel_sheet(source: Image.Image, path: Path) -> None:
    """Warm granular court gravel from the locked top-reference path pixels."""
    rng = np.random.default_rng(61043)
    arr = np.asarray(source.crop((430, 330, 850, 720)).convert("RGB"), dtype=np.float32).reshape(-1, 3)
    r, g, b = arr[:, 0], arr[:, 1], arr[:, 2]
    value = arr.mean(axis=1)
    chroma = arr.max(axis=1) - arr.min(axis=1)
    picked = arr[(r > g * 1.015) & (g > b * 1.01) & (chroma < 62) & (value > 82) & (value < 196)]
    if len(picked) < 256:
        picked = arr[(chroma < 68) & (value > 78) & (value < 205)]
    lo, hi = np.percentile(picked, 12, axis=0), np.percentile(picked, 88, axis=0)
    picked = picked[np.all((picked >= lo) & (picked <= hi), axis=1)]
    size = 1536
    coarse = picked[rng.integers(0, len(picked), 128 * 128)].reshape(128, 128, 3)
    image = Image.fromarray(np.uint8(coarse)).resize((size, size), Image.Resampling.BICUBIC).filter(ImageFilter.GaussianBlur(0.45))
    draw = ImageDraw.Draw(image)
    for _ in range(26000):
        x, y = int(rng.integers(0, size)), int(rng.integers(0, size))
        c = picked[rng.integers(0, len(picked))]
        radius = int(rng.integers(1, 4))
        shade = tuple(int(v) for v in np.clip(c * rng.uniform(0.82, 1.10), 0, 255))
        draw.ellipse((x-radius, y-radius//2, x+radius, y+max(1, radius//2)), fill=shade)
    image.save(path)


def source_specific_lawn_sheet(source: Image.Image, path: Path) -> None:
    """Non-periodic lawn patina from only the locked top-reference greens."""
    rng = np.random.default_rng(61041)
    arr = np.asarray(source.crop((510, 360, 770, 690)).convert("RGB"), dtype=np.float32).reshape(-1, 3)
    r, g, b = arr[:, 0], arr[:, 1], arr[:, 2]
    value = arr.mean(axis=1)
    picked = arr[(g > r * 1.02) & (g > b * 1.05) & (value > 30) & (value < 155)]
    if len(picked) < 256:
        picked = arr
    lo, hi = np.percentile(picked, 12, axis=0), np.percentile(picked, 88, axis=0)
    picked = picked[np.all((picked >= lo) & (picked <= hi), axis=1)]
    size = 1536
    fine = picked[rng.integers(0, len(picked), size * size)].reshape(size, size, 3)
    coarse = picked[rng.integers(0, len(picked), 96 * 96)].reshape(96, 96, 3)
    coarse = np.asarray(Image.fromarray(np.uint8(coarse)).resize((size, size), Image.Resampling.BICUBIC), dtype=np.float32)
    mixed = coarse * 0.72 + fine * 0.28
    image = Image.fromarray(np.uint8(np.clip(mixed, 0, 255))).filter(ImageFilter.GaussianBlur(0.55))
    draw = ImageDraw.Draw(image)
    for _ in range(1750):
        x, y = int(rng.integers(0, size)), int(rng.integers(0, size))
        c = picked[rng.integers(0, len(picked))] * np.array([0.80, 0.88, 0.78])
        length = int(rng.integers(2, 8))
        draw.line((x, y, x + int(rng.integers(-2, 3)), y - length), fill=tuple(int(v) for v in np.clip(c, 0, 255)), width=1)
    image.save(path)


def make_materials(rectified: Image.Image) -> list[dict]:
    front = Image.open(SOURCES["front"][0]).convert("RGB")
    top = Image.open(SOURCES["true_top"][0]).convert("RGB")
    records: list[dict] = []

    brick_path = MATERIALS / "hofje-medieval-aged-stretcher-brick-albedo-v1.png"
    source_specific_brick_sheet(front, brick_path)
    records.append({
        "role": "brick_carriers_returns_chimneys",
        "path": str(brick_path.relative_to(ROOT)),
        "source": "references/catalogue/variant_0.png",
        "source_regions_px": [[600, 120, 900, 590]],
        "morphology": "source-measured warm red-brown stretcher bond; approximately 210 x 55 mm fired units with pale 10 mm joints, alternating half-bond phase and worn arrises",
        "operation": "deterministic exact-source pixel population mapped into the observed bond; sun-biased values chromatically normalized to the locked facade midpoint; no photographed architectural fragment retained",
        "physical_scale_m": [2.4, 3.2],
        "axes": "wall-local X-Z or Y-Z with one shared phase per wing",
        "sha256": sha256(brick_path)
    })

    roof_path = MATERIALS / "hofje-medieval-weathered-pantile-albedo-v1.png"
    source_specific_pantile_sheet(top, roof_path)
    roof_rec = {
        "role": "pantile_roof",
        "path": str(roof_path.relative_to(ROOT)),
        "source": "references/catalogue/variant_0_angle_90.jpg",
        "source_regions_px": [[310, 45, 890, 315]],
        "morphology": "source-measured overlapping warm-dark Dutch pantile rows with alternating half-tile phase, rounded lower edges and weathered S-profile highlights",
        "operation": "deterministic exact-source pixel population mapped into observed pantile cadence; sun-biased values chromatically normalized to the locked roof midpoint; no dormer, chimney, eave, sky or neighbouring building retained",
        "physical_scale_m": [2.2, 3.0],
        "axes": "slope-local across/down-slope",
        "sha256": sha256(roof_path)
    }
    records.append(roof_rec)

    # Small roles use projection-clean source-distribution swatches. Their
    # construction morphology is physical geometry (profiles, frames, rods,
    # panes, paths, hedge solids), not photographed architecture.
    swatch_specs = [
        ("pale_stone_trim", front, (646, 302, 858, 327), "hofje-medieval-pale-stone-trim-albedo-v1.png", 0.8, 1.02, 0.58, "stone"),
        ("painted_timber", front, (500, 500, 548, 624), "hofje-medieval-deep-green-painted-timber-albedo-v1.png", 0.25, 1.03, 0.95, "green"),
        ("wrought_iron", front, (565, 593, 682, 681), "hofje-medieval-wrought-iron-albedo-v1.png", 0.45, 1.12, 0.48, "dark_neutral"),
        ("low_iron_glass_tint", front, (686, 356, 735, 474), "hofje-medieval-residential-glass-tint-v1.png", 0.45, 0.82, 0.52, "glass"),
        ("aged_lead_dormer_flashings", top, (350, 95, 880, 430), "hofje-medieval-aged-lead-albedo-v1.png", 0.65, 0.88, 0.18, "stone"),
        ("pale_painted_dormer_sash", top, (350, 95, 880, 430), "hofje-medieval-pale-painted-dormer-sash-v1.png", 0.25, 0.92, 0.20, "stone"),
        ("courtyard_gravel", top, (510, 330, 800, 625), "hofje-medieval-courtyard-gravel-albedo-v1.png", 1.2, 1.06, 0.72, "warm_plaster"),
        ("garden_lawn", top, (510, 360, 770, 690), "hofje-medieval-courtyard-lawn-albedo-v1.png", 1.3, 1.06, 1.02, "green"),
        ("hedge_foliage", front, (350, 559, 485, 602), "hofje-medieval-clipped-hedge-albedo-v1.png", 0.8, 1.12, 1.06, "green"),
        ("courtyard_flowers", front, (338, 540, 620, 646), "hofje-medieval-courtyard-flower-albedo-v1.png", 0.18, 1.08, 1.08, "flower"),
        ("warm_interior_plaster", front, (580, 250, 900, 570), "hofje-medieval-warm-interior-plaster-albedo-v1.png", 0.9, 0.92, 0.58, "warm_plaster"),
    ]
    for role, source, crop, filename, scale, contrast, saturation, selector in swatch_specs:
        rec = sampled_swatch(source, crop, filename, contrast=contrast, saturation=saturation, selector=selector)
        if role == "garden_lawn":
            source_specific_lawn_sheet(top, ROOT / rec["path"])
            rec["operation"] = "deterministic non-periodic exact-source green population; multi-scale patina and sparse source-family tufts; no photographed object or generic turf"
            rec["sha256"] = sha256(ROOT / rec["path"])
        if role == "courtyard_gravel":
            source_specific_gravel_sheet(top, ROOT / rec["path"])
            rec["operation"] = "deterministic exact-source warm path population with source-scale granular aggregate; no photographed object or generic paving"
            rec["sha256"] = sha256(ROOT / rec["path"])
        rec.update({"role": role, "physical_scale_m": [scale, scale]})
        records.append(rec)

    board = Image.new("RGB", (1800, 1500), (229, 226, 216))
    d = ImageDraw.Draw(board)
    d.text((55, 34), "EXACT-SOURCE MATERIAL AUTHORITY", fill=(28, 30, 27), font=font(48, True))
    d.text((58, 92), "Amsterdam Hofje / variant 0 — no generic fallback materials", fill=(66, 67, 61), font=font(28))
    for i, record in enumerate(records):
        x = 55 + (i % 3) * 580
        y = 155 + (i // 3) * 330
        img = cover(Image.open(ROOT / record["path"]).convert("RGB"), (530, 245))
        board.paste(img, (x, y))
        d.rectangle((x, y, x + 530, y + 245), outline=(45, 48, 43), width=3)
        d.rectangle((x, y + 197, x + 530, y + 245), fill=(24, 27, 25))
        d.text((x + 12, y + 206), record["role"].replace("_", " ").upper(), fill=(244, 241, 232), font=font(20, True))
    board.save(ROOT / "references" / "source-conditioned-material-board.png")
    return records


def main() -> None:
    MATERIALS.mkdir(parents=True, exist_ok=True)
    IDENTITY.mkdir(parents=True, exist_ok=True)
    verified = []
    for role, (path, expected) in SOURCES.items():
        actual = sha256(path)
        if actual != expected:
            raise SystemExit(f"source hash mismatch: {role}: {actual} != {expected}")
        verified.append({"role": role, "path": str(path.relative_to(ROOT)), "bytes": path.stat().st_size, "sha256": actual})
    locked_board()
    rectified, rect_record = rectify_facade()
    material_records = make_materials(rectified)
    provenance = {
        "schema": "cityprompt.rlasm.asset-provenance@6.1",
        "candidate_id": "rlasm-amsterdam-hofje-medieval-v023",
        "sources": verified,
        "identity_derivatives": [rect_record],
        "material_generation": {
            "provider": "deterministic local OpenCV/Pillow conditioning",
            "model": None,
            "generative_ai_used": False,
            "prompt": "Rectify exact locked hofje pixels to shadow-neutral wall/roof coordinates; isolate repeating substance morphology; remove perspective context by bounded crop and projective transform; preserve brick bond, mortar scale, pantile cadence, age, roughness cues and source hue; create no invented facade fragments, windows, lighting, text or generic fallback material.",
            "operations": ["four-point rectification", "bounded exact-source crops", "mirror seam conditioning", "restrained tonal normalization"],
            "materials": material_records
        },
        "one_visual_owner_per_feature": True,
        "perspective_crop_mounted_on_facade": False
    }
    prov_path = ROOT / "references" / "asset-provenance.json"
    prov_path.write_text(json.dumps(provenance, indent=2), encoding="utf-8")
    print(json.dumps({"status": "prepared", "sources": len(verified), "materials": len(material_records), "provenance_sha256": sha256(prov_path)}, indent=2))


if __name__ == "__main__":
    main()
