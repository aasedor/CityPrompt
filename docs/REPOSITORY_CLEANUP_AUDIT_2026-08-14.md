# Repository cleanup audit — 2026-08-14

## Outcome

The latest pilot/fix line is fast-forwarded onto local `main`. The repository
now has enforceable frontend, backend, dependency, dead-code, bundle, and asset
gates. High-confidence obsolete files and unreachable frontend subsystems were
removed without changing the verified runtime workflow.

This is a release candidate, not yet a student release. The remaining release
blockers are listed below.

## Removed with high confidence

- broken `2D Maps` nested-repository metadata;
- root-level reference/PPTX clutter and tracked smoke/video output;
- forbidden legacy `parks_plazas` and `streets_pathways` public trees;
- Storybook (two stories, no runtime/CI consumer, and the source of all npm
  audit findings);
- superseded local Google 3D Tiles and globe drawing prototypes;
- unused massing, viewpoint, procedural-style, entourage, guide, card, and
  metadata-schema modules;
- two one-off catalogue mutation scripts that described an obsolete
  45-archetype catalogue;
- the unmaintained standalone-viewer visual-regression suite, which targeted a
  route that no longer exists and had no committed screenshot baselines;
- unused npm dependencies, while adding the two dependencies that were used
  but undeclared (`@playwright/test` and `three-stdlib`).

Knip now passes for unreachable files, unused dependencies, and undeclared
dependencies, and that check is mandatory in CI. `public/sw.js` is an explicit
entry because it is registered by URL in production rather than imported.

## Runtime assets

`frontend/src/data/runtimeAssetManifest.json` is generated from the reachable
application graph, catalogue availability, and dynamic LEGO/park collections.
At this checkpoint it proves:

- 1,437 direct public-asset references;
- 3,261 required deployable files;
- approximately 8.98 GiB of required logical asset content;
- zero missing references among items advertised as usable;
- 15,247 unclassified files that are candidates for artifact migration; and
- two family directories absent from runtime family signatures.

The unclassified set is not automatically safe to delete. It contains compiler
source textures, review renders, validation evidence, and comparison output.
Many compiler tests still inspect those paths. Move that evidence to versioned
object/artifact storage and update the compiler test fixtures before deleting
it from Git.

The current checkout still contains 2,532 required Git LFS pointer files rather
than hydrated objects. CI now uses `actions/checkout` with LFS and rejects an
unhydrated runtime build. A release clone must run `git lfs pull` before the
student workflow is tested.

## Catalogue classification

The generated availability data distinguishes complete, partial, and
unavailable entries. Pickers expose only references that exist; missing
variants no longer appear as broken cards.

| Domain | Usable | Complete | Partial | Unavailable |
| --- | ---: | ---: | ---: | ---: |
| Buildings | 79 | 32 | 47 | 145 |
| Open spaces | 130 | 130 | 0 | 0 |
| Streets | 115 | 11 | 104 | 0 |
| LEGO family signatures | 134 | 134 | — | 30 |

Adding an authored reference asset and regenerating the availability/asset
manifests promotes that entry automatically. This keeps asset creation as an
incremental content workflow rather than a source-code edit.

## Verification completed

- ESLint 9 flat configuration: zero warnings/errors;
- TypeScript: passes;
- Vitest: 105 files, 1,054 tests pass;
- backend pytest: 1,063 tests pass;
- Ruff and Black: pass across the backend;
- mypy: mandatory for the clean core/model/schema boundary;
- production build and bundle budget: pass;
- npm audit: zero vulnerabilities;
- archetype, Sticker Method, runtime-manifest, and dead-code checks: pass;
- Playwright: 13 current auth, project, and integrated 3D-workspace tests pass;
- browser checks reject uncaught page exceptions, unexpected HTTP failures,
  and console errors; and
- a cold browser run starts its own Vite server and passes in approximately 16
  seconds on this checkout; and
- a depth-one clean checkout passes `npm ci` with zero vulnerabilities, all 13
  browser tests, the production build, bundle budget, and the unhydrated
  runtime-manifest check.

The clean-checkout exercise also fixed a Windows-only false negative: the
runtime-manifest checker now normalizes CRLF/LF before comparing deterministic
JSON. The shared long-lived local Git database is approximately 9.93 GiB, so a
full local-history clone is not representative of a new student clone and is
too expensive on the current drive.

The compiler suite was also run in the current checkout. It reported 547
passes, 86 failures, and 55 setup errors. The failures are not a deletion
signal: exact-reference inputs such as
`civic_modernism_rec_centre/variant_0.png` are Git LFS pointer text rather than
hydrated image bytes. The checkout remained clean after the run.

## Remote branch audit

After fetching `cityprompt`, 24 named pilot/wave branches have zero commits
outside local `main`. Eight branches still have unique commits and must be
reviewed before retirement:

| Branch | Unique commits |
| --- | ---: |
| `codex/direct3d-inventory-fidelity` | 43 |
| `codex/direct3d-object-seed` | 21 |
| `codex/fixed-glb-meshy-blender-pilot` | 2 |
| `codex/park-lego-variant-closure` | 23 |
| `codex/park-meshy-object-pilot-v1` | 33 |
| `codex/sticker-method-batch-01` | 2 |
| `codex/sticker-method-street-pilot` | 1 |
| `feat/clean-3d-style-renders` | 2 |

Do not delete even the fully merged branches until this local integration is
pushed to `cityprompt/main`; the canonical remote branch still trails the
release candidate.

GitHub CLI verification confirms that `aasedor/CityPrompt` is private, `main`
is its default branch, and the current account has administrator access. The
remote `main` branch is not protected yet. Locally, `main` tracks
`cityprompt/main` and `remote.pushDefault` is set to `cityprompt`, so an
unqualified future push cannot accidentally target the historical `origin`
remote.

## Remaining release blockers

1. Hydrate the required LFS objects and prove the manifest against real bytes.
   Free capacity on the current drive fluctuated between approximately 5.3
   and 14.1 GiB during verification, while the required runtime set is 8.98
   GiB before clone, dependency, build, and Docker overhead. Hydration is not
   safe here without first freeing substantial space.
2. Move the 15,247 compiler/review candidates to external artifact storage;
   8.98 GiB of runtime content is also too heavy for a normal student clone and
   should ultimately be served from object storage/CDN.
3. Re-run the compiler test suite after LFS hydration and the artifact-storage
   boundary are complete; the unhydrated run is 547 passed, 86 failed, and 55
   errors.
4. Run the complete real-account student workflow against a fresh Docker clone
   with hydrated LFS assets and documented test credentials. The controlled
   browser suite now passes, but it intentionally mocks API responses.
5. Expand mypy beyond core/models/schemas; the legacy API/rendering backlog is
   not part of the current mandatory boundary.
6. Rotate the historical Cloudflare credentials already removed from the
   current tree; Git history still contains them.
7. Enable GitHub branch protection for the now-mandatory CI jobs.
8. Audit and retire merged remote pilot branches, then tag the release only
   after the fresh-clone workflow passes.
