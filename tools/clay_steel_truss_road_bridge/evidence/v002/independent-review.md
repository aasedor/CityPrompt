# Independent holistic review: clay-steel-truss-road-bridge v002 (RLASM v6.1 architectural clay)

Reviewer: independent; I did not build this candidate. I judged only rendered pixels against the three locked sources (sources/front.png, sources/oblique.jpg, sources/top.jpg). I opened all 18 renders at full resolution, plus the four phone boards. I made zoomed crops only in the new folder /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/review-crops-trussbr-v002-439610582 (left_side, top ends, front bottom-right, aerial right end).

## 1. Verdict

**PASS_ZERO_P0_P1**: the pixels show a single-span rust-orange riveted Pratt through-truss. It has inclined end posts, double-lattice portals, three long X-bays of top laterals between four struts, a two-lane road, sidewalks with rails outside the trusses, and brick abutments on concrete quays. The five v001 blockers (the front camera, the truss web, the lateral bay count, the quay kerb across the road, and the occluded rear truss) are resolved in the renders. What remains is P2 polish.

Counts: P0 = 0, P1 = 0, P2 = 13

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P2 | portal_frame, front, roadway_inside | Portal knee braces are straight bars from end post to lower portal strut. The oblique source shows a curved (arched) knee brace under each portal. | Knee brace authored as a straight box (builder left it unchanged). | Replace each knee brace with a 6–8 segment arc from the end post to the portal strut, at the same section. |
| 2 | P2 | river_underside | The underside is still crushed near-black. Floor beams and the soffit read only as silhouettes, though the beam grid and quay walls are legible. | No fill or bounce light under the deck, plus low exposure on this camera. | Raise exposure for this view by about 1 stop, or add a weak area fill below the deck. |
| 3 | P2 | rear_north, front, aerial, left_side | The end-post feet and bottom-chord ends sit straight on the deck or bottom chord, with no bearing shoe or seat on the abutment. | Bearings were not modelled (unchanged). | Add a simple shoe plate and seat block under each of the 4 end-post feet. |
| 4 | P2 | top | In plan the top chords are thin lines, about 5% of truss spacing. The top source shows chords about 10%, so the chord frame reads weaker than the lateral X's. | Top-chord plan width unchanged. | Widen the top-chord cover plate to about 2x its current plan width. |
| 5 | P2 | architecture_close, deck_sidewalk | Sidewalk concrete shows soft, blotchy white and grey patches that do not line up with any member shadow. | Noisy or denoised soft shadows from the truss and railing on a bright surface (unchanged). | Raise samples for these views or reduce the light size; check that the sidewalk has no overlapping coplanar faces. |
| 6 | P2 | glass_close, facade_close, rear_north | Gusset rivets are a few (about 6 per plate) large square nubs. In the sources they are dense rows of small round heads, so close-ups read as bolted. | Rivet instancing is too coarse, and the heads are cubes. | Use small domed or octagonal heads in 2–3 rows at about half the current pitch. |
| 7 | P2 | abutment, aerial, left_side, right_side | The stepped wing pilasters are smooth, uncoursed brown slabs next to the brick-coursed abutment face. A black slot shows between the pilaster tops and the quay coping. | Pilaster material lacks the brick pattern, and the coping does not meet the pilaster top. | Apply the abutment brick material to the pilasters, and close the coping so it sits on the pilaster tops. |
| 8 | P2 | top, rear_north, roadway_inside | The dark deck expansion joint is at the quay edge, but the truss end posts and bottom chords run about 3 m further onto the approach slab. The white stop lines fall inside the truss footprint, between end-post foot and portal. In the top source the transverse line sits just beyond the truss end. | Joint keyed to the quay line, not to the end floor beam. Stop line placed relative to the joint. | Move the joint to the end floor beam at the end-post feet, and the stop line about 1–2 m beyond it on the approach. |
| 9 | P2 | left_side, right_side, rear_side, aerial, facade_close | Rust floor-beam ends hang below the white deck fascia as six isolated boxes in every elevation. The source front shows a clean concrete deck edge over the brick abutment. | Floor beams extend past the fascia line, or the fascia is not deep enough to hide them. | Stop the floor beams inside the fascia, or deepen the fascia to cover them. |
| 10 | P2 | top | Sidewalks are about 0.21 of the truss spacing (source about 0.12), and the truss sits almost on the outer lane line, with no shoulder. Overall bridge width to river width is 0.65 against 0.54 in the source. | Sidewalk width parameter is generous and the shoulder is omitted. | Narrow the sidewalks by about 30% and add a shoulder of about 0.4 lane between the truss and the edge line. |
| 11 | P2 | top, rear, deck_sidewalk | The sidewalk railings run on about 9 m along the approaches as freestanding fences between the sidewalk and the quay promenade. In the oblique source the bridge rail turns onto the quay at the bridge end and the approach sidewalk is open. | Railing extension added as a v002 fix. | End the approach rail at the quay wall corner and return it along the quay edge. |
| 12 | P2 | front_corner | The near-left end-post foot is still only about 20 px above the bottom frame edge. | Camera target or framing only slightly loosened. | Tilt up or pull back by about 3% of the frame height. |
| 13 | P2 | truss_panel, facade_close, left_side | The flat-bar counters are only marginally slimmer than the mains, so the X panels read as two equal heavy diagonals at close range. In the source front the counters are clearly lighter. | Counter section too close to the main section. | Cut counter width to about 50–60% of the mains. |

No P0 or P1 findings.

## 3. Source conformance checklist

| Item | Status | View(s) used | Note |
|---|---|---|---|
| Plan and proportions | conforms (P2 #10) | top vs top source, aerial | Single span north–south over an east–west river. Truss length to truss spacing is about 2.7 against about 2.85 in the source. River clear width to truss length is 0.84 against 0.85. End posts land about 3 m behind both quay edges, on land. Sidewalks are a little wide. |
| Truss type and panel count | conforms | left_side (crop), right_side, rear_side, aerial, facade_close | Pratt with 7 panels: two end-post triangles plus 5 top-chord panels. Mains slope down toward midspan. Crossed counters are in the three middle panels, with single mains in the panels beside each hip vertical. Hip verticals are plain; intermediate verticals are laced, as in the source front. |
| End posts | conforms | front, rear, portal_frame, rear_north, left_side | Heavy inclined box end posts at all four corners, visible in full in front and rear. |
| Top chord and bracing | conforms (P2 #4) | top, roadway_inside, portal_frame, front_corner | Four struts (two hip struts and two at the thirds) and three long, near-square X-bays with a gusset plate at each crossing, matching the top source's 3 X-bays. Top chord is thin in plan. |
| Portal frames | conforms (P2 #1) | portal_frame, front, rear | Double lattice portal at each end with knee braces, as in source front and oblique. The knee braces are straight where the source has curved ones. |
| Deck and lanes | conforms (P2 #8) | rear, roadway_inside, top, front | Two lanes with a double yellow centre line and white edge lines. Road and deck meet flush, and the v001 raised kerb bar is gone. The joint and stop-line positions are slightly off. |
| Sidewalks and railings | conforms (P2 #5, #11) | deck_sidewalk, front, left_side, facade_close | Cantilevered sidewalks outside both trusses with vertical-baluster steel rails. The approach rails run on too far. |
| Abutments and quays | conforms (P2 #3, #7) | abutment, front (crop), aerial (crop), left_side | Brick abutment faces under the deck, with a concrete cap, concrete quay walls and stepped brick wing pilasters. The deck bears over the abutment. There are no bearings, and the pilasters have no brick coursing. |
| River | conforms | left_side, right_side, aerial, top | Dark water channel between vertical quay walls, with no contact defects at the waterline. |
| Context | conforms | aerial, front_corner, rear, oblique board | Simplified multi-storey brick warehouses at the quay corners, plus street trees and simple vehicle masses with opaque cabins. Appropriate for clay context. |
| Materials hierarchy | conforms | front, left_side, aerial | Steel is a clearly more orange rust than the darker warehouse brick. Concrete deck, sidewalks and quays are light grey and the road is dark grey. Hierarchy reads at phone-board scale. |

## 4. Camera validity

- **front**: valid. The camera stands outside the railing at the quay corner. The whole near portal and inclined end post are in frame, the top chord has about 160 px margin, and the far end post, sidewalk rail, brick abutment, wing pilaster and water are visible. The composition matches the source front's role.
- **front_corner**: valid. The near foot is tight to the bottom edge but not clipped (P2 #12).
- **aerial, top, left_side, right_side, rear_side**: valid. The whole envelope is in frame with margin.
- **rear**: valid. Both trusses, both end posts and both feet are unobstructed; vehicles are small and between the trusses.
- **Detail views** (facade_close, architecture_close, glass_close, portal_frame, truss_panel, deck_sidewalk, abutment, roadway_inside, rear_north): valid and legible. Cropping of members is intentional for detail framing.
- **river_underside**: valid but dark (P2 #2). Its targets (beam grid, soffit, quay walls) are still identifiable.

No view has its target occluded, clipped so that identity is lost, or illegible.

## 5. Previous-version (v001) findings: resolved in the pixels?

| v001 finding | Severity | Resolved? | Evidence |
|---|---|---|---|
| Front camera inside the portal bay; top chord, end post, portal, abutment and river out of frame | P0 | **Resolved** | front: camera on the quay corner. Whole near portal and end post, top chord with margin, far end post, rail from bottom, brick wing pilaster and water at bottom-right. |
| Truss web plain Pratt with crossed diagonals only in the centre panel | P1 | **Resolved** | left_side crop, facade_close, aerial: crossed counters in the three middle panels; single mains in the panels beside the hip verticals. |
| Overhead laterals 5 short X-bays between 6 struts | P1 | **Resolved** | top: 4 struts and 3 long near-square X-bays with crossing plates, matching the top source. |
| Raised light-grey kerb bar across the carriageway at each end | P1 | **Resolved** | rear, roadway_inside, top, front: road and deck flush, no transverse bar. White stop line on the incoming lane (joint and stop-line placement now P2 #8). |
| Rear: bus and car hid the right truss and its end-post foot | P1 | **Resolved** | rear: both trusses, end posts and feet unobstructed. |
| Proud castellated top-chord gussets with dark recessed-looking rivets | P2 | Resolved (castellation); rivet coarseness remains P2 #6 | glass_close, facade_close: plates flush with the chord top, raised steel-coloured heads. |
| Steel and warehouse brick nearly the same colour | P2 | Resolved | front, left_side: orange steel against darker brick. |
| All diagonals as heavy as verticals; laced hip verticals | P2 | Partly resolved | Hip verticals are plain, but counters are only marginally slimmer (P2 #13). |
| Straight portal knee braces; no plates at lateral X crossings | P2 | Plates resolved; knee braces **not** resolved (P2 #1) | portal_frame, roadway_inside. |
| Translucent ghost car cabins | P2 | Resolved | portal_frame, roadway_inside: opaque dark cabins. |
| Blotchy sidewalk shadows | P2 | **Not resolved** (P2 #5) | architecture_close, deck_sidewalk. |
| Crushed-dark river_underside | P2 | **Not resolved** (P2 #2) | river_underside. |
| front_corner near foot touching the bottom edge | P2 | Improved, still tight (P2 #12) | front_corner. |
| Thin top chords and white quay copings in plan | P2 | Copings resolved (brick-red); thin chords **not** resolved (P2 #4) | top. |
| End-post feet without bearings | P2 | **Not resolved** (P2 #3) | rear_north, aerial. |
