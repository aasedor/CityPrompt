# Independent holistic review: passatge v006 (RLASM v6.1 architectural clay)

Reviewer: independent; did not build the candidate. Evidence is rendered pixels only. I opened the three locked sources (front.png, oblique.jpg, top.jpg) and all 18 renders at full resolution, plus all four phone boards. I also made enlarged crops of the source front (both facades, the north portal), the source oblique (vault and south mouth) and the renders (front end wall, south arch foot, pavilion arch foot, interior end arch, rear portal, roof crests). The builder's notes, counts and hashes were not used as proof.

## 1. Verdict

**PASS_ZERO_P0_P1**: The renders read as the locked Barcelona covered passage. The plan has the vault right of centre, the tiled square at the south mouth and streets on three sides. The passage facades have stone shop pilasters with brick arch-tier piers, the pointed glass vault sits on iron ribs that land on corbels, and the arched brick north portal and the iron end arch between brick pavilions are both present. All openings have depth and every part makes contact. The remaining deviations are polish only.

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| — | P0 | — | None found. | — | — |
| — | P1 | — | None found. The v005 P1 is resolved. In facade_close and architecture_close the paneled cream pilasters stop under the shop entablature, and the piers through the arch tier are brick up to the modillion cornice. The source front crops (both facades) show the same: brick piers and brick arch rings above the stone shop storey. | — | — |
| 1 | P2 | front, interior, architecture_close, glass_close | The springing brackets read as a thin ladder strut plus a ring and hanger. In the source they are large spandrel panels filled with dense openwork scrollwork, the visually heaviest iron element. | Bracket modelled as a strut, ring and hanger, with no filled spandrel panel. | Add a triangular openwork panel (scroll or lattice infill) between each main rib leg and its rib, from the cornice down to the corbel. |
| 2 | P2 | roof_vault, front_corner, south_portal | The outside crests are sparse thin zigzag or X fins on the ribs and ridge. The source oblique shows continuous dark lattice crest bands over every main rib and along the ridge. | Crest geometry is too sparse and too thin. | Denser crest bands (closer pickets plus a scroll or ring infill), a little taller, on the main ribs and the ridge. |
| 3 | P2 | glass_close, front, interior | Each rib's upper half is close to a straight line from haunch to ridge, so the section reads slightly as a gable with curved eaves. The source vault is a smooth two-centred pointed arch. | Rib profile built from a curved haunch plus a straight rafter. | Resample the rib and glazing profile as a two-centred arc so the curvature continues to the apex. |
| 4 | P2 | front, shopfronts, floor_tiles | The two north-wall medallions render as round flat concentric discs with a small tab. The source has oval cartouches with a portrait relief and a carved frame. | Disc primitive. | Scale them to a vertical oval, add a raised frame lip and a low central relief boss. |
| 5 | P2 | rear, north_portal, front | The glazed lunette is an inclined, hipped fan of radial bars. Seen from above (rear) it reads as a sloped facet. The source front shows a vertical glazed tympanum above the end-wall cornice. From inside it still reads correctly as a glazed lunette with radial bars. | End glazing modelled as a hip instead of a vertical plane. | Make the lunette a vertical plane on the end-wall cornice under the last rib, keeping the radial bars and the dark outer end frame. |
| 6 | P2 | top, front_corner | In plan the east range strip is about 29% of the vault's width. In source top it is a thin parapet strip of roughly 6–10%. The vault is still right of centre and the strip reads as a narrow parapeted range. | East range given a roof-trough width. | Narrow the east strip toward the source proportion, or leave it as context. |
| 7 | P2 | front, facade_close, shopfronts | The arch-tier balconies have thick, deep cream slabs and simple diagonal-lattice rails. Source balconies are shallow, with ornate scroll and roundel railings. | Slab depth and thickness overscaled; rail pattern simplified. | Thin and shallow the slabs by about 30–40%, and add a roundel or scroll band to the railing panels. |
| 8 | P2 | glass_close, facade_close | There is no longitudinal openwork lattice frieze along the vault springing. The source front shows a lattice band at the eaves between the rib brackets. | Purlin at the springing modelled as a plain bar. | Replace the lowest purlin each side with a shallow openwork lattice girder. |
| 9 | P2 | facade_close, front, roof_vault | The lighter intermediate ribs are hard to tell apart from the transverse glazing bars. The source front shows distinct secondary arches between the bracketed main ribs. | Intermediate rib section too close to the glazing-bar section. | Give the intermediate ribs a section about 1.5–2× the glazing bar and a small crest, so they read as a second rib order. |
| 10 | P2 | rear, floor_tiles | Small X glyph marks show on the outer north archivolt (rear). The passage-floor lattice uses single grey bands where the source has paired lines. | Stray decal or voussoir marker; simplified tile bands. | Remove the X marks; optionally split the lattice bands into paired lines. |

## 3. Source conformance checklist

| Item | Status | View used |
|---|---|---|
| **Plan**: straight N–S passage through the block | conforms | top, left_side, right_side |
| Vault right of centre in the top view | conforms (vault centre about 51% across the frame vs about 51% in source) | top vs source top |
| Square at the south mouth | conforms | top, front_corner, aerial |
| Streets either side and to the north | conforms | top, rear, aerial |
| **Passage facades**: brick walls with cream stone pilasters (shop storey) and brick piers above | conforms | facade_close, architecture_close vs source front crops |
| Timber shopfronts, plate glass, bulkheads, transoms | conforms | shopfronts, facade_close |
| Dark green signboards with gilt name bands | conforms | facade_close, shopfronts |
| Stone shop cornice band | conforms | facade_close |
| Arched French windows with fanlights, one tall tier, one per bay | conforms (one tier, about 8 bays, matches source front/top) | facade_close, architecture_close, left_side |
| Archivolts and keystones (arch-tier rings) | conforms (deep stepped brick rings as in source; stone archivolt and keystone at the portal) | architecture_close, front |
| Iron balconies | conforms; slab depth and rail pattern deviate (P2 #7) | facade_close |
| Belts | conforms | facade_close |
| Modillion cornice | conforms | facade_close, architecture_close |
| Wall lanterns on pilasters | conforms | facade_close, shopfronts |
| Awnings over three shops | conforms | facade_close, shopfronts, floor_tiles |
| **Glass vault**: pointed section | conforms; upper curvature flattened (P2 #3) | glass_close, interior |
| Main ribs | conforms | glass_close, roof_vault |
| Legs, corbels and lattice brackets | conforms with simplification (P2 #1); legs land on stone corbels | architecture_close, front |
| Intermediate ribs | deviates (weakly differentiated, P2 #9) | facade_close, roof_vault |
| Glazing bars | conforms | glass_close |
| Purlins | conforms; eaves lattice frieze missing (P2 #8) | glass_close |
| Crests | conforms, sparse (P2 #2) | roof_vault |
| Ridge cap | conforms | roof_vault, rear |
| Gutters | conforms | pavilion_finial, roof_vault |
| **North end wall**: great round-arched portal | conforms | front, north_portal |
| Stone archivolt, keystone, imposts | conforms | front crop, north_portal |
| Two medallions | conforms in count and placement; shape deviates (P2 #4) | front crop |
| Cornice | conforms | front crop |
| Glazed lunette with radial bars | conforms from inside; inclined rather than vertical (P2 #5) | front crop, rear |
| Street beyond: cream blocks and two trees | conforms | front, floor_tiles, rear |
| **South mouth**: two two-storey brick pavilions | conforms | south_portal, pavilion_finial |
| Quoins, cornices, parapets | conforms | south_portal, pavilion_finial |
| Urn finials | conforms | pavilion_finial |
| Ornamental iron end arch (inner arch, radial bars, rings) | conforms; arch foot ties into the pavilion with a strut frame (contact OK) | south_portal, interior, pavilion_finial |
| **Floor**: pale tile | conforms | floor_tiles |
| Grey diamond lattice | conforms (single bands, P2 #10) | floor_tiles |
| Border | conforms | floor_tiles |
| Square diamond lattice (coarse over fine) | conforms | front_corner, aerial |
| **Furniture**: two pairs of back-to-back benches on the axis | conforms | front, floor_tiles |
| Cafe tables and chairs near the portal | conforms | front, shopfronts |
| Planters flanking the portal | conforms | front, floor_tiles |
| Two lamp posts on the square | conforms | front_corner, top |
| **Roofs**: west block flat terracotta deck | conforms | front_corner, rear |
| Stone balustrade along the vault | conforms | pavilion_finial, roof_vault |
| East range parapet along the vault | conforms; strip too wide in plan (P2 #6) | top, front_corner |
| White rooftop rooms | conforms | front_corner, left_side |
| Pergola | conforms | front_corner, rear, top |
| **Context blocks**: cream five- and six-storey blocks with balconies and terracotta decks, west, east and north | conforms | front_corner, aerial, rear_side |
| **Materials hierarchy**: red-orange brick field, cream stone dressings, dark green iron, glass, timber shopfronts, green and gilt signs, pale tile | conforms | facade_close, front, south_portal |

## 4. Camera validity

All 18 views are valid. None has the target occluded, the asset clipped or nothing legible.

- left_side and right_side are high oblique overviews rather than side elevations, but the passage block, vault and square are fully legible.
- architecture_close and glass_close are steep upward views that clearly show the corbels, brackets, ribs and glazing.
- pavilion_finial crops the pavilion's lower storey, but the finial, cornice, parapet and arch foot it is meant to show are in frame.
