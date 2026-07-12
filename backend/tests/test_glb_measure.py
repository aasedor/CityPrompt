"""GLB measurement for the archetype model cache (plan-generator dims)."""

import io

import trimesh

from app.processing.glb_measure import measure_glb


def _box_glb(extents: list[float]) -> bytes:
    scene = trimesh.Scene(trimesh.creation.box(extents=extents))
    return scene.export(file_type="glb")


def test_measures_box_dims_and_aspect():
    # glTF Y-up: extents [x=30, y=50, z=20] -> footprint 30x20, height 50
    dims = measure_glb(_box_glb([30, 50, 20]))
    assert dims is not None
    assert dims["native_y"] == 50
    assert dims["footprint_long"] == 30
    assert dims["footprint_short"] == 20
    assert dims["aspect"] == 1.5
    assert dims["long_per_height"] == 0.6
    assert dims["short_per_height"] == 0.4


def test_footprint_axes_order_insensitive():
    # Long side on Z instead of X must yield the same footprint values.
    dims = measure_glb(_box_glb([20, 50, 30]))
    assert dims is not None
    assert dims["footprint_long"] == 30
    assert dims["footprint_short"] == 20


def test_garbage_bytes_return_none():
    assert measure_glb(b"not a glb at all") is None


def test_degenerate_flat_model_returns_none():
    # A plane with ~zero height cannot be height-anchored.
    plane = trimesh.creation.box(extents=[10, 1e-9, 10])
    glb = trimesh.Scene(plane).export(file_type="glb")
    assert measure_glb(glb) is None


def test_roundtrip_through_bytesio_export():
    # Exercise the exact load path (BytesIO, file_type="glb").
    raw = _box_glb([12, 40, 12])
    buf = io.BytesIO(raw)
    assert buf.getvalue() == raw
    dims = measure_glb(raw)
    assert dims is not None
    assert dims["aspect"] == 1.0
