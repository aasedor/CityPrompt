from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

import pytest
from PIL import Image, ImageStat


TOOL_DIR = Path(__file__).parents[1]
SCRIPT = TOOL_DIR / "prepare_civic_modernism_rec_centre_v98_assets.py"
SPEC = importlib.util.spec_from_file_location("rec_centre_assets_v98", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(MODULE)


def _snapshot() -> dict[str, str]:
    return {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in sorted(MODULE.OUT.iterdir())
            if path.is_file() and ".tmp" not in path.name}


@pytest.fixture(scope="module")
def prepared() -> dict:
    MODULE.main(); first = _snapshot(); MODULE.main(); second = _snapshot()
    assert first == second
    return json.loads((MODULE.OUT / "provenance.json").read_text(encoding="utf-8"))


def test_exact_reference_hashes_and_crop_bounds(prepared: dict) -> None:
    assert prepared["identity_authority"] == "three_exact_variant_0_images"
    assert len(prepared["exact_reference_sources"]) == 3
    for path, digest in MODULE.EXPECTED_REFERENCE_HASHES.items():
        assert MODULE._hash(path) == digest
    for spec in prepared["palette_conditioning"]["crops_px"].values():
        path = MODULE.REPO / spec["path"]
        assert tuple(spec["box"]) == MODULE.assert_crop(path, tuple(spec["box"]))
    with pytest.raises(ValueError):
        MODULE.assert_crop(MODULE.STREET, (0, 0, 4096, 4096))


def test_assets_are_hash_bound_rgb_and_expected_dimensions(prepared: dict) -> None:
    assert len(prepared["assets"]) == 20
    atlases = {"pool_hall_interiors", "community_lobby_interiors"}
    for role, record in prepared["assets"].items():
        path = MODULE.REPO / record["path"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == record["sha256"]
        with Image.open(path) as image:
            assert image.mode == "RGB"
            assert image.size == ((2048, 1024) if role in atlases else (1024, 1024))


def test_all_assets_record_semantic_exclusions(prepared: dict) -> None:
    for record in prepared["assets"].values():
        assert record["contains_printed_structural_grid"] is False
        assert record["contains_printed_mullions"] is False
        assert record["contains_printed_reflections_or_horizon"] is False
        assert record["contains_baked_directional_lighting"] is False
        assert record["contains_printed_apertures"] is False
    assert prepared["glass_contract"].startswith("Intrinsic neutral optical field only")


def test_registered_brick_and_disjoint_roof_assets(prepared: dict) -> None:
    front = Image.open(MODULE.OUT / "warm_brick_front_intrinsic.png").convert("RGB")
    returned = Image.open(MODULE.OUT / "warm_brick_return_intrinsic.png").convert("RGB")
    assert front.getpixel((137, 271)) == returned.getpixel((1023 - 137, 271))
    assert prepared["roof_contract"].startswith("Low deck, high deck and perimeter patch are disjoint")
    roof_paths = {prepared["assets"][role]["path"] for role in
                  ("low_roof_membrane", "high_roof_membrane", "roof_perimeter_patch")}
    assert len(roof_paths) == 3


def test_glass_and_interior_atlases_are_separate_and_neutral(prepared: dict) -> None:
    assert prepared["atlas_grid"] == [4, 2]
    assert prepared["assets"]["physical_clear_glass"]["path"] != prepared["assets"]["pool_hall_interiors"]["path"]
    assert prepared["assets"]["physical_clear_glass"]["path"] != prepared["assets"]["community_lobby_interiors"]["path"]
    glass_mean = ImageStat.Stat(Image.open(MODULE.OUT / "physical_clear_glass_intrinsic.png").convert("RGB")).mean
    assert min(glass_mean) > 190 and max(glass_mean) - min(glass_mean) < 12
    for name in ("pool_hall_interior_atlas.png", "community_lobby_interior_atlas.png"):
        with Image.open(MODULE.OUT / name) as image:
            assert image.size == (2048, 1024)
            # Exact quarter-by-half cells, with no padding or separator bars.
            for row in range(2):
                for column in range(4):
                    assert image.crop((column * 512, row * 512, (column + 1) * 512, (row + 1) * 512)).size == (512, 512)


def test_optical_v3_cards_are_visible_but_subordinate_and_semantically_separate(prepared: dict) -> None:
    pool = Image.open(MODULE.OUT / "pool_hall_interior_atlas.png").convert("RGB")
    lobby = Image.open(MODULE.OUT / "community_lobby_interior_atlas.png").convert("RGB")
    pool_mean = ImageStat.Stat(pool).mean; lobby_mean = ImageStat.Stat(lobby).mean
    assert min(pool_mean) > 65 and min(lobby_mean) > 65
    assert max(pool_mean) < 135 and max(lobby_mean) < 135
    # Pool cards retain a cyan/blue identity; lobby cards are warmer.
    assert pool_mean[2] > pool_mean[0] + 10 and pool_mean[1] > pool_mean[0] + 7
    assert lobby_mean[0] > lobby_mean[2] + 7
    assert hashlib.sha256(pool.tobytes()).hexdigest() != hashlib.sha256(lobby.tobytes()).hexdigest()


def test_palette_is_reference_compatible_and_finish_roles_exist(prepared: dict) -> None:
    palette = prepared["palette_conditioning"]["prepared_palette_rgb"]
    brick, concrete = palette["brick"], palette["concrete"]
    assert brick[0] > brick[1] > brick[2]
    assert max(concrete) - min(concrete) <= 10 and 145 < min(concrete) < 175
    required = {"ribbed_canopy_top", "smooth_canopy_fascia_soffit_posts", "dark_aluminum_joinery",
                "warm_entry_door_finish", "entry_threshold", "aged_galvanized_hvac_service",
                "dark_service_grille", "skylight_glass", "skylight_curb", "pale_concrete_coping"}
    assert required <= set(prepared["assets"])
