# Independent RLASM v6.1 holistic review: Halifax Georgian colonial house, clay v003

Reviewer: independent source-locked architectural-clay reviewer. I did not build this candidate.

I examined these inputs at full resolution with direct image reads: `sources/front.png`, `sources/oblique.jpg` and `sources/top.jpg`; all 18 renders in `renders/` (1440 x 1080 PNG); and the four phone boards in `boards/`. For the comparison with v002 I used the v002 renders in `tools/clay_halifax_georgian_colonial/evidence/v002/renders/`. Zoomed crops supporting the evidence below are in `review/crops_qhvzmt/` (files prefixed `v2_` are the same box cut from the v002 render). All pixel coordinates refer to the 1440 x 1080 renders. L is the 0–255 luminance of a pixel (0.299 R + 0.587 G + 0.114 B).

## 1. Verdict

Verdict: PASS_ZERO_P0_P1

Counts: P0=0 P1=0 P2=12

The v002 P1 (black slot at the west end of the portico entablature) is closed at both ends, the borderline lintel and sill creases are gone, the street-edge hedge has moved to the house base, and every v001 and v002 fix still holds; nothing at review scale is left that blocks production-quality approval, so in the brief's vocabulary this is PASS_ZERO_P0_P1.

## 2. Findings table

No P0 or P1 findings. The P2 polish list follows; #1 and #12 are newly recorded, and the rest are carried unchanged from v002.

| id | severity | view(s) | finding (what the pixels show) | evidence | likely cause | suggested fix |
|---|---|---|---|---|---|---|
| 1 | P2 | front_corner | A 1 px dark diagonal hairline, about 30 px long, sits under the portico entablature between the west column and the second column. It runs where the shaded brick of the pavilion face meets the lit stone surface below it (the portico platform). It is **not new**: the same line is in v002 (16 px at L < 22 there, 14 px in v003). It was not recorded in v002, because that review's front_corner box (x 891–893) was the entablature-end slot a few pixels to the left. | front_corner x 965–990, y 823–843: one pixel wide, minimum L 11, with no pixel at 0. Row y=829 reads 94, 84, **11**, 113, 148, so it is a single-pixel crease between shaded brick (L≈80) and lit stone (L≈150), not a slot with width. Crops: `fc_porch_line.png` (v003) and `v2_fc_porch_line.png` (v002), with context in `fc_porch_ctx.png`. The same junction in `aerial` (`aerial_portico.png`, box x 440–640, y 600–800) bottoms out at L 44, with nothing below 22. I graded it P2 for the same reasons the v002 review graded hairline creases P2: it is one pixel wide, its core is not black, it shows only from this one grazing high angle, and at review scale it reads as a shadow edge under the portico. | The portico platform's back edge (YP + 5 cm) and the pavilion's brick face do not overlap, so this camera sees a hairline into the joint. | Run the platform 5 cm or more under the pavilion face, or add a stone plinth return along that junction inside the portico. Rerender `front_corner`. |
| 2 | P2 | top, roof_deck | The pavilion gable ridge still runs back nearly to the deck edge (v002 #4, unchanged). | top: the apex is at y≈655, against the deck front at ≈640. | Same as v002. | Lower the ridge so it dies into the hip about two-thirds of the way up the slope. |
| 3 | P2 | cornice_chimneys, front_corner, aerial | The slate coursing is still coarse, at about 10 lines per slope (v002 #5, unchanged). | cornice_chimneys, main slopes | Same as v002. | Halve the course spacing. |
| 4 | P2 | facade_close, porch_columns | The door still has a rectangular four-light transom rather than a fanlight. Its panes read dark brown (RGB ≈ 26/18/15) because the hall behind is unlit. The bars and the reveal have depth, so this is an interior, not a void (v002 #6, unchanged). | facade_close x 652–787, y 634–649 (`facade_jamb.png`); porch_columns x 640–659, y 438–484 (`porch_doorhead.png`) | Same as v002. | Use an elliptical or segmental fanlight, and light the hall. |
| 5 | P2 | architecture_close | A small blue-grey wedge of roof shows where the main eave stops against the pediment corner block. It is not black (v002 #7, unchanged). | x≈1200–1206, y≈596–606 | The eave run has no end cap. | Add an end return on the eave run. |
| 6 | P2 | front_corner, aerial, cornice_chimneys | The modillions read as a coarse toothed band from high cameras (v002 #8, unchanged). | front_corner eaves | Same as v002. | Use a deeper corona and smaller, closer modillions. |
| 7 | P2 | rear, rear_wings | The rear door is a plain slab, and the north front has no downpipes (v002 #9, unchanged). No source shows this face, so it is judged for coherence only. | rear x≈695–745, y≈680–785 | Same as v002. | Add a simple surround and transom, and downpipes at the wing re-entrant corners. |
| 8 | P2 | aerial, front_corner, rear, rear_side | The east neighbour is a beige rendered box with plain gables. The source shows grey coursed stone with stepped gable parapets (v002 #10, unchanged; context only). | aerial x 900–1440 | Same as v002. | Use a grey stone value and stepped parapets. |
| 9 | P2 | rear, rear_wings, interior, facade_close | The brick reads salmon in the lit north views, the portico entablature is heavy for its columns, and the interior walls use the exterior brick colour (v002 #11, unchanged). | rear, rear_wings, interior | Same as v002. | Darken the brick slightly, slim the entablature, and use a plaster colour inside. |
| 10 | P2 | front_corner, facade_close | In `front_corner` the base of the west front touches the bottom frame edge, which matches the crop of the locked oblique source. In `facade_close` a canopy fragment intrudes at the top centre (x≈510–740, y 0–45). Both are unchanged from v002 #12. | front_corner y=1080 across x≈560–660; facade_close top edge | Same as v002. | Optional: pull `front_corner` back about 5%, and move the canopy or the camera for `facade_close`. |
| 11 | P2 | right_side, left_side | The `right_side` framing is bottom-heavy: only about 28 px of grade shows below the plinth, while the sky above is wide. The wing returns are blind brick in both side views (v002 #13, unchanged). | right_side, column at x=700 | Same as v002. | Lower the target by about 1 m, and optionally add one window per floor on each wing return. |
| 12 | P2 | top | The new foundation hedge against the south plinth is hidden under the eave overhang in plan. The lawn appears to run right up to the eave line. In the source top view the low hedge reads as a distinct band just beyond the eave (source y≈668–680, against the eave at ≈662). Elevations and obliques show it correctly. | `top_frontstrip.png` (v003) against `v2_top_frontstrip.png`; render top, eave edge at y≈800 with lawn directly below it; front, front_corner and garden_fence show the hedge on the plinth line (`front_lawns.png`, `fc_base.png`, `gf_frontlawn.png`) | The hedge is narrower than the eave projection. | Optional: widen the foundation hedge by about 0.3 m so it shows past the eave in plan. |

Checks that came back negative:

- **Re-scan for dark clusters.** I scanned all 18 renders for connected clusters of 8 or more pixels at L < 22. Apart from #1, every cluster is one of the following, and none is a geometry void:
  - **Black iron downpipes and hopper heads.** These are continuous members that run from eave to plinth, with a lit highlight edge (`aerial_se.png`, `rearside_mid.png`, `roofdeck_br.png`). Examples: aerial x 1076–1082, y 477–503; architecture_close x 1188–1237; porch_columns x 1317–1381 and x 1259–1274, y 274–280; right_side x≈287 and x≈1040; west_front x 1323–1330; glass_close x 1305–1312; rear_side x 1181–1193 and x 903–907, y 587–602; roof_deck x 1384–1439, y 932–1079, which is the SE downpipe with the shaded east wall below the eave. All of these match v002 within ±6 px.
  - **Railing bars.**
  - **Dark green foliage undersides.** These have a green hue (RGB ≈ 10/21/6): front x 410–439; garden_fence x 680–729; left_side x 895–964; top x 338–349; west_front x 987–1082.
  - **Window interiors seen through glass.** These are neutral or brown, behind lit glazing bars: garden_fence x 945–979, y 101–110 and x 945–953, y 203–205; the east neighbour's dark window panes at rear x 153–212.
  - **The transom interior** (#4).
  - **Single-pixel creases between the door leaf and its reveal.** In facade_close (x 627–637 and x 803–814, 1 px wide, RGB ≈ 32/13/4) these are dark brown, the colour of the door and brick in shade. They are bounded by the door leaf and the jamb, so they are contact creases of a door set in a reveal, not slots. They are unchanged from v002.
  - **The deep shadow between the west-front tree crown and the wall** (front x 546–550, y 548–554, RGB ≈ 30/19/11; `front_546.png`).
  - **The neighbour's own downpipe head** at aerial x 1092–1094, y 604–610.
- **Regression diff against v002.** Every view differs by only 0.56–1.28 mean L. The changed pixels are confined to the portico ends, lintels, sills and the front-lawn strip. No new defect appears anywhere else.
- **Lintel and sill fix by-product.** Lifting the lintel soffit 1.5 cm leaves a hairline brick course between the lintel and the frame head in the closest views (`porch_lintel.png`). It reads as brick, not as a void, and is not visible at whole-envelope scale. I did not record it as a finding.

## 3. Source conformance checklist

| item | status | view(s) used |
|---|---|---|
| Silhouette: free-standing two-storey hipped block, deck, four stacks, pedimented pavilion, portico | conforms | front vs source front; front_corner and aerial vs source oblique |
| Storey count (2) | conforms | front, left_side, right_side, rear |
| Plan: main block (nearly square) | conforms | top vs source top |
| Plan: pavilion projection (slight) | conforms | top, rear_side, front |
| Plan: rear wings and recessed court | conforms | top, rear, rear_wings |
| Plan: portico | conforms (slightly wide, as in v002) | top, front |
| Brick coursing | conforms | glass_close, west_front, right_side |
| Window grid: seven bays on the south front (2+3+2) | conforms | front, front_corner |
| Window grid: four bays per side | conforms (west: left_side, west_front; east: right_side) | left_side, right_side |
| Sashes and glazing bars (three panes wide) | conforms | glass_close, west_front, interior |
| Lintels (shouldered, raised centre) and sills | conforms. The v002 creases are gone: porch_columns min L 30, facade_close heads min 39, architecture_close sill min 73 | glass_close, porch_columns, facade_close, architecture_close |
| Stone plinth | conforms (hidden behind the foundation hedge on the south front, as in the source) | right_side, left_side, rear, fc_base |
| Stone first-floor string course | conforms | glass_close, right_side, left_side |
| White eave cornice and modillions | conforms (coarse from high cameras, P2 #6) | west_front, right_side, cornice_chimneys |
| Pavilion: four giant pilasters | conforms | facade_close, architecture_close |
| Pavilion: capitals | conforms (block capitals; corner blocks closed) | facade_close |
| Pavilion: entablature | conforms | facade_close, architecture_close |
| Pavilion: brick pediment with stone rakes | conforms (small non-black eave-end wedge, P2 #5) | architecture_close |
| Pavilion: oval cartouche | conforms | architecture_close, front |
| Pavilion: slate gable running back into the hip | deviates (ridge too deep, P2 #2) | top, roof_deck |
| Portico: stone platform | conforms (hairline at the back junction, P2 #1) | front, aerial, front_corner |
| Portico: steps | conforms | front, aerial |
| Portico: four Tuscan columns | conforms | porch_columns, facade_close |
| Portico: entablature | conforms. The end slots are closed at both ends; heavy proportion only (P2 #9) | garden_fence, front_corner, front, porch_columns |
| Portico: low hipped standing-seam roof | conforms | architecture_close, aerial, top |
| Front door (panelled) and fanlight | door conforms; fanlight deviates (rectangular transom, P2 #4) | facade_close, porch_columns |
| Roof: hips | conforms | top, cornice_chimneys, right_side |
| Roof: slate courses | deviates (coarse, P2 #3) | cornice_chimneys |
| Roof: flat lead deck | conforms | roof_deck, top |
| Roof: four corner chimney stacks with clay pots | conforms | roof_deck, top, front |
| Roof: rear wings hipped into the main roof | conforms | top, rear_wings, rear_side |
| Downpipes (dark) | conforms on the south, west and east fronts; none on the north front (P2 #7) | front, west_front, right_side |
| Box-hedge parterres (west and north) | conforms | top, left_side, rear |
| Brick paths | conforms | top, rear_side, garden_fence |
| Lawns and hedges (low hedges before the front) | conforms. The street-edge hedge is gone, and a low box hedge now runs along the plinth on both sides of the portico, with open lawn and a low stone curb before it. It is hidden under the eave in plan (P2 #12) | front, front_corner, garden_fence, top |
| Tall iron railing (street frontage of the west garden, and the west side) | conforms. It ends with an end post at the west brick path | top, front, garden_fence, left_side |
| Trees (cones at SW, dark tree by the west front, NW, NE and court trees, two street trees) | conforms | top, front, left_side, garden_fence |
| Grey stone Georgian neighbour with gabled slate roof and dormers to the east | massing and dormers conform; palette and gable parapets deviate (P2 #8) | top, aerial, front_corner, rear |
| Streets and sidewalks (south and west) | conforms | top, aerial, front, left_side |
| Materials hierarchy (red brick, pale stone, blue-grey roof, pale deck, dark iron, green landscape) | conforms (brick slightly salmon in lit north views, P2 #9) | all |

## 4. Camera validity

- **right_side: valid.** The near-level east elevation shows plinth to chimney pots, four bays on both floors, the string course, the modillion cornice, both east stacks and the north-east wing return. The near-clip cut-away removes only the context neighbour, and no cut edge appears in frame. Framing is bottom-heavy (P2 #11). The render matches v002 (mean diff 0.75 L).
- **front_corner: valid with note.** The west-front base touches the bottom edge, which matches the locked oblique's crop (P2 #10). `aerial` proves the full envelope.
- **facade_close: valid.** A canopy fragment sits at the top centre; the target is unaffected (P2 #10).
- **Other whole-envelope views: valid.** `front`, `aerial`, `top`, `left_side`, `rear` and `rear_side` show the whole asset with neutral margin and a legible target.
- **Detail views: valid.** `architecture_close`, `glass_close`, `porch_columns`, `cornice_chimneys`, `west_front`, `roof_deck`, `rear_wings`, `interior` and `garden_fence` each frame their intended detail.
- No view has an occluded, clipped or illegible target.

## 5. Previous findings

### v002 (P0=0, P1=1, P2=12)

| v002 finding | status in v003 | evidence |
|---|---|---|
| P1 #1: pure-black slot where the west end of the portico entablature meets the brick front (garden_fence, front_corner, front) | **fixed** | **garden_fence** x 1330–1370, y 320–380: v003 minimum L 52 with 0 px below 22, against v002 minimum 1 with 94 px. The only dark pixels in the wider box x 1300–1440, y 280–400 (3 px, minimum 19) belong to the downpipe. **front_corner** x 880–905, y 780–815: minimum 94, against 18. **front** x 845–865, y 545–585: minimum 56, against 11. **East end**: front x 1060–1090, y 540–590, minimum 69; porch_columns x 1150–1300, y 280–520 has only the 3 downpipe pixels, the same as v002. The junction now shows lit brick, then a soft cornice shadow, then the lit stone return (`gf_portico_west.png` against `v2_gf_portico_west.png`; `fc_portico.png`; `front_portico.png`). |
| P2 #2: 1–2 px black creases under lintels and along sills | **fixed** | porch_columns x 0–237, y 220–295: minimum 30 with 0 px below 22, against v002 minimum 1 with 462 px (`porch_lintel.png`). facade_close upper heads, the full-width strip at y 285–300: minimum 39 with 0 px, against 12 with 219 (`facade_heads.png`). architecture_close sill x 922–963, y 998–1029: minimum 73 with 0 px, against 2 with 53 (`arch_sill.png`). |
| P2 #3: hedge on the curb line, not against the house | **fixed** (residual plan visibility, P2 #12) | `front_lawns.png` against `v2_front_lawns.png`: the street-edge hedge is gone. `fc_base.png` and `gf_frontlawn.png` show the hedge on the plinth line, with open lawn and a low stone curb before it. |
| P2 #4 pavilion ridge depth | not fixed | P2 #2 |
| P2 #5 slate coursing | not fixed | P2 #3 |
| P2 #6 transom, not a fanlight | not fixed | P2 #4 |
| P2 #7 eave-end wedge | not fixed (unchanged, not black) | P2 #5 |
| P2 #8 modillions | not fixed | P2 #6 |
| P2 #9 rear door and north downpipes | not fixed | P2 #7 |
| P2 #10 neighbour palette and gables | not fixed | P2 #8 |
| P2 #11 brick tone, entablature weight, interior colour | not fixed | P2 #9 |
| P2 #12 front_corner bottom touch and facade_close canopy | not fixed (matches the source crop) | P2 #10 |
| P2 #13 right_side framing and blind wing returns | not fixed | P2 #11 |
| Not recorded in v002: hairline at the junction of the portico platform and the pavilion face in front_corner | present in v002 and v003 at the same strength (16 px and 14 px at L < 22); not a regression | P2 #1 |

### v001 (P0=0, P1=3): all fixes still hold

| v001 P1 | status in v003 | evidence |
|---|---|---|
| #1: `right_side` invalid (worm's-eye camera in the gap, clipped, tree-blocked) | **fixed, holds** | See section 4. The render matches v002 (mean diff 0.75 L), with the whole east front, four bays per floor, and the wing return. |
| #2: black slits at the tops of the door-surround pilasters and under the pediment corner block | **fixed, holds** | The same boxes as the v002 review, v003 against v002: facade_close (608–637, 600–612) minimum 61 against 63; (803–832, 600–612) minimum 42 against 40; porch_columns (457–491, 328–350) minimum 97 against 97; (706–738, 412–430) minimum 63 against 59; architecture_close (1118–1132, 625–635) minimum 161 against 161. None has a pixel below 22. |
| #3: street railing along the south front; no low curb or hedges at the front lawns | **fixed, holds** | The railing still ends with an end post at the west brick path: top x≈310, front x≈735, garden_fence end post (`gf_frontlawn.png`). The front lawns carry a low stone curb and, now, a foundation hedge on the plinth line. |

**Regression check.** Every one of the 18 views differs from v002 by only 0.56–1.28 mean L, and the changes are confined to the targeted members. Dark-cluster counts in unchanged regions match v002 (for example: aerial SE hopper 63 against 64 px; roof_deck SE corner 832 against 838; rear_side hopper 58 against 53). No earlier fix has regressed.
