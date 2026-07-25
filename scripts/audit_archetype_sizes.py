"""
Audit recommended sizes and heights across all building archetypes and their variants.

Checks:
  A. Field presence (which archetypes/variants are missing size/height info)
  B. Internal consistency (suggested between min/max, area = w*d, aspect matches w:d, min<=max floors)
  C. Variant-vs-parent conflicts (variant floors outside parent range, etc.)
  D. Typology-vs-scale realism (townhouse with 30 floors, tower with 2 floors, etc.)
  E. Floor-height x floors implied total height vs typology norms

Usage:
    python scripts/audit_archetype_sizes.py            # text report
    python scripts/audit_archetype_sizes.py --csv      # also write artifacts/audit/archetype_sizes_audit.csv
    python scripts/audit_archetype_sizes.py --md       # also write docs/ARCHETYPE_SIZES_AUDIT_2026_04_28.md
"""

from __future__ import annotations

import json
import math
import sys
import argparse
import csv
import os
import re
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CATALOG_PATH = "frontend/src/data/buildingArchetypes.json"

# Typology priors — realistic floor counts for known categories. Triggered by
# substring match against archetype id, title, subcategory, or variant label/desc.
# Tuple: (label, min_floor_floor, max_floor_ceiling, typical_floor_height_m).
# Ordered MOST-SPECIFIC FIRST so they hit before broader patterns.
# These are *advisory* — used to flag wildly off entries, not to mass-edit.
TYPOLOGY_PRIORS = [
    # === Towers (specific) — must come before generic "mixed_use" / "midrise" ===
    ("art_deco_setback_tower|setback_tower|skyscraper|supertall|streamline_moderne_tower",
        ("art-deco / setback tower", 12, 60, 3.6)),
    ("hotel.*tower|tower.*hotel|corporate_tower",
        ("hotel/corporate tower", 12, 40, 3.6)),
    ("podium_tower|condo_podium|tower_podium",
        ("podium + tower", 6, 40, 3.4)),
    ("highrise_residential|residential_highrise|residential_tower|condo_tower",
        ("residential high-rise", 12, 35, 3.2)),
    ("vertical_farm|farmscraper",
        ("vertical farm (very tall niche)", 2, 50, 4.0)),
    ("vertical_forest",
        ("residential tower with planted balconies", 8, 30, 3.4)),
    ("glass_tower|tower_modern",
        ("modern glass tower", 12, 60, 3.6)),

    # === Stadium / arena / megastructure — big footprint, few floors ===
    ("stadium|arena",
        ("stadium / arena", 1, 5, 12.0)),
    ("megastructure",
        ("megastructure (large, low floors)", 1, 8, 5.0)),

    # === Industrial / warehouse ===
    ("warehouse|big_box|logistics|distribution|hangar|fulfillment|data_center",
        ("warehouse / big-box", 1, 4, 6.0)),
    ("brewery|distillery",
        ("brewery / distillery", 1, 4, 5.5)),
    ("power_station|powerstation",
        ("power station", 1, 4, 8.0)),
    ("factory|industrial",
        ("industrial mid-bay", 1, 6, 5.0)),

    # === Cultural / performance / civic monumental ===
    ("opera_house|concert_hall|theater|theatre|symphony|amphitheater|amphitheatre|cinema_palace|movie_palace",
        ("cultural / performance", 1, 5, 6.5)),
    ("cathedral|church|temple|mosque|chapel|synagogue|basilica",
        ("religious", 1, 4, 8.0)),
    ("monumental|civic_classical|courthouse|capitol|state_house|legislature",
        ("monumental civic", 1, 6, 6.0)),
    ("museum|gallery|library",
        ("museum / library", 1, 5, 6.0)),

    # === Education / health / research ===
    ("research_lab|laboratory|innovation_hub|biotech",
        ("research lab", 2, 10, 4.5)),
    ("hospital|healthcare|medical_center|clinic",
        ("healthcare", 3, 12, 4.0)),
    ("school|university|college|education|collegiate|academic",
        ("educational", 2, 6, 3.8)),

    # === Transit / infrastructure ===
    ("vertiport|heliport|airport_terminal",
        ("aviation infrastructure", 1, 4, 7.0)),
    ("transit_hub|train_shed|intermodal|station_hub",
        ("transit infrastructure", 1, 5, 6.0)),
    ("parking_garage|parking_structure",
        ("parking garage", 2, 10, 3.0)),

    # === Retail / commercial ===
    ("mall_redevelopment|shopping_centre|shopping_center|department_store|grand_magasin",
        ("retail anchor", 1, 6, 4.5)),

    # === Greenhouse / pavilion ===
    ("greenhouse|conservatory",
        ("glasshouse", 1, 2, 7.0)),
    ("park_pavilion|garden_pavilion|pavilion(?!_block)",
        ("pavilion", 1, 2, 4.0)),

    # === Rec / community ===
    ("rec_centre|recreation_centre|recreation_center|community_centre|community_center|natatorium|swimming_centre",
        ("rec / community centre", 1, 3, 5.0)),
    ("climbing_wall",
        ("climbing facility", 2, 5, 6.0)),

    # === Hotels / hospitality (non-tower) ===
    ("boutique_hotel(?!_tower)|inn(?!_)|lodge|resort_low_rise",
        ("boutique hotel / lodge", 2, 8, 3.6)),

    # === Residential typologies (specific) ===
    ("rowhouse|brownstone|townhouse|terrace_housing|machiya|shophouse|lanehouse|terraced_house|infill_townhouse",
        ("low-rise residential row", 2, 5, 3.2)),
    ("detached.*infill|alpine_chalet|villa_estate|cottage|farmhouse|bungalow|single_family|detached_home|estate_home",
        ("low-rise detached", 1, 3, 3.0)),
    ("senior_living|assisted_living|retirement|aged_care",
        ("senior living", 2, 8, 3.2)),

    # === Generic mid-rise / mixed-use (last resort, broad) ===
    ("midrise|mid_rise|courtyard_block|streetwall|main_street|haussmann|grand_magasin|parisian_midrise",
        ("mid-rise residential", 4, 8, 3.4)),
    ("mixed_use|live_work",
        ("mixed-use mid-rise", 3, 8, 3.4)),
    ("apartment|condo|residential",
        ("generic residential", 3, 12, 3.2)),

    # === Generic offices / civic / industrial fallbacks ===
    ("brutalist",
        ("brutalist (variable)", 2, 20, 3.5)),
    ("office|hq|headquarters|commercial_block",
        ("generic office", 3, 20, 3.8)),
    ("civic|government|municipal|town_hall",
        ("generic civic", 1, 6, 4.5)),
]


def find_typology_prior(arch, variant=None):
    """Return (label, min_floor_floor, max_floor_ceiling, typical_floor_height) or None.

    Variant text takes priority — if a variant matches a more-specific typology,
    use that instead of the parent's typology.
    """
    if variant is not None:
        v_needle = " ".join([
            variant.get("id", "") or "",
            variant.get("label", "") or "",
            variant.get("description", "") or "",
        ]).lower()
        for pattern, prior in TYPOLOGY_PRIORS:
            if re.search(pattern, v_needle):
                return prior

    a_needle = " ".join([
        arch.get("id", "") or "",
        arch.get("title", "") or "",
        arch.get("buildingSubcategory", "") or "",
        " ".join(arch.get("generationTags", []) or []),
    ]).lower()
    for pattern, prior in TYPOLOGY_PRIORS:
        if re.search(pattern, a_needle):
            return prior
    return None


def parse_aspect(aspect_str):
    """Parse '2.5:1' or '1:2.5' into a w/d ratio."""
    if not aspect_str or ":" not in aspect_str:
        return None
    try:
        a, b = aspect_str.split(":", 1)
        return float(a) / float(b)
    except (ValueError, ZeroDivisionError):
        return None


def fmt_pct(n, d):
    return f"{100*n/d:.1f}%" if d else "n/a"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", action="store_true", help="Also write CSV of every issue")
    ap.add_argument("--md", action="store_true", help="Also write markdown report")
    args = ap.parse_args()

    with open(CATALOG_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    arches = data["archetypes"]

    findings = []  # list of dicts: archetype_id, scope, severity, code, message
    def add(arch_id, scope, severity, code, message):
        findings.append({
            "archetype_id": arch_id,
            "scope": scope,
            "severity": severity,
            "code": code,
            "message": message,
        })

    # ── Tallies ──────────────────────────────────────────────────────────────
    n_archs = len(arches)
    n_variants = sum(len(a.get("variants", [])) for a in arches)

    presence = {
        "minWidth_m": 0, "maxWidth_m": 0, "minDepth_m": 0, "maxDepth_m": 0,
        "suggestedWidth_m": 0, "suggestedDepth_m": 0, "aspectRatio": 0,
        "minFloors": 0, "maxFloors": 0, "suggestedAreaSqm": 0,
        "legacy_floorRange": 0, "legacy_suggestedArea_m2": 0,
    }
    variant_presence = {
        "minFloors": 0, "maxFloors": 0,
        "suggestedAreaSqm": 0, "suggestedFloorHeight": 0,
    }

    # ── Per-archetype audit ──────────────────────────────────────────────────
    for arch in arches:
        aid = arch["id"]
        # presence
        for f in ("minWidth_m", "maxWidth_m", "minDepth_m", "maxDepth_m",
                  "suggestedWidth_m", "suggestedDepth_m", "aspectRatio",
                  "minFloors", "maxFloors", "suggestedAreaSqm"):
            if f in arch:
                presence[f] += 1
        if "floorRange" in arch:
            presence["legacy_floorRange"] += 1
            add(aid, "archetype", "med", "LEGACY_SCHEMA",
                f"Uses legacy `floorRange`={arch['floorRange']!r} instead of minFloors/maxFloors")
        if "suggestedArea_m2" in arch:
            presence["legacy_suggestedArea_m2"] += 1
            add(aid, "archetype", "med", "LEGACY_SCHEMA",
                f"Uses legacy `suggestedArea_m2`={arch['suggestedArea_m2']!r} instead of suggestedAreaSqm")

        # missing core fields
        if "suggestedWidth_m" not in arch or "suggestedDepth_m" not in arch:
            add(aid, "archetype", "high", "MISSING_FOOTPRINT",
                "Missing suggestedWidth_m/suggestedDepth_m")
        if not all(k in arch for k in ("minWidth_m", "maxWidth_m", "minDepth_m", "maxDepth_m")):
            add(aid, "archetype", "med", "MISSING_RANGE",
                "Missing one or more of min/max width/depth")
        if "minFloors" not in arch or "maxFloors" not in arch:
            add(aid, "archetype", "high", "MISSING_FLOORS",
                "Missing minFloors/maxFloors")
        if "suggestedAreaSqm" not in arch:
            add(aid, "archetype", "med", "MISSING_AREA",
                "Missing suggestedAreaSqm")

        # internal consistency: width/depth ranges
        sw = arch.get("suggestedWidth_m")
        sd = arch.get("suggestedDepth_m")
        mnw = arch.get("minWidth_m")
        mxw = arch.get("maxWidth_m")
        mnd = arch.get("minDepth_m")
        mxd = arch.get("maxDepth_m")

        if mnw is not None and mxw is not None and mnw > mxw:
            add(aid, "archetype", "high", "RANGE_INVERT",
                f"minWidth_m ({mnw}) > maxWidth_m ({mxw})")
        if mnd is not None and mxd is not None and mnd > mxd:
            add(aid, "archetype", "high", "RANGE_INVERT",
                f"minDepth_m ({mnd}) > maxDepth_m ({mxd})")

        if sw is not None and mnw is not None and mxw is not None:
            if sw < mnw - 0.001 or sw > mxw + 0.001:
                add(aid, "archetype", "high", "SUGGESTED_OUT_OF_RANGE",
                    f"suggestedWidth_m ({sw}) outside [{mnw}, {mxw}]")
        if sd is not None and mnd is not None and mxd is not None:
            if sd < mnd - 0.001 or sd > mxd + 0.001:
                add(aid, "archetype", "high", "SUGGESTED_OUT_OF_RANGE",
                    f"suggestedDepth_m ({sd}) outside [{mnd}, {mxd}]")

        # aspect ratio sanity
        ar_str = arch.get("aspectRatio")
        if ar_str and sw and sd:
            ar_parsed = parse_aspect(ar_str)
            if ar_parsed:
                ar_actual = sw / sd
                # tolerate ~12% drift (catalog rounds e.g. 25:18 → "1.4:1")
                drift = abs(math.log(ar_parsed / ar_actual))
                if drift > math.log(1.15):
                    add(aid, "archetype", "low", "ASPECT_MISMATCH",
                        f"aspectRatio={ar_str} (={ar_parsed:.2f}) but suggestedWidth/Depth={sw}/{sd} ratio={ar_actual:.2f}")

        # area sanity (suggestedAreaSqm should be ≥ footprint when single-storey,
        # and roughly = footprint × floors when multi-storey; but the field semantics
        # are inconsistent across the catalog — some use FOOTPRINT, some use GFA.
        sa = arch.get("suggestedAreaSqm")
        mnf = arch.get("minFloors")
        mxf = arch.get("maxFloors")
        if sa and sw and sd:
            footprint = sw * sd
            if sa < 0.7 * footprint:
                add(aid, "archetype", "med", "AREA_LT_FOOTPRINT",
                    f"suggestedAreaSqm ({sa}) much less than footprint ({sw}×{sd}={footprint:.0f}) — inconsistent semantics")
            elif mnf and mxf and mnf > 0:
                avg_floors = (mnf + mxf) / 2
                expected_gfa = footprint * avg_floors
                # allow 0.4× to 2.0× tolerance (some have light wells / setbacks / podiums)
                if avg_floors > 1.5:
                    if sa > 2.5 * expected_gfa:
                        add(aid, "archetype", "low", "AREA_GT_GFA",
                            f"suggestedAreaSqm ({sa}) much larger than footprint×avgFloors ({footprint:.0f}×{avg_floors:.1f}={expected_gfa:.0f})")
                    elif sa < 0.3 * footprint and avg_floors >= 2:
                        add(aid, "archetype", "med", "AREA_TOO_SMALL",
                            f"suggestedAreaSqm ({sa}) << footprint ({footprint:.0f}) for {mnf}-{mxf} floors")

        # floor range
        if mnf is not None and mxf is not None:
            if mnf > mxf:
                add(aid, "archetype", "high", "FLOORS_INVERT",
                    f"minFloors ({mnf}) > maxFloors ({mxf})")
            if mnf <= 0:
                add(aid, "archetype", "high", "FLOORS_NONPOS",
                    f"minFloors={mnf} (must be ≥1)")
            if mxf > 100:
                add(aid, "archetype", "med", "FLOORS_TOOHIGH",
                    f"maxFloors={mxf} (suspiciously high)")

        # typology prior (archetype level)
        prior = find_typology_prior(arch)
        if prior and mnf is not None and mxf is not None:
            label, lo, hi, _h = prior
            # flag if typology range and catalog range don't intersect
            if mxf < lo or mnf > hi:
                add(aid, "archetype", "med", "TYPOLOGY_FLOOR_MISMATCH",
                    f"floors=[{mnf},{mxf}] outside typology prior '{label}' [{lo},{hi}]")
            # also flag if catalog range is much wider than typology in BOTH directions (placeholder)
            if mnf <= 1 and mxf >= 50 and label not in ("brutalist (variable, often big)", "vertical farm (very tall niche)"):
                add(aid, "archetype", "low", "FLOORS_TOO_BROAD",
                    f"floors=[{mnf},{mxf}] suspiciously wide for '{label}'")

        # ── Per-variant audit ────────────────────────────────────────────────
        variants = arch.get("variants", []) or []
        # Are ALL variants identical (suggesting catalog never differentiated)?
        var_floors = [(v.get("minFloors"), v.get("maxFloors")) for v in variants]
        var_areas = [v.get("suggestedAreaSqm") for v in variants]
        var_with_scale = sum(1 for f in var_floors if f != (None, None))

        for v in variants:
            vid = v.get("id", "<no id>")
            vlabel = v.get("label", "")
            scope = f"variant:{vid}"
            for f in ("minFloors", "maxFloors", "suggestedAreaSqm", "suggestedFloorHeight"):
                if f in v:
                    variant_presence[f] += 1

            v_mnf = v.get("minFloors")
            v_mxf = v.get("maxFloors")
            v_fh = v.get("suggestedFloorHeight")
            v_sa = v.get("suggestedAreaSqm")

            # presence: variant has SOME scale info?
            has_some = any(v.get(f) is not None for f in ("minFloors", "maxFloors", "suggestedAreaSqm", "suggestedFloorHeight"))
            if not has_some:
                # only flag this if the parent has scale spread (mxf - mnf >= 3) — otherwise inheriting parent is fine
                if mnf is not None and mxf is not None and (mxf - mnf) >= 4:
                    add(aid, scope, "med", "VARIANT_NO_SCALE",
                        f"Variant '{vlabel}' has no per-variant scale (parent floors span {mnf}-{mxf} — too wide to inherit)")

            # internal consistency on variant
            if v_mnf is not None and v_mxf is not None:
                if v_mnf > v_mxf:
                    add(aid, scope, "high", "FLOORS_INVERT",
                        f"Variant '{vlabel}' minFloors ({v_mnf}) > maxFloors ({v_mxf})")
                if v_mnf <= 0:
                    add(aid, scope, "high", "FLOORS_NONPOS",
                        f"Variant '{vlabel}' minFloors={v_mnf}")

            # variant-vs-parent
            if v_mnf is not None and mxf is not None and v_mnf > mxf + 0.001:
                add(aid, scope, "med", "VARIANT_EXCEEDS_PARENT",
                    f"Variant '{vlabel}' minFloors ({v_mnf}) > parent maxFloors ({mxf})")
            if v_mxf is not None and mnf is not None and v_mxf < mnf - 0.001:
                add(aid, scope, "med", "VARIANT_BELOW_PARENT",
                    f"Variant '{vlabel}' maxFloors ({v_mxf}) < parent minFloors ({mnf})")

            # floor-height sanity
            if v_fh is not None:
                if v_fh < 2.4:
                    add(aid, scope, "med", "FLOOR_HEIGHT_TOO_LOW",
                        f"Variant '{vlabel}' suggestedFloorHeight={v_fh}m (humans need ≥2.4m clear)")
                if v_fh > 12:
                    add(aid, scope, "med", "FLOOR_HEIGHT_TOO_HIGH",
                        f"Variant '{vlabel}' suggestedFloorHeight={v_fh}m (>12m is unusual outside hangars/cathedrals)")

            # area sanity at variant level
            if v_sa and sw and sd:
                footprint = sw * sd
                avg_v_floors = ((v_mnf or mnf or 1) + (v_mxf or mxf or 1)) / 2 if (v_mnf or mnf) else 1
                if avg_v_floors >= 1:
                    expected_gfa = footprint * avg_v_floors
                    if v_sa > 4 * expected_gfa:
                        add(aid, scope, "low", "VARIANT_AREA_HUGE",
                            f"Variant '{vlabel}' suggestedAreaSqm ({v_sa}) much larger than footprint×floors ({expected_gfa:.0f})")

            # typology prior for this specific variant
            v_prior = find_typology_prior(arch, v)
            if v_prior:
                label, lo, hi, typ_h = v_prior
                check_mnf = v_mnf if v_mnf is not None else mnf
                check_mxf = v_mxf if v_mxf is not None else mxf
                if check_mnf is not None and check_mxf is not None:
                    if check_mxf < lo or check_mnf > hi:
                        add(aid, scope, "med", "VARIANT_TYPOLOGY_FLOOR_MISMATCH",
                            f"Variant '{vlabel}' floors=[{check_mnf},{check_mxf}] outside typology prior '{label}' [{lo},{hi}]")
                if v_fh is not None and (v_fh < typ_h * 0.55 or v_fh > typ_h * 1.8):
                    add(aid, scope, "low", "VARIANT_FLOOR_HEIGHT_OFF",
                        f"Variant '{vlabel}' suggestedFloorHeight={v_fh}m vs typology '{label}' typical {typ_h}m")

    # ── Print summary ────────────────────────────────────────────────────────
    print("=" * 78)
    print(f"BUILDING ARCHETYPE SIZE/HEIGHT AUDIT — {n_archs} archetypes, {n_variants} variants")
    print("=" * 78)
    print()
    print("FIELD PRESENCE (archetype level):")
    for f in ("suggestedWidth_m", "suggestedDepth_m", "aspectRatio",
              "minWidth_m", "maxWidth_m", "minDepth_m", "maxDepth_m",
              "minFloors", "maxFloors", "suggestedAreaSqm"):
        n = presence[f]
        print(f"  {f:24} {n:3}/{n_archs} ({fmt_pct(n, n_archs)})")
    print(f"  legacy floorRange         {presence['legacy_floorRange']:3}/{n_archs}")
    print(f"  legacy suggestedArea_m2   {presence['legacy_suggestedArea_m2']:3}/{n_archs}")

    print()
    print("FIELD PRESENCE (variant level):")
    for f in ("minFloors", "maxFloors", "suggestedAreaSqm", "suggestedFloorHeight"):
        n = variant_presence[f]
        print(f"  {f:24} {n:3}/{n_variants} ({fmt_pct(n, n_variants)})")

    print()
    print("FINDINGS BY SEVERITY:")
    by_sev = Counter(f["severity"] for f in findings)
    for sev in ("high", "med", "low"):
        print(f"  {sev:5} {by_sev[sev]}")
    print(f"  TOTAL  {len(findings)}")

    print()
    print("FINDINGS BY CODE:")
    by_code = Counter(f["code"] for f in findings)
    for code, n in by_code.most_common():
        print(f"  {n:4}  {code}")

    print()
    print("HIGH-SEVERITY FINDINGS (top 50):")
    high = [f for f in findings if f["severity"] == "high"]
    for f in high[:50]:
        print(f"  [{f['archetype_id']:42}] [{f['scope']:30}] [{f['code']:24}] {f['message']}")
    if len(high) > 50:
        print(f"  ... and {len(high) - 50} more")

    print()
    print("MEDIUM-SEVERITY FINDINGS (top 30):")
    med = [f for f in findings if f["severity"] == "med"]
    for f in med[:30]:
        print(f"  [{f['archetype_id']:42}] [{f['scope']:30}] [{f['code']:30}] {f['message']}")
    if len(med) > 30:
        print(f"  ... and {len(med) - 30} more")

    # ── Output files ─────────────────────────────────────────────────────────
    if args.csv:
        os.makedirs("artifacts/audit", exist_ok=True)
        out = "artifacts/audit/archetype_sizes_audit.csv"
        with open(out, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["archetype_id", "scope", "severity", "code", "message"])
            w.writeheader()
            for row in findings:
                w.writerow(row)
        print(f"\nWrote {out} ({len(findings)} rows)")

    if args.md:
        os.makedirs("docs", exist_ok=True)
        # the markdown report is built externally — this script just dumps facts
        out = "artifacts/audit/archetype_sizes_findings.json"
        os.makedirs("artifacts/audit", exist_ok=True)
        with open(out, "w", encoding="utf-8") as f:
            json.dump({
                "totals": {"archetypes": n_archs, "variants": n_variants},
                "presence_archetype": presence,
                "presence_variant": variant_presence,
                "findings_by_severity": dict(by_sev),
                "findings_by_code": dict(by_code),
                "findings": findings,
            }, f, indent=2)
        print(f"\nWrote {out}")


if __name__ == "__main__":
    main()
