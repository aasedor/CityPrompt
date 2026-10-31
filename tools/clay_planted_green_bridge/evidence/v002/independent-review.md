# Independent holistic review: planted green bridge, clay v002 (RLASM v6.1)

Reviewer: independent; judged only rendered pixels against the locked sources (sources/front.png, sources/oblique.jpg, sources/top.jpg). I opened all 18 renders at full resolution, the three sources and the four phone boards. Zoomed crops (read-only derivatives) are in /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/crops-green-v002-rev-16694989/.

## 1. Verdict

**VISUAL_REWORK_REQUIRED**. The v001 camera, bed-width and pod-outline defects are fixed. Three P1s remain. The viewing pods are about 25 to 30 % undersized and too pointed. The new pod access spur makes a full-width paved cross in plan that the source does not have. The beds still read as heaps of faceted green boulders, with only token lavender and flat poppy chips.

Counts: P0 = 0, P1 = 3, P2 = 7

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | top, aerial, front_corner, front, boards/phone-01 | **Viewing pods are undersized and pointed.** Measured against outer-to-outer deck width in the top view, the pods project about 0.56 of the deck width (source top about 0.75 to 0.77). Each chord along the deck edge is about 0.78 of the deck width (source about 1.05). The outer face is about 0.35 of the deck width (source about 0.6). front_corner gives the same result: each pod projects about 0.48 of the deck width at that depth, against about 0.61 and 0.80 in the oblique. The pods read as small wedge bays hung on the deck. In the source they are broad, nearly full-hexagon planted platforms that are as long as the deck is wide, with flanks close to perpendicular to the deck. | The v001 "15 % too long" note was overcorrected. An 11 m chord, 8 m projection and 5 m outer face were set against a deck about 14 m wide, and flanks at about 69 degrees narrow the outer face. | Scale each pod to a chord of about 14 to 15 m (about 1.05 x deck width), a projection of about 10.5 m (about 0.75 x deck) and an outer face of about 8 to 8.5 m, so the flanks sit at about 75 to 80 degrees to the deck axis. Keep the chord on the deck edge and move the crosshead and column pair to the new south flank. Re-check top-view ratios against sources/top.jpg. |
| 2 | P1 | top, aerial, rear_side, left_side, front, boards/phone-03 top | **The pod access spur turns the plan into a cross.** A pale paved band (about 0.36 of the path width), the same tone as the path, runs straight across the west bed, the path, the east bed and both pods at one station. At phone scale the top view reads as a "+" crossroads. It cuts both beds into separate blocks and leaves a planted sliver with a tree at each pod's south end, so pod planting falls to about 60 % of the pod. In the source top the beds and pod planting form one continuous mass. The only access visible is a small pale threshold near each pod's north end, almost hidden by planting, plus a narrow perimeter walk inside the pod rail. | The v001 "no paved route to the pods" note was answered with a straight, kerb-free 1.8 m band placed south of the pod's middle, mirrored on both sides, in path-coloured paving. | Narrow the spur to about 1.2 m and move it to the north third of each pod, where the source threshold is. Let the bed and pod planting overhang its edges so it does not read as a stripe in top or aerial views. Restore continuous planting across the pod interior, with access only via the existing perimeter walk. Optionally give the spur a slightly darker or warmer paving tone than the main path. |
| 3 | P1 | front, front_corner, planting_bed, rear_north, rear, central_path, top | **The beds read as boulder fields, not lush perennial planting.** Ground cover and shrubs are 1 to 2 m faceted icosphere lumps. They match the bank riprap rocks in form and scale, so the beds read as green rocks. Lavender is about 4 to 6 small purple lumps with a few spikes per bed ("sea-urchin" shapes in planting_bed), plus thin slivers along the west path rail in top. The east bed has almost none. The broad lavender drifts that dominate the west-bed foreground of the source front and oblique are missing. Poppies are flat orange pyramids lying on mound faces, not upright flowers above the foliage. Fountain grass is a sparse fan of 7 to 10 straight shards. Most of the mass sits at or below the path-rail top. In the source, grasses and shrubs rise well above the path rail and partly hide it. | The bed generator uses one low-poly mound primitive at a large scale, and accent species are sparse decorations on top of it rather than their own masses. | Cut the mound scale by about half and raise its silhouette variance; add a fine-grain layer of upright perennial and grass clumps. Model lavender as long drifts, each at least 3 to 5 m and made of many thin vertical spikes about 0.6 to 0.8 m tall, covering about 15 to 20 % of the west bed and about 5 % of the east bed. Model poppies as upright stems carrying small red cups 0.3 to 0.6 m above the foliage. Let about 40 % of the planting top out at 1.2 to 2 m, above the path rail. |
| 4 | P2 | front | The wide lens strongly keystones the context towers, which fill the upper half of the frame. The camera sits higher than the source eye point, so the pods read small. | Wide FOV chosen to fit both pods and both rails. | Narrow the FOV slightly, drop the camera by about 1 m and pitch it a little further down. |
| 5 | P2 | front_corner | A deck tree in the right foreground covers about 15 % of the frame, including the near east outer railing and bed. | A tree is placed near the camera axis. | Shift the camera about 2 m west or move that tree. |
| 6 | P2 | front, rail_bollard, glass_close, central_path | Bollards are near-white cylinders. In the source they are dark steel posts with a lighter lamp band at the top. | Bollards are given the light rail material. | Use dark steel grey with a pale head band. |
| 7 | P2 | facade_close, architecture_close, pier_column, viewing_pod | The pod railings have black end and corner posts, which read as a missing material against the pale railing elsewhere. | A default dark material is left on terminal posts. | Assign the outer-rail material. |
| 8 | P2 | central_path, rail_bollard, glass_close | A continuous bare brown soil strip about 0.5 m wide runs between the pale path kerb and the planting. Rail posts stand in it and it still reads faintly as a gutter. In the source, planting spills to the path edge. | Bed planting is inset from the kerb. | Extend ground cover to the kerb or overhang it. |
| 9 | P2 | rear, rear_north, aerial | The deck trees are single-trunk "lollipop" trees about 6 to 8 m tall, not small multi-stem specimens. | Reuses the context tree asset. | Use a smaller multi-stem tree with 2 to 3 trunks. |
| 10 | P2 | glass_close | It is still a generic path close-up. The bridge has no glazing, so the role has no true subject. | Fixed role list. | Accept as a path-edge detail, or relabel the role if the method allows. |

## 3. Source conformance checklist

| item | status | view used / evidence |
|---|---|---|
| Plan and proportions | **deviates** | top vs sources/top.jpg. Deck-to-river ratio matches (about 0.69 vs 0.70). Pods are about 25 to 30 % undersized (finding 1), and the spur adds a cross figure (finding 2). |
| Deck | conforms | left_side, facade_close, pier_column: corten fascia over a dark steel girder band and a soffit. |
| Central path | conforms | top, central_path: pale straight path, about one third of the deck width, with pale kerbs. |
| Planting beds and their variety | **deviates** | front, planting_bed, top: bed width now about equal to the path (source about 1.0 to 1.2), but the planting reads as boulders, lavender and poppies are token, and the planting is low (finding 3). |
| Railings and bollards | conforms (P2 colour) | front, rail_bollard: outer rail with timber-tone cap and vertical balusters; slender two-rail path rail; bollards offset to the bed side. Bollard colour too light (finding 6). |
| Viewing pods and columns | **deviates** (size) | top, aerial, architecture_close: half-hexagon outline with corten fascia, girder and concrete crosshead on a column pair under the south flank conforms. Size and outer-face length deviate (finding 1). |
| Piers | conforms | pier_column, water_under, left_side: round concrete columns enter the water cleanly; crossheads bear on the girder underside (zoom confirmed); main-deck piers sit on the banks. |
| Water and banks | conforms | left_side, right_side, top: river channel, riprap rocks, bank paths with rails, lamp posts. |
| Context | conforms (simplified) | front, aerial: simplified brick towers, parking and bank trees. Acceptable as simplified context. |
| Materials hierarchy | conforms | All views: pale path, corten fascia, dark grey girder, pale concrete columns, timber-tone rail cap, green planting. Minor exceptions: white bollards and black rail posts (P2). |

## 4. Camera validity

All 18 views are valid. In each the target is legible, not clipped, and not occluded enough to block judgement.
- front: valid. Both pods, water on both sides and both outer deck railings are in frame. The wide lens distorts the context (P2 #4).
- front_corner: valid. A foreground deck tree hides part of the near east bed and rail (P2 #5).
- water_under: dark but legible. Column and crosshead contact can be read.
- No view shows a floating part, an interpenetration or an asset clipped at the frame edge in a way that hides the subject.

## 5. Previous-version (v001) findings: resolved in the pixels?

| v001 finding | status in v002 pixels |
|---|---|
| P1 Front camera too low and too far back; pods, water and outer rails hidden | **Resolved.** front shows both pods with corten fascia, water through the railings on both sides, and both outer deck railings running to the pods. |
| P1 Each bed about 1.5 x path width | **Resolved.** In top the beds measure about 1.0 x path width (source about 1.0 to 1.2). |
| P1 Pods were chamfered rectangles and about 15 % too long | **Outline resolved, size not.** The pods are now half-hexagons with angled flanks, but they are now about 25 to 30 % too small and pointed (new P1 #1). |
| P1 No paved route to the pods | **Resolved functionally, but it introduced new P1 #2.** A paved spur reaches the pod perimeter walk, and the path rails, kerbs and bollards are opened there. It reads as a full-width crossroads. |
| P1 Beds read as flat mown lawn with scattered shrubs below the rail tops | **Mostly resolved.** No lawn shows, the mounds overlap continuously over soil, and some masses reach the path-rail top. The mounds now read as boulders and most stay below the rail (part of P1 #3). |
| P1 Planting lacked variety (flat lavender, single-spike grasses, poppy balls) | **Partly resolved, still P1 #3.** Grass fans, spiky lavender lumps and poppy chips exist, but lavender is token (no drifts) and poppies are flat chips. |
| P2 Weak girder band under pod fascia | **Resolved.** A distinct dark girder band sits under the corten in facade_close, architecture_close and pier_column. |
| P2 Pod columns centred instead of under the south flank | **Resolved.** The crosshead and column pair run under the south flank (architecture_close, aerial). |
| P2 Chunky square path rails | **Resolved.** The posts are slender with thin rails (rail_bollard, central_path). |
| P2 Dark kerb strip read as a gutter | **Partly resolved.** The kerb is now pale, but a bare brown soil strip remains (P2 #8). |
| P2 Large trees all along the beds; one fills a third of rear | **Resolved** for count and rear framing. The trees are still single-trunk, not multi-stem (P2 #9). |
| P2 rail_bollard showed no bollard | **Resolved.** A bollard is centred in rail_bollard. |
| P2 Bollards tight against the rail line | **Resolved.** The bollards are offset to the bed side (rail_bollard, glass_close). |
| P2 glass_close a generic path close-up | **Not resolved.** It is unchanged in kind and inherent, since the bridge has no glazing (P2 #10). |
