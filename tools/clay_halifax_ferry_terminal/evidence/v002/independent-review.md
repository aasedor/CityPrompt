# Independent RLASM v6.1 holistic review: Halifax ferry terminal clay, v002

Reviewer: independent source-locked reviewer (did not build this candidate).
Inputs judged: `sources/front.png`, `sources/oblique.jpg`, `sources/top.jpg`; all 18 renders in `renders/` at 1440x1080; the 4 phone boards in `boards/`. For the comparison I used the v001 renders in `tools/clay_halifax_ferry_terminal/evidence/v001/renders/`.
Zoomed evidence crops: `review/crops_tvkmqa/`. Pixel coordinates are in the original 1440x1080 render unless a crop is named. Luminance L = 0.2126 R + 0.7152 G + 0.0722 B (0-255).

## 1. Verdict

Verdict: FAIL

Counts: P0=0 P1=1 P2=12

All ten v001 P1 items are fixed in the pixels: F1a-d, F2, F3, F4, F5, F6 and F7. Nothing regressed. One pure-black geometric slot remains. It is a 7x2 px hole at a bench member joint in the interior view. It was already present in v001 and that review missed it. It is the same failure class as v001 F1, so under the stated rule it is P1. In the brief's terms the verdict is VISUAL_REWORK_REQUIRED. The rework is a single, finite fix.

## 2. Findings table

| id | severity | view(s) | finding (what the pixels show) | evidence | suggested fix |
|---|---|---|---|---|---|
| N1 | P1 | interior | **A pure-black rectangular slot sits in the near waiting bench**, where the backrest board meets the seat or end post of the bench run (x≈1006-1013, y≈878-879). It has hard edges and sits at L 0-7, inside lit tan wood at L 85-115 on every side. It is not a contact shadow: the shadows under the benches and counters in this frame keep their hue and stay at or above about 28. It is not a dark-by-design part: the bench is uniform timber. The same slot is in v001 at the same pixels (v001 min L 1.7), so this is a pre-existing miss, not a regression. | `crops_tvkmqa/int_bench.png`, `int_bench_wide.png`, `int_v001.png`. Pixel dump of rows 878-879: 7 3 3 5 5 5 / 3 0 1 0 1 0. | Close the bench assembly. Run the backrest board down into the seat or end post, or cap the open member end with an end face, so that no member shares or stops short of a face. Re-render interior and confirm that no pixel in the bench falls below about 40. |
| F8 | P2 | front | Carried from v001, unchanged. The front camera is role-matched, but the near west bay dominates. The glass box does not read as the tall, central volume that the source front draws. | front vs `sources/front.png` (board phone-01). | Optional: a slightly longer lens from further south-south-west. No geometry change needed. |
| F9 | P2 | glass_close, entrance_canopy, front_corner | Carried, unchanged. The lettered canopy is a flat-topped box. The source oblique shows a deeper canopy with a sloped standing-seam top. | `crops_tvkmqa/fc_glassbox.png` vs `src_obl_box.png`. | Deepen the canopy and give it a shallow standing-seam fall. |
| F10 | P2 | front_corner | Carried, unchanged. Where the canopy wraps onto the south face of the west bay, it is a shallow ledge. The west run is deep and correct. | `fc_glassbox.png` (crop x≈150-300, y≈300-350). | Give the south return the same depth as the west run. |
| F11 | P2 | facade_close, entrance_canopy, glass_close | Carried, unchanged. The letters are stair-stepped voxel glyphs. They read correctly, but crudely at close range. | facade_close y≈480-600. | Use extruded outline glyphs. |
| F12 | P2 | top, aerial, rear_side | Carried, unchanged. The heritage roof is closed over the rear lightwell. The source top shows it as a dark notch at x≈890-935, y≈350-490. | top render: a continuous roof at the matching place. | Cut a small lightwell with a closed weathering edge. |
| F13 | P2 | aerial, rear_north, rear_side | Carried, unchanged. The east context neighbour is still a windowless prism in the heritage brick hue, so it merges with the heritage block. | aerial x≈20-330, y≈215-540; rear_north x≈200-410. | Add punched windows and a different brick value. |
| F14 | P2 | roof_mechanical, front_corner | Carried, unchanged. The harbour is a flat water plane, with no legible piers or ferry. | roof_mechanical y≈240-420; front_corner top-right corner. | Add 2-3 pier slabs and a simple ferry hull. |
| F15 | P2 | aerial | Carried, unchanged. About a third of the frame is featureless ground beyond the scene extent. | aerial y≈130-440. | Extend the context, or tighten the frame. |
| F16 | P2 | all whole-envelope views, top | Carried, unchanged. The concrete is near-white against the source's mid blue-grey, and the top view is dim with a grey veil. | front, front_corner vs the sources; top. | Darken the concrete one step, and lift the top-view exposure. |
| F17 | P2 | entrance_canopy, right_side, rear_side, rear, roof_boxes | Carried, partly improved. North-end rooms are now lit (aerial and rear_north, where v001 showed dark panes). Still open: the storefront east of the doors opens onto an empty white box room (entrance_canopy x≈985-1195). Several east-wall and north-wall rooms remain nearly unlit: right_side x≈595-635, y≈390-460 (L≈21-25); rear_side x≈720-750, y≈535-580; rear window 5. Each of these has a visible frame, mullion, sill and reveal, so it is a dark room, not a void. The roof boxes keep the dark louvre strip that the source does not show. | `crops_tvkmqa/rs_win2.png`, `rsd_720.png`, `ec_storefront_east.png`. | Furnish the storefront room, balance the room lights, and lighten or drop the roof-box strip. |
| N2 | P2 | right_side, rear_side, rear_north | Residual from F5. The rear and wing windows now have proud surrounds, sashes with meeting rails or glazing bars, and readable depth. However, every pane is a uniform slate grey, and the promised lit room plate is not perceptible at review scale. They read as windows, no longer as flat cards, but as uniformly dark glass. | `crops_tvkmqa/rs_brickwin.png`, `rs_wingwin.png`, `rsd_wing.png`. | Raise the room-plate value, or vary it a little per window, so that some interior depth reads through. |
| N3 | P2 | facade_close | A 1 px high, 5 px long dark crease (L 17-24) where the door-head transom meets the centre post (x≈1132-1136, y≈837). It continues the 1 px shadow line under the transom (L 34-46) into the re-entrant corner. It is a contact crease, not an open slot, and is not visible at phone scale. | `crops_tvkmqa/fcl_1135.png`. Row y=837, x 1126-1141: 46 45 42 40 39 34 24 19 17 17 21 32 49 60 63 63. | Optional: bevel the transom underside, or let the post run 1-2 mm proud. |

### Dark areas judged genuine (not defects), and how

- **Cast-iron shopfronts, dark by design.** Applies to front x≈960-1260, y≈640-860; front_corner x≈840-960, y≈720-840; glass_close x≈1140-1440, y≈740-1000; brick_neighbour lower band. The darkest pixels (L 8-20) are the dark-green pier sides and the slim transom glazing bars of the heritage shopfronts. They keep a green or brown cast, they follow the pier and muntin outlines, and they sit inside dark-painted members, not at a gap between two lit faces (`front_junction.png`, `front_shop2.png`, `fc_shopfront.png`, `bn_shop.png`).
- **Contact and overhang shadows.** These keep their hue and grade softly:
  - the soffits of the window heads and arch springings on the brick block (brick_neighbour y≈240-300, L 10-25, warm brown; `bn_arch1.png`);
  - the eave shadow on the brick hip (rear_north x≈650-680, y≈265-285, RGB 34/9/1; `rn_chim.png`);
  - the narrow service passage between the context prism and the heritage wing (rear_side x≈150-320, y≈560-1000, a soft gradient in a brick hue; `rsd_dark.png`);
  - the shadow line under the desk counter (facade_close y≈886, 2 px at L≈28; `fcl_desk.png`);
  - the occluded gap between two distant context blocks (right_side x≈1310-1340, y≈200-280; `rs_top2.png`).
- **Dark by design.**
  - door handles (architecture_close, lawn_bench);
  - the steel stair handrail in interior: a thin rod at L≈16 that follows the stair rake into the stair void;
  - black bench bases (aerial, left_side, lawn_bench);
  - the dark-grey loading door and the aluminium mullions;
  - the stair underside seen through the glass in roof_boxes (x≈955-990, y≈815-860, min L 19, soft edges, enclosed by a lit floor; `rb_wedge.png`).
- **Top view.** No dark stripes between volumes. The ferry/brick junction strip (x 752-785, y 400-900) has a minimum L of 89 and a median of 129.

## 3. Source conformance checklist

| item | mark | view used / note |
|---|---|---|
| Silhouette and storey count | conforms | front, front_corner, left_side. The ferry has 2 storeys, a flat roof and roof boxes. The brick block has 3 storeys, a cornice, a parapet and hipped roofs. The brick cornice sits just above the ferry cap, as in the oblique. |
| Plan (top: proportions, glass box, fins and roof boxes, brick block and roofs) | conforms (P2 lightwell, F12) | top vs the source top. The roof ratio is about 2.04 (2.08 with the box projection), against about 2.1-2.2 in the source. The glass box projects at the south. The 3 roof boxes sit at 0.18-0.26, 0.52-0.60 and 0.77-0.85 of the length, matching the source. The enclosure, AHU and 3 skylights are in matching positions, with the enclosure a few percent further east. The heritage block, wing, narrow range and parking court are all in place. |
| Glass box: end frames | conforms | glass_close, front_corner. |
| Glass box: three glazing tiers | conforms | glass_close, entrance_canopy. |
| Glass box: mullion grid | conforms (F3 fixed) | glass_close: 5 bays (mullions at x≈110/380/605/785/940/1060). front_corner and front: 5 bays. This matches the source oblique (`src_obl_box.png`) and the source front. |
| Glass box: frosted band | conforms | glass_close, front_corner. |
| Glass box: projecting cap | conforms (F1a fixed) | front_corner, glass_close. The east end is closed and lit (`fc_eastcap.png`, `gc_capend.png`). |
| Glass box: cantilever | weakly legible (F9, P2) | front_corner, glass_close. |
| Entrance canopy and lettering | conforms in presence and text; simplified (F9, F11, P2) | entrance_canopy, facade_close, front. |
| Storefronts | conforms (P2 empty east room, F17) | entrance_canopy, glass_close. The storefronts are glazed, with benches and a desk behind. |
| Doors (two pairs of glass doors) | conforms (F4 fixed) | entrance_canopy: two pairs of glazed stile-and-rail leaves, with handles and the interior visible. Also interior, front, front_corner (`fc_doors.png`). The west door is glazed too (architecture_close, `ac_westdoors.png`). |
| Wrapping canopy on west bay and west front | conforms on the west run; south return shallow (F10, P2) | architecture_close, lawn_bench, left_side, front_corner. The north end is closed (F1b fixed). |
| West front bays and fins | conforms | left_side, architecture_close, roof_boxes: 3 full-height fins, glazed upper bays and a glazed ground floor. |
| Roof boxes | conforms | roof_boxes, roof_mechanical, top, left_side: 3 white boxes on the fins, cantilevering over the lawn strip. |
| Parapet bands and copings | conforms | roof_mechanical, aerial, rear. |
| Roof: membrane panels | conforms | roof_mechanical, top. |
| Roof: gravel border | conforms (flat clay band) | roof_mechanical, top. |
| Roof: louvred enclosure and AHU | conforms | roof_mechanical, top, right_side: AHU with 3 fans. |
| Roof: skylights / hatches / vents | conforms | roof_mechanical: 3 skylights, hatches and several vent stacks. |
| North wall | conforms | rear, rear_north, right_side: punched windows with surrounds and sills, a service door and a sectional loading door. Uneven room lighting is P2 (F17). |
| East wall | conforms (F2 fixed) | right_side, rear_side: punched windows and a service door. The base meets the court paving with a soft contact line, at L about 52-65 (`rs_base_z1.png`, `rs_base_z2.png`, `rsd_base_z.png`). |
| Brick block: cast-iron shopfronts | conforms | brick_neighbour, front, front_corner. |
| Brick block: window types per floor | conforms | brick_neighbour: segment-headed on the 2nd floor and round-headed on the 3rd, with sash and meeting rails. |
| Brick block: hoods and keystones | conforms | brick_neighbour. |
| Brick block: pilasters, string courses | conforms | brick_neighbour. |
| Brick block: corbelled frieze, bracketed cornice | conforms (F1d fixed) | brick_neighbour; glass_close shows the cornice end plate closed (`gc_cornice.png`). |
| Brick block: parapet and corner finials | conforms | front, glass_close. |
| Brick block: pediment and oculus | conforms | brick_neighbour, front_corner. The apex block closes the junction of the copings, with no dark dot (`fc_pediment.png`, `front_pediment.png`). |
| Brick block: hipped tile roofs, chimneys | conforms (P2 lightwell, F12) | aerial, rear_side, top. |
| Brick block: rear and wing windows | conforms (F5 fixed; P2 residual N2) | right_side, rear_side, rear_north: proud surrounds, sashes and glazing bars. |
| Hipped brick wing, narrow flat-roofed range, parking court | conforms | rear_side, right_side, top. |
| Streetscape: sidewalks, curbs | conforms | front, lawn_bench, left_side. |
| Streetscape: lawn strip and bench | conforms | lawn_bench, architecture_close, left_side. |
| Streetscape: tree pits and trees | conforms (low-poly clay) | top, front, left_side. |
| Streetscape: tactile strip | conforms | entrance_canopy, top, front_corner. |
| Streetscape: crossings, lane markings | conforms | top, front_corner, front. |
| Context blocks across the west and north streets | conforms | front_corner, roof_mechanical, right_side. |
| East neighbour | deviates (F13, P2) | aerial, rear_north. |
| Harbour with piers and ferry | partial: water only (F14, P2) | roof_mechanical, front_corner. |
| Glass reads as glass with interior depth | conforms (P2 N2, F17) | glass_close, entrance_canopy, interior, left_side, roof_boxes, lawn_bench. The interiors are furnished and lit, the doors are now transparent, and the frosted band reads frosted. |
| No black slots | deviates (N1, P1) | Every v001 slot is closed (F1a-d, F2). One pure-black slot remains in the interior bench. No other near-black pixel in the 18 renders is a geometric gap (see "Dark areas judged genuine"). |
| Materials hierarchy | conforms (P2 value issue, F16) | Pale concrete, dark aluminium, clear glass, warm brick, terracotta tile and stone trim are all distinct. |

## 4. Camera validity

| view | valid? | note |
|---|---|---|
| front | valid | Role-matched to the source front. The west end is cropped as in the source. The glass box and brick block are legible. A tree overlaps part of the box, as in the source (F8, P2). |
| front_corner | valid | Matches the source oblique's role. The whole south front, the roof and the brick front are in frame. |
| aerial | valid | The whole ferry and heritage block are in frame. Excess empty ground (F15, P2). |
| top | valid | True plan with the complete footprint and neighbours. Slightly dim (F16). |
| left_side | **valid (F6 fixed)** | A raised west elevation from the far sidewalk. The NW corner (x≈145) and the SW canopy end (x≈1330) both sit inside the frame with more than 100 px of neutral margin. All 3 fins and roof boxes, the grade (y≈660) and the parapet (y≈400) are visible. The trees stand clear of the central bay. |
| right_side | **valid (F7 fixed)** | A raised three-quarter view from the north-east. It shows the whole exposed east wall (x≈545-970), the party-wall junction with the heritage block, the NE corner and the north wall to x≈1310, from grade to parapet, with margin. The heritage wing is cut by the left and bottom frame edges, but it is not the target of this view. |
| rear | valid | The full north elevation from grade to parapet, with margin. |
| rear_side | valid | The ferry's north and east walls, the heritage rear, the wing and the court are all legible. The foreground context prism clips only the frame corners. |
| facade_close, glass_close, entrance_canopy, architecture_close, roof_boxes, roof_mechanical, interior, lawn_bench, rear_north | valid | Each target is legible and unobstructed. |
| brick_neighbour | valid | A street tree hides part of the shopfront level, but enough remains to judge it. The upper floors, cornice and pediment are clear. |

## 5. Previous findings (v001: 0 P0 / 7 P1)

I compared every view pixel by pixel against v001. Differences above the noise floor are confined to the targeted regions: the glass box and doors in entrance_canopy, facade_close, glass_close, interior and front; the north-end rooms in aerial and rear_north; the west doors in architecture_close and lawn_bench; and the reframed left_side and right_side. brick_neighbour, rear and top are otherwise identical to v001.

| v001 finding | status | evidence |
|---|---|---|
| F1a black slot at the glass-box cap east end (front_corner, glass_close) | **fixed** | The cap's end face is closed and lit. In front_corner (660-800, 520-640) the minimum L is 31.9 and the 1st percentile is 56; in v001 the slot was at 0-6. See `fc_eastcap.png` and `gc_capend.png`. |
| F1b black hole at the west canopy north end (aerial, architecture_close) | **fixed** | In aerial (700-860, 640-780) the minimum L is 33.0, against 0.7 in v001 at the same place (`ae_canopyN.png` vs `ae_canopyN_v001.png`). architecture_close shows a closed slab end with its drip edge (`ac_canopyend.png`). |
| F1c black squares at the door-head joints (entrance_canopy, facade_close, interior) | **fixed** | The entrance_canopy door-head band (480-1000, 440-640) has a minimum L of 29.6 and a 1st percentile of 44 (`ec_doorhead.png`). interior door head: minimum 25.4 (`int_doorhead.png`). In facade_close only a 1 px contact crease remains (N3, P2). |
| F1d black hairline under the heritage cornice crown (glass_close) | **fixed** | The end plate is visible and runs from the bed mould to the crown. The crop's minimum L is 25.8, in shaded stone, with no hairline (`gc_cornice.png`). |
| F2 black slit along the base of the east wall (right_side) | **fixed** | A soft contact line at L about 52-65, with no slit, along the whole base in right_side and rear_side (`rs_base_z1.png`, `rs_base_z2.png`, `rsd_base_z.png`). |
| F3 glass box with 8 bays against the sources' 5 | **fixed** | 5 equal bays, with the frosted band and 3 tiers kept (glass_close, front_corner, front, entrance_canopy). |
| F4 opaque entrance doors | **fixed** | The leaves are glazed stile-and-rail frames with the interior visible from outside and from inside. Handles are kept. The leaf bottoms are clean, with no slits (`ec_doorbottom.png`). |
| F5 flat grey card windows on the brick block's rear faces and wing | **fixed** (P2 residual, N2) | Proud surrounds, sashes with meeting rails and four-pane glazing bars, against plain cards in v001 (`rsd_wing.png` vs `rsd_v001_left.png`). The panes still read as uniform slate. |
| F6 left_side crops the west front | **fixed** | See camera validity. |
| F7 right_side is a close court corner shot | **fixed** | See camera validity. |
| Smoke-test extra: black dot at the pediment apex | **fixed** | `fc_pediment.png`, `front_pediment.png`. |
| v001 P2s F8-F17 | not fixed (they were not targeted), none regressed | F17 is partly improved: the north-end rooms are now lit. |
| Missed in v001: black slot in the interior bench | **still open; now N1 (P1)** | Present at the same pixels in v001 and v002. |
