#!/usr/bin/env python3
"""Snapshot private classroom objects and rehearse restore into a NEW bucket.

Uses the backend's S3_* configuration. Pause writers for a coordinated database
and object snapshot. Never prunes backups, changes bucket policy or overwrites an
existing restore bucket. No paid generation or external notifications.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHUNK = 1024 * 1024
SCHEMA = "cityprompt.object-backup@1"
ATTRIBUTES = ("ContentType", "ContentEncoding", "ContentDisposition", "CacheControl", "Metadata")


def digest_stream(stream, destination=None):
    digest, size = hashlib.sha256(), 0
    for block in iter(lambda: stream.read(CHUNK), b""):
        digest.update(block)
        size += len(block)
        if destination is not None:
            destination.write(block)
    return digest.hexdigest(), size


def inventory(client, bucket):
    return sorted([
        {"key": item["Key"], "bytes": item["Size"], "etag": item["ETag"], "modified": item["LastModified"].isoformat()}
        for page in client.get_paginator("list_objects_v2").paginate(Bucket=bucket)
        for item in page.get("Contents", [])
    ], key=lambda row: row["key"])


def snapshot(client, bucket, output: Path):
    output = output.resolve()
    if output.exists():
        raise ValueError("Choose a new backup directory; existing snapshots are never overwritten")
    rows = inventory(client, bucket)
    output.parent.mkdir(parents=True, exist_ok=True)
    if shutil.disk_usage(output.parent).free < sum(row["bytes"] for row in rows) + 1024 ** 3:
        raise ValueError("Insufficient disk space for the snapshot plus a 1 GiB reserve")
    output.mkdir()
    (output / "objects").mkdir()
    for row in rows:
        # Object keys never become filesystem paths, including hostile ../ keys.
        name = hashlib.sha256(row["key"].encode()).hexdigest() + ".blob"
        response = client.get_object(Bucket=bucket, Key=row["key"], IfMatch=row["etag"])
        try:
            with (output / "objects" / name).open("xb") as target:
                sha, size = digest_stream(response["Body"], target)
        finally:
            response["Body"].close()
        if size != row["bytes"]:
            raise ValueError("An object changed or was truncated during backup")
        row.update(file=name, sha256=sha, attributes={key: response[key] for key in ATTRIBUTES if key in response})
    if inventory(client, bucket) != [{key: row[key] for key in ("key", "bytes", "etag", "modified")} for row in rows]:
        raise ValueError("Object inventory changed; pause writers and create a new snapshot")
    manifest = {"schema": SCHEMA, "bucket": bucket, "created_at": datetime.now(timezone.utc).isoformat(), "objects": rows}
    # A partial backup has no manifest and therefore cannot qualify for restore.
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return verify(output)


def verify(source: Path):
    source = source.resolve()
    manifest = json.loads((source / "manifest.json").read_text(encoding="utf-8"))
    if manifest.get("schema") != SCHEMA or not isinstance(manifest.get("objects"), list):
        raise ValueError("Invalid snapshot manifest")
    keys = set()
    for row in manifest["objects"]:
        key, name = row["key"], row["file"]
        if not isinstance(key, str) or key in keys or name != hashlib.sha256(key.encode()).hexdigest() + ".blob":
            raise ValueError("Invalid or duplicate snapshot key")
        keys.add(key)
        path = source / "objects" / name
        if not path.resolve().is_relative_to(source) or path.is_symlink():
            raise ValueError("Snapshot object escapes its directory")
        with path.open("rb") as stream:
            sha, size = digest_stream(stream)
        if sha != row["sha256"] or size != row["bytes"]:
            raise ValueError("Snapshot object failed its byte/hash check")
        if set(row["attributes"]) - set(ATTRIBUTES):
            raise ValueError("Unsupported snapshot attributes")
    return manifest


def restore_new(client, source: Path, destination: str, live_bucket: str, region="us-east-1"):
    from botocore.exceptions import ClientError

    manifest = verify(source)  # Validate ALL local bytes before making remote writes.
    if (not re.fullmatch(r"cityprompt-restore-[a-z0-9][a-z0-9-]{0,42}", destination)
        or destination in {live_bucket, manifest["bucket"]}):
        raise ValueError("Restore only to a new cityprompt-restore-* bucket, never the live/source bucket")
    try:
        client.head_bucket(Bucket=destination)
    except ClientError as exc:
        if exc.response["Error"]["Code"] not in {"404", "NoSuchBucket", "NotFound"}:
            raise
    else:
        raise ValueError("Restore bucket already exists; nothing was overwritten")
    options = {} if region == "us-east-1" else {"CreateBucketConfiguration": {"LocationConstraint": region}}
    client.create_bucket(Bucket=destination, **options)
    # A random, previously absent bucket is mandatory. No public ACL is applied.
    for row in manifest["objects"]:
        with (source / "objects" / row["file"]).open("rb") as stream:
            client.put_object(Bucket=destination, Key=row["key"], Body=stream, IfNoneMatch="*", **row["attributes"])
        response = client.get_object(Bucket=destination, Key=row["key"])
        try:
            sha, size = digest_stream(response["Body"])
        finally:
            response["Body"].close()
        if (sha, size) != (row["sha256"], row["bytes"]):
            raise ValueError("Restored object failed readback; keep this bucket isolated")
        if any(response.get(key) != value for key, value in row["attributes"].items()):
            raise ValueError("Restored object metadata differs from the snapshot")
    actual = inventory(client, destination)
    if {row["key"] for row in actual} != {row["key"] for row in manifest["objects"]}:
        raise ValueError("Restored inventory differs from the snapshot")
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("snapshot", "verify", "restore-new"))
    parser.add_argument("directory", type=Path)
    parser.add_argument("--destination-bucket")
    args = parser.parse_args()
    if args.command == "verify":
        manifest = verify(args.directory)
    else:
        sys.path.insert(0, str(ROOT / "backend"))
        from app.services.render_attempt_storage import _client
        from app.core.config import get_settings
        client, bucket = _client()
        if args.command == "snapshot":
            manifest = snapshot(client, bucket, args.directory)
        else:
            if not args.destination_bucket:
                parser.error("restore-new requires --destination-bucket")
            manifest = restore_new(client, args.directory, args.destination_bucket, bucket, get_settings().s3_region)
    print(json.dumps({"command": args.command, "objects": len(manifest["objects"]), "bytes": sum(row["bytes"] for row in manifest["objects"]), "verified": True}))


if __name__ == "__main__":
    main()
