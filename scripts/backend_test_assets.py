"""Hydrate only the hash-locked binary fixtures exercised by backend pytest.

The repository's default historical-LFS exclusion remains unchanged. No asset
generation, deployment or global Git configuration changes occur here.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def fixture_assets(root: Path = ROOT) -> dict[str, str]:
    assets: dict[str, str] = {}

    def read(relative):
        return json.loads((root / relative).read_text(encoding="utf-8"))

    def add(path, sha):
        target = (root / path).resolve()
        if not target.is_relative_to(root.resolve()):
            raise ValueError("Test asset escaped repository")
        relative = target.relative_to(root.resolve()).as_posix()
        if relative in assets and assets[relative] != sha:
            raise ValueError("Conflicting test asset hashes")
        assets[relative] = sha

    starter = read("seed/classroom-release/starter-v1.json")
    dependencies = {d["id"]: d for d in starter["dependencies"]}
    for row in read("seed/classroom-release/model-bindings.json")["entries"]:
        dep = dependencies[row["modelDependency"]]
        add(dep["path"], dep["sha256"])

    base = Path("seed/model-library/rlasm-architectural-clay")
    for family in read(base / "house-flex-pilot-v001.json")["families"]:
        for assembly in family["assemblies"]:
            add(base / assembly["path"], assembly["sha256"])

    for entry in read("seed/claude-five-trial/library.json")["entries"]:
        add(Path("seed/claude-five-trial") / entry["model"]["path"], entry["model"]["sha256"])
        for ref in entry["references"]:
            add(ref["repo_path"], ref["sha256"])

    for entry in read("frontend/src/features/parks/detailCatalogueExtras.json"):
        if entry.get("sourceKit") == "traffic-safety-v1":
            add(Path("frontend/public") / entry["url"].lstrip("/"), entry["sha256"])
    if not assets or len(assets) > 80:
        raise ValueError("Review unexpected backend fixture batch size")
    return assets


def verify(root: Path, assets: dict[str, str]) -> None:
    for relative, sha in assets.items():
        data = (root / relative).read_bytes()
        if data.startswith(b"version https://git-lfs.github.com/spec/v1"):
            raise ValueError(f"Unhydrated backend test asset: {relative}")
        if hashlib.sha256(data).hexdigest() != sha:
            raise ValueError(f"Changed backend test asset: {relative}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fetch-lfs", action="store_true")
    args = parser.parse_args()
    assets = fixture_assets()
    if args.fetch_lfs:
        subprocess.run(["git", "lfs", "pull", "--include=" + ",".join(sorted(assets)), "--exclude="], cwd=ROOT, check=True)
    verify(ROOT, assets)
    print(f"Verified {len(assets)} exact backend test assets")


if __name__ == "__main__":
    main()
