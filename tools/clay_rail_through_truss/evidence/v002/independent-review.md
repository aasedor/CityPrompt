# Independent holistic review: clay-rail-through-truss v002 (RLASM v6.1)

Reviewer: independent; did not build this candidate. Judged only rendered pixels against the locked source pixels (sources/front.png, sources/oblique.jpg, sources/top.jpg). I opened all 18 renders and the 4 phone boards. Zoomed crops (no other file touched) are in `/tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/rt2-review-crops-bf7fa887/`.

## 1. Verdict

**Verdict: VISUAL_REWORK_REQUIRED.** v002 fixes the v001 rib type, the trestle X-bracing, the front_corner voids and the train openings. Two P1s remain. The spandrel lattice, an identity element, has shrunk to a single haunch bracket because every rib crown is pushed into the deck girder. Every car end also shows a full-height black slot at the side-to-end corner.

Counts: P0 = 0, P1 = 2, P2 = 9

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | arch_span, lattice_detail, facade_close, front, right_side, architecture_close (vs source front) | **What the source shows:** each span is a riveted plate rib under a deep, continuous open spandrel lattice. The lattice is a band of 4 to 6 vertical posts per half-span with V/N diagonals meeting at gussets on the rib. It runs right over the crown, where a crown gusset and a full-height post rise to the girder. At the crown the lattice is about half the rib rise deep (see the src_front_spandrel crop). **What the render shows:** the rib extrados runs straight into the underside of the plate girder over roughly the middle half of every span. In lattice_detail and facade_close the extrados flange laps onto the girder face, and seat blocks are pasted across the junction. The "lattice" is one short post, one diagonal and a horizontal strut at each haunch (arch_span: blocks at x≈200/370 and 1060/1230 only). The view named lattice_detail shows almost no lattice. Each span reads as a knee-braced portal with an arched soffit, not as a latticed-spandrel arch. | The fix for v001 P1-5 overcorrected. The rise was raised to a near-semicircle from a 6 m springing until the crown met the girder, and that left no spandrel depth at the crown for the lattice the brief describes. | Lower the rib crown, either by reducing the rise or lowering the springing relative to the girder, so the crown sits about 0.4 to 0.5 × rise below the girder underside. Then fill the whole spandrel from springing to springing with evenly spaced vertical posts (about 5 per half-span, one on the crown with a crown gusset) and N/V diagonals falling toward the crown, with gussets at the rib and at the girder. Remove the pasted crown seat blocks. Re-render arch_span, lattice_detail, facade_close and front. |
| 2 | P1 | glass_close, train_cars, left_side, right_side, aerial (every car end) | A solid black vertical strip, roughly 3 to 5 % of car length wide, runs the full height of the body from underframe to roof at the corner where each car's side meets its end face. It shows on both cars at every coupling (crops gc_carend, ls_carend). It reads as an open seam or exposed void, not as a gangway or diaphragm. A gangway would sit centred on the end face; here the end faces are blank silver. | The new dark interior core is wider than the silver skin's end returns, or the side skin stops short of the end panel, so the core shows through at the corner. | Wrap the silver skin around each corner: extend the side panels to meet the end panels, or close the end panel to the full body width. Keep the dark core only behind real openings. If a gangway is wanted, model a centred recessed gangway door or diaphragm on the end face. Re-render glass_close and train_cars. |
| 3 | P2 | arch_span, architecture_close, facade_close, lattice_detail | Rib intrados and extrados are still visibly polygonal (straight facets catch the light along the curve). | 16 segments are too few at close-up distance. | Use 32 to 48 segments, or a smooth-shaded bevel on the curve. |
| 4 | P2 | arch_span, column_base, street_under | Rivets are sparse single dots spaced widely on the ribs. The columns show no rivet rows or flange-plate seams, unlike the heavily riveted columns in the source. | Rivet instancing applies to the ribs only, at a coarse pitch. | Tighten the rib rivet pitch and add rivet rows to the column flange edges and the girder stiffeners. |
| 5 | P2 | column_base | The base-shoe gusset is a single tilted wedge plate standing proud of the column face. Its foot touches the base plate only at a point, so it reads as loose. | The gusset is rotated or offset from the column face and not seated on the base plate. | Seat the gussets flush on all four column faces, with their feet fully on the base plate. |
| 6 | P2 | facade_close (far-plane rib), lattice_detail | Hairline black slivers remain between the far-plane rib extrados and the girder either side of the crown seat (crop fac_farcrown). | The rib-to-girder contact is still approximate; the seat blocks hide the gap only near the crown. | Resolved together with #1. Otherwise extend the extrados flange to bear fully on a girder bottom flange. |
| 7 | P2 | arch_span, facade_close, column_base, left_side | Context window frames still have black corner dots (unchanged from v001). | Corner pieces of the window frames use a dark material or are missing faces. | Give the frame corners the frame material. |
| 8 | P2 | track_deck, front_corner, rear_north, aerial | The deck is a solid pale plate between the tracks (unchanged). The run is short, about 9 to 10 deck spans plus the bowstring, against more than 14 visible in the source oblique, and the tracks stop dead at the end-bent caps (unchanged). | Accepted carry-overs. | Optionally add open ties over stringers or a darker ballast and deck tone, a few more spans, or a fade-out or approach at the ends. |
| 9 | P2 | glass_close, train_cars, left_side, top | The door windows are flat darker panels with no recess. The car ends show no gangway door. The body has no lower fluting. The top camera is about 50° oblique, while the source is near-nadir (the bearing now matches). | Detail and camera simplifications. | Recess the door glazing; add an end gangway door; optionally raise the top camera pitch. |

## 3. Source conformance checklist

| Item | Status | View used | Note |
|---|---|---|---|
| Plan and proportions | conforms | top, aerial, rear_side vs source top/oblique | Viaduct runs SW-NE over the west promenade, with the cycle lane, road and east footway beside it. The bowstring is at the SW end. Bay height-to-width is close to the source front. |
| Span count and rhythm | conforms (short run, P2) | front, rear_side, right_side | The rhythm is regular and the bays match the source. The run is shorter than the source (finding #8). |
| Arch ribs and lattice | **deviates (P1 #1)** | arch_span, lattice_detail, facade_close vs source front | The single solid plate rib now conforms. The spandrel lattice is reduced to haunch brackets and the crown runs into the girder. |
| Columns and pedestals | conforms | front, street_under, column_base | Tall built-up columns stand on pale concrete pedestals, with capital and shoe details. Riveting is sparse (P2 #4) and the shoe is loose (P2 #5). |
| Deck and tracks | conforms (P2 #8) | track_deck, right_side, top | Plate-girder fascia with stiffeners and railings, and twin tracks with sleepers. The deck plate is solid and pale. |
| Train | deviates (P1 #2) | glass_close, train_cars, left_side | A silver multi-car train with recessed window openings and door leaves. Black slots show at every car-end corner. |
| Street, cycle lane and footways beneath | conforms | front, street_under, rear_north | The red cycle lane runs beside the road and a paved promenade runs open beneath the viaduct. The bents no longer block the footway. |
| Context | conforms (P2 #7) | aerial, front, left_side | Brick mid-rise apartment blocks with punched windows, flat roofs with rooftop boxes, and street trees. |
| Materials hierarchy | conforms | all | Grey-green steel, pale concrete pedestals, brick context, red cycle lane, dark asphalt and a silver train, all in the source palette. |

## 4. Camera validity

No view is invalid. Every whole-envelope view (front, front_corner, aerial, top, left_side, right_side, rear, rear_side) frames the viaduct without occluding or clipping the target. front_corner now includes the end-bent pedestals; left_side is clear of the west roofs; front reads as an elevation rather than a soffit; top matches the source bearing, though at a more oblique pitch (P2 #9).

All detail views are legible. lattice_detail is framed correctly, but it shows how little lattice there is (evidence for P1 #1, not a camera defect). track_deck shows no train, which is acceptable because its subject is the deck.

## 5. Previous-version (v001) findings: resolved in the pixels?

| v001 finding | Status in v002 pixels |
|---|---|
| P1: double-chord trussed arch ring with lattice inside, only short posts above; source has a solid riveted plate rib plus open spandrel lattice of posts and N-diagonals | **Partly resolved.** The rib is now a single solid plate rib with flanges, so the rib part is fixed. The spandrel lattice is still not delivered: only one post and diagonal per haunch, and the crown runs into the girder. Carried forward as P1 #1. |
| P1: full-height X-bracing in every transverse bent, trestle look, blocked footway | **Resolved.** The X-bracing is gone. Transverse portal arches with head girders sit high between the paired columns, and the promenade is open (street_under, architecture_close, front). |
| P1: train had no window openings (flat band, proud door plates) | **Resolved for openings.** Windows are recessed with visible returns and the door leaves are recessed. A new defect is visible: black slots at the car-end corners (P1 #2). The door windows are still flat (P2 #9). |
| P1: black voids or missing faces where the through-arch truss and deck end met the end cap (front_corner) | **Resolved.** The closed cap girders seal the column tops and deck ends; no voids are visible in front_corner (crop fc_endbent) or rear_north. |
| P1: crown not seated on the deck (dark slit; neighbouring rib segments poking into the girder) | **Resolved on the near plane, overcorrected.** There is no slit on the near-plane ribs, but the extrados now laps into the girder over the middle of the span. Hairline slivers remain on the far plane (P2 #6), and the geometry change causes P1 #1. |
| P2: no rivet rows, base shoes or capitals | Partly resolved. The ribs carry sparse rivets and shoes and capitals are present. Column rivets are missing and the shoe is loose (P2 #4, #5). |
| P2: faceted ribs | Not resolved; still visibly faceted (P2 #3). |
| P2: heavy overhead struts closing the through-arch into a tunnel | Resolved; two slender struts near the crown (front_corner, aerial). |
| P2: black corner dots on context window frames | Not changed (P2 #7). |
| P2: solid pale deck | Not changed (P2 #8). |
| P2: short run | Not changed (P2 #8). |
| P2: front_corner clipping end-bent pedestals | Resolved. |
| P2: top not matching source bearing | Resolved for bearing; the pitch is still more oblique (P2 #9). |
| P2: left_side blocked by a foreground roof | Resolved. |
| P2: front soffit-dominated | Resolved. |
