# Independent holistic review: road diet complete street, v002

Reviewer: independent RLASM v6.1 holistic reviewer. I did not build this candidate.
Evidence used: the rendered pixels of all 18 renders, the 4 phone boards and the 3 locked sources (front.png, oblique.jpg, top.jpg). I opened every image at full resolution. I made zoomed crops only in a new folder, `/tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/rd2-indep-crops-b17880ae/`. I did not use builder notes, metadata or counts as proof.

## 1. Verdict

**VISUAL_REWORK_REQUIRED**: the section, markings, crossings, islands and street wall now hold, and five of the six v001 P1s are resolved, but in the governing front view and in verge_trees the west-verge cobra-head lamps still read as bare black poles that end inside the tree foliage, with no arm or head visible.

Counts: P0 = 0, P1 = 1, P2 = 8

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | front, verge_trees (the views v001 named) | **The west-verge lamp is still a pole without a head.** In front, the pole at about x 490–510 rises from its base (y ≈ 685) and stops at y ≈ 350, exactly at the lower edge of the nearest verge-tree crown. In verge_trees, the pole at x 490–510 stops at y ≈ 265, also at the nearest crown's underside. In both views no arm and no cobra head are visible. The lamp reads as a black stick going up into the foliage, so the v001 symptom remains in the governing pedestrian view. In the source front, the left lamp shows its pole and bracket against the foliage. The same lamps do read correctly (arm and head clear) from above, in rear, front_corner and aerial. | The lamps were moved midway between trees in plan only. The cobra head is still mounted inside the crown height band (crown base ≈ 42 % of 11.5 m ≈ 4.8 m, top 11.5 m). The crowns are now larger and overlap along the verge, so from a low camera looking along the verge the nearer crown always hides the head and arm. | Make the lamp head readable from pedestrian height. Option A: mount the cobra head below the local crown base (raise the trunk-clear height of the verge trees to about 55 % near each lamp, and put the head at about 6 m on an arm of about 2 m reaching over the bike lane). Option B: pull the road-side lobes of the two crowns next to each lamp back by about 1.5 m, so that a clear slot exists over the curb line at head height. Re-render front and verge_trees, and confirm that the arm and head silhouette show against sky or against a farther crown, not hidden behind the nearer crown. |
| 2 | P2 | refuge_island, crosswalk_zebra, turn_lane, rubber_curb | The grasses are much better than v001's plank-and-cube version, but they are not yet one dense mass. The 16 tussock bases read as separate pale beige lumps, like sandbags, ringed along the bed edge, with brown mulch visible between them. The blades are kinked straight sticks. From above (turn_lane), they splay like a haystack. | The mound bases are oversized, smooth-faceted ellipsoids set in a grid, and each blade is 2 straight segments. | Shrink the mound bases and sink them about 60 % into the bed. Add a low infill blade layer between mounds so no mulch shows inside the curb. Give the blades 3–4 segments with a progressive bow. |
| 3 | P2 | front, verge_trees, aerial, rear_side, rear (tree crop) | The tree crowns are rounded and overlap correctly, but the lobes are visibly low-poly. They show faceted silhouettes and jagged seams where one lobe pokes through another, even though the builder claims they are smooth-shaded. | Low subdivision count on the lobes, and lobe-to-lobe boolean seams are left visible. | Raise the lobe subdivision by one level, or apply true smooth normals. Slightly increase the lobe overlap so the seams fall inside neighbouring lobes. |
| 4 | P2 | bike_symbol (crop) | The bicycle glyph is legible and has no black triangles, but it is malformed. It has a detached pedal stub floating left of the frame, a handlebar stroke that crosses the front wheel, and visible stepped edges where the stacked strokes overlap. | The stroke layout was hand-placed, and the 1.4 mm per-stroke step shows at grazing light. | Snap the pedal stroke to the bottom bracket, and move the handlebar to the head tube. Merge the frame strokes into one flat mesh at a single height (a union, not a stack). |
| 5 | P2 | rubber_curb, front | The new yellow chevrons are present and point toward the crosswalk. Under each post, the post base plate sits on top of a chevron, and the chevrons near the posts show doubled, offset plates. | The chevrons are placed on the same pitch as the post bases, and a second chevron copy overlaps the first. | Space the chevrons between the posts, remove the duplicate chevron instance, and keep each post base on bare black rubber. |
| 6 | P2 | crosswalk_zebra, refuge_island | The far-end keep-right sign on each island shows its back face (the pole is in front of the plate), with a faint ghost of the arrow visible through it. | The sign plate is single-thickness and the arrow geometry bleeds through, or the back face uses the front material. | Give the plate a plain grey back face, and offset the arrow so it does not show from behind. Alternatively, turn the far-end sign to face the opposing traffic. |
| 7 | P2 | bike_lane_separator, rubber_curb, front | The placeholder car wheels are thin black boards standing outside the body side. The cabin and roof are now correct. | The wheel blocks are placed outside the body footprint. | Inset the wheel blocks so they sit under the body sill, half hidden. |
| 8 | P2 | brief view list vs renders/ | The brief's detail list names facade_close, architecture_close and glass_close, but those files do not exist. The folder holds the stated 18 views. The facade evidence is covered by storefronts and corner_signal, so this is a bookkeeping mismatch only. Separately, in left_side and right_side the nearest cross-street tree fills about the right third of the frame, but the target remains legible. | The view-list template is out of sync with the render set. The foreground tree sits close to those camera positions. | Remove the three names from the view list, or render those views. Optionally move the left_side and right_side cameras about 3 m inward. |

## 3. Source conformance checklist

| Item | Status | View(s) used |
|---|---|---|
| Section order from the west: (lawn, sidewalk,) grass verge with trees and lamps, curb, green bike lane, raised separator, travel lane, centre turn lane, travel lane, separator, green bike lane, east sidewalk, storefronts | conforms | front, verge_trees, bike_lane_separator, turn_lane, top |
| Section widths and proportions: bike lanes narrow, travel lanes about equal, centre lane slightly narrower; matches source top proportions | conforms | top vs source top, turn_lane |
| Green paint extent: continuous along both main-street lanes and cross-street curb lanes, interrupted only under the crosswalk stripes, not painted through the intersection box | conforms | top, front, bike_symbol, crosswalk_zebra |
| Raised separators with white delineator posts on both sides of the main street, stopping before each crosswalk | conforms | bike_lane_separator, rubber_curb, top, rear |
| Rubber curb stops in the gap between separator end and crosswalk: black, yellow chevrons, three posts | conforms (P2 #5 chevron stacking) | rubber_curb, front, bike_symbol, top |
| Centre-lane yellow lines: solid outer and dashed inner on both edges of the TWLTL | conforms | turn_lane, rear, front |
| Opposing white left-turn arrows: correct directions for northbound and southbound, no black overlap triangles | conforms | turn_lane, rear, top (crops) |
| Refuge islands in the centre lane just beyond each main-street crosswalk: curb, straw grass planting, keep-right sign with black arrow, yellow-and-black object marker | conforms (P2 #2 grass form, P2 #6 back face) | refuge_island, crosswalk_zebra, front, top, aerial |
| Continental zebra crosswalks on all four legs, spanning the bike lanes | conforms | top, aerial, crosswalk_zebra, corner_signal |
| Stop bars: main street on the approach side of the crosswalks (southbound north leg, northbound south leg); cross street on both approaches | conforms | top, refuge_island, left_side |
| Cross-street dashed yellow centre line | conforms | cross_street_lane, left_side, right_side, top |
| Cross-street hatched painted buffers with posts and green curb-side lanes | conforms | cross_street_lane, left_side, right_side, top |
| White bicycle symbols on all green lanes | conforms (P2 #4 glyph form) | top, bike_symbol, turn_lane, cross_street_lane |
| Signal poles with mast arms and three-lamp heads at the four corners | conforms | corner_signal, aerial, top, left_side |
| Black cobra-head lamps | **deviates** in the pedestrian views: west-verge heads and arms are hidden by crowns in front and verge_trees (P1 #1). They conform in rear, front_corner and aerial, and the east lamps conform everywhere | front, verge_trees, rear, front_corner |
| Mature west-verge street trees: tall, rounded, dense crowns hanging low and overlapping along the verge | conforms (P2 #3 faceting) | front, front_corner, aerial, rear_side, verge_trees |
| East trees in pits, crowns clear of the facades | conforms | top (crop), corner_signal, rear, right_side, cross_street_lane, storefronts |
| Bins and bike racks on the east sidewalk | conforms | storefronts, crosswalk_zebra, front_corner |
| Storefront row: brick ground storey, large shopfront glazing with transoms and doors, dark sign band, cream upper storey, brick pilasters, sash windows, coping | conforms | storefronts, corner_signal, rear, cross_street_lane |
| Four-storey brick apartment block with balconies, further north on the east side | conforms | front, front_corner, aerial, bike_lane_separator |
| South-east beige stucco two-storey block | conforms | aerial, right_side, rear_side |
| West blocks: two-storey brick office and one-storey block, set back behind lawns | conforms | aerial, left_side, verge_trees, rear_side |
| Context massing: plain blocks beyond | conforms | aerial, rear_side, front_corner |
| Materials hierarchy: terracotta brick, cream render, dark sign band and glass, pale concrete, dark asphalt, muted green paint, yellow/white markings, straw grasses | conforms | all |

## 4. Camera validity

- No view is invalid. Every target is legible, nothing important is clipped, and nothing is fully occluded.
- front: valid, and it follows the brief's top-view-governed placement (camera at the intersection looking north). The canopy fills the top-left, as in the source. Note that this is the view where the lamp head is hidden (P1 #1, an asset/placement defect, not a camera defect).
- bike_lane_separator: the near car is cut by the right frame edge, but the separator and posts are fully legible.
- left_side / right_side: a foreground tree takes about the right third of the frame. The cross street, buffers, lanes and crossings remain legible (P2 #8).
- The other 13 views (front_corner, aerial, top, rear, rear_side, verge_trees, refuge_island, crosswalk_zebra, bike_symbol, turn_lane, storefronts, corner_signal, cross_street_lane, rubber_curb) are clear and correctly targeted.

## 5. Status of the v001 findings (checked in the pixels)

| v001 finding | Status in v002 pixels | Evidence |
|---|---|---|
| 1. Verge trees were flat-bottomed slabs on Y-forks (parasol underside) | **Resolved.** The crowns are rounded, multi-lobe masses with lobes hanging below the forks. The underside seen from pedestrian height is lumpy, not a flat plane. The crowns overlap from tree to tree along the west verge. Residual low-poly faceting is logged as P2 #3. | front, verge_trees, front_corner, aerial, rear_side |
| 2. Cobra-head lamp arm buried in the canopy (front, verge_trees) | **Not resolved in the named views.** In front and verge_trees, the pole still ends at the nearest crown's underside, with no arm or head visible. It is resolved only in the elevated views (rear, front_corner, aerial), where the arm and head are clear. Retained as P1 #1. | front, verge_trees (crops), front_corner, rear |
| 3. East-sidewalk and corner tree canopies cut through the facades | **Resolved.** In top view the crown edges stop short of the east and cross-street building lines. In the perspective views the crowns sit in front of the facades without cutting into them, and the sash windows are intact. | top (crop), corner_signal, rear, right_side, cross_street_lane, storefronts |
| 4. Refuge-island grasses were planks in green cubes on bare soil | **Largely resolved.** There are no cubes or planks and no bright green; the island reads as dense straw grasses at normal viewing distance. In close-up there are residual sandbag-like mound bases with mulch between them, and kinked straight blades (P2 #2). | refuge_island, crosswalk_zebra, turn_lane, rubber_curb |
| 5. Car cabins transparent, roof floating | **Resolved.** The cabins are an opaque grey volume, and the roof slab rests on and overhangs the cabin. | turn_lane, rubber_curb, bike_lane_separator, front |
| 6. Black triangles at overlapping marking strokes | **Resolved.** There are no black triangles in the bicycle symbols or the turn-arrow elbows. Glyph malformation is logged as P2 #4. | bike_symbol, turn_lane, rear, top (crops) |
| Cheap P2: yellow chevrons on the rubber curb stops | **Done.** Chevrons are present and point toward the crosswalk. There is a stacking artefact under the post bases (P2 #5). | rubber_curb, front |

Things v001 got right still hold: the lane order and widths, both separators with white posts, the solid and dashed yellow TWLTL with opposing arrows, continental crosswalks on all four legs, planted refuge islands with keep-right signs and object markers beyond each main-street crosswalk, the cross street's dashed centre line, hatched buffer with posts and green curb lanes, the corner mast arms, the brick-and-cream storefront row, the four-storey brick apartment block, and the set-back west blocks.
