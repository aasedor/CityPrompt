# Batch A: ready for browser verification

Status: **implemented and automatically checked; browser/visual acceptance
pending**. User requested implementation here and browser testing with another
model. No browser was started, API generation purchased, or push performed.

Test worktree `C:/dev/CityPrompt-grounding-edit-race`, branch
`codex/grounding-edit-race-hardening`. It includes park-race checkpoint
`4792bd950` and the follow-up changes described below, based on main `7378ce2a7`.
Read `GROUNDING_EDIT_RACE_HANDOFF_2026-09-19.md` for the earlier race cases and
`NEXT_EDIT_PLAN_2026-09-19.md` for the batch boundaries.

## Reproduced and corrected

### Building footprint support

Five new failing regressions exposed incomplete site-boundary classification:
thin crossings, a site inside an offset building footprint, a narrow concave
notch, crossings while ground is pending, and detached pads whose shared origin
is on site while both pads are outside.

The contact solver now uses the actual site polygon, splits footprint edges at
boundary crossings, and checks the intervals between crossings. Fixed 2 m
elevation probes alone cannot establish polygon containment. The provider exposes
the current boundary while sampling; a ready snapshot supplies the same domain.
Boundary analysis is bounded to one million edge comparisons. Legacy callers
without an explicit domain retain their prior predicate-based path.

Fully outside pads retain outside-site behavior. A partly unsupported footprint
is unresolved; it must not receive a guessed foundation. Native dimensions,
separate modules, terrain interpolation and the existing 3 m foundation limit
remain unchanged. No RLASM model, catalogue entry or review status was changed.

### Capture freshness during tile changes

Two lifecycle regressions showed that capture could accept stale ground between
a relevant tile event/renderer replacement and the next animation frame.
Verification now becomes pending on invalidation while the last safe display
surface remains visible. A synchronous freshness guard also rejects a caller
holding the earlier React state before its replacement commits. Existing
image/video capture and end-of-capture assertions use that guard.

Unmount retires that evidence. Reopening remeasures; metadata-only saves do not
force new measurements. Existing off-site event filtering, failed-refresh display
retention, two-pass verification and bounded retry behavior continue to pass.

## Automated checks

From this worktree's `frontend` directory:

```powershell
npx vitest run src/components/viewer/globe/buildingGroundContact.test.ts src/components/viewer/globe/importedBuildingGround.test.ts src/components/viewer/globe/SharedSiteGroundProvider.test.tsx src/components/viewer/globe/sharedGroundSelection.test.ts src/components/viewer/globe/sharedGroundCapture.test.ts src/components/viewer/globe/sharedSiteGround.test.ts src/components/viewer/globe/parkTerrain.test.ts src/components/viewer/globe/AutomaticParkGround.test.tsx src/features/pickPlace/saveAutomaticParkGround.test.ts src/store/undoRevision.test.ts src/store/undoProjectScope.test.ts src/hooks/useSiteZones.test.ts
npm run type-check
npx eslint src/components/viewer/globe/buildingGroundContact.ts src/components/viewer/globe/buildingGroundContact.test.ts src/components/viewer/globe/SharedSiteGroundProvider.tsx src/components/viewer/globe/SharedSiteGroundProvider.test.tsx src/components/viewer/globe/sharedGroundCapture.ts --max-warnings=0
```

Final focused suite: 141 tests across 12 suites passed. TypeScript and changed-file
lint passed. No new dependencies, runtime source files or saved-data schema.
Runtime asset source reachability is unchanged; no manifest regeneration needed.

## Setup for the testing model

- Verify the exact branch and clean Git status. Other worktrees contain unrelated
  uncommitted changes; do not copy these fixes over them or test their code by mistake.
- This source worktree is sparse. `node_modules` is an ignored junction to the
  existing transformation worktree. Set `CITYPROMPT_PUBLIC_DIR` to the existing
  verified hydrated assets before starting Vite; check asset availability first.
- Verify backend availability and `API_PROXY_TARGET`, then choose an unused local
  frontend port. Preserve any existing user session. Earlier runtime notes are in
  `TRANSFORMATION_HANDOFF_2026-09-16.md`; recheck their process/port assumptions.
- Keep paid AI generation disabled. Use free deterministic captures/guide previews
  for readiness checks. The separate mission US $10 API ceiling is unchanged.
- Duplicate a test project. Never reshape the frozen Gold Standard to create or
  conceal a failure. Site-edge cases may require a disposable imported fixture
  because normal placement correctly rejects plots outside the site. Do not
  weaken placement validation merely to construct a test.

## Browser acceptance sequence

1. **Normal contact:** place a reviewed building fully inside a flat site and
   another on supported slope. Inspect base contact from above and pedestrian
   height. Rotate/move, undo/redo, reload and compare coordinates and dimensions.
2. **Site-edge recovery:** in a disposable fixture, test a narrow boundary crossing
   a building, a concave notch under a footprint, and a site enclosed by a larger
   footprint. Expect a grounding warning/unresolved capture, not a guessed base.
   Move the affected building fully inward and verify recovery. Previously accepted
   but unsupported buildings may now show the existing ground warning.
3. **Detached pads:** test separate modules with the measured site lying only in
   their intervening yard. Do not treat that yard as one building foundation.
   Also verify a legitimate footprint sharing an exact boundary edge.
4. **Tile refinement:** once ground is ready, navigate enough to refine relevant
   tiles. Last safe geometry should remain visible while capture waits for ground
   verification. Once two stable passes finish, a free capture should succeed.
   Look for flicker, Z oscillation, excessive waiting and repeated network calls.
5. **Failure/recovery:** safely interrupt context loading, restore it and retry.
   Verify no guessed captured grade, lost design or permanently stuck progress.
   Navigate away and reopen; wait for fresh measurements and compare saved geometry.
6. **Earlier park race:** execute the preceding park handoff's edit-while-sampling,
   pause/resume, queued edit, archetype-change and reload checks.

Inspect console and failed network requests throughout. Save and visually inspect
screenshots before/during/after refinement, plus API revisions and geometry before
and after reload, outside Git (suggested root:
`C:/dev-artifacts/CityPrompt/grounding-batch-a/`). Use consistent cameras.

Browser timing may not reproduce the sub-frame capture race deterministically;
report that honestly. Automated lifecycle tests cover its event ordering. Browser
acceptance must still prove visible stability and usable recovery. No paid render
or AI video is required for this gate.

Report PASS/FAIL/NOT TESTED for each step with evidence and a bounded defect list.
Grounding acceptance and Batch B implementation remain pending until review of
the relevant results. No professional image, entrance-accessibility, comprehensive
performance or full mixed-object release pass is claimed here.
