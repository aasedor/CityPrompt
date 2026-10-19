# Independent holistic review: clay-calgary-riverwalk v002 (RLASM v6.1 architectural clay)

Reviewer: independent, adversarial. Evidence used: only the pixels of `sources/front.png`, `sources/oblique.jpg`, `sources/top.jpg`, all 18 `renders/*.png` (each opened at full resolution) and the four `boards/*.png`, plus zoomed crops written to a new folder, `scratchpad/crops-rwalk2-227522939/`. I did not treat builder notes, metadata or counts as proof.

## 1. Verdict

**VISUAL_REWORK_REQUIRED.** The v001 P0 is fixed: the Peace Bridge now lands on a promenade-level landing through an opening in the rail. Two P1 blockers remain. First, the `right_side` whole-envelope camera shows only the land-side backs of the blocks and the whole street section is hidden. Second, every window has a black hole where the mullion crosses the transom, and it is plainly visible in the close detail views.

Counts: P0 = 0, P1 = 2, P2 = 13

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | right_side (also phone-03 board) | The camera looks from the land side at the three blocks' rear faces. They fill a thin horizontal band (y≈365–668 of 1080), and about 60% of the frame is empty grey ground and sky. River, rip-rap, riparian strip, rail, promenade, planters and Peace Bridge are all hidden behind the blocks. Only two treetops and a sliver of patio show through the gaps. The street section does not read at all. This is the same framing failure v001 recorded for rear, left_side and rear_side, and it was not corrected here. | The right_side camera is a level, low elevation from inland, and the context blocks fully occlude the street option they sit behind. | Re-aim right_side as a raised three-quarter view (about 25–35° down) from the inland side so the camera looks over the block roofs and down the gaps to the promenade, planters, riparian strip and bridge. Alternatively, hide or section the blocks for this view. Fill at least 70% of the frame with the asset. |
| 2 | P1 | glass_close, architecture_close, planters_benches, facade_close | Every window has an opaque black square (≈8–10 px at 1440 wide) where the mullion meets the transom. It shows on all four windows in glass_close, on the ground-floor windows in architecture_close (≈990,365) and on those in planters_benches (≈535,415 and ≈1025,440). It reads as a hole or inverted face in the frame. | The mullion and transom boxes are coincident or overlap at the crossing. That causes a non-manifold or inverted-normal patch, or a gap through to the black interior. | Make the mullion and transom one merged frame mesh, or offset the transom by a few mm. Recalculate normals outward and re-render the three close views to confirm there are no black pixels at the crossings. |
| 3 | P2 | peace_bridge, front, aerial, front_corner | The bridge silhouette is humped. The crown of the lattice rises well above the deck like a barrel vault, which reads deeper than the slender, nearly flat-topped lens in the front and oblique sources. The diamond lattice is a fine double mesh of about 30 bays, against about 16 large diamond bays in the source. In plan (top) the ends are square-cut, while the source top shows angled, pointed tips. | The tube section is too deep at midspan and the helix pitch is too fine. | Flatten the crown so the tube is about 1:11 depth to span. Halve the number of lattice bays. Bevel the plan ends to a point. |
| 4 | P2 | rear_side, peace_bridge, rear | No stone abutment can be read under the near deck end. In the rear_side crop the deck underside sits directly on rip-rap boulders, and in peace_bridge the near end leaves the frame over the boulders. | The abutment is buried in or hidden by the rip-rap, or it is too small. | Expose a 1–1.5 m coursed-stone abutment face under the landing, between the rip-rap crest and the deck soffit, and keep boulders clear of the deck underside. |
| 5 | P2 | top, aerial, peace_bridge | The far bank is a flat mown-lawn slab with 6 to 8 isolated lollipop trees and scattered pebbles. The sources show a wooded bank with a rip-rap edge and a path. | Context bank was authored minimally. | Add a rip-rap strip along the far-bank edge, cluster the trees into a continuous woodland mass, and add a path to the far landing. |
| 6 | P2 | planters_benches, architecture_close | The "gabion" planters and patio walls read as pale square tiles in a brown timber-like grid. There are no stone lumps behind the mesh, and the mesh is brown, not galvanised grey. The coursed-stone planters read as concrete block. | The gabion is modelled as a flat panel with a grid overlay. | Put faceted stone fill behind a thin grey mesh grid. Give the coursed stone a warm grey-buff tone and irregular course heights. |
| 7 | P2 | river_railing, front, promenade_section | Riparian grass tufts are rigid, evenly sized cones that read as spikes or miniature conifers rather than soft, golden native grasses. | A single cone primitive is used for grass. | Use clumped multi-blade tufts of varied height, leaning outward, with more golden-straw tones. |
| 8 | P2 | riprap_bank, left_side | A continuous black wedge or band runs along the waterline under the boulders. It reads as a void or skirt instead of boulders entering the water. | A dark bank base plane shows between the boulder row and the water plane. | Lower the bottom boulder row below the water surface, or give the base plane the rip-rap grey. |
| 9 | P2 | front, river_railing, architecture_close, planters_benches | River rail, planter rails, lamps, benches and tree trunks all share one mid brown, so the bronze handrail is not distinguished from timber. | One brown material is reused. | Give the handrails and lamp shafts a darker bronze, distinct from the warmer timber of the benches. |
| 10 | P2 | glass_close, facade_close | Balconies have no door. The windows behind them have sills about 0.7 m above the balcony slab, so the balconies cannot be reached. The oblique source shows full-height glazed doors. | Window module reused at balcony bays. | Swap the window at each balcony bay for a full-height glazed door. |
| 11 | P2 | front, facade_close | Lamp posts crowd the benches. In the front view the end of a bench seat touches or overlaps the lamp shaft. | Lamp and bench are placed on the same rhythm with no clearance. | Offset the lamps by at least 0.5 m from the bench ends, or alternate their bays. |
| 12 | P2 | architecture_close | The building-side planter rail posts stand in the soil, not on the coping, and the top rail passes through shrub canopies. | Rail placed on the soil centreline. | Seat the posts on the river-side coping and pull the shrubs back from the rail line. |
| 13 | P2 | front, peace_bridge, riprap_bank | In front, the river shows only as a thin sliver behind the riparian planting (the source front shows a broad expanse of water). In peace_bridge, the near landing is clipped by the frame and a large foreground shrub fills the lower right. The boulders are sharp-faceted rather than rounded river stone, and the blocks lack the darker recessed top storey seen in the oblique. | Camera height and aim; low-poly boulder primitive; simplified context massing. | Raise the front camera slightly toward the river rail. Pull the peace_bridge camera back so both landings are in frame. Smooth the boulder facets (subdivide once). Optionally add a set-back top storey. |

## 3. Source conformance checklist

| Item | Status | View(s) used | Note |
|---|---|---|---|
| Section order (river, rip-rap, riparian planting, rail, promenade, building edge, blocks) | conforms | top, left_side, rear, rear_north | The order is correct from the river inland. |
| Section widths | conforms | top (pixel run at y=560 and 700) | Rip-rap ≈56 px, riparian ≈60–63 px, promenade ≈52 px, building edge ≈30–35 px. Rip-rap and riparian are each about the promenade width, as in the top source. |
| River | conforms | top, aerial, left_side | Blue-green water plane. In the front view it is barely visible (P2 #13). |
| Rip-rap | conforms | left_side, riprap_bank, front_corner, aerial_section | Packed grey boulders, clearly darker than the promenade. They are angular, not rounded (P2 #13), and there is a black waterline band (P2 #8). |
| Riparian grasses | conforms (simplified) | rear, rear_north, river_railing | Dense continuous cover. The cone tufts read as spikes (P2 #7). |
| Shrubs | conforms | left_side, rear_north, aerial | Dense shrub masses. |
| Cottonwoods | conforms | front, left_side, aerial_section | Tall riparian trees at regular spacing. |
| Handrail | conforms | river_railing, promenade_section | Slender rail on low posts with base plates on a stone kerb, with an opening at the landing. The colour is not distinguished as bronze (P2 #9). |
| Promenade surface and joints | conforms | front, facade_close, promenade_section | Wide pale concrete with scored square joints. |
| Planters | conforms | architecture_close, planters_benches, rear | Raised planters with soil, grasses, shrubs and a river-side rail. |
| Gabions | deviates (minor) | planters_benches | Present as gridded walls but they do not read as stone-filled gabions (P2 #6). |
| Benches | conforms | architecture_close, planters_benches | Timber benches with backs, grounded on legs. |
| Edge trees | conforms | front, facade_close, rear | Small trees in the planters. |
| Lamps | conforms (addition) | front, facade_close | Not contradicted by the sources. They crowd the benches (P2 #11). |
| Blocks and patios | conforms | front_corner, left_side, right_side, rear | Pale mid-rise blocks with balconies. Rear and end faces now have window grids. Gabion patio walls are present. Balconies lack doors (P2 #10). |
| Peace Bridge truss | conforms (with deviation) | peace_bridge, rear_side, aerial | Red diamond-lattice tube tapering to pointed ends, with a white roof skin. The crown is humped and the lattice too fine (P2 #3). |
| Peace Bridge deck | conforms | peace_bridge, rear_side | Shallow arched deck visible beneath the lattice. |
| Peace Bridge landing | conforms | top, aerial, aerial_section, rear, rear_north | A promenade-level landing slab crosses the riparian strip. The kerb and river rail open at the landing, with landing rails on both beds, and the truss runs onto the landing with a closed end. The abutment is not legible (P2 #4). |
| Far bank | deviates (context) | top, aerial, peace_bridge | Lawn with sparse trees, not woodland (P2 #5). The far landing slab is present. |
| Materials hierarchy | conforms (minor deviation) | all | Water, then dark rip-rap, then olive planting, then pale promenade, then cream blocks, with the red bridge reading clearly. The bronze is not separated from timber (P2 #9). |

## 4. Camera validity

- **right_side: invalid (P1 #1).** The context blocks occlude the target street section entirely, and the asset fills only a thin band of the frame.
- peace_bridge: valid but weak. The near landing is clipped at the right edge and a foreground shrub covers the lower right (P2 #13). The landing is read from rear, rear_north, aerial and aerial_section instead.
- front: valid. The promenade, rail, riparian strip, edge and bridge read; the river is under-shown (P2 #13).
- front_corner, aerial, top, left_side, rear, rear_side, rear_north, aerial_section, facade_close, architecture_close, glass_close, promenade_section, river_railing, planters_benches and riprap_bank are all valid. In each, the target is legible, unclipped and unoccluded.

## 5. Previous-version (v001) findings: resolved in the pixels?

| v001 finding | Status in v002 pixels | Evidence |
|---|---|---|
| P0: Peace Bridge stops short of the promenade, no abutment or landing, river rail continuous across its end, open truss ends | **Resolved.** The abutment itself is still not legible (P2 #4). | In top, a pale landing slab spans the riparian strip from the truss end to the promenade, with a gap in the kerb and rail. In aerial and aerial_section, landing rails line both riparian beds and the promenade-side rail stops at the landing. In rear and rear_north, the truss runs onto the landing and its end converges to a closed, pointed end with a curved end member. |
| P1: bridge not read as a tapered tube with pointed ends, shallow arched deck and white roof | **Resolved**, with a P2 residual on silhouette and lattice density (P2 #3). | peace_bridge: the far end tapers to a point, the deck soffit arches, and a white roof skin shows through the lattice. as_landing crop: the near end is pointed. |
| P1: band widths off the top source | **Resolved** | Top pixel runs: rip-rap ≈56, riparian ≈60–63, promenade ≈52, edge ≈32 px. |
| P1: rip-rap too pale, not packed grey boulders darker than the promenade | **Resolved.** The boulders are angular rather than rounded (P2 #13). | left_side, riprap_bank, front_corner: dense, multi-row, dark grey packed boulders, well below promenade value. |
| P1: thin riparian strip without dense grass and shrub cover | **Resolved** | left_side, rear_north, aerial: continuous shrub masses, tufts and cottonwoods across the full strip width. |
| P1: building-edge planters without stone or gabion walls, planting or building-side bronze rail | **Resolved**, with gabion and stone read as P2 (#6). | architecture_close, planters_benches: coursed-stone and gridded gabion planters with soil, shrubs and grasses, a rail on the river side, gabion patio walls and benches. |
| P1: blank rear and end facades | **Resolved** | right_side: window grids on all three rear faces. front_corner and rear_side: windows on the end faces. |
| P1: slot between promenade slab and riparian bed, floating rail posts | **Resolved** | rear and rear_north section cuts: the riparian soil block butts the promenade section with no gap. river_railing: posts on base plates on a continuous stone kerb. |
| P1: rear, left_side and rear_side framed so the section did not read | **Resolved for those three views.** The same defect remains in right_side (P1 #1). | rear: section cut through every band. left_side: river to blocks. rear_side: section with the bridge and its landing. |
