# Classroom catalogue runtime status — 27 September 2026

The local validation catalogue exposes **45 exact choices: 20 buildings, 15 parks and 10 streets**. The exact variant IDs, source revisions and asset hashes remain in `frontend/src/data/validationCatalogue.json` (27) and `frontend/src/data/classroomExpansion.json` (18). Those files are the identity roster; their inherited `runtime_status: NOT TESTED` fields are package-snapshot metadata, not a claim about this later browser session.

## Current evidence and decision

| Gate | Result | Evidence / limit |
| --- | --- | --- |
| Exact roster and local selection | PASS for 45/45 | Frontend catalogue tests and live student picker; all 10 streets offer route drawing. |
| Native visual mounting, ordinary edit and cold reopen | PASS for 45/45 across the combined bounded checks | The first browser matrix tested every exact choice. Targeted retests cleared its five failures: Side-by-side duplex identity, Crystal brewhouse rotation/fit feedback, and the three new native streets. |
| Automatic Community 3D update | PASS in the repaired street scene and one larger disposable scene | Each settled to `3D saved` after load/edit. Long-scene latency and rapid multi-user editing were not benchmarked. |
| Connected new-student sample | PASS for Halifax, Buff-brick, Quiet Residential Street and Reading Garden after shared access repairs | A disposable prepared site supported real 3D step picking, park-to-sidewalk connection, move/rotation, cold reopen, Walk and a downloaded free exact aerial PNG. This four-choice sample does not establish connected access for the other 41 exact choices. |
| Placement rejection | PARTIAL | Crystal retained its last valid geometry after an out-of-bound shape request and displayed the reason plus a persistent `Shape not saved` message. The bridge rejected unsuitable terrain in the first run. A per-item insufficient-space check for all 45 remains open. |
| Image rendering | PASS for five bounded Sunburst requests; broader fidelity review open | A new student project saved five AI images: original-scene overhead, oblique, Halifax Walk, Botanical Walk and overhead after a saved house move and cold reopen. All five images and their exact-scene records loaded after reopening. The provider originals carry `review_required`, so this is workflow evidence rather than blanket visual approval. Video was not tested. |
| Human visual release approval | OPEN | Browser inspection is evidence of app behavior, not a new approval of every exact asset version for classroom release. |
| Publication | VALIDATION BRANCH ONLY | This record does not mark the catalogue classroom-complete or authorize a merge into the release branch. |

The native street runtime missed three family registrations even though their saved backend recipes were valid. Commit `99c19b649` registers them. Sol browser retesting then showed Ruelle Verte, Protected Cycle Avenue and Playful School Street with their native details at overhead, oblique and Walk height, after bends and cold reopen. The same check confirmed render controls enabled without a paid submission.

The Side-by-side duplex shared its parent archetype with Calgary Modern Infill. Commit `e921691b6` makes the editor select by exact catalogue choice, and the live retest showed the correct building type and variant before and after reload. Crystal brewhouse accepted a clear-site 10° rotation and retained it after reload. A separate deliberately oversized edit was rejected without changing the saved plot; the editor now states that the draft shape was not saved and shows the fit reason.

Commit `7a253f898` derives the catalogue heading from the current selection and updates its focused checks. The live picker showed 20 building, 15 park and 10 street choices; the larger disposable project reached `3D saved` after the street repair.

A separate new-student trial used project `1b503f29-b1dc-418e-a7ca-67c785791a34` at Nose Hill Park. The student drew a site, placed Halifax, Botanical and Neighbourhood Main Street, then moved Halifax and cold reopened. Botanical required the prepared-ground option: placement on terrain-following ground was rejected with an actionable message; **Clear site for redevelopment** allowed the same native park to save. Five single-image Sunburst calls returned AI images and cost 690 City Prompt tokens in total. After reload, Project Renders held five viewable AI originals and five paired exact-scene records; all ten thumbnails loaded. The last render reflected the moved house and had a changed scene-revision hash. The AI originals' `review_required` status and the absence of per-item fit checks keep human release approval open.

Evidence is outside the source tree:

- `C:/dev-artifacts/CityPrompt/classroom-45-sol-2026-09-27/acceptance-report.md` and `matrix.json` — original per-item checks and screenshots.
- `C:/dev-artifacts/CityPrompt/native-street-runtime-retest-2026-09-27/retest-report.md` — three native streets after repair.
- `C:/dev-artifacts/CityPrompt/building-runtime-retest-2026-09-27/retest-report.md` — duplex identity, accepted Crystal rotation and rejected shape.
- `C:/dev-artifacts/CityPrompt/fresh-student-five-render-2026-09-27/five-render-report.md` and `audit.json` — the fresh project, five AI images, source views, saved records and remaining image-review limit.
- `C:/dev-artifacts/CityPrompt/connected-student-qa-2026-09-27/REPORT.md`, `zones-redacted.json` and three exact/Walk captures — ordinary-control connected sample and repair retest.
- `C:/dev-artifacts/CityPrompt/catalogue-visual-review-2026-09-27/REVIEW_LEDGER.md` and `exact-variant-ledger.json` — per-choice source, isolated runtime, sampled connection, fit and visual-release gates. The 45 source identities were checked as 36 local files, four local-server byte responses and five street manifest fingerprints; the latter are not a standalone assembly byte readback.

Keep the catalogue available as a **validation collection**. To mark an exact choice classroom-complete, record its remaining fit/no-fit behavior and obtain the intended human visual approval against its locked source revision. Do not transfer approval to a later hash by archetype name alone.
