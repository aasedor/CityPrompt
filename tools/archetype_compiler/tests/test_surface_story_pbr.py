"""Tests for deterministic, export-safe surface-story texture baking."""
from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image


def _write_source(root: Path, key: str, size: int = 64) -> None:
    destination = root / key
    destination.mkdir(parents=True)
    x = np.linspace(0, 1, size, dtype=np.float32)[None, :, None]
    y = np.linspace(0, 1, size, dtype=np.float32)[:, None, None]
    albedo = np.broadcast_to(120 + 35 * x + 15 * y, (size, size, 3))
    roughness = np.broadcast_to(150 + 20 * y, (size, size, 3))
    normal = np.zeros((size, size, 3), dtype=np.uint8)
    normal[..., 0] = np.clip(127 + 8 * np.sin(x[..., 0] * np.pi * 4), 0, 255)
    normal[..., 1] = np.clip(127 + 8 * np.sin(y[..., 0] * np.pi * 3), 0, 255)
    normal[..., 2] = 255
    Image.fromarray(albedo.astype(np.uint8), "RGB").save(destination / "albedo.jpg")
    Image.fromarray(roughness.astype(np.uint8), "RGB").save(destination / "roughness.jpg")
    Image.fromarray(normal, "RGB").save(destination / "normal.png")


def test_surface_story_bake_is_deterministic_and_writes_three_pbr_channels(tmp_path):
    from derive_surface_story_pbr import RECIPES, derive

    recipe = RECIPES[0]
    source_root = tmp_path / "source"
    _write_source(source_root, recipe.source_key)
    first = derive(recipe, source_root, tmp_path / "first", 64)
    second = derive(recipe, source_root, tmp_path / "second", 64)

    assert first == second
    assert first["baked_pbr"] is True
    assert set(first["channels"]) == {"albedo", "roughness", "normal"}
    for filename in ("albedo.jpg", "roughness.jpg", "normal.png"):
        assert (tmp_path / "first" / recipe.output_key / filename).read_bytes() == (
            tmp_path / "second" / recipe.output_key / filename
        ).read_bytes()
    assert first["statistics"]["albedo_std"] > 1.0
    assert first["statistics"]["roughness_std"] > 1.0
    assert first["statistics"]["normal_xy_std"] > 1.0
