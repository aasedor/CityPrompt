# Independent holistic review: clay-cable-stayed-cycle-ring v003 (RLASM v6.1)

Reviewer: independent; judged only rendered pixels against the locked sources (sources/front.png, sources/oblique.jpg, sources/top.jpg). I opened all 18 renders and the 4 phone boards at full resolution. I made zoomed crops only into the new folder `/tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/ring-v003-review-crops-bf18b0e9/`. I did not read builder metadata or notes, and none of my conclusions rely on them.

## 1. Verdict

**Verdict: PASS_ZERO_P0_P1**. The ring now reads correctly as the source bridge in every whole-envelope view. It is a circular red cycle ring with white glass railings, hung by a radial cable fan from one tall central pylon over a marked four-arm intersection, with concrete piers and one straight pale-grey ramp landing at the road. All three v002 P1s are fixed in the pixels. What remains is polish only.

Counts: P0 = 0, P1 = 0, P2 = 9

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P2 | top, ramp_landing, aerial | The ramp centre line is very faint, about 14 grey levels above the surface. In `top` it shows at x≈583 from the ring edge (y≈555) only to y≈810, then disappears for the lower ~45% of the ramp down to the foot (y≈1030). In `ramp_landing` no line is visible on the lower ramp or at the landing. The builder says the line runs "from the ring edge to the foot", but the pixels show that is only partly true. | The line strip is probably one straight segment while the ramp deck is hogged or curved, so the lower part sinks below the deck surface. It may also be a coplanar strip with too little offset or contrast. | Sweep the line along the actual ramp deck surface with a +5–10 mm offset, run it all the way to the foot, and use full white so it reads the way the ring's dashes do. |
| 2 | P2 | front, front_corner, facade_close, column_support | The deck edge reads heavier than in the source. In `front_corner` at x=600, the outer railing is about 12 px and the fascia below the kerb about 11 px (ratio ≈1.0). The source oblique and front show a slim white edge band about 0.45× the glass railing height. The ring reads as a thicker grey band with a low railing. | The fascia depth is too large relative to the railing, or the railing is too low. | Reduce the visible fascia to about 0.4–0.5× the railing height, either by thinning the edge band and setting the soffit back, or by raising the glass railing to the source proportion. Keep the anchor blocks seated on the reduced fascia. |
| 3 | P2 | architecture_close, column_support, intersection_under, front | The piers are not one family. Most ring piers are strong wedges (top:bottom width ≈ 2.2:1 in `architecture_close`), but at least one is a straight prismatic shaft (`column_support`, right). The source piers are all near-prismatic concrete posts with only a slight taper (≈1.4:1 or less). | Two different pier generators, and the wedge taper is exaggerated. | Use one pier profile matched to the source: rectangular, with a slight top flare of about 1.3–1.5:1. Apply it to every ring and ramp-junction pier. |
| 4 | P2 | rear, rear_north, ramp_landing, rear_side | Context house walls are blank. The two foreground houses in `rear`, the gable house in `rear_north` and the long barn-like block in `ramp_landing` have no windows on any visible face. Other houses have windows on only one long face. | The window arrays are generated for one elevation only. | Add the same simple window rhythm to every visible long face and gable of the pitched houses. This is context only, so a coarse rhythm is enough. |
| 5 | P2 | front (collar crop), pylon_head, cable_fan | Small dark voids or sockets show between the cable stubs where they meet the ring under the cone collar. | The cable ends are not fully closed into the collar ring, or there are gaps in the ring geometry. | Close the cable-ring band into a solid collar so each cable end sits inside it with no visible gap. |
| 6 | P2 | top | The ring band is slightly narrow. Band width / outer diameter ≈ 0.077 (≈43/555 px), against ≈0.093 (≈70/756 px) in the source top. | The deck width parameter is about 15–20% under the source. | Widen the ring deck by about 15–20%, keeping the outer diameter. Re-seat railings and anchors. |
| 7 | P2 | facade_close | There is a bright specular hotspot on one glass railing panel (x≈760–850, y≈220–260). | Glass roughness is too low for clay, combined with the key light angle. | Raise glass roughness or cut specular on the railing glass for clay renders. |
| 8 | P2 | front | The render's `front` camera is a distant view near deck height, from outside the ring. The source front is an elevated near view from the ramp junction, where the ring overfills the frame. The ring fills ≈63% of frame width in the render against more than 100% in the source, so the matched-role comparison is weaker, though still legible. | The camera station was not matched to the source viewpoint. | Optionally move the `front` camera to the ramp junction, about 3 m above the deck, looking across the ring toward the pylon, as in the source. |
| 9 | P2 | top, aerial, intersection_under | The intersection markings are simplified. Lane dashes, red cycle crossings with dotted edges and stop bars are present. The source's shark-teeth give-way triangles, turn arrows and kerbed traffic islands or medians are absent. | The context markings were simplified. | Optionally add give-way triangles and a few arrows at the stop lines. |

There are no P0 or P1 findings.

## 3. Source conformance checklist

| item | status | view(s) used | note |
|---|---|---|---|
| Plan and proportions | conforms | top vs source top, aerial | The circular ring is centred over the four-arm intersection, with the crossings inside the hole and the band passing over the corner pavements. One straight ramp leaves tangentially toward the south and runs beside the south arm, as in the source top. |
| Ring radius and width | conforms (minor deviation) | top | The diameter relative to the intersection is plausible. The band is about 15–20% narrow (P2 #6). |
| Pylon | conforms | front, left_side, right_side, rear, pylon_head, intersection_under | One tall slender steel pylon stands on a round base island at the intersection centre. The spike continues above the cable collar. |
| Cable fan | conforms | front, cable_fan, top, architecture_close, column_support | A radial fan of about 24–32 cables runs from one collar to the inner ring edge. The collar is a downward-flaring cone (fixed). Each cable lands in an anchor block seated on the inner fascia, with no gap. |
| Deck surface and edges | conforms (minor deviation) | glass_close, ring_deck, top, front_corner | Red cycle surface with a white dashed centre line. The edge band is heavier than in the source (P2 #2). |
| Railings | conforms | glass_close, ring_deck, facade_close, front | White posts and handrail with glass infill on both the inner and outer edges. The ring railing opens where the ramp joins. |
| Columns | conforms (minor deviation) | front_corner, left_side, architecture_close, column_support, intersection_under | There are four ring piers plus the ramp piers, matching the source count. All bear on the ground and meet the soffit. Pier shape is inconsistent and over-tapered (P2 #3). |
| Ramps and landings | conforms | ramp_landing, aerial, front, front_corner, right_side, top | One straight ramp with a pale grey-beige concrete deck, white railings on both sides, piers seated under the soffit, and a flush landing on a grade apron at the road with a cycle crossing. The red ring against the grey ramp now reads clearly. The centre line is truncated and faint (P2 #1). |
| Intersection beneath | conforms (simplified) | top, intersection_under, facade_close | Four arms with dashed lanes, red cycle tracks, red cycle crossings with dotted edges and stop bars. Some source markings are missing (P2 #9). |
| Context | conforms (simplified) | front, rear, rear_north, ramp_landing, left_side, rear_side, aerial | Low brick blocks with grey roofs and low-poly trees. Every pitched house is now one closed brick solid under a closed slate roof prism. Some walls are blank (P2 #4). |
| Materials hierarchy | conforms | all | The red cycle surface, pale grey concrete ramp, piers and fascia, white steel pylon, cables and railings, brick context, slate roofs and grey asphalt all follow the source palette and its hierarchy. |

## 4. Camera validity

- All 18 views are valid. None has the target occluded, the asset clipped in a way that hides identity, or nothing legible.
- `rear_side`: a foreground flat-roof context block fills the bottom-centre of the frame, but the whole ring, pylon and fan stay unobstructed above it. Valid.
- `pylon_head` and `cable_fan` intentionally crop to the head and fan. They are legible and show the collar and cable termination.
- `glass_close` and `ring_deck` are near-duplicate deck-level views along the ring. Both are valid, though there is little extra coverage (no finding).
- `front` is valid but does not match the source front station (P2 #8).

## 5. Previous-version findings: resolved in the pixels?

| previous finding | status in v003 pixels | evidence |
|---|---|---|
| v002 P1: cables stop at the top of the inner kerb while the anchor blocks hang lower on the fascia, with bare fascia between, so the blocks float | **Resolved** | In `architecture_close` (crop `anchor_blocks.png`) each cable runs into the top face of its block. The block sits on the inner fascia directly under the kerb, with no bare fascia between cable and block. `column_support` and `facade_close` (crop `inner_anchor_row.png`) show the same for the whole visible anchor row. |
| v002 P1: every pitched context house shows a solid black slot along the gable base or eave (also the surviving v001 black-gable finding) | **Resolved** | I inspected every house in `front` (left house and gable end), `rear_north` (gable house), `ramp_landing` (long house with gable end), `rear` (two foreground houses and the far long house), `rear_side`, `left_side`, `right_side`, `front_corner` and `aerial` at 3–5× zoom. All gables are continuous brick to the verge, the eaves are closed with an overhang, and no black slot or gap remains anywhere. |
| v002 P1: the ramp deck carries the ring's red finish and dashed line, where the sources show a pale grey-beige concrete ramp with a solid white centre line | **Resolved (finish), with a residual P2** | The ramp deck is pale grey-beige in `ramp_landing`, `aerial`, `front`, `front_corner` and `top`, and the red ring against the grey ramp reads clearly. The solid white centre line exists but is faint and runs only over the upper ~55% of the ramp, with nothing at the foot (P2 #1). |
| v002 P2: the cable collar is a drum with a funnel narrowing downward instead of the source's cone flaring downward | **Resolved** | In `pylon_head` the collar is a cone flaring downward from the shaft to the cable ring, and `front`, `cable_fan` and `rear_side` agree. Small socket voids remain at the cable ring (P2 #5). |
| v001 P0: ramp landing (confirmed fixed in v002) | **Still resolved** | In `ramp_landing` the ramp deck meets the grade apron flush at the cycle crossing, with no step, gap or float. The ramp piers are seated under the soffit. |
| v001 P1s, four of five confirmed fixed in v002 (the fifth was the black gable) | **No regression seen** | The ring geometry, railings, piers and pylon show no new defects in any view. The black-gable item is now resolved as above. |
