# Independent holistic review: The Overhang, v001 (RLASM v6.1 architectural clay)

Scope: rendered pixels only, compared with `sources/front.png`, `sources/oblique.jpg` and `sources/top.jpg`. I opened all 18 renders at full resolution, plus zoomed crops of the shell junction, the shell rim and hollow, the climbers and the area under the east overhang. I did not use any metadata, counts, hashes or builder notes as evidence. Pixel coordinates refer to the 1440x1080 renders unless noted otherwise.

## 1. Verdict

**VISUAL_REWORK_REQUIRED**: the building block, roof program and landscape largely match the sources, but the CLT climbing shell (the identity element) has the wrong fold geometry where it meets the pool block, misplaced climbers that appear to float, a missing crash mat and a washed-out timber colour, and two whole-envelope cameras clip the asset.

## 2. Findings

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | front, front_corner, top, architecture_close | The shell's west side is one inclined plane from the foot (front ~780,800) to the rim corner (front ~905,150). Its west edge leans away from the pool block, leaving a wedge of white roof/penthouse visible between the shell and the parapet end (front ~805-840, 300-420; front_corner ~820-840, 420-500). In top (~565-580, 700-730) an open black seam shows where the west face fails to close against the building. In the sources (front ~585, 100-290; oblique ~690-700, 240-400) the upper west face rises from the pool-block parapet corner as a separate panel, and a fold crease at parapet height separates it from the lower flared face. | The west face was modelled as a single quad from the foot to the rim. No upper panel was anchored to the parapet's SE corner, and the shell was not sealed to the building. | Split the west side into (a) a lower flared face from the foot to a crease at parapet height and (b) an upper panel whose west edge sits on the pool-block parapet SE corner and rises to the rim's west edge. Close the seam to the frame-box side and the parapet so no void shows from above. |
| 2 | P1 | front, front_corner, climbing_face, rim_interior, wall_base_contact | Only one climber sits on the south face, and it is at the extreme SE fold. The other two hang beyond the shell's silhouette with their hands gripping nothing: against the plaza and grass strip (front ~1235-1280, 455-520; front_corner ~1175-1220, 540-590), against the east-block glazing (climbing_face ~830-910, 610-810), against the paving (rim_interior ~760,760 and ~850,765), and against the brick neighbour (wall_base_contact ~1030-1055, 190-310). In the sources all three climbers are on the middle of the south face, inside its outline (front ~710-810, 340-405; oblique ~830-920, 480-530). | The climbers were placed at the SE corner offsets rather than on the south-face plane. Their hand points are not snapped to holds on any face. | Move all three climbers onto the south-face mid-panel, in the band between about one third and half of the height. Snap the hands and feet to hold positions on that plane and verify from front, front_corner and climbing_face that each climber is fully inside the timber silhouette. |
| 3 | P1 | top, rim_interior | The open top shows the inner walls and white holds, but no crash mat. The hollow floor appears only as a thin light blue-grey sliver along the inner west edge (top ~700-715, 730-840). In source top a broad dark crash mat fills the centre of the hollow floor (~590-720, 620-670) and is the most legible feature inside the rim. | The hollow floor was left as plaza paving or as a thin strip, or the mat is hidden or missing. The inner wall geometry also hides the floor from above. | Add a dark crash-mat slab across the hollow floor, sized and positioned so that, as in source top, it is visible from the top camera through the rim. If the lean hides it, pull the north inner wall back so the mat reads. |
| 4 | P1 | front, front_corner, top, right_side, climbing_face, wall_base_contact | The timber reads as pale greyish beige or cardboard rather than honey CLT. The lit west face measures RGB ~(183,160,127), saturation 0.31 (front ~1000-1060, 200-260), against the source's lit west face of ~(247,182,83), saturation 0.66 (source front ~600-700, 200-300) and ~(250,179,76) in the oblique. The timber/white contrast that defines the material hierarchy is lost. The source-vs-render board pairing makes this obvious. | The base colour is under-saturated and too dark, and the global grey haze or tonemapping desaturates it further. | Set the CLT base colour to the source palette (about #E8B05A lit, about #8A5530 shade, hue ~35°, saturation ≥0.6), then re-check against the source on the board. Reduce the global haze so the white precast stays white and the timber stays honey. |
| 5 | P1 | rear, left_side | The whole-envelope cameras clip the asset. In rear, the left frame edge cuts the east block's north facade mid-bay (x=0) and the right edge cuts the pool block's NW corner (x~1380-1440). Rear is also underexposed. In left_side, the frame cuts the west elevation at its north end (x=0, partial bay), so the full west rhythm and the north corner are not shown. | The cameras are too close, or the field of view is too narrow, for the full elevation. | Pull rear and left_side back, or widen them, until each full elevation plus a margin fits the frame. Raise the exposure on the north elevation. |
| 6 | P2 | right_side, climbing_face | On the east side, the facade below the overhang is a white plane sloped parallel to the shell. It cuts the east block's glass ribbons diagonally (right_side ~510-660, 220-700), so the east face sits flush on a sloped wall instead of overhanging a vertical white facade (source front ~790-845, 380-500). No source shows this face, so this is a coherence note only. | The infill was modelled to follow the shell's lean. | Make the white facade under the east overhang vertical and end the ribbons at a vertical return. |
| 7 | P2 | top, rim_interior | The inner shell walls are smooth-shaded and read as curved or warped bands (top ~760-990, 680-860), not as flat folded CLT planes. | Smooth normals on faceted geometry. | Use flat shading, or split the normals per face, on the shell's inner and outer faces. |
| 8 | P2 | front, right_side, climbing_face | The holds are denser and more clustered than in the source, especially black clusters near the SE fold, and there is a dense hold field on the east face. | The scatter density is too high. | Thin the holds by about 30-40% and keep the south face as the densest face. |
| 9 | P2 | top, rear | The penthouse is wider (about 41% of the frontage, against about 32% in source top) and stands taller than the east block, so the east block is correspondingly narrower. | Plan widths were not taken from source top. | Re-proportion the penthouse and east-block widths to source top. |
| 10 | P2 | aerial | The "aerial" is a rear (north) aerial: the shell shows only as a sliver of rim, and it does not match the role of the oblique source. The board pairs it with the locked top. | Camera azimuth choice. | Keep it as a rear aerial and add, or re-pair, an SW oblique aerial that matches `oblique.jpg`. |
| 11 | P2 | front, plaza_planters, right_side | Only about 2 bollards are visible, against a row of about 5 at the plaza's SE edge in the source. The plaza planters are plain rectangles, whereas one source planter is L-shaped. The roof-garden trees are mid-green rather than yellow-green. | Landscape simplifications. | Add the bollard row, make the SE planter L-shaped and shift the roof-tree tint toward yellow-green. |
| 12 | P2 | facade_close | A street tree covers about 35% of the frame. | Camera placement. | Shift the camera one bay north. |

P0 count: 0. P1 count: 5. P2 count: 7.

## 3. Source conformance checklist

| item | status | view used |
|---|---|---|
| Silhouette and storey count: three-storey pool block | conforms | front, left_side, rear |
| Penthouse (one storey) | conforms; it is slightly oversized (P2 #9) | front_corner, rear, pool_deck |
| Four-storey east block | conforms | right_side, rear, aerial |
| Plan (top view): corner block, west pool block, middle penthouse, east block, south plaza | conforms in arrangement; the penthouse/east-block width split deviates (P2 #9) | top vs source top |
| Shell: foot on the plaza in front of the facade | conforms | wall_base_contact, entrance, front |
| Shell: lean east and overhang over the plaza | conforms | front, front_corner, top |
| Shell: folded faces (west faces flare at the foot and meet the parapet at a fold) | **deviates**: single inclined west plane, no parapet fold (P1 #1) | front, front_corner vs source front/oblique |
| Shell: level open rim with light fascia | conforms | rim_interior, top, front_corner |
| Shell: contact with the plaza | conforms (clean ground contact, no float) | wall_base_contact, entrance |
| Shell: contact with the facade | **deviates**: gap and open black seam at the parapet junction (P1 #1) | top, front, front_corner |
| Holds (dark and white, densest on the south face) | conforms; over-dense (P2 #8) | front, rim_interior, climbing_face |
| Three climbers on the south face | **deviates**: two hang off the silhouette or float, one sits at the edge (P1 #2) | front, front_corner, climbing_face, rim_interior |
| Open top and inner walls with white holds | conforms | rim_interior, top |
| Crash mat at the hollow floor | **deviates**: missing or illegible (P1 #3) | top vs source top |
| West front rhythm: fins, spandrels, recessed windows with returns | conforms | left_side, facade_close |
| West front: glazed ground floor behind white columns | conforms | left_side |
| South frame box with two glass ribbons | conforms | front, architecture_close, glass_close |
| Entrance doors: two pairs under the frame box | conforms | entrance, front_corner |
| Parapet band (deep, white) | conforms | left_side, architecture_close |
| Pool deck: long N-S infinity pool along the west edge | conforms | top, pool_deck, rear_side |
| Pool deck: weir and trough | conforms (dark trough strip along the west edge; the glass weir is not distinct, which is acceptable for clay) | pool_deck, rear_side |
| Pool deck: glass balustrades on the parapet | conforms | left_side, front, pool_deck |
| Pool deck: row of white loungers | conforms | pool_deck, top |
| Roof garden: raised planters, grasses, small trees at the north end | conforms; tree tint differs (P2 #11) | rear_side, pool_deck, top |
| Penthouse: glazed south end to the deck, solid north part with a door | conforms | pool_deck, front_corner |
| Penthouse: AHU and fan on the roof | conforms | top, rear_side |
| East block roof: two skylights and small plant | conforms | top, aerial |
| White facade under the overhang | deviates (sloped wedge, coherence only, P2 #6) | right_side, climbing_face |
| Plaza: two-tone paving bands | conforms | top, wall_base_contact, plaza_planters |
| Plaza: two raised planters with straw grasses | conforms; planter shape simplified (P2 #11) | plaza_planters, top |
| Plaza: low planted strip along the east edge | conforms | top, right_side |
| Plaza: bollards | partially present; sparse (P2 #11) | right_side |
| Plaza: lamp posts | conforms | front, plaza_planters |
| West concrete sidewalk | conforms | left_side, front |
| Street trees in pits | conforms | left_side, front |
| West street with crossings | conforms | front_corner, top, aerial |
| East street with parked cars | conforms | right_side, top |
| Neighbours: brick mid-rise and residential | conforms (generic banded brick slabs) | front, rear_side, pool_deck |
| Materials hierarchy: white precast, glass, honey CLT, grey granite | **deviates**: CLT is desaturated beige, so the hierarchy is weakened (P1 #4) | front vs source front |

## 4. Camera validity

- **rear**: the asset is clipped at both frame edges (east block NE corner, pool block NW corner), and the view is underexposed. It is invalid as a whole-envelope view (P1 #5).
- **left_side**: the north end of the west elevation is clipped at x=0. It is invalid as a whole-envelope view (P1 #5).
- **aerial**: legible, but it is a rear aerial that hides the shell and is mismatched in role to `oblique.jpg` (P2 #10).
- **facade_close**: legible, but a tree occludes about 35% of the frame (P2 #12).
- All other views (front, front_corner, top, right_side, rear_side, climbing_face, wall_base_contact, rim_interior, pool_deck, architecture_close, glass_close, interior, plaza_planters, entrance) are valid: the target is legible, not occluded and not clipped beyond the intended detail framing.
