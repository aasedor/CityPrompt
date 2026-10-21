# Independent RLASM v6.1 review: shared planting kit showcase v003

Candidate: `clay-planting-kit-showcase-clay-v003`. This is a showcase of the shared planting kit, not a catalogue building.
Reviewer: independent. I did not build this model.

Verdict: FAIL

Counts: P0=0 P1=2 P2=12

## What I looked at and how

- **v003 renders:** all 15, at full 1440 x 1080, plus all three phone boards.
- **v002 renders:** eye_shrub_mass, eye_b8_rear, eye_specimen_close, eye_climber_wall, eye_cascade_pots, eye_lavender_rail and eye_bedding_band.
- **Comparison family renders:**
  - Prince's Island v003 `promenade_beds`
  - Halifax v003 `carpet_beds`
  - Green bridge v003 `planting_bed`
  - Stepped plaza v003 `architecture_close`
- **Reviews:** the five family reviews named in the brief, and the v002 kit review.
- **Reference:** the benchmark text in `docs/HIGH_QUALITY_3D_PARK_MEMORY.md` and the botanical-garden reference `variant_0.png`. `variant_0_angle_60.jpg` in the working tree is a Git LFS pointer, not an image, so I could not view it.
- **Non-visual inputs:** I used `build-report.json`, `evidence/planting-kit-size.json`, the GLB JSON chunk (parsed directly) and the camera roster in `prework-manifest.json`. I used them only for sizes, instancing and camera positions. Every visual judgement below comes from the pixels.
- **Crops:** zoom crops and dark-pixel masks are only in the new folder `review/crops_hjtzut/`. In the masks, magenta means luminance below 15 and amber means 15-30.

**Dark-pixel method.** I ran a luminance scan over every render and looked at each dark cluster by eye in a masked crop. I counted a dark cluster as **occlusion or contact shadow** only when all four of these held:

1. It lay under or behind an occluding leaf or lobe on the key-light side.
2. Its outline followed the occluder's edge, and its value ramped into the surrounding tone.
3. It sat in a concave or under-canopy position.
4. The same surface with nothing over it (lawn, kerb, felt, wall, carrier) was clean.

I would have counted it as a **geometry defect** if it was hard-edged and not tied to an occluder, or if it sat on an open surface, or if it ran as a slit along a junction between two shells.

**Dark-pixel results:**

| render | pixels below luminance 10 | what the dark clusters are |
|---|---|---|
| eye_shrub_mass | 15,267 | Gaps between leaf cards on the shaded lower half of the shrubs, and the contact shadow under the lifted skirt (`shrub_right_base_mask`). Occlusion. |
| eye_b8_rear | 7,890 | The same kind of cluster (`b8_shrub_mask`). Occlusion. |
| eye_perennial_bed, eye_perennial_drift, eye_flower_heads, eye_specimen_close | 1,806-3,208 each | Undersides of rosette leaves lying close to the felt (`fh_right_mask`), and pockets between leaves in the hydrangea skirt (`hydrangea_mask`). Occlusion. |
| eye_cascade_pots, eye_climber_wall | — | Small irregular gaps between leaf sprays onto the shaded carrier (`cascade_left_mask`, `cascade_right_mask`), and pot soil. No slits. |
| eye_groundcover | 0 (minimum luminance 14.9) | — |
| front_corner, top | 5-9 | Shrub undersides only. |

I found **no** black patch, slot, wedge or z-fighting caused by geometry in any render. In particular, the v002 black slits at the bougainvillea shell junction are gone.

## Summary

v003 fixes the module that failed hardest, the bougainvillea. It now reads, at both cameras built for it, as a real flowering climber: arching leafy sprays, three-bract magenta clusters, trailing canes and a woody armature, with no balloons and no black slits. Several other v002 P1s are also fixed in the pixels:

- The panicle is an open, nodding raceme.
- The lavender is an upright fan of spikes over grey needle foliage. It no longer reads as a sea urchin.
- The bedding cushions are lumpy, leaf-skinned mounds that carry floret clusters.
- The hydrangea is a broad, low, skirted mound, no longer a drum.
- The pots no longer intersect.

Two P1s keep the verdict at FAIL:

1. **The shrub method still shows its hull at eye level.** Smooth, rounded, mid-green lobes show between large flat leaf cards. At 3-5 m the B4 group and the B8 backdrop shrub read as leaf-pasted lumpy mounds or boulders. The same hull shows under the hydrangea and the begonia cushion.
2. **Placement now lets shrub canopies cross kerbs.** The B8 west shrub straddles the kerb at the bed tip, and the B8 east and B4 north-west canopies cover their kerbs in plan. This regresses a fix that v002 had confirmed.

## 3. Findings

| id | severity | view(s) | finding | evidence | suggested fix (kit level) |
|---|---|---|---|---|---|
| 1 | P1 | eye_shrub_mass, eye_b8_rear, eye_specimen_close, eye_carpet_bed, eye_bedding_band (begonia) | **The shared hull-plus-card method still shows a smooth, rounded, lumpy hull at pedestrian range.** The silhouette is fixed: an irregular outline, off-centre lobes, twigs breaking the edge, a lower and wider form, and a skirt that lifts. But between the outer leaves the hull reads as smooth mid-green domes, with only faint outlines of the flat inner leaves on them. The inner third of the leaves lies flat on the hull, and their normals are bent 70% toward the canopy normal, so they shade as one smooth surface. That is exactly why they vanish into a smooth hull. The result: the B4 group at 4-5 m reads as one heap of leaf-pasted balls (lumpy topiary or an ivy-covered boulder pile), and the B8 backdrop shrub reads as an ivy-covered boulder. The hydrangea body shows two smooth dark spheres under its leaves, with a dark crease where they meet. The begonia cushion shows smooth maroon bulges under its leaf skin. At 8 m or more (eye_perennial_bed, eye_arching_grass background, front_corner, top) the shrubs read correctly as loose, leafy shrubs. This would carry the green bridge's boulder and gumdrop reading into any close camera such as that family's `planting_bed`. | **eye_shrub_mass:** smooth lobes at x 386-530, y 197-510 (crop `shrub_left`). **eye_b8_rear:** smooth hull faces at x 1013-1133, y 313-420 and x 1133-1267, y 540-633 (crop `b8_shrub`). **Hydrangea:** core spheres at eye_specimen_close x 610-682, y 599-693, and the crease at x 602-699, y 688-738 (crops `hydrangea` and `hydrangea_mask`); also `carpet_hydr`. **Begonia:** crop `cushions`, left and right red mounds. | 1. Stop rendering the hull as a visible surface. Either shrink it 6-10 cm inside the leaf layer and give it a dark, rough, unlit-looking leaf-shadow colour (about #1F3319), or delete it once the leaf layers are dense enough to be opaque. 2. Replace the flat-lying inner third with a second layer of **lifted** leaves (10-25°). Raise the overall card density about 1.5x in the outer 15 cm, and use smaller leaves on the inner layer. 3. Keep the normal bending at about 40-50%, not 70%, so each card keeps its own value step while the mass still shades as one canopy. 4. Apply the same rule to the hydrangea body and the begonia cushion. 5. Add an assessor check: in a 1440 px eye-level test render at 3 m, no contiguous hull-material region larger than about 0.5% of the plant's screen area. |
| 2 | P1 | top, front_corner | **Shrub canopies cross bed kerbs.** This regresses v001 #6, which v002 had confirmed fixed. The **B8 west shrub** stands at the narrow west tip of B8. In plan its canopy covers the whole kerb tip and reaches about 0.15-0.25 m beyond the kerb onto the lawn. In front_corner its lowest lobe sits down onto the kerb end. From these two views I cannot tell whether the hull penetrates the kerb or overhangs it, but either way the plant is not within its bed. The **B8 east shrub** canopy covers about 1.4 m of the north kerb in plan. The **B4 north-west** canopy laps over its kerb. The build report says `clearance_violations: 0`, so the clearance test is evidently made against a smaller footprint than the delivered canopy. The lifted outer leaves and twig sprigs push the canopy out further than the hull radius. | **top:** B8 west x 294-346, y 205-275, kerb tip at about x 318 (crops `top_b8`, `top_b8_west`); B8 east x 661-710, y 215-290 (`top_b8_east`); B4 north-west x 760-770, y 727-740 (`top_b4`). **front_corner:** B8 west lobe on the kerb end at x 212-240, y 530-549 (`fc_b8_west`). | 1. Run `fits` / `audit()` against the **delivered canopy footprint**: the hull radius plus the lift of the outer leaves plus the reach of the sprigs, measured from the built prototype's bounds after non-uniform scale and lean. Then add a 0.10 m clearance to the kerb's inner arris. 2. Reject any placement whose footprint disc crosses a polygon vertex region narrower than its diameter, so no shrub sits at a bed tip. 3. Add an eye-level camera on the B8 west tip, and count canopy-over-kerb overlaps in the report. |
| 3 | P2 | eye_b8_rear (foreground), eye_shrub_mass, eye_specimen_close | Close up (1-3 m), the "ovate" shrub and hydrangea leaves read as cut-paper kites or pentagons with straight edges and flat value. At about 10-15 cm they are large for every shrub size, so the 0.4 m and 1.6 m shrubs share one leaf scale. | eye_b8_rear x 0-400, y 450-1080 (crop `b8_fg_leaves`). | Give each card 8-10 outline vertices, with a curved margin on each side of the midrib. Scale leaf size with shrub size (about 4-6 cm on 0.4-0.8 m shrubs, 7-10 cm on 1.2-1.6 m shrubs), and add ±15% per-card size jitter. |
| 4 | P2 | eye_climber_wall, eye_cascade_pots (top left) | The bougainvillea carrier sheet shows as a flat, mid-dark-green panel with hard, geometric cut edges:<br>• a straight vertical strip along the window's left jamb;<br>• an arched cut above the door;<br>• a clean, straight-cut triangle over the window head.<br>It reads as a green felt backing board with sprays pinned on it, not as foliage depth. | eye_climber_wall x 442-450, y 462-498 (straight edge left of the door head); x 482-546, y 462-482 (arch above the door); x 980-1080, y 450-498 (cut over the window); x 797-810, y 537-667 (jamb strip). Crops `drape_left`, `drape_right`, `window_jamb`. | Inset the carrier 0.10-0.15 m inside the outer spray boundary everywhere. Give its outline a noisy, ragged offset (±5 cm), and make sure every carrier edge is overlapped by at least one spray. Darken the carrier further so it reads as shadow. |
| 5 | P2 | eye_climber_wall, eye_cascade_pots | The leafy sprays are visibly stamped. There are 114 instances of a single `bougainvillea_leafy` prototype, so the wall and the cascade show a regular, repeating herringbone of identical pinnate sprays, like ivy wallpaper. The bract clusters on the crest are seen from below, so they read as dark maroon or brown. | Crops `cascade_right` and `drape_right`. Crest bracts at eye_cascade_pots x 230-300, y 300-330 and x 800-1000, y 285-320. | Use 3 leafy-spray seeds with different leaf counts and arch curves. Add ±20% scale and ±25° roll per instance. Turn crest bract clusters so their upper faces tilt toward the street side, or brighten the darker magenta role. |
| 6 | P2 | eye_specimen_close, eye_flower_heads, eye_carpet_bed | The hydrangea heads still read as cotton-ball or cauliflower clusters of large, smooth spheres. This is v002 #13, not addressed. | Crops `hydrangea` and `carpet_hydr`. | As in v002 #13: use a 4-petal floret-card skin of 40-80 cards per head, and keep dome bulges at 0.25 x r or less. |
| 7 | P2 | eye_specimen_close | The yarrow corymbs are still coarse popcorn of about 8 large domes. This is v002 #14, not addressed. | eye_specimen_close x 700-950, y 580-1000. | Use 25-40 floret domes of radius 6-9 mm on a flatter dome. |
| 8 | P2 | eye_climber_wall, eye_cascade_pots | The box ball still reads as a cactus: a smooth sphere with sparse spikes. It is the most prominent object in eye_cascade_pots. The climber trunk is still one bare straight pole from the pot to the canopy. The pot overlap is fixed. | Crops `pots` and `boxball`. | Skin the box ball with 1.5-2.5 cm leaf cards at full cover, and do not render a visible hull. Give the trunk 2-3 twisting stems that fork 0.3-0.5 m below the canopy. |
| 9 | P2 | eye_bedding_band, eye_carpet_bed, eye_groundcover | The carpet and bedding bands and the B5 groundcover are still smooth felt with sparse triangular specks. There is no leaf grain. At eye level the silver band is still a pale grey-green apron close to the kerb's value. These are v002 #9 and #10, with no visible change in the pixels. This is the main remaining risk for Halifax: close up, the beds may now read as coloured rubber matting. | Crops `band_edge`, `carpet_edge`, `gc_left`. | Use the v002 #9 and #10 fixes: a 300-600 per m² leaf-rosette layer in two tones, clustered florets at 250-400 per m², and silver micro-leaf specks with a 1.5 cm step down to the kerb. |
| 10 | P2 | eye_groundcover, eye_flower_heads | In oblique views a brown mulch sliver shows between the rounded shoulder of the groundcover or underlay and the kerb's inner face. The far rim of B5 still wobbles in visible kerb width. v002 #11 is only partly fixed. | eye_groundcover x 0-20, y 517-610 (crop `gc_left`) and far rim x 300-1150, y 365-410 (`gc_rim_far`). eye_flower_heads x 33-57, y 593-677 (`fh_kerb_left`). | Carry the field to the kerb's inner face at full height, with a vertical lap of 1-2 cm below the arris, and drop the 8 cm rounded shoulder at the kerb. Resample the rim at fixed spacing and clamp it to kerb-top minus 1 cm. |
| 11 | P2 | eye_lavender_rail | The lavender reads as lavender now. But the flower stems are long, bare and sparse, like a whisk broom, and the spikes are tiny. The plants are spaced apart on felt rather than knitting, so the strip does not give the soft purple haze that the green bridge source needs. The two seeds look alike. | Crop `lavender`. eye_lavender_rail x 0-1000, y 470-750. | Shorten the stems by about 25%. Make the spikes about 1.5x longer, with denser whorls, and double the flower-stem count. Set spacing at 0.40-0.45 m so the foliage mounds touch. Add a third seed with a lower, wider fan. |
| 12 | P2 | eye_perennial_drift, eye_b8_rear, eye_perennial_bed | `coneflower1` is still one seed with 29 instances, and the repeat shows in B2 and B8. This is v002 #15, partly addressed: salvia and lavender now have 2 seeds each. | Prototype counts in build-report.json. eye_perennial_drift x 400-1150, y 280-560. | Use 2-3 coneflower seeds with jittered stem count and height. |
| 13 | P2 | eye_arching_grass, top | B3 is sparser than in v002: 9 tufts (5 fountain grass, 4 blue grass), down from 14, on a largely bare felt underlay. v002 #17 got worse. | Prototype counts. eye_arching_grass whole bed. | Use 25-35 tufts and put 3-4 feather-reed clumps back as the grass-layer test. Pay for them from the 2-3 seed savings above, or move to GPU instancing (#14). |
| 14 | P2 | build report / GLB | Size and instancing. I re-measured the GLB at 4,100,404 bytes, which leaves 94 KB (2.2%) under the cap. There is still no `EXT_mesh_gpu_instancing`. The file has 656 nodes and 101 meshes, with 622 nodes sharing 67 meshes. Fixes #1, #3, #5, #11 and #13 add triangles, so with this headroom they cannot land without GPU instancing or culling. v002 #20 is not addressed. | GLB JSON: `extensionsUsed` is absent. `planting-kit-size.json`. | Export plants with `EXT_mesh_gpu_instancing`, or have the loader batch shared meshes into `InstancedMesh`. Record a per-prototype triangle budget in the build report. |

Count check: P0 = none. P1 = #1 and #2 (2). P2 = #3-#14 (12).

## 4. Conformance checklist

| # | item | mark | notes |
|---|---|---|---|
| 1 | Flower heads read as flowers (daisy, spike, umbel, hydrangea), not gems, cones or balls | **PASS, with P2s** | **Pass:** daisy (coneflower, rudbeckia), spike (salvia), cup (poppy), and the panicle, now an open branched raceme with air between the branches and a nodding tip (crop `panicle`). Astilbe reads as a pink plume. **Lavender:** the spikes are tiny but read as spikes (P2 #11). **P2s:** the hydrangea heads are still clusters of spheres (#6), and the yarrow is coarse (#7). No gems or cones anywhere. |
| 2 | Grasses read as arching blade tufts, not flat ribbons or straw sheets | **PASS** | Fountain grass and blue grass are fine arching blades. The feather-reed plumes are slim, feathery spindles. B3 is sparse (P2 #13). |
| 3 | Shrub masses read as loose leafy shrubs, not boulders, gumdrops or lumpy topiary | **FAIL** | They pass at 8 m or more. At 3-5 m the smooth hull lobes show (P1 #1), and the hydrangea and begonia bodies share the same flaw. The cushions are no longer gumdrops. |
| 4 | Groundcover hides bare fill; no visible bare mulch where a bed is meant to be full | **PASS, with P2** | The underlay or groundcover fills every bed. A thin mulch sliver shows at the kerb in oblique views (P2 #10). |
| 5 | Carpet bedding and bedding bands read as clipped low planting with clean edges | **PASS, with P2** | The bands are flat and clipped with clean edges, with no tubes and no valleys. They are felt-like at eye level, and the silver band reads as an apron (P2 #9). |
| 6 | Every plant grounded; none floating or intersecting kerbs or walks; all within its bed | **FAIL** | Nothing floats. Every plant meets the soil through a skirt and contact shadow. The pots are clear of each other, and the lavender strip is clear of the rail. But the B8 west shrub straddles its kerb tip, and two other canopies cover their kerbs (P1 #2). |
| 7 | No black patches, slots, wedges or z-fighting | **PASS** | I checked every dark cluster against the method above. All are under-canopy occlusion, contact shadow or pot soil. The v002 bract-shell slits are gone. The band and kerb boundaries show no z-fighting (crops `carpet_edge`, `band_edge`). |
| 8 | Smooth shading where curvature is intended; no faceting at 1440 px eye level | **PASS, with P2** | There are no faceted lobes or bract shells. Leaf outlines are polygonal close up (P2 #3). The smooth hull showing through is a design fault, counted under P1 #1, not a faceting fault. |
| 9 | Variation: no obvious clones; drifts look planted | **PARTIAL** | B2 and B8 read as planted. The coneflower repeats (P2 #12). The bougainvillea sprays are stamped (P2 #5). The B4 shrubs now differ in form. |
| 10 | Aerial read: beds read as planting with a legible pattern | **PASS** | front_corner and top read clearly: all nine beds, the bands, the leaf-shaped carpet bed, the lavender strip and the planted plaza corner. In plan the B4 shrubs are irregular clumps, no longer circles. |
| 11 | GLB under 4,194,304 bytes; instances survive the round trip | **PASS** (P2 #14) | 4,100,404 bytes. 629 instance nodes, 337 placements from 31 prototypes, round-trip delta 0.0, `build_valid`. Only 2.2% headroom, and no GPU-instancing extension. |
| 12 | The kit could plausibly close each of the four families' planting findings | **PARTIAL** | It would close Prince's Island, Halifax and the stepped plaza. It would not yet close the green bridge, because of P1 #1 and P1 #2. See section 7. |

## 5. Camera validity

The roster in `prework-manifest.json` is the same as for v002. I checked each frame.

- **front_corner** (−11.0, −20.5, 13.5 → 6, 0, 0; 24 mm): an elevated oblique. All nine beds, both walks, the B9 rail and the plaza corner are in frame, unclipped. Valid.
- **top** (orthographic, scale 42, at 60 m): the full 41 x 22 m lawn with an even margin. Valid.
- **eye_flower_heads, eye_perennial_drift, eye_arching_grass, eye_shrub_mass, eye_lavender_rail** (z = 1.6 m, on the lawn just inside the south edge): each frames its bed whole or almost whole. Valid pedestrian views.
- **eye_specimen_close** (z = 1.45 m, about 2.3 m from the B1 hydrangea, 35 mm): valid. This is the view that exposes the hull core.
- **eye_groundcover, eye_bedding_band** (on the south gravel walk), **eye_carpet_bed** (raking along B7) and **eye_perennial_bed**: valid.
- **eye_b8_rear** (2.0, 11.2, 1.6 looking south): valid. It shows the rear kerb clear of the shrub at this point. The B8 west tip, where P1 #2 occurs, is just outside its frame.
- **eye_climber_wall, eye_cascade_pots**: valid. The wall, door, window, drape, cascade and pots are all in frame.
- No camera is inside geometry, below grade or outside the site.

**Gaps** (not counted as findings):

- There is no eye-level view of the B8 west tip.
- There is no backlit view.
- There is no oblique side view of the wall drape, which would show its depth off the wall and the carrier's edges.

**Boards:** the boards reproduce the renders faithfully. They carry large empty letterbox bands, and phone-03 has one empty cell. This is presentation only.

## 6. Previous findings (v002 P0 and P1)

| v002 finding | status | evidence |
|---|---|---|
| P0 #1: bougainvillea reads as a padded quilt with pink balloon patches | **FIXED** | eye_climber_wall and eye_cascade_pots show arching pinnate leaf sprays, three-bract magenta clusters, trailing canes with leaves and bracts, and visible brown canes on the wall. There are no smooth shells and no balloons. Residual P2s: #4 (carrier edges) and #5 (stamping). |
| P1 #2: shrubs read as topiary balls or ivy boulders | **NOT FIXED** (improved) | The outline is fixed: irregular lobes, a bay, lifted sprigs, a lower and wider form. In plan they are irregular clumps. But the smooth hull still shows at eye level (P1 #1). This is the shrub finding's third attempt. |
| P1 #3: hydrangea drum | **FIXED** (silhouette) | eye_specimen_close and eye_carpet_bed show a broad, low dome with a splayed, drooping skirt to the soil and heads seated in the leaves. The visible hull core is carried under P1 #1. |
| P1 #4: panicle cone | **FIXED** | An open, nodding raceme with side branches and air between them, in cream, plus a pink astilbe (crops `panicle`, `fh_right`). |
| P1 #5: sea-urchin lavender | **FIXED** | No dome. An upright vase fan over grey needle foliage. Residual sparseness is P2 #11. |
| P1 #6: gumdrop cushions | **FIXED** | Lumpy leaf-skinned mounds with clustered florets (crop `cushions`). The begonia hull showing through is carried under P1 #1. |
| P1 #7: black slits at the shell junction | **FIXED** | No slits. The luminance scan and masks show only under-leaf occlusion (`cascade_left_mask`, `cascade_right_mask`). |
| P1 #8: pots intersecting | **FIXED** | The climber pot and the box pot are clearly separated (crop `pots`). The box pot is clear of the door. |
| v001 #6 / v002 confirmation: all B8 shrubs clear of their kerbs | **REGRESSED** | Raised as P1 #2. |

**v002 P2 status, briefly:**

- **Unchanged:** #9 and #10 (felt bands and silver apron, now P2 #9), #13 (now #6), #14 (now #7), #19 (pot size), #20 (now #14).
- **Partly fixed:** #11 (now #10). #12: the pots are separated, but the box ball and trunk are unchanged (now #8). #15 (now #12). #16: B8 now has 5-6 shrubs. #18: the coneflower rosettes are slightly softer.
- **Worse:** #17 (now #13).

## 7. Per-family closure

**Prince's Island Park.** The stopped finding was faceted cone flower heads, flat straw-ribbon grasses and bare fill between mounds. *v003 would close it.*
- **Flowers:** the coneflower, rudbeckia, salvia, yarrow and the new open panicle all read as flowers, with no cones. The panicle was the element that would have put cone heads back.
- **Grasses:** arching blade tufts and plume spindles replace the straw ribbons.
- **Bare fill:** closed by the default underlay.
- **Shrubs:** Prince's Island's own review accepted its shrubs at distance. Its promenade cameras look at the beds from 5-15 m, where the kit shrubs read as leafy.
- **Still missing:**
  - a default tuft density high enough for the source's "dense layered mounds" (P2 #13);
  - leaf grain on the underlay (P2 #9);
  - the hull fix (P1 #1), if the family puts a camera within about 4 m of a shrub.

**Halifax Public Gardens.** The stopped finding was carpet-bed plants reading as faceted gems with hard outlines. *v003 would plausibly close it.*
- **Bands:** the carpet bands are flat and clipped, with clean edges and no gems.
- **Cushions:** the ring and strip beds would use the new leaf-skinned cushions, which are no longer gumdrops or pebbles.
- **Hydrangea spine:** a skirted leafy mound.
- **Still missing or at risk:**
  - At Halifax's close `carpet_beds` camera the bands may read as coloured felt or rubber mat, because there is no leaf grain and the florets are sparse (P2 #9).
  - The hydrangea heads are sphere clusters (P2 #6).
  - The hydrangea and begonia hulls show (P1 #1).
- None of these is the gem reading, but #9 should be fixed before the family is rebuilt on the kit.

**Planted green bridge.** The stopped findings were boulders, then gumdrop mounds, solid lilac capsules, and kerb and rail overrun. *v003 would not yet close it.*
- **Closed:**
  - The lavender capsules: the lavender is now spikes over needle foliage, though sparse (P2 #11).
  - The missing grass layer: arching tufts are available.
  - The poppy cups read well.
- **Not closed:**
  1. The shrub range from 0.4 to 1.6 m still shows a smooth lumpy hull at close range (P1 #1). The bridge's `planting_bed` camera is at point-blank range, so the beds would read as leaf-pasted lumps, which is the boulder and gumdrop reading again.
  2. The kit's clearance rule no longer holds canopies inside kerbs (P1 #2). The bridge's P1 was planting overrunning the path rail, the kerb and the outer rail. A rule tested against the hull radius rather than the delivered canopy would reproduce that.
- **Still missing:**
  - a soft purple haze at knitting density;
  - a bright yellow-green bunch-grass variant;
  - the canopy-footprint clearance rule.

**Stepped terraced plaza.** The stopped finding was bougainvillea as faceted balloons with no drape. *v003 would close it.*
- The wall drape is now a continuous canopy over the coping, falling between door and window. It is cut clear of the openings and reads as foliage with bract clusters, trailing canes and a woody armature. The parapet cascade reads the same way. There are no balloons, slits or pot clashes.
- **Still missing (P2):**
  - a carrier edge that does not read as a backing panel (#4);
  - 2-3 spray seeds against stamping (#5);
  - a leafy box ball (#8);
  - a branching trunk (#8).

## Crops written

All crops are in `review/crops_hjtzut/`: b8_fg_leaves (+_mask), b8_shrub (+_mask), band_edge, boxball, carpet_edge, carpet_hydr (+_mask), cascade_left (+_mask), cascade_right (+_mask), cushions, drape_left (+_mask), drape_right (+_mask), fc_b4, fc_b8_east, fc_b8_west, fh_kerb_left, fh_right (+_mask), gc_left, gc_rim_far, hydrangea (+_mask), lavender, panicle, pots, shrub_left (+_mask), shrub_right_base (+_mask), top_b4, top_b8, top_b8_east, top_b8_west, top_plaza, window_jamb.
