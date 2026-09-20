# Currie entrance side details and recovery — 20 September 2026

## Result

Shared approach geometry now includes concept side rails and landing posts
meeting measured terrain. Both high Craftsmen and the low Edwardian were
inspected in the live disposable Currie layout, including low side views.
Insufficient clear width gives an actionable failure and blocks export.
Save/Undo/Redo/reload passed after fixing an entrance-only rebuild trigger.
This is bounded runtime/visual evidence, not complete architectural acceptance.

Worktree `C:/dev/CityPrompt-grounding-edit-race`, branch
`codex/grounding-edit-race-hardening`, based on `be52a0695`. Browser Chromium,
1440 × 900, real localhost frontend/backend and measured terrain. No native
asset edits, paid generation, catalogue activation or push.

Protected original: `f5bffc94-def9-4c43-942e-9ae7411872e9`.
Disposable copy: `54bb844c-1ff4-4d67-bc7f-0c8c36d0030e`.

## Shared concept geometry

`buildingApproachDetails.ts` consumes the validated route sections. A section
with more than 0.3 m measured drop, or a flight with more than 0.3 m rise/fall,
receives side rails. Their top follows the flight or level landing, with posts
and vertical pickets. The concept rail top is 1.05 m above the section's linear
profile; this does not certify a handrail, guard or local construction standard.

Rails remain inside the existing route envelope and leave both ends open.
Each side reserves 0.08 m; the current concept minimum clear width is 1.2 m,
so a guarded route requires at least 1.36 m total width. A narrower route stays
unresolved as `entrance_clear_width_too_small`. Connections explains this before
save and ground/capture errors give the same repair guidance.

Landing/walk support posts use small complete footprints in the same measured
triangle field as the approach. Their feet follow measured corner heights and
their tops meet the shallow slab underside. Posts are omitted where terrain
already meets the slab. Display posts do not establish bearing, foundations,
bracing or structural adequacy. No geometry cuts or flattens the terrain.

The approach, rails and posts retain street capture ownership and the original
house owner. All three geometries retire together if the route becomes invalid;
their resources use the existing deferred disposal mechanism. The native house
and its authored steps remain separate.

## Browser observations

| House | Total width | Reserved clear width | Landing posts | Reviewed views |
| --- | ---: | ---: | ---: | --- |
| West 2 Craftsman | 1.80 m | 1.64 m | 4 | Oblique |
| West 3 Craftsman | 1.80 m | 1.64 m | 4 | Oblique, low opposite side, exact export |
| West 4 Edwardian | 1.65 m | 1.49 m | 4 | Oblique, low opposite side |

The landing remains level, rails follow the distinct flight, and both entry
and exit remain open. Posts meet the visible terrain under the landing. The
long Craftsman climb and exposed foundation cap/edges remain prominent. Native
stairs above the landing have their own unresolved rail/guard transitions.
The Edwardian's compact flight remains distinct from the level street approach.
Tree foliage obscured some oblique views; the low opposite-side views exposed
the joins. No systematic furniture-envelope acceptance was performed.

From the oblique Craftsman view, a new rail occluded the selected native step.
The picker correctly asked for a clear view. Moving the camera to the front
allowed the actual low-step pick and ready feedback. The rail was not ignored
to make picking pass. Cancel/draft behavior and saved anchors were preserved.

Through Connections, west 3 was temporarily set to 1.2 m total width. The
ground warning appeared and free export failed with the same clear-width
guidance. Undo restored 1.8 m; Redo restored the failure; a final Undo and reload
restored all seven ready approaches. The final free exact 3D export was downloaded
and inspected. No AI image was used.

## Reproduced entrance-edit rebuild defect

The first rapid width edit cycle exposed a stale representation after Undo:
one house disappeared from the scene while the sidebar said “3D saved”, and
export remained disabled. The saved footprint, entrance, model ID and recipe
were intact. Entrance properties were included in `useAutomatic3D`'s rebuild
trigger even though they are runtime geometry and are absent from the backend
building source hash. Rebuilding advanced model compilation metadata; restoring
older zone properties could strand its otherwise identical representation.

The focused regression first failed with two unnecessary compiler calls. The
rebuild trigger now excludes only `pedestrian_building_entrance`. The full
authored-state comparison still includes it when checking derived revisions.
Actual footprint changes continue to rebuild. This is a narrow fix for entrance
edits; it does not certify every historical metadata-restoration path.
The isolated recovery fix is committed as `0c6a6a017`.

During recovery, changing the trigger refreshed the copy's compiled timestamps.
The legacy Generate to 3D panel was also tried and reported that its prepared
modules differed from the locked recipe. Its strict rejection was preserved;
that separate legacy-panel failure is open. After refresh, the normal student
scene had seven ready approaches again. The full width Save/Undo/Redo/Undo/reload
trial was repeated with request observation: **zero model plan/place requests**,
unchanged compiled markers, and successful final export.

## State, checks and evidence

All copy coordinates and saved entrance anchors match the start-of-turn
snapshot, including west 3's previously accepted 1.165 m extra setback. Building
IDs are retained. Derived compilation timestamps were refreshed during recovery;
do not describe the entire copy JSON as unchanged. The protected original's
full zone response still matches the preceding checkpoint exactly.

95 tests passed across nine focused files: `buildingEntranceApproach`,
`BuildingEntranceApproaches`, `BuildingGroundProblems`, `buildingGroundContact`,
`pedestrianCapture`, `pickBuildingEntrance`, `ConnectionEditor`,
`pedestrianConnections`, and `useAutomatic3D`. The support-foot test was then
strengthened with cross-slope measurements; all 20 approach tests passed again.
Type-check and changed-file lint pass. React review found geometry derived in
the existing memo, bounded detail loops, no new fetching/subscriptions and
cleanup for all three geometry resources. Capture/picking remain on shared paths.

External evidence root: `C:/dev-artifacts/CityPrompt/grounding-batch-a/`:

- `edges-baseline-zones.json`, `edges-refreshed-zones.json`: original and
  recovered compilation snapshots.
- `edges-browser-review.json`: section/detail metadata and low-view checks;
  page-error collection empty during that review.
- `edges-Shared-street-west-2.png`, `edges-Shared-street-west-3.png`,
  `edges-Shared-street-west-4.png`, `edges-low-Shared-street-west-3.png`,
  `edges-low-Shared-street-west-4.png`: inspected views.
- `edges-width-capture-blocked.png`, `edges-recovery.json`: final width failure,
  ordinary-control recovery and fixture preservation.
- `edges-pre-fix-recovery.json`, `edges-compile-readback.json`,
  `edges-model-markers.json`: first-cycle diagnostic evidence.
- `edges-rebuild-regression.json`: no plan/place requests and unchanged markers
  across the second complete width cycle.
- `edges-legacy-rebuild-blocked.png`: separate legacy-panel rejection.
- `edges-free-export.png`, `edges-export-panel.png`, `edges-export-state.json`:
  final exact capture and mesh ownership. Hash manifest: `edges-evidence-sha256.json`.

Key SHA-256 records (local evidence, not a shared backup):

| File | SHA-256 |
| --- | --- |
| `edges-recovery.json` | `a2d9e29f2f681f3d3c6e19cf752805df14e502e6d251472feda590e6cc6af437` |
| `edges-rebuild-regression.json` | `4660ca2701b82768f35afcc8c26554995e2621299feb0d17560106245411324c` |
| `edges-free-export.png` | `30bc831d00563706b239e3858c63cdea30acd685801a4968b48826a47f8d5bf6` |

Some initial camera/capture harness checks ran before new ground/model updates
settled. Recovery checks then waited for the actual seven approach meshes and
the ordinary 3D saved state. Do not confuse the first true compilation defect
with these harness timing retries. Evidence remains local-only.

## Next bounded work

Keep Astra for the foundation-edge and native-step transition review. Decide
which exposed cap edges are actual pedestrian surfaces, identify supported
guard/handrail joins without editing unrelated model geometry, and review
furniture clearance. Then define the student-facing response when the site
cannot offer a supported accessible route. Do not label all seven houses
student-ready from a clear ground issue list or add rails to every native mesh
without variant-specific evidence.

Complete a novice-authored placement-to-presentation pilot after those decisions.
Keep the legacy Generate to 3D mismatch open for a separate reproducer/fix.
Shared integration guidance and the template now carry the envelope, width,
support, occlusion and entrance-only rebuild lessons into future archetypes.
RLASM 6.1 and its executable method companions are unchanged.
