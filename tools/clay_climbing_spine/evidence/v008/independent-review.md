# Independent holistic review — climbing spine tower, v008

Reviewer: independent (not the builder). Basis: rendered pixels in `renders/*.png` and `boards/*.png` compared with the locked sources `sources/front.png`, `sources/oblique.jpg` and `sources/top.jpg`. All 18 renders, the 3 sources and the 4 boards were opened at full resolution. I also cropped and upscaled matched regions (the source and render spines side by side, and the east wing transoms in the source front and oblique) to count storeys. I treated builder notes and metrics as orientation only, not as evidence.

## 1. Verdict

**VISUAL_REWORK_REQUIRED.** The tower is about 1.5 to 2 storeys short of the source with the same uniform balcony rhythm (P0). Two P1 defects remain: the spine reads as tan, crumpled low-poly paper rather than pale cleaved stone, and the spine's east flank lacks the smooth light wall with doors that the balconies hang from.

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | **P0** | front vs source front; front_corner vs source oblique; board phone-01 | **Storey count, height and balcony rhythm are wrong.** I counted the east wing transoms in the source oblique: about 15.4 storey modules from the base head to the parapet (about 35 px per storey). The source front gives about 15 (base head about y=650, parapet about y=95, about 37 px per storey). The render front has about 13.4 (base head about y=877, parapet about y=140, about 55 px per storey). Tower height against front width is about 1.01 in the source and about 0.92 in the render, so the render reads visibly squatter on the source-vs-render board. Source balconies rise in 2-storey steps for the lower five, then a **taller gap of about 3.2 to 3.5 storeys** to the sixth, which sits about 2.5 storeys below the parapet. Render balconies are evenly spaced at 2 storeys (y = 270/378/490/600/712/822 in front), so the tall upper gap is missing. | Typical floor count fixed at 13 above the base, taken from the prose ("thirteen floors") rather than the source pixels. The balcony schedule was then built on a uniform modulus. | Add two typical floors (about 15 above the 8 m base). Keep the base and floor-to-floor heights. Move the top balcony to about floor 12 to 12.5 (lower five stay at 1/3/5/7/9) so it sits about 2.5 storeys below the parapet. Raise the spine with the roof so it still stands about 6 m over the parapet, and carry the curtain wall, side-face bars, notch glazing and roof assemblies up with it. |
| 2 | **P1** | front, front_corner, aerial, architecture_close, rest_balconies, roof_terrace vs source front / oblique | **The spine reads as crumpled kraft-paper low-poly, not cleaved light stone.** The shaft is covered in many small, randomly oriented triangles with thin parallel vertical fissures. There are no long cleavage planes and no consistently tilted shadow edges. The source shows large smooth slabs with long diagonal (about 60 to 70 degree) cleavage shadows and bright cream highlights. Tone, measured on the shaft at matched boxes: source front mean 182/144/110 with luminance median 161 and p90 202; render front 155/128/99 with median 140 and p90 172 (front_corner p90 172 against oblique p90 198). The render spine is a mid-tan "cardboard" a full step darker in the highlights. At the matched scale on phone-01 it reads as a different material from the source's pale stone. | Facet size and orientation are still noise-driven. Merging coplanar facets has not produced macro cleavage planes with a dominant dip. The albedo and highlight level are too low and too saturated for the lit faces. | Rebuild the shaft relief from about 1.5 x 3 to 4 m cleaved slabs sharing one dominant dip direction (down to the west, matching the source). Use few, large planar faces per slab with sharp stepped edges 0.3 to 0.8 m deep, so a raking sun casts long diagonal shadow lines. Reduce the fine triangle noise. Raise lit-face albedo toward a pale warm cream (target luminance p90 of about 195 to 205 and median of about 155 to 165 under the review light), keeping the deep-stone tone only in the cleft returns. |
| 3 | **P1** | front_corner, rest_balconies, architecture_close vs source oblique (zoom) and source front | **The spine's east flank and the notch-east wall are wrong.** In both sources, immediately east of the carved front face is a **smooth, pale, full-height stone or concrete flank**. Behind it is a pale recessed wall strip carrying a **dark door or slot opening at each balcony level**, and only then the dark full-height glazing behind the balcony decks. In the render, the faceted tan relief wraps onto the east side face and the balconies meet dark glazing and a bronze post directly. There is no pale wall and no balcony doors, so the balconies have no legible access, and the high-contrast pale strip that frames the balcony stack in the source is missing. | The east side face was given the same carved treatment as the front, and the notch-east wall was modelled as curtain wall. | Make the spine's east side face a smooth pale stone plane (no relief, same palette as the cap). Add a pale recessed wall strip of about 1.5 to 2 m between that flank and the dark glazing, with one dark door opening (with jamb returns) onto each balcony. Keep the dark glazing for the rest of the balcony backs. |
| 4 | P2 | boulder_garden, front | The foot is a separate grey low-poly lump. The tan shaft ends on it in a hard staggered seam with tan "drips" over the grey, so it reads as two objects. (The source foot is also greyer, but mostly because it is in shade, and the stone looks continuous.) | Separate material and mesh for the foot. | Blend the shaft stone into the foot over about 2 m (mixed facets), or use the same pale stone in a slightly cooler tone. |
| 5 | P2 | top, roof_terrace, front_corner | Roof beds are flat rectangular lawn strips along the parapet with sparse tufts. The source has irregular L-shaped beds with shrubs and grasses, and paving threading between the boulders. Roof boulders are a little smaller (about 2.5 m) and whiter than the source's 3 to 4 m warm-grey granite. | Bed outlines carried over from earlier versions. | Reshape the beds into L-shaped planting with shrub masses, use fewer and larger warm-grey boulders, and show more paving. |
| 6 | P2 | top | In plan, the east part of the notch (balcony zone) is about 6 m against about 4.8 m in the source, and the balconies step about 1.8 m past the wing corner where the source shows about 1 m. | Balcony width or notch split. | Trim the east notch by about 1 m and shorten the balcony overhang. |
| 7 | P2 | rear_side, rooftop_plant, left_side | The amenity storey reads as opaque bronze panel cladding over a short dark glass band. The source reads more as bronze fins over glazing. | Panel material without glazing behind. | Turn the panels into fins of about 0.3 m over dark glass. |
| 8 | P2 | rooftop_plant | The camera is tilted down, so the plant fills the lower half and the sky the upper third. | Camera aim. | Lower the target by about 3 m. |
| 9 | P2 | rear, rear_side | The base of the tower is partly hidden by foreground context (the north mid-rise in rear, the glass tower edge in rear_side). The target is still legible. | Camera placement. | Raise or swing the cameras slightly. |
| 10 | P2 | front, east_facade | The fins read slightly golden-yellow against the source's deeper bronze-copper. | Fin albedo. | Shift fin colour about 10% toward red-brown. |

Counts: **P0 = 1, P1 = 2, P2 = 7.**

## 3. Source conformance checklist

| Item | Status | View used |
|---|---|---|
| Silhouette and storey count | **deviates** (P0 #1). The silhouette is correct as a notched slab with a spine over the roof, but there are about 13.3 storeys above the base against the source's about 15, and the tower reads squatter. | front vs source front, front_corner vs oblique, phone-01 |
| Plan: top view 2:1 block | conforms (about 52 x 27 m) | top vs source top |
| Plan: street-front notch | conforms in position and depth (about 19 m wide, 3 to 4 m deep). The east part is slightly wide (P2 #6). | top |
| Plan: amenity block over the north half | conforms. Set back with west, east and south terrace strips, north edge near the north face. | top, rear, rear_side |
| Curtain wall: vision glass and spandrels | conforms. Dark bronze glass, spandrel bands with depth. | glass_close, facade_close |
| Curtain wall: front fin rhythm | conforms (about 2 m spacing on the street front). The fin tone is slightly yellow (P2 #10). | front, facade_close |
| Curtain wall: side-face sunshade bars | conforms. Close fins and horizontal bars on the east and west faces. | east_facade, left_side, right_side |
| Spine width | conforms (about 7 m against about 7 to 8 m in the source) | front, top |
| Spine height above roof | conforms (about 1.3 storeys, about 6 m) | front, front_corner |
| Spine carved relief | **deviates** (P1 #2). The relief is small, random triangulated facets with vertical fissures, with no large cleavage slabs or consistent dip, and the tone is too dark and tan. | front, front_corner, architecture_close, rest_balconies |
| Spine holds | conforms (sparse small holds) | architecture_close, rest_balconies |
| Spine flared foot | conforms in form: wider rocky mass with boulders heaped against it. The material seam is a P2 (#4). | boulder_garden, front |
| Spine cap | conforms (pale flat cap) | front_corner, roof_terrace |
| Notch west glazing | conforms. Dark recessed full-height glazing. | front, facade_close |
| Notch east wall | **deviates** (P1 #3). The pale smooth flank, pale recessed wall and balcony doors are missing, and the faceted relief wraps the east face. | front_corner, rest_balconies vs oblique |
| Balconies: count | conforms (6) | front, front_corner |
| Balconies: levels | **deviates** (P0 #1). Uniform 2-storey spacing; the source's tall gap of about 3.2 to 3.5 storeys before the top balcony is missing. | front vs source front, front_corner vs oblique |
| Balconies: copper edges, railings, decks and soffits | conforms. Copper slab edge, steel picket railing, timber deck and soffit. | architecture_close, rest_balconies |
| Balconies: support and contact | conforms. Slabs bear on the notch wall and spine flank with no floating parts, but there is no door access (P1 #3). | rest_balconies, architecture_close |
| Roof terrace: parapet coping | conforms (light coped parapet) | roof_terrace, top |
| Roof terrace: beds | deviates mildly (P2 #5). Rectangular lawns instead of L-shaped planted beds. | top, roof_terrace |
| Roof terrace: boulders | conforms in placement and contact, slightly small and white (P2 #5) | roof_terrace, front_corner |
| Roof terrace: paving | conforms (light pavers) | top, roof_terrace |
| Amenity block | conforms in massing and setback. The cladding reads opaque (P2 #7). | rear_side, rooftop_plant |
| Roof plant | conforms. Condenser banks, air handlers, ducts and a stair overrun. | rooftop_plant, top |
| Base: canopy | conforms. White canopy along the west wing shopfronts, ending at the spine. | retail_base, boulder_garden |
| Base: shopfronts | conforms. Double-height glazing with white piers. | retail_base |
| Base: lobby glazing and entrances | conforms. Doors in the west shopfront and the notch-east lobby. | retail_base, boulder_garden |
| Boulder garden and plaza planters | conforms. Curved kerbed planters with boulders, shrubs and grass, a second oval planter to the east and a long planter to the west. | boulder_garden, top |
| Street trees and lamps | conforms (tree pits and lamp posts along the sidewalk) | top, boulder_garden, aerial |
| Streets and crossings | conforms. Front street and two side streets with zebra crossings. | top, aerial |
| Context massing | conforms. Tan and red low blocks to the west, a white mid-rise to the north, a white block and a glass tower to the east, low blocks to the south. | aerial, top, left_side, right_side |
| Materials hierarchy | **deviates** (via P1 #2). In the source the spine is clearly the lightest, palest element against dark bronze glass. In the render the spine is a mid-tan only moderately lighter than the fins, which weakens the hierarchy. | front, phone-01 |
| North face, north halves of the side faces, interiors | not visible in the sources. They are coherent with the visible grammar. | rear, rear_side, left_side, interior |

## 4. Camera validity

- No view has the target fully occluded, clipped past legibility, or empty. All 18 cameras are valid.
- rooftop_plant: tilted down, but the plant is legible (P2 #8).
- rear and rear_side: foreground context partly covers the tower base, but the target is legible (P2 #9).
- interior, glass_close and facade_close: close-ups with legible depth (spandrel returns, mullion depth and interior floor plate visible).
