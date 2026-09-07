# Student placement retrial — 6 September 2026

Local follow-up to `STUDENT_READINESS_FOUNDATIONS_2026-09-06.md`.
Initiative: `codex/student-placement-trials`, isolated checkout
`C:/dev/CityPrompt-building-next3`. Browser used port 5178 with backend 8002,
preserving the original checkout and its runtime rather than using 5174.

## Observed and fixed

1. **Entered dimensions differed from saved placement.** On occupied-site trial C,
   selecting the post-war bungalow, entering width 21, and clicking the site
   without pressing Update placement preview saved a 15 × 20 m plot. Undid that
   test placement. Valid input now updates the actual draft immediately. Blank,
   undersized or oversized dimensions and unfinished rotations suspend placement
   instead of silently using old dimensions. The invalid ghost is hidden; desktop,
   centre-placement and project mutation handlers reject unfinished input. Draft
   text survives a temporary hiding/remounting of the controls.
2. **Red previews did not explain apparently empty spaces.** On a 1024 × 768
   viewport, a neighbourhood park appeared to fit beside a bungalow but overlapped
   its surrounding plot. The preview now persistently reports overlap or boundary
   problems. Overlap copy explains that building plots include surrounding space.
   Only status changes propagate from the pointer preview to the planner.

## Browser trials

- C: invalid width 0 followed by a site click created no building. Correcting to
  21 × 20 m with -90° rotation placed the intended plot in clear space. A first
  location near the mid-rise was correctly rejected for overlap.
- C: Undo, Redo and reopening retained the corrected dimensions and compiled
  state. Retained test bungalow: `65c8bfef-68ed-4b12-adfa-a2b6a2f7ce71`.
- Tablet C: park dimensions 22 × 24 m correctly report the archetype's existing
  30 × 30 m minimum. Correcting to 30 × 30 m restores the live preview. Moving
  across existing plots and beyond the boundary changes the visible explanation.
  No additional park was saved in the crowded gaps; cancelled the draft.
- Hillside B: Follow existing terrain reproduced the abrupt-height diagnostic
  (visible sample range approximately 1051.5–1054.3 m). Undo restored the prepared
  1052.5 m surface and building. Setting 1053 m survived reload and produced a free
  exact 3D export. Restored the original 1052.5 m level afterward.
- C: free exact 3D export succeeded after placement. The second existing bungalow
  is occluded by the mid-rise in this camera view; no AI reconstruction was used.
- No uncaught browser errors observed. Desktop viewport restored to 1600 × 1000.

## Verification

- 37 Vitest checks passed: PlacementControls, geometry, sitePreparationSurface,
  sharedGroundCapture and groundReview.
- `npm run type-check` passed.
- Targeted ESLint for PlacementControls, its tests, GlobePlacementPreview and
  geometry passed. React hook, state, accessibility and rerender review completed.
- `git diff --check` passed.
- No backend changes or paid render calls. App balance remained 9,445 tokens.
  Prior beta authorization remains 7 of 10 paid image calls used.

## Remaining work

Prepared ground is still a level surface with abrupt boundaries. It does not yet
design retaining walls, ramps or transitions into sloped existing terrain. Visible
Google surface discontinuities remain unsuitable for automatic ground-following
on hillside B. No terrain thresholds were relaxed in this iteration.

This trial does not resolve AI image drift. Free exports faithfully capture the
current 3D view; prior AI fidelity findings still apply. Tablet testing here used
a resized desktop browser, not physical touch hardware.

Screenshots are outside Git at
`C:/dev-artifacts/CityPrompt/student-beta-2026-09-06/`:
`tablet-park-overlap-explained.png`, `ground-raised-export.png`,
`placement-trials-final-export.png`. Local test project data and these artifacts
are separate from the source checkpoint. No catalogue assets or main deployment
were changed.
