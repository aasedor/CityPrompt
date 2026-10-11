# Independent RLASM v6.1 holistic review: rowhouse v006

## 1. Verdict

**VISUAL_REWORK_REQUIRED**: 0 P0, 2 P1, 9 P2. The envelope, storeys, bays, gables, chimneys, stoops and fence all match the sources. v005's gable-base pent, bay cap and end-gable apex holes are fixed. But the loose trim sliver at the apex of every cross gable is still there, and new grey eave and valley spikes stab down into the first-floor wall.

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | gable_close (~615-700, 265-490); roof_contact (~545-615, 620-770, cream W gable, right rake); architecture_close (~1290-1340, 270-460 green E gable, and ~130-185, 200-520 brick middle gable); rear (~295-305, 240-320 W rear gable and ~1105-1125, 225-300 E rear gable); rear_yards (all three rear gables) | A thin pale strip runs inside one rake of each of the six cross gables, front and rear. It starts at the apex under the finial block and splits away from the bargeboard, leaving a dark slot (black in roof_contact). It stops in mid-air about a third of the way down the rake. A small dark notch also shows at the apex where the two slate verge strips meet under the finial (gable_close ~698, 262). The sources show one bargeboard per rake running cleanly from the finial to the foot. **v005 P1 #3 is not resolved.** | A leftover verge or trim strip, or the infill edge's bevel, still generated per rake. It is offset or rotated against the bargeboard and clipped to a shorter length. | Delete the extra strip, or snap it coplanar under the bargeboard at full rake length. Close the apex so the two verge strips and the bargeboards meet under the finial with no gap. Re-check all 6 gables in gable_close, roof_contact, architecture_close and rear. |
| 2 | P1 | front (~628-652, 495-532 and ~793-815, 495-532); facade_close (~228-268, 0-95 and ~712-738, 35-100); rear (~435-450 / ~600-612 / ~830-842 / ~995-1008, 515-535); rear_yards (~212-240, 240-292; ~522-545, 250-298; ~898-918, 258-292; ~1122-1142, 258-292) | Slender grey diagonal slate pieces hang below the main eave at the foot of each cross-gable roof. They pierce the brick face and cross the first-floor window heads and lintels; in facade_close they read as struts poking out of the wall. The sources show a clean eave line with nothing below it. | The cross-gable roof planes, or their valley boards, are extruded past the main roof's eave and down through the wall plane. | Clip the cross-gable roof and valley geometry to the main eave line or wall face. End the valleys at the gutter. |
| 3 | P2 | front_corner (~640-760, 620-670), aerial (~430-510, 500-530 and ~710-800, 690-720) | A flat light-grey deck with green fascia edges sits on top of each end bay, in front of the set-back gable infill. In the oblique source, the gable infill sits directly over the bay face. (The v005 hipped pent itself is gone.) | The gable plane is set back from the bay's front face. | Bring the gable infill and fascia forward to the bay face, or shrink the deck to a thin flashing strip. |
| 4 | P2 | architecture_close (~0-160, 620-745), front (~695-735, 385-455) | The middle gable's blind arch is a flat cream half-disc set proud over a narrower rectangular recess. The source shows an arch-headed recess with a brick arch. | A separate hood primitive with no arched recess under it. | Cut an arch-headed recess the same width as the hood. |
| 5 | P2 | right_side (~455-985, 285-500); front (~1110-1180, 250-470) | The east end gable has a cream verge and one window per floor. The source front shows a dark-green bargeboard and two narrow windows per floor on the flank. | Simplified flank. | Make the verge green and add the second window per floor, with bands kept. |
| 6 | P2 | front_corner, aerial, top (front gardens ~385-1050, 770-900); rear_side, rear_yards, top (rear yards ~380-1060, 95-310) | Front gardens are bare brown soil with a hedge strip and one small shrub. Rear yards are bare grey slabs. The sources show dense hedged and shrub-filled front gardens and green rear lawns with paving. | Minimal landscape. | Fill the front gardens with massed shrub volumes. Give the rear yards lawn and paving colour. |
| 7 | P2 | bay_window (~1085-1150, 862-884); front_corner (~627-640, 848-858) | A small black cavity at the foot of the east and west bays, where the plinth block meets the quoin stack. | The bottom quoin block is offset or missing. | Extend the plinth or quoin to close the gap. |
| 8 | P2 | party_wall (~300-1430, 250-370); left_side (~455-985, 505-520) | Brick coursing on the blank west party wall stops at eaves height. The gable triangle above is smooth, leaving a visible seam. | Separate gable primitive without the coursing material. | Apply the same coursed-brick material to the gable triangle. |
| 9 | P2 | front (~490-960, 680-790), entrance_steps | On the ground floor between the bays the render alternates door, window, door, window, door. Every source view shows the middle unit's two windows as a pair, with only two doors visible. The brief requires three doors, so the builder recorded this as a conflict. | Brief versus source conflict. | Acceptable as recorded. Optionally pair the two middle windows and move the middle door beside them. |
| 10 | P2 | architecture_close (~730-835, 295-345) | There is a step and ledge where a cross-gable roof plane meets the main ridge cap. | Ridge cap and cross-gable ridge at slightly different heights. | Align the ridges or add a matching cap. |
| 11 | P2 | interior (0-1330, 730-1080) | A large foreground slab hides the lower half of the frame. The bay windows and shutters are still legible. | Camera placed behind furniture. | Raise the camera or move it forward. |

## 3. Source conformance checklist

| item | status | view used |
|---|---|---|
| Silhouette | conforms. Three steep front cross gables, a long main ridge, a tall party-wall gable to the W and a brick end gable to the E. | front vs source front; front_corner and aerial vs oblique |
| Storey count | conforms. Two storeys plus an attic in the gables. | front, rear, right_side |
| Unit rhythm and doors | deviates (P2 #9). Three doors on stoops with railings, the green door beside the E bay and red doors elsewhere, as the sources show. The middle-unit window pairing differs. | front, entrance_steps, facade_close vs source front and oblique |
| Bays and gables | partly deviates. Two-storey canted bays now carry one sloped slate hip cap between the floors (good). Gable infill comes down to a green fascia (good). The rake sliver (P1 #1) and the bay-top deck (P2 #3) remain. | front, bay_window, gable_close, front_corner |
| Dormer and roof | deviates (P1 #2). The middle brick gable has a green bargeboard and a blind arch (P2 #4). The slate main roof and rear cross gables match the top source, but valley and eave spikes pierce the wall. | architecture_close, top vs source top |
| Chimneys | conforms. Two stacks with cream caps and pots on the ridge at the party-wall and E-end positions. | top, roof_contact, left_side, right_side |
| Fence and gardens | fence conforms; gardens deviate (P2 #6). Iron railings and gates on a low wall with hedges inside. | front, entrance_steps, top |
| Rear | conforms for coherence. Three rear cross gables, banded brick, rear doors, walled yards. The rake sliver also shows here (P1 #1). | rear, rear_side, rear_yards |
| Materials hierarchy | conforms. Red-brown brick with cream bands, sills, lintels and quoins, green and cream gable infill, slate-grey roof, dark-green doors. | all whole-envelope views |

## 4. Camera validity

Every view is valid. The asset is not clipped and the target is not occluded in any whole-envelope view. interior has a large foreground slab across its lower half (P2 #11), but it is still legible. party_wall is intentionally a blank wall, judged only for coherence.

## Prior-version (v005) findings

| v005 finding | status in v006 pixels | evidence |
|---|---|---|
| P1: hipped slate pent inside the base of each end gable | resolved | The front crops show the cream and green infill coming straight down to a green fascia on the first-floor brick, with no slate pent. A flat bay-top deck remains (P2 #3). |
| P1: bay cap was three flat grey boxes open at the cant corners | resolved | bay_window (250-1225, 80-250) and front (255-490 and 950-1185, 645-675) show one continuous sloped slate hip cap with hipped corners projecting round the bay. |
| P1: thin trim strip leaves each rake at the apex, splits from the bargeboard and ends in mid-air | not resolved | Still present on all six cross gables. See P1 #1. |
| P1: black holes at the apexes of the E end gable and W party gable | resolved | The right_side apex (~700-720, 285) and left_side party-gable apex (~720, 290) are closed. A small apex notch on the cross gables is folded into P1 #1. |
