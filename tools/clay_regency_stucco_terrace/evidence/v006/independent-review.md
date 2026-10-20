# Independent holistic review: regency v006 (RLASM v6.1 architectural clay)

Reviewer: independent; did not build this candidate. I judged rendered pixels only, against `sources/front.png`, `sources/oblique.jpg` and `sources/top.jpg`. I opened all 18 renders at full resolution, all four phone boards and the three sources. I made zoomed crops only in a new folder: `/tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/regency-v006-indep-crops-6111028f/`.

## 1. Verdict

**VISUAL_REWORK_REQUIRED.** Both v005 roof findings are fixed in the pixels. Two P1s remain:
- The block plan and the light court are compressed north–south against the governing top view.
- The new court box dormers have windows that render as blank pale panels, with no glass, bars or reveal.

Counts: P0 = 0, P1 = 2, P2 = 12

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | top, aerial, front_corner, left_side, right_side (vs source top, oblique, front) | **The plan is shallow north–south and the court is too square.** On top.png the block is about 500 px N–S by 620 px W–E (depth/width about 0.81). The source top is about 478 by 510 (about 0.93–0.95). The court opening measures about 160 px N–S by 138 px W–E (about 1.16:1); the source court is a long N–S slot of about 185 by 115 (about 1.6:1). Court depth is about 33% of block depth against about 39% in the source. The porch fronts (W/E, about 11–12 bays) also read shorter than the pediment front (S). Both the front and oblique sources show the porch front as the longer face. | Block depth and court length were set short, or the W/E fronts have too few bays. The roof-share fix was measured only against block *width*, so the N–S error never surfaced. | Add about 13–15% to the N–S depth (1–2 bays on each W/E porch front, keeping porch and fin spacing even). Lengthen the court N–S to about 1.5–1.6:1 and keep the per-side roof shares already achieved. Re-render top, aerial, front_corner, left_side and right_side, and re-check against the source top. |
| 2 | P1 | front_corner, aerial, mansard_dormers, rear_side, rear_north | **Court box-dormer windows read as blank panels.** Each of the four big box dormers shows two tall, flat, uniform pale rectangles with no glazing bars, frame or reveal shadow. Sampled pixels are (146–151, 148–153, 148–153), the same as the backdrop sky (151, 156, 159). The street dormers' glass beside them reads dark (38–45). They look like white shutters or boards, not windows. This is an opening without visible depth on the feature added to fix v005 #2. | The glazing is set flush in the dormer cheek and uses a mirror-like glass that reflects the flat grey environment at grazing angles. There is no frame or sash bar. | Recess the glazing about 0.15 m behind a white frame with a meeting rail and a centre bar, and use the street-dormer glass material. Confirm the panes read darker than the slate in front_corner and mansard_dormers. |
| 3 | P2 | architecture_close, front, front_corner, mansard_dormers, rear_north, east_side | Small solid-black cubes sit at every hip and lead-band corner. They are about 25 px in architecture_close and visible as black dots in every whole-envelope view. | Corner caps or roll ends use an unlit or black material. | Give the caps the lead material, or delete them. |
| 4 | P2 | porch_balcony, east_side | Black hairline slits show between the paired Tuscan abaci and at both ends of the porch balcony slab where it meets the wall band. | Small modelling gaps that show the void behind. | Close the seams by merging or overlapping the abacus blocks and seating the slab into the wall. |
| 5 | P2 | end_pediment, facade_close | A thin dark wedge runs under the left raking cornice of the pediment. At the apex the left raking member rides over the right one (mitre mismatch). | Tympanum top edge stops short of the soffit; raking members are not mitred. | Extend the tympanum to the soffit and mitre the apex. |
| 6 | P2 | facade_close, giant_order | The two balustrade pedestals beside the pediment sit about half a column width off the column axes below. Every other pedestal aligns. | Pedestals placed at the pediment ends, not on the column axes. | Snap them to the column centre lines. |
| 7 | P2 | glass_close, facade_close | Balconette side-return stubs poke out sideways past the end standards. | Return bars are too long or not rotated back to the wall. | Trim the returns to meet the reveal. |
| 8 | P2 | front_corner, aerial, mansard_dormers | The rooflights on the N/S inner slopes read as tilted half-black, half-white slabs that seem to stand proud of the slate, not flush lights. | Glass reflection split plus a raised frame. | Lower them flush and use a dark glass with a thin lead frame. |
| 9 | P2 | rear, rear_side, top, left_side, right_side | The north terrace is one hipped brick block with a uniform window grid. It has none of the house-by-house parapets, party-wall stacks or roof breaks seen in the source top and oblique. | Context massing simplified to one box. | Split it into 4–5 houses with parapets and stacks on the party walls. |
| 10 | P2 | top, east_side, left_side | Each W/E mansard has three white fins with stacks. The source top shows two per side. | Fin spacing tied to the bay count. | Re-space to two per side, or accept as coherent (front source shows more). |
| 11 | P2 | porch_balcony, east_side, facade_close | The Tuscan porch shafts are visibly faceted (polygonal), with almost no echinus or abacus capital. | Low segment count; capital collapsed into a block. | Raise the segment count and add a simple echinus and abacus. |
| 12 | P2 | giant_order, architecture_close | The Corinthian capitals pass the brief: closed bell meets the abacus, two leaf tiers, corner spurs. But the leaves are flat cut planks and the volutes are straight spurs, not scrolls. | Low-detail capital proxy. | Optional: curl the volute spurs and soften the leaf tips. |
| 13 | P2 | left_side, right_side, rear, aerial | The building fills only about 37–48% of the frame width, with a large empty foreground. It is legible, but framing is loose. | Camera distance and FOV. | Tighten FOV or distance so the block fills about 70% of the width. |
| 14 | P2 | boards/phone-01 | Board 1 pairs the locked top with render *aerial*. The top-vs-top comparison appears only on board 4, without its source. | Board layout. | Pair locked top with render top on board 1. |

Note, not a finding: the brief's compass wording puts the porches on the south and pediments on the E/W ends. The render has the porches (and fins) on the W/E fronts and one central pediment on the S front. This matches the source pixels: in the oblique, porches and fins share a face and the pediment is on the adjacent face, and the top places the fins on W/E. I judged against the pixels.

## 3. Source conformance checklist

| Item | Status | View(s) used |
|---|---|---|
| Silhouette | conforms (block, balustraded cornice line, mansard with fins and stacks) | front, front_corner, east_side |
| Storey count | conforms: basement areas; rusticated ground floor; two storeys inside the giant order; mansard with dormers | facade_close, east_side, front |
| Plan and light court | **deviates**: block about 0.81 depth/width vs about 0.94 in the source; court about 1.16:1 vs about 1.6:1 (finding 1). Court dressing (box dormers, inner slopes, coping, cream walls with windows) now conforms. | top, aerial, front_corner |
| Rustication | conforms: channelled ground floor; channels stop at the voussoir fans; no black squares | facade_close, porch_balcony, east_side |
| Giant order (columns, capitals, rhythm) | conforms: fluted engaged columns between every bay, coupled at the corner; capitals have a closed bell, two leaf tiers and corner spurs (crude, P2) | giant_order, architecture_close, front |
| Entablature and cornice | conforms: architrave and frieze band, modillion cornice | giant_order, architecture_close |
| Balustrade and pedestals | conforms; two pedestals by the pediment are off-axis (P2) | east_side, facade_close, mansard_dormers |
| Porches and balconies | conforms: paired Tuscan columns carry stone balustraded balconies, three per W/E front plus one under the S pediment; shafts faceted (P2) | east_side, porch_balcony, facade_close |
| End pediment | conforms: central pediment over the giant order on the S front; tympanum relief simplified to panels (clay) | end_pediment, facade_close, front |
| Windows (sizes per floor, balconettes, heads) | conforms: tall first-floor windows with cornice heads and iron balconettes; shorter second-floor windows; ground floor with voussoir fans; recessed with reveals (interior shows depth) | facade_close, glass_close, interior |
| Mansard (dormers, fins, stacks, flat top) | conforms on the outer roof: steep slate band with short dormers, broad upper slate, narrow ribbed lead ring, white fins with stacks. **Court box-dormer glazing deviates** (finding 2). Fin count 3 vs 2 per side (P2). | mansard_dormers, top, front_corner, architecture_close |
| Areas and railings | conforms: iron railings along the pavements with areas behind | front, facade_close, porch_balcony |
| Streets and trees | conforms: streets on S, E and W; street trees and lamps (low-poly clay) | top, front, aerial |
| Terrace houses north | deviates (P2): one generic hipped brick block, no house rhythm | rear, rear_side, top |
| Materials hierarchy | conforms: cream stucco, blue-grey slate, paler lead ring, black iron, brick context, orange pots | front_corner, mansard_dormers, front |

## 4. Camera validity

- No view has the target occluded or clipped, and none is illegible.
- **front:** valid. The mansard, dormers and white fins show above the balustrade. The whole west porch front (to the terrace junction) and the south pediment end are in frame. Two trees partly cover the northern first-floor bays, which is acceptable.
- **rear:** shows mainly the north terrace. This is expected, because the north is the party side.
- **left_side, right_side, rear, aerial:** framing is loose; the building fills less than half the width (P2, finding 13).
- **Details** (facade_close, architecture_close, glass_close, porch_balcony, giant_order, end_pediment, mansard_dormers, east_side, interior, rear_north): each frames its subject legibly.

## 5. Previous-version findings: resolved in the pixels?

| Finding | Status | Evidence |
|---|---|---|
| v005 #1: slate and lead swapped (about 75% pale lead) | **Resolved** | On top.png, west side as a share of block width: outer slate (steep band plus upper slope) about 12%, ribbed lead about 7%, inner slate about 13%. The source is about 13 / 8 / 12. The lead is now a narrow ribbed ring; the broad outer and inner slopes are smooth slate. The same split shows in front_corner, aerial, mansard_dormers and rear_north. |
| v005 #2: court under-scaled (lead ring and blue wall into a hole) | **Largely resolved** | Four large box dormers, about 2.5–3 times street-dormer width, stand on broad W/E inner slate slopes. A stone coping runs over the court wall tops. The cream court walls with dark sash windows are visible below in aerial and front_corner. Residual defects: the box-dormer glazing reads as blank panels (new P1, finding 2), and the court is too square in plan (P1, finding 1). |
| Front camera shows mansard, dormers and fins with the whole west porch front and south end | **Holds** | front.png |
| Outer lower mansard is a steep slate band with short dormers high on it | **Holds** | mansard_dormers, architecture_close, east_side |
| Rustication channels stop at the voussoir fans, no black squares | **Holds** | facade_close, porch_balcony. There are black corner cubes on the roof hips, but that is a different element (P2, finding 3). |
| Corinthian capital: closed bell touching the abacus, two leaf tiers, corner volutes | **Holds** (crude) | giant_order zoom |
| v004: court roof carries dormers and rooflights | **Holds** | Box dormers on W/E, two rooflights on N, two rooflights plus a skylight on S (top, front_corner, rear_north). Rooflight finish is P2 (finding 8). |
