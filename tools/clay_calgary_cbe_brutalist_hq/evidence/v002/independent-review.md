# Independent holistic review: clay-calgary-cbe-brutalist-hq, v002 (RLASM v6.1 architectural clay)

Reviewer: independent; did not build this candidate. I judged only rendered pixels against the locked source pixels (sources/front.png, sources/oblique.jpg, sources/top.jpg). I opened all 18 renders at full resolution and all four phone boards. For measurements I made zoomed crops in a new folder: /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/review-crops-cbe-v002-q7x3/

## 1. Verdict

**VISUAL_REWORK_REQUIRED.** The parapet, ground-storey height and site, roof and plaza layout now match the sources. One P1 remains: the windows are smaller and sit much deeper than in the sources. At oblique angles the jambs hide almost all of the glass, so the east face still reads as a blank, glassless crate in front, front_corner and aerial, where the sources show a dark window in every bay.

Counts: P0 = 0, P1 = 1, P2 = 6

## 2. Findings

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | front, front_corner, aerial (compare with source front and oblique); also facade_close, window_module | **Windows are too small and too deep, and the glass vanishes at oblique angles.** In the source oblique, the east face at a steep angle still shows a large dark window in every bay, about half the bay width, between thin tapered fins. In aerial at a similar angle, the render's east face shows only a thin dark slit in each cell, about 0.1 of the bay, and the rest is pale splayed concrete. In front and front_corner the east face shows no glass at all and reads blank, which is the same symptom v001 reported. Head-on, the glass is about 0.55 of the bay width (facade_close) against about 0.65 in the source front. So the render reads as a heavy egg-crate with small buried windows, where the source reads as large dark windows between slender fins over sloped sill noses. | The coffer was over-corrected for v001 finding 2. The glass sits at the back of a 0.9 m coffer, is only 1.6 m wide in a 2.7 m cell, and the jamb splays are too shallow in angle. At grazing views the near jamb hides the whole pane. | Widen the glass to about 1.8 to 1.9 m (0.65 to 0.7 of the bay) and keep the 2.2 m height. Make the jambs read as tapered fins: bring the glass plane forward so the jamb depth is about 0.5 to 0.6 m, or open the jamb splay so the fin's front edge is about 0.25 to 0.3 m. Keep the deep sloped sill nose and the flush horizontal floor-line members. Re-render front, front_corner and aerial, and accept only when a dark pane shows in every east-face bay as it does in the source oblique. |
| 2 | P2 | front | The front camera is still much more square to the south face than the source: the east face spans about 0.17 of the south face's width, against about 0.6 in the source front. Because of this, the penthouse louvre and the two air-handling units that the source front shows above the parapet are not visible. | Camera yaw and height | Rotate the camera further toward the SE corner and lift it slightly to match the source framing. |
| 3 | P2 | sculpture_plaza, front | The figures are rectangular prisms with cube heads. The source has smooth, slender, round-headed standing figures. | Low-detail placeholder figure | Use tapered, rounded figure massing. Count and ring arrangement are already correct. |
| 4 | P2 | top | The strip west of the building is lawn and a path. The source top view shows a paved parking lot with a walkway there. | Site simplification | Pave that strip as a parking lot and keep the walkway. |
| 5 | P2 | facade_close, corner_cantilever, right_side | The fascia over the ground storey has a vertical joint at every bay, so it reads as panelled. The source fascia reads as one plain continuous band. | Panel-per-bay fascia | Remove or soften the vertical joints. |
| 6 | P2 | right_side, east_side, rear, roof_penthouse | Around the cell field there is a wide flat margin with a stepped reveal, wider than the source's corner members. The penthouse louvre sits in the lower middle of its wall, where the source oblique shows it in the upper middle. | Frame and inset parameters; louvre z position | Narrow the margin to a corner-pier width and raise the louvre. |

## 3. Source conformance checklist

| Item | Status | View(s) used |
|---|---|---|
| Silhouette and storey count | **Conforms.** Near-square box; recessed ground storey plus three office floors plus a plain parapet; set-back penthouse. The overall height now matches the source front proportions. | front, right_side, rear, aerial, source front and oblique |
| Bay rhythm 14 x 13 | **Conforms.** 14 bays on south and north, 13 on east and west. Plan ratio 345:317 (render top) against 605:555 (source top). | front, right_side, east_side, rear, rear_north, top |
| Window depth and fin/nose relief | **Deviates (P1-1).** Depth reads strongly, with returns on all four sides and a sloped sill, but too strongly: the glass is too narrow and too deep, and disappears at oblique views. Head-on, the cellular grid itself is correct. | facade_close, window_module, front, front_corner, aerial against source oblique |
| Fascia and parapet bands | **Conforms.** The parapet is plain with one horizontal joint and a coping, and no grid member enters it. It measures about 0.58 to 0.62 of the storey pitch (right_side 65/113 px; facade_close 155/250 px; front about 0.59), against about 0.5 to 0.55 in the source. The fascia is about 0.4 of the pitch; its per-bay joints are P2-5. | right_side, facade_close, front crop |
| Cantilever over the recessed ground storey with board-formed columns | **Conforms.** Soffit about 1.48 storey pitches above the podium (front crop), about 3 m overhang, freestanding board-formed columns rising to the soffit, two-tier storefront with transom under a board-formed band. | front, corner_cantilever, arcade_soffit, ground_entrance |
| Entrances and podium steps | **Conforms.** Glazed double doors with handles face the plaza. A second entrance door is on the east face near the SE corner. A low podium has a continuous flight of steps along the south and east. Street trees are not on the east entrance. | ground_entrance, sculpture_plaza, corner_cantilever, east_side |
| Penthouse and roof plant | **Conforms.** The penthouse sits from about 0.26 to 0.74 of the width and 0.08 to 0.76 of the depth, offset north, matching the source top. Two air-handling units with two round fans each are on the penthouse roof. Also present: small vents, and a railed unit on the main roof east of the penthouse. The south face has a steel door west of the louvre and another near the east end, as in the source oblique. Louvre height is P2-6. | top, aerial, front_corner, roof_penthouse, rear |
| Sculpture plaza and site | **Conforms.** The paved plaza is SE with the round plinth and ring of figures at about 0.83 of the building width (same as source top). Lawn to the SW, brick neighbours west and north, sidewalks, east street trees, lamp, and a crossing on the east street near the south end. The parking lot is P2-4 and the figure form is P2-3. | top, aerial, front_corner, sculpture_plaza |
| Materials hierarchy | **Conforms.** Warm beige-grey precast for the upper box; board-formed lines on columns and ground walls; dark storefront and window glass; brick-red neighbours; green lawn. | front, corner_cantilever, arcade_soffit |

## 4. Camera validity

- No render has its target occluded or clipped, and none is illegible. All 18 render files are present at 1440x1080.
- rear and rear_north: the north brick neighbours hide part of the north ground storey, but the office grid, penthouse and louvre stay legible. Acceptable.
- rear_side: the neighbours cover the lower ground storey. The envelope is legible.
- front: valid, but less oblique than the source front (P2-2). This makes the P1-1 blank-east-face symptom worse but does not cause it, because aerial, which is closer to the source oblique angle, shows the same thing.
- The brief's detail list names architecture_close and glass_close, which are not among the 18 renders, and lists facade_close twice. The 18 files that exist cover every role in the brief, so I record this as a brief inconsistency, not a candidate defect.

## 5. v001 findings: resolved in the pixels?

1. **Parapet not plain and too shallow: RESOLVED.** It is one continuous plain band with a single horizontal joint and a coping, with no fins or cells in it. It measures about 0.58 to 0.62 of the storey pitch (right_side, facade_close, front crop).
2. **Grid hierarchy inverted and east face blank: PARTLY RESOLVED, and it carries P1-1.** The pilaster fins and box spandrels are gone. Head-on, the facade is now a flush cellular grid of coffers splayed on all four sides, with continuous floor-line members and corner piers (facade_close, window_module, right_side, rear). However, the east face still reads almost blank in the front view, and also in front_corner and aerial. The new coffer is too deep for its glass, and the source shows a dark pane in every bay at those angles.
3. **Ground storey too short: RESOLVED.** Podium to soffit measures about 1.48 storey pitches in the front crop, consistent with the claimed 5.8 m over a 4.0 m pitch. The storefront is two-tier with a transom under a board-formed band, and the columns reach the new soffit (front, corner_cantilever, ground_entrance).

Builder's P2 claims checked in the pixels:

- **Warmer beige-grey concrete:** yes.
- **Front camera moved east and back:** the SE corner and the east face now show, but much less than in the source (P2-2).
- **Extra board-formed bay at the west end:** a solid board-formed wall run between the west columns is present (front crop).
- **Slimmer, taller figures:** slimmer and taller, but still block forms (P2-3).
- **Penthouse doors:** yes, one west of the louvre and one near the east end.
- **East trees off the east entrance:** yes. The trunks stand between bays, clear of the SE-corner door.

What v001 got right still holds: the 14 x 13 rhythm, the roughly 3 m cantilever on freestanding board-formed columns, the entrances and podium steps, the penthouse position and roof plant, and the SE sculpture plaza.
