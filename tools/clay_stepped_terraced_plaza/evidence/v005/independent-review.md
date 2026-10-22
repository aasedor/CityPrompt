# Independent holistic review: clay-stepped-terraced-plaza v005 (RLASM v6.1)

Reviewer: independent; not the builder. I judged rendered pixels against the locked sources only (sources/front.png, sources/oblique.jpg, sources/top.jpg). I opened all three sources, all 18 renders and all 4 phone boards at full resolution with the Read tool. Zoom crops are in `review/crops_qzuziz/` inside the v005 folder; no other file was touched. I ignored the builder's metadata, counts, audits and notes as proof.

To confirm the brief's claim that nothing else changed, I also diffed each v005 render against the same v004 render (grey difference over 25). The changes are confined to the four targeted areas:
- the two bougainvilleas (front, side_stair, architecture_close, front_corner, top, aerial, rear_north, rear_side, left_side and right_side);
- the south-west house (front_corner and aerial);
- the two crosses (chapel_top, rear, front_corner and rear_side).

central_stair, glass_close, interior, parapet_pots and seating_terraces are unchanged from v004.

## 1. Verdict

Verdict: PASS_ZERO_P0_P1

Counts: P0=0 P1=0 P2=11

All four v004 P1s are fixed in the pixels, the three v003 P1s stay fixed, and I found no new P0 or P1. Eleven polish items remain (P2); none blocks approval.

## 2. Findings

How I told geometry voids from shadow:
- I scanned every render for neutral pixels (channel spread under 25) with luminance under 30.
- **Foliage.** Every cluster sat inside foliage, at these locations:
  - side_stair ≈(480-600, 880-1080): the east plant's curtain on the outer face of the lowest pier;
  - front ≈(1160-1440, 600-760), parapet_pots, central_stair, facade_close and seating_terraces: geranium leaves;
  - architecture_close and rear_north: the west plant.

  The darkest of these pixels are tinted green (for example (9,17,4) and (2,5,1)). They are bounded by individual leaf outlines, and at 5-6x zoom they break up into leaf gaps (crops `ss_hang`, `ac_foot2`, `front_east_low`). I count them as leaf shadow, not voids.
- **Non-foliage.** The only sub-30 pixels outside foliage are a window pane on the east face of the south-west house: aerial (319,626) = (22,28,34). It is a blue-tinted pane inside a blue frame, matching the other glazing.
- **Crosses.** No cross pixel falls below 109 luminance.
- **South-west door.** The darkest pixel in the door region is the door's own glazed panel (about 48).

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P2 | front, side_stair | **The east bougainvillea is one continuous cascade, but its massing is still a little boxy.** From the front (crops `front_east`, `front_east_mid`), each terrace's drape is a near-rectangular block with a near-vertical inner face and a fairly straight hem about 0.6 m down. The step-end drapes join the blocks, so no bare pier shows. On top of the coping, the side_stair view shows a flat-topped, hedge-like run (crop `ss_upper`). The oblique source mass is looser, rounder and weighted to the outer face. | Each terrace's spray envelope is a box swept along the parapet. | Optional: round the top of the envelope and vary the depth of the inner-face hang per terrace (0.3-0.8 m), so the stepped blocks read as one irregular mass. |
| 2 | P2 | architecture_close | **The west plant's carrier is now hidden at every edge. In the thinner upper canopy, a smooth dark-green under-layer still shows between the leaves.** It shows at ≈(1070-1190, 10-60), just under the rim sprays along the roof edge, and faintly at ≈(700-850, 200-330) (crops `ac_righttop`, `ac_mid`, `ac_upper_1x`). At review scale it reads as deep foliage, not as a board: there is no straight silhouette and no hard-edged panel. | The inset carrier is visible through gaps where the spray density is low. | Optional: add a few sprays in the upper-right canopy, or darken the carrier towards leaf-shadow tone. |
| 3 | P2 | top, front_corner, aerial | Unchanged from v004 #5. The west splay covers two terraces (about 17% of the strip length), against about four terraces (about 28%) in the top source. The outside stair is short and ends on a flat apron. | The bougainvillea house position is kept. | As in v004 #5. |
| 4 | P2 | front_corner, aerial, architecture_close | Unchanged from v004 #6. The west climber's overall silhouette is still a crisp stencilled T, with a fairly straight lower hem on the south wall (crops `fc_westfoot`, `aerial_westfoot`). The new rim sprays soften the edge only locally. | Regular envelope. | Break up the hem and outline with a few longer, irregular trailing sprays. |
| 5 | P2 | front_corner, right_side, aerial | Unchanged from v004 #7. The belfry's arches are about 40% of the face width, against about 75% in the source. The upper stage is square, not an octagonal arcade. | Simplified stage proportions. | As in v003 #4. |
| 6 | P2 | top, chapel_top | Unchanged from v004 #8. The chapel is a small cube with a dome, and the drum has no arched windows. | Simplified massing. | As in v003 #6. |
| 7 | P2 | front, seating_terraces, facade_close | Unchanged from v004 #9. The platform paving is too pale against the white risers. | Paving tone. | Warm and darken the platform and landing colour. |
| 8 | P2 | interior | Unchanged from v004 #10. The door leaf is narrower than the opening, and a sliver of the exterior shows at the right jamb (x≈932-940; crop `interior_jamb`). | The leaf width is under the reveal width. | Size the leaf to the opening. |
| 9 | P2 | rear_north | Unchanged from v004 #11. About half the frame is a blank volume. | Camera position. | Raise the camera or move it east. |
| 10 | P2 | glass_close | Unchanged from v004 #12. A blue rectangle floats behind the lower-right pane. | Interior element. | Remove or align it. |
| 11 | P2 | top, front_corner, aerial | **The south-west house sits on the plaza's edge (new observation, geometry unchanged since v004).** Its new south door opens onto the plaza near its north-west corner, cleanly. However, the western part of the house's south face stands over the bare base, not over paving (top ≈(345-418, 805-815)). | The plaza slab stops at x≈418 in the top view; the house extends further west. | Optional: extend the plaza paving west under the full south face of the house. |

(P0 rows: none. P1 rows: none. P2 rows: 1-11 = 11.)

## 3. Source conformance checklist

| item | status | view used | note |
|---|---|---|---|
| Plan and proportions | conforms (P2 #3, #11) | top, aerial, front_corner | A long strip climbs north, with house rows tight on both edges, a north square, a lower plaza across the foot and a west splay at the foot. The splay is shorter than in the source. |
| Central stair: steps, landings, handrails | conforms | central_stair, facade_close, top | The stair is narrow, with a landing at each terrace level, a mid cross-landing and an offset above it. It has two metal handrails on posts. |
| Terraces: risers, seats, paving | conforms (P2 #7 tone) | seating_terraces, front, aerial | About 11-12 levels, each with a white riser, a seating step and a deep platform. |
| East parapet and pots | conforms | parapet_pots, side_stair, front | A stepped white parapet with coping. Terracotta pots of red geraniums stand on the terraces against its inner face. The bougainvillea now covers the lower four parapet runs as one mass. |
| Side stair | conforms | side_stair, top | A narrow straight flight runs between the parapet and the east houses. The outer-face drape hangs into it without blocking it. |
| West parapet | conforms | top, front_corner, aerial | A low, white, slanting parapet with pots on the coping and clean contact, west of the house line, with the outside stair beyond it. |
| Flanking houses: doors, windows, stepped heights | conforms | front_corner, aerial, left_side, right_side, glass_close | White cubes step up both sides, with blue doors and blue-framed windows set in reveals. The south-west house now has its door on its south face onto the plaza. The door is clean, with no wedge and no stair across it, and the face has two windows above the diagonal stair (crops `fc_swhouse`, `aerial_swhouse`). |
| Bougainvillea | conforms (P2 #1, #2, #4) | architecture_close, front, side_stair, front_corner, top | **West:** a continuous canopy over the roof edge, falling down the corner to a pot clear of the door. Its rim is leafy and no carrier board shows. **East:** one continuous cascade over four terraces. It is weighted to the outer face, crosses every step-end, and its hem hangs into the side stair. |
| Chapel and dome | conforms (P2 #6) | chapel_top, top, front_corner, rear | A blue dome on a drum and podium, at the top on the west. The cross is a closed solid with no hole (crop `chapel_cross`, minimum luminance 130). |
| Belfry and cupola | conforms (P2 #5) | front_corner, right_side, aerial, rear_side, rear_north | White, two-stage, with a blue cupola and bell, at the foot on the east. The cross foot sits on the cupola with no gap and no dark crossing (crops `fc_belfry`, `rs_belfry`, `rside_belfry`, `rn_belfry`, `aerial_belfry`). |
| Lower plaza | conforms (P2 #11) | front, front_corner, top | A level paved grid across the foot. |
| Materials hierarchy | deviates (P2 #7) | front, seating_terraces | White render, blue trim, terracotta, timber pergola, and green and magenta planting all read. The paving is too close to white. |

## 4. Camera validity

- **front, front_corner, aerial, top, left_side, right_side and rear_side:** valid; the whole asset is in frame and legible.
- **rear:** valid as a coherence view, since the north solids are blank by design.
- **facade_close, central_stair, seating_terraces, parapet_pots and side_stair:** valid; each target is unoccluded. side_stair now shows the east cascade clearly.
- **architecture_close:** valid; the west climber, the door and the windows are fully legible.
- **glass_close and interior:** valid.
- **chapel_top:** valid. The dome and the closed cross are legible, though about 60% of the frame is blank roof.
- **rear_north:** weak (P2 #9).
- No view clips the asset or hides its named target.

## 5. Previous findings

### v004 P1s (0 P0 / 4 P1)

1. **East bougainvillea as four separate collars: fixed.**
   - In side_stair (crop `ss_boug`, compared with v004 side_stair), the plant is one continuous mass from the lowest pier to the fourth terrace. No bare pier face shows between runs.
   - Most of the mass hangs on the outer face, and an irregular hem of trailing sprays reaches well down towards the side-stair treads (crop `ss_hang`).
   - From front_corner (crop `fc_east`) it reads as one cascade along the parapet, not four blocks. From the front, it is continuous across the step-ends.
   - The residual box-like massing is P2 #1.
2. **Climber carrier as flat dark-green panels: fixed.**
   - There is no hard-edged or straight-sided green board at the foot of the west corner column (crops `ac_foot`, `ac_foot2`) or at the right end of the roof canopy (crops `ac_right`, `ac_righttop`). The silhouettes are leafy everywhere.
   - On the east plant, there is no flat mat on the copings and no slab down the pier sides (crops `ss_boug`, `ss_upper`, `ss_hang`).
   - The residual under-layer visible through a few gaps in the upper canopy is P2 #2.
3. **Black wedge at the south-west house door: fixed.**
   - The door is now on the south face, onto the plaza. Its sill meets the paving cleanly.
   - In the same region, the minimum luminance is 48 in front_corner (the door's own glazing; it was 0.1 in v004). In aerial the minimum is 63.
   - The east face carries two windows, both clear of the diagonal stair's cheek (crops `fc_swhouse`, `aerial_swhouse`, `top_swfoot`).
4. **Black holes through the chapel and belfry crosses: fixed.**
   - Chapel cross: minimum luminance 130 in chapel_top (0 in v004), 137 in rear (34 in v004) and 113 in front_corner. It is a closed white plus shape (crops `chapel_cross`, `rear_cross`, `fc_cross`).
   - Belfry cross: minimum luminance 121 in front_corner (42 in v004). The foot now meets the cupola with no gap in every view that shows it (crops `fc_belfry`, `rs_belfry`, `rside_belfry`, `rn_belfry`, `aerial_belfry`).

### v004 P2s

5. **West splay short (#5):** not fixed (P2 #3). It was not targeted.
6. **West climber stencilled silhouette (#6):** not fixed (P2 #4).
7. **Belfry proportions (#7):** not fixed (P2 #5).
8. **Chapel size and drum windows (#8):** not fixed (P2 #6).
9. **Paving tone (#9):** not fixed (P2 #7).
10. **Interior door sliver (#10):** not fixed (P2 #8).
11. **rear_north camera (#11):** not fixed (P2 #9).
12. **glass_close blue rectangle (#12):** not fixed (P2 #10).

### v003 P1s (0 P0 / 3 P1)

1. **Bougainvillea as faceted balloons with no roof-edge canopy:** still fixed. Both plants are leafy, flowering drapes; there are no ovoids anywhere.
2. **No west splay at the foot:** still fixed. The splay is short (P2 #3).
3. **Pergola standing in the east seating terraces:** still fixed. The pergola stands on east house 1, beyond the side stair. The posts meet the beams with no void (crops `front_pergola`, `fc_pergola`).

### Regressions

None. The v004-to-v005 render diff touches only the four targeted areas. No new black patch, slot or wedge appears in any view, and the v003 and v004 fixes are intact.
