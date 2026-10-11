# Independent RLASM v6.1 holistic review: clay energy centre v007

Reviewer: independent (no relationship with the builder). Evidence used: only `sources/front.png`, `sources/oblique.jpg`, `sources/top.jpg`, the 18 renders in `renders/`, and the 4 phone boards in `boards/`. I opened every image at full resolution, plus crops of the sources and renders where I needed to measure. I did not read any build code, reports or notes.

## 1. Verdict

**VISUAL_REWORK_REQUIRED**: all three v006 P1s are fixed in the pixels. One P1 remains: the bay rhythm of the west face is wrong. The north grey bay is about 35-40 % too narrow and the corner bay too wide, which is clearly visible next to the locked oblique.

**Counts: P0 = 0, P1 = 1, P2 = 10**

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | **P1** | left_side.png (bays at x≈280-470 vs x≈775-1085, y≈500-830); front_corner.png (grey bay x≈290-360 vs corner bay x≈480-630, y≈540-880); boards/phone-01 middle row | **West-face bay rhythm is wrong.** In the render, the north grey-panel bay (with the overhead door) is about 190 px wide and the brick-framed corner bay (lights, concrete, glass) about 310 px, a ratio of about 0.61. The corner bay takes about 33 % of the face and the north bay about 20 %. In the sources the north bay is nearly as wide as the corner bay. Along the oblique coping, the north bay measures about 115 px and the corner bay about 140 px, and the north bay is farther from the camera, so its true ratio is about 0.9 or more. In the source front, the far-left bay is about 265 px against 320 px for the corner bay, again while farther away. The sources give the north bay about 28-30 % and the corner bay about 26-27 % of the face. In the side-by-side, the render's corner bay dominates the west face and its grey bay reads as a narrow strip. | The bay widths along the west face were set without measuring them against the sources. The corner bay was enlarged, probably while rebuilding the head band and lights for the v006 fix, and the north bay absorbed the difference. | Keep the total west-face length and the pier widths. Re-split the bays to about: north pier 3 %, grey bay 29 %, pier 3 %, tall glazed bay 20 %, pier 9 %, corner bay 27 %, corner pier 9 %. That makes the grey bay about 1.0-1.1 times the corner bay. Keep the corner bay's head-band, lights, concrete and glass ratios (15/14/36/35 %), and keep about six lights by widening the light module slightly. Then re-render left_side and front_corner. |
| 2 | P2 | corner_entry.png (canopy y≈380-430, lower glass y≈430-750); left_side.png (canopy y≈712) | The entrance zone in the tall glazed bay is too tall. The canopy sits about 65 % of the way down the bay, so the entry glass is about 32 % of the wall height. The source front shows a low soffit with the entry under it at about 20 % of the height. A shallow recess reveal is visible at the left jamb, so the opening does have depth. | The canopy height is set to a storey line rather than the source door head. | Lower the canopy or soffit to about 80 % of the wall height (just above the door transom), and deepen the recess slightly under it. |
| 3 | P2 | left_side.png (ribbon y≈517-550 over grey bay) | The clerestory ribbon over the north grey bay is about 10 % of the wall height. The sources show about 17-20 %, with taller lights. | The light module was kept too short. | Make the ribbon lights about 1.8 times taller. |
| 4 | P2 | corten roof in top.png (x≈875-950, y≈290-445), aerial.png, roof_plant.png | The northern corten rooftop unit has 3 fans. In the source top it has 2 fans and sits in the west third of the corten roof, with pipe loops running from it to the single-fan unit. The render's pipe loops are missing and the unit is centred. | The bank fan-box component was reused. | Use 2 fans, move the unit to about 25-35 % of the corten roof width from its west edge, and add a simple rectangular pipe loop to the single-fan unit. |
| 5 | P2 | architecture_close.png (corten wall above brick roof, x≈670-920, y≈170-350) | The source front shows a dark louvre or recess band high on the corten west face above the brick roof. The render shows plain corten there. | The element is omitted. | Add one horizontal louvre panel at that position. |
| 6 | P2 | front.png (slot x≈1030-1065, y≈428-770) | The corten slot runs almost to the parapet. In the source front it starts about 20 % down the face, and it sits about 70 % across the face from the west (about 61 % in the render). | Slot extents. | Lower the slot head by about 15 % of the height and shift it about 0.5 m east. |
| 7 | P2 | roof_plant.png (railing panels x≈655-705 and 795-850, y≈255-340); stack_contact.png | The hourglass stack's platform carries only two short, separate railing panels, which read as fragments. | Partial guardrail. | Make the guard continuous around the platform, or remove it. |
| 8 | P2 | facade_close.png, glass_close.png, corten_block.png | The panel joints on the board-formed concrete and on the corten are drawn as thin orange lines. That colour belongs to neither material and reads as a texture error up close. | One joint colour is used for every material. | Use a joint tone slightly darker than each base colour. |
| 9 | P2 | front.png vs sources/front.png | The "front" render is a square-on south elevation, but the locked front is a three-quarter SW view dominated by the west face, so front cannot be compared like for like. left_side plus front_corner cover the comparison, so the camera is still valid. | Camera role definition. | Add or redefine front as a SW three-quarter street-level view that matches the locked front. |
| 10 | P2 | left_side.png (glazed bay x≈500-690) | The tall glazed bay has 5 mullion columns. The sources read as about 3-4 wider lights. | Mullion module. | Use 4 columns. |
| 11 | P2 | front.png (concrete band y≈598-700) | The board-formed concrete band on the south face is a little short: about 31 % of the wall, against about 38 % in the source front. The upper curtain is correspondingly taller. | Band split. | Move the curtain sill up by about 0.5 m. |

## 3. Source conformance checklist

| item | status | view(s) used |
|---|---|---|
| Silhouette (two volumes: lower brick frame W, taller corten block E, flush south line) | conforms | top.png vs top.jpg (brick 400x720 px against corten about 365 wide, the same plan ratio of about 0.55); rear.png (corten about 1.2 times the brick height, matching the source front) |
| Storey count (two-storey brick frame, taller corten block) | conforms | left_side, front, rear |
| Bay rhythm and glazing | **deviates** (finding 1). The order and typology of the bays conform: grey bay with overhead door, tall glazed bay, pier, corner bay, corner pier. The widths do not. | left_side, front_corner vs oblique.jpg and front.png |
| Concrete corner panel (west corner bay: brick head band about 15 %, single row of 6 lights, concrete, glass) | conforms | left_side (band y 493-543 over a wall of 493-830), front_corner, glass_close |
| South face (two-row curtain to the coping, concrete band, ground glazing with concrete column and door) | conforms (band proportion is P2) | front, facade_close, plant_window |
| Corner pier return | conforms. The south return is about 38-44 % of the west pier width, and the glass and concrete turn almost to the corner. | front (x 230-270 vs left_side x 1085-1190), front_corner crop |
| Entrance (tall glazed bay, canopy, recessed doors) | conforms in position (it matches the source pixels: the middle bay, north of the corner bay); the entrance zone proportion is P2 | corner_entry, left_side |
| Corten block and slot | conforms (minor slot extent P2) | front, corten_block, aerial |
| Roof plant and stack: two 3-fan banks with twin duct runs east to the corten wall; N-S trunk beside the corten wall with a stub into it; three flues west of the trunk, just north of the south bank; hourglass stack between the banks in the west third; two corten rooftop units | conforms (corten unit fan count P2) | top.png vs top.jpg, roof_plant, stack_contact, front_corner |
| Materials hierarchy (buff brick frame, light board-formed concrete, dark-framed glass, dark corten, light membrane) | conforms (joint colour P2) | all whole-envelope views |
| North and east faces (no source) | coherent: blank brick and corten with service door and louvre | rear, right_side, rear_side, rear_service |

## 4. Camera validity

No view has its target occluded or clipped, and every view is legible. Every detail view shows its named subject. front.png is valid but does not match the locked front's role (P2, finding 9). Contact checks pass: the duct runs rest on visible supports, the stack and flues stand on plinths, the bank ducts butt the corten wall without passing through it, and the flues are clear of the trunk (top.png x 585-625 vs trunk x 655-700).

## 5. v006 findings: status judged from the v007 pixels

| v006 finding | status | evidence |
|---|---|---|
| P1: the west-face corner bay's upper glazing was a two-row curtain running to the coping; the sources show a solid brick head band (about 14 %) over a single row of about 6 lights on the concrete panel | **resolved** | left_side.png: the brick band runs y 493-543 (about 15 % of the 337 px wall), with 6 lights at y 543-590 over concrete at y 590-712. front_corner shows the same. Only the south face carries the curtain to the coping (front.png, architecture_close). |
| P1: the corner pier returned onto the south face as a 3.8 m brick column; the source return is about half the west pier's width | **resolved** | front.png: the south return is about 40 px against the west pier's 105 px in left_side at the same scale (about 0.38). The front_corner crop gives 35 vs 80 px (about 0.44). The glass and concrete turn almost to the corner. |
| P1: the N-S duct spine ran down the middle of the roof with the flues east of it; the source puts the trunk beside the corten wall with a stub into it, and the flues west of it just north of the south bank | **resolved** | top.png: the trunk is at x 655-700 next to the corten wall at x 740, with a stub at y 525-550. The three flues are at x 585-625, y 635, which is west of the trunk and just north of the south bank (y 685-825). roof_plant and stack_contact confirm this. |
