# Three Sticker Landmarks — V90

This finite batch tests three previously unattempted exact catalogue variants.
Each fixed select-and-place landmark uses one continuous registered facade per
elevation; roof, silhouette, bay, porch, balcony, dome and construction returns
remain physical geometry.

- `01-exact-archetype-comparison.png` compares exact street evidence, the
  image-match render and facade close-up.
- `02-oblique-side-comparison.png` compares exact oblique evidence with front
  and rear Blender views.
- `03-roof-comparison.png` compares exact aerial evidence with the roof audit.
- Each building folder includes the three exact references, rectified sticker
  sheet and all six architect-review views.

Five bounded GPT Image calls were used: three first-pass sheets and selective
retries for Amsterdam and Toronto. No semantic-mask calls or unbounded retries
were made. Blender, OpenCV-derived masks, PBR baking and QA were local.

## Review result

All technical validation and surface-finish checks pass, but strict named
architect review rejects all three for catalogue release:

| Building | Score | Status | Primary hard stop |
| --- | ---: | --- | --- |
| Amsterdam Neck-Gable Merchant | 64/100 | rejected | doubled neck-gable silhouette and blank side/rear |
| Toronto Yellow-Brick Bay-and-Gable | 61/100 | rejected | doubled cross-gable, generic roof and misregistered porch |
| Parisian Zinc-Dome Corner | 54/100 | rejected | wrong mansard/dormer/corner-pavilion assembly |

The accurate stickers have outpaced the 3D massing. Before another batch, the
pipeline must require a source-matched roof/silhouette proxy and all-elevation
occupancy map before sticker generation. Generic glazing, balconies, gables or
porches may not duplicate photographed features. Near-perfect source-to-GLB
foreground parity is an export check only; it does not measure archetype
likeness.

See `architect-review.json` for the complete per-building assessment.
