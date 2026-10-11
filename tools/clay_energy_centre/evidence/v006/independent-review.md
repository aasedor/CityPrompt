# Independent RLASM v6.1 holistic review: clay energy centre v006

Reviewer: independent, pixel-only. Inputs inspected: `sources/front.png`, `sources/oblique.jpg`, `sources/top.jpg`; all 18 renders at full resolution, plus zoomed crops of the corner pier, the jambs and the roof plant; all four phone boards. No build code, reports, README or VERSIONS files were read. I checked every builder claim against the pixels.

## 1. Verdict

**VISUAL_REWORK_REQUIRED.** The v006 stack, north service bay and duct trunks clearly improve on v005, and the massing, storeys and identity elements all read correctly. Three P1 fidelity defects remain against the locked sources: the west-face corner bay has no brick head, the corner pier's return on the south face is too wide, and the roof duct spine sits in the wrong place.

**Counts: P0 = 0, P1 = 3, P2 = 10**

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | **P1** | left_side (corner bay x 775-1085, y 510-615); front_corner (x 480-630, y 600-700); board phone-03 left_side | The upper glazing of the west-face corner bay is a 2-row x 7-light curtain that starts right under the coping (left_side y 512). The bay reads as glass / panel / glass in equal thirds with no brick above. **Source:** front.png (x 410-570, y 180-365) and oblique.jpg (x 490-620, y 470-600) both show a solid brick head band, about 14% of the wall height, above a **single-row** punched window band (about 6 lights) sitting on the concrete panel. Only the **south** face has the curtain that runs to the coping. The two faces differ, and this brick head is part of the "brick-framed" identity. | The v005 "storey split on both corner bays" fix gave the south-face curtain recipe to both faces. | West face only: lower the window head so about 1/7 of the wall height (about 1.2-1.5 m) of brick runs from the coping to the head. Use one row of about 6 lights about 1/7 of the wall high. Raise the top of the concrete panel to meet the window sill, so the panel is about 36% and the ground glazing about 36%. Leave the south face as it is. |
| 2 | **P1** | front (x 230-333, the full height); front_corner (zoom x 680-745: the south return is as wide as or wider than the west pier); facade_close (x 0-550) | The corner pier returns onto the south face as a 3.8 m solid brick column, about 20% of the south brick face. It reads as a blank brick tower at the corner. **Source:** oblique.jpg shows a south-face return about half the width of the west-face pier (about 20 px vs about 40 px at x 430-490, y 430-730). In front.png the south-face glazing and concrete start almost at the corner (x 630), so the corner bay's glass and concrete turn the corner with only a slim brick edge. | The return was set to the same width as the widened west pier (claim 2). | Keep the west-face pier at about 3.8 m. Cut the south-face return to about 1.2-1.8 m and widen the south corner bay's curtain, panel and ground glazing westward to match. |
| 3 | **P1** | top (spine x 525-570, y 360-695; flues x 585-625, y 540); aerial (x 540-640, y 400-560); front_corner (roof); stack_contact | The 2 m north-south duct spine runs down the **middle** of the brick roof, about 52% of the way across from the west parapet, so the roof reads as an "I-beam" that splits the stack from the flues, and the three flues sit **east** of the spine. **Source:** top.jpg puts the north-south trunk next to the corten wall (about 80-86% across, x 578-610), with a short take-off stub into the corten wall at mid-depth. The flue cluster sits **west** of the spine, just north of the south bank (x 530-565, y 480-555), and the stack and flues share one open roof field. | The spine was placed "between the inner trunks" with no reference to where the source puts it east-west. | Move the spine east so its centreline is about 1.5-2 m clear of the corten wall, connecting the north and south bank trunk pairs near their take-off boxes. Add a short stub into the corten wall at mid-depth. Move the three flues to about 65-75% across and about 60-65% of the way from north to south, west of the spine and just north of the south bank. |
| 4 | P2 | f_roof zoom (front x 440-500, y 300-335); roof_plant (x 655-850, y 250-340); stack_contact | The stack's collar platform carries two separate guard-rail segments. The source collar is a plain plate. In roof_plant the struts kink with a visible gap of about 15 px to the tube at the pinch (x 705-725, y 490), where the source struts curve smoothly. | Added detail; straight segments. | Remove the rails or make one continuous rail, and bring the strut pinch onto the tube or a ring. |
| 5 | P2 | top (stack x 450-505, y 460-510) | The stack sits about 2 m north of the midpoint between the banks (the midpoint is y ≈ 540). | Offset. | Move it about 2 m south. |
| 6 | P2 | front_corner, roof_plant, stack_contact | The cooling-bank fans are flat black discs with no shrouds. The bank ends have no louvred faces, and the pipe rails along the banks are missing (source oblique). | Simplification. | Add short fan cowls, louvre end faces and one pipe rail per bank. |
| 7 | P2 | top (x 875-950, y 290-445 and x 880-945, y 720-785); aerial | The corten roof has a 3-fan unit in the centre and a single unit to the south. **Source:** a 2-fan unit and a 1-fan unit with a pipe loop, both in the west half of the north half of the roof. This P2 was carried over from v005 and is not addressed. | Not addressed. | Move and resize the units to match top.jpg. |
| 8 | P2 | front, corten_block, aerial | The corten panels are a rectilinear grid with horizontal joints, where the source has narrow vertical standing seams. The dark louvre on the corten west wall above the brick roof (front.png x 790-810, y 240-270; oblique) is missing. The corten block does not project about 1 m north past the brick volume (top.jpg). | Simplification. | Use vertical seams only, add the high louvre and extend the north face about 1 m. |
| 9 | P2 | left_side (x 500-690) | The tall glazed bay has 5 mullion columns. The source has 3-4 (front.png x 275-365). | Grid choice. | Use 4 columns. |
| 10 | P2 | left_side (x 280-470, y 515-550) | The north-bay clerestory sits right under the coping. front.png shows a brick head over it (oblique.jpg does not), so the sources disagree. | Source ambiguity. | Optional: add 0.5-0.8 m of brick head. |
| 11 | P2 | interior (x 0-190 and 1250-1440, y 255-365); glass_close; plant_window | The plant showcase is sparse: two boxes, a column and two pipe stubs that end in mid-air in the interior frame. The source shows dense pipework, pumps and cabinets behind the glass. | Low-density interior set. | Add 2-3 vertical pipe drops and a pump row, and end the pipe runs into the equipment. |
| 12 | P2 | front; boards/phone-01 | The "front" render is a square-on south elevation, but the locked front is a south-west 3/4 pedestrian view dominated by the **west** face. The board's Locked front / Render front pair therefore compares different faces. | Camera role. | Add or replace with a south-west eye-level 3/4 render matched to front.png for the board. |
| 13 | P2 | top | The two trunks of each bank pair have a gap about the width of one trunk; the source pair is tighter. The north-south spine runs fully into the south trunks, where the source stops just short. | Spacing. | Tighten the gap to about half a trunk width. |

## 3. Source conformance checklist

| item | status | view used |
|---|---|---|
| Silhouette (two volumes, taller corten block east, corten about 20% higher) | conforms | front, rear, front_corner vs front.png, oblique.jpg, top.jpg |
| Storey count (two-storey brick frame) | conforms | left_side, front |
| Bay rhythm and glazing (west face: north service bay / tall glazed entrance bay / corner bay; south face: corner bay + corten) | deviates: the west corner bay has no brick head or single-row band (F1); the south-face pier return is too wide (F2) | left_side, front, front_corner |
| Concrete panel (upper corner bay, both faces) | conforms in presence and recess. Its proportion on the west face follows F1. | facade_close, architecture_close, glass_close |
| Entrance (recessed glazed entrance with dark canopy, west face) | conforms | corner_entry, left_side |
| Corten block and slot (narrow full-height-ish slot near the east end of the south face) | conforms; panel seams are P2 (F8) | front, corten_block |
| Roof plant and stack (two 3-fan banks, duct trunks, 3-flue cluster, hourglass stack) | elements present; the hourglass stack now reads correctly. The layout deviates: the spine and flue placement are wrong (F3). | top, aerial, roof_plant, stack_contact |
| Materials hierarchy (buff-brown brick frame > grey concrete panel > dark glazing; dark corten block) | conforms (brick sampled at about 152/126/95 vs source about 172/130/88; concrete mid-grey) | front, left_side |

## 4. Camera validity

- No view is occluded, clipped or illegible. All 18 renders show their target.
- corten_block: a tree covers the lower left, but the slot window and panelling stay legible. Acceptable.
- interior: legible, but sparse (F11).
- The `front` role does not match the locked front viewpoint (F12, P2). It does not invalidate the view, but the source-vs-render board compares different faces.

## 5. Prior-version (v005) P1 findings: status judged from pixels

| v005 P1 | claimed fix | status | pixel evidence |
|---|---|---|---|
| 1. Stack | Slender tube in a square cage; collar at about 75% height, pinch at about mid-height, splay to a plinth; tie ring at about 1/3 height; midway between the banks | **resolved** (P2 residue: F4, F5) | front f_roof zoom, roof_plant, stack_contact: tube, collar, hourglass struts, tie ring and square plinth all read; the stack sits between the banks, about 2 m north of centre. |
| 2. West corner pier | Widened to about 3.8 m, corner bay narrowed to about 11.2 m, return on the south face the same width | **partly** | The west-face pier/bay ratio of about 0.32 matches the source (about 0.31). The equal-width south return is too wide against the source (F2). |
| 3. North service bay | 7-light clerestory, recessed concrete panel to grade, service door at the north end, brick on either side | **resolved** | left_side x 280-470: 7 lights, panel to grade, overhead door at the north end, brick piers on both sides. |
| 4. Roof ducts | Two parallel 2 m trunks per bank to a take-off box at the corten wall; north-south trunk between the inner trunks | **partly** | The trunk pairs, flanges and take-off boxes are present and touch the corten wall (top, roof_plant). The spine position and the flue side do not match the source (F3). |
| 5. Storey split | Thirds on both corner bays; curtain to 0.4 m below the coping | **partly** | South face: about 31/33/36%, which conforms. West face: wrong, because the source has a brick head and a single window band there (F1). |
| P2 (v005): warmer brick, mid-grey concrete, entrance curtain to the same head | (taken on the way) | resolved | front, left_side colour samples; corner_entry |
| P2 (v005): flue and corten roof | not addressed | not resolved | F7; the flue placement is now part of P1 F3 |
