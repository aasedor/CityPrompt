# Independent RLASM v6.1 holistic review: clay campus shed office, v005

Reviewer: independent; I did not build this. Evidence used: only the three locked sources (`sources/front.png`, `sources/oblique.jpg`, `sources/top.jpg`), the 18 renders in `renders/` and the 4 phone boards in `boards/`. I opened all of them at full resolution and cropped the entrance, roller-door/ramp and north-wall areas to check them. No build code, reports or notes were read.

## 1. Verdict

**VISUAL_REWORK_REQUIRED**: 0 P0, 4 P1, 8 P2. Four of the five v004 P1s are fully fixed. The south ground-storey material fix is only partial. Three new P1 defects can be seen in the pixels: a black full-height element at the entrance, a roller door that the ramp cuts through, and north-wall windows that run into the columns.

Counts: **P0 = 0, P1 = 4, P2 = 8**

## 2. Findings

| # | severity | view(s) and approx. pixels | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | entrance_corner x615-640, y0-785; left_side x965-978, y475-705; front_corner x~535-545, y555-770; terrace_roof x45-75, y840-1080 | The portal column between the west window bay and the X-brace corner bay reads as one black element, about one column wide, running from above the parapet beam to below the plinth. The galvanised column there cannot be seen: the frame beams stop against the black strip on both sides. The strip passes through the entrance canopy and splits the plinth (entrance_corner y760-785). The sources (oblique x450-465, front x370-380) show a **galvanised** column at this position, running down between the two door sets. | The new downpipe (the v004 P2 fix) was placed on the column face. It is the same width as the column and is charcoal/black, so it hides the column completely. | Move the downpipe to one side of the column (for example the inside corner against the cladding), make it about 1/3 of the column width and galvanised/light grey like the valley downpipes, and stop it at a shoe above the plinth. The galvanised column must stay readable from the parapet to the ground, and the canopy should run around the column, not appear pierced by a pipe. |
| 2 | P1 | facade_close x790-970, y740-810; front x445-540, y570-640 (crop of the ramp bay) | The roller door in the first bay east of the corner has a horizontal bottom edge partway up the sloped ramp. On the west half of the door there is a wedge-shaped gap above the ramp surface. On the east half the ramp surface crosses the door leaf, so the lower part of the door is buried in the ramp. The door therefore cannot open onto a level surface. | The door sill is set at dock level, but the ramp is aligned along the wall face in front of the door, not ending before it. | Either (a) end the ramp at a level landing at dock height before the door bay and set the door sill on that landing, or (b) set the door sill to ground level with the ramp passing outside the door bay. Either way, the bottom edge of the door must meet one level surface along its full width. |
| 3 | P1 | front x268-410, y560-650 (corner bay) and x420-565, y560-650 (ramp bay); facade_close x240-720, y490-870 and x740-1010, y490-800; glass_close y850-1080 | The dock bays further east are now light-grey precast (fixed). The corner-window bay is still **charcoal cladding** on both sides of the large window and above it, with only a thin light upstand under the sill (about 17% of the storey height). The ramp/roller-door bay is fully charcoal. Sources: front x555-690, y430-625 shows light-grey precast filling roughly the lower 35-40% of the corner bay below a lower sill, with precast at the jambs. Oblique x645-755, y530-730 shows the same, and the roller-door bay (oblique x760-850) is precast-grey around the door. | The precast material was applied only to the dock bays. The corner-window bay kept the charcoal panel, with a shallow plinth. | Make the ground storey of the corner bay and the roller-door bay light-grey precast. Raise the corner window sill so the precast upstand is about 35-40% of the ground-storey height, and use precast jambs/lintel at the window, matching the dock bays. Keep the charcoal cladding above the mid-height beam. |
| 4 | P1 | rear x330-388, y505-555 and x1053-1110, y505-555; rear_side x665-710, y600-645 and x1110-1140, y510-550 | On the north wall (not shown in any source, so judged for coherence), the upper windows of the end bays run into the portal columns. The column covers part of the glazing, and the window sill sticks out past the other side of the column (crop of rear x300-480). This is an opening/structure intersection of the same kind as the "door split by a column" that v002 rejected. | The window centres on the north wall are set at bay edges, not inset from the column lines. | Inset each north-wall window so it sits fully inside its bay, with at least one mullion width of clear cladding on each side of the column. Check the east-end elevation for the same problem. |
| 5 | P2 | front x1550-1840, y175-300 (crop); top source x750-880 | The second south X-brace is in the last (east-end) bay. The top source puts it in the 4th canopy bay, with a rod bay to the east. The brief's wording does accept "east-end bays". | Carried over from v004. | Optional: move the X-brace one bay west to match top.jpg. |
| 6 | P2 | right_side x925-1085, y440-680 | The north gable bay on the east elevation has no windows, while the other two gable bays have two storeys of windows. | Carried over from v004. | Add the two-storey window pair to match the rhythm of the other gable bays. |
| 7 | P2 | left_side x975-1060 vs x815-975; top x295-325 / y745-815 vs y620-745 | The corner X-brace bay on the west face is about half the width of the window bay, so the terrace depth is about 0.6 of the monitor pitch. In the sources the corner bay is equal to or wider than the window bay (front x240-370 vs x375-530), and in top.jpg the terrace is about 1.1x the monitor pitch. | The bay grid was compressed when the south monitor was moved onto the window bay. | Widen the corner bay or terrace to about the window-bay width. |
| 8 | P2 | entrance_corner (545,445)-(600,390) | The middle tie rod of the entrance canopy ends on the transom glazing frame, not on a frame member. | The rod anchor is placed at transom height. | Run the rod up to the galvanised beam or column and add a small plate. |
| 9 | P2 | architecture_close (290,410), (1145,340); dock_contact | The dock-canopy tie rods meet the column faces with no anchor plate or clevis. | Carried over from v004. | Add small plates/clevises. |
| 10 | P2 | interior x210-355, y695-820 and x605-745, y755-930 | The desk monitors float above the desktops (cast shadow is detached, no stand). | No stand geometry. | Add a stand/foot touching the desk. |
| 11 | P2 | terrace_roof x715-745, y415-455 | The rooftop-unit duct ends directly in the clerestory glass of the south monitor. In top.jpg the duct drops into the opaque base of the monitor. | The duct end is set too high. | Lower the duct termination into the opaque upstand under the glazing. |
| 12 | P2 | dock_contact x0-225, y535-560 | The dock edge west of the central stair (the ramp-top landing) has only a black edge, with no yellow nosing. The yellow nosing starts east of the stair. | The nosing strip is only on the main dock segment. | Continue the yellow nosing along the landing edge. |

## 3. Source conformance checklist

| item | status | view(s) used |
|---|---|---|
| Silhouette (sawtooth over braced office box) | conforms. There are four south-glazed monitors. The southernmost monitor rises off the box over the west window bay, and the terrace sits over the corner bay. | front_corner, left_side, top, aerial vs oblique/top.jpg |
| Storey count | conforms. The office box has two storeys and the gable bays have two storeys of windows. | front, left_side, right_side |
| Bay rhythm, south | conforms in count: corner X-bay plus 5 canopy bays. Deviations: X-brace bay index (P2 #5) and corner-bay material (P1 #3). | front, top vs top.jpg, front.png |
| Bay rhythm, west | conforms in count: 3 gable bays + window bay + corner bay = 5. Deviates in proportion (P2 #7) and in the black intermediate column (P1 #1). | left_side, front_corner vs oblique |
| Entrance and canopy | partly deviates. The canopy is on the west face only and covers both bays, and the transom glazing band is now present in both bays. Problem: the black full-height element between the two bays (P1 #1). | entrance_corner, left_side, front_corner |
| Dock | conforms. There is a raised dock with yellow nosing (gap noted in P2 #12), light-grey precast dock bays and a cantilevered dock canopy starting east of the corner bay. | dock_contact, front, aerial |
| Ramp and stairs | deviates. The ramp cuts the roller door (P1 #2). The two stairs (central and east end) are present and touch the ground correctly. | facade_close, front, dock_contact, aerial |
| Portal frame and braces | partly deviates. X-braces appear only in the corner and east-end bays, and thin tie rods appear in the canopy bays. Nothing pierces the canopy except the black downpipe (P1 #1). | front, facade_close, architecture_close, terrace_roof |
| Monitors and clerestories | conforms. The glazing has mullions and transoms and the frame stands proud of the glass. The reveal is shallow but readable. | clerestory_close, sawtooth_contact, terrace_roof |
| Terrace and rooftop plant | conforms. There is a rail on the west and south, and a rooftop unit with ductwork at the west end. The terrace is shallow (P2 #7) and the duct ends in glass (P2 #11). | terrace_roof, top, front |
| Gable ends | the east and north faces are not visible in any source. They are coherent apart from P1 #4 and P2 #6. | right_side, rear, rear_side |
| Materials hierarchy | deviates. There is charcoal where the sources show precast on the corner-window and roller-door bays (P1 #3), and black where the sources show a galvanised column (P1 #1). | front, facade_close, entrance_corner |

## 4. Camera validity

All 18 cameras are valid. The target is legible in every view, and no view is occluded or clipped badly enough to hide what it is meant to show. The interior and stairs cameras are now inside the envelope and show desks, the stair, the slab opening and the west-entrance glazing with its transom band. In sawtooth_contact the lower storey is cropped at the frame edge, but the subject of that view (the monitor and gable junctions) is fully visible.

## 5. Prior findings, judged from the pixels

| prior finding | source review | status in v005 | evidence |
|---|---|---|---|
| Southernmost monitor one bay north of the box; should rise off the box over the window bay, with the terrace only over the corner bay (west face 5 bays) | v004 P1 | **resolved** | left_side x815-975, front_corner, top y620-820 |
| Entrance transom glazing band missing in both west bays | v004 P1 | **resolved** | entrance_corner x345-600, y400-445 and x665-915, y355-455 |
| Canopy tie rod crossed the upper window | v004 P1 | **resolved**. The rods stay below the upper window, though one ends on the transom frame (P2 #8). | entrance_corner |
| South ground storey charcoal where the sources show light-grey precast (dock bays and under the corner window) | v004 P1 | **partly**. The dock bays are fixed. The corner-window bay has only a thin upstand with charcoal jambs and head, and the roller-door bay is still charcoal (P1 #3). | front, facade_close, dock_contact |
| Interior camera outside the envelope | v004 P1 | **resolved** | interior, stairs |
| Second south X-brace bay index | v004 P2 | not resolved (P2 #5) | front |
| North gable bay without windows | v004 P2 | not resolved (P2 #6) | right_side |
| No yellow dock nosing | v004 P2 | **resolved** on the main dock; small gap at the landing (P2 #12) | dock_contact, aerial |
| Dock-canopy rod anchors | v004 P2 | not resolved (P2 #9) | architecture_close |
| Shallow clerestory reveal | v004 P2 | **resolved** (frame depth readable) | clerestory_close |
| Floating task chair | v004 P2 | **resolved** (chairs have stems to the floor). Floating desk monitors are a new finding (P2 #10). | stairs, interior |
| No downpipes | v004 P2 | **partly**. Valley downpipes are present on the west face, but the new entrance downpipe causes P1 #1. | left_side, entrance_corner |
| Braces piercing the canopy | v002 | **resolved** for the braces and rods; the downpipe now pierces the canopy (P1 #1) | front, architecture_close |
| Door split by a column | v002 | **resolved** (each door sits fully within its bay). The similar defect has moved to the north-wall windows (P1 #4). | entrance_corner |
| One-bay west face | v002 | **resolved** (5 bays) | left_side |
| Wrap-around canopy | v002 | **resolved** (west face only) | front, front_corner |
| X-braces in every bay | v002 | **resolved** | front, facade_close |
