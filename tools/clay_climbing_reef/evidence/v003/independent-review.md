# Independent holistic review: The Reef (climbing_wall_building / variant_3), v003

Reviewer: independent, adversarial. I judged only rendered pixels against the locked sources (sources/front.png, sources/oblique.jpg, sources/top.jpg). I opened all 18 renders at full resolution, plus the three sources and the phone boards. I also made enlarged crops of the source walls and of the render's pocket field and roll-over. I ignored builder notes, counts and metadata as evidence.

## 1. Verdict

**VISUAL_REWORK_REQUIRED**: envelope, plan, bands, domes, entrances, apron/curb and landscape all conform. The climbing pockets are still the blocker: v003 overshoots v002. At envelope scale the walls read as Swiss cheese, with about three times the source's pocket density spread evenly down to the dark base. On the pale roll-over the pockets read as flat teal decals or bubbles, not as hollows.

Counts: **P0 = 0, P1 = 2, P2 = 8**.

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | front, front_corner, left_side, right_side, rear, rear_side, climbing_pockets, facade_close, top; board phone-01 | **Pocket rhythm, density and distribution do not match the source.** Render front shows roughly 45-55 pockets on the three visible lobe faces. Source front shows about 16-18 on the same faces. The render's pockets sit in a near-regular field on every band, including the lowest dark band and the tucked base. In climbing_pockets a 1.5 m hollow (x 320-590, y 770-985) touches the apron line. In left_side and right_side the near lobe carries four stacked rows of near-equal ellipses. In the source the lower wall is mostly smooth and carries only holds. The source's pockets cluster on the upper wall and the roll-over shoulder, vary in size and aspect (several are vertically elongated), and blend into the skin with soft rounded rims. The render's rims are crisp cookie-cutter ellipses of near-uniform size. Side by side on board phone-01, the render reads as a perforated sponge or cheese, not a sculpted reef shell with sparse pockets. | About 72 caps placed with roughly area-uniform spacing over every wall band. The 0.9-1.6 m range is used near its top end, with no height bias and no rim blend. | Cut to about 30-36 pockets in total. Put about 70% of them on the upper wall band and the roll-over shoulder. Allow no more than 2-3 per lobe face on the two lowest bands, and none within 0.6 m of the base tuck. Vary the diameter from 0.6 to 1.6 m and the aspect from 1.0 to 1.6 (some vertical). Add a 5-10 cm rounded fillet at each rim so it blends instead of cutting. Re-render front, left_side and climbing_pockets and compare against the source front crop. |
| 2 | P1 | front (x 560-720, y 490-560), front_corner (x 600-700, y 560-640), roof_skylights (x 180-250, y 680-740; x 560-640, y 950-1030; x 990-1040, y 950-1030; x 1230-1270, y 600-640), architecture_close (x 370-450, y 500-580; x 880-950, y 490-550), top (ring of teal spots around the plan edge) | **Roll-over and shoulder pockets read as flat teal decals or translucent raised bubbles, not hollows.** Their edges are soft and ghosted, with no shadowed inner wall or lip highlight. The saturated teal lining against the pale seafoam band does all the work, so they read as polka dots. In front and roof_skylights several look convex. In the source, the shoulder pockets keep the host band's pale hue and read as hollows only through shadow and an inner wall. | The rule "lining one contour band darker" switches the hue on the pale bands. Caps are shallow relative to the low-curvature roll-over and lit by a near-top light. The soft roof material also hazes the rim. | On the roll-over and roof, keep the lining in the host band's hue with only a value step (10-15% darker). Deepen those caps to at least 0.45 m, or tilt them toward the wall normal so an inner wall is visible. Add a rim fillet so it catches a highlight. Verify in roof_skylights and front that each shoulder pocket shows a shadowed upper inner wall. |
| 3 | P2 | front, front_corner, meadow_path, facade_close | Holds cluster in a sprinkled band just below the roll-over. The lowest dark band is sparse. The source's holds run in vertical routes from the base up through the mid bands. | Hold scatter is weighted by band area or curvature, not by reach height. | Weight hold density toward 0.3-4 m height and group holds into loose vertical routes. |
| 4 | P2 | front, top, glass_close, roof_skylights | Roof contour edges are soft and milky, with mottled grey blotches (top x 520-700, y 450-560; front x 600-900, y 350-500). The source shows crisp stepped contour lines on a matte pale roof. | Roof shading softness or a translucency-like material, and the bands blended with too wide a falloff. | Give the roof bands a hard step (no more than 2 cm blend) and keep the roof material opaque and matte. |
| 5 | P2 | architecture_close (about x 500-610, y 730-760) | A light rectangular shading smear sits below a large pocket. | A normal or tessellation artefact where the cap boolean meets a band seam. | Recompute normals and add support loops around that cap. |
| 6 | P2 | entrance_sw, entrance_se, meadow_path | The arch lining edge shows visible straight polygon facets. | Low segment count on the arch profile. | Use at least 48 segments on the arch sweep, or smooth shading. |
| 7 | P2 | curb_gap, meadow_path, top, aerial | The white shell paths have jagged zigzag edges. The source shows soft organic edges. | Low-resolution, randomly jittered path outline. | Smooth the outline with a spline and reduce the jitter amplitude. |
| 8 | P2 | aerial, rear_side, architecture_close, left_side, right_side, rear, facade_close | Few low-poly trees. The source has a dense mature canopy beyond the ring path and small trees inside the meadow beds near the curb. A finite lawn disc shows a curved edge against a grey void at the top of aerial and rear_side, and side views have a flat grey sky. | Sparse tree scatter, plus a finite ground plane with no horizon treatment. | Add 6-10 more trees beyond the ring and 3-4 small trees in the beds. Extend the lawn past the horizon, or fade it to a sky gradient. |

Minor notes, not counted: one pocket is cut by the lobe silhouette in facade_close (about x 1130, y 740). The tunnel ends read as black voids in interior, which is coherent for glazed doors in shade.

## 3. Source conformance checklist

| item | status | view(s) used | note |
|---|---|---|---|
| Silhouette and plan: four lobes | conforms | top vs source top | Four-lobed starfish. EW:NS is about 1.13 in the render vs about 1.11 in the source. |
| Lobe relative sizes (N narrowest, W longest) | conforms | top | The north lobe is narrowest and the west lobe slightly the longest. The render is a little more symmetric than the source. |
| Concave bays between lobes | conforms | top, front, aerial | Soft concave bays at NE, SE, SW and NW. |
| Wall height and bulge | conforms | right_side, rear, front | Near-vertical bulging walls with a tucked dark base. |
| Roll-over to the roof plateau, roughly 7 m | conforms | front, architecture_close, left_side | Rounded shoulder to a gently undulating plateau. The roof is somewhat smoother and less lumpy than the source (P2-level). |
| Contour bands: count and colours | conforms | front, facade_close, meadow_path | About 5-6 bands, deep teal through teal and aquamarine to pale seafoam on the roof. |
| Contour bands: wavy edges and roof contour lines | deviates (P2) | front, top, glass_close | The wall bands are wavy as required. The roof contour lines are soft and milky rather than crisp (finding 4). |
| Pockets: size | conforms (range) / deviates (uniformity) | climbing_pockets, facade_close | Sizes fall within 0.9-1.6 m but are near-uniform and toward the large end. |
| Pockets: number | deviates (P1) | front vs source front, left_side, right_side | About three times the source density (finding 1). |
| Pockets: distribution | deviates (P1) | front, left_side, climbing_pockets | Spread evenly down to the base. The source biases them to the upper wall and shoulder (finding 1). |
| Pockets: depth reading | conforms on the walls / deviates on the roll-over (P1) | facade_close, climbing_pockets / roof_skylights, front | Wall pockets show a shadowed inner wall. Shoulder pockets read as decals or bubbles (finding 2). |
| Climbing holds | conforms (presence, colour, form) / deviates in distribution (P2) | entrance_sw, facade_close, front | Rounded multicoloured six-sided holds sit on the skin with contact. They skew toward the upper band (finding 3). |
| Skylight domes: count 12 | conforms | top, front_corner, roof_skylights | 1 large plus 11 small. |
| Skylight positions | conforms | top vs source top | Large dome at the centre. Small domes: 1 at the N tip and 3 in the N cluster, 2 on the W lobe, 2 on the E lobe, 2 in the S cluster and 1 at the S tip. This matches the source pattern. |
| Large central dome | conforms | top, glass_close | |
| Dome white rims and contact | conforms | glass_close | The rims sit flush on the roof with a visible upstand. No floating. |
| Entrances: position in the bays | conforms | front (SW, SE), rear and right_side (NE, NW), aerial, rear_side | At the foot of each bay. |
| Entrances: arched, cave-like form with depth and returns | conforms | entrance_sw, entrance_se, meadow_path, curb_gap | A deep lining return with set-back dark glazed doors. The lining edge is faceted (P2, finding 6). |
| Apron: sand crash pad following the outline | conforms | top, front, front_corner | |
| Curb: low, rounded, sand-coloured | conforms | curb_gap, climbing_pockets | Rounded end caps. |
| Curb: four diagonal gaps | conforms | top, aerial, curb_gap | Gaps at NW, NE, SE and SW, aligned to the paths. |
| White crushed-shell paths | conforms (presence and colour) / deviates in edge quality (P2) | curb_gap, top | Flake texture is present. Edges are jagged (finding 7). |
| Meadow beds: grasses, palmetto clumps, shrubs on dark mulch | conforms | front, curb_gap, meadow_path | Low beds with rounded ends. |
| Trees | deviates (P2) | aerial, rear_side, front | Too few, and none in the inner beds near the curb in most views (finding 8). |
| Ring path, about 46 m | conforms | top, aerial | About 47 m measured against the 30 m shell span. |
| Lawn beyond | conforms / deviates at the frame top (P2) | front, rear, aerial, rear_side | Lawn reaches every side edge. A curved disc edge and grey void show at the top of aerial and rear_side. |
| Materials hierarchy | conforms | all | Teal shell over sand apron and curb, white paths, dark mulch, green lawn, grey-glass domes on white rims. All in clay source palette. |
| Interior (coherence only) | coherent | interior | The dome oculi align with the roof field. Holds are on the inner skin, entrance arches read from inside, and there are boulder props. |

## 4. Camera validity

All 18 views are valid. The target is legible and not clipped in any of them.

- entrance_sw: a curb end-cap intrudes at bottom right (x 1060-1440, y 1010-1080). It does not occlude the entrance.
- interior: dim but legible.
- climbing_pockets and facade_close crop the lobe at the frame edge by design. Contact with the apron is visible.
- aerial and rear_side show the lawn disc edge at the top of the frame. That is a background matter (P2, finding 8), not a camera invalidation.
