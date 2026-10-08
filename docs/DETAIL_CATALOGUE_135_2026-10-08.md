# Standalone detail catalogue: 135 choices

## Scope

Add 35 fixed-size objects to the existing 100-choice detail catalogue. Twenty-six
reuse current park/street builders or runtime geometry; nine small amenities use
the same timber, muted green, stone and metal palette. No embedded archetype
objects or building families change. Local checkpoint only; no deployment.

Students use **Edit details**, search or select a category, choose a model and
add it. Move, rotate, remove and undo remain confined to this editor. Placement
is independent of building, street and park footprints.

## New choices

| Category | Additions |
|---|---|
| Seating (7) | Team bench; three-row bleachers; hammock; cafe table and four chairs; backless bench; classic picnic table; four-seat audience row |
| Shelters & markets (4) | Covered team bench; bus shelter; garden teaching canopy; projection booth |
| Street furniture (6) | Bus stop pole; bicycle pump; dog-waste bag dispenser; fire hydrant; wayfinding fingerpost; community mailbox |
| Edges & gates (3) | Picket fence; boardwalk railing; low stone wall |
| Landscape (3) | Planted tree surround; guarded tree surround; stepping stone |
| Planting (4) | Compact shrub; fine grass tuft; low flowering perennial; wildflower meadow patch |
| Garden & growing (2) | Botanical label; corten growing bed |
| Lighting (2) | Twin-head court light; festoon light span |
| Play (2) | Dog agility hoop; dog agility tunnel |
| Sport & exercise (1) | Referee chair |
| Water & landmarks (1) | Outdoor cinema screen |

## Assets and performance

The 35 local GLBs total 2,202,128 bytes and 36,599 triangles, with at most five
material meshes per asset. The largest object is 18,100 triangles. Models load
on placement and use the existing shared geometry/material and instanced-copy
renderer. No new textures, animations, provider calls or camera-frame rebuilds.
This preserves the existing optimization; it is not a new laptop FPS benchmark.

Each registry entry records dimensions, grounded centre offset, source builder,
SHA-256, byte size and mesh/triangle counts. New backend allowlist entries match
all frontend IDs. The runtime asset manifest includes all 35 files. GLBs are
intentional Git LFS deliverables, individually staged despite the general
generated-output ignore rule.

## Reproduction

Run from the repository root with installed frontend dependencies and Blender:

```text
node tools/detail_catalogue/export_kit.cjs <fresh-external-kit-directory>
python tools/detail_catalogue/build.py --output <fresh-external-batch-directory> --dry-run
blender --background --python tools/detail_catalogue/build.py -- --kit <kit-directory>/kit.json --output <fresh-external-batch-directory>
```

Use repeated `--id` arguments for a bounded pilot. The builder refuses to replace
an existing output directory. Inspect exported models before promotion; derive
registry dimensions and offsets from actual GLB bounds (Y-up), not nominal sizes.
Backend restart is required after changing the server allowlist.

## Verification

- Dry run: exactly 35 models, zero paid calls.
- Cafe table and bicycle pump pilot rendered and inspected before full batch.
- All 35 inspected on browser review pages 5–7; all served GLB bytes match hashes.
- 49 narrow frontend tests passed; eight backend detail tests passed.
- TypeScript and focused ESLint passed.
- Browser trial in `Bench detail editor · pilot`: added cafe seating, bicycle pump
  and dog tunnel in open space, moved and rotated, removed and undid removal,
  saved, then reloaded. All three persisted with the prior 17 details (20 total).
- Reviewed the placed scene in 3D. At close range, original Google tile trees
  outside the cleared site can obscure the camera; this is not changed here.
- Local review pagination now derives its seven pages from the catalogue size.

Evidence and intermediate output stay outside Git:
`C:/dev-artifacts/CityPrompt/detail-catalogue-135-2026-10-08/`.
The local server uses the hydrated public directory under the existing
`render-readiness-2026-10-07/assets-model-fix/public` folder. A release still needs
the usual complete asset hydration; tracked metadata validation alone does not
prove the whole release package is hydrated.
