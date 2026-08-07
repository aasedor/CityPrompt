"""Validate the bounded P0 park object catalogue without opening Blender."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", type=Path, default=Path(__file__).with_name("park_object_kits_p0_spec.json"))
    parser.add_argument("--kit-root", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()

    spec = json.loads(args.spec.read_text(encoding="utf-8"))
    errors: list[str] = []
    assets: list[dict] = []
    for family in spec["families"]:
        family_dir = args.kit_root / family["id"]
        manifest_path = family_dir / "kit_manifest.json"
        if not manifest_path.is_file():
            errors.append(f"missing manifest: {manifest_path}")
            continue
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        expected = {asset["filename"] for asset in family["assets"]}
        declared = set(manifest.get("depthAssets", []))
        if declared != expected:
            errors.append(f"manifest mismatch for {family['id']}: {sorted(declared ^ expected)}")
        if manifest.get("surfaceOwner") != "lego_park_grammar":
            errors.append(f"surface ownership mismatch for {family['id']}")
        if manifest.get("people") is not False or manifest.get("largeBuildings") is not False:
            errors.append(f"forbidden people/building flag for {family['id']}")
        for definition in family["assets"]:
            path = family_dir / definition["filename"]
            if not path.is_file():
                errors.append(f"missing GLB: {path}")
                continue
            header = path.read_bytes()[:4]
            if header != b"glTF":
                errors.append(f"invalid GLB header: {path}")
            size = path.stat().st_size
            if size < 4_000:
                errors.append(f"implausibly small GLB: {path} ({size} bytes)")
            assets.append({"family": family["id"], "id": definition["id"], "filename": path.name, "bytes": size})

    report = {
        "schemaVersion": 1,
        "kitVersion": spec["kitVersion"],
        "familyCount": len(spec["families"]),
        "assetCount": len(assets),
        "bytes": sum(asset["bytes"] for asset in assets),
        "assets": assets,
        "errors": errors,
        "passed": not errors,
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
