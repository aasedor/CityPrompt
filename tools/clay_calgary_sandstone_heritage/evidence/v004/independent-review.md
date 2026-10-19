# Independent holistic review: sand v004 (RLASM v6.1 architectural clay)

Reviewer: independent; I did not build this. I judged only rendered pixels against the locked source pixels. I opened every render (18), all three sources and all four phone boards at full resolution, and made zoomed crops in a new scratch folder (`rev-v004-crops-976011388`).

## 1. Verdict

**VISUAL_REWORK_REQUIRED**: the v003 clock-tower P1 is substantially fixed, but two clearly visible fidelity defects remain. On every pavilion face the window tiers are shifted up one storey, so there is no third-floor small-arch arcade above the giant arches. The north and west sidewalks also have no street trees, although the governing top source shows trees on all four frontages.

Counts: P0 = 0, P1 = 2, P2 = 11

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | front, front_corner, architecture_close, gables_pinnacles, rear_north, right_side, east_side, left_side, rear | On every corner pavilion's outward faces, the giant round arches sit on the **third** floor, directly under the eave (rear_north crop: arched heads y≈160–310 with small 3-arch groups beside them, not above). Below them, the second floor has tall **rectangular** lights joined to the arches by colonnettes, and the first floor has a separate row of paired rectangular windows. In the source (front SE and SW pavilions, oblique SE and SW pavilions) the order is different. A giant round-arched arcade rises from above the basement: rectangular first-floor lights with round-arched second-floor heads. Above it, under the cornice, runs a continuous third-floor arcade of 4–5 small arches. The pavilions are the most prominent masses in the source front, and their arcade rhythm reads as a different elevation. (The wings are correct: paired rectangular, then arched, then small arcade.) | The pavilion facade module stacks the "giant bay" one storey too high and reuses the wing's small-arcade tier only as side fillers, not as a full-width top tier. | On all four pavilions' outward faces: drop the giant arcade by one storey, so the rectangular lights are on the first floor and the round-arched heads on the second (springing at the current second/third string course). Replace the pavilion's first-floor paired-rectangle row with the giant-arcade lower lights. Then fill the whole third-floor width under the cornice with a continuous arcade of 4–5 small round arches on colonnettes, matching the wing arcade module. Keep the storey count and string-course heights unchanged. |
| 2 | P1 | top, left_side, rear, rear_north, aerial, rear_side | Street trees stand only on the south and east sidewalks. The west sidewalk (top render, x≈65–190) is empty, and so is the north sidewalk (rear_north, rear, and aerial top-right edge). The top source shows two trees on each of the block's own four sidewalks (north at x≈450 and 725; west at x≈270 near y≈355 and 630; south and east also two each), with more on the opposite kerbs. The two unseen fronts read as an unplanted service edge, which the source does not show. | The tree scatter was placed only along the frontages visible in the front and oblique sources. | Add 2 trees to the north sidewalk (flanking the north cross gable, about a quarter and three-quarters of the way along the frontage) and 2 to the west sidewalk (flanking the west cross gable), using the same tree asset, spacing, kerb offset and ground contact as the south and east trees. Re-render top, aerial, left_side, rear and rear_north. |
| 3 | P2 | right_side, east_side, front, rear_north | The tower is much improved but still slightly low against source front. In the near-orthographic right_side, the clock-face centre is about 1.1× the pavilion-apex height (source front against the NE pavilion: about 1.4×), the crown is about 1.3× (source about 1.7×) and the spire tip is about 1.7× (source about 2.1×). In right_side the bottom of the clock face is level with the pavilion finials, and in front the clock sits below the near SE-pavilion finial. | Shaft below the clock stage still short by about 3–4 m. | Optionally lengthen the shaft below the clock-stage string course by about 3–4 m, so the whole clock stage clears the pavilion finials in every view. |
| 4 | P2 | right_side, east_side, front_corner | The tower shaft is mostly blank. The 4-lancet cluster takes about 12% of the tower height, against about 24% for the tall lancet arcade in the source. | The lancets are modelled at standard window height. | Stretch the east cluster and the N/S pairs to about 2× their height, as one tall arcade under the clock-stage corbel table. |
| 5 | P2 | architecture_close, gables_pinnacles, front | The pavilion gables are lower and broader than the source's tall, steep coped gables, which nearly reach the pyramid apex and carry roundels. | Gable pitch and height parameters. | Raise the gable apex by about 30% and add a roundel disc. |
| 6 | P2 | all | The sandstone is a desaturated khaki (sampled about 110,97,72 and 118,104,80) against the source's warm golden ochre (about 131,99,60 and 141,108,64). The copper reads pinkish salmon (about 159,135,123) against the source's red-brown copper (about 148–172,114–130,95–105). | Palette tokens. | Shift the wall base colour toward about (140,105,62), and the copper toward about (160,115,90). |
| 7 | P2 | facade_close, glass_close, portal_arch | No rock-faced or rusticated differentiation of the basement; walls are flat with faint coursing lines. Acceptable for clay. | Clay simplification. | Optional: a slightly darker basement band with deeper joint lines. |
| 8 | P2 | front | A low, close camera gives strong three-point (worm's-eye) convergence; the source front is an eye-level, corrected two-point view. Two large tree canopies hide the SE pavilion corner at the first and second floors. | Camera height and FOV. | Move the camera back, raise it slightly, narrow the FOV, and keep the verticals near vertical. |
| 9 | P2 | top | Framing is tight: the north and south pavilion edges are within about 8 px of the frame, and the north and south streets are out of frame (the source top shows streets and neighbouring blocks on all four sides). | Orthographic scale. | Increase the ortho extent about 15% so all four streets are visible. |
| 10 | P2 | east_side | The spire's finial tip touches row 0 (it is clipped at the top edge); the spire cone itself is fully in frame. | Camera re-aim left no headroom. | Tilt or raise the camera about 3% for headroom. |
| 11 | P2 | aerial | The building fills only about 35% of the frame width; legible but distant. | Camera distance. | Dolly in about 25%. |
| 12 | P2 | clock_tower, east_side | The clock faces are plain white discs with no stone frame or bezel ring; the source has framed dials. | Simplified dial. | Add a thin stone surround ring. |
| 13 | P2 | portal_arch | A tree canopy covers most of the balcony above the portal; the portal itself is clear. | Tree placement near the camera axis. | Shift the camera or that tree about 2 m. |

## 3. Source conformance checklist

| item | status | view used |
|---|---|---|
| Silhouette | conforms. A square block with four pyramid-roofed corner pavilions and a dominant spired clock tower on the east front. | front_corner vs oblique; right_side; aerial |
| Storey count | conforms. Basement plus 3 full storeys plus gable attic, on wings and pavilions. | rear_north, facade_close, right_side |
| Plan | conforms. A square footprint with a central square court, cross gables at mid-wing on N/S/W, and the tower at mid-east. | top vs top |
| Court and pavilion projection | conforms. The court is open, its inner walls are fenestrated and it has mid-side inner hips. The pavilions step forward of the wing planes. | roofs_court, top, rear_north |
| Sandstone coursing | deviates (P2). Coursing lines are faint, the palette is desaturated and the basement is not rusticated. | glass_close, facade_close |
| Window tiers: basement | conforms. Small windows. | facade_close, rear_north |
| Window tiers: paired rectangular | conforms on wings; deviates on pavilions (see #1). | facade_close, rear_north |
| Window tiers: round-arched | conforms on wings (second floor); deviates on pavilions, where the giant arches are on the third floor (#1). | rear_north, front |
| Window tiers: small arcades | conforms on wings (third floor); deviates on pavilions, where the tier above the giant arches is missing (#1). | facade_close, rear_north |
| Opening depth and reveals | conforms. Projecting sills, arch surrounds and recessed glazing; the interior shows a deep reveal. | glass_close, interior, front crop |
| String courses and eave cornice | conforms. | facade_close, glass_close, architecture_close |
| Gables and pinnacles | conforms with a P2 (gables low and broad). Coped gables with apex and foot pinnacles on outward pavilion faces and wing cross gables. | gables_pinnacles, architecture_close |
| Roofs: wing hips | conforms. Steep slate hips. | roofs_court, aerial |
| Roofs: pavilion pyramids | conforms. Steep slate pyramids with copper finials. | front_corner, top |
| Roofs: cross gables | conforms. | top, rear_north, left_side |
| Portal | conforms. A deep round-arched vaulted portal with steps and a balustraded balcony at the SW pavilion; a second portal and balcony at the tower foot. | portal_arch, front, right_side |
| Clock tower: projection | conforms. Projects from the mid-east wing. | top, right_side |
| Clock tower: lancets | conforms with a P2 (short). A 4-lancet cluster on the east face and pairs on the N and S faces. | east_side, rear, front_corner |
| Clock tower: clocks | conforms. Dials on four faces, above the clock-stage string course. | clock_tower, front_corner |
| Clock tower: belfry | conforms. A five-arch belfry arcade above the clocks. | clock_tower, east_side |
| Clock tower: turrets | conforms. Four round, corbelled corner turrets with tall copper cones. | clock_tower, front crop |
| Clock tower: spire | conforms. A slender octagonal copper spire on an octagonal base, with a finial; height to base about 1.65. | east_side, front_corner, top |
| Streets and trees | deviates (P1 #2). There are streets on all four sides, but trees only on the S and E sidewalks. | aerial, top, left_side, rear |
| Materials hierarchy | conforms with a P2 (hues). Buff walls, lighter trim, dark slate, copper accents, dark glazing. | all |

## 4. Camera validity

No view is invalid: in every view the target is legible, unoccluded and inside the frame. Minor issues, all P2:
- **front:** strong worm's-eye perspective, and trees partly hide the SE pavilion corner (#8).
- **top:** framed too tight, so the north and south streets are cut off (#9).
- **east_side:** the finial tip touches the top edge (#10).
- **aerial:** the building is small in the frame (#11).
- **portal_arch:** a canopy hides the balcony (#13).
- **rear_north:** the tower top is cut off, but the tower is not the target of that detail view, and the north facade itself is legible.
- **interior:** dim but legible, and shows the window reveal.

## 5. Previous-version (v003) findings: are they resolved in the pixels?

| v003 finding | status in v004 pixels |
|---|---|
| Tower top cornice below the corner-pavilion pyramid finials | **Resolved.** The crown clears the pavilion finials in every view: right_side crown at y≈378 against finials at y≈465; east_side crown at y≈225 against finials at y≈420; front crown above the near SE finial. |
| Clock faces below the pavilion apexes | **Resolved in elevation, with a thin margin.** east_side clock centre at y≈340 against finials at y≈420–430; right_side at 448 against 465 (the dial's lower edge is level with the finials). In the low front camera the clock still projects below the near SE finial (perspective). Residual P2 (#3). |
| Whole tower about 1.3× pavilion height against about 2× in source | **Largely resolved.** Now about 1.7× (right_side 1.66, east_side 1.68), against about 2.1× (NE pavilion) or 1.4× (SE pavilion) in the source front. Residual P2 (#3). |
| Broad four-sided pyramid spire, height:base about 1.0 | **Resolved.** An octagonal copper spire on an octagonal stone base, with a finial; height to base about 1.65 (east_side) to 1.9 (front). |
| Builder claims: 4-lancet cluster on the east face, pairs on the N and S faces | **Verified**: east_side, rear, front_corner. The lancets are short (P2 #4). |
| Builder claims: five-arch belfry above the clocks, four corner turrets with taller copper caps | **Verified**: clock_tower, east_side. |
| Builder claims: east_side, clock_tower, front and front_corner re-aimed so the whole tower and spire stay in frame | **Verified** for clock_tower, front and front_corner. In east_side the spire cone is fully in frame but the finial tip touches the top edge (P2 #10). |
