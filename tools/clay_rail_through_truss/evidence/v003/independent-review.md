# Independent holistic review: clay-rail-through-truss v003 (RLASM v6.1 architectural clay)

Reviewer: independent; I did not build this candidate. I judged only rendered pixels against the locked source pixels (sources/front.png, sources/oblique.jpg, sources/top.jpg). I opened all 18 renders and the 4 phone boards at full resolution and made zoomed crops (written only to the new folder `scratchpad/rt3-review-crops-5c672c63/`).

## 1. Verdict

**VISUAL_REWORK_REQUIRED**: the v002 P1s (the lattice that had shrunk to a knee-brace, and the black car-corner strips) are resolved in the pixels. One P1 remains. The bowstring span is the foreground hero of both the oblique and top sources, and the render shows the wrong structure type: a light, tall through-arch on a straight-column gantry. The sources show a heavy riveted arched truss whose arch continues below the deck to columns on pedestals.

Counts: P0 = 0, P1 = 1, P2 = 12

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | front_corner, aerial, top, rear_side, rear (vs oblique.jpg, top.jpg) | The bowstring span stands on a flat deck girder. Its outer end rests on a straight two-column portal with a cap girder, which reads as a gantry. Nothing arches below the deck, so the street-level arcade rhythm stops under it. Its chords and web are thin, unriveted bars, and its crown rises about one car height above the roofs. In both sources this span is a heavy riveted arched truss. The truss plane carries on **below** the deck as an arch rib that springs down to a riveted column on a concrete pedestal (oblique: the column and pedestal just right of centre under the near truss; top: columns on pedestals under the right-hand truss). The chords are deep riveted built-up members, and the arch is low (the crown sits near the car roof line). | The bowstring was modelled as a separate generic tied arch on an end bent. The source's arch-below-deck and pedestal column were not carried into this span. Member sections were taken from a light truss preset. | Below the bowstring deck, add the viaduct's own rib and lattice-spandrel grammar on each truss plane: a solid riveted rib springing from columns on pedestals, with the same 15 m bay rhythm or one long rib, as the source shows. Replace the straight portal legs with the viaduct's column, haunch and pedestal. Deepen the top and bottom chords to built-up riveted sections about 2 to 3 times the current depth, with rivet rows. Lower the arch crown to about car-roof height so it reads as the source's low arched truss. |
| 2 | P2 | arch_span, facade_close, lattice_detail | At close range the rib extrados still shows visible segment kinks (22 segments). | Segment count is capped by the file-size limit. | Use 32 or more segments on the extrados edge only, or add a bevel or smooth-shading normal pass on the rib flanges. |
| 3 | P2 | column_base, architecture_close, street_under (vs front.png) | Rivets are single sparse dots at about 1.6 m pitch. Columns are plain smooth boxes. The source front shows dense double rivet rows on the ribs and riveted batten/cover plates up every column. | Rivet pitch was widened to fit the size cap. Columns were left as plain primitives. | Use instanced rivet strips (a shared mesh) at about 0.4 m pitch on the rib flanges and column edges, and add cover-plate strips to the columns. |
| 4 | P2 | column_base | The trapezoidal base-shoe gusset leans out of the column face. Its lower edge only touches the base plate along one corner, with a shadow wedge under it, so it reads as a loose plate (unchanged from v002). | The gusset is rotated rather than set flush against the column face. | Make the gusset coplanar with the column flange, with its full lower edge seated on the base plate. |
| 5 | P2 | column_base (top of frame) | A flat plate (the rib springing or bracket web) passes through the column cap block at an angle and sticks out above it. | The rib leg's end plate overlaps the cap volume. | Trim the rib leg to end at the cap face, or seat it on a bearing plate. |
| 6 | P2 | facade_close, lattice_detail, arch_span | The lattice gussets are solid cubes hanging below the girder and sitting on the rib, with an extra collar block halfway up some posts. The source shows thin riveted gusset plates. | Gussets are modelled as boxes, not as plates. | Make the gussets thin plates (about 20 mm proud of the web faces) with rivet dots, and remove the mid-post collars. |
| 7 | P2 | front, facade_close, left_side, street_under | Black dots remain at the corners of the context window frames (unchanged). | Frame corner pieces overlap or are degenerate. | Mitre or butt the frame members, or merge the frame mesh. |
| 8 | P2 | track_deck, aerial, right_side | The deck is a solid pale plate. The source shows dark open ties and stringers between the rails. | Unchanged. | Darken the deck plate, or show tie gaps between the rails. |
| 9 | P2 | front, aerial, rear_side | About 9 arch spans plus the bowstring. The source front recedes over 15 or more spans to the horizon. | Unchanged run length. | Extend the run with instanced spans toward the vanishing direction. |
| 10 | P2 | glass_close, train_cars | Door windows are flat painted rectangles. There is no gangway diaphragm between cars (corner posts are present). | Unchanged. | Recess the door glazing 2 to 3 cm and add a simple diaphragm box between car ends. |
| 11 | P2 | top | The top camera is about 50 degrees oblique. The source top is steeper (about 65 to 70 degrees). | Unchanged camera pitch. | Pitch the top camera to about 65 to 70 degrees down. |
| 12 | P2 | aerial, top, front_corner (vs oblique.jpg, top.jpg) | The bowstring has overhead transverse struts crossing above the train. Neither source shows overhead bracing between the two arched trusses (the source reads as open, pony/half-through). | Generic through-arch template. | Remove the overhead struts, or replace them with knee braces below the car roof line. |
| 13 | P2 | top, aerial, right_side (vs top.jpg, oblique.jpg) | The train runs on the building-side track. In both sources it runs on the street-side track, next to the spandrel face. | The train was placed on the wrong track. | Move the train consist onto the street-side track. |

## 3. Source conformance checklist

| item | status | view(s) used | note |
|---|---|---|---|
| Plan and proportions | conforms | top, aerial vs top.jpg | The viaduct runs parallel to the street over a paved strip. Trees sit between the viaduct and the buildings. The red lane, road and far footway are in source order. The deck sits at about 11 to 12 m. |
| Span count and rhythm | deviates (P2-9) | front, aerial, right_side vs front.png | The bay rhythm is even and correct, but the run is short. |
| Arch ribs and lattice | conforms | arch_span, facade_close, lattice_detail, right_side, front vs front.png | Solid plate ribs with flanges and rivets, and no lattice inside the rib. A continuous lattice of 11 posts per span with V-diagonals fills the whole spandrel. A lattice band of about 0.35 to 0.4 times the rise runs over the crown. The crown sits clearly below the girder, and nothing laps into it. Facets and gusset blocks remain P2. |
| Columns and pedestals | conforms (finish P2) | column_base, street_under, front | Concrete pedestals and steel columns are correct in rhythm and contact. The columns are plain (P2-3), and there are the base gusset and cap plate issues (P2-4, P2-5). |
| Deck and tracks | conforms (finish P2) | track_deck, right_side, aerial | Twin tracks with ties and rails, edge railings, and a plate girder edge. The deck plate is pale (P2-8). |
| Bowstring / through-arch span (source foreground) | deviates (P1-1, P2-12) | front_corner, aerial, top vs oblique.jpg, top.jpg | Wrong support form and member weight, and overhead struts. |
| Train | conforms (placement P2) | glass_close, train_cars, aerial, rear_side | Silver-white multi-car consist with recessed windows, recessed doors, end gangway doors and a cab windscreen. There are no black corner strips. It is on the wrong track (P2-13). |
| Street, cycle lane and footways beneath | conforms | front, street_under, right_side, rear_north | Red cycle lane between the road and the footway. The footway under the viaduct is open, with no cross-bracing in the way. |
| Context | conforms | front, aerial, rear | Simplified brick blocks with flat roofs and plant boxes, as clay context. Window corner dots are P2-7. |
| Materials hierarchy | conforms | all | Steel is one blue-grey tone throughout (I sampled the bowstring and viaduct pixels: the difference is lighting only). Pedestals are pale concrete, the context is brick red, the paving is pale grey, the lane is red, and the train is silver-white. |

## 4. Camera validity

All 18 views are valid. In none of them is the target occluded or clipped to the point of being illegible.
- front: the viaduct fills the right half and recedes correctly. The near column is partly cut at the right edge, which is acceptable (the source frames it the same way).
- column_base: the pedestal and column foot are legible. The camera is low and close, which is intended.
- top: legible, but the pitch is shallower than the source (P2-11).
- glass_close and train_cars both frame the train sides and car ends, which is appropriate.
- track_deck: the deck, both tracks and the railings are legible.

## 5. Previous-version findings: resolved in the pixels?

**v002 P1s**
- **P1-1, lattice shrunk to a knee-brace with the crown lapping into the girder: RESOLVED.** arch_span, facade_close, lattice_detail and right_side show a continuous lattice over the whole spandrel: 11 posts per span (one on the crown), with V-diagonals rising from alternate rib nodes. The crown node carries a V. The rib extrados crown sits well below the girder underside, with a full-height post and gussets between them. No seat block remains, and nothing laps into the girder. Each span now reads as a lattice-spandrel arch, not as a portal.
- **P1-2, black strips at car-end corners: RESOLVED.** glass_close and train_cars (the junction between cars), rear_side (the tail car's end face) and aerial/front_corner (the cab end) all show light end faces with a thin silver corner post. I found no black vertical strip. A dark-pixel scan finds near-black only under the cars (bogies and underframe), which is expected.

**v002 P2s**
- Faceted ribs: improved (22 segments), but kinks are still visible close up (P2-2).
- Sparse rivets and plain columns: not resolved (P2-3).
- Loose base-shoe gusset: not resolved (P2-4).
- Hairline slivers at the far-plane crown: not observed in front or arch_span; resolved.
- Black corner dots on context window frames: not resolved, as the builder states (P2-7).
- Solid pale deck: not resolved, as stated (P2-8).
- Short run: not resolved, as stated (P2-9).
- Flat door windows and no gangway: door windows are still flat. End gangway doors are present, but there is no diaphragm (P2-10).
- 50-degree top camera: not resolved, as stated (P2-11).

**Earlier v001 fixes (must still hold)**
- v001 P1-1, solid riveted plate ribs with flanges and rivet rows, no lattice inside the rib: **holds** (arch_span, facade_close).
- v001 P1-2, open bents with a riveted transverse portal arch, no X-bracing, footway open beneath: **holds**. In front and street_under the transverse arch with its lattice is visible under the deck, and the footway is clear.
- v001 P1-3, real window openings with set-back glazing and recessed door leaves: **holds** (glass_close and train_cars show visible reveals at windows and doors).
- v001 P1-4, closed riveted cap girders at the end bents and the bowstring bent, with no black voids: **holds** (rear_north, front_corner). Note that the form of the bowstring support is now raised separately as P1-1.
