# Traffic-safety integration

Current evidence and release scope: [RELEASE_VALIDATION.md](RELEASE_VALIDATION.md).
44 supplied assets and ten Calgary concepts passed placement/save/reload; twelve
curb bulbs remain disabled. Production promotion is still pending. The sections
below preserve the earlier checkpoint and are superseded by that validation log.

## Historical checkpoint — before restart and support integration

**Not ready for production. No push or deployment has been performed.**
Working branch: `codex/traffic-safety-live-56`, based on c56414430.
Production identity and rollback references are in
`../plans/2026-10-15-traffic-safety-live-56.md`.

## Restart recovery — 2026-10-15 evening

The Docker blocker described below is resolved after the user's Windows restart.
Existing PostgreSQL, Redis and media containers were started without replacement.
The local API runs on 8012 and frontend on 5174 with the existing runtime profile;
the Calgary candidate gate is enabled only for this local process.
The frontend startup audit reports 151 choices, 504 dependencies, zero failures.
`GET /ready` now returns ready: database, Redis, storage and reference worker pass;
durable image worker and classroom starter checks are not enabled locally.

Before applying the repository's existing startup migrations, a 2,197,059-byte
database backup was saved at
`C:/dev-artifacts/CityPrompt/traffic-safety-restart-2026-10-15/local-before-existing-migrations.dump`.
Normal Alembic startup applied the missing legacy document-task branch and merge
revision `031_merge_legacy_documents`. No migration source was created or changed.

Actual app pilot: disposable project `2aff81c0-143b-4263-a400-d6822a79aad6`
(Traffic safety — local roadway acceptance). Created a no-parking local road,
verified all five group counts plus ten Calgary candidates in Add Details, and
placed `calgary_delineator_illustrative_r1`. Page reload preserved the item and
the editor displayed its correct variant. A 0.5 m east move and 15-degree rotation
saved as revision 2, verified by local database readback. This is one-item
persistence evidence, not acceptance of all variants or roadway datum alignment.
No paid generation, Git push or production deployment occurred in this recovery.
Road-height/flatness and curb-host integration remain release blockers.

## Completed checks

- Five authorized source ZIPs preserved at
  `D:/CityPrompt-traffic-safety-2026-10-15/source`; extracted originals alongside.
- All 56 GLB counts, SHA-256 hashes, byte lengths and containers match manifests.
  Runtime copies remain byte-for-byte identical; no mesh/material adaptations.
- All 56 load through the browser GLTFLoader with verified response hashes.
- All 56 draw through the existing `buildDetailInstances` implementation in an
  isolated local WebGL harness. Oblique images were saved and visually inspected.
  This is **not** full CityPrompt scene or placement acceptance.
- 46 narrow frontend tests pass across eight files: grouping, fixed datum,
  existing instances, placement history, duplication, project serialization and
  source-bound curb attachment validation. These are not browser workflow tests.
- 44 backend project-details tests pass, including every new ID, legacy-data
  preservation, revision conflicts and rejection of arbitrary scale fields.
- 13 hosted-asset tests pass; new catalogue included in selective asset preparation.
- TypeScript check and lint of all changed TypeScript files pass.

## Implemented locally

The metadata describes five groups and 56 stable variants, with rigid metre
transforms, source pivots, labels, dimensions and visualization limitations.
Family cards expose supported size/state choices. Safety GLBs use zero extra
datum lift; legacy furniture retains its prior 0.084 m lift. The server registry
accepts the new IDs using the existing project metadata schema (no migration).

The 12 original attachment curves and polygons are extracted without changes from
`footprints.json`, SHA-256
`12524be5dba5d9db363a7cf764052b747f48875d8682053ba200f90d047c6354`.
`scripts/import_traffic_safety_contracts.py` refuses any other source bytes.
The pure curb attachment validator checks the whole ordered seam in both
directions, the 150 mm height and protected access polygons; it returns the
remaining portions of a host curb without mutating the host. **It is not yet
connected to sidewalk authoring/rendering or persisted host references.**

Detail placements, edits and deletions now register per-item changes in the shared
undo/redo store. Replay uses the current revision and preserves unrelated items;
remote edits and failed saves retain history instead of overwriting data. The
catalogue permits normal undo keyboard shortcuts, and selected items expose
"Place a copy" with the original variant/yaw. A delayed-save test guards leaving
and returning to the same project while an old request is in flight.

## Unfinished gates / blockers

- Curb bulbs require matching complete sidewalk attachment curves, a 0.15 m deck
  above the road datum, old-curb replacement and ramp/access-route rejection.
  Current Add Details and street geometry do not implement this contract. The user
  approved extending sidewalk integration on 2026-10-15; implementation is underway.
  Do not enable them on an intact curb or assume bounding-box alignment is enough.
- Road-height resolution and full-footprint flatness validation remain to be wired
  into placement/movement/rotation and all scene renderers. Current base ground
  sampling is insufficient for 4 mm paint above an authored street surface.
- Docker Desktop failed startup with an inaccessible
  `C:/Users/andre/AppData/Local/Docker/run/sailor-ingest.sock`; its Linux engine and
  the local API/database are unavailable. Do not reset Docker or delete volumes.
  A normal quit/restart reproduced the error. With Docker fully stopped, an exact
  rename of that runtime socket also failed with the same Windows error; no file
  was moved or deleted. Docker is currently stopped. The user was asked to restart
  Windows and reopen Docker Desktop, without factory reset. No production repair
  or deployment was attempted to bypass the preview gate.
- Actual application selection/duplication/deletion/undo-redo, browser persistence,
  AI scene capture, mixed scenes, terrain/depth and live smoke checks remain open.
- Full build/lint/regression suites, independent review and production deployment
  have not run. No representative laptop/mobile hardware has been tested.

## Measured costs and limits

56 GLBs total 6,052,912 bytes. Isolated single-model drawing used 0 textures;
highest decoded geometry buffer allocation measured was 460,344 bytes for an
overhead pair. This excludes JS objects, driver overhead and render targets.
That pair draws 8,272 triangles in **156 draw calls**; the RRFB pair uses 150.
Repeated-instance/frame-time tests and a baseline comparison are still required.
These numbers do not establish student-laptop suitability.

The source reports disclose illustrative hardware dimensions, uncalibrated PBR
materials, static amber rather than operational flashing, generic/concept marking
patterns and no engineering/compliance approval. Bulb skew/asymmetric footprints
were tested mathematically; only the 12 standard meshes have independent audit.

## Evidence and restart

`asset-inventory.json` contains all 56 IDs, source/runtime hashes, dimensions,
URLs, browser results and screenshot paths. Detailed evidence is outside Git at
`D:/CityPrompt-traffic-safety-2026-10-15/`, including `browser-load-audit.json`,
`browser-gpu-audit.json`, `gpu-captures/` and browser screenshots.

The local diagnostic is `http://127.0.0.1:5174/traffic-safety-review.html` while
the worktree Vite server runs. It is not a production route. Runtime GLBs under
`frontend/public/street-kits/traffic-safety-r1` remain ignored/uncommitted until
promotion; existing LFS rules cover them. Preserve the source ZIPs and never
stage a whole generated directory. Final promotion must use an explicit inventory.
