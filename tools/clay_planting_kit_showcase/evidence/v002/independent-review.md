# Independent RLASM v6.1 review: shared planting kit showcase v002

Candidate: `clay-planting-kit-showcase-clay-v002` (showcase of the shared planting kit, not a catalogue building)
Reviewer: independent. I did not build this model.

What I looked at:
- All 15 renders at full 1440 x 1080, and all three phone boards.
- The v001 renders: `eye_shrub_mass`, `eye_carpet_bed`, `eye_flower_heads`, `eye_arching_grass`, `eye_bedding_band` and `top`.
- The comparison families' planting renders: Prince's Island v003 `promenade_beds`, Halifax v003 `carpet_beds`, green bridge v003 `planting_bed`, and stepped plaza v003 `parapet_pots` and `architecture_close`.
- The planting findings in the five family reviews named in the brief, and the v001 review.

I wrote zoom crops only to the new folder `review/crops_wkhpzr/` inside the v002 folder. I also ran a luminance scan (pixels with luminance below 25-30) over every render, and I checked each dark cluster by eye. I used the build report, `planting-kit-size.json`, the GLB JSON chunk and the camera roster in `prework-manifest.json` only for sizes, instancing and camera positions. Every visual judgement comes from the pixels.

Verdict: FAIL

Counts: P0=1 P1=7 P2=12

Summary: v002 fixes four of the six v001 P1s in the pixels:
- The bedding bands and carpet bed are now flat, clipped and valley-free.
- The yarrow is a domed corymb.
- The feather-reed plumes are slim, feathery spindles.
- The clearance rule keeps every shrub off its kerb and the rail.

The grasses, daisies, salvia spikes and poppy cups are good. The B2 and B8 drifts read as planted.

But the shrub skin method still fails. It now gives perfect spheres and eggs shingled in hard, flat leaf chips over a near-black hull, so the shrubs read as topiary balls or ivy-covered boulders. That skin also turns the hydrangea body into a vertical-sided drum.

Several new modules also bring back the families' failed readings:
- The white panicle is a bumpy white cone.
- The lavender is a grey sea-urchin dome.
- The bedding cushions are gumdrops with sprinkles.
- The bougainvillea `wall_drape` and its parapet cascade read as a padded green quilt with pink balloon patches. It also has true-black slits where the bract shell meets the canopy shell.
- Two pots interpenetrate.

## 3. Findings

| id | severity | view(s) | finding | evidence | suggested fix (kit level) |
|---|---|---|---|---|---|
| 1 | P0 | eye_climber_wall, eye_cascade_pots, eye_lavender_rail (bg), eye_carpet_bed (bg), front_corner, top | **The `wall_drape` / parapet-cascade module reads as a different object: a padded green quilt or upholstered bolster with pink polka-dot pillows.** It is not a bougainvillea. The canopy is one smooth, inflated green shell with rolled, pillowy edges. The bract masses are smooth pink balloon lobes laid on it as separate blobs, with green showing between them. The pink lobes interpenetrate the green shell, leaving ragged green "holes" inside the pink patches. The small pink and green cards are too sparse to break the two smooth surfaces. At front_corner distance it passes as a flowering climber. At both cameras built for the module it reads as a cushion or a quilt. The structure is now right: a continuous canopy over the coping, a drape between door and window, a cut clear of the openings, and a cascade mode. The surface rendering is what fails, and it brings back the stepped plaza's "faceted balloons" finding in smooth form. | Crops `cascade_left.png` and `cascade_right.png` show the pillow lobes, green holes through the pink (cascade x 290-340 / 440-560, y 330-380 in the full frame) and faceted silhouettes on the lobes. Crops `drape_window.png` and `drape_top_left.png` show a rolled padded bolster along the coping and pink discs on a smooth green sheet. Compare the stepped plaza v003 `architecture_close` (separate faceted balloons): v002 joins them, but the read is still balloon-on-blanket. | 1. Drop the smooth inflated canopy shell as a visible surface. Keep it only as a hidden scatter carrier, shrunk 3-5 cm behind the visible foliage and coloured dark. 2. Skin the carrier with dense small leaf cards (0.04-0.07 m, 600-1,500 per m² of canopy) and with bract clusters made of three papery bracts each (0.03-0.05 m cards in two magenta tones). Group them into irregular panicles of 0.15-0.30 m. Do not use smooth bract-mass lobes. 3. Break the outline with 20-40 trailing cane strands per metre of drape. Each strand is a thin tube 0.6-1.2 m long that ends in leaf and bract cards, so the lower edge hangs as a fringe and not a hem. 4. Add a visible woody armature: 3-5 branching canes from the trunk that fan along the wall and over the coping. 5. Do not let two closed shells occupy the same volume (see #7). |
| 2 | P1 | eye_shrub_mass, eye_b8_rear, eye_perennial_bed, eye_lavender_rail (B9 0.4 m shrub), eye_arching_grass (bg), eye_perennial_drift (bg), top, front_corner | **Shrub masses read as clipped topiary balls or ivy-covered boulders, not loose leafy shrubs.** The v001 creases and spurs are gone. But every shrub silhouette is now a near-perfect sphere or egg. The B4 group is five or six balls of different sizes, and the B8 backdrop is an egg. Each is shingled in hard, flat, angular leaf chips (rhombs and triangles with sharp corners and flat shading). The near-black hull (measured RGB ≈ 7/17/5) shows as a smooth dark ball between the cards. In plan (top) the B4 shrubs are perfect circles. This fails checklist items 3 and 8, and it would carry the green bridge's gumdrop/boulder reading straight into that family. The non-uniform scale and lean barely change the read, because the hull is still a sphere. | Crop `shrub_right.png`: flat chip cards, dark smooth hull visible through the gaps, circular outline. Crop `shrub_dark.png`. Crop `top_b4.png`: six circular balls. eye_b8_rear x 820-1240, y 150-690: an egg-shaped topiary. | 1. **Silhouette from structure, not a sphere.** Build the hull from 4-9 overlapping, irregular, flattened ellipsoid lobes at different heights. Give it a wider, lower base (height:width 0.6-0.8 for mounding shrubs) and notched gaps on the outline. Cut 2-4 concave bays into the silhouette. 2. **Leaves:** use curved, tapered ovate cards (at least 4 verts along the midrib, slight fold, rounded tip) at 0.05-0.09 m. Do not use flat rhombs. Use smooth shading with per-card normal bending toward the hull normal, so the cards shade as one canopy. Use three tones with ±8 % value jitter. 3. Place 15-25 % of the cards on short twig stubs that stand 0.05-0.15 m out from the hull, so the outline is airy. 4. Raise the hull colour to a mid-dark leaf green (around #2E4A26), not near-black, and keep it ≥ 4 cm inside the leaf layer. 5. Add a few visible stems at the base, so the shrub meets the soil through stems and not a dark ball. |
| 3 | P1 | eye_specimen_close, eye_flower_heads, eye_carpet_bed, front_corner, top | **The hydrangea plant body regressed to a vertical-sided, leaf-shingled drum.** The v001 hydrangea was a leafy mound. In v002 the "shrubby mound" under the heads is a cylinder with straight vertical sides and a flat top rim, using the same flat-chip skin and dark hull as #2. In B7 (the Halifax white spine) the two hydrangeas read as clipped topiary barrels with cotton balls on top. The heads themselves are fixed: smooth, lumpy floret domes with no creases (P2 #13). | Crop `hydrangea.png`: straight vertical flanks at x 530-940, y 420-760 in the full frame, and the dark hull visible. Crop `carpet_hydrangea.png`, and eye_carpet_bed x 640-890, y 400-560 (two barrels). | Give the hydrangea its own body, not the shrub skin: a broad, low, rounded mound (height:width ≈ 0.75) with a domed top, built from 3-5 lobes. Use large ovate leaves (0.10-0.15 m, serrate outline optional) that splay outward and droop at the skirt to the soil. Seat the heads into the leaf layer, not on a rim. Test against a 3:4 width:height silhouette rule in the assessor. |
| 4 | P1 | eye_perennial_bed, eye_b8_rear, eye_flower_heads, front_corner | **The new `'panicle'` head reads as a smooth white cone studded with bead bumps** (like a pine cone or a white candle), not a loose floret panicle. It is the "conical head" reading that stopped Prince's Island, made smooth. These are the most prominent white accents in B8 and B1. | Crops `panicle_plume.png` and `b8_panicles_plumes.png`. eye_flower_heads x 1135-1195, y 265-500. eye_b8_rear x 520-600, y 220-360. | Build the panicle as an open branched raceme: a rachis 0.15-0.30 m long with 8-14 side branches that shorten toward the tip and angle 35-60° up. Each branch carries 6-12 tiny floret specks (r 0.005-0.008 m) or short fuzzy cards. Use a feathery cream outline with visible air between the branches, and a slight nod at the tip. Use two tones (cream and white), and add a pink astilbe variant. |
| 5 | P1 | eye_lavender_rail, top (B9) | **The lavender reads as a sea urchin or pincushion,** not a lavender mound. The foliage is a smooth grey-green hemisphere with sparse needle spikes sticking out. The flower stems radiate in a stiff starburst from the dome, and each ends in a smooth lilac capsule. The 18 instances come from one prototype and look stamped along the strip. This is the green bridge's "solid lilac capsules / gumdrop" finding at smaller scale, and it would not give the source's soft purple haze. | Crops `lavender_right.png` and `lavender_left.png`. eye_lavender_rail x 880-1240, y 560-760. In `top_b9_rail.png`, 17 near-identical grey rosettes. | 1. Remove the smooth dome. Build the foliage from 150-300 needle leaves (0.03-0.05 m, grey-sage) on 20-40 short upright stems, making a loose, low, hemispherical mass where the soil shows at the edge. 2. Flower stems should form a vase-shaped upright fan (±25° from vertical), not a radial starburst. Make each spike a stack of 6-10 tiny whorls tapering to the tip, not a capsule. 3. Use 2-3 seeds, with ±15 % height and spread jitter, and let neighbours knit (spacing 0.45-0.6 m) so the strip reads as a drift. |
| 6 | P1 | eye_bedding_band, front_corner, eye_perennial_drift (bg), eye_arching_grass (bg) | **The new `bedding_cushion` (begonia, ageratum, alyssum) reads as gumdrops or iced cupcakes with sprinkles,** not bedding plants. Each one is a smooth hemisphere of uniform colour with a sparse scatter of separate floret beads on top. It has no leaf texture and a hard dome outline. This would carry the Halifax ring and strip beds from "polygonal pebbles" to "smooth gumdrops", and it repeats the green bridge's gumdrop reading. | Crop `cushions.png`. eye_bedding_band x 390-1040, y 390-690. | Make the cushion a leaf-skinned low mound: 0.08-0.12 m high, a broad low profile (height:width ≈ 0.35), with 0.03-0.05 m leaves at 400-700 per m². Cover 40-70 % of the top with flower clusters at 250-500 per m² (begonia: 3-4 bead clusters with a dark bronze-leaf role; ageratum: fuzzy lavender puffs; alyssum: a dense white froth). Give the dome a lumpy outline from 5-8 sub-mounds, and allow cushions to merge where they touch. |
| 7 | P1 | eye_cascade_pots, eye_climber_wall | **True-black slits and wedges** where the pink bract shell meets or folds against the green canopy shell. These are not shadows: the luminance is 0, and there is no occluder on the light side. | Crop `cascade_slit.png`: a slit at full-frame x 405-445, y 455-462, min luminance 0, 103 px below 40. Crop `drape_dark_check.png`: black crease wedges at the drape crest, x 425-435 and 485-500, y 336-342. Further dark slivers at the cascade crest, x 705-760, y 256-272. | These come from two closed shells sharing a surface, and from thin folds in the bract shell that trap light. Fix with #1: remove the inflated bract-mass shells, or keep them strictly outside the canopy shell with a ≥ 1 cm normal offset and no self-folding (check the minimum dihedral angle). Add to `kit.audit()` a coincident/near-coincident face test (faces within 2 mm with opposing normals) that fails the build. |
| 8 | P1 | eye_climber_wall | **Two pots interpenetrate.** The climber's root pot cuts into the rim and wall of the box-ball pot beside it. The kit's clearance rule covers beds, rails and walls, but not pot-to-pot or plant-to-plant footprints in the plaza corner. | Crop `pots_touch.png`, full frame x 665-690, y 745-830. | Register every `pot_plant` and the `wall_drape` root pot as an obstacle with its rim radius plus 0.03 m, and run them through the same `fits` / `audit()` path as the beds. Count pot-pot overlaps as clearance violations. |
| 9 | P2 | eye_carpet_bed, eye_bedding_band | The sage-silver outer band is now the right colour family, but it is almost the same value as the granite kerb and shows no florets. At eye level it reads as a second, wider kerb or a concrete apron, not as the silver Cineraria/Santolina edge band. | Crops `carpet_silver.png` and `band_edge.png`. | Darken and cool the silver role (around #9FAE97). Add silver micro-leaf specks at 150 per m², and keep a visible 1.5 cm step down to the kerb. |
| 10 | P2 | eye_bedding_band, eye_carpet_bed, eye_groundcover | The micro-florets (3-sided specks at 110-130 per m²) read as sprinkles on smooth felt. The bands are clean and clipped, but they have no leaf grain at eye level. The B5 groundcover and every drift underlay are the same smooth felt (v001 #10 is only partly addressed). | Crops `band_edge.png` and `gc_rim.png`. | Add a fine leaf-rosette instancing layer (0.02-0.04 m, 300-600 per m², two tones) over the field top. Raise the floret density in the flowering bands to 250-400 per m², with clusters, not uniform scatter. |
| 11 | P2 | eye_groundcover | The B5 groundcover's far rim is a wavy line that rides up onto the kerb's inner top in places, so the visible kerb width wobbles. | Crop `gc_rim.png`, full frame x 300-1300, y 365-400. | Clamp the field's outline ring to kerb-top minus 1 cm, and resample the ring at a fixed spacing (as for the bands). |
| 12 | P2 | eye_climber_wall, eye_cascade_pots | The box ball reads as a cactus (a smooth sphere with sparse spikes). The climber trunk is one bare straight pole from pot to canopy, with no branching. The drape's lower-left fringe touches the door head. | Crops `pots_touch.png` and `drape_top_left.png`. | Skin the box ball with dense small leaves (0.015-0.025 m) over a slightly faceted-free hull. Give the trunk 2-3 twisting stems that branch below the canopy. Keep the drape ≥ 0.10 m off the door head. |
| 13 | P2 | eye_specimen_close, eye_flower_heads, eye_carpet_bed | The hydrangea heads (head only) read as cotton-ball or cauliflower clusters. Nine large smooth floret domes are too coarse to read as many 4-petal florets at 1-2 m. | Crop `hydrangea.png`. | Add a floret-card skin (40-80 small 4-petal cards per head) over the domes, and cut the dome bulges to ≤ 0.25 × r. |
| 14 | P2 | eye_specimen_close, eye_perennial_drift | The yarrow corymb's eight floret domes are coarse, so the head looks like popcorn at 1.5 m. It does read as a flat-topped flower head, though. | Crop `yarrow.png`. | Use 25-40 floret domes at r 0.006-0.009 m on a flatter dome. |
| 15 | P2 | eye_b8_rear, eye_perennial_bed, eye_lavender_rail, top | Clones: coneflower1 (41 instances) and lavender1 (18) are single prototypes, and the repetition is visible in the B8 and B9 near rows. The B4 shrubs share one spherical silhouette across seeds. | `planting-kit-size.json` and build-report prototype counts. eye_b8_rear foreground clumps. | Give coneflower, salvia and lavender 2-3 seeds each, and add per-instance stem count and height jitter. |
| 16 | P2 | top, eye_perennial_bed, eye_b8_rear | The B8 backdrop is still sparse: three shrubs on a 12 m rear edge, not a layered backdrop (v001 #14 is only partly addressed). | Crop `top_b8.png`. | Fill the rear strip at 1.2-1.5 m spacing with 0.8-1.6 m shrubs (once #2 is fixed), plus a mid layer of feather reed between them. |
| 17 | P2 | eye_arching_grass, top | B3 now holds only 14 tufts on a mostly empty felt underlay, and its feather reed has moved to B8. The grass bed reads empty at eye level. | eye_arching_grass whole bed. | Raise the tuft count to 25-35 and add 3-4 feather-reed clumps back to B3 as the grass-layer test. |
| 18 | P2 | eye_flower_heads, eye_perennial_drift, eye_b8_rear | The perennial rosettes are stiff, flat, broad blades that splay like agave or bromeliad rosettes. The coneflower foliage is especially stiff. | eye_b8_rear x 450-720, y 760-1010. | Add 2-3 bends along each leaf and droop the outer leaves to the soil. Shorten the coneflower basal leaves and add stem leaves. |
| 19 | P2 | eye_climber_wall (pots), eye_cascade_pots | The geranium heads now read as red floret clusters, which is a clear improvement on the stepped plaza's "gift-bow cubes". The pots are about 0.45 m tall, which is still large against a terrace riser. | Crop `cascade_fringe.png`. | Offer a 0.30-0.35 m pot size. |
| 20 | P2 | build report / GLB | No `EXT_mesh_gpu_instancing` (v001 #15, not addressed): 427 nodes and 98 meshes, with 388 nodes sharing 59 meshes. The GLB has 6 % headroom under the cap (3,931,904 of 4,194,304 bytes), so fixes #1-#6 must stay triangle-neutral or move to GPU instancing. | GLB JSON: `extensionsUsed` absent. `planting-kit-size.json`. | Export plants with `EXT_mesh_gpu_instancing`, or batch shared meshes into `InstancedMesh` in the loader. Budget per-prototype triangles in the build report. |

Count check: P0 = #1. P1 = #2-#8 (7). P2 = #9-#20 (12).

## 4. Conformance checklist

| # | item | mark | notes |
|---|---|---|---|
| 1 | Flower heads read as flowers (daisy, spike, umbel, hydrangea), not gems, cones or balls | **FAIL** | Daisy (coneflower, rudbeckia): PASS. Spike (salvia): PASS, tighter than v001. Cup (poppy): PASS. Umbel/corymb (yarrow): PASS with P2 #14. Hydrangea heads: PASS with P2 #13. Panicle: **FAIL** (white studded cone, P1 #4). Lavender spikes: capsule tips (P1 #5). |
| 2 | Grasses read as arching blade tufts | **PASS** | Fountain grass and blue grass are fine arching blades with no visible crown dome (v001 #13 fixed). The feather-reed plumes are slim feathery spindles (v001 #5 fixed). |
| 3 | Shrub masses read as loose leafy shrubs | **FAIL** | Topiary spheres and eggs (P1 #2). Drum-bodied hydrangea (P1 #3). Gumdrop cushions (P1 #6). |
| 4 | Groundcover hides bare fill | **PASS** | No bare mulch anywhere. The underlay is now the default in B1, B2, B3, B4 and B8 (v001 #9 fixed). It reads as felt (P2 #10). |
| 5 | Carpet bedding and bedding bands read as clipped low planting with clean edges | **PASS (bands and carpet), with P2** | Flat tops, steep clipped shoulders, no soil valleys, no teeth (v001 #2 fixed). The silver band reads as kerb (P2 #9), and the florets read as sprinkles (P2 #10). The separate cushion module fails (P1 #6). |
| 6 | Every plant grounded, none intersecting kerbs or walks, all within its bed | **FAIL** | No floating plants. All shrubs are clear of their kerbs (top, eye_b8_rear) and the lavender strip is clear of the rail (`top_b9_rail.png`). v001 #6 is fixed. But two plaza pots interpenetrate (P1 #8), and the B5 groundcover rim wobbles onto the kerb (P2 #11). |
| 7 | No black patches, slots, wedges or z-fighting | **FAIL** | True-black slits in the bougainvillea bract/canopy shell overlap (P1 #7), and the shells interpenetrate (P0 #1). I checked every other dark cluster. The shrub interiors are the dark-green hull (RGB ≈ 7/17/5), counted under P1 #2 as a design defect, not a void. The other dark clusters are pot soil, the window glass, rail post feet and under-leaf contact shadow. The kerb, soil, lawn, gravel and paving are clean. |
| 8 | Smooth shading, no faceting visible at 1440 px eye level | **FAIL** | The shrub leaf chips are hard, flat, angular polygons (P1 #2). The bract lobes show facets on their silhouettes (P0 #1). The daisies, blades, spindles, poppies and band fields are smooth. |
| 9 | Variation, no obvious clones; drifts look planted | **PARTIAL** | The B2 and B8 drifts read as planted. Coneflower and lavender are visibly stamped (P2 #15). The B4 shrubs differ in size but not in form. |
| 10 | Aerial read: beds read as planting with a legible pattern | **PASS** | front_corner and top read clearly: specimen bed, drift, grass, shrub group, groundcover, concentric bands, leaf-shaped carpet bed, long perennial bed, lavender strip and plaza corner. In top the B4 shrubs are perfect circles (P1 #2). |
| 11 | GLB under 4,194,304 bytes; instances survive the round trip | **PASS** | 3,931,904 bytes, re-measured from the GLB. 427 nodes and 98 meshes, with 388 nodes referencing 59 shared meshes. The report lists 159 plants, 27 prototypes, 399 instance nodes, `clearance_violations: 0` and a round-trip delta of 0.0. Headroom is only 6 %, and there is no GPU-instancing extension (P2 #20). |
| 12 | Kit could plausibly close each family's planting finding | **FAIL** | None of the four is fully closed. See section 7. |

## 5. Camera validity

The positions below are from `prework-manifest.json`.

- **front_corner** (−11.0, −20.5, 13.5 → 6, 0, 0, 24 mm). An elevated oblique from outside the south-west corner. All nine beds, both walks, the B9 rail and the plaza corner are in frame, and nothing is clipped. The plaza is small at the far end but legible. Valid.
- **top** (orthographic, scale 42 m, at 60 m). Covers the full 41 × 22 m lawn with an even margin. Valid.
- **eye_flower_heads, eye_perennial_drift, eye_arching_grass, eye_shrub_mass, eye_lavender_rail** (z = 1.6 m, y −9.6 to −10.3, 26-30 mm). Each stands on the lawn just inside the south site edge (−10.5) and aims at its bed. Each bed is wholly or almost wholly in frame. Valid pedestrian views.
- **eye_specimen_close** (z = 1.45 m, about 2.3 m from the B1 hydrangea, 35 mm). Valid. This is the close specimen view the v001 review asked for.
- **eye_groundcover, eye_bedding_band** (on the south gravel walk, z = 1.6 m). Valid.
- **eye_carpet_bed** (raking along B7, 24 mm). Valid. It exposes the band shoulders, which are now clean.
- **eye_perennial_bed** (24 mm, on the lawn south of the north walk). Valid. The foreground foliage is cut at the left edge, which is acceptable.
- **eye_b8_rear** (2.0, 11.2, 1.6, looking south). It stands inside the north site edge (11.5) and shows the rear kerb and the backdrop shrub. Valid. This is the view the v001 review asked for, and it confirms the kerb clearance.
- **eye_climber_wall** (20.0, 1.6, 1.6, looking north at the plaza wall, 22 mm). The whole wall, the door, the window, the drape and the pots are in frame. Valid.
- **eye_cascade_pots** (z = 1.5 m, about 3 m from the terrace wall, 28 mm). Valid.
- No camera is inside geometry, below grade or outside the site.
- Gaps (not counted):
  - There is still no backlit view: every planting eye view looks north or south under the same key light.
  - There is no oblique side view of the wall drape, which would show its depth off the wall and where it attaches.
  - There is no eye view at the far end of B9, where the strip meets the rail.

## 6. Previous findings (v001 P1s)

| v001 P1 | status | evidence |
|---|---|---|
| 1 Shrub masses crumpled, creased, spurred, slit | **NOT FIXED** (the reading changed, but it still fails) | The creases, spurs and slits are gone. The new hull-plus-chip skin gives perfect spheres and eggs, hard flat leaf chips and a near-black hull showing through. They read as topiary balls or boulders (P1 #2). |
| 2 Bedding bands and carpet bed as puffy tubes with saw-tooth crests and mulch valleys; groundcover rim spikes | **FIXED** | eye_bedding_band and eye_carpet_bed: flat clipped tops, steep shoulders, no valleys, no teeth, sage-silver band. The groundcover rim spikes are gone; only a slight wobble remains (P2 #11). The new cushion module is a separate failure (P1 #6). |
| 3 Mophead hydrangea heads as crumpled paper wads | **FIXED for the heads; plant REGRESSED** | The heads are smooth floret-dome clusters with no creases or flakes (P2 #13 for coarseness). The body changed from a leafy mound to a vertical-sided, leaf-shingled drum (P1 #3). |
| 4 Yarrow umbels as jagged flat plates | **FIXED** | It is a smooth, domed corymb in yellow and cream, on narrow divided leaves (P2 #14 for coarse florets). |
| 5 Feather-reed plumes as stacks of faceted pods | **FIXED** | eye_perennial_bed and eye_b8_rear show slim, hairy, nodding spindles with varied heights. |
| 6 Placement rule let the B8 backdrop shrub swallow its kerb | **FIXED** | In top, `top_b8.png` and eye_b8_rear, every B8 shrub sits clear inside its kerb. B9 is clear of the rail. The report shows `clearance_violations: 0`. The rule does not yet cover pot-to-pot clearance (P1 #8). |

## 7. Per-family closure

**Prince's Island Park (v003 P1: faceted cone flower heads, flat straw-ribbon grasses, bare fill between mounds).** *Mostly closable, but not closed by v002.*
- Flower heads: the coneflower, rudbeckia, salvia and yarrow heads would close the cone-head reading.
- Grasses: the arching blade tufts and the new plume spindles close the straw-ribbon reading. This is the clearest win in the kit.
- Bare fill: the default underlay closes it, although at eye level the underlay is felt (P2 #10).
- Still reproduces the failure: the new white **panicle** reads as a studded white cone (P1 #4). It is exactly the element the source's white panicles need, so it would put cone heads back into the beds. The bed shrubs would read as topiary balls (P1 #2).
- Still missing: a loose panicle head, a loose mounding shrub, and enough backdrop density for the source's "dense layered mounds" (P2 #16).

**Halifax Public Gardens (v002/v003 P1: carpet-bed plants read as faceted gems with hard outlines).** *Not closed.*
- The flat `carpet_bands` field does close the gem reading for the coloured ribbons. They are flat and clipped, with clean edges and no valleys.
- The white hydrangea spine is now a leaf-chip drum with cotton-ball heads (P1 #3, P2 #13).
- The ring and strip beds would use `bedding_cushion`, which reads as gumdrops with sprinkles (P1 #6).
- At eye level the carpet ribbons lack the dense flowering texture of the source (P2 #10). The silver edge band reads as kerb (P2 #9).
- Still missing: a leaf-skinned bedding cushion with dense floret clusters, and a loose hydrangea body.

**Planted green bridge (v002 boulders; v003 gumdrop mounds, solid lilac capsules, kerb and rail overrun).** *Partly closable; not closed.*
- Rail and kerb overrun: closed. The clearance rule keeps the B9 lavender and shrub off the rail and kerb (`top_b9_rail.png`).
- Grass layer: the fountain grass would supply the bunch-grass layer. No bright yellow-green variant is shown.
- Poppy cups: read well.
- Still reproduces the failure:
  - The **lavender** is a grey sea-urchin dome with capsule-tipped starburst stems (P1 #5). That is the gumdrop and capsule reading again.
  - The **shrub range** of 0.4-1.6 m exists, but every size is a topiary ball (P1 #2), which would carry the gumdrop/boulder reading.

**Stepped terraced plaza (v003 P1: bougainvillea as faceted balloons, no drape).** *Not closed.*
- The module now has the right structure: a canopy over the coping, a drape between the door and the window that is cut clear of both, a parapet-cascade mode and a root pot.
- But it reads as a padded quilt with pink balloon patches (P0 #1). It has black slits (P1 #7), and its pot clashes with its neighbour (P1 #8). That is the balloon finding in a new form.
- The `pot_plant` geranium would close the stepped plaza's "gift-bow cube" P2 (#5 there), although the pots are still large (P2 #19). The box ball reads as a cactus (P2 #12).
- Still missing: a leaf-and-bract-card canopy surface with trailing canes and a visible branching armature, in place of the two smooth shells.

## Crops written

All crops are in `review/crops_wkhpzr/`: b8_panicles_plumes, b8_shrub_dark_mask, band_edge, carpet_hydrangea, carpet_silver, cascade_fringe, cascade_fringe_mask, cascade_left, cascade_right, cascade_slit, cushions, drape_dark_check, drape_top_left, drape_window, fc_plaza, gc_rim, hydrangea, lavender_left, lavender_right, panicle_plume, pots_touch, shrub_dark, shrub_dark_mask, shrub_right, top_b4, top_b8, top_b9_rail, yarrow.
