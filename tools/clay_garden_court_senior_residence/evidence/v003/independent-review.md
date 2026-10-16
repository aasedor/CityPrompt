# Independent holistic review: garden-court senior residence, v003 (RLASM v6.1 clay)

Reviewer: independent; no relationship with the builder. I judged only the rendered pixels against the three locked sources (`sources/front.png`, `sources/oblique.jpg`, `sources/top.jpg`). I opened all 18 renders at full resolution and checked the four phone boards. I made zoomed crops into a new scratch folder, `indep-review-v003-crops/`. I did not use metadata, hashes or the builder's notes as proof.

## 1. Verdict

**VISUAL_REWORK_REQUIRED.** The v003 fixes clear all four v002 P1s in the pixels. Two new visible defects still block approval: a pure-black void slot under the garden-room French doors in `interior`, and a loggia roof ridge that runs into a second-storey window in `facade_close`.

Counts: P0 = 0, P1 = 2, P2 = 11

## 2. Findings

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | interior | A solid black band runs the full width of the court-side French doors, between the door's bottom rail and the interior floor (about 20 px tall at 1440 px wide). It samples as pure black, RGB (1,1,1), and has no shading. It reads as a void slot into an unlit cavity, the same failure class as the v002 plinth slots. It is not visible from outside, where the threshold step reads correctly in `court_view` and `architecture_close`. | The new threshold step and door frame sit below or apart from the interior floor slab. The camera sees into a closed, unlit gap between the bottom of the door leaf or frame, the slab edge and the step. | Raise the door frame's bottom rail or sill so it sits on the interior floor top, or extend the floor slab under the threshold so the gap closes. Give the sill an inner face in sill or floor material. Re-render `interior` and check that no pixel row under either door (south and north) is below about RGB 20. |
| 2 | P1 | facade_close | The copper hip/ridge of an abutting one-storey loggia roof meets the pavilion wall above a second-storey window's sill. The ridge cap ends against the glass and the roof surface covers the lower sash and the whole sill. The roof plane cuts through the opening. Clearance is also very tight at other loggia junctions (court_view, NW pavilion: the loggia roof top reaches the window sill line). | The loggia ridge height and the pavilion's window grid were placed independently. No window is suppressed or lowered where a loggia roof abuts. | Do one of two things: lower or hip back the loggia roof so that its highest wall junction stays at least about 0.3 m below the lowest sill above it, or omit or blank that window bay on every face where a loggia abuts. Apply the rule at all six loggia–block junctions and re-render `facade_close` and `court_view`. |
| 3 | P2 | loggia_arcade, pergola_terrace | A dark, sharp-edged band (RGB about 24,23,11) runs under every cream water table at grade. It reads more like a reveal or a slight lift than ground contact. | Plinth base is set fractionally above the grade plane, or a dark footing face. | Seat the plinth bottom 2–3 cm below grade. |
| 4 | P2 | glass_close, architecture_close | Each garden-room door bay is a solid white panel with a transom and an inset two-leaf door. The source shows full-height multi-pane glazed French doors in a glazed bay. | Door bay modelled as a wall with a cut opening. | Glaze the side panels and add muntins to the doors. |
| 5 | P2 | pergola_terrace | Chairs no longer pass through the tables, but they are all rotated the same way, so several face sideways or away from their table. A tiny black pinhole shows at each seat–back joint. | One chair yaw is used for every chair. | Orient each chair to face its table and close the seat–back joint. |
| 6 | P2 | front, front_corner | Gables of the far-slope dormers still show as "teeth" above the south wing and pavilion ridges. | Dormer ridge close to the main ridge height. | Lower dormer ridges or move them down-slope. |
| 7 | P2 | facade_close, loggia_arcade | Brick coursing lines are coarse, with wide spacing. | Coursing texture scale. | Halve the course spacing. |
| 8 | P2 | court_view, front | The court is still sparsely planted. Rose beds are pink octagonal slabs with one small tuft each, and the lawns are mostly empty compared with the source's dense beds. | Low planting count. | Add rose mounds and border shrubs along the paths. |
| 9 | P2 | court_view, garden_beds | The fenced kitchen garden shows no gate where the paths meet it. | Fence modelled as a closed run. | Leave a gate gap on the path axis. |
| 10 | P2 | left_side, right_side, rear | The asset fills only a thin horizontal strip (under about 15% of the frame height). | Long camera distance. | Tighten the framing. |
| 11 | P2 | glass_close, interior, court_view | A grey veil or haze still lowers contrast through the glass and over close views. | Glass or world fog settings. | Lower the glass roughness and haze. |
| 12 | P2 | loggia_arcade | The tree canopy (top-left, about 25% of the frame) and a cream column (right edge) still crowd the arcade. | Camera placement. | Move the camera about 1 m to clear both. |
| 13 | P2 | all whole-envelope views | There is no outer street entrance on any block. The forecourt door of the garden room is the only exterior entry. | The sources do not show the outer faces. | Optional: add a modest entrance on the west street face. |

## 3. Source conformance checklist

| Item | Status | View(s) used |
|---|---|---|
| Silhouette | conforms. Ring of three-storey hipped copper blocks with a central octagon and cupola; massing reads as the source complex | front vs source front; front_corner vs oblique |
| Storey count | conforms. Three brick storeys plus a dormer attic; one-storey loggias | rear, left_side, right_side, facade_close |
| Plan (ring of blocks, court) | conforms to the top source. Two north pavilions, SW pavilion, long east wing, long south wing, loggia links, enclosed court | top vs source top |
| Roofs and dormers | conforms. Pavilions are hipped to a flat top with rooftop units; wings are hipped to a ridge; gabled dormers on the long slopes. Far-slope dormer teeth are P2 | top, dormer_roof, front |
| Loggias and arches | conforms. Round-arched brick arcades with brick-tone archivolts, cream imposts and copper roofs; full-length links. The roof-into-window collision is P1 #2 | loggia_arcade, court_view, rear |
| Garden room and cupola | conforms. Octagonal glazed room with a copper standing-seam roof, glass dome cupola and finial; doors on the south and north. Door-bay solidity is P2; the interior threshold void is P1 #1 | architecture_close, hub_cupola, glass_close, rear |
| Window rhythm and balconies | conforms. Regular white double-hung windows with cream heads and sills; arched garden doors with iron balconies above on the court faces | facade_close, interior, court_view |
| Garden elements (paths, fountain, beds, pergola) | conforms. Brick-tone path ring and cross axes, tiered fountain with upper bowl and finial, fenced raised timber beds, slatted timber pergola over a dining terrace. Planting density is P2 | court_view, garden_beds, pergola_terrace, top |
| Forecourt | conforms. Circular lawn with cross paths and a tiered fountain; the drive loop now joins the north street at two throats | top, hub_cupola, rear_side |
| Materials hierarchy | conforms. Red brick walls, cream trim and water tables, copper roofs, white frames, black iron, timber beds and pergola | all close views |

## 4. Camera validity

- **No view is invalid.** No target is occluded, no asset is clipped, and no view is illegible.
- **Small framing (P2 #10):** `left_side`, `right_side` and `rear` show the whole asset but very small.
- **Partial occlusion (P2 #12):** in `loggia_arcade` the tree canopy and a column partly occlude the frame, but the arcade, piers, archivolts and plinth junction are all legible.
- **Close views:** `glass_close`, `interior`, `facade_close`, `dormer_roof`, `hub_cupola`, `garden_beds` and `pergola_terrace` each frame their target legibly.
- **Court view:** `court_view` is a valid source-matched view into the court.

## 5. Previous-version (v002) findings: status in the pixels

| v002 finding | Status | Evidence |
|---|---|---|
| P1 solid black band under every copper eave | **Resolved** | front and court_view crops, loggia_arcade, architecture_close, dormer_roof: the eaves show the fascia and soffit with no black band |
| P1 black void slots at plinth junctions; loose stub block | **Resolved** | loggia_arcade: the block's water table and the loggia plinth meet cleanly. The front_sw and front_se crops show continuous plinths at the wing corners and no stub. A residual dark grade line is P2 #3 |
| P1 garden room has no doors; paths end at glass | **Resolved** | court_view and architecture_close: south French doors under a transom with a threshold step meeting the path. rear: north door bay facing the forecourt path. This introduced the new P1 #1 interior void |
| P1 drive loop not connected to any street | **Resolved** | top and rear_side: both curved ends of the loop join the north street |
| P2 far-slope dormer teeth | Not resolved | front (P2 #6) |
| P2 coarse coursing | Not resolved | facade_close (P2 #7) |
| P2 faceted cream archivolts | Resolved | loggia_arcade: brick-tone, smoother archivolts |
| P2 sparse court planting | Not resolved | court_view (P2 #8) |
| P2 low court fountain | Resolved | court_view: tiered basin, upper bowl, cap and finial |
| P2 chair through a table; no pergola slats | Resolved (chairs clear; slat layer present); new orientation issue is P2 #5 | pergola_terrace |
| P2 loggia_arcade crowded by mullions | Partly resolved | No mullions now, but the canopy and a column intrude (P2 #12) |
| P2 thin side framing | Not resolved | left_side, right_side (P2 #10) |
| P2 no outer entrance | Not resolved | P2 #13 |
| P2 glass haze | Not resolved | glass_close, interior (P2 #11) |
