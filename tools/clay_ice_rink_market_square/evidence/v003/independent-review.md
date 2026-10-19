# Independent holistic review: clay-ice-rink-market-square v003 (RLASM v6.1)

Reviewer: independent, adversarial. Evidence used: only the pixels of `sources/front.png`, `sources/oblique.jpg`, `sources/top.jpg`, all 18 `renders/*.png` at full resolution, the four phone boards, and zoomed crops written to a new scratch folder (`rink-v003-review-crops-245219150`). I did not use builder notes, metadata, counts or hashes as proof.

## 1. Verdict

**VISUAL_REWORK_REQUIRED** — the v002 chalet-spacing, tree-foliage and side-view tree-cropping defects are fixed in the pixels, but four P1s remain: cube "baubles" on the hero tree, a front view that still lacks the source's garlanded handrail and east chalets, an aerial camera that hides a whole long row of chalets behind the near frontage, and a west town front that is blank above its second storey.

Counts: P0 = 0, P1 = 4, P2 = 9

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | christmas_tree, front, left_side, right_side, rear, rear_side, rear_north, ice_surface, interior | Every tree ornament is an axis-aligned cube. In christmas_tree the red and gold "baubles" are 40-50 px dice or gift boxes. Several pairs interpenetrate (gold and red cubes fused at about (745-785, 95-160), (690-755, 540-590) and (1000-1085, 560-610)). The "lights" are small cream cubes. At medium distance the tree reads as studded with blocks. The source tree (front, oblique) is densely covered in round baubles and warm point lights. | The ornament primitive is a cube (or a very low-segment primitive with flat shading). Placement jitter has no minimum spacing between ornaments. | Replace the ornaments with UV spheres or icospheres (at least 12x8 segments, smooth-shaded) at 0.25-0.35 m. Make the lights small emissive-palette spheres. Enforce a minimum centre-to-centre spacing of at least the sum of the radii. Roughly double the light count so the tree reads lit, as in the source. |
| 2 | P1 | front | The camera move worked: the tree is left of centre, the boards run up the right and the penguin is unclipped. But the right-hand boards show only a bare timber rail over glass. The garland can be seen only as faint red smudges through the glass (crop front_right), because it is mounted on the outer (deck) face. The east chalets show only as small gable tips at the right edge (about 1210-1440, 520-650), roughly 10% of frame height. The source's signature right foreground is a lush garland with red baubles along the handrail, with the east chalets large behind it (x 800-1024, y 180-550). | The board garland is modelled only on the outside face of the rail. The camera yaw and position keep the east chalet row small and at the edge of the frame. | Drape the garland over the handrail so that it reads from the ice side too: add an inner-face garland run along the top of the glass on the long sides. Then yaw the front camera about 8-12° right, or move it about 1.5 m closer to the east boards, so that boards, garland and chalets fill the right quarter of the frame, as in the source. |
| 3 | P1 | aerial | The near (south-east) context frontage and its roof hide the entire near long row of six chalets and the near long side of the boards. In the near short row only 3 of 4 chalets are visible, and about a third of the rink is behind the roof (crop aerial_market). The subject also takes up under 10% of the frame. This is an occluded-target camera. | The camera elevation is too low for the frontage height, and it is placed outside the context ring. | Raise the aerial to a 45-55° depression angle and dolly in until the near eave line falls below the near long row of chalets, or hide or section the near frontage for this view. Check that all 20 chalets and the full board loop are visible. |
| 4 | P1 | front, right_side, facade_close | The west town front (salmon) has only two rows of windows at ground and first floor. Above them is a blank band about two storeys high, up to the eave (crops rs_salmon, front_left). In the front view this blank wall fills most of the left third of the frame. The other three frontages carry windows up to the eaves, and the source's west fronts show 4-5 window rows with dormers. | The west-frontage window-row count (or start height) does not match its wall height. This is likely a per-frontage parameter that was not updated when the frontage was raised. | Generate window rows up to the eave on the west frontage, using the same storey pitch as the cream frontages (4-5 rows). Optionally add a dormer row to match the source. |
| 5 | P2 | left_side, right_side, rear_north, rear_side | The tree and star are now fully in frame. But the builder's claim that near roofs sit "at or below the bottom edge" is false: near chalet roofs still fill the bottom 13-18% of left_side and right_side and hide part of the near boards and garland. In rear_side the near west row fills about the left third of the frame. | The camera is not high or far enough for the near-row eaves. | Lower the pitch about 3-4° or raise the camera about 2 m, until the near ridges sit at or below the bottom edge. |
| 6 | P2 | front, ice_surface, glass_close, square_aerial | The skating aid reads as a lantern or bin: stacked octagonal cylinders, a flat white rectangle for a belly, and a block beak. The inverted-L handle bar's right leg ends in mid-air beside the body (crop front_penguin). | It is built from primitives without a penguin silhouette, and the handle has no second attachment point. | Taper the body into a teardrop. Add flippers and a curved belly patch. Anchor both handle legs to the back of the body, or to the base plate. |
| 7 | P2 | front_corner, top | The subject occupies about 10-15% of the frame. Blank, windowless outer faces of the context ring dominate front_corner. The source oblique and top fill the frame with the market. | The cameras are framed to the context bounding box rather than to the square. | Frame to the market and rink with the frontages' inner faces as the border. Or give the outer faces a minimal window grid. |
| 8 | P2 | all whole-envelope views | The town fronts are four uniform bars with identical window grids, no plot rhythm and no dormers. The source has individual houses of mixed colours and heights with dormers. This is acceptable as simplified context but flat. | Each frontage is a single extrusion. | Split each frontage into 4-6 plots with varied heights and colours, and add a dormer row. |
| 9 | P2 | market_chalets, architecture_close | The counter garland bar is shorter than the awning board above it (it starts about 150 px inside the awning end) and stops abruptly in mid-span. | The garland length is set from the opening width, not the awning width. | Make the garland span the full awning width, or end it at the awning returns. |
| 10 | P2 | top, square_aerial | Seen from above, the tree canopy covers the island, so the ring wall and glass ring do not read as a band round the tree. The source top shows a distinct dark ring with glass round the tree. | The lowest skirt radius is close to or above the ring radius. | Reduce the bottom skirt radius to about 85% of the ring's inner radius, or darken the ring cap so it reads as a band. |
| 11 | P2 | facade_close | The "facade" close-up frames the blank brown backs of two near chalets rather than their decorated fronts. | The camera is placed on the lane side of the row. | Put the camera on the deck side, looking at the counters and gables. |
| 12 | P2 | dasher_boards, front | The white boards and the ice are the same value, so the junction between board and ice is barely readable. The deck reads mid-brown rather than the source's dark timber. | Same albedo for the boards and the ice. The deck palette is too light. | Give the ice a faint blue-grey tint, or add a thin kick-plate line. Darken the deck one step. |
| 13 | P2 | top | The market sits north of the square's centre, leaving a large empty field of setts to the south. The source's lanes are tight on all four sides. | The south frontage is placed further out than the others. | Move the south frontage in so the south lane matches the other lanes (about 6 m). |

## 3. Source conformance checklist

| item | status | view(s) used | note |
|---|---|---|---|
| Plan and proportions | conforms | top, square_aerial vs source top | The rounded rectangle has its long axis N-S, length to width about 1.5 (source about 1.47). The tree is just north of the rink centre. |
| Ice | conforms | ice_surface, front | A plain pale clay plane, which is acceptable for clay. Board and ice contrast is low (P2 #12). |
| Dasher boards: board | conforms | dasher_boards, glass_close | Low white board, continuous round the corners. |
| Dasher boards: glass | conforms | glass_close, front | Clear panels with a slight tint. Garland baubles show through. |
| Dasher boards: posts | conforms | glass_close, dasher_boards | Dark posts at regular centres. |
| Dasher boards: rail | deviates | front, rear_side | The timber rail is present, but its garland is on the outer face only, so it cannot be seen from the ice in the front view (P1 #2). |
| Deck | conforms (tone deviates) | top, rear_north | A timber band round the boards on all sides. It is lighter than the source (P2 #12). |
| Tree island: ring wall | conforms | ice_surface, front | A low white ring wall. |
| Tree island: glass ring | conforms | ice_surface, left_side | Glass with posts. From above it is hidden by the canopy (P2 #10). |
| Tree island: tree | conforms | christmas_tree, front, top | Layered drooping skirts with serrated tips in two greens. No pinwheel and no soil seen from above. |
| Tree island: ornaments | deviates | christmas_tree, front | Cubes instead of round baubles, some interpenetrating, and too sparse (P1 #1). |
| Tree island: star | conforms | front, rear, rear_north | An extruded gold five-point star, fully in frame in every whole view. |
| Chalets: count and arrangement | conforms | top, square_aerial, front_corner | 4 on each short side and 6 on each long side, 20 in total. They are free-standing with sett gaps, and their gables face the ice. |
| Chalets: walls | conforms | market_chalets, facade_close | Dark timber boxes. The backs are plain, as in the source. |
| Chalets: counters | conforms | market_chalets, architecture_close | Projecting counter shelf with an open service opening that has visible depth and returns. |
| Chalets: awnings | conforms | market_chalets | A projecting board over the opening. The garland under it is short (P2 #9). |
| Chalets: snowy roofs | conforms | top, square_aerial, architecture_close | Thick white roof slabs with a timber ridge board on every roof. The ridges read from above. |
| Chalets: garlands | conforms | market_chalets, architecture_close | Rake garland under the roof edge with lights, a bow at the apex and a wreath on the gable. |
| Benches | conforms | dasher_boards, square_aerial | Timber seats on dark supports, on the ice by the boards, as in the source front. Contact is good. |
| Skating aid | deviates | front, ice_surface | Present and unclipped, but it reads as a lantern and has a floating handle leg (P2 #6). |
| Setts | conforms | market_chalets, facade_close | Staggered cross joints are visible. |
| Lamps | conforms | front_corner, square_aerial, right_side | Dark posts with lantern heads at the lanes. |
| Town fronts | deviates | front, right_side | Uniform bars. The west front is blank above the 2nd storey (P1 #4, P2 #8). The south frontage closes the square. |
| Materials hierarchy | conforms | all | Dark timber chalets, white snow and boards, green garlands, red and gold accents, grey setts, cream and salmon fronts. The source palette order is kept. |

## 4. Camera validity

- **aerial**: invalid as a whole-envelope view. The near frontage roof hides the near long row of 6 chalets, one short-row chalet and about a third of the rink (P1 #3).
- **front**: valid and legible, but the source's right-hand foreground is still missing (P1 #2).
- **front_corner, top**: the target is legible but small (about 10-15% of the frame) inside the context ring (P2 #7). Nothing is clipped.
- **left_side, right_side, rear, rear_north**: the whole tree and star are in frame. Near roofs still intrude 13-18% at the bottom edge (P2 #5).
- **rear_side**: the star is about 8 px from the top edge (tight but not clipped). The near west row fills about the left third of the frame (P2 #5).
- **interior**: legible. The counter and awning frame a slot view of the boards, island and tree. This is acceptable for an interior.
- **facade_close**: legible but aimed at the backs of the chalets (P2 #11).
- **christmas_tree, market_chalets, architecture_close, dasher_boards, glass_close, ice_surface, square_aerial**: valid.

## 5. Previous-version (v002) findings: resolution in the pixels

1. **Chalets eave to eave, long-row roofs overlapping like shingles, short rows reading as one slab, no gaps or ridges**: **RESOLVED.** In top (crops top_market, top_northrow) every chalet is a separate roof with a clear strip of setts between neighbours and a visible ridge line. square_aerial and front_corner show free-standing huts, each with a timber ridge board.
2. **Tree as a smooth cone, flat plank branches, bottle brush from the side, 12-spoke pinwheel with soil from above**: **RESOLVED for the foliage.** The tree reads as overlapping drooping skirts with serrated tips in two greens (christmas_tree, front). From above it is a serrated green disc with ornaments and no soil (crop top_tree). A new ornament defect replaces it (P1 #1).
3. **left_side, right_side, rear and rear_north cropping the upper third of the tree and the star; near roofs filling 20-25%**: **RESOLVED for the tree and star crop** (fully in frame in all four). **PARTIALLY RESOLVED for the near roofs**: still 13-18% at the bottom of left_side and right_side, not "at or below the bottom edge" as claimed (now P2 #5).
4. **Front camera mid-rink, tree dead centre, about 45% empty ice, no right-hand boards, garlanded handrail or east chalets, skating aid clipped**: **PARTIALLY RESOLVED.** The camera is now on the ice by the east boards. The tree is left of centre, the boards run up the right and the skating aid is whole. **Not resolved**: the garlanded handrail does not read from the ice, and the east chalets are reduced to small gable tips at the frame edge (P1 #2).

Cheap P2 claims checked: the rake garland under the roof edge, apex bow under the roof edge, counter garland on the awning's front edge (but short, P2 #9), wider tree island, wider lanes, south frontage, staggered sett joints and window surrounds are all **seen in the pixels**. The skating aid now has a body, head, belly, beak and handle, but **still reads as a lantern, with a floating handle leg** (P2 #6).
