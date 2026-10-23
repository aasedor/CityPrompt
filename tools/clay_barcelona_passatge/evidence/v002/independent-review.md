# Independent holistic review: passatge v002 (RLASM v6.1 architectural clay)

Reviewer: independent. Evidence used: the rendered pixels in `renders/*.png` (all 18 opened at full resolution, with zoomed crops of the facade bays, leg brackets, cornice crossings, end arch, benches and context), compared against `sources/front.png`, `sources/oblique.jpg` and `sources/top.jpg`. The phone boards were checked only to confirm they show the same renders. I did not use any builder notes, counts or hashes as proof.

## 1. Verdict

**VISUAL_REWORK_REQUIRED.** The plan, vault, ironwork, portal, floor, furniture and roofs now conform, but two clearly visible fidelity defects remain. The upper-storey windows do not match the source's tall round-arched French windows. The south iron end arch reads as an ordinary vault rib instead of the source's deep ornamental arch.

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | facade_close, architecture_close, front, interior, south_portal | Each tall arched recess holds a **square-headed** first-floor window with no fanlight, and a second-floor "French window" that is only a squat lunette. In facade_close the lunette is about 95 px (about 1.4 m at about 69 px/m, from the 5 m bay) from the balcony slab to the crown. A 1.0 m railing covers it up to the arch springing, so the balcony serves an opening too short to step through. No bay shows the source's tall round-arched French window with a fanlight above a balcony. The upper zone reads as one window plus a half-moon light, not two storeys of arched French windows. | The recess was split into two storeys with the second-floor slab and balcony set at the impost line. The cornice and vault springing were not raised to give that storey a door-height window. | Raise the cornice and vault springing by about 0.8 to 1.0 m, or shorten the first-floor window by the same amount. The second-floor French window then gets at least 2.1 m of glass below its arch crown, with the balcony at its sill. Give the first-floor French windows a round-arched head with a fanlight transom, so both floors carry an arched French window with a fanlight, as the brief and source require. Keep the existing archivolt, imposts, keystone and 0.3 m reveals. |
| 2 | P1 | front_corner (matched to oblique), aerial, south_portal, pavilion_finial | The ornamental south end arch is drawn as the last pointed lattice rib, the same weight as the interior main ribs. It has a short band of five rings only near the apex and small scrolls at the springing. In front_corner and aerial it does not read as a distinct object. The source oblique's end arch is a deep openwork band with an **inner round arch** springing from the pavilion parapet corners beside the urns. Its spandrel between the inner and outer arch is filled with radial bars and rings, with a crest at the apex. In the render the inner arch is absent below the apex band, and the mouth under it is an empty pointed opening. | The end arch reuses the standard main-rib profile, with a token ring strip instead of a separate two-arch assembly. | Model the end arch as its own assembly. Make an outer pointed band about 0.8 to 1.0 m deep. Add a semicircular inner arch springing from the pavilion parapet corners, with radial bars and rings filling the spandrel between the two arches, and an apex crest. Keep it in the dark-iron palette and seat both springings on the existing pavilion cornice blocks. |
| 3 | P2 | front, glass_close, architecture_close | The leg brackets (strut, hangers, two rings) are present but light and sparse. In the source the spandrel between leg and rib is a dense openwork lattice triangle. | Low member count in the bracket. | Add a lattice fill to the bracket triangle. |
| 4 | P2 | facade_close, architecture_close | The corbels are plain cream boxes with a slot. | Placeholder primitive. | Give the corbels a moulded or scrolled profile. |
| 5 | P2 | facade_close, shopfronts | The stone shop cornice band above the signboards is thin and almost flush. The source's band is a strong projecting moulding. | Shallow projection. | Project it about 0.15 to 0.2 m with a cyma profile. |
| 6 | P2 | front, floor_tiles | The grey diamond lattice is still about 1.5 to 2 times coarser than the source's floor. | Lattice module too large. | Reduce the diamond module. |
| 7 | P2 | top, front_corner | The tiled square is about 2.1 times the vault width and runs past the east strip into the east-street sidewalk. In the top source it is about 1 to 1.6 times the vault width and stops at the east strip. | Square extent. | Trim the east edge to the line of the east strip. |
| 8 | P2 | top | The east range strip is about 2.9 m wide in plan, against about 1.4 m in the top source. | Strip width. | Narrow the strip. |
| 9 | P2 | front_corner, south_portal, pavilion_finial | The pavilions' south faces have round-arched windows. The source pavilions show tall rectangular windows with ornamented heads and a small balcony. | Window type reused from the passage facades. | Use rectangular openings with a decorated head. |
| 10 | P2 | front | The inner face of the north end wall beside the portal piers is plain brick. The source shows a pale stone base and side openings. | Simplification. | Add a stone plinth band. |
| 11 | P2 | aerial, front_corner, roof_vault | Context blocks have blank street-facing end faces (south and east blocks in aerial). Their balcony rails are single floating bars, and some blocks show 6 to 7 storeys against the source's 5 to 6. | Context simplification. | Add window grids to the exposed end faces and a second rail bar to the balconies. |
| 12 | P2 | facade_close | The brick is indicated by short tick marks only at the edges of the brick panels, which read as stray marks. | Coursing applied at edges only. | Run the coursing across the panel, or remove it. |

## 3. Source conformance checklist

| Item | Status | View used |
|---|---|---|
| **Plan:** straight north-south passage through the block | conforms | top, rear |
| Plan: vault right of centre in the top view | conforms (west block about 305 px, vault about 270 px, east strip about 70 px) | top vs top.jpg |
| Plan: tiled square at the south mouth | conforms (oversized; P2 #7) | top, front_corner |
| Plan: streets on both sides and to the north | conforms | top, left_side, right_side, rear |
| **Passage facades:** brick with stone pilasters | conforms | facade_close |
| Facades: timber shopfronts with plate glass, bulkheads, transoms | conforms (low bulkheads) | shopfronts |
| Facades: green signboards with gilt bands | conforms | facade_close, shopfronts |
| Facades: stone shop cornice band | deviates (thin, nearly flush; P2 #5) | facade_close |
| Facades: arched first- and second-floor windows with fanlights | **deviates (P1 #1)**: first floor square-headed, second floor squat lunette | facade_close, architecture_close |
| Facades: archivolts, imposts, keystones | conforms | architecture_close |
| Facades: iron balconies | conforms (second-floor balcony implausible against its window; P1 #1) | facade_close |
| Facades: plinth and belt courses | conforms (plinth, shop band and sill band) | facade_close |
| Facades: modillion cornice | conforms | architecture_close, glass_close |
| Facades: wall lanterns | conforms | shopfronts, front |
| Facades: awnings over three shops | conforms (two east, one west) | floor_tiles, shopfronts |
| **Glass vault:** pointed section | conforms | south_portal, front, glass_close |
| Vault: main ribs as lattice girders | conforms | glass_close |
| Vault: legs and corbels | conforms (plain corbels; P2 #4) | facade_close, ac crops |
| Vault: lattice brackets (strut, hangers, ring) | conforms (light; P2 #3) | front, glass_close |
| Vault: intermediate ribs | conforms | glass_close |
| Vault: glazing bars and purlins | conforms | glass_close, roof_vault |
| Vault: crests and ridge cresting | conforms | roof_vault, south_portal |
| Vault: ridge cap | conforms | rear, south_portal |
| Vault: gutters | conforms (gutter box at the springing) | pavilion_finial, architecture_close |
| Vault: legs at the cornice | conforms: the strut passes clear in front of the cornice, and the lattice leg stops under the cornice and resumes above it, with no visible intersection | architecture_close (zoomed) |
| **North end wall:** brick wall with great round-arched portal | conforms | front, north_portal |
| North end: stone archivolt, keystone, imposts | conforms | front, north_portal |
| North end: stone portal piers | conforms | front |
| North end: two medallions | conforms | front, shopfronts |
| North end: cornice | conforms | front |
| North end: glazed lunette with radial bars | conforms | front |
| North end: the street beyond (cream block, two trees) | conforms | front, floor_tiles |
| **South mouth:** two brick pavilions | conforms | south_portal, front_corner |
| South mouth: stone quoins | conforms | south_portal |
| South mouth: cornices and parapets | conforms (mitred corners) | pavilion_finial |
| South mouth: urn finials | conforms | pavilion_finial |
| South mouth: ornamental end arch (inner arch, radial bars, rings) | **deviates (P1 #2)** | front_corner, south_portal, pavilion_finial |
| **Floor:** pale tile | conforms | floor_tiles |
| Floor: grey diamond lattice | conforms (coarse; P2 #6) | floor_tiles |
| Floor: border | conforms | floor_tiles, facade_close |
| **Furniture:** two pairs of back-to-back benches on the axis | conforms (checked: parallel to the axis, converging to the vanishing point) | front, floor_tiles |
| Furniture: cafe tables and chairs near the portal | conforms | front, shopfronts |
| Furniture: planters flanking the portal | conforms | front, floor_tiles |
| Furniture: two lamp posts on the square | conforms | front_corner, top |
| **Roofs:** terracotta deck on the west block | conforms | left_side, rear |
| Roofs: stone balustrade along the vault | conforms | roof_vault, pavilion_finial |
| Roofs: east parapet along the vault | conforms (strip too wide; P2 #8) | right_side, aerial |
| Roofs: white rooftop rooms | conforms | rear, rear_side |
| Roofs: pergola | conforms | left_side, rear_side |
| **Context blocks:** cream stuccoed blocks with balconies and terracotta decks on the west, east and north streets, plus the block south of the square | conforms (simplified; P2 #11) | aerial, front_corner, rear |
| **Materials hierarchy:** red-orange brick, cream stone, dark green iron, timber shopfronts, green and gilt signboards, pale tile, terracotta decks | conforms | all views |

## 4. Camera validity

All 18 views are valid. None has its target occluded, the asset clipped or the subject illegible.
- front, front_corner, aerial, top, left_side, right_side, rear and rear_side frame the whole envelope with the passage, square and streets readable.
- top shows the north street, as the widened camera intends.
- Detail views show their targets in full: facade_close, architecture_close, glass_close, interior, roof_vault, south_portal, north_portal, shopfronts, floor_tiles and pavilion_finial.
- pavilion_finial looks under the open south end of the vault into the passage. This is consistent with the source, where the passage is open under the end arch, and is not a missing-glass defect.

Counts: **P0 = 0, P1 = 2, P2 = 10.**
