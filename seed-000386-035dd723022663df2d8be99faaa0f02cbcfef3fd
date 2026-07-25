# Transport Standards — Catalog Gap-Check (Step D)
**Date:** 2026-06-25 · **Branch:** `side/transport-standards` · Source: `frontend/src/data/streetPathArchetypes.json` (this working tree, incl. WIP)

## Headline
**You do not need to author Calgary geometry — it already exists. You need to (1) WIRE the existing geometry into the faithful render path and (2) add a standards index.** The real *authoring* gaps are **TAC + NACTO** (needed for the COMPARE differentiator) and **CSPS033 fire access** (the SURFACE wedge).

## What's in the street catalog
115 street archetypes / 8 categories. Split by relevance to this side project:

| Category | Count | In scope? | Notes |
|---|---|:--:|---|
| `calgary_street_manual` | 13 | ✅ core | All 13 carry a to-scale `section` block (`confidence: "exact"`, figure refs) + vector `section.svg` |
| `traffic_safety_vision_zero` | 22 | ✅ core | Calgary Street Manual Ch10 calming; 7 diagram-tagged, ~10 with section data |
| `alberta_bike_design_guide` | 8 | ✅ core | Alberta Bicycle Facilities Design Guide; 6 with section data |
| `intersections` | 13 | ✅ core | Street Manual Ch9; 4 diagram-tagged, several with section data |
| `pedestrian_oriented` | 20 | ❌ out | Character archetypes (Amsterdam, Barcelona…) — belong to main City Prompt |
| `cycling_oriented` | 3 | ❌ out | Bridges/pathways, character |
| `transit_oriented` | 7 | ❌ out | Generic BRT/LRT character |
| `auto_oriented` | 29 | ❌ out | Generic global street character (Haussmann, Parisian…) |

**In-scope transportation archetypes: 56.**

## The render-readiness finding (the crux)
- **11 archetypes are `technical-diagram`-tagged** → hit the geometry-faithful, building-free render path **today**. (The `*_diagram` siblings: chicane, curb-extension, raised-crossing, speed-cushion/hump/table, two-stage-median, compact + mini roundabout, protected + raised intersection.)
- **36 archetypes carry an exact to-scale `section` block but are NOT diagram-tagged** → they render off the photoreal card, so the standard's precise widths get softened. **This includes all 13 Calgary Street Manual cross-sections.** Example: `calgary_collector` has `section.zones` (ROW 20.0 m, MUP 3.0, boulevard 3.4, lanes 3.3…) AND a `sectionSvgUrl` vector — the faithful geometry is *right there*, just not used as the conditioning input.
- **No archetype has a populated standards-citation field** (`calgaryStreetManualRef` is referenced in code but empty; only the `section` block carries `figure`/`draftStatus`). → the Standards Browser needs its own index.

## Coverage vs. the standards corpus
| Standard | Coverage | Render today | Action |
|---|---|---|---|
| **Calgary Street Manual — cross-sections (Ch4 / Complete Streets TP021 / CTP classes)** | 13 archetypes, exact section data + vectors | Card only (softened) | **Wire section vector → diagram path** |
| **Calgary Street Manual — traffic calming (Ch10)** | ~14 (7 diagram + section) | Diagram ones faithful | Mostly covered |
| **Calgary Street Manual — intersections (Ch9) / TAC roundabout** | 13 (4 diagram + section) | Diagram ones faithful | Mostly covered |
| **Alberta Bicycle Facilities Design Guide** | 8 (6 with section data) | Card only | Wire section → diagram |
| **Neighbourhood Streets / Residential Street Design / Pedestrian / Bicycle policies** | Piecemeal across the above | Partial | Label/organize in index |
| **Roundabout Policy (TP016)** | 4 roundabout archetypes (2 diagram) | Diagram ones faithful | Optional TAC-dimensioned variant |
| **CSPS033 — fire/EMS access width** | ❌ none | NO | **AUTHOR — the SURFACE wedge** (pair with existing `calgary_local`) |
| **TAC Geometric Design Guide (GDGCR) cross-sections** | ❌ none (pending) | NO | **AUTHOR — needed for COMPARE** |
| **NACTO Urban Street / Bikeway cross-sections** | Implicit in Vision Zero dims, not a labeled set | Partial | **AUTHOR NACTO set — needed for COMPARE** |
| **TAC MUTCDC (signs/markings)** | ❌ none | NO | Author later (lower priority) |
| **AASHTO Green Book** | ❌ none | NO | Author later (lower priority) |

## Verdict by pillar
- **SHOW — ~90% ready.** 11 render faithfully now; 36 need only a *wire-up* (feed the existing `section.svg`/`section` as the diagram-conditioning ref, or add the `technical-diagram` tag). Net-new = the standards index + the wiring. **No Calgary geometry authoring required.**
- **COMPARE (Calgary vs TAC vs NACTO) — blocked on authoring.** Only Calgary exists. The TAC GDGCR set (pending) and a labeled NACTO cross-section set must be authored. This is the main lift for the engineer-killer view.
- **SURFACE (fire vs walkability) — one author job.** Author the CSPS033 fire-access cross-section; pair-partner (`calgary_local`) already exists.

## Decision this gates (for Step A)
**How do the 36 section-data archetypes render faithfully?**
- **Option 1 — feed `sectionSvgUrl` as the diagram-conditioning reference** at render time (don't change the catalog; the Standards Browser swaps the conditioning input). Cleanest, non-destructive, reuses the proven path. **Recommended.**
- **Option 2 — add `technical-diagram` to their `generationTags`** (text-splice, never json.dump). Simpler wiring but changes the shared catalog + may alter their behaviour in main City Prompt.

Recommendation: **Option 1** — keep the side project's render strategy in its own layer, leave the shared catalog untouched.
