# Treetop and rose parks — local catalogue pair

Two new parks are available in the local validation catalogue. Both have
authored planting, actual 3D stairs and walking surfaces tied to their exported
models. They reuse the existing native-park placement and walking systems.

| Park | Native plot | Main experience | Triangles |
| --- | --- | --- | --- |
| Treetop Walk Park | 56 × 64 m | Twin stairways, 4.2 m elevated circuit, shaded lookout and ground-level resting glade | 816,558 |
| Terraced Rose Garden | 50 × 64 m | Three rose terraces, paired stairways rising 2.4 m, fountain and pergola | 741,104 |

Rose requires 50.1 × 64 m of placement space to include projecting details.
Parcel resizing preserves each complete assembly's authored scale. These are
prepared-level park concepts; the raised routes use stairs.

## Quality and corrections

Seven views of each reimported GLB were reviewed, including three pedestrian
views. Aerial and entrance views were compared with the approved
`conservatory-v013` visual benchmark. These are original designs with an author
visual pass; independent human approval and public activation remain pending.

The treetop pilot gained grounded stair supports, dense woodland borders and
closely spaced guard balusters. The rose garden gained guarded terrace edges,
smaller blooms, fuller foliage and twelve edged tree wells with paving openings.
Detailed rose shrubs are consolidated by material to keep export practical.
Earlier candidates remain outside the source tree and are not catalogue choices.

## Verification

- 8,154 offline movement samples passed, in both directions, with a 0.44 m
  torso-clearance sweep against the actual GLB. Maximum tread rise is 0.15 m.
- Both complete main circuits passed in City Prompt using ordinary keyboard
  walking. Measured rises were 4.2 m and 2.4 m. Return-to-entrance and exit worked.
- Catalogue search, card selection, placement, parcel resize/rotation, move,
  Undo, Redo and reload passed. Saved geometry and exact model selections agree.
- All 1,422 treetop and 291 rose mesh instances are visible at their authored
  scales. The settled pair scene reports no grounding issues or browser errors.
- An undersized rotated treetop parcel was rejected without changing the saved
  park; enlarging it recovered through the normal controls.
- 48 focused frontend tests, 44 backend native-park tests and TypeScript pass.
- All 27 previous native layouts and prior expansion entries are unchanged.

The exact hashes, measurements, browser results and limitations are in
`TREETOP_ROSE_PARKS_2026-10-01.json`. Each seed package includes its own runtime
review. These bounded checks do not guarantee every possible input sequence.
Natural/sloped terrain, public street connections, paid images and export file
downloads were not tested for this pair. No public deployment or push occurred.

## Source and generated output

Reviewed deliverables are in `seed/classroom-parks/garden-treetop-v003` and
`seed/classroom-parks/garden-rose-v005`: exact models, modules, authoring snapshots,
recipes, seven renders, offline checks and runtime reviews. Model/image binaries
use Git LFS. Catalogue thumbnails use the authoritative openspaces directory.

Full experiments, logs and browser screenshots remain externally at
`C:/dev-artifacts/CityPrompt/treetop-rose-parks-2026-10-01`.
Hydrated public GLBs are generated local copies, not additional source models.
Pre-existing unrelated street images and hydrated assets are preserved.

## Reproduction

Run Blender with `tools/public_realm_assets/build_treetop_rose_parks.py`,
`--kind treetop` or `--kind rose`, an explicit `--kit` and a new `--output`
directory. Use `--dry-run` first. Each package records exact source/kit hashes;
the included authoring snapshots reproduce its retained version.

Run `node tools/public_realm_assets/verify_climbable.mjs <package>` and review
the seven renders. Then run `scripts/register_treetop_rose_parks.py --package
<package> --dry-run`, followed by registration without `--dry-run`.
Registration verifies exact model, module, source and review hashes, preserves
prior bindings, and retains a registry backup externally. Hydrate the public
assets and restart Vite after adding files because public watching is disabled.
