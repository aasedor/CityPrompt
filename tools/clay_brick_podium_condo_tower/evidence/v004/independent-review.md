# Independent RLASM v6.1 holistic review: condo v004

## 1. Verdict

**VISUAL_REWORK_REQUIRED.** Three of the v003 blockers are fixed in the pixels: the corner columns, the south balcony stacks and the interior. Two P1 defects remain. The corner bay at podium level still does not match the source, and the penthouse is about half the source's height and footprint.

**Counts: P0 = 0, P1 = 2, P2 = 6**

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | corner_entry (corner pier x~705-760, canopy x~730-1360 y~430-480); right_side (entry canopy x~440-545 y~880-905); front_corner (podium corner x~770-800 y~800-900) | A solid brick pier sits on the SE corner. Both faces next to it have single-height storefronts under a dark canopy, with brick and a punched window above. The lobby entry and its canopy are in the **first** east bay, right beside the corner. The source (front.png x~515-640 y~520-680; oblique.jpg x~320-560 y~400-650) shows a **double-height glazed corner bay**. It wraps the corner on a **thin mullion** with a grey spandrel band between the storeys and brick piers on either side. The entry is a stone-framed portal with its own canopy in the **second** east bay (front.png x~680-740). | v003 corner grammar was not rebuilt. Only the canopy was moved to the east face. | Remove the corner brick pier. Make the corner bay full-height glass on both faces, from grade to the cornice, with a slim corner mullion and a dark spandrel at the 2nd-floor line. Flank it with brick piers. Move the lobby portal and its canopy one bay north on the east face and give it a pale stone surround. |
| 2 | P1 | front (penthouse x~630-1030 y~83-145); roof_crown (x~270-1130 y~375-700); top (x~615-1070 y~455-785); aerial; rear_side | The penthouse is a plain box about one storey tall, about 62% of the tower width and about 61% of its depth. It is pushed to the south-east, which leaves a large empty roof deck on the north and west. The source (front.png y~45-140, oblique.jpg x~350-800 y~80-240, top.jpg x~330-885 y~245-520) shows a **large** pale louvred screen enclosure. It is about 2-3 storeys tall and covers about 75% of the roof in each direction, with only a narrow walkable perimeter inside the guard rail. | The penthouse was sized as a small mechanical box rather than the dominant crown. | Scale the penthouse to about 75% x 75% of the tower roof and centre it, or shift it slightly north. Raise it to about 2.5 typical floor heights. Run continuous horizontal louvre banding along its faces in place of the five separate dark panels. |
| 3 | P2 | top (west terrace x~290-410); front (x~330-450 y~690-745); rear_side | The tower is set back about 14% of the podium width from the west edge and about 9% from the north edge. This leaves a wide west terrace with planters. In the source the tower comes close to the west and north podium edges, and the main terrace is the strip along the south. | Leftover from the v003 footprint fix | Widen the tower to the west or north so the exposed terrace is mainly the south strip plus a narrow perimeter. |
| 4 | P2 | top, front_corner | The tower plan ratio is about 1.34:1 (E-W to N-S). The source south face reads clearly longer than the east face, at roughly 1.6-2:1. | Plan depth | Shorten the N-S depth or lengthen the E-W length of the tower slightly. Keep 5 stacks on the south face and 2 on the east. |
| 5 | P2 | front (lowest tower floor y~710-745), right_side, left_side | There is no balcony on the lowest tower floor. In the source the stacks run down to just above the podium terrace. | Stack start index | Start the balcony stacks at the first tower floor. |
| 6 | P2 | right_side (x~1010-1145 y~470-605, crop); rear_lane (x~178-545 y~512-895) | The service/garage doors are flat white panels set almost flush with the brick, with only a hairline reveal. The source garage door (front.png x~785-820) is dark grey and clearly recessed. | Door material and inset | Recess the doors about 150-200 mm with jamb returns, and use a dark grey door panel. |
| 7 | P2 | front, podium_retail | The ground storefronts are noticeably shorter than the second storey (about 75 px against about 110 px in front.png). In the source the two storeys read roughly equal, with a tall retail ground floor. | Floor-to-floor split | Raise the canopy line so the retail storey is at least as tall as the second storey. |
| 8 | P2 | interior | The interior view is now legible: a lobby desk, mullioned glazing and a floor. The glass reads as an opaque grey, so there is no exterior context. | Glass/backdrop shading | Lower the glazing opacity, or add a street/ground plane visible through it. |

No floating or intersecting parts were found. The podium cornice is unbroken on all faces. The tower corner columns land on the podium terrace deck (front_corner crop around x~770-800 y~800). All balcony slabs project with visible thickness and returns, and their glass balustrades sit on top (balcony_stack, facade_close, glass_close).

## 3. Source conformance checklist

| item | status | view used |
|---|---|---|
| Silhouette | Deviates (P1 #2 crown too small; P2 #3/#4 plan) | front, aerial, top |
| Storey count | Conforms: 2-storey podium + 11 tower floors (bands y~210-765 in left_side) | left_side, front |
| Podium bays and storefronts | Deviates at the corner (P1 #1). Mid-face bays between brick piers, the dark canopy band and ribbon windows with precast sills conform. | corner_entry, podium_retail, architecture_close, front |
| Podium terrace and setback | Conforms on the south (glass balustrade, deck, planters). P2 on the oversized west terrace. | podium_setback, architecture_close, top |
| Tower curtain wall and spandrels | Conforms: continuous mullions, an opaque spandrel band at every floor, white corner columns | facade_close, glass_close, balcony_stack |
| Balcony stacks | Conforms: 5 continuous stacks on the south, 2 per face on the east, west and north, every floor except the lowest (P2 #5) | front, right_side, left_side, rear, facade_close |
| Penthouse | Deviates (P1 #2) | front, roof_crown, top |
| Materials hierarchy | Conforms: red brick podium, pale precast cornice and sills, dark canopy, grey-blue glass, white frame, pale penthouse | all |

## 4. Camera validity

Every view is valid. No target is occluded or clipped, and all are legible. The interior view now shows a lobby desk, mullioned glazing and the floor, not just a frosted pane. Trees partly mask the storefronts in front and podium_retail, but not enough to stop review.

## 5. v003 findings: status judged from v004 pixels

| v003 finding | status | evidence |
|---|---|---|
| East corner columns piercing the podium cornice into the second-storey brick | **Resolved** | front_corner crop: the white corner column stops on the terrace deck. The cornice and brick below are unbroken (right_side, corner_entry). |
| South balconies a checkerboard on 4 stacks against 5 continuous stacks | **Resolved** | front: 5 stacks (x~470-540, 600-670, 730-800, 860-930, 990-1060) continuous on every floor. Only the lowest floor is missing (P2 #5). |
| Tower footprint too small and pushed south-east on the podium | **Partly** | top: the tower now covers about 84% x 82% of the podium and is centred N-S, flush on the east with a south terrace strip. It is still held back on the west (about 120 px) and north (P2 #3). |
| Corner grammar (brick pier and south entry against a double-height glazed corner on a thin mullion, with the lobby on the east face under a canopy) | **Partly / not resolved** | The entry has moved to the east face under a canopy. The brick corner pier is still there, the double-height glazed corner bay is still missing, and the entry is in the first bay rather than the second (P1 #1). |
| Interior camera showing only a frosted pane | **Resolved** | interior: a legible lobby desk, mullions and floor. The glazing is still opaque (P2 #8). |
