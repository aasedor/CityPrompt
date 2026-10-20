# Independent holistic review: Halifax Public Gardens clay, v003 (RLASM v6.1)

Reviewer: independent, not the builder. I judged only the rendered pixels against the three locked sources (sources/front.png, sources/oblique.jpg, sources/top.jpg). I opened all 18 renders at full resolution and the four phone boards. I checked bed-scale detail with zoomed crops, which are saved in a separate new folder, `/tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/hpg_v003_review_crops_70758b3f/`.

## 1. Verdict

**VERDICT: VISUAL_REWORK_REQUIRED.** The plan, gate, fence, bandstand, trees and context still hold, and both v002 P2 claims (the bench and the hip rolls) are true. But the carpet-bed plant heads still read as faceted gems at bed scale. They have hard 6- to 8-sided outlines and creased crowns, the green heads are flat hexagonal tiles, and at eye level the rows look pointed. So the v002 P1 (the v001 plant-form finding) is still open after its second targeted fix.

Counts: P0 = 0, P1 = 1, P2 = 5

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | carpet_beds, inner_lawn_beds, bandstand (lower-right corner and ring bed), loop_benches, gate_piers_fence, front, mature_trees, rear, rear_north, right_side/left_side at bed scale | The heads are now smaller (about 0.4 to 0.5 m), grounded, densely packed and colour-banded. They read as a cushion only at aerial/top/front_corner distance. Seen close (carpet_beds lower half, inner_lawn_beds bed), every head has a hard hexagonal or octagonal outline, a flat polygonal crown cap and a creased shoulder ring. The bed reads as a honeycomb of hexagonal pebbles or cut gems, not flower heads. The green "foliage" heads are flat dark-green hexagonal tiles lying among them. In the bandstand corner (x 1270-1440, y 990-1080) the nearest heads are flat-shaded hexagonal prisms with sharp facet edges. At eye level (gate_piers_fence x 0-500, y 500-610; front y 650-700; mature_trees right edge) the shoulder-plus-crown profile gives every head a pointed peak, so the bed edges read as rows of onion-dome or sawtooth crystals. The builder's claim "smooth-shaded so no facets show" is false in the pixels. | The lathed lobe primitive has too few radial segments (about 6 to 8) and too few profile rings. The crown is a separate cone-like ring that ends in a point. Smooth normals cannot hide a 6-sided outline or the crease where the shoulder ring meets the crown. The foliage heads are flattened caps of the same 6-gon. | Rebuild the bed head with at least 16 radial segments and a rounded crown with no apex vertex (a hemispherical or squashed-dome cap, crown height at most 0.6 of the radius). Add per-head jitter of ±15% in scale, ±10° in rotation and ±3 cm in height so the outlines break up. Make foliage heads lower mounded domes, not flat caps. Leave a little soil showing between some heads. Re-render carpet_beds, inner_lawn_beds, bandstand, gate_piers_fence and rear_north, and confirm by zooming that no polygonal outline or point shows. |
| 2 | P2 | mature_trees, side_entrance, left_side, right_side, rear_side, front | Shade-tree crowns are coarse low-poly clusters with large flat facets. In mature_trees the crown reads as a faceted boulder on a trunk. The trunks are grounded and the volume and placement are right. | Low-subdivision icosphere crown lobes with flat shading. | Subdivide the crown lobes once, smooth-shade them and add 2 to 3 more lobes per crown. |
| 3 | P2 | rear_north, rear, left_side, bandstand_roof | Free-standing hydrangeas sit on a green base with an octagonal outline and sharp corners, which reads as a faceted plinth under the white lobes. They are grounded and nothing balances on a vertex. | Low-segment base ring on the shrub primitive. | Raise the segment count of the base skirt to 16 or more and roll its upper edge. |
| 4 | P2 | gate_arch, front, gate_piers_fence | The C-scrolls and the crossed scrolls on the sign arch are chains of short box segments with visible joints and small notches. They are the same segment-joint artefact that was just fixed on the hip rolls. They do touch the arch top, so nothing floats. | The scrolls are built as discrete box segments. | Sweep each scroll as one closed tube, using the same method as the fixed hip rolls. |
| 5 | P2 | front | The foreground bench stands on the light-grey public sidewalk outside the gate line. The source front shows it on the brick paving inside the gateway. It is now correctly turned with its backrest towards the camera. | Bench placed at the sidewalk y-coordinate. | Move it about 2 to 3 m north onto the brick forecourt inside the gate and keep the orientation. |
| 6 | P2 | rear | Through the gap between the two context buildings behind the gate (about x 670-770, y 270-290), a dark grey band shows where the modelled ground ends against the sky. | The ground plane ends just past the south context row. | Extend the ground plane or the context row so the gap shows built frontage or distant ground. |

No P0. One P1 (row 1). P2 rows 2 to 6 are polish only.

## 3. Source conformance checklist

| Item | Status | View(s) used | Note |
|---|---|---|---|
| Block ratio (about 43 x 57 m, long axis north-south) | conforms | top, aerial | About 650 x 900 px in top, a ratio of about 0.72 (target 0.75). |
| Straight brick axis from the south gate to the north fence | conforms | top, rear, rear_north | |
| East-west cross path meeting the axis at a round paved circle | conforms | top, aerial, left_side | The circle has concentric ring joints. |
| Oval loop: Y off the axis north of the bandstand, swelling to the cross path near the side fences, straight legs returning south to the side piers | conforms | top, aerial, front_corner, rear_north | The Y sits north of the north leaf lawns. The legs reach the side piers. |
| Four leaf-shaped inner lawns (north ones rounded leaf islands, corners filleted with edging) | conforms | top, top_center crop, rear_north | |
| Four outer lawns | conforms | top, aerial | |
| Path paving colour (plain brick) and granite edging | conforms | top, carpet_beds, loop_benches, inner_lawn_beds | Edging follows every fillet. |
| Gate: tall brick piers on granite bases | conforms | front, gate_piers_fence, front_corner | |
| Gate: iron lanterns on the piers | conforms | front, gate_arch | |
| Gate: iron sign arch with crest and two-line sign (abstract lettering) | conforms (P2 #4 on the scroll finish) | gate_arch, front | |
| Gate: open double gates | conforms | front, front_corner, top | The leaves swing inward. |
| Gate: lower ball-capped side piers with side gates where the loop legs enter | conforms | front, front_corner, gate_piers_fence | |
| Fence: pickets, rails, posts, granite curb | conforms | gate_piers_fence, side_entrance, mature_trees | |
| Fence: continuous round the block | conforms | aerial, rear_side, top | Broken only at the entrances. |
| Bandstand: octagon, posts | conforms | bandstand, top | 8 posts. |
| Bandstand: fretwork arches | conforms | bandstand (zoom) | Simplified arched brackets. Acceptable for clay. |
| Bandstand: balustrade, lattice skirt, front stair | conforms | bandstand, rear_north | |
| Bandstand: pink-copper ogee roof, hip rolls and finial | conforms | bandstand_roof, bandstand | The hip rolls are continuous tubes with no notches. Ball-and-spike finial. |
| Bandstand: ring bed | deviates (P1 #1, plant form) | bandstand, top | Layout and colour blocks are right. The heads are faceted. |
| Carpet beds: leaf/crescent shape and soil edge | conforms | top, inner_lawn_beds, carpet_beds | Heads stay inside the soil outline (checked in plan on top). |
| Carpet beds: hydrangea spine and lavender/purple/pink bands | conforms | top, front_corner, carpet_beds | |
| Carpet beds: plant form | deviates (P1 #1) | carpet_beds, inner_lawn_beds, gate_piers_fence, loop_benches | Faceted hexagonal heads with pointed crowns. |
| North-axis strip beds | deviates (P1 #1, plant form at close range) | rear, rear_north, top | Banding is right and the heads stay inside the soil (top). The heads read as polygonal balls. |
| Shade trees: count and placement (two big south-corner trees, north-corner clusters) | conforms | top, aerial, front_corner | |
| Shade trees: trunks at grade | conforms | mature_trees, rear_side | Crown finish is P2 #2. |
| Benches along the loop, with front arm supports, facing the path (north arc included) | conforms | loop_benches, rear_north (zoom), top | |
| Lamps at the circle and the side entrances | conforms | front_corner, side_entrance, bandstand | |
| Context streets on four sides, brick mid-rises and glass office block | conforms | aerial, rear, front | The south row sits beyond the south street (rear). There is a world-edge gap (P2 #6). |
| No coplanar paving or bed surfaces (no z-fighting) | conforms | all | No flicker or striping seen. |
| All vertices at or above grade | conforms | all detail views | No sunken or floating parts. The arch scrolls touch the arch. |
| Framed locked views (front vs front, front_corner/aerial vs oblique, top vs top) | conforms | boards/phone-01, front, front_corner, top | The front framing closely matches the source composition. front_corner matches the oblique. |

## 4. Camera validity

- No locked or detail view has its target occluded, clipped or illegible.
- aerial: no context roof blocks it. The garden, all four bounding streets and the context frontages are readable.
- front, front_corner, top: all frame the asset completely and match their source roles.
- bandstand_roof: the roof fills the frame as intended. The hip rolls and finial are legible.
- mature_trees: the crown dominates the frame as intended, with the trunk base visible at grade.
- side_entrance: the ball-capped piers, fence and lamp are legible, with the garden beyond.
- The brief's view list also names facade_close, architecture_close and glass_close. These do not exist in renders/ (18 files are present, matching the stated count of 18). They are building-template names and have no counterpart for this open-space asset. I raise no finding for them.

## 5. Previous-version findings: resolved in the pixels?

| Previous finding | Status in the v003 pixels |
|---|---|
| v002 P1 #1 / v001 P1 #2 (beds): every bed plant was one large faceted icosahedron, so the beds read as piles of gems | **Not resolved (partly improved).** The heads are smaller, grounded, densely massed and correctly colour-banded, so the beds read as cushions at plan and aerial distance. At bed scale they are still hard-edged hexagonal or octagonal pebbles with polygonal crowns and flat green hexagonal tiles, and they look pointed at eye level. The "smooth-shaded, no facets" claim is false. Carried forward as P1 #1. |
| v002 P2: front bench should face into the garden with its backrest towards the camera | **Resolved.** The back posts occlude the slats, the arm supports are on the far side, and the seat faces north into the garden. The new P2 #5 is only about its position on the sidewalk. |
| v002 P2: the eight hip rolls should be continuous tubes with no segment joints or notches | **Resolved.** bandstand_roof shows eight smooth continuous rolls from the finial collar to the capped eave ends. No notches. |
| v001 P1 #1: aerial must be unblocked by any context roof | **Holds.** |
| v001 P1 #2 (shrubs): free-standing shrubs and hydrangeas must be grounded lobe clusters, none balanced on a vertex | **Holds.** All are grounded. The octagonal base outline is P2 #3. |
| v001 P1 #3: loop Y join on the north axis, rounded north leaf islands, filleted lawn corners with edging | **Holds.** (top, rear_north) |
| Long paths plain brick colour | **Holds.** |
| Every bench has front arm supports | **Holds.** (loop_benches, rear_north) |
| South context row and far sidewalk beyond the south street | **Holds.** (rear, aerial) |
| gate_piers_fence has no lamp mid-frame | **Holds.** The only lamp is a small background post at the left. |
| North-arc benches face the path | **Holds.** (rear_north zoom: front legs and arm supports are on the path side) |
| v001 strengths: brick-pier gate with lanterns and gilded sign arch; white octagonal bandstand with pink-copper ogee roof and flower ring; four carpet beds; mature shade trees; iron fence on granite curb; side gates | **All still present and legible.** (front, gate_arch, bandstand, top, aerial, gate_piers_fence) |
