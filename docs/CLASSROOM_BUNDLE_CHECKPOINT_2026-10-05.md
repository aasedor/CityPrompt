# Classroom bundle checkpoint — 2026-10-05

Initiative: `codex/classroom-bundle-performance-2026-10-05`, following the site
reference-map checkpoint. No catalogue entries, prompts, variants, image paths,
3D models or publication decisions were changed.

The production build packs the three archetype JSON modules and the native
park/street registries losslessly using
zlib. The browser restores their original objects once using the inflater
already distributed with Three.js. Development retains readable source data.
This avoids compiling megabytes of catalogue text into JavaScript literals.

| Measure | Baseline | Packed build |
| --- | ---: | ---: |
| Total JavaScript | 10,845.9 KiB | 8,032 KiB |
| Catalogue chunk | 3,366 KiB | 1,179.9 KiB |
| Initial app shell | 455.2 KiB | 455.2 KiB |
| All JS compressed with zlib level 9 | 2,722.2 KiB | 2,734 KiB |

These builds include the real map configuration. A keyless build omits map
code and is unsuitable for this comparison.

The compressed transfer is essentially unchanged (0.43% larger in this local
comparison). This is a reduction in JavaScript source/parse volume, not evidence
of a smaller compressed network download or a measured classroom speedup.
Node import/decode plus comparison took roughly 90–110 ms for buildings and
23–26 ms for each other archetype catalogue and 14–19 ms for each native registry.
Basic student devices still need testing.

## Verification

- Six build-plugin tests execute the actual browser decoder and deeply compare
  every source field. They pass; no reference paths or Unicode are altered.
- TypeScript checking, production build and all bundle-budget checks pass.
- 21 tests in the additional catalogue/resolver suites passed. Nine assertions
  in the old aesthetic/canonical catalogue suites fail identically with the
  original Vite configuration: they expect retired availability/asset identities.
  The packing plugin runs only during production builds, not those Vitest runs.
  These existing assertions were preserved and were not weakened to pass.
- The production browser opened the saved trial project and displayed its
  catalogue, with 95 exact choices (34 buildings, 30 parks, 31 streets).
  Google 3D tiles loaded and their observed responses were HTTP 200. The captured
  browser warning/error log was empty. Temporary development-only fixture
  additions remain separate. Screenshot: `packed-production-catalogue.jpg` in
  the external output directory.

The build and baseline comparison outputs, launch logs and screenshots belong
under `C:/dev-artifacts/CityPrompt/overnight-2026-10-04`, or the ignored frontend
`dist/` directory. No generated assets are committed. No hosting trial,
deployment, paid generation, push or catalogue promotion occurred.

Remaining performance work: actual project-load/frame measurements on basic
Windows laptops and iPads, asset-transfer and LOD review, server concurrency,
shared multi-worker caching and a 40-user hosted classroom rehearsal.
