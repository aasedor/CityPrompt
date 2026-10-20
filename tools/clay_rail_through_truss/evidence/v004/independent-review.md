# Independent holistic review: railtruss v004 (RLASM v6.1, architectural clay)

Reviewer: independent; judged only on rendered pixels against `sources/front.png`, `sources/oblique.jpg` and `sources/top.jpg`. I opened all 18 renders, the 3 sources and the 4 phone boards. Zoomed crops are in `/tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/rt-v004-crops-d09344e5/` (a new folder; nothing in the candidate was modified).

## 1. Verdict

**VISUAL_REWORK_REQUIRED**: the rebuilt bowstring now reads correctly as a low, open, heavy arched truss over a continuing arcade, but the `track_deck` detail view is a fully black frame, and the bowstring trusses show pure-black voids at their end panels in three whole-envelope views.

Counts: P0 = 1, P1 = 1, P2 = 12

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P0 | track_deck (also the phone-03 board) | The whole 1440x1080 frame is black: every channel is 0 to 1 and the mean is 0.4, so nothing is legible. The deck, ties, rails, both tracks and the deck edge cannot be inspected at detail scale, so the deck-and-tracks detail check fails. | The camera sits inside or under a closed solid (most likely inside the solid deck plate, the train body or a cap girder), or it faces a back face with no light reaching it. | Move the `track_deck` camera above the rail top (for example 2 to 3 m above the deck, beside the west track, looking along it at about 30 degrees down). Check that the frame is not near-black (mean above 40), then re-render and rebuild board 03. |
| 2 | P1 | front_corner (about px 968,745 and 1110,715), aerial (about px 45,815 and 135,885), top (about px 455,750 and 560,795) | Pure-black wedges and panels (luminance 0) sit on the inner face of both bowstring arched trusses at the end panels next to the springing and bearing shoes. Some show rivet dots on a black field. At normal viewing size they read as holes in the truss. This is the same class of defect as the black voids v001 P1-4 removed from the cap girders. | A gusset or shoe plate with inverted normals, or with a near-black or unassigned material, or an open end on the built-up chord or shoe box that exposes an unlit inside. | Give the shoe and end-panel gusset plates the steel material and outward normals, and cap any open chord or shoe ends. Re-render front_corner, aerial and top, and confirm that no pixel on the bowstring falls below the shaded-steel range (about luminance 25 or more). |
| 3 | P2 | arch_span, facade_close, lattice_detail | The deck-arch ribs show visible polygon facets (18 segments) along their curves. | The segment count was cut for the size cap. | Use 24 or more segments, or smooth the shading on the rib faces. |
| 4 | P2 | arch_span, lattice_detail, column_base | Rivets are sparse (about a 2 m pitch on the ribs), and the column shafts and plates have no rivet rows. The source shows dense rivet fields on columns, ribs and gussets. | The rivet pitch was relaxed for the size cap. | Add a rivet row or normal-map strip on the column flanges, and tighten the visible rib rivet pitch to about 1 m. |
| 5 | P2 | column_base | A tilted base-shoe gusset plate stands off the column face with a gap at its foot. It floats and does not bear on the shoe. | The plate is mis-rotated or offset from the column face. | Make the plate flush with the flange and seat it on the base plate. |
| 6 | P2 | column_base (top of frame) | A rotated rib end plate pokes through the top of the column cap. | The rib end block intersects the cap. | Trim the rib end so it seats on the cap face, or hide it inside the cap. |
| 7 | P2 | facade_close, lattice_detail, architecture_close | The lattice post heads are plain rectangular boxes under the girder, not riveted gusset plates. | Box primitives are used as gussets. | Use thin plates with chamfers and rivets. |
| 8 | P2 | left_side, right_side, front_corner, rear_north | The deck is a solid, pale, uniform plate. In the source the deck is darker steel, with stringers and ties reading between the rails. | Simplified deck. | Darken the deck to the steel tone, and show stringers or tie gaps between and outside the rails. |
| 9 | P2 | front, aerial, rear_side, top | The run is short: about 8 arcade spans plus the bowstring. The source viaduct recedes for dozens of spans. | Length was limited for the size cap. | Extend with instanced spans, or fade the run into distance context. |
| 10 | P2 | glass_close, train_cars | The car door windows are flat, painted-on rectangles with no recess, and there is no gangway between cars. | Same as v003; not changed. | Recess the door glazing by 20 to 30 mm, and add a simple gangway bellows block between cars. |
| 11 | P2 | top | The top camera is at about 50 degrees. The locked top source is steeper and frames the viaduct diagonally with the street beside it. | Same as v003; not changed. | Raise the pitch to about 65 to 70 degrees and match the diagonal framing. |
| 12 | P2 | rear_north, rear | The north end bent is a straight two-column portal with a flat cap girder and no transverse portal arch. The interior bents and the south end bent have the riveted portal arch. No source shows this face, but it breaks the visible bent grammar. | The termination bent was not given the portal arch. | Add the same transverse riveted portal arch under the north cap girder. |
| 13 | P2 | (coverage) all detail views | No detail view frames the rebuilt bowstring. Its rivets, gussets and shoes can only be judged from aerial distance. | The view list predates the bowstring rebuild. | Add a `bowstring_close` detail view of one girder-plane truss at its shoe and first two panels. |
| 14 | P2 | facade_close, glass_close (context windows) | The context glazing has a faint swirl or streak texture. This is minor and does not read as a defect at whole-envelope scale. | A procedural glass shader. | Use flat glass. |

The table's P2 rows (3 to 14) are the 12 P2 findings.

## 3. Source conformance checklist

| Item | Status | View(s) used | Note |
|---|---|---|---|
| Plan and proportions | conforms | top, aerial, rear vs source top/oblique | Order matches the top source: viaduct on its footway between the west brick blocks (with trees) and the east street. Width and height read right against the 4 to 5 storey context. |
| Span count and rhythm | conforms (rhythm) / deviates (count, P2 #9) | right_side, front, rear_side | The arcade rhythm is regular and runs on under the bowstring (two spans per plane on the intermediate bent). The run is short. |
| Arch ribs and lattice | conforms | arch_span, facade_close, lattice_detail, front | The ribs are solid flanged plate with no internal lattice. The crown sits about 0.35 to 0.4 of the rise below the girder, with a continuous 11-post spandrel lattice, matching source front. Finish deviates (P2 #3, #4, #7). |
| Columns and pedestals | conforms (form) / deviates (finish) | column_base, street_under, front | Built-up columns sit on concrete pedestals with transverse portal arches. There are no rivets, the gusset floats and a plate pokes through the cap (P2 #4 to #6). |
| Deck and tracks | deviates | left_side, right_side, rear_north; track_deck **not visible (black)** | Both tracks and the railings read correctly in the envelope views. The deck plate is pale and solid (P2 #8). The deck detail view is invalid (P0 #1). |
| Bowstring (south end) | conforms (form) / deviates (finish) | front_corner, aerial, top, rear_side vs oblique/top | It is a heavy arched truss in each girder plane, with the crown at about car-roof height, open above (no overhead struts), and the deck arcade continuing below. It has black voids at the end panels (P1 #2). |
| Train | conforms | left_side, right_side, front_corner, aerial, top, rear_north, train_cars | Silver-white cars on the street-side (east) track, as in the sources. The car end skins are inset with silver corner posts. Door glazing is flat and there is no gangway (P2 #10). |
| Street, cycle lane and footways beneath | conforms | front, street_under, top, rear | The paved footway runs open beneath the bents, the red cycle lane runs along the viaduct side, then the carriageway with dashed centre line, then the far footway. |
| Context | conforms | aerial, right_side, facade_close | Simplified brick blocks with flat pale roofs and plant boxes. The window frames are a single plate with no black corner dots. |
| Materials hierarchy | conforms | all | Blue-grey steel, pale concrete pedestals, brick context, silver-white train, red lane, dark asphalt and pale paving. The deck tone is too pale (P2 #8). |

## 4. Camera validity

- **track_deck: invalid (P0 #1).** The frame is entirely black and nothing is legible.
- top: valid but too shallow (about 50 degrees) for the matched top role (P2 #11).
- All other views (front, front_corner, aerial, left_side, right_side, rear, rear_side, facade_close, architecture_close, glass_close, arch_span, column_base, lattice_detail, train_cars, street_under, rear_north) are valid. The target is legible and not clipped, and no context mass occludes the asset. In front_corner and aerial the near building roofs crowd the left side of the frame, but they do not hide the bowstring.

## 5. Previous-version findings: resolved in the pixels?

| Previous finding | Resolved? | Evidence |
|---|---|---|
| v003 P1: wrong bowstring type (light, tall through-arch on a flat girder over a gantry; nothing arching below; unriveted; crown about one car height above the roofs; overhead struts) | **Resolved as structure type** | front_corner, aerial, top, rear_side show a deep arched top chord in each girder plane with verticals and crossed diagonals and the crown at about car-roof level. There are no overhead struts. The arcade arches with spandrel lattice continue below the deck as two spans per plane on an intermediate bent with a portal arch. The outer end stands on viaduct columns and pedestals, not a gantry. Rivets on the chords are not verifiable at the available scale (P2 #13). New defect: black voids at the end panels (P1 #2). |
| v003 P2: faceted ribs | Not resolved (worse: 22 to 18 segments) | arch_span (P2 #3) |
| v003 P2: sparse rivets, plain columns | Not resolved | column_base, arch_span (P2 #4) |
| v003 P2: loose base-shoe gusset | Not resolved (builder says unchanged) | column_base (P2 #5) |
| v003 P2: rib end plate through a column cap | Not resolved | column_base, top edge (P2 #6) |
| v003 P2: box-like lattice gussets | Partly. The rib-side gussets were removed, but the girder-side box heads remain | facade_close, lattice_detail (P2 #7) |
| v003 P2: black corner dots on context window frames | Resolved | facade_close and right_side crops show a clean single frame plate |
| v003 P2: solid pale deck | Not resolved (unchanged) | left_side, right_side (P2 #8) |
| v003 P2: short run | Not resolved (unchanged) | front, aerial (P2 #9) |
| v003 P2: flat door windows, no gangway | Not resolved (unchanged) | glass_close, train_cars (P2 #10) |
| v003 P2: 50-degree top camera | Not resolved (unchanged) | top (P2 #11) |
| v003 P2: overhead struts on the bowstring | Resolved | aerial, front_corner, top: open above |
| v003 P2: train on the building-side track | Resolved | Train on the east (street-side) track in left_side, right_side, front_corner, aerial, top, rear_north |
| v001 P1-1: solid riveted plate ribs, no lattice inside the rib | Holds | arch_span, facade_close |
| v001 P1-2: open bents with riveted transverse portal arch, no X-bracing, footway open | Holds for interior and south end bents | street_under, column_base, front_corner. The north end bent has no portal arch (P2 #12). |
| v001 P1-3: real window openings with set-back glazing, recessed door leaves | Holds for context windows and car side windows | facade_close, glass_close (car door glazing is still flat, P2 #10) |
| v001 P1-4: closed riveted cap girders at end bents and bowstring bent, no black voids | Holds for the cap girders | rear_north, front_corner. Black voids have reappeared on the bowstring trusses themselves (P1 #2). |
| v002 P1-1: rib crown about 0.4 x rise below the girder, continuous 11-post spandrel lattice | Holds | arch_span: 11 posts, crown about 0.36 of the rise below the girder line |
| v002 P1-2: car end skins inset, silver corner posts, no black strips | Holds | glass_close, train_cars, front_corner (the leading car end is clean) |
