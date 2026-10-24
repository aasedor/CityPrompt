# Boundary recovery and local/live comparison

> Execute inline with superpowers:executing-plans; use test-driven-development and verification-before-completion.

**Goal:** Correct the observed student boundary recovery problem, restore the published local model library, and compare one matched student journey against production.

**Spec:** The user's request in this chat and `artifacts/student-stress-tests-3-4-20261024/report.txt` in the primary checkout. Invalid outlines must remain editable, recovery actions must be visible on laptop screens, and detailed buildings must be compared with equivalent data.

**Architecture:** Reuse the existing polygon checks through a shared utility before the drawing callback accepts a site. Place draft recovery above the collapsible tools. Keep server validation and durable draft protection. Install existing reviewed seed data into the disposable QA database and bucket only.

**Approaches:** Merely hiding raw errors would leave the lost-draft problem. Merely moving the buttons would still send avoidable invalid writes. Use early validation plus visible fallback recovery; restore published seed data instead of changing building geometry or catalogue definitions.

**Constraints:** Preserve the dirty primary checkout. No publish, push, paid generation, new building construction, or edits to existing live projects. Use a new labelled live QA project if signed in. Keep screenshots and runtime helpers ignored. Restore viewport overrides.

## Task 1 — boundary authoring and recovery

- [x] Add failing tests for crossed and touching outlines, concave valid boundaries, visible compact-screen recovery and readable server fallback errors.
- [x] Extract shared polygon validation from the park validator; check sites before accepting create/reshape. Preserve points when rejected.
- [x] Render recovery before collapsible tool content and replace raw polygon validity diagnostics with actionable copy.
- [x] Run narrow Vitest files, frontend type-check, and reproduce/correct a crossed outline on localhost:5174.

## Task 2 — local model-library parity

- [x] Inventory canonical seed and hydrate existing Git LFS objects.
- [x] Dry run and install one published duplex; inspect it in the existing local test project.
- [x] Install the remaining finite published collection (81 canonical entries total), verify hashes and public database bindings, and refresh existing fallback models.

## Task 3 — matched student journeys and comparison

- [x] Local: new project, invalid boundary recovery, valid site, duplex/grocery, street/park, edge placement, save/reload and free presentation.
- [x] Live: equivalent labelled project and catalogue choices; inspect dimensions, handles, placement, persistence and presentation. Record current build and access limitations.
- [x] Compare code defects separately from data/configuration differences. Save evidence and report; obtain independent code review. Keep verified source checkpoints local.

## Task 4 — defects exposed by the comparison

- [x] Stop counting one assembled native mesh as one dwelling for exact catalogue variants without a reviewed housing programme. Preserve legacy single-house and reviewed catalogue counts. Show unknown quantities with useful guidance instead of a pointless rebuild request.
- [x] Reconcile editing handles with the actual saved shape after a second snap. Cover Undo/Redo, a revision arriving during a drag, and changing selection before pointer release. Verify each newly exposed failure red then green.
- [x] Repeat ordinary-control edge/overlap moves, Undo and Redo in the local app after the final fix. Reproduce the old handle bug on live to distinguish it from a new regression.

## Review focus

Closing clicks and concave polygons must remain valid. A failed outline must retain its points. Retained legacy server errors must have reachable recovery. Model installs must target only the isolated QA services and exact activated seed entries. Production testing must not mutate existing user projects or spend credits.

## Progress

Initial diagnosis: site drafts are cleared before asynchronous server rejection; recovery follows the tall site panel. QA model_library has zero rows and canonical GLBs in the linked worktree were Git LFS pointers. Existing LFS objects hydrated successfully; no model geometry or approval changed.

Completed comparison on 2026-10-24:

- Local project: `http://localhost:5174/projects/7757651a-fe5a-409f-ad32-d1185bb1067e`.
- Live project: `https://www.cityprompt.ca/projects/8feec6f6-f5ef-471c-9e4b-9c1138917cff`.
- Both journeys used Side-by-Side Duplex (17 × 25 m), Brick Corner Grocery (16.1 × 16.4 m), Neighbourhood Main Street (23 m), and Flexible Shade Courtyard. Detailed building geometry, saves, report reasoning persistence after reload, and decoded free image exports were verified on both.
- Restored only the existing 81-entry canonical clay library into the disposable QA database/bucket, following one-model dry run, install, visual pilot, bounded remaining install, and readback/hash verification. Refreshing the earlier local project removed its remaining design-massing warning. No model source, catalogue definition, or production asset was changed.
- Local invalid boundaries retain points and provide corrective instructions. Live clears the points and displays the raw server geometry diagnostic. Live recovery was tested in a wide viewport; a below-fold laptop recovery claim is not established by this comparison.
- Both versions initially reported one compiled dwelling for the duplex. Local now reports Unknown until a reviewed programme or student estimate supplies a quantity. Live retains the old result.
- Both versions exhibited stranded handles after an edge move and Undo. Final local browser checks confirmed near-edge and slight-overlap snapping, plus aligned handles after Undo and Redo. Regression tests also exercise background revision and selection changes during a drag.
- Full rendered park lists: local 42, live 41. The sole local-only entry is `Stepped Terraced Plaza — park only`, documented as a local trial in `docs/CLAUDE_ASSET_LOCAL_TRIAL_2026-10-22.md`. Both list 97 building choices and 53 streets.
- Latest verification: 118 tests across 13 targeted frontend files; 45 student-report backend tests; frontend type-check; production bundle using the existing hydrated public overlay. All passed. Existing bundle-size/mixed-import and pytest fixture-loop warnings remain. Independent source review approved the final changes.
- Evidence and detailed report: primary checkout `artifacts/local-live-student-comparison-20261024/`. Runtime helpers and production build output remain ignored in this worktree's `artifacts/student-readiness-fixes/`.

Limits: independent site outlines at the same test address, different browser zoom levels, two building models visually compared rather than a full catalogue audit. Paid generations and completed download delivery were not retested; live credits remained 848. Changes are local only; no push, merge, production deployment, or catalogue publication was requested or performed. Temporary browser viewport overrides were reset after testing.
