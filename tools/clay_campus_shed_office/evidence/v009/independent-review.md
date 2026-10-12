# Independent holistic review — clay-campus-shed-office v009 (RLASM v6.1)

Reviewer: independent (did not build; read only `sources/`, `renders/`, `boards/` and the brief). All pixel coordinates are in the native 1440 x 1080 render frame unless marked `src`.

## 1. Verdict

**PASS_ZERO_P0_P1** — every identity element (sawtooth silhouette over a braced portal-frame office box, two-bay west face with the corner entrance canopy, cantilevered dock canopy over a raised dock with a two-bay ramp and two stairs, terrace rail and rooftop plant) is present in the rendered pixels with the source's rhythm, and the three v008 P1 defects are gone; what remains is polish.

Counts: P0 = 0, P1 = 0, P2 = 9

## 2. Findings table

| # | severity | view(s) with pixel regions | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P2 | front.png x 410–1028, y 460–525; architecture_close.png x 320–1110, y 390–720 | The canopy-bay tie rods are the same section as the X-brace flats (≈4 px in front, ≈10 px in architecture_close vs ≈12–14 px for the X in facade_close). In `src/front.png` the rods are visibly ~1/3 the width of the X flats, so the "thin rod vs heavy brace" hierarchy is flattened. | one shared member profile used for both brace types | give the four rod members a profile ≈ 0.35 x the X-brace flat (keep the same in-plane full-bay diagonal geometry) |
| 2 | P2 | front.png x 410–1190, y 518–548; facade_close.png x 730–1440, y 350–470 | Dock canopy is a thin slab (~12 px) with a sliver of charcoal cladding visible between its underside and the floor beam; `src/front.png` x 700–1000, y 400–470 shows a deep fascia that covers that zone down to the beam. | canopy modelled as a plate, no fascia depth | deepen the fascia to ≈ 2.5 x the current slab thickness so its underside lands on the floor-beam top |
| 3 | P2 | clerestory_close.png x 0–1440, y 580–1000; front_corner.png x 300–1060, y 390–470 | Each monitor clerestory is a two-row grid (tall lower row + short upper row). `src/oblique.jpg` y 80–200 and `src/top.jpg` show a single row of tall panes with one transom. | glazing module split into two rows | single row of tall panes with one mid transom, same mullion pitch |
| 4 | P2 | facade_close.png x 450–1200, y 650–1050; front.png x 265–568, y 590–640; top.png x 325–456, y 830–880 | A balustrade rail runs the full outer edge of the ramp. None of the three sources shows a rail on the ramp — only the yellow kerb (`src/front.png` x 640–900, y 580–650; `src/oblique.jpg` x 690–920, y 640–960). | added safety entourage | delete the ramp rail, keep the yellow kerb; keep the short rails on the two stairs (those are in the sources) |
| 5 | P2 | entrance_corner.png x 230–420, y 390–440 | A strip of transom glazing runs above the entrance canopy across the north (window) bay of the west face. `src/front.png` x 230–370, y 430–470 shows a solid dark sign band there; the strip glazing exists only on the corner bay in the source. | transom strip copied across both bays | remove the transom strip from the north bay only; keep it on the corner bay |
| 6 | P2 | entrance_corner.png x 460–900, y 490–790; front_corner.png x 500–580, y 640–730 | Corner-bay ground floor of the west face is a full-bay glazed shopfront. `src/front.png` x 420–530, y 480–600 shows a half-bay glazed panel with a dark corrugated panel against the corner column. | simplification | split the shopfront: ≈ 0.6 bay glass + ≈ 0.4 bay charcoal panel at the corner-column end |
| 7 | P2 | left_side.png x 740–830, y 525–600 | The low-poly tree sits in front of the west face and hides the north end of the entrance canopy, the sign plate and part of the window above the door, so the whole-envelope west elevation does not show the canopy start. (The detail views entrance_corner and front_corner show it clearly, so this is not a camera failure.) | entourage placed on the camera axis of the side elevation | move the tree ≈ 1 bay north (toward the shed) or omit it from the left_side render only |
| 8 | P2 | right_side.png x 345–560, y 450–660; rear_side.png x 220–300, y 480–640 | The box's east face is split by a mid column into two half-width bays (~100 px each) while every other portal bay on the box is a full bay; the terrace depth equals ≈ 1.1 south-face bays, so the extra column has no structural reading. No source shows this face; judged for coherence only. | east face subdivided to fit windows | remove the mid column; place the two windows and the door within one full bay, keep the ladder |
| 9 | P2 | dock_contact.png x 260–305, y 430–530; rear.png x 795–820, y 605–660 | Person doors on the dock face and the north wall have a frame and a set-back leaf but the reveal is very shallow (≈ 1–2 px at 4x zoom); at whole-envelope distance (front.png x 600–620) they read as flat black rectangles. All other openings (windows, roll-up doors, clerestories, entrance doors) show clear depth, so this is not an opening-class failure. | door leaf nearly coplanar with the wall | recess the leaf one frame-depth (≈ the window reveal) and add a sill/threshold step |

No P0 and no P1 found.

## 3. Source conformance checklist

| Item | Status | View(s) used and evidence |
|---|---|---|
| Silhouette (four monitors E–W, south-glazed, over a flat-roofed two-storey corner box) | **conforms** | front_corner.png x 240–1230, y 380–790 vs `src/oblique.jpg`; left_side.png x 370–1075, y 400–660 vs `src/front.png` x 0–530: three west gables + tooth 4 over the box's north bay, terrace over the corner bay; top.png x 325–1115, y 255–815: four teeth + terrace, same order as `src/top.jpg` |
| Storey count | **conforms** | front.png y 455–630 (two storeys + clerestory above); left_side.png two rows of windows per shed bay; `src/front.png` identical |
| Bay rhythm — south face | **conforms** | front.png columns at x 268/410/568/722/875/1028/1178 = 6 bays; `src/top.jpg` x 205–1000 = 6 bays; corner-bay ground-floor window, roll-up in bay 2, door + window bay 3, roll-ups bays 4–5, window bay 6 matches `src/front.png` sequence |
| Bay rhythm — west face | **conforms** | left_side.png columns at x 756/878/1067: window bay (under tooth 4) + X bay (under terrace); `src/oblique.jpg` x 300/440/640 same two-bay arrangement with tooth 4 over the window bay |
| Entrance and canopy | **conforms** | entrance_corner.png: double glazed door x 280–350 whole within the north bay (columns x 216 and 425), thin canopy spanning both box bays to the corner column x 930 with three tie-rods up to the floor beam; canopy ends at the corner (no wrap: front.png corner bay x 268–410 has no canopy). left_side.png x 760–1090, y 440–465 canopy starts at the north column, matching `src/front.png` x 230–520 |
| Dock | **conforms** | dock_contact.png: raised platform x 0–1440, y 540–700 with yellow edge, roll-up doors with recessed panels, person door, window; canopy over it from column 2 to the east end (front.png x 410–1190) as in `src/top.jpg` x 330–1010 |
| Ramp and stairs | **conforms** | front.png ramp x 265→568 against columns 268/410/568 = 2.0 bays; top.png ramp x 329→456 open then under canopy to ≈585; mid stair front.png x 680–720, east stair x 1150–1180; `src/top.jpg` ramp ≈ 2.3 bays with stairs at x 545–580 and 800–835 |
| Portal frame and braces | **conforms** | front.png: X in bay 1 (x 268–410) and bay 6 (x 1028–1178), single full-bay "\" rods in bays 2–5; west face X in corner bay only (entrance_corner x 440–930, y 0–420, confined above the floor beam at y ≈ 305–345); matches `src/front.png` (X corner, "\" rods in canopy bays) and `src/top.jpg` (X at both ends) |
| Monitors and clerestories | **conforms** (row count P2 #3) | front_corner.png x 300–1060, y 390–470 four south-facing glazed bands, roofs sloping north; sawtooth_contact.png gables high at south; clerestory_close.png mullions with depth |
| Terrace and rooftop plant | **conforms** | terrace_roof.png: rail on the parapet all round, unit with fan + duct elbow at the west end (`src/top.jpg` x 330–480, y 430–530 same position); terrace spans corner-bay depth only, tooth 4 clerestory forms its north edge, as in `src/front.png` x 740–1100, y 60–290 |
| Gable ends (east, north) | **not visible** in any source; coherent | right_side.png / rear.png / rear_side.png: solid charcoal gables with window pairs per bay, north wall 6 bays + door, ladder on the box; grammar matches the visible west face (P2 #8 noted) |
| Materials hierarchy | **conforms** | light galvanised frame, charcoal vertical cladding, light concrete ground storey on the south face and plinth on the shed, dark frames, dark canopies, yellow kerb — same palette roles as `src/front.png`; no textures expected in clay |

## 4. Camera validity

All 18 views are valid: target visible, asset not clipped, legible.

- Whole-envelope views (front, front_corner, aerial, top, left_side, right_side, rear, rear_side): the building occupies 55–65 % of the frame width, nothing clipped, all edges inside the frame.
- front.png x 215–265, y 515–585: the tree overlaps the SW corner column by a few pixels; negligible.
- left_side.png x 740–830, y 525–600: tree partially hides the entrance-canopy start (P2 #7); the entrance itself and both bays remain legible, and entrance_corner/front_corner show the detail unobstructed, so the view is not invalid.
- interior.png and stairs.png are dark but the stair, void edge, desks and the corner-bay glazing are all readable.
- No view shows a see-through hole, a floating part or an intersecting part.

## 5. Previous-version findings — status in the v009 pixels

### v008 independent review (0 P0, 3 P1)

| v008 finding | Status | Pixel evidence |
|---|---|---|
| P1 — dock ramp one bay long (~1:5) where sources show 2–2.5 bays | **Resolved** | front.png: ramp from x 265 (grade) to x 568 (dock level) spanning bays 1 and 2 (columns 268/410/568) = 2.0 bays; facade_close.png x 450–1200, y 650–1050 shallow continuous slope; top.png x 329→456 visible, continuing under the canopy. Within the brief's 2–2.5-bay band. |
| P1 — see-through hole at the terrace SW corner where the parapet rail beams missed the column cap | **Resolved** | terrace_roof.png x 300–750, y 650–1080: both parapet beams meet at a solid corner cap, the rail post stands on it, no background shows through; front_corner.png x 580–640, y 500–560 and aerial.png x 270–300, y 430–470 show a closed corner from the other sides. |
| P1 — canopy-bay rods were perpendicular hangers instead of in-plane full-bay diagonals | **Resolved** | architecture_close.png x 320–1110, y 390–720: one straight in-plane diagonal from the top of the left column to the base of the right column; front.png bays 2–5 all "\" full-bay diagonals in the same direction as `src/front.png` x 690–1000, y 230–440 and `src/oblique.jpg` x 740–1050. Section thickness remains a P2 (#1). |

### v007 finding carried in the brief

| Finding | Status | Pixel evidence |
|---|---|---|
| West face two bays, entrance under the gable (resolved in v008) | **Still resolved** | left_side.png columns x 756/878/1067; entrance_corner.png: door x 280–350 in the north bay, tooth 4 gable above it, X in the corner bay. |

### v002 findings named in the brief (builder claims fixed)

| v002 finding | Status | Pixel evidence |
|---|---|---|
| Braces piercing the canopy | **Resolved** | architecture_close.png: rods terminate at the column/floor-beam junction above the canopy slab (y ≈ 700); facade_close.png x 0–720, y 0–470: X confined to the upper storey; entrance_corner.png: X ends at y ≈ 305–345 at the corner column, only the thin canopy tie-rod (x 828–930, y 345–461) touches the canopy, which matches the source's rod detail. |
| Door split by a column | **Resolved** | entrance_corner.png: the double door (x 280–350, y 515–720) sits wholly between columns x 216 and 425. |
| One-bay west face | **Resolved** | see v007 row. |
| Wrap-around canopy | **Resolved** | entrance canopy ends at the corner column (entrance_corner.png x 930; front_corner.png x 575–590); the south-face corner bay (front.png x 268–410, y 455–630) carries no canopy; the dock canopy begins at column 2 (x 410). |
| X-braces in every bay | **Resolved** | front.png: X only in bays 1 and 6; rods in bays 2–5; west face X only in the corner bay. |
