# Independent RLASM v6.1 holistic review: Vancouver laneway house, clay v003

Reviewer: independent holistic source-locked reviewer (not the builder).

I opened these at full resolution with the Read tool: `sources/front.png`, `sources/oblique.jpg`, `sources/top.jpg`, all 18 renders in `renders/`, and boards `phone-01` to `phone-04`. For comparison I also opened the v002 renders `front`, `front_corner`, `left_side`, `west_wall`, `garden` and `entry_steps` from `tools/clay_vancouver_laneway_house/evidence/v002/renders/`. I judged pixels only and did not use the builder's notes or metadata as proof.

Zoomed evidence crops are in `review/crops_ybrifw/`. No other file was modified and nothing was rendered.

## 1. Verdict

Verdict: FAIL
Counts: P0=0 P1=2 P2=15

In the brief's terms this is VISUAL_REWORK_REQUIRED. v003 restores the tall grass mass in front of the glazed bay and scales up the ferns, but in doing so it removes the dense sword-fern hedge along the side-street wall, the most prominent planting in both the source oblique and the source front. The enlarged fern prototype also now reads as bare thorny canes, not leafy sword fern.

**What v003 fixes, confirmed from the pixels:**
- **Grass mass at the glazed bay:** tall feather-reed clumps with plumes now stand in front of the bay plinth. They rise to roughly the lower third of the lower glazing, as in the sources. Evidence: front x 590-830 (plumes to about y 750, lower glazing y 545-865); front_corner x 560-660 (`fc_bayfront_bed.png`); entry_steps x 0-110.
- **Fescue:** blue fescue is now visible in quantity in front, front_corner, top and garden.
- **Bed cover:** both front beds read as covered in top (`top_front_beds.png`).

**Building and camera geometry are unchanged from v002.** A per-pixel difference against the v002 renders (mean channel difference above 40) is confined to the planting beds in every view. architecture_close shows zero changed pixels. Every v001 geometry fix therefore still holds, which I also checked directly in crops.

**What still blocks approval:**
- **N7, west-wall ferns lost:** the fern hedge along the west wall is gone.
- **N8, fern form wrong:** the new fern form is wrong at review scale.

## 2. Findings

### How black geometry defects were told apart from genuine shadow

I scanned all 18 renders for connected regions with luma below 10 and at least 20 px in size. I inspected each region in a crop. None is a geometry void, and no new dark region appears relative to v002.

| region | where | why it is not a geometry defect |
|---|---|---|
| East side-yard shade | aerial x 816-842, y 720-763; right_side x 696-737, y 716-803; rear x 425-447, y 590-729 | Soft gradient. The fence and east-wall board joints stay readable. This is the same shade v001 and v002 accepted. |
| East-wall upper window under the eave | aerial x 973-976, y 448-458; right_side x 855-858, y 380-393 (`aerial_dark_973_448.png`, `right_side_dark_855_380.png`) | A rectangular window with a lit pane next to a black frame jamb in eave shade. The region sits inside a framed opening, not at a joint between volumes, and it is unchanged from v002. |
| Dark by design: black frames | facade_close x 383-385 (vertical, bay frame edge); entry_steps x 401-412, y 0-770; architecture_close x 0-31; garden x 0-11, y 44-170 | Black window and bay frames, as designed. Each is a thin, straight member with a lit edge beside it. |
| Neighbour window glass | facade_close x 1249-1279, y 662-769; rear x 399-404, y 563-573 (`rear_dark_399_563.png`); garden x 1227-1259, y 18-37 | Dark glass inside a white trim frame. |
| Maple leaf shadow | front x 1288-1381, y 781-842; garden (inside the maple) | Dappled shadow inside the foliage mass that follows the leaf outlines. |
| Tyres and cars | front x 0-17, y 850-868; left_side x 171-200, y 900-911; rear x 1305-1439, y 892-1031 | Tyres, wheel arches and dark car bodies. |

glass_close has a minimum luma of 8.3 and no region below 10, and its frame nodes are continuous (`glass_nodes.png`). side_entry has a minimum luma of 11.4, west_wall 12.8 and roof_seams 20.0, with no voids.

### Findings table

| id | severity | view(s) | finding | evidence (pixels) | likely cause | suggested fix |
|---|---|---|---|---|---|---|
| N7 | **P1** | front_corner, front, west_wall, left_side (against source oblique and front) | **The sword-fern hedge along the side-street wall is missing (a regression from v002).** See the N7 detail below this table. | Crops: `fc_west_beds.png` against `src_obl_west_beds.png`; `front_beds.png` against `src_front_beds.png`; `west_wall_beds.png` against `v002_west_wall_beds.png`. | The fern cap of "40-50% per front bed" and the "sparser fern pass in the bay-front bed" were applied to the whole L-shaped bed, including its west leg along the side-street wall. The ferns' slots there went to grass and fescue. | Treat the west leg of the bay bed (side steps to bay corner) as its own bed: plant it as a continuous row of the 0.8-1.0 m sword ferns at about 0.6 m spacing, touching each other, with no grass. North of the side steps, plant a dense back row of feather reed and a front row of chartreuse forest-grass mounds at 0.3 m spacing, or extend the dark ground cover so soil does not show. Keep the bay-front grass mass and fescue as they are. |
| N8 | **P1** | entry_steps, garden, front, front_corner, garage (against source front and oblique) | **The enlarged sword-fern prototype reads as bare thorny canes or bramble, not as leafy sword fern.** See the N8 detail below this table. | Crops: `entry_ferns_right.png`; `front_east_bed.png` against `src_front_east_bed.png`; compare v002 entry_steps x 1000-1440, y 800-1080. | The frond was lengthened to 1.32 m and given an upright stretch while the pinna count and size stayed the same. The pinnae are therefore spaced out and look tiny relative to the rachis. | Scale the pinnae with the frond, to about 8-10 cm long and 1.5-2 cm wide at mid-frond. Increase the pinna count to about 35-45 per side so they overlap. Apply the upright stretch only to the rachis curve, not as a non-uniform object scale. A fern should read as a solid dark-green fountain of strap-like blades at front and garden scale. |
| N9 | P2 | garden, entry_steps, front, front_corner, west_wall | The new "ground cover" is a flat, untextured, saturated green plane that reads as turf or felt, not as a low leafy carpet over dark mulch. | garden: the bed floor at y 600-830 is one flat green. entry_steps: x 0-380 and x 900-1440, y 850-1080. | A plain plane with a green material. | Darken it toward the source's dark mulch-green, and break it with a scatter of small leaf instances, or with a noise in tone, so it reads as planting. |
| N10 | P2 | top, front_corner, garden (against source top) | The red Japanese maple is undersized relative to the source. In the source top, the maple and its companion shrubs fill about 40% of the east front bed (x 770-910 of 650-1000). In the render top the maple covers about 25% (x 935-1030 of 810-1050). | `top_front_beds.png` against `src_top_front_beds.png`. | Maple scale kept from v001. | Scale the maple about 1.3× in plan and add one dark shrub mass east of it. |
| N2 | P2 | front_corner, front, side_entry | Carried from v002, unchanged. The side-entry door reads as a plain panel in front_corner. The mailbox or intercom is on the south return; the sources show it on the north return. | side_entry x 838-858, y 440-515. | Unchanged. | As in v002. |
| N3 | P2 | top | Carried from v002, unchanged. The garage is narrower than in the source top. | top: garage x 557-952 against main roof x 478-1050. | Unchanged. | Widen it about 1 m. |
| N4 | P2 | top | Carried from v002, unchanged. The front sidewalk and curb radius are cropped at the bottom edge. | top y 1065-1080. | Unchanged. | Widen the ortho scale slightly. |
| N5 | P2 | architecture_close | Carried from v002, unchanged. A dark slit at the glass-railing panel joints. | x 940-946, y 590-612. | Glass-edge refraction. | As in v002. |
| N6 | P2 | right_side | Carried from v002, unchanged. Tight framing at the west eave. | Left edge. | Camera. | Pull back about 5%. |
| F9 | P2 | front, glass_close, facade_close | Carried, unchanged. The transom pattern differs from the source. | `glass_nodes.png`. | Generic grid. | Match the source per-light pattern. |
| F10 | P2 | facade_close, entry_steps | Carried, unchanged. No porch transom; vertical boards where the source has a horizontal panel under the window. | facade_close x 500-1040, y 630-900. | Simplification. | As before. |
| F11r | P2 | facade_close, architecture_close | Carried, unchanged. Square bolt heads; the fascia is a lighter grey than the source. | facade_close x 425-1210, y 525-595. | As before. | As before. |
| F13 | P2 | west_wall, side_entry | Carried, unchanged. The side entry has a single step, and its horizontal panel is centred. | west_wall x 668-850, y 880-930. | As before. | As before. |
| F14 | P2 | front | Carried, unchanged. The large backdrop trees are missing. | front x 0-80. | As before. | As before. |
| F15 | P2 | aerial, right_side | Carried, unchanged. The neighbour has no half-storey and no gable. | aerial x 810-1440. | As before. | As before. |
| F16 | P2 | interior | Carried, unchanged. A near-camera wall fills x 0-540, with a dark strip at x 225-275. | interior. | As before. | As before. |
| F17 | P2 | boards/phone-04 | Carried, unchanged. The dimming overlay is still on the tiles. | phone-04 against renders/rear.png. | As before. | As before. |

**N7 detail: the west-wall beds against the sources**

| source or render | what it shows |
|---|---|
| Source oblique, x 320-600, y 640-800 | A continuous, dense hedge of large, dark, arching sword ferns runs the full length of the west wall, from the side-entry steps to the bay corner. The ferns stand about sill-high (0.8-1.0 m). |
| Source oblique, x 230-350, y 470-620 | North of the side steps: tall golden feather reed and dense chartreuse forest-grass mounds. |
| Source front, x 265-430, y 555-625 | The same fern mass is the darkest, largest planting element in the frame. |
| v003 front_corner, x 490-760, y 830-1000 | The same strip holds only a sparse scatter of low fescue and forest-grass tufts on a flat green plane. There is no fern. |
| v003 front_corner, x 300-440, y 660-780 | The bed north of the side steps is a thin row of small tufts with about half its area bare brown soil. |
| v003 front, x 400-600, y 820-880 | Thin tufts, no fern mass. |
| v003 west_wall, x 860-1300, y 860-935 | Grass tufts on flat green. |
| v003 left_side, x 545-785 and x 890-1360, y 720-770 | Grass tufts on flat green. |
| v002 west_wall | Both west beds held fern rosettes. They were undersized, but they were ferns. |

In v003, the ferns survive only in the east front bed. The brief's statement that ferns "still mass in the side-street beds" is not borne out by the pixels. The loss is plainly visible on phone-01, where the source oblique's dark fern band has no counterpart in the front_corner tile.

**N8 detail: what the fern form looks like**

| view | what it shows |
|---|---|
| entry_steps, x 1030-1440, y 700-1080 | Each frond is a long, thin green stem with small triangular spikes about 8-10 px long, spaced about 20-30 px apart. The spikes do not overlap. They read as a bramble or barbed cane. |
| garden, x 330-1000, y 400-560 | The same long arching canes rise above the bed. |
| garage, x 60-360, y 700-880 | The same canes. |
| Source front, x 790-880, y 555-630 (`src_front_east_bed.png`) | Broad, overlapping, glossy pinnae that form solid leafy fronds. |
| v002 (same prototype at smaller scale) | The pinnae were dense enough to read as fern. |
| v003 front (`front_east_bed.png`) and front_corner, at whole-view scale | The ferns dissolve into a wispy, pale-green haze. They no longer give the dark, solid fern masses that frame the steps in the source front. |

## 3. Source conformance checklist

| item | mark | view(s) used | note |
|---|---|---|---|
| Silhouette and roof: low hip | conforms | front, front_corner, left_side vs source front, oblique | Unchanged from v002. |
| Short ridge front to back | conforms | top vs source top | |
| Standing seams | conforms | top, roof_seams, front_corner | |
| Hip caps | conforms | front_corner, roof_seams | |
| Thin dark fascia | conforms | roof_seams, front | |
| Skylight on west slope | conforms | top, front_corner, left_side | |
| Plan: glazed bay at the front line | conforms | top, aerial, front | |
| Recessed porch at the front line | conforms | facade_close, aerial | |
| End fin | conforms | facade_close, right_side, aerial | Continuous plinth at the fin base (`right_side_fin_base.png`). |
| Rear garage | conforms (P2 width, N3) | top, rear, rear_side, left_side | |
| Storey heights | conforms | left_side, front | Two storeys. |
| Plinth | conforms | west_wall, entry_steps, right_side | |
| Cedar cladding: vertical boards | conforms | all elevations | |
| Cedar tone variation | conforms | left_side, west_wall | |
| Cedar board joints | conforms | side_entry, west_wall | |
| Horizontal panel over side entry | conforms (P2 placement, F13) | west_wall, front | |
| Glazed corner: black frames | conforms | glass_close, facade_close, front | No node voids. |
| Glazed corner: two lights per face per storey | conforms | front, glass_close | |
| Glazed corner: spandrel | conforms | glass_close, front | |
| Glazed corner: transoms | deviates (P2, F9) | glass_close vs source front | |
| Balcony: steel fascia with bolts | conforms (P2, F11r) | facade_close, architecture_close | 8 paired heads. |
| Balcony: glass railing | conforms | architecture_close, facade_close | |
| Balcony: cap rail | conforms | architecture_close | |
| Balcony: sliding wall behind | conforms | facade_close | Four lights. |
| Porch: front door | conforms | facade_close, entry_steps | |
| Porch: sidelight | conforms | facade_close, entry_steps | |
| Porch: two-light window | conforms (P2, F10) | facade_close | |
| Porch: cedar ceiling | conforms | entry_steps | |
| Porch: landing and steps | conforms | entry_steps, front_corner | |
| Front cedar band under eave | conforms | facade_close, front | |
| Side street: tall narrow windows | conforms | west_wall, left_side, front | |
| Side street: lamp | conforms | west_wall, front | |
| Side street: recessed side entry | conforms (P2, N2) | front (`front_sideentry.png`), front_corner, side_entry | Door visible at the back of the boarded recess. Head corners closed. |
| Side street: side-entry steps | deviates (P2, F13) | west_wall | Single step. |
| Side street: small window over entry | conforms | west_wall | |
| Side street: small rear windows | conforms | west_wall, left_side | |
| Side street: downpipe | conforms | west_wall, front | |
| Garage: board door facing side street | conforms | garage, left_side, rear_side | |
| Garage: hip roof | conforms | top, rear, rear_side | |
| Garden beds: ferns | **deviates (P1, N7 and N8)** | front_corner, front, west_wall, entry_steps, garden vs source oblique, front | Height is now about right in the east bed. Missing from the whole west-wall strip, and the frond form reads as bare canes. |
| Garden beds: ornamental and feather reed grasses | conforms | front, front_corner, entry_steps, glass_close, top | The tall plume mass is restored at the bay. The north-of-side-steps bed is too sparse (part of N7). |
| Garden beds: blue fescue | conforms | top, front_corner, front, garden | |
| Garden beds: red Japanese maple | conforms (P2 size, N10) | front, garden, top | |
| Sidewalks on both streets | conforms | aerial, left_side, front | |
| Curb radius | conforms | aerial, front | Cropped in top (N4). |
| Walk to front steps | conforms | top, entry_steps, front_corner | |
| Two parked cars on side street | conforms | left_side, rear_side, rear | |
| Utility pole and wires | conforms | front, rear, rear_side, aerial | |
| Neighbour house | deviates (P2, F15) | aerial, right_side | |
| Board fence | conforms | aerial, right_side, rear | |
| Trees | deviates (P2, F14) | front | |
| Materials hierarchy | conforms | front, front_corner | Dark metal roof, cedar body, concrete plinth, black frames, grey steel. The bed floor is a flat bright green (N9). |

## 4. Camera validity

Camera positions are unchanged from v002: the pixel difference is confined to the planting.

| view | status | note |
|---|---|---|
| front | valid | Whole house; role matches source front. |
| front_corner | valid | Whole house; role matches source oblique. |
| aerial | valid | |
| top | valid (P2 framing, N4) | House and garage in frame. Front sidewalk and curb radius cropped. |
| left_side | valid | |
| right_side | valid (P2 framing, N6) | |
| rear | valid | |
| rear_side | valid | The pole crosses the north wall; the target stays legible. |
| facade_close | valid | |
| architecture_close | valid | |
| glass_close | valid | Plumes in the foreground do not hide the frame. |
| entry_steps | valid | |
| side_entry | valid | |
| west_wall | valid | |
| roof_seams | valid | |
| garage | valid | |
| interior | valid (P2 composition, F16) | |
| garden | valid | |

No view has an occluded, clipped or illegible target.

## 5. Previous findings

### v002 open P1 (v002: 0 P0 / 1 P1)

| id | sev | status in v003 | evidence |
|---|---|---|---|
| N1, front beds a low fern carpet; tall grass at the glazed corner missing; ferns about half source height | P1 | **partly fixed; superseded by new P1s N7 and N8** | **Fixed:** the tall feather-reed and grass mass at the bay. front x 590-830; front_corner `fc_bayfront_bed.png`; entry_steps x 0-110; glass_close x 870-1000, y 850-1080. Blue fescue is present in all front views. Fern height in the east bed is now about 0.8 m (garden, entry_steps). **Not fixed:** the ferns' leafy mass. The ferns were removed from the west-wall strip where the source shows them most strongly (N7), and the scaled prototype now reads as bare canes (N8). Net: the front planting still does not match the sources. |

### v001 P1s (all fixed in v002)

| v001 id | sev | status in v003 | evidence |
|---|---|---|---|
| F1 side-entry head wedges | P1 | **still fixed** | side_entry: both head corners are closed cedar, minimum luma 11.4 (`side_entry_head.png`). No change from v002. |
| F2 black squares at glazing nodes | P1 | **still fixed** | glass_close: minimum luma 8.3; nodes continuous (`glass_nodes.png`). facade_close: only the thin black frame edge at x 383-385. |
| F3 fin plinth slot | P1 | **still fixed** | Continuous plinth at the fin base in right_side (`right_side_fin_base.png`) and aerial. |
| F4 side-entry door hidden; flat lining | P1 | **still fixed** (P2 residual N2) | In front, the boarded return and the door panel with its black head are visible (`front_sideentry.png`). front_corner shows the same. |
| F5 garage roof turned 90° | P1 | **still fixed** | top: north slope with north-south seams and hipped ends; rear and rear_side agree. |
| F6 ferns missing, side bed bare | P1 | **regressed in part (N7)** | v002 had fern rosettes in both west beds. v003 has none in the west-wall strip, and the north-of-side-steps bed is about half bare soil again. |
| F7 right_side too close | P1 | **still fixed** | Whole roof and front facade in frame. |
| F8 top cuts off the garage | P1 | **still fixed** | Whole garage in frame. |

### v001 and v002 P2s

| id | status in v003 |
|---|---|
| F9, F10, F13, F14, F15, F16, F17 | not fixed (not targeted) |
| F11r | not fixed (not targeted) |
| N2, N3, N4, N5, N6 | not fixed (not targeted) |
| F12 hip caps, F18 garage depth | still resolved |

**Regression check:**
- **Black geometry:** no new slots, wedges or voids in any of the 18 views.
- **Building and context:** massing, roof, glazed corner, balcony, porch, front band, west-wall openings, plinth and street context are pixel-identical to v002 outside the beds.
- **Regressions:** both are landscape-only. The west-wall fern hedge was lost (N7), and the fern form changed for the worse (N8).
