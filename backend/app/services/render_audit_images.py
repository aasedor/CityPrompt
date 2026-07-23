"""Helpers for render audit image storage and thumbnails."""

from __future__ import annotations

import io
import logging

from PIL import Image, ImageOps

logger = logging.getLogger(__name__)

THUMBNAIL_SIZE = (480, 360)
THUMBNAIL_QUALITY = 72


def thumbnail_key_for(image_key: str) -> str:
    """Return the deterministic S3 key for a render audit thumbnail."""
    base = image_key.rsplit(".", 1)[0]
    return f"{base}-thumb.jpg"


def make_thumbnail(image_bytes: bytes) -> bytes:
    """Create a small JPEG preview for the render logs table."""
    with Image.open(io.BytesIO(image_bytes)) as image:
        image = ImageOps.exif_transpose(image)

        if image.mode in ("RGBA", "LA") or "transparency" in image.info:
            rgba = image.convert("RGBA")
            background = Image.new("RGB", rgba.size, (255, 255, 255))
            background.paste(rgba, mask=rgba.getchannel("A"))
            image = background
        else:
            image = image.convert("RGB")

        image.thumbnail(THUMBNAIL_SIZE, Image.Resampling.LANCZOS)

        output = io.BytesIO()
        image.save(
            output,
            format="JPEG",
            quality=THUMBNAIL_QUALITY,
            optimize=True,
            progressive=True,
        )
        return output.getvalue()


def put_image_with_thumbnail(s3, bucket: str, image_key: str, image_bytes: bytes) -> None:
    """Store a full audit image and a best-effort cached thumbnail."""
    s3.put_object(
        Bucket=bucket,
        Key=image_key,
        Body=image_bytes,
        ContentType="image/png",
    )

    try:
        thumbnail_bytes = make_thumbnail(image_bytes)
        s3.put_object(
            Bucket=bucket,
            Key=thumbnail_key_for(image_key),
            Body=thumbnail_bytes,
            ContentType="image/jpeg",
        )
    except Exception as exc:
        logger.warning("Failed to create render audit thumbnail for %s: %s", image_key, exc)


def get_or_create_thumbnail(s3, bucket: str, image_key: str) -> tuple[bytes, bool]:
    """Read a cached thumbnail, creating it from the full image if needed.

    Returns the thumbnail bytes plus whether the cached object already existed.
    """
    thumbnail_key = thumbnail_key_for(image_key)

    try:
        obj = s3.get_object(Bucket=bucket, Key=thumbnail_key)
        return obj["Body"].read(), True
    except Exception:
        pass

    obj = s3.get_object(Bucket=bucket, Key=image_key)
    image_bytes = obj["Body"].read()
    thumbnail_bytes = make_thumbnail(image_bytes)

    s3.put_object(
        Bucket=bucket,
        Key=thumbnail_key,
        Body=thumbnail_bytes,
        ContentType="image/jpeg",
    )
    return thumbnail_bytes, False
