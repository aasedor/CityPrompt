# Independent holistic review: clay-grand-magasin v002 (RLASM v6.1)

Reviewer: independent, pixels only. I opened every render in `renders/` (all 18), the three locked sources and the four phone boards, plus zoomed crops of `corner_dome.png`, `roof_domes.png`, `left_side.png` and `front.png`. I did not use the builder's notes, metadata or audit JSON as evidence.

## 1. Verdict

**Verdict: VISUAL_REWORK_REQUIRED.** The v001 P0 is fixed: the glazed drum now stands clear above the mansard and carries a ribbed dome and a lantern. Four P1 defects remain visible in the pixels. Three are on the corner and dome group, which is the identity element, and one is the upper-bay grammar, which makes the iron-and-glass store read as a punched-window block.

Counts: P0 = 0, P1 = 4, P2 = 8

## 2. Findings

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | corner_dome, roof_domes, front, front_corner, left_side | The new "stone attic cylinder with arched windows" under the drum has no windows. It shows five blank, flat white slabs with notched pennant-shaped bottoms. They stand proud of a pale-zinc conical skirt and read as stuck-on planes, with no openings, reveals or arches. The source has no stone attic and no zinc cone here: the curved glazed bay rises through the gilded balustrade directly into the glazed drum. | The attic window modules were authored as solid panel geometry (or their boolean cut failed) and placed on a tapered skirt mesh. The attic and cone add a tier that the source does not have. | Either remove the cone skirt and seat the drum directly on the corner bay's top cornice and gilded ring, as the source shows, or cut real round-arched openings with reveals of at least 0.25 m and dark glass into a vertical stone cylinder. Remove the white slabs. |
| 2 | P1 | front, facade_close, gilded_balconies, left_side, architecture_close, mansard_dormers | The upper bays between pilasters are ordinary punched windows: 2 or 3 lights, plain stone strips about 15–20% of the bay on each side, and a stone lintel band between floors. The glass fills only about 60–65% of the pilaster-to-pilaster width. The source bays are iron-and-glass frames that fill the full bay, with iron mullions and ornamental arched heads. At street scale the building reads as a hotel or office block, not a Belle Epoque magasin. | The window module is sized as a punched opening inside a wall panel instead of an infill frame spanning the full pilaster opening. | Widen the glazing frame to span the full clear width between pilasters and from floor band to floor band. Use a dark iron frame with a slender central mullion and transom and an arched or segmental iron head at each bay. Remove the stone side strips and keep the pilasters and floor bands. |
| 3 | P1 | architecture_close, marquise_sign, front, roof_domes | The curved corner bay reads as a plain modern curtain wall. Its top storey has flat heads, not the round arches of the source corner bay, and its balcony levels carry thin yellow wire rails, not the solid gilded balcony fronts the source shows on the corner bay. The adjacent street faces carry arched top storeys and gilt panels, so the hero bay is the least ornamented part of the building. | The corner-bay assembly uses a generic curved mullion wall with a rail primitive instead of the facade's arched-head and gilt-front modules. | Give the corner bay's top storey round-arched iron heads in each light. Replace the wire rails at the balcony levels with curved solid gilt fronts that match the street-face panels in height and colour. |
| 4 | P1 | roof_domes, corner_dome, left_side, rear, front, top | The second dome sits on a blank white cylinder with an obliquely chamfered, prow-like underside. The cylinder is perched on the upper roof well back from the facade, and part of it overhangs the start of the mansard slope, so it reads as a rooftop pod. It has no openings and no facade element carrying it down to the street. The top source shows the smaller dome over a round projection that reaches the facade line, flush with the building edge. | The dome was placed on a free-standing drum primitive at roof level. The underside was trimmed against the hip instead of being supported by the wall below. | Carry the small dome on a drum that is continuous with the facade at the end bay of the west face, as a rounded end pavilion or a drum set on the cornice line. Give the drum glazed or arched openings like the main drum's, and remove the chamfered underside. |
| 5 | P2 | facade_close, gilded_balconies, architecture_close | A black square void sits at the centre of each cross ornament on the gilt panels and reads as punched holes. The gilt is a pale, desaturated ochre (about 162,145,95) against the source's deep gold (about 107,84,54). | Ornament centre faces use a black material, and the gilt material is too light. | Use the gilt material for the ornament centres and darken and saturate the gilt slightly. |
| 6 | P2 | mansard_dormers, left_side, rear | The top-storey "round" arches are canted polygons with chamfered shoulders. | The arch profile has too few segments. | Raise the arc segment count or use a true semicircular head. |
| 7 | P2 | corner_dome, front (zoom) | Small black slits appear where the attic skirt meets the flanking pavilion gables. | There are gaps or z-fighting at the junction. | Close the junction geometry. |
| 8 | P2 | marquise_sign, left_side | The marquise and sign band break and change section at the pavilion piers, where the corner band and street bands do not join. | The bands are separate segments. | Run one continuous canopy edge around the corner. |
| 9 | P2 | top, aerial | The court is now central, but the deep inner mansard narrows the visible void to about 30% of the block width. In the top source the light well, with its vertical inner walls, spans about 50%. | The inner mansard projects too far inward. | Steepen or shorten the inner mansard so the inner facades rise closer to the roof edge. |
| 10 | P2 | front, corner_dome | The corner dome is close to a hemisphere with a small lantern. The source dome is taller and bulbous, with a more prominent lantern. | Dome profile. | Lift the dome profile about 15–20% and enlarge the lantern. |
| 11 | P2 | left_side, right_side, rear | The end bays show diagonal streaks through the glass, where the interior shell or roof underside is visible. | There is no interior backing or blind behind the end-bay glass. | Add an interior backing plane or ceiling at the end bays. |
| 12 | P2 | interior | The interior view is very dark, and a column fills the centre of the frame. It is still legible. | Exposure and camera placement. | Raise the exposure and offset the camera from the column. |
| 13 | P2 (method note) | top vs sources | The top source shows a large ribbed dome over the central court and the smaller dome on a corner projection. The render follows the brief's arrangement: corner dome over the curved bay, small dome at the far end of the west face, open court. This is not counted against the build. | The locked top source and the brief's identity text disagree. | The method owner should confirm which arrangement governs. |

The P2 count is items 5–12. Item 13 is an advisory note and is not counted.

## 3. Source conformance checklist

| Item | Status | View used |
|---|---|---|
| Silhouette (corner block, hipped mansard ring, corner drum and dome above eave) | conforms | front, front_corner, aerial |
| Storey count (double-height ground floor, 4 upper storeys, mansard) | conforms | left_side, front |
| Corner bay and dome: drum | conforms (stands clear of the mansard, glazed with mullions) | front (zoom), corner_dome |
| Corner bay and dome: ribs | conforms | corner_dome, top |
| Corner bay and dome: lantern | conforms, but undersized (P2) | corner_dome, front (zoom) |
| Corner bay and dome: attic or base between bay and drum | deviates (blank slabs on a zinc cone, P1 #1) | corner_dome, roof_domes |
| Curved glazed corner bay | deviates (flat heads, wire rails, P1 #3) | architecture_close, marquise_sign |
| Bay rhythm and pilasters | pilasters and rhythm conform; bay infill deviates (punched windows, P1 #2) | facade_close, left_side |
| Gilded balconies | conforms on the street faces (solid gilt fronts, now dense); deviates on the corner bay (P1 #3); tone and holes P2 | gilded_balconies, architecture_close |
| Ground-floor display windows and marquise with red sign band | conforms (glass canopy, red and gold band, continuous display windows); junction breaks P2 | glass_close, marquise_sign, left_side |
| Arched top storey and bracketed cornice | conforms on the street faces (arches polygonal, P2); deviates on the corner bay | mansard_dormers, left_side |
| Gilded cornice balustrade | conforms (continuous solid gilt between stone piers on the street faces) | mansard_dormers, corner_dome |
| Mansard and dormers | conforms (blue-grey zinc, arched zinc dormers, hipped upper roofs with ridges) | mansard_dormers, rear_side, aerial |
| Projecting stone pavilions with arched gable dormers beside the corner bay | conforms | corner_dome, roof_domes, left_side |
| Second dome | deviates (blank pod perched on the roof, P1 #4) | roof_domes, corner_dome, left_side |
| Light well and court | conforms in position and has inner facades and dormers; narrow void P2 | top, rear_side, rear_court |
| Materials hierarchy (limestone > zinc > iron and glass > gilt > red band) | conforms broadly; gilt too pale (P2) | front, facade_close |
| North and east faces (not in any source) | coherent with the visible grammar: same pilasters, arches, mansard and dormers, with no balconies or marquise | right_side, rear |

## 4. Camera validity

- All eight whole-envelope views (front, front_corner, aerial, top, left_side, right_side, rear, rear_side) frame the whole asset without clipping or occlusion.
- `rear_court` now looks down into the inner court and shows the inner facades and the court floor, so it is valid. This resolves the v001 camera finding.
- `interior` is legible but very dark, and a column sits in the centre of the frame (P2, not invalid).
- Every other detail view frames its named target legibly.
- No view is invalid.

## 5. Previous-version (v001) findings, checked in pixels

| v001 finding | Resolved in pixels? | Evidence |
|---|---|---|
| P0: corner drum sunk into the mansard, too short to clear the eave, posts ending in spikes | **Resolved.** The glazed drum with mullions stands on a gilded ring well above the mansard eave and is capped by a ribbed dome and lantern, with no spikes. However, the new stone attic under it has no real windows, which is a new P1 (#1). | front (zoom), corner_dome, roof_domes |
| P1: near-white zinc | **Resolved.** The zinc is a mid blue-grey (about 138,146,152) and is no longer near white. | front_corner, top, mansard_dormers |
| P1: flat upper roof without wings or ridges | **Resolved.** Hipped upper roofs with ridges and hips are visible around the court ring. | aerial, rear_side, top |
| P1: small off-centre light well | **Mostly resolved.** The court is centred, with inner facades and dormers. The void is still narrower than the source because of the deep inner mansard (P2 #9). | top, aerial, rear_side, rear_court |
| P1: no continuous gilded cornice balustrade | **Resolved.** A continuous solid gilt balustrade runs between stone piers along the street cornices. | mansard_dormers, corner_dome |
| P1: no projecting stone pavilions with arched gable dormers beside the corner bay | **Resolved.** One-bay projecting pavilions with segmental-arched gables flank the corner. | corner_dome, roof_domes, front |
| P1: sparse gilt balcony grids | **Resolved on the street faces** (solid gilt panel fronts on every bay and level). **Not resolved on the corner bay**, which still has thin wire rails (P1 #3). | gilded_balconies, architecture_close |
| P1: black dormer cheeks | **Resolved.** The dormer cheeks are zinc-coloured. | mansard_dormers, roof_domes |
| P1: rear_court camera on the outer face | **Resolved.** The camera looks into the inner court. | rear_court |

The builder's claim of "a stone attic cylinder with arched windows" is **not true in the pixels**: the attic carries blank white slabs and no arched openings.
