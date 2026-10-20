# Independent holistic review: clay-halifax-waterfront-warehouse v005 (RLASM v6.1 architectural clay)

Reviewer: independent, adversarial. I judged only rendered pixels against the three locked sources (`sources/front.png`, `sources/oblique.jpg`, `sources/top.jpg`). I opened all 18 renders and the 4 phone boards at full resolution. Zoomed crops (read-only derivatives) are in `/tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/hfxwh-v005-indep-crops-aecade08/`.

## 1. Verdict

**VISUAL_REWORK_REQUIRED**: the v004 east-elevation count defect is fixed, and every earlier fix still holds in the pixels. One P1 material-fidelity defect remains: the arched ground windows on the east side carry grey granite archivolts, but both sources show plain brick arch heads there.

Counts: P0 = 0, P1 = 1, P2 = 9

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | east_side, right_side, front, front_corner, aerial | All five arched ground windows on the east elevation (bay 2 ground triplet, bay 3 ground pair) have thick light-grey archivolt rings. The sampled ring colour is about RGB 97-111 neutral grey, the same as the granite. In both sources these ground arches are plain brick arch heads with no stone ring (front source x≈800-900 / y≈470-620; oblique x≈840-1000 / y≈470-560). Only the sills are stone. As a result the ground windows read as copies of the upper windows, and the source's material hierarchy is lost: granite archivolts with keystones belong to the upper storey, plain brick arches to the ground storey. | The ground-arch assembly reuses the upper-storey archivolt component and the granite material. The v005 bay-3 rework ("brick-arched windows") was also built with that component. | Change the ground-storey arch ring on all five east ground windows to a flush or slightly proud brick (rubbed-brick) voussoir ring in the brick colour, or drop the ring and let the brick wall form the head. Keep the granite sills. Leave the upper-storey archivolts unchanged. Re-render east_side, right_side and front_corner. |
| 2 | P2 | architecture_close, copper_cornice | The raised parapet block at the south-east corner has two copper cap slabs (the south cap and the east cap) that lap with a visible offset seam. | Two corner blocks, one per elevation, overlap at the corner. | Use one corner block with a single cap. |
| 3 | P2 | facade_close, arched_windows | The extrados of the large middle-bay arch's archivolt is visibly faceted (about 12 straight segments). | Low segment count on the arch ring. | Raise the arch segment count to 32 or more. |
| 4 | P2 | right_side, east_side, front | The belt entablature is a plain band with one ledge, and the ground piers run into it with no cap. The source shows a three-part entablature (architrave, frieze, cornice) and moulded pier caps. | Simplified profile. | Add an architrave step and a cap ring on each ground pier. |
| 5 | P2 | rear_side, copper_cornice | The cornice breaks over the piers are separate corona plates set higher and lapping onto the bay plates, so the cornice top reads as stepped shingles. The source has a continuous corona with shallow breaks. | Each break is a separate slab placed on top. | Make each break a shallow forward projection that sits flush with the bay corona's top surface. |
| 6 | P2 | facade_close, front | The middle-bay entrance is symmetric: sidelight, double door, sidelight. The source shows the door assembly filling the bay under a large transom, with at most one narrow side panel. | Generic entrance template. | Widen the double door and transom. Optionally remove one sidelight. |
| 7 | P2 | east_side, right_side | The east-street tree canopy covers part of the bay-3 upper pair (the north window and its lower half). Counting is still possible. | The tree sits in the camera's line of sight. | Nudge the east_side and right_side cameras, or move the tree slightly. |
| 8 | P2 | top, front_corner, aerial | The east-street tree stands near the north end of the east face. The top source has it near mid-depth, roughly in front of bays 2 and 3. | Tree placement. | Move the tree about 25-30% of the depth southward, keeping the corner-pier and lamp clearances. |
| 9 | P2 | left_side (≈1255,390) | A tiny black notch shows at the junction of the west coping and the south-west raised block. | A small gap between the coping and the block. | Extend the coping by a few centimetres into the block. |
| 10 | P2 | rear, rear_north, left_side | The north elevation has plain flat-headed windows with no lintels or arches. No source shows this face, so it is judged for coherence only. It is coherent but bare. | Minimal rear grammar. | Optional: add brick segmental or stone lintels over the rear windows. |

## 3. Source conformance checklist

| item | status | view(s) used | note |
|---|---|---|---|
| Silhouette | conforms | front, front_corner, aerial, top | Two-storey block with a deep cornice, a parapet with blocks, a raised middle panel and two north chimneys. Plan aspect is about 1.43 in the render and about 1.44 in the top source. |
| Storey count and proportions | conforms | right_side, front | Two storeys. Measured shares of total height: ground ≈41% (source ≈36%), belt ≈8% (≈9%), upper ≈36% (≈34%), cornice ≈12% (≈16%). Within clay tolerance. |
| Piers (rustication, caps) | conforms with minor deviation | granite_piers, right_side, facade_close | Rusticated grey granite piers at every bay division and at the corners, with paired consoles on top. Ground pier caps are missing (P2 #4). |
| Brick bays | conforms | facade_close, east_side, right_side | Red brick infill between the piers on both street faces. |
| Shopfronts and entrance | conforms | facade_close, glass_close, interior, front | Dark-green framed glazing with transoms and green stallboards. Double entrance door in the middle south bay on a granite step. Glazing has depth and interior. Sidelight arrangement is P2 #6. |
| Belt entablature | conforms with simplification | right_side, east_side | Continuous granite belt at the floor line. Profile simplified (P2 #4). |
| Arched windows: south front | conforms | front, facade_close, right_side | Triplet, one large arch and a pair, each with a granite archivolt, keystone and stone sill. Spandrels are flush. |
| Arched windows: east side, per bay (south to north) | conforms | east_side, right_side, front, front_corner, aerial | Upper: pair / triplet / pair. Ground: shop glazing (2 lights) / arched triplet / arched pair. This matches both sources. The ground triplet and pair are centred under the upper triplet and pair. |
| Archivolts, keystones, sills | conforms upper / deviates ground | east_side, arched_windows | Upper storey correct. Ground arches wrongly in granite (P1 #1). |
| Copper cornice and brackets | conforms | copper_cornice, architecture_close, east_side, rear_side | Deep verdigris cornice with modillion brackets, frieze, paired consoles and breaks over the piers. Wraps the south-east corner. Stepped-plate look is P2 #5. |
| Parapet, raised blocks and coping | conforms | aerial, front_corner, roof_chimneys, right_side | Brick parapet, copper coping, raised blocks over the piers, raised stone panel over the middle south bay. Corner cap seam is P2 #2. |
| East ground windows | deviates (material) | east_side, right_side | Arched and in brick walls as the source shows, with correct counts, but the arch heads are granite rather than brick (P1 #1). |
| Roof and chimneys | conforms | top, roof_chimneys, rear, aerial | Flat membrane roof with small vents. Two brick chimneys straddle the north parapet at about 34% and 67% of the width; the source has them at about 30% and 67%. |
| Sidewalks, trees and lamp | conforms with minor placement deviation | top, front_corner, aerial, front | South and east sidewalks with a curb return and crossing. Trees on the south-west sidewalk and on the east street. Lamps on both streets. East tree position is P2 #8. |
| Neighbour | conforms | top, front, left_side | Brick neighbour attached on the west, lower than the warehouse. Its main block stops about 71% of the depth back from the street, followed by a lower annex and an alley. No slit at the party wall. |
| Materials hierarchy | deviates (one item) | east_side, right_side | Granite piers, belt and archivolts; brick bays and parapet; verdigris copper cornice and coping; dark-green frames. The only break is granite on the ground-storey east arches (P1 #1). |

## 4. Camera validity

All 18 views are valid. In each one the target is legible, unclipped where it matters, and not blocked by a camera artefact.
- **left_side** looks mostly at the north face and the west neighbour. This is expected, because the west face is a party wall. The exposed rear part of the west wall, above the annex, is visible.
- **east_side** and **right_side**: a tree partly covers the bay-3 upper pair, but the windows can still be counted (P2 #7).
- **interior** reads correctly as the inside of the middle-bay door assembly and the east-bay shopfront.
- **glass_close** shows a framed shopfront with visible depth.

## 5. Previous-version findings: status in the pixels

| previous finding | status | evidence |
|---|---|---|
| v004 P1: east elevation window counts (render had pair/pair/pair over shop/triplet/triplet; sources show pair/triplet/pair over shop/triplet/pair) | **Resolved** | east_side, right_side, front, front_corner and aerial all show upper pair / triplet / pair over ground shop glazing / arched triplet / arched pair. Bay 2's upper triplet has narrower windows with slimmer archivolts, keystones, imposts and sills, centred over the ground triplet (centres line up at x≈600/720/840 in east_side). Bay 3's ground pair is centred under the upper pair (x≈1140/1320). Pier positions are unchanged. The new bay-3 ground pair has the same granite-ring material defect as the bay-2 ground triplet (P1 #1). |
| Back of the wrapped copper cornice overhangs closed (south-west end past the west wall, north-east return), no black slots | **Holds** | rear and left_side, north-east end: solid closed end with no slot. left_side, south-west overhang seen from behind: closed back face. front, south-west end: closed. Only a pinhead notch at the coping and block junction remains (P2 #9). |
| West neighbour's main block stops about 70% back, lower annex and alley behind, no slit at the party wall | **Holds** | top: main block ≈71% of depth, annex band, paved alley. left_side: annex and alley visible, junction tight. front: neighbour meets the south-west pier with no gap. |
| Arch spandrels flush, no rectangular recess at the arch shoulders (especially the large middle-bay arch) | **Holds** | facade_close, arched_windows and east_side: brick runs flush to every archivolt, with no shoulder recesses. |
| Entrance door on a granite step | **Holds** | facade_close and front: the double door sits on a projecting granite step. |
| Frieze with paired consoles and cornice breaks over the piers | **Holds** | east_side, facade_close, right_side and copper_cornice. |
| Corner-pier clearance, curb return and crossing, framed views | **Holds** | front_corner and top: clear corner pier, radiused curb return, zebra crossing on the side street. All whole-envelope views are framed with margin. |
