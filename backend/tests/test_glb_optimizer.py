"""GLB optimizer tests — texture downscale, JPEG re-encode, fail-open."""

import io

import numpy as np
import pytest
import trimesh
from PIL import Image
from pygltflib import GLTF2

from app.processing.glb_optimizer import optimize_glb


def _textured_glb(tex_size: int = 2048, with_normal: bool = False) -> bytes:
    """Build a small GLB with an embedded noise texture (noise defeats PNG
    compression, so the size win must come from downscale + JPEG)."""
    mesh = trimesh.creation.box()
    rng = np.random.default_rng(42)
    base = Image.fromarray(rng.integers(0, 255, (tex_size, tex_size, 3), dtype=np.uint8), "RGB")
    kwargs = {"baseColorTexture": base}
    if with_normal:
        kwargs["normalTexture"] = Image.fromarray(rng.integers(0, 255, (tex_size, tex_size, 3), dtype=np.uint8), "RGB")
    material = trimesh.visual.material.PBRMaterial(**kwargs)
    uv = rng.random((len(mesh.vertices), 2))
    mesh.visual = trimesh.visual.TextureVisuals(uv=uv, material=material)
    return mesh.export(file_type="glb")


def _embedded_images(glb_bytes: bytes) -> list[tuple[str, Image.Image]]:
    """(mimeType, PIL image) for every embedded image in a GLB."""
    gltf = GLTF2.load_from_bytes(glb_bytes)
    blob = gltf.binary_blob()
    out = []
    for image in gltf.images:
        view = gltf.bufferViews[image.bufferView]
        start = view.byteOffset or 0
        data = blob[start : start + view.byteLength]
        out.append((image.mimeType, Image.open(io.BytesIO(data))))
    return out


def test_optimizer_shrinks_and_downscales():
    original = _textured_glb(tex_size=2048)
    optimized = optimize_glb(original, max_texture_dim=1024)

    assert len(optimized) < len(original)
    images = _embedded_images(optimized)
    assert images, "optimized GLB lost its images"
    for mime, img in images:
        assert max(img.size) <= 1024
        assert mime == "image/jpeg"  # opaque baseColor becomes JPEG


def test_optimized_glb_still_loads_as_valid_gltf():
    optimized = optimize_glb(_textured_glb(tex_size=2048))
    gltf = GLTF2.load_from_bytes(optimized)
    assert gltf.meshes and gltf.accessors and gltf.buffers[0].byteLength > 0
    # geometry survived: reload through trimesh
    scene = trimesh.load(io.BytesIO(optimized), file_type="glb")
    assert len(scene.geometry) == 1


def test_normal_map_stays_png():
    optimized = optimize_glb(_textured_glb(tex_size=2048, with_normal=True))
    gltf = GLTF2.load_from_bytes(optimized)
    normal_sources = {
        gltf.textures[m.normalTexture.index].source for m in gltf.materials if m.normalTexture is not None
    }
    for idx, image in enumerate(gltf.images):
        if idx in normal_sources:
            assert image.mimeType == "image/png"


def test_small_textures_left_alone():
    original = _textured_glb(tex_size=256)
    # 256px noise: downscale does nothing; JPEG may still shrink it, but the
    # contract under test is "never grows, never corrupts".
    optimized = optimize_glb(original, max_texture_dim=1024)
    assert len(optimized) <= len(original)
    GLTF2.load_from_bytes(optimized)


@pytest.mark.parametrize("garbage", [b"", b"not a glb", b"glTF\x00\x00corrupt"])
def test_fail_open_on_corrupt_input(garbage):
    assert optimize_glb(garbage) == garbage
