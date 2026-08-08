# Swiss Alpine chalet v70 roof-detail pass

This bounded follow-up keeps the validated v69 chalet massing and facade while
rebuilding its roof surfaces as actual Alpine construction. The roof is now a
major identity assembly rather than three smooth gable prisms.

![Roof detail comparison](roof-detail-comparison.png)

![Street identity comparison](street-identity-comparison.png)

## Added roof detail

- Separate dark shingle fields on the main roof and warmer stone-slab fields on
  the projecting front cross-gables.
- Overlapping, staggered roof courses consolidated into three meshes.
- Sparse low-poly stone ballast with deterministic scale and placement.
- Aged-metal ridge caps, junction/drainage lines and eave gutters.
- Layered timber verges and retained exposed rafter/bracket construction.
- Hero-detail geometry remains below the configured 180,000-triangle ceiling.

## Validation

| Gate | v70 | Threshold | Result |
| --- | ---: | ---: | :---: |
| Structural validation | Pass | Pass | Pass |
| Silhouette IoU | 0.70299 | >= 0.58 | Pass |
| Roofline RMSE | 0.12055 | <= 0.14 | Pass |
| Aspect-ratio error | 0.17836 | <= 0.22 | Pass |
| Assembled triangles | 102,252 | <= 180,000 | Pass |

The OpenCV score remains regression evidence, not final likeness approval. The
family is still review-only until the footprint matrix, near/far PBR package and
live Google Tiles orbit receive explicit approval.

Individual outputs: [aerial](final-aerial.png) and
[front corner](final-front-corner.png).
