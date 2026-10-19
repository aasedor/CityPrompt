# Independent holistic review: clay-stone-arch-road-bridge v002 (RLASM v6.1 architectural clay)

Reviewer: independent; I had no part in the build. I opened all 18 renders at full resolution, the three locked sources (front.png, oblique.jpg, top.jpg) and the four phone boards. I checked suspect areas in zoomed crops, written only to a new folder (`/tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/indrev-crops-dbc1a9aa/`). I judged pixels only. I did not use metadata, builder notes or evidence JSON as proof.

## 1. Verdict

**Verdict: VISUAL_REWORK_REQUIRED.** v002 fixes the v001 P0, the plan, the scene edges, the palette and the side views. Four visible P1 defects remain:
- the west quadrant corners are doubled and intersecting
- the lamp arms show black gaps at their joints
- every pier panel has black voids at its corners
- rear_side clips the east end of the bridge

Counts: P0 = 0, P1 = 4, P2 = 9

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | front (hero, x≈1040–1320, y≈480–900), front_corner (SW corner, x≈430–800, y≈620–900) | The west quadrant corners have two concentric curved barriers. The inner one is a balustrade on a plinth. The outer one is a heavy coped slab that sweeps round the corner. Under the outer coping, stepped balusters show on its outer face, and some balusters poke up past the slab edge (front crop x≈1180–1300, y≈640–880). The slab and the balusters occupy the same volume. The source front has one quadrant balustrade, ending at a pedestal where the solid parapet begins. | The west quay wall's swept coping ("curves round each corner under the parapet") is set at or above the quadrant plinth and on nearly the same radius, so it cuts through the quadrant balustrade instead of passing under it. | Drop the quay-wall coping below the quadrant plinth bed, or stop it at the tangent pedestal. One continuous barrier should remain at each west corner: quadrant balustrade → end pedestal → solid quay parapet. Then re-check front and front_corner for any baluster that pokes through. |
| 2 | P1 | glass_close (arms x≈560–880, y≈380–660), lamp_standard (x≈640–800, y≈360–520), front (near lamp arms) | The "C-scroll" arms are chains of straight box segments with black wedge-shaped gaps at every joint (6–8 per arm). The "volutes" under the collar are crude bent boxes, also with black gaps. The black joints are visible on the hero lamp in front. The ornate double-lantern lamp is a named identity element, and the source shows smooth, continuous scrolled arms. | The arm was built from separate rotated box segments with no mitre or bridging geometry. The gaps show back-faces or the void. | Rebuild each arm as one swept tube along a smooth curve (and each volute as one swept spiral), or weld and bridge the segment ends. Check for no black pixels on the arms in glass_close and lamp_standard. |
| 3 | P1 | architecture_close (panel x≈605–860, y≈585–715), facade_close (both piers), left_side (x≈1255–1395, y≈305–355), river_underside (top right), rear_side, aerial | Every pier pilaster panel frame has solid black squares at all four corners. They read as holes or voids in the stonework at every pier on both faces, and are visible at medium distance as well as in close-ups. This is the same class of black see-through artefact as the v001 jamb slit. | The four frame bars are separate boxes cut short or not mitred, which leaves open corner pockets onto unlit or back-facing interior faces. | Build the panel frame as one mitred ring, or extend the bars to overlap at the corners. Check for no black pixels around the panels in architecture_close and facade_close. |
| 4 | P1 | rear_side (left edge, x=0; sandstone pixels in the edge column at y≈497–672) | rear_side is a whole-envelope view, but it cuts the east end. The east abutment, its quadrant and end lamp lie outside the frame, the parapet runs off the left edge, and the land arch sits against the frame edge. | The camera was reframed to clear the trees, but its yaw/FOV was not re-checked against the full bridge extent. | Pull back or pan the camera so the whole bridge, from the east abutment and quadrant to the west abutment, sits inside the frame with a ≥3% margin. Keep the trees out of the sight line. |
| 5 | P2 | balustrade, front (quadrant crop), architecture_close | The balusters are still square stepped stacks, not the source's turned vase balusters (left unaddressed from v001). | Box-profile baluster primitive. | Lathe a vase profile with 8–12 segments. |
| 6 | P2 | left_side (x≈540–720, y≈350–400), right_side (x≈915–1020, y≈340–390) | Under the curved quadrant plinth runs a blue-grey strip with regular orange tabs. Its edge reads as saw-tooth, and the plinth looks as if it sits on blocks above the wall (a mild residue of the v001 overhang finding). | The polygonal coping vertices of the curved quay/retaining wall stick out past the smooth swept plinth, or the plinth has a small gap. | Sweep the wall coping on the same smooth curve as the plinth and seat the plinth flush on it. |
| 7 | P2 | arch_spandrel (x≈130–400, y≈760–980), river_underside (x≈90–400, y≈740–840), cutwater_pier (x≈0–415, y≈670–750), aerial | Inside the west river arch, the springing rests on a grey quay-material ledge about 1–1.5 m above the water, while the pier springings run straight to the water. It reads as a change of material in the abutment. | The quay wall body runs on under the end arch, in quay material. | Clad the abutment below the springing in the bridge stone, or end the quay wall at the abutment face. |
| 8 | P2 | top, aerial, front_corner | The east river pier at the edge of the low quay has a flat pilaster face and no downstream cutwater. Source top shows a pointed cutwater at that pier (x≈820). | The pier was treated as a quay-edge pier with no cutwater. | Add the downstream cutwater on the water side of the east river pier. |
| 9 | P2 | top vs source top | The plan is close, with some drift: (a) the NE quay is a long S-curve, so the upstream channel is full width at the bridge line and narrows only further north, whereas the source has a straight quay with a tight fillet into the bridge; (b) bridge length/width is ≈3.7 against ≈4.7 in the source top, so the deck reads wide for its length; (c) the land-arch-to-river-arch span ratio is ≈0.63 against ≈0.75. | The plan was traced loosely from the top view. | Tighten the NE quay curve to a fillet near the bridge, lengthen the spans slightly or narrow the deck edges, and widen the land arch. |
| 10 | P2 | top (x≈500–760, y≈470–600), balustrade (footway x≈450–700) | Blotchy shadow smears remain on the deck and wavy smears on the footway. | Low-sample soft shadows, or noise on a thin surface. | Increase shadow samples or apply denoise. |
| 11 | P2 | front (near lamp) | The right lantern finial of the hero lamp reaches y=1, touching the top edge of the frame. | The camera is framed tight to the lamp. | Tilt the camera down 1–2° or widen it slightly. |
| 12 | P2 | top, aerial, front_corner | The context town sits back from the quays behind large empty grey plots. Source top has blocks right up to the quay roads on the NE and SE. | Context placement is sparse. | Move a few blocks up to the quay roads, and add the SE garden strip. |
| 13 | P2 | lamp_standard (right lantern, x≈810–820, y≈298–310) | There are small white specks at a lantern corner post. | A stray face or normal at the glazing frame. | Fix the lantern glazing frame geometry. |

## 3. Source conformance checklist

| Item | Status | View(s) used | Note |
|---|---|---|---|
| Plan and proportions | deviates (minor, P2) | top vs source top; aerial; front_corner | Matches the source in topology: a high west quay with an at-grade crossing and zebras; a low east quay road passing under a land arch; a curved NE quay; a narrower upstream channel; 4-lane deck. The proportions drift (finding 9). |
| Arch count and form | conforms | rear, aerial, front_corner, facade_close | Three semicircular river arches plus one land arch over the east quay road, as in source oblique and top. The barrels have real depth and returns. |
| Voussoirs and spandrels | conforms | arch_spandrel, facade_close, architecture_close | Voussoirs alternate light and dark, the keystone is lowered, and the spandrels are coursed ashlar. A grey ledge shows under the west springing (P2, finding 7). |
| Piers and cutwaters | conforms (minor deviation) | cutwater_pier, facade_close, rear_north, rear | Pointed cutwaters with pyramidal caps meet the water cleanly, and there is no jamb slit. The pilaster panels have black corner voids (P1, finding 3). The east river pier has no cutwater (P2, finding 8). |
| Cornice | conforms | arch_spandrel, river_underside, architecture_close | Moulded cornice with dentils, returned at the keystone. |
| Balustrades and pedestals | deviates | balustrade, front, front_corner | Pedestals and rhythm conform. The balusters are square stacks (P2). The west quadrant balustrades intersect the quay coping (P1, finding 1). |
| Lamp standards | deviates | glass_close, lamp_standard, front | The double hexagonal lanterns, central finial, ringed shaft and bell base conform to the source. The arms and volutes have black segment gaps (P1, finding 2). |
| Carriageway and footways | conforms | roadway_deck, top, balustrade | Four lanes, a single solid centreline, kerbed footways, and the deck is unobstructed. Footways are narrow (P2, carried over). |
| Approaches and quays | deviates | front, front_corner, left_side, right_side, aerial, rear | All four corners now have quadrants, and there is no overhang at the east corners. The west corners are doubled and intersecting (P1). The plinth sits on saw-tooth tabs (P2). |
| River | conforms | aerial, rear, top, facade_close | Dark olive water continues past every frame edge, and the upstream channel is narrower. |
| Context | conforms (simplified) | aerial, front_corner, rear, roadway_deck | Hipped-roof town blocks of varied height and colour. The plots are sparse near the quays (P2). |
| Materials hierarchy | conforms | front, arch_spandrel, left_side, roadway_deck | Bridge stone is warm honey (sampled hue ≈32°, saturation ≈0.3), which matches the sampled source front stone (hue ≈33°, saturation ≈0.31). Quay walls are greyer and darker, paving is cool grey and water is dark olive, so all four are distinct. |

## 4. Camera validity

- **rear_side: invalid as a whole-envelope view.** The east abutment, its quadrant and the end lamp are clipped at the left edge (P1, finding 4).
- **front: valid.** The near abutment, the NW quadrant, the end lamp and all three river arches are in frame, and the arches recede left. The hero lamp finial touches the top edge (P2, finding 11).
- **front_corner: valid.** The near SW abutment and quadrant are fully in frame, and the land arch and NW quadrant can be read.
- **aerial, top, rear: valid.** The whole bridge and both ends are in frame.
- **left_side, right_side: valid and distinct.**
  - left_side is a lateral view of the west abutment and curved quay corner. About half the frame is plain quay wall, but the target can be read.
  - right_side looks north through the land arch along the low quay road.
- **Detail views: all valid.** No target is occluded. The bus no longer hides the deck in roadway_deck.

## 5. Previous-version (v001) findings: resolved in the pixels?

| v001 finding | Status in v002 pixels | Evidence |
|---|---|---|
| P0: the front view clipped the bridge (1 pier and about 1.5 arches, no abutment or approach) | **Resolved** | front shows the near abutment, the quadrant, the approach road at right and all three river arches. |
| P1: front_corner cut the near abutment and approach wall | **Resolved** | The SW abutment and quadrant are fully in frame. |
| P1: the plan was a mirror-symmetric cross (should be a land arch over the east quay road, a curved NE quay, a narrower upstream channel) | **Resolved** (P2 proportion drift remains) | top, aerial, right_side and rear show the land arch over the low quay road, the S-curved NE quay and the narrower upstream channel. |
| P1: the splayed approach walls were tiny stubs | **Resolved** | Quadrant walls sweep round all four corners. The west ones now intersect the quay coping, which is a new P1 (finding 1). |
| P1: the curved approach wall overhung, with a black saw-tooth underside and a loose wedge | **Mostly resolved** | There is no overhang, no black underside and no wedge. Blue-grey saw-tooth tabs remain under the plinth (P2, finding 6). |
| P1: see-through black slit at every pier where jamb meets cutwater | **Resolved** | facade_close, architecture_close and cutwater_pier show a clean joint. New black voids appear at the pier panel corners (P1, finding 3). |
| P1: plain utility lamps | **Resolved in form, new defect** | Double hexagonal lanterns, finials and a bell base are present. The arms have black segment gaps (P1, finding 2). |
| P1: the scene visibly ended (river against a grey plane, exposed block end, grey band through the arches) | **Resolved** | River, quays and town continue past every frame edge, and the views through the arches recede to the horizon. |
| P1: cool grey stone, teal water, materials hard to tell apart | **Resolved** | Warm sandstone matches the sampled source hue. The water is dark olive, and quay, paving and stone are distinct. |
| P1: two trees hid the near arch and abutment in rear_side | **Resolved** (new framing defect) | No trees are in the sight line, but the east end is now clipped (P1, finding 4). |
| P1: left_side and right_side were tiny (under 8% of frame) mirror images | **Resolved** | Both are large, distinct views. |
| P2: double centreline | **Resolved** | top and roadway_deck show a single solid centreline. |
| P2: square balusters | **Not resolved** (the builder says so) | balustrade view (finding 5). |
| P2: plain pier pilaster | **Resolved, with a new defect** | A recessed panel is present, with black corner voids (finding 3). |
| P2: the keystone notched the dentils | **Resolved** | arch_spandrel and river_underside show the keystone below the dentils, with the dentils returned. |
| P2: shadow smears on the deck | **Not resolved** | top and balustrade (finding 10). |
| P2: oversized upstream cutwaters | **Resolved** | rear and rear_north show upstream cutwaters sized like the downstream ones. |
| P2: a bus hid the deck in roadway_deck | **Resolved** | The deck reads clearly in roadway_deck. |
| P2: repetitive context blocks | **Resolved** | Block heights and colours vary. The plots are still sparse (finding 12). |
