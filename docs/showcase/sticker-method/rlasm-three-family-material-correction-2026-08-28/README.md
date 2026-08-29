# RLASM three-family source-specific material correction

This package supersedes the earlier `rlasm-three-family-builder-pass` package.
The earlier geometry corrections remain useful, but its overall builder-pass
decision was rescinded after phone review showed that family-specific material
names were masking shared generic noise, wave, and brick shader recipes.

The corrected candidates are:

- Art Deco judicial courthouse v8 — source-derived buff ashlar plus graded
  carved stone and source-matched civic step stone.
- Grand log lodge v13 — distinct source-derived timber, staggered wood
  shingles, and world-scaled fieldstone across chimney, corner blocks, piers,
  and steps.
- Chinese Siheyuan v8 — distinct cool-grey brick, blue-grey ceramic tile,
  cinnabar lacquer, dark lattice, pale granite, and world-scaled human-size
  courtyard paving.

Start with `rlasm-three-family-phone-overview.png`, then inspect
`rlasm-reviewed-material-specimens-phone.png` and the three 1080 × 1920
source/model boards. The JSON reviews record the immutable catalogue sources,
GLB hashes, source-derived specimen hashes, rejected iterations, and complete
geometry/architectural/material review state.

All three are `PASS_BUILDER_REVIEW_AWAITING_INDEPENDENT_APPROVAL` and remain
`NOT_A_KEEPER`. No builder self-promotion occurred.
