# Independent holistic review: clay-amsterdam-canal-warehouse v003 (RLASM v6.1)

Reviewer: independent; I did not build this candidate. I judged only the rendered pixels in `renders/*.png` and `boards/*.png` against the locked sources `sources/front.png`, `sources/oblique.jpg` and `sources/top.jpg`. I opened all 18 renders, the 3 sources and the 4 phone boards with the Read tool. I made zoomed crops only in the new folder `/tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/crops-indrev-913e8033/`.

## 1. Verdict

**Verdict: VISUAL_REWORK_REQUIRED**. The envelope, storeys, gables, door stacks, east wall and the two-canal site now read correctly, but three P1 defects remain:
- a tan slot is still open in the front valley;
- the coping on the new curved canal end shows black wedge gaps;
- the roof deck has been raised to the west ridge and widened to run from ridge to ridge, where the top and oblique sources show a narrower sunken deck between inner slopes.

Counts: P0 = 0, P1 = 3, P2 = 10

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | top, roof_deck (also on board 4, top) | In the front valley between the two gables, a flat tan/brown rectangle (top.png about x 628-645, y 607-650; RGB about 90,82,74) shows behind the valley pier cap. Zoomed in roof_deck, it is a flat floor lying between the two roof surfaces, which stop short of the valley and leave an open channel about 1.5-2 m long. This is the "tan strip in the valley" from v002, still there. | The inner slopes and the apex of the hip plate do not close onto a single valley line. The top of the interior section wall (or a valley board) is still exposed through the gap. | Bring both inner slopes and the apex of the hip plate down to one shared valley edge (or add a grey valley gutter that covers the slot) running from the valley pier back to the deck corner. Delete or lower whatever tan surface is visible there. Re-check in top and roof_deck. |
| 2 | P1 | top, front_corner, aerial, right_side, rear_side, left_side (the curved end shows in every view of the quay corner) | The white stone coping on the new curved parapet end at the street line shows a ring of black triangular "teeth": dark wedge gaps between straight coping segments around the curve. It is very visible against the white coping, in plan and in every elevated view. | The curve is approximated by rectangular coping blocks with no mitre, so open wedges are left on the outside of the arc and the dark underside shows through. | Build the curved coping as one swept or bevelled ring (or mitre each segment so they meet), and close the coping's outer and top faces. Re-render top and front_corner. |
| 3 | P1 | top, front_corner, aerial, roof_deck, gable_tops, rear, left_side vs sources top and oblique | The flat deck sits level with the west ridge and spans almost the full distance between the ridges (top.png: deck x 483-795 between ridges at about x 480 and 812, about 95% of that span). No west inner slope continues north beside it. From the oblique cameras the roof reads as a high flat plateau, and the rear profile is a clipped flat-topped gable. In the top and oblique sources, the deck is sunken and narrower: about 56% of the span between ridges (top source: west ridge about x 445, deck x 530-710, east ridge about x 765). The inner slopes of both sections run the full depth beside it and fall to the deck. A horizontal tiled ridge, carrying a chimney, separates the top edge of the hip plate from the lower deck. | This was the v002 "warped plate" fix: the deck was raised flush with the west ridge so the plate could stay planar. | Lower the deck to about mid-height of the inner slopes and inset it about 25% of each section's half-width from each ridge. Carry both inner slopes north alongside it. Run the top of the hip plate as a short horizontal ridge between the two ridge points, with the deck stepping down behind it. Keep the hip plate planar. Re-check against the top source and the oblique source. |
| 4 | P2 | front, arched_doors, facade_close | The cart doors are plain vertical timber boards up into the arch head. In the source, the arch head of each cart door holds a small glazed fanlight with bars. | The fanlight was simplified away. | Add a glazed band with bars at the springing line inside the arch. |
| 5 | P2 | arched_doors, facade_close | A faint rectangular outline sits around the shoulders of the cart-door arch, and the spandrels inside it have no course lines. | The carrier or aperture patch is offset from the main wall plane, or has no course-line texture. | Make the patch coplanar with the wall and continue the course lines across it, or remove it. |
| 6 | P2 | architecture_close, right_side, rear_side, aerial | The dormer on the east slope has a pitched (gabled) roof. The source dormer is a flat-topped box dormer clad in zinc, with a white fascia and a two-pane window. | Generic dormer preset. | Use a flat-roof box dormer with a white fascia. |
| 7 | P2 | top, roof_deck, aerial, gable_tops | The deck vents are square boxes with dark lids; the source has round, cylindrical hooded vents. The source chimney on the horizontal ridge at the top of the hip plate is missing. | Simplified roof furniture. | Use cylindrical vents and add the brick chimney at the head of the hip plate. |
| 8 | P2 | right_side, front vs front source and oblique source | The side door in the east wall is in the 4th of 7 ground bays counting from the quay. In both sources it is in the 3rd bay. | Bay index. | Swap the door and the window in bays 3 and 4. |
| 9 | P2 | gable_tops, roof_deck | The hip plate carries a soft dark diagonal gradient, so it reads slightly curved in close-up. It is probably a soft shadow from the east ridge. Its edges now sit on both slopes and no lift is visible. | Soft sun shadow or smooth-shaded normals. | Set the plate to flat shading. If the gradient is only shadow, accept it. |
| 10 | P2 | front, front_corner, aerial, left_side | The neighbour to the west is a plain triangular-gabled box. It has unframed dark windows, and its roof is the same colour as its walls. The source neighbour has a neck/bell gable with white trim, white window frames and a red tile roof. | Low-detail context mass. | Add a white-trimmed gable profile, white window frames and a tile-coloured roof. |
| 11 | P2 | front, front_corner (vs front source right edge, oblique source, top source) | The low red-tile gabled annex behind the warehouse on the east street (north of the east wall) is missing, so the east wall ends against an empty plot. | Context element was not modelled. | Add a simple one- to two-storey mass with a red-tile gabled roof north of the east wall. |
| 12 | P2 | front, plus the hoist beams in every gable view | The front camera is low and tilted up, so verticals converge (three-point keystone). The source is two-point with vertical verticals. Separately, each hoist beam is a long tan timber block hanging well below a small white hood; in the sources the white hood is the dominant element. | Camera pitch without lens shift; proportions of the beam and hood. | Level the camera and use shift (or match the source pitch). Shorten the beam under the hood. |

## 3. Source conformance checklist

| item | status | view(s) used |
|---|---|---|
| Silhouette (two parallel gabled sections, corner block) | conforms at the street faces. The roof deck deviates (finding 3). | front, front_corner, aerial vs front, oblique |
| Storey count and proportions | conforms: four storeys (ground plus three loading levels, the top one in the gable). The western section is lower and somewhat narrower (plan width ratio about 0.9, consistent with the source's about 0.9 at the facade line). | front, top, rear vs front, top |
| Brick and joints | conforms for clay: red-brown body with course lines and a darker plinth. Minor patch seam (finding 5). | facade_close, glass_close, arched_doors |
| Gables: copings, shoulder piers, pinnacles, hoist beams | conforms: white stone copings on all rakes, raised shoulder piers at the outer feet and the valley, a brick pinnacle with stone cap at each peak, projecting hoist beams with hoods. Beam proportion P2 (finding 12). | front, gable_tops, architecture_close, aerial |
| Loading doors and shutters | conforms: three green glazed round-headed loading doors stacked on each section axis, green board shutters folded flat on both sides, stone sills, brick arches. | facade_close, loading_doors, front |
| Cart doors (arches, springers, keystones) | conforms: round-arched timber doors with brick arch ring, stone springers, stone keystone and stone base blocks. The leaves reach the paving. Fanlight missing (finding 4). | arched_doors, front, front_corner |
| Windows (arches, frames, sills) | conforms: segmental heads with brick arches, dark multi-pane frames set back with visible reveals, stone sills. Placement flanks levels 1-2 and the ground, as in the source. | glass_close, loading_doors, facade_close |
| Anchors | conforms: vertical iron anchors at the floor lines on all faces. | glass_close, east_side, right_side |
| East wall windows and cornice | conforms: two rows of small segmental windows plus a ground row of tall arched windows and a door, 7 bays, white cornice under the eave, blank brick with anchors under the cornice. Door bay index P2 (finding 8). | east_side, right_side vs front, oblique |
| Roofs: two gables and valley | gables conform. The valley deviates (finding 1, open tan slot). | top, roof_deck, gable_tops |
| Roofs: hip plate | conforms in shape (planar triangle from the valley to the deck front at both ridges), with a P2 shading note (finding 9). | top, gable_tops, aerial |
| Roofs: deck and vents | deviates: the deck is raised to the west ridge and wider than the source (finding 3); vents are square, not round (finding 7). | top, roof_deck vs top, oblique |
| Roofs: dormer | present at the right position on the east slope. Its form deviates (gabled, not a flat box; finding 6). | right_side, architecture_close |
| Roofs: chimneys | present (pinnacles, chimneys on the west slope, the deck and the east slope). The chimney at the head of the hip plate is missing (finding 7). | aerial, front_corner, top |
| Quay | conforms: paved quay along the south face with a tree and a lamp. | front_corner, top, front |
| Parapet | conforms in layout: low brick parapet with stone coping along the south canal, ending in a curve at the street line. Its finish deviates (finding 2, wedge gaps). | top, front, front_corner |
| Canals | conforms: two separate canals. The south canal ends at the building's east line, the street is paved south across the corner, and the east canal begins north of it at about the facade line. | top vs top source corner |
| Neighbour | partly conforms: an attached gabled red-brown canal house to the west, flush with the facade, but simplified (finding 10). | front, aerial, top |
| Materials hierarchy | conforms: brick body, white stone trim, green joinery, dark window frames, tan timber cart doors, grey roof, grey deck. | all |
| North face | not visible in any source. It is coherent with the visible grammar (segmental windows, anchors, arched door, coped gable). | rear, rear_north |

## 4. Camera validity

All 18 views are legible. None has its target occluded or the asset clipped badly enough to make the view invalid.
- front: low camera tilted up with keystoned verticals (P2, finding 12). The building is fully framed from the paved corner, as the v002 fix intended.
- gable_tops: the valley foot is cut by the bottom frame edge. That is exactly where finding 1 sits, so this view cannot show the defect. Reframe it about 10% lower.
- rear_north: the top of the north gable is cropped. This is acceptable for a wall detail.
- left_side: the west face is mostly a party wall hidden by the neighbour, so the view mainly shows the north face. This is inherent to the site, not a defect.
- interior: dark but legible. The openings show depth.

## 5. Previous-version (v002) findings: status in the pixels

| v002 finding | status | evidence |
|---|---|---|
| Fourth row of small attic windows on the east and north walls under the cornice | **Resolved** | east_side, right_side, rear and rear_north show two upper rows plus the ground row, with blank brick and anchors under the cornice. This matches the front source east wall (two upper rows plus ground). |
| Stone plinth running across both quay cart doors and the east side door, so the leaves stop above the paving | **Resolved** | In arched_doors the plinth stops at the stone base blocks at each jamb, and the leaves reach the paving. The west cart door in front_corner, the east door in right_side and the north door in rear do the same. |
| South and east canals joined into one L of water round the corner | **Resolved in layout** | top shows two canals: the south canal ends in a curved parapet at the building's east line, the street is paved across the corner, and the east canal starts north of it. The front camera stands on the paved corner. A new finish defect on that curved end is raised as finding 2 (P1). |
| Hip plate reading as a warped sheet lifted off the slopes over a tan strip in the valley | **Partly resolved** | The plate now reads as a planar triangle with its edges on both inner slopes, and no lift is visible in gable_tops, aerial or front_corner. Only a soft shading gradient remains (P2, finding 9). **The tan strip in the valley is still visible** in top and roof_deck (finding 1, P1). The fix also raised and widened the deck (finding 3, P1). |
