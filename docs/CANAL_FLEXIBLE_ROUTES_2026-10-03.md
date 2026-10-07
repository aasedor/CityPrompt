# Flexible canal routes — 3 October 2026

## Scope and implementation

Street-fixes branch, based on `30de8b2c188864c014e64941dfefec0c6fdf8037`.
The user requested the flexibility of ordinary street authoring rather than
the canal's fixed-study length restrictions. This is a local source change;
the running app on port 5199 and its project were preserved.

The canal now uses the ordinary 36 m-wide street authoring range, 36–2000 m,
and the shared rounded route controls. Add bend point, endpoint edits, boundary
snapping, bank connections, and walking use the drawn route. The width stays
36 m; the water remains 18 m wide and 2.05 m below the prepared site.
Prepared level ground remains required. Ordinary roads cannot cross the water.

Straight routes at least 80 m retain the original basin, arch and furnishings
assembly, followed by the existing detailed open-channel extension. Shorter
and bent routes use continuous brick quays and channel geometry, a compact
closed head, native trees/benches/lamps/bollards, and the unscaled source arch.
The arch moves to a straight run with room for both complete approaches.
A continuously curving route with no such run remains drawable without an
arch; the settings explain how to leave a straight stretch for a crossing.
Short routes omit furniture that would obstruct the arch's approaches.

The source GLBs and source programme hashes are unchanged. Mirrored
`canalRoutePolicy.json` files describe the expanded authoring contract.
The backend retains the exact old capability for existing recipes, including
their old length limits and historical catalogue identity. New routes use
the expanded capability. Old hashes do not authorize expanded targets.

## Runtime review

This is an agent-run implementation and geometry pilot, not human visual
approval or a full classroom release. Existing source modules remain locked
to their recorded hashes in `nativeStreetPilots.json`.

| Gate | Status | Evidence / remaining work |
| --- | --- | --- |
| C1 Identity | PASS (automated) | Existing saved classroom recipes still validate; new 36, 53.7, 79, 334, 712.5 and 2000 m recipes round-trip. |
| C2 Dimensions | PASS | 36 m section; source module scale 1; bridge transformed centre checked against its selected station. |
| C3 Ground | NOT TESTED live | Existing prepared-ground gate retained. Preview cutout regression passes; full terrain inspection remains open. |
| C4 Freshness | PASS (automated, partial) | Existing route/draft changes retain preview recovery tests; interactive late-save races not retested. |
| C5 Circulation | PASS (automated, partial) | Actual curved route projection follows banks and relocated arch; water is not a walking floor. New live pedestrian traversal remains open. |
| C6 Editing/persistence | PASS (automated, partial) | Bend and route tests plus server recipe round-trips; signed-in browser save/undo/reload of the new implementation not run. |
| C7 Recovery | PASS (automated, partial) | Short/valid/oversize/valid previews remain editable; missing ground still blocks geometry. New live failed-save exercise not run. |
| C8 Visibility | PASS (geometry pilot), capture NOT TESTED | Hydrated short 53.7 m, long 334 m and bent canal inspected in browser; no console errors. Exact project export not run. |
| C9 Student controls | NOT TESTED end-to-end | Existing app's 217 m preview and old 334 m rejection reproduced before editing; new ordinary-control save remains open. |
| S1 Metric section | PASS | Native width and rigid modules preserved; water and bank geometry tests. |
| S2 Topology | PASS (automated, partial) | Bent canal bank protection, endpoint snapping and existing street tests pass. Live bank connection review remains open. |
| S3 Grade/public connections | NOT TESTED live | Prepared level gate and prohibition on ordinary road crossings retained. |
| S4 Clearance | PASS (geometry pilot) | Arch sits on a straight run; short-route furniture yields around approaches. Exhaustive curve/canopy inspection not run. |
| B1–B5 / P1–P4 | N/A | No building or park implementation changed. |

## Verification and local outputs

- 215 tests passed across 13 focused Vitest files, including the canal,
  drawing preview, route editing, bank connections, walking, bridge and rail.
- 22 backend tests passed in `test_native_specialist_streets.py` and
  `test_native_street_candidate_contract.py`.
- `npm run type-check` passed; `git diff --check` passed.
- `PlacementPalette.test.tsx` has a pre-existing pagination assertion failure:
  it expects all 28 parks after one 12-item page expansion, which shows 24.
  Reproduced with the unmodified HEAD component. Six other tests passed.
  This unrelated release-cleanup issue was left unchanged.

Ignored outputs: `artifacts/canal-review/` contains screenshots and prototype
source; `frontend/test-results/canal-review/` contains the served review page.
These are not source deliverables and were not staged. The review uses the
hydrated assets in
`C:/dev-artifacts/CityPrompt/road-trial-ui-recovery-2026-10-02/public`.
The checkout's own public files contain LFS placeholders.

The separate frontend preview runs on `http://127.0.0.1:5202`.
Its geometry review is `/test-results/canal-review/index.html`; this page uses
the production geometry and module placement code without changing a project.
It is not evidence of a signed-in application save against the revised backend.
