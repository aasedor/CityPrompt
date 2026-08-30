#!/usr/bin/env python3
"""Reject oversized ordinary Git blobs and malformed Git LFS entries.

The check inspects committed blobs, not smudged working-tree files. A hydrated
LFS object therefore remains valid because the Git object is still a compact
pointer.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

DEFAULT_MAX_BYTES = 1024 * 1024
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
    if explicit:
        return explicit

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
        if not is_pointer and len(blob) > max_bytes:
            failures.append(
                f"{path}: ordinary Git blob is {len(blob)} bytes; "
                f"limit is {max_bytes} bytes (use Git LFS, artifact storage, or split it)"
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
        f"ordinary blob limit={args.max_bytes} bytes."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
