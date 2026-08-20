# Catalogue expansion handoff — 2026-08-19

## Start here

- Active worktree: `C:\Users\wbesh\OneDrive\Desktop\Projects\CityPrompt-catalogue-wave1`
- Active branch: `codex/catalogue-expansion-wave1`
- Pipeline commits before promotion: `da751c76c Add reviewed catalogue expansion pipeline`
  and `58f42aa66 Document catalogue expansion handoff`
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
- Human visual approval: recorded for all four families by `wbesh` on
  2026-08-19 after reviewing the local comparison gallery.
- Catalogue quality assessment: `pass`; all four families report
  `high_quality_ready: true` with no findings.
- Promotion status: promoted locally. The seed now contains 705 rows, including
  28 new rows (seven per family), and all 28 promoted GLBs have unique URLs,
  valid `glTF` headers, files below the 75 MB API cap, and exact `bottom_y = 0`.
- Live seed status: the local database/object store was hydrated successfully;
  28 database rows were inserted and the new object URLs return HTTP 200.
- Publish status: not pushed from this worktree.

The live `Generate to 3D` test project built and placed two detailed Machiya
buildings successfully. Both GLBs loaded without asset errors and visibly sit
flush on the neutral preview plane. The only browser diagnostic was the known
terrain-elevation fallback caused by the missing Google Maps frontend key.

The modular rebuild path is approximately five times faster than rebuilding
the complete landmark geometry. Individual modular files were reduced by
roughly 63–75 percent during the pilot. Treat these as measured pilot results,
not a guarantee for every future archetype.

Runtime planning was also optimized for the expanded catalogue. The two live
`POST /lego-assembly/plan` calls now take 2.59 s and 2.62 s instead of roughly
26.5 s each (about 10x faster, or a 90% reduction). The complete fresh browser
flow planned, persisted, and displayed both buildings in about 7.2 s.

## Review locally

The local review gallery is served from the artifact root. If it is not
running, launch it from PowerShell:

```powershell
python -m http.server 4173 --bind 127.0.0.1 --directory "C:\Users\wbesh\OneDrive\Desktop\Projects\CityPrompt-asset-grounding\artifacts\catalogue-expansion-wave1\families"
```

Then open `http://127.0.0.1:4173/`.

The full local app is served at `http://127.0.0.1:5174/`; its API health check
is `http://127.0.0.1:8000/health`. The app can run the neutral 3D preview, but
map/Google Tiles QA still needs a real `VITE_GOOGLE_MAPS_API_KEY`. No usable
key was found in the accessible sibling CityPrompt folders or OS environment,
so do not invent or commit one.

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
2. Treat the four-family batch as approved and locally promoted; do not repeat
   approval or regenerate it unless the source manifests intentionally change.
3. Review the local commits and Git LFS status, then push only when explicitly
   requested.
4. Add the missing local Google Maps key outside Git before map/terrain QA.
5. For the next catalogue wave, keep the same bounded dry-run, visual-review,
   approval, promotion, grounding-audit, and live-app sequence.

Verified checks at this handoff:

- catalogue promotion audit: 28/28 rows and 28/28 grounded GLBs passed;
- catalogue workflow tests: 5 passed;
- LEGO assembly and Master Planner catalogue tests: 194 passed;
- frontend runtime tests: 68 passed across six files;
- frontend TypeScript check: passed;
- live browser: two detailed buildings placed and GLBs fully loaded.

The older `test_wave14_variant_families.py` fixture still assumes generated
families live under `frontend/public/families`; this pilot deliberately keeps
heavy review artifacts external, so its 20 path-based failures are a legacy
fixture-location mismatch rather than a generated-asset regression.

Never copy API keys into this handoff, source files, generated manifests, or
Git history. Use the existing local environment files only when the full app is
tested.
