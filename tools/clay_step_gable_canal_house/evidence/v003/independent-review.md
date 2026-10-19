# Independent holistic review: clay-step-gable-canal-house v003 (RLASM v6.1 architectural clay)

Reviewer: independent; I have no relationship with the builder. I judged only rendered pixels against the locked source pixels. I opened all 18 renders, the 3 sources and the 4 phone boards at full resolution. I made zoomed crops only in `/tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/indep_v003_crops_q7/`. Every colour value quoted below is a median RGB sampled from the PNG/JPG pixels.

## 1. Verdict

**VISUAL_REWORK_REQUIRED**: v003 fixes most v002 defects (front, east and north brick jointing, a near-black roof, a single plain coped rear gable with a two-pot chimney, east-window placement, glass_close, the tree), but five P1 defects remain. The west wall still reads as bed-joint-only siding and has frameless, sill-less windows. The rear gable triangle is untextured. Projecting dark string courses, which the source does not have, band the street facade. The aerial camera clips the chimney.

Counts: P0 = 0, P1 = 5, P2 = 11

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | left_side (also board phone-03) | The entire west wall is horizontal pale lines on flat brick: bed joints only, no head joints. It reads as lap siding, unlike the east wall at the same camera distance (right_side), which shows a staggered running-bond grid. This is the v002 "brick reads as siding" defect, still present on this face. | The v003 joint material or UV fix went to the S, E and N wall objects only. The west wall keeps the old bed-line-only material, or its UV scale collapses the head joints. | Assign the same running-bond brick material, with the same UV scale and offset, to the west wall mesh. Re-render left_side and confirm staggered head joints at that distance. |
| 2 | P1 | left_side | The 3 west openings (two small upper, one tall ground) are pale grey glass with a thin white cross. They have no white frame, no stone sill and no visible reveal; they sit flush on the wall. This breaks the grammar used on S, E and N, which all have white frames and projecting sills. | The west windows were never upgraded to the shared sash component; they are flat glazing planes with a cross mullion. | Replace them with the same white-framed sash plus sill component used on the east wall (small 2x2 and tall 2x4), recessed about 1 brick into the wall so a return shows. |
| 3 | P1 | rear, rear_north, rear_side, aerial | The whole rear gable triangle, and a band just below the eave line, is a smooth unjointed plane that is lighter than the wall below (134,94,76 vs 126,87,69). There is a hard material seam where the jointed wall stops. It reads as render or stucco, not brick. | The gable-infill mesh has a plain brick-colour material, or no UVs, so the joint texture does not appear. | Apply the jointed brick material with matching UVs to the rear gable infill (and the eave band) so that it is continuous with the wall below. |
| 4 | P1 | front, facade_close, wall_anchors, entrance_stoop, front_corner | Two full-width projecting dark-brown horizontal bands cross the street facade at both floor lines (about 20 px tall in facade_close at y 465 and y 930). The anchors hang from them. The source front has no string courses: its floor lines show only iron anchors and segmental brick relieving arches. The bands add a strong horizontal banding that changes the facade's reading. | A floor-line cornice or band component was added (possibly as a mount for the anchors) without checking the source. | Remove both bands from the S facade. Mount the anchors directly on the brick face at the floor lines, as on the E and N walls. |
| 5 | P1 | aerial | The chimney cap and both pots are cut off by the top frame edge (the chimney runs from y=0 to about 75 at x 845–900). An identity element is clipped in a whole-envelope view. | The tighter v003 aerial framing put the rear chimney top at the frame edge. | Lower the aerial target or pull back about 8–10% so the chimney pots clear the top edge with margin, keeping the tight framing. |
| 6 | P2 | stepped_gable, architecture_close, front | The source gable has a projecting white hoist-beam housing near the top; the render has none. | Element not modelled. | Add a small white hoist-beam box under the top step. |
| 7 | P2 | stepped_gable | The source gable carries several iron anchors up its face; the render's gable has anchors only at the eave line. | Anchors placed only at the floor lines. | Add 4–6 anchors on the gable face at the source positions. |
| 8 | P2 | facade_close, glass_close | There are no segmental brick relieving arches over the windows; the source has one over every street opening. | Not modelled. | Add shallow segmental arch reliefs above each street opening. |
| 9 | P2 | glass_close, facade_close | The glazing bars are white; the source has thin dark (brown) glazing bars inside white or stone frames. | Frame material reused for the muntins. | Give the muntins a dark brown material and keep the outer frames white. |
| 10 | P2 | entrance_stoop, front | The stoop is 5 white risers and narrower than in the source, which has 3 wide grey granite steps; the plinth is raised higher than in the source. | Stoop height and material not taken from the source. | Use 3 wider grey-stone steps and lower the threshold to match. |
| 11 | P2 | roof_chimney, aerial, stepped_gable | The chimney stack and the top gable pinnacle block are smooth and unjointed, and the chimney is a pale salmon lighter than the walls; the source chimney is the same jointed brick as the walls. | Separate plain-colour material on the chimney and pinnacle. | Apply the wall brick material to both. |
| 12 | P2 | rear_north, rear | The rear loft opening is two flat pale-grey panels in a white frame (it reads as blank shutters), and the rear door is a plain recessed brown slab with no frame. Both are weaker than the street-side grammar (this face is judged for coherence only). | Placeholder components. | Use a glazed small-paned attic sash (or explicit timber shutters) and give the door a simple white frame. |
| 13 | P2 | facade_close, stepped_gable, rear_north | The gutter end caps show as black angular wedges just outside the wall outline at all four eave corners. | Gutter ends extend past the gable planes. | Stop the gutters at the gable faces or close them with simple stop ends. |
| 14 | P2 | front, front_corner | The tree trunk is a pale tan pole (the source trunk is dark grey-brown), and the lamp is a plain post with a box head (the source has a lantern on a post). | Clay simplification. | Darken the trunk; give the lamp a lantern-shaped head. |
| 15 | P2 | front, top, aerial | The street is one flat pinkish-taupe slab with no kerb or carriageway split; the source has grey brick paving with a kerb and roadway. | Single ground plane. | Split the slab into pavement and carriageway with a kerb step, in a grey paving tone. |
| 16 | P2 | left_side, right_side, rear, rear_side, top | The building fills only about 15–25% of the frame width. It is legible, but small. | Wide orbit radius. | Tighten these orbit cameras the same way as front_corner. |

## 3. Source conformance checklist

| item | status | view used / note |
|---|---|---|
| Silhouette | conforms | front, front_corner vs source front/oblique: narrow, deep, gable-fronted block, with the stepped gable rising proud of the roof and a plain coped rear gable |
| Storey count and proportions | conforms | front, facade_close vs source front: raised ground floor (window, door, window) plus 2 three-bay upper floors plus 1 gable window, with basement lights, matching the source rows. (The brief's text says "three upper floors"; the source pixels show 2 three-bay upper floors plus the gable window, and the render matches the pixels.) The plinth is slightly higher than in the source (see #10). |
| Brick and joints | deviates | glass_close, east_side, rear_north: running bond with head joints, and a median front tone of 106,73,58 that matches the source's 102,71,56. The west wall is bed-joint only (#1); the rear gable, chimney and pinnacle are unjointed (#3, #11). |
| Stepped gable: step count | conforms | stepped_gable vs source gable crop: 6 coping levels per side including the top block, matching the source |
| Stepped gable: copings | conforms | stepped_gable, architecture_close: white stone copings on every step, sitting on the steps with overhang, no floating |
| Stepped gable: gable window | conforms | stepped_gable: a single white small-paned window with a sill, centred, in the lower gable |
| Stepped gable: pinnacle | deviates (minor) | stepped_gable: the top block is present but smooth (#11); the hoist beam is missing (#6); there are no gable anchors (#7) |
| Sashes and sills | conforms (street, E and N faces) / deviates (W face) | facade_close, glass_close, east_side, rear_north: white small-paned sashes with stone sills and visible reveals; the W face has frameless, sill-less glazing (#2); the muntins are white, not dark (#9) |
| Door, transom and surround | conforms | entrance_stoop: panelled door, diamond-pattern transom, white surround |
| Stoop and rails | conforms (minor deviation) | entrance_stoop: stone stoop with iron rails both sides, sitting on the pavement and meeting the threshold; 5 white risers vs 3 grey in the source (#10) |
| Anchors | conforms (minor deviation) | wall_anchors, east_side, rear_north: iron anchors at the floor lines on S, E, W and N; none on the gable face (#7); on the street face they hang from string courses the source does not have (#4) |
| Side walls and windows | conforms (E) / deviates (W) | right_side vs source front/oblique east wall: two small windows stacked over the first of two tall rear-third windows, plus a basement light, matching the source. The W wall fails (#1, #2). |
| Roof and chimney | conforms (minor deviation) | front_corner, roof_chimney, top vs source top: near-black roof (61,63,67), darker than the brick; a two-pot chimney at the rear gable apex as in the source top view. The chimney is unjointed and salmon (#11), and its top is clipped in the aerial (#5). |
| Street | deviates (minor) | front, top: a flat taupe slab with an east alley strip; no kerb or carriageway (#15) |
| Tree and lamp | conforms (minor deviation) | front, front_corner: a tall oval-crowned tree reaching the eaves and a black lamp standard on the street; simplified trunk colour and lantern (#14) |
| Materials hierarchy | deviates | dark roof, then brick, then white frames, copings and sills, then iron anchors and rails reads correctly on the street and east faces. It is broken by the dark-brown string courses (#4), the smooth rear gable (#3) and the west siding (#1). |

## 4. Camera validity

- **aerial**: the chimney cap and pots are clipped at the top frame edge (#5, P1). The rest of the envelope is legible.
- front_corner and aerial are now framed tightly; the v002 "far too wide" defect is resolved for both.
- left_side, right_side, rear, rear_side and top: the target is not occluded or clipped but is small in the frame (#16, P2). All of them are legible.
- No detail view has an occluded target. glass_close is centred on the full first-floor sash with its sill; entrance_stoop, stepped_gable, wall_anchors, east_side, roof_chimney, rear_north, architecture_close and facade_close all frame their targets legibly. interior shows the three-bay front room clearly.

## 5. Previous-version (v002) findings: resolved in the pixels?

| v002 finding | status in v003 pixels |
|---|---|
| Brick reads as siding (bed joints only, no head joints) | **Partly resolved.** The S, E and N walls now show pale bed joints and staggered head joints (glass_close, east_side, rear_north). The **W wall is still bed-joint-only siding** (left_side), and the rear gable triangle has no joints at all. Not resolved overall: #1, #3. |
| Roof lighter than the brick | **Resolved.** The roof measures 61,63,67, against brick at about 106–114, 73–82, 58–69. |
| Second crow-stepped rear gable; chimney alone on the east slope | **Resolved.** The rear gable is a plain raked gable with white coping, and the two-pot chimney sits at its apex, matching the source top view (top, roof_chimney, rear). |
| Small east windows in the front third instead of over the rear tall window | **Resolved.** right_side shows them stacked over the first of the two rear-third tall windows, matching the source front and oblique. |
| North face without white frames, sills, anchors or joints | **Mostly resolved.** The wall below the eave has white 6-over-6 sashes, sills, anchors and joints (rear_north). The gable triangle above it is still untextured (#3), and its loft opening is a blank panel (#12, P2). |
| front_corner and aerial framed far too wide | **Resolved for width**, but the new aerial framing clips the chimney top (#5). |
| glass_close cropping the sash | **Resolved.** The full first-floor sash, meeting rail and sill are centred, with the neighbouring sashes at the edges. |
| Short umbrella-crowned street tree | **Resolved.** The tree has a tall oval low-poly crown reaching about eave height (front, front_corner). |
