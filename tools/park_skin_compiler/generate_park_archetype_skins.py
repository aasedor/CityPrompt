"""Generate batch-2 exact-archetype stationary PBR park skin libraries."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image

try:
    from .compile_neighborhood_park_skins import REPO_ROOT, crop_pixels, derive_ao, derive_normal, derive_roughness
    from .generate_adaptive_urban_materials import (
        ROLES,
        asphalt_pattern,
        lawn_pattern,
        paver_pattern,
        planting_pattern,
        safety_pattern,
        stationary_base,
        timber_pattern,
    )
except ImportError:
    from compile_neighborhood_park_skins import REPO_ROOT, crop_pixels, derive_ao, derive_normal, derive_roughness
    from generate_adaptive_urban_materials import (
        ROLES,
        asphalt_pattern,
        lawn_pattern,
        paver_pattern,
        planting_pattern,
        safety_pattern,
        stationary_base,
        timber_pattern,
    )


SCHEDULE_PATH = Path(__file__).with_name("park_archetype_batch2_skin_sources.json")
DEFAULT_OUT = REPO_ROOT / "frontend/public/park-skins"


def load_schedule() -> dict:
    return json.loads(SCHEDULE_PATH.read_text(encoding="utf-8"))


def validate_schedule(schedule: dict, source_root: Path = REPO_ROOT) -> list[str]:
    errors: list[str] = []
    if schedule.get("sourcePixelsProjected") is not False:
        errors.append("source photographs must not be projected onto geometry")
    if len(schedule.get("archetypes", {})) != 5:
        errors.append("expected five archetype skin schedules")
    for slug, item in schedule.get("archetypes", {}).items():
        source = source_root / item.get("source", "")
        if not source.exists():
            errors.append(f"{slug}: missing source")
        if set(item.get("crops", {})) != set(ROLES):
            errors.append(f"{slug}: every adaptive role requires a crop")
        for role, crop in item.get("crops", {}).items():
            left, top, right, bottom = crop
            if not (0 <= left < right <= 1 and 0 <= top < bottom <= 1):
                errors.append(f"{slug}/{role}: invalid normalized crop")
    return errors


def synthesize_role(role: str, crop: Image.Image, seed: int, pattern: str) -> Image.Image:
    base = stationary_base(crop, role, seed)
    if pattern == "paver":
        result = paver_pattern(base, seed)
    elif pattern == "lawn":
        result = lawn_pattern(base)
    elif pattern == "asphalt":
        result = asphalt_pattern(base, seed)
    elif pattern == "planting":
        result = planting_pattern(base, seed)
    elif pattern == "safety":
        result = safety_pattern(base, seed)
    elif pattern == "timber":
        result = timber_pattern(base, seed)
    else:
        raise ValueError(pattern)
    # Reference statistics set the palette; restrained variance keeps the
    # stationary tile from reading as a blurred photograph at parcel scale.
    factors = {"paver": 0.42, "lawn": 0.58, "asphalt": 0.44, "planting": 0.76, "safety": 0.30, "timber": 0.56}
    array = np.asarray(result, dtype=np.float64)
    mean = array.reshape(-1, 3).mean(axis=0)
    array = mean + (array - mean) * factors[role]
    return Image.fromarray(np.clip(array, 0, 255).astype(np.uint8), mode="RGB")


def generate(
    schedule: dict,
    output_root: Path,
    selected: str = "all",
    source_root: Path = REPO_ROOT,
) -> None:
    defaults = schedule["materialDefaults"]
    items = schedule["archetypes"].items()
    if selected != "all":
        if selected not in schedule["archetypes"]:
            raise SystemExit(f"unknown archetype slug: {selected}")
        items = [(selected, schedule["archetypes"][selected])]
    for archetype_index, (slug, item) in enumerate(items):
        source = Image.open(source_root / item["source"]).convert("RGB")
        target = output_root / slug / "adaptive-v1"
        manifest = {
            "schemaVersion": 1,
            "archetype": slug,
            "source": item["source"],
            "method": schedule["method"],
            "apiCalls": 0,
            "sourcePixelsProjected": False,
            "materials": {},
        }
        for role_index, role in enumerate(ROLES):
            crop_box = item["crops"][role]
            pixels = crop_pixels(source, crop_box)
            crop = source.crop(pixels)
            spec = defaults[role]
            seed = 12011 + archetype_index * 1301 + role_index * 503
            pattern = item.get("patterns", {}).get(role, role)
            albedo = synthesize_role(role, crop, seed, pattern)
            normal = derive_normal(albedo, float(spec["normalStrength"]))
            roughness = derive_roughness(albedo, float(spec["roughness"]))
            ao = derive_ao(albedo)
            role_dir = target / role
            role_dir.mkdir(parents=True, exist_ok=True)
            crop.save(role_dir / "source_crop.jpg", quality=92)
            albedo.save(role_dir / "albedo.jpg", quality=92, optimize=True)
            normal.save(role_dir / "normal.png", optimize=True)
            roughness.save(role_dir / "roughness.jpg", quality=90, optimize=True)
            ao.save(role_dir / "ao.jpg", quality=90, optimize=True)
            manifest["materials"][role] = {
                "cropNormalized": crop_box,
                "cropPixels": pixels,
                "metresPerTile": spec["metresPerTile"],
                "pattern": pattern,
                "files": {
                    "sourceCrop": f"{role}/source_crop.jpg",
                    "albedo": f"{role}/albedo.jpg",
                    "normal": f"{role}/normal.png",
                    "roughness": f"{role}/roughness.jpg",
                    "ao": f"{role}/ao.jpg"
                },
            }
        target.mkdir(parents=True, exist_ok=True)
        (target / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        print(f"wrote {target / 'manifest.json'}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--archetype", default="all")
    parser.add_argument("--source-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    schedule = load_schedule()
    source_root = args.source_root.resolve()
    errors = validate_schedule(schedule, source_root)
    if errors:
        raise SystemExit("\n".join(errors))
    if args.dry_run:
        print(f"archetypes={len(schedule['archetypes'])} roles={len(ROLES)} api_calls=0 source_pixels_projected=false")
        return
    generate(schedule, args.out, args.archetype, source_root)


if __name__ == "__main__":
    main()
