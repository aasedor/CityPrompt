# Park LEGO Batch 7

Batch 7 adds ten exact-reference, executable park families. Each family was
selected only after reviewing all four catalogue variants. The chosen image is
the source of truth for spatial hierarchy, human scale, material palette and
landscape character; it is not projected onto the site.

## Families

| Family | Exact catalogue selection | Site-adaptation rule |
| --- | --- | --- |
| English regional landscape | `regional_park_v0` | Add whole meadow rooms, tree groups and secondary loops; keep pond, bridge and path widths human-scaled. |
| Munich chestnut beer garden | `beer_garden_v0` | Add complete trestle-table rows and canopy bays; never stretch furniture. |
| Intimate sunken courtyard | `sunken_plaza_v0` | Preserve one lower court, three step approaches, accessible edge and central fountain. |
| Modernist terraced cascade | `stepped_terraced_plaza_v3` | Add or remove complete terrace bands while preserving the three-basin water axis and wrap ramp. |
| Open festival lawn square | `market_square_v1` | Keep one contiguous lawn; repeat complete vendor pads, utility bollards and shade anchors at the edge. |
| Maritime boardwalk | `promenade_boardwalk_v0` | Repeat complete rail, lamp and bench bays along one continuous accessible promenade. |
| Formal reflecting fountain | `fountain_water_feature_v1` | Keep one complete basin and continuous coping; add or remove symmetric jet pairs. |
| Natural swimming pond | `swimming_pool_complex_v0` | Preserve the geometric lap basin and deck inside a distinct organic regeneration pond. |
| Tallgrass prairie preserve | `nature_preserve_v1` | Habitat stays dominant; add whole prairie drifts and trail loops without widening paths. |
| Lake swimming beach | `riverfront_park_beach_v1` | Adapt shoreline and sand length while dock, float, kayak rack and safety clearances retain human scale. |

People in the reference images were used only as scale and use evidence. No
people are part of the LEGO families. Large buildings and surrounding roads
remain separate families; the lake beach therefore reserves a bathhouse pad
without generating the bathhouse.

## Material method

Each exact reference produces six stationary PBR roles: `paver`, `lawn`,
`asphalt`, `planting`, `safety` and `timber`. Reference crops provide colour
and tonal statistics. Role-specific procedural structure creates tileable
albedo, normal, roughness and ambient-occlusion maps. This avoids monochrome
surfaces without copying people, buildings or perspective distortion into the
ground.

- Paid image calls: `0`
- Source pixels projected onto geometry: `false`
- Generated files: `31` per family (`310` total)
- Comparison sheet: `park_lego_batch7_reference_skin_sheet.jpg`

## Reproduction

```powershell
python tools/park_skin_compiler/generate_park_archetype_batch7_skins.py --dry-run
python tools/park_skin_compiler/generate_park_archetype_batch7_skins.py --archetype beer-garden-munich-chestnut --out artifacts/batch7_skin_pilot
python tools/park_skin_compiler/generate_park_archetype_batch7_skins.py
python tools/park_skin_compiler/render_park_archetype_batch7_sheet.py
```
