# Park LEGO Batch 8

Batch 8 adds ten exact-reference, parcel-adaptive park families. Each family was selected only after visually comparing all four catalogue variants. Four weak city-labelled sets were rejected because their images showed building context rather than legible park geometry.

## Exact families

1. Reclaimed Industrial Park v0 - linear wharf, native strips, whole cor-ten crane modules.
2. Quarry / Sunken Garden v2 - complete limestone terraces and linked cascade basins.
3. Estate Picnic Grove v1 - repeatable whole oak-table-grill stations around a central lawn.
4. Constructed Wetland v0 - discrete treatment cells and a continuous zig-zag boardwalk.
5. Academic Courtyard v0 - whole raised planted beds, seat ledges and clear cross routes.
6. Campus Pedestrian Spine v0 - continuous walk, paired rain gardens and repeating tree bays.
7. Botanical Garden v3 - complete rose-garden rooms and human-scale timber arbors.
8. Teaching Arboretum v0 - varied specimen trees, interpretive loop, plaques and boulders.
9. Rewilding Zone v1 - irregular pioneer sapling cohorts and complete habitat-log piles.
10. Stormwater Resilience Park v3 - continuous dry rock channel and xeric planting.

## Method

- The selected catalogue image supplies material statistics and compositional evidence; source pixels are never projected onto the site.
- Six PBR roles are generated per family: paver, lawn, asphalt, planting, safety and timber.
- The LEGO builder adapts by adding or removing whole human-scale modules. It does not stretch furniture, trees, cranes, tables, arbors or channels.
- People communicate scale in the references but are not rendered.
- Large surrounding buildings, greenhouses, conservatories and nature centres remain separate building-family work.
- The compiler makes zero image API calls.

## Compact-site adaptation

The catalogue's suggested acreage is compositional guidance, not a literal build requirement. These families now accept compact urban receiving polygons when their whole defining modules can still be arranged legibly. On smaller sites the builder reduces module count and spacing; it never stretches a table, crane, arbor, tree, treatment cell or channel into an oversized object.

## City Prompt browser pilot

All ten variants were selected and compiled one at a time in the same no-boundary City Prompt project, beside a separately generated building family. The irregular receiving polygon measured 1,790 m2 with an approximately 99 m by 37 m oriented footprint. Every trial ended with the exact expected `public_realm_lego.family_id`, `community_3d.state = compiled`, and `community_3d.generator = park_kit`. The run made zero paid image-generation calls.

The browser pilot also exposed and fixed a stale-revision race: rebuilding an adjacent building now refreshes the ground-system revisions held by the Generate to 3D panel before the park compile is submitted.

The mobile comparison sheet is [park_lego_batch8_reference_skin_sheet.jpg](park_lego_batch8_reference_skin_sheet.jpg).
The selector captures are [reclaimed industrial wharf](browser_trials/01_reclaimed_industrial_wharf.png) and [quarry tier cascade](browser_trials/02_quarry_tier_cascade.png).
