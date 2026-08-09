"""Derive export-ready, non-uniform PBR textures for a bounded building pilot.

The source library remains the material truth.  This pass adds restrained,
tile-safe macro variation and location-specific material variants, then writes
ordinary image maps that the glTF exporter can carry without Blender-only
procedural nodes.
"""
from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image


@dataclass(frozen=True)
class StoryRecipe:
    output_key: str
    source_key: str
    tint: tuple[int, int, int]
    tint_mix: float
    macro_strength: float
    roughness_strength: float
    normal_strength: float
    seed: int
    role: str


RECIPES = (
    StoryRecipe(
        "limestone_story_v83", "limestone", (206, 193, 168), 0.20,
        0.055, 0.080, 1.85, 83, "clean dressed limestone with broad tonal variation",
    ),
    StoryRecipe(
        "limestone_patina_v83", "limestone", (184, 171, 146), 0.28,
        0.105, 0.135, 1.95, 183, "lower-course and cornice limestone with restrained water patina",
    ),
    StoryRecipe(
        "red_brick_story_v83", "red_brick", (119, 72, 55), 0.16,
        0.075, 0.095, 1.30, 283, "soot-softened terminal brick with non-uniform roughness",
    ),
    StoryRecipe(
        "standing_seam_story_v83", "standing_seam", (74, 91, 88), 0.30,
        0.085, 0.115, 1.25, 383, "oxidized grey-green standing seam with panel-scale patina",
    ),
    StoryRecipe(
        "concrete_roof_story_v83", "concrete", (154, 151, 143), 0.38,
        0.095, 0.145, 1.30, 483, "pale mineral roof surface with drainage-scale tonal breakup",
    ),
    StoryRecipe(
        "pale_granite_story_v84", "granite", (208, 204, 194), 0.34,
        0.050, 0.075, 1.60, 584, "pale courthouse granite with broad ashlar-scale tonal variation",
    ),
    StoryRecipe(
        "pale_granite_detail_v84", "granite", (224, 219, 207), 0.44,
        0.035, 0.065, 1.45, 684, "cleaner pale granite for columns, steps and portico detail",
    ),
    StoryRecipe(
        "verdigris_copper_story_v84", "standing_seam", (84, 121, 105), 0.66,
        0.050, 0.105, 1.18, 784, "green-patina courthouse copper with panel-scale oxidation",
    ),
    StoryRecipe(
        "natural_stone_story_v84", "natural_stone", (163, 139, 104), 0.24,
        0.085, 0.115, 1.65, 884, "warm rough-cut arcade stone with restrained protected-face variation",
    ),
    StoryRecipe(
        "ochre_stucco_story_v84", "stucco", (194, 146, 83), 0.42,
        0.060, 0.095, 1.35, 984, "ochre lime stucco with broad hand-applied tonal movement",
    ),
    StoryRecipe(
        "terracotta_roof_story_v84", "mediterranean_roof_tile", (145, 91, 60), 0.24,
        0.070, 0.115, 1.35, 1084, "weathered terracotta roof covering with bounded tile-field variation",
    ),
    StoryRecipe(
        "red_brick_story_v84", "red_brick", (62, 36, 32), 0.48,
        0.055, 0.105, 1.45, 1184, "dark Richardsonian brick with soot-softened field variation",
    ),
    StoryRecipe(
        "brownstone_story_v84", "brownstone", (103, 72, 55), 0.24,
        0.075, 0.120, 1.55, 1284, "rusticated brownstone base and loading-bay surround",
    ),
    StoryRecipe(
        "roof_membrane_story_v84", "roof_membrane", (48, 49, 48), 0.38,
        0.055, 0.105, 1.20, 1384, "dark built-up roof membrane with drainage-scale variation",
    ),
)


def periodic_noise(size: int, seed: int) -> np.ndarray:
    """Return deterministic seamless low-frequency noise in the range -1..1."""
    rng = np.random.default_rng(seed)
    y, x = np.mgrid[0:size, 0:size].astype(np.float32)
    x /= size
    y /= size
    field = np.zeros((size, size), dtype=np.float32)
    weight = 0.0
    for frequency, amplitude in ((1, 1.0), (2, 0.58), (3, 0.31), (5, 0.16)):
        for _ in range(3):
            kx = int(rng.integers(0, frequency + 1))
            ky = int(rng.integers(0, frequency + 1))
            if kx == 0 and ky == 0:
                kx = frequency
            phase = float(rng.uniform(0.0, math.tau))
            field += amplitude * np.sin(math.tau * (kx * x + ky * y) + phase)
            weight += amplitude
    field /= max(weight, 1e-6)
    field -= field.mean()
    peak = max(abs(float(field.min())), abs(float(field.max())), 1e-6)
    return field / peak


def load_rgb(path: Path, size: int) -> np.ndarray:
    image = Image.open(path).convert("RGB").resize((size, size), Image.Resampling.LANCZOS)
    return np.asarray(image, dtype=np.float32)


def save_rgb(array: np.ndarray, path: Path, *, png: bool = False) -> None:
    image = Image.fromarray(np.clip(array, 0, 255).astype(np.uint8), "RGB")
    if png:
        image.save(path, optimize=True)
    else:
        image.save(path, quality=94, optimize=True, subsampling=0)


def derive(recipe: StoryRecipe, source_root: Path | list[Path], output_root: Path, size: int) -> dict:
    source_roots = [source_root] if isinstance(source_root, Path) else list(source_root)
    source = next(
        (root / recipe.source_key for root in source_roots if (root / recipe.source_key).exists()),
        source_roots[0] / recipe.source_key,
    )
    required = {
        "albedo": source / "albedo.jpg",
        "roughness": source / "roughness.jpg",
        "normal": source / "normal.png",
    }
    missing = [str(path) for path in required.values() if not path.exists()]
    if missing:
        raise FileNotFoundError("missing source PBR maps: " + ", ".join(missing))

    destination = output_root / recipe.output_key
    destination.mkdir(parents=True, exist_ok=True)
    macro = periodic_noise(size, recipe.seed)
    # A second phase produces subtle vertical drainage/soot bands without a
    # hard edge at the tile boundary.
    x = np.arange(size, dtype=np.float32) / size
    vertical = (
        0.56 * np.sin(math.tau * (2 * x + 0.17))
        + 0.29 * np.sin(math.tau * (5 * x + 0.61))
        + 0.15 * np.sin(math.tau * (9 * x + 0.31))
    )[None, :]
    story = np.clip(macro * 0.72 + vertical * 0.28, -1.0, 1.0)

    albedo = load_rgb(required["albedo"], size)
    tint = np.asarray(recipe.tint, dtype=np.float32)[None, None, :]
    albedo = albedo * (1.0 - recipe.tint_mix) + tint * recipe.tint_mix
    albedo *= (1.0 + story[..., None] * recipe.macro_strength)
    save_rgb(albedo, destination / "albedo.jpg")

    roughness = load_rgb(required["roughness"], size)
    roughness += story[..., None] * (255.0 * recipe.roughness_strength)
    save_rgb(roughness, destination / "roughness.jpg")

    normal = load_rgb(required["normal"], size)
    nx = (normal[..., 0] / 127.5 - 1.0) * recipe.normal_strength
    ny = (normal[..., 1] / 127.5 - 1.0) * recipe.normal_strength
    length = np.maximum(1.0, np.sqrt(nx * nx + ny * ny + 1.0))
    encoded = np.empty_like(normal)
    encoded[..., 0] = (nx / length * 0.5 + 0.5) * 255.0
    encoded[..., 1] = (ny / length * 0.5 + 0.5) * 255.0
    encoded[..., 2] = (1.0 / length * 0.5 + 0.5) * 255.0
    save_rgb(encoded, destination / "normal.png", png=True)

    albedo_std = float(np.asarray(Image.open(destination / "albedo.jpg")).std())
    roughness_std = float(np.asarray(Image.open(destination / "roughness.jpg")).std())
    normal_xy_std = float(np.asarray(Image.open(destination / "normal.png"))[..., :2].std())
    return {
        "texture_key": recipe.output_key,
        "source_texture_key": recipe.source_key,
        "role": recipe.role,
        "resolution": [size, size],
        "channels": {
            "albedo": f"{recipe.output_key}/albedo.jpg",
            "roughness": f"{recipe.output_key}/roughness.jpg",
            "normal": f"{recipe.output_key}/normal.png",
        },
        "statistics": {
            "albedo_std": round(albedo_std, 3),
            "roughness_std": round(roughness_std, 3),
            "normal_xy_std": round(normal_xy_std, 3),
        },
        "baked_pbr": True,
        "tile_safe": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--additional-source-root", type=Path, action="append", default=[])
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--size", type=int, default=2048)
    parser.add_argument("--pipeline-version", default="v83")
    args = parser.parse_args()
    if args.size < 512:
        raise ValueError("surface-story textures must be at least 512 px")
    args.output_root.mkdir(parents=True, exist_ok=True)
    source_roots = [args.source_root, *args.additional_source_root]
    materials = [derive(recipe, source_roots, args.output_root, args.size) for recipe in RECIPES]
    manifest = {
        "schema": "surface-story-pbr@1",
        "pipeline_version": args.pipeline_version,
        "method": "tile-safe baked image textures with restrained macro variation",
        "materials": materials,
    }
    path = args.output_root / "surface-story-manifest.json"
    path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(path)


if __name__ == "__main__":
    main()
