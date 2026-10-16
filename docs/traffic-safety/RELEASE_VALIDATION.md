# Safety catalogue release validation â€” 2026-10-15

Status: partial release live and representative hosted checks passed. Twelve curb bulbs remain disabled.

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

## Live-discovered precision correction

The first rollout (ec0b3d0fa) exposed a polygon-clipping sweep-line ring-stitching
exception during cushion positioning on densified road triangles. It interrupted
the scene without deleting saved data. The failure was reproduced locally using
the actual buildRibbonBandGeometry builder (101 stations, three lane bands).

The support calculation now intersects convex footprints with triangles using
half-plane clipping and subtracts each covered triangle from uncovered convex
pieces. Duplicate/overlapping faces cannot conceal holes. Height/slope checks and
the full-footprint requirement remain; pathological fragmentation fails closed.
The previously failing 500-position sweep passes, as do duplicate-face/hole/slope
tests. Independent math review found no critical/important issue. Actual local
browser placement at three stations, undo and redo pass with no console errors.
Fresh affected suites: 23 tests, TypeScript and ESLint pass. The corrected hosted
build passes all catalogue, asset and bundle gates (156 choices; total JS
8,415.7 KB within 8,448 KB). Follow-up live results are recorded below.

## Verified production release

- Live URL: https://www.cityprompt.ca
- Repository aasedor/CityPrompt; source branch deployment-version, feature branch
  codex/traffic-safety-live-56. Both code commits were pushed without force.
- Frontend commit f4c6a739ec383176dc5f992e06b5af42c3996217;
  Render deployment dep-db8nblei0phs738an9bg, live 2026-10-15 19:00 MDT.
- API commit ec0b3d0fa878c0a5708bec44d86585450fee8857;
  deployment dep-db8n04ei0phs7389ff50. No backend changes in the frontend fix.
- Public version.json matches the frontend commit. /health matches the API commit;
  /ready reports database, Redis, storage, image worker and reference worker ready.
  Classroom starter assets are not enabled. Hosted build reports source_dirty=true
  after asset hydration; the build receipt is not a clean-tree claim.
- Render production build passed: initial JS 474.9 KB; total JS 8,433.2 KB within
  8,448 KB; CSS 188.6 KB within 192 KB. npm reported 11 dependency vulnerabilities
  (3 moderate, 8 high); dependency remediation was not part of this asset release.
- All 66 live model URLs return HTTP 200, valid GLB 2 containers, exact manifest
  SHA-256 and byte lengths. All ten Calgary WebPs return HTTP 200 and exact hashes.
- Actual signed-in picker shows all five supplied groups (4/24/8/12/8) plus ten
  Calgary additions. All twelve curb-bulb choices remain disabled as intended.
- Disposable live project f7d1149e-4b0b-4617-adc9-69eec401796c:
  crosswalk, standard unlit RRFB, 6 m unlit overhead arm and TC flexpost curb were
  placed and saved through the picker. The first cushion attempt exposed the
  precision crash above. After the correction deployed, the same cushion position
  saved successfully. Global undo/redo passed. Arrangement selection/deletion,
  0.5 m east movement, 15-degree rotation and save passed. Reload retained three
  final objects with no recovery notice. Close-up crosswalk road contact was
  visually inspected. Closely spaced test hardware was removed using the editor
  because its existing conservative object-clearance check blocked arrangement
  saving. The fixture is a workflow test, not an approved traffic layout.
- Existing project The Exchange — live student plan was loaded read-only. Its
  buildings, parks and street geometry displayed; walking entry, movement and exit
  passed. No scene data was edited. No console errors observed in either fresh
  live tab; no missing-resource/CORS error observed during these checks.
- Exact live 3D source export passed through the existing Image panel. Paid AI
  image/video generation was not run for this release; AI semantic preservation
  and video output remain unverified. No paid credits spent.

Independent visual review inspected all 66 model captures and found no critical
corruption, missing parts or obvious family swaps. RRFB rectangular bars remain
visually distinct from overhead round heads and black signs/white figures.
Raised-zebra ramp grades still need a low-angle capture to certify visually;
metadata and the isometric image alone are not installation/clearance proof.
Physical laptop/mobile performance and every operation on every live variant
remain untested. Those limitations do not change the twelve-bulb placement block.

Final external receipts: live-final-asset-audit.json,
live-final-thumbnail-audit.json, live-final-health.json, live-final-ready.json,
rollout.json. Screenshots: live-roadway-close.png, live-exact-source.png and
live-existing-project.png. Independent contact sheets:
visual-review-sheet-{1,2,3}.jpg. All are under the evidence directory above.

## Changed-file guide

- frontend/src/features/parks: catalogues, grouped selectors, support validation,
  static geometry batching, placement/editor compatibility and focused tests.
- frontend/src/components/viewer/globe/GlobeStreetDetailLayer.tsx: loaded road
  triangle registration for conservative safety support.
- backend/app: optional saved support-zone reference, preserving legacy props.
- scripts: selective hosted assets and generated-asset checks; no LFS policy change.
- frontend/public/street-kits: 66 reviewed GLBs under existing LFS rules and ten
  intentional WebP previews. Source GLBs are unchanged; runtime batching is in memory.
- docs/traffic-safety and docs/plans: inventories, evidence and rollback path.

Rollback remains the pre-recorded Render history procedure. After new IDs are
saved, keep the compatible API and use a compatibility-preserving frontend revert;
old releases must not silently discard the newly saved detail IDs. No rollback
was needed. This final evidence-only commit does not require another deployment.
