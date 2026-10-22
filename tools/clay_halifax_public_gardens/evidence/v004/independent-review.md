# Independent holistic review: Halifax Public Gardens clay, v004 (RLASM v6.1)

Reviewer: independent; I did not build this candidate. I judged only rendered pixels against the three locked sources (sources/front.png, sources/oblique.jpg, sources/top.jpg). I opened all 18 renders in renders/ at full resolution, the three sources and the four phone boards with the image reader. For regression checks I also opened the v003 evidence renders (carpet_beds, top, bandstand) and diffed every v004 render against its v003 counterpart. Zoomed crops are only in the new folder `review/crops_kmvuwy/`. Builder notes, metadata, counts and the clearance audit were not accepted as proof.

## 1. Verdict

Verdict: FAIL

Counts: P0=0 P1=2 P2=7

(In the brief's terms this is VISUAL_REWORK_REQUIRED.) The P1 shared by v002 and v003 is **fixed**: the bed plants no longer read as gems, pebbles or gumdrops. The kit hydrangeas are lobed white mopheads in real leaf foliage, the lavender and salvia are spikes on strap-leaf clumps, and the ageratum shows as small floret cushions. However, the new planting adds two blocking defects. First, the "clipped carpet-bedding rim" renders as a smooth, rounded, satin-pink (or lilac) bolster round every bed. At eye level it reads as a tube or an inflatable kerb, and from the air as a crisp magenta outline that no source shows. Second, the planting is now so sparse that the bandstand ring bed reads as an almost empty pink trough, and the mauve masses either side of the white spine, which conformed in v003, can no longer be read from the top, aerial or front_corner views.

## 2. Findings table

| # | severity | view(s) | finding (what the pixels show) | evidence | likely cause | suggested finite fix |
|---|---|---|---|---|---|---|
| 1 | P1 | carpet_beds, inner_lawn_beds, loop_benches, bandstand, bandstand_roof, rear_north, rear; also top, aerial, front_corner, left_side, right_side, rear_side | **The bed rim reads as a tube or kerb, not as clipped planting.** Every leaf bed, the bandstand ring and both north strip borders are framed by one continuous extruded band about 0.34 m wide. It has a rounded convex top, a smooth satin gradient and a hard vertical outer face standing on a brown soil plinth. The only surface detail is a few sparse dark dots. At eye level it reads as a pink foam bolster or an inflatable kerb (in inner_lawn_beds the whole bed looks like a pink inflatable dinghy, with a faceted mitred point at the tip). The north strip borders read as lilac-painted trays. From the air (top, aerial, front_corner) it draws a saturated magenta line round all four leaf beds and a double magenta ring round the bandstand. In the sources, the beds end in a dark soil margin against the lawn and have no coloured outline (top, oblique, front). This is the "tube" reading the brief asked about. | carpet_beds x 380-1060, y 470-1080 (crops cb_near.png, cb_rim_4x.png: an unbroken smooth pink surface with about 5 flecks across 180 x 200 px); inner_lawn_beds x 690-980, y 470-810, tip x 730-860, y 760-810 (ilb_bed.png); bandstand x 230-1200, y 800-920 (bs_ring_left.png, bs_ring_right.png); rear_north x 400-1030, y 790-1080 (rn_strip.png); top x 540-900, y 340-880 (top_beds.png); front_corner x 520-950, y 380-840 (fc_beds.png). Compare with src_top_beds.png and src_obl_beds.png (dark soil edges, no rim colour). | The rim is a single swept or extruded closed-profile mesh with a flat material and a near-zero fleck density. It is not built from kit plant instances. Its height and rounded cross-section give it a kerb silhouette. | Rebuild the rim as planting. Either (a) instance a dense low rosette or clipped-foliage prototype (40 or more per m², height 0.10-0.15 m, ±15% scale and ±10% hue/value jitter, 30-50% bronze-leaf mix) so the top surface is broken and the edge is irregular, or (b) remove the coloured rim, return to the source's dark soil margin with a low green groundcover edge, and plant the pink or magenta begonia as a band of small mounded plants inside it. In either case drop the rim top to 0.10-0.15 m above the soil, remove the satin bevel and the mitred tip facet, and desaturate it so that from the air it reads as a soft border, not an outline. Re-render carpet_beds, inner_lawn_beds, bandstand, rear_north, top and front_corner. |
| 2 | P1 | bandstand, bandstand_roof, front_corner, top, aerial, rear, left_side, right_side; side bands in carpet_beds and inner_lawn_beds | **Bed fill is too sparse, the ring bed is nearly empty and the mauve bands are lost.** The bandstand ring bed shows a broad, bare, pale-pink centre band (it reads as sand or concrete) with only about 3-4 isolated plants per visible half-ring, spaced roughly 1.5-3 m apart: one hydrangea clump, two or three lavender or salvia tufts. In the top and front_corner views it reads as a pink double circle with about a dozen white dots. In the sources the ring is a continuous planted mass: dense green shrubs with white and purple flowers round the base (oblique, top), and hydrangea and pink/lilac masses either side of the stair (front). In the four leaf beds, the white spine is good, but the side bands are mostly flat dark-green groundcover with single spaced lavender clumps and ageratum cushions. From top, aerial and front_corner the beds read as a green body with one row of white dots inside a pink outline, and no mauve or purple band is legible. In v003, at the same cameras, the white / lavender / pink banding was legible and was marked as conforming, so the colour-band item has **regressed**. The source oblique shows massed lavender and purple drifts and burgundy foliage on both sides of the white hydrangeas. | bandstand x 230-450, y 800-890 and x 840-1200, y 800-905 (bs_ring_left.png, bs_ring_right.png, cb_far_ring.png); bandstand_roof x 180-330 and x 1100-1280, y 900-1080; top ring x 640-800, y 450-600 (top_beds.png); front_corner (fc_beds.png). Hue count, same SW-bed crop at the same camera (top x 575-700, y 580-870): lavender-hue pixels 4.9% in v003 against 0.0% in v004. NW bed (x 540-690, y 340-480): 4.5% against 0.0%. Source: src_obl_beds.png. | The kit placement uses one single-plant spacing for the side bands and the ring, with no drift or mass grouping. The ring's "pink centre band" is a near-white flat surface rather than planted begonia. The lavender and salvia prototypes are thin spikes that disappear in plan. | Plant the ring bed densely: hydrangea mounds and lavender/salvia at 0.5-0.6 m centres, so the soil or centre band is no more than about 15% visible in the bandstand view. Replace the flat centre band with instanced low pink plants. In each leaf bed, group the lavender, salvia and ageratum into drifts of 3-7 plants either side of the spine, and add a mounded mauve or purple mass (for example, a purple-mophead or salvia drift prototype with broad heads that read in plan) so a purple band is legible in top and front_corner. Confirm by a hue check on the top render: about 3% or more lavender-hue pixels in each leaf-bed crop. |
| 3 | P2 | bandstand (x 380-440, y 890-905 and x 815-870, y 895-912) | Where the ring bed is cut at the stair, its brown soil plinth projects past the rim as a flat brown slab that reads as a timber board. (The same slab is present in v003, so this is not a regression.) | bs_ring_right.png, cb_far_ring.png | The bed plinth end is not trimmed back to the rim. | Trim the plinth flush with the rim end, or cap it with the granite edging. |
| 4 | P2 | mature_trees, side_entrance, left_side, right_side, rear_side, front | v003 P2 #2 not addressed: the shade-tree crowns are coarse low-poly clusters with large flat facets. They now contrast more sharply with the finer kit planting. Trunks are at grade. | mature_trees x 210-1270, y 0-590 | Low-subdivision crown lobes. | Subdivide and smooth-shade the crown lobes, and add 2-3 lobes per crown. |
| 5 | P2 | rear_north (x 290-480, y 640-780; x 975-1115, y 595-705), rear, left_side, bandstand_roof | v003 P2 #3 not addressed: the free-standing hydrangeas are faceted white lobes on an octagonal green plinth. Next to the new kit hydrangeas in the strip beds they now read as a different, cruder species. | rear_north | v003 shrub primitive kept. | Replace them with the kit hydrangea prototype scaled up as a shrub mass (or 3-5 kit instances), so all hydrangeas share one grammar. |
| 6 | P2 | gate_arch, front, gate_piers_fence | v003 P2 #4 not addressed: the C-scrolls and crossed scrolls on the sign arch are chains of short box segments with visible joints. They do touch the arch. | arch_scrolls.png (gate_arch x 540-960, y 280-420) | Discrete box segments. | Sweep each scroll as one tube. |
| 7 | P2 | front | v003 P2 #5 not addressed: the foreground bench (backrest correctly towards the camera) stands on the grey public sidewalk instead of the brick paving inside the gate. | front x 670-1100, y 760-960 (front_bench.png) | Bench placed at the sidewalk coordinate. | Move it about 2-3 m north onto the brick forecourt. |
| 8 | P2 | rear | v003 P2 #6 not addressed: between the two south context blocks a flat grey world-edge band shows where the ground plane ends. | rear x 660-780, y 265-300 (rear_horizon.png) | Ground plane ends just past the south row. | Extend the ground plane or the context row. |
| 9 | P2 | front, gate_piers_fence, aerial | v002 P2 #4 is still present (it was not carried in the v003 review): the forecourt apron between the sidewalk and the gate has long transverse plank-like joints that read as decking rather than brick. | front y 700-800; gate_piers_fence x 420-1000, y 600-900 | Old joint pattern on the apron. | Make it plain brick, or brick-scale joints. |

**Black patches, slots and wedges.** I found no geometry-caused black patches, slots or wedges in any render. The near-black pixels in the beds are dark green, not neutral black. They sit only in the interstices between kit leaves. They follow the leaf outlines and fade gradually, and in cb_hyd_4x.png they read as leaf self-shadow. A neutral-black scan of the inner_lawn_beds bed (x 680-990, y 440-810) finds only 179 neutral-dark pixels, all inside the hydrangea leaf mass. The dark diamonds in the bandstand lattice skirt are the intended voids behind the white lattice; they are unchanged since v002 and backed by the skirt interior. The other near-black areas are the iron fence, gates, benches and lamp posts, all of which are black by material.

## 3. Source conformance checklist

| item | status | view(s) used | note |
|---|---|---|---|
| Block ratio (about 43 x 57 m, long axis N-S) | conforms | top vs top source | About 650 x 900 px fence block. Unchanged from v003. |
| Straight axis from the south gate to the north fence | conforms | top, rear, rear_north | |
| E-W cross path to both side fences | conforms | top, left_side, right_side | |
| Paved circle with concentric and radial courses | conforms | top, bandstand, bandstand_roof | |
| Oval loop: Y off the axis north of the bandstand, swell to the cross path, straight legs to the side piers | conforms | top vs top source, front_corner vs oblique, aerial | |
| Four leaf-shaped inner lawns with filleted, edged corners | conforms | top, rear_north, inner_lawn_beds | |
| Four outer lawns | conforms | top, aerial | |
| Path paving colour (brick) | conforms | top, front_corner vs oblique | |
| Forecourt apron paving | deviates (P2 #9) | front, gate_piers_fence | Plank joints. |
| Granite edging on every path | conforms | carpet_beds, inner_lawn_beds, loop_benches | |
| Gate: tall brick piers on granite bases | conforms | front vs front source, gate_piers_fence | |
| Gate: iron lanterns | conforms | front, gate_arch | |
| Gate: iron sign arch with crest and two-line sign (abstract lettering) | conforms (P2 #6 on the scroll finish) | gate_arch, front | |
| Gate: open double gates | conforms | front, front_corner, gate_piers_fence | |
| Gate: ball-capped side piers and side gates | conforms | front, front_corner, side_entrance | |
| Fence: pickets, rails, posts, granite curb | conforms | gate_piers_fence, side_entrance, mature_trees | |
| Fence continuity round the block | conforms | aerial, rear_side, top | Breaks only at the entrances. |
| Bandstand: octagon, posts | conforms | bandstand, top | |
| Bandstand: fretwork arches, balustrade, lattice skirt, front stair | conforms | bandstand | Unchanged from v003. |
| Bandstand: ogee pink-copper roof, continuous hip rolls, finial | conforms | bandstand_roof, bandstand | The hip rolls are still continuous with no notches. |
| Bandstand ring bed | deviates (P1 #1 rim, P1 #2 sparse) | bandstand, bandstand_roof, top, front_corner | Placement and coloured ring are present, but it reads as a near-empty pink trough. |
| Carpet beds: leaf/crescent shape | conforms | top, inner_lawn_beds | Plants stay inside the bed outline in plan. |
| Carpet beds: hydrangea spine | conforms | carpet_beds, top, front_corner | White mophead spine, legible at every scale. |
| Carpet beds: colour bands (lavender, purple, pink either side) | deviates (P1 #2; regression from v003) | top, aerial, front_corner, carpet_beds | Pink survives only as the outline rim. Mauve is not legible from the air, and at eye level it is limited to sparse spikes and cushions. |
| Carpet beds: soil edge | deviates (P1 #1) | carpet_beds, inner_lawn_beds, top | Replaced by a smooth coloured bolster. The source shows a dark soil margin. |
| Carpet beds: plant form (v002/v003 P1) | conforms (fixed) | carpet_beds (cb_near.png, cb_hyd_4x.png), inner_lawn_beds, bandstand, loop_benches, gate_piers_fence, front | No polygonal outlines, apex points or hexagonal tiles. They read as hydrangea, lavender, salvia and ageratum. |
| North-axis strip borders | plant form conforms; rim deviates (P1 #1) | rear_north, rear | |
| Free-standing hydrangeas and shrubs | conforms with P2 #5 | rear_north, rear, left_side | Grounded, with an octagonal plinth. |
| Shade trees: count and placement | conforms | top vs top source, aerial | |
| Shade trees: trunks at grade | conforms (crown finish P2 #4) | mature_trees, rear_side | |
| Benches along the loop, with arm supports, facing the path | conforms | loop_benches, rear_north, top | |
| Front bench | orientation conforms; position deviates (P2 #7) | front | |
| Lamps at the circle and side entrances | conforms | bandstand, side_entrance, front_corner | |
| Context streets on four sides, brick mid-rises, glass block | conforms (P2 #8 world edge) | aerial, rear, front, left_side | |
| No coplanar paving or bed surfaces (no z-fighting) | conforms | carpet_beds, inner_lawn_beds, bandstand, top | No striping at the rim, groundcover or paving junctions. |
| All vertices at or above grade, no floating parts | conforms | all detail views | Kit plants are seated in the bed soil, and no plant floats above the rim or bed. |
| Framed locked views | conforms | boards/phone-01; front vs front, front_corner vs oblique, aerial/top vs top | |

## 4. Camera validity

- All 18 renders are valid. In none is the target occluded, clipped or illegible, and all are lit with neutral, broad light.
- front, front_corner, aerial and top frame the whole asset with margin and match their source roles.
- left_side, right_side, rear and rear_side are valid. In rear_side the near NW canopies cover about a third of the frame, but the bandstand, beds, paths and gate stay legible.
- carpet_beds, inner_lawn_beds, bandstand and loop_benches put the new bed planting at eye level and are the right proof views for this change. bandstand_roof and rear_north also show the ring bed and the strip borders.
- gate_arch, gate_piers_fence, mature_trees and side_entrance are valid and on target.
- The brief's view list also names facade_close, architecture_close and glass_close. No such renders exist, and 18 files are present, which matches the stated count. These are building-template roles with no counterpart for this open space. No finding is raised.

## 5. Previous findings

| previous finding | status in v004 pixels |
|---|---|
| v002 P1 #1 / v001 P1 #2 (beds): every bed plant a single faceted icosahedron, reading as gems | **Fixed.** No faceted gem heads remain in any bed (carpet_beds, inner_lawn_beds, bandstand, rear_north). |
| v003 P1 #1: small heads with hard 6-8-sided outlines, pointed crowns, flat green hexagonal tiles; honeycomb of pebbles up close | **Fixed.** The hydrangeas are rounded lobed mopheads set in serrated leaf foliage, with no polygonal silhouette at 4x zoom (cb_hyd_4x.png). Lavender and salvia are spikes, ageratum shows as floret cushions, and there are no flat green tiles. At eye level (gate_piers_fence, front, mature_trees edge) the bed edges read as a low flowering border, not sawtooth crystals. The bed finding as originally worded is closed. New P1s #1 and #2 are defects introduced by the replacement planting. |
| v003 colour-band conformance (white / lavender / pink banding legible from the air) | **Regressed** (P1 #2). |
| v003 P2 #2 tree crowns faceted | Not fixed (P2 #4). The brief stated this was not addressed. |
| v003 P2 #3 free-standing hydrangea octagonal base | Not fixed (P2 #5). The brief stated this was not addressed. |
| v003 P2 #4 arch scrolls as box segments | Not fixed (P2 #6). |
| v003 P2 #5 front bench on the sidewalk | Not fixed (P2 #7). |
| v003 P2 #6 rear world-edge gap | Not fixed (P2 #8). |
| v002 P2 #4 forecourt plank joints | Not fixed (P2 #9). It was missing from the v003 carry-forward. |
| v002 P2: front bench back to the camera | Holds (front_bench.png: the back posts occlude the back slats, and the arm supports are on the far side). |
| v002 P2: continuous hip rolls with no notches | Holds (bandstand_roof). |
| v001 P1 #1: aerial unblocked by context roofs | Holds (aerial). |
| v001 P1 #3: loop Y join, rounded north leaf islands, filleted edged corners | Holds (top, rear_north). |
| v001/v002 strengths: brick-pier gate with lanterns and sign arch, white octagonal bandstand with pink-copper ogee roof, fence on granite curb, side gates, mature trees, context streets | All still present and unchanged. Apart from the beds, the v004-against-v003 render diffs show only scattered edge noise, with no change to the gate, bandstand, fence, trees or context. |
