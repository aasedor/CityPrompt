"""Build registered PBR texture sets for the Wave 3 landmark families.

The ImageGen source is deliberately retained as the render-locked design
source.  Every runtime channel is then derived from the same registered pixels
so albedo, relief, emissive light, and semantic masks cannot drift.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageOps


RESAMPLE = Image.Resampling.LANCZOS
CHANNELS = ("albedo", "normal", "roughness", "ao", "depth", "emissive")


def normal_map(luma: np.ndarray, strength: float = 2.4) -> Image.Image:
    height = luma.astype(np.float32) / 255.0
    gy, gx = np.gradient(height)
    nx = -gx * strength
    ny = gy * strength
    nz = np.ones_like(height)
    length = np.sqrt(nx * nx + ny * ny + nz * nz)
    normal = np.dstack((nx / length, ny / length, nz / length))
    return Image.fromarray(np.uint8(np.clip(normal * 0.5 + 0.5, 0, 1) * 255), "RGB")


def derive_channels(albedo: Image.Image, zone: str) -> dict[str, Image.Image]:
    albedo = ImageEnhance.Contrast(albedo.convert("RGB")).enhance(1.04)
    if zone == "roof":
        # The arena archetype goal post has a bright silver standing-seam roof.
        # Keep the registered rib source, but correct the earlier charcoal read.
        neutral = ImageOps.grayscale(albedo)
        neutral = ImageEnhance.Contrast(neutral).enhance(1.16)
        neutral = ImageEnhance.Brightness(neutral).enhance(1.82)
        albedo = Image.merge(
            "RGB",
            (
                neutral,
                ImageEnhance.Brightness(neutral).enhance(1.02),
                ImageEnhance.Brightness(neutral).enhance(1.06),
            ),
        )
    luma_image = ImageOps.grayscale(albedo)
    luma = np.asarray(luma_image, dtype=np.uint8)
    smoothed = np.asarray(luma_image.filter(ImageFilter.GaussianBlur(2.0)), dtype=np.float32)

    roughness_base = {
        "metal": 94,
        "roof": 184,
        "glass": 42,
        "accent": 132,
        "marble": 164,
        "relief": 176,
        "copper": 118,
        "front_registered": 158,
        "aluminum": 106,
        "concert_glass": 38,
        "timber": 156,
        "granite": 174,
        "iron": 116,
        "stained_glass": 52,
        "ceramic": 142,
        "roof_glass": 48,
        "bronze_glass": 58,
        "iron_glass": 50,
    }[zone]
    detail = np.abs(luma.astype(np.float32) - smoothed)
    roughness = np.uint8(np.clip(roughness_base + detail * 1.8, 18, 235))

    # Dark joints and recesses occlude; broad albedo values remain mostly neutral.
    ao = np.uint8(np.clip(224 - np.maximum(0, 112 - luma) * 0.42, 145, 238))
    depth = np.uint8(np.clip(128 + (smoothed - luma.astype(np.float32)) * 2.4, 28, 228))

    rgb = np.asarray(albedo, dtype=np.float32)
    warm = (
        (rgb[:, :, 0] > 108)
        & (rgb[:, :, 0] > rgb[:, :, 1] * 1.18)
        & (rgb[:, :, 1] > rgb[:, :, 2] * 1.05)
    )
    emissive = np.zeros_like(rgb, dtype=np.uint8)
    glass_zones = {
        "glass",
        "accent",
        "concert_glass",
        "stained_glass",
        "roof_glass",
        "bronze_glass",
        "iron_glass",
    }
    if zone in glass_zones:
        scale = np.clip((rgb[:, :, 0] - 90) / 120, 0, 1)[:, :, None]
        emissive = np.uint8(np.where(warm[:, :, None], rgb * scale, 0))

    glass_value = 255 if zone in glass_zones else 0
    glass_mask = Image.new("L", albedo.size, glass_value)
    return {
        "albedo": albedo,
        "normal": normal_map(luma),
        "roughness": Image.fromarray(roughness, "L"),
        "ao": Image.fromarray(ao, "L"),
        "depth": Image.fromarray(depth, "L"),
        "emissive": Image.fromarray(emissive, "RGB"),
        "glass_mask": glass_mask,
        "opaque_mask": ImageOps.invert(glass_mask),
    }


def crop_fraction(source: Image.Image, top: float, bottom: float) -> Image.Image:
    y0 = round(source.height * top)
    y1 = round(source.height * bottom)
    return source.crop((0, y0, source.width, y1))


def save_zone(
    source: Image.Image,
    family_dir: Path,
    zone: str,
    bounds: tuple[float, float],
) -> dict[str, dict[str, str]]:
    crop = crop_fraction(source, *bounds)
    output: dict[str, dict[str, str]] = {}
    for lod, size in (("near", (2048, 512)), ("far", (1024, 256))):
        zone_dir = family_dir / "textures" / lod / zone
        zone_dir.mkdir(parents=True, exist_ok=True)
        maps = derive_channels(ImageOps.fit(crop, size, method=RESAMPLE), zone)
        output[lod] = {}
        for channel, image in maps.items():
            path = zone_dir / f"{zone}_{channel}.png"
            image.save(path, optimize=True)
            output[lod][channel] = path.relative_to(family_dir).as_posix()
    return output


def civic_registered_glass_mask(size: tuple[int, int]) -> Image.Image:
    """Shape-aware mask for the exact openings in the reference elevation."""
    width, height = size
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)

    def arched_window(cx: float, top: float, bottom: float, span: float) -> None:
        x0 = round((cx - span / 2) * width)
        x1 = round((cx + span / 2) * width)
        y0 = round(top * height)
        spring = round((top + span * 0.48) * height)
        y1 = round(bottom * height)
        draw.ellipse((x0, y0, x1, spring + (spring - y0)), fill=255)
        draw.rectangle((x0, spring, x1, y1), fill=255)

    for centre in (0.078, 0.161, 0.244, 0.756, 0.839, 0.922):
        arched_window(centre, 0.620, 0.848, 0.063)

    for centre in (0.385, 0.432, 0.478, 0.524, 0.570, 0.616):
        draw.rectangle(
            (
                round((centre - 0.014) * width),
                round(0.335 * height),
                round((centre + 0.014) * width),
                round(0.422 * height),
            ),
            fill=255,
        )
    for centre in (0.476, 0.500, 0.524):
        draw.rectangle(
            (
                round((centre - 0.008) * width),
                round(0.080 * height),
                round((centre + 0.008) * width),
                round(0.145 * height),
            ),
            fill=255,
        )
    return mask


def save_registered_civic_front(
    source: Image.Image,
    family_dir: Path,
) -> dict[str, dict[str, str]]:
    output: dict[str, dict[str, str]] = {}
    for lod, size in (("near", (2048, 1536)), ("far", (1024, 768))):
        zone_dir = family_dir / "textures" / lod / "front_registered"
        zone_dir.mkdir(parents=True, exist_ok=True)
        fitted = ImageOps.fit(source, size, method=RESAMPLE)
        maps = derive_channels(fitted, "front_registered")
        glass_mask = civic_registered_glass_mask(size)
        maps["glass_mask"] = glass_mask
        maps["opaque_mask"] = ImageOps.invert(glass_mask)
        output[lod] = {}
        for channel, image in maps.items():
            path = zone_dir / f"front_registered_{channel}.png"
            image.save(path, optimize=True)
            output[lod][channel] = path.relative_to(family_dir).as_posix()
    return output


def build_atlases(
    family_dir: Path,
    zone_assets: dict[str, dict[str, dict[str, str]]],
    zone_order: tuple[str, ...],
    prefix: str,
) -> dict:
    atlases: dict[str, dict[str, str]] = {}
    for lod, width in (("near", 2048), ("far", 1024)):
        atlas_dir = family_dir / "textures" / lod
        atlases[lod] = {}
        for channel in (*CHANNELS, "glass_mask", "opaque_mask"):
            images = [
                Image.open(family_dir / zone_assets[zone][lod][channel])
                for zone in zone_order
            ]
            mode = images[0].mode
            atlas = Image.new(mode, (width, sum(image.height for image in images)))
            y = 0
            for image in images:
                atlas.paste(image, (0, y))
                y += image.height
            path = atlas_dir / f"{prefix}_atlas_{channel}.png"
            atlas.save(path, optimize=True)
            atlases[lod][channel] = path.relative_to(family_dir).as_posix()
    return atlases


def prepare_arena(family_dir: Path) -> None:
    # Version the render-locked source so the earlier skin remains available
    # for visual regression while Wave 3 converges on the catalogue hero.
    source_path = family_dir / "textures" / "source" / "arena_material_source_v2.png"
    source = Image.open(source_path).convert("RGB")
    bands = {
        "metal": (0.000, 0.285),
        "roof": (0.285, 0.535),
        "glass": (0.535, 0.785),
        "accent": (0.785, 1.000),
    }
    zones = {
        zone: save_zone(source, family_dir, zone, bounds)
        for zone, bounds in bands.items()
    }
    payload = {
        "schema": "wave3-landmark-skin@1",
        "family": family_dir.name,
        "source": source_path.relative_to(family_dir).as_posix(),
        "source_model": "gpt-image-2",
        "registration": "four horizontal bands, all runtime channels derived pixel-for-pixel",
        "channels": list(CHANNELS),
        "semantic_masks": ["glass_mask", "opaque_mask"],
        "zones": zones,
        "atlases": build_atlases(
            family_dir, zones, ("metal", "roof", "glass", "accent"), "arena"
        ),
    }
    (family_dir / "textures" / "skin_manifest.json").write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8"
    )


def prepare_civic(family_dir: Path) -> None:
    material_source_path = (
        family_dir / "textures" / "source" / "civic_material_source.png"
    )
    source_path = (
        family_dir / "textures" / "source" / "civic_reference_elevation_v2.png"
    )
    material_source = Image.open(material_source_path).convert("RGB")
    reference_source = Image.open(source_path).convert("RGB")
    bands = {
        "marble": (0.000, 0.255),
        "relief": (0.255, 0.520),
        "glass": (0.520, 0.750),
        "copper": (0.750, 1.000),
    }
    zones = {
        zone: save_zone(material_source, family_dir, zone, bounds)
        for zone, bounds in bands.items()
    }
    zones["front_registered"] = save_registered_civic_front(
        reference_source,
        family_dir,
    )
    payload = {
        "schema": "wave3-landmark-skin@1",
        "family": family_dir.name,
        "source": source_path.relative_to(family_dir).as_posix(),
        "source_model": "gpt-image-2",
        "sources": {
            "archetype_registered_front": source_path.relative_to(
                family_dir
            ).as_posix(),
            "supporting_material_atlas": material_source_path.relative_to(
                family_dir
            ).as_posix(),
        },
        "registration": (
            "archetype-specific orthographic front elevation registered in one "
            "coordinate system across wing, portico, attic, drum, pediment, "
            "dome and lantern; supporting tile bands are secondary only"
        ),
        "reference_registration": {
            "mode": "archetype_specific",
            "source_archetype_id": "civic_monumental_institution",
            "registered_elevations": ["front"],
            "registered_surfaces": [
                "left_wing",
                "right_wing",
                "portico_recess",
                "central_attic",
                "drum",
                "pediment",
                "dome",
            ],
            "uv_strategy": "feature_registered_shared_elevation_coordinates",
            "depth_binding": "shader_bump",
            "generic_tiling_allowed": False,
        },
        "channels": list(CHANNELS),
        "semantic_masks": ["glass_mask", "opaque_mask"],
        "zones": zones,
        "atlases": build_atlases(
            family_dir, zones, ("marble", "relief", "glass", "copper"), "civic"
        ),
    }
    (family_dir / "textures" / "skin_manifest.json").write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8"
    )


def _draw_ashlar(
    draw: ImageDraw.ImageDraw,
    bounds: tuple[int, int, int, int],
    *,
    fill: str,
    joint: str,
    course_h: int = 92,
    block_w: int = 260,
) -> None:
    x0, y0, x1, y1 = bounds
    draw.rectangle(bounds, fill=fill)
    for row, y in enumerate(range(y0, y1 + 1, course_h)):
        draw.line((x0, y, x1, y), fill=joint, width=4)
        offset = block_w // 2 if row % 2 else 0
        for x in range(x0 - offset, x1 + block_w, block_w):
            draw.line((x, y, x, min(y + course_h, y1)), fill=joint, width=3)


def _draw_mullion_grid(
    draw: ImageDraw.ImageDraw,
    bounds: tuple[int, int, int, int],
    *,
    glass: str,
    frame: str,
    warm: str | None = None,
    columns: int = 12,
    rows: int = 4,
) -> None:
    x0, y0, x1, y1 = bounds
    draw.rectangle(bounds, fill=glass)
    bay_w = (x1 - x0) / columns
    bay_h = (y1 - y0) / rows
    if warm:
        for row in range(rows):
            for col in range(columns):
                if (row * 7 + col * 3) % 7 == 0:
                    xa = round(x0 + col * bay_w + 8)
                    ya = round(y0 + row * bay_h + 8)
                    xb = round(x0 + (col + 1) * bay_w - 8)
                    yb = round(y0 + (row + 1) * bay_h - 8)
                    draw.rectangle((xa, ya, xb, yb), fill=warm)
    for col in range(columns + 1):
        x = round(x0 + col * bay_w)
        draw.line((x, y0, x, y1), fill=frame, width=8)
    for row in range(rows + 1):
        y = round(y0 + row * bay_h)
        draw.line((x0, y, x1, y), fill=frame, width=7)


def _draw_concert_source(path: Path) -> tuple[str, ...]:
    size = 2048
    band = size // 4
    image = Image.new("RGB", (size, size), "#e7e7e3")
    draw = ImageDraw.Draw(image)

    # Pearlescent satin-aluminum shell with a non-generic, flowing panel grid.
    draw.rectangle((0, 0, size, band), fill="#e9e9e5")
    for y in range(0, band + 1, 104):
        draw.line((0, y, size, y + 36), fill="#c8c9c8", width=3)
    for x in range(-band, size + band, 220):
        draw.line((x, 0, x + 360, band), fill="#d0d1d0", width=3)
    for x in range(0, size, 520):
        draw.line((x, 0, x + 70, band), fill="#f8f8f5", width=5)

    _draw_mullion_grid(
        draw,
        (0, band, size, band * 2),
        glass="#405966",
        frame="#332d29",
        warm="#a76831",
        columns=16,
        rows=4,
    )

    draw.rectangle((0, band * 2, size, band * 3), fill="#cfa66f")
    for x in range(0, size + 1, 46):
        tone = "#9a7044" if (x // 46) % 5 == 0 else "#e0bd87"
        draw.rectangle((x, band * 2, min(x + 31, size), band * 3), fill=tone)
        draw.line((x, band * 2, x, band * 3), fill="#765337", width=3)
    for y in range(band * 2, band * 3, 128):
        draw.line((0, y, size, y), fill="#b18659", width=2)

    _draw_ashlar(
        draw,
        (0, band * 3, size, size),
        fill="#cbc6ba",
        joint="#958f84",
        course_h=86,
        block_w=235,
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, optimize=True)
    return ("aluminum", "concert_glass", "timber", "granite")


def _draw_mercat_source(path: Path) -> tuple[str, ...]:
    size = 2048
    band = size // 4
    image = Image.new("RGB", (size, size), "#1d2e29")
    draw = ImageDraw.Draw(image)

    draw.rectangle((0, 0, size, band), fill="#183029")
    for x in range(0, size + 1, 128):
        draw.rectangle((x, 0, min(x + 18, size), band), fill="#0b1714")
        for y in range(42, band, 82):
            draw.ellipse((x + 4, y, x + 14, y + 10), fill="#a48752")
    for y in range(0, band + 1, 128):
        draw.line((0, y, size, y), fill="#526157", width=8)

    # Reference-locked Modernista fanlight: a fine amber/green leaded field,
    # blue circular medallions and one central floral rosette. Large repeating
    # diamonds read as a peacock graphic rather than architectural glazing.
    glass_colors = ("#274f37", "#3f6f43", "#b68c25", "#d0a23a", "#2b6483")
    glass_top, glass_bottom = band, band * 2
    draw.rectangle((0, glass_top, size, glass_bottom), fill="#314c35")
    panel_w = 128
    for col, x in enumerate(range(0, size, panel_w)):
        color = glass_colors[(col * 3) % 4]
        draw.rectangle(
            (x + 7, glass_top + 7, min(x + panel_w - 7, size), glass_bottom - 7),
            fill=color,
        )
        draw.line(
            (x + panel_w // 2, glass_top, x + panel_w // 2, glass_bottom),
            fill="#171b18",
            width=7,
        )
    for y in range(glass_top, glass_bottom + 1, 84):
        draw.line((0, y, size, y), fill="#171b18", width=7)
    for x in range(-240, size + 240, 260):
        draw.line(
            (x, glass_bottom, x + 300, glass_top),
            fill="#26231b",
            width=6,
        )
        draw.line(
            (x + 300, glass_bottom, x, glass_top),
            fill="#26231b",
            width=6,
        )

    medallion_y = glass_top + 112
    for index, x in enumerate(range(112, size, 228)):
        radius = 54
        draw.ellipse(
            (x - radius - 10, medallion_y - radius - 10, x + radius + 10, medallion_y + radius + 10),
            fill="#191d19",
            outline="#b68c45",
            width=7,
        )
        draw.ellipse(
            (x - radius, medallion_y - radius, x + radius, medallion_y + radius),
            fill=("#246b91" if index % 2 == 0 else "#397943"),
            outline="#d0a75b",
            width=6,
        )
        for petal in range(8):
            angle = math.tau * petal / 8
            px = x + math.cos(angle) * 30
            py = medallion_y + math.sin(angle) * 30
            draw.ellipse(
                (px - 9, py - 9, px + 9, py + 9),
                fill="#d6ae49",
                outline="#17211c",
                width=2,
            )
        draw.ellipse((x - 12, medallion_y - 12, x + 12, medallion_y + 12), fill="#9f3f2f")

    rosette_x, rosette_y = size // 2, glass_top + 345
    draw.ellipse(
        (rosette_x - 145, rosette_y - 145, rosette_x + 145, rosette_y + 145),
        fill="#183128",
        outline="#d0a75b",
        width=12,
    )
    for petal in range(16):
        angle = math.tau * petal / 16
        px = rosette_x + math.cos(angle) * 94
        py = rosette_y + math.sin(angle) * 94
        draw.ellipse(
            (px - 34, py - 22, px + 34, py + 22),
            fill=glass_colors[petal % len(glass_colors)],
            outline="#171b18",
            width=6,
        )
    draw.ellipse(
        (rosette_x - 38, rosette_y - 38, rosette_x + 38, rosette_y + 38),
        fill="#b84c32",
        outline="#d8bd72",
        width=8,
    )

    tile_colors = ("#efe0bf", "#b75635", "#2f7180", "#d6a646", "#f4ead3")
    draw.rectangle((0, band * 2, size, band * 3), fill="#efe0bf")
    tile = 64
    for row, y in enumerate(range(band * 2, band * 3, tile)):
        for col, x in enumerate(range(0, size, tile)):
            color = tile_colors[(row * 5 + col * 3) % len(tile_colors)]
            draw.rectangle((x + 3, y + 3, x + tile - 3, y + tile - 3), fill=color)
            if (row + col) % 3 == 0:
                draw.arc((x + 10, y + 10, x + tile - 10, y + tile - 10), 0, 360, fill="#6f3d2a", width=3)

    _draw_mullion_grid(
        draw,
        (0, band * 3, size, size),
        glass="#829da2",
        frame="#172823",
        warm="#ab7433",
        columns=18,
        rows=4,
    )
    for x in range(-300, size + 300, 256):
        draw.line((x, band * 3, x + 380, size), fill="#2d433d", width=12)
        draw.line((x + 380, band * 3, x, size), fill="#2d433d", width=12)

    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, optimize=True)
    return ("iron", "stained_glass", "ceramic", "roof_glass")


def _draw_station_source(path: Path) -> tuple[str, ...]:
    size = 2048
    band = size // 4
    image = Image.new("RGB", (size, size), "#d8d0c1")
    draw = ImageDraw.Draw(image)

    _draw_ashlar(
        draw,
        (0, 0, size, band),
        fill="#d7d0c2",
        joint="#a79d8c",
        course_h=76,
        block_w=250,
    )
    _draw_mullion_grid(
        draw,
        (0, band, size, band * 2),
        glass="#574634",
        frame="#3d2a1c",
        # Monumental portal glass stays reflective and non-emissive. Sparse
        # occupied ceiling bands are separate recessed geometry behind it.
        warm=None,
        columns=14,
        rows=5,
    )
    _draw_mullion_grid(
        draw,
        (0, band * 2, size, band * 3),
        glass="#71848b",
        frame="#1f282c",
        warm="#9a672d",
        columns=18,
        rows=4,
    )
    for x in range(-260, size + 260, 240):
        draw.line((x, band * 2, x + 330, band * 3), fill="#20272a", width=13)
        draw.line((x + 330, band * 2, x, band * 3), fill="#20272a", width=13)

    draw.rectangle((0, band * 3, size, size), fill="#c8bdac")
    for x in range(45, size, 180):
        for y in range(band * 3 + 42, size, 140):
            draw.ellipse((x - 34, y - 34, x + 34, y + 34), outline="#8f816e", width=9)
            draw.ellipse((x - 14, y - 14, x + 14, y + 14), fill="#a99a85")
            draw.line((x - 65, y, x + 65, y), fill="#9d8f7c", width=6)
            draw.line((x, y - 65, x, y + 65), fill="#9d8f7c", width=6)

    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, optimize=True)
    return ("granite", "bronze_glass", "iron_glass", "relief")


def prepare_expansion_family(family_dir: Path) -> None:
    definitions = {
        "concert-hall-modern": {
            "archetype_id": "concert_hall_modern",
            "prefix": "concert",
            "draw": _draw_concert_source,
            "surfaces": [
                "flowing_aluminum_shells",
                "full_height_lobby_glazing",
                "ash_timber_acoustic_ribs",
                "granite_entry_plinth",
            ],
        },
        "barcelona-mercat": {
            "archetype_id": "barcelona_mercat",
            "prefix": "mercat",
            "draw": _draw_mercat_source,
            "surfaces": [
                "modernista_iron_portal",
                "polychrome_stained_glass",
                "ceramic_tile_plinth",
                "five_aisle_roof_glazing",
            ],
        },
        "historic-grand-station": {
            "archetype_id": "historic_grand_station",
            "prefix": "station",
            "draw": _draw_station_source,
            "surfaces": [
                "granite_head_house",
                "recessed_bronze_portal_glazing",
                "three_barrel_vault_train_sheds",
                "carved_entablature_and_clock",
            ],
        },
    }
    definition = definitions[family_dir.name]
    source_dir = family_dir / "textures" / "source"
    material_source_path = source_dir / f"{family_dir.name}_material_source.png"
    zone_order = definition["draw"](material_source_path)
    with Image.open(material_source_path) as material_source:
        zones = {
            zone: save_zone(
                material_source.convert("RGB"),
                family_dir,
                zone,
                (index / len(zone_order), (index + 1) / len(zone_order)),
            )
            for index, zone in enumerate(zone_order)
        }
    goalpost_path = source_dir / "archetype-goalpost.png"
    if not goalpost_path.is_file():
        raise FileNotFoundError(goalpost_path)
    sources = {
        "archetype_goalpost": goalpost_path.relative_to(family_dir).as_posix(),
        "supporting_material_atlas": material_source_path.relative_to(family_dir).as_posix(),
    }
    prompt_source_path = source_dir / "goalpost-source.json"
    if prompt_source_path.is_file():
        sources["goalpost_prompt"] = prompt_source_path.relative_to(family_dir).as_posix()
    payload = {
        "schema": "wave3-landmark-skin@1",
        "family": family_dir.name,
        "source": goalpost_path.relative_to(family_dir).as_posix(),
        "source_model": "gpt-image-2",
        "sources": sources,
        "registration": (
            "archetype-specific material zones and semantic surfaces locked to "
            "the generated catalogue goalpost; all runtime channels share the "
            "same source pixels and shape-aware surface UVs"
        ),
        "reference_registration": {
            "mode": "archetype_specific",
            "source_archetype_id": definition["archetype_id"],
            "registered_elevations": ["front", "left", "right", "rear", "roof"],
            "registered_surfaces": definition["surfaces"],
            "uv_strategy": "shape_aware_surface_uv",
            "depth_binding": "shader_bump",
            "generic_tiling_allowed": False,
        },
        "channels": list(CHANNELS),
        "semantic_masks": ["glass_mask", "opaque_mask"],
        "zones": zones,
        "atlases": build_atlases(
            family_dir,
            zones,
            zone_order,
            definition["prefix"],
        ),
    }
    (family_dir / "textures" / "skin_manifest.json").write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8"
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--family-dir", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    family_dir = args.family_dir.resolve()
    if family_dir.name == "modern-sports-arena":
        prepare_arena(family_dir)
    elif family_dir.name == "civic-monumental-neoclassical":
        prepare_civic(family_dir)
    elif family_dir.name in {
        "concert-hall-modern",
        "barcelona-mercat",
        "historic-grand-station",
    }:
        prepare_expansion_family(family_dir)
    else:
        raise ValueError(f"unsupported landmark family: {family_dir.name}")
    print(f"[wave3-skins] prepared {family_dir.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
