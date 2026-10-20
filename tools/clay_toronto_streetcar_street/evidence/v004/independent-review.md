# Independent holistic review: Toronto streetcar main street, clay v004

Reviewer: independent RLASM v6.1 holistic reviewer. I did not build this candidate. I judged only rendered pixels against the three locked source pixels: sources/front.png, sources/oblique.jpg and sources/top.jpg. I opened all 18 renders and all 4 phone boards at full resolution. I made zoomed crops in a new folder, /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/ind-review-v004-crops-07e9f233.

## 1. Verdict

**VISUAL_REWORK_REQUIRED.** Both v003 P1s are fixed in the pixels. The streetcar cab junctions are clean and every balcony now has glass returns. One new P1 remains: the Romanesque gable's stone coping leaves pure-black open slots where its raking pieces meet the horizontal cornice and the apex block. The slots are clear in the dedicated victorian_arches close-up and show as dark specks in streetcar_nose and right_side.

Counts: P0 = 0, P1 = 1, P2 = 7

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | victorian_arches (clearest), streetcar_nose, right_side | On the west Romanesque corner block's central gable, the raking stone coping fails to meet the horizontal corbelled cornice. It also fails to meet the apex block. Three pure-black slivers show in victorian_arches: at the left eave foot (about x 490, y 455), at the right eave foot where the gable coping meets the cornice cap (about x 975-1005, y 90-105) and at the apex (about x 700, y 150). At 8x zoom they are solid black (0,0,0-class), so they are voids or back-faces, not shading. In streetcar_nose and right_side the same junctions read as two small dark dots on the coping. This is a contact/finish defect on a named identity element, in the close-up made to check it. It is the same "black seam / slot" class the brief rejects at the cab junction. | The raking coping boxes are butt-jointed or end short of the cornice cap and apex block, with no miter. The open ends show unlit interior or back-faces, or a small gap where the coping, cornice top and apex block do not overlap. | Extend each raking coping piece past the cornice cap and into the apex block by at least one coping thickness, or miter and close the ends. Cap any open coping ends. Re-render victorian_arches, streetcar_nose, right_side and front_corner, and confirm there is no pixel below about 15% luminance on the coping at those junctions. |
| 2 | P2 | streetcar_nose, track_slab | Both cab-to-roof junctions are now clean: no fans, no slot and no black seam. A faint soft darker vertical band remains where the lofted red dome starts to taper. At the cap start line there is also a crisp vertical colour line where the grey roof side meets the red dome. | Normal transition at the start of the smooth-shaded taper, plus the hard material boundary on the cab-start line. | Optional: add one more loft ring near the cab start, or blend the first taper ring. |
| 3 | P2 | roof_skylights, top, front_corner, aerial | The two east-corner-block skylights are present but read as low glazed trays with a barely visible hip. They are also smaller than the large, steep hipped/pyramidal glazed skylights in oblique.jpg. | The hip rise and plan size are under-scaled. | Raise the hip ridge so the glass reads as a pyramid or hip, and enlarge the plan to roughly the source proportion. |
| 4 | P2 | front_corner, rear_side, span_wire_pole, pantograph_wire | The brick condo wing has projecting glass box balconies on alternate bays and every floor. Oblique.jpg shows mostly inset loggia-style openings with glass rails set within the brick frame. | Box balconies were used for both condos. | Optional: recess part of the balcony depth into the brick frame on the brick wing. |
| 5 | P2 | front, condo_balconies, rear | Charcoal-condo balconies are per-bay boxes separated by recessed dark piers, where front.png shows long deep slabs. At street scale they still read as near-continuous bands. | The balcony module equals one bay. | Optional: merge adjacent bays into longer slabs with a shared glass rail. |
| 6 | P2 | front | The render's front camera looks south, so the right foreground is the brick condo wing. In the source front, the right foreground is a Victorian brick storefront frontage. The sources disagree here (front.png and top.jpg place the condo frontages differently), and the brief says the top view governs. | Source inconsistency, resolved in favour of the plan. | None required. Note it in the method record. |
| 7 | P2 | (render set) | The brief names facade_close, architecture_close and glass_close, but those files do not exist. 18 renders are present and on the boards, and corner_storefront, victorian_arches and condo_balconies cover that content. | The brief's list and the street-specific view set differ. | Align the brief's list with the 18 published views. |
| 8 | P2 | left_side, front_corner, rear_side | The brick condo wing's south end wall and rear are blank brick planes. They are coherent as party walls but read slightly unfinished above the 3-storey neighbours. | No source shows these faces. | Optional: add a faint brick course or a parapet return. |

## 3. Source conformance checklist

| item | status | view(s) used |
|---|---|---|
| Section order, west to east: storefronts / sidewalk / brick strip / curb lane / track lane / yellow centre line / track lane / curb lane / strip / sidewalk | conforms | top, rear, intersection_crossing |
| Widths (about 25 m building line to building line; west sidewalk about 3.9 m, east about 5.3 m) | conforms. Measured in top: west sidewalk about 3.8 m, east about 5.4 m, curb lanes about 4.3 m each, slab about 7.7 m, total about 25 m. | top |
| Pale concrete track slab with transverse joints | conforms | track_slab, intersection_crossing, front |
| Twin embedded grooved-rail tracks, 1495 mm gauge, correct centres | conforms. Gauge measures about 1.45-1.5 m in top; the tracks sit either side of the single yellow line. | top, track_slab |
| Single yellow centre line | conforms | track_slab, streetcar_nose, top |
| White lane dashes in the curb lanes | conforms | front, top, streetcar_nose |
| Toronto two-line crossings over both streets | conforms | top, intersection_crossing |
| Stop bars | conforms. Southbound half on the north approach; cross-street approaches present. | top, intersection_crossing |
| Corner curb returns | conforms | top, intersection_crossing, front_corner |
| Yellow centre line on the cross street | conforms | top, left_side, right_side |
| Paired poles and span wires pole to pole | conforms | top, front, intersection_crossing, span_wire_pole |
| Hangers and insulators | conforms | front (white insulators on hangers), span_wire_pole |
| Contact wires over each track | conforms | top, front, pantograph_wire |
| Long-armed cobra-head street lights on the poles | conforms | intersection_crossing, span_wire_pole, condo_balconies |
| Streetcar: five modules | conforms | top, front_corner |
| Streetcar livery bands (red skirt / wide white / dark window band / wide white / narrow red roof band) | conforms | east_sidewalk, track_slab, front |
| Black joint stripes | conforms | front, east_sidewalk, pantograph_wire |
| Cab ends: rake, dome, windscreen, white pillars, amber sign, light band with headlights, white apron, red brow | conforms. The nose projects at the light band and rakes back over the windscreen; the domed cap has rounded shoulders. | streetcar_nose, track_slab, east_sidewalk, front |
| Doors | conforms | front, pantograph_wire |
| Wheels on the rails | conforms as clay. The skirt sits over the east-track rails with a ground shadow; wheels are hidden, as on a low-floor car. | track_slab, streetcar_nose |
| Pantograph raised to the wire | conforms. The head bar crosses the contact wire. | pantograph_wire, track_slab, streetcar_nose, front |
| Streetcar on the east track, northbound, mid-block | conforms | top, rear, front |
| Red TTC stop pole on the east corner | conforms | corner_storefront, intersection_crossing, front_corner |
| Tree pits and young trees | conforms | intersection_crossing, east_sidewalk, top |
| Bins | conforms | east_sidewalk, corner_storefront, front_corner |
| West Romanesque corner block: segmental 2nd-storey and round-arched 3rd-storey windows | conforms | victorian_arches, front_corner |
| West Romanesque block: corbelled cornice turning the corner | conforms | front_corner, left_side |
| West Romanesque block: central gable and plaque | conforms in form; deviates in finish (open coping slots, finding 1) | victorian_arches, streetcar_nose, right_side |
| West Romanesque block: corner pier and storefront arcade | conforms | front_corner, east_sidewalk |
| West Romanesque block: cross-street facade (one corner shopfront with a short sign-band return; mostly solid ground storey with doors and small sashes; irregular pairs of flat-headed sashes) | conforms | left_side, aerial, front_corner |
| Plainer west block with white bracketed cornice | conforms | front_corner, front, streetcar_nose |
| West brick condo wing, 7 storeys, balconies on alternate bays with glass returns | conforms; deviates slightly in balcony type (finding 4) | front_corner, rear_side, span_wire_pole |
| 10-storey glass slab with floor bands, green roof and penthouse | conforms. Whole slab held in front_corner. | front_corner, rear, rear_side, top |
| East corner block: storefronts on both streets | conforms | corner_storefront, right_side, front_corner |
| East corner block: two skylights | conforms in count; deviates in hip and size (finding 3) | roof_skylights, top |
| East second brick block with segmental windows and bracketed cornice | conforms | corner_storefront (background), aerial |
| East low two-storey block with dark roof | conforms | top, aerial |
| East charcoal condo: balconies with glass returns, green roof, set-back penthouse | conforms; balconies are per-bay (finding 5) | condo_balconies, rear, rear_side, top |
| Storefront glazing, transoms, bulkheads and doors | conforms | corner_storefront, east_sidewalk, right_side |
| Roofs and parapets | conforms (brick parapets, flat roofs, rooftop units) | roof_skylights, front_corner, aerial |
| Context south of the cross street and beyond the lanes | conforms (plain massing with window patches) | intersection_crossing, left_side, right_side |
| Materials hierarchy (red brick, pale stone trim, pale concrete slab and sidewalks, red paver strip, dark asphalt, charcoal frame, blue-grey glass, green roofs) | conforms | all |

## 4. Camera validity

All 18 views are valid. No target is occluded or clipped, and every target is legible.
- front_corner holds the whole glass slab with its green roof and penthouse, the Romanesque main facade with its gable, the streetcar and the intersection.
- aerial shows the west corner block's cross-street face and roof rather than its main facade. This is acceptable because front_corner and victorian_arches cover the main facade.
- span_wire_pole and condo_balconies are steep worm's-eye views, but the pole, span wire, insulators and balcony returns are all legible.
- The three detail names facade_close, architecture_close and glass_close in the brief have no files (finding 7). Their content is covered by other views.

## 5. Previous-version findings (v003), checked in the pixels

1. **North-cab dark fans and rear-lip wedge/slot: resolved.** The north cab in streetcar_nose shows a smooth red dome meeting the boxed red band and the grey roof. At 6x zoom there are no fan streaks, no slot and no black seam. The south cab in track_slab, front_corner and rear is equally clean; the earlier faint vertical crease is reduced to a soft shading band (finding 2, P2). The rake and dome still read in east_sidewalk (side profile slopes back above the light band), streetcar_nose and front.
2. **Balconies as open trays: resolved.** Every balcony now shows glass returns at both ends, running back to the building face, so the balconies read as glass boxes:
   - charcoal condo: condo_balconies, rear (top-down view of the open-backed three-sided boxes) and front (left);
   - brick condo wing: rear, rear_side, front (right) and span_wire_pole.

Earlier fixes that must still hold, all confirmed:
- raked, domed Flexity nose;
- white-dominant livery band order;
- west corner block cross-street facade (left_side);
- front_corner holds the whole glass slab;
- smaller street trees;
- twin 1495 mm tracks on the pale slab with a single yellow line;
- span-wire catenary with contact wires and the pantograph at the wire;
- TTC stop pole;
- Romanesque main facade with segmental and round arches, corbelled cornice and central gable (now with the coping-seam defect, finding 1);
- east corner block with storefronts on both streets and two skylights.
