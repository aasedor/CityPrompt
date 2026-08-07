# Park LEGO Batch 11

Ten previously uncovered city archetypes now have exact park LEGO families. All four catalogue views for each parent were reviewed; the selected view supplies scale, ground, planting, furniture, and spatial-composition evidence only. Buildings and people visible in those references are deliberately excluded.

| Exact variant | Family | Composition retained |
| --- | --- | --- |
| Place Royale V3 | `park_paris_place_royale_v2` | Open cobbled centre, four approaches, formal edge trees |
| Square Parisien V4 | `park_paris_square_tree_grid_v3` | Gravel social room, tree grid, perimeter bench bays |
| London Circus V2 | `park_london_circus_planted_v1` | Radial geometry, planted island, curved seating, cycle ring |
| New York Pocket Park V1 | `park_newyork_pocket_water_v0` | Water rill, whole seat-planter bays, compact pergola |
| New York Community Garden V4 | `park_newyork_community_greenhouse_v3` | Raised-bed grid, accessible path, compost/tool bay, modest greenhouse |
| Vancouver Seawall V3 | `park_vancouver_seawall_cycle_v2` | Continuous separated cycle/walk pair, seawall, view bays |
| Vancouver Beach Park V1 | `park_vancouver_beach_pavilion_v0` | Shore-parallel routes, dune planting, view lawn, modest pavilion |
| Toronto Ravine — Summer Creek Shade | `park_toronto_ravine_creek_v1` | Creek, continuous trail, bridge crossings, grove cohorts |
| Toronto Urban Square — Summer Market Plaza | `park_toronto_urban_market_v1` | Flexible centre, complete vendor and rain-planter bays |
| Halifax Coastal Park — Foggy Morning Path | `park_halifax_coastal_fog_path_v2` | Granite path, coastal grove cohorts, boardwalk lookout |

The compiler adds or removes complete rooms and kit modules to fit the polygon; it never scales an entire reference plan uniformly. The ten parents were also remapped from orphaned city-category IDs into standard City Prompt picker groups.

All ten were generated one at a time in project `20c08c19-8bf3-48ab-b9d1-62482b46a66e` on the shared 99 × 37 m park polygon, with the separate mid-rise LEGO building retained. Every run reported `1 buildings · 1 parks · 0 streets`, park state `compiled`, `No family 0`, and `Archetype-owned skin and metric 3D depth kit; no AI drape or generic park dressing`. Paid image API calls: 0. Meshy calls: 0.

See [city_prompt_trial_results.json](./city_prompt_trial_results.json) and [park_lego_batch11_reference_skin_sheet.jpg](./park_lego_batch11_reference_skin_sheet.jpg).

After this checkpoint the matrix has 130 parents, 520 variants, 97 partial parents, 30 fully uncovered parents, 92 exact variants, 18 reviewed shared mappings, and 410 unmapped variants.
