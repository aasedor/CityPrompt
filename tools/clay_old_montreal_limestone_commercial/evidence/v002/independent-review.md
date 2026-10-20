# Independent holistic review: oldmtl v002 (RLASM v6.1 architectural clay)

Reviewer: independent; judged on rendered pixels against the locked sources only (sources/front.png, sources/oblique.jpg, sources/top.jpg). I opened all 18 render PNGs, the three sources and the four phone boards at full resolution with the Read tool, and checked zoomed crops (written only to the new folder `/tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/oldmtl-v002-indep-crops-891e8621/`).

## 1. Verdict

**VISUAL_REWORK_REQUIRED**: both v001 P1s are fixed in the pixels (giant-order portico; two-tier pavilion with attic, balustrade and arched tympanum window). Two new P1s block approval. The pavilion attic roof is a double pyramid with a central valley, not the source's low hipped slate roof. The whole-envelope rear camera cuts off the west end of the hall at the frame edge.

Counts: P0 = 0, P1 = 2, P2 = 6

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | front_corner, aerial, top, rear, right_side | Inside the attic balustrade, the pavilion roof shows as two pyramids side by side. In top view it reads as an "X" over the north half, a lit diamond-shaped valley in the middle, and a second pyramid with the skylight over the south half. In front_corner and aerial the facets are near-black and show a cross-valley. In rear and right_side, black slivers and slots show between the facets and the balustrade. The source top and oblique show one continuous low hipped slate roof. It has a single ridge, its west hip meets the range roof, and it carries a skylight on the slope and a chimney. Its colour matches the range slate. | The attic roof seems to be built as two square hipped pyramids, one per half of the rectangle, instead of one rectangular hip with a ridge. The facet normals or the material leave it darker than the range slate. | Replace it with one rectangular low hipped roof (ridge along the long axis, four hips) seated on the attic wall plate inside the balustrade. Keep the skylight on the south slope and the chimney. Use the same slate material and normals as the range roof. Confirm in top, front_corner and rear that there is no central valley and no black slot. |
| 2 | P1 | rear | The west range's north face runs straight off the right edge of the frame (x = 1440). The north-west corner pilaster strip, the end of the hipped roof and the west end are not in the picture. Building pixels touch the edge from the eave down to the plinth. This whole-envelope view clips the asset. | The rear camera was narrowed to "frame the hall" but is centred on the dome block. The west range (longer than the east range's north face) runs past the frame. | Shift the rear camera target west, or widen it or pull it back, until both the pavilion (left) and the west range's west hip and corner (right) sit inside the frame with a margin of 3% or more. Re-render rear only. |
| 3 | P2 | portico | The portico frieze "triglyphs" are plain square blocks with no glyph grooves. | Simplified frieze module. | Add two vertical grooves to each block, or accept as clay simplification. |
| 4 | P2 | portico | There is a small dark notch where the portico's side cornice return meets the range eave cornice (just above the right-hand column capital). | The portico cornice and range cornice profiles don't meet with a mitre. | Extend the portico cornice return to meet the range cornice, or add a short closer block. |
| 5 | P2 | front_corner, aerial (vs oblique) | The pavilion attic walls are plain between the sashes. The source attic has recessed vertical panel strips between and beside its windows. | Attic wall lacks the strip/panel module. | Add shallow recessed pilaster panels to the attic long faces. |
| 6 | P2 | top (vs source top) | The source shows three small vents/dormers on the west part of the east range roof, plus a few more on the court slope. Render shows five court-slope dormers only. Render also puts trees on the north sidewalk east of the dome block, where the source has a neighbouring building and no trees. | Simplified roof furniture and tree list. | Optional: add the west vent dormers and drop the two north-east sidewalk trees. |
| 7 | P2 | top | The pavilion is a little narrow in plan: about 17% of the east-range length, against about 22% in the source top. It still has three bays on its south face, which matches the source. | Bay module slightly tight. | Optional: widen the pavilion bay pitch slightly. |
| 8 | P2 | renders folder | The brief names facade_close, architecture_close and glass_close, but those files are not in renders/. 18 files are present, which matches the brief's stated count. Window depth and returns are still clearly visible in long_facade, balconettes, east_door, end_pavilion_arches and interior. | View list in the brief is out of step with the render manifest. | Render the three named views, or correct the brief's list. |

## 3. Source conformance checklist

| Item | Status | View(s) used |
|---|---|---|
| Silhouette | Conforms. Long low three-storey hall, dome on a square attic rising well above the roofs, pedimented portico above the range roof, and a pavilion with attic and balustrade at the east end. | front, front_corner, aerial vs oblique/front |
| Storey count | Conforms. Basement vents plus three storeys of sashes on the ranges. The pavilion has two tall arched tiers within the range height plus an attic storey. | long_facade, end_pavilion_arches, front |
| Plan: offset ranges | Conforms. The west range lines up with the dome block. The east range is stepped south by a full range depth. Length ratio east/west is about 1.58 (source 1.57). | top vs source top |
| Plan: dome block | Conforms. Square block, west and north faces flush with the west range. | top, rear_north |
| Plan: portico | Conforms. At the west end of the east range, on the south street. | top, aerial, portico |
| Plan: north porch | Conforms. About 90–95% of the dome block width, centred on its north face. | top, rear_north |
| Limestone coursing | Conforms (clay). Shallow horizontal course joints are visible on the walls. | long_facade, balconettes |
| Basement vents | Conforms. Small barred vents in the plinth under each bay. | long_facade, east_door |
| Three tiers of sashes | Conforms. Six-over-six sashes (12 lights) with stone sills and flat projecting lintels on every plain bay. | long_facade, west_range, rear_north |
| Pavilion arches and fanlights | Conforms. Round arches with radial fanlights and keystones on both tiers. | end_pavilion_arches, east_door, balconettes |
| Pilaster strips | Conforms. Dressed strips every three bays with small capitals under the eave. | long_facade, front |
| Plinth | Conforms. | long_facade, east_door |
| Sill bands | Conforms. | long_facade |
| Eave cornice | Conforms. Modillioned, continuous across the ranges and the pavilion. | long_facade, end_pavilion_arches, portico |
| End pavilion: two arched tiers | Conforms. A shorter ground tier and a taller first tier. | end_pavilion_arches, right_side |
| End pavilion: grilles | Conforms. Iron bars in the ground-tier reveals. | east_door, end_pavilion_arches |
| End pavilion: south arched door | Conforms. Arched door with steps in the middle bay of the south face. | end_pavilion_arches |
| End pavilion: balconettes | Conforms. Iron balconettes on stone slabs at the foot of each first-tier window. | balconettes, east_door |
| End pavilion: main cornice | Conforms. Continues the range eave. | end_pavilion_arches |
| End pavilion: attic storey with sashes | Conforms. Three six-over-six sashes on each long face. Panel strips missing (P2 #5). | end_pavilion_arches, rear, front_corner |
| End pavilion: balustrade and top cornice | Conforms. Balustrade with pedestals on all four sides. | front_corner, right_side |
| End pavilion: hipped roof | **Deviates (P1 #1).** Double pyramid with central valley instead of one low hipped roof. Skylight and chimney are present. | top, front_corner, aerial |
| End pavilion: pediment with arched tympanum window | Conforms. Springs from the main cornice, raking cornices, round-arched fanlit window with keystone and sill. No oculus. Attic set back behind it. | right_side, front |
| End pavilion: east door and hood | Conforms. Corniced square door on consoles, with transom and three steps. | east_door |
| Portico: podium and steps | Conforms. | portico |
| Portico: giant-order columns to the eave | Conforms. Four Tuscan columns rise from the podium through all three storeys. | portico, front, front_corner |
| Portico: entablature | Conforms. Cornice top level with the range eave. Triglyphs simplified (P2 #3). | portico (crop) |
| Portico: pediment above the roof | Conforms. Has an oculus; tin roof runs back into the range roof. | portico, aerial, left_side |
| Dome attic: panels, pedestals, urns | Conforms. | dome_drum, rear_north |
| Drum: arched windows, engaged columns, entablature | Conforms. Sixteen-bay rhythm. | dome_drum, rear_north, left_side |
| Dome: ribs and profile | Conforms. Ribbed, slightly raised hemisphere, lighter silver than the stone. | dome_drum, right_side |
| Lantern, cupola, cross | Conforms. | dome_drum, front_corner |
| Roofs: hips and gable ends | Conforms for the ranges (low hips; portico gable). Deviates for the pavilion (P1 #1). | top, aerial, roofs_dormers |
| Roofs: chimneys | Conforms. | roofs_dormers, west_range |
| Roofs: vent dormers | Conforms. Small vent dormers on the court (north) slope of the east range. West vents simplified (P2 #6). | roofs_dormers, top |
| Roofs: skylight | Conforms. On the south slope of the west range, and on the pavilion. | top, west_range |
| North porch | Conforms. Flat-roofed, three open arches with depth, balustrade, central steps and door. | rear_north |
| Streets | Conforms. Streets and sidewalks on all four sides, plus a far south sidewalk in the front foreground. | top, aerial, front |
| Squares | Conforms. South-west square, and a north-east court plate. | top, west_range |
| Trees | Conforms. Trees on the south sidewalk, the south-west square and the north sidewalk. Extra north-east trees (P2 #6). | top, west_range |
| Materials hierarchy | Conforms, except the pavilion roof. Grey stone walls, darker blue-grey slate, lighter silver dome, lantern and portico tin, black iron. The pavilion roof facets read near-black (part of P1 #1). | left_side, rear_north, front_corner |

## 4. Camera validity

- **rear**: invalid as a whole-envelope view. The west end of the west range is clipped at the right frame edge (P1 #2).
- **front**: valid. The dome shows above the range roof to the left of the pavilion. The west range does not appear left of the portico. I checked this geometrically from the façade vanishing point and the top-view plan: with this camera's bearing, the west range falls behind the east range, so its absence is correct occlusion, not a missing mass.
- **aerial**: valid but small in frame. The building fills about 45% of the width. It is still legible.
- **interior**: valid. A window seen from inside, with reveal depth, sash and outside tree. Minimal content but legible.
- All other views (front_corner, top, left_side, right_side, rear_side, portico, dome_drum, end_pavilion_arches, balconettes, east_door, long_facade, roofs_dormers, west_range, rear_north): the target is unoccluded, unclipped and legible.

## 5. Previous-version (v001) findings: are they resolved in the pixels?

1. **Portico one storey too short: RESOLVED.**
   - In portico, front and front_corner, the four Tuscan columns rise from the stepped podium past the ground-, second- and third-floor windows.
   - In the portico zoom, the entablature cornice meets the range's modillioned eave at its return.
   - The pediment (with oculus) stands clear above the slate roof, and its tin roof runs back into the range roof (aerial, left_side, roofs_dormers).
   - The slot under the raking cornice is closed. Only a small cornice-return notch remains (P2 #4).
2. **End pavilion tier hierarchy and missing attic: RESOLVED, except one new defect in the same element.**
   - end_pavilion_arches, east_door, balconettes and right_side show the expected tiers. The ground tier is shorter and has barred arched windows, with an arched door and steps in the middle of the south face. The taller first tier has iron balconettes.
   - The main cornice continues the range eave.
   - Above it, an attic storey has three six-over-six sashes per long face, a top cornice and a balustrade with pedestals on all four sides.
   - The east pediment springs from the main cornice and carries a round-arched fanlit window with keystone. The oculus is gone.
   - However, the attic's own roof is not a low hipped slate roof: it is a double pyramid with a central valley and dark slots (new P1 #1).

The other v001 conformance points still hold:
- the plan (offset ranges, dome block, portico, porch)
- three tiers of sashes and basement vents on the plain bays
- the modillioned eave cornice
- the dome attic with panels, pedestals and urns
- the drum of arched windows between columns
- the ribbed dome, lantern, cupola and cross
- the chimneys, vent dormers and west skylight

The builder's other claimed changes are confirmed:
- the front camera shows the dome left of the pavilion
- the side cameras frame the hall
- the far south sidewalk is in place
- the dome is lighter silver
- the pilaster capitals are present
- the porch is wider

The narrower rear camera now clips the west end (P1 #2).
