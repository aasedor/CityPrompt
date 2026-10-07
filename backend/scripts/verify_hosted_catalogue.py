"""Read-only exact catalogue verification; no seed, generation, or approval writes.

From a reviewed checkout, with DATABASE_URL and S3_* explicitly exported:
  python backend/scripts/verify_hosted_catalogue.py --metadata-only
  python backend/scripts/verify_hosted_catalogue.py --verify-target --report receipt.json

The frontend-generated native contract identifies current selections. Candidate
revisions resolve through the seed manifest; native SHA revisions are delivered
by the static frontend and do not require Model Library rows. Optional authored
storey modules/assemblies are outside this base-selection receipt.
"""

from __future__ import annotations

import argparse
import asyncio
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import re
import struct
import sys
from types import SimpleNamespace
from urllib.parse import unquote, urlsplit

import asyncpg
import boto3
from botocore import UNSIGNED
from botocore.config import Config
from botocore.exceptions import ClientError

BACKEND = Path(__file__).resolve().parents[1]
ROOT = BACKEND.parent
sys.path.insert(0, str(BACKEND))
REQUIRED_ENV = ("DATABASE_URL", "S3_ENDPOINT_URL", "S3_BUCKET_NAME", "S3_ACCESS_KEY", "S3_SECRET_KEY")
SHA256 = re.compile(r"[a-f0-9]{64}")


def load_expected(contract_path: Path, library_path: Path) -> list[dict]:
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    library = json.loads(library_path.read_text(encoding="utf-8"))
    if (contract.get("schema") != "cityprompt.native-model-contract@1"
            or library.get("schema") != "cityprompt.rlasm-architectural-clay-library@1"):
        raise ValueError("Unrecognized catalogue contract")
    rows, seen = [], set()
    for row in contract["records"]:
        if not row.get("current"):
            continue
        if row["asset_id"] in seen:
            raise ValueError("Duplicate current catalogue identity")
        seen.add(row["asset_id"])
        if SHA256.fullmatch(str(row.get("revision", ""))):
            continue  # Native frontend GLB, not a Model Library binding.
        matches = [entry for entry in library["entries"]
                   if entry["candidate"] == row["revision"] and entry["variant_id"] == row["variant_id"]]
        if len(matches) != 1:
            raise ValueError("Current candidate is missing or ambiguous in the seed manifest")
        entry = matches[0]
        model = entry["model"]
        dimensions = row["dimensions_m"]
        if (not SHA256.fullmatch(model["sha256"]) or type(model["bytes"]) is not int or model["bytes"] < 20
                or len(dimensions) != 3 or any(type(v) not in (int, float) or not math.isfinite(v) or v <= 0 for v in dimensions)):
            raise ValueError("Invalid exact model contract")
        rows.append({"asset_id": row["asset_id"], "variant_id": row["variant_id"],
                     "candidate": entry["candidate"], "sha256": model["sha256"], "bytes": model["bytes"],
                     "dimensions_m": dimensions, "local_trial_only": bool(entry.get("local_trial_only"))})
    if not rows:
        raise ValueError("Current Model Library selection is empty")
    return rows


def _metadata(row):
    value = row.get("metadata")
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except ValueError:
            return {}
    return value if isinstance(value, dict) else {}


def _optional_component(row):
    metadata = _metadata(row)
    lego = metadata.get("lego")
    return (metadata.get("rlasm", {}).get("delivery_format") == "architectural_clay_module_v1"
            and isinstance(lego, dict) and lego.get("role") in {"podium", "floor", "roof"})


def _object_key(url):
    if not isinstance(url, str):
        return None
    try:
        parsed = urlsplit(url)
    except ValueError:
        return None
    prefix = "/api/v1/files/"
    path = unquote(parsed.path)
    if parsed.scheme or parsed.netloc or parsed.query or parsed.fragment or not path.startswith(prefix):
        return None
    key = path[len(prefix):]
    if not key or "\\" in key or any(piece in {"", ".", ".."} for piece in key.split("/")):
        return None
    return key


def _stored_model(client, bucket, key, expected):
    """Stream exact bytes without retaining models or returning provider errors."""
    try:
        response = client.get_object(Bucket=bucket, Key=key)
        body = response["Body"]
        try:
            digest, size, header = hashlib.sha256(), 0, b""
            while chunk := body.read(1024 * 1024):
                size += len(chunk)
                if size > expected["bytes"]:
                    return "size_mismatch"
                digest.update(chunk)
                if len(header) < 12:
                    header = (header + chunk)[:12]
        finally:
            body.close()
        if size != expected["bytes"]:
            return "size_mismatch"
        if len(header) != 12 or struct.unpack("<4sII", header) != (b"glTF", 2, size):
            return "invalid_glb"
        if digest.hexdigest() != expected["sha256"]:
            return "hash_mismatch"
        return None
    except ClientError as exc:
        code = exc.response.get("Error", {}).get("Code")
        return "missing_object" if code in {"NoSuchKey", "404", "NotFound"} else "storage_unavailable"
    except Exception:
        return "storage_unavailable"


def _privacy(client, bucket, key):
    try:
        response = client.get_object(Bucket=bucket, Key=key)
        response["Body"].close()
        return "object_publicly_readable"
    except ClientError as exc:
        # The authenticated read already proved the object exists.
        if exc.response.get("Error", {}).get("Code") in {"AccessDenied", "403", "404", "NoSuchKey", "NotFound"}:
            return None
        return "privacy_unverified"
    except Exception:
        return "privacy_unverified"


def verify_catalogue(expected, bindings, bucket, storage, anonymous):
    from app.services.lego_assembly import descriptor_from_library_entry

    results = []
    for wanted in expected:
        result = {**wanted, "status": "failed", "private_storage": "unverified", "issues": []}
        issues = result["issues"]
        if wanted["local_trial_only"]:
            issues.append("local_trial_only")
        related = [row for row in bindings if isinstance(_metadata(row).get("rlasm"), dict)
                   and _metadata(row)["rlasm"].get("variant_id") == wanted["variant_id"]]
        matching = [row for row in related if _metadata(row)["rlasm"].get("candidate") == wanted["candidate"]]
        if not matching:
            issues.append("stale_binding" if related else "missing_binding")
        else:
            matching = [row for row in matching if not _optional_component(row)]
            if not matching:
                issues.append("missing_assembly_binding")
            # Shared catalogue eligibility follows public complete assemblies.
            # Private user copies and separately authored storey modules are not
            # alternative shared base selections. Every eligible public alias
            # must still pass; one correct alias cannot conceal a broken one.
            public = [row for row in matching if row.get("is_public") is True]
            matching = public or matching
        private_count = 0
        for row in matching:
            metadata = _metadata(row)
            if metadata["rlasm"].get("model_sha256") != wanted["sha256"]:
                issues.append("stale_binding")
                continue
            if row.get("is_public") is not True:
                issues.append("binding_not_public")
                continue
            try:
                descriptor = descriptor_from_library_entry(SimpleNamespace(
                    id=row.get("id"), name="Catalogue verification", model_url=row.get("model_url"), metadata_=metadata))
                valid = (descriptor and descriptor.role == "assembled"
                         and descriptor.source_variant_id == wanted["variant_id"]
                         and all(math.isclose(actual, correct, rel_tol=0, abs_tol=0.001) for actual, correct in
                                 zip((descriptor.width_m, descriptor.depth_m, descriptor.height_m), wanted["dimensions_m"])))
            except Exception:
                valid = False
            if not valid:
                issues.append("invalid_runtime_binding")
                continue
            key = _object_key(row.get("model_url"))
            if not key:
                issues.append("unsafe_model_url")
                continue
            issue = _stored_model(storage, bucket, key, wanted)
            if issue:
                issues.append(issue)
                continue
            issue = _privacy(anonymous, bucket, key)
            if issue:
                issues.append(issue)
            else:
                private_count += 1
        if matching and private_count == len(matching):
            result["private_storage"] = "verified"
        result["issues"] = list(dict.fromkeys(issues))
        if not issues:
            result["status"] = "verified"
        results.append(result)
    return results


async def connect_database(url):
    return await asyncpg.connect(url.replace("postgresql+asyncpg://", "postgresql://", 1),
                                 timeout=10, command_timeout=30,
                                 server_settings={"default_transaction_read_only": "on"})


async def read_bindings(url, variants=None):
    connection = await connect_database(url)
    try:
        async with connection.transaction(readonly=True):
            rows = await connection.fetch(
                "SELECT id, model_url, metadata, is_public FROM model_library "
                "WHERE ($1::text[] IS NULL OR metadata->'rlasm'->>'variant_id' = ANY($1::text[]))", variants)
        return [dict(row) for row in rows]
    finally:
        await connection.close()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--metadata-only", action="store_true", help="Resolve the complete roster without network access")
    mode.add_argument("--verify-target", action="store_true", help="Read the explicitly configured DB and S3 target")
    parser.add_argument("--contract", type=Path, default=BACKEND / "app/data/native_model_contract.json")
    parser.add_argument("--library", type=Path, default=ROOT / "seed/model-library/rlasm-architectural-clay/library.json")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args(argv)
    report = {"schema": "cityprompt.hosted-catalogue-verification@1", "checked_utc": datetime.now(timezone.utc).isoformat(),
              "read_only": True, "metadata_only": args.metadata_only, "catalogue": [], "errors": []}
    exit_code = 2
    try:
        if args.verify_target and any(not os.environ.get(name, "").strip() for name in REQUIRED_ENV):
            report["errors"].append("target_configuration_missing")
        else:
            expected = load_expected(args.contract, args.library)
            report["source_sha256"] = {"contract": hashlib.sha256(args.contract.read_bytes()).hexdigest(),
                                       "library": hashlib.sha256(args.library.read_bytes()).hexdigest()}
            report["expected_count"] = len(expected)
            if args.metadata_only:
                report["catalogue"] = [{**row, "status": "metadata_only"} for row in expected]
                exit_code = 0
            else:
                bindings = asyncio.run(read_bindings(os.environ["DATABASE_URL"], [row["variant_id"] for row in expected]))
                options = dict(endpoint_url=os.environ["S3_ENDPOINT_URL"], region_name=os.environ.get("S3_REGION", "us-east-1"))
                limits = dict(connect_timeout=3, read_timeout=20, retries={"max_attempts": 1})
                storage = boto3.client("s3", **options, aws_access_key_id=os.environ["S3_ACCESS_KEY"],
                                       aws_secret_access_key=os.environ["S3_SECRET_KEY"], config=Config(signature_version="s3v4", **limits))
                anonymous = boto3.client("s3", **options, config=Config(signature_version=UNSIGNED, **limits))
                report["catalogue"] = verify_catalogue(expected, bindings, os.environ["S3_BUCKET_NAME"], storage, anonymous)
                exit_code = int(any(row["status"] != "verified" for row in report["catalogue"]))
    except Exception:
        # Never serialize a driver exception, URL, raw metadata, or credential.
        report["errors"].append("verification_unavailable")
    report["status"] = "metadata_only" if args.metadata_only and exit_code == 0 else "verified" if exit_code == 0 else "failed"
    text = json.dumps(report, indent=2) + "\n"
    if args.report:
        try:
            args.report.write_text(text, encoding="utf-8")
        except OSError:
            report["errors"].append("report_write_failed")
            report["status"] = "failed"
            text, exit_code = json.dumps(report, indent=2) + "\n", 2
    print(text, end="")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
