# Independent holistic review: clay-prewar-apartment-tower v003 (RLASM v6.1)

Reviewer: independent; I did not build this candidate. I judged rendered pixels only, against `sources/front.png`, `sources/oblique.jpg` and `sources/top.jpg`. I opened all 18 renders and the 4 phone boards at full resolution. I made zoomed crops (read-only copies) in `/tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/indep-review-v003-crops-k7q2/`.

## 1. Verdict

**VISUAL_REWORK_REQUIRED**. All five v002 findings are fixed. However, the rebuilt south-east corner and the new cornice corner blocks introduce three clearly visible P1 defects at the building's most visible corner and at every cornice corner.

Counts: P0 = 0, P1 = 3, P2 = 9

## 2. Findings

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | architecture_close, front_corner, front, right_side, aerial | **The south-east corner reads as a different building.** On both street faces the corner bay is a solid, full-height, plain white limestone pier. The windows sit in deep stone slots, and no brick shows from storey 3 to the cornice. Between the two projecting bays, the real building corner is a narrow re-entrant notch with the quoin strip set back inside it (crop `r_arch_corner.png`). From front and front_corner the corner reads as a wide white stone tower with a vertical groove. Both sources show a salient red-brick corner with quoins. The windows next to it on each face have individual eared stone surrounds, with brick between each surround and the corner (`src_front_corner.png`, `src_obl_corner.png`). The materials hierarchy is inverted at the most visible corner. | The bay was modelled as a solid stone slab offset outward from each face. The two offsets leave the corner square unfilled, and the bay face carries stone material instead of brick. | Rebuild each corner bay as a brick wall plane, either flush or with a shallow projection whose return reaches the true arris. Give each window its own stone surround (eared jambs, head, sill, apron panel). Keep the corner salient, and put the quoins on that outer edge so no notch remains. |
| 2 | P1 | architecture_close (crop `r_arch_corner.png`) | **Small stone cubes and a short slab stub float or collide inside the corner notch at every storey,** where the sill and band courses of the two corner bays end. They read as loose fragments stuck to the quoin strip. | Band and sill end-caps are generated from each bay's extents and clipped against the notch instead of being returned or mitred. | Remove the notch (finding 1). Then return or mitre every band and sill course around the salient corner, or stop each one cleanly at the bay return. Check all storeys. |
| 3 | P1 | cornice_balustrade, architecture_close, front (all four corners) | **An oversized plain stone box stands at each corner of the cornice.** It projects past the corona and drops below the modillion bed, so the modillion cornice stops on both sides of the box instead of wrapping the corner. The box overlaps the heads of the top-storey windows next to each corner (crop `r_corn_corner.png`: about a third of the right window head is hidden). At the south-east corner the pedestal is a second plain cube on top and the urn is two stacked cylinders (`r_arch_top.png`). The source cornice wraps the corner continuously, with a pedestal and urn only above the corona. | A corner block was sized to hide the old junction gap, not to the cornice profile. | Mitre the fascia, corona and modillion bed around each corner as one continuous profile, with a corner modillion. Limit the corner mass to the parapet pedestal above the corona. Keep the cornice soffit above the top-storey window heads. |
| 4 | P2 | entrance_marquee | The east end of the marquee covers the head of the corner-bay ground-floor window, and the double door is off-centre under the canopy. | Marquee width is set wider than the door bay. | Shorten the marquee to the door bay plus sidelights, or centre it on the door. |
| 5 | P2 | tank_house, front, front_corner | The tank house is roughly cubic. In the oblique source it is noticeably taller than it is wide, and its corner stones read as smooth strips rather than alternating quoins. | Height parameter is too low. | Raise the tank house body by about 20–30%. |
| 6 | P2 | top, tank_house | The catwalk's short stair is at the north-west end. In the source the stair drops on the east side near the plant units. Some rail posts render near-black instead of the light rail colour. | Stair side is mirrored, and stray posts use a dark material. | Move the stair to the east leg and give the posts the rail material. |
| 7 | P2 | top vs front/oblique | The top source puts the marquee at mid-south-face, while front and oblique put it near the south-east corner. The build follows front and oblique (two of three sources). | The sources conflict. | Accept, and record the source conflict. |
| 8 | P2 | limestone_base, entrance_marquee | The sources show brick panels between stone pilasters in the corner pavilion of the base. The render's base is all channel-jointed limestone, which matches the brief text. | Simplification to match the brief. | Optional: add brick panels in the corner pavilion. |
| 9 | P2 | rear_court, rear | Rear and west windows are 2-over-2, while the street faces are 1-over-1. This is coherent but inconsistent. | Separate window module. | Optional: unify the window modules. |
| 10 | P2 | rear (crop `r_rear_base.png`) | The areaway railing ends at the north-east in a diagonal stair-like rail running down to grade. | Railing end-cap. | Stop the railing with a newel post. |
| 11 | P2 | front_corner, aerial | The building fills only about a quarter of the frame. It is legible, but roof and base detail are small. | Wide framing. | Tighten the framing. |
| 12 | P2 | limestone_base | A street-tree trunk and canopy cover one bay and the upper third of the frame. Rustication is still legible. | Camera placed behind the tree. | Shift the camera half a bay. |

## 3. Source conformance checklist

| item | status | view(s) used | note |
|---|---|---|---|
| Silhouette | conforms | top, front, front_corner vs top/oblique | Plan aspect is about 1.27:1 in both the render and the source top. The tank house is central, slightly north, and about 33% of the roof width in both. |
| Storey count | conforms | front, right_side, left_side, rear | 12 storeys: 2 limestone + 10 brick, with a belt course and a band under the top storey. |
| Base and rustication | conforms | limestone_base, entrance_marquee, front | Two-storey channel-jointed limestone base with tall windows (see P2 #8). |
| Entrance and marquee | conforms | entrance_marquee, front, front_corner, top | Dark marquee on two tie rods over a glazed double door, in the second bay from the south-east corner, under the south balcony stack (P2 #4, #7). |
| Window rhythm | conforms (except SE corner bays) | front, right_side, rear, facade_close | Regular bays: 10 on the south face, 8 on the east face, 10 on the north face. No halved windows. |
| Lintels and sills | conforms | glass_close, facade_close, fire_balconies | Flat stone lintels and sills, dark 1-over-1 sash, visible reveals (architecture_close, interior). |
| Quoins | deviates at SE; conforms elsewhere | architecture_close (SE); fire_balconies, cornice_balustrade, left_side, rear | At the south-east corner the quoins are set back in a re-entrant notch (P1 #1). |
| Stone bay | deviates | architecture_close, right_side, front, front_corner | Solid full-height stone piers instead of stone-framed windows on brick (P1 #1). |
| Iron balconies | conforms | fire_balconies, front, right_side, front_corner | South stack sits over the entrance bay; east stack is at about 63–75% along the face, matching the source's 65–82%. Railings and slabs show depth and attach to the wall. |
| Cornice and balustrade | deviates | cornice_balustrade, architecture_close, front | Modillion cornice, balustrade, pedestals and urns are present, but every corner is a plain block that interrupts the cornice and overlaps window heads (P1 #3). |
| Tank house | conforms | tank_house, top, front, front_corner | Brick body, stone quoins, copper pyramid with standing seams and eave band, small windows, door at deck level (P2 #5). |
| Catwalk and chimneys | conforms | tank_house, cornice_balustrade, top, rear_side | Light grating on posts, light rails, wrapping west, south and east, with a stair (P2 #6). Three brick chimneys with clay pots in source positions (two on the north edge, one south-west of the tank house). Four plant units north of the tank house. |
| Materials hierarchy | deviates at SE corner | front, front_corner, architecture_close | Brick over a limestone base holds on all faces except the south-east corner bays, which are all white stone (P1 #1). |
| Areaway railing (east) | conforms | right_side, rear | Iron railing along the east base (P2 #10). |

## 4. Camera validity

- No view is invalid. In every render the target is legible and unclipped.
- entrance_marquee now frames the whole marquee, both tie rods, the door and the sconces.
- front_corner and aerial are legible but loosely framed (P2 #11). limestone_base is partly occluded by a tree (P2 #12).
- interior, glass_close, facade_close and rear_court are valid close views.

## 5. Previous-version (v002) findings: resolution in pixels

| v002 finding | resolved? | evidence |
|---|---|---|
| P1: full-height stone pier over a window column, halving it on every brick storey | **Resolved** | front, right_side, facade_close and rear show every brick-storey window at full width with no pier across it. However, the new corner-bay execution adds P1 #1. |
| P1: entrance group mid-face instead of hard by the SE corner, with a wide stone-framed bay at the corner of the east face | **Resolved (placement)** | front, front_corner and top show the marquee and the south balcony stack in the second bay from the south-east corner. A stone corner bay sits on the south face and at the south end of the east face. Their material and topology are wrong (P1 #1, #2). |
| P1: black slit and stepped coronas where the cornice meets the corner pedestal | **Resolved as stated, superseded** | No dark slit or stepped corona is visible in cornice_balustrade or architecture_close. The replacement corner block is a new P1 (#3). |
| P1: rooftop catwalk a near-black ring at deck level | **Resolved** | tank_house, cornice_balustrade, front_corner and top show light bar-grating raised on posts, light rails, and a short stair (P2 #6 on stair side and dark posts). |
| P1: entrance_marquee camera clips the marquee and door | **Resolved** | entrance_marquee shows the marquee, tie rods and door whole. |
