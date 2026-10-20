# Independent holistic review: road diet complete street, v001 (RLASM v6.1 architectural clay)

Reviewer: independent; I did not build this. I judged only rendered pixels against the three locked sources (sources/front.png, sources/oblique.jpg, sources/top.jpg). I opened all 18 renders at full resolution and all 4 phone boards. Zoomed crops are in /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/crops-review-68af4526/.

## 1. Verdict

**VISUAL_REWORK_REQUIRED**: the road-diet topology and street identity are right (one lane each way, a centre two-way left-turn lane, protected green bike lanes, four zebra crosswalks, planted refuge islands, four signal corners and the correct street wall), but six clearly visible P1 defects block production-quality approval. They are in landscape fidelity, contact (canopies and lamps passing through other parts), the island planting, the placeholder cars and the marking finish.

Counts: P0 = 0, P1 = 6, P2 = 7

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | front, bike_lane_separator, verge_trees, turn_lane, rear | Each west-verge "mature street tree" is a flat-bottomed faceted slab on a bare Y-fork armature. From pedestrian height the canopy underside reads as a flat green plane, like a parasol or table top. In front, the nearest canopy is a flat sheet that fills the top-left of the frame. The source front and oblique show tall, dense, rounded elm-type crowns whose foliage hangs low and overlaps from tree to tree. | The canopy is one flattened low-poly hull with its base cut flat at a fixed height, and the branch stubs are exposed below it. | Use rounded multi-lobe crowns (3 to 5 overlapping ico-spheres, vertical/horizontal ratio about 0.8 to 1.0) with lobes hanging below the fork height so the Y-armature is hidden. Raise the crown mass so neighbouring crowns overlap along the verge, as in the source. |
| 2 | P1 | front, verge_trees | The cobra-head lamp's arm is buried inside a verge-tree canopy. In front, the pole rises into the canopy underside and the head sticks out of the canopy edge with no visible arm (crop front_lamp.png). In verge_trees, the pole passes through the second canopy. | Lamp positions and tree positions on the verge share stations, and nobody checked them for clearance. | Put the lamps midway between trees (offset half a tree pitch), or lower the arm below the crown base, so pole, arm and head read as one connected object clear of foliage. |
| 3 | P1 | corner_signal, rear, right_side, left_side, top | The east-sidewalk and corner tree canopies cut through the storefront facades. In corner_signal (crop corner_canopy.png), the crown is sliced by the cream upper-storey wall and covers a sash window. In rear (crop rear_canopy.png), a crown sinks into the facade over the sign band. In top, the canopies touch or overlap the building footprint edges. | Tree-pit offset from the facade is smaller than the crown radius. | Clamp the crown radius to (facade offset minus 0.3 m), or move the pits to the kerb side of the sidewalk, as in the source oblique, and re-check that the crown and facade do not intersect. |
| 4 | P1 | refuge_island, rubber_curb, turn_lane, crosswalk_zebra, aerial | The refuge-island planting reads as bundles of flat straight planks stuck into bright green cubes, like fries in boxes, set apart on bare brown soil (crop island_plant.png). The source front and oblique show one dense, continuous mound of tall straw grasses that covers the island bed. | The grass clump is modelled as stacked plank blades on a cubic base, and the clumps are sparsely instanced. | Replace each clump with tapered, arching blade fans (or rounded tussock hulls in the straw tone) with no cube base. Increase density so the clumps merge and cover at least 80 % of the bed, and drop the green cube colour. |
| 5 | P1 | right_side, turn_lane, front, cross_street_lane, rubber_curb, bike_lane_separator | The placeholder cars have a cabin of transparent glass, so the roof slab floats above the body with a visible gap (crop rs_car.png). In turn_lane and right_side it reads as a loose plate hovering over a box. | The glass material on the cabin volume is fully transmissive, and no pillars connect the roof to the body. | Make the cabin an opaque dark-grey clay volume (or add four pillars) so the roof visibly rests on the body. The cars remain simple massing. |
| 6 | P1 | bike_symbol, turn_lane | The pavement markings show black triangles and quads wherever strokes overlap: on the bicycle-symbol frame joints (crop bike_sym.png), on the centre-lane turn-arrow elbows (crop turn_lines.png) and on the bike symbols in turn_lane. | Coplanar overlapping marking strips z-fight, or have flipped normals or a negative solidify, where they overlap. | Union each symbol into one mesh (boolean union or a single curve-to-mesh) with consistent normals and a single z-offset above the paint. Then re-render bike_symbol and turn_lane. |
| 7 | P2 | rubber_curb, front, crosswalk_zebra | The yellow marks on the rubber curb stop are rectangular bands. The source shows yellow chevrons. | The pattern is simplified to blocks. | Make the yellow inserts diagonal chevrons. |
| 8 | P2 | turn_lane, refuge_island | The black arrow strokes of the keep-right sign show through the back of the panel (crop sign_back.png). On the face, the arrow is a straight diagonal with a short tail, not the source's curved keep-right arrow. | The arrow geometry is thicker than the panel's offset, or the panel is single-sided. | Inset the arrow on the front face only, leave the back face plain grey, and redraw the arrow as the curved keep-right glyph. |
| 9 | P2 | top | The cross street is wide relative to the main street: its curb-to-curb width is about 0.70 of the main street's, against about 0.53 in the source top, and its travel lanes are close to main-street lane width. | The cross-street lane width is reused from the main street. | Narrow the cross-street travel lanes by about 30 %. |
| 10 | P2 | front, bike_symbol | The west-verge lawn ends near the intersection in a sharp diagonal wedge. | The lawn polygon is chamfered at the corner return. | Square off the lawn end or follow the corner radius. |
| 11 | P2 | storefronts, corner_signal | The shop doors have no transom over them, while the shopfront glazing does. The source storefronts show transoms over the doors as well. Opening depth itself is fine: the glazing and doors are recessed with brick returns and sills (crop store_depth.png). | The door module omits the transom. | Add a transom pane above each door, aligned with the glazing transom. |
| 12 | P2 | (render set) | The brief names facade_close, architecture_close and glass_close, but no such files exist. The set has 18 views, so storefronts is the only close-range proof of glazing depth. | Generic view names are left over in the brief, or those cameras were never rendered. | Render a glass_close of one shopfront bay, or correct the view list in the brief. |
| 13 | P2 | boards/phone-01..04 | Each render tile fills only about 40 % of its cell height, leaving large empty bands, so detail is small on a phone. | The board layout letterboxes 4:3 tiles inside tall cells. | Size the cells to the tile aspect ratio. |

## 3. Source conformance checklist

| item | status | view(s) used |
|---|---|---|
| Section order west to east (verge, bike lane, separator, travel lane, centre turn lane, travel lane, separator, bike lane, sidewalk, storefronts) | conforms | top, turn_lane, rear, front |
| Band widths (main street) | conforms; travel and centre lanes in plausible proportion, verge generous as in the source | top, turn_lane |
| Cross-street width | deviates (P2 #9, too wide) | top |
| Green paint extent (all four main-street lanes, cross-street curb lanes, through the crosswalks under the bars) | conforms | top, bike_symbol, corner_signal, aerial |
| Raised concrete separators with white delineator posts | conforms (raised, kerbed, posts on bases) | bike_lane_separator, rubber_curb, turn_lane |
| Rubber curb stops with three posts at the crosswalks | conforms in placement and posts; chevrons simplified to bands (P2 #7) | rubber_curb, crosswalk_zebra, bike_symbol, top |
| Centre-lane yellow lines (solid outer, dashed inner) | conforms | turn_lane (crop turn_lines.png), rear |
| Opposing white left-turn arrows | conforms in layout; joint artifacts (P1 #6) | turn_lane, rear, top |
| Refuge island curb | conforms (raised white kerb, soil bed) | refuge_island, crosswalk_zebra |
| Refuge island planting | deviates (P1 #4) | refuge_island, rubber_curb |
| Keep-right sign | conforms in presence and placement; glyph and back face are P2 #8 | refuge_island, turn_lane, aerial |
| Yellow-and-black object marker | conforms | refuge_island, crosswalk_zebra |
| Refuge islands beyond the crosswalks in the centre lane (as in the top view) | conforms | top, aerial |
| Continental crosswalks on all four legs, over the bike lanes | conforms | top, aerial, crosswalk_zebra, bike_symbol |
| White stop bars | conforms (all four approaches) | top, crosswalk_zebra |
| Cross-street dashed yellow centre line | conforms | cross_street_lane, top |
| Cross-street hatched painted buffer with posts | conforms | cross_street_lane, left_side, right_side |
| Cross-street green curb lanes | conforms | cross_street_lane, top |
| White bicycle symbols on all green lanes | conforms in presence; finish defect (P1 #6) | top, bike_symbol, turn_lane, cross_street_lane |
| Signal poles with mast arms and three-lamp heads at the four corners | conforms | top, corner_signal, aerial, left_side |
| Black cobra-head lamps in the west verge | conforms in presence; contact defect with canopies (P1 #2) | verge_trees, front_corner, top |
| Mature verge trees | deviates (P1 #1) | front, verge_trees, bike_lane_separator |
| East sidewalk young trees in pits | conforms in placement; canopy-facade intersection (P1 #3) | storefronts, crosswalk_zebra, corner_signal |
| Pale east sidewalk with scored joints | conforms (faint joints) | crosswalk_zebra, verge_trees (west equivalent) |
| Bins and bike racks | conforms | storefronts, crosswalk_zebra, front_corner |
| Storefront row: brick ground storey with large shopfront glazing and transoms | conforms; glazing recessed with returns | storefronts (crop store_depth.png), corner_signal |
| Storefront row: doors | conforms with recess; no door transoms (P2 #11) | storefronts |
| Storefront row: dark sign band | conforms | storefronts, corner_signal |
| Storefront row: cream upper storey, brick pilasters, sash windows, coping | conforms | storefronts, corner_signal, rear |
| Four-storey brick apartment block with balconies further north on the east | conforms (projecting slabs and railings) | front, front_corner, bike_lane_separator |
| Beige stucco two-storey block on the south-east corner | conforms | right_side, aerial |
| Two-storey brick office and one-storey block set back behind lawns on the west | conforms | left_side, front, rear_side, verge_trees |
| Context massing further out | conforms (plain clay boxes) | aerial, rear_side, top |
| Cars as simple clay placeholders | deviates (floating roof, P1 #5) | right_side, turn_lane |
| Pedestrians and cyclist omitted | conforms (as instructed) | all |
| Materials hierarchy (asphalt dark, green paint, pale concrete, brick, cream, dark glazing, black metal, straw planting) | conforms, except the green cube bases on the island planting | all |

## 4. Camera validity

- All 18 views are legible, and none has its target occluded.
- front: the camera stands at the intersection looking north, as the brief directs, and pairs correctly with the locked front. The nearest verge-tree canopy is clipped by the top edge as a flat sheet over about 15 % of the frame. That is a symptom of P1 #1, not an invalid camera.
- storefronts: a very close oblique. It is valid and proves the opening depth.
- left_side and right_side: looking along the cross street. They are valid; foreground canopies are clipped at the frame edge, but the targets are clear.
- The three detail views named in the brief but absent (facade_close, architecture_close, glass_close) are logged as P2 #12. Their absence does not leave any identity element unverifiable.

## 5. Previous-version findings

This is the first version (v001), so there are no previous-version findings to carry forward or close.
