#!/usr/bin/env python3
"""Synchronize the finite classroom roster and verify its exact asset bytes.

No generation, downloads, database writes or activation. A successful metadata
check does not imply that assets are hydrated or that runtime reviews passed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path("seed/classroom-release/starter-v1.json")
COPIES = (
    Path("frontend/src/data/classroomStarter.json"),
    Path("backend/app/data/classroomStarter.json"),
)
SHA = re.compile(r"[0-9a-f]{64}")
LFS = b"version https://git-lfs.github.com/spec/v1"


def safe_path(value: object) -> bool:
    return isinstance(value, str) and bool(value) and "\\" not in value and ":" not in value and not PurePosixPath(value).is_absolute() and ".." not in PurePosixPath(value).parts


def validate(manifest: dict) -> list[str]:
    errors: list[str] = []
    if manifest.get("schema") != "cityprompt.classroom-starter@1":
        errors.append("Unsupported classroom manifest schema")
    entries, dependencies = manifest.get("entries", []), manifest.get("dependencies", [])
    if Counter(row.get("domain") for row in entries) != {"building": 3, "street": 3, "park": 3}:
        errors.append("The first release requires exactly three buildings, streets and parks")
    ids = [row.get("variantId") for row in entries]
    if len(set(ids)) != len(ids) or not all(ids):
        errors.append("Duplicate or empty variant identity")
    dep_ids = [row.get("id") for row in dependencies]
    if len(set(dep_ids)) != len(dep_ids) or not all(dep_ids):
        errors.append("Duplicate or empty dependency identity")
    used = set()
    for row in entries:
        for key in ("archetypeId", "placementId", "revision", "representation", "review"):
            if not row.get(key):
                errors.append(f"{row.get('variantId')}: missing {key}")
        if not row.get("dependencies"):
            errors.append(f"{row.get('variantId')}: missing dependency closure")
        used.update(row.get("dependencies", []))
        if row.get("review", {}).get("runtime") not in {"pending", "partial", "passed"}:
            errors.append(f"{row.get('variantId')}: invalid runtime review")
    for dep in dependencies:
        if dep.get("location") not in {"public", "repository", "artifact"} or not safe_path(dep.get("path")):
            errors.append(f"{dep.get('id')}: unsafe dependency location")
        if not SHA.fullmatch(str(dep.get("sha256", ""))) or not isinstance(dep.get("bytes"), int) or dep["bytes"] <= 0:
            errors.append(f"{dep.get('id')}: invalid byte lock")
    if used != set(dep_ids):
        errors.append(f"Dependency closure mismatch: {sorted(used.symmetric_difference(dep_ids))}")
    return errors


def canonical(manifest: dict) -> str:
    return json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"


def check_copies(manifest: dict, root: Path) -> list[str]:
    expected = canonical(manifest)
    return [f"Stale or missing generated copy: {path.as_posix()}" for path in COPIES
            if not (root / path).is_file() or (root / path).read_text(encoding="utf-8") != expected]


def inspect_dependency(dep: dict, *, root: Path, public_root: Path, artifact_root: Path | None) -> dict:
    location = dep["location"]
    base = {"repository": root, "public": public_root, "artifact": artifact_root}[location]
    result = {"id": dep["id"], "status": "missing", "location": location, "path": dep["path"]}
    if base is None:
        result["status"] = "unpackaged"
        return result
    path = base / dep["path"]
    if not path.is_file():
        return result
    data = path.read_bytes()
    if data.startswith(LFS):
        result["status"] = "unhydrated"
        return result
    if dep.get("normalizeText"):
        data = data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    result["status"] = "verified" if len(data) == dep["bytes"] and hashlib.sha256(data).hexdigest() == dep["sha256"] else "revision-mismatch"
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("check", "sync", "preflight"))
    parser.add_argument("--public-root", type=Path, default=ROOT / "frontend/public")
    parser.add_argument("--artifact-root", type=Path)
    parser.add_argument("--require-release", action="store_true", help="Also require packaged assets and accepted runtime reviews")
    parser.add_argument("--report", type=Path, help="Write a diagnostic JSON report (use an ignored artifact directory)")
    args = parser.parse_args()
    manifest = json.loads((ROOT / SOURCE).read_text(encoding="utf-8"))
    errors = validate(manifest)
    if errors:
        print("\n".join(errors))
        return 1
    if args.command == "sync":
        for copy in COPIES:
            (ROOT / copy).parent.mkdir(parents=True, exist_ok=True)
            (ROOT / copy).write_text(canonical(manifest), encoding="utf-8", newline="\n")
    errors.extend(check_copies(manifest, ROOT))
    results = []
    if args.command == "preflight":
        results = [inspect_dependency(dep, root=ROOT, public_root=args.public_root, artifact_root=args.artifact_root)
                   for dep in manifest["dependencies"]]
        errors.extend(f"{row['status']}: {row['id']}" for row in results if row["status"] != "verified")
    if args.require_release:
        if args.command != "preflight":
            errors.append("--require-release requires preflight; metadata alone cannot qualify a release")
        errors.extend(f"Unpackaged dependency: {dep['id']}" for dep in manifest["dependencies"] if dep["location"] == "artifact")
        errors.extend(f"Runtime review pending: {row['variantId']}" for row in manifest["entries"] if row["review"]["runtime"] != "passed")
    report = {"release": manifest["releaseId"], "command": args.command, "dependencies": results, "errors": errors}
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(canonical(report), encoding="utf-8")
    print(f"{manifest['releaseId']}: {len(manifest['entries'])} exact variants, {len(manifest['dependencies'])} pinned dependencies")
    if results:
        print(json.dumps(dict(Counter(row["status"] for row in results)), sort_keys=True))
    for error in errors:
        print(error)
    return int(bool(errors))


if __name__ == "__main__":
    raise SystemExit(main())
