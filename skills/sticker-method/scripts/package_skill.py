#!/usr/bin/env python3
"""Create a deterministic shareable ZIP containing one skill folder."""

from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from pathlib import Path


EXCLUDED_PARTS = {"__pycache__", ".pytest_cache", ".DS_Store"}
EXCLUDED_SUFFIXES = {".pyc", ".pyo", ".zip"}
FIXED_TIME = (2020, 1, 1, 0, 0, 0)


def included(path: Path) -> bool:
    return not any(part in EXCLUDED_PARTS for part in path.parts) and path.suffix not in EXCLUDED_SUFFIXES


def package(skill_dir: Path, output: Path) -> dict[str, object]:
    skill_dir = skill_dir.resolve()
    output = output.resolve()
    if not (skill_dir / "SKILL.md").is_file():
        raise ValueError(f"missing SKILL.md: {skill_dir}")
    files = sorted(path for path in skill_dir.rglob("*") if path.is_file() and included(path))
    if not files:
        raise ValueError("skill has no files")
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in files:
            relative = Path(skill_dir.name) / path.relative_to(skill_dir)
            info = zipfile.ZipInfo(str(relative).replace("\\", "/"), FIXED_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    digest = hashlib.sha256(output.read_bytes()).hexdigest()
    return {"status": "pass", "output": str(output), "sha256": digest, "file_count": len(files)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skill-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = package(args.skill_dir, args.output)
    except ValueError as exc:
        print(json.dumps({"status": "fail", "error": str(exc)}, indent=2))
        return 1
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
