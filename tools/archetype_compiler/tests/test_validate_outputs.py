"""Regression tests for explicit delivery-envelope contracts."""
from __future__ import annotations

import trimesh


def test_assembled_projection_allowance_is_explicit_and_opt_in(tmp_path):
    from validate_outputs import _check_module

    path = tmp_path / "market.glb"
    mesh = trimesh.creation.box(extents=(14.0, 3.0, 10.0))
    mesh.apply_translation((0.0, 1.5, 0.0))
    mesh.export(path)

    errors_without: list[str] = []
    _check_module(
        path,
        {"role": "assembled", "width_m": 10.0, "depth_m": 10.0, "height_m": 3.0},
        errors_without,
        [],
    )
    assert any("X extent" in error for error in errors_without)

    errors_with: list[str] = []
    _check_module(
        path,
        {
            "role": "assembled",
            "width_m": 10.0,
            "depth_m": 10.0,
            "height_m": 3.0,
            "footprint_projection_allowance_m": 4.0,
        },
        errors_with,
        [],
    )
    assert not any("extent" in error for error in errors_with)
