# Independent holistic review: clay-halifax-waterfront-warehouse v006 (RLASM v6.1)

Reviewer: independent; did not build the candidate. I judged only rendered pixels against the three locked sources (`sources/front.png`, `sources/oblique.jpg`, `sources/top.jpg`). I opened all 18 renders and the 4 phone boards at full resolution, and made zoomed crops in a new scratch folder (`/tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/hfx6-crops-f98f496d/`). I did not use metadata, build reports or builder notes as proof.

## 1. Verdict

**Verdict: PASS_ZERO_P0_P1**. The v005 P1 is fixed in the pixels: all five ground-storey east arches now have brick voussoir heads with granite sills only. Every earlier fix still holds, and what remains is polish.

Counts: P0 = 0, P1 = 0, P2 = 6

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P2 | east_side (also right_side at close zoom) | In the bay-2 ground triplet, the voussoir rings of neighbouring arches touch at the springing line. Each of the two junctions leaves a small near-black triangular wedge, about 4–6 px, where brick wall should show. | The aperture cutters or ring extrados meet at the shoulders and expose a sliver of the dark carrier or interior behind the 1.5 cm-proud ring. The wall fill does not close the gap between the two rings. | Clip the ring outer radius so adjacent rings stop just short of each other, or fill the shoulder triangle with wall brick. Confirm the cutter does not reach above the springing line between adjacent arches. |
| 2 | P2 | architecture_close, copper_cornice (barely visible in front) | The raised parapet block over the SE corner pier reads as two overlapping boxes: a wide south-face block and a narrower east-face block offset behind it. Their copper copings sit at slightly different levels with a visible seam and step. | The south-face and east-face pier blocks are each generated per facade and overlap at the corner, instead of forming one corner pedestal. | Replace the two corner blocks with a single corner pedestal and one wrapped coping, or merge them to equal height with a mitred coping. |
| 3 | P2 | right_side, east_side, arched_windows, facade_close | Between the modillions under the corona, the background is dark brick-brown wall rather than a copper bed-mould or frieze backing. At façade distance this reads as a continuous dark slot band under the cornice. It is not see-through. | The frieze plate stops below the corona soffit, so the modillion zone exposes the wall or parapet behind. | Extend the copper frieze or bed-mould backing up to the soffit underside in the modillion zone. The modillion blocks stay as they are. |
| 4 | P2 | granite_piers, front, right_side | Pier rustication is only thin incised lines on flat faces. The source shows deeper banded and chamfered rustication with clear shadow lines. | The groove depth and width are minimal. | Deepen and widen the rustication joints, for example with a V or chamfered channel of about 2–3 cm, so the banding casts shadow at whole-envelope distance. |
| 5 | P2 | front, right_side, front_corner vs sources/front.png | The granite reads as pale warm off-white. The source piers and belt are a mid grey-beige, noticeably darker against the brick. The material hierarchy is still legible. | The granite base colour is lifted too high. | Darken the granite clay colour slightly toward the source's mid grey-beige. |
| 6 | P2 | front | Framing is tight on the right: the NE end of the east elevation sits about 25 px from the frame edge and the east tree is cropped. The lower third is mostly empty road. | The camera target and distance are biased to the south front. | Pan or widen slightly so the NE end has margin, and raise the horizon a little. |

There are no P0 and no P1 findings.

## 3. Source conformance checklist

| item | status | view(s) used | note |
|---|---|---|---|
| Silhouette | conforms | front, front_corner, aerial, top vs front/oblique/top | Rectangular two-storey block, deep wrapped copper cornice on the south and east, parapet with raised blocks, flat roof. Plan proportion matches top.jpg. |
| Storey count and proportions | conforms | right_side, front, facade_close | Two storeys. The tall ground storey, granite belt, upper arcade storey, cornice and parapet are in source proportion. |
| Piers (rustication, caps) | conforms (P2 #4) | granite_piers, right_side, arched_windows | Four piers on the south front and four on the east, with granite caps under paired copper consoles. The rustication is shallow. |
| Brick bays | conforms | right_side, east_side, facade_close | Red brick infill between the piers on both street faces. |
| Shopfronts and entrance | conforms | facade_close, glass_close, front, interior | Dark-green framed glazing with transoms and green kick panels. The double door is in the middle south bay with sidelights and transom, on a granite step. The interior has visible depth. |
| Belt entablature | conforms | right_side, facade_close, granite_piers | A continuous granite belt wraps the corner and returns at the NE end and at the west party wall. |
| Arched windows (counts per bay, archivolts, keystones, sills) | conforms | facade_close, east_side, right_side, arched_windows | South front: triplet / one large arch / pair. East, south to north: upper pair / triplet / pair. Ground: shop glazing / arched triplet / arched pair, centred bay by bay. The upper windows have granite archivolts with keystones and imposts. Every arched window has a granite sill and visible reveals. |
| Copper cornice and brackets | conforms (P2 #3) | copper_cornice, architecture_close, right_side | Deep verdigris corona, modillions, frieze, paired consoles and cornice breaks over the piers. The cornice wraps the SE corner, with closed ends at the SW and NE. |
| Parapet, raised blocks and coping | conforms (P2 #2) | aerial, front_corner, copper_cornice, roof_chimneys | Brick parapet with copper coping. Raised blocks over the piers and a raised panel over the middle south bay. The corner block is doubled. |
| East ground windows | conforms | east_side, right_side, front, front_corner | Arched ground windows sit in brick behind the corner shop. The heads are plain rubbed-brick voussoir rings with no granite archivolt or keystone, on granite sills. |
| Roof and chimneys | conforms | top, roof_chimneys, aerial | Flat membrane roof. Two brick chimneys sit on the north (rear) parapet at positions consistent with top.jpg, with small vents and a hatch. |
| Sidewalks, trees and lamp | conforms | top, front_corner, aerial, right_side | Sidewalks on both streets, curb return and crossing, a tree and lamp on the south sidewalk near the west end, and a tree and lamp on the east sidewalk. |
| Neighbour | conforms | top, front_corner, left_side, rear, front | An attached brick neighbour to the west. Its main block stops about 70–75% of the warehouse depth back from the street, with a lower annex and paved alley behind. There is no slit at the party wall. |
| Materials hierarchy | conforms (P2 #5) | front, right_side | Granite frame, then red brick infill, then dark-green joinery, with the verdigris cornice and coping on top. The granite is slightly too light. |
| North and west faces (no source) | coherent | rear, rear_north, left_side, rear_side | Plain brick rear wall with 4×2 rectangular windows on granite sills and a closed NE cornice return. Judged for coherence only. |

## 4. Camera validity

- All 18 views are valid. None has the target occluded or the asset clipped in a way that hides an identity element.
- **front**: framing is tight at the NE end and the east tree is cropped (P2 #6). The whole building is still in frame and legible.
- **right_side**: the east tree canopy overlaps part of the bay-3 upper pair. The windows behind it are verified unobstructed in east_side, so this is not a defect.
- **glass_close, rear_north and interior** are deliberately close crops, and each one shows what it is meant to show.
- **top**: true plan view. It is legible and matches top.jpg in orientation: street south, side street east, neighbour west.

## 5. Previous-version findings: resolved in the pixels?

| previous finding | status | evidence |
|---|---|---|
| v005 P1: five east ground arches (bay-2 triplet and bay-3 pair) had grey granite archivolts copied from the upper storey | **Resolved** | In east_side and right_side, all five ground arch heads are rubbed-brick voussoir rings with radial joints. They are slightly redder than the wall, have no keystone or impost blocks, and sit on granite sills. In front (zoomed), the heads read as brick with no grey ring. In front_corner and aerial the heads sit under the belt overhang, and no grey ring is visible. The upper granite archivolts, keystones and imposts and the south front are unchanged. A tiny shoulder wedge remains (P2 #1). |
| v004: east elevation per bay, south to north, upper pair / triplet / pair over ground shop glazing / arched triplet / arched pair, centred bay by bay | Holds | In right_side and east_side each upper group is centred over its ground group within its bay. |
| Back of every wrapped cornice overhang closed (SW end past the west wall, NE return), no black slots | Holds | In front (SW zoom) and front_corner/aerial (SW zoom), the SW cornice end is closed over the neighbour roof. In rear and rear_side (NE zoom), the NE return is closed with end faces and no black slot. |
| West neighbour main block stops about 70% of the depth back, with a lower annex and alley behind, and no slit at the party wall | Holds | In top, the main block covers about 70–75% of the depth, then a shallow annex, then paved alley. left_side and rear show the annex and alley. In front, front_corner and aerial there is no slit at the party wall. |
| Arch spandrels flush, no rectangular shoulder recess (especially the large middle south arch) | Holds | In facade_close (zoom on the large arch), arched_windows and east_side, the spandrels are flush brick with no rectangular recess. |
| Entrance door on a granite step; frieze with paired consoles and cornice breaks over the piers; corner-pier clearance; curb return and crossing; framed views | Holds | facade_close shows the step. right_side, east_side and architecture_close show the consoles and breaks. In front, granite_piers and top, the lamp and trees are clear of the corner pier. top and front_corner show the curb return and crossing. Framing is acceptable (see P2 #6). |
