# Independent holistic review: clay garden-court senior residence, v004

Reviewer: independent (did not build). Basis: rendered pixels only, compared with sources/front.png, sources/oblique.jpg and sources/top.jpg. I opened all 18 renders and the 4 phone boards at full resolution. My zoom crops are in `/tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/indrev-v004-crops-q7/`, a new folder. I did not overwrite any existing file.

## 1. Verdict

**VISUAL_REWORK_REQUIRED.** The envelope, plan, roofs, loggias, garden room and court program now match the sources well, and the garden-room threshold void is fixed. Two P1 defects remain:
- The fix for the v003 loggia-roof clash was not applied at the junction of the north link loggia and the NE pavilion. A second-storey window there is still crossed by the roof.
- Every court bench is a legless slab hovering above the paving.

Counts: P0 = 0, P1 = 2, P2 = 9

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | court_view (crop `court_NE_junction_z.png`, about x 1070-1095 and y 95-160 in the original) | The north link loggia, between the garden room and the NE pavilion, has a hipped end that runs up the NE pavilion's west face. The roof meets the wall on a line from the eave at the pavilion corner up to the ridge end. A second-storey double-hung window sits right at that line. Its glass runs down into the copper slope and the roof cuts it off, with no sill and no bottom of the lower sash. The window one bay further north on the same face shows its full sash and sill, so this one is clipped by about 20% of its height. This is the v003 P1 defect, still present at this junction. | The new rule omits second-storey windows "where an abutting loggia roof (with overhang) would meet them". It does not catch this window. The likely reasons are that it tests only the face the loggia meets end-on, or only the eave and overhang band. The rising hip-end and ridge region on the abutting side wall is not tested. | Run the omission or clearance test against the full roof-wall intersection: the hip-end slope up to the ridge, plus the overhang, on every pavilion face that any loggia touches. Then either drop that window bay or lower the loggia ridge or hip so the roof stays at least one sill height below the second-storey sill. Check again in court_view, front (NE link) and hub_cupola (NW link). |
| 2 | P1 | garden_beds (top left, crop `gb_top.png`), court_view (benches on the central lawn ring and by the fountain, crops `court_benches.png`, `court_bench3.png`), pergola_terrace (foreground slab) | Every court bench is a single flat timber slab with no legs, ends or back. In garden_beds, from an oblique angle, there is clear pavement between the slab's underside and its offset shadow, and no support of any kind. A chair beside it in the same crop does have legs. On the lawn the shadow sits apart from the slab, so it reads as hovering. | The bench part was authored as a seat board raised to seat height, and its leg or end-frame parts are missing or were never instanced. | Give each bench two solid end frames or four legs that reach the ground, plus a backrest. The sources show slatted benches with backs. Seat the frames on the paving or lawn plane. |
| 3 | P2 | pergola_terrace (crop `pergola_chairs.png`) | Every chair faces +x whatever table it belongs to. Several sit in front of a table side-on, facing away from it. This is unchanged from v003. | Chairs are placed with a fixed rotation. | Rotate each chair to face its table's centre. |
| 4 | P2 | facade_close, loggia_arcade, pergola_terrace, court_view | Up close, the brick is uniform horizontal lines with no head joints, so walls read as clapboard siding. Unchanged from v003 ("coarse coursing"). | The coursing is a line-only displacement or texture. | Use finer coursing with staggered head joints, or plain untextured clay brick colour. |
| 5 | P2 | glass_close, interior | The glazing has milky haze and low contrast, which flattens the interior. | Glass transmission or roughness, or a volumetric or fog setting. | Lower roughness or haze on the clear glass. |
| 6 | P2 | glass_close, court_view (crop `court_gardenroom_doors.png`) | The garden-room door bays now read as glazed with a transom, which fixes the v003 panel problem. However, the lower 4×2 grid looks like fixed glazing. There is no heavier meeting stile and no hardware to mark the two French door leaves. | The muntin grid is uniform. | Widen the central meeting stile and add small pull bars. |
| 7 | P2 | hub_cupola (crop `cupola_base.png`) | A row of small seam-end "teeth" stands proud around the base of the cupola drum. | The standing seams stop short of the drum, or overshoot it, instead of tucking under a flashing collar. | Add a flashing collar or trim the seams to the drum radius. |
| 8 | P2 | court_view, garden_beds | The fenced kitchen garden has no gate, which is unchanged. Planting is sparse: the rose beds are pink discs holding one shrub each. | Not authored. | Add a gate leaf in the west or north fence run, and fill the rose beds more densely. |
| 9 | P2 | left_side, right_side, rear | The asset fills only about half the frame width, with large empty margins. It is still legible, but thin. No outer-face entrance is visible on the street sides, which is unchanged. | The framing distance is set for the bounding sphere. | Tighten the framing. Optionally add an entrance canopy on a street face, though no source shows one. |
| 10 | P2 | loggia_arcade | A tree canopy covers the left third of the frame, and a white post or mullion runs the full height of the right edge. The view is less crowded than in v003 but still partly obstructed. | The camera sits inside neighbouring objects. | Move the camera clear of the tree and post, or hide them for this shot. |
| 11 | P2 | all whole-envelope views, compared with the front and oblique sources | The north link loggias have 2 or 3 arches each, where the front and oblique sources show 6 or 7. This is consistent with the top-view plan the builder followed, where the links are short, so I record it only as an acknowledged deviation. | The plan follows sources/top.jpg. | None required. Document the deviation. |

## 3. Source conformance checklist

| Item | Status | View(s) used | Note |
|---|---|---|---|
| Silhouette | conforms | front, front_corner, aerial, rear_side vs front/oblique | Four hipped blocks with flat tops and two ridged wings ring the court, with the octagonal garden room and cupola as the centre accent. |
| Storey count | conforms | front, left_side, right_side, rear, court_view | All blocks are three brick storeys with a dormered attic. Loggias are one storey. |
| Plan (ring of blocks, court) | conforms | top vs top.jpg | Two north pavilions, a SW pavilion, a long south wing and a long east wing, joined by loggias round a closed court. The garden room sits on the link between the north pavilions. This follows the top view, as the brief says. |
| Roofs and dormers | conforms | dormer_roof, front, aerial, top | Copper standing seam. Pavilions are hipped to a flat top with rooftop units. Wings are hipped to a ridge. Gabled dormers sit on every slope. |
| Loggias and arches | conforms, but the NE junction is a P1 | loggia_arcade, court_view, rear, left_side | Round arches have reveals, imposts and copper roofs. The north links are shorter than in the front and oblique sources (P2-11). The roof clashes with a second-storey window at the NE link (P1-1). |
| Garden room and cupola | conforms | architecture_close, glass_close, hub_cupola, interior | Octagonal, fully glazed with white muntins, under a hipped copper roof, with a glass ribbed cupola and finial. The door bays are now glazed and sit under a transom. |
| Window rhythm and balconies | conforms | facade_close, court_view, interior | White double-hung windows with lintels and sills on a regular grid. Court faces have arched garden doors with iron balconies above. |
| Garden elements (paths, fountain, beds, pergola) | conforms, but benches are a P1 | court_view, garden_beds, pergola_terrace, top | Brick paths, lawns, rose beds, the tiered fountain in the SW of the court, the fenced timber raised beds, and the timber pergola over a dining terrace beside the east wing are all present. The benches float (P1-2). |
| Forecourt | conforms | top, hub_cupola, rear | The circular lawn with cross paths and a tiered fountain sits north of the garden room, inside the drive loop by the street. |
| Materials hierarchy | conforms, with P2 coursing | all | Brick-red walls, copper roofs, white trim and glazing frames, timber beds and pergola, dark iron rails. The brick reads as siding up close (P2-4). |

## 4. Camera validity

- No view has its target occluded, clipped or illegible to a degree that invalidates it.
- left_side, right_side and rear are framed loosely, with the asset at about 50% of the frame width, but they are legible (P2-9).
- loggia_arcade is partly obstructed by a foreground canopy and a post, but the arcade, its reveals and the roof are still readable (P2-10).
- court_view is a valid source-matched view into the court.
- front and front_corner are valid whole-envelope views from high above the south.

## 5. Previous-version (v003) findings: are they resolved in the pixels?

| v003 finding | Result in v004 | Evidence |
|---|---|---|
| P1: black void slot between the garden-room French doors' bottom rail and the interior floor | **Resolved** | interior (crop `interior_threshold.png`): the glazing's bottom rail sits on a continuous pale threshold or sill strip that meets the floor, with no dark slot. court_view: the door bay base is a continuous white plinth. |
| P1: abutting loggia roof meeting the pavilion wall over a second-storey window, covering its lower sash and sill | **Not resolved (partially fixed)** | facade_close shows that the omission works on one face: there is blank wall above the loggia roof. court_view at the north link and NE pavilion west face still shows a second-storey window cut off by the roof, with no sill (P1-1). The NW link in hub_cupola has a sill sitting right on the hip line, which is acceptable but tight. |
| P2: dark band under the water tables | Largely resolved | pergola_terrace and loggia_arcade show only a hairline contact shadow. |
| P2: garden-room door bays read as white panels with a small inset door | Resolved | glass_close, architecture_close and court_view show wide multi-pane glazed bays under a transom. The meeting stile is weak (P2-6). |
| P2: chair orientation | Not resolved | pergola_terrace (P2-3). |
| P2: far-slope dormer teeth | Acceptable or unchanged | In front and aerial, the far-slope dormers show as small gables above the hips, which is consistent with dormers on every slope. |
| P2: coarse coursing | Not resolved | P2-4. |
| P2: sparse planting | Not resolved | P2-8. |
| P2: no kitchen-garden gate | Not resolved | P2-8. |
| P2: thin side framing | Not resolved | P2-9. |
| P2: glass haze | Not resolved | P2-5. |
| P2: crowded loggia_arcade view | Improved, but still obstructed | P2-10. |
| P2: no outer entrance | Not resolved | P2-9. |
