# Independent holistic review: clay mews coach house v006 (RLASM v6.1)

Reviewer: independent; I did not build this candidate. Inputs I opened at full resolution: sources/front.png, sources/oblique.jpg, sources/top.jpg; all 18 renders; boards phone-01 to phone-04. I also made zoomed crops (written only to the new folder `/tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/mews-v006-review-crops-bb5ca6a6/`). I ignored metadata, build reports and builder claims as proof.

## 1. Verdict

**PASS_ZERO_P0_P1.** The pixels show the white-painted two-storey corner mews house: a hipped slate roof, the long two-step party-wall stack with 5 + 4 round clay pots, the red boarded coach door under its glazed transom, the white panelled door with fanlight, six-over-six sashes, the attached neighbour with its hipped back wing, and the enclosed yard with the red door in a coped wall. All three v005 P1s are resolved in the pixels and the v004 fixes still hold. What remains is polish.

Counts: P0 = 0, P1 = 0, P2 = 12

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P2 | facade_close, eaves_corner, front, roof_chimneys | The upper south window heads are a raised segmental band. It stands proud of the brick, casts a shadow line, and its radially cut "ears" overhang the reveals by about 1 brick each side. Below it a solid white tympanum sits over a flat sash head. The source front shows a flush arched reveal, with the arch read only as a shadowed recess over the sash head. | The arch is modelled as a projecting hood moulding, not a flush gauged arch, and the segment is filled. | Bring the arch band flush (proud by 0 to 5 mm) and trim its ends to the reveal width. Recess the segment between the arch and the sash head to the sash plane, or tint it as reveal shadow. |
| 2 | P2 | rear_north, rear | The rear kneeler at the foot of the long party-wall stack bears on top of the black rear gutter, and the gutter runs continuously beneath it. The white eaves band under the gutter is cut out below the kneeler, leaving a lit notch with a dark sliver on one side. | The kneeler was raised to the eaves line by placing it on the gutter's top surface. The eaves band was boolean-cut at the party-wall line. | Stop the gutter against the kneeler's sides, or tuck the kneeler behind the gutter onto the wall head. Run the eaves band continuously across the party line. |
| 3 | P2 | eaves_corner, architecture_close, roof_chimneys | A pale chamfered curb strip runs along every slate eaves edge, above the black gutter, and frames the roof in a light line. In the source the slate runs straight into the gutter, and the white band is only below the gutter. | An eaves fillet or undercloak piece was given the white trim material. | Give the strip the slate colour, or drop it below the slate's lower edge. |
| 4 | P2 | front_corner, roof_chimneys, front | The party-wall parapet on the front slope, from the stack down to the eaves, is topped by a broad white slab coping that reads like a plank laid on the roof. In the oblique and front sources the parapet is a narrow tan stock-brick upstand with a thin coping. | The coping is too wide and uses the stone-white material. | Narrow the coping to about the wall thickness plus a small drip, and use a buff or stone tone closer to the stack cap. |
| 5 | P2 | top vs source top, rear | Measured centre to centre, the neighbour bay is about 0.72 to 0.76 of the end-house frontage, against about 0.80 in the source top. At wall line the back wing is about 73% of the bay and centred (rear elevation), so the v004 fix holds. From above, though, its eaves fill about 90% of the bay and leave only slivers of the neighbour's rear slope either side, where the source top shows clear slope both sides. | The neighbour bay is slightly narrow, and the wing eaves overhang is generous. | Widen the neighbour bay by about 0.5 m to the west and reduce the wing's eaves overhang. |
| 6 | P2 | top, front_corner, aerial, right_side | The whole side street is paved in setts. The source top and oblique show an asphalt carriageway on the side street, with setts only at the corner and junction mouth and at the coach-door crossing. | One material is assigned to the whole side-street plane. | Split the plane so that asphalt is the default and setts appear only at the junction mouth. |
| 7 | P2 | front, architecture_close, east_side, top | The east-face downpipe sits at the SE corner. In the front and oblique sources it is about a quarter of the way along the east face, beside the windows. The lamp head points west and south over the mews pavement, while in the source front its bracket points east over the side street. | Placement choices. | Move the downpipe north to sit beside the east windows. Turn the lamp bracket to the east. |
| 8 | P2 | rear, rear_north, rear_side | The rear ground floor mixes six-over-six sashes with one plain two-light window that has no glazing bars. One rear ground sash shows a strong red cast through its panes (the back of the coach door), so it reads as red glass at distance. | A one-off opening type; interior visibility through the glass. | Make the odd opening a barred sash, or a small six-pane casement in the same grammar. Add a neutral interior partition or blind behind that rear sash. |
| 9 | P2 | front vs source front | In the render front the neighbour's front slope is foreshortened to a thin strip behind its west parapet, so its skylights and slate slope are not legible. The source front shows the slope with a skylight. | The front camera is slightly lower and closer than the source's. | Raise the front camera by about 1 m, or pull it back to match the source's horizon. |
| 10 | P2 | left_side | On the exposed west party gable, the buff gable triangle is wider than the white wall below it and oversails the gutter ends on both sides. | The gable mesh was sized to the eaves overhang, not to the wall face. | Trim the gable triangle to the wall face, or return the eaves onto the gable with a small cut-off. |
| 11 | P2 | interior | An unexplained black bar runs along the junction of ceiling and right-hand wall. | It looks like an exterior element (the gutter or string course) showing through, or a stray beam. | Identify it and remove it or hide it from the interior camera. |
| 12 | P2 | rear_north | The wing downpipe runs tight against the end of the wing's east-window sill. At this resolution the sill end and the pipe appear to touch. | The pipe line was set without checking the sill projection. | Shorten that sill's horn by about 30 mm, or shift the pipe about 50 mm north. |

## 3. Source conformance checklist

| Item | Status | View(s) used | Note |
|---|---|---|---|
| Silhouette | conforms | front vs source front; front_corner and aerial vs oblique; top vs source top | Two-storey block hipped to the corner. Long party-wall stack near the ridge. Attached neighbour with a coped west party parapet and a hipped back wing. The plan footprint and corner position match the top source. |
| Storey count and proportions | conforms | front, right_side, rear | Two storeys, string course at first floor, frontage roughly square to the eaves as in the source. The upper rhythm (paired sash, single, single) sits correctly over the coach door and front door. The neighbour bay is slightly narrow (finding 5). |
| Painted brick and plinth | conforms | facade_close, east_side, front | White-painted brick with coursing in close views, and a black plinth on the south and east faces and on the neighbour. |
| Coach door (boards, transom) | conforms | coach_door, facade_close, front | Red vertical boarding with dark grooves. A full-width glazed transom with bars sits above it in its frame. Proportion is close to the source. |
| Front door and fanlight | conforms | front_door, facade_close | White four-panel door with knocker, letter plate and knob, under a rectangular glazed fanlight, set in a reveal. |
| Sashes | conforms | facade_close, glass_close, east_side, rear | Six-over-six with meeting rails, reveals and dark sills on the south, east and rear faces and on the back wing. The paired south window has a dark central post as in the source. The heads deviate slightly (finding 1). There is one odd unbarred rear opening (finding 8). |
| Eaves band and gutter | conforms (minor) | eaves_corner, architecture_close | Thin white band under a black gutter all round. There is an extra pale curb above the gutter (finding 3) and a notch at the rear party line (finding 2). |
| Roof: hip | conforms | top, architecture_close, eaves_corner | The corner end is hipped. The hips and ridge carry terracotta ridge tiles, as in the oblique. |
| Roof: slate | conforms | all roof views | Untextured grey slate tone (clay). |
| Roof: chimneys | conforms | top, roof_chimneys, rear_side, left_side, right_side | One long two-step stack on the party wall between the end house and the neighbour. It runs from just south of the ridge down the rear slope to the rear eaves. Each step has a stone cap and an oversailing course. The neighbour's west party wall has no stack. |
| Roof: pots | conforms | top (crop), roof_chimneys, front_corner | Tall round terracotta pots with rims: 5 on the ridge step and 4 on the rear step, matching the clusters in the top source. From the front, the rear-step pots peek over the ridge to the right of the stack, as in the source front. |
| Roof: skylights | conforms | top, front_corner, aerial | Two small skylights on the neighbour's slope. In the locked top source they lie on the south (mews-side) slope, between the neighbour's ridge and its front eaves, and the render places them there too. The brief's wording "rear slope" does not match the source pixels, so I judged against the pixels. |
| Neighbour | conforms | front, facade_close, rear, top | The neighbour repeats the white panelled door with fanlight and six-over-six sashes (a paired ground window with a dark post, plus singles). Its back wing is hipped and centred, about 73% of the bay at wall line. Its ridge rises into the main rear slope at about mid-height with two valleys and a hipped north end. Wing windows are barred sashes with sills. |
| Setts | conforms (minor) | front, top | Setts crossing in front of the coach door. The side street is over-setted (finding 6). |
| Pavement and street furniture | conforms (minor) | front, top, architecture_close | Pavements on the mews and side street. Low-poly plane tree in front of the neighbour, centred on its bay as in the top source. Black lamp standard at the corner, with its arm direction differing from the source (finding 7). |
| Garden wall and red yard door | conforms | rear_side (crop), top (crop), right_side, front | A continuous coped buff brick wall runs from the house's NE corner along the side street, then west to the back wing, closing the yard. The red boarded door sits between capped piers under a head. |
| Materials hierarchy | conforms | all | White painted brick, black plinth, gutter, pipes and sills, red boarded doors, grey slate, buff stock brick for stacks, party parapets and the garden wall, terracotta pots and ridges. The only off-hierarchy element is the white slab coping on the front party parapet (finding 4). |

## 4. Camera validity

No view is invalid: in every view the target is unoccluded, unclipped and legible.
- front: valid. It is a little closer and lower than the source, so the neighbour's front slope is foreshortened (finding 9).
- front_corner, aerial: valid. The building fills only about 35 to 40% of the frame, but the identity elements are legible.
- top: valid orthographic plan, with the whole envelope, yard and streets in frame.
- left_side, right_side, rear, rear_side: valid and unclipped.
- Detail views (facade_close, architecture_close, glass_close, coach_door, front_door, roof_chimneys, east_side, eaves_corner, interior, rear_north): all legible. front_door is tight and crops off the fanlight and threshold, but facade_close shows both.

## 5. Previous-version findings: resolved in the pixels?

### v005 P1s

1. **Same short square stack with three stubby square pots on every party wall: RESOLVED.**
   - The top crop shows a single long stack on the end-house/neighbour party wall, from just south of the ridge to the rear eaves.
   - It carries round pots in two clusters: 5 at the ridge step and 4 at the rear step.
   - left_side and the top view show no stack on the neighbour's west party wall, only a coped parapet.
   - The pots are tall and round with rims (roof_chimneys, rear_side), and each step has a cap and an oversailing course.

2. **Rear-wing downpipes dropping from the gutter overhang, standing clear of the wall, with an orphan stub: RESOLVED.**
   - rear_north shows a swan-neck from an outlet under the wing gutter back to the wing's east wall.
   - The pipe then runs down just off the wall face, with visible clips.
   - There is no stub anywhere. The pipe foot is behind the yard wall, so I could not see the shoe in any view.
   - The pipe runs tight against one sill end (finding 12, P2).

3. **Free-standing wall panel and red door leaf on the east pavement: RESOLVED.**
   - The wall is a continuous coped brick wall from the house's NE corner along the side street, returning west to the back wing, and it closes the yard (top crop, rear_side crop, rear).
   - The red boarded door is set between capped piers under a head.

### Builder-claimed v005 P2 fixes

- Kneelers raised to the eaves line: done at the front party line. At the rear, the kneeler now sits on the gutter and notches the eaves band (finding 2).
- East string course to the SE corner: done (east_side, front).
- Six-over-six sashes on the rear face: done on the upper floor. One unbarred ground-floor opening remains (finding 8).
- Lamp arm turned over the carriageway: done (it points over the mews), though it differs from the source's eastward bracket (finding 7).

### v004 fixes (must still hold)

- **Upper south sashes:** still rectangular six-over-six under a shallow segmental arch with a rise of about 0.1 of the span. They are not round-headed. The arch is a little proud and has ears rather than being strictly flush (finding 1, P2).
- **Neighbour's back wing:** still a hipped wing, about 73% of the bay at wall line and centred on the bay. Its ridge rises out of the main rear slope at about mid-height, with two valleys and a hipped north end. I could not judge from the pixels whether it is hollow, because its windows show interior shade. The eaves look wide from above (finding 5, P2).
- **Back-wing windows:** still framed six-over-six sashes with bars, sills and reveals (rear, rear_north, rear_side).
