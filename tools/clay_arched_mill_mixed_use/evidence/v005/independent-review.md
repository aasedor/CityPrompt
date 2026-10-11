# Independent RLASM v6.1 holistic review: mill v005

Reviewer: independent (did not build). Evidence: sources/front.png, sources/oblique.jpg, sources/top.jpg; all 18 renders at 1440x1080; boards phone-01..04. No build code, reports or builder notes were read.

## 1. Verdict

**PASS_ZERO_P0_P1** (P0 = 0, P1 = 0, P2 = 8). The v004 P1 is fixed in the pixels. On both eave faces the top-storey windows now show segmental arched heads with a brick head and a strip of brick below the dentil course. Every remaining defect is polish. None of them changes identity, topology, openings, contact or camera validity.

## 2. Findings table

No P0 or P1 findings.

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P2 | front (gable ~x400-1040, apex y~328, eave coping y~435); rear; chimney_contact | Gable rise is about 107 px over a 458 px wall height (ratio ~0.23). The source front gable gives about 112 px over ~365 px (ratio ~0.31). The roof is about 25% flatter than the source, and the raked gable silhouette reads squat. | Main roof pitch set too low | Raise the ridge so rise/eave height is ~0.30 (roughly 33-35 deg). Re-seat the gable coping and pilaster tops to the new rake. |
| 2 | P2 | top (roof field x720-1000), aerial, rear_side | The slate field is a light blue-grey, average about (115,119,125). The source slate is dark charcoal, about (75,74,82) in top.jpg. Contrast between slate and glass pavilion is weaker than in the source. | Slate palette value too light | Darken the slate swatch about 30-35% toward the source charcoal. Keep it cooler than the brick. |
| 3 | P2 | roof_pavilion (x310-975, y400-560); left_side (x160-1080, y330-440); front_corner | The glazed pavilion reads as a flat-topped box with only a very shallow hipped top. In the oblique source, the glass roof is a clearly raked plane rising from the front glazed wall toward the ridge. | Pavilion roof pitch too low | Give the pavilion roof a monopitch, or a raked plane parallel to the main slope at a visibly steeper angle, with glazing bars running down the slope. |
| 4 | P2 | top (rooflights x780-910, y360-610), aerial, rear_side | All four rooflights sit as two pairs on the slope opposite the pavilion. In top.jpg two rooflights sit beside the pavilion on its own slope (~x600-660) and two sit on the other slope (~x705-770), staggered rather than in a grid. | Rooflight layout not traced from the top source | Move one pair to the strip between the pavilion and the ridge. Stagger the other pair to match top.jpg. |
| 5 | P2 | roof_pavilion (~x800-835, y695-715; visible in zoom) | A small terracotta wedge shows between the pavilion terrace deck edge and the cut edge of the slate field. Bare substrate is visible at the slate cut. | Slate cut-out around the deck not closed against the deck upstand | Extend the slate or the deck upstand to close the wedge, or add a flashing strip along the cut. |
| 6 | P2 | front (whole-envelope set) | The front camera is a square-on gable elevation. The locked front source is a street-level south-west three-quarter view of the corner, showing the eave face and gable together. corner_entry covers the street corner but is a close crop, not a whole-envelope match. | Camera role not matched to the source front | Add or replace with a street-level three-quarter camera matching the source front composition (corner near left-centre, about 35 mm, eye ~1.6 m). |
| 7 | P2 | interior (left window head, x30-300, y85-95) | A dark trapezoid sits between the flat top of the glazing frame and the soffit of the segmental arch. The arch void is unglazed and reads as a black sliver. | Glazing and frame are rectangular, while the arched head opening is taller | Fit the glass and frame head to the segmental arch, or add an arched fanlight panel. |
| 8 | P2 | front (gable apex ~x720, y~330), fr zoom | At the ridge, the two raking coping pieces meet with a tiny dark notch rather than a closed apex or apex stone. | Coping segments mitred short at the apex | Extend and mitre the copings to meet, or add a small apex block. |

## 3. Source conformance checklist

| item | status | view used | note |
|---|---|---|---|
| Silhouette | conforms (minor deviation, see P2-1) | front vs source front; front_corner vs oblique | Near-square four-storey block, gable on the short face and chimney rising behind at the NE corner. The rake is somewhat low. |
| Storey count | conforms | left_side, front, rear, corner_entry | Ground floor plus three upper storeys. The stone band sits over the ground floor. |
| Bay rhythm and pilasters | conforms | left_side (4 bays), front (4 bays + door), corner_entry | Full-height pilasters frame each bay. The gable-face pilasters run up into the rake as in the source. The ground-floor door is at the right end of the gable face as in the source. |
| Arched openings | conforms | facade_close, arched_windows, shopfront, glass_close, corner_entry, architecture_close | Segmental arched heads with brick heads on all three upper storeys, the top storey included. Arched shopfronts with dark frames sit between piers. Reveals and returns are visible. |
| Cornice and band | conforms | architecture_close, left_side, corner_entry, facade_close | Stone sill band over the ground floor. The dentil cornice under the eave parapet ends cleanly against the corner pier. |
| Roof and gables | deviates (P2 only) | front, top, aerial, chimney_contact | Slate roof pitched from a ridge on the long axis to raked coped gable parapets. Pitch, tone and rooflight layout are polish deviations (P2-1, P2-2, P2-4). |
| Pavilion and chimney | conforms (pavilion roof pitch P2-3) | roof_pavilion, left_side, front_corner, chimney_contact | Glazed pavilion with a terrace rail on the front slope at the western end. A tall square brick chimney with a stone cap sits at the NE corner, with clean roof contact and no float or intersection gap. |
| Materials hierarchy | conforms | all | Brick body, pale stone sills, band, cornice and coping, dark window frames, grey slate and clear glass. The ordering matches the source. Slate is slightly light (P2-2). |

North face (right_side, rear_yard): no source shows it. It follows the visible grammar (arched windows, pilasters, band, cornice, service door) and is coherent.

## 4. Camera validity

All 18 views are valid. The target is never fully occluded or clipped and every view is legible. In shopfront, a tree trunk covers the left edge (x80-300) but the arched shopfront stays fully readable. In corner_entry and facade_close the trees overlap only peripheral bays. Only P2-6 is noted: the whole-envelope front is not a three-quarter match to the source front.

## 5. v004 findings status (judged from v005 pixels)

| v004 finding | sev | status | evidence |
|---|---|---|---|
| Top-storey windows on both eave faces read as plain rectangles running into the dentil course | P1 | **resolved** | left_side y~505-570: arched heads with a brick head and a brick strip under the dentils. architecture_close x100-610 y445-500. chimney_contact x820-1100 y850-900. right_side y~505. |
| Glasshouse roof pitch low | P2 | not resolved | roof_pavilion and left_side show a near-flat top (P2-3) |
| Rooflight positions | P2 | not resolved | top shows a 2x2 grid all on the non-pavilion slope (P2-4) |
| Cornice ends cut square past the gable plane | P2 | resolved | architecture_close ~x685 y350-400: the cornice stops against the corner pier and does not pass the gable plane |
| Small gap at the slate cut | P2 | not resolved | roof_pavilion wedge at ~x800-835 y695-715 (P2-5) |
| Main roof pitch and slate tone | P2 | not resolved | P2-1 and P2-2 |
| No street-level south-west three-quarter front camera | P2 | partly | corner_entry adds a street-level corner close-up. There is still no whole-envelope three-quarter view (P2-6). |
| Dark sliver at one interior window head | P2 | not resolved | interior x30-300 y85-95 (P2-7) |
