# Independent holistic review: clay Vancouver Special, v002

Reviewer: independent RLASM v6.1 holistic reviewer. I judged only rendered pixels against the three locked sources (sources/front.png, sources/oblique.jpg, sources/top.jpg). I opened all 18 renders at full resolution and the four phone boards, and checked the trim joints, corners, brick and stair heads with nearest-neighbour zoomed crops and pixel sampling. The crops are in a new folder, `scratchpad/review-crops-v002-cb129a07/`. No candidate file was changed and no build was run.

## 1. Verdict

**VISUAL_REWORK_REQUIRED.** The three v001 P1s are resolved in the pixels. However, two new near-black artefacts of the same class appear (a continuous black slot under both front rake fascias, and a black pit at every brick mortar T-junction), and the locked front camera is not matched.

Counts: P0 = 0, P1 = 3, P2 = 10

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | architecture_close (also a dark seam in front, facade_close, front_apex crop) | A continuous pure-black slot, 2–3 px wide, runs the full length of the front rake, between the underside of the brown rake fascia and the white rake soffit. Sampled along the rake at x = 240…900 it is RGB (1–7, 1–6, 1–5) at every 60 px step. At whole-envelope scale it reads as a dark line (about 40–60 luminance) under both front rakes. The rear rakes do not have it: the darkest value along the rear rake is about 130. | The front rake board sits off the front rake soffit or verge, or the soffit stops short of the board's inner face, so the camera sees into the unlit roof cavity or a back face. The rear gable is built differently and is closed. | Close the front rake the way the rear rake is built. Either extend the front rake soffit or frieze strip to meet the inner face of the rake board, or drop the board's lower edge so it overlaps the soffit by at least 10 mm. Re-render architecture_close and front and confirm no pixel below about 60 luminance along the rake. |
| 2 | P1 | brick_base, entry_stair (sub-pixel and not seen in facade_close or front) | Every mortar T-junction in the brick veneer (the foot of each head joint where it meets a bed joint) shows a near-black dot. brick_base min is RGB (13, 14, 12), with 689 px below 40 luminance spread on a regular grid. The two brick detail views therefore show a regular stipple of black pits across the whole ground storey. | The head-joint and bed-joint mortar pieces overlap or end short at each T, leaving a tiny unlit void or a coplanar overlap. This is the same mechanism as the v001 black trim faces. | Model the mortar as one continuous recessed plane behind the brick units, or end the head-joint strips flush on the top face of the bed-joint strip with no overlap and no gap. Re-render brick_base and entry_stair and confirm no pixel below about 40 luminance inside the brick field. |
| 3 | P1 | front (compare with locked front, phone-01) | The front camera azimuth does not match the locked front. In the source, the east (side-street) wall is about half as wide as the street front (front about 580 px, east about 305 px, ratio about 0.53). The side-suite door, its landing and flight, both east ground openings, both east upper windows and the exposed foundation band are all large and legible. In the render, the east wall is about 70 px against about 695 px for the front (ratio about 0.10). The suite door, its stair and the east openings shrink to slivers, and the house fills about 59% of the frame width against about 94% in the source. | The camera is placed nearly on the front axis. The source is a near one-point view taken from well east of centre, about on the line of the east wall or the side-street boulevard, with the vanishing point of the east wall far to the right. | Move the front camera east until it stands roughly on the side-street sidewalk line, keep it aimed north perpendicular to the front, and use horizontal lens shift (or a wider FOV) to recentre. Target an east-to-front visible width ratio of about 0.5 and a building width of about 90% of the frame, then re-check against the locked front on the phone board. |
| 4 | P2 | front, architecture_close, rear, front_ecorner and rear_rcorner crops | The rake-foot return blocks close the corners, but each is a cube that stands above the rake and roof line, so a small brown knob shows in the silhouette at the eave corners (front 1045–1090/235–265). In the rear view, the eave gutter end profile and swan-neck sit about 8 px inboard of and below the block, with a light gap, so "one height" holds only at the front-east close-up. | The block is sized larger than both fascias and is not mitred into the eave fascia. At the rear, the gutter end is not carried into the block. | Trim the block top to the top plane of the rake fascia, and carry the eave fascia and gutter end into the block at the rear corners as well. |
| 5 | P2 | front_corner vs oblique, top vs top | The roof is a pale warm-grey taupe (median RGB about 138–149) against the source's dark brown-grey asphalt (about 92–126). The roof-to-stucco value contrast falls from about 0.57 to about 0.80, which weakens the material hierarchy. | Shingle albedo set too high, plus soft overcast lighting. | Lower the shingle base colour by about 25–30% in value, keeping a slight warm bias. |
| 6 | P2 | rear, front | The roof pitch reads at about 21° (about 4.7:12) in the rear gable elevation, a little steeper than the source's very low front gable. | Rise set slightly high. | Reduce the ridge rise to about 17–18° (about 3.5–4:12) if the plan width stays. |
| 7 | P2 | brick_base, facade_close | The ground-storey window sills are plain orange slabs with no rowlock coursing, while the surrounding wall shows brick joints. | The sill was modelled as a solid block. | Add rowlock head joints to the sill face. |
| 8 | P2 | facade_close, glass_close, brick_base | From outside, the curtains read as blue-grey panels behind glass, while the source curtains read as cream sheers. | Glass tint over the curtain panels. | Warm or lighten the curtain panels, or reduce the glass tint. |
| 9 | P2 | rear_side (and aerial) | Despite the claim that it was moved clear, the north-east tree crown still fills the bottom-centre of rear_side (about 330–960 × 760–1080). It hides the deck-post footings and the rear ground-floor window. A foreground tree also covers the front-west ground corner in aerial. | The tree was not moved, or the camera was not moved. | Move the tree east of the rear_side frustum or raise the camera. |
| 10 | P2 | side_entry, east_side, right_side | The fence's front-end post butts against the outer corner of the side landing. The landing's north rail sits on the yard side of the fence, with no gate or clearance. | The fence start was set to the landing depth. | Start the fence about 0.6 m north of the landing, or add a gate. |
| 11 | P2 | top vs top, rear | The cedars run only along the east fence. The source top also has a cedar clump along the north fence at the north-east corner. | Incomplete planting set. | Add 3–4 cedars along the north fence at the north-east corner. |
| 12 | P2 | front, front_corner, aerial | Planting is sparse: three ball shrubs west of the landing and two by the stair. The source has mixed flowering beds along the front and a hedge at the west. | Simplified landscape. | Add a mixed bed along the front west and a low hedge. |
| 13 | P2 | rear, right_side, rear_side | The rear-deck posts never show ground contact in any view (the fence, cedars and tree hide it). | Occlusion only. | Show the post feet in one view, or add a footing visible over the fence in rear_side. |

## 3. Source conformance checklist

| Item | Status | View used |
|---|---|---|
| Silhouette and storey count (boxy two-storey, plan proportion) | conforms. Two storeys; plan width/depth about 1.18 against about 1.20 in the source. | front, top vs top |
| Roof pitch | deviates (P2-6, slightly steep) | rear, front_corner vs oblique |
| Front-gable ridge front to back over the middle | conforms. Ridge at the plan centre. | top vs top, roof_ridge |
| Deep overhangs | conforms | right_side, east_side, front |
| Shingle courses | conforms (courses and tabs visible); colour deviates (P2-5) | roof_ridge, front_corner |
| Fascias | deviates. The front rake has a black slot (P1-1) and the corner blocks stand proud (P2-4). | architecture_close, front |
| Gutters | conforms; rear corner end is inboard (P2-4) | east_side, rear |
| Outriggers under the gable rakes | conforms. Three per rake, front and rear. | front, facade_close, rear |
| Brick ground storey (street front only) | conforms in extent and colour | front, facade_close |
| Brick joints | deviates. Black pits at every T-junction (P1-2). | brick_base, entry_stair |
| Rowlock sills | deviates. Plain slab (P2-7). | brick_base |
| Stucco upper storey and all other walls | conforms | east_side, left_side, rear |
| Balcony slab and thick white fascia | conforms | balcony_rail, facade_close |
| Balcony grey aluminium picket railing | conforms (returns at the west end) | balcony_rail |
| Balcony extent (east two thirds) | conforms. Starts at about 27–32% from the west, against about 31–37% in the source. | front_corner vs oblique, top vs top |
| Windows: bronze sliders | conforms | glass_close, brick_base |
| Windows: light count | conforms. Three-light upper-left, three-panel slider, smaller window behind the balcony, three-light ground windows each side. | facade_close |
| Windows: sizes per floor | conforms | front vs front |
| Curtains | deviates (P2-8, colour) | facade_close |
| Front door (white panelled) | conforms | entry_stair |
| Glazed sidelight | conforms | entry_stair |
| White casing | conforms. The head stands proud and there are no black corners. | casing crop |
| Two coach lamps | conforms | facade_close |
| Mailbox (slim, on the wall) | conforms | entry_stair |
| Raised concrete landing | conforms | entry_stair, front_corner |
| Front stair down eastwards along the front, aluminium railings both sides | conforms | entry_stair, fc_stair crop |
| East side windows (small, upright, stacked over one ground window and the suite door, front about 45% and rear third blank) | conforms. Front about 47% blank, rear about 26% blank. | east_side, right_side |
| Side suite door (full-lite) | conforms | side_entry |
| Side landing and flight down towards the street | conforms; fence abutment (P2-10) | side_entry, front_corner |
| Downpipes at the corners | conforms. No black joints. | east_side, front, rear |
| Exposed concrete foundation (sides and rear) | conforms on the visible east and west runs; rear hidden by the fence | east_side, front_corner |
| Lawn | conforms | front_corner, aerial |
| Beds and shrubs | deviates (P2-12, sparse) | front, aerial |
| Front walk | conforms | top vs top, front_corner |
| Sidewalks, boulevards and curbs on both streets | conforms, including the side path to the suite stair | top, front_corner |
| Board fence with lattice top round the back yard | conforms | left_side, rear |
| Cedars at the rear corner | partially conforms. East row only (P2-11). | top, right_side |
| Street trees | deviates (minor). Boulevard trees added where the source has lot trees. | front, top |
| Materials hierarchy (dark roof over white stucco, red brick base) | deviates. The roof is too pale (P2-5). | front_corner vs oblique |
| West and north faces (upper rear deck, back stoop): not visible in the sources, judged for coherence only | coherent. Deck-post contact is unverified (P2-13). | rear, top, left_side |

## 4. Camera validity

- **front:** legible, but the azimuth does not match the locked front, and the east elevation is compressed to about 10% of the visible width (P1-3).
- **front_corner vs oblique:** matched. Visible width ratios are about 0.38 against 0.43, with similar elevation and apex position.
- **top vs top:** matched (north up, ridge vertical at the centre).
- **aerial:** valid. It is a south-west aerial (not a matched role). A foreground tree crown covers the front-west ground corner (P2-9).
- **rear_side:** the house is legible, but the north-east tree crown occludes the lower about 25% of the frame, including the deck footings and the rear ground floor (P2-9).
- No view clips the asset or has an occluded target that would make it invalid.
- **Detail and interior views:** all legible. These are facade_close, architecture_close, glass_close, balcony_rail, entry_stair, brick_base, east_side, side_entry, roof_ridge and interior.

## 5. Previous-version (v001) findings: resolved in the pixels?

1. **Pure-black trim faces:**
   - Gable apex spike, front and rear: **resolved.** The front apex min is RGB (53, 48, 36) with no spike; the rear apex min is (91, 76, 56).
   - Black rake-fascia ends: **resolved.** Brown return blocks cover them.
   - Downpipe elbow, offset and outlet joints: **resolved.** They are brown throughout (east_dp, front_ecorner, front_wcorner and the rear corner crops).
   - Black squares at the casing top corners: **resolved.** The head stands proud and the corners are clean.
   - Black dots on the stair-head post caps: **resolved.** The only dark object near the stair heads is the door lockset.
   - The defect class is **not eliminated**, because two new near-black artefacts appear: the front-rake soffit slot (P1-1) and the brick T-joint pits (P1-2).
2. **Rake-to-eave corners:** **resolved as a P1.** There is no bare end face and no slot, and at the front-east close-up the eave fascia and gutter emerge from one closed brown return. Residual P2-4: the blocks stand proud above the roof line, and at the rear corners the gutter end sits inboard and below the block.
3. **East openings on an even grid:** **resolved.** One ground window and the suite door are mid-wall, with an upright upper window stacked over each, the front about 47% blank and the rear about 26% blank. The side landing and flight moved with the door, and the door is full-lite.
4. **Claimed P2 fixes:**
   - Warmer roof shingles: warmer, but now much lighter than the source (P2-5).
   - Slim wall mailbox: **done.**
   - Cedars clear of the side landing: **done.**
   - North-east tree clear of rear_side: **not done** (P2-9).
5. **Strengths that must still hold:**
   - Low wide front gable with outriggers: holds; slightly steep (P2-6).
   - Brick ground storey under a stucco upper storey: holds.
   - Long front balcony with picket railing: holds.
   - Raised front landing with its stair along the front: holds.
   - Oblique framing: holds.
   - **Front framing: does not hold** (P1-3).
