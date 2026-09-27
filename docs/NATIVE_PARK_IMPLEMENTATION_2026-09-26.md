# Native park implementation checkpoint

Initiative: original eight parks plus Basketball Long. Worktree:
`C:/dev/CityPrompt-approved-validation`, branch `codex/custom-render-prompts`.
Starting commit: `014300ecc3f41eed93bb7fe0c098363243f8add5`.

## Source and runtime boundaries

The original handoff ZIP and `seed/validation/runtime-assets.zip` are unchanged.
The native registry in `frontend/src/data/nativeParks.json` has an exact backend
copy checked by tests. It records immutable source hashes, recipe hashes,
composition transforms, native dimensions and occupied dimensions. Acceptance
status is separate from content identity.

The Basketball and Botanical native layouts and the Basketball Long composition
are local pilots, **not completed or published variants**. The remaining six
registry entries are withheld pending the pilot's application and visual review.
Their existing legacy placements are not upgraded automatically.

Original Botanical geometry remains 48 × 62 m. Actual mesh bounds project about
7–10 cm beyond those dimensions; its placement reserve is 48.2 × 62.2 m. Never
scale or crop its original assembly to erase these projections.

Basketball Long uses two complete 36 × 23 m court modules centered at x=-20/+20
m in a 92 × 39 m parcel. It preserves source bench/tree assets and vegetation
scale 0.72, with separately authored circulation and source grass/paving colors.
This is a new composition requiring visual review, not a reapproved source file.

## Implemented pilot mechanisms

- Schema-v2 native park recipes in `public_realm_lego`, resolved and checked by
  the server; schema-v1 remains supported. Unknown revisions cannot become a
  generic fallback. Semantic source hashes include the native selection/frame.
- Content-addressed asset staging, embedded-dependency checks and browser
  SHA-256 verification before a model can claim ready. Saved park identity is
  independent of cache URLs and timestamps.
- Explicit layout preview/apply/cancel with one atomic undoable save. Failed
  fit/save keeps the previous park. Model proportions never follow parcel size.
- Explicit legacy upgrade; native move/rotation frames are restored on undo.
- Shared prepared-ground ownership, entrance connector solver and capture
  readiness. Capture expects each current native instance and waits for loads.

Reproduction (no provider calls):

```powershell
python scripts/stage_native_parks.py
python scripts/stage_native_parks.py --public-dir C:/dev-artifacts/CityPrompt/approved-validation-2026-09-24/public
```

The first command verifies without writing. The second refuses conflicting
existing bytes and writes only missing content-addressed GLBs. A different
public directory is supported for a local production build.

## Evidence and remaining gates

Evidence directory: `C:/dev-artifacts/CityPrompt/native-parks-2026-09-26/`.
The development fixture `/native-park-review.html` uses the same NativeParkModel
renderer as the application, but **does not establish application acceptance**.
Its screenshots cannot prove persistence, project terrain, editing or capture.

GPT-6 Sol is assigned browser verification. The user restarted Docker after its
startup failure. The existing isolated Postgres 55432, Redis 56379 and MinIO 19002
containers and validation API 8006 are now running; browser login succeeded.
No database reset or replacement was performed. Saved-project checks are ongoing.

The user approved the six aerial/walking-height pilot fixture images on
2026-09-26: continue the remaining six once application checks pass. This approval
is recorded separately from runtime acceptance in
`docs/native_park_acceptance_2026-09-26.json`.

Do not roll out the next pairs or mark any runtime row PASS until the original
pilot passes in a disposable project and its visual review is recorded.
Next pairs: Sculpture/Orchard; Performance/Square; Wetland/Teaching.

Paid authorization: **at most five single-image Sunburst submissions**, failed
requests included. Current submitted count: **0**. The required sequence is
native Basketball aerial, Long Basketball street, Botanical walk, mixed eight
parks aerial, Teaching street after movement/reload. No comparison batches,
automatic paid retries or provider substitution. Record request IDs and source
captures in the external evidence ledger before proceeding to another request.

Unfinished acceptance: authenticated placement/edit/save/reload and shared-ground
checks, genuine production-preview browser verification, five paid image checks,
and the six-park rollout (human pilot visual approval is already recorded). Do not infer completion from unit
tests or the isolated visual fixture.

## Verified local checkpoint

`4c5c4e31c`: native registry, server recipes, source freshness and asset staging.
No push or publication. The frontend pilot is being verified in disposable
project `eb222ee2-61ab-4f8f-a4ea-d2ac9f36148f`.

Focused checks so far: 78 frontend tests across 11 files, TypeScript check,
103 native/public-realm backend tests, 37 native/residual/site-landscape tests,
and 198 direct-render/presentation/zone API tests passed. These suites overlap;
these counts are not a count of unique tests. The initial source registry and
all 11 embedded-dependency GLBs passed source/hash checks. Long's conservative
component bounds do not intersect its primary 2.4 m paths.

The production build succeeded using a bounded public directory containing the
native GLBs; all 11 production HTTP responses matched their locked SHA-256.
This is an asset/bundle smoke test, not full production scene acceptance:
other large shared catalogue assets are omitted. The first full-public build
was stopped while copying the large shared catalogue. A command to link those
assets into the smoke output was rejected by automatic approval review without
a specific reason; no links were made.

Development hot reload exposed an existing canvas-listener lifecycle issue:
Botanical preview followed the pointer but clicks did not reach the API.
A full page reload restored placement immediately. The listener lifecycle now
reattaches on effect restart; its browser regression remains pending. Treat
hot-refresh evidence separately from saved-project reload. Native asset errors
now keep Retry 3D update visible even if background compilation finishes.
Unit checks cover that race and recovery after a failed asset download.
