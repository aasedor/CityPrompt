# Independent holistic review: clay-toronto-bay-and-gable-house v001 (RLASM v6.1 architectural clay)

Reviewer: independent; did not build this candidate. Judged only the rendered pixels in `renders/*.png` and `boards/*.png` against the locked sources `sources/front.png`, `sources/oblique.jpg` and `sources/top.jpg`. I opened every render, every board and all three sources at full resolution with the Read tool, and checked zoomed crops (written only to the new folder `/tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/bayg-v001-indep-crops-725129740/`). I did not use metadata, counts, hashes or builder notes as proof.

## 1. Verdict

**Verdict: VISUAL_REWORK_REQUIRED.** The house reads as the right red-brick bay-and-gable type with a raised stone base, a canted bay, a side porch, slate roofs and an east chimney, but its headline front gable ornament is incoherent (arch floating outside the gable, bargeboards running past the gable onto the wall), the rear hipped roof has a stacked double eave with black voids at its corners, and the plan and west gable do not follow the locked top and front sources.

Counts: P0 = 0, P1 = 6, P2 = 10

## 2. Findings

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | gable_bargeboard, front, front_corner, roof_chimney, west_gable | The "curved fretwork arch" is two segmented arcs with black tick marks, sitting **outside** the gable rakes and lying across the main roof slopes like a halo (gable_bargeboard x 410–1030, y 300–530; it shows edge-on as a curved strip on the roof at west_gable x 1250–1310). Horizontal stub boards also stick out through both rakes just below the apex (gable_bargeboard ~530–600 / 840–910, y 310). In front.png the source has the curved fretwork arch **inside** the gable, under the bargeboard, framing the triple attic window. | The arch's radius and centre are set off the gable plane or larger than the gable opening, so it sweeps through the rakes. The collar or stub members are longer than the gable width at that height. | Rebuild the arch as one pierced board inside the gable face, inset behind the bargeboard, springing from the bargeboard feet at the attic-window sill level and peaking just under the pendant. Trim the stub boards to stop inside the rake boards. |
| 2 | P1 | gable_bargeboard, front, bay_window, front_corner | The roundel and drop "bargeboard" is a second pair of diagonal boards set well inside the rakes. They cross the gable face and run **below the gable foot**, past the bay tray, and end in mid-air on the brick wall beside the bay (gable_bargeboard ends at ~190,1030 and ~1250,1030; bay_window ~300,160 and ~1040,160). The roundels are loose rings floating on the brick between the rake and the diagonal, not holes pierced in a board. Source front: a wide pierced bargeboard that hugs the rake underside, with drops on its lower edge, stops at the gable foot on corner brackets. | The bargeboard is placed with its own slope and offset rather than parented to the rake line, and its length was not clipped to the gable eave. The roundels are separate tori, not holes cut in the board. | Make the bargeboard one board directly under each rake, the same slope and length as the rake, ending at the gable foot on a bracket. Cut the roundels as holes in that board, or put them flush within its depth, and hang the drops from its lower edge. Remove the inner diagonal boards. |
| 3 | P1 | rear_north, rear, rear_side, aerial, top, front_corner, west_side | The rear hipped roof does not run down to its eave. It sits on a flat tan ledge, with a separate lower grey skirt and gutter under it, so the eave reads as two stacked roofs. Each hip corner ends in a **solid black void block** (rear_north ~250–310,300 and ~1135–1195,300; rear_side ~745,600 and ~945,505; aerial ~735,405 and ~865,488; top ~620,400 and ~820,400; front_corner ~572,487). | The hip pyramid is set on top of a wall-plate or cornice slab instead of running out to the fascia. A second eave or gutter run is added below it. Corner pieces are left open or have back faces showing as black. | Run the hip planes out to one fascia line with one mitred gutter. Delete the lower skirt, or merge it into the eave. Close the corner geometry, and check the normals so that no black faces show at any hip foot. |
| 4 | P1 | top, aerial, rear, rear_side vs source top (and oblique) | **Plan and roof massing do not follow the governing top source.** In the source top, the front gabled section is the dominant roof mass (about 70% of the house depth, with an E-W ridge and the chimney at its east end). The rear hipped section is a **narrower** wing set in from both side walls (rear-hip eaves span about 70% of the main-block width, inset more on the east). In the render top, the rear hip is **full width**, flush with both side walls, and takes about 47% of the depth, so the front gabled section is only about 53%. The rear wing's corner step and the band where the front roof's north slope sits between the side eaves are missing. | Rear block is built at full width and too deep, probably from a simplified rectangular footprint. | Narrow the rear hipped block to about 70% of the main width, inset more on the east than the west, and give it the matching wall steps. Deepen the front E-W gabled section to about 2/3 of the house depth, keeping the chimney at the east gable on that ridge. Then re-check the west gable extent (finding 5) against the new depth. |
| 5 | P1 | west_gable, west_side, left_side, front_corner vs source front / oblique | The west gable has one small square **2x2 window** (west_gable centre). In the source front and oblique the west gable has a **paired attic window**: two tall narrow sashes side by side with stone sills and lintels, matching the tall west-side sashes below. | The window module for the west gable uses a generic attic casement instead of the source pair. | Replace it with two tall one-over-one sashes, centred in the gable and sized like the west second-floor windows, with a shared or separate stone sill and lintel. |
| 6 | P1 | bay_window, front, foundation_fence, gable_bargeboard vs source front | The bay's **continuous buff stone sill and lintel bands** are not continuous. Each bay face has its own sill slab with gaps and steps at the canted corners (bay_window y ~400–420 and ~885–940; foundation_fence y ~260–305). The upper bay has **no lintel band at all**: the window heads run into the underside of the gable tray. The source shows unbroken buff bands that wrap all three bay faces at sill level and at lintel level on both floors (front.png bay at the y ~380 and ~430/575 levels). | Sills are made per opening rather than as a wrapped band. The upper lintel course was left out under the gable tray. | Replace the per-face sills with one band at each sill level that follows the bay's canted plan and runs back into the main wall. Add a matching lintel band above the upper bay windows below the tray, and keep the lower one under the skirt roof as one mitred band. |
| 7 | P2 | gable_bargeboard, front | The front gable field is brick. The source fills it with grey-brown decorative shingle or panel work behind the bargeboard. | Gable infill material not assigned. | Give the gable triangle above the tray a shingle or panel finish in the source's grey-brown. |
| 8 | P2 | front, gable_bargeboard | The spike finial is about twice the source's height relative to the gable. | Finial scale. | Reduce it to about 60% of its current length. |
| 9 | P2 | gable_bargeboard (~500,880 / 930,880), porch_frieze (~155,520 / 440,515 / 1000,610), west_gable apex (~718,205) and eave (~105,840), roof_chimney (~540,485) | Small black triangles and diamonds at mitres and joints: the gable tray corners, the tops of the porch brackets, the west gable apex and the junction of the rear hip with the front ridge. | Unclosed mitres, or back faces. | Close the joints. |
| 10 | P2 | porch_entrance, porch_frieze | The lower panels of the green door are flat tan patches that read like boards fixed over the door. In the source they are green raised panels. | Panel material set to trim colour. | Use the door green, or a slightly darker green, for the panels. |
| 11 | P2 | west_side, bay_window, front | Amber "stained" transoms are on every window, including the whole west side and the window east of the bay. In the source, stained glass is limited to the bay sashes and the door transom, which dilutes the bay's identity. | Global window module. | Limit the amber transoms to the bay sashes and the door. Use plain upper sashes elsewhere. |
| 12 | P2 | front, porch_frieze, porch_entrance | From street level the porch roof reads almost flat, with a heavy dark fascia band. The source porch roof is a visibly pitched slate hip. | Low pitch and an oversized fascia or gutter. | Raise the pitch to about 25–30° and slim the fascia. |
| 13 | P2 | rear_north | The upper rear windows have no stone lintels, but the lower rear windows and every other elevation have them. | Missing lintel instances. | Add the lintels. |
| 14 | P2 | gable_bargeboard, bay_window, front_corner | The canted tray between the bay top and the gable foot is a heavy, deep box that reads like a balcony. The source shows a thinner moulded cornice on brackets. | Tray depth and height. | Reduce the tray's projection and height, and add the corner brackets seen in the source. |
| 15 | P2 | front_corner, aerial, top, left_side, right_side, rear (and phone boards) | Framing is loose. The house fills only about 15–25% of the frame width, against about 40% in the oblique source and about 35% in the top source, so matched-role detail is small on the phone boards. The target is still legible, not occluded and not clipped. | Camera distance and focal length. | Tighten the framing so that the house fills about 40–60% of the frame width. |
| 16 | P2 | evidence set | The brief's detail list names `facade_close`, `architecture_close` and `glass_close`, but none of them exist. The 18 renders present match the brief's stated count of 18. | Template list differs from the render manifest. | Either render those three views or correct the view list. |

There are no P0 findings. The type, storey count, raised base, bay, porch, roofs, chimney and site all read correctly, and no camera is invalid.

## 3. Source conformance checklist

| Item | Status | View(s) used |
|---|---|---|
| Silhouette | deviates: correct type and overall outline, but the rear block is full width and too deep, the front gabled block too shallow, and the arch protrudes past the front gable outline (findings 1, 4) | front, front_corner, top, aerial vs all sources |
| Storey count and proportions | conforms: two and a half storeys over a raised ground floor; the bay is about half the facade width; the gable is steep | front, left_side, west_side |
| Brick and joints | conforms for clay: red brick with coursing lines; colour inside the source palette | bay_window, west_side, porch_entrance |
| Stone foundation and basement windows | conforms: grey raised base with muntined basement windows on the front, the west side and the rear (smooth, which is acceptable for clay) | foundation_fence, west_side, rear_north |
| Canted bay: three faces | conforms | bay_window, front, top |
| Canted bay: sashes | conforms: tall one-over-one sashes on all three faces, both floors | bay_window |
| Canted bay: transoms | conforms on the bay. Over-applied on other windows (finding 11) | bay_window, west_side |
| Canted bay: stone bands | deviates: per-face sills with corner gaps and no upper lintel band (finding 6) | bay_window, foundation_fence |
| Canted bay: skirt roof | conforms: grey canted skirt roof between the floors | bay_window, front |
| Front gable: bargeboard | deviates: inner diagonal boards are not on the rake and overrun below the gable foot (finding 2) | gable_bargeboard, front |
| Front gable: roundels | deviates: loose floating rings, not pierced in a board (finding 2) | gable_bargeboard |
| Front gable: arch | deviates: outside the gable, lying across the roof (finding 1) | gable_bargeboard, west_gable, roof_chimney |
| Front gable: finial | conforms in kind, but oversized (finding 8) | gable_bargeboard |
| Front gable: pendant | conforms: king post with a medallion and drop at the apex | gable_bargeboard |
| Front gable: triple attic window | conforms: tall centre light with narrower side lights | gable_bargeboard, front |
| Porch posts | conforms: turned posts | porch_entrance, porch_frieze |
| Porch frieze | conforms: spindle frieze | porch_frieze |
| Porch brackets | conforms: corner brackets (with small black mitre voids, finding 9) | porch_frieze |
| Porch balustrade | conforms: iron balustrade | porch_entrance, front |
| Porch hipped roof | deviates slightly: hipped in plan, but reads almost flat from the street (finding 12) | top, front, porch_frieze |
| Door and transom | conforms: dark green door with an amber stained transom (panel colour, finding 10) | porch_entrance |
| Stair and walk | conforms: stone stair with iron handrails down to a short brick walk to the sidewalk | porch_entrance, front, top |
| Roof: cross gable | conforms in position, over the bay on the west half of the front | top, front_corner, roof_chimney |
| Roof: west and east gables | conforms in kind: gables on the front section, west and east | left_side, right_side, west_gable |
| Roof: rear hip | deviates: full width with a stacked double eave and black corner voids (findings 3, 4) | rear_north, rear_side, top |
| Roof: chimney | conforms: brick chimney with pots at the east end of the front-section ridge, by the east gable | right_side, roof_chimney, top |
| West side windows | conforms: tall sashes in a regular rhythm with stone sills and lintels | west_side, left_side |
| West gable window | deviates: one 2x2 window instead of a paired attic window (finding 5) | west_gable |
| Fence | conforms: low iron fence enclosing the front lawn and returning toward the bay corner | foundation_fence, front, top |
| Lawn | conforms | front, top |
| Sidewalks | conforms: on the south street and the west side street, with a grass strip | top, front_corner |
| Trees | conforms: street trees on the west side street and an east-side tree (shrubs present) | top, front |
| Materials hierarchy | mostly conforms: brick body, buff stone trim, grey slate roofs, tan woodwork, dark iron, grey base. Deviates on the brick gable infill (finding 7) and the transoms on every window (finding 11) | front, bay_window, gable_bargeboard |

## 4. Camera validity

- No view has an occluded target, a clipped asset or an illegible subject.
- `front` matches the source front role: low street-level three-quarter view from the south-west.
- `front_corner` matches the oblique role (high three-quarter from the south-west, showing the front and the long west wall).
- `top` is a valid nadir view with the south street at the bottom and the west side street on the left, which matches the plan orientation of the source top.
- `front_corner`, `aerial`, `top`, `left_side`, `right_side` and `rear` are framed loosely: the house fills only about 15–25% of the frame width, which makes matched-role comparison on the phone boards harder (P2, finding 15).
- In `west_gable` a tree crown covers the lower-right corner, but the gable itself is fully visible.
- `interior` is a legible interior with a fireplace.

## 5. Previous-version findings

This is the first version (v001), so there are no previous-version findings to carry forward or close.
