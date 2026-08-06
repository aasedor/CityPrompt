# Archetype-Owned Park LEGO - Batch 5

Batch 5 promotes ten additional catalogue v0 archetypes to deterministic,
reference-owned Public Realm LEGO programs. Preview remains a flat labelled
polygon. Generate to 3D resolves the exact ground grammar, stationary PBR skin,
vertical park kit and bounded microdetail without an image API call.

The catalogue ranking and recommended next queue are recorded in
[FAMILY_SCAN.md](FAMILY_SCAN.md).

| Exact variant | Site-adaptive composition rule | Vertical 3D kit |
|---|---|---|
| Disc Golf / Wooded Championship | Pair nine whole tees and targets along non-crossing wooded corridors | Concrete tees and galvanized chain baskets |
| Bocce / Italian Piazza | Keep one complete 27.5 x 4 m lane; social edge remains outside | Stone containment and vine pergola |
| Climbing / Competition Boulder | Walls vary within one complete 22 x 17 m fall zone | Angular overhangs and colour-coded holds |
| Mini Golf / Classic Themed | Retain nine separate putting lanes and connected sequence | Windmill, loop and castle obstacles |
| Beach Volleyball / Competition | Keep one complete 24 x 16 m envelope; add only whole envelopes on larger sites | Net, padded posts and referee stand |
| Pollinator Meadow / Prairie Restoration | Adapt contiguous habitat drifts around one connected mown loop | Interpretive stations and layered microdetail |
| Urban Orchard / Heritage Apple | Add or remove whole trees/rows while retaining harvest access | Fruit-tree rows, small shed pad and pergola edge |
| Bioswale / Streetside | Preserve downhill flow through three linked treatment cells | Curb grates, crossings and check-dam cues |
| Sculpture Garden / Museum Court | Keep separate 360-degree viewing rooms around five works | Plinths and varied abstract sculpture set |
| Labyrinth / Classical Stone | Preserve one legible seven-circuit entrance-to-centre route | Hedge rings and central stone bench |

People in source images are scale and use evidence only. Large buildings are
excluded because City Prompt compiles those through separate building LEGO
families. The skin compiler samples reference statistics and synthesizes
stationary role-specific PBR materials; source pixels are never projected onto
site geometry.

## Reproduce

```powershell
python tools/park_skin_compiler/generate_park_archetype_batch5_skins.py --dry-run
python tools/park_skin_compiler/generate_park_archetype_batch5_skins.py
python tools/park_skin_compiler/render_park_archetype_batch5_sheet.py
```

The mobile review sheet is
`park_lego_batch5_reference_skin_sheet.jpg` in this directory.
