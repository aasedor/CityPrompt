# Independent holistic review: clay ice rink market square, v004

Reviewer: independent, adversarial. I compared the pixels of the 18 renders and 4 phone boards with the three locked sources (front.png, oblique.jpg, top.jpg). I made zoomed crops only in a new folder: /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/rink-v004-crops-42d0db2e.

## 1. Verdict

**VISUAL_REWORK_REQUIRED**: the four v003 P1s are fixed in the pixels, but three new P1s block production approval. The matched front view cuts off the tree's star, the gold star floats clear of the spire tip in every view that shows it, and the dasher-rail garland shows pure-black wedge gaps at every segment joint round the rink corners.

Counts: P0 = 0, P1 = 3, P2 = 12

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | front (also phone-01 "Render front") | The tree runs off the top edge of the frame. The green spire tip touches y≈0 and the gold star is not in the image. In the locked front the full tree, the star and clear sky above it are inside the frame (star at about 12% of the frame height). This is the matched hero view, and its main identity element is clipped. | The camera was moved onto the ice near the south-east boards to fix v003 finding 2, but the pitch and focal length were not re-checked against the tree height. The camera is too close or too level for a tree about 18 m high. | Keep the camera position and the east-row composition. Tilt up by about 4–6°, or widen the lens slightly, so the star and about 5% sky margin sit inside the frame. Re-check that the right-hand chalets still run large. |
| 2 | P1 | rear, rear_north, rear_side, left_side, right_side (crops rear_star2, rn_star, ls_star, rsd_star) | The gold star hangs in mid-air. A clear band of sky or façade separates the star's lower points from the spire apex, about 4–6 px at full resolution, so the star does not touch the tree. From east and west (left_side, right_side) the star is a flat plate seen edge-on. It reads as a thin gold sliver that floats, not as a star. | The star's origin or z-offset is above the spire apex, and the star is a single flat extrusion that faces only north and south. | Lower the star until its bottom point sits on the spire apex, or add a short gold stem or finial into the tip. Make it a two-sided or 3D star (two crossed plates, or an extruded star with bevel) so it reads from the east and west views. |
| 3 | P1 | rear_side, rear, rear_north, square_aerial, front_corner, market_chalets (crops rs_corner, mc_garland) | The garland on top of the dasher handrail is a chain of straight green boxes round each rounded corner. Each joint leaves a triangular wedge of pure black (RGB 0,0,0 sampled in market_chalets). There are about 8–10 black notches per corner, and in market_chalets two large black slashes fill the foreground. This is a clear finish defect on an identity element, and it is visible in whole-envelope views. | Straight garland segments are placed on a polygonal approximation of the corner radius with no mitre or overlap. The open box ends or back faces show through as black. | Sweep the garland as one continuous profile along the rail curve, or mitre or overlap each segment by its half-width. Close the end caps and make the normals consistent. Re-render rear_side and market_chalets to confirm there is no black left. |
| 4 | P2 | christmas_tree, front, ice_surface | Baubles are round now but visibly low-poly (about 10–12 facets in the close view). The "warm lights" are cream rotated cubes that read as studs or diamonds, not small lamps. Ornaments are still somewhat sparser than the source's dense baubles and glow. | Low sphere segment count. The lights have no emission and use a cube primitive. | Raise the sphere segments, use small spheres or a soft emissive warm material for the lights, and add about 30% more lights. |
| 5 | P2 | front, ice_surface, interior, rear (crops front_island, interior_island) | Seen through the tinted glass ring, the lowest tier of baubles hangs below the bottom skirt tips. At the base of the planter they read as a loose ring of balls with no boughs visibly above them. | The "hang under bough tip" offset is applied to the lowest skirt as well, which sits behind the glass below the rim. | Skip or raise the baubles on the lowest skirt so they sit at or above the glass rim. |
| 6 | P2 | glass_close, dasher_boards, front, interior | The dasher garland is a smooth flat slab with a square section, not a lush bough garland. Chalet wreaths are 12 blocky segments with a cube bow. | Box primitives. | Use a rounded or scalloped garland profile, and a torus wreath with a simple bow. |
| 7 | P2 | front, glass_close, dasher_boards | The glass panels read smoky grey and the posts read heavy black. The source shows clear glass with slim posts. | Glass tint and transmission settings, and post width. | Lighten the glass tint and slim the posts slightly. |
| 8 | P2 | front (crop front_aid), right_side | From behind, the penguin skating aid reads as a black lantern or bin with a handle frame. It reads as a penguin only from the side and from above. | Simplified cylinder body with no head or flipper silhouette. | Add a rounded head and flipper bumps to the black body. |
| 9 | P2 | front_corner, aerial, left_side, right_side, rear | The town fronts are four identical, uniform slabs with a repeated window grid, no dormers, one eave height and two colours. The source has varied coloured fronts (red, ochre, cream, salmon), dormers, chimneys and varied heights. This is acceptable as simplified context, but it is monotonous. | One façade module repeated round the ring. | Split each side into 3–5 fronts with varied colour, eave height and a dormer row. |
| 10 | P2 | front_corner, aerial, top (phone-01, phone-04) | The whole-envelope frames include the full frontage block on large empty grey ground, so the rink assembly is small. On the phone board the top view's rink is only about 13% of the frame width, while the locked top and oblique frame tight on the rink. | The framing targets the frontage bounds, not the rink and chalets. | Frame top and front_corner to the chalet ring plus the street margin. |
| 11 | P2 | square_aerial, top, rear_north | The deck reads mid-brown to tan, lighter than the source's dark timber. In the top view the tree canopy covers the whole planter ring, while the source shows the ring rim and a dark planter band round the canopy. | Deck albedo, and the canopy radius roughly equal to the ring radius. | Darken the deck albedo. Shrink the lowest-skirt radius about 10%, or enlarge the ring, so the rim shows from above. |
| 12 | P2 | market_chalets | The camera stands right behind the dasher garland, which fills the bottom ~18% of the frame (and carries the black wedges from #3). | Camera too close to the rail. | Move the camera about 1 m back onto the deck, or raise it so the rail drops out of the frame. |
| 13 | P2 | oblique vs aerial/front_corner | The source's angled north-east corner chalet and the small fenced enclosure at the south-east corner of the deck are not modelled. All 20 chalets sit in straight rows. | Simplification. | Optional: rotate the north-east corner chalet about 30–45°, and add a low fence at the south-east deck corner. |
| 14 | P2 | ice_surface, front | The ice is uniformly flat grey-white, with none of the source's soft skate-scuff variation. This is clay, so it is polish only. | Single flat material. | Optional: add a subtle value variation or a scuff overlay. |
| 15 | P2 | architecture_close, market_chalets | The chalet ridge board stops slightly past the gable apex, and a small dark notch shows between the ridge board and the snow slab at the gable. | Ridge-board length and offset. | Trim the ridge board flush with the bargeboard, or cap the apex. |

## 3. Source conformance checklist

| Item | Status | View used / note |
|---|---|---|
| Plan and proportions | conforms | top vs top.jpg. A rounded rectangle with its long axis north-south, about 1:1.58 (source about 1:1.47). The tree is slightly north of the rink centre, and the chalet ring is 4 N / 6 E / 4 S / 6 W. |
| Ice | conforms (P2 #14) | top, ice_surface, front. A flat white rounded rectangle with radiused corners. |
| Dasher boards – board | conforms | glass_close, dasher_boards, rear_side. A low white board with a white outer skirt. |
| Dasher boards – glass | deviates (P2 #7) | glass_close, front. Present and continuous, but tinted smoky. |
| Dasher boards – posts | conforms (P2 #7) | glass_close. Evenly spaced posts, slightly heavy. |
| Dasher boards – rail/garland | deviates (P1 #3, P2 #6) | front, glass_close, rear_side. The timber rail and the garland on top now read from the ice and the deck, but there are black wedge gaps at the corners. |
| Deck | conforms (P2 #11) | top, square_aerial, rear_north. A timber band round the boards with the chalets on its outer edge. A little light in colour. |
| Tree island – ring wall | conforms | ice_surface, rear. A low white circular wall. |
| Tree island – glass ring | conforms | ice_surface, interior, front. A glass ring with posts on top of the wall. |
| Tree island – tree | conforms | left_side, rear_north, christmas_tree. Layered drooping fir skirts, conical, about 18 m, with no soil visible from above (top). |
| Tree island – ornaments | conforms (P2 #4, #5) | christmas_tree. Round red and gold baubles under the bough tips and light studs on the tips. No cube "dice" remain. |
| Tree island – star | deviates (P1 #1, #2) | rear_north, left_side, front. Gold five-point star, but it floats above the tip, reads as a flat sliver from E/W, and is clipped out of the front view. |
| Chalets – count and arrangement | conforms | top, aerial, square_aerial. 20 chalets: 4 north, 4 south, 6 east, 6 west. Each is separate, with setts visible between the eaves in top. |
| Chalets – walls | conforms | facade_close, market_chalets. Timber brown boxes with blank backs. |
| Chalets – counters | conforms | market_chalets, architecture_close. A recessed opening with visible depth, interior floor and side returns, and a projecting counter shelf. |
| Chalets – awnings | conforms | market_chalets, architecture_close. A lifted top flap with a green garland bar on its lip, attached at the awning edge. |
| Chalets – snowy roofs | conforms (P2 #15) | facade_close, square_aerial. White snow slabs with overhang, and a ridge board on every roof. |
| Chalets – garlands | conforms (P2 #6) | front (right-hand row), glass_close, market_chalets. Green fascia garlands with light studs, a red bow at the apex and a wreath on each rink-facing gable. |
| Benches | conforms | dasher_boards, top, rear. Timber-top benches on dark legs at the ice edge, on the ice as in the locked front. Contact is clean. |
| Skating aid | conforms (P2 #8) | square_aerial, ice_surface. A penguin pusher on a yellow base. It reads poorly from behind in front. |
| Setts | conforms | facade_close, square_aerial. A dark grey cobbled grid over the whole square. |
| Lamps | conforms | left_side, rear_north, square_aerial. Simple lamp posts round the square margin, consistent with the street lamps in the oblique source. |
| Town fronts | deviates (P2 #9) | right_side, rear, front. Window rows run to the eaves on every front, and the west (salmon) front now carries three rows. They are uniform and repetitive compared with the source. |
| Materials hierarchy | conforms | All views. White ice and boards, a timber deck and chalets, green garlands and tree, red and gold accents, white snow roofs, dark setts and cream or salmon fronts. This follows the source palette order. |

## 4. Camera validity

- **front**: the asset is clipped. The top of the tree and the star are cut off by the top edge of the frame (P1 #1). Everything else is legible: the tree on the left, the east chalet row running large down the right, and the garlanded handrail.
- **market_chalets**: a foreground occluder (the dasher garland, with black artifacts) fills the bottom ~18% of the frame. The chalet is still fully legible (P2 #12).
- **front_corner, aerial, top**: the target is valid and unoccluded, but small within the frame (P2 #10). All 20 chalets, the rink, the deck and the tree are legible.
- **interior**: valid. The view looks out from inside a chalet over the counter to the boards and the tree island. The awning garland crosses the top of the frame but does not hide the target.
- All other views (left_side, right_side, rear, rear_side, rear_north, facade_close, architecture_close, glass_close, christmas_tree, dasher_boards, ice_surface, square_aerial) are valid. The side and rear views hold the whole tree and star in frame; in rear_side the star is close to the top edge but inside.

## 5. Previous-version (v003) findings: are they resolved in the pixels?

1. **Tree ornaments as axis-aligned cubes reading as dice or gift boxes, red and gold cubes interpenetrating, sparse compared with the source.** RESOLVED. christmas_tree, front and left_side show round red and gold baubles under alternate bough tips, smaller ones on the upper skirts, and a light stud on every tip. No cubes or interpenetrating ornament pairs remain. Some baubles are partly hidden behind a bough tip, which reads as natural occlusion. Residual polish only: faceting, unlit lights, and density somewhat below the source (P2 #4, #5).
2. **Front-view handrail bare from the ice (garland on the deck face), and east chalets only as small gable tips at the right edge.** RESOLVED. In front, a green garland with red baubles runs along the top of the handrail down the right of the frame, and the east chalet row with wreathed gables runs large down the right, matching the source's right-hand foreground. The camera change introduced a new defect, the clipped star (P1 #1).
3. **Aerial camera too low: the near south-east frontage hid the near long row, one short-row chalet and about a third of the rink.** RESOLVED. aerial now looks down at roughly 50°. The whole rink, the deck, the tree and all 20 chalets (6 + 6 + 4 + 4) read inside the frontage ring, with no frontage occlusion.
4. **West (salmon) front with only two window rows and a blank two-storey band up to the eave.** RESOLVED. right_side and rear show the salmon front with three window rows (the lowest with doors) running up to just below the eave. Every other front also carries window rows up to its eave.

v003 fixes that had to keep holding:
- Separate chalets with about 1 m of setts between the eaves: **holds** (top, facade_close).
- A ridge board on every roof: **holds** (facade_close, square_aerial, architecture_close).
- The tree as layered drooping fir skirts in two greens, no soil from above, and a gold star: **holds, except that the star now floats clear of the tip** (P1 #2). The top view shows canopy only, with no soil.
- The side and rear views hold the whole tree and star: **holds** (left_side, right_side, rear, rear_side, rear_north).
