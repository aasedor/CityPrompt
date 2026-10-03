# Runtime integration review — Treetop Walk Park

## Candidate and scope

- Park: `student_treetop_walk_v1`; exact model `8e89485ba931a223f7ae334db5018bce1958f8c6f669a8d525e50d141ab0e30a`.
- Revision: `aef679e13148ddede9c39e73dbea57d74c23b41400d0363f3a132f93b6e72366`; source base `7855cd6cf` plus this finite park pair.
- Codex author review, 2026-10-01, Windows Chromium, 1264 × 625, mouse and keyboard.
- Disposable project: http://localhost:5186/projects/719fced3-0ea1-4e7d-8337-dc6a5a31cd65. Ordinary UI draws the Currie boundary,
  prepares the site and places both parks. API/debug reads verify saved values;
  no API writes or walk-pose changes were used.
- Native plot 56 × 64 m; metre X/Y ground plane,
  Z up, base at 0; standard GLB Y-up conversion. Model remains unscaled inside
  an enlarged 72 × 80 m parcel rotated 8 degrees.
- 816,558 triangles; 1422 mesh instances. Kit vegetation
  uses authored scales recorded in recipe; routes and tree crowns stay separate.
- Material geometry, joints, furniture and planting checked in seven reimport views.
  Aerial and pedestrian finish compared against conservatory-v013. Original design,
  not a reconstruction of an external reference photograph. Modules and source
  snapshots are included with exact hashes.
- Asset review PASS_AUTHOR_VISUAL_REVIEW; human visual approval and publication pending.
- Static public GLB and thumbnail hash readback; frontend/backend registry parity.
  Model Library bucket checks are N/A for this native park asset path.

## Gates

| Gate | Status | Evidence / limitation |
| --- | --- | --- |
| C1 Exact identity | PASS | Saved layout, content revision and exact GLB SHA survive reload. |
| C2 Dimensions and transformations | PASS | Enlarged/rotated parcel and move; native mesh scales preserved. |
| C3 Full footprint support | PASS | Prepared site, settled scene, zero grounding issues; exported bounds fit declared occupied footprint. |
| C4 Freshness and late results | PASS (bounded) | Ready exact revision after edits/reload; pending-edit and interrupted-network cases not repeated. |
| C5 Pedestrian continuity | PASS (internal) | Actual GLB route samples and app keyboard walk in both directions. External street connection NOT TESTED. |
| C6 Edit / Undo / save / reopen | PASS | Exact coordinates and selection compared after move/Undo/Redo/reload. |
| C7 Failure and recovery | PASS (bounded) | Return to park entrance and exit controls; shared automated missing/corrupt-model checks. Network fault injection NOT TESTED. |
| C8 Low/aerial views and capture | PASS (views) | Reimport renders and browser screenshots; export download and paid imagery NOT TESTED. |
| C9 Student controls | PASS (agent simulation) | Catalogue search, card, placement, reshape, walking; novice usability NOT TESTED. |
| B1–B5 | N/A | No building authored in this initiative. |
| S1–S4 | N/A | No street authored in this initiative. |
| P1 Exact program and rigid amenities | PASS | Complete native assembly with visible stairs, planted beds and seating. |
| P2 Shared park terrain | PASS (prepared) | Native prepared-level contract; natural terrain unsupported in this delivery. |
| P3 Automatic remeasurement | PASS (bounded) | Move/parcel reshape settle to current ready scene. |
| P4 Park access and grade | PASS (internal) | Entrance and rise checked; public connection and step-free route not claimed. |

## Bounded live matrix and evidence

- `treetop-browser-walk.json`: complete circuit forward and reverse via normal
  WASD/arrow-key controls, including ascent and descent; no pose injection.
- `walking-verification.json`: 4,838 samples, 0.44 m body clearance,
  maximum tread rise 0.15 m; material-aware checks against actual exported GLB.
- `pair-before-move`, `pair-moved`, `pair-undo`, `pair-redo`, `pair-reloaded`:
  coordinates, revision and selection readbacks. Regenerated recipe timing may differ;
  exact saved geometry and model selection agree.
- Direct canvas selection after reload, native-size placement, parcel enlargement,
  8-degree parcel rotation, movement and recovery tested. Both models visible together.
- Treetop undersized rotated parcel rejected; enlargement recovered without losing
  the existing park. This error case was not repeated on rose.
- Exit controls and entry recovery passed. Zero captured browser exceptions and
  zero grounding issues in the settled pair scene.
- Sloped/natural terrain, maximum parcel size, explicit public-road approach,
  mixed building/street scene, pending-ground edits, delete/Undo, forced save conflict,
  export download and paid render are NOT TESTED for these new variants.
- Full evidence root: `C:\dev-artifacts\CityPrompt\treetop-rose-parks-2026-10-01`. Durable exact offline/render evidence and compact
  runtime report retained beside this review in Git LFS/source files.

## Verification and decision

48 focused frontend tests, 44 backend native-park tests and TypeScript check pass.
Prior catalogue entries preserved. No shared walking or terrain behavior changed.
Runtime decision: PASS_LOCAL_PREPARED_SITE within the scope above. Visual decision:
author pass. Publication/activation: pending separate human decision. Original user
projects and unrelated street assets remain untouched.

Archived pergola module geometry retains its authored terrace elevation; the complete assembly is the supported runtime asset. Individual module restaging was not exercised.
