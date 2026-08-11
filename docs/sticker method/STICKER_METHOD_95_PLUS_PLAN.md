# Sticker Method: final steps to 95+

## Outcome sought

Raise a building from the Belle Époque V94 baseline of 91/100 to at
least 95/100 without hiding errors in a hero camera, weakening the LEGO
assembly rules, or accepting unstickered surfaces.

The next gain should come from **geometry-conditioned sticker generation and
closed-loop reprojection**, not simply from requesting a prettier facade image.

## 1. Freeze the final carrier before making final stickers

Approve the clay model in reference-matched street, oblique and roof cameras.
The locked carrier includes:

- footprint, floor and cornice datums;
- straight, chamfered and curved facade transitions;
- roof planes, domes, dormers, chimneys and edge returns;
- entrance void contours, jambs, soffits, tunnels and occupied backs;
- projecting balconies, canopies, bays and other shadow-bearing construction.

After the lock, topology or proportion changes invalidate every affected
sticker. The pipeline must rebake and regenerate those charts rather than
stretching the old pixels.

## 2. Bake a carrier-space generation package

Blender exports an atlas template from the exact final mesh. Every sticker
request receives the matching reference images and these mesh-derived guides:

- UV chart and padded island mask;
- object/world position;
- surface normal and facing direction;
- depth and visibility from each approved reference camera;
- curvature, ambient occlusion and convex/concave edge masks;
- floor band, elevation, construction role and material role IDs;
- opening, glass, frame, column, ornament and void masks;
- window centres, column axes, floor datums and seam-pair anchors;
- UV stretch/distortion heatmap.

The generated pixels must already live in the final chart resolution and
bounds. Post-generation crop, aspect-ratio adjustment or independent scaling is
forbidden. If an image provider cannot consume multiple control maps directly,
the pipeline supplies a labelled carrier guide/contact sheet and performs an
iterative render-and-correct pass in UV space.

The sticker master is a surface material, not a screenshot. Perspective,
directional sunlight, cast shadow, sky reflection and lens distortion must be
removed from the source before projection. The pipeline then restores real
shading through the carrier normals, authored PBR maps, scene illumination and
physical glass. This avoids double shadows, painted highlights and the plastic
look that appears when a photograph is treated as albedo.

## 3. Use surface-specific projection, not one mapping rule

| Carrier | Required mapping |
| --- | --- |
| Straight walls | Rectified elevation chart tied to metre and floor datums |
| Rounded pavilions/turrets | Cylindrical or conformal unwrap with fixed angular anchors |
| Chamfers/corners | One shared cross-corner chart or paired charts with shared boundary texels |
| Pitched roofs | Per-slope plan/orthographic charts with ridge, valley and eave anchors |
| Domes | Radial/gores chart matched to dome ribs and rings |
| Dormers/chimneys | Separate front, cheek, cap and return charts |
| Entrances/canopies | Separate foreground, reveal, soffit, edge and recessed-back charts |

When a chart exceeds the distortion threshold, split it along a construction
joint and regenerate the affected pieces. Do not compensate by stretching.
Maintain an audited texel density on every chart and preview the actual
anisotropic/mipmap result at the intended city and hero distances.

## 4. Generate floor-addressable stickers on a continuous wall

Maintain four semantic bands:

1. fixed ground/podium;
2. complete repeatable middle floor modules;
3. fixed top/crown;
4. disjoint roof domain.

These are material and face-ownership bands, not closed floor boxes. Adjacent
bands share exact boundary texels, physical scale and anchors. A six-storey
sibling is produced by inserting one complete approved middle geometry module
and its matching carrier-conditioned sticker, then translating the unchanged
crown and roof. The approved fixed landmark itself is never stretched.

## 5. Make seams a generated constraint

- Generate adjacent corner/return patches together whenever possible.
- Copy a common texel strip across paired chart borders before dilation.
- Add bleed in the same physical distance in object and UV space.
- Keep roof planes off fascias and steep returns; those get direction-specific
  construction stickers.
- Validate seams in a neutral, shadow-light render and in grazing-angle views.
- Prohibit cosmetic belts or rails that cross windows or columns to conceal a
  mapping error.

## 6. Keep one owner for each visual feature

Geometry owns silhouette and parallax. The sticker owns fine surface identity.
PBR channels own roughness, normal response, transmission and reflection.

- A photographed balcony may receive a real slab/rail only when the geometry is
  registered to the same balcony boundaries.
- Physical glass is confined to the exact sticker-derived glass mask and sits
  behind the registered frame plane.
- A public doorway is cut from the same negative-space contour used to clear
  the sticker and build its reveal/tunnel.
- Roof albedo does not replace construction-role-correct normals or roughness.

Duplicated windows, columns, balconies, frames or gables are hard stops.

## 7. Close the render-to-sticker correction loop

For every required camera:

1. render the stickered model with neutral lighting and object masks;
2. align it to the exact archetype image using audited camera parameters;
3. compare silhouettes, feature anchors, material zones and visible seams;
4. back-project the measured error into the responsible UV chart or geometry
   assembly;
5. regenerate or locally correct only that owned region;
6. repeat until every numeric gate passes; then request architect review.

Never correct a geometry error by painting false depth into albedo. Never move a
UV feature to compensate for an incorrect carrier silhouette.

## 8. Quantitative pre-review gates

The proposed 95+ release gates are intentionally stricter than the V94 checks:

| Gate | Release threshold |
| --- | ---: |
| Visible polygon sticker/construction ownership | 100% |
| Generic blue/grey/clay/default fallback faces | 0 |
| Floor band gaps or overlaps | 0 |
| Roof-owned occupied-wall faces | 0 |
| Internal exterior-wall floor caps | 0 |
| Anchor reprojection RMSE at 1600 px | ≤ 2 px |
| Window/column centre drift | ≤ 0.25% of elevation width |
| Paired seam colour difference, neutral render, p95 | ΔE00 ≤ 3 |
| Symmetric UV area stretch, p95 | ≤ 1.25× |
| Masked source/export silhouette IoU | ≥ 0.98 |
| Alpha-masked source/export mean error | ≤ 3% |
| Required review cameras present | 7/7 |
| Architect score | ≥ 95/100, no hard stops |

Automated image similarity is diagnostic rather than a substitute for
architectural judgment. A high similarity score cannot excuse wrong storeys,
roof topology, entrances, window rhythms or proportions.

## 9. Belle Époque bounded 95+ pilot — implemented

Keep V94 as the controlled baseline and make only four architectural repairs:

1. broaden and curve the entrance canopy to the reference contour;
2. calibrate dome transmission, warm occupied backing and rib/ring occlusion so
   the stained glass remains luminous rather than dark or plastic;
3. reconstruct dormer fronts, cheeks and returns with their own fitted charts;
4. lighten the straight-to-rounded pavilion transition and recondition its
   sticker on the revised curve.

V95 implemented these repairs on 198 fingerprinted carriers. The final Blender
scene passed 26 generation gates and a 1,804-face, zero-failure surface audit;
the architect and sticker reviews both scored 95/100 with no hard stops. The
floor agent independently verified 30 ground, 78 middle, 28 top/crown and 62
roof carriers with no gap or overlap.

One cross-view defect revealed a required production rule: landmark dome glass
cannot use the same `near` LOD visibility as optional facade optical overlays.
It must remain visible in street, corner, roof and aerial presentations, or the
pale light-well backing replaces the approved dome sticker. The fixed result
uses an all-view landmark-glass classification.

## 10. Prove the method before catalogue scale

After Belle Époque passes, run a three-building proof set:

- one mostly planar, floor-repeatable streetwall;
- one curved/turreted landmark;
- one roof-dominant building with dormers or complex intersections.

Each must independently clear 95 with zero fallback faces and zero registration
hard stops. Only then consolidate materials, create city-distance LODs, verify
source-to-GLB parity again, and move to bounded catalogue batches.

## Expected contribution to the missing four points

The estimate below is a prioritization aid, not a guaranteed score:

- carrier-conditioned curved/roof/dormer charts: **+1.0 to +2.0**;
- entrance and canopy reconstruction: **+0.5 to +1.0**;
- dome optics and occupied depth: **+0.5 to +1.0**;
- pavilion transition and seam refinement: **+0.5 to +1.0**.

The key is that all four improvements are judged on the projected building,
not on the attractive flat sticker master.
