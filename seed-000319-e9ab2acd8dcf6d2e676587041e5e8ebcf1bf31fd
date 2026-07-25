# Workspace Recovery — 2026-07-19

## Why this checkpoint exists

Codex stopped abruptly on 2026-07-19 at approximately 14:55 America/Edmonton
while a tool command was still being streamed. Git remained structurally
healthy, but the working tree contained several initiatives and large generated
asset batches without a checkpoint.

Recovery branch: `codex/recovery-2026-07-19`

Baseline commit: `0e6c4adb` (`feat: add architect-wow facade signature pipeline`)

## Pre-recovery inventory

- 119 modified tracked files
- 19,133 insertions and 1,884 deletions in the tracked diff
- 4,589 untracked files
- approximately 4.4 GB of untracked data
- no merge, rebase, cherry-pick, or stale Git lock
- `git fsck --connectivity-only --no-dangling` passed

Largest untracked generated groups at inventory time:

| Approximate size | Directory |
| ---: | --- |
| 1,161 MB | `tools/archetype_compiler/facade_sheets_pbr_catalog/` |
| 1,071 MB | `tools/archetype_compiler/facade_sheets_pbr_v21/` |
| 676 MB | `tools/archetype_compiler/facade_sheets_pbr_v20/` |
| 239 MB | `tools/archetype_compiler/facade_sheets_pbr_v36/` |
| 197 MB | `tools/archetype_compiler/facade_sheets_pbr_new_site/` |
| 192 MB | `tools/archetype_compiler/facade_sheets_pbr_variant_pilot_v1/` |
| 184 MB | `tools/archetype_compiler/facade_sheets_pbr_v34/` |
| 119 MB | `tools/archetype_compiler/facade_sheets_pbr_v16/` |

These files were not deleted or moved during initial recovery. Confirmed
generated families were added to `.gitignore` so they no longer dominate normal
source review. Existing tracked assets remain tracked.

## Source-work buckets requiring review

The remaining visible changes span at least these initiatives:

1. Building-family and façade compiler work
2. Parks, streets, terrain, and globe rendering
3. Community 3D compilation and LEGO assembly
4. Backend planning, geometry, files, and zone APIs
5. Catalog data, documentation, and quality memory

Each bucket should be tested and committed independently. Do not use
`git clean`, a hard reset, or a bulk delete to reduce this inventory.

## Relocation plan

After source checkpoints are committed:

1. Create a fresh clone outside OneDrive, preferably `C:\dev\3D-Maps`.
2. Keep heavy experiments under a separate local artifact root, such as
   `C:\dev-artifacts\3D-Maps`.
3. Copy only explicitly selected outputs or authoritative source images into
   the fresh clone.
4. Track required large binaries with Git LFS or publish them through artifact
   storage.
5. Verify tests in the fresh clone before retiring this recovery workspace.

The OneDrive workspace remains the recovery source until that verification is
complete.
