# Independent RLASM v6.1 review: clay-montreal-plateau-rue v003

Verdict: PASS_ZERO_P0_P1

Counts: P0=0 P1=0 P2=13

## 1. Verdict

Verdict: PASS_ZERO_P0_P1. v003 fixes the only v002 P1. In every stair-head view, both handrails now die into capped stair-head newels, so no free iron bar rises out of the gallery deck. Every earlier fix still holds, and pixel diffs against v002 show the change is confined to the stairs.

Reviewer method: I opened all 3 locked sources, all 18 renders at 1440 px and all 4 phone boards with the Read tool. Zoomed crops and v002/v003 side-by-side crops are only in `review/crops_xcvtqe/`.

I diffed every v003 render against the v002 render of the same view, using a per-pixel max-channel difference over 40 on a 40 px grid:

- **Bit-identical:** architecture_close, glass_close, mansard_caps, rear, rear_yards and roof_parapets.
- **Changed by fewer than 25 px in total:** corner_building and top.
- **Changed only at stair heads and stair feet:** all other views.

I also ran a solid-black search over every render, flagging pixels with max channel under 20 that form a 9×9 px solid core, and classified every hit by eye.

How I told geometry defects from shadow and dark-by-design parts:

- **Contact and soffit shadow** stays above about RGB 40. Examples are under the gallery decks, under the flights, in the yards and under the cars.
- **Black iron** (stairs, newels, railings, fences, support posts) is dark by design. It is about RGB 6–30, but it keeps its member outline: separate treads, sawtooth stringers, pickets and capped posts, with lit wall showing between members.
- **Other dark-by-design parts:**
  - car tyres and dark car roofs (sidewalk_trees crop `st_cars.png`)
  - roof vents
  - ground-floor transoms in deck shade (about RGB 13–16). They sit inside a white frame with a reveal (crop `front_transom.png`).
- **A geometry defect** is near-black with no member or frame outline (a slot, wedge or slab), or an iron member where none belongs.

Every solid-black hit was a stair flight underside with a legible sawtooth outline, a framed transom, car tyres or a vent. No view has a geometry slot, wedge, slab or free-ending iron member.

## 2. Findings

| # | severity | view(s) | symptom (what the pixels show) | evidence | likely cause | finite fix |
|---|---|---|---|---|---|---|
| — | P0 | — | none | — | — | — |
| — | P1 | — | none. The v002 P1 is fixed (see section 5). | — | — | — |
| 1 | P2 (new) | front (≈ x955–975, y295–365), iron_stair (green plex ≈ x415–435, y185–265), sidewalk_trees (≈ x1010–1025, y370–420) | From street-level cameras below the deck, the new wall-side stair-head newel sits about 0.9 m behind the fascia. The fascia hides its base, so it looks like a short capped post standing on the gallery deck behind the gallery's front pickets, with the wall-side rail dropping from its cap behind the fascia. Seen from above the deck, the same post clearly stands at the wall-side corner of the stair opening (balcony_gallery crop `bg_top.png`, right_side crop `rs_stair.png`, facade_close crop `fc_head.png`). It is a correct, terminated member, not a defect, but the stair head reads a little busier than in the source, where the stair rail flows into the gallery railing. | crops `front_stair_top.png`, `is_green_top.png`, `st_stair.png`, `cmp_front_head.png`, `cmp_rs_head.png` | Two 80 mm newels per stair head, with the wall-side one set back at d = −0.3. | Optional: slim the head newels to about 50–60 mm, or turn the wall-side rail's head into a short level return to the wall instead of a free-standing post. |
| 2 | P2 (new note) | iron_stair (x1150–1440, y0–120) | The frame top cuts off the main (blue plex) stair head: both head-newel caps and the gallery top rail are out of frame. The stair-head detail is still fully legible on the green plex in the same view, and the main stair's flight, curl, newels and foot are fully in frame. | crop `cmp_is_main_head.png` | Camera tilt and framing, unchanged since v002. | Tilt up about 3–4° or pull back slightly so the main stair head sits inside the frame. |
| 3 | P2 (carried, v002 F2) | front vs sources/front.png | The camera sits on the sidewalk close to the facade. The near plex fills about 45% of the width (source about 26%), and the roadway is barely in frame. | front, board `phone-01` | Camera offset. | Move the camera about 3–4 m out to the curb and widen slightly. |
| 4 | P2 (carried, v002 F3) | top vs sources/top.jpg | The plan and framing match, but the render is near-nadir. The source tilts enough to show the east-row facades. | top | Camera pitch. | Tilt about 20–25° toward the block interior. |
| 5 | P2 (carried, v002 F4) | front_corner vs sources/oblique.jpg | The angle and arris match. The view is slightly wider and shows a bare interior lawn where the source has mature trees behind the roofs. | front_corner | Distance/focal length and interior planting. | Pull in about 10% and/or add interior tree masses. |
| 6 | P2 (carried, v002 F5) | front, facade_close, balcony_gallery, sidewalk_trees, corner_building (≈ x930–955, y745–850) | The door pairs carry a white lower panel that reads as a kick-plate. The corner plex's east-face entrance is a single narrow green leaf. | front (≈ x1095–1335, y750–835) | Door module material and corner door width. | Paint the lower panels in the door colour with a darker inset, and use a door pair at the corner entrance. |
| 7 | P2 (carried, v002 F6) | left_side, right_side, aerial, roof_parapets, rear_side | The context rows' teal caps are plain cubes. | right_side (x175–245, y345–400) | Low-detail context primitive. | Use a frustum or pyramid. |
| 8 | P2 (carried, v002 F7) | left_side (x0–270) | The north row ends in a blank grey party wall standing on the lawn. | left_side | Modelled extent. | Score or brick the party wall and give it a parapet, or extend the row past the frame. |
| 9 | P2 (carried, v002 F8) | front_corner, aerial, roof_parapets | Only the corner plex has a chimney. | roof_parapets (x925–975, y565–640) | Roof furniture. | Add a small brick chimney per plex at a party line. |
| 10 | P2 (carried, v002 F9) | front, facade_close | The third-floor balconies are as wide as the galleries (facade_close: about 400 px against 430 px). The sources show visibly smaller upper balconies. | facade_close | Shared balcony span. | Cut the third-floor balcony width to about 60–70%. |
| 11 | P2 (carried, v002 F10) | rear, rear_yards, roof_parapets | The rear windows are framed with depth and sills, but on brick walls their glass reads brick-brown, like a tinted infill. | rear_yards (x460–510, y415–480) | Glass transparency over the solid wall. | Use an opaque dark glass tone matching the street glass, or back the glass with a dark panel. |
| 12 | P2 (carried, v002 F11) | front (≈ x1060–1310, y475–535), facade_close (≈ x805–1085, y855–895), balcony_gallery, sidewalk_trees | The ground-floor transoms under the galleries render near-black. They are framed glass with a reveal, so this is not a slot, but they are the darkest flat areas on the facades. | crop `front_transom.png` | Glass tone in soffit shade. | Lighten the glass slightly so the shaded transoms read near RGB 35–45. |
| 13 | P2 (carried, v002 F13) | left_side, right_side | The context window glass stands slightly proud of its white surround. | right_side (x1320–1400, y440–540) | Context window layering. | Set the glass 2–3 cm behind the surround face. |

v002 F12 is fixed. The street-side rail used to level off in a short stub into the central newel. Now it keeps its pitch and dies into the newel's side (crops `cmp_front_foot.png`, `bg_foot.png`, `is_main_foot.png`).

Top view, dark-stripe check (crop `top_left.png`): the party lines are continuous lit parapets, with no dark gap stripes or wedges. The near-black shapes are the curling stairs, which keep their tread and curl outline, plus the vents.

## 3. Source conformance checklist

| item | status | view(s) used |
|---|---|---|
| Plan: two streets meeting at a corner | conforms | top, front_corner, aerial |
| Plan: building lines (continuous street walls) | conforms | top, front_corner, aerial |
| Plan: front yards | conforms | front, iron_stair, top |
| Plan: sidewalks | conforms | sidewalk_trees, front, top |
| Plan: roadways | conforms | top, sidewalk_trees, left_side, right_side |
| Plan: curb returns | conforms | top, front_corner |
| Corner building: limestone corner pavilion (east street) | conforms | corner_building, front_corner |
| Corner building: limestone quoins (north street) | conforms | corner_building |
| Corner building: brick | conforms | corner_building, front_corner |
| Corner building: windows (three floors, sills, lintels) | conforms | corner_building |
| Corner building: belt courses | conforms | corner_building |
| Corner building: mitred bracketed cornice round the corner | conforms | corner_building, front_corner |
| Corner building: corner mansard cap with gabled dormers | conforms (fully in frame) | corner_building, front_corner, top |
| Corner building: end mansard caps | conforms | front_corner, roof_parapets, rear_side |
| Corner building: north-end balcony and stair | conforms (flight, curl and foot newels read; the head is hidden by the tree in corner_building) | corner_building (crop `cb_stair.png`), front_corner |
| North-street turret plex: corbel | conforms | left_side, architecture_close |
| North-street turret plex: octagonal turret | conforms | left_side, architecture_close, top |
| North-street turret plex: turret windows | conforms | left_side |
| North-street turret plex: slate spire | conforms | architecture_close, left_side |
| North-street row: limestone and brick plexes, second turret plex | conforms | front, left_side, aerial, rear_side |
| East-street row: brick and limestone plexes | conforms | right_side, aerial |
| East-street row: stone bays and teal caps at the party lines | conforms | right_side, mansard_caps, aerial |
| Doors and door pairs: colours (blue, green, red) | conforms | front, facade_close, balcony_gallery |
| Doors and door pairs: stoops | conforms | front, iron_stair, corner_building |
| Doors: panelling | deviates (white kick-plate panel; corner entrance is a single leaf; #6, P2) | facade_close, corner_building |
| Windows: coloured frames | conforms | glass_close, facade_close |
| Windows: transoms | conforms (shaded ground-floor transoms very dark; #12, P2) | glass_close, facade_close, front |
| Windows: sills and lintels | conforms (rear glass tone off on brick; #11, P2) | glass_close, rear_yards, roof_parapets |
| Gallery and third-floor balconies: decks | conforms | balcony_gallery, facade_close |
| Gallery and third-floor balconies: painted fascias | conforms | balcony_gallery, facade_close |
| Gallery and third-floor balconies: brackets | conforms | iron_stair, balcony_gallery, sidewalk_trees |
| Gallery and third-floor balconies: railings | conforms (front railing now ends on the street-side head newel; the stair opening is open between two capped newels) | balcony_gallery (crop `bg_top.png`), facade_close (crop `fc_head.png`), right_side |
| Gallery and third-floor balconies: smaller third-floor balcony | deviates (same width; #10, P2) | front, facade_close |
| Iron exterior stairs: treads | conforms (landing tread flush with the deck end) | facade_close, iron_stair |
| Iron exterior stairs: stringers | conforms (start below the landing; nothing through the deck or fascia) | facade_close (crop `fc_head.png`), iron_stair (crop `is_main_top.png`) |
| Iron exterior stairs: rails | conforms (both rails start on capped head newels; no free ends; #1, P2) | front, iron_stair, balcony_gallery, right_side, sidewalk_trees |
| Iron exterior stairs: pickets | conforms | iron_stair, facade_close |
| Iron exterior stairs: curl | conforms (continuous wall-side sweep, fanned winders) | iron_stair, balcony_gallery, corner_building, aerial, top |
| Iron exterior stairs: newel | conforms (capped head, central and foot newels; the street-side rail now pitches into the central newel) | iron_stair, balcony_gallery, facade_close, front |
| Cornices and consoles | conforms | architecture_close, right_side, corner_building |
| Flat roofs | conforms | top, roof_parapets |
| Parapets | conforms (turret seam closed) | left_side, roof_parapets, top |
| Vents | conforms | top, roof_parapets |
| Chimney | deviates (one only; #9, P2) | front_corner, roof_parapets |
| Front yards: paving | conforms | iron_stair, front |
| Front yards: fences on stone curb | conforms | front, iron_stair, corner_building |
| Front yards: gaps at stairs and stoops | conforms | front, iron_stair, aerial |
| Front yards: shrubs | conforms | right_side, sidewalk_trees |
| Sidewalks: scored joints | conforms | sidewalk_trees, front |
| Sidewalks: tree pits | conforms | sidewalk_trees, front_corner |
| Sidewalks: street trees | conforms (simplified masses, allowed) | sidewalk_trees, left_side |
| Roadway | conforms | sidewalk_trees, top |
| Parked cars along far curbs | conforms (simple massing, allowed) | sidewalk_trees, left_side, top |
| Context rows | conforms with P2s (cube caps #7, proud glass #13) | left_side, right_side, aerial, roof_parapets |
| Block interior: lawn with trees | conforms | rear, rear_yards, front_corner |
| Materials hierarchy (limestone, brick, teal metal, slate, black iron, timber, concrete, asphalt) | conforms | corner_building, front, mansard_caps, architecture_close |

## 4. Camera validity

- **front**: valid. The subject is legible and unoccluded, and it matches sources/front.png in role and direction. The camera is closer and lower than the source (#3, P2).
- **front_corner**: valid. It matches sources/oblique.jpg in direction, height and arris placement, and is slightly wide (#5, P2).
- **top**: valid. Plan orientation and framing match sources/top.jpg, but the view is more nadir (#4, P2).
- **aerial, left_side, right_side, rear, rear_side**: valid. Targets are legible, and nothing is clipped or occluded.
- **corner_building**: valid. The corner cap, dormers and finial clear the top edge, and the quoins, pavilion, belt courses, cornice and both street walls are in frame.
- **iron_stair**: valid. The main stair head is cut by the top edge (#2, P2), but the green-plex stair head and the main stair's flight, curl, newels and foot are fully legible.
- **facade_close, architecture_close, glass_close, balcony_gallery, mansard_caps, sidewalk_trees, roof_parapets, rear_yards**: valid. architecture_close crops the turret's lower shaft but keeps the corbel, cornice band, spire and consoles legible.
- No view is illegible, and no whole-envelope view is occluded by trees or foreground.

## 5. Previous findings

### v002 (0 P0 / 1 P1)

| v002 finding | status in v003 | evidence |
|---|---|---|
| P1 F1: the wall-side handrail head ends free above the deck end and reads as a black bar rising through the gallery deck and railing, stopping in mid-air | **fixed** | In every view v002 cited, the bar now ends in a capped newel post, with no free end. v002/v003 crops: `cmp_front_head.png` (front x895–970, y310–390), `cmp_rs_head.png` (right_side x1100–1175, y740–810) and `cmp_is_main_head.png`. Single crops: `is_green_top.png`, `bg_top.png` and `st_stair.png`. From above the deck (balcony_gallery, right_side), the newel visibly stands at the wall-side corner of the stair opening, past the deck end, on the landing-tread line. The street-side rail also dies into its own capped head newel, which ends the gallery front railing. Residual perception note only: #1, P2. |
| P2 F12: level stub at the central newel | **fixed** | `cmp_front_foot.png`, `bg_foot.png`, `is_main_foot.png` |
| P2 F2–F11, F13 | not fixed (unchanged; carried as #3–#13) | same views as v002; non-stair pixels are identical to v002 |

### v001 (0 P0 / 6 P1)

| v001 finding | status in v003 | evidence |
|---|---|---|
| P1-1: stringer through the gallery deck; stair arriving under the fascia; balcony brace through the stringer | **fixed** (all parts, now including the bar v002 left) | crop `fc_head.png`: the landing tread is flush with the deck end, the stringers start below it and nothing rises through the deck or fascia. Crops `is_green_top.png` and `st_stair.png`: the stair-side bracket runs clear of the stringer, with no X. |
| P1-2: curl does not read (Z-jog in the handrail, loose tall newel) | **fixed, holds** | `is_main_foot.png`, `bg_foot.png`, `cb_stair.png`, `fcn_stairs.png`: continuous wall-side sweep to a capped foot newel, fanned winders, no Z-jog. The street-side rail now pitches cleanly into the central newel. |
| P1-3: pure-black slit at the turret/parapet seam (left_side) | **fixed, holds** | The darkest pixel at x240–260, y300–360 is RGB (71,74,73), which is lit stone. left_side differs from v002 only at the stairs (x400–600, y600–760). |
| P1-4: rear windows as flat dark rectangles | **fixed, holds** | rear and rear_yards are bit-identical to v002: framed windows with depth and sills (glass tone P2 #11). |
| P1-5: context rows boarded up | **fixed, holds** | The context windows and picketed balconies are unchanged from v002 (left_side and right_side differ only at the stairs). |
| P1-6: corner_building camera cuts the corner cap | **fixed, holds** | corner_building differs from v002 by 18 px in total. The cap, dormers and finial clear the top edge. |

Regressions: none found. Outside stair heads and feet, no render changed from v002. Inside them, the only changes are the new head newels, the rails dying into them, and the street-side rail pitching into the central newel.
