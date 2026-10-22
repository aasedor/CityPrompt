# Independent holistic review: clay-stepped-terraced-plaza v004 (RLASM v6.1)

Reviewer: independent; not the builder. I judged rendered pixels against the locked sources only (sources/front.png, sources/oblique.jpg, sources/top.jpg). I opened all three sources, all 18 renders and all 4 phone boards at full resolution with the Read tool. Zoom crops are in `review/crops_qmzvtk/` inside the v004 folder; no other file was touched. I ignored the builder's metadata, counts, audits and notes as proof.

## 1. Verdict

Verdict: FAIL

Counts: P0=0 P1=4 P2=8

In the brief's terms this is VISUAL_REWORK_REQUIRED. v004 fixes the west bougainvillea, the pergola placement and the missing west splay at the foot. Four P1 defects remain:
- The east bougainvillea still reads as four separate collars on the parapet steps, not one cascade.
- The climbers' carrier shell shows as flat, hard-edged dark-green panels.
- The relocated south-west house has a near-black wedge at its door sill, where the new diagonal stair rises across the door.
- The crosses on the chapel and the belfry each have a black hole at the crossing.

## 2. Findings

How I told geometry voids from shadow:
- Leaf-gap shadow inside the canopies is mid-to-dark green and broken up by individual leaves. It never falls below about 30 luminance on a neutral (grey) pixel.
- Contact shadow under doors, pots and terrace edges is soft-edged, with a minimum luminance of about 45-90 (for example, at the base of the bougainvillea house door, aerial ≈(470-500, 600-625)).
- I counted a patch as a geometry void when all of these held: it is neutral (not green), hard-edged, at or near 0 luminance, keeps the same shape from two or more cameras, and is bounded by the geometry rather than by a light direction.

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | side_stair, front_corner, front | **The east bougainvillea is four separate collars, not a cascade.** In side_stair (crop `ss_boug`), the plant is four horseshoe wreaths, each wrapped round the top of one stepped parapet pier. The pier faces between them are bare white, and there is little hang down the outer face into the side stair. In front_corner (crop `fc_east`), the plant reads as four boxy green blocks sitting on the parapet runs, interrupted by the white step-ends. In the oblique source (x 820-930, y 510-790; crop `src_obl_east`), the plant is one continuous, irregular mass. It drapes over the parapet and falls down the outer face almost to the side-stair treads over about four terraces, hiding the parapet behind it. The front render (crop `front_east`) is the most acceptable view, but the white step-ends still poke through above each segment. | One kit wall_drape instance was placed per parapet segment, with its carrier following each stepped coping. Nothing spans the steps, and the outer-face hang is about 1 m. | Build the east plant as one wall_drape over the whole four-terrace run. Carry the sprays across the parapet step-ends so that no bare pier face shows between segments. Put most of the mass on the outer (side-stair) face, falling to about 0.3-0.5 m above the side-stair treads, with an irregular lower hem. |
| 2 | P1 | architecture_close, side_stair, front_corner | **The climber carrier is visible as flat, hard-edged dark-green panels.**<br>West plant: at the foot of the corner column, a smooth dark-green board with straight vertical edges and a square bottom hangs below the leaf cover (architecture_close ≈(590-650, 950-1075); crop `ac_carrier_foot`). A smooth lobed carrier edge projects past the leaves at the right end of the roof canopy (≈(1190-1235, 290-350); crop `ac_right`).<br>East plant: a flat dark-green mat lies on top of each parapet coping, and a vertical dark-green slab runs down the side of each pier (side_stair ≈(440-560, 920-935) and (545-575, 930-1000); crops `ss_dark`, `ss_boug`).<br>These surfaces are untextured planes with straight silhouettes, so they are not leaf-gap shadow. They read as cut-out green boards. | The hidden carrier extends beyond the instanced sprays and is not inset behind the leaf cover at its edges and ends. | Inset the carrier by at least one leaf length inside the spray envelope on every edge, especially the lower tip of the west column and the copings and pier sides of the east plant. Alternatively, cover its rim with an extra row of sprays. Re-check architecture_close and side_stair for any untextured green face. |
| 3 | P1 | front_corner, aerial, top | **There is a black wedge at the door of the relocated south-west house.**<br>The new diagonal stair and its sloping cheek rise across the foot of the house's east door. A hard-edged, near-black triangle fills the bottom of the door reveal (front_corner ≈(284-312, 692-706), minimum luminance 0; aerial ≈(312-348, 614-636), minimum 24; crops `fc_swdoor`, `aerial_swdoor`). Its hypotenuse follows the stair slope.<br>The door therefore opens onto the middle of a flight, with no level threshold. For comparison, the bougainvillea house door base is clean (crop `aerial_bdoor`). | The house was moved 8 m west onto the line of the new stair, but its door was kept on the east face at plaza level. The rising stair or ground surface cuts across the door, and the reveal's bottom is open to the void. | Do one of the following:<br>- Move the door to the house's south or west face, onto the plaza.<br>- Give the door a level landing the width of the door, flush with the sill, and start the stair beyond it.<br>Then close the reveal floor. Confirm that no pixel below 30 luminance remains in front_corner or aerial at the door. |
| 4 | P1 | chapel_top, rear, front_corner, right_side | **There is a black square hole at the crossing of the crosses.** The chapel's cross has a crisp black square where the arms meet: chapel_top ≈(712-724, 92-106), minimum luminance 0 (crop `chapel_cross`). The same black dot shows from the opposite side in rear ≈(1207, 343) (crop `rear_cross`) and in front_corner (crop `fc_cross`), so it is a through-void, not shading. The belfry cross shows the same dark dot (crop `fc_belfry`, top).<br>This was already present in v003 (crop `v003_chapel_cross`) but was not recorded there. | The cross is built from two boxes, with the crossing face deleted or the two boxes not merged. The renderer sees through to back-faces or the interior. | Build the cross as one closed, merged solid, or union the bar and the arm with no missing faces at the crossing. Use the same fix for the belfry cross. |
| 5 | P2 | top, front_corner, aerial | **The west splay is present but short.** The two lowest west terraces now run about 20-25% of the strip width west of the house line, to a slanting parapet with pots. A stair outside the parapet leads to an apron beside the bougainvillea house (crops `top_westfoot`, `fc_westfoot`). The source matches on the width and the slant.<br>However, the source's widened zone covers about four terraces, roughly 28% of the strip length. The bougainvillea house sits higher in the source, and the diagonal stair keeps climbing north-west up the alley beside that house (crop `src_top_westfoot`). In the render the zone is about 17% of the length (two terraces). The stair is short and nearly parallel to the strip, and it ends on a flat apron. | The bougainvillea house position was kept from v003, which limits the splay to two terraces. | Optional: move the bougainvillea house about two terraces north, extend the splay to about four terraces, and carry the diagonal stair on up the alley west of that house. |
| 6 | P2 | front_corner, aerial, architecture_close | The west climber is now a convincing draping canopy. However, its overall silhouette is a crisp stencilled T or arrow, with a straight horizontal hem on the south wall (crop `fc_bougw`). The source mass is looser and more irregular. | The envelope is a regular shape. | Break up the hem and the canopy outline with a few longer, irregular trailing sprays. |
| 7 | P2 | front_corner, right_side | Unchanged from v003 #4. The belfry's arches are about 40% of the face width, against about 75% in the source. The upper stage is square, not an octagonal arcade, and the tall shaft reads as a campanile. | Simplified stage proportions. | As in v003 #4. |
| 8 | P2 | top, chapel_top | Unchanged from v003 #6. The chapel is a small cube with a dome, and the drum has no arched windows. | Simplified massing. | As in v003 #6. |
| 9 | P2 | front, seating_terraces | Unchanged from v003 #7. The platform paving is too pale against the white risers. | Paving tone. | As in v003 #7. |
| 10 | P2 | interior | Unchanged from v003 #8. The door leaf is narrower than the opening, and a sliver of the exterior shows at the right jamb (x≈932-940). | The leaf width is under the reveal width. | Size the leaf to the opening. |
| 11 | P2 | rear_north | Unchanged from v003 #9. About half the frame is a blank volume. | Camera position. | Raise the camera or move it east. |
| 12 | P2 | glass_close | Unchanged from v003 #10. A blue rectangle floats behind the lower-right pane. | Interior element. | Remove or align it. |

(P0 rows: none. P1 rows: 1-4 = 4. P2 rows: 5-12 = 8.)

## 3. Source conformance checklist

| item | status | view used | note |
|---|---|---|---|
| Plan and proportions | conforms (P2 #5) | top, aerial, front_corner | Strip with house rows tight on both edges, north square, lower plaza. The west foot now splays with a slanting parapet and an outside stair. The splay is shorter than in the source. |
| Central stair: steps, landings, handrails | conforms | central_stair, facade_close, top | Narrow stair with landings at each terrace level, a mid cross-landing and the offset above it. Two metal handrails with posts. |
| Terraces: risers, seats, paving | conforms (P2 #9 tone) | seating_terraces, front, aerial | About 11-12 levels, each with a white riser, a seating step and a deep platform. |
| East parapet and pots | conforms | parapet_pots, side_stair, front | Stepped white parapet with coping. Kit terracotta pots at the right scale, with clustered red flower heads, on the terraces against the inner face. No pots on the plaza floor. |
| Side stair | conforms | side_stair, top | A narrow straight flight between the parapet and the east houses. It is clear of the pergola. |
| West parapet | conforms | top, front_corner, aerial | Low, white and slanting, with pots on the coping and clean contact. It now sits west of the house line. |
| Flanking houses: doors, windows, stepped heights | **deviates** (P1 #3) | front_corner, left_side, right_side, glass_close | White cubes stepping up, with blue doors and blue-framed windows that have reveals. The relocated south-west house's door has a black wedge and opens onto the middle of a stair flight. |
| Bougainvillea | **deviates** (P1 #1, #2) | architecture_close, front, side_stair, front_corner, top | West: fixed. A continuous leafy, flowering canopy over the roof edge, across the head of the east facade and round onto the south wall. It falls down the corner to a pot clear of the door jamb, and the door and windows are clear. East: four segmented collars, not one cascade. The carrier shows on both plants. |
| Chapel and dome | deviates (P1 #4; P2 #8) | chapel_top, top, front_corner | A blue dome on a drum and podium, west of the upper houses. There is a black hole at the crossing of the cross, and the body is undersized. |
| Belfry and cupola | conforms with defect (P1 #4 cross; P2 #7) | front_corner, right_side, aerial | White, two-stage, with a blue cupola and a bell, at the foot on the east. Its cross shares the black crossing hole. |
| Lower plaza | conforms | front, front_corner, top | A level paved grid plaza across the foot. The extra pots are gone. |
| Materials hierarchy | deviates (P2 #9) | front, seating_terraces | White render, blue trim, terracotta, timber pergola and green and magenta planting all read. The paving is too close to white. |

## 4. Camera validity

- **front, front_corner, aerial, top, left_side, right_side, rear_side:** valid; the whole asset is in frame and legible. The front camera does not reach the new west parapet, but top, front_corner and aerial show it clearly. This is acceptable.
- **rear:** valid as a coherence view, since the north solids are blank by design.
- **facade_close, central_stair, seating_terraces, parapet_pots, side_stair:** valid; each target is unoccluded.
- **architecture_close:** valid; the west climber, the door and the windows are fully legible.
- **glass_close, interior:** valid.
- **chapel_top:** valid. The dome and cross are legible, though about 60% of the frame is blank roof.
- **rear_north:** weak (P2 #11).
- No view clips the asset or hides its named target.

## 5. Previous-version (v003) findings: resolved in the pixels?

1. **v003 P1 #1: bougainvillea as faceted balloons with no canopy draping from the roof edge.** **Partly fixed.**
   - West plant: **fixed.** There are no balloon or ovoid shapes. A dense canopy of leafy and flowering sprays spans the roof edge over the door and windows, wraps onto the south wall and falls down the south-east corner to a pot that stands clear of the jamb (architecture_close, front, front_corner, aerial, top).
   - East plant: **not fixed in form.** It now spans four terraces, but it reads as four separate collars on the parapet steps, not one cascade (new P1 #1).
   - Both plants: the kit carrier is exposed (new P1 #2).
2. **v003 P1 #2: the strip's foot does not widen west.** **Fixed.**
   - The two lowest west terraces run west of the house line to a slanting low parapet with pots.
   - A stair runs outside the parapet.
   - The south-west house has moved west beyond the stair.
   - The residual is P2 #5: the splay is shorter than in the source.
   - The move introduced a new P1 at that house's door (P1 #3).
3. **v003 P1 #3: the pergola stands on the seating terraces instead of on the east house beyond the side stair.** **Fixed.**
   - The pergola stands on the roof terrace of east house 1, east of the side stair (top, front_corner, front, side_stair).
   - The side stair and the east terraces are clear.
   - The posts rise into the beams, and the v003 black void at the post head is gone (crops `front_pergola`, `ss_pergola`).
4. **v003 P2 #4, belfry proportions:** not fixed (P2 #7).
5. **v003 P2 #5, pot scale, bow-like flowers and plaza pots:** **fixed.** The kit pots are at the right scale, with clustered flower heads, and the plaza pots are gone.
6. **v003 P2 #6, chapel size and drum windows:** not fixed (P2 #8).
7. **v003 P2 #7, paving tone:** not fixed (P2 #9).
8. **v003 P2 #8, interior door sliver:** not fixed (P2 #10).
9. **v003 P2 #9, rear_north camera:** not fixed (P2 #11).
10. **v003 P2 #10, glass_close blue rectangle:** not fixed (P2 #12).
11. **Not recorded in v003 but present there:** the black hole in the chapel cross (crop `v003_chapel_cross`). It is still present and is now recorded as P1 #4.
12. **Regressions:** one new P1, the black wedge at the south-west house door (P1 #3), was introduced by the west-splay change.
