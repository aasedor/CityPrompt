# Independent RLASM v6.1 holistic review: Halifax ferry terminal clay, v003

Reviewer: independent source-locked reviewer. I did not build this candidate.

Inputs judged:
- the locked sources `sources/front.png`, `sources/oblique.jpg` and `sources/top.jpg`;
- all 18 renders in `renders/`, at 1440x1080;
- the 4 phone boards in `boards/`;
- for the comparison, the v002 renders in `../v002/renders/`.

Zoomed evidence crops are in `review/crops_qhzmwe/`. Pixel coordinates refer to the original 1440x1080 render unless a crop is named. Luminance is L = 0.2126 R + 0.7152 G + 0.0722 B, on a 0-255 scale.

## 1. Verdict

Verdict: FAIL

Counts: P0=0 P1=1 P2=13

**The v002 P1 is fixed.** The bench-joint slot in the interior view is gone. All seven v001 P1 fixes still hold, and nothing regressed. The v003 change shows up only on the benches, in 11 of the 18 renders, and 7 renders are pixel-identical to v002.

**One P1 remains.** Every upper-lounge seating row floats about 0.4 m above the lounge floor, with no legs or base. The glass box shows them as shelves hanging in mid-air, with lit floor between each seat and its own shadow. This defect is in v001, v002 and v003, and both earlier reviews missed it. The brief names floating parts as a failure, so it is P1. In the brief's terms the verdict is VISUAL_REWORK_REQUIRED, and the fix is one finite change.

## 2. Findings table

| id | severity | view(s) | finding (what the pixels show) | evidence | likely cause | suggested fix |
|---|---|---|---|---|---|---|
| N4 | P1 | glass_close, front_corner, roof_boxes, left_side (faint) | **The upper-lounge seating rows float.**<br><br>Behind the glass box, the three south lounge benches show only a backrest board and a seat ledge. There are no legs, plinth or base.<br><br>A band of lit floor runs between the underside of each seat and its soft shadow on the floor, so each bench reads as an L-shaped shelf hanging in the air. The west lounge rows behind the fins show the same thing in roof_boxes.<br><br>This is not a lighting artefact: the concourse benches on the ground floor, in the same renders, sit on dark bases that meet the floor. | glass_close, column x=300: the seat underside ends at y≈739. Lit floor follows at L 131→111 (y 741-768), then the bench's own shadow at L 69 (y 771-777), then floor again.<br><br>Column x=420: the same pattern, seat at y≈726, lit floor at L 154→126, shadow at L≈88 (y 759-765).<br><br>Crops: `crops_qhzmwe/gc_upper_lounge.png`, `fc_box_lounge.png` (front_corner), `rb_lounge.png` (roof_boxes).<br><br>The defect is identical in v002 (`gc_upper_lounge_v002.png`) and was present in v001. | The lounge seating boxes (the seat at F1+0.45 and the back at F1+0.75) have no support member. Only the concourse benches have the `hardware` pedestal. | Give every lounge seating row, both the west rows and the south rows, a pedestal or a pair of end legs from the lounge floor to the seat underside, in the same dark hardware as the concourse benches. Re-render glass_close, front_corner and roof_boxes, and confirm that each seat meets its shadow with no lit floor between. |
| N5 | P2 | interior, front, lawn_bench, architecture_close | New observation, not a regression. The stair handrail is a bare rod with no posts or balusters, set just outside the tread ends. Its lower end stops in mid-air about 1 m above the floor. It reads as a floating line, not a rail. | `crops_qhzmwe/int_stair.png`: the rail ends at about (952, 675) in interior, with no support beneath it. | The handrail beams are not tied to the treads or the floor. | Add 3-4 posts from the treads to the rail, or a newel at the foot of the stair. |
| F8 | P2 | front | Carried from earlier versions, unchanged. The near west bay dominates the frame, so the glass box does not read as the source front's central tall volume. | Board phone-01. | Camera fitted to the box and the brick block. | Optional: a slightly longer lens. |
| F9 | P2 | glass_close, entrance_canopy, front_corner | Carried, unchanged. The canopy is a flat-topped box. The source has a deeper canopy with a sloped standing-seam top. | glass_close y≈840-950. | Simplified primitive. | Deepen the canopy and give its top a shallow fall. |
| F10 | P2 | front_corner | Carried, unchanged. The south return of the wrapping canopy is a shallow ledge. | front_corner, at the canopy's south-west corner (pixel-identical to v002). | — | Match the depth of the west run. |
| F11 | P2 | facade_close, entrance_canopy, glass_close | Carried, unchanged. The letter glyphs are stair-stepped voxel shapes. | facade_close y≈480-600. | — | Use extruded outline glyphs. |
| F12 | P2 | top, aerial, rear_side | Carried, unchanged. The heritage roof runs closed over the rear lightwell. | top render. | — | Cut the lightwell. |
| F13 | P2 | aerial, rear_north, rear_side | Carried, unchanged. The east context neighbour is a windowless prism in the heritage brick hue. | aerial x≈20-330, y≈215-540. | — | Add punched windows and use a different brick value. |
| F14 | P2 | roof_mechanical, front_corner | Carried, unchanged. The harbour is flat water only, with no piers or ferry. | roof_mechanical y≈240-420. | — | Add pier slabs and a ferry hull. |
| F15 | P2 | aerial | Carried, unchanged. Large featureless ground beyond the scene extent. | aerial y≈130-440. | — | Extend the context, or tighten the frame. |
| F16 | P2 | whole-envelope views, top | Carried, unchanged. The concrete is near-white against the source's blue-grey, and the top view is dim. | front, front_corner, top. | — | Darken the concrete one step, and lift the top-view exposure. |
| F17 | P2 | entrance_canopy, right_side, rear_side, rear, roof_boxes | Carried, unchanged:<br>- the storefront room east of the doors is empty and white (entrance_canopy x≈985-1195);<br>- some east-wall and north-wall rooms are nearly unlit (rear window 5, right_side x≈595-635);<br>- the roof boxes keep their dark louvre strip. | As in v002. | — | Furnish and light those rooms, and lighten the strip. |
| N2 | P2 | right_side, rear_side, rear_north | Carried, unchanged. The rear and wing panes of the brick block are uniform slate grey, with little interior depth perceptible. | rear_side x≈320-560, y≈690-960. | — | Raise or vary the room-plate value. |
| N3 | P2 | facade_close | Carried, unchanged; the builder states it is not addressed. A 1 px dark contact crease where the door-head transom meets the centre post. It is an inside-corner shadow, not an open slot, and it is invisible at phone scale. | Row y=837, x 1126-1141: 46 45 42 41 39 34 24 19 18 18 22 32 49 60 63 63. Crop `crops_qhzmwe/fcl_transom.png`. | — | Optional: bevel the transom, or let the post run proud. |

### Dark areas: which are geometric defects and which are genuine

I scanned all 18 renders for pixels with L below 30 whose 15x15 neighbourhood mean is above 75, which is how a slot inside lit material shows up. I did the same for v002.

**Results.** Every v003 hit falls in the same 24 px cell as a v002 hit, with one exception: a single pixel at L 30 in interior (216, 402). That is the soft shadow line under the door transom, not a slot. In interior, four v002 cells are gone, including the bench slot. No render has a hard-edged near-black hole between two lit faces. The remaining dark pixels are genuine, as follows.

- **Cast-iron shopfronts, dark by design.** These are in front (x≈990-1135, y≈680-730, L 8-13), glass_close (x 1165, y 755-764, L 10) and brick_neighbour (y≈926-960, L 16-20). They keep a green cast (RGB about 10/12/9 to 17/21/18) and follow the outlines of the shopfront piers and muntins. They sit inside dark-painted members, not in a gap between two lit faces.
- **Contact and overhang shadows.** These keep a warm brick hue and grade softly:
  - the arch-head soffits and window-hood undersides on the brick block (brick_neighbour x 154, 592, 940, 1252, y 277-311; RGB about 19-34 / 6-16 / 1-9);
  - the eave shadow on the brick hip (rear_north 658, 273, RGB 33/11/4);
  - the gap between distant context blocks (right_side 1320, 274).
- **Dark by design.**
  - the black bench bases: aerial 1030-1047 / 622-633 and left_side 1183 / 716 (`ae_bench.png`);
  - the door handles: lawn_bench 765 / 573 and rear_north 1382 / 948;
  - the slim aluminium mullions in shade: front 506 / 495-503, RGB 14/18/18;
  - the stair handrail rod in interior (see N5);
  - the stair underside seen through the glass in roof_boxes. Its minimum L is above 16, its edges are soft, and lit floor surrounds it.
- **The v002 bench slot is gone.** Interior rows 878-879 at x 1006-1013 now read 84-94 in tan timber, against 0-7 in v002. Across the whole bench quadrant (x 800-1440, y 640-1080) the minimum L is 30.9, at a soft contact shadow under the bench seats; it was 0.2 in v002. See `int_bench_v003.png` against `int_bench_v002.png`, and `int_benches_wide_v003.png`.

## 3. Source conformance checklist

| item | mark | view used / note |
|---|---|---|
| Silhouette and storey count | conforms | front, front_corner, left_side. The ferry has 2 storeys and a flat roof with roof boxes. The brick block has 3 storeys, a cornice, a parapet and hipped roofs. |
| Plan (top: proportions, glass box, fins and roof boxes, brick block and its roofs) | conforms (P2 lightwell, F12) | top against the source top. The long-to-short ratio is about 2:1, the glass box projects at the south, the 3 roof boxes sit on the west edge at matching stations, the enclosure, AHU and 3 skylights are in place, and the heritage block, wing, narrow range and court are all present. |
| Glass box: end frames | conforms | glass_close, front_corner. |
| Glass box: three glazing tiers | conforms | glass_close, entrance_canopy. |
| Glass box: mullion grid | conforms | glass_close: 5 bays, matching the source oblique and the source front. |
| Glass box: frosted band | conforms | glass_close, front_corner. |
| Glass box: projecting cap | conforms | front_corner, glass_close. The east end is closed (front_corner 660-800 / 520-640: min L 31.9). |
| Glass box: cantilever | weakly legible (F9, P2) | front_corner, glass_close. |
| Glass box interior (lounge furniture) | deviates (N4, P1) | glass_close, front_corner. The lounge benches float. |
| Entrance canopy and its lettering | conforms in presence and text; simplified (F9, F11, P2) | entrance_canopy, facade_close, front. |
| Storefronts | conforms (P2, F17) | entrance_canopy, glass_close, facade_close. |
| Doors (two pairs of glass doors) | conforms | entrance_canopy, interior. The leaves are glazed stile-and-rail with handles. |
| Wrapping canopy on the west bay and west front | conforms; the south return is shallow (F10, P2) | architecture_close, lawn_bench, left_side, front_corner. |
| West front bays and fins | conforms | left_side, architecture_close, roof_boxes: 3 full-height fins, glazed upper bays and a glazed ground floor. |
| Roof boxes | conforms | roof_boxes, roof_mechanical, top, left_side. |
| Parapet bands and copings | conforms | roof_mechanical, aerial, rear. |
| Roof: membrane panels | conforms | roof_mechanical, top. |
| Roof: gravel border | conforms (flat clay band) | roof_mechanical, top. |
| Roof: louvred mechanical enclosure and AHU | conforms | roof_mechanical, right_side: an AHU with 3 fans. |
| Roof: skylights, hatches, vents | conforms | roof_mechanical: 3 skylights, hatches and vent stacks. |
| North wall | conforms (P2, F17) | rear, rear_north: punched windows, a service door and a sectional loading door. |
| East wall | conforms | right_side, rear_side. The base meets the court with a soft contact line (min L 61.7 along the base). |
| Brick block: cast-iron shopfronts | conforms | brick_neighbour, front, glass_close. |
| Brick block: window types per floor | conforms | brick_neighbour: segment-headed on the 2nd floor, round-headed on the 3rd. |
| Brick block: hoods and keystones | conforms | brick_neighbour. |
| Brick block: pilasters, string courses | conforms | brick_neighbour. |
| Brick block: corbelled frieze, bracketed cornice | conforms | brick_neighbour, glass_close. The cornice end plate is closed (min L 29.8). |
| Brick block: parapet and corner finials | conforms | front, glass_close. |
| Brick block: pediment and oculus | conforms | brick_neighbour, front_corner. |
| Brick block: hipped tile roofs, chimneys | conforms (P2 lightwell, F12) | aerial, rear_side, top. |
| Brick block: rear and wing windows | conforms (P2, N2) | right_side, rear_side. |
| Hipped brick wing, narrow flat-roofed range, parking court | conforms | rear_side, right_side, top. |
| Streetscape: sidewalks, curbs | conforms | front, lawn_bench, left_side. |
| Streetscape: lawn strip and bench | conforms | lawn_bench, architecture_close. The street bench backrest now sits proud of the seat with inset ends, and the joint is clean (`lb_bench.png`, `ac_bench.png`). |
| Streetscape: tree pits and trees | conforms (low-poly clay) | top, front, left_side. |
| Streetscape: tactile strip | conforms | entrance_canopy, top, front_corner. |
| Streetscape: crossings, lane markings | conforms | top, front_corner, front. |
| Context blocks across the west and north streets | conforms | front_corner, roof_mechanical, right_side. |
| East neighbour | deviates (F13, P2) | aerial, rear_north. |
| Harbour with piers and ferry | partial: water only (F14, P2) | roof_mechanical, front_corner. |
| Glass reads as glass with interior depth | conforms (P2, N2 and F17) | glass_close, entrance_canopy, interior, left_side, roof_boxes, lawn_bench. |
| No black slots | conforms | The v002 slot is closed. No geometric near-black gap remains in any of the 18 renders (see "Dark areas" above). |
| No floating or intersecting parts | deviates (N4, P1; N5, P2) | glass_close, front_corner, roof_boxes, interior. |
| Materials hierarchy | conforms (P2 value issue, F16) | Pale concrete, dark aluminium, clear glass, warm brick, terracotta tile and stone trim are distinct. |

## 4. Camera validity

The camera set is unchanged from v002. front_corner, rear, rear_north, rear_side, right_side, roof_mechanical and top are pixel-identical to v002, apart from one bench column in top. Every other view differs only in bench pixels.

| view | valid? | note |
|---|---|---|
| front | valid | Role-matched to the source front. The west end is cropped as in the source (F8, P2). |
| front_corner | valid | Role-matched to the source oblique. The whole south front, the roof and the brick front are in frame. |
| aerial | valid | The whole ferry and the heritage block are in frame. Excess empty ground (F15, P2). |
| top | valid | True plan with the complete footprint and neighbours. Dim (F16). |
| left_side | valid | The whole west front from the NW corner to the SW canopy end, with margin. All 3 fins and roof boxes are in view, from grade to parapet. |
| right_side | valid | A raised three-quarter view from the north-east. The whole exposed east wall, the party-wall junction and the NE corner are in frame, with margin. |
| rear | valid | The full north elevation, with margin. |
| rear_side | valid | The ferry's north and east walls, the heritage rear, the wing and the court are all legible. |
| facade_close, glass_close, entrance_canopy, architecture_close, roof_boxes, roof_mechanical, interior, lawn_bench, rear_north | valid | Each target is legible and unobstructed. |
| brick_neighbour | valid | A street tree hides part of the shopfront level. The upper floors, cornice and pediment are clear. |

## 5. Previous findings

Baselines: v002 had 0 P0 / 1 P1; v001 had 0 P0 / 7 P1.

| prior finding | status in v003 | evidence |
|---|---|---|
| v002 N1 (P1): 7x2 px pure-black slot at the bench joint in interior (x≈1006-1013, y≈878-879) | **fixed** | Rows 878-879 now read L 84-94 (tan timber) against 0-7 in v002. The bench quadrant minimum is 30.9 (a soft contact shadow), against 0.2 in v002. The slot class does not appear on any other bench: concourse benches (`fcl_benches.png`, `gc_benches.png`, `ec_benches.png`), the street bench (`lb_bench.png`, `ac_bench.png`, `ae_bench.png`) and the lounge rows (`gc_upper_lounge.png`). |
| v001 F1a: black slot at the east end of the glass-box cap | **fixed, holds** | front_corner 660-800 / 520-640: min L 31.9, p1 56.0. Pixel-identical to v002. |
| v001 F1b: black hole at the north end of the west canopy | **fixed, holds** | aerial 700-860 / 640-780: min L 33.0, p1 54.9. |
| v001 F1c: black squares at the door-head joints | **fixed, holds** | entrance_canopy 480-1000 / 440-640: min 29.6. Interior door head: min 25.6 (`int_doorhead.png`). In facade_close only the N3 crease remains (P2). |
| v001 F1d: black hairline under the heritage cornice crown | **fixed, holds** | glass_close 1100-1220 / 130-190: min 29.8, p1 54.2. |
| v001 F2: black slit along the base of the east wall | **fixed, holds** | right_side 560-1440 / 780-1060: min 61.7. Pixel-identical to v002. |
| v001 F3: glass box with 8 bays against the sources' 5 | **fixed, holds** | 5 bays in glass_close, front_corner and front. |
| v001 F4: opaque entrance doors | **fixed, holds** | Glazed leaves with the interior visible (entrance_canopy, interior). |
| v001 F5: flat card windows on the brick block's rear faces and wing | **fixed, holds** (P2 residual, N2) | right_side and rear_side, pixel-identical to v002. |
| v001 F6: left_side crops the west front | **fixed, holds** | See camera validity. |
| v001 F7: right_side is a close court corner shot | **fixed, holds** | See camera validity. Pixel-identical to v002. |
| v001 smoke-test extra: black dot at the pediment apex | **fixed, holds** | front_corner is pixel-identical to v002. |
| P2s F8-F17, N2, N3 | not fixed (not targeted), none regressed | Unchanged pixels outside the bench regions. |
| Missed in v001 and v002: floating upper-lounge seating | **open; now N4 (P1)** | Identical in v002 (`gc_upper_lounge_v002.png`). |
