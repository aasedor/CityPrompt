# Independent holistic review: clay climbing spine v002 (RLASM v6.1)

Reviewer: independent; not the builder. Evidence: the three locked sources (`sources/front.png`, `sources/oblique.jpg`, `sources/top.jpg`), all 18 renders opened at full 1440x1080, and the four phone boards. Builder notes, counts and metadata were not used as proof.

## 1. Verdict

**VISUAL_REWORK_REQUIRED**: the envelope, plan, storey count, notch, six balconies and amenity block now match the sources. But the `right_side` whole-envelope camera clips the roof crown (P0). The spine still reads as a flat, speckled white panel rather than the source's deeply carved rock, and the roof and plaza boulders read as small faceted crystals rather than massive rounded granite (P1).

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | **P0** | right_side | The top frame edge (y=0) cuts through the glazed amenity storey and the spine shaft above the roof: the amenity roof, its plant and the spine cap are out of frame. Building pixels run straight into the top border from about x 385 to 940, so this whole-envelope east view does not show the full asset. | The re-aimed camera (lower east-street block, glass tower moved north) was tilted or framed too low. Its frustum stops below the amenity parapet. | Raise the target point or widen the FOV until the amenity parapet, roof plant and spine cap clear the top edge by at least 5% of frame height. Keep the base and east street in frame. Re-render right_side only. |
| 2 | **P1** | front, front_corner, architecture_close, rest_balconies, boulder_garden, phone-01 | Spine relief is almost invisible. The source has continuous, deep, sun-and-shadow carved flakes and ledges over the full face (strong dark diagonal shadow ledges every 1–2 m). The render shows a nearly flat light panel with faint low-contrast triangular facets. On the phone board the source spine reads as sculpted rock and the render reads as a plain white strip. | The relief is limited to about 0.42 m inward-only carving on a straight prism. Flake sides are only slightly darker, and the facets are too few and too large, with no overhanging ledge undersides to throw shadow. | Raise carving depth to about 0.8–1.2 m peak (still inside the 7.4 m envelope). Add stacked ledge bands with downward-facing undersides at roughly 1.2–2 m pitch and continuous vertical flake ridges across the whole face. Darken the flake and ledge undersides one more step so the relief survives at phone scale. Re-check front, front_corner and architecture_close. |
| 3 | **P1** | front, front_corner, architecture_close, rest_balconies, roof_terrace, top | Holds dominate the spine. About 160 high-contrast charcoal box holds cover the face evenly as a dotted speckle, the most legible texture on the spine. In the source, holds are sparse and barely visible next to the carved relief. | Hold count and contrast are tuned as an identity cue rather than to match source pixels. The relief (finding 2) is too weak to compete with them. | Cut holds to about 40–60, cluster them along two or three climbing lines, and shrink them about 30%. Shift their colour toward mid warm grey so they read only at close range (architecture_close) and disappear at whole-envelope distance. |
| 4 | **P1** | front, front_corner, aerial, roof_terrace, right_side, top, phone-01 | Roof boulders are under-scaled and the wrong form. In the source front and oblique views, many massive rounded tan granite boulders (about 3–4 m) crowd the front corners of both wings and rise a full storey above the coping. In render front they barely clear the parapet (about 1.5 m showing). In roof_terrace and right_side, the tall ones are pointed hexagonal "crystal" prisms and the rest are low-poly white icospheres. They sit one at a time in a single row, about 7 per side, where the source has dense clusters of 10–14 per side. | Boulder generator uses stretched low-subdivision icospheres or prisms in near-white, spread evenly along a narrow bed strip. | Replace them with rounded, irregular boulder meshes (smoothing at least 2, squash 0.7–0.9, no pointed tips) in warm tan-grey granite. Cluster 4–6 large boulders (3–4 m) at each front wing corner and along the street-half terrace edge, with smaller ones between. Boulders sit on the paving or beds, not strictly in a single strip. Check that in render front they rise about one storey above the coping. |
| 5 | **P1** | boulder_garden, front, front_corner, top, phone-01 | The spine foot is a small pile of separate angular shards about 4.6 m tall, and the plaza "boulders" at the foot are tall faceted crystal prisms. In the sources, the foot is a continuous, bulging, rock-textured plinth that swells wider than the shaft through roughly the full double-height base. One large rounded boulder (about 2.6 m) and many rounded cobbles sit in the curved planters. | The flare is built as loose broken pieces over only the bottom 4.6 m. The plaza boulders use the same crystal-prism generator as the roof. | Model the foot as one continuous flared rock mass rising to the base head (about 8–10 m). Swell it about 0.8–1.5 m past the shaft faces at grade, with carved relief matching the shaft. Swap the plaza boulders to rounded granite forms (same fix as finding 4). Keep the 2.6 m boulder rounded and seated against the foot. |
| 6 | P2 | front_corner, retail_base, boulder_garden | The canopy fascia is plain white. The source shows a dark bronze fascia band on the canopy edge. | Single material on the canopy slab. | Add a 0.4–0.6 m dark bronze fascia band. |
| 7 | P2 | top, front | The west planter is a short (about 4 m) single box. The source shows a long, roughly 10 m run of planters along the west shopfronts. | Planter length or count. | Extend it to a long planter or a row of beds along the west shopfront. |
| 8 | P2 | architecture_close, boulder_garden | Tiny black dots or cubes sit at the corners of the notch-east wall window and door frames. | Stray micro-geometry such as corner caps or anchor markers. | Delete or hide the corner markers. |
| 9 | P2 | left_side, front, facade_close | The curtain wall reads semi-transparent and hollow. Bright rectangles from the opposite glazing show through the upper west face, and interior slab shadows make diagonal bands on the front. | Low-opacity glass shader with an empty interior. | Raise glass reflectance or darkness on the envelope shader (keep interior visibility for the interior view only). |
| 10 | P2 | front, rest_balconies | The balcony stack sits about one storey higher than in the source. The top balcony is about 1.3 storeys below the roof versus about 2.5 in the source. Spacing (3, 2, 2, 2, 2 storeys) matches. | Stack base level offset. | Lower the whole stack by one floor if the next evidence pass confirms it. |
| 11 | P2 | boulder_garden, front | The notch-east wall inside the double-height base shows two stacked single-storey openings, not one double-height entrance. | Upper-floor opening module repeated into the base. | Use one double-height door bay at grade. |
| 12 | P2 | front, left_side, aerial | West-street context reads as tan and grey blocks with little red brick. The source shows mixed tan and red brick walk-ups. | Context palette. | Recolour one or two west-street blocks red brick. |
| 13 | P2 | rear | The spine cap touches the top frame edge behind the amenity storey. This view does not target the spine. | Tight framing. | Add slight headroom. |
| 14 | P2 | roof_terrace, top | Terrace beds are uniform strips along the parapet. The source mixes beds and paving paths around the boulders. | Simplified bed outline. | Break the strips into L-shaped and irregular beds with paving paths between them. |

## 3. Source conformance checklist

| item | status | view(s) used | note |
|---|---|---|---|
| Silhouette and storey count | conforms | front, front_corner, left_side | Double-height base, 13 curtain-wall floors (spandrels counted on the west wing front and the notch-east wall openings), amenity storey and spine above. Proportions match source front and oblique. |
| Plan (2:1 block, street-front notch, amenity over north half) | conforms | top vs source top, aerial | Notch is about 36% of the width (source about 35%) and shallow at roof level as in the source. Amenity covers about 63% of the depth with about 7–9 m side setbacks (source about 6.5–8.5 m). The spine cap extends about 5 m north of the notch back, as in the source. |
| Curtain wall: vision glass, spandrels | conforms (P2 transparency) | facade_close, glass_close | Dark bronze glass with dark flush spandrels per floor. Glass reads too see-through (finding 9). |
| Curtain wall: fin rhythm | conforms | front, facade_close vs source front and oblique | Front fins about 1.2–1.3 m, matching the source's roughly 14 fins per wing front. |
| Side-face sunshade bars | conforms | right_side, east_facade, rear_side vs source oblique east face | Close fins plus horizontal bars read as a dense bronze louvre, as in the source. |
| Spine: width | conforms | top, front | About 7.5 m. |
| Spine: height above roof | conforms | front, front_corner | About 6 m (about 8.5–9% of the tower height above the parapet in both source and render). |
| Spine: carved relief | **deviates (P1)** | front, architecture_close, phone-01 | Finding 2. |
| Spine: holds | **deviates (P1)** | architecture_close, rest_balconies | Finding 3. |
| Spine: flared foot | **deviates (P1)** | boulder_garden, front | Finding 5. |
| Spine: cap | conforms | front_corner, roof_terrace, top | Flat plain cap. |
| Notch west glazing | conforms | facade_close, front | Dark recessed glazing with dark mullions and a visible recess return. |
| Notch east wall | conforms (P2 items) | architecture_close, rest_balconies | Light concrete wall with door and window openings. Openings show a thin reveal and the doors show the interior. Corner-dot artifacts (finding 8) and the base openings (finding 11) are P2. |
| Rest-station balconies: count | conforms | front, rest_balconies, top | Six. |
| Rest-station balconies: levels | conforms (P2 offset) | front | Spacing matches the source. The stack is about one floor high (finding 10). |
| Rest-station balconies: copper edges, railings, timber | conforms | rest_balconies, architecture_close | Copper-tone edges, timber decks and soffits, steel picket railings. |
| Rest-station balconies: support and contact | conforms | rest_balconies, architecture_close, roof_terrace, right_side | They span from the spine to the east wing and project past both faces, with the west end lapping in front of the spine as in source oblique. No visible gap or float. |
| Roof terrace: parapet coping | conforms | roof_terrace, front_corner | Light coping. |
| Roof terrace: beds | conforms (P2 simplification) | top, roof_terrace | L and U bed strips (finding 14). |
| Roof terrace: boulders | **deviates (P1)** | front, roof_terrace, right_side | Finding 4. |
| Roof terrace: paving | conforms | top, roof_terrace | Paved U terrace on the street half. |
| Amenity block | conforms | front_corner, roof_terrace, rear, rear_side | Glazed storey with bronze fins, set back over the north part of the roof, flush with the north face. |
| Roof plant | conforms | rooftop_plant, top | Eight condensers, air handlers, ducts and a stair overrun. |
| Base: canopy | conforms (P2 fascia) | retail_base, boulder_garden | White canopy in front of the west wing shopfronts (finding 6). |
| Base: shopfronts | conforms | retail_base | Double-height glazing between piers, with depth. |
| Base: east lobby glazing | conforms | front, top | Full-height piers with a light base head. |
| Base: entrances | conforms | retail_base, boulder_garden | Entrances present. |
| Boulder garden and plaza planters | **deviates (P1 boulder form)** | boulder_garden, top | Curved kerbed planters with a path and the east oval planter are present. Boulder form is wrong (finding 5). The west planter is short (finding 7, P2). |
| Street trees and lamps | conforms | front, top, boulder_garden | Trees in pits and lamp posts along the south and east sidewalks. |
| Streets and crossings | conforms | top, aerial | South street and both side streets, with crosswalks at the corners. |
| Context massing | conforms (P2 palette) | front, aerial, rear, top | White mid-rise to the north, white block and glass tower to the east, low blocks to the south and tan blocks to the west. Red brick is under-represented (finding 12). |
| Materials hierarchy | deviates (P1 via findings 2, 4, 5) | phone-01 | Bronze glass and fin hierarchy is correct. The spine and boulders are too white and flat, so the rock identity is weak against the source. |
| North face, north halves of side faces, interiors | not visible in sources; coherent | rear, rear_side, left_side, interior | Same fin and bar grammar continues; the interior is a plausible office floor. |

## 4. Camera validity

- **right_side: invalid (P0, finding 1).** In this whole-envelope view, the top frame edge clips the amenity storey and the spine above the roof.
- rear: the spine cap touches the top edge behind the amenity storey. The envelope is otherwise fully in frame (P2, finding 13).
- front, front_corner, aerial, top, left_side and rear_side: valid. The target is fully in frame, unoccluded and legible.
- Detail views (facade_close, architecture_close, glass_close, boulder_garden, rest_balconies, roof_terrace, retail_base, interior, rooftop_plant, east_facade): valid. Each target is legible and unoccluded. The tree in boulder_garden partly overlaps the east planter but does not hide the spine foot.
