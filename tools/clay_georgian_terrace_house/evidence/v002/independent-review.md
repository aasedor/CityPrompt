# Independent holistic review: clay Georgian terrace end house, v002

Reviewer: independent RLASM v6.1 holistic reviewer (not the builder). Evidence: the three locked sources (`sources/front.png`, `sources/oblique.jpg`, `sources/top.jpg`), all 18 renders at full resolution, the four phone boards, and zoomed crops written to `/tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/indep-review-georg-v002-crops/`. I did not use any metadata, counts, hashes or builder notes as proof.

## 1. Verdict

**VISUAL_REWORK_REQUIRED**: the v001 blockers are fixed in the pixels, but two P1 defects remain. All five dormer sashes are malformed: the lower sash is unglazed with stub bars, the sill is detached, a black speck sits on each meeting rail, and the openings are squat. The main block is also about 25 % too deep for its width compared with the governing top view.

Counts: P0 = 0, P1 = 2, P2 = 16

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | mansard_dormers, architecture_close, chimney_stacks, roof_lead, front, front_corner, aerial | All five dormer windows have the same faults. (a) The upper sash is one plain pane with no glazing bars. (b) The lower sash has no glass: the slate blue-grey shows straight through. Two white bars hang from the meeting rail and stop short, and there is no bottom rail, so the window reads as a "π" frame. (c) The stone sill floats below the frame, with slate visible between them. (d) A solid black square sits at the centre of every meeting rail. (e) The opening is about square (≈1:1), but the source dormers are portrait sashes (≈1:1.8) with glazing bars in both sashes (oblique crop). | The dormer sash component is missing its lower glass pane and bottom rail. The lower bars are modelled as pendants, not sash bars. The meeting-rail lock or fitting has no material or is a hole. The dormer opening was sized from the old pediment dormer. | Rebuild the dormer sash as the main-facade sash at reduced size: a portrait opening of about 1:1.7, glazed upper and lower sashes with glazing bars, a full bottom rail seated on the sill, and the sill touching the frame. Delete or re-material the meeting-rail fitting. Re-render mansard_dormers and architecture_close. |
| 2 | P1 | top (vs locked top), front_corner/aerial (vs oblique) | The main block's plan is too deep. On the roof outline in top, depth:width is ≈0.83 (≈206 × 248 px). In the locked top it is ≈0.65 (≈338 × 520 px). The render reads near-square where the source reads as a clear 1.55:1 oblong. The oblique pair agrees in direction: the east wall to front ratio is ≈0.46 in front_corner against ≈0.42 in the oblique. | The plan depth was set from an assumed terrace depth instead of being measured from the top source. It is inflated further by moving the rear zone (lead strip, rear stack) back. | Shorten the main block depth by about 20–25 % so the roof outline is ≈1.5:1 in the top view. Keep the dormer row, the ridge at about 60 % depth from the front, the lead strip and the rooflight in their source proportions, then re-check top against the source. |
| 3 | P2 | top, roof_lead, chimney_stacks | All three stacks sit about 15 % of the depth too far forward. In the source, the east and west-middle stacks span ≈33–70 % of the depth and the west-rear stack straddles the rear parapet corner. In the render they span ≈17–55 %, and the rear stack stops inside the rear corner. | Stacks were placed from the oblique, where perspective pulls them forward. | Move the stacks back to the top-view positions after fix 2. |
| 4 | P2 | top, rear, rear_side | The rear additions are out of proportion. The east one-storey extension is ≈28 % of the main depth (source ≈10 %), and its flat roof is rendered in the wall brick tan instead of grey lead. The hipped wing has projecting eaves, where the source shows a parapeted, coped box with the hip inside the parapet. | The rear additions were blocked out generically. | Make the east extension shallower, give its roof a lead/grey material, and give the wing a coped parapet around the hip. |
| 5 | P2 | front, facade_close, architecture_close, mansard_dormers | There is an extra stone band about a parapet height below the parapet coping. The source has a single stone coping at the foot of the mansard, with brick running straight down to the top-floor window arches. | A cornice band was added over the source. | Remove the lower band, or merge it into the coping. |
| 6 | P2 | facade_close, front | Top-floor sashes are ≈0.67 of the first-floor height. The source is ≈0.83, so the top-floor windows look squat. | Storey heights or window templates were scaled down. | Raise the top-floor window heads by about 15–20 %. |
| 7 | P2 | right_side, east_side, front_corner | The stone string course and plinth wrap the full east wall. The source east wall (oblique crop) shows plain brick with no band. | The front band was extruded around the corner. | Stop the string course at the front corner, or one return deep. |
| 8 | P2 | chimney_stacks, roof_lead, left_side, aerial | There are black void seams, a few px wide, at the mitred coping corners: north-east, and north-west below the rear stack. | The coping pieces do not meet, so the background shows through. | Extend or weld the coping segments at the corners. |
| 9 | P2 | front, front_corner, aerial, top | The west neighbour is lower than in the source: its eaves sit near the house's top-floor window heads. In the source, the neighbour's main cornice is about level with the house parapet. | Neighbour storey count or heights were reduced. | Raise the neighbour by about one storey. Keep the stucco ground floor, the hipped slate roof, dormers and stacks. |
| 10 | P2 | rear, rear_side | The neighbour's rear wall is a blank box with no windows. | Only the context front was detailed. | Add a simple rear sash grid. |
| 11 | P2 | left_side (left_detail crop) | There is one off-centre west-wall window glazed as a 2×2 cross, which breaks the six-over-six grammar. | A different window template was used. | Use the narrow six-over-six or 4-over-4 side-wall sash, or omit the window. |
| 12 | P2 | front, front_corner, aerial | The tree is a low, flat low-poly umbrella crown at about first/second-floor height. It reads as a stone pine. The source plane tree is tall and rises above the eaves. | Generic tree asset. | Use a taller trunk with a rounded, irregular crown reaching about the parapet. |
| 13 | P2 | front, facade_close (front_gate crop) | The west garden gate is a blank recessed panel in the brick colour. The source gate is a timber board gate. | Gate material set to brick. | Give the gate leaf a timber or dark material and a plank or panel break. |
| 14 | P2 | doorcase_balconette, front_corner | The balconette end stays splay outward and visually cross the adjacent first-floor window in the low doorcase view. | Stay angle or length. | Turn the stays back into the brick between openings. |
| 15 | P2 | doorcase_balconette | The door has 4 plain panels and the fanlight has 3 lights. The source has a 6-panel door with a single-light rectangular fanlight. | Simplified door asset. | Use 6 panels and a single-light fanlight. |
| 16 | P2 | front | The top of the east chimney stack and its pots are clipped by the top frame edge. The locked front also crops the upper right, so this is not invalidating. | Camera tilt. | Tilt or pull back slightly so the stack and pots are in frame. |
| 17 | P2 | top, right_side, rear | The house is small in frame (≈17–25 % of the frame width). It is legible, but detail is hard to judge. | Wide framing. | Frame the target at about 60 % of the frame width. |
| 18 | P2 | left_side | The neighbour roof fills about 35 % of the lower foreground and hides the west-wall ground storey. The target is still legible. | Camera from over the neighbour. | Raise or tilt the camera slightly so more of the west wall shows. |

## 3. Source conformance checklist

| Item | Status | View(s) used |
|---|---|---|
| Silhouette | deviates: correct elements, but the main block is too deep in plan (finding 2) | top vs top, front_corner vs oblique, aerial |
| Storey count and bay rhythm | conforms: 3 brick storeys plus the mansard; 5 even bays with the central door/French window bay; dormers align with the bays | front, facade_close, front_corner |
| Brick and joints | conforms (clay): flat tan brick tone with coursing lines; no texture required | facade_close, glass_close |
| Sashes (sizes per floor, bars, sills, flat arches) | conforms, with a P2: six-over-six (3×4) on every floor front and rear; first floor tallest; stone sills project; flush, splayed buff flat arches seated on the heads; visible reveal returns. Top floor slightly squat (finding 6) | facade_close, glass_close, arch_win crop, rear_north |
| Doorcase (pilasters, frieze, fanlight, door) | conforms: plain stone pilasters with caps, entablature/frieze, rectangular fanlight, black panelled door, stone step. Panel and light count differ (P2) | doorcase_balconette, front |
| French window and balconette | conforms: a full-height French window to the slab, black iron railing on the stone doorcase slab, seated with a contact shadow | facade_close (french crop), doorcase_balconette, interior |
| String course and plinth | conforms on the front. Deviates on the east wall, where it wraps (finding 7) | facade_close, front_plinth crop, east_side |
| Parapet and coping | deviates (P2): short parapet with coping present, plus an extra stone band below it (finding 5); coping corner seams (finding 8) | architecture_close, mansard_dormers |
| Mansard (pitch, slate, dormers) | deviates: steep slate-grey mansard with five flat lead-topped dormers and slate cheeks is correct; dormer sashes are malformed (finding 1) | mansard_dormers, architecture_close, front_corner |
| Lead flat and skylight | conforms: an upper slate plane to a mid-depth ridge, a rear lead strip and a kerbed rooflight toward the west | roof_lead, chimney_stacks, aerial, top |
| Side parapets and chimney stacks with pots | conforms, with a P2: coped side parapets follow the mansard profile; three long stacks (two west, one east) with rows of 4–5 clay pots; stacks set too far forward (finding 3) | chimney_stacks, roof_lead, left_side, aerial |
| Side wall windows | conforms: one column of narrow sashes at about 55–60 % depth on the east wall, one per storey, with arches, sills and reveals, matching the narrow deep-reveal east windows in the oblique | east_side, right_side, rear_side, src_obl_east crop |
| Passage | conforms: paved east passage between the house and the boundary wall with a front pier | front_corner, aerial, top, right_side |
| Garden walls and gate | deviates (P2): the west wall and pier are present; the gate reads as a brick panel (finding 13) | front (front_gate crop), front_corner |
| Lamp | conforms: black lamp standard at the front-east corner on the pavement | front, front_corner, top |
| Tree | deviates (P2): present at the west gap, but low and umbrella-shaped (finding 12) | front, front_corner, top |
| Neighbour terrace | deviates (P2): Georgian, with a stucco ground storey, framed sashes, hipped slate roof, dormers and stacks; about one storey low, with a blank rear (findings 9, 10) | front, front_corner, aerial, rear |
| Materials hierarchy | conforms, with a P2: brick tan, white stone dressings and sashes, slate grey roof, black iron, door and lamp, terracotta pots; the east extension roof is wrongly in brick tan (finding 4) | front_corner, aerial, top |

## 4. Camera validity

No view is invalid. In every view the target is unoccluded and legible.
- **front**: the top of the east stack is clipped by the frame (P2, finding 16). The locked front crops the upper right in the same way.
- **left_side**: the neighbour roof fills the lower-right foreground and hides the west ground storey. The upper west wall, the rear wall, the stacks and the rear wing are clear (P2, finding 18).
- **top, right_side, rear**: legible but small in frame (P2, finding 17).
- front_corner, aerial, rear_side and every detail view are well framed.

## 5. Previous-version (v001) findings: resolved in the pixels?

| v001 finding | Status in v002 pixels | Evidence |
|---|---|---|
| left_side hidden behind a full-height neighbour box (P0) | **Resolved.** The camera looks over a lower neighbour from the north-west. The house's west and rear walls, stacks and rear wing are visible. | left_side |
| Pedimented dormers instead of flat lead-topped dormers | **Resolved.** Flat projecting lead caps, slate cheeks. A new sash defect replaces it (finding 1). | mansard_dormers, architecture_close |
| Black notches at the dormer pediments | **Resolved** at the pediments, which are gone. New black specks appear on the dormer meeting rails (finding 1) and black seams at the coping corners (finding 8). | dormer3 crop, notches crop |
| Proud salmon flat arches floating above the heads | **Resolved.** Flush, splayed buff arches seated directly on the window heads. | glass_head crop, facade_close |
| Nine-over-nine first-floor sashes | **Resolved.** The first floor is 3×4 six-over-six, as on all other floors. | facade_close, glass_close |
| Two columns of large windows on the east wall | **Resolved.** One column of narrow sashes at mid-depth. | east_side, right_side, rear_side |
| Two short chimney stacks instead of three long ones | **Resolved.** Three long stacks (two west, one east) with rows of 4–5 pots. Position is a P2 (finding 3). | chimney_stacks, roof_lead, left_side |
| Flat ribbed metal upper roof | **Resolved.** Upper slate planes to a mid-depth ridge, a rear lead strip and a rooflight. No ribs. | roof_lead, aerial |
| East rear extension missing | **Resolved.** A parapeted one-storey east rear extension is present. Its depth and roof colour are P2 (finding 4). | rear, rear_side, top |
| Rear wing roof cutting a rear window; blank wing windows | **Resolved.** The wing roof sits below the second-floor rear sashes. The wing windows are glazed six-over-six. | rear_north, rear |
| Modern flat-topped neighbour | **Resolved.** Georgian neighbour with a stucco ground storey, sashes, a hipped slate roof, dormers and stacks. Its height and blank rear are P2 (findings 9, 10). | front, front_corner, aerial, rear |
| (claim) Close framings for front_corner and aerial | **Resolved.** Both views frame the house tightly and legibly. | front_corner, aerial |
