# Independent holistic review: climbing spine v004 (RLASM v6.1 clay)

Reviewer: independent; judged only rendered pixels against `sources/front.png`, `sources/oblique.jpg`, `sources/top.jpg`. I opened all 18 renders, the 3 sources and the 4 phone boards at full resolution, plus zoomed crops of the spine, balconies, amenity crown, spine foot and storey bands.

## 1. Verdict

**VISUAL_REWORK_REQUIRED**: the envelope, plan, notch, storey count, balcony count and levels, terrace U and spine-foot garden all match the sources (0 P0). Five clearly visible fidelity defects still block production approval: the spine's relief language, the spine's tone, the roof boulders, the amenity crown rhythm and how the balconies meet the spine (5 P1).

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | front, front_corner, aerial, top, architecture_close, rest_balconies, boulder_garden, east_facade | The spine relief reads as orthogonal stepped blocks and small cubic pockets (a voxel or camouflage pattern). In top it reads as a crumpled field of small facets. The relief breaks the spine's outer arrises, so both long edges are stair-stepped and notched (front_corner right edge, boulder_garden left edge). In front/oblique/top the source spine is a crisp prism with straight arrises. Inside them sit large smooth cleaved planes cut by sinuous, mostly vertical cleft lines, and the side faces are plain. | Relief built from axis-aligned box offsets plus about 110 small flakes up to +0.6 m, applied right to the edges. The mesh was coarsened, which squares off the planes. | Rebuild the relief as about 25–35 large, vertically elongated planes 2–4 m wide and 6–15 m tall, each gently inclined (5–15°) and separated by narrow sinuous V-clefts. Drop the rectangular pockets and most of the small flakes. Keep a 0.3 m plain margin so both front arrises stay straight. Keep the side faces and cap plain. |
| 2 | P1 | front, front_corner, aerial, top, architecture_close, boulder_garden | The spine reads as a mid khaki/buff that is darker than the plaza paving: in top, spine face L≈113 against sidewalk L≈128. It is also visibly darker than the white notch-east wall and canopy beside it, so the spine is not the lightest element of the street front. In the sources it is the palest element: top spine face L≈165 against sidewalk L≈125, the neutral cap reads light grey, and the notch-east strip matches the spine tone. | Albedo sampled from golden-hour pixels (0.62/0.53/0.41), plus a 25% darkening on the cleft faces. | Raise the base albedo to a light warm grey (about 0.80/0.76/0.70 linear-equivalent sRGB), cut the cleft-face darkening to about 10–15%, and tone the notch-east wall to the same family, a hair cooler. Target spine L at least 1.2× the paving in top. |
| 3 | P1 | front, front_corner, aerial, roof_terrace, top, left_side, right_side, rear, rear_side | The roof boulders are near-identical rounded, upright faceted ovoids ("eggs"/"teeth") standing shoulder to shoulder in single file along the parapet beds, in the same buff as the spine. In the sources (oblique, front, top) the boulders are angular cleft granite in a cooler light grey and vary in shape: tall standing slabs, flat-topped blocks, tilted stones. They sit in irregular groups with gaps, and several stand inside the paved part of each wing (top), not only on the edge line. | Stones are instanced from one rounded prototype with small scale jitter, placed along the bed centreline, with the spine material reused. | Author 5–6 distinct prototypes with large planar fracture faces (flat tops, sheared sides, aspect ratios from 1:2.5 slab to 2:1 block), and vary yaw and tilt (≤15°). Give them a cool light-grey granite separate from the spine. Re-place per wing as 2–3 irregular groups with 1–3 m gaps, plus 2–3 stones in the paving, following the source top. |
| 4 | P1 | front, front_corner, aerial, roof_terrace, rooftop_plant, left_side, rear | The amenity crown reads as a deep fluted louvre screen: narrow slats at about 0.8 m pitch with dark gaps, so there are about 40+ slats across the south face. In the sources (front, oblique) it is a flush bronze-panel box: about 18–20 broad panels of roughly 2 m across the same face, thin joints, and a dark glazing band low on the face. The rhythm is about 2–3× too dense and the read is different. | Panels modelled as 0.44 m fins at 0.8 m pitch, 0.4 m deep. | Replace them with flush bronze panels about 1.8–2.0 m wide, 0.05–0.08 m reveals and ≤0.1 m relief over the upper about 2/3 of the storey, with a recessed dark-glazed band below. Keep the height, setbacks and roof plant. |
| 5 | P1 | rest_balconies, architecture_close, roof_terrace, front | The rest-station balconies project south past the spine's front face. In frontal views their west ends overlap the spine's east strip: in rest_balconies the slabs start at x≈565 while the spine arris is at x≈620, and in front the slabs start at x≈740 inside a spine ending at x≈775. In roof_terrace each slab shows an exposed west edge with no railing return and no copper edge. In front and oblique the source balconies butt the spine's east edge, roughly flush with its face, with the railing ending at the stone. | Slab depth is greater than the spine projection and the slab's west edge is placed on the spine's east face plane, with no guard on the overhang. | Start each slab at the spine's east face and limit its depth so the front edge is ≤ the spine face (within 0.1 m). If any overhang remains, add a railing return and a copper edge on the west end. Keep the 6 levels and the small step past the east wing. |
| 6 | P2 | architecture_close, rest_balconies | The holds are small grey cubes in a near-regular 3-column grid. The source holds are sparse and irregular. | Hold placement on a lattice. | Scatter the holds with Poisson spacing and vary their size and tint. |
| 7 | P2 | front, front_corner, architecture_close, rest_balconies | The notch-east wall has a window or door on every floor, so it reads as a stair tower. In the source (oblique, front) the strip is mostly blank, with door openings only at balcony levels. | One opening per storey. | Keep openings only at the 6 balcony levels and the ground floor. |
| 8 | P2 | left_side, right_side, rear_side | Light interior props or panels show through the top-floor curtain wall, and there are pale patches between the fins at the NE corner. | Interior props are not dimmed near the top floors, and the corner glazing is see-through. | Dim or cull those props and make the corner spandrel opaque. |
| 9 | P2 | boulder_garden, top | The east crescent planter runs across the whole notch-east ground frontage, right against the glazed opening. In the source top it stops near the spine and leaves open paving in front of the east lobby. In the source the boulders hug the spine foot. Here the large stone sits off the foot in the west crescent. | Planter arc radius and extent. | Shorten the east crescent so it ends near the spine's east third, keeping 2 m+ of paving clear before the glazing. Move 1–2 large stones against the flared foot. |
| 10 | P2 | top, front, retail_base | The canopy is shallower (about 2.4 m against about 4.4 m in the source top) and does not return around the west corner, as it does in the source front. | Canopy depth parameter. | Deepen it to about 4 m and add a short return on the west face. |

## 3. Source conformance checklist

| item | status | view used / note |
|---|---|---|
| Silhouette and storey count | conforms | front vs source front: about 14 curtain-wall floor bands over a double-height base in both (row-profile count; pitch ≈54 px render, ≈40 px source). Balcony spacing ratio matches (top gap ≈3 floors, others ≈2). |
| Plan: 2:1 block | conforms | top: 885×445 px ≈ 1.99:1, source 760×380 = 2:1. |
| Plan: street-front notch | conforms | top: notch ≈37% of width in both; depth and spine position match. |
| Plan: amenity block over the north half | conforms | top: about 59% of depth from the north, against about 63% in the source; side setbacks about 14%/17.5% against 12%/16%. |
| Curtain wall: vision glass, spandrels | conforms | facade_close, glass_close: dark bronze glass, spandrel band per floor, fins standing proud with depth. |
| Curtain wall: fin rhythm | conforms | front: street-front fins wider spaced than the side faces, as in the source. |
| Curtain wall: side-face sunshade bars | conforms | east_facade, front_corner: close fins plus horizontal bars per floor. |
| Spine: width | conforms | front about 14% and front_corner about 20% of the facade, against source about 16%/19%. |
| Spine: height above roof | conforms | front: about 1.35 storeys over the roof, against source about 1.4. |
| Spine: carved relief | deviates (P1 #1) | front_corner, architecture_close: voxel-stepped blocks and broken arrises against the source's large cleaved planes. |
| Spine: holds | deviates (P2 #6) | architecture_close: grid-regular cubes. |
| Spine: flared foot | conforms | boulder_garden, front: the foot swells at grade. |
| Spine: cap | conforms | front_corner, top: plain capped top. |
| Spine: tone | deviates (P1 #2) | top, front: darker than the paving and the white notch wall. |
| Notch west glazing | conforms | front, facade_close, boulder_garden: dark recessed glazing. |
| Notch east wall | deviates (P2 #7) | architecture_close: light wall present, but openings on every floor. |
| Rest-station balconies: count, levels | conforms | front: 6, spacing ratio matches the source. |
| Rest-station balconies: copper edges, railings, timber decks | conforms | rest_balconies, top. |
| Rest-station balconies: support and contact with spine | deviates (P1 #5) | rest_balconies, roof_terrace: overrun the spine face, exposed unguarded west edge. |
| Roof terrace: parapet coping | conforms | roof_terrace, top. |
| Roof terrace: L-beds | conforms | top: L-beds wrap the corners. |
| Roof terrace: paving | conforms | top, roof_terrace. |
| Roof terrace: boulders | deviates (P1 #3) | roof_terrace, front_corner, top: uniform eggs in single file. |
| Amenity block: height and setback | conforms | front: crown about 0.7 storey over the spine cap, against source about 0.6. |
| Amenity block: facade rhythm | deviates (P1 #4) | front_corner vs oblique: louvre slats against broad flush panels. |
| Roof plant: condensers, AHU, ducts, stair overrun | conforms | rooftop_plant, rear. |
| Base: canopy | deviates (P2 #10) | top, retail_base: present but shallow, no west return. |
| Base: shopfronts, lobby glazing, entrances | conforms | retail_base: piers, set-back glazing, double doors with reveals. |
| Boulder garden and plaza planters | conforms in topology (two kerbed crescents with a path to the foot, east teardrop with one boulder, long west planter); deviates in east-crescent extent (P2 #9) | top vs source top, boulder_garden. |
| Street trees and lamps | conforms | front, top: tree pits and lamp posts along the south walk (low-poly crowns acceptable for clay). |
| Streets and crossings | conforms | top, aerial: three streets, crossings at the SW and SE corners. |
| Context massing | conforms | front, aerial, rear: tan and red blocks to the west, white mid-rise to the north, white block and glass tower to the east, low blocks to the south, all as simple masses. |
| Materials hierarchy | deviates (P1 #2, #3) | The spine should be the lightest element on the street front and the roof stones a distinct cool granite. Here the spine sits below the paving and the white wall in value, and the stones share the spine's buff. |
| North face, north half of the side faces, interiors | not visible in sources; coherent | rear, rear_side, interior: same fin and spandrel grammar, dim office interior. Minor see-through artefacts (P2 #8). |

## 4. Camera validity

All 18 views are valid. The target is legible in every view, and no view has the target occluded or the asset clipped in a way that defeats its purpose.
- rear and rear_side: foreground context masses cover part of the north face base and the lower west corner. The north face, crown and roof remain legible.
- east_facade: the spine and balconies are cut by the left frame edge. The subject is the east facade, which is fully legible.
- interior: dim but legible (desks, glazing wall, view into the notch).
