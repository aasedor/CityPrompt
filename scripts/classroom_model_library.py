#!/usr/bin/env python3
"""Check/install the three exact starter Model Library bindings, without overwrite.

Default is an offline dry run. --verify reads the configured DB and object store.
--apply requires an existing owner and release reviews, or --local-trial against
loopback services. This never regenerates geometry or changes another model row.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import uuid
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.classroom_release import SOURCE, validate, inspect_dependency


def load_bindings(root=ROOT):
    roster = json.loads((root / SOURCE).read_text(encoding="utf-8"))
    payload = json.loads((root / "seed/classroom-release/model-bindings.json").read_text(encoding="utf-8"))
    if validate(roster) or payload.get("schema") != "cityprompt.classroom-model-bindings@1":
        raise ValueError("Invalid starter inventory or bindings")
    buildings = {entry["variantId"]: entry for entry in roster["entries"] if entry["domain"] == "building"}
    rows = payload["entries"]
    if len(rows) != len(buildings) or {row["variantId"] for row in rows} != set(buildings) or len({row["id"] for row in rows}) != len(rows):
        raise ValueError("Bindings must cover exactly the three starter buildings")
    dependencies = {dep["id"]: dep for dep in roster["dependencies"]}
    binding_dep = dependencies["repository:seed/classroom-release/model-bindings.json"]
    if inspect_dependency(binding_dep, root=root, public_root=root / "frontend/public", artifact_root=None)["status"] != "verified":
        raise ValueError("Model binding bytes differ from the pinned starter revision")
    for row in rows:
        uuid.UUID(row["id"])
        entry = buildings[row["variantId"]]
        dep = dependencies[row["modelDependency"]]
        rlasm, lego = row["metadata"]["rlasm"], row["metadata"]["lego"]
        if (dep["id"] not in entry["dependencies"] or dep["location"] != "repository"
            or rlasm["candidate"] != entry["revision"] or rlasm["variant_id"] != entry["variantId"]
            or rlasm["model_sha256"] != dep["sha256"] or lego["source_variant_id"] != entry["variantId"]
            or row["model_url"] != f"/api/v1/files/library/rlasm-architectural-clay/{entry['revision']}.glb"):
            raise ValueError("A model binding does not match its exact starter")
        if inspect_dependency(dep, root=root, public_root=root / "frontend/public", artifact_root=None)["status"] != "verified":
            raise ValueError(f"Missing or incorrect model bytes: {entry['revision']}")
    return roster, rows


def binding_matches(existing, row):
    return (existing.is_public and existing.model_url == row["model_url"]
            and all((existing.metadata_ or {}).get(key) == row["metadata"][key] for key in ("rlasm", "lego")))


def object_matches(client, bucket, row):
    from botocore.exceptions import ClientError
    key = row["model_url"].removeprefix("/api/v1/files/")
    try:
        response = client.get_object(Bucket=bucket, Key=key)
    except ClientError as exc:
        if exc.response["Error"]["Code"] in {"NoSuchKey", "404", "NotFound"}:
            return "missing"
        raise
    try:
        digest = hashlib.sha256()
        for block in iter(lambda: response["Body"].read(1024 * 1024), b""):
            digest.update(block)
    finally:
        response["Body"].close()
    return "verified" if digest.hexdigest() == row["metadata"]["rlasm"]["model_sha256"] else "conflict"


def validate_target(settings, roster, *, local_trial):
    if local_trial:
        if any(urlsplit(value).hostname not in {"127.0.0.1", "localhost", "::1"} for value in (settings.database_url, settings.s3_endpoint_url)):
            raise ValueError("Local trials require loopback database and object storage")
    elif any(entry["review"]["runtime"] != "passed" for entry in roster["entries"]):
        raise ValueError("Starter runtime reviews remain open; release installation is not qualified")


def synchronize(db, client, bucket, roster, rows, *, apply=False, owner_id=None, root=ROOT):
    from sqlalchemy import select, text
    from app.models.models import ModelLibraryEntry, User

    # No writer can race a second invocation into partially duplicated bindings.
    if apply:
        db.execute(text("SELECT pg_advisory_xact_lock(:key)"), {"key": 23_140_785_570_742})
        owner = db.get(User, owner_id)
        if owner is None or not owner.is_active:
            raise ValueError("Seed owner must be an existing active account")
    existing_rows = list(db.scalars(select(ModelLibraryEntry)))
    report = []
    for row in rows:
        existing = next((item for item in existing_rows if str(item.id) == row["id"]), None)
        if existing is not None and not binding_matches(existing, row):
            raise ValueError("An existing starter row differs; preserve it and review the conflict manually")
        for other in existing_rows:
            metadata = other.metadata_ or {}
            if (str(other.id) != row["id"] and other.is_public
                and metadata.get("rlasm", {}).get("runtime_enabled")
                and metadata.get("lego", {}).get("source_variant_id") == row["variantId"]):
                raise ValueError("Another active model claims this starter; resolve its ownership before seeding")
        status = object_matches(client, bucket, row)
        if status == "conflict":
            raise ValueError("Stored starter model has different bytes; it was not overwritten")
        report.append({"variant": row["variantId"], "binding": "verified" if existing else "missing", "object": status})
    if not apply:
        return report
    dependencies = {dep["id"]: dep for dep in roster["dependencies"]}
    for row, status in zip(rows, report):
        if status["object"] == "missing":
            key = row["model_url"].removeprefix("/api/v1/files/")
            with (root / dependencies[row["modelDependency"]]["path"]).open("rb") as body:
                client.put_object(Bucket=bucket, Key=key, Body=body, ContentType="model/gltf-binary", IfNoneMatch="*")
            if object_matches(client, bucket, row) != "verified":
                raise ValueError("Installed model failed exact byte readback")
        if status["binding"] == "missing":
            db.add(ModelLibraryEntry(id=uuid.UUID(row["id"]), owner_id=owner_id,
                name=row["name"], category="building", model_url=row["model_url"],
                lod_urls={"0": row["model_url"]}, generation_engine="rlasm", is_public=True,
                tags=["rlasm", "architectural-clay", row["variantId"]], metadata_=row["metadata"]))
    db.commit()
    return synchronize(db, client, bucket, roster, rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--verify", action="store_true")
    modes.add_argument("--apply", action="store_true")
    parser.add_argument("--owner-id", type=uuid.UUID)
    parser.add_argument("--local-trial", action="store_true")
    args = parser.parse_args()
    roster, rows = load_bindings()
    if not args.apply and not args.verify:
        print("3 exact starter bindings and local GLB hashes verified; no database or storage changes")
        return 0
    sys.path.insert(0, str(ROOT / "backend"))
    from app.core.config import get_settings
    from app.services.render_attempt_storage import _client
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session
    settings = get_settings()
    if args.apply:
        if args.owner_id is None:
            parser.error("--apply requires --owner-id")
        validate_target(settings, roster, local_trial=args.local_trial)
    engine = create_engine(settings.database_url_sync)
    client, bucket = _client()
    try:
        with Session(engine) as db:
            report = synchronize(db, client, bucket, roster, rows, apply=args.apply, owner_id=args.owner_id)
        print(json.dumps(report, indent=2))
        return int(any(row["binding"] != "verified" or row["object"] != "verified" for row in report))
    finally:
        engine.dispose()


if __name__ == "__main__":
    raise SystemExit(main())
