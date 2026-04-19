# CHANGES AT A GLANCE — Polygon + Subvariant Authority (Globe)

Date: 2026-04-18
Plan: `artifacts/prompt-audit/POLYGON_AUTHORITY_PLAN.md`

## Goals

1. Polygon the user draws = footprint Gemini renders.
2. Subvariant image the user picks = style Gemini renders.
3. No quality regression on scenes that currently work.

## Before / After (signals sent to Gemini)

| Signal | Before | After (phase) |
|---|---|---|
| Scale token in zone line | archetype `suggestedAreaSqm` literal (e.g. `~150m²` regardless of polygon) | computed `polygon LxWm (AREAm²)` from polygon itself (Phase 2) |
| Shape descriptor | absent | adjective: rectangular / elongated / near-square / L-shaped / irregular (Phase 3) |
| MANDATORY rule | permissive — mentions "landscaping" inside building footprint | "polygon edges ARE walls; polygon size is authoritative" (Phase 4) |
| Variant-resolved prompt text | `getMapOverlayPrompt` matches by archetypeId, never reads selected variant | selected variant shadows parent fields in both overlay prompt and archetype info (Phase 5) |
| Variant-level JSON overrides | absent | optional fields (facadeDetail, roofDetail, renderPrompt) on variants; 3-archetype pilot (Phase 6) |
| Roof vs facade emphasis at nadir | always uses `mapOverlay` (facade-heavy); `roofView` never fires | pitch < 20deg uses `renderPrompt.roofView`; features branch on pitch band (Phase 7) |
| Mask dilation | 8 px constant (50% inflation on 4 m polygon) | 5% of min edge, clamped [2, 8] px (Phase 8) |
| Feather | outward blur | erode -> blur -> clamp, inward-only (Phase 8) |
| Backend image labels | hardcoded "3D clay massing model" / "Apply the exact style" | honor client-supplied role; fallback to today's text (Phase 9) |

## Files touched (with anchor)

| File | Approx LOC | Anchor |
|---|---|---|
| `frontend/src/components/viewer/globe/polygonMetrics.ts` (new) | +60 | top-level |
| `frontend/src/components/viewer/globe/useGlobeAIRender.ts` | ~50 changed | `:334, :487-500, :652-738, :744-879` |
| `frontend/src/data/buildingArchetypes.json` | +30 (pilot 3 archetypes, text-level splice) | variants arrays |
| `backend/app/api/v1/render.py` | ~20 | `:54-58, :378-465` |

## Validation (2 lines)

6 fixture polygons (rectangle, elongated, near-square, L, tiny, huge) x 2 pitches (0deg, 45deg) x 2 variants = 24 renders per regression pass, ties to `siteforge-render-diagnostics` skill in `docs/tooling-plan-v3.md` Phase 4b.
Success criteria: polygon coverage 85-105%, subvariant recognizable in blind compare, <=0.5% changed pixels outside mask.

## Out of scope (3 lines)

No Mapbox pipeline changes (dead code per 2026-04-18 user confirmation).
No prompt-builder architectural rewrite; surgical edits only.
No archetype schema rewrite; variant fields are optional additive.

## Priority if time-boxed

1. Phase 4 (MANDATORY port, one-line edit).
2. Phase 2 (computed area swap in scale token).
3. Phase 5 (variant-resolved prompt text).
4. Phase 7 (pitch-branched roofView selection).
5. Phase 3 (shape adjective).

Stop there if time is tight; Phases 6, 8, 9 are long-tail polish.
