"""
Backfill dimension metadata for completed archetype_model_cache entries.

Runs INSIDE the backend container (needs DB + MinIO):
    docker compose exec backend python scripts/backfill_cache_dims.py --dry-run
    docker compose exec backend python scripts/backfill_cache_dims.py

Measures each completed entry's GLB (native extents + aspect) and writes it
to the row's metadata JSONB — the plan generator uses these dims to carve
parcels matching the model's proportions.
"""

import argparse
import sys

sys.path.insert(0, "/app")

from sqlalchemy import select

from app.core.config import get_settings
from app.models.models import ArchetypeModelCache
from app.processing.glb_measure import measure_glb
from app.tasks.processing import _get_s3_client, _get_sync_session


def _download_by_key(key: str) -> bytes:
    # model_key is a bare S3 key (not a full storage URL), so fetch directly.
    s3 = _get_s3_client()
    obj = s3.get_object(Bucket=get_settings().s3_bucket_name, Key=key)
    return obj["Body"].read()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="measure and print, write nothing")
    parser.add_argument("--force", action="store_true", help="re-measure entries that already have dims")
    args = parser.parse_args()

    session = _get_sync_session()
    rows = session.execute(select(ArchetypeModelCache).where(ArchetypeModelCache.status == "completed")).scalars().all()
    print(f"{len(rows)} completed cache entries")

    for row in rows:
        existing = (row.metadata_ or {}).get("dimensions")
        if existing and not args.force:
            print(f"  {row.archetype_id}/{row.variant_id}: already measured (aspect {existing['aspect']})")
            continue
        if not row.model_key:
            print(f"  {row.archetype_id}/{row.variant_id}: no model_key, skipping")
            continue
        glb = _download_by_key(row.model_key)
        dims = measure_glb(glb)
        if dims is None:
            print(f"  {row.archetype_id}/{row.variant_id}: MEASUREMENT FAILED")
            continue
        print(
            f"  {row.archetype_id}/{row.variant_id}: aspect {dims['aspect']} "
            f"long/h {dims['long_per_height']} short/h {dims['short_per_height']}"
            + (" [dry-run]" if args.dry_run else "")
        )
        if not args.dry_run:
            row.metadata_ = {**(row.metadata_ or {}), "dimensions": dims}
            session.commit()

    print("done")


if __name__ == "__main__":
    main()
