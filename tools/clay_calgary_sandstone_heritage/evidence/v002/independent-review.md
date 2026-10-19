# Independent holistic review: clay-calgary-sandstone-heritage v002 (RLASM v6.1 architectural clay)

Reviewer: independent (not the builder). Evidence: the three locked sources (sources/front.png, sources/oblique.jpg, sources/top.jpg), all 18 renders at full resolution and the four phone boards. Zoomed crops for this review are in `/tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/review-crops-sand-v002-9433865c/`. Builder metadata, counts and notes were not used as proof. The builder's carrier aperture audit (FAIL) was checked only against the pixels.

## 1. Verdict

**VISUAL_REWORK_REQUIRED**: v002 fixes most of the v001 roof, pavilion, arcade and portal defects. However, the outer bay of the east and west faces of all four corner pavilions is visibly blocked by stone, with half-filled or blind windows. The tower-base entrance porch shown in both sources is missing, and the interior view shows blind window recesses.

Counts: P0 = 1, P1 = 2, P2 = 8

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P0 | right_side, left_side, east_side, front (SE pavilion east face at the corner), rear_side | On the east and west faces of all four corner pavilions, the outermost bay is filled with buff stone inside its own surrounds. Third floor: the end arcade light is a blank arch between colonnettes. Second floor: the end round-arched window has its hood mould and sill, but the opening is stone apart from a 1 to 3 px dark sliver at one jamb. First floor: one leaf of the end paired window is solid stone and the other is a sliver. Basement: the window in that bay is missing. This repeats at both ends of each E/W pavilion face, so the windows read as broken or bricked up in every whole-envelope elevation that shows these faces. It is also visible in the hero front view (blank arcade lights and a ghost arch at the SE pavilion's east corner). | When the pavilions were stepped 2 m forward, their E/W faces kept the old bay layout. The perpendicular N/S pavilion wall slab and/or the corner pier now runs through the outer bay behind the glazing plane, so a solid carrier sits inside the aperture (the same fault the builder's carrier audit reports). | Lay out the E/W pavilion bays from the clear face length, inset by the perpendicular wall thickness plus the corner pier, or boolean-cut every aperture through all intersecting carriers. Re-render right_side, left_side, east_side and front, and confirm that every E/W pavilion opening shows glass or a frame with a reveal return and no stone infill. |
| 2 | P1 | east_side, right_side, clock_tower (vs sources/front.png and sources/oblique.jpg) | Both sources show a projecting entrance at the foot of the clock tower: a deep round arch of several orders, steps, and a flat-topped porch carrying a parapeted or balustraded balcony at second-floor level. In the render the tower base is a flush shaft with a plain arched double door and no porch, balcony or steps. | The tower module was built as a plain shaft. The porch assembly was placed only at the SW pavilion. | Instance the porch assembly (arched passage, colonnettes, steps, landing, balustraded balcony) on the east face of the tower base, scaled to the tower width. Re-render east_side and right_side. |
| 3 | P1 | interior | The interior view's main subject is window reveals. The wall opposite the glazed arched window shows four tall rectangular openings as blind recesses with flat solid backs: no glass, no frame and no view out. This contradicts the glazed exterior openings and reads as blocked windows. | The interior lining or partition, or the same solid carrier as #1, closes the back of these apertures. Alternatively, the openings were cut only into the inner lining and not through the outer wall. | Cut these openings through to the exterior and place frame and glazing in each, or move the interior camera to a bay whose openings are real. Re-render interior. |
| 4 | P2 | portal_arch | At the inner end of the SW porch, the door leaf is a dim flat panel that is hard to tell apart from the passage walls. The fanlight above the transom is near-black (about RGB 4,4,3) and reads as a void. A thin dark vertical slit sits along the right jamb, which reads as a gap between the leaf and the jamb. | The leaf is narrower than the opening, and the fanlight glazing material is unlit or too dark. | Widen the leaf to the jambs, or add a centred meeting stile. Give the fanlight a lighter glass value and the leaf a distinct timber value. |
| 5 | P2 | clock_tower, east_side, right_side | Below the clock, each tower face has only two short narrow lancets and then single punched arched windows. The sources show groups of 4 to 5 very tall lancets on each face. The belfry has 3 arches per face, while the sources show a continuous ring of small arches under the spire. | The tower opening schedule was simplified. | Use 4 to 5 tall lancets per face over the upper shaft and 5 or more belfry arches per face. |
| 6 | P2 | clock_tower, front, top | The copper spire and turret caps read as a pale salmon pink (about RGB 157,128,113 in light). The sources show a saturated orange-brown copper (about RGB 117,80,62). | The copper base colour is too desaturated and too light. | Shift the copper toward a deeper orange-brown. |
| 7 | P2 | front_corner, roofs_court, gables_pinnacles | The slate is now dark, as required, but reads as a neutral near-black (about RGB 43 to 76, equal channels) with no warm cast. | The slate colour is neutral. | Add a slight warm or blue-grey bias to match the source slate (about RGB 64,71,77 to 106,103,98). |
| 8 | P2 | gables_pinnacles | Behind the SE pavilion, where two wing hip slopes meet near the court, there is a small dark vertical slot. It reads as a gap or crease between two roof volumes. | Two hip volumes overlap or leave a gap instead of sharing a valley. | Close the junction with a proper valley or ridge, or trim one volume to the other. |
| 9 | P2 | east_side, front_corner (vs sources/oblique.jpg, top.jpg) | The sources show small gabled dormers on the east wing roof on both sides of the tower, plus a chimney near the NE court corner. The render has plain roof planes and no chimney. | Wing dormers and the chimney were not modelled. | Add two small gabled dormers on each east wing slope and one stone chimney stack. |
| 10 | P2 | facade_close, glass_close, portal_arch | The stone is a smooth flat buff with fine horizontal joint lines. Rock-faced coursing and the rusticated basement are not expressed in the massing. This is acceptable for clay but flat. | Coursing is implied by line insets only. | Optionally, give the basement band deeper horizontal channel joints so it reads as rusticated. |
| 11 | P2 | top, east_side, aerial, rear | The top view is framed so tightly that the north, south and west streets fall outside the frame. The east_side view clips the spire and turret caps at the top edge. Trees are sparse: about 9 low-poly trees, almost all on the S and E sides. The source top shows a ring of street trees on all four sides. | The camera margins are too small, and only a limited set of trees was placed. | Add about 10% margin to the top camera, lower or widen east_side so the spire tip is in frame, and add street trees on the N and W sidewalks. |

## 3. Source conformance checklist

| item | status | view(s) used |
|---|---|---|
| Silhouette (corner pyramids, gabled fronts, tall copper-spired tower) | conforms | front, front_corner, right_side vs source front/oblique |
| Storey count (rusticated basement + paired-window floor + round-arched floor + arcade floor + gable attic) | conforms | facade_close, rear_north, east_side |
| Plan (square block round a square light court, tower mid-east, streets on four sides) | conforms | top, aerial vs source top |
| Court and pavilion projection (pavilions step forward on all faces; court with cross hips and terrace) | conforms | top (about 3 m step on every face), front_corner, roofs_court |
| Sandstone coursing | deviates (P2 #10: flat coursing lines, no rock-face or rustication) | facade_close, glass_close |
| Window tiers: basement | conforms on wings and N/S pavilion faces; deviates on E/W pavilion faces (end basement window missing, P0 #1) | facade_close, right_side, left_side |
| Window tiers: paired rectangular first floor | conforms on wings; deviates on E/W pavilion end bays (half-blind, P0 #1) | facade_close, east_side |
| Window tiers: tall round-arched second floor | conforms on wings; deviates on E/W pavilion end bays (filled with stone, P0 #1) | glass_close, east_side |
| Window tiers: third-floor arcades | conforms (runs of four lights on colonnettes with a shared sill; pavilion centre bays have three tall arches over tall lights with a spandrel panel); deviates on E/W pavilion end lights (blind, P0 #1) | facade_close, rear_north, east_side |
| String courses and eave cornice | conforms | facade_close, architecture_close |
| Gables and pinnacles (coped gables with shoulder blocks and pinnacles on the outward faces of corner pavilions and at mid-fronts) | conforms | architecture_close, gables_pinnacles, top |
| Roofs: wing hips | conforms | roofs_court, top |
| Roofs: pavilion pyramids | conforms (rise clearly above the wing hips) | front_corner, rear_north, roofs_court |
| Roofs: cross gables (mid-front N, S, W; court-side cross hips) | conforms; east wing dormers missing (P2 #9) | top, rear_north, left_side, roofs_court |
| Portal (SW pavilion) | conforms (projecting porch, arched passage, colonnettes, steps, landing, balustraded balcony); inner door finish P2 #4 | portal_arch, front_corner |
| Portal (tower base, per both sources) | deviates (P1 #2) | east_side vs source front/oblique |
| Clock tower: projection | conforms | top, right_side |
| Clock tower: lancets | deviates (P2 #5: too few, too short) | east_side, clock_tower |
| Clock tower: clocks | conforms (faces on the visible sides) | clock_tower, east_side, rear_side |
| Clock tower: belfry | conforms (reduced arch count, P2 #5) | clock_tower |
| Clock tower: turrets | conforms (corbelled polygonal turrets with copper caps) | clock_tower |
| Clock tower: spire | conforms in form; copper hue P2 #6 | clock_tower, right_side |
| Streets and trees | streets conform; trees deviate (P2 #11) | aerial, top, rear |
| Materials hierarchy (buff stone / dark slate / copper / dark glazing) | conforms, with hue notes P2 #6 and #7 | front_corner, clock_tower |

## 4. Camera validity

- No view has an invalid camera. In every view the target is legible and not hidden behind other objects.
- **top**: valid, but the framing is tight. The building fills the frame edge to edge, so the N, S and W streets are out of frame (P2 #11). The asset itself is not clipped.
- **east_side**: valid detail view. The spire and turret caps are clipped at the top edge (P2 #11). The spire is fully shown in clock_tower and right_side.
- **front, facade_close, portal_arch**: tree canopies overlap some second-floor windows and the porch balcony. The subject is still legible.
- **aerial, left_side, right_side, rear, rear_side**: the building occupies under half of the frame but is fully legible.
- **interior**: valid camera, but its subject shows the defect in P1 #3.

## 5. Previous-version (v001) findings: resolved in the pixels?

| v001 finding | status in v002 pixels | evidence |
|---|---|---|
| Roof one plain ring of hips (no mid-front gables N, S, W; no court-side cross hips; no light-court terrace; wing hips swallowing the corner pyramids) | Resolved | top and rear_north show coped mid-front gables on N, S and W. top and roofs_court show four court-side cross hips and a pale membrane terrace round the court. The corner pyramids rise well clear of the wing hips in front_corner and rear_north. |
| Corner pavilions almost flush | Resolved | top shows the pavilions stepping about 45 px (about 3 m) proud of the wing faces on every side. The step is visible in front_corner. (This step is the likely source of the new P0 #1.) |
| Slate pale cool grey | Resolved (residual P2 #7: neutral, not warm) | front_corner, roofs_court |
| Third-floor arcades built as separate pairs | Resolved | facade_close and glass_close show runs of four small arched lights on colonnettes with a shared sill. |
| Pavilions with generic punched windows | Resolved, but the E/W end bays are now blocked (P0 #1) | east_side and rear_north show three tall arches on colonnettes over tall lights with a spandrel panel in each centre bay. |
| SW portal shallow and flush, with no porch, colonnettes, steps or balcony | Resolved | portal_arch and front_corner show a projecting porch with a barrel passage, colonnettes, two steps, a landing and a balustraded balcony. |
| Rectangular door leaves under open arch heads showing the hollow interior | Largely resolved (residual P2 #4) | portal_arch shows a transom and a fanlight. The leaf fills to the transom, but the fanlight reads near-black and there is a slit at the right jamb. The tower door in east_side is clean. |
| Black void between the hood moulds of every paired window | Resolved | facade_close and glass_close show no voids between heads. |
| Gable rake copings stopping short of the cornice and shoulder blocks | Resolved | In architecture_close and gables_pinnacles, the rakes rise from inside taller shoulder blocks. |
| Smeared shading crease where the wing hips meet the corner pavilion | Resolved at the pavilion junction (residual small slot elsewhere, P2 #8) | gables_pinnacles, roofs_court |
