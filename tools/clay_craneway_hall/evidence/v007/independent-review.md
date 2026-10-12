# Independent holistic review: clay crane-way hall, v007 (RLASM v6.1)

Reviewer: independent (did not build). Evidence used: sources/front.png, sources/oblique.jpg, sources/top.jpg, all 18 renders at full resolution, the four phone boards. No code, reports or builder notes were read as proof.

## 1. Verdict

**VISUAL_REWORK_REQUIRED**: the section, gable mouth, aisle west frames, braced aisle walls, stair and sidings now match the sources. The roof monitors are still wrong in form, glazing face and distribution. That remains a clearly visible identity defect against oblique.jpg and top.jpg.

Counts: P0 = 0, P1 = 2, P2 = 6

## 2. Findings table

Pixel regions are given as x0-x1, y0-y1 in the native 1440x1080 render, or in the 1195x896 / 1024x768 source.

| # | severity | view(s) with pixel regions | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | top (390-1050, 445-635); aerial (430-1045, 380-500); front_corner (495-1000, 405-500); monitor_close (700-1140, 0-320); architecture_close (380-1260, 0-300); sources oblique (380-1150, 40-410), top (255-1000, 90-530) | The monitors are still square in plan: each is about 65x65 px in top, the same in both directions. They read as tall, house-shaped boxes with large blank white cheek walls. The only glazing is a short strip of 3-4 lights high on the gabled face, which faces the long facade. In the sources the monitors are about twice as long as they are wide along their ridge. They sit low, and a continuous mullioned glazed band runs the full length of both long cheeks under the eaves. Their gable ends are solid cladding. The v007 "wider, lower" change does not show in the pixels: on the sloping nave roof the downhill cheek still reads as a tall blank wall (monitor_close 860-1140, 90-320). | The monitor footprint is nearly square, about 6x6.5 m. Glazing is applied to the gable end instead of the long sides. The cheek height is measured from the uphill eave, so the downhill side grows tall. | Rebuild each monitor at about 12-14 m along the ridge by about 6 m wide. Glaze both long cheeks over their full length as one mullioned band about 1.5 m tall. Keep the gable ends solid and corrugated. Seat the monitor on a level curb so that neither cheek exceeds about 2 m above the roof plane. Keep the low pitch and the eave overhang. |
| 2 | P1 | top (390-1050, 445-635): all nine monitors on the nave strip, with both aisle roof strips (y 345-440 and 640-720) empty; left_side and right_side (600-860, 370-415): three monitors at a single height; sources oblique (crop shows rows at three roof levels: the south row at 695-910, 300-410 sits on the south aisle roof outboard of the nave clerestory band 560-720, 450-560) and top (south row 540-700, 415-530; 715-860, 300-390; 860-990, 205-285, inboard of the outer aisle glazing and outboard of the nave clerestory) | The render packs all nine monitors into a staggered checkerboard on the two nave slopes. The sources show the three monitor rows on three roof levels: one row on the north aisle, one on the nave and one on the south aisle. As a result the stepped roofscape the sources show (monitors at three heights, aisle roofs carrying lanterns) is replaced by one crowded nave and two bare aisle roofs. | The three rows were laid out across the nave width instead of one row per roof. | Keep 3 monitors on the nave, centred on the ridge. Move one row of 3 onto each aisle roof, set between the nave clerestory and the aisle upper glazing, staggered in plan against the nave row as in top.jpg. Give each aisle row the same monitor form as finding 1. |
| 3 | P2 | stair_contact (1100-1310, 590-710) | The intermediate stair landing sits in the same plane as the bay's window hood and visibly merges into it. Its support post rises through the hood edge. | The landing height coincides with the hood height. | Raise or lower the landing by 0.3-0.5 m, or cut the hood back in that bay so the landing clears it. |
| 4 | P2 | facade_close (355-390, 340-460; 800-840, 365-470; 1140-1190, 390-480); side_doors (465-500, 105-265; 980-1035, 175-305) | Diagonal gallery knee braces run from the gallery fascia into the face of the lattice columns. They end mid-column across the X-bracing instead of landing on a node. | The braces were placed independently of the lattice tier nodes. | End each brace on the top lattice node, or on a cleat on the column chord. |
| 5 | P2 | crane_interior (140-1420, 490-625; 805-820, 490-765); front_corner (355-465, 515-600); source oblique (215-720, 470-610) | The overhead crane is present but weakly legible. From the oblique-role camera the gable mouth reads as a dark void. In the close view the bridge reads as a horizontal braced deck. The hook line hangs almost to the floor. The source shows a distinct crane bridge with railings, a trolley cab and a yellow hook high in the mouth. | Thin, low-contrast bridge girders; the hook rope is too long. | Use deeper twin bridge girders with a walkway rail and a boxy trolley, give the hook a source-yellow tone, and shorten the rope so the hook hangs in the upper third. |
| 6 | P2 | interior (700-940, 80-330) | The nave ceiling is closed, with only panel outlines under the monitors. No monitor openings or light wells read from inside, and no crane runway girders run along the nave. | The ceiling is a continuous plane. | Cut the openings for the monitor throats and add runway girders on the nave columns. |
| 7 | P2 | all whole-envelope views; facade_close | The lattice steel, frames and cladding all share one pale clay tone. The source separates dark steel from the lighter corrugated cladding, so the steel-versus-cladding hierarchy is weak. | One palette slot is used for both. | Darken the structural steel slot (columns, lattice, mouth frame, stair) by about 25-30% against the cladding. |
| 8 | P2 | front (whole) vs source front | The front render is a straight south elevation and shows neither the west gable mouth nor the green doors. The source front is a south-west corner view in which the gable mouth dominates. The front_corner render covers this role, so legibility is not lost. | The camera is set to the elevation axis. | Optionally yaw the front camera about 30 degrees toward the west gable to match the source role. |

## 3. Source conformance checklist

| item | status | view used |
|---|---|---|
| Silhouette | conforms for nave/aisle stepping; deviates at roofscape (monitors, findings 1-2) | left_side, front, front_corner, aerial |
| Section (nave and aisles) | conforms: tall nave, aisles with a solid lower storey, a gallery and a tall glazed upper storey under a thin roof strip, and a clerestory band above | front (290-1150, 440-645), left_side, architecture_close |
| Bay rhythm and bracing | conforms: projecting X-braced lattice columns in tiers, with hooded windows between them in every bay on both long sides | facade_close, side_doors, glass_close, yard_sidings, rear |
| Gable mouth and doors | conforms: solid lower storey with three green sliding leaves, open steel frame above, glazed band under the gable triangle | left_side, gable_mouth, front_corner |
| Monitors and clerestory | clerestory conforms; monitors deviate (findings 1-2) | top, aerial, monitor_close, architecture_close |
| Crane and interior | conforms in presence, weak in legibility (P2 findings 5-6) | crane_interior, gable_mouth, interior |
| Stair | conforms: SW-corner switchback in the same sense as the source (lower flight rising east to a landing, upper flight returning west to the gallery), grounded; minor hood clash (P2 finding 3) | stair_contact, front_corner, front |
| Yard and sidings | conforms: concrete apron, two sidings on the north side, a boxcar on wheels sitting on the rails | top, yard_sidings, rear, rear_side, right_side |
| Materials hierarchy | partially conforms: green doors and red boxcar read; steel is not separated from cladding (P2 finding 7) | all |
| East gable (not in sources) | coherent: plain nave gable with an industrial door and lower aisle blocks | right_side, aerial |

## 4. Camera validity

No view has an occluded target, a clipped asset or an illegible subject. Front, rear and the side views frame the building at about 60% of the frame width. That is small on the phone board but still legible. The close views each show their named subject.

## 5. Previous-version (v006) findings

1. **Aisle roof read as a wide blank lean-to above the gallery: RESOLVED in pixels.** The aisle upper storey now reads as a full-height glazed band above the gallery rail, under a thin roof edge. See front (290-1150, 515-560), facade_close (0-1440, 40-380) and architecture_close (0-1440, 600-1000).
2. **West aisle upper storeys were short lean-to wedges: RESOLVED in pixels.** Both aisle ends are now upright rectangular open frames with mid posts and X-bracing at full upper-storey height. See left_side (440-570, 515-580 and 865-1000, 510-580), front_corner (310-420 and 25-120 of the crop region 290-1090, 390-760) and gable_mouth (230-420, 410-560).
3. **Monitors were small near-square tall boxes: NOT RESOLVED in pixels.** They are still square in plan and still read as tall, blank-cheeked boxes, and they carry only a small gable-end window strip. See P1 finding 1. A new related defect is the distribution of all monitors on the nave (P1 finding 2).
