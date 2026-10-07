"""Build the full current catalogue for a hosted HTTPS API; no deployment.

Required: explicit VITE_GOOGLE_MAPS_API_KEY and VITE_API_URL, installed locked
frontend dependencies, and the committed LFS objects (or --fetch-lfs).
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

from hosted_assets import ROOT, RepositoryAssets, browser_environment, prepare, stamp_service_worker, validate_packet


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--assets", type=Path, help="Reuse a completed hosted-assets packet")
    parser.add_argument("--output", type=Path, default=ROOT / "frontend/dist")
    parser.add_argument("--work-dir", type=Path, help="New external directory for build evidence and temporary inputs")
    parser.add_argument("--fetch-lfs", action="store_true")
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists():
        raise ValueError("Output already exists; preserve it and choose a new build directory")
    if output == ROOT or output.is_relative_to(ROOT / "frontend/src") or output.is_relative_to(ROOT / "frontend/public"):
        raise ValueError("Build output cannot replace source")
    if args.work_dir:
        work = args.work_dir.resolve()
        if work.exists() or work.is_relative_to(ROOT) or ROOT.is_relative_to(work):
            raise ValueError("Choose a new external work directory")
        work.mkdir(parents=True)
    else:
        work = Path(tempfile.mkdtemp(prefix="cityprompt-hosted-build-"))
    (work / "env").mkdir()
    # Validate before downloads, without printing any credential values.
    env = browser_environment(os.environ, work / "env", work / "unused-public")
    assets = args.assets.resolve() if args.assets else work / "assets"
    if args.assets:
        receipt = validate_packet(assets, RepositoryAssets(ROOT))
    else:
        receipt = prepare(assets, args.fetch_lfs)
    env["CITYPROMPT_PUBLIC_DIR"] = str(assets / "public")
    env["CITYPROMPT_BUILD_DIR"] = str(output)
    frontend = ROOT / "frontend"
    commands = [
        ["node", "scripts/check-catalogue-json.mjs"],
        ["node", "scripts/check-model-contract.mjs"],
        ["node", "scripts/check-policy-map-assets.mjs"],
        ["node", "--test", "scripts/render-style-examples.test.mjs"],
        ["node", "scripts/check-catalogue-delivery.mjs"],
        ["node", "node_modules/typescript/bin/tsc", "--noEmit"],
        ["node", "node_modules/vite/bin/vite.js", "build", "--outDir", str(output)],
        ["node", "scripts/check-bundle-size.js"],
    ]
    for command in commands:
        subprocess.run(command, cwd=frontend, env=env, check=True)
    # Browser-visible commit identity contains no environment values or secrets.
    sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    dirty = bool(subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT).strip())
    version = {"application": "City Prompt", "commit": sha, "catalogue_choices": receipt["choice_count"], "source_dirty": dirty}
    (output / "version.json").write_text(json.dumps(version) + "\n", encoding="utf-8")
    identity = (sha.encode() + (assets / "assets.json").read_bytes()
                + (output / ".vite/manifest.json").read_bytes())
    worker = output / "sw.js"
    worker.write_text(stamp_service_worker(worker.read_text(encoding="utf-8"), identity), encoding="utf-8")
    # Refuse accidentally publishing LFS placeholders or private configuration.
    for path in output.rglob("*"):
        if not path.is_file():
            continue
        if path.name.startswith(".env"):
            raise ValueError("Environment file in static output")
        if path.stat().st_size < 300 and path.read_bytes().startswith(b"version https://git-lfs.github.com/spec/v1"):
            raise ValueError(f"Unhydrated LFS pointer in build: {path.relative_to(output)}")
    # Some desktop temp cleaners remove an empty env-only work directory during
    # a long build using --assets. Keep receipt writing independent of that.
    work.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(assets / "assets.json", work / "delivery-assets.json")
    (work / "build-receipt.json").write_text(json.dumps({**version, "output": str(output),
        "asset_bytes": receipt["bytes"],
        "release_approval": False}, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(output), "receipt": str(work / "build-receipt.json"), **version}))


if __name__ == "__main__":
    main()
