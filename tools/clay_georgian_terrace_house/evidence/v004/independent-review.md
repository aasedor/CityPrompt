# Independent holistic review: georg v004 (RLASM v6.1 architectural clay)

Reviewer: independent, adversarial. Evidence: the three locked sources (`sources/front.png`, `sources/oblique.jpg`, `sources/top.jpg`), all 18 renders at full resolution, and the four phone boards. Zoomed crops were made only for inspection, in a new folder: `/tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/crops-indrev-f81eef79/`. I did not use metadata, counts or the builder's notes as evidence.

## 1. Verdict

**VISUAL_REWORK_REQUIRED**: the house itself matches the sources closely, but the new glazed lantern on the east rear extension is built wrongly. Its glazing bars are opaque white fins, and its two end frames stand clear of the hipped glass ends. From the oblique rear views it reads as an open white crate, not the dark long hipped lantern in the locked top view.

Counts: P0 = 0, P1 = 1, P2 = 8

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | rear_side, rear_north, rear, left_side, top | **East rear extension lantern is built wrongly and does not match the source.** In rear_north the lantern is a white upstand carrying eight vertical rectangular white fins. The hipped glass ends slope inward from the ridge, but a full-height vertical end frame stands clear of the glass at each end (left end around x 270–300, right end around x 725–735 at y 735–810). In rear_side the transverse fins read as solid opaque partitions and the glass is almost invisible, so the lantern looks like an open white egg-crate or rack sitting on the roof. In top the lantern is a white grid box of 8 cells covering about 80 % of the length and about 50 % of the width of the inner roof, with no hip diagonals. The locked top view shows a dark, long hipped glazed roof that fills nearly the whole area inside the stone rim, with clear hip lines at both ends. | The glazing bars are modelled as full-height gable-profile or rectangular fins, and the end trusses sit at the upstand ends instead of following the hip planes. The glass material is near-clear or white, so it does not read against the white bars. The lantern footprint is undersized. | Rebuild the lantern as one hipped glazed volume. Run the ridge along the long axis, slope both hip ends down to the upstand, and keep every glazing bar inside the glass planes as a thin rib that follows the slope (no vertical end frames proud of the hips). Use a darker, grey-tinted glass with some reflectance so the panes read as glazing. Enlarge the footprint to about 90 % of the area inside the rim, matching the top view. Re-render top, rear, rear_side, rear_north and left_side. |
| 2 | P2 | chimney_stacks, roof_lead, architecture_close, left_side | A black hairline gap (dark sliver, about 35 px long in chimney_stacks) where the rear parapet coping meets the east side parapet coping at the north-east corner. | The two coping solids are mitred or butted short, so the void shows through. | Extend one coping to overlap the other, or close the mitre. |
| 3 | P2 | mansard_dormers, architecture_close | A thin dark seam under each dormer sill where the sill meets the dormer cheek and the slate slope. | Small gap or z-offset between the sill and the cheek or slope. | Close the gap or extend the cheek down to the slope. |
| 4 | P2 | front_corner, aerial | Neighbour terrace: small white T-shaped window-head stubs poke through its roof slope above every top-floor window. | The neighbour's top-floor window frames are taller than the eave and intersect the roof plane. | Lower those window heads below the eave, or trim them at the roof plane. |
| 5 | P2 | rear, rear_side, top, left_side | The neighbour reads as a single detached hipped block with a blank windowless rear wall and a hipped west end. The sources show a continuing terrace with party-wall stacks. | Simplified context block. | Run the roof out to the frame edge (or add a second house), add a gable or party wall at the west, and put a few rear openings in. |
| 6 | P2 | top, rear, rear_side | No ground or context north of the rear range. The source top shows a lawn, paving, trees and buildings there, and a modern block east of the passage; the renders show grey void. | Site plane cropped at the rear. | Extend the ground plane and add simple garden, paving and tree massing behind the house. |
| 7 | P2 | top, roof_lead | The main-roof skylight is a wide, shallow upstand (about 2:1, long east–west). In the source top it is a near-square or north–south-elongated rooflight near the rear-west parapet. Its position is correct. | Wrong proportion. | Re-proportion it to roughly square or north–south-long. |
| 8 | P2 | front | The top frame edge clips the pot on the east chimney stack. | Camera framing is tight. | Tilt or raise the camera slightly, or widen the FOV a little. |
| 9 | P2 | left_side, right_side, rear | In left_side the neighbour roof fills the right half of the foreground, hiding the lower west wall and clipping a neighbour stack at the frame edge. In right_side and rear the house fills only about 15–20 % of the frame width. All three remain legible. | Camera distance and position. | Move the left_side camera higher or further west so it clears the neighbour roof. Dolly in on right_side and rear. |

## 3. Source conformance checklist

| Item | Status | View(s) used / note |
|---|---|---|
| Silhouette | conforms | front vs front; front_corner and aerial vs oblique. Three-storey block with parapet, mansard and side parapets rising with the mansard profile, chimney stacks above. |
| Storey count and bay rhythm | conforms | front, facade_close. Three storeys plus mansard, five bays, door in the centre bay, dormers aligned over the bays. |
| Brick and joints | conforms (clay) | facade_close, glass_close. Flat tan stock-brick tone (sampled about RGB 139,128,107 vs source about 141,117,90) with fine coursing lines. No texture expected in clay. |
| Sashes: sizes per floor, bars, sills, flat arches | conforms | facade_close, glass_close. Six-over-six on all three floors; first floor tallest; white stone sills; trapezoidal gauged flat arches. Reveals and returns are visible and there are interior rooms behind the glass. |
| Doorcase: pilasters, frieze, fanlight, door | conforms | doorcase_balconette, front. Stone pilasters with caps, frieze, cornice slab, rectangular three-light fanlight, black panelled door in a reveal, stone step. |
| French window and balconette | conforms | doorcase_balconette, facade_close, interior. The centre first-floor window runs down to the floor; the iron balconette with end stays sits on the doorcase cornice; it is visible from inside. |
| String course and plinth | conforms | facade_close, front (base crop), east_side. Stone string course at first-floor level, carried round the east wall; a brick plinth projects at the base. |
| Parapet and coping | conforms | facade_close, mansard_dormers. Short brick parapet with stone coping above the cornice band. |
| Mansard: pitch, slate, dormers | conforms | mansard_dormers, front_corner, roof_lead. Steep grey slate lower slope with a shallower upper slope; five lead-cheeked dormers with sills and glazing bars. Minor sill seams (P2 #3). |
| Lead flat and skylight | conforms (minor deviation) | roof_lead, top. Grey lead flat behind a roll line, with the skylight at the rear-west. Proportion is off (P2 #7). |
| Side parapets and chimney stacks with pots | conforms | front_corner, chimney_stacks, roof_lead, top. Coped side parapets follow the mansard profile. Two stacks on the west and one on the east at the source positions, each with a row of clay pots. NE coping gap is P2 #2. |
| Side wall windows | conforms | front_corner, east_side, right_side. One column of windows mid-depth on the east wall with flat arches and sills, matching the source front and oblique. No mansard-level side window, which is also correct. |
| Rear range (wing and extension) | deviates | top, rear_north, rear_side. The wing conforms. The extension lantern deviates (P1 #1). |
| Passage | conforms | front_corner, aerial, top, rear_side. Paved side passage on the east between the house and a boundary wall. |
| Garden walls and gate | conforms | front, front_corner, facade_close. Low wall with a pier and a recessed gate panel between the house and the west terrace; east boundary wall with a street pier. |
| Lamp | conforms | front, aerial, top. Black lamp standard on the pavement at the east corner. |
| Tree | conforms (clay) | front, front_corner, top. Plane tree on the pavement in front of the gap to the west; low-poly canopy. |
| Neighbour terrace | conforms in elevation, deviates in plan/rear (P2) | front, front_corner, rear. Lower, stuccoed white ground floor with brick upper floors and dormers. Detached-block reading and window-head intersections are P2 #4 and #5. |
| Materials hierarchy | conforms | All views. Brick field, white stone dressings (sills, string, coping, doorcase), grey slate and lead, black ironwork, door and pipe, terracotta pots. |
| North face (not shown by sources, judged for coherence) | coherent | rear, rear_north. Full-height brick rear wall to the parapet, two window columns, flat arches. Consistent with the flat-topped rear edge in the source top. |

## 4. Camera validity

- No view is invalid. In every view the target is present, unclipped where it matters, and legible.
- **front**: a single chimney pot is clipped at the top frame edge (P2 #8).
- **left_side**: the neighbour roof occupies much of the foreground and hides the lower west wall; the house's upper west wall, rear and rear range stay legible (P2 #9).
- **right_side, rear**: the asset is small in frame but legible (P2 #9).
- **architecture_close**: the top of the stack is cropped, which is acceptable for a detail view.
- **interior**: valid. It shows the first-floor room with the French window and two sashes, with real reveal depth.

## 5. Previous-version (v003) findings: are they resolved in the pixels?

1. **East rear extension: brick-coloured flat roof, no rooflight, reading as an open yard.** **Partly resolved.**
   - The roof is now grey lead inside a pale stone rim (top, rear_side, rear_north), so it no longer reads as a yard. That part is resolved.
   - A long lantern on a pale upstand with glazing bars is now present.
   - The lantern is still not resolved. Its form contradicts itself (vertical end frames standing outside the hipped glass, opaque fin bars, near-invisible glass). It reads as an open white crate from the oblique rear and lacks the hip-ended dark glazed form of the locked top view. This is carried forward as the new **P1 #1**.
2. **Hipped rear wing with overhanging eaves where the source encloses the roof in a coped parapet.** **Resolved.**
   - A coped brick parapet runs round the wing's north and side edges.
   - The hipped slate roof sits inside the parapet with no eave overhang visible (top, rear_north, rear_side, left_side), which matches the source top.
