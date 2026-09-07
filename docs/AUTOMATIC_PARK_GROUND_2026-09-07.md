# Automatic park ground alignment

Priority: students should move and reshape parks without repeatedly opening Review ground.

Branch: `codex/automatic-park-ground`, based on `2cd4184f4`.
Local checkout: `C:/dev/CityPrompt-building-next3`.
Pilot: http://127.0.0.1:5178/projects/f289f565-1a52-43ec-accc-38cb5ac24ea2
No push, no catalogue changes, no changes to the original OneDrive checkout.

## Student experience

- Terrain-following neighbourhood parks remeasure automatically after movement,
  resizing and rotation. Newly placed neighbourhood parks also align when the
  site is already in landscape mode. Existing prepared sites are not silently
  switched to landscape mode; the initial choice remains explicit.
- The park stays visible as a temporary draft. All its ground layers use the
  same draft triangles, avoiding lawn/path intersections while measurement runs.
- Sampling starts after edits and automatic 3D rebuilding settle. A small status
  message explains alignment; no modal, successful-save toast or extra Undo step.
- Each park measures separately from original Google tiles. One park runs at a
  time with debouncing, three bounded attempts, and a one-minute attempt deadline.
  A newer footprint cancels an older result. Online recovery retries the queue.
- If tiles or saving remain unavailable, the design stays editable as a draft
  with a retry control. Final capture waits for verified measurements rather than
  treating approximate draft heights as measured terrain.
- Successful profiles persist and remain valid after reopening. Background writes
  merge current properties, use the existing server version guard, and advance
  the local Undo revision. Conflicts refresh quietly without overwriting edits.

## Measurement corrections found in this trial

The original 2.5 m grid rejected a curved hillside shoulder after a 30-to-32 m
resize (local residual 0.616 m against a 0.6 m limit). Park sampling now targets
1.25 m, retaining the existing 1,200-sample bound and coarsening large footprints.
The finer measured grid reduced residual to 0.319 m; thresholds were not relaxed
for this correction. Grid spacing is part of measurement source identity.

A subsequent move of roughly half a metre crossed a steep edge with measured
gradient 1.11 m/m and residual 0.283 m. The earlier whole-park 1.0 m/m slope cap
incorrectly rejected this repeatable landscape. Landscape acceptance now retains
finite measured slopes while still requiring plausible finite heights, complete
coverage, two raw passes within 0.08 m and local residual at most 0.6 m. Shared
site-ground walkability-related limits are unchanged. Landscape acceptance is not
an accessibility finding; path grades and landings still need separate review.

## Verification

Live UI sequence on the Salisbury Avenue hillside:

1. Resized the existing 30 x 30 m park to 32 x 30 m. New automatic profile
   `reviewed-park-7249463c`: 675 samples, pass difference 0 m.
2. Dragged it approximately 0.42 m east and 0.38 m north. Profile
   `reviewed-park-fc1968e4` persisted at the new coordinates without Review ground.
3. Resized to 34 x 30 m. The draft remained coherent while aligning. Profile
   `reviewed-park-4eac9e82`: 725 samples, pass difference 0 m, residual 0.336 m.
4. One Undo restored 32 m; automatic alignment restored the corresponding profile.
   One Redo restored 34 m and its correct profile. No background Undo step appeared.
5. Reopened the project. The 34 m profile and row revision persisted with no new
   alignment request on the unchanged footprint.
6. Exported the current 3D view through the render panel. Loaded 1600 x 936 exact
   capture inspected visually. No paid image or video generation; balance 9,445.

55 tests pass in 11 affected suites: stale/deleted jobs, bounded failure and
never-finishing provider, coherent drafts, geometry, persistence conflicts,
Undo revisions, saved profile validation and existing terrace/review behavior.
TypeScript and targeted lint checks passed for this checkpoint.

QA images are outside Git in `C:/dev-artifacts/CityPrompt/student-beta-2026-09-06/`:
`auto-park-coherent-draft.png`, `auto-park-new-ground.png`, `auto-park-exact3d.png`.
Earlier images with loading tiles or failed draft triangulation are diagnostic
artifacts, not final acceptance evidence.

## Remaining scope

This is the neighbourhood-park pilot, not automatic conversion of all park families.
The compact layout has no playground/pavilion pads; a larger amenity-rich sloped
park remains the next bounded visual trial. Graded links to streets, edge blending,
and differences between saved ground and later Google tile detail remain open.
Original Google meshes may contain trees, roofs or photogrammetry artifacts;
measuring them does not establish surveyed bare earth or remove obstructions.
