"""Prepare intrinsic Sticker Method skins for Neighborhood Park v0.

The exact park image supplies palette and material statistics only. The shared
park skin generator synthesizes stationary, geometry-free, shadow-neutral PBR
tiles, so paths, timber members and planting remain physical construction.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from PIL import Image, ImageOps


HERE = Path(__file__).resolve().parent
REPO_ROOT = Path(__file__).resolve().parents[4]
SKIN_TOOL = REPO_ROOT / "tools" / "park_skin_compiler"
DEFAULT_OUTPUT = REPO_ROOT / "frontend" / "public" / "park-skins"

if str(SKIN_TOOL) not in sys.path:
    sys.path.insert(0, str(SKIN_TOOL))

from generate_park_archetype_skins import generate, validate_schedule  # noqa: E402
from compile_neighborhood_park_skins import derive_ao, derive_normal, derive_roughness  # noqa: E402


def prepare_object_roles(schedule: dict, output_root: Path) -> None:
    target = output_root / "neighborhood-park-rustic-v0" / "adaptive-v1"
    manifest_path = target / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    source = schedule["archetypes"]["neighborhood-park-rustic-v0"]["source"]
    for role, spec in schedule["objectMaterialRoles"].items():
        base_role = spec["baseRole"]
        base_dir = target / base_role
        role_dir = target / role
        role_dir.mkdir(parents=True, exist_ok=True)
        base = Image.open(base_dir / "albedo.jpg").convert("RGB")
        albedo = ImageOps.colorize(
            ImageOps.grayscale(base), black=spec["dark"], white=spec["light"]
        ).convert("RGB")
        crop = Image.open(base_dir / "source_crop.jpg").convert("RGB")
        normal = derive_normal(albedo, float(spec["normalStrength"]))
        roughness = derive_roughness(albedo, float(spec["roughness"]))
        ao = derive_ao(albedo)
        crop.save(role_dir / "source_crop.jpg", quality=92)
        albedo.save(role_dir / "albedo.jpg", quality=92, optimize=True)
        normal.save(role_dir / "normal.png", optimize=True)
        roughness.save(role_dir / "roughness.jpg", quality=90, optimize=True)
        ao.save(role_dir / "ao.jpg", quality=90, optimize=True)
        manifest["materials"][role] = {
            "source": source,
            "derivedFromIntrinsicRole": base_role,
            "metresPerTile": spec["metresPerTile"],
            "pattern": f"{role}_intrinsic",
            "files": {
                "sourceCrop": f"{role}/source_crop.jpg",
                "albedo": f"{role}/albedo.jpg",
                "normal": f"{role}/normal.png",
                "roughness": f"{role}/roughness.jpg",
                "ao": f"{role}/ao.jpg",
            },
        }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    schedule = json.loads((HERE / "skin-sources.json").read_text(encoding="utf-8"))
    errors = validate_schedule(schedule, REPO_ROOT)
    if errors:
        raise SystemExit("\n".join(errors))
    if args.dry_run:
        print("archetypes=1 roles=9 api_calls=0 source_pixels_projected=false")
        return 0
    generate(schedule, args.out.resolve(), "all", REPO_ROOT)
    prepare_object_roles(schedule, args.out.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
