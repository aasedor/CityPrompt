# Independent holistic review: passatge v005

Reviewer: independent (did not build this candidate). I opened every render at full resolution: front, front_corner, aerial, top, left_side, right_side, rear, rear_side, facade_close, architecture_close, glass_close, interior, roof_vault, south_portal, north_portal, shopfronts, floor_tiles and pavilion_finial. I also opened the three locked sources (front.png, oblique.jpg, top.jpg) and the four phone boards. I made zoomed crops of the source front's right and left facades and its north end, the oblique's south mouth, and the render's vault, end wall, pavilion, north doorway and north lunette. I judged rendered pixels only. I did not treat builder notes or metadata as evidence.

## 1. Verdict

**VISUAL_REWORK_REQUIRED**: the plan, vault, 8-bay rhythm, north end wall and south mouth now conform, but one P1 remains. In the passage facades' arch tier, the piers are rendered as full-height cream stone pilasters. The locked front shows brick piers, and the stone pilasters stop at the shop entablature. This turns the dominant interior elevation from a brick arcade over a stone shop storey into a cream frame with brick infill panels.

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | facade_close, architecture_close, front, interior, south_portal, glass_close | Between the arches, the cream stone pilasters run unbroken from the floor through the arch tier to the modillion cornice. The stepped rib corbels sit on cream stone at mid-arch height, so the upper tier reads as alternating cream and brick bands. In the locked front (right facade around the CAFE DEL PASSATGE bay, and the left facade beside the LLIBRERIA ARTISTICA bay), the paneled stone pilasters end at the stone shop entablature under the balconies. Above that line the piers between the arches, the arch rings and the wall up to the vault are continuous red-orange brick, and the iron rib legs and corbels are fixed to brick piers. The render's material hierarchy (stone shop storey, all-brick arcade above) is inverted in the upper tier. | The pilaster solid is modelled as one full-height member, from the plinth to the cornice, instead of stopping at the shop entablature. | Stop the stone pilasters (with a small capital or console) at the top of the shop entablature or balcony belt. Change the arch-tier pier faces between the arches to the facade brick colour, leaving the stepped arch rings as brick. Keep only the rib corbel blocks (stone or dark iron) where the legs land. Rerender front, facade_close, architecture_close, interior and south_portal. |
| 2 | P2 | front, glass_close, architecture_close, south_portal | The lattice brackets between each rib leg and the vault haunch read as a thin ladder strut plus one ring and a loop. The source front shows large, dense triangular openwork scroll panels filling that spandrel. They are much heavier and more prominent. | The bracket is built as a strut, hangers and a ring only, with no infill panel. | Add a triangular openwork panel (an array of rings or scroll curves) between the leg and the rib haunch, about 1.2 m deep. |
| 3 | P2 | facade_close, architecture_close, front | The balconies are straight-fronted with a simple X-pattern rail. The source shows heavier balconies with roundel and scroll panels, on visibly projecting slabs. | Simplified rail module. | Add a roundel infill row to the balcony rail. Optionally give the front a slight bow. |
| 4 | P2 | facade_close, shopfronts | The shopfronts are inset with cream stone margins of about 0.4 m at the sides and a cream band above the signboard. In the source, the timber shopfront and signboard fill almost the full bay between the pilasters. | The shopfront width is set narrower than the bay clear width. | Widen the shopfront frame to the inner faces of the pilasters. |
| 5 | P2 | front, r_vault crop, north_portal | The north glazed lunette reads as a nearly opaque pale panel with a cream band at its base. From the street, its radial bars render as pale grey rather than dark iron, and there is no dark iron end frame on the outer face. | The glass material is too bright or diffuse at that end, and the bars take the glass tint. | Use the vault glass material and dark iron bar material on the lunette. Add a dark end-rib frame on the outer face. |
| 6 | P2 | north end (front, floor_tiles, shopfronts) | The portal keystone is a small plain block, and the medallions are round disks with a crest block. The source keystone is a large carved block reaching the cornice, and the medallions are ornate oval cartouches. | Simplified ornament. | Enlarge the keystone so it reaches the belt or cornice, and make the medallion frames oval. |
| 7 | P2 | front_corner, aerial, top | The paving of the south square is a uniform diamond lattice with a border. The oblique shows a two-scale pattern: large dark-banded diamonds subdivided by a finer lattice. | A single lattice scale. | Overlay a coarser dark-band diamond, at 3 to 4 times the module, on the square only. |
| 8 | P2 | front_corner, aerial | South of the west pavilion, the west block's south face continues as plain cream stucco. In the source this face is all pavilion, because the block narrows. This follows from not modelling the converging street geometry, which the brief allows, but the brick pavilion reads as a narrow bay attached to a stucco block. | Rectangular west block. | Optional: extend the brick and quoin treatment of the south pavilion face to the west corner, or chamfer the block. |
| 9 | P2 | top | The east strip measures about 2.9 m wide against an 11 m vault. The source top suggests a narrower strip. | Strip width chosen to fit shops. | Acceptable as is. Narrow it slightly if the shop depth allows. |

P0 count: 0. P1 count: 1. P2 count: 8.

## 3. Source conformance checklist

| Area | Element | Status | View used |
|---|---|---|---|
| Plan | Straight north-south passage through the block | conforms | top, left_side, right_side |
| Plan | Vault right of centre in the top view (centre about 0.51 of the frame width, matching the source) | conforms | top vs source top |
| Plan | Tiled square at the south mouth | conforms | top, front_corner, aerial |
| Plan | Streets to the west, east and north | conforms | top, rear, left_side, right_side |
| Plan | 8 bays (9 crested rib lines from the south end arch to the north end) | conforms | top, left_side, right_side, roof_vault |
| Passage facades | Brick, with stone pilasters at the shop level | deviates: the pilasters continue up through the arch tier (P1 #1) | facade_close, architecture_close vs source front |
| Passage facades | Timber shopfronts with plate glass, bulkheads, transoms | conforms (slightly inset, P2 #4) | facade_close, shopfronts |
| Passage facades | Dark green signboards with gilt name bands | conforms | facade_close, front |
| Passage facades | Stone shop cornice band | conforms | facade_close, shopfronts |
| Passage facades | One tall tier of deep recessed brick arches, one per bay, French windows with fanlights | conforms (tier proportion about 0.67 of the shop storey; source about 0.65) | facade_close, architecture_close |
| Passage facades | Arch surrounds and keystones | conforms (stepped brick rings; no keystone is visible in the source arcade either) | architecture_close |
| Passage facades | Iron balconies | conforms (simplified, P2 #3) | facade_close |
| Passage facades | Belts and modillion cornice | conforms | architecture_close, glass_close |
| Passage facades | Wall lanterns on the pilasters | conforms | facade_close, shopfronts, front |
| Passage facades | Canvas awnings over three shops (pitched, with valances) | conforms | facade_close, shopfronts, floor_tiles |
| Glass vault | Pointed section | conforms | glass_close, south_portal, rear |
| Glass vault | Main ribs (7) with lattice web | conforms | glass_close, roof_vault |
| Glass vault | Legs, corbels, lattice brackets (strut, hangers, ring) | conforms in topology; bracket ornament lighter than the source (P2 #2) | architecture_close, glass_close |
| Glass vault | Intermediate ribs | not modelled by design (no intermediate rib reads in the source top) | top vs source top |
| Glass vault | Glazing bars and purlins | conforms | glass_close, roof_vault |
| Glass vault | Crests on the ribs, ridge cresting, ridge cap | conforms | roof_vault, left_side, rear |
| Glass vault | Gutters | conforms | pavilion_finial |
| North end wall | Great round-arched portal, stone archivolt, keystone, imposts | conforms (keystone small, P2 #6) | front, north_portal |
| North end wall | Stone below the impost band, brick above | conforms | front, north_portal, floor_tiles |
| North end wall | Two medallions | conforms (round, P2 #6) | front, shopfronts |
| North end wall | Cornice | conforms | front |
| North end wall | Glazed lunette with radial bars | conforms in form; reads as opaque (P2 #5) | front, glass_close, north_portal |
| North end wall | Side doorway at 4.6 m in a stone surround, with visible depth | conforms | front, floor_tiles, north_portal |
| North end wall | Street beyond with cream blocks and two trees | conforms | front, interior, rear |
| South mouth | Two brick pavilions, stone quoins, cornices, parapets | conforms | south_portal, pavilion_finial, front_corner |
| South mouth | Urn finials at the inner corners only, short brick piers outside | conforms (matches the oblique) | pavilion_finial, south_portal vs source oblique |
| South mouth | Ornamental iron end arch with an inner arch, radial bars and rings | conforms | south_portal, interior, pavilion_finial |
| Floor | Pale tile, grey diamond lattice, border | conforms | floor_tiles, front |
| Square paving | Diamond lattice | conforms (single scale, P2 #7) | front_corner, top |
| Furniture | Two pairs of back-to-back benches on the axis | conforms | front, floor_tiles |
| Furniture | Cafe tables and chairs near the portal | conforms | front, shopfronts, floor_tiles |
| Furniture | Planters flanking the portal | conforms | front, floor_tiles |
| Furniture | Two lamp posts on the square | conforms | top, front_corner |
| Roofs | Terracotta west deck | conforms | left_side, aerial |
| Roofs | Stone balustrade along the vault | conforms | roof_vault, left_side |
| Roofs | Brick parapet on the east strip | conforms | right_side, rear |
| Roofs | White rooftop rooms and pergola | conforms | left_side, pavilion_finial |
| Context | Cream 5- and 6-storey blocks with balconies and terracotta decks on the west, east and north streets | conforms (plain massing, acceptable as clay) | aerial, rear_side, front_corner |
| Materials hierarchy | Brick, cream stone, dark iron, timber, green signs | deviates in the upper tier: cream predominates where the source is brick (P1 #1) | front, facade_close vs source front |

## 4. Camera validity

All 18 views are valid. In each, the target is unoccluded and legible. Some frame edges cut off content, but the brief does not require any of it:
- top: the south end of the square runs off the bottom edge, as in the source top.
- roof_vault: the vault's far end is cut off at the left edge, but the vault body, crests and balustrade are legible.
- north_portal: the wide-angle distortion is strong, but the portal, doorway, impost line and lunette are legible.

No view shows floating parts, clipping through the asset, or openings without depth. The north side doorway, the shopfront reveals and the deep arch recesses all show returns.
