# The Reef v009: independent RLASM v6.1 holistic review

Reviewer: independent, not the builder. I opened all three locked sources (front.png, oblique.jpg, top.jpg) and all 18 renders at full 1440x1080 resolution. I then made 2-4x crops of the top-view outline, the bay-junction walls in left_side and right_side, the front south-lobe pockets, the interior ceiling and walls, the entrance_sw jamb and the glass_close large dome. The judgement uses rendered pixels only. I did not treat the builder's measurements or notes as proof.

## 1. Verdict

**PASS_ZERO_P0_P1**: the four-lobed shell, teal-to-seafoam contour bands, cupped pockets with holds, the field of 12 rimmed skylights, the four arched bay entrances, the apron and curb with four diagonal gaps, and the meadow ring setting all match the locked sources. The v008 pocket-shading defects (stepped ring shades and a dark centre slit) no longer appear in any view, and the only defects left are polish.

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| — | P0 | — | None found. | — | — |
| — | P1 | — | None found. In front, front_corner, architecture_close, facade_close, climbing_pockets, entrance_sw/se, curb_gap and meadow_path, each cup darkens smoothly from mouth to floor. No stepped rings and no centre slit appear anywhere. | — | — |
| 1 | P2 | left_side (x≈540–620, y≈420–560), right_side (x≈540–600, y≈440–560), front_corner bay walls | Some pockets on the concave bay walls next to the lobe junctions read as narrow slashes or fins with a sharp folded lip, not round cups. Visible in 3x crops; in the whole view they pass as foreshortened pockets. | The pocket stamp sits on a saddle with high curvature, so the cup mouth tears into a sliver at grazing angles. | Keep pocket centres a minimum distance from bay saddle lines, or clamp mouth eccentricity on surfaces with high Gaussian curvature. |
| 2 | P2 | top (NW bay, north-lobe west flank, SE bay) | At the roll-over edge, the plan outline is slightly ragged and stepped. The source top shows a soft, smooth outline. | Relief noise reaches the silhouette ring. | Fade the relief amplitude toward the outermost silhouette ring, or smooth the outline normals. |
| 3 | P2 | top, roof_skylights, front | The roof contour lines are fainter and fewer than in the source. The render shows about 2–3 soft tonal steps on the plateau; the source top/front show several crisp mint contour lines. | Roof band colours are close in value. | Widen the value step between the two or three palest roof bands. |
| 4 | P2 | entrance_sw (x≈445–475, y≈785–815), entrance_se (x≈430–450, y≈785–800) | A tiny olive-green wedge of ground plane shows between the apron edge and the base of the arch reveal on one jamb. | The apron polygon stops just short of the reveal return at the jamb foot. | Extend the apron under the reveal by about 0.1 m, or cap the reveal floor. |
| 5 | P2 | interior (ceiling x≈620–820, y≈320–360) | Small crumpled creases on the underside of the ceiling. | The inner offset surface folds where roof relief is strong. | Smooth or clamp the inner offset under strong relief. |
| 6 | P2 | entrance_sw (bottom-right, x≈1060–1260, y≈1010–1080) | A tan curb-end fragment is cut by the camera near plane at the frame edge. | Camera is too close to the curb end. | Pull the camera back slightly or nudge the near clip; the target is unaffected. |
| 7 | P2 | glass_close (large dome) | A horizontal horizon-reflection streak crosses the large dome. It reads as a seam at close range. | Reflection of the environment horizon on the glass. | Optional: raise roughness slightly on the dome glass. |

## 3. Source conformance checklist

| Item | Status | View(s) used and evidence |
|---|---|---|
| Silhouette and plan: four lobes | conforms | top vs source top. N, E, S and W lobes with soft concave bays. Measured from the centre dome, the lobe reaches normalise to W 386 : E 343 : N 289 : S 357, against the source's 383 : 347 : 308 : 347. West is longest and north is narrowest, as in the source. |
| Lobe relative sizes and bays | conforms | top, aerial, rear_side. The bays are rounded concave scallops matching the source. The outline is slightly ragged at the edge (P2 #2). |
| Wall height and roll-over to the plateau | conforms | front, left_side, right_side, rear, facade_close. Near-vertical bulging walls with a darker base that tucks in slightly, rolling over into a lumpy plateau. The wall-to-plateau proportion matches source front and oblique. |
| Contour bands (count, colours, wavy edges) | conforms on the walls; the roof deviates slightly (P2) | front, facade_close, meadow_path. Five or six wavy bands on the walls run from dark navy-teal at the base through teal and aquamarine to pale mint. The roof contour lines are fainter than in the source (P2 #3). |
| Pockets (size, number, distribution) | conforms | front, front_corner, architecture_close, climbing_pockets, facade_close. Rounded cups of mixed sizes, spread over all lobes, including small dimples near the roof edge as in the source. They have real depth, smooth darkening and no slit. Some saddle pockets are sliver-like (P2 #1). |
| Climbing holds | conforms | facade_close, climbing_pockets, entrance_sw/se. Small multicoloured faceted holds sit on the surface with contact shadows. No floating holds were seen. |
| Skylight domes (count 12, positions, large central dome, rims) | conforms | top, roof_skylights, glass_close. Exactly 12 domes. Each source dome, mapped about the centre dome at a scale of 1.27, lands on a render dome within about 15 px. The large central dome is present, and every dome sits on a white rim. |
| Entrances (position in the bays, arched form) | conforms | front, left_side, right_side, rear, aerial, entrance_sw, entrance_se, meadow_path. There are four dark arched cave-like entrances, one at the foot of each bay. Each has a visible reveal or return and recessed double doors. |
| Apron and curb (outline, four gaps) | conforms | top, front, curb_gap, climbing_pockets. A sand apron follows the shell outline inside a low rounded sand curb. The curb breaks into four lobe segments, with gaps at the NE, SE, SW and NW diagonals. |
| Shell paths | conforms | top, curb_gap, meadow_path, aerial. White paths arrive diagonally at each curb gap and run out to the ring path. |
| Meadow beds and planting | conforms | top, front, left_side, curb_gap. Grasses, palmetto-like spiky clumps and shrubs on dark brown mulch beds between the apron and the ring, and beyond the ring. |
| Trees | conforms | front, aerial, rear_side. Small low-poly trees scattered in the beds and on the lawn, comparable to the source's scattered small trees. |
| Ring path | conforms | top, aerial, left_side. A concrete ring concentric with the shell, about 45 m across by scale against the 30 m shell. |
| Lawn | conforms | front, aerial, rear_side. Green lawn beyond the ring. |
| Materials hierarchy | conforms | all. The teal-banded shell dominates; then the sand apron and curb, the white paths, the grey concrete ring, dark mulch with green planting, and lawn. Domes are grey glass on white rims. |
| Interior (coherence only) | conforms | interior. A bouldering hall lit through the skylight oculi, with teal boulder forms, holds on the walls and arched entrances from inside. Minor ceiling creases (P2 #5). |

## 4. Camera validity

All 18 views are valid. In every whole-envelope view (front, front_corner, aerial, top, left_side, right_side, rear, rear_side) the full shell, apron and ring setting are framed with no clipping or occlusion. All detail views keep their target legible:

- curb_gap has a foreground tree trunk at the left edge that does not block the gap or the entrance.
- entrance_sw has a near-plane cut on a curb end at the lower-right frame edge (P2 #6), away from the target.
- interior is dark but legible.

No view is invalid.
