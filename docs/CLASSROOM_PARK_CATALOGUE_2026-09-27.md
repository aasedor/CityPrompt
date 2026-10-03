# Fifteen local park types: model-build checkpoint

Branch `codex/classroom-park-catalogue`, starting at `a1ef001cd`. Seven new
fixed native choices extend the existing eight park types. Basketball Long is
an additional layout of Basketball, not a sixteenth park type.

The user requested Astra construction first, followed by Sol browser testing.
These seven additions have agent visual review and offline asset/geometry checks;
they have **not** passed the new browser acceptance. `completed` remains false.
The original eight retain their separate existing acceptance records. No paid
image call, Git push or hosted deployment is included in this checkpoint.

| Added park | Exact build | Native dimensions |
| --- | --- | --- |
| Shaded Reading Garden | reading-v002 | 30 × 26 m |
| Pickleball Social Garden | pickleball-tree-wells-v001 | 34 × 34 m |
| Garden Tennis Court | tennis-v002 | 38.3 × 56.6 m |
| Bocce Pergola Garden | bocce-v002 | 26.4 × 49 m |
| Rustic Pocket Garden | pocket-native-v003 | 30 × 26 m |
| Railway Meadow Greenway | greenway-native-v002 | 18 × 64 m |
| Inclusive Woodland Playground | inclusive-native-v002 | 38 × 36 m |

The shared native registry uses full measured occupied bounds, including a
small edge allowance where geometry projects beyond the nominal ground.
Exact GLB hashes, content revisions and source recipes are in
`frontend/src/data/nativeParks.json` and its identical backend companion.
The new seed packages are in `seed/classroom-parks/`, with GLBs and thumbnails
in Git LFS. Existing bindings and original source assets were not replaced.

## Construction and review

Reading retains its two pergolas, furniture, paths and tree wells while adding
fuller planting. Pickleball, Tennis and Bocce reuse their latest source assemblies,
with their hashes checked and geometry verification rerun before registration.
This preserves proper sport dimensions and each source-specific social setting.

Pocket and Greenway lock the three original reference views. Pocket retains its
circular lawn, curved timber seat, rustic pergola, west entry and three trees.
All curved ground regions share boundary vertices; an early millimetre seam was
found by walking rays and fixed before acceptance. Greenway retains its curving
trail, rail fragments, meadow edges, bench alcoves and steel truss. Its truss is
a level gateway: it does not create an elevated bridge across surrounding streets.

The first playground recovery did not meet the visual standard and remains
outside the catalogue. The final composition rebuilds the towers, ramp, guards,
slides, swings, sensory panel and shelters as physical metre-scale geometry;
it preserves the original spinner at native scale. Separate ground regions
cover the full 1,368 m² site exactly once. Tree roots have physical soil openings.
Play-equipment safety certification and in-app ramp navigation are not claimed.

Reviewed source and generated evidence live outside Git at
`C:/dev-artifacts/CityPrompt/classroom-parks-2026-09-27/`. Rejected attempts remain
there with their own logs. Only the selected assets, preview, original recipe
and geometry report are promoted to each seed directory.

## Local availability and staging

The searchable picker merges `classroomExpansion.json` with the existing
validation catalogue. Every added card resolves through the same schema-v2
native park lifecycle, with fixed model scale, explicit placement frame,
measured fit, model hashing, shared ground ownership and saved content revision.
No new park fallback or separate rendering path was introduced.

Run `python scripts/stage_native_parks.py --public-dir <public directory>` to
validate all source recipe and asset hashes before writing. It handles the
unchanged original ZIP plus the new repository seed packages, embeds dependencies,
and rejects path escapes or conflicting destination bytes. Hydrate LFS assets
first in a fresh checkout. Staging is required for both development and production.
Restart a running backend after registry changes to reload its finite registry.

The local validation public directory has all 25 required park asset/thumbnail
files staged and the backend has been restarted. No user project was edited.

## Sol acceptance still required

Use disposable prepared-level projects and ordinary student controls. For every
new park check discovery, placement, actual entrance, move/rotate, rejection of
insufficient space, Undo/Redo, save/reopen, aerial and Walk appearance, exact
capture and render preparation. Inspect full native bounds, court counts, tree
roots, furniture and duplicate surfaces. Then try a mixed scene for performance.
Use the same exact asset hashes and record PASS / FAIL / NOT TESTED separately.
No paid provider budget is granted by this document.

## Checkpoint checks

- Focused Vitest: 15 passed. An initial fork-worker startup timeout was rerun
  successfully with one thread worker; no browser was involved.
- Backend native park, staging and ground-partition pytest: 36 passed.
- TypeScript check and production code build: passed. The build used the external
  smoke configuration with bulk public copying disabled; this is not a browser
  acceptance of a production installation.
- Seven delivered assemblies: hashes, embedded dependencies, finite full bounds,
  physical route rays and tree-root support passed. The new Pocket loop includes
  525 sampled route rays; Greenway 672; Playground 273.
- All 25 staged park model/thumbnail URLs returned matching SHA-256 bytes over
  local HTTP. Git diff whitespace checks passed.
