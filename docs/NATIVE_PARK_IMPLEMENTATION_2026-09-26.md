# Original eight native parks and Basketball Long

Worktree: `C:/dev/CityPrompt-approved-validation`.
Branch: `codex/custom-render-prompts`.
Starting commit: `014300ecc3f41eed93bb7fe0c098363243f8add5`.
Current runtime checkpoint: `0f2ccd6aa`.

## Current acceptance

All eight native parks and Basketball Long are enabled for local verification.
The pilot and each bounded pair passed applicable placement, editing, save/reopen,
aerial, Walk and exact-source checks in disposable projects. The user approved
the pilot views and authorized rollout after its application checks passed.
Subsequent agent reviews are recorded separately from human approval.

All eight native parks have also been placed and reopened together in a fresh
local production session. All eight now resolve valid street approaches and the
mixed-scene exact PNG export passed. Five single-image Sunburst comparisons
succeeded. Botanical's external approach passed visual review. Basketball Long
movement, rotation, Undo/Redo and reopening preserved its two courts, original
position and orientation. Nothing is pushed or published.

The exact-variant ledger is `docs/native_park_acceptance_2026-09-26.json`.
It separates asset verification, visual approval, runtime evidence and publication.

| Layout | Native dimensions | Entry |
| --- | --- | --- |
| Botanical v013 | 48 × 62 m | South, 2.4 m |
| Museum Sculpture Court | 30 × 44 m | South, 2.4 m |
| Neighbourhood Orchard | 36 × 30 m | South, 1.8 m |
| Terraced Performance Lawn | 64 × 64 m | West stairs, 2.4 m |
| Timber & Stone Square | 32 × 28 m | South, 2.4 m |
| Wetland Boardwalk | 64 × 64 m | South timber, 2 m |
| Teaching Demonstration Garden | 42 × 50 m | South, 2.2 m |
| Native Basketball | 52 × 39 m | South, 2.4 m |
| Basketball Long | 92 × 39 m | South, 2.4 m |

## Runtime contract and preservation

The supplied handoff and original asset archive remain unchanged. The archive
SHA-256 is `76e640f93b54228a479e39cd6113ee5556519e795920395ee0151be61dd99731`.
The shared frontend/backend nativeParks registry has immutable content revisions,
source/recipe hashes, metric bounds, entrance metadata and ground ownership.
Its current SHA-256 is
`a11a6d3e8d99f01eb0fc8e6dc8ac2a86362d731be87f4b3b741aa6bee994765f`.

Schema-v2 recipes are server-resolved under `public_realm_lego`. Unknown revisions
and untrusted assets are rejected. Schema-v1 and legacy instance bindings remain;
upgrading a legacy park requires an explicit preview. Rigid models retain their
size and selected layout when parcels change. Preview / Apply / Cancel uses an
atomic undoable save; failed fit/save preserves the prior park. Fitting checks
actual polygons, holes, obstacles and approach reservations. New acceptance is
limited to prepared level ground; unsupported terrain receives a recoverable error.

Botanical's original geometry remains 48 × 62 m. Its projecting details require
a 48.2 × 62.2 m placement reserve; no original assembly is scaled or cropped.
Basketball Long uses two complete 36 × 23 m modules centered at x=-20/+20 m,
with a 4 m separation, connected paths and source benches/planting. Its measured
full bounds fit the proposed parcel. The original one-court composition remains.

Native assets are SHA-verified with embedded dependency closure before mounting.
Capture checks expected current instances against mounted revisions before and
after capture, so an absent park cannot pass as a complete scene. Automatic
updates include layout, frame and content identity, coalesce rapid edits and
reject stale asset-error callbacks. Custom prompts and prior render images remain.

Native entrances share the existing access solver. Actual paving/timber probes
trim connectors at the authored surface, retaining missing approaches rather than
covering source paths. The same actual surfaces support the walking camera.
Performance stair samples measured 0.1333, 0.4, 0.6667 and 1.2 m; Wetland timber
measured 0.22 m. These numerical results are asset probes, not browser measurements.

Sculpture's coplanar source paving/soil needed a cloned-material depth bias in
the logarithmic-depth renderer. Original mesh/material bytes are untouched.
The second browser recheck passed; fine authored gravel/shadow aliasing remains a
follow-up. Walk entry from overhead now faces displayed map-up rather than an
unstable horizontal projection of the camera direction.

## Verification and remaining limits

- Final focused checkpoint: 97 frontend tests in 13 files and 44 backend tests
  passed. TypeScript checking and the local production build passed on this
  runtime. Earlier focused render/landscape/community suites are retained in
  the external evidence. Automated results do not substitute for visual checks.
- Eleven native asset files pass reproducible staging and actual HTTP hash checks.
  Run `python scripts/stage_native_parks.py` to verify, or add `--public-dir`
  with an explicit local public directory to stage missing files. Conflicts reject.
- Pair1 approaches survived reopening: Sculpture 2.2 m wide across a 7.23 m
  sidewalk-centre gap; Orchard 1.8 m across 4.27 m after an ordinary move.
  Sculpture's approach is partly obscured by Market stalls in the Walk view.
- Mixed-scene saved geometry resolves all eight street approaches. Square,
  Wetland and Teaching low-view connections passed agent review. Performance's
  west approach became valid after extending the street endpoint north through
  ordinary controls: 2.2 m wide across a 5.18 m sidewalk-centre gap. Its stair foot
  is grounded in the low view, with part of the short connector obscured by a
  Market stall. The earlier diagonal end-cap rejection is
  retained for investigation in the separate street initiative.
  Wetland held-forward movement onto timber is not yet browser-verified; a brief
  CLI keypress did not establish it. The separate height probe passed.
- A historical 166 m Market drawing attempt did not finish; cause unconfirmed.
  A later 86 m pilot and 168 m pair1 street saved through ordinary controls.
- Historical development HMR errors are retained rather than erased. Fresh
  production page errors were empty at initial reopen. The bounded production
  bundle initially omitted its logo and three decorative foliage textures;
  original bytes were staged and HTTP-verified before final reload and capture.
  The fresh production checks passed with historical console events retained;
  a completely cleared isolated console log was not captured.

All five authorized single-image Sunburst submissions succeeded: Basketball
native aerial, Basketball Long street, Botanical walking height, mixed-eight
aerial and Teaching street after movement/reopening. Same-camera sources and
outputs are hash-locked in `paid-render-ledger.json`; all twelve retained PNG
files passed byte verification in `paid-file-verification.json`. Broad layouts
were preserved; tiny or occluded component counts and plant-by-plant fidelity
are not asserted. Five requests consumed 470 local credits (2498 to 2028).
The budget is closed: no retries, batches, alternate engine or further paid calls.

Evidence: `C:/dev-artifacts/CityPrompt/native-parks-2026-09-26/`.
Primary records: `runtime-results.json`, `pair1-runtime-results.json`,
`pair2-runtime-results.json`, `pair3-runtime-results.json`,
`actual-native-surface-probe.json`, `final-focused-checks.json`,
`production-http-checkpoint.json` and the paid ledger. The external
`stage-production-context.py` verifies/stages 45 locked context files separately
from the 11 native GLBs. Heavy source captures, models and screenshots stay outside
Git. Only source, tests, metadata and concise acceptance records are committed.

Final reports: `mixed-runtime-results.json`, `production-browser-results.json`
and `basketball-final-edit-results.json`. Registry acceptance metadata now records
bounded prepared-level results; all immutable content revisions remain unchanged.
The tested production build contains the same runtime and asset content. The
acceptance ledger records both tested and current registry hashes. Wetland held
walking and the other stated limitations remain open; this is not a claim of
unrestricted classroom release.
