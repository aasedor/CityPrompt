# Independent holistic review: clay-rail-through-truss v005 (RLASM v6.1 architectural clay)

Reviewer: independent, no relationship with the builder. I judged only the rendered pixels against the locked source pixels. I opened all 18 renders at full resolution, the three locked sources (sources/front.png, sources/oblique.jpg, sources/top.jpg) and the four phone boards. Zoomed crops and dark-pixel scans are in `/tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/railtruss-v005-indep-crops-116683888/`. Luminance is L = 0.299R + 0.587G + 0.114B.

## 1. Verdict

**PASS_ZERO_P0_P1**: the deck view can now be read and the bowstring no longer has black panels or wedges. The long riveted latticed steel arch viaduct on columns over a street with a red cycle lane, the open-topped bowstring end span, the twin tracks and the silver train on the east track all match the sources. What remains is polish.

Counts: P0 = 0, P1 = 0, P2 = 9

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P2 | aerial, facade_close, front_corner | Thin crevice lines of 1 to 3 px reach L < 10 where bowstring members meet: about 120 px in the aerial bowstring zone and 23 px in facade_close (2 px at L < 3, at about x611-641, y501-603). These are contact-shadow lines along member junctions, not panels or wedges, and they do not read as holes. Because of them, the brief's literal test that no bowstring pixel is black is not met at the single-pixel level. | Ambient-occlusion or contact shadow in narrow gaps between the gusset, vertical and diagonal at the first panel points. | Close the small gaps of about 5 to 10 mm between the gussets and members, or add a little world or fill light. Optional. |
| 2 | P2 | facade_close | At the second vertical of the west truss, the upper and lower riveted gussets are two separate plates. They sit on slightly different planes and step past each other at mid-height, so the joint reads as two loose patches rather than one built-up panel point. | The top-chord gusset and the bottom-chord gusset are authored on different offsets. | Put both gussets on the same face offset, or join them into one full-height plate as was done at the end-panel verticals. |
| 3 | P2 | column_base | The base-shoe gusset is a skewed plate whose lower corner sticks out past the column base plate. The rib end plate at the cap meets the column cap as a tilted slab. Both look like loose plates. These are the "not changed" items. | The gusset is rotated with the rib-springing angle instead of following the column face. | Align the gusset to the column flange and clip it to the base-plate footprint. |
| 4 | P2 | column_base, street_under, architecture_close | The column shafts have built-up flanges and batten bands but no rivet rows at all. The source front shows dense rivet lines on every column. | Rivets were placed only on the ribs, chords and cap girders. | Add two rivet rows per flange at the existing rib rivet pitch. |
| 5 | P2 | arch_span, lattice_detail, front | The ribs and girders carry sparse single rivet dots. In the source the ribs and girders have dense paired rivet rows. | Rivet pitch was deliberately left unchanged. | Halve the pitch on ribs and girders if budget allows. |
| 6 | P2 | track_deck, left_side, right_side | The deck is a continuous smooth grey plate with the sleepers sitting on it. The source oblique and top views show an open-deck track with dark gaps between the sleepers. | The deck plate is modelled as a closed slab. | Darken the inter-sleeper band, or recess the deck between the stringers under each track. |
| 7 | P2 | glass_close, train_cars, rear_north | Below the car-end skins, the underframe gap between cars is pure black (568 px at L < 3 in glass_close, about y830-870). The end skins and silver corner posts are correct; the black is below the body line. | Unlit underframe cavity and the shadow under the car body. | Give the underframe a dark-grey clay tone of about L 40 and a short end sill plate. |
| 8 | P2 | all whole-envelope views | The steel is a cool blue-grey. The source steel is a warmer green-grey or olive-grey. | Palette choice. | Shift the steel hue slightly toward green-grey. |
| 9 | P2 | track_deck, rear, rear_north | The deck and both tracks stop abruptly in the sky at the north end bent, with no end treatment. | The run length and the north end bent were deliberately left unchanged. | Optional: a low end curb or bumper line at the deck edge. |

There are no P0 or P1 findings.

## 3. Source conformance checklist

| Item | Status | View(s) used |
|---|---|---|
| Plan and proportions | conforms. The viaduct runs straight along the west edge of the street, with the footway or plaza strip under it and a tree row on the west footway. Its plan position relative to the road and cycle lane matches the top source. The span-to-height ratio and the column height relative to pedestal height match the front source. | top vs top, aerial, front vs front |
| Span count and rhythm | conforms. A long, regular run of equal arch spans springs from columns at every bent, and the arcade continues under the bowstring with an intermediate column. | front, right_side, rear_side, aerial, front_corner |
| Arch ribs and lattice | conforms. The ribs are solid riveted plate ribs with flanges, with no lattice inside the rib. The spandrel lattice is continuous with 11 posts and diagonals from springing to springing. The rib crown sits about 0.35 to 0.4 of the rise below the girder, and nothing laps into the girder. | arch_span, lattice_detail, architecture_close |
| Columns and pedestals | conforms in form: built-up steel columns with batten bands sit on square concrete pedestals with good ground contact. Columns lack rivets (P2 #4) and the shoe gusset is skewed (P2 #3). | column_base, street_under, front |
| Deck and tracks | conforms. The braced deck has edge railings and twin tracks with sleepers and rails, legible at detail scale. The deck finish is closed (P2 #6). | track_deck, left_side, right_side |
| Bowstring end span | conforms. In each girder plane there is a heavy, low, open-topped riveted arched truss with its crown near the car roof line. It has deep chords, verticals, X diagonals and counters, riveted gussets, solid end-panel plates and no overhead struts. Deck arches with spandrel lattice continue beneath it. | front_corner, aerial, top, facade_close, rear_side |
| Train | conforms. A silver multi-car train runs on the street-side (east) track. It has recessed windows with set-back glazing, recessed door leaves, inset end skins and silver corner posts. | front_corner, aerial, top, right_side, left_side, rear_north, glass_close, train_cars |
| Street, cycle lane and footways beneath | conforms. A two-lane road with a centre dash, a red cycle lane on the viaduct side, a curb strip, a paved footway under the viaduct and a footway on the far side. | front, street_under, top, rear |
| Context | conforms. Simplified brick apartment blocks with flat roofs, parapets and rooftop units, framed windows with no black corner dots, and street trees. | aerial, top, front, arch_span |
| Materials hierarchy | conforms with a P2 caveat: grey steel, light concrete pedestals, a brick context, a dark asphalt road, a red cycle lane, brown sleepers, dark rails and a silver train. The steel hue is cooler than the source (P2 #8). | all |

## 4. Camera validity

- track_deck: **valid**. The camera stands above the deck between the two tracks and looks north. The deck, sleepers, rails, both tracks and both edge railings are clearly legible. The minimum L across the whole frame is 29.3, with zero pixels below 20.
- facade_close: **valid**. It is now a bowstring close-up of the west truss's inner face at the south end panels. The arched top chord, bottom chord, end-panel plate, gussets, verticals and X counters are all legible. The shoe itself is just below the frame edge (acceptable).
- column_base, street_under, arch_span, lattice_detail, architecture_close, glass_close, train_cars, rear_north: valid. Each target is in frame and legible, and nothing is clipped.
- front, front_corner, aerial, top, left_side, right_side, rear, rear_side: valid. The whole envelope is legible, nothing occludes it, and the bowstring end span is visible in front_corner, aerial, top and rear_side.
- No view is occluded, clipped or illegible.

## 5. Previous-version findings: are they resolved in the pixels?

**v004 P0: track_deck entirely black, camera inside the last car.** **Resolved.** track_deck now shows the deck from above between the tracks, looking north, with full luminance range (min L 29.3, mean 120.9, no pixels below 20). The deck, sleepers, rails, both tracks and the edge railings are inspectable.

**v004 P1: pure-black wedges and panels with rivet dots on a black field, on the inner faces of the bowstring end panels (front_corner, aerial, top).** **Resolved.** At the end-panel verticals I now see one riveted gusset per face, and the end panel between the shoe and the first vertical is a solid grey riveted plate (facade_close, front_corner, aerial, top). I scanned the dark pixels in the bowstring zones:
- front_corner: there are 0 pixels below L 3. The L < 10 cluster at x920-1035, y620-690 is contact shadow on the deck under the train skirt, not the truss.
- top: 5 px at L < 10.
- aerial: about 120 px at L < 10, all in 1 to 3 px crevice lines at member junctions.

No black wedge, panel or rivets-on-black field remains. The residual crevice lines are recorded as P2 #1.

**Bowstring a heavy, low, open-topped riveted arched truss with deep chords, verticals, diagonals, counters and gussets and no overhead struts (v003 P1).** Holds (front_corner, aerial, top, rear_side, facade_close).

**Plate-rib deck arches with spandrel lattice continuing under the bowstring to riveted columns on pedestals, with a transverse portal at the intermediate column pair, and an end bent that is not a gantry (v003 P1).** Holds. In front_corner, deck arches with lattice run under the bowstring to the intermediate column, and the south end bent is a closed riveted cap girder on two columns with the deck-arch rib springing from it. The transverse members show only obliquely (street_under) and there is no X-bracing.

**Train on the street-side (east) track, and no black corner dots on the context window frames.** Holds. The train is on the east track in top, aerial, front_corner, right_side, left_side and rear_north. The window frames are clean in arch_span and front.

**Solid riveted plate ribs with flanges and rivet rows and no lattice inside the rib (v001 P1-1).** Holds (arch_span, lattice_detail).

**Open bents with a riveted transverse portal arch, no X-bracing and the footway open beneath (v001 P1-2).** Holds as far as visible (street_under, rear_north, column_base): the footway is open and there is no X-bracing.

**Real window openings with set-back glazing and recessed door leaves (v001 P1-3).** Holds (glass_close, train_cars).

**Closed riveted cap girders at the end bents and the bowstring bent, with no black voids (v001 P1-4).** Holds (rear_north, front_corner, rear).

**Rib crowns about 0.4 of the rise below the girder, with a continuous eleven-post spandrel lattice and nothing lapping into the girder (v002 P1-1).** Holds. arch_span shows 11 posts and a crown gap of about 0.35 to 0.4 of the rise.

**Car end skins inset between the sides, with silver corner posts and no black strips (v002 P1-2).** Holds at body level (glass_close). The pure-black underframe gap below the body line is recorded as P2 #7.

**Unchanged items (rib facets and rivet pitch, base-shoe gusset and rib end plate, run length, door-window recess and gangway, top camera pitch, north end bent).** These look unchanged and introduce no new P0 or P1 defects. Polish notes are in P2 #3, #5 and #9.
