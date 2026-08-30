# RLASM repository policy

**Status:** active
**Method authority:** RLASM v6.1
**Canonical remote:** `https://github.com/aasedor/CityPrompt.git`
**Canonical branch:** `origin/main`

This policy keeps exact-source building work reviewable without turning the
active Git repository into an experiment cache. It complements
`docs/RLASM_LATEST_METHOD.md` and
`tools/archetype_compiler/rlasm_method.json`.

## Active Git contents

The active repository may contain:

- the canonical human and machine RLASM method;
- building compiler source and narrow contract tests;
- the keeper registry;
- one intentionally promoted package per approved keeper;
- exact locked catalogue sources used by that keeper;
- source and material provenance, prompts, hashes, and prework measurements;
- deterministic preparation and build scripts;
- the final complete render set and two phone boards;
- final builder and independent holistic reviews; and
- the keeper manifest and discrepancy ledger.

A promoted keeper must have a complete independent holistic review with zero
P0 and zero P1 blockers. Scoped material, contact, roof, or optical passes do
not authorize promotion.

## External artifact contents

Keep these outside the active Git tree in content-addressed artifact storage:

- rejected and superseded candidate versions;
- `.blend`, `.glb`, raw render batches, clay studies, and diagnostic movies;
- transient source/material generation attempts;
- browser profiles, test fixtures, caches, and temporary worktrees; and
- full legacy-method snapshots retained only for reproducibility.

Each retained external candidate bundle must include a manifest with candidate
ID, lifecycle state, source hashes, file hashes, review decision, creation
date, and the keeper or successor that closed it. Verify the external copy
before removing the active duplicate.

## Historical methods

Sticker Method/V98 records may remain temporarily when current runtime code or
tests still consume them. They are compatibility data, not current building
authority. Retire each legacy subsystem as one bounded, tested change:

1. identify every runtime and test consumer;
2. replace the consumer with an RLASM keeper or neutral compatibility fixture;
3. archive immutable historical evidence externally;
4. remove generators, generated payloads, reviews, and tests together; and
5. run the complete affected compiler and runtime gates.

Do not merge a legacy batch wholesale into the keeper registry. Re-review each
building under canonical RLASM and promote only the passing candidate.

## Working-directory hygiene

Agent scratch, pytest copies, render experiments, and candidate iteration
folders are ignored. Do not use `git clean` or bulk deletion in a recovery
workspace. Resolve exact paths, verify that no active worktree or process owns
them, and remove only the confirmed disposable target.

Use one named branch or worktree per initiative. Remove a worktree only after
its status is clean and its commits are merged, pushed, or archived. Never
remove a dirty worktree to make status output quieter.

## Branch and history hygiene

- Delete merged pilot branches after verifying their tips are contained in
  `origin/main`.
- Classify unmerged branches as promote, archive, or drop before deletion.
- Preserve unique valuable commits with an immutable tag or verified Git
  bundle.
- Never force-push shared `main` during ordinary cleanup.
- Treat an in-place history rewrite as a scheduled migration requiring a
  remote freeze, verified mirror backup, credential rotation, collaborator
  notice, and mandatory reclone.

Large runtime media belongs in object storage or Git LFS, not ordinary Git
blobs. Adding an LFS attribute does not convert existing history; normalization
and history migration are separate reviewed operations.

## Promotion checklist

Before committing a keeper package:

1. confirm the package is the exact independently approved version;
2. verify source, render, board, provenance, and review hashes;
3. exclude failed versions, caches, models, and transient renders;
4. confirm large promoted binaries use the repository's approved storage;
5. run the narrow RLASM contract tests;
6. run `git diff --check`, inspect `git diff --stat`, and inspect the complete
   staged file list; and
7. push only to the explicitly authorized remote and feature branch.
