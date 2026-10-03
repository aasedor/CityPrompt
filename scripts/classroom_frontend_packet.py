#!/usr/bin/env python3
"""Build a finite, verified static web packet outside the repository.

Uses installed frontend dependencies. No generation, downloads or deployment.
Provide browser-only VITE_* variables explicitly; shared developer dotenv files
are not loaded. --candidate preserves open runtime reviews in the output receipt.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.classroom_release import LFS, safe_path

BROWSER_ENV = {"VITE_GOOGLE_MAPS_API_KEY", "VITE_MAPBOX_TOKEN", "VITE_SENTRY_DSN"}
TEXT_EXTENSIONS = {".js", ".json", ".svg", ".txt"}


def copy_verified(row, source_root: Path, destination_root: Path):
    path = row["path"]
    if not safe_path(path) or not path.startswith("frontend/public/"):
        raise ValueError("Unsafe runtime asset path")
    relative = Path(path.removeprefix("frontend/public/"))
    source = (source_root / relative).resolve()
    target = (destination_root / relative).resolve()
    if not source.is_relative_to(source_root.resolve()) or not target.is_relative_to(destination_root.resolve()):
        raise ValueError("Runtime asset escaped its source or target")
    if not source.is_file():
        raise ValueError(f"Required runtime file is missing: {relative.as_posix()}")
    if target.exists():
        raise ValueError("Runtime asset would replace a generated build file")
    target.parent.mkdir(parents=True, exist_ok=True)
    digest, count = hashlib.sha256(), 0
    with source.open("rb") as handle, target.open("xb") as output:
        first = handle.read(1024 * 1024)
        if first.startswith(LFS):
            raise ValueError(f"Required LFS object is not hydrated: {relative.as_posix()}")
        if not row.get("lfsOid") and source.suffix.lower() in TEXT_EXTENSIONS:
            # The inventory locks text independently of checkout line endings.
            data = (first + handle.read()).replace(b"\r\n", b"\n").replace(b"\r", b"\n")
            output.write(data)
            digest.update(data)
            count = len(data)
        else:
            block = first
            while block:
                output.write(block)
                digest.update(block)
                count += len(block)
                block = handle.read(1024 * 1024)
    sha = digest.hexdigest()
    if count != row["logicalBytes"] or (row.get("lfsOid") and sha != row["lfsOid"]):
        raise ValueError(f"Runtime asset differs from its pinned revision: {relative.as_posix()}")
    return {"path": relative.as_posix(), "bytes": count, "sha256": sha}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--public-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--candidate", action="store_true")
    args = parser.parse_args()
    output, public = args.output.resolve(), args.public_root.resolve()
    if output.exists() or output.is_relative_to(ROOT) or output.is_relative_to(public) or public.is_relative_to(output):
        parser.error("Choose a new packet directory outside source and public assets")
    if not os.environ.get("VITE_GOOGLE_MAPS_API_KEY"):
        parser.error("Set the restricted browser VITE_GOOGLE_MAPS_API_KEY for this candidate")
    if not args.candidate and subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT).strip():
        parser.error("Freeze a clean source revision before preparing a release packet")
    # Require an up-to-date complete inventory before copying any large assets.
    subprocess.run(["node", "frontend/scripts/generate-runtime-asset-manifest.mjs", "--tracked-metadata", "--check"], cwd=ROOT, check=True)
    inventory = json.loads(subprocess.check_output(["node", "frontend/scripts/generate-runtime-asset-manifest.mjs", "--tracked-metadata", "--list-required-files-json"], cwd=ROOT))
    output.parent.mkdir(parents=True, exist_ok=True)
    if shutil.disk_usage(output.parent).free < sum(row["logicalBytes"] for row in inventory) + 2 * 1024 ** 3:
        parser.error("Insufficient disk for the packet plus a 2 GiB reserve")
    output.mkdir()
    (output / "empty-public").mkdir()
    (output / "empty-env").mkdir()
    preflight = [sys.executable, "scripts/classroom_release.py", "preflight", "--public-root", str(public), "--report", str(output / "starter-receipt.json")]
    if not args.candidate:
        preflight.append("--require-release")
    subprocess.run(preflight, cwd=ROOT, check=True)
    # Vite must not copy the enormous historical experiment tree or inherit a
    # developer API origin. Browser keys are the only approved build-time values.
    env = {key: value for key, value in os.environ.items() if not key.startswith("VITE_")}
    env.update({key: os.environ[key] for key in BROWSER_ENV if key in os.environ})
    env.update(VITE_API_URL="", VITE_ENV_DIR=str(output / "empty-env"), CITYPROMPT_PUBLIC_DIR=str(output / "empty-public"))
    frontend = ROOT / "frontend"
    with (output / "build.log").open("wb") as log:
        subprocess.run(["node", "node_modules/typescript/bin/tsc", "--noEmit"], cwd=frontend, env=env, stdout=log, stderr=subprocess.STDOUT, check=True)
        subprocess.run(["node", "node_modules/vite/bin/vite.js", "build", "--outDir", str(output / "www")], cwd=frontend, env=env, stdout=log, stderr=subprocess.STDOUT, check=True)
    assets = [copy_verified(row, public, output / "www") for row in inventory]
    for name in ("Dockerfile.web", "nginx.conf"):
        shutil.copyfile(ROOT / "deployment/classroom" / name, output / name)
    # This Docker build context includes only the reviewed static delivery.
    (output / ".dockerignore").write_text("*\n!www/\n!www/**\n!nginx.conf\n!Dockerfile.web\n", encoding="utf-8")
    receipt = {"schema": "cityprompt.frontend-packet@1", "candidate_only": args.candidate,
               "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
               "source_dirty": bool(subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT).strip()),
               "assets": assets, "bytes": sum(row["bytes"] for row in assets)}
    (output / "packet.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"assets": len(assets), "bytes": receipt["bytes"], "candidate_only": args.candidate, "output": str(output)}))


if __name__ == "__main__":
    main()
