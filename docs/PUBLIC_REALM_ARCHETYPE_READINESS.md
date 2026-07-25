# Public-Realm Archetype Readiness

This log tracks the incremental park, plaza, street and pathway workflow:

1. Build a polygon from the catalog's real metric metadata.
2. Compile an exact, ground-seated 3D program in Google Photorealistic 3D Tiles.
3. Generate a photoreal current-view render as the appearance target.
4. Generate or refine the orthographic ground drape without changing the program topology.
5. Compare render and tile scene; add only essential fixed 3D program elements (nets, bridges, conservatories, etc.). Trees, benches and other finishing entourage stay in the render pass unless they are essential to the program.
6. Mark each archetype/variant ready only after scale, topology, grounding, context and visual checks pass.

## Catalog safety net

- Open space: 130 archetypes / 520 variants.
- Streets and paths: 115 archetypes / 355 variants.
- Every current catalog entry now resolves to a non-empty deterministic program instead of silently receiving a generic park or asphalt ribbon.
- Every selected variant is carried into the 3D and render contract.
- Regulation court and field envelopes use authoritative metre dimensions and are never stretched to fill the parcel.
- This safety net prevents broken cards while detailed visual acceptance continues in small daily batches; it does not mean all 875 variants have completed visual QA.

## Batch 01 - 2026-07-18

All three trials use the same validated downtown vacant-lot context. Their polygons are newly constructed from each archetype's catalog width/depth metadata and centered inside that lot.

### Tennis court cluster / Professional Grade

- Trial: `http://localhost:5175/projects/0d73b4ea-31ea-48bf-8590-f1862f950201`
- Polygon: 82 x 46 m, 3,770.8 m2.
- Metadata correction: the previous 40 x 36 m recommendation could not contain the described four-to-six court cluster. The catalog now recommends 82 x 46 m for a regulation four-court complex.
- Fixed topology: four 36.58 x 18.29 m court/run-off envelopes in a two-by-two array plus a 3.0 m central circulation spine.
- Tile result: AI ground drape preserved all four courts and materially improved acrylic, line and surround realism.
- Fixed 3D result: four regulation nets, 3.05 m perimeter fencing and six 12 m floodlight standards are generated after the ground program. Trees and benches remain render-stage finishing elements.
- Render result: photoreal target preserved four courts and added believable fencing, lighting, bleachers and perimeter landscape.
- Status: archetype geometry and Professional Grade v0 accepted for continued use; remaining variants require their own material-pass comparisons.

### Formal civic plaza / Neoclassical Stone

- Trial: `http://localhost:5175/projects/0d73b4ea-31ea-48bf-8590-f1862f950202`
- Polygon: 80 x 75 m, 5,998.0 m2.
- Fixed topology: one central fountain, contiguous accessible event field and clear approaches.
- Tile result: AI drape preserved the basin and produced warm stone paving, dark civic bands and perimeter planting pits.
- Render result: formal stone pattern, central jet, edge allées, civic lighting and furnishing created a strong target without moving the fountain.
- Status: archetype geometry and Neoclassical Stone v0 accepted; later work should add an optional low-cost 3D fountain jet/rim and validate the three alternate material variants.

### Wetland / rain garden / Native Restoration

- Trial: `http://localhost:5175/projects/0d73b4ea-31ea-48bf-8590-f1862f950203`
- Polygon: 80 x 60 m, 4,798.4 m2.
- Fixed topology: three hydraulically connected shallow treatment cells and one exact 2.4 m accessible boardwalk crossing.
- Tile result: AI drape preserved all three distinct cells and the boardwalk while adding shallow water, emergent planting texture and dry meadow edges.
- Render result: convincing water/vegetation mosaic, wetland depth and mature perimeter habitat while retaining the three-cell sequence.
- Status: archetype geometry and Native Restoration v0 accepted; later work should validate inlet/outlet expression and the three alternate ecological variants.

## Cost and verification

- Batch 01 requested six current-view preview images and three optional AI ground-drape images (nine image calls total). No image-to-3D or building-model generation was used.
- Exact dollar cost is provider-dependent and is not inferred from call count; the batch stayed within the user's stated $10 limit.
- Frontend test suite: 45 files / 368 tests passed.
- Production TypeScript/Vite build passed (3,354 modules); existing bundle-size warnings remain.

## Next batch candidates

- Pickleball courts (regulation 18.29 x 9.14 m envelopes) across two material variants.
- Playground/adventure versus nature-play comparison.
- Main Street Complete and protected bidirectional cycle street, including context connection at parcel edges.

## Batch 02 - 2026-07-18

The complete screenshot audit is stored in [`artifacts/park-drape-comparisons/2026-07-18-batch-02`](../artifacts/park-drape-comparisons/2026-07-18-batch-02/README.md).

### Wetland / rain garden — Native Restoration refinement

- Trial: `http://localhost:5175/projects/0d73b4ea-31ea-48bf-8590-f1862f950203`
- The exact profile now authors three larger treatment cells and a closed-loop boardwalk with cross-link and southern access spur.
- The AI drape is required to retain that network instead of replacing it with a single straight crossing.
- Status: materially closer to the render target; topology accepted, but the Tiles material result remains more rectilinear and diagrammatic than the photoreal reference.

### Classical Japanese garden

- Trial: `http://localhost:5175/projects/0d73b4ea-31ea-48bf-8590-f1862f950301`
- Polygon: approximately 70 × 70 m.
- Fixed topology: one pond, one loop walk, one gravel court, stepping-stone route and one red bridge.
- The first render pair failed by importing an unrelated European parterre program. Exact profiles now ignore incompatible variant program prose and catalog style imagery.
- The corrected render and `japanese-garden-v4` Tiles drape share the same program; the bridge is painted into the drape and reinforced by a low live 3D bridge element.
- Status: topology, scale, grounding and essential fixed-program gates pass. Vegetation richness remains a render-stage difference by design.

### Nature play / organic — Nature-Based

- Trial: `http://localhost:5175/projects/0d73b4ea-31ea-48bf-8590-f1862f950302`
- Polygon: 40 × 30 m.
- Fixed topology: two linked sandy play clearings, an internal loop and natural rill/log/boulder play cues.
- The Tiles drape correctly remains inside the metric footprint. The generated render landscaped well beyond the polygon, so it fails the scale/footprint gate even though its internal design language is useful.
- Status: Tiles program accepted; render-stage site masking and camera framing must be corrected before the appearance-match gate can pass.

### Batch 02 cost and verification

- Ten image-generation calls were used: six current-view render images (three two-image batches) and four ground-drape generations/retries. Exact dollar cost is provider-dependent and is not inferred from call count.
- Focused park-ground/profile tests and the production frontend build are the required release checks for this batch.

## Batch 03 - 2026-07-18

The complete same-footprint screenshot audit is stored in [`artifacts/park-drape-comparisons/2026-07-18-batch-03`](../artifacts/park-drape-comparisons/2026-07-18-batch-03/README.md).

All three trials clone the user's exact 144 × 76.8 m (9,694.6 m²) parcel and terrain context.

### Pond / Lake — Formal Reflecting

- Trial: `http://localhost:5175/projects/0d73b4ea-31ea-48bf-8590-f1862f950401`
- The user-authored render produced a softened rectangular pond with a tree-lined perimeter promenade.
- The prior catalog fallback drape retained an ellipse and introduced twin jets, so appearance/topology matching did not pass.
- `pond-lake-v3` now locks one rounded-rectangular water body and one continuous 3 m promenade for the next regeneration.
- Status: grounding and footprint pass; appearance/topology require one v3 regeneration and screenshot comparison.

### Botanical Garden — Woodland Naturalistic

- Trial: `http://localhost:5175/projects/0d73b4ea-31ea-48bf-8590-f1862f950403`
- The render and Tiles drape preserve the same interpretive loop, compact conservatory pad and three distinct collection rooms.
- Status: ground topology, material appearance, scale and grounding pass. Mature canopy remains final-render finishing so collection beds stay legible in Tiles.

### Urban Forest — Rewilded Urban

- Trial: `http://localhost:5175/projects/0d73b4ea-31ea-48bf-8590-f1862f950402`
- The drape preserves the continuous low-impact loop, two daylight clearings and a convincing woodland floor.
- The render's volumetric mixed canopy is the defining program feature and is necessarily absent from a ground-only drape. The current single generic tree asset is not sufficient for a photoreal forest library.
- The parcel is 3.2 m shallower than the catalog's nominal 80 m minimum, so this is explicitly retained as a boundary stress test.
- Status: ground topology, scale and grounding pass; full appearance fails pending a realistic species/age/crown canopy system.

### Batch 03 cost

- Nine image-generation calls were used: six current-view render images and three ground drapes. One call remained unused under the renewed ten-call ceiling.

## Batch 04 - 2026-07-18

The complete same-footprint screenshot audit is stored in [`artifacts/park-drape-comparisons/2026-07-18-batch-04`](../artifacts/park-drape-comparisons/2026-07-18-batch-04/README.md). All trials use the same 144.0 x 76.8 m (9,694.6 m2) parcel.

### Accepted on this footprint

- Pond / Lake - Formal Reflecting: `pond-lake-v3` now preserves one softened rectangular basin and one continuous 3 m promenade with no invented fountains.
- Neighborhood Park - Natural Meadow: `neighborhood-park-v4` locks the social lawn, complete walking circuit, four gateway links, meadow/rain-garden rooms, playground pad and pavilion pad. Two corrective drape iterations removed the disconnected path islands and invented central paving.
- Stormwater Pond - Naturalistic: `stormwater-retention-pond-v1` closely matches the render's single basin, wet shelf, inlet, outlet/service pad and dry access.
- Sports Complex - Professional Grade: `sports-field-complex-v3` is the strongest render/Tiles match and preserves a 100 x 64 m football/soccer pitch plus three 36.58 x 18.29 m tennis safety envelopes without scale-to-fit distortion.

### Not yet accepted

- Linear Greenway - Daylighted Creek: grounding passes, but the generic greenway drape produces several broad water bands where the render has one creek corridor. The test parcel is 16.8 m deeper than the catalog maximum. This variant needs its own fixed creek guide and an explicit footprint-compatibility rule.

### Batch 04 cost

- Fifteen image calls were used: eight current-view render images and seven ground-drape generations/retries. The 100-call authorization was treated as a hard ceiling rather than a spending target.
