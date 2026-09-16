# Student transformation — user-requested pause

Paused for user exploration and remaining account usage on 16 September 2026.
The whole mission is **not complete**. Do not equate individual verified slices
with release acceptance. Consult `STUDENT_TRANSFORMATION_GATES.md` for details.

## Completed and verified slices

- Architecture audit and frozen Gold Standard baseline: 16 buildings, streets,
  intersections, two parks and five repeatable views.
- Site → Design → Present navigation; manual authoring remains primary.
- Canonical catalogue discovery: 468 eligible entries at audit time, search,
  categories and authoritative references. No unpublished family promotion.
- Building placement/street-facing, move, rotate, type/height/resize controls,
  truthful detailed-model fallback and undo.
- Street drawing, T/four-way/angled connections, type/width editing and undo.
- Reviewed park placement, recessed surface handling and a seating-edit pilot.
- Camera startup ownership and recovery from rejected ground placement.
- Current-view image controls, explicit people/vehicles toggles, failure/fallback
  handling and provenance. **All 22 original render styles restored** to the
  primary picker after the user's correction; retain their identities and labels.
- Boundary undo after background context enrichment; safe concurrent-edit checks.
- Three older projects load with saved geometry/identity preserved; boundary-free
  projects open in Design. One older project edit/undo/reload verified.
- Free deterministic video preview and download pilot; see its checkpoint.
- Bounded alternative-context pilots documented; further LiDAR/splat work deferred
  by the user.

## Main remaining work, in priority order

1. Grounding release gate: mixed-object flat/slope/entrance/contact matrix,
   prepared-site edges, asynchronous context refinement and reload. Google visible
   surfaces include roofs; do not use those as surveyed ground or alter the frozen
   benchmark to conceal defects.
2. Environment and interactive appearance: extend existing semantic placement;
   verify collisions/entrances, reviewed identities and measured performance.
3. Professional image acceptance: closer RLASM/public-realm views, same-camera
   source/output comparisons and explicit entourage tests. One real image exists,
   but professional quality and detailed architectural fidelity are not accepted.
4. Video Start→End, named camera presets, semantic Community Tour and simpler
   primary UI. Verify deterministic guides before any paid finishing.
5. Broader persistence/older-project editing, accessibility/responsive and failure
   recovery; same-benchmark performance measurements.
6. Fresh complete student journey, professional/grounding/archetype/street/park
   acceptance and final evidence report.

## Local runtime and recovery

- Worktree: `C:/dev/CityPrompt-student-design-transformation`
- Branch: `codex/student-design-transformation`; local commits only, no push.
- Original dirty OneDrive checkout remains untouched.
- Frontend: `http://127.0.0.1:5174`; backend: `http://127.0.0.1:8000`.
- PostgreSQL/Redis/MinIO local stack remains running. API harness:
  `C:/dev-artifacts/CityPrompt/student-design-transformation/runtime.py serve`.
  It loads Maps for the local test, with image/video AI credentials disabled.
- Heavy assets and screenshots remain outside Git in the same evidence root.
  Do not mutate externally hydrated/hardlinked authoritative assets.
- Gold Standard `e18c8436-2612-4548-990e-0fa506748efd` is a frozen benchmark.
  Prefer a new project for experimentation.
- API ledger: one image estimated US $0.116525 plus US $2 conservative Maps
  reserve = US $2.116525 accounted for against the US $10 ceiling. No paid video.
- Latest video source checks and first full guide capture pass; recheck progress
  labels and history-request deduplication in the next full browser capture.

Use checkpoint documents and external evidence to resume; do not restart the
audit or re-run paid image validation without an evidence-backed reason.
