# Independent RLASM v6.1 holistic review: Gastown heritage commercial block, clay v002

Reviewer: independent source-locked reviewer. I did not build this model. I opened every source, all 18 renders and
the four phone boards at full resolution with the Read tool, and I judged from the pixels. Zoomed and annotated crops
are in `review/crops_zgoqoa/`. Crops named `black_*` paint every pixel with max(R,G,B) <= 4 magenta. I sampled pixel
values with read-only scripts. I read the builder scripts only to name likely causes, never as proof. I changed no
other file, did not touch git, and rendered nothing.

**Source note.** `sources/front.png` is **missing** from the candidate. The `sources/` folder holds only `oblique.jpg`
and `top.jpg`. For the front comparison I used the catalogue original that `source-entry.json` records,
`frontend/public/archetypes/buildings/gastown-heritage-commercial/variant_0.png`. Its sha256 (`ddd3ab09…cf42f3`)
matches the recorded hash byte for byte, so it is the locked front. The missing file and the broken board it causes
are finding 3.

## 1. Verdict

Verdict: FAIL

Counts: P0=0 P1=3 P2=12

All five v001 P1s are fixed in the pixels, and identity, storeys, plan, bay rhythm and the roof still match the
sources. But the candidate keeps lifecycle state `visual_rework_required` (VISUAL_REWORK_REQUIRED), for three reasons:

- Every recessed door has a pure-black recess floor. This defect was already in v001 but was not reported then.
- The v002 north-block extension now buries the north-wall windows.
- The locked front source is missing from the package and from phone board 01.

## 2. Findings

| # | severity | view(s) | finding (what the pixels show) | evidence | suggested fix |
|---|---|---|---|---|---|
| 1 | P1 | storefronts, front_corner, steam_clock, right_side, east_facade, front, aerial | **Pure-black recess floors at every recessed door.** Under each pair of shop doors, and under the east end-bay side door, a hard-edged black band runs the full door width. From the elevated front_corner the floors read as solid black parallelograms in five shop entrances. The defect is **pre-existing**: v001 `storefronts.jpg` has the same band at y 960–982 (luminance 0–2). It is not a v002 regression, but it was missed in the v001 review. | storefronts: x 110–340 and 660–915, y 961–984 = RGB (0,0,0)–(1,1,1), with one faint edge line at y 976 (luminance 5–15). The sidewalk 1 cm below reads 52–56, and the stone jamb liners in the same recess read 30–65. front_corner floors: (265–293, 743–767), (388–410, 817–837), (463–497, 863–887), (725–760, 1020–1050), (830–857, 1017–1047). right_side side door: (1097–1171, 986–993). Crops `shop_door_sills.png`, `black_front_corner_200_620.png`, `black_front_corner_680_880.png`, `black_right_side_1040_900.png`, `black_steam_clock_40_600.png`. **Why this is not contact shadow or glass:** it is a horizontal surface open to the sky and street (front_corner looks down onto it). It is uniform zero, with no falloff from the open street edge towards the door. Shaded stone in the same recess keeps its hue (30–65). No glass is in front of it. Likely cause: the stone threshold's top (z = G0 = 0.15 m) is coplanar with the floor of the wall cut, which also starts at G0. The cut floor is missing or inverted, or the threshold is enclosed, so the surface renders unlit. | Give every door cut, shop and side door alike, one closed and correctly oriented floor. Raise the threshold 5–10 mm above the cut floor and the sidewalk, and check its normals. Re-render storefronts, front_corner, steam_clock and right_side, and confirm that no recess-floor pixel is at zero luminance. |
| 2 | P1 | rear (and rear_north by omission) | **North-wall windows buried in the north block. This is a regression caused by the v002 north-block extension.** In rear, two dark window heads stick up as slivers just above the north block's roof, at the east end of the subject's north wall. The rest of each opening is inside the neighbour's mass, so the lower windows are buried completely. rear_north is aimed at the exposed gap west of the north block, and it shows a blank wall there. These are openings that intersect an adjoining building. | rear x 427–455 and 467–495, y 536–539: luminance 13–30 inside brick at about 85, sitting on the neighbour roof line at y 540. Crop `rear_north_wall_band.png`. Likely cause, from the scripts: the north face's tangent is (−1,0,0). The holes at u = −11.8 and −10.4 therefore land at world x = +11.8 and +10.4 (the east end, inside the north block, which spans x −8.1 to 12.95 and is 13.4 m tall). They were meant for x = −10.4 and −11.8, where rear_north is aimed. The top-floor heads (z 11.2–13.6 m) clear the 13.4 m roof by 0.2 m. | Move the north-wall windows to world x −10.4 and −11.8 (in the exposed gap), or remove them. Re-render rear and rear_north and check that no opening meets a neighbour mass. |
| 3 | P1 | boards/phone-01, sources/ | **The locked front source is missing, and the source-vs-render board is broken.** This is a regression from v001. The "Locked front" panel of phone-01 is empty: a dark box with red missing-file text ("…nt.png"). `sources/` has no front.png. The compact v002 package lists only oblique.jpg and top.jpg under sources/. v001's board and package both carried the front source. The governing front comparison therefore cannot be made from the candidate's own evidence. | phone-01, top-left panel. Listing of `sources/` (oblique.jpg, top.jpg). `source-entry.json` still records `sources/front.png`, sha256 ddd3ab09…, 1,472,172 bytes. Not P0: the hash-locked original exists at the catalogue path, I verified it byte-exact, and I reviewed against it. | Restore `sources/front.png` byte-exact from the recorded original path, re-verify its sha256, rebuild phone-01, and include it in the package. |
| 4 | P2 | rear_north | The camera does not show what it claims ("the exposed north wall to grade"). The frame centre is on the exposed north wall, but grade falls below the frame bottom and the coping falls above the frame top. What remains is a featureless 4.9 m slice of brick. The view is legible, but it proves no contact. | rear_north (720,540) is on the wall. The wall runs off both frame edges, x 540–920. Crop `rear_north_base.png`. | Pull back or lower the camera so that both the wall foot on the north sidewalk strip and the coping are in frame. |
| 5 | P2 | front, east_facade, steam_clock, storefronts | The glazed side returns of the door recesses read near-black. This is **unlit display space seen through glass, not geometry**: the darkness has a soft gradient (luminance 5–20, falling to 0 only in the far corner), it sits inside frame members, and it has a glass plane in front of it. Next to the bright shop windows it still reads as a void. | front x 832–848 and 987–1008, y 775–930. east_facade x 418–445, y 830–1010. Crops `black_front_760_700.png`, `black_east_facade_360_720.png`. | Light the display zone behind the returns, or give the returns a back panel in the interior colour. |
| 6 | P2 | storefronts | A bright vertical slit shows between the leaves of the double doors, which leave a gap of about 3 cm. | storefronts x 789–791, y 605–700. Crop `shop_door_slit.png`. | Close the meeting gap, or add a meeting stile. |
| 7 | P2 | architecture_close | At the corner of the cornice soffit, above the corner capital, a red-brown brick patch shows. The carrier is visible where the frieze top does not reach the soffit, and there is no corner modillion. | architecture_close (702–765, 262–280). Crop `arch_soffit_corner.png`. | Add a corner modillion or block, or carry the frieze up to the soffit at the corner. |
| 8 | P2 | glass_close, facade_close, name_frieze_pediment | The arched top-floor window frame still stops at the springing line, and the fan muntins sit in a bare arch (v001 #10 not fixed). The arch ring's facets show at close range. | glass_close y 0–330: no frame around the head. Facets visible at (180–300, 0–300) and (1060–1260, 0–300). | Run the frame round the head. Add segments to the arch ring. |
| 9 | P2 | front_corner | At the oblique angle the frieze still reads "GASTOWN LOMMERLE BUILDIN…" (v001 #11 not fixed). Frontal views read correctly. | front_corner (300–500, 380–470). Crop `fc_pediment.png`. | Refine the C, N and G glyphs. |
| 10 | P2 | top, roof_skylights, front_corner | The small skylight is still a mini pyramid. The sources show a small ridged or hipped glazed box (v001 #9, skylight part). The lamp heads now read as 5 globes on two tiers and match. | top (720–785, 410–455) vs source top (590–635, 337–375). | Model the small skylight as a hipped glazed box. |
| 11 | P2 | top, aerial, rear_side, front, front_corner, boards | Context and framing items carried over unchanged: the west lane is still a near-black strip in top (v001 #6); context blocks are blank boxes and the subject is small in aerial and rear_side (v001 #8); safety margins are thin (front: east lamp cut at the right edge; front_corner: clock base about 3 px from the bottom, v001 #13); phone-01 pairs locked top with render aerial (v001 #12). | top x 220–300, y 0–575. aerial: subject about 25% of frame width. front_corner clock base y 1040–1077. | As in v001. |
| 12 | P2 | top, roof_skylights | Soft, curved radial shadow arcs still sweep across the roof, which points to a near point or area light (v001 #14). | top roof field. | Use a distant sun plus sky fill. |

The P2 count is 12. Row 11 groups four carried-over context, framing and board items (v001 #6, #8, #12, #13). For
the count they are tallied as four separate P2s, and rows 4 to 10 and row 12 as eight more.

No P0: the building is the correct one. Storey count, plan, both street rhythms, the program, the envelope and the
roof are right. No part floats. I found no open gap between the subject's own volumes.

## 3. Source conformance checklist

| item | mark | view(s) used | note |
|---|---|---|---|
| Silhouette and storey count | conforms | front, front_corner, right_side vs source front and oblique | Three storeys with frieze, cornice and a crested pediment. |
| Plan (top view, near-square, party walls) | conforms | top vs source top | The block is near square (about 865 × 780 px, ratio about 1.1). The west wall abuts the cream neighbour in its south half and faces the lane in its north half. The north block now runs to the east building line. Roof items fall within about 0.02 of the source positions. |
| Bay rhythm, south (five bays) | conforms | front, front_corner, facade_close | Four single bays, then a wider corner bay with paired windows. The pediment is over bay 3. |
| Bay rhythm, east (corner bay, four narrow bays, paired-arch end bay) | conforms | right_side, east_facade | Wide corner bay with a single arched window; four narrow sash bays on three floors; a pilastered end bay with paired arched windows over paired sashes, and a side door. |
| Rusticated sandstone corner and end piers | conforms | front, right_side, architecture_close, east_facade | The south-west, corner and north-east piers are rusticated to full height. The corner-shop jambs are now closed by continuous stone liners. |
| Brick pilasters and carved capital panels | conforms | front, facade_close, name_frieze_pediment | Square stone boss panels at the arch springing and at frieze level. The simplified carving is acceptable for clay. |
| Window types per floor | conforms (P2 #8) | front, facade_close, glass_close, right_side | Arched three-light windows on the top floor; three-light windows with small-paned transoms below; paired windows in the corner bay; narrow sashes on the east. |
| Sill and lintel bands | conforms | front, right_side, facade_close | Continuous sill and lintel bands; capped lintels on the east. |
| Lettered frieze | conforms (P2 #9) | name_frieze_pediment, front | Reads "GASTOWN COMMERCE BUILDING" frontally. |
| Modillion cornice and dentils | conforms (P2 #7) | architecture_close, right_side, name_frieze_pediment | Block modillions with dentil pairs, a deep soffit, and returns at both street ends. |
| Pediment (shell, crest, pedestals) | conforms | name_frieze_pediment, front_corner, roof_skylights, front | Shell and crest present. The rakes die cleanly into both pedestals with a closed sloping back, and there is no wedge. |
| Shopfronts (bulkheads, glass, transoms, recessed doors, signboards, shop cornice) | deviates (P1 #1; P2 #5, #6) | storefronts, steam_clock, front_corner | All elements are present and the corner shop wraps onto the east. The recess floors render pure black. |
| Roof (parapet coping, chimney, penthouse, skylights) | conforms (P2 #10) | top, roof_skylights, front_corner vs source top and oblique | Brick chimney, clapboard penthouse with door and window, two glazed pyramids and a small skylight, inside a coped parapet. |
| Steam clock | conforms | front, steam_clock, front_corner, top | Stone and bronze base with plaques, glazed cabinet with works, four-faced head, small roof and whistles. The head is above the shop cornice, the whistles reach the lower second-floor windows, and the clock stands about 2 m off the facade. |
| Bollards and chains | conforms | front, steam_clock, top | Chained bollards along the curb by the clock. |
| Globe lamps | conforms | front, right_side, east_facade, top | Five globes on two tiers, on both sidewalks. |
| Paving (brick sidewalks, setts, asphalt) | conforms (P2 #11, lane) | front, top, aerial | Brick sidewalks, grey setts, and asphalt with a centre line. No black curb line. |
| Neighbours | conforms with P2 deviations (#11) | front, top, left_side, rear | The lower cream west neighbour is correct. The north block is now continuous to the east line. Context blocks are blank boxes. |
| Materials hierarchy | conforms | all | Red brick body, buff sandstone dressings, dark green joinery, timber doors, bronze and brass clock, and a light roof membrane. Matches the source palette. |
| Opening depth and returns | deviates (P1 #1, P1 #2) | storefronts, glass_close, front_corner, rear | Window reveals and occupied depth read correctly. The door recess floors are black, and the north-wall openings are buried in the neighbour. |

## 4. Camera validity

- **front**: valid. The full south front and the visible east front are in frame. The east lamp is cut at the right edge (P2 #11).
- **front_corner**: valid matched oblique. The clock base is about 3 px from the bottom edge (P2 #11).
- **aerial**: valid. The subject is small and the context boxes dominate (P2 #11).
- **top**: valid true top: the whole footprint, the roof items and the street edges.
- **left_side**: **valid now.** The elevated camera shows the west party wall from the coping down to the neighbour roofs, plus the parapet, the roof and the street edge. Grade is properly hidden by the adjoining neighbours.
- **right_side**: valid. The full east elevation is in frame, with grade and cornice.
- **rear**: **valid now.** It shows the north party wall from the coping down to the north-block roof, the full roof footprint, the penthouse, the chimney, the skylights and the back of the pediment. It is also the view that reveals P1 #2.
- **rear_side**: valid but weak. The subject is small and partly screened by the across-street boxes.
- **facade_close, architecture_close, glass_close**: all present, legible and correctly targeted.
- **steam_clock, storefronts, name_frieze_pediment, east_facade, roof_skylights, interior**: all legible and correctly targeted.
- **rear_north**: legible, but it misses its stated target: neither grade contact nor coping is in frame (P2 #4).

## 5. Previous findings (v001: 0 P0 / 5 P1)

| v001 finding | status | pixel evidence |
|---|---|---|
| P1 #1: pure-black slots in the south jamb of the east corner-shop entrance | **fixed** | east_facade jamb columns x 398–416, y 790–1010 read buff stone RGB (49–73, 37–60, 27–46) continuously. The v001 zero rows at (405–412, 868–1000) are gone. The right_side jamb at x 196–216 is likewise lit throughout. Crops `east_corner_shop.png`, `right_side_corner_shop.png`. The only zero pixels left in that opening are the recess floor (new P1 #1, a different surface) and the dim side glazing (P2 #5). |
| P1 #2: pediment rake overshoot, wedge and doubled edge | **fixed** | front_corner: the right rake runs down into the left face of the right pedestal, with no dark wedge and no second slab. roof_skylights: one closed sloping back dies into the pedestal on the coping. name_frieze_pediment: both rake ends are seated against the pedestals. Crops `fc_pediment.png`, `roof_pediment_back.png`, `nfp_right_pedestal.png`, `nfp_left_pedestal.png`. |
| P1 #3: steam clock undersized, too low, too close | **fixed** | front: the clock is about 387 px tall against a ground storey of about 220 px (1.76×; source about 1.7×). The faces (y 612–665) sit above the shop cornice (about y 685). The whistles reach y 548, in the lower second-floor windows. top: the clock centre is about 68 px (about 2.0 m) off the south wall face (source about 1.9 m) and sits at 0.82 of the block width (source 0.84). |
| P1 #4: missing facade_close, architecture_close, glass_close | **fixed** | All three files are present at 1440 × 1080 and show what they should: a typical south bay through all three floors; the corner pier capital, frieze and bracketed cornice; and an arched window with its reveal, frame and fan. |
| P1 #5: left_side and rear blocked by neighbours | **fixed** | Both cameras are now elevated and show the party walls, parapet and roof footprint (see section 4). |
| P2 #6 lane | not fixed | top x 220–300 is still near black. |
| P2 #7 north neighbour set back | fixed, with a regression | The north block now runs to the east line (top: x 465–1127 against the subject's face at about 1135). This change caused P1 #2. |
| P2 #8 context boxes | not fixed | aerial, rear_side. |
| P2 #9 lamps and small skylight | lamps conform; skylight not fixed | Five globes on two tiers. The small skylight is still a pyramid. |
| P2 #10 arch-head frame | not fixed | glass_close. |
| P2 #11 frieze glyphs at the oblique | not fixed | front_corner. |
| P2 #12 board pairing | not fixed, plus a regression | phone-01 still pairs locked top with aerial, and its front panel is now empty (P1 #3). |
| P2 #13 margins | not fixed (unchanged by design) | front right edge; front_corner bottom edge. |
| P2 #14 roof shadow arcs | not fixed | top. |
| Curb line (brief note) | fixed | No zero pixels along the south curb in front. |

Score against v001: the five v001 P1s are all fixed. v002 has three P1s: one pre-existing defect that v001 missed
(#1) and two regressions (#2 and #3).
