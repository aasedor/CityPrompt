import hashlib
import importlib.util
import json
from pathlib import Path

from PIL import Image, ImageStat


TOOL_DIR = Path(__file__).parents[1]
ROOT = TOOL_DIR.parents[1]
PATH = TOOL_DIR / "prepare_market_historic_iron_glass_v98_assets.py"
SPEC = importlib.util.spec_from_file_location("market_historic_assets_v98", PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(MODULE)


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _mean(name: str) -> tuple[float, float, float]:
    with Image.open(MODULE.OUT / name) as image:
        return tuple(ImageStat.Stat(image.resize((32, 32))).mean)


def test_asset_preparation_is_byte_deterministic():
    MODULE.main()
    first = {path.name: _hash(path) for path in MODULE.OUT.iterdir() if path.is_file()}
    MODULE.main()
    second = {path.name: _hash(path) for path in MODULE.OUT.iterdir() if path.is_file()}
    assert first == second


def test_exact_reference_hashes_dimensions_and_crop_bounds():
    for relative, record in MODULE.REFERENCES.items():
        path = ROOT / relative
        assert _hash(path) == record["sha256"]
        with Image.open(path) as image:
            assert list(image.size) == record["size"]
        x0, y0, x1, y1 = record["conditioning_crop_bounds_px"]
        assert 0 <= x0 < x1 <= record["size"][0]
        assert 0 <= y0 < y1 <= record["size"][1]


def test_assets_are_rgb_intrinsic_and_registered():
    provenance = json.loads((MODULE.OUT / "provenance.json").read_text(encoding="utf-8"))
    assert provenance["canonical_dimensions_m"] == {"length": 60.0, "width": 45.0}
    assert provenance["metric_contract"]["continuous_resize_allowed"] is False
    assert len(provenance["assets"]) == 25
    required = set(MODULE.EXCLUSIONS)
    for record in provenance["assets"].values():
        path = ROOT / record["path"]
        assert _hash(path) == record["sha256"]
        with Image.open(path) as image:
            assert image.mode == "RGB"
            assert list(image.size) == record["size"]
        assert required <= set(record["semantic_exclusions"])


def test_registered_brick_courses_share_metric_phase():
    names = (
        "warm_brick_front_intrinsic.png",
        "warm_brick_return_intrinsic.png",
        "warm_brick_rear_intrinsic.png",
    )
    for name in names:
        with Image.open(MODULE.OUT / name) as image:
            assert image.size == (1024, 1024)
            gray = image.convert("L")
            row_means = [ImageStat.Stat(gray.crop((0, y, 1024, y + 2))).mean[0] for y in range(0, 1024, 32)]
            adjacent = [ImageStat.Stat(gray.crop((0, min(y + 5, 1022), 1024, min(y + 7, 1024)))).mean[0]
                        for y in range(0, 1024, 32)]
            assert sum(a - b for a, b in zip(row_means, adjacent)) / len(row_means) > 10


def test_iron_is_green_and_ornate_finish_is_subordinate():
    cast = _mean("heritage_green_cast_iron_intrinsic.png")
    rail = _mean("dark_ornate_rail_intrinsic.png")
    assert cast[1] > cast[0] + 25 and cast[1] > cast[2] + 12
    assert sum(rail) < sum(cast)
    assert 85 < cast[1] < 105


def test_glass_assets_are_separate_neutral_and_without_hard_grids():
    names = (
        "physical_vertical_low_iron_glass_intrinsic.png",
        "physical_curved_roof_glass_intrinsic.png",
        "ridge_lantern_glass_intrinsic.png",
        "rooflight_glass_intrinsic.png",
    )
    assert len({_hash(MODULE.OUT / name) for name in names}) == 4
    for name in names:
        with Image.open(MODULE.OUT / name) as image:
            gray = image.convert("L").resize((128, 128))
            pixels = gray.load()
            row = [sum(pixels[x, y] for x in range(128)) / 128 for y in range(128)]
            col = [sum(pixels[x, y] for y in range(128)) / 128 for x in range(128)]
            assert max(abs(row[i] - row[i - 1]) for i in range(1, 128)) < 3
            assert max(abs(col[i] - col[i - 1]) for i in range(1, 128)) < 3


def test_interior_atlases_are_exact_four_by_two_and_nonrepeating():
    for name in ("ground_market_interior_atlas.png", "gallery_market_interior_atlas.png"):
        with Image.open(MODULE.OUT / name) as image:
            assert image.size == (2048, 1024)
            cells = []
            for row in range(2):
                for col in range(4):
                    cell = image.crop((col * 512, row * 512, (col + 1) * 512, (row + 1) * 512))
                    cells.append(tuple(round(value, 2) for value in ImageStat.Stat(cell.resize((16, 16))).mean))
            assert len(set(cells)) == 8
    assert _hash(MODULE.OUT / "ground_market_interior_atlas.png") != _hash(MODULE.OUT / "gallery_market_interior_atlas.png")
    ground = _mean("ground_market_interior_atlas.png")
    gallery = _mean("gallery_market_interior_atlas.png")
    assert sum(ground) > sum(gallery) + 25
    assert 235 < sum(gallery) < 255 and 270 < sum(ground) < 290


def test_signboard_is_blank_and_cavern_is_subordinate():
    with Image.open(MODULE.OUT / "blank_dark_signboard_intrinsic.png") as image:
        assert max(ImageStat.Stat(image).stddev) < 3
    cavern = _mean("dark_cavern_backing_intrinsic.png")
    ground = _mean("ground_market_interior_atlas.png")
    assert sum(cavern) < sum(ground)


def test_roof_materials_remain_semantically_distinct():
    slate = _mean("weathered_slate_intrinsic.png")
    zinc = _mean("aged_zinc_roof_intrinsic.png")
    roof_glass = _mean("physical_curved_roof_glass_intrinsic.png")
    assert sum(zinc) - sum(slate) > 220
    assert roof_glass[1] >= roof_glass[0]
    assert sum(roof_glass) > 480
    assert len({
        _hash(MODULE.OUT / "weathered_slate_intrinsic.png"),
        _hash(MODULE.OUT / "aged_zinc_roof_intrinsic.png"),
        _hash(MODULE.OUT / "flashing_coping_intrinsic.png"),
    }) == 3
    with Image.open(MODULE.OUT / "weathered_slate_intrinsic.png") as image:
        assert min(ImageStat.Stat(image.resize((64, 64))).stddev) > 4
    with Image.open(MODULE.OUT / "aged_zinc_roof_intrinsic.png") as image:
        assert min(ImageStat.Stat(image.resize((64, 64))).stddev) > 3


def test_rooflight_glass_and_coping_are_separate_intrinsic_finishes():
    rooflight = MODULE.OUT / "rooflight_glass_intrinsic.png"
    lantern = MODULE.OUT / "ridge_lantern_glass_intrinsic.png"
    coping = MODULE.OUT / "flashing_coping_intrinsic.png"
    assert len({_hash(rooflight), _hash(lantern), _hash(coping)}) == 3
    assert sum(_mean("flashing_coping_intrinsic.png")) > 465


def test_warm_stone_and_registered_brick_have_reference_conditioned_finish():
    ashlar = _mean("pale_ashlar_intrinsic.png")
    plinth = _mean("weathered_stone_plinth_intrinsic.png")
    front = _mean("warm_brick_front_intrinsic.png")
    rear = _mean("warm_brick_rear_intrinsic.png")
    assert ashlar[0] > ashlar[2] + 20 and plinth[0] > plinth[2] + 18
    assert sum(ashlar) > sum(plinth) + 70
    assert front[0] > front[1] * 1.6 and rear[0] > rear[1] * 1.6
