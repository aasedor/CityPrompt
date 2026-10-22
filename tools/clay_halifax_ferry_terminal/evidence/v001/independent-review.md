# Independent RLASM v6.1 holistic review: Halifax ferry terminal clay, v001

Reviewer: independent source-locked reviewer (did not build this candidate).
Inputs judged: `sources/front.png`, `sources/oblique.jpg`, `sources/top.jpg`; all 18 renders in `renders/` at 1440 px; the 4 phone boards in `boards/`.
Zoomed evidence crops: `review/crops_qoswyc/`. Pixel coordinates below are in the original 1440x1080 render unless a crop is named.

## 1. Verdict

Verdict: FAIL

Counts: P0=0 P1=7 P2=10

The candidate is the right building, with the right plan, storeys, roof programme, fins and roof boxes, brick neighbour and streetscape. It still has unclosed member ends that render pure black, a ground-contact slit, a wrong glass-box mullion rhythm, opaque entrance doors, flat blind windows on the brick block's rear and wing, and two whole-side cameras that crop the asset. In the brief's terms it is VISUAL_REWORK_REQUIRED.

## 2. Findings table

| # | severity | view(s) | finding (what the pixels show) | evidence | likely cause | suggested finite fix |
|---|---|---|---|---|---|---|
| F1 | P1 | front_corner, aerial, entrance_canopy, facade_close, interior, glass_close | Pure-black voids at unclosed member ends. (a) A black vertical slot at the east end of the glass-box cap, between the cap and the recessed return wall beside the brick block. (b) A black rectangular hole at the north end of the west-front canopy, where the slab meets the north fin. (c) Black squares where the door-head transom meets the jambs: three on the entrance, also visible from inside. (d) A black hairline under the heritage cornice crown at the pediment end. | (a) front_corner x≈724-728, y≈586-598, luminance 0-6 against 140-150 lit faces either side (crop `r_fc_eastslot.png`). (b) aerial x≈735-760, y≈715-735 (`r_ae_dark.png`). (c) entrance_canopy x≈510/740/965, y≈562-570; facade_close x≈725/1150, y≈820-838; interior x≈325, y≈410 (`r_fc2_black.png`). (d) glass_close x≈1130-1200, y≈150-170 (`r_gc_top.png`). These are not shadows: the canopy soffits, contact shadows and shaded brick in this lighting never fall below about 50. The voids are hard-edged and at or near 0 even where both neighbouring faces are lit, and the dark door handles in the same frame stay above 12. | Box ends left open or cut back short of the adjoining owner, so the camera sees the unlit inside of the shell or a gap behind it. | Close every end face. Run the cap, canopy slab and cornice crown into their bearing walls or fins, or cap them with an end plate. Extend the door-head transom to the jamb faces. Re-render front_corner, aerial, entrance_canopy, facade_close, interior and glass_close and confirm that no pixel near those joints falls below about 40. |
| F2 | P1 | right_side | A continuous black hairline runs along the whole base of the exposed east wall where it meets the parking-court paving, so the wall reads as slightly lifted or slit off the ground. | right_side, from about x 590, y 820 to x 1430, y 1050, 1-2 px wide and near 0 luminance (`r_rs_base.png`). The north wall (rear, rear_north) and the west front have no such line. | The parking-court slab and the wall plinth leave a sliver gap, or the court slab stops short of the wall. | Extend the court paving under the wall line, or drop the wall base into the slab, then re-render right_side and rear_side. |
| F3 | P1 | glass_close, front_corner, front, facade_close, entrance_canopy | Wrong rhythm on the glass box. The model has 8 narrow bays across the box front. The sources have 5 wide bays: tall panes, each about as wide as the end frame is deep. At phone scale the box reads as a dense grid, not the source's broad glazing. | glass_close mullions at x≈110/285/440/575/695/805/905/990/1060, giving 8 bays. Source oblique (`src_obl_glassbox.png`): verticals at about 358/418/480/546/612/668 in the crop, giving 5 bays. Source front (`src_front_box.png`): 5 bays. The tier count (frosted band plus 3 clear tiers) does match. | The bay module was set from a generic curtain-wall spacing, not from the source. | Rebuild the box grid as 5 equal bays between the end frames. Keep the frosted band and the 3 transom tiers. Re-render the front, glass and entrance views. |
| F4 | P1 | entrance_canopy, facade_close, glass_close, front, interior | The two pairs of entrance doors are opaque, dark grey slab panels with handles: no glass and no view through, from outside or inside. The sources show two pairs of glazed aluminium-framed doors under a glazed transom. | entrance_canopy x≈515-975, y≈570-850: solid panels. Interior x≈0-320: the same doors are opaque from inside. Source front (`src_front_box.png`) doors at crop x≈280-460 are clearly glazed. | A door assembly with a solid leaf material instead of the storefront glass authority. | Make each leaf a slim aluminium stile frame around the same optical glass as the storefronts, with the interior visible behind it. Keep the handles. |
| F5 | P1 | right_side, rear_side, rear_north, aerial | Every window on the brick block's rear faces and on its hipped rear wing is a flat grey card inside a stone surround: no reveal, no sash, no glass optics, no room behind. This contradicts the same building's street-front windows, which do have depth. The method lists this as a hard stop (flat window). | right_side x≈80-430, y≈0-930: six large flat panels (`r_rs_windows.png`). rear_side wing and rear wall (`r_rsd_left.png`). Compare brick_neighbour, where the windows have sash bars, glass and an interior. | The secondary faces got placeholder window panels, not the cut-reveal window assembly used on the south front. | Apply the same cut-wall window section to the rear and wing faces: reveal, recessed sash with a meeting rail, glass, offset room plane. Simple segmental or flat heads are enough on unseen faces. |
| F6 | P1 | left_side | The whole-side camera for the 41 m west front crops both ends. The north roof box is cut at the left edge (x 0-140), and the glazing runs off the right edge, so the SW corner and the west-bay wrap are missing. Neither the full footprint nor any neutral margin is shown. The method lists this as a hard stop (whole-side camera crops the asset). | left_side frame edges at x=0 and x=1440 both cut building geometry. | The camera was placed for a centred elevation crop and never fitted to the actual west-front length. | Pull back, or widen to an orthographic-like long lens, so that both the north-west and south-west corners, all three fins and roof boxes, grade and the parapet fit with visible margin. Keep the tree out of the central bay. |
| F7 | P1 | right_side | The "right_side" camera is a close corner shot from the parking court. It shows part of the ferry's east wall cut at the right edge (no NE corner margin) and the brick wing cut at the top and left. The full exposed east side, its roof line and its ground are not framed. | right_side: the east wall continues past x=1440; the wing's eaves leave the frame at the top; there is no neutral margin. rear_side does show the east wall whole, but the named whole-side view is invalid. | The camera sits inside the narrow court with too short a standoff. | Re-aim from above the parking court, in a raised, three-quarter view if the court is too narrow, so the whole exposed east wall from grade to parapet, the party-wall junction and the NE corner all sit inside the frame with margin. |
| F8 | P2 | front | The front camera matches the source composition approximately: the glass box sits near the source position and the brick block spans a similar width. But the near west bay dominates, and the glass box no longer reads as the tallest, central volume the source front draws. | front vs `sources/front.png` on board phone-01. | The source front cannot be satisfied together with the top and oblique views (see section 5). | Optional: a slightly longer lens from a little further south-south-west, to give the box more weight. No geometry change. |
| F9 | P2 | glass_close, entrance_canopy, front_corner | The lettered entrance canopy is a flat-topped box of moderate depth. The source oblique shows a deeper canopy with a sloped standing-seam top, and the box's cantilever over the entrance is only weakly legible from above. | `r_gc_canopy.png`, `r_fc_south.png` vs `src_obl_glassbox.png`. | A simplified canopy primitive. | Deepen the canopy and give its top a shallow fall toward the fascia. Push the storefront line back so that the box overhang reads clearly. |
| F10 | P2 | front_corner, front | The canopy that wraps the SW corner is a shallow ledge on the south face. In the source it is a deep slab, with the ground-floor glazing well recessed beneath it. The west-front run (architecture_close) is deep and correct. | `r_fc_swcorner.png` vs `src_obl_swcorner.png`. | The south return was not given the same depth as the west run. | Give the south return the west run's depth. |
| F11 | P2 | facade_close, entrance_canopy, glass_close | The HALIFAX FERRY TERMINAL lettering is built from voxel blocks, so its strokes are stair-stepped at close range. It reads correctly, but crudely. | facade_close y≈480-600. | A bitmap-style glyph extrusion. | Use extruded outline glyphs. |
| F12 | P2 | top, aerial, rear_side | The heritage roof is closed over the rear lightwell between the two hipped roofs, which the source top shows as a dark notch. | `sources/top.jpg` x≈890-935, y≈350-490; top render: a continuous roof over the matching area. | Simplified roof union. | Cut a small open lightwell with a closed weathering edge. |
| F13 | P2 | aerial, rear_side, rear_north | East of the heritage block, the context neighbour is a large windowless prism in the same brick hue. It merges with the heritage block, so the complex reads bigger and blank. The source shows a windowed brick building there. | `r_ae_box.png`; rear_north x≈200-410. | Context block with no fenestration. | Add a punched-window rhythm and a slightly different brick or roof value. |
| F14 | P2 | front_corner, roof_mechanical | The harbour is present as a flat water plane, but the piers and the ferry described by the brief are not legible. | `r_fc_harbour.png`, `r_rm_harbour.png`. | Minimal background context. | Add 2-3 pier slabs and a simple ferry hull massing. |
| F15 | P2 | aerial | About a third of the frame is a featureless ground plane beyond the scene extent, and the south street context stops abruptly. | aerial y≈130-440. | Scene bounds are smaller than the camera cone. | Extend the street and blocks south, or tighten the frame. |
| F16 | P2 | all whole-envelope views | The concrete frames and walls are near-white. The source concrete and panels are a mid blue-grey, so the material hierarchy (concrete / aluminium / glass) is flatter than in the source. The top render also has a grey veil and is a little underexposed. | front, front_corner vs the sources. | The palette value is too high, and the top view's exposure was too low. | Darken the concrete one step toward the source grey, and lift the top-view exposure. |
| F17 | P2 | entrance_canopy, right_side, roof_boxes | Interiors are inconsistent. The storefront east of the doors opens onto an empty white box room (entrance_canopy x≈985-1195). One east-wall window shows an almost unlit room (right_side x≈640-720): it has a visible reveal, sill and mullion, so it is a dark room, not a void. The roof boxes carry a dark horizontal louvre strip that the source does not show. | As listed. | Placeholder interior and roof-box trim. | Furnish or light the storefront room. Balance the east-room light. Lighten or remove the roof-box strip. |

### Dark areas judged genuine (not defects)

- **Shaded areas.** The canopy soffits (entrance_canopy, architecture_close), the shaded rear brick faces between the heritage wings (rear_side), and the tree-pit and bench contact shadows all keep their hue and a soft gradient, at luminance of about 50-100.
- **Dark wedge in roof_boxes.** The wedge at x≈955-990, y≈815-860 is the underside of the interior stair, seen through the glass. The lit floor surrounds it, its edges are soft, and its luminance stays above 12 (`r_rb_wedge.png`).
- **Dark by design.** The dark aluminium mullions, the roof-box louvre strips, the dark-grey loading door and the cast-iron green shopfront piers are dark by design.
- **Top view.** There are no dark stripes between volumes. The ferry/brick junction strip (x≈745-790) has a minimum luminance of 92-139: pale flashing or paving, not an open gap. The joints at the roof boxes, the glass-box projection and the parking court are all pale.

## 3. Source conformance checklist

| item | mark | view used / note |
|---|---|---|
| Silhouette and storey count | conforms | front_corner, front, left_side: ferry 2 storeys, flat roof with roof boxes; brick block 3 storeys plus cornice, parapet and hipped roofs. The brick cornice sits slightly above the ferry cap, as in the oblique. |
| Plan (top: proportions, glass box, fins and roof boxes, brick block and roofs) | conforms (P2: lightwell, F12) | top vs top source. Roof ratio about 2.04 vs 2.10. Glass box projects at the south. The 3 roof boxes sit at 0.18-0.26 / 0.53-0.60 / 0.77-0.85 of the length, matching the source. Enclosure, AHU and the 3 skylights match within a few percent. Heritage block, wing, narrow range and parking court are all in place. |
| Glass box: end frames | conforms | glass_close, front_corner. |
| Glass box: three glazing tiers | conforms | glass_close. |
| Glass box: mullion grid | deviates (F3, P1) | glass_close: 8 bays vs 5. |
| Glass box: frosted band | conforms | glass_close, front_corner. |
| Glass box: projecting cap | conforms in form; deviates at the east end (F1a void) | front_corner. |
| Glass box: cantilever | weakly legible (F9, P2) | front_corner, glass_close. |
| Entrance canopy and lettering | conforms in presence and text; canopy simplified (F9, F11, P2) | entrance_canopy, facade_close. |
| Storefronts | conforms | entrance_canopy, glass_close: glazed, with benches behind. |
| Doors (two pairs of glass doors) | deviates (F4, P1) | entrance_canopy, interior. |
| Wrapping canopy on west bay and west front | conforms on the west run; south return shallow (F10, P2) | architecture_close, lawn_bench, front_corner. |
| West front bays and fins | conforms | left_side, architecture_close, roof_boxes: 3 full-height fins, glazed upper bays, glazed ground floor. |
| Roof boxes | conforms | roof_boxes, roof_mechanical, top: 3 white boxes cantilevering over the lawn strip on the fins. |
| Parapet bands and copings | conforms | roof_mechanical, aerial. |
| Roof: membrane panels | conforms | roof_mechanical, top. |
| Roof: gravel border | conforms (flat clay band) | roof_mechanical, top. |
| Roof: louvred enclosure and AHU | conforms | roof_mechanical, top: AHU with 3 fans. |
| Roof: skylights / hatches / vents | conforms | roof_mechanical: 3 skylights, 2 hatches, multiple vent stacks. |
| North wall | conforms | rear, rear_north: punched windows, service door, sectional loading door. |
| East wall | conforms in grammar; deviates at the base (F2, P1) | rear_side, right_side. |
| Brick block: cast-iron shopfronts | conforms | brick_neighbour, front. |
| Brick block: window types per floor | conforms on the street front | brick_neighbour: segment-headed 2nd floor, round-headed 3rd floor. |
| Brick block: hoods and keystones | conforms | brick_neighbour. |
| Brick block: pilasters, string courses | conforms | brick_neighbour. |
| Brick block: corbelled frieze, bracketed cornice | conforms | brick_neighbour, glass_close. |
| Brick block: parapet and corner finials | conforms | front, glass_close. |
| Brick block: pediment and oculus | conforms | brick_neighbour, front_corner. |
| Brick block: hipped tile roofs, chimneys | conforms (P2 lightwell, F12) | aerial, rear_side, top. |
| Brick block: rear and wing windows | deviates (F5, P1) | right_side, rear_side. |
| Hipped brick wing, narrow flat-roofed range, parking court | conforms | rear_side, top. |
| Streetscape: sidewalks, curbs | conforms | front, lawn_bench. |
| Streetscape: lawn strip and bench | conforms | lawn_bench, architecture_close. |
| Streetscape: tree pits and trees | conforms (low-poly clay) | top, front. |
| Streetscape: tactile strip | conforms | entrance_canopy, top. |
| Streetscape: crossings, lane markings | conforms | top, front_corner. |
| Context blocks across the west and north streets | conforms | front_corner, roof_mechanical. |
| East neighbour | deviates (F13, P2) | aerial. |
| Harbour with piers and ferry | partially (water only; F14, P2) | front_corner, roof_mechanical. |
| Glass reads as glass with interior depth | conforms except the doors (F4) | left_side, glass_close, facade_close, lawn_bench, roof_boxes, interior: furnished, lit interiors visible through the glass; the frosted band reads frosted. |
| No black slots | deviates (F1, F2, P1) | front_corner, aerial, entrance_canopy, facade_close, glass_close, right_side. The top view has no gap stripes. |
| Materials hierarchy | conforms (P2 value issue, F16) | Pale concrete, dark aluminium, clear glass, warm brick, terracotta tile and stone trim are all distinct. Concrete is lighter than in the source. |

## 4. Camera validity

| view | valid? | note |
|---|---|---|
| front | valid | Role-matched to the source front. Its west end is cropped, as in the source. The glass box and brick block are legible. A tree partly overlaps the box, as in the source (F8, P2). |
| front_corner | valid | Matches the source oblique role well. Whole south front, roof and brick front in frame. |
| aerial | valid | Whole ferry and heritage block in frame. Excess empty ground (F15, P2). |
| top | valid | True plan. Complete footprint plus neighbours. Slightly dim (F16). |
| left_side | **invalid** | Crops both ends of the west front (F6, P1). |
| right_side | **invalid** | Close corner shot; the east wall and wing leave the frame (F7, P1). |
| rear | valid | Full north elevation from grade to parapet, with margin. |
| rear_side | valid | Ferry north and east walls, heritage rear and court all legible. The foreground context prism and roof clip only the frame corners. |
| facade_close, glass_close, entrance_canopy, architecture_close, roof_boxes, roof_mechanical, interior, lawn_bench, rear_north | valid | Each target is legible and unobstructed. |
| brick_neighbour | valid | A street tree hides about a quarter of the shopfront level, but enough remains to judge the shopfronts. Upper floors, cornice and pediment are clear. |

## 5. Note on the inconsistent source front

The top and oblique sources agree on several points. The ferry has one roof height, with the glass box's cap level with the main parapet and the gravel running straight behind it. The box projects only modestly from the west bay. The box takes roughly 57-64 % of the 20 m south front. The model follows those two sources for the geometry and fits only the camera to the front view. That is the right priority, and it is a reasonable compromise. The cost is that the front render cannot reproduce the source front's taller, dominant box (F8, P2 only). None of the P1 findings comes from this compromise.
