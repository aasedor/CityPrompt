# Independent RLASM v6.1 holistic review: Gastown heritage commercial block, clay v003

Reviewer: independent source-locked reviewer. I did not build this model. I opened all three locked sources, all 18
renders and the four phone boards at full resolution with the Read tool, and I judged from the pixels. I also opened
the v002 renders, and I made pixel diffs and side-by-side crops against them to confirm what changed. My zoomed and
annotated crops are in `review/crops_bojfdg/`. In crops named `black_*`, every pixel with max(R,G,B) <= 4 is painted
magenta. Crops named `pair_*` show v002 on the left and v003 on the right. I sampled pixel values with read-only
scripts kept outside the candidate folder. I changed no other file, did not touch git, and rendered nothing.

**Provenance.** `sources/` now holds `front.png`, `oblique.jpg` and `top.jpg`. Their sha256 values match the values
recorded in `source-entry.json` byte for byte: front `ddd3ab09…cf267f0` (the same as the catalogue original
`variant_0.png`), oblique `3b43cbf5…44529` and top `f9db097b…cf42f3`. Phone board 01 shows the locked front.

## 1. Verdict

Verdict: PASS_ZERO_P0_P1

Counts: P0=0 P1=0 P2=11

All three v002 P1s are fixed in the pixels:

- Every recess floor reads as lit stone.
- The north-wall windows sit on the exposed wall west of the north block, and they are seen from grade to coping.
- The locked front source is present and verified.

The five v001 fixes still hold. The diff against v002 is confined to the door recesses, the north wall and the
rear_north camera, and I found no regression. The 11 remaining items are polish only. All of them were already
present in v002.

## 2. Findings

No P0 and no P1. P2 items:

| # | severity | view(s) | finding (what the pixels show) | evidence | likely cause | suggested fix |
|---|---|---|---|---|---|---|
| 1 | P2 | storefronts, front, steam_clock, east_facade, right_side, front_corner | **The glazed side returns of the door recesses still read near-black** (v002 P2 #5, not fixed). I judge this to be shading and unlit display space seen through glass, **not geometry**. The pixels have a soft gradient: luminance 2–9 across the panel, rising toward the open street side. The panels sit inside the frame members. The only exact zeros are 1–4 px seam lines where the panel meets the frame, and small wedges in the top inner corner. Nothing about them reads as a hole: there is no hard-edged zero field and no alternating pattern. | east_facade x 419–451, y 831–1009: row y 900 reads 1.0, 6.6, 7.5, 7.9, 7.8, 6.9, 6.6, 5.9, 5.9, 8.8. front x 982–1008, y 773–806: values 1–8 with a gradient. Crops `black_east_facade_cornershop_x3.png`, `black_steam_clock_cafe_x3.png`, `black_steam_clock_ironGifts_x2.png`, `black_front_groundfloor_x2.png`. | The display zone behind the returns is unlit. | Light the display zone behind the returns, or give them a back panel in the interior colour. |
| 2 | P2 | storefronts, front | **The recess-head soffits read as a near-black band.** This is pre-existing (v002 storefronts row 496 reads 3–8) and was not reported before. Under the transom bar of each recessed door is a band about 12 px tall at close range. It reads luminance 4–10, darker toward the corners. A zero crease 1 px tall runs along the transom rail, and a small zero wedge sits in each inner corner. This is genuine occlusion on a downward-facing surface inside a three-sided recess: it has a gradient and a warm hue (RGB about 10,8,5). It is not an open slot. | storefronts y 491–503, x 110–360. Row y 494: 3, 5, 6, 8, 9, 8, 8, 9, 9, 9, 10, 9, 8, 9, 9, 6. Crop `black_storefronts_headL_x4.png`. | The soffit is lit only by bounce from the sidewalk. | Give the soffit a lighter stone or timber finish, or add a small fill light in the recess. |
| 3 | P2 | architecture_close | At the corner of the cornice soffit, red-brown carrier brick still shows above the corner block (v002 P2 #7, not fixed). | architecture_close about (702–765, 262–285). Crop `arch_soffit_corner_x4.png`. | The frieze top stops short of the soffit at the corner, and there is no corner modillion. | Add a corner modillion or block, or carry the frieze up to the soffit. |
| 4 | P2 | glass_close, facade_close, name_frieze_pediment | The arched top-floor window frame still stops at the springing line, so the fan muntins sit in a bare arch. The arch ring's facets show at close range (v002 P2 #8, not fixed). | glass_close y 0–330: no frame member follows the semicircular head. | The frame is built rectangular, and the fan is added separately. | Run the frame round the head. Add segments to the arch ring. |
| 5 | P2 | front_corner | At the oblique, the frieze still reads "GASTOWN LOMMERLE BUILDIHG" (v002 P2 #9, not fixed). Frontal views read correctly. | Crop `fc_pediment_frieze_x2.png`. | Low-resolution block glyphs for C, N and G. | Refine the C, N and G glyphs. |
| 6 | P2 | top, roof_skylights, front_corner | The small skylight is still a mini pyramid. The sources show a small ridged or hipped glazed box (v002 P2 #10, not fixed). | top (720–785, 410–455) vs source top (590–635, 337–375). | A generic library part. | Model it as a hipped glazed box. |
| 7 | P2 | top | The west lane is still a near-black strip, luminance mean 33, min 15. It is shadowed ground in a narrow canyon, not a gap, because it fades toward the open north end (v001 #6, not fixed). | Crop `top_west_lane_x1.png`. | Unpaved ground plane and low ambient light in the rig. | Pave the lane and raise the top-view fill light. |
| 8 | P2 | aerial, rear_side | The context blocks are featureless boxes, and the subject fills about 25% of the aerial frame (v001 #8, not fixed). | aerial, rear_side frames. | Context massing only. | Add window grids to the context blocks, or tighten the aerial framing. |
| 9 | P2 | front, front_corner | The safety margins are still thin (v001 #13, not fixed). In front, the east lamp is cut at the right edge. In front_corner, the clock base runs off the bottom edge. | Crop `front_right_edge_x3.png`. front_corner rows y 1060–1079 at x 600–700 are clock base and sidewalk. | Framing from nominal extents. | Pull both cameras back about 5%. |
| 10 | P2 | boards/phone-01 | The board still pairs "Locked top" with "Render aerial" rather than with the top render (v001 #12, not fixed). The front panel is now correct. | phone-01, bottom row. | Board layout. | Pair locked top with render top. |
| 11 | P2 | top, roof_skylights | Soft radial shadow arcs still sweep across the roof, which points to a near point or area light (v001 #14, not fixed). | top roof field. | QA lighting rig. | Use a distant sun with sky fill. |

**How I separated defect blacks from shadow and glass.** I scanned every render for connected clusters of pixels
with max(R,G,B) <= 4. Every cluster of 15 px or more falls into one of these groups:

- dim glazed recess returns and transom panes (#1);
- recess-head soffit shading (#2);
- dark joinery or lamp-post edges, 1–4 px wide;
- the inside of the near window frame in the interior view, a dark frame seen from the unlit side.

None of them is a hard-edged zero field set in an otherwise lit plane. None shows the v001-style alternating ladder,
and none is a horizontal surface open to the sky. The v002 recess floors were exactly that kind of surface. Totals of
pixels at max <= 6 fell from v002 to v003: storefronts 16,588 → 5,349, front_corner 2,540 → 735, steam_clock
8,890 → 6,964 and right_side 5,838 → 4,288. (The v002 renders are JPEGs, so I used a tolerance of 6.)

## 3. Source conformance checklist

| item | mark | view(s) used | note |
|---|---|---|---|
| Silhouette and storey count | conforms | front, front_corner, right_side vs source front and oblique | Three storeys with frieze, bracketed cornice and a crested pediment. |
| Plan (top view, near-square, party walls) | conforms | top vs source top | Outer footprint about 840 × 785 px (ratio 1.07; source 1.09). The west wall abuts the cream neighbour in its south half and faces the lane in its north half. The north block starts about 0.20 of the width east of the west face (source 0.19), which leaves the exposed north-wall strip. Chimney, penthouse, small skylight and both pyramids fall within about 0.03 of their source plan positions. |
| Bay rhythm, south (five bays) | conforms | front, front_corner, facade_close | Four single bays, then a wider corner bay with paired windows. The pediment is over bay 3. |
| Bay rhythm, east (corner bay, four narrow bays, paired-arch end bay) | conforms | right_side, east_facade | Wide corner bay; four narrow sash bays on three floors; a pilastered end bay with paired arched windows over paired sashes, and a side door. |
| Rusticated sandstone corner and end piers | conforms | front, right_side, architecture_close, east_facade | South-west, corner and north-east piers are rusticated to full height. The corner-shop jamb liner is lit throughout. |
| Brick pilasters and carved capital panels | conforms | front, facade_close, name_frieze_pediment | Square stone boss panels at the arch springing and at frieze level. The simplified carving is acceptable for clay. |
| Window types per floor | conforms (P2 #4) | front, facade_close, glass_close, right_side | Arched three-light windows on the top floor; three-light windows with small-paned transoms below; paired windows in the corner bays; narrow sashes on the east. |
| Sill and lintel bands | conforms | front, right_side, facade_close | Continuous sill and lintel bands; capped lintels on the east. |
| Lettered frieze | conforms (P2 #5) | name_frieze_pediment, front | Reads "GASTOWN COMMERCE BUILDING" frontally. |
| Modillion cornice and dentils | conforms (P2 #3) | architecture_close, right_side, name_frieze_pediment | Block modillions with dentil pairs, a deep soffit, and returns at both street ends. |
| Pediment (shell, crest, pedestals) | conforms | name_frieze_pediment, front_corner, roof_skylights | Shell and acanthus crest present. The rakes die into both pedestals with a closed sloping back, and there is no wedge or doubled edge. |
| Shopfronts (bulkheads, glass, transoms, recessed doors, signboards, shop cornice) | conforms (P2 #1, #2) | storefronts, steam_clock, front_corner, east_facade, right_side | Panelled bulkheads, plate glass, small-paned transoms, glazed timber double doors, dark fascias with gilt lettering, and a moulded shop cornice. The corner shop wraps onto the east. The recess floors are now lit stone with a proud threshold, and a meeting stile closes the leaves. |
| Roof (parapet coping, chimney, penthouse, skylights) | conforms (P2 #6) | top, roof_skylights, front_corner vs source top and oblique | Brick chimney; clapboard penthouse with door and window; two glazed pyramids and a small skylight; all inside a stone-coped parapet. |
| Steam clock | conforms | front, steam_clock, front_corner, top | Stone and bronze base with plaques, glazed cabinet with works, four-faced head, small roof and whistles. The head is above the shop cornice, and the clock stands about 2 m off the facade. |
| Bollards and chains | conforms | front, steam_clock, top | Chained bollards along the curb by the clock. |
| Globe lamps | conforms | front, right_side, east_facade, top | Five globes on two tiers, on both sidewalks. |
| Paving (brick sidewalks, setts, asphalt) | conforms (P2 #7) | front, top, aerial | Brick sidewalks, grey setts on the south street, and asphalt with a centre line on the east street. |
| Neighbours | conforms with P2 deviations (#7, #8) | front, top, left_side, rear, rear_north | The lower cream west neighbour is correct. The north block runs to the east line and leaves the exposed west strip of the north wall, as in the source top. The context blocks are blank boxes. |
| Materials hierarchy | conforms | all | Red brick body, buff sandstone dressings, dark green joinery, timber doors, bronze and brass clock, and a light roof membrane. Matches the source palette. |
| Opening depth and returns | conforms (P2 #1, #2) | storefronts, glass_close, front_corner, rear, rear_north | Window reveals and occupied depth read correctly. Door recesses have lit floors. The north-wall windows have sills and reveals in clear masonry, and they meet no neighbour mass. |

## 4. Camera validity

- **front**: valid. The full south front and the visible east front are in frame. The east lamp is cut at the right edge (P2 #9).
- **front_corner**: valid matched oblique, with the target legible. The clock base runs off the bottom edge (P2 #9).
- **aerial**: valid. The subject is small, and the context boxes dominate (P2 #8).
- **top**: valid true top. The whole footprint, the roof items and the street edges are in frame.
- **left_side**: valid. The elevated view shows the west party wall from coping to neighbour roofs, plus the parapet and roof. Grade is properly hidden by the adjoining neighbours.
- **right_side**: valid. The full east elevation is in frame, with grade and cornice.
- **rear**: valid. It shows the north party wall from coping to the north-block roof, the roof footprint and the back of the pediment. The new north-wall windows show at the west end, beside the north block.
- **rear_side**: valid but weak. The subject is small and partly screened by the boxes across the street.
- **rear_north**: **valid now.** The camera is level and frames the exposed north wall west of the north block. The stone coping is in frame at the top (y ≈ 80–95), and the wall foot meets the brick ground at y ≈ 995. Four windows (two per floor, second and third storeys) sit in clear brick between the north block's west face (x ≈ 600) and the lane (x ≈ 860). Crops `rear_north_base_x2.png`, `rear_north_top_x2.png`.
- **facade_close, architecture_close, glass_close, steam_clock, storefronts, name_frieze_pediment, east_facade, roof_skylights, interior**: all present, legible and correctly targeted.

No view has an occluded target, a clipped asset that hides the subject, or illegible content.

## 5. Previous findings

### v002 (0 P0 / 3 P1)

| v002 finding | status | pixel evidence |
|---|---|---|
| P1 #1: pure-black recess floors at every recessed door | **fixed** | storefronts recess floors, y 958–981: luminance min 46, mean 70–84 under both door pairs. At v002's zero band (x 110–340 and 660–915, y 961–984), no pixel is <= 4. front_corner, at v002's five floor boxes: mean luminance 73, 71, 72, 54 and 46, 10th percentile 21–48. The only zeros left there (5–15 px per box) are jamb seam lines and transom glass, not the floor. right_side side-door step, (1097–1171, 984–996): luminance min 19, mean 55, stone RGB about (74,60,47). Crops `storefronts_cafe_sill_x3.png`, `black_storefronts_doors.png`, `black_front_corner_shops_x2.png`, `right_side_sidedoor_x4.png`, `pair_v002_v003_right_side_cornershop.png`. |
| P1 #2: north-wall windows buried in the north block | **fixed** | In rear, v002's sliver window heads at x 427–495, y 533–541 are gone: luminance min 76–89, plain brick and north-block roof. Crops `rear_north_wall_east_end_x4.png` and `v002_rear_north_wall_east_end_x4.png`. The windows now sit at the west end of the north wall, beside the north block: rear x 1005–1075. rear_north shows all four in clear brick, with sills, about 1 m from the north block's west face. rear_side also shows them above the north-block roof line (`pair_v002_v003_rear_side_north_windows.png`). That partial view is an occlusion from the camera angle, and rear_north shows the openings are clear. |
| P1 #3: locked front source missing; phone-01 front panel broken | **fixed** | `sources/front.png` is present. Its sha256 `ddd3ab09…cf267f0` matches the recorded hash and the catalogue original. The phone-01 "Locked front" panel shows the source image. |
| P2 #4: rear_north missed grade and coping | fixed | See section 4. |
| P2 #5: dim glazed recess returns | not fixed | Finding #1. |
| P2 #6: light slit between door leaves | fixed | storefronts x 785–797, y 600–940: max luminance 60. The door surface is continuous (about 53–58) with no bright slit, so a meeting stile is present. |
| P2 #7: soffit corner brick patch | not fixed | Finding #3. |
| P2 #8: arch-head frame and facets | not fixed | Finding #4. |
| P2 #9: frieze glyphs at the oblique | not fixed | Finding #5. |
| P2 #10: small skylight is a pyramid | not fixed | Finding #6. |
| P2 #11: lane, context boxes, margins, board pairing | not fixed | Findings #7–#10. |
| P2 #12: roof shadow arcs | not fixed | Finding #11. |

### v001 (0 P0 / 5 P1): do the fixes still hold?

| v001 finding | status | pixel evidence |
|---|---|---|
| P1 #1: pure-black slot ladder in the east corner-shop jamb | **still fixed** | east_facade jamb x 398–416, y 790–1010: minimum max-channel 9, mean RGB (54,43,32), and no row contains a zero pixel. In right_side, the jamb region is pixel-identical to v002 apart from the floor fix (`pair_v002_v003_right_side_cornershop.png`). |
| P1 #2: pediment rake overshoot, wedge and doubled edge | **still fixed** | name_frieze_pediment, front_corner and roof_skylights are unchanged from v002 (diff: 0 px above 25 in name_frieze_pediment and roof_skylights). The rakes die into the pedestals with a closed back. Crop `fc_pediment_frieze_x2.png`. |
| P1 #3: steam clock undersized, too low and too close | **still fixed** | The clock geometry is unchanged; the front and steam_clock diffs touch only the door recesses. The head sits above the shop cornice, and in top the clock stands about 2 m off the facade at 0.85 of the block width (source 0.84). |
| P1 #4: missing facade_close, architecture_close, glass_close | **still fixed** | All three are present at 1440 × 1080 and correctly targeted. |
| P1 #5: left_side and rear blocked by neighbours | **still fixed** | Both cameras are elevated and valid (section 4). |

**Regression check.** I diffed each v003 render against its v002 counterpart, counting pixels whose luminance
differs by more than 25. All 18 views were checked. The changed pixels fall in three places only:

- the door-recess floors and thresholds (storefronts, front, front_corner, steam_clock, east_facade, right_side, facade_close and aerial);
- the north-wall windows (rear, rear_side, and a two-pixel row of sill in top);
- the re-aimed rear_north camera.

Six views have zero changed pixels: architecture_close, glass_close, interior, left_side, name_frieze_pediment and roof_skylights.
One small cluster in right_side (x 1240, y 320) is a JPEG highlight artefact in v002, not a v003 change. I found no
regression.
