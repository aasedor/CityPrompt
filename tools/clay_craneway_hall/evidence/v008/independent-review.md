# Independent holistic review - crane-way hall, v008 (RLASM v6.1 architectural clay)

Reviewer: independent; judged only rendered pixels (renders/*.png, boards/*.png) against the locked sources (sources/front.png, oblique.jpg, top.jpg). No source code, build reports or builder notes were consulted.

## 1. Verdict

**VISUAL_REWORK_REQUIRED** - v008 fixes both v007 monitor findings (the monitors are now long, low and glazed, with one row of three on each roof level), but the two aisle monitor rows face the wrong way, the hood knee-braces float, and the aisle windows have no reveal.

Counts: P0 = 0, P1 = 3, P2 = 6

## 2. Findings

| # | severity | view(s) with pixel regions | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | top.png aisle rows at x 410-1030, y 380-435 (north) and y 640-700 (south); architecture_close.png monitor at x 540-1220, y 380-590; monitor_close.png x 365-1055, y 370-700; aerial.png x 400-500 / 575-680 / 775-895, y 460-615; vs oblique.jpg x 690-1080, y 400-590 and top.jpg x 660-920, y 550-730 | Every aisle-roof monitor is built like the nave ones: the ridge runs along the hall and the glazed band runs on the long north and south sides. In both oblique sources, the aisle monitors are short boxes turned 90 degrees. Their ridge runs across the hall. The corrugated roof planes slope to the west and east. The glazed band sits under the west-facing eave. The solid gable triangles face the nave wall and the aisle eave. Only the nave-ridge row runs along the hall in the sources. As a result the aisle roofscape reads as a different rhythm (three parallel strips of the same lanterns), not the source's crossed aisle lanterns against the long nave lanterns. | The single 10 x 4.4 m longitudinal monitor module was applied to all three roof levels. | Keep the nave row as built. Rotate the six aisle monitors 90 degrees about vertical: ridge across the hall, about 7-8 m along the hall x 4-5 m deep. Put the glazed band under the eave on the west and east faces, and make the gable triangles solid, facing the nave wall and the aisle eave. Place the outer gable about 1 m back from the aisle parapet. Re-render top, aerial, front_corner, architecture_close and monitor_close. |
| 2 | P1 | side_doors.png x 465-505, y 105-265; x 975-1035, y 175-305; x 1355-1425, y 225-325; facade_close.png x 355-390, y 340-460; x 795-840, y 370-470; x 1135-1185, y 390-480; glass_close.png x 870-900, y 0-50; yard_sidings.png at every lattice column top | At every lattice column, a slanted knee-brace bar drops from the walkway soffit. It ends in mid-air in front of the X-bracing, below the X node, without meeting a member (zoom: the end hangs about 0.3 m in front of the cross with no connection). It repeats in every bay along both long walls, so it reads as stray sticks clipping through the lattice. | The brace was given a fixed length and angle that do not land on the column. It was probably meant to support the walkway or cantilever and was left unattached after the column or lattice depth changed. | Either remove the braces, or re-run each one from the walkway soffit edge to the outer face of its lattice column chord at the first horizontal (about 1.2-1.5 m below the soffit), in the column plane, so both ends make contact. Check facade_close, side_doors and stair_contact. |
| 3 | P1 | glass_close.png left window x 80-645, y 595-905 and right window x 1060-1440, y 590-860; facade_close.png windows x 455-690 / 870-1045 / 1190-1325, y 690-880; side_doors.png x 0-315, y 610-800 | The hooded aisle windows sit flush. The dark frame lies in the cladding plane, with no jamb, head or sill return and no shadow line under the hood, even in glass_close, the detail camera for this, which looks at an angle. The windows read as flat dark rectangles pasted on the wall. The sources (front.png x 140-310, y 540-610) show windows set back in the bays between the lattice columns, with a visible sill and reveal. The roller door in side_doors (x 850, y 560-800) shows a reveal, so it is only the windows. | The window frame and glass were placed on the wall face, not in a cut opening with depth. | Cut each opening through the cladding and recess the frame and glass 150-250 mm. Add 4 returns (jambs, head, sill) in the cladding colour, plus a thin projecting sill (about 50 mm). Re-render glass_close and facade_close and confirm a visible return and shadow. |
| 4 | P2 | crane_interior.png x 420-1070, y 480-560; gable_mouth.png x 880-1085, y 370-420 | The overhead crane reads as a plain dark slab with a small orange block. There is no hook block, no hanging rope and no railing walkway, where the sources (front.png x 700-1000, y 250-330; oblique.jpg x 290-560, y 490-580) show a girder with a railing and a yellow hook. | Simplified crane massing. | Add a hook block with a rope drop (yellow, source palette) under the trolley, and a light railing on the bridge girder. |
| 5 | P2 | gable_mouth.png x 515-990, y 560-950; left_side.png x 620-820, y 585-715 | The green sliding doors are three flush leaves in one plane, filling the full lower storey. There is no top track or header, no gap or open leaf, and no clad band above. The sources show leaves on a top rail, with a dark open slot between leaves and a clad band over them. | Doors modelled as one subdivided panel. | Offset the leaves 100-150 mm in depth, add a top rail, and open one leaf about 1 m to show a dark slot. |
| 6 | P2 | interior.png x 260-1180, y 0-430 | The ceiling is a flat dark plane with faint monitor outlines. The monitors do not open into the interior, and there are no visible roof trusses, while the gable truss is visible from outside. | The monitor openings were not cut through the roof. The interior roof is a closed shell. | Cut the roof under each monitor, or at least show truss chords under the ceiling. |
| 7 | P2 | stair_contact.png x 1100-1210, y 640-700 | The intermediate stair landing sits directly on top of a window hood. It touches visually, but the support is ambiguous. | Landing height clashes with the hood height. | Raise or lower the landing clear of the hood, or shorten that hood. |
| 8 | P2 | front.png, rear.png, left_side.png, right_side.png | The whole-envelope elevation cameras frame the building at about 60% of the width and 20-30% of the height, with large empty sky and ground. It is legible but small. | Conservative camera distance. | Tighten the elevation framing to about 80% of the width. |
| 9 | P2 | top.png; aerial.png | All three monitor rows sit in the same three bays. The sources stagger the aisle lanterns slightly against the nave lanterns. Low confidence; this falls away with finding 1 if the aisle monitors are re-placed. | Shared x positions. | Offset the aisle rows by half a bay to match top.jpg once they are rotated. |

## 3. Source conformance checklist

| Item | Status | View(s) used |
|---|---|---|
| Silhouette (stepped nave over lower aisles, gabled) | conforms | left_side, right_side, front_corner vs oblique |
| Section (tall nave, two lean-to aisles, clerestory over aisle roofs) | conforms | left_side, rear_side, architecture_close vs oblique/top |
| Bay rhythm and bracing (lattice X-braced columns between hooded windows) | conforms in rhythm; deviates in detail (floating knee braces, F2; flush windows, F3) | front, facade_close, side_doors, yard_sidings vs front.png |
| Gable mouth and doors (open steel upper frame, green sliding doors below) | conforms, with P2 door simplification (F5) | left_side, gable_mouth, crane_interior vs front.png / oblique |
| Monitors and clerestory | clerestory conforms; nave monitor row conforms; aisle monitor rows deviate (orientation, F1) | top, aerial, architecture_close, monitor_close, rear vs oblique/top |
| Crane and interior | crane present but simplified (F4); interior coherent but flat ceiling (F6) | crane_interior, gable_mouth, interior |
| External stair (SW corner) | conforms (position and flights reach the ground and the walkway); P2 landing/hood clash | stair_contact, front, front_corner |
| Yard and sidings (concrete apron, two sidings, boxcar on north side) | conforms | top, yard_sidings, rear, rear_side, aerial |
| Materials hierarchy (light clay cladding, darker glazing and frames, green doors, rust boxcar) | conforms | all whole-envelope views |
| East gable (not shown in any source) | coherent (solid gable, roller door, small windows) | right_side, rear_side, aerial |

## 4. Camera validity

No view has its target hidden, clipped or unreadable. front, rear, left_side and right_side are small in the frame but readable (P2, F8). monitor_close is now correctly aimed at a south-aisle monitor with the nave clerestory behind it. glass_close, side_doors and stair_contact all show their subjects.

## 5. Previous-version (v007) findings - checked in the v008 pixels

| v007 finding | Status in v008 pixels |
|---|---|
| P1: monitors square in plan, reading as tall boxes with blank cheeks | **Resolved.** The monitors are now long, low gabled boxes with a continuous glazed band under the eave on both long sides (south side: architecture_close x 700-1200, y 495-560; north side: rear.png y 430-440) and solid gable ends (architecture_close x 545-700). The new P1 in finding 1 is separate: the aisle rows face the wrong way. |
| P1: all nine monitors on the nave in a staggered pattern | **Resolved.** top.png shows one row of three on the north aisle (y 380-435), three on the nave ridge (y 515-560) and three on the south aisle (y 640-700). |
| Aisle-roof finding (verified resolved in v007) | Still resolved: lean-to aisle roofs are present on both sides (left_side, top). |
| West aisle-end finding (verified resolved in v007) | Still resolved: the aisle ends show an open braced upper frame over a clad lower wall (left_side x 440-575 and x 860-1000). |
| The six v007 P2s | The brief does not name them, so they cannot be checked one by one. The open P2s seen in v008 are listed above. |
