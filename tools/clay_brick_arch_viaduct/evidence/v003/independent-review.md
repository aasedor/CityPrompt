# Independent holistic review: clay-brick-arch-viaduct v003 (RLASM v6.1 architectural clay)

Reviewer: independent; did not build the candidate. I judged only rendered pixels against the three locked sources (sources/front.png, sources/oblique.jpg, sources/top.jpg). I opened all 18 renders at full resolution and all four phone boards. I made zoomed crops only in the new folder `/tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/viad-v003-crops-512630062/`.

## 1. Verdict

**PASS_ZERO_P0_P1**: the arched run now continues to the horizon in every camera, and the street trees are back on the terrace-side pavement, so both v002 P1s are resolved in the pixels. No new P0 or P1 appears. What remains is context and finish polish. The city still visibly runs out in the south-looking aerials, and the run closes on a windowless block.

Counts: P0 = 0, P1 = 0, P2 = 19

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P2 | rear, rear_side (also a corner wedge in front_corner and aerial, top-left) | Behind the four south rows of gabled blocks, an empty flat grey plain runs to a ruler-straight horizon. In rear_side it is a full-width band about 10% of the frame high (y ≈ 92–200). In front_corner and aerial a grey wedge shows beyond the outer side rows. The builder's claim of "no scene end in any camera" is true for the run, the street and the ground edge, but not for the city: it visibly stops about 4 rows south and about ±100 m to the sides. | Context belts are finite: 4 rows south and 5 rows each side, on a bare 6 km ground plane. | Add more low-detail block rows south and at the outer sides until the grey plain leaves the rear, rear_side, front_corner and aerial frusta, or tint the far ground and add a distance haze so it reads as continuing roofscape. |
| 2 | P2 | cobbled_street, pier_pilasters, parapet_coping, front_corner (top edge) | At the vanishing point the viaduct, both pavements, the carriageway and the terrace all run straight into a single windowless 20 m brick wall (the "city belt"). In one-point street views it reads as a backdrop wall closing the set, and a twin-track railway ends in a blank wall with no portal. | The far cut is hidden by one plain straddling block. | Give the belt block a bridge or portal opening where the viaduct passes through, plus window rows and a roofline break. Alternatively, curve or step the far run slightly so the vista closes obliquely on varied blocks. |
| 3 | P2 | front, rear_north | The south vista along the street closes on windowless brick and render gable blocks beyond the cross street. The source front closes on a windowed terrace and a gridded modern block. | The south context blocks are plain massing. | Add window rows and doors to the street-facing faces of the two or three blocks on the street axis. |
| 4 | P2 | track_ballast, top, aerial | Ballast is pale, smooth and nearly white-grey with sparse chips; the source ballast is darker brown-grey and granular. (carried from v002) | Ballast material value is too light and the chip scatter too sparse. | Darken the ballast to the source grey-brown and densify the chip scatter on the shoulders. |
| 5 | P2 | aerial, front_corner (crop ae_near) | The near-end blind arch ring runs down to the ground with no stone impost at springing, unlike every long-face arch. (carried) | The end-wall arch is built without the impost module. | Add impost blocks at the springing of the end-wall blind arch. |
| 6 | P2 | facade_close, arch_shopfront, architecture_close | Arch rings and intrados are visibly faceted polygons at close range. (carried) | Low segment count on the ring sweep. | Raise ring and intrados segments (≥ 48 per semicircle) or add smooth shading. |
| 7 | P2 | architecture_close, front | The pier pilasters read as thin flat planks beside a slot, not stepped brick pilasters with returns as in the source front. (carried) | Pilaster built as one shallow slab offset from the pier face. | Model the pilaster as a 2-step brick projection with returns and its own cap. |
| 8 | P2 | architecture_close, pier_pilasters | Faint rectangular outline panels sit in the spandrels beside the arch rings. (carried) | Leftover spandrel panel or recess geometry. | Delete the stray spandrel panel edges or make them a deliberate recessed panel. |
| 9 | P2 | aerial, front_corner, right_side, top, rear_side | Terraces are very long single roof slabs with a chimney row. The sources show short gabled house units with party-wall parapets, chimney groups and roofs that step. (carried "barn-like terraces") | Terraces generated as continuous extrusions. | Break the terrace roofs into house-width units with party-wall upstands and paired chimney stacks. |
| 10 | P2 | top (right edge), aerial (right edge) | The rear wall of the street-side (east) terrace is blank brown. (carried) | No rear openings authored. | Add window and door rows or back extensions to the rear face. |
| 11 | P2 | facade_close, arch_shopfront | The dark fascia band runs behind the stone imposts, and its ends tuck into the imposts instead of stopping on the pier. (carried) | Fascia width equals the clear span plus overlap. | Trim the fascia to the clear opening, or return its ends against the pier faces. |
| 12 | P2 | front | The train shows only as a thin red-and-white line above the coping. The source front shows the carriage windows above the parapet. (carried) | Camera height and parapet height leave the train mostly hidden. | Raise the front camera slightly, or lower the parapet slightly, so the upper carriage band reads. |
| 13 | P2 | track_ballast, train_cars | The train is a plain box: a flat black cab window, no bogie or underframe detail, and an ends-only livery. (carried "train track and livery") | Simple massing. | Add bogie blocks, a cab windscreen split and the source's door bands. |
| 14 | P2 | front, cobbled_street | Distant setts dissolve into flat grey and fine shimmer. (carried) | Sett line texture under-sampled with distance. | Fade the sett lines with distance or raise the sample count. |
| 15 | P2 | glass_close, arch_shopfront | The door leaf sits proud of the glazing grid and butts the mullion without a frame or reveal. (carried "door framing") | The door is a separate plate placed over the grid. | Seat the door inside a framed bay with head and jamb members. |
| 16 | P2 | top, rear, left_side | A wide lawn strip lies between the viaduct's garden face and the garden walls. In the sources the back gardens and their trees run right up to the viaduct wall. (carried) | The terrace setback is too large on the garden side. | Extend the garden walls to the viaduct face and drop the open lawn strip. |
| 17 | P2 | right_side, left_side | A foreground terrace roof fills about 35–40% of right_side and about 20% of left_side. The target is fully legible, but the composition is weak. (carried) | Camera placed above or behind the terrace. | Raise or advance both side cameras so the viaduct fills more of the frame. |
| 18 | P2 | boards | The phone boards still omit the aerial render. (carried) | Board layout list. | Add aerial to phone-04 (the free slot). |
| 19 | P2 | front_corner, aerial, cobbled_street | The far pavement shows about 7 trees in the oblique frame against about 4 in the source. At street level the distant five read as a regular avenue line. Their placement is correct (terrace-side, kerbside, clear of the shopfronts and the terrace face). | Three extra continuation trees at 83, 104 and 141 m. | Optional: drop one continuation tree or widen the gap between the far trees. |

No P0 or P1 rows.

## 3. Source conformance checklist

| item | status | view(s) used | note |
|---|---|---|---|
| Plan and proportions | conforms | top vs top.jpg, aerial | Long straight viaduct, street and pavement on one side, terraces both sides, near end wall as in oblique. The garden-side setback is too wide (P2 #16). |
| Arch count and rhythm | conforms | front, aerial, right_side, front_corner | Even 8.2 m pitch of tall semicircular arches. The far run continues the rhythm as dark arch-headed recesses (crops fc_far, ae_far). |
| Piers and pilasters | conforms (finish deviates) | front, pier_pilasters, architecture_close | Massive piers with projecting pilasters and stone caps at the parapet. Pilasters are slot-like (P2 #7). |
| Imposts and arch rings | conforms | front, facade_close, left_side, pier_pilasters | A stone impost course with rings springing from it on both long faces. The rings are faceted (P2 #6), and the end-wall blind arch has no impost (P2 #5). |
| Shopfront infill (glazing, frames, signs) | conforms | facade_close, arch_shopfront, glass_close, front | Timber-gridded glazed fanlight, dark fascia band, glazed lower bays with a door and shelving depth behind. The near-end arch has a roller shutter, as in the oblique source. Fascia ends (#11) and door framing (#15) are P2. Signage text is not required. |
| Parapet and coping | conforms | parapet_coping, train_cars, front | Brick parapet with a stone coping, a deck string course and pier caps rising through the coping. |
| Track deck (ballast, rails, sleepers) | conforms (material deviates) | track_ballast, top, front_corner | Twin trapezoidal ballast beds with sleepers and rails, continuing on the far run. The ballast is too pale (P2 #4). |
| Train | conforms | aerial, front_corner, left_side, train_cars | A three-car red-and-white unit mid-run, with open track ahead of both cabs. Massing is simple (P2 #13). |
| Cobbled street and pavement | conforms | cobbled_street, front, rear_north | Staggered setts with gutter courses and kerbs. The arcade pavement has planters, cafe tables and bollards. Trees are on the far, terrace-side pavement in pits near the kerb. |
| Context terraces | deviates (P2) | aerial, front_corner, right_side, top, rear | Brick terraces with slate roofs and chimneys are present on both sides, but read as barn-like slabs (#9). The city stops at visible extents (#1, #2, #3). |
| Materials hierarchy | conforms | all whole-envelope views | Brick body, pale stone imposts, coping and caps, dark glazing with timber frames, dark fascia, slate-grey roofs, grey setts and paving. This matches the source palette in clay. |

## 4. Camera validity

- No view has an occluded target, a clipped asset or illegible content. All eight whole-envelope views show the viaduct clearly, and all ten detail views show their named subject.
- front_corner and top are on the street side and show the shopfront arcade, as required.
- left_side is clear of the terrace roof. The roof ridge occupies only the bottom band.
- Composition caveats (P2 #17, not invalidating): right_side has about 35–40% foreground roof; front shows the train only as a stripe (#12).
- No ground-plane edge appears in any frustum. The horizon is the ground meeting the sky at distance. The empty plain beyond the context (#1) is a content issue, not a camera clip.

## 5. Previous-version findings (v002) — resolved in pixels?

**v002 P1s (second and last targeted fix):**

1. **The run ended in frame**: RESOLVED.
   - In front_corner and aerial, the viaduct, both tracks, parapets, pavements, street and terraces now run to the top edge of the frame (crops fc_far, ae_far, fc_topstrip). The far run carries the arch recesses at the same pitch.
   - In cobbled_street, the street no longer ends at a ground edge against the sky. It runs to a distant building.
   - Residual context issues are logged as P2: the grey plain beyond the south and side context (#1) and the windowless straddling block that closes the vista (#2).
2. **The street trees were on the wrong side**: RESOLVED.
   - In front_corner, aerial, top, rear, rear_side, rear_north, cobbled_street and front, all street trees stand on the far, terrace-side pavement at the kerb. They are irregularly spaced, have smaller crowns and stand clear of the terrace face.
   - The arcade pavement carries only planters, cafe tables and bollards, and no shopfront bay is screened.
   - Minor count and avenue reading: P2 #19.

**v002 P2s:**

| v002 P2 | status in v003 pixels |
|---|---|
| Visible ground-plane edge | Resolved: no ground edge in any view. |
| Empty grey plane beyond the terraces | Partly resolved: the plane between the near rows is now filled with block rows, but an empty grey plain is still visible beyond the outer rows (#1). |
| Pale smooth ballast | Open (#4). |
| No impost on near-end blind arch | Open (#5). |
| Faceted arch rings | Open (#6). |
| Slot-like pilaster strips | Open (#7). |
| Stray spandrel outline | Open (#8). |
| Barn-like terraces | Open (#9). |
| Blank east-terrace rear wall | Open (#10). |
| Fascia ends behind the imposts | Open (#11). |
| Thin train stripe in front | Open (#12). |
| Train track and livery | Open (#13). |
| Distant sett aliasing | Open (#14). |
| Door framing | Open (#15). |
| Lawn strip on the garden side | Open (#16). |
| right_side and rear_north composition | right_side open (#17); rear_north is now acceptable (street, arcade and train legible, closing on buildings). |
| Phone boards omitting aerial | Open (#18). |

**Fixes that must still hold (v001 and v002):**
- Staggered setts with gutter courses: hold (cobbled_street, front).
- Trapezoidal ballast beds with sleepers and rails: hold (track_ballast).
- Stone impost course with rings springing from it on both long faces: holds (front, left_side, pier_pilasters).
- Train mid-run with open track ahead of both cabs: holds (aerial, front_corner, rear).
- front_corner and top on the street side, showing the arcade: hold.
- phone-01 pairing the locked top with the render top: holds.
- left_side clear of the terrace roof: holds.
