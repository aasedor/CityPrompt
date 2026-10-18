# Independent holistic review: clay-cmu-dock-warehouse v005 (RLASM v6.1)

Reviewer: independent; did not build this candidate. I judged only the rendered pixels against the locked source pixels (sources/front.png, sources/oblique.jpg, sources/top.jpg). I opened all 18 renders at full resolution, plus the 4 phone boards. I took measurements from the pixels and from zoomed crops in `scratchpad/wh-v005-indep-crops-q7/`.

## 1. Verdict

**VISUAL_REWORK_REQUIRED.** All three v004 findings are fixed and nothing earlier has regressed. One P1 is still open: the east face has one fewer high window than the locked oblique shows.

Counts: P0 = 0, P1 = 1, P2 = 13

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | front_corner, aerial, right_side, rear_side, parapet_corner vs locked oblique | **Source:** the locked oblique's east face has one low window near the SE corner and **three** high punched windows spaced along the whole face. In screen space they sit at about 47%, 70% and 87% of the visible face; the last is close to the NE corner. The front source shows the first two, and its frame cuts off the third. **Render:** one low window plus only **two** high windows, at about 31% and 57% of the face (right_side elevation). The northern ~40% of the east face is blank wall in every view, so the east-face rhythm visibly differs in the matched oblique role. | The window schedule was taken from the front source (which shows only two high windows) or from the brief's summary, not from the oblique. | Add a third high window on the east face. Use the same size, sill height and returns as the other two, centred at about 80–85% of the face length from the south corner. Re-space the three at roughly even intervals (about 33% / 58% / 83%). Re-render front_corner, right_side, east_windows and rear_side. |
| 2 | P2 | front | Building fills about 78% of the frame width and about 40% of its height, against about 92% / 57% in the locked front. About 38% of the frame is empty sky. Same role and side, with the corner at about 84% vs 80%. | Camera is slightly farther and higher-framed than the source. | Dolly in about 15% and drop the target so the parapet sits near 25% of frame height. |
| 3 | P2 | front_corner, aerial | front_corner fill is about 74% of the width (source oblique about 90%). | Camera distance. | Dolly in about 15%. Optional. |
| 4 | P2 | facade_close, dock_doors, front | Each overhead door shows a row of **4** lites; the locked front and oblique show **2** small lites per door. | Generic door component. | Reduce to 2 lites centred in the third section. |
| 5 | P2 | facade_close, top | Gaps between shelters are about 0.2 m (about 5% of shelter width). The source front and top show slightly wider wall strips between surrounds (about 10–15% of surround width). | Shelter spacing tuned to keep the dock band at 62%. | Optional: narrow the shelters slightly and widen the gaps to about 0.4 m, keeping the 11.5–62% span. |
| 6 | P2 | facade_close, dock_doors | Guide posts are free-standing square bollards rising from the apron to dock level in front of each jamb. In the source they are slim yellow guides mounted against the lower jamb, beside the door bottom. | Bollard primitive used for guides. | Optional: make them thinner and attach them to the jamb face at dock level. |
| 7 | P2 | glass_close, entry_canopy | Entry reads as two equal glazed leaves with no transom or hardware. The source shows a single door (with pull) plus a sidelight, under a transom bar. | Simplified storefront. | Add a transom mullion and a door pull, and make the leaf/sidelight split read. |
| 8 | P2 | glass_close, architecture_close, front | The wide window beside the entry has **3** lites; the source shows **2**. | Mullion count. | Use one central mullion. |
| 9 | P2 | roof_units, top, parapet_corner, front_corner | The four "vent domes" are rendered as low rectangular boxes. The source shows small rounded translucent domes. Their positions near the four roof corners are correct. | Box primitive. | Swap for low domes or rounded curbs. |
| 10 | P2 | top, front_corner | Membrane seam lines run N–S. The source top and oblique show seams running mostly E–W, with one central N–S lap. | Seam orientation. | Rotate the seam pattern 90°. |
| 11 | P2 | all exterior views | CMU paint reads as a pale greige/putty. The mean wall colour is about (157,152,140), R−B about 17. Sunlit source wall is about (214,188,151) to (240,203,152), R−B about 60–90. It still reads beige, but cooler and less saturated than the source palette. | Neutral grey lighting combined with a desaturated albedo. | Warm the wall base colour slightly, for example toward (205,185,150) albedo. |
| 12 | P2 | east_windows, front_corner | High east windows are single-pane. The source oblique shows 2×2 divided lites. | Window component. | Add a cross muntin, as on the north-face window. |
| 13 | P2 | front, architecture_close, front_corner | The landing is a plain box. The source landing has a projecting cast cap/nosing along its top edge. Similarly, the source canopy has a louvered/slatted top seen from above, where the render has a plain slab (acceptable per the brief's "flat concrete canopy"). | Simplified masses. | Optional: add a 50–75 mm cap overhang to the landing. |
| 14 | P2 | left_side, right_side, rear, rear_side, aerial | Orthographic-style side and rear views put the building at only 28–41% of the frame width and about 11–16% of its height. They are legible, but most of each frame is empty ground and sky. | Context camera distance. | Tighten these cameras if the views are used for review boards. |

## 3. Source conformance checklist

| Item | Status | View(s) used | Notes |
|---|---|---|---|
| Silhouette | conforms | front, front_corner, aerial, top | Single flat-roofed rectangular box with a parapet. No setbacks or extra masses. |
| Height and proportions | conforms | top, front, right_side | Plan is 450 × 344 px in the top view, a ratio of about 1.31 (target about 1.3). Single storey. The south-face length-to-height ratio in the front view is about 3.3, the same as the source front (3.3). |
| CMU coursing | conforms | facade_close, glass_close, entry_canopy, architecture_close, rear_north | Running bond with both bed and head joints visible on all four faces. Colour is slightly desaturated (P2 #11). |
| Dock bays: doors | conforms (P2 lites) | facade_close, dock_doors, front | Four white sectional doors with horizontal sections, recessed inside the shelters, with visible returns. Lites are 4 against 2 in the source (P2 #4). |
| Dock bays: surrounds | conforms | facade_close, dock_doors, front, front_corner | Dark steel/foam surrounds with a heavy head and jambs, at a jamb-to-door ratio comparable to the source. Rhythm is four equal bays. |
| Dock bays: bumpers | conforms | facade_close, dock_doors | Two black bumpers under each leveler lip. |
| Dock bays: guides | conforms (P2 form) | facade_close, dock_doors, front | Eight yellow posts, one at each jamb. Free-standing rather than jamb-mounted (P2 #6). |
| Dock bays: dock height | conforms | front, facade_close | Door sills sit about 11% of the wall height above the apron, matching the source front. Concrete dock base is present. |
| Dock band extent | conforms | top (crop), front | Shelters span about 11.5% to 62% of the south face in the top render; the source top shows about 9% to 62%. |
| Entry: door and sidelight | conforms (P2 detail) | glass_close, front, architecture_close | Glazed aluminium pair at landing height. Transom and hardware are missing (P2 #7). |
| Entry: canopy | conforms | entry_canopy, glass_close, front, front_corner | Flat pale slab, asymmetric over the door (longer to the west, as in the source), set just above the door head. In plan it spans about 74–87% of the face, against 72–84% in the source top. |
| Entry: rods | conforms | entry_canopy, glass_close | Two dark rods run from square wall anchors to the canopy's front edge. There are no gaps or intersections. |
| Entry: window | conforms (P2 lites) | glass_close, front | Wide window immediately east of the canopy. Its head is above the door head and it has a projecting sill. Height ratio to the door is 0.76, matching the source's 0.76. It has 3 lites against 2 (P2 #8). |
| Landing and steps | conforms | front, front_corner (crop), top (crop), architecture_close | A long cast block at door-sill height running from about 66% of the face to just short of the SE corner, with steps at its west end. The steps sit at about 66–70% of the face, clear of bay 4 (the shelters end at 62%). This matches the source top (steps 66–70%). |
| East windows | **deviates (P1 #1)** | front_corner, right_side, east_windows, rear_side vs oblique | The low window near the south corner is correct. Two high windows are present where the locked oblique shows three. |
| Parapet and coping | conforms | parapet_corner, roof_units, facade_close, rear_north | Flat parapet with a beige inner face and a thin pale coping on all four sides. |
| Roof: membrane | conforms (P2 seams) | top, roof_units, front_corner | Grey membrane. Seam direction is rotated (P2 #10). |
| Roof: units | conforms | top, roof_units, front_corner | Two RTUs with dark fan tops, side by side slightly north of centre (about 38% and 54% across), as in the source (41% and 53%). |
| Roof: domes | conforms in layout (P2 form) | top, roof_units | Four, one near each roof corner. They are boxes, not domes (P2 #9). |
| Roof: vents | conforms | roof_units, top, parapet_corner | Several small pipe vents. |
| Apron and site | conforms | front, front_corner, aerial, top | Street to the south and a concrete apron along the south face. Parking lane with striped stalls to the east. The tree and car massing is simple and acceptable for clay. |
| North and west faces (no source) | coherent | rear, rear_north, left_side, rear_side | CMU with a few high punched windows. The north face has a hollow-metal service door with a stoop, steps and rails; the stoop meets the wall and there is no floating. |
| Materials hierarchy | conforms (P2 tone) | all | Beige CMU field, dark shelters, white doors, pale coping, grey membrane, light concrete landing and apron, dark rods. The hierarchy reads correctly. The CMU is cooler and paler than the source (P2 #11). |

## 4. Camera validity

- **front**: valid. Same role as the source: a street-level south view with the bays to the west, the entry to the east and the east face receding at right. Framing is farther than the source (P2 #2), but no target is occluded or clipped and all elements are legible.
- **front_corner**: valid and now correct. The camera is elevated, at the south-east, with the SE corner nearest the camera, both the south and east faces and the roof visible, and the building filling about 74% of the width. This matches the locked oblique's role (P2 #3 for fill).
- **aerial, top**: valid. The top view is close to nadir and shows the full plan, roof equipment and both street sides.
- **left_side, right_side, rear, rear_side**: valid but small (P2 #14). The building is fully in frame and its openings are legible.
- **Details** (facade_close, architecture_close, glass_close, dock_doors, entry_canopy, roof_units, east_windows, parapet_corner, interior, rear_north): all valid. Targets are unoccluded and in frame. Opening depth and returns are visible at the doors, windows and shelters. Contact is clean at the canopy anchors, landing, steps, bumpers, guides and stoop. roof_units shows a sliver of a dome box at the bottom-left frame edge, which is harmless.
- No view is invalid.

## 5. Previous-version findings (v004) and regression check

| v004 finding | Resolved in the pixels? | Evidence |
|---|---|---|
| P0: landing steps stood in front of bay 4's east jamb and guide post, blocking the bay (dock band to 68% against about 62%) | **Resolved** | In the top-render crop, the shelters end at 62% of the south face and the steps occupy about 66–70%. That leaves about 3.9% of the face (≈1.2 m at the implied ≈30 m face) of clear wall between the last shelter and the steps. In the front_corner crop, the stair foot lands on the apron east of bay 4's guide post without overlapping it. The front view shows bay 4's east post and jamb fully clear. |
| P1: no wall between the bays and the entry; canopy touching the bay 4 shelter (gap about 8% vs about 15%) | **Resolved** | The front view shows a clear CMU strip between bay 4's shelter (ends at x≈750) and the canopy (starts at x≈838). The shelter-to-door distance is about 17% of the face in the front view and about 16% in plan, against about 15% in the source. The canopy does not touch the shelter in front, front_corner or parapet_corner. |
| P1: front_corner from the south-west at about 37% fill (locked oblique is the SE corner at about 90%) | **Resolved** | Now an elevated SE-corner view at about 74% fill. The residual fill difference is P2 only. |
| Builder claim: 3.65 m shelters 0.2 m apart spanning about 11.5–62% | Confirmed | Top crop: 11.5% to 62%. Thin, even gaps. |
| Builder claim: about 1.25 m of clear wall between the last shelter and the landing steps; about 15% of the face between the shelters and the door | Confirmed (≈1.2 m; ≈16%) | See above. |
| Builder claim: close, elevated SE front_corner | Confirmed | See camera validity. |

Earlier resolved findings, checked for regression:

- Shelter rhythm: not regressed. Four equal, evenly spaced shelters.
- Front camera: not regressed. Correct role and side; framing is slightly farther (P2).
- Door height: not regressed. The entry door is about 12 courses (≈2.4 m) and its sill sits at landing and dock height.
- Dock base: not regressed. A concrete dock base runs under the bays.
- Coping: not regressed. A thin pale coping runs continuously on all sides.
- Head joints: not regressed. Running bond with head joints on every face.
- Guide posts: not regressed. Eight yellow posts at the jambs (form is P2).
- Rear door: not regressed. The north service door has a stoop, steps and rails, with clean contact.

Note on the brief: the brief describes "two high clerestories" on the east face. The locked oblique shows three, and per the method the locked pixels govern. This drives P1 #1.
