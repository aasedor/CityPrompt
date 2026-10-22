# Independent holistic review: Halifax Public Gardens clay, v005 (RLASM v6.1)

Reviewer: independent; I did not build this candidate. I judged only rendered pixels against the three locked sources (sources/front.png, sources/oblique.jpg, sources/top.jpg). I opened all 18 renders in renders/ at full resolution (1440 x 1080), the three sources and the four phone boards with the image reader. For regression checks I also opened the v004 evidence renders (bandstand, top, mature_trees) and diffed every v005 render against its v004 counterpart on a 120 px grid. Zoomed crops are only in the new folder `review/crops_itdfsm/`. Builder notes, hue figures, metadata and audits were not accepted as proof; the hue figures quoted below are my own measurements.

## 1. Verdict

Verdict: PASS_ZERO_P0_P1

Counts: P0=0 P1=0 P2=11

Both v004 P1s are closed in the pixels. The coloured tube rim is gone from every bed, so there is no pink bolster at eye level and no magenta outline from the air. The beds are now massed white-spine-and-mauve plantings whose bands read in top, aerial and front_corner. The remaining defects are polish: bed fill thins to flat groundcover toward the edges and tips, the new margin reads as a raised brown board, the north strips are still sparse, there are hairline dark ticks at the new ring caps, and six P2s carried over unchanged.

## 2. Findings table

| # | severity | view(s) | finding (what the pixels show) | evidence | likely cause | suggested finite fix |
|---|---|---|---|---|---|---|
| 1 | P2 | inner_lawn_beds, carpet_beds (far band), bandstand, front_corner | **Fill thins to bare groundcover toward the edges and tips.** The spine and the mauve drifts are full, but the outer band of each leaf bed is a flat, untextured dark-green groundcover with only scattered ageratum cushions and single salvia clumps. In inner_lawn_beds the last quarter of the bed toward the tip holds only four small cushions, so the plants do not "run out to the margin" as the brief claims. By eye, about a fifth to a third of the visible bed surface is flat groundcover. A conservative pixel estimate gives 20% in inner_lawn_beds and 15% in carpet_beds. The ring bed is a single row of plants along its centre line, with a strip of groundcover in front of it, and its plants are lower and smaller than the source's shrub masses at the bandstand base (front, oblique). This is no longer the near-empty trough of v004. | crops ilb_bed.png (native x 690-980, y 450-800), cb_margin.png, bs_ring_left.png, bs_ring_right.png, fc_beds.png; source oblique beds | The edge shrink/fallback leaves gaps of 0.5 m or more between the outermost plants and the margin, and the tips get no spine plants. | Add one more ring of ageratum and salvia cushions about 0.25-0.3 m inside the margin, extend the spine to within about 0.6 m of each tip, and scale the ring-bed hydrangeas up about 20-30%. |
| 2 | P2 | inner_lawn_beds, carpet_beds, loop_benches, rear_north | **The new dark margin reads as a raised brown edging board, not a soil margin, and the bed tip is blunt with a step.** The margin is about 0.3 m wide, flat-topped, with a crisp vertical outer face, in mid-dark brown (sampled about RGB 70/63/54 in the inner_lawn_beds light). At eye level it reads as a timber planter frame. At the leaf tip the margin is truncated square and its inner edge has a small rectangular jog where the groundcover ends. From the air it is a thin dark line, which matches the source top. | ilb_tip_8x.png (native x 730-880, y 740-815); cb_margin.png | The margin is an extruded offset band with a vertical face, and the groundcover offset is clipped at the tip. | Lower the margin to about 0.03-0.05 m above the lawn, or bevel its outer face into the lawn. Darken it toward the stated near-black, and taper the tip to a point with a matching groundcover offset. |
| 3 | P2 | rear_north, rear, top | The two north-axis strip borders are still single-file rows of 4-5 plants about 1.5 m apart on flat groundcover. The source top shows these strips densely planted. | rn_strip.png (native x 380-1060, y 770-1080) | The strip bed uses one-plant-wide spacing without the leaf-bed drift logic. | Apply the leaf-bed fill (spine plus edge cushions) to the strips. |
| 4 | P2 | bandstand | Where each new granite cap meets the ring curb, there are hairline neutral-black ticks about 5 x 1-2 px (pixel value 1/1/1). They are geometry seams, not shadow, because they are pure neutral black with hard edges and sit exactly at the cap-curb joints. They are too small to read as a slot at review scale. | bs_rcap_6x.png (native about x 806-812, y 893 and x 850-862, y 920); bs_lcap_6x.png shows the left cap clean | The cap box ends short of, or is coplanar with, the curb end faces, exposing a gap or backface. | Extend each cap 0.02 m into the curb, or merge the cap and curb ends. |
| 5 | P2 | carpet_beds, inner_lawn_beds | Up close, the mauve mophead heads are made of smooth uniform spheres and are about 1.5-2 times the size of the white heads, so they read slightly as balloon clusters. The planting kit's dark leaf shade between leaves is unchanged, as the brief states. | cb_near.png | Prototype head scale and smooth floret spheres. | Scale the mauve heads to about 0.8 times their current size, and add ±15% jitter to floret size. |
| 6 | P2 | mature_trees, side_entrance, left_side, right_side, rear_side, front | Carried over (v004 #4): the shade-tree crowns are coarse low-poly lobes with large flat facets. Trunks are at grade. | mature_trees x 210-1270, y 0-590 | Low-subdivision crown lobes. | Subdivide and smooth-shade the lobes. |
| 7 | P2 | rear_north, rear, left_side, front_corner | Carried over (v004 #5): the free-standing hydrangea and shrub masses are faceted white, or pink-white, lobes on an octagonal plinth, a different grammar from the kit hydrangeas in the beds. | rear_north x 290-480, y 630-780 and x 975-1110, y 595-705 | Old shrub primitive kept. | Replace them with clustered kit hydrangea instances. |
| 8 | P2 | gate_arch, front, gate_piers_fence | Carried over (v004 #6): the arch C-scrolls are chains of short box segments with visible joints. | gate_arch x 540-960, y 280-420 | Discrete box segments. | Sweep each scroll as one tube. |
| 9 | P2 | front | Carried over (v004 #7): the foreground bench stands on the grey public sidewalk, not on the brick forecourt. | front x 670-1100, y 760-960 | Placement coordinate. | Move it 2-3 m north. |
| 10 | P2 | rear | Carried over (v004 #8): a grey world-edge band shows between the two south context blocks. | rear x 660-780, y 265-300 | The ground plane ends just past the south row. | Extend the ground plane. |
| 11 | P2 | front, gate_piers_fence, aerial | Carried over (v004 #9): the forecourt apron has long transverse plank-like joints that read as decking. | front y 700-800; gate_piers_fence x 420-1000, y 600-900 | Joint pattern. | Use brick-scale joints. |

**Black patches, slots and wedges.** I found no geometry-caused black patch, slot or wedge at review scale. Apart from the hairline cap ticks in P2 #4, I sorted the dark pixels as follows:

- **Beds.** A neutral-black scan (max channel < 30, chroma < 10) over the carpet_beds bed finds small irregular flecks only in the interstices of the kit leaves and under the flower heads. In cb_leafshade_4x.png they follow the leaf outlines and fade gradually into green, so they are leaf self-shadow, not holes. None appear on the groundcover, the margin or the paving. The top view has only 17 such pixels across all the beds.
- **Lattice skirt.** The dark diamonds are the intended voids behind the white lattice, backed by the skirt interior and unchanged since v002.
- **Stair corner.** The dark vertical strip between the right stair stringer and the skirt (bandstand x 800-807, y 865-890) is mid-dark grey (mean about 45), and in v004 it was 50. It is the shadowed inner corner, not a gap.
- **Black by material.** The iron fence, gates, lamps and bench frames are black by material.

## 3. Source conformance checklist

| item | status | view(s) used | note |
|---|---|---|---|
| Block ratio (about 43 x 57 m, long axis N-S) | conforms | top vs top source | Unchanged. |
| Straight axis from the south gate to the north fence | conforms | top, rear, rear_north | |
| E-W cross path to both side fences | conforms | top, left_side, right_side | |
| Paved circle with concentric and radial courses | conforms | top, bandstand, bandstand_roof | |
| Oval loop: Y off the axis north of the bandstand, swell to the cross path, straight legs to the side piers | conforms | top vs top source, front_corner vs oblique, aerial | |
| Four leaf-shaped inner lawns | conforms | top, rear_north, inner_lawn_beds | |
| Four outer lawns | conforms | top, aerial | |
| Path paving colour (brick) | conforms | top, front_corner vs oblique | |
| Forecourt apron paving | deviates (P2 #11) | front, gate_piers_fence | Plank joints. |
| Granite edging on every path | conforms | carpet_beds, inner_lawn_beds, loop_benches | |
| Gate: tall brick piers on granite bases | conforms | front vs front source, gate_piers_fence | |
| Gate: iron lanterns | conforms | front, gate_arch | |
| Gate: iron sign arch with crest and two-line sign (abstract lettering) | conforms (P2 #8 scroll finish) | gate_arch, front | |
| Gate: open double gates | conforms | front, front_corner, gate_piers_fence | |
| Gate: ball-capped side piers and side gates | conforms | front, front_corner, side_entrance | |
| Fence: pickets, rails, posts, granite curb | conforms | gate_piers_fence, side_entrance, mature_trees | |
| Fence continuity round the block | conforms | aerial, rear_side, top | Breaks only at the entrances. |
| Bandstand: octagon, posts | conforms | bandstand, top | |
| Bandstand: fretwork arches, balustrade, lattice skirt, front stair | conforms | bandstand | Unchanged. |
| Bandstand: ogee pink-copper roof, continuous hip rolls, finial | conforms | bandstand_roof, bandstand | Hip rolls continuous, no notches. |
| Bandstand ring bed | conforms (P2 #1 low/thin, P2 #4 cap ticks) | bandstand, rear_north, top, front_corner | A continuous white and mauve row along the centre line over groundcover. No pink band and no rim. The ring ends at the stair are capped in granite, and the brown slab is gone. |
| Carpet beds: leaf/crescent shape | conforms | top, inner_lawn_beds | Plants stay inside the outline in plan. |
| Carpet beds: hydrangea spine | conforms | carpet_beds, top, front_corner | |
| Carpet beds: colour bands (lavender/purple/pink either side) | conforms | top, aerial, front_corner, carpet_beds | Mauve drifts flank the white spine in every bed. Lavender-hue share in my top-view crops: SW 2.9%, NW 3.6%, NE 3.5%, SE 3.2%. The same crops give v004 0.0% and v003 4.2-6.0%. No pink band remains; the source's pink is minor. |
| Carpet beds: soil edge | conforms (P2 #2) | top, carpet_beds, inner_lawn_beds | It reads as a dark bed edge in plan, as in the source, but as a raised board at eye level. |
| Carpet beds: plant form (v002 P1) | conforms | carpet_beds (cb_near.png), inner_lawn_beds, bandstand | Mophead hydrangeas, salvia spikes and ageratum cushions. No gems or polygonal heads (P2 #5 on the mauve head finish). |
| Carpet beds: no coloured outline / tube (v004 P1 #1) | conforms | top, aerial, front_corner, bandstand, carpet_beds, inner_lawn_beds, rear_north | Magenta-hue share is 0.0% in the top bed crop (v004 3.3%) and in the bandstand ring crop (v004 7.5%). |
| North-axis strip borders | deviates (P2 #3) | rear_north, rear | Sparse. |
| Free-standing hydrangeas and shrubs | conforms with P2 #7 | rear_north, rear, left_side | Grounded. |
| Shade trees: count and placement | conforms | top vs top source, aerial | |
| Shade trees: trunks at grade | conforms (P2 #6 crowns) | mature_trees, rear_side | |
| Benches along the loop | conforms | loop_benches, rear_north, top | |
| Front bench | orientation conforms; position deviates (P2 #9) | front | |
| Lamps at the circle and side entrances | conforms | bandstand, side_entrance, front_corner | |
| Context streets on four sides, brick mid-rises, glass block | conforms (P2 #10) | aerial, rear, front, left_side | |
| No coplanar paving or bed surfaces (no z-fighting) | conforms | carpet_beds, inner_lawn_beds, bandstand, top | No striping at the margin, groundcover, cap or paving junctions. |
| All vertices at or above grade, no floating parts | conforms | all detail views | Plants are seated in the groundcover, and the caps sit on the curb. |
| Framed locked views | conforms | boards/phone-01; front vs front, front_corner vs oblique, aerial/top vs top | |

## 4. Camera validity

- All 18 renders are valid. In none is the target occluded, clipped or illegible.
- front, front_corner, aerial and top frame the whole asset with margin and match their source roles.
- left_side, right_side, rear and rear_side are valid. Near canopies in rear_side and left_side cover part of the frame, but the bandstand, beds, paths and gate stay legible.
- carpet_beds, inner_lawn_beds, bandstand, rear_north and bandstand_roof put the reworked planting at eye level or near it. They are the right proof views for this change.
- gate_arch, gate_piers_fence, mature_trees, loop_benches and side_entrance are valid and on target.
- The brief's list also names facade_close, architecture_close and glass_close. No such files exist, and the 18 present renders match the stated count. These are building-template roles with no counterpart in this open space, so no finding is raised.

## 5. Previous findings

| previous finding | status in v005 pixels |
|---|---|
| v004 P1 #1: rim read as a rounded pink/lilac tube, with a magenta outline from the air | **Fixed.** No coloured rim remains on any leaf bed, the ring or the north strips (top, aerial, front_corner, bandstand, carpet_beds, inner_lawn_beds, rear_north). Magenta-hue share fell to 0.0% from 3.3% (top) and 7.5% (bandstand ring). The replacement margin is a P2 (#2), not a tube. |
| v004 P1 #2: fill too sparse, ring nearly empty, mauve bands lost beside the white spine | **Fixed.** Broad mauve heads in drifts flank the white spine in all four beds and read from top, aerial and front_corner. Lavender-hue share is 2.9-3.6% against v004's 0.0%. The ring is a continuous planted row with no pale centre band. Residual edge thinning is P2 #1. |
| v004 P2 #3: brown soil slab at the ring ends beside the stair | **Fixed.** Both ends are capped by a granite beam, with the groundcover running to it. The right cap leaves hairline joint ticks (P2 #4). |
| v002 P1 (and v003 P1): bed plants as faceted gems or polygonal heads | **Fixed, and no regression.** No faceted or polygonal heads in any bed; the mophead and spike forms hold. |
| v003 colour-band conformance (regressed in v004) | **Restored.** It conforms again, though the lavender share is slightly below v003's. |
| v004 P2 #4 tree crowns faceted | Not fixed (P2 #6). The crown lobes differ slightly from v004 in mature_trees but are of the same faceted quality; this is not a regression. |
| v004 P2 #5 free-standing faceted shrubs | Not fixed (P2 #7). |
| v004 P2 #6 arch scrolls as box segments | Not fixed (P2 #8). |
| v004 P2 #7 front bench on the sidewalk | Not fixed (P2 #9). |
| v004 P2 #8 rear world-edge band | Not fixed (P2 #10). |
| v004 P2 #9 forecourt plank joints | Not fixed (P2 #11). |
| v002 P2: front bench back to the camera; continuous hip rolls | Hold (front, bandstand_roof). |
| v001 P1s: aerial unblocked, loop Y join, rounded north islands, filleted edged corners | Hold (aerial, top, rear_north). |
| Strengths: gate, bandstand, fence on granite curb, side gates, trees, context | Unchanged. The diffs against v004 are confined to the beds, plus anti-aliasing and crown-lobe noise. The gate, bandstand, fence and context show no change. |
