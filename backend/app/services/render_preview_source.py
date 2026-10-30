"""Bounded source images for previews, read only from server-owned document keys."""

from io import BytesIO
import re
import uuid

import boto3
from botocore.config import Config
from PIL import Image, ImageOps, UnidentifiedImageError

from app.core.config import get_settings

MAX_SOURCE_BYTES = 5 * 1024 * 1024
MAX_SOURCE_PIXELS = 16_000_000
MAX_SOURCE_EDGE = 8192
MAX_PREPARED_EDGE = 2048


def document_image_key(document, project_id: uuid.UUID) -> str:
    """Check the persisted source belongs to this project and its document prefix."""
    if document.project_id != project_id:
        raise ValueError("Source image must be an uploaded image in this project.")
    if document.file_type.lower() not in {"jpg", "jpeg", "png", "tiff"}:
        raise ValueError("Choose an uploaded JPG, PNG or TIFF image.")
    if not 0 < document.file_size_bytes <= MAX_SOURCE_BYTES:
        raise ValueError("Source image exceeds the 5 MB size limit.")
    settings = get_settings()
    url = document.storage_url
    prefixes = (
        f"{settings.s3_endpoint_url.rstrip('/')}/{settings.s3_bucket_name}/",
        "/api/v1/files/",
    )
    key = next((url[len(prefix) :] for prefix in prefixes if url.startswith(prefix)), "")
    pattern = rf"projects/{project_id}/documents/[0-9a-f-]{{36}}\.(jpg|jpeg|png|tiff)"
    if not re.fullmatch(pattern, key):
        raise ValueError("Source image is not a server-owned project document.")
    return key


def prepare_source_image(data: bytes) -> bytes:
    """Validate before decoding, remove metadata, and send a bounded PNG upstream."""
    if not data or len(data) > MAX_SOURCE_BYTES:
        raise ValueError("Source image is empty or exceeds the 5 MB size limit.")
    try:
        with Image.open(BytesIO(data)) as original:
            if original.format not in {"JPEG", "PNG", "TIFF"}:
                raise ValueError("Choose a JPG, PNG or TIFF source image.")
            if (
                original.width * original.height > MAX_SOURCE_PIXELS
                or max(original.size) > MAX_SOURCE_EDGE
                or getattr(original, "n_frames", 1) != 1
            ):
                raise ValueError("Source image dimensions or frame count exceed the preview limit.")
            original.load()
            image = ImageOps.exif_transpose(original).convert("RGB")
            image.thumbnail((MAX_PREPARED_EDGE, MAX_PREPARED_EDGE), Image.Resampling.LANCZOS)
            output = BytesIO()
            image.save(output, format="PNG")
            return output.getvalue()
    except (Image.DecompressionBombError, UnidentifiedImageError, OSError) as exc:
        raise ValueError("Source image is not a readable image within the preview limits.") from exc


def read_source_image(document, project_id: uuid.UUID) -> bytes:
    """Use configured object storage only; never follow a client source URL."""
    key = document_image_key(document, project_id)
    settings = get_settings()
    s3 = boto3.client(
        "s3",
        endpoint_url=settings.s3_endpoint_url,
        aws_access_key_id=settings.s3_access_key,
        aws_secret_access_key=settings.s3_secret_key,
        region_name=settings.s3_region,
        config=Config(signature_version="s3v4", connect_timeout=5, read_timeout=15, retries={"max_attempts": 1}),
    )
    obj = s3.get_object(Bucket=settings.s3_bucket_name, Key=key)
    body = obj["Body"]
    try:
        size = obj.get("ContentLength")
        if isinstance(size, int) and size > MAX_SOURCE_BYTES:
            raise ValueError("Stored source image exceeds the 5 MB size limit.")
        data = body.read(MAX_SOURCE_BYTES + 1)
    finally:
        body.close()
    return prepare_source_image(data)
