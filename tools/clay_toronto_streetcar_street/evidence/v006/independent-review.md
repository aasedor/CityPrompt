# Independent holistic review: Toronto streetcar main street, clay v006

Reviewer: independent RLASM v6.1 holistic reviewer. I did not build this candidate. I judged only rendered pixels against the three locked sources: sources/front.png, sources/oblique.jpg and sources/top.jpg. I opened all three sources, all 18 renders and all 4 phone boards at full resolution with the image reader. I wrote zoomed crops and side-by-side comparisons only into the new folder review/crops_typqwy/ inside the v006 folder. I changed no other file and rendered nothing.

## 1. Verdict

Verdict: FAIL

Counts: P0=0 P1=1 P2=10

Under the brief's wording this is VISUAL_REWORK_REQUIRED. The targeted fix works: the v005 black stripe between the west glass slab and the brick condo wing is gone from top, and the black crevice is gone from aerial. The v004 gable-coping slots and the v002 cab-nose finding both stay fixed. One P1 remains, and it is a different defect. It has the same cause as the v005 P1, an unlit open-air slot between two masses, and it was missed by the fix pass. In the governing top view, a 0.6 m slot between the east corner block's rear wall and the east context block renders as a near-black line about 6 px wide over 154 rows. It is milder than the v005 stripe, but it fails the same under-15%-luminance test. It is unchanged, pixel for pixel, in the v002, v004 and v005 top renders, so it is not a regression. Neither earlier review recorded it.

## 2. Findings table

| id | severity | view(s) | finding (what the pixels show) | evidence / likely cause | suggested finite fix |
|---|---|---|---|---|---|
| 1 | P1 | top (primary) | **Dark slot behind the east corner block.** A near-black line, about 6 px wide (about 0.5 m at 12.6 px/m), runs north-south between the east corner block's rear parapet and the pale east context block. It spans x 1286-1292, y 704-859. Its core is RGB about 31-37 and it fades to the shaded back lane at its north end. At 1440 px it reads as a dark ink line or void along the block's rear edge. The source top shows no dark slot there: the corner block's rear meets a lit lot or lane. It is less dark and less long than the v005 stripe (core L 0.11 against 0.02, and 154 rows against 495), but it is the same class of defect, and the brief and the task reject black slots and stripes. | Luminance probe in top.png, x 1283-1296, y 690-900: 388 px below L 0.15, minimum 0.108. Row profile at y 750: 0.23 / 0.16 / 0.16 / 0.15 / 0.14 / 0.12 / 0.12, then 0.28 at the neighbour's parapet. v002, v004 and v005 top give 393, 392 and 392 px below 0.15 in the same window, with minimum 0.112, so the slot is unchanged. Crops: crops_typqwy/top_east_slot_1x.png (native scale), top_eastcorner_gap.png (4x) and top_east_full.png (2x). Likely cause (from the build script; cause only, not proof): the East corner block's depth is 28.0 m from the building line x = 13.4, so its rear face is at x = 41.4 m. The east context "neighbour" box starts at x = 42.0 m. That leaves a 0.6 m open slot about 18 m long, and the 1.8 m height step means no light reaches its floor. The 1.5 m slot on the west (corner block -43.0 against context -44.5) and the wider back lanes are lit (L about 0.3) and are not defects. | Close the slot the way v006 closed the slab gaps. Either deepen the East corner block to 28.8 m (rear face at x 42.2, 0.2 m into the neighbour), or start the neighbour box at x 41.2. For the same reason, also butt the south-of-cross-street east row (XEB + 26 = 39.4) against its context box at x 40.0. That 0.6 m gap is outside every current frame, but it is the same pattern. Re-render top, aerial and rear_side, and confirm no pixel below about 15% luminance along any block-to-block junction. |
| 2 | P2 | top | A residual 1 px crease outlines the low glass base where it meets the brick wing and the west brick block. One line runs at x 473, y 395-500 (L 0.16-0.18, down to 0.12 at the south-east corner). Another runs along y 503, x 400-473 (L 0.12-0.16). It is a crease line, not a slot. It has no width and reads as an edge. | Probes in top.png. Crop: top_westslab_v006.png. | Optional: bevel or lower the base roof edge by a few centimetres, or raise its roof slightly above the meeting parapets so the crease catches light. |
| 3 | P2 | aerial | The brick condo wing's street parapet shows a row of small orange squares through its cream coping. The brick pier tops poke through, or are coplanar with, the coping. They read as a dotted line along the far roof edge. | Crop: ae_wing_parapet.png (aerial x 350-580, y 220-340). | Stop the piers 2-3 cm below the coping underside, or run the coping over them. |
| 4 | P2 | victorian_arches | Carried from v005 #2. A thin mid-grey seam (minimum L 0.37) on the gable apex block where the two raking coping halves overlap. It is not black and it is not a gap. | Crop: va_apex.png. Apex window minimum L 0.166. | Optional: miter at the apex line. |
| 5 | P2 | streetcar_nose, track_slab | Carried. A soft darker vertical band where the red dome begins to taper. There are no fans, slot or black seam. | Crop: sn_cab.png. | Optional: add one more loft ring at the cab start. |
| 6 | P2 | roof_skylights, aerial, front_corner | Carried. Both skylights are the same hipped form. The oblique source shows one elongated ridged lantern and one pyramidal. | Visual. | Optional: lengthen the western skylight to about 2:1 with a ridge. |
| 7 | P2 | front_corner, rear_side, span_wire_pole, pantograph_wire | Carried. The brick condo wing has projecting glass-box balconies, where the oblique source shows mostly inset loggias. | Visual. | Optional: recess part of the balcony depth into the frame. |
| 8 | P2 | front, condo_balconies, rear | Carried. The charcoal condo's balconies are per-bay boxes, where the front source shows long continuous slabs. | Visual. | Optional: merge the bays into longer slabs. |
| 9 | P2 | front | Carried. The near-right of the front render is the brick condo wing, where the front source shows Victorian storefronts. The sources conflict here, and the render follows the governing top view. | Visual. | None. Record it in the method notes. |
| 10 | P2 | (render set) | Carried. The brief names facade_close, architecture_close and glass_close, but no such files exist. corner_storefront, victorian_arches and condo_balconies cover that content. | File listing (18 PNGs). | Align the brief's view list with the 18 published views. |
| 11 | P2 | left_side, front_corner, rear_side | Carried. The brick wing's south end wall and rear are blank brick planes standing above the three-storey neighbours. | Visual. | Optional: a brick course or a parapet return. |

Ids run from 1 to 11 with no gap. There is one P1 (#1) and ten P2s (#2-#11).

## 3. Source conformance checklist

Scale from top.png: building line to building line is about x 625-940, which is about 315 px for 25 m (about 12.6 px/m). A pixel diff against v005 shows that only the slab-complex region changed. The diff boxes are at top x 189-474, aerial x 14-426, and small regions of front_corner, rear, rear_side and right_side round the slab. Every other view differs by less than 1.6 mean grey levels, which is compression noise. I still checked every item below against the v006 pixels.

| item | status | view(s) used |
|---|---|---|
| Section order, west to east: storefronts / sidewalk / brick strip / curb lane / track lane / yellow centre line / track lane / curb lane / strip / sidewalk | conforms | top, rear, intersection_crossing, front |
| Widths | conforms. Curb lanes are about 51-52 px (about 4.1 m), the slab about 99 px (about 7.8 m) and the east sidewalk visibly wider than the west. | top |
| Pale concrete track slab with transverse joints | conforms | track_slab, intersection_crossing, streetcar_nose |
| Twin grooved-rail tracks at 1495 mm gauge, correct centres | conforms (two rail pairs either side of the yellow line; grooves read) | track_slab, top, front |
| Single yellow centre line | conforms | track_slab, streetcar_nose, front, top |
| White lane dashes | conforms | front, streetcar_nose, track_slab, intersection_crossing |
| Toronto two-line crossings over both streets | conforms | top, intersection_crossing, front_corner, aerial |
| Stop bars | conforms | top, intersection_crossing |
| Corner curb returns | conforms | top, intersection_crossing, front_corner |
| Yellow centre line on the cross street | conforms | left_side, right_side, aerial, top |
| Poles and span wires pole to pole | conforms | top, front, intersection_crossing, span_wire_pole |
| Hangers and insulators | conforms | front, span_wire_pole, pantograph_wire |
| Contact wires over each track | conforms | front, pantograph_wire, intersection_crossing |
| Long-armed cobra-head lights | conforms | span_wire_pole, condo_balconies, intersection_crossing, streetcar_nose |
| Streetcar: five modules | conforms | top, front_corner (fc_southcab.png) |
| Livery bands (red skirt / white / dark window band / white / red roof band) | conforms | east_sidewalk (es_profile.png), front, track_slab |
| Black joint stripes | conforms. These are the only pure-black pixels left in aerial: x 614-727, y 461-539. | east_sidewalk, pantograph_wire, aerial |
| Cab ends: rake, domed red cap with rounded shoulders, wrapped windscreen, amber sign, white apron, red light band with lamps | conforms | streetcar_nose (sn_cab.png), track_slab, east_sidewalk, front |
| Cab-to-roof junctions | conforms (no fans, gaps or black seams) | streetcar_nose, track_slab, front_corner |
| Doors | conforms | pantograph_wire, front |
| Wheels on the rails | conforms as clay (skirt over the east-track rails, contact shadow) | streetcar_nose, track_slab |
| Pantograph raised to the wire | conforms | pantograph_wire, streetcar_nose, front_corner |
| Streetcar on the east track, northbound, mid-block | conforms | top, rear, front_corner |
| Red TTC stop pole on the east corner | conforms | corner_storefront, intersection_crossing, front_corner |
| Tree pits and young trees | conforms | east_sidewalk, intersection_crossing, top |
| Bins | conforms | east_sidewalk, corner_storefront |
| West Romanesque corner block: segmental 2nd-storey and round-arched 3rd-storey windows | conforms | victorian_arches, front_corner |
| West Romanesque corner block: corbelled cornice turning the corner | conforms | front_corner, left_side, victorian_arches |
| West Romanesque corner block: gable and plaque | conforms (coping clean at both feet; apex seam is P2 #4) | victorian_arches, streetcar_nose, right_side |
| West Romanesque corner block: corner pier and storefront arcade | conforms | front_corner, east_sidewalk |
| West Romanesque corner block: cross-street facade | conforms (paired flat sashes, solid ground storey with doors, one corner shopfront) | left_side, aerial |
| Plainer west block with white bracketed cornice | conforms | streetcar_nose, front_corner, corner_storefront |
| West brick condo wing: seven storeys, balconies on alternate bays with glass returns | conforms (balcony type is P2 #7; parapet dots are P2 #3) | front_corner, rear, span_wire_pole, rear_side |
| West ten-storey glass slab: floor bands, green roof, penthouse, junction with the wing and base | conforms. The v005 slot is closed, and only a 1 px crease remains (P2 #2). | top, aerial, front_corner, rear, rear_side |
| East corner block: storefronts on both streets | conforms | corner_storefront, front_corner, aerial |
| East corner block: two skylights | conforms (form is P2 #6) | roof_skylights, aerial, top |
| East corner block: rear junction with the east context | deviates (P1 #1, dark slot) | top |
| East second brick block: segmental windows, bracketed cornice | conforms | aerial, front_corner |
| East low two-storey block with dark roof | conforms. The roof is an intended charcoal, RGB about 33/34/37, matching the source. | top, aerial |
| East charcoal condo: balconies with glass returns, green roof, set-back penthouse | conforms (per-bay balconies are P2 #8) | condo_balconies, rear, rear_side, top |
| Storefront glazing, transoms, bulkheads and doors | conforms (openings show depth and returns) | corner_storefront, east_sidewalk, right_side |
| Roofs and parapets | conforms, except P1 #1 and P2 #3 | roof_skylights, aerial, rear_side |
| Context south of the cross street and beyond the lanes | conforms as plain massing (the south and west lanes are lit, with no black slots) | intersection_crossing (ic_south.png), left_side, right_side, aerial (ae_southeast.png) |
| Materials hierarchy (red brick, pale stone, pale slab and walks, red paver strips, dark asphalt, charcoal frame, blue-grey glass, green roofs) | conforms, except the dark slot | all |

## 4. Camera validity

All 18 views are valid. No target is occluded or clipped, and every target is legible.
- front_corner holds the whole glass slab with its green roof and penthouse, the Romanesque facade with its gable, the streetcar and the intersection.
- span_wire_pole and condo_balconies are steep worm's-eye views, but the pole, span wire, insulators, cobra-head and balcony returns are legible.
- aerial shows the west corner block's cross-street face. front_corner and victorian_arches cover its main facade.
- top is a true plan and frames both street walls, the intersection and the streetcar.
- The phone boards reproduce the renders and the locked sources in matched pairs.
- The brief's facade_close, architecture_close and glass_close views do not exist (P2 #10).

## 5. Previous findings

**v005 P1: black stripe between the west glass slab and the brick condo wing. Fixed.**
- top.png: no pixel below L 0.03 (v005 had 3668).
  - The 11,421 px component below L 0.15 at x 189-473 in v005 is gone.
  - Along the slab's east edge, the slab-to-wing seam now probes at L 0.33-0.41 (rows 50-385), and the slab's west side at 0.36-0.58.
  - What remains is a 1 px crease at the low base, at L 0.12-0.18 (P2 #2).
- aerial.png: the v005 dark components are gone. One was 2,214 px at x 31-162 (minimum L 0.00), the other 1,545 px at x 359-424.
  - Pixels below L 0.03 fell from 476 to 99, and all 99 are streetcar joint stripes.
  - The slab's west face now butts the context block, with no crevice.
- Crops: top_westslab_v006.png against top_westslab_v005.png, cmp_v005_left_v006_right_aerial.png, and the front_corner, rear, rear_side and right_side comparisons.

**v004 P1: black slivers in the Romanesque gable coping. Still fixed.**
- victorian_arches has zero neutral (low-chroma) pixels below L 0.15 in each junction window:
  - left foot: minimum 0.123, brick shadow only;
  - apex: minimum 0.166;
  - right foot: minimum 0.115, corbel brick shadow only.
- victorian_arches has no pixel below L 0.03 anywhere.
- Crops: va_gable.png, va_left_foot.png, va_apex.png and va_right_foot.png.

**v002 P1: cab noses as vertical boxes. Still fixed.**
- streetcar_nose and track_slab show a raked windscreen, a domed red cap with rounded shoulders, white pillars, the amber sign, a red light band with lamps and a white apron.
- The east_sidewalk side profile curves back above the light band.
- front_corner shows the south cab domed as well.
- Crops: sn_cab.png, es_profile.png and fc_southcab.png.

**Earlier P1s. All still fixed.**
- v001 #1, livery: fixed.
- v001 #2, boxy cabs: fixed.
- v001 #3, invented cross-street facade: fixed. left_side shows paired flat sashes and a solid ground storey.
- v001 #4, front_corner clipping the slab: fixed.
- v003 #1, cab-junction fans and slot: fixed.
- v003 #2, balconies without glass returns: fixed. Returns are visible in condo_balconies and front.

**v005 P2s.**
- #2, apex seam: not fixed (P2 #4).
- #3, cab taper band: not fixed (P2 #5).
- #4, skylight form: not fixed (P2 #6).
- #5, wing balcony type: not fixed (P2 #7).
- #6, charcoal balconies per bay: not fixed (P2 #8).
- #7, source conflict at the front near-right: carried (P2 #9).
- #8, brief view list: not fixed (P2 #10).
- #9, blank party walls: not fixed (P2 #11).
- None regressed.

**Against the candidates.**
- v002: 0 P0, 1 P1 (the cab nose, since fixed).
- v005: 0 P0, 1 P1 (the slab-gap stripe, fixed here).
- v006: 0 P0, 1 P1.
- The v006 P1 (#1, the east-corner slot) is present unchanged in the v002, v004 and v005 top renders (392-393 px below L 0.15 in the same window). Judged by the same rule, v002 and v005 would each carry it as a second P1.
- v006 is therefore strictly better than both candidates and has no regression, but it does not reach zero P1.
- The remaining fix is the one-dimension closure described in finding #1.
