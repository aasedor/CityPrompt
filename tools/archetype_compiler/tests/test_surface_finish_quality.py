"""Unit tests for baked material and render-parity auditing."""
from __future__ import annotations

import numpy as np
from PIL import Image


def test_render_parity_accepts_small_export_shift_and_rejects_large_change(tmp_path):
    from surface_finish_quality import render_parity

    source = np.full((32, 32, 3), 128, dtype=np.uint8)
    near = np.full((32, 32, 3), 136, dtype=np.uint8)
    far = np.full((32, 32, 3), 240, dtype=np.uint8)
    for name, value in (("source", source), ("near", near), ("far", far)):
        Image.fromarray(value, "RGB").save(tmp_path / f"{name}.png")
    assert render_parity(tmp_path / "source.png", tmp_path / "near.png")["passed"] is True
    assert render_parity(tmp_path / "source.png", tmp_path / "far.png")["passed"] is False


def test_render_parity_scores_alpha_masked_building_not_background(tmp_path):
    from surface_finish_quality import render_parity

    source = np.zeros((64, 64, 4), dtype=np.uint8)
    roundtrip = np.zeros((64, 64, 4), dtype=np.uint8)
    source[24:40, 24:40] = [140, 100, 70, 255]
    roundtrip[24:40, 24:40] = [20, 30, 40, 255]
    Image.fromarray(source, "RGBA").save(tmp_path / "source.png")
    Image.fromarray(roundtrip, "RGBA").save(tmp_path / "roundtrip.png")

    report = render_parity(tmp_path / "source.png", tmp_path / "roundtrip.png")
    assert report["scope"] == "alpha_masked_building_foreground"
    assert report["foreground_pixel_count"] == 256
    assert report["passed"] is False


def test_surface_audit_requires_all_exported_pbr_channels():
    from surface_finish_quality import assess

    grammar = {
        "materials": {"primary": {"texture_key": "stone_story", "baked_pbr": True}},
        "architectural_signature": {"production_contract": {"surface_finish": {
            "required_baked_materials": ["primary"],
        }}},
    }
    manifest = {"materials": [{
        "texture_key": "stone_story", "baked_pbr": True,
        "statistics": {"albedo_std": 8.0, "roughness_std": 4.0, "normal_xy_std": 2.0},
    }]}
    glb = {"materials": [{
        "name": "Stone", "extras": {"texture_key": "stone_story"},
        "pbrMetallicRoughness": {"baseColorTexture": {"index": 0}, "metallicRoughnessTexture": {"index": 1}},
        "normalTexture": {"index": 2},
    }]}
    report = assess(grammar, manifest, glb)
    assert {item["id"] for item in report["failures"]} == {"neutral_glb_roundtrip_parity"}

    glb["materials"][0].pop("normalTexture")
    report = assess(grammar, manifest, glb)
    assert "glb_pbr_channels:primary" in {item["id"] for item in report["failures"]}
