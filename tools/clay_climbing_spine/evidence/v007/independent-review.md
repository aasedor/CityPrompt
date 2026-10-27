# Independent holistic review: clay-climbing-spine v007 (RLASM v6.1)

Reviewer: independent; no part in the build. Evidence is the 18 renders in `renders/`, the four phone boards and the locked sources (`sources/front.png`, `sources/oblique.jpg`, `sources/top.jpg`), all opened at full resolution. I also checked crops and luminance samples from the same pixels. Builder notes, logs and metrics were used only to find my way around, not as proof.

## 1. Verdict

**VISUAL_REWORK_REQUIRED.** The envelope, plan, storey count and the four identity elements are all present, and I found no P0. Two P1 defects block approval. First, the spine, the main identity element, reads as a shallow, pale, triangulated low-poly prism rather than the deeply cleaved, strongly shadowed rock face in the sources. Second, the rest-station stack sits about one storey low: the lowest station lands on the retail-base head instead of one glazed storey above it.

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | front, front_corner, aerial, architecture_close, rest_balconies, roof_terrace, phone-01 | The spine shaft reads as crumpled paper or a low-poly triangle mesh. Its relief is shallow and its highlights are flat: luminance std/mean is 0.13–0.15 in front/front_corner and 0.10 in architecture_close, against 0.25–0.29 on the source spine, and the 95th-percentile luminance is only about 11 levels above the median (source: about 45). The fissures and cleave faces in the sources (long dark vertical fissures, big planar faces with hard shadow edges) are not legible at whole-envelope scale. Close up, the small triangles (0.4–1.5 m) break the 1–2 m cleaved blocks into a noisy mesh instead of a few large planar faces. The shaft tone is a dull greige (≈135/128/114 RGB), not a warm light beige clearly separated from the glass. | Block depth of 0–0.5 m is too small for the 7.4 m face. Facets are triangulated per block instead of merged into large planar cleave faces. Soft, overcast-only lighting with no directional key flattens the relief. | Keep the straight envelope, but recess the base plane so blocks can stand 0.4–1.0 m proud. Merge the facets of each block into 2–4 large planar cleave faces, and cut 6–10 continuous vertical fissures 0.2–0.4 m deep and 0.15–0.3 m wide down the full shaft. Add a warm directional key light, low and from the SW (25–35° elevation), for the whole-envelope views. Raise the shaft albedo toward the source beige (about 190/160/125 before lighting). Re-render front, front_corner and architecture_close, then confirm that the spine's luminance spread reaches at least 0.22 std/mean and that its fissures read in front. |
| 2 | P1 | front, front_corner, aerial, boulder_garden, phone-01 | The six rest stations sit about one storey too low against the base. In render front and front_corner, the lowest station's slab lies on the retail storefront head and canopy line, 0.1–0.2 storey above it. In both sources it sits one full dark-glazed office storey above the storefront head, with the deep entrance recess under it (base comparison crop: source gap ≈ 1.0 storey, render ≈ 0.2). The east-wing storefront also measures about 2.9 office-storey heights against about 2.5 in the source. The spacing between stations and the larger gap at the top are correct, so the whole stack has slipped down relative to a base that is too tall. | The station levels are keyed to floors 3, 5, 7, 9, 11 and 14 over a base that is about 0.5 storey too tall. | Reduce the base head to about two office storeys plus mezzanine, so the storefront is about 2.5 office storeys tall as in the source. Then place the stations so the lowest has one full glazed office storey below it (floors 4, 6, 8, 10, 12, with the top station kept at its current height under the roof, about 2.1 storeys below the parapet). Re-check front against the source front for the gap between the lowest station and the base head. |
| 3 | P2 | front, front_corner, east_facade, right_side, rear_side | The side faces show fins at about 1.6 m with one dark floor band per storey, and read as a dark grid. In the source east face, close bronze fins are crossed by paired thin light-bronze sunshade bars on each storey and read as a bronze screen. | v007 replaced the bars with a dark spandrel band. | Give the side-face band the bronze fin material, or split it into two thin bronze bars per storey proud of the fins. |
| 4 | P2 | boulder_garden, front, front_corner | The foot is correctly greyer than the shaft (the source foot is about 110/115/120 in shade). However, the change happens at a ruler-straight horizontal seam at the canopy line, and the foot facets are still small triangles, not 1.5–2.5 m blocks. | The foot is a separate prism with its own triangulated facet set. | Stagger the seam over about 1–2 m and use the merged large-block faceting from #1 on the foot. |
| 5 | P2 | roof_terrace, top, aerial | The roof beds are straight-edged turf strips running round the perimeter, where the source has organic beds set within the paving. The roof boulders stand upright like eggs, lined up in rows; the source boulders are lumpier and more varied, some lying low. | Beds are parametric strips; boulder orientation is constrained upright. | Bend the bed edges, vary boulder tilt and scale, and lay 30–40% of the boulders low and wide. |
| 6 | P2 | rooftop_plant, top, roof_terrace | The amenity-roof plant is all white or pale grey, with low contrast and sparse coverage (one overrun, one AHU, one 8-unit condenser group, one duct). The source has a denser field of grey condensers and ducts. | Plant material is the same tone as the roof membrane; the plant count is low. | Use a mid-grey plant material and add a second condenser bank and duct runs. |
| 7 | P2 | top, front_corner, rest_balconies | The stations step only about 0.7 m past the east-wing notch corner; the source shows about 1.5 m. | East-end extent. | Extend the east ends by about 0.8 m. |
| 8 | P2 | top, front_corner, boulder_garden | The two boulder-garden lobes are smaller and more regular than the source's kidney-shaped planter with its heaped boulders (known #10, unchanged). | Unchanged from v006. | Enlarge and irregularise the west lobe and heap larger boulders against the foot. |
| 9 | P2 | aerial, front, top | The context is a little off-palette: the north mid-rise is grey-blue rather than white, and one block across the south street is a light mid-rise rather than low brick. | Context colour and height presets. | Recolour the north mid-rise white and lower the south block to brick walk-up height. |
| 10 | P2 | rooftop_plant | About half the frame is empty sky, and the target sits in the lower half. | Camera tilt. | Tilt the camera down about 10° or move it closer. |

**Counts: P0 = 0, P1 = 2, P2 = 8.**

## 3. Source conformance checklist

| item | status | view(s) used | note |
|---|---|---|---|
| Silhouette and storey count | conforms | front, front_corner, east-face band profile | 2-storey base plus 13 curtain-wall storeys, a set-back amenity storey, and the spine about 1.1 storeys above the parapet (source ≈1.1). The base is about 0.5 storey too tall (see #2). |
| Plan: 2:1 block | conforms | top vs source top | Render about 895×445 px (2.01:1); source about 765×380 (2.0:1). |
| Plan: street-front notch | conforms | top | Render notch about 36% of the frontage and about 3.6 m deep; source about 34% and about 3.4 m. The spine is centred in the notch and runs about 4.7 m north of the notch back wall (source about 5 m). |
| Plan: amenity block over north half | conforms | top, aerial | About 68% of the width, held to the north edge, with the paved terrace wrapping it on three sides. |
| Curtain wall: vision glass and spandrels | conforms | facade_close, glass_close | Dark bronze glass. Spandrels are about 29% of the storey height and openings show depth behind the fins. |
| Curtain wall: front fin rhythm | conforms | front, facade_close | Wider-spaced slim bronze fins, about 13 across the east-wing front (source about 12). |
| Curtain wall: side-face sunshade bars | deviates (P2 #3) | east_facade, front | Close fins are present, but the bars are replaced by one dark band per storey. |
| Spine: width | conforms | front, top | Spine/frontage ratio 0.14 against 0.16 in the source. |
| Spine: height above roof | conforms | front, roof_terrace | About 1.1–1.2 storeys above the parapet, finishing below the amenity top as in the source. |
| Spine: carved relief | deviates (P1 #1) | front, architecture_close | The relief is too shallow and triangulated, the fissures are not legible, and the tone is dull. |
| Spine: holds | conforms | architecture_close, rest_balconies | Sparse small holds. |
| Spine: flared foot | conforms (P2 #4) | boulder_garden | Wider grey rock mass with boulders heaped against it. The seam is too straight. |
| Spine: cap | conforms | roof_terrace, front_corner | Flush light coping on a solid block that rock wraps on all four faces. |
| Notch west glazing | conforms | front, facade_close | Dark recessed gridded glazing between the west wing and the spine. |
| Notch east wall | conforms | rest_balconies, front | Dark glazed wall carrying the stations. |
| Rest stations: count | conforms | front, front_corner | 6. |
| Rest stations: levels | deviates (P1 #2) | front, front_corner, boulder_garden | Spacing and the larger top gap match, but the stack is about one storey low against the base head. |
| Rest stations: copper edges, timber decks/soffits, railings | conforms | rest_balconies, architecture_close | Copper slab edges, timber deck and soffit, steel picket rails with end returns. |
| Rest stations: support / contact | conforms | rest_balconies, east_facade | Cantilevered from the notch east wall. No floating; the west ends stand clear in front of the spine's east edge, as in the source. |
| Roof terrace: parapet coping | conforms | roof_terrace, top | Light coping that returns round the notch. |
| Roof terrace: beds | conforms (P2 #5) | top, roof_terrace | L-shaped beds are present, but straight-edged. |
| Roof terrace: boulders | conforms (P2 #5) | front, roof_terrace | Large clusters show above the parapet in front, as in the source. The forms are too upright and uniform. |
| Roof terrace: paving | conforms | top, roof_terrace | A U-shaped paved band round the amenity block. |
| Amenity block | conforms | roof_terrace, rear_side, front_corner | Bronze-finned storey over dark recessed glazing, set back over the north part. |
| Roof plant | conforms (P2 #6) | rooftop_plant, top | Overrun, AHU, condensers and duct are present, but too pale and sparse. |
| Base: canopy | conforms | front, retail_base, boulder_garden | White canopy along the west-wing shopfronts, running to the spine. It abuts the foot cleanly. |
| Base: shopfronts | conforms | retail_base | Tall glazing with a transom and doors, recessed behind white piers. |
| Base: lobby glazing and entrances | conforms | boulder_garden, front | East lobby glazing with doors beside the spine foot. Base height runs about 0.5 storey tall (#2). |
| Boulder garden and plaza planters | conforms (P2 #8) | top, boulder_garden | Two curved kerbed lobes with a path to the spine, boulders, grasses and shrubs, plus an east oval planter and a long west planter, all matching the source top. |
| Street trees and lamps | conforms | top, front, boulder_garden | Tree pits and lamp posts along the south and side sidewalks. |
| Streets and crossings | conforms | top, aerial | South street and both side streets, with zebra crossings at the corners. |
| Context massing | conforms (P2 #9) | front, aerial, left_side | Tan and red-brick low blocks to the west, a mid-rise to the north, a white block and glass tower to the east, and low blocks to the south. |
| Materials hierarchy | deviates (P1 #1) | front, phone-01 | The order glass < bronze < stone holds, but the spine stone is too dull and flat to dominate as it does in the source. |
| North face, rear halves of the side faces, interiors (not shown in the sources) | coherent | rear, rear_side, left_side, interior | The visible fin and band grammar continues coherently; the interior shows a furnished office floor with the spine seen through the notch glazing. |

## 4. Camera validity

No view is invalid. Every whole-envelope view (front, front_corner, aerial, top, left_side, right_side, rear, rear_side) shows the complete asset, unclipped and legible. In right_side, rear and rear_side, large context towers fill much of the frame, but none overlaps the target. Every detail view frames its target legibly (facade_close, architecture_close, glass_close, boulder_garden, rest_balconies, roof_terrace, retail_base, interior, rooftop_plant, east_facade). The only weakness is rooftop_plant, where about half the frame is empty sky (P2 #10).
