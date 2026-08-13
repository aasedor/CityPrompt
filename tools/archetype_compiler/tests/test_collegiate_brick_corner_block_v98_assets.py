from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

import pytest
from PIL import Image, ImageStat


TOOL_DIR = Path(__file__).parents[1]
SCRIPT = TOOL_DIR / "prepare_collegiate_brick_corner_block_v98_assets.py"
SPEC = importlib.util.spec_from_file_location("collegiate_brick_assets_v98", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(MODULE)


def _snapshot() -> dict[str, str]:
    return {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(MODULE.OUT.iterdir())
            if p.is_file() and ".tmp" not in p.name}


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
        with Image.open(path) as image:
            assert image.mode == "RGB"
    for spec in prepared["palette_conditioning"]["crops_px"].values():
        path = MODULE.REPO / spec["path"]
        assert tuple(spec["box"]) == MODULE.assert_crop(path, tuple(spec["box"]))
    with pytest.raises(ValueError):
        MODULE.assert_crop(MODULE.STREET, (0, 0, 4096, 4096))


def test_assets_are_hash_bound_rgb_and_expected_dimensions(prepared: dict) -> None:
    assert len(prepared["assets"]) == 25
    atlases = {"residential_interiors", "corner_interiors", "ground_lobby_interiors"}
    for role, record in prepared["assets"].items():
        path = MODULE.REPO / record["path"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == record["sha256"]
        with Image.open(path) as image:
            assert image.mode == "RGB"
            assert image.size == ((2048, 1024) if role in atlases else (1024, 1024))


def test_all_assets_are_intrinsic_and_geometry_free(prepared: dict) -> None:
    for record in prepared["assets"].values():
        assert record["contains_printed_openings"] is False
        assert record["contains_printed_frames_or_mullions"] is False
        assert record["contains_printed_bands_or_pilasters"] is False
        assert record["contains_printed_reflection_or_horizon"] is False
        assert record["contains_baked_directional_lighting"] is False
        assert record["contains_text_or_logo"] is False
    assert "no printed opening" in prepared["brick_contract"]


def test_metric_brick_registration_palette_and_course_frequency(prepared: dict) -> None:
    front = Image.open(MODULE.OUT / "warm_tan_brick_front_intrinsic.png").convert("RGB")
    returned = Image.open(MODULE.OUT / "warm_tan_brick_return_intrinsic.png").convert("RGB")
    assert front.getpixel((137, 271)) == returned.getpixel((1023 - 137, 271))
    courtyard = Image.open(MODULE.OUT / "subdued_courtyard_brick_intrinsic.png").convert("RGB")
    assert sum(ImageStat.Stat(front).mean) / 3 > sum(ImageStat.Stat(courtyard).mean) / 3
    # A 28px material course is later bound to a 2.4m tile: 65.6mm/course.
    gray = front.convert("L")
    rows = [sum(gray.crop((0, y, 1024, y + 1)).getdata()) / 1024 for y in range(1024)]
    mortar_rows = [y for y, value in enumerate(rows) if value > 156]
    groups = sum(1 for i, y in enumerate(mortar_rows) if i == 0 or y > mortar_rows[i - 1] + 1)
    assert 34 <= groups <= 39


def test_glass_and_three_interior_atlases_are_separate(prepared: dict) -> None:
    assert prepared["atlas_grid"] == [4, 2]
    residential_glass = Image.open(MODULE.OUT / "physical_residential_glass_intrinsic.png").convert("RGB")
    corner_glass = Image.open(MODULE.OUT / "physical_corner_glass_intrinsic.png").convert("RGB")
    assert residential_glass.tobytes() != corner_glass.tobytes()
    assert min(ImageStat.Stat(residential_glass).mean) > 170
    atlases = [Image.open(MODULE.OUT / name).convert("RGB") for name in
               ("residential_interior_atlas.png", "corner_interior_atlas.png", "ground_lobby_interior_atlas.png")]
    assert len({hashlib.sha256(atlas.tobytes()).hexdigest() for atlas in atlases}) == 3
    for atlas in atlases:
        for row in range(2):
            for column in range(4):
                cell = atlas.crop((column * 512, row * 512, (column + 1) * 512, (row + 1) * 512))
                assert cell.size == (512, 512) and 50 < min(ImageStat.Stat(cell).mean) < 120


def test_required_roof_and_construction_roles_are_disjoint(prepared: dict) -> None:
    required = {
        "pale_precast", "weathered_base_plinth_reveal", "pale_coping_cornice", "dark_joint_sealant",
        "bronze_oriel_frames", "bronze_spandrel_casing", "bronze_mechanical_screen",
        "gravel_ballast_roof", "dark_inner_membrane", "membrane_service_path", "roof_perimeter_flashing",
        "aged_galvanized_hvac", "galvanized_duct_rails_vents", "rooflight_glass", "rooflight_curb",
        "threshold", "door_hardware",
    }
    assert required <= set(prepared["assets"])
    roof_paths = {prepared["assets"][role]["path"] for role in
                  ("gravel_ballast_roof", "dark_inner_membrane", "membrane_service_path")}
    assert len(roof_paths) == 3
    assert prepared["roof_contract"].startswith("Seamless light gravel, dark inner membrane and service path belong only")


def test_material_fields_have_readable_intrinsic_variation(prepared: dict) -> None:
    for name in ("warm_tan_brick_front_intrinsic.png", "pale_precast_intrinsic.png",
                 "gravel_ballast_roof_intrinsic.png", "dark_inner_membrane_intrinsic.png",
                 "bronze_mechanical_screen_intrinsic.png"):
        image = Image.open(MODULE.OUT / name).convert("RGB")
        stats = ImageStat.Stat(image)
        assert max(stats.rms) - min(stats.mean) > 2


def test_v2_roof_hierarchy_periodic_gravel_and_metal_character(prepared: dict) -> None:
    gravel = Image.open(MODULE.OUT / "gravel_ballast_roof_intrinsic.png").convert("RGB")
    membrane = Image.open(MODULE.OUT / "dark_inner_membrane_intrinsic.png").convert("RGB")
    path = Image.open(MODULE.OUT / "membrane_service_path_intrinsic.png").convert("RGB")
    assert gravel.crop((0, 0, 512, 512)).tobytes() == gravel.crop((512, 512, 1024, 1024)).tobytes()
    assert min(ImageStat.Stat(gravel).mean) > max(ImageStat.Stat(path).mean) + 25
    assert min(ImageStat.Stat(path).mean) > max(ImageStat.Stat(membrane).mean) + 8
    screen = Image.open(MODULE.OUT / "bronze_mechanical_screen_intrinsic.png").convert("L")
    columns = [sum(screen.crop((x, 0, x + 1, 1024)).getdata()) / 1024 for x in range(1024)]
    assert max(columns) - min(columns) > 5
    assert "no printed membrane seam" in prepared["roof_contract"]
