# Independent holistic review: clay chamfer-corner dome block, v008

## 1. Verdict

**VISUAL_REWORK_REQUIRED.** The bowed bay, the eye-level chamfer camera and the projecting dome-foot disc are fixed. Three dome identity elements still do not match the source pixels: the dormers are blank discs, the ribs are segmented, and the cresting is a hairline fence.

Counts: P0 = 0, P1 = 3, P2 = 7

Inputs inspected at full resolution: sources/front.png, sources/oblique.jpg, sources/top.jpg; all 18 renders; boards phone-01 to phone-04. I also used crops of the source dome (oblique x480-760, y220-620) and the render dome (chamfer_dome x500-940, y280-700; top x360-660, y620-900).

Storey-count note: the brief's prose says "five-storey ... three storeys of brick". The locked sources show a ground floor plus two upper storeys under the cornice: source front, left wing, window rows at about y440-520 and y330-410; oblique, left wing, the same two rows above the continuous balcony. The render also has a ground floor plus two upper storeys, so it matches the sources. This is not a finding.

## 2. Findings

| # | severity | view(s) with pixel regions | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | chamfer_dome x545-900 y430-500 (four dormers); architecture_close x500-940 y170-250; front x630-805 y320-360; top x410-560 y770-880 | Each dormer is a solid copper disc with a crescent hood plate set on its upper rim. There is no dark glazed oculus and no reveal, so no opening reads at any distance. The two outer dormers (chamfer_dome x550-600 and x840-890) stand off the silhouette as tilted plates. The source shows round oculi with dark glass inside a moulded copper frame, with the hood swept into the shell (oblique crop: three oculi with dark centres). | The dormer face was modelled as a closed disc cap with no inset glass or recess. The hood was authored but the opening was not. | Model each dormer as a ring frame (outer radius R, inner radius about 0.6R) with a dark glass disc recessed at least 0.15 m behind the frame face. Seat the frame base into the shell so that no gap shows on the silhouette. Re-render chamfer_dome and front and confirm four dark oculi are visible. |
| 2 | P1 | chamfer_dome x545-900 y330-640 (outer ribs); dome crop at the left and right silhouettes; architecture_close x490-950 y60-390; top x400-600 y700-880 | Only the central rib is smooth and continuous. The outer ribs show a sawtooth stepped profile along the silhouette and a dark tick gap every 20-25 px down their length. In the top view all eight ribs read as segmented ladders and stop short of the lantern neck, leaving a plain ring. The source shows about eight smooth, continuous ribs from the cornice disc to the lantern base. | The ribs are still built as chains of short straight boxes that follow the curve, so the joints open or overlap. The rib ends were not extended to the lantern collar. | Sweep each rib as one profile along the meridian curve, sharing vertices with the shell, or as one continuous tube or loft. Run each rib from the disc top to the lantern collar. Check that the top view shows eight unbroken spokes and that no silhouette steps remain. |
| 3 | P1 | chamfer_dome x520-915 y580-640; architecture_close x465-975 y390-440; front x625-820 y410-425 (a hairline); aerial x455-590 y560-585 | The dome foot now has a projecting disc, but the cresting is a low fence of thin posts with a zigzag rail. It is about 8% of dome height, it sits out at the disc lip with a visible ring of bare disc between it and the dome base, and it disappears to a hairline in the front view. The disc itself is cream stone. In the source (oblique dome crop, y850-1000) the dome foot carries tall pierced scroll panels about 18-20% of dome height between pedestals, standing on a copper-clad disc against the dome base. This band is a strong silhouette element in source front y195-235. | The cresting was authored as a wire railing, not as perforated panels. The disc took the stone material. | Replace the railing with 8-16 pierced copper panels about 0.9-1.1 m high, cut as arched or scroll openings in a solid plate, between small copper pedestals. Stand them at the dome base on a copper-clad top to the disc, and keep the stone bed mould below. Verify that the band reads as a solid lacy belt in the front view. |
| 4 | P2 | front x695-745 y210-280; chamfer_dome x670-770 y130-280 | The lantern is an open white-post gazebo under a smooth hemispherical cap. The source has an octagonal glazed lantern under a ribbed copper cupola with a finial. | Simplified lantern. | Add glass between the posts, use a copper octagonal frame and add ribs to the cap. |
| 5 | P2 | top x705-835 y450-580; front_corner x680-790 y465-530; aerial x700-810 y490-585 | The central rooflight reads as a flat grey slab from above. Only left_side x640-760 y450-500 shows a low pyramid. The source top (x540-660 y380-500) shows a steep framed glass pyramid on a plinth. | Low pitch and flat glass shading. | Raise the pitch to about 35-40 degrees, add hip and ridge frame members and a plinth. |
| 6 | P2 | ground_arcade x0-300 and x1120-1440 y430-730; glass_close | The wing ground floor is a flat wall with hairline joints and narrow slot openings with shallow reveals. Source front (y560-700) shows pilasters with capitals between the shop bays and deeper stone surrounds. | Pilasters were not modelled. | Add shallow pilasters with cap blocks between bays and deepen the reveals to at least 0.25 m. |
| 7 | P2 | top x385-435 y650-705 and x545-600 y830-880 | The chamfer pier caps appear as rotated wedges overlapping the parapet ends next to the disc. | The 45-degree pier caps collide with orthogonal parapet ends. | Trim the parapet at the pier faces and square the cap footprint. |
| 8 | P2 | balcony_ironwork x180-260 y630-705 | The bay balcony slab meets the stone pier with a notched step. | Slab and pier overlap. | Butt the slab cleanly to the pier face. |
| 9 | P2 | rear_court x290-390 y220-440 | A rear window shows straight through to a far-side French window and balcony, so the interior reads as a hollow shell. | No interior partitions or backing. | Add a dark interior backing plane behind the plain-face windows. |
| 10 | P2 | front, chamfer_dome | The salmon copper sits close in value to the terracotta roof. Source copper is browner and more saturated with darker shadows. | Material palette. | Darken and brown the copper by about 15%. |

## 3. Source conformance checklist

| item | status | view used |
|---|---|---|
| Silhouette (square block, chamfer corner with dome) | conforms | front, front_corner, aerial vs source front and oblique |
| Storey count (ground plus two upper storeys plus cornice and parapet) | conforms | front, left_side vs source front and oblique |
| Chamfer bay and dome | deviates: the bay conforms; the dormers, ribs and cresting deviate (findings 1-3); the lantern is simplified (finding 4) | front, chamfer_dome, architecture_close, top vs oblique crop |
| Window rhythm and balconies (continuous piano-nobile balcony; individual balconies on tall French windows above) | conforms | facade_close, balcony_ironwork, left_side vs source front |
| Ground-floor arches and entrance (arched glazed entrance on the chamfer with consoles under the bay; tall shop openings) | conforms, with a P2 for the missing pilasters | ground_arcade vs source front |
| Cornice and parapet (modillion cornice, balustrade with corner pedestals) | conforms; balusters are simplified posts (acceptable in clay) | cornice_contact, roof_terrace |
| Roof elements (terracotta flat roof, central rooflight, two small rooflights, chimneys) | deviates (P2): the pyramid is too flat | top, aerial, left_side vs source top |
| Materials hierarchy (stone ground floor and bay, brick upper walls, stone surrounds, copper dome, dark iron) | conforms; P2 on the copper value | front, facade_close |

## 4. Camera validity

All 18 views are valid. No target is occluded and no asset is clipped. The front view is now at eye height on the chamfer normal and centred on the bay and dome. The interior view is dark but legible: a French window with its balcony railing.

## 5. v007 findings: status in v008 pixels

1. **Dome foot (disc and cresting): partially resolved.** A projecting round disc on a bed mould is now present (chamfer_dome y590-650; top ring). The cresting is a thin wire zigzag fence, not pierced copper panels, and the disc reads as stone. It remains P1 (finding 3).
2. **Dormers: not resolved.** The cream toothed rings are now smooth copper and the hoods are curved, but the dormers are blank discs with no glazed oculus, and the outer two stand off the silhouette. It remains P1 (finding 1).
3. **Ribs: partially resolved.** There are eight ribs and the shell is smoother. Only the front rib is continuous; the others are visibly segmented, step on the silhouette and stop short of the lantern collar. It remains P1 (finding 2).
4. **Chamfer bay: resolved.** The bay is a continuous bow with five tall lights per level between round stone columns, one curved railing on a curved sill per level, and stone piers beside it (architecture_close, ground_arcade, front).
5. **Front camera: resolved.** The front view is at eye level on the chamfer normal, centred on the bay and dome.
