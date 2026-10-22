# Independent holistic review: clay-princes-island-park v004 (RLASM v6.1)

Verdict: FAIL

Counts: P0=0 P1=4 P2=7

Reviewer: independent. I did not build this model. I judged only rendered pixels against the locked sources `sources/front.png`, `sources/oblique.jpg` and `sources/top.jpg`. I opened all 18 renders in `renders/` at full resolution (1440 x 1080), all four phone boards, and the matching v003 renders in `tools/clay_princes_island_park/evidence/v003/renders/` for the regression comparison. Zoomed crops and the pixel measurements quoted below are read-only derivatives in `review/crops_joowne/`.

Note: the brief's render list names `facade_close`, `architecture_close` and `glass_close`. None of these exist. The 18 renders present are aerial, bench_plaza, boardwalk, footbridge, front, front_corner, glazing_close, green_roof, left_side, pavilion_close, porch_northwest, promenade_beds, rear, rear_side, right_side, riprap_bank, top and west_path.

## 1. Verdict

**FAIL (VISUAL_REWORK_REQUIRED).** The new kit fixes the v003 primitive look. Flower heads are now real coneflower, salvia and panicle forms, and the grasses are fine and arching with plumes. Four P1s remain.
- Near-field bed margins at eye level still show a smooth, featureless green fill plane.
- The large grove bed between the pavilion and the boardwalk has regressed from planted to near-bare lawn.
- Pure-black geometry voids sit at every paving joint crossing, in the bench seats and under the pavilion doors. They were already present in v003 and the v003 review missed them.
- A continuous pure-black slot runs along the footbridge deck edge.

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | front (both foreground beds), promenade_beds (left bed), west_path (right bed), porch_northwest (right bed edge); crops `front_right_bed.png`, `front_left_bed.png`, `prom_left_bed.png`, `west_right_bed.png` | **The plant forms are fixed, but the fill is not.** Inside each near-field kerb, roughly 40–60% of the visible bed is a smooth, untextured, uniformly lit mid-green plane, with plants standing as isolated clumps on it. In front (right foreground bed) the whole left half of the bed, from the kerb to the first rosette, is bare carpet with one small blue grass. In front (left bed) the plants sit in the outer third and the rest is flat green. In promenade_beds (left bed), one leafy shrub, two small clumps and one feather-reed grass stand on an open green sheet that runs to the kerb. In west_path (right bed), the strip from the kerb to the salvias is empty carpet. The promised "second pass of small edging plants" does not show at the margins. In the locked front and oblique, the beds are covered kerb to kerb, with grasses and shrubs spilling over the edge and no visible ground. Mid- and far-field beds read dense (promenade_beds right bed, bench_plaza, west_path far beds), so the defect sits where the camera is closest. | The groundcover carpet is a flat, low mesh with a plain material and no relief or instanced cover. The margin pass is too sparse, or its plants are too small to read from 1.6 m. The density falloff runs from the centre outward, so the margins nearest the path are thinnest. | Instance the kit's low groundcover tufts or mat clumps over the carpet at a density that hides at least 85% of it from eye level. Reverse the falloff at path-facing kerbs so the front 0.6 m of each bed is the densest band, with grasses and salvias leaning over the kerb. Verify with front, promenade_beds and west_path crops. |
| 2 | P1 (regression) | right_side, rear_side, rear, front_corner, green_roof, aerial, porch_northwest; crops `grove_bed_source_v003_v004.png`, `aerial_grove_bed.png` | **The grove beds have become lawn.** The large kerbed grove bed between the pavilion and the boardwalk is now a dark-green carpet with about 15 isolated dark shrub balls and 2–3 lone grass tufts spread across it. Most of the bed reads as empty mown grass. The same bed in v003 was filled with mounds, grasses and flowers. The locked oblique (between the pavilion's north-east face and the boardwalk) and the top view (under the grove north and north-east of the roof) both show a dense, layered understorey of shrubs and straw grasses with no ground visible. The north-west grove bed is thinner but still reads as planted. | The "sparser grove" setting sets the kit density far below the source. The tree-trunk clearance rule may also be removing most candidates under the large crowns. | Raise grove-bed density to at least 60% of the promenade-bed density. Use shade-type kit shrubs, feather-reed and fountain grasses, and drifts in groups of 5–9 rather than single specimens. Shrink the trunk clearance to the trunk radius plus 0.3 m. Check right_side and front_corner against the oblique. |
| 3 | P1 (pre-existing since v003, missed by the v003 review) | bench_plaza (visible even on phone board 03), front, promenade_beds, pavilion_close, front (SW door), west_path (bench back); crops `bench_joints.png`, `front_joint_dots.png`, `bench_top_dots.png`, `westpath_bench.png`, `pavclose_door_sill.png` | **Pure-black geometry voids.** (a) At every pale-slab joint crossing there is a 4–8 px square of RGB 0–1, while the joint grooves either side render at about 155 and the darkest genuine contact shadow in the same frame (under the bench) is about 120. (b) In bench_plaza, each bench seat has two black rectangular slots where the steel frame meets the top slat. In west_path the bench back post shows a black vertical slot. (c) Under both pavilion doors (pavilion_close, about 100 x 10 px; front SW door; porch doors) a black slot runs between the door leaf and the slab. All of these are identical in the v003 renders (same pixels, RGB 0). **How I told them apart from shadow:** genuine contact and leaf shadow in these frames never falls below about 35–120 because of the grey world fill, and it has soft gradients. These patches are hard-edged, zero-irradiance and sit on geometry seams. That points to open cavities or interior faces, not shadow. | The joint grooves are cut as strips that stop short of each other, leaving an open well into the inside of the slab at each crossing. Bench frame posts pass through the slat volume, showing their inner faces. The door leaves are short of the threshold, with an open, unlit cavity behind. | Cap the slab joint crossings: extend one groove strip through the crossing, or add a groove-floor quad. Trim the bench posts below the slat underside or close the slat mesh. Add a threshold or extend the door leaf to 10 mm above the slab, and close the door reveal. Re-scan all renders for clusters of 4 or more pixels with max channel below 10 on hardscape. |
| 4 | P1 (pre-existing since v003, missed by the v003 review) | footbridge, rear_side (at distance); crop `bridge_edge_line.png` | **A pure-black slot runs along the footbridge deck edge.** A continuous 1–3 px pure-black line (RGB 0–1 at every sampled column, x = 720…1080) runs the full length of the near deck edge, between the kerb upstand and the edge beam, under the railing. The edge beam's own shadowed face beside it renders at about 35–80. At review scale it reads as a black seam or cut through the bridge fascia. | There is a gap between the deck slab and the edge beam or kerb meshes, showing an unlit interior or backfaces. | Close the seam: merge or overlap the deck, kerb and edge-beam profiles, or add a filler face. Recheck footbridge. |
| 5 | P2 | aerial, top, front_corner; crop `se_bed_top_v003_v004.png` | From the air the beds read as an even salt-and-pepper of pink flower clusters and straw fountain-grass stars on dark carpet. The noise-grouped drifts do not read as drifts. The source top shows the south-east bed dominated by rounded yellow-green and dark-green shrub masses, with pink only as accents. Bed plan shapes and positions still match the top view. | Low shrub share and a high coneflower share. Drift noise scale is too fine to read at plan scale. | Raise the shrub share in the pavilion-side and south-east beds, enlarge the drift noise scale to about 3–4 m, and cut pink to accent patches. |
| 6 | P2 | green_roof, aerial, front_corner, front | The sedum is still a flat camouflage decal with sparse cube nubs, flush with the fascia, and is not visible above the fascia at eye level. After the reseed it is more ochre- and straw-dominant than v003 (less olive), and from the aerial it shows a streaky, maze-like pattern. The top source roof is olive-green with ochre and rust. | Random stream change on the roof decal, and the roof surface sits flush. | Re-weight toward olive green, coarsen the patches, raise the mat slightly above the fascia and add fine tufts. |
| 7 | P2 | riprap_bank, right_side, rear_side | The rip-rap is pale, hard-faceted polyhedra with sparse single grass tufts and a flat dark waterline apron. Unchanged from v003. | Low-segment boulder mesh. | Add subdivision and smooth shading, warm the colour, cluster the bank grass. |
| 8 | P2 | boardwalk, footbridge, right_side | The railings are pale grey-white open pickets, while the sources show darker steel. Unchanged. | Material colour. | Darken toward the source steel grey. |
| 9 | P2 | bench_plaza, front_corner | The benches have no end armrests (the locked front bench has them). Unchanged. | Simplified bench. | Add armrest frames. |
| 10 | P2 | footbridge, rear_side, west_path, rear | Hard model edges and grey void show at frame edges. Unchanged. | Finite plinth. | Extend the ground skirt or tighten the framing. |
| 11 | P2 | rear, footbridge, all wide views | The trees are repetitive low-poly blob clusters, and the far-bank trees are lollipops on bare poles. In rear, foreground crowns cover about half the frame. Unchanged. | Shared tree kit; rear camera behind the grove. | Vary crowns; retarget the rear camera. |

## 3. Source conformance checklist

| Item | Status | View(s) used |
|---|---|---|
| Plan vs top: pavilion position and rotation (~27° off river) | conforms | aerial, top vs top.jpg |
| Plan: promenade from south plaza past SW face to NW; paved band crossing west; slab paths to porch and north | conforms | aerial, front_corner, left_side |
| Plan: two N–S cycle paths, eastern one onto boardwalk | conforms | aerial, top, front_corner |
| Plan: lens-shaped kerbed beds between paths | conforms (shapes and positions unchanged) | aerial, top, front_corner |
| Plan: groves north of pavilion and along boardwalk | conforms for trees; **understorey deviates (P1 #2)** | aerial, right_side, rear |
| Plan: boardwalk along rip-rap bank, river on east | conforms | aerial, top, right_side |
| Pavilion: green sedum roof | conforms in presence; deviates in finish (P2 #6) | green_roof, aerial |
| Pavilion: thin dark metal fascia | conforms | pavilion_close, porch_northwest, glazing_close |
| Pavilion: cedar board-and-batten | conforms | pavilion_close, porch_northwest, front |
| Pavilion: fully glazed SE face, dark mullions, depth, long table inside | conforms | glazing_close |
| Pavilion: SW door and corner glazing | conforms; **door sill void (P1 #3)** | front, pavilion_close |
| Pavilion: open NW porch with two doors | conforms; **door sill voids (P1 #3)** | porch_northwest |
| Pavilion: NE clerestory windows | conforms | riprap_bank, glazing_close (from inside) |
| Pavilion: slim timber posts at roof corners | conforms | front, green_roof, porch_northwest |
| Pavilion: interior | conforms | glazing_close, pavilion_close |
| Promenade: pale slabs with joints | conforms in layout; **black voids at joint crossings (P1 #3)** | bench_plaza, front, promenade_beds |
| Promenade: flush dark granite sett borders and bands | conforms (holds) | front, promenade_beds, pavilion_close |
| South plaza: sett frame | conforms | front_corner, aerial |
| South plaza: two trees in kerbed pits (now with groundcover and a ring of small grasses) | conforms | front_corner, aerial |
| Cycle paths: asphalt, yellow dashed centre line, flush concrete edges | conforms | west_path, bench_plaza, front_corner |
| Boardwalk: raised concrete deck and kerbs, clear of boulders | conforms (holds) | boardwalk, right_side, rear_side |
| Boardwalk: railings on both sides, open | conforms in form; deviates in colour (P2 #8) | boardwalk, right_side |
| Boardwalk: ramps and landings | conforms | rear_side, right_side |
| Rip-rap and bank grasses | deviates slightly (P2 #7) | riprap_bank, right_side |
| River | conforms (flat clay water) | right_side, rear_side, footbridge |
| Planting beds: kerbs | conforms (no plant through or over the kerb plane; leaves overhang only) | front, promenade_beds, west_path |
| Planting beds: grasses | conforms (feather-reed with plumes, fountain grass, blue edging grass; fine arching blades) | promenade_beds, glazing_close, bench_plaza |
| Planting beds: shrubs | conforms at eye level (leafy 0.8 m shrubs); under-represented from the air (P2 #5) | promenade_beds, aerial |
| Planting beds: pink, lavender and white flowers | conforms (coneflowers with reflexed petals and cones, salvia spikes, white panicles, astilbe) | front, glazing_close, west_path, bench_plaza |
| Planting beds: fill and density | **deviates (P1 #1)** at near-field margins; conforms mid- and far-field; grove beds **deviate (P1 #2)** | front, promenade_beds, west_path, right_side |
| Trees: rounded deciduous groves | conforms (P2 #11) | left_side, boardwalk, rear |
| Benches (timber on dark steel) and corten bins | conforms in form; **seat-frame voids (P1 #3)**; no armrests (P2 #9) | bench_plaza, west_path, front |
| Footbridge: cambered deck, two piers | conforms | footbridge, rear_side |
| Footbridge: abutments, landings, open railings | conforms; **deck-edge black slot (P1 #4)** | footbridge, rear_side, top |
| Far bank: wooded | conforms (holds; understorey reseeded, still reads wooded) | footbridge, top, left_side |
| Materials hierarchy (pale slab > dark sett > asphalt > cedar > greens) | conforms | front, front_corner |
| Aerial-scale finish vs park benchmark | conforms with P2 #5 (composition) | aerial, front_corner, left_side |
| Pedestrian-scale finish vs park benchmark (conservatory) | plant forms now conform; **fill, density and voids deviate (P1 #1, #3)** | front, promenade_beds, west_path, bench_plaza, glazing_close |

## 4. Camera validity

- No view is invalid. In every render the target is in frame, unclipped and legible.
- rear: foreground grove crowns fill about half the frame and the pavilion reads only as a roof patch (P2 #11). It is legible as the north grove.
- footbridge, rear_side, west_path: the plinth edge or grey void shows at the frame edge (P2 #10). The target is still legible.
- glazing_close: kit plumes and panicles rise in front of the lower glazing but do not hide the mullions, table or interior.
- Dark-pixel scan: I measured every cluster of 4 or more pixels darker than 22 in all 18 renders and checked each by crop. Large dark clusters inside the beds (front lower right, promenade_beds, bench_plaza) are leaf self-shadow inside dense rosettes, with soft gradients and leaf-shaped outlines. Wide dark bands in glazing_close, pavilion_close and porch_northwest are the dark metal fascia material. Small dark specks in boardwalk, riprap_bank and right_side are shrub leaf shadow behind the railings. Only the items in P1 #3 and #4 are zero-irradiance geometry voids.

## 5. Previous-version (v003) findings: status in pixels

1. **P1 #1, beds read as primitives at eye level: PARTIALLY FIXED, with the remainder carried as P1 #1.**
   - (a) Faceted cone flower heads: **fixed.** Every flower is now a coneflower with reflexed pink petals and a brown cone, a salvia spike, a white panicle or an astilbe plume, on stems above leafy rosettes (glazing_close, front, west_path crops). No pointed cone or crystal heads remain.
   - (b) Flat straw-ribbon grasses: **fixed.** The grasses are fine, tapered, arching blades with feather-reed plumes, a green fountain grass and a blue edging grass (promenade_beds, front, glazing_close).
   - (d) Faceted shrubs: **fixed.** The 0.8 m kit shrub is leafy and has no faceted silhouette (promenade_beds left bed).
   - (c) Bare fill between mounds: **not fixed.** The fill is now a smooth carpet instead of fill with troughs, but at near-field margins it still shows as a flat, untextured green plane over 40–60% of the visible bed (see P1 #1).
2. P2 #2, rip-rap faceted with sparse grass: **not fixed** (unchanged; P2 #7).
3. P2 #3, pale railings: **not fixed** (unchanged; P2 #8). The open pickets still hold.
4. P2 #4, sedum decal flush with fascia: **not fixed, slightly regressed in hue.** The reseed is more ochre and straw, less olive, with a streaky pattern from the air (P2 #6).
5. P2 #5, benches without armrests: **not fixed** (P2 #9).
6. P2 #6, hard model edges: **not fixed** (P2 #10).
7. P2 #7, repetitive trees and weak rear camera: **not fixed** (P2 #11).

Earlier fixes and v003 strengths checked for regression:
- Aerial planting pattern (bed shapes and positions against the top view): **holds.** Composition is now less shrubby (P2 #5).
- Grove understorey: **regressed** (P1 #2).
- Sett paving: flush dark granite sett borders, sett bands across the promenade, and the south-plaza sett frame **hold**.
- Sedum roof: holds as a continuous mat. Hue drift is P2 #6.
- Railings: open picket railings on both boardwalk sides and the footbridge, with no solid panels, **hold**.
- Boardwalk: raised deck clear of boulders, both kerbs clear, ramps and landings **hold**.
- Wooded far bank round the footbridge landing: **holds** (footbridge, top).
- Pavilion (position, rotation, cedar, glazed SE face with table, porch, posts, fascia), cycle paths with yellow dashes, footbridge on two piers, corten bins: **hold**.
- The geometry voids in P1 #3 and #4 are **not regressions**. They are pixel-identical in v003 and were missed by the v003 review.
