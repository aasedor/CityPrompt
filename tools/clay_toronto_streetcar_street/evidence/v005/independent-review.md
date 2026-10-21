# Independent holistic review: Toronto streetcar main street, clay v005

Reviewer: independent RLASM v6.1 holistic reviewer. I did not build this candidate. I judged only rendered pixels against the three locked sources: sources/front.png, sources/oblique.jpg and sources/top.jpg. I opened all three sources, all 18 renders and all 4 phone boards at full resolution with the image reader. I wrote zoomed crops and luminance probes only into the new folder review/crops_qhvtzk/ inside the v005 folder. I changed no other file and rendered nothing.

## 1. Verdict

Verdict: FAIL

Under the brief's wording this is VISUAL_REWORK_REQUIRED. The v004 gable-coping P1 is fixed in the pixels, and the v002 cab-nose P1 stays fixed. One P1 remains: a 1 m open slot between the west glass slab and the brick condo wing renders as a pure-black stripe the full length of the slab in the governing top view. A matching black crevice shows on the slab's west side in aerial. The stripe is the same, pixel for pixel, in v002 and v004, so it is not a regression, but neither earlier review recorded it.

Counts: P0=0 P1=1 P2=8

## 2. Findings table

| id | severity | view(s) | finding (what the pixels show) | evidence / likely cause | suggested finite fix |
|---|---|---|---|---|---|
| 1 | P1 | top (primary), aerial | **Black slot round the west glass slab.** In top, a pure-black stripe about 11 px wide (about 0.9 m at 12.6 px/m) runs the whole east edge of the west glass slab and its low base, from y 0 to y 495 at x 463-473. It sits between the slab's grey edge and the brick wing's orange parapet. A 1-2 px black line also separates the slab from its low base at y 393-394. In aerial, a black crevice about 4-6 px wide runs down the slab's west/south side (x 40-160, y 470-700). The source top shows the glass slab and the brick wing as one joined complex, with lit glass and balconies along the slab's east edge and no dark slot. Read at 1440 px, the stripe looks like an ink outline or a void, not a building face. It fails the "black patches, slots or wedges" rule. | Luminance probe: top.png row 250 and row 450, x 463-473, L = 0.02-0.03 (the slab roof is 0.45 and the wing roof 0.41). Column 330, y 393-394, L = 0.00-0.06. aerial.png has about 380 px below L 0.03 in that crevice. Crops: crops_qhvtzk/top_slab_v005.png, top_slab_eastface.png and ae_slab_base.png. The same stripe is in v002 and v004 top (3678 / 3672 / 3604 px below L 0.03 in the same crop). Likely cause (from the build script; cause only, not proof): the wing's rear wall face is at x = -24.0 m, but the slab and base east face is at -25.0 m. That leaves a 1.0 m open air slot, 23-31 m deep and about 40 m long, that no light reaches. The base ends at y = 45.7 m and the slab starts at 46.0 m, a 0.3 m slot. The west context block stops at x = -47.0 m against the slab's west face at -46.0 m, another 1 m slot. | Close the slots. Extend the wing's rear wall and roof to x = -25.0 (or bring the slab and base east face to -24.0), and run the base on to y = 46.0 so it meets the slab. Either butt the west context block to x = -46.0 or widen that gap into a real lane, at least about 4 m, that daylight reaches. Re-render top and aerial and confirm there is no pixel below about 15% luminance along the slab's edges. |
| 2 | P2 | victorian_arches | At the gable apex, a crisp 1 px mid-grey vertical seam (L about 0.37 on a 0.55 coping) runs about 15 px down the left face of the apex block, where the two raking coping halves overlap past the apex line. It is not black and not a gap. | Probe at x 703, y 140-157. Crop: crops_qhvtzk/va_apex.png. It is the visible end face of the 1 cm overlap. | Optional: miter the two halves at the apex line, or bury the overlap inside the finial block. |
| 3 | P2 | streetcar_nose, track_slab | Carried from v004 #2. A soft darker vertical band where the red dome starts to taper, plus a crisp colour line where the grey roof side meets the red cap. No fans, slot or black seam. | Crops: sn_cab.png and ts_cab.png. | Optional: add one more loft ring at the cab start. |
| 4 | P2 | roof_skylights, aerial, front_corner, top | The skylights now read as hipped glazed lanterns: v004 P2 #3 is taken. Both still have the same form. In the oblique source, one is an elongated ridged lantern and the other is pyramidal. In front_corner they still read low. | Crop: fc_sky.png. | Optional: lengthen the western skylight to about 2:1 with a ridge. |
| 5 | P2 | front_corner, rear_side, span_wire_pole, pantograph_wire | Carried. The brick condo wing has projecting glass-box balconies, where oblique.jpg shows mostly inset loggias within the brick frame. | Visual. | Optional: recess part of the balcony depth into the frame. |
| 6 | P2 | front, condo_balconies, rear | Carried. The charcoal condo's balconies are per-bay boxes, where front.png shows long continuous slabs. They still read as near-continuous bands at street scale. | Visual. | Optional: merge the bays into longer slabs. |
| 7 | P2 | front | Carried. The near-right of the front render is the brick condo wing, where the front source shows Victorian storefronts. The sources conflict here, and the render follows the governing top view. | Visual. | None. Record it in the method notes. |
| 8 | P2 | (render set) | The brief names facade_close, architecture_close and glass_close, but those files do not exist. 18 renders are present, and corner_storefront, victorian_arches and condo_balconies cover that content. | File listing. | Align the brief's view list with the 18 published views. |
| 9 | P2 | left_side, front_corner, rear_side | Carried. The brick wing's south end wall and rear are blank brick planes standing above the three-storey neighbours. They are coherent as party walls, but read slightly unfinished. | Visual. | Optional: a brick course or a parapet return. |

## 3. Source conformance checklist

Scale from top.png: building line to building line is x 625-940, which is 315 px, or about 25 m (about 12.6 px/m).

| item | status | view(s) used |
|---|---|---|
| Section order, west to east: storefronts / sidewalk / brick strip / curb lane / track lane / yellow centre line / track lane / curb lane / strip / sidewalk | conforms | top (pixel profile at row 760), rear, intersection_crossing |
| Widths | conforms: west sidewalk with strip 47 px (about 3.7 m); curb lanes 53 and 54 px (about 4.2 and 4.3 m); slab 95 px (about 7.5 m); east strip and sidewalk 66 px (about 5.2 m) | top |
| Pale concrete track slab with transverse joints | conforms | track_slab, intersection_crossing, front |
| Twin grooved-rail tracks at 1495 mm gauge, correct centres | conforms: two pairs of rails on the slab either side of the yellow line; grooves read in track_slab | top, track_slab, top_crossing crop |
| Single yellow centre line | conforms | track_slab, streetcar_nose, front, top |
| White lane dashes in the curb lanes | conforms | front, streetcar_nose, top, intersection_crossing |
| Toronto two-line crossings over both streets | conforms | top (top_crossing crop), intersection_crossing, front_corner |
| Stop bars | conforms (main street north approach; cross-street approaches) | top, intersection_crossing |
| Corner curb returns | conforms | top, intersection_crossing, front_corner |
| Yellow centre line on the cross street | conforms | top, left_side, right_side, aerial |
| Poles and span wires pole to pole | conforms | top, front, intersection_crossing, span_wire_pole |
| Hangers and insulators | conforms (white insulator on a hanger, clamp on the contact wire) | front (fr_hanger crop), streetcar_nose, span_wire_pole |
| Contact wires over each track | conforms | front, pantograph_wire, top |
| Long-armed cobra-head street lights | conforms | intersection_crossing, span_wire_pole, condo_balconies, streetcar_nose |
| Streetcar: five modules | conforms | top, front_corner, rear |
| Livery bands (red skirt / wide white / dark window band / wide white / narrow red roof band) | conforms | east_sidewalk (es_car crop), front, track_slab |
| Black joint stripes | conforms | east_sidewalk, pantograph_wire, front |
| Cab ends: projection at the light band, about 20 deg rake, domed red cap with rounded shoulders, wrapped windscreen with white pillars, amber sign following the rake, white apron, red light band with headlights, red brow | conforms. The side profile slopes back over the windscreen into the dome. | east_sidewalk, streetcar_nose, track_slab, front (fr_cab crop) |
| Cab-to-roof junctions at both ends | conforms (no fans, gap, step slot or black seam) | streetcar_nose, track_slab (north cab); front_corner, rear (south cab) |
| Doors | conforms | pantograph_wire, front |
| Wheels on the rails | conforms as clay (skirt over the east-track rails, with a contact shadow) | streetcar_nose, track_slab, east_sidewalk |
| Pantograph raised and at the wire | conforms (the head bar crosses the contact wire at the arm head) | pantograph_wire (pw_head crop), streetcar_nose (sn_panto crop), front_corner |
| Streetcar on the east track, northbound, mid-block | conforms | top, rear, front_corner |
| Red TTC stop pole on the east corner | conforms | corner_storefront, intersection_crossing |
| Tree pits and young trees | conforms (smaller trees kept) | east_sidewalk, intersection_crossing, top |
| Bins | conforms | east_sidewalk, corner_storefront |
| West Romanesque corner block: segmental 2nd-storey and round-arched 3rd-storey windows | conforms | victorian_arches, front_corner |
| West Romanesque corner block: corbelled cornice turning the corner | conforms | front_corner, left_side, victorian_arches |
| West Romanesque corner block: central gable and plaque | conforms. The coping is clean at both feet and the apex (finding 2 is P2 polish only). | victorian_arches, streetcar_nose, right_side, front_corner |
| West Romanesque corner block: corner pier and storefront arcade | conforms | front_corner, east_sidewalk |
| West Romanesque corner block: cross-street facade (one corner shopfront with a short sign-band return; solid coursed ground storey with doors and small sashes; irregular pairs of flat-headed sashes) | conforms | left_side, aerial |
| Plainer west block with white bracketed cornice | conforms | front_corner, streetcar_nose, front |
| West brick condo wing: 7 storeys, balconies on alternate bays with glass returns | conforms (balcony type is P2 #5) | front_corner, rear, span_wire_pole |
| West 10-storey glass slab: floor bands, green roof, penthouse | form conforms; junction with the wing and base deviates (P1 #1, black slot) | front_corner, rear, rear_side, top, aerial |
| East corner block: storefronts on both streets | conforms | front_corner, aerial, corner_storefront |
| East corner block: two skylights | conforms (now hipped; P2 #4) | roof_skylights, aerial, top |
| East second brick block: segmental windows, bracketed cornice | conforms | corner_storefront, aerial |
| East low two-storey block with dark roof | conforms | top, aerial |
| East charcoal condo: balconies with glass returns, green roof, set-back penthouse | conforms (per-bay balconies are P2 #6) | condo_balconies, rear, rear_side, top |
| Storefront glazing, transoms, bulkheads and doors | conforms (openings show depth and returns) | corner_storefront, east_sidewalk, right_side |
| Roofs and parapets | conforms (brick parapets, flat membranes, rooftop units) | roof_skylights, front_corner, aerial |
| Context south of the cross street and beyond the lanes | conforms as plain massing (the 1 m slot at the slab's west side is part of P1 #1) | intersection_crossing, left_side, right_side, aerial |
| Materials hierarchy (red brick, pale stone trim, pale slab and sidewalks, red paver strips, dark asphalt, charcoal frame, blue-grey glass, green roofs) | conforms, except the black slot | all |

## 4. Camera validity

All 18 views are valid. No target is occluded or clipped, and every target is legible.
- front_corner holds the whole glass slab with its green roof and penthouse, the Romanesque main facade with its gable, the streetcar and the intersection.
- span_wire_pole and condo_balconies are steep worm's-eye views, but the pole, span wire, insulators and balcony returns are all legible.
- aerial shows the west corner block's cross-street face rather than its main facade. front_corner and victorian_arches cover the main facade.
- The brief's facade_close, architecture_close and glass_close have no files (P2 #8).
- The phone boards match the renders.

## 5. Previous findings

**v004's open P1: black slivers in the west Romanesque gable coping. Fixed.**
- victorian_arches: probes at the left eave foot, the right eave foot and the apex find no neutral (stone-coloured) pixel below 15% luminance on the coping.
  - Left foot crop: the pixels below 0.15 are brick shadow between the corbels (RGB about 56/26/14), not the coping.
  - Apex crop: the darkest coping pixel is 0.37, a thin overlap seam (P2 #2).
  - Right foot crop: the darkest pixels are corbel brick shadow at 0.14 (RGB 58/32/20).
- The only neutral dark pixels in the gable area are window glass, plus one isolated pixel at (935, 208).
- The same junctions are clean in right_side (minimum L 0.19), streetcar_nose (the dark pixels are the contact wire and the lamp arm) and front_corner (the dark pixels are window glass).
- Crops: va_gable_full.png, va_left_foot.png, va_apex.png, va_right_foot.png, sn_gable.png, rs_gable.png and fc_gable.png.

**v004 P2 #3: skylights under-scaled and flat. Fixed.** They read as hipped glazed lanterns in roof_skylights and aerial (residual P2 #4).

**v002's P1: cab noses as vertical boxes. Still fixed.**
- In the east_sidewalk side profile, the cab end curves back above the light band into a domed red cap.
- streetcar_nose, track_slab and front show the wrapped windscreen, white pillars, raked amber sign, red light band with headlights, white apron and red brow.

**Earlier fixes that must still hold. All hold.**
- Clean cab-to-roof junctions at both ends.
- White-dominant livery in the specified band order.
- Glass returns on every balcony of both condos.
- The west corner block's cross-street facade.
- The main-street segmental and round arches, arcade, corbelled cornice, gable and plaque.
- front_corner holding the whole slab.
- Smaller trees.
- 1495 mm twin tracks on the pale slab with a single yellow line.
- Span-wire catenary with contact wires and the pantograph at the wire.
- The TTC stop pole.
- The east corner block with storefronts on both streets.

**Against the candidates.**
- v002 had 0 P0 and 1 P1 (cab nose). That P1 is fixed here.
- v004 had 0 P0 and 1 P1 (gable coping). That P1 is fixed here.
- The new P1 #1, the black slot round the glass slab, is not a regression. The same stripe is in the v002 and v004 top renders, with near-identical counts of near-black pixels. Neither review recorded it, so v002 and v004, judged against the same rule, would each carry a second P1.
- v005 is therefore strictly better than both candidates, but it does not reach zero P1.
