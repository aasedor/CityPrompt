"""Pure contract checks for the Blender semantic-clay exporter."""

from __future__ import annotations

import importlib.util
import sys
import types
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


def load_exporter(monkeypatch):
    """Load the mapping code without requiring Blender in ordinary pytest."""

    fake_bpy = types.ModuleType("bpy")
    fake_mathutils = types.ModuleType("mathutils")
    fake_mathutils.Vector = object
    monkeypatch.setitem(sys.modules, "bpy", fake_bpy)
    monkeypatch.setitem(sys.modules, "mathutils", fake_mathutils)
    path = ROOT / "tools" / "archetype_compiler" / "export_semantic_clay.py"
    spec = importlib.util.spec_from_file_location("semantic_clay_export", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_semantic_palette_is_small_complete_and_texture_free(monkeypatch) -> None:
    exporter = load_exporter(monkeypatch)
    assert set(exporter.SEMANTIC_PALETTE) == {
        "masonry",
        "wall",
        "trim",
        "roof",
        "glass",
        "timber",
        "interior",
        "hardware",
    }
    for color, roughness in exporter.SEMANTIC_PALETTE.values():
        assert len(color) == 4 and color[3] == 1.0
        assert 0.0 <= roughness <= 1.0


def test_source_material_names_map_to_stable_semantic_roles(monkeypatch) -> None:
    exporter = load_exporter(monkeypatch)
    assert exporter.semantic_role("Calgary red brick masonry") == "masonry"
    assert exporter.semantic_role("Weathered asphalt roof shingle") == "roof"
    assert exporter.semantic_role("Low-e window glass") == "glass"
    assert exporter.semantic_role("Douglas fir porch timber") == "timber"
    assert exporter.semantic_role("Painted wood trim") == "trim"
    assert exporter.semantic_role("Interior warm light") == "interior"
    assert exporter.semantic_role("Black metal hardware") == "hardware"
    assert exporter.semantic_role("Mineral stucco") == "wall"
