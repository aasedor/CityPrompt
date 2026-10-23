# Claude asset local trial implementation plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Trial verified Claude buildings, parks and streets in the current local CityPrompt app.

**Architecture:** Add a finite development-only registry using the existing fixed-native building and public-realm review loaders. Preserve exact source assets and saved IDs. Production discovery excludes the cohort.

**Tech Stack:** React/TypeScript, Three.js, Vitest, existing local FastAPI/PostGIS stack.

**Spec:** `docs/superpowers/specs/2026-10-22-claude-asset-local-trial-design.md`

## Global constraints

- Source commit `2e6f4860b75545aebe5a9cccabb845f3943ba8e9`; 31 eligible fixed scene trials, two oversized bridges held.
- Local development only; no publication or paid generation.
- Preserve exact originals. Latest user correction requires separate park-only derivatives that remove off-site buildings and their dependent features, with fresh hashes and scoped independent review; retained geometry and materials stay unchanged.
- Preserve all pre-existing work and source originals; new generated evidence stays external.

## Review focus

- Production must not discover this local-only cohort.
- Saved exact revisions must not silently inherit another candidate.
- Asymmetric source bounds must stay within the plot after the existing single axis conversion.
- Fixed street scenes must not become stretchable routes or affect existing adaptive streets.
- Missing/unprepared ground or failed model loads must remain visible capture failures.

### Task 1: Local fixed-model pilot registration

**Files:** Create `frontend/src/data/claudeAssetLocalTrial.json`, `frontend/src/features/pickPlace/claudeAssetLocalTrial.ts`, and its test. Modify `assetRegistry.ts`, `canonicalCatalogue.ts`, `publicRealmTrial.ts` and `nativeStreetModelTrim.ts` only for the finite local cohort.

**Interfaces:** `localClaudeAssets(enabled: boolean): PlaceAsset[]`; exact public-realm fixtures use the existing placement contract with native centering opted in.

- [x] Write tests for disabled discovery, exact saved IDs/revisions, fixed dimensions/rotation, category binding and unchanged source transforms.
- [x] Run the tests and observe the missing-cohort failure.
- [x] Register the first building/park/street; copy verified public assets externally; use the existing source hash guard.
- [ ] Run narrow Vitest and type-check, then trial all three through the local UI and record results.

### Task 2: Bounded cohort and evidence

**Files:** Expand only the local trial JSON. Create `docs/CLAUDE_ASSET_LOCAL_TRIAL_2026-10-22.md`; external per-asset evidence and screenshots.

**Interfaces:** Same fixed-model registry as Task 1. No canonical publication or new backend capability implied.

- [ ] Read source reviews and boards, preserve holds and copy only exact eligible bytes.
- [ ] Apply the pilot path to the remaining eligible assets, verifying every URL, hash, scale and category.
- [ ] Exercise mixed-scene edits, undo/redo, save/reload and free scene capture. Record actually run per-asset and shared workflow checks.
- [ ] Retain performance holds; do not describe raw heavy parks as laptop-ready.

### User correction: park-only runtime copies

- [x] Remove source-owned context buildings from rink, Halifax garden and stepped plaza in bounded derivatives; preserve original files and park-owned chalets, bandstand, stairs and planting.
- [x] Preserve rejected plaza r001 inspection checkpoint; correct residual house cap in r002.
- [x] Record exact removal provenance, runtime bounds, hashes, six views per derivative and measured draw calls; obtain independent scoped visual review.
- [x] Retire raw rink from discovery while retaining its saved exact ID/bytes. Fail readiness on mismatched saved revision/URL.
- [x] Finish actual local app edit/persistence/capture pilot: all three display; rink select/rotate/move/delete/undo/redo/reload; free exact capture downloaded. Larger original cohort remains pending.

### Task 3: Regression and review

**Files:** Narrow existing regression tests only if their local-only exception requires explicit coverage; final review/evidence report.

- [ ] Run affected Vitest suites, TypeScript check, catalogue delivery checks and backend tests if backend changes are required.
- [ ] Obtain a fresh whole-change review; address material issues and record untested limits.
- [ ] Review diff/status and preserve source changes separately from external generated assets. No push or deployment.
