# Meshy park-object batch v1

This finite pilot tests Meshy only where it adds value to the park LEGO builder:
organic, sculptural, and craft-detail objects. Regulation geometry, site fitting,
clearances, playing surfaces, paths, and terrain remain deterministic City Prompt
LEGO geometry.

## Result

- 15 archetype-derived candidates generated through consistent multi-view image
  guidance and Multi-Image-to-3D.
- 585 Meshy credits used: balance 7,518 to 6,933.
- 12 runtime GLBs accepted after Blender metric normalization, ground contact,
  12,000-face bounding, 512 px packed PBR maps, and four-angle visual review.
- 3 candidates rejected and not copied into the runtime catalogue.
- No people or large buildings are present in any accepted GLB.

## Accepted runtime assets

| Archetype | Asset | Metric envelope |
| --- | --- | --- |
| Nature play | granite climbing boulder | 2.8 × 2.2 × 1.8 m |
| Nature play | sandstone crawl/scramble boulder | 2.6 × 2.0 × 1.6 m |
| Rewilding | riparian root wad | 3.2 × 2.8 × 2.2 m |
| Rewilding | standing habitat snag | 1.2 × 1.2 × 5.5 m |
| Rewilding | hollow habitat snag | 1.4 × 1.4 × 6.0 m |
| Rewilding | brush habitat pile | 4.0 × 2.6 × 1.6 m |
| Pollinator meadow | timber insect hotel | 1.4 × 0.5 × 2.0 m |
| Urban orchard | rustic potting bench | 2.2 × 0.8 × 1.3 m |
| Memorial garden | woodland memorial bench | 2.4 × 0.8 × 1.0 m |
| Mini golf | sculptural rock obstacle | 3.0 × 2.2 × 2.0 m |
| Sculpture garden | Corten loop | 2.2 × 1.6 × 3.0 m |
| Sculpture garden | limestone portal | 2.6 × 1.5 × 3.2 m |

## Rejected candidates

- `nature-play-hollow-nurse-log-v1`: good multiview guidance but the reconstructed
  mesh read as a stump instead of a crawl-through log.
- `rewilding-root-wad-riparian-v1`: Meshy carried a detached boardwalk fragment
  from the scene into the object.
- `rewilding-deadwood-habitat-pile-v1`: attractive source views, but the metric
  runtime result read as stacked bark/cardboard sheets.

The rejected raw outputs remain outside the repository under the batch artifact
root for audit and possible prompt/crop regeneration.
