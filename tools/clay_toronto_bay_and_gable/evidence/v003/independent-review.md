# Independent holistic review: bayg v003 (RLASM v6.1 architectural clay)

Reviewer: independent; no relationship with the builder. Inputs read: `sources/front.png`, `sources/oblique.jpg`, `sources/top.jpg`, all 18 `renders/*.png` at full resolution, and the 4 phone boards. Zoomed crops (read-only derivatives) are in `/tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/crops-bayg-v003-indrev-9ee1c0ed/`.

## 1. Verdict

**VISUAL_REWORK_REQUIRED**: both v002 P1s are fixed in the pixels and the envelope now reads as the source house. Two new P1s block approval. First, the entrance stair has moved east of the door, with an iron guard across the door's front, where the source has a wide stair directly in front of the door between the posts. Second, the two re-framed whole-envelope cameras (front_corner and aerial) clip the asset, and aerial looks from the wrong quadrant.

Counts: P0 = 0, P1 = 2, P2 = 9

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | porch_entrance, front, front_corner, aerial, top | In porch_entrance, the porch runs from post x≈330 to post x≈1175. The door sits at x≈495–700, and an iron balustrade runs straight across its front (x≈355–720). The stone stair starts only east of the door (x≈720–1240) and runs past the east post line. The same layout shows in front (stair at x≈1110–1230, east of the door at x≈895–950) and top (stair and walk under the porch's east end). In the source (front crop and oblique crop), the stair is wide and spans the porch front from post to post, directly in front of the door. The iron guard is only on the porch sides and down the stair's east flank. The entrance sequence (door, then straight down the stair to the brick walk) is reversed in the render. | The stair is placed at the porch's east end, and the front guard is generated across the remaining front span. | Centre the stair on the door and widen it to span between the two front posts. Remove the front guard section in front of the door, and keep guards only on the porch's west and east sides and as handrails on the stair. Move the brick walk so it lines up with the new stair. |
| 2 | P1 | front_corner, aerial (whole-envelope roles) | front_corner: the chimney is cut off by the top edge of the frame, along with the east part of the main roof, and the porch stair, handrails and fence are cut off by the bottom edge. aerial: the porch posts, stair and front fence are cut off by the bottom edge. aerial also looks from the south-east, so it shows the porch end and the unsourced east wall and east gable. The builder says it frames from the source oblique's direction (south-west, west elevation on the left), but it does not, so it cannot be compared with the oblique. | The cameras were pushed in to fill the frame without any margin, and the aerial azimuth points to the wrong corner. | Pull both cameras back about 10–15% so the chimney pots, the finial and the stair foot are all inside the frame with margin. Turn aerial round to the south-west quadrant, at a higher elevation than front_corner, to match the source oblique. |
| 3 | P2 | gable_bargeboard, front | All three attic lights are the same height, under one head, with amber upper sashes in all three. In the source, the centre light is taller and the side lights are shorter, with their tops stepped down, and only the side lights have stained glass. | The builder made the heights equal on purpose (a v003 P2 change), which moves the gable away from the source. | Step the side lights down so their heads sit about 25% below the centre head. Put stained glass in the side lights only and clear glass in the centre. |
| 4 | P2 | porch_frieze, porch_entrance | A thin black seam runs across the top of each porch post cap, where the cap meets the beam above. | The post cap stops just short of the beam soffit, or the two faces z-fight. | Extend the cap 5–10 mm into the beam, or set the cap top exactly on the beam soffit. |
| 5 | P2 | bay_window (y≈975), foundation_fence | Small black notches at both bay-to-main-wall corners on the stone water table. The water table on the main wall is higher than the bay's water table, and a sloped transition piece joins them, leaving a void. | The bay plinth and the main-wall plinth are at different heights. | Run one water table at one height round the bay and along the main wall, mitred at the canted corners. |
| 6 | P2 | bay_window | The west hip of the porch roof and the east end of the bay's slate skirt roof cut into each other. The end of the porch's west fascia is left exposed in front of the skirt. | Two roofs are placed independently with overlapping extents. | Stop the porch roof against the bay's side face, or finish its west side with a short flashing return under the skirt. |
| 7 | P2 | porch_frieze | A small gap above the porch's east-side beam, where it meets the house's south wall, shows background tree pixels through the porch ceiling. | The east side beam and the ceiling do not close at the wall. | Extend the porch soffit or ceiling plane to meet the wall above the east-side beam. |
| 8 | P2 | porch_entrance, porch_frieze, gable_bargeboard | The porch corner brackets are straight diagonal braces, where the source has curved, pierced fretwork brackets. The gable has no pierced lattice spandrel panels beside the attic lights. The bargeboard foot drops hang about 0.5 m below the gable-base cornice. | Detail was simplified. | Use curved bracket profiles, add flat pierced panels either side of the attic windows, and shorten the bargeboard drops to finish near the knee brackets. |
| 9 | P2 | all; left_side, right_side, rear, top | The brick reads as pale, desaturated salmon (render mean ≈ RGB 159,123,107) instead of the source's saturated red-orange brick. The foundation is smooth light grey rather than reading as rough stone. In left_side, right_side, rear and top the house fills under about 30% of the frame. The brief's view list also names facade_close, architecture_close and glass_close, but those PNGs do not exist; 18 files are delivered. | Clay palette and lighting; default orbit framing; the view list does not match the render set. | Warm and saturate the brick base colour. Darken the foundation and give it a coarser tone. Tighten the orthographic-style elevation framings. Either deliver the three named close views or correct the view list. |

## 3. Source conformance checklist

| item | status | view(s) used / note |
|---|---|---|
| Silhouette | conforms | front vs source front; front_corner vs oblique: steep west gable, projecting south cross gable, hipped rear wing, east chimney |
| Storey count and proportions | conforms | front, west_side: raised ground floor, second floor, attic in the gables (2½ storeys) |
| Brick and joints | conforms, with palette deviation (P2 #9) | bay_window, west_side: coursed brick lines everywhere; colour too pale |
| Stone foundation and basement windows | conforms | foundation_fence, front, west_side, rear_north: grey raised plinth, muntined basement windows; smooth rather than rough (P2) |
| Canted bay: three faces | conforms | bay_window, front_corner, top |
| Bay: tall one-over-one sashes | conforms | bay_window |
| Bay: amber stained transoms | conforms | bay_window: amber transoms on all three faces of both floors |
| Bay: stone sill and lintel bands | conforms | bay_window: one mitred band per level; plinth notch (P2 #5) |
| Bay: slate skirt roof between floors | conforms | bay_window, front; clips porch roof (P2 #6) |
| Front gable: projects over the bay on a cornice | conforms | front, front_corner, gable_bargeboard, bay_window, top: the gable face is on the bay face plane and the cross-gable eave projects past the main eave in top. One moulded base cornice sits on two knee brackets and two consoles. No flat ledge. |
| Bargeboard with roundels and drops | conforms | gable_bargeboard; drops too long (P2 #8) |
| Fretwork arch | conforms | gable_bargeboard, front: inside the gable, under the rakes |
| Finial and pendant | conforms | gable_bargeboard: spike finial; the pendant stops just above the shared head |
| Attic windows | deviates (P2 #3) | gable_bargeboard: three lights the same height under one head; the source has a stepped triple with stained side lights |
| Porch: turned posts | conforms | porch_entrance, porch_frieze |
| Porch: spindle frieze | conforms | porch_frieze: shallower beam, frieze raised to meet it |
| Porch: corner brackets | conforms (simplified, P2 #8) | porch_frieze: brace ends are clean, with no black patches or slivers |
| Porch: iron balustrade | deviates (P1 #1) | porch_entrance: the guard runs across the door front instead of along the porch sides only |
| Porch: hipped roof | conforms | front_corner, aerial, top |
| Door and transom | conforms | porch_entrance: dark green door with panels and an amber transom under a stone head |
| Stair and walk | deviates (P1 #1) | porch_entrance, front, top: the stair is offset east of the door and past the east post; the brick walk follows the stair |
| Roof: cross gable | conforms | front_corner, roof_chimney, top: valleys into the main south slope, ridge below the main ridge |
| Roof: west and east gables | conforms | west_gable, roof_chimney, aerial |
| Roof: rear hip | conforms | top, rear_side, rear_north: the hip ridge dies into the main north slope; no voids |
| Roof: chimney at east | conforms | roof_chimney, aerial, top: brick stack with pots at the east end of the ridge |
| West side windows | conforms | west_side, left_side: tall sashes with stone sills and heads in a regular rhythm |
| West gable paired attic window | conforms | west_gable: paired tall sashes with separate heads and sills |
| Fence | conforms | foundation_fence, front, top: low iron fence round the front lawn, returning along the west |
| Lawn, shrubs, sidewalks, street trees | conforms | front, top, left_side: lawn, low-poly shrubs, sidewalks on both streets, street trees on the west |
| Plan (L following the source top) | conforms | top vs source top: the narrower rear wing is inset on both sides; the cross gable is weighted west; the porch is at the south-east |
| Materials hierarchy | conforms, with tone deviation (P2 #9) | brick walls; buff stone bands; grey slate; brown woodwork; dark iron; grey-brown gable shingle |

## 4. Camera validity

- **front_corner**: the target is legible, but the asset is clipped. The chimney and the east roof are cut off at the top edge, and the stair and fence at the bottom edge (P1 #2).
- **aerial**: the asset is clipped at the bottom edge (porch, stair, fence). The view is also from the south-east, the opposite diagonal to the source oblique, so it cannot be compared with it as a matched role (P1 #2).
- **rear_north**: the chimney pots touch the top edge. This is acceptable for a detail view of the rear face.
- **roof_chimney**: valid. The chimney, the east gable and the cross-gable valley are all legible.
- **left_side, right_side, rear, top**: valid and unobstructed, but the house is small in the frame (P2 #9).
- **Every other view** (front, rear_side, bay_window, gable_bargeboard, porch_entrance, porch_frieze, west_side, west_gable, foundation_fence, interior): the target is in view and legible. Trees partly cover the edges of west_side, west_gable and left_side, but no identity element is hidden.
- **Not delivered**: facade_close, architecture_close and glass_close are named in the brief, but no PNGs exist for them. 18 renders were delivered (P2 #9).

## 5. Previous-version findings: status in the pixels

**v002 P1s**

1. **Front gable flush with the main eave, upper bay projecting under a flat slate ledge**: **RESOLVED.**
   - In front, gable_bargeboard and bay_window, the gable face is on the bay's front plane. It sits on one moulded base cornice carried by knee brackets at both ends and two consoles at the bay's front corners.
   - In top, the cross-gable eave projects south of the main eave line.
   - front_corner and roof_chimney show no flat ledge in front of the gable, and the cross-gable roof valleys into the main south slope.
2. **Black patch or sliver where each porch brace meets the rail and the post**: **RESOLVED.**
   - Zoomed crops of every visible brace end in porch_frieze (left and right posts, front and side frieze) and porch_entrance (both posts) show clean ends at the rail soffit and inside the post.
   - None of those ends shows a black patch or sliver.
   - A separate thin black seam remains at the top of the post cap, where it meets the beam (P2 #4).

**Builder's v003 P2 claims**

- Attic lights the same height under one head, with the pendant above the head: done. However, this departs from the source's stepped triple (P2 #3).
- Gable shingle darker grey-brown with closer, darker courses: done.
- Porch beam shallower, with the frieze raised and the caps carried up: done, apart from the cap seam (P2 #4).
- Bay cornice replaced by the straight gable-base cornice, with no mitre slivers: done.
- front_corner and aerial framed from the source oblique's direction: **not true for aerial**, which looks from the south-east, and both views clip the asset (P1 #2).

**Earlier fixes that must still hold**

- Fretwork arch inside the gable, bargeboards on the rakes, no boards poking through: **holds** (gable_bargeboard, front).
- One eave line per roof, rear hip ridge dying into the main north slope, no black voids at hips or valleys: **holds** on the roofs (top, rear_side, rear_north). The only black voids found are at the bay water table (P2 #5).
- L plan following the source top: **holds** (top).
- West gable with paired tall attic sashes: **holds** (west_gable).
- One mitred stone band per level round the bay: **holds** (bay_window).
- Raised-panel door: **holds**. Stained transoms only where the source shows them: **holds** for the bay and the door; the attic transoms are covered in P2 #3. Every upper lintel clears the eaves: **holds**, narrowly, for the east upper window (bay_window).
