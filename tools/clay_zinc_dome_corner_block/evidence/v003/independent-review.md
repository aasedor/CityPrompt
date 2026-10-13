# Independent holistic review: clay-zinc-dome-corner-block v003 (RLASM v6.1)

Reviewer: independent, adversarial. Evidence: the locked sources (`sources/front.png`, `sources/oblique.jpg`, `sources/top.jpg`), all 18 renders at full resolution, zoomed crops of the dome, drum, oculus dormer, court and frame corners, and the four phone boards. Pixel values are sRGB samples from the renders. I did not use builder notes, metadata or hashes as proof.

## 1. Verdict

**VISUAL_REWORK_REQUIRED**: two of the three v002 findings are fixed in the pixels. The third, the oculus dormer, now has no geometry clash, but its aperture is filled with a zinc-toned surface and still reads blind. The court-wall fix also left full-height open slots at the inside corners of the court.

Counts: P0 = 0, P1 = 2, P2 = 9

## 2. Findings

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | front, corner_dome, left_side, roof_court, architecture_close | The oculus dormer on the dome reads as a white stone ring around a **pale blind disc**. The aperture samples (168-169, 174, 177-178) in front, corner_dome and roof_court. That matches the zinc around it (162-168, 168-174, 173-177) and is about double the drum-roundel glass (83-89, 85-89, 84-88). The source oculus is a dark glazed eye with a hood. In left_side the reveal is visible, but the opening is filled with the same pale value, so it reads as a zinc plug, not a window. The claimed recessed glass is not legible. | The oculus glass uses the zinc material or a highly reflective glass. Or there is no glass, and the visible surface is the back of the zinc cylinder hood. | Give the oculus pane the same dark glass material as the drum roundels (target about 80-90 sRGB). Set it back behind the reveal with a dark reveal return. Add the cross bar so it reads as a glazed oeil-de-boeuf at front-view scale. |
| 2 | P1 | rear_court (centre and lower right), front_corner, aerial, top | **Open vertical slots at the inside corners of the court.** The two court walls stop short of each other, leaving a gap about 20 px wide from cornice to court floor in rear_court. Through it the dark interior (34-68 sRGB) and lit floor-slab edges are visible. The slot shows as a black hairline at the court corner in front_corner and aerial. Top shows pure-black (0,0,0) ticks at all four court corners. A second dark wedge is visible at lower right in rear_court. This is an envelope breach, and it is new in v003. | The v002 fix stopped the floor slabs clear of the court walls, and the court wall segments were also trimmed, or never extended, to the corner. The wall panels do not overlap or mitre. | Extend each court wall segment by the wall thickness at both ends, or add corner posts, so the court envelope is closed at all four corners. Keep the slabs inset. Re-render rear_court and top, and confirm there are no black corner pixels. |
| 3 | P2 | corner_dome, architecture_close, front | The drum roundels are now real openings: annular frame, dark recessed glass, and a visible reveal on the oblique roundels. But the claimed cross bar is not visible in any view, and the four keystone blocks per ring are heavy. | The cross bar is too thin, or sits behind the dark glass. | Make the cross bar thicker or lighter in value, or drop the claim. Optionally slim the keystones. |
| 4 | P2 | architecture_close, corner_dome, front | The drum is cantilevered beyond the chamfer face on a curved, shadowed soffit, and the bracketed main cornice is not carried across the chamfer. In the source front the cornice runs continuously over the chamfer, with the dome above. | The drum radius is larger than the chamfer width. | Carry the cornice across the chamfer under the drum, or reduce the drum overhang. |
| 5 | P2 | front, left_side, corner_dome | The dome profile is slightly bulbous, and the ribs are heavy and raised (melon-like). The source dome is a smoother, near-hemispherical ribbed dome. | Rib extrusion depth and profile curve. | Reduce rib depth and straighten the lower profile. |
| 6 | P2 | mansard_dormers | The arched dormer heads are faceted voussoir boxes with dark wedge gaps between them, and the lowest blocks hang past the window jambs. The dormer tops are flat slabs, where the source has pedimented or curved hoods. | Arch built from separate boxes. | Use a continuous arched architrave, and optionally a curved hood. |
| 7 | P2 | glass_close, facade_close | Small pure-black voids at the corners of shopfront and window frames. | Frame members end short at the mitres. | Overlap or mitre the frame members. |
| 8 | P2 | top, rear_side | Black wedges at the outer hip corners of the mansard curb or cornice (pure black at 3 outer corners in top). | Perimeter roof or curb segments do not meet at the corners. | Close the corner joints. |
| 9 | P2 | mansard_dormers, front, all whole-envelope views | The cornice crown or mansard curb is a brick-red strip. The source reads stone or zinc here. | Wrong material slot. | Assign stone or zinc. |
| 10 | P2 | top, aerial, rear_court | All court walls are brick to the ground. The court faces in the top source read as pale stone or render. | Street grammar copied into the court. | Optionally use pale render for the court faces. |
| 11 | P2 | all | The brick is a salmon/pink tone. The source brick is a deeper red-brown. | Palette value. | Darken the brick. |

## 3. Source conformance checklist

| item | status | view(s) used | note |
|---|---|---|---|
| Silhouette | conforms | front vs source front; front_corner and aerial vs oblique; top vs top | Corner block with a chamfer, streets south and west, inner court, flat-topped mansard, dome on the chamfer. |
| Storey count | conforms | left_side, rear, facade_close | Stone ground floor, stone first storey, three brick storeys, and the mansard. |
| Chamfer and dome | conforms (P2 caveats) | front, corner_dome, front_corner | Ribbed zinc dome on the chamfer. The drum overhang (P2 #4) and bulbous profile (P2 #5) are polish issues. |
| Drum windows and lantern | deviates (P1 #1) | corner_dome, left_side, front | Drum roundels are now glazed openings with reveals. The oculus dormer reads blind. The open columned lantern, zinc cap and gilded finial conform. |
| Balcony rhythm (individual and continuous) | conforms | left_side, facade_close, balcony_ironwork | Individual balconies on the first and third storeys, continuous on the second and fourth. Ironwork reads, and the railings sit on their slabs. |
| Brick-and-stone banding | conforms | facade_close, balcony_ironwork, architecture_close | Brick with stone string courses, window surrounds and quoins. |
| Mansard and dormers | conforms (P2 #6) | mansard_dormers, rear, left_side | Zinc mansard with arched dormers and a flat top. The dormer heads are faceted. |
| Cafe awning and ground floor | conforms | cafe_awning, front, front_corner, top | Red awning wraps the chamfer and returns along both streets, with a valance. Glazed shopfronts with depth, and cafe interior visible. |
| Cornice | conforms (P2 #4, #9) | mansard_dormers, architecture_close | Bracketed modillion cornice on both wings. It is interrupted at the chamfer, and the crown strip is brick-red. |
| Materials hierarchy | conforms (P2 #9, #11) | all | Stone, brick, zinc, iron, red awning and gilt in the correct hierarchy. |
| North and east faces (no source) | coherent | rear, right_side, rear_side | Same brick and stone grammar without balconies. This reads plausibly as secondary facades. |

## 4. Camera validity

No view is invalid. Every whole-envelope view frames the full asset, unclipped, with the target legible. The detail views (facade_close, architecture_close, glass_close, corner_dome, cafe_awning, balcony_ironwork, mansard_dormers, roof_court, interior, rear_court) each show their intended target unoccluded. The interior view is dark, but the floor plate, window openings, court box and furniture are legible. The rear_court camera stays valid, as verified in v002, and is the view that exposes P1 #2.

## 5. v002 findings: resolved in the pixels?

| v002 finding | status | evidence |
|---|---|---|
| Three drum oeils-de-boeuf were blind stone discs ringed by cog-tooth blocks | **Resolved** | corner_dome and architecture_close crops: each roundel is an annular stone frame around a dark recessed pane (83-89 sRGB). The side roundels show a visible reveal return in the oblique views. Four keystones replace the cog ring. The claimed cross bar is not visible (P2 #3). |
| The oculus dormer's white frame ring cut through its conical hood | **Partly resolved: the intersection is gone, but the opening is still not legible** | The ring no longer cuts through a hood. It sits in front of a zinc cylinder under a flat stone cap, with zinc side cheeks. But the aperture is filled with a zinc-toned value (169,174,178), so the dormer still reads as a blind ring on the dome (P1 #1). |
| Pure-black horizontal bands at every floor line on the court walls | **Resolved, with a regression** | rear_court, aerial and front_corner: no horizontal black bands on the court walls. The fix exposed or created full-height open slots at the inside corners of the court, with floor slabs visible through them (P1 #2). |
| Awning, cheeks, valances, dome placement, court camera (verified resolved in v002) | Still resolved | cafe_awning, corner_dome, top and rear_court show no regression. |
