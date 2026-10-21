# Independent holistic review: clay-calgary-cbe-brutalist-hq v004 (RLASM v6.1 architectural clay)

Verdict: PASS_ZERO_P0_P1

Counts: P0=0 P1=0 P2=6

## 1. Verdict

**PASS_ZERO_P0_P1.** The re-aimed front_corner camera fixes the v003 P1. Its east face now shows a dark pane at the back of the coffer in cells 1 to 12 on all three floors, at the source-oblique share of the building width. The geometry still matches the earlier fixes, and no black patches, slots, wedges, floating parts or intersecting parts appear in any of the 18 renders.

Inputs opened at full resolution with the Read tool:
- the three locked sources: sources/front.png, sources/oblique.jpg and sources/top.jpg;
- all 18 renders: front, front_corner, aerial, top, left_side, right_side, rear, rear_side, facade_close, window_module, corner_cantilever, ground_entrance, arcade_soffit, sculpture_plaza, west_side, roof_penthouse, interior and rear_north;
- the four phone boards.

Zoomed crops and gridded measurement overlays were written only to the new folder `review/crops_qhtvmz/` inside the v004 folder. No other file was modified.

## 2. Findings table

No P0 or P1 findings.

| # | severity | view(s) | symptom (what the pixels show) | evidence | likely cause | finite fix |
|---|----------|---------|--------------------------------|----------|--------------|------------|
| 1 | P2 | front_corner | The northernmost east cell (cell 13) on each floor shows only a pale grey sliver with a dark mullion dot, not a dark pane. Cells 1 to 12 on every floor show a clear dark pane. | crops_qhtvmz/fc_east_ne_end.png (5x), fc_east_far.png and fc_east_near.png (3x) | At the far end of the face the incidence is about 75 degrees, so the near jamb hides most of the glass, and the remaining sliver picks up a light interior or reflection. | Optional: darken the glass shader at grazing angles, or accept as is. This cell is at the extreme end of a foreshortened face, and the face reads as glazed. |
| 2 | P2 | front | The penthouse now rises above the south parapet, by about 25 to 45 px, but the parapet hides the lower half of the louvre, which reads as a thin dark slot. The air-handling units show only as slivers. In the source the penthouse, its full louvre and the air-handling units clearly clear the parapet. The source's south face also converges more strongly: its west end is about 0.64 of the corner height, against 0.81 in the render. | crops_qhtvmz/fr_roofline.png (3x) | A long lens and a distant eye-level camera flatten the view. The source perspective is not fully physical. | Optional: raise the camera 1 to 2 m, or shorten the lens slightly (about 50 to 55 mm), so the whole louvre clears the parapet. |
| 3 | P2 | front_corner | The ground-storey storefront glass under the cantilever reads pale and light grey. In the source oblique the storefront band is dark and shadowed under the box, and the board-formed ground storey reads darker than the precast box. | crops_qhtvmz/fc_ground.png (3x) | The storefront glass reflects the bright paving. Ambient light under the soffit is too high. | Darken the storefront glass, or add some occlusion under the soffit. |
| 4 | P2 | aerial | This finding carries over from v003 (#5). Every east cell shows a pane, but each is a narrow slit about 0.35 to 0.4 of the foreshortened bay. The source oblique shows about 0.5. | crops_qhtvmz/ae_east.png (3x) | The splayed jamb partly hides the glass at oblique incidence. | Optional: narrow the jamb splay to about 0.22 m, or lower the aerial elevation slightly. |
| 5 | P2 | right_side, corner_cantilever | This finding carries over from v003 (#6). The east entrance reads only as a glazed bay with a mid-rail. It is hard to tell apart from the adjacent storefronts. | crops_qhtvmz/rs_ground_left.png (3x) | The door has no distinguishing frame, canopy or head band. | Give the east doors a heavier frame or a head band. |
| 6 | P2 | (render set) | This finding carries over from v003 (#4). The brief's view list names `architecture_close`, `glass_close` and `east_side`, and lists facade_close twice. renders/ contains none of those three, and it contains `west_side`, which the list does not name. | the renders/ listing (18 files) | The brief template and the camera manifest have drifted apart. | Bring the view list in line with the delivered renders. |

## 3. Source conformance checklist

| Item | Status | Evidence (view) |
|------|--------|-----------------|
| Silhouette and storey count | conforms | front, front_corner, aerial, rear and left_side show three precast office floors over a tall recessed ground storey, with one set-back penthouse. The near-square plan matches the source top. In the top render the building is 347 x 315 px (ratio 1.10). In the source top it is 610 x 555 px (ratio 1.10). |
| Bay rhythm 14 x 13 | conforms | rear_north and front show 14 bays on the north and south faces. right_side and west_side show 13 bays on the east and west faces. front_corner shows 14 bays on the south face and 13 on the east. |
| Window depth and fin/nose relief | conforms | facade_close, window_module, corner_cantilever and sculpture_plaza show four-way splayed coffers, with tapered verticals per cell, continuous floor-line members, sloped sill noses and glass set at the back. The glass-to-bay ratio is 0.687 in facade_close: a dark run of 112 px over a 163 px pitch, measured on the bottom row (y=820). This is unchanged from v003. front_corner and aerial show panes on the east face in every cell, with one P2 exception (#1). |
| Fascia and parapet bands | conforms | right_side, rear_north and facade_close show one continuous plain parapet band of about 0.55 to 0.6 of the pitch, with a coping and the grid stopping at its foot. The deep plain fascia over the ground storey has no panel joints (front, corner_cantilever). |
| Cantilever over the recessed ground storey with board-formed columns | conforms | corner_cantilever, arcade_soffit, ground_entrance and front_corner show a cantilever of about 3 m with freestanding board-formed (horizontally banded) columns. Their contact with the paving and the soffit is clean. Board-formed wall panels sit at the west end of the south front (front, left_side). Solid corner piers are present (corner_cantilever, front). |
| Entrances and podium steps | conforms | ground_entrance and sculpture_plaza show glazed double doors facing the plaza, two-tier storefronts and podium steps. The east entrance is present but weak (P2 #5). |
| Penthouse and roof plant | conforms | In top, the penthouse is about 0.48 x 0.69 of the building, about 0.09 of the depth from the north edge and 0.22 from the south, centred east-west. The source top gives about 0.49, 0.086 and 0.22. roof_penthouse, west_side and rear show louvres in the upper middle of the walls, steel doors, and two air-handling units with twin round fans. The railed unit stands on the main roof just east of the penthouse, as in the source top, and small vents are present. In front the penthouse and louvre read above the parapet, but only partly (P2 #2). |
| Sculpture plaza and site | conforms | top, aerial, front_corner and sculpture_plaza show a round plinth with a ring of standing figures in the south-east paved plaza, with the figures in contact with the plinth top. The lawn is to the south-west, the brick neighbours to the west and north, and the east street has street trees, a crossing and a lamp. The south street has sidewalks. |
| Materials hierarchy | conforms | The precast box is warm grey, and the board-formed ground storey is slightly darker and banded (front, ground_entrance, corner_cantilever). Glazing is dark, the neighbours are brick, the lawn green and the asphalt grey. The ground glass in front_corner reads lighter than in the source (P2 #3). |

## 4. Camera validity

No view has its target occluded or clipped, and every view is legible.

- **front_corner** matches the source-oblique viewpoint, measured on gridded overlays (crops_qhtvmz/src_oblique_grid.png and fc_grid.png).
  - Projected face widths: south about 626 px and east about 434 px in the render, a ratio of 1.44. The source gives about 530 px and 405 px, a ratio of 1.31. The east face takes 41% of the building width in the render and 43% in the source.
  - The east parapet edge slopes at -0.59 in both.
  - The south parapet edge slopes at 0.39 in the render and 0.27 in the source, so the render looks slightly more from the east and higher.
  - Its perspective is somewhat stronger than the source's.
  - Overall the azimuth and elevation fall within the source-oblique regime: south face left, east face right, roof plane and penthouse fully read, sculpture plaza in the lower centre. The v003 grazing angle is gone.
- **front** matches the locked front.
  - The camera is at eye level: the ground line is near-horizontal in both.
  - The south-east corner sits at about 65% of the frame width in the render and 64% in the source.
  - The south face runs on the left and the foreshortened east face on the right, cut off at the frame edge as in the source.
  - The plinth is in the foreground and the board-formed west end is visible.
  - Deviations: the penthouse and louvre show less above the parapet, and the south face converges less than in the source (P2 #2).
- **west_side** is a valid, elevated coherence view.
  - No source shows the west face, so it was not judged against the sources' angles.
  - It shows the 13-bay west face with a pane in every one of its 39 cells, and the penthouse with its west louvre and steel door.
  - The three-storey brick neighbour sits in the foreground without hiding the facade. A freestanding column under the cantilever makes clean contact with the ground (crops_qhtvmz/ws_lower_right.png).
- **aerial** is unchanged from v003 and valid.
- **right_side** remains the only head-on east elevation, so the v003 duplicate is gone.
- **interior** shows a uniform grey exterior through the windows. This is legible and acceptable for clay.

## 5. Previous-version findings

| Previous finding | Status in v004 pixels |
|------------------|-----------------------|
| v003 P1: front_corner east face reads blank at a grazing azimuth | **Fixed.** At 3x zoom the east face shows a dark pane in cells 1 to 12 on all three floors. Cell 13 at the far end shows only a pale sliver (P2 #1). The camera now matches the source-oblique azimuth and face share. |
| v002 P1: glass too small and too deep in the coffers, east face blank at oblique angles | **Fixed.** Glass is 0.687 of the bay in facade_close, with readable splays and returns. East panes read in front, front_corner and aerial. |
| v003 P2 #2: front camera hides the penthouse | **Partly fixed.** The penthouse and louvre now read above the south parapet, but the louvre is half hidden (P2 #2). |
| v003 P2 #3: duplicate east views | **Fixed.** east_side is replaced by west_side, a valid west coherence view. |
| v003 P2 #4: brief view list does not match the render set | **Not fixed** (P2 #6). |
| v003 P2 #5: narrow aerial panes | **Not fixed** (P2 #4). The brief said it would not be addressed. |
| v003 P2 #6: weak east door | **Not fixed** (P2 #5). The brief said it would not be addressed. |
| Earlier fixes that must still hold: the cell grid, the 1.85 x 2.4 m glass, the continuous parapet band with the grid stopping at its foot, the 5.8 m recessed ground storey under a plain fascia with two-tier storefronts, the solid corner piers, the 14 x 13 rhythm, the cantilever of about 3 m on board-formed columns, the entrances and steps, the penthouse position, louvres and plant, the south-east sculpture plaza, and the warm palette | **All still hold.** No regression was found (see the checklist). |
