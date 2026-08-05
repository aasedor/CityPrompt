from __future__ import annotations

import json
from pathlib import Path

from PIL import Image
from shapely.geometry import Point, Polygon

from tools.park_skin_compiler import compile_neighborhood_park_skins as compiler
from tools.park_skin_compiler import generate_adaptive_park_layouts as adaptive_layouts
from tools.park_skin_compiler import generate_adaptive_urban_materials as adaptive_materials


def load_schedule() -> dict:
    return json.loads(compiler.SCHEDULE_PATH.read_text(encoding="utf-8"))


def test_schedule_has_four_bounded_reference_atlases() -> None:
    schedule = load_schedule()
    assert schedule["method"] == "reference_crop_rectify_atlas_pbr"
    assert len(schedule["variants"]) == 4
    for variant in schedule["variants"].values():
        source = compiler.REPO_ROOT / variant["source"]
        assert source.exists()
        left, top, right, bottom = variant["atlasCrop"]
        assert 0 <= left < right <= 1
        assert 0 <= top < bottom <= 1


def test_compiler_writes_one_pbr_atlas_per_variant(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(compiler, "TEXTURE_SIZE", 128)
    public_out = tmp_path / "public"
    artifact_out = tmp_path / "artifacts"
    manifest = compiler.compile_textures(load_schedule(), public_out, artifact_out)

    assert manifest["apiCalls"] == 0
    assert manifest["atlasSize"] == 128
    assert set(manifest["variants"]) == {"variant_0", "variant_1", "variant_2", "variant_3"}
    for variant_id, record in manifest["variants"].items():
        assert record["projection"].startswith("single non-repeating")
        for filename in ("albedo.jpg", "normal.png", "roughness.jpg", "ao.jpg"):
            output = public_out / variant_id / filename
            assert output.exists()
            assert Image.open(output).size == (128, 128)


def test_adaptive_material_kit_uses_reference_statistics_not_photo_projection(monkeypatch) -> None:
    schedule = json.loads(adaptive_materials.SCHEDULE_PATH.read_text(encoding="utf-8"))
    assert schedule["method"] == "reference_statistics_plus_procedural_structure"
    assert set(schedule["materials"]) == set(adaptive_materials.ROLES)
    monkeypatch.setattr(adaptive_materials, "SIZE", 64)
    source = Image.open(adaptive_materials.REPO_ROOT / schedule["source"]).convert("RGB")
    for index, role in enumerate(adaptive_materials.ROLES):
        spec = schedule["materials"][role]
        crop = source.crop(adaptive_materials.crop_pixels(source, spec["crop"]))
        generated = adaptive_materials.synthesize(role, crop, 100 + index)
        assert generated.size == (64, 64)
        assert generated.tobytes() != crop.resize((64, 64)).tobytes()


def test_adaptive_layout_recomposes_and_clips_to_irregular_parcel() -> None:
    parcel = Polygon([(-18, -8), (-10, -12), (7, -11), (18, -4), (14, 10), (2, 13), (-13, 8), (-19, 1)])
    layout = adaptive_layouts.build_layout("irregular", "Irregular", parcel)
    assert layout["areaM2"] == round(parcel.area, 1)
    assert layout["surfaceAreasM2"]["asphalt"] > 0
    assert layout["surfaceAreasM2"]["lawn"] > 0
    assert len(layout["trees"]) >= 6
    assert all(parcel.buffer(0.01).covers(Point(point)) for point in layout["trees"])
