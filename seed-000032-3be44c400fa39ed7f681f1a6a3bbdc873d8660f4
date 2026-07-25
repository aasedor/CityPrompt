"""
Generic file proxy — serves files from MinIO/S3 storage by key.

Keys contain UUIDs and are unguessable, so no auth is required
(matches the pattern used by document and building file proxies).
"""

import logging

import boto3
from botocore.config import Config
from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from app.core.config import get_settings

logger = logging.getLogger(__name__)

router = APIRouter()
settings = get_settings()


def _s3_client():
    return boto3.client(
        "s3",
        endpoint_url=settings.s3_endpoint_url,
        aws_access_key_id=settings.s3_access_key,
        aws_secret_access_key=settings.s3_secret_key,
        region_name=settings.s3_region,
        config=Config(signature_version="s3v4"),
    )


@router.head("/{file_path:path}")
async def head_file(file_path: str):
    """Check immutable object availability without downloading its payload."""
    if not file_path:
        raise HTTPException(status_code=400, detail="File path is required")

    try:
        obj = _s3_client().head_object(Bucket=settings.s3_bucket_name, Key=file_path)
    except Exception as exc:
        raise HTTPException(status_code=404, detail="File not found in storage") from exc

    headers = {"Cache-Control": "public, max-age=31536000, immutable"}
    content_length = obj.get("ContentLength")
    if content_length is not None:
        headers["Content-Length"] = str(content_length)
    return Response(
        status_code=200,
        media_type=obj.get("ContentType", "application/octet-stream"),
        headers=headers,
    )


@router.get("/{file_path:path}")
async def get_file(file_path: str):
    """Serve a file from S3-compatible storage by its key."""
    if not file_path:
        raise HTTPException(status_code=400, detail="File path is required")

    try:
        obj = _s3_client().get_object(Bucket=settings.s3_bucket_name, Key=file_path)
        file_data = obj["Body"].read()
        content_type = obj.get("ContentType", "application/octet-stream")
    except Exception as exc:
        raise HTTPException(status_code=404, detail="File not found in storage") from exc

    return Response(
        content=file_data,
        media_type=content_type,
        headers={"Cache-Control": "public, max-age=31536000, immutable"},
    )
