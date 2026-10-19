# Independent holistic review — clay mews coach house, v004 (RLASM v6.1)

Reviewer: independent. I opened all three locked sources, all 18 renders and all 4 phone boards at full resolution. I also made zoomed crops into a new scratch folder, `crops-indrev-ac1d97dd`, which holds no candidate files. I judged the pixels only and did not treat the builder's claims as proof.

## 1. Verdict

**VISUAL_REWORK_REQUIRED**: three P1 defects remain and there are no P0s. The upper south sashes now have arched heads, but the arches are about three times too steep and the glazing follows the curve. The new back-wing has the wrong width, position and roof junction against the top source. The back-wing windows are flat panels with no depth.

Counts: P0 = 0, P1 = 3, P2 = 9

## 2. Findings

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | front, front_corner, facade_close, architecture_close, eaves_corner, glass_close, roof_chimneys, interior | Every upper south sash on the end house and the neighbour has a tall arched head, measured on the front render. On the east-most sash the span is about 90 px and the rise about 28 px, so rise/span is about 0.31. The locked front shows a very shallow segmental brick arch: span about 73 px, rise about 8–9 px, so rise/span is about 0.11. In the render the top sash rail and the top panes are cut to the curve, and a raised white "eyebrow" ring with chamfered stub ends stands proud of the wall (clearest in glass_close and eaves_corner). In the source the six-over-six sash stays rectangular. A dark recessed segment sits between the flat sash head and a flush, painted arch. The windows now read as Italianate round-topped windows, which is a different building's grammar. | The arch rise is set as too large a fraction of the opening width. The sash frame and glazing are cut to the arch profile instead of sitting under it. | Set the arch rise to 0.10–0.12 × opening width on all six upper south openings, including the neighbour. Keep the sash frame and bars rectangular, with the top rail at springing height. Fill the segment between sash head and arch soffit with a dark recessed panel set back at least as far as the sash. Make the arch ring flush with the wall, or no more than about 10 mm proud, and remove the stub ends. |
| 2 | P1 | top, aerial, rear, rear_side, left_side, right_side | The neighbour's back-wing is a narrow tower about 95 px wide at the top-render scale, against a neighbour roof about 220 px wide (about 40 %). It sits flush with the west party wall. Its hipped roof lies entirely below the main rear eaves and stops against the wall under the gutter, so the wing ridge is lower than the main eaves (rear, left_side). In the locked top, the wing spans about 70 % of the neighbour's width, from just inside the west parapet to just short of the party-wall stack. Its north–south ridge climbs the main rear slope to about mid-slope. Two valleys run from that junction down to the main rear eaves at the wing's corners. | The wing was added as a separate low block under the eaves instead of being modelled as a roof that intersects the main rear slope. Its width and offset were not taken from the top source. | Widen the wing to about 0.7 × the neighbour bay. Place it from just inside the west parapet to about one stack-width short of the party-wall stack. Raise its eaves to the main eaves height. Run its ridge south into the main rear slope to about half the slope height, with two valleys down to the main rear eaves. Keep the north end form. Check the result against the locked top. |
| 3 | P1 | rear_side, rear, right_side | The back-wing's openings are two pale-grey rectangles flush with the white wall (zoomed crop of rear_side). They have no frame, no glazing bars, no sill and no reveal or return, so they read as painted patches. This breaks the opening grammar that every other window in the model follows. | A placeholder material panel was used instead of the shared recessed sash module. | Replace both with the same recessed sash module used on the main rear face. That means a reveal of at least 100 mm, frame, bars and a black sill. |
| 4 | P2 | top, front, roof_chimneys | The party-wall stacks are small, with three pots in a single row. The locked top shows a long stack on the end/neighbour party wall: about 6 pots at the ridge and a second cluster of about 4 pots on the rear slope. The locked front shows a broad, tall buff stack. | The stack is simplified to a single module. | Lengthen the stack north–south and add the rear cluster. Use about 6 + 4 pots. |
| 5 | P2 | front, rear_north, roof_chimneys, facade_close | The parapet kneelers are buff blocks that cantilever forward of the gutter and hang below the eaves band. In the source the kneeler sits on the wall line above the gutter. | The kneeler block is offset outward and down. | Pull each kneeler back to the wall plane and seat it on top of the eaves band. |
| 6 | P2 | front, facade_close, eaves_corner | The white eaves band is a plain slab. The source band is cogged/dentilled. | Detail omitted. | Add a simple dentil course to the band. |
| 7 | P2 | front, facade_close | The black plinth is a thin strip, about 2 % of wall height. The source plinth is about 8 % of wall height. | Plinth height parameter is too small. | Raise the plinth to about 0.4–0.5 m. |
| 8 | P2 | top, roof_chimneys, aerial | The rooflights are now correctly on the neighbour's south slope, but they are dark square boxes sitting slightly east of the source position: about 40–57 % and 72–88 % across the bay, against 26–38 % and 57–69 % in the source. The source rooflights are portrait, light-framed and blue-glazed. | Approximate placement and a generic box. | Shift both rooflights west. Make them portrait with a pale frame. |
| 9 | P2 | top, front, front_corner | The whole east side street is setts. In the locked top and oblique it is asphalt with yellow lines, and setts appear only at the junction mouth and in front of the coach door. | The ground material extent is simplified. | Make the east street asphalt and keep the setts at the corner and in front of the coach door. |
| 10 | P2 | rear, rear_north | The rear windows are cross-barred two-over-two with flat heads. They are plausible, but only loosely tied to the six-over-six south grammar. No source shows this face. | A generic rear module. | Optional: use six-over-six, or keep as is and record it as an inferred face. |
| 11 | P2 | coach_door, facade_close | The coach door is one uniform boarded leaf with no meeting stile and no handle. The source shows a central handle/lock. | Detail omitted. | Add a central meeting stile and a small black handle. |
| 12 | P2 | front (zoom), facade_close | On the neighbour's ground-floor paired sash, the dark central mullion runs past the sill. | Mullion length is not clipped to the frame. | Clip the mullion to the frame bottom. |

## 3. Source conformance checklist

| Item | Status | View used |
|---|---|---|
| Silhouette (two-storey end house plus attached neighbour, hipped east end, party gable west) | conforms | front, front_corner, top, left_side |
| Storey count and proportions | conforms. Two storeys with a first-floor band. The end-house plan is near-square in the top view, matching the source (hip apex about 55 % from the west in both). | front, top, right_side |
| Painted brick and plinth | painted brick conforms. The plinth deviates (too thin, P2 #7). | front, facade_close |
| Coach door (boards, transom) | conforms. Red vertical boarding, a glazed transom of 3 × 5 lights and a shallow but visible jamb return. Missing handle is P2 #11. | coach_door, facade_close, front zoom |
| Front door and fanlight | conforms. White panelled door with a rectangular fanlight, recessed with returns. | front_door, facade_close |
| Sashes | deviates (P1 #1). Pane pattern and rhythm conform (paired + single + single above, six-over-six), but the heads are over-arched and the glazing follows the arch. | front, facade_close, glass_close |
| Eaves band and gutter | conforms. Black gutter runs continuously round the SE corner. Dentil detail is P2 #6 and kneelers are P2 #5. | eaves_corner, architecture_close |
| Roof: hip | conforms | top, architecture_close |
| Roof: slate | conforms (grey) | top, front_corner |
| Roof: chimneys and pots | conforms in presence. Stack size and pot count deviate (P2 #4). | top, roof_chimneys, front |
| Roof: skylights | conforms in location (neighbour south slope, west of stack). Form and offset are P2 #8. | top, roof_chimneys |
| Neighbour (door, fanlight, sashes, back-wing) | facade conforms. The back-wing deviates (P1 #2, P1 #3). | front, top, rear_side |
| Setts | conforms in front of the coach door and at the corner. Over-extended on the east street (P2 #9). | top, front |
| Pavement and street furniture | conforms. Flag pavements, black lamp standard at the SE corner, plane tree in front of the neighbour, red gate in the east boundary wall. | front_corner, aerial, top, right_side |
| Materials hierarchy | conforms. White walls; black plinth, gutter and sills; grey slate; terracotta ridges and pots; buff stacks and parapets; red coach door. | front, architecture_close |

## 4. Camera validity

- All 18 views are legible and none clips the target asset.
- The tree canopy partly covers the neighbour in front, top and roof_chimneys. The source does the same, and the target stays readable.
- In front_corner and aerial the asset fills only about 30 % of the frame, but it is still legible.
- front_door is framed tight on the leaf. Its fanlight is checked in facade_close instead.
- glass_close is centred on the pier between two sashes. Glazing depth is still readable on both sides.
- No view is invalid.

## 5. Previous-version (v003) findings: resolved in the pixels?

1. **Flat sash heads on the upper south face (end house and neighbour): NOT RESOLVED. It is over-corrected and now a new P1.** Every upper south sash has an arched head with a painted ring, so the flat-head defect is gone. But the arch rise is about 0.31 of the span against about 0.11 in the source, and the sash glazing is cut to the curve instead of staying rectangular under a shallow arch (finding #1).
2. **Gutter stopping short at the SE hip corner: RESOLVED.** In eaves_corner and architecture_close the south gutter turns the corner and meets the east gutter in a closed mitre. The hip tile ends on the corner over the eaves band and no longer drops into a gap.
3. **Rooflights on the end house's rear slope: RESOLVED in location.** In top, aerial and roof_chimneys there are two rooflights on the neighbour's south slope, west of the party-wall stack, lying in the slope. Their form and slight eastward offset are P2 #8.
4. **Neighbour's hipped rear back-wing missing: PARTIALLY RESOLVED, still P1.** A hipped wing now exists on the neighbour's north side, but it is about 40 % of the bay width against about 70 % in the source. It sits against the west party wall instead of in the middle of the bay. Its roof stays below the main rear eaves instead of climbing into the rear slope with valleys (finding #2), and its windows are flat panels (finding #3).
