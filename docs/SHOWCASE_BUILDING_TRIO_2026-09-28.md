# Three reference-locked showcase buildings

Finite local additions requested for a colleague demonstration. These use the current RLASM v6.1 architectural-clay tier: complete native geometry, physical openings, source-specific proportions and a restrained material palette. They are not textured keeper approvals. Browser placement, Walk, editing and image capture are **NOT TESTED**, as requested. No remote publication is authorized by this work.

| Building | Candidate | Actual exported width × depth × height |
|---|---|---|
| Grand Iron & Glass Market | `showcase-market-clay-v006` | 35.25 × 48.48 × 19.09 m |
| Gilded Terracotta Tower | `showcase-tower-clay-v005` | 32.78 × 29.32 × 68.60 m |
| Living-Roof Aquatic Centre | `showcase-aquatic-clay-v004` | 38.36 × 56.74 × 16.60 m |

The market includes eighteen stocked stalls, two occupied galleries, connected stairs, a glazed barrel vault with physical panel seams, a ridge monitor, brick aisles and side entrances. The tower has seventeen occupied storeys, projecting centre bays, re-entrant terraces, narrow recessed windows, broad terracotta piers, sunburst relief, a dark retail plinth, cream mezzanine and a constructed gilded lantern. Its crown braces bear on octagonal frame receivers; the entrance canopy bears on granite piers. The aquatic centre includes an eight-lane pool, full deck, changing wing, a 28 m glulam vault beside a 9 m planted wing, eight vault and four wing rooflights, three single-slope PV groups, two ventilation towers and a four-metre-deep entrance porch.

Dimensions are conceptual reference inferences, not a survey. The registered plots include clearance beyond measured model bounds. All three use fixed native placement: a larger surrounding plot retains the same building; an insufficient plot must not squash the model or substitute another design. Existing model identities and saved bindings are preserved.

## Exact asset record

- Market: `ea1d0d55ccfe5de9ce74bd8a8e2b998748f045728bd674195cb1f6f1323e0074` — 97,412 triangles, 12 runtime meshes.
- Tower: `a0b4f53281c43b0cd3a98f057a5da4ea0de5f56476e7a6227074d79e61a54b80` — 217,128 triangles, 9 runtime meshes.
- Aquatic centre: `f81cd1aadb24768d513cea6a87fa9ff26e5ec5736349d195d195c257f0ed9041` — 115,814 triangles, 15 runtime meshes.

Every GLB has embedded geometry/materials, zero texture or image dependencies and zero measured bounds change after export/reimport. Photographic picker heroes are separately preserved under immutable `showcase-v1-*` names; they are never baked into model geometry. Existing reference filenames are untouched.

`seed/classroom-buildings/showcase-selection.json` records the finite selection and pending runtime status. The canonical clay library records exact GLB, source and independent-review hashes. The promotion tool requires a full independent architectural-clay pass for each exact candidate, with zero P0/P1 findings, before local trial registration. No self-approval or completed-catalogue flag is introduced.

## Evidence and reproduction

Complete authoring files, original source locks, rejected versions and 43 final reimported-GLB views are outside the source tree:

`C:/dev-artifacts/CityPrompt/showcase-nine-2026-09-27/buildings/`

Each final package includes three locked source views, full-resolution orthographic/oblique/detail/interior or entrance renders, a phone board and the independent review. Earlier failed candidates remain intact.

- Lock sources with `tools/showcase_building_trio/prepare.py`.
- Run the finite Blender builder `tools/showcase_building_trio/build.py --kind <kind> --lock <lock.json> --output <new external directory> --version <number>`, first with `--dry-run`.
- Register a fully reviewed package with `scripts/showcase_buildings.py --package <delivery>`.
- Stage the three photographic reference sets with `scripts/showcase_buildings.py --stage-public <public directory>`.
- Install only the selected trio through the existing `scripts.classroom_buildings.install` local-only, additive, hash-readback installer. It requires an existing local owner and refuses different existing bindings or stored model bytes.

All three final candidates passed separate holistic architectural-clay review with zero unresolved P0/P1 findings. Verification passed: 51 Python promotion/compilation tests, 11 focused frontend catalogue/placement tests and TypeScript type-check. The tests exposed and corrected a sibling-card restore bug: canonical building lookup now matches both parent and exact variant. Focused checks cover promotion integrity, exact native compilation, enlarged plots, undersized-plot rejection, distinct picker cards and stable revision bindings. Browser validation and human visual activation remain separate future gates.
