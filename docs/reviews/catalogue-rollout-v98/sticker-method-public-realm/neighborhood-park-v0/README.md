# Neighborhood Park v0 — Sticker Method pilot review

This bounded review shows the first building-independent use of the Sticker
Method in CityPrompt. The exact selected archetype is
`openspaces/neighborhood-park/variant_0.png` (SHA-256
`38c1079127126017edb7945f77f47d73c4d0dde1fe5a566ac5dc0e791473d5c3`).

The site uses the `site_adaptive_whole_program` representation. Ground and
residual planting fit the parcel, while the pavilion, climbing tower/slide,
swing frame, split-rail fence sections and boulder groups remain whole metric
GLBs at scale 1. Source pixels are not projected onto geometry.

Reviewed preview files:

- `neighborhood-park-v0-hero.png` — SHA-256 `83d36bf728074235b953a55a86a59781427c6830d4c7470b2971a35de4c7076b`
- `neighborhood-park-v0-aerial.png` — SHA-256 `a7828f49cfa4966db67b9bfd6622234bb2b3c34b8c59cbcaab46a3bea7b0032e`

The images are visual-QA evidence, not source textures. Runtime authority is
the compiled manifest at
`frontend/src/data/neighborhoodParkV0StickerKit.json` and its five referenced
GLBs under `frontend/public/park-kits/neighborhood-park-rustic-v0/`.
