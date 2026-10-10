# Independent RLASM v6.1 holistic review — clay-brick-podium-condo-tower v002

Reviewer: independent (did not build). Evidence: all 18 renders, the three locked sources and the four phone boards opened at full resolution; regions enlarged 2x–8x where contact or alignment had to be confirmed. Builder notes, counts and hashes were not used as proof.

Orientation used throughout (derived from the pixels, not the notes): the three street trees sit along the south face; `front.png` looks north at the south face (east on the right); `right_side.png` looks west at the east face (south on the left); `left_side.png` looks east at the west face; `rear.png` looks south at the north face; `top.png` is north-up; `aerial.png` is the south-east (street) corner; `front_corner.png` is the south-west corner.

## 1. Verdict

**VISUAL_REWORK_REQUIRED** — the three v001 P0s and both v001 P1s are genuinely fixed in the pixels, but v002 introduces a new P0: the tower's east corner columns are carried down the podium's east face and slice through a second-storey ribbon window and a ground-floor storefront bay, which the sources never show.

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|----------|---------|--------------------------------|--------------|------------|
| 1 | **P0** | right_side (x≈490–505 and x≈855–870, y 770–950), aerial (SE corner, column through parapet/brick/canopy), corner_entry (column x≈695–775 with the east-face window's glazing continuing to its left at x≈580–695) | Two white tower corner columns run from the tower top straight down the podium's east brick face to grade. The SE column is centred in the first second-storey ribbon window (glazing visible on both sides, precast sill cut in two), passes through the dark canopy band and then bisects the first ground-floor storefront bay. The NE column covers the right jamb of the last window, cuts its sill, and lands on the storefront/pier junction. Sources (`front.png` right face of podium, `oblique.jpg` east face) show plain brick, storefronts and a garage door with no column lines on the podium. Reads as intersecting parts / wrong geometry on a street face. | Column assembly extruded to z=0 wherever the tower face is coplanar with the podium face (east only), with no check against the podium bay grid. | Terminate the four tower columns at the podium cornice/terrace slab (matches the sources), or, if continuous columns are kept, re-grid the east podium bays so each column lands on a full brick pier with the window and storefront modules shifted clear of the column width. Re-render right_side, aerial, corner_entry. |
| 2 | **P1** | corner_entry (near column base x≈695–775, y≈825–840; far column x≈1380–1440, y≈700–712) | Both east-face columns end on a hard-edged dark inverted wedge/cone at grade, wider than the column at the top and tapering below the pavement line; the adjacent brick pier and storefront meet the pavement cleanly with a light plinth. The entry-corner column therefore reads as standing on a dark footing or pushing through the pavement rather than landing on it. | Column primitive extends below the ground plane and a dark base/shadow-catcher primitive (or a pavement cut) is exposed; or an AO/contact element with geometric edges. | Clip the column at z=0 (or sit it on a light plinth matching the pier base), delete the dark wedge primitive / close the pavement, re-render corner_entry. Disappears automatically if finding 1 is fixed by stopping the columns at the cornice. |
| 3 | **P1** | front_corner | The view named for the front corner is taken from the south-west: the nearest corner shows the large west terrace, west storefronts and west canopy; the south street face (three trees) recedes to the right and the east street face with the flush tower edge is at the far side. The locked oblique is the south-east street corner. The SE corner is therefore documented only by the high `aerial.png`; there is no mid-height whole-envelope view of the identity corner (corner entry, flush tower edge, two street faces) to match the oblique. | Corner camera azimuth mirrored (SW instead of SE). | Rotate the front_corner camera ~90° about the building centre to the SE at the same elevation; keep aerial as the high match. |
| 4 | P2 | front, src front | South-face balcony rhythm: render is a checkerboard (stacks A/C/E on odd floors, B/D on even; ~5–6 slabs per stack), source shows every-floor zig-zag stacks (~11 slabs per stack) and slabs about two bays wide versus ~1.5 bays here. Count and stagger are now right; density and slab width are not. | Stagger implemented as alternate floors. | Place a slab on every floor and offset adjacent stacks horizontally; widen slabs. |
| 5 | P2 | top, aerial, front | Tower east face flush with the podium east edge; `top.jpg` and `oblique.jpg` show a narrow terrace strip on the east as well as the wide south one. | Tower footprint snapped to east edge. | Pull the tower ~1.5 m west; also removes the coplanar condition that produced finding 1. |
| 6 | P2 | roof_crown, top | Penthouse is a plain rectangular box with flat dark louvre panels; `top.jpg` shows a U-shaped screen enclosure with an open equipment yard and two volumes, `oblique.jpg` a stepped louvred box. Acceptable clay simplification; plan shape differs. | Single box primitive. | Optional: split into two offset boxes or notch the plan. |
| 7 | P2 | interior | Valid but almost featureless: three mullions, the balcony rail outside, a dark floor slab; no ceiling, wall return or slab edge to anchor scale. | Camera placed hard against the glass. | Pull the camera 2 m back into the unit so the ceiling and a side wall appear. |
| 8 | P2 | balcony_stack | Right 40% of frame is empty sky; the stack is legible but framing is wasteful. | Camera aim. | Pan ~10° left. |
| 9 | P2 | left_side, right_side, front | East-side tree cluster is three overlapping low-poly canopies at three heights, one canopy floating at second-storey level in front.png with its trunk hidden; the west face carries storefronts and a canopy although west is not a street. Entourage/coherence only. | Entourage placement; west face copied from south grammar. | Normalise tree heights; optional plain brick/service grammar on the west. |
| 10 | P2 | architecture_close, podium_retail, src front | Podium second storey is flat punched ribbon windows with sills; source shows deep-set glazing with inset rails. Seven south storefront bays versus ~5–6 plus a corner glass box in the source. Acceptable for clay. | Bay module. | Optional bay re-count. |

### Verification of the v001 findings (each checked in the pixels)

- v001 P0 "curtain wall stopping above the terrace deck with a void beneath": **fixed**. `podium_setback.png` shows the lowest sill band meeting the terrace deck continuously (y≈455–500 across the full width, no dark gap); `architecture_close.png` and `front.png` show the glass landing on the cornice slab.
- v001 P0 "lowest balconies below the podium cornice": **fixed**. `front.png` lowest slabs at y≈690–720 sit above the cornice at y≈745; `right_side.png` lowest slabs at y≈730–745 above the cornice at y≈770; `balcony_stack.png` lowest slab clears the brick.
- v001 P0 "interior camera inside the core": **fixed**. `interior.png` is now inside a unit looking out through the curtain wall at a balcony balustrade (see P2 #7 for its thinness).
- v001 P1 "two straight stacks on the south face against five staggered": **fixed** in count and stagger — five stacks in a checkerboard (see P2 #4 for density).
- v001 P1 "tower flush with the south edge where the sources show a terrace strip": **fixed** — `top.png` shows a strip between tower face (y≈805) and podium edge (y≈865); `podium_setback.png` shows the deck with bench and planter in front of the glass. The east edge remains flush (P2 #5).

## 3. Source conformance checklist

| item | status | view used / evidence |
|------|--------|----------------------|
| Silhouette | conforms | `front.png` vs `sources/front.png`, `aerial.png` vs `sources/oblique.jpg`: two-storey brick podium filling the lot, taller glass slab on the east/south, pale penthouse crown; podium extends west and north of the tower as in the sources. |
| Storey count | conforms | Source east stack (`sources/front.png` x≈655–690) shows 11 slab bands between parapet and podium; render `front.png` shows 11 glazed floors between roof parapet (y≈150) and base band (y≈745), spandrel every ~57 px. |
| Podium bays and storefronts | conforms (bay count deviates, P2 #10) | `podium_retail.png`, `corner_entry.png`, `front.png`: double-height glazed storefronts between brick piers, dark canopy band, second-storey ribbon windows with projecting sills, precast cornice. |
| Podium terrace and setback | conforms south / deviates east (P2 #5) | `top.png`, `podium_setback.png`: south terrace strip with glass balustrade and planters present; east flush where `top.jpg`/`oblique.jpg` show a narrow strip. |
| Tower curtain wall and spandrels | conforms | `facade_close.png`, `glass_close.png`: continuous dark mullions crossing white spandrel bands at every floor; glass shows interior depth. |
| Balcony stacks | conforms in placement, deviates in rhythm (P2 #4) | `front.png`: five staggered stacks south; `right_side.png` / `aerial.png`: two straight stacks east with glass balustrades, slabs clear of the corner columns. |
| Penthouse | conforms (plan shape P2 #6) | `roof_crown.png`, `top.png`: pale box with dark louvre panels, roof guard rail on all edges, rooftop units on the deck, matching `oblique.jpg` massing. |
| Materials hierarchy | conforms | Red brick podium, white precast cornice/sills, dark canopy, grey-blue glass with white spandrels, white corner columns, pale penthouse — matches source palette roles. |
| North / west faces | not visible in sources — coherent | `rear.png`, `rear_lane.png`, `left_side.png`: brick with ribbon windows, a service door, west storefronts (P2 #9); no fidelity judgement. |

## 4. Camera validity

- No view has the target occluded or the asset clipped; every view is legible.
- `front_corner.png`: valid image but wrong corner (SW instead of the SE street corner the oblique locks) — recorded as P1 #3.
- `interior.png`: valid (inside a unit, looking out), but near-featureless — P2 #7.
- `balcony_stack.png`: valid, poorly framed — P2 #8.
- `corner_entry.png`: valid and is the view that exposes P0 #1 and P1 #2 at the identity corner.
- All other whole-envelope and detail views are correctly aimed and readable.
