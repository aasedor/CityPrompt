# Independent holistic review: Second Empire city hall, v003 (RLASM v6.1 architectural clay)

Reviewer: independent (did not build). Basis: rendered pixels only, compared against `sources/front.png`, `sources/oblique.jpg` and `sources/top.jpg`. I opened all 18 renders at full resolution, the three sources and the four phone boards, and cropped regions for magnification (crops saved outside the candidate directory). I did not use metadata, counts or builder notes as proof.

## 1. Verdict

**VISUAL_REWORK_REQUIRED.** v003 fixes most of v002, but four P1 defects remain:
- **Storey hierarchy:** the source's half-height rusticated basement and its round-arched main floor are missing, so the wall reads as three equal storeys.
- **Tower lower stage:** it reads as a tall, plain stone shaft where the source has a slate mansard stage with a segmental-pedimented aedicule.
- **Court coping:** black voids show at all four corners.
- **Forecourt:** the lawns carry trees that the source does not have, and the trees hide the pavilion balconies in the front view.

Counts: P0 = 0, P1 = 4, P2 = 15

## 2. Findings

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | front, porch_stair, facade_close, left_side, right_side, rear; vs source front + oblique | **Storey hierarchy deviates from the source.** In the source the wing and pavilion rows are: (a) a low rusticated basement of short segmental/round-headed windows, about one-third the height of the floors above; (b) a tall main floor of round-arched windows, with iron balconies on the pavilions; (c) an upper floor of rectangular hooded windows under the bracketed cornice. In the render the rows are: a full-height ground floor of tall arched windows, a rectangular piano nobile and a rectangular second floor. The low basement plinth is gone and the arched windows have dropped to street level, so the facade reads as three equal storeys rather than a raised main floor over a base. *Note: the brief's one-line summary describes the render's arrangement. The source pixels do not, and the method says pixels govern.* | The storey stack follows the text summary instead of the measured source rows. | Reduce the ground storey to about 0.5–0.6 of the main-floor height, with short segmental-headed windows and heavier channelled rustication. Give the main-floor windows round-arched heads in moulded surrounds; the pavilion pairs keep their stone balconies and iron rails. Keep the upper floor as rectangular hooded windows. Re-seat the porch podium and stair so the short flight climbs the basement height to the main-floor porch tier, as in the source. |
| 2 | P1 | clock_tower, front, roof_court, pavilion_mansard; vs source front (tower) and oblique | **Tower lower stage is still a plain, overlong stone shaft.** Above the roof the render shows a cream masonry shaft about 1.9× the height of the clock stage. It has pilasters, a flat-hooded arched opening and a small square window. In the source the stage under the clock is a steep slate mansard about as tall as the clock stage. It carries, on each face, a stone aedicule with a segmental pediment, scroll consoles and urn finials framing the arched opening. The v002 "plain lower stage" is therefore only partly resolved: articulation was added, but the material, proportion and aedicule are still wrong. The tower is the primary identity element. | The lower stage is modelled as an extruded masonry prism instead of a mansard stage with dormer-aedicules. | Shorten the stone portion to a plinth roughly at the main roof ridge. Above it, add a slate mansard stage (steep, slightly concave faces) about as tall as the clock stage. On each face, set a stone aedicule into it: arched opening, segmental pediment, side scrolls, and urns on the corners of the pavilion parapet below. Keep the clock stage and dome as they are. |
| 3 | P1 | rear_court, top, roof_court (small) | **Black square voids at all four corners of the court coping/parapet.** They are prominent black squares in rear_court (upper right and lower left, plus one at the inner string-course corner) and four black dots at the court-opening corners in top. This is the same defect class as the v002 black voids, moved to the court. | The coping and cornice strips butt short of each other at the corners and are not mitred or capped, which opens a hole into an unlit cavity. | Extend each coping run by its own depth (or add a corner cap block) so that the runs overlap at all four court corners. Do the same for the court string courses. Re-render top, roof_court and rear_court. |
| 4 | P1 | front, front_corner, aerial, top, porch_stair (edge) | **Trees in the forecourt lawns.** Each lawn has a low-poly tree standing in front of a corner pavilion. In the primary front view their crowns cover the left pavilion's piano-nobile balcony and ground windows, and part of the right pavilion's. In the source top and oblique the forecourt lawns hold only low hedges and shrubs; the only trees are street trees beyond the corners and on the side street. This is a landscape fidelity defect that hides an identity element (pavilion balconies) in the matched view. | Generic landscape placement reused from the street-tree pass. | Remove the two lawn trees. Replace them with a low hedge or shrub border along the fence line and the building base, as in the source top. Keep the west and east street trees where they are. |
| 5 | P2 | cornice_contact, architecture_close, pavilion_mansard | Wing dormers have flat slab caps. The source dormers have rounded bonnet hoods (oblique and top) or segmental pediments (front). | Simplified dormer cap. | Give the cap a segmental/round hood profile. |
| 6 | P2 | clock_tower, front | The clock-stage pediments are triangular; the source's are segmental. The dome is purely convex, with no concave flare at its spring. White teardrop pendants hang under the clock stage and do not appear in the source. | Generic pediment and dome profile; extra ornament. | Use segmental pediments, add a slight concave kick at the dome's base, and remove the pendants. |
| 7 | P2 | porch_stair, front; vs oblique | The porch's ground tier is a pier-and-arch arcade. The source shows paired columns at ground level as well, in front of an arched door. | Follows the brief's "arcade" wording. | Optional: set columns in front of the piers. |
| 8 | P2 | glass_close, facade_close | The loggia balustrade runs continuously in front of the column shafts, so the column plinths crowd and nearly touch the balusters. In the source the balustrade panels sit between the columns. | Balustrade modelled as one run. | Split the balustrade into panels between the column pedestals. |
| 9 | P2 | front (tower crop) | The porch pediment apex overlaps the lower part of the central pavilion's second-storey windows. | Pediment height versus window row. | Lower the pediment, or replace those windows with the source's carved panels. |
| 10 | P2 | pavilion_mansard, roof_court | A thin black slit where the pavilion mansard corner meets the cornice corner block, and dark mitre seams in the cornice. | Small vertical offset or unmitred joints. | Seat the mansard base on the cornice top and close the mitres. |
| 11 | P2 | cornice_contact | A thin dark vertical seam along the wing/pavilion wall junction, and a small dark diagonal at the cornice return. | Coplanar gap. | Close the seam. |
| 12 | P2 | top, roof_court, front_corner, aerial | The court coping and upper walls glow white and spill a halo onto the roof planes. | Overexposed white material or a light inside the court. | Tone the coping down to the trim value, or remove the court light. |
| 13 | P2 | all whole-envelope views | The walls are pale cream; the source walls are warm brick between grey limestone dressings. The roofs are blue slate; the source roofs are grey-green zinc. (v002 accepted the wall tones.) | Palette choice. | Optional: warm and darken the wall field slightly, and shift the roof towards grey-green. |
| 14 | P2 | top, aerial, rear_side | The outer ring of the upper roof reads flat and only the inner planes visibly pitch into the court. The source reads as ridged double-pitch planes. There is no cresting on the wing flats. | Simplified roof. | Optional: raise a shallow ridge and add cresting. |
| 15 | P2 | front, architecture_close | The corner pavilions lack the source's attic band of small square windows between the cornice and the mansard. The pavilion mansards are slightly lower relative to the wall than in the source oblique (about 0.56 versus 0.63). | Simplified pavilion. | Add the attic band and raise the pavilion mansard about 10%. |
| 16 | P2 | front_corner, aerial, top | The forecourt lawns are plain turf; the source has hedges and shrubs. See also #4. | Landscape simplification. | Add hedges. |
| 17 | P2 | facade_close, glass_close | The ground-floor arch heads are visibly faceted (low segment count). | Low arc resolution. | Raise the arc segment count. |
| 18 | P2 | aerial, front_corner | The building fills only about a third of the frame width. It is legible, but loose for a hero view. | Framing. | Tighten the framing. |
| 19 | P2 | architecture_close | The pavilions have plain pilaster strips; the source has banded quoins. | Simplification. | Optional: band the quoins. |

There are 4 P1 findings (#1–4) and 15 P2 findings (#5–19).

## 3. Source conformance checklist

| item | status | views used | note |
|---|---|---|---|
| Silhouette | conforms | front, front_corner, aerial, top | Pavilion-wing-pavilion front, central tower, courtyard block, forecourt to the south. |
| Storey count | deviates | front, porch_stair vs source front and oblique | Three rows are present, but the hierarchy is wrong (finding #1). |
| Tower stages and clock faces | deviates | clock_tower, front, roof_court | Four clock faces, verdigris clock stage, ribbed convex dome with oculi and lantern: these conform. The lower stage is wrong (#2). The pediments are triangular, not segmental (#6). |
| Porch and stair | conforms | porch_stair, front, top | A short broad flight between cheek walls leads to a raised arcade, with a balustraded four-column loggia and pediment above. P2 notes in #7 and #8. |
| Pavilions and mansards | conforms (P2) | architecture_close, pavilion_mansard, front | Taller square pavilion mansards, one arched dormer per face, flat top with iron cresting. The attic band is missing and they are slightly low (#15). |
| Dormer rhythm | conforms | front, left_side, right_side, rear, cornice_contact | Three wing dormers each side of the tower on the front, aligned to the bays. The cap profile is a P2 (#5). |
| Window rhythm and hoods | partly deviates | front, facade_close, architecture_close | The bay rhythm conforms: 2 pavilion + 3 wing + centre + 3 wing + 2 pavilion. Pavilion piano-nobile windows have pediments and iron-railed balconies. Window head shapes per storey deviate (#1). |
| Cornice and rustication | conforms | cornice_contact, facade_close | Bracketed (modillion) cornice and channelled ground storey are present. The rustication height is part of #1. |
| Fence and forecourt | deviates | porch_stair, front, top | The iron fence on a stone curb with piers, and the lawn forecourt, conform. The trees in the lawns do not (#4). |
| Materials hierarchy | conforms (P2) | all | Dark slate roof over light wall, white dressings, verdigris clock stage and black iron are in the correct value order. The wall hue is paler than the source (#13). |
| North and east faces (not in any source) | coherent | rear, right_side, rear_side | They repeat the visible grammar consistently. |

## 4. Camera validity

- No view is occluded, clipped or illegible, so there is no camera P0.
- **front_corner and aerial:** the building is small in frame (#18) but fully legible.
- **front:** the forecourt trees cover part of the pavilion balconies. This is a model defect (#4), not a camera defect.
- **interior:** legible as a room with a mullioned window, furniture and a view out.
- **rear_court:** looks straight down the court and shows the floor and all court walls.

## 5. Previous-version (v002) findings: resolved in the pixels?

| v002 P1 | v003 status | evidence |
|---|---|---|
| Black voids where wing mansards meet pavilion mansards and beside the tower | **Resolved** at those locations | architecture_close, pavilion_mansard, roof_court and clock_tower show continuous slate with no voids. **New** black voids appear at the court coping corners (#3), and a hairline slit at the pavilion mansard base (#10, P2). |
| Black floor-line bands in the court | **Resolved** | rear_court shows cream string courses and sills and no black bands. Corner voids remain (#3). |
| Stair climbing a full storey to a single-tier porch | **Resolved** | porch_stair and front show a short broad flight with cheek walls to a raised three-arch arcade, under a balustraded four-column loggia and pediment. |
| Onion-like tower cap and plain lower stage | **Cap resolved; lower stage only partly resolved** | clock_tower shows a ribbed convex dome with oculi and a lantern, no longer onion-like. The lower stage now has pilasters and an entablature but is still an overlong stone shaft without the source's slate mansard stage and segmental-pedimented aedicule (#2, P1). |
| Oversized court and near-flat upper roofs | **Resolved** (P2 residue) | In top, the court is about 26% × 17% of the footprint; the source is about 28% × 13%. Hipped inner planes read in aerial, front_corner and rear_side. The outer ring is still flatter than the source (#14, P2). |
| Upper roofs lighter than the walls | **Resolved** | In all whole-envelope views the roofs are a mid blue-grey, clearly darker than the cream walls. |
| West trees against the facade | **Resolved** | top and front_corner show the west street trees on the sidewalk with clear space between crown and wall. The new forecourt-lawn trees are a separate P1 (#4). |
