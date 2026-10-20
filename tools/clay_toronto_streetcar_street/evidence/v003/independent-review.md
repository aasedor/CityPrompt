# Independent holistic review: Toronto streetcar main street, clay v003

Reviewer: independent RLASM v6.1 holistic reviewer (not the builder). Judged only on rendered pixels against `sources/front.png`, `sources/oblique.jpg` and `sources/top.jpg`. I opened all 18 renders at full resolution, the three sources and the four phone boards. Zoomed crops are in `/tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/review-crops-v003-ef53bfa8/`.

## 1. Verdict

**VISUAL_REWORK_REQUIRED**: the cab nose is now domed and raked, but the north cab's cap-to-body junction has a crinkled shading pinch and a small dark slot. Separately, the balconies on both condominiums have glass on the front edge only, so their sides are open.

Counts: P0 = 0, P1 = 2, P2 = 5

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | streetcar_nose (native ~480-520, 335-380), track_slab (~983-1017, 193-213) | On the north cab, the junction where the lofted red cap meets the boxed red roof band and grey roof has fan-shaped dark streaks across the red, which read as crumpled sheet. A small dark wedge or slot sits at the cap's rear top lip, where it stands proud of the boxed roof band (crop `sn_capjunction.png`, `ts_captop.png`). This fails the brief's test of no gap, step slot or black seam at the junction. The south-cab junction is clean in front_corner and east_sidewalk (only a faint vertical crease). | The loft's last ring does not share vertices or profile with the boxed band section, and its sides draw in by up to 0.40 m. Smooth shading across that ring then pinches the normals, and the cap's rear lip is left higher than the band it should meet. | Make the loft's rear ring exactly the boxed band's cross-section (same vertices, no draw-in at the junction ring), weld it, and start the shoulder draw-in one ring forward. Either add a support loop or limit smoothing at the junction with auto-smooth around 30 degrees. Tuck the cap's rear lip to or below the roof band top so no dark slot shows. Re-render streetcar_nose and track_slab and check both cabs. |
| 2 | P1 | rear (left block ~430-560, 380-760; right block ~840-1000, 300-800), rear_side (brick wing), front (left foreground), condo_balconies, span_wire_pole, pantograph_wire | Every balcony on the charcoal condo and on the brick condo wing is a slab with one glass panel on its outer (street) edge. Both side edges are open, with no glass returns. From the elevated rear and rear_side views the balconies read as open trays (crops `rear_charcoal.png`, `rear_west.png`). In the source front, the glass balustrades return at the balcony ends. | Balcony component models only the front guard panel. | Add side glass guard returns at both ends of every balcony slab, using the same panel height, thickness and material as the front panel. On the charcoal condo, consider joining the per-bay slabs of each floor into one continuous slab with end returns, to match the source's continuous balconies (see P2 #5). |
| 3 | P2 | victorian_arches (~498,452; ~701,154; ~982,102) | Small black slivers at the gable's raking-cornice mitres: at both base returns and at the apex. | Raking and horizontal cornice segments are not mitred or overlapped. | Extend the raking cornice segments into the horizontal cornice and apex block, or add mitre caps. |
| 4 | P2 | roof_skylights, top, front_corner | The two east corner-block skylights are glazed but almost flat. The hip pitch is barely visible, whereas the source oblique shows clearly pitched hipped glass roofs. | Hip rise set too low. | Raise the hip ridge to about 25-30 degrees. |
| 5 | P2 | front (left), aerial, rear | The charcoal condo's balconies are discrete per-bay slabs broken at every pier, and in the front view they read as staggered. The source shows continuous glass-railed balconies along the floor. | Per-bay balcony instancing. | Use one continuous slab per floor (with the guard returns from #2). |
| 6 | P2 | east_sidewalk (south cab ~1145-1180, 400-640) | At the south cab, a faint vertical shading crease runs where the boxed body meets the loft. The lower white band and the red skirt step by a few pixels. | Same ring mismatch as #1, but with less draw-in at this end. | Fixed by the same ring-matching fix as #1. |
| 7 | P2 | renders folder | The brief's detail list names `facade_close`, `architecture_close` and `glass_close`, but no such PNGs exist. The 18 renders present match the brief's count of 18, and the named targets are covered by other views. | Template list not pruned. | Prune the list, or render the three views. |

## 3. Source conformance checklist

| Item | Status | View used |
|---|---|---|
| Section order: storefronts, west sidewalk, brick furnishing strip, curb lane, track lane, yellow centre line, track lane, curb lane, strip, east sidewalk | conforms | top (`top_section.png`), rear, intersection_crossing |
| Widths (building line to building line about 25 m; curb lane wider than track lane; east sidewalk wider than west) | conforms (measured on top at about 12.6 px/m from the gauge: about 24.6 m overall, curb lane about 4.3 m, track lane about 3.7 m) | top |
| Pale concrete track slab with transverse joints | conforms | track_slab, intersection_crossing |
| Twin embedded grooved-rail tracks, right gauge and centres | conforms (gauge-to-centre ratio is plausible for 1495 mm; dark groove beside pale rail head) | top, track_slab (`ts_rails.png`) |
| Single yellow centre line between the tracks | conforms | track_slab, top |
| White lane dashes in curb lanes | conforms | front, track_slab, top |
| Toronto two-line crossings on both streets | conforms | intersection_crossing, top (`top_cross.png`), front_corner |
| Stop bars on both streets | conforms | top, intersection_crossing |
| Yellow centre line on the cross street | conforms | left_side, right_side, top |
| Corner curb returns | conforms | intersection_crossing, top |
| Paired poles and span wires pole to pole | conforms | top, front, span_wire_pole |
| Hangers and insulators | conforms | front, span_wire_pole, top_cross |
| Contact wires over each track | conforms | front, pantograph_wire, top |
| Long-armed cobra-head street lights on the poles | conforms | span_wire_pole, intersection_crossing, condo_balconies |
| Streetcar modules (5) | conforms | fr_nose, top, front_corner |
| Livery bands: red skirt, white, dark window band, white, red roof band | conforms (white-dominant order holds on every module) | east_sidewalk, front, pantograph_wire |
| Black joint stripes | conforms | front, east_sidewalk |
| Cab ends: sloped/raked, domed red cap, rounded shoulders | conforms in form; deviates at the north-cab junction finish (P1 #1) | streetcar_nose, track_slab, front, east_sidewalk, front_corner |
| Large wrapped windscreen and amber destination sign | conforms | streetcar_nose, front, front_corner |
| Doors | conforms (red door leaves in side modules) | front, pantograph_wire |
| Wheels on the rails | conforms (car centred on the east-track rails; bogies under the skirt; shadow contact) | top, track_slab |
| Pantograph raised to the wire | conforms (collector head on the contact wire; foot on the base frame) | pantograph_wire (`panto.png`) |
| Northbound on the east track, mid-block | conforms | top, rear |
| Red TTC stop pole on the east corner | conforms | corner_storefront, intersection_crossing, front_corner |
| Tree pits and young trees (smaller) | conforms | intersection_crossing, east_sidewalk, top |
| Bins | conforms | east_sidewalk, corner_storefront, fc_west |
| West Romanesque corner block: segmental 2nd-storey and round-arched 3rd-storey windows | conforms | victorian_arches, front_corner |
| Corbelled cornice turning onto the cross street | conforms | victorian_arches, left_side, front_corner |
| Central gable with plaque | conforms (P2 mitre slivers) | victorian_arches |
| Corner pier and corner shopfront | conforms | front_corner, left_side |
| Cross-street facade: corner shopfront with sign-band return, solid ground storey with doors and small sashes, irregular paired flat-headed sashes | conforms | left_side, aerial |
| Main-street storefront arcade | conforms | front_corner (`fc_west.png`) |
| Plainer west three-storey block with white bracketed cornice | conforms | front_corner, rear |
| West seven-storey brick condo wing with balconies on alternate bays | deviates (open-sided balconies, P1 #2) | front_corner, rear, span_wire_pole |
| Ten-storey glass slab with floor bands, green roof, penthouse | conforms; whole slab framed in front_corner | front_corner, rear_side, aerial |
| East corner block: storefronts on both streets | conforms | corner_storefront, right_side |
| East corner block: two glazed hipped skylights | conforms in count; deviates mildly in pitch (P2 #4) | roof_skylights, top |
| East second brick block: segmental windows, bracketed cornice | conforms | aerial, east_sidewalk |
| East low two-storey block with dark roof | conforms | top, aerial |
| East six-storey charcoal condo: balconies, green roof, set-back penthouse | green roof and penthouse conform; balconies deviate (P1 #2, P2 #5) | aerial, rear, condo_balconies |
| Storefront glazing, transoms, bulkheads, doors | conforms (recessed mullioned glazing, dark bulkheads, sign band, doors) | corner_storefront, east_sidewalk, right_side |
| Roofs and parapets | conforms | roof_skylights, front_corner, aerial |
| Context south of the cross street and beyond the lanes kept plainer | conforms | intersection_crossing, left_side, right_side, aerial |
| Materials hierarchy (red brick, pale stone trim, pale concrete walks and slab, brick-paver strips, dark asphalt, charcoal and glass condos) | conforms | all |

## 4. Camera validity

All 18 views are valid. No target is occluded or clipped so that it becomes illegible.
- east_sidewalk crops the streetcar at the right edge, but the cab-end profile (the check target) is fully in frame.
- span_wire_pole crops the streetcar and a tree at the bottom and left edges; the pole, lamp, span-wire attachment and insulators are clear.
- front_corner holds the whole glass slab with its green roof and penthouse.
- Of the cameras named in the brief, facade_close, architecture_close and glass_close were not rendered (P2 #7). They are not counted against validity because the brief's own count of 18 matches.

## 5. Previous-version findings: resolved in the pixels?

**v002 P1 (cab nose only partly fixed)**
- Rake in profile (east_sidewalk): **resolved.** The south cab end no longer runs dead vertical. The windscreen leans back and the red cap curves back into the roof (crops `es_nose.png`, `es_junction.png`). The apparent rake is shallower than the claimed 20 degrees because the camera foreshortens it, but it clearly reads as a sloped cab.
- Domed cap and rounded shoulders (streetcar_nose, front, track_slab): **resolved.** The red cap is domed with rounded shoulders on both sides; it is not a flat panel with a straight top. Seen in `sn_nose.png`, `fr_nose.png` and `ts_nose.png`, and on the south cab in `fc_cab8.png`.
- No gap, step slot or black seam at the boxed-body/loft junction: **not resolved at the north cab.** It shows a shading pinch and a dark slot (P1 #1). The south cab is clean except for a faint crease (P2 #6).

**Earlier fixes that must still hold**
- White-dominant livery and band order on every module: holds.
- West Romanesque cross-street facade (corner shopfront with return, solid ground storey, irregular paired flat sashes) with the main-street arches and arcade kept: holds.
- front_corner holds the whole glass slab, green roof and penthouse: holds.
- Smaller street trees: holds.
- Twin grooved rails at 1495 mm on the pale slab with a single yellow line: holds.
- Span-wire catenary on paired poles, real contact-wire tubes, pantograph touching the wire: holds.
- TTC stop pole: holds.
- Romanesque segmental and round arches, corbelled cornice, central gable: holds (P2 mitre slivers).
- East corner block storefronts on both streets and two skylights: holds (P2 pitch).
- Brick condo wing and charcoal condo with glass-railed balconies: **does not fully hold.** The railings are front-only and the balconies are open at the sides (P1 #2). This was not raised in v002, but it is visible in the v003 pixels.
