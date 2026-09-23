# Automatic park grounding: implementation and browser handoff

Status: **implemented; browser and visual validation pending**. The user asked
for coding and narrow automated verification here, with browser testing under
another model. This checkpoint does not accept the grounding release gate.

Branch: `codex/grounding-edit-race-hardening`, based on main `7378ce2a7`.
Local worktree: `C:/dev/CityPrompt-grounding-edit-race`.

## Problem and change

A terrain measurement could finish after a park property edit without any
footprint movement. The sampler accepted it, and persistence used the *new*
cached row revision to authorize a write containing *old* measurements. A save
waiting behind an authored edit in the project write queue had the same issue.
A callback from a retired sampler could also finish after pause/resume.

- Sampling jobs now include the park revision, active site ID/revision and
  fallback elevation, in addition to the footprint.
- Unmounted samplers ignore provider callbacks, including after pause/resume.
- Completion passes the sampled zone to persistence. Inside the existing write
  queue, a different current zone revision discards the result without a request.
- Existing server conflict checks, cache revision checks, undo revision handling,
  measured-grid validation, 60-second deadlines and three-attempt limits remain.

This deliberately restarts a pending measurement after *any* saved row revision,
including a rename. It does not introduce a schema migration, resample already
valid saved park terrain, or change how Google surfaces are interpreted.

## Automated evidence

Three new race regressions failed against main before the fix and pass after it.
Additional checks cover site revision changes, changing park archetype, a newer
cache revision during an in-flight save, and the existing move/retry/undo paths.

From `frontend`:

```powershell
npx vitest run src/features/pickPlace/saveAutomaticParkGround.test.ts src/components/viewer/globe/AutomaticParkGround.test.tsx src/components/viewer/globe/parkTerrain.test.ts src/components/viewer/globe/sharedSiteGround.test.ts src/components/viewer/globe/buildingGroundContact.test.ts
# 44 tests, 5 suites passed
npx vitest run src/store/undoRevision.test.ts src/store/undoProjectScope.test.ts src/hooks/useSiteZones.test.ts
# 64 tests, 3 suites passed
npm run type-check
# passed
npx eslint src/features/pickPlace/saveAutomaticParkGround.ts src/features/pickPlace/saveAutomaticParkGround.test.ts src/components/viewer/globe/AutomaticParkGround.tsx src/components/viewer/globe/AutomaticParkGround.test.tsx --max-warnings=0
# passed
```

No browser automation, paid generation, dependency installation or asset
modification was performed for this checkpoint. `node_modules` is an ignored
junction to the existing transformation worktree. Source changes are two
production files, their two test files, and this handoff. No push was performed.

## Browser verification for the next model

Test **this branch**, not the older running transformation worktree, which has
unrelated uncommitted changes. The new worktree is sparse and intentionally omits
heavy public assets. Set `CITYPROMPT_PUBLIC_DIR` to a verified hydrated asset
directory before starting its frontend. Verify the local backend, proxy and
asset paths first; use an available port and preserve any other running session.
The existing runtime notes are in `TRANSFORMATION_HANDOFF_2026-09-16.md`; their
September 16 process/port state must be checked again. Keep paid AI disabled.

Use a disposable project or duplicate, not the frozen Gold Standard project.
Select landscape terrain and place the reviewed adaptive neighbourhood park
(`neighborhood_park`, `neighborhood_park_v0`, `adaptive_rustic_v1`). Test while
automatic ground measurement is pending; an already valid saved terrain profile
does not exercise this race. Network throttling may help expose the timing.

1. On a flat site, let measurement finish normally. Verify one successful derived
   terrain write, visible ground contact, and stable geometry after reload.
2. On a slope, move/reshape the park before sampling finishes. Verify the saved
   terrain boundary matches the final outline, then inspect paths, furniture and
   perimeter from above and pedestrian height. Undo/redo and reload.
3. While sampling, save a park property edit without moving its outline (a name
   edit is sufficient to change the revision). Verify an old measurement does
   not save using the newer revision; only a fresh job may finish. The authored
   edit must survive, and derived terrain must add no extra undo step.
4. While sampling, change site ground settings, then let the restarted job
   finish. Inspect for jumps and retained authored settings. This is visual
   validation of pending sampling, not a claim that already saved profiles are
   invalidated by every site change.
5. Pause sampling through an authored edit, resume, and rapidly change the park
   archetype or delete it. Verify retired callbacks cannot recreate or overwrite
   the object. Navigate away and back as another cancellation check.
6. Interrupt context loading safely. Verify retries remain bounded and the
   student has a recovery path; restore the connection and retry. Check for
   repeated requests, uncaught errors and stuck progress.

Record source revision, API write order/revisions, saved coordinates/properties,
console/network results and screenshots; visually inspect every captured view.
Put evidence outside Git, for example under
`C:/dev-artifacts/CityPrompt/grounding-edit-race/`.

If deterministic timing cannot be reproduced in the live browser, report it as
not reproduced. The automated race tests are evidence for callback ordering,
not substitutes for visual grounding acceptance. Request no paid renders for
this verification. The separate US $10 mission API ceiling remains unchanged.

## Remaining scope

Building/entrance contact, prepared-site seams, the full mixed-object slope
matrix, asynchronous tile-refinement visuals, context-switch behavior and final
student acceptance remain open. This fix does not prove that Google photogrammetry
is bare-earth terrain. LiDAR and Gaussian-splat work remains deferred.
