"""
Subject isolation for image→3D inputs.

The 2026-07-10 pilot proved that non-isolated archetype card images fuse
neighbouring buildings into the generated mesh (Meshy models whatever is in
frame). This pass mattes out the background with rembg (U²-Net), composites
the subject onto a neutral backdrop, and crops to the subject bbox + margin.

rembg + onnxruntime are OPTIONAL dependencies (they require a docker image
rebuild). isolate_building fails open: if rembg is unavailable or errors,
the original bytes come back and generation proceeds un-isolated.
"""

import io
import logging

from PIL import Image

logger = logging.getLogger(__name__)

_BACKDROP_RGB = (240, 240, 240)
_CROP_MARGIN_FRAC = 0.06


def rembg_available() -> bool:
    try:
        import rembg  # noqa: F401

        return True
    except ImportError:
        return False


def isolate_building(image_bytes: bytes) -> bytes:
    """Return PNG bytes of the isolated subject on a neutral backdrop,
    cropped to the subject. Falls back to the input on any failure."""
    try:
        from rembg import remove
    except ImportError:
        logger.warning(
            "rembg not installed — sending image to image-to-3D WITHOUT isolation "
            "(neighbouring objects may fuse into the mesh). "
            "Add rembg+onnxruntime to requirements and rebuild to enable."
        )
        return image_bytes

    try:
        matted = Image.open(io.BytesIO(remove(image_bytes))).convert("RGBA")

        bbox = matted.getbbox()
        if bbox is None:
            return image_bytes
        # margin around the subject so Meshy sees a little context
        mx = int((bbox[2] - bbox[0]) * _CROP_MARGIN_FRAC)
        my = int((bbox[3] - bbox[1]) * _CROP_MARGIN_FRAC)
        bbox = (
            max(0, bbox[0] - mx),
            max(0, bbox[1] - my),
            min(matted.width, bbox[2] + mx),
            min(matted.height, bbox[3] + my),
        )
        cropped = matted.crop(bbox)

        backdrop = Image.new("RGB", cropped.size, _BACKDROP_RGB)
        backdrop.paste(cropped, mask=cropped.split()[3])

        out = io.BytesIO()
        backdrop.save(out, format="PNG")
        return out.getvalue()
    except Exception:
        logger.warning("Isolation failed; using original image", exc_info=True)
        return image_bytes
