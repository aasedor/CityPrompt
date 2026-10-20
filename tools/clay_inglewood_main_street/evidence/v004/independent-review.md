# Independent holistic review: clay-inglewood-main-street v004 (RLASM v6.1)

Reviewer: independent; judged only on rendered pixels against the locked sources (`sources/front.png`, `sources/oblique.jpg`, `sources/top.jpg`). I opened all 18 renders at full resolution, the 4 phone boards, and zoomed crops (written only to `/tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/ingle-v004-indrev-crops-f471081d/`). Builder notes, metadata and hashes were not accepted as proof. I also scanned every render for near-black clusters (luma < 14). The only hits were the dark metal cornice, car tyres, lamp poles, bins and the shaded sides of tree crowns. No void was found.

## 1. Verdict

**PASS_ZERO_P0_P1.** The v003 P1, a black slot at the end-block/east-neighbour junction, is gone in right_side, aerial and phone-03. The end pier now reads as one continuous cream pier from the sidewalk to its capital. Every earlier fix still holds, and the only remaining findings are polish.

Counts: P0 = 0, P1 = 0, P2 = 7

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P2 | front_corner (x 150–360, y 600–800), corner_entrance (x 0–50, 245–300) | The piers on the corner block's main-street face and the corner pier are now brick with stone caps and plinths. The cross-street face still has two full-height cream/stone pilasters between its storefronts. The source oblique shows brick piers on that face too, so the claim "corner block piers brick" is only partly carried out. | The pier material swap was applied to the main-street pier list and the corner pier, but not to the side-face piers. | Switch the cross-street face piers to brick with stone cap and plinth, matching the main face. |
| 2 | P2 | front, sidewalk_section, angle_parking, street_furniture | The narrower street-tree crowns now read as tall, faceted columns with a notched double-lobe top, close to a cypress/poplar shape. The source's young trees have small rounded leafy crowns. | The crown was narrowed by scaling the faceted mesh in x/y only. | Use a rounder, slightly squatter crown of about the same width, or blend two or three overlapping spheroids. |
| 3 | P2 | rear (x 1040–1080, y 735–760; x 0–90, y 740–790) | The lower bay's lane window, sill and door now clear the context roof. The bottoms of the ground-floor lane openings on the middle block's west end and on the far-left blocks are still cut by the foreground context roofs. | The camera was raised only enough for the lower bay. | Optional: raise or pull back slightly more, or lower the near context boxes a little. |
| 4 | P2 | storefront_close (x 700–1210, y 610–690) | A soft pale smear floats across two panes at mid-height. It is a blurred reflection that reads like a fogged band. | The glass reflects a bright context surface through a glossy shader. | Raise glass roughness slightly or dim the reflection of the context. |
| 5 | P2 | aerial | The south-side context boxes take up the lower-left 35–40 % of the frame. The north street wall is fully legible, but it sits in the upper-right half. | Camera placement over the south row. | Optional: pan or tilt a little to centre the street section. |
| 6 | P2 | renders/ folder | The brief's detail list names `facade_close`, `architecture_close` and `glass_close`, but none exist. The folder holds exactly 18 renders, which matches the brief's "18 views". Their roles are covered by storefront_close, arched_windows and bracketed_cornice. | The brief's list is a template carry-over, or those cameras were dropped. | Align the brief's view list with the 18-camera set, or add the three cameras. |
| 7 | P2 | right_side (end pier, about y 805), aerial | There is a barely perceptible tonal hairline across the end pier where the ground stage meets the upper stage. Width is continuous and nothing at the junction is dark or open. | Two coplanar pier pieces with a hairline shading difference at the joint. | Merge them into one pier mesh, or add a small stone string at the joint. |

There are no P0 or P1 findings.

## 3. Source conformance checklist

| item | status | view(s) used |
|---|---|---|
| Section order (storefronts / sidewalk / brick furnishing strip / 50° angled parking / travel lane / double yellow / travel lane / parking / strip / sidewalk, mirrored) | conforms | top, angle_parking, right_side |
| Section widths (sidewalk ≈ 2× strip; parking ≈ sidewalk + strip; two lanes ≈ 1.5× parking, compared against source top) | conforms | top vs source top |
| Curb extensions and tapers (pale scored concrete, brick band along the curb, reverse-curve tapers) | conforms | front, top, right_side, crosswalk_bulbout |
| Angled stall lines and edge line | conforms | angle_parking, top, front_corner |
| Double yellow centre line | conforms | angle_parking, crosswalk_bulbout, right_side |
| Brick crossings with white edge lines at the intersection (both streets) | conforms | crosswalk_bulbout, left_side, top |
| Mid-block white ladder crossing over a brick band | conforms | right_side, top, front, aerial |
| Sidewalk scored joints | conforms | front, sidewalk_section, top |
| Brick furnishing strip and tree pits | conforms | angle_parking, street_furniture |
| Young street trees | conforms (crown shape P2 #2) | front, sidewalk_section, top |
| Black lamps with red banners | conforms | crosswalk_bulbout, angle_parking, right_side |
| Bins | conforms | angle_parking, sidewalk_section |
| Bike hoops | conforms | street_furniture, sidewalk_section |
| Benches (on brick pads at the curb extensions) | conforms | crosswalk_bulbout, left_side, top |
| Corner block: 3 bays of paired upper sashes split by a pier | conforms | corner_entrance, front_corner |
| Corner block: stone belt and white cornice turning the corner | conforms | corner_entrance, front_corner, left_side |
| Corner block: side shopfronts on the cross street | conforms | corner_entrance, left_side, rear_side |
| Corner block: corner pier (brick with stone cap and plinth) | conforms; side-face piers still stone (P2 #1) | front_corner crop, corner_entrance |
| Lower bay (one storey, membrane roof, two storefronts, sign band, stone cornice) | conforms | front_corner, top, rear |
| Middle block: cream pilasters and cream sign band | conforms | storefront_close, right_side, front |
| Middle block: segmental upper windows with stone rings | conforms | roof_parapets, right_side |
| Middle block: modillioned white cornice | conforms | front, roof_parapets, right_side |
| Middle block: raised stepped central parapet with a light-stone name panel | conforms | roof_parapets, front, right_side |
| Middle block: exposed west wall with four framed upper windows | conforms | front_corner |
| Bracketed-cornice block (dark metal cornice with brackets and consoles, segmental windows, dark sign band) | conforms | bracketed_cornice, front, right_side |
| Round-arched block (round-arched windows in brick voussoir rings, corbelled brick cornice) | conforms | arched_windows, front, right_side |
| End block (tallest; cream stone fascia; tall flat-headed windows; cream end pier continuous to grade) | conforms | front, right_side, aerial, front_corner |
| Storefront glazing, transoms, panelled bulkheads, recessed glazed doors | conforms | storefront_close, corner_entrance, sidewalk_section, front |
| Blade signs | conforms | corner_entrance, sidewalk_section, right_side |
| Roofs and parapets (flat roofs inside brick parapets; pale membrane on the lower bay and end block) | conforms (clay: no gravel texture, as expected) | top, roof_parapets, rear, aerial |
| Back lane (lane surface, coursed-brick rear walls, framed openings with lintels and sills; lower-bay door and window separate) | conforms | rear, rear_lane, rear_side |
| South-side context (plainer two-storey brick row) | conforms | front, right_side, sidewalk_section |
| Materials hierarchy (red brick field; cream/stone trim; dark green storefront frames; dark metal cornice; pale concrete; red brick paving) | conforms | all |
| Awnings, pedestrians, dogs | correctly not modelled | — |

## 4. Camera validity

- All 18 renders are valid. No target is occluded or clipped, and every subject is legible.
- aerial: the south context takes up a lot of the frame, but the street wall is legible (P2 #5).
- rear: the lower bay lane wall is fully clear. Small partial occlusion of other ground-floor lane openings remains (P2 #3).
- left_side: the closer framing down the cross street is in place. The corner block, its corner, the side shopfronts and the intersection crossings are all legible.
- The brief names three detail views that do not exist (facade_close, architecture_close, glass_close). The renders folder matches the brief's stated count of 18, and the roles are covered by other close-ups (P2 #6).

## 5. Previous-version findings: resolved in the pixels?

**v003 P1: black slot at the end block's east pier base.** **Resolved.** right_side shows a continuous cream pier from the sidewalk to its capital, at a constant width. It butts directly onto the pink east neighbour, with no dark slot at any height (crop `rs_endpier.png`). The aerial crop (`aer_endpier.png`) shows the same, and phone-03 right_side shows no seam. Only a faint tonal hairline remains (P2 #7).

**Builder's cheap P2 claims:**
- Corner block piers brick: **partly resolved.** The main-street face and the corner pier are brick with stone caps and plinths. The cross-street face still has stone pilasters (P2 #1).
- Name panel in light stone: **resolved** (roof_parapets).
- Tree crowns about 20 % narrower: **resolved** as narrower, but the shape is now columnar (P2 #2).
- Rear camera raised: **resolved** for the lower bay. Its window and sill clear the context roof (crop `rear_lowerbay.png`).

**v003 fixes still holding:**
- Lower bay lane wall: service door and ground window are apart, each with its own stone lintel, and the window has its own sill. There is no black void and no overlapping openings on any rear wall (rear, rear_lane). **Holds.**
- Cafe/end block roof is the pale membrane (top, aerial, right_side). **Holds.**
- left_side has the closer cross-street framing. **Holds.**

**v002 fixes still holding:**
- Corner block: 3 bays of paired sashes, with the belt and cornice turning the corner. **Holds.**
- Lower bay: one storey, membrane roof, two storefronts, sign band, stone cornice. **Holds.**
- Middle block west wall: coursed brick with four framed upper windows (front_corner). **Holds.**
- Middle block segmental heads with stone rings. **Holds.**
- Round-arched brick voussoir rings. **Holds.**
- End block is the tallest, with tall upper windows. **Holds.**
- Curb extensions: pale scored concrete, brick band, brick pads, reverse-curve tapers. **Holds.**
- Rear walls: coursed brick with framed, glazed openings in reveals, on stone sills under stone lintels. **Holds.**
- v002 P2s: bulkhead panel mouldings (sidewalk_section, front), the brick band under the ladder crossing, the raised parapet and name panel, the bracket console, opaque car cabins. **All hold.**

**v001 positives still holding:**
- Section order, 50° stalls with the edge line, double yellow, brick crossings with white edges, the mid-block ladder crossing. **Hold.**
- Black lamps with red banners, bins, bike hoops, benches. **Hold.**
- The middle block's pilasters, sign band and modillion cornice. **Hold.**
- The dark bracketed cornice and the corbel table. **Hold.**
- Storefront glazing with transoms and recessed doors. **Hold.**
