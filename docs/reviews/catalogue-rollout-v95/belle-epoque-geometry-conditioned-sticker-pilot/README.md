# Belle Époque Grand Magasin — V95 geometry-conditioned Sticker pilot

Decision: **approved at 95/100 with no architectural or sticker hard stops**.

V95 is the first production reference for the final Sticker Method. It retains
the locked select-and-place landmark and conditions every sticker against its
exact final carrier. The carrier package contains 198 fingerprinted surfaces:
30 ground, 78 middle, 28 top/crown and 62 roof.

## What changed from V94

- rebuilt smaller, construction-complete dormers with separate front, cheek,
  cap, flashing, dark physical glazing and frames;
- broadened the curved entrance canopy and added a registered identity sign;
- separated the occupied corner tower from its roof transition at 20.5 m;
- gave both domes radial intrinsic glass stickers, ribs and occupied light wells;
- classified landmark glazing as all-view so aerial LOD switching cannot hide
  the dome sticker;
- split all eight outside returns floor-by-floor and finished them as explicit
  limestone construction joints;
- made floor/roof ownership derive from target geometry rather than shader
  class; and
- declared the measured landmark projection envelope without shrinking the
  approved corner-pavilion silhouette.

## Release evidence

- architectural review: 95/100, pass, zero hard stops;
- sticker/material review: 95/100, pass;
- floor ownership audit: strict pass;
- generation quality contract: 26/26 gates pass;
- final Blender surface audit: 1,804 faces, zero failures;
- runtime GLB/module validation: pass;
- required presentation renders: 9/9 present.

The assembled GLB is 69,556 triangles and 17.7 MB. Its 196 materials and size
remain explicit optimization warnings. Consolidation and texture reduction are
deferred until after the visual lock so they cannot silently damage sticker
alpha, mapping or optical parity.

Start with
[the V94/V95 comparison board](v94-v95-geometry-conditioned-comparison-board.jpg),
then inspect [the front corner](front-corner.png), [rear corner](rear-corner.png),
[roof audit](roof-audit.png), [aerial view](aerial.png), and
[close facade](facade-close.png).

The reusable method lives in
[docs/sticker method](../../../sticker%20method/README.md).
