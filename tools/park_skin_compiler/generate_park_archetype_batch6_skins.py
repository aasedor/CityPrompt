"""Generate the ten exact-reference PBR skin sets in park LEGO batch 6."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from compile_neighborhood_park_skins import REPO_ROOT
from generate_park_archetype_skins import generate, validate_schedule


SCHEDULE_PATH = Path(__file__).with_name("park_archetype_batch6_skin_sources.json")
DEFAULT_OUT = REPO_ROOT / "frontend/public/park-skins"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--archetype", default="all")
    parser.add_argument("--source-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    schedule = json.loads(SCHEDULE_PATH.read_text(encoding="utf-8"))
    source_root = args.source_root.resolve()
    errors = validate_schedule(schedule, source_root)
    if errors:
        raise SystemExit("\n".join(errors))
    if args.dry_run:
        count = schedule["expectedArchetypeCount"]
        print(f"archetypes={count} roles=6 api_calls=0 source_pixels_projected=false")
        return
    generate(schedule, args.out.resolve(), args.archetype, source_root)


if __name__ == "__main__":
    main()
