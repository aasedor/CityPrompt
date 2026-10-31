#!/usr/bin/env python3
"""Reject oversized ordinary Git blobs and malformed Git LFS entries.

The check inspects committed blobs, not smudged working-tree files. A hydrated
LFS object therefore remains valid because the Git object is still a compact
pointer.

Scope: a pull request audits its whole delta against the base branch; a push
audits every commit since the push's previous tip (``--base``), falling back to
``HEAD^`` only when that tip is unknown (branch creation, rewritten history).
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

DEFAULT_MAX_BYTES = 1024 * 1024
# These editable source datasets are imported without LFS hydration. Preserve
# geographic precision and readable catalogue metadata with exact-path budgets;
# runtime models, imagery and arbitrary JSON keep the ordinary limit.
SOURCE_JSON_BUDGETS = {
    "frontend/src/data/buildingArchetypes.json": (3 * 1024 * 1024, "archetypes"),
    # Expanded native layouts and their generated addressability index remain
    # readable source metadata. Exact-path caps do not exempt binary assets or
    # arbitrary JSON, and explicitly stricter callers still take precedence.
    "frontend/src/data/nativeParks.json": (1280 * 1024, "layouts"),
    "backend/app/data/nativeParks.json": (1280 * 1024, "layouts"),
    "frontend/src/data/runtimeAssetManifest.json": (1536 * 1024, "explicitReferences"),
    "frontend/src/features/policyPlans/data/east-calgaryUrbanForm.json": (2 * 1024 * 1024, "features"),
    "frontend/src/features/policyPlans/data/heritageUrbanForm.json": (2 * 1024 * 1024, "features"),
    "frontend/src/features/policyPlans/data/south-shaganappiUrbanForm.json": (2 * 1024 * 1024, "features"),
    "frontend/src/features/policyPlans/data/west-elbowUrbanForm.json": (2 * 1024 * 1024, "features"),
    # Official transportation and transit vector layers are editable GeoJSON
    # sources served from /policy-maps/transport-vectors-v1 and imported by
    # their unit tests, so they stay ordinary readable blobs with exact caps.
    "frontend/public/policy-maps/transport-vectors-v1/5a.geojson": (8 * 1024 * 1024, "features"),
    "frontend/public/policy-maps/transport-vectors-v1/service-routes.geojson": (6656 * 1024, "features"),
    "frontend/public/policy-maps/transport-vectors-v1/service-stops.geojson": (3 * 1024 * 1024, "features"),
    # The native street pilot registry is a top-level list of pilots (collection
    # None). The backend copy must stay byte-identical to the frontend source.
    "frontend/src/data/nativeStreetPilots.json": (2560 * 1024, None),
    "backend/app/data/nativeStreetPilots.json": (2560 * 1024, None),
}
LFS_HEADER = b"version https://git-lfs.github.com/spec/v1\n"


def git(repo: Path, *args: str, check: bool = True) -> bytes:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if check and result.returncode:
        raise RuntimeError(result.stderr.decode("utf-8", errors="replace").strip())
    return result.stdout


def resolve_base(repo: Path, explicit: str | None) -> str | None:
    if explicit and explicit.strip("0"):
        if git(repo, "rev-parse", "--verify", "--quiet", f"{explicit}^{{commit}}", check=False):
            return explicit
        # The previous tip of a rewritten or shallow history cannot be diffed.
        print(f"Base {explicit} is not a reachable commit; auditing the PR base or HEAD^ instead.", file=sys.stderr)

    github_base = os.environ.get("GITHUB_BASE_REF")
    if github_base:
        remote_base = f"origin/{github_base}"
        if git(repo, "rev-parse", "--verify", "--quiet", remote_base, check=False):
            return remote_base

    if git(repo, "rev-parse", "--verify", "--quiet", "HEAD^", check=False):
        return "HEAD^"
    return None


def changed_paths(repo: Path, base: str | None) -> list[str]:
    if base is None:
        payload = git(repo, "ls-files", "-z")
    else:
        payload = git(
            repo,
            "diff",
            "--name-only",
            "--diff-filter=AMCR",
            "-z",
            f"{base}...HEAD",
        )
    return sorted(
        {
            item.decode("utf-8", errors="surrogateescape")
            for item in payload.split(b"\0")
            if item
        }
    )


def blob_bytes(repo: Path, path: str) -> bytes:
    return git(repo, "show", f"HEAD:{path}")


def lfs_tracked(repo: Path, path: str) -> bool:
    value = git(repo, "check-attr", "filter", "--", path).decode(
        "utf-8", errors="replace"
    )
    return value.rstrip().endswith(": lfs")


def valid_lfs_pointer(blob: bytes) -> bool:
    if not blob.startswith(LFS_HEADER):
        return False
    lines = blob.decode("ascii", errors="ignore").splitlines()
    return (
        len(lines) >= 3
        and lines[1].startswith("oid sha256:")
        and len(lines[1].removeprefix("oid sha256:")) == 64
        and lines[2].startswith("size ")
        and lines[2].removeprefix("size ").isdigit()
    )


def has_expected_collection(source: object, collection: str | None) -> bool:
    """A named budget applies only to the dataset shape it was granted for."""
    if collection is None:
        return isinstance(source, list)
    return isinstance(source, dict) and isinstance(source.get(collection), list)


def audit_paths(repo: Path, paths: list[str], max_bytes: int) -> list[str]:
    failures: list[str] = []
    for path in paths:
        try:
            blob = blob_bytes(repo, path)
        except RuntimeError as exc:
            failures.append(f"{path}: cannot read committed blob ({exc})")
            continue

        tracked_by_lfs = lfs_tracked(repo, path)
        is_pointer = tracked_by_lfs and valid_lfs_pointer(blob)
        if tracked_by_lfs and not is_pointer:
            failures.append(
                f"{path}: filter=lfs but committed blob is not a valid LFS pointer"
            )
        limit = max_bytes
        if max_bytes == DEFAULT_MAX_BYTES and path in SOURCE_JSON_BUDGETS:
            try:
                source = json.loads(blob)
                budget, collection = SOURCE_JSON_BUDGETS[path]
                if has_expected_collection(source, collection):
                    limit = budget
            except (ValueError, UnicodeDecodeError):
                pass
        if not is_pointer and len(blob) > limit:
            failures.append(
                f"{path}: ordinary Git blob is {len(blob)} bytes; "
                f"limit is {limit} bytes (use Git LFS, artifact storage, or split it)"
            )
    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", help="Base revision; defaults to PR base or HEAD^")
    parser.add_argument("--max-bytes", type=int, default=DEFAULT_MAX_BYTES)
    parser.add_argument(
        "--path",
        action="append",
        dest="paths",
        help="Audit an explicit committed path; repeatable",
    )
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    args = parser.parse_args()

    repo = args.repo.resolve()
    base = resolve_base(repo, args.base)
    paths = sorted(set(args.paths or changed_paths(repo, base)))
    failures = audit_paths(repo, paths, args.max_bytes)

    if failures:
        print("Repository blob policy failed:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1

    scope = f"{len(paths)} changed path(s)" if base else f"{len(paths)} tracked path(s)"
    print(
        f"Repository blob policy passed for {scope}; "
        f"ordinary blob limit={args.max_bytes} bytes; named source JSON budgets apply at the default limit."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
