# Independent holistic review: clay-cmu-dock-warehouse v004 (RLASM v6.1 architectural clay)

Reviewer: independent; did not build the candidate. Evidence: `sources/front.png`, `sources/oblique.jpg`, `sources/top.jpg`, all 18 `renders/*.png` at full resolution, the four `boards/*.png`. I also made zoomed crops, written only to the new folder `/tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/wh-v004-indep-crops-7f3a/`. I used no metadata, counts, hashes or builder notes as proof.

## 1. Verdict

**VISUAL_REWORK_REQUIRED.** The v003 dock-shelter rhythm and front-camera findings are fixed. But the dock band was widened eastward without moving the entry group. The landing's west steps now sit in front of bay 4's east jamb, bumper and guide post, and the canopy butts against the bay 4 shelter. In the source, the bay group and the entry group are clearly separated.

Counts: P0 = 1, P1 = 2, P2 = 6

## 2. Findings

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P0 | top, front, front_corner, aerial, parapet_corner | **The landing and steps collide with bay 4.** In the near-orthographic top view, the bay 4 shelter covers about x 743–801 px. The steps at the landing's west end cover about x 780–800 px, so they are directly in front of bay 4's east jamb and the east edge of its door. In front, the landing's west face starts about 58 px inside the bay 4 shelter span. It hides bay 4's east bumper, and bay 4's east yellow guide post disappears behind the landing. In front_corner, the bay 4 east guide post rises from the top corner of the steps. In the source top, the steps start about 35 px (about a third of a shelter width, roughly 1.4 m) east of the last shelter, with clear wall between them. A truck cannot berth at bay 4 as built, so one of the four raised loading bays is not a working bay (program and contact defect). | The shelters were enlarged to 3.9 m and the band was moved to span about 11.5–68% of the south face. The source spans about 9.5–62% (top view). The landing (about 63–95%) and the steps were not moved, so the two groups now overlap by about 1.4 m. | Bring the dock band back to the source span: west jamb of shelter 1 at about 9.5% and east jamb of shelter 4 at about 62% of the south face. For example, use about 3.65 m shelters with 0.4 m gaps (about 2.85 m from the west corner on a face of about 30 m). Keep at least 1.2 m of clear CMU wall between the shelter 4 east jamb and the first stair riser. Keep the landing at about 66–91%. Re-render the top, front, front_corner and aerial views and confirm that bay 4 shows both bumpers and both guide posts standing free on the apron. |
| 2 | P1 | front, front_entry crop, parapet_corner, architecture_close | **The wall between the dock group and the entry is gone.** In front, the canopy's west edge touches the bay 4 shelter in elevation (x 808 vs 812). In parapet_corner, the canopy slab overlaps the shelter's east jamb in projection. Distance from the shelter to the entry door: about 8% of the face in the render vs about 15% in the source front; about 4% vs 10% in top. The source reads as two separate groups: bays, then wall, then the canopied entry. The render reads as one continuous strip. | Same root cause as #1: the bay band grew eastward while the canopy, door and landing stayed in place. | Fixed by the band correction in #1. Then check that the canopy's west edge is at least 1.5 m east of the shelter 4 east jamb, and that front shows clear beige CMU between them, as in the source front (about half a shelter width). |
| 3 | P1 | front_corner, phone-01 board | **The oblique comparison view shows the wrong corner.** The board pairs "Locked oblique" (elevated south-east corner, building filling about 80–95% of the frame, entry and landing large) with front_corner. front_corner is taken from the south-west, shows the west face that no source shows, and the building fills only about 37% of the frame. The aerial view does face the right corner, but at about 40% of frame width. As a result, no render matches the source oblique, and the landing, steps and canopy area, where #1 and #2 sit, is only legible in crops. | The front_corner camera is placed on the west side, at long range. | Move front_corner (or add a dedicated oblique camera) to the source's south-east, elevated viewpoint: about 35–40° down, looking north-west, with the building filling at least 75% of the frame width so the south face and east face both read. Put that view next to the locked oblique on phone-01. |
| 4 | P2 | glass_close, front, architecture_close | The wide entry window has 3 lights; the source front and oblique show 2 (a single central mullion). | Window module count. | Use 2 equal lights with one mullion. |
| 5 | P2 | glass_close, entry_canopy | The entry door and sidelight are two identical panels with no door hardware. The source shows a door with a handle and pull, next to a fixed sidelight. | Simplified storefront. | Add a pull and a door-stile distinction to the door leaf. |
| 6 | P2 | top, roof_units, aerial | The roof membrane seams run north–south in strips of about 75 px. The source oblique and top read as east–west laps plus one centre seam. Vent domes are drawn as flat white boxes; in the source they are low domed hatches. | Seam and dome primitives. | Turn the seam strips to run east–west; give the domes a rounded top. |
| 7 | P2 | front, facade_close | The yellow guide posts are free-standing bollards about 1.2 m in front of each jamb. In the source they are short yellow guides hugging the base of each shelter jamb. They read as guides, so this is polish only (apart from the bay 4 post in #1). | Post offset. | Move the posts to about 0.15 m off the jamb face. |
| 8 | P2 | front | A red car is cut off at the right edge of the frame (about x 1420, y 800). | Entourage placement. | Move or remove it from the front frame. |
| 9 | P2 | left_side, right_side, rear | The elevation cameras are long-range, so the building fills only about 28–40% of the frame width. The views are legible but CMU coursing does not read. | Elevation camera distance. | Tighten the elevation cameras to about 70% frame fill. |

## 3. Source conformance checklist

| Item | Status | View(s) used | Note |
|---|---|---|---|
| Silhouette | conforms | front, aerial, top | Single flat-roofed box; plan ratio 446 × 344 px = 1.30. |
| Height and proportions | conforms | front, left_side | Single storey. South-face height-to-length ratio is about 0.29 (source about 0.30). |
| CMU coursing | conforms | facade_close, glass_close, architecture_close, rear_north | 2:1 blocks in running bond with visible head joints; beige; carried round to the east and north faces. |
| Dock bays: doors | conforms | facade_close, dock_doors | Four overhead sectional doors, 5 panels, door height about 75% of the shelter (source about 68%). |
| Dock bays: lites | conforms | dock_doors | One row of 4 small lites per door. |
| Dock bays: surrounds | **deviates** | top, front, facade_close | Dark steel surrounds with head and jambs. Gaps are about 10% of a shelter width and shelters about 12.8% of the face, so the v003 finding is fixed. But the band runs to about 68% of the face against about 62% in the source (#1). |
| Dock bays: bumpers | **deviates** | front, front_bay4_landing crop | Black bumpers under the leveller lip on bays 1–3; bay 4's east bumper is hidden by the landing (#1). |
| Dock bays: guides | **deviates** | front_corner, front | Yellow posts at every bay; bay 4's east post stands at or on the step corner (#1). Offset noted as P2 (#7). |
| Dock bays: dock height | conforms | facade_close, front | Door sills at dock height above the apron on a grey concrete dock base. |
| Entry: door and sidelight | conforms (P2) | glass_close | Glazed aluminium pair; no hardware (#5). |
| Entry: canopy | **deviates** | front, parapet_corner, glass_close | Flat pale slab, wider than the door, overhanging further on the west. Its west edge now touches the bay 4 shelter (#2). |
| Entry: rods | conforms | entry_canopy, glass_close | Two dark rods from square wall plates to the slab's front edge; contact is visible at both ends. |
| Entry: window | conforms (P2) | glass_close, architecture_close | Wide aluminium window with a sill, east of the door; 3 lights instead of 2 (#4). |
| Landing and steps | **deviates** | top, front_corner, aerial | Cast-concrete landing at dock height with steps at its west end. Its east end correctly reaches the window's east end. The steps overlap bay 4's berth (#1). |
| East windows | conforms | right_side, architecture_close, east_windows, aerial | One low two-light window near the south corner and two small high clerestories; sills and reveals give visible depth. |
| Parapet and coping | conforms | parapet_corner, roof_units, rear_north | Flat parapet with a thin pale metal coping all round; beige inner parapet face. |
| Roof: membrane | conforms (P2) | top, roof_units | Grey membrane; seam direction differs (#6). |
| Roof: rooftop units | conforms | top, roof_units, aerial | Two RTUs left of centre, near mid-depth, matching source top positions (about 41% and 53% across). |
| Roof: vent domes | conforms (P2) | top | Four, set in from the corners as in the source top; drawn as boxes (#6). |
| Roof: pipe vents | conforms | roof_units, top | Several small pipe stacks present. |
| Apron and site | conforms | front, aerial, top | Street to the south, concrete apron in front of the bays, parking lane with stalls to the east, corner site. |
| Materials hierarchy | conforms | all | Beige CMU field, dark shelters, pale coping, canopy and landing, grey membrane, yellow guides; source palette kept. |
| North and west faces (not shown in any source) | coherent | rear, rear_north, left_side, rear_side | Same CMU and coping; small high windows; a man door on the north face with steps and handrails that touch the ground and wall correctly. |

## 4. Camera validity

- **front:** valid. The horizon sits about 73% down the frame (source about 73%), and the bay group spans about 30% of the frame width (source about 31%). It is at eye level and looks slightly up, matching the source.
- **front_corner:** legible, but it has the wrong role for the oblique comparison (#3, P1). It shows the south-west corner at about 37% frame fill, while the source oblique is the south-east corner at about 90% fill.
- **aerial:** the right corner (south-east) but distant (about 40% frame fill). The entry, landing and steps are only legible in a crop.
- **top:** valid. Close to nadir; the whole footprint and site are visible; it governs the plan.
- **left_side, right_side, rear:** valid but long-range (about 28–40% fill); coursing does not read (P2 #9).
- **rear_side:** valid.
- **Detail views:** all valid and unclipped: facade_close, architecture_close, glass_close, dock_doors, entry_canopy, roof_units, east_windows, parapet_corner, interior, rear_north. The target is visible in each, and openings show returns and reveals (dock doors recessed inside the shelters, the entry door's jamb return in entry_canopy, window sills and reveals on the east face).
- No view has its target occluded or the asset clipped.

## 5. Previous-version findings

| v003 finding | Resolved in pixels? | Evidence |
|---|---|---|
| P1: dock shelters too narrow and too far apart (gaps about 55% of a shelter width; shelters about 9% of the face) | **Resolved as stated, but the fix caused a new P0.** | facade_close: shelter 390 px, gap 40 px, so the gap is about 10% (source 7–18%). top: a shelter is about 57/446 px = 12.8% of the face (source about 13%). The overall band, however, now runs about 11.5–68% (source about 9.5–62%), which causes #1 and #2. The builder's claimed span of "about 12% to 68%" is confirmed in pixels; that span is itself the problem. |
| P1: front camera too close to the south-east corner and aimed down (horizon about 54%, bays 17% of frame width) | **Resolved.** | front: horizon at about 790/1080 = 73%; bays span x 373–808 = 30% of the frame width; eye level, looking slightly up. |

Earlier resolved findings, checked for regression:

| Earlier finding | Status | Evidence |
|---|---|---|
| Door height | holds | Door about 75% of the shelter height (dock_doors, facade_close). |
| Dock base | holds | Grey concrete dock wall under the shelters and the leveller lip (facade_close, dock_doors). |
| Coping | holds | Thin pale coping all round (parapet_corner, rear_north). |
| Head joints | holds | Running-bond head joints visible (glass_close, entry_canopy). |
| Entry position | **partly regressed** | The door and canopy are still at about 70–86% of the face (source 72–83%). However, the dock band now runs into the entry group, which removes the wall between them (#2). |
| Guide posts | holds, except bay 4 | Yellow posts at every bay; bay 4's east post now stands on or behind the steps (#1). |
| Rear door | holds | North-face man door with steps and handrails, touching the ground correctly (rear_north, rear). |
