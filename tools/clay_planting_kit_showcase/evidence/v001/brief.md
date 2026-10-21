# Review brief: shared planting kit showcase v001

This is not a catalogue building. It is a showcase of a shared planting kit that four park families will reuse.
There are no locked catalogue sources. The question is whether the kit's plants read as real, grounded,
smooth planting at eye level and from the air, closing the planting findings that stopped four park families.

## Renders (1440 px, 32 samples, rendered from the re-imported optimised GLB)
- /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/plantkit/v001/renders/eye_arching_grass.png
- /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/plantkit/v001/renders/eye_bedding_band.png
- /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/plantkit/v001/renders/eye_carpet_bed.png
- /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/plantkit/v001/renders/eye_flower_heads.png
- /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/plantkit/v001/renders/eye_groundcover.png
- /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/plantkit/v001/renders/eye_perennial_bed.png
- /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/plantkit/v001/renders/eye_perennial_drift.png
- /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/plantkit/v001/renders/eye_shrub_mass.png
- /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/plantkit/v001/renders/front_corner.png
- /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/plantkit/v001/renders/top.png

Phone boards: /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/plantkit/v001/boards/phone-01-kit-showcase.png /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/plantkit/v001/boards/phone-02-kit-showcase.png 

Build report: /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/plantkit/v001/build-report.json (build_valid, carrier aperture audit, instancing stats).

Layout: eight kerbed beds on a 29 x 22 m lawn with two gravel walks. South row: flower heads, perennial drift,
arching grass, shrub mass. Middle row: groundcover, bedding rings, a Halifax-style leaf carpet bed. North: a
Prince's-Island-style perennial bed. Cameras: front_corner (elevated oblique), top, eight eye-level views at 1.6 m.

## The findings the kit must close (read each review)
- Prince's Island Park v003: /home/user/CityPrompt/tools/clay_princes_island_park/evidence/v003/independent-review.md (faceted cone flower heads, flat straw-ribbon grasses, bare fill between mounds)
- Halifax Public Gardens v002/v003: /home/user/CityPrompt/tools/clay_halifax_public_gardens/evidence/v002/independent-review.md and evidence/v003 (carpet-bed plants read as faceted gems, hard outlines)
- Planted green bridge v002/v003: /home/user/CityPrompt/tools/clay_planted_green_bridge/evidence/v003/independent-review.md (boulders, then gumdrops and solid lilac capsules)
- Stepped terraced plaza v003: /home/user/CityPrompt/tools/clay_stepped_terraced_plaza/evidence/v003/independent-review.md (bougainvillea as faceted balloons)
Look at those families' renders in the same evidence folders for comparison.

## Standard
- /home/user/CityPrompt/docs/HIGH_QUALITY_3D_PARK_MEMORY.md (conservatory benchmark: legible plan, controlled richness, grounded complete 3D at pedestrian height).
- Reference photo-style images of a real botanical garden: /home/user/CityPrompt/frontend/public/archetypes/openspaces/botanical-garden/variant_0.png, variant_0_angle_60.jpg.

## Conformance checklist
1. Flower heads read as flowers (daisy, spike, umbel, hydrangea), not gems, cones or balls.
2. Grasses read as arching blade tufts, not flat ribbons or straw sheets.
3. Shrub masses read as loose leafy shrubs, not boulders, gumdrops or lumpy topiary.
4. Groundcover hides bare fill; no visible bare mulch where a bed is meant to be full.
5. Carpet bedding and bedding bands read as clipped low planting with clean edges, not puffy tubes or sausages.
6. Every plant is grounded: no floating, no plants intersecting kerbs or walks, all within its bed.
7. No black patches, slots, wedges or z-fighting anywhere (coplanar or coincident faces).
8. Smooth shading where curvature is intended; no faceting visible at 1440 px eye level.
9. Variation: no obvious clones in a row; drifts look planted, not stamped.
10. Aerial read: from front_corner and top, beds read as planting with legible pattern.
11. Size and instancing: GLB under 4,194,304 bytes; instances survive the round trip (build report).
12. The kit could plausibly close each of the four families' planting findings listed above (say which, if any, it would not).

Severity: P0 = broken render or a kit element that reads as a different object; P1 = a kit element that would
reproduce one of the four families' failed findings, or any visible defect at review scale (black patch, floating
plant); P2 = minor polish.
