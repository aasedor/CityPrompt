# Deployment branch consolidation implementation plan

> For agentic workers: execute with superpowers:executing-plans. Preserve both source histories and verify the combined release before promotion.

**Goal:** Capture the completed City Prompt UI, runtime, catalogue and image changes in the user-selected `deployment-version` lineage for the LuxModus handoff.

**Spec:** The user's 29 October instruction identifies `deployment-version` as the handoff target and requires the previous changes and edits to be captured there.

**Architecture:** Start from verified `origin/deployment-version` `62e31ad621238c6ce1da62934710128831df3b5e`. Integrate the student app checkpoint `62ab3982ca21c575263c905b51b958ea50b5a24e` and catalogue checkpoint `3c02448f23a5637d119e1a624dab3e02f3c0ac2c` using their common ancestor. Resolve each overlap to retain both behaviors, regenerate derived manifests and compare with the running local source export.

**Tech stack:** Git/LFS, React/TypeScript/Vite/Vitest, Python/FastAPI/pytest, existing hosted asset and catalogue workflows.

## Global constraints

- Target `aasedor/CityPrompt` `deployment-version`; preserve history, never force-push.
- Preserve original worktrees, source export, unrelated changes and generated evidence.
- Keep GLB bytes and existing trial/approval status intact; no new model generation or keeper promotion.
- Never parse and rewrite the authored archetype catalogues.
- No paid jobs, secret disclosure, production deployment or private security-proof publication.
- Keep known security blockers visible; source consolidation is not a security clearance.

## Review focus

- Imported GLBs, ground finishes and simplified reports survive the older catalogue branch's overlapping edits.
- Building-only geometry, tight footprints and bridge assemblies survive the student runtime merge.
- Photographic images resolve with exact asset bytes, including restored local images.
- Regression tests present in Git are retained even when absent from the partial running export.
- Production build/asset selection reflects the combined source rather than either old standalone snapshot.

## Task 1: Integrate the two completed histories

- [x] Record source commits, remote baseline and the running export's uncommitted differences externally.
- [x] Fast-forward the integration branch to the student app checkpoint, then merge the catalogue checkpoint without committing unresolved conflicts.
- [x] Resolve individual overlaps, preserving both sets of tests; regenerate only derived metadata.
- [x] Verify both source commits are ancestors of the resulting merge and inventory remaining local-only differences.

## Task 2: Verify the combined release

- [x] Run focused tests for imported GLBs, surfaces, reports, towers, snapping, intersections, catalogue cards, fixed footprints and bridge corrections.
- [x] Run TypeScript, lint, relevant backend tests, hosted asset checks and production build.
- [ ] Run browser placement/edit/save/reload/walk/free-capture checks on the combined build.
- [x] Obtain an independent whole-integration review, address regressions and record honest limits.

## Task 3: Capture the handoff branch

- [x] Commit the coherent integration and a source/asset coverage note after diff checks.
- [ ] Verify the remote target has not moved; preserve exact commit and LFS-object availability evidence.
- [ ] Prepare a checked PR targeting `deployment-version`; promote through the existing CI process only when passing and within the user's branch-update authorization.
- [ ] Verify remote readback and retain a rollback commit. Keep production deployment a separate action.

## Actual completion boundary

Browser checks covered project/boundary creation, catalogue discovery, hospital placement/rotation, saved reload, tower height editing and quantitative reports. A complete fresh browser walk/free-export/route matrix remains unrun on this combined checkout; earlier local evidence and automated tests are separate. Seven unpublished building pilots still fail the intentional publication preflight. The source consolidation may be proposed as a draft PR, but cannot be merged through failing required CI or treated as security clearance.
