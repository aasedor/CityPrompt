#!/usr/bin/env python3
"""
Enrich orphan stub archetypes to Tier-1 quality using Claude API (Sonnet 4.6 vision).

For each orphan stub (placeholder description, "Style Variant N" labels, no
styleProfile/prompt/facadeDetail), call Claude Sonnet 4.6 with:
  - the current stub metadata
  - the archetype's 4 variant PNGs (so it grounds claims in actual imagery)

Claude returns a fully enriched archetype object with:
  - rich archetype-level description + aestheticCategory + generationTags
  - 11-field styleProfile + prompt (subject + details)
  - per-variant: descriptive label, prose description, facadeDetail, roofDetail,
    and per-variant minFloors/maxFloors/suggestedFloorHeight/suggestedAreaSqm
    (variants differ across era/typology/scale/materials, not just facade)

Uses TEXT-LEVEL splicing for the catalog (never json.dump the whole catalog —
per CLAUDE.md rule). Preserves immutable routing fields (id, thumbnailUrl,
developmentType, buildingSubcategory) by merging Claude output with the stub.

Usage:
    python scripts/enrich_orphan_archetypes.py --limit=2            # enrich first 2
    python scripts/enrich_orphan_archetypes.py --ids-file=<path>    # specific IDs
    python scripts/enrich_orphan_archetypes.py                      # enrich all orphans

Requirements:
    pip install anthropic
    ANTHROPIC_API_KEY env var or `ANTHROPIC_API_KEY=...` line in backend/.env
"""

from __future__ import annotations

import base64
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Any

try:
    import anthropic
except ImportError:
    print("ERROR: `anthropic` package not installed. Run: pip install anthropic")
    sys.exit(1)


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT / "frontend" / "src" / "data" / "buildingArchetypes.json"
PUBLIC_BUILDINGS = ROOT / "frontend" / "public" / "archetypes" / "buildings"
ORPHAN_IDS_FILE = ROOT / "artifacts" / "orphan-ids" / "buildings.txt"
ENV_FILE = ROOT / "backend" / ".env"
MODEL = "claude-sonnet-4-6"


def load_anthropic_key() -> str:
    """Load ANTHROPIC_API_KEY from root .env, backend/.env, or env var."""
    key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if key:
        return key
    for env_path in (ROOT / ".env", ENV_FILE):
        if not env_path.exists():
            continue
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("ANTHROPIC_API_KEY="):
                val = line.split("=", 1)[1].strip().strip('"').strip("'")
                if val:
                    return val
    print("ERROR: ANTHROPIC_API_KEY not found in env or .env files")
    sys.exit(1)


# ---------------------------------------------------------------------------
# System prompt for Claude — the enrichment rules
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """You are an architectural metadata enrichment assistant for SiteForge, a site-planning tool that generates AI renders from zone polygons + archetype metadata.

Given a stub archetype entry + its 4 variant reference images, produce a Tier-1 enriched JSON block.

QUALITY BAR (gold standard: vertical_farm, grand_magasin, brownstone_rowhouse_frontage):
- Archetype level: rich `description` (3-5 sentences describing typology, program, architectural character), `aestheticCategory` (e.g. "contemporary_urban" / "institutional_healthcare" / "historical" / "modernist" / "industrial_brick" / "brownstone_rowhouse"), `generationTags` (5-8 keywords), `styleProfile` with 11 fields: materials (3-6 items), facadeRhythm, roofForm, frontageType, windowStyle, massing, heightTendency, streetRelationship, renderingMood, articulation, publicRealm — each a specific phrase matching the archetype's language, not generic. `prompt` with `subject` (one specific sentence) + `details` (5-6 visually grounded bullet points).
- Variant level: descriptive label (NOT "Style Variant N"), 150-250 char prose description grounded in what the PNG actually shows (specific materials, colors, massing features), `facadeDetail` (primaryMaterial, secondaryMaterial, optional accentMaterial, groundFloor, colorScheme), `roofDetail` (form, material). AND per-variant `minFloors`, `maxFloors`, `suggestedFloorHeight`, `suggestedAreaSqm` — reflecting the scale actually shown.

VARIANT DIFFERENTIATION (CRITICAL):
Variants should differ across MULTIPLE dimensions — not just facade materials. Look at the 4 PNGs and vary across whichever dimensions the images actually support:
1. SIZE — `minFloors` / `maxFloors` / `suggestedFloorHeight` / `suggestedAreaSqm` can differ meaningfully between variants. vertical_farm spans 15-55 storeys across its 4 variants. Some archetypes (urban infill offices) honestly stay at the same scale — don't force differences that contradict the images.
2. TYPOLOGY — standalone tower vs attached wing vs heritage retrofit vs campus complex vs infill. Use different variant IDs/labels to signal this.
3. ERA / movement — classical / heritage-Victorian / mid-century / contemporary / sustainable-mass-timber / parametric. A hospital archetype could have a Victorian pavilion variant, a mid-century utilitarian variant, a contemporary teaching-hospital variant, and a biophilic wellness variant.
4. MATERIALS / cladding — fine to vary but must not be the ONLY dimension of variation unless the PNGs genuinely only differ in facade.
5. CONTEXT — urban dense vs campus quad vs waterfront vs industrial zone.

Ground every claim in the actual PNGs. If you see green walls + solar roof, name those. If you see a clock tower + red brick, use "Heritage Victorian Pavilion" typology.

OUTPUT FORMAT (strict):
Return ONLY a JSON object. No markdown fences. No commentary. No "Here is the enriched..." preamble. Just the raw JSON. The object must contain these top-level keys exactly:

{
  "description": "...",
  "aestheticCategory": "...",
  "generationTags": ["...", "..."],
  "styleProfile": {
    "materials": ["...", "..."],
    "facadeRhythm": "...",
    "roofForm": "...",
    "frontageType": "...",
    "windowStyle": "...",
    "massing": "...",
    "heightTendency": "...",
    "streetRelationship": "...",
    "renderingMood": "...",
    "articulation": "...",
    "publicRealm": "..."
  },
  "prompt": {
    "subject": "...",
    "details": ["...", "..."]
  },
  "suggestedWidth_m": 30,
  "suggestedDepth_m": 20,
  "minFloors": 3,
  "maxFloors": 6,
  "variants": [
    {
      "id": "<snake_case_id_unique_to_this_variant>",
      "label": "<descriptive label like 'Heritage Victorian Pavilion' — NOT 'Style Variant N'>",
      "description": "<150-250 chars, specific to this PNG>",
      "color": "#RRGGBB",
      "minFloors": 4,
      "maxFloors": 6,
      "suggestedFloorHeight": 4.0,
      "suggestedAreaSqm": 3600,
      "facadeDetail": {
        "primaryMaterial": "...",
        "secondaryMaterial": "...",
        "accentMaterial": "...",
        "groundFloor": "...",
        "colorScheme": "..."
      },
      "roofDetail": {
        "form": "...",
        "material": "..."
      }
    },
    // ...4 variants total, in the same order as the PNGs I send you (variant_0, variant_1, variant_2, variant_3)
  ]
}

DO NOT include `thumbnailUrl` — the caller preserves those. DO NOT include `id` at the archetype top level, `title`, `buildingSubcategory`, or `developmentType` — those are preserved from the stub. Include only the enrichment fields listed above.
"""


# ---------------------------------------------------------------------------
# Image loading + user message assembly
# ---------------------------------------------------------------------------


def load_png_b64(path: Path) -> str | None:
    if not path.exists():
        return None
    return base64.b64encode(path.read_bytes()).decode("ascii")


def build_user_content(stub: dict, folder: Path) -> list[dict]:
    """Build the user-message content: stub JSON + 4 variant PNGs."""
    parts: list[dict] = []

    # Stub summary (what we know already — id, title, subcategory, etc.)
    stub_summary = {
        "id": stub.get("id"),
        "title": stub.get("title"),
        "buildingSubcategory": stub.get("buildingSubcategory"),
        "developmentType": stub.get("developmentType"),
        "folder_on_disk": folder.name,
    }
    parts.append({
        "type": "text",
        "text": (
            "Stub archetype to enrich:\n```json\n"
            + json.dumps(stub_summary, indent=2)
            + "\n```\n\nThe 4 variant reference PNGs follow, in order variant_0 → variant_3. "
              "Study each image before writing. Ground your metadata in what you see."
        ),
    })

    # Load 4 variants (fail early if missing)
    for i in range(4):
        vpath = folder / f"variant_{i}.png"
        b64 = load_png_b64(vpath)
        if b64 is None:
            raise FileNotFoundError(f"Missing {vpath}")
        parts.append({"type": "text", "text": f"variant_{i}.png:"})
        parts.append({
            "type": "image",
            "source": {"type": "base64", "media_type": "image/png", "data": b64},
        })

    return parts


# ---------------------------------------------------------------------------
# Enrichment via Claude
# ---------------------------------------------------------------------------


def enrich_one(client: anthropic.Anthropic, stub: dict) -> dict:
    """Call Claude for a single archetype. Returns the enrichment dict."""
    thumb = stub.get("thumbnailUrl", "")
    if thumb.startswith("/archetypes/buildings/"):
        folder_name = thumb.split("/")[3]
    else:
        folder_name = stub.get("id", "").replace("_", "-")
    folder = PUBLIC_BUILDINGS / folder_name

    content = build_user_content(stub, folder)

    response = client.messages.create(
        model=MODEL,
        max_tokens=4000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": content}],
    )
    text = response.content[0].text.strip()

    # Strip any accidental markdown fences
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*\n", "", text)
        text = re.sub(r"\n```\s*$", "", text)
    text = text.strip()

    try:
        enriched = json.loads(text)
    except json.JSONDecodeError as e:
        # Dump for debugging
        debug_path = ROOT / "artifacts" / f"enrich_failed_{stub.get('id')}.json"
        debug_path.parent.mkdir(parents=True, exist_ok=True)
        debug_path.write_text(text, encoding="utf-8")
        raise RuntimeError(f"Claude returned invalid JSON (saved to {debug_path}): {e}") from e

    return enriched


# ---------------------------------------------------------------------------
# Merge + splice into catalog
# ---------------------------------------------------------------------------


def merge_with_stub(stub: dict, enriched: dict) -> dict:
    """Merge enriched fields with preserved stub fields."""
    # Preserved (immutable routing + stable fields)
    merged: dict[str, Any] = {
        "id": stub["id"],
        "title": stub["title"],
        "buildingSubcategory": stub.get("buildingSubcategory"),
        "developmentType": stub.get("developmentType"),
    }
    # Add enrichment fields at archetype level (order matters for readability)
    for key in ("aestheticCategory", "description", "generationTags", "styleProfile",
                "prompt", "suggestedWidth_m", "suggestedDepth_m", "minFloors", "maxFloors"):
        if key in enriched:
            merged[key] = enriched[key]
    merged["thumbnailUrl"] = stub.get("thumbnailUrl")

    # Per-variant merge — preserve thumbnailUrl from stub
    stub_variants = stub.get("variants", [])
    enr_variants = enriched.get("variants", [])
    merged_variants = []
    for i, stub_v in enumerate(stub_variants):
        enr_v = enr_variants[i] if i < len(enr_variants) else {}
        mv: dict[str, Any] = {}
        # Use Claude's id if provided; else fall back to stub's
        mv["id"] = enr_v.get("id") or stub_v.get("id")
        mv["label"] = enr_v.get("label") or stub_v.get("label")
        mv["description"] = enr_v.get("description") or stub_v.get("description", "")
        mv["thumbnailUrl"] = stub_v.get("thumbnailUrl")  # preserve path
        mv["color"] = enr_v.get("color") or stub_v.get("color", "#888888")
        for key in ("minFloors", "maxFloors", "suggestedFloorHeight",
                    "suggestedAreaSqm", "facadeDetail", "roofDetail"):
            if key in enr_v:
                mv[key] = enr_v[key]
        merged_variants.append(mv)
    merged["variants"] = merged_variants
    return merged


def splice_archetype(text: str, arch_id: str, new_obj: dict) -> str:
    """Replace the archetype block in the catalog text with new_obj's JSON.

    Text-level replacement (never json.dump the whole catalog — preserves
    every other entry's formatting and avoids the thumbnailUrl corruption
    bug documented in CLAUDE.md).
    """
    needle = f'"id": "{arch_id}"'
    idx = text.find(needle)
    if idx < 0:
        raise RuntimeError(f"Archetype {arch_id} not found in catalog")

    # Walk backward to the enclosing '{'
    start = text.rfind("{", 0, idx)
    # Walk forward to matching '}'
    depth = 0
    i = start
    while i < len(text):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                end = i + 1
                break
        i += 1

    # JSON-serialize new_obj with indent=4, then shift inner lines 4 more
    # spaces to match the archetype-in-array indentation (outer array is at
    # 4-space indent; the archetype object's own inner keys are at 8-space).
    raw = json.dumps(new_obj, indent=4, ensure_ascii=False)
    lines = raw.split("\n")
    shifted = lines[0] + "\n" + "\n".join("    " + line for line in lines[1:])

    return text[:start] + shifted + text[end:]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def parse_args() -> dict:
    args: dict[str, Any] = {"limit": None, "ids_file": None, "dry_run": False, "sleep": 2.0}
    for a in sys.argv[1:]:
        if a.startswith("--limit="):
            args["limit"] = int(a.split("=", 1)[1])
        elif a.startswith("--ids-file="):
            args["ids_file"] = Path(a.split("=", 1)[1])
        elif a == "--dry-run":
            args["dry_run"] = True
        elif a.startswith("--sleep="):
            args["sleep"] = float(a.split("=", 1)[1])
        elif a in ("-h", "--help"):
            print(__doc__)
            sys.exit(0)
    return args


def load_orphan_ids(ids_file: Path | None) -> set[str]:
    path = ids_file or ORPHAN_IDS_FILE
    if not path.exists():
        print(f"ERROR: orphan IDs file not found: {path}")
        sys.exit(1)
    return {line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()}


def main() -> int:
    args = parse_args()
    orphan_ids = load_orphan_ids(args["ids_file"])

    # Exclude the two already-enriched pilots
    PILOTS_ALREADY_DONE = {
        "administrative_faculty_office_building",
        "regional_hospital_medical_center",
    }
    orphan_ids -= PILOTS_ALREADY_DONE

    # Load catalog once to locate stubs
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    stubs: list[dict] = [a for a in catalog.get("archetypes", []) if a.get("id") in orphan_ids]

    if args["limit"] is not None:
        stubs = stubs[: args["limit"]]

    print(f"Enriching {len(stubs)} orphan archetype(s)"
          f"{' (DRY RUN)' if args['dry_run'] else ''}")
    print(f"Excluded (already Tier-1): {', '.join(sorted(PILOTS_ALREADY_DONE))}")
    print()

    if args["dry_run"]:
        for s in stubs:
            print(f"  - {s.get('id')}  ({s.get('title')})")
        return 0

    # Backup
    backup = CATALOG.with_suffix(CATALOG.suffix + ".bak-enrich")
    backup.write_bytes(CATALOG.read_bytes())
    print(f"Backup saved: {backup.name}\n")

    # Initialize Claude client
    api_key = load_anthropic_key()
    client = anthropic.Anthropic(api_key=api_key)

    text = CATALOG.read_text(encoding="utf-8")
    succeeded = 0
    failed: list[tuple[str, str]] = []

    for i, stub in enumerate(stubs, 1):
        aid = stub["id"]
        print(f"[{i}/{len(stubs)}] {aid}...", end=" ", flush=True)
        try:
            enriched = enrich_one(client, stub)
            merged = merge_with_stub(stub, enriched)
            text = splice_archetype(text, aid, merged)
            # Validate incrementally — parse check
            parsed = json.loads(text)
            assert any(a.get("id") == aid for a in parsed.get("archetypes", []))
            succeeded += 1
            print(f"OK (variants: {[v.get('label') for v in merged.get('variants', [])]})")
        except Exception as e:
            failed.append((aid, str(e)))
            print(f"FAILED: {e}")
            continue

        # Write after each success so a mid-run crash doesn't lose work
        CATALOG.write_text(text, encoding="utf-8")

        time.sleep(args["sleep"])  # gentle pacing

    print()
    print(f"=== Done: {succeeded}/{len(stubs)} succeeded ===")
    if failed:
        print(f"Failed: {len(failed)}")
        for aid, err in failed[:10]:
            print(f"  {aid}: {err}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
