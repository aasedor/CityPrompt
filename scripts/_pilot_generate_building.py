"""Pilot runner: generate variant_N.png for a single BUILDING archetype id,
using a Style-6-quality street-level prompt WITH moderate pedestrian life and
Calgary context — matching the look of the recent Calgary building cards
(calgary-beltline-mid-rise, calgary-modern-infill-house).

Why a dedicated script instead of generate_card_images.py:
  - generate_card_images.py's building path uses BUILDING_STYLE (NO_PEOPLE) and
    generates a hero.png. The recent Calgary cards clearly have street life, and
    we no longer author hero.png (UI exposes only the 4 variant slots).
  - generate_card_images.py rewrites the JSON via json.dumps(), which CORRUPTS
    buildingArchetypes.json thumbnailUrl paths (underscores -> hyphens). This
    script NEVER writes the JSON back — it only reads ids and writes images.

Imports the proven Style 6 machinery (Gemini 3.1 Flash Image @ temp 0.7,
Kodak Portra camera suffix) from generate_card_images.py.

Usage:
    python scripts/_pilot_generate_building.py --id rndsqr_sculptural_block
    python scripts/_pilot_generate_building.py --id rndsqr_sculptural_block --skip-existing
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_SCRIPT_DIR))

from generate_card_images import (  # type: ignore
    STYLE_ANCHOR,
    PEOPLE_CAMERA_SUFFIX,
    generate_image,
    resize_to_card,
    _slugify,
    _DATA_DIR,
    _PUBLIC_DIR,
)

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


# Moderate, unobtrusive street life — building stays the hero (Calgary demo
# convention: "moderate pedestrian activity", summer afternoon).
BUILDING_PEOPLE = (
    "Include a few fictional people at street level for scale and life — a "
    "couple walking on the sidewalk, a cyclist passing in a bike lane, someone "
    "entering the ground-floor cafe or lobby, a person waiting at the corner. "
    "Keep the pedestrian activity moderate and unobtrusive; the building is the "
    "hero of the image, not the people. "
)

# Inner-city Calgary setting cues (prairie sky, distant foothills, summer).
CALGARY_CONTEXT = (
    "Setting: an inner-city Calgary street on a clear summer afternoon, with "
    "mature deciduous street trees, a clear blue prairie sky, faint Rocky "
    "Mountain foothills low on the distant horizon, and neighbouring low- and "
    "mid-rise buildings lining the block. "
)

# Critical constraints live at the END (Gemini weights later text more heavily).
BUILDING_STYLE_PEOPLE = (
    "Photorealistic architectural visualization. "
    "Street-level perspective from across the street, approximately 25 meters "
    "away, at a 3/4 angle showing two facades. The full building is visible "
    "from ground to roofline with some sky above and the street/sidewalk below. "
    "{description} "
    + CALGARY_CONTEXT
    + STYLE_ANCHOR
    + " "
    + BUILDING_PEOPLE
    + PEOPLE_CAMERA_SUFFIX
)


def build_building_description(arch: dict, variant: dict | None) -> str:
    """Compose a rich card description from facade/roof/scale metadata."""
    title = arch.get("title", arch.get("id", ""))
    if variant is None:
        out = f"{title}. {arch.get('description', '')}"
        fac = arch.get("facadeDetail", {})
        roof = arch.get("roofDetail", {})
        mn, mx = arch.get("minFloors"), arch.get("maxFloors")
    else:
        out = f"{title} — {variant.get('label', 'Variant')} variant. {variant.get('description', '')}"
        fac = variant.get("facadeDetail", {})
        roof = variant.get("roofDetail", {})
        mn = variant.get("minFloors", arch.get("minFloors"))
        mx = variant.get("maxFloors", arch.get("maxFloors"))

    if fac.get("primaryMaterial"):
        out += f" Primary facade material: {fac['primaryMaterial']}."
    if fac.get("secondaryMaterial"):
        out += f" Secondary material: {fac['secondaryMaterial']}."
    if fac.get("accentMaterial"):
        out += f" Accent material: {fac['accentMaterial']}."
    if fac.get("groundFloor"):
        out += f" Ground floor: {fac['groundFloor']}."
    if fac.get("colorScheme"):
        out += f" Colour scheme: {fac['colorScheme']}."
    if roof.get("form"):
        out += f" Roof: {roof['form']}."
    if mn and mx:
        out += f" Approximately {mn}–{mx} storeys tall."
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--id", required=True, help="building archetype id")
    parser.add_argument("--skip-existing", action="store_true")
    args = parser.parse_args()

    catalog = json.loads((_DATA_DIR / "buildingArchetypes.json").read_text(encoding="utf-8"))
    archetypes = catalog if isinstance(catalog, list) else catalog.get("archetypes", catalog)

    arch = next((a for a in archetypes if a.get("id") == args.id), None)
    if arch is None:
        print(f"ERROR: archetype id={args.id!r} not found in buildingArchetypes.json")
        return 1

    arch_title = arch.get("title", args.id)
    slug = _slugify(arch_title)
    out_dir = _PUBLIC_DIR / "buildings" / slug
    out_dir.mkdir(parents=True, exist_ok=True)

    variants = arch.get("variants", [])
    print(f"Pilot building (Style 6 + people): {arch_title} -> {out_dir}")
    print(f"  {len(variants)} variants, slug={slug}")

    generated = failed = skipped = 0
    for vi, v in enumerate(variants):
        img_path = out_dir / f"variant_{vi}.png"
        if args.skip_existing and img_path.exists():
            print(f"  [{vi}] SKIP (exists): {img_path.name}")
            skipped += 1
            continue

        description = build_building_description(arch, v)
        prompt = BUILDING_STYLE_PEOPLE.format(description=description)

        print(f"\n  [{vi}] Generating: {v.get('label', '?')}")
        print(f"      Prompt: {len(prompt)} chars")
        img_bytes = generate_image(prompt)
        if img_bytes is None:
            print("      FAILED")
            failed += 1
            continue

        resized = resize_to_card(img_bytes)
        img_path.write_bytes(resized)
        kb = img_path.stat().st_size / 1024
        print(f"      Saved {img_path.name} ({kb:.1f} KB)")
        generated += 1
        time.sleep(2)

    # No hero.png (see feedback_no_hero_image.md). No JSON writeback (see the
    # NEVER json.dump buildingArchetypes.json rule) — author thumbnailUrl in the
    # catalog by hand via text-level splice.
    print(f"\nDone: generated={generated} failed={failed} skipped={skipped}")
    return 0 if failed == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
