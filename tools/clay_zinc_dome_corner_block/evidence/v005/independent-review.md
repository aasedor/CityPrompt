# Independent holistic review: zinc dome corner block, v005 (RLASM v6.1 architectural clay)

Reviewer: independent; did not build this candidate. I judged only the rendered pixels against the locked source pixels. I opened all 18 renders, the 3 locked sources and the 4 phone boards. I checked fine detail on zoomed crops of the renders, kept in a scratch folder outside the candidate directory. No candidate file other than this review was changed, and the build was not run.

## 1. Verdict

**VISUAL_REWORK_REQUIRED**: the v004 chamfer balcony P1 is fixed. A separate P1 remains at the same identity element. On the chamfer, the stone drum sags forward past the chamfer wall plane on a curved, corbel-like soffit and breaks the main bracketed cornice. Both sources carry that cornice continuously across the chamfer, with the dome set back above it.

Counts: P0 = 0, P1 = 1, P2 = 10

## 2. Findings

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | architecture_close (centre, y 240-340), corner_dome (y 830-900), roof_court (drum base), left_side (x 1000-1070, y 440-480), front (chamfer top) | The main cornice stops at the chamfer. Only two stepped ressaut stubs remain at the chamfer edges. Between them the drum's lower body bulges out past the chamfer wall face. Its curved, lit underside (a "chin" or bowl soffit) drops to just above the storey-4 chamfer window head. In left_side, a sloped wedge soffit visibly projects outward under the drum. Source front (y 210-240) and source oblique (y 470-500) both show the bracketed, dentilled cornice running unbroken across the chamfer. The dome sits on a low attic set back behind it. So the render reads as a corbelled turret, not a dome on an attic. | The drum radius or centre is set so the drum's outer face lands forward of the chamfer wall plane. The chamfer cornice segment was then cut away (or never generated) to clear it, and a soffit or flare was added to close the underside. | Run the main cornice and modillion course across the chamfer at wing height, with the same profile. Move the drum centre inward, or reduce its radius, so the whole drum stands on or behind the cornice crown. Then delete the curved soffit or corbel under the drum. Optionally add a low stone attic plinth between the cornice and the drum, as in the source front. Re-render front, architecture_close, corner_dome and left_side to confirm. |
| 2 | P2 | mansard_dormers, corner_dome, left_side, right_side, rear | The dormers are zinc-faced boxes with flat slab caps and round-arched windows. Both sources show segmental (curved) hoods over rectangular French windows, and in source front the dormer fronts are stone. The dormers also sit one per bay, denser than the source rhythm. | Simplified dormer module | Give the dormer a segmental hood and a rectangular window. Use a stone-palette front frame on zinc cheeks. Optionally space dormers on alternate bays. |
| 3 | P2 | front, left_side, corner_dome | The dome gores bulge as convex lobes (melon or pumpkin profile) with a scalloped silhouette. The source dome is smooth, with fine standing seams and a clean hemispherical outline. | Gores modelled as convex segments rather than ribs on a smooth shell | Use a smooth shell with raised ribs. |
| 4 | P2 | mansard_dormers (y 820-850) | Below the cornice crown, red brick shows between the modillions. Short stone strips start and stop irregularly in that frieze. | Brick wall runs up into the frieze; fragments of the window-head band poke through | Fill the modillion frieze with a continuous stone band. |
| 5 | P2 | roof_court (cornice tops beside the drum), top (corner blocks) | Thin black slivers mark the cornice-ressaut tops next to the drum and the junctions of the new corner blocks. | Small gaps or coplanar seams between abutting boxes | Overlap or weld the abutting solids. |
| 6 | P2 | glass_close, balcony_ironwork, facade_close | Small black cubes sit at window-frame corners. | Corner caps in dark material, or tiny gaps | Recolour to the frame colour or remove. |
| 7 | P2 | rear_side (rear hip) | The two hip-end dormers of adjacent faces collide at the hip; their cheeks and caps merge. | Dormer run not inset from the hip | Stop each dormer run one module short of the hip. |
| 8 | P2 | right_side, rear, rear_side | No source shows the north and east faces. Their ground floor has 5 small openings that do not follow the 9-10 bay rhythm above, and the faces have no balconies. The faces stay coherent but plain. | Rear-face ground floor generated independently of the bay grid | Align ground-floor openings to the bay axes. |
| 9 | P2 | aerial, front_corner, roof_court, mansard_dormers | Chimneys are plain stone-coloured stacks. The sources show brick or terracotta stacks with pots. | Single chimney primitive | Use a brick-palette stack and add a pot row. |
| 10 | P2 | interior, rear_court | The interior face of the court wall carries the exterior brick colour, and the room is very dark (it is still legible). Court walls have only sills and lintels, with no stone base or string courses. | Single-sided wall material; court treated as a secondary face | Use plaster on interior faces and raise the interior fill light. A stone plinth band in the court is optional. |
| 11 | P2 | corner_dome, left_side | The oculus dormer is a ring on a zinc box with a flat slab cap and zinc side fins. The source has a stone aedicule with scroll consoles. | Simplified module | Use a stone surround with a curved hood and console scrolls. |

## 3. Source conformance checklist

| item | status | view(s) used | note |
|---|---|---|---|
| Silhouette | conforms | front vs source front; front_corner and aerial vs source oblique; top vs source top | Corner block with chamfer at the south-west street corner, inner court, mansard and corner dome in the right position and scale. The flat mansard top is accepted per the brief. |
| Storey count | conforms | left_side, front, facade_close | Ground floor, stone storey 1, brick storeys 2-4, then the mansard. |
| Chamfer and dome | **deviates** | architecture_close, corner_dome, left_side, front | The chamfer is a stone face and the ribbed zinc dome sits on it. But the drum bulges forward over the chamfer and breaks the cornice (P1 #1), and the gores are lobed (P2 #3). |
| Drum windows and lantern | conforms | corner_dome, left_side | Three oeil-de-boeuf windows on a stone drum. Oculus dormer on the dome (form simplified, P2 #11). Open columned lantern, small cap and gilded finial. |
| Balcony rhythm (individual and continuous) | conforms | facade_close, balcony_ironwork, left_side, front, architecture_close, cafe_awning | Wings: individual balconies on storeys 1 and 3, continuous on 2 and 4. Chamfer, going up: narrow, wide on two consoles, narrow, wide. |
| Brick-and-stone banding | conforms | facade_close, balcony_ironwork, right_side | Red brick infill between stone window surrounds and quoins, with stone string courses. Small brick leak in the cornice frieze (P2 #4). |
| Mansard and dormers | deviates (P2) | mansard_dormers, left_side, rear_side | Steep zinc mansard with dormers is present. The dormer hood and window form differ from the sources (P2 #2), and the dormers collide at the rear hip (P2 #7). |
| Cafe awning and ground floor | conforms | cafe_awning, front, front_corner, top | Red awning with valance wraps the chamfer and both street faces. The cafe glazing at the chamfer shows interior chairs. Stone ground floor with shopfronts. |
| Cornice | **deviates** | mansard_dormers, front_wcorner crop, architecture_close | The bracketed cornice runs along both wings with a zinc gutter above, but it is broken across the chamfer by the drum (P1 #1). |
| Materials hierarchy | conforms with P2 notes | all whole-envelope views | Stone ground floor, storey 1, chamfer and surrounds; brick upper storeys; zinc roof and dome; iron rails; red awning; gilded finial. Dormer faces are zinc where source front shows stone (P2 #2). |

## 4. Camera validity

- All 18 renders have a valid camera. None has an occluded target, a clipped asset or an illegible view.
- front, front_corner, aerial, top, left_side, right_side, rear and rear_side each frame the whole envelope with margin. top is a true nadir.
- Every detail view frames its named subject:
  - facade_close, architecture_close, glass_close, corner_dome, cafe_awning, balcony_ironwork, mansard_dormers and roof_court are clear.
  - rear_court shows the court floor and all walls.
  - interior is dark but legible: window wall, court opening and furniture are readable.
- The trees in front and left_side overlap only small parts of the facade and hide no identity element.

## 5. Previous-version findings (v004), checked in pixels

| v004 finding | resolved? | evidence |
|---|---|---|
| P1: full-width console balcony sat at chamfer storey 1, directly over the awning frieze; it should read narrow, wide, narrow, wide going up | **Resolved** | The pixels show the corrected stack. cafe_awning: a window-width iron balcony at storey 1 sits clear above the awning sign frieze, and the full-width stone balcony on two consoles is at storey 2. front chamfer crop, left_side and architecture_close: narrow (s1), wide on consoles (s2), narrow (s3), wide (s4). |
| P2: brick band showing above the main cornice at the wall heads; a zinc gutter should cap them | **Resolved** | mansard_dormers and the front_wcorner, top_nw and top_se crops: above the cornice crown, a zinc gutter strip runs into the mansard and no brick shows above the cornice. Residual: brick still shows below the crown, between the modillions (new P2 #4). |
| P2: corner blocks to close the wall-head corner tops seen from above | **Resolved** | top and aerial: square stone corner blocks close all four outer corners. Residual: thin black seam slivers at some block junctions (P2 #5). |
