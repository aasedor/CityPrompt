# Independent holistic review: clay-ice-rink-market-square v005 (RLASM v6.1)

Reviewer: independent, not the builder. I looked at the three locked sources (front.png, oblique.jpg, top.jpg), all 18 renders at full resolution, the four phone boards, and zoomed crops I made into a new scratch folder (`rink-v005-review-crops-703525255`). I did not use metadata, counts, hashes or builder notes as evidence.

## 1. Verdict

**VISUAL_REWORK_REQUIRED**: the v004 P1s are fixed in the pixels, and the plan, rink, tree island and 20-chalet ring now match the sources. One P1 remains: every chalet's outward-facing gable and outer eaves are bare brown boxes. The locked oblique shows a lit garland on every eave and a red bow on every outward gable apex.

Counts: P0 = 0, P1 = 1, P2 = 8

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | facade_close, square_aerial, front_corner, aerial, rear_side, left_side, right_side (foreground chalets) | The rink-facing gable of each chalet has a garland fascia, warm lights, a wreath and an apex bauble. The outward-facing rear gable and both outer eave lines have none of them: no garland, no light strand, no red bow. facade_close (the close-up facade view) shows two plain brown boxes under snow plates with only a ridge board. In square_aerial the 10 chalets seen from behind (west and south rows) read as undecorated sheds. In the locked oblique, the south row seen from outside (crop of x100-650, y540-860) has a green garland with warm lights along every eave and a red bow at the apex of every outward gable. | The chalet module puts its decoration only on the counter (rink-facing) gable. The rear gable and side eaves were never given the trim. | In the shared chalet module, mirror the existing eave garland fascia and light strand onto the rear gable rakes and run it along both side eaves. Add a red bow (the same red as the front apex bauble) at the rear gable apex. One module change carries to all 20 instances. Then re-check facade_close and square_aerial. |
| 2 | P2 | front | The tree sits at the left edge of the frame and hides the west chalet row. In the source front the west row is a lit band in the left mid-ground beside a centre-left tree. | Camera yaw is slightly too far east. | Yaw about 3-5° west so the west row shows to the left of the tree, keeping the east row as the right foreground. |
| 3 | P2 | front, dasher_boards, glass_close, ice_surface | The white board face and the white ice merge, so the board-to-ice contact line is barely readable. | Board and ice share almost the same value and there is no base trim. | Add a thin darker kick-plate or base line at the ice, or lower the board value slightly. |
| 4 | P2 | front_corner, aerial, square_aerial | The deck reads as pale tan at aerial scale, not the dark timber of the sources. Square deck pads also stick out past the chalet ring at the corners (most visible SW). | Deck albedo is too light, and the corner fill rectangle is oversized. | Darken the deck to the source dark-timber tone and trim the corner pads to the chalet line. |
| 5 | P2 | front, left_side, right_side, rear, front_corner, aerial | The town fronts are four uniform monolithic blocks: one height, one window type, a continuous roof, no dormers and no house divisions. The outward walls are blank, and the gable ends overlap at the ring corners. | The context is deliberately simplified. | Optionally split each front into 3-5 house bays with varied eave heights and dormers. Add window rows on the outward faces, or hide them from the aerial cameras. |
| 6 | P2 | dasher_boards, glass_close, front | The garland's ice-side face shows red baubles but few warm lights, with long runs that have no lights. | The light spacing on the inner face is sparse. | Halve the light spacing on the ice-side face to match the deck side. |
| 7 | P2 | christmas_tree, front | Several baubles are half buried in the drooping skirts and read as flat red or gold crescents. | Bauble placement intersects the skirt geometry. | Push the baubles outward along the bough normals until they are fully visible, or cull the intersecting ones. |
| 8 | P2 | front, ice_surface, square_aerial; top | The penguin skating aid reads as a black lantern on a stand. The chalet-and-rink ensemble sits in the north part of the square with a large empty south plaza. The top view frames the square small, with wide grey margins. | The skating aid is abstracted too far. The plan offset and the top-camera framing are as built. | Give the skating aid a head and beak silhouette. Optionally centre the ensemble north-south and tighten the top framing. |

## 3. Source conformance checklist

| item | status | view(s) used |
|---|---|---|
| Plan and proportions | conforms: a rounded rectangle with a north-south long axis. Aspect ratio is about 1.5 (source about 1.49). The tree island is about 0.34 of rink width (source about 0.38) and sits about 3% north of rink centre (source about 2%). | top, top crop, aerial |
| Ice | conforms: a flat, clean white surface | ice_surface, front, rear |
| Dasher boards: board | conforms in form: low white boards all round. The ice contact line is weak (P2 #3). | dasher_boards, rear_side |
| Dasher boards: glass | conforms: clear glass panels above the boards, with the chalets visible through them | dasher_boards, glass_close, interior |
| Dasher boards: posts | conforms: dark slim posts at a regular pitch | glass_close, front |
| Dasher boards: rail | conforms: one continuous timber handrail, mitred smoothly round the corners, with no gaps | rear corner crops, rear_side crop |
| Deck | conforms with a P2: a timber deck rings the boards and is visible in top, rear_north and square_aerial. It reads too pale at aerial scale (P2 #4). | top, rear_north, square_aerial |
| Tree island: ring wall | conforms: a low white circular wall | ice_surface, interior |
| Tree island: glass ring | conforms: a clear glass ring with posts | ice_surface, left_side |
| Tree island: tree | conforms: layered drooping fir skirts in two closely related greens, tiers alternating light and dark. No soil shows from above. | christmas_tree, top crop |
| Tree island: ornaments | conforms: round red and gold baubles, and a warm light at every bough tip. Some baubles are clipped by the skirts (P2 #7). | christmas_tree, tree crop |
| Tree island: star | conforms: a solid crossed-prism gold star seated on the leader by a short gold stem, reading as a star from S, W, E, N and SE | front, left_side, right_side, rear, rear_side crops |
| Chalets: count and arrangement | conforms: 4 north, 4 south, 6 west, 6 east (20). The rink-facing gables are separate, with gaps of about 1 m of setts. | top, aerial, square_aerial, front_corner |
| Chalets: walls | conforms: dark timber boxes | architecture_close, facade_close |
| Chalets: counters | conforms: a recessed opening with visible depth, a back wall, a counter shelf and a flap board | market_chalets, architecture_close, interior |
| Chalets: awnings | conforms: flap board plus green garland bar on the counter face | market_chalets |
| Chalets: snowy roofs | conforms: white snow-laden pitched roofs, each with a ridge board | facade_close, square_aerial crop |
| Chalets: garlands | **deviates (P1 #1)**: the rink-facing gable only. The rear gables and outer eaves are bare, where the oblique source shows garland and lights on every eave and a bow on every outward gable. | facade_close, square_aerial vs oblique |
| Benches and skating aid | benches conform (two on the ice by the SW boards, as in the source front). The skating aid deviates slightly (P2 #8). | dasher_boards, right_side, ice_surface |
| Setts | conforms: a dark grey paved square (clay pattern) | square_aerial, facade_close |
| Lamps | conforms: dark lamp posts at the square corners | front_corner, rear, square_aerial |
| Town fronts | conforms as simplified context, with window rows up to the eaves on every inner front. Monolithic and uniform (P2 #5). | front, left_side, right_side, rear, square_aerial |
| Materials hierarchy | conforms: white ice and boards, clear glass, dark timber, green garland, red and gold accents, cream and red frontages, terracotta roofs | all |

## 4. Camera validity

No view has its target occluded or clipped, and every view is legible.
- front: the whole tree, star and sky are inside the frame. The east chalet row and the garlanded boards form the right foreground. The west row is mostly hidden behind the tree (P2 #2, composition only).
- front_corner and aerial: the whole frontage ring, the rink and all 20 chalets are inside the frame. The asset fills about 60% of the frame width, which is acceptable.
- top: legible. The square is small in the frame with wide margins (P2 #8, framing only).
- left_side, right_side, rear, rear_side, rear_north: the whole tree and star are in every frame.
- The detail views (facade_close, architecture_close, glass_close, christmas_tree, market_chalets, dasher_boards, ice_surface, square_aerial, interior) each frame their target. christmas_tree is a deliberate mid-tree crop.

## 5. Previous-version findings: resolved in the pixels?

**v004 P1s**
- Front tree ran off the top of the frame and the star was cut off: **resolved.** In front.png the star is at about y=105 with clear sky above it. The garlanded boards and the east chalet row remain the right foreground.
- Star floated 4-6 px above the spire with sky between, and read as a thin flat sliver from the east and west: **resolved.** In zoomed crops of front, left_side, right_side, rear and rear_side, a short gold stem joins the star to the leader tip with no sky gap, and the crossed prisms read as a solid star from every direction.
- Handrail garland built of straight segments left black wedge gaps, two of them large slashes in the market_chalets foreground: **resolved.** The market_chalets foreground garland is one continuous green tube. The rear SW and SE corner crops and the rear_side corner show smooth faceted bends with no black wedges.

**v004 fixes that must still hold**
- Round red and gold baubles and a warm light on every bough tip: **holds** (christmas_tree).
- Garland on top of the handrail, readable from the ice and the deck, with round baubles and lights on both faces: **holds.** Baubles and lights show on the deck face (square_aerial and rear_side crops) and on the ice face (dasher_boards, glass_close). Lights on the ice face are sparse (P2 #6).
- East chalet row as the large right-hand foreground of the front: **holds.**
- High aerial showing the whole rink and all twenty chalets inside the frontage ring: **holds** (counted 6+4+6+4 in aerial).
- Window rows up to the eaves on every town front: **holds** (front, left_side, right_side, rear, square_aerial).

**v003 fixes that must still hold**
- Separate chalets with about 1 m of setts between the eaves, and a ridge board on every roof: **holds** (top crop, square_aerial crop).
- Tree as layered drooping fir skirts in two greens, with no soil from above: **holds** (christmas_tree, top crop).
- Side and rear views hold the whole tree and star: **holds** (left_side, right_side, rear, rear_side, rear_north).
