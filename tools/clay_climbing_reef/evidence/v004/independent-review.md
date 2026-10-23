# The Reef v004 — independent RLASM v6.1 holistic review

Reviewer: independent (not the builder). Basis: the pixels of all 18 renders at full resolution, the 4 phone boards, and the three locked sources (front.png, oblique.jpg, top.jpg). I did not use the builder's notes, counts or metadata as proof. I checked the plan by overlaying the render top-view silhouette, scaled to the source bbox, onto source top.jpg. I checked pocket depth with vertical luminance profiles through pocket mouths in architecture_close, front and roof_skylights, compared with the same profiles through source oblique pockets.

## 1. Verdict

**VISUAL_REWORK_REQUIRED** — The envelope, plan, domes, entrances, apron, curb and paths now match the sources well. Two P1s remain: the climbing pockets are still hard-edged elliptical cut-outs, not soft eroded rock pockets, and the meadow beds are sparse and lack the small in-bed trees that appear in every source view.

Counts: **P0 = 0, P1 = 2, P2 = 8**

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | facade_close, architecture_close, climbing_pockets, meadow_path, front, front_corner, roof_skylights | Each pocket mouth is a crisp, mathematically clean ellipse. The luminance profile steps in a single 6 px sample at the rim (architecture_close x=720: 156 → 124; x=790: 137 → 69; front x=790: 136 → 87), so the 7 cm fillet is not visible at any rendered scale. The interior is a flat tinted cup that brightens evenly downward, with no brow or lip. Several mouths are tall 2:1 slots (facade_close 255-350 × 210-395 and 320-420 × 395-610; front 900-935 × 655-745; climbing_pockets 740-880 × 385-655). On the pale roll-over bands the interior contrast is only about 20 levels (architecture_close top-centre pocket 124-136 against 156/139 surround), so those pockets read as flat painted ovals or near-convex blisters. In the source, the pockets are rounder (about 1.0-1.4:1), with soft scooped edges, an overhanging upper brow with deep shadow under it, and a highlighted lower lip that blends into the wall over a broad gradient (oblique x=470 falls smoothly 150 → 96 over about 50 px). The count and distribution now match (about 14-16 in the front faces), but the form and edge still read as cut portholes, not rock pockets. | Pockets are made by a boolean or ellipse cut with a uniform inset lining. The fillet is too small relative to the 0.6-1.6 m mouth to survive rendering. There is no asymmetric brow or depth falloff. Aspect ratio is not capped. | Rebuild each pocket as a displaced dimple, not a cut. Use a smooth depth falloff over the outer 30-40% of the mouth radius (about 0.2-0.4 m, not 7 cm). Make the profile asymmetric, with the deepest point offset upward under a 0.10-0.15 m overhanging upper brow and a soft rolled lower lip. Cap mouth aspect at ≤1.4:1, keeping at most 2-3 elongated ones. Deepen roll-over pockets so their upper interior sits ≥40 levels below the surrounding band in the front and front_corner lighting. Re-check with the same luminance profiles: there should be no single-sample rim step, and the profile should show a gradual entry. |
| 2 | P1 | front, front_corner, aerial, top, left_side, right_side (vs source front, oblique, top) | The ring of meadow beds between the curb and the ring path is low, evenly spaced spiky tufts and a few round shrubs, with about 40-50% bare brown mulch showing (top view). In-bed small trees appear only in the north beds (top.png about (290,70) and (1160,80), plus one beside the N path in rear_side). The south, west, east, SW and SE beds have none. The source top shows about six small trees spread through all beds (NW, N, W, SW, S/SE and E). The source front and oblique each show prominent foreground trees in the beds on both sides of the S lobe (front about (60-190, 510-700) and (900-1010, 430-600); oblique about (170-300, 670-800) and (950-1060, 570-700)). The source beds are dense, tall golden grass with palmetto clumps and shrubs, with mulch visible only in gaps. On phone-01, the render foregrounds are uniform tuft carpets with no trees, where both locked views show framing trees. | The meadow scatter density and height are too low. Tree placement was limited to the north beds and the area beyond the ring. There is no palmetto or tall-grass mix class. | Add 4-5 small multi-stem trees (about 4-6 m) in the W, SW, S/SE and E beds at the source-top positions, plus the existing N ones. Roughly double the bed scatter density. Add a tall golden bunch-grass class (about 0.8-1.2 m) and fan-leaf palmetto clumps, so mulch shows only in small gaps (≤20% in the top view). Re-render front and front_corner and compare against the phone-01 source panels. |
| 3 | P2 | front, right_side, rear, facade_close | Contour bands are near-parallel stripes of fairly even width with gentle waves, which reads as a layer cake. In the source, the band edges wander strongly, with tongues and dips: the mint/aqua bands dip deep into the S-lobe face and rise over the shoulders, and band widths vary 2-3×. | The band function is height plus a low-amplitude wave, not tied to the surface relief. | Increase band-edge amplitude and drive it from the local surface undulation and lobe curvature. Vary band thickness per lobe. |
| 4 | P2 | front, front_corner, glass_close, roof_skylights | The roof plateau and roll-over are smoother than the source. The source shows distinct hummocks, ridges running from the plateau down the shoulder between pockets, and folds at the lobe tips. The render shows soft tonal blotches and only slight silhouette lumps. | The "calmer roof lumps" change went too far, and there are no shoulder ridges. | Restore about 0.2-0.35 m hummock relief on the plateau. Add 3-5 soft ridges per lobe shoulder that run between pockets. |
| 5 | P2 | front, right_side, rear, facade_close, climbing_pockets | Holds are uniformly saturated rainbow polyhedra set in rigid, evenly pitched vertical bead strings, which read as streaks at whole-envelope scale. Source holds are smaller, more muted (many dark or neutral) and set in looser, irregular clusters. | Route generator uses a fixed pitch and lateral jitter that is too small. Palette is fully saturated. | Jitter the pitch ±40% and the lateral position by ±0.3 m. Mix in about 40% dark or neutral holds. Reduce the mean size by about 20%. |
| 6 | P2 | entrance_sw, entrance_se, meadow_path, curb_gap | The arch reveal shows visible straight polygon facets along its outer silhouette, for example entrance_se right jamb at about x=1100-1140 and y=480-650. | Reveal outer edge is under-tessellated or flat-shaded despite the 48-segment lining. | Smooth-shade the reveal and raise the outer-edge segment count. |
| 7 | P2 | entrance_sw, entrance_se, curb_gap, meadow_path | A thin orange or tan line runs across the apron about 0.3 m in front of every entrance threshold. It reads as a seam or z-fighting strip. | Threshold plate edge or coplanar apron patch. | Remove the strip or merge the threshold into the apron surface. |
| 8 | P2 | all exterior views | The palette is slightly greyer and duller than the source. The roof mint is about (148,170,166) against the source's bright mint and aquamarine. White shell paths read as flat light-grey concrete with sparse specks. The interior large skylight disc shows a V-notch artefact at its top (interior about (740,15)). | Clay lighting/exposure; path material too grey; skylight shaft geometry. | Lift the roof and upper band values and saturation slightly. Whiten the shell-path base colour. Fix the skylight-shaft notch. |

## 3. Source conformance checklist

| Item | Status | View(s) used / note |
|---|---|---|
| Silhouette and plan — four lobes | **conforms** | top vs top.jpg overlay. The render outline lies on the source shell edge within a few px around the whole perimeter. |
| Lobe relative sizes (N narrowest, W longest) | **conforms** | top, aerial. N lobe narrowest, W longest; bbox W/H ≈ 1.11, same as source. |
| Bays (soft concave) | **conforms** | top overlay. Bay depth and curvature match; NE and SW bays at most marginally deeper. |
| Wall height ~5 m and roll-over to ~7 m plateau | **conforms** | front, left_side, meadow_path, climbing_pockets. Near-vertical bulging walls roll into the plateau. |
| Tucked dark base | **conforms** | facade_close, climbing_pockets. Darkest teal band with a slight inward curve at the apron contact. |
| Contour bands — count | **conforms** | front, facade_close. 6 wall bands plus roof tones, against about 5-6 in the source. |
| Contour bands — colours | **conforms (minor deviation)** | Deep teal → teal → aquamarine → mint ordering is correct; overall slightly duller (P2 #8). |
| Contour bands — wavy edges / roof contour lines | **deviates (P2)** | front, right_side: too parallel and regular (P2 #3). Roof contour zones are visible in top and glass_close. |
| Pockets — number and distribution | **conforms** | front about 15-16 in W/S/E faces (source about 15); front_corner about 12-14 (oblique about 12). Upper wall and shoulder weighted; none at the base or in creases. |
| Pockets — size | **conforms** | front: about 1.2-2 m mouths, as in the source. |
| Pockets — form, edge and depth read | **deviates (P1 #1)** | facade_close, architecture_close, climbing_pockets: crisp elliptical cut edges, 2:1 slots, no brow or lip, weak contrast on pale bands. |
| Climbing holds | **conforms (rhythm P2)** | Present and multicoloured on all faces; rigid vertical strings (P2 #5). |
| Skylight domes — count 12 | **conforms** | top, roof_skylights, front: 1 large plus 11 small. |
| Skylight domes — positions | **conforms** | top overlay: each dome lands on its source dome within about 10 px. |
| Large central dome | **conforms** | top, glass_close. |
| White rims | **conforms** | glass_close: continuous white rim seated on the roof, with contact shading and no gap. |
| Entrances — position in bays | **conforms** | front (SW, SE match the source), rear and left/right sides (NE, NW). 4 in total, each at a bay foot. |
| Entrances — arched, cave-like, depth/returns | **conforms** | entrance_sw, entrance_se: deep reveal with returns, recessed doors. Facet edge is P2 #6. |
| Apron — outline | **conforms** | top: sand apron follows the shell; curb outline matches the source quatrefoil within a few px (W curb ≈ x 148 vs source ≈ 150 after scaling). |
| Curb — low, rounded, four diagonal gaps | **conforms** | top, front, curb_gap: four offset-overlap gaps at NW/NE/SE/SW, as in the source. |
| Shell paths | **conforms (finish P2)** | top, curb_gap, meadow_path: four paths from the gaps to the ring; colour too grey (P2 #8). |
| Meadow beds and planting | **deviates (P1 #2)** | top, front, front_corner: sparse tufts on mostly bare mulch; no palmetto or tall golden grass mass. |
| Trees — small in-bed trees | **deviates (P1 #2)** | top, front, front_corner: only on the N side; none in the S/W/E/SW/SE beds, which are visible in the sources. |
| Trees — beyond ring | **conforms** | front, aerial, rear_side. |
| Ring path ~46 m | **conforms** | top: ring diameter ≈ 1.57 × plan width (source ≈ 1.6×), about 46-48 m. |
| Lawn beyond | **conforms** | aerial, rear, rear_side. |
| Materials hierarchy (teal shell > white rims/glass domes > sand apron/curb > white paths > dark mulch/green planting) | **conforms** | all whole-envelope views. |
| Interior (coherence only) | **conforms** | interior: bouldering hall with holds, boulder blocks, skylight openings overhead, arched openings consistent with the exterior. Skylight notch is P2 #8. |

## 4. Camera validity

All 18 views are valid. No target is occluded, no asset is clipped beyond the intended detail framing, and every view is legible.
- front ↔ source front and front_corner ↔ source oblique are matched in azimuth and elevation (S lobe toward the camera, W left, E right). top is a true nadir matching top.jpg.
- The detail views (facade_close, architecture_close, glass_close, climbing_pockets, roof_skylights, curb_gap, meadow_path) crop the shell intentionally. Their subjects are fully in frame and in focus.
- interior is dim but legible: floor, blocks, openings and skylights all read.
- left_side, right_side and rear place the building mid-frame with the ring path and beds visible. No near-camera foliage blocks the shell.
