# Independent holistic review: The Reef (climbing_wall_building / variant_3), clay v006

Reviewer: independent RLASM v6.1 holistic reviewer. I did not build this candidate.
Method: I opened all three locked sources and all 18 renders at full resolution, plus the 4 phone boards. I also made enlarged crops of the pocket rims, entrance hoods, wall-band value profile, top plan and interior ceiling. Judgements are based on rendered pixels only. The builder's notes and smoke counts were not taken as proof. Colour values below are 7x7 mean RGB samples taken from the PNG/JPG pixels.

## 1. Verdict

**VISUAL_REWORK_REQUIRED.** Plan, skylights, entrances, apron, curb gaps, paths and ring path all match the locked sources, and I found no P0. Four P1 defects remain on the identity-critical shell surface:
- the pockets read as soft teardrop smears rather than the source's crisp round cups
- the pocket rims render as serrated or torn tessellation
- a pocket collides with a kinked entrance hood
- the wall bands go dark immediately below the roll-over, which leaves a pale "lid" on a dark-teal body instead of the source's aquamarine upper walls

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | front, front_corner, facade_close, meadow_path, climbing_pockets, architecture_close, top | **Pocket form and legibility do not match the source.** In the source, each pocket is a crisp round or oval cup with a full rim all round, including a lit lower lip (e.g. source front S lobe at 515,435 / 610,435 / 650,525). Pockets also sit on the roll-over shoulder itself and well down into the deep-teal base band. In the render, each pocket is a dark upper crescent that fades into a long soft smear running 1.5-2.5x the mouth height down the wall. It has no lower rim, so it reads as a drip or gouge (facade_close 240-300,250-520 and 340-460,400-640; meadow_path 170-320,370-540; climbing_pockets 740-880,220-420). At board and front scale the pockets read as faint notches, much weaker than the source's dominant cratered texture. The deep-teal lower band of the S lobe face is almost bare (front 560-900,700-850). The shoulder roll-over carries none, because of the 0.6 m-below-roll-over rule, whereas the source has many on the shoulder (source front 335,285 / 440,320 / 205,312). The locked top shows about 15 legible shoulder dimples (src top 430,220 / 600,200 / 330,460 / 580,640 / 775,465 ...). Render top shows none legible. | The dish "eases out flat across the lower floor" with no lower lip, so the lower half has no silhouette or terminator. The roll-over exclusion band is too wide. Shoulder dimples are too shallow to register. | Give each dish a defined lower lip: end the ease-out at about 0.9 of the mouth radius with a convex rim bead so the lower lip catches the key light. Cap the dish's vertical extent at about 1.2x its width. Allow pockets on the roll-over shoulder and in the deep-teal base band, matching the source positions. Deepen the source-located roof-shoulder dimples to read at top-view scale, and add the visible ones beyond five. Re-render front, oblique and top and compare pocket legibility side by side. |
| 2 | P1 | entrance_se, entrance_sw, curb_gap, facade_close, architecture_close, front (560-700,700-760) | **Serrated, torn pocket rims.** In entrance_se (430-670,280-500) the upper lip is a regular saw-tooth "bottle-cap" edge. In entrance_sw (380-660,0-280) the rim has spiky shards and ragged hair-like slivers, with a smeared dark blob. curb_gap (860-980,170-230) and facade_close (590-780,165-260) show jagged faceted lips. These are hard, noisy edges on a surface that should read as smooth moulded fibreglass. | The 18 cm overhang plus 20 cm undercut is built on locally subdivided faces whose ring vertices alternate in and out, so the undercut lip folds over itself. The -6/-12/-20% shade steps then land on alternating triangles. | Build the lip from a single smoothed ring that is monotonic in radius, with no per-vertex alternation, at no fewer than 64 segments. Clamp the undercut so the lip never self-overlaps. Blend the shade grade by distance-from-mouth rather than per face. Verify at entrance_se and entrance_sw distances. |
| 3 | P1 | entrance_se, curb_gap, right_side, rear, left_side | **Entrance hood kinked and colliding with a pocket.** On at least one bay entrance (entrance_se and curb_gap; also visible in right_side 460-520,590-660, rear 500-560,580-650 and left_side 490-530,580-650), the arched surround steps out into a second lower shoulder on its left jamb, so it reads as a folded flap or double arch. A wall pocket's bowl overlaps the hood: the arch frame runs straight across the pocket dish (entrance_se 470-690,320-500). Source entrances are clean, soft cave mouths cut into the shell with no competing elements. | The pocket exclusion near entrances is too small. The hood mesh is deformed by the pocket displacement, or vice versa, so two features occupy the same surface. | Make the pocket exclusion radius around each entrance at least the arch half-width plus 1.5 m. Rebuild the hood as one continuous, symmetric arch profile. Re-check all four bay entrances in close views. |
| 4 | P1 | front, front_corner, aerial, rear_side, left_side, right_side, board phone-01 | **Wall band value hierarchy is wrong: a pale lid on a dark body.** Source S lobe (front, x=560): pale mint at the roll-over (185,212,214), then aquamarine (105,178,182) for roughly the upper 40% of the wall, then teal (0,135,149), with deep teal (1,65,78) only in the lower third. Render S lobe (front, x=700): greyed seafoam roof (131,169,164) that stops at the roll-over, then directly dark teal (2,96,99) with no aquamarine wall band. The roof plateau is also greyed and darker than the source seafoam: (142,170,166) against (174,203,205). Side by side on phone-01, the source shell reads light aquamarine with a dark base, while the render reads as a two-tone flat lid over dark teal walls. | Band thresholds are measured on the roof, so the first wall band already starts at teal. The roof and upper-band albedos are still desaturated and grey. | Move the band breaks down the wall so the roll-over and upper wall carry seafoam and then aquamarine, about 35-45% of wall height. Reserve deep teal for the lower third. Raise roof/seafoam albedo toward the source mint and add saturation (target around 175,205,205 under neutral key). Re-sample the same vertical profile against the source. |
| 5 | P2 | front, front_corner, top, curb_gap | Apron and curb read as dull khaki-olive (133,121,96) rather than the source's warm sand (186,151,124). Partly a lighting difference, but the hue is visibly greener. | Apron albedo too low and too grey. | Warm and lighten the apron and curb albedo. |
| 6 | P2 | top, left_side, right_side, rear, aerial | Meadow beds read as bare brown mulch with straw-tan tufts. The source beds are dense yellow-green grasses and palmetto clumps with little mulch showing. | Sparse scatter; tan grass albedo dominates. | Raise bed density and shift the grass mix toward yellow-green, with more palmetto fans. |
| 7 | P2 | glass_close, roof_skylights, front | The roof plateau is smoother than the source's lumpy hummocked roof. Undulation is present but weak. | Hummocks clamped. | Allow slightly more amplitude on the outer roof. |
| 8 | P2 | top | Lobe tips are a little more tapered and the bays a little deeper than the source. The W lobe is less blunt, so the apron reads wider in the bays. | Plan spline tension. | Fatten lobe tips and the W lobe slightly. |
| 9 | P2 | top | The outer wall rim seen from above is crumpled and notched (east and south lobe edges). | Pocket mouths on the silhouette plus wall noise. | Smooth the silhouette band after fix #1. |
| 10 | P2 | front, rear, facade_close | Holds cluster in patches, leaving large bare wall areas. The source spreads holds evenly over every lobe. | Placement mask. | Even out the distribution. |
| 11 | P2 | interior | Pinched creases on the ceiling (650-830,320-345). The small skylight reveals read as flat grey discs, not openings to sky. | Ceiling offset artefact; reveal shading. | Relax the ceiling mesh; lighten the small reveals. |
| 12 | P2 | entrance_sw, entrance_se | A visible seam or step line where the apron slab meets the tunnel floor (entrance_sw 460-1180,800-830). | Two coplanar slabs. | Merge or bevel the threshold. |
| 13 | P2 | boards | `aerial` is not on any phone board. | Board layout. | Add it. |

P0 count: 0. P1 count: 4. P2 count: 9.

## 3. Source conformance checklist

| Item | Status | View(s) used / note |
|---|---|---|
| Silhouette and plan: four lobes | conforms | top vs locked top: N, E, S and W lobes are present, N is narrowest and W is longest; the N tip is offset slightly east as in the source |
| Lobe relative sizes and bays | deviates (P2) | top: lobes are slightly more tapered and bays slightly deeper (#8) |
| Overall footprint ~30 x 27 m | conforms | top: shell width-to-depth ratio is about 1.1 in both; the shell-to-ring ratio gives about 47 m for the ring |
| Wall height and near-vertical bulging walls with tucked dark base | conforms | climbing_pockets, facade_close, front |
| Roll-over to lumpy plateau about 7 m | deviates (P2) | front, glass_close: the roll-over is present but the plateau is smoother than the source (#7) |
| Contour bands: count | conforms | front: about 4 wall bands plus 3-4 roof contours, against about 5-6 in the source |
| Contour bands: colours / value hierarchy | deviates (P1 #4) | front x-profile: no aquamarine upper-wall band, and the roof is greyed |
| Contour bands: wavy edges and contour lines on roof | conforms | front, meadow_path, roof_skylights |
| Pockets: number | conforms (approx.) | front about 13 visible against about 18-20 in the source front; oblique similar |
| Pockets: size | conforms (slightly small) | front: about 1.2-1.7 m |
| Pockets: form (round cup with full rim) | deviates (P1 #1, #2) | facade_close, meadow_path, entrance_se, entrance_sw |
| Pockets: distribution (shoulder, base band, roof dimples) | deviates (P1 #1) | front, top |
| Climbing holds, multicoloured | conforms | facade_close, climbing_pockets; distribution is patchy (P2 #10) |
| Skylight domes: count 12 | conforms | top, roof_skylights: 1 large plus 11 small |
| Skylight domes: positions | conforms | top vs locked top: N lobe 4, W 2, E 2, S 3, centre 1 |
| Large central dome | conforms | top, glass_close |
| White rims | conforms | glass_close (light grey-white rims; the reveal liner is visible in interior) |
| Entrances: position in bays | conforms | front (SW and SE bays, matching the source), rear (NW and NE) |
| Entrances: arched cave form with depth/returns | conforms / deviates (P1 #3) | entrance_sw is a clean arch with a deep reveal and recessed doors; entrance_se, curb_gap and rear have a kinked hood colliding with a pocket |
| Apron outline following shell | conforms | top, front_corner |
| Curb, low rounded, sand | conforms (hue P2 #5) | curb_gap, climbing_pockets |
| Four diagonal curb gaps | conforms | top: NW, NE, SW and SE gaps at the same positions as the source |
| White shell paths into gaps | conforms | curb_gap, meadow_path, top, aerial |
| Meadow beds, grasses, palmetto, shrubs on dark mulch | conforms (density and colour P2 #6) | top, left_side, right_side |
| Small trees in beds | conforms | front, aerial; north-bed trees are clear of the rear sight line in rear and rear_side |
| Ring path about 46 m | conforms | top, aerial |
| Lawn and trees beyond | conforms | aerial, rear_side |
| Materials hierarchy (shell / apron / curb / paths / mulch) | deviates | the shell value hierarchy is P1 #4; apron hue is P2 #5. The order apron < curb < paths in lightness is correct |
| Interior (coherence only) | conforms | interior: hall, bouldering blocks, arched entrances and skylight reveals are coherent; P2 #11 |

## 4. Camera validity

All 18 views are valid. Each target is legible, and no asset is clipped in a way that hides the subject.
- left_side and right_side: foreground trees partly overlap one lobe, but the shell, entrances and bands stay legible.
- curb_gap: multi-stem tree trunks cover the left 12% of the frame; the gap, path and entrance are clear.
- meadow_path: a tree crown intrudes at the top-right; the subject is clear.
- interior and entrance_se: low key, but legible.

No view is invalid.
