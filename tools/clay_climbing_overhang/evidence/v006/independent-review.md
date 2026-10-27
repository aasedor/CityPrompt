# Independent holistic review: The Overhang, v006 (RLASM v6.1 architectural clay)

Reviewer: independent; did not build this candidate. Basis: the rendered pixels of all 18 renders, each opened at full resolution, compared with the three locked sources (`sources/front.png`, `sources/oblique.jpg`, `sources/top.jpg`). I also made zoomed crops of matched regions. I did not accept the builder's metadata, ratios or notes as proof. Where I cite a number, I measured it myself on the pixels.

## 1. Verdict

**VISUAL_REWORK_REQUIRED**: there are no P0 defects, but five clearly visible P1 defects block production-quality approval:

- the climbing shell tapers to a point instead of standing on a broad foot;
- the west front has 13 bays where the source has 11;
- the open top does not show the inner box or the crash-mat floor;
- lamp posts stand inside the grass planters;
- the grass planters read as green lawn instead of dense straw-coloured grass masses.

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | front, front_corner, right_side, aerial (vs source front, oblique) | The climbing shell narrows to a sharp point where it meets the plaza and reads as an inverted cone or horn. In both sources the shell stands on a broad base: the bottom edge of the south face sits nearly flat on the granite for a long stretch east of the doors, then rises gently to a low east corner. In the render the underside starts rising immediately from a foot only a few pixels wide. Relative to the facade baseline, the render's underside rises about twice as steeply (≈0.37 against ≈0.19 in the source front). The lower west face reads as one slanted facet, where the source shows a broad, nearly vertical flared face. | The foot polygon was kept compact (about 3.2 m) and the lowest east vertex sits well above the plaza, so the faces converge too fast toward the ground. | Widen the foot along the facade to about 0.3× the rim width. Drop the lower east corner of the south face to about z = 0–1.5 m so the bottom edge runs low and nearly level before the east edge rises. Make the lower west face a near-vertical flared plane. Then re-check the silhouettes in front and front_corner against the sources. |
| 2 | P1 | front, front_corner, left_side, facade_close (vs source front, oblique) | The rhythm of the west front is wrong. I count 13 window bays (14 piers) on each upper storey; the source shows 11 bays (12 fins) between the north end and the frame-box corner, in both the front and oblique views. In the oblique render views the windows read as narrow slots between broad, deep piers, where the source glass takes about half or more of each bay. | The bay module is too small (about 2.8 m against about 3.3 m), and the fins are deeper and wider than in the source. | Rebuild the west front at 11 bays over the same length. Thin the fin faces and reduce their projection so the glazing takes about 55–60 % of each bay in the oblique view. Keep the spandrel bands and the recessed ground floor aligned to the new module. |
| 3 | P1 | top, rim_interior (vs source top) | Inside the open top, the inner walls twist into a converging funnel with a diagonal ridge, and only a thin dark sliver shows along the west inner wall. The source top shows a thick-walled rectangular box: four inner walls running parallel to the rim, white holds on the inner north and south walls, and a large dark rectangular floor (crash mat) about 45 % of the opening wide at the bottom. No crash mat can be made out in any render. | The inner surface is an offset of the twisted outer faces, not its own box with a floor. The floor sits too deep or is hidden by converging walls. | Model the inner shell as a box whose walls are near vertical or slope slightly inward, parallel to the rim. Add a flat dark crash-mat floor that can be seen from above. Re-render top and rim_interior. |
| 4 | P1 | front, front_corner, aerial (vs source front, oblique) | In both plaza planters a black lamp post rises out of the middle of the grass bed. In the source, lamp posts stand on the paving and the sidewalk, outside the planters. | Lamp positions were placed without checking the planter footprints. | Move the lamp posts onto the paving or sidewalk at the source positions (by the SE corner and along the south sidewalk), and keep the planter beds clear. |
| 5 | P1 | front, front_corner, aerial, rim_interior, top (vs source front, oblique, top) | Both plaza planters read as bright green lawn with thin, scattered straw tufts. In the source the beds are completely filled by dense, tall, straw-coloured grass masses, with no green ground showing. | A green turf ground plane under a sparse instanced grass. | Raise the grass density and height until the bed reads as a continuous straw mass. Change the bed ground to a dark mulch or straw tone, not green. |
| 6 | P2 | rim_interior, top, front | The rim fascia is only slightly lighter than the shell body. In the source top it is a clearly pale, cream timber frame. | The fascia colour is too close to the body colour. | Lighten the fascia to a pale cream timber, roughly RGB 200,170,140. |
| 7 | P2 | front, front_corner, climbing_face | The three climbers are bunched near the east edge of the south face. In the source, one climber is high near the middle of the face and two are lower and slightly right. Hands and feet do land on holds. | Climber anchors were placed on the densest hold field. | Move the climbers to the source positions at about 35–55 % of the face width. |
| 8 | P2 | plaza_planters, right_side | A pure-black wedge sits under the soffit between the shell foot and the white wall. It reads as a void, not as shade. | No bounce light reaches the gap; it may also be a real gap between the shell and the wall. | Close the gap, or add an ambient or bounce term so the area reads as dark grey shade. |
| 9 | P2 | front, front_corner, aerial (vs source front, oblique) | The source plaza steps down to the south and east sidewalks with handrails at the planter edges. The render plaza is flat, with no steps. The paving is broad two-tone E–W stripes, where the source has smaller mixed granite modules with a dark accent band. | Plaza simplified. | Add two or three risers with handrails along the south and SE edges, and an optional finer paving module. |
| 10 | P2 | front (vs source front, oblique) | The solid north part of the penthouse's west face has no door. The source shows a dark door there. The render's door is on the north end face instead. | Door placed on the wrong face. | Add a door to the solid west wall of the penthouse, north of the glazing. |
| 11 | P2 | front, front_corner, top, rear_side | The roof garden reads as a green lawn with sparse grass. The source shows yellow-green grasses and shrubs in raised planters. | Same turf treatment as finding 5. | Use denser yellow-green grasses and shrubs, and a planter-bed ground that is not lawn. |
| 12 | P2 | boards/phone-01 | The board pairs the locked top with the aerial render instead of the top render, so it is not a role-matched comparison. | Board layout. | Put the top render next to the locked top on the board. |
| 13 | P2 | all | The whole-envelope renders (front, front_corner, aerial, top, sides, rear) have older file times than the detail renders. I checked the pixels: climbers, holds, pool and rim match across the two sets, so I do not raise this as a provenance defect. | Partial re-render. | Re-render all 18 views from the same final GLB in one pass before the next review. |

P0: none. P1: 5. P2: 8.

## 3. Source conformance checklist

| item | status | view(s) used |
|---|---|---|
| Silhouette and storey count: three-storey pool block | conforms | front, left_side, front_corner |
| Penthouse, one storey on the middle of the roof | conforms | front, rear, top |
| Four-storey east block | conforms | aerial, right_side, rear |
| Plan (top view): about 39 × 36 m corner block, pool block W, penthouse middle, east block E, shell straddling the south front | conforms (shell rim slightly narrower relative to the building: about 0.42 of the image width against 0.52; position correct) | top vs source top |
| Climbing shell: foot on the plaza east of the doors | deviates: the foot is a point, not a broad base (finding 1) | front, front_corner, wall_base_contact |
| Climbing shell: lean east and cantilever over the plaza | conforms (rim projects about 7–8 m beyond the facade, leaning east) | top, front_corner, right_side |
| Climbing shell: folded faces, west faces meeting the pool-block parapet at a fold | conforms (horizontal fold at parapet level, frame-box jamb trimmed along the shell face as in the source) | front_corner, architecture_close |
| Climbing shell: level open rim | conforms | front, front_corner, rim_interior |
| Climbing shell: light timber fascia | deviates, weakly lighter (finding 6) | rim_interior, top |
| Climbing shell: contact with the plaza | conforms (flush, no float) | wall_base_contact, right_side |
| Climbing shell: contact with the facade | conforms; black wedge noted (finding 8) | architecture_close, entrance, plaza_planters |
| Holds: dark and white, densest on the south face | conforms | front, climbing_face, rim_interior |
| Climbers: three on the south face | conforms in count; placement deviates (finding 7) | front, climbing_face |
| Open top and inner walls | deviates: twisted funnel, no legible crash mat (finding 3) | top, rim_interior |
| West front rhythm: fins, spandrels, recessed windows, glazed ground floor behind columns | deviates in bay count and window-to-pier ratio (finding 2); the elements themselves conform | left_side, front, facade_close |
| South frame box and two-storey glass ribbons | conforms | front, architecture_close, glass_close |
| Entrance doors: two pairs in recessed ground-floor glazing | conforms | entrance, interior |
| Parapet band: deep, white | conforms | left_side, architecture_close |
| Pool deck: infinity pool N–S along the west edge | conforms (aspect about 2.36 against about 2.3) | top, front |
| Pool deck: glass weir and trough | conforms (glass weir line and trough visible at the west parapet) | front (zoomed) |
| Pool deck: glass balustrades | conforms | left_side, pool_deck, architecture_close |
| Pool deck: loungers in a row along the east edge, plus a row at the north | conforms | top, pool_deck |
| Roof garden: raised planters, grasses, small yellow-green trees at the north end | conforms in layout; planting reads as lawn (finding 11) | top, front, rear_side |
| Penthouse: glazing to the pool deck at its south end | conforms | front, rear_side, pool_deck |
| Penthouse: solid end with a door | partly conforms: door on the north face, none on the solid west face (finding 10) | rear, front |
| Penthouse: roof air-handling unit and fan | conforms | top, front_corner |
| East block roof: membrane, two skylights, small plant | conforms | top, aerial |
| White facade under the overhang | conforms | right_side, climbing_face, plaza_planters |
| Plaza: two-tone paving bands | conforms (simplified module, finding 9) | front_corner, wall_base_contact |
| Plaza: grass planters | deviates (findings 4 and 5) | front_corner, aerial, plaza_planters |
| Plaza: bollards | conforms (present at the south and SE edges) | right_side, aerial |
| Plaza: lamp posts | deviates: two stand inside planters (finding 4) | front, front_corner |
| Plaza: steps and handrails | not modelled (finding 9) | front_corner |
| Low planted strip along the east edge | conforms | front_corner, rim_interior, right_side |
| Sidewalks: concrete west sidewalk | conforms | left_side, front |
| Street trees in pits | conforms | left_side, front |
| Streets and crossings: west street, east street, crosswalks | conforms | top, aerial, front |
| Parked cars on the east street | conforms (simple massing) | right_side, top, front |
| Neighbours: brick mid-rise and residential blocks | conforms (simplified massing) | front, aerial, rear_side |
| Materials hierarchy: white precast, dark glass, honey timber shell, grey granite | conforms (measured shell median: hue 24, saturation 145–164, RGB about 190,143,79, against sunlit source hue 25–26; the shaded inner walls are oversaturated, which is noted but not raised) | front, front_corner, top |

## 4. Camera validity

All 18 views are valid. In every view the target is legible, unclipped and not occluded by anything that defeats the view's purpose:

- In left_side, street-tree canopies partly hide the ground floor, but the rhythm of the upper storeys and the parapet stay fully readable.
- pool_deck is taken at water level, so the west weir is hard to read there; the weir is legible in front.
- climbing_face, wall_base_contact and entrance crop the shell on purpose, as detail views.

No view fails.
