from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

import pytest
from PIL import Image, ImageStat


TOOL_DIR = Path(__file__).parents[1]
SCRIPT = TOOL_DIR / "prepare_halifax_waterfront_warehouse_v98_assets.py"
SPEC = importlib.util.spec_from_file_location("halifax_assets_v98", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(MODULE)


def _snapshot() -> dict[str, str]:
    return {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in sorted(MODULE.OUT.iterdir())
            if path.is_file() and not path.name.endswith(".tmp.png")}


@pytest.fixture(scope="module")
def prepared() -> dict:
    MODULE.main(); first = _snapshot(); MODULE.main(); second = _snapshot()
    assert first == second
    return json.loads((MODULE.OUT / "provenance.json").read_text(encoding="utf-8"))


def test_exact_reference_hashes_and_path_a_override(prepared: dict) -> None:
    assert prepared["identity_override"]["authority"] == "exact_image_locked_two_storey_italianate"
    assert len(prepared["exact_reference_sources"]) == 3
    for path, digest in MODULE.EXPECTED_REFERENCE_HASHES.items():
        assert MODULE._hash(path) == digest


def test_palette_crops_are_strictly_in_bounds(prepared: dict) -> None:
    for spec in prepared["palette_conditioning"]["crops_px"].values():
        path = MODULE.REPO / spec["path"]
        assert tuple(spec["box"]) == MODULE.assert_crop(path, tuple(spec["box"]))
    with pytest.raises(ValueError):
        MODULE.assert_crop(MODULE.STREET, (-1, 0, 10, 10))


def test_assets_are_rgb_expected_dimensions_and_hash_bound(prepared: dict) -> None:
    assert len(prepared["assets"]) == 16
    atlases = {"ground_retail_interiors", "upper_commercial_interiors"}
    for role, record in prepared["assets"].items():
        path = MODULE.REPO / record["path"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == record["sha256"]
        with Image.open(path) as image:
            assert image.mode == "RGB"
            assert image.size == ((2048, 1024) if role in atlases else (1024, 1024))
        assert record["contains_printed_modeled_geometry"] is False
        assert record["contains_baked_directional_lighting"] is False


def test_front_and_return_match_and_glass_interiors_stay_separate(prepared: dict) -> None:
    assert prepared["atlas_grid"] == [4, 2]
    assert prepared["glass_contract"].startswith("No printed mullions")
    front = MODULE.OUT / "warm_brick_front_intrinsic.png"
    returned = MODULE.OUT / "warm_brick_return_intrinsic.png"
    with Image.open(front) as a, Image.open(returned) as b:
        assert a.getpixel((117, 241)) == b.getpixel((1023 - 117, 241))
    assert prepared["assets"]["clear_upper_glass"]["path"] != prepared["assets"]["upper_commercial_interiors"]["path"]
    assert prepared["assets"]["clear_storefront_glass"]["path"] != prepared["assets"]["ground_retail_interiors"]["path"]


def test_material_v2_palette_and_quiet_interiors(prepared: dict) -> None:
    palette = prepared["palette_conditioning"]["prepared_palette_rgb"]
    brick, stone, patina, joinery = (palette[key] for key in ("brick", "stone", "patina", "green"))
    assert brick[0] > brick[1] > brick[2] and brick[1] <= 120
    assert max(stone) - min(stone) <= 12
    assert patina[1] >= 125 and patina[2] >= 120
    assert sum(patina) / 3 > sum(joinery) / 3 + 45
    assert "no tan stripes" in prepared["interior_contract"]
    for name in ("ground_retail_interior_atlas.png", "upper_commercial_interior_atlas.png"):
        with Image.open(MODULE.OUT / name) as image:
            mean = ImageStat.Stat(image.convert("RGB")).mean
        assert max(mean) < 65
        assert max(mean) - min(mean) < 8


def test_stone_variation_is_channel_correlated_and_glass_is_neutral_bright(prepared: dict) -> None:
    stone = Image.open(MODULE.OUT / "pale_warm_stone_intrinsic.png").convert("RGB")
    samples = list(stone.get_flattened_data())
    # Neutral luma variation preserves stable channel differences instead of
    # the independent RGB bands that appeared iridescent in Cycles v5.
    rg = {red - green for red, green, _blue in samples[::257]}
    gb = {green - blue for _red, green, blue in samples[::257]}
    assert len(rg) <= 3 and len(gb) <= 3
    for name in ("clear_upper_glass_intrinsic.png", "clear_storefront_glass_intrinsic.png"):
        mean = ImageStat.Stat(Image.open(MODULE.OUT / name).convert("RGB")).mean
        assert min(mean) > 105
        assert max(mean) - min(mean) < 18
