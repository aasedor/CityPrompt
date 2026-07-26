"""Build deterministic PBR texture sets for the concert-hall skin pilot.

The source atlases are intentionally retained beside this script's inputs so
the render-locked material treatment can be reproduced without another image
generation call. Glass stays optically smooth; brick and roof retain restrained
height detail for grazing-light realism.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

from upgrade_facade_pbr import delight_image, derive_normal


ROOT = Path(__file__).resolve().parent
DEFAULT_SOURCE = ROOT / "facade_sources_openai_concert_v1"
DEFAULT_OUTPUT = ROOT / "textures"


def _save_texture_set(
    source: Image.Image,
    output: Path,
    *,
    surface: str,
) -> None:
    output.mkdir(parents=True, exist_ok=True)
    source = source.convert("RGB")
    source.save(output / "raw.jpg", quality=95, subsampling=0)

    if surface == "glass":
        albedo = source
        grey = np.asarray(source.convert("L"), dtype=np.float32) / 255.0
        broad = np.asarray(
            source.convert("L").filter(ImageFilter.GaussianBlur(max(8.0, source.width / 90))),
            dtype=np.float32,
        ) / 255.0
        roughness_values = np.clip(0.105 + (grey - broad) * 0.09, 0.075, 0.18)
        roughness = Image.fromarray(np.uint8(roughness_values * 255), mode="L")
        normal = Image.new("RGB", source.size, (128, 128, 255))
    elif surface == "roof":
        albedo = delight_image(source, strength=0.28)
        grey = np.asarray(albedo.convert("L"), dtype=np.float32) / 255.0
        broad = np.asarray(
            albedo.convert("L").filter(ImageFilter.GaussianBlur(max(3.0, source.width / 360))),
            dtype=np.float32,
        ) / 255.0
        height = np.clip(0.53 + (grey - broad) * 0.48, 0.32, 0.74)
        normal = derive_normal(height, strength=4.2)
        edge = np.asarray(albedo.convert("L").filter(ImageFilter.FIND_EDGES), dtype=np.float32) / 255.0
        roughness_values = np.clip(0.27 + edge * 0.24 + (1.0 - grey) * 0.08, 0.22, 0.58)
        roughness = Image.fromarray(np.uint8(roughness_values * 255), mode="L")
    else:
        albedo = delight_image(source, strength=0.42)
        grey = np.asarray(albedo.convert("L"), dtype=np.float32) / 255.0
        broad = np.asarray(
            albedo.convert("L").filter(ImageFilter.GaussianBlur(max(3.0, source.width / 360))),
            dtype=np.float32,
        ) / 255.0
        height = np.clip(0.52 + (grey - broad) * 0.62, 0.20, 0.82)
        normal = derive_normal(height, strength=5.6)
        edge = np.asarray(albedo.convert("L").filter(ImageFilter.FIND_EDGES), dtype=np.float32) / 255.0
        dark = 1.0 - grey
        roughness_values = np.clip(0.66 + edge * 0.18 + dark * 0.10, 0.48, 0.94)
        roughness = Image.fromarray(np.uint8(roughness_values * 255), mode="L")

    albedo.save(output / "albedo.jpg", quality=95, subsampling=0)
    normal.save(output / "normal.png", compress_level=7)
    roughness.save(output / "roughness.jpg", quality=95, subsampling=0)


def build(source_root: Path, output_root: Path) -> None:
    jobs = (
        ("crystalline-glass-elevation-v1.png", "concert_crystalline_glass", "glass"),
        ("warehouse-brick-elevation-v1.png", "concert_warehouse_brick", "brick"),
        ("tensile-roof-tiles-v1.png", "concert_tensile_roof", "roof"),
    )
    for filename, texture_key, surface in jobs:
        source_path = source_root / filename
        if not source_path.exists():
            raise FileNotFoundError(source_path)
        with Image.open(source_path) as image:
            _save_texture_set(image, output_root / texture_key, surface=surface)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    build(args.source.resolve(), args.output.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
