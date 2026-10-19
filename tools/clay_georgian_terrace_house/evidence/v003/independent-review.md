# Independent holistic review: georg v003 (RLASM v6.1 architectural clay)

Reviewer: independent; this reviewer did not build the candidate. Evidence: the three locked sources (front.png, oblique.jpg, top.jpg), all 18 renders opened at full resolution, the four phone boards, and zoomed crops made only in a new folder, `scratchpad/georg-v003-indrev-crops-a9af577d/`. Builder notes, metadata and counts were not used as proof.

## 1. Verdict

**VISUAL_REWORK_REQUIRED**: the main block, the facade grammar and the rebuilt dormers now match the sources, but the rear range does not match the locked top view, so one P1 remains.

Counts: P0 = 0, P1 = 1, P2 = 14

## 2. Findings

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | top, rear_side, rear, rear_north, left_side vs locked top | The rear range does not match the governing top source. (a) The single-storey east rear extension has a flat top the same tan as the brick walls, with no rooflight. In the top render it reads as an open walled yard. The locked top shows a grey lead/slate roof inside a stone-coped rim, with a long hipped glazed lantern running east–west. (b) The hipped rear wing has a slate roof with overhanging eaves on a bare box. The locked top shows the hips sitting inside a stone-coped parapet rim like the main block's. | The extension roof slab was given the brick material, and the lantern and the wing parapet were never modelled. The rear range was not re-checked against the top source after the plan refit. | Give the extension roof the roof/lead palette and add a long low hipped lantern (glazing bars, lead/grey frame) inside a stone-coped upstand. Replace the wing's eaves overhang with a short brick parapet and stone coping that enclose the hipped roof. Re-render top, rear_side and rear_north and compare them with the locked top. |
| 2 | P2 | mansard_dormers, chimney_stacks, front_corner | Each dormer sash shows a small black pinhole where its glazing bars cross (upper and lower sash), and a hairline dark slit runs under each dormer sill where it meets the slate apron. | The bar meshes do not overlap at the crossings, and there is a sliver gap between the sill and the apron. | Overlap the bars at each crossing by about 1 mm. Seat the sill on the apron or extend the apron under it. |
| 3 | P2 | mansard_dormers, front vs oblique/front sources | The dormer sashes have 2 panes across (four-over-four, narrow portrait). The source dormers show 3 panes across with a wider portrait opening. | The muntin count/width parameter was reused from the side windows. | Use 3 columns per sash and widen the dormer light by about 25%, keeping it portrait. |
| 4 | P2 | front_corner, aerial, roof_lead, mansard_dormers vs oblique, top | Behind the mansard, the upper roof is a uniform light-grey flat. In the oblique and top sources, a large shallow slate slope in the same dark slate tone as the mansard rises to the lead flat at the rear. | The upper slope was simplified into the lead flat. | Tint the front half of the upper roof (from the mansard break to the roll) in the mansard slate tone, with a slight pitch, and keep only the rear strip with the skylight as lead. |
| 5 | P2 | all whole-envelope and facade views | The brick reads as a grey-beige putty (about RGB 139/128/107), less yellow than the source stock brick (about 150–164/120–131/92). | Brick base colour desaturated / lighting compensation. | Shift the brick base toward a warmer yellow-brown, keeping the darker coursing lines. |
| 6 | P2 | facade_close, glass_close, doorcase vs front crop | The sash frames are bright white, the same value as the stone sills. In the source pixels the frames are a putty/greige, slightly darker than the sills. | A single white material is used for both joinery and stone. | Use a separate off-white joinery tone a little darker and warmer than the stone. |
| 7 | P2 | facade_close, mansard_dormers, front | There are two pale stone bands at roof level: a cornice band, then a strip of brick parapet, then the coping. The sources show the brick running straight up to a single stone coping under the mansard. | An extra cornice band was added. | Remove the lower band, or reduce it to a slim brick dentil course, and keep the single coping. |
| 8 | P2 | front_corner, chimney_stacks, left_side vs oblique, top | The two west stacks carry 3 pots each. The source west stacks carry 4–5 pots each. | The pot count was not matched per stack. | Use 4 pots on each west stack. |
| 9 | P2 | chimney_stacks, roof_lead, left_side | There are short black slits in the coping at the rear corners of the side parapets. | Corner coping pieces are mitred or butted without overlap. | Extend one coping piece through each corner. |
| 10 | P2 | east_side, front_corner, rear_side | A dark vertical seam runs from the ground to the extension top where the rear extension meets the main block's east wall. | The extension wall is set back from the main wall, with a void or unlit return. | Close the gap, or give the return the brick material and a visible reveal. |
| 11 | P2 | front, facade_close vs front source (west) | The west garden gate is not legible: the pier and wall are one tan tone, with only a faint recessed panel. The source shows a brick pier with a boarded timber gate. | The gate was given the brick material. | Give the gate a darker timber tone with vertical boarding. |
| 12 | P2 | front, front_corner (base) vs front source | The plinth projects as a plain brick step with no stone weathering band. The source shows a brick plinth under a stone band. | The plinth cap was omitted. | Add a thin stone cap to the plinth. |
| 13 | P2 | doorcase_balconette | The balconette end stays read as loose diagonal bars. A thin shadow gap shows between the underside of the balcony slab and the top of the doorcase entablature. | Stay orientation and a small vertical offset. | Run the stays straight back into the wall, and seat the slab on the entablature. |
| 14 | P2 | front, front_corner, aerial, left_side, right_side, rear | The plane tree has a low, flat umbrella crown, while the source tree is tall and reaches the attic. On camera: left_side has its lower half filled by the neighbour roof, and right_side and rear frame the target small. All three views are still legible. | Generic tree preset; camera distances. | Lift and enlarge the crown. Tighten right_side and rear, and raise the left_side camera above the neighbour ridge. |

## 3. Source conformance checklist

| item | status | view(s) used |
|---|---|---|
| Silhouette | Conforms. Brick box with a steep mansard; side walls rise above the mansard as coped parapets; stacks at the corners. | front, front_corner, aerial vs front, oblique |
| Storey count and bay rhythm | Conforms. Three brick storeys plus a mansard attic, five evenly spaced bays, door in the centre bay, dormers over the bays. | facade_close, front |
| Main block plan proportion | Conforms. Depth/width is about 0.66 in the top render, against about 0.66–0.68 in the locked top. | top vs top |
| Brick and joints | Deviates (P2 #5). Coursing lines are present, but the tone is greyer than the source. | facade_close, glass_close |
| Sashes: sizes per floor, bars, sills, flat arches | Conforms. First-floor windows are tallest, the second floor is shortest, the ground floor is intermediate. Six-over-six bars with meeting rails, projecting stone sills, gauged flat arches over every main window. Frame tone is P2 #6. | facade_close, architecture_close, glass_close |
| Doorcase (pilasters, frieze, fanlight, door) | Conforms. Stone pilasters with capitals, an entablature, a rectangular three-light fanlight, a black panelled door and a stone step. | doorcase_balconette, front |
| French window and balconette | Conforms. The centre first-floor opening drops behind a black iron balconette on the stone slab over the doorcase, and the interior shows it as a full-height opening. Minor stays/gap issue (P2 #13). | doorcase_balconette, interior, facade_close |
| String course and plinth | String course conforms (at first-floor level, returning onto the east wall). Plinth deviates: no stone band (P2 #12). | front, front_corner, east_side |
| Parapet and coping | Conforms, with an extra band (P2 #7). Short parapet with a stone coping. | mansard_dormers, front |
| Mansard (pitch, slate, dormers) | Conforms. Steep slate-grey lower slope, five dormers aligned to the bays with lead cheeks and cap, portrait sashes. Glazing pattern and pinholes are P2 #2–3. | mansard_dormers, front_corner, front |
| Lead flat and skylight | Partly deviates (P2 #4). The lead flat and the upstand skylight in the rear-west quarter conform. The source's slate upper slope is drawn as flat lead. | roof_lead, top vs top, oblique |
| Side parapets and chimney stacks with pots | Conforms. Side walls rise as coped parapets that follow the mansard profile. Two west stacks and one east stack, at plan positions matching the top source, each with a row of clay pots. West pot count is P2 #8. | chimney_stacks, aerial, top vs top, oblique |
| Side wall windows | Conforms. The east face has one column of windows on three floors with arches and sills, plus a downpipe at the front corner. The west face is not shown by any source; a single upper window is coherent. | east_side, right_side, front_corner vs oblique, front |
| Rear wing / rear range | **Deviates (P1 #1).** Extension roof material and lantern, and the parapet of the wing. | top, rear_side vs top |
| Passage | Conforms. A paved strip along the east side, bounded by a long brick wall with a front pier. | front_corner, aerial, top |
| Garden walls and gate | Partly deviates (P2 #11). The wall and pier are present; the gate is not legible. | front, facade_close vs front |
| Lamp | Conforms (simplified black standard at the front-east corner). | front, front_corner |
| Tree | Present in the right place. The form is weak (P2 #14). | front, aerial |
| Neighbour terrace | Conforms. A lower terrace to the west, with a white stucco ground floor, buff upper floors, a slate roof with dormers and potted stacks. | front, front_corner, aerial |
| Materials hierarchy | Mostly conforms: brick body, pale stone dressings, white joinery, slate mansard, lead flat, black ironwork and door, terracotta pots. It is broken on the rear extension roof (P1 #1). | all |
| North face | Not visible in any source. It is coherent: brick wall with two window columns, arches and sills. | rear, rear_north |

## 4. Camera validity

- No view has the target fully occluded, clipped or illegible. There is no P0 or P1 camera defect.
- left_side: the bottom-right half of the frame is the neighbour's roof. The rear and west upper faces of the target are still legible (P2 #14).
- right_side and rear: the target fills only about 15–20% of the frame width, but stays legible (P2 #14).
- top: the building is small in frame but fully legible, and its plan is readable.
- interior: valid. It shows window reveals and the balconette through the French window.

## 5. Previous-version findings (v002) re-checked in pixels

| v002 finding | status in v003 pixels | evidence |
|---|---|---|
| Dormer sashes broken: no bars in the upper sash, no glass or bottom rail in the lower, stub bars hanging, a floating sill, square openings | **Resolved.** All five dormers stand clear of the slope with tapered lead cheeks and a cap. Each has a full white frame, upper and lower sashes with complete bars, a meeting rail and bottom rail, grey glass visible behind the bars in both sashes, a stone sill on a slate apron, and a portrait opening. No stub bars, and no sill that floats visibly. Residual polish only: pinholes at the bar crossings and a hairline under the sill (P2 #2), and 2 rather than 3 panes across (P2 #3). | mansard_dormers (and zoomed crop), front, front_corner, chimney_stacks, roof_lead |
| Main block too deep in plan (about 0.83 to 1, where the locked top is about 0.65) | **Resolved.** Measured in the top render: about 248 px wide × 164 px deep, ≈ 0.66. The locked top measures ≈ 0.66–0.68. The stacks and the skylight sit at matching relative positions. | top vs top (zoomed crops) |
