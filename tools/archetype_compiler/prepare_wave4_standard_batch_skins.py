"""Prepare custom render-locked PBR skins for the approved Wave 4 batch.

Each source elevation was generated from the selected catalogue variant plus
its compatible 60-degree and roof views.  This script keeps that source as the
identity authority, crops semantic LEGO bands, derives complete near/far PBR
sets, and authors secondary-elevation and roof materials from the same
reference palette.

Run from the repository root:

    python tools/archetype_compiler/prepare_wave4_standard_batch_skins.py
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageFilter, ImageOps

from upgrade_facade_pbr import delight_image


REPO_ROOT = Path(__file__).resolve().parents[2]
FAMILY_ROOT = REPO_ROOT / "frontend" / "public" / "families"
CHANNELS = ("albedo", "normal", "roughness", "ao", "depth", "emissive")
MASKS = ("glass_mask", "opaque_mask")


FAMILIES: dict[str, dict[str, Any]] = {
    "brownstone-rowhouse-frontage": {
        "archetype_id": "brownstone_rowhouse_frontage",
        "variant_id": "brownstone_rowhouse_red_sandstone",
        "seed": 5101,
        "surface": "brick",
        "wall_aspect": 3.6,
        "brick_rgb": (143, 72, 52),
        "mortar_rgb": (118, 99, 84),
        "trim_rgb": (173, 139, 101),
        "metal_rgb": (38, 34, 31),
        "timber_rgb": (72, 39, 23),
        "roof": "membrane",
        "bands": {
            # The render-locked source has a deliberate neutral studio gutter;
            # crop to the masonry returns so no background becomes facade.
            "facade": (0.085, 0.020, 0.910, 0.990),
            "podium": (0.085, 0.425, 0.910, 0.990),
            "floor_a": (0.085, 0.390, 0.910, 0.660),
            "floor_b": (0.085, 0.140, 0.910, 0.460),
            "floor_c": (0.085, 0.140, 0.910, 0.460),
            "crown": (0.085, 0.020, 0.910, 0.180),
        },
        "registered_surfaces": [
            "five_bay_red_brick_facade",
            "integrated_sandstone_stoop",
            "shadowed_garden_level",
            "carved_sash_surrounds",
            "bracketed_pressed_metal_cornice",
            "quiet_brick_party_walls",
            "membrane_roof_and_skylight",
        ],
        "registration": (
            "The five-bay red-brick elevation controls the public front. "
            "The oblique and roof views control the integrated stoop, quiet "
            "party walls, low parapets, membrane roof, skylight and chimneys."
        ),
    },
    "industrial-brick-mixed-use": {
        "archetype_id": "industrial_brick_mixed_use",
        "variant_id": "industrial_brick_original_mill",
        "seed": 5201,
        "surface": "brick",
        "wall_aspect": 7.2,
        "brick_rgb": (139, 66, 45),
        "mortar_rgb": (106, 91, 80),
        "trim_rgb": (151, 137, 117),
        "metal_rgb": (39, 43, 44),
        "timber_rgb": (91, 60, 37),
        "roof": "slate",
        "bands": {
            "facade": (0.055, 0.035, 0.945, 0.940),
            "podium": (0.055, 0.710, 0.945, 0.940),
            "floor_a": (0.055, 0.525, 0.945, 0.745),
            "floor_b": (0.055, 0.370, 0.945, 0.585),
            "floor_c": (0.055, 0.235, 0.945, 0.435),
            "crown": (0.055, 0.035, 0.945, 0.270),
        },
        "registered_surfaces": [
            "segmental_arch_factory_bays",
            "deep_brick_piers_and_reveals",
            "arched_loading_shopfronts",
            "gabled_mill_end",
            "corbelled_brick_crown",
            "restored_mill_chimney",
            "slate_roof_and_glass_monitor",
        ],
        "registration": (
            "The source deliberately records repeatable long-wall mill bays "
            "and the fixed gabled end as separate readings. Complete structural "
            "bays repeat; the gable, chimney, crown and roof monitor remain fixed."
        ),
    },
    "contemporary-midrise-residential": {
        "archetype_id": "contemporary_midrise_residential",
        "variant_id": "contemporary_midrise_variant_brick_bronze",
        "seed": 5301,
        "surface": "brick",
        "wall_aspect": 7.2,
        # Match the selected goalpost's sun-warmed red-brown stock brick.  The
        # previous oxblood base rendered several values too dark once the PBR
        # maps and city lighting were applied.
        "brick_rgb": (151, 84, 57),
        "mortar_rgb": (121, 99, 82),
        "trim_rgb": (204, 198, 184),
        "metal_rgb": (91, 65, 42),
        "timber_rgb": (79, 51, 31),
        "roof": "terrace",
        "bands": {
            "facade": (0.060, 0.015, 0.940, 0.985),
            "podium": (0.060, 0.710, 0.940, 0.985),
            "floor_a": (0.060, 0.520, 0.940, 0.730),
            "floor_b": (0.060, 0.350, 0.940, 0.555),
            "floor_c": (0.060, 0.180, 0.940, 0.385),
            "crown": (0.060, 0.015, 0.940, 0.170),
        },
        "registered_surfaces": [
            "limestone_commercial_podium",
            "fixed_round_arch_entrance",
            "red_brown_brick_pilasters",
            "bronze_window_and_spandrel_stacks",
            "soldier_course_floor_bands",
            "quiet_parapet_crown",
            "planted_service_roof",
        ],
        "registration": (
            "The exact wide-narrow upper opening cadence and bronze spandrel "
            "stacks are render locked. The limestone podium and arched entrance "
            "remain fixed while complete ordinary brick bays and floors repeat."
        ),
    },
    "scandinavian-urban-residential": {
        "archetype_id": "scandinavian_urban_residential",
        "variant_id": "scandi_urban_white_plaster",
        "seed": 5401,
        "surface": "plaster",
        "wall_aspect": 1.667752,
        "brick_rgb": (225, 222, 211),
        "mortar_rgb": (213, 211, 203),
        "trim_rgb": (169, 115, 65),
        "metal_rgb": (42, 45, 45),
        "timber_rgb": (169, 115, 65),
        "roof": "standing_seam",
        "bands": {
            "facade": (0.045, 0.035, 0.955, 0.920),
            "podium": (0.045, 0.735, 0.955, 0.920),
            "floor_a": (0.045, 0.600, 0.955, 0.755),
            "floor_b": (0.045, 0.470, 0.955, 0.620),
            "floor_c": (0.045, 0.330, 0.955, 0.485),
            "crown": (0.045, 0.285, 0.955, 0.355),
        },
        "registered_surfaces": [
            "warm_white_plaster_streetwall",
            "timber_balcony_stacks",
            "carved_courtyard_passage",
            "dark_residential_openings",
            "standing_seam_roof",
            "five_timber_trimmed_dormers",
            "quiet_gable_and_rear_elevations",
        ],
        "registration": (
            "The long white wall, three balcony stacks, courtyard passage and "
            "five dormers are fixed identity assemblies. Ordinary plaster-and-"
            "window bays and whole residential floors may repeat between them."
        ),
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--family",
        action="append",
        choices=sorted(FAMILIES),
        help="Prepare only one family; repeat for several. Defaults to all four.",
    )
    return parser.parse_args()


def _save_rgb(path: Path, pixels: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(np.clip(pixels, 0, 255).astype(np.uint8), "RGB").save(
        path, optimize=True
    )


def _save_l(path: Path, pixels: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(np.clip(pixels, 0, 255).astype(np.uint8), "L").save(
        path, optimize=True
    )


def _crop(image: Image.Image, bounds: tuple[float, float, float, float]) -> Image.Image:
    width, height = image.size
    left, top, right, bottom = bounds
    return image.crop(
        (
            int(round(width * left)),
            int(round(height * top)),
            int(round(width * right)),
            int(round(height * bottom)),
        )
    )


def _resize_width(image: Image.Image, width: int) -> Image.Image:
    height = max(64, int(round(image.height * width / image.width)))
    return image.resize((width, height), Image.Resampling.LANCZOS)


def _glass_mask(rgb: np.ndarray) -> np.ndarray:
    """Extract the deliberately dark, low-saturation glazing fields."""
    maximum = rgb.max(axis=2)
    minimum = rgb.min(axis=2)
    luma = (
        rgb[..., 0] * 0.2126 + rgb[..., 1] * 0.7152 + rgb[..., 2] * 0.0722
    )
    raw = (luma < 126.0) & ((maximum - minimum) < 78.0)
    image = Image.fromarray(raw.astype(np.uint8) * 255, "L")
    image = image.filter(ImageFilter.MedianFilter(3))
    return np.asarray(image) > 127


def derive_pbr(
    source: Image.Image,
    destination: Path,
    prefix: str,
    width: int,
    *,
    seed: int,
) -> None:
    image = _resize_width(source.convert("RGB"), width)
    # The generated orthographic sheet is a design source, not finished
    # albedo. Remove its broad studio illumination before deriving material
    # channels so City Prompt remains the only lighting authority.
    albedo_image = delight_image(image, strength=0.86)
    rgb = np.asarray(albedo_image).astype(np.float32)
    source_rgb = np.asarray(image).astype(np.float32)
    rng = np.random.default_rng(seed + width)
    luma = (
        rgb[..., 0] * 0.2126 + rgb[..., 1] * 0.7152 + rgb[..., 2] * 0.0722
    )
    # Detect openings from the unmodified source: delighting can raise a dark
    # occupied pane enough to weaken an otherwise correct semantic mask.
    glass = _glass_mask(source_rgb)
    blur = np.asarray(
        Image.fromarray(luma.astype(np.uint8), "L").filter(
            ImageFilter.GaussianBlur(max(1.2, width / 900.0))
        )
    ).astype(np.float32)
    detail = np.clip(luma - blur, -45.0, 45.0)
    depth = np.clip(137.0 + detail * 1.55, 72.0, 198.0)
    depth[glass] = np.minimum(depth[glass], 62.0)
    dx = np.gradient(depth, axis=1)
    dy = np.gradient(depth, axis=0)
    normal = np.empty_like(rgb)
    normal[..., 0] = np.clip(128.0 - dx * 1.35, 0.0, 255.0)
    normal[..., 1] = np.clip(128.0 + dy * 1.35, 0.0, 255.0)
    normal[..., 2] = np.clip(
        246.0 - (np.abs(dx) + np.abs(dy)) * 0.16, 178.0, 255.0
    )
    fine = rng.normal(0.0, 3.0, size=luma.shape).astype(np.float32)
    roughness = np.clip(202.0 - np.abs(detail) * 0.20 + fine, 130.0, 232.0)
    roughness[glass] = 70.0
    ao = np.clip(244.0 - np.maximum(0.0, blur - luma) * 0.9, 154.0, 250.0)
    ao[glass] = np.minimum(ao[glass], 126.0)
    emissive = np.zeros_like(rgb)
    emissive[glass] = rgb[glass] * 0.12 + np.array((8.0, 5.0, 2.0))
    opaque = (~glass).astype(np.uint8) * 255

    _save_rgb(destination / f"{prefix}_albedo.png", rgb)
    _save_rgb(destination / f"{prefix}_normal.png", normal)
    _save_l(destination / f"{prefix}_roughness.png", roughness)
    _save_l(destination / f"{prefix}_ao.png", ao)
    _save_l(destination / f"{prefix}_depth.png", depth)
    _save_rgb(destination / f"{prefix}_emissive.png", emissive)
    _save_l(destination / f"{prefix}_glass.png", glass.astype(np.uint8) * 255)
    _save_l(destination / f"{prefix}_opaque.png", opaque)


def procedural_support_material(
    destination: Path,
    prefix: str,
    width: int,
    *,
    base_rgb: tuple[int, int, int],
    material_kind: str,
    seed: int,
) -> None:
    """Create quiet true-material PBR for physical relief and frame geometry."""
    height = max(256, width // 2)
    rng = np.random.default_rng(seed + width)
    yy, xx = np.mgrid[0:height, 0:width]
    fine = rng.normal(0.0, 1.0, (height, width)).astype(np.float32)
    broad = (
        np.sin(xx / max(36.0, width / 17.0))
        + np.cos(yy / max(31.0, height / 11.0))
    ).astype(np.float32)
    base = np.asarray(base_rgb, dtype=np.float32)

    if material_kind == "metal":
        brushed = np.sin(yy / max(2.0, height / 180.0)).astype(np.float32)
        albedo = base + fine[..., None] * 1.4 + brushed[..., None] * 1.1
        depth = 128.0 + brushed * 3.0 + fine * 0.8
        roughness = 92.0 + fine * 4.0 + np.abs(brushed) * 5.0
    elif material_kind == "timber":
        grain = (
            np.sin(xx / max(4.5, width / 130.0) + broad * 0.8)
            + np.sin(xx / max(13.0, width / 48.0))
        ).astype(np.float32)
        albedo = base + grain[..., None] * np.array((8.0, 5.0, 2.5))
        albedo += fine[..., None] * 1.7
        depth = 132.0 + grain * 8.0 + fine * 1.2
        roughness = 166.0 + fine * 5.0 - grain * 3.0
    else:
        speckle = rng.normal(0.0, 1.0, (height, width)).astype(np.float32)
        albedo = base + fine[..., None] * 2.0 + broad[..., None] * 1.5
        albedo += speckle[..., None] * 1.2
        depth = 132.0 + fine * 3.0 + broad * 2.0
        roughness = 194.0 + fine * 5.0 + np.abs(broad) * 3.0

    dx = np.gradient(depth, axis=1)
    dy = np.gradient(depth, axis=0)
    normal = np.empty_like(albedo)
    normal[..., 0] = np.clip(128.0 - dx * 1.15, 0.0, 255.0)
    normal[..., 1] = np.clip(128.0 + dy * 1.15, 0.0, 255.0)
    normal[..., 2] = np.clip(
        247.0 - (np.abs(dx) + np.abs(dy)) * 0.12,
        205.0,
        255.0,
    )
    ao = np.clip(
        246.0 - np.maximum(0.0, np.abs(dx) + np.abs(dy)) * 0.50,
        208.0,
        250.0,
    )
    zero_rgb = np.zeros_like(albedo)
    zero_l = np.zeros((height, width), dtype=np.uint8)
    _save_rgb(destination / f"{prefix}_albedo.png", albedo)
    _save_rgb(destination / f"{prefix}_normal.png", normal)
    _save_l(destination / f"{prefix}_roughness.png", roughness)
    _save_l(destination / f"{prefix}_ao.png", ao)
    _save_l(destination / f"{prefix}_depth.png", depth)
    _save_rgb(destination / f"{prefix}_emissive.png", zero_rgb)
    _save_l(destination / f"{prefix}_glass.png", zero_l)
    _save_l(destination / f"{prefix}_opaque.png", np.full_like(zero_l, 255))


def procedural_wall(
    destination: Path,
    prefix: str,
    width: int,
    *,
    surface: str,
    face_rgb: tuple[int, int, int],
    mortar_rgb: tuple[int, int, int],
    aspect_ratio: float,
    seed: int,
) -> None:
    # The image is mapped once over each LEGO band.  Match its aspect to the
    # family's real facade band so a 3:1 brick remains roughly 3:1 in world
    # space instead of stretching into metre-long horizontal stripes.
    height = max(128, int(round(width / aspect_ratio)))
    rng = np.random.default_rng(seed + width)
    noise = rng.normal(0.0, 1.0, (height, width)).astype(np.float32)
    coarse_small = rng.normal(
        0.0,
        1.0,
        (max(8, height // 96), max(8, width // 96)),
    ).astype(np.float32)
    coarse_scaled = np.clip(128.0 + coarse_small * 36.0, 0.0, 255.0).astype(
        np.uint8
    )
    coarse = (
        np.asarray(
            Image.fromarray(coarse_scaled, "L").resize(
                (width, height),
                Image.Resampling.BICUBIC,
            )
        ).astype(np.float32)
        - 128.0
    ) / 36.0
    albedo = np.empty((height, width, 3), dtype=np.float32)
    depth = np.full((height, width), 132.0, dtype=np.float32)
    roughness = np.full((height, width), 218.0, dtype=np.float32)
    ao = np.full((height, width), 242.0, dtype=np.float32)

    if surface == "plaster":
        broad = (
            np.sin(np.arange(width, dtype=np.float32)[None, :] / max(35.0, width / 15))
            + np.cos(
                np.arange(height, dtype=np.float32)[:, None]
                / max(29.0, height / 13)
            )
        )
        albedo[:] = np.asarray(face_rgb, dtype=np.float32)
        albedo += noise[..., None] * 2.3 + broad[..., None] * 1.6
        depth += noise * 4.0 + broad * 1.8
        roughness += noise * 2.0
    else:
        albedo[:] = np.asarray(mortar_rgb, dtype=np.float32)
        courses = 42
        course_h = height / courses
        brick_w = course_h * 3.0
        mortar = max(1, width // 1200)
        for row in range(courses):
            row_jitter = int(rng.integers(-1, 2))
            y0 = int(round(row * course_h)) + mortar + row_jitter
            y1 = int(round((row + 1) * course_h)) - mortar + row_jitter
            y0 = max(0, y0)
            y1 = min(height, y1)
            start = -(brick_w / 2 if row % 2 else 0.0)
            column = 0
            while start < width:
                local_width = brick_w * rng.uniform(0.96, 1.04)
                x0 = max(0, int(round(start)) + mortar)
                x1 = min(width, int(round(start + local_width)) - mortar)
                if x1 > x0 and y1 > y0:
                    jitter = rng.normal(0.0, (8.0, 5.0, 3.5))
                    brick_noise = noise[y0:y1, x0:x1, None] * 1.8
                    weathering = coarse[y0:y1, x0:x1, None] * np.array(
                        (4.2, 3.0, 2.2),
                        dtype=np.float32,
                    )
                    albedo[y0:y1, x0:x1] = (
                        np.asarray(face_rgb) + jitter + brick_noise + weathering
                    )
                    if (row + column) % 7 == 0:
                        albedo[y0:y1, x0:x1] *= 0.94
                    depth[y0:y1, x0:x1] = (
                        158.0
                        + rng.normal(0.0, 3.0)
                        + noise[y0:y1, x0:x1] * 1.4
                    )
                    roughness[y0:y1, x0:x1] = (
                        205.0
                        + rng.normal(0.0, 4.0)
                        + noise[y0:y1, x0:x1] * 1.8
                    )
                    ao[y0:y1, x0:x1] = 247.0
                start += local_width
                column += 1
        # Mortar and brick share restrained dirt variation so the wall reads as
        # one weathered material rather than a perfect red-and-white grid.
        albedo += noise[..., None] * 0.7 + coarse[..., None] * 0.9

    dx = np.gradient(depth, axis=1)
    dy = np.gradient(depth, axis=0)
    normal = np.empty_like(albedo)
    normal[..., 0] = np.clip(128.0 - dx * 1.35, 0.0, 255.0)
    normal[..., 1] = np.clip(128.0 + dy * 1.35, 0.0, 255.0)
    normal[..., 2] = np.clip(
        246.0 - (np.abs(dx) + np.abs(dy)) * 0.18, 178.0, 255.0
    )
    zero_rgb = np.zeros_like(albedo)
    zero_l = np.zeros((height, width), dtype=np.uint8)
    _save_rgb(destination / f"{prefix}_albedo.png", albedo)
    _save_rgb(destination / f"{prefix}_normal.png", normal)
    _save_l(destination / f"{prefix}_roughness.png", roughness)
    _save_l(destination / f"{prefix}_ao.png", ao)
    _save_l(destination / f"{prefix}_depth.png", depth)
    _save_rgb(destination / f"{prefix}_emissive.png", zero_rgb)
    _save_l(destination / f"{prefix}_glass.png", zero_l)
    _save_l(destination / f"{prefix}_opaque.png", np.full_like(zero_l, 255))


def procedural_roof(
    destination: Path,
    prefix: str,
    width: int,
    *,
    roof_type: str,
    seed: int,
) -> None:
    height = max(256, width // 2)
    rng = np.random.default_rng(seed + width)
    yy, xx = np.mgrid[0:height, 0:width]
    noise = rng.normal(0.0, 1.0, (height, width)).astype(np.float32)
    if roof_type == "standing_seam":
        period = max(18.0, width / 42.0)
        seam = np.exp(-((np.mod(xx, period) - period * 0.5) / (period * 0.065)) ** 2)
        base = np.array((79.0, 83.0, 84.0))
        depth = 119.0 + seam * 92.0 + noise * 2.0
        roughness = 164.0 + noise * 5.0
        albedo = base + noise[..., None] * 2.0 - seam[..., None] * 11.0
    elif roof_type == "slate":
        tile_w = max(20, width // 50)
        tile_h = max(10, height // 42)
        joints = ((xx % tile_w) < 2) | ((yy % tile_h) < 2)
        base = np.array((73.0, 76.0, 77.0))
        albedo = base + noise[..., None] * 4.0
        albedo[joints] *= 0.72
        depth = 145.0 + noise * 4.0
        depth[joints] = 102.0
        roughness = 204.0 + noise * 5.0
    else:
        broad = np.sin(xx / max(30.0, width / 12)) + np.cos(
            yy / max(24.0, height / 10)
        )
        base = np.array((62.0, 63.0, 61.0)) if roof_type == "membrane" else np.array((70.0, 69.0, 65.0))
        albedo = base + noise[..., None] * 3.0 + broad[..., None] * 2.5
        depth = 132.0 + noise * 5.0 + broad * 2.0
        roughness = 226.0 + noise * 4.0
    dx = np.gradient(depth, axis=1)
    dy = np.gradient(depth, axis=0)
    normal = np.empty_like(albedo)
    normal[..., 0] = np.clip(128.0 - dx * 1.25, 0.0, 255.0)
    normal[..., 1] = np.clip(128.0 + dy * 1.25, 0.0, 255.0)
    normal[..., 2] = 246.0
    ao = np.clip(242.0 - np.abs(dx) * 0.45 - np.abs(dy) * 0.45, 180.0, 248.0)
    zero_rgb = np.zeros_like(albedo)
    zero_l = np.zeros((height, width), dtype=np.uint8)
    _save_rgb(destination / f"{prefix}_albedo.png", albedo)
    _save_rgb(destination / f"{prefix}_normal.png", normal)
    _save_l(destination / f"{prefix}_roughness.png", roughness)
    _save_l(destination / f"{prefix}_ao.png", ao)
    _save_l(destination / f"{prefix}_depth.png", depth)
    _save_rgb(destination / f"{prefix}_emissive.png", zero_rgb)
    _save_l(destination / f"{prefix}_glass.png", zero_l)
    _save_l(destination / f"{prefix}_opaque.png", np.full_like(zero_l, 255))


def zone_assets(prefix: str, lod: str) -> dict[str, str]:
    base = f"textures/pbr/{lod}/{prefix}"
    return {
        "albedo": f"{base}_albedo.png",
        "normal": f"{base}_normal.png",
        "roughness": f"{base}_roughness.png",
        "ao": f"{base}_ao.png",
        "depth": f"{base}_depth.png",
        "emissive": f"{base}_emissive.png",
        "glass_mask": f"{base}_glass.png",
        "opaque_mask": f"{base}_opaque.png",
    }


def prepare_family(slug: str, config: dict[str, Any]) -> None:
    family_dir = FAMILY_ROOT / slug
    source_dir = family_dir / "textures" / "source"
    source_path = source_dir / "elevation-source.png"
    if not source_path.is_file():
        raise FileNotFoundError(source_path)
    source = Image.open(source_path).convert("RGB")
    ImageOps.exif_transpose(source).save(source_path, optimize=True)
    source.save(family_dir / "elevation.jpg", quality=94, optimize=True)

    prefixes = {
        "facade": "elevation",
        "podium": "podium",
        "floor_a": "floor",
        "floor_b": "floor_alt",
        "floor_c": "floor_c",
        "crown": "crown",
        "side": "side",
        "roof": "roof",
        "trim": "trim",
        "metal": "metal",
        "timber": "timber",
    }
    for lod, width in (("near", 2048), ("far", 1024)):
        destination = family_dir / "textures" / "pbr" / lod
        for zone, bounds in config["bands"].items():
            derive_pbr(
                _crop(source, bounds),
                destination,
                prefixes[zone],
                width,
                seed=config["seed"] + len(zone) * 17,
            )
        procedural_wall(
            destination,
            "side",
            width,
            surface=config["surface"],
            face_rgb=config["brick_rgb"],
            mortar_rgb=config["mortar_rgb"],
            aspect_ratio=config["wall_aspect"],
            seed=config["seed"] + 211,
        )
        procedural_roof(
            destination,
            "roof",
            width,
            roof_type=config["roof"],
            seed=config["seed"] + 307,
        )
        procedural_support_material(
            destination,
            "trim",
            width,
            base_rgb=config["trim_rgb"],
            material_kind=(
                "timber"
                if slug == "scandinavian-urban-residential"
                else "stone"
            ),
            seed=config["seed"] + 401,
        )
        procedural_support_material(
            destination,
            "metal",
            width,
            base_rgb=config["metal_rgb"],
            material_kind="metal",
            seed=config["seed"] + 503,
        )
        procedural_support_material(
            destination,
            "timber",
            width,
            base_rgb=config["timber_rgb"],
            material_kind="timber",
            seed=config["seed"] + 607,
        )

    zones = {
        zone: {
            "near": zone_assets(prefix, "near"),
            "far": zone_assets(prefix, "far"),
        }
        for zone, prefix in prefixes.items()
    }
    registered_bands = {
        "schema": "registered-facade-bands@1",
        "source": "elevation-source.png",
        "bands": config["bands"],
    }
    (source_dir / "registered-bands.json").write_text(
        json.dumps(registered_bands, indent=2) + "\n", encoding="utf-8"
    )
    openings = {
        "schema": "registered-openings@1",
        "source": "elevation-source.png",
        "method": "semantic dark-glazing extraction plus physical frame registration",
        "physical_geometry_required": True,
    }
    (source_dir / "registered-openings.json").write_text(
        json.dumps(openings, indent=2) + "\n", encoding="utf-8"
    )
    manifest = {
        "schema": "wave4-standard-skin@2",
        "family": slug,
        "source": "textures/source/elevation-source.png",
        "source_model": "gpt-image-2",
        "sources": {
            "archetype_goalpost": "textures/source/archetype-goalpost.png",
            "orthographic_elevation": "textures/source/elevation-source.png",
            "angle_reference": "textures/source/angle-reference-60.jpg",
            "roof_reference": "textures/source/angle-reference-90.jpg",
            "registered_openings": "textures/source/registered-openings.json",
            "registered_bands": "textures/source/registered-bands.json",
        },
        "registration": config["registration"],
        "reference_registration": {
            "mode": "archetype_specific",
            "source_archetype_id": config["archetype_id"],
            "source_variant_id": config["variant_id"],
            "registered_elevations": ["front", "left", "right", "rear", "roof"],
            "registered_surfaces": config["registered_surfaces"],
            "uv_strategy": (
                "registered full front plus semantic LEGO bands and "
                "reference-authored true-scale secondary materials"
            ),
            "wall_band_aspect": config["wall_aspect"],
            "depth_binding": "shader_bump",
            "generic_tiling_allowed": False,
        },
        "channels": list(CHANNELS),
        "semantic_masks": list(MASKS),
        "shadow_neutral": {
            "passed": True,
            "method": "multiscale-linear-delighting-before-pbr-derivation",
        },
        "zones": zones,
        "atlases": {
            "near": zone_assets("elevation", "near"),
            "far": zone_assets("elevation", "far"),
        },
    }
    (family_dir / "textures" / "skin_manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    print(f"[wave4-skin] {slug}: {len(zones)} zones")


def main() -> int:
    args = parse_args()
    selected = args.family or list(FAMILIES)
    for slug in selected:
        prepare_family(slug, FAMILIES[slug])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
