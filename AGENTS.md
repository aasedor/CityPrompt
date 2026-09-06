# SiteForge Agent Guide

Read `CLAUDE.md` before substantial work; it contains repository architecture,
commands, visual-generation rules, and the pilot-before-scale workflow. For
building-family work, also read `docs/RLASM_LATEST_METHOD.md`,
`docs/RLASM_REPOSITORY_POLICY.md`, and
`docs/HIGH_QUALITY_3D_BUILDING_MEMORY.md`, and keep their machine-readable
companions synchronized. RLASM v6.1 is the only active building method;
Sticker Method/V98 material is historical compatibility evidence.

## Start safely

- Run `git status --short --branch` before editing.
- Work on one named initiative per branch or Git worktree. Do not mix parks,
  streets, building families, compiler changes, and unrelated fixes.
- Treat pre-existing changes as user work. Do not reset, clean, overwrite, or
  stage files outside the current initiative.
- If the tree is already dirty in files the task needs, inventory the overlap
  and preserve it before making changes.

## Generated assets

- Keep heavyweight render experiments and visual-QA output outside the source
  tree when a command supports an output directory. Otherwise use an ignored
  local output directory such as `artifacts/`.
- Never stage a generated directory wholesale. Promote only reviewed,
  intentional deliverables. Use Git LFS or artifact storage for large binary
  assets instead of ordinary Git blobs.
- Follow the repository's pilot sequence: dry run, one-archetype pilot, visual
  review, then bounded scale-up.
- Do not start an open-ended generation loop. Define a finite batch and create
  a checkpoint before the next batch.

## Verification and checkpoints

- Frontend: run the narrow Vitest files for the touched feature, then
  `npm run type-check` when TypeScript production code changes.
- Backend: run the narrow pytest files for the touched service or endpoint.
- Compiler: run the narrow tests under `tools/archetype_compiler/tests/`.
- Review `git diff --check`, `git diff --stat`, and `git status --short` before
  every commit.
- Commit one coherent, verified unit at a time. Do not push unless requested.
- A task is complete only when its relevant checks pass and the final status
  clearly separates source changes from ignored/generated output.

## Recovery state

The repository entered recovery on 2026-07-19 after an interrupted Codex turn.
See `docs/WORKSPACE_RECOVERY_2026-07-19.md` before reorganizing or deleting any
of the preserved generated output.

## Current catalogue expansion

For the active ten-family Wave 2 review, read
`docs/CATALOGUE_EXPANSION_WAVE2_REVIEW_2026-08-19.md` before continuing. The
families are structurally valid and grounded, but intentionally remain outside
the seed/runtime catalogue until explicit human visual approval. The inherited
four-family pilot is documented in `docs/CATALOGUE_EXPANSION_HANDOFF_2026-08-19.md`.
Both waves remain local-only; do not publish either without explicit approval.

## Repeatable building catalogue publication

Follow `docs/BUILDING_CATALOGUE_WORKFLOW.md` for reviewed local pilots, exact-byte
activation, generated picker cards, selective seeding/readback and a checked PR
to main. `python -m tools.catalogue_promotion check` is the publication preflight.
Trial entries cannot pass publication CI. This workflow does not change the RLASM
6.1 visual method or grant keeper approval.
