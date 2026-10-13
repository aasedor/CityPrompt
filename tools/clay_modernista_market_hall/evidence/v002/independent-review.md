# Independent holistic review: clay-modernista-market-hall v002 (RLASM v6.1)

Reviewer: independent; judged only rendered pixels against the locked sources (`sources/front.png`, `sources/oblique.jpg`, `sources/top.jpg`). All 18 renders and the 4 phone boards were opened at full resolution, and the regions in question were cropped and zoomed. Builder notes, metadata and counts were not accepted as proof.

## 1. Verdict

**Verdict: VISUAL_REWORK_REQUIRED.** The gable arch, lantern, gablets, dado and front framing are now fixed in the pixels. However, every wing roof carries arched exterior ribs that float off the flat roof plates, pure-black faces show at all four ridge-monitor ends, the quadrant roofs are still opaque low hips without the source's glazed pyramids, and the interior is still an opaque soffit with no trusses.

Counts: P0 = 1, P1 = 3, P2 = 9

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P0 | architecture_close, lantern_roofs, rear_court, rear_side, front_corner, aerial, plaza_awnings, aisle_arcade, left/right_side, rear | Every wing roof face carries 4–6 segmented, semicircular dark iron ribs that do not lie on the flat pitched roof plate. Each rib bows away from the plate and casts a detached shadow on it. The lower ends taper to points at the eave gutter. The upper ends stop bluntly in mid-air above the plate, short of the ridge monitor (zoom of architecture_close top-left). This is the v001 "semicircular hoop on a pointed gable" defect moved from the gable onto the roof field. It is a floating contact defect repeated across all 8 wing roof faces, and it makes the wings read as curved greenhouse vaults. The source wings are straight-pitched, standing-seam metal roofs with no exterior ribs (front, oblique, top). | The bay "trusses" were built as semicircular arcs with the archivolt radius and placed outside the roof skin, instead of as triangular or king-post trusses under the pitched plane | Remove the exterior ribs. Model the trusses inside the roof as straight-rafter trusses that follow the roof pitch, sitting under the plate and bearing on the column line. If exterior expression is wanted, use flat standing-seam battens lying in the roof plane. |
| 2 | P1 | lantern_roofs, front_corner, aerial, rear_side, rear_court, crest_contact | At the outer end of each of the four glazed ridge monitors there is a triangular face rendered pure black (sampled RGB 0,0,0). Thick pure-black seams also run along each wing ridge from the monitor out to the gable apex, and in crest_contact a black slab sits behind the cresting. Nothing else in the lit scene is pure black. | Inverted normals, a zero-thickness or non-manifold end cap, or an open slot along the ridge between the two roof plates (if it is open, this becomes an envelope P0) | Close each monitor end with a correctly oriented hipped or gabled glazed cap. Cap the ridge with a solid ridge roll joining both plates. Recalculate normals and re-render, then confirm no pixel in the roof region is 0,0,0. |
| 3 | P1 | front_corner, aerial, architecture_close, top, rear_side, lantern_roofs | The four corner-quadrant roofs are low, opaque tan hips, each with only two small rectangular skylights. The source oblique shows the front quadrant as a steep, mostly glazed pyramid with coloured (green/blue) panes. The source top shows every quadrant with large diagonal glazed and stained-glass triangles. The v001 "quadrant glazing" finding is only cosmetically addressed. | The quadrant roof was kept as a generic low hip with token skylight cut-outs | Raise the quadrant roofs to the source pitch (about the oblique's steep pyramid). Glaze most of each pyramid as triangular panels with iron glazing bars and a few coloured panes, following the diagonal-hip layout in the top source. Keep the eave gablets. |
| 4 | P1 | interior | The interior ceiling is a continuous opaque dark-brown soffit. No bay trusses are visible anywhere. The ridge-monitor and lantern well overhead is dark brown (sampled about RGB 47–64), not daylit. The only light comes from a few small rectangular patches. This contradicts the glazed lantern drum, glazed monitors and glazed strips shown outside. The v001 finding (opaque interior roof without trusses) is not resolved. | Roof plates are single-sided opaque solids, glazing cut-outs do not pass through the inner face, and the "trusses" exist only as the exterior ribs of finding 1 | Make the glazed strips, monitors and lantern drum glazing pass through to the interior. Add exposed iron trusses (see finding 1) at every bay under the roof plane. Re-render interior and confirm the lantern well reads as bright glazing. |
| 5 | P2 | great_arch, crest_contact, front | The coat of arms is a small yellow hexagonal plaque with two red stripes, tucked under the finial. The source shield is a prominent pointed shield with red/yellow pales and an ornamental surround in the gable field. | Placeholder-level shield geometry | Enlarge the shield to a pointed heater shield about 1/6 of the gable height with a simple raised surround. |
| 6 | P2 | crest_contact, great_arch | The rake cresting reads as a handrail: vertical posts with cylinder knobs on a rail, not openwork iron cresting. The wheel finial is acceptable as a rose. | Railing primitive reused as cresting | Replace with a pierced cresting band of fleur and scroll cut-outs. |
| 7 | P2 | front, great_arch, facade_close | The tympanum is stained glass, but in a regular sunburst fan. The source is an irregular mosaic with a large roundel rose, and its archivolt and spandrels carry blue roundel medallions. The render has small gold octagon bosses instead. | Simplified pattern | Add 10–14 blue roundel medallions around the archivolt band and in the spandrels, and break the fan into a mosaic. |
| 8 | P2 | glass_close, aisle_arcade, plaza_awnings, architecture_close | Each awning valance carries a pure-black stripe (RGB 1,1,1). The awnings are thick, near-flat boxes rather than sloped canvas on visible arms. | Black material or back face on the valance underside; box primitive | Use a dark-colour valance hem (not pure black). Pitch the awning plane about 20°, thin it, and add two drop arms. |
| 9 | P2 | aisle_arcade, plaza_awnings, front | The dado is a plain ochre/timber-toned band with no tile panelling and no stone posts between bays. The source shows patterned tile panels between stone pedestals. | Single box | Add stone pedestals at each column, with recessed tile panels in two source tones between them. |
| 10 | P2 | front, left_side, right_side, rear | The building fills only about 55% of the width and about 35% of the height. Half the frame is empty ground. Not clipped, and legible. | Camera widened to fix v001 clipping, then overshot | Tighten to about 75–80% width, keeping a margin for the awnings. |
| 11 | P2 | top, aerial, plaza_awnings | The plaza is a uniform light grey slab with no paving joint grid or kerb. | Untreated ground | Add a paving grid with a kerb edge in the same palette. |
| 12 | P2 | left_side, right_side, rear, rear_court | The north, east and west tympana use blue-only glass while the south is full colour. This is coherent but monotone. | Different material set | Optional: carry two or three accent colours into the secondary tympana. |
| 13 | P2 | front, interior | The main entrance opening is a flat glazed screen with an unframed rectangular void. The source has a deep iron portal frame within the piers. | Thin screen | Add a portal frame with returns about 0.3 m deep. |

## 3. Source conformance checklist

| Item | Status | View used | Note |
|---|---|---|---|
| Silhouette | conforms | front, left_side, rear_side vs source front/oblique | Single storey, cross of gabled wings, raised central lantern, lower aisles. |
| Roof pinwheel and lantern | deviates | front_corner, aerial, top, lantern_roofs vs oblique/top | The cross plan and the steep glazed lantern on a glazed drum conform. The wing roof faces deviate: floating arched ribs (F1) and black monitor ends and ridge seams (F2). |
| Great arch: archivolt | conforms | great_arch, crest_contact, left_side | The archivolt now sits inside the pointed gable and meets the piers. Nothing protrudes past the rakes. |
| Great arch: tympanum | conforms (P2 pattern) | great_arch, facade_close | Reads as stained glass set behind tracery, with depth. Fan pattern instead of mosaic/roundels (F7). |
| Great arch: crest and coat of arms | deviates (P2) | crest_contact | Wheel/rose finial present. Shield undersized (F5). Cresting reads as a rail (F6). |
| Great arch: piers | conforms | great_arch, front | Stone piers with plinth and panel. |
| Aisle walls: dado | conforms (P2 finish) | aisle_arcade | Ochre, no longer teal. Plain band (F9). |
| Aisle walls: cast-iron columns | conforms | aisle_arcade, architecture_close | Round columns with branching brackets. |
| Aisle walls: glazing | conforms | glass_close, aisle_arcade | Mullioned glazing with interior visible through it. |
| Awnings | conforms (P2 finish) | top, architecture_close, plaza_awnings | Red/yellow/blue over every quadrant bay. Black valance stripe and boxy form (F8). |
| Gablets | conforms | architecture_close, aisle_arcade | Closed double-pitch gablets along the quadrant eaves. |
| Quadrant roofs | deviates | front_corner, top, architecture_close vs oblique/top | Opaque low hips with two token skylights, not glazed stained pyramids (F3). |
| Clerestories | conforms | architecture_close, lantern_roofs | Louvred clerestory band between aisle roof and wing eave. Glazed ridge monitors present. |
| Entrance | conforms (P2) | great_arch, front | Entrance between stone piers, with stalls visible inside. Shallow portal (F13). |
| Interior | deviates | interior | Stalls present. Opaque dark soffit, no trusses, unlit lantern well (F4). |
| Plaza | conforms (P2) | aerial, top | Plaza slab with bollards, lamps and trees. No paving (F11). |
| Materials hierarchy | deviates | lantern_roofs, glass_close | Stone, iron, glass and canvas hierarchy readable. Pure-black unlit faces break the clay palette (F2, F8). |

## 4. Camera validity

- No view has its target occluded or the asset clipped. Every target is legible.
- front, left_side, right_side, rear: valid, but loosely framed. The building fills about 35% of the frame height (F10, P2).
- glass_close: valid. The camera looks through the glazing behind two awnings, and the column, glazing bars and interior are legible.
- interior: valid. The ceiling is legible enough to show finding F4.
- top: valid near-nadir with mild perspective, comparable to the top source.

## 5. Previous-version (v001) findings: resolved in the pixels?

| v001 finding | Status in v002 pixels | Evidence |
|---|---|---|
| P0: iron arch hoop above and outside a pointed gable | **Resolved at the gable; recurs on the roof field** | great_arch and crest_contact: the archivolt is inside the rakes, under the coping. The same semicircular-hoop error now appears as floating exterior ribs on every wing roof (new P0, F1). |
| P0: open valleys at the lantern base showing the interior | **Resolved** (new related P1) | lantern_roofs and rear_side: the valleys under the lantern drum are closed grey surfaces. New pure-black faces and seams at the monitor ends and ridges (F2). |
| P1: tympanum not stained glass | **Resolved** | facade_close and great_arch: coloured panes set behind iron tracery. Pattern simplified (P2, F7). |
| P1: crest and coat of arms placeholders | **Partly resolved** (now P2) | crest_contact: rose finial present. Shield small and cresting rail-like (F5, F6). |
| P1: roofs read as flat glass without clerestories or quadrant glazing | **Partly resolved** | Clerestories and glazed ridge monitors are present (architecture_close). Quadrant glazing is still only two token skylights (F3, P1). |
| P1: low opaque lantern pyramid | **Resolved** | left_side, lantern_roofs: tall glazed drum with a steep glazed pyramid and finial. |
| P1: gablet roofs as single slabs | **Resolved** | architecture_close: closed double-pitch gablets. |
| P1: teal dado | **Resolved** | aisle_arcade: ochre/timber-tone dado. |
| P1: opaque interior roof without trusses | **Not resolved** | interior: opaque dark soffit, no trusses, dark lantern well (F4). |
| P1: front camera clipping the awnings | **Resolved** (overshot to loose framing, P2) | front: all awnings inside the frame. Building small in frame (F10). |
