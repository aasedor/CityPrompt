# Local version readiness — 28 October 2026

Initiative: `codex/luxmodus-readiness-20261028`, based on `b0ab52f2d`.
Scope: the current local application and portable production build. GitHub
permissions, main, production deployment, catalogue approval and paid generation
were not changed. The local development history is ahead of `origin/main`;
this report must not be read as evidence that GitHub main already contains it.

## Changes

- Focus building now approaches a single small building instead of applying
  the 70 m whole-site camera floor. The complete roof remains part of the fit;
  whole-site framing retains its existing margin. A regression test failed at
  70 m before the correction and passes with the closer frame.
- Corrected frontend lint findings, including hook dependencies and test
  syntax. Exact dimension literals retain the same IEEE double values and
  pass the unchanged backend model contract check.
- Removed the unused four-step workflow component and obsolete detail-model
  component. Knip now recognizes actual HTML review/fixture entry points.
- Declared the directly imported esbuild test dependency and applied compatible
  lockfile patches, including Vite 6.4.5 and Vitest 4.1.12. No framework major
  upgrade was made. The final npm audit reports zero advisories.
- Made backend pytest's repository-root script imports explicit. Isolated
  production-settings tests from developer dotenv files and supplied current
  project-details query results in render-provenance test fixtures. Production
  validation, freshness checks and spending controls were not weakened.
- Split the aggregate all-streets UI test into individual selection cases.
  Its former 60-second aggregate timed out during concurrent build/browser QA
  and took 58.14 seconds even in isolation. All 53 street selections retain
  their placement and dialog assertions; timeout limits were not increased.

## Verification

Evidence directory: `C:/dev-artifacts/CityPrompt/luxmodus-readiness-20261028`.

| Check | Result |
| --- | --- |
| Backend full suite | 2,572 passed; 70 skipped; existing warnings recorded |
| Frontend full suite on final patched dependencies | 3,950 passed across 467 files; zero failed/skipped |
| TypeScript and ESLint, zero warnings allowed | Passed |
| Knip files/dependencies audit | Passed |
| Catalogue delivery script tests | 26 passed |
| Full catalogue/asset packet audit | 186 choices; 578 distinct dependencies; zero failures |
| Portable asset packet | 3,723 verified files; 1,667,410,799 bytes |
| Production build on patched dependencies | Passed, external `production-dist-patched` directory |
| Bundle budgets | Passed: app shell ~475.5 KiB; total JS ~7,670 KiB |
| npm audit | Zero advisories |
| API readiness | Database, Redis, storage, image and reference workers ready |
| Independent review | No important/critical regressions; minor findings corrected |

Review follow-up: the independent street cases do not repeat all 53 selections
on one mounted palette, as the previous aggregate loop did. Individual choice
and dialog-close coverage is retained; broader same-session catalogue cycling
remains a minor test follow-up rather than a claimed automated acceptance.

Binary fixtures and render-example/policy-map files were restored from the
existing local LFS cache and verified, without generating replacements.
The production build used the authoritative portable assets from
`scripts/hosted_assets.py`, rather than assuming the development runtime's
external public directory exists on another machine. A plain source checkout
without hydrated asset delivery correctly fails its build guards. For a hosted
handoff, use `scripts/build_hosted_frontend.py` with explicit hosting settings
and a fresh/revalidated asset packet; do not copy local environment files.

## Fresh browser checks

QA project: `246003b1-5062-421d-9ceb-d8133b2ec548`.
External GLB project: `79150c2b-1479-43f0-a9e1-3d28e5d801f4`.

- Existing detailed external GLBs loaded after reopening; the selected house
  now fills a useful close view without foreground tiles obscuring it.
- Brick Podium tower changed from 13 to 25 and 40 storeys, retained detailed
  geometry and the same 57 x 47 m plot, and preserved 40 storeys after reload.
  The QA tower was then restored to 13 storeys.
- Site Context / Policy organization opened correctly. Street labels loaded;
  public water mains loaded 93 records and displayed blue spatial lines. Both
  test toggles were restored to off.
- Drew and moved camera-route points, completed the route and rendered a free
  preview. The MP4 played to completion; browser metadata and ffprobe confirm
  4 seconds, 96 frames, 24 fps, 1280 x 720, H.264.
- Delete route removed the route and preview and disabled generation until a
  new route is drawn. Photographic finish was enabled by default.
- The first preview attempt was interrupted by a test-file edit triggering
  Vite's development reload. It was rerun successfully with source held steady.
  The browser download event timed out, but the normal Downloads output was
  found, verified and delivered; no export gate was bypassed.

## Limits and delivery

Paid AI images, Omni provider output and the native GLB file chooser were not
rerun in this pass. This does not certify every optional tool, production
deployment, Docker image or CI job. Local-only catalogue trials retain their
existing approval status. Imported third-party model appearance remains source
dependent; the generic properties panel still exposes generation controls for
imports and merits a later usability pass.

Seven labelled browser screenshots and the original free source-preview MP4
are delivered privately at:
https://drive.google.com/drive/folders/1kZxMu8I07L8UomPjj1Mvu9lGlL6IeDu0

The local delivery manifest records Drive IDs, hashes, sizes and readback.
No paid render jobs or additional credits were used.
