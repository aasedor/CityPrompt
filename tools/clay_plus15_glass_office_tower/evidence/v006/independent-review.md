# Independent RLASM v6.1 holistic review: clay-plus15-glass-office-tower v006

Reviewer: independent. I looked only at the three locked sources, the 18 renders and the 4 phone boards. I did not read any build code, reports, README or VERSIONS files. Every measurement below comes from pixels I sampled myself, at 1440x1080 for renders, 1195x896 for the oblique and top sources, and 1024x768 for the front source.

## 1. Verdict

**PASS_ZERO_P0_P1**: the tower, its 16-storey spandrel and mullion grammar, the corner columns and parapet, the recessed colonnade lobby, the Plus 15 bridge on two piers and the green roof around the L-shaped glazed penthouse all read correctly. Both v005 P1s are fixed in the pixels. Only polish items (P2) remain.

**Counts: P0 = 0, P1 = 0, P2 = 11**

## 2. Findings table

No P0 or P1 findings. The P2 items are listed below.

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P2 | top.png (bridge x 683-719, tower x 578-862); front.png (bridge x ~673-717); front_corner.png | The bridge centreline now sits at 0.43 of the south face from the west corner. Source top.jpg puts it at 0.48 (bridge x 580-627 on a 364-860 roof). The render bridge spans 0.37-0.50, so it ends exactly at centre. The source bridge spans 0.44-0.53 and straddles the centre line. | The bridge was moved about 0.05 of the face width too little. | Move the bridge east by about 0.05 of the face width (about 1.5-2 m), so its east edge sits just past the face centre. |
| 2 | P2 | top.png (bridge 36 px wide; clear span y 678-905); left_side.png (x 898-1160); plus15_bridge.png | The bridge is about 34% wider than the source relative to the tower (0.127 vs 0.095 of the face). Its clear span over the street is about 0.80 of the face width. Source top.jpg gives about 0.37 uncorrected, or about 0.5-0.6 after correcting for roof-height perspective, so the street and bridge read noticeably long. | The street and receiving stub are placed too far south, and the bridge section is oversized. | Narrow the bridge to about 0.10 of the face width. Pull the receiving stub north so the span is about 0.55 of the face width. |
| 3 | P2 | top.png (south bed y 628-655, NE bed x 727-813 / y 424-450); roof_terrace.png; aerial.png | The green beds are thin strips. The south bed is 0.10 of the roof depth against 0.16 in the source (y 540-612 of 185-640). The NE bed is 0.09 deep and 0.30 wide against 0.17 and 0.36 in the source. Total green cover is about 19% of the roof against about 27% in the source. A wide white margin is left between the south bed and the parapet. | The bed depths were not taken from the source plan. | Deepen the south bed to about 0.15 of the roof depth, out to about 0.05 from the parapet. Make the NE bed about 0.16 deep and 0.35 wide. |
| 4 | P2 | top.png (west path gap y 474-488) | The white walkway that crosses the west bed is at 0.30 of the roof depth. In the source it is at 0.52 (y 398-445) and about 0.10 wide, against 0.05 in the render. | The path position was not changed from v005. | Move the gap in the west bed to mid-depth and widen it to about 0.10. |
| 5 | P2 | top.png; roof_terrace.png; aerial.png | There is no roof hatch. The source shows a pale square hatch in the south bed (top.jpg x 555-590, y 578-612; oblique.jpg left bed) and a pale landing at the west path. | The hatch was omitted. | Add a pale low hatch box of about 1.2 m square in the south bed at about x 0.40 of the face. |
| 6 | P2 | roof_terrace.png; crown_penthouse.png | The bed planting is one flat green with a regular row of identical shrub balls. The source shows mottled sedum with irregular clumps. | A single bed material and a regular scatter pattern. | Use two or three green tones in patches and cluster the shrubs irregularly. |
| 7 | P2 | plus15_bridge.png (x 540-655, y 240-248); rear_service.png (x ~1415-1440, y 45-55) | The open corner arcade now coherently shows background through the corner bay (sampled RGB 151,156,159, the same as the sky). A thin black wedge still shows along the soffit or spandrel edge above that bay. | A small gap or back-face between the arcade soffit and the first spandrel fascia at the corner. | Close the soffit to the fascia at the corner bays, or give the soffit edge a pale return. |
| 8 | P2 | interior.png (window band y 330-555) | From inside, the window wall is one uninterrupted dark band. Only small white ticks show at the sill. None of the closely spaced mullions seen outside appear, so the interior contradicts the exterior grammar. | Interior-side mullions or glass divisions are not modelled or are hidden. | Show the mullions on the interior face at the exterior bay spacing (22 bays per face). |
| 9 | P2 | front.png (stub block x 627-755, y 855-972) | The "front" camera is a head-on south elevation. The bridge is seen end-on as a sliver, and the receiving stub block covers the lower centre third of the lobby colonnade. No render matches the source front role, which is a street-level 3/4 view from the south-east with the bridge in profile. The tower itself is fully legible, so the camera is not invalid. | Front camera choice. | Add or replace with a street-level SE 3/4 camera that matches front.png. Keep the head-on elevation, but crop or position it so the stub does not cover the entry. |
| 10 | P2 | crown_penthouse.png; roof_terrace.png; left_side.png | The penthouse is uniform clear glass with close white fins on every face. The source oblique shows pale translucent louvre panels on one face and clear glass on the other, plus a door on the south face. Its height (about 2.2-2.4 storeys) and its two panel tiers do match. | The material is not split by face. | Give the louvred face a paler, more opaque panel colour and add a door panel on the south face. |
| 11 | P2 | plus15_bridge.png (bays about 300 px wide by 240 px tall); left_side.png | The bridge glazing has wide, sparse bays, about 1.25:1. The source front bridge has close mullions with roughly square or upright bays (about 40 px pitch by 40 px glass height). | The bridge mullion spacing is too coarse. | Halve the bridge mullion spacing. |

## 3. Source conformance checklist

| Item | Status | View used | Note |
|---|---|---|---|
| Silhouette | conforms | front.png, left_side.png, front_corner.png vs oblique.jpg | Square slab tower with a set-back penthouse and a bridge on the south. |
| Floor count | conforms | left_side.png (16 dark vision bands, y 207-774) | 16 floors over a tall lobby, as the brief records. |
| Spandrel and mullion rhythm | conforms | facade_close.png, glass_close.png, curtain_grid.png, left_side.png (22 bays per face) | The pale spandrel is about 0.26 of the floor pitch. Mullions run continuously and the dark vision band is clearly dominant. |
| Corner columns and parapet | conforms | front.png, crown_penthouse.png (x 960-1030, y 865-885), architecture_close.png | Pale full-height corner piers, with a parapet coping band and a capped corner. |
| Lobby colonnade and entry | conforms | rear.png, right_side.png, architecture_close.png, rear_service.png, lobby_entry.png | The glazed lobby box is recessed behind a perimeter colonnade with a transom and door sets, and the corner arcades are open. The black soffit-edge sliver is a P2 (#7). |
| Bridge | conforms (P2 residuals) | top.png, plus15_bridge.png, left_side.png, right_side.png, front_corner.png | Enclosed glazed bridge at the second level, leaving the west half of the south face, carried on two grounded piers. It is about 0.05 west of the source position and wide and long (#1, #2, #11). |
| Green roof and penthouse | conforms (P2 residuals) | top.png, aerial.png, roof_terrace.png, crown_penthouse.png, rear_side.png | The penthouse has an L-shaped solid roof, an open mechanical court with four RTUs, and glazed or finned walls. The beds wrap the NW, W and S sides, plus a NE bed, but are shallow, with no hatch and an off-position path (#3-#6, #10). |
| Materials hierarchy | conforms | all | Pale piers, spandrels and coping over dark vision glass, lighter lobby glass, green beds and grey paving. The clay palette is consistent. |

## 4. Camera validity

- All 18 renders are valid: the target is legible, nothing is clipped, and no camera sits inside geometry.
- front.png: the receiving stub block partly covers the lower centre of the lobby colonnade, and the bridge is end-on. The view is still valid, and the bridge is legible in left_side, right_side, plus15_bridge, front_corner and aerial (P2 #9).
- interior.png: valid, but see #8.
- top.png: valid nadir view. Heavy soft shadows cross the ground but do not cover the roof.

## 5. Prior-version (v005) findings, judged from the pixels

| v005 finding | Severity then | Status in v006 | Evidence |
|---|---|---|---|
| Bridge leaves the south face at about 0.22 of the face width from the west corner, against about 0.48 in the source | P1 | **partly resolved (residual is P2)** | top.png bridge centre is at 0.43 (x 683-719 on 578-862). It was 0.22 and the source is 0.48. The remaining offset is about 0.05 of the face width (#1). |
| Colonnade corner bay not closed: loose full-height glass leaf past the last column in rear_service | P1 | **resolved** | rear_service.png: the glazing ends behind the last column (x 1200-1305). No glass leaf stands past it, and the corner bay is an open arcade under the soffit. |
| Colonnade corner bay not closed: black soffit void beside the corner column in plus15_bridge | P1 | **resolved (minor residue P2)** | plus15_bridge.png x 535-655, y 245-385 now shows background through a coherent open corner arcade, consistent with the inset lobby box seen in rear.png and right_side.png. Only a thin black edge line at y 240-248 remains (#7). |
| South and NE green-roof beds slightly shallow | P2 | not resolved | top.png: south bed 0.10 against 0.16; NE bed 0.09 against 0.17 (#3). |
| West path off mid-depth | P2 | not resolved | top.png path at 0.30 against 0.52 (#4). |
| Missing roof hatch | P2 | not resolved | No hatch in top.png, roof_terrace.png or aerial.png (#5). |
| Flat bed colour | P2 | not resolved | roof_terrace.png and crown_penthouse.png show uniform green (#6). |
| "and others" (unnamed v005 P2s) | P2 | not assessable | The brief does not itemise them. Every P2 still visible is listed above. |
