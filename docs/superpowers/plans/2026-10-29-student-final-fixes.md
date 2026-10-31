# Student final fixes implementation plan

> **For agentic workers:** Use superpowers:executing-plans or scoped parallel agents for the independent fixes below. Preserve unrelated changes.

**Goal:** Repair the four failures identified in the October 29 student stress test and verify the original workflows locally.

**Architecture:** Keep existing exact-source, placement, and visibility validation. Correct surface classification and street geometry ownership; improve bounded placement candidates; make private local tower installation work for a second student account without sharing private entries or changing GLBs.

**Tech stack:** React/TypeScript/Vitest, FastAPI/SQLAlchemy/pytest, local Postgres/MinIO, browser verification.

**Spec:** The user's “Let's fix the remaining items” refers to the October 29 stress evidence at `D:/CityPrompt-review-artifacts/storage-and-stress-20261029/test-summary.json`.

## Constraints and review focus

- No GLB edits, deployment, paid generations, or remote publication.
- Preserve private model ownership and immutable stored bytes.
- Recognized flat surfaces may accompany a verified compiled scene; unknown polygons and stale source claims remain rejected.
- Street repairs must preserve genuine crossings and junction ownership.
- Nearby fitting must preserve boundary, collision and distance limits; a failed proposal must not mutate the saved object.
- Original browser scenarios and reloads are separate acceptance gates from unit tests.

## Tasks

- [x] Reproduce surface rejection in frontend and backend tests; repair eligibility and landscape scope binding.
  Files: GlobeAIRenderPanel.tsx, residual_landscape.py, direct_3d_render.py and associated tests.
- [x] Reproduce long-street bands; preserve longitudinal travel surfaces while retaining actual crossings.
  Files: nativeStreetProgram.ts, nativeStreetContinuity.test.ts, runtime review checklist.
- [x] Reproduce and repair nearby court fitting, including the original saved scene; retain full collision checks.
  Files: snapPlacement.ts/test.ts.
- [x] Reproduce local tower installer collision across accounts; support additive private per-owner bindings and install for the disposable student account.
  Files: brick_podium_storeys.py, regular_tower_storeys.py, landmark_tower_storeys.py, shared identity helper and regression tests.
- [x] Run narrow frontend/backend suites and TypeScript checks; review diff and source changes.
- [x] Serve the exact reviewed source locally; test surface capture, tower height/reload, court rotation and long streets in the browser.
- [x] Save accurately labelled screenshots and review notes, upload to the existing private Google Drive review folder, verify metadata and record receipts.

## Checkpoint

Final combined verification passes 210 frontend and 399 backend/installer tests, TypeScript and diff checks. Browser retests pass the four original failures. A secondary surface-freshness finding was repaired and independently rechecked for both image/video preflight. See `docs/STUDENT_FINAL_FIXES_2026-10-29.md` for the scope and explicit unrun gates.

Delivery completed: 15 files verified in private Drive folder `1aroll2NQfIETlqj6VrxJrAZFz19211f3`; local receipts retained under the external evidence directory. Source implementation checkpoint: `c7d3a8ebf`. No remote push or deployment.
