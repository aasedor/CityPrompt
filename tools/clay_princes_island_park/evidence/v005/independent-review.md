# Independent holistic review: clay-princes-island-park v005 (RLASM v6.1)

Verdict: PASS_ZERO_P0_P1

Counts: P0=0 P1=0 P2=10

Reviewer: independent. I did not build this model. I judged only rendered pixels against the locked sources `sources/front.png`, `sources/oblique.jpg` and `sources/top.jpg`. I opened all 18 renders in `renders/` at full resolution (1440 x 1080), all four phone boards, and the matching v004 renders in `tools/clay_princes_island_park/evidence/v004/renders/` for side-by-side regression checks. Zoomed crops, v004/v005 pairs and pixel measurements are read-only derivatives in `review/crops_qmvtek/`. I ignored the builder's notes, counts and evidence JSON as proof.

Note: the brief's render list names `facade_close`, `architecture_close` and `glass_close`. None of these exist. The 18 renders present are aerial, bench_plaza, boardwalk, footbridge, front, front_corner, glazing_close, green_roof, left_side, pavilion_close, porch_northwest, promenade_beds, rear, rear_side, right_side, riprap_bank, top and west_path. `pavilion_close` and `glazing_close` cover the pavilion close-ups.

## 1. Verdict

**PASS_ZERO_P0_P1.** All four v004 P1s are fixed or reduced to polish: the geometry voids at paving crossings, benches, door sills and the footbridge deck edge are gone; the grove bed is now a planted understorey; and the bare kerb-side fill has roughly halved and is broken up by edging plants. Nothing that read correctly in v003 and v004 regressed. What remains is P2 polish: a residual bare strip at two near-kerb bed tips, a thinner-than-source grove understorey from above, pinpoint black specks at the footbridge railing post heads, and the unchanged P2s carried from v004.

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P2 (residual of v004 P1 #1) | front (right foreground bed), promenade_beds (right bed tip, left bed kerb strip); crops `front_right_bed_v004_v005.png`, `prom_right_v004_v005.png`, `prom_left_v004_v005.png` | The near beds now read planted. Blue edging grass, white alyssum cushions and salvias break up the kerb-side fill, and the left beds in front, porch_northwest and west_path read fully planted. A smooth green strip still shows inside the near kerb of the front right bed (left tip and the long near kerb) and at the tip of the promenade_beds right bed. Measured as the share of green pixels with a 7x7 local std below 2.5 (flat carpet) in the same crop boxes, v004 to v005: front right bed 0.43 to 0.25; promenade left 0.45 to 0.21; promenade right 0.32 to 0.19; west_path right 0.43 to 0.22; porch right 0.47 to 0.13; porch left 0.73 to 0.18. (v004 is JPEG, whose noise biases its flat share down, so the real improvement is at least this large.) The 2.8 cm groundcover undulation is not visible. Leaves never spill over the kerb, whereas the locked front and oblique show grasses spilling over the kerb edge. This is a small, frame-edge strip, not a bed-scale bare carpet. | The 0.27 m cushion ring is too sparse on long straight kerb runs, and the 3 cm canopy clearance stops any overhang. | Add 2 or 3 more cushion or edging-grass runs on the near kerbs of the front right bed and the promenade right bed tip, and allow low grass blades (not stems) to overhang the kerb top by 5 to 10 cm. |
| 2 | P2 (residual of v004 P1 #2) | green_roof, right_side, aerial, boardwalk; crops `grove_green_roof_v004_v005.png`, `grove_right_side_v004_v005.png`, `grove_aerial_v004_v005.png`, `grove_boardwalk_v004_v005.png` | The grove bed between the pavilion and the boardwalk is now clearly planted: large leafy shrub masses, fountain and feather-reed grasses, astilbe and panicles, with an edging band along both kerbs. From eye level (boardwalk, right_side) it reads as a full understorey. From the steeper green_roof view, green ground still shows between the clumps over roughly a third of the bed. The oblique source shows a denser, continuous layered understorey with no ground visible. | 1.4 m spacing leaves gaps once clumps sit under the tree-trunk clearance. | Infill with low shade groundcover clumps at 0.7 m between the existing clumps in the bed centre. |
| 3 | P2 | footbridge (top rails), present identically in v004; crop `bridge_rail_dots.png` | About seven pinpoint pure-black specks (1 to 3 px across, RGB 1 to 7, e.g. at x 1326 y 700, x 1038 y 744, x 1200 y 636) sit where railing posts meet the top rail. They are hard-edged and zero-irradiance, so they are geometry voids, not shadow. Lit rail faces beside them read 150 to 170 and the darkest true shadow on the rail is about 75. They are visible only on close inspection and are far smaller than the v004 joint-crossing squares (4 to 8 px, repeated over every paving crossing). | Post-head caps intersect or share a plane with the top rail, exposing an inner face. | Stop each post 2 mm under the top-rail underside, or merge the post head into the rail profile. Re-scan footbridge for clusters with max channel below 10. |
| 4 | P2 (v004 P2 #5, partially addressed) | aerial, top, front_corner | From the air the beds still read as an even scatter of pink dots and straw fountain-grass stars on dark carpet, though with more shrub mass than v004. The top source shows rounded yellow-green and dark shrub masses dominating, with pink as accents. Bed shapes and positions still match the top view. | Drift noise scale too fine; coneflower share still high in the rear beds. | Enlarge the drift scale to 3 to 4 m and cut pink to accent patches. |
| 5 | P2 (v004 #6, not addressed) | green_roof, aerial, front | The sedum is still a flat olive, ochre and rust camouflage decal with cube nubs and a streaky pattern from the air. At eye level it is flush with the fascia and not visible. The source roof is olive-dominant and the mat crests the fascia in the locked front. | Flat decal, flush surface. | Re-weight toward olive, raise the mat slightly, add fine tufts. |
| 6 | P2 (v004 #7) | riprap_bank, right_side, rear_side | Pale, hard-faceted boulder polyhedra with sparse single grass tufts and a flat dark waterline apron. | Low-segment boulder mesh. | Subdivide and smooth, warm the colour, cluster the bank grasses. |
| 7 | P2 (v004 #8) | boardwalk, footbridge, right_side | Railings are pale grey-white open pickets; the sources show darker steel. The pickets are now 200 mm apart and still read as open. | Material colour. | Darken toward the source steel grey. |
| 8 | P2 (v004 #9) | bench_plaza, west_path, front_corner | Benches have no end armrests; the locked front bench has them. | Simplified bench. | Add armrest frames. |
| 9 | P2 (v004 #10) | footbridge, rear_side, left_side, west_path | Hard model edges: the plinth and the river end at a straight cut into grey void. | Finite plinth. | Extend the ground skirt or tighten the framing. |
| 10 | P2 (v004 #11) | rear, footbridge, all wide views | Trees are repetitive low-poly blob clusters; far-bank trees are lollipops on bare poles. In rear, foreground crowns fill about half the frame and the pavilion reads as a roof patch. | Shared tree kit; rear camera behind the grove. | Vary crowns; retarget the rear camera. |

## 3. Source conformance checklist

| Item | Status | View(s) used |
|---|---|---|
| Plan vs top: pavilion position and rotation (~27° off river) | conforms | top, aerial vs top.jpg |
| Plan: promenade from south plaza past SW face to NW; paved band crossing west; slab paths to porch and north to footbridge landing | conforms | aerial, top, front_corner, left_side |
| Plan: two N–S cycle paths, eastern one rising onto boardwalk | conforms | aerial, top, front_corner |
| Plan: lens-shaped kerbed beds between paths | conforms (shapes and positions unchanged) | aerial, top, front_corner |
| Plan: groves north of pavilion and along boardwalk | conforms (understorey now planted; P2 #2) | aerial, right_side, green_roof, boardwalk |
| Plan: boardwalk along rip-rap bank, river on east | conforms | aerial, top, right_side |
| Pavilion: green sedum roof | conforms in presence; finish deviates (P2 #5) | green_roof, aerial |
| Pavilion: thin dark metal fascia | conforms | pavilion_close, porch_northwest, glazing_close |
| Pavilion: cedar board-and-batten | conforms | pavilion_close, porch_northwest, front |
| Pavilion: fully glazed SE face, dark mullions, depth, long table inside | conforms | glazing_close, front_corner |
| Pavilion: SW door and corner glazing | conforms; door sits on a solid threshold with no void (crops `pav_door_v004_v005.png`, `front_sw_door.png`) | front, pavilion_close |
| Pavilion: open NW porch with two doors | conforms; both doors meet the sill with no void (crop `porch_doors_v004_v005.png`) | porch_northwest, promenade_beds |
| Pavilion: NE clerestory windows | conforms | riprap_bank, glazing_close (from inside) |
| Pavilion: slim timber posts at roof corners | conforms | front, green_roof, porch_northwest |
| Pavilion: interior | conforms (table, benches, rear doors, ceiling light) | glazing_close, pavilion_close |
| Promenade: pale slabs with joints | conforms; no voids at joint crossings (front paving min > 25 away from planting; crop `front_paving.png`) | front, bench_plaza, promenade_beds |
| Promenade: flush dark granite sett borders and bands | conforms (holds) | front, promenade_beds, pavilion_close |
| South plaza: sett frame | conforms | front_corner, aerial |
| South plaza: two trees in kerbed pits | conforms | front_corner, aerial |
| Cycle paths: asphalt, yellow dashed centre line, flush concrete edges | conforms | west_path, bench_plaza, front_corner |
| Boardwalk: raised concrete deck and kerbs, clear of boulders | conforms (holds) | boardwalk, right_side, rear_side |
| Boardwalk: railings on both sides, open | conforms in form; colour deviates (P2 #7) | boardwalk, right_side |
| Boardwalk: ramps and landings | conforms | rear_side, right_side |
| Rip-rap and bank grasses | deviates slightly (P2 #6) | riprap_bank, right_side |
| River | conforms (flat clay water) | right_side, rear_side, footbridge |
| Planting beds: kerbs | conforms (no plant through the kerb); no spill over the kerb (P2 #1) | front, promenade_beds, west_path |
| Planting beds: grasses | conforms (feather-reed with plumes, fountain grass, blue edging grass) | promenade_beds, glazing_close, boardwalk |
| Planting beds: shrubs | conforms at eye level; under-represented from the air (P2 #4) | promenade_beds, green_roof, aerial |
| Planting beds: pink, lavender and white flowers | conforms (coneflowers, salvia spikes, white panicles, alyssum, astilbe) | front, glazing_close, west_path, bench_plaza |
| Planting beds: fill and density | conforms with a residual near-kerb strip (P2 #1); grove bed conforms with P2 #2 | front, promenade_beds, west_path, porch_northwest, right_side |
| Trees: rounded deciduous groves | conforms (P2 #10) | left_side, boardwalk, rear |
| Benches (timber on dark steel) and corten bins | conforms; no seat or back-post voids (crops `bench_plaza_bench.png`, `west_bench_v004_v005.png`); no armrests (P2 #8) | bench_plaza, west_path, front |
| Footbridge: cambered deck, two piers | conforms | footbridge, rear_side |
| Footbridge: abutments, landings, open railings | conforms; deck-edge seam gone (crop `bridge_edge_v004_v005.png`); pinpoint rail-head specks (P2 #3) | footbridge, rear_side, top |
| Far bank: wooded | conforms (holds) | footbridge, top, left_side |
| Materials hierarchy (pale slab > dark sett > asphalt > cedar > greens) | conforms | front, front_corner |
| Aerial-scale finish vs park benchmark | conforms with P2 #4 and #5 | aerial, front_corner, left_side |
| Pedestrian-scale finish vs park benchmark (conservatory) | conforms with P2 #1 and #3; kit plant forms hold and the hardscape is now clean | front, promenade_beds, west_path, bench_plaza, glazing_close, porch_northwest |

## 4. Camera validity

- No view is invalid. In every render the target is in frame, unclipped and legible.
- rear: foreground grove crowns fill about half the frame and the pavilion reads only as a roof patch (P2 #10). It is still legible as the north grove and pavilion.
- footbridge, rear_side, left_side, west_path: the plinth edge or grey void shows at the frame edge (P2 #9). The target is still legible.
- glazing_close: plumes, salvias and panicles rise in front of the lower glazing but do not hide the mullions, table or interior.
- west_path: the far bench back is partly screened by near salvias; where visible it shows no void.
- How I told geometry voids from shadow. I scanned every render for clusters of 4 or more pixels with max channel below 10, then pixels below 25 and 40 restricted to hardscape, benches and door sills, and checked each cluster by crop.
  - Clusters inside beds (front lower right, bench_plaza left, promenade_beds bed edges, porch_northwest left bed, boardwalk, riprap_bank, west_path) are leaf self-shadow inside dense rosettes and shrubs. They have soft gradients and leaf-shaped outlines.
  - Thin dark bands at y 199–265 in pavilion_close, y 66–78 in glazing_close and y 213–230 in porch_northwest are the dark metal fascia material.
  - The darkening at the base of the porch doors is a soft vertical gradient on the dark door material (row means 20 to 27, falling smoothly to the sill), not a slot.
  - No hardscape region (front, bench_plaza, promenade_beds, west_path and pavilion_close paving, door sills) has any pixel below 25.
  - The only zero-irradiance geometry pixels left are the footbridge rail-head specks in P2 #3.

## 5. Previous findings: status in pixels

Candidate v003 (0 P0 / 1 P1):
- **v003 P1, eye-level planting read as primitives (cone heads, straw ribbons, bare fill): fixed and holds.** The flowers are coneflowers, salvia spikes, panicles and alyssum, with no cone or crystal heads. The grasses are fine, arching blades with plumes, with no flat ribbons, and the shrubs are leafy. The shared grass-blade change for the size cap does not show at review scale. The bare-fill part is reduced to P2 #1.

Candidate v004 (0 P0 / 4 P1):
1. **P1 #1, bare flat carpet over 40–60% of the near beds: fixed as a P1, with a residual P2 (#1).** The flat-carpet share roughly halved in every near bed measured, to 0.13–0.25. The porch_northwest left bed, which was 73% flat in v004, now reads fully planted. The edging band of blue grass, alyssum and salvia is visible along most near kerbs. A small strip remains at the front right bed and the promenade right bed tip.
2. **P1 #2, grove bed by the boardwalk reduced to near-bare lawn: fixed.** right_side, boardwalk, green_roof and aerial all show a planted understorey of shrub masses, fountain and feather-reed grasses and panicles, with edging bands. Residual openness seen from above is P2 #2.
3. **P1 #3, pure-black holes: fixed.**
   - Paving-joint crossings in front, bench_plaza and promenade_beds show no dark pixels; hardscape minimum is above 25.
   - The bench seat-frame slots and the back-post slot are gone (bench_plaza, west_path).
   - The SW door (pavilion_close, front) and both porch doors (porch_northwest) now sit on a solid threshold, where v004 had RGB 0 slots.
4. **P1 #4, black seam along the footbridge deck edge: fixed.** The near deck edge in footbridge is a continuous lit kerb face with no dark line (side-by-side crop `bridge_edge_v004_v005.png`). rear_side shows no seam at distance. Pinpoint specks at the railing post heads, present identically in v004 and not reported there, are logged as P2 #3.
5. v004 P2 #5 (aerial salt-and-pepper): partially addressed, still P2 (#4). P2s #6–#11: not addressed, as the brief states (now #5–#10).

Regression check of elements that read correctly before:
- Aerial plan: **holds.** Bed shapes, path geometry, pavilion position and rotation are unchanged against the top source.
- Sett paving: **holds.** Flush dark sett borders, sett bands and the south-plaza frame are unchanged. The two-level joint change introduced no visible step or z-fighting.
- Sedum roof: **holds** as a continuous mat (finish remains P2 #5).
- Railings: **hold.** Open pickets on both boardwalk sides and the footbridge; the 200 mm spacing still reads as a picket railing.
- Boardwalk: **holds.** Raised deck clear of boulders, kerbs, ramps and landings.
- Wooded far bank: **holds** (footbridge, top).
- Pavilion, cycle paths, footbridge piers and corten bins: **hold.**
