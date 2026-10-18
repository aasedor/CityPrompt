# Independent holistic review: lab v003 (RLASM v6.1 architectural clay)

Reviewer: independent; I did not build this candidate. Evidence used: only the locked sources (`sources/front.png`, `sources/oblique.jpg`, `sources/top.jpg`), all 18 renders at full resolution, and the 4 phone boards. Zoomed crops were written to `/tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/indep-review-v003-crops/`. Pixel coordinates refer to the 1440x1080 renders.

## 1. Verdict

**VISUAL_REWORK_REQUIRED**: the plan, storey count and identity elements are all present, and three of the four v002 findings are fixed. One v002 P1 is still there (pure-black end faces at the entrance portal head), and two hero-view problems remain: the perforated rooftop crown is lost behind a solid white upstand, and the east louvre infill still reads as narrow inset slits in a white frame.

Counts: P0 = 0, P1 = 3, P2 = 13

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | front (736-741, 662-666), cantilever (~1360-1395, 712-722); same defect class at rear (997-1000, 648-651, NW cantilever corner) and front_corner / rear_side / top (black dots on every exoskeleton column top along the east roof edge) | A solid black rectangle (RGB sum < 40) sits where the proud portal head meets the portal post at door-head height. It shows in the hero front view and again in the cantilever close-up. Smaller black squares and dots also appear at the NW bottom corner of the box and on the open tops of the exoskeleton columns. This is the v002 "black block at portal post/head" finding, still present. | The exposed end caps of the proud head box have missing faces, flipped normals or a black/unassigned material. The column tops are open tube ends showing unlit interior faces. | Close and recalculate normals on the head-box end faces, and give them the white structural material. Cap every exoskeleton column top and the cantilever corner piece. Re-render front and cantilever and confirm zero pixels with RGB sum < 40 on the structure. |
| 2 | P1 | front, compared with source front (also left_side, rear) | In the matched hero view the glazed box ends in a solid white upstand/spandrel band about a third of a storey deep. Above it only one row of square perforations shows, so the perforated plant screen is practically invisible and only the three stacks rise above a plain parapet. In the source front the glass runs to a thin roof edge and the perforated screen reads as a tall, continuous crown along the whole south side. The heavy white edge frame on all four edges of the box adds to the "white-framed block" reading, against the source's near-frameless glass box. | The top edge parapet/upstand is modelled too deep and solid. The screen is set back behind it at a height and position that a street-level camera cannot see over. | Reduce the box's top edge to a thin slab-edge band (on the order of the floor slab bands) with the glass running up to it. Raise the screen, or bring its south run closer to the edge (keeping the walkway from the top plan), so that in the front view it reads as a perforated crown of about half a storey, as in the source. |
| 3 | P1 | front, front_corner, rear_side (hero/oblique roles); elevation views right_side, exoskeleton, architecture_close are acceptable | In the oblique hero views the east louvre bays read as narrow, split vertical strips deeply recessed between doubled columns/beams and bracket blocks, with wide white reveals around them. The east elevation reads mostly white, with grey only in slits. In the source front and oblique, grey louvre panels sit nearly flush and fill the middle bays, behind a slender round-tube white frame. The louvres are also lighter than the source (about 135-140 luminance against about 94 in the source). The square, chunky exoskeleton members with corbel blocks are heavier than the source's slender tubes. The v002 symptom is therefore resolved in elevation only, not in the hero views. | The louvre panels sit too deep behind a second (facade-plane) column/beam frame, so deep reveals hide them at grazing angles. The exoskeleton member sections are oversized and square. The louvre material value is too light. | Bring the louvre panels forward to within a small reveal of the exoskeleton plane, or remove the inner duplicate column/beam frame in the louvre bays. Use slimmer (ideally round) exoskeleton members without the bracket blocks. Darken the louvre clay value toward the source grey. Re-check front and front_corner, where the grey louvre field should cover most of each middle bay. |
| 4 | P2 | facade_close, glass_close, rear_north | Black pinhead specks at every mullion/transom crossing. | Overlapping or unclosed mullion end faces at the nodes. | Trim the transoms between mullions, or cap the ends. |
| 5 | P2 | facade_close, front, rear_north | The curtain wall has a mid-height transom, giving two lites per floor. The source shows floor-to-floor panes. | Wrong panel module. | Remove the mid transom or make it much less prominent. |
| 6 | P2 | front, facade_close, glass_close | Slab bands are about 17% of the floor-to-floor height. The source's thin white bands are about 8%. | Slab-edge depth too large. | Halve the slab edge band depth. |
| 7 | P2 | facade_close, glass_close, front | A green duct runs at about bench height in every bay of every floor and reads like a rail behind the glass. Source services sit mainly at ceiling level, with vertical drops. | Duct layout. | Move the green run to the ceiling zone; keep the vertical drops. |
| 8 | P2 | front, front_corner, rear, cantilever | The west cantilever reads shallower than in the source (about 23% of box length against roughly a third). The angled soffit is pale white, where the source soffit is dark. | Ground-floor footprint too long to the west; soffit material. | Pull the west ground-floor wall back and give the soffit a mid/dark grey value. |
| 9 | P2 | right_side, architecture_close, cantilever, front | The concrete base walls are only weakly separated from the white steel (about 144-158 against 175-193; the source is about 117 against 178). | Concrete clay value too light. | Darken the concrete to a distinct mid-grey. |
| 10 | P2 | top, aerial, roof_screen | Three stack clusters (N-W, E, S). The source top shows four clusters of three (W, N, E, S). | Missing west cluster. | Add a west cluster of three stacks on the west duct run. |
| 11 | P2 | front, front_corner | An extra inset white column and a narrow glazed bay at the east end of the south face; the source glazing meets the exoskeleton corner column directly. | Corner-wrap module adds a bay. | Run the south glazing to the corner column. |
| 12 | P2 | v_pilotis, front | The portal posts continue above the head up to the soffit, forming an H, where the source shows a simple Π portal frame. A blurred elliptical highlight appears on the ground-floor glass. There are black slivers at the screen panel joints (stacks, roof_screen). | Post height; glass roughness/lamp reflection; panel joint gaps. | Stop the posts at the head; raise glass roughness or move the lamp; close the panel joints. |
| 13 | P2 | v_pilotis, front_corner, aerial, top | The v_pilotis detail view cuts off the V feet, so ground contact cannot be judged in that view (it can be in front). front_corner and aerial are far more distant than the source oblique, with the building about 30% of frame width. The top view is low contrast. | Camera framing. | Reframe v_pilotis to include the feet. Tighten the front_corner/aerial distance to match the source oblique. Increase contrast or exposure in the top view. |

## 3. Source conformance checklist

| item | status | view used |
|---|---|---|
| Silhouette / plan (corner site, streets south and east, near-rectangular block, plan ratio ~1.2) | conforms | top vs source top; aerial |
| Storey count (glazed ground + 3 glazed lab floors) | conforms | front, left_side, rear |
| Curtain wall and slab bands | deviates (bands too heavy, mid transom, solid top upstand; findings 2, 5, 6) | front, facade_close, glass_close |
| Coloured services behind glass (blue, green, yellow) | conforms (layout P2, finding 7) | facade_close, glass_close, interior, front |
| Cantilever west and angled soffit | conforms in kind; deviates in depth and soffit tone (finding 8) | front, cantilever, rear |
| V-pilotis and recessed glazed ground floor; entrance between the Vs | conforms (black head end, finding 1; H-portal, finding 12) | front, v_pilotis, cantilever |
| Concrete base walls (west end, service bays) | deviates (too light to read as concrete; finding 9) | cantilever, right_side, architecture_close |
| Exoskeleton: columns, beams | conforms in layout; deviates in weight and section (finding 3) | right_side, architecture_close, front |
| Exoskeleton: alternating diagonals | conforms (end bays, alternating per floor) | right_side, architecture_close |
| Exoskeleton: louvre infill and white panels | conforms in elevation; deviates in hero views (finding 3) | right_side, exoskeleton vs front, front_corner |
| Exoskeleton: SE corner wrap | conforms with an extra bay (finding 11) | front, top |
| Roof: pale edge walkway | conforms | top, roof_screen, aerial |
| Roof: perforated screen enclosing plant | conforms in roof views; not legible in front view (finding 2) | roof_screen, stacks, front_corner vs front |
| Roof: raised penthouse with units | conforms | roof_screen, stacks, top |
| Roof: duct runs | conforms | top, roof_screen |
| Roof: exhaust stacks in clusters of three | conforms; one cluster short (finding 10) | top, roof_screen, stacks |
| Materials hierarchy (white steel / grey glass / concrete base / grey louvres / coloured services) | deviates (concrete and louvres too light; findings 3, 9) | right_side, cantilever, front |
| North face (no source) | coherent with the visible grammar (glazed box, slab bands, services) | rear, rear_north |

## 4. Camera validity

- No view has its target occluded or the asset clipped in a way that invalidates the candidate. No P0 camera defect.
- v_pilotis: the V feet are below the frame, so this detail view cannot show contact. Contact is visible and clean in front (P2, finding 13).
- front_corner and aerial: legible but distant (building about 30% of frame width), which makes matched-role comparison with the source oblique weaker (P2).
- top: legible but low contrast. The large wedge across the ground is the building's own cast shadow, not an occluder (confirmed with an equalized crop).
- interior: dim but legible (benches, ceiling services).

## 5. Previous-version findings: resolution in pixels

| v002 finding | builder claim | status in v003 pixels |
|---|---|---|
| P1: middle east bays had vertical slats in small inset panels with wide white margins (source: horizontal blades filling each bay) | Full-bay louvre openings with horizontal blades | **Partially resolved.** In right_side, exoskeleton and architecture_close the blades are horizontal and fill each middle bay. In the hero front and front_corner views the louvres still read as narrow split strips with wide white reveals, the same perceived symptom, now raised as finding 3 (P1). |
| P1: roof screen perforated only on outer faces; far runs read as a plain parapet from above | Perforations on both faces of every screen run | **Resolved.** The far and inner faces show perforations in roof_screen, stacks, front_corner, aerial and rear_side. |
| P1: entrance portal inside the east V-piloti, with a leg crossing the doorway | Door in the bay between the two V-pilotis, which were moved apart, with a proud portal head | **Resolved.** The portal stands in the bay between the two Vs and no leg crosses the opening (front, v_pilotis, cantilever). |
| P1: black block where the portal post meets its head, and black triangle at the foot of the west V | Piloti legs offset so their faces never coincide | **Not resolved for the block; resolved for the triangle.** The west V foot is clean in front (no dark pixels). The black block at the head/post junction is still present in front (736-741, 662-666) and cantilever (about 1360-1395, 712-722). Finding 1 (P1). |
| Seven v001 findings resolved in v002 | n/a | The brief does not list them, so they could not be checked item by item. Every identity category in the brief was checked for regression: storey count, cantilever, coloured services, V-pilotis, exoskeleton columns/beams/diagonals/infill, perforated screen, penthouse, ducts, stacks, and plan from the top. None has regressed to missing or broken. The deviations recorded above are fidelity issues, not regressions to absence. |
