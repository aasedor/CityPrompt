# Independent RLASM v6.1 holistic review: slab v006 (clay-slab-balcony-tower)

Reviewer: independent, not the builder. Evidence: the locked sources (front.png, oblique.jpg, top.jpg), all 18 renders read at full 1440x1080 resolution, and the 4 phone boards. Zoomed crops were taken of the front roof edge, the front_corner roof, the front base, the aerial corner pier and the roof_penthouse corner. No build code, reports or notes were read.

## 1. Verdict

**VERDICT: VISUAL_REWORK_REQUIRED.** The v005 roof-edge P1 is fixed, but every corner pier is an open hollow box with no cap. From above it shows as a hard black hole at all four roof corners, in every elevated view and on the phone boards.

**Counts: P0 = 0, P1 = 1, P2 = 7**

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | **P1** | aerial.png (approx. 455,433 / 705,187 / 985,402 / 737,666); front_corner.png (approx. 490,365 / 728,203 / 943,380 / 705,567); top.png (approx. 457,278 / 980,278 / 457,800 / 980,800); rear_side.png (approx. 483,345 / 735,190 / 957,372 / 705,550); roof_penthouse.png (approx. 175,720); boards/phone-01 and phone-04 (top panel corners) | Where the two L-shaped corner fin heads meet above the parapet, a solid black square void of about 5-8 px (aerial) shows. It is an open shaft into the hollow corner pier, and it reads as a modelling hole at all four corners. In roof_penthouse it shows as a black slot on top of the near corner fin head. The source oblique shows solid concrete corner piers with closed tops. | The corner pier / fin head is built as two plates (or a hollow box) with no top cap, so the camera sees into the unlit inside | Add a solid cap (or build the corner pier as one closed solid prism) at fin-head height at each of the 4 corners. Check aerial, top, front_corner and roof_penthouse for zero near-black pixels at the corner fin heads. |
| 2 | P2 | front.png centre bay (approx. 670-770, y 190-830); glass_close.png (approx. 620-1200, y 480-580 and 800-1150, y 0-80); rear_lane.png (approx. 820-960, y 40-90) | Large soft white elliptical highlight blobs on the centre-bay window glass, repeated on every storey. They read as emitted light or smudges, not as reflection. | Area-light or HDRI hotspot reflected in a glossy glass shader | Make the glass rougher or dim the specular, or move or soften the key light |
| 3 | P2 | top.png, aerial.png, roof_penthouse.png, front_corner.png | The three grey rooftop units sit near three parapet corners, far from the penthouse. The source oblique and top show the AC units clustered against the penthouse's east side and base. | Placement rule spreads plant to the corners | Move the units onto the roof next to the penthouse's east and south faces |
| 4 | P2 | top.png (annex approx. 825-912, y 420-512); rear_side.png; right_side.png (approx. 700-845, y 98-210); roof_penthouse.png | The penthouse is a cluster of three masses (main box, a raised box and a lower annex with a door). The source top and oblique show one simple near-square two-storey concrete box with a low slab step at its south base. | Extra annex volume | Merge into a single box. Keep the louvre and door on it. |
| 5 | P2 | facade_close.png (approx. 185-200, 720-750); architecture_close.png; base_corner.png | Thin terracotta jamb and head strips frame the outer-bay balcony windows. The source front supports narrow brick piers at the bay edges, so this is acceptable, but the strips read slightly thin and over-uniform. | Brick trim width | Optional: widen to pier proportion, or leave as is |
| 6 | P2 | base_corner.png (tree approx. 755-1205, y 300-1080) | A low-poly tree stands in front of the entrance corner and hides about a quarter of the base-corner detail (canopy and lobby glazing). | Landscape placement in the detail-camera line | Move the tree about 3 m along the kerb or retarget the camera |
| 7 | P2 | interior.png | The camera is pressed against one window. It shows only a mullion, the frame and the horizon, so no room is legible. It is still a legal camera (a window seen from inside), so P2. | Camera too close to the glazing | Pull the camera back 3-4 m into the room so floor, ceiling and the window wall are all in frame |
| 8 | P2 | top.png versus source top.jpg | The source top shows the north-centre bay of the roof outline projecting slightly (source approx. 525-690, y 128-150), where the render recesses the centre bay on all four faces. The north face is not otherwise visible, so this is judged only as coherence. | Symmetric notch applied to all four faces | Optional: let the north centre bay come flush or slightly proud if the source top is read as north-up |

## 3. Source conformance checklist

| Item | Result | View used / note |
|---|---|---|
| Silhouette | conforms | front, left_side, right_side, rear: a square-plan tower with balcony plates on the outer bays projecting past the fins, a recessed centre bay and the penthouse above. The top and aerial now show a notched roof outline, matching source top.jpg. |
| Storey count | conforms | front.png: 12 residential storeys (window rows about 210 to 835) over a recessed ground floor, consistent with the brief's twelve |
| Balcony stacks and slab bands | conforms | front, facade_close, balcony_close: stacked outer-bay plates with glass balustrades and side returns; the slab band continues across the centre bay on each floor |
| Fins and corners | conforms in elevation, deviates at top | front, architecture_close, base_corner: full-height fins at the bay lines and corner piers. Fin heads rise above the parapet (front crop). Corner pier tops are open voids (Finding 1). |
| Centre-bay spandrels and windows | conforms | front, glass_close, rear_lane: a brick spandrel under a framed window band, recessed between fins, on every storey |
| Recessed ground floor and lobby | conforms | front base crop, lobby_entry, fin_contact, base_corner: columns, recessed dark glazing with mullion depth, an entrance door and a canopy on its support wall. No floating parts seen. |
| Penthouse and roof plant | conforms with P2 deviations | roof_penthouse, aerial, front: concrete penthouse of about two storeys with a louvre and door. It has an extra annex, and the plant is placed at the corners rather than at the penthouse (Findings 3 and 4). |
| Materials hierarchy | conforms | All views: light concrete (fins, slabs, penthouse) dominant, terracotta brick secondary in the spandrels and parapet, a teal stripe on the parapet, grey-green glass. A flat source palette is appropriate for clay. |

## 4. Camera validity

- No view has the target occluded, clipped or illegible to the level of an invalid camera.
- interior.png is borderline: the target is legible only as one window from inside (P2, Finding 7).
- base_corner.png is about 25% occluded by a tree, but the corner, columns and lobby are still legible (P2, Finding 6).
- All whole-envelope views (front, front_corner, aerial, top, left_side, right_side, rear, rear_side) frame the whole asset with no clipping.

## 5. Prior-version findings

| Prior finding | Status in v006 | Pixel evidence |
|---|---|---|
| v005 P1: the roof edge was one uniform thick flat white square ring over the centre bay. It should be a thin ledge over the outer bays only, notched over the centre bay, with a low brick parapet, a thin teal stripe and fin heads rising above | **Resolved** | front.png roof crop: a thin ledge over the outer bays steps back over the centre bay; a brick parapet with a teal stripe sits behind it; fin heads and corner piers rise above it. top.png and aerial.png show a notched outline. (A new defect at the corner fin heads is logged separately as Finding 1.) |
| v004: trays past the fins round the corners with glass returns | Resolved (still) | front, architecture_close, base_corner: the outer-bay plates end at the corner pier and centre-bay jamb lines with glass side returns |
| v005 P2: soft glazing highlights | Not resolved | front centre bay, glass_close (Finding 2) |
| v005 P2: rooftop units far from the penthouse | Not resolved | top, aerial, roof_penthouse (Finding 3) |
| v005 P2: penthouse annex | Not resolved | top, right_side, rear_side (Finding 4) |
| v005 P2: brick jamb strips | Not resolved (acceptable) | facade_close, architecture_close (Finding 5) |
| v005 P2: tree at the base corner | Not resolved | base_corner (Finding 6) |
| v005 P2: interior camera too close | Not resolved | interior (Finding 7) |
