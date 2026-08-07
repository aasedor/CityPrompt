# Park LEGO Batch 13

Ten formerly uncovered landscape and waterfront parents now have exact executable LEGO families. Every parent’s four catalogue views were reviewed before selecting the family anchor. Reference people establish scale only and are not rendered; architectural objects—including the lighthouse and pier buildings—remain separate from the park assembly.

| Exact variant | Family | Composition retained |
| --- | --- | --- |
| Intensive Rooftop Garden | `park_rooftop_intensive_garden_v0` | Raised garden rooms, accessible loop, wind edge, modest pergola |
| Healing Garden | `park_community_healing_garden_v2` | Therapeutic beds, accessible loop, seating niches |
| Forested Rail-Trail Buffer | `park_greenbelt_rail_trail_v1` | Continuous multi-use trail, woodland cohorts, rest bays |
| Heathland Moor Trail | `park_foothill_heathland_trail_v2` | Terrain-seated ridge path, heather cells, viewpoints |
| Pacific Floating-Dock Marina | `park_marina_pacific_dock_v2` | Public quay, modular dock fingers, clear navigation channel |
| Brooklyn Park Pier | `park_working_pier_brooklyn_park_v3` | Continuous deck, whole lawn/planting rooms, view edge |
| Floating Meadow Loop | `park_floating_meadow_loop_v2` | Whole meadow islands and continuous boardwalk loop |
| Pacific Lighthouse Headland | `park_lighthouse_pacific_headland_v2` | Cliff-setback trail, grove cells, separate lighthouse reservation |
| Modern Timber Lakefront Deck | `park_lake_edge_timber_deck_v2` | Continuous deck, step-seat bays, rain planters |
| Naturalized Stormwater Creek | `park_stormwater_natural_creek_v0` | Continuous low-flow channel, floodplain cells, trail and bridges |

The compiler adapts by repeating or omitting complete dock fingers, planting rooms, rest bays, islands, and crossings—not by stretching the reference plan. Paid image API calls: 0. Meshy calls: 0.

All ten were generated one at a time in City Prompt project `20c08c19-8bf3-48ab-b9d1-62482b46a66e` on the shared 99 × 37 m park polygon, retaining its separate mid-rise LEGO building. Every final run reported `1 buildings · 1 parks · 0 streets`, park state `compiled`, `No family 0`, and the archetype-owned no-drape contract. The Healing Garden trial also exposed and fixed a generic resolver bug that previously rewrote non-numeric catalogue variant IDs.

See [city_prompt_trial_results.json](./city_prompt_trial_results.json) and [park_lego_batch13_reference_skin_sheet.jpg](./park_lego_batch13_reference_skin_sheet.jpg).

After this checkpoint the deterministic matrix contains 130 parents, 520 variants, 117 partial parents, 10 fully uncovered parents, 112 exact variants, 18 reviewed shared mappings, and 390 unmapped variants.
