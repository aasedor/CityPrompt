# Independent holistic review — clay-climbing-overhang v005

## 1. Verdict

**VISUAL_REWORK_REQUIRED** — the pool block, plaza, roof deck and envelope grammar read faithfully, but the climbing shell — the one element the building is named for — stands on a base roughly four times wider than the locked sources show and its east face is grounded on the plaza, so the leaning blade that cantilevers clear over the plaza has become a squat grounded tub in which no overhang is legible from the east.

## 2. Findings

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | **P0** | front, front_corner, aerial, right_side, top, wall_base_contact, entrance | The shell lands on a broad splayed quadrilateral that runs from the frame-box jamb right across the plaza. Measured foot-width ÷ rim-width: locked front **0.20**, locked oblique **0.16**; render front **0.84**, render front_corner **0.63** — about **4× too wide**. In `sources/oblique.jpg` the shell narrows to a compact foot about 4–5 m across, planted just east of the entrance doors with open granite on three sides (a bin and a small black mat beside it); in `renders/front.png` the contact line runs unbroken from x≈741 to x≈1125. The signature "balanced on a point" wedge has become a pyramid. | v005 rebuilt the base as a 14.2 m quadrilateral (x −15.2 → x −1) with a 3.5 m forward apron; the locked oblique supports roughly 8–9 m at the facade and far less projection. | Re-cut the base quadrilateral to ~8–9 m along the facade and ≤1.5 m of forward projection, keeping the rim, lean and cantilever as built; re-loft the west flare and south face to the narrower foot. |
| 2 | **P0** | right_side, aerial, rear_side | The shell's **east face runs all the way down to the plaza** — its lower edge sits on the paving at (200–660, 1250–1320) in right_side. In `sources/front.png` the east face terminates in a sharp point about two storeys up, with the blank white facade and the open east sidewalk visible beneath it. Consequence: in right_side and aerial the shell reads as a near-vertical closed box and **no cantilever is legible at all** — the rim projects only ~110 px east of the white wall over a ~1200 px height. | The widened base quadrilateral extends east to the facade line, grounding what should be a free airborne edge. | Lift the east face's lower edge clear of the plaza so it terminates as a free blade above the white facade; re-trim the south/east fold so the only ground contact is the south-face foot and the west flare. |
| 3 | P1 | right_side, aerial, front, front_corner | Hold coverage is confined to a narrow band either side of the south/east fold. The **east face is nearly bare** — about 20 scattered holds across a ~20 m plane in right_side — where `sources/front.png` shows that face densely stippled with dark holds edge to edge. The lower half of the south face and the whole west flare are also blank, whereas the locked oblique carries holds from rim to foot. | Holds scattered on a narrow band of the mesh rather than over the full south and east panels. | Extend the hold scatter to cover the whole east face at source density (dark-dominant) and continue the south-face scatter down to the foot; leave the west flare blank as the source does. |
| 4 | P1 | top (pool west edge), front_corner, pool_deck | **No infinity edge.** `sources/top.jpg` shows, west to east: parapet coping → a pale overflow trough → a frameless glass weir → water. The render shows: parapet coping → a close-spaced balustrade → a **dark teal vertical side face** → water. The water is modelled as a solid slab standing proud of the deck with its west side exposed; there is no trough and no weir. The brief lists the weir and trough as identity items. | Pool authored as a raised water box rather than a basin with a weir wall and perimeter trough. | Sink the water into a basin, add a frameless glass weir wall at the west edge and a recessed overflow trough between weir and parapet; hide the slab's side faces. |
| 5 | P1 | climbing_face, front_corner, aerial | **Climbers do not engage the wall.** In climbing_face the middle figure's two feet land on blank CLT at (290–330, 700–740) and (490–540, 660–700); the right figure's raised hand, horizontally outstretched arm and both feet all land on blank CLT. Limbs are flat extruded sticks lying flush on the surface, so the figures read as decals; the right figure's splayed pose does not read as climbing. In the locked front and oblique every climber visibly grips holds with hands and feet. | Figures placed by surface projection without snapping extremities to hold positions. | Snap each hand and foot to an existing hold (or add a hold under it), give the limbs some stand-off from the plane, and re-pose the right figure into a climbing stance. |

### P2 (polish only)

1. **Shell plan oversize** — measured against building width in matched top views, the rim is ~21 × 13 m in `sources/top.jpg` and ~24 × 16 m in `renders/top.png` (≈15–20% larger). Neither camera is true nadir, so treat the figure as indicative.
2. **Shell wall reads thick** — the rim fascia band is ~6% of the rim width in the render against ~4% in the source, so the CLT shell looks about twice as heavy as the source's slim skin (top, rim_interior).
3. **Balustrades** built as closely spaced white posts with glass infill, reading as a picket fence along the whole west parapet (left_side, front_corner, rear); the source is frameless glass with a slim cap.
4. **Plaza value too light** — near-white paving with very faint bands against the source's mid-grey two-tone granite; the figure-ground between shell and plaza is flattened (front, top, plaza_planters).
5. **Street trees** are opaque lollipop canopies set at ground-floor head height; six of them occlude essentially the whole west ground floor in left_side and front_corner. Source canopies sit higher and read through.
6. **West ground floor** reads as a continuous recessed glass band under a sill band; the source's white columns between ground-floor bays, continuing the fin rhythm, are only expressed at the south-west corner (left_side vs `sources/front.png`).
7. **Penthouse** — the glazed run to the pool deck reads longer than the source's, and the north door sits on the west wall rather than the north end (pool_deck, rear_side, rear).
8. **North front** has no base condition — the ground-floor bay repeats the upper-floor bay exactly and there is no entrance (rear). Not shown by any source; flagged for coherence with the grammar on the other three fronts only.
9. **Pool basin** has no shallow ledge or steps; the source top shows steps at the north end and a ladder (top, pool_deck).
10. **Shell contact band** is a uniform-width grey apron with a hard outer edge that reads as paint rather than a kerb or a shadow (front, wall_base_contact). Roof-garden and plaza planters likewise read as bright green lawn beds with tufts sitting on top rather than a continuous grass bed (plaza_planters, rear_side).

**Counts: P0 = 2 · P1 = 3 · P2 = 10**

## 3. Source conformance checklist

| Item | Status | View used |
|---|---|---|
| Silhouette — three-storey pool block | **conforms** — parapet band, two storeys of tall recessed windows between fins with a spandrel band, glazed ground floor | left_side, front_corner |
| Silhouette — penthouse | **conforms** — one-storey white volume on the middle of the roof | front_corner, rear_side, top |
| Silhouette — four-storey east block | **conforms** — four window rows on the east front | right_side, aerial, rear |
| Plan (top view) | **conforms** — west pool strip, central penthouse strip, east membrane roof, shell on the south front at ~0.20–0.82 of the width; cantilever ~10 m south of the facade against ~8 m in `sources/top.jpg` | top vs `sources/top.jpg` |
| Climbing shell — foot on the plaza | **deviates (P0-1)** — base quadrilateral ~4× the source's foot width | front, front_corner, wall_base_contact |
| Climbing shell — lean and overhang | **deviates (P0-2)** — plan cantilever is right, but the east face is grounded so no overhang reads from the east | top (conforms) vs right_side, aerial (deviates) |
| Climbing shell — folded faces | **conforms** — west flare in two planes, south triangle widening from its foot, east face, clean fold lines | front_corner, aerial |
| Climbing shell — level open rim, light fascia | **conforms** — level rectangular rim with a pale timber fascia band (fascia heavier than source, P2-2) | rim_interior, top, aerial |
| Climbing shell — contact with plaza | **conforms** — seated on the paving with a contact band, no float, no gap | wall_base_contact |
| Climbing shell — contact with the facade | **conforms** — frame-box head, spandrel, east post, parapet band and coping all cut cleanly against the shell section; ribbons stop short | front_corner (fold crop), architecture_close, aerial |
| Holds | **deviates (P1-3)** — present, dark and white, densest on the south face, but the east face and the lower south face are nearly bare | right_side, aerial, climbing_face |
| Climbers | **deviates (P1-5)** — three present on the south face, but hands and feet land on blank CLT and limbs are flat | climbing_face |
| Open top and inner walls | **conforms** — hollow open top, inner north/east/west walls with white holds, dark crash mat at the bottom | rim_interior, top |
| West front rhythm — fins, spandrels, recessed windows | **conforms** — deep white fins with returns, projecting spandrel band, glazing recessed with visible reveals | left_side, facade_close |
| West front — glazed ground floor | **conforms with reservations (P2-5, P2-6)** — recessed and glazed, but columns under-expressed and mostly occluded by trees | left_side, entrance, wall_base_contact |
| South frame box and glass ribbons | **conforms** — projecting white frame wrapping the SW corner, two glass ribbons over the recessed ground floor, ribbons stopping short of the shell | architecture_close, glass_close, front |
| Entrance doors | **conforms** — two pairs of glazed doors with pull handles, recessed under a soffit | entrance, interior |
| Parapet band | **conforms** — deep white band with coping, cut cleanly at the shell | left_side, front_corner |
| Pool deck — infinity pool | **conforms (extent)** — long north–south pool, width ≈0.72 of the block and length/width ≈1.9, matching the source's 0.71 / 1.94 | top vs `sources/top.jpg` |
| Pool deck — weir and trough | **deviates (P1-4)** — neither modelled; water is a proud slab with an exposed side face | top (west-edge crop), front_corner |
| Pool deck — balustrades | **conforms with reservations (P2-3)** — glass-infill balustrade present on the parapet, built as a close picket run | left_side, front_corner, rear |
| Pool deck — loungers | **conforms** — row along the east side of the pool plus a row at the north end | front_corner, top, rear_side |
| Roof garden — planters, grasses, small trees | **conforms** — raised planters with straw grasses and small yellow-green trees at the north end | rear_side, top, rear |
| Penthouse — glazing, solid end, roof plant | **conforms with reservations (P2-7)** — glazed to the pool deck, solid bay with a door, AHU box and round fan on the roof; glazed run longer than source and door on the west wall | pool_deck, top, front_corner |
| East block roof — skylights, plant | **conforms** — membrane roof, two skylights, small plant boxes | top, aerial |
| White facade under the overhang | **conforms** — one plain white plane with a straight coping, no openings, stray plate gone | right_side, aerial (junction crop) |
| Plaza — paving bands | **conforms with reservations (P2-4)** — two-tone bands present but much lighter in value than the source granite | front, plaza_planters, top |
| Plaza — grass planters | **conforms** — two raised planters of tall straw grasses plus the low planted strip on the east edge | top, right_side, plaza_planters |
| Plaza — bollards | **conforms** — grey bollards along the south-west plaza edge | right_side |
| Plaza — lamp posts | **conforms** | plaza_planters, front, right_side |
| Sidewalks | **conforms** — concrete west sidewalk and plaza-to-street edge on the east | front_corner, right_side, top |
| Street trees | **conforms with reservations (P2-5)** — eight trees in square pits along the west sidewalk | front_corner, left_side |
| Streets and crossings | **conforms** — west and east streets with lane markings and crossings at the corners | top, aerial |
| Parked cars | **conforms** — cars on the east street, a van on the west | right_side, aerial, top |
| Neighbours | **conforms** — brick mid-rise and residential blocks on all sides, coherent heights | aerial, rear_side, front |
| Materials hierarchy | **conforms** — white precast, grey glass, honey CLT, grey granite, teal water, straw grasses, green foliage; CLT is a duller mustard than the source honey, plaza lighter (both P2) | all whole-envelope views |
| North and east fronts | **not judged for fidelity** (no source) — coherent with the white-frame/recessed-glazing grammar; see P2-8 for the missing base condition | rear, right_side |
| Building interiors, shell interior, plaza people | **not judged** — authored assumptions / not modelled per brief | interior, glass_close, rim_interior |

## 4. Camera validity

No view is invalid: in all eighteen renders the target is on screen, unclipped and legible at full resolution. Qualifications:

- **pool_deck** — roughly 60% of the frame is an unbroken flat teal plane; the deck, loungers, roof garden, penthouse and parapet are compressed into a thin band across the upper third, and the west edge where the weir and trough belong is never resolved. Legible but the weakest composition in the set; it does not evidence the thing it exists to evidence.
- **left_side** — six opaque low-poly canopies occlude essentially the whole west ground floor. The upper two storeys, spandrels, parapet and balustrade are fully legible, and the ground-floor condition is evidenced instead at the south-west corner by `entrance` and `wall_base_contact`, so the view is not invalid — but it carries no ground-floor information.
- **rear** — a shaded north front against a light sky; low contrast and legible only at full resolution (it reads as a dark block on phone-04).
- **right_side / aerial** — valid cameras, correctly framed and unoccluded. The shell reading as a grounded near-vertical block in both is a model defect (P0-1, P0-2), not a camera defect.
- **climbing_face** — valid. A small dark cube sits at the foot of the white facade at approximately (765–800, 1010–1060); the locked oblique does show a bin and a black mat at the shell's foot, so this is noted rather than called a stray.
