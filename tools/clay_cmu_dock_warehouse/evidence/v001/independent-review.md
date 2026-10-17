# Independent holistic review: clay-cmu-dock-warehouse v001 (RLASM v6.1 architectural clay)

Reviewer: independent, adversarial. I judged only rendered pixels against the locked source pixels (`sources/front.png`, `sources/oblique.jpg`, `sources/top.jpg`). I opened all 18 renders and the 4 phone boards at full resolution and cut zoomed crops into a separate scratch folder (`indrev-wh-v001-crops-q7k2`). I did not use metadata, counts, hashes or builder notes as evidence.

## 1. Verdict

**VISUAL_REWORK_REQUIRED.** The candidate is the right building type and every identity element is present. It still has nine P1 defects that block production approval:
- the envelope is too long and low, and the dock bays are squat;
- the south-face entry group is shifted west;
- the CMU reads as lap siding;
- the coping breaks at the SE corner;
- the yellow guides are mis-modelled;
- the rear door is incoherent;
- two cameras are invalid for their roles.

Counts: P0 = 0, P1 = 9, P2 = 14

## 2. Findings

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | facade_close, dock_doors, front, aerial (vs source front, oblique) | The dock doors and shelters are square or landscape. In facade_close a door opening is about 310 x 315 px (W:H about 1:1) and its surround is about 428 x 407 px (about 1:0.95). In source front at bay 4, where the CMU blocks read at their true 2:1 so there is no horizontal foreshortening, the door is about 108 x 205 px (about 1:1.9) and the shelter about 181 x 265 px (about 1:1.45). Both sources show tall, narrow, portrait openings. Measured in CMU courses, the doors have about the same height in both (about 14 courses) but the render's doors are about 2x too wide. | The bay width was set as a fraction of the plan length, not from the source door module, while the plan is oversized (see #2). | Rebuild the bay module from the source: door W:H about 1:1.9 and shelter about 1:1.45, keeping door height at about 14 courses. Re-space the 4 bays so their pitch stays at about 14% of the south-face length after #2 is fixed. |
| 2 | P1 | front, aerial, rear, left_side, phone-01 (vs source front, oblique) | The envelope reads as a long, low shed. The shelters fill 0.58 (front) to 0.75 (aerial) of the wall height at their bay, against 0.49 to 0.50 in source front and oblique. The wall is about 34 courses high in the render against about 41 in the source. In the matched oblique pair, the length/height ratio of the south face is about 3.3 in aerial and about 2.4 in the source oblique. The rear elevation reads about 4.6:1. | The wall height is too low for the CMU and door module, and the plan is scaled up. | Raise the parapet to about 41 courses above the apron, or shrink the plan, so that the shelter-to-wall ratio is about 0.5 and the south face reads about 2.5 to 3:1 in the aerial. Keep the plan W:D at about 1.3. |
| 3 | P1 | aerial, front_corner, front, top (vs source oblique, top, front) | The entry group (canopy, door and office window) and the landing sit too far west. A long blank wall runs from the window to the SE corner: about 3 window-widths in aerial (window 668-697 px, corner at 790 px) and about 2.6 in front_corner. Both sources show only about 0.5 to 0.6 window-widths (oblique: window 690-778, corner at 830; front: 655-765, corner at 820). In top, the canopy sits at about 51-68% of the south-face length; in the source top it is at 72-84%. The landing also runs well east of the window, but in the source it ends under the window's east end. | The entry was placed from the dock run with a fixed gap, not anchored to the SE corner. | Anchor the office window so it ends about 0.5 window-width from the SE corner. Place the door, sidelight and canopy just west of it, and end the landing under the window's east jamb, with the steps at its west end. Keep a small gap between bay 4 and the landing. |
| 4 | P1 | facade_close, dock_doors, glass_close, entry_canopy, east_windows, architecture_close, rear_north | The wall shows only continuous horizontal joints at about 22 px spacing, with no head joints. It reads as horizontal lap siding or clapboard, not CMU. Both sources show unmistakable running-bond block, with vertical head joints offset half a block per course. | The coursing generator emits bed joints only. | Add running-bond head joints at 2 course-heights (block 2:1), offset half a block on alternate courses, at the same joint depth and colour as the bed joints. Apply them on all four faces and return them at the corners. |
| 5 | P1 | architecture_close, parapet_corner | At the prominent SE corner, the south coping stops short with an exposed end cap. The east coping starts separately, about one coping-width further on. The notch between them exposes the beige parapet top and corner, and black specks (open faces or holes) show at both coping ends. The sources show one continuous mitred coping round the corner. | The coping is built as four separate straight runs, trimmed to the wall length with no corner overlap or miter, and has non-manifold end faces. | Build the coping as one closed perimeter ring (or mitre the four runs and extend each by the coping width) so the SE, SW, NE and NW corners are continuous. Cap or delete the open end faces. Check all four corners. |
| 6 | P1 | facade_close, dock_doors, aerial, front_corner (vs source front, oblique) | The yellow guides are long stripes painted on the shelter-jamb faces, running about 70% of the jamb height. In both sources, the guides are short yellow posts at the bottom of each jamb, around the sill and leveler level (front: about the bottom 20% of the jamb; oblique: short yellow members at each jamb foot). | The guide was modelled as a decal strip instead of a post. | Replace each stripe with a short yellow post, about 1/4 of the door height tall, standing at the foot of each jamb beside the leveler, two per bay. |
| 7 | P1 | front | The front camera is placed at the SW corner, looking at the west and south faces. The locked front was taken from the SE (south and east faces, with the entry and office window near the camera, the east low window and two clerestories visible). As a result, the east face, the near-corner entry and the corner coping cannot be checked against the matched front view. | Camera azimuth mirrored, or set from the wrong corner. | Move the front camera to the SE, matching the source front: a low eye-level view along the south face toward the west, with the SE corner and east face at right. Re-render front and the phone-01 board. |
| 8 | P1 | architecture_close (also, partly, parapet_corner) | A foreground low-poly tree crown covers about 45% of the architecture_close frame. It hides the SE corner, the corner meeting of the coping and the wall, the landing end and most of the low east window, which is the target of this detail. | A street tree sits between the camera and the target corner. | Move the camera or the tree (or exclude trees from the detail camera) so the SE corner, coping, east low window and landing end are unobstructed. |
| 9 | P1 | rear, rear_north, rear_side | Coherence fault on a face no source shows. The north "man door" is a frameless glazed panel with a cross muntin and a black speck at the crossing. It has no door leaf, frame, hardware or threshold, so it reads as a tall window. It sits on a solid plinth about dock height (about 1.2 m) with no steps or ramp, so it is unreachable. | The rear-door assembly reused a window component, and the stoop was built without steps. | Model a hollow-metal man door (frame, solid or vision-lite leaf, handle) and add steps, or an L-stair with a guard, from the stoop to grade, matching the landing grammar on the south face. |
| 10 | P2 | glass_close, front | The entry is two equal glazed panes. The source has a door leaf with a pull handle beside a sidelight with a transom bar. | Simplified storefront. | Distinguish the door leaf (pull handle) from the sidelight, and add the transom bar. |
| 11 | P2 | glass_close, entry_canopy | The office window has 3 lites; the source shows 2 equal lites. | Wrong mullion count. | Use one centre mullion. |
| 12 | P2 | roof_units, parapet_corner, top | The vent domes are flat rectangular boxes. In the source they are low curbed domed units. | Primitive box. | Add a low dome or raised curb profile. |
| 13 | P2 | top, aerial, roof_units | The membrane is paler and bluer than the source's mid-grey. The seams run N-S in strips, while the source shows E-W sheet laps with one N-S centre seam. | Material tone and seam orientation. | Darken to the source grey and rotate the seam pattern. |
| 14 | P2 | all exterior | The wall colour is a desaturated greige; the source is a warmer sandy beige. | Palette sampling. | Re-sample the wall colour from the sunlit CMU in the source front. |
| 15 | P2 | front, aerial, facade_close | No exposed pale concrete base band at dock height under the dock run. Both sources show one, but the render runs the coursing to the apron. | Missing plinth. | Add a pale concrete stem band, about dock height, along the south dock run and the landing. |
| 16 | P2 | facade_close, dock_doors | Each door has 4 lites; the source shows 2 per door. This is acceptable as "a row". | Lite count. | Use 2 lites once the door width is corrected (#1). |
| 17 | P2 | dock_doors, facade_close | The jamb boxes stand proud of the header, so their top faces show beneath it, and the left jamb is offset about 5 px from the header end. | Header and jamb depth mismatch. | Give the header and jambs equal projection, flush at the outer corners. |
| 18 | P2 | top | The shelters project only slightly from the wall in plan. The source top shows deep U-shaped shelters. | Shallow shelter depth. | Deepen the shelter projection to match the source top. |
| 19 | P2 | front_corner, front | The landing steps start almost touching bay 4's bumper, and the landing has no top lip. | Placement and detail. | Leave a gap (this resolves with #3) and add a slight top-slab overhang. |
| 20 | P2 | rear_north, rear | A black speck shows at the muntin crossing of the north windows and door. | Degenerate geometry or a hole at the crossing. | Merge the muntin crossing geometry. |
| 21 | P2 | left_side, right_side, rear, front_corner | The building fills only about 30-40% of the frame width. It is legible but wastes resolution. | Camera distance. | Tighten the framing so the asset fills about 70-80% of the frame. |
| 22 | P2 | front, parapet_corner | A foreground tree overlaps the SW corner and roofline in front, and the bottom edge of parapet_corner. The targets stay legible. | Tree placement. | Move the trees clear of the camera cones. |
| 23 | P2 | top, aerial | The dock run starts about 3% of the length from the west corner; the source starts it at about 6-9%. | Bay placement. | Shift the bays east slightly when re-placing for #1 and #3. |

Counting note: rows 10-23 are 14 P2 items (rows 21 and 22 are framing polish).

## 3. Source conformance checklist

| item | status | view(s) used | note |
|---|---|---|---|
| Silhouette (single-storey flat-roof box) | conforms | aerial, front_corner, rear_side | One storey, flat roof, plain rectangular box. |
| Height and proportions | deviates | front, aerial, rear vs source front and oblique | The wall is too low for the door and CMU module, and the south face reads too long (#2). Plan W:D of about 1.31 in top conforms to the brief's 1.3. |
| CMU coursing | deviates | facade_close, glass_close, east_windows | Horizontal bed joints only, so it reads as siding (#4). Course height is plausible. |
| Dock bays: count and position | conforms (count) / deviates (spacing) | facade_close, top, aerial | Four bays on the west half. They start a little close to the west corner (#23). |
| Dock bays: doors | deviates | facade_close, dock_doors | Square, about 2x too wide; the source doors are tall and narrow (#1). Sectional panels conform. |
| Dock bays: lites | conforms (minor) | dock_doors | A row of small lites; 4 against the source's 2 (#16). |
| Dock bays: dark surrounds | deviates | facade_close, top | Present and dark, with returns. The proportions are squat (#1), the projection is shallow (#18), and the header and jamb meet poorly (#17). |
| Dock bays: bumpers | conforms | facade_close, dock_doors | Black bumpers and leveler lip below each door, mounted on the wall. |
| Dock bays: guides | deviates | dock_doors, aerial | Full-height stripes instead of short posts at the jamb foot (#6). |
| Dock bays: dock height | conforms | facade_close, front | Door sills about 1/3 of the door height above the apron, as in the source. The concrete base band is missing (#15). |
| Entry door and sidelight | conforms (massing) / deviates (detail) | glass_close | Glazed aluminium assembly present. No leaf/sidelight distinction, handle or transom (#10). |
| Canopy and rods | conforms | glass_close, entry_canopy, front | Flat slab hung on two diagonal rods with wall anchors. The rods reach the slab, and the slab bears on the wall. It is wider than the door and extends west of it, as in the source. |
| Office window | conforms (size) / deviates (lites) | glass_close | The width ratio to the door assembly (about 1.5) and the head and sill relationship match. 3 lites against the source's 2 (#11). |
| Entry group placement | deviates | aerial, front_corner, top | Shifted west, leaving a long blank wall to the SE corner (#3). |
| Landing and steps | conforms (form) / deviates (extent) | front, front_corner, aerial | A raised cast-concrete landing at dock height, with steps at the west end. It runs too far east (#3) and its steps crowd bay 4 (#19). |
| East windows | conforms | right_side, parapet_corner, east_windows, aerial | One low window near the south corner and two high clerestories, with frames, sills and reveal depth. The source oblique hints at a third clerestory; the render follows the brief's two. |
| Parapet and coping | deviates | parapet_corner, architecture_close, roof_units | Flat parapet with a thin pale coping. It is broken at the SE corner (#5). |
| Roof membrane | conforms (form) / deviates (tone) | top, roof_units | Grey membrane with seams. Too pale, and the seams run the wrong way (#13). |
| Rooftop units | conforms | top, roof_units | Two RTUs near the centre, slightly south of the source's position. They sit on the roof with contact shadows. |
| Vent domes | conforms (count and position) / deviates (form) | top, roof_units | Four, near the corners as in the source top. Box-shaped (#12). |
| Pipe vents | conforms | roof_units, parapet_corner, top | Several small pipe stacks present. |
| Apron and site | conforms | top, aerial, front | Street to the south, a concrete apron and sidewalk, a parking lane to the east with stall striping and massing cars, and asphalt to the west. |
| Materials hierarchy | deviates | all exterior | The palette order (beige wall, dark shelters, white doors, pale coping, grey membrane, pale concrete) is right. The CMU reads as siding (#4), the wall is too grey (#14) and there is no concrete base band (#15). |
| North and west faces (unsourced; coherence only) | west: conforms / north: deviates | left_side, front, rear_north | West: plain wall with small windows, coherent. North: the door and stoop are incoherent (#9). |
| Interior (unsourced) | conforms | interior | Racked warehouse interior, coherent. |

## 4. Camera validity

- **front**: invalid for its role (P1, #7). It is taken from the SW corner, while the locked front is from the SE. The east face and near-corner entry cannot be checked front against front. The tree overlaps the SW corner (P2).
- **architecture_close**: target occluded (P1, #8). A tree crown covers about 45% of the frame, including the SE corner and the low east window.
- **parapet_corner**: valid. A tree intrudes at the bottom edge (P2), but the corner is legible, which is how #5 was found.
- **front_corner**: valid but small, at the SW corner. The matched oblique role is carried by **aerial**, which correctly views from the SE like the source oblique.
- **left_side, right_side, rear, rear_side**: valid and legible, but the building fills only about 30-40% of the frame width (P2, #21).
- **top**: valid orthographic plan, unobstructed.
- **facade_close, dock_doors, glass_close, entry_canopy, roof_units, east_windows, rear_north, interior**: valid, unobstructed and legible. No asset clipping beyond the intended detail crop (the canopy's west end runs off frame in glass_close, but is fully shown in entry_canopy, front and aerial).

## 5. Previous-version findings

None. This is v001, the first build of this family. The brief names no previous-version findings, so there is nothing to mark resolved or unresolved. Every P0 and P1 above should be tracked into v002.
