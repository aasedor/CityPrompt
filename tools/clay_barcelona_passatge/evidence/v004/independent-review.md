# Independent holistic review: passatge v004 (RLASM v6.1 architectural clay)

Reviewer basis: the three locked sources (front.png, oblique.jpg, top.jpg) and all 18 renders, each opened at full resolution, plus zoomed crops of the end wall, the south mouth and the vault. I used the four phone boards only to check layout. I did not treat builder notes, the v004 measurement list, counts or hashes as proof.

## 1. Verdict

**VISUAL_REWORK_REQUIRED**: the passage reads as the right building type, and there are no P0 defects. Two clearly visible P1 fidelity defects remain:
- The facades have 6 bays where the locked sources have about 8, so the hero view shows 3 wide, squat bays per side where the source shows 6 to 7 tall, narrow ones.
- The lower stage of the north end wall, beside the portal, is brick. The locked front shows it in cream stone.

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | front, interior, south_portal, left_side, right_side, top, facade_close vs source front, oblique, top | **Wrong bay rhythm.** The vault has 6 crested main ribs and bays along its length (right_side crop: ribs at about x=25, 195, 330, 465, 600, 735, then the north end; top shows the same spacing of about 115 px). The locked top has 8 bays: crested ribs at about y=50, 165, 300, 435, 580, 735, 900, 1065, 1250 in a 2x crop. The oblique also shows about 8 ribs from the south end arch to the north end. In the hero front the end wall fills about 30% of the frame width in both images. Between the camera and that wall, the source shows 6 to 7 bays per side; the render shows only 3 (left: shops at x=0-240, 290-415, 435-500; right: 1180-1440, 1030-1140, 965-1015). The render's bays are about 5 m and its arched openings are wide and squat, about 1.1:1 for ring height to width in facade_close. The source's bays are about 3.7 m with tall, narrow arched French windows. | The bay module was set at about 5 m (30 m / 6) and never checked against the bay count in the locked sources. | Rebuild the facade, rib and corbel module at 8 bays over the 30 m passage (about 3.75 m centres). Narrow each recessed arch to about 2.7 m (keep the 0.6 m reveals). Keep crown, springing, entablature and cornice heights. Place one main rib, corbel, lattice bracket, lantern, balcony and shopfront per bay. Keep the intermediate ribs halfway between main ribs. Re-render front, interior, facade_close, top, left_side and right_side, and count 8 bays in each. |
| 2 | P1 | front (end wall), shopfronts, floor_tiles, south_portal (far end) vs source front | **Wrong material on the lower stage of the north end wall.** Below the continuous stone impost band, the flanks on both sides of the portal piers are brick panels with coursing lines (front crop x=60-180 and 815-940 at 2x; shopfronts x=90-210). In the locked front, everything below the impost band is cream stone ashlar: the piers, the wall around the west side doorway, and the east flank. Brick starts only above the band. On the hero focal wall this reverses the stone-base / brick-upper hierarchy. | The brick material was applied to the whole end-wall slab, and only the piers, band and archivolt were overridden with stone. | Give the end-wall flanks from floor level up to the underside of the impost band the stone material, with faint ashlar joints at most. Keep brick above the band. Frame the west side doorway in the same stone. Re-render front and shopfronts. |
| 3 | P2 | front, north_portal | The west side doorway is short: its head is well below the impost band (about 55% of the lower stage). In the source the doorway rises to just under the band (about 75 to 80%). | Doorway height is too low. | Raise the doorway head to about 0.5 m below the impost band. |
| 4 | P2 | front, shopfronts | The medallions are plain stepped discs. The source medallions are framed ovals with a wreath and crest. | Simplified profile. | Add an oval frame ring and a small crest block above each medallion. |
| 5 | P2 | front_corner, pavilion_finial, south_portal | Each pavilion has two urn finials, one at each parapet corner. In the oblique each pavilion has a single urn, at the inner corner beside the end arch; the outer corner is a plain brick pier. | Finials were placed symmetrically. | Remove the outer-corner urns and keep a short brick pier there. |
| 6 | P2 | facade_close, front, shopfronts, floor_tiles | Each shopfront has a brick-coloured reveal strip around it. In the source, the timber shopfronts fill the space between the stone pilasters, and there is no brick at shop level. | The brick material bleeds into the shop-zone reveals. | Give the reveals the timber or stone material. |
| 7 | P2 | front, shopfronts, facade_close | The awnings are thin, almost flat slabs. In the source they are sloped canvas awnings with a valance. | Simplified geometry. | Increase the pitch to about 25 to 30 degrees and add a 0.25 m valance. |
| 8 | P2 | facade_close, architecture_close, glass_close | The lattice brackets are narrow ladder struts with a ring. In the source each bracket is a broad openwork triangular spandrel running from the cornice down to the corbel. Balconies are rectangular; in the source they are slightly bowed. | Lighter detail level. | Widen the bracket into a spandrel panel with scroll or ring infill. Add a slight bow to the balcony fronts. |
| 9 | P2 | front, glass_close | Above the end-wall cornice the north lunette reads as a tall triangular gable. In the source front it reads as a lower, segmental glazed screen under the last rib. The vault's overall rise matches the south end arch in the oblique. | The lunette is cut to the full pointed section. | Lower the lunette's visible head, or add a transverse member below the crown so the screen reads segmental. |
| 10 | P2 | top, roof_vault, rear | From above, the glazing reads as one smooth barrel. In the top and oblique sources it is faceted: steeper lower panels, with the glazing dipping between crested ribs. | Single-curvature glazing surface. | Add a longitudinal break line on each side of the vault, at about one third of the rise. |

P0 count: 0. P1 count: 2. P2 count: 8.

## 3. Source conformance checklist

| item | status | view used |
|---|---|---|
| **Plan**: straight passage through the block | conforms | top, aerial |
| Vault right of centre in the top view, running up the frame | conforms | top (vault x=605-865 inside a block spanning about x=245-1000) |
| Tiled square at the south mouth | conforms | top, front_corner |
| Streets on both sides and to the north | conforms (straightened; the converging street geometry is not modelled, which is allowed) | top, rear, left_side |
| **Passage facades**: red-orange brick with cream stone pilasters | conforms | facade_close |
| Plinth and belt courses | conforms | facade_close, shopfronts |
| Timber shopfronts with plate glass, transoms and bulkheads | conforms (panelled bulkhead is shallow) | facade_close, shopfronts |
| Dark green signboards with gilt bands | conforms | facade_close |
| Stone shop cornice band (entablature) | conforms | facade_close, shopfronts |
| One tier of deep recessed round brick arches above the shop cornice | conforms in tier count; deviates in bay count and arch proportion (finding 1) | facade_close, front |
| French windows with fanlights | conforms | architecture_close |
| Arch rings, archivolts and keystones | conforms (brick arch ring) | architecture_close |
| Iron balconies | conforms (rectangular rather than bowed, P2) | facade_close |
| Modillion cornice | conforms | architecture_close |
| Wall lanterns on the pilasters | conforms | facade_close |
| Awnings over three shops | conforms in count (two on the east near the portal, one on the west); shape deviates (P2) | front, shopfronts, floor_tiles |
| **Glass vault**: pointed section | conforms | glass_close, front |
| Main ribs | conforms in form; deviates in count (6 against about 8) | right_side, top |
| Rib legs, corbels and lattice brackets | conforms in topology; brackets simplified (P2) | architecture_close, facade_close |
| Intermediate ribs | conforms | glass_close |
| Glazing bars | conforms | glass_close |
| Purlins | conforms | glass_close |
| Crests on the ribs | conforms | roof_vault, right_side |
| Ridge cap and cresting | conforms | rear, roof_vault |
| Gutters | conforms (a gutter box is legible at the vault foot by the pavilion) | pavilion_finial |
| **North end wall**: great round-arched portal | conforms | front |
| Stone archivolt, keystone, imposts and continuous impost band | conforms | front crop |
| Piers on bases | conforms | front |
| Two medallions | conforms in placement; simplified (P2) | front |
| Cornice | conforms | front |
| Glazed lunette with radial bars | conforms (taller than the source, P2) | front, glass_close |
| Side doorway | conforms in position; short (P2) | front |
| Lower-stage stone | deviates: it is brick (finding 2) | front |
| Street beyond the portal, with cream apartment blocks and two trees | conforms | front, interior, north_portal |
| **South mouth**: two two-storey pavilions (stone shop storey, then a brick storey with one window and a balcony) | conforms | south_portal, front_corner |
| Pavilion stone quoins, cornices and parapets | conforms | pavilion_finial |
| Pavilion urn finials | deviates: four urns where the source shows two (P2) | front_corner |
| Ornamental iron end arch with an inner arch, rings and radial bars | conforms | south_portal, pavilion_finial |
| **Floor**: pale tile | conforms | floor_tiles |
| Grey diamond lattice | conforms | floor_tiles |
| Border band | conforms | floor_tiles |
| Diamond paving on the square | conforms | front_corner |
| **Furniture**: two back-to-back bench pairs on the axis | conforms | front, floor_tiles |
| Cafe tables and chairs near the portal | conforms | front, shopfronts |
| Planters flanking the portal | conforms | front |
| Two lamp posts on the square | conforms | front_corner, top |
| **Roofs**: terracotta decks | conforms | aerial, rear |
| Stone balustrade along the vault on the west deck | conforms | roof_vault, pavilion_finial |
| Narrow east brick strip with a parapet on the east street | conforms | right_side, rear |
| White rooftop rooms and pergola on the west deck | conforms | rear, pavilion_finial |
| **Context blocks**: cream five- and six-storey blocks with balconies and terracotta decks on the west, east and north | conforms (simplified massing, acceptable for context) | aerial, front_corner, rear_side |
| **Materials hierarchy**: stone base and pilasters, brick upper walls, timber shopfronts, green iron | mostly conforms; deviates at the end-wall lower stage (finding 2) and in the brick reveals at shop level (P2) | front, facade_close |

## 4. Camera validity

All 18 views are valid. None has its target occluded, clipped or illegible:
- **front**, **interior**, **south_portal**, **north_portal** and **floor_tiles** frame the passage axis clearly.
- **top**, **aerial**, **front_corner**, **left_side**, **right_side**, **rear** and **rear_side** show the whole envelope and its context.
- In **pavilion_finial**, the end arch crops at the right edge, but the target (urns, parapet, cornice, quoins and the arch springing) is fully legible.
- No detail view hides its subject behind furniture or context.
