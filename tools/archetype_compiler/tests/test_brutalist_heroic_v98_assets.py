import hashlib
import importlib.util
import json
from pathlib import Path

from PIL import Image

TOOL_DIR = Path(__file__).parents[1]
ROOT = TOOL_DIR.parents[1]
PATH = TOOL_DIR / "prepare_brutalist_heroic_v98_assets.py"
SPEC = importlib.util.spec_from_file_location("brutalist_assets_v98", PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(MODULE)


def _hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_asset_preparation_is_byte_deterministic():
    MODULE.main()
    first = {path.name: _hash(path) for path in MODULE.OUT.iterdir() if path.is_file()}
    MODULE.main()
    second = {path.name: _hash(path) for path in MODULE.OUT.iterdir() if path.is_file()}
    assert first == second


def test_reference_hashes_are_exact():
    for relative, expected in MODULE.REFERENCES.items():
        assert _hash(ROOT / relative) == expected


def test_assets_are_registered_rgb_and_semantically_intrinsic():
    provenance = json.loads((MODULE.OUT / "provenance.json").read_text(encoding="utf-8"))
    assert provenance["metric_concrete_tile_m"] == 2.0
    assert len(provenance["assets"]) == 13
    for name, record in provenance["assets"].items():
        path = ROOT / record["path"]
        assert _hash(path) == record["sha256"]
        with Image.open(path) as image:
            assert image.mode == "RGB"
            assert list(image.size) == record["size"]
        exclusions = set(record["semantic_exclusions"])
        assert {"printed openings", "printed frames", "printed panel joints", "directional lighting", "reflection horizon", "text"} <= exclusions


def test_atlases_are_exact_four_by_two_and_distinct():
    ground = MODULE.OUT / "ground_public_interior_atlas.png"
    upper = MODULE.OUT / "upper_institutional_interior_atlas.png"
    with Image.open(ground) as image:
        assert image.size == (2048, 1024)
    with Image.open(upper) as image:
        assert image.size == (2048, 1024)
    assert _hash(ground) != _hash(upper)


def test_material_hierarchy_is_readable():
    def mean(name):
        with Image.open(MODULE.OUT / name) as image:
            pixels = list(image.resize((32, 32)).getdata())
        return sum(sum(pixel) / 3 for pixel in pixels) / len(pixels)
    assert mean("boardformed_concrete_front_intrinsic.png") > mean("deep_concrete_reveal_intrinsic.png")
    assert mean("physical_neutral_glass_intrinsic.png") > mean("dark_bronze_joinery_intrinsic.png")
    assert mean("roof_membrane_intrinsic.png") > mean("sunken_roof_court_intrinsic.png")


def test_board_form_is_directional_and_not_isotropic_sand():
    with Image.open(MODULE.OUT / "boardformed_concrete_front_intrinsic.png") as image:
        gray = image.convert("L").resize((256, 256))
        pixels = gray.load()
        horizontal_change = sum(abs(pixels[x + 1, y] - pixels[x, y]) for y in range(256) for x in range(255))
        vertical_change = sum(abs(pixels[x, y + 1] - pixels[x, y]) for y in range(255) for x in range(256))
    assert horizontal_change > vertical_change * 1.18


def test_board_form_has_no_square_or_edge_tile_cadence():
    with Image.open(MODULE.OUT / "boardformed_concrete_front_intrinsic.png") as image:
        gray = image.convert("L").resize((256, 256))
        pixels = gray.load()

        def column_jump(x):
            return sum(abs(pixels[x, y] - pixels[x - 1, y]) for y in range(256)) / 256

        def row_jump(y):
            return sum(abs(pixels[x, y] - pixels[x, y - 1]) for x in range(256)) / 256

        column_jumps = [column_jump(x) for x in range(1, 256)]
        row_jumps = [row_jump(y) for y in range(1, 256)]
        typical_column = sorted(column_jumps)[len(column_jumps) // 2]
        typical_row = sorted(row_jumps)[len(row_jumps) // 2]
        # The wrapped texture edges and quarter-cell positions may not become
        # the strongest transitions; that was the visible 2m checker symptom.
        assert max(column_jumps[63::64]) < max(typical_column * 2.5, 1.0)
        assert max(row_jumps[63::64]) < max(typical_row * 2.5, 1.0)
        edge_column = sum(abs(pixels[0, y] - pixels[255, y]) for y in range(256)) / 256
        edge_row = sum(abs(pixels[x, 0] - pixels[x, 255]) for x in range(256)) / 256
        assert edge_column < max(typical_column * 2.5, 1.0)
        assert edge_row < max(typical_row * 2.5, 1.0)


def test_cards_are_dark_subordinate_and_without_hard_bands():
    for name in ("ground_public_interior_atlas.png", "upper_institutional_interior_atlas.png"):
        with Image.open(MODULE.OUT / name) as image:
            gray = image.convert("L")
            assert sum(gray.resize((32, 16)).getdata()) / (32 * 16) < 46
            # No row may become a broad bright stripe across an atlas cell.
            for row in range(2):
                for col in range(4):
                    cell = gray.crop((col * 512, row * 512, (col + 1) * 512, (row + 1) * 512)).resize((32, 32))
                    row_means = [sum(cell.crop((0, y, 32, y + 1)).getdata()) / 32 for y in range(32)]
                    assert max(row_means) - min(row_means) < 14


def test_roof_palette_is_cool_and_courts_are_distinct():
    def rgb(name):
        with Image.open(MODULE.OUT / name) as image:
            data = list(image.resize((16, 16)).getdata())
        return tuple(sum(pixel[index] for pixel in data) / len(data) for index in range(3))
    roof = rgb("roof_membrane_intrinsic.png")
    court = rgb("sunken_roof_court_intrinsic.png")
    assert roof[2] >= roof[0]
    assert sum(roof) / 3 - sum(court) / 3 > 55
