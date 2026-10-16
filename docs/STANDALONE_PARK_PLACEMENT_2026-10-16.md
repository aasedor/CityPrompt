# Standalone park placement repair

## Cause and change

The reported second-object failure was the native park API's unconditional
requirement for an active prepared site boundary, not a two-object limit.
Native rendering and walking enforced the same restriction. Flexible parks
had the equivalent API restriction.

Standalone native and flexible parks now prepare their own footprint at the
finite ground elevation saved when the user picks a placement. Ground,
native models, walking and capture share that datum. An existing prepared
site remains authoritative. Missing heights, retained/natural terrain and
invalid native dimensions still fail validation. No models, migrations,
global scale, providers or stored scene formats change.

## Local verification

- 194 frontend tests passed across standalone/prepared ground, authored camera
  ground, park assembly ground, native walking/layouts, catalogue, canonical
  placement, snapping and automatic 3D updates.
- 101 backend tests passed across standalone ground, optional site boundary,
  flexible/native parks, zone utilities and schema validation.
- TypeScript check and production Vite bundle build passed. Build used the
  existing hydrated public asset directory; public files were not recopied.
- Targeted ESLint: no errors, one existing NativeParkLayer effect-dependency
  warning. `git diff --check` passed.
- Actual Edge local fixture: `4167be5a-1bca-4e31-af94-b28d8e90fa01` on port 5174.
  Two industrial sheds and two native basketball parks placed without any
  site boundary. Save/reload, rotation, move, delete, undo/redo, walk entry and
  free street-view 3D capture passed. No paid generation was submitted.
- Screenshots outside Git: `C:/dev-artifacts/CityPrompt/standalone-parks-local-`
  with suffixes `overhead.png`, `walk.png`, `street-preview.png`.

Flexible parks have automated validation coverage; individual flexible designs
and every native park layout were not individually placed in the browser.
This is a level footprint, not a terrain-following mesh or a newly validated
retaining-wall solution for steep hillsides. Moving keeps the saved authoring
datum, consistent with an existing prepared site.

## Release and rollback recorded before promotion

Production: https://www.cityprompt.ca, GitHub `aasedor/CityPrompt`,
branch `deployment-version`, existing Render services only.

Before this change:

| Service | Service ID | Verified prior commit | Prior live deployment |
| --- | --- | --- | --- |
| Frontend | srv-d6ehqtjh46gs73e28n50 | 379299deb7d79a7af96bdd4d1a01e02847123485 | dep-db8rfjjbc2fs73bu7ph0 |
| API | srv-d6ehtvk1hm7c73f5ho9g | e1fb0282989dde62d7b45d878b820fbcae4b2819 | dep-db8r57bl550s73etk140 |
| Worker | srv-d6ehtvk1hm7c73f5hob0 | e1fb0282989dde62d7b45d878b820fbcae4b2819 | dep-db8r5c6q1p3s7393l340 |

Use the existing Render deployment rollback controls for these deployments if
necessary. No schema rollback is required. Prior code cannot edit/render new
standalone native parks, so preserve their records and pending browser drawings
when rolling back; do not delete them to conceal the issue.

Promotion requires the tested commit, frontend version verification, API
readiness and a dedicated hosted placement/save/reload check. Local checks
above are not evidence of a completed production deployment.
