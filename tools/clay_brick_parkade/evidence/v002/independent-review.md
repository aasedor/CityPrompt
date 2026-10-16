# Independent holistic review: clay-brick-parkade v002 (RLASM v6.1 architectural clay)

Reviewer: independent, with no relationship to the builder. Basis: pixels only. I opened the three locked sources (front.png, oblique.jpg, top.jpg), all 18 renders at full resolution and the four phone boards. I made zoomed crops into a separate scratch folder (`indep-review-parkade-v002-crops/`). I did not use metadata, counts, hashes, the builder's notes or the audit JSON as proof.

## 1. Verdict

**VISUAL_REWORK_REQUIRED.** All six v001 pixel defects are fixed or materially improved, and the identity elements are now present, but two façade-grammar defects remain at P1. The east-face decks read as pale open bays full of cars, where the source shows dark mullioned ribbon bands. The south face's open zone is three brick-pier bays, where the source shows one wide brick-framed opening.

Counts: P0 = 0, P1 = 2, P2 = 9

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | front_corner, aerial, right_side, rear_side, architecture_close (vs oblique, front sources) | East-face deck openings between the SE and NE towers read **light and open**. Each opening shows two thin grey rails, with grey/red car boxes and the far side of the deck visible through it. In the source oblique and front, the two southern east-face bays read as **dark horizontal bands with close vertical mullions** (dark ribbon glazing/screens) over pale precast spandrels, and only the north bay reads as open deck. At phone scale the east face changes from dark-banded (source) to pale and see-through (render). | The east-face openings use the same open-deck guard-rail assembly as the open bays. No dark screen or glazing infill panel exists in the opening plane. | In the two southern east-face bays on decks 1–4, set a dark (source bronze/charcoal) infill panel in the opening plane, recessed behind the brick and precast face, with vertical mullions at about 1.2–1.5 m. Keep the north bay as open deck with rails. Re-render front_corner, aerial and right_side. |
| 2 | P1 | front, front_corner, aerial, facade_close (vs front, oblique sources) | South face, between the west glazed stair and the curtain-wall bay: the open-deck zone is divided by **two extra full-height brick piers into three equal punched bays**, so the face reads as a regular brick grid. The source front and oblique show **one wide brick-framed opening**, with recessed concrete columns and pale concrete spandrel upstands spanning the zone and no intermediate brick piers. Secondary deviations in the same face: the ribbon bay has ribbon windows on all four decks with brick between them, where the source shows pale precast panels between three ribbons over a brick deck-1 band. The curtain-wall bay runs through decks 1–4, where the source shows a curtain wall on decks 2–4 over a punched deck-1 window in brick. | The bay generator still places a brick pier at every structural grid line. The v002 changes (ribbon, curtain, slot) swapped bay types but kept the uniform pier rhythm. | On the south face, delete the two intermediate brick piers in the open zone and replace them with recessed concrete columns set back at least 0.6 m. Make that zone's per-deck spandrels pale precast upstands spanning the full width inside one brick frame. In the ribbon bay, change the inter-ribbon spandrels to pale precast and make deck 1 solid brick. Stop the curtain wall at deck 2 and put a punched brick-framed window at deck 1. Re-render front and front_corner. |
| 3 | P2 | tower_crown, front_corner, right_side | The patina panel is present but **pale mint** (≈164,183,179) where the source is deep verdigris teal (≈74,123,127). It reads as a plate applied in front of the frame, overlapping the edge of the adjacent louvre strip. | Light patina albedo; panel set proud of the frame plane. | Darken the patina toward the source teal. Seat the panel flush in its frame bay, between the verticals. |
| 4 | P2 | architecture_close, glass_close | The bronze now reads dark brown (≈80,72,63), but it is still lighter and greyer than the source (≈45–70,35–56,25–47). | Bronze albedo slightly high. | Lower the bronze albedo by about 25 %. |
| 5 | P2 | architecture_close | At the SE tower corner, two separate bronze posts sit on either side of a pale vertical sliver, and the transoms on each face stop short of the corner. The source shows a single dark corner post. | Per-face frames with a precast panel edge exposed at the corner. | Add one shared bronze corner post and run the transoms into it. |
| 6 | P2 | top, stair_penthouse | From the nadir, the stair well reads as a **pure black (0,0,0) rectangle** with two pale bars. In stair_penthouse there are black wedges below the flights, and the front guard-rail corner post appears to drop into the well. | Unlit, unenclosed shaft below the roof opening. | Add shaft walls and a lit floor inside the well, and seat the corner post on the slab edge. |
| 7 | P2 | roof_deck, aerial | The lift overrun is mid-grey ribbed; the source overrun is near-black. | Albedo. | Darken it to the source charcoal. |
| 8 | P2 | facade_close | On deck 1 the grey lintel bands sit about 0.4 storey above the new slot openings, leaving a brick strip between band and opening. | The band height was kept from the full-height opening. | Drop the band onto the slot head, or delete it on deck 1. |
| 9 | P2 | interior | The car boxes interpenetrate one another along the right-hand row. | Stall spacing is shorter than the vehicle length. | Space the vehicles to stall pitch. |
| 10 | P2 | front, left_side, front_corner | The west glazed stair has only a thin grey cap. The source shows a dark solid head box above the glazing. | Simplified head. | Add a dark solid head volume about 1/3 storey tall. |
| 11 | P2 | retail_base, facade_close, front/left/right/rear elevations | Tree trunks or canopies partly cover the retail glazing and the deck-1 slots in the close-ups. Whole-envelope elevations show the building at only about 35–45 % of frame width. | Camera placement. | Shift the close-up cameras 1–2 m clear of the tree line, and tighten the elevation framing. |


## 3. Source conformance checklist

| Item | Status | View(s) used | Note |
|---|---|---|---|
| Silhouette | conforms | top, aerial, front_corner vs top/oblique | Long rectangle about 1.35:1 with the long side south. The NE tower projects past the north and east parapets and the SE tower past the south and east parapets, as in the top source. |
| Level count | conforms | front, right_side, left_side | Ground retail storey plus four decks plus parapet. Towers rise about one crown above the parapet. |
| Bay rhythm and piers | deviates | front, front_corner | South open zone has three pier-divided bays instead of one wide frame (P1 #2). East face bay count (three) matches. |
| Spandrels (brick south, precast east) and screens | deviates | facade_close, right_side, front_corner | South: brick with grey caps, thin dark rails (acceptable). East: precast spandrels conform, but the openings lack the dark screen/ribbon band (P1 #1). |
| Retail base | conforms | retail_base, front, front_corner | Bronze-mullioned glazing set in brick bays on a pale plinth. The glass is recessed and the interior has depth. |
| Corner tower: strips | conforms | architecture_close, front | Precast, glass and louvre strips on both faces. Louvres have depth, with stairs visible behind. |
| Corner tower: band | conforms | architecture_close, front_corner | Projecting bronze band at the first deck wraps both faces. |
| Corner tower: crown | conforms | tower_crown, front | Louvred crown above the parapet with a dark backing. |
| Corner tower: coping | conforms (tone P2) | tower_crown, aerial | Closed ring that is continuous at the SE corner. Pale mint tone. |
| Corner tower: patina | conforms (tone/placement P2) | tower_crown, front_corner, right_side | Panel at the north end of the east-face crown, matching the source position. |
| North-east tower | conforms | right_side, rear_side, top, roof_deck | Larger tower of the same grammar, with crown, band and a patina panel on the north face. |
| West glazed stair | conforms (head P2) | front, left_side | Narrow fully glazed stair with flights visible through the glass. The head is simplified. |
| Roof deck: stripes | conforms | top, roof_deck | Stall stripes and drive-aisle lines. |
| Roof deck: poles | conforms | roof_deck, aerial | Light poles with bases seated on the deck. |
| Roof deck: overrun | conforms (tone P2) | roof_deck, top | Ribbed overrun at the west end of the central service row, as in the top source. |
| Roof deck: units | conforms | stair_penthouse, top | Rooftop units between the overrun and the well. |
| Roof deck: stair well | conforms (optics P2) | stair_penthouse, aerial, top | Open well with a perimeter guard rail and flights. Reads black from the nadir. |
| Materials hierarchy | conforms with reservations | all | Brick frame, then precast, then bronze, then glass, then patina accent. Bronze and patina values are lighter than the source (P2 #3, #4). |
| Vehicle entry/exit on the east street | conforms | vehicle_entry, right_side, rear_side | Two dark openings with bronze canopy lintels, columns and floor visible inside. |

## 4. Camera validity

No view is invalid: in every view the target is unoccluded, the asset is unclipped and the subject is legible.
- retail_base: a tree trunk covers about 6 % of the frame at centre. The glazing stays legible (P2 #11).
- facade_close: a tree canopy covers part of the lower-left deck-1 slot (P2 #11).
- front, left_side, right_side, rear: the building fills only about 35–45 % of frame width. It is still legible and unclipped.
- interior: dark, but the columns, deck, vehicles and perimeter openings are all legible.
- top: valid nadir. The roof and both towers are fully in frame.

## 5. Previous-version (v001) findings: status in the pixels

| v001 finding | Status | Evidence |
|---|---|---|
| P1: grid of black squares across the roof slab | **Resolved** | top and aerial show a clean slab with stripes. The only black area left is the stair well opening (P2 #6), not a grid. |
| P1: black voids at every mullion/transom crossing of the tower bronze frames | **Resolved** | glass_close and architecture_close show continuous bronze crossings with no black voids. The horizontals pass in front of the verticals. |
| P1: tower bronze pale greige instead of dark bronze | **Resolved** (residual P2 #4) | The bronze samples at about 80,72,63 and reads dark brown. It is slightly lighter than the source. |
| P1: patinated copper-green panel on the south-east crown missing | **Resolved** (residual P2 #3) | tower_crown, front_corner and right_side show the patina panel at the north end of the SE crown's east face. Its tone is too pale. |
| P1: crown coping open at its south-east corner | **Resolved** | tower_crown and aerial show a closed coping ring, continuous at the SE corner. |
| P1: south face five identical open-deck bays, missing the curtain-wall bay, ribbon bay and more solid first deck | **Partially resolved; still P1 (#2)** | The curtain-wall bay next to the tower, the ribbon bay by the west stair and the deck-1 slot openings are now present (front, front_corner). The open zone is still three identical brick-pier bays instead of one wide brick-framed opening. The ribbon-bay spandrels and the curtain-wall extent also differ from the source. |
| Carrier aperture audit: louvre strip on the hidden west face of the SE tower | **Not contradicted in the pixels** | That face is hidden below the parapet in every render. Above the roof, tower_crown shows the crown's west louvres with a solid dark backing and no stray aperture. Per the method I did not use the audit JSON as proof. |
