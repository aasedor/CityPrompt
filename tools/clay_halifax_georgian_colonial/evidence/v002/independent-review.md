# Independent RLASM v6.1 holistic review: Halifax Georgian colonial house, clay v002

Reviewer: independent source-locked architectural-clay reviewer. I did not build this candidate.

I examined these inputs at full resolution with direct image reads: `sources/front.png`, `sources/oblique.jpg` and `sources/top.jpg`; all 18 renders in `renders/` (1440 x 1080); and the four phone boards in `boards/`. For the v001 comparison I used the v001 renders in `tools/clay_halifax_georgian_colonial/evidence/v001/renders/`. Zoomed crops supporting the evidence below are in `review/crops_kwbnrx/`. All pixel coordinates refer to the 1440 x 1080 renders. L is the 0–255 luminance (grey value) of a pixel.

## 1. Verdict

Verdict: FAIL

Counts: P0=0 P1=1 P2=12

All three v001 P1s are fixed and nothing regressed. However, a pure-black geometry slot at the junction of the portico entablature and the façade fails the zero-P1 gate; it was already present in v001 but was not recorded there. In the brief's vocabulary this is VISUAL_REWORK_REQUIRED.

## 2. Findings table

| id | severity | view(s) | finding (what the pixels show) | evidence | likely cause | suggested fix |
|---|---|---|---|---|---|---|
| 1 | P1 | garden_fence, front_corner, front | A pure-black vertical slot runs down the west end of the portico entablature, where the entablature meets the brick of the front. The slot spans exactly the entablature's height. It stops at the entablature's top and bottom edges, and lit stone lies on one side and lit brick on the other. | **garden_fence:** x 1349–1352, y 331–371, L = 0 across a 2–3 px core. The row profile at y=350 reads 99, 77, **2, 0**, 27, 150, 161, so lit brick (L≈100) is followed by the void and then the lit stone end face (L≈160). Crops: `gf_dark.png`, `gf_portico_junction.png`. **front_corner:** x 891–893, y 792–802 (`fc_portico_end.png`). **front:** a 1 px dark line at x 854, y 553–577 (`front_portico_ent.png`). **Not contact shadow:** the soft shadow the portico cornice casts on the same brick, 10–40 px to the left, bottoms out at L≈60 with a gradient. The slot is flat L 0 with hard edges and ends exactly at the member's limits. **Not dark-by-design:** the black downpipe beside it (x 1305–1315) is a continuous member from eave to plinth and passes through the string course. The slot exists only over the entablature's height. **Not a regression:** the same box in v001 `garden_fence.jpg` holds the same cluster (98 px at L < 22, min 0.6). v001 filed it among its "downpipe" clusters. | The portico entablature/architrave box stops a few centimetres short of the face of the wall or pavilion behind it, or its back end is open. The view therefore looks into an unlit gap. This is the same failure family as v001 P1 #2, at a junction that was not included in the v002 sweep. | Run the portico entablature, frieze and cornice back into the wall face by 2 cm or more. Alternatively, add a solid end/return block that laps into the brick, as was done for the door head and the pediment corner blocks. Check the east end of the portico entablature the same way. Rerender `garden_fence`, `front_corner`, `front` and `porch_columns`, then re-scan for flat L < 22 clusters on lit stone/brick junctions. |
| 2 | P2 | porch_columns, facade_close, architecture_close | Hairline dark creases persist along lintel soffits and sill joints when the camera looks into the joint (carried from v001 #7). The worst is under the lintel of the left ground-floor window in `porch_columns`. | porch_columns x 0–237, y 220–295: a 2 px core at L 0–1, with column profiles such as 93, 23, **0**, 18, 67 (`porch_lefthead.png`). facade_close upper heads at y=294: 1 px at L 18–20. architecture_close sill at x 922–963, y 998–1029: 1 px at L 6–7. I graded this P2 rather than P1 for three reasons. First, it is a uniform 1–2 px crease along the full length of a concave lintel-to-wall corner, not a bounded slot between two lit faces. Second, it appears only from cameras that look up into that corner, and it is absent in the head-on `glass_close`. Third, at review scale it reads as an occlusion crease, not as an opening. It is borderline: if it persists after the overlap fix below, escalate it. The same box in v001 has the same pixel count (469 against 459), so it is unchanged. | Lintels and sills are butted against the reveal with no overlap. Alternatively, the lintel soffit is open. | Overlap lintels and sills 5 mm or more into the wall and reveal, and close the lintel underside. Apply this in the same pass as #1. |
| 3 | P2 | front, top, aerial, garden_fence | The new front-lawn edging hedge sits at the street edge, behind the curb, with open lawn running up to the house. In the sources the low box hedge is a foundation planting against the house base, and the lawn lies between it and the curb. | source top: hedge band at y≈668–680 against the wall, curb at y≈738. source front: shrubs at x 430–660, y 520–560 at the plinth. render top: lawn at y 800–870, hedge at y 870–888 by the sidewalk (`top_frontstrip.png`). render front: hedge at the walk edge (`front_lawns.png`). | The hedge was placed on the curb line rather than the wall line. | Move the low hedges to the plinth line. Keep the stone curb at the sidewalk. |
| 4 | P2 | top, front_corner, roof_deck | The pavilion gable ridge still runs back nearly to the deck edge (v001 #4, unchanged). | top: apex at y≈655 against the deck front at ≈640. | Same as v001. | Lower the ridge so it dies into the hip about two-thirds of the way up the slope. |
| 5 | P2 | cornice_chimneys, front_corner, aerial | The slate coursing is still coarse, at about 10 lines per slope (v001 #5, unchanged). | cornice_chimneys main slopes | Same as v001. | Halve the course spacing. |
| 6 | P2 | facade_close, porch_columns | The door still has a rectangular four-light transom, not a fanlight. Its panes read dark brown (L≈19, RGB ≈ 26/18/15) because the hall behind is unlit. The glazing bars and the reveal have visible depth, so this is an interior, not a void (v001 #6, unchanged). | facade_close x 652–787, y 634–649 (`facade_doorhead.png`) | Same as v001. | Use an elliptical or segmental fanlight, and light the hall. |
| 7 | P2 | architecture_close | The rake-to-eave pocket is improved by the new corner block. A small blue-grey wedge of roof is still visible where the main eave stops against the block, at x≈1200–1206, y≈596–606. It is not black (v001 #8, reduced). | `arch_rakecorner.png` | The eave run still has no end cap. | Add an end return or cap on the eave run. |
| 8 | P2 | front_corner, aerial, cornice_chimneys | The modillions read as a coarse toothed band from high cameras (v001 #9, unchanged). | front_corner eaves | Same as v001. | Use a deeper corona and smaller, closer modillions. |
| 9 | P2 | rear, rear_wings | The rear door is a plain slab, and the north front has no downpipes (v001 #10, unchanged). This face is unseen in the sources, so it is judged for coherence only. | rear x 695–745, y 680–785 | Same as v001. | Add a simple surround and transom, and downpipes at the wing re-entrant corners. |
| 10 | P2 | aerial, front_corner, rear, rear_side | The east neighbour is a beige rendered box with plain gables. The source shows grey coursed stone with stepped gable parapets (v001 #11, unchanged; context only). | aerial x 900–1440 | Same as v001. | Use a grey stone value and stepped parapets. |
| 11 | P2 | rear, rear_wings, interior, facade_close | The brick reads salmon or pink in the lit north views. The portico entablature is heavy for its columns. The interior walls use the exterior brick colour (v001 #13, unchanged). | rear, rear_wings, interior | Same as v001. | Darken the brick slightly, slim the portico entablature, and use a plaster colour inside. |
| 12 | P2 | front_corner, facade_close | In `front_corner` the base of the west front touches the bottom frame edge, which matches the crop of the locked oblique source. In `facade_close` a canopy fragment intrudes at the top centre (x 510–740, y 0–45). Both are unchanged from v001 #14 and the v001 camera notes. | front_corner y=1080 across x 560–660 | Same as v001. | Optional: pull `front_corner` back about 5%, and move the canopy or the camera for `facade_close`. |
| 13 | P2 | right_side, left_side | The new `right_side` is valid (see section 4), but its framing is bottom-heavy. Only about 28 px of grade shows below the plinth (plinth bottom at y≈1052), while about 23% of the frame above the chimney pots is empty sky. Separately, the east and west faces of the rear wings are plain brick with no openings, in both side views. That is coherent but bare. | right_side column at x=700: plinth (L≈85) ends at y≈1052, then path to y=1080 (`rs_bottom_left.png`, `rs_bottom_right.png`, `rs_wing.png`) | Target height and grade margin were not balanced. | Lower the target by about 1 m, or tilt the camera down slightly, for a larger grade margin. Optionally add one window per floor on each wing return. |

No P0 findings. Checks that came back negative:

- **Dark-cluster scan.** I scanned every render for connected L < 22 clusters. Apart from #1 and #2, each one is one of the following:
  - black downpipes and hoppers, which are continuous eave-to-plinth members (for example architecture_close x 1188–1237, porch_columns x 1318–1381, right_side x≈287 and x≈1040, west_front x 1323–1330);
  - railing bars;
  - dark-green foliage undersides, which have a green hue (for example front x 410–439, y 704–729; garden_fence x 680–729, y 596–629);
  - the cone-tree tips in `top`;
  - the transom interior (#6);
  - the neighbour's own downpipe head at aerial x 1092–1094, y 604–610 (`aerial_dark.png`).
- **Top view.** No dark stripes from open joints between volumes.
- **Roofs.** Hips, valleys, the wing hips and the deck edge close cleanly in `top`, `roof_deck`, `rear_wings` and `rear_side`. The grey band behind the deck in `roof_deck` (x 930–1040, y 470–530) is the north slope seen at a grazing angle (L≈115–125). It is not a void.
- **Relocated trees.** None of the relocated trees intersects the house or the neighbour:
  - The new tree south-east of the east front has its crown just clear of the SE roof corner in `top` (`top_SEtree.png`), and its crown top sits below the eave in `aerial` (`aerial_SEtree.png`).
  - The court tree and the narrowed street tree sit clear of every roof.
- **Tree trunks.** In `garden_fence` the trunk is a single, clean cylinder (`gf_trunk.png`). The v001 #12 step is not reproduced at review scale.

## 3. Source conformance checklist

| item | status | view(s) used |
|---|---|---|
| Silhouette: free-standing two-storey hipped block, deck, four stacks, pedimented pavilion, portico | conforms | front vs source front; front_corner and aerial vs source oblique |
| Storey count (2) | conforms | front, left_side, right_side, rear |
| Plan: main block (nearly square, about 1.4:1 including the pavilion) | conforms | top vs source top |
| Plan: pavilion projection (slight) | conforms | top, rear_side, front |
| Plan: rear wings and recessed court | conforms (wings inset from the side walls, court between them) | top, rear, rear_wings |
| Plan: portico | conforms (slightly wide, as in v001) | top, front |
| Brick coursing | conforms | glass_close, west_front, right_side |
| Window grid: seven bays on the south front (2+3+2) | conforms | front, front_corner |
| Window grid: four bays per side | conforms. West: left_side, west_front. East: now verified in right_side, four bays on both floors | left_side, right_side |
| Sashes and glazing bars (three panes wide) | conforms | glass_close, west_front, interior |
| Lintels (shouldered, raised centre) and sills | conforms (hairline creases, P2 #2) | glass_close, west_front, porch_columns |
| Stone plinth | conforms | right_side, left_side, rear |
| Stone first-floor string course | conforms | glass_close, right_side, left_side |
| White eave cornice and modillions | conforms (coarse from high cameras, P2 #8) | west_front, right_side, cornice_chimneys |
| Pavilion: four giant pilasters | conforms | facade_close, architecture_close |
| Pavilion: capitals | conforms (block capitals; corner blocks now closed) | facade_close (`facade_pedcornerL.png`, `facade_pedcornerR.png`) |
| Pavilion: entablature | conforms | facade_close, architecture_close |
| Pavilion: brick pediment with stone rakes | conforms (small eave-end wedge, P2 #7) | architecture_close |
| Pavilion: oval cartouche | conforms | architecture_close, front |
| Pavilion: slate gable running back into the hip | deviates (ridge too deep, P2 #4) | top, roof_deck |
| Portico: stone platform | conforms | front, aerial |
| Portico: steps | conforms | front, aerial |
| Portico: four Tuscan columns | conforms | porch_columns, facade_close |
| Portico: entablature | **deviates: black end slot (P1 #1)**; also heavy (P2 #11) | garden_fence, front_corner, front |
| Portico: low hipped standing-seam roof | conforms | architecture_close, aerial, top |
| Front door (panelled) and fanlight | door conforms, and the v001 jamb/head slits are closed; fanlight deviates (rectangular transom, P2 #6) | facade_close, porch_columns |
| Roof: hips | conforms | top, cornice_chimneys, right_side |
| Roof: slate courses | deviates (coarse, P2 #5) | cornice_chimneys |
| Roof: flat lead deck | conforms | roof_deck, top |
| Roof: four corner chimney stacks with clay pots | conforms | roof_deck, top, front |
| Roof: rear wings hipped into the main roof | conforms | top, rear_wings, rear_side |
| Dark downpipes | conforms on the south, west and east fronts; the north front has none (P2 #9) | front, west_front, right_side |
| Box-hedge parterres (west and north) | conforms | top, left_side, rear |
| Brick paths | conforms | top, rear_side, garden_fence |
| Lawns and hedges (low hedges before the front) | conforms in substance (open lawns, low curb, low box edging, no railing); the hedge is on the wrong edge of the lawn (P2 #3) | top, front, garden_fence |
| Tall iron railing (street frontage of the west garden, and the west side) | conforms. It now ends with an end post at the west brick path, matching source top (x≈280/1195) and source front (x≈450) | top, front, garden_fence, left_side |
| Trees (cones at SW, dark tree by the west front, NW, NE and court trees, two street trees) | conforms | top, front, left_side, garden_fence |
| Grey stone Georgian neighbour with gabled slate roof and dormers to the east | massing and dormers conform; palette and gable parapets deviate (P2 #10) | top, aerial, front_corner, rear |
| Streets and sidewalks (south and west) | conforms | top, aerial, front, left_side |
| Materials hierarchy (red brick, pale stone, blue-grey roof, pale deck, dark iron, green landscape) | conforms (brick slightly pink in lit views, P2 #11) | all |

## 4. Camera validity

- **right_side: VALID (v001 P1 #1 fixed).** The camera is now a near-level east elevation. It shows the whole east front: grade, plinth, both floors with four bays each, the string course, the modillion cornice, the hipped roof, and both east chimney stacks with their pots. It also shows the full return of the north-east rear wing (x≈1065–1170) and the SE corner and portico edge (x≈240–370), with neutral margin left, right and top.
  - **Cut-away.** The near-clip cut-away removes only the context neighbour. It is a legitimate whole-side elevation proof: the target building is complete and unclipped, and no cut slab, hedge or wall edge appears anywhere in frame. I checked the bottom edge at 2x (`rs_bottom_left.png`, `rs_bottom_right.png`). The ground, the side path and the hedges continue cleanly to the frame edge.
  - **Context.** The neighbour's relation to the house is still proven in `top`, `aerial`, `front_corner`, `rear` and `rear_side`.
  - **Remaining notes.** The grade margin below the plinth is thin (about 28 px), and a context tree crown is cropped at the top-left frame edge. Both are P2 #13 only.
- **front_corner: valid with note (P2 #12).** The west-front base touches the bottom edge, which matches the locked oblique source's crop. `aerial` proves the full envelope.
- **facade_close: valid.** A canopy fragment sits at the top centre; the target is unaffected.
- **Other whole-envelope views: valid.** `front`, `aerial`, `top`, `left_side`, `rear` and `rear_side` show the full asset with neutral margin and a legible target.
- **Detail views: valid.** `architecture_close`, `glass_close`, `porch_columns`, `cornice_chimneys`, `west_front`, `roof_deck`, `rear_wings`, `interior` and `garden_fence` each frame their intended detail.

## 5. Previous findings (v001: P0=0, P1=3)

| v001 finding | status in v002 | evidence |
|---|---|---|
| P1 #1: `right_side` invalid (worm's-eye camera in the 3.5 m gap, clipped, blocked by a tree) | **fixed** | See section 4. The whole east front reads with its four-bay rhythm, plinth to chimney pots and the wing return. The v002 frame differs from v001 by a mean of 49.6 L; the other diffed views differ by 1.5–4.6. |
| P1 #2: black slits at the tops of the door-surround pilasters and under the pediment corner block | **fixed** | The former slit boxes now read as continuous lit stone: facade_close (608–637, 600–612) min L 60 against v001 1, and (803–832, 600–612) min 68 against 1; porch_columns (457–491, 328–350) min 97 against 0, and (706–738, 412–430) min 69 against 0; architecture_close (1118–1132, 625–635) min 161 against 0. The jamb column profiles at x=620 and x=820 stay at L≈100 straight into the head. The pediment corner blocks are solid (`facade_doorhead.png`, `porch_doorhead.png`, `facade_pedcornerL.png`, `facade_pedcornerR.png`, `arch_rakecorner.png`). |
| P1 #3: street railing along the south front; no low curb or hedges at the front lawns | **fixed** | In `top` the railing ends at x≈310, at the west brick path. In `front` it ends at x≈735, before the house's south bays in plan. In `garden_fence` an end post stands at the path, followed by open lawn, a low stone curb and a low box hedge (`gf_end.png`, `top_frontstrip.png`, `front_lawns.png`). The residual hedge-edge placement is P2 #3. |
| P2 #4 pavilion ridge depth | not fixed | P2 #4 |
| P2 #5 slate coursing | not fixed | P2 #5 |
| P2 #6 transom, not fanlight | not fixed | P2 #6 |
| P2 #7 lintel and sill hairlines | not fixed (unchanged; borderline) | P2 #2 |
| P2 #8 rake-to-eave pocket | partly fixed (now a small non-black wedge) | P2 #7 |
| P2 #9 modillions | not fixed | P2 #8 |
| P2 #10 rear door and north downpipes | not fixed | P2 #9 |
| P2 #11 neighbour palette and gables | not fixed | P2 #10 |
| P2 #12 trunk diameter step | not reproduced at review scale | `gf_trunk.png` |
| P2 #13 brick tone, entablature weight, interior colour | not fixed | P2 #11 |
| P2 #14 front_corner bottom touch | not fixed (matches the source crop) | P2 #12 |
| Not recorded in v001: black slot at the portico entablature end | present in v001 and v002 unchanged; not a regression | P1 #1 |

**Regression check.** No new defect appears. The seven other renders I diffed against v001 (front, top, aerial, facade_close, architecture_close, porch_columns, garden_fence) differ by only 1.5–4.6 mean L, which is the targeted changes plus JPEG noise. The dark-cluster counts in unchanged regions match v001: in the same boxes, garden_fence has 98 (v001) against 94 (v002) pixels at L < 22, and porch_columns has 469 against 459. The relocated trees do not intersect any building. The shortened railing leaves no orphan posts or rails.
