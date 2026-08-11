# Belle Époque continuous-shell Sticker Method pilot (V94)

## Outcome

V94 run 6 is **architecturally approved at 91/100 with no hard stops**. It is
the first Belle Époque Grand Magasin iteration to clear the stricter 90-point
visual gate. The result is materially more faithful than V93 while preserving
floor-addressed sticker ownership and the select-and-place landmark contract.

The visual approval is not yet a runtime-delivery approval: the assembled GLB
is 23.12 MB with 142 materials, above the 8 MB delivery target. Texture/material
consolidation is the next bounded optimization and must preserve this approved
six-view appearance.

## What changed

- Replaced five closed floor prisms with nine continuous, cap-free elevation
  shells while retaining exact ground/middle/crown face ownership.
- Added a real recessed iron-and-glass entrance section, occupied depth and a
  thin supported canopy.
- Added physical meridional ribs and rings to both registered dome skins.
- Kept the plan roof atlas on roof planes, removed its pale isolation border,
  and assigned direction-specific zinc stickers to roof-edge faces.
- Shortened and re-cropped the corner cupola so it remains subordinate to the
  central courtyard dome.
- Removed obsolete oversized cornice boxes that read as crossing rails.
- Assigned the principal straight-wall end cap a registered corner-derived
  return sticker, eliminating the exposed atlas boundary.

## Technical gates

| Gate | Result |
| --- | ---: |
| Continuous exterior walls | 9 |
| Internal floor caps | 0 |
| Final audited faces | 1,756 |
| Fallback/unowned faces | 0 |
| Roof faces below roof datum | 0 |
| Triangles | 46,624 |
| Architect score | **91/100 — approve** |
| GLB delivery size | 23.12 MB — optimization warning |

## Review board

Columns are **exact reference / V93 / V94 run 6**. Rows are the street/archetype
match, oblique/front-corner comparison, and aerial/roof audit.

![V93 to V94 comparison](v93-v94-comparison-board.jpg)

The individual street, front-corner, rear-corner, close-facade, roof-audit,
aerial and context renders are included beside the board so side/rear coverage
and roof construction can be inspected directly.

No paid API calls were required. The approved existing stickers contained
enough evidence; the successful changes were geometry, UV ownership and
assembly-order corrections.
