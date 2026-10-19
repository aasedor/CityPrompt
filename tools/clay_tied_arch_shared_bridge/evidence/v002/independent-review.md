# Independent holistic review: clay-tied-arch-shared-bridge v002 (RLASM v6.1)

Reviewer: independent, adversarial. Evidence used: only `sources/front.png`, `sources/oblique.jpg`, `sources/top.jpg`, all 18 `renders/*.png` at full resolution, the four `boards/*.png`, and zoomed crops I made in a new folder (`/tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/review-crops-v002-6aa20905/`). I did not use builder metadata, counts or notes as proof.

## 1. Verdict

**VISUAL_REWORK_REQUIRED**: the v001 tie count and deck, quay and soffit defects are fixed in the pixels. Two P1s remain. The square deck ends do not follow the quay lines that the governing top source shows. The rear elevation also cuts off both ends of the span.

Counts: P0 = 0, P1 = 2, P2 = 7

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | top, aerial, rear_side, arch_springing, left_side, right_side | In plan the deck is a plain rectangle turned about 13 degrees, and both ends are square to the bridge axis. The ends therefore sit about 13 degrees off the quay copings. The landing overrun varies from corner to corner. In top.png the west end's NW corner sits about 140 px (roughly 6 m) past the west coping and the SW corner about 75 px (roughly 3 m). The east end is the mirror image: NE about 60 px, SE about 140 px. The deck reads as a slab dropped diagonally across the quay streets, and the four springing plinths sit at four different setbacks from the coping. In source top.jpg (crops of the west and east ends), each deck end runs parallel to the quay or kerb edge beside it. The landing is a clean line along the quay, and the north and south springings sit on that line. The "brick wedges" the builder claims are not distinct in the pixels: the area between the deck end and the coping is the same undifferentiated quay paving. | The whole bridge was rotated as a rigid rectangle. The deck ends, landing plates and plinth line were not cut skew to the quay lines. | Make each deck end a skew line parallel to its quay coping (deck plan as a parallelogram), so the end lands at a constant setback from the coping. Set the north and south plinths on that skew end line, at equal setback. Keep the 13-degree axis, the 7 ties and the vertical hangers unchanged. |
| 2 | P1 | rear (also rear_north) | The rear whole-envelope elevation cuts off both near-arch springings. The near arch leaves the left frame edge at about y 560 and the right frame edge at about y 645. The west deck end, the west plinths and the quay contact run off the left edge. rear_north also loses the whole west end off its left edge. This rear and north elevation is the only one that would show the full span profile, rise-to-span ratio and both abutments together, and it shows none of the springings. | The camera was re-aimed and tightened for v002 without widening for the 13-degree rotated, roughly 46 m deck plus its landings. | Pull rear back, or widen its FOV, so both plinths of the near arch and both deck ends sit inside the frame with about 5% margin. Do the same for rear_north, or re-aim it on one abutment as a detail. |
| 3 | P2 | planter_divider, cycle_lane, front | The grasses are faceted low-poly boulders and crystals. Several large ochre pyramids remain, so the planting reads as rubble or rocks rather than soft grass clumps spilling over the planter edge. | Icosphere-style clumps with too few, too-flat facets, plus surviving cone primitives. | Replace the remaining cones with tufted or blade clusters, raise the clump density, and let the grass spill slightly over the planter rim. |
| 4 | P2 | top, aerial, hangers, glass_close | The footway is neutral mid-grey, sampled at about (160,160,160). The source footway is warm pale concrete, about (199,188,175). The arches are a mid-dark blue-grey, darker than the source's pale silver. Value separation now exists, but the overall key is darker and colder than the source. | The palette values were moved away from each other rather than matched to the source. | Warm and lighten the footway toward the source concrete. Lighten the arch, tie and fascia steel to a pale silver-blue that keeps the hue separation. |
| 5 | P2 | left_side, hangers, glass_close, cycle_lane | On the context blocks, the balcony slabs float on blank wall with no balustrade or door. A huge cantilever slab sits at the top right of left_side. In left_side the windows of the right-hand block stick out as dark plaques instead of being recessed. | The context generator puts in slab primitives without supports, and the window extrusion sign is flipped on one block. | Recess the windows on every context block. Give balcony slabs a thin balustrade, or drop them. Clamp the slab size. |
| 6 | P2 | aerial | The lower-right context block's roof hides the south arch's east springing and the south-east landing. This is the v001 occlusion P2 again, now caused by the roof rather than a parallax parapet. | The aerial was re-aimed without checking its line of sight to all four springings. | Raise or rotate the aerial camera, or lower or set back that block, until all four plinths are visible. |
| 7 | P2 | arch_springing | A dark brown vertical slab, a context building corner close to the camera, covers the right roughly 4% of the frame. | The near-field context was not culled for this detail camera. | Move the camera off the facade, or exclude that block from this render. |
| 8 | P2 | front, arch_springing, rear_side | The deck landing plates are thin slabs sitting on the paving with a visible edge. The red lane surfacing continues outside the railing line around the NW plinth (front lower-left), so the cycle surfacing spreads onto the quay beyond the arch foot. | The square deck rectangle extends past the railing and arch-foot line at the landing. Linked to #1. | Trim the landing surfacing to the railing line and set it flush with the paving. This largely disappears once #1 is fixed. |
| 9 | P2 | quay_under, rear, deck_edge | The concrete bearing shelf with a seat face is now present. The bearings only read as a thin dark line between the soffit and the shelf, with no distinct bearing blocks. | The bearings are too thin or too dark compared with the shadow under the deck. | Make 2 to 3 bearing blocks under each edge tie slightly taller, in a lighter neutral. |

## 3. Source conformance checklist

| item | status | view(s) used | note |
|---|---|---|---|
| Plan and proportions | deviates | top vs source top; aerial; rear_side | The 13-degree skew of the axis now matches (north edge about 13.2 degrees in top.png). The deck ends are square to the axis, not parallel to the quays (P1 #1). The red lane is about 0.65 times the footway width, matching the source's roughly 0.7. |
| Arch form and inclination | conforms | front, left_side, right_side, facade_close, rear_side | Two box-section steel arches lean toward each other with the crown well above the deck, which matches the front and oblique sources. The full elevation profile is only partly visible because rear is clipped (P1 #2). |
| Cross ties | conforms | top, aerial, rear_side, architecture_close, facade_close | 7 box ties, evenly spaced about 100 px apart in top.png, spanning about 56% of the springing-to-springing length. The source top shows 7 over about 54%. |
| Hangers | conforms | rear, rear_north, facade_close, hangers, front_corner | Slender rods at even spacing, about 12 to 13 per arch, vertical in elevation, landing on the deck edge tie. |
| Deck | conforms (edges) / deviates (ends) | rear, deck_edge, quay_under, top | The fascia is about 0.7 to 0.8 times the railing height and the soffit sits clearly above the water. The deck ends deviate (P1 #1). |
| Cycle lane and footway | conforms | top, cycle_lane, front, left_side | The red lane with dashed centre line is on the north side and the pale footway on the south, as in the source. The footway's tone is neutral rather than warm (P2 #4). |
| Planter | conforms (form) / deviates (planting finish) | top, planter_divider, front | A raised concrete trough runs nearly the full length between lane and footway, as in the source. The planting reads as faceted rocks (P2 #3). |
| Railings | conforms | glass_close, cycle_lane, hangers, rear | Steel post and vertical-bar railings on both outer edges, matching the source. |
| Quays and landings | deviates | top, arch_springing, rear_side, quay_under | Brick quay walls now show about 2 to 3 m above the water, with a coping and a bearing shelf. The landings are square deck plates, not ends aligned with the quays (P1 #1). |
| Water | conforms | rear, facade_close, aerial, top | A continuous canal extends past every frame, with clearance under the deck. |
| Context | conforms (simplified) | front_corner, aerial, right_side, left_side | Brick-red apartment blocks with punched windows; the composition of front_corner and aerial echoes the oblique source. Minor primitive defects (P2 #5). |
| Materials hierarchy | conforms (with polish) | top, aerial, front | Steel (blue-grey) is now distinct from the footway (grey), the red lane, the green and ochre planting and the brick quays. Values are darker and colder than the source (P2 #4). |

## 4. Camera validity

- **rear**: invalid. Both near-arch springings and the west deck end are cut off at the frame edges (P1 #2).
- **rear_north**: the west end of the span and the west springing are cut off at the left frame edge (included in P1 #2).
- **aerial**: the target is legible, but a context roof hides the south arch's east springing and the south-east landing (P2 #6).
- **arch_springing**: the target is legible. A near context slab covers the right edge of the frame (P2 #7).
- **front**: valid. It is now on the west landing left of the axis, with the near-left springing and plinth in frame, as in the source.
- **front_corner, top, left_side, right_side, rear_side**: valid. The whole asset is in frame and the springings are visible. In front_corner the near context block hides only part of the south fascia, which mirrors the source oblique.
- **facade_close, architecture_close, glass_close, hangers, planter_divider, cycle_lane, deck_edge, quay_under**: valid and legible.

## 5. Previous-version (v001) findings: resolved in the pixels?

| v001 finding | status in v002 pixels |
|---|---|
| P1: bridge at 90 degrees, but the source shows a 13-degree skew with wedge-shaped landings | **Partly resolved.** The axis is visibly skewed about 13 degrees in top.png and every other view turns with it. The landings are square deck ends, not ends aligned with the quays, and no distinct wedge landing reads. Carried forward as P1 #1. |
| P1: 5 cross ties instead of 7 | **Resolved.** 7 evenly spaced box ties over the central part of the span (top, aerial, rear_side). |
| P1: fascia about 1.4 times the railing, soffit barely above the water, no quay wall showing, no bearing seat | **Resolved.** The fascia is about 0.7 to 0.8 times the railing (rear crop), the soffit clears the water, and the brick quay walls show clearly above the water (rear, facade_close, deck_edge). A concrete bearing shelf with a seat face is present (quay_under, rear right). The bearings themselves are faint (P2 #9). |
| P2: arches, ties, fascia and railing the same pale grey as the footway | **Resolved.** The steel is blue-grey and distinct from the footway. A tone-match issue remains (P2 #4). |
| P2: generic office-slab context, tan blocks, visible world edge | **Resolved.** The blocks are brick-red with punched windows, and the ground and canal extend past every frame. Primitive defects remain (P2 #5). |
| P2: front camera mid-deck | **Resolved.** The camera is on the west landing left of the axis, with the near-left springing in frame. |
| P2: springing pads with a stray box | **Resolved.** There is one chamfered plinth per springing with no stray box (front, arch_springing, top). |
| P2: spiky cone planting | **Partly resolved.** The clumps are ochre and green, but prominent cones and pyramids remain (P2 #3). |
| P2: context parapet over the east springing in aerial and narrow side views | **Partly resolved.** The side views are clear. In aerial a context roof now hides the south-east springing (P2 #6). |
