from __future__ import annotations

import json
from pathlib import Path

from PIL import Image
from shapely.geometry import Point, Polygon

from tools.park_skin_compiler import compile_neighborhood_park_skins as compiler
from tools.park_skin_compiler import generate_adaptive_park_layouts as adaptive_layouts
from tools.park_skin_compiler import generate_adaptive_urban_materials as adaptive_materials
from tools.park_skin_compiler import generate_lego_depth_asset_pilot as lego_depth_pilot
from tools.park_skin_compiler import generate_park_archetype_batch as park_batch


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


def test_lego_depth_pilot_keeps_surface_and_depth_ownership_separate() -> None:
    contract_path = lego_depth_pilot.REPO_ROOT / "tools/park_skin_compiler/lego_depth_asset_pilot.json"
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    layout = lego_depth_pilot.build_layout()

    assert contract["baseCheckpoint"] == "b5ad07d6"
    assert contract["surface"]["includesCourtAndMarkings"] is True
    assert contract["depth"]["includesHorizontalSurface"] is False
    assert contract["depth"]["metricScale"] == 1.0
    assert contract["depth"]["referenceViews"] == ["base", "angle_60", "angle_90"]
    assert layout["court"]["envelopeM"] == [32.0, 19.0]
    assert layout["court"]["playingSurfaceM"] == [28.0, 15.0]
    assert layout["surfaceAreasM2"]["court"] == 608.0
    assert len(layout["trees"]) >= 20


def test_five_park_batch_is_bounded_people_free_and_building_free() -> None:
    contract = park_batch.load_contract()

    assert park_batch.validate_contract(contract) == []
    assert contract["method"] == "lego_surface_plus_metric_program_assets"
    assert contract["apiCalls"] == 0
    assert len(contract["archetypes"]) == 5
    assert contract["renderPolicy"]["people"] is False
    assert contract["renderPolicy"]["largeBuildings"] is False
    assert sum(len(item["depthAssets"]) for item in contract["archetypes"]) == 22
    assert {item["id"] for item in contract["archetypes"]} == {
        "inclusive_playground",
        "skate_park",
        "dog_park",
        "splash_pad_area",
        "community_garden",
    }


def test_five_park_batch_promotes_complete_metric_glb_kits() -> None:
    contract = park_batch.load_contract()
    kit_root = park_batch.REPO_ROOT / "frontend/public/park-kits"

    for item in contract["archetypes"]:
        archetype_root = kit_root / item["slug"]
        manifest = json.loads((archetype_root / "kit_manifest.json").read_text(encoding="utf-8"))
        assert manifest["metricScale"] == 1.0
        assert manifest["groundContactOriginZM"] == 0.0
        assert manifest["surfaceOwner"] == "lego_park_grammar"
        assert manifest["people"] is False
        assert manifest["largeBuildings"] is False
        assert manifest["depthAssets"] == sorted(item["depthAssets"])
        for filename in item["depthAssets"]:
            asset = archetype_root / filename
            assert asset.exists()
            assert asset.read_bytes()[:4] == b"glTF"
