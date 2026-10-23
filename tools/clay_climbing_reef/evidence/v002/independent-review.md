# Independent holistic review: The Reef v002 (climbing_wall_building / variant_3)

Reviewer: independent RLASM v6.1 holistic reviewer. I opened all 18 renders at full resolution, the three locked sources (front.png, oblique.jpg, top.jpg) and the four phone boards. I judged rendered pixels only and did not use builder notes, counts or hashes as proof.

## 1. Verdict

**VISUAL_REWORK_REQUIRED**: envelope, plan, bands, skylight field, entrances, apron, curb and paths now conform, but the rounded climbing pockets, a named identity element, still read as faint soft smudges instead of the source's crisp, numerous round hollows (1 P1).

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | **P1** | front, front_corner, aerial, top, left_side, right_side, rear, facade_close, climbing_pockets, meadow_path; board phone-01 | **Pockets have lost their identity.** In the locked front and oblique views the shell is visibly pocked: about 30–35 crisp round or slightly oval hollows, roughly 1–1.5 m across, on the visible faces. Each has a sharp rim, a lit lower lip and a dark interior, and they are spread over every band, including the roof shoulders and lobe tips. Locked top also shows dents on the roof edges at about (530,270), (425,505) and (500,600). In the render envelope views the pockets are almost invisible: a dozen faint lumps on the upper bands of front and front_corner, and none on the roof in top. Up close (facade_close, climbing_pockets, meadow_path) they are shallow kidney dents with blurred, rimless edges. Their dark shading reads as smudges or stains, for example meadow_path (380–560, 410–470) and (1180–1340, 360–400), not as recessed hollows. Side by side on phone-01, the render shell reads as a smooth banded blob, not a pocked reef. | The v002 change to "fewer, smoothly dished oval/kidney hollows" overshot. Depth-to-diameter is too low and the falloff too wide, so no rim edge or lip highlight forms. The count is too low and none sit on the roof shoulders. | Raise the count to about 30–40 per visible half-envelope, spread over all bands, with 6–10 on the upper roll-over and roof shoulders (none in the bay creases). Use round to mildly oval plans 0.9–1.6 m across, about 0.35–0.5 m deep, with a tight rim radius (≤0.08 m) so each hollow shows a crisp rim line and a lit lower lip. Re-verify in front, front_corner and top at envelope scale, not just in climbing_pockets. |
| 2 | P2 | aerial, rear_side, architecture_close, left_side, right_side, rear | The world edge shows: a grey backdrop box with a visible corner kink (aerial (645,35), rear_side (740,105)) and a flat grey horizon band past the ground disc. | The ground disc and backdrop are finite and the world colour is a flat grey. | Extend the lawn plane past the horizon or fade it into a horizon gradient, and remove the visible box corner. |
| 3 | P2 | front, front_corner, curb_gap, meadow_path, rear | Mulch beds are thick extruded slabs with vertical brown sides and straight cut trapezoid ends outside the ring path (front (70,320)). The source beds are flush, with organic edges. | Beds are extruded solids with a hard boundary. | Drop the beds to about 2–3 cm, bevel or feather their edges, and round the outer bed ends. |
| 4 | P2 | top, front, aerial | Few small trees stand inside the ring. The source has several small trees inside the meadow beds near the apron (source front (90,240), (230,185), (120,620), (950,510)). There are no palmetto fan clumps, only grass tufts and round shrubs. | Planting scatter excludes trees inside the ring and has no palmetto asset. | Add 4–6 small trees in the inner beds and a simple fan-palmetto clump mesh. |
| 5 | P2 | entrance_sw, entrance_se, front, front_corner | The entrances are slightly taller than wide (about 0.8 w/h), with a proud torus rim lip. The source cave mouths are broader (about 1.1–1.4 w/h in the same roles) and flush, with no lip. | The arch profile is too narrow and has a separate rim ring. | Widen the arch about 25% at the same crown height and blend the rim into the shell. |
| 6 | P2 | front (both bays), facade_close (0–160, 800–825), roof_skylights | A thin dark seam line runs diagonally across the apron from each entrance threshold. | Apron mesh seam or threshold trim edge on the bay crease. | Merge the apron seam or hide the trim edge. |
| 7 | P2 | all whole-envelope views; top | The palette is greyer and less saturated than the source. Roof is about (150,168,165) against the source seafoam about (181–215, 206–222, 197–207). Mid-wall teal is about (24,115,116) against source (0,135,149). The detail views look dim and hazy. | Flat overcast world light and a grey tint on the band materials. | Push the roof seafoam and the mid teals toward the source values and lift the exposure on the detail cameras. |
| 8 | P2 | front, front_corner, facade_close | Holds are faceted cubes and cluster as dotted lines along some band edges and bay creases. | Holds are scattered along curves, not across the area. | Use an area-uniform scatter with rounded hold primitives. |
| 9 | P2 | interior | The left entrance tunnel sticks into the hall as a freestanding tube with its outer skin exposed. This is plausible as a vestibule but reads oddly. | The tunnel depth is longer than the shell thickness. | Trim the tunnel flush with the inner skin or wrap it in a vestibule surround. |
| 10 | P2 | curb_gap, meadow_path | The shell-path flakes are large, flat white triangles that read as scattered confetti at close range. | Flake instance scale is too large and the shape is a plain triangle. | Halve the flake scale and randomise to irregular polygons. |

Counts: **P0 = 0, P1 = 1, P2 = 9.**

## 3. Source conformance checklist

| Item | Status | View(s) used |
|---|---|---|
| Silhouette and plan: four lobes | conforms | top vs locked top, aerial, rear_side |
| Lobe relative sizes (north narrowest/shortest, west longest) | conforms. Arm ratios to the east arm: render W 1.04, N 0.84, S 0.99; source W 1.09, N 0.88, S 1.00. West is only marginally longest. | top vs locked top |
| Soft concave bays between lobes | conforms | top, front, front_corner |
| Plan extents (about 30 × 27 m) | conforms. Bounding aspect is 1.126 in the render and 1.115 in the source. | top vs locked top |
| Wall height (about 5 m near-vertical bulging walls) | conforms | front, left_side, climbing_pockets |
| Slightly tucked dark base | conforms | facade_close, climbing_pockets |
| Roll-over to plateau (about 7 m) | conforms | facade_close, architecture_close, left_side |
| Lumpy, undulating roof plateau | deviates (minor). Smoother than the source and lacks roof-shoulder pockets; the pocket part is covered by finding 1. | glass_close, roof_skylights vs locked front and top |
| Contour bands: count | conforms. About 5 wall bands plus 2–3 roof contour rings. | front vs locked front |
| Contour bands: colours (deep teal to seafoam/mint) | conforms in sequence but greyer and less saturated (P2 #7) | front, top vs locked front and top |
| Contour bands: wavy edges and roof contour lines | conforms | front, meadow_path, glass_close |
| Pockets: size | deviates. Rimless, shallow, soft dents (P1 #1). | facade_close, climbing_pockets vs locked front |
| Pockets: number | deviates. About 12 faint dents in front against about 30–35 crisp pockets in the source front (P1 #1). | front vs locked front |
| Pockets: distribution | deviates. None on the roof shoulders or lobe tips, which the source shows (P1 #1). | top vs locked top |
| Climbing holds (small, multicoloured) | conforms. Cubic and somewhat line-clustered (P2 #8). | facade_close, climbing_pockets, front |
| Skylight domes: count 12 | conforms (12) | top, roof_skylights, front |
| Skylight positions | conforms. The pattern matches the source: N tip, N pair, NW inner, W tip and inner, centre, E inner and tip, S pair, S tip. | top vs locked top |
| Large central dome | conforms | top, roof_skylights, glass_close |
| White rims (level collars, seated, no float) | conforms | glass_close, roof_skylights |
| Entrances: position at the foot of the bays (SW and SE as in source; NE and NW for coherence) | conforms | front, front_corner (SW/SE), aerial, rear_side (others) |
| Entrances: arched, cave-like form, depth and returns | conforms. Deep teal-lined tunnels with visible returns and recessed dark doors. Proportions are slightly narrow (P2 #5). | entrance_sw, entrance_se, curb_gap, meadow_path |
| Apron (sand rubber, follows outline) | conforms | top, front, front_corner |
| Curb (low, rounded, sand) | conforms | curb_gap, climbing_pockets, front |
| Four diagonal curb gaps | conforms | top vs locked top, front, rear_side |
| White crushed-shell paths arriving at the gaps | conforms. Irregular edges; flakes oversized (P2 #10). | top, curb_gap, meadow_path |
| Meadow beds (grasses, shrubs, dark mulch) | conforms. Slab edges (P2 #3); no palmettos (P2 #4). | front, left_side, curb_gap |
| Trees (small) | deviates (minor). Sparse inside the ring (P2 #4). | top, front vs locked front and top |
| Ring path (about 46 m) | conforms. About 46–47 m measured against the shell span in both. | top vs locked top |
| Lawn and meadow beyond | conforms. World edge visible (P2 #2). | front, aerial, rear_side |
| Materials hierarchy (dark base, teal walls, seafoam roof, white rims, glass, sand apron and curb, white paths, grey ring, mulch, lawn) | conforms. Palette greyed (P2 #7). | front, top, glass_close, curb_gap |
| Interior hall (coherence only) | conforms. Boulders are off the entrance axes, skylights read from below, no emitters visible. The tunnel tube intrudes (P2 #9). | interior |

## 4. Camera validity

All 18 views are valid. In every view the target is unoccluded and legible, and nothing is clipped beyond the intended framing of a detail view. Minor notes only:
- entrance_sw has a curb end-cap fragment in the lower-right foreground. It does not obscure the target.
- curb_gap crops the top of the shell by design; the curb gap, path and entrance are fully legible.
- aerial and rear_side show the backdrop box corner (P2 #2). This is not a validity failure.
