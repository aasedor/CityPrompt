"""
Generic file proxy — serves files from MinIO/S3 storage by key.

Project assets require current project access. Only canonical cache assets and
explicitly public library models are anonymous downloads.
"""

import logging
import re
import uuid
from pathlib import PurePosixPath
from urllib.parse import urlsplit

import boto3
from botocore.config import Config
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel, Field
from sqlalchemy import Text, cast, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import get_db
from app.core.security import (
    check_project_asset_access,
    create_file_asset_ticket,
    decode_token,
    get_current_user,
    is_admin_or_above,
    require_auth,
)
from app.models.models import ModelLibraryEntry, Project, RenderAuditLog, User

logger = logging.getLogger(__name__)

router = APIRouter()
settings = get_settings()


class FileReadTicketRequest(BaseModel):
    file_path: str = Field(min_length=1, max_length=2048)


async def _file_ticket_user(file_path: str, file_ticket: str, db: AsyncSession) -> User:
    payload = decode_token(file_ticket)
    if payload.get("type") != "file_asset" or payload.get("file_path") != file_path:
        raise HTTPException(status_code=403, detail="File ticket does not cover this object")
    try:
        user_id = uuid.UUID(payload["sub"])
    except (KeyError, ValueError, TypeError):
        raise HTTPException(status_code=401, detail="Invalid file ticket") from None
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="File ticket account is inactive")
    return user


@router.post("/read-ticket")
async def issue_file_read_ticket(
    request: FileReadTicketRequest,
    response: Response,
    user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Issue an exact-object read ticket after checking current ownership/access."""
    await _authorize_file(request.file_path, user, db, None, None)
    response.headers.update(_cache_headers(False))
    return {"file_ticket": create_file_asset_ticket(request.file_path, user.id), "expires_in": 900}


def _key_from_url(url: str | None) -> str | None:
    if not url:
        return None
    path = urlsplit(url).path
    for prefix in ("/api/v1/files/", f"/{settings.s3_bucket_name}/"):
        if prefix in path:
            return path.split(prefix, 1)[1]
    return None


async def _authorize_file(
    file_path: str,
    user,
    db: AsyncSession,
    share_token: str | None,
    asset_ticket: str | None,
) -> bool:
    """Return whether immutable public caching is safe for this exact object."""
    parts = PurePosixPath(file_path).parts
    if (
        not parts
        or ".." in parts
        or any(character in file_path for character in ("\\", "?", "#"))
        or file_path.startswith("/")
        or PurePosixPath(file_path).as_posix() != file_path
    ):
        raise HTTPException(status_code=400, detail="Invalid file path")
    if parts[0] == "archetype-cache":
        return True
    if parts[0] == "projects" and len(parts) >= 3:
        try:
            project_id = uuid.UUID(parts[1])
        except ValueError:
            raise HTTPException(status_code=404, detail="File not found") from None
        await check_project_asset_access(project_id, user, db, share_token=share_token, asset_ticket=asset_ticket)
        if share_token and parts[2] not in {"models", "thumbnails"}:
            project = await db.get(Project, project_id)
            metadata = (project.metadata_ or {}) if project else {}
            public_urls = [
                item.get("image_url")
                for item in metadata.get("saved_renders", [])
                if item.get("variant") != "provider_original"
            ] + [
                item.get("video_url")
                for item in metadata.get("video_pilot_attempts", [])
                if item.get("status") == "complete"
            ]
            if file_path not in {_key_from_url(url) for url in public_urls}:
                raise HTTPException(
                    status_code=403,
                    detail="This file is not part of the public presentation",
                )
        return False
    if parts[0] == "library":
        result = await db.execute(
            select(ModelLibraryEntry).where(
                or_(
                    ModelLibraryEntry.model_url.contains(file_path, autoescape=True),
                    ModelLibraryEntry.thumbnail_url.contains(file_path, autoescape=True),
                    cast(ModelLibraryEntry.lod_urls, Text).contains(file_path, autoescape=True),
                )
            )
        )
        for entry in result.scalars().all():
            urls = [
                entry.model_url,
                entry.thumbnail_url,
                *(entry.lod_urls or {}).values(),
            ]
            if not any(_key_from_url(url) == file_path for url in urls):
                continue
            if entry.is_public:
                # Public library status is revocable: don't cache it for a year.
                return False
            if user and (entry.owner_id == user.id or is_admin_or_above(user)):
                return False
        raise HTTPException(status_code=403, detail="Not authorized to access this library file")
    if parts[0] == "render-audit":
        if not user:
            raise HTTPException(status_code=401, detail="Authentication required")
        if is_admin_or_above(user):
            return False
        try:
            audit_id = uuid.UUID(parts[1])
        except (ValueError, IndexError):
            raise HTTPException(status_code=404, detail="File not found") from None
        result = await db.execute(select(RenderAuditLog).where(RenderAuditLog.id == audit_id))
        audit = result.scalar_one_or_none()
        if audit and audit.user_id == user.id:
            return False
        raise HTTPException(status_code=403, detail="Not authorized to access this render audit")
    # New storage roots must declare their access policy before being served.
    raise HTTPException(status_code=403, detail="File is not publicly available")


def _cache_headers(public: bool) -> dict[str, str]:
    return {
        "Cache-Control": "public, max-age=31536000, immutable" if public else "private, no-store",
        "Referrer-Policy": "no-referrer",
    }


def _safe_download_name(requested: str | None, file_path: str) -> str:
    """Return an ASCII filename that is safe inside Content-Disposition."""
    fallback = PurePosixPath(file_path).name or "download"
    candidate = (requested or fallback).strip()[:160]
    sanitized = re.sub(r"[^A-Za-z0-9._-]+", "-", candidate).strip(".-")
    return sanitized or fallback


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
async def head_file(
    file_path: str,
    user: User | None = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    share_token: str | None = None,
    asset_ticket: str | None = None,
    file_ticket: str | None = None,
):
    """Check immutable object availability without downloading its payload."""
    if not file_path:
        raise HTTPException(status_code=400, detail="File path is required")
    if file_ticket:
        user = await _file_ticket_user(file_path, file_ticket, db)
    public = await _authorize_file(file_path, user, db, share_token, asset_ticket)

    try:
        obj = _s3_client().head_object(Bucket=settings.s3_bucket_name, Key=file_path)
    except Exception as exc:
        raise HTTPException(status_code=404, detail="File not found in storage") from exc

    headers = _cache_headers(public)
    content_length = obj.get("ContentLength")
    if content_length is not None:
        headers["Content-Length"] = str(content_length)
    return Response(
        status_code=200,
        media_type=obj.get("ContentType", "application/octet-stream"),
        headers=headers,
    )


@router.get("/{file_path:path}")
async def get_file(
    file_path: str,
    download: bool = False,
    filename: str | None = None,
    user: User | None = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    share_token: str | None = None,
    asset_ticket: str | None = None,
    file_ticket: str | None = None,
):
    """Serve a file from S3-compatible storage by its key."""
    if not file_path:
        raise HTTPException(status_code=400, detail="File path is required")
    if file_ticket:
        user = await _file_ticket_user(file_path, file_ticket, db)
    public = await _authorize_file(file_path, user, db, share_token, asset_ticket)

    try:
        obj = _s3_client().get_object(Bucket=settings.s3_bucket_name, Key=file_path)
        file_data = obj["Body"].read()
        content_type = obj.get("ContentType", "application/octet-stream")
    except Exception as exc:
        raise HTTPException(status_code=404, detail="File not found in storage") from exc

    headers = _cache_headers(public)
    if download:
        safe_name = _safe_download_name(filename, file_path)
        headers["Content-Disposition"] = f'attachment; filename="{safe_name}"'

    return Response(
        content=file_data,
        media_type=content_type,
        headers=headers,
    )
