"""
One-time script to backfill _preview_history from existing MinIO images.

Scans the S3 bucket for layout-previews/ and site-previews/ images,
matches them to zones by the zone ID embedded in the filename, and
populates zone.properties._preview_history.

Usage (run inside the backend container):
    python -m scripts.backfill_preview_history

Or via docker exec:
    docker exec devplatform-backend python -m scripts.backfill_preview_history
"""

import asyncio
import logging
import re
from datetime import datetime, timezone

import boto3
from botocore.config import Config
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import flag_modified

from app.core.config import get_settings
from app.core.database import async_session_factory
from app.models.models import SiteZone

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()

# Key patterns:
#   projects/{project_id}/layout-previews/{zone_id}_{uuid}.png
#   projects/{project_id}/site-previews/{zone_id}_{option_index}_{uuid}.png
LAYOUT_RE = re.compile(
    r"^projects/[^/]+/layout-previews/([0-9a-f-]{36})_([0-9a-f-]{36})\.png$"
)
SITE_RE = re.compile(
    r"^projects/[^/]+/site-previews/([0-9a-f-]{36})_(\d+)_([0-9a-f-]{36})\.png$"
)


def list_preview_keys() -> list[dict]:
    """List all preview image keys from MinIO and parse metadata."""
    s3 = boto3.client(
        "s3",
        endpoint_url=settings.s3_endpoint_url,
        aws_access_key_id=settings.s3_access_key,
        aws_secret_access_key=settings.s3_secret_key,
        region_name=settings.s3_region,
        config=Config(signature_version="s3v4"),
    )

    entries = []
    for prefix_type in ("layout-previews", "site-previews"):
        paginator = s3.get_paginator("list_objects_v2")
        for page in paginator.paginate(Bucket=settings.s3_bucket_name, Prefix="projects/"):
            for obj in page.get("Contents", []):
                key = obj["Key"]
                last_modified = obj.get("LastModified")

                if prefix_type == "layout-previews":
                    m = LAYOUT_RE.match(key)
                    if m:
                        entries.append({
                            "key": key,
                            "zone_id": m.group(1),
                            "preview_type": "layout",
                            "option_index": 0,
                            "last_modified": last_modified,
                        })
                else:
                    m = SITE_RE.match(key)
                    if m:
                        entries.append({
                            "key": key,
                            "zone_id": m.group(1),
                            "preview_type": "site",
                            "option_index": int(m.group(2)),
                            "last_modified": last_modified,
                        })

    return entries


async def backfill() -> None:
    logger.info("Scanning MinIO for existing preview images...")
    entries = list_preview_keys()
    logger.info("Found %d preview images in MinIO", len(entries))

    if not entries:
        logger.info("Nothing to backfill.")
        return

    # Group by zone_id
    zone_entries: dict[str, list[dict]] = {}
    for entry in entries:
        zone_entries.setdefault(entry["zone_id"], []).append(entry)

    # Sort each zone's entries by last_modified (oldest first)
    for zid in zone_entries:
        zone_entries[zid].sort(key=lambda e: e["last_modified"] or datetime.min.replace(tzinfo=timezone.utc))

    async with async_session_factory() as db:
        updated = 0
        skipped = 0

        for zone_id, zone_imgs in zone_entries.items():
            result = await db.execute(select(SiteZone).where(SiteZone.id == zone_id))
            zone = result.scalar_one_or_none()
            if not zone:
                logger.warning("Zone %s not found in DB — skipping %d images", zone_id, len(zone_imgs))
                skipped += len(zone_imgs)
                continue

            props = zone.properties or {}
            history: list = props.get("_preview_history", [])
            existing_urls = {e["image_url"] for e in history}

            added = 0
            for img in zone_imgs:
                image_url = f"/api/v1/files/{img['key']}"
                if image_url in existing_urls:
                    continue  # already backfilled

                created_at = img["last_modified"].isoformat() if img["last_modified"] else datetime.now(timezone.utc).isoformat()

                if img["preview_type"] == "layout":
                    label = f"Layout Preview"
                else:
                    label = f"Site Preview (option {img['option_index'] + 1})"

                history.append({
                    "image_url": image_url,
                    "label": label,
                    "strategy": "unknown",
                    "created_at": created_at,
                    "preview_type": img["preview_type"],
                    "option_index": img["option_index"],
                })
                added += 1

            if added > 0:
                # Cap at 20 most recent
                if len(history) > 20:
                    history = history[-20:]
                props["_preview_history"] = history
                zone.properties = props
                flag_modified(zone, "properties")
                db.add(zone)
                updated += added
                logger.info("Zone %s: added %d preview(s) (total: %d)", zone_id, added, len(history))

        await db.commit()
        logger.info("Backfill complete: %d images added, %d skipped (zone not found)", updated, skipped)


def main() -> None:
    asyncio.run(backfill())


if __name__ == "__main__":
    main()
