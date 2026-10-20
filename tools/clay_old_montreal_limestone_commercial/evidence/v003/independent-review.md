# Independent holistic review: oldmtl v003 (RLASM v6.1 architectural clay)

Reviewer: independent; I did not build this. I judged only rendered pixels against the locked source pixels. I opened all 18 render PNGs, the three locked sources and the four phone boards at full resolution. Zoomed crops are in `/tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/crops-indrev-4dafab44/`, a new folder. No candidate file was changed.

## 1. Verdict

**VISUAL_REWORK_REQUIRED**: both v002 P1s are fixed in the pixels and every earlier fix still holds. One clearly visible rhythm and plan defect remains on the east end pavilion. Its east front has five narrow arched bays per tier, but both sources show three wide bays, and the pavilion is about 30 % too short east-west against the top view.

Counts: P0 = 0, P1 = 1, P2 = 7

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | right_side, front, front_corner, aerial, east_door, top (against sources oblique, front, top) | **The east pavilion has the wrong rhythm and plan proportion.** In the render the east front has **5 round-arched bays per tier**. The upper tier has 5 arched windows with balconettes. The ground tier has 4 grilled arched windows plus the corniced door in the third bay. All are separated by narrow piers. The oblique source shows **3 wide bays** on the east front: upper tier windows at about x 845, 940 and 1025, and on the ground tier a window, the corniced door, then a window. Broad pilaster piers separate them, and the tympanum window sits over the middle (door) bay. The front source agrees: two wide bays are visible before the crop, with the door in the second bay. In the top view the render pavilion inside its balustrade measures about 107 × 203 px (east-west ÷ north-south ≈ 0.53, about 16 % of the east range length). The source top measures about 153 × 200 px (≈ 0.77, about 24 % of the range length). The source pavilion is a near-square block; the render pavilion is a thin slice. This shows side by side on board phone-01 (front against front, oblique against front_corner). | The bay module of the long range (about 3.3–3.5 m) was reused on the east front, and the pavilion length was set to about 9–10 m instead of the source's ≈ 13–14 m. The east front was then filled with as many range-module bays as fit, not the source's three. | Lengthen the pavilion east-west to ≈ 0.75–0.8 × range depth (≈ 13.5 m at 17.7 m depth). Then rebuild the east front as **3 equal wide bays** with broad pilaster piers. The ground tier is a grilled arched window, the corniced square door on consoles with steps, and a grilled arched window. The upper tier is 3 tall arched fanlit windows with balconettes. Re-centre the tympanum fanlit window over the door bay, keep the pediment springing from the main cornice, and re-span the attic, balustrade pedestals and hipped roof to the new length. Keep the south front at 3 bays with the arched door in the middle, widening its bays to the new length. Re-render right_side, front, front_corner, aerial, top, east_door, end_pavilion_arches, balconettes and rear. |
| 2 | P2 | front_corner, aerial, rear | The pavilion chimney stands **in the line of the north balustrade**, interrupting it like a pedestal. In the oblique source the chimney stands clear of the balustrade, on the roof slope. | The chimney position was snapped to the attic's north-west perimeter. | Move the chimney about 1.5–2 m inboard onto the roof slope and close the balustrade run behind it. |
| 3 | P2 | top, front_corner | The pavilion skylight sits mid-west slope. In the source top and oblique it sits east of the chimney, toward the north half. | Placement only. | Shift the skylight north-east of the chimney when the pavilion is rebuilt (finding 1). |
| 4 | P2 | right_side | At the left (south) foot of the east pediment, the raking cornice overshoots the horizontal cornice end. A thin dark sliver shows between the raking cornice soffit and the tympanum. | The raking cornice box is not mitred to the horizontal cornice return. | Trim and mitre the raking cornice foot to the horizontal cornice return and close the soffit gap. |
| 5 | P2 | portico | The portico frieze carries plain square blocks. They read as triglyph positions but have no glyph grooves or metopes. | Simplified frieze. | Add two vertical grooves per block, or alternate block and metope relief. |
| 6 | P2 | top, aerial, rear | Two trees stand on the north sidewalk **east** of the dome block. The source top has north-side trees only along the west part, and the north-east is a court or square. The small annex on the dome block's east face (source top, x ≈ 710–760, y ≈ 390–510) is absent. | Landscape and annex simplification. | Drop or relocate the two north-east trees to the west north sidewalk. Optionally add the low annex block on the dome block's east face. |
| 7 | P2 | brief / boards | The brief names `facade_close`, `architecture_close` and `glass_close`, but none exists in `renders/` (18 files, which matches the stated count of 18) or on the boards. long_facade, balconettes, end_pavilion_arches, east_door and interior cover that detail. Silver tin is distinguished from limestone only by a small value step (dome ≈ RGB 154/159/162 against wall ≈ 113–133). | The view manifest and the brief list diverge. The clay palette is close in value. | Align the brief's view list with the rendered set, or render the three named close-ups. Optionally lift the dome and portico tin a little cooler and lighter for clearer material hierarchy. |

## 3. Source conformance checklist

| item | status | view(s) used |
|---|---|---|
| Silhouette (long hall, offset ranges, central dome, near pavilion with attic) | conforms, except that the pavilion is mis-proportioned (finding 1) | front, front_corner, aerial, rear |
| Storey count (3 storeys over a low basement) | conforms | long_facade, left_side, rear_north |
| Plan: west range in line with the dome block, east range stepped south by a full depth | conforms | top against source top |
| Plan: dome block | conforms (square, deck around drum) | top, dome_drum |
| Plan: portico (south, at the west end of the east range, under the dome block) | conforms | top, portico |
| Plan: north porch | conforms | top, rear_north |
| Plan: pavilion length | **deviates** (≈ 0.53 against ≈ 0.77 of depth, finding 1) | top against source top |
| Limestone coursing | conforms (fine horizontal coursing lines in clay) | long_facade, balconettes |
| Basement vents (barred) | conforms | long_facade, east_door, end_pavilion_arches |
| Three tiers of six-over-six sashes with stone sills and flat lintels | conforms | long_facade, west_range, rear_north |
| Pavilion arches and radial fanlights with keystones | conforms in detail; **deviates** in east-front bay count (5 against 3) | end_pavilion_arches, balconettes, east_door, right_side |
| Pilaster strips | conforms | long_facade, front, right_side |
| Plinth, sill bands, modillioned eave cornice | conforms | long_facade, front_dome crop, end_pavilion_arches |
| End pavilion: two tall arched tiers within the range height | conforms | end_pavilion_arches, front |
| End pavilion: ground-tier iron grilles | conforms | east_door, end_pavilion_arches |
| End pavilion: south arched door with steps in the middle bay | conforms | end_pavilion_arches |
| End pavilion: balconettes on the first tier | conforms (seated on sills, no float) | balconettes, east_door |
| End pavilion: main cornice continuing the range eave | conforms | end_pavilion_arches, rear |
| End pavilion: attic storey with six-over-six sashes on the long faces | conforms | end_pavilion_arches, rear |
| End pavilion: top cornice and balustrade with pedestals on all four sides | conforms | front_corner, right_side, rear |
| End pavilion: low hipped slate roof inside the balustrade | conforms (single north-south ridge) | top, front_corner, aerial |
| End pavilion: east pediment with arched fanlit tympanum window | conforms; foot mitre is P2 (finding 4) | right_side, front |
| End pavilion: east door and hood (corniced, on consoles, steps) | conforms, but sits in bay 3 of 5 rather than bay 2 of 3 | east_door |
| Portico: stepped podium and steps | conforms | portico |
| Portico: giant-order Tuscan columns through three storeys to the eave entablature | conforms | portico, front |
| Portico: entablature with triglyph blocks | conforms; glyph detail is P2 | portico |
| Portico: pediment with oculus above the slate roof; silver roof dying into the range roof | conforms | portico, front_corner, top |
| Portico: arched doorway behind | conforms | portico, fc_portico crop |
| Dome-block attic: sunk panels, corner pedestals with urns | conforms | dome_drum, rear_north |
| Drum: round-arched windows between engaged columns, entablature | conforms (about 8 visible per half, consistent with 16) | dome_drum, left_side, right_side |
| Dome: ribs and hemispherical profile | conforms | dome_drum, rear_north |
| Lantern, cupola and cross | conforms | dome_drum, front_dome crop |
| Roofs: hipped ranges | conforms | left_side, west_range, top |
| Roofs: chimneys | conforms (pavilion chimney placement is P2) | roofs_dormers, west_range |
| Roofs: vent dormers on the court slope | conforms | roofs_dormers, rear_north, top |
| Roofs: west-range skylight | conforms | west_range, top |
| Roofs: pavilion skylight | conforms (placement is P2) | top, front_corner |
| North porch: three arches, flat roof, balustrade | conforms | rear_north |
| Streets and sidewalks | conforms | top, aerial, front |
| South-west cobbled square with trees | conforms (untextured clay) | top, west_range |
| South-sidewalk trees | conforms | top, front |
| North-sidewalk trees | conforms on the west; extra trees on the north-east (P2) | top |
| Materials hierarchy | conforms: limestone grey, slate blue-grey, tin light grey, iron black, foliage green. Tin and limestone are close in value (P2). | dome_drum, long_facade, top |
| Faces no source shows (north, west, dome-block east, porch) | coherent with the visible grammar | rear, rear_north, left_side, roofs_dormers |

## 4. Camera validity

- All 8 whole-envelope views (front, front_corner, aerial, top, left_side, right_side, rear, rear_side) frame their target with no occlusion or clipping.
- **rear** now shows both ends with a margin: the east pavilion at x ≈ 175 and the west range's west hip and north-west corner at x ≈ 1355 of 1440.
- **left_side** crops only the bottom of the near basement vents at the frame edge. The full west face, hip and north-west corner are inside the frame. This is acceptable.
- All 10 detail views are legible, and their targets are unoccluded except for normal tree overlap in long_facade and west_range. **interior** is a legible view out through a sash window from inside a dark room.
- No view is invalid. The three close-ups named in the brief but not rendered are noted under finding 7.

## 5. Previous-version findings: resolved in the pixels?

**v002 P1 #1 (the pavilion roof rendered as two pyramids):** **Resolved.**
- The top view, zoomed, shows one hipped slate plate with a single north-south ridge and four hips. There is no "X" and no lit diamond valley.
- In front_corner and aerial the roof reads as one hipped plane set, in the range slate tone. There are no near-black facets and no cross-valley.
- In rear and right_side, the roof meets the balustrade with no black slivers or slots.
- The skylight is on the west slope. The chimney is at the north-west; its placement is a P2.

**v002 P1 #2 (the rear view cut off the west end):** **Resolved.** The west range's west hip, north-west corner strip and end face are fully inside the frame with about 85 px of margin, and the east pavilion has about 175 px.

**v001 P1 (the portico as a giant order):** **Still holds.** The columns rise from the stepped podium through three storeys to an entablature at the range eave line. The oculus pediment stands above the slate roof, and the silver roof dies into the range roof (portico, front_corner, top).

**v001 P1 (the pavilion grammar):** **Still holds.**
- The two arched tiers sit within the range height, with grilles on the ground tier, the arched door in the middle south bay and balconettes on the first tier.
- The main cornice continues the range eave.
- The attic storey has six-over-six sashes, a top cornice and a balustrade with pedestals on all four sides.
- The east pediment springs from the main cornice and has a round-arched fanlit tympanum window, with no oculus.
- The new P1 above concerns bay count and plan length, not this grammar.

**The dome above the range roof, left of the pavilion, in the front view:** **Still holds.** The dome, lantern, cupola and cross show above the range eave to the left of the pavilion. The drum is hidden by the eave, which the brief accepts as a consequence of the top-view plan.

**v001 conformance:** **Still holds.** The plan, the three sash tiers with basement vents, the modillioned eave and the dome-block attic with panels, pedestals and urns all hold. So do the arcaded drum, ribbed dome, lantern, cupola and cross, the chimneys, the court-slope vent dormers and the west skylight. The only deviation is the pavilion proportion and east rhythm in finding 1.
