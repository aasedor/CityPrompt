# Independent holistic review: clay-calgary-sandstone-heritage v005 (RLASM v6.1)

## 1. Verdict

**VISUAL_REWORK_REQUIRED.** Both v004 P1s are fixed in the pixels, but all three locked sources put the south entrance (the deep arched portal, its balustraded balcony and the giant arcade rising from the balcony) in a central south pavilion under the large gable. The render puts them in the south-west corner pavilion, which leaves one P1 open.

Counts: P0 = 0, P1 = 1, P2 = 9

Method note: I judged only rendered pixels against the locked source pixels: `sources/front.png`, `sources/oblique.jpg` and `sources/top.jpg`. I opened all 18 renders and all 4 boards. Zoomed crops are in `/tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/review-crops-v005-124e45c3/`. The P1 below conflicts with the brief's wording ("a deep round-arched portal in the south-west pavilion"). The method says the sources are the only truth and the top view governs the plan, and all three sources agree with each other and against that wording. The method owner should rule on it.

## 2. Findings

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | front, front_corner, top, portal_arch, facade_close (vs all 3 sources) | **The entrance is in the wrong place on the south front.** In the render, the portal porch with its balustraded balcony and the giant arcade rising from the balcony sit in the **south-west corner pavilion**. In top.png the porch is at x≈345-440, y≈990-1050, centred on the SW pavilion (x≈270-525). The south-wing centre (x≈625-815) carries only a plain cross gable over the ordinary wing rhythm (facade_close, front x≈440-560). All three sources put the porch at the **centre of the south front**. In top.jpg the balustraded porch deck is at x≈543-653, y≈745-772, between round pinnacle bases at x≈537 and 660, centred under the wing's large central gable, and the SW pavilion (x≈285-445) has no deck. In oblique.jpg the SW pavilion (x≈170-300, plain giant arcade) and the SE pavilion (x≈490-640) flank a separate central block (x≈310-435) that holds the portal, the balcony, the giant arcade and a large coped gable framed by turret pinnacles. front.png shows the same sequence: SW pavilion x≈120-215, portal block with big gable x≈215-350, SE pavilion x≈380-670. The primary-front composition and the main-entrance plan position therefore differ from the governing sources. | The portal was assigned to the SW pavilion (brief wording) rather than read from the top source. | Move the portal porch, its balustraded balcony and the "giant arcade from the second floor" bay to the centre of the south wing. Give that bay the source's larger coped gable with a small arcade in the gable and a turret pinnacle each side. Return the SW pavilion's south face to the standard pavilion grammar (giant arcade from the first floor under the small-arch tier), the same as the other three pavilions. Keep the north-centre gable as is. Re-render front, front_corner, top, aerial and portal_arch. |
| 2 | P2 | top, front, front_corner | South sidewalk carries 4 trees (top x≈200, 460, 775, 1200). The source top shows 2 on the south sidewalk (x≈490, 760). N, W and E now have 2 each, which is correct. | South-front tree set kept from v004. | Remove the two corner trees on the south sidewalk, or move them to the corners as the source shows. |
| 3 | P2 | top | The orthographic frame still clips the north and south context. North and south tree canopies are cut at y=0 and y=1080, and the N/S streets are out of frame. The building itself is fully in frame. | 4:3 landscape frame on a square block; the extent was widened only enough for the sidewalk inner edges. | Widen the ortho scale about 10% more, or centre on the block including the curbs. |
| 4 | P2 | front, facade_close, rear_north, east_side | Tree canopies are flat faceted "umbrella" discs on thin forked trunks. The sources show round, full deciduous crowns. | Low-poly canopy primitive flattened in Z. | Use a taller rounded canopy (about 1:1 height to width) on the same trunks. |
| 5 | P2 | front, front_corner, rear_north, gables_pinnacles | South and north pavilion faces read as three bays: outer side bay (pair, single arch, 3 small arches), giant arcade, inner side bay. In front.png and oblique.jpg the 3-light giant arcade runs against the broad corner pier, with only an inner side bay. | The side-bay generator is applied symmetrically on the N/S faces. | On the N/S faces, drop the outer side bay and widen the corner pier, as was already done on the E/W faces. |
| 6 | P2 | glass_close, facade_close, portal_arch, rear_north | Glazing is see-through: other arched windows, lit panes and greenery from beyond show through the panes, so the building reads as a hollow shell in close views. | Transparent glass with no interior backing behind most openings. | Make the panes darker or reflective, or add a dark back-plane behind the windows that have no interior. |
| 7 | P2 | all whole-envelope views | The slate is near-black charcoal. The sources show mid-grey, slightly warm slate, so the roofs dominate the clay more than they should. | Roof palette value set too low. | Raise the slate value to the source mid-grey. |
| 8 | P2 | glass_close, facade_close | The second-floor arch hood moulds and heads show visible polygon facets (8 segments). | Segment count reduced to stay under the size cap. | Accept, or use 10-12 segments on the large arches only. |
| 9 | P2 | front_corner, east_side (vs oblique) | The east wing roof between the SE pavilion and the tower is plain. oblique.jpg shows small gabled dormers on the wing roofs (around x 630-700). | Dormers omitted on the wings. | Add 1-2 small coped dormers per wing slope. |
| 10 | P2 | aerial, rear_side | The building fills only about a third of the frame width. It is legible but loosely framed. | Camera distance. | Dolly in about 25%. |

## 3. Source conformance checklist

| item | status | view used |
|---|---|---|
| Silhouette (three gabled pyramids per front, dominant tower with copper spire) | conforms | front vs front.png; front_corner vs oblique.jpg |
| Storey count (rusticated basement + first + second + third + gable attic) | conforms | facade_close, rear_north vs front.png |
| Plan (square block, corner pavilions, central court, tower mid-east) | deviates: south entrance porch is at the SW pavilion instead of the south-wing centre (P1 #1). Otherwise conforms. | top vs top.jpg |
| Court and pavilion projection | conforms: square open court with window grid; pavilions step forward with visible returns | top, roofs_court, front |
| Sandstone coursing | conforms (clay): buff horizontal coursing lines; rock-facing not modelled, which is allowed for clay | glass_close, facade_close |
| Window tiers: basement | conforms: small windows in base band | facade_close, east_side |
| Window tiers: paired first floor | conforms (wings and side bays) | facade_close |
| Window tiers: round-arched second floor | conforms; giant arcade on pavilions rises from the first floor | rear_north crop, east crops, front SE crop |
| Window tiers: third-floor small-arch arcades | conforms: 3+5+3 across the N/S pavilion faces, 5+3 on E/W, 4-arch groups on wings | front SE crop, rear crops |
| String courses and eave cornice | conforms | facade_close, architecture_close |
| Gables and pinnacles on outward pavilion faces | conforms: coped gables on both outward faces, pinnacles at feet and apex | gables_pinnacles, architecture_close |
| Roofs: wing hips | conforms | roofs_court, top |
| Roofs: pavilion pyramids | conforms (copper finials) | top, front_corner |
| Roofs: cross gables | conforms on N/S wing centres. The south one should be the large portal gable (P1 #1). Wing dormers are missing (P2 #9). | top, facade_close |
| Portal | deviates in location (P1 #1). Form conforms: deep round arch with a returned vault, steps, balustraded balcony. | portal_arch, front_corner |
| Clock tower: projection | conforms: projects from the east wing mid-front, with porch beyond | top, east_side |
| Clock tower: lancets | conforms: tall grouped lancets on the shaft | east_side, front_corner |
| Clock tower: clocks | conforms: four faces, above the pavilion apexes in elevation | east_side, left_side, rear_north, clock_tower |
| Clock tower: belfry | conforms: 5-arch arcade above the clocks | clock_tower |
| Clock tower: turrets | conforms: octagonal corner turrets with copper cones | clock_tower |
| Clock tower: spire | conforms: tall slender octagonal copper spire | clock_tower, east_side |
| Streets and trees | conforms on four streets and sidewalks with 2 trees each on N/W/E. South has 4 (P2 #2). Canopy form is off (P2 #4). | top, front |
| Materials hierarchy (buff stone > dark slate > copper accents) | conforms. Slate is too dark (P2 #7). | all |

## 4. Camera validity

- No view is invalid. In every view the target is legible and the asset is not clipped.
- top: the building is fully in frame. The north and south sidewalk trees are cut at the frame edges and the N/S streets fall outside it (P2 #3).
- aerial and rear_side: loosely framed but legible (P2 #10).
- interior: a straight-on view from inside a window with visible jambs and reveal. Minimal but legible and valid.
- portal_arch: a near-frontal view from slightly east. The balcony end overlaps the outer-bay arched window only through parallax; the top view confirms the porch is centred on its bay, so this is not a defect.

## 5. Previous-version findings: resolved in the pixels?

| previous finding | status | evidence |
|---|---|---|
| v004 P1-1: pavilion window tiers shifted up one storey | **resolved** | All four pavilions now show a 3-light giant arcade. It rises from first-floor rectangular lights through a spandrel panel at the second-floor line to round heads on the second floor, with colonnette piers running continuously (rear_north NE/NW crops; east_side SE/NE crops; left_side crops; front SE crop). The separate first-floor pair in that bay is gone. The third-floor small-arch tier runs the full pavilion width under the cornice (3+5+3 on N/S, 5+3 on E/W). On the SW pavilion the arcade rises from the second floor above the balcony (front_corner). |
| v004 P1-2: street trees only on S and E sidewalks | **resolved** | top: two trees on the north sidewalk (x≈490, 950) and two on the west sidewalk (y≈300, 760), flanking the cross gables, in the same style as the others. The south now has 4 (P2 #2). |
| v004 P2 #9: top camera extent | **partly resolved** | The W/E streets and all four sidewalks are now in frame, but the N/S trees are still clipped at the edges (P2 #3). |
| v003 P1: clock tower | **still holds** | The crown clearly dominates. The clocks sit above the pavilion apexes in elevation (east_side: clock y≈340 vs apex y≈420-440). Five-arch belfry above the clocks, slender octagonal copper spire, four corner turrets with copper caps (clock_tower). |
| Arched tower porch with balustraded balcony | **still holds** | east_side, front_corner, front (tower porch crop). |
| SW portal porch and balcony | **form holds, location challenged** | portal_arch and front_corner show a deep arch, steps and balcony. The position conflicts with the sources (P1 #1). |
| E/W pavilion faces carry only the inner side bay | **still holds** | east_side and left_side crops: corner pier, then giant arcade, then inner side bay. |
| Straight-on interior camera | **still holds** | interior.png: frontal window with reveal jambs. |
| v002 P0 and two P1s (fixed in v003) | no regression seen | No envelope, contact or opening-depth defects in any view. |
