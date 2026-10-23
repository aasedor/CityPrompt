# Independent holistic review: passatge v003 (RLASM v6.1 architectural clay)

Reviewer: independent; did not build the candidate. Evidence used: the three locked sources (front.png, oblique.jpg, top.jpg) and all 18 renders, each opened at full resolution, plus 2x/3x pixel crops of the source end wall, the source passage facades (both sides), the source south mouth, and render details (portal head, window reveals, balconies, south-arch feet and legs, shopfront and awning, belt zone). Phone boards were checked for presentation only. Builder notes, counts and metadata were not used as proof.

## 1. Verdict

**VISUAL_REWORK_REQUIRED**: v003 has no P0, but it has two P1s. The locked source pixels show one tall tier of deep, recessed, round-arched brick bays above the shops, with one balcony per bay. v003 replaced this with two tiers of smaller stone-framed windows on a flat brick wall, adding a storey to the passage facades and both pavilions. Separately, the north portal is about 40% too wide for its end wall.

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | front, interior, facade_close, architecture_close, south_portal, front_corner, north_portal vs source front + oblique | **The upper facade and pavilions are one storey too tall and use the wrong bay grammar.** Render: above the shop cornice, every bay has two tiers of round-arched French windows. Each tier has a cream archivolt with a keystone and its own balcony, set on a flat brick wall. The cornice is about 12.5 m high. In the far-end bays of render front, the upper zone is about 1.07 times the height of the shop zone. Source front (crops at far left and far right): above the stone shop entablature with its signboards there is **one** tier of tall, deep round-arched **brick** recesses with brick soffits. The French window is set well back, and a single wrought-iron balcony sits at the base of the recess. The vault brackets spring from corbels at arch-springing level, directly above that single tier, and no second balcony row exists anywhere in the frame. In the source front the upper zone is about 0.6 times the shop zone, and the end-wall cornice is about 10 m (end wall roughly square on an 11 m passage). Source oblique (crop of the south mouth) confirms two storeys: each pavilion has a cream stone ground storey with shop and signboard, **one** brick upper storey with one window and a small balcony, then a cornice and a brick attic with urns. Inside the passage there is one tier of arched balconied windows. The render pavilions have three storeys (shop, then window with balcony, then window) under the cornice. | The v003 change #1 followed the brief's wording ("three storeys … first and second floors") instead of the locked pixels. The brief text and the sources conflict here, and the method makes the sources the only truth. | Rebuild the upper passage facade as one storey of tall, deeply recessed round-arched brick bays, one per pilaster bay. Each bay gets a brick arch ring with a visible brick soffit and reveal of at least 0.5 m, one tall French window with a fanlight set at the back of the recess, and one balcony on the shop cornice at the recess base. Lower the cornice and vault springing to about 10 m and re-seat the corbels and brackets at the new arch-springing level. Rebuild the pavilions as a stone ground storey plus one brick storey with a single window and balcony, then cornice, brick attic and urns. Lower the south-arch springing to match. If the owner explicitly rules that the brief text overrides the source here, record that decision. The finding then drops to P2 (archivolts and keystones in stone where the source shows brick arch rings). |
| 2 | P1 | front, north_portal, south_portal (distant) vs source front | **The north portal is too wide for its end wall.** Render front: the clear opening at the arch is about 0.70 of the end-wall width, and the archivolt's outer edge runs almost to both flanking pilasters. That leaves thin brick piers, and the two medallions are crowded into the corners next to the arch crown. Source front (end-wall crop): the clear opening is about 0.50 of the end-wall width, between full-height cream stone piers on bases. There are broad brick fields on each side with the medallions centred in them, about halfway between the impost and the crown, and a continuous stone impost entablature runs across the whole end wall in line with the shop cornice. A smaller stone-framed side doorway sits left of the portal. | The portal is sized to fill the 11 m end wall rather than to the source proportion. | Narrow the clear opening to about 50% of the end-wall width (≈5.5 m), keeping the crown just under the end-wall cornice. Make the stone piers about 1 m wide on bases, and widen the brick fields. Centre the medallions in those fields at mid-arch height. Run the impost as a continuous stone band across the end wall, aligned with the shop cornice. Optional P2: add the small side doorway in a stone surround. |
| 3 | P2 | front, facade_close, architecture_close, glass_close, interior vs source front | The lattice brackets read as a thin ladder leg, one ring and one strut. In the source, every bay has a large, dense openwork spandrel that fills the triangle between leg, rib and wall, and the brackets read as continuous dark lace. | Sparse lattice web. | Fill the leg–rib–wall triangle with a denser lattice of scrolls and rings, so each bracket reads as a solid openwork spandrel at clay scale. |
| 4 | P2 | facade_close, shopfronts | No belt course separates the two upper window tiers; only the shop cornice band exists. This becomes moot if finding 1 restores a single tier. | — | Resolve through finding 1. If two tiers are kept by ruling, add a stone belt at the second-floor sill. |
| 5 | P2 | facade_close, shopfronts | The shopfront plate glass runs almost to a thin timber sill, with no readable bulkhead panel. | Bulkhead too low. | Add a timber bulkhead of about 0.45 m with a panel below each shop window. |
| 6 | P2 | facade_close | The awning projects past the shop opening, across a third of the pilaster, and its right edge touches the wall lantern. | Awning width taken from the bay, not the opening. | Clip the awning to the shopfront opening, or drop the lantern clear of it. |
| 7 | P2 | top, aerial, front_corner | The east strip is about 0.26 of the vault width, against about 0.08–0.12 in the source top and oblique. It reads as a narrow roof channel rather than a parapet strip. The plan reading still holds. | Width not changed in v003. | Narrow the east strip to about 1–1.5 m. |
| 8 | P2 | south_portal, front_corner, pavilion_finial vs oblique | The pavilion ground storeys are brick with quoins, but the source ground storey is cream stone. This is also covered by the rebuild in finding 1. | Material assignment. | Make the pavilion ground storey cream stone. |
| 9 | P2 | south_portal, pavilion_finial, front_corner vs oblique | The south end arch reads well: outer band, rings, inner semicircle, radials, crest, finial, and legs landing on corbels. Its band is sparser than the source's dense scrolled band. | Simplification. | Thicken the band web if desired. |
| 10 | P2 | roof_vault, pavilion_finial | No vault-foot gutter can be distinguished from the cornice and balustrade top. | Gutter not modelled, or hidden. | Add a small dark gutter channel along the glass foot. |
| 11 | P2 | all | The brick reads salmon rather than the source's deeper red-orange. | Palette value. | Darken and saturate the brick slightly. |

## 3. Source conformance checklist

| item | status | view used |
|---|---|---|
| **Plan**: straight N–S passage through the block | conforms | top, left_side, right_side |
| vault right of centre in the top view | conforms (vault centre ≈0.51 of the frame width, matching the source) | top vs source top |
| tiled square at the south mouth | conforms (diamond lattice with border, two lamp posts) | top, front_corner, aerial |
| streets either side and to the north | conforms | top, rear, aerial |
| **Passage facades**: red-orange brick with cream stone pilasters and plinth | conforms (brick tone P2) | facade_close |
| shopfronts with plate glass, transoms, bulkheads | conforms / bulkhead deviates (P2) | facade_close, shopfronts |
| dark green signboards with gilt bands | conforms | facade_close, front |
| stone shop cornice band | conforms | facade_close, shopfronts |
| arched upper windows with fanlights | **deviates** (two tiers on a flat wall vs one tier of deep brick recesses; finding 1) | facade_close, architecture_close vs source front |
| archivolts and keystones | deviates (stone archivolts on every window; source bays are brick arch rings; finding 1) | architecture_close vs source front crops |
| iron balconies | deviates in count (two per bay vs one; finding 1); the railings themselves conform | facade_close |
| openings with depth and returns | conforms for the modelled 0.28 m reveals; source recess is much deeper (finding 1) | interior, front, south_portal crops |
| belt courses | deviates (P2, finding 4) | facade_close |
| modillion cornice | conforms | architecture_close, glass_close |
| wall lanterns on pilasters | conforms | facade_close, shopfronts |
| canvas awnings over three shops | conforms (awning clash P2) | front, facade_close, shopfronts |
| **Glass vault**: pointed section | conforms | glass_close, south_portal, rear |
| main ribs | conforms | glass_close, roof_vault |
| legs down the pilasters to corbels | conforms (contact OK) | architecture_close, facade_close |
| lattice brackets (strut, hangers, ring) | conforms in parts, deviates in density (P2, finding 3) | architecture_close, glass_close vs source front |
| intermediate ribs | conforms | glass_close, left_side |
| glazing bars, purlins | conforms | glass_close, roof_vault |
| crests on ribs, ridge cap and crest | conforms | roof_vault, right_side, rear |
| gutters | not visible (P2) | roof_vault |
| **North end wall**: great round-arched portal | **deviates** in proportion (finding 2) | front vs source front |
| archivolt, keystone, imposts | conforms (impost blocks only; source has a continuous impost band, finding 2) | front crop, north_portal |
| two medallions | conforms in presence, deviates in placement (finding 2) | front crop |
| cornice | conforms | front crop |
| glazed lunette with radial bars | conforms | front, glass_close |
| street beyond (cream blocks, two trees) | conforms | front, floor_tiles, rear |
| **South mouth**: two brick pavilions | **deviates** (three storeys vs two; brick ground storey vs stone; findings 1 and 8) | south_portal, front_corner vs oblique |
| quoins, cornices, parapets, urn finials | conforms | pavilion_finial, front_corner |
| ornamental iron end arch with inner arch, radial bars, rings | conforms (band density P2) | south_portal, pavilion_finial, front_corner |
| **Floor**: pale tile with grey diamond lattice and border | conforms | floor_tiles, front, interior |
| **Furniture**: two pairs of back-to-back benches on the axis | conforms | front, floor_tiles |
| cafe tables and chairs near the portal | conforms | front, shopfronts |
| planters flanking the portal | conforms | front, floor_tiles |
| two lamp posts on the square | conforms | top, front_corner, aerial |
| **Roofs**: terracotta decks | conforms | top, aerial |
| stone balustrade along the vault (west) | conforms | roof_vault, pavilion_finial |
| east parapet strip | conforms in kind, deviates in width (P2, finding 7) | top, right_side |
| white rooftop rooms, pergola | conforms | top, left_side, pavilion_finial |
| **Context blocks**: cream five-storey with balconies and terracotta decks on W, E and N | conforms | aerial, rear_side, roof_vault |
| **Materials hierarchy** (brick < stone dressings < dark green iron; timber shops; green and gilt signs; pale floor) | conforms (brick tone P2; stone archivolts where the source has brick, finding 1) | all |

## 4. Camera validity

All 18 views are valid. No target is occluded, no asset is clipped, and every view is legible. front matches the source front role (interior, looking north at the portal). front_corner and aerial match the oblique role, and top matches the top role. glass_close is a straight-up view and is legible. left_side and right_side are high near-plan views rather than true side elevations; both are legible and show the vault, decks and street. rear and rear_side show the north end wall and portal, the latter partly foreshortened but readable. north_portal, south_portal, pavilion_finial, shopfronts, floor_tiles, interior, roof_vault, architecture_close and facade_close each frame their stated target.
