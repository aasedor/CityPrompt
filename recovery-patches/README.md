# City Prompt recovered development series

This directory preserves the verified local development history from the
recovered workspace base through the completed parcel-landscape, Direct 3D,
and AI LEGO-only community-planning work.

- Local implementation branch: `codex/ai-lego-only-planner`
- Verified local tip: `05b7f036fb72d59b575eb5577cfe0bfd8ba397db`
- Recovered shallow base: `3cbfcdaa90a02fea7220d185b1230b09923f2168`
- Patch files: `1` through `34`, in application order
- Empty-lot and Direct 3D feature patch: `32`
- Initial LEGO archetype handoff fix: `33`
- AI LEGO-only planner and completed handoff patch: `34`
- Patch 34 SHA-256: `F025F4CA525E7176F4FB3DEE8087DF938F83D3F031CF60B44E263B35F10B6A56`

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

## Patch 34 outcome

- AI Master Planner buildings are selected only from the runtime LEGO catalog,
  with project-owner/private inventory, exact dimensions, floor compatibility,
  and catalog fingerprints enforced before persistence and placement.
- AI parks and streets carry explicit renderable archetype identities. Meshy
  and generic planned-massing fallbacks are excluded from current AI plans.
- Site-boundary area not claimed by an authored physical polygon is compiled as
  deterministic residual landscape without changing the parcel source.
- Direct 3D is conditioned only by authoritative persisted proposal zones and
  compiled Building snapshots. Classic colored-polygon rendering remains on
  its established source and pipeline.
- Industrial Brick Mixed Use selection now hands the current unsaved draft to
  LEGO Builder, clears stale variants when Automatic is chosen, and reports
  missing versus incompatible families separately.

## Patch 34 verification

- Backend focused matrix: 285 passed; Ruff passed
- Frontend focused matrix: 15 files / 125 passed
- TypeScript type check and production build: passed
- Common pilot: 5 LEGO buildings, 2 parks, 7 streets, 5,570 m² residual
  landscape, 4 deterministic trees, zero Meshy references and zero generic
  planned-massing records
- Stress pilot: 46 LEGO buildings, 6 parks, 13 streets, 7,288 m² residual
  landscape, and 65 of 65 physical fingerprints current after rebuild
- Browser QA passed at 30-degree oblique, steep, and overhead camera angles,
  plus model off/on, reload, overlay, LEGO Builder, Direct 3D, and Classic
  pipeline isolation checks
- Close Direct photoreal QA retained 92.3% registration, 99.8% building edges,
  98.6% semantic edges, and zero exterior-pixel delta
