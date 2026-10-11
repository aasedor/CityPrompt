# Independent RLASM v6.1 holistic review: slab v005

Reviewer: independent. I judged only the locked sources (front.png, oblique.jpg, top.jpg), the 18 renders and the 4 phone boards, all opened at full resolution, with crops of the roof edge, corner trays and base. I did not read any build code, reports or builder notes.

## 1. Verdict

**VISUAL_REWORK_REQUIRED.** The balcony trays now cantilever past the fins and wrap the corners correctly. But the roof edge is a plain, thick, unnotched square cornice ring. The locked oblique shows something different: a low brick-and-teal-banded parapet, a thin projecting top slab, a stepped outline and fin heads rising above the roof. This is one clearly visible P1 in the matched oblique and top roles.

**Counts: P0 = 0, P1 = 1, P2 = 7**

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | **P1** | aerial (approx. x 430-1020, y 200-700), front_corner (x 455-985, y 185-610), top (ring x 418-1022, y 238-840), roof_penthouse (x 90-1440, y 620-1080), rear_side (x 450-1000, y 200-600) | The roof edge is one uniform, thick, flat white square ring at the same depth on all four faces. It runs straight over the recessed centre brick bay, so the centre bay sits under an overhanging cornice (aerial crop: the ring edge passes over the brick strip at about x 560-600, y 560-760). The roof outline is a pure square. The only "notching" comes from the outer-bay trays one floor below, which peek out about 15 px beyond the ring in top.png (for example x 400-418 and 1022-1035, and the top edge y 222-238). The ring has no material change. The concrete bay-line fins and corner piers stop beneath the ring. | The crown was modelled as one offset square slab and parapet. It was not derived from the per-bay slab plan used for the floors below. | Rebuild the crown from the typical floor plan. (a) Make the top slab a thin ledge that projects only over the outer bays, wrapping the corners like the trays below. Over the centre bay, step it back to the brick face so the roof outline is visibly notched in top/aerial, matching the top.jpg south and east steps. (b) Set a low parapet on the building line behind that ledge. Give its outer face the brick band with the thin teal stripe that oblique.jpg shows (crop x 80-660, y 300-480). (c) Extend the bay-line fins and corner piers about 0.5-1 m above the parapet as concrete fin heads (oblique.jpg x 660-715 and 830-880, y 290-340). (d) Reduce the crown thickness to match the floor slab-edge depth. Re-render top, aerial, front_corner, rear_side and roof_penthouse. |
| 2 | P2 | front (centre bay x 665-770, y 190-830), left_side (x 520-910 at most floors), right_side, facade_close (x 940-1100, y 380-440 and 590-640), glass_close (x 620-1180, y 0-110 and 470-590), rear_lane (x 700-1000, y 40-110) | Soft white elliptical blooms sit in the glazing on most floors. They read as lamp glare smeared on the glass, not as sky reflection. | Interior ceiling emitters or a glossy plane reflecting a point light into a low-roughness glass shader | Remove or dim the interior emitters, or raise glass roughness. Alternatively, use a uniform sky-tinted reflection for the clay palette. |
| 3 | P2 | top (units x 515-565/y 375-415, x 515-565/y 665-705, x 865-912/y 688-728), aerial, roof_penthouse (x 340-450, 640-770, 1170-1280) | Four rooftop units are spread to three roof corners, far from the penthouse. The sources (oblique x 480-800, y 245-330; top x 610-740, y 265-430) cluster the AC units and plant hard against the east and south sides of the penthouse, with two low hatch boxes in front of its south face. | Units placed on a symmetric corner grid | Cluster the units against the penthouse's east side. Add the two low hatch boxes on its south side, as in top.jpg x 460-500/555-660, y 360-560. |
| 4 | P2 | top (x 825-912, y 420-515), aerial (crop x 590-720, y 320-470), rear_side (x 637-705, y 390-470), roof_penthouse (x 965-1000, y 605-720) | The penthouse is still a cluster of three volumes: the main box, a taller rear block and a lower annex with a door on the east. Both sources show one simple box (the oblique has a single cube with a louvre and a door). | Stair/lift overrun modelled as separate add-on boxes | Merge into one rectilinear two-storey box. At most keep a flush door recess. |
| 5 | P2 | front (centre bay jambs x 660-668 and 768-776 on every floor), facade_close (x 1100-1140, full height), right_side, rear | Brick still runs up both jambs of the centre-bay window band, so each window reads as framed in brick on three sides. The source front (x 655-730) shows brick only as the spandrel band under each window, with the glazing running fin to fin. The heads are now clear. | Brick jamb strips kept in the centre-bay module | Remove the vertical brick jamb strips. Let the window band meet the concrete fins directly and keep only the horizontal spandrel. |
| 6 | P2 | base_corner (tree x 750-1210, y 300-1080) | The low-poly tree still stands directly in front of the entry canopy and right-hand ground-floor bay. It hides about a quarter of the detail view's subject. The corner pier and recessed base stay legible. | Tree placed on the camera axis | Move the tree about 4 m east along the kerb, or move the camera. |
| 7 | P2 | interior (whole frame) | The camera still sits right at the pane. The frame shows only a window, one mullion, the head and the sill. No floor, ceiling, walls or room depth is legible. The view does still show frame depth. | Camera inside the window reveal | Pull the camera back 3-4 m into the room and widen the FOV so the floor, ceiling, slab edge and balcony beyond read. |
| 8 | P2 | lobby_entry (x 0-300, 470-660, 860-960, y 360-790), fin_contact (x 90-470, y 400-890), front (base x 520-905, y 880-950) | The recessed ground-floor glazing renders as near-black opaque panels. The source front (x 425-715, y 565-645) shows transparent storefront glazing with lit interiors and mullions. | Glass shader too dark or backed by an unlit volume | Lighten the glass tint, add a mullion grid and add a simple lit lobby interior volume. |

Notes. The fin_contact canopy's upturned fascia block (x 610-1030, y 300-420) sits just under the first-floor soffit without a visible gap or clash. It is not a contact defect, but a flat canopy would be simpler. I found no floating, intersecting or clipped parts.

## 3. Source conformance checklist

| Item | Status | View(s) used / note |
|---|---|---|
| Silhouette | **deviates** | top, aerial, front_corner vs top.jpg / oblique.jpg: the tower and tray massing is right, but the roof crown is a plain thick square ring with no stepped outline or fin heads (Finding 1). |
| Storey count | conforms | front, left_side, right_side, rear: 12 stacked balcony/slab levels over the recessed ground floor, plus the roof slab. This is within the 12-13 read from the oblique. |
| Balcony stacks and slab bands | conforms | front (trays at x 458-512 and 965-980 cantilever past the corner piers, with glass end returns), front_corner, base_corner, architecture_close (glass runs continuously round the corner pier): trays now project past the fin fronts and wrap the corners. The exposed slab edge shows on every storey. The projection is somewhat shallower than the oblique suggests (P2-level, not raised separately). |
| Fins and corners | conforms (below the roof) / deviates at the crown | front, facade_close, fin_contact, base_corner: full-height fins at the bay lines, and corner piers carried to the ground. They do not rise above the roof as the oblique shows (Finding 1). |
| Centre-bay spandrels and windows | conforms with P2 | front, facade_close, glass_close, lobby_entry, rear_lane: a brick spandrel under a continuous window band on every floor. Brick jamb strips remain (Finding 5). |
| Recessed ground floor and lobby | conforms with P2 | front, fin_contact, lobby_entry, base_corner: columns carry the slab, the glazing is set back, and there is an entry canopy. The glazing is too dark and opaque (Finding 8). The rear (rear_lane) has a brick service base with a garage door, which is coherent with the grammar on an unseen face. |
| Penthouse and roof plant | conforms with P2 | roof_penthouse, left_side, aerial, top: a concrete penthouse about two storeys tall, with a louvre and a door, near the roof centre. It has an annex (Finding 4), and the plant is dispersed (Finding 3). |
| Materials hierarchy | deviates (roof edge only) | aerial, front_corner: the concrete/brick/glass hierarchy is correct on the shaft. The parapet lacks the brick-and-teal band that the oblique shows (Finding 1). |

## 4. Camera validity

- All 8 whole-envelope views (front, front_corner, aerial, top, left_side, right_side, rear, rear_side) are valid. The target is fully in frame, unclipped and legible.
- base_corner: valid. The tree partly occludes the entry side (P2, Finding 6).
- interior: borderline. Only the window pane and its frame are legible, with no room context (P2, Finding 7).
- facade_close, architecture_close, glass_close, balcony_close, fin_contact, lobby_entry, roof_penthouse, rear_lane: valid and legible.

## 5. Prior-version (v004) findings, judged from v005 pixels

| v004 finding | Status | Evidence |
|---|---|---|
| P1: outer-bay balcony plates stopped at the fin fronts and corner piers (framed box with loggias). The sources show trays cantilevering past the fins and round the corners with glass end returns, notching the roof outline. | **partly resolved** | Resolved in elevation. In front (x 458-475 and 965-980), front_corner, base_corner and architecture_close, the trays run past the fins and corner piers with glass end returns and wrap the corners. Not resolved at the roof. top/aerial show the roof outline as a plain square crown ring that overhangs the centre bay; only about 15 px tray slivers notch it. Carried forward as Finding 1 (P1). |
| P2: soft white highlights in the glazing | not resolved | front centre bay, left_side, facade_close, glass_close (Finding 2) |
| P2: rooftop units far from the penthouse | not resolved | top, aerial, roof_penthouse: four units at the roof corners (Finding 3) |
| P2: penthouse annex | not resolved | top x 825-912, aerial, rear_side, roof_penthouse (Finding 4) |
| P2: brick ringing every centre-bay window | partly resolved | Heads are clear. Brick jamb strips remain on both sides (Finding 5). |
| P2: tree in front of the base corner | not resolved | base_corner x 750-1210 (Finding 6) |
| P2: interior camera too close to the glass | not resolved | interior: the frame is filled by one pane (Finding 7) |
