#!/usr/bin/env python3
"""Restore the shared LEGO/3D model library onto a fresh City Prompt machine.

The runtime loads building modules from object storage
(``/api/v1/files/library/lego/...`` -> the ``library/`` prefix of the uploads
bucket), while ``model_library`` rows bind archetype ids to those files. Neither
lives in Postgres-free form anywhere else, so a clean clone renders plain
massing until this seed is applied.

``seed/model-library`` in this repo carries both halves:

    rlasm-architectural-clay/  canonical reviewed building GLBs and manifest
    model_library.json        legacy/exported catalogue rows
    objects/**                legacy GLB/preview files, byte-for-byte from MinIO

Usage::

    python tools/seed_model_library.py                      # apply everything
    python tools/seed_model_library.py --dry-run            # report, change nothing
    python tools/seed_model_library.py --objects-only       # upload files, skip rows
    python tools/seed_model_library.py --rows-only          # insert rows, skip files
    python tools/seed_model_library.py --rlasm-clay-only    # canonical clay buildings only
    python tools/seed_model_library.py --owner-id <uuid>    # bind rows to an existing local user

Defaults match the host ports in ``cityprompt-compose.yml``. Override with
``--endpoint``, ``--bucket``, ``--database-url`` or the matching environment
variables when the target stack differs. If the exported seed owner does not
exist in that database, pass ``--owner-id`` with an existing local user UUID.

Existing rows are matched on primary key and left untouched unless ``--replace``
is passed, so re-running is safe.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
import sys
from urllib.parse import urlparse

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from tools.rlasm_clay_library import CLAY_ROOT, REPO_ROOT, _validate_payload, clay_seed_objects, clay_seed_rows, load_library

SEED_DIR = pathlib.Path(__file__).resolve().parents[1] / "seed" / "model-library"
ROWS_FILE = SEED_DIR / "model_library.json"
OBJECTS_DIR = SEED_DIR / "objects"
OBJECT_PREFIX = "library/"

DEFAULT_ENDPOINT = os.environ.get(
    "S3_ENDPOINT_URL",
    os.environ.get("S3_ENDPOINT", "http://127.0.0.1:9000"),
)
DEFAULT_BUCKET = os.environ.get("S3_BUCKET_NAME", "dev-platform-uploads")
DEFAULT_KEY = os.environ.get("S3_ACCESS_KEY", "minioadmin")
DEFAULT_SECRET = os.environ.get("S3_SECRET_KEY", "minioadmin")
DEFAULT_DB = os.environ.get(
    "DATABASE_URL_SYNC",
    "postgresql://devuser:devpassword@localhost:5432/dev_platform",
)

# JSON/JSONB columns are round-tripped as text so psycopg adapts them correctly.
JSON_COLUMNS = {"tags", "lod_urls", "metadata"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--endpoint", default=DEFAULT_ENDPOINT)
    parser.add_argument("--bucket", default=DEFAULT_BUCKET)
    parser.add_argument("--access-key", default=DEFAULT_KEY)
    parser.add_argument("--secret-key", default=DEFAULT_SECRET)
    parser.add_argument("--database-url", default=DEFAULT_DB)
    parser.add_argument(
        "--owner-id",
        default=os.environ.get("MODEL_LIBRARY_SEED_OWNER_ID"),
        help="override every seeded row owner with an existing users.id UUID",
    )
    parser.add_argument("--objects-only", action="store_true")
    parser.add_argument("--rows-only", action="store_true")
    parser.add_argument("--replace", action="store_true", help="overwrite rows that already exist")
    parser.add_argument(
        "--rlasm-clay-only",
        action="store_true",
        help="seed only the canonical RLASM architectural-clay building collection",
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--clay-library", type=pathlib.Path,
                        help="explicit reviewed manifest under repository seed/; requires selected clay candidates")
    parser.add_argument(
        "--candidate",
        action="append",
        help="exact clay candidate to install; repeat for a finite batch (requires --rlasm-clay-only)",
    )
    parser.add_argument(
        "--verify", action="store_true", help="read back GLB hashes and public database bindings without writing"
    )
    parser.add_argument(
        "--local-trial", action="store_true", help="allow reviewed unpublished pilots on loopback storage/database only"
    )
    return parser.parse_args()


def load_seed_library(manifest, *, repo_root=REPO_ROOT):
    """Normalize a separate reviewed handoff in memory; keep canonical validation."""
    if manifest is None:
        return load_library(), CLAY_ROOT
    repo_root = repo_root.resolve()
    manifest = pathlib.Path(manifest).resolve()
    seed_root = (repo_root / "seed").resolve()
    if not manifest.is_relative_to(seed_root) or manifest.suffix != ".json":
        raise ValueError("Explicit clay manifest must be a JSON file within repository seed/")
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    roots = set()
    for entry in payload.get("entries", []):
        relative = str(entry["model"]["path"])
        if ":" in relative or "\\" in relative or pathlib.PurePosixPath(relative).is_absolute():
            raise ValueError("Explicit clay source must be a relative model path")
        source = (manifest.parent / relative).resolve()
        if not source.is_relative_to(seed_root) or source.suffix != ".glb" or source.parent.name != "models":
            raise ValueError("Explicit clay source must stay within a repository seed models/ directory")
        roots.add(source.parent.parent)
        entry["model"]["path"] = "models/" + source.name
    if len(roots) != 1:
        raise ValueError("Explicit clay manifest must use one common models/ directory")
    clay_root = roots.pop()
    _validate_payload(payload, clay_root=clay_root, repo_root=repo_root)
    return payload, clay_root


def remote_hash(s3, bucket, key):
    body = s3.get_object(Bucket=bucket, Key=key)["Body"]
    digest = hashlib.sha256()
    try:
        for block in iter(lambda: body.read(1024 * 1024), b""):
            digest.update(block)
    finally:
        body.close()
    return digest.hexdigest()


def upload_explicit_objects(s3, bucket, objects, hashes):
    """Refuse any conflict before uploading the bounded missing-object set."""
    from botocore.exceptions import ClientError

    missing = []
    for path, key in objects:
        try:
            existing = s3.head_object(Bucket=bucket, Key=key)
        except ClientError as exc:
            if exc.response.get("Error", {}).get("Code") not in {"404", "NoSuchKey", "NotFound"}:
                raise
            missing.append((path, key))
            continue
        if existing["ContentLength"] != path.stat().st_size or remote_hash(s3, bucket, key) != hashes[key]:
            raise ValueError(f"Refusing conflicting stored clay object: {key}")
    for path, key in missing:
        s3.upload_file(str(path), bucket, key)
    return len(missing)


def seed_metadata_digest(metadata):
    """Seal the complete historical JSON value independently of object-key order."""
    return hashlib.sha256(json.dumps(metadata, sort_keys=True, separators=(",", ":"),
                                     ensure_ascii=False, allow_nan=False).encode("utf-8")).hexdigest()


def verified_seed_review(entry, *, repo_root=REPO_ROOT):
    """Read only the review bytes already pinned by this canonical entry."""
    path = (repo_root / entry["review"]["repo_path"]).resolve()
    if not path.is_relative_to(repo_root.resolve()) or hashlib.sha256(path.read_bytes()).hexdigest() != entry["review"]["sha256"]:
        raise ValueError("Independent seed review bytes do not match the canonical entry")
    return json.loads(path.read_text(encoding="utf-8"))


def verify_existing_row(expected, stored, *, review=None, verified_model_sha256=None):
    """Accept canonical metadata, or one fully sealed unchanged historical row.

    Compatibility never updates a row. It requires the hashed canonical review,
    its original raw review, exact historical metadata, and separately verified
    stored GLB bytes. Only the documented provenance/family differences vary.
    """
    metadata = stored["metadata"]
    if isinstance(metadata, str):
        metadata = json.loads(metadata)
    lod_urls = stored["lod_urls"]
    if isinstance(lod_urls, str):
        lod_urls = json.loads(lod_urls)
    if (stored["model_url"] != expected["model_url"] or stored["is_public"] is not True
            or lod_urls != expected["lod_urls"] or not isinstance(metadata, dict)):
        raise ValueError("Refusing conflicting existing clay database binding")
    if all(metadata.get(key) == expected["metadata"].get(key) for key in ("rlasm", "lego")):
        return
    canonical, legacy = expected["metadata"], metadata
    if not all(isinstance(legacy.get(key), dict) for key in ("rlasm", "lego")):
        raise ValueError("Refusing conflicting existing clay database binding")
    rlasm, lego = canonical.get("rlasm", {}), canonical.get("lego", {})
    review = review if isinstance(review, dict) else {}
    attestation = review.get("legacy_seed_metadata_attestation") or {}
    source = review.get("source_review") or {}
    candidate, model_hash = rlasm.get("candidate"), rlasm.get("model_sha256")
    storage_key = f"library/rlasm-architectural-clay/{candidate}.glb"
    # Exact digest plus unchanged runtime fields; this is not a general family
    # or reviewer allowlist. The source-specific values live in two sealed reviews.
    rlasm_provenance = {"review_sha256", "review_status", "design_dimensions_m", "source_delivery", "import_scope"}
    unchanged_rlasm = {k: v for k, v in legacy.get("rlasm", {}).items() if k not in rlasm_provenance}
    expected_rlasm = {k: v for k, v in rlasm.items() if k not in rlasm_provenance}
    unchanged_lego = {k: v for k, v in legacy.get("lego", {}).items() if k != "family"}
    expected_lego = {k: v for k, v in lego.items() if k != "family"}
    if (not isinstance(attestation, dict)
            or attestation.get("schema") != "cityprompt.clay-legacy-seed-attestation@1"
            or attestation.get("candidate") != candidate or attestation.get("row_id") != expected["id"]
            or attestation.get("storage_key") != storage_key
            or expected["model_url"] != "/api/v1/files/" + storage_key
            or attestation.get("model_sha256") != model_hash or verified_model_sha256 != model_hash
            or review.get("candidate") != candidate or review.get("model_sha256") != model_hash
            or review.get("architectural_clay_pass") is not True or review.get("holistic_review_performed") is not True
            or review.get("unresolved_p0") != 0 or review.get("unresolved_p1") != 0
            or not isinstance(source, dict) or not isinstance(source.get("text"), str)
            or hashlib.sha256(source["text"].encode("utf-8")).hexdigest() != source.get("sha256")
            or source.get("sha256") != legacy.get("rlasm", {}).get("review_sha256")
            or attestation.get("source_review_sha256") != source.get("sha256")
            or attestation.get("native_floors") != lego.get("native_floors")
            or attestation.get("native_dimensions_m") != rlasm.get("native_dimensions_m")
            or attestation.get("legacy_metadata_sha256") != seed_metadata_digest(metadata)
            or unchanged_rlasm != expected_rlasm or unchanged_lego != expected_lego):
        raise ValueError("Refusing conflicting existing clay database binding")


def select_candidates(payload, candidates):
    if not candidates:
        return payload
    selected = set(candidates)
    missing = selected - {entry["candidate"] for entry in payload["entries"]}
    if missing:
        raise ValueError(f"Unknown clay candidates: {sorted(missing)}")
    return {**payload, "entries": [entry for entry in payload["entries"] if entry["candidate"] in selected]}


def verify_install(args, payload):
    import boto3
    import sqlalchemy as sa

    s3 = boto3.client(
        "s3", endpoint_url=args.endpoint, aws_access_key_id=args.access_key, aws_secret_access_key=args.secret_key
    )
    engine = sa.create_engine(args.database_url)
    explicit = bool(getattr(args, "clay_library", None))
    row_columns = "model_url, is_public, metadata" + (", lod_urls" if explicit else "")
    try:
        with engine.connect() as conn:
            for entry, row in zip(payload["entries"], clay_seed_rows(payload)):
                key = "library/rlasm-architectural-clay/" + pathlib.PurePosixPath(entry["model"]["path"]).name
                verified_hash = remote_hash(s3, args.bucket, key)
                if verified_hash != entry["model"]["sha256"]:
                    raise ValueError(f"Stored GLB mismatch: {entry['candidate']}")
                stored = (
                    conn.execute(
                        sa.text(f"SELECT {row_columns} FROM model_library WHERE id = :id"),
                        {"id": row["id"]},
                    )
                    .mappings()
                    .first()
                )
                if not stored or stored["model_url"] != row["model_url"] or not stored["is_public"]:
                    raise ValueError(f"Missing or incorrect public binding: {entry['candidate']}")
                if explicit:
                    try:
                        verify_existing_row(row, stored)
                    except ValueError:
                        if not entry.get("review"):
                            raise
                        verify_existing_row(row, stored, review=verified_seed_review(entry),
                                            verified_model_sha256=verified_hash)
                metadata = stored["metadata"]
                if isinstance(metadata, str):
                    metadata = json.loads(metadata)
                if (
                    metadata.get("rlasm", {}).get("model_sha256") != entry["model"]["sha256"]
                    or metadata.get("lego", {}).get("variant_key") != entry["variant_id"]
                ):
                    raise ValueError(f"Stale model metadata: {entry['candidate']}")
                print(f"verified: {entry['candidate']}")
    finally:
        engine.dispose()
    return 0


def upload_objects(args: argparse.Namespace, clay_payload: dict, *, clay_root=CLAY_ROOT) -> int:
    import boto3
    import botocore

    if not args.rlasm_clay_only and not OBJECTS_DIR.is_dir():
        print(f"!! {OBJECTS_DIR} is missing -- did `git lfs pull` finish?")
        return 1

    objects = (
        []
        if args.rlasm_clay_only
        else [
            (path, OBJECT_PREFIX + path.relative_to(OBJECTS_DIR).as_posix())
            for path in sorted(OBJECTS_DIR.rglob("*"))
            if path.is_file()
        ]
    )
    objects.extend((item.source, item.storage_key) for item in clay_seed_objects(clay_payload, clay_root=clay_root))
    total = sum(path.stat().st_size for path, _ in objects)
    print(f"objects : {len(objects)} files, {total / 1073741824:.2f} GB")

    # A pointer stub is ~130 bytes of text; a real GLB never is. Catching this
    # here beats a runtime 200 that returns unusable geometry.
    stubs = [path for path, _ in objects if path.stat().st_size < 200 and path.suffix.lower() == ".glb"]
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
    if getattr(args, "clay_library", None):
        s3.head_bucket(Bucket=args.bucket)
        hashes = {"library/rlasm-architectural-clay/" + pathlib.PurePosixPath(entry["model"]["path"]).name:
                  entry["model"]["sha256"] for entry in clay_payload["entries"]}
        sent = upload_explicit_objects(s3, args.bucket, objects, hashes)
        print(f"   uploaded {sent} new object(s); {len(objects) - sent} exact objects already present")
        return 0
    try:
        s3.head_bucket(Bucket=args.bucket)
    except Exception:
        print(f"   creating bucket {args.bucket}")
        s3.create_bucket(Bucket=args.bucket)

    sent = 0
    clay_hashes = {
        "library/rlasm-architectural-clay/" + pathlib.PurePosixPath(e["model"]["path"]).name: e["model"]["sha256"]
        for e in clay_payload["entries"]
    }
    for path, key in objects:
        try:
            existing = s3.head_object(Bucket=args.bucket, Key=key)
            if existing["ContentLength"] == path.stat().st_size:
                if key not in clay_hashes or remote_hash(s3, args.bucket, key) == clay_hashes[key]:
                    continue
        except Exception:
            pass
        s3.upload_file(str(path), args.bucket, key)
        sent += 1
        if sent % 100 == 0:
            print(f"   uploaded {sent}...", flush=True)
    print(f"   uploaded {sent} new object(s); {len(objects) - sent} already present")
    return 0


def insert_rows(args: argparse.Namespace, clay_payload: dict) -> int:
    import sqlalchemy as sa

    clay_rows = list(clay_seed_rows(clay_payload))
    if args.rlasm_clay_only:
        columns = list(clay_rows[0])
        legacy_rows = []
    else:
        if not ROWS_FILE.is_file():
            print(f"!! {ROWS_FILE} is missing")
            return 1
        payload = json.loads(ROWS_FILE.read_text(encoding="utf-8"))
        columns = payload["columns"]
        legacy_rows = list(payload["rows"])
    rows = [*legacy_rows, *clay_rows]
    if args.owner_id:
        rows = [{**row, "owner_id": args.owner_id} for row in rows]
    print(f"rows    : {len(rows)} catalogue entries " f"({len(clay_rows)} canonical RLASM clay)")

    if args.dry_run:
        print("   (dry run -- nothing written)")
        return 0

    clay_entries = {entry["candidate"]: entry for entry in clay_payload["entries"]}
    engine = sa.create_engine(args.database_url)
    inserted = skipped = replaced = 0
    col_list = ", ".join(f'"{c}"' for c in columns)
    placeholders = ", ".join(f":{c}" for c in columns)

    with engine.begin() as conn:
        available_owners = {str(r[0]) for r in conn.execute(sa.text("SELECT id FROM users"))}
        missing_owners = sorted({str(row["owner_id"]) for row in rows} - available_owners)
        if missing_owners:
            print("!! seeded owner UUID(s) do not exist in users: " + ", ".join(missing_owners))
            print("   pass --owner-id with an existing local users.id UUID")
            return 1
        present = {str(r[0]) for r in conn.execute(sa.text("SELECT id FROM model_library"))}
        for row in rows:
            rid = str(row["id"])
            if rid in present:
                if getattr(args, "clay_library", None):
                    stored = conn.execute(sa.text("SELECT model_url, is_public, metadata, lod_urls FROM model_library WHERE id = :id"),
                                          {"id": rid}).mappings().one()
                    try:
                        verify_existing_row(row, stored)
                    except ValueError:
                        entry = clay_entries[row["metadata"]["rlasm"]["candidate"]]
                        review = verified_seed_review(entry)
                        if not review.get("legacy_seed_metadata_attestation"):
                            raise
                        # --rows-only must prove the same exact stored GLB too;
                        # an earlier upload check cannot stand in for this read.
                        import boto3
                        client = boto3.client("s3", endpoint_url=args.endpoint,
                                              aws_access_key_id=args.access_key,
                                              aws_secret_access_key=args.secret_key)
                        key = "library/rlasm-architectural-clay/" + pathlib.PurePosixPath(entry["model"]["path"]).name
                        verify_existing_row(row, stored, review=review,
                                            verified_model_sha256=remote_hash(client, args.bucket, key))
                if not args.replace:
                    skipped += 1
                    continue
                conn.execute(sa.text("DELETE FROM model_library WHERE id = :id"), {"id": rid})
                replaced += 1
            params = {c: (json.dumps(row[c]) if c in JSON_COLUMNS and row[c] is not None else row[c]) for c in columns}
            conn.execute(
                sa.text(f"INSERT INTO model_library ({col_list}) VALUES ({placeholders})"),
                params,
            )
            inserted += 1

    print(f"   inserted {inserted}, replaced {replaced}, skipped {skipped} already present")
    if skipped and not args.replace:
        print("   (pass --replace to overwrite existing entries)")
    return 0


def main() -> int:
    args = parse_args()
    if (args.candidate or args.verify) and not args.rlasm_clay_only:
        raise ValueError("--candidate and --verify require --rlasm-clay-only")
    if args.verify and (args.dry_run or args.objects_only or args.rows_only or args.replace):
        raise ValueError("--verify is a standalone read-only action")
    if args.clay_library and (not args.rlasm_clay_only or not args.candidate or args.replace):
        raise ValueError("--clay-library requires --rlasm-clay-only and finite --candidate selections; --replace is forbidden")
    clay_payload, clay_root = load_seed_library(args.clay_library)
    clay_payload = select_candidates(clay_payload, args.candidate)
    if args.local_trial:
        if (
            not args.rlasm_clay_only
            or not args.candidate
            or any(
                urlparse(url).hostname not in {"localhost", "127.0.0.1", "::1"}
                for url in (args.endpoint, args.database_url)
            )
        ):
            raise ValueError("Local trials require selected candidates and loopback storage/database")
    elif any(entry.get("local_trial_only") for entry in clay_payload["entries"]):
        raise ValueError("Unpublished pilot: use --local-trial with isolated loopback services")
    # Verify the actual independent review, not just the manifest's PASS label.
    from tools.catalogue_promotion import validate_review

    for entry in clay_payload["entries"]:
        validate_review(entry, SEED_DIR.parent.parent)
    print(f"endpoint: {args.endpoint}   bucket: {args.bucket}")
    if args.verify:
        return verify_install(args, clay_payload)
    status = 0
    if not args.rows_only:
        status |= upload_objects(args, clay_payload, clay_root=clay_root)
    if not args.objects_only and status == 0:
        status |= insert_rows(args, clay_payload)
    if status == 0:
        if args.dry_run:
            print("\nDry run passed. No files uploaded or database rows changed.")
            return 0
        print("\nDone. Refresh City Prompt, select the building and place it on an empty site.")
        path = "rlasm-architectural-clay" if args.rlasm_clay_only else "lego or rlasm-architectural-clay"
        print(f"A 200 on a /api/v1/files/library/{path}/... request confirms the library is live.")
    return status


if __name__ == "__main__":
    sys.exit(main())
