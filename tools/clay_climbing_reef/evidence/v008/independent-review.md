# Independent holistic review: The Reef (climbing_wall_building / variant_3), v008

Reviewer: independent RLASM v6.1 holistic reviewer (not the builder). I judged only rendered pixels against the locked sources `sources/front.png`, `sources/oblique.jpg` and `sources/top.jpg`. I opened all 18 renders and all 4 phone boards at full resolution and zoomed in on the cup interiors, the plan silhouette, the curb gaps, the entrance thresholds and the band edges.

## 1. Verdict

**VISUAL_REWORK_REQUIRED**: the envelope, plan, domes, entrances, apron, curb gaps and landscape now match the sources and have no P0 defects, but every climbing pocket still shows clearly stepped concentric shade terraces and a dark pinched crease at the bottom of the cup at close and mid range, so the pockets do not read as the smooth moulded scoops in the sources (2 P1).

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | entrance_sw (cup at 300-640,0-160), entrance_se (400-620,30-200), architecture_close (pockets at 300,480 / 500,500 / 310,750 / 580,830), climbing_pockets (540,625 / 790,800), meadow_path (all four cups), facade_close (620,600), curb_gap (320,120 / 890,90) | Each cup interior shows about 8 distinct concentric bands of flat shade, like a terraced contour map, rather than a continuous darkening into the cup. The steps are plain at close range and still show at mid range (meadow_path, curb_gap). In the sources (front: pockets at 590,240 / 830,250 / 920,470; oblique: 420,390 / 600,580; top) the cups are smooth, continuously shaded scoops with no rings. | Cup colour is set per ring as 8 discrete shades (-10% per step) without interpolation across the ring, so each ring renders as a flat annulus. The ring count is too low for the curvature to hide the steps. | Replace the stepped per-ring shade with one continuous gradient: interpolate vertex colours, or use a radial ramp sampled per vertex with at least 16 rings or a smoothstep, and cap the total darkening at the measured interior/band ratio (about 0.72-0.76). Check again at entrance_se and climbing_pockets. |
| 2 | P1 | climbing_pockets (dark "V" at 540,625 and 790,780), meadow_path (640,465 / 1235,560 / 400,680), entrance_se (500,160), entrance_sw (475,80), architecture_close (520,525 / 600,830), top (pockets at 375,600 / 515,605 / 625,725) | Almost every cup has a sharp dark star or slit at its deepest point. It reads as a crack or puncture in the bottom of the pocket. No source pocket has this. | The cup rings close in a triangle fan onto one apex vertex. The normals and shading collapse there, giving a pinched, discontinuous normal (and the apex may sit below the rounded floor). | Close the cup with a small flat or spherical cap ring, not a single apex vertex. Average or weld the apex normals and keep the bottom rounded (normal equal to the cup axis). Check again at climbing_pockets and meadow_path. |
| 3 | P2 | top, glass_close, roof_skylights, front | The seafoam roof plateau is a little darker and bluer than the source (render reads as light aqua, source as pale mint-seafoam with near-white highlights). The difference is most visible on the front board. | Roof band albedo and light gain are still slightly low. | Raise the top band toward about 168/198/192 or raise the key gain slightly. Keep the contour steps between bands. |
| 4 | P2 | entrance_se (pale patch at 820-1090,0-215), architecture_close (pale band "drips" at 60-180,640-800) | Close up, some band boundaries show straight polygon facets and finger-like tongues hanging down the wall. Source band edges are smooth, gently wavy curves. | Iso-line bands are cut at mesh resolution and the relief lifts them into tongues over ridge crests. | Smooth the iso-band field (blur the meridian distance before banding) and subdivide the band edge locally. |
| 5 | P2 | top (W lobe 230-300,380-560; E tip 1100-1165,450-520), top_w crop | In plan, the shell outline is finely crinkled or torn. Source outlines are smooth with only soft lumps. | The 32 radial ridges add high-frequency noise to the silhouette when seen from above. | Low-pass the radial relief near the plan silhouette, or limit relief amplitude where the wall faces the zenith camera. |
| 6 | P2 | top, board phone-01 | Lobes taper slightly more to points than in the source (the W lobe is less blunt and rounded, the N lobe more pointed). The four-lobe starfish still reads correctly. | Lobe radius profile is a little sharp. | Widen the lobe tips by about 10%, especially the W lobe. |
| 7 | P2 | left_side, right_side, rear, rear_side foregrounds | Outer meadow beds are mostly bare dark mulch with sparse tufts. Source beds are densely planted grasses and palmetto. | Bed density was reduced to fit the GLB budget. | Add instanced clumps in the outer beds, or reuse a few clump instances. |
| 8 | P2 | facade_close, climbing_pockets, curb_gap | Holds are bright, saturated, faceted hexagonal nuts. Source holds are smaller and more muted. | Hold palette and low-poly primitive. | Desaturate about 15% and soften the hexagonal facets. |
| 9 | P2 | right_side (380,600 / 780,655), curb_gap (555,255) | The pale "volume" beside each entrance reads as a stray grey boulder stuck to the wall. | Bolt-on volume primitive in a neutral grey. | Tint it toward the band palette or shrink it. |
| 10 | P2 | entrance_sw (jamb bases at 460,800 / 1160,790) | The apron edge steps at the arch jambs, and small olive ground slivers show at both inner corners. | The tunnel floor sits under the apron, so the apron cut does not quite reach the jamb lining. | Extend the apron or tunnel floor to the jamb lining. |
| 11 | P2 | facade_close (310,520-700 sliver; 1020-1140,230-410 gash at the silhouette) | Two pockets at a lobe junction stretch into narrow slots or gashes. | Pocket aspect or tilt is at its extreme on strongly curved surface. | Clamp the aspect for pockets on high-curvature or junction seats. |

P0 count: 0. P1 count: 2. P2 count: 9.

## 3. Source conformance checklist

| Item | Status | View used | Note |
|---|---|---|---|
| Silhouette and plan: four lobes, N narrowest, W longest, soft concave bays | conforms (lobes slightly pointier, P2 #6; edge crinkle, P2 #5) | top vs source top, board phone-01 | 12-dome cross layout, bays and proportions (about 1.1 W/H) match. |
| Wall height and roll-over to plateau | conforms | front, front_corner, left_side, right_side, climbing_pockets | Near-vertical bulging walls on a tucked dark base, rolling into a lumpy plateau. |
| Contour bands: count, colours, wavy edges | conforms (faceting and drips, P2 #4; roof slightly dark, P2 #3) | front, facade_close, meadow_path, top | Deep teal/navy base through teal and aquamarine to pale mint. Edges are wavy, and bands run onto the roof margin as contour lines. |
| Pockets: size, number, distribution | deviates (finish, P1 #1 and #2) | climbing_pockets, entrance_se, meadow_path, front | Size, rounded irregular mouths, distribution on upper walls and roof margins and the crisp upper lip all match. The cup interiors are terraced and pinched. |
| Climbing holds | conforms (palette, P2 #8) | facade_close, climbing_pockets, front | Multicoloured small holds strung on route lines. Contact shadows are present and none float. |
| Skylight domes: 12, positions, large centre dome, white rims | conforms | top, roof_skylights, glass_close, aerial | 12 counted, matching the source layout (N 4, W 2, E 2, S 3, centre 1). Rims are white and seated. |
| Entrances: position in bays, arched form | conforms (threshold, P2 #10) | front, entrance_sw, entrance_se, meadow_path, aerial, rear_side | Dark arches at the foot of the bays, with hood, lining reveal and recessed doors. They have visible depth and returns. |
| Apron and curb: outline, four gaps | conforms | top (nw/sw/se crops), curb_gap, front | Quatrefoil sand apron inside a rounded sand curb, broken by four diagonal gaps. |
| Shell paths | conforms | top, curb_gap, meadow_path | Pale crushed-shell paths arrive through each gap. This is acceptable for clay. |
| Meadow beds and planting | conforms near the building / deviates in the outer beds (P2 #7) | front, top, left_side | Grass, palmetto and shrub clumps on dark mulch. |
| Trees | conforms | front, front_corner, top | Small trees in the beds and larger trees beyond. Clay low-poly crowns. |
| Ring path | conforms | top, aerial, left_side | A concrete ring encircles the beds. |
| Lawn | conforms | aerial, rear, rear_side | Lawn beyond the ring. |
| Materials hierarchy | conforms | all | Teal shell is dominant, then sand apron and curb, white rims and glass, then planting and mulch. |
| Interior (coherence only) | conforms | interior | Dark teal hall with skylight apertures matching domes, two boulder volumes and arched openings. Coherent. |

## 4. Camera validity

All 18 views are valid. The target is legible in every one, nothing is clipped and no key element is occluded. In curb_gap, a foreground tree trunk at the left covers part of the shell, but the curb gap, path and entrance are clear. The interior is dim but readable. The aerial camera is farther away and more frontal to a bay than the source oblique, but front_corner covers the oblique role correctly.
