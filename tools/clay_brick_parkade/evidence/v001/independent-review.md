# Independent holistic review: clay-brick-parkade v001 (RLASM v6.1 architectural clay)

Reviewer: independent; did not build the candidate. Judged only rendered pixels against the locked sources `sources/front.png`, `sources/oblique.jpg` and `sources/top.jpg`. Opened all 18 renders and all 4 phone boards at full resolution. Zoomed nearest-neighbour crops are in `/tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/parkade-v001-review-crops/`; no candidate file was changed.

## 1. Verdict

**VISUAL_REWORK_REQUIRED**: the envelope, level count, footprint, tower placement and roof programme match the sources and there are no P0 defects, but six P1 defects remain. They are black voids in the roof slab and at every tower-frame node, a pale greige tower frame where the sources show dark bronze, a missing patinated crown panel, an unclosed crown coping corner, and a uniform south-face bay rhythm that leaves out the source's glazed bays.

Counts: P0 = 0, P1 = 6, P2 = 9

## 2. Findings

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | roof_deck, stair_penthouse, aerial, front_corner, top, tower_crown, rear_side | About 20 flat, pure-black squares (RGB about 0,0,0, with no depth or interior shading) sit in a regular grid across the roof deck. Up close they read as holes punched in the slab. The source top shows a continuous slab with no marks at all. | Column or drain cut-outs in the roof slab, either with no column cap or drain body filling them, or carrying an unlit or black material. | Cap every column at the slab soffit and remove the cut-outs. If drains are intended, model them as small recessed grates finished in a mid-grey clay colour no bigger than about 0.3 m. Re-render roof_deck, stair_penthouse and top and confirm the slab is continuous. |
| 2 | P1 | architecture_close, glass_close, tower_crown, front (visible as dots), front_corner | Every crossing of a mullion and a transom on both towers' bronze frames shows a pure-black square void: the vertical member stops above and below, the horizontal member stops left and right, and nothing fills the node. See the crop `tower_node.png`. | The frame members are generated as segments clipped between nodes, with no node block, or the node block has a missing or black material. | Run the verticals continuously through the transoms, or add a node block in the frame material at every crossing. Confirm there is no black pixel at the nodes in architecture_close and glass_close. |
| 3 | P1 | front_corner, aerial, architecture_close, tower_crown, board phone-01 | The tower frame, transoms and louvres render as a light greige-taupe: lit at about (122,110,97), close in value to the pale precast strips. In both sources the tower is a dark bronze mass, with frames at about (74,62,50) in shade and warm bronze in sun, carrying pale precast strips. The render tower reads pale and washed out next to the brick, which reverses the source's dark-tower-against-brick hierarchy. | The bronze palette value is set too high and too desaturated, and the louvres share that material. | Darken and warm the bronze to source value: a base around RGB 70-80 / 55-62 / 42-50 in diffuse light, keeping some warmth. Apply it to the frame, louvres, first-deck band and crown louvres. Keep the precast strips pale so the strip contrast is restored. Check front_corner against oblique.jpg. |
| 4 | P1 | tower_crown, front_corner, front, right_side | The SE tower crown is uniform bronze louvres on every face. Both the front source (upper east face of the crown) and the oblique source (east face of the crown, beside the louvres) show a distinct patinated copper-green panel occupying about the outer third of the crown's east face, a prominent accent in both views. | The crown is built as one louvre ring with no panel variant. | On the crown's east face, replace the outer louvre bay (the bay next to the precast strip below it) with a flat patinated panel in the coping's verdigris family, darker and more saturated than the coping, for the full crown height. |
| 5 | P1 | tower_crown (crop `crown_coping.png`) | The patinated coping of the SE tower does not close at its south-east corner. The south run stops short and the east run starts at a slightly different line, leaving a visible notch or step where the two meet over the corner post. | The coping is built as four separate boxes per face with no mitre or overlap. | Build the coping as one closed ring: a single solid offset from the tower outline, or mitred pieces with matching top and outer faces. Check all four corners on both towers. |
| 6 | P1 | front, front_corner, aerial (against sources front and oblique) | The south face is five identical open-deck bays repeated on every deck. Both sources show a mixed south face. There is a full-height glazed curtain-wall bay (three decks of glass) directly west of the corner tower. There is a closed bay of ribbon glazing over pale spandrels next to the west glazed stair. The first deck reads more solid than the others, as a brick spandrel with a lower dark slot. Only the middle bays are open decks. | The south-face generator applies one open-deck bay type uniformly. | Assign bay types along the south face from west to east: west stair, ribbon-glazed bay, open-deck bays, glazed curtain bay, corner tower. Give the first deck a deeper brick spandrel. Match the bay widths to front.png and oblique.jpg. |
| 7 | P2 | front, board phone-01 | Front is an axial south elevation that frames the asset at about 40% of the width and 22% of the height. The source front is a street-level perspective onto the SE corner, and no render reproduces that eye-level corner view. The camera is valid but a weak match for its role. | Camera preset. | Add, or change front to, a street-level perspective onto the SE corner that matches front.png, with the asset filling at least 60% of the width. |
| 8 | P2 | facade_close, north_lane, vehicle_entry | Each deck opening has only two thin dark rails. The sources read as denser dark horizontal screens filling the lower part of each opening. | Low screen density. | Use 4-6 rails or a perforated band with a darker fill. |
| 9 | P2 | facade_close, front | The brick piers are flush with the spandrel plane. In the sources the piers stand proud of the spandrels. | No pier projection. | Project the piers about 0.15-0.2 m. |
| 10 | P2 | front, facade_close, board phone-01 | The brick is a desaturated salmon or pink. The source brick is a deeper orange-red-brown. | Palette value. | Shift the brick colour toward source mid-tone, about (150,85,60). |
| 11 | P2 | stair_penthouse | The stair flights in the open stair well are smooth inclined slabs with no treads. The source top shows switchback treads. | Simplified stair. | Step the flights. |
| 12 | P2 | top, roof_deck | The overrun, rooftop units and stair well are spread along a row with gaps between them. In the source they form one compact central strip, and the overrun roof is ribbed (the render's roof is flat). | Placement spacing. | Close up the strip and rib the overrun roof. |
| 13 | P2 | aerial, rear, rear_side | The penthouse behind the west glazed stair is a brick box. In the source oblique it is a dark box. | Material assignment. | Use the dark metal or overrun material. |
| 14 | P2 | right_side, vehicle_entry | The sidewalk and curb run unbroken past both vehicle openings on the east street, with no apron or curb cut. | The site generator ignores entries. | Add a driveway apron at each vehicle opening. |
| 15 | P2 | interior, left_side | No inter-deck ramp is clearly legible in the interior view. The only hint is a sloped element glimpsed through the west openings. | The camera does not frame the ramp. | Frame the ramp in interior, or make it legible through the openings. |

## 3. Source conformance checklist

| Item | Status | View(s) used |
|---|---|---|
| Silhouette (rectangular block, two corner towers on the east edge projecting past the north, east and south lines, west glazed stair) | conforms | top vs top.jpg (block ratio about 1.34 vs 1.33; towers project correctly), aerial, front_corner vs oblique.jpg |
| Level count (glazed ground storey plus 4 parking decks, roof deck) | conforms | front, left_side, right_side vs front.png and oblique.jpg |
| Bay rhythm and piers | deviates: the south face is uniform open decks, missing the glazed curtain bay and ribbon-glazed bay (F6), and the piers are flush (F9). The east face's 3 bays between the towers is plausible. | front, front_corner, right_side vs front.png and oblique.jpg |
| Spandrels: brick on the south face, precast on the east face | conforms (brick south, pale precast east; the pale lintel band on the south openings matches the source) | facade_close, right_side, front_corner |
| Screens in deck openings | conforms in kind, but sparse (F8) | facade_close, north_lane |
| Retail base (glazed bays in brick, pale plinth) | conforms | retail_base, front, right_side |
| Corner tower: strips (precast at the outer edges, glass and louvre toward the corner) | conforms | architecture_close, front_corner vs front.png and oblique.jpg |
| Corner tower: bronze band at the first deck, wrapping onto both facades | conforms in geometry, deviates in colour (F3) | front_corner, front, architecture_close |
| Corner tower: louvred crown above the parapet (about 1.2-1.3 storeys) | conforms in geometry. Deviates: the patinated panel is missing (F4) and the frame colour is wrong (F3) | tower_crown, right_side, front |
| Corner tower: patinated coping | present, but the corner is not closed (F5) | tower_crown |
| Frame finish | deviates: black node voids (F2) | architecture_close, glass_close |
| North-east tower (larger, same grammar) | conforms (larger footprint, same strips, louvred crown, patina coping) | right_side, rear_side, top vs top.jpg |
| West narrow glazed stair at the west end of the south face, rising slightly above the parapet | conforms (penthouse material is P2, F13) | front, left_side, aerial |
| Roof deck: stall stripes | conforms | top, roof_deck |
| Roof deck: light poles | conforms (6 poles, grounded on bases) | roof_deck, aerial |
| Roof deck: dark ribbed lift overrun | conforms (ribbed sides; the top is flat, P2) | roof_deck, top |
| Roof deck: rooftop units | conforms | roof_deck, stair_penthouse |
| Roof deck: open stair well with guard rail | conforms (treads simplified, P2) | stair_penthouse, top |
| Roof slab integrity | deviates: black voids (F1) | roof_deck, top, aerial |
| Vehicle entry and exit on the east street | conforms (two dark ground openings with a bronze header and gate arms in the east face) | right_side, vehicle_entry |
| Materials hierarchy (dark bronze tower set against red brick frame, pale precast and glass) | deviates: the tower reads pale greige, which reverses the hierarchy (F3), and the brick is light (F10) | front_corner, aerial vs oblique.jpg and board phone-01 |
| North and west faces (in no source; checked for coherence only) | coherent (brick frame with pale spandrels on the north face, solid brick ground storey with windows on the west face) | rear, left_side, north_lane |

## 4. Camera validity

- No view has an occluded target, a clipped asset, or nothing legible. All 18 views are valid.
- front: valid but weak. It is an axial elevation at about 40% frame width, which does not match the source front's street-level corner perspective (P2, F7).
- left_side, right_side and rear: valid. The asset is small, at about 35-45% of the frame width, but every element is legible.
- retail_base: valid. A street tree trunk crosses the centre of the frame but does not hide the storefront grammar.
- interior and vehicle_entry: valid. The interiors are dark but the columns and gate arms are legible.
