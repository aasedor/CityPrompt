# Independent holistic review: zinc dome corner block, v006 (RLASM v6.1 architectural clay)

Reviewer: independent, adversarial. Evidence: the three locked sources (front.png, oblique.jpg, top.jpg), all 18 renders opened at full resolution, all four phone boards, plus enlarged crops of the chamfer and dome in both sources and renders. Builder notes, metadata and counts were not used as proof.

## 1. Verdict

**VISUAL_REWORK_REQUIRED.** The v005 cornice defect is fixed in the pixels. The signature corner dome still differs clearly from both aerial sources. In the renders the dome narrows inward to a smaller ring, sits on a tall drum mostly buried in the mansard, and carries a second porthole stacked under its oculus. The oculus dormer sticks out as a ring with a loose hood slab. In the sources a broad, stilted dome springs from a low attic just above the cornice, and its single oculus sits in a stone aedicule.

Counts: P0 = 0, P1 = 1, P2 = 9

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | corner_dome, front, front_corner, left_side, roof_court, aerial, architecture_close (compare oblique, top, source front) | **The dome profile, springing height and oculus differ from the sources.** (a) **The dome narrows inward at its base.** Its widest point is about 446 px across in corner_dome, roughly 70 px above a springing ring only about 378 px across, so the ring is about 0.85 of the dome's maximum width. The ribs curl back in under the bulge, so the dome reads slightly onion or bell shaped. In oblique and front the dome is a stilted hemisphere whose sides are nearly vertical at the base and full width at the springing. (b) **The dome springs too high.** It sits on a stone drum standing about 40 px above the chamfer cornice in front_corner, against a dome height of about 100 px (ratio about 0.4). In oblique the springing is about 17 px above the cornice against a dome of about 153 px (ratio about 0.1), with the dome rising almost directly from the eave. (c) **There are two stacked round openings.** A drum oeil-de-boeuf sits directly below the dome oculus. No source shows a drum opening under the oculus; the sources show only the base of the aedicule there. (d) **The oculus dormer reads as a ring sticking out of the dome.** It is a thick ring projecting well clear of the dome surface, with a thin flat hood slab overhanging it. In left_side it breaks the dome silhouette like a horn, and in aerial it appears edge-on as a loose white card beside the dome. In all three sources the oculus is set in a stone aedicule with scrolled ears and a cartouche, standing on the springing ring at the foot of the dome. | When the corbel ring was removed, the v005 drum was moved back behind the cornice but kept its full height, so the dome stayed raised. The dome profile curve has its maximum radius above the springing. The oculus is modelled as a torus plus a slab, not as an aedicule. | 1. Lower the dome springing to a low attic or base ring sitting just behind the cornice at eave level, about 0.1 to 0.15 of the dome height above the cornice top. 2. Re-profile the dome as a stilted hemisphere with its maximum radius at the springing, removing the inward curve at the base, and keep the ribs, lantern and finial. 3. Rebuild the oculus as a stone aedicule standing on the springing ring: oculus frame flush with the aedicule face, ears and a crowning cartouche, with no floating hood slab. 4. Remove the drum oeil-de-boeuf from under the oculus, or, if the brief's drum windows must stay, make them small and below the springing, never stacked under the oculus. 5. Re-render front, front_corner, corner_dome, left_side and aerial, and compare them against oblique and front. |
| 2 | P2 | corner_dome, architecture_close, front_corner | **The drum is sliced by the mansard planes.** Where the hip planes cut the drum, what remains visible is a shield-shaped stone apron with knife-point pilaster strips, and the scroll consoles land on the slope. This is architecturally plausible as a penetration, but it reads as a modelling cut, with no curb or flashing. | The drum has been pushed down into the mansard without a curb. | Fixing finding 1 removes it. Otherwise add a flat curb or flashing ring where the drum meets the slope and end the pilasters on it. |
| 3 | P2 | glass_close, facade_close, balcony_ironwork | **Small black cube nubs appear at the frame corners** of every window and shopfront. | Corner joint geometry has a dark material, or the faces z-fight. | Give the corner blocks the frame material, or remove them. |
| 4 | P2 | mansard_dormers, corner_dome | **The dormers are capped with flat slabs.** The source dormers carry curved or pedimented hoods. | Simplified dormer cap. | Use a segmental or pedimented cap. |
| 5 | P2 | cafe_awning, front | **The awning valance has square tabs and the awning is shallow.** The source awning is a deep red awning with a plain straight valance, extending about 2 to 3 bays each side. | Awning preset. | Use a plain valance, deepen the projection and add a bay each side. |
| 6 | P2 | architecture_close, front_corner (compare source front) | **The chamfer windows are narrow two-leaf openings** set in a wide plain stone field. The source has broad transomed casements, and the second-storey chamfer balcony sits on large scroll consoles. | Window module reused from the side faces. | Widen the chamfer windows to transomed triple lights, and add the console pair under the chamfer balcony. |
| 7 | P2 | right_side, rear, rear_side | **The north and east faces have no balconies** and small punched ground-floor openings. They are coherent as secondary faces, but the street grammar is weaker. These faces are not visible in any source. | Deliberate secondary-face simplification. | Optional: carry the balcony rhythm round, or treat the faces as party or rear walls. |
| 8 | P2 | front (phone-01) | **The front camera is axial to the chamfer and distant**, with the building about 45 % of the frame width. The source front is a closer three-quarter view. The view is still legible and valid. | Camera preset. | Move closer and rotate toward the source's three-quarter angle. |
| 9 | P2 | front_corner, roof_court, aerial | **The chimneys are few, stone coloured and plain.** The source chimneys are numerous brick stacks with pots on the party walls. | Simplification. | Make the stacks brick, with pots. |
| 10 | P2 | interior | **The inner faces read as brick-red** through the court opening, and the room is dim. It is legible. | Exterior brick material is shared on both faces of the court walls. | Use the plaster tone on interior faces. |

## 3. Source conformance checklist

| Item | Status | View(s) used |
|---|---|---|
| Silhouette (perimeter block, chamfered south-west corner, inner court, flat-topped mansard) | Conforms. The block massing, chamfer and open court read correctly. The roof is flatter than the hipped source roof, but the brief specifies a flat top. | front_corner vs oblique; top/aerial vs top |
| Storey count (stone ground floor, stone first storey, three brick storeys, mansard) | Conforms | left_side, front_corner, architecture_close |
| Chamfer and dome | **Deviates.** The chamfer is correct and the cornice is continuous across it. The dome is pinched at its base and raised on a tall drum (finding 1). | corner_dome, front_corner vs oblique, front vs source front |
| Drum windows and lantern | **Deviates.** The lantern (open columns, cap, gilded finial) conforms. The oculus is a ring sticking out of the dome, not a stone aedicule, and an extra drum oeil-de-boeuf is stacked beneath it. The side drum openings are hidden by the mansard, as the builder states. | corner_dome, left_side, aerial |
| Balcony rhythm (individual on 1st and 3rd, continuous on 2nd and 4th) | Conforms on both street faces and on the chamfer | left_side, facade_close, balcony_ironwork, architecture_close |
| Brick-and-stone banding (string courses, quoins, surrounds) | Conforms | facade_close, balcony_ironwork, right_side |
| Mansard and dormers | Conforms in rhythm and placement: arched dormers with voussoirs, cheeks seated on the slope. The caps are simplified (P2). | mansard_dormers, left_side, rear |
| Cafe awning and ground floor | Conforms. A red awning wraps the chamfer, and there are stone piers and glazed shopfronts with shallow but visible reveals. The valance and depth are simplified (P2). | cafe_awning, glass_close, front_corner vs oblique |
| Cornice | Conforms. It is bracketed and continuous across the chamfer and both street faces. | corner_dome, architecture_close, front crop, mansard_dormers |
| Materials hierarchy (stone base, brick upper storeys, zinc roof and dome, iron balconies, gilt finial) | Conforms | all whole-envelope views |

## 4. Camera validity

- No view has an occluded target, a clipped asset or illegible content.
- front: valid but distant and axial (finding 8).
- interior: dim but legible.
- rear_court: legible, steep downward view into the court.
- aerial and top: the whole asset is in frame.
- The detail views each frame their target.

## 5. Previous-version findings

| Previous finding | Status in v006 pixels |
|---|---|
| v005 P1: the drum bulged forward past the chamfer wall on a curved corbel soffit and broke the main bracketed cornice | **Resolved.** In corner_dome, architecture_close and the front crop, the bracketed cornice runs unbroken across the chamfer between the two pier-cap blocks. The drum front sits behind it, with a strip of zinc between them. No corbel soffit is visible. |
| Builder's claimed side effect: the steep mansard hides the two side oeil-de-boeuf openings, and only the front one is visible | **Confirmed.** Only the front drum opening is visible in every view. The drum sides are buried in the mansard slopes, which produces the cut-apron look in P2 finding 2. |
| "Nothing else changed" | Cannot be verified from pixels without the v005 renders, and was not used as evidence. The dome defects in finding 1 are present in v006 and were not raised in the v005 review. Whatever their history, they block approval now. |
