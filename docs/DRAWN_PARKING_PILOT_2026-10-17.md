# Drawn parking lots: local pilot, 2026-10-17

Later same-day extension: see [the driveway and real-development trial](PARKING_DRIVEWAY_TRIAL_2026-10-17.md).
The results below describe the original checkpoint, before road connections and
the three authorized paid tests were added.

Status: implemented and locally trialled; **not published**. Branch:
`codex/drawn-parking-pilot`, starting from
`3e73508bfcc1caed57540713592f9653d4dc138a`.

## Try it

Open the local app at `http://127.0.0.1:5184`. The disposable project is
`/projects/dd6893db-311c-470d-8023-b223b3d56eb6`, named
“Drawn parking lots · local pilot”. It belongs to the existing local Animation
browser QA account. No real user project was altered.

Choose **Design → Streets → Parking lots → Draw parking lot**. The plan opens
with corner placement active. The original **Add details → Arrange details &
custom paving** route remains available for editing saved lots and other details.
Click outline corners in the plan, then **Finish parking lot** and **Save details**.
Select its outlined shape in the plan to edit it. Choose rows along/across the
first edge, rotate the whole lot by 15 degrees, move its centre or individual
corners, or remove it. Undo and Redo cover both lot and object edits.

## Runtime integration review

This is a procedural public-realm surface, reviewed against
`ARCHETYPE_RUNTIME_INTEGRATION.md` and `ARCHETYPE_RUNTIME_REVIEW_TEMPLATE.md`.
It is not a building GLB, and adds no binary assets or catalogue storage rows.

- Recipe: optional `parking: {version: 1, rowAngle: 0 | 90}` on existing
  `scene_details.surfaces`. Stable surface IDs, geographic coordinates, material,
  revision checks and project permissions use the existing details API.
- Dimensions: concept perpendicular bays, 2.7 × 5.5 m; 6 m circulation aisle
  and side connector; 0.5 m perimeter allowance. These are visualization defaults,
  not a verified Calgary engineering or accessibility design.
- Limits: 64 outline corners, 15,000 m², 300 m across in the row frame, 500 spaces
  per lot; existing project surface-count limits still apply. Invalid/no-fit
  outline changes reject without changing the saved lot.
- Geometry: metre ENU coordinates; first corner remains the paving origin.
  Whole-lot rotation preserves real bay sizes. Boundary edits recompute capacity.
  Complete bay/aisle modules must fit the polygon, including concave cutouts.
  A bounded interior-spine search permits slightly tapered edges.
- Ground: existing paving/prepared-site contract; paint is 5 mm above the actual
  triangulated paving surface. No second opaque marking backing, building
  clearance, terrain flattening or automatic public-road connection is added.
- Resources: one base surface and one merged paint mesh per lot, disposed on
  replacement. Layout is memoized and not regenerated during each walking frame.
  Existing procedural asphalt texture is reused by convention; no image downloads.
- Compatibility: old paving records omit the new optional field, and round-trip
  unchanged. No migration, production configuration, provider or LFS-policy change.
  Any later publication must include both the API recipe contract and frontend.

| Check | Result | Evidence / practical limit |
| --- | --- | --- |
| Rectangular and irregular outlines | PASS locally | Browser created a four-corner lot and six-corner L lot; unit fixtures include concave/tapered outlines. Conservative packing may leave usable-looking areas empty; it does not maximize capacity. |
| Real-size layout and count | PASS | Exact 40 × 18 m unit fixture: 24 spaces along, 16 across. Browser lot: 24 → 16 after corner edit. Fixed bay dimensions asserted independently. |
| Direction and whole-lot rotation | PASS locally | Browser switched 24 → 16 → 24; 15-degree whole-lot turn retained 24. Review found and fixed the unsupported intermediate-angle spinner. |
| Selection, movement, corner edit | PASS in plan editor | Selected lime outline, move centre, corner edit and recount. Direct clicking/dragging the parking surface in the 3D map is not implemented. |
| Delete / Undo / Redo | PASS locally | Browser removal: lot count 1 → 0 → 1 → 0 → 1. Automated shared detail-history regression also passed. |
| Save / full reload / reopen | PASS locally | Both lot recipes restored via actual local API; six-corner lot reopened with 16 spaces and was moved/resaved. |
| Existing building mixed scene | PASS locally | Calgary Modern Infill placed beside both lots; normal save and 3D generation reached “3D saved”. |
| Prepared-ground contact and walk | PASS for tested level site | Human-height view shows readable paint above asphalt; walking input tested. No certification for hills, holes or tile refinement. |
| Aerial and street source captures | PASS for mixed scene | Actual free aerial PNG and Street view 3D preview include paint and asphalt. No paid AI or video generation. |
| Boundary plus details only, before first physical-zone compilation | BLOCKED by existing workflow gate | Present disables Image/Video because residual landscaping is absent. Placing the house compiled the site and enabled capture. This pilot does not bypass the residual-landscape guard. Boundaryless parking-only capture remains NOT TESTED. |
| Browser console | PASS for captured final check | No captured console errors returned by browser diagnostic. This is not a long-duration guarantee. |
| Review | PASS for bounded pilot | Independent review found one Important direction-control issue; follow-up confirmed resolution and independently ran 10 parking tests. No remaining Critical/Important findings reported. |
| Sloped/natural-ground coverage | NOT TESTED | Corner-derived paving can bridge irregular ground. Keep the pilot on prepared level surfaces. |
| Site landscape and automatic trees | NOT TESTED | Parking metadata is not a compiler-owned occupied zone; automatic planting/AI landscape exclusion has not been added. Keep generated vegetation clear manually. |
| Public road / sidewalk access | NOT IMPLEMENTED | A clear internal connector does not create an entrance, curb cut, ramp or accessible route. |
| Accessible bays, cars, islands, angled stalls | NOT IMPLEMENTED | Existing individual details remain available separately; no automatic distribution. |
| Student laptop/mobile performance | NOT TESTED | Only this desktop/IAB and local CPU microbenchmark were measured. |
| Production / paid AI fidelity | NOT TESTED | No push, deployment, paid generation or credit changes. |

## Tests and measured cost

- 68 tests passed in 9 frontend files covering parking layout/editor, paving
  geometry/ground, shared detail editing/persistence and direct capture preview.
- 54 tests passed in `backend/tests/test_project_details.py`, including legacy
  paving round-trip, version/angle validation and bounded area.
- `npm run type-check` and ESLint on every changed TypeScript file passed.
- Initial default build stopped because this isolated worktree's default public
  folder is not hydrated. Rebuilt with the already verified local public directory
  and environment, using Vite's normal production build API with
  `copyPublicDir: false` and external output: passed, 3,814 modules. This verifies
  application compilation and configured asset guard, not a fresh deployable asset
  publication. Existing large-chunk warnings remain.
- Actual two-lot desktop sample, Balanced: 57 fps / 18 ms, 2177 × 1180 buffer,
  297 total scene draw calls and 216,667 triangles. These totals include Google
  tiles. The earlier one-lot sample (56 fps, 9 calls) had different tile loading
  and **cannot establish an incremental cost or speed improvement**.
- Local Node CPU microbenchmark: 24-space rectangle, 100 measured runs after
  warmup, median 0.342 ms / p95 0.649 ms for layout; paint 144 triangles,
  10,368 typed geometry-attribute bytes. 490-space 140 × 100 m fixture, 20 runs:
  median 4.063 ms / p95 4.862 ms; paint 2,940 triangles / 211,680 attribute bytes.
  This excludes base mesh, texture, GPU overhead and other scene content.

## Evidence, changed sources and rollback

External generated evidence remains outside Git:
`C:/dev-artifacts/CityPrompt/parking-pilot-2026-10-17/`.
It includes `aerial-capture.png`, `street-capture.png`, `walk-browser.png`,
`two-lot-plan.png`, performance text samples, `layout-measurements.json`,
production-code build output and local API logs. PNG content was extracted from
the app's actual free previews; an actual Download button/file-delivery test was
not performed.

Sources: new `parkingLot.ts` and tests; `PavingEditor` controls/plan; paving
geometry height lookup; `GlobePavingSurfaces` merged paint; `BenchDetailEditor`
redo history; API optional recipe validation and associated tests. This report
is the only documentation addition. No generated output or binaries are staged.

Local rollback: switch to the base branch/commit and restart local frontend/API.
Existing old scenes remain compatible; do not edit newly authored parking
recipes with the old API contract. Production is unchanged. Before any later live
release, resolve the capture-only boundary gate, landscape exclusions and remaining
terrain/performance/publication checks above.
