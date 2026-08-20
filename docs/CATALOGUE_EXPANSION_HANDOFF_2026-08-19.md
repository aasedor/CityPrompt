# Catalogue expansion handoff — 2026-08-19

## Start here

- Active worktree: `C:\Users\wbesh\OneDrive\Desktop\Projects\CityPrompt-catalogue-wave1`
- Active branch: `codex/catalogue-expansion-wave1`
- Pipeline commit at handoff: `da751c76c Add reviewed catalogue expansion pipeline`
- Canonical integration remote/branch: `cityprompt/main`
- Generated artifact root: `C:\Users\wbesh\OneDrive\Desktop\Projects\CityPrompt-asset-grounding\artifacts\catalogue-expansion-wave1\families`

Do not use `C:\Users\wbesh\OneDrive\Documents\ChatGPT\Cityprompt` as a source
worktree. It is only a local redirect for older Codex tasks.

## What exists

The bounded pilot contains four Sticker + LEGO building families:

1. `modern-black-screen-machiya`
2. `red-machiya-cafe-gallery`
3. `mid-century-wood-stone-pavilion`
4. `mid-century-white-brise-soleil-pavilion`

Each family has an assembled GLB, six modular GLBs, registered source imagery,
near/far PBR atlases, manifests, validation output, quality assessment output,
and multiple Blender review renders. There are 28 GLBs in the pilot.

## Current quality state

- Structural validation: pass for all four families.
- Grounding audit: all module and assembled bounds start at `Y = 0.000 m`; no
  floating, sinking, inverted-normal, or vertical-stack errors were found.
- Catalogue quality assessment: `review`, not approved.
- Remaining gate: human visual approval of the photoreal skin and assembled
  appearance.
- Promotion status: not promoted into the seed/runtime catalogue.
- Publish status: not pushed from this worktree.

The modular rebuild path is approximately five times faster than rebuilding
the complete landmark geometry. Individual modular files were reduced by
roughly 63–75 percent during the pilot. Treat these as measured pilot results,
not a guarantee for every future archetype.

## Review locally

The local review gallery is served from the artifact root. If it is not
running, launch it from PowerShell:

```powershell
python -m http.server 4173 --bind 127.0.0.1 --directory "C:\Users\wbesh\OneDrive\Desktop\Projects\CityPrompt-asset-grounding\artifacts\catalogue-expansion-wave1\families"
```

Then open `http://127.0.0.1:4173/`.

Review the overview first, then inspect comparison, corner, street, aerial,
and context views for every family. Human approval should explicitly check:

- contact with the ground plane;
- no interpenetration between podium, repeat floors, crown, and roof;
- facade identity and material continuity around corners;
- windows, screens, and entrances reading as physical depth rather than flat
  paint;
- acceptable repetition across the flexible-height variants.

## Pipeline files on the branch

- `tools/archetype_compiler/approve_family_review.py`
- `tools/archetype_compiler/create_wave14_comparison_sheets.py`
- `tools/archetype_compiler/generate_wave14_variant_families.py`
- `tools/archetype_compiler/tests/test_catalogue_expansion_workflow.py`
- `tools/promote_compiled_families_to_seed.py`

The approval tool records the human decision. The promotion tool is deliberately
separate so a generated family cannot silently enter the runtime catalogue.

## Safe continuation sequence

1. Confirm `git status --short --branch` and read `CLAUDE.md` plus
   `docs/HIGH_QUALITY_3D_BUILDING_MEMORY.md`.
2. Open the review gallery and obtain an explicit approve/revise decision for
   each family.
3. Record only approved families with `approve_family_review.py`.
4. Run the narrow compiler workflow tests and grounding audits again.
5. Run the promotion tool in dry-run mode before modifying catalogue data.
6. Promote only the approved bounded batch, then verify it in CityPrompt at
   `localhost:5174` before committing or pushing.

Never copy API keys into this handoff, source files, generated manifests, or
Git history. Use the existing local environment files only when the full app is
tested.
