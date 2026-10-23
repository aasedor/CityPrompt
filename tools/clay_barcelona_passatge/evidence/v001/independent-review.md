# Independent holistic review: passatge v001 (RLASM v6.1 architectural clay)

Reviewer: independent, did not build. Basis: the three locked sources (`sources/front.png`, `sources/oblique.jpg`, `sources/top.jpg`), all 18 renders read at full resolution, zoomed crops of key junctions, and the four phone boards. I did not use metadata, counts, hashes or builder notes as proof.

## 1. Verdict

**VISUAL_REWORK_REQUIRED.** The plan, envelope, storeys, portal, pavilions, end arch, floor and furniture are all present and correctly placed, so there is no P0. Four P1 defects block production approval:
- The ironwork has lost its ornate lattice character (no openwork brackets, no crests).
- The upper facade bays read as generic punched windows rather than the source's bay-filling arches.
- The south mouth opens onto an unmodelled grey void.

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | front, facade_close, architecture_close, glass_close, interior, north_portal (vs source front) | Each main rib comes down the pilaster as a plain square bar. One straight diagonal strut joins it to the rib, and it lands on a plain cream box corbel. No openwork lattice spandrel bracket is visible, and neither are the hangers or the ring. In the source, each main rib carries a large pierced scroll and lattice bracket between the leg and the rib, which is the dominant interior motif. The intermediate ribs and purlins are also plain bars, where the source shows lattice girder ribs. | The bracket was built as a minimal strut primitive; the lattice infill, hanger and ring sub-parts were not authored or were dropped. | On every main rib, add a pierced lattice spandrel plate (a perimeter frame plus diagonal lattice or scroll infill, in the source palette's dark green-grey) filling the triangle between the leg, the rib and the strut. Add 2 vertical hangers and 1 ring at the strut. Give the main ribs a twin-flange lattice web, 2 to 3 times the depth of the intermediate ribs. |
| 2 | P1 | roof_vault, rear, rear_side, left_side, right_side, aerial, front_corner (vs source oblique) | Seen from outside, the main ribs are smooth single bars with only a small spike at the ridge. The source shows a tall openwork cresting standing proud of the glazing on every main rib, plus a continuous crested ridge. The ridge cap and gutters are not legible as distinct members. | The crest geometry was never instanced on the outside face of the ribs; the ridge was modelled as a plain line. | Instance a pierced crest band, about 0.4 to 0.6 m tall, along the outer edge of each main rib from springing to ridge, plus a continuous ridge cresting. Add a visible ridge cap profile and an eaves gutter box at each springing line. |
| 3 | P1 | facade_close, architecture_close, front, interior, shopfronts (vs source front) | The upper bays are two small stacked arched windows, each about 40% of the bay width, set in a flat brick field. They carry very deep, thick slab balconies (about 1 m) with plain vertical-bar rails. In the source, each bay above the signboard is a tall round-arched opening that nearly fills the bay between pilasters, set in a deep brick reveal and arch surround. Its balcony is shallow, with dense ornamental railings. The render reads as a generic stacked hotel facade, not the source arcade rhythm. | The window module was sized as a standard punched window and the balcony was given a generic slab depth. | Widen the arched openings and surrounds to about 65 to 75% of the bay. Recess the glazing about 0.3 m in brick reveals with visible returns. Reduce the balcony slabs to about 0.45 m deep and 0.12 m thick, with a moulded edge. Replace the rails with a denser pattern of balusters and scrolls. Keep the two upper floors the brief specifies. |
| 4 | P1 | interior, north_portal | Looking south out of the south mouth, the frame shows only a flat grey plane and a raw horizon line. There is no street frontage, block or skyline beyond the square, and the square ends abruptly. This sits inside a hero interior view. | No context was placed south of the square; the world bounds end at the square and street. | Add a cream stuccoed 5 to 6 storey context frontage across the street south of the square, built from the same block grammar as the east, west and north blocks, so the end arch frames a city view. |
| 5 | P2 | pavilion_finial | A black hairline gap and a small step where the pavilion cornice meets the passage-facade cornice, under the foot of the end arch. | Cornice segments are not mitred or overlapped. | Extend one segment by 2 to 5 cm, or mitre the joint. |
| 6 | P2 | pavilion_finial, front_corner, rear | The "urn" finials read as faceted pointed spires or obelisks. The source shows rounded urn or sculpture forms on pedestals. | The finial was built as a lathed cone. | Re-lathe it as a bellied urn: foot, body, neck and lid knob. |
| 7 | P2 | architecture_close, facade_close | The main-rib legs run through the projecting modillion cornice, overlapping its top surface, rather than being clearly notched or stood off. | The leg is a continuous bar through the cornice volume. | Stand the leg off the cornice face, or notch the cornice around it. |
| 8 | P2 | front, north_portal, shopfronts | The north end wall is all brick down to the ground. The source has pale stone piers and a lower stone zone flanking the portal up to the imposts. The medallions are plain discs. | Simplified wall material zoning. | Give the portal jambs and the lower wall band a stone colour up to impost height, and add a raised rim and boss to the medallions. |
| 9 | P2 | front, floor_tiles, shopfronts | The diamond lattice is coarse (cells about 2.5 to 3 m) and the cells are flat, with no inner tile subdivision. The source shows smaller diamonds with a pale tile infill. | The lattice spacing was set too large. | Reduce the lattice pitch to about 1.5 m and add a faint inner tile grid. |
| 10 | P2 | facade_close, shopfronts | The plate glass reads as milky white panels and the bulkheads are almost absent (only a sill). | Clay glass shader and a low bulkhead dimension. | Raise the bulkheads to about 0.5 m in timber colour and darken the glazing slightly. |
| 11 | P2 | shopfronts | A wall lantern sits right at the junction of two awnings and visually clips the awning end. | The lantern and awning positions are not cross-checked. | Shift the lantern up or sideways onto the pilaster face clear of the awning. |
| 12 | P2 | aerial, front_corner, rear_side, roof_vault | The context blocks are blank extruded boxes with one white rooftop cube each. On the east and north blocks the balcony slabs cross the windows near mid-height. | Generic context generator. | Put the balcony slabs at the window sills, and add a few rooftop rooms and parapets to the decks. |
| 13 | P2 | top, front_corner | The square spans the full block width, while the source top view keeps it near the passage and pavilion width. The top camera crops off the north street and block that the source top view shows. | Square footprint set to the block width; top camera framed too tightly. | Narrow the square toward the pavilion faces, and widen or shift the top camera to include the north street. |

Counts: **P0 = 0, P1 = 4, P2 = 9.**

## 3. Source conformance checklist

| Item | Status | View used |
|---|---|---|
| **Plan**: straight N–S passage through the block | conforms | top, left_side, right_side |
| Plan: vault right of the block's centre in the top view | conforms (west deck wide, east strip narrow) | top vs source top |
| Plan: tiled square at the south mouth | conforms (but wider than the source, P2 #13) | top, front_corner |
| Plan: streets either side and to the north | conforms (west, east and north streets; the converging street geometry is not modelled, as permitted) | top, rear, aerial |
| **Passage facades**: red-orange brick with cream stone pilasters | conforms | facade_close |
| Plinth and belt courses | conforms | facade_close, architecture_close |
| Shopfronts: timber, plate glass, transoms | conforms; bulkheads minimal (P2 #10) | facade_close, shopfronts |
| Dark green signboards with gilt band, under a stone shop cornice band | conforms | facade_close, shopfronts |
| Round-arched French windows with fanlights on the first and second floors | deviates: too small, flat reveals (P1 #3) | facade_close, architecture_close vs source front |
| Archivolts and keystones | partly conforms (archivolts present; keystones legible only on the first-floor arches) | facade_close |
| Wrought-iron balconies | deviates: plain rails, overly deep slabs (P1 #3) | architecture_close |
| Modillion cornice at the vault springing | conforms | architecture_close, glass_close |
| Wall lanterns on the pilasters | conforms | facade_close, shopfronts |
| Canvas awnings over three shops | conforms (2 on one side, 1 on the other) | shopfronts, floor_tiles, front |
| **Glass vault**: pointed section | conforms | glass_close, south_portal, rear |
| Main ribs | conforms in position and count (7 ribs, 6 bays) but deviates in ornament (P1 #1, #2) | glass_close, roof_vault |
| Legs to corbels | conforms (plain) | facade_close |
| Lattice brackets (strut, hangers, ring) | deviates: strut only (P1 #1) | front, architecture_close |
| Intermediate ribs | conforms | glass_close |
| Glazing bars and purlins | conforms | glass_close, roof_vault |
| Crests | deviates: absent (P1 #2) | roof_vault, rear |
| Ridge cap | deviates: a line only (P1 #2) | rear |
| Gutters | not visible | roof_vault |
| **North end wall**: brick wall with a great round-arched portal | conforms | north_portal, front |
| Stone archivolt, keystone, imposts | conforms | north_portal |
| Two medallions | conforms (plain discs, P2 #8) | front, shopfronts |
| Cornice | conforms | front, north_portal |
| Glazed lunette with radial bars | conforms | front, glass_close, rear |
| Street beyond with cream block and two trees | conforms | front, floor_tiles |
| **South mouth**: two brick pavilions | conforms | front_corner, south_portal, pavilion_finial |
| Pavilion stone quoins, cornices, parapets | conforms | pavilion_finial, south_portal |
| Urn finials | deviates slightly: spire-like (P2 #6) | pavilion_finial |
| Ornamental iron end arch with inner arch, radial bars and rings | conforms | south_portal, front_corner |
| **Floor**: pale tile | conforms | floor_tiles |
| Grey diamond lattice | conforms (coarse, P2 #9) | floor_tiles, top |
| Border | conforms | floor_tiles, front_corner |
| **Furniture**: two pairs of back-to-back benches on the axis | conforms | front, floor_tiles |
| Cafe tables and chairs near the portal | conforms | front, shopfronts |
| Planters flanking the portal | conforms | front, floor_tiles |
| Two lamp posts on the square | conforms | front_corner, top |
| **Roofs**: west terracotta deck | conforms | left_side, top |
| Stone balustrade along the vault | conforms | roof_vault, left_side |
| White rooftop rooms | conforms | left_side, right_side |
| Pergola | conforms | top, left_side |
| East range: narrow brick strip with parapet | conforms | right_side, aerial |
| **Context blocks**: cream stuccoed blocks with balconies and terracotta decks on the W, E and N streets | conforms in massing; deviates in detail (P2 #12) | aerial, front_corner |
| Context south of the square | deviates: void (P1 #4) | interior, north_portal |
| **Materials hierarchy**: brick field, cream stone dressings, dark green-grey iron, green and gilt signs, terracotta decks, cream context | conforms | all |

## 4. Camera validity

- All 18 renders are legible, the target is unoccluded, and the asset is not clipped in any way that hides the subject.
- **front**: the vault apex is cropped at the top edge, consistent with the source front. Valid.
- **interior** and **north_portal**: valid framing, but the view south through the mouth ends in an unmodelled grey void with a visible horizon. This is logged as P1 #4 for coherence, not as an invalid camera.
- **top**: crops off the north street and north context block that the source top view includes (P2 #13). The vault, square and both blocks remain fully legible.
- **pavilion_finial**, **roof_vault** and **glass_close**: valid. The targets are filled and in focus.
