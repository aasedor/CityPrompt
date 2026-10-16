# Safety catalogue release validation — 2026-10-15

Status: preview verified to the extent below; production promotion pending.

## Release decision

44 supplied variants and ten Calgary concept additions are enabled. All twelve
curb bulbs remain previewable but unavailable in both add menus and rejected by
placement validation. Their complete sidewalk attachment, old-curb replacement
and protected access-route integration remain unfinished. This is a partial
release, not acceptance of all 56 supplied assets for student placement.

The supplied GLBs remain byte-for-byte identical to approved manifests. All 66
models use the existing metre-scale loader, source pivots and rigid position/yaw.
No migrations, providers, paid resources or LFS policy changes are introduced.

## Executed preview checks

- Verified all 56 supplied hashes and all ten generated Calgary hashes, byte
  lengths and GLB containers. Per-asset records: asset-inventory.json and
  calgary-inventory.json.
- Actual browser WebGL load/draw for all 66 models. Safety-only static geometry
  batching preserves materials and vertex attributes. Pixel comparison reports
  zero changed pixels for all 66, with equal triangle counts. Total isolated
  single-model draw calls decrease from 1,597 to 263. The overhead pair decreases
  from 156 to nine; the RRFB pair from 150 to six. 100 overlapping instances were
  a draw-call scaling check, not a realistic frame-rate test.
- Full app disposable project 2aff81c0-143b-4263-a400-d6822a79aad6: all 54 enabled
  variants selected through catalogue controls, placed on an authored level
  Industrial collector roadway, saved and reloaded. Database revision 57 contains
  54 unique variants and 55 explicit road references (one repeated crosswalk).
  These deliberately overlapping stress placements were subsequently reduced
  through the arrangement editor; the complete snapshot is preserved externally.
- Actual narrow/sloped support rejection; preparation of a level site; choosing
  a wider road instead of stretching the crosswalk. Full footprint coverage and
  triangle height checks reject gaps and slopes, including during edits/replay.
- Arrangement selection, deletion, undo restoration and save exercised. Earlier
  pilot movement 0.5 m and rotation 15 degrees persisted. Automated tests cover
  copy, shared undo/redo, conflicts, delayed requests, deletion/recovery and
  unchanged off-screen items. Every operation on every variant was NOT tested.
- Exact 3D source export through the existing image presentation panel includes
  the crosswalk on the road. No paid AI image/video generation was submitted.
- Reloaded browser error log: no errors observed.

## Terrain and performance limits

Only loaded ribbon-street surfaces participate in support resolution. Authored
network-ground, polygon streets and junction meshes are not yet registered.
The full footprint must fit one compatible level surface. A road edit may make a
saved item unsupported; it stays saved, shows a recovery notice and blocks capture
until moved or removed through Arrange details. No silent terrain lift or stretch.

No physical student laptop/mobile measurements are available. Isolated desktop
GLB buffer counts exclude JS objects, render targets, driver overhead and cached
merged geometry. ZIP bytes are not runtime memory. No walking-FPS claim is made.
All supplied/source engineering, generic/concept, static amber and material
qualifications remain in catalogue descriptions and the preserved source reports.

## Evidence and rollback

Evidence outside Git: C:/dev-artifacts/CityPrompt/traffic-safety-restart-2026-10-15
(optimized-gpu-audit.json, optimized-captures, roadway-placement-trial.json,
roadway-reloaded-details.json, roadway-exact-capture.png, roadway-capture-ui.png).
Immutable source archives: D:/CityPrompt-traffic-safety-2026-10-15/source.

Production baseline, service IDs and rollback are recorded in
../plans/2026-10-15-traffic-safety-live-56.md. Deploy API compatibility before the
frontend. After new IDs have been saved, keep the compatible API when rolling back
frontend behavior; never erase saved details to satisfy an older release. Revert
the feature in a compatibility-preserving commit if a full rollback is necessary.

Independent code review found no P0/P1 runtime regression. Its stale 56-vs-66
test assertion was repaired by scoping supplied-kit assertions to its manifest.
Fresh verification before the release commit: 63 focused frontend tests and 62
existing-feature regression tests pass, 47 backend project-detail tests pass,
16 hosted/generated-asset tests pass, TypeScript and targeted ESLint pass.
The production build passes with 156 existing catalogue choices, 514 distinct
catalogue dependencies and zero delivery audit failures. Its selective public
packet contains 3,584 exact assets (1,537,725,373 bytes), including all 66 new GLBs
and ten Calgary WebP previews. Initial JS is 474.9 KB; total JS 8,415.1 KB is within
the existing 8,448 KB budget. Build output and logs remain outside source/ignored.
Push and live results will be recorded separately.
