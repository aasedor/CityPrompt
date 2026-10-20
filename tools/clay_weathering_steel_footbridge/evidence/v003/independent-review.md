# Independent holistic review: clay weathering-steel footbridge v003 (RLASM v6.1)

Reviewer: independent; I did not build this candidate. I judged only rendered pixels against the locked source pixels (`sources/front.png`, `sources/oblique.jpg`, `sources/top.jpg`). I opened all 18 renders and the 4 phone boards at full resolution. I made zoomed crops only in a new folder, `/tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/review-crops-v003-7c59f750/`. I did not use builder metadata, counts or notes as proof.

## 1. Verdict

**Verdict: PASS_ZERO_P0_P1.** In the pixels, the bend is now a kite: a collar tie runs across the corner about one panel back from the outer apex, and two struts rise from the inner corner node to the collar ends. There is no apex fan and no bisector tie, which matches the oblique and top sources. Every earlier fix still holds, and only polish-level deviations remain.

Counts: P0 = 0, P1 = 0, P2 = 12

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P2 | front | The span sits mostly over a pale plaza. Road paving shows only at the bottom-left, and a white bus box sits end-on under the bottom chord. The source front looks down onto several traffic lanes, with cars directly under the span. | Front camera yaw/target puts the crossing arm's landing end over the plaza, not over the road. | Pan or retarget the front camera toward mid-road, about 10-15 degrees, so lanes and cars fill the lower third under the chord. |
| 2 | P2 | top, aerial, left_side, front_corner | The context is simplified: a 4-lane road with a centre double-yellow line (the source shows a wider multi-lane arterial with turn lanes and crosswalks), and no low brick block runs along the land arm as in the top source. | Context kept to clay minimum. | Optional: widen the road to 5-6 lanes and add a low brick block along the land-arm side. |
| 3 | P2 | road_under | A thin black mitre seam or wedge shows on the bottom-chord underside at the outer apex (about x 10-45, y 605 in the render). | The underside faces of the two bottom-chord mitre pieces do not close; a small gap shows the void. | Extend or weld the bottom-chord mitre underside faces, or add a closing plate under the apex node. |
| 4 | P2 | mesh_infill | A small black triangular void at the foot of the diagonal V where it meets the bottom chord (about x 920-1000, y 680-720). | The diagonal end bevels leave an uncapped gap above the chord top face. | Cap the V foot with a gusset block flush to the chord top. |
| 5 | P2 | front, facade_close, landing_stair, architecture_close | The fascia squares read as raised grey studs rather than perforations or bolt recesses. | Flat grey boxes placed proud of the fascia. | Recess them, or darken them to read as holes, or swap to small round heads in the rust colour. |
| 6 | P2 | glass_close, mesh_infill, deck_walk | The cable-net strands are slightly heavy and pale, so the infill reads closer to chain-link than to the source's fine stainless net. | Strand radius a little large for the 1.6 m panel scale. | Reduce strand thickness by about 30-40%. |
| 7 | P2 | rear_side | The pale-roofed warehouse in the foreground hides the outer apex, its corner post and the bend underside. The inner corner and collar remain readable. | Camera height or position too low behind the warehouse. | Raise the camera or shift it laterally so the outer apex clears the roof edge. |
| 8 | P2 | landing_stair, aerial, left_side | The deep fascia chord runs straight into the tower face with no visible bearing seat or corbel. | No bearing element modelled at the towers. | Add a small rust bearing plate or brick corbel under the chord end at each tower. |
| 9 | P2 | top, deck_walk, top_chord, glass_close | The deck shows mottled dark blotches (render noise) and reads as a medium-dark brown, not the warm tan-rust perforated plate in the sources. | Low sample count or denoise on the deck material, and a slightly dark base colour. | Raise the samples or the denoise quality for the deck and lift its value toward the source tan. |
| 10 | P2 | road_under | The foreground car has an oversize translucent glass cabin box that reads as a ghost volume. | Glass cabin primitive larger than the body, with high transmission. | Shrink the cabin to the body footprint and make it opaque dark glass. |
| 11 | P2 | top, front_corner | The kite proportion is slightly long. The collar sits about 73% of the way from the outer apex to the inner corner node (about 65% in the top source), so the apex triangle is a bit long and the lower struts are short and flat. | Collar node placed about 1.3-1.4 panel lengths from the apex instead of about 1. | Optional: pull the collar nodes about 0.3 panel toward the apex. |
| 12 | P2 | aerial | The land-arm landing tower is partly cut by the left frame edge. The landing itself and the bridge end are still visible. | Aerial framing slightly tight on the left. | Widen the aerial frame or shift its target about 5% to the right. |

No P0 or P1 findings.

## 3. Source conformance checklist

| item | status | view(s) used | notes |
|---|---|---|---|
| Plan and proportions | conforms | top vs top.jpg; aerial, left_side, rear | One mitred V bend with no hub, ring or hub deck. The crossing arm is about 70 degrees to the road; the land arm is about 19-20 degrees off the road and runs along the kerb/plaza edge. Measured in the top render: the crossing arm direction is about 20 degrees from horizontal against a vertical road, and the land arm about 19 degrees from vertical. The source top gives about 65 and 21 degrees. |
| Truss geometry and panel rhythm | conforms | front vs front.png; facade_close, road_under, rear_north | Warren panels with bold diagonals and no verticals in the side trusses. The rhythm is regular, and whole Warren panels run to the tower face with a single end post and no crossing members (landing_stair, aerial_left crop). |
| Chords and diagonals | conforms | front, front_corner, truss_node, top_chord, deck_walk | Heavy top chord. In the top plane there is one transverse tie and one diagonal per bay, alternating into a zig-zag (rear crop, deck_walk, top). At the bend: a collar tie across the corner from the first outer top-chord node of each arm, plus two struts from the inner corner node to those nodes, with no apex fan and no bisector tie (top crop, front_corner crop, rear_side crop). One corner post per node. |
| Mesh infill | conforms (P2 #6) | glass_close, mesh_infill, front | Diamond cable net on slim pale posts at about 1.6 m, with a bottom cable/rail and a dark handrail. The strands are slightly heavy. |
| Deck | conforms (P2 #9) | top, deck_walk, top_chord | A continuous one-colour plate deck runs through the bend with joint lines. The colour is darker and blotchier than the source. |
| Landings and supports | conforms (P2 #8) | landing_stair, aerial, left_side, right_side, rear, rear_north, architecture_close | Brick stair towers at both ends with doors. The deep fascia bottom chord is seated into the towers. A single steel pier stands under the outer apex (aerial crop, rear, rear_north, road_under). There is no visible bearing seat. |
| Road beneath | conforms (P2 #1, #2) | top, front_corner, road_under, rear | Lanes, centre double yellow, sidewalks and simple car/bus massing. Narrower than the source arterial. The front view under-shows the road. |
| Context | conforms (simplified, P2 #2) | aerial, left_side, right_side, rear_side | Brick blocks with punched windows and a glass curtain-wall block, as in the sources. Simplified massing. |
| Materials hierarchy | conforms | all | Rust-orange Cor-Ten truss dominant, brick context secondary, pale glass block, grey road. Clay palette consistent with the sources. |

## 4. Camera validity

- **No view is invalid.** In every view the target is legible, nothing is clipped in a way that hides identity, and no structural target is fully occluded.
- left_side shows the whole bridge (both arms, the bend, the pier and both towers), so the earlier fix holds.
- rear_side: the foreground warehouse partly occludes the outer apex and the bend underside (P2 #7). The inner corner, the collar and both arms remain legible.
- aerial: the land-arm tower is partly cut by the left frame edge (P2 #12), but the landing is visible.
- front_corner: both arms run off the frame edges, as the arms do in the oblique source. The bend is centred and legible.
- front: the camera is valid, but the road is under-represented (P2 #1).

## 5. Previous-version (v002) findings: resolution in the pixels

| v002 finding | severity | v003 status | evidence |
|---|---|---|---|
| Overhead framing at the bend did not match the sources (three-strut apex fan, no member across the corner). | P1 | **Resolved** | Top crop: nothing leaves the outer apex except the two outer chords. A single collar tie joins the first outer top-chord node of each arm, roughly perpendicular to the bend bisector. Two struts run from the inner corner node to those two nodes, forming a triangle (kite) with a crossbar. There is no roof tie along the bisector. Front_corner and rear_side crops confirm the same members, and the regular transverse ties and diagonals start after the triangle. The proportion is slightly long (P2 #11). |
| Front camera: mostly pale plaza under the span, bus end-on under the chord. | P2 | Not resolved | Unchanged (P2 #1). |
| Simplified context (no low brick block along the land arm, 4-lane road). | P2 | Not resolved | Unchanged (P2 #2). |
| Small black square on top of the outer and inner corner posts in overhead views. | P2 | **Resolved** | Top, front_corner, aerial and architecture_close all show a closed rust-coloured cap plate just above the chord top at both corner posts. There is no black square. |
| Thin black mitre wedge at the outer apex in road_under. | P2 | Not resolved | The black seam is still visible on the underside of the apex mitre (P2 #3). |
| Fascia squares read as studs rather than holes. | P2 | Not resolved | Unchanged (P2 #5). |
| Cable-net strands a little heavy. | P2 | Not resolved | Unchanged (P2 #6). |
| Pale-roof warehouse hiding the bend underside in rear_side. | P2 | Not resolved | Unchanged (P2 #7). |
| No visible bearing seat at the towers, deck render noise, ghost-glass car cabin. | P2 | Not resolved | Unchanged (P2 #8, #9, #10). |

Earlier fixes that must still hold, verified in the pixels:

- One mitred V with no hub, ring or hub deck, and one corner post per node: holds (top, architecture_close, front_corner).
- Arm angles of about 70 degrees (crossing) and 20-25 degrees (land): holds (top).
- One transverse tie and one diagonal per bay in a zig-zag: holds (rear, deck_walk, top).
- Fine diamond cable net on slim posts at about 1.6 m with a bottom cable and dark handrail: holds (glass_close, mesh_infill).
- Whole Warren panels to the tower face with a single end post and no crossing members: holds (landing_stair, aerial).
- Deep fascia bottom chord seated into the towers: holds (landing_stair).
- Single steel pier under the outer apex: holds (aerial, rear, rear_north, road_under).
- Continuous one-colour plate deck through the bend: holds (top).
- left_side shows the whole bridge: holds.

New in v003: a small black void at a diagonal foot in mesh_infill (P2 #4), and the slightly long kite proportion (P2 #11). Neither blocks approval.
