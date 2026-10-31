# Student QA Implementation Plan

> **For agentic workers:** Follow systematic debugging and test-driven development for each bounded fix.

**Goal:** Preserve the first Import GLB action during project startup and expose the project-name fields to accessible queries.

**Architecture:** Trace the real toolbar/dialog lifecycle before changing import behavior. Reuse the existing local dialog state and native HTML label association; keep the production change small.

**Tech Stack:** React, TypeScript, Vitest, Testing Library.

**Spec:** Authorized overnight student QA brief; observed first-click loss and unnamed Edit Project textbox.

## Constraints

- Work on `codex/overnight-student-qa-20261030`; preserve existing hydrated assets and security work.
- No backend, catalogue, asset, budget-limit, staging, or commit changes.
- Notify the root agent before production edits trigger HMR.
- Import must not wait for all Google tiles; preserve the 8448 KiB production JavaScript budget.

## Tasks

- [x] Trace startup and the Import GLB dialog; identify and reproduce the actual loss boundary with a focused red regression.
- [x] Implement the smallest fix and verify the first action remains effective through startup.
- [x] Add accessible-query regressions for Edit Project and the matching New Project name field; observe red, associate their existing labels, then verify green.
- [x] Run narrow Vitest, TypeScript, scoped ESLint, and diff checks. Root agent runs the production build and browser verification.
- [x] Wire the isolated startup regression into the existing browser CI without changing the strict functional browser suite.
- [x] Strengthen startup regression with a pre-click hit test and pending-cover assertions after dialog/file opening, before terrain release.
- [x] Add a red imported-model dimension display regression for wide and narrow controls; format one shared label to one decimal while preserving exact native numeric dimensions and generated-model guidance.

## Review Focus

- Startup transitions must preserve open import/file state.
- Opening an import must not depend on terrain or tile completion.
- Accessible labels must identify the existing fields and preserve submission behavior.

## Evidence

- Initial branch: `codex/overnight-student-qa-20261030`, security checkpoint `1a595406e`.
- Existing dirty files are hydrated LFS image/video/model assets; no overlap with these UI edits.
- Import currently opens through `PlacementPalette` local state, with an eager dialog import and an always-present generated-model callback; no readiness bridge is involved.
- Browser regression RED: an enabled `Import GLB` button cannot receive its first click while the globe is preparing. Playwright identifies the map's `absolute inset-0 z-40` loading cover as the pointer interceptor above the sibling `z-30` toolbar (`artifacts/student-qa-import-red.log`).
- Label regressions RED: Edit Project and New Project cannot resolve the existing name field by accessible role/name (`artifacts/student-qa-label-red.log`).
- Decision: put only the preparation cover below the `z-30` project controls (`z-40` to `z-20`) rather than change all map overlays or add handler, terrain, or tile readiness gates; use the existing native labels to name the two inputs.
- Browser GREEN: `npx playwright test --config playwright.startup.config.ts --reporter=line` passed 1/1. Import opens while terrain is pending and retains the selected GLB after the terrain check completes. The isolated server uses a dummy key and mocks backend responses; CI wiring additionally blocks all requests outside that local server.
- Narrow Vitest GREEN: ProjectEditModal, ProjectListPage, ImportGlbDialog, and StudioControls passed 14/14 tests across four files.
- Scoped ESLint and scoped `git diff --check` passed. Name-label wrappers retain the original styled block text and `mb-1` spacing above each input.
- Full TypeScript check passed. Initial full Vitest: 4,208 passed, 23 skipped, one existing catalogue UI test hit its 5-second limit under concurrent type checking. That file passed 55/55 in isolation. `npm run test -- --run --maxWorkers=2` then passed 4,209 tests with 23 skipped (494 files passed, one skipped) in 327.34 seconds, retaining the same test timeout.
- CI wiring GREEN: `npm run test:e2e:startup` passed 1/1 in 9.9 seconds with all nonlocal requests blocked. The existing browser job's `npm run test:e2e` step is unchanged; a following step invokes the new script. Async globe-module setup may wait 20 seconds; the physical first-click assertion remains limited to 5 seconds.
- Scoped diff checks passed. No files were staged or committed. Hydrated binary assets and prior security work remain untouched. Root retains production build/budget and live UI verification.
- Review follow-up: the strengthened startup test passed 1/1 in 10.4 seconds. Browser hit testing must see the Import button before the click, and both preparation labels must remain visible after dialog/file UI opens, before terrain is released. The reviewer received the receipt.
- Imported-size follow-up RED: wide and narrow regressions expose the unrounded native values. GREEN: 129/129 tests across PlacementControls, generatedPlacement, courtOnlyControls, and releaseCandidateContracts. A shared display label rounds to one decimal and removes unnecessary trailing zeroes; exact native width `24.000001907348633` and depth `26.499999046325684` survive manual and keyboard rotation. Imported models omit the original-plot hint; existing generated-model guidance remains. Scoped lint and diff checks pass; root was notified before this display-only HMR edit.
- Follow-up full TypeScript check passed. Source is frozen again after the authorized display edit. The 4,209-test full-suite receipt predates this formatting change; its latest focused receipt is 129/129. No duplicate full suite was started while root owns final integration verification.
