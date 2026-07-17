"""Facade-sheet processing and world-class library contract tests."""
from __future__ import annotations

import json
from pathlib import Path

import pytest


def test_worldclass_registry_has_twenty_unique_real_archetypes():
    registry = json.loads(
        (Path(__file__).parents[1] / "worldclass_v7_library.json").read_text(encoding="utf-8")
    )
    entries = registry["entries"]
    ids = [entry["archetype_id"] for entry in entries]
    assert len(entries) == 20
    assert len(set(ids)) == 20
    assert all(entry.get("floors", 0) >= 3 for entry in entries)
    assert registry["generation_profile"]["geometry_detail"] == "city"


def test_corner_archetype_compiles_corner_condition():
    from compiler import compile_archetype
    from test_compiler import payload_mixed_use_midrise

    grammar = compile_archetype(payload_mixed_use_midrise(
        archetypeId="parisian_boulevard_corner",
        archetypeLabel="Parisian Boulevard Corner",
    ))
    assert grammar.massing.corner_condition == "corner"


def test_facade_prompts_pin_texture_map_and_forbid_scene_completion():
    pytest.importorskip("PIL")
    pytest.importorskip("numpy")
    from generate_facade_sheets import PROMPT_TEMPLATES

    for prompt in PROMPT_TEMPLATES:
        lowered = prompt.lower()
        assert "texture" in lowered
        assert "orthographic" in lowered or "zero perspective" in lowered
        assert "no sky" in lowered
        assert "no people" in lowered


def test_horizontal_blend_wraps_without_vertical_tiling():
    np = pytest.importorskip("numpy")
    pytest.importorskip("PIL")
    from PIL import Image
    from generate_facade_sheets import make_horizontally_tileable

    array = np.zeros((64, 96, 3), dtype=np.uint8)
    array[:, :, 0] = np.linspace(10, 240, 96, dtype=np.uint8)[None, :]
    array[:16, :, 1] = 220
    result = np.asarray(make_horizontally_tileable(Image.fromarray(array)))
    horizontal_seam = abs(result[:, 0].astype(float) - result[:, -1].astype(float)).mean()
    assert horizontal_seam < 2.0
    assert result[:16, :, 1].mean() > result[-16:, :, 1].mean() + 100


def test_emissive_mask_prefers_warm_lit_pixels():
    np = pytest.importorskip("numpy")
    pytest.importorskip("PIL")
    from PIL import Image
    from generate_facade_sheets import derive_emissive_mask

    array = np.zeros((64, 64, 3), dtype=np.uint8)
    array[:, :32] = (188, 132, 62)
    array[:, 32:] = (84, 132, 188)
    mask = np.asarray(derive_emissive_mask(Image.fromarray(array)))
    assert mask[:, :28].mean() > mask[:, 36:].mean() + 100
