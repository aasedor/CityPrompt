# Independent RLASM v6.1 holistic review — Halifax Georgian colonial house, clay v001

Reviewer: independent source-locked architectural-clay reviewer (did not build this candidate).
Inputs examined at full resolution: `sources/front.png`, `sources/oblique.jpg`, `sources/top.jpg`; all 18 renders in `renders/` (1440 x 1080); the four phone boards in `boards/`. Zoomed crops for the evidence below are in `review/crops_qvtmzk/`. All pixel coordinates refer to the 1440 x 1080 renders. Luminance (L) is the 0–255 grey value of the pixel.

## 1. Verdict

Verdict: FAIL

Counts: P0=0 P1=3 P2=11

The house is clearly the right building, with no P0 problems. Under the brief's verdict vocabulary this is VISUAL_REWORK_REQUIRED, for three reasons: the east whole-envelope camera (`right_side`) is invalid; the main entrance has pure-black geometry slits at stone-trim junctions; and the street railing and front-yard landscape do not match the locked top and front sources.

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | evidence | likely cause | finite fix |
|---|---|---|---|---|---|---|
| 1 | P1 | right_side (also aerial, roof_deck) | The "right_side" whole-envelope camera sits at grade in the narrow passage between the east wall and the neighbour, with an extreme wide-angle, worm's-eye perspective. The east front is seen at a grazing angle. The eave and cornice are cut by the top edge, the façade runs off the left edge, and a street-tree trunk and canopy block the centre of the frame. Neither end of the east front, its roof edge, nor its four-bay rhythm can be read. No other render proves the east front at whole-envelope scale. In `aerial` it is mostly hidden behind the neighbour, and `roof_deck` shows only a sliver at the bottom-right. | right_side full frame: red-brick wall from x=0 to 790 rising out of the top edge; trunk at x≈800–850 runs top to bottom; neighbour wall fills x≈990–1440. | The camera was placed by nominal side offset without allowing for the neighbour gap of about 3.5 m (top: 115 px gap against a 734 px house width). | Re-author `right_side` as an elevated south-east or east three-quarter view above the neighbour's eave. Alternatively, render the east elevation proof with the neighbour context hidden. Frame grade to chimney-pot top and the full depth, including the east rear wing, with a visible neutral margin. Rerender and re-review. |
| 2 | P1 | facade_close, porch_columns, architecture_close | Pure-black, hard-edged slits appear at stone-trim junctions of the main entrance. There is one across the top of each door-surround pilaster, directly under the door head and frieze block. A further black sliver sits under the pediment corner block where it meets the pilaster capital. | facade_close (608–637, 606–607) and (803–832, 606–607): L = 1–7, with neighbours at L ≈ 98. Vertical profile at x=620 is 98, 96, 66, **7**, 20, 80, 102. porch_columns (457–491, 332–345) and (706–738, 416–427): L = 0. architecture_close (1122–1128, 629–631): L = 0. Crops: `chk_porch_door.png`, `facade_doorslots.png`, `porch_slots.png`, `arch_rakecorner.png`. **Not contact shadow:** each slit lies on fully lit, camera-facing stone planes. It is 1–2 px tall with no soft fall-off, stops exactly at the member's width, and reaches L 0–7. Real contact shadow elsewhere in the same renders (for example under the lintels in `glass_close`) is a soft gradient that never drops below L ≈ 60. **Not dark-by-design:** the black iron downpipes are continuous vertical members at L ≈ 18–40 (for example architecture_close x 1183–1238), and the railings are similar. These slits are short horizontal voids between two pale stone volumes. | The door-surround pilasters stop short of the underside of the head block, or overlap it without a cap, which leaves an open gap onto the void behind. The pediment corner block and the capital have the same kind of gap. | Extend the pilaster tops to meet the head block's underside, or add a cap block that overlaps by 5 mm or more. Close the junction between the pediment return and the capital the same way. Check every stone-trim junction of the same family (window surrounds, the pilaster/entablature in the pavilion). Rerender `facade_close`, `porch_columns` and `architecture_close` and re-scan for L < 22 clusters. |
| 3 | P1 | front, top, front_corner, garden_fence | In the sources the street railing runs only along the west garden. In `sources/top.jpg` it ends at x ≈ 280 of 1195, at the west brick path, and in `sources/front.png` it ends at the south-west corner, x ≈ 450. In front of the house, either side of the portico, the sources show open lawns behind a low curb with low box-hedge edging. In the render the railing continues east along the street, in front of the two western bays of the south front, as far as the portico walk. The front lawns are plain grass with no low hedges. | top render: the railing line at y ≈ 892 runs from x=60 to x ≈ 620 (`top_frontrail.png`). front render: the railing crosses x 0–975, past the SW corner downpipes at x ≈ 625–660 and up to the portico steps (`front_left.png`). Source front: the railing ends at x ≈ 450 and is followed by a hedge and curb run (x 430–660, y 520–575). | The phrase "along the street" was read as the whole western frontage instead of following the plan in the top view, which governs. Front-lawn edging hedges were omitted. | End the street railing at the east edge of the west garden (the west brick path), with an end post. Add a low stone curb and low box-hedge edging to the front lawns either side of the portico walk, as in source top (y ≈ 665–680) and source front. Rerender `front`, `top`, `front_corner`, `aerial` and `garden_fence`. |
| 4 | P2 | top, front_corner, aerial, front | The pavilion gable ridge runs back almost to the edge of the flat deck. The pediment and gable therefore read taller and deeper relative to the main hip than in the sources. | top: ridge apex at y ≈ 655 against the deck front edge at y ≈ 640, about 90% of the run from eave to deck. Source top: apex at y ≈ 565 against the deck at 515, about 66%. | The gable pitch or depth was set without matching the source's ridge-to-hip intersection. | Lower the pavilion gable ridge so it dies into the hip about two-thirds of the way up the slope. |
| 5 | P2 | front_corner, aerial, cornice_chimneys, roof_deck | The main roof's course lines are very coarse, about 10 per slope. They read more like board or panel roofing than slate. | cornice_chimneys, main slope. | The course spacing is too large. | Use about twice as many course lines on the slate planes. |
| 6 | P2 | facade_close, porch_columns | The front door has a rectangular four-light transom, not a fanlight. Its panes read near-black (L 5–20) because the hall behind is unlit. The sash depth and muntin returns are visible, so this is a dark interior, not a void. | `chk_facade_transom.png` | A simplified transom; the interior is unlit. | Use a segmental or elliptical fanlight head, and give the hall interior the same light-catching finish as the room interiors seen through the sashes. |
| 7 | P2 | porch_columns, architecture_close, facade_close | Hairline dark creases (1 px, L 5–17) run along some lintel-to-reveal and sill-to-frame joints when seen from oblique close cameras. They are absent in the head-on `glass_close`. | porch_columns lintel (0–238, 220–296); architecture_close sill (915–966, 1005); facade_close upper heads y=294. The profile is a single dark pixel with a gradient on both sides, consistent with a very tight contact or a sub-millimetre gap. | Members are butted with no overlap. | Overlap the lintels and sills into the reveal by a few mm. |
| 8 | P2 | architecture_close, cornice_chimneys | Where the pediment's rake meets the eave, the main eave gutter and fascia stop open-ended against the side of the pediment corner block, leaving a shaded pocket. | architecture_close (1195–1215, 575–605), L ≈ 53. | No end return or cap on the eave run. | Add an end return or cap where the eave meets the pediment block. |
| 9 | P2 | front_corner, aerial, rear_side, cornice_chimneys | From high cameras the modillions read as a coarse toothed band with brick showing between the blocks. The source shows a continuous white corona and soffit with denser, smaller modillions. | `cornice_hipcorner.png` | The corona projection is small relative to the modillions, and their spacing is wide. | Deepen the corona and soffit, and use smaller, closer modillions. |
| 10 | P2 | rear, rear_wings | The rear (court) door is a plain slab with no surround or fanlight, and the north front has no downpipes. This face is not shown in any source, so it is judged for coherence only. | rear (695–745, 680–785) | Simplified rear entrance. | Add a simple stone surround and transom, and downpipes at the wing re-entrant corners. |
| 11 | P2 | front, aerial, rear, cornice_chimneys | The east neighbour reads as a beige rendered wall, not grey coursed stone, and its gables are plain instead of the stepped gable parapets in the source oblique. | aerial (900–1440, 330–1080) | Context palette and simplified gables. | Use a grey stone palette value and add stepped gable parapets. |
| 12 | P2 | garden_fence, west_front | The tree trunks show a visible step in diameter just below the canopy. | `chk_gardenfence_tree.png`, `chk_westfront_tree.png` | Two trunk segments with mismatched radii. | Taper the trunk as a single piece. |
| 13 | P2 | rear, rear_wings, facade_close, interior | The brick reads light salmon or pink under the lit north-side views, against the deeper red of the sources. The portico entablature is heavy relative to its columns. The interior walls use the exterior brick colour. | rear, rear_wings, facade_close | Palette and proportion choices. | Darken the brick value slightly, slim the portico entablature, and use a plaster colour for the interior. |
| 14 | P2 | front_corner | The base of the west front touches the bottom edge of the frame, and the neighbour is cut at the top right. | front_corner bottom edge at y=1080 across x 180–660 | Framing matches the locked oblique source, which crops the same way. | Optionally pull back about 5% so the plinth clears the bottom edge; `aerial` already proves the full envelope. |

No P0 findings. Checks that came back negative:
- **Top view:** no dark stripes from open gaps between volumes. The only L < 22 clusters in `top` are tree shadows (x 334–350, y 626–656, a green-hued shadow on the brick path) and the two cone tops.
- **Hip and wing junctions:** the wing hips, valleys and main hips meet cleanly in `top_wingW.png`, `top_wingE.png` and `rearwings_corner.png`.
- **Hip-to-eave corners:** clean in `left_side`, `rear_wings` and `cornice_chimneys`.
- **Wing roofs:** the parallel "stepped" roof slices seen beyond the north-west and north-east hips in `front_corner` and `aerial` are the outer slopes of the inset rear wings. Their course lines run parallel to their own eaves, so the geometry is coherent; it is not a floating plate.
- **Grey band behind the deck in roof_deck:** the unseamed band at (940–1040, 465–530) is the main north slope over the court seen at a grazing angle (L ≈ 117–123, the same family as the shaded roof). It is not a void.
- **Remaining dark clusters:** every other L < 22 cluster in the 18 renders is a downpipe, hopper, railing or dark-green foliage underside (dark-by-design hue, not black).

## 3. Source conformance checklist

| item | status | view(s) used |
|---|---|---|
| Silhouette (free-standing two-storey hipped block, deck, four stacks, pedimented pavilion, portico) | conforms | front vs source front; front_corner and aerial vs source oblique |
| Storey count (2) | conforms | front, left_side, rear |
| Plan: main block (nearly square, about 1.4:1 including the pavilion bay) | conforms | top vs source top (734x525 px against 606x425 px; ratio 1.40 against 1.43) |
| Plan: pavilion projection (slight) | conforms | top, rear_side, front_pav crop |
| Plan: rear wings and recessed court | conforms (wings inset from the side walls, projecting about 10%, as in source) | top, rear, rear_wings |
| Plan: portico | conforms (slightly wider: 37% of the front against 30%) | top, front |
| Brick coursing | conforms (coursed line pattern) | glass_close, west_front |
| Window grid: seven bays on the south front (2+3+2) | conforms | front, front_corner |
| Window grid: four bays per side | west conforms; east not reliably verifiable (`right_side` is invalid, `aerial` is partly occluded) | left_side, west_front; right_side, aerial |
| Sashes and glazing bars (three panes wide) | conforms | glass_close, west_front, interior |
| Lintels (shouldered with raised centre) and sills | conforms (hairline creases are P2 #7) | glass_close, west_front |
| Stone plinth | conforms | rear, left_side, west_front |
| Stone first-floor string course | conforms | glass_close, left_side |
| White eave cornice and modillions | conforms (toothed read from high cameras is P2 #9) | west_front, rear_wings, cornice_chimneys |
| Pavilion: four giant pilasters | conforms | front_pav crop, facade_close |
| Pavilion: capitals | conforms (simple block capitals) | architecture_close |
| Pavilion: entablature | conforms | architecture_close, facade_close |
| Pavilion: brick pediment with stone rakes | conforms (rake-to-eave pocket is P2 #8) | architecture_close |
| Pavilion: oval cartouche | conforms | architecture_close, front_pav crop |
| Pavilion: slate gable running back into the hip | deviates (ridge too deep, P2 #4) | top, front_corner, roofdeck_pav crop |
| Portico: stone platform | conforms | front, porch_columns |
| Portico: steps | conforms | front, facade_close |
| Portico: four Tuscan columns | conforms | porch_columns, facade_close |
| Portico: entablature | conforms (heavy, P2 #13) | facade_close |
| Portico: low hipped standing-seam roof | conforms | top_pav crop, architecture_close |
| Front door (panelled) and fanlight | door conforms; fanlight deviates (rectangular transom, P2 #6); black junction slits (P1 #2) | facade_close, porch_columns |
| Roof: hips | conforms | top, cornice_chimneys, left_side |
| Roof: slate courses | deviates (too coarse, P2 #5) | cornice_chimneys |
| Roof: flat lead deck | conforms | roof_deck, top |
| Roof: four corner chimney stacks with clay pots | conforms (three pots each, at the deck corners) | roof_deck, top, front |
| Roof: rear wings hipped into the main roof | conforms | top, rear_wings, rear_side |
| Dark downpipes | conforms on south and west (north missing, P2 #10) | front, west_front, garden_fence |
| Box-hedge parterres (west and north) | conforms | top, left_side, rear |
| Brick paths | conforms | top, rear_side |
| Lawns and hedges (low hedges before the front) | deviates (front low hedges and curb missing, P1 #3) | top, front |
| Tall iron railing (street at the west garden, and the west side) | deviates (runs on along the south front to the portico walk, P1 #3) | top, front, garden_fence |
| Trees (conical evergreens at SW, dark tree by the west front, NW/NE/E trees, two street trees) | conforms | top, front, left_side, garden_fence |
| Grey stone Georgian neighbour with gabled slate roof and dormers to the east | massing and dormers conform; material and gable parapets deviate (P2 #11) | top, aerial, front_corner |
| Streets and sidewalks (south street, west street) | conforms | top, aerial, front_corner |
| Materials hierarchy (red brick body, pale stone dressings, blue-grey roof, pale deck, dark iron, green landscape) | conforms (brick slightly pink in lit views, P2 #13) | all |

## 4. Camera validity

- **right_side — INVALID (P1 #1).** The target is clipped on the top and left edges and occluded in the centre by a street tree. The perspective is too extreme to read the east front's envelope or bay rhythm. It must be reframed and the full set rerendered.
- **front_corner — valid with note (P2).** The base of the west front touches the bottom edge of the frame and the neighbour is cut at the top right. This matches the cropping of the locked oblique source, and `aerial` gives the full envelope with margin.
- **facade_close — valid.** A canopy fragment intrudes at the top (x 510–740, y 0–45); the target is unaffected.
- **Other whole-envelope views — valid.** `front`, `aerial`, `top`, `left_side`, `rear` and `rear_side` show the whole asset with neutral margin and a legible target. In `front`, about 30% of the frame is empty foreground ground plane, but the target is still legible.
- **Remaining detail views — valid.** `architecture_close`, `glass_close`, `porch_columns`, `cornice_chimneys`, `west_front`, `roof_deck`, `rear_wings`, `interior` and `garden_fence` each frame their intended detail. Any cropping of the roof or chimney tops in detail views is intentional.
