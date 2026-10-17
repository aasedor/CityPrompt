# Independent holistic review: clay-cmu-dock-warehouse v002 (RLASM v6.1 architectural clay)

Reviewer: independent; did not build this candidate. Judged only rendered pixels against the locked sources (`sources/front.png`, `sources/oblique.jpg`, `sources/top.jpg`). All 18 renders and the 4 phone boards were opened at full resolution. Zoomed crops (read-only derivatives) are in `/tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/indep-review-wh-v002-crops/`.

## 1. Verdict

**VISUAL_REWORK_REQUIRED.** Most v001 defects are fixed, but the dock doors and shelters are still too tall for the wall. The front camera does not reproduce the source's south-east three-quarter view. The source's cast-concrete dock base is missing. These leave three P1 blockers.

Counts: P0 = 0, P1 = 3, P2 = 7

## 2. Findings

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | facade_close, front, front_corner, aerial, dock_doors | Docks dominate a wall that reads low. Measured grade-to-coping in near-elevation (facade_close): shelter heads sit at about 67–68 % of wall height and door heads at about 60 %. Only about 14 CMU courses rise above the shelter heads, against about 25 courses spanned by a shelter. In the sources (front crop and oblique crop), shelter heads sit at about 55 % and door heads at about 43 %, with about 20 courses above a shelter and about 15 within it. Door aspect also overshoots: render door h:w ≈ 2.1 against about 1.75 in the source front. | The v001 fix grew the doors to 4.0 m tall and enlarged the shelters around them. The 8.4 m eave was not raised to keep the wall-to-dock ratio. | Preferred: lower the door head about 1.3 m (door about 2.7 m tall above the dock sill) and the shelter head to about 55 % of grade-to-coping (about 4.7 m above the apron). Narrow the door and shelter so the door keeps h:w ≈ 1.7–1.8. Alternative: keep 2.3 × 4.0 m doors and raise the eave and parapet to about 10.5–11 m. Accept when the shelter head sits at 53–57 % of wall height in facade_close and front. |
| 2 | P1 | front (board phone-01) | The render front is almost elevational. The east face is a sliver about 25 px wide at the right edge, so its low window and two clerestories are illegible. The building fills only the upper-middle band, about 67 % of frame width, and roughly the lower 40 % of the frame is empty apron and road. The source front is a low eye-level south-east three-quarter view. In it, the east face takes about 20 % of the frame with all three windows legible, and the building fills about 70 % of the width at a larger scale. | The v001 mirror was fixed by moving the camera to the east side, but the azimuth stayed nearly square to the south face, with too much distance and too low a target. | Rotate the front camera about 25–30° from due south toward the east. Bring it closer and lower (eye height about 1.6–2 m, across the street). Aim at about mid-wall height so the south face spans about 65–70 % of the width, the east face about 20 % with all three windows legible, and the road crosses the lower quarter as in the source. |
| 3 | P1 | facade_close, dock_doors, front, glass_close | CMU coursing runs straight down to the apron under every dock door and along the whole south face. No cast-concrete dock wall or foundation band appears. Under each door there are only two black bumper blocks, with no leveler lip or plate. All three sources show a grey cast-concrete base about 0.8–1.0 m high along the south face: it is the dock face under the shelters, the base under the landing, and the grey band in the top view. Bumpers and a steel leveler lip sit on it. | The base or plinth assembly is omitted, and the CMU material is applied to grade. | Add a cast-concrete base band (source concrete grey, about 0.9–1.0 m, flush or 20–30 mm proud) along the south face, wrapping both south corners. Add a dark steel leveler lip or plate under each door between the bumpers. Start the CMU above the band. |
| 4 | P2 | facade_close, dock_doors, front | The yellow guides are thick freestanding bollards on the apron, set beside the jambs. The source shows slim yellow guides fixed to the foot of each shelter jamb. Bay gaps are about 0.37 of a shelter width, against about 0.15 in the source, where the shelters nearly touch. | Guide modelled as a pipe bollard; bay pitch kept from v001. | Mount slim guides on the jamb pad feet and tighten the bay gaps toward the source rhythm. |
| 5 | P2 | glass_close, entry_canopy | The entry is two equal glass panes with no handle or push hardware and no transom. The source shows a swing leaf with a handle plus a sidelight. Frames are silver-white, while the source office window frame is dark grey. The office window has 3 lights; the source has 2. | Generic glazing module. | Make it one leaf with a pull handle plus a sidelight, a 2-light office window and darker frames. |
| 6 | P2 | glass_close | The office window glass renders as an opaque frosted grey, while the door glass shows the interior racking. Front and architecture_close show racking through the same window. | View-dependent glass shader or reflection at a frontal angle. | Use the same transmissive glass material for both. |
| 7 | P2 | top | Pipe vents cast tri-radial "asterisk" shadows on the membrane. | Several hard lights in the top rig. | Use a single sun or a softer light for the top view. |
| 8 | P2 | left_side, right_side, rear, rear_side, aerial, front_corner (boards 01/03/04) | The building fills only about 25–35 % of frame width. Openings are barely legible at phone-board scale, though the massing is legible. | Cameras placed for the site extent, not the building. | Tighten framing to about 60–70 % of width. |
| 9 | P2 | front_corner | The camera is south-west (it shows the unseen west face), while the source oblique is south-east. The aerial carries the matched south-east role. | Role assignment. | Optional: move front_corner to the south-east, or keep it as a supplementary view. |
| 10 | P2 | east_windows, aerial | Car massing has a roof slab overhanging a translucent band, so the slab reads as floating. | Simplified car proxy. | Tuck the roof onto the cabin. |

P2 rows: 4–10 (7 in total). P1 rows: 1–3. No P0.

## 3. Source conformance checklist

| Item | Status | View(s) used | Notes |
|---|---|---|---|
| Silhouette | conforms | top, aerial, front_corner | A single flat-roof rectangular box with no extra volumes. |
| Height and proportions | **deviates** | facade_close, front, top | Plan ≈ 1.36:1 including coping in top, against the source's ≈ 1.3, which conforms. One storey. Wall height against the dock elements is wrong (finding 1). |
| CMU coursing | conforms | facade_close, glass_close, entry_canopy, rear_north, architecture_close | Running bond with head joints, painted beige. Course height is consistent with about 43 courses to coping. |
| Dock bays: doors | deviates | facade_close, dock_doors | Four overhead sectional doors with panel joints, but too tall for the wall (finding 1). |
| Dock bays: lites | conforms | facade_close, dock_doors | A row of 4 small lites in one panel. |
| Dock bays: surrounds | deviates | facade_close, front | Dark steel or padded surrounds with a head and jambs and real projection, but too tall (finding 1) and more widely spaced than the source (finding 4). |
| Dock bays: bumpers | conforms | dock_doors | Black bumpers under each sill. The leveler lip is missing (finding 3). |
| Dock bays: guides | conforms (P2) | facade_close | Short yellow posts at the jamb feet, but bollard-like (finding 4). |
| Dock bays: dock height | deviates | facade_close, dock_doors | The sill is raised about 1 m above the apron, which is correct. The cast-concrete dock face is missing (finding 3). |
| Entry door and sidelight | conforms (P2) | glass_close, front | Glazed aluminium entry in a recessed frame with a reveal; the hardware is wrong (finding 5). |
| Canopy | conforms | entry_canopy, glass_close, parapet_corner | A flat pale slab hung from two dark rods to wall anchor plates. It touches the wall, nothing floats, and it spans the door. |
| Rods | conforms | entry_canopy | Both rods connect, with anchor plates. |
| Office window | conforms (P2) | glass_close, front | A wide window beside the door with a projecting sill. 3 lights against 2 (finding 5). |
| Landing and steps | conforms | front, glass_close, architecture_close, top | A long cast-concrete landing at sill height, with steps at the west end. It ends at the office window's east jamb, as in the source. |
| East windows | conforms | right_side, architecture_close, east_windows, parapet_corner | One low 2-light window near the south-east corner and two high portrait clerestories, all with reveals and sills. Not legible in front (finding 2). |
| Parapet and coping | conforms | parapet_corner, roof_units, front, architecture_close | A low parapet with a beige inner face and a continuous thin pale coping ring. The corner is clean. |
| Roof: membrane | conforms | top, roof_units | Grey membrane with sheet seams. |
| Roof: units | conforms | top, roof_units, aerial | Two rooftop units placed close together, left of centre, as in the source top. |
| Roof: domes | conforms | top | Four small vent units near the corners, matching the source top layout. They render as boxes, not domes, which is acceptable in clay. |
| Roof: vents | conforms | roof_units, top | Several small pipe vents; shadow artifact (finding 7). |
| Apron and site | conforms | top, aerial, front | Street to the south, a concrete apron or sidewalk in front of the docks, a parking lane with stalls to the east, and asphalt to the west. |
| Materials hierarchy | **deviates** | facade_close, front | Beige CMU, dark surrounds, white doors, pale coping and grey concrete landing are all present. The concrete base or dock band layer is missing (finding 3). |
| North and west faces (no source) | coherent | rear, rear_north, left_side, top | Sparse high windows. North man door: a solid dark leaf with a lever, on a stoop with steps and two handrails. Consistent grammar. |

## 4. Camera validity

- No view has the target occluded or the asset clipped. architecture_close is now clear of trees.
- **front** (P1, finding 2): legible but not a matched role. It is a near-elevation instead of the source's south-east three-quarter view, the east face is illegible, and the foreground is oversized.
- **front_corner** (P2, finding 9): a south-west viewpoint, not the oblique's south-east one. aerial provides the south-east match and is valid.
- **left_side, right_side, rear, rear_side, aerial, front_corner** (P2, finding 8): the building is small in frame. Massing is legible, but openings are marginal on phone boards.
- **top**: valid and orthographic over the full plan.
- **Detail views**: all valid and legible. These are facade_close, architecture_close, glass_close, dock_doors, entry_canopy, roof_units, east_windows, parapet_corner, interior and rear_north.
- **interior**: a valid racking aisle that is coherent with the clay palette.

## 5. Previous-version (v001) findings: resolved in pixels?

| v001 finding | Builder claim | Resolved? | Pixel evidence |
|---|---|---|---|
| Dock doors and shelters square and about twice too wide | 2.3 × 4.0 m doors in taller shelters | **Resolved (overshoot)** | The doors now read tall and narrow (h:w ≈ 2.1 against the source ≈ 1.75). The added height feeds finding 1. |
| Block too long and low; shelters fill too much wall height | 30 × 23 m block, 8.4 m eave | **Not resolved** | The plan ratio is fixed (≈ 1.36:1 in top). Shelter heads still sit at about 67–68 % of wall height against about 55 % in the source, and door heads at about 60 % against about 43 % (finding 1). |
| Entry group and landing shifted west; too much blank south-east wall; landing past the window | Entry moved south-east; landing ends at the office window | **Resolved** | Door at about 66 % along the facade (source 62 %), window at 78–92 % (source 78–93 %), blank south-east wall about 8 % (source 7 %). The landing ends at the window's east jamb (front, architecture_close). |
| CMU bed joints only, reading as lap siding | Running-bond head joints | **Resolved** | Staggered head joints appear in facade_close, glass_close, entry_canopy and rear_north. |
| Coping broken at the south-east corner with black specks | One continuous lapped coping ring | **Resolved** | parapet_corner and architecture_close show a continuous clean corner with no specks. |
| Yellow guides as full-height stripes | Short yellow guide posts | **Resolved** (P2 residual) | Short posts about 1.1 m tall at the jamb feet (facade_close, dock_doors). They are bollard-like (finding 4). |
| Front camera mirrored (south-west) | South-east front camera | **Partially resolved** | The east face is now on the right, so the side is correct. The view is nearly elevational and the east face is illegible: new P1 (finding 2). |
| Tree crown hiding architecture_close | Tree moved north-east | **Resolved** | architecture_close is unobstructed. Trees stand at the south-west corner and in the north-east parking area (top). |
| North man door reads as a window on an unreachable stoop | Solid steel leaf with steps and handrails | **Resolved** | rear_north shows a dark solid leaf with a lever, its sill at stoop level, with four risers and two handrails. |
