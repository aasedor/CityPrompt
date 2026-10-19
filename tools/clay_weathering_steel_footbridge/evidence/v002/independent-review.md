# Independent holistic review: Cor-Ten Warren truss footbridge, v002

Reviewer: independent RLASM v6.1 holistic reviewer (not the builder).
Inputs I judged: `sources/front.png`, `sources/oblique.jpg`, `sources/top.jpg`, all 18 `renders/*.png` at full resolution, and the 4 `boards/*.png`. I made zoomed crops in a new scratch folder, `indep-crops-v002-622a1828`, and wrote nothing else. Builder notes, counts and hashes are not treated as proof.

## 1. Verdict

**VISUAL_REWORK_REQUIRED.** Most v001 defects are fixed in the pixels: the hub is gone, the plan angles are right, the roof uses a zig-zag, the infill is a diamond net and the end panels are clean. One P1 remains. The overhead framing at the bend, the identity node that the oblique source shows close up, is laid out the opposite way round from both sources.

Counts: P0 = 0, P1 = 1, P2 = 8

## 2. Findings

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | top, aerial, front_corner, architecture_close, rear_north, rear_side (compare sources/oblique.jpg and sources/top.jpg at the apex) | **The render fans the bend roof members out from the outer apex; the sources do not.** In the render, three struts run from the outer apex node: one along the bisector to the inner corner node, and one each to the first inner top-chord node of each arm (top.png apex at about 490,145 with lines to about 542,260 (inner node), 520,300 and 578,270). There is no member across the corner between the outer chords. Both sources show a different topology. A long **collar tie** crosses the corner and joins the first outer-chord node of the land arm to the first outer-chord node of the crossing arm, about one panel back from the apex: oblique about 180,170 to 790,210, and top about 540,495 to 650,515. **Two struts from the inner corner node** rise to those same two outer-chord nodes, so the corner reads as a triangle (kite) with a crossbar. There is no fan from the apex and no roof tie along the bisector. The only thing at the outer apex is the corner post, seen as a short member going down in the top view. As built, the signature corner reads as a different node. | The v001 phrase "roof members radiating from the apex" was implemented literally instead of being traced from the source pixels, so the strut endpoints were mirrored from the inner node to the outer node. | Delete the three apex-fan struts and the overhead bisector tie. Add one collar tie between the first top-chord panel point of each **outer** truss. Add two struts from the inner corner node to those same two outer-chord nodes. Start each arm's regular tie and zig-zag sequence after that triangle. Keep the corner posts, the mitred chords and the continuous deck. Re-render top, aerial, front_corner and architecture_close and lay them beside the oblique source. |
| 2 | P2 | front | Road lanes fill only the lower-left corner. Most of the ground under the span is a pale empty plaza, and a white block (the bus seen end-on, with no window band) sits under the bottom chord and reads as a pier. In the source front, multi-lane road with lane marks fills the lower half under the span. | The camera is aimed past the east kerb. | Pan or yaw the camera so the span sits over the carriageway as in the source, or move the bus out of the shot under the chord. |
| 3 | P2 | top, front_corner, aerial (compare oblique and top) | Context is still simplified. The dark-roof brick warehouse that runs along the land arm in both sources (top source about 110 to 550 x 330 to 640; the gravel roof in the oblique, lower left) is missing, so the land arm crosses an empty lot. The road has 4 lanes, against the source's wide road with turn lanes. The crossing arm lands on a freestanding tower; in the source top it heads toward the pale-roof block in the south-east. | Simplified context massing. | Add a low brick block along the west side of the land arm. Widen the road to about 6 lanes. Optionally attach the east tower to a building. |
| 4 | P2 | top, aerial, rear, rear_north, rear_side | A small black square or dot sits on top of the outer apex node and the inner corner node in every overhead view. | The corner-post top is open or uncapped, or has a dark back face poking through the chord mitre. | Cap the corner posts flush below the chord top, or give them a closed end face in the steel material. |
| 5 | P2 | road_under (left, about 10 to 40 x 600 to 612) | A thin black wedge shows at the outer apex where the bottom-chord fascia meets the deck or floor beam. | A small mitre gap between the two arms' bottom plates. | Close the mitre: extend both fascia and deck plates to the bisector plane. |
| 6 | P2 | front, facade_close, landing_stair, rear_north | The fascia row reads as raised grey studs or bolt heads. In the source front it is a row of small dark square perforations. | Boss geometry in a light material instead of recessed holes. | Recess the squares, or shade them dark as through-holes. |
| 7 | P2 | glass_close, mesh_infill, front | The diamond net now reads correctly, but the strands are thick and opaque pale, so at mid-distance it reads closer to chain-link than the source's near-transparent fine stainless net. | Strand radius and albedo are set too high. | Thin the strands by about 40 to 50% and darken them slightly, or lower their opacity. |
| 8 | P2 | rear_side | The foreground pale-roof warehouse hides the bend's underside, the inner bottom chords, the corner-post base and the apex pier. | Camera height or azimuth. | Raise the camera or swing it about 10 degrees so the apex underside clears the roof edge. |
| 9 | P2 | landing_stair, top, aerial; deck_walk, mesh_infill; road_under | No bearing seat or corbel is visible where the fascia butts the tower face, so the claimed 15 cm seating cannot be seen. The deck has blotchy dark render-noise patches. The foreground car in road_under has an oversized ghost-glass cabin box. | Missing seat geometry, low sample count, and the entourage mesh. | Add a visible steel seat angle or corbel at each tower. Raise the samples or denoise. Fix or remove the car cabin. |

## 3. Source conformance checklist

| Item | Status | View(s) used | Note |
|---|---|---|---|
| Plan and proportions | **Conforms** | top vs sources/top.jpg; aerial | One sharp mitred V with an included angle of about 89 degrees. The crossing arm is about 70 degrees to the road axis. The land arm is about 19 to 22 degrees off the road, running beside the west kerb. The apex is at the west kerb, with the pale-roof block just behind it. The plan is not mirrored. |
| Truss geometry and panel rhythm | **Conforms** | front, rear, road_under, right_side, top | Pure Warren with bold diagonals at about 60 degrees, no verticals except at the ends and corners, and whole panels to the tower face. Depth-to-handrail ratio is about 2.7, against about 2.6 in the source front. |
| Chords and diagonals | **Deviates (P1 #1)** | top, aerial, front_corner, architecture_close vs oblique and top | Chords mitre cleanly to one outer and one inner node with corner posts. Each arm's ties plus single alternating diagonal match the source. **The bend overhead framing is a fan from the apex instead of the source's collar tie plus struts from the inner node.** The end panels at the towers are clean: one end post, with the last diagonal landing on the bottom node (landing_stair, front, top). |
| Mesh infill | **Conforms** (P2 #7) | glass_close, mesh_infill, front, deck_walk | Fine diamond net on slim pale posts at about 1.6 m, with a bottom cable and a dark top rail. The strands are a little heavy. |
| Deck | **Conforms** (P2 #9) | deck_walk, top, architecture_close, facade_close | Plate deck, continuous through the bend in one colour, with plate joints and no plank striping. Floor beams are visible from below. |
| Landings and supports | **Conforms** (P2 #3, #9) | landing_stair, aerial, right_side, rear, rear_north | Brick stair towers with grade and deck-level doors. The bottom chord meets the tower face with no gap. There is one steel pier under the outer apex with a base plate on the sidewalk. No extra columns. No visible bearing seat. |
| Road beneath | **Conforms (simplified)** (P2 #2, #3) | road_under, front_corner, aerial, top | Asphalt with lane marks and a double yellow line, kerbs and sidewalks, and block cars and a bus. Narrower than the source. Under-represented in the front view. |
| Context | **Deviates (P2 #3)** | top, front_corner, aerial vs oblique and top | Brick blocks, a glass block and trees are present. The warehouse flanking the land arm is missing. |
| Materials hierarchy | **Conforms** | all | Rust-orange steel dominant, pale stainless net, dark handrail, rust-brown deck, red-brown brick, pale glass grid. |

## 4. Camera validity

- **front:** valid. An oblique look along the crossing arm with the deck visible through the near truss. Composition is P2 #2.
- **front_corner and aerial:** valid. The apex is fully legible; the arms run off frame, as in the oblique source.
- **top:** valid. The whole bridge, both towers and the road axis are in frame.
- **left_side:** valid. The whole bridge is visible. The foreground blocks frame the shot but no longer hide it (v001 P1 fixed).
- **right_side and rear:** valid. The whole bridge, both towers and the pier are visible.
- **rear_side:** valid, but the apex underside and pier are partly hidden by the foreground roof (P2 #8). The top apex node and both arms stay legible.
- **Detail views:** all frame their targets with nothing blocking them. These are facade_close, architecture_close, glass_close, truss_node, mesh_infill, deck_walk, landing_stair, road_under, top_chord and rear_north.
- No view has its asset clipped in a way that hides identity, and no view shows nothing legible.

## 5. v001 findings: resolved in the pixels?

| v001 finding | Status | Evidence |
|---|---|---|
| P1: separate hexagonal "gazebo" hub at the bend | **Resolved** | top, aerial, front_corner, architecture_close: one mitred V with no hub, ring, posts or dark hub deck. The new apex roof framing does not match the sources; see P1 #1. |
| P1: V rotated against the road (about 50 and 45 degrees) | **Resolved** | top: crossing arm about 70 degrees to the road axis, land arm about 19 to 22 degrees off it along the west kerb. Landings follow. |
| P1: full X in every roof bay | **Resolved** | deck_walk, truss_node, top: one transverse tie and one diagonal per bay, alternating into a zig-zag. |
| P1: heavy square bar-grid infill | **Resolved** | glass_close, mesh_infill: diamond cable net. Minor strand weight is P2 #7. |
| P1: crossed diagonals and stacked cluster in the end panel | **Resolved** | landing_stair, front, top: a single end post with the last diagonal on the tower bottom node and no crossing members. The top view shows a half-bay roof end that is consistent with this. |
| P1: left_side half hidden by a brick block | **Resolved** | left_side: the whole bridge is visible. |
| P2: extra steel columns under the hub and beside a tower | **Resolved** | There is now a single apex pier (rear, rear_north, aerial). The front-view "pole" is a tree trunk behind the span. |
| P2: plank-striped deck | **Resolved** | deck_walk, top: plate deck. |
| P2: plain box bottom chord instead of a deep perforated fascia | **Mostly resolved** | A deep fascia with a row of squares is visible, but they read as studs rather than holes (P2 #6). |
| P2: front camera an elevation, not the source's perspective | **Resolved** | front is now oblique along the arm. Road coverage is weak (P2 #2). |
| P2: dark hub deck | **Resolved** | The deck is one colour through the bend. |
| P2: no slim posts carrying the cable net | **Resolved** | Posts at about 1.6 m (glass_close, mesh_infill). |
| P2: simplified narrow road and context | **Open** | Still 4 lanes, and the land-arm warehouse is missing (P2 #3). |
| P2: no bearing seat at the towers | **Open / not visible** | The fascia butts the tower flush, with no seat visible in any view (P2 #9). |
