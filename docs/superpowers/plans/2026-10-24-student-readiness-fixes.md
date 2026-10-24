# Student readiness fixes implementation plan

> **For agentic workers:** Use superpowers:executing-plans to implement this plan task by task.

**Goal:** Correct the seven observed student usability failures, remove resize vertices from fixed-size models, and repeat a bounded student UI exercise.

**Architecture:** Preserve the existing catalogue and geometry. Reuse boundary containment validation, derive editing affordances from actual resize capability, distinguish flexible parks from native assemblies, and make preview capture cancellable with a browser-compatible media URL.

**Tech stack:** React/TypeScript/Vite/Vitest; FastAPI/Python/pytest; local browser verification.

**Spec:** User-approved fixes from the second student stress test (`artifacts/student-stress-test-20261024/report.txt` in the primary workspace), plus the user's explicit instruction to show resize vertices only on resizable things.

## Constraints

- Work from tested release 62e31ad; preserve all unrelated source work.
- No archetype mesh scaling, paid generation, public deployment or push.
- Preserve public-road connection exceptions and ordinary Undo/Redo.
- Unknown quantities remain unknown; automatic catalogue models must not advertise an unavailable rebuild workflow.
- One bounded free preview; test cancellation before a complete run.

## Review focus

- A rejected boundary edit retains prior geometry and useful feedback through reload.
- Fixed objects cannot resize via visible or invisible handles; rotate and move remain available.
- Flexible park identity and adaptive controls survive save/reload.
- A cancelled preview cannot publish late results, call paid generation or leave capture state active.
- Media object URLs are revoked on replacement/unmount; browser playback and download remain usable.

## Tasks

1. [x] Boundary safety: add a failing endpoint regression; call `_assert_boundary_covers_existing_zones` before mutation; verify rejected and valid edits plus frontend rollback/error feedback.
2. [x] Editing affordances: regression for fixed versus resizable handles; suppress pointer targets as well as visible corners; align fixed-size placement hints and rejection guidance.
3. [x] Park identity: regression for flexible asset resolution and editor control eligibility; preserve the selected flexible label and exclude incompatible native-layout upgrades.
4. [x] Report guidance: regression for automatically rendered catalogue plots; distinguish unresolved certified quantities from stale legacy 3D without inventing counts.
5. [x] Video preview: regressions for cancellation/late result ownership and media URL lifecycle; propagate AbortSignal through capture and encoding; use a Blob URL for playback and download, with visible playback errors.
6. [x] Map-context recovery: expose the working existing-street recovery action when automatic map context fails.
7. [x] Verification: narrow Vitest/pytest, TypeScript check, relevant build checks, browser student exercise against corrected local build, independent final review, diff/status checks and a coherent local checkpoint. Download-completion and provider-preflight limits are recorded below.
8. [x] Closest fitting placement (user follow-up): reuse placement and movement snapping, keep native size and orientation, and prefer a nearby combined boundary/neighbour correction over the first farther clear candidate. Preserve bounded search and existing path reservations; explain a conflict only when no nearby fit is found.

## Execution ledger

- Baseline: isolated managed worktree at release 62e31ad; branch `codex/student-readiness-fixes-20261024`; locked frontend dependency install in progress.
- Ruling: execute the requested bug fixes directly from the reproduced report; no redesign of model geometry or catalogue expansion.
- Boundary regression: observed RED (both boundary endpoint cases), then GREEN (15 backend containment/concurrency tests).
- UI regressions: observed RED for fixed-size hints, flexible identity and fixed-model vertices; then GREEN (29 tests). Resize vertices and their 3D hit targets are omitted together; move/rotate remain.
- Flexible identity cause: shape-first selection passed `asset.properties` without the picker identity. New drawings now carry placement properties; old drawings resolve their exact programme before the generic parent fallback.
- Ruling: defer the coherent commit until the required localhost UI check, as required by CLAUDE.md.
- Immediate boundary feedback: RED then GREEN in the zone hook; rejected drags return false so globe preview snaps back. A racing API rejection clears selection before a possibly slow refetch.
- Report guidance: RED then GREEN; 55 relevant backend tests pass. Unknown counts remain unknown and automatic models no longer advertise a hidden rebuild step.
- Video regressions: RED confirmed missing cancel, missing Blob media URL, ignored encoder cancellation and a non-cancellable tile wait. GREEN: 91 targeted tests across six files after implementation.
- Optional map context: retained the external-service failure caveat, added the exact working Layers recovery path and extended the message to eight seconds. External service availability is not claimed repaired.
- Live report check found fixed native catalogue objects omit `pick_place_automatic_3d` but retain `pick_place_asset`. Added the real-format regression and mixed legacy/automatic guidance; RED then GREEN (57 backend tests).
- Closest-fit follow-up: observed a 20.02 m snap when a valid diagonal under 15.7 m existed. Keep a usable fallback while exploring closer candidates; 56 snapping, boundary and entrance tests pass, including a slight combined conflict resolved within 1.3 m. The existing search remains bounded at 30 m and 64 expansions.
- New visual finding during the repeat exercise: dark-mode studio controls combined pale text with pale cards or dark text with dark buttons. Added matching surface/foreground overrides; verify site, design and report views in both themes.
- Final checks: 292 tests in 16 frontend files, 57 backend tests, TypeScript check and production bundle pass. Build uses the existing hydrated public catalogue and skips duplicating unchanged public files; four existing landing media files were hydrated from local LFS storage. Existing large-chunk and mixed-import warnings remain.
- Browser: disposable editor, irregular 1.0 ha site, three fixed houses, one five-corner flexible park, one three-point lane, 18 trees and six people. Invalid boundary shrink rejected with named objects; valid expansion/Undo/reload passed. Park dimensions and all 24 details persisted. Fixed move/rotate/no-corners persisted, and edge/overlap placements snapped without size or rotation changes.
- Free preview: Cancel and Escape stopped active preparation and restored controls. One full 8-second, 192-frame H.264 preview took about four minutes. Edge reported 1280x720, duration 8, readyState 4, no media error; native Play advanced to 6.742861 seconds while unpaused.
- Independent review covered the tracked diff and all new source/tests. It found one new lime-button contrast regression; paired foreground exceptions corrected it. Both actual style controls now show rgb(21,21,21) on rgb(190,242,100) in dark mode. Final code review approved with no remaining Critical/Important findings.
- Verification limits: the actual Download link was activated, but browser policy blocks its internal download-history page, so completed-file verification is not claimed. The isolated QA API lacks a provider key, so paid-video preflight is not validated. No paid generation was requested.
- Remaining usability observations: four-minute preview preparation is slow; a tree canopy can intercept a click intended for a building underneath. The final test uses a large desktop viewport, not mobile or concurrent-user load.
- Evidence: `artifacts/student-fixes-stress-20261024/report.txt` and screenshots in the primary workspace. Source changes stay on this isolated branch; generated output stays ignored. Preserve this worktree and do not merge or push into the dirty primary checkout.
