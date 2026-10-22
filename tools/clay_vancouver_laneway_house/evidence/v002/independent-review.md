# Independent RLASM v6.1 holistic review: Vancouver laneway house, clay v002

Reviewer: independent holistic source-locked reviewer (not the builder).

I opened these at full resolution with the Read tool: `sources/front.png`, `sources/oblique.jpg`, `sources/top.jpg`, all 18 renders in `renders/`, and boards `phone-01` to `phone-04`. I judged pixels only and did not use the builder's notes or metadata as proof.

Zoomed evidence crops are in `review/crops_ramnyk/`. No other file was modified and nothing was rendered.

## 1. Verdict

Verdict: FAIL
Counts: P0=0 P1=1 P2=13

v002 fixes seven of the eight v001 P1s and leaves one landscape P1, a regression in the front-bed planting, so in the brief's terms it is VISUAL_REWORK_REQUIRED.

**What v002 fixes, confirmed from the pixels:**
- The side-entry head wedges, glazing-node squares and fin-plinth slot are gone.
- The side-entry door and its board lining now read in the matched front view.
- The garage roof now matches the top view.
- The right_side and top cameras are valid.

**What still blocks approval:** the fern fix crowded out the source's grasses. The beds in front of the glazed corner and the porch are now a uniform carpet of low fern rosettes. The tall feather-reed and ornamental grass mass that stands in front of the glazed bay in both the front and oblique sources is missing. The ferns are also about half the source height.

## 2. Findings

### How black geometry defects were told apart from genuine shadow

I ran a pixel scan over all 18 renders for connected regions with luma below 10 and below 22. Every hit was then inspected in a crop. None is a geometry void.

| region | where | why it is not a geometry defect |
|---|---|---|
| East side-yard shade | aerial x 785-845, y 692-791; right_side x 660-737, y 684-846; rear x 417-447, y 583-747 | A soft gradient from luma ~110 down to ~15. The board joints of the east wall and fence and the AC unit stay readable inside it. This is the same genuine shade v001 accepted (`aerial_east.png`, `right_side_base.png`, `rear_sideyard.png`). |
| Maple and leaf shadow | front x 1306-1391, y 818-856; garden x 787-985, y 410-575; facade_close x 1079-1098, y 947-979 | Dappled, following leaf outlines, inside the foliage mass. |
| Dark by design: black frames | the bay's east frame post (entry_steps x 401-412, architecture_close x 0-31), the side-door frame (side_entry x 489-598, west_wall x 677-716) | Black window and door frames, with luma 17-40 and a highlight edge. |
| Dark by design: other parts | car tyres and wheel arches (left_side x 168-394, y 900-917; rear x 1286-1371); neighbour window glass (facade_close x 1249-1279) | Tyres, wheel arches and dark window glass, as designed. |
| Small glass-edge darkening | architecture_close x 940-946, y 590-612 | Luma 34-40 against 78 around it, not 0, so it is not a void. Noted as P2 N5. |

The darkest pixel in glass_close is luma 4.8, in a 10 px foliage spot at the lower right. The glazing frames themselves sit at luma 40-55 with no zero-luma squares.

### Findings table

| id | severity | view(s) | finding | evidence (pixels) | likely cause | suggested fix |
|---|---|---|---|---|---|---|
| N1 | **P1** | front, front_corner, top, garden, entry_steps (against source front, oblique, top) | **Front-bed planting is a uniform low fern carpet, and the tall grass mass at the glazed corner is missing (a regression from v001).** See the detail rows below this table. | Crops: `front_beds.png` against `src_front_beds.png`; `fc_corner_bed.png` against `src_obl_corner_bed.png`; `top_front_beds.png` against `src_top_front_beds.png`. | The ferns are placed first in every bed and take all the slots in the two front beds, so the other species never get placed. The fern prototype is scaled to about half the height of a mature sword fern. | Reserve the back row of the bay-front bed for a feather-reed grass clump (about 1.2-1.5 m with plumes) along the bay plinth. Add a front layer of forest-grass mounds and blue fescue, as in the source oblique and top. Scale the sword ferns to 0.8-1.0 m with wider fronds, and limit them to about 40-50% of each front bed. Keep the west-bed fern masses but raise their density so the soil reads as mostly covered. |
| N2 | P2 | front_corner, front, west_wall | The side-entry door is now visible, but in front_corner it reads as a plain tan panel. The lintel hides its black head frame and no handle is visible. The mailbox is on the south return. The sources show it, with a wall light, on the north return near the door, where the south-west views see it. | `fc_sideentry_zoom.png` (plain panel at x 475-515, y 615-750) against `src_obl_sideentry.png`. Source front x 300-325, y 505-520: mailbox. | Door tone is the same as the cedar, and the mailbox was placed on the opposite return. | Give the door a slightly darker wood tone or visible stiles, and move the mailbox and lamp to the north return. |
| N3 | P2 | top (against source top) | The garage roof form now matches, but the garage is narrower than the source. Its eave spans about 0.68 of the main roof width (x 557-952 of 478-1050). In the source it spans about 0.80 even before correcting for perspective (x 450-805 of 385-890), so its true share is larger. | `top_garage.png` against `src_top_garage.png`. | Garage width was kept from v001. | Widen the garage about 1 m, toward the main eave width minus about 0.4 m each side, and re-centre the door. |
| N4 | P2 | top | The re-centred ortho now includes the whole garage, but crops the front sidewalk and the curb radius at the bottom edge. The front beds end at y about 1060. The source top shows the front sidewalk and the corner radius. | top, y 1060-1080. | The frame was shifted north to fit the garage. | Widen the scale slightly (about 22) so the garage, both sidewalks and the radius all fit. |
| N5 | P2 | architecture_close | At the two glass-railing panel joints, the panel edge refracts the sliding-door sill into a dark 6 × 20 px slit just above the base shoe. | x 940-946, y 590-612, luma 34-40; `arch_glass_joint.png`. | Glass-edge refraction. | Bevel or round the glass edge, or use a thin-glass shader for the railing. Close-up only. |
| N6 | P2 | right_side | The camera is valid now, but framing is tight: the west eave corner is about 12 px from the left edge. The role also largely duplicates aerial. | `right_side_leftedge.png`. | Camera field of view. | Pull back about 5% or nudge the target east. |
| F9 | P2 | front, glass_close, facade_close | Not addressed: a mid transom in every upper light and none in the lower lights. This does not match the source pattern. | `front_bay.png`. | Generic grid. | Match the per-light transom pattern from the source front. |
| F10 | P2 | facade_close, entry_steps | Not addressed: there is no transom over the porch door and sidelight, and the boards under the porch window are vertical where the source has a horizontal panel. | facade_close x 500-1040, y 630-900. | Simplification. | Add the transom and the horizontal panel. |
| F11r | P2 | architecture_close, facade_close | Bolt count is fixed (8 paired heads, matching the source). The heads are still square rather than round, and the fascia is still a lighter blue-grey than the source's darker steel. | facade_close x 425-1210, y 525-595. | Bolt and colour choice. | Use round heads and darken the fascia one step. |
| F13 | P2 | west_wall, side_entry, left_side | Not addressed: the side entry has a single step where the source shows 2-3 risers, and the horizontal-board panel is centred over the recess instead of offset. | west_wall x 668-850, y 880-930. | Simplification. | Add risers and offset the panel. |
| F14 | P2 | front | Not addressed: the large canopy trees behind the house in the source front are missing. | front x 0-80 only. | Context placement. | Add 1-2 large canopy trees to the north-west. |
| F15 | P2 | aerial, right_side, front_corner | Not addressed: the neighbour is a plain two-storey hip box. The source shows 2.5 storeys with front gables. | aerial x 810-1440. | Context simplification. | Add a half-storey and a gable. |
| F16 | P2 | interior | Not addressed: a near-camera wall fills x 0-540, with a dark vertical strip at x 225-275. | interior. | Camera placement. | Move the camera off the wall. |
| F17 | P2 | boards/phone-04 | Not addressed: the board still has the dimming overlay. | phone-04 against renders/rear.png. | Board compositing. | Regenerate without the overlay. |

**N1 detail: the bed in front of the glazed bay (source front and oblique)**

| source | what it shows |
|---|---|
| Source front, x 590-720, y 540-660 | A tall feather-reed and ornamental grass clump rising to about the lower third of the bay glazing. |
| Source oblique, x 680-780, y 740-850 | The same tall grasses. |
| Source oblique, x 600-700 and x 900-1000 | Forest-grass mounds and blue fescue in front of the grasses. |

| render | what it shows |
|---|---|
| front, x 560-1180, y 860-970 | Only fern rosettes. |
| front_corner, x 600-1080, y 860-1080 | Only fern rosettes, plus one tiny blue tuft. |
| top, x 460-690, y 885-1075 | Fern rosettes with two tiny fescue tufts. The source top shows a row of feathery grasses along the bay base and fescue mounds (x 380-555, y 680-830). |
| garden | Ferns, the maple and one shrub. The only grass is one fescue at x 170, y 740. There are no plumes. |

In v001 the "ornamental and feather reed grasses" item conformed in the front and garden views. In v002 the plumes survive only in the west side bed (left_side, west_wall).

**N1 detail: fern scale**

In entry_steps the stair risers are about 45 px each (about 0.18 m), and the foreground ferns are about 110 px tall, so about 0.45 m. The source oblique ferns beside the steps are about 0.8 m measured the same way against its risers. The source ferns are dense, overlapping masses. The render shows separate rosettes with soil between them: the east front bed in top is 15% visible soil and 51% green.

## 3. Source conformance checklist

| item | mark | view(s) used | note |
|---|---|---|---|
| Silhouette and roof: low hip | conforms | front, front_corner, left_side vs source front, oblique | |
| Short ridge front to back | conforms | top vs source top | Ridge is about 28% of roof depth (source about 29%). |
| Standing seams | conforms | top, roof_seams, front_corner | |
| Hip caps | conforms | front_corner, roof_seams | Narrowed. Still one step lighter, which is acceptable. |
| Thin dark fascia | conforms | roof_seams, front | |
| Skylight on west slope | conforms | top, front_corner, left_side | Position 0.19 / 0.37 of roof width and depth (source 0.16 / 0.36). |
| Plan: glazed bay at the front line | conforms | top, aerial, front | |
| Recessed porch at the front line | conforms | facade_close, aerial | |
| End fin | conforms | facade_close, right_side, aerial | The base slot is gone. |
| Rear garage | conforms (P2 width, N3) | top, rear, rear_side, left_side vs source top | Hip with a north slope and hip ends, ridge on the rear wall. |
| Storey heights | conforms | left_side, front | Two storeys. |
| Plinth | conforms | west_wall, entry_steps, right_side | Continuous at the fin junction. |
| Cedar cladding: vertical boards | conforms | all elevations | |
| Cedar tone variation | conforms | left_side, west_wall | |
| Cedar board joints | conforms | side_entry, west_wall | |
| Horizontal panel over side entry | conforms (P2 placement, F13) | west_wall, front | |
| Glazed corner: black frames | conforms | glass_close, facade_close, front | No node squares. |
| Glazed corner: two lights per face per storey | conforms | front, glass_close | |
| Glazed corner: spandrel | conforms | glass_close, front | |
| Glazed corner: transoms | deviates (P2, F9) | glass_close vs source front | |
| Balcony: steel fascia with bolts | conforms (P2 residual, F11r) | facade_close, architecture_close | 8 paired heads. |
| Balcony: glass railing | conforms | architecture_close, facade_close | |
| Balcony: cap rail | conforms | architecture_close | |
| Balcony: sliding wall behind | conforms | facade_close | Four lights. |
| Porch: front door | conforms | facade_close, entry_steps | |
| Porch: sidelight | conforms | facade_close | |
| Porch: two-light window | conforms (P2 panel, F10) | facade_close | |
| Porch: cedar ceiling | conforms | entry_steps | |
| Porch: landing and steps | conforms | entry_steps, front_corner | |
| Front cedar band under eave | conforms | facade_close, front | |
| Side street: tall narrow windows | conforms | west_wall, left_side, front | |
| Side street: lamp | conforms | west_wall, front | |
| Side street: recessed side entry | conforms (P2, N2) | front, front_corner vs sources; side_entry, west_wall | Shallower recess, horizontal-board lining on the returns, back wall and head. The door is visible in front. |
| Side street: side-entry steps | deviates (P2, F13) | west_wall | Single step. |
| Side street: small window over entry | conforms | west_wall | |
| Side street: small rear windows | conforms | west_wall, left_side | |
| Side street: downpipe | conforms | west_wall, front | |
| Garage: board door facing side street | conforms | garage, left_side, rear_side | |
| Garage: hip roof | conforms | top, rear, rear_side | |
| Garden beds: ferns | conforms in presence, deviates in scale and density (P1, N1) | front, front_corner, garden, west_wall, top | |
| Garden beds: ornamental and feather reed grasses | deviates (P1, N1) | front, front_corner, garden, top vs sources | Present only in the west side bed. Missing in front of the bay. |
| Garden beds: blue fescue | deviates (part of N1) | top, front_corner, garden | Only 2-3 tiny tufts. |
| Garden beds: red Japanese maple | conforms | front, garden, top | |
| Sidewalks on both streets | conforms | aerial, left_side, front | |
| Curb radius | conforms | aerial, front | Not in the top view (N4). |
| Walk to front steps | conforms | top, entry_steps, front_corner | |
| Two parked cars on side street | conforms | left_side, rear_side, rear | |
| Utility pole and wires | conforms | front, rear, rear_side, aerial | |
| Neighbour house | deviates (P2, F15) | aerial, right_side | |
| Board fence | conforms | aerial, right_side, rear | |
| Trees | deviates (P2, F14) | front | |
| Materials hierarchy | conforms | front, front_corner | Dark metal roof over a cedar body on a concrete plinth, with black glazing frames and grey steel accents. |

## 4. Camera validity

| view | status | note |
|---|---|---|
| front | valid | Whole house; role matches source front. |
| front_corner | valid | Whole house; role matches source oblique. |
| aerial | valid | |
| top | valid (P2 framing, N4) | House and the whole garage are in frame. The front sidewalk and curb radius are cropped. |
| left_side | valid | Full west elevation with the garage. |
| right_side | valid (P2 framing, N6) | High south-east oblique. The roof, front facade, fin and upper east wall are in frame. The lower east wall is hidden by the fence and neighbour, which is physically unavoidable in the 1.5 m yard and is an unseen teaching face. |
| rear | valid | |
| rear_side | valid | The pole crosses the north wall, but the garage roof and west wall stay legible. |
| facade_close | valid | |
| architecture_close | valid | |
| glass_close | valid | |
| entry_steps | valid | |
| side_entry | valid | |
| west_wall | valid | |
| roof_seams | valid | |
| garage | valid | |
| interior | valid (P2 composition, F16) | |
| garden | valid | |

## 5. Previous findings (v001: 0 P0 / 8 P1 / 10 P2)

| v001 id | sev | status in v002 | evidence |
|---|---|---|---|
| F1 side-entry head wedges | P1 | **fixed** | side_entry and west_wall: both head corners are closed cedar with no pixel below luma 10 in the recess (side_entry minimum 5.5 is on the black door frame). Crops `side_entry_head.png`, `west_wall_recess.png`. The recess floor edge is also clean (`side_entry_floor.png`). |
| F2 black squares at glazing nodes | P1 | **fixed** | glass_close, facade_close, front: every transom and mullion crossing is continuous dark grey (luma 40-55), with no zero-luma squares. Crops `glass_nodes.png`, `facade_bay_nodes.png`, `front_bay.png`. |
| F3 fin plinth slot | P1 | **fixed** | right_side and aerial: one continuous plinth at the fin base. Crops `right_side_base.png`, `aerial_east.png`. |
| F4 side-entry door hidden; flat lining | P1 | **fixed** (P2 residual N2) | front: the boarded north return plus the door panel with its black head are visible, in proportions close to the source front. front_corner: boarded return, recess floor and door panel. Crops `front_sideentry.png`, `fc_sideentry.png`. |
| F5 garage roof turned 90° | P1 | **fixed** | top: a north slope with north-south seams, and west and east hip ends with east-west seams, with hip lines converging toward the rear wall as in the source top (`top_garage.png` against `src_top_garage.png`). rear, rear_side and left_side agree. |
| F6 ferns missing, side bed bare | P1 | **partly fixed; residual P1 (N1)** | Sword ferns are now present in every bed and the side-street bed is planted. However, the front beds lost their grasses and the ferns are undersized (see N1). |
| F7 right_side too close | P1 | **fixed** | Whole roof and front facade in frame (P2 framing note N6). |
| F8 top cuts off the garage | P1 | **fixed** | The whole garage roof is in frame with grass beyond it (P2 N4 for the front sidewalk and curb). |
| F9 transom pattern | P2 | not fixed (not targeted) | |
| F10 porch transom and panel | P2 | not fixed (not targeted) | |
| F11 bolt grid, fascia | P2 | mostly fixed (8 pairs). Residual on head shape and colour (F11r). | |
| F12 wide, light hip caps | P2 | fixed | |
| F13 side-entry steps and panel | P2 | not fixed (not targeted) | |
| F14 backdrop trees | P2 | not fixed (not targeted) | |
| F15 neighbour half-storey | P2 | not fixed (not targeted) | |
| F16 interior camera | P2 | not fixed (not targeted) | |
| F17 board dimming | P2 | not fixed (not targeted) | |
| F18 garage over-depth | P2 | resolved | The garage now projects about 2.4-2.6 m beyond the main eave in top, consistent with the source top once perspective is allowed for. The width is now the open item (N3). |

**Regression check:**
- **Black geometry:** the dark-pixel scan and crops found no new slots, wedges or voids in any of the 18 views.
- **Unchanged items:** massing, roof, glazed corner, balcony, porch, front band, west-wall openings, plinth and street context all still conform.
- **One regression:** the "ornamental and feather reed grasses" item, which conformed in v001's front and garden views, now deviates in the front beds (N1).
