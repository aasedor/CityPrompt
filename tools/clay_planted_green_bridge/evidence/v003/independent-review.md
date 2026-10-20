# Independent holistic review: planted green bridge, v003 (RLASM v6.1 clay)

Reviewer: independent; judged only from rendered pixels against the locked sources (sources/front.png, sources/oblique.jpg, sources/top.jpg). All 18 renders and the 4 phone boards were opened at full resolution. Zoomed crops were written only to the new folder `/tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/green-v003-indep-crops-88a0414d/`.

## 1. Verdict

**VISUAL_REWORK_REQUIRED**: the pod plan now matches the source top and the "+" spur is gone, but glass_close is an occluded camera (P0), and six P1s remain. Two of the P1s are failed must-hold fixes: the front view shows no water and rail_bollard shows no bollard. The other four are planting that overruns both the path rail and the outer rail, lavender and grass vocabulary that does not read as the source, and deck ends that stop in mid-air.

Counts: P0 = 1, P1 = 6, P2 = 9

## 2. Findings

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P0 | glass_close | About 80% of the frame is the faceted side of a single foreground planting mound at point-blank range. Only tower tops, two deck trees and a sliver of path at the left edge can be seen. No bridge element (path, rail, bollard, bed edge, pod) can be read. This is an invalid, occluded camera. | Camera eye point placed inside or against a v003 mound. The new, larger and taller mounds (1.15 to 1.6 m) now sit on the old camera line. | Re-aim glass_close as a clear path-level close-up: eye about 1.6 m above the path centreline, target on the path rail, kerb and bed edge. Add a clearance check so no mesh lies within about 3 m of the eye. |
| 2 | P1 | front (matched role to source front) | Must-hold fix regressed. The front frame contains zero water pixels (a colour count found 0 teal pixels, against 4.4% in front_corner). Both pods are cut by the left and right frame edges and seen only as a corner of railing and corten at about y 600 to 800. No pod column, cross-head or water is visible under them. The main-deck outer railings cannot be told apart from the pod railings. The source front shows both pods whole, at mid-distance, on columns over clearly visible water, with the outer railings running in from the foreground. The wide lens also keystones the towers. | Camera too low and too close to the pod station, with a wide FOV, so the pods fall at the frame edges and the water is hidden behind the bed mass, which v003 raised to 1.15 to 1.6 m. | Pull the front camera back down the path, about 2 pod-chord lengths short of the pods, at about 1.7 m eye height, with a normal FOV (about 50 to 55 degrees) so both pods sit fully inside the frame with water and columns visible beneath them. Lower or thin the mounds in the first 10 m of the beds if they still mask the water. Verify with a water-pixel count above 3%. |
| 3 | P1 | front, rear, central_path, rail_bollard, rear_north, planting_bed | The beds overrun the path edge. Mounds stand on the path side of the path rail and bulge over and past the kerb onto the path surface, giving a wavy, scalloped path edge. The rail top and mid bars pass straight through mound meshes (rail_bollard: the mid-rail emerges from inside a mound; central_path: the lower bar enters a mound). The pale kerb exists (central_path left) but is hidden for most of its length. The source shows a crisp line of path, kerb, rail and bollard, with planting behind the rail that only leans over it. | Mound scatter placed against the bed polygon including the kerb and rail strip, with no clearance mask. The larger v003 mound radii now cross the rail line. | Clip mound centres to at least the mound radius plus 0.15 m inside the path rail line. Keep a clear 0.3 m kerb and rail zone with only low fine grass blades allowed to lean over it. Recheck that no mound intersects the rail bars or the path surface in front, central_path and rail_bollard. |
| 4 | P1 | rail_bollard | Must-hold fix regressed. No bollard is in frame. The view shows a path-rail post and bars swallowed by mounds and a cluster of oversized poppy cups. The named target (the bollard) is absent or hidden inside planting. | The camera kept its old target while v003 planting now covers the bollard. Alternatively, the target is a rail post rather than a bollard. | Re-aim at the nearest bollard on the bed side of the path rail, with the bollard, the rail post, the kerb and the bed edge all unobstructed. Combine with fix #3 so the bollard is not buried. |
| 5 | P1 | left_side, right_side, rear_side, aerial, facade_close | Planting mounds pierce the main-deck outer railing and hang outside it, draped over the corten fascia as green lumps. Examples: rear_side about x 830 to 910, y 590 to 710; left_side about x 1180 to 1230, y 480 to 525; right_side about x 120 to 330 and x 1150 to 1250, y 470 to 525; aerial along the whole near fascia; facade_close about x 1310 to 1370. Floating green chips also sit on the fascia face. In the source, the fascia line is clean and planting stays inside the rail. | Mounds scattered to the outer bed boundary with no inset for the rail and fascia, so the meshes cross the rail plane and protrude past the deck edge. | Inset the scatter by at least the mound radius plus 0.2 m from the outer rail line. Delete any mound or chip whose bounds cross the deck-edge plane. Recheck the side, rear_side and aerial silhouettes for a clean corten line. |
| 6 | P1 | front, planting_bed, rear, top, aerial | The planting vocabulary does not match the source identity. The lavender drifts are smooth, solid lilac capsules or "sausages" with a few sparse dark spikes (planting_bed, front, rear; pill-shaped ellipses in top and aerial). They cover a small share of the west bed, where the source has a broad soft haze of purple spikes over much of the bed foreground. Grasses appear only as a few loose straw blades. The source's bright, dense bunch-grass masses and tan plume grasses, a major textural layer, are missing. The rest is a carpet of near-uniform 1 to 1.5 m gumdrop mounds. The boulder reading of v002 is gone, but the beds still do not read as the source mix of grasses, shrubs and perennials. | Lavender modelled as one closed hull per drift. Grass clumps too few, thin and low to register as masses. Mound size distribution too narrow. | Model lavender as a sage base carpet with a dense field of many thin purple spike tufts (no solid lilac hull visible), with drifts widened to about half of the west bed foreground. Add dense, bright yellow-green bunch-grass clumps (about 0.6 to 1.0 m) and a few tan plume grasses as a visible layer in both beds. Widen the mound size range (low 0.4 m fillers to 1.6 m shrubs). |
| 7 | P1 | aerial (far end), rear_side (far end) | Both deck ends stop abruptly in the air above the bank lawns, about 3 to 4 m up, with a cut corten end face. There is no abutment, landing, stair or ramp to grade and no continuation. The pedestrian path therefore ends at a drop. The source shows the deck continuing out of frame past the bank roads. Faces the source does not show must still be coherent. | Model truncated at the build extent, with no end condition authored. | Either extend the deck past every rendered frame boundary (as in the source top), or author a coherent end condition (abutment wall and landing to grade or a ramp) at each end. Recheck the aerial and rear_side. |
| 8 | P2 | front, front_corner, central_path | Wide lens still keystones the context towers (they lean outward). | Wide FOV. | Fixed by the FOV change in #2. Apply the same to front_corner. |
| 9 | P2 | front_corner | A large deck tree in the right foreground still masks the east bed and the pod approach. | Tree placement on the camera line. | Move the tree or shift the camera. |
| 10 | P2 | front, central_path, rear_north | Bollards are still near-white rather than the source's mid-grey steel. | Material value. | Darken them to the source steel grey. |
| 11 | P2 | facade_close, architecture_close, rear_north | Pod-rail end posts are still black against the pale railing. | Separate end-post material. | Match the railing steel. |
| 12 | P2 | top, planting_bed, rear_north | Bare brown soil is still visible between mounds near the kerb and at the bed ends. | Gaps in the scatter. | Fill with low groundcover. |
| 13 | P2 | all deck views | Deck trees are still single-trunk low-poly "lollipops". | Tree asset. | Use multi-stem or irregular crowns, as in the source. |
| 14 | P2 | rail_bollard, front, viewing_pod | Poppies read as oversized bell or mushroom caps and are dense in the west bed too. The source shows small open red heads, mostly in the east bed. | Head scale and shape, and the distribution weighting. | Shrink the heads to about 0.08 m and shape them as open cups. Weight the poppies to the east bed. |
| 15 | P2 | central_path | The kerb shows a serrated, stepped profile where kerb segments meet. | Segmented kerb geometry. | Use a continuous kerb. |
| 16 | P2 | water_under | The underside is very dark. It is legible but loses the girder and cross-head reading. | No fill light. | Raise the exposure or add bounce light. |

## 3. Source conformance checklist

| item | status | view(s) used | note |
|---|---|---|---|
| Plan and proportions | conforms | top vs source top | Deck about 334 px for 14.5 m. Pod projection about 261 px (0.78 of deck width), chord about 356 px (1.07), outer face about 212 px (0.63), all close to the source's 0.76 / 1.05 / 0.6. Broad half-hexagons, no "+" spur. |
| Deck | conforms | top, aerial, left_side | Wide deck with corten fascia over a dark girder band. The ends are incoherent (#7). |
| Central path | deviates | front, central_path, rear | Pale path at about 4.6 m, matching the bed widths, but its edges are overrun by mounds (#3). |
| Planting beds and their variety | deviates | front, planting_bed, top, rear | Continuous across the beds and pods, and mass now above the rail top. Lavender reads as capsules and the grass layer is missing (#6). The poppies are oversized (#14). |
| Railings and bollards | deviates | rail_bollard, central_path, left_side, rear_side | The rail forms match (picket outer rail with tan cap, slender two-bar path rail, bollards on the bed side). Mounds intersect both rails (#3, #5). The bollard is missing from rail_bollard (#4). The bollards are too white (#10). |
| Viewing pods and columns | conforms | top, aerial, left_side, facade_close, architecture_close, pier_column | Broad planted half-hexagons with corten fascia, a dark girder band, and a cross-head on a column pair. The perimeter walk strip and the five-stone threshold are visible in top and rear_side. |
| Piers | conforms | pier_column, facade_close, water_under, left_side | Round concrete columns under a pale cross-head, with deck piers on the banks. They meet the water and the soffit cleanly. |
| Water and banks | conforms | left_side, right_side, aerial, top | River with sloped grass banks, grey rip-rap distinct from the planting, bank paths with guardrails, and trees. Water is not visible in the front view (#2). |
| Context | conforms (simplified) | front, aerial, rear_side | Brown towers with strip windows, a parking lot and lawns, acceptable as simplified context. |
| Materials hierarchy | conforms | architecture_close, facade_close | Pale path, corten fascia, dark girder band, pale concrete piers, pale steel railings with tan cap, greens and accent colours. The black end posts are an exception (#11). |

## 4. Camera validity

- **glass_close: invalid (P0, #1).** The target is occluded by a point-blank mound and nothing about the bridge is legible.
- **rail_bollard: target missing (P1, #4).** No bollard is in frame.
- **front: role mismatch (P1, #2).** Both pods are clipped at the frame edges, and no water or pod columns are visible, against the source front.
- **front_corner:** valid. A foreground tree partly masks the east bed (P2, #9).
- **water_under:** valid but dark (P2, #16).
- **All others are valid and legible:** aerial, top, left_side, right_side, rear, rear_side, facade_close, architecture_close, planting_bed, central_path, viewing_pod, pier_column, rear_north.

## 5. Status of the previous-version (v002) findings, from the pixels

### v002 P1s

| v002 finding | status in v003 pixels |
|---|---|
| P1: pods undersized and pointed (wedge bays) | **Resolved.** In top, the pods are broad half-hexagons at about 0.78 / 1.07 / 0.63 of the deck width, matching the source top. The aerial and left_side read as broad planted platforms. |
| P1: 1.8 m spur made a "+" crossroads, cut the beds into blocks, and pod planting about 60% | **Resolved.** There is no spur in top or aerial. The planting is continuous across the beds and pods. Only a five-stone threshold near the north end of each pod remains, and the rail is opened there (rear_side). |
| P1: beds read as boulder fields | **Partly resolved.** The mounds are now smooth, in several greens, distinct from the grey rip-rap, and rise above the path-rail top. The lavender, however, reads as solid capsules, the grass layer is missing and the mound sizes are uniform. This is carried forward as P1 #6. The mounds now also intersect both rails (#3, #5). |

### v002 P2s

| v002 finding | status in v003 pixels |
|---|---|
| Wide front lens keystoning the towers | Not resolved (#8). |
| Deck tree in the front_corner foreground | Not resolved (#9). |
| Near-white bollards | Not resolved (#10). |
| Black pod-rail end posts | Not resolved (#11). |
| Bare soil strip along the path kerb | Reduced, still visible (#12). |
| Single-trunk lollipop deck trees | Not resolved (#13). |
| glass_close was a generic path close-up | Worse: now an occluded camera (P0, #1). |

### v001/v002 must-hold fixes

| must-hold fix | status in v003 pixels |
|---|---|
| Front camera shows both pods, water and both outer railings | **Fails.** No water pixels, both pods clipped, outer railings not legible (#2). |
| Each bed about the path width | Holds. In top: west bed about 107 px, path about 105 px, east bed about 112 px. |
| Dark girder band behind the corten pod fascia | Holds (facade_close, architecture_close, pier_column). |
| Each pod on its own cross-head and column pair under its south flank | Holds (left_side, right_side, facade_close, pier_column, aerial). |
| Slender round path-rail posts | Holds (central_path, rail_bollard). |
| Pale path-edge kerbs | Present, but mostly hidden under overrunning mounds (#3), with a serrated profile (#15). |
| Bollards offset to the bed side | Holds (front, central_path). |
| rail_bollard aimed at a bollard | **Fails.** No bollard in frame (#4). |
