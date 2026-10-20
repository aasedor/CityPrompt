# Independent holistic review: Halifax Public Gardens clay candidate v002 (RLASM v6.1)

Reviewer: independent; did not build the candidate. I opened all 18 render PNGs at full resolution, the three locked sources (front.png, oblique.jpg, top.jpg) and the four phone boards. Zoomed crops were written only to the new folder `/tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/hpg-v002-review-crops-3a6c6332/`. Builder notes, metadata and counts were not accepted as proof.

## 1. Verdict

**VISUAL_REWORK_REQUIRED**: the three v001 P1s are fixed in the pixels. However, every flower in the carpet beds, the bandstand ring bed and the north-axis strip beds is still a single large faceted icosahedron, so the beds read as heaps of white, pink, lavender and green gems in every close view. This is the same defect the v001 review raised, and so far it has been fixed only for the free-standing shrubs.

Counts: P0 = 0, P1 = 1, P2 = 6

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | carpet_beds, inner_lawn_beds, bandstand, rear_north, rear, bandstand_roof, side_entrance (also legible in front_corner, left_side, right_side) | Each bed plant is one large faceted icosahedron, roughly 0.7 to 1 m across. The carpet beds are rows of these packed gems; in carpet_beds the near white "hydrangeas" show the five-triangle icosahedron apex at full frame size. In the bandstand ring bed (bandstand, crop ring_bed_white), single white, pink and lavender icosahedra lie tipped against the lattice skirt like crystals. The north-axis strip beds in rear_north and rear alternate single white, green and lavender polyhedra on bare soil. None of them reads as a mounded hydrangea or a low flower carpet; they read as gems or boulders, which is exactly the v001 P1 #2 reading. | The v001 fix replaced only the free-standing shrub and hydrangea primitive with a grounded lobe cluster. The bed-fill instancer still places the old single-icosahedron flower primitive. | Instance the bed fill with the same grounded lobe-cluster grammar: a low flattened base mound with its base ring sunk into the bed soil, plus 3 or 4 smaller flower-head lobes. Use smaller heads (about 0.3 to 0.5 m) at higher density with a lower overall profile, so that each bed reads as a continuous mounded carpet. Keep the white hydrangea spine and the lavender, purple and pink bands, and apply the change to the carpet beds, the ring bed and the north strip beds. Re-render carpet_beds, inner_lawn_beds, bandstand and rear_north. |
| 2 | P2 | front | The foreground bench faces the camera and the street. The seat's front edge, the front arm supports and the nearer legs are on the camera side, and the backrest stands on the garden side (crop front_bench). The source has the bench back-to-camera, facing the gate. The builder's claim that it "now has its back to the camera" is **not** true in the pixels. | The bench is rotated 180 degrees about Z relative to the intent, or the rotation was not applied to this instance. | Rotate the front-view bench 180 degrees so that its backrest is nearest the camera and the seat faces north toward the gate. |
| 3 | P2 | bandstand_roof (faintly in bandstand) | All eight hip rolls and the eave edges still show regularly spaced dark-brown notches or gaps, about every 0.4 to 0.6 m (crop roof_hips). The builder's claim of "no dark notches" is **not** true in the pixels. | Hip-roll segments still butt or leave gaps that expose a darker underside or backface. | Make each hip roll one continuous swept or bent tube along the ogee curve, or extend each segment so they overlap, and give the inside the same copper material. |
| 4 | P2 | front, gate_piers_fence, aerial | The gate forecourt apron between the sidewalk and the gate has long transverse plank-like joints that read as timber decking (crop aerial_gate). The source shows brick paving there. The long garden paths are plain brick colour as claimed. | The forecourt still uses the old joint-line pattern. | Make the apron plain brick colour, or use a small brick/herringbone joint scale matching the circle courses. |
| 5 | P2 | loop_benches, rear_north, top | Loop benches sit 2 to 3 m back from the path edge on the lawn rather than at the granite edging (they do face the path, on the outer side of the arcs). | The bench offset is measured from the path centreline with too large a value. | Move the benches out to about 0.5 m beyond the edging. |
| 6 | P2 | rear_side | The two nearest NW-corner canopies cover roughly a third of the frame, including most of the NW outer lawn and part of the west fence. The bandstand, beds, paths and gate remain legible, so the camera stays valid. | The camera is low over the NW tree cluster. | Raise the camera by about 5 to 8 m or shift it outboard of the NW trees. |
| 7 | P2 | (view set) | The brief's detail list names facade_close, architecture_close and glass_close, but no such renders exist. 18 renders exist, which matches the stated "18 views". These are building-template names that do not apply to an open space, so no pixels are affected. | The view list was carried over from the building template. | Remove the three names from the brief or view manifest, or map them to open-space detail roles. |

## 3. Source conformance checklist

| item | status | view(s) used | note |
|---|---|---|---|
| Block ratio and orientation (long axis N-S) | conforms | top vs top source | Render fence block is about 650 x 860 px (1 : 1.32); source is about 540 x 745 px (1 : 1.38); the brief's 43 x 57 m gives 1 : 1.33. |
| Straight axis south gate to north fence | conforms | top, rear_north, front_corner | Continues to the north entrance piers. |
| E-W cross path to both side fences | conforms | top (crop top_cross), left_side, right_side | |
| Round paved circle with concentric and radial courses | conforms | top, bandstand, left_side | |
| Oval loop: south legs straight from side gates, S-bend out to cross path, north arcs swing in | conforms | top vs top source, front_corner vs oblique | Loop crosses the cross path about 0.62 of the way from the circle to the fence; the source is about 0.65. |
| North Y junction (v001 #3) | conforms | top (crop top_north), rear_north, front_corner | The arcs join the axis in a Y about 10% of the block length from the north fence; the source is about 7%. |
| Four leaf-shaped inner lawns | conforms | top, rear_north, rear | North lawns are leaf islands with rounded tips pointing up the axis. South lawns are long curved leaves between the axis and the legs, as in the source. |
| Filleted lawn corners at circle/axis/cross path and at the loop/cross-path crossings | conforms | top_cross, rear_north, inner_lawn_beds | Granite edging follows the rounded outlines. |
| Four outer lawns | conforms | top, aerial | |
| Path paving colour | conforms | front_corner, top vs oblique, top source | Pinkish-grey brick tone. Mean RGB about (149,141,135) against the source's about (173,151,133) in sun and (144,141,137) in shade. |
| Path joints | deviates (P2 #4) | front, aerial | Long paths are plain. The forecourt apron has plank joints. |
| Granite edging on every path | conforms | carpet_beds, loop_benches, inner_lawn_beds | |
| Gate: tall brick piers on granite bases with granite caps | conforms | front vs front source, gate_piers_fence | |
| Gate: iron lanterns on the main piers | conforms | front, gate_arch | |
| Gate: iron sign arch, crest, two-line sign (abstract lettering) | conforms | gate_arch (crop arch_scrolls), front | Scrolls and the crest touch the arch, with no float. |
| Gate: double gates thrown open | conforms | front, front_corner, gate_piers_fence | |
| Ball-capped side piers with side gates at the loop legs | conforms | front (right side gate open), front_corner, gate_piers_fence | |
| Fence: pickets, rails, posts, granite curb | conforms | gate_piers_fence, side_entrance, mature_trees | |
| Fence continuity round the block | conforms | aerial, top, rear_side | Breaks only at the entrances. |
| Bandstand octagon, posts, fretwork brackets, balustrade, lattice skirt, front stair | conforms | bandstand, top, left_side | The stair faces south toward the gate. |
| Bandstand ogee pink-copper roof and finial | conforms (P2 #3 finish) | bandstand_roof, bandstand | |
| Bandstand ring bed | deviates (P1 #1) | bandstand, top | Present and correctly placed, but the plants are single gems. |
| Carpet beds: shape, white spine, colour bands, soil edge | shape, spine, bands and soil conform; plant form deviates (P1 #1) | carpet_beds, inner_lawn_beds, top | |
| Free-standing hydrangeas and shrubs (v001 #2) | conforms | rear_north, rear, left_side (crop left_shrubs), bandstand_roof, mature_trees, loop_benches | Lobe clusters on a sunk green base dome. None balances on a point. |
| Shade trees: count and placement | conforms | top vs top source, aerial | Clusters of 4 to 5 in the north corners and one very large tree plus 2 to 3 smaller in each south outer lawn. |
| Shade tree trunks at grade | conforms | mature_trees, left_side, rear_side | |
| Benches (front arm support, on the outer side of the north arcs facing the path) | conforms (P2 #5 setback) | loop_benches, rear_north (crop rn_benches), top | |
| Front-view bench orientation | deviates (P2 #2) | front | |
| Lamps at the circle and side entrances | conforms | top, rear_north, left_side, side_entrance | |
| Context streets on all four sides with brick mid-rises and a glass block | conforms | aerial, front, rear, right_side | |
| South context row beyond the south street | not visible | top, aerial | Frames end at the south street, so the builder's claim cannot be verified from pixels. |
| No coplanar paving or bed surfaces (no z-fighting) | conforms | bandstand, left_side, inner_lawn_beds | No flicker or striping at circle, path or bed junctions. |
| All vertices at or above grade; no floating parts | conforms | all detail views | Shrubs are grounded, benches and lamps sit on grade, and the gate ornaments touch the arch. |
| Framed locked views | conforms | front vs front, front_corner vs oblique, top vs top | Comparable vantage and composition. |

## 4. Camera validity

- front, front_corner, aerial, top, left_side, right_side, rear: valid. The target is legible and nothing is clipped.
- aerial (v001 #1): valid. No context roof stands between the camera and the block. The garden, all four streets and the east frontage read; the glass block on the right edge is cut by the frame but legible.
- rear_side: valid, with heavy near-canopy occlusion of the NW corner (P2 #6).
- Detail views (gate_arch, gate_piers_fence, bandstand, bandstand_roof, carpet_beds, inner_lawn_beds, loop_benches, mature_trees, side_entrance, rear_north): all valid and on target. gate_piers_fence no longer has a lamp in the middle of the frame. Frame edges crop the side_entrance and rear_north foreground piers, but the subject is not affected.
- facade_close, architecture_close, glass_close: not present (P2 #7). They do not apply to an open space and do not invalidate the camera set.

## 5. Previous-version (v001) findings: resolved in pixels?

1. **Aerial roof blocking the east side: RESOLVED.** No context mass occludes the block. The east sidewalk, east street and east frontage are visible.
2. **Free-standing hydrangeas and shrubs as single faceted icosahedra balanced on a vertex: RESOLVED for free-standing plants.** In rear_north, rear, left_side, bandstand_roof, mature_trees, loop_benches and side_entrance each one is now a cluster of lobes on a broad green base dome sunk into the lawn; none stands on a point. **The same gem primitive remains in all bed plantings**, raised here as P1 #1.
3. **Plan departure (north semicircle with a right-angle T, square-cornered north lawns, no fillets): RESOLVED.** The north arcs meet the axis in a Y, the north inner lawns are leaf islands with rounded tips pointing up the axis, every lawn corner at the circle, axis and cross-path junctions is filleted, and the granite edging follows the rounded outlines. This matches the top source.

Builder's cheap-P2 claims:
- Long paths plain without plank joints, circle courses kept: true. The forecourt apron still has plank joints (P2 #4).
- Hip rolls overlap with no dark notches: **false** (P2 #3).
- Every bench has a front arm support: true.
- Front-view bench back to camera, facing the garden: **false** (P2 #2).
- South context row and far sidewalk: not verifiable in any frame.
- No lamp in the middle of the gate_piers_fence frame: true.
- North-arc benches on the outer side facing the path: true.

v001 strengths still hold: the brick-pier gate with lanterns and the gilded sign arch with crest, the white octagonal bandstand with its pink-copper ogee roof and ring bed, the four carpet beds (layout and colour), the mature shade trees, the iron fence on its granite curb, and the side gates.
