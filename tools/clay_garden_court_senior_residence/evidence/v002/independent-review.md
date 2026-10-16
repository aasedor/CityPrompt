# Independent holistic review: clay-garden-court-senior-residence v002 (RLASM v6.1 architectural clay)

Reviewer: independent, adversarial. Evidence used: only the pixels of `sources/front.png`, `sources/oblique.jpg`, `sources/top.jpg`, all 18 `renders/*.png` (every one opened at full resolution) and the 4 phone boards. Zoomed crops were written only to the new folder `/tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/indep-review-senior-v002-crops-1792117471/`. Metadata, audit JSON and builder notes were not used as proof.

## 1. Verdict

**VISUAL_REWORK_REQUIRED**: v002 fixes every v001 P0 and P1 in the pixels, and the plan, storeys, roofs, garden room and court programme now match the sources. However, four clearly visible P1 defects remain:
- a black void band under the copper eaves;
- black void slots at plinth junctions;
- a garden room with no doors although the sources show French doors and both path axes end at its glass;
- a drive loop that no street reaches.

Counts: P0 = 0, P1 = 4, P2 = 10

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | loggia_arcade (clearest), court_view, hub_cupola, dormer_roof, architecture_close (loggia eaves), front/front_corner (thin dark eave line) | A solid pure-black band about 0.25 to 0.3 m deep runs along every copper eave, between the roof edge and the cream cornice. At close range it reads as a void or missing fascia under the roof, not as a copper edge or a gutter. The sources show copper eaves over a light cornice with no dark band. | The roof shell does not meet the top of the cornice and the camera sees an unlit cavity, or a fascia/gutter got a near-black material. | Close the gap: drop the roof eave onto the cornice, or add a fascia strip in copper or cornice-cream that fills the band. Re-render loggia_arcade and hub_cupola to confirm no black remains. |
| 2 | P1 | loggia_arcade (black slot at the pavilion/loggia plinth junction, about x 370-390, y 840-930, with a stray cream stub block beside it), pergola_terrace (black notch at the wing plinth corner, about x 60-100, y 660-720) | Black rectangular holes appear at plinth corners where the cream base course of one mass stops short of the next. A loose cubic stub sits on top of the loggia plinth next to the hole. These are visible contact/closure defects in two hero detail views. | Plinth segments are cut to each block's footprint without mitring or closing at junctions; the leftover stub is an orphan base piece. | Extend or mitre the plinth course so it closes on every block-to-loggia and block-to-block junction, delete the orphan stub, and check every link junction (there are 5 loggia junctions) in a close render. |
| 3 | P1 | glass_close, court_view, architecture_close, interior, rear (north face), top (path axes) | The octagonal garden room is glazed all round over a solid knee base and has **no doors**. The centre court-facing bay is a fixed 3 x 3 grid with a sill, and the north face has no door either. Both the court ring path and the forecourt N-S axis path end at the glass. The front and oblique sources clearly show a pair of glazed French doors in the court-facing bay. | The garden-room bay generator puts the same window panel on all 8 faces. | Replace the court-facing bay (and preferably the forecourt-facing bay) with a pair of glazed doors down to floor level, plus a threshold/step meeting the path. Re-render glass_close and court_view. |
| 4 | P1 | top, front_corner, front, hub_cupola, rear_side | The new drive is a closed racetrack loop round a planted island. It sits isolated in lawn, with no throat to the west street and no north street to connect to, so no vehicle can reach it. In the top source the drive lane meets the street at both curved ends. | The loop was modelled as a standalone shape without a site-access link, and the north street from the source was not modelled. | Add an access throat at one or both curved ends to the west street, or add the north street edge from the top source and join the curved ends to it. |
| 5 | P2 | front, front_corner | The north-slope dormers on the south wing (and the far-slope dormers on the east wing) still appear above the ridge as a row of small "teeth". The rear, rear_side and right_side views confirm the ridges are clean, so this is parallax from deep dormers, not penetration. | The dormers still project a long way from the slope. | Optional: shorten the dormer depth a little more or lower the dormer ridges. |
| 6 | P2 | facade_close, pergola_terrace, loggia_arcade | Horizontal coursing grooves about 0.3 m apart make the walls read as clapboard/lap siding at close range rather than brick. | Course-groove spacing is too large. | Use finer groove spacing (about 0.075 m) or none, and let colour carry the brick. |
| 7 | P2 | loggia_arcade, court_view | Arch archivolts are visibly faceted (low segment count) and done in cream stone. The source arches are brick-on-brick with at most a light keystone. | Low arc segmentation; trim colour choice. | Raise the arc segments to at least 16 and use brick or a near-brick tone for the archivolts. |
| 8 | P2 | court_view, top, front | The court is much sparser than the sources: open lawn and a few lollipop trees. The sources show dense shrub borders, hedges along the paths and flowering beds. Rose beds read as flat pink pucks with a single green blob. | Planting density/variety is low. | Add low hedge strips along the paths and shrub masses at the bed edges, and break up the rose beds. |
| 9 | P2 | court_view | Seen from above, the court fountain reads as a basin with a short stub rather than a tiered fountain. The interior view shows the upper bowl, and the forecourt fountain reads as tiered. | The upper tier is low or small relative to the basin. | Raise the pedestal and upper bowl and add a finial. |
| 10 | P2 | pergola_terrace | The chair back on the rear right table passes through the table top. The pergola has beams and rafters but not the source's top slat/lattice layer. | Chairs placed too close; one pergola layer missing. | Push chairs out about 0.15 m and add a top slat layer. |
| 11 | P2 | loggia_arcade | Garden-room mullions in the near foreground cover the right ~20% of the frame, and a tree crown cuts the top-left. The arcade itself is legible. | The camera is placed tight against the garden room. | Move the camera about 1 to 2 m to the west/south. |
| 12 | P2 | left_side, right_side, rear | The asset fills only a thin band (about 55% width, about 15% height) with large empty ground and sky, so elevation detail is small. | The orthographic-style framing uses a wide margin. | Tighten the framing. |
| 13 | P2 | rear, left_side, right_side | No main entrance is legible on any outer face (pavilion north faces, forecourt). No source shows these faces; this is coherence only. | Not modelled. | Optional: add an entrance door or portico on a north pavilion face toward the forecourt. |
| 14 | P2 | glass_close, interior | A slight milky haze washes over the glazing close-ups. | Glass/volume or exposure settings. | Reduce the glass roughness and haze. |

## 3. Source conformance checklist

| Item | Status | View(s) used |
|---|---|---|
| Silhouette | conforms. Five hipped copper blocks in a ring with low links and a central octagon with a cupola. | front, front_corner, aerial, rear, top vs oblique/top |
| Storey count | conforms. Three brick storeys plus a dormered attic on every block; links are one storey. | left_side, right_side, rear, front |
| Plan (ring of blocks, court) | conforms to the top source. Two north pavilions, a SW pavilion, a long east wing and a long south wing round a closed court. | top vs top.jpg |
| Roofs and dormers | conforms. Pavilions are hipped to a flat top with rooftop units; wings are hipped to a ridge; there are gabled dormers with double-hung sashes on every slope and none on the wing hip ends. Ridges are clean in near-horizontal views (P2 #5 parallax only). Eave finish deviates (P1 #1). | dormer_roof, top, rear, rear_side, front |
| Loggias and arches | conforms in form: one-storey brick loggias with round arches and copper roofs on all five links. Deviates in finish: black eave band (P1 #1), plinth voids (P1 #2), and faceted cream archivolts (P2). | loggia_arcade, court_view, rear, left_side, right_side |
| Garden room and cupola | conforms in form: octagonal glazed room, copper roof, glass ribbed dome on a drum with finial. **Deviates** because it has no French doors (P1 #3). | architecture_close, hub_cupola, glass_close, court_view |
| Window rhythm and balconies | conforms. White double-hung windows in a regular 5-bay rhythm on pavilion court faces; an iron balcony over the middle bay; an arched garden door with fanlight under the balcony slab (interior). | front_nw crop, court_view, interior, facade_close |
| Garden elements (paths, fountain, beds, pergola) | conforms. Brick path ring and cross, a tiered fountain in the SW of the court with rose beds, a fenced 2 x 5 raised timber bed garden, and a timber pergola over a dining terrace at the east. Planting density deviates (P2). | top, court_view, garden_beds, pergola_terrace, interior |
| Forecourt | partly deviates. The circular lawn with ring and cross paths and a central tiered fountain conform. The drive loop with island has no street access (P1 #4). | top, hub_cupola, front_corner |
| Materials hierarchy | mostly conforms: red-brick walls, copper roofs, cream trim/plinths, white glazing frames, iron railings, timber pergola and beds. It deviates in the black eave band (P1 #1), the siding-like coursing and the cream archivolts (P2). | facade_close, loggia_arcade, dormer_roof |

## 4. Camera validity

- **No view is invalid.** No camera is inside a solid, no frame is black, and no target is fully occluded or clipped.
- **facade_close, garden_beds, pergola_terrace:** now taken from open ground; each target is fully legible.
- **court_view:** frames the garden room, both north pavilions, the loggias, the path ring, the fountain, the rose beds, the fenced bed garden and the pergola. It matches the source front composition.
- **loggia_arcade:** legible. The right ~20% is masked by near-foreground garden-room mullions and a tree cuts the top-left corner (P2 #11).
- **left_side, right_side, rear:** legible but the asset is small in frame (P2 #12).
- **front, front_corner, aerial, top, rear_side, dormer_roof, hub_cupola, architecture_close, glass_close, interior:** valid and legible.

## 5. Previous-version (v001) findings: resolved in the pixels?

| v001 finding | Status in v002 pixels | Evidence |
|---|---|---|
| P0: facade_close, garden_beds and pergola_terrace cameras inside solids (black frames) | **Resolved.** All three show legible targets from open ground. | facade_close, garden_beds, pergola_terrace |
| P1: dormers too deep, piercing the wing ridges as a row of teeth | **Resolved.** The wing ridges are clean in the rear, rear_side and right_side views. The dormers are shorter, have double-hung sashes, and none sit on the wing hip ends (top). The teeth seen over the south-wing ridge in front and front_corner are parallax of far-slope dormers (P2 #5). | rear crop, rear_side crop, right_side, top, dormer_roof |
| P1: court-face garden doors flat-headed under the balconies | **Resolved.** The arched garden door with fanlight now sits clearly below the iron balcony slab. | interior |
| P1: forecourt drive a straight slab, not a loop with an island | **Resolved as to form.** It is now a loop with curved ends round a planted island, with a cross path to the forecourt circle. It introduces new P1 #4 because the loop has no street access. | top crop, front_corner |
| P1: court_view pitched too far north, missing the fountain and beds | **Resolved.** The fountain, rose beds, bed garden and pergola are all in frame. | court_view |
| P1: loggia_arcade blocked by a court tree | **Resolved.** The arcade is legible; only minor edge occlusion remains (P2 #11). | loggia_arcade |
| Carrier aperture audit: two ground windows behind the south-east loggia | **Resolved in pixels.** No window is cut or hidden by the SE loggia roof or piers. | front_east crop, right_side |
| Builder claim: 2 x 5 raised-bed grid | **Verified.** Ten beds in two columns inside the fence. | top crop, garden_beds, court_view |
