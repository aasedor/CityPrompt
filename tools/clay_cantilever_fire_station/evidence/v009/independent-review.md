# Independent holistic review: clay-cantilever-fire-station v009 (RLASM v6.1)

Reviewer: independent; I judged only the pixels of the 3 locked sources, the 18 renders and the 4 phone boards. I did not read any source code, build report or builder note.

## 1. Verdict

**VISUAL_REWORK_REQUIRED**: massing, tower, loggia soffit and roof are fixed, but on the primary south elevation every apparatus bay still has an opaque black header band where the source shows a glazed transom. As a result the glazed hall still reads as about a third of the facade height, and that v008 P1 is only partly resolved.

Counts: P0 = 0, P1 = 1, P2 = 7

## 2. Findings table

| # | severity | view(s) with pixel regions | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | front.png: bays x 500-920, y 647-670 (flat black band; the measured strip has RGB about 10,10,10 with std about 1). apparatus_bays.png: x 245-775 and 915-1440, y 165-320 (mean RGB 11-19, std 1.2-9, no mullions, no reflection). glass_close.png: y 0-75. interior.png: y 270-385 (the same band is solid from inside). facade_close.png: y 600-705. | Above each of the four glazed bay doors there is a solid matte-black header about 20% of the hall height. Source front.png (x 470-880, y 440-500) shows a glazed transom row with mullions and a lit interior from the soffit edge down to the open bays. Because of the band, the visible hall glass on the main elevation is about 81 px of a 257 px facade (0.32). The source equivalent is about 175 of 378 px (0.46). On the front view the box/hall reading is about 1.42 (box 494-645, hall to recessed bay base 645-751). The same measurement on the source gives about 1.16. The hall still reads as the low, "about a third" band the v008 review flagged. | The hall was raised to 8.0 m, but the space between the door head and the soffit was filled with an opaque dark header instead of a glazed transom. | Replace the header band in each bay (and the matching band in the west curtain-wall bay and east entry) with a glazed transom: the same glass material as the doors, 3-4 vertical mullions per bay that align with the door mullions, and a transom rail at door-head height. Glass should then run continuously from the soffit trim to the apron. Re-render front, apparatus_bays, glass_close, facade_close and interior. |
| 2 | P2 | front.png: y 645-646 and the notch edge at x 950-1030, y 645-697. soffit_corner.png: the trim along the soffit edge. | The "lit soffit edge" is a 1-2 px cream trim line. At whole-envelope scale it barely registers, whereas in the source the edge is the dominant glowing outline. | The trim is modelled as a thin unlit cream strip. | Widen the trim to about 0.15-0.2 m and give it a slightly emissive warm cream so it reads at the front-view scale. |
| 3 | P2 | apparatus_bays.png: piers at x 105-245 and 775-915. front.png: piers between bays. | The bay piers are wide (about 26% of door width), pale concrete-grey and matte. The source columns (src_bays region of front.png x 590-605, 685-700, 765-785) are slimmer, dark steel/glass-clad and greenish-grey. | A placeholder pier material and width. | Narrow the piers to about 0.6 m and use a dark grey-green glass/metal cladding colour from the source. |
| 4 | P2 | glass_close.png: the whole door. apron_contact.png: x 150-1300, y 100-680. | The bay door glass is milky: the appliances are visible but washed out. | Glass roughness/tint is too high. | Lower the roughness and tint so the red appliances read clearly through the glass, as in the source. |
| 5 | P2 | tower_clock.png: x 550-880, y 585-645. front.png: x 1060-1128, y 380-390. | The red sign band is about 0.6 of the face width and sits one clock radius below the clock. In the source, the LED band spans nearly the full tower face directly under the clock. | Band width and offset. | Widen the band to about 0.9 of the face width and move it up to sit just under the clock disc on both clock faces. |
| 6 | P2 | loggia_close.png: glazing x 240-1050, y 120-620, railing y 555-835, pale rectangles x 380-1050, y 385-460, ellipse x 905-975, y 165-185. | The loggia glass is a 3-row x 13-column grid with a balustrade in front of it. In the source the glazing is a single tall tier of fine vertical mullions with no visible railing. Through the glass the far-wall windows and a ceiling-light ellipse are visible, which is busy rather than a dark interior. | Generic curtain-wall grid and interior props. | Use tall single-tier panes with a fine vertical rhythm, drop or lower the railing behind the glass line, and darken the upper-level interior behind the loggia. |
| 7 | P2 | top.png: memorial wall x 340-350, y 660-790, and shelter x 1090-1170, y 825-865. front_corner.png: wall x 540-610, y 840-910. | The memorial wall runs north-south along the west edge. In the source (oblique.jpg x 145-330, y 730-840; top.jpg x 235-345, y 590-615) it runs east-west and faces south. The shelter's long axis is east-west; the source shelter (top.jpg x 905-985, y 615-770) runs north-south beside the tower. | Rotation of the forecourt props. | Rotate the memorial wall 90 degrees to face the south plaza west of the bays, and rotate the shelter 90 degrees. |
| 8 | P2 | rear.png: x 400, face 499-664 and hall 664-801. right_side.png: x 800, face 509-659 and hall 659-782. | The true box/hall ratio on the unrecessed elevations is about 1.2-1.3, a little above the source's about 1.1. This is acceptable once finding 1 restores the glazed transom. | Upper level and parapet together are slightly taller than the hall. | Optional: trim the parapet by about 0.3-0.5 m. |


## 3. Source conformance checklist

| Item | Status | Views used |
|---|---|---|
| Silhouette (long oxblood box over a glazed hall, east-end drop, west-face notch, proud SE tower) | conforms | front.png against source front.png; front_corner.png against oblique.jpg; left_side.png |
| Storey count (one cantilevered upper level over one tall hall; no second upper floor) | conforms. The rear shows a single window row (rear.png y 563-600), the loggia glass has no slab through it, and the south face has one cluster of slot windows. | rear.png, rear_side.png, loggia_close.png, front.png |
| Bay count and rhythm (west curtain-wall bay, four apparatus bays, glazed entry under the east drop) | conforms in count and rhythm (pitch about 109 px in front.png). The bay head deviates (finding 1) and the pier material deviates (finding 3). | front.png, apparatus_bays.png, facade_close.png |
| Cantilever and lit soffit | conforms in geometry: the soffit is dark oxblood with the edge trim continuous round the notch and corner. The lit quality is weak (finding 2). | soffit_corner.png, facade_close.png, front.png |
| Loggia (deep glazed recess in the west face of the upper level, framed by the box, dark oxblood ceiling) | conforms. The recess has deep returns, the ceiling is dark oxblood and there is no strip light. The glazing grain deviates (P2, finding 6). | loggia_close.png, left_side.png, front_corner.png |
| Tower and clock (slender glass tower at the SE corner, proud of the front, clocks high on two faces, red sign band) | conforms. Tower height is about 1.86 building heights (front.png: 277-755 against 494-751); the source is about 1.79. Width is about 1.05 bay pitch (115/109 px). The clock is at 14% from the top, matching the source. The sign band is narrow (finding 5). | front.png, tower_clock.png, right_side.png, aerial.png |
| Forecourt elements (flagpole, memorial wall, benches, flat shelter, apron, bollards) | all present. The orientation of the memorial wall and shelter deviates (finding 7). | top.png, front.png, front_corner.png, apron_contact.png |
| Materials hierarchy (oxblood panel box, glass hall, dark grey base on west/north, white membrane roof with red coping, glass tower) | conforms except for the pale piers and the opaque bay headers (findings 1 and 3). The roof is clean white with no raised plate. | top.png, aerial.png, rear_side.png, apparatus_bays.png |
| North face | not visible in any source. It is coherent: one oxblood window row over a grey base, with a door and a roller door. | rear.png, rear_door.png |

## 4. Camera validity

All 18 views are valid. No target is occluded or clipped, and every view is legible. In soffit_corner.png the flagpole crosses the frame at x 585-625, but it does not hide the corner. In tower_clock.png the top of the tower and its parapet are in frame. The interior view is dim but legible.

## 5. Status of the v008 findings in the pixels

1. **Glazed hall too low (about a third of the height) and an extra upper floor with two window rows and a slab through the loggia glass:** partly resolved.
   - Resolved: the second floor, the second window row and the loggia slab are gone (rear.png, loggia_close.png). The true box/hall ratio is now about 1.2-1.3 (rear.png, right_side.png).
   - Not resolved: the glazed transom over the bay doors is missing. An opaque black header takes its place, so on the front elevation the hall glass still reads as about 0.32 of the facade height against 0.46 in the source. This is carried as P1 finding 1.
2. **Clock tower too short and thin:** resolved. It now stands about 1.86 building heights tall and about 1.05 bay pitch wide, with the clocks at the source's relative height.
3. **Loggia ceiling pale with a strip light:** resolved. loggia_close.png shows a dark oxblood ceiling (y 40-120) and no strip light. Only a faint interior-light reflection is visible behind the glass (P2, finding 6).
4. **Raised oxblood plate on the white roof along the west edge:** resolved. top.png and aerial.png show a clean white roof with only the perimeter red coping (top.png x 428-433).
