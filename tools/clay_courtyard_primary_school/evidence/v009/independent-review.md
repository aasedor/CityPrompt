# Independent holistic review: clay-courtyard-primary-school v009 (RLASM v6.1)

Reviewer basis: the three locked sources (sources/front.png, sources/oblique.jpg, sources/top.jpg), all 18 renders at full resolution plus enlarged crops, and the four phone boards. I did not read any build reports, metadata or builder notes. The pixel coordinates below refer to the 1440x1080 renders unless a source is named.

## 1. Verdict

**PASS_ZERO_P0_P1.** The brick U, the playground, the coloured fins, the corten third storey, the deep corten canopy over the concrete corner wall, the street-facing lined entrance and the railed roofs all match the locked sources. Every remaining defect is polish.

Counts: P0 = 0, P1 = 0, P2 = 7

## 2. Findings table

| # | severity | view(s) with pixel regions | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P2 | facade_close x735-810 y600-760; entrance_passage x820-910 y465-670; playground x1290-1410 y370-560; canopy_contact x1345-1440 y650-770 | The open concrete stair in the passage climbs to the passage soffit. No stairwell void or landing shows at its head, so the top flight seems to run into the ceiling. | The stair mesh was placed without cutting a slab opening, or the opening is not visible from below. | Cut a visible stairwell void in the first-floor slab above the top flight (or put the stair behind the lobby glazing), and give the stair a landing that meets the slab edge. |
| 2 | P2 | front x675-720 y448-492; aerial x650-710 y465-500; penthouse_terrace x1125-1295 y565-720; top x683-725 y560-600 | A brick-coloured roof box about one storey tall stands on the terrace at the north-west corner of the courtyard and breaks the front roofline. The top source shows no such box there (top.jpg ~x480-500 y440-470 is plain paving). | A stair or lift overrun was added on the builder's own initiative. | Lower it to a flush hatch or skylight, or move it behind the corten block where it does not break the front silhouette. |
| 3 | P2 | top x395-585 y615-915; aerial x190-560 y450-600 | The west wing roof is one uniform gravel field. Both sources show two raised skylight or rooflight boxes on it (oblique.jpg x215-330 y330-380; top.jpg x315-440 y555-660). | The rooflight volumes were left out. | Add the two low raised rooflight boxes with concrete upstands where the sources show them. |
| 4 | P2 | front_corner x920-1000 y600-680; courtyard x1085-1225 y660-945; architecture_close x500-530 y830-1020 | The canopy rests on two or three chunky square concrete posts. The oblique source shows one slender column (oblique.jpg x512-522 y610-680) plus the corner wall. | The post section and count are generic. | Use a single slender round or square steel column at the outer canopy corner, plus the concrete wall. |
| 5 | P2 | right_side x340-415 y607-672; rear_side x235-260 y600-650 (gap between the corner wall's north end and the entrance block) | The canopied forecourt between the corner wall and the entrance block is open to the east pavement, and there is no fence or gate across it. The oblique source also shows paving here (oblique.jpg x800-860 y640-700), so the geometry is fine. Only the enclosure of the yard is unclear. | The yard-security line was not continued across the forecourt. | Add a low fence or gate on the line of the forecourt behind the wall, or confirm that the open forecourt is intended. |
| 6 | P2 | rear x783-795 y600-670; rear_side x1000-1300 y560-700 | The step in the north boundary between the hall and the north-west block leaves a narrow notch. Two storeys of fin-dressed windows face into that notch beside a party wall, and a yellow fin shows through the gap in the rear elevation. | The facade grammar was applied to every exposed face. | Make the notch face blank brick (party-wall grammar), or close the notch so the hall meets the north boundary. |
| 7 | P2 | front x345-660 y420-485; penthouse_terrace x0-1015 y385-850; left_side x240-712 y418-495 | The corten storey is a smooth, uniform orange. The oblique source shows vertical standing-seam panels with a darker weathered tone (oblique.jpg x440-620 y230-330). | Flat clay material, with no panel module beyond faint joints. | Strengthen the vertical panel joints, or step the module slightly, to read as corten cassettes. Clay finish only. |

There are no P0 or P1 findings.

## 3. Source conformance checklist

| item | status | views used |
|---|---|---|
| Silhouette | conforms. The corner plot is mid-block, with party walls to the west and north, the lower U in front and the corten box at the north-west. The only extra element in the front roofline is the roof box in finding 2. | front, front_corner, aerial vs front.png and oblique.jpg; top vs top.jpg |
| Storey count | conforms. The wings are two storeys, the hall is two storeys and the corten third storey sits over the north-west block only. | front, right_side, left_side, rear |
| Courtyard and wings | conforms. The brick U opens south to the playground. Its proportions match top.jpg: the courtyard is about 0.34 of the plot width in the render against 0.33 in the source. The playground has a green mat and play houses. | top, aerial, courtyard, playground |
| Entrance passage and canopy | conforms. The corner concrete wall sits wholly under the deep corten fascia, with the fascia overhanging it on the south and east (aerial crop, right_side crop, entrance_passage). The east face of the entrance block now has a concrete-lined opening with visible returns and recessed glazed doors under the brick upper storey. The ground floor of the passage is open toward the yard. | entrance_passage, facade_close, right_side, rear_side, aerial, canopy_contact |
| Fins and glazing | conforms. Strip windows carry red, yellow, green and teal fins on both storeys of the courtyard and street faces. Courtyard classrooms have full-height glazing, the frames are recessed and the fins have depth. | glass_close, fins_close, interior, courtyard, right_side |
| Corten storey | conforms. The south face is solid corten with a door and the east face is a glazed band, matching oblique.jpg. The roof has rails and plant boxes. | aerial, rear_side, penthouse_terrace, architecture_close |
| Roofs and rails | conforms, with minor deviations. Gravel roofs and the paved hall terrace have perimeter rails. The west wing rooflights are missing (finding 3) and there is an extra roof box (finding 2). | top, aerial, penthouse_terrace |
| Materials hierarchy | conforms. Tan brick is the field, light concrete forms the slab bands, parapets and corner wall, corten forms the canopy and third storey, and the fins are coloured. The corten finish is slightly flat (finding 7). | all |

## 4. Camera validity

All 18 views are valid. No target is occluded, no asset is clipped and every view is legible. left_side and rear show party-wall elevations, which are correctly blank. The detail views (entrance_passage, canopy_contact, facade_close, playground) each frame their subject without obstruction.

## 5. Previous-version findings

- **v008 P1, passage read as a slot beside the wall, with a classroom window on the entrance block's east ground floor:** RESOLVED. right_side (x428-522 y597-672, crop at 4x) shows a lined concrete opening under the brick upper storey and the first-floor band. It has a visible left return and three-panel glazed doors set back inside it. rear_side (x260-305 y600-650) and aerial (x845-890 y750-800) show the same recess from the north-east and south-east. There is no classroom window between the corner and the opening. The ground-floor windows begin only beyond it, as in front.png x850-970.
- **v008 P1, corner concrete wall read as a separate box as tall as the canopy, with its top exposed:** RESOLVED. In entrance_passage (x965-1175 y420-760) the wall rises to the canopy soffit, and the corten fascia passes over it to the corner at x1215. In aerial (crop x605-800) the wall's top is entirely covered by the canopy deck. In right_side (x305-365 y607-672) the fascia overhangs the wall on the street face. The yard fence returns to the wall's south-west corner (aerial x710-760 y820-880).
- **v007 findings previously verified (deep fascia, ground-floor fins, corten storey glazed band):** still resolved in v009 pixels. The fascia is deep in facade_close and canopy_contact. Ground-floor fins appear in courtyard, interior and right_side. The east glazed band shows in aerial x700-880 y370-470 and rear_side x800-1000 y440-530.
- **v008 P2s (not individually named in the brief):** not assessed individually. The current P2 list above stands on its own.
