# Local teaching buildings implementation plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make seven reviewed buildings selectable and usable on localhost before the user's test.

**Architecture:** A finite development-only manifest feeds the existing native model registry, discovery and teaching adapters. A hash-checking local installer hydrates the configured public directory without touching the production seed or database. Ordinary UI trials verify the runtime separately.

**Tech Stack:** React/TypeScript/Vite/Vitest; Python/pytest; existing Three.js native building renderer.

**Spec:** docs/superpowers/specs/2026-10-26-local-teaching-buildings.md

## Global Constraints

- Exactly seven independently reviewed candidates; exclude the unfinished shoebox.
- Development-only trial discovery and exact stable saved identities.
- Fixed native dimensions, no resizing or unsupported floor edits.
- Preserve the 196-choice historical audit and existing projects.
- No paid generation, database migration, production seed activation, push or deployment.
- Verify installed bytes; refuse different bytes at an existing destination.

## Review Focus

- Production build must omit the seven local trial choices and their lesson payload.
- Reopened or stale saved variants must retain exact identity or show an actionable failure, never a generic building.
- Asymmetric model envelopes must stay centred and unscaled, including the side-split.
- New teaching fields must remain bound to exact model revisions and withhold stale classifications.
- Missing/different local asset files must fail installation without overwriting existing content.

### Task 1: Register and install seven exact local trials

**Files:** Add `frontend/src/data/localTeachingBuildings.json`, `frontend/src/features/pickPlace/localTeachingBuildings.ts` and its test; add `tools/local_teaching_buildings.py` and `tools/test_local_teaching_buildings.py`; modify registry, canonical roster and teaching/history adapters.

**Interfaces:** `localTeachingBuildings(enabled: boolean): PlaceAsset[]`; `LOCAL_TEACHING_BUILDINGS`; local exact lesson/history maps. Installer `install(manifest, source_root, public_dir, candidates, apply=False)` verifies locked sources/reviews/native metrics, plans/copies only finite manifest files, and readbacks hashes.

- [x] Write Vitest cases for seven unique entries, production exclusion, saved revision rejection, fixed geometry/no resize, centred asymmetric GLB and exact teaching/stale withholding. Run and observe RED.
- [x] Write pytest cases for dry-run, hash mismatch, conflict refusal and exact model review binding. Run and observe RED.
- [x] Create the manifest from exact existing review/build/source records; wire the existing native renderer and additive lessons; implement the finite installer.
- [x] Run focused frontend/backend-independent tool tests, existing registry/catalogue tests and TypeScript check. Expected: PASS.
- [x] Dry run all seven; install only Victory as a pilot. Verify actual localhost model/reference bytes. Commit the coherent source unit after UI pilot if successful.

### Task 2: Complete ordinary UI runtime review and bounded continuation

**Files:** Add `docs/LOCAL_TEACHING_BUILDINGS_TRIAL_2026-10-26.md`; external/ignored exact per-variant runtime evidence and captures.

**Interfaces:** Consumes the stable trial IDs and hash-checked installer from Task 1. Produces project/evidence URLs, truthful per-variant acceptance records and ready local catalogue.

- [x] Create a disposable vacant prepared-site project through normal UI. Place Victory, rotate/move/undo, save/reload and inspect its exact model. Expected: correct geometry with no persistent generic proxy.
- [x] Install remaining six after the pilot succeeds; place all seven through normal controls. Inspect aerial and close views, save/reopen and browser errors. Expected: same exact variants persist.
- [x] Record applicable passes and all untested runtime rows honestly. Run the Task 1 focused suite and type-check. Expected: PASS.
- [x] Commit only intentional source/review documentation; retain ignored generated evidence separately. Request one fresh whole-branch source review, address important findings with RED/GREEN verification, and leave the local app ready. No push/deploy.
