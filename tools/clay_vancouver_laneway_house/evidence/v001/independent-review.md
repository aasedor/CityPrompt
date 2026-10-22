# Independent RLASM v6.1 holistic review: Vancouver laneway house, clay v001

Reviewer: independent holistic source-locked reviewer (not the builder).
Inputs inspected at full resolution: `sources/front.png`, `sources/oblique.jpg`, `sources/top.jpg`; all 18 renders in `renders/`; boards `phone-01` to `phone-04`. Zoomed evidence crops are in `review/crops_qhvzkt/`. No other file was modified and nothing was rendered.

## 1. Verdict

Verdict: FAIL
Counts: P0=0 P1=8 P2=10

The building is the right building. Massing, the low hip roof with its short front-to-back ridge, the black glazed corner, the recessed balcony over the porch, the front cedar band, the plinth and the street context all read correctly. It still cannot be approved. There are three separate black geometry slots or wedges, the side entry's door is hidden in both matched views, the garage roof is turned 90 degrees against the top view, the fern planting is missing, and two whole-envelope cameras clip the asset. In the brief's terms the verdict is VISUAL_REWORK_REQUIRED.

## 2. Findings

How black geometry defects were told apart from genuine shadow: every P1 black mark below has luma 0 and a hard-edged rectangular or sliver shape, with no gradient. Each one sits beside lit surfaces with luma 55 to 130 and keeps the same shape when seen from other angles. Genuine shade in these renders looks different:
- **Maple leaf shadow** (front, garden, facade_close) is dappled and follows the leaf outlines, with luma around 20 to 60.
- **East side-yard shade** (right_side, aerial, rear) is a soft gradient, and the fence boards and ground stay readable inside it.
- **Plinth contact shadow** is a soft darkening along the ground line, never a void.

| id | severity | view(s) | finding | evidence (pixels) | likely cause | suggested fix |
|---|---|---|---|---|---|---|
| F1 | P1 | side_entry, west_wall | **Black wedges at the side entry's head corners.** Both top corners of the recess opening show pure black slots where the cedar jamb returns stop short of the head and panel. | side_entry: black bars at x 429-457, y 118-123 and x 862-891, y 110-115 (luma 0 next to cedar at 130). west_wall: the same at x 662-669, y 544-545. Crops: `crops_qhvzkt/side_entry_head.png`, `west_wall_recess.png`. | The jamb lining boards end below the head lining, or the head lining is narrower than the opening, leaving the unlit wall cavity visible. | Extend both jamb linings to the head soffit and make the head lining span the full opening width, so the corners close. Add a 10-20 mm overlap rather than butting. |
| F2 | P1 | glass_close, facade_close, front | **Black squares at every node of the glazed corner frame.** Wherever a transom crosses a mullion or the corner post, a black square appears. | glass_close: x 503-519, y 209-229; x 806-827, y 236-254; x 985-1001, y 272-287. facade_close: x 149-166, y 341-352 and x 374-385, y 330-359. front: x 643-654, y 392-401. All are luma 0 inside frames with luma 55-67. Crop: `crops_qhvzkt/facade_bay_nodes.png`, `glass_transoms.png`. | Frame members overlap with coincident or inverted faces at the crossings (or a node block has flipped normals), so the crossing renders as a void. | Build the transoms as split members that butt into the mullions, or union them into one frame mesh. Recalculate normals outward and delete interior coincident faces. |
| F3 | P1 | right_side, aerial | **Black vertical slot at the base of the east end fin.** A thin void opens between the fin's plinth return and the east wall plinth. | right_side: x 585-588, y 992-1048 (luma 0; the plinth on both sides is luma ~80-110). aerial: x 759-760, y 839-853. Crops: `crops_qhvzkt/right_side_slot.png`, `right_side_base.png`, `aerial_east.png`. | The fin's plinth block and the east wall plinth do not meet. One is set back from the other, leaving an open gap down to the ground. | Extend the east wall plinth to butt into the fin plinth, or wrap one continuous plinth around the fin's return. Check every plinth junction for the same gap. |
| F4 | P1 | front, front_corner (against source front and oblique) | **Side entry door not visible in either matched view, and the recess lining is wrong.** Both sources show the wood door at the back of the cedar-lined recess, with horizontal-board lining on the visible return wall. The renders show only a flat, untextured cedar return wall and no door. The recess is too deep for its width. | Source front: recess 262-325 px, with the door showing at x 300-325. Source oblique: door and mailbox at about x 385-405, y 480-560, with the return wall in horizontal boards. Render front: recess x 400-470, y 590-840 is one flat tan plane. Render front_corner: x 445-515 is the same. Crops: `src_front_garage_sideentry.png`, `src_obl_garage.png`, `front_sideentry.png`, `fc_sideentry.png`. The door does exist: it appears in left_side and side_entry. | Recess depth is too large relative to its width, and the return lining is a plain slab instead of the horizontal-board lining. | Reduce the recess depth to about 0.6-0.8 of the opening width, so about 40% of the door shows from the south-west camera as in the source. Clad both returns and the head in horizontal cedar boards with visible joints. |
| F5 | P1 | top, rear, rear_side (against source top) | **Garage roof turned 90 degrees.** The top view governs the plan. It shows the garage hip roof with its ridge running east-west, parallel to the main rear wall: a north slope with north-south seams, plus hip ends at the west and east. The render instead runs the ridge north-south, perpendicular to the rear wall, with east and west slopes carrying east-west seams and a hip only at the north end. | Source top: garage trapezoid x 450-805, y 80-140, hip lines from the north corners toward the centre, seams vertical in the image (`crops_qhvzkt/src_top_garage.png`). Render top: a centre ridge at x 755 with horizontal seams on both sides (`crops_qhvzkt/top_rear.png`). Render rear: a north hip triangle with its apex on the main wall. | Garage roof built with its ridge axis rotated. | Rebuild the garage roof as a hip with the ridge parallel to the main house's rear wall: north slope plus two hipped ends, with seams running down each slope. Keep the board door on the west face. |
| F6 | P1 | front, front_corner, garden, top, left_side | **Sword-fern masses missing and the side-street bed too sparse.** In both sources, large arching sword ferns are the dominant planting: along the west wall, in front of the glazed bay and in the east front bed. The render fills every bed with upright strap-leaf grass tufts, plus one round leafy shrub. The bed along the side-street wall is mostly bare soil with a few small tufts. | Source front: fern masses at x 265-430, y 560-620 and x 790-880, y 555-630. Source oblique: ferns at x 360-500, y 640-780 and x 830-960, y 650-760. Render front: west bed x 200-560, y 830-880 is bare brown soil with sparse tufts (`crops_qhvzkt/front_west_bed.png`). Garden view: all plants are strap-leaf clumps. | The planting library has no fern form, and the side bed has a low scatter density. | Add a clay sword-fern form: a mound of arching pinnate fronds 0.6-0.9 m high. Mass it where the sources show it (west wall bed, front of bay, east front bed). Raise side-bed coverage so the soil reads as mostly covered, as in the source. |
| F7 | P1 | right_side | **Camera: a whole-envelope view clips the asset.** "right_side" is listed as a whole-envelope view, but its camera sits in the east side yard. The roof is cut off at the top, the front facade at the left, and most of the east elevation is hidden behind the fence and neighbour. The east envelope cannot be judged as a whole from it. | Roof cut at the top edge, x 0-800. Front balcony cut at x 0. East wall visible only from x 530 to 800 and foreshortened. | Camera too close and too low for the narrow side yard. | Raise and pull back the camera (for example a high oblique from the south-east, above the fence) so the whole east elevation, roof edge and fin fit in frame. |
| F8 | P1 | top | **Camera: the plan view clips the rear garage.** The top frame cuts off the garage's north half and its north hip at y=0. The governing plan comparison of the garage (see F5) cannot be completed from this view. | Garage roof x 548-968 runs off the top edge. The source top shows the whole garage, the car beyond it and the grass. | Ortho framing centred on the main house only. | Re-centre or widen the top camera so the full lot fits: garage, both sidewalks and the curb radius. |
| F9 | P2 | front, glass_close, facade_close | Glazed-corner subdivision differs from the source. The render puts a mid-height transom in every upper light and none in the lower lights. The source's upper front-left light is undivided, and its lower west lights have low transoms. | Source crop `src_bay_balcony.png` against render `front_bay_porch.png`. | Generic grid. | Match the per-light transom pattern from the source front. |
| F10 | P2 | facade_close, entry_steps, front | The porch is missing the glazed transom over the front door and sidelight. The two-light window has vertical boards below it, where the source has a horizontal cedar panel. | Source crop `src_bay_balcony.png`: transom at y 415-455, horizontal panel under the window. | Simplification. | Add the transom light and the horizontal-board panel. |
| F11 | P2 | architecture_close, facade_close, right_side | The balcony fascia carries a dense two-row grid of square bolt heads, which reads as a perforated plate. The source has paired round standoff bolts at the glass panel joints. The fascia is also lighter blue-grey than the source's darker steel, and the glass sits on top of the fascia instead of being face-fixed in front of it. | Render: about 15 columns × 2 rows of squares. Source: about 8 pairs of round heads. | Bolt array spacing too tight. | Use about 8 pairs of round heads at the panel joints, darken the steel, and hang the glass in front of the fascia face. |
| F12 | P2 | front_corner, aerial, roof_seams | The hip caps are wide and much lighter than the roof sheets, so they read as bold bands. The source caps are thin and close in tone to the roof. | front_corner: the hip from (720,550) to (780,140). | Cap width and material. | Narrow the caps and use a tone one step lighter than the roof at most. |
| F13 | P2 | west_wall, left_side, front | The side entry has a single low step. The source shows 2-3 concrete steps down to the sidewalk. The horizontal-board panel is centred over the recess, where the source offsets it and also runs it down one side of the recess. | Source front crop: steps at x 305-395, y 800-880. | Simplification. | Add 2 more risers and offset the panel. |
| F14 | P2 | front | The large deciduous trees that frame the source front behind the house appear only as a small blob at the left edge. | Source front x 0-450, y 110-520 against render front x 0-80. | Context placement. | Place one or two large canopy trees north-west of the house so they rise above the roof in the front view. |
| F15 | P2 | aerial, right_side, rear | The neighbour reads as a plain two-storey box with a hip roof. The source neighbour reads as 2.5 storeys, with a front gable or dormer and a shingle roof. | Source oblique x 900-1190, y 140-500. | Context simplification. | Add a front gable or dormer and a half-storey of height. |
| F16 | P2 | interior | A near-camera wall takes up the left third of the frame, with an unexplained dark vertical strip at x 225-275. It is legible, but the composition is weak. | `crops_qhvzkt/interior_left.png`. | Camera placement. | Move the camera off the wall. |
| F17 | P2 | boards/phone-04 | The board is rendered with a dark dimming overlay, so the rear, rear_side and top tiles show lower contrast than the source renders. | phone-04 against renders/rear.png. | Board compositing. | Regenerate the board without the overlay. |
| F18 | P2 | left_side, rear | The garage measures about 5.4 m deep in left_side (wall x 145-550 against the house's 555-1165). The source top suggests a shallower garage, though perspective makes this uncertain. | Source top: north eave at y 80 against the main roof at 145. | Possible over-depth. | Re-check against the source top once F8 is fixed. |

Top view, checked for dark stripes from open gaps between volumes: none found.
- **Garage roof to main roof:** they meet the main north eave at y=150 with fascia luma 56-63, with no void.
- **East eave:** a narrow dark line at x 1072-1078 runs along the east eave. It is the shaded side-yard ground strip between the eave edge and the fence top. The board fence is at x 1080-1085 and the shaded ground with the AC unit at x 1086-1115. The source top shows the same dark side yard at x 860-890, so this is genuine shade, not a gap (`crops_qhvzkt/top_east.png`).

## 3. Source conformance checklist

| item | mark | view(s) used | note |
|---|---|---|---|
| Silhouette and roof: low hip | conforms | front, front_corner, left_side vs source front, oblique | Low pitch and dark sheet tone match. |
| Short ridge front to back | conforms | top vs source top | Ridge is about 28% of roof depth in the render, about 29% in the source. |
| Standing seams | conforms | top, roof_seams | Seams run down each slope as in the source. |
| Hip caps | deviates (P2) | front_corner, roof_seams | Too wide and too light (F12). |
| Thin dark fascia | conforms | roof_seams, front | |
| Skylight on west slope | conforms | top, front_corner, left_side vs source top, oblique | Position within about 7% of the source. |
| Plan: glazed bay at the front line | conforms | top, aerial, front | |
| Recessed porch at the front line | conforms | facade_close, aerial | |
| End fin | conforms | facade_close, front, right_side | Base slot defect (F3). |
| Rear garage | deviates (P1) | top, rear, rear_side vs source top | Roof rotated (F5); top view clipped (F8). |
| Storey heights | conforms | left_side, front | Two storeys. |
| Plinth | conforms (with defect) | west_wall, entry_steps | Exposed concrete; slot at the fin (F3). |
| Cedar cladding: vertical boards | conforms | all elevations | |
| Cedar tone variation | conforms | left_side, west_wall | |
| Cedar board joints | conforms | side_entry, west_wall | |
| Horizontal panel over side entry | conforms (P2 placement) | west_wall, front_corner | Placement differs (F13). |
| Glazed corner: black frames | conforms (with defect) | glass_close | Black node squares (F2). |
| Glazed corner: two lights per face per storey | conforms | front, glass_close | |
| Glazed corner: spandrel | conforms | glass_close, front | |
| Glazed corner: transoms | deviates (P2) | glass_close vs source front | Pattern differs (F9). |
| Balcony: steel fascia with bolts | deviates (P2) | architecture_close | Bolt grid and colour (F11). |
| Balcony: glass railing | conforms | architecture_close, facade_close | Frameless panels. |
| Balcony: cap rail | conforms | architecture_close | |
| Balcony: sliding wall behind | conforms | facade_close | Four lights. |
| Porch: front door | conforms | facade_close, entry_steps | |
| Porch: sidelight | conforms | facade_close | |
| Porch: two-light window | conforms (P2 panel) | facade_close | F10. |
| Porch: cedar ceiling | conforms | entry_steps | Flat cedar tone with a cove light. |
| Porch: landing and steps | conforms | entry_steps, front_corner | |
| Front cedar band under eave | conforms | facade_close, front | |
| Side street: tall narrow windows | conforms | west_wall, left_side | |
| Side street: lamp | conforms | west_wall, front | |
| Side street: recessed side entry and steps | deviates (P1) | front, front_corner vs sources; side_entry | Door hidden and lining flat (F4); geometry wedges (F1); single step (F13). |
| Side street: small window over entry | conforms | west_wall | |
| Side street: small rear windows | conforms | west_wall | |
| Side street: downpipe | conforms | west_wall, front | |
| Garage: board door facing side street | conforms | garage, left_side | |
| Garage: hip roof | deviates (P1) | top, rear | Hipped, but the ridge axis is rotated (F5). |
| Garden beds: ferns | deviates (P1) | front, garden, front_corner | F6. |
| Garden beds: ornamental and feather reed grasses | conforms | front, garden | Plumes present. |
| Garden beds: blue fescue | conforms | top, front_corner | Blue-grey tufts present. |
| Garden beds: red Japanese maple | conforms | front, garden, top | |
| Sidewalks on both streets | conforms | top, aerial, left_side | |
| Curb radius | conforms | top, aerial, front | |
| Walk to front steps | conforms | top, entry_steps | |
| Two parked cars on side street | conforms | left_side, rear, rear_side | |
| Utility pole and wires | conforms | front, rear, rear_side, aerial | |
| Neighbour house | deviates (P2) | aerial, right_side | Simplified (F15). |
| Board fence | conforms | aerial, rear, right_side | |
| Trees | deviates (P2) | front | Large backdrop trees missing (F14). |
| Materials hierarchy | conforms | front, front_corner | Dark metal roof over cedar body over concrete plinth, with black glazing frames and grey steel accents, as in the sources. |

## 4. Camera validity

| view | status | note |
|---|---|---|
| front | valid | Whole house in frame; role matches source front. |
| front_corner | valid | Whole house; role matches source oblique. |
| aerial | valid | Whole house from the south-east; roof, porch and fence legible. |
| top | **invalid in part (P1, F8)** | House fully in frame, but the rear garage is clipped at the top edge, so the plan comparison is incomplete. |
| left_side | valid | Full west elevation with garage. |
| right_side | **invalid (P1, F7)** | A whole-envelope view that clips the roof and front facade, and shows only a sliver of the east elevation. |
| rear | valid | Garage and rear wall legible. |
| rear_side | valid | The pole crosses part of the west wall, but the target stays legible. |
| facade_close | valid | |
| architecture_close | valid | Fascia, railing and sliding wall legible. |
| glass_close | valid | |
| entry_steps | valid | |
| side_entry | valid | |
| west_wall | valid | |
| roof_seams | valid | |
| garage | valid | Door and wall legible; roof form not shown, so it is covered by rear and rear_side. |
| interior | valid (P2 composition, F16) | |
| garden | valid | |
