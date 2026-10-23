# Claude models: local pilot and park-only correction

## Local integration acceptance update

User authorized integration of the corrected parks if checks passed. The three
park-only versions are enabled in the current local Parks picker. A fresh
ordinary-control trial deleted and placed **each** exact park again using the
picker and map, selected it, rotated it, and reloaded the saved project. Final
rotations are Halifax 10°, rink 20°, plaza -15°; all fixed plot dimensions and
runtime hashes persisted. No model geometry in that final scene was authored
through the API. The prepared boundary remains the original developer test
fixture. Captured browser error logs were empty during this bounded trial.

Fresh checks: 32 affected frontend tests, 9 backend tests, 4 derivative ownership
tests, and three exact HTTP-200 GLB/hash + thumbnail checks passed. The rink's
walking-view entry was also inspected in the actual app. No source behavior
change was needed: the existing DEV-only catalogue integration was already
enabled and passed these checks. No production activation is implied.

New evidence: external `local-trial/park-only-integration-final.json`,
`park-only-integration-before.json`, `rink-integrated-walk.jpg` and a completed
bounded runtime-review record for each exact park under
`local-trial/runtime-reviews/<asset-id>/RUNTIME_REVIEW.md`.
General terrain/route, mobile and student-laptop limits below remain open.

Status: local pilots only. No commit, push, source-branch merge, production
catalogue/storage/database change, deployment or paid AI generation was made.
Branch: `codex/claude-assets-local-trial`, based on
`056608657b2eb7582ad6dc2073f7c4426b5d87b4`.
Source branch `claude/ten-new-buildings` is pinned at
`2e6f4860b75545aebe5a9cccabb845f3943ba8e9`.
Inherited hydrated LFS differences remain untouched.

## Current scope

Discovery inventoried 69 candidates: 48 buildings, 5 parks, 15 streets/bridges
and one planting showcase. Thirty-three have prior passing source reviews;
two oversized context bridges remain held. This does not establish runtime
readiness. The planned bounded trial has 31 candidates. Five are currently
selectable local pilots: CMU Dock Warehouse, Inglewood Main Street and the
three corrected parks below. The other 26 remain pending, including Prince's
Island. No entire-cohort acceptance is claimed.

The user's park correction supersedes copying complete reference scenes:
off-site buildings do not belong in park placements. Original GLBs remain
immutable. Runtime derivatives remove off-site building shells, windows,
doors, roofs and trim. Plaza climbers supported by removed houses are removed;
supported east-parapet planting remains. Park-owned chalets, bandstand, gates,
terraces, stairs, glass, furniture and trees are retained. Native paving and
road/apron surfaces are retained in this pass and included in plot dimensions.
Prince's Island's pavilion belongs to its park; it is not a context building.

## Exact park versions

Dimensions are runtime width × depth × height in metres, including retained ground.

| Park | Source | Runtime revision | Runtime dimensions | Browser draw calls / triangles |
| --- | --- | --- | --- | --- |
| Halifax Public Gardens | v005 | park-only r001 | 72.955 × 90.760 × 14.460 | 859 / 1,585,082 |
| Ice Rink Market Square | v007 | park-only r001 | 53.600 × 73.515 × 14.990 | 43 / 129,224 |
| Stepped Terraced Plaza | v005 | park-only r002 | 40.000 × 58.000 × 9.410 | 1,397 / 497,140 |

SHA-256:

| Park | Immutable source | Runtime derivative |
| --- | --- | --- |
| Halifax | `a2b8dfc2241bf3681573e81d8ca757dfc0efd0cbb302879696fe436c85f31577` | `d94cefb6028ef823e075e5e9e229bdab8c1d0b8d2a6a24fcb30ab64d4a368250` |
| Rink | `1a0ca9fbffcb84fa1978280572934f19400145852353907a317c66e116ae3f75` | `6a578c3c8e3c54b729d50d83da473a52c1e039664c498ca4603343ee47bdd7a8` |
| Plaza | `36631aac2b3a5c42e620473a0993fd38e2a413526b5db9f9b22d43f16453aff4` | `c564869a31bef9348b9802574f837fec536846223ca1a9dcd5a08a3f594e3eb2` |

The local JSON registry holds full source and runtime hashes and source-review
hashes. Plaza r001 is retained as a rejected inspection checkpoint: a floating
house-cap strip was found, then removed in r002. No candidate was overwritten.
Retained vertex/normal/UV values and complete material definitions were checked
bit-for-bit against source. Unreferenced removed building bytes are excluded
from runtime files; node transforms are retained.

## Local app checks actually run

Open `http://127.0.0.1:5184/projects/763fe821-f9c7-4caf-b197-b025c4db8e5a`
while the existing local frontend/API/database/storage services are running.
This is a disposable local test project, not a real development proposal.

- All three park-only models saved and compiled through the normal local API;
  all three displayed together on a prepared level boundary in the actual app.
- Parks picker search `park only` shows exactly three corrected entries using
  screenshots of those derivatives. The context-heavy raw rink is retired
  from new discovery but its exact saved ID and bytes remain resolvable.
- Shared workflow trial on the rink: select by clicking the model, rotate 20°,
  drag the move handle, delete, undo, redo, undo to restore, then reload.
  Saved coordinates retain 20° rotation and a translation of approximately
  6.057 m east / 1.527 m north. All three parks retain exact runtime hashes.
- Free image export captured the three-park scene, opened the exact-3D preview
  and downloaded a valid PNG. No paid Generate button was submitted.
- Earlier warehouse/street pilot also exercised ordinary UI placement,
  selection, fixed sizing, rotation, street movement, delete/undo/redo and
  reload. Its original raw-rink project is preserved separately.

Technical checks: 32 affected Vitest tests across six suites; 9 narrow backend
tests; 21 catalogue-delivery/asset-guard tests; 4 derivative ownership tests;
TypeScript check; targeted ESLint; catalogue JSON/model-contract checks;
`git diff --check`. All passed. The backend emitted an existing pytest-asyncio
loop-scope deprecation warning.

Fresh independent review inspected all 18 current six-view screenshots, source
boards/code and exact derivative bytes. Context-removal visual category passed.
Review identified saved-revision enforcement and stale inherited inventory
measurements; both were corrected and re-reviewed without remaining blockers
in that scope. This is not holistic keeper, classroom or publication approval.

## Implementation and limitations

New DEV-only registry and fixtures reuse current catalogue, native loaders,
selection, edits, serialization and undo. Native public-realm centering is
explicitly opted in, preserving existing fixture origins. Backend exact local
fixture validation is restricted to development. Production rejects the local
namespace. Browser readiness also rejects mismatched saved revision, asset ID
or URL without substituting a generic park. Existing published IDs are unchanged.

Measured browser costs above use a desktop Edge browser and a 1280×720 isolated
QA canvas. CPU submission timings are not FPS or GPU-complete timings. Halifax
and plaza remain expensive local review assets; laptop/mobile suitability,
repeated instances in the actual app and heavy-park optimization remain pending.
No stretch, repeatable floors, route bending or new circulation capabilities
are claimed. Per-model interaction/capture acceptance beyond this shared pilot
has not been completed. Native steps and sloped circulation still need further
walk/access testing. Ground/road aprons have not been trimmed.

## Evidence and reproducibility

External root:
`C:/dev-artifacts/CityPrompt/claude-model-discovery-2026-10-22`.

- `quality/technical-audit.json`: immutable source models, source locks/reviews.
- `park_only.py`, `test_park_only.py`: bounded context removal and ownership checks.
- `quality/park-only-r001/inventory.json`: current runtime measurements and
  separately labelled source measurements/reviews; current plaza is r002.
- Adjacent `.provenance.json`: exact source/runtime hashes and each removed
  component/node, plus preservation assertions.
- Adjacent 18 current screenshots and `browser-measurements.json`.
- `register_park_only.py`: local DEV registry/public copy setup; no production writes.
- `local-trial/park-only-app-checks.json`, `park-only-after-reload.json`,
  `park-only-picker.png`, `park-only-app-overview.png`,
  `park-only-capture-preview.png`, `park-only-exact-capture.png`.

Exact capture SHA-256:
`50ac9cb7f1934fce0aba1891a987e3b0e42e063fd7f45026824af13cea2bc452`.
Runtime GLBs and thumbnails live in the existing external local public tree at
`C:/dev-artifacts/CityPrompt/add-details-recovery-2026-10-12/public/validation-assets/claude-local/`.
They are not committed binaries. A new machine needs those exact hashed files;
the source checkout alone does not reproduce this unpublished local trial.
