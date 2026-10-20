# Independent RLASM v6.1 holistic review: clay-halifax-public-gardens v001

Reviewer: independent (not the builder). Evidence used: the locked sources `sources/front.png`, `sources/oblique.jpg` and `sources/top.jpg`; all 18 PNGs in `renders/`; the four phone boards. I opened every render at full resolution and made zoomed crops into a new scratch folder (`hpg-review-crops-175571736`). I did not use metadata, counts, hashes or builder notes as proof.

## 1. Verdict

**Verdict: VISUAL_REWORK_REQUIRED.** The garden's identity is present and reads correctly: sign gate, bandstand, loop and cross paths, carpet beds, fence and shade trees. Three P1 defects block approval:
- the aerial whole-envelope camera is obstructed;
- the free-standing shrubs read as boulders balanced on a point;
- the governing top-view plan grammar departs from the source (a T-junction loop and square-cornered fan lawns instead of rounded leaf lawns).

Counts: P0 = 0, P1 = 3, P2 = 11

There are no previous-version findings to carry forward because this is the first version (v001).

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | aerial | A featureless light-grey slab fills roughly the lower-right 40 to 45% of the frame. It is the roof of a nearby context building. Its edge runs right along the east fence and hides the east sidewalk, the east street, the east context frontage and part of the east side entrance. The garden is legible, but this whole-envelope view mostly shows a roof plane. | The aerial camera sits barely above, and just outside, a tall east-side context block, so that block's roof occludes everything beyond the fence. | Move or raise the aerial camera so that no context mass lies between it and the block (for example, pull it back over the SE street intersection, or raise it above the roof height plus a margin). Alternatively, lower or omit that one context block. Re-render and check that all four bounding streets are visible. |
| 2 | P1 | rear, rear_north, loop_benches, left_side, front_corner, mature_trees, gate_piers_fence, side_entrance, aerial | The free-standing hydrangea specimens and lawn shrubs are each one large faceted icosahedron, white or green, sitting on the lawn. Several balance on a single lower vertex: rear_north (985-1110, 605-690) shows a pointed underside with daylight and shadow beneath. They read as white and green boulders or gems, not shrubs, and the hero detail views show them as rocks. | A single low-subdivision icosphere is used per shrub with random rotation and no ground seating. Shrubs use no clustering the way the carpet beds do. | Build each specimen shrub as a cluster of 3 to 7 smaller lumps (as the beds already do), flattened to a dome and sunk 5 to 10% into grade so the contact is a flat ring. Lock its rotation so no vertex points down. Re-render rear_north, rear and loop_benches to confirm. |
| 3 | P1 | top, aerial, front_corner, rear_north, rear | Plan grammar departs from the governing top source. (a) The north half of the loop is a true semicircle centred on the bandstand that meets the north axis at a right-angle T. In the source the loop's arcs leave the axis in a tangential Y, giving the north lawns pointed tips. (b) As a result, the two north inner lawns are sharp-cornered quarter-annulus fans instead of the source's rounded leaf islands. (c) Every lawn corner at the circle, cross path and loop junctions is a hard angle. In the source these junctions have broad filleted paving, so all eight lawns read as soft-cornered islands. The beds inside are leaf-shaped, but the lawns framing them are not. | The loop is generated as a circle plus straight south legs. Lawn polygons are boolean leftovers of path bands without corner fillets. | Make the north loop an oval or a pair of curves that join the axis tangentially about 1 loop half-width north of the circle. Apply corner fillets of roughly 2 to 3 m to every lawn polygon at path junctions. Re-render top and front_corner and compare against `sources/top.jpg`. |
| 4 | P2 | carpet_beds, inner_lawn_beds, loop_benches, rear_north, rear, front | The path paving is scored as long transverse strips, so it reads as a timber boardwalk rather than the brick or herringbone paving in the source. The colour is right. | The joint generator uses plank-length module spacing. | Shorten the joint module to brick or paver proportions, or drop the joints and keep the flat colour. |
| 5 | P2 | bandstand_roof | The hip rolls on the ogee roof are built of straight segments with small dark notches or gaps at every joint. | A segmented hip-roll sweep has gaps between segments. | Use one continuous swept hip-roll per hip, or overlap the segments. |
| 6 | P2 | loop_benches, rear_north | The bench armrests are bars cantilevered forward from the back posts with no front arm-post or leg under the free end. One reads as a floating stick. | The arm geometry has no front support. | Add a front arm support down to the seat or leg. |
| 7 | P2 | front, gate_arch, front_corner | The arch scrollwork is a few isolated C-hooks made of segmented links. The source has continuous filigree scrolls flanking the crest. The crest is a plain roundel with a block. | Scrolls are low-resolution, isolated primitives. | Add 2 to 3 linked scroll pairs per side, joined to the arch band and to each other. Add a shield silhouette to the crest. |
| 8 | P2 | front | The foreground bench sits on the public sidewalk in front of the gate and faces the street. In the source the bench is inside on the paving with its back to the camera, facing the garden. | Entourage was placed outside the gate threshold. | Move it inside the gate onto the forecourt and rotate it 180 degrees. |
| 9 | P2 | rear, rear_north, side_entrance | There is no context south of the south street. A grey ground plane runs to an empty horizon behind the main gate, so the gate is framed against nothing. | No south-side context blocks were placed. | Add a simple south context row matching the other streets. |
| 10 | P2 | front, bandstand, gate_arch, mature_trees | A bright diagonal triangular light wedge appears on otherwise shaded brick context facades. | A sun or shadow terminator crosses from a neighbouring block, or a stray light. | Check the light set-up. Either soften or remove it, or accept it as cast shadow. |
| 11 | P2 | inner_lawn_beds, bandstand; gate_piers_fence (camera); boards | The paving has a faint lighter seam where the circle paving overlaps the cross-path paving. The gate leaf seen in gate_piers_fence stands off the west side pier, and its free end overlaps the main pier face, so the hinge is ambiguous. The foreground lamp in gate_piers_fence cuts through the gate centre. Board 01 pairs the locked top with the render aerial instead of the render top. | Stacked paving meshes; hinge offset; camera placement; board layout. | Merge or clip the circle and path paving. Hang the side leaf on its pier. Shift the camera half a metre off the lamp. Pair the locked top with the render top on board 01. |

## 3. Source conformance checklist

| Item | Status | View(s) used |
|---|---|---|
| Block ratio (about 43 x 57 m, long axis N-S) | conforms: measured about 1.32:1 | top |
| Straight N-S axis from the south gate to the north fence | conforms | top, rear_north |
| E-W cross path to both side fences | conforms | top, right_side |
| Round paved circle around the bandstand | conforms, though the ring is somewhat wider than in the source | top, bandstand |
| Oval loop: leaves the axis north of the bandstand | deviates: right-angle T, not a tangential Y (finding 3) | top |
| Oval loop: swell to the cross path near the side fences, straight south legs to the side openings | conforms: about 0.69 of the half-width against about 0.64 in the source | top, front_corner |
| Four leaf-shaped inner lawns | deviates: the north pair are hard-cornered fans; the south pair conform | top |
| Four outer lawns | conforms in topology; corners are unfilleted | top |
| Path paving colour | conforms: pink-grey brick colour | front, carpet_beds |
| Paving pattern | deviates (P2): reads as planks (finding 4) | carpet_beds |
| Granite edging on every path | conforms | carpet_beds, inner_lawn_beds, loop_benches |
| Gate: two tall brick main piers on granite bases with granite caps | conforms | front, gate_piers_fence |
| Gate: iron lanterns on the main piers | conforms | front, gate_arch |
| Gate: iron sign arch with crest roundel, main sign band and hanging FOUNDED plaque (abstract lettering) | conforms; scrollwork simplified (P2) | gate_arch, front |
| Gate: double gates open inward | conforms | front_corner, top, aerial |
| Gate: lower ball-capped side piers with side gates at the loop legs | conforms; hinge ambiguity in one view (P2) | front_corner, top, gate_piers_fence |
| Fence: black pickets with spear tips, rails, posts | conforms | gate_piers_fence, mature_trees, side_entrance |
| Fence: granite curb | conforms | gate_piers_fence, side_entrance |
| Fence: continuity round the block, with gaps only at the S, N and E/W entrances | conforms | top, aerial, rear_side |
| Bandstand: octagon, white posts | conforms | top, bandstand |
| Bandstand: fretwork arches | conforms (simplified) | bandstand |
| Bandstand: balustrade, lattice base | conforms | bandstand |
| Bandstand: front stair facing south | conforms | bandstand, top |
| Bandstand: pink-copper ogee or bell roof with ball-and-spike finial | conforms; hip-roll notches (P2) | bandstand_roof, front |
| Bandstand: ring bed with soil edge | conforms | bandstand, top |
| Carpet beds: lens or leaf shape | conforms | top, inner_lawn_beds |
| Carpet beds: white hydrangea spine | conforms | carpet_beds, inner_lawn_beds |
| Carpet beds: lavender, purple and pink bands, soil tray edge | conforms | carpet_beds |
| Shade trees: count and placement (clusters in NW, NE, SW and SE outer lawns) | conforms | top, front_corner |
| Shade trees: trunks at grade | conforms | mature_trees |
| Specimen shrubs | deviates: read as boulders on point contact (finding 2) | rear_north, loop_benches |
| Benches along the loop | conforms in placement; arm support missing (P2) | loop_benches, top |
| Lamps at the circle and entrances | conforms | front_corner, rear_north, side_entrance |
| Context: brick mid-rises and a glass office block on the streets | conforms on W, N and E; the south side is empty (P2) | front, aerial, rear |
| No coplanar paving or bed surfaces | conforms, with no z-fighting seen; faint overlap seam (P2) | inner_lawn_beds, bandstand |
| All vertices at or above grade | conforms for the hard landscape; shrub icosahedra rest on a vertex (finding 2) | rear_north |
| Framed locked views: front and front_corner | conforms | front, front_corner |
| Framed locked views: top | conforms | top |
| Framed locked views: aerial | deviates (finding 1) | aerial |

## 4. Camera validity

- **aerial: P1.** A near-camera context roof fills about 40 to 45% of the frame and hides the east sidewalk, the east street and the east context. The garden itself is unoccluded and legible, but this whole-envelope view is not validly framed.
- **gate_piers_fence: P2.** A foreground lamp post bisects the frame through the main gate opening. The piers, arch and fence are still legible.
- **front:** the whole arch, both main piers and one side pier are visible, and the bandstand is visible through the gate. This is valid and comparable to the locked front.
- **front_corner:** a close match to the locked oblique. Valid.
- **top:** true nadir, with the whole block and all four streets in frame. Valid.
- **The other views are valid:** left_side, right_side, rear, rear_side, rear_north, bandstand, bandstand_roof, carpet_beds, inner_lawn_beds, loop_benches, mature_trees, side_entrance and gate_arch. In each, the target is in frame, unclipped and legible.
- **Missing views:** the brief's list also names facade_close, architecture_close and glass_close. No renders with those names exist. The 18 renders present match the brief's stated count of 18 views, and the garden-specific details cover the identity elements. I do not count this as a defect, but the builder should confirm the view list.

## 5. Previous-version findings

There are no previous-version findings because this is the first version (v001).
