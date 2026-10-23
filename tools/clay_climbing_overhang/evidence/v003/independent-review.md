# Independent holistic review — The Overhang, v003 (RLASM v6.1 architectural clay)

Reviewer: independent, not the builder. I opened all three locked sources and all 18 renders at full resolution, plus 2x–3x crops of the shell/pool-block junction, the west facade bays, the hold distribution, the white wall under the east overhang and the frame-box corner. Boards were glanced at only as a cross-check. Metadata and builder notes were not used as proof.

## 1. Verdict

**VISUAL_REWORK_REQUIRED** — Envelope, plan, storeys, shell form, junction, roof program and camera set now conform with zero P0. Two clearly visible fidelity defects remain: the west street facade has a coarser bay rhythm than the source, and the white holds are scattered over the shell's upper west and flare faces, which the source shows as plain timber.

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | front, front_corner, left_side, rear_side vs source front/oblique | The west (street) facade of the pool block has **10 fin bays** from the north corner to the SW corner pier (counted in front and left_side). The same facade in the source front and oblique shows **about 12–13** narrower bays (oblique crop: 12 full windows visible before the far end). Render bays are about 20–25% wider, so the street elevation looks coarser and the tall-window rhythm is lost. | The bay module is set too wide (≈3.0–3.6 m) for the source's ≈2.5–2.7 m fin spacing. | Re-module the west facade to 12 bays (13 if the far end allows) along the same length, keeping the fin depth, the spandrel bands and the two-pane tall recessed windows. Re-render front, front_corner, left_side and rear_side. |
| 2 | P1 | front, front_corner, rim_interior, plaza_planters vs source front/oblique/top | About 50 **white** holds are scattered across the shell's upper flare face (just below the rim, west side) and the large west face. In the source, the flare face and most of the big west face are **plain timber**. Their white holds form a narrow diagonal band along the west/south fold, and the dark holds sit on the south face. The render's hero silhouette reads as speckled all over, not "plain folded timber plus a dense south climbing face". | The hold scatter's region mask covers whole west faces instead of a strip along the fold. The v003 thinning cut the count but did not move the holds. | Remove the white holds from the flare face and the outer two-thirds of the west face. Keep about 15–20 white holds in a ≈1.5–2 m band along the west/south fold. Leave the south-face dark-hold density and the climbers unchanged, and keep the inner-wall white holds. |
| 3 | P2 | architecture_close (≈x490–530, y190–225) | A small stray block with a sloped top sits at the SW corner, where the west-facade corner pier, the frame-box top and the parapet band meet. It reads as an orphan corbel. | Leftover end of the cornice or spandrel element after the frame box and parapet were re-cut. | Trim the stub flush with the corner pier, or extend the parapet band over it. |
| 4 | P2 | climbing_face, right_side, aerial | The white wall under the east overhang is a full-height blank wall with two thin horizontal slots and projecting sills (the "deeper ribbons"). Up close they read as stub ledges rather than glazing. The source shows only a plain white wall here, with dark glazing beyond. Coherent, but slightly odd. | Ribbon recesses are too shallow and too short to read as openings. | Either drop the slots (plain white wall) or make them full recessed glass ribbons with visible glass and returns. |
| 5 | P2 | rim_interior, top | The crash mat at the bottom of the hollow is not legible; it reads as a uniform dark void. This is consistent with the dark floor in the source top, but there is no mat edge. | Fill light does not reach the floor; the mat value is too close to the shadow. | Raise the mat albedo slightly or add a mat edge bevel. |
| 6 | P2 | front, front_corner, top vs source | The plaza grass planters read sparser than the source's dense straw mass, with green ground visible between tufts in the aerial views. | The tuft count is low for the planter area. | Increase tuft density by about 1.5x in both planters. |
| 7 | P2 | front, top vs source | The west sidewalk has 6 street trees against about 8–9 in the source. | Tree spacing is too wide. | Add 2–3 trees at the source spacing. |
| 8 | P2 | architecture_close, entrance vs source front | Frame-box ribbons have 4 panes per storey; the source shows about 5 narrower panes. | Mullion count. | Add one mullion per ribbon. |
| 9 | P2 | all shell views | The CLT reads a little darker and more saturated amber than the sunlit honey of the source (shadow-side sample ≈(149,104,28)). Acceptable for clay. | Material base colour and lighting. | Optional: lift the value about 10% and reduce saturation slightly. |

No P0 findings.

## 3. Source conformance checklist

| Item | Status | View(s) used |
|---|---|---|
| Silhouette / storey count: three-storey pool block | conforms (ground + 2 upper + deep parapet) | left_side, front, rear |
| Penthouse: one storey | conforms; it sits just above the east block roof | front, rear, pool_deck |
| Four-storey east block | conforms | right_side, rear, aerial |
| Plan (top view): pool block W, penthouse strip middle, east block E, shell over SE plaza, roughly 39 x 36 m | conforms (rim ≈0.39–0.80 of the building width, matching the source) | top vs source top |
| Climbing shell: foot on the plaza in front of the facade | conforms | wall_base_contact, entrance, front |
| Shell: lean east and ~10 m overhang | conforms | front, front_corner, right_side, top |
| Shell: folded faces, west flare meeting the parapet at a fold, triangular south face | conforms | front, rim_interior, climbing_face |
| Shell: level open rim with light fascia | conforms | rim_interior, front |
| Shell contact with plaza and facade (v003 vertical return plane) | conforms; the frame box, spandrels, parapet and coping die into the CLT along one edge, with no gap or poke-through at 3x | front/front_corner crops, architecture_close, rim_interior |
| Holds | **deviates**: white holds spread over the flare and west faces (finding 2); south-face dark density is OK | front, climbing_face, rim_interior |
| Climbers | conforms: 3 on the south face, distinct poses | climbing_face |
| Open top and inner walls | conforms (inner white holds, dark floor); mat edge illegible (P2) | rim_interior, top |
| West front rhythm: fins, spandrels, recessed windows, glazed ground floor | **deviates** on bay count, 10 vs about 12–13 (finding 1); fin/spandrel/recess grammar and recessed glazed ground floor conform | left_side, front, facade_close |
| South frame box and glass ribbons | conforms (projecting white frame, two ribbons, recessed ground floor) | architecture_close, front |
| Entrance doors (two pairs) | conforms | entrance, interior |
| Parapet band | conforms (deep white band, coping) | architecture_close, left_side |
| Pool deck: infinity pool along the west edge | conforms (pool proportion about 1:2, as in the source) | top, pool_deck |
| Pool deck: weir and trough | conforms (dark trough strip at the west edge) | pool_deck, top |
| Pool deck: glass balustrades | conforms | left_side, architecture_close |
| Pool deck: loungers | conforms (along the east side of the pool, plus a north row) | top, front |
| Roof garden: planters, grasses, small yellow-green trees | conforms | rear_side, top, front |
| Penthouse: glazing to the deck at the south end | conforms | front, pool_deck |
| Penthouse: solid north end with door | conforms (door near the north end) | front, rear |
| Penthouse: AHU with fan on the roof | conforms | front, top |
| East block roof: two skylights, small plant | conforms | top, aerial |
| White facade under the overhang | conforms in mass; the slot "ribbons" read oddly (P2) | climbing_face, right_side |
| Plaza: two-tone paving bands | conforms | front, wall_base_contact |
| Plaza: two grass planters (rectangle + L) | conforms in layout; density is low (P2) | top, plaza_planters |
| Plaza: east planted strip | conforms | top, right_side |
| Plaza: bollards | conforms | aerial, right_side |
| Plaza: lamp posts | conforms | front, plaza_planters |
| Sidewalks: concrete west sidewalk | conforms | front, left_side |
| Street trees in pits | conforms in type; count is low (P2) | front, top |
| Streets and crossings (west and east streets) | conforms | front, top, aerial |
| Parked cars (east street) | conforms (simple massing) | top, right_side |
| Neighbours (brick mid-rise and residential blocks) | conforms (clay massing) | aerial, front |
| Materials hierarchy: white precast > glass > honey CLT accent, granite plaza | conforms; CLT is slightly saturated (P2) | all |
| North and east fronts (no source) | coherent with the visible grammar | rear, right_side |

## 4. Camera validity

All 18 views are valid. No target is occluded or clipped, and every view is legible.

- **pool_deck**: the near water fills about 55% of the frame, but the pool, trough, balustrade, loungers, penthouse and garden are all legible.
- **interior**: an authored lobby, looking out through the entrance doors to the shell foot. Legible.
- **top**: slight perspective, but the plan reads clearly.
- **front / front_corner / aerial**: match the source roles, with the shell and rim fully in frame.
