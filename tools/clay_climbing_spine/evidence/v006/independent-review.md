# Independent holistic review — clay-climbing-spine v006 (RLASM v6.1)

Reviewer: independent; I had no part in the build. I opened all three locked sources and all 18 renders at full resolution, plus the four phone boards. I zoomed into the spine crown, the spine relief, the balcony ends, the side faces, the roof boulders and the spine foot. Metadata and the builder's notes were not used as proof. Every finding below comes from rendered pixels compared against source pixels.

## 1. Verdict

**VISUAL_REWORK_REQUIRED.** The spine crown is a white cap plate that cantilevers several metres north over the roof with sky visible beneath it (P0). The spine relief reads as a twisted, diagonally wrapped column with sawtooth arrises, not as the source's straight-edged, vertically cleaved rock prism (P1). The side faces lose their storey rhythm at envelope scale (P1).

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | **P0** (contact / envelope) | right_side, left_side, roof_terrace, rooftop_plant, front, top | **The crown cap floats.** In right_side the beige rock above the roof covers only the southern ~40% of the cap depth (about 27 px of about 67 px). North of it the cap is a black bar with **sky-coloured pixels (≈152,156,159) under it**. In left_side the cap underside renders **pure black (0,0,0)**, again with sky beneath it, so it reads as a thin dark "Π" frame rather than a solid stone block. roof_terrace and rooftop_plant show the cap plate overhanging the rock body on the west/north side by roughly 3–4 m, over open terrace paving. The source oblique and top views show a solid ~7 × 6 m block with a flush coping, and rock on the faces up to the top. | The cap is sized to the full spine footprint, but the rock shell above the parapet is shallower than that footprint (or stops short of the north face). The cap underside has no lit material or has inverted normals. | Make the spine above the roof a full-depth solid prism under the whole cap footprint, ending flush with the coping. Close the north face of the crown with the same rock and stone. Shrink the cap to the prism outline with no more than a 50 mm drip and give it the stone material on all faces. Re-render left_side, right_side and roof_terrace to confirm there is no sky under the crown. |
| 2 | **P1** (fidelity / material) | front, front_corner, aerial, architecture_close, rest_balconies, boulder_garden | **The spine relief has the wrong grammar.** Regularly spaced diagonal ledges (about one per storey) all rise in the same direction for the full height, so the strip reads as a barber-pole / twisted / draped-fabric column. This is very obvious on the phone board next to the source. The source shows mostly vertical fissures with blocky cleaved facets and irregular, deep cast shadows. It has no consistent diagonal banding. The foot (lower two storeys) in the source is a distinctly chunkier, greyer mass of large blocks. In the render the foot is only a slight bulge with the same banding. | The ledge generator uses one global slope sign and a near-constant 2–4 m period. Ledge dominance overwhelms the facet lattice. | Change the dominant fracture direction to near-vertical (±20°) with mixed slope signs. Break the regular period (no two adjacent ledges parallel), cut the ledge count by about half and add vertical fissure shadows. Give the foot its own larger-block facet scale (1.5–2.5 m) and its own shadowing. |
| 3 | **P1** (envelope fidelity) | front, front_corner, architecture_close, rest_balconies, boulder_garden | **The spine arrises are sawtooth, not straight.** Every ledge lip projects past the side planes. Both long edges zigzag in the front view (about 5–10 px on a 113 px wide shaft), and by 30–40 px in architecture_close and rest_balconies. The source arrises are crisp straight lines from plaza to crown (sources/front.png, oblique.jpg). | Ledge lips are pushed outward beyond the envelope at the folds instead of being undercut inward. | Clamp all facet vertices to inside the prism envelope (0 to −0.5 m) on the front and side faces. Form the undercuts by recessing rather than projecting, so the silhouette stays a straight rectangle in every view. |
| 4 | **P1** (rhythm / material hierarchy) | front, front_corner, aerial (east and west side faces) | **The side faces read as a solid bronze plate.** At envelope distance the close fins plus sunshade bars merge into an undifferentiated gold surface with fine vertical hatching. No storey bands and no dark vision glass can be read. Mean colour is close to the source (≈77/62/41 render vs ≈88/64/45 source), but the source east face clearly shows horizontal floor bands and dark glass between the fins in both front.png and oblique.jpg. (The close view east_facade is legible, so the issue is at envelope scale.) | Fin depth and density are too high for the camera distance, and the sunshade bars are too thin and fin-coloured to register as storey lines. | Reduce side-face fin projection or count by about 30–40%. Make the per-floor sunshade bar / spandrel band thicker and darker than the fins so each storey reads at 1440 px whole-envelope scale. Check against sources/front.png at x 700–815. |
| 5 | P2 | rest_balconies, architecture_close, boulder_garden | The west end of each balcony carries a light-grey end block, unpainted relative to the slab edge. It sits in front of the rock with no shadow or bearing. Contact itself is confirmed in top and east_facade. | Slab end cap uses the default material. | Use the copper slab-edge material on the end and add a small contact shadow or bearing plate. |
| 6 | P2 | rest_balconies, east_facade | The balcony slab edges read as the same tan as the timber decks, so there is no copper distinction. | Material reuse. | Use a slightly redder, more saturated copper fascia. |
| 7 | P2 | boulder_garden, front | The spine-foot and plaza boulders are near-icospheric geodesic balls of very similar size. The source boulders are flatter-faced, rounded-angular granite. | Low subdivision with uniform noise. | Flatten 2–3 cleavage planes per boulder and vary the scale (0.6–1.8 m). |
| 8 | P2 | roof_terrace | The largest corner boulders crowd the glazed guard and their bases touch the guard line. The source has a light coped parapet with no glass. | Boulder placement too close to the edge. The guard type differs from the source. | Pull boulders ≥0.6 m in from the parapet. Lower or remove the glass so the coping reads. |
| 9 | P2 | boulder_garden, top | The white canopy stops about 1 m short of the spine. In the source it runs to the spine. | Canopy length. | Extend the canopy to the spine's west face. |
| 10 | P2 | top, boulder_garden | The boulder garden reads as a split semicircle of two wedge planters. The source has two free-curved kerbed lobes with a curving path between them. | Simplified planter outline. | Reshape into two irregular curved lobes. |
| 11 | P2 | top, roof_terrace | Terrace and plaza paving is mid-grey and cool. The source pavers are lighter and warmer. | Palette. | Raise the paving value by about 15% and warm it slightly. |
| 12 | P2 | rear, rear_side | Foreground context blocks hide part of the north and west base. These faces are not in the sources, so it is legibility only. | Camera height or context placement. | Raise the camera slightly or nudge it sideways. |

## 3. Source conformance checklist

| Item | Status | View(s) used / note |
|---|---|---|
| Silhouette and storey count | conforms | front vs sources/front.png: spandrel profile in the notch glazing gives about 13 office floors at ~51 px, over a double-height base, = 15 storeys. Spine rises about 1.4 floors (~6 m) above the parapet. Amenity crown is about 2 floors tall. |
| Plan: 2:1 block | conforms | top: roof ≈ 895 × 440 px (2.03:1) vs source ≈ 765 × 380 px (2.0:1). |
| Plan: street-front notch | conforms | top: notch ≈ 36% of the width (source ≈ 35%), centred, with the spine in it. |
| Plan: amenity block over the north half | conforms (minor) | top: flush with the north face, set in from the west and east parapets. Side offsets are 14.5% / 18% vs source 12% / 16%. |
| Curtain wall: vision glass and spandrels | conforms | facade_close and glass_close: dark bronze glass, spandrel bands, interior depth. |
| Curtain wall: fin rhythm, street front | conforms | front: wider-spaced bronze fins on the wing fronts, matching the source. |
| Curtain wall: side-face sunshade bars | deviates (P1 #4) | east_facade shows them up close. They are lost at envelope scale in front and front_corner. |
| Spine width | conforms | about 0.47 of the west-wing width vs 0.40 in the source, ~7 m. |
| Spine height above the roof | conforms | front and front_corner: about 6 m. |
| Spine carved relief | deviates (P1 #2) | architecture_close and front vs sources/front.png and oblique.jpg: diagonal helical banding instead of vertical cleaved rock. |
| Spine straight-edged prism | deviates (P1 #3) | Sawtooth arrises in front, architecture_close and rest_balconies. |
| Spine holds | conforms | Sparse grey holds in architecture_close and rest_balconies. |
| Spine flared foot | deviates (part of P1 #2) | boulder_garden: only a slight bulge, with no distinct chunkier block mass. Boulders are heaped at the foot and sit on the ground. |
| Spine cap | deviates (**P0 #1**) | left_side, right_side, roof_terrace, rooftop_plant: the cap cantilevers over open air and its underside renders black. |
| Notch west glazing | conforms | facade_close, front: dark recessed glazing with mullions and returns. |
| Notch east wall | conforms | rest_balconies, east_facade: dark glazing carrying the balconies. The source shows a light strip next to the spine, which is ambiguous at source resolution, so not graded. |
| Rest-station balconies: count | conforms | front, front_corner: 6. |
| Rest-station balconies: levels | conforms | Lowest just above the base, larger gap below the top one, matching the source front spacing ratio (≈1.6 vs 1.55). |
| Rest-station balconies: copper edges | deviates (P2 #6) | Edges read as timber tan. |
| Rest-station balconies: railings | conforms | Steel picket railings. |
| Rest-station balconies: support | conforms | Cantilevered slabs bear on the spine and east wing (top, east_facade). They step past the wing face (right_side). |
| Roof terrace: parapet coping | deviates (P2 #8) | A glass guard sits on the coping. |
| Roof terrace: beds | conforms | top: L-shaped planting beds on both wings, U-shaped around the amenity block. |
| Roof terrace: boulders | conforms (P2 #8 placement) | Corner clusters, lumpy rounded-angular. |
| Roof terrace: paving | deviates (P2 #11) | Too grey and cool. |
| Amenity block | conforms | roof_terrace, rooftop_plant: bronze panelled storey over a dark recessed glazed band, set back. |
| Roof plant | conforms | rooftop_plant: 8 condensers, air handlers, duct run, stair overrun box. |
| Base: canopy | conforms (P2 #9) | front, boulder_garden, retail_base: white canopy in front of the west wing shopfronts. |
| Base: shopfronts | conforms | retail_base: mullioned glazing, white piers, depth. |
| Base: lobby glazing | conforms | boulder_garden, front: east-wing lobby glazing. |
| Base: entrances | conforms | Doors in retail_base and boulder_garden. |
| Boulder garden | conforms (P2 #7, #10) | boulder_garden, top: kerbed planters with boulders, grass and shrubs at the spine foot. |
| Plaza planters | conforms | top: east teardrop planter and long west planter present. |
| Street trees and lamps | conforms | top, front, aerial: tree pits and lamp posts along the sidewalk. |
| Streets and crossings | conforms | aerial, top: streets on three sides with zebra crossings. |
| Context massing | conforms | aerial, front, rear: tan and red brick to the west, white mid-rise to the north, white block and glass tower to the east, low blocks to the south, as simple massing. |
| Materials hierarchy | deviates (P1 #2, #4) | Stone is lighter than the glass (conforms). The side faces collapse into flat bronze, and the spine reads as draped fabric rather than stone. |

## 4. Camera validity

- **No view is invalid.** In every whole-envelope and detail camera the target is framed, unclipped and legible.
- **rear and rear_side:** the foreground context blocks and the blue tower hide part of the north and west base. Those faces are not in the sources, so this is P2 #12 only.
- **left_side and right_side:** valid. They are the views that expose the floating crown cap (P0 #1).
- **interior and glass_close:** dark but legible.
