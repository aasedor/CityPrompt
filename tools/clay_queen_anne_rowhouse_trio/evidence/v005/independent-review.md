# Independent RLASM v6.1 holistic review: Queen Anne rowhouse trio, v005

**Verdict: VISUAL_REWORK_REQUIRED.** The envelope, the unit rhythm and the gable identity now match the sources. Four clearly visible defects still block approval: a slate pent filling the base of each end gable, the bay caps modelled as flat slabs with open corners, a detached trim strip inside every gable, and black holes at the apex of both side gables.

**Counts: P0 = 0, P1 = 4, P2 = 10**

Evidence used: sources/front.png, sources/oblique.jpg and sources/top.jpg; all 18 renders at full resolution, with 3-4x zoom crops where noted; boards phone-01 to phone-04. Pixel coordinates are given in each render's native 1440x1080 frame.

## 1. Verdict

VISUAL_REWORK_REQUIRED: there are no P0 defects, but four P1 defects remain, two of them carried over in part from v004.

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | front (left gable x 290-480 y 465-500; right gable x 960-1150 y 465-500), gable_close (x 440-1010 y 955-1040), architecture_close (x 1085-1440 y 900-1080), aerial (x 700-800 y 640-700) | A hipped slate pent still sits inside the base of each end gable. It runs between the bottom of the cream or green infill and the first-floor brick, and the kneelers sit at its outer feet. In the sources (front x 545-735 y 235-250; oblique x 650-850 y 455-500 and x 210-340 y 380-410), the infill comes down to a timber fascia that rests directly on the first-floor brickwork, with no slate inside the gable. | The cap over the first-floor bay was kept as a hipped roof, and the gable was set on top of it. | Remove the first-floor bay hip cap under each end gable. Carry the infill down to a green or cream fascia board at the first-floor head, and run the kneelers and bargeboard feet onto that fascia line. |
| 2 | P1 | bay_window (x 255-1190 y 120-235; gap at x 880-890), front (x 255-490 and x 945-1185 y 655-670), facade_close (x 690-1330 y 475-510), front_corner (x 625-750 y 760-780) | The cap between the ground and first floors of each canted bay is three flat grey rectangular boxes with no pitch. At each cant corner the boxes are open, with a visible gap showing the pilaster behind (bay_window zoom). The sources show a substantial sloped slate hip cap that projects around the bay (front x 560-765 y 410-455; oblique x 655-860 y 595-680). Per the brief, this cap is an identity element. | The cap was built from extruded box segments, one per face, rather than as a hipped roof over the bay polygon. | Build one hipped slate roof over the bay polygon: about 30-40 degrees pitch, mitred hips at the cant corners, a projecting eave with a fascia, and its back edge flashed into the wall. |
| 3 | P1 | gable_close (x 615-700 y 270-490), architecture_close (x 1290-1340 y 280-460; left gable x 140-180 y 300-520), roof_contact (x 600-620 y 630-760), front (inside the rakes of all three front gables) | A thin cream strip leaves each rake at the apex. It diverges from the bargeboard, with slate visible between them, and ends in mid-air partway down the gable. This reads as a floating part on every gable. | The inner board of the bargeboard (or the infill edge trim) is mis-rotated or offset from the rake plane and is not cut to the infill. | Align the inner trim with the rake so it lies flush against the underside of the bargeboard along its full length, from the apex to the kneeler, or delete it. |
| 4 | P1 | right_side (black diamond at x 712-724 y 266-282, directly under the chimney), left_side and party_wall (black slot at x 713-724 y 279-287; front_corner x 377-385 y 245-253) | Both side gables (the east end gable and the west party wall) show a black hole at the apex. On the east gable the two coping pieces fail to meet. The three front gables no longer have this hole. | The coping or verge mitres are short at the ridge, and the chimney base leaves a void. | Extend and mitre the coping to close at the apex. Fill the gable up to the underside of the ridge and the chimney base. |
| 5 | P2 | front gables (dark sliver under the finial blocks), gable_close (x 690-720 y 265-300) | There is a small dark V between the bargeboard tops and the finial block. | The bargeboards stop short of the apex. | Extend the bargeboards under the finial block. |
| 6 | P2 | bay_window (x 1080-1150 y 860-880), front_corner (x 625-640 y 845-850) | A black slot appears where the plinth blocks meet at the corners of the bay cants. | The plinth segments are not mitred. | Mitre the plinth around the bay polygon. |
| 7 | P2 | rear (x 207-213 at y 500, 646, 686), party_wall (x 285-300 y 370-380, plus stubs at y 520, 640, 800) | The rear band ends and the west kneeler of the rear cross gable overrun the west party-wall plane by about 6 px (roughly 10 cm). There is no slate slab past the plane now. | The band length and kneeler position are not clipped to the party-wall plane. | Clip all trim to x <= the party-wall plane. |
| 8 | P2 | front (x 255-280 y 560, 625, 727), front_corner (x 625-640 y 705-715 and 742-750) | Short cream band stubs float on the west cant of the west bay. They touch neither the window nor the corner. The sources wrap their bands continuously around the bay. | The band segments are not trimmed to the cant. | Run the bands continuously around all three bay faces, or omit them on the cant. |
| 9 | P2 | glass_close (window corners x 425/925, y 225/945), facade_close (all window corners) | Black dots sit at the four corners of every window frame, and the reveals are shallow. | There are reveal mitre gaps. | Close the reveal corners. Deepen the reveal to about 1 brick (0.11 m) or more. |
| 10 | P2 | right_side (one window per floor, x 790-845), front_corner/aerial east face | The east wall has one window per floor and a cream coping. The sources show two or more narrow windows per floor on this face (front x 830-930; oblique x 900-1010) and a green verge on the main east gable (front x 900-970 y 120-340). | The fenestration on the secondary face was simplified. | Add a second narrow window per floor, and colour the east verge green. |
| 11 | P2 | facade_close, front | The window surrounds are lintels and sills only. The sources also dress the jambs in buff brick in alternating blocks. | This was omitted. | Add alternating buff jamb blocks to the front windows. |
| 12 | P2 | architecture_close, gable_close | The bargeboards are plain wide boards. The sources show pierced or scalloped fretwork bargeboards and pendant finials. Acceptable for clay. | The models are simplified. | Optionally add a cut-out silhouette to the bargeboard edge. |
| 13 | P2 | rear_yards (x 925-975 y 760-820; x 1340-1385 y 705-760; x 380-435 y 830-890) | Stacked cream stubs appear where the rear bands terminate beside the yard divider walls. | The band ends are not resolved against the dividers. | End the bands cleanly at the divider face. |
| 14 | P2 | top, front_corner, aerial | The front gardens are bare brown soil with a few small bushes. The sources show dense planting and small trees behind the fence. | The landscape is sparse. | Add massed shrub volumes and one small tree in each end garden. |

## 3. Source conformance checklist

| item | status | view used |
|---|---|---|
| Silhouette | Conforms. Three front cross gables over a slate main roof, a blank west party gable and an east end gable. Matches the east-end portion of the oblique and top sources. | front, front_corner, aerial vs oblique/top |
| Storey count | Conforms. Two brick storeys plus an attic in the gables. | front vs source front |
| Unit rhythm and doors | Conforms. There are three individual doors with stoops, gates and handrails: red door beside the west bay, green door beside the east bay, and a door between them. The four first-floor windows across the middle match the source. | front, entrance_steps, facade_close |
| Bays and gables | Deviates. The two-storey canted bays and the three gable treatments now match: cream infill with a round-headed window, brick with a blind arch, and green infill with a round-headed window. But the bay caps are flat boxes with open corners (finding 2), a slate pent sits inside the end-gable bases (finding 1), and floating rake strips appear (finding 3). | front, bay_window, gable_close, architecture_close |
| Dormer and roof | Mostly conforms. The middle brick gable with its blind arch sits in the dormer position. The slate main roof has its ridge, and there are front and rear cross gables. Apex defects are noted in findings 4 and 5. | front, top, roof_contact |
| Chimneys | Conforms. Two brick stacks with cream caps and pots, on the ridge at the party lines. | front, rear, roof_contact |
| Fence and gardens | Conforms, with P2. The iron fence stands on a low base, with gates and hedges. Planting is sparse. | front, entrance_steps, top |
| Rear | Coherent. Three brick rear cross gables with kneelers, a window and a door per unit, and walled yards. | rear, rear_side, rear_yards, top |
| Materials hierarchy | Conforms. Red-brown brick has cream head, impost, sill and string bands on each storey. There are buff quoins at the east corner and on the bay pilasters, slate roofs and green timber. The jamb dressings are missing (P2). | front, facade_close, right_side |

## 4. Camera validity

All 18 views are valid. None has the target occluded, the asset clipped or the subject illegible. The party_wall view is tight on the blank wall but shows the plane, the verge and the yard junction. The interior view shows a bay with real depth and the fence beyond.

## 5. v004 findings, re-checked against the v005 pixels

| v004 P1 finding | status | evidence |
|---|---|---|
| Slate slab and rear cross-gable verge projected past the west party-wall plane | Resolved (P2 residual) | top and front_corner show no slab past the plane. The rear-gable kneeler and band ends overrun by about 6 px (finding 7). |
| Front slate pent wrapped the east corner and stopped over a black slot | Resolved | In front (x 1100-1200 y 440-700) the pent stops at the kneeler, the quoins continue, and there is no slot. The only black slot now is at the bay plinth corner (finding 6, P2). |
| A slate band at the eaves ran through the base of every gable, with the bargeboard feet hanging below it, where the sources land them on kneelers | Partly resolved | The kneelers are added and the bargeboard feet land on them. A slate pent still fills the base of each end gable (finding 1). |
| Every gable apex showed a black notch | Partly resolved | The three front gables are closed apart from a tiny P2 sliver. The east and west side gables still show black apex holes (finding 4). |
| The front brick was a uniform red field where the sources band each storey in cream with buff quoins and surrounds | Resolved (P2 residual) | Each storey now has head, impost, sill and string bands, with east-corner quoins and bay pilasters. Only the jamb dressings are absent (finding 11). |
| One gable treatment was reused for all three, with an undersized infill and shutters | Resolved | The end gables have full-height cream and green infill with round-headed windows. The middle gable is brick with a blind arch, and there are no shutters. |
| The canted bays stopped at the ground floor | Resolved | Both end bays rise through the first floor under the end gables (front, front_corner, top). |
