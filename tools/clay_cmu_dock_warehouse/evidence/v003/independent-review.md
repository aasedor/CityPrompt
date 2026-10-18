# Independent holistic review: wh / v003 (RLASM v6.1 architectural clay)

Reviewer: independent; I did not build this candidate. I judged rendered pixels against locked source pixels only. I opened all 18 renders, the 3 sources and the 4 phone boards at full resolution. Zoomed crops are in `/tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/indep-review-wh-v003-crops/`.

## 1. Verdict

**VISUAL_REWORK_REQUIRED**: v003 fixes the dock height and adds the concrete dock base, but there are still two P1 defects. The dock-bay rhythm is wrong: the shelters are too narrow and separated by wide CMU piers, where the source shows them almost touching. The front camera still has the wrong vantage and vertical framing.

Counts: P0 = 0, P1 = 2, P2 = 11

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | facade_close, dock_doors, top, front, front_corner, aerial | **Dock-bay rhythm and width are wrong.** In the source the four dark shelters stand almost shoulder to shoulder. The gap between shelters is about 7–18% of a shelter's width (source top: shelters 230/215/215/210 px with gaps of 15/40/35 px at 2x; source front gaps of 8–13 px between shelters 52–92 px wide). In the render the shelters are narrow and set apart by CMU piers about half a shelter wide: facade_close (frontal) shows a 285 px shelter and a 153 px gap (54%), and the top view shows 125 px shelters with 73 px gaps (58%). Each shelter is about 9.3% of the south-face width against about 13% in the source. Each door is about 5.6% of the face width against about 7.3%. The tight, heavy band of dock seals that defines the source has turned into four separate punched openings. | The doors were narrowed to 1.9 m to bring the door head down to about 45% of the wall, but the bay pitch was kept. Door width and shelter width shrank while the spacing between bays did not. | Keep the 3.0 m door height and the 1.0 m dock floor, because the height ratio is now right. Widen each door to about 2.5 m and each shelter to about 4.2–4.5 m outer width. Set the clear gap between shelters to about 0.3–0.6 m and keep the bay pitch at about shelter width plus that gap. Place the group so that it runs from about 12% to about 62% of the south-face length from the west corner. This matches the source top, where the render group now starts at about 5.6%. Re-render front, front_corner, aerial, top, facade_close and dock_doors. |
| 2 | P1 | front | **The front camera still does not match the source vantage, and the lower part of the frame is empty.** The east face now reads well: it takes about 20% of the frame width, the same as the source, so that part of the v002 finding is fixed. The camera is still too close to the SE corner and pitched down. The horizon sits at about 54% of the frame height, against about 73% in the source. The bottom 35–40% of the frame is empty asphalt and sidewalk, against about 17% in the source. The south face converges much harder: the west-end wall is about 0.34 of the corner height in the render and about 0.50 in the source. As a result the four dock bays take up only about 17% of the frame width (x 490–735 of 1440), against about 31% in the source (x 113–430 of 1024). | The camera was moved closer and lower to show more of the east face. It is wide-angle, sits near the corner and is aimed slightly down. | Pull the camera back along its view axis by about 1.5x and narrow the FOV to match. Keep the eye height at about 1.4–1.6 m. Pitch the camera up, or use a vertical lens shift, so that the horizon sits about 73% down the frame. The south face should then span about 70% of the frame width, with the bays at about 10–42%. |
| 3 | P2 | facade_close, front, aerial | The cast-concrete dock base is now there as a continuous band under the bays. Its tone (RGB about 154,153,148) is almost the same as the apron (about 159,159,157) and the CMU (about 150,145,132), so at front and aerial scale it reads only faintly or as separate per-bay pads. In the source it is a clearly distinct weathered-concrete band. | Same light-grey material as the apron. | Make the base a mid-grey concrete about 15–20% darker than the apron so that it reads as its own band. |
| 4 | P2 | dock_doors, facade_close | The shelters are charcoal (about 74,72,71). The source surrounds are near-black and brown-black (about 29,26,17). | Value too light. | Darken the shelter material to about 35–45 luminance. |
| 5 | P2 | front, facade_close | The yellow guides are free-standing bollards placed out on the apron. In the source they are slim yellow guide posts mounted against the lower outer jambs of each shelter. | Generic bollard component. | Use slim posts hard against each shelter jamb at the base. |
| 6 | P2 | dock_doors, front | Each door has 4 lites. The source front and oblique show 2 dark lites per door. | Lite count. | Use 2 lites per door. |
| 7 | P2 | glass_close, entry_canopy | The entry is two equal glass panels with no handle or hardware, so door and sidelight cannot be told apart. The canopy soffit sits about 0.4 m above the door head, while in the source the canopy sits tight on the door head. | Simplified storefront; canopy set too high. | Give the door a stile, a pull handle and a narrower sidelight. Lower the canopy to about 0.1 m above the frame head. |
| 8 | P2 | glass_close, architecture_close | The wide window beside the entry has 3 panes. The source shows 2 (one central mullion). | Mullion count. | Use 2 panes. |
| 9 | P2 | front, front_corner, architecture_close | The landing is a plain box. The source landing has a projecting cast cap over a recessed body. | Missing cap reveal. | Add a cap about 0.05 m proud with a shadow reveal. |
| 10 | P2 | top, roof_units | The vent domes are modelled as flat boxes and pushed close to the roof corners (x at about 11% and 80% of the width). In the source they are low domed curbs further in (x at about 22–35% and 69–77%). The membrane seams run N–S, while in the source they run E–W, parallel to the south face. | Placement and primitive choice; seam direction rotated. | Move the domes in, round their tops, and rotate the seam pattern 90 degrees. |
| 11 | P2 | front | The second east clerestory is cut by the right frame edge. The source front shows both clerestories. | Framing (this goes away with the fix for #2). | Covered by the camera fix in #2. |
| 12 | P2 | top | The landing runs to about 95% of the south-face length, against about 91% in the source. The steps sit at about 63–68%, against about 66–71%. | Small offsets. | Shift the landing and steps about 1 m west and shorten the landing's east end by about 1 m. |
| 13 | P2 | top | The rooftop units sit slightly south of their source position (about 40% of the depth from the north edge, against about 31%). | Placement. | Move both units about 3 m north. |

## 3. Source conformance checklist

| Item | Status | View(s) used | Note |
|---|---|---|---|
| Silhouette | conforms | top, front_corner, aerial, rear_side | Single low flat-roofed box. The plan is about 1.33 wide to 1 deep (446 by 335 px in the top view), matching the source's about 1.3. |
| Height and proportions | conforms | front, facade_close, left_side, rear | Single storey on a dock-height floor. The wall-height-to-plan relationship is plausible against the oblique. |
| CMU coursing | conforms | facade_close, glass_close, east_windows, rear_north | Painted beige running-bond block with horizontal coursing, visible on all faces. |
| Dock bays: doors | deviates (P1 #1) | facade_close, dock_doors, top | The head height is now right (door head about 44–47% of the wall; source about 44%). The doors are too narrow relative to the face. |
| Dock bays: lites | deviates (P2 #6) | dock_doors | There is a row of lites, but 4 per door against 2. |
| Dock bays: surrounds | deviates (P1 #1, P2 #4) | facade_close, top | The shelter head is at about 51–55% of the wall (source about 53%), which is correct. The shelters are too narrow and spaced too widely, and slightly too light. |
| Dock bays: bumpers and lip | conforms | dock_doors, facade_close | There is a dark steel leveller lip shelf at each sill and two black bumpers under each bay, all in contact. |
| Dock bays: guides | deviates (P2 #5) | facade_close, front | These are yellow bollards rather than jamb-mounted guides. |
| Dock bays: dock height and base | conforms (tone P2 #3) | facade_close, dock_doors | A continuous concrete base takes up about 10.5% of the wall height (source about 13%), which is about 1 m. |
| Entry door and sidelight | deviates (P2 #7) | glass_close, entry_canopy | A glazed aluminium pair with visible jamb returns, but no hardware or door/sidelight distinction. |
| Canopy and rods | conforms (height P2 #7) | entry_canopy, glass_close, architecture_close | A flat concrete slab hung on two dark rods from wall plates. The rods meet the slab top and the plates sit on the wall, with no floating parts. |
| Window beside entry | deviates (P2 #8) | glass_close | Correct position, sill and depth, but 3 panes against 2. |
| Landing and steps | conforms (P2 #9, #12) | front_corner, aerial, front, top | A long cast-concrete landing at door-threshold height, with steps at its west end. |
| East windows | conforms | right_side, architecture_close, east_windows, parapet_corner | One low two-pane window near the south corner and two high clerestories, with sills and reveals. |
| Parapet and coping | conforms | parapet_corner, roof_units, facade_close, rear_north | A flat parapet with a thin pale coping all round. The inner parapet face is visible. |
| Roof: membrane | conforms (seam direction P2 #10) | top, roof_units | Grey membrane with seams. |
| Roof: units | conforms (position P2 #13) | top, roof_units, aerial | Two boxed rooftop units with dark fan tops, near the centre. |
| Roof: domes and vents | deviates (P2 #10) | top, roof_units | Four curbs are present but box-shaped and too far toward the corners. Pipe vents are present. |
| Apron and site | conforms | top, aerial, front | A wide concrete apron in front of the bays, the street to the south and parking on the east lane, as the top view governs. |
| Materials hierarchy | deviates (P2 #3, #4) | front, facade_close | Beige CMU over a concrete base, dark shelters, pale coping and metal. The base and shelter values are too weak to read at front scale. |
| Unseen north and west faces | coherent | rear, rear_north, left_side, rear_side | The same CMU grammar, small high windows, and a rear man-door with a stoop, steps and rails, all in contact. Not judged for fidelity. |
| Interior | coherent | interior | A racked warehouse aisle under a plausible clear height. |

## 4. Camera validity

- No view has an occluded target, a clipped asset or illegible content, so there is no P0 camera defect.
- front: valid but not faithful to the source (P1 #2). Too much empty asphalt, horizon too low, wide-angle convergence, bays undersized in the frame, and the second clerestory cut at the frame edge.
- front_corner and aerial: valid. The building is small in the frame (about 30–35% of the width) but all identity elements are legible. This is acceptable.
- left_side, right_side and rear: valid elevations. The building takes up about 28–40% of the frame width, with a lot of empty ground plane below. This is acceptable for envelope coherence, and tighter framing would be polish.
- top: valid nadir and governs the plan. The landing and steps read faintly but are legible.
- All detail views (facade_close, architecture_close, glass_close, dock_doors, entry_canopy, roof_units, east_windows, parapet_corner, interior, rear_north) are valid, on target and legible.

## 5. Previous-version findings

| Finding | Status in v003 pixels | Evidence |
|---|---|---|
| v002 P1: dock doors and shelters too tall (shelter top about 68% against about 55%; door top about 60% against about 43%) | **Resolved** | facade_close (frontal): shelter top about 51% and door head about 44% of the wall height. Front render at bay 4: shelter top about 55% and door top about 47%. The source front at bay 4 gives about 53% and about 44%. The width that the fix sacrificed has opened a new P1 (#1). |
| v002 P1: front camera almost straight at the south face, east face a sliver, empty ground below | **Partially resolved; still P1 (#2)** | The east face now takes about 20% of the frame width (source about 20%) with its windows readable. The empty foreground remains (bottom 35–40% of the frame against about 17%), the horizon is about 54% against about 73%, and the bays take up 17% of the frame width against 31%. |
| v002 P1: grey cast-concrete dock base and steel lip missing | **Resolved (tone polish P2 #3)** | facade_close and dock_doors show a continuous concrete base band about 1 m high and a dark steel leveller lip at each sill with bumpers below. The base tone is too close to the apron. |
| v001 findings (six; resolved in v002) | **No regression observed** | The brief does not list the six v001 items, so I checked them against the full identity grammar: CMU coursing, flat parapet with coping, two rooftop units, rod-hung canopy, landing with west-end steps, east low window and clerestories, dock bumpers and guides, and opening depth and returns. All are present and in contact in v003. |
