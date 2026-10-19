# Independent holistic review: Regency stucco terrace block, v003 (RLASM v6.1 architectural clay)

Reviewer: independent; I took no part in the build. Evidence used: the pixels of sources/front.png, sources/oblique.jpg and sources/top.jpg, all 18 renders/*.png at full resolution, and boards/phone-01..04. Zoomed crops were written only to a new folder, `scratchpad/crops-rev-2304227065/`. I used no metadata or builder notes as proof.

## 1. Verdict

**VISUAL_REWORK_REQUIRED**: the black voids at the porch-balcony and parapet corners are fixed. However, the front view still hides the whole mansard, its dormers and its fins. The mansard also reads as a low hipped roof, and two new classes of dark void or gap repeat across the facades: one at every ground-floor voussoir head and one under every Corinthian abacus.

Counts: P0 = 0, P1 = 4, P2 = 8

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | front (vs source front; board phone-01) | The mansard slope, the dormer windows and the white party-wall fins are all invisible. Above the balustrade the sky shows only chimney stacks and the flat grey lids of a few dormers (crop of x 360-1100, y 240-560). The building sits in the lower right of the frame below about 35% empty sky. The source front shows a continuous slate mansard with a dormer row and fins rising above the balustrade along the whole long front. The south face also runs off the right frame edge, with a cut tree fragment at x≈1430. The earlier finding (v002 P1) is therefore only partly fixed. | The camera is still close and almost at ground level: the horizon sits at y≈785 and the building base at y≈800. Combined with a mansard that springs behind a gutter at moderate pitch (see #2), the parapet hides the roof. | Raise the eye to about 1.6 m and pull back about 1.4-1.6x along the same SW bearing, so that the cornice sits near 30-35% from the top and the full mansard band with its dormers and fins shows above the balustrade. Then re-check against the source framing, where the long porch front fills the left two-thirds. Fixing #2 also fixes this. |
| 2 | P1 | front_corner, aerial, mansard_dormers, architecture_close, end_pediment (vs oblique, top) | The lower roof slope is a broad, moderate-pitch plane, roughly 30-40°. It reads as a hipped slate roof, not a steep Nash mansard. The dormers have to be long tunnel boxes about 2-3x deeper than they are wide to reach the slope (front_corner crop, mansard_dormers). In the oblique source the mansard is a steep slate band directly behind the balustrade with short, compact dormers, then a break to the shallow lead top. In plan the render's outer slope runs about 21% of the block width against about 12% in the top source. | The lower slope pitch is too low and its run too long. The break to the upper lead slope is set too far inboard. | Steepen the lower mansard to about 65-75° and spring it at the cornice or balustrade line. Move the break outward to about 12% of the block width and keep the shallow upper (lead) slope beyond it. Shorten the dormer bodies to suit the steeper slope. Re-render front, front_corner, mansard_dormers and top. |
| 3 | P1 | facade_close, porch_balcony, east_side, front_corner | Every ground-floor window head shows a row of solid black squares, one where each radiating voussoir strip crosses the horizontal rustication channel (porch_balcony crop at x 1080-1440, y 420-560; facade_close at y≈790-800 on every bay). These are the same class of black void that v002 had at the coping. They show at mid distance on whole facades. | The voussoir strips are thinner than the channel is deep, or they stop at the channel face. The recessed channel's back face or its unlit void shows through at each crossing. | Run each voussoir strip through the channel to the wall plane, or fill the channel locally behind the fan. Alternatively cap each strip so that it sits proud across the groove. Verify that there are no black pixels in the porch_balcony and facade_close crops. |
| 4 | P1 | giant_order, facade_close, architecture_close, end_pediment | Every Corinthian capital shows a dark crescent or seam between the top of the bell and the underside of the abacus. The abacus reads as hovering on the corner-volute blocks, not resting on the bell (giant_order crop at x 480-780, y 420-620; facade_close at y≈265-300; architecture_close at y≈690). The acanthus is a ring of splayed rectangular sticks, so in the detail views the capital reads as a spiky crown, not a Corinthian bell with volutes. | The bell cylinder is shorter than the gap to the abacus, or it has an open or recessed top. The leaves are loose box primitives. | Extend the bell to touch the abacus soffit and close its top. Replace the stick leaves with two tiers of curved or tapered leaf blocks hugging the bell, plus four diagonal corner volutes under the abacus horns. Re-render giant_order and facade_close. |
| 5 | P2 | porch_balcony | Thin black slivers appear under the balcony pedestals where they meet the slab (x≈960-1000, y≈330; x≈1090, y≈365). Short black slits also show between the paired column caps at the porch soffit (x≈440 and 805, y≈455-470). | Small coplanar gaps between the pedestal base and the slab, and between adjacent abaci. | Extend the pedestal bases into the slab, and merge the paired-column abaci into one plinth under the beam. |
| 6 | P2 | top, aerial, front_corner (vs top) | The light court is a nearly square hole centred in the plan (about 130x160 px in the top render). In the source it is clearly elongated north-south (about 1:1.7), with inner wing roofs and rooflights. | The court is simplified to a square cut. | Elongate the court north-south to the source ratio and add simple inner roof blocks. |
| 7 | P2 | top, front_corner | The south mansard carries about 2-4 dormers against about 6 in the top source. The lead (upper) slope uses the same grey as the slate, so the slate/lead hierarchy is lost. | Dormers were placed for a sparse south row, and only one roof material is used. | Add the missing south dormers (3 each side of the pediment) and give the upper slope a lighter lead grey. |
| 8 | P2 | rear, rear_side, rear_north, left_side, right_side | The north "row of brick terrace houses" is one monolithic three-storey brick block under a single hipped roof, with tripled windows. It has no party walls, no house-by-house roofs and no brick parapets, so it reads as a warehouse. | Context massing is simplified. | Split it into 5-6 houses with party-wall parapets, individual pitched roofs and stacks, as in the top source. |
| 9 | P2 | front_corner | A street tree on the south pavement covers the lower two storeys of about three south bays, including part of the porch. | Tree placement. | Shift it about two bays west or east, clear of the porch. |
| 10 | P2 | front | The south (right) face runs off the frame edge with a cut tree fragment. The source also crops its right return, so this is not a camera failure, but it adds to the off-balance framing in #1. | Framing. | This resolves with the camera fix in #1. |
| 11 | P2 | end_pediment, facade_close | The tympanum carries three blank rectangular blocks (sculpture placeholders). This is acceptable clay. | Simplified sculpture. | Optional: one low-relief block group. |
| 12 | P2 | front_corner, mansard_dormers | The fins are long white slabs that run the full depth of the shallow slope up to the stacks near the ridge. This exaggerates the white striping compared with the short fins on the steep mansard in the source. | A consequence of #2. | This resolves with #2. |

Note on orientation (not a defect): the brief text places the porches on a long south front and the pediments on the east and west ends. The governing top source, however, shows the fins and dormer rows on the east and west sides and a single central pediment on the south edge. The build follows the top source: porch fronts face west and east, and the pediment faces south. The north side is a party wall, so no second pediment would be visible. I accept this as plan-conformant.

## 3. Source conformance checklist

| item | status | view used |
|---|---|---|
| Silhouette | deviates: the roof reads as a low hipped mass, not a tall steep mansard band (#2) | front_corner, front, end_pediment vs oblique/front |
| Storey count | conforms: basement area, rusticated ground floor, tall first floor, shorter second floor, mansard with dormers | east_side, facade_close |
| Plan and light court | partly conforms: rectangular block, streets on S, E and W, terrace on N. The court is square, not elongated (#6) | top, aerial vs top |
| Rustication | conforms in banding and voussoir fans; deviates through the black voids at the voussoirs (#3) | porch_balcony, facade_close |
| Giant order (columns, capitals, rhythm) | rhythm conforms (one engaged fluted column per bay pier through first and second floors). Capitals deviate (#4) | east_side, giant_order |
| Entablature and cornice | conforms: architrave, frieze, modillion cornice continuous round the corners | architecture_close, giant_order |
| Balustrade and pedestals | conforms: pedestals over the columns, balusters between, corner pedestals clean | architecture_close, east_side |
| Porches and balconies | conforms: three porches of paired Tuscan columns per long front, with balustraded balconies. Coping corners now clean; minor slivers (#5) | east_side, porch_balcony |
| End pediments | conforms to the top source: one central pediment on the south end over the giant order (see orientation note) | facade_close, end_pediment |
| Windows (sizes per floor, balconettes, heads) | conforms: tall first floor with iron balconettes and cornice heads, shorter second floor, reveals with depth | glass_close, east_side, interior |
| Mansard (dormers, fins, stacks, flat top) | deviates: pitch too low and dormers too deep (#2), south dormers sparse (#7), single roof colour (#7). Fins and stacks are present | mansard_dormers, front_corner, top |
| Areas and railings | conforms: iron railings along the pavement edge with a set-back area strip | front_corner, porch_balcony, east_side |
| Streets and trees | conforms: streets on S, E and W, pavements, lamps, trees (one tree poorly placed, #9) | top, aerial, front |
| Terrace houses north | deviates (P2): one monolithic block (#8) | rear, rear_side |
| Materials hierarchy | mostly conforms: cream stucco, grey slate, black ironwork, brick context, orange pots. Lead and slate are not differentiated (#7) | aerial, mansard_dormers |

## 4. Camera validity

- **front**: the target is not occluded, but its identity is not legible. The mansard, dormers and fins, which the source front shows, are entirely hidden, and the south face is clipped at the right edge. This is invalid as a match to the source front and is counted as P1 #1, not P0, because the stucco palace front with its order, porches and balustrade is still legible.
- **left_side, right_side, rear, aerial**: the building fills only about 40-45% of the frame width, but it is unclipped and legible. Acceptable.
- **interior**: legible. Window reveals and the balconettes outside are visible.
- **rear_north**: legible. It shows the party-side roof over the brick terrace.
- **All detail views**: the target is unoccluded and unclipped where intended.

## 5. Previous-version findings (v002) in the pixels

1. **Black voids where the coping meets the corner pedestals on every porch balcony and at the main parapet corners**: **resolved.** In porch_balcony every balcony pedestal now rises above the rail with its own cap, and the coping dies into the pedestal faces with no black pixels. The main parapet corner in architecture_close and the corners in front_corner are also clean. However, new black voids of the same class appear at the ground-floor voussoir crossings (#3) and as small slivers under the balcony pedestals (#5).
2. **Front render not matching the source front**: **not resolved.**
   - The camera now stands in the south-west, with the long west porch front receding left and the south end to the right.
   - The street trees have moved along the west front, clear of the corner order.
   - The pediment end no longer dominates; the pediment is small at the far right.
   - The mansard, dormers and fins are still hidden behind the balustrade. The camera is still very low (horizon about 15 px above the building base) and close, with about 35% empty sky above, and the right face is clipped.

   The core of the finding, a front that does not show the roof grammar the source front shows, persists (#1).
