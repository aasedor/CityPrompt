# Independent RLASM v6.1 holistic review: chamfer v006

Reviewer: independent and adversarial. I did not build this candidate. I looked only at the three locked sources, the 18 renders and the 4 phone boards, all opened at full resolution, with crops of the dome base, lantern, chamfer entrance and front-view bay. I read no build code, reports or notes.

## 1. Verdict

**VISUAL_REWORK_REQUIRED**. The v005 P0 (floating lantern) and two of its three P1s (entrance, cornice) are fixed in the pixels. Two P1s remain at the identity element. The copper dome still sits on a recessed stone drum ringed by a balustrade, where the sources show a solid bay frieze and a projecting cornice carrying copper cresting. The dome also has none of the round oeil-de-boeuf dormers that all three sources show.

**Counts: P0 = 0, P1 = 2, P2 = 12**

### Storey count (my own reading from the pixels)
- **sources/front.png:** left wing (x 190-420) and right wing (x 650-850) each show a stone ground floor (y ~560-700), a first residential storey on a continuous iron balcony (windows y ~460-530, balcony y ~515-560) and a second residential storey with individual balconies (windows y ~330-420). A deep frieze, a cornice and a balustrade come next. The chamfer bay shows the same two residential levels above the arched entrance: a glazed storey between columns at y ~410-520, and an upper storey of three windows with a curved balcony at y ~285-365. A frieze and cornice at y ~240-285 come next, then the dome.
- **sources/oblique.jpg:** gives the same reading on both wings: ground, a continuous-balcony storey, an individual-balcony storey, then the frieze, cornice and balustrade.
- **Reading:** the sources show **3 storeys (ground + 2 residential) plus an attic frieze and parapet**, not the "five storeys" in the brief. The pixels also show warm brick at the continuous-balcony storey on both wings, not a stone piano nobile. They show flat-headed ground-floor shop openings; the round arch appears only at the chamfer entrance.
- **Render:** shows ground + 2 residential storeys + parapet, with brick on both residential storeys and flat-headed shop openings. This **matches the source pixels**. I am not raising the brief's five-storey or stone-piano-nobile wording as a defect, because the locked pixels contradict it.

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | **P1** | chamfer_dome (x 535-905, y 590-760); architecture_close (x 475-960, y 455-610); roof_terrace (x 545-850, y 680-790); front (x 430-530, y 460-500); rear_side (x 680-795, y 385-415) | **Dome base.** The dome stands on a plain stone drum that is set back behind a curved stone balustrade ring (about 12 square balusters) sitting on the bay top. It ends in a thin ledge, and the dome rises from that ledge. There is no projecting cornice. The cresting is a row of separate dark T-shaped posts on a plain copper band (chamfer_dome y 590-640) and reads as a fence or scaffold. The **sources** (front y 200-285, oblique crop around dome base, top) show something different. The bay's ornamented frieze stays solid and flush with the bow face up to a strongly **projecting cornice / copper eave**. Continuous pierced, scrolled **copper cresting panels** sit directly on that cornice at the dome foot. There is no balustrade and no recessed drum. | The v005 drum was only partly removed. A parapet balustrade module was carried around the bow, and the cresting was modelled as discrete posts. | Delete the curved balustrade ring and the recessed drum. Extrude the bow wall and frieze solid and flush to the dome springing. Cap them with a moulded cornice projecting about 0.6-0.8 m beyond the bow face, with a copper eave band on top. Replace the T-posts with a continuous ring of pierced scroll-silhouette cresting panels (about 0.8 m high) standing on the cornice lip and touching the dome skirt. |
| 2 | **P1** | chamfer_dome (dome x 550-890, y 310-640); architecture_close (x 495-945, y 15-450); front (x 355-560, y 270-460); left_side (x 880-1085, y 280-480); top (x 410-590, y 680-850) | **Dome has no dormers.** The render dome is a smooth gored shell with about 16 thin ribs and nothing on it. All three sources show **round oeil-de-boeuf dormers with hooded frames** at about 45 % of dome height, three of them on the street-facing half: front at about (465,160), (522,155) and (578,165); oblique at about (548,470), (608,480) and (668,465); in the top view they read as bumps on the ribs. They are a primary identity feature of this dome at every distance. | Dormers were never modelled. | Add round dormers on alternate main-rib axes at about 45 % of dome height: 4 in total, or 8 if the dome keeps 8 main ribs. Give each a projecting circular frame of about 0.6 m diameter, a small copper hood and a dark recessed glass disc, so each one shows depth. |
| 3 | P2 | chamfer_dome (x 470-970, y 750-930); front crop (x 360-525, y 595-760); architecture_close (x 465-970, y 750-840) | The bow balconies are separate straight pieces per facet with gaps. The outer facets have angled returns that stick out past the bow onto the wing wall. The source shows one continuous curved balcony per level with stone dies. | Per-facet balcony instancing. | Replace each level with one curved railing following the bow arc, with stone dies at the column axes. |
| 4 | P2 | chamfer_dome, architecture_close, ground_arcade (x 500-940, y 40-330) | The two bay storeys are identical glazed panels. In the source the lower bay storey is full-height glazing between columns, and the upper storey has three windows in stone surrounds over a balustraded balcony. | Single bay-storey module reused. | Make the upper bow storey stone wall with three framed French windows. Keep the lower storey as glazing between columns. |
| 5 | P2 | ground_arcade (x 620-820, y 415-745); crop | The entrance arch reads well but is faceted. Its transom sits at mid-height instead of at the arch springing. The keystone corbel (x 705-750, y 360-430) overlaps the arch crown. The reveal is shallow. | Low arch segment count; mullion grid not tied to the springing. | Use 16+ arch segments, move the transom bar to the springing line, recess the glazing about 0.25 m with visible returns, and seat the keystone on the arch extrados. |
| 6 | P2 | all dome views | The dome is the same salmon-terracotta as the roof deck, so it does not read as copper. It also has about 16 even gores instead of the source's 8 strong ribs. | Material reuse and gore count. | Give the dome a distinct darker copper-brown clay swatch and 8 pronounced ribs (lantern and cresting in the same swatch). |
| 7 | P2 | top (x 705-835, y 450-580); aerial (x 700-810, y 490-580); front_corner (x 680-790, y 465-530) | The pyramid rooflight reads as a flat grey square from above. A low peak is only just visible in left_side (x 640-760, y 450-495). The source top shows a pronounced glazed pyramid with ridge ribs. | Pyramid too low; no ridge members. | Raise the pyramid pitch to about 35-40 degrees and add four ridge ribs and a perimeter curb. |
| 8 | P2 | facade_close, balcony_ironwork | The brick is pale peach. The source brick is warm red-orange. | Palette value. | Darken and saturate the brick swatch toward the source mid-tone. |
| 9 | P2 | top; rear_court | There is no rear light-well or court. The source top shows a light-well on the inner side of the block (x 520-620, y 200-330). | Not modelled (unseen faces). | Optional: cut a small light-well at the rear party line. |
| 10 | P2 | front.png | The "front" camera looks square onto a wing elevation, with the bay at the left edge. The source front is an eye-level corner view centred on the chamfer. | Camera role mismatch. | Aim the front camera at the chamfer axis from the street corner at about 1.6 m eye height. |
| 11 | P2 | front (x 570-1070, y 470-500); chamfer_dome (x 100-470 and x 970-1340, y 490-620) | The wing balustrades run unbroken between corner blocks. The source has pedestal dies on each bay axis. | Not modelled. | Insert dies over each pier axis. |
| 12 | P2 | ground_arcade; glass_close; ground_arcade (x 405-450 and x 975-1030, y 260-390) | The ground floor is flat with incised joint lines only. There are no pilasters or consoles between the shop openings, which the source front shows clearly, and the reveals are shallow. Slivers of orange brick also show between the bow and the flanking stone piers, where the source is all stone. The ironwork and window heads are plain bars and plain lintels, which is acceptable for clay. | Simplified ground and chamfer-wall materials. | Add shallow pilasters with simple capitals between the shop bays, deepen the reveals to about 0.3 m, and switch the chamfer wall behind the bow to the stone swatch. |

## 3. Source conformance checklist

| item | status | view(s) used |
|---|---|---|
| Silhouette (square corner block, chamfer, dome on chamfer, flat roof with parapet) | conforms | front_corner, aerial, top, roof_terrace vs oblique/top |
| Storey count (ground + 2 residential + attic frieze/parapet, by my reading of the source) | conforms | front, left_side, facade_close vs front/oblique |
| Chamfer bay and dome | **deviates** (P1 #1 dome base on balustraded drum; P1 #2 no dormers; P2 #3, #4, #6) | chamfer_dome, architecture_close, roof_terrace |
| Window rhythm and balconies (4 bays per wing; continuous balcony on first storey, individual on second; tall French windows) | conforms (ironwork simplified, acceptable for clay) | facade_close, front, balcony_ironwork |
| Ground-floor arches and entrance (flat-headed shop openings on wings, round-arched glazed door on chamfer between piers with corbelled bow above) | conforms, with P2 detail (#5, #12) | ground_arcade, glass_close |
| Cornice and parapet (bracketed cornice with shadowed soffit, balustrade) | conforms (dies missing, P2 #11) | cornice_contact, facade_close, rear_court |
| Roof elements (pyramid rooflight, small rooflights, chimney stacks) | conforms in presence; pyramid too flat (P2 #7) | top, aerial, roof_terrace, left_side |
| Materials hierarchy (stone ground / brick wings / stone dressings and bay / copper dome / terracotta roof) | deviates slightly (dome same colour as roof, pale brick, brick slivers on chamfer wall; all P2) | facade_close, chamfer_dome, ground_arcade |

## 4. Camera validity

No view is invalid. The target is legible and unclipped in every view.
- **front_corner and aerial:** the building fills only about 30 % of the frame, but it is legible.
- **front.png:** shows a wing elevation, not a chamfer-centred view (P2 #10).
- **interior:** dark but legible: a French window with a balcony rail.
- **glass_close and cornice_contact:** tight crops, but they show the intended contact.

## 5. v005 findings: status in the v006 pixels

| v005 finding | severity | status | evidence |
|---|---|---|---|
| Lantern floats above dome apex, background under base disc | P0 | **resolved** | chamfer_dome (x 670-770, y 265-330): a copper neck cylinder runs from the dome apex to the lantern base disc, with no background gap; the same holds in architecture_close and left_side. |
| Chamfer entrance a flat-headed glass panel (needs a round-arched door with transom, frieze over the arch, projecting piers, corbelled bow underside) | P1 | **resolved** (detail residue P2 #5) | ground_arcade (x 545-895, y 360-750): a round-arched glazed door between projecting piers, a frieze band and corbel blocks under the bow. The transom sits at mid-height, not at the springing. |
| Dome squat hemisphere on a tall plain stone cylinder (needs a taller ribbed dome whose copper skirt and cresting sit on the bay cornice, no drum) | P1 | **partly** (still P1, finding #1) | The dome is now taller and ribbed. It still sits on a recessed stone drum behind a balustrade ring, with no projecting cornice and post-type cresting (chamfer_dome x 535-905, y 590-760). |
| Cornice a flat fascia (needs a heavily projecting bracketed cornice with shadowed soffit) | P1 | **resolved** | cornice_contact (x 0-920, y 400-560): modillion brackets under a projecting slab, with a shadowed soffit between them. The same appears in facade_close and rear_court. |
| Bow balconies segmented per facet | P2 | not resolved | chamfer_dome (x 470-970, y 750-930) |
| Mauve dome colour | P2 | partly | No longer mauve, but salmon-terracotta, the same as the roof (P2 #6). |
| Flat pyramid rooflight | P2 | partly | A low pyramid shows in left_side; it is flat from top and aerial (P2 #7). |
| Flat bow soffit | P2 | resolved | Corbel blocks under the bow (ground_arcade, y 360-430). |
| Pale brick | P2 | not resolved | facade_close |
| No rear light-well | P2 | not resolved | top, rear_court |
| Front camera on a wing elevation | P2 | not resolved | front.png |
| No balustrade dies | P2 | not resolved | front, chamfer_dome |
