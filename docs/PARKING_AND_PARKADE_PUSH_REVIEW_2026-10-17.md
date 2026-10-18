# Parking tools and five parkades: repeat trial and review push

The user requested: “Trial them one more time. Then organize a push with the
latest updates.” This authorizes pushing the tested work to the canonical
`aasedor/CityPrompt` repository. It does not turn the five DEV-only parkade
trials into a live catalogue publication.

## Branch and scope

- Review branch: `codex/parkade-family-pilot`.
- Fetched canonical `origin/main`: `30de8b2c188864c014e64941dfefec0c6fdf8037`.
  It is an ancestor of this branch.
- Fetched current release branch `origin/deployment-version`:
  `3e73508bfcc1caed57540713592f9653d4dc138a`, also an ancestor.
- Before this report, there were seven local commits beyond that release:
  drawn parking lots, driveway connections, connected-development evidence,
  Streets discovery, Classic pilot, and the finite five-model trial.
- Review against `deployment-version` keeps the existing release history out
  of the diff; reviewing against main would include 348 commits already in the
  release lineage. No merge, release-branch update or deployment is part of
  this review push.
- Existing LFS rules apply to exactly five GLBs and 25 source/preview PNGs.
  The LFS dry run listed only those 30 new objects. No LFS policy changes.

## Repeat trial actually performed

The existing disposable local project
`http://127.0.0.1:5184/projects/060a2f62-af41-4670-b4a9-0da25d2b10cc`
was reloaded before testing. Each of Classic Concrete, Urban Brick, Green
Terraces, Solar Ribbon and Mobility Courtyard was selected in the actual map,
rotated from 15 to 30 degrees, deleted, restored with Undo, reselected and
checked for the preserved 30-degree edit. Each was then restored to 15 degrees.
The full page was reloaded again. All five models displayed and both save
indicators read saved.

Independent read-only SQL verification against the guarded local test database
confirmed six zones (boundary plus five buildings), five compiled building
rows, every exact variant and native floor count, and 15-degree polygon yaw
for each. Local Model Library verification again confirmed every DB binding
and exact object-storage byte hash.

The existing connected-development project
`http://127.0.0.1:5184/projects/c8d16205-ef09-4662-a1ba-66629a1fa8ad`
was reloaded without edits. The road, driveway, marked parking lot and hall
displayed together on the prepared boundary. Streets still exposed the parking
lot drawing entry and the shared parkade shortcut. Both reloaded project tabs
returned zero captured browser error logs during this pass.

Fresh automated checks:

- 271 Python tests: parkade tools, local identity gating, plan archetypes,
  LEGO assembly.
- 55 Python project-details persistence/validation tests.
- 71 Vitest tests in seven files: parkade trial, picker palette, canonical
  catalogue, registry, picker categories, parking layout and driveway geometry.
- 15 Vitest tests in three files: bench/detail editor, paving editor, paving
  surfaces.
- `npm run type-check`: passed.
- `python -m tools.catalogue_promotion check --metadata-only`: passed for the
  existing 58 published buildings. The five trials remain separate.
- All five local seed/object verifications: passed.

The previously successful configured production build remains evidence for the
unchanged implementation commit `99f5cc576`; this pass changes only this report.
No new paid render was generated. There is no claim of a fresh full-suite run,
hosted publication, student-laptop performance or engineering approval.

## Evidence and next release boundary

Repeat evidence is external under
`C:/dev-artifacts/CityPrompt/parkade-family-2026-10-17/`:
`repeat-browser-trials.json`, `repeat-trial-readback.json`,
`repeat-trial-after-reload.png`, `repeat-connected-development.png`.
Earlier exact model/source inventories, browser capture and measurements are
linked from `PARKADE_FAMILY_LOCAL_TRIAL_2026-10-17.md`.

Keep the worktree and local scene available for review. The five parkades remain
DEV-only with an explicit local API identity overlay; a Git push does not add
them to cityprompt.ca. Publishing them needs the existing exact-byte catalogue
promotion, hosted storage verification and deployment checks. Existing saved
scenes and live services are unchanged by the review push.
