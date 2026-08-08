# Swiss Alpine chalet v69 pilot

This bounded pilot applies the no-install OpenCV and Blender workflow to the
Swiss Traditional Chalet. It is a substantial facade, proportion and
construction-detail improvement, but remains **review-only** until the family
receives its footprint matrix, full PBR/LOD package and explicit visual approval.

![Street identity comparison](street-identity-comparison.png)

![Roof-plan comparison](roof-plan-comparison.png)

## What improved

- Rebuilt the structure as a fieldstone podium with two weathered timber levels.
- Added a main gable plus two real front cross-gables with timber infill and
  physically framed gable windows.
- Added deep exposed rafter tails, diagonal eave brackets, a central paired
  chimney, an arched timber entry and supported two-level balconies.
- Added planter boxes with low-poly foliage and red flower clusters.
- Moved from the compact 14 m default to the catalogue's valid 18 m frontage
  tier after the first silhouette comparison proved the model too square.
- Derived the facade from all three exact variant references and used audited
  side/podium crops to prevent the entrance from repeating around the building.
- Replaced a false automatic glass mask with fourteen audited sash openings,
  reducing one repeatable module from more than 230,000 triangles to roughly
  29,000 triangles.

## Measured result

| Gate | v69 | Threshold | Result |
| --- | ---: | ---: | :---: |
| Silhouette IoU | 0.71255 | >= 0.58 | Pass |
| Roofline RMSE | 0.11430 | <= 0.14 | Pass |
| Aspect-ratio error | 0.17836 | <= 0.22 | Pass |

The first compact pilot failed all three gates. Rebuilding at the catalogue's
18 m maximum corrected the broad street silhouette without exceeding the
declared placement range. The OpenCV pass remains a regression result, not a
likeness approval: the exact reference has more wing depth and localized side
openings than this pilot.

![Fidelity overlay](fidelity-overlay.png)

## Next decision

Before catalogue promotion, author the small/large footprint matrix, deliver
near/far PBR atlases and obtain a live Google Tiles orbit approval. A later
multi-wing tier should repeat audited ordinary timber bays between fixed wings,
gables and entry rather than stretching a complete elevation.

Individual outputs: [front corner](final-front-corner.png) and
[aerial](final-aerial.png).
