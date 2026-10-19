# Independent holistic review: clay-halifax-waterfront-warehouse v004 (RLASM v6.1)

Reviewer: independent; did not build the candidate. Judged only rendered pixels against the locked source pixels (sources/front.png, sources/oblique.jpg, sources/top.jpg). All 18 renders, the three sources and the four phone boards were opened at full resolution. Zoomed crops for checking were written only to the new folder `/tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/review-crops-v004-98f5df19/`.

## 1. Verdict

**VISUAL_REWORK_REQUIRED**: all three v003 P1s are resolved in the pixels, but the east (side-street) elevation's window rhythm does not match two independent locked sources. The middle east bay is a triplet over a triplet in the sources and a pair over a triplet in the render.

Counts: P0 = 0, P1 = 1, P2 = 6

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | right_side, east_side, front, front_corner, aerial, rear_side (vs sources front + oblique) | **East elevation fenestration rhythm is wrong.** Render upper storey, south to north: pair / pair / pair. Render ground: two shop-glazed openings / triplet of arched windows / triplet of arched windows. So the upper and ground counts disagree in two of the three bays. Both sources show matching upper and ground counts in each bay. **Source front:** bay 2 (pier at x≈785–807 to pier at x≈905–917) has three upper arched windows at x≈815, 855, 887 over three ground arched windows at x≈820, 855, 890. **Source oblique:** bay 1 has a pair at x≈755 and 810. Bay 2, between piers at x≈850 and 963, has a triplet at x≈877, 912 and 945. Bay 3, between piers at x≈963 and 1023, has a pair at x≈983 and 1010, over two arched ground openings. Source east = pair / triplet / pair over shop glazing / triplet / pair. The render's middle east bay has lost one upper arch and its northern bay has gained one ground arch, so the bays no longer line up vertically. | The east-side bay program was taken from the text spec ("pairs on the east side") instead of the source pixels. The ground triplet looks copied from bay 2 into bay 3. | Make east bay 2's upper storey a triplet of round-arched windows with granite archivolts, keystones, imposts and sills, centred over the existing ground triplet. Make east bay 3's ground storey a pair of brick-arched windows centred under the existing upper pair. Keep pier positions. Re-render right_side, east_side, front, front_corner and rear_side. |
| 2 | P2 | left_side (≈x 266–288, y 367–373); rear (≈x 140–210, y 300–312) | The north-east cornice return over the north wall has a small near-black wedge (RGB ≈ 27–46, about 15×4 px) between the corona soffit and the top of the frieze/bed block where it meets the wall. In the rear elevation a band of bare brick shows between the corona and the lower block along the return. The recess is closed by the wall, not open, so this is not the v002 open-slot class, but it reads as two stacked slabs. | The return's frieze/bed block stops below the corona soffit. | Raise the return's frieze/bed block to meet the corona soffit, or add a cymatium/bed fillet across the gap. |
| 3 | P2 | left_side (≈x 1254–1257, y 388–392) | Tiny black notch at the junction of the SW corner raised block's base and the west parapet coping. | A coping segment ends short of the raised block. | Extend the coping to butt the block, or tuck it under. |
| 4 | P2 | architecture_close (≈x 800–960, y 245–345); front (corner block) | The SE corner raised parapet block reads as two overlapping brick blocks, one for the south corner and one for the east corner, with copper caps at slightly different heights. The source has one corner block. | The south and east raised-block generators each place a block at the shared corner. | Emit one corner block with one cap. |
| 5 | P2 | east_side, right_side, front | The east-side ground arched windows have light granite-coloured arch rings. In the sources (front crop x≈800–900, oblique x≈940–1020) these are plain brick-arched openings without stone archivolts. | The upper-window archivolt component is reused on the ground arches. | Use brick (or brick soldier-course) arches for the east ground windows. |
| 6 | P2 | top, roof_chimneys, aerial | The roof membrane renders as near-neutral mid grey, about (133,130,126). The source membrane is brown-grey, about (135,117,101). The builder's "darker brown-grey" change barely reads. | Membrane colour has too little chroma. | Shift the membrane toward warm brown-grey. |
| 7 | P2 | granite_piers, facade_close, front | Pier rustication is thin incised lines. The source shows deep channel joints with pronounced block faces and a projecting plinth at the pier foot, which the render lacks. The NW coping lap also shows a small step (left_side ≈x 810–814, y 537–545). Neighbour windows are flat dark rectangles with no reveal (context only). | Shallow joint depth; no plinth component. | Deepen the channel joints, add a pier plinth course and align the NW coping mitre. Optionally recess the neighbour windows. |

## 3. Source conformance checklist

| Item | Status | View(s) used |
|---|---|---|
| Silhouette (two-storey corner block with parapet, cornice and corner pier) | conforms | front, front_corner, aerial vs source front/oblique |
| Storey count and proportions (tall ground storey, tall upper storey, deep cornice, parapet) | conforms (ground ≈205 px vs upper ≈160 px in render front, similar ratio to source) | front, right_side |
| Piers (rusticated granite, caps under brackets) | conforms, with shallow rustication and no plinth (P2 #7) | granite_piers, facade_close, arched_windows |
| Brick bays between piers | conforms | facade_close, east_side, arched_windows |
| Shopfronts and entrance (dark-green frames, transoms, double door in middle south bay with sidelights) | conforms. Left bay has 2 lights, middle bay has door and sidelights, corner bay has 3 lights, all with transoms. The east corner bay's two tall glazed openings in brick match the source. | facade_close, glass_close, interior, front, granite_piers |
| Belt entablature (granite) | conforms | facade_close, granite_piers, east_side |
| Arched windows on the south front (triplet / one large arch / pair, granite archivolts, keystones, sills, imposts) | conforms | front, facade_close, arched_windows, front_corner |
| Arched windows on the east side (counts per bay) | **deviates** (P1 #1): upper pair/pair/pair vs source pair/triplet/pair | right_side, east_side vs source front, oblique |
| Copper cornice and brackets (deep verdigris corona, frieze, modillions, consoles at piers) | conforms. SW overhang back is closed. NE return has a minor shadow gap (P2 #2). | copper_cornice, architecture_close, arched_windows, left_side, rear |
| Parapet, raised blocks over piers, raised panel over middle bay, copper coping | conforms. The SE corner block is doubled (P2 #4). | copper_cornice, roof_chimneys, front_corner, aerial, architecture_close |
| East ground windows (arched, in brick, behind corner shop) | partly deviates. Arches are present, but their rings are granite-coloured (P2 #5), and the north bay has a triplet where the source has a pair (P1 #1). | east_side, right_side |
| Roof and chimneys (flat membrane, two brick chimneys on the north parapet) | conforms in position (≈0.36/0.70 along the north parapet vs source ≈0.31/0.70). The chimneys sit within the coping. Membrane colour is too neutral (P2 #6). | top, roof_chimneys, rear_north, left_side |
| Sidewalks, trees and lamp (tree and lamp at the SW on the south walk, tree and lamp at the NE on the east walk, corner crossing) | conforms | top, front_corner, aerial |
| Neighbour (brick, attached west, main block stops short of the north wall, lower annex and paved strip behind) | conforms. In the render top the main block reaches about 71% of warehouse depth, with the annex and asphalt behind. The source top shows about 69% of depth, with a lower annex and a paved strip behind. The warehouse's west parapet stands free for its northern part. No slit at the party wall. | top, left_side, rear_side, rear, front |
| Materials hierarchy (granite piers and trim > brick bays > dark-green glazing frames; verdigris cornice and coping) | conforms | all whole-envelope views |
| North and west faces (not shown by any source) | coherent: coursed brick, plain punched windows with sills, copper coping | rear, rear_north, left_side |

## 4. Camera validity

All 18 views are valid. The target is legible in every view, nothing important is clipped, and no view is occluded.
- east_side: the low-poly tree crown covers part of the northern upper pair (x≈1185–1440, y≈405–700). The bay is still readable.
- right_side: the tree covers part of the north bay's upper right window. The bay is still readable.
- glass_close and interior are tight but legible, showing frames, transoms and the bulkhead.
- top: the plan is legible and matches the source top in orientation (street south, side street east, neighbour west).

## 5. Previous-version (v003) findings: are they resolved in the pixels?

| v003 finding | Resolved? | Evidence |
|---|---|---|
| Back of the south copper cornice's south-west end, where it runs past the west wall above the neighbour, open with pure-black slots between the corona, frieze and bracket layers | **Resolved** | left_side (≈x 1250–1320, y 395–440): seen from the north-west, the back of the overhang is closed by a continuous copper face following the profile, with no black slots. front_corner and aerial show the corona over the neighbour intact. One tiny unrelated black notch at the raised-block/coping junction is listed as P2 #3. |
| West neighbour running deeper than the warehouse, reversing the locked top view | **Resolved** | top: the neighbour's main block spans ≈y 467–692 against the warehouse's ≈y 380–695, about 71% of depth. A lower annex sits at ≈y 432–467 and asphalt continues north. This matches the source top (about 69%, annex and paved strip behind). left_side and rear_side show the free-standing north part of the warehouse's west wall with coping, and the lower annex with windows and a door. No slit opens at the party wall. |
| Rectangular recess at both shoulders of the large arched window in the middle south bay (wall cut larger than the arched head) | **Resolved** | facade_close and the front_corner zoom: the spandrels at both shoulders are flush brick, with mortar courses running continuously to the archivolt. No rectangular recess or cut corner is visible. |

Also checked against the builder's P2 claims. Copper coping on the west parapet: present. Coursed brick on the north and west walls: present. Granite impost blocks at the arch springing: present, and the arcs are smooth at render scale. Chimneys seated in the coping: yes. Roof membrane darker brown-grey: only marginally; it still reads neutral grey (P2 #6). Windows on the neighbour's rear face and annex: present.
