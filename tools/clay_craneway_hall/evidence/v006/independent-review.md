# Independent RLASM v6.1 holistic review: crane-way hall v006

Reviewed: sources/front.png, sources/oblique.jpg, sources/top.jpg; all 18 renders at full resolution; boards phone-01 to phone-04. I did not read any build code, reports or notes. Every statement below comes from the pixels.

## 1. Verdict

**VISUAL_REWORK_REQUIRED.** The monitor orientation and the west nave glazed band are now correct. But the aisle section is still too low, so the long sides still show a wide blank aisle roof. The west-end aisle upper storeys are still low wedges, and the roof monitors are read as small tall "doghouse" boxes, not the long low gabled monitors in the sources.

**Counts: P0 = 0, P1 = 3, P2 = 7**

## 2. Findings

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | aerial (aisle roof band approx. x 330-1060, y 470-650); architecture_close (blank roof y 545-720 across full width); monitor_close (blank plane approx. y 520-870, about 40 % of frame); front_corner (x 470-1080, y 500-590); front / rear (glazed band only y 518-545 against a lattice storey of y 545-650) | Above the gallery, the long elevations still show a wide, blank lean-to aisle roof that is about as tall in view as the glazed band below it. The aisle-upper glazed band is only about 0.25 of the lattice-storey height. In the sources (oblique crop x 550-1195, y 150-700; front x 0-490, y 110-400), the order is nave roof, clerestory, a **narrow** aisle-roof strip, then a tall mullioned band (about 0.4 of the lattice storey), then the railed gallery on its bracketed beam. The gallery and its brackets are now present. The narrow-strip and tall-band proportions are not. | The aisle eave is too low relative to the nave (aisle/nave eave height about 0.72 in left_side against about 0.85-0.9 in the sources), so the lean-to roof has to cover the full aisle depth at a shallow pitch. | Raise the aisle upper-storey wall and eave until the aisle roof meets the nave wall just below the clerestory sill. Make the aisle-upper mullioned band about 0.4 of the lattice-storey height, so the aisle roof reads as a strip of at most about 1/4 of the band height in architecture_close and aerial. Keep the gallery and brackets as they are. |
| 2 | P1 | left_side (north aisle x 440-575 and south aisle x 865-1000, y 515-560); gable_mouth (north aisle x 230-415, y 410-510; south aisle x 1130-1420, y 300-470) | At the west end, each aisle's upper storey is a short lean-to wedge about 40 px tall, about 1/4 of the solid lower wall below it (155 px). Its sloping X-strut reads as a roof truss, not as an upright open frame. The sources (front x 495-690, y 120-340; oblique north aisle x 80-215, y 370-490 and south aisle x 560-740, y 410-560) show **full-height open truss frames** rising to about the bottom of the nave glazed band. | Same low aisle section as finding 1. | Carry the aisle upper storey up to the raised eave from finding 1. Show it as an open rectangular steel frame with posts, a top chord and truss diagonals that stand clear of the solid lower wall. The frame should be at least about 0.6 of the lower-wall height. |
| 3 | P1 | top (nine monitors about 45x50 px on a 190 px nave, e.g. x 600-645, y 455-505); architecture_close (x 50-310, y 0-270 and x 890-1190, y 40-290); aerial crop (each monitor about 1.5x as tall as it is wide); front (triangles x 405-450, y 415-465, about 45 wide x 50 tall) | The monitors now run across the hall in three staggered rows of three, but they are small, near-square, tall solid boxes with a short window strip high up. They read as dormers or chimneys. The sources (oblique crop x 140-490, y 0-270; top x 360-990, y 90-530) show long, **low** gabled monitors. Each spans about 0.4 of the nave width across the hall, has a shallow, wide gable triangle (width greater than height) and a continuous glazed strip along almost the full length of each long face, sitting directly on the roof plane. | The monitor footprint and height were kept from the old along-hall version and only rotated. The box height is excessive. | Lengthen each monitor across the hall to about 0.4 of the nave width and keep its depth along the hall about 0.2 of the nave width. Cut the solid wall height to near zero, so the glazed strip starts at the roof plane. Lower the gable pitch so the triangle is about twice as wide as it is tall. Make the gable-end triangles solid (see P2-8). |
| 4 | P2 | crane_interior (x 420-1020, y 480-540, orange block x 760-870, y 490-530); interior (only an orange sliver at x 780-815, y 0-15); gable_mouth (x 450-1080, y 385-425) | There is a crane girder with a trolley block, but no hook or hoist. In interior, looking down the nave, no crane bridge is legible. The source oblique shows the bridge, walkway rails and a hanging yellow hook in the gable mouth. | The crane is modelled as a girder only. | Add a hoist block and a hanging hook under the trolley in the gable mouth. Place the bridge so it is visible in interior. |
| 5 | P2 | left_side (x 615-825, y 585-710); gable_mouth (x 515-995, y 555-895) | One closed opening with three flush leaves. The source shows two large leaves with a dark open gap between them (front x 870-900; oblique x 360-395). | Door is modelled as one closed slab. | Slide one leaf part open to leave a dark gap with a visible jamb. |
| 6 | P2 | facade_close (struts x 350-385, y 235-345; x 800-835, y 275-370); side_doors (x 455-500, y 0-130) | The gallery bracket struts start at the X-brace crossing in the middle of a panel, not at a column node. | Bracket anchor is set on the brace centre. | Start each bracket at the lattice-column chord or a panel node. |
| 7 | P2 | right_side (x 410-440 and x 1000-1030, y 540-560) | The gallery railing ends stick out past the east aisle walls like floating stubs. | The gallery is longer than the aisle walls. | Stop the gallery at the end wall, or return the railing against it. |
| 8 | P2 | aerial crop (window strips on gable-triangle faces, e.g. x 415-460, y 55-75) | Window strips are placed in the monitors' gable-end faces. In the sources, the gable ends are solid corrugated and the glazing is on the long faces. | Glazing is applied to all faces. | Make the gable ends solid. Glaze the long faces only. |
| 9 | P2 | facade_close (awnings x 460-750, y 570-640); yard_sidings; glass_close | The lower-window hoods are thin, shallow flat awnings. The source shows deeper, sloped pent hoods per bay that are clearly legible (oblique crop x 300-560, y 330-550). They need not span the whole aisle, which was the v004 defect. | The hoods were cut back too far when v004 was fixed. | Increase the hood projection and slope modestly, keeping them per window. |
| 10 | P2 | front | Straight orthographic-like south elevation. The building fills about 60 % of the width and 25 % of the height, and the camera role does not match the source front, which is a low perspective of the south-west corner. It is legible, and front_corner covers the source role. | Camera choice. | Optionally move "front" toward the source front's low south-west corner viewpoint. |

Window depth checked: in glass_close (x 80-645, y 600-900) a lighter left jamb return and a sill are visible inside the frame, so the openings have depth. No finding.

## 3. Source conformance checklist

| Item | Status | View used |
|---|---|---|
| Silhouette (stepped nave and aisles) | deviates: steps are present but the aisles are too low (findings 1-2) | left_side, right_side, aerial |
| Section (nave and aisles) | deviates: aisle eave about 0.72 of the nave eave; wide aisle roof; short aisle upper storey | left_side, architecture_close |
| Bay rhythm and bracing | conforms: lattice X-braced columns between hooded windows at a regular bay rhythm on both long sides | facade_close, yard_sidings, side_doors, front, rear |
| Gable mouth and doors | conforms (P2-5): solid lower wall, green sliding doors, nave mullioned glazed band directly under the triangle, crane zone open below | left_side, gable_mouth, crane_interior |
| Monitors and clerestory | clerestory conforms; monitors deviate in proportion (finding 3). Orientation (across the hall) and count (9, in 3 staggered rows of 3) conform | top, architecture_close, aerial, front |
| Crane and interior | partly conforms: girder and trolley present, no hook (P2-4); interior is coherent (nave columns, clerestory, aisle windows) | crane_interior, interior, gable_mouth |
| Stair | conforms: two flights with a landing at the south-west corner, grounded at the foot, landing on the gallery, landing posts reach the ground | stair_contact, front_corner, front |
| Yard and sidings | conforms: concrete apron, two sidings on the north side, boxcar on wheels sitting on the rails | top, rear_side, yard_sidings, right_side |
| Materials hierarchy | conforms for clay: light-grey cladding, dark mullions, green doors, orange boxcar | all |

## 4. Camera validity

No view is invalid. In all 18 renders the target is unoccluded and unclipped. The close views (stair_contact, gable_mouth, architecture_close, monitor_close) crop on purpose and stay legible. The "front" view is small in the frame and does not match the source's camera role (P2-10), but it is legible.

## 5. Prior-version findings

| Prior finding | Status in v006 pixels | Evidence |
|---|---|---|
| v005 P1: monitors ran along the hall (11 monitors, glazing facing N/S) | **Resolved** for orientation and count; the new proportion defect is finding 3 | top: 9 monitors in 3 staggered rows of 3; front/rear: gable triangles face the long sides; left_side: the glazed faces look west |
| v005 P1: long sides stepped straight from the lattice wall to a wide blank aisle roof (no gallery, no tall glazed band, no narrow strip) | **Partly resolved** | Railed gallery on bracketed beam now present (facade_close, architecture_close). The mullioned band is present but short (about 0.25 of the lattice storey). The aisle roof is still wide and blank (aerial, architecture_close, monitor_close), see finding 1 |
| v005 P1: west nave upper storey open with no glazing under the triangle; aisle upper storeys not full-height truss frames | **Partly resolved** | Nave mullioned band directly under the triangle with the crane zone open below: resolved (left_side x 575-860, y 445-485; gable_mouth; crane_interior). Aisle upper storeys are still short wedges (finding 2) |
| v004 P1: solid west gable lower wall | Resolved (remains so) | left_side, gable_mouth: green doors in the lower wall, open upper storey |
| v004 P1: deep pent roofs over every aisle bay | Resolved (remains so); hoods are now somewhat too shallow (P2-9) | facade_close, yard_sidings |
