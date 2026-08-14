# CityPrompt repository workflow

## Contents

1. Canonical locations
2. File naming
3. Verification commands
4. Generated output policy
5. Git checkpoints

## 1. Canonical locations

In CityPrompt, Sticker Method work normally uses:

```text
frontend/public/archetypes/buildings/<archetype>/
tools/archetype_compiler/build_<family>_v98.py
tools/archetype_compiler/prepare_<family>_v98_assets.py
tools/archetype_compiler/compile_<family>_v98.py
tools/archetype_compiler/create_<family>_v98_review.py
tools/archetype_compiler/sticker_assets/<family>/
tools/archetype_compiler/tests/test_<family>_geometry_v98.py
tools/archetype_compiler/tests/test_<family>_assets_v98.py
tools/archetype_compiler/tests/test_<family>_compiler_v98.py
docs/reviews/catalogue-rollout-v98/sticker-method-batch-01/<review-name>/
artifacts/sticker-method-batch-01/<review-name>/
```

The repository memory and common carrier schema are:

```text
docs/HIGH_QUALITY_3D_BUILDING_MEMORY.md
tools/archetype_compiler/high_quality_building_memory.json
tools/archetype_compiler/sticker_carrier_space.py
tools/archetype_compiler/sticker_method_batch_01.json
```

## 2. File naming

Use deterministic, semantic names. Prefer:

- `front_<role>_<index>` and side/rear/court equivalents;
- explicit `head`, `sill`, `jamb`, `return`, `pane`, `card`, `backing`, `cap`, `soffit`, and `curb` suffixes;
- `whole_<module-size>_module` tags only on real rendered construction;
- `fixed_<identity>` tags on singular assemblies.

Do not use opaque count-only names that hide ownership or orientation.

## 3. Verification commands

Run the focused family suite:

```powershell
python -m pytest `
  tools/archetype_compiler/tests/test_<family>_geometry_v98.py `
  tools/archetype_compiler/tests/test_<family>_assets_v98.py `
  tools/archetype_compiler/tests/test_<family>_compiler_v98.py -q
```

Compile scripts:

```powershell
python -m py_compile `
  tools/archetype_compiler/build_<family>_v98.py `
  tools/archetype_compiler/prepare_<family>_v98_assets.py `
  tools/archetype_compiler/compile_<family>_v98.py `
  tools/archetype_compiler/create_<family>_v98_review.py
```

Before every commit:

```powershell
git diff --check
git diff --stat
git status --short --branch
```

## 4. Generated output policy

Keep experiments under `artifacts/` or another ignored location. Use finite folders such as:

```text
clay-canonical-v1
beauty-canonical-v2-eevee
cycles-diagnostic-v3
formal-canonical-v1
formal-extended-v1
```

Promote only selected renders, boards, validation, preflight, and evidence JSON. Do not stage an artifact tree wholesale.

## 5. Git checkpoints

- Start from `git status --short --branch`.
- Keep one building initiative per branch/worktree.
- Stage explicit paths in a dirty worktree.
- Commit only after the formal release and evidence publisher pass.
- Push after each approved wave only when requested.
- Never reset, clean, or stage unrelated user work.
- For a release destined for another remote, test the cherry-picked commit in a clean integration worktree and restore any explicitly required shared dependency or exact reference before merging.
