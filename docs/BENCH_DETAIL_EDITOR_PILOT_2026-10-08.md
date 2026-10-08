# Bench detail editor pilot — 8 October 2026

## Scope and use

This is a bounded bench-editing pilot for the existing detailed rustic neighbourhood park (`adaptive_rustic_v1`). It reuses the park's real 1.9 m timber bench GLB and terrain placement. No replacement models or generated images were introduced.

Open the local **Bench detail editor · pilot** project:

http://127.0.0.1:5183/projects/099fdc75-8eb1-4849-b602-8eebecef296e

Select the park, choose **Edit details · benches**, then add, drag, nudge, rotate or remove a bench in the top-view editor. **Save details** updates the 3D scene. Closing discards unsaved changes. Undo inside the editor applies to bench edits; saved edits use the existing project history.

The rustic park is a saved-project-compatible legacy asset, not a current default catalogue choice. The trial project and prepared site boundary were created in the browser. Its one 70 × 55 m rustic park fixture was created through the normal backend `create_zone` function with the project owner and validation, because it cannot currently be selected from the catalogue. No legacy catalogue entries were reintroduced. This verifies detail editing, not catalogue discovery.

## Interaction and persistence

- Individual benches are selectable only in the modal editor. A bench click in the normal 3D view selects the whole park.
- The underlying app is inert while editing; map interactions and project undo shortcuts are paused. Keyboard deletion and undo remain local to the draft.
- Versioned `bench_details` JSON in existing zone properties stores stable IDs and positions/orientation relative to the park. An empty list means remove all benches, rather than restore automatic benches.
- Whole-park translation and rotation carry saved benches with them. Metric bench dimensions stay fixed.
- The editor prevents overlap with other benches, park modules and walking paths, and keeps benches inside the park.
- Automatic trees and flowers leave 1.5 m clearance around edited benches. This avoids regenerating planting through saved furniture when moving a park. Unedited parks retain their original planting.
- Save errors retain the open draft for retry. The existing owned-zone update, optimistic update, concurrency and history infrastructure is reused; no new backend endpoint or migration is required.

## Verification

Browser trial at port 5183, using the existing signed-in local QA account:

1. Opened three automatic benches; added a fourth.
2. Nudged, rotated and dragged the new bench; removed one automatic bench and saved three benches.
3. Reloaded and confirmed the edited arrangement persisted.
4. Deleted a bench with the keyboard and restored it with local undo; single Escape returned focus to the park controls.
5. Rotated the whole park 15 degrees, moved it using the keyboard and later dragged the whole park. Saved bench orientation and relative positions followed it.
6. Confirmed selecting a bench alone does not create an edit, and repeated drag/save after fixing a selection-layout shift.
7. Inspected the real timber bench in the 3D scene. Clicking it exposed park controls, not an individual-object editing mode.

Automated checks: focused bench geometry/persistence/editor, park reshape/layout and paused history tests; TypeScript type-check; lint on the new editor, geometry and modified history hook. The focused suite contains 34 passing tests. It covers removal of all benches, save/reload, parent transforms, different capture origins, malformed data, four park sizes, failed save draft retention, and keyboard isolation.

## Boundaries of this trial

- One supported park family and one bench model, up to 32 benches. Other parks, street furniture, trees and playground objects are not individually editable yet.
- Editing uses a 2D plan; 3D updates after saving. There is no separate 3D gizmo editor.
- Changing the park outline or adding access paths can put a saved bench in a conflict. The editor asks the student to reposition it; saved furniture is not silently discarded. Irregular reshaping and sloped terrain were not browser-tested in this trial.
- The trial data is local and belongs to the local QA account. No deployment, push or paid generation was performed.
- Screenshots and the fixture helper are outside the repository in `C:/dev-artifacts/CityPrompt/bench-editor-2026-10-08/`; source changes contain no generated binaries.
