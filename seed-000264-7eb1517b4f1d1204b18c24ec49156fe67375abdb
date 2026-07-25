# City Prompt LEGO Library QA

Date: 2026-07-18  
Project: `effbaeae-2676-4d4b-9d89-f53afe12cf59`  
Temporary-zone marker: `properties.qa_batch = "all-imported-lego-2026-07-18"`

## Scope

This pass exercises every LEGO family currently imported into the local model
library. It does not cover catalogue archetypes that do not yet have an
imported module family.

- 11 imported families
- 59 module GLBs
- 59/59 asset requests returned HTTP 200
- 11/11 native-scale assembly plans succeeded
- 11/11 recipes were placed and persisted in City Prompt
- No matching Vite load errors after the scene settled
- The original Chateauesque parcel was not modified

## Family results

| Family | Native test | Floors | Instances | Assembled tris | Result | Visual note |
| --- | ---: | ---: | ---: | ---: | --- | --- |
| `calgary-modern-infill-house` | 7 x 13 m | 2 | 3 | 720 | Technical pass / legacy-quality warning | Loads and stacks correctly, but geometry is too sparse for close architectural viewing. |
| `chateauesque-grand-railway-hotel` | 55 x 36 m | 6 | 7 | 35,726 | Pass | Detailed roof and facade survive Google Tiles; dark materials can crush to black at the current oblique lighting angle. |
| `chateauesque-grand-railway-hotel-large` | 90 x 40 m | 4 | 5 | 39,598 | Pass | Best large-parcel integration in this batch; appropriate for the existing hotel site. |
| `contemporary-midrise-residential` | 25 x 18 m | 5 | 6 | 396 | Technical pass / legacy-quality warning | Baked facade reads well at city scale, but silhouette and depth remain box-like close up. |
| `contemporary-townhouse-courtyard` | 8 x 12 m | 3 | 4 | 149,644 | Pass / performance warning | Detailed geometry loads, but the family is 30.58 MB across its seven source modules and needs compressed LODs. |
| `courtyard-family-housing` | 14 x 14 m | 3 | 4 | 72,172 | Pass / performance warning | Courtyard and roof articulation read correctly; source family is 19.02 MB. |
| `hotel-particulier` | 18 x 22 m | 3 | 4 | 2,276 | Technical pass / legacy-quality warning | Correct stack and scale, but facade depth and roof silhouette are insufficient for the target realism. |
| `minimalist-courtyard-block` | 25 x 25 m | 4 | 5 | 159,936 | Pass / performance warning | Strongest small-block geometry in the grid; source family is 18.67 MB and needs city LODs. |
| `nordic-timber-charred-wood` | 20 x 16 m | 5 | 6 | 140 | Technical pass / material warning | Loads correctly, but the charred facade becomes nearly black and the extremely low-poly massing reads as a box. |
| `nordic-timber-midrise` | 20 x 16 m | 5 | 6 | 396 | Technical pass / legacy-quality warning | Baked timber facade is legible, but geometry lacks recesses, balconies and corner depth. |
| `rndsqr-terraced-mixed-use-midrise` | 38 x 30 m | 6 | 7 | 420 | Technical pass / legacy-quality warning | Attractive baked glazing and green roof at city scale; close-range geometry remains nearly planar. |

## Cross-family findings

1. **Opaque site-preparation surfaces are the largest integration defect.**
   Every test polygon produces a large white slab over Google Tiles. The slab
   remains visible in Clean 3D mode and prevents otherwise successful models
   from appearing grounded in their geographic context.

2. **The library contains two visibly different quality tiers.**
   V21/high-detail families use roughly 35,000-160,000 triangles per assembled
   building and retain architectural depth. Legacy families use only 140-2,276
   triangles per assembled building, so no texture improvement alone can make
   them resemble the Kinnaird reference at close range.

3. **Dark facade materials need an environment-aware floor.**
   Charred timber and some Chateauesque/Hotel Particulier faces crush to black
   in the Google Tiles lighting. Their albedo and roughness response should be
   calibrated against the City Prompt environment, not only the standalone
   compiler preview.

4. **High-detail small families need compression and LODs.**
   The townhouse, courtyard housing and minimalist block look materially more
   architectural, but are disproportionately heavy. KTX2 textures and
   simplified city-scale modules are required before district-scale use.

5. **Variant IDs currently alias shared geometry.**
   Alias support makes all variants placeable, but it does not yet provide the
   unique roof, entrance, corner, window and material assemblies required for
   visibly distinct archetype variants.

## Recommended implementation order

1. Make the site-preparation surface transparent/depth-only, or clip only the
   underlying photogrammetry without drawing an opaque replacement slab.
2. Upgrade the six legacy-quality families with the V21 semantic facade,
   glazing and architectural-relief methodology.
3. Add City Prompt lighting calibration for very dark albedos.
4. Package KTX2 textures and lower-detail city LODs for the three heavy small
   families.
5. Introduce variant-specific assembly profiles while continuing to share only
   repeatable middle bays.

## Cleanup and subsequent test workflow

The 11 QA polygons and their linked temporary buildings were deleted after the
batch integration pass. The original parcel is the only remaining polygon.

Subsequent visual tests should reuse that parcel sequentially: remove the
current temporary building recipe, place one family, capture and review it,
then delete it before placing the next family. Do not create a district-scale
grid unless a future test explicitly requires multi-building performance QA.
