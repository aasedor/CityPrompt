# Independent holistic review: clay Vancouver Special, v003 (RLASM v6.1)

Reviewer: independent; did not build. Evidence: the three locked sources, all 18 renders opened at full resolution, the four phone boards, and pixel crops and luminance samples written only to `/tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/v003-review-crops-baddebd5/`. I ignored builder metadata and notes as proof.

## 1. Verdict

**VISUAL_REWORK_REQUIRED.** All three v002 P1s are fixed in the pixels, but the front gable is measurably steeper than both locked views, the roof is much too light against the source palette, and one downpipe outlet at the hero corner still shows a near-black slot that the v002 must-hold list forbids.

Counts: P0 = 0, P1 = 3, P2 = 11

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | front_corner vs locked oblique; front vs locked front; rear; roof_ridge | The front gable is too steep for a "low wide" Vancouver Special gable. In the matched oblique, apex rise above the line joining the two eave tips is 0.195 of the tip-to-tip span in front_corner (tips 234,367 / 991,608; apex 556,314) against 0.13 in the locked oblique (tips 167,277 / 782,497; apex 420,282). The two cameras are matched: the corner-height to front-length ratio is 0.53 in front_corner and 0.54 in the oblique, so this is geometry, not camera. In the oblique the source's west rake runs almost level to the apex, but the render's west rake climbs clearly. Rise against eave-corner wall height gives 0.47 render vs 0.27 source. In the front view the apex rise is 0.41 of the street-front width against 0.21 in the source. The near-frontal rear elevation measures about 21° in the render; scaling by the matched-oblique ratio puts the source at about 14–15°. | The roof pitch was authored at about 4.5–5:12 instead of the source's about 3–3.25:12. | Lower the roof to about 15° (3.25:12), keeping eave height, overhang depth, the centred front-to-back ridge, fascia depth and outrigger spacing (re-space outriggers along the shorter rake). Re-render front, front_corner, aerial, rear, rear_side and roof_ridge. Acceptance: front_corner apex rise / tip span = 0.13 ± 0.02. |
| 2 | P1 | front_corner, aerial, top, roof_ridge, left_side, right_side, rear_side; phone-01 | The roof reads as a light pinkish taupe, not the source's medium-dark brown-grey asphalt. Median roof luminance is about 135–143 (front_corner 141,136,132; top W 148,143,138, E 138,133,129) against 90–115 in the sources (oblique 93,91,89; top E 93,91,88, W 126,114,102). This holds even though the render's white stucco is darker than the source's (177–190 vs 220–236). The roof-to-stucco value ratio is about 0.78 in the render against about 0.4–0.5 in the sources, so the dark-roof-over-white-box hierarchy that defines the source silhouette from above is lost. | The shingle base colour or albedo was set far above the sampled source palette. | Set the shingle material to the sampled source colour (about sRGB 95,90,86 for field shingles, with the ridge cap slightly darker), and keep the course geometry. Acceptance: in front_corner, the roof median luminance / front stucco median luminance ≤ 0.55. |
| 3 | P1 | architecture_close (x≈1056–1062, y≈482–515), front (x≈900–905, y≈157–162) | At the front-east eave (the hero corner), there is a near-black slit about 3 px wide and 30 px tall where the downpipe outlet stub drops out of the gutter, between the gutter's inner face and the outlet's west side. Luminance falls to 8 (72 px under 30). The v002 must-hold says no black faces on any downpipe outlet. The other seven outlets checked (right_side ×2, left_side ×2, east_side ×2, rear_side) stay at or above 36. | The gutter-bottom drop hole is wider than the outlet stub, or the outlet sits off-centre in it, so the camera sees into an unlit void or backface inside the gutter. | Centre the outlet stub in the drop hole and make the hole no larger than the stub, or cap the gap with a brown gutter-bottom plate. Give any interior gutter face the brown trim material. Acceptance: minimum luminance ≥ 45 in architecture_close box (1040,470)-(1090,540) and in front box (890,145)-(915,175). |
| 4 | P2 | front vs locked front | The front camera is more strongly convergent than the source. Front-wall far-edge height / near-corner height is 0.70 in the render against 0.80 in the source, so in the front view the balcony's west return visually crosses the lower third of the upper-left window. facade_close confirms that the geometry keeps them clear. The east wall / street front width ratio, which v002 flagged, is now 0.47 against 0.54 in the source, which is acceptable. | The camera is slightly too close / wide for the source's weaker front recession. The source front is not fully physically consistent. | Optionally pull the camera back along the same bearing and lengthen the lens about 15%, keeping eye height and an east/front ratio of 0.50 ± 0.05. |
| 5 | P2 | locked front (x≈268–292), locked oblique; facade_close, front_corner | The source shows a shallow vertical jog or pilaster in the upper front stucco between the upper-left window and the mid window, with a lit east return visible in the oblique. The render's upper front is one flat plane. | Massing articulation was omitted. | Add a shallow (about 0.15–0.3 m) step or pilaster at that line. |
| 6 | P2 | brick_base, entry_stair, phone-02 | The brick reads browner and less saturated than the source's red-orange. Red minus blue is about 55 in the render against about 85 in the source. | Brick base colour is too desaturated. | Shift the brick face colour toward about sRGB 180,110,75. |
| 7 | P2 | brick_base, facade_close | The brick sills are plain slabs, with no on-edge rowlock unit joints. | The sill was simplified. | Score rowlock joints into the sill face. |
| 8 | P2 | architecture_close, front | The rake-to-eave corner return is one closed brown block, but it reads chunky: it stands about 8 px proud of the rake board above and below. | The block was enlarged to cover the deeper rake board. | Optionally trim it to flush or about 10 mm proud. |
| 9 | P2 | top vs locked top; rear_side | The cedars are a single row along the east fence only. The source cedars run as an L along the north fence and down the east fence. | Planting layout was simplified. | Add 3–4 cedars along the north fence at the NE corner. |
| 10 | P2 | top vs locked top | The front walk meets the stair foot at 0.58–0.67 of roof width from the west, against 0.76–0.86 in the source, which has a concrete pad east of the stair foot. | The walk was placed directly at the stair foot. | Add the pad and move the walk east. |
| 11 | P2 | facade_close, entry_stair | The coach lamps are modern box lanterns rather than coach-style lanterns. | Simplified fixture. | Use a coach-lantern profile. |
| 12 | P2 | side_entry, east_side | The suite flight has one stair railing (plus the landing guard). The locked front shows railings on both sides of the suite flight. | Second railing omitted. | Add the inner stair railing. |
| 13 | P2 | aerial; top | In aerial, the foreground boulevard tree covers part of the SW brick ground storey and bed. The top view crops off the south street and the corner curb return that the locked top shows. | Framing. | Nudge the aerial camera or tree, and widen or lower the top frame by about 8%. |
| 14 | P2 | facade_close vs locked front | The upper mid window, behind the balcony, is a two-light slider. The source reads as a single large pane. The source is ambiguous here. | Generic window type was reused. | Optionally use a single fixed light. |

## 3. Source conformance checklist

| item | status | view(s) used |
|---|---|---|
| Silhouette and storey count (boxy two-storey, corner lot, street south / side street east) | conforms | front, front_corner, top, right_side |
| Plan proportion (W/D) and ridge position | conforms. W/D is 1.18 vs 1.20; ridge at 0.50 vs 0.51 of width | top vs locked top |
| Roof pitch | **deviates (P1 #1)**. About 21° vs about 15° | front_corner vs oblique, rear, front |
| Front-gable ridge front-to-back over the middle | conforms | top, aerial, roof_ridge |
| Overhangs (deep at rakes and eaves) | conforms | front, left_side, right_side, rear |
| Shingle courses | conforms geometrically (modelled tab courses) | roof_ridge, front_corner |
| Roof colour | **deviates (P1 #2)**. Far too light | phone-01, front_corner, top |
| Fascias (brown, rake and eave), rake soffit, no black slot | conforms. Fascia ~120 → 1 px edge ~105 → soffit ~148, never black | architecture_close, front, facade_close |
| Gutters | conforms, except the outlet slot (P1 #3) | architecture_close, right_side, left_side |
| Outriggers under front gable (tip, mid, near apex each side) | conforms | front, facade_close, front_corner |
| Brick ground storey on street front, joints | conforms. Clean T-junctions, minimum luminance in brick fields 71–75, no pits | brick_base, entry_stair (5× / 4× crops) |
| Brick colour | deviates, minor (P2 #6) | brick_base |
| Rowlock sills | deviates, minor. Present as brick-coloured slabs without unit joints (P2 #7) | brick_base, facade_close |
| Stucco upper storey and all other walls | conforms | facade_close, left_side, right_side, rear |
| Upper-front jog / pilaster | deviates, minor (P2 #5) | locked front/oblique vs facade_close |
| Balcony slab and thick white fascia | conforms | facade_close, balcony_rail |
| Balcony railing (grey aluminium pickets, end returns) | conforms | balcony_rail, facade_close |
| Balcony extent (east two-thirds) | conforms. Starts at 0.29 of width vs 0.27 in the source | facade_close vs locked front |
| Windows: bronze sliders, light count | conforms. Upper-left 3-light, slider 3-panel, lower-left 3-light, big ground 3-light; upper mid is 2-light (P2 #14) | facade_close, glass_close, brick_base |
| Window sizes / positions per floor | conforms. All within ±0.03 of width of the source fractions | facade_close vs locked front |
| Window depth / returns | conforms. Visible reveals, frames and interior | glass_close, brick_base, balcony_rail |
| Curtains | conforms in clay terms (side curtain panels; interior shows them) | glass_close, interior |
| Front door (white, panelled) | conforms | entry_stair, facade_close |
| Sidelight (glazed, west of door) | conforms | entry_stair |
| Casing (white, top corners not black) | conforms | entry_stair crop |
| Lamps | conforms in placement (flanking the door); style differs (P2 #11) | facade_close |
| Mailbox | conforms (right of door) | facade_close, entry_stair |
| Raised concrete landing | conforms | entry_stair, front |
| Front stair running down eastwards along the front | conforms | entry_stair, front, front_corner, top |
| Front railings and stair-head post caps | conforms. Caps not black | entry_stair crop |
| East side windows (small, upright; upper stacked over ground window and door) | conforms | right_side, east_side, front |
| East wall front ~45% blank | conforms. 46% in right_side | right_side |
| Side (suite) door, full-lite, mid-wall, with lamp | conforms | side_entry, east_side |
| Suite landing and flight down towards the street | conforms; one stair railing (P2 #12) | side_entry, east_side, front |
| Downpipes at corners, elbows and offsets | conforms, except the front-east outlet slot (P1 #3) | architecture_close, right_side, left_side, east_side |
| Exposed concrete foundation (sides, rear) | conforms where visible | east_side, side_entry, rear_side, front |
| Lawn | conforms | front, front_corner, top |
| Beds and shrubs | conforms | entry_stair, facade_close, top |
| Front walk | conforms in presence; position offset (P2 #10) | top, front_corner |
| Sidewalks, boulevards, curbs on both streets | conforms. Curbs read only as simple edges at clay scale | front_corner, aerial, top, right_side |
| Fence with lattice top round the back yard (incl. west run) | conforms | left_side, rear, rear_side, aerial |
| Cedars at rear corner | conforms in presence; layout simplified (P2 #9) | top, rear_side, side_entry |
| Street trees | conforms (low-poly boulevard trees) | aerial, right_side, front_corner |
| Unseen faces: upper rear deck, back stoop | coherent with the visible grammar | rear, rear_side, top |
| Materials hierarchy | **deviates (P1 #2)**. The roof value is too close to the walls; trim, brick and stucco order is otherwise right | phone-01, front_corner |

## 4. Camera validity

- No view has the target occluded, the asset clipped or the target illegible. No P0 camera defect.
- **front**: valid. The east-wall to street-front ratio is 0.47 against 0.54 in the source; the suite door, landing, flight and both east openings are legible. The front recedes more strongly than in the source (P2 #4).
- **front_corner**: valid, and framing matches the locked oblique (corner-height to front-length 0.53 vs 0.54).
- **aerial**: valid. A foreground tree covers a small part of the SW ground storey (P2 #13).
- **top**: valid plan read. The south street and corner curb return are cropped (P2 #13).
- **rear_side**: valid. The north-east boulevard tree is no longer in frame, as claimed.
- Detail views (facade_close, architecture_close, glass_close, balcony_rail, entry_stair, brick_base, east_side, side_entry, roof_ridge, interior): all legible, with no clipping of their targets.

## 5. Previous-version findings, checked in the pixels

**v002 P1s**
1. Black slot along both front rakes, between the rake fascia and the rake soffit: **resolved.** I checked luminance profiles across the rake in architecture_close at x = 200, 450, 600 and 750: fascia ~120, a 1 px anti-aliased edge of 101–116, soffit ~148, a 1 px edge, then the wall. The minimum in the front-rake band is 41, with nothing under 30. Zoomed crops of both rakes in front and of the facade_close rakes show no dark slot.
2. Near-black pits at brick mortar T-junctions: **resolved.** The minimum luminance in all brick fields of brick_base is 71–75 (zero pixels under 70 outside the window and sill). 5× and 4× crops of brick_base and entry_stair show clean, continuous light-grey T-junctions.
3. Front camera not matching (east wall about 0.10 of the street front): **resolved.** It is now 0.47 against 0.54 in the source, and the suite door, landing, flight and both east openings are legible. A residual stronger front recession remains (P2 #4).

**v002 fixes that must still hold**
- No black trim faces:
  - Front and rear gable apex fascias: hold. The rear apex minimum is 85.
  - Rake ends: hold.
  - Door casing top corners: hold.
  - Stair-head post caps: hold. The only black there is the door hardware, which is intended.
  - Downpipe elbows and offsets: hold.
  - Downpipe outlets: **do not fully hold.** The front-east outlet shows a near-black slit (P1 #3). The other outlets are clean.
- Each rake-to-eave corner is one closed brown return at one height: **holds** at front-east (architecture_close) and front-west (front crop). The block reads chunky (P2 #8).
- East wall arrangement: **holds.** The front 46% is blank, with one ground window and the full-lite suite door mid-wall, an upright upper window stacked over each, and the side landing and flight at the door.

**v001 strengths**
- Low wide front gable with outriggers: **partly holds.** The outriggers and wide front are right, but the pitch is now measured steeper than both locked sources (P1 #1).
- Brick ground storey under a stucco upper storey: holds.
- Long front balcony with picket railing: holds.
- Raised front landing with its stair running along the front: holds.
- Oblique camera framing matched to the locked view: holds.

**v003 P2 claim:** the NE boulevard tree is out of the rear_side frame. Confirmed.
