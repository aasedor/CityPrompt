# Independent holistic review: clay energy centre v009 (RLASM v6.1)

Reviewer: independent; judged only rendered pixels (renders/*.png, boards/*.png) against locked sources (sources/front.png, oblique.jpg, top.jpg). No code, build reports or builder notes used as proof.

## 1. Verdict

**VISUAL_REWORK_REQUIRED**: one P1 remains. The concrete panel in the west corner bay starts about 10% of wall height above the south-face concrete band, so the datum that wraps the identity corner in both perspective sources is broken and the west upper glazing band is half its source height. Everything else is P2.

Counts: P0 = 0, P1 = 1, P2 = 10

## 2. Findings table

| # | severity | view(s) and pixel regions | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | front_corner x 555-950, y 570-900 (corner pier at x~700); left_side bay x 915-1130, y 470-855; front x 230-745, y 455-830 | The bands do not line up at the corner. On the west corner bay the concrete runs from 25% to 64% of wall height (left_side y 565-715) and the upper glass is only 11% (y 517-560). On the south face the concrete runs from 35% to 68% (front y 588-710) under a 32% glass band. In front_corner the west concrete head sits about 32 px above the south concrete head at the corner pier. In the sources the two concrete heads meet level at the pier (front: within about 9 px after depth correction; oblique crop: about 300 vs 310 px). The west upper glass is about 0.7 of the south glass height there (front 90 vs 140 px; oblique 70 vs 150 px). Here it is 0.36. | The west-bay sill and transom heights were set on their own, not taken from the south-face datum. The v009 lift of the south upper glass row was not carried round the corner. | Drop the west-bay concrete head to the south-face concrete head (about 35% of crown height below the coping), so the west upper glass band becomes about 20% of wall height (about 0.7 of the south band). Keep the concrete bottoms aligned at the lower-glass head, at about 64-68%. |
| 2 | P2 | front (whole), left_side (whole); measured against sources/front.png | The lower volume still reads somewhat short, though much less than in v008. Rebuilding the camera from the locked front's two vanishing points (VP about (-596,606) and (1394,598), f about 988 px) gives the west face a length to crown-height ratio of about 2.16. The render left_side gives 940/385 = 2.44, so height is about 12% short. The south face reads 1.37 in the render (515/378) against 1.02 direct from the front source. That direct figure conflicts with the locked plan, whose south-to-west ratio is 0.55 against 0.47 in the front source. Corrected by the plan, the source south ratio is about 1.19, so height is about 15% short. The residual of about 12-15% sits inside the disagreement between the sources, so it is not P1. | The 14.0 m crown is still a little low against the locked front perspective. | Optional: raise the crown to about 15.6-16.0 m (+12-15%) and the corten block in proportion (about 19.3 m, keeping the 1.21-1.24 ratio that matches the sources now). Keep the plan unchanged. |
| 3 | P2 | phone-01 bottom row; front vs sources/front.png | The matched-role "front" is a straight south elevation. The locked front is a low two-point corner perspective. Board 1 pairs the locked top with render aerial (an SE view), not with render top, which only appears on board 4. | Camera and board role mapping. | Add or replace with a street-level SW corner camera that matches the locked front, and pair the locked top with render top on board 1. |
| 4 | P2 | top x 390-740, y 255-825; roof_plant | Ducts form a continuous ⊐ loop along the east edge of the lower roof. The source top shows a separate N-S duct at about 79-91% of the width (y 34-67%) that does not join the south run. | Simplified routing. | Break the east return so it reads as the source's single central riser run. |
| 5 | P2 | top x 858-965, y 250-535 | The two-fan and single-fan units on the corten roof sit about 10% of the block length north of the source (source 21-38% and 46-61% from the north edge; render 10-24% and 37-46%), and about 10-15% east. | The move north overshot. | Shift both units about 0.1 L south and slightly west. |
| 6 | P2 | top x 450-505, y 460-510 | The hourglass stack is about 8% of the length north of the source position (source y 48-59%, render 39-46%). | Placement. | Move the stack pad about 0.08 L south. |
| 7 | P2 | facade_close, front, left_side (concrete areas) | The board-formed concrete is a flat light grey with buff joint lines. The source concrete is darker and cooler in the front source. It still reads as the panel and is acceptable for clay, but contrast with the precast service panel is low (render values about 121 vs 139). | Palette choice. | Darken the concrete one step toward the source grey (about 0.85x). |
| 8 | P2 | glass_close, plant_window y 245-260 | The glass head meets the concrete panel almost flush. The reveal and soffit read only at the mullion pier (x 840-925). | Shallow glass setback. | Increase the glass setback under the concrete band so a soffit shadow line shows. |
| 9 | P2 | right_side (whole), rear x 695-1210 | The east and north faces are large blank planes with one door and one louvre each. They are coherent and in no source, but sparse. | Faces with no source. | Optional: add a second louvre or panel joints so the faces keep the visible grammar. |
| 10 | P2 | front, front_corner (brick) | The buff brick reads lighter and more orange than the source brick in shade. It is the same hue family. | Clay palette. | Optional slight desaturation. |
| 11 | P2 | front x 1015-1080, y 470-790 | The slot sits at about 58-72% of the corten south face width. In the source it is at about 70-78% after correcting for depth. | Placement. | Shift the slot about 0.08 W east. |

There are no floating or intersecting parts. The stack legs land on the concrete pad. The flues stand on their pad with cone caps. The ducts sit on dark sleepers. The corten single-fan unit and its pipe loop stand on legs that reach the roof. The trees are grounded.

## 3. Source conformance checklist

| Item | Status | View used |
|---|---|---|
| Silhouette (two volumes, corten taller, plan L-ratio) | conforms. Plan ratio is 1.78 vs 1.81. Corten to lower height is 1.21 vs about 1.24. The residual height deficit is P2 #2. | top, rear, front vs sources/top.jpg, sources/front.png |
| Storey count (two-storey lower frame) | conforms | left_side, front |
| Bay rhythm and glazing (west: service bay / full-height glazed bay / pier / concrete corner bay / corner pier) | conforms in plan widths. Source shares are 41.8/18.8/8.1/23.9/7.4%; render shares are 42.6/20.7/7.4/22.9/6.4%. The vertical bands deviate at the corner bay (P1 #1). | left_side vs sources/front.png |
| Concrete panel (upper corner bay, wrapping the corner) | deviates: the band does not align across the corner (P1 #1) | front_corner, left_side, front |
| Entrance (glazed bay, canopy, recessed doors) | conforms. The canopy fascia, recessed doors, jamb returns and step are visible. It sits in the full-height glazed bay, as in both perspective sources. | glass_close, corner_entry, left_side |
| Corten block and slot | conforms. It has vertical seams, a single-light slot with visible head and jamb reveal, and the west louvre above the lower parapet. The slot is slightly west (P2 #11). | corten_block, architecture_close, front |
| Roof plant and stack (two three-fan banks, ducts, three flues, hourglass stack, two corten units) | conforms. Placement and routing deviate slightly (P2 #4-6). | top, roof_plant, stack_contact, front_corner |
| Materials hierarchy (buff brick frame > glass > concrete > corten > membrane) | conforms. Concrete is slightly pale (P2 #7). | front_corner, facade_close |

## 4. Camera validity

No view has its target occluded, clipped or illegible. In roof_plant the near-right cooling bank is cut by the frame edge, which is acceptable for a detail view. The interior view is legible: a plant-room column, equipment and glazing grid. The only role issue is that the "front" camera does not match the locked front's corner perspective, and board 1 pairs the locked top with aerial (P2 #3).

## 5. Previous-version (v008) findings: resolved in pixels?

| v008 finding | v009 pixels | Status |
|---|---|---|
| P1 lower volume 30-40% too low (south face about 1.6) | The south face is now 1.37 and the west face 2.44, against source about 1.02-1.19 and 2.16. The remaining deficit is about 12-15%, measured from sources/front.png with a perspective rebuild and corrected by the plan from sources/top.jpg. | Largely resolved; residual downgraded to P2 #2 |
| Single tall row of upper panes on the south face | One row of 11 panes runs up to the coping (front y 468-588; architecture_close) | Resolved. It was not carried round to the west bay (P1 #1). |
| Flues cut to about 1.3 bank heights with cone caps | stack_contact: flues are about 1.1-1.3 times the bank box height, with conical caps | Resolved |
| West louvre on the corten above the lower parapet | architecture_close x 690-775, y 205-275; front_corner x 900-925, y 515-540 | Resolved |
| One wide single-light slot with a lower head | corten_block: a single light with a reveal; head at about 21% of block height | Resolved (position is P2 #11) |
| Two-fan unit plus single-fan unit moved north with a pipe loop | roof_plant x 65-610, y 230-325; top | Present. It overshoots north (P2 #5). |
| Vertical-only standing seams on the corten | right_side, corten_block | Resolved |
| Even brick piers of about 6-7% | left_side piers 6.4% and 7.4%; front left pier 8% | Resolved |
| Five clerestory lights | left_side x 305-580, y 490-525: 5 lights | Resolved |
| Lighter precast service panel | left_side service bay about 139 against concrete 121 | Resolved |
