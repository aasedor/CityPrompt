"""Focused sweep: find placeholder/stub archetypes+variants and sanity-check
recommended sizes. Answers two questions:

  1. Which archetypes/variants give the model almost no prompt?
     (stub archetype description, "Style Variant N" labels, "<Title> — style
      variant N." descriptions)
  2. Are the recommended sizes (suggestedAreaSqm + width/depth) plausible?
     Surfaces the smallest archetypes and dimension<->area inconsistencies.

Read-only. Prints a report to stdout. Run: python scripts/_audit_stub_and_size.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "frontend" / "src" / "data"
CATALOGS = {
    "buildings": DATA / "buildingArchetypes.json",
    "streets": DATA / "streetPathArchetypes.json",
    "openspaces": DATA / "openSpaceArchetypes.json",
}

AREA_FIELDS = ("suggestedAreaSqm", "minAreaSqm", "maxAreaSqm", "footprintSqm",
               "typicalAreaSqm", "suggestedAreaSm")
WIDTH_FIELDS = ("suggestedWidth_m", "typicalWidth_m", "minWidth_m", "maxWidth_m", "width_m")
DEPTH_FIELDS = ("suggestedDepth_m", "typicalDepth_m", "depth_m", "suggestedLength_m", "length_m")


def first(d: dict, fields) -> float | None:
    for f in fields:
        if d.get(f) is not None:
            return d[f]
    return None


def is_stub_desc(desc: str, title: str) -> bool:
    if not desc:
        return True
    n = desc.strip().lower()
    t = title.lower()
    return n in (f"a {t}.", f"an {t}.", f"the {t}.", t, f"{t}.") or len(n) < 20


STYLE_VARIANT_LABEL = re.compile(r"^style variant \d+$", re.IGNORECASE)


def variant_desc_is_stub(desc: str, title: str) -> bool:
    """True if a variant description carries no real prompt signal."""
    if not desc:
        return True
    n = desc.strip().lower()
    t = title.lower()
    # "<Title> — style variant N." (any dash) or "style variant N" or just title
    if re.match(rf"^{re.escape(t)}\s*[—\-–]\s*style variant \d+\.?$", n):
        return True
    if re.match(r"^style variant \d+\.?$", n):
        return True
    if len(n) < 25:
        return True
    return False


def load(path: Path):
    data = json.loads(path.read_text(encoding="utf-8"))
    arr = data.get("archetypes", data) if isinstance(data, dict) else data
    return arr


def analyze(domain: str, path: Path):
    arr = load(path)
    placeholder = []        # stub desc AND all variant labels are "Style Variant N"
    stub_desc_only = []     # arch desc stub, but variants have real labels
    stub_variants_only = [] # arch desc OK, but variants are placeholder
    sizes = []              # (id, title, area, w, d, consistent, per_variant_areas)

    for a in arr:
        aid = a.get("id", "?")
        title = a.get("title") or a.get("label") or aid
        variants = a.get("variants", []) or []

        desc_stub = is_stub_desc(a.get("description", ""), title)
        labels = [v.get("label", "") for v in variants]
        all_label_stub = bool(labels) and all(STYLE_VARIANT_LABEL.match(l or "") for l in labels)
        vdescs = [v.get("description", "") for v in variants]
        all_vdesc_stub = bool(vdescs) and all(variant_desc_is_stub(d, title) for d in vdescs)
        variants_stub = all_label_stub or all_vdesc_stub

        if desc_stub and variants_stub:
            placeholder.append((aid, title, len(variants)))
        elif desc_stub:
            stub_desc_only.append((aid, title))
        elif variants_stub:
            stub_variants_only.append((aid, title))

        # sizes
        area = first(a, AREA_FIELDS)
        w = first(a, WIDTH_FIELDS)
        d = first(a, DEPTH_FIELDS)
        consistent = None
        if area and w and d:
            wd = w * d
            consistent = abs(wd - area) / max(area, 1) < 0.30  # within 30%
        pv = [first(v, AREA_FIELDS) for v in variants]
        pv = [x for x in pv if x]
        sizes.append((aid, title, area, w, d, consistent, pv))

    return placeholder, stub_desc_only, stub_variants_only, sizes


def main():
    grand_placeholder = {}
    for domain, path in CATALOGS.items():
        placeholder, stub_desc, stub_var, sizes = analyze(domain, path)
        grand_placeholder[domain] = placeholder
        print("=" * 78)
        print(f"CATALOG: {domain}  ({len(load(path))} archetypes)")
        print("=" * 78)

        print(f"\n--- PLACEHOLDER archetypes (stub description AND stub variants): {len(placeholder)} ---")
        print("    (these give the model almost no prompt at all — like Equestrian Center)")
        for aid, title, nv in placeholder:
            # find the size for this one
            sz = next((s for s in sizes if s[0] == aid), None)
            area = sz[2] if sz else None
            w, d = (sz[3], sz[4]) if sz else (None, None)
            print(f"    - {aid:42s} '{title}'  area={area} ({w}x{d})  variants={nv}")

        print(f"\n--- Stub ARCHETYPE description only (variants have real labels): {len(stub_desc)} ---")
        for aid, title in stub_desc:
            print(f"    - {aid:42s} '{title}'")

        print(f"\n--- Stub VARIANTS only (archetype desc is fine): {len(stub_var)} ---")
        for aid, title in stub_var:
            print(f"    - {aid:42s} '{title}'")

        # size sanity
        with_area = [s for s in sizes if s[2]]
        print(f"\n--- SIZE sweep: {len(with_area)}/{len(sizes)} archetypes have an area value ---")

        inconsistent = [s for s in sizes if s[5] is False]
        print(f"\n  Dimension<->area MISMATCH (w*d differs from stated area by >30%): {len(inconsistent)}")
        for aid, title, area, w, d, _, _ in inconsistent[:25]:
            print(f"    - {aid:40s} area={area}  w*d={w}x{d}={(w*d) if w and d else '?'}")

        if domain != "streets":
            smallest = sorted(with_area, key=lambda s: s[2])[:25]
            print(f"\n  SMALLEST 25 by suggested area (eyeball for implausibly tiny):")
            for aid, title, area, w, d, cons, pv in smallest:
                pvs = f"  per-variant={pv}" if pv else "  (no per-variant area)"
                print(f"    - {area:>8} m²  {aid:38s} '{title}'{pvs}")

        print()

    print("=" * 78)
    total_ph = sum(len(v) for v in grand_placeholder.values())
    print(f"TOTAL placeholder archetypes across all catalogs: {total_ph}")
    for domain, items in grand_placeholder.items():
        print(f"  {domain}: {len(items)}")
    print("=" * 78)


if __name__ == "__main__":
    main()
