#!/usr/bin/env python3
"""Restore the shared LEGO/3D model library onto a fresh City Prompt machine.

The runtime loads building modules from object storage
(``/api/v1/files/library/lego/...`` -> the ``library/`` prefix of the uploads
bucket), while ``model_library`` rows bind archetype ids to those files. Neither
lives in Postgres-free form anywhere else, so a clean clone renders plain
massing until this seed is applied.

``seed/model-library`` in this repo carries both halves:

    model_library.json      677 catalogue rows exported from Postgres
    objects/**              the GLB/preview files, byte-for-byte from MinIO

Usage::

    python tools/seed_model_library.py                      # apply everything
    python tools/seed_model_library.py --dry-run            # report, change nothing
    python tools/seed_model_library.py --objects-only       # upload files, skip rows
    python tools/seed_model_library.py --rows-only          # insert rows, skip files

Defaults match ``cityprompt-compose.yml``. Override with ``--endpoint``,
``--bucket``, ``--database-url`` or the matching environment variables when the
target stack differs.

Existing rows are matched on primary key and left untouched unless ``--replace``
is passed, so re-running is safe.

The export retains historical owner and source ids. A clean database does not
contain those users/projects/buildings, so restore creates inactive placeholder
owners, clears optional source provenance, and exposes LEGO modules as the
shared catalogue that the planner expects.
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import sys

SEED_DIR = pathlib.Path(__file__).resolve().parents[1] / "seed" / "model-library"
ROWS_FILE = SEED_DIR / "model_library.json"
OBJECTS_DIR = SEED_DIR / "objects"
OBJECT_PREFIX = "library/"

DEFAULT_ENDPOINT = os.environ.get("S3_ENDPOINT", "http://127.0.0.1:9000")
DEFAULT_BUCKET = os.environ.get("S3_BUCKET_NAME", "dev-platform-uploads")
DEFAULT_KEY = os.environ.get("S3_ACCESS_KEY", "minioadmin")
DEFAULT_SECRET = os.environ.get("S3_SECRET_KEY", "minioadmin")
DEFAULT_DB = os.environ.get(
    "DATABASE_URL_SYNC",
    "postgresql://devuser:devpassword@localhost:5432/dev_platform",
)

# JSON/JSONB columns are round-tripped as text so psycopg adapts them correctly.
JSON_COLUMNS = {"tags", "lod_urls", "metadata"}


def _seed_owner_ids(rows: list[dict]) -> list[str]:
    return sorted({str(row["owner_id"]) for row in rows if row.get("owner_id")})


def _prepare_row_for_restore(row: dict, columns: list[str]) -> dict:
    """Adapt an exported row to the foreign-key and visibility contract of a fresh database."""
    params = {
        column: (
            json.dumps(row[column])
            if column in JSON_COLUMNS and row.get(column) is not None
            else row.get(column)
        )
        for column in columns
    }
    # Historical source objects are provenance only and are intentionally not
    # part of this portable catalogue seed. PostgreSQL still validates SET NULL
    # foreign keys on insert, so omit those unavailable references up front.
    params["source_building_id"] = None
    params["source_project_id"] = None

    metadata = row.get("metadata")
    lego = metadata.get("lego") if isinstance(metadata, dict) else None
    if isinstance(lego, dict) and lego.get("asset_kind") == "lego_module":
        # These are the shared building modules restored by this seed. Keeping
        # their historical private flag makes every module invisible to users
        # created on the new machine and silently forces plain massing.
        params["is_public"] = True
    return params


def _ensure_seed_owners(conn, owner_ids: list[str], sa) -> None:
    for owner_id in owner_ids:
        conn.execute(
            sa.text(
                """
                INSERT INTO users (
                    id, email, hashed_password, full_name, role,
                    is_active, render_credits
                ) VALUES (
                    :id, :email, NULL, :full_name, 'viewer', false, 0
                )
                ON CONFLICT (id) DO NOTHING
                """
            ),
            {
                "id": owner_id,
                "email": f"cityprompt-seed-{owner_id}@seed.cityprompt.invalid",
                "full_name": "CityPrompt Catalogue Seed",
            },
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--endpoint", default=DEFAULT_ENDPOINT)
    parser.add_argument("--bucket", default=DEFAULT_BUCKET)
    parser.add_argument("--access-key", default=DEFAULT_KEY)
    parser.add_argument("--secret-key", default=DEFAULT_SECRET)
    parser.add_argument("--database-url", default=DEFAULT_DB)
    parser.add_argument("--objects-only", action="store_true")
    parser.add_argument("--rows-only", action="store_true")
    parser.add_argument("--replace", action="store_true", help="overwrite rows that already exist")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--skip-asset-audit",
        action="store_true",
        help="skip the GLB grounding/smoothness preflight (maintenance escape hatch)",
    )
    return parser.parse_args()


def upload_objects(args: argparse.Namespace) -> int:
    import boto3
    import botocore

    if not OBJECTS_DIR.is_dir():
        print(f"!! {OBJECTS_DIR} is missing -- did `git lfs pull` finish?")
        return 1

    files = sorted(p for p in OBJECTS_DIR.rglob("*") if p.is_file())
    total = sum(p.stat().st_size for p in files)
    print(f"objects : {len(files)} files, {total / 1073741824:.2f} GB")

    # A pointer stub is ~130 bytes of text; a real GLB never is. Catching this
    # here beats a runtime 200 that returns unusable geometry.
    stubs = [p for p in files if p.stat().st_size < 200 and p.suffix.lower() == ".glb"]
    if stubs:
        print(f"!! {len(stubs)} GLB files are still Git LFS pointer stubs. Run: git lfs pull")
        return 1

    if args.dry_run:
        print("   (dry run -- nothing uploaded)")
        return 0

    s3 = boto3.client(
        "s3",
        endpoint_url=args.endpoint,
        aws_access_key_id=args.access_key,
        aws_secret_access_key=args.secret_key,
        config=botocore.client.Config(signature_version="s3v4"),
    )
    try:
        s3.head_bucket(Bucket=args.bucket)
    except Exception:
        print(f"   creating bucket {args.bucket}")
        s3.create_bucket(Bucket=args.bucket)

    sent = 0
    for path in files:
        key = OBJECT_PREFIX + path.relative_to(OBJECTS_DIR).as_posix()
        try:
            existing = s3.head_object(Bucket=args.bucket, Key=key)
            if existing["ContentLength"] == path.stat().st_size:
                continue
        except Exception:
            pass
        s3.upload_file(str(path), args.bucket, key)
        sent += 1
        if sent % 100 == 0:
            print(f"   uploaded {sent}...", flush=True)
    print(f"   uploaded {sent} new object(s); {len(files) - sent} already present")
    return 0


def insert_rows(args: argparse.Namespace) -> int:
    import sqlalchemy as sa

    if not ROWS_FILE.is_file():
        print(f"!! {ROWS_FILE} is missing")
        return 1

    payload = json.loads(ROWS_FILE.read_text(encoding="utf-8"))
    columns = payload["columns"]
    rows = payload["rows"]
    print(f"rows    : {len(rows)} catalogue entries")

    if args.dry_run:
        print("   (dry run -- nothing written)")
        return 0

    engine = sa.create_engine(args.database_url)
    inserted = skipped = replaced = 0
    col_list = ", ".join(f'"{c}"' for c in columns)
    placeholders = ", ".join(f":{c}" for c in columns)

    with engine.begin() as conn:
        owner_ids = _seed_owner_ids(rows)
        _ensure_seed_owners(conn, owner_ids, sa)
        present = {
            str(r[0])
            for r in conn.execute(sa.text("SELECT id FROM model_library"))
        }
        for row in rows:
            rid = str(row["id"])
            if rid in present:
                if not args.replace:
                    skipped += 1
                    continue
                conn.execute(sa.text("DELETE FROM model_library WHERE id = :id"), {"id": rid})
                replaced += 1
            params = _prepare_row_for_restore(row, columns)
            conn.execute(
                sa.text(f"INSERT INTO model_library ({col_list}) VALUES ({placeholders})"),
                params,
            )
            inserted += 1

    print(f"   ensured {len(owner_ids)} inactive catalogue owner(s)")
    print(f"   inserted {inserted}, replaced {replaced}, skipped {skipped} already present")
    if skipped and not args.replace:
        print("   (pass --replace to overwrite existing entries)")
    return 0


def main() -> int:
    args = parse_args()
    print(f"endpoint: {args.endpoint}   bucket: {args.bucket}")
    status = 0
    if not args.rows_only and not args.skip_asset_audit:
        from audit_seed_model_library import audit_seed_library, print_summary

        audit = audit_seed_library(SEED_DIR)
        print_summary(audit)
        if audit["status"] != "pass":
            return 1
    if not args.rows_only:
        status |= upload_objects(args)
    if not args.objects_only and status == 0:
        status |= insert_rows(args)
    if status == 0:
        print("\nDone. Restart the backend, then Generate to 3D on a building zone.")
        print("A 200 on a /api/v1/files/library/lego/... request confirms the library is live.")
    return status


if __name__ == "__main__":
    sys.exit(main())
