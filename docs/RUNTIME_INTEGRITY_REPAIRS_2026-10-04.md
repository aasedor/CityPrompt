# Runtime integrity repairs — 2026-10-04

This initiative repairs the reviewed City Prompt snapshot without replacing its
authored buildings or promoting the ten local trial families. The source baseline
is `0d7a9ddad515b862bdd332656738fbee0962f2c6`; the repair branch is
`codex/runtime-integrity-repairs-2026-10-04`. It reuses the maintenance checkout.
There are nine registered worktrees. No main-branch integration or push is part
of this checkpoint.

## Behavior and data contracts

- Saved asset identity includes the asset ID, variant and model revision. The
  explicitly registered older Buff-brick model retains revision
  `3c7ab81c4db3c2a67ec280788ff84008da0cbd20a16129feba75dffcfcd0d4a6`
  and its 10.48 m authored height. The current Buff model remains 10.68 m and
  Charcoal remains 9.64 m. Unknown saved revisions require an explicit replacement;
  they cannot silently inherit today's model URL.
- Fixed native buildings use authored dimensions and storeys in controls,
  assembly planning and rendering. Building type can be derived for display
  without automatically rewriting saved metadata. Explicit new edits retain the
  exact selected revision. Plot geometry remains separate from building geometry.
- Student report method `student-review-v2-placement-plots` reports placement
  plot area separately. Native plots and GLB bounding boxes do not establish
  measured footprints or floor plates. Missing measurements produce incomplete
  footprint/GFA results. Existing report snapshots and student responses remain
  unchanged and carry a historical-method notice, including printed HTML.
- Full-project Community 3D recovery reloads the complete current persisted scope
  once after a source conflict. Newly added zones join that retry; removed zones
  leave it. Selection and boundary actions retain their bounded scopes. A second
  conflict stops instead of retrying indefinitely.
- A shared classification map governs picker groups and guide interpretation.
  Category descriptions are not legal zoning approvals. Legacy guide assertions
  use explicitly named saved rosters; retired choices are not reactivated.
- The selected image engine persists per project through panel reopen/reload and
  prompt updates. An unavailable explicit preference remains visible and blocks
  generation with an actionable message. No paid generation was used to test it.
- Fifty-eight duplicate JSON members were reconciled by retaining their existing
  effective final values. The duplicate checker prevents recurrence in CI and
  builds. Generated backend native-model metadata must match the frontend source
  contract; `npm run check:catalogue-json` checks both conditions.

## Asset delivery and installation

The delivery audit includes five rustic park GLBs and the registered historical
Buff revision. Development delivery can read verified objects from the shared Git
LFS cache while leaving tracked pointer files unchanged. Missing or corrupt bytes
return an explicit error. A verified external catalogue packet provides portable
assets and copies its payloads into production output.

Use `frontend/scripts/check-catalogue-delivery.mjs` to audit declared dependencies
and create a packet with `--packet-dir=<external-directory>`. Supply the declared
public assets and seed assets, hydrated through Git LFS or an existing verified
packet. HTTP auditing additionally requires a fresh Model Library storage receipt
through `--library-report`. `CITYPROMPT_CATALOGUE_PACKET` binds an existing packet
for Vite development, preview and production builds. Keep packets, reports and
build output outside source directories. A production build needs the portable
packet; a developer's LFS cache alone is not a deployment artifact.

Install the declared Model Library using `tools/seed_model_library.py` and the
reviewed manifest under `seed/model-library/rlasm-architectural-clay`. The isolated
rehearsal selected the 19 building candidates declared in `classroomExpansion.json`
with `--rlasm-clay-only --local-trial --candidate <candidate>` and a private owner,
database and bucket. The manifest loader validates its 23 declared GLBs and 69
reference photos before applying the selected candidates. Local-trial status and
owner scope were retained. Use `scripts/check_model_library_storage.py` to verify
stored payloads against their exact declarations.

The frontend checker can refresh backend contract metadata with
`node scripts/check-model-contract.mjs --write` from `frontend`; review that
specific JSON file and rerun `npm run check:catalogue-json`. It does not modify
model bytes, seed manifests or asset activation.

## Preserved state and verification

Verification artifacts are outside Git at
`C:/dev-artifacts/CityPrompt/repairs-2026-10-04`. The original runtime on port 5176
and its source checkout were preserved. The repaired preview on port 5177 uses
an isolated restored database and private bucket; browser edits affect that copy.
The source baseline database still contains five projects, 34 zones, 21 buildings,
19 library records, one report and one user. Seventy-three original media objects
(238,559,176 bytes) were backed up, cloned and verified against their hashes.
The database dump SHA256 is
`f90119bbd49ef39634161bb355e3b4fef526f4bf73398a04266ef2ca0e5ad051`.

The backup receipt is recorded in
`baseline/preservation-receipt.json`; use that receipt when restoring. Restore
only to a named separate recovery target before considering any live data change.
There is no database migration or bulk saved-project rewrite in this repair.

Validation completed:

- 212 frontend tests in 15 targeted files; TypeScript type checking passed.
- 45 backend/storage tests and 11 Node delivery/data tests passed.
- Maintenance and fresh-source production builds passed. Both outputs contained
  all 316 packet assets with exact size and SHA256 matches.
- The HTTP catalogue audit covered 105 local choices and 365 dependencies with
  no failures. This is delivery evidence, not visual approval of every choice.
- Sixteen concurrent GLB requests retained the existing ten-second timeout;
  all returned exact bytes, with the slowest taking 0.1961 seconds in this local
  run. The local fixture launcher validates its sealed manifest once and checks
  payload identity on delivery, rather than parsing all ten models per request.
- Browser checks covered current Buff and Charcoal heights, the historical Buff
  model, placement-plot report quantities, Sunburst persistence after reload,
  park placement and rotation/undo/redo/save. A controlled two-tab compile used
  a seven-zone request, received 409, then included all eight current zones and
  succeeded on its one permitted retry. The copied project retained its models.
- A bounded fresh-source export with no Git checkout or G-drive dependency built
  successfully and installed 19 models into an empty database/private bucket;
  19 of 19 stored models passed exact readback checks. It reused the existing
  dependency installation and schema; this was not a new-machine OS or dependency
  installation test. The fresh database remained free of projects.

Large existing JavaScript chunks still produce Vite warnings. Bundle optimization,
paid-provider execution, legal-policy certification, and visual approval of the
ten trial families are outside this verified repair. Original model geometry,
reference photos and rendered images were not regenerated.

## Recovery and handoff

Retain the verified database/media backup and external asset packet. The preview
launcher explicitly binds its copied database and bucket and blocks paid image
requests. Its temporary conflict-test barrier and logs are verification helpers,
not application features. The repaired source has no dependency on those helpers.
To return to the approved application, use the unchanged port-5176 runtime.
To deliver this repair elsewhere, build with the verified packet and install the
declared private Model Library into that environment; do not copy personal
credentials, local fixture bindings or test databases into a public deployment.

Before integration, review this coherent repair commit against the approved
baseline and run the relevant checks in the target environment. Runtime-required
assets belong in a declared delivery mechanism; future reference collections and
heavy visual-QA output remain external to the source tree.
