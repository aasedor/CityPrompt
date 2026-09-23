# Building entrance grounding — source implementation and browser pilot

The browser pilot is complete. Read `CURRIE_ENTRANCE_BROWSER_QA_2026-09-19.md`
for measured results, the Undo identity defect found and fixed during testing,
and the remaining student-ready work. The procedure below is retained as the
scope of that bounded test, not as an unperformed task list.

Continue in `C:/dev/CityPrompt-grounding-edit-race`, branch
`codex/grounding-edit-race-hardening`. This source work began on top of
`64038424e`. No push or paid generation occurred. This is a continuation of
the vacant Currie grounding initiative.

## Status and intended behavior

The prior browser continuation found that `Shared street west 2` had native
entrance steps resting on its generated foundation cap, with another roughly
two-metre drop to the surrounding measured terrain. A ready foundation did
not establish a usable entrance. See
`CURRIE_GROUNDING_CONTINUATION_2026-09-19.md` for the actual visual evidence.

The runtime now supports a concept stair approach from a selected street to
an explicitly authored entrance at the native foundation edge:

- Connections retains its existing plot-relative horizontal anchor and adds
  `heightAboveBaseM`, defaulting to zero for legacy saved entrances. This height
  is never scaled with plot resizing. The user must place and visually review
  the anchor at the actual outer foot of the model's steps.
- The owning model supplies its measured native footprints and actual base
  height. Each tread uses the existing full-polygon support solver against
  the shared terrain. No model scaling, catalogue changes, or terrain
  flattening are involved.
- The existing route planner checks site coverage and obstacles. The new
  geometry check also rejects routes through the owning building's pads,
  anchors away from the pad edge, missing ground, inadequate run, or terrain
  protruding through a tread. An unresolved approach is omitted and reported.
- A supported foundation with more than 0.30 m of relief now reports
  `entrance_connection_required` when no valid entrance is authored. The
  model remains visible. Its issue participates in the existing capture
  blocking path, with an actionable Connections message.
- Measured-ground building paths use this approach instead of the old
  terrain-draped strip. Prepared-site paths and street crossings keep their
  existing behavior. Approach capture tags belong to the destination street,
  while the native building retains its building identity.

The 0.30 m review threshold and the bounded stair geometry (maximum 0.18 m
rise, minimum 0.28 m going for multiple treads, maximum 3 m total rise) are
concept-display limits. They do not certify accessibility, edge protection,
construction suitability, or every entrance on a multi-building plot.
No automatic doorway inference or reviewed catalogue entrance metadata was
introduced. A manual coordinate editor still needs usability review before
it can be treated as a finished student workflow.

## Source and automated verification

New modules:

- `frontend/src/components/viewer/globe/buildingEntranceApproach.ts`: pure
  terrain-supported approach geometry, including descending routes.
- `frontend/src/components/viewer/globe/BuildingEntranceApproaches.tsx`:
  shared authoring inputs, model-owned geometry, capture ownership and
  deferred resource disposal.

Integration touches the imported/generated and LEGO model layers,
`GlobeSitePlannerMap`, `GlobePedestrianConnections`, grounding messages, and
the existing Connections editor/parser. The hook derives geometry from the
current model and terrain inputs; it adds no asynchronous registry or saved
generated mesh. Existing retained-safe-ground behavior remains in charge.

The bounded regression run passed **91 tests across 11 files**:

```powershell
cd C:/dev/CityPrompt-grounding-edit-race/frontend
npx vitest run src/components/viewer/globe/BuildingEntranceApproaches.test.tsx src/components/viewer/globe/buildingEntranceApproach.test.ts src/components/viewer/globe/GlobeBuildingModelsLayer.test.tsx src/components/viewer/globe/buildingGroundContact.test.ts src/components/viewer/globe/importedBuildingGround.test.ts src/components/viewer/globe/strictModeResourceDisposal.test.ts src/components/viewer/globe/pedestrianCapture.test.ts src/components/viewer/globe/sharedGroundCapture.test.ts src/components/viewer/globe/SharedSiteGroundProvider.test.tsx src/features/pickPlace/pedestrianConnections.test.ts src/features/pickPlace/ConnectionEditor.test.tsx
```

Coverage includes elevated and descending approaches, a 95-degree rotation,
explicit entrance height, a narrow concave coverage failure, an obstructing
detached pad, insufficient run, unavailable elevations, target deletion,
legacy entrance parsing, and a model-layer callback test that keeps the model
visible while reporting its unresolved entrance. **Changed-file ESLint,
`npm run type-check`, and `git diff --check` passed.** A final four-test hook
rerun also passed after completing its typed fixture data. The initial
type-check caught that incomplete test fixture; it was corrected before the
successful final check.

Automated tests are not visual acceptance. The separate browser report records
the one-house visual pilot and its limits. The user switched models and
authorized the browser checks; do not spawn agents.

## Bounded browser pilot procedure (performed)

1. Reuse healthy frontend `127.0.0.1:5174` and backend `127.0.0.1:8000` from
   this worktree. Read the recent memory and prior continuation for startup,
   authentication and evidence paths. Do not start duplicate processes.
2. Use the **vacant Currie** fixture
   `f5bffc94-def9-4c43-942e-9ae7411872e9`. Its unchanged eight-vertex boundary,
   seven houses, park and six-metre street are the reference. The target is
   `Shared street west 2`, zone
   `9ee6effb-7821-4e63-b702-3e556e6e72a9`, building
   `d9064815-e224-4721-9a06-eb66ee5ccce1`, saved at 95 degrees.
3. First confirm the new entrance issue appears while the grounded building
   stays visible, and a capture attempt gives the Connections message. More
   than one house may now require an entrance; this is expected. Do not remove
   warnings or flatten the site to make the capture succeed.
4. For the one-house positive pilot, use a disposable copy of this same vacant
   parcel with the target bungalow and its matching street retained. Preserve
   the main fixture and exact boundary. The older disposable copy
   `bfcc05d2-b5b8-4447-8fe3-79f0f6e60a3d` has one house moved 22 m north and no
   matching street, so it is not already a positive entrance fixture.
5. In Connections, select that street and author the anchor against the actual
   foot of the bungalow steps. Keep plot scaling off for the unscaled native
   house. Use zero height only if the actual step foot reaches the model base.
   Do not guess an anchor merely to clear the warning. If the true step foot
   does not meet the native bounding-pad edge, record the mismatch as a
   blocker; the conservative edge restriction may need another source pass.
6. Inspect pedestrian views from both sides and a close view of both joins:
   native step to approach and approach to sidewalk. Check for gaps, buried
   treads, terrain intrusions, visual side-wall problems, and unreasonable
   stair layout. Read the actual images. A successful capture alone is not
   acceptance, and these stairs do not claim an accessible route.
7. On that disposable pilot, rotate slightly, Undo, Redo and reload; check the
   anchor, approach and model stay aligned. Delete/hide the target street and
   restore it; verify stale approach geometry disappears and issues recover.
   Perform one bounded terrain-refinement/capture check. Capture should wait
   or reject while unresolved, then succeed only with current support.
8. Verify a direct 3D capture retains the building ID and gives the approach
   its target street identity. Do not call paid image/video generation.
9. Save evidence outside Git under
   `C:/dev-artifacts/CityPrompt/grounding-batch-a/`. Reuse the frozen-camera
   file and `currie-final-same-camera.png` for the main-fixture comparison.
   The read-only source snapshot from this implementation is
   `currie-entrance-source-project.json` in that directory.
10. Record pass/fail before expanding to the other six houses. If the pilot
    passes, complete a coherent source checkpoint after the repository's
    required local verification. `CLAUDE.md` requires localhost verification
    before committing; the current changes deliberately remain uncommitted
    pending that model-switched browser pass.

After this entrance gate is accepted, follow
`STUDENT_TRANSFORMATION_GATES.md`: complete the remaining edit/recovery
checks, exercise the novice save/reopen/present journey, then run a small
student pilot. This change alone does not make Batch A or the product accepted.
