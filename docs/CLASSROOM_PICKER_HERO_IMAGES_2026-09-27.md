# Classroom picker hero images — 27 September 2026

The validation picker has 45 exact choices. A visual audit found 12 cards showing
technical/isometric model previews among otherwise photographic reference views.
Those cards now use curated 960 × 540 WebP hero images under the authoritative
`frontend/public/archetypes/{buildings,openspaces,streets}` roots. The card's
image is presentation only: its placement ID, locked asset hash, native model,
and capture behavior are unchanged. The other 33 cards retain their existing
reference images.

| Choice | Hero source |
| --- | --- |
| Machiya cafe and gallery | Exact v005 source facade angle, `japanese_machiya_mixed_use/variant_2_angle_60.jpg` |
| Neighbourhood orchard | Urban orchard source hero |
| Timber and stone square | Montreal neighbourhood square source variant 0 |
| Shaded Reading Garden | Earlier photoreal City Prompt render of the same native garden; oblique view |
| Pickleball Social Garden | Pickleball courts source hero |
| Garden Tennis Court | Tennis court cluster source hero, cropped to the near court |
| Bocce Pergola Garden | Bocce court source hero |
| Rustic Pocket Garden | Urban pocket park source variant 0 |
| Railway Meadow Greenway | Multi-use trail source variant 3 |
| Inclusive Woodland Playground | Inclusive playground source hero |
| Planted shared lane | Woonerf shared street source variant 0 |
| Quiet residential street | Narrow residential street source variant 0 |

The source photos are illustrative archetype references, not exact-scene
captures or a promise that adjacent buildings and furnishings are placed by
the model. The Reading Garden image is a prior AI result and retains its
separate fidelity-review status. Picker image selection is keyed by the exact
runtime placement ID in `pickerHeroImages.ts`, so a sibling variant cannot
silently borrow the wrong image.

`scripts/validation_bundle.py unpack` stages these images alongside the locked
runtime packet. Existing local installations can run
`py -3 scripts/validation_bundle.py sync-picker-heroes`; the staging step
preserves any differing local file rather than overwriting it. The original
references and technical preview images remain untouched.
