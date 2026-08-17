from __future__ import annotations

import json
import struct
from pathlib import Path

from tools.audit_seed_model_library import (
    _dimension_warnings,
    _validate_lego_contract,
    inspect_glb,
    object_path_from_url,
)


def _write_fixture_glb(
    path: Path,
    *,
    minimum: list[float] | None = None,
    maximum: list[float] | None = None,
    include_normals: bool = True,
    translation: list[float] | None = None,
) -> None:
    attributes = {"POSITION": 0}
    if include_normals:
        attributes["NORMAL"] = 1
    payload = {
        "asset": {"version": "2.0"},
        "scene": 0,
        "scenes": [{"nodes": [0]}],
        "nodes": [{"mesh": 0, "translation": translation or [0, 0, 0]}],
        "meshes": [{"primitives": [{"attributes": attributes, "indices": 2}]}],
        "accessors": [
            {
                "count": 3,
                "type": "VEC3",
                "componentType": 5126,
                "min": minimum or [-12.0, 0.0, -9.0],
                "max": maximum or [12.0, 4.0, 9.0],
            },
            {"count": 3, "type": "VEC3", "componentType": 5126},
            {"count": 3, "type": "SCALAR", "componentType": 5123},
        ],
    }
    raw_json = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    raw_json += b" " * ((4 - len(raw_json) % 4) % 4)
    total_length = 12 + 8 + len(raw_json)
    path.write_bytes(
        struct.pack("<4sII", b"glTF", 2, total_length)
        + struct.pack("<II", len(raw_json), 0x4E4F534A)
        + raw_json
    )


def _lego_contract() -> dict:
    return {
        "role": "podium",
        "width_m": 24,
        "depth_m": 18,
        "height_m": 4,
        "coordinate_contract": {"units": "metres", "origin": "bottom centre"},
    }


def test_inspect_glb_reads_bounds_triangles_and_normals_without_vertex_decode(tmp_path: Path):
    path = tmp_path / "module.glb"
    _write_fixture_glb(path)

    stats = inspect_glb(path)

    assert stats.bounds.minimum == (-12.0, 0.0, -9.0)
    assert stats.bounds.extents == (24.0, 4.0, 18.0)
    assert stats.triangles == 1
    assert stats.missing_normal_primitives == 0
    assert _validate_lego_contract(stats, _lego_contract()) == []


def test_grounding_contract_rejects_buried_geometry(tmp_path: Path):
    path = tmp_path / "buried.glb"
    _write_fixture_glb(path, minimum=[-12.0, -2.0, -9.0], maximum=[12.0, 2.0, 9.0])

    errors = _validate_lego_contract(inspect_glb(path), _lego_contract())

    assert any("bottom sits at Y=-2.000" in error for error in errors)


def test_inspect_glb_applies_scene_node_transforms_to_ground_bounds(tmp_path: Path):
    path = tmp_path / "translated.glb"
    _write_fixture_glb(path, translation=[3.0, -1.5, 2.0])

    stats = inspect_glb(path)

    assert stats.bounds.minimum == (-9.0, -1.5, -7.0)
    assert stats.bounds.maximum == (15.0, 2.5, 11.0)


def test_grounding_contract_requires_normals_for_smooth_lighting(tmp_path: Path):
    path = tmp_path / "faceted.glb"
    _write_fixture_glb(path, include_normals=False)

    errors = _validate_lego_contract(inspect_glb(path), _lego_contract())

    assert any("no NORMAL accessor" in error for error in errors)


def test_stackable_module_must_reach_the_next_module_datum(tmp_path: Path):
    path = tmp_path / "short-floor.glb"
    _write_fixture_glb(path, maximum=[12.0, 3.5, 9.0])

    errors = _validate_lego_contract(inspect_glb(path), _lego_contract())

    assert any("below the next-module datum" in error for error in errors)


def test_stack_seam_allows_facade_details_above_the_declared_height(tmp_path: Path):
    path = tmp_path / "corniced-floor.glb"
    _write_fixture_glb(path, maximum=[12.0, 4.4, 9.0])

    errors = _validate_lego_contract(inspect_glb(path), _lego_contract())

    assert errors == []
    assert any(
        "visually verify the seam-crossing detail" in warning
        for warning in _dimension_warnings(inspect_glb(path), _lego_contract())
    )


def test_dimension_drift_is_an_optimization_warning_not_a_seed_blocker(tmp_path: Path):
    path = tmp_path / "landmark.glb"
    _write_fixture_glb(path, maximum=[20.0, 4.0, 20.0])
    stats = inspect_glb(path)

    assert _validate_lego_contract(stats, _lego_contract()) == []
    assert _dimension_warnings(stats, _lego_contract())


def test_object_url_maps_to_seed_library_key(tmp_path: Path):
    objects = tmp_path / "objects"
    path = object_path_from_url(
        "http://minio:9000/dev-platform-uploads/library/lego/family/module.glb",
        objects,
    )
    assert path == objects / "lego" / "family" / "module.glb"
