from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

import pytest
from PIL import Image, ImageFilter, ImageStat


TOOL_DIR = Path(__file__).parents[1]
SCRIPT = TOOL_DIR / "prepare_shophouse_peranakan_v98_assets.py"
SPEC = importlib.util.spec_from_file_location("shophouse_peranakan_assets_v98", SCRIPT)
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
        MODULE.assert_crop(MODULE.STREET, (0, 0, 9999, 9999))


def test_assets_hash_bound_rgb_dimensions_and_deterministic_contact_sheet(prepared: dict) -> None:
    assert len(prepared["assets"]) == 44
    atlas_roles = {"ground_shop_interiors", "upper_residential_interiors"}
    for role, record in prepared["assets"].items():
        path = MODULE.REPO / record["path"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == record["sha256"]
        with Image.open(path) as image:
            assert image.mode == "RGB"
            assert image.size == ((2048, 1024) if role in atlas_roles else (1024, 1024))
    contact = MODULE.REPO / prepared["contact_sheet"]["path"]
    assert prepared["contact_sheet"]["diagnostic_only"] is True
    assert hashlib.sha256(contact.read_bytes()).hexdigest() == prepared["contact_sheet"]["sha256"]


def test_all_assets_are_intrinsic_and_geometry_free(prepared: dict) -> None:
    for record in prepared["assets"].values():
        assert record["contains_printed_openings"] is False
        assert record["contains_printed_pilasters_or_arches"] is False
        assert record["contains_printed_rails_or_mullions"] is False
        assert record["contains_baked_directional_lighting"] is False
        assert record["contains_printed_reflection_horizon"] is False
    assert "five-foot-way cavern" in prepared["geometry_ownership"]


def test_six_pastel_families_have_front_return_rear_and_are_distinct(prepared: dict) -> None:
    means = {}
    for name in MODULE.PASTELS:
        roles = [f"plaster_{name}_{suffix}" for suffix in ("front", "return", "rear")]
        assert set(roles) <= set(prepared["assets"])
        means[name] = ImageStat.Stat(Image.open(MODULE.OUT / f"plaster_{name}_front_intrinsic.png").convert("RGB")).mean
        front = hashlib.sha256((MODULE.OUT / f"plaster_{name}_front_intrinsic.png").read_bytes()).hexdigest()
        returned = hashlib.sha256((MODULE.OUT / f"plaster_{name}_return_intrinsic.png").read_bytes()).hexdigest()
        rear = hashlib.sha256((MODULE.OUT / f"plaster_{name}_rear_intrinsic.png").read_bytes()).hexdigest()
        assert len({front, returned, rear}) == 3
    rounded = {tuple(round(c) for c in mean) for mean in means.values()}
    assert len(rounded) == 6


def test_tile_glass_and_interior_semantics(prepared: dict) -> None:
    assert prepared["atlas_grid"] == [4, 2]
    assert prepared["tile_contract"].startswith("Six deterministic whole-unit ceramic dado families")
    glass = ImageStat.Stat(Image.open(MODULE.OUT / "physical_clear_glass_intrinsic.png").convert("RGB")).mean
    assert min(glass) > 195 and max(glass) - min(glass) < 25
    for filename in ("ground_shop_interior_atlas.png", "upper_residential_interior_atlas.png"):
        with Image.open(MODULE.OUT / filename) as image:
            assert image.size == (2048, 1024)
            for row in range(2):
                for col in range(4):
                    assert image.crop((col*512, row*512, (col+1)*512, (row+1)*512)).size == (512, 512)
    shop = (MODULE.OUT / "ground_shop_interior_atlas.png").read_bytes()
    home = (MODULE.OUT / "upper_residential_interior_atlas.png").read_bytes()
    assert hashlib.sha256(shop).hexdigest() != hashlib.sha256(home).hexdigest()


def test_roof_and_construction_roles_are_disjoint(prepared: dict) -> None:
    roles = {"terracotta_roof_field", "terracotta_ridge_cap", "party_wall_plaster", "party_wall_coping",
             "roof_flashing", "gutter_downpipe", "painted_fretwork_fascia", "wrought_iron",
             "balcony_plaster", "arcade_soffit_reveal", "rear_service_finish", "threshold_hardware",
             "pale_trim_relief", "fine_ornament", "ceramic_dado", "walkway_tile", "carved_dark_timber"}
    assert roles <= set(prepared["assets"])
    assert len({prepared["assets"][role]["path"] for role in roles}) == len(roles)
    assert prepared["post_generation_nonuniform_scale_allowed"] is False


def test_material_v2_roof_frequency_plaster_chalk_glass_and_motif_scale(prepared: dict) -> None:
    roof = Image.open(MODULE.OUT / "terracotta_roof_field_intrinsic.png").convert("RGB")
    # Five strong course transitions in one repeat correspond to 0.20m at the
    # compiler's declared 1.0m repeat; require visible intrinsic relief.
    samples = [ImageStat.Stat(roof.crop((0, y, 1024, min(y + 18, 1024)))).mean[0] for y in range(0, 1000, 40)]
    assert max(samples) - min(samples) > 28
    assert roof.getbbox() == (0, 0, 1024, 1024)
    glass = ImageStat.Stat(Image.open(MODULE.OUT / "physical_clear_glass_intrinsic.png").convert("RGB")).mean
    assert min(glass) > 215 and max(glass) - min(glass) < 22
    front = ImageStat.Stat(Image.open(MODULE.OUT / "plaster_coral_front_intrinsic.png").convert("RGB")).mean
    rear = ImageStat.Stat(Image.open(MODULE.OUT / "plaster_coral_rear_intrinsic.png").convert("RGB")).mean
    assert max(front) - min(front) < 115 and tuple(round(v) for v in front) != tuple(round(v) for v in rear)
    ornament = ImageStat.Stat(Image.open(MODULE.OUT / "fine_ornament_intrinsic.png").convert("RGB"))
    assert max(ornament.extrema[i][1] - ornament.extrema[i][0] for i in range(3)) > 35


def test_material_v3_barrel_pan_relief_dense_ornament_and_quiet_plaster(prepared: dict) -> None:
    roof = Image.open(MODULE.OUT / "terracotta_roof_field_intrinsic.png").convert("RGB")
    # Adjacent barrel/pan modules must have different transverse profiles while
    # retaining the exact five-course 0.20m contract.
    # Sample a complete non-clipped course; the first negative-origin course is
    # intentionally clipped at the seamless texture boundary.
    a = ImageStat.Stat(roof.crop((10, 230, 118, 385))).mean
    b = ImageStat.Stat(roof.crop((138, 230, 246, 385))).mean
    assert sum(abs(x-y) for x, y in zip(a, b)) > 5
    ornament = Image.open(MODULE.OUT / "fine_ornament_intrinsic.png").convert("RGB")
    detail = ornament.filter(ImageFilter.FIND_EDGES)
    assert sum(ImageStat.Stat(detail).mean) > 17
    plaster = Image.open(MODULE.OUT / "plaster_turquoise_front_intrinsic.png").convert("RGB")
    # Broad limewash remains, but high-frequency procedural freckle is restrained.
    assert sum(ImageStat.Stat(plaster.filter(ImageFilter.FIND_EDGES)).mean) < 10


def test_six_whole_unit_ceramic_panel_families_are_distinct_and_intrinsic(prepared: dict) -> None:
    roles = [f"ceramic_dado_family_{i}" for i in range(6)]
    assert prepared["ceramic_panel_families"] == roles
    hashes = []
    signatures = []
    for role in roles:
        record = prepared["assets"][role]; path = MODULE.REPO / record["path"]
        hashes.append(hashlib.sha256(path.read_bytes()).hexdigest())
        image = Image.open(path).convert("RGB")
        # Coarse spatial signature distinguishes floral, scroll, lotus, vine,
        # medallion and pendant families—not mere phase-shifted diamonds.
        thumb = image.resize((16,16), Image.Resampling.BOX)
        signatures.append(thumb.tobytes())
        assert image.size == (1024,1024) and record["contains_printed_openings"] is False
    assert len(set(hashes)) == 6 and len(set(signatures)) == 6
