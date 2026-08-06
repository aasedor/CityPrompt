"""Generate the thirty exact-reference PBR skin sets that close Batch 14 variants."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from compile_neighborhood_park_skins import REPO_ROOT
from generate_park_archetype_skins import generate, validate_schedule

SCHEDULE_PATH = Path(__file__).with_name("park_archetype_batch15_skin_sources.json")
DEFAULT_OUT = REPO_ROOT / "frontend/public/park-skins"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--archetype", default="all")
    parser.add_argument("--source-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    schedule = json.loads(SCHEDULE_PATH.read_text(encoding="utf-8"))
    default_crops = schedule.pop("defaultCrops")
    for item in schedule["archetypes"].values():
        item.setdefault("crops", default_crops)
    source_root = args.source_root.resolve()
    errors = validate_schedule(schedule, source_root)
    if errors:
        raise SystemExit("\n".join(errors))
    if args.dry_run:
        print(f"archetypes={schedule['expectedArchetypeCount']} roles=6 api_calls=0 source_pixels_projected=false")
        return
    generate(schedule, args.out.resolve(), args.archetype, source_root)


if __name__ == "__main__":
    main()
