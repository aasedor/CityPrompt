"""
Pick the next wave of archetypes for the 3D model library.

Ranks building archetypes by how often the plan generator's resolver picks
them (simulated across every development_type in the dims table x common
floor counts), filters to archetypes with a complete 3-angle reference set
(street card + _angle_60 + _angle_90 via variants[0].thumbnailUrl), skips
keys already completed in the model cache, and prints the next N ids plus
the ready-to-run prewarm command.

Usage (from repo root):
  python scripts/next_model_batch.py --count 10
  python scripts/next_model_batch.py --count 10 --exclude id1,id2   # no API auth needed
  python scripts/next_model_batch.py --count 10 --api-url http://localhost:8000  # skip cached

Auth (only for the cache check): SITEFORGE_ADMIN_TOKEN, or
SITEFORGE_ADMIN_EMAIL + SITEFORGE_ADMIN_PASSWORD.
"""

import argparse
import collections
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
DIMS = ROOT / "backend/app/data/archetype_plan_dims.json"
CATALOG = ROOT / "frontend/src/data/buildingArchetypes.json"
PUBLIC = ROOT / "frontend/public"

# Floor counts plans commonly request — the resolver is simulated over the
# full (development_type x floors) grid, so every dev type contributes.
FLOOR_GRID = [1, 2, 3, 4, 6, 8, 12, 20, 30]


def _norm(value) -> str:
    return re.sub(r"[\s\-]+", "_", str(value if value is not None else "").lower().strip())


def resolver_pick(table: list[dict], dev_type: str, floors: int) -> str | None:
    """Mirror of resolve_building_archetype (plan_geometry/archetypes.py),
    aesthetic-free: pool by dev type, floor-range filter, stable pick."""
    pool = [e for e in table if e["usable"] and _norm(e["development_type"]) == dev_type]
    if not pool:
        pool = [
            e for e in table
            if e["usable"]
            and (_norm(e["development_type"]).startswith(f"{dev_type}_")
                 or dev_type.startswith(f"{_norm(e['development_type'])}_"))
        ]
    if not pool:
        pool = [e for e in table if e["usable"] and _norm(e["development_type"]) == "mixed_use"]
    if not pool:
        return None
    mn = lambda e: e["min_floors"] if e["min_floors"] is not None else 1
    mx = lambda e: e["max_floors"] if e["max_floors"] is not None else 999
    in_range = [e for e in pool if mn(e) <= floors <= mx(e)]
    if in_range:
        pool = in_range
    else:
        dist = lambda e: min(abs(mn(e) - floors), abs(mx(e) - floors))
        best = min(dist(e) for e in pool)
        pool = [e for e in pool if dist(e) == best]
    return sorted(pool, key=lambda e: (0 if e.get("has_variants") else 1, e["id"]))[0]["id"]


def has_full_ref_set(arch: dict) -> bool:
    variants = arch.get("variants") or []
    url = (variants[0].get("thumbnailUrl") if variants else None) or arch.get("thumbnailUrl")
    if not url:
        return False
    street = PUBLIC / url.lstrip("/")
    stem = street.with_suffix("")
    return all(p.exists() for p in (street, Path(f"{stem}_angle_60.jpg"), Path(f"{stem}_angle_90.jpg")))


def completed_ids(api_url: str) -> set[str]:
    """(archetype_id) keys already completed in the model cache (engine=meshy,
    variant default). Import the driver's auth helpers to stay in sync."""
    sys.path.insert(0, str(ROOT / "scripts"))
    from prewarm_archetype_models import api, get_token

    token = get_token(api_url)
    entries = api(api_url, "GET", "/api/v1/model-cache/entries?status=completed", token=token)["entries"]
    return {e["archetype_id"] for e in entries if e["engine"] == "meshy" and e["variant_id"] == "default"}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--count", type=int, default=10)
    parser.add_argument("--api-url", help="check the live cache and skip completed keys")
    parser.add_argument("--exclude", default="", help="comma-separated archetype ids to skip")
    args = parser.parse_args()

    table = json.loads(DIMS.read_text(encoding="utf-8"))["archetypes"]
    catalog = {a["id"]: a for a in json.loads(CATALOG.read_text(encoding="utf-8"))["archetypes"]}

    picks = collections.Counter()
    picked_for: dict[str, list[str]] = collections.defaultdict(list)
    dev_types = sorted({_norm(e["development_type"]) for e in table if e["usable"]})
    for dev in dev_types:
        for fl in FLOOR_GRID:
            p = resolver_pick(table, dev, fl)
            if p:
                picks[p] += 1
                slot = f"{dev}@{fl}f"
                if len(picked_for[p]) < 4:
                    picked_for[p].append(slot)

    exclude = {i.strip() for i in args.exclude.split(",") if i.strip()}
    if args.api_url:
        cached = completed_ids(args.api_url)
        print(f"(skipping {len(cached)} already-completed cache keys)")
        exclude |= cached

    ranked = []
    for arch_id, count in picks.most_common():
        if arch_id in exclude:
            continue
        arch = catalog.get(arch_id)
        if arch is None:
            continue
        if not has_full_ref_set(arch):
            continue
        ranked.append((arch_id, count))
        if len(ranked) >= args.count:
            break

    print(f"\nNext {len(ranked)} archetypes by plan-resolver pick frequency:")
    for arch_id, count in ranked:
        print(f"  {arch_id:45s} picks={count:2d}  e.g. {', '.join(picked_for[arch_id])}")

    ids = ",".join(a for a, _ in ranked)
    print("\nReady to run:")
    print(f"  python scripts/prewarm_archetype_models.py --mode multi-image --ids {ids} \\")
    print("      --download-artifacts artifacts/model_library_multiimage")


if __name__ == "__main__":
    main()
