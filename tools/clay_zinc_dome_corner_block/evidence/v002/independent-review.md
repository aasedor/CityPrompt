# Independent holistic review: zinc v002 (clay-zinc-dome-corner-block)

Reviewer: independent RLASM v6.1 holistic reviewer (did not build this candidate).
Inputs opened at full resolution: sources/front.png, sources/oblique.jpg, sources/top.jpg; all 18 renders/*.png; boards/phone-01..04. Zoomed crops of the drum, oculus dormer, awning, court corner and frame corners were inspected (and a 3x brightened rear_court copy). Builder notes, metadata and counts were not used as evidence.

## 1. Verdict

**VISUAL_REWORK_REQUIRED**: the awning, dormer cheeks, dome placement and court camera are now fixed, but the three drum oeils-de-boeuf are solid cog-shaped bosses with no openings, the oculus dormer's frame ring cuts through its conical hood, and the court walls carry pure-black bands at every floor line.

Counts: P0 = 0, P1 = 3, P2 = 10

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | corner_dome, architecture_close, front, roof_court, left_side, front_corner | The three drum "oeils-de-boeuf" are solid stone discs ringed by eight square blocks, so they read as cog wheels or rosettes. There is no opening, no glass and no reveal or return. In left_side and front they look like carved gear medallions, not windows. This is an identity element ("stone drum with oeil-de-boeuf windows") and an opening without depth. | The medallion is modelled as a raised boss with keystone blocks and no boolean cut or recessed glazing. | Cut each roundel as an opening about 0.15–0.25 m deep. Use a recessed dark-glass disc, a continuous moulded stone ring frame with visible inner returns, and at most 4 keystones (top, bottom and sides) instead of 8 cog teeth. Keep all three on the drum's front arc. |
| 2 | P1 | corner_dome, roof_court, front, left_side, front_corner | The oculus dormer now projects and has recessed glass, but its white frame ring passes through the conical hood: thin white arcs of the ring show on the cone's surface on both sides. The plain pointed cone hood plus the off-centre lower crescent of the frame make it read as a "C" or crescent moon in front and as a spike-hatted eye in left_side. The source shows a framed oval oeil-de-boeuf under a moulded or pedimented stone hood. | The ring torus radius is larger than the hood's clearance, and the hood is a default cone primitive placed over the ring. | Shrink the ring or raise and widen the hood so nothing intersects. Replace the cone with a curved (segmental) stone or zinc hood that sits on the ring's top. Show the full ring, so the frame is visible all the way round in front view. Check for no intersection from front, corner_dome and left_side. |
| 3 | P1 | rear_court (also visible on the 3x brightened copy) | Every court wall has a pure-black (0,0,0) horizontal band about 10 px thick at each floor line, on lit and shaded walls alike. These bands are either open gaps between per-storey wall slabs or a black material. v001 already failed pure-black parts (cheeks and valances). Here the problem recurs on the court elevations, which are the subject of a required detail view. | Court walls are built per storey with a gap or an unassigned/black material on the floor-line band. | Close the storey slabs (or make one continuous court wall) and give the floor-line band the stone string-course colour used on the street faces. Re-render rear_court and confirm that no pixel cluster below RGB 10 remains on wall surfaces. |
| 4 | P2 | corner_dome, left_side, front, roof_court | Dome gores are deeply concave between raised ribs, so the dome reads as a scalloped melon. The source's dome is a smooth zinc hemisphere with fine standing-seam ribs. | The gores are modelled as concave lobes rather than a smooth shell with applied ribs. | Make the shell smooth and spherical. Keep the 12–16 ribs as thin raised seams. |
| 5 | P2 | roof_court, corner_dome (zoom) | Thin black slivers show where the drum meets the mansard and cornice on both sides of the chamfer. | Small gap or unlit sliver between the drum cylinder and the roof mesh. | Extend the drum base or a flashing collar about 0.1 m into the roof and cornice. |
| 6 | P2 | architecture_close, corner_dome, front | The bracketed cornice stops at the chamfer piers. The drum's concave corbel soffit sits directly over the top chamfer window. The source carries the dentilled cornice and a cartouche continuously across the chamfer, with the dome above it. | The drum projection replaced the cornice segment on the chamfer. | Run a short cornice segment (with a cartouche) across the chamfer under the drum's corbel ring. |
| 7 | P2 | cafe_awning, architecture_close, front_corner | The chamfer's 1st-storey balcony spans the full chamfer, but both the front and oblique sources show a narrow individual railing there. The chamfer's 2nd-storey balcony lacks the large scrolled consoles that are visible in the front source. | The chamfer reuses the continuous-balcony module. | Narrow the 1st-storey chamfer railing to the window width. Add two scroll consoles under the 2nd-storey chamfer balcony. |
| 8 | P2 | glass_close, facade_close, balcony_ironwork | Small black squares sit at the top corners of most window frames. | Corner blocks or rod ends with a black/unassigned material, or tiny holes. | Assign the frame material or delete the stray corner geometry. |
| 9 | P2 | mansard_dormers, front_corner, roof_court | A terracotta band runs between the stone cornice and the zinc mansard foot. The source has stone running directly into zinc. | The brick wall top or a gutter band is exposed above the cornice. | Recolour it to stone or zinc, or lower the wall top behind the cornice. |
| 10 | P2 | top, front_corner, aerial, rear_side | The terrasson is a dead-flat plate around a large centred square court, while the source top and oblique show pitched upper zinc planes with hips and ridges and a smaller light well. The brief's "flat top" makes this acceptable, but the roof reads heavier and flatter than the source. | The upper roof is modelled as a horizontal plane. | Give the terrasson a shallow pitch (about 10–15°) with hip lines, and optionally add 2–3 skylight boxes. |
| 11 | P2 | glass_close | The shopfront glazing sits almost flush with the stone piers. The reveal is only a thin sliver, and the brown transom panel reads as a box inside the glass. | Small frame setback. | Set the shopfront frames back about 0.2 m and put the fascia panel outside the glass plane. |
| 12 | P2 | rear_court, interior | Both views are badly underexposed: the court is legible only when brightened, and the interior is mostly dark. The internal court corner also shows a neutral-grey vertical strip that I could not confirm as either a quoin or a seam. | No fill light inside the court or rooms. | Add court and interior fill light, then re-render and confirm that the corner strip is intended stone. |
| 13 | P2 | rear, right_side, rear_side | The north and east faces have no balconies and no ground-floor shopfronts. They are coherent as secondary or party faces (no source shows them), and are noted only for completeness. | Deliberate simplification. | None required. Optionally add the stone 1st-storey individual balconies for grammar continuity. |

(P2 count in the header covers rows 4–13.)

## 3. Source conformance checklist

| Item | Status | View(s) used | Note |
|---|---|---|---|
| Silhouette | conforms | front vs source front; front_corner and aerial vs oblique | Corner block with the chamfer dome as the high point and a mansard on both street faces. The flat terrasson is heavier than the source (P2 #10). |
| Storey count | conforms | left_side, front, facade_close | Stone ground floor, stone 1st storey, three brick storeys, then the mansard with one dormer row, on both street faces and the chamfer. |
| Chamfer and dome | conforms (placement); deviates (dome finish) | top, corner_dome, front, left_side | The dome is centred on the chamfer diagonal. The drum's front is at or over the chamfer face and the drum is fully exposed above the mansard eave. The gores read as a melon (P2 #4). |
| Drum windows and lantern | deviates (drum windows); conforms (lantern) | corner_dome, left_side, roof_court | There are three roundels, but they are blind cog bosses (P1 #1). The lantern is open (colonnettes plus cap) with a gilded finial. |
| Balcony rhythm (individual and continuous) | conforms on street faces; minor deviation on chamfer | facade_close, balcony_ironwork, left_side, architecture_close | Individual on the 1st and 3rd storeys, continuous on the 2nd and 4th, with slabs and returns. The chamfer's 1st storey is over-wide (P2 #7). |
| Brick-and-stone banding | conforms | balcony_ironwork, left_side, facade_close | Brick storeys with stone string courses, window surrounds and corner quoin piers. The 1st storey and the chamfer are stone. |
| Mansard and dormers | conforms | mansard_dormers, left_side, rear | Arched dormers with stone voussoirs. The cheeks are now zinc grey, not black. |
| Cafe awning and ground floor | conforms | cafe_awning, front_corner, top, left_side | One continuous red canopy with mitred arrises wraps the chamfer and returns about 2 bays along each street. It has a red valance and a glazed cafe front with furniture inside. |
| Cornice | conforms on street faces; deviates at chamfer | mansard_dormers, architecture_close | Bracketed modillion cornice. It is interrupted across the chamfer (P2 #6). |
| Materials hierarchy | conforms on exterior; deviates in court | front, left_side, cafe_awning, rear_court | Stone, then brick, then zinc, with red awning and dark iron. The court has pure-black bands (P1 #3). |

## 4. Camera validity

- front, front_corner, aerial, top, left_side, right_side, rear, rear_side: the target is unoccluded, unclipped and legible.
- Detail views (facade_close, architecture_close, glass_close, corner_dome, cafe_awning, balcony_ironwork, mansard_dormers, roof_court): each frames its subject. architecture_close crops the top of the dome on purpose, and corner_dome covers it.
- rear_court: valid. The camera now looks down into the court, onto two inner elevations and the court floor. It is underexposed (P2 #12) but legible.
- interior: valid, but dark (P2 #12).
- No invalid camera found.

## 5. Previous-version (v001) findings: resolved in pixels?

| v001 finding | Status in v002 pixels | Evidence |
|---|---|---|
| Red awning in three separate canopies with gaps at the chamfer arrises | **Resolved** | cafe_awning, front_corner and top show one continuous canopy with mitred joins at both arrises and no gaps. |
| Pure-black dormer cheeks and awning valances | **Resolved for those elements** | mansard_dormers: the cheeks are zinc blue-grey. cafe_awning: the valance is red. Pure black recurs elsewhere, as the court-wall bands (new P1 #3). |
| Dome set inboard of the chamfer, drum buried in the mansard, only one oeil-de-boeuf | **Partly resolved** | Placement is fixed: corner_dome, top and front show the drum on corbels at the chamfer, fully exposed above the eave. There are now three roundels, but none is a window; all are blind cog bosses (P1 #1). |
| Oculus a flat disc instead of a projecting dormer | **Resolved as to projection; new defect** | corner_dome and left_side show a projecting dormer with cheeks and recessed glass inside a frame ring. The ring intersects the cone hood and reads as a crescent (P1 #2). |
| rear_court camera on the outer face | **Resolved** | rear_court looks down into the inner court. It is underexposed (P2 #12). |
