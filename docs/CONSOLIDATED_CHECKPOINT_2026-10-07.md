# Consolidated City Prompt checkpoint - October 7, 2026

This checkpoint brings the completed recent work into the existing review branch `codex/catalogue-runtime-preparation-2026-10-06` on `aasedor/CityPrompt`. It is a backup and review checkpoint, not a production release or Render deployment.

## Included

- Calgary existing and proposed zoning, drawing and opacity, assessment context, permitted/discretionary catalogue screening, all approved LAP Urban Form overlays, and MDP/CTP policy maps.
- The integrated affordable-housing and zoning-coverage batches, five community building trials, sandy beach, five narrow pathways, continuous walking and simplified Walk controls.
- Saved-render Kling animation, local image-engine choices and higher-quality local Qwen settings.
- The four new UBST RLASM architectural-clay candidates, their locked references, generation source, GLBs, comparison boards and independent reviews. [Open their gallery](showcase/ubst-rlasm-2026-10-07/README.md). They are not activated or final textured models.
- The outstanding local startup guard and candidate-revision audit fixes, copied from the working preview without changing that checkout.
- Five exact existing runtime assets formerly available only in a local packet. [Supplement and hashes](../seed/validation/supplemental-2026-10-07/README.md).

The affordable-housing worktree's remaining lawn correction and the planning worktree's zoning reassessment documents were compared with this branch and were already included.

## Verification in this consolidation pass

| Check | Result |
|---|---|
| Catalogue delivery and local-runtime guard tests | 16 passed |
| Frontend TypeScript check | Passed |
| Full frontend Vitest run | 342 suites passed; 15 failed. 2,912 tests passed; 39 failed; one suite failed during collection |
| Kling, saved-render animation, recovery and local-image backend tests | 16 passed; 24 PostgreSQL-dependent integration tests skipped because no isolated test database URL was configured |
| UBST reference-lock tests | 4 passed |
| Exact local catalogue asset audit | 133 choices; 404 dependencies; zero failures after restoring pinned assets |
| New review archive | 49 selected deliverables match recorded byte counts and SHA-256 hashes |
| Browser smoke check | Consolidated preview on port 5183 opened; both landing images loaded; no warning/error console entries observed |

The browser session was signed out, so this pass does not claim a fresh authenticated map, placement or render-generation trial. Ports 5174 and 5181 were already occupied and left untouched. No paid generations were submitted.

The full-suite failures include historical catalogue IDs/counts, street reference expectations, park placement/revision expectations, prepared public roads and junction expectations. They remain visible follow-up work; the full suite is not green. A broad LFS-pointer consistency check also reports legacy binary files committed directly before their paths acquired LFS attributes; no history migration was attempted.

## Local setup and recovery

Keep keys, databases and private environment files outside Git. The new optional ignored `artifacts/local-runtime.json` uses schema `cityprompt.local-runtime@1`, absolute `envDir` and `cataloguePacket` paths, optional `publicDir`, `apiProxyTarget` and `port`. It groups the environment and exact asset packet; direct Vite startup checks Maps configuration and all catalogue dependencies before serving.

The verified packet on this machine is `C:/dev-artifacts/CityPrompt/consolidated-2026-10-07/catalogue`. It includes a source-hash receipt for this catalogue. Regenerate a packet when catalogue inputs change; do not edit its receipt to bypass a mismatch. To run the audit directly, set `CITYPROMPT_CATALOGUE_PACKET` to that path before `node frontend/scripts/check-catalogue-delivery.mjs`.

For another machine, hydrate the tracked Git LFS assets, unpack the original [validation bundle](CLAUDE_VALIDATION_SETUP.md), restore the supplemental files at their manifest URLs, and stage the current native park/street and model-library seeds. The older validation setup document describes its baseline; it is not evidence of a fresh deployment of this consolidated version. Run the catalogue audit before serving. Backend credentials, migrations, model-library storage and project database setup remain separate deployment prerequisites.

## Preserved separately

Uncommitted experiments in the primary checkout and older place/student-design worktrees remain untouched and are not part of this checkpoint. The earlier four-family and ten-family expansion reviews have not been newly activated or published. Heavy Blender files, all raw render iterations, private project databases and environment credentials remain local. Only explicitly selected reviewed deliverables were added, using Git LFS for model/image binaries.
