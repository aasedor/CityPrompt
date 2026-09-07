# Twenty-building student trial — 7 September 2026

## Outcome

Created a fresh local Currie community through the student UI: **20 buildings and one 32 × 30 m neighbourhood park**, on land visibly vacant in the Google tiles. Buildings follow the surrounding street grid and avoid the visible roadways and existing buildings. Final building mix: 15 infill homes, three Craftsman bungalows and two Edwardian Foursquares. All 20 buildings were visible and had no reported grounding issues at the end.

This is a useful performance and usability fixture, **not a completed, connected master plan**. The attempted internal street did not fit the gaps left between plots. The remaining work is a circulation layout with adequate rights-of-way and connected entrances. Do not present the pictured arrangement as a finished neighbourhood or claim its access requirements are resolved.

- Project: `Student trial - Currie 20-building community`
- ID: `3c12dda6-3b15-4151-bf8b-eb59628a99ff`
- Local URL: `http://127.0.0.1:5178/projects/3c12dda6-3b15-4151-bf8b-eb59628a99ff`
- Tested source: main baseline `fcd3acce17491aec415f985f8a537867ec55a8e0`.
- Branch: `codex/twenty-building-student-trial`.
- Browser: automated Chromium, 1600 × 1000 viewport, Windows desktop, NVIDIA GeForce RTX 5060 through ANGLE/D3D11, local Vite development server.
- No paid renders or model generation. One free exact-3D export succeeded and was visually inspected.

## Performance evidence

Five-second requestAnimationFrame samples; these measure browser frame cadence, not GPU draw time. Camera position, tile detail and the mix of buildings changed during the trial, so these are practical observations rather than a controlled scalability benchmark. Do not infer tablet performance from this desktop GPU.

| Check | Median frame interval | 95th percentile | Frames over 50 ms |
| --- | ---: | ---: | ---: |
| 10 saved buildings | 17.5 ms | 18.1 ms | 0 |
| 20 saved buildings, before replacing the unresolved bungalow | 17.5 ms | 18.2 ms | 0 |
| Final 20 buildings plus park, immediately after deletion/settling | 17.6 ms | 18.1 ms | 2 |
| Orbit test, 20 buildings plus park, 5.69 seconds | 17.7 ms | 18.2 ms | 2 |

The orbit sample's longest frame was 52.8 ms; its PerformanceObserver recorded two 55 ms long tasks. Steady frame cadence was approximately 57 fps. There was no sustained rendering slowdown at this scale on this machine. Scene traversal counted roughly 849,000 triangles in the final overhead scene, including Google tiles; this is not a count of actually submitted draw calls or a standalone asset budget.

Reopening the project reached ready ground approximately **12.8 seconds after navigation**. All 20 building zones, the `green_space` park zone, and the imported reference overlay survived the reload. The project returned to its development view.

## Findings, in priority order

### 1. A local ground problem can hide the entire development

The first building saved successfully and the toolbar reported `3D saved`, but no building appeared. Shared ground had rejected the whole site for a discontinuity. The initial boundary measured a maximum local residual of about 0.981 m and maximum slope of 0.457. A clearer southern boundary still failed because one local residual was about 0.650 m, above the 0.600 m limit.

Closer viewing did not resolve this. After excluding the small problematic patch from the boundary, the measured surface passed (maximum residual about 0.531 m, maximum slope about 0.381). This required developer diagnostics and repeated boundary work; an ordinary student should not have to do that.

One large bungalow subsequently exceeded the 3 m foundation limit. Moving it did not resolve that issue. It was replaced with a smaller infill home, and the unresolved bungalow was removed. The final count is 20, with no grounding issues.

**Recommendation:** make ground failures spatially local and identify the affected object/patch directly. Preserve a clearly marked last-known or provisional visible representation during resampling without misrepresenting it as verified capture evidence. Keep the real ground/foundation checks; do not simply raise limits to make this fixture pass.

Relevant implementation: `SharedSiteGroundProvider.tsx`, `sharedSiteGround.ts`, `buildingGroundContact.ts` and the building layers under `frontend/src/components/viewer/globe/`.

### 2. Camera changes can temporarily remove all buildings

Panning, switching view and orbiting triggered shared-ground sampling and temporarily removed the proposed buildings. The camera itself remained responsive. This can feel like a slow or broken program even when frame rate is healthy.

**Recommendation:** separate editing visibility from verification readiness; retain visible geometry while relevant terrain updates are checked. Keep invalidation spatially scoped and avoid repeating unrelated measurements. Measure the duration of the disappearance explicitly in the next ground fix; the orbit frame sample alone does not measure that wait.

### 3. Circulation needs to be planned before filling the site

The student-facing street catalogue exposed one choice: a **16 m Calgary local street**. The trial left smaller gaps suitable for access lanes or paths, so the route was correctly rejected for overlapping building plots. A later extra point produced a switchback warning, and removing that point restored the overlap warning. No street was saved; zero authored road zones is intentional evidence of the failed attempt.

This is partly a layout mistake in the trial, not a performance bug. The app should make the required corridor width apparent before students fill their site. A narrow lane and pedestrian path should be selectable before drawing, rather than requiring a successfully placed full-width street before its properties can be changed.

**Recommendation:** reserve streets/paths first, show their full corridor during placement, then place frontage-oriented buildings. Pilot narrow access and pedestrian choices with the same collision and grounding checks. Repeat this fixture with a connected street/park network before calling the workflow classroom-ready.

### 4. Placement controls obscure the intended drop location

The bottom-centred placement panel intercepted a click intended to place a fifth home lower in the viewport; the click focused a dimension input instead. Panning was necessary to expose the site. This also complicates repeated placement in a dense scene.

`Place another` passes raw measured dimensions to the placement fields, producing values such as `15.999999…`. The reshape panel already rounds its own displayed values.

**Recommendation:** put placement controls in the side inspector or make them relocatable; display sensible precision without altering stored geometry. Relevant files: `frontend/src/features/pickPlace/PlacementControls.tsx` and `ReshapePanel.tsx`.

### 5. Rapid Undo needs a targeted regression trial

Two Undo operations during the early boundary/building workflow produced `Another session changed this drawing. Refresh the plan before trying again.` Only this browser was editing the new project. The exact interaction with automatic compilation/history revisions remains unconfirmed.

A later controlled test succeeded: change an infill plot from 12 m to 13 m, wait for `3D saved`, then Undo. The field returned to 12 m and the final scene remained healthy. This indicates that timing around asynchronous work deserves investigation; it does not establish that all Undo operations fail.

### 6. Existing-street context works, but is not complete sidewalk data

The optional `Load nearby Calgary streets & paths` action loaded a reference layer. It could be shown/hidden and survived reload. The overlay helped inspect the street grid; it did not turn lines into proposed buildings.

The park connection editor found no eligible adjacent sidewalk/path target for this site. It correctly did not reinterpret street centrelines as sidewalks. No park connection was saved. Mapped centreline and imagery alignment are contextual evidence, not a survey or proof of available right-of-way.

## Working checks

- UI login, new-project creation and address search.
- Catalogue placement, repeated placement and rotation.
- Plot-overlap and boundary containment rejection.
- Dragging a building; an excessive-foundation warning remained correctly unresolved.
- Resizing a placed home and Undo after saving.
- Compact park programme: the 32 × 30 m park omitted playground/pavilion elements instead of forcing them into the footprint.
- Optional reference-layer import, visibility and persistence.
- Project reload: 20 buildings plus one park retained.
- Final exact-3D export: successful, no AI transformation, visually inspected.
- Browser page-error command returned no uncaught page errors. Transient UI validation messages and the Undo conflict are recorded separately above.

## Evidence and next bounded trial

Screenshots, the final exact capture, zone inventory and timing JSON are outside Git at:

`C:/dev-artifacts/CityPrompt/twenty-building-trial-2026-09-07/`

Use `performance-10-confirmed.json`, `performance-20.json`, `performance-20-final.json` and `performance-orbit.json` for the table. The earlier `performance-10.json` was captured after a rejected placement and is exploratory, not the confirmed ten-building sample. `reopen.json` uses an incorrect `park` type filter and therefore reports zero parks; the authoritative inventory contains one `green_space` zone, confirmed visually after reopening. Its text-based reference visibility flag is also not an overlay persistence assertion.

Key images: `first-home-settled.png` (invisible first home), `five-homes.png` (placement panel/dimension issue), `transport-overlay-settled.png` (context comparison), `reopened.png`, and `community-final-capture.png` (successful final export).

Next priority is a bounded **ground visibility and circulation** pilot on this saved project: fix local failure presentation/resampling visibility, reproduce rapid Undo, and lay out a connected corridor before filling frontage plots. Retest at 20 buildings on this desktop and on actual tablet hardware. There is no evidence here that reducing catalogue detail or a broad renderer rewrite is the first necessary change.

No application source or assets were changed in this trial. Local project/database state and external evidence are separate from this report. Nothing was pushed or published.
