# Independent holistic review: clay-calgary-sandstone-heritage v006 (RLASM v6.1)

Verdict: PASS_ZERO_P0_P1

Counts: P0=0 P1=0 P2=10

## 1. Verdict

**PASS_ZERO_P0_P1.** The south entrance now sits at the centre of the south front, under a larger coped gable between round turret pinnacles, and that closes the only open v005 P1. The clock-tower fix from v003 still holds. No view shows a black patch, a hole, floating or intersecting parts, or an invalid camera. What remains is polish, chiefly a simplified central frontispiece (P2 #1).

Method note: I judged only rendered pixels against the locked sources `sources/front.png`, `sources/oblique.jpg` and `sources/top.jpg`. These are byte-identical to the v005 package sources. I opened all 18 renders at 1440 x 1080 and all 4 phone boards. For comparison I opened v005 `front` and v003 `east_side` from the version archives. Zoomed crops, plus the extracted prior-version renders, are in `review/crops_gdmssw/`. Builder claims, metadata and audit JSON were not taken as proof.

## 2. Findings

All findings are P2. There are no P0 or P1 findings.

| id | severity | view(s) | finding (what the pixels show) | evidence | likely cause | suggested fix |
|---|---|---|---|---|---|---|
| 1 | P2 | facade_close, front, front_corner, top (vs front.png, oblique.jpg, top.jpg) | **The central frontispiece is simplified.** The source central block is a frontispiece standing slightly forward of the wing. In the sources, its large coped gable springs below the eave line and carries a graduated arcade of 5 small round-arched lights, with a lattice tympanum above. Its round turrets run from about balcony level up past the eave. Its three arcade lights descend to the balcony deck. In the render, the eave cornice and the third-floor small-arch tier run straight across the bay. The gable stands on the eave like a large dormer, with 5 **rectangular** lights under one lintel. The turrets are short (about 3 m of shaft on a corbel ring at the eave). The bay is flush with the wing. The three arched lights over the balcony have their sills about at rail height, above the deck. Every identity element is present and in the right place, so this is fidelity polish, not a mismatch. | Crop `r_fc_gable.png`: 5 flat-headed lights. Crops `src_front_portal.png` and `src_obl_portal.png`: 5 stepped arched lights, long turret shafts, arcade reaching the deck. In top.jpg the gable front and pinnacle bases sit about 15 px forward of the wing eave. In top.png the gable coping (y≈930-945) is on the eave line (y≈945-950). | The gable component is reused from the pavilion gable, enlarged and given turrets. The bay has no projection. | Project the central bay about 1-1.5 m for its full height, about 10.8 m wide. Drop the eave and the third-floor tier inside it so the gable springs at the third-floor sill. Put a graduated 5-light round-arched arcade in the gable. Run the round turrets down to the balcony cornice on corbels. Drop the three balcony lights to the deck as door-height openings. |
| 2 | P2 | top | The orthographic frame still clips the N and S tree canopies at y=0 and y=1080. The N and S streets are out of frame. The building, with its porch steps, is fully in frame. | top.png: tree canopies cut by both frame edges. | 4:3 frame on a square block. | Widen the ortho extent about 10%. |
| 3 | P2 | front, facade_close, rear_north, east_side, left/right_side | Tree canopies are flat faceted "umbrella" discs on thin forked trunks. The sources show round, full deciduous crowns. | front.png x≈120-280, 490-690; rear_north. | Canopy primitive flattened in Z. | Use rounded canopies with about a 1:1 height-to-width ratio. |
| 4 | P2 | front, rear_north, front_corner | The N and S pavilion faces still read as three symmetric bays: outer side bay, giant arcade, inner side bay. In front.png and oblique.jpg the giant arcade sits against a broad corner pier. | Crop `r_front_sw_pav.png`: third-floor tier 3+5+3, first-floor pair, triple and pair. | Side-bay generator is symmetric on the N/S faces. | Drop the outer side bay on the N/S faces, as is already done on E/W. |
| 5 | P2 | glass_close, facade_close, front_corner | Glazing is see-through. Other arched windows and green ground show through the panes, so close views read as a hollow shell. | glass_close, left arched window x≈365-540, y≈495-600. | Transparent glass with no backing. | Darken the glass or add a dark back plane behind openings that have no interior. |
| 6 | P2 | portal_arch, facade_close | The portal fanlight above the door transom renders as a flat near-black semicircle with no glazing bars (mean RGB ≈ 16/15/12; ordinary glazing measures 29-48). I checked it against the black-patch rule. It is bounded by the transom bar and the arch intrados. It sits in the door plane 2.5 m inside a shadowed porch vault, so it is a recessed fanlight, not a hole or missing face. The source porch interiors are equally dark. It still reads as a void at close range. | Crop `r_portal_vault.png`. | Dark glass in deep shadow with an unlit hall behind. | Add 3-4 radial glazing bars and a lighter frame, or a faint interior glow. |
| 7 | P2 | front_corner, east_side (vs oblique.jpg) | Wing roof slopes have no small gabled dormers. oblique.jpg shows them on the wing roofs (around x 630-700). | east_side: plain slopes between the pavilions and the tower. | Dormers omitted. | Add 1-2 small coped dormers per wing slope. |
| 8 | P2 | glass_close, portal_arch | The arch hood moulds, archivolts and the portal ring show visible polygon facets. | glass_close hood moulds; portal arch ring has about 8 facets. | Low segment count, kept low for the size cap. | Accept, or use 12 segments on the portal and the large arches only. |
| 9 | P2 | aerial, rear_side | The building fills only about a third of the frame width. It is legible but loosely framed. | aerial: building x≈490-1000. | Camera distance. | Dolly in about 25%. |
| 10 | P2 | facade_close, rear_north | Detail framing clips the top edge. facade_close cuts the apex of the new central gable at y=0. rear_north cuts the tower crown at y=0. The full gable and crown are legible in front, front_corner, east_side and clock_tower. | facade_close top edge x≈860-960; rear_north top-left. | Detail camera aimed low. | Tilt facade_close up about 3°, or lower its target about 1.5 m. |

## 3. Source conformance checklist

| item | status | view used |
|---|---|---|
| Silhouette (gabled pavilion pyramids, central south gable, dominant tower with copper spire) | conforms | front vs front.png; front_corner vs oblique.jpg; board phone-01 |
| Storey count (rusticated basement + first + second + third, gable attic) | conforms | facade_close, rear_north, east_side |
| Plan (square block, corner pavilions, central court, tower mid-east, porch centred on the south wing) | conforms. The porch is at x≈670-770 between pinnacle bases at x≈620/820 on a block spanning x 270-1170, i.e. centred, matching top.jpg. | top vs top.jpg |
| Court and pavilion projection | conforms: square open court with a window grid; the pavilions step forward with returns. The central bay is flush (P2 #1). | top, roofs_court, front |
| Sandstone coursing | conforms (clay): buff horizontal coursing; rock-facing not modelled, which is allowed | glass_close, portal_arch |
| Window tiers: basement | conforms | facade_close, east_side, portal_arch |
| Window tiers: paired first floor | conforms | facade_close, portal_arch |
| Window tiers: round-arched second floor | conforms. The pavilion giant arcades rise from the first floor; the triple arcade over the balcony is grouped on colonnettes (sills sit high, P2 #1). | front_corner, east_side, facade_close |
| Window tiers: third-floor small-arch arcades | conforms: full width on every pavilion (3+5+3 N/S, 5+3 E/W), continuous on the wings | architecture_close, rear_north, east_side |
| String courses and eave cornice | conforms | facade_close, glass_close, architecture_close |
| Gables and pinnacles | conforms: coped gables with pinnacles on both outward pavilion faces. The central south gable sits between round turret pinnacles; its arcade and turret length are simplified (P2 #1). | gables_pinnacles, architecture_close, facade_close |
| Roofs: wing hips | conforms | roofs_court, top |
| Roofs: pavilion pyramids | conforms: steep, with copper finials, slate now mid-grey | front_corner, top |
| Roofs: cross gables | conforms: N, W and S centre gables, cross hips at the court. Wing dormers missing (P2 #7). | top, roofs_court, left_side |
| Portal | conforms: deep round-arched porch at the centre of the south front, with vault returns, colonnettes, steps, door leaves, transom and balustraded balcony. Fanlight is P2 #6. | portal_arch, facade_close, front, top |
| Clock tower: projection | conforms: projects from the middle of the east wing, with an arched porch and balustraded balcony at its foot | top, east_side, right_side |
| Clock tower: lancets | conforms: tall 4-light lancet cluster, then pairs and singles below | east_side |
| Clock tower: clocks | conforms: four faces, above the pavilion apexes in elevation (east_side clock y≈340 vs apexes y≈420-440) | east_side, clock_tower, rear_north |
| Clock tower: belfry | conforms: 5-arch belfry above the clocks | clock_tower |
| Clock tower: turrets | conforms: four round corner turrets with copper cones | clock_tower |
| Clock tower: spire | conforms: tall, slender octagonal copper spire, about 1.6x the pavilion apex height above grade (source range about 1.4-2.1x depending on depth) | right_side, east_side, clock_tower |
| Streets and trees | conforms: streets and sidewalks on four sides, 2 trees on each of N, S, W and E, matching top.jpg. Canopy form is P2 #3. | top, aerial |
| Materials hierarchy (buff stone > mid-grey slate > copper accents, dark glazing) | conforms | all whole-envelope views |

## 4. Camera validity

- **Every camera shows what its name says.** No camera is inside geometry, and no target is occluded. No whole-envelope view clips the asset.
- front, front_corner, left_side, right_side, rear and east_side: the full building is in frame with a visible margin.
- top: the full building, porch steps and E/W streets are in frame; the N/S trees and streets are clipped at the frame edge (P2 #2).
- aerial and rear_side: valid but loose (P2 #9).
- portal_arch: re-aimed correctly at the centred porch. The porch, balcony and arcade lights above are all legible.
- facade_close: on the central bay; the gable apex is clipped (P2 #10).
- rear_north: on the north front; the tower crown is clipped at the top edge (P2 #10).
- clock_tower: the crown, belfry, clocks, turrets and spire are fully framed. The shaft is cut at the bottom by design.
- interior: a straight-on view from inside a window with lit jamb returns and glazing bars. The arched head is above the frame. Minimal but valid.
- glass_close, architecture_close, gables_pinnacles and roofs_court: on target and legible.

## 5. Previous findings

| previous finding | status | evidence |
|---|---|---|
| v005 P1: south entrance in the SW pavilion instead of the centre of the south front | **fixed** | top: porch centred on the south wing between turret pinnacles. front, front_corner and facade_close: porch, balcony and arcade under the larger central gable. In v005 `front.jpg` the porch sat at the SW corner (x≈150-200). The SW pavilion's south face is back to the standard grammar: giant arcade from the first floor under the full-width small-arch tier (crops `r_front_sw_pav.png`, `r_fcorner_sw_pav.png`). |
| v003 P1 (also carried in v005): clock tower too short and squat, spire four-sided | **fixed, no regression** | In east_side the clocks sit above the pavilion apexes; in v003 `east_side.jpg` they sat below the apexes. The 5-arch belfry, four round turrets with copper cones and the slender octagonal copper spire are all present (clock_tower). |
| v005 P2 #2: four trees on the south sidewalk | fixed | top: 2 south trees, at x≈490 and 945 |
| v005 P2 #7: near-black slate | fixed | Roofs read mid-grey in every view |
| v005 P2 #3: top-view clipping | not fixed (P2 #2) | top |
| v005 P2 #4: umbrella tree canopies | not fixed (P2 #3) | front |
| v005 P2 #5: symmetric N/S pavilion bays | not fixed (P2 #4) | front, rear_north |
| v005 P2 #6: see-through glazing | not fixed (P2 #5) | glass_close |
| v005 P2 #8: arch facets | not fixed (P2 #8) | glass_close |
| v005 P2 #9: wing dormers | not fixed (P2 #7) | east_side |
| v005 P2 #10: loose aerial and rear_side framing | not fixed (P2 #9) | aerial, rear_side |
| Earlier fixes that had to hold: tower porch with balcony; pavilion giant arcades from the first floor with a full-width third-floor tier; 2 trees on each of N/W/E; E/W pavilion faces with only the inner side bay; straight-on interior camera; open square court with cross hips | **all hold, no regression** | east_side, right_side, rear_north, left_side, top, interior, roofs_court |
