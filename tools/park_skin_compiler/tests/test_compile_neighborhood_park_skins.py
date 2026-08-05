from __future__ import annotations

import json
from pathlib import Path

from PIL import Image

from tools.park_skin_compiler import compile_neighborhood_park_skins as compiler


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
