# Vacant Currie entrance browser QA — 19 September 2026

This continuation verified the explicit entrance approach on the **visibly
vacant Currie parcel** using the local browser at `127.0.0.1:5174` and backend
at `127.0.0.1:8000`. The existing main fixture
`f5bffc94-def9-4c43-942e-9ae7411872e9` was read only. A bounded positive
pilot used a new disposable copy, `0899968f-b8a6-416b-b893-4826684b2a69`,
with the same eight-vertex boundary, first western Craftsman bungalow and
matching six-metre street. Evidence and one-time scripts are outside Git in
`C:/dev-artifacts/CityPrompt/grounding-batch-a/`. No paid AI endpoint or push
was used.

After the browser fix, the final focused regression run passed **141 tests
across 13 files**. `npm run type-check`, changed-file ESLint, and
`git diff --check` passed. The full test suite was not run.

## Results

| Check | Outcome | Evidence and limit |
| --- | --- | --- |
| Main fixture baseline | PASS for warning; entrance still unresolved | Shared ground was ready with two passes and seven visible houses. All seven raised foundations reported `entrance_connection_required`. The frozen east camera still showed the native bungalow steps ending on the cap (`entrance-main-east-before.png`). The free export rejected with the new actionable Connections message. The main site's geometry and entrance settings were not edited. |
| One-house disposable copy | PASS for faithful setup | `entrance-pilot-project.json` records the copied boundary, house, street and building. The initial view matched the main bungalow (`entrance-pilot-east-before.png`). |
| Authored anchor | PASS for measured model foot | In the loaded native `CLAY_STONE` mesh, the bottom step reaches model base at `z≈11.045 m` and spans `x=-0.85…2.75 m` before the model's centering transform. The authored plot offsets are `x=0.9 m`, `y=-10.35 m`, height above base `0`, scaling off. The route planner reported a connected plan route. The closest generated approach vertex to the center of that native step edge was **0.0119 m** in rendered world coordinates. This is a bounded mesh measurement, not a human access certification. |
| Original street setback | Correctly unresolved | Street-to-step run was 2.918 m with about 2.41 m rise, requiring 14 bounded treads. The code reported `entrance_approach_too_short` and drew no approach. A 0.6 m westward move in the disposable copy still reported too short (3.518 m run). The model or terrain was not stretched or flattened. |
| Supported one-house placement | PASS for concept geometry | An additional 0.6 m westward move, 1.2 m total, remained within the unchanged vacant parcel and did not overlap the street (`entrance-pilot-move{,2}.json`). The 4.118 m run showed 14 treads and no grounding issue. The frozen east and close northeast images (`entrance-pilot-east-supported.png`, `entrance-pilot-northeast-close.png`) show the top join and street-side run. The generated side walls read as bulky concept geometry; accessibility, guards and exact constructed dimensions still require design work. |
| Free exact 3D export and identity | PASS in the pilot | `entrance-pilot-free-capture-preview.png` shows the exported frame. The approach mesh carried the selected street's `siteforgeDirect3DInstance.zone_id`; the bungalow retained its own building ID. The export opened a preview without paid generation, and browser page errors were empty. |
| Rotate, Undo, Redo, reload | PASS | The bungalow went from 95° to 97° through the UI. Its approach remained present and issue-free: 292 geometry vertices at 97°, 324 after Undo, 292 after Redo and 292 after reload. The saved plot rotation and anchor remained aligned. This did not remeasure the native top join after every angle. |
| Delete target street and Undo | Initial FAIL, then PASS after source fix | Deleting the street removed stale approach geometry and produced `entrance_approach_obstructed`. The existing Undo path recreated the street with a new ID, leaving the entrance pointed at a missing target. The fix uses the existing zone snapshot restore endpoint to preserve zone identity on Undo of deletion and Redo of creation. On a fresh UI retry, Undo restored the same street ID, route and approach; a reload retained the restored route without a warning. |
| Capture during refinement | PASS in one bounded attempt | `entrance-refinement-capture-result.json` records free export clicked while shared ground was `sampling`, with zero entrance issues. The preview opened in `ready` about 7.2 seconds later (`entrance-pilot-refinement-capture.png`). This one pass does not establish every interruption or retry ceiling. |

The disposable copy's final authored entrance points to street
`f7133443-d9cf-49d5-9d22-cc6e0ddbddd5`, which the fixed Undo preserved. The
copy's house is at 97° and 1.2 m west of its source position. The reference
main Currie fixture still holds seven houses, the park, street, unchanged
boundary and 95° bungalow, with its unresolved entrance and capture block.

## What remains for the student-ready goal

The entrance feature is accepted only as a **one-house concept pilot on a
setback-adjusted copy**. Batch A remains blocked on the unaltered seven-house
layout: its bungalow needs a deliberate layout or entrance design decision,
and the other six raised houses need their actual entrances reviewed. Do not
infer that the whole site is accessible from one concept stair.

Next, settle the first house's street setback and entrance design in a
reviewed layout, then pilot the remaining houses one at a time with current
model geometry. Replace the coordinate-heavy Connections task with reviewed
native entrance metadata or a clear visual anchor workflow before the novice
journey. Then complete the remaining edit/recovery and presentation gates in
`STUDENT_TRANSFORMATION_GATES.md`, followed by a small student pilot. Park,
street-end and full mixed-slope checks from the previous continuation also
remain open.

A subsequent seven-house layout review is recorded in
`CURRIE_FULL_LAYOUT_ENTRANCE_REVIEW_2026-09-19.md`. It established that 1.2 m
and 2.4 m westward alternatives fit the original boundary and neighbouring
plots. The first house's measured connection remained issue-free in the full
copy, while the other six retained entrance warnings. Pedestrian screenshots
show that the high foundation and long stair still need design refinement;
neither alternative was promoted to the main fixture.
