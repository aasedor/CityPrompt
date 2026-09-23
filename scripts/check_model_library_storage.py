#!/usr/bin/env python3
"""Read-only check that Model Library GLBs exist in the configured S3 bucket.

Run with the same DATABASE_URL and S3_* environment as the backend. This is a
classroom setup check; it never copies objects or changes database rows.
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

import asyncpg  # noqa: E402
import boto3  # noqa: E402
from botocore.exceptions import ClientError  # noqa: E402

from app.core.config import get_settings  # noqa: E402


def storage_key(url: str, bucket: str) -> str | None:
    """Recognize server-owned file URLs and legacy bucket URLs only."""
    path = unquote(urlsplit(url).path)
    for prefix in ("/api/v1/files/", f"/{bucket}/"):
        if prefix in path:
            key = path.split(prefix, 1)[1].strip("/")
            return key or None
    return None


def check_urls(rows: list[tuple[str, str]], bucket: str, client) -> tuple[list[str], list[str]]:
    missing: list[str] = []
    uncheckable: list[str] = []
    for name, url in rows:
        key = storage_key(url, bucket)
        if key is None:
            uncheckable.append(name)
            continue
        try:
            result = client.head_object(Bucket=bucket, Key=key)
        except ClientError as exc:
            if exc.response["Error"]["Code"] not in {"404", "NoSuchKey", "NotFound"}:
                raise
            missing.append(f"{name}: {key}")
            continue
        if int(result.get("ContentLength", 0)) < 20:
            missing.append(f"{name}: {key} (empty or truncated)")
    return missing, uncheckable


async def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bucket", help="Override the backend's configured S3 bucket")
    args = parser.parse_args()
    settings = get_settings()
    bucket = args.bucket or settings.s3_bucket_name
    connection = await asyncpg.connect(settings.database_url_sync)
    try:
        records = await connection.fetch(
            "SELECT name, model_url FROM model_library WHERE model_url IS NOT NULL ORDER BY name"
        )
    finally:
        await connection.close()
    rows = [(str(record["name"] or "Unnamed model"), str(record["model_url"])) for record in records]
    client = boto3.client(
        "s3",
        endpoint_url=settings.s3_endpoint_url,
        aws_access_key_id=settings.s3_access_key,
        aws_secret_access_key=settings.s3_secret_key,
        region_name=settings.s3_region,
    )
    missing, uncheckable = check_urls(rows, bucket, client)
    print(f"Model Library storage: {len(rows) - len(missing) - len(uncheckable)}/{len(rows)} present in {bucket}")
    for item in missing:
        print(f"MISSING {item}")
    for item in uncheckable:
        print(f"UNCHECKABLE {item}")
    return 1 if missing or uncheckable else 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
