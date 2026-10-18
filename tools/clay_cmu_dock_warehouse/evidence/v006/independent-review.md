# Independent holistic review: clay-cmu-dock-warehouse v006 (RLASM v6.1 architectural clay)

Reviewer: independent (not the builder). Basis: rendered pixels against the locked source pixels only. I opened all three locked sources (`sources/front.png`, `sources/oblique.jpg`, `sources/top.jpg`), all 18 renders at full resolution and the four phone boards. Zoomed crops were written only to the new folder `/tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/wh-v006-indep-crops-k7q2/`. I did not use builder metadata, counts, hashes or notes as proof.

## 1. Verdict

**PASS_ZERO_P0_P1**: the v006 pixels show a single-storey beige CMU box on a dock-height base, with the correct south-face dock band, entry, landing and east-face fenestration (now one low window and three evenly spaced high windows matching the oblique). No identity, topology, contact or camera defect remains; only polish-level deviations are left.

Counts: P0 = 0, P1 = 0, P2 = 7

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P2 | dock_doors, facade_close, front vs source front/oblique | Each sectional dock door has a row of four small, evenly spaced lites. The source doors show two wider lites, one toward each jamb (clearest in the source front crop and in the oblique). | Generic lite-row parameter (count 4, centred) | Set the lite count to 2, place them at about 1/4 and 3/4 of the door width and widen each lite slightly |
| 2 | P2 | top, facade_close, front vs source top/front | The four dock surrounds sit almost edge to edge, with a gap of about 5% of the surround width. In the source they are separated by visible strips of beige CMU (about 7% to 25% of the surround width in the top view). The band's overall extent (about 10% to 62% of the south face) matches. | Surround width or pitch tuned to fill the band | Hold the band extent and reduce each surround's width by about 8%, or enlarge the gaps to about 0.15 of the surround width |
| 3 | P2 | entry_canopy, glass_close, top vs source oblique/top | The canopy is a plain solid slab. In the oblique and top sources its upper face is ribbed or louvred. The flat profile, rod hangers and coverage are correct. | Slab primitive with no top relief | Optionally add 6 to 8 shallow transverse ribs on the top face. Keep the flat silhouette. |
| 4 | P2 | glass_close, front, architecture_close vs source front/oblique/top | The wide entry window has three lights (two mullions). The source shows two lights with one central mullion. Size, head height, sill and spacing to the door all match. | Default mullion count | Set the mullion count to 1 (centred) |
| 5 | P2 | east_windows, right_side, front_corner vs source oblique | The east clerestories are single-pane. In the oblique the high windows read as 2x2 divided lights (the rear north window already uses that grammar). | Muntin grid not applied to the east clerestory type | Apply the 2x2 muntin grid to the three east high windows |
| 6 | P2 | front, left_side, right_side, rear, rear_side, aerial | The front camera is wider than the locked front: the building fills about 62% of the frame width against about 90% in the source. The elevation-type views show the building at about 28% of the frame width. Everything stays legible and nothing is clipped. | Conservative framing distance | Tighten the front FOV or distance to match the source framing. Optionally frame the elevations to about 60% of the width. |
| 7 | P2 | right_side, east_windows vs source oblique | The low east window sits slightly farther from the south-east corner (about 8% of the face length) than in the oblique, where it almost touches the corner reveal. | Corner offset parameter | Reduce the corner offset by about half |

## 3. Source conformance checklist

| Item | Status | View(s) used | Notes |
|---|---|---|---|
| Silhouette | conforms | front, front_corner, aerial, top, rear_side | Single flat-roofed rectangular box with no setbacks, matching the oblique and top sources |
| Height and proportions | conforms | top, right_side, rear, front | Plan aspect about 1.31 (top: 445 x 340 px) against the source's about 1.3. Single storey. The south-face length-to-height ratio at the west end is about 3.4 against the front source's about 3.3. |
| CMU coursing | conforms | facade_close, glass_close, entry_canopy, rear_north, architecture_close | Beige running-bond CMU with horizontal coursing and visible head joints on every face. No regression. |
| Dock bays: doors | conforms | front, facade_close, dock_doors | Four overhead sectional doors with horizontal panel joints. The door aspect (about 0.45 W:H) and height relative to the surround match the front source. Door height has not regressed. |
| Dock bays: lites | deviates (P2 #1) | dock_doors | A row of four small lites against two in the source |
| Dock bays: surrounds | conforms (spacing P2 #2) | facade_close, dock_doors, front | Dark steel surrounds with a projecting head and jamb pads. The door is recessed with a visible jamb return. |
| Dock bays: bumpers | conforms | facade_close, dock_doors | Black bumper blocks below each leveller lip, in contact with the dock face |
| Dock bays: guides | conforms | facade_close, front, front_corner | A yellow guide post at each jamb of all four bays, standing on the apron. No regression. |
| Dock bays: dock height and base | conforms | facade_close, front | A raised concrete dock plinth runs under the band. Leveller lips sit at dock height. The surrounds rise to about 0.47 of wall height, as in the source. No regression. |
| Dock band position and rhythm | conforms | top, front | The band runs from about 10% to 62% of the south face, the same as the source top. Four equal bays. No regression. |
| Entry: door and sidelight | conforms | glass_close, front | An aluminium-framed glazed door and sidelight of similar width, recessed in the CMU |
| Entry: canopy | conforms (top relief P2 #3) | entry_canopy, glass_close, front, front_corner | Flat canopy about 2.1 times the door-plus-sidelight width, biased west, as in the source |
| Entry: rods | conforms | entry_canopy, front, front_corner | Two dark rods run from wall anchor plates to the canopy's outer edge, in contact at both ends |
| Entry: window | conforms (mullions P2 #4) | glass_close, front | Window-to-door width about 1.5 against the source's 1.42. The door-to-window gap matches (about 0.55 of door width). The head is slightly above the door head. Projecting sill. Entry spacing has not regressed. |
| Landing and steps | conforms | front, front_corner, top | A long cast-concrete landing runs from just east of dock 4 to the window's east end, with steps at its west end descending west, as in the source top. The door sill meets the landing. No regression. |
| East windows | conforms (P2 #5, #7) | front, front_corner, right_side, east_windows, architecture_close | One low two-light window near the south corner and **three** high clerestories. In front_corner their positions along the face are 0.46, 0.69 and 0.87; in the oblique they are 0.47, 0.71 and 0.89. |
| Parapet and coping | conforms | parapet_corner, roof_units, rear_north, front | A low flat parapet with a thin, pale, continuous metal coping and a beige inner parapet face. Clean corner mitre. No regression. |
| Roof: membrane | conforms | top, roof_units, front_corner | Grey membrane with seam lines |
| Roof: rooftop units | conforms | top, roof_units, aerial | Two RTUs side by side, central and slightly north of centre, as in the source top |
| Roof: vent domes | conforms | top, front_corner | Four small domes near the roof corners, as in the source top |
| Roof: pipe vents | conforms | roof_units, parapet_corner, top | Several thin pipe vents |
| Apron and site | conforms | front, front_corner, aerial, top | Street on the south. A concrete dock apron and sidewalk. An asphalt lane with parking stalls on the east and an asphalt drive on the west. Massing-level cars and trees only. |
| Materials hierarchy | conforms | all | Beige CMU dominant, dark dock surrounds, pale coping, grey membrane, light concrete landing and apron, yellow guides, aluminium frames. Untextured, source-palette clay. |
| North and west faces (no source; coherence only) | conforms | rear, rear_north, left_side, rear_side | High square windows in the same grammar, and a hollow-metal rear door on a concrete stoop with steps and handrails, all in contact. The rear door has not regressed. |

## 4. Camera validity

All 18 cameras are valid. In every view the target is visible and unoccluded, the asset is not clipped where the view's role needs it, and the subject is legible:
- front: the east face runs off the right edge, as it also does in the locked front. The south face is complete.
- front_corner, aerial, rear_side: the whole envelope is visible.
- top: true nadir, the whole plan is visible, and the trees do not overlap the roof.
- left_side, right_side, rear: the whole face is visible but small (P2 #6).
- Details (facade_close, architecture_close, glass_close, dock_doors, entry_canopy, roof_units, east_windows, parapet_corner, interior, rear_north): each frames its named target and none is occluded. dock_doors and facade_close crop off the outer bays on purpose.
- interior: the camera is inside the envelope and shows a legible racked aisle with a far-wall clerestory. There is no clipping through the envelope.

Cameras have not regressed.

## 5. Previous-version findings: resolved in the pixels?

| Previous finding | Status in v006 pixels | Evidence |
|---|---|---|
| v005 P1: the east face showed two high windows against three in the oblique, leaving the north 40% blank | **RESOLVED** | front_corner, right_side, architecture_close, parapet_corner and front all show three evenly spaced high windows. front_corner positions 0.46, 0.69 and 0.87 against the oblique's 0.47, 0.71 and 0.89. The north part of the face is no longer blank. |
| Dock band extent and rhythm | not regressed | top: about 10% to 62% of the face, four equal bays |
| Entry spacing | not regressed | glass_close, front |
| Landing | not regressed | front, front_corner, top |
| Cameras | not regressed | Section 4 |
| Door height (dock doors) | not regressed | front, dock_doors |
| Dock base | not regressed | facade_close |
| Coping | not regressed | parapet_corner, rear_north |
| Head joints | not regressed | facade_close, glass_close, rear_north |
| Guide posts | not regressed | facade_close, front |
| Rear door | not regressed | rear_north, rear, rear_side |
