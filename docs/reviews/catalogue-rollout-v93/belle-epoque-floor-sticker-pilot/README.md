# Belle Époque floor-addressed Sticker Method pilot (V93)

## Outcome

V93 proves the floor-addressed Sticker Method but is **not approved for the catalogue**. The roof sticker is isolated from occupied walls, and the six-storey proof adds a complete middle-floor unit instead of stretching the five-storey façade. The independent architect/design review scored the five-storey archetype pilot **77/100** and the six-storey scaling proof **79/100**; both remain below the 85/no-hard-stop gate.

The main remaining defects are visible floor-atlas seams and corner tears, broad pale belts that read as exposed carriers, an over-heavy and dark entrance canopy, and flattened or smeared dome treatment. Those defects are now explicit hard stops for the next iteration.

## Floor-addressed contract

The building is assembled from disjoint semantic bands:

1. `ground` — shopfronts, public entrance, plinth, and canopy datum
2. `middle_lower` — lowest glazed gallery and balcony datum
3. `middle_repeat` — the only repeatable occupied-floor unit
4. `middle_upper` — upper gallery below the principal cornice
5. `top_crown` — masonry top floor, setback, balustrade, and crown cornice
6. `roof` — mansard, terrace, eaves, soffits, dormers, domes, and cupola

The five-storey sequence uses one `middle_repeat`. The six-storey sequence inserts a second `middle_repeat`, then translates the fixed `middle_upper`, `top_crown`, and complete roof group by 4.1 metres. Ground, top, and roof textures are never stretched or repeated. Roof sources are forbidden on vertical walls and on `top_crown`.

## Coverage result

The previous registration-only check was a false positive: 1,242 of 3,232 rendered polygons (38.4%) still used fallback materials. V93 audits the final bound Blender faces, not only the declared material carriers.

| Pilot | Final faces checked | Fallback faces | Roof faces below roof datum | Result |
| --- | ---: | ---: | ---: | --- |
| Five storeys | 1,956 | 0 | 0 | Technical coverage pass |
| Six storeys | 2,028 | 0 | 0 | Technical coverage pass |

The five-storey segmented geometry hash is `2f433ac720d49e35cc48d8f92f2d7d4540710e3ec98a641c99567f50dcee1e9c`; the six-storey hash is `c0d0a0636e2095918a8d96198528394a2629fe7ce95dc639d1b49bf9f4d5d1c0`.

## Review images

The comparison board is arranged as **reference / five storeys / six storeys** from left to right. Rows show street/archetype view, oblique view, and roof audit.

![Floor-addressed comparison](floor-comparison-board.jpg)

Additional close and rear views are included alongside the board so seams, roof ownership, and back/corner coverage can be inspected rather than hidden.

## Publication blockers

- Replace broad pale coverage belts with architecturally sized, continuously stickered cornice/eave geometry.
- Make every floor crop seam-safe using shared boundary texels or blended overlap zones; reject visible horizontal cuts.
- Resolve front/corner and rear/corner joins in a common UV chart instead of allowing torn triangular joins.
- Reconstruct the entrance as readable iron-and-glass doors, occupied interior depth, curved signage, and a lighter canopy.
- Rebuild domes as ribbed translucent glass systems with dedicated drums and caps; do not project roof imagery across dome tops.
- Reduce the assembled GLB below the 8 MB delivery gate. The five-storey and six-storey pilots are approximately 19.66 MB and 19.72 MB respectively.

No paid API calls were used for this pilot.
