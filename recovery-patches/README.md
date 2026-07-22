# City Prompt recovered development series

This directory preserves the verified local development history from the
recovered workspace base through the completed parcel-landscape and Direct 3D
render work.

- Local branch: `codex/public-realm-render-quality-v2`
- Verified local tip: `e4d4e3c4ad9d4cfbbccf029a3f71112071b80c8e`
- Recovered shallow base: `3cbfcdaa90a02fea7220d185b1230b09923f2168`
- Patch files: `1` through `34`, in application order
- Final feature patch: `32`
- Follow-up LEGO archetype handoff fix: `33`
- Terrain-contact, dark-LOD and public-realm detail upgrade: `34`

The recovered base commit and several of its promised objects are no longer
retained by the GitHub remote. A normal branch push therefore attempted to
re-send the 6.18 GiB recovered snapshot and was rejected by GitHub. These
binary-safe `git format-patch --binary --full-index` files preserve every local
commit after that base without uploading unrelated recovered assets.

Apply only to a checkout that already contains the recovered base or an
equivalent recovered workspace:

```bash
git am --3way 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34
```

## Final feature outcome

- Site-boundary remainder is compiled as deterministic residual lawn,
  groundcover, boulevard/foundation/perimeter planting and cleared trees.
- The established Classic colored-polygon renderer remains isolated.
- Direct 3D captures beauty, proposal mask and semantic class passes, makes one
  masked GPT Image 2 call, then applies a source-anchored finish that discards
  provider geometry and restores exterior pixels byte-for-byte.
- Paid preflight is bound to exact zone source/representation hashes, building
  revisions and the current residual-landscape hash under a project row lock.

## Verification at the preserved tip

- Relevant backend suite: 147 passed
- Entire frontend suite: 55 files / 445 passed
- TypeScript type check: passed
- Production build: passed
- Ruff and Python bytecode compilation: passed
- Browser QA: 30-degree oblique, 65-degree steep and 90-degree overhead; all
  four models, park, street and residual landscape remained mounted
- Clean browser reload: zero warnings/errors and Direct 3D immediately ready
- Final paid pilot: exterior delta 0, geometry lock applied, provider geometry
  discarded, building-edge retention 98.9%, semantic-edge retention 93.5%
- Total paid QA: 136 SiteForge tokens / $0.68; no automatic retries

The paid pilot is saved as project render 8 in project
`1c46efd3-03df-4a70-b977-35631c755e46`.

## Patch 33 verification

- Industrial Brick Mixed Use at 30 x 20 m and 6 floors selected the
  `industrial-brick-original-mill-v1-renderlocked` family in live browser QA.
- Frontend focused suite: 43 passed
- Backend LEGO suite: 46 passed
- TypeScript type check and production build: passed
- Ruff and Git diff checks: passed

## Patch 34 outcome and verification

- Street, intersection, roundabout, park-prop and specialty-structure contact
  now uses bounded multi-probe terrain planes with outlier rejection and
  deterministic fallbacks.
- Prepared ground overlaps the Google Tiles mask edge to suppress white
  contact seams, and public-realm surface/curb/marking datums are centralized.
- Legacy LEGO ambient-occlusion failure is disabled only on the LEGO assembly
  path; base colour is treated as sRGB and facade LOD pairing now fails safe
  per joined mesh and facade role.
- Street families add drains, sidewalk joints, bins, racks, bollards, tree
  grates, planting cells and warranted signal assemblies. Park families add
  bounded, collision-aware furnishings and planting/stone clumps, including
  functional greenway and stormwater assemblies.
- Frontend: 66 files / 612 tests passed; TypeScript type check and production
  build passed (3,379 modules transformed).
- Compiler quality-memory suite: 6 passed; `git diff --check` passed.
- Live City Prompt QA passed on compact, full-site and 30-building stress
  projects at 30-degree oblique, 58/72-degree steep and 86-degree overhead.
  Far-LOD zoom and model off/on recovery produced no black facade failures,
  browser warnings/errors or WebGL context loss.
