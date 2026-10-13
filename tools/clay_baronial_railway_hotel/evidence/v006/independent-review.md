# Independent holistic review - clay-baronial-railway-hotel v006 (RLASM v6.1 architectural clay)

Reviewer: independent (did not build). Evidence: the three locked sources, all 18 renders opened at full resolution, the four phone boards, and zoomed crops written only to a new scratch folder (`scratchpad/review-v006-crops/`). Builder notes, JSON evidence, counts and hashes were not used as proof.

## 1. Verdict

**PASS_ZERO_P0_P1** - the two v005 P1 defects are gone from the pixels (porch walls and jamb piers now land on a paved slab at grade; no black void lines remain in the carriage passage or under the court-side ring), and no new P0 or P1 defect appears in any of the 18 views.

Counts: P0 = 0, P1 = 0, P2 = 7

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P2 | porte_cochere, facade_close, rear_court | Pin-sized pure-black notches between voussoirs: about 14 px at the crown of the street arch ring (≈740,318), 10 px at the west haunch (≈565,407), 7 px at the east haunch (≈893,449); 6 px notch at the crown of the court-side ring (≈730,510). Only legible in close-ups; not the line-type voids of v005. | Wedge voussoir blocks don't fully close against each other or against the wall behind at the crown and haunches, so the empty space behind them shows. | Add a thin backing plate or extrude the ring 2–3 cm into the wall, or give the voussoirs a slight overlap at the joints. |
| 2 | P2 | porte_cochere | A row of 2–4 px black dots runs up the joint between the east passage wall and the east jamb pier at each string-course height (≈886–896, y 585/688/792/898/932). | String-course strips end at the reveal with an open end, or stop just short of the passage wall. | Cap or trim the string courses at the reveal, or stop them flush with the pier face. |
| 3 | P2 | porte_cochere, facade_close | Inside the passage, the inner (tower-wall) pointed arch reads as a wedge hanging down to impost level, with a clean cut foot and nothing under it, in front of the lit east wall. | The transverse arch's intrados sits lower than the porch vault and its foot has no respond. | Add a shallow impost or respond under the inner arch's foot, or match its intrados to the vault so it doesn't read as a pendant. |
| 4 | P2 | front, entrance_tower, facade_close | The tower front between the porch parapet and the crown is plain: windows and a blank tablet only. The source's central corbelled oriel or niche stack and the carved panels are missing. | Simplified to keep the tower massing legible. | Optional: add one corbelled oriel box with a corbel cone on the tower axis at about the 4th–5th storey. |
| 5 | P2 | front, front_corner, roof_court | The roof masses behind the crow-stepped gables are chunky, irregular slate facets where the cross-gables meet the main roofs, not the clean steep cross-ridges in the oblique source. | Boolean or hip intersections of the cross-gable roofs with the main roofs. | Give each cross-gable a simple ridge running back to the main slope, with a clean valley. |
| 6 | P2 | rear_court | The low-poly court tree hides the east half of the court-side arch and its ring, so the ring can only be checked on the west half and the crown. | The camera is placed beside the tree. | Move the camera about 2 m west or raise it so the whole arch clears the canopy. |
| 7 | P2 | front | The building fills only the upper ~55 % of the frame, leaving a large empty foreground. The asset is still whole and legible. | Lens shift or framing. | Tilt or shift the frame down to centre the asset. |

No P0. No P1.

## 3. Source conformance checklist

| Item | Status | View(s) used | Note |
|---|---|---|---|
| Silhouette | conforms | front vs source front; front_corner/aerial vs oblique; top vs top | Quadrangle with an open court; the tall tower breaks the skyline above the ridges; conical caps punctuate the corners and flanks. |
| Storey count | conforms | front, left_side, right_side, rear, crow_gables vs source front | Four full storeys under the cornice, plus an attic of dormers and gable windows and an upper gable window level. This matches the source's ranges (tower taller). |
| Entrance tower and porte-cochere | conforms | front, front_corner, aerial, top, porte_cochere, facade_close | Square tower about 0.3 of the way along the south face (top). Lower crenellated porch projection with a pointed arch, voussoir ring and impost piers. The passage runs through to the court (court tree and window visible through the arch in front; matching court arch in rear_court). The tower front lacks the source oriel (P2 #4). |
| Tower tourelles and parapet | conforms | entrance_tower, glass_close, front | Crenellated parapet on a corbel table. Round crenellated bartizans with corbel cones at the front corners. Taller round tourelle with conical slate cap at the rear corner, as in the source front and top. |
| Corner tourelles | conforms | front, corner_tourelle, architecture_close, left_side, right_side, rear | Round tourelles corbelled out above the first storey (cone corbels at about the first-floor head), with conical slate caps and finials at every corner, plus intermediate flank tourelles on the long faces as in the oblique source. |
| Crow-stepped gables | conforms | crow_gables, front, left_side, right_side, rear, roof_court | Wall gables rise through the eaves with stepped skews and windows in two levels. A court-side gable faces the court, as in the top source. |
| Roof slopes and dormers | conforms (P2 #5) | front_corner, aerial, roof_court, rear | Steep slate roofs with a ridge, gabled dormers and chimney stacks. The cross-gable roof intersections are coarse. |
| Window rhythm and surrounds | conforms | facade_close, glass_close, front, sides | Regular vertical bays of sash windows with four-light glazing bars, set in stone surrounds with hoods and sills. The glass is recessed behind the frame and the surround returns are visible. |
| Court | conforms | top, aerial, roof_court, rear_court | Open paved court with four trees, matching the top source. Court elevations carry the same window grammar. The court arch opening has depth. |
| Fence and lawn | conforms | front, front_corner, aerial, porte_cochere, top | Iron fence on a low wall with lawn strips and trees along the south and west streets. The lawn stops at the gate piers and does not run under the porch. |
| Materials hierarchy | conforms | all | Pink-grey granite mass with horizontal rustication grooves. Lighter stone dressings (surrounds, string courses, voussoirs, corbels). Blue-grey slate, grey glass and lead flat on the tower. This is the source palette in clay. |

## 4. Camera validity

- Whole-envelope views (front, front_corner, aerial, top, left_side, right_side, rear, rear_side) all show the full asset unclipped and legible. In front, the asset sits high in the frame (P2 #7) but nothing is cut off.
- Detail views (facade_close, architecture_close, glass_close, entrance_tower, porte_cochere, corner_tourelle, crow_gables, roof_court, interior) all show their target unoccluded and legible.
- rear_court: the target court is legible. The court-side arch is about half hidden by the tree canopy (P2 #6). Its west jamb, west ring and crown are visible and the passage depth reads, so the view is valid.
- interior: a generic room with sash windows looking onto the court tree. It is legible and valid.

## 5. Previous-version (v005) findings - resolution in the pixels

| v005 finding | Resolved? | Pixel evidence |
|---|---|---|
| P1: porch walls and jamb piers stopped short of the ground at the street threshold (a pure-black slot under the porch wall; the lawn running under the east pier and flank wall) | **Resolved** | Both jamb piers and both porch flank walls in porte_cochere, front (crop of the porch base), front_corner and aerial land on a continuous grey paved slab that runs under the projection and out to the kerb. There is no black slot: near-black pixel scan of the porch base finds none. The lawn strip ends behind the gate pier on each side and does not run under the east pier or the flank wall (front_corner, aerial crops). |
| P1: pure-black void lines inside the carriage passage along the vault and west side-wall join, and under the court-side arch ring | **Resolved** | In porte_cochere, the vault and west-wall junction reads as a shaded brown crease, not a black line. A near-black (<25) cluster scan of the whole passage region (x460–970, y290–970) finds only 47 px in 8 isolated pinholes, the largest 14 px, and all on the street ring or string-course ends (P2 #1, #2). There are no lines along the vault or side walls. In rear_court, the court-side ring sits against the court wall face with no black seam under it. Only a 6 px crown notch remains (P2 #1). The east half of that ring is hidden by the tree (P2 #6). |

v005 renders were not available to this reviewer, so the check is against the brief's description of v005. No new contact, void or envelope defect was found in any whole-envelope or detail view.
