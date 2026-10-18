# Independent holistic review: lab v002 (RLASM v6.1 architectural clay)

Reviewer: independent; I did not build this candidate. I judged only rendered pixels against the locked source pixels (sources/front.png, sources/oblique.jpg, sources/top.jpg). I opened all 18 renders at full resolution and all 4 phone boards. Zoomed crops are in `/tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/indrev-v002-crops-7q3/`.

## 1. Verdict

**VISUAL_REWORK_REQUIRED**: the building's identity, orientation and storey count now read correctly with zero P0. Four P1 defects still block approval: the east louvre blades run vertically where the source blades are horizontal; the far runs of the roof screen read as solid from inside; the entrance portal is crossed by a V-piloti leg; and a black geometry artifact sits on the portal.

Counts: P0 = 0, P1 = 4, P2 = 9

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | right_side, exoskeleton, architecture_close, rear_side, front, front_corner | The louvre infill in the three middle east bays is made of **vertical** grey slats. Each panel is a smaller inset rectangle with a wide white margin to the columns and beams. In the front view, the foreshortened panels read as pairs of narrow dark slots, like windows. The source (front.png crop of the east face; oblique.jpg) shows **horizontal** louvre blades. Each panel spans from column to column and fills almost the whole floor height, so the louvres read as continuous grey bands behind the frame. | The blade array was modelled along the wrong axis, probably from the brief's phrase "vertical louvre panels", which describes the panels, not the blades. The inset frame margin on each panel is too large. | Rotate the blade array 90 degrees so the blades are horizontal, at about the same pitch as the source (roughly 12 to 15 blades per floor). Grow each panel to the clear opening between columns and floor beams, leaving only a thin edge frame. Keep the 3 middle louvre bays and the braced white end bays. |
| 2 | P1 | front_corner, aerial, rear_side, roof_screen, stacks | All four screen runs show perforations on their **outer** faces (left_side, rear, right_side, front, roof_screen). Their **inner** faces are blank white panels. In every elevated view, the two far runs, seen from the plant side, therefore read as a solid white parapet wall. In oblique.jpg the far (north and west) runs are visibly perforated from the inside. The perforations are dark grey squares, not see-through holes. | The perforation is a one-sided relief or decal on the outer face of a solid slab, not through-holes. | Make the holes go through the panel (boolean-cut array or an alpha/cutout material on a thin panel), or at minimum mirror the perforation onto the inner face. Re-render roof_screen, stacks, front_corner and aerial to confirm that the far runs read as perforated. |
| 3 | P1 | front, v_pilotis | The entrance door portal sits **inside the eastern V-piloti**. The V's west leg runs diagonally across the door opening, from the portal's top-left to its bottom-right. In v_pilotis, the portal head (lintel) runs into the V's east leg, so the two intersect. The portal posts run full height to the soffit, so it reads as a framed bay with a crossbar, not a door portal. In front.png the portal is a squat, freestanding, thick white frame at about half the ground-storey height. It stands between the two V's, clear of both legs. | The portal was placed by bay index without a clearance check against the V legs. Its posts were extended to the soffit. | Move the portal west into the clear zone between the two V's (in the source it sits just west of the east V's west leg). Make it a freestanding frame with two posts and a head, about 0.5 of the ground-storey height and about 1.5 times the current member depth. It must not touch the soffit or either piloti. Check that it is clear of both legs in plan. |
| 4 | P1 | v_pilotis (dominant), front (black marks at both lintel ends), v_pilotis lower-left (black triangle at the V foot) | A large solid black block sits at the junction of the portal post and lintel in the v_pilotis close-up. In the front hero view, the same junctions show as black dashes at both ends of the lintel. A small black triangle shows at the foot of the west V. | Back faces or flipped normals, or a zero-thickness or coincident box where the lintel and post overlap. The same applies to an open mesh gap at the joint of the piloti base. | Recompute normals and close the joints. Merge or offset the coincident faces. Rebuild the lintel and post as one closed solid. Re-render v_pilotis and front and check that no pure-black pixels show on white members. |
| 5 | P2 | facade_close, glass_close, cantilever, rear_north | Black pin-dots show at every mullion and transom intersection of the curtain wall. | Gaps where mullion and transom boxes meet. | Extend the transoms through the mullions, or add a junction cap. |
| 6 | P2 | front_corner, aerial, top | A row of black dots shows on top of each east exoskeleton column at roof level. | Open-ended column tubes or uncapped hollow sections. | Cap the column tops. |
| 7 | P2 | roof_screen, stacks | Tiny black notches show at the tops of the screen posts and corners. These are the residue of the v001 black bars. | Small gaps at the post and panel joints. | Close the post caps. |
| 8 | P2 | front, front_corner, aerial, left_side | The roof fascia and parapet band above the top floor is about 0.35 of a floor height; the source is about 0.1 to 0.2. The intermediate slab bands are about 1.5 to 1.8 times source thickness. In the street-level front view, the heavy fascia leaves the rooftop screen reading as a low dotted strip, where the source front shows a tall framed screen. | The fascia and slab depth were over-scaled. | Thin the top fascia to about 0.15 of a floor and the slab bands to about 0.1. |
| 9 | P2 | top, aerial, stacks | The roof has 3 three-stack clusters (north, east, south); top.jpg has 4, including a west cluster. The plant ring is sparse: four plain bars and a box penthouse, with no visible duct runs or elbows like those in top.jpg. | The plant layout was simplified. | Add the west cluster of three stacks and 2 to 3 duct runs with elbows around the penthouse ring. |
| 10 | P2 | front, front_corner, architecture_close | At the south-east corner, a narrow extra bay of separately framed window boxes (thick white frames) interrupts the curtain wall. In the source, the curtain wall runs continuously to the corner column. | The exoskeleton wrap bay was modelled as a framed bay on the south face. | Run the curtain wall glazing and slab bands through to the corner column. Keep the wrap to the column and beams only. |
| 11 | P2 | architecture_close, exoskeleton, right_side | The exoskeleton members are square, chunky box sections. The source members are slender round tubes. | A primitive choice. | Use cylindrical members, or chamfered members at least for the columns and diagonals. |
| 12 | P2 | right_side, front, cantilever | The concrete base walls and service bays are nearly the same off-white as the painted steel, so the source's concrete-grey and white-steel hierarchy is weak. | The palette value for concrete is too light. | Darken the concrete to a mid warm grey from the source palette. |
| 13 | P2 | front_corner, aerial, left_side, right_side, rear, top; phone-01 board | The building fills only about 30 to 35% of the frame in the whole-envelope views, so the board comparison against the tightly framed sources is weak. In the front view the east face is more foreshortened than in front.png: the east/south projected width ratio is about 0.37 against about 0.55. The cantilever overhang reads as about 22% of the south length against about 32% in the source. | The camera distance and azimuth are slightly off. The overhang is slightly short. | Tighten the framing, rotate the front camera about 10 degrees further toward the east, and consider lengthening the overhang a little. |

## 3. Source conformance checklist

| Item | Status | View(s) used |
|---|---|---|
| Silhouette (rectangular block, west cantilever, rooftop screen box) | conforms | front, front_corner, aerial, top vs front.png / oblique.jpg / top.jpg; plan ratio about 1.22 against source about 1.2 |
| Storey count (glazed ground + 3 glazed lab floors = 4) | conforms | front, left_side, rear, right_side |
| Curtain wall and slab bands | deviates (P2: heavy top fascia and bands, grid reads as a window grid; P2: SE corner framed bay) | front, facade_close, glass_close |
| Coloured services behind glass (blue, green, yellow) | conforms (saturated and legible on south and west; faint on north, which no source shows) | front, facade_close, glass_close, left_side, interior |
| Cantilever and angled soffit (west) | conforms (the sloped wedge soffit reads correctly; overhang slightly short, P2) | front, cantilever, rear, front_corner |
| V-pilotis and recessed ground floor | V-pilotis conform (2 V's, head plates in contact with the soffit, base contact). Recessed full-height glazed lobby conforms. **Door portal deviates (P1 #3, #4)** | front, v_pilotis |
| Concrete base walls (west end, service bays) | conform in geometry (west end wall under the cantilever; east service bays with roll-up doors and a door); palette weak (P2) | cantilever, right_side, architecture_close, rear |
| Exoskeleton: columns | conform in count and rhythm (6 lines, 5 bays); square instead of round (P2) | right_side, architecture_close |
| Exoskeleton: floor beams | conform | right_side, architecture_close |
| Exoskeleton: alternating diagonals | conform (chevron or alternating diagonals in the end bays only; none at ground level) | right_side, architecture_close, front |
| Exoskeleton: louvre infill | **deviates (P1 #1: vertical blades, inset panels)** | exoskeleton, right_side, front |
| Exoskeleton: white panel infill | conforms (braced white end bays) | right_side, architecture_close |
| Exoskeleton: corner wrap | conforms in principle; the south-face wrap bay is over-framed (P2 #10) | front, front_corner |
| Roof: pale edge walkway | conforms | top, aerial, roof_screen |
| Roof: perforated screen | **deviates (P1 #2: inner faces solid, far runs read as a solid wall)** | front_corner, aerial, roof_screen, stacks |
| Roof: raised penthouse | conforms (simplified) | roof_screen, stacks, aerial |
| Roof: plant units and duct runs | deviates (P2 #9: sparse, no duct runs) | top, aerial |
| Roof: three-stack clusters | deviates (P2 #9: 3 clusters against 4 in top.jpg) | top, stacks, left_side |
| Materials hierarchy (white steel, clear glass with colour, concrete base, grey louvres) | deviates (P2: concrete too close to white; louvre orientation under P1 #1) | right_side, front, cantilever |

## 4. Camera validity

- **front**: valid. Taken from the south-east, matching front.png (south glazing at left, east exoskeleton at right). The target is unoccluded: the trees now stand west of the pilotis. The east face is more foreshortened than in the source (P2 #13).
- **front_corner and aerial**: valid. Taken from the elevated south-east, matching oblique.jpg. The building is small in frame (about 35%) but legible (P2).
- **top**: valid. A true plan with the street to the south and east; the building is small in frame (P2).
- **left_side, right_side, rear, rear_side**: valid and legible, with no clipping; small in frame (P2).
- **Detail views** (facade_close, architecture_close, glass_close, v_pilotis, exoskeleton, roof_screen, cantilever, stacks, interior, rear_north): all valid and unclipped. The cantilever tree overlaps the corner glazing but does not hide the soffit or the pilotis. The interior view is dim but legible.
- No view has its target occluded, the asset clipped, or nothing legible. **No camera P0.**

## 5. Previous-version (v001) findings: resolved in pixels?

| v001 finding | Builder's claim | Resolved? | Evidence |
|---|---|---|---|
| P0: front and front_corner looked from the south-west, with the east exoskeleton edge-on | South-east front cameras | **Resolved** | front, front_corner and aerial all show the south glazing at left and the east exoskeleton at right, as in front.png and oblique.jpg. |
| P1: east infill was a checkerboard of inset louvres with a diagonal in every bay | Louvres in the 3 middle bays; braced white end bays | **Resolved for layout**. A new P1 (#1) remains: the blades are vertical where the source blades are horizontal, and the panels are inset rather than full-bay. | right_side, architecture_close, exoskeleton |
| P1: ground-floor diagonals crossed in front of the east service doors | No ground-level bracing | **Resolved** | right_side, architecture_close: the ground bays are clear concrete with roll-up doors. |
| P1: the recessed south ground floor was a solid wall with punched windows | Six-bay full-height glazed lobby with a white door portal | **Lobby resolved; portal not**. The portal is straddled and intersected by the east V-piloti and carries a black artifact (new P1 #3, #4). | front, v_pilotis |
| P1: roof screen perforated only on its south and east runs | Perforations on all 4 runs | **Partially resolved; not resolved as seen**. All 4 outer faces are perforated, but the inner faces are solid, so the far runs still read as solid in every elevated view (P1 #2). | left_side, rear, right_side, front (outer faces); front_corner, aerial, rear_side, roof_screen, stacks (inner faces solid) |
| P1: coloured services behind the glass were faint | Larger, saturated blue, green and yellow services on the south and west | **Resolved** | front, facade_close, glass_close, left_side |
| P1: piloti heads left a wedge gap under the soffit | Head plates on the pilotis | **Resolved** | v_pilotis and front: the head plates bear flush on the soffit underside. |
| P1: black vertical bars at the roof-screen corners | Duplicate corner posts removed | **Resolved**. Only tiny black notches remain at the post tops (P2 #7). | roof_screen, stacks (zoomed) |
| P1: trees hid the V-pilotis and the entrance | Trees moved west under the cantilever | **Resolved** | front, front_corner, aerial: both V's and the lobby are unobstructed. |
