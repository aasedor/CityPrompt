# Park LEGO Batch 10

This checkpoint adds ten exact, city-specific park archetype families. All four catalogue views for every parent were reviewed before choosing the representative variant. The references supply composition, scale, material, planting, and use evidence; their pixels are not draped onto the site.

## Families

| Archetype and exact variant | LEGO family | Parcel-aware composition |
| --- | --- | --- |
| Amsterdam Hofje Garden — Variant 1 (`amsterdam_hofje_garden_v0`) | `park_amsterdam_hofje_garden_v0` | One enclosed gravel-cross room, four complete hedge/flower beds, central pump or well, modest shade trees, and one gate |
| Amsterdam Plein — Variant 1 (`amsterdam_plein_v0`) | `park_amsterdam_plein_v0` | Open brick civic centre with complete edge market-stall, tree, bench, and bicycle-rack bays |
| Vondelpark Garden — Variant 4 (`amsterdam_vondelpark_v3`) | `park_amsterdam_vondelpark_pavilion_v3` | Whole lawn, grove, pond, bridge, winding-path, and modest pavilion-terrace rooms |
| Eixample Interior Courtyard — Variant 1 (`barcelona_pati_interior_v0`) | `park_barcelona_pati_green_v0` | Reclaimed courtyard with fountain, shaded loop, Mediterranean planting rooms, benches, and a compact play bay |
| Chamfer Plaza — Variant 3 (`barcelona_placa_xamfra_v2`) | `park_barcelona_xamfra_corner_v2` | Chamfer-aware octagonal tile room, clear diagonal route, one mature tree, and complete café-table clusters |
| Barcelona Superblock — Variant 2 (`barcelona_superilla_v1`) | `park_barcelona_superilla_green_v1` | Continuous pedestrian/cycle route with added whole coloured activity rooms, planter-tree bays, and social/play furniture |
| Calgary Prairie Urban Plaza — Summer Market Square (`calgary_prairie_plaza_v1`) | `park_calgary_prairie_market_v1` | Open event centre, shallow pool axis, whole timber market bays, native-grass planters, and wind screens |
| Prince's Island Park — Summer Festival Ground (`calgary_princes_island_v0`) | `park_calgary_princes_island_festival_v0` | Festival lawn, cottonwood trail network, connected wetland, repeatable boardwalk bays, and one modest stage shelter |
| Mount Royal Park — Variant 3 (`montreal_mount_royal_v2`) | `park_montreal_mount_royal_grove_v2` | Continuous switchback ascent, whole maple cohorts, granite terraces, and a terrain-seated belvedere |
| Montréal Neighbourhood Square — Variant 4 (`montreal_square_v3`) | `park_montreal_neighbourhood_square_v3` | Geometric gravel loop/cross, one central fountain, low iron perimeter, seasonal beds, and whole maple-bench bays |

## Method

- The drawn park remains a plain, labelled planning polygon. Detailed skins and 3D depth appear only after **Generate to 3D** persists the exact `public_realm_lego` recipe.
- Each compiler family adds or removes complete landscape rooms and kit modules to fit the parcel. It does not stretch a reference plan to the boundary.
- Six PBR material roles are generated per family: paver, lawn, asphalt/secondary hardscape, planting, safety/accent surface, and timber. Reference-derived colour statistics are combined with repeat-safe procedural detail, roughness, and normals.
- People are used only as scale and use evidence. No people are emitted. Large buildings, skyline objects, vehicles, and enclosing blocks are excluded from park assemblies.
- The ten assemblies use terrain-relative placement so their surfaces and kit remain seated on the parcel rather than floating or doubling.
- This batch made zero paid image-generation calls and zero Meshy calls.

## City Prompt validation

All ten exact variants were selected and generated one at a time in project `20c08c19-8bf3-48ab-b9d1-62482b46a66e`. The same approximately 99 × 37 m (1,793 m²) park polygon was overwritten between trials, while a separate mid-rise LEGO building remained in the scene. Every fresh-snapshot run reported:

- `1 buildings · 1 parks · 0 streets`
- park state `compiled`
- `No family 0`
- an archetype-driven procedural or archetype-owned ground contract with no image API call

The initial Amsterdam Plein rebuild correctly rejected one stale client revision. Reloading the authoritative project snapshot and retrying immediately passed; the remaining sequential trials used that intended concurrency-safe workflow and had no stale-revision failures.

The catalogue category metadata was corrected so all ten parents are reachable in their intended City Prompt picker groups. See [city_prompt_trial_results.json](./city_prompt_trial_results.json) for the per-family ledger and [park_lego_batch10_reference_skin_sheet.jpg](./park_lego_batch10_reference_skin_sheet.jpg) for the reviewed reference/skin comparison.

## Catalogue checkpoint

After Batch 10, the machine-readable matrix records 130 parents and 520 variants: 82 exact variants, 18 intentional shared-family mappings, 420 variants still unmapped, and 40 parents still fully uncovered. This is a bounded checkpoint toward catalogue completion, not the final catalogue.
