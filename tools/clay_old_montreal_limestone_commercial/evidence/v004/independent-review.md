# Independent holistic review: clay-old-montreal-limestone-commercial v004 (RLASM v6.1)

Reviewer: independent; judged only on rendered pixels against the locked sources (`sources/front.png`, `sources/oblique.jpg`, `sources/top.jpg`). I opened all 18 delivered renders and the 4 phone boards at full resolution. I made zoomed crops only in the new folder `/tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/review-crops-v004-82052a16/`. I ignored builder metadata, counts and notes as proof.

## 1. Verdict

**PASS_ZERO_P0_P1**: the v003 P1 (east end pavilion rhythm and plan proportion) is fixed in the pixels, all earlier fixes still hold, and the remaining defects are polish only.

Counts: P0 = 0, P1 = 0, P2 = 8

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P2 | top, front_corner, aerial | The pavilion attic chimney stands on the west slope near the north-west corner. In the source top, the chimney and the skylight both sit on the east slope beside the north-south ridge, with the chimney south of the skylight. | The chimney was moved inboard to the west slope to clear the balustrade, not to the source position. | Move the chimney onto the east slope just south of the skylight, about 1 m east of the ridge, and keep it clear of the balustrade. |
| 2 | P2 | top, front_corner, west_range, rear | The range chimneys stand on or near the ridges. In the source oblique and top, the stacks rise off the eave walls at the cornice line. | Chimneys are placed on the ridge line instead of on the wall line. | Move the range chimneys onto the south and north wall lines at the eave, using the same spacing as the oblique. |
| 3 | P2 | balconettes, end_pavilion_arches | The arched door in the middle of the pavilion's south face has a plain arched transom with no radial bars. The source front shows a radial fanlight over this door, like the windows beside it. | The door assembly does not reuse the fanlight muntin pattern. | Add the radial fanlight muntins to the door transom. |
| 4 | P2 | rear, roofs_dormers (far left) | On the north face of the pavilion (a face no source shows), the arched heads read as dark voids without visible radial fanlight bars. This is weaker than the south and east faces. | The fanlight bars are thin or missing on the north-face arches. | Use the same fanlight muntins on the north-face arches, so all three faces of the pavilion read alike. |
| 5 | P2 | top | The west hip end of the east range, facing the south-west square, has no slope furniture. The source top shows three small vent dormers on that west-facing slope. | The vent dormers were only placed on the north (court) slope. | Add 3 small vent dormers to the west hip slope of the east range. |
| 6 | P2 | front_corner, dome_drum, portico, right_side | The dome, lantern and portico roof are almost the same pale grey as the limestone walls. The source's silver tin against grey stone hierarchy reads weakly. | The tin material value is too close to the stone value. | Shift the tin material to a cooler, slightly brighter and more specular silver within the clay palette. |
| 7 | P2 | left_side | This whole-envelope view crops the bottom edge of the plinth and the ground contact on the west face at the frame edge. The facade is still fully legible, and contact shows in west_range, aerial and rear_side. | Camera target and height are set slightly low and tight. | Pull back or tilt so there is a small strip of ground below the plinth. |
| 8 | P2 | renders/ (set) | The brief's detail list names `facade_close`, `architecture_close` and `glass_close`, but these are not in `renders/`. 18 views were delivered, which matches the brief's stated count. Opening depth and returns are still verifiable in balconettes, east_door, long_facade and interior. | The view list and the camera manifest are out of sync. | Either render the three named closes or drop them from the view list, so the brief and the render set agree. |

No P0 or P1 findings.

## 3. Source conformance checklist

| item | status | view(s) used |
|---|---|---|
| Silhouette (long low hall, square dome block, dome rising well above, pavilion attic over the east end, giant portico pediment) | conforms | front, front_corner, aerial vs oblique/front |
| Storey count (three storeys over a low basement; pavilion with two tall arched tiers inside the range height plus an attic) | conforms | long_facade, front, end_pavilion_arches |
| Plan: offset ranges (west range in line with the dome block; east range stepped south by a full range depth) | conforms. West range about 40.6 m, dome block about 23 m, east range about 67 m, range depth 19.5 m. Source is about 42, 23 and 66 m. | top vs source top |
| Plan: dome block | conforms (square, between the ranges) | top, rear, rear_north |
| Plan: portico (on the south street at the west end of the east range, aligned under the dome block) | conforms (width about 17.5 m against about 18 m in the source) | top, front_corner, portico |
| Plan: north porch | conforms (on the north front of the dome block) | top, rear_north |
| Limestone coursing | conforms (horizontal ashlar course lines in untextured clay) | balconettes, east_door, long_facade |
| Window tiers: barred basement vents | conforms | long_facade, east_door, rear |
| Window tiers: three tiers of six-over-six sashes with stone sills and flat lintels | conforms | long_facade, west_range, left_side |
| Window tiers: pavilion arches with radial fanlights and keystones | conforms on the south and east faces; north face weaker (P2 #4) | end_pavilion_arches, east_door, right_side, rear |
| Pilaster strips | conforms | long_facade, front, west_range |
| Plinth | conforms | long_facade, east_door |
| Sill bands | conforms | long_facade |
| Modillioned eave cornice | conforms | long_facade, end_pavilion_arches |
| End pavilion: flush with the range | conforms | top, front |
| End pavilion: two arched tiers within the range height | conforms | front, end_pavilion_arches, right_side |
| End pavilion: iron grilles on the ground tier | conforms | east_door, right_side |
| End pavilion: arched south door with steps, in the middle bay | conforms; transom lacks a fanlight (P2 #3) | end_pavilion_arches, balconettes |
| End pavilion: iron balconettes on the first tier | conforms | balconettes, east_door, front |
| End pavilion: main cornice continuing the range eave | conforms | end_pavilion_arches, front |
| End pavilion: attic storey with three six-over-six sashes per long face | conforms | end_pavilion_arches, rear, front |
| End pavilion: top cornice, balustrade with pedestals on all four sides, and one closed hipped slate roof | conforms (single north-south ridge, no near-black facets or slots) | front_corner, aerial, top, right_side |
| End pavilion: chimney and skylight | conforms in presence; chimney slope differs from the source (P2 #1) | top, front_corner |
| End pavilion: east pediment springing from the main cornice, full width, round-arched fanlit tympanum window, no oculus | conforms | right_side, front, aerial |
| End pavilion: east door (square, corniced hood on consoles, steps, middle bay) | conforms | east_door, right_side |
| End pavilion: east front rhythm (3 wide bays per tier between broad piers) | conforms | right_side, east_door, front, front_corner, aerial |
| Portico: stepped podium and steps | conforms | portico, front_corner |
| Portico: four giant-order Tuscan columns through three storeys | conforms | portico, front |
| Portico: entablature with triglyphs at the eave line | conforms | portico, front_corner |
| Portico: pediment with oculus above the slate roof; tin roof dying into the range roof | conforms | portico, front_corner, top |
| Portico: arched doorway behind the columns | conforms | portico |
| Dome-block attic: sunk panels, corner pedestals, urns | conforms | dome_drum, rear_north, right_side |
| Drum: round-arched windows between engaged columns, with entablature | conforms (about 16 by visible half-count) | dome_drum, right_side, rear_north |
| Dome: ribs and profile | conforms (ribbed hemispherical profile; tin value weak, P2 #6) | dome_drum, top, front |
| Lantern, cupola and cross | conforms (open colonnetted lantern, cupola, cross) | dome_drum, right_side |
| Roofs: hips | conforms | top, left_side, west_range |
| Roofs: gable ends | conforms (portico gable, pavilion pediment) | front_corner |
| Roofs: chimneys | conforms in presence; position deviates from the source eave-wall stacks (P2 #2) | top, west_range, front_corner |
| Roofs: vent dormers on the court slope | conforms (5 on the north slope of the east range); west hip-slope vents missing (P2 #5) | roofs_dormers, rear, top |
| Roofs: skylight | conforms (west range and pavilion) | top, west_range, front_corner |
| North porch: three arches, flat roof, balustrade | conforms | rear_north, rear |
| Streets | conforms (asphalt band around the block) | aerial, top |
| Squares (cobbled, as a flat clay plane) | conforms | top, west_range |
| Trees: south sidewalk | conforms | top, front |
| Trees: south-west square | conforms | top, west_range |
| Trees: north sidewalk (west part) | conforms | top, rear |
| Materials hierarchy (grey limestone walls, dark slate roofs, iron black, pale tin) | conforms; tin and stone too close (P2 #6) | front_corner, portico, dome_drum |

## 4. Camera validity

- front: valid. The pavilion corner, the long south front, the portico and the dome all read. The dome shows above the range roof to the left of the pavilion and is not clipped.
- front_corner, aerial, top, rear_side: valid. The whole asset is in frame with margin.
- rear: valid. Both building ends are held with a margin: the pavilion and pediment edge at about x = 170 and the west range at about x = 1352 of 1440.
- right_side: valid. The full east front, the dome block east face and the dome are in frame.
- left_side: valid but tight. The bottom edge of the plinth and the ground contact on the west face are cropped (P2 #7). The target is legible.
- Detail views (portico, dome_drum, end_pavilion_arches, balconettes, east_door, long_facade, roofs_dormers, west_range, interior, rear_north): valid. Each target is legible and unoccluded, and opening reveals and depth are visible. Trees overlap long_facade and portico only partly.
- facade_close, architecture_close and glass_close: not delivered (P2 #8). The 18-view count in the brief is met.

No view is invalid.

## 5. Previous-version findings: resolved in the pixels?

| finding | origin | status in v004 pixels |
|---|---|---|
| East front rhythm: 5 narrow bays per tier, door in the 3rd bay, against the source's 3 wide bays between broad piers, door in the middle | v003 P1 | **Resolved.** right_side, east_door, front, front_corner and aerial all show 3 wide bays per tier between broad piers. The ground tier has a grilled arched window, the corniced square door with steps in the middle bay, and a grilled arched window. The first tier has 3 tall arched windows with balconettes. The tympanum window sits over the middle bay. This matches the oblique (3 bays, door in the middle) and the front source. |
| Pavilion east-west length about 0.53 of the range depth, against about 0.77 in the source | v003 P1 | **Resolved.** In the top view the pavilion measures about 178 px (west balustrade to east wall) against a range depth of about 207 px, or about 0.86. The attic inside the balustrade is about 0.65–0.7. The source pavilion measures about 0.8 by the same method. The plan proportion now matches the source closely. |
| Pavilion south and north fronts re-spaced as 3 wide bays, south arched door in the middle; attic with 3 sashes per long face | v004 claim | **Verified.** end_pavilion_arches and front show the south face; rear shows the north face. |
| Pavilion attic roof: one closed hipped slate roof, single ridge, no near-black facets or slots against the balustrade | v002 P1 | **Holds.** front_corner, aerial and top crops show one closed hipped roof, uniform slate and no slots. |
| Pavilion chimney off the balustrade; skylight on the east slope | v004 P2 claim | **Holds** (clear of the balustrade by about 4 m in the top view). The chimney slope still differs from the source (P2 #1). |
| Raking cornice feet trimmed to the horizontal cornice return | v004 P2 claim | **Holds.** No overrun shows in right_side, front or aerial. |
| North street trees on the west part of the north sidewalk | v004 P2 claim | **Holds** (top, rear). |
| Rear view holds both building ends with a margin | v002 P1 | **Holds.** |
| Portico as a giant order through three storeys to an entablature at the eave, pediment above the slate roof, tin roof dying into the range roof | v001 P1 | **Holds** (portico, front_corner, top). |
| End pavilion grammar: two arched tiers within the range height, ground-tier grilles, first-tier balconettes, main cornice continuing the eave, attic with sashes, top cornice, balustrade with pedestals on four sides, east pediment from the main cornice with an arched fanlit tympanum window (no oculus) | v001 P1 | **Holds** (end_pavilion_arches, right_side, east_door, aerial). |
| Dome visible above the range roof to the left of the pavilion in the front view | earlier | **Holds** (front; the cross, lantern, ribbed dome and top of the drum read). |
| v001 conformance: plan, three sash tiers with basement vents, modillioned eave cornice, dome-block attic with panels, pedestals and urns, drum of 16 arched windows, ribbed dome, lantern, cupola and cross, chimneys and vent dormers | v001 | **Holds** (see checklist). |
