# Fresh Currie student workflow pilot — 20 September 2026

## Scope and fixture

Worktree `C:/dev/CityPrompt-grounding-edit-race`, branch
`codex/grounding-edit-race-hardening`. The user prioritized a usable concept model
and strong visuals over perfection. This pilot tests ordinary student controls,
with actual failures retained rather than beginning another fine-detail review.

New project: `0320bb4f-395c-41c6-a6c0-ad28bb1572ef`, named
**Currie student workflow pilot — 20 September**. It was created through Projects,
New Project, Currie address search and Create Project. Its site outline was drawn
with pointer input on the visibly vacant Currie parcel and finished with Enter.
The boundary, street, house, park and entrance were authored through the UI;
no saved fixture geometry or entrance offsets were inserted through the API.
Read-only API snapshots and scene diagnostics were used for verification/debugging.

Protected Currie `f5bffc94-def9-4c43-942e-9ae7411872e9` has an identical final
full zone response. The earlier seven-house copy was not edited. New project IDs:

| Object | ID |
| --- | --- |
| Site boundary | `171f4dfb-ad7a-4e2d-9551-ac724375963d` |
| Yield/shared street, Dutch Woonerf, 6 m | `dfa3ecda-e8d4-4ee2-911b-070f9533d560` |
| Calgary Modern Infill House, Flat Roof Minimal plot | `9b901a75-d618-41fd-b234-bba82ae79cc5` |
| Native building | `21d1f5a6-d458-4830-8f7b-1273ac218496` |
| Neighbourhood park, Rustic Timber & Gravel | `e1694458-ed97-413f-9dd0-5f15236a9fcd` |

## What happened in the ordinary workflow

1. Searched Currie, created the project, used Top View and ordinary pan, then
   drew a six-corner boundary on vacant ground. Confirm site opened Design.
2. Chose the six-metre shared street and drew a two-point route. Selected the
   infill card and clicked to place a 12×16 m plot; street-facing rotation was
   automatic. Selected the neighbourhood park and clicked a 40×35 m plot.
3. Natural-ground measurement rejected the site's rough surface. The save state
   still said 3D saved, but the house was not visible while its ground was
   unavailable. Initial hand-drawn site was about 1.9 ha. The first inward
   boundary edit reduced it to about 1 ha but did not clear the problem.
4. Ground review's original red markers used an unrelated 2 m adjacent-height
   threshold. The validator uses triangle slope and local residual. A rejection
   could therefore appear without a corresponding red marker. This defect was
   fixed in this unit; the live review then highlighted the relevant north
   patches and offered a direct Adjust site boundary action.
5. Trying to crop across the street was rejected and preserved the saved layout.
   The message named an object UUID instead of a useful street label. Reload
   saved version recovered; shortening the street through its white endpoint
   allowed further boundary edits. More bounded edits still left a small local
   failure. No threshold was relaxed and no measured height was replaced.
6. The remaining authoring flow was tested with the explicit Prepare a level
   redevelopment surface action, at the UI's proposed 1102.620745713007 m datum,
   with measured retaining edges enabled. This is an intentional alternative
   concept-grade trial, not a natural-ground pass. The house/street/park became
   visible, and the park's automatic path met the street.
7. Connections initially had its link checkbox off. Enabling it exposed the
   target and 3D picker. Focus, scroll and right-drag brought the native steps
   into view. Two actual low-step clicks produced occlusion messages. Source
   inspection also establishes that the picker requires ready measured ground
   and contact, while this prepared mode supplies inactive shared ground; waiting
   cannot make that contract succeed. Exact occluder identity was not established.
8. Cancel pick retained the dialog. A pointer click in the plot guide, without
   supplied offsets, selected an approximate entrance and Save persisted it:
   x 2.64 m, y -5.76 m, width 1.8 m, unscaled, height 0. A path is visible in plan.
   This is authoring proof, not exact native-step alignment acceptance.
9. Dragging the native house body panned the camera in this trial. The visible
   Move handle worked: a subsequent move changed the saved footprint, Undo
   restored original coordinates, Redo restored the move and reload retained it.
   All actions used normal controls. The final new project retains that move.
10. Render this view → Image → Export current 3D view · free produced a download.
    The exported image was inspected: one house, street, park and connecting paths
    are present on the explicitly prepared site. This is a sparse concept scene;
    it is not a professional AI-image-quality acceptance. No paid AI was invoked.

## Source change and validation

`validateSharedSiteGroundPass` optionally reports sample indices involved in its
existing slope/residual rejection. Validation behavior, thresholds and measured
heights are unchanged. `describeGround` now uses those exact diagnostics instead
of duplicating a 2 m rule. `GroundReviewPanel` offers boundary editing on unavailable
natural ground, explains that placed objects must remain inside, and does not
apply a prepared level as part of that action. The map selects the actual active
boundary and closes the review.

54 tests pass in six relevant suites: `groundReview`, `GroundReviewPanel`,
`sharedSiteGround`, `sharedGroundCapture`, `preparedSiteEdges` and
`buildingGroundContact`. The review regression covers rejected bumps and a steady
steep slope below the old per-neighbour 2 m threshold, then a valid flat surface.
The action test verifies no ground-setting mutation. Type-check and changed-file
ESLint pass. No new fetches, new geometry or changed grounding limits were added.

Browser evidence verifies the corrected red regions and direct boundary selection.
Natural-ground recovery remains FAIL; changing to prepared mode does not erase it.
Move/Undo/Redo/reload and exact export observed zero page errors. Boundary rejection
409s were actual expected validation responses; their UUID wording remains open.
Some automation attempts timed out because DOM accessible labels differed in case
from the browser's displayed uppercase labels, and the initial create-response
predicate did not match the request. The project was already created; it was not
created again. These harness retries are separate from product defects.

## Concrete release findings

- **Blocker:** local natural-ground problems disable the whole scene. Last saved
  failure had max slope 0.4339875387 and max local residual 0.6232191151 m. Two
  diagnostic cells were highlighted. These are observed values, not a proposed
  new threshold. Review natural-scene availability and recovery, not just limits.
- **Blocker for advertised picking:** prepared-site native step picking lacks a
  compatible ground/contact contract. The user can use the approximate plot guide,
  but this does not prove an accurate native-step join.
- **Usability:** raw model drag pans while Move-handle drag works; align instructions
  or gestures. Boundary rejection messages need useful object names.
- **Presentation:** free export works. Attractive, faithful AI output still needs
  a real bounded test; this runtime harness disables paid AI providers.
- **Separate existing issue:** legacy Generate to 3D locked-recipe mismatch remains
  open and was not re-tested or bypassed in this unit.

Fine railing joins, tiny seams and comprehensive code/accessibility checks are
follow-up work under the user's clarified concept-design target. They must not
crowd out the concrete blockers above. Shared integration guidance/template and
`CLASSROOM_READINESS_PLAN_2026-09-20.md` now capture this priority.

## Evidence and final state

External root `C:/dev-artifacts/CityPrompt/grounding-batch-a/`, `student-*`:
`student-project.json` holds the new project and protected-original baseline;
`student-ground-failure.json`, `student-ground-after-shrink.json`,
`student-residual-blocker.json` preserve natural-ground failures;
`student-ground-recovery-action.png` and `student-boundary-direct-edit.png`
show the fix; `student-pick-front.png` and `student-pick-result2.png` show the
prepared-site picking attempt; `student-edit-recovery.json` verifies persisted
coordinates and original preservation; `student-free-export.png` and
`student-export-result.json` hold the final capture. The local hash manifest is
`student-evidence-sha256.json`; it is not a shared backup.

| Evidence | SHA-256 |
| --- | --- |
| `student-residual-blocker.json` | `fe6f0e6084ddfc313d5a7da521812bc2b72a757f3c0c8c6551fb72ac155aa374` |
| `student-edit-recovery.json` | `aece7c397082852b4f2f7eb55b8bc23e87a5931d5eceb9e9a99ee2218fc9763e` |
| `student-free-export.png` | `5b352ced5ebc8f8c6bcbf33a27d30a0f62b75fe7661c4af2fea49dd61f8bd33e` |

No assets, catalogue activation, RLASM method companions or production state
changed. Do not publish the new project as a seed or call the entire student
workflow passed. The current new fixture is intentionally prepared; use the
saved natural-ground failure snapshots to reproduce the next grounding work.
