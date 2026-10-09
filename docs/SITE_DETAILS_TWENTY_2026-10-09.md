# Twenty site-finishing details — 9 October 2026

Branch: `codex/site-details-twenty`. Local implementation; not pushed or deployed.

## Delivered inventory

The Add Details catalogue now contains 165 choices (145 existing plus 20 new).
All additions use metric, lightweight GLBs, live model previews, existing search,
placement, rotation, selection, movement and project persistence.

| Category | New objects |
| --- | --- |
| Access & levels | Outdoor stairs, accessible ramp, modular handrail, retaining wall, tactile curb ramp |
| Traffic & safety | Pedestrian refuge island, accessible parking bay, loading zone |
| Landscape | Planted curb extension |
| Street furniture | Bicycle locker, EV charging station, community noticeboard |
| Edges & gates | Waste enclosure, privacy screen, cafe barrier |
| Water & landmarks | Public art sculpture |
| Shelters & markets | Covered bicycle parking, food truck, public washroom |
| Garden & growing | Rainwater cistern |

Catalogue JSON is authoritative for labels/categories and asset measurements.
The 20 GLBs total 1,284,012 bytes. The largest object has 5,928 triangles;
each uses at most seven material meshes. Existing instanced detail rendering
is retained. The development review grid measured 79 draw calls and 25,736
triangles for all twenty objects plus its ground.

## Geometry and walking

`tools/detail_catalogue/build_site_details.py` reproduces the bounded set using
Blender. The pilot and subsequent visual review corrected ramp entry geometry,
parking markings, refuge strip orientation, curb warning-strip placement and
washroom wall joints before promotion.

Stairs, the 1:12 concept ramp and the tactile curb ramp include explicit walking
profiles. A mount-time spatial index follows the exact model placement and
rotation; walking does not raycast the GLBs or scan every object. Ascending,
descending, leaving a profile, rotated placement, registration cleanup and
non-walkable furniture are covered by focused tests. Existing building interior
inspection retains priority.

These are fixed-size concept design objects. Rails, walls and screens can be
repeated manually; automatic joining and adjustable rise/length are not included.
The washroom has an open doorway and visible interior fixtures. Dimensions are
design aids, not a claim of building-code or accessibility approval.

## Verification

- Frontend: 23 tests passed across detailCatalogue, DetailPlacementPanel,
  detailWalking, detailInstances and useDetailPlacement; TypeScript check passed.
- Backend: 43 project-detail tests passed, including all twenty IDs, persistence,
  rotation and invalid input rejection. Existing project security/access checks
  also passed (32 tests).
- Generator: five tests passed, including actual GLB metadata, dimensions and
  walking profile checks against the reviewed export.
- All twenty locally served GLBs returned valid GLB data with SHA-256 matching
  the catalogue.
- Browser: all twenty loaded together in the development review grid. The live
  picker showed the new Access & levels category and real model previews.
  Repeated ramp placement, stairs placement, selecting a placed ramp, changing
  its rotation to 45 degrees, moving it and reloading were verified. The moved
  ramp remained in its new position with its saved 45-degree rotation.
- Browser: walking mode opened beside a placed ramp and displayed it at eye
  level. Sustained up/down traversal was not verified by browser automation:
  brief automated key presses did not produce a useful walkthrough. The walking
  profiles are covered by the automated tests; manual keyboard traversal remains
  a useful acceptance check.

Trial project: `724900f5-82fa-481f-9c25-38d78ee1da66`, “Site finishing · twenty
detail trial”, on the existing local Animation browser QA account.

## Source and generated evidence

Selected runtime GLBs live in `frontend/public/street-kits/site-details-v1/`
under the existing Git LFS rule. Catalogue metadata, backend allowlist, generator,
walking integration, tests, review-page filter and runtime manifest are source
deliverables. No paid generation calls were made.

Visual experiments, Blender previews, contact sheet and browser evidence remain
outside the repository at
`C:/dev-artifacts/CityPrompt/site-details-twenty-2026-10-09/`.
The reviewed `deliverable/` contains the final twenty GLBs and previews;
`browser-twenty.jpg` shows the actual browser model grid, and `browser-ramp.jpg`
shows a placed ramp at walking height. Earlier experiments were preserved.
Pre-existing untracked street reference images were not included in this change.
