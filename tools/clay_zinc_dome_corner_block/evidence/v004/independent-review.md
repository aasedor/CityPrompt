# Independent holistic review: clay-zinc-dome-corner-block v004 (RLASM v6.1)

Reviewer: independent, did not build the candidate. Evidence used: the three locked sources (`sources/front.png`, `sources/oblique.jpg`, `sources/top.jpg`), all 18 renders opened at full resolution, and the four phone boards. Read-only pixel sampling (luminance and RGB) was run on renders to confirm dark/void readings. No metadata, counts, hashes or builder notes were used as proof.

## 1. Verdict

**VISUAL_REWORK_REQUIRED.** Both v003 P1s are now fixed in the pixels. One new P1 remains: on the chamfer bay, the wide bracketed balcony sits at the first storey. Both sources and the locked balcony grammar put an individual balconette there and carry the wide bracketed balcony one storey higher.

Counts: P0 = 0, P1 = 1, P2 = 9

## 2. Findings

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | front, cafe_awning, architecture_close, front_corner, roof_court (vs sources front.png and oblique.jpg) | On the chamfer, the first-storey window directly above the awning frieze has a full-bay railing about 3.4 times the window width (cafe_awning x 445-985 against a window at x 640-800). It sits on a slab carried by the two console brackets in the frieze over the awning. Going up the chamfer, the balconies read wide / wide / narrow / wide for storeys 1 to 4. Both sources show a narrow individual balconette at chamfer storey 1, about window width (front.png x 430-535, y 490-515). The two consoles sit above that window's head and carry the full-chamfer balcony at storey 2 (front.png x 383-575, consoles at y 385-445; the same in oblique.jpg). The render therefore breaks the locked rhythm (individual on storeys 1 and 3, continuous on 2 and 4) on the hero bay, and moves the signature bracketed balcony one storey down. | The chamfer balcony list (or its storey-index mapping) gives storey 1 the "continuous/bracketed" type. The console pair is tied to the storey-1 slab instead of the storey-2 slab. | Make chamfer storey 1 an individual balconette sized to the window, on the same slab and rail as the flank storey-1 balconettes. Move the console pair up so it sits in the storey-1 window-head zone under the storey-2 full-chamfer slab. Leave storeys 2, 3 and 4 as they are. Re-render front, cafe_awning and architecture_close. |
| 2 | P2 | top (also 2-3 px in aerial, front_corner, roof_court) | Pure-black (luma 0-1) 7-8 px squares at the tops of all four inner court corners, and 6 px squares at the three non-chamfer outer corners. From court level the corners are closed (rear_court); this is a hole in the wall-top or coping, seen from above. | The wall slabs now meet, but no corner post or coping cap closes the corner column, so the camera sees down into an unlit cavity. | Add a solid corner block or coping cap at each court corner and outer corner, at full wall height. |
| 3 | P2 | corner_dome, roof_court | A black hairline wedge, about 30 x 2-3 px (15 x 5 px in roof_court), at each flank where the drum base meets the main cornice and mansard. | The drum's outer face and the cornice or mansard return leave a small gap into the dark interior. | Extend the cornice/mansard return into the drum by a few cm, or add a drum plinth ring that overlaps both. |
| 4 | P2 | all whole-envelope views, mansard_dormers | A continuous salmon/brick-coloured band on top of the main cornice, directly under the mansard. The sources show a stone cornice with a zinc gutter there. | The cornice top or gutter strip uses the brick material. | Assign stone (or zinc for the gutter) to that strip. |
| 5 | P2 | facade_close, balcony_ironwork, left_side | The brick fields carry two thin stone stripes per storey that run between the window surrounds. The sources show toothed long/short stone quoins at the edges of the brick panels. The facade reads as banding, not quoining. | The quoin pattern is simplified to horizontal string strips. | Optional: alternate the strip lengths at the panel edges so they read as quoins. |
| 6 | P2 | rear_court, aerial, rear_side (vs top.jpg) | The inner court walls are red brick with stone sills. In top.jpg the court walls are pale stone or render. | The street-facade brick material is reused on the court walls. | Optional: use the pale stone or render palette on the court walls. |
| 7 | P2 | mansard_dormers, left_side | The dormers have flat rectangular zinc caps over arched windows. The sources show arched or pedimented dormer hoods. | The dormer head is simplified. | Optional: use a segmental or pediment cap. |
| 8 | P2 | glass_close, facade_close | Tiny black pinholes (4-8 px) at the corners of window and shopfront frames. | Frame and reveal slabs meet with small gaps at the mitre corners. | Overlap the frame members at the corners, or add corner blocks. |
| 9 | P2 | aerial (vs top.jpg) | The aerial orbit looks at the rear (non-chamfer) corner. The dome and awning are on the far side, only partly visible. top.jpg looks at the chamfer head-on. The view is valid but a weak role match. front_corner covers the identity corner. | Camera azimuth. | Optional: rotate the aerial azimuth about 180 degrees so the chamfer faces the camera, as in top.jpg. |

Also noted, not counted: the dome gores read as slightly concave melon lobes, where the sources show a smooth dome with standing-seam ribs. This is acceptable for clay.

## 3. Source conformance checklist

| item | status | view used |
|---|---|---|
| Silhouette (corner block, chamfer, mansard with flat top, dome on chamfer, court) | conforms | front, front_corner, top, aerial |
| Storey count (stone ground, stone first, 3 brick, mansard) | conforms | left_side, rear, facade_close |
| Chamfer and dome (ribbed zinc dome on the chamfer, oculus dormer on the dome) | conforms | corner_dome, front, roof_court |
| Drum windows and lantern (three oeil-de-boeuf roundels with keystones; open columned lantern, cupola, gilded finial) | conforms | corner_dome, architecture_close |
| Balcony rhythm, flanks (individual on storeys 1 and 3, continuous on 2 and 4) | conforms | left_side, facade_close, balcony_ironwork |
| Balcony rhythm, chamfer | deviates (P1 #1: storey 1 wide and bracketed instead of an individual balconette; consoles one storey low) | front, cafe_awning, architecture_close |
| Brick-and-stone banding (string courses, surrounds, quoins) | conforms on string courses and surrounds; quoins simplified to bands (P2 #5) | facade_close, balcony_ironwork |
| Mansard and dormers (zinc, arched dormers per bay, flat top) | conforms; dormer caps simplified (P2 #7) | mansard_dormers, left_side, rear |
| Cafe awning and ground floor (red awning wrapping the chamfer with valance; stone piers; glazed cafe) | conforms | cafe_awning, front, top |
| Cornice (bracketed and modillioned) | conforms; top strip wrong material (P2 #4) | mansard_dormers, architecture_close |
| Materials hierarchy (stone base and chamfer, brick upper fields, zinc roof and dome, iron rails, gilt finial) | conforms, except the brick court walls (P2 #6) | front, aerial, rear_court |
| North and east faces (no source) | coherent with the visible grammar (same banding, storeys and mansard; balconies omitted on the secondary faces) | right_side, rear, rear_side |

## 4. Camera validity

- No view has the target occluded, clipped or illegible. Front, front_corner, aerial, top, left_side, right_side, rear and rear_side all frame the whole envelope with margin.
- The detail views (facade_close, architecture_close, glass_close, corner_dome, cafe_awning, balcony_ironwork, mansard_dormers, roof_court, rear_court) each show their subject legibly.
- interior is dark but legible: the window wall, the court enclosure and a window opening onto the lit court all read.
- The aerial is valid but matches the top.jpg role poorly (P2 #9). front_corner carries the oblique role well.

## 5. Previous-version findings (v003 P1s)

1. **Oculus dormer read blind: RESOLVED.** In corner_dome the oculus inside the pale ring now reads as dark glass with a horizontal glazing bar and a darker upper edge from the ring soffit, which gives a depth cue. Sampled luma: oculus glass RGB about (93,98,100) to (111,116,118). Drum roundels: (73-86). Dome zinc: (162,168,173). Ring: (192,190,185). The opening now sits in the same dark family as the drum roundels and is clearly separated from the zinc. It reads as an opening in roof_court and the front views as well.
2. **Open slots at the four inner court corners: RESOLVED at elevation.** In rear_court the far court corner is a continuous closed junction from coping to floor. Sampling shows no light or void slit there, and the near corners show a continuous wall/floor junction. In aerial, front_corner and roof_court the court elevations show no vertical slots. What remains is a small wall-top pinhole at each corner, visible only from above (P2 #2). It does not reopen the slot.
