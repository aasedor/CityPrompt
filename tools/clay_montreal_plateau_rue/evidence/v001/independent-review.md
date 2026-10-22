# Independent RLASM v6.1 review: clay-montreal-plateau-rue v001

Verdict: FAIL

Counts: P0=0 P1=6 P2=8

## 1. Verdict

Verdict: FAIL (brief status: VISUAL_REWORK_REQUIRED). The street scene is right: a corner of two one-way rues, continuous three-storey plex walls, a brick and limestone corner plex with corner and end teal caps, turret plexes, curling black iron stairs, gallery balconies, fenced yards and a tree-lined sidewalk all read correctly against the three locked views. It still has six P1 defects visible at review scale. Two are at the stair-to-gallery junction and the stair curl, which are identity elements. One is a pure-black geometry slit. Two are flush, depthless window openings on the rear faces and on the context rows. One is a detail camera that crops off the corner mansard cap.

Reviewer method: I opened all 3 sources, all 18 renders at 1440 px and all 4 phone boards with the Read tool. I made zoomed crops (written only to `review/crops_qkvmzt/`) for the top-view party lines, the stair tops and bottoms, the left_side slit, the rear windows and the context balconies, and sampled pixel values where black needed classifying.

How I told black geometry defects from dark-by-design parts and shadow: the scene's genuine contact and soffit shadows never fall below about RGB 40–60, for example under the gallery decks, under the stair flights and in the yards. The black iron stairs, railings and fences are a uniform near-black (about 15–30) and keep their member shapes: treads, pickets and stringers, with lit wall visible between members. A defect is a region that is near-black and also has no member shape (a slit or slab), or that sits where no iron element exists.

## 2. Findings

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | front (≈ x940–980, y300–385), iron_stair (≈ x1150–1370, y120–390), balcony_gallery (≈ x380–760, y640–800) | At the top of the main stair, a black stringer bar sticks up through the blue-fascia gallery deck and stands inside the railing, as a diagonal stub between the pickets (crop `front_deck_bar.png`). In iron_stair the top stringer block pokes through the bottom of the fascia. The top tread arrives at the underside of the fascia, not at deck level. The balcony's diagonal knee-brace runs straight through the stair's outer stringer, forming an X. | The stair flight length/rise is computed to the deck underside plus overshoot, and the stringer is not trimmed at the deck plane. The knee-brace is placed without checking it against the stair. | Set the stair's top landing elevation to the deck top and trim both stringers at the deck's front edge. Add an opening or gate in the gallery railing where the stair arrives. Move or shorten the knee-brace on the stair side, or drop it there, so it no longer intersects the stringer. Apply this to every plex stair instance. |
| 2 | P1 | iron_stair (≈ x570–800, y480–900), front (≈ x640–800, y600–900), balcony_gallery (≈ x0–320, y740–1080), crops `ironstair_base.png`, `front_stair_base.png`, `bg_stair.png` | The quarter-turn "curl" does not read as a curl. The outer handrail climbs past the turn, then jogs horizontally back toward the wall and climbs again, a Z-kink that looks like a broken rail. The bottom newel is a free-standing square post, roughly 0.8–1 m taller than the rail. It is not joined to the rail end, which stops on a thin picket beside it. The winder treads in the turn read as a jumbled dark block, not as fanned treads. | The rail is built as separate straight segments per flight with no swept segment through the winders. The newel height and position come from a separate constant that is not tied to the rail end. | Sweep the outer handrail as one continuous curve over the winder arc, from the flight down to the newel. Cap the newel at rail height and terminate the rail on the newel cap. Fan the winder treads radially about the newel so each tread edge is visible. (The corner plex's north-end stair in corner_building and `corner_left_end.png` already does this correctly and can serve as the reference.) |
| 3 | P1 | left_side (x≈246–248, y≈312–355), crop `leftside_slit.png` | A hairline vertical slot, 2–3 px wide and about 40 px tall, between the end plex's parapet return and the turret's corbelled cornice. Sampled values go down to RGB (3,4,4). Both neighbours are lit stone at RGB 114–126. Sky would be grey at about 150, and no shadow in the scene is this dark, so this is a see-through gap onto an unlit back-face or void, not shadow or iron. | The parapet or cornice return of the row-end plex stops short of the turret mass, or a back-face is exposed at the seam. | Extend the parapet/cornice return to overlap the turret by at least one cornice depth, or close the seam with a cap piece. Re-check every turret/parapet junction (both turret plexes). |
| 4 | P1 | rear, rear_yards (crop `rear_windows.png`), roof_parapets, rear_side | All rear facades of the subject plexes, including the corner plex's courtyard faces, have window openings drawn as flat dark rectangles flush with the wall, with only a thin white sill. There is no reveal, frame, glazing bar or lintel. This breaks the visible grammar: street windows have coloured frames, sills, lintels and a clear reveal (glass_close). It is the "openings without visible depth/returns" failure the brief names. | The rear elevation uses a decal or solid-inset shortcut, not the street-front window assembly. | Reuse the street window assembly at reduced detail on rear faces: a recessed glazing panel (about 8–12 cm reveal), a simple frame and sill, and optionally a plain lintel. Keep the rear plain (no balconies needed), but give every opening depth. |
| 5 | P1 | right_side (x≈60–190, y≈490–700), left_side (x≈1270–1340, y≈500–700), aerial (top-left row), roof_parapets, rear, sidewalk_trees; crop `context_rail.png` | The context rows across both streets look boarded-up. Every window is a flush brown panel with no glass tone, frame or reveal. Every balcony is a timber shelf carrying a solid opaque black slab where an iron railing should be. The slabs are dark-by-design in colour but have no picket structure, so at review scale they read as black boards or patches. They fill half the frame in left_side and right_side. | The context building generator uses a solid box for the railing and a coplanar panel for the window. | Swap the railing slab for a rail plus 4–6 pickets (or an alpha-free bar grid), and replace the window panels with recessed glazing in the source glass tone plus a white sill. This keeps the context plainer than the subject while making it coherent. |
| 6 | P1 | corner_building | The detail camera for the corner building cuts the corner mansard cap at the top edge of the frame, about the top 40% of the cap and dormers. The corner cap is a named identity element of this building. The view otherwise frames the quoins, pavilion, belt courses and cornice well. | The camera is too close or aimed too low for the cap's height. | Raise the target or pull back by about 10–15% so the cap's finial clears the top edge with a margin. |
| 7 | P2 | front vs sources/front.png | The subject and composition match: the near limestone plex with a blue door pair, a red upper door and a blue-fascia gallery, the row receding left, and a street tree at left. But the camera stands on the sidewalk closer to the facade, so the near plex fills about 45% of the width against about 26% in the source. The roadway, about a third of the source frame, is almost out of frame. | The camera position is offset toward the building. | Move the camera about 3–4 m outward to the curb/roadway edge and widen slightly. |
| 8 | P2 | top vs sources/top.jpg | The plan and framing match: corner at bottom centre, north street up-left, east street up-right, curb return, corner roof about 42% of the width in both. The render is near-nadir, while the source has a forward tilt that shows the east-row facades. | Camera pitch. | Tilt about 20–25° toward the block interior. |
| 9 | P2 | front_corner vs sources/oblique.jpg | The angle matches: the corner arris near the centre, the brick-with-quoins north face to the left and the limestone pavilion on the east face to the right. The render is a little wider, so it exposes the whole empty block-interior lawn, where the source shows mature trees behind the roofs. | Camera distance and focal length. | Pull in about 10% and/or add more interior tree masses. |
| 10 | P2 | facade_close, balcony_gallery, front, corner_building | Door pairs carry a white horizontal lower panel that reads as a kick-plate, not as a coloured panel. The corner plex's east-face entrance is a single narrow leaf where a pair is expected. | Door module material assignment. | Paint the lower panels in the door colour with a slightly darker inset. Use a door pair on the corner plex. |
| 11 | P2 | left_side, right_side, aerial, roof_parapets | The context rows' "teal caps" are plain cubes on the parapet. They read as rooftop boxes, not mansard caps. | Low-detail context primitive. | Use a frustum or a pyramid. |
| 12 | P2 | left_side | The north row ends in a blank, untextured grey party wall standing on lawn, which reads as a cut model edge. | Modelled extent. | Give the row end a stone-scored or brick party wall with a parapet, or extend the row by one plex beyond the frame. |
| 13 | P2 | front_corner, aerial, roof_parapets | Only the corner plex has a chimney. The sources show a chimney or stack on most plex roofs. | Roof furniture generation. | Add a small brick chimney per plex at the party line. |
| 14 | P2 | front, facade_close | Third-floor balconies are about the same width and depth as the second-floor galleries. The sources show smaller third-floor balconies. | One shared balcony module. | Scale the third-floor deck to about 60–70% width and depth. |

Top view, dark-stripe check: no dark stripes from open gaps between buildings. All party lines are continuous lit parapets (crops `top_left_row.png`, `top_right_row.png`, `top_corner.png`). The only near-black shapes in top are the curling iron stairs in the front yards, which keep their tread and curl outline, and the vent boxes. I found no wedges or slots.

Iron stairs read as open stairs: yes, in front, iron_stair, right_side, sidewalk_trees, fc/aerial crops and corner_building. The stairs have separate treads, sawtooth stringers and pickets, with lit wall and windows visible between treads. Exceptions are the junction and curl defects in findings 1–2. In balcony_gallery the flight seen from below reads as a denser mass. That is the underside of treads and stringers, not a slab: the sawtooth outline stays legible.

## 3. Source conformance checklist

| item | status | view(s) used |
|---|---|---|
| Plan: two streets meeting at a corner | conforms | top, front_corner, aerial |
| Plan: building lines (continuous street walls on both streets) | conforms | top, front_corner, aerial |
| Plan: front yards | conforms | front, iron_stair, front_corner, top |
| Plan: sidewalks | conforms | sidewalk_trees, front, top |
| Plan: roadways | conforms | top, sidewalk_trees, left_side, right_side |
| Plan: curb returns | conforms | top, front_corner |
| Corner building: limestone corner pavilion (east street) | conforms | corner_building, front_corner |
| Corner building: limestone quoins (north street) | conforms | corner_building, fc crop |
| Corner building: brick | conforms | corner_building |
| Corner building: windows (three floors, stone sills and lintels) | conforms | corner_building |
| Corner building: belt courses | conforms | corner_building |
| Corner building: mitred bracketed cornice round the corner | conforms | corner_building, front_corner |
| Corner building: corner mansard cap | conforms (but cropped in corner_building, F6) | front_corner, top, roof_parapets |
| Corner building: end mansard caps | conforms | front_corner, mansard_caps, rear_side |
| Corner building: north-end balcony and stair | conforms | corner_building, crop `corner_left_end.png` |
| North row turret plex: corbel | conforms | left_side |
| North row turret plex: octagonal turret | conforms | left_side, architecture_close, top |
| North row turret plex: turret windows | conforms | left_side |
| North row turret plex: slate spire | conforms | architecture_close, left_side |
| North row: limestone and brick plexes, second turret plex | conforms | front, left_side, aerial |
| East row: brick and limestone plexes | conforms | right_side, aerial |
| East row: stone bays and teal caps at the party lines | conforms | right_side, aerial crop, mansard_caps |
| Doors and door pairs: colours (blue, green, red) | conforms | front, facade_close, balcony_gallery |
| Doors and door pairs: stoops | conforms | front, iron_stair, corner_building |
| Doors: panelling and detail | deviates (white kick-plate panel; single leaf on corner east door, F10) | facade_close, corner_building |
| Windows: coloured frames | conforms | glass_close, facade_close |
| Windows: transoms | conforms | glass_close |
| Windows: sills and lintels | conforms (street faces) / deviates (rear faces flush, F4) | glass_close, rear_yards |
| Gallery and third-floor balconies: decks | conforms | balcony_gallery |
| Gallery and third-floor balconies: painted fascias | conforms | balcony_gallery, facade_close |
| Gallery and third-floor balconies: brackets | deviates (knee-brace intersects stair, F1) | iron_stair |
| Gallery and third-floor balconies: railings | conforms | facade_close, balcony_gallery |
| Gallery and third-floor balconies: smaller third-floor balcony | deviates (F14) | front, facade_close |
| Iron exterior stairs: treads | conforms | iron_stair, front |
| Iron exterior stairs: stringers | deviates (top stringer pierces deck, F1) | front, iron_stair |
| Iron exterior stairs: rails | deviates (Z-kink at curl, F2) | iron_stair, balcony_gallery |
| Iron exterior stairs: pickets | conforms | iron_stair, facade_close |
| Iron exterior stairs: curl | deviates (does not read as a swept curl, F2) | iron_stair, front |
| Iron exterior stairs: newel | deviates (oversized free-standing post, F2) | iron_stair, front |
| Cornices and consoles | conforms | architecture_close, right_side, corner_building |
| Flat roofs | conforms | top, roof_parapets |
| Parapets | conforms (except the turret seam slit, F3) | roof_parapets, top, left_side |
| Vents | conforms | top, roof_parapets |
| Chimney | deviates (one only, F13) | front_corner, roof_parapets |
| Front yards: paving | conforms | iron_stair, front |
| Front yards: fences on stone curb | conforms | front, iron_stair, corner_building |
| Front yards: gaps at stairs and stoops | conforms | front, iron_stair |
| Front yards: shrubs | conforms | right_side, sidewalk_trees |
| Sidewalks: scored joints | conforms | sidewalk_trees, front |
| Sidewalks: tree pits | conforms | sidewalk_trees, front_corner |
| Sidewalks: street trees | conforms (simplified masses, allowed) | sidewalk_trees |
| Roadway | conforms | sidewalk_trees, top |
| Parked cars along far curbs | conforms (simple massing, allowed) | sidewalk_trees, top, left_side |
| Context rows | deviates (boarded-look windows, black slab railings, cube caps; F5, F11) | right_side, left_side, aerial, roof_parapets |
| Block interior: lawn with trees | conforms | rear, rear_yards, front_corner |
| Materials hierarchy (limestone, brick, teal metal, slate, black iron, timber, concrete, asphalt) | conforms | corner_building, front, mansard_caps, architecture_close |

## 4. Camera validity

- **front**: valid. The subject is legible and unoccluded. Compared with sources/front.png, the angle and composition match: the near plex at right, the row receding left and a tree at left. The camera is closer and on the sidewalk, so the roadway is mostly out of frame (P2, F7).
- **front_corner**: valid. It matches sources/oblique.jpg in viewing direction, height and the placement of the corner arris and both faces. It is slightly wider and exposes the empty interior lawn (P2, F9).
- **top**: valid. It matches sources/top.jpg in plan orientation, with the corner at bottom centre and the streets running up-left and up-right, and in framing. It is more nadir than the source's tilted view (P2, F8). There are no dark gap stripes.
- **aerial, left_side, right_side, rear, rear_side**: valid. The target is legible, with nothing clipped or occluded.
- **facade_close, glass_close, balcony_gallery, iron_stair, mansard_caps, sidewalk_trees, roof_parapets, rear_yards, architecture_close**: valid. Architecture_close crops the turret's lower shaft but keeps the turret band, spire, cornice and consoles, which are the target, fully legible.
- **corner_building**: the target is partly clipped. The corner mansard cap is cut at the top edge (P1, F6). Everything else in the view is legible.
- No view is illegible. No whole-envelope view has its target occluded by trees or foreground.
