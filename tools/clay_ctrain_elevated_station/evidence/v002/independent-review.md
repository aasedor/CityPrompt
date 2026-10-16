# Independent holistic review: ctrain v002 (RLASM v6.1 architectural clay)

I judged this from rendered pixels only. I opened the three locked sources (front.png, oblique.jpg, top.jpg), all 18 renders at full resolution and the four phone boards. Zoomed crops are in `review/crops-indep/`, a new folder. No other file was modified.

## 1. Verdict

**VISUAL_REWORK_REQUIRED**: the station's topology now reads correctly and most v001 defects are fixed in the pixels. Four P1 defects remain:
- The front is still not the source's street-level view, and the side views are too small to read.
- An invented ramp to grade replaces the level elevated guideway that the sources show south of the platforms.
- The pale tower caps carry a pure-black stripe.

Counts: P0 = 0, P1 = 4, P2 = 8

## 2. Findings

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | front (and phone-01) | The front is a distant, elevated overview. The roof plane, the tops of the canopies and the whole site slab are visible. The asset is only about 800 x 190 px in a 1440 x 1080 frame, about 18% of the frame height. The source front is a street-level view from the south-west at eye height. It looks up at the SW stair tower's glazed bay, with the west skywalk overhead on the left and the platform deck and train on the right. On the phone board the render front is a thin strip. The builder's claim of "a street-level front from the south-west" is not true of the pixels. | The camera is still placed for a whole-site establishing shot: high, far and wide focal length. It was not matched to the source's eye-level station point. | Put the camera about 1.6 m above the sidewalk at the SW corner of the E-W/N-S intersection, aimed at the SW tower's glazed bay, with a focal length near the source's (about 28-35 mm equivalent). Frame the tower centre-left, the skywalk underside crossing the top-left and the deck and train on the right, so the asset fills at least 70% of the frame height. |
| 2 | P1 | left_side, right_side (phone-03) | Both side views show the asset as a band about 820 x 150 px, roughly 10-14% of the frame height, with about 85% empty sky and slab. At phone size the storeys, glazed bays, skywalk truss and canopies cannot be read. This repeats the v001 framing finding. Only rear and rear_side are framed adequately. | The orthographic-style side cameras are still sized to the full site extent, including the long ramp and the skywalk pavilions, at a large distance. | Re-frame each side view to the asset's bounding box with about 8-10% margin. Remove or shorten the ramp (finding 3), which stretches the bounding box. Lower the camera so the ground line sits in the lower third. |
| 3 | P1 | front, front_corner, aerial, left_side, top (phone-01) | Right at the platforms' south ends the guideway turns into a long sloping ramp to grade, with low parapets and rails. It is as long as the headhouse is deep and dominates the south half of every whole-envelope silhouette. The sources show the opposite. In top.jpg the guarded double-track deck continues level southward past the platform-end stairs to the image edge. In oblique.jpg the deck continues level to the south-east on a round pier with glass guards. The ramp is invented geometry that changes the identity silhouette of "guideway deck on piers". At this length it would also be an implausibly steep grade for light rail. | The builder over-corrected v001's "open deck end" by inventing a terminus instead of continuing the source's level deck to the site edge. | Delete the ramp. Continue the level guarded deck south for one to two more pier bays on round piers and cap beams, matching the oblique. End it at the site boundary with a clean section cut or a short closed parapet end, flush with a pier line. Keep the platform-end stairs as they are. |
| 4 | P1 | tower_cap; visible as a dark line in rear, rear_side, front_corner, aerial | The front and side edges of each pale tower cap's top slab render pure black (sampled RGB 0,0,0 at tower_cap x=700, y=492-500). This makes a hard black stripe between the cap slab and its fascia on the identity element. A lit vertical face cannot be pure black in clay. The source caps are pale with only a soft shadowed soffit. | A black material, missing material or flipped normals on the cap top slab's side faces, or a deliberate "dark coping" outside the source palette. | Give the cap slab's side faces the same pale cap material (or recalculate their normals outward), so the edge reads as a light, slightly shaded fascia. Re-check all four views. |
| 5 | P2 | top, front_corner, facade_close | The west skywalk lands on the headhouse west face immediately north of the SW tower, beside the projecting glazed bay. In top.jpg and front.png it enters the tower itself, its roof falling within the tower's N-S extent. It is now offset by about half a tower width. | The link axis was placed at the tower's north face line, not at its centre. | Shift the west link about half a tower width south, so it frames into the glazed bay's upper level. |
| 6 | P2 | top, aerial | The glazed canopies run almost the full platform length, about 70%, over the whole street width. In top.jpg they cover about 55-60%, leaving a longer open platform with the pylons and stairs. | The canopy length is parameterised to the street rather than the source. | Shorten each canopy by about 2 bays from the south. |
| 7 | P2 | interior | The timber ledge or benches in front of the brick sill hover without supports. Their shadow on the floor is detached well away from the wall. The glazed-band mullions are flat lines without depth, and the room is otherwise bare. | Furniture is offset from the wall and has no brackets or legs. Mullions are modelled as planar strips. | Fix the ledges to the sill with brackets or set them on pedestals. Give the mullions about 5-10 cm depth. |
| 8 | P2 | facade_close | The traffic-signal mast arm's signal head is embedded in a tree crown. | A placement collision. | Move the tree or rotate the mast arm. |
| 9 | P2 | rear, rear_side | The north tail track is a very short tub-like stub, about one car length, on one or two piers, coming out of a framed opening. It reads as a balcony. The north face is not in any source, so it is judged for coherence only. | It is a minimal terminus. | Lengthen it by one bay and add a pier line matching the south piers. |
| 10 | P2 | tower_cap, facade_close | The tower's south-face glazed slot reads as unglazed at its top section, where white interior surfaces show. The sources show the tower south faces as mostly brick. | The slot glass pane stops short. | Glaze the slot to the top, or narrow or omit it to match the brick-dominant south face. |
| 11 | P2 | glass_close | A stray pale diagonal tube sits under the canopy glazing. | A leftover brace primitive. | Delete it or align it to the rafter grid. |
| 12 | P2 | street_underpass | The deck soffit fills about 45% of the frame as a uniform near-black mass. It is legible, but heavy. | There is no bounce light under the deck. | Add fill light or lower the camera pitch slightly. |

## 3. Source conformance checklist

| item | status | view used / note |
|---|---|---|
| Silhouette | **deviates** | front_corner and aerial against oblique and top: the headhouse, towers, skywalks and platforms match, but the south ramp to grade (finding 3) changes the overall silhouette. |
| Storey count | conforms | rear, left_side, front_corner: three storeys (ground, windowed second, glazed top band), with the towers rising above the roof. |
| Headhouse and glazed band | conforms | rear, architecture_close, east_skywalk: red-brick headhouse with a continuous top-storey glazed band on all faces. The south face band sits above the track portal. |
| Stair towers and caps | conforms in geometry; **deviates** in finish | facade_close, tower_cap, front_corner, east_skywalk: square brick towers at the two south corners. Wide projecting glazed bays are on the outer (west/east) faces and the pale projecting caps sit above the roof. The black cap stripe is finding 4, and the south-face slot is P2. |
| Deck and piers | conforms under the platforms; **deviates** south of them | street_underpass, front_corner: round piers with cap beams carry the deck over the E-W street. South of the platforms the deck becomes a ramp (finding 3). |
| Platforms: guards, tactile edges, pylons, stairs | conforms | aerial crop, platform_canopy, train_platform, front_corner: two side platforms either side of two tracks, glass guards on the outer edges, yellow tactile edges, a red pylon near each south end, and solid stair flights with posted handrails descending outward to the ground. |
| Canopies | conforms; length is P2 | aerial, platform_canopy, glass_close: long glazed gable canopies on steel posts, slightly too long (finding 6). |
| Skywalks | conforms; west link offset is P2 | skywalk_bridge, east_skywalk, top: a glazed steel X-truss Plus 15 skywalk leaves the west face across the west street to a glazed pavilion. The east link from beside the SE tower meets a long N-S truss skywalk on round columns, ending at glazed pavilions. |
| Train | conforms | train_platform, aerial: a two-car red-and-white light-rail train on the west track at the west platform. The bogies contact the trackbed. |
| Streets | conforms | top, street_underpass: the E-W street passes under the deck and the N-S street runs along the west face under the west skywalk. Crosswalks and lane marks are present. |
| Materials hierarchy | conforms, except the cap stripe | All views: red brick, pale caps and coping, grey steel, pale concrete deck, light glass, yellow tactile edges and red pylons and train. The pure black on the caps is outside the palette (finding 4). |

## 4. Camera validity

- **front**: the target is legible, but the view is invalid for its role. It is not the source's street-level south-west view of the tower, and the asset is far too small in the frame (finding 1).
- **left_side, right_side**: the target is not occluded or clipped, but it is too small to be legible at phone scale (finding 2).
- **interior**: valid. The camera is in the upper concourse looking south through the glazed band, with the canopies visible beyond. It is not occluded.
- **street_underpass**: valid, though dominated by a dark soffit (P2).
- **front_corner, aerial, top, rear, rear_side**: valid and legible. front_corner and aerial are somewhat loose but acceptable.
- **facade_close, architecture_close, glass_close, platform_canopy, skywalk_bridge, tower_cap, train_platform, east_skywalk**: valid. Each shows its target unoccluded and unclipped where it matters.

## 5. Previous-version (v001) findings: resolved in the pixels?

| v001 finding | status in v002 pixels |
|---|---|
| P0: interior camera occluded by an unlit slab | **Resolved.** interior.png shows the upper concourse looking south through the glazed band, with the canopies visible outside. Only P2 furniture and mullion issues remain. |
| P1: glazed stair bays narrow and flush on the south faces | **Resolved.** facade_close, tower_cap, front_corner and east_skywalk show wide glazed bays on the outer west/east faces, projecting with returned frames and running from ground to just below the cap. A narrow slot remains on the south faces (P2). |
| P1: skywalks joining well north of the stair towers | **Resolved.** Both links now land directly beside the towers (top, front_corner, east_skywalk). The west link still sits about half a tower width north of the source position (P2, finding 5). |
| P1: guideway a blocked stub (blank wall in headhouse, open deck end at south) | **Partly resolved.** At the north end, the tracks visibly pass through a portal in the headhouse to a guarded tail track with buffer stops (platform_canopy, train_platform, rear, rear_side). At the south end, the open deck end has been replaced by an invented ramp to grade that contradicts the sources' level elevated continuation. That ramp is the new P1, finding 3. |
| P1: street stairs floating ribbons with detached rails | **Resolved.** front_corner, aerial and street_underpass show solid stair flights with stringers and posted handrails. They descend outward from the platform ends and land on the ground. |
| P1: whole-envelope framing too small; front not the source's street-level view toward the SW tower | **Not resolved.** The front is still a distant elevated overview, and left_side and right_side are still tiny (findings 1 and 2). |
