# Independent holistic review: clay-ctrain-elevated-station v003 (RLASM v6.1)

Reviewer: independent; I did not build this candidate. I judged only rendered pixels against the locked sources (`sources/front.png`, `sources/oblique.jpg`, `sources/top.jpg`). I opened all 18 renders at full resolution, plus the four phone boards. Zoomed crops are in `/tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/ctrain-v003-indep-crops-q7/`, which is a new folder. No other file was touched.

## 1. Verdict

**VERDICT: VISUAL_REWORK_REQUIRED**. All four v002 P1s are fixed in the pixels. One new P1 remains: in the hero front view, the SW tower's glazed stair bay does not reach the ground. It stops on a projecting sill above the sidewalk with a shadow gap below it. In the front and oblique sources this bay is the glazed street entrance and it reaches the ground.

Counts: P0 = 0, P1 = 1, P2 = 10

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | front (hero), left_side, front_corner, aerial (SE tower likewise) | The SW tower's glazed stair bay ends on a projecting grey sill plate about 0.3–0.6 m above the sidewalk. A dark shadow strip and brick/plinth show below it, so the bay reads as an oriel or bay window hung on the tower. The grid is uniform from bottom to top. It has no deep transom band at first-floor height and no glazed entry at the sidewalk. In `sources/front.png` (crop `src_front_baybase.png`) and `sources/oblique.jpg` (crop `src_obl_tower.png`), the bay runs down to grade on a thin flush base. It has a heavy horizontal band at about first-floor height, and its ground storey is the glazed station entrance. | The bay box is built from a raised sill height and was never brought down to grade. The ground-storey bay grammar (transom band and entry) was not modelled. | For both towers: extend the bay mullions and glazing to grade, sitting on a flush base of at most 0.15 m with no overhang and no shadow gap. Add the projecting horizontal band at first-floor height (about 4.5 m). Model the ground storey of the bay as a glazed entry with a door pair, about 0.15 m recessed. Re-render front, left_side and facade_close. |
| 2 | P2 | top, front, tower_cap | The west Plus 15 still meets the headhouse west face just north of the SW tower, beside the tower rather than into it (unchanged from v002). | Deliberate. The west face begins at the tower's north face. | Optional: move the skywalk about one bay south so its end frames into the tower's glazed bay, as in the front source. |
| 3 | P2 | front | The 24 mm three-point view makes the verticals converge strongly. The tower and the west façade lean inward. The source front is a corrected two-point street view. The train is hidden behind the guard and shows only as a blue sliver, while the source shows the train prominently on the deck. | Wide lens with a pitched camera and a low eye height close to the tower. | Level the camera and use lens shift. Step back 10–15 m toward the opposite corner so the train clears the guard. |
| 4 | P2 | front, glass_close, architecture_close | Canopy posts render two-tone: a grey shaft with a bright white mid-section. It reads as two coincident objects, a post plus a mast. | A second white cylinder (mast or light) overlaps the canopy post, or there is a material split. | Delete the duplicate, or offset the mast so it stands clear, and give the post one material. |
| 5 | P2 | skywalk_bridge, east_skywalk, front (guards) | Small black specks at truss panel nodes and at the joints between guard posts and handrail. | Tiny gaps or coincident faces at member ends. | Overlap members by about 10 mm at the nodes, or cap the joints. |
| 6 | P2 | street_underpass, left_side, front_corner | The underpass soffit is still charcoal, with a mean value of about 63/255. The new fill light makes a hard elliptical hotspot on the road that reads as a lamp pool, not ambient fill. | A point or spot fill light below the deck. | Use a broad area fill or raise the bounce, and soften or spread the hotspot. |
| 7 | P2 | front, facade_close, all whole-envelope views | The brick reads as light salmon. In comparable shade the mean is about 142/104/91, against 92/56/41 for the sources' deeper red-brown. | Base colour too light and desaturated. | Darken and saturate the brick base toward the source red-brown, then re-check against the pale caps. |
| 8 | P2 | top, front_corner, aerial | The relation between the platforms and the street has shifted. The E-W street lies closer to the headhouse, the canopies now span most of the street, and the pylons sit south of the street over the sidewalk. In the top source, the canopies end over the street's north third and the pylons stand over the street. Overall, the platforms are about 15% short relative to the headhouse width. | Street centreline placed too far north after the canopies were shortened. | Shift the E-W street about 6–8 m south, or lengthen the uncovered platform and deck by one bay, so the pylons stand over the street. |
| 9 | P2 | aerial, front_corner, left_side, top | The deck extension south of the platforms ends in a closed parapet with red buffer stops, which reads as a terminus. Both sources show the tracks running on through. | An asset-boundary convention. | Optional: end with a plain cut deck edge or a short tapered fascia, without buffer stops. |
| 10 | P2 | facade_close | A flat grey slab sits under the north (hip) end of the glazed canopy, and the hip rafters come down onto it. The junction is cluttered. | An entry hood at platform level overlaps the canopy hip. | Lower or trim the hood so the rafters land on a single ridge or wall plate. |
| 11 | P2 | top, east_skywalk, right_side | The long N-S skywalk's run south of the link is shorter than in the top source (about 1.2 against about 1.5 headhouse widths). | Pavilion placed early. | Optional: extend the south run by about 10 m. |

## 3. Source conformance checklist

| item | status | view(s) used | note |
|---|---|---|---|
| Silhouette | conforms | front_corner vs oblique, top vs top, aerial | Square flat-roofed headhouse. Twin towers at the south corners project above the roof. Platforms run south from the south face. One skywalk goes west and one link goes east to the N-S skywalk. |
| Storey count | conforms | front, left_side, rear | Three storeys: a tall ground storey, a punched second storey and a continuous glazed top band. The towers rise about half a storey above the roof. |
| Headhouse and glazed band | conforms | left_side, east_skywalk, architecture_close, rear | The continuous glazed band along the top storey has a pale sill and coping on every face. |
| Stair towers and caps | deviates (P1 #1) | front, facade_close, tower_cap, aerial | Square brick towers. Tall glazed bays on the west and east faces with brick south faces, as in the sources. The pale stepped caps are lit correctly with no black faces. The bays stop short of grade and have no first-floor band or entry. |
| Deck and piers | conforms | front, street_underpass, left_side, aerial | Concrete deck on round piers with hammerhead cap beams over the E-W street. The level double-track deck continues south past the platforms on round piers. There is no ramp. |
| Platforms: guards, tactile edges, pylons, stairs | conforms (P2 #8 placement) | aer_south and top_plat crops, train_platform, platform_canopy | Glass guards on the outer edges. Yellow tactile strips run the full length of both platforms. One red pylon on each platform near the south end, and one stair from each platform down to the sidewalk. The pylons sit slightly south of where the source places them. |
| Canopies | conforms | platform_canopy, glass_close, front_corner, top | Long glazed gable canopies on central steel posts, now two bays shorter, with a canopy-to-platform ratio of about 0.57 against about 0.63 in the source. The posts are two-tone (P2 #4). |
| Skywalks | conforms (P2 #2, #11) | skywalk_bridge, east_skywalk, left_side, right_side, top | Glazed with steel X-truss bracing. The west Plus 15 crosses the west street to a glazed stair pavilion. The east link meets a long N-S skywalk on round columns, with a pavilion at each end. |
| Train | conforms | train_platform, platform_canopy, aerial, top, right_side | Two cars, red and white with blue-grey glazing, standing at the west platform. Bogies sit on the track. |
| Streets | conforms (P2 #8) | top, left_side, front_corner | The west N-S street runs under the west skywalk. The E-W street passes under the deck, with crossings and a corner tree that is clear of the signal arm. |
| Materials hierarchy | conforms (P2 #7) | all | Brick body, pale caps and copings, grey steel and mullions, glass, light concrete deck, yellow tactile strips and red pylons. The brick is lighter and pinker than the sources. |

## 4. Camera validity

- No view has an occluded target, a clipped asset or an illegible frame.
- **front:** now a valid eye-level street view from the SW corner. The tower, glazed bay, west skywalk, deck, piers and canopy are all in frame. The converging verticals and the hidden train are polish only (P2 #3).
- **left_side and right_side:** raised. The asset fills about 75% of the frame width, and the deck, canopies, train, skywalks and stairs are all legible.
- **rear:** shows a face no source covers. It is legible. The tail-track portal has returns and a lintel, and the stub stands on a round pier.
- **street_underpass:** legible, with piers, cap beams, the soffit and the street through to daylight. It is dark but not black (P2 #6).
- **interior:** legible. It looks out through the top-storey glazed band over the canopies, and the benches stand on pedestals.

## 5. v002 findings: resolved in pixels?

| v002 finding | status | evidence |
|---|---|---|
| P1: front was a distant elevated overview, not an eye-level street view toward the SW tower | **Resolved** | front.png is an eye-level view looking up at the SW tower's glazed bay, with the skywalk on the left and the deck and canopy on the right. |
| P1: left_side and right_side showed the asset as a thin band | **Resolved** | Both are raised oblique views. The deck, canopies, train, skywalks and stairs read clearly. |
| P1: invented ramp to grade south of the platforms | **Resolved** | aerial, front_corner, left_side and top show the level double-track deck continuing south on round piers, with glass guards and a closed end. No ramp is visible. A terminus reading remains (P2 #9). |
| P1: tower cap slab side faces rendered pure black | **Resolved** | In tower_cap, front, front_corner and aerial, all cap faces are pale and properly shaded. |
| P2: west skywalk lands beside rather than into the SW tower | **Not resolved** (unchanged by design) | top, tower_cap (P2 #2). |
| P2: canopies too long | **Resolved** | top and front_corner show the canopy-to-platform ratio at about 0.57 against about 0.63 in the source. |
| P2: interior benches floating | **Resolved** | interior and platform_canopy show the benches on pedestal legs. |
| P2: signal head inside a tree crown | **Resolved** | top, front_corner and left_side show the tree crown clear of the signal arm. |
| P2: north tail track a short stub | **Resolved** | rear_side, top and left_side show a longer tail on several piers. |
| P2: south-face tower slot unglazed at the top | **Resolved** | The south faces are plain brick, as in the sources (front, facade_close). |
| P2: stray diagonal tube under the canopy | **Resolved** | No knee brace is visible. Only the canopy rafters remain, with one cluttered hip junction (P2 #10). |
| P2: dark underpass soffit | **Partly resolved** | The soffit is lifted to about 63/255 and is legible, but the fill shows as a hard hotspot (P2 #6). |
