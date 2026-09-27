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
requests included. Current submitted count: **2** (native Basketball aerial and Long street succeeded). The required sequence is
native Basketball aerial, Long Basketball street, Botanical walk, mixed eight
parks aerial, Teaching street after movement/reload. No comparison batches,
automatic paid retries or provider substitution. Record request IDs and source
captures in the external evidence ledger before proceeding to another request.

Authenticated pilot checks now pass for native Basketball placement/reload,
Long preview/cancel/apply, Botanical placement, move/rotate/undo/redo, reopening,
walking-height inspection, overlap rejection and exact 3D image export.
The exported source is `exact-source-current-view.png` in the evidence directory;
its SHA-256 is `f91275684f1bc0f2c867a8c7f3e06e4046ab4b7c4d8eb5cb58b84d397f2afa6f`.
Entrance connection verification passed on an 86 m Pedestrian Market Street:
the Basketball approach meets the street, stays clear of the courts, is grounded
in Walk and survives reload (`street-connector-walk.png`, `street-reloaded.png`).
An earlier 166 m route near Botanical did not finish; its rejection reason was
not captured and remains unconfirmed. No street implementation was changed.

Unfinished acceptance: the next pairs' entrance/shared-ground checks, genuine production-preview
browser verification, five paid image checks and the six-park rollout. Human pilot
visual approval is recorded separately. Do not infer completion from unit tests
or the isolated visual fixture.

## Verified local checkpoint

`4c5c4e31c`: native registry, server recipes, source freshness and asset staging.
`3dcaa1ae9`: native pilot editing, rendering and capture integration.
`48cc42468`: capture checks use the current scene; layout controls follow undo.
`81a434558`: unsupported custom terrain and invalid exclusions receive recoverable
validation errors; native parks do not expose unsupported terrace controls.

After the approved pilot passed its app gate, Sculpture Court and Neighbourhood
Orchard were enabled for local pair-one review. Their measured entrances are
recorded in the registry, with Orchard capped at its 1.8 m clear width. Their
native GLB bytes are unchanged. Existing native approaches now reserve space
against new placements and residual trees. Pair-one browser acceptance is pending;
Performance/Square and Wetland/Teaching remain withheld.
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

The exact-layout runtime review records are initialized under the external
`runtime-reviews/` directory. Unrun gates remain NOT TESTED. The source GLBs
contain about 3.27 million triangles across all eight native assemblies;
`model-budgets.json` records per-layout triangle counts and dependency bytes.
This is a measured source budget, not a performance pass. The mixed-scene browser
check must still establish usable visual performance without altering the originals.

The first paid Sunburst result preserved the one-court park, its entrance and
plaza relationship, and the separate conservatory garden in the aerial source.
Source/result are `paid1-source.png` and `paid1-result.png`; individual hoop and
furniture counts are too small at this scale for a definitive component audit.
The external paid ledger records the hashes and the one submitted request.

Shared regression checkpoint: six added cases reproduced stale native-layout load
errors, missing side entrances (including 90-degree rotation), a lost approach
inside an asymmetrically enlarged parcel, flat Walk height on native steps and
paving-only probing of a timber deck. They now pass. Entrance protection follows
the measured entry-to-arrival axis; the solver considers its projection onto the
actual parcel edge. Walk samples verified native paving, boardwalk and lawn
surfaces in the saved placement frame. Asset errors are scoped to that selection
and cannot leak from superseded edits or deleted parks. Null exclusions now match
the server's recoverable validation policy.

Measured entrance metadata is prepared for all remaining layouts, but only
Sculpture/Orchard are active for the current pair review. Performance/Square and
Wetland/Teaching remain withheld. All original pilot registry entries and all
asset identities are unchanged. The shared registries are byte-identical and the
hash-verified staging check passes for all 11 files. Paid request two succeeded after this code checkpoint; its paired source matches
the pre-submit source SHA exactly. Botanical comparison and pair-one app review
are continuing on the frozen runtime.

The production surface-probe functions were also bundled outside the repository
and run against all nine layouts loaded through the real SHA-verifying asset
loader on port 5180. All nine measured full-width entrance arrivals were found.
Performance stair samples returned 0.1333, 0.4, 0.6667 and 1.2 m; Wetland returned
0.22 m. The probe correctly retained missing approaches at Basketball, Sculpture
and Teaching rather than covering their original paving. Results and script are
in `actual-native-surface-probe.json` and `probe-native-surfaces.mts` under the
external evidence directory. This is actual-asset verification, not a substitute
for the pending in-app Walk and connection checks.

The second Sunburst result preserved the two fenced court areas and the plaza
stalls, lamps and benches. Four hoops are partly occluded, so complete visible
hoop-count fidelity is not asserted. The paired original and pre-submit source
both have SHA-256 `227b198a99f57ddc87fef8e957d592c3b4f8de3ddc767a6834a22a099982b9fb`.

The latest shared fixes and pair-one activation also passed a fresh production build. The external production-build-checkpoint.json locks its manifest and registry SHA. It remains a bounded bundle/asset check; production browser acceptance and the final all-eight rebuild are still pending.

The third and final pilot Sunburst comparison succeeded at Botanical walking height. Its paired original matches the pre-submit source SHA `75500aa7d5424371abd84a9043a64aeb5080fd0fd9fddee8ccb16ccd6e300178`. The split curving paths, conservatory, fountain and broad flower-bed layout remain recognizable in place. Added foliage/flower detail is not proof of plant-by-plant fidelity. Three of five authorized submissions have been used; mixed-scene and moved/reopened Teaching checks remain pending.

Pair-one browser checks passed placement, rotation, move, Undo/Redo, reopening and overlap rejection for both exact parks in disposable project `5d79af7a-f92b-406b-b52d-f05083b48743` (361 x 224 m prepared site). Orchard Walk and exact source passed. Sculpture exhibited speckled paving in Walk and exact capture. An actual-GLB ray probe found its zero-height paving/soil coplanar with its original edge/base cap at all 25 sampled ground positions. A runtime-only depth policy now prioritizes planar datum finishes using cloned materials; original geometry, material colours and model bytes remain unchanged. Focused tests and type-check pass; browser recheck is pending and the pair remains unaccepted.

The first conventional polygon-offset fix failed its browser recheck. The active globe uses logarithmic fragment depth; the finish policy now adds an explicit small conditional depth bias after Three's log-depth calculation as well. A real-asset probe confirms only Sculpture's planar paving and soil receive the policy, while originals remain untouched. The focused shader/material tests and type-check pass; the second browser recheck is pending.

The second depth fix passed Walk before/after a small camera turn and the exact captured source (`pair1-depthfix2-sculpture-exact-source.png`): the broad moving patch is gone, with paving/soil still present and no new shader/compile errors observed. The remaining small triangular flecks are the original native gravel aggregate (source builder lines 127–138, heights 6–14 mm), not the previous overlap artifact. Fine close-range gravel/shadow aliasing is recorded as a visual follow-up. Old development-HMR page errors remain historical session evidence; fresh-page logging and pair-one street connections are still being checked.


## Pair-one checkpoint and pair-two activation

Pair one passed ordinary placement, movement, rotation, Undo/Redo, save/reopen,
overlap rejection and native aerial/Walk/exact capture checks. The Sculpture
floor fix passed its second browser recheck. Both saved entrance connections
survive reopening: Sculpture 2.2 m wide across a 7.23 m sidewalk-centre gap;
Orchard 1.8 m across 4.27 m after an ordinary move closer to the street. The
Orchard path is clearly continuous from Walk; Sculpture is visible from above
but partly obscured by Market stalls at walking height. This visibility limit
and fine native gravel shadow aliasing remain recorded. Original asset bytes
are unchanged. Evidence: external pair1-runtime-results.json and
pair1-access-probe.json. Protected Basketball/Botanical smoke checks passed.

Performance Lawn and Timber & Stone Square are now enabled for bounded local
pair-two review. Only activation status changed; immutable content and asset
identities did not. Wetland and Teaching remain withheld. The transition passed
23 focused frontend tests, 24 backend native tests, TypeScript checking and all
11 staged asset checks. Three paid requests have succeeded; the final two remain
unsubmitted. No push or publication.

Pair two passed bounded student-control checks: original placement, rotation,
movement, Undo/Redo, reopening, and refusal of a 240 × 240 m parcel without
disturbing the four saved parks. Exact native captures show Performance's
curving path, stage and rising tiers grounded, and Square's paving, benches,
lamps, planting and trees intact. Numeric stair/gate dimensions are actual-asset
and test evidence, not browser measurements. An overlap click found adjacent
free space; the extra disposable Square was removed through normal controls.
External street connections for this pair remain NOT TESTED until the final
mixed-scene check. Evidence: pair2-runtime-results.json. Paid total remains three.
