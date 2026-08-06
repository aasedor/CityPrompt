# Park LEGO Batch 9

This batch adds ten exact park archetype families selected after reviewing all four catalogue views for each parent archetype. The reference images provide evidence for composition, scale, material variation, and kit selection. Their pixels are not draped onto the site.

## Families

| Archetype and exact variant | LEGO family | Parcel-aware composition |
| --- | --- | --- |
| Urban Pocket Park — Rustic Timber & Gravel (`urban_pocket_park_v0`) | `park_urban_pocket_rustic_v0` | Gravel room, whole timber seating/deck modules, planting pockets, and a clear pedestrian spine |
| Neighborhood Park — Urban Contemporary (`neighborhood_park_v3`) | `park_neighborhood_contemporary_v3` | Central flexible lawn, loop/cross paths, play and social rooms, perimeter shade planting |
| Cemetery / Memorial Grounds — Classical Formal (`cemetery_memorial_grounds_v0`) | `park_cemetery_classical_v0` | Ordered memorial rows, axial lane, quiet lawn rooms, and formal tree structure |
| Courtyard Plaza — Contemporary Urban (`courtyard_plaza_v1`) | `park_courtyard_linear_water_v1` | Linear water axis, paved gathering room, seat walls, planting bands, and uncluttered circulation |
| Street Plaza / Parklet — SF Parklet (`street_plaza_parklet_v1`) | `park_parklet_sf_timber_v1` | Narrow timber platform bays, planters, guard edge, and complete seating modules rather than stretched props |
| Jardin à la Française — Variant 2 (`parisian_jardin_v1`) | `park_french_parterre_axis_v1` | Central water axis, mirrored parterre rooms, gravel promenades, clipped planting, and movable-chair cues |
| London Garden Square — Variant 2 (`london_garden_square_v1`) | `park_london_railed_square_v1` | Continuous iron perimeter, gated entry, central lawn, gravel circuit, and mature plane-tree rhythm |
| Halifax Public Gardens — Rose Garden Peak (`halifax_public_gardens_v0`) | `park_halifax_rose_bandstand_v0` | Whole rose-bed rooms, serpentine promenade, ornate bandstand, gate, and Victorian enclosure |
| Picturesque Olmsted Park — Central Park Multi-Landscape (`picturesque_olmsted_park_v3`) | `park_olmsted_multilandscape_v3` | Connected meadow, grove, water-edge, and winding-path rooms scaled to the available polygon |
| Hilltop Topographic Park — Pacific Terraced Viewpoint (`hilltop_topographic_park_v3`) | `park_hilltop_viewpoint_v3` | Contour-following terraces, overlook deck, retaining steps, native planting bands, and a legible ascent |

## Method

- The drawn park remains a plain labelled planning polygon. The detailed skin, planting, and kit are mounted only after **Generate to 3D** persists an exact `public_realm_lego` recipe.
- The compiler chooses complete spatial modules and changes their count, spacing, and orientation to fit the polygon. It does not uniformly stretch a reference layout or a single regulation element.
- Six material roles are generated per family: paver, lawn, asphalt, planting, safety surface, and timber. Colour statistics come from the exact selected reference; procedural structure supplies repeat-safe texture, roughness, and normals.
- People in the references are scale and use evidence only. No people are emitted. Large buildings remain separate LEGO families and are not emitted by a park assembly.
- Raw and adjacent unreviewed variants fail closed to generic planning display until their own exact family is compiled.
- This batch made zero paid image-generation calls and zero Meshy calls.

## City Prompt validation

All ten families were selected and generated one at a time in project `20c08c19-8bf3-48ab-b9d1-62482b46a66e`. The shared trial polygon is approximately 99 × 37 m (1,793 m²), with one separate compiled mid-rise LEGO building retained in the project. Every run reported:

- `1 buildings · 1 parks · 0 streets`
- park state `compiled`
- `Archetype-owned skin and metric 3D depth kit; no AI drape or generic park dressing`

The Paris, London, and Halifax catalogue records were also corrected to the `specialty_gardens` category so their exact variants are reachable in the City Prompt picker.

See [city_prompt_trial_results.json](./city_prompt_trial_results.json) for the per-family ledger and [park_lego_batch9_reference_skin_sheet.jpg](./park_lego_batch9_reference_skin_sheet.jpg) for the reviewed reference/skin comparison.
