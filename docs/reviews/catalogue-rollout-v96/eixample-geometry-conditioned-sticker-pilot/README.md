# Eixample V96 geometry-conditioned Sticker Method pilot

Status: **approved — 96/100**

Placement model: **select-and-place landmark**

Paid facade/API calls: **0**

This pilot transfers the final Sticker Method from the Belle Époque Grand
Magasin to a second, architecturally different building. The carrier is a
locked 46 × 46 m Cerdà octagon with four visible storeys, broad chamfers, an
open light court, a lower court roof and a genuinely recessed entrance tunnel.
The 117 sticker carriers are authored floor by floor and conditioned in the
locked carrier's UV space; every locked face has exactly one final-surface
owner.

## Review boards

- [Street archetype comparison](01-street-archetype-comparison.png)
- [Oblique and all-elevation comparison](02-oblique-all-elevation-comparison.png)
- [Roof and courtyard comparison](03-roof-courtyard-comparison.png)

Exact catalogue references:

- `frontend/public/archetypes/buildings/eixample-apartment-block/variant_0.png`
- `frontend/public/archetypes/buildings/eixample-apartment-block/variant_0_angle_60.jpg`
- `frontend/public/archetypes/buildings/eixample-apartment-block/variant_0_angle_90.jpg`

## Final architectural gate

| Category | Score |
| --- | ---: |
| Archetype silhouette and massing | 25/25 |
| Floor, proportion and alignment | 20/20 |
| Sticker continuity and coverage | 19/20 |
| Entrance, courtyard and roof geometry | 14/15 |
| Materials, glazing and detail | 9/10 |
| Cross-view coherence and presentation | 9/10 |
| **Total** | **96/100** |

No hard stops were found. The reviewer verified four visible storeys, the broad
Cerdà octagon, continuous outer and courtyard stickers, one-owner balcony
ironwork, a true recessed portal, a visible lower court roof, dark glazed
rooflights, and coherent identity across all eight review views.

Non-blocking material polish remains: add subtle terrace grime/roughness,
slightly clearer rooflight glass and finer curbs, and modest variation in
planters, shutters and occupied glazing. These improvements must not reopen or
non-uniformly scale the locked carrier.

## Reproducibility record

- Locked geometry SHA-256: `f26d4f6a427b838beee4cf6cdfc38f979c3b6e10b0fdf155771d8c4ae94df534`
- Sticker package SHA-256: `8462cc89ba6987bfe90ec318b2ff8274c523bc12c50ab3623f1294090682676e`
- Sticker carriers: `117`
- Final-surface audit: `pass` (`133` audited faces, `0` failures)
- Focused regression suite: `26 passed`

The machine-readable approval is in [visual_approval.json](visual_approval.json).
