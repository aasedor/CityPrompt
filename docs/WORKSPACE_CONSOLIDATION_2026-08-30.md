# Workspace consolidation — 2026-08-30

## Outcome so far

This pass protects existing work while reducing active clutter around canonical
RLASM production.

- Canonical remote: `origin` → `https://github.com/aasedor/CityPrompt.git`.
- The former dirty local `main` workspace is preserved unchanged on
  `codex/recovery-main-2026-08-30`.
- Local `main` now points to `origin/main`; clean maintenance work uses a
  separate sparse worktree.
- PR #8 made RLASM v6.1 the canonical building method and retired the
  self-contained legacy Sticker Method skill.
- Seventy-three stale merged remote branches and three stale local branches
  were pruned; the temporary cleanup branch was retired after merge.
- Git object garbage is zero after removing 1.36 GiB of an interrupted
  temporary pack.
- All twenty-three Amsterdam Hofje candidates (v001-v023) were copied and
  file-by-file verified in `C:\dev-artifacts\CityPrompt\sha256`, then removed
  from `artifacts/`. Their 23 unique tree manifests cover 1,296 files and
  1,661,348,946 bytes. A two-file smoke-test object used to validate the archive
  workflow was removed after the production archive completed.
- The independently approved v023 keeper was squash-merged by PR #9 at
  `e1279319c2256ff019f1b18d95123ef7d29e2c38`. Its compact Git package uses LFS
  for promoted visual evidence while BLEND/GLB files remain external and
  hash-bound. Its clean worktree and obsolete local branch were retired only
  after their tree exactly matched `origin/main`.

## Protected recovery workspace

`C:\Users\andre\OneDrive\Documents\CityPrompt` is intentionally dirty on
`codex/recovery-main-2026-08-30`.

Unique tracked work preserved there:

- `docs/HIGH_QUALITY_3D_BUILDING_MEMORY.md`;
- `tools/archetype_compiler/generate_worldclass_library.py`;
- `tools/archetype_compiler/high_quality_building_memory.json`;
- `tools/archetype_compiler/quality_memory.py`; and
- `tools/archetype_compiler/tests/test_quality_memory.py`.

Two untracked backend diagnostic scripts and permission-locked test scratch also
remain. Do not reset, clean, or delete this workspace. Review and commit the
five-file family-wave memory initiative separately after its narrow tests pass.

## Worktree classification

The command below produces the current machine-readable classification:

```powershell
.\scripts\audit_git_worktrees.ps1 -Repository .
```

As of this checkpoint, no pre-existing worktree is removal-eligible:

- the main recovery, building-memory repair, old-Montreal reproduction, and
  relaxed-bardeen worktrees are merged but dirty;
- `cp-building-trial-images` is merged but locked in an incomplete initializing
  state and must not be force-removed without a separate recovery decision;
- the consolidation worktree is the only cleanup initiative still active;
- recursing-murdock, both Brick/Bronze initiatives, Sticker reproduction, and
  the Parisian midrise worktree contain unmerged work; and
- the Parisian worktree is clean but belongs to the separate 3D-Maps workspace,
  so this CityPrompt cleanup does not modify it.

A worktree is removable only when the audit reports
`removal_eligible: true`, its branch/commit is published or archived, and no
active process owns the path.

## Artifact state

After complete Hofje candidate archival, `artifacts/` contains 59 top-level
directories totaling approximately 722,115,383 bytes. The remaining majority
is generated pytest output that is
safe in principle but currently owned by another Windows identity. Deletion was
attempted only after confirming no pytest process was active; Windows denied
all 54 exact `artifacts/pytest-*` roots. Do not take ownership or bypass ACLs
during routine cleanup.

Use the content-addressed archive command for valuable immutable evidence:

```powershell
.\scripts\archive_content_addressed.ps1 \
  -AllowedSourceRoot .\artifacts \
  -SourcePath .\artifacts\candidate-name \
  -StoreRoot C:\dev-artifacts\CityPrompt \
  -RemoveSource
```

The script computes a canonical tree SHA-256, copies to a staging object,
rehashes every destination file, writes `archive-manifest.json`, and removes
the source only after verification.

## Enforcement added by this initiative

`scripts/check_repository_blob_policy.py` rejects:

- a newly changed ordinary Git blob above 1 MiB; and
- a path marked `filter=lfs` whose committed object is not a valid LFS
  pointer.

The CI workflow runs the gate against the pull-request delta using full Git
history. Existing historical blobs are not rewritten by this check; their
migration follows `docs/GIT_HISTORY_MIGRATION_RUNBOOK.md`.

PR #10 squash-merged these controls at
`3246067fa9324bfab34ec686ff8391f27601a80e`. The `main` branch now requires a
strict, current-base pass from `backend`, `frontend`, `browser`, `docker`, and
`repository-hygiene`. Protection applies to administrators, requires linear
history and resolved conversations, and disables force-pushes and branch
deletion.

## Remaining bounded work

1. Review and checkpoint the protected five-file family-wave memory initiative.
2. Resolve permission-locked pytest/scratch roots with their owning Windows
   account; do not bypass ownership from an automated cleanup.
3. Run the history migration rehearsal in a mirror clone. Do not perform the
   cutover or rewrite shared refs without the separate approval required by the
   migration runbook.
