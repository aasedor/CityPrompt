# Independent holistic review — climbing spine tower, v003

Reviewer: independent (not the builder). Evidence: only rendered pixels in `renders/*.png` (all 18 opened at full resolution, with zoomed crops of the spine, base, roof terrace, amenity crown and balconies) compared against `sources/front.png`, `sources/oblique.jpg` and `sources/top.jpg`. Phone boards were opened and match the renders. Builder notes and metadata were not used as proof.

## 1. Verdict

**VISUAL_REWORK_REQUIRED.** The envelope, plan, storey count, notch, spine footprint and balcony stack match the sources, but four P1 defects remain: the spine's relief and tone, the roof and plaza boulders, the boulder garden, and the amenity crown each read visibly unlike the locked sources.

Counts: **P0 = 0, P1 = 4, P2 = 6**

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | front, front_corner, aerial, top, architecture_close, rest_balconies, boulder_garden, east_facade | The spine's carved face reads as a two-tone horizontal camouflage or mosaic. Short horizontal dashes of dark taupe alternate with pale patches at an even ~1.7 m pitch across the whole face, and the shaft looks mid-grey and busy at envelope scale. The source (front and oblique crops) shows one pale warm-grey monolith: large smooth cleaved planes cut by long sinuous **vertical and diagonal** fissures and flakes, with relief shown mainly by soft shadow and no second stone colour. The source's grain runs vertically, the render's horizontally. | Ledge lips on regular diagonal bands at about 1.7 m produce a horizontal rhythm. The darker stone assigned to the undersides and flake sides turns every lip into a dark dash. The facets are small and evenly sized. | Use one light warm-grey material across the spine and let shading alone show depth. Remove the darker under-ledge and flake-side stone, or bring it within ~5% value of the face. Replace the regular diagonal ledge bands with 6–10 long vertical or diagonal fissures and flake edges, each 3–12 m long and irregularly spaced, with large planar facets of 1.5–4 m between them. Keep the ±0.55 m depth. Check against the `sources/front.png` and `oblique.jpg` spine crops at the same framing. |
| 2 | P1 | roof_terrace, front, front_corner, aerial, left_side, right_side, rear, rear_side, top, boulder_garden | The roof boulders are soft, smooth, rounded tan "loaves" heaped and overlapping in dense piles at the wing corners. Peeking over the parapet in front, left_side and right_side, they read as clouds or cotton puffs. The source boulders are crisp-edged, faceted, light-grey granite with flat cleavage faces. They include upright slabs and blocky pieces, set individually in planting with space around each one. The plaza boulders share the same puffy or flat-pebble form. | Over-smoothed boulder generator: subdivision with no planar cuts, a single tan albedo, and cluster placement that packs instances together. | Generate boulders from a convex hull with 3–6 planar cleavage cuts and sharp edges. Vary the aspect ratio, with 30–40% upright slabs taller than wide. Shift the colour to the spine's light warm grey (slightly cooler than now). Place 1–2 m apart, seated in the beds, with no interpenetration. Keep the existing count per wing and the 3–4 m sizes. |
| 3 | P1 | boulder_garden, front, front_corner, top, aerial | The spine-foot garden reads as two flat lawn crescents holding one large rounded boulder, about 8 flattened lozenge "pebbles" and a few grass tufts. In the source (front base crop and top), the same curved kerbed beds are densely planted with dark shrubs and grasses. They hold about 15 granite boulders of mixed size, several upright and angular, crowding up to the spine foot. | Low planting density and the scattering of small flattened boulder instances. Lawn ground fill instead of shrub mass. | Fill both crescents with clustered low shrub masses at about 60–70% cover, darker green than the current lawn, plus grass clumps. Place 12–16 boulders using the cleaved generator from finding 2, 0.6–2.5 m high, including 3–4 upright ones against the spine foot. Keep the kerbs, the path and the east and west planters as they are. |
| 4 | P1 | front_corner, aerial, roof_terrace, rear, rear_side, left_side, rooftop_plant, front | The amenity storey reads as a low clear-glass pavilion. Thin bronze sticks stand at wide spacing in front of see-through glazing that shows a bright white empty interior. In front view its top is level with the spine cap. In the source (oblique and front), the amenity is a darker, dense bronze-panelled crown whose vertical bronze panels dominate the glass. It rises clearly above the spine cap (by about 0.5 storey in the front view) and reads as the warm dark top of the building. | The fins are too thin for their spacing. The glass is too transparent and the interior too bright. The storey height is about one floor, where the source reads as about 1.5. | Widen the amenity fins to 0.3–0.45 m deep bronze panels at the current pitch so that bronze fills about 50–60% of the elevation. Give the amenity the tower's dark bronze glass and dim its interior. Raise the amenity storey height by about 1.5–2 m so its roof edge sits clearly above the spine cap in the front view. Keep the footprint and the plant layout. |
| 5 | P2 | roof_terrace | Above the roof, the spine's west flank is a large plain smooth box face, while the same flank below the roof is carved. This face is not shown in the sources, but the smooth-over-carved change is incoherent. | The cap volume uses a plain material on its flank. | Continue light relief up the west flank to the cap, or carry the smooth face down as a consistent plain return. |
| 6 | P2 | architecture_close, rest_balconies, front | The climbing holds read as tiny pale specks and are effectively invisible at envelope scale. | Holds are small and close in value to the face. | Enlarge them slightly or give them a modest value contrast. Optional. |
| 7 | P2 | top, roof_terrace | The terrace beds are separate side and front strips with boulder heaps on bare paving at each corner. In the source the beds wrap the corners as L-shapes around the boulders. | Corner "courts" replaced the bed corner. | Return each bed around the wing corner and set the boulders within it. |
| 8 | P2 | front, aerial, rear, left_side | The context blocks across the south street are white or grey boxes with blue windows. The source shows low brick blocks there. | Context palette. | Recolour the south-street blocks to red or tan brick. |
| 9 | P2 | front, front_corner, facade_close | The vision glass is near-black, and floor lines and spandrels are barely legible at envelope scale. The source glass reads bronze-tinted, with visible floor rhythm. | Glass value lowered in v003. | Lift the glass value slightly or warm its tint so the spandrel bands read. |
| 10 | P2 | interior | The interior is very dim, with an almost black ceiling. | Interior light lowered in v003. | Add modest ceiling fill. |

No P0 findings. All visible openings show frames and returns. The canopy, balconies, spine foot, planters and boulders all make contact with their supports, and no floating parts were found. Boulders overlap in the image but sit on paving or in beds.

## 3. Source conformance checklist

| item | status | view(s) used | note |
|---|---|---|---|
| Silhouette and storey count | conforms | front, front_corner, f_east crop vs source front | Double-height base plus 13 curtain-wall floors = 15. Wing roof parapet height and the notch silhouette match. |
| Plan: 2:1 block | conforms | top vs source top | Roof measures ~900×450 px, about 2.0:1, matching the source. |
| Plan: street-front notch | conforms | top, aerial | The notch spans ~36% of the width at ~14% of the depth (source 36% / 13%). It is centred, with the spine centred in it. |
| Plan: amenity block over the north half | conforms (footprint), deviates (height and material, see finding 4) | top, rear, front_corner | Footprint ~67% × 68% of the block. Like the source, the east strip is wider than the west, and the north face is flush. |
| Curtain wall: vision glass | deviates (P2) | facade_close, glass_close, front | The glass is near-black and flat. |
| Curtain wall: spandrels | conforms | facade_close, glass_close | Dark spandrel band at every floor. |
| Curtain wall: fin rhythm, street front | conforms | front, front_corner, facade_close | Wider-spaced bronze fins on the south faces. |
| Curtain wall: side-face fins and sunshade bars | conforms | left_side, right_side, east_facade, rear_side | Close fins plus horizontal bars form the grid. |
| Spine: width | conforms | top, front | ~7.5 m. |
| Spine: height above roof | conforms | front, front_corner, roof_terrace | About 1.3 floors, roughly 5–6 m above the wing roof. |
| Spine: carved relief | deviates (P1, finding 1) | architecture_close, front, rest_balconies | Horizontal two-tone mosaic, where the source has pale vertical fissured rock. |
| Spine: holds | conforms (sparse), P2 legibility | architecture_close | |
| Spine: flared foot | conforms | boulder_garden, front base crop | A continuous plinth that flares into the plaza and sits cleanly between the planters. |
| Spine: cap | conforms; P2 for the west-flank smoothness | front, front_corner, roof_terrace | Flat light top. The east flank above the roof is plain, matching the source's plain east return. |
| Notch west glazing | conforms | facade_close, front | Dark recessed glazing with mullion grid. |
| Notch east wall | conforms | architecture_close, rest_balconies, front | Light concrete wall with door and window openings framed with reveals. |
| Balconies: count | conforms | front, front_corner, aerial | 6. |
| Balconies: levels | conforms | front vs source front (normalised) | Height fractions below the roof are 0.17/0.40/0.55/0.69/0.84/0.99, against the source's 0.17/0.39/0.54/0.68/0.82/0.96. The lowest balcony sits at the top of the base and the top gap is larger, both as in the source. |
| Balconies: copper edges, timber decks and soffits | conforms | rest_balconies, rb_bal crop | |
| Balconies: railings | conforms | rest_balconies | Steel pickets on the front and side returns. |
| Balconies: support | conforms | rest_balconies, architecture_close | Cantilevered from the notch-east wall and spine flank, stepping slightly past the east wing, as in the source. |
| Roof terrace: parapet coping | conforms | roof_terrace, top | Light coping. |
| Roof terrace: beds | deviates (P2) | top | Broken into strips rather than L-shapes. |
| Roof terrace: boulders | deviates (P1, finding 2) | roof_terrace, front, sides | Soft tan heaps instead of cleaved grey granite. |
| Roof terrace: paving | conforms | roof_terrace, top | Grid paving. |
| Amenity block | deviates (P1, finding 4) | front_corner, aerial, roof_terrace, rear | Clear-glass pavilion with thin fins, where the source has a dense bronze crown; also too low. |
| Roof plant | conforms | rooftop_plant, rear, top | Condensers (8), air handlers, duct run and stair overrun. |
| Base: canopy | conforms | boulder_garden, retail_base, front | White slab with bronze fascia in front of the west wing shopfronts, ending at the spine. |
| Base: shopfronts | conforms | retail_base | Light piers and framed glazing set back with returns. |
| Base: lobby glazing | conforms | front base crop, right_side | East wing double-height glazing between piers. |
| Base: entrances | conforms | retail_base, boulder_garden | Shop doors, plus the double-height entrance east of the spine. |
| Boulder garden and plaza planters | deviates (P1, finding 3) | boulder_garden, top, front | Kerbs, path, east oval and long west planter match. Planting and boulders are sparse and do not match. |
| Street trees and lamps | conforms | front, top, aerial, boulder_garden | Tree pits and lamp posts line the sidewalks. |
| Streets and crossings | conforms | top, aerial, front | South street plus west and east side streets, with zebra crossings at the corners. |
| Context massing: west | conforms | front, front_corner, aerial | Tan and red-brick blocks. |
| Context massing: north | conforms | top, rear | Light mid-rise. |
| Context massing: east | conforms | aerial, right_side | White block and glass tower. |
| Context massing: south | deviates (P2) | front, aerial | White and grey rather than brick. |
| Materials hierarchy | deviates (P1) | front, front_corner, aerial | Bronze glass and fins read correctly. The spine is not read as the single pale monolith (finding 1), and the crown is lighter than the tower body where the source is darker (finding 4). |

## 4. Camera validity

All 18 views are valid. None has its target occluded, clipped or illegible.
- right_side: the re-aimed wider lens shows the full east face, the roof crown and the plaza. The glass tower on the right does not overlap the target.
- rear and rear_side: the headroom is adequate and the full crown is visible. The foreground blocks stop at the target's base line, and the blue tower in rear_side stays left of the building.
- left_side: the full west face, crown and base are visible.
- east_facade: the top and bottom of the building fall outside the frame, which is acceptable for a facade detail view because the east face and balcony edge stay legible.
- interior: legible but dim (P2 #10).
