"""Prepare the render-locked skin package for Wave 4 standard buildings.

The Historical Brick Main Street pilot reuses the reviewed GPT elevation and
PBR channels preserved in the external production artifact store.  Those
assets are promoted into the family before this script runs.  This script adds
the roof-specific PBR set and writes the canonical skin manifest consumed by
the Blender generator and quality assessor.

Run from the repository root:

    python tools/archetype_compiler/prepare_wave4_standard_skin.py
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_FAMILY_DIR = (
    REPO_ROOT / "frontend" / "public" / "families" / "historical-brick-main-street"
)
CHANNELS = ("albedo", "normal", "roughness", "ao", "depth", "emissive")
MASKS = ("glass_mask", "opaque_mask")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--family-dir",
        type=Path,
        default=DEFAULT_FAMILY_DIR,
        help="Delivered Historical Brick Main Street family directory.",
    )
    return parser.parse_args()


def _save_rgb(path: Path, pixels: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(np.clip(pixels, 0, 255).astype(np.uint8), "RGB").save(
        path,
        optimize=True,
    )


def _save_l(path: Path, pixels: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(np.clip(pixels, 0, 255).astype(np.uint8), "L").save(
        path,
        optimize=True,
    )


def generate_corrugated_roof(root: Path, lod: str, width: int) -> None:
    """Create a shadow-neutral galvanized corrugated roof from roof-plan cues."""
    height = width // 2
    rng = np.random.default_rng(4404 if lod == "near" else 4405)
    x = np.arange(width, dtype=np.float32)[None, :]
    y = np.arange(height, dtype=np.float32)[:, None]
    period = width / 38.0

    primary = 0.5 + 0.5 * np.cos((2.0 * np.pi * x) / period)
    seam = np.exp(-((np.mod(x, period) - period * 0.5) / (period * 0.075)) ** 2)
    broad_weather = (
        0.55
        + 0.22 * np.sin(y / max(20.0, height / 13.0))
        + 0.12 * np.sin((x + y * 0.35) / max(32.0, width / 21.0))
    )
    noise = rng.normal(0.0, 1.0, size=(height, width)).astype(np.float32)

    base = np.empty((height, width, 3), dtype=np.float32)
    roof_colour = np.array([143.0, 145.0, 142.0], dtype=np.float32)
    base[:] = roof_colour
    base += (primary[..., None] - 0.5) * 15.0
    base += (broad_weather[..., None] - 0.5) * np.array([13.0, 10.0, 7.0])
    base += noise[..., None] * 2.2
    base -= seam[..., None] * 17.0

    depth = np.clip(105.0 + primary * 95.0 + seam * 50.0, 0.0, 255.0)
    dx = np.gradient(depth, axis=1)
    normal = np.empty((height, width, 3), dtype=np.float32)
    normal[..., 0] = np.clip(128.0 - dx * 2.4, 0.0, 255.0)
    normal[..., 1] = 128.0
    normal[..., 2] = np.clip(246.0 - np.abs(dx) * 0.35, 176.0, 255.0)
    roughness = np.clip(166.0 + noise * 8.0 + broad_weather * 12.0, 128.0, 212.0)
    ao = np.clip(244.0 - seam * 42.0 - (1.0 - primary) * 8.0, 180.0, 255.0)

    output = root / "textures" / "pbr" / lod
    _save_rgb(output / "roof_albedo.png", base)
    _save_rgb(output / "roof_normal.png", normal)
    _save_l(output / "roof_roughness.png", roughness)
    _save_l(output / "roof_ao.png", ao)
    _save_l(output / "roof_depth.png", depth)
    _save_rgb(output / "roof_emissive.png", np.zeros_like(base))
    _save_l(output / "roof_glass.png", np.zeros((height, width), dtype=np.uint8))
    _save_l(output / "roof_opaque.png", np.full((height, width), 255, dtype=np.uint8))


def _dilate(mask: np.ndarray, radius: int) -> np.ndarray:
    """Return a small antialias-friendly dilation without a scipy dependency."""
    diameter = max(3, radius * 2 + 1)
    if diameter % 2 == 0:
        diameter += 1
    image = Image.fromarray(mask.astype(np.uint8) * 255, "L")
    return np.asarray(image.filter(ImageFilter.MaxFilter(diameter))) > 127


def _arched_openings(
    width: int,
    height: int,
    centres: tuple[float, ...],
) -> np.ndarray:
    """Create the three reference-registered side-wall window voids."""
    yy, xx = np.mgrid[0:height, 0:width]
    x_norm = (xx + 0.5) / width
    y_norm = (yy + 0.5) / height
    radius = 0.028
    spring_y = 0.32
    bottom_y = 0.86
    result = np.zeros((height, width), dtype=bool)
    for centre in centres:
        jamb = (
            (np.abs(x_norm - centre) <= radius)
            & (y_norm >= spring_y)
            & (y_norm <= bottom_y)
        )
        arch = (
            ((x_norm - centre) ** 2 + (y_norm - spring_y) ** 2 <= radius**2)
            & (y_norm < spring_y)
        )
        result |= jamb | arch
    return result


def generate_polychrome_side_wall(root: Path, lod: str, width: int) -> None:
    """Author the long secondary elevation from the 60-degree reference.

    This is deliberately not a generic brick tile.  It encodes the selected
    variant's red pressed-brick scale, three paired cream courses per LEGO
    storey, restrained weathering, and three registered arched openings.  The
    same datums repeat cleanly when a user adds one whole upper-floor module.
    """
    # Match the delivered module's 21.4:3.6 aspect so one brick remains close
    # to its true 225 x 75 mm size after UV mapping.
    height = width * 11 // 64
    rng = np.random.default_rng(4414 if lod == "near" else 4415)
    mortar = max(1, width // 1024)
    course_count = 48
    course_height = height / course_count
    brick_width = course_height * 3.0

    albedo = np.empty((height, width, 3), dtype=np.float32)
    # Red-brown mortar avoids a pale moire veil when the true-scale brick grid
    # minifies in city views; the cream courses receive their own pale mortar.
    albedo[:] = (108.0, 78.0, 62.0)
    depth = np.full((height, width), 88.0, dtype=np.float32)
    roughness = np.full((height, width), 210.0, dtype=np.float32)
    ao = np.full((height, width), 202.0, dtype=np.float32)

    cream_courses = {9, 10, 23, 24, 37, 38}
    for row in range(course_count):
        row_start = int(round(row * course_height))
        row_end = int(round((row + 1) * course_height))
        if row in cream_courses:
            albedo[row_start:row_end] = (166.0, 153.0, 128.0)
        y0 = int(round(row * course_height)) + mortar
        y1 = int(round((row + 1) * course_height)) - mortar
        if y1 <= y0:
            continue
        half_offset = brick_width / 2 if row % 2 else 0.0
        start = -half_offset
        column = 0
        while start < width:
            x0 = max(0, int(round(start)) + mortar)
            x1 = min(width, int(round(start + brick_width)) - mortar)
            if x1 > x0:
                if row in cream_courses:
                    base = np.array((199.0, 182.0, 145.0), dtype=np.float32)
                    colour_jitter = rng.normal(0.0, (5.0, 4.2, 3.2))
                    face_depth = 168.0 + rng.normal(0.0, 4.0)
                    face_roughness = 184.0 + rng.normal(0.0, 5.0)
                else:
                    base = np.array((139.0, 55.0, 35.0), dtype=np.float32)
                    colour_jitter = rng.normal(0.0, (10.0, 6.0, 4.0))
                    face_depth = 151.0 + rng.normal(0.0, 5.0)
                    face_roughness = 202.0 + rng.normal(0.0, 7.0)
                albedo[y0:y1, x0:x1] = base + colour_jitter
                depth[y0:y1, x0:x1] = face_depth
                roughness[y0:y1, x0:x1] = face_roughness
                ao[y0:y1, x0:x1] = 239.0
                # A soft kiln-fired variation keeps long blank wall runs alive.
                if (row + column) % 5 == 0:
                    albedo[y0:y1, x0:x1] *= 0.94
            start += brick_width
            column += 1

    y_gradient = np.linspace(1.04, 0.90, height, dtype=np.float32)[:, None, None]
    albedo *= y_gradient
    broad_weather = (
        0.97
        + 0.03
        * np.sin(
            np.linspace(0.0, 5.0 * np.pi, width, dtype=np.float32)[None, :]
        )
    )
    albedo *= broad_weather[..., None]

    openings = _arched_openings(width, height, (0.21, 0.48, 0.75))
    surround = _dilate(openings, max(4, width // 170)) & ~openings
    outer_shadow = _dilate(openings, max(6, width // 125)) & ~(
        openings | surround
    )
    albedo[outer_shadow] *= 0.76
    depth[outer_shadow] = 108.0
    roughness[outer_shadow] = 218.0
    ao[outer_shadow] = 146.0
    albedo[surround] = (201.0, 184.0, 148.0)
    depth[surround] = 193.0
    roughness[surround] = 178.0
    ao[surround] = 228.0
    albedo[openings] = (8.0, 20.0, 16.0)
    depth[openings] = 42.0
    roughness[openings] = 74.0
    ao[openings] = 54.0

    # Reference-accurate pale sills remain visible even if a runtime LOD drops
    # the physical sill mesh.
    sill_height = max(3, height // 70)
    sill_half_width = int(width * 0.044)
    sill_y = int(height * 0.865)
    for centre in (0.21, 0.48, 0.75):
        cx = int(width * centre)
        x0 = max(0, cx - sill_half_width)
        x1 = min(width, cx + sill_half_width)
        y0 = max(0, sill_y)
        y1 = min(height, sill_y + sill_height)
        albedo[y0:y1, x0:x1] = (211.0, 197.0, 164.0)
        depth[y0:y1, x0:x1] = 205.0
        roughness[y0:y1, x0:x1] = 174.0
        ao[y0:y1, x0:x1] = 235.0

    dx = np.gradient(depth, axis=1)
    dy = np.gradient(depth, axis=0)
    normal = np.empty((height, width, 3), dtype=np.float32)
    normal[..., 0] = np.clip(128.0 - dx * 1.25, 0.0, 255.0)
    normal[..., 1] = np.clip(128.0 + dy * 1.25, 0.0, 255.0)
    normal[..., 2] = np.clip(
        246.0 - (np.abs(dx) + np.abs(dy)) * 0.18,
        174.0,
        255.0,
    )

    output = root / "textures" / "pbr" / lod
    _save_rgb(output / "side_albedo.png", albedo)
    _save_rgb(output / "side_normal.png", normal)
    _save_l(output / "side_roughness.png", roughness)
    _save_l(output / "side_ao.png", ao)
    _save_l(output / "side_depth.png", depth)
    _save_rgb(output / "side_emissive.png", np.zeros_like(albedo))
    _save_l(output / "side_glass.png", openings.astype(np.uint8) * 255)
    _save_l(output / "side_opaque.png", (~openings).astype(np.uint8) * 255)


def generate_pressed_brick_crown(root: Path, lod: str, width: int) -> None:
    """Create the unpierced red-brick side parapet seen in the aerial goalpost."""
    height = max(96, width * 7 // 104)
    rng = np.random.default_rng(4424 if lod == "near" else 4425)
    mortar = max(1, width // 2048)
    course_count = 19
    course_height = height / course_count
    brick_width = course_height * 3.0

    albedo = np.empty((height, width, 3), dtype=np.float32)
    albedo[:] = (169.0, 151.0, 125.0)
    depth = np.full((height, width), 90.0, dtype=np.float32)
    roughness = np.full((height, width), 214.0, dtype=np.float32)
    ao = np.full((height, width), 204.0, dtype=np.float32)
    for row in range(course_count):
        y0 = int(round(row * course_height)) + mortar
        y1 = int(round((row + 1) * course_height)) - mortar
        offset = brick_width / 2 if row % 2 else 0.0
        start = -offset
        column = 0
        while start < width:
            x0 = max(0, int(round(start)) + mortar)
            x1 = min(width, int(round(start + brick_width)) - mortar)
            if x1 > x0 and y1 > y0:
                base = np.array((137.0, 52.0, 32.0), dtype=np.float32)
                albedo[y0:y1, x0:x1] = base + rng.normal(
                    0.0,
                    (9.0, 5.5, 3.5),
                )
                if (row + column) % 6 == 0:
                    albedo[y0:y1, x0:x1] *= 0.94
                depth[y0:y1, x0:x1] = 151.0 + rng.normal(0.0, 4.0)
                roughness[y0:y1, x0:x1] = 202.0 + rng.normal(0.0, 6.0)
                ao[y0:y1, x0:x1] = 239.0
            start += brick_width
            column += 1

    dx = np.gradient(depth, axis=1)
    dy = np.gradient(depth, axis=0)
    normal = np.empty((height, width, 3), dtype=np.float32)
    normal[..., 0] = np.clip(128.0 - dx * 1.25, 0.0, 255.0)
    normal[..., 1] = np.clip(128.0 + dy * 1.25, 0.0, 255.0)
    normal[..., 2] = np.clip(
        246.0 - (np.abs(dx) + np.abs(dy)) * 0.18,
        174.0,
        255.0,
    )

    output = root / "textures" / "pbr" / lod
    _save_rgb(output / "side_crown_albedo.png", albedo)
    _save_rgb(output / "side_crown_normal.png", normal)
    _save_l(output / "side_crown_roughness.png", roughness)
    _save_l(output / "side_crown_ao.png", ao)
    _save_l(output / "side_crown_depth.png", depth)
    _save_rgb(output / "side_crown_emissive.png", np.zeros_like(albedo))
    _save_l(
        output / "side_crown_glass.png",
        np.zeros((height, width), dtype=np.uint8),
    )
    _save_l(
        output / "side_crown_opaque.png",
        np.full((height, width), 255, dtype=np.uint8),
    )


def generate_weathered_service_deck(root: Path, lod: str, width: int) -> None:
    """Author the dark granular plant deck visible in the 90-degree reference."""
    height = width
    rng = np.random.default_rng(4434 if lod == "near" else 4435)
    yy, xx = np.mgrid[0:height, 0:width]
    fine = rng.normal(0.0, 1.0, size=(height, width)).astype(np.float32)
    broad = (
        np.sin(xx / max(32.0, width / 13.0))
        + np.cos(yy / max(38.0, width / 11.0))
        + 0.55 * np.sin((xx + yy) / max(45.0, width / 9.0))
    )
    drain_wash = np.exp(
        -(
            ((xx - width * 0.70) / (width * 0.20)) ** 2
            + ((yy - height * 0.34) / (height * 0.13)) ** 2
        )
    )
    albedo = np.empty((height, width, 3), dtype=np.float32)
    albedo[:] = (72.0, 70.0, 65.0)
    albedo += fine[..., None] * np.array((5.0, 4.5, 4.0))
    albedo += broad[..., None] * np.array((4.2, 3.8, 3.2))
    albedo -= drain_wash[..., None] * np.array((14.0, 13.0, 11.0))

    # Subtle patched felts echo the irregular service zones in the roof image.
    for x0, y0, x1, y1, delta in (
        (0.08, 0.16, 0.35, 0.37, 6.0),
        (0.50, 0.58, 0.88, 0.82, -5.0),
        (0.18, 0.69, 0.44, 0.91, 3.5),
    ):
        left, top = int(width * x0), int(height * y0)
        right, bottom = int(width * x1), int(height * y1)
        albedo[top:bottom, left:right] += delta

    depth = np.clip(126.0 + fine * 7.0 + broad * 2.5, 94.0, 160.0)
    dx = np.gradient(depth, axis=1)
    dy = np.gradient(depth, axis=0)
    normal = np.empty((height, width, 3), dtype=np.float32)
    normal[..., 0] = np.clip(128.0 - dx * 1.4, 0.0, 255.0)
    normal[..., 1] = np.clip(128.0 + dy * 1.4, 0.0, 255.0)
    normal[..., 2] = 246.0
    roughness = np.clip(224.0 + fine * 5.0 + drain_wash * 12.0, 198.0, 252.0)
    ao = np.clip(240.0 - np.abs(broad) * 6.0 - drain_wash * 18.0, 196.0, 248.0)

    output = root / "textures" / "pbr" / lod
    _save_rgb(output / "deck_albedo.png", albedo)
    _save_rgb(output / "deck_normal.png", normal)
    _save_l(output / "deck_roughness.png", roughness)
    _save_l(output / "deck_ao.png", ao)
    _save_l(output / "deck_depth.png", depth)
    _save_rgb(output / "deck_emissive.png", np.zeros_like(albedo))
    _save_l(output / "deck_glass.png", np.zeros((height, width), dtype=np.uint8))
    _save_l(output / "deck_opaque.png", np.full((height, width), 255, dtype=np.uint8))


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


def verify_assets(family_dir: Path, zones: dict[str, dict[str, dict[str, str]]]) -> None:
    missing: list[str] = []
    for zone in zones.values():
        for lod in ("near", "far"):
            for relative in zone[lod].values():
                if not (family_dir / relative).is_file():
                    missing.append(relative)
    if missing:
        raise FileNotFoundError(
            "Wave 4 skin package is incomplete:\n" + "\n".join(sorted(missing))
        )


def main() -> int:
    args = parse_args()
    family_dir = args.family_dir.resolve()
    generate_corrugated_roof(family_dir, "near", 2048)
    generate_corrugated_roof(family_dir, "far", 1024)
    generate_polychrome_side_wall(family_dir, "near", 2048)
    generate_polychrome_side_wall(family_dir, "far", 1024)
    generate_pressed_brick_crown(family_dir, "near", 2048)
    generate_pressed_brick_crown(family_dir, "far", 1024)
    generate_weathered_service_deck(family_dir, "near", 1024)
    generate_weathered_service_deck(family_dir, "far", 512)

    prefixes = {
        "facade": "elevation",
        "podium": "podium",
        "floor_a": "floor",
        "floor_b": "floor_alt",
        "floor_c": "floor_c",
        "crown": "crown",
        "side": "side",
        "side_crown": "side_crown",
        "deck": "deck",
        "roof": "roof",
    }
    zones = {
        zone: {
            "near": zone_assets(prefix, "near"),
            "far": zone_assets(prefix, "far"),
        }
        for zone, prefix in prefixes.items()
    }
    verify_assets(family_dir, zones)

    manifest = {
        "schema": "wave4-standard-skin@1",
        "family": "historical-brick-main-street",
        "source": "textures/source/elevation-source.jpg",
        "source_model": "gpt-image-2",
        "sources": {
            "archetype_goalpost": "textures/source/archetype-goalpost.png",
            "orthographic_elevation": "textures/source/elevation-source.jpg",
            "angle_reference": "textures/source/angle-reference-60.jpg",
            "roof_reference": "textures/source/angle-reference-90.jpg",
            "registered_openings": "textures/source/registered-openings.json",
            "registered_bands": "textures/source/registered-bands.json",
            "provider_manifest": "textures/source/legacy-pbr-manifest.json",
        },
        "registration": (
            "The full Victorian polychrome elevation is render-locked to the "
            "selected catalogue variant. Audited bands and openings drive the "
            "front, while a dedicated reference-authored polychrome side wall "
            "and roof-plan-derived corrugated PBR set complete the orbit-visible "
            "envelope."
        ),
        "reference_registration": {
            "mode": "archetype_specific",
            "source_archetype_id": "historical_brick_main_street",
            "source_variant_id": "historical_brick_victorian",
            "registered_elevations": ["front", "left", "right", "rear", "roof"],
            "registered_surfaces": [
                "victorian_polychrome_facade",
                "forest_green_cast_iron_storefront",
                "round_arch_upper_sashes",
                "carved_cornice_and_parapet",
                "pressed_brick_side_parapet",
                "weathered_gravel_service_deck",
                "corrugated_concealed_roof",
            ],
            "uv_strategy": (
                "registered_full_front_elevation_and_reference-authored "
                "secondary-elevation modules"
            ),
            "depth_binding": "shader_bump",
            "generic_tiling_allowed": False,
        },
        "channels": list(CHANNELS),
        "semantic_masks": list(MASKS),
        "zones": zones,
        "atlases": {
            "near": zone_assets("elevation", "near"),
            "far": zone_assets("elevation", "far"),
        },
    }
    destination = family_dir / "textures" / "skin_manifest.json"
    destination.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(destination)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
