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
from PIL import Image, ImageFilter


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
    pattern: str = "source"


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
    StoryRecipe(
        "brownstone_story_v85", "brownstone", (129, 82, 62), 0.24,
        0.060, 0.105, 1.45, 1485, "warm dressed brownstone wall and stoop construction",
    ),
    StoryRecipe(
        "carved_limestone_story_v85", "limestone", (218, 209, 187), 0.40,
        0.045, 0.070, 1.90, 1585, "pale carved limestone trim and cornice detail",
    ),
    StoryRecipe(
        "pale_roof_membrane_story_v85", "roof_membrane", (205, 202, 192), 0.72,
        0.035, 0.080, 1.10, 1635, "pale weathered built-up roof membrane matching the brownstone aerial reference",
    ),
    StoryRecipe(
        "black_metal_story_v85", "black_metal", (35, 37, 38), 0.32,
        0.035, 0.080, 1.10, 1685, "blackened iron rails and restrained architectural metal",
    ),
    StoryRecipe(
        "anodized_aluminum_story_v85", "metal_panel", (116, 128, 136), 0.34,
        0.040, 0.075, 1.05, 1785, "cool anodized aluminum mullions, spandrels and roof screens",
    ),
    StoryRecipe(
        "pale_lobby_stone_story_v85", "granite", (213, 211, 204), 0.46,
        0.030, 0.065, 1.30, 1885, "pale polished lobby stone with restrained mineral variation",
    ),
    StoryRecipe(
        "natural_larch_story_v85", "scandinavian_larch", (161, 113, 67), 0.18,
        0.055, 0.090, 1.35, 1985, "vertical natural-larch infill with bounded board-scale variation",
    ),
    StoryRecipe(
        "honey_glulam_story_v85", "glulam", (151, 99, 49), 0.24,
        0.045, 0.085, 1.25, 2085, "honey-tone glulam structural posts, beams and roof pavilion",
    ),
    StoryRecipe(
        "sedum_roof_story_v85", "sedum_roof", (91, 105, 60), 0.18,
        0.080, 0.120, 1.35, 2185, "mixed sedum roof field with low planted variation",
    ),
    StoryRecipe(
        "board_formed_concrete_story_v86", "concrete", (188, 185, 177), 0.22,
        0.055, 0.105, 1.20, 2286, "board-formed civic concrete with restrained lift and tie variation",
        "board_formed",
    ),
    StoryRecipe(
        "pale_civic_roof_story_v86", "roof_membrane", (218, 216, 209), 0.76,
        0.030, 0.075, 1.05, 2386, "pale weathered civic roof membrane",
    ),
)


def load_recipe_manifest(path: Path) -> tuple[StoryRecipe, ...]:
    """Load bounded campaign recipes without expanding the global recipe table."""
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    if payload.get("schema") != "surface-story-recipes@1":
        raise ValueError(f"unsupported recipe manifest schema: {payload.get('schema')!r}")
    recipes: list[StoryRecipe] = []
    seen: set[str] = set()
    for number, item in enumerate(payload.get("recipes") or [], 1):
        output_key = str(item.get("output_key") or "").strip()
        source_key = str(item.get("source_key") or "").strip()
        if not output_key or not source_key:
            raise ValueError(f"recipe {number} requires output_key and source_key")
        if output_key in seen:
            raise ValueError(f"duplicate external recipe output_key: {output_key}")
        seen.add(output_key)
        raw_tint = item.get("tint")
        if isinstance(raw_tint, str) and len(raw_tint) == 7 and raw_tint.startswith("#"):
            tint = tuple(int(raw_tint[index:index + 2], 16) for index in (1, 3, 5))
        elif isinstance(raw_tint, list) and len(raw_tint) == 3:
            tint = tuple(int(channel) for channel in raw_tint)
        else:
            raise ValueError(f"recipe {output_key} tint must be #RRGGBB or three channels")
        if any(channel < 0 or channel > 255 for channel in tint):
            raise ValueError(f"recipe {output_key} tint channels must be 0..255")
        recipes.append(StoryRecipe(
            output_key=output_key,
            source_key=source_key,
            tint=tint,
            tint_mix=float(item.get("tint_mix", 0.42)),
            macro_strength=float(item.get("macro_strength", 0.055)),
            roughness_strength=float(item.get("roughness_strength", 0.09)),
            normal_strength=float(item.get("normal_strength", 1.25)),
            seed=int(item.get("seed", 1)),
            role=str(item.get("role") or output_key),
            pattern=str(item.get("pattern") or "source"),
        ))
    return tuple(recipes)


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


def board_formed_maps(
    albedo: np.ndarray,
    roughness: np.ndarray,
    normal: np.ndarray,
    size: int,
    seed: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Replace generic panel joints with horizontal board-form construction cues."""
    rng = np.random.default_rng(seed)
    period = max(32, size // 16)
    # Remove the source's regular square-panel hierarchy while retaining broad
    # concrete mottling and a small amount of aggregate texture.
    blurred_albedo = np.asarray(
        Image.fromarray(np.clip(albedo, 0, 255).astype(np.uint8), "RGB").filter(
            ImageFilter.GaussianBlur(max(3.0, size / 128.0))
        ),
        dtype=np.float32,
    )
    albedo = blurred_albedo * 0.86 + albedo * 0.14
    blurred_roughness = np.asarray(
        Image.fromarray(np.clip(roughness, 0, 255).astype(np.uint8), "RGB").filter(
            ImageFilter.GaussianBlur(max(2.0, size / 192.0))
        ),
        dtype=np.float32,
    )
    roughness = blurred_roughness * 0.72 + roughness * 0.28

    height = np.zeros((size, size), dtype=np.float32)
    board_count = math.ceil(size / period)
    for board in range(board_count):
        y0 = board * period
        y1 = min(size, y0 + period)
        tone = float(rng.uniform(-0.035, 0.035))
        albedo[y0:y1] *= 1.0 + tone
        roughness[y0:y1] += tone * 95.0
        if y0 < size:
            rows = slice(y0, min(size, y0 + 2))
            albedo[rows] *= 0.76
            roughness[rows] += 24.0
            height[rows] -= 1.0
        if y0 + 2 < size:
            albedo[y0 + 2:min(size, y0 + 4)] *= 1.055
            height[y0 + 2:min(size, y0 + 4)] += 0.22
        # Sparse staggered shutter joints avoid reverting to a precast grid.
        if board % 4 == 1:
            joint = size // 2
            xs = slice(joint, min(size, joint + 2))
            albedo[y0:y1, xs] *= 0.88
            height[y0:y1, xs] -= 0.38

    nx = (normal[..., 0] / 127.5 - 1.0) * 0.24
    ny = (normal[..., 1] / 127.5 - 1.0) * 0.24
    grad_y, grad_x = np.gradient(height)
    nx -= grad_x * 2.8
    ny -= grad_y * 2.8
    length = np.maximum(1.0, np.sqrt(nx * nx + ny * ny + 1.0))
    encoded = np.empty_like(normal)
    encoded[..., 0] = (nx / length * 0.5 + 0.5) * 255.0
    encoded[..., 1] = (ny / length * 0.5 + 0.5) * 255.0
    encoded[..., 2] = (1.0 / length * 0.5 + 0.5) * 255.0
    return albedo, roughness, encoded


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
    roughness = load_rgb(required["roughness"], size)
    roughness += story[..., None] * (255.0 * recipe.roughness_strength)
    normal = load_rgb(required["normal"], size)
    if recipe.pattern == "board_formed":
        albedo, roughness, encoded = board_formed_maps(
            albedo, roughness, normal, size, recipe.seed
        )
    else:
        nx = (normal[..., 0] / 127.5 - 1.0) * recipe.normal_strength
        ny = (normal[..., 1] / 127.5 - 1.0) * recipe.normal_strength
        length = np.maximum(1.0, np.sqrt(nx * nx + ny * ny + 1.0))
        encoded = np.empty_like(normal)
        encoded[..., 0] = (nx / length * 0.5 + 0.5) * 255.0
        encoded[..., 1] = (ny / length * 0.5 + 0.5) * 255.0
        encoded[..., 2] = (1.0 / length * 0.5 + 0.5) * 255.0
    save_rgb(albedo, destination / "albedo.jpg")
    save_rgb(roughness, destination / "roughness.jpg")
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
    parser.add_argument("--recipe-manifest", type=Path, default=None)
    args = parser.parse_args()
    if args.size < 512:
        raise ValueError("surface-story textures must be at least 512 px")
    args.output_root.mkdir(parents=True, exist_ok=True)
    source_roots = [args.source_root, *args.additional_source_root]
    external = load_recipe_manifest(args.recipe_manifest) if args.recipe_manifest else ()
    duplicate_keys = {recipe.output_key for recipe in RECIPES} & {recipe.output_key for recipe in external}
    if duplicate_keys:
        raise ValueError("external recipes duplicate built-in keys: " + ", ".join(sorted(duplicate_keys)))
    materials = [
        derive(recipe, source_roots, args.output_root, args.size)
        for recipe in (*RECIPES, *external)
    ]
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
