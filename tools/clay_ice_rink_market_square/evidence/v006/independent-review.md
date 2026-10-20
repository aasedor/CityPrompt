# Independent holistic review: clay ice rink market square, v006

Reviewer: independent RLASM v6.1 holistic reviewer (not the builder).
Evidence used: `sources/front.png`, `sources/oblique.jpg`, `sources/top.jpg`; all 18 `renders/*.png` at full resolution; `boards/phone-01..04`. I made zoomed crops into a new folder of my own (`rink-v006-review-crops-eae1d7ca` under the scratchpad). I treated metadata and the builder's notes as claims, not proof.

## 1. Verdict

**VISUAL_REWORK_REQUIRED**: the plan, rink, boards, tree island and the 4/6/6/4 chalet ring all conform, and every earlier fix still holds. One P1 from v005 is only partly fixed. The outward gables now carry garland, lights and a bow, but the outer side-eave garland is tucked under the snow-slab overhang. As a result it does not show in any elevated view, and from the high oblique (square_aerial) the rear-facing chalets still read as plain white-roofed brown sheds. The locked oblique shows a lit garland outlining every roof edge.

Counts: P0 = 0, P1 = 1, P2 = 8

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | square_aerial, rear_north, left_side, rear_side (facade_close only partly) | Seen from above or behind, no garland or lights show along any long side eave of the 20 chalets. Each long eave is a bare white snow-slab edge over a brown wall. In square_aerial the rear-gable garland is a hairline green sliver with pin-point lights, and the apex bow is a 2-3 px red fleck (zoomed: the south row and west row from behind). In the locked oblique, every chalet's long eaves and rear rakes carry a thick lit green garland that reads plainly from the same high angle, with a red bow at each outward apex. The 10 chalets seen from behind therefore still read as undecorated sheds in the matched high oblique role. Up close (facade_close) the rear-gable rake garland, cube lights and red apex block do now show, so that part of the v005 fix is real. | The new garland was placed "just inside the eave edge", under the roof slab's overhang and thickness. From any camera above eave height the slab hides it. The rear-rake garland is also thinner than the slab edge, so it shrinks to a sliver at aerial scale. | In the shared chalet module, move the side-eave garland outboard and down so it hangs on the outer face of the eave fascia, proud of the slab edge by about 0.1 m and at least as deep as the slab edge, with warm lights on its outer and upper faces. Do the same for the rear-rake garland. Enlarge the rear apex bow to about the rink-side bow's size so it reads from square_aerial. Re-check in square_aerial, rear_north and front_corner. |
| 2 | P2 | rear_side, rear, left_side (handrail) | The extra warm lights on the ice side of the handrail garland read from elevated views as cream specks hovering about 0.2 m off the garland, over the ice (rear_side near corner, rear south rail). From eye level (dasher_boards, glass_close) they sit on the garland. | Light instances are offset outward from the garland's ice face, not seated on it. | Pull the ice-side light offset in so each light touches the garland face. |
| 3 | P2 | christmas_tree, front, ice_surface | Several neighbouring red and gold baubles at the tree silhouette pass into each other (paired spheres overlapping on the left and right edges). None are buried in the skirt any more. | Pushing baubles outward made some tip positions collide. | Add a minimum spacing between baubles, or drop the second bauble where two tips coincide. |
| 4 | P2 | facade_close | The outward gable has a bow but no small wreath or gold ornament beneath it. The oblique shows one under several rear bows. | Rear-gable decoration set is reduced. | Optionally add a small wreath or ornament under the rear bow. |
| 5 | P2 | front, left_side, right_side, rear | Town fronts are four uniform continuous slabs with one roofline, regular window grids and no dormers or mansards. The sources show varied five-to-six-storey fronts with dormer roofs. Acceptable as simplified context. | Context kept deliberately minimal. | Optional: vary eave heights per bay and add dormer boxes on the roofs. |
| 6 | P2 | front_corner, aerial, top | The square fills only about 35-40% of the frame, with a large empty grey ground plane, so chalet and garland detail is illegible at this scale. The top view also shows a wide empty south strip of setts compared with a tight north strip. The image is legible and nothing is clipped. | Envelope cameras framed for the whole frontage ring plus margin. | Optional: tighten the framing to the frontage ring. |
| 7 | P2 | architecture_close, market_chalets, facade_close | Chalet timber is a mid warm brown, a little lighter and redder than the dark-stained timber in the oblique and top sources. | Palette value. | Darken the chalet wall colour one step. |
| 8 | P2 | front, ice_surface | The penguin skating aid is a black octagonal body with a white belly, an orange beak and a handle on a yellow skid. From the front camera at distance it reads as a lantern or bin rather than a penguin. | Simplified massing. | Optional: add a rounded head and flipper bumps. |

The christmas_tree detail view crops off the star and the base. As a mid-tree detail that is acceptable, and the whole tree and star are held in front, left_side, right_side, rear, rear_side and rear_north, so it is not counted.

## 3. Source conformance checklist

| item | status | view used |
|---|---|---|
| Plan and proportions (rounded-rectangle rink, long axis N-S, ratio about 1.5, ring of chalets, frontage ring) | conforms | top vs top.jpg; aerial; front_corner |
| Ice (flat pale surface, rounded corners) | conforms | ice_surface, top, front |
| Dasher boards: white board | conforms | glass_close, dasher_boards |
| Dasher boards: clear glass panels | conforms | glass_close, dasher_boards, interior |
| Dasher boards: dark posts | conforms | glass_close, rear_corner crop |
| Dasher boards: timber handrail with garland, continuous round corners, baubles and lights on both faces | conforms (P2 #2 on ice-side light seating) | rear, square_aerial, rear_side, dasher_boards |
| Dasher boards: dark kick-plate at the ice line | conforms | glass_close, dasher_boards, front |
| Deck (dark timber round the boards, no pad past the chalet line) | conforms (chamfered corners; source corners read square but are hidden by chalets) | top, square_aerial, rear_north |
| Tree island: ring wall | conforms | ice_surface, front |
| Tree island: glass ring | conforms | ice_surface, interior |
| Tree island: tree (layered drooping fir skirts, two greens, no soil from above) | conforms | christmas_tree, top crop, front |
| Tree island: ornaments (red and gold baubles, warm light on bough tips) | conforms (P2 #3 overlaps) | christmas_tree |
| Tree island: star (crossed solid prisms on a gold stem, solid from every side) | conforms | front, left_side, right_side, rear, rear_side, rear_north (star crops) |
| Tree island position (just north of rink centre) | conforms | top |
| Chalets: count and arrangement (4 N, 6 W, 6 E, 4 S, separate, about 1 m of setts between eaves) | conforms | top, front_corner, aerial |
| Chalets: walls (dark timber boxes) | conforms (P2 #7 tone) | architecture_close, facade_close |
| Chalets: counters (open hatch with depth, back wall, floor, projecting counter, facing the ice) | conforms | market_chalets, architecture_close |
| Chalets: awnings (flap with green garland beam) | conforms | market_chalets |
| Chalets: snowy roofs with ridge board | conforms | all views |
| Chalets: garlands, rink-facing gable (garland, lights, wreath, apex bow) | conforms | market_chalets, architecture_close, glass_close |
| Chalets: garlands, outward gable (rake garland, lights, bow) | deviates in elevated views (P1 #1); conforms at close range | facade_close vs square_aerial |
| Chalets: garlands, side eaves | deviates (P1 #1); not legible in any view | square_aerial, rear_north, left_side, rear_side |
| Benches | conforms (on the ice by the boards, as in the source front) | dasher_boards, top, square_aerial |
| Skating aid (penguin) | conforms (P2 #8 legibility) | ice_surface, front |
| Setts (cobbled square) | conforms | facade_close, architecture_close, square_aerial |
| Lamps | conforms | square_aerial, rear, left_side, ice_surface |
| Town fronts (simplified context, window rows up to the eaves on every front) | conforms as simplified context (P2 #5) | front, front_corner, left_side, rear_north |
| Materials hierarchy (white ice and boards, clear glass, dark posts, timber rail, green garland, red and gold ornaments, dark timber deck and chalets, white snow, grey setts, render fronts with terracotta roofs) | conforms | all |

## 4. Camera validity

- No view has its target occluded, clipped or illegible in a way that makes it invalid.
- front: the whole tree, the gold star and sky are in frame. The garlanded east boards and the east chalet row form the right-hand foreground, and the west row now shows to the left of the tree. Valid.
- front_corner, aerial and top: whole envelope, all 20 chalets and the whole rink inside the frontage ring. Valid, but small in frame (P2 #6).
- left_side, right_side, rear, rear_side and rear_north each hold the whole tree and star. Valid.
- christmas_tree: a mid-tree detail that crops off the star and base. Acceptable for a detail; the tree's completeness is shown elsewhere.
- interior: from inside a chalet, looking past the counter and awning beam to the boards and the tree island. Valid and legible.

## 5. Previous-version findings: are they resolved in the pixels?

| v005 finding or builder claim | resolved? | evidence |
|---|---|---|
| **P1: outward rear gables and outer eaves bare (no garland, lights or bow)** | **Partly. Still P1.** | facade_close: both foreground chalets now show a green rake garland with cube lights and a red apex block, so the rear gable is fixed up close. But the side-eave garland is hidden under the slab overhang in every elevated view, and in square_aerial the 10 rear-facing chalets show only hairline green slivers and red flecks. They still read as undecorated against the oblique. See finding #1. |
| P2: front camera yawed so the west row shows to the left of the tree | Resolved | front: two west-row chalets with wreathed gables sit left of the tree; the east row is still the right-hand foreground. |
| P2: dark kick-plate at the foot of the boards | Resolved | glass_close, dasher_boards, front: a continuous dark band marks the board-to-ice line. |
| P2: deck darkened and corners chamfered to the chalet line | Resolved | top, square_aerial: dark timber deck with chamfered corners, nothing past the chalet ring. |
| P2: more warm lights on the ice-side face of the handrail garland | Resolved, with a new P2 | Lights are present on the ice side, but from elevated views they look detached (finding #2). |
| P2: tree baubles pushed out past the bough tips | Resolved, with a new P2 | None are half-buried in the skirt; some adjacent baubles now overlap (finding #3). |
| Earlier fix: whole tree, star and sky in the front frame; garlanded boards and east row as right-hand foreground | Holds | front |
| Earlier fix: star as two crossed solid prisms on a gold stem | Holds | Star crops from front, left_side, right_side, rear, rear_side and rear_north: solid from every side, seated on the leader tip. |
| Earlier fix: handrail and garland as one continuous loop with no black wedge gaps | Holds | rear and square_aerial corner crops, rear_side |
| Earlier fix: round red and gold baubles with a warm light on every bough tip; garland on the handrail reads from the ice and the deck with baubles and lights on both faces | Holds | christmas_tree, dasher_boards, glass_close, rear_side |
| Earlier fix: high aerial shows the whole rink and all 20 chalets inside the frontage ring; window rows up to the eaves | Holds | aerial, front_corner, front, left_side |
| Earlier fix: separate chalets about 1 m apart with ridge boards; rink-facing gables with garland, lights, wreath and apex bow | Holds | top, square_aerial, market_chalets, architecture_close |
| Earlier fix: tree as layered drooping skirts in two greens with no soil from above; side and rear views hold the whole tree and star | Holds | christmas_tree, top crop, left_side, right_side, rear, rear_side, rear_north |
