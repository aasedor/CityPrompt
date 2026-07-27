#!/usr/bin/env python3
"""Upgrade one rectified facade sheet into a shadow-neutral PBR/LOD package.

The image model remains responsible for architectural identity.  This pass is
deliberately deterministic: it de-lights the elevation, derives registered PBR
maps, creates semantic glass masks and produces several interchangeable middle
bay strips without changing the fixed end bays.
"""

from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageOps

from generate_facade_sheets import (
    derive_glass_mask_fallback,
    extract_glass_regions,
    normalize_semantic_glass_mask,
)


PBR_KEYS = ("albedo", "normal", "roughness", "ao", "depth", "emissive")

# Normalized crops from the rectified Parisian elevation.  The cached v8
# bands straddled storey boundaries (and the old crown contained three floors),
# which compressed multiple windows into one LEGO level.  These ranges isolate
# one construction storey per repeatable module.
PARISIAN_BAND_CROPS = {
    "crown": (0.200, 0.400),
    "floor": (0.400, 0.600),
    "floor_alt": (0.600, 0.800),
    "podium": (0.800, 1.000),
}
PARISIAN_GLASS_REGIONS = {
    "crown": [
        [0.112, 0.27, 0.205, 0.82], [0.362, 0.27, 0.455, 0.82],
        [0.612, 0.27, 0.705, 0.82], [0.862, 0.27, 0.955, 0.82],
    ],
    "floor": [
        [0.112, 0.22, 0.205, 0.79], [0.362, 0.22, 0.455, 0.79],
        [0.612, 0.22, 0.705, 0.79], [0.862, 0.22, 0.955, 0.79],
    ],
    "floor_alt": [
        [0.112, 0.16, 0.205, 0.71], [0.362, 0.16, 0.455, 0.71],
        [0.612, 0.16, 0.705, 0.71], [0.862, 0.16, 0.955, 0.71],
    ],
    "podium": [
        [0.018, 0.28, 0.365, 0.91], [0.655, 0.28, 0.982, 0.91],
    ],
}

# The Chateauesque source is a high-quality full elevation, but its legacy v8
# manifest sliced several photographed storeys into each 3.6 m LEGO level.  It
# also treated most of the podium and crown as glass.  These audited cuts follow
# actual construction datums in the 1536 x 2752 source: one upper-wall storey,
# two interchangeable middle storeys, and one complete monumental ground floor.
CHATEAUESQUE_BAND_CROPS = {
    "crown": (397 / 2752, 654 / 2752),
    "floor": (842 / 2752, 1123 / 2752),
    "floor_alt": (1382 / 2752, 1626 / 2752),
    "podium": (2194 / 2752, 1.0),
}
CHATEAUESQUE_GLASS_REGIONS = {
    "crown": [
        [0.076, 0.25, 0.205, 0.75], [0.326, 0.25, 0.455, 0.75],
        [0.576, 0.25, 0.705, 0.75], [0.826, 0.25, 0.955, 0.75],
    ],
    "floor": [
        [0.076, 0.22, 0.205, 0.82], [0.326, 0.22, 0.455, 0.82],
        [0.576, 0.22, 0.705, 0.82], [0.826, 0.22, 0.955, 0.82],
    ],
    "floor_alt": [
        [0.076, 0.24, 0.205, 0.91], [0.326, 0.24, 0.455, 0.91],
        [0.576, 0.24, 0.705, 0.91], [0.826, 0.24, 0.955, 0.91],
    ],
    "podium": [
        [0.072, 0.14, 0.205, 0.70], [0.282, 0.14, 0.415, 0.70],
        [0.438, 0.16, 0.562, 0.72],
        [0.585, 0.14, 0.718, 0.70], [0.795, 0.14, 0.928, 0.70],
    ],
}
CHATEAUESQUE_PODIUM_OUTER_SLICES = ((0.0, 0.42), (0.58, 1.0))
CHATEAUESQUE_PODIUM_REPEAT_GLASS_REGIONS = [
    [0.086, 0.14, 0.244, 0.70], [0.336, 0.14, 0.494, 0.70],
    [0.506, 0.14, 0.664, 0.70], [0.756, 0.14, 0.914, 0.70],
]
CHATEAUESQUE_ENTRANCE_X_BOUNDS = (0.36, 0.64)

AUDITED_BAND_LAYOUTS = {
    "parisian_midrise_block": {
        "crops": PARISIAN_BAND_CROPS,
        "glass_regions": PARISIAN_GLASS_REGIONS,
    },
    "chateauesque_grand_railway_hotel": {
        "crops": CHATEAUESQUE_BAND_CROPS,
        "glass_regions": CHATEAUESQUE_GLASS_REGIONS,
    },
}


def _srgb_to_linear(array: np.ndarray) -> np.ndarray:
    return np.where(array <= 0.04045, array / 12.92, ((array + 0.055) / 1.055) ** 2.4)


def _linear_to_srgb(array: np.ndarray) -> np.ndarray:
    return np.where(array <= 0.0031308, array * 12.92, 1.055 * np.power(array, 1 / 2.4) - 0.055)


def resize_width(image: Image.Image, width: int) -> Image.Image:
    height = max(1, round(image.height * width / image.width))
    return image.resize((width, height), Image.Resampling.LANCZOS)


def reorder_bays(image: Image.Image, order: list[int]) -> Image.Image:
    """Reorder equal-width bays while preserving exact output dimensions."""
    if sorted(order) != list(range(len(order))):
        raise ValueError("bay order must be a permutation")
    cuts = [round(image.width * index / len(order)) for index in range(len(order) + 1)]
    output = Image.new(image.mode, image.size)
    cursor = 0
    for source_index in order:
        crop = image.crop((cuts[source_index], 0, cuts[source_index + 1], image.height))
        target_width = cuts[order.index(source_index) + 1] - cuts[order.index(source_index)]
        if crop.width != target_width:
            crop = crop.resize((target_width, image.height), Image.Resampling.LANCZOS)
        output.paste(crop, (cursor, 0))
        cursor += crop.width
    return output


def mask_from_regions(size: tuple[int, int], regions: list[list[float]]) -> Image.Image:
    """Create a crisp registered semantic mask from audited opening bounds."""
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    width, height = size
    for x0, y0, x1, y1 in regions:
        box = (
            round(x0 * width), round(y0 * height),
            round(x1 * width), round(y1 * height),
        )
        draw.rounded_rectangle(box, radius=max(2, round(min(width, height) * 0.006)), fill=255)
    return mask


def crop_normalized(image: Image.Image, bounds: tuple[float, float]) -> Image.Image:
    top, bottom = bounds
    return image.crop((0, round(image.height * top), image.width, round(image.height * bottom)))


def stitch_horizontal_slices(
    image: Image.Image,
    slices: tuple[tuple[float, float], ...],
) -> Image.Image:
    """Join audited facade slices without rescaling their architectural details."""
    crops = [
        image.crop((round(image.width * left), 0, round(image.width * right), image.height))
        for left, right in slices
    ]
    output = Image.new(image.mode, (sum(crop.width for crop in crops), image.height))
    cursor = 0
    for crop in crops:
        output.paste(crop, (cursor, 0))
        cursor += crop.width
    return output


def delight_image(image: Image.Image, strength: float = 0.82) -> Image.Image:
    """Remove broad baked illumination while retaining joints and patina."""
    rgb = np.asarray(image.convert("RGB"), dtype=np.float32) / 255.0
    linear = _srgb_to_linear(rgb)
    luminance = np.sum(linear * np.array([0.2126, 0.7152, 0.0722], dtype=np.float32), axis=2)
    luminance_image = Image.fromarray(np.uint8(np.clip(luminance, 0, 1) * 255), mode="L")
    radius_a = max(18.0, min(image.size) / 26.0)
    radius_b = max(42.0, min(image.size) / 9.0)
    illumination_a = np.asarray(luminance_image.filter(ImageFilter.GaussianBlur(radius_a)), dtype=np.float32) / 255.0
    illumination_b = np.asarray(luminance_image.filter(ImageFilter.GaussianBlur(radius_b)), dtype=np.float32) / 255.0
    illumination = illumination_a * 0.62 + illumination_b * 0.38
    valid = illumination[illumination > 0.025]
    target = float(np.median(valid)) if valid.size else 0.5
    correction = np.power(target / np.maximum(illumination, 0.035), strength)
    correction = np.clip(correction, 0.58, 1.85)
    corrected = np.clip(linear * correction[:, :, None], 0.0, 1.0)
    # Restore only high-frequency material variation; broad directional shade
    # remains removed so City Prompt's sun can light the geometry itself.
    output = np.clip(_linear_to_srgb(corrected), 0.0, 1.0)
    return Image.fromarray(np.uint8(output * 255), mode="RGB")


def derive_depth(albedo: Image.Image, glass_mask: Image.Image) -> np.ndarray:
    grey = np.asarray(albedo.convert("L"), dtype=np.float32) / 255.0
    blur = np.asarray(
        Image.fromarray(np.uint8(grey * 255), mode="L").filter(ImageFilter.GaussianBlur(max(2.0, albedo.width / 420))),
        dtype=np.float32,
    ) / 255.0
    detail = np.clip((grey - blur) * 1.35, -0.20, 0.20)
    height = np.clip(0.54 + detail, 0.18, 0.86)
    glass = np.asarray(glass_mask.convert("L"), dtype=np.float32) / 255.0
    # Vision glass is a real recess, not a painted dark rectangle.
    height = height * (1.0 - glass) + 0.16 * glass
    return height.astype(np.float32)


def derive_normal(height: np.ndarray, strength: float = 9.0) -> Image.Image:
    gradient_y, gradient_x = np.gradient(height)
    nx = -gradient_x * strength
    ny = gradient_y * strength
    nz = np.ones_like(height)
    length = np.sqrt(nx * nx + ny * ny + nz * nz)
    normal = np.stack((nx / length, ny / length, nz / length), axis=2)
    normal = np.clip(normal * 0.5 + 0.5, 0.0, 1.0)
    return Image.fromarray(np.uint8(normal * 255), mode="RGB")


def derive_roughness(albedo: Image.Image, glass_mask: Image.Image) -> Image.Image:
    rgb = np.asarray(albedo.convert("RGB"), dtype=np.float32) / 255.0
    value = rgb.max(axis=2)
    saturation = rgb.max(axis=2) - rgb.min(axis=2)
    roughness = np.full(value.shape, 0.76, dtype=np.float32)
    dark_metal = (value < 0.30) & (saturation < 0.22)
    roughness[dark_metal] = 0.34
    glass = np.asarray(glass_mask.convert("L"), dtype=np.float32) / 255.0
    roughness = roughness * (1.0 - glass) + 0.13 * glass
    micro = np.asarray(albedo.convert("L").filter(ImageFilter.FIND_EDGES), dtype=np.float32) / 255.0
    roughness = np.clip(roughness + micro * 0.07 * (1.0 - glass), 0.08, 0.94)
    return Image.fromarray(np.uint8(roughness * 255), mode="L")


def derive_ao(height: np.ndarray) -> Image.Image:
    source = Image.fromarray(np.uint8(np.clip(height, 0, 1) * 255), mode="L")
    nearby = np.asarray(source.filter(ImageFilter.GaussianBlur(5.0)), dtype=np.float32) / 255.0
    cavity = np.maximum(nearby - height, 0.0)
    ao = np.clip(1.0 - cavity * 3.4, 0.42, 1.0)
    return Image.fromarray(np.uint8(ao * 255), mode="L")


def derive_emissive(albedo: Image.Image, glass_mask: Image.Image) -> Image.Image:
    glass = np.asarray(glass_mask.convert("L"), dtype=np.float32) / 255.0
    rgb = np.asarray(albedo.convert("RGB"), dtype=np.float32) / 255.0
    luminance = np.sum(rgb * np.array([0.2126, 0.7152, 0.0722], dtype=np.float32), axis=2)
    # All occupied windows remain legible.  Preserve some authored variation,
    # but never return to the dead navy/off panes that motivated the glass LOD.
    intensity = glass * np.clip(0.30 + luminance * 0.55, 0.30, 0.82)
    warm = np.array([1.0, 0.69, 0.38], dtype=np.float32)
    emissive = intensity[:, :, None] * warm[None, None, :]
    return Image.fromarray(np.uint8(np.clip(emissive, 0, 1) * 255), mode="RGB")


def build_pbr_set(image: Image.Image, mask: Image.Image) -> dict[str, Image.Image]:
    albedo = delight_image(image)
    depth = derive_depth(albedo, mask)
    return {
        "albedo": albedo,
        "normal": derive_normal(depth),
        "roughness": derive_roughness(albedo, mask),
        "ao": derive_ao(depth),
        "depth": Image.fromarray(np.uint16(np.clip(depth, 0, 1) * 65535)),
        "emissive": derive_emissive(albedo, mask),
    }


def _save_set(images: dict[str, Image.Image], output: Path, stem: str) -> dict[str, str | list[int]]:
    output.mkdir(parents=True, exist_ok=True)
    payload: dict[str, str | list[int]] = {"px": list(images["albedo"].size)}
    for key in PBR_KEYS:
        filename = f"{stem}_{key}.png"
        kwargs = {"compress_level": 7}
        images[key].save(output / filename, **kwargs)
        payload[key] = (output.name + "/" + filename).replace("\\", "/")
    return payload


def process_source(
    source: Image.Image,
    *,
    near_width: int,
    far_width: int,
    output: Path,
    stem: str,
    mask: Image.Image | None = None,
    regions: list[list[float]] | None = None,
) -> tuple[dict, Image.Image, Image.Image]:
    near_source = resize_width(source, near_width)
    raw_mask = (
        mask_from_regions(near_source.size, regions)
        if regions is not None else
        mask or derive_glass_mask_fallback(near_source)
    )
    near_mask = normalize_semantic_glass_mask(raw_mask, near_source.size)
    near_images = build_pbr_set(near_source, near_mask)
    far_images = {
        key: resize_width(value, far_width)
        for key, value in near_images.items()
    }
    near_payload = _save_set(near_images, output / "near", stem)
    far_payload = _save_set(far_images, output / "far", stem)
    near_mask.save(output / "near" / f"{stem}_glass.png", compress_level=7)
    ImageOps.invert(near_mask).save(output / "near" / f"{stem}_opaque.png", compress_level=7)
    far_mask = resize_width(near_mask, far_width).point(lambda value: 255 if value >= 128 else 0, mode="L")
    far_mask.save(output / "far" / f"{stem}_glass.png", compress_level=7)
    ImageOps.invert(far_mask).save(output / "far" / f"{stem}_opaque.png", compress_level=7)
    near_payload.update({
        "glass_mask": f"near/{stem}_glass.png",
        "opaque_mask": f"near/{stem}_opaque.png",
    })
    far_payload.update({
        "glass_mask": f"far/{stem}_glass.png",
        "opaque_mask": f"far/{stem}_opaque.png",
    })
    return {"near": near_payload, "far": far_payload}, near_mask, far_mask


def upgrade(
    source_dir: Path,
    output_dir: Path,
    near_width: int,
    far_width: int,
    elevation_override: Path | None = None,
) -> Path:
    source_manifest = json.loads((source_dir / "manifest.json").read_text(encoding="utf-8"))
    output_dir.mkdir(parents=True, exist_ok=True)
    elevation_path = elevation_override or source_dir / str(
        source_manifest.get("elevation_source") or "elevation_raw.jpg"
    )
    if not elevation_path.exists():
        raise FileNotFoundError(f"facade elevation does not exist: {elevation_path}")
    elevation_source_name = "elevation_source" + elevation_path.suffix.lower()
    shutil.copy2(elevation_path, output_dir / elevation_source_name)

    elevation = Image.open(elevation_path).convert("RGB")
    semantic_elevation = source_manifest.get("semantic_glass") or {}
    semantic_mask_name = semantic_elevation.get("glass_mask")
    semantic_mask_path = source_dir / semantic_mask_name if semantic_mask_name else None
    semantic_mask = (
        Image.open(semantic_mask_path).convert("L")
        if semantic_mask_path and semantic_mask_path.exists() else None
    )
    elevation_lods, elevation_mask, _ = process_source(
        elevation, near_width=near_width, far_width=far_width,
        output=output_dir, stem="elevation",
        mask=semantic_mask,
    )

    bands: dict[str, dict] = {}
    archetype_id = str(source_manifest.get("archetype_id") or "")
    # A render-locked facade source can carry its own audited construction
    # datums. This lets the convergence pipeline replace the identity image
    # without silently reusing crop coordinates from an older elevation with
    # a different number or proportion of storeys.
    manifest_layout = source_manifest.get("audited_band_layout")
    audited_layout = (
        manifest_layout if isinstance(manifest_layout, dict)
        else AUDITED_BAND_LAYOUTS.get(archetype_id)
    )
    audited_crops = audited_layout["crops"] if audited_layout else {}
    audited_regions = audited_layout.get("glass_regions", {}) if audited_layout else {}
    podium_outer_slices = tuple(
        tuple(float(value) for value in bounds)
        for bounds in (audited_layout or {}).get(
            "podium_outer_slices", CHATEAUESQUE_PODIUM_OUTER_SLICES,
        )
    )
    podium_repeat_regions = (audited_layout or {}).get(
        "podium_repeat_glass_regions", CHATEAUESQUE_PODIUM_REPEAT_GLASS_REGIONS,
    )
    entrance_x_bounds = tuple(
        float(value) for value in (audited_layout or {}).get(
            "entrance_x_bounds", CHATEAUESQUE_ENTRANCE_X_BOUNDS,
        )
    )
    entrance_regions = (audited_layout or {}).get(
        "entrance_glass_regions", [[0.29, 0.14, 0.71, 0.74]],
    )
    fixed_entrance_layout = bool(
        audited_layout and audited_layout.get("entrance_x_bounds")
    )
    # ``side`` is a deliberately clean secondary-elevation bay generated from
    # the render-locked atlas.  Keep it through the PBR upgrade so identity
    # features such as signs, portals and fire escapes do not wrap around the
    # corners as a flat photograph.
    for role in ("floor", "floor_alt", "side", "crown", "podium"):
        source_band = source_manifest["bands"].get(role)
        if not source_band:
            continue
        role_is_audited_crop = bool(audited_layout and role in audited_crops)
        image = (
            crop_normalized(elevation, audited_crops[role])
            if role_is_audited_crop else
            Image.open(source_dir / source_band["albedo"]).convert("RGB")
        )
        role_regions = audited_regions.get(role) if role_is_audited_crop else None
        if role == "podium" and (
            archetype_id == "chateauesque_grand_railway_hotel" or fixed_entrance_layout
        ):
            # The middle ceremonial portal is a fixed landmark. Remove it from
            # the repeatable podium strip so resizing adds arched window bays,
            # not a new grand entrance every 9.6 metres.
            image = stitch_horizontal_slices(image, podium_outer_slices)
            role_regions = podium_repeat_regions
        source_mask_name = source_band.get("glass_mask")
        source_mask_path = source_dir / source_mask_name if source_mask_name else None
        source_mask = (
            Image.open(source_mask_path).convert("L")
            if source_mask_path and source_mask_path.exists() else None
        )
        lods, near_mask, _ = process_source(
            image, near_width=near_width, far_width=far_width,
            output=output_dir, stem=role,
            mask=source_mask,
            regions=role_regions,
        )
        bands[role] = {
            **source_band,
            **lods["far"],
            "lods": lods,
            "glass_regions": extract_glass_regions(near_mask),
            "audited_storey_crop": role_is_audited_crop,
            "audited_openings": bool(audited_regions.get(role) or source_mask is not None),
            "source_crop_normalized": (
                list(audited_crops[role]) if role_is_audited_crop
                else source_band.get("source_crop_normalized")
            ),
        }

    if archetype_id == "chateauesque_grand_railway_hotel" or fixed_entrance_layout:
        podium_full = crop_normalized(elevation, audited_crops["podium"])
        entrance_left, entrance_right = entrance_x_bounds
        entrance_image = podium_full.crop((
            round(podium_full.width * entrance_left), 0,
            round(podium_full.width * entrance_right), podium_full.height,
        ))
        entrance_lods, entrance_mask, _ = process_source(
            entrance_image, near_width=near_width, far_width=far_width,
            output=output_dir, stem="entrance",
            regions=entrance_regions,
        )
        bands["entrance"] = {
            "height_m": source_manifest["bands"]["podium"].get("height_m", 4.5),
            **entrance_lods["far"],
            "lods": entrance_lods,
            "glass_regions": extract_glass_regions(entrance_mask),
            "audited_storey_crop": True,
            "audited_openings": True,
            "fixed_landmark": "central_entrance",
            "source_x_bounds_normalized": list(entrance_x_bounds),
        }

    # A third repeatable floor changes only the middle bays.  Bay zero and bay
    # three remain stable termination/corner conditions at every building size.
    source_alt = source_manifest["bands"].get("floor_alt") or source_manifest["bands"]["floor"]
    floor_c_source = (
        crop_normalized(elevation, audited_crops["floor_alt"])
        if audited_layout else
        Image.open(source_dir / source_alt["albedo"]).convert("RGB")
    )
    floor_c_image = reorder_bays(floor_c_source, [0, 2, 1, 3])
    floor_c_source_mask_name = source_alt.get("glass_mask")
    floor_c_source_mask_path = source_dir / floor_c_source_mask_name if floor_c_source_mask_name else None
    floor_c_registered_mask = (
        reorder_bays(Image.open(floor_c_source_mask_path).convert("L"), [0, 2, 1, 3])
        if not audited_layout and floor_c_source_mask_path and floor_c_source_mask_path.exists()
        else None
    )
    floor_c_lods, floor_c_mask, _ = process_source(
        floor_c_image, near_width=near_width, far_width=far_width,
        output=output_dir, stem="floor_c",
        mask=floor_c_registered_mask,
        regions=audited_regions.get("floor_alt") if audited_layout else None,
    )
    bands["floor_c"] = {
        **source_alt,
        **floor_c_lods["far"],
        "lods": floor_c_lods,
        "glass_regions": extract_glass_regions(floor_c_mask),
        "variant_of": "floor_alt",
        "middle_bay_order": [2, 1],
        "audited_storey_crop": bool(audited_layout),
        "audited_openings": bool(audited_regions.get("floor_alt") or floor_c_registered_mask is not None),
        "source_crop_normalized": list(audited_crops["floor_alt"]) if audited_layout else None,
    }

    manifest = {
        **source_manifest,
        "schema": "facade-sheet@5",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source_manifest_schema": source_manifest.get("schema"),
        "elevation_source": elevation_source_name,
        "reference_guided_source": {
            "enabled": elevation_override is not None,
            "source_filename": elevation_path.name,
            "role": "shadow-neutral orthographic identity atlas",
        },
        "audited_layout_source": "manifest" if isinstance(manifest_layout, dict) else "built-in",
        "pbr_lods": elevation_lods,
        "semantic_glass": {
            "glass_mask": elevation_lods["far"]["glass_mask"],
            "opaque_mask": elevation_lods["far"]["opaque_mask"],
            "glass_regions": extract_glass_regions(elevation_mask),
            "method": "deterministic-semantic-fallback",
        },
        "bands": bands,
        "span_m": (
            float(source_manifest.get("requested_span_m"))
            if audited_layout and source_manifest.get("requested_span_m") else
            source_manifest.get("span_m")
        ),
        "bay_strategy": {
            "sheet_bays": 4,
            "fixed_end_bays": [0, 3],
            "repeatable_middle_bays": [1, 2],
            "middle_variants": ["floor", "floor_alt", "floor_c"],
            "rule": "entrance, corner, crown and roof remain fixed; only middle floor bays repeat",
        },
        "shadow_neutral": {
            "enabled": True,
            "method": "multiscale-linear-delighting plus audited storey crops",
            "lighting_authority": "City Prompt environment and sun",
        },
        "delivery": {
            "near_atlas_width_px": near_width,
            "far_atlas_width_px": far_width,
            "near_usage": "close-range physical glazing and PBR facade",
            "far_usage": "city-scale baked facade",
            "container": "PNG source; KTX2/UASTC packaged at GLB delivery",
        },
    }
    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--elevation",
        type=Path,
        default=None,
        help="optional reference-guided elevation image replacing source/elevation_raw.jpg",
    )
    parser.add_argument("--near-width", type=int, default=2048)
    parser.add_argument("--far-width", type=int, default=1024)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.near_width < 2048 or args.near_width > 4096:
        raise SystemExit("--near-width must be between 2048 and 4096")
    if args.far_width >= args.near_width:
        raise SystemExit("--far-width must be smaller than --near-width")
    print(upgrade(
        args.source.resolve(),
        args.output.resolve(),
        args.near_width,
        args.far_width,
        args.elevation.resolve() if args.elevation else None,
    ))


if __name__ == "__main__":
    main()
