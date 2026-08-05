"""Generate stationary PBR skins for the regulation-park pilot families."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from generate_adaptive_urban_materials import ROLES
from generate_park_archetype_skins import generate
from compile_neighborhood_park_skins import REPO_ROOT


SCHEDULE_PATH = Path(__file__).with_name("regulation_park_skin_sources.json")
DEFAULT_OUT = REPO_ROOT / "frontend/public/park-skins"


def load_and_validate() -> dict:
    schedule = json.loads(SCHEDULE_PATH.read_text(encoding="utf-8"))
    errors: list[str] = []
    if schedule.get("sourcePixelsProjected") is not False:
        errors.append("source photographs must not be projected onto geometry")
    if not schedule.get("archetypes"):
        errors.append("at least one regulation archetype skin is required")
    for slug, item in schedule.get("archetypes", {}).items():
        if not (REPO_ROOT / item.get("source", "")).exists():
            errors.append(f"{slug}: missing source")
        if set(item.get("crops", {})) != set(ROLES):
            errors.append(f"{slug}: every adaptive role requires a crop")
        for role, crop in item.get("crops", {}).items():
            left, top, right, bottom = crop
            if not (0 <= left < right <= 1 and 0 <= top < bottom <= 1):
                errors.append(f"{slug}/{role}: invalid normalized crop")
    if errors:
        raise SystemExit("\n".join(errors))
    return schedule


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--archetype", default="all")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    schedule = load_and_validate()
    if args.dry_run:
        print(f"archetypes={len(schedule['archetypes'])} roles={len(ROLES)} api_calls=0 source_pixels_projected=false")
        return
    generate(schedule, args.out, args.archetype)


if __name__ == "__main__":
    main()
