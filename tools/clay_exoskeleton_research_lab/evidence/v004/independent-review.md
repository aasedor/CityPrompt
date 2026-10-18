# Independent holistic review: clay-exoskeleton-research-lab v004 (RLASM v6.1, architectural clay)

Reviewer: independent; I did not build this. I judged only the rendered pixels against the locked source pixels. I opened all 18 renders, the 3 locked sources and the 4 phone boards at full resolution, and made zoomed crops in `scratchpad/indrev-v004-crops-7f3a/`. I ignored the metadata, counts, hashes and the builder's notes.

## 1. Verdict

**VISUAL_REWORK_REQUIRED**: the building is clearly the source lab and has no P0, but six P1s block approval. Black-pixel junction defects remain, at a new soffit seam and on the curtain-wall nodes. The curtain-wall rhythm, the east bay count, the stack height and the roof-plant plan all depart visibly from the sources.

Counts: P0 = 0, P1 = 6, P2 = 10

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | cantilever, rear (x~998,y~655), rear_north | **Contact:** a continuous pure-black hairline (≈1,400 px at value 0–35) runs along the whole junction between the slab edge band and the angled soffit, so the soffit reads as detached from the slab. A dark 5×6 px block is still visible at the cantilever's north-west corner in the rear view. | The v004 change that "kept the soffit clear of the slab faces" leaves a real gap that the renderer shows as an unlit slit. A residual overlap or open box end remains at the NW corner. | Make the soffit's top edge coincident with the underside of the slab, or embed it 5–10 mm into the slab. Cap the open end at the NW corner. Do not leave an air gap. Re-render cantilever and rear and confirm there are 0 px below 40 along the seam. |
| 2 | P1 | glass_close, facade_close, cantilever, rear_north, architecture_close; roof_screen, stacks | **Optical/finish:** a pure-black (RGB 0,0,0) ≈7×7 px square sits at every mullion/transom crossing (≈56 in facade_close, 5 per row in glass_close). Black L-shaped caps also show on the tops of the perforated-screen posts (roof_screen, stacks). They read as holes or render errors, not as source spider fittings, which are light metallic. | The node and post-cap objects have no material, a black material or flipped normals, or they are zero-thickness coincident faces. | Give the node caps and post caps the light-grey mullion or screen material, or delete them. If spider fittings are intended, make them small light-grey bosses. Re-render and confirm there are 0 px at value 0 in these views. |
| 3 | P1 | front, front_corner, facade_close, glass_close, rear | **Rhythm:** each lab floor is split by a mid-height transom into two rows of panes, behind white slab bands about 9–10 % of floor height plus heavy white edge members. The result reads as a gridded office window wall. The source front and oblique show frameless, full-storey-height panes with point fixings and hairline floor joints, so the facade reads as a glass box. | The curtain-wall module has a transom at mid-storey, and the slab-edge fascia is oversized. | Remove the mid-storey transom so there is one pane per storey (mullions keep their current spacing). Reduce the slab fascia to about 3–4 % of storey height. Keep the mullions slim and light so the glass dominates. |
| 4 | P1 | front, left_side, right_side, roof_screen, stacks vs src front/oblique | **Identity:** the exhaust stacks barely reach the top of the perforated screen. In elevation they clear it by only about 0.25 of the screen height, and in the front view they are completely hidden. In the source front, two clusters of three stacks stand well above the crown; in the oblique they clear the screen by about one screen height. | The stacks are too short relative to the 3.8 m screen. | Raise the stacks until their tops sit about 0.8–1.0 × screen height above the screen top. Verify that both clusters read above the crown in the front view, as in the source. |
| 5 | P1 | top, aerial, front_corner, roof_screen vs src top/oblique | **Roof plan:** the plant composition is under-scaled and simplified against the top source, which governs the plan. (a) The penthouse covers about 44 % × 41 % of the screened enclosure; in the source it is about 70 % × 54 %. (b) The continuous duct loop and air-handler blocks around the penthouse are reduced to four isolated bars. (c) The west cluster of three stacks is missing: the render has 3 clusters (N, E, S), the source has 4 (N, W, E, S). (d) The south walkway is about 5 % of depth; in the source it is about 11 %, and the oblique shows a broad pale walkway in front of the south screen. | The roof was simplified, and the setback was tuned only for the front view. | Enlarge the penthouse to the source footprint. Add the L-shaped duct runs and the paired units along N, W and S. Add the west stack cluster. Set the south screen line back to about 11 % of depth, keeping west, east and north at about 5 %; the front view still shows the crown at that setback. |
| 6 | P1 | right_side, front, front_corner, architecture_close, rear_side vs src front/oblique | **Rhythm:** the east exoskeleton has 5 structural bays: white/diagonal, louvre, louvre, louvre, white/diagonal. Both sources show 4 bays (white/diagonal, louvre, louvre, white/diagonal), so the louvre share is 60 % against the source's 50 %. | The bay count was set to 5 across the depth. | Re-space to 4 equal bays across the east depth, with 2 louvre bays flanked by white diagonal bays. Keep the zig-zag diagonals in the end bays. |
| 7 | P2 | front, exoskeleton, architecture_close, rear_side | Each louvre bay is a main panel plus a narrow louvre sliver between paired columns, so from the front angle it reads as two dark strips per bay. | A secondary louvre plane sits beside each panel, with doubled columns. | Use one louvre panel per bay, edge to edge, between single columns. |
| 8 | P2 | front, architecture_close vs src | Exoskeleton steel is still about 1.5× the source member weight and square in section; the source uses round tubes. | Section size and profile. | Slim the columns and beams further. Use a round or octagonal tube profile if the budget allows. |
| 9 | P2 | front, v_pilotis vs src | The door portal posts continue up to the soffit above the head, making an H-frame. The source portal is a stand-alone door-height frame. | This was the fix for the v003 black block. | Stop the posts at the head and leave the glazing above uninterrupted, without reintroducing the black junction. |
| 10 | P2 | front, v_pilotis | The V-pilotis arms are about 1.7× the source thickness relative to ground-floor height. | Arm section. | Reduce the arm width by about 40 %. |
| 11 | P2 | facade_close, glass_close, front | The services read as uniform full-width blue and green stripes on every floor, with one green run at about pane mid-height. The source concentrates vertical risers and ceiling-level runs. | Procedural service layout. | Cluster the risers in the central bays and keep the horizontal runs at ceiling level. |
| 12 | P2 | front, front_corner | On the south face, an extra two-pane glazed bay framed by heavy white piers sits at the SE corner, where the source curtain wall runs to a single corner column. On the ground floor, the east end of the south face is clear glazing; the source shows concrete behind the glass there. | Corner-wrap interpretation. | Run the curtain wall to one slim corner column. Add a concrete backing wall behind the east lobby bays. |
| 13 | P2 | front, cantilever | The soffit is pale clay; the source soffit is a dark grey metal plane. The two front trees hide most of the cantilever tip and soffit. | Material choice and tree placement. | Use a mid/dark grey soffit material. Move the trees about 3 m east, or lower their crowns. |
| 14 | P2 | v_pilotis | A large oval area-light reflection floats on the lobby glass. | Specular reflection of the key light. | Lower the glass specular, or move the light. |
| 15 | P2 | top | Radiating dark shadow wedges and low contrast make the roof plan noisy. | Multiple light sources or shadows. | Use one sun plus fill for the nadir view. |
| 16 | P2 | front_corner, aerial | The building fills only about 14 % of the frame, and the two views are near-duplicates. | Framing. | Tighten the FOV or distance so the building fills about 35–45 % of the frame, and separate the elevations. |

## 3. Source conformance checklist

| Item | Status | View(s) used |
|---|---|---|
| Silhouette (box on recessed base, west cantilever, crown screen) | conforms | front, front_corner, left_side vs src front/oblique |
| Plan proportion (W:D about 1.22, streets S and E) | conforms | top vs src top |
| Storey count (3 lab floors over a taller ground floor = 4) | conforms | front, left_side, rear, right_side |
| Curtain wall and slab bands | deviates: a mid-storey transom doubles the horizontal rhythm, and the white bands and edge members are heavier than the source's hairline joints (P1 #3) | front, facade_close, glass_close vs src front |
| Coloured services behind glass (blue, green, yellow) | conforms (distribution P2 #11) | facade_close, glass_close, interior, front |
| Cantilever and angled soffit | geometry conforms; contact deviates (black seam and NW block, P1 #1); tone P2 #13 | cantilever, rear, front |
| V-pilotis and recessed glazed ground floor | conforms (arm weight P2 #10) | v_pilotis, front |
| Door portal position (between the Vs, just west of V2) | conforms (H-frame form P2 #9) | front, v_pilotis |
| Concrete base walls (west end, service bays) | conforms at the west end and the east service face; the south lobby's east end lacks concrete backing (P2 #12) | cantilever, left_side, right_side, rear |
| Exoskeleton: columns and floor beams | conforms; weight and profile P2 #8 | right_side, architecture_close |
| Exoskeleton: alternating diagonals | conforms (per-floor zig-zag in the white end bays) | right_side, architecture_close |
| Exoskeleton: louvre infill and white panels | infill conforms; bay count deviates, 5 against 4 (P1 #6); sliver strips P2 #7 | right_side, front, exoskeleton |
| Exoskeleton corner wrap at SE | conforms in principle; the extra south bay is P2 #12 | front, front_corner |
| Roof: edge walkway | deviates: the south walkway is about half the source width (P1 #5d) | top, front_corner vs src top/oblique |
| Roof: perforated screen | conforms (height, perforations, thin parapet; v003 fix holds) | front, roof_screen, stacks |
| Roof: penthouse and units | deviates: undersized (P1 #5a) | top, roof_screen |
| Roof: duct runs | deviates: four isolated bars against the source's continuous loop (P1 #5b) | top, roof_screen |
| Roof: clusters of three exhaust stacks | deviates: 3 clusters against 4, and too short to read above the crown (P1 #4, #5c) | top, front, roof_screen |
| Materials hierarchy (glass dominant S/W, white steel and grey louvres E, pale roof plant) | partly deviates: the white curtain-wall framing competes with the glass (P1 #3); louvre tone is acceptable (render L≈132 against source ≈108–137 in the front view) | front, right_side |
| North face (not shown in sources; judged for coherence) | coherent: glazed lab floors over a concrete ground floor with a door | rear, rear_north |

## 4. Camera validity

- All 18 views are valid. No target is occluded, no asset is clipped, and every view is legible. I found no P0 camera defect.
- front_corner and aerial: the building fills only about 14 % of the frame, and the two views nearly duplicate each other (P2 #16).
- front: the trees hide the cantilever tip (P2 #13). The target is still legible.
- top: legible, but the shadow wedges add noise (P2 #15).
- interior: legible but dark. Acceptable.

## 5. Status of the v003 findings and the earlier resolved items

| Previous finding | Resolved in pixels? | Evidence |
|---|---|---|
| v003 P1: black block where the portal post meets its head | **Resolved** | v_pilotis has no pixels below 35, and the post/head junction is clean. |
| v003 P1: black block at the cantilever's NW corner | **Not resolved** | rear (x≈998, y≈655): a 5×6 px dark block (values 32–60) remains. The v004 soffit change also introduced a full-length black seam (P1 #1). |
| v003 P1: black blocks on the open exoskeleton column tops | **Resolved** | right_side, architecture_close and front show the columns capped above the top beam with no dark pixels. |
| v003 P1: deep white band above the top floor and a heavy frame hiding the roof screen in front | **Resolved** | front: a thin parapet, glass nearly to the edge, and the perforated crown fully legible at about 0.5 storey height. Side effect: the stacks are now hidden in front (P1 #4). |
| v003 P1: east louvres reading as narrow recessed strips with wide white margins; steel chunkier and louvres lighter than the source | **Largely resolved** | Louvres now fill the bay height, the blades are darker and nearly flush, and the steel is slimmer. Front-view louvre tone L≈132 against source ≈108–137. Residuals are P2: the paired-column sliver still reads as two strips per bay (#7), and the steel is still about 1.5× the source and square in section (#8). |
| Earlier resolved: cameras | No regression | All 18 legible (framing P2 #16). |
| Earlier resolved: bay layout | **Flagged** | The east exoskeleton shows 5 bays against 4 in both sources (P1 #6). From the pixels alone I cannot tell whether this is a regression or was accepted earlier. The curtain-wall vertical bay spacing is consistent with the source. |
| Earlier resolved: lobby | No regression | Recessed glazed ground floor behind the Vs (v_pilotis, front). |
| Earlier resolved: services | No regression | Blue, green and yellow visible behind the glass on all three lab floors (layout P2 #11). |
| Earlier resolved: pilotis | No regression | Two Vs; clean contact at the caps and at grade (v_pilotis). |
| Earlier resolved: trees | No regression | Grounded low-poly trees on the south and west (placement P2 #13). |
| Earlier resolved: screen perforations | No regression | Perforated panels with square holes on all sides (roof_screen, stacks, front). |
| Earlier resolved: door position | No regression | The portal sits between V1 and V2, just west of V2, as in the source. |
