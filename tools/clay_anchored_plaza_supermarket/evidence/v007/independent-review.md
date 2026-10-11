# Independent RLASM v6.1 holistic review: plaza v007

## 1. Verdict

**VISUAL_REWORK_REQUIRED.** v007 fixes all four v006 P1s in the pixels. One P1 remains: the cafe wing's west elevation has no brick pilasters, although the oblique source shows them clearly.

**Counts: P0 = 0, P1 = 1, P2 = 8**

What I reviewed: the three locked sources, all 18 renders at full resolution and the four phone boards. I also made zoomed crops of the cafe, the end-cap, the west elevation and the east site edge, and compared them against matching source crops. I did not read any build code, build reports or notes.

## 2. Findings

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | **P1** | left_side.png (building x 383-1010, y 505-600); front_corner.png (west face x 255-380, y 530-600) | The whole west elevation of the west wing (cafe and the box north of it) is plain beige EIFS with a continuous brick base. It has three or four bare punched windows and a brick pilaster only at the SE corner (left_side about x 1010-1020). The oblique source (crop x 30-340, y 340-560) shows a regular rhythm of about five full-height brick pilasters along this face. The windows sit between the pilasters in brick-lined bays over the brick base, and a small dark awning covers the southern side window. Brick pilasters are a named identity element, and this face is visible in a locked source. | The pilaster module was applied to court-facing elevations only. The west face reuses the plain rear/service wall grammar. | Add full-height brick pilasters to the west face at the shop-bay module (about 5 or 6 pilasters, matching the width and projection of the inline pilasters), with brick reveals at the window bays. Add a small dark awning over the southernmost west window. |
| 2 | P2 | front.png (x 180-300, y 485-515); left_side.png (x 410-580 vs 580-715 at the roofline) | The west wing is two boxes of different heights. The north box stands about one cornice depth above the cafe box, and a cornice stub returns at the step. The oblique and top sources show one continuous low roof over the whole west wing. | The west wing was modelled as two volumes. | Unify the west wing at the cafe parapet height, with one roof and one cornice. |
| 3 | P2 | front.png (cafe x 140-300, y 515-605); anchor_entrance.png (x 0-345) | The cafe front is a separate single door at the west end plus a 5-pane ribbon window. The front source shows one storefront group with a central double door between window bays. | The bay layout was simplified. | Re-lay the cafe storefront as a symmetric group of window bays with a central double door under the dark lintel. |
| 4 | P2 | aerial.png (end-cap south face, about x 915-1015, y 590-615) | The end-cap's south face carries one small window (about 12% of the face width) set in beige. The oblique source shows a long dark window group (about 35-40% of the face) set in a brick ground storey west of the beige panel. | The drive-through window was modelled as a single small opening. | Widen it to a 4-5 mullion window group in a brick surround that runs up to the beige band. |
| 5 | P2 | front.png (x 1325-1385, y 590-625); endcap_corner.png (x 830-1035, y 500-810) | On the end-cap's west (court) face, the storefront run stops one bay short of the SW corner pier. That bay is blank beige with a small window and two bollards, outside the canopy. The front and oblique sources show the pharmacy storefront running up to the brick corner pier. | The pickup window was placed on the court face. | Carry the storefront and canopy to the corner pier. The pickup window belongs on the south face only (see #4). |
| 6 | P2 | front.png (x 1200-1260, y 495-530); inline_shops.png (x 1390-1430, y 430-480) | Canopy tie-rods from the inline and end-cap canopies cross in an X at the inside corner, so the rods pass through each other. | The rod arrays from the two wings overlap at the corner bay. | Drop the last rod on one wing, or mitre the corner bay with a single diagonal rod. |
| 7 | P2 | top.png (x 240-275, y 705-770); aerial.png (x 270-300, y 505-560) | The pylon sign stands on the asphalt at the SW corner, in line with the west stall column. The sources place it in the grass verge between the court and the road. | Placement offset. | Move the pylon south into the verge strip, on its own small footing. |
| 8 | P2 | top.png; aerial.png; parking_court.png | Landscape is thin. Only the south verge is lawn-coloured. There are no curbed grass islands at the parking-row ends, and only 3 trees stand along the east, where the source has a dense row of about 10 poplars. Everything around the pad is neutral grey ground, where the source shows prairie grass on all sides. | The site dressing is minimal. | Add the row-end islands, a lawn band around the pad perimeter, and an east tree row of 8-10 columnar trees. |
| 9 | P2 | top.png (x 430-505, y 540-590); roof_units.png (x 375-930, y 595-760) | The anchor tower's roof is a dark-brown slab. The source tower has a beige/grey roof with a lighter coping cap. | The cornice material was assigned to the whole roof plane. | Use the roof-membrane colour for the roof and keep the dark band as the coping only. |

The P2 count is 8 (findings 2-9).

## 3. Source conformance checklist

| item | status | view used |
|---|---|---|
| Silhouette (low single-storey run, taller anchor, tallest tower) | conforms | front.png vs source front.png |
| L-plan and wings (anchor + cafe west, inline north, end-cap east wrapping the court) | conforms. West wing split into two heights (P2 #2) | top.png vs top.jpg; aerial.png |
| End-cap proportion (second-largest volume, about 1.5-1.8x inline depth) | conforms: end-cap is about 155 px deep vs about 95 px inline in top.png (about 1.6x) | top.png vs top.jpg |
| Anchor tower (projecting, taller, brick corner pilasters, green base frame) | conforms. Roof colour P2 #9 | front.png, anchor_entrance.png, roof_units.png |
| Anchor sign band (green band on light field) | conforms (clay, no text) | facade_close.png, architecture_close.png |
| Shop-front rhythm and canopy (brick pilasters between glazed bays, continuous canopy turning the corner) | conforms. Tie-rod clash P2 #6; end-cap blank bay P2 #5 | inline_shops.png, endcap_corner.png, top.png |
| End-cap and drive-through | conforms in massing and route. South-face window undersized (P2 #4) | aerial.png, top.png, right_side.png |
| Parking court (striped stalls, cars, accessible hatch, perimeter drive, west parking row) | conforms | top.png, parking_court.png |
| Pylon sign | conforms in form; placement P2 #7 | front_corner.png, aerial.png, top.png |
| Roof units (flat roofs, RTUs scattered on every volume) | conforms | roof_units.png, top.png |
| Materials hierarchy: court faces (brick base and pilasters, beige EIFS, dark cornice, light sign band) | conforms | inline_shops.png, facade_close.png, front.png |
| Materials hierarchy: cafe front (brick ground storey, end piers, dark lintel, beige sign band, no canopy) | conforms | front.png crop vs source front/oblique crops |
| Materials hierarchy: west elevation | **deviates (P1 #1)** | left_side.png vs oblique.jpg |
| Lawn verges / landscape | partly: south verge only (P2 #8) | top.png vs top.jpg |
| Rear / east faces (not shown by any source) | coherent with the visible grammar (beige, brick base, cornice, service doors, compactor pad) | rear.png, rear_side.png, rear_service.png, right_side.png |

## 4. Camera validity

No view is invalid. Every target is unoccluded and unclipped, and its subject is legible:

- left_side, right_side, rear and rear_side frame the building small (about 35-60% of the frame width) on a large empty ground plane. This is legible but loose, so tighter framing is recommended (polish only).
- The close-up views are all filled by their subjects: facade_close, architecture_close, glass_close, anchor_entrance, inline_shops, endcap_corner, parking_court, roof_units, interior and rear_service.
- Openings show depth. Storefront glazing is recessed behind the brick base and lintel (glass_close.png). The anchor doors are set back in the green wall with visible returns (anchor_entrance.png x 455-470). The interior reads through the glazing.

## 5. v006 findings: status in v007 pixels

| v006 finding | status | evidence |
|---|---|---|
| P1: east end-cap was a thin bar equal to the inline depth; source shows it at 1.5-1.8x and the second-largest volume | **resolved** | top.png: end-cap x 1008-1168 (about 160 px) vs inline depth y 323-420 (about 97 px), about 1.6x. Clearly the second-largest roof after the anchor, as in top.jpg. |
| P1: site pad stopped 2-3 m short of the north, east and west walls; no wrap-around drive, no drive-through route, no west perimeter parking row | **resolved** | top.png: pad extends about 87 px north of the building and about 87 px east and west of it. Lane lines run down the east side of the end-cap (x about 1175/1200, y 265-685) and turn west along its south face (y about 655/685). A west row of about 16 stalls runs along x 240-275. |
| P1: cafe mostly beige with a canopy and no brick pier at its east end | **resolved** | front.png cafe crop: brick ground storey across the full width, wide brick piers at both ends, dark lintel, light/beige sign band above, no canopy. Matches the front and oblique source crops. (The bay layout and the west face are separate findings, P2 #3 and P1 #1.) |
| P1: end-cap south face beige with brick only as a base; source has a brick corner pier at the west and a full-height brick panel at the SE | **resolved** | aerial.png end-cap crop: full-height brick pier at the SW corner, and a full-height brick panel at the SE corner running from the base to the sign band. (Window size is a new P2, #4.) |
| v006 P2s (6, not itemised in the brief) | not verifiable individually | Remaining polish items are listed fresh above as P2 #2-#9. |
