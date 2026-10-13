# Independent holistic review: clay Baronial railway hotel, v004

Reviewer: independent (not the builder). Inputs opened at full resolution with the Read tool: `sources/front.png`, `sources/oblique.jpg`, `sources/top.jpg`, all 18 `renders/*.png` and the 4 `boards/*.png`. Where a defect was small I cropped and enlarged the render and sampled pixel values. I judged pixels only; metadata, counts and builder notes were not taken as proof.

## 1. Verdict

**VISUAL_REWORK_REQUIRED**: all five v003 findings are fixed in the pixels and there are no P0s, but two new P1 contact defects remain on the entrance tower: the porte-cochere voussoir ring does not reach its jamb piers, and there is a pure-black void around the tower roof deck.

Counts: P0 = 0, P1 = 2, P2 = 13

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | porte_cochere, facade_close, front_corner | The pale outer voussoir ring of the street-side pointed arch stops short of the jamb piers on both sides. Its last block ends with a horizontal cut about 15-25 px above the pier cap, with pink wall showing in the gap (facade_close left foot at about x 575-610 / y 790-845, pier top at about y 870; the right foot behaves the same way). The ring is also set outboard of the pier faces, so it reads as a separate floating hood and not as an arch bearing on its jambs. Only the inner soffit band lands on the piers. | The ring was regenerated when the passage and reveal were reworked, but its springing height and width were not re-tied to the jamb pier tops and faces. | Run the outer voussoir ring down to the pier caps, or raise the pier caps to the springing line as imposts. Make the ring's outer and inner radii match the pier face width so each kneeler sits on its pier. Re-render porte_cochere and facade_close. |
| 2 | P1 | roof_court, top, aerial, front_corner | A continuous pure-black void line, RGB (0,0,0) to (9,9,10) and 2-3 px wide, runs where the tower roof deck meets the inner faces of the crenellated parapet, on at least two sides. It shows in the nadir view (top.png x 528-530, y 716-718), so it cannot be a cast shadow. The porch deck in top.png has the same outline. This is the same class of defect as the v003 court-corner black notches. | The deck slab is inset, or sits below the parapet's inner face, leaving a see-through gap into the unlit interior volume. | Extend the deck slab under the parapet walls (overlap of at least 0.1 m), or close the gap with an inner parapet face that runs down to below deck level. Do the same on the porch deck. |
| 3 | P2 | porte_cochere, facade_close | Former full-height slot: four small black pinholes (about 5-6 px each) remain at the junction of the right arch reveal and the passage wall, at y ≈ 585, 685, 790 and 895, one at each rustication-joint groove. | The joint grooves cut through the reveal's return and show the void behind. | Stop the joint grooves short of the reveal return, or back the junction with a solid filler. |
| 4 | P2 | porte_cochere, facade_close, rear_court | Small black wedge notches between the voussoir blocks at several joints, including at the apex. | Voussoir segments have a gap at the extrados. | Close the segment gaps or add a backing ring. |
| 5 | P2 | porte_cochere, facade_close | Inside the passage, a pale pointed rib or wedge hangs below the crown. It is separated from the street-arch soffit by a band of dark wall and its foot is cut off at mid-height, so the vault does not read as one continuous surface. | A short vault shell, or the court-arch soffit, sits at a different depth from the street arch. | Make the passage soffit one continuous pointed barrel (or a flat soffit) from the street reveal to the court reveal. |
| 6 | P2 | porte_cochere | A thin threshold slab protrudes onto the pavement in front of the opening. There is a black contact line under the left pier and a sliver of lawn shows under the right pier. | Plinth, lawn and threshold are not trimmed to the gate piers. | Trim the lawn and threshold to the piers and seat the pier bases on the slab. |
| 7 | P2 | architecture_close, corner_tourelle | On the narrow side-face (west) gable, the upper window head sits at exactly the height of the neighbouring step copes. In foreshortened obliques the head and copes read as one continuous band, and the outer jamb appears flush with the riser. The frontal and elevation views (crow_gables, front, left_side, rear) are clear. | Head height is snapped to the cope level. | Drop the gable window heads about half a step below the cope level, or narrow the upper window by about 0.15 m. |
| 8 | P2 | crow_gables | A small isolated grey slab floats on the dark roof wedge on the tower-side flank of the gable (about x 475-490, y 505-515) and is not attached to any step. | A leftover cope or step slab from the rebuild. | Delete it or snap it to its step. |
| 9 | P2 | rear_court | Court window head hoods sit at string-course height and partly overlap the course, most clearly at the inner corner. Court windows have heads but no jamb surrounds. | The hood offset matches the course offset. | Lower the hoods below the course, or let the course break around them. |
| 10 | P2 | top, aerial, roof_court | The tower and porch roof decks show cloud-like mottled light and dark shading, unlike the matte clay elsewhere. | Glossy material or denoiser blotching on a large flat face. | Use the same matte clay roughness as the other surfaces. |
| 11 | P2 | glass_close, facade_close, entrance_tower | Rustication is shown only as sparse horizontal channel lines (about 3 per window height). It reads more like banded render than coursed rock-faced granite. Acceptable for clay. | Joints were spaced out to stay under the GLB size limit. | Tighten the course spacing on the street faces only, if budget allows. |
| 12 | P2 | entrance_tower, front | The tower lacks the source's corbelled mid-height oriel or balcony and its heraldic panels. The roofline sequence next to the tower (gable, then dormer, then gable) follows the oblique source, not the front source (three dormers, then a gable). The sources conflict here. | Simplification and source conflict. | Optional: add a corbelled oriel at third-floor level on the tower's south face. |
| 13 | P2 | porte_cochere, crow_gables, architecture_close | The faceted corbel cones under the bartizans and tourelles are visible at close range. The lower-right window in crow_gables has a bright pink-white interior hotspot. | Low segment counts (GLB budget) and an interior light leak. | Raise corbel segment counts on the street faces only, and dim the interior light behind that window. |

## 3. Source conformance checklist

| item | status | view used / note |
|---|---|---|
| Silhouette | conforms | front vs source front, front_corner and aerial vs oblique, top vs top. A quadrangle with a dominant crenellated tower, conical tourelles at the corners and along the side faces, steep hipped slate roofs and crow-stepped gables. |
| Storey count | conforms | front, left_side, glass_close. Four storeys below the corbelled eaves cornice plus two gable tiers and dormers, matching the source's ground + 3 + attic and gable levels. |
| Entrance tower and porte-cochere | conforms, with P1 #1 | front, porte_cochere, facade_close. Square tower about a third of the way along the south face (the brief says a quarter). Pointed-arch porte-cochere through to the court: in front.png the court (tree and window) shows through the passage. The arch ring is not tied to its jambs (#1). |
| Tower tourelles and parapet | conforms, with P1 #2 | entrance_tower, roof_court. Corbelled crenellated parapet with round bartizans and conical-capped stair tourelle at the rear corner, legible at eye level. Deck-to-parapet black void (#2). |
| Corner tourelles | conforms | front, left_side, right_side, rear, corner_tourelle, architecture_close. Round, corbelled out above the first storey, with conical slate caps. |
| Crow-stepped gables | conforms | crow_gables, front, left_side, rear. Stacked step slabs with copes and visible risers, rising through the eaves, windows clear of the copes in elevation. P2 residuals #7 and #8. |
| Roof slopes and dormers | conforms | front, aerial, rear, left_side. Steep slate hips with gabled dormers and multi-pot chimney stacks. There are fewer dormers than in the source; acceptable. |
| Window rhythm and surrounds | conforms | glass_close, facade_close, left_side. Regular bays of two-by-two sash windows with projecting stone surrounds, sills and cornice heads, all with visible returns and depth. |
| Court | conforms | top, aerial, roof_court, rear_court. Open court with paving and four trees, as in source top. Court-facing crow gables are present. Court corners are clean. |
| Fence and lawn | conforms | front, porte_cochere, aerial, top. Iron railings on a low wall with gate piers at the porte-cochere, lawn strips and trees on the south and west streets. |
| Materials hierarchy | conforms | all views. Pink granite walls, pale stone dressings, dark blue-grey slate. Rustication is sparse (P2 #11). |

## 4. Camera validity

No view is invalid. None has its target occluded, clipped or illegible.

- front: the building fills the upper half and the lower third is empty ground plane. The target is fully legible. It could be framed tighter, but this is not a defect.
- porte_cochere: legible. Because the camera is oblique to the passage axis, the passage reads as a lit east side wall and the court is not visible through it. The front view does show the through route.
- rear_court: legible. The court-side arch is partly hidden by the court tree, but enough of it shows.
- interior: a generic room. Legible, with the windows reading as openings.
- Phone boards 01-04: legible, with matched source and render pairs on board 01.

## 5. Previous-version (v003) findings: are they resolved in the pixels?

| v003 finding | status in v004 pixels |
|---|---|
| **P0: full-height black slot inside the porte-cochere** at the junction of the porch reveal and the passage wall (also in v002) | **Resolved. The slot does not survive.** There is no full-height dark slot in porte_cochere, facade_close or front. Dark-pixel sampling along the reveal finds only four 5-6 px pinholes at the joint grooves (P2 #3). The arch-ring contact problem (P1 #1) is a separate, new defect. |
| P1: two-tier gables, where lower window heads merged into the step copes and outer jambs were flush with the risers | **Resolved** in crow_gables, front, left_side and rear. The heads now sit under the copes with wall between, and the jambs clear the risers by about one step. A residual visual merging remains on the upper head of the narrow side gable in foreshortened obliques (P2 #7). |
| P1: the tower-side flank of the gable next to the tower read as a straight rake with no risers over a near-black wedge | **Resolved.** Enlarged crow_gables shows vertical risers and horizontal copes stepping down the flank. The dark area behind now reads as slate roof between the gable and the tower. One stray floating slab remains (P2 #8). |
| P1: the tower's conical stair tourelle was too small, too low and invisible at eye level | **Resolved.** A tall shaft with a cone rises above the parapet at the tower's rear corner. It is clearly visible at eye level in front, entrance_tower, left_side, right_side and rear, and from above in aerial and roof_court. |
| P1: black notches where the court string courses meet at the inner corners (also in v002) | **Resolved. The notches do not survive.** At 2.5x enlargement, rear_court shows clean mitred course junctions at the inner corner with no black pixels. |
