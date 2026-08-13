from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

import pytest
from PIL import Image, ImageStat


TOOL_DIR = Path(__file__).parents[1]
SCRIPT = TOOL_DIR / "prepare_industrial_tilt_up_concrete_v98_assets.py"
SPEC = importlib.util.spec_from_file_location("industrial_tilt_up_assets_v98", SCRIPT)
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


def test_exact_reference_hashes_modes_and_crop_bounds(prepared: dict) -> None:
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
    assert len(prepared["assets"]) == 26
    atlases = {"lobby_lower_office_interiors", "upper_office_interiors"}
    for role, record in prepared["assets"].items():
        path = MODULE.REPO / record["path"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == record["sha256"]
        with Image.open(path) as image:
            assert image.mode == "RGB"
            assert image.size == ((2048, 1024) if role in atlases else (1024, 1024))


def test_semantic_exclusions_and_concrete_ownership(prepared: dict) -> None:
    for record in prepared["assets"].values():
        assert record["contains_printed_structural_grid"] is False
        assert record["contains_printed_apertures"] is False
        assert record["contains_printed_mullions"] is False
        assert record["contains_printed_reflections_or_horizon"] is False
        assert record["contains_baked_directional_lighting"] is False
        assert record["contains_text_or_logo"] is False
    for role in ("warm_buff_concrete_front", "warm_buff_concrete_return", "cool_gray_side_rear_concrete",
                 "weathered_plinth_reveal_concrete"):
        assert prepared["assets"][role]["contains_printed_panel_joints"] is False
    assert "no printed panel grid" in prepared["concrete_contract"]


def test_registered_front_return_and_reference_compatible_palette(prepared: dict) -> None:
    front = Image.open(MODULE.OUT / "warm_buff_concrete_front_intrinsic.png").convert("RGB")
    returned = Image.open(MODULE.OUT / "warm_buff_concrete_return_intrinsic.png").convert("RGB")
    assert front.getpixel((137, 271)) == returned.getpixel((1023 - 137, 271))
    palette = prepared["palette_conditioning"]["prepared_palette_rgb"]
    warm, cool = palette["warm"], palette["cool"]
    assert sum(warm) / 3 > sum(cool) / 3
    assert warm[0] > warm[2] and max(cool) - min(cool) < 18
    cool_image = ImageStat.Stat(Image.open(MODULE.OUT / "cool_gray_side_rear_concrete_intrinsic.png").convert("RGB")).mean
    assert min(cool_image) > 145


def test_glass_and_two_interior_atlases_are_disjoint(prepared: dict) -> None:
    assert prepared["atlas_grid"] == [4, 2]
    glass = Image.open(MODULE.OUT / "physical_neutral_glass_intrinsic.png").convert("RGB")
    mean = ImageStat.Stat(glass).mean
    assert min(mean) > 155 and max(mean) - min(mean) < 28
    lower = Image.open(MODULE.OUT / "lobby_lower_office_interior_atlas.png").convert("RGB")
    upper = Image.open(MODULE.OUT / "upper_office_interior_atlas.png").convert("RGB")
    assert hashlib.sha256(lower.tobytes()).hexdigest() != hashlib.sha256(upper.tobytes()).hexdigest()
    for atlas in (lower, upper):
        for row in range(2):
            for column in range(4):
                assert atlas.crop((column * 512, row * 512, (column + 1) * 512,
                                   (row + 1) * 512)).size == (512, 512)


def test_required_construction_finish_roles_and_roof_disjointness(prepared: dict) -> None:
    required = {
        "dark_joint_sealant", "pale_coping_flashing", "charcoal_bronze_aluminum",
        "canopy_top", "canopy_fascia", "canopy_soffit_posts", "ribbed_overhead_doors",
        "dock_rubber_hardware", "galvanized_threshold", "personnel_doors", "safety_yellow_bollards",
        "off_white_tpo", "roof_perimeter_patch", "rooflight_glass", "rooflight_curb",
        "aged_galvanized_hvac_duct_vents", "service_grille", "blank_sign_plate", "openwork_shadow_backing",
    }
    assert required <= set(prepared["assets"])
    assert prepared["assets"]["off_white_tpo"]["path"] != prepared["assets"]["roof_perimeter_patch"]["path"]
    assert prepared["roof_contract"].startswith("Off-white TPO and perimeter patch belong only")


def test_material_v2_screen_glass_cards_doors_and_roof_readability(prepared: dict) -> None:
    fins=ImageStat.Stat(Image.open(MODULE.OUT/"charcoal_bronze_aluminum_intrinsic.png").convert("RGB")).mean
    backing=ImageStat.Stat(Image.open(MODULE.OUT/"openwork_shadow_backing_intrinsic.png").convert("RGB")).mean
    assert sum(fins)/3 > sum(backing)/3 + 4
    glass=ImageStat.Stat(Image.open(MODULE.OUT/"physical_neutral_glass_intrinsic.png").convert("RGB")).mean
    assert glass[2] > glass[0] + 8 and glass[1] > glass[0] + 5
    for name in ("lobby_lower_office_interior_atlas.png","upper_office_interior_atlas.png"):
        mean=ImageStat.Stat(Image.open(MODULE.OUT/name).convert("RGB")).mean
        assert max(mean) < 75
    door=Image.open(MODULE.OUT/"ribbed_overhead_doors_intrinsic.png").convert("RGB")
    assert ImageStat.Stat(door).rms[0] > 10
    roof=Image.open(MODULE.OUT/"off_white_tpo_intrinsic.png").convert("RGB")
    assert ImageStat.Stat(roof).rms[0] > 10


def test_material_v3_sectional_door_is_medium_gray_with_horizontal_metric_ribs(prepared: dict) -> None:
    door=Image.open(MODULE.OUT/"ribbed_overhead_doors_intrinsic.png").convert("RGB")
    mean=ImageStat.Stat(door).mean
    assert 115 < min(mean) < 150 and max(mean)-min(mean) < 10
    # Horizontal section edges create substantially more row-to-row than
    # column-to-column luma variation; this guards against smooth/vertical doors.
    gray=door.convert("L")
    row_means=[sum(gray.crop((0,y,1024,y+1)).getdata())/1024 for y in range(1024)]
    col_means=[sum(gray.crop((x,0,x+1,1024)).getdata())/1024 for x in range(1024)]
    row_span=max(row_means)-min(row_means); col_span=max(col_means)-min(col_means)
    assert row_span > 35 and row_span > col_span * 2.5
    # Count contiguous dark course bands. Difference-based edge counting is
    # intentionally avoided because each formed highlight has several slopes.
    dark_edges=[y for y,value in enumerate(row_means) if value < min(row_means) + 10]
    edge_bands=sum(1 for i,y in enumerate(dark_edges) if i == 0 or y > dark_edges[i-1] + 1)
    assert 8 <= edge_bands <= 16
