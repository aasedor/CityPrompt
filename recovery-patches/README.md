# City Prompt recovered development series

This directory preserves the verified local development history from the
recovered workspace base through the completed parcel-landscape and Direct 3D
render work.

- Local branch: `codex/empty-lot-community`
- Verified local tip: `767d12351a2ec517ac2bd9ee2f2c4ff8bd0c1c2d`
- Recovered shallow base: `3cbfcdaa90a02fea7220d185b1230b09923f2168`
- Patch files: `1` through `33`, in application order
- Final feature patch: `32`
- Follow-up LEGO archetype handoff fix: `33`

The recovered base commit and several of its promised objects are no longer
retained by the GitHub remote. A normal branch push therefore attempted to
re-send the 6.18 GiB recovered snapshot and was rejected by GitHub. These
binary-safe `git format-patch --binary --full-index` files preserve every local
commit after that base without uploading unrelated recovered assets.

Apply only to a checkout that already contains the recovered base or an
equivalent recovered workspace:

```bash
git am --3way 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32
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
