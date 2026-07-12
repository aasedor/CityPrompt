"""
GLB size optimizer — shrink AI-generated models before storage.

Meshy/Tripo GLBs arrive at 70-80MB, ~95% of which is 4K PBR textures. The
globe viewer loads up to 20 models at once (GlobeBuildingModelsLayer), so
oversized GLBs directly hurt load time and memory. This pass downscales
embedded textures and re-encodes color maps as JPEG, targeting <8MB.

Output stays plain GLB: the frontend loads via drei useGLTF with no draco or
meshopt decoders, so compression extensions are off the table.

Fail-open by design: any exception returns the original bytes — a paid
generation must never be lost to a codec bug.
"""

import io
import logging

from PIL import Image
from pygltflib import GLTF2

logger = logging.getLogger(__name__)

# Material texture slots that store non-color (linear) data. JPEG's chroma
# subsampling corrupts normal vectors and ORM channels, so these stay PNG.
_LINEAR_SLOTS = ("normalTexture", "occlusionTexture")


def optimize_glb(
    glb_bytes: bytes,
    *,
    max_texture_dim: int = 1024,
    jpeg_quality: int = 85,
) -> bytes:
    """Return a smaller GLB, or the original bytes if optimization fails
    or does not shrink the file."""
    try:
        optimized = _optimize(glb_bytes, max_texture_dim, jpeg_quality)
    except Exception:
        logger.warning("GLB optimization failed; keeping original bytes", exc_info=True)
        return glb_bytes

    if optimized is None or len(optimized) >= len(glb_bytes):
        return glb_bytes
    logger.info(
        "GLB optimized: %.1fMB -> %.1fMB",
        len(glb_bytes) / 1e6,
        len(optimized) / 1e6,
    )
    return optimized


def _linear_image_indices(gltf: GLTF2) -> set[int]:
    """Image indices used by normal/occlusion/metallicRoughness slots."""
    linear: set[int] = set()

    def _add(tex_info) -> None:
        if tex_info is None:
            return
        texture = gltf.textures[tex_info.index]
        if texture.source is not None:
            linear.add(texture.source)

    for material in gltf.materials or []:
        for slot in _LINEAR_SLOTS:
            _add(getattr(material, slot, None))
        pbr = material.pbrMetallicRoughness
        if pbr is not None:
            _add(pbr.metallicRoughnessTexture)
    return linear


def _reencode_image(
    data: bytes, *, is_linear: bool, max_dim: int, jpeg_quality: int
) -> tuple[bytes, str] | None:
    """Downscale/re-encode one embedded image. Returns (bytes, mime) or None
    to keep the original."""
    img = Image.open(io.BytesIO(data))
    img.load()

    if max(img.size) > max_dim:
        img.thumbnail((max_dim, max_dim), Image.LANCZOS)

    has_alpha = img.mode in ("RGBA", "LA") or (
        img.mode == "P" and "transparency" in img.info
    )

    out = io.BytesIO()
    if is_linear or has_alpha:
        if img.mode == "P":
            img = img.convert("RGBA" if has_alpha else "RGB")
        img.save(out, format="PNG", optimize=True)
        mime = "image/png"
    else:
        if img.mode != "RGB":
            img = img.convert("RGB")
        img.save(out, format="JPEG", quality=jpeg_quality)
        mime = "image/jpeg"

    encoded = out.getvalue()
    if len(encoded) >= len(data):
        return None
    return encoded, mime


def _optimize(glb_bytes: bytes, max_texture_dim: int, jpeg_quality: int) -> bytes | None:
    gltf = GLTF2.load_from_bytes(glb_bytes)
    blob = gltf.binary_blob()
    if not blob or not gltf.images or not gltf.bufferViews:
        return None
    # The rebuild below assumes ONE binary buffer. A multi-buffer GLB would
    # be silently corrupted (views into buffer 1 rewritten against buffer 0),
    # and fail-open couldn't catch it because nothing raises — so bail out.
    if len(gltf.buffers) != 1 or any((v.buffer or 0) != 0 for v in gltf.bufferViews):
        logger.info("GLB has multiple buffers; skipping optimization")
        return None

    linear_indices = _linear_image_indices(gltf)

    # Re-encode each embedded image, keyed by its bufferView index.
    replacements: dict[int, bytes] = {}
    for idx, image in enumerate(gltf.images):
        if image.bufferView is None:
            continue  # external/data-URI image — leave untouched
        view = gltf.bufferViews[image.bufferView]
        start = view.byteOffset or 0
        original = blob[start : start + view.byteLength]
        result = _reencode_image(
            original,
            is_linear=idx in linear_indices,
            max_dim=max_texture_dim,
            jpeg_quality=jpeg_quality,
        )
        if result is None:
            continue
        replacements[image.bufferView], image.mimeType = result

    if not replacements:
        return None

    # Rebuild the binary buffer with new offsets (4-byte aligned per GLB spec).
    new_blob = bytearray()
    for view_index, view in enumerate(gltf.bufferViews):
        data = replacements.get(view_index)
        if data is None:
            start = view.byteOffset or 0
            data = blob[start : start + view.byteLength]
        if len(new_blob) % 4:
            new_blob.extend(b"\x00" * (4 - len(new_blob) % 4))
        view.byteOffset = len(new_blob)
        view.byteLength = len(data)
        new_blob.extend(data)

    gltf.buffers[0].byteLength = len(new_blob)
    gltf.set_binary_blob(bytes(new_blob))

    out = gltf.save_to_bytes()
    return b"".join(out) if isinstance(out, (list, tuple)) else out
