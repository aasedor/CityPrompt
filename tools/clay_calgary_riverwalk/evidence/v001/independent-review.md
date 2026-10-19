# Independent holistic review: clay-calgary-riverwalk v001 (RLASM v6.1)

Reviewer: independent, adversarial. Evidence: the rendered pixels in `renders/*.png` and `boards/*.png`, checked against the locked sources `sources/front.png`, `sources/oblique.jpg` and `sources/top.jpg`. I did not use metadata, counts, hashes or builder notes as proof. I made zoomed crops into a new folder, `/tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/rwalk-review-crops-196906655/`. I wrote no other files.

## 1. Verdict

**VISUAL_REWORK_REQUIRED**: the street section reads correctly overall, but the Peace Bridge does not connect to the promenade. Its south end stops inside the riparian planting bed, against a continuous handrail (P0). Eight production-quality defects (P1) also need fixing:
- bridge form
- band widths
- rip-rap
- riparian cover
- building-edge planters, gabions and rail
- blank rear facades
- the gap between the promenade slab and the bank
- whole-envelope camera framing

Counts: P0 = 1, P1 = 8, P2 = 5

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P0 | aerial, rear_north, river_railing, top, aerial_section | **The Peace Bridge does not land on the promenade.** The deck and truss cross the rip-rap and run over the riparian bed, then stop against the promenade's river handrail. The handrail continues unbroken past the bridge end (aerial ~x600-950 y200-340; rear_north ~x760-800). No abutment, landing apron, ramp or opening in the rail exists, so the bridge cannot be reached from the walk. The south end is open, with zig-zag truss bar stubs and no end ring or portal (river_railing ~x1100-1145 y340-520). Grass blades and a faceted shrub rise into the deck zone (rear_north crop). In the sources the bridge lands at the north end of the walk and joins the path (top, oblique). | Bridge placed by span length only. Landing not integrated with the bank, planting scatter and rail generator. | Add a south abutment and a paved landing apron that connects the deck to the promenade at grade. Cut a gap in the river handrail at the landing and add rail returns. Exclude planting and tree scatter from the bridge footprint plus a ~1 m margin. Close both truss ends with an end ring or portal so no bars are left as free stubs. |
| 2 | P1 | front, river_railing, peace_bridge, rear, aerial, front_corner | **The bridge reads as a straight rectangular lattice box.** Its section is constant over the full span, the top and deck are flat, and the deck sits at bank level with almost no clearance over the water (peace_bridge: deck soffit ~10-15 px above the water). In the sources (front, oblique, top) the bridge is a long lens-shaped helical tube: tapered, pointed ends, a shallow arched deck clearly above the water, and a white roof skin over the red helix. The render's roof plane is clear, so the white canopy band is missing. | Truss swept along a straight line with a fixed radius and no camber. Roof given a glass material. | Taper the helix radius toward both ends to pointed noses. Give the deck a shallow camber, roughly 1.5-2.5 m rise at midspan above the bank seats. Change the roof skin to an opaque or translucent white source colour. |
| 3 | P1 | top, aerial, front_corner | **Wrong band widths.** Measured on top.png at y=600: rip-rap ≈24 px, riparian strip ≈33 px, promenade ≈50 px, planter edge ≈21 px. In source top, rip-rap and riparian each roughly equal or exceed the promenade width (approx. 90 : 100 : 90 px near the bottom of the frame). The rip-rap is about half its source proportion, and the riparian strip about two-thirds. | Section widths in the family recipe taken from a generic street template, not from the top source. | Re-proportion the section from the top source: rip-rap ≈ 1.0×, riparian ≈ 1.0-1.2× and building-edge planter strip ≈ 0.5-0.6× the promenade width. Keep the promenade width unchanged. |
| 4 | P1 | riprap_bank, front_corner, aerial_section, rear_north, peace_bridge | **The rip-rap is near-white angular cubes.** It is brighter than the promenade (pixel ~154 grey vs promenade ~140), so it reads as rubble, ice blocks or spilled paving. The sources show rounded, varied mid-to-dark grey boulders, densely packed down a slope. The cubes are also sparse, with flat apron showing between them. | Box primitives with a single pale material, scattered at low density. | Use rounded or chamfered low-poly boulders (icosphere or beveled, non-uniform scale) in 2-3 mid-grey source tones darker than the promenade. Pack them to cover the slope fully from the waterline to the grass. |
| 5 | P1 | promenade_section, riprap_bank, aerial, aerial_section, front, river_railing | **The riparian strip is mostly bare brown soil**, with sparse vertical stick grasses and a few isolated faceted green shrubs. The sources show continuous, dense native grass and shrub cover in green-gold, with no visible soil, wrapping the cottonwood trunks. | Grass scatter density far too low. Soil material left exposed as the finish. | Add a continuous green-gold grass ground-cover mass (a low undulating mesh or dense clumps) over the whole strip. Raise clump density several-fold, add shrub masses at varied heights, and limit visible soil to small gaps. |
| 6 | P1 | front, facade_close, planters_benches, architecture_close, promenade_section | **The building edge does not match the sources.** The raised planters are smooth beige plaster boxes, not stone-faced. There are no gabion walls anywhere. Planting is solid green cubes (topiary blocks). The bronze rail on the building-side planter and gabion edge, seen in source front (right) and oblique (lower right), is missing. Source oblique and front show gabion walls (caged grey stone), rough stone-faced planter walls, grasses and shrubs, and a slender rail. | Planter assembly built as a generic box. Gabion and rail parts not authored. | Give the planter walls a grey stone-faced material and coursing in the clay palette. Add gabion wall segments (caged-stone grid read) between or beneath the planters. Replace the cube shrubs with grass and shrub clumps. Add the slender bronze rail on the planter and gabion edge. |
| 7 | P1 | right_side, rear_side, rear, aerial | **The rear (inland) facades of all three blocks are blank, windowless walls.** The north and south end walls are also blank, apart from balcony edges in rear. This contradicts the windowed, balconied grammar of the river facade. Right_side shows only three plain boxes. | Facade generator applied to the river face only. | Repeat the window grid (and patio or balcony rhythm where appropriate) on the rear and end facades at the same storey heights. A simplified window grid is acceptable for clay. |
| 8 | P1 | rear_north (section cut), promenade_section | **Contact defect: an open slot runs between the promenade slab and the riparian bed** for the full depth of the section (rear_north crop: a dark vertical slit beside the slab end). It shows along the length as a dark seam. River-rail post bases sit on the slab edge with thin white slivers, so they read as partly overhanging the slot. | Promenade slab and bank block built as separate solids with a small offset. | Butt the slab and bank solids together, or add a kerb or edge-strip solid that fills the slot. Seat the rail posts fully on the kerb or slab with small base plates. |
| 9 | P1 | rear, left_side, rear_side (and phone-03/phone-04 boards) | **The whole-envelope cameras frame the asset too small.** In rear the section is a thin sliver about 12% of the frame height. Left_side and rear_side show the asset at roughly 15-20% of the frame height with large empty ground. At phone-board size the section bands, rail and bridge landing are illegible. | Orbit distance fixed for a larger bounding box. | Fit each whole-envelope camera to the asset bounds with about 10% margin. Lower the rear and left_side elevation, or tighten the focal length, so the asset fills at least 60% of the frame width and reads clearly on the phone board. |
| 10 | P2 | facade_close, glass_close, front_corner | The blocks are smooth cream render, not pale brick. There is no darker top-storey or penthouse setback (source oblique and top). Balconies are projecting slabs with no balcony doors behind them (glass_close: sill well above the slab). | Generic facade kit. | Add brick-coursing tone and a darker set-back top storey. Turn one window per balcony into a door. |
| 11 | P2 | front, aerial_section, left_side | The cottonwoods are identical lollipop canopies at uniform spacing. Source cottonwoods are taller and more open, with irregular crowns. | One tree prototype instanced. | Use 2-3 tree variants with varied height, crown and lean. |
| 12 | P2 | peace_bridge | A grey rectangular block sits in the water under the deck near the far bank. It looks like an in-river pier, which the sources do not show. | Far-bank abutment extends past the bank line. | Pull the abutment back behind the far-bank edge. |
| 13 | P2 | top, aerial, left_side | The far bank is a flat green slab with a single row of trees. The source far bank is wooded, with its own rip-rap edge. | Context simplified. | Add a rip-rap edge strip and a denser tree massing on the far bank. |
| 14 | P2 | front, facade_close | Lamp posts are tall lantern posts on bare paving with no base. | Simplified lamp. | Add a small base plate or plinth. |

## 3. Source conformance checklist

| Item | Status | View(s) used |
|---|---|---|
| Section order (river → rip-rap → riparian → rail → promenade → edge → blocks) | **Conforms** in order | top, aerial, promenade_section |
| Section widths | **Deviates**: rip-rap ≈0.5× and riparian ≈0.65× promenade vs ≈1× in source (F3) | top vs source top |
| River (blue-green water) | Conforms (flat teal, straight bank) | top, aerial, front_corner |
| Rip-rap bank | **Deviates**: sloped, but white angular cubes, sparse, too narrow (F3, F4) | riprap_bank, rear_north, front_corner |
| Riparian grasses | **Deviates**: sparse sticks on bare soil (F5) | promenade_section, riprap_bank |
| Shrubs | **Deviates**: isolated single faceted blobs, not shrub masses (F5) | promenade_section, river_railing |
| Cottonwoods | Conforms in placement and rhythm in the riparian strip. Form simplified (F11, P2). | front, aerial_section |
| Handrail (slender bronze, low posts) | Conforms in colour, slenderness and position on the river edge. Post seating defect (F8). Unbroken across the bridge landing (F1). | river_railing, promenade_section |
| Promenade surface and joints | Conforms: wide pale concrete with scored square joints | front, facade_close, architecture_close |
| Planters | **Deviates**: smooth beige boxes, cube planting (F6) | planters_benches, front |
| Gabions | **Deviates: absent** (F6) | planters_benches, architecture_close, front |
| Benches (timber) | Conforms: timber benches facing the promenade, grounded | planters_benches, architecture_close |
| Edge trees | Conforms: small trees in planters | facade_close, planters_benches |
| Lamps | Conforms (plausible). Not clearly shown in the sources; no base (F14, P2). | front, facade_close |
| Blocks and patios | Patios conform (low slatted fences, ground-floor glazing). Blocks deviate: blank rear and end facades (F7), smooth render, no top-storey setback (F10). | architecture_close, right_side, rear_side |
| Peace Bridge: truss | Partly conforms: red diagonal helix lattice is legible. Box section, no tapered ends, clear roof (F2). | river_railing, peace_bridge, aerial |
| Peace Bridge: deck | **Deviates**: flat, at bank level, minimal water clearance (F2) | peace_bridge, rear |
| Peace Bridge: landing | **Deviates (P0)**: ends in the planting bed against a continuous rail, no connection (F1) | aerial, rear_north, river_railing |
| Far bank | Conforms as context (wooded bank simplified, F13) | top, aerial, left_side |
| Materials hierarchy | **Deviates**: rip-rap brighter than the promenade; planters read as plaster; soil dominates the riparian strip (F4, F5, F6) | riprap_bank, promenade_section |

## 4. Camera validity

- **rear**: the asset is a thin sliver, about 12% of the frame height, centred in a mostly empty ground and sky field. Its silhouette is legible at full resolution, but band order, rail and landing cannot be read on the phone board (F9, P1).
- **left_side**: the asset is small, about 15% of the frame height. The bridge is foreshortened and the near abutment is ambiguous. Marginal at phone size (F9).
- **rear_side**: the asset fills about 30% of the width. The street section is mostly hidden behind the blank rear boxes (F7, F9).
- **right_side**: the inland view is necessarily occluded by the context blocks. It is valid as an envelope view, but it shows only blank walls (F7).
- **front, front_corner, aerial, top and all ten detail views**: valid. The target is unoccluded, unclipped and legible. The near foreground bench in front is cropped by the frame edge, which is acceptable.
