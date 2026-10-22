# Independent RLASM v6.1 review: clay-montreal-plateau-rue v002

Verdict: FAIL

Counts: P0=0 P1=1 P2=12

## 1. Verdict

Verdict: FAIL (brief status: VISUAL_REWORK_REQUIRED). v002 fixes five of the six v001 P1s outright. The quarter-turn curl and its newels now read, the left_side slit is closed, rear windows have frames and depth, the context rows are no longer boarded up, and the corner_building camera clears the cap. The stair-head part of v001 finding 1 is only partly fixed. The stringer, landing and brace are now correct, but the most visible symptom is still there in every stair-head view, including the hero front view: a black iron bar that seems to rise out of the gallery deck inside its railing and stop in mid-air.

Reviewer method: I opened all 3 locked sources, all 18 renders at 1440 px and all 4 phone boards with the Read tool. I also opened the v001 front, iron_stair and right_side renders to check for regressions. Zoomed crops are only in `review/crops_hvtrnk/`. I sampled pixel values and searched each render for solid near-black blobs (pixels under 20 that are at least 9 px thick). For finding 1 only, I projected the delivered GLB's hardware triangles through the iron_stair and balcony_gallery cameras to identify the member the pixels show. The finding itself rests on the pixels.

How I told black defects from dark-by-design parts and shadow: lit-scene contact and soffit shadows stay above about RGB 40. Examples are under the gallery decks, under the flights and in the yards. The black iron (stairs, railings, fences, newels) is uniformly about 6–30, but it keeps its member shapes: treads, sawtooth stringers and pickets, with lit wall showing between members. Car windows and roof vents are dark-by-design blocks inside a clear outline. Glass in deep shade can also be near-black. One example is the ground-floor transoms under the galleries (about 13–16), which sit inside a white frame with a reveal. I count a region as a geometry defect when it is near-black and has no member or frame shape (a slot, wedge or slab), or when it is an iron member where none belongs. The blob search found only stairs, fences, railings, framed transoms, car glass and vents. No view has a geometry slot, wedge or slab.

## 2. Findings

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | front (≈ x895–970, y310–390, crop `front_stair_top.png`), iron_stair (green plex ≈ x385–430, y190–280, crop `is_green_top.png`), balcony_gallery (≈ x395–520, y465–640, crop `bg_top.png`), right_side (≈ x1100–1175, y740–810, crop `rs_stair.png`), sidewalk_trees (≈ x990–1020, y375–425, crop `st_stair.png`) | At every plex stair head, a black diagonal bar about 0.5–0.6 m long seems to grow out of the gallery's deck/fascia at the open end. It rises through the gallery railing pickets and stops in mid-air at rail height, with a free, uncapped end. This is the same symptom v001 F1 described as "a black stringer bar sticks up through the gallery deck and stands inside the railing", at the same place in front.png. In v002 it is not the stringer. Projecting the GLB through the iron_stair and balcony_gallery cameras shows it is the head of the stair's wall-side handrail: for the green plex, x ≈ -0.30, y 40.72→41.3, z 4.94→4.49, just past the deck end at y ≈ 40.7. Its first segment ends free 0.3 m off the wall. It meets no newel, wall bracket or gallery-railing return, because the gallery railing's stair-end return was removed. From any viewpoint below or beside the deck, the rest of the rail is hidden behind the deck. Only the rising head shows, seen through the railing. At review scale it reads as an iron member through the gallery, an intersecting/floating part. In the source front, the stair rails turn into the gallery railing with no loose end. | `ext_stair` starts the wall-side handrail at `s_in` (deck end + 3 cm, d = −0.3, deck top + 0.92 m) with nothing at its head. `balcony(..., open_end=...)` drops the whole stair-side return, so neither the rail nor the railing ends on a post. | Terminate the wall-side rail on a stair-head newel standing on the landing tread at d = −0.3, capped at rail height. Alternatively, keep a short stair-end railing return from the wall out to d ≈ −0.35 and end the rail on its post. Give the street-side rail head a matching post at the gallery railing's front end post, or join it to that post. Apply this to every plex stair and the corner building's stair. Re-check front, iron_stair, balcony_gallery, right_side and sidewalk_trees for any free rail head above the deck. |
| 2 | P2 | front vs sources/front.png | The composition matches, but the camera is still on the sidewalk close to the facade. The near plex fills about 45% of the width (source about 26%) and the roadway is barely in frame. This carries over v001 F7. | Camera offset. | Move the camera about 3–4 m out to the curb/roadway edge and widen slightly. |
| 3 | P2 | top vs sources/top.jpg | The plan and framing match, but the render is near-nadir. The source tilts enough to show the east-row facades. This carries over v001 F8. | Camera pitch. | Tilt about 20–25° toward the block interior. |
| 4 | P2 | front_corner vs sources/oblique.jpg | The angle and arris placement match. The view is slightly wider and shows the bare interior lawn where the source has mature trees behind the roofs. This carries over v001 F9. | Distance/focal length. | Pull in about 10% and/or add interior tree masses. |
| 5 | P2 | facade_close, front, balcony_gallery, sidewalk_trees, corner_building | The door pairs still carry a white lower panel that reads as a kick-plate. The corner plex's east-face entrance is still a single narrow leaf (corner_building ≈ x930–955, y745–850). This carries over v001 F10. | Door module material and corner door width. | Paint the lower panels in the door colour with a darker inset, and use a door pair at the corner entrance. |
| 6 | P2 | left_side, right_side, aerial, roof_parapets, rear_side | The context rows' teal "caps" are still plain cubes. This carries over v001 F11. | Low-detail context primitive. | Use a frustum or pyramid. |
| 7 | P2 | left_side (x0–270, crop `ls_end.png`) | The north row still ends in a blank grey party wall standing on lawn. This carries over v001 F12. | Modelled extent. | Score or brick the party wall and give it a parapet, or extend the row one plex past the frame. |
| 8 | P2 | front_corner, aerial, roof_parapets | Only the corner plex has a chimney. This carries over v001 F13. | Roof furniture. | Add a small brick chimney per plex at a party line. |
| 9 | P2 | front, facade_close | The third-floor balconies are shallower than the galleries but the same width. The sources show visibly smaller ones. This carries over v001 F14. | Shared balcony span. | Cut the third-floor balcony width to about 60–70%. |
| 10 | P2 | rear, rear_yards, roof_parapets (crops `ry_windows.png`, `rp_windows.png`) | The new rear windows have frames, depth and sills, so v001 F4 is fixed. On brick walls, though, the glass reads brick-brown: sampled median (102,76,65) against brick (132,90,69). On limestone the glass reads pale grey-green (97,104,98). At distance the brick-wall windows read as tinted or filled panels rather than glass. | The glass slab sits over solid wall, so its transparency shows the wall colour. | Give the rear glass an opaque dark glass tone matching the street glass (about 50 grey), or back it with a dark panel. |
| 11 | P2 | front (≈ x1060–1310, y470–510), facade_close (≈ x805–1085, y855–895), sidewalk_trees, balcony_gallery (crops `front_transom.png`, `fc_transom.png`, `st_transom.png`) | The ground-floor door transoms under the galleries render near-black (median about 13–16). They are framed glass with a reveal, so they are dark-by-design glass in deck shade, not a slot. Still, they are the darkest flat areas on the facades. This is unchanged from v001. | The glass tone combined with soffit shade. | Lighten the glass slightly or add a faint reflection so the shaded transoms read near 35–45. |
| 12 | P2 | iron_stair, front, balcony_gallery (crops `is_main_foot.png`, `bg_foot.png`) | The street-side rail levels off in a short horizontal stub into the central newel cap. This is acceptable as a newel termination, but it reads as a small kink beside the clean wall-side sweep. | The last handrail segment runs from the flight foot to the newel centre at the same height. | Ramp the last segment slightly into the cap, or extend the flight pitch to the newel face. |
| 13 | P2 | left_side, right_side (crops `ls_context.png`, `rs_context.png`) | The context window glass stands slightly proud of its white surround instead of being recessed. At review scale it still reads as glazed windows. | Context window layering. | Set the glass 2–3 cm behind the surround face. |

Top view, dark-stripe check (crops `top_left.png`, `top_right.png`): all party lines are continuous lit parapets. I found no dark gap stripes or wedges. The only near-black shapes are the curling stairs, which keep their tread and curl outline, and the roof vents.

Iron stairs read as open stairs in front, iron_stair, right_side, sidewalk_trees, aerial, left_side and corner_building. They have separate open-riser treads, sawtooth stringers and pickets, with lit wall showing between members. The quarter-turn curl now reads in every view where it is visible. In balcony_gallery, the flight seen from below is a dense dark mass, but the sawtooth outline stays legible. It is the treads' underside, not a slab.

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
| Corner building: corner mansard cap | conforms (now fully framed) | corner_building (crop `cb_cap.png`), front_corner, top |
| Corner building: end mansard caps | conforms | front_corner, roof_parapets, rear_side |
| Corner building: north-end balcony and stair | conforms (curl reads, crop `cb_stair.png`; the stair head shares finding 1 by construction but is not visible in these views) | corner_building, front_corner |
| North-street turret plex: corbel | conforms | left_side, architecture_close |
| North-street turret plex: octagonal turret | conforms | left_side, architecture_close, top |
| North-street turret plex: turret windows | conforms | left_side |
| North-street turret plex: slate spire | conforms | architecture_close, left_side |
| North-street row: limestone and brick plexes, second turret plex | conforms | front, left_side, aerial, rear_side |
| East-street row: brick and limestone plexes | conforms | right_side, aerial |
| East-street row: stone bays and teal caps at the party lines | conforms | right_side, mansard_caps, aerial |
| Doors and door pairs: colours (blue, green, red) | conforms | front, facade_close, balcony_gallery |
| Doors and door pairs: stoops | conforms | front, iron_stair, corner_building |
| Doors: panelling | deviates (white kick-plate panel, corner single leaf; F5, P2) | facade_close, corner_building |
| Windows: coloured frames | conforms | glass_close, facade_close |
| Windows: transoms | conforms (shaded ground-floor transoms very dark; F11, P2) | glass_close, facade_close, front |
| Windows: sills and lintels | conforms (street faces; rear faces now framed with sills, glass tone off on brick; F10, P2) | glass_close, rear_yards, roof_parapets |
| Gallery and third-floor balconies: decks | conforms | balcony_gallery, facade_close |
| Gallery and third-floor balconies: painted fascias | conforms | balcony_gallery, facade_close |
| Gallery and third-floor balconies: brackets | conforms (stair-side bracket now clear of the stringer) | iron_stair, balcony_gallery, sidewalk_trees |
| Gallery and third-floor balconies: railings | deviates (stair-end return removed with no post where the stair rail arrives; F1) | balcony_gallery, front, right_side |
| Gallery and third-floor balconies: smaller third-floor balcony | deviates (same width; F9, P2) | front, facade_close |
| Iron exterior stairs: treads | conforms (landing tread flush with the deck) | facade_close, iron_stair |
| Iron exterior stairs: stringers | conforms (start below the landing, nothing through the deck or fascia) | iron_stair (crop `is_main_top.png`), facade_close |
| Iron exterior stairs: rails | deviates (wall-side rail head ends free above the deck end; F1) | front, iron_stair, balcony_gallery, right_side, sidewalk_trees |
| Iron exterior stairs: pickets | conforms | iron_stair, facade_close |
| Iron exterior stairs: curl | conforms (continuous wall-side sweep, fanned winders) | iron_stair, balcony_gallery, corner_building, aerial |
| Iron exterior stairs: newel | conforms (central and foot newels capped at rail height, rails land on them) | iron_stair, balcony_gallery, facade_close |
| Cornices and consoles | conforms | architecture_close, right_side, corner_building |
| Flat roofs | conforms | top, roof_parapets |
| Parapets | conforms (turret seam closed) | left_side (crop `ls_seam.png`), roof_parapets, top |
| Vents | conforms | top, roof_parapets |
| Chimney | deviates (one only; F8, P2) | front_corner, roof_parapets |
| Front yards: paving | conforms | iron_stair, front |
| Front yards: fences on stone curb | conforms | front, iron_stair, corner_building |
| Front yards: gaps at stairs and stoops | conforms | front, iron_stair, aerial |
| Front yards: shrubs | conforms | right_side, sidewalk_trees |
| Sidewalks: scored joints | conforms | sidewalk_trees, front |
| Sidewalks: tree pits | conforms | sidewalk_trees, front_corner |
| Sidewalks: street trees | conforms (simplified masses, allowed) | sidewalk_trees, left_side |
| Roadway | conforms | sidewalk_trees, top |
| Parked cars along far curbs | conforms (simple massing, allowed) | sidewalk_trees, left_side, top |
| Context rows | conforms with P2s (framed glazed windows, picketed balconies; cube caps F6, proud glass F13) | left_side, right_side, aerial, roof_parapets |
| Block interior: lawn with trees | conforms | rear, rear_yards, front_corner |
| Materials hierarchy (limestone, brick, teal metal, slate, black iron, timber, concrete, asphalt) | conforms | corner_building, front, mansard_caps, architecture_close |

## 4. Camera validity

- **front**: valid. The subject is legible and unoccluded, and it matches sources/front.png in role and direction. The camera is closer and lower on the sidewalk (P2, F2).
- **front_corner**: valid. It matches sources/oblique.jpg in direction, height and arris placement. It is slightly wide (P2, F4).
- **top**: valid. It matches sources/top.jpg in plan orientation and framing, but is more nadir (P2, F3).
- **aerial, left_side, right_side, rear, rear_side**: valid. Targets are legible, and nothing is clipped or occluded.
- **corner_building**: valid. It is now fixed: the corner cap, dormers and finial clear the top edge with a margin, and the quoins, pavilion, belt courses, cornice and both street walls are in frame.
- **facade_close, architecture_close, glass_close, iron_stair, balcony_gallery, mansard_caps, sidewalk_trees, roof_parapets, rear_yards**: valid. architecture_close crops the turret's lower shaft but keeps the target fully legible: the corbel band, the cornice band, the spire and the consoles.
- No view is illegible, and no whole-envelope view is occluded by trees or foreground.

## 5. Previous findings (v001: 0 P0 / 6 P1)

| v001 finding | status in v002 | evidence |
|---|---|---|
| P1-1 stair stringer through the gallery deck; stair arriving under the fascia; balcony brace through the stringer | **not fixed (partly fixed)** | Fixed: the landing tread now sits at deck level next to the deck end (facade_close crop `fc_top.png`, iron_stair crop `is_main_top.png`). The stringers start below the landing and nothing rises through the deck or fascia. The stair-side bracket no longer forms an X with the stringer. Not fixed: the bar in the gallery that v001 cropped as `front_deck_bar.png` is still there, in the same place in front.png and in iron_stair, balcony_gallery, right_side and sidewalk_trees. It is the free head of the wall-side handrail (finding 1). |
| P1-2 curl does not read (Z-jog in the handrail, loose tall newel) | **fixed** | The wall-side rail sweeps continuously round the quarter turn to a capped foot newel. The street-side rail lands on a capped central newel, and the winders fan visibly (crops `is_main_foot.png`, `bg_foot.png`, `front_stair_foot.png`, `cb_stair.png`). The Z-jog is gone. A small level-off stub at the central newel remains (P2, F12). |
| P1-3 pure-black slit at the turret/parapet seam (left_side) | **fixed** | At the former slit location (x 240–260, y 300–360), the darkest pixel is now RGB (71,74,73), which is lit stone. The seam reads closed (crop `ls_seam.png`). |
| P1-4 rear windows as flat dark rectangles | **fixed** | Every rear window now has a proud white frame, recessed glass and a stone sill (crops `ry_windows.png`, `rp_windows.png`). The glass tone on brick walls is off (P2, F10). |
| P1-5 context rows boarded up | **fixed** | Context windows have a white surround and grey glass. Context balconies have top and bottom rails with pickets and open returns, and no black slabs (crops `ls_context.png`, `rs_context.png`). Minor: the glass stands proud of the surround (P2, F13). |
| P1-6 corner_building camera cuts the corner cap | **fixed** | The cap, both dormers and the finial clear the top edge (crop `cb_cap.png`). |

Regressions: none found. I compared v002 against v001 for front, iron_stair and right_side directly, and for every other view against the v001 review's description. Nothing that conformed in v001 deviates in v002. The v001 P2s (F7–F14) are unchanged and are carried over above as F2–F9.
