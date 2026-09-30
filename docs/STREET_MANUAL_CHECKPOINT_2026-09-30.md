# Street Manual runtime checkpoint — 2026-09-30

Work on `codex/street-manual-completion`, based on `66f8b4b0a`.
This is a local pilot checkpoint, not final dimensional or classroom approval.
The exact-variant ledger is [STREET_MANUAL_REVIEW_2026-09-30.json](STREET_MANUAL_REVIEW_2026-09-30.json).

## Source authority

The supplied **Street Manual Draft 4.0a**, October 2025, is 146 pages and marked
FOR DISCUSSION. SHA-256:
`3d0e3e57431100a5dd487ed43522b6d8e67da354d43fb346c7cc013965943087`.
Page 70 lists 13 base cross-sections and several A/B/C variants. Its footnote
explicitly states that cross-sections were circulated separately as PDF files.
Those dimensional drawings were not supplied. The earlier Google Drive download
was a two-page Google sign-in capture, not the manual; it is not source evidence.

The implementation preserves the existing catalogue's recorded band dimensions.
A passing sum/mesh/hash test proves fidelity to that record, not to the missing
official drawings. The manual's walking/cycling guidance supports the separation
of raised cycle tracks from the carriageway, but does not establish the individual
recorded widths. Do not describe these pilots as City-approved or construction-ready.

## Implemented scope

Thirteen base sections, each with a new `<archetype>_manual_v1` saved identity,
shared frontend/backend manifest, immutable section hash, fixed metric width and
production capability binding. The original `_v0` selections remain unchanged.
New manual variants appear in the **Street Manual** picker category and existing
street controls, including the metric cross-section diagram. Routes use the shared
live preview, rounded bends, saving, automatic 3D updates and exact capture pipeline.
No new external model dependencies or paid generation requests were introduced.

| Figure | Base street | Recorded right of way |
| --- | --- | --- |
| 1 | Calgary Alley | 6.5 m |
| 2 | Calgary Local | 16 m |
| 3 | Calgary Local – Industrial | 18 m |
| 4 | Calgary Local – High Activity | 21 m |
| 5 | Calgary Local – Rural | 20 m |
| 6 | Calgary Collector | 20 m |
| 7 | Calgary Collector – Industrial | 26 m |
| 8 | Calgary Collector – High Activity | 27 m |
| 9 | Calgary Arterial – 4 Lanes Divided (50) | 33 m |
| 10 | Calgary Arterial – 4 Lanes Divided (70) | 36 m |
| 11 | Calgary Arterial – High Activity | 36 m |
| 12 | Calgary Arterial – 6 Lanes | 46 m |
| 13 | Calgary Skeletal | 60 m |

The new profiles retain the utility/setback strips, walking/cycle bands, parking
allocation and medians. Surface masks now preserve asymmetric utility strips.
Shared painting order was fixed after Walk exposed asphalt hiding the lane lines.
The manual variants use their own material colours and avoid blocky proxy cars,
automatically repeated transit shelters and unverified bollard layouts. Eligible
urban boulevards receive existing metric trees, lighting and furniture. Industrial
planting is withheld pending the utility-clearance drawings. The registry also
now derives every existing native street family from its inventory: three recent
native entries had selections but lacked matching family definitions.

## Verification performed

- Frontend: 173 tests in ten focused street/picker files passed. After the final
  furniture/material refinement, the 87 affected tests passed again; type-check passed.
- Backend: 23 tests across manual, catalogue and native candidate contracts passed.
- Production Vite bundle built successfully with public-asset copying disabled;
  source assets continue to use the existing hydrated public directory. This is
  build verification, not a fresh installation or production-browser acceptance.
- All 13 thumbnail URLs returned 200 with image content locally.
- Through ordinary student controls, drew a prepared redevelopment boundary and
  Collector route; then applied each of the other twelve sections to that route.
  Each returned to **3D saved / Drawings saved**. Screenshots capture those states.
- Collector: draft 3D preview, selection, overhead, Walk and exact street-view
  preview. Marking-order defect reproduced and visually confirmed fixed.
- High-activity Collector: Walk, Add bend point and handle drag, reload, exact
  identity/27 m width readback, three controls and a 15-point rounded centreline.
  Fresh exact street-view preview after reopening passed. Final image shows
  asphalt cycle bands without inherited proxy cars.
- Six-lane arterial / Skeletal: Undo and Redo restored the corresponding type.
- No user projects modified. No paid renders submitted. No push performed.

Local project: `http://127.0.0.1:5183/projects/60db592e-2d49-4cfb-8d53-fb8004c25784`.
Evidence: `C:/dev-artifacts/CityPrompt/street-manual-2026-09-30`.
`reopened-road.json` contains read-only API evidence of the student-authored road;
`screenshot-hashes.json` identifies screenshots. Browser authoring did not use API
geometry creation. Initial screenshots without `-applied` from a failed automation
selector are not variant-application evidence. Historical session errors include
older unrelated park/model failures, so this checkpoint makes no global clean-console
claim. The current backend log contains slow-request warnings, without a street failure.

## Remaining acceptance and source work

1. Obtain sections 1–13 and their A/B/C dimensional drawings; reconcile every band,
   utility reservation, curb/shoulder and marking treatment before freezing approval.
   Do not infer alternative parking/school sections from the base profile.
2. Rural ditches and the depressed Skeletal median are currently level grass bands.
   Vertical drainage geometry, clear zones, slopes, barriers, HOV details and design
   speeds are not certified. These types remain provisional.
3. Review every type from multiple close views and test intersections, public-road
   connections, natural/sloped terrain, size limits and failed-save recovery. The
   all-type Apply smoke pass does not satisfy those runtime gates.
4. Verify final exact captures and installation/asset delivery independently of the
   current local hydrated environment. Paid-image comparisons remain NOT TESTED.

Existing models/catalogue photos and the supplied manual remain unchanged.
Generated screenshots, logs and production bundles stay outside the source tree.
