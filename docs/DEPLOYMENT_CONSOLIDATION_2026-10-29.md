# Deployment-version source consolidation — 29 October 2026

The LuxModus handoff target is `aasedor/CityPrompt` `deployment-version`, as selected by the user. This integration preserves both completed histories from their common deployment baseline; it does not deploy a service or grant catalogue activation approval.

## Source coverage

| Source | Exact checkpoint | Coverage |
| --- | --- | --- |
| Deployment baseline | `62e31ad621238c6ce1da62934710128831df3b5e` | Existing deployment lineage |
| Student application | `62ab3982ca21c575263c905b51b958ea50b5a24e` | 78 commits: simplified UI/imported GLBs, tower storeys, drawn ground surfaces, quantitative reports, teaching filters, context/policy maps, snapping/intersections and rendering workflow changes |
| Catalogue/runtime | `3c02448f23a5637d119e1a624dab3e02f3c0ac2c` | 8 commits: building-only geometry, snug footprints, photographic heroes, additional buildings and corrected crossings |

The running local export was compared across 1,434 source files. Its 1,431 equivalent files are represented by the student checkpoint. The three differences were six photographic hero overrides already in the catalogue checkpoint, and two test files whose newer committed regression tests are retained. Unrelated experiments and dirty files in the original worktrees are preserved outside this integration.

Independent review confirmed retention of every catalogue-exclusive path and every student-exclusive path except the intentionally composed fixed-footprint predicate. Both authored-program and native fixed-footprint semantics are retained. Review regressions in deferred resource cleanup and landscape texture centring were fixed with reproducing tests.

Twelve exact, hash-named local trial model/image assets previously existed only in an external public folder. They are now explicitly tracked through LFS under `frontend/public/validation-assets/claude-local/` (20,754,327 payload bytes). Existing model geometry bytes and activation flags are preserved.

## Verification

- Complete frontend run: **4,183 passed, 25 skipped**, across 488 passing and two skipped test files.
- Focused integration run: 159 tests passed. Related backend run: 224 passed; regenerated model-contract follow-up: 106 passed.
- TypeScript, strict ESLint and dead-code checks passed. Full npm audit reported zero advisories at the time of the check.
- Four deployment workflow regression tests, five archive-materialization safety tests and 41 lossless catalogue-packing tests passed.
- Runtime manifest check passed with 5,470 required records. Exact production asset preparation passed for 186 choices, 585 dependencies and 3,730 files / 1,672,384,441 payload bytes.
- The backend model contract now includes the exact new hospital, fire station and student residence identities, without removing or changing the existing 106 records.
- CI includes `deployment-version` and restores pinned archive outputs independently in frontend and browser checkouts. Additional static registries use the existing lossless build codec; performance limits are unchanged.
- Local browser trial: account/project creation, boundary save, 214-choice picker, hospital placement/15-degree rotation, saved building reload, 13-to-25-storey tower edit and quantitative report request succeeded. The tower trial required installing the existing exact private modules for the disposable QA owner. Those modules are a local pilot, not production activation. Report counts matched the two saved buildings; unmeasured floor areas and units remained explicitly unknown.

The combined local catalogue has **214 choices: 112 buildings, 43 parks and 59 streets**. This is a local validation roster, not a statement that all choices are activated in production.

## Open release gates

Seven building entries remain local-only pilots: the Crucible, Overhang and Reef climbing centres, sandstone clock-tower block, modern fire station, regional teaching hospital and student residence tower. `tools.catalogue_promotion check --metadata-only` deliberately rejects these entries until genuine successful trial evidence and human activation approval are recorded. Do not clear their flags or weaken this check to merge the source consolidation.

The fresh hosted build compiles successfully but its performance gate still fails: **8,604.1 KiB total JavaScript versus the 8,448 KiB limit**. The lossless metadata packing reduced the initial combined build from 8,969 KiB. This remaining gate is visible and has not been raised or bypassed. This checkpoint is a review candidate until all required gates pass.

Hosted CI, remote exact LFS availability and final browser/build receipts must be read before approving the handoff. Previously confirmed authentication, session/recovery, throttling and upload-processing security findings remain open in the private review material. This consolidation is not a security certification or public-release clearance.

Local verification logs, inventories, browser evidence and asset receipts are retained externally in `C:/dev-artifacts/CityPrompt/deployment-consolidation-20261029`. Private credentials and detailed security probes are excluded from Git.
