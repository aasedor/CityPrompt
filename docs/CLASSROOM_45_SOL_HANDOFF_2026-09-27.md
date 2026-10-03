# Sol browser acceptance: the 20 / 15 / 10 catalogue

Run this phase with **gpt-6-sol** after the Astra build phase. This document is a
handoff, not evidence that browser testing has happened. The additions remain
local pilots until observed results justify a different status.

Checkout: `C:/dev/CityPrompt-approved-validation`.
Build branch: `codex/classroom-street-catalogue`, inheriting the separate park
checkpoint `ced60e946` and building checkpoint `ce24487c8`.
App: `http://127.0.0.1:5180`; backend: `http://127.0.0.1:8006`.
Use the existing local validation account/session. Credentials remain in private
local setup, outside Git; do not expose provider configuration or invent logins.
Confirm the checkout commit and running service paths before recording results.

Read the classroom park, building and street catalogue documents and exact
ledgers dated 2026-09-27. The complete visible roster is
`classroom_student_roster_2026-09-27.json`; it is a list of choices, not an approval
list. Existing model revisions and earlier limited browser evidence stay intact.

## Bounded checks with ordinary student controls

Create disposable projects; leave the user's existing projects untouched. Do not
seed geometry through scripts, APIs, database writes or console evaluation.
First test one new park, building and street, fix blockers, then continue in
small groups. Record PASS / FAIL / NOT TESTED per exact variant and action.

1. Confirm 20 building, 15 park and 10 street choices are searchable and distinct.
   Check thumbnails, labels and selection. Alternate Basketball layouts do not
   increase the park-type count; sibling building variants must remain distinct.
2. Place every choice at native size. Compare aerial and walking-height views
   with the exact offline/source evidence. Check entrances, materials, full
   components, paths, ground contact, tree positions, duplicate surfaces and
   floating/buried or missing models. Do not grant a group pass from one sample.
3. Move and rotate each new addition, undo/redo, save, close and reopen. Check
   stable identity, position and orientation. Try insufficient space and ensure
   a useful message preserves the previous valid design. Advanced resizing is
   deferred; fixed native buildings/parks must not stretch their contents.
4. Draw each street point by point. For the three additions test native length,
   double length, reverse direction, a moderate bend, a tight rejected bend and
   connection to another street. Cycle Avenue is 24 m wide / min 48 m; Green
   Alley 11 m / min 40 m; School Street 18 m / min 48 m. Max is 480 m. Check
   markings, fixtures and end clipping; no building-like placement rectangle.
5. Explicitly inspect building door approaches and tower framing. Check the
   Foursquare's loading/performance. Parks need complete native paths/equipment;
   Botanical v013 remains the visual benchmark. Existing Basketball Long must
   retain two complete courts and connected access.
6. In mixed scenes, make rapid moves then immediately open aerial and street-view
   render preparation. It must await the current saved scene and required models
   automatically. Confirm exact source capture includes all expected objects,
   preserves the custom prompt, and needs no manual Community 3D/landscape step.
   Do not submit paid image/video requests: no new provider budget is authorized.
7. Record console/network failures and useful loading/recovery behavior. Include
   a cold reopening and a representative mixed scene with larger buildings,
   planting-rich parks and longer streets to assess student responsiveness.

Keep screenshots, logs and captures outside the source tree in a new dated
evidence directory. Each result needs variant/revision, commit, disposable
project, action, observed outcome and evidence path. A blocked step is NOT TESTED,
never an inferred pass. Summarize classroom blockers separately from refinements.
Only promote exact variants after their actual evidence passes. Do not push,
publish, replace old saved bindings or broaden to new archetypes during testing.
