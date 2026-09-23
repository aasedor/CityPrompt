# Currie 3D entrance-picking pilot — 20 September 2026

The Connections dialog now lets a student pick the lowest entrance step on a
native catalogue house in 3D. It keeps unsaved settings while the student
navigates, checks the chosen point against current measured ground and the
selected sidewalk, and returns a draft to the dialog. Save remains explicit.
An unresolved approach retains the picked anchor and gives recovery guidance.
This pilot does not identify doors automatically or establish accessibility.

## Source behavior

- Capture the model surface at pointer-down, then accept only a click within
  the existing six-pixel drag threshold. Globe controls can adjust the camera
  on release; collecting the model hit only on click missed small steps.
- Transform the low model hit into plot coordinates and snap it to the nearby
  measured foundation edge. Reject high surfaces, distant edges, pending or
  stale ground, and hits on a different house.
- Check foreground scene geometry as well as interactive meshes. Respect
  transparent texture pixels: street-tree billboard margins initially caused
  false occlusion. Opaque foreground geometry still blocks the pick.
- Preserve the target sidewalk and unsaved width. Escape or Cancel pick
  restores the draft; changing the plot invalidates stale dialog saving.
- Pause normal plot selection/edit controls while picking. Camera navigation
  remains available. Exact offsets and the keyboard plot guide remain usable.

## Live browser evidence

Used existing local services at ports 5174 and 8000 and the disposable
seven-house Currie project `54bb844c-1ff4-4d67-bc7f-0c8c36d0030e`.
The pilot house was Shared street east 1, zone
`522b87a9-26eb-4da6-806e-6ab53e9cdc3e`, a modern infill rotated -90 degrees.
Camera helpers framed the scene; actual browser pointer events selected the
step. No application selection callback was invoked by the test scripts.

| Check | Result |
| --- | --- |
| Pick mode hides dialog, retains draft, shows instructions | PASS |
| High window click is rejected with lowest-step guidance | PASS |
| Transparent tree margin does not falsely block visible step | PASS after fix |
| Click during renewed terrain sampling asks the student to wait | PASS |
| Drag from step does not accept it | PASS |
| Escape restores unsaved 2.05 m width | PASS |
| No network writes from drag, cancellation, or draft selection | PASS |
| Picked point (3.05, -5.875) returns with current-ground fit feedback | PASS |
| Save returns HTTP 200; reload restores picked offsets and 2.05 m width | PASS |
| Reload reaches current ready ground with zero building-ground issues | PASS |
| Restore original (2.88, -5.875), width 2.12 m through editor | PASS; HTTP 200 and ground ready without issues |
| Other families, touch devices, full novice journey | NOT TESTED in this slice |
| Actual short-setback recovery through browser | NOT TESTED; helper test covers guidance |

Visually inspected the accepted-pick dialog and restored house screenshots.
The page-error query returned no error entries. The protected original project
`f5bffc94-def9-4c43-942e-9ae7411872e9` was not edited; a read-only API comparison
confirmed all ten zone coordinate arrays still match the saved snapshot.

Focused Vitest passed **46 tests across four files**: `ConnectionEditor`,
`pickBuildingEntrance`, `pedestrianConnections`, and
`buildingEntranceApproach`. Frontend TypeScript and changed-file ESLint passed.
Tests include rotated plots, missing streets, insufficient setback, stale
ground, stale dialog edits, and visible versus transparent occlusion.

Evidence stays outside Git under
`C:/dev-artifacts/CityPrompt/grounding-batch-a/`, including
`currie-3d-pick-result.png`, `currie-3d-pick-restored.png`,
`currie-3d-pick-saved.json`, `finish_entrance_pick.cjs`, and
`verify_entrance_reload.cjs`. The first save script's reload wait used an
incomplete optional-chain guard and stopped after a successful save; the
separate reload script verified persistence and restored the baseline.
No paid generation, catalogue asset changes, or push occurred.

## Next bounded work

1. Browser-pilot this authoring flow on the Currie Craftsman and Edwardian;
   reproduce insufficient setback and guide the student through moving the
   plot, repicking, saving, Undo, and reload. Keep trials in disposable copies.
2. Review high exposed foundations and long stairs as a separate design unit:
   landings, guards, accessible alternatives, and street furniture clearance
   remain unresolved. Zero solver warnings are not visual acceptance.
3. Run a complete novice journey from vacant parcel through placement,
   connections, editing, ground review, save/reopen, and free exact 3D capture.
   Then continue the rapid-edit/failure-recovery matrix in
   `docs/NEXT_EDIT_PLAN_2026-09-19.md` and the student transformation gates.

Batch A and the whole product remain unaccepted. This checkpoint completes a
bounded authoring improvement and one live model pilot, not student readiness.
