# Independent holistic review — sand v003 (RLASM v6.1 architectural clay)

Reviewer: independent; judged only the rendered pixels against the three locked sources (front.png, oblique.jpg, top.jpg). I opened all 18 renders and the 4 phone boards at full resolution. Zoomed crops are in `/tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/crops-rv-1500331824/`.

## 1. Verdict

**VISUAL_REWORK_REQUIRED** — the three v002 defects are fixed in the pixels and nothing invalidates the candidate, but the clock tower, the main landmark, is clearly too short and squat compared with the source. That is one P1.

Counts: P0 = 0, P1 = 1, P2 = 9

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|----------|---------|-------------------------------|--------------|------------|
| 1 | P1 | right_side, east_side, front, clock_tower, gables_pinnacles (vs source front, oblique) | The clock tower barely clears the main roofs. In the right_side elevation, the tower's top cornice (y≈440) is below the copper finials of the corner pavilion pyramids (y≈410). The clock faces (y≈500) sit below the pavilion apexes, about at the wing roof ridge. Total height with spire is only ≈1.3× the pavilion pyramid height. In source front, the clock stage and belfry stand well above every roof (clocks at y≈225 against the nearest pavilion apex at y≈365), and the tower is about 2× the pavilion height. The spire is also a broad **four-sided** pyramid with height:base ≈ 1.0. The source spire is a slender **octagonal/conical** copper spire with height:base ≈ 1.4–1.8. Together these lose the soaring tower silhouette that defines this building. | The tower shaft and clock/belfry stages are scaled to the wing's storey heights instead of the source's tower proportion. The spire is modelled as a 4-segment pyramid. | Raise the tower shaft so the clock stage sits wholly above the pavilion pyramid apexes, with the belfry arcade above that, matching source front: belfry cornice ≈ 1.8× eave height and spire tip ≈ 2.2–2.4× eave height above grade. Rebuild the spire as an 8-sided (or 16-sided) copper cone, height ≈ 1.5× its base, set inside the four corner turrets. Re-render front, right_side, east_side, clock_tower and front_corner. |
| 2 | P2 | east_side, right_side, clock_tower | Tower shaft has one pair of lancets plus two single arched windows. The source shaft shows tall clustered lancets (about 4 per face) running about 2 storeys. The belfry arcade has 3 small arches per face where the source has 5–6. | Simplified opening schedule on the tower. | Use a 4-light tall lancet cluster in the shaft and 5–6 belfry arches per face. |
| 3 | P2 | facade_close, glass_close, front | The basement is the same plane and colour as the upper wall: no rustication, no projecting plinth. Only faint horizontal course lines suggest rock-faced coursing. | Clay wall uses one uniform surface with incised course lines. | Give the basement a slight projection or deeper banded courses, and strengthen course grooves on the upper walls. |
| 4 | P2 | portal_arch | The SW portal is deep, with a vault, steps, colonnettes and a balcony, which is good. Its back wall is a blank plane with only a hairline jamb, under a black lunette. The door leaves are not differentiated. | Back plane modelled as a single slab. | Add a recessed paired door leaf with frame below the lunette transom. |
| 5 | P2 | roofs_court, front_corner, aerial | The light-court walls carry plain punched rectangular windows with no string courses or arched heads. The oblique source shows arched court windows and coursing. | Court elevations use a reduced opening module. | Carry the string courses and the arched second-floor tier into the court elevations. |
| 6 | P2 | top | The frame is tight. The south-west entrance porch projecting from the south face is cut by the bottom frame edge, and the south sidewalk is cropped. | Ortho extent fitted to the main envelope, not the projections. | Widen the ortho scale by about 5% so porches, sidewalks and some street show on all four sides. |
| 7 | P2 | aerial | The building fills only about 30% of the frame width. It is still legible, but detail is lost compared with the oblique source framing. | Camera distance. | Move the camera closer and keep the four-street context in frame. |
| 8 | P2 | facade_close, front (vs source front) | In the source front, the central bay between the SW pavilion and the tower reads as a slightly projecting gabled block with tall arched windows. The render has a dormer gable over a flat wing face. | Mid-wing gable modelled as a roof dormer only. | Project the 3–5 central bays slightly under the gable. |
| 9 | P2 | interior | The view looks out through a glazed opening with visible jambs, so the opening is through. The arch head is out of frame, so this view does not show the round-arched identity of the window. | Camera tilt/height. | Tilt the camera up or step back slightly so the arched head is in frame. |

## 3. Source conformance checklist

| item | status | view used |
|------|--------|-----------|
| Silhouette | deviates: the tower is too short and squat relative to the pavilion pyramids (finding 1); otherwise the stepped pavilion/wing skyline matches | right_side, front vs source front |
| Storey count | conforms: rusticated-basement level plus paired-rectangular, round-arched and arcade tiers, with attic gables | facade_close, left_side, rear_north |
| Plan | conforms: square block with corner pavilions, a square central light court, and the tower at the middle of the east front | top vs source top |
| Court and pavilion projection | conforms: corner pavilions project from the wings on both faces; the court is open and deep | top, roofs_court, front_corner |
| Sandstone coursing | conforms for clay (faint course lines, buff source palette); rustication is weak (P2 #3) | glass_close, facade_close |
| Window tiers: basement | conforms (small basement windows on every bay) | facade_close, left_side |
| Window tiers: paired first floor | conforms (paired rectangular windows with lintels and sills) | facade_close, es crops |
| Window tiers: tall arched second floor | conforms (round-arched windows with archivolts and deep reveals) | glass_close, facade_close |
| Window tiers: third-floor arcades | conforms (groups of 4 small arches with colonnettes) | facade_close, left_side |
| String courses and eave cornice | conforms (continuous string courses at each tier, dark eave cornice band) | facade_close, architecture_close |
| Gables and pinnacles | conforms (coped gables with 3-light windows and flanking pinnacles on both outward faces of each corner pavilion) | architecture_close, gables_pinnacles, top |
| Roofs: wing hips | conforms | front_corner, roofs_court |
| Roofs: pavilion pyramids | conforms (steep slate pyramids with copper finials) | front_corner, rear_side |
| Roofs: cross gables | conforms (mid-wing gables on N/S/W; inner cross hips at the court) | top, rear_north, left_side |
| Portal | conforms (deep round-arched portal in the SW pavilion with steps, colonnettes and a balustraded balcony; door detail is P2 #4) | portal_arch, front |
| Clock tower: projection | conforms (projects from the east wing, with a projecting arched porch, steps and balustraded balcony at its foot) | front_corner, top, east_side |
| Clock tower: lancets | deviates (sparse paired lancets, P2 #2) | east_side |
| Clock tower: clocks | conforms (clock faces on four sides) | clock_tower, rear_side |
| Clock tower: belfry | conforms in position (arcade above the clocks); deviates in count (3 arches, P2 #2) | clock_tower |
| Clock tower: turrets | conforms (four corner turrets with copper conical caps) | clock_tower, top |
| Clock tower: spire | deviates (too short, four-sided and squat, P1 #1) | clock_tower, right_side vs source front/oblique |
| Streets and trees | conforms (sidewalk and street ring on all four sides; low-poly street trees, sparser than the source but acceptable for clay) | aerial, front_corner, top |
| Materials hierarchy | conforms (buff stone walls, lighter stone trim and copings, dark slate roofs, copper spire, turret caps and finials, dark glazing) | front_corner, architecture_close |

## 4. Camera validity

- All 18 views are legible and on target. No view has its target occluded by trees or geometry; the trees in front, facade_close and portal_arch cover only part of the façade.
- **top**: tight framing clips the SW entrance porch and south sidewalk at the bottom edge (P2 #6). The building envelope is otherwise complete. This does not invalidate the view.
- **aerial**: valid but distant (P2 #7).
- **interior**: valid. It looks through the glazing to the exterior, but the arched head is out of frame (P2 #9).
- No invalid camera, so there is no P0 here.

## 5. Previous-version findings (v002: 1 P0, 2 P1)

1. **v002 P0: outer bays of the corner-pavilion east and west faces filled with stone.** **Resolved in pixels.** east_side (crops es_left/es_right), left_side and right_side (crops ls/rs) show the pavilion E/W faces with open windows across the face: a 3-light arched group over 3 tall lights, a 3-arch arcade, a single arched window, paired rectangular windows and basement windows. Several show interior light or a view through to the court. Only a narrow corner pier is solid. No stone-filled bays remain. (Note: the builder describes "only the inner side bay" on these faces, but the pixels show a fuller multi-bay face. That is fine, because the pixels govern.)
2. **v002 P1: no projecting arched entrance porch with a balustraded balcony at the foot of the clock tower.** **Resolved in pixels.** The fc_porch crop shows a block projecting forward of the tower shaft, with a round-arched opening, colonnettes, steps, a landing and a balustraded balcony on top. east_side and right_side show it frontally, and top shows its footprint beyond the tower.
3. **v002 P1: interior view showed openings as blind recesses with solid backs.** **Resolved in pixels.** The interior view looks through a glazed, mullioned opening with lit jamb returns on both sides, out to sky and ground beyond. It is not a solid back. portal_arch also shows a ground-floor window reading through to a court window. The arched head is not in frame (P2 #9 only).
