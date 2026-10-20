# Independent holistic review: clay-vancouver-special v001 (RLASM v6.1 architectural clay)

Reviewer: independent holistic reviewer (not the builder). Evidence used: only the locked sources (`sources/front.png`, `sources/oblique.jpg`, `sources/top.jpg`), the 18 render PNGs in `renders/` and the four phone boards in `boards/`. All were opened at full resolution. Zoomed crops (no overwrites) are in `/tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/vspec-review-crops-4275fa7d/`. Builder notes, metadata, counts and hashes were not used as proof.

## 1. Verdict

**VISUAL_REWORK_REQUIRED**: the massing, roof, brick/stucco split, balcony, landing and stairs read correctly as this Vancouver Special, but three P1 defects block approval. Black unlit faces show on the trim, casings and pipe joints in the street-facing views. The rake-to-eave roof corners are unresolved. The fenestration rhythm on the east (side-street) face does not follow either source.

Counts: P0 = 0, P1 = 3, P2 = 7

## 2. Findings

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | front, rear, rear_side, architecture_close, facade_close, balcony_rail, entry_stair, side_entry | Solid black patches on otherwise brown or white trim. A black spike sits at the gable apex fascia mitre (front and rear). Black end faces show on the rake fascia ends, on every downpipe elbow, offset and outlet joint, and as black squares at both top corners of the white front-door casing. Black dots appear on the railing post caps at the stair heads. They are visible from the street-level front view as well as in the close-ups. | Open-ended or coincident box ends with inverted or missing normals, or an unassigned/black material slot on end caps and corner blocks. Coplanar overlapping caps may also be z-fighting into black. | Recalculate outward normals on the fascia, downpipe, casing and post-cap meshes. Cap the open ends with the parent material, or remove the duplicate corner/cap cubes and use mitred or overlapping geometry with a small offset. Assign brown or white material to every face, then re-render front, rear, facade_close and architecture_close to confirm no pure-black pixels remain on trim. |
| 2 | P1 | architecture_close, front (east and west eave corners), front_corner | The brown rake fascia does not wrap the front roof corners. At the front-east corner the rake board stops with an exposed end face, and the eave gutter box starts beside it at a different height and angle. The result is a stepped, misaligned joint with a visible slot, not a continuous corner. The front-west corner shows the same stepped junction at a smaller scale. | The rake fascia and the eave gutter/fascia are generated as independent straight members, with no corner return or mitre solve at the gable-eave intersection. | Add a corner-return solve: extend the eave fascia and gutter to the rake plane and terminate the gutter with an end cap flush to the rake fascia face, or mitre the rake fascia into the eave fascia, so that the two brown members meet on one plane with no gap or step at all four gable corners. |
| 3 | P1 | east_side, right_side, side_entry, front, front_corner (vs sources front and oblique) | Fenestration rhythm on the side-street face does not match the sources. Both sources leave the front roughly 40-50% of the east wall blank and group the openings mid-wall. In the front source, two upper windows stack directly over one ground window and the suite door. In the oblique source, small upper windows sit high under the eave. The render spreads three upper windows evenly from about 21% of the wall length and puts a ground window right behind the front corner (about 21-29%). It sets the suite door at about 60% with no window above it and adds a third ground window at the rear. | The east elevation openings were laid out on an even bay grid, not taken from the source-visible positions. | Re-place the east openings from the sources. Keep the front ~45% of both storeys blank stucco. Put the upper windows (two, or small high-set ones per the oblique) in the middle third, stacked over the ground window and the suite door. Keep the door, landing and southward flight together. Remove or justify the near-front ground window and upper window. |
| 4 | P2 | top, aerial, front_corner, roof_ridge, left_side | Roof shingles are a neutral cool grey. Both photographic sources show a warm brown-grey (taupe) asphalt shingle. | Roof clay colour sampled too neutral. | Shift the roof clay toward the source brown-grey (warmer and slightly darker). |
| 5 | P2 | brick_base, facade_close | Window sills on the brick storey are plain projecting orange slabs. There is no rowlock (on-edge brick) coursing, which the front source shows. | Sill modelled as a single block without the rowlock joint pattern. | Add rowlock joint lines (vertical header joints) or a header-course step to the sill block. |
| 6 | P2 | brick_base | The brick joint pattern has small black pinholes at many joint intersections. | Joint texture/procedural artefact at T-junctions. | Clean the joint map so the intersections use the mortar colour. |
| 7 | P2 | east_side, side_entry | The suite door is a half-glazed panel door, where the front source shows a near full-lite glazed door. The suite flight has only an outer railing; the sources show railings on both sides, with a concrete cheek wall in the oblique. | Generic door and stair-rail preset. | Use a full-lite glazed door. Add the second railing and the cheek wall to the suite flight. |
| 8 | P2 | front, entry_stair, facade_close | The mailbox is a large black box. The source shows a small wall-mounted mailbox plate beside the door. | Oversized placeholder. | Reduce it to a slim wall plate of roughly the source size. |
| 9 | P2 | top, aerial, right_side | The lawn strip between the east wall and the public sidewalk is noticeably wider than in the top source. The sidewalk/curb at the street corner has a square return, where the top source shows a radiused curb return. | Site offsets and corner geometry simplified. | Narrow the east side strip to the source proportion. Add a radiused curb and sidewalk return at the corner. |
| 10 | P2 | rear_side, top, aerial, front | Extra broadleaf boulevard trees appear that are not in the sources. In rear_side the foreground tree hides the lower north-east quarter, including the cedar row and the fence corner. The target is still legible, and these features are shown in right_side, east_side and rear. | Context trees placed without checking the view cones. | Remove or move the boulevard trees so they match the sources. Keep the rear_side camera cone clear of foreground canopy. |

## 3. Source conformance checklist

| item | status | view(s) used | note |
|---|---|---|---|
| Silhouette and storey count | conforms | front, east_side, left_side, rear vs source front/oblique | Boxy two-storey block, plan proportion about 1.17 (render top) vs 1.19 (source top) |
| Roof pitch | conforms | rear, front, front_corner vs source front/oblique | Low, wide gable. It reads marginally steeper in the low-angle front camera; the near-orthographic rear rise/width matches the source front (about 0.19) |
| Front-gable ridge front-to-back over the middle | conforms | top, aerial, roof_ridge vs source top | Ridge centred (about 50% of width), running north-south |
| Overhangs | conforms | front, left_side, east_side | Deep rake and eave overhangs |
| Shingle courses | conforms (colour deviates, P2 #4) | top, roof_ridge, front_corner | Courses parallel to the eaves, darker ridge cap |
| Fascias | deviates (P1 #1, #2) | architecture_close, front | Brown fascias present; apex and corner junctions defective |
| Gutters | deviates (P1 #2) | architecture_close, left_side, east_side | Brown gutters on the side eaves; corner termination unresolved |
| Outriggers under the front gable | conforms | front, facade_close, architecture_close | Brown blocks under the open rakes |
| Brick ground storey (joints) | conforms (P2 #6) | facade_close, brick_base, entry_stair | Red-orange brick on the street front only, white joints |
| Rowlock sills | deviates (P2 #5) | brick_base, facade_close | Plain orange ledge |
| Stucco upper storey and other walls | conforms | front, left_side, east_side, rear | White stucco on the upper front and on all other walls |
| Balcony slab and fascia | conforms | balcony_rail, front_corner | Thick white slab fascia, cantilevered |
| Balcony railing | conforms | balcony_rail, facade_close | Grey aluminium pickets, top rail, end returns to the wall |
| Balcony extent | conforms | top, facade_close, aerial vs source top/front | Covers the east ~69% of the front (source ~65%), flush with the east corner |
| Windows: bronze sliders | conforms | glass_close, brick_base, facade_close | Bronze frames, visible reveals and depth, sills |
| Windows: light count | conforms | facade_close | Upper-left 3-light; small upper 2-light; 3-panel sliding door; both ground front windows 3-light |
| Windows: sizes per floor | conforms | facade_close vs source front | Wide upper-left, small window and wide slider behind the balcony, wide ground windows on either side of the entry |
| Windows: curtains | conforms | glass_close, brick_base, interior | Side curtain panels on the outer lights |
| Front door | conforms | facade_close, entry_stair | White panelled door |
| Sidelight | conforms | facade_close | Glazed sidelight on the west side of the door |
| Casing | deviates (P1 #1) | facade_close, entry_stair, balcony_rail | White casing with black corner squares |
| Coach lamps | conforms | facade_close, entry_stair | Two, one on each side of the entry |
| Mailbox | conforms (size P2 #8) | facade_close | East of the door |
| Landing | conforms | facade_close, entry_stair, top | Raised concrete landing under the door and sidelight |
| Front stair and railings | conforms | entry_stair, top, front | Runs down eastwards along the front, aluminium railings on both sides plus a landing guard |
| East side windows | deviates (P1 #3) | east_side, front vs source front/oblique | Rhythm and positions wrong |
| Side (suite) door | conforms (glazing P2 #7) | east_side, side_entry | Door with a lamp beside it |
| Side landing and flight | conforms (railings P2 #7) | east_side, side_entry, right_side | Concrete landing; flight descends south towards the street |
| Downpipes | conforms in placement (joints P1 #1) | front, left_side, east_side, architecture_close | Brown downpipes at the corners |
| Concrete foundation | conforms | east_side, side_entry, left_side, rear_side | Exposed grey band on the sides and rear; brick to grade on the front |
| Lawn | conforms | front, front_corner, top | Front and side lawns |
| Beds and shrubs | conforms | front, entry_stair, top | Mulch bed with shrubs west of the landing, shrubs east of the stair |
| Walks | conforms | top, front_corner, right_side | Front walk from the stair to the sidewalk; side walk from the suite stair to the street |
| Sidewalks | conforms | front, top, aerial | On both streets |
| Boulevards and curbs | conforms (corner return P2 #9) | front, top, aerial | Green boulevards and a curb line on both streets |
| Fence and lattice | conforms | left_side, rear, right_side, east_side | Board fence with a lattice top round the back yard |
| Cedars | conforms | right_side, east_side, top | Row of six cedars at the north-east rear corner |
| Street trees | deviates (P2 #10) | top, aerial, rear_side | Extra boulevard trees not in the sources |
| Materials hierarchy | conforms (roof colour P2 #4) | all envelope views | Brick front ground storey, then white stucco, then brown trim, then concrete base; source palette otherwise respected |
| Faces no source shows (west, north) | coherent | left_side, rear, rear_side, top | Rear upper deck with a slider and posts, back door with stoop, two-by-two west windows; consistent grammar |

## 4. Camera validity

- All 18 renders are valid: in each, the target is in frame, unclipped and legible.
- rear_side: a foreground boulevard tree hides the lower north-east quarter (cedar row, fence corner, part of the lower east wall). The view still reads, and the hidden features are shown in right_side, east_side and rear, so this is logged as P2 #10, not a camera P0.
- aerial: a foreground tree overlaps the south-west front corner, but the landing, stair, balcony and brick front remain legible. No finding.
- interior: legible. It shows the slider, curtains and the balcony railing outside.
- The brief lists `glass_close` twice. One `glass_close.png` exists and there are 18 render files in total.

## 5. Previous-version findings

This is the first version (v001). There are no previous-version findings to carry forward or close.
