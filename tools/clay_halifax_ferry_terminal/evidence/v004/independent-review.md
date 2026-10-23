# Independent RLASM v6.1 holistic review: Halifax ferry terminal clay, v004

Reviewer: independent source-locked reviewer. I did not build this candidate.

Inputs judged:
- the locked sources `sources/front.png`, `sources/oblique.jpg` and `sources/top.jpg`;
- all 18 renders in `renders/` (1440x1080);
- the 4 phone boards in `boards/`;
- for comparison, the v003 and v002 renders in `../v003/renders/` and `../v002/renders/`.

I opened every source, render and board with the image reader and judged from the pixels. Zoomed evidence crops are in `review/crops_qifgxm/`. Pixel coordinates refer to the original 1440x1080 render unless a crop is named. Luminance is L = 0.2126 R + 0.7152 G + 0.0722 B, on a 0-255 scale.

## 1. Verdict

Verdict: FAIL

Counts: P0=0 P1=1 P2=13

**The v003 P1 (N4) is fixed.** Every upper-lounge seating row and every south lounge bench now stands on a dark pedestal. Each seat meets its contact shadow, with no lit floor between them. The v002 bench-joint fix and every v001 fix still hold. Outside the lounge seating, the v004 renders are pixel-identical to v003. A diff at a threshold of 8 levels shows only these changes:
- glass_close, front_corner, roof_boxes, left_side and aerial change in the lounge regions only;
- front changes by 2 px and roof_mechanical by a 46x22 px corner;
- the other 11 renders are identical to v003.

**One P1 remains (N6).** Neither earlier review raised it. It has been in the renders since v002, unchanged. Where the stair reaches the upper floor, a hard-edged, near-black patch shows on the lounge floor and on the hall ceiling under it.
- It is darker than the near-black pedestals that are lit beside it, so it receives no direct light. It is not a cast shadow.
- It sits in the same place in four views: roof_boxes, left_side, lawn_bench and architecture_close.

The upper floor has no stairwell opening. The stair runs into a solid slab, and its post-less handrails pass through the ceiling and come up through the lounge floor as free-ended stubs. The brief rules that black patches caused by geometry, and floating or intersecting parts, are failures. In the brief's terms the verdict is VISUAL_REWORK_REQUIRED, and the fix is one finite change.

## 2. Findings table

| id | severity | view(s) | finding (what the pixels show) | evidence | likely cause | suggested fix |
|---|---|---|---|---|---|---|
| N6 | P1 | roof_boxes, left_side, lawn_bench, architecture_close, interior | **Black patch and intersecting stair at the head of the lounge stair.**<br><br>(a) On the lounge floor, at the south end of the west lounge row behind fin 1, there is a hard-edged near-black triangle (roof_boxes) or band (left_side). It extends beyond the end of the bench and the pedestal.<br><br>(b) Directly below it, a thin near-black wedge sits on the hall ceiling at the head of the stair, seen through the west glazing (lawn_bench, architecture_close).<br><br>(c) No stairwell opening is visible in either the ceiling or the lounge floor. In interior, both handrails run into the solid ceiling. In left_side, a handrail stub rises out of the lounge floor and ends in mid-air about 1 m up. The rails have no posts or balusters anywhere along the flight (interior, front, lawn_bench). | **roof_boxes (975-985, 835-848):** L 22.1-23.3, RGB 18/23/25. The lit near-black pedestal in the same view (x 930, y 808-823) reads L 28-29. The pedestal's own soft shadow then grades L 35→79 over 25 px (y 824-849). The triangle's lower edge drops L 25→68 within about 4 px (x 965, y 850-856). Crops `rb_quad_v004.png`, `rb_quad_v003.png`, `rb_sw_lounge.png`.<br><br>**left_side, column x=960:** floor L 65, then L 23-30 (y 519-527) with 1 px edges, then floor L 60-78. Pedestal at x 935: L 28-30. Crops `ls_landing_v004.png`, `ls_landing_v003.png`, `ls_rail_stub.png`.<br><br>**lawn_bench, column x=970:** ceiling L 73-75, then L 22-29 (y 335-343), then L 74-80, with 1-2 px edges. architecture_close, column x=1010: L 19-26 (y 480-483) inside L 70-82. Crops `lb_stair_top.png`, `lb_stairhead_ctx.png`, `ac_stair.png`.<br><br>**interior:** the rails disappear into the ceiling plane at about (1395, 410) and (1413, 400). Crops `int_stair.png`, `int_stair_top.png`.<br><br>All four patch boxes are identical in v002, v003 and v004 (min L 19.2-23.2), so this is not caused by the v004 pedestals. In v003, before the pedestals, the floor patch was already a crisp dark quad at the end of the floating bench. | The upper floor slab is a single unbroken plate (z 4.3-4.6), with no cut for the stair.<br><br>A separate stair-head landing block (about 1.8 x 1.4 m) sits inside the slab. Its top and bottom faces are exactly coplanar with the slab's top and soffit, and the top tread is coplanar with the floor. Coincident faces block their own light and render black: on the floor in roof_boxes and left_side, and on the soffit in lawn_bench and architecture_close.<br><br>The two handrail beams are not trimmed to the stair. They run from 1 m above the hall floor at the foot to 1 m above the lounge floor at the head, so they pierce the slab. | 1. Cut a stairwell opening in the upper slab over the top of the flight (about x -7.2..-5.2, y -12.6..-10.7).<br>2. Delete the redundant landing block, or let it stop 1 cm short of both slab faces.<br>3. End the top tread at the slab edge, so that no face is coplanar with the floor.<br>4. End both handrails on newels at the foot and at the slab edge, and add balusters or posts along the flight.<br>5. Add a guard rail around the opening on the lounge side.<br><br>Then re-render roof_boxes, left_side, lawn_bench, architecture_close and interior. Confirm that the floor, the soffit and the stair head read L > 40 wherever they are lit, and that no rail ends inside the slab or in mid-air. |
| N7 | P2 | facade_close | New observation, not a regression. A 1 px dark line separates the ticket-counter top panel from the counter body. It reads as an overhang shadow or a hairline gap, and it is invisible at phone scale. | facade_close, row about y 886, x 560-920. Crop `fcl_counter.png`. | The top panel sits about 4 cm above the counter body. | Seat the panel on the counter top. |
| F8 | P2 | front | Carried, unchanged. The near west bay dominates the frame, so the glass box does not read as the source front's central tall volume. | Board phone-01. | The camera is fitted to the box and the brick block. | Optional: use a slightly longer lens. |
| F9 | P2 | glass_close, entrance_canopy, front_corner | Carried, unchanged. The canopy is a flat-topped box. The source has a deeper canopy with a sloped standing-seam top. | glass_close y≈840-950. | Simplified primitive. | Deepen the canopy and give its top a shallow fall. |
| F10 | P2 | front_corner | Carried, unchanged. The south return of the wrapping canopy is a shallow ledge. | The SW canopy corner in front_corner. | — | Match the depth of the west run. |
| F11 | P2 | facade_close, entrance_canopy, glass_close | Carried, unchanged. The letter glyphs are stair-stepped voxel shapes. | facade_close y≈480-600. | — | Use extruded outline glyphs. |
| F12 | P2 | top, aerial, rear_side | Carried, unchanged. The heritage roof runs closed over the rear lightwell that the source top shows. | top render compared with the source top (x≈890-930, y≈360-480). | — | Cut the lightwell. |
| F13 | P2 | aerial, rear_north, rear_side | Carried, unchanged. The east context neighbour is a windowless prism in the heritage brick hue. | aerial x≈20-330, y≈215-540. | — | Add punched windows and use a different brick value. |
| F14 | P2 | roof_mechanical, front_corner | Carried, unchanged. The harbour is flat water only, with no piers or ferry. | roof_mechanical y≈240-420. | — | Add pier slabs and a ferry hull. |
| F15 | P2 | aerial | Carried, unchanged. Large featureless ground beyond the scene extent. | aerial y≈130-440. | — | Extend the context, or tighten the frame. |
| F16 | P2 | whole-envelope views, top | Carried, unchanged. The concrete is near-white against the source's blue-grey, and the top view is dim. | front, front_corner, top. | — | Darken the concrete one step, and lift the top-view exposure. |
| F17 | P2 | entrance_canopy, right_side, rear, roof_boxes | Carried, unchanged:<br>- the storefront room east of the doors is empty and white;<br>- some east-wall and north-wall rooms are nearly unlit;<br>- the roof boxes keep their dark louvre strip. | entrance_canopy x≈985-1195; rear window 5. | — | Furnish and light those rooms, and lighten the strip. |
| N2 | P2 | right_side, rear_side, rear_north | Carried, unchanged. The rear and wing panes of the brick block are uniform slate grey, with little interior depth. | rear_side x≈320-560, y≈690-960. | — | Raise or vary the room-plate value. |
| N3 | P2 | facade_close | Carried, unchanged. A 1 px dark contact crease where the door-head transom meets the centre post. It is an inside-corner shadow, not an open slot. | Row y=837, x 1120-1144: 48 … 23 19 17 17 21 31 49 60 … 63. | — | Optional: bevel the transom. |

Note: the v003 P2 N5 (a floating stair handrail with no posts) is now part of N6. The pixels show that the rails also pass through the ceiling and the lounge floor, at the same place as the black patch.

### Dark areas: which are geometric defects and which are genuine

I scanned all 18 renders for pixels with L below 30 whose 15x15 neighbourhood mean is above 75, in 24 px cells. Then I checked by hand every patch that sits inside glazing, where the glass lowers the neighbourhood mean below that threshold. Apart from the lounge seating, every hit is in a pixel-identical region of v003.

**Geometric defects.**
- The N6 stair-head patch, at roof_boxes (950-987, 820-857), left_side (930-977, 517-529), lawn_bench (944-1000, 334-343) and architecture_close (985-1065, 479-484).
- It fails three tests that every genuine shadow in these renders passes. Its edges are hard, within 1-4 px. It is darker than a lit near-black object beside it. It stands apart from the soft, graded shadows of the furniture next to it.

**Dark by design.**
- The new lounge pedestals. They read L 28-43 (glass_close, column x=300: L 32-36; column x=420: L 41-43), with a blue-grey hue that matches the concourse bench bases. The seat sits on the pedestal, and the pedestal sits on its own soft shadow:
  - glass_close x=300: the seat underside ends at y 739, the pedestal runs y 740-770, and the floor shadow grades L 39→91 over y 771-787;
  - glass_close x=420: the seat at y 727, the pedestal y 728-757, then L 54→103.
- Door handles: front (792-864, 768-840), glass_close (840, 936-1008) and (1104, 912-936), lawn_bench (744, 552), architecture_close (816, 696) and rear_north (1368, 936).
- The slim aluminium mullions in shade (front 504, 480-504), and the handrail rods themselves (interior 1150-1270, 480-530).
- The cast-iron shopfronts on the brick block: brick_neighbour (1032-1150, 912-984), with a green-black cast (RGB about 15-21 / 18-27 / 16-23), following the shopfront piers and muntins.

**Genuine contact and overhang shadows.** These are soft, and they keep the host hue:
- the window-hood and arch-head undersides in brick_neighbour (144, 576, 936 and 1248, at y 240-312), warm brick RGB about 19-37 / 6-18 / 1-10;
- the eave and chimney shadows in right_side (1008, 192), rear_north (648, 264) and rear_side (1104, 360-408);
- the bench bases and their contact shadows in aerial (1008-1047, 600-648), left_side (1128-1200, 696), architecture_close (576, 792) and lawn_bench (456, 672);
- the head of the loading door in rear (912-936, 624);
- tree shadows on the lawn in top (360-384, 888-912).

**Not slots.**
- The interior door head (0-200, 336-410) is a soft transom shadow (`int_doorhead.png`).
- The facade_close row at y≈864-888 is the N7 counter line and the bench-back tops.

## 3. Source conformance checklist

| item | mark | view used / note |
|---|---|---|
| Silhouette and storey count | conforms | front, front_corner, left_side. The ferry has 2 storeys and a flat roof with roof boxes. The brick block has 3 storeys, a cornice, a parapet and hipped roofs. |
| Plan (top: proportions, glass box, fins and roof boxes, brick block and its roofs) | conforms (P2 lightwell, F12) | top against the source top:<br>- the long-to-short ratio is about 2:1;<br>- the glass box projects on the south front;<br>- the 3 roof boxes sit on the west edge at the source stations;<br>- the enclosure, AHU and 3 skylights are in place;<br>- the heritage block, the hipped wing, the narrow range and the court are all present. |
| Glass box: end frames | conforms | glass_close, front_corner. |
| Glass box: three glazing tiers | conforms | glass_close, entrance_canopy. |
| Glass box: mullion grid | conforms | glass_close: 5 bays, matching the source oblique and the source front. |
| Glass box: frosted band | conforms | glass_close, front_corner. |
| Glass box: projecting cap | conforms | front_corner, glass_close. The east end is closed (front_corner 660-800 / 520-640: min L 31.9). |
| Glass box: cantilever | weakly legible (F9, P2) | front_corner, glass_close. |
| Glass box interior (lounge seating) | conforms (fixed in v004) | glass_close, front_corner, roof_boxes. The seats sit on pedestals with contact shadows (`gc_lounge_v004.png`, `fc_lounge_v004.png`, `rb_lounge_v004.png`). |
| Entrance canopy and its lettering | conforms in presence and text; simplified (F9, F11, P2) | entrance_canopy, facade_close, front. HALIFAX FERRY TERMINAL is legible. |
| Storefronts | conforms (P2, F17) | entrance_canopy, glass_close, facade_close. |
| Doors (two pairs of glass doors) | conforms | entrance_canopy, interior. The leaves are glazed, with handles. |
| Wrapping canopy on the west bay and west front | conforms; the south return is shallow (F10, P2) | architecture_close, lawn_bench, left_side, front_corner. |
| West front bays and fins | conforms | left_side, architecture_close, roof_boxes: 3 full-height fins, glazed upper bays and a glazed ground floor. |
| Roof boxes | conforms | roof_boxes, roof_mechanical, top, left_side: three white boxes on the fins, cantilevered over the lawn strip. |
| Parapet bands and copings | conforms | roof_mechanical, aerial, rear. |
| Roof: membrane panels | conforms | roof_mechanical, top. |
| Roof: gravel border | conforms (flat clay band) | roof_mechanical, top. |
| Roof: louvred mechanical enclosure and AHU | conforms | roof_mechanical, right_side: the AHU has 3 fans. |
| Roof: skylights, hatches, vents | conforms | roof_mechanical: 3 skylights, hatches and vent stacks. |
| North wall | conforms (P2, F17) | rear, rear_north: punched windows, a service door and a sectional loading door. |
| East wall | conforms | right_side, rear_side. The base meets the court with a soft contact line (min L 61.7). |
| Brick block: cast-iron shopfronts | conforms | brick_neighbour, front, glass_close. |
| Brick block: window types per floor | conforms | brick_neighbour: segment-headed on the 2nd floor, round-headed on the 3rd. |
| Brick block: hoods and keystones | conforms | brick_neighbour. |
| Brick block: pilasters, string courses | conforms | brick_neighbour. |
| Brick block: corbelled frieze, bracketed cornice | conforms | brick_neighbour, glass_close. The cornice end is closed (glass_close 1100-1220 / 130-190: min L 29.8). |
| Brick block: parapet and corner finials | conforms | front, glass_close. |
| Brick block: pediment and oculus | conforms | brick_neighbour, front_corner. |
| Brick block: hipped tile roofs, chimneys | conforms (P2 lightwell, F12) | aerial, rear_side, top. |
| Hipped brick wing, narrow flat-roofed range, parking court | conforms (rear windows P2, N2) | rear_side, right_side, top. |
| Streetscape: sidewalks, curbs | conforms | front, lawn_bench, left_side. |
| Streetscape: lawn strip and bench | conforms | lawn_bench, architecture_close, left_side. |
| Streetscape: tree pits and trees | conforms (low-poly clay) | top, front, left_side. |
| Streetscape: tactile strip | conforms | entrance_canopy, top, front_corner. |
| Streetscape: crossings, lane markings | conforms | top, front_corner, front. |
| Context blocks across the west and north streets | conforms | front_corner, roof_mechanical, right_side. |
| East neighbour | deviates (F13, P2) | aerial, rear_north. |
| Harbour with piers and ferry | partial: water only (F14, P2) | roof_mechanical, front_corner. |
| Glass reads as glass with interior depth | conforms (P2, N2 and F17) | glass_close, entrance_canopy, interior, left_side, roof_boxes, lawn_bench. |
| No black slots | **deviates (N6, P1)** | A near-black, unlit patch at the stair head, on the lounge floor (roof_boxes, left_side) and on the hall ceiling (lawn_bench, architecture_close). |
| No floating or intersecting parts | **deviates (N6, P1)** | The handrails have no posts. They pass through the ceiling (interior) and stand up from the lounge floor as free stubs (left_side). The stair rises into a solid slab. The lounge seating is fixed. |
| Materials hierarchy | conforms (P2 value issue, F16) | Pale concrete, dark aluminium, clear glass, warm brick, terracotta tile and stone trim are distinct. |

## 4. Camera validity

The camera set is unchanged from v003. Eleven renders are pixel-identical to v003. The other seven differ only in the lounge seating, and in front by 2 px.

| view | valid? | note |
|---|---|---|
| front | valid | Role-matched to the source front. The west end is cropped as in the source (F8, P2). |
| front_corner | valid | Role-matched to the source oblique. The whole south front, the roof and the brick front are in frame. |
| aerial | valid | The whole ferry terminal and the heritage block are in frame. Excess empty ground (F15, P2). |
| top | valid | True plan, with the complete footprint and the neighbours. Dim (F16). |
| left_side | valid | The whole west front from the NW corner to the SW canopy end, with margin. All 3 fins and roof boxes are in view, from grade to parapet. |
| right_side | valid | The whole exposed east wall, the party-wall junction and the NE corner are in frame, with margin. |
| rear | valid | The full north elevation, with margin. |
| rear_side | valid | The ferry's north and east walls, the heritage rear, the wing and the court are all legible. |
| facade_close, glass_close, entrance_canopy, architecture_close, roof_boxes, roof_mechanical, interior, lawn_bench, rear_north | valid | Each target is legible and unobstructed. |
| brick_neighbour | valid | A street tree hides part of the shopfront level. The upper floors, cornice and pediment are clear. |

No view has its target occluded, the asset clipped, or nothing legible.

## 5. Previous findings

Baselines: v003 had 0 P0 / 1 P1; v002 had 0 P0 / 1 P1; v001 had 0 P0 / 7 P1.

| prior finding | status in v004 | evidence |
|---|---|---|
| v003 N4 (P1): upper-lounge seating rows float about 0.4 m above the lounge floor, with no legs | **fixed** | glass_close, column x=300: the seat ends at y 739, the pedestal runs y 740-770 (L 32-36), then a graded contact shadow L 39→91, with no lit floor between. Column x=420: the seat at 727, the pedestal 728-757, shadow 54→103. In v003, lit floor at L 131→111 separated the seat from its shadow.<br><br>The same holds in front_corner and roof_boxes. Crops `gc_lounge_v004.png` against `gc_lounge_v003.png`, `fc_lounge_v004.png` against `fc_lounge_v003.png`, `rb_lounge_v004.png` against `rb_lounge_v003.png`. |
| v002 N1 (P1): black slot at the bench joint in interior (x≈1006-1013, y≈878-879) | **fixed, holds** | interior is pixel-identical to v003. The bench quadrant (800-1440 / 640-1080) has min L 30.9, at a soft contact shadow under a seat. |
| v001 F1a: black slot at the east end of the glass-box cap | **fixed, holds** | front_corner 660-800 / 520-640: min L 31.9, p1 56.0. |
| v001 F1b: black hole at the north end of the west canopy | **fixed, holds** | aerial 700-860 / 640-780: min L 33.0, p1 54.7. |
| v001 F1c: black squares at the door-head joints | **fixed, holds** | entrance_canopy 480-1000 / 440-640: min L 29.6. In facade_close only the N3 crease remains (P2). |
| v001 F1d: black hairline under the heritage cornice crown | **fixed, holds** | glass_close 1100-1220 / 130-190: min L 29.8, p1 53.9. |
| v001 F2: black slit along the base of the east wall | **fixed, holds** | right_side 560-1440 / 780-1060: min L 61.7. Pixel-identical to v003. |
| v001 F3: glass box with 8 bays against the sources' 5 | **fixed, holds** | 5 bays in glass_close, front_corner and front. |
| v001 F4: opaque entrance doors | **fixed, holds** | Glazed leaves with the interior visible (entrance_canopy, interior). |
| v001 F5: flat card windows on the brick block's rear faces and wing | **fixed, holds** (P2 residual, N2) | right_side and rear_side, pixel-identical to v003. |
| v001 F6: left_side crops the west front | **fixed, holds** | See camera validity. |
| v001 F7: right_side is a close court corner shot | **fixed, holds** | See camera validity. |
| v001 smoke-test extra: black dot at the pediment apex | **fixed, holds** | front_corner 1235-1290 / 560-620: min L 52.8. |
| v003 N5 (P2): floating stair handrail | **not fixed; now part of N6 (P1)** | The rails also pierce the ceiling and the lounge floor at the black stair-head patch. |
| P2s F8-F17, N2, N3 | not fixed (not targeted), none regressed | Pixel-identical outside the lounge seating. |
| Missed in v002 and v003: the black patch at the stair head and the stair running into a solid slab | **open; now N6 (P1)** | Identical in v002, v003 and v004. Crops `rb_quad_v003.png` and `ls_landing_v003.png`, against their v004 versions. |

Against the baselines: v004 has the same count as v002 and v003 (0 P0 / 1 P1). The one remaining P1 is a different defect, which the earlier reviews did not raise. Neither N1 nor N4 has regressed.
