"""Build registered PBR texture sets for the Wave 3 landmark families.

The ImageGen source is deliberately retained as the render-locked design
source.  Every runtime channel is then derived from the same registered pixels
so albedo, relief, emissive light, and semantic masks cannot drift.
"""
from __future__ import annotations

import argparse
import json
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
    if zone in {"glass", "accent"}:
        scale = np.clip((rgb[:, :, 0] - 90) / 120, 0, 1)[:, :, None]
        emissive = np.uint8(np.where(warm[:, :, None], rgb * scale, 0))

    glass_value = 255 if zone == "glass" else 0
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
    else:
        raise ValueError(f"unsupported landmark family: {family_dir.name}")
    print(f"[wave3-skins] prepared {family_dir.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
