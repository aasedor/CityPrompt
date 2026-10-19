# Independent holistic review: covered timber footbridge, v003 (RLASM v6.1 clay)

Reviewer: independent, adversarial. I judged only rendered pixels against the locked source pixels (`sources/front.png`, `sources/oblique.jpg`, `sources/top.jpg`). I opened all 18 renders, the 3 sources and the 4 phone boards at full resolution, and made zoomed crops in a new folder: `/tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/v003-indep-crops-1f87f0ac/`.

## 1. Verdict

**VISUAL_REWORK_REQUIRED.** The v002 bay-rhythm P1 is fixed (7 frames, 6 equal bays). Two clearly visible fidelity defects still block approval. First, the end bays are fully louvred rectangles, but in every source the louvres stop on the long diagonal and the triangle below it is open with glass. Second, in the views that match the oblique source, the glass balustrade reads as an opaque grey parapet.

Counts: P0 = 0, P1 = 2, P2 = 8

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | front, front_corner, aerial, rear, rear_side, rear_north, louvre_wall, architecture_close, pier_abutment, portal_end | Every end bay (both walls, both ends) is filled with vertical louvres over its full height, from the bottom rail to the wall plate. The long diagonal is laid over them, so the lower triangle below the diagonal is solid louvres. In the sources the louvre fins **stop on the diagonal**. Only the triangle bounded by the portal post, the wall plate and the diagonal is louvred. The triangle bounded by the diagonal, the bottom beam and the midspan-side post is **open**, and the glass balustrade continues through it. In source front, the woman and pram are seen clearly below the near-wall diagonal, and the river and trees are seen below the far-wall diagonal. In source oblique, the deck and glass are visible below both end-bay diagonals. In the render, the end bays read as closed louvre boxes rather than louvred triangles over an open, braced bay. | The v003 fix took the v002 wording "full-height louvres with the diagonal laid over them" literally, instead of following the source pixels. The louvre array is generated per bay as a rectangle and is not clipped by the diagonal. | In each of the 4 end bays, clip the louvre array to the triangle above the diagonal: trim each fin's lower end to the diagonal's upper face and keep the 9 cm inset. Drop the bottom rail under that triangle, or keep it only as the diagonal's seat. Then extend the glass balustrade and handrail through the lower open triangle of each end bay, to the end post. Re-render front, front_corner, aerial, rear and louvre_wall. |
| 2 | P1 | front_corner, aerial (also rear_side, rear_north, rear) | The glass balustrade in the four open bays renders as a near-opaque, neutral light-grey band filling the lower half of each bay. Sampled pixels are about RGB 104-108/103-105/95-96 in front_corner and aerial, with no deck boards readable through it. From above, the bridge therefore reads as having solid grey parapet walls. In the matched oblique source, the same panels are almost invisible, and the warm deck boards (about RGB 200-230/160-190/105-140) read straight through them to the edge beam. This is a clear optical and material-hierarchy defect in the two headline views. | The glass material's Fresnel and reflection term dominates at the steep downward camera angle, and/or the transmission and alpha are too low. The overcast grey sky is being reflected as a flat grey. | Give the balustrade glass high transmission with low reflectance (for example, alpha around 0.15 or transmission around 0.9, roughness 0, with Fresnel/IOR reflection reduced or clamped). Then check that deck boards and the inner face of the edge beam are readable through the panels in front_corner and aerial. Front, deck_inside and glass_close already read transparent, so keep them unchanged. |
| 3 | P2 | rear, front, louvre_wall, front_corner | The louvre pitch is about 1.5 times finer than the source: about 19-20 thin slats per end bay in the render, against about 12-13 deep fins in source front and source oblique. The fins read as a slatted screen rather than deep, widely spaced fins. | The fin pitch and section were not derived from the source bay subdivision. | Set about 12-13 fins per end bay, using a deeper (wall-normal) and slightly wider section. |
| 4 | P2 | front, portal_end, architecture_close, left_side, right_side | Both end portals carry transverse knee braces from post to header, so the portal opening reads as trapezoidal. The source end portal (source front) is a clean rectangular post-and-header opening with a timber soffit. | The interior-frame transverse braces are also instanced on the end frames. | Omit the transverse knee braces on the two end portal frames only. |
| 5 | P2 | front, architecture_close, portal_end | A small dark box stands proud of the roof at each hip apex. It is the ridge-cap terminal, about 8 px high in portal_end. It does not pierce the roof from below, but it reads as a stub. | The ridge-cap box is extruded past the hip apex. | Trim the ridge cap to end flush at the hip junction, or mitre it into the hip caps. |
| 6 | P2 | architecture_close, front (crop) | A hairline black seam runs along the top face of the portal header, against the triangular hip soffit infill. | There is a small gap between the header top and the soffit plane. | Close the gap (raise the infill or extend the header by a few mm). |
| 7 | P2 | top, architecture_close, front_corner | The roof's hip-end faces are plain, with no standing seams. The source oblique shows seams on the hip face as well. | Seams are generated only on the two long roof planes. | Add seams to the hip faces, running down the fall. |
| 8 | P2 | top, rear, stream_under, pier_abutment | The stream has hard vertical concrete edges with railings at water level throughout. The source banks are soft, planted edges that meet the water (top, oblique), with paved lower paths only near the bridge. The approaches are uniform grey tiles rather than stone setts. | The context is simplified as a canal. | Optional: soften one bank with a planted slope into the water, and give the paving a sett-scale grid. |
| 9 | P2 | right_side, rear_north | In right_side, a context block fills the right ~20 % of the frame and a tree fills the left, so the bridge is small but legible. rear_north clips both bridge ends (it is a detail view, so this is acceptable). | Camera placement. | Move the right_side camera off the block face, or narrow the FOV onto the bridge. |
| 10 | P2 | front | The large round pier under the near portal-side post, prominent in source front, is hidden behind the railing and ground in the render's front view. | The render camera is higher and further onto the plaza than the source camera. | Optional: lower the front camera by about 0.5 m, or move it towards the stair rail, so the near pier shows below the edge beam. |

## 3. Source conformance checklist

| item | status | view(s) used | note |
|---|---|---|---|
| Plan and proportions | conforms | top, rear vs source top | Post-to-post length divided by roof length is 0.888 in the render (rear) against 0.889 in the source (top). Roof length:width is about 5.0 against 4.7. The hipped ends and the timber landings at both ends match. |
| Frames and braces | deviates | rear, front_corner, front, portal_end | 7 frames and 6 equal bays (rear posts at x≈175/350/545/725/910/1085/1245), and 4 open interior bays with knee braces at both post heads. One long diagonal per end bay, rising from the portal-side foot to the midspan-side head, matching both sources. These all conform. Deviation: P2 #4 (extra transverse knee braces on the end portals). |
| Louvres | deviates | front, rear, louvre_wall, architecture_close vs source front/oblique | The end-bay louvres are full height where the source fins stop on the diagonal (P1 #1), and the pitch is too fine (P2 #3). The single upper louvre layer between the continuous rail and the wall plate in the open bays conforms. |
| Roof and eaves | conforms (P2 polish) | front, roof_eaves, top, rear | Grey standing-seam roof, hipped ends and deep eaves. Ridge-cap stub (#5), plain hip faces (#7). |
| Deck | conforms | deck_inside, glass_close, portal_end, top | Timber deck with a kerb, and landings beyond both portals. |
| Piers and abutments | conforms | pier_abutment, rear, stream_under | Round piers with concentric headstocks stand on the lower walkway at the water edge, as in source front and oblique. Wedge abutments are cut into both banks, and the side faces follow the slope. |
| Approaches and railings | conforms (simplified) | front, left_side, portal_end, top | Paved approaches with steel bar railings, and glass on the landing boards. Tile scale is simplified (#8). |
| Stream and banks | deviates (P2) | top, stream_under | The channel is canalised with hard edges (#8). Relative stream width under the span is 0.47 against 0.52 in the source. |
| Planting | conforms (simplified) | aerial, rear, top | Green bank strips, shrubs and trees. |
| Context | conforms | front_corner, aerial, left_side | Brick apartment blocks with balconies. |
| Materials hierarchy | deviates | front_corner, aerial | Timber, zinc, concrete and paving conform. The glass reads as an opaque grey solid (P1 #2). |

## 4. Camera validity

- No view has an occluded target, a clipped asset in a whole-envelope view, or an illegible target.
- front: holds the whole near portal, the roof corner and the eaves. Valid.
- aerial: clear of the foreground tree, which sits at the lower right and does not overlap the bridge. Valid.
- right_side: valid but weak framing (P2 #9).
- rear_north: clips both ends. It is a detail view, so this is acceptable (P2 #9).
- left_side and right_side are end-on approach views, not side elevations. The side elevations are covered by rear, rear_side and rear_north.

## 5. Previous-version findings: resolved in pixels?

| previous finding / required hold | resolved? | evidence |
|---|---|---|
| v002 P1: side wall read as 10 narrow bays (louvre-only end bay, open diagonal bay, six open bays) instead of 6 equal bays between 7 posts | **Resolved** | rear: 7 posts, 6 bays of about 160-195 px (equal within perspective). front_corner and aerial: end bay, 4 open knee-braced bays, end bay. The separate louvre-only bay and the open diagonal bay are gone. The bay-to-roof proportion now matches the source (see checklist). New residual issue: the end-bay louvre fill (P1 #1) is a distinct defect, not a regression of the bay count. |
| Each end bay: full-height louvres on a bottom rail, 9 cm inside the post line, diagonal laid over them on the outside | Built as claimed (rear end bay at 5x, front portal crop, louvre_wall) | However, the claim itself does not match the sources: see P1 #1. |
| Four interior bays open, knee braces at both post heads under the continuous rail, one louvre layer between rail and wall plate | Holds | facade_close, roof_eaves, stream_under, rear |
| Glass balustrade along the four open bays | Holds geometrically | rear, deck_inside, glass_close. The material reads opaque from above (P1 #2). |
| One regular louvre layer with a bottom rail in the end bays | Holds | rear end-bay crop, architecture_close |
| Nothing piercing the zinc roof at the hips | Holds | Nothing penetrates from below. Only the ridge-cap terminal stands proud at the apex (P2 #5). |
| No black voids at the portal post tops | Holds | architecture_close and front crops. There is a hairline seam along the header top, not at the post tops (P2 #6). |
| Straight, shallow, square-ended edge beams bearing on concrete abutments cut into both banks | Holds | rear left and right crops, pier_abutment, stream_under |
| Round piers with concentric headstocks | Holds | pier_abutment, rear, rear_north |
| Front camera holds the whole near portal, roof corner and eaves | Holds | front |
| Aerial clear of the foreground tree | Holds | aerial |
| Landing glass on the landing boards | Holds | portal_end left landing crop: the glass foot sits on the landing edge. |
