#!/usr/bin/env python3
"""Package generated facade GLBs with UASTC KTX2 textures and a new manifest."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import struct
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path


TRANSCODER_PATH = "https://cdn.jsdelivr.net/npm/three@0.170.0/examples/jsm/libs/basis/"


def packaged_manifest(source: dict, *, assembled_packaged: bool = True) -> dict:
    payload = json.loads(json.dumps(source))
    payload["created_at"] = datetime.now(timezone.utc).isoformat()
    payload["texture_delivery"] = {
        "container": "KTX2",
        "basis_mode": "UASTC",
        "mipmaps": True,
        "zstd_level": 18,
        "near_atlas": "2048-4096 px source, physical glazing LOD",
        "city_atlas": "1024 px source, baked facade LOD",
        "runtime_transcoder_path": TRANSCODER_PATH,
    }
    payload["package_profile"] = "full_family" if assembled_packaged else "lego_modules"
    for module in payload.get("modules", []):
        module["texture_container"] = "KTX2/UASTC"
    if payload.get("assembled"):
        if assembled_packaged:
            payload["assembled"]["texture_container"] = "KTX2/UASTC"
            payload["assembled"]["packaged"] = True
        else:
            payload["assembled_master"] = {
                **payload["assembled"],
                "texture_container": "WebP master family",
                "packaged": False,
            }
            payload["assembled"] = None
    return payload


def has_ktx2_texture(path: Path) -> bool:
    """Fast GLB JSON-chunk check used by resumable release packaging."""
    if not path.exists() or path.stat().st_size < 20:
        return False
    with path.open("rb") as stream:
        header = stream.read(20)
        if header[:4] != b"glTF":
            return False
        json_length = struct.unpack_from("<I", header, 12)[0]
        payload = stream.read(json_length)
    return b"KHR_texture_basisu" in payload


def _run_uastc(
    npx: str,
    source: Path,
    output: Path,
    *,
    level: int,
    jobs: int,
    ktx_bin: Path | None,
) -> None:
    environment = os.environ.copy()
    if ktx_bin:
        if not ktx_bin.exists():
            raise SystemExit(f"--ktx-bin does not exist: {ktx_bin}")
        environment["PATH"] = str(ktx_bin.parent) + os.pathsep + environment.get("PATH", "")
    with tempfile.TemporaryDirectory(prefix="lego-ktx2-") as temp_dir:
        normalized = Path(temp_dir) / "normalized-png.glb"
        commands = [
            [
                npx, "--yes", "@gltf-transform/cli", "png",
                str(source), str(normalized),
                "--formats", "webp", "--effort", "70",
            ],
            [
                npx, "--yes", "@gltf-transform/cli", "uastc",
                str(normalized), str(output),
                "--level", str(level),
                "--rdo", "--rdo-lambda", "0.65",
                "--zstd", "18", "--jobs", str(jobs),
            ],
        ]
        for command in commands:
            result = subprocess.run(
                command, text=True, capture_output=True, encoding="utf-8", errors="replace",
                env=environment,
            )
            if result.returncode:
                detail = "\n".join((result.stdout + "\n" + result.stderr).splitlines()[-30:])
                raise SystemExit(f"KTX2 packaging failed for {source.name}:\n{detail}")


def package(
    family_dir: Path,
    output_dir: Path,
    *,
    level: int,
    jobs: int,
    ktx_bin: Path | None = None,
    resume: bool = False,
    include_assembled: bool = True,
) -> Path:
    manifests = sorted(family_dir.glob("*_manifest.json"))
    if len(manifests) != 1:
        raise SystemExit(f"expected one *_manifest.json in {family_dir}, found {len(manifests)}")
    source_manifest = json.loads(manifests[0].read_text(encoding="utf-8"))
    output_dir.mkdir(parents=True, exist_ok=True)
    npx = shutil.which("npx") or shutil.which("npx.cmd")
    if not npx:
        raise SystemExit("npx is required to run @gltf-transform/cli")

    filenames = [module["filename"] for module in source_manifest.get("modules", [])]
    if include_assembled and source_manifest.get("assembled"):
        filenames.append(source_manifest["assembled"]["filename"])
    for filename in dict.fromkeys(filenames):
        source = family_dir / filename
        if not source.exists():
            raise SystemExit(f"manifest GLB is missing: {source}")
        target = output_dir / filename
        if resume and has_ktx2_texture(target):
            print(f"[package_ktx2] {filename} (resume: already KTX2)", flush=True)
            continue
        print(f"[package_ktx2] {filename}", flush=True)
        _run_uastc(npx, source, target, level=level, jobs=jobs, ktx_bin=ktx_bin)

    for pattern in ("*.png", "*.jpg", "*.webp", "validation_report.json"):
        for source in family_dir.glob(pattern):
            shutil.copy2(source, output_dir / source.name)

    if not include_assembled and source_manifest.get("assembled"):
        # A prior interrupted/full pass may have left a non-KTX assembled GLB
        # in the target. Remove that ambiguous artifact; the packaged manifest
        # explicitly directs standalone viewers to the WebP master family.
        (output_dir / source_manifest["assembled"]["filename"]).unlink(missing_ok=True)

    target_manifest = output_dir / manifests[0].name
    target_manifest.write_text(
        json.dumps(packaged_manifest(source_manifest, assembled_packaged=include_assembled), indent=2) + "\n",
        encoding="utf-8",
    )
    return target_manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("family_dir", type=Path)
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--level", type=int, choices=range(5), default=4)
    parser.add_argument("--jobs", type=int, default=8)
    parser.add_argument("--ktx-bin", type=Path, default=None,
                        help="optional path to Khronos ktx.exe when it is not on PATH")
    parser.add_argument("--resume", action="store_true", help="skip target GLBs that already require KHR_texture_basisu")
    parser.add_argument("--skip-assembled", action="store_true",
                        help="package only LEGO modules; keep the large assembled hero as a separate optional asset")
    args = parser.parse_args()
    family_dir = args.family_dir.resolve()
    output = (args.output or family_dir / "ktx2").resolve()
    print(package(
        family_dir, output, level=args.level, jobs=max(1, args.jobs),
        ktx_bin=args.ktx_bin.resolve() if args.ktx_bin else None,
        resume=args.resume,
        include_assembled=not args.skip_assembled,
    ))


if __name__ == "__main__":
    main()
